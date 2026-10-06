"""Stage 0B: cached post-answer hidden-state diagnostic.

The module never generates answers and never runs an NLI model.  It reconstructs
leave-one-out semantic entropy from cached pairwise judgments, teacher-forces one
cached answer through the frozen generator, and evaluates leakage-safe probes on
the original fixed split.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import os
import platform
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any

import matplotlib
import numpy as np
import sklearn
import torch
import transformers
import yaml
from scipy.stats import spearmanr
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import accuracy_score, log_loss, mean_squared_error, r2_score, roc_auc_score
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from transformers import AutoModelForCausalLM, AutoTokenizer

from stage0.direction_stability import grouped_bootstrap_interval
from stage0.pipeline import (
    best_train_threshold,
    choose_device,
    choose_dtype,
    clear_device_cache,
    cluster_entropy,
    normalize_answer,
    stable_hash,
)


matplotlib.use("Agg")
from matplotlib import pyplot as plt  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]


def _resolve(value: str | Path) -> Path:
    path = Path(value).expanduser()
    return path.resolve() if path.is_absolute() else (ROOT / path).resolve()


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def _atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")
    os.replace(temporary, path)


def _atomic_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True, allow_nan=False) + "\n")
    os.replace(temporary, path)


def _atomic_npz(path: Path, arrays: dict[str, np.ndarray]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp.npz")
    np.savez_compressed(temporary, **arrays)
    os.replace(temporary, path)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _context_group(context: str) -> str:
    normalized = " ".join(context.lower().split())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _class_counts(labels: np.ndarray, indices: np.ndarray) -> dict[str, int]:
    return {str(key): int(value) for key, value in Counter(labels[indices].tolist()).items()}


def load_stage0b_config(config_path: str | Path) -> dict[str, Any]:
    path = _resolve(config_path)
    with path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    try:
        config["_config_path"] = str(path.relative_to(ROOT))
    except ValueError:
        config["_config_path"] = str(path)
    return config


def validate_preserved_split(
    records: list[dict[str, Any]],
    source_probe: dict[str, Any],
    expected_sizes: dict[str, int] | None = None,
) -> dict[str, Any]:
    """Validate and return the exact source train/validation/test membership."""

    split = {
        name: np.asarray(source_probe[f"{name}_indices"], dtype=np.int64)
        for name in ("train", "validation", "test")
    }
    if expected_sizes is not None:
        for name, expected in expected_sizes.items():
            if len(split[name]) != int(expected):
                raise ValueError(f"Source {name} split has {len(split[name])}, expected {expected}")
    joined = np.concatenate(list(split.values()))
    if len(joined) != len(records) or len(np.unique(joined)) != len(records):
        raise ValueError("Source split is not a one-to-one partition of all questions")
    if set(joined.tolist()) != set(range(len(records))):
        raise ValueError("Source split indices do not cover exactly the cached row range")
    groups = np.asarray([_context_group(record["context"]) for record in records])
    overlaps = {}
    for left, right in (("train", "validation"), ("train", "test"), ("validation", "test")):
        overlap = set(groups[split[left]].tolist()) & set(groups[split[right]].tolist())
        overlaps[f"{left}_{right}"] = len(overlap)
        if overlap:
            raise ValueError(f"Source split leaks {len(overlap)} contexts across {left}/{right}")
    return {
        **split,
        "groups": groups,
        "audit": {
            "method": source_probe.get("split_method"),
            "sizes": {name: int(len(indices)) for name, indices in split.items()},
            "unique_contexts": {
                name: int(len(np.unique(groups[indices]))) for name, indices in split.items()
            },
            "context_overlap_counts": overlaps,
            "membership_sha256": stable_hash(
                {name: indices.tolist() for name, indices in split.items()}
            ),
            "source_membership_reused_exactly": True,
        },
    }


def greedy_leave_one_out_clusters(
    record: dict[str, Any],
    observed_answer_index: int,
    nli_cache: dict[str, dict[str, Any]],
    nli_model_id: str,
    used_judgments: dict[str, dict[str, Any]] | None = None,
) -> tuple[list[int], list[int]]:
    """Re-run the repository's greedy clustering after removing one answer.

    Returned assignments follow the remaining answers' original index order.
    Missing judgments fail closed; this function never invokes an NLI model.
    """

    generations = record["generations"]
    if not 0 <= int(observed_answer_index) < len(generations):
        raise IndexError("Observed answer index is outside the cached generations")
    remaining = [index for index in range(len(generations)) if index != observed_answer_index]
    texts = [f"{record['question']} {generation['text']}" for generation in generations]

    def entails(from_index: int, to_index: int) -> bool:
        if normalize_answer(generations[from_index]["text"]) == normalize_answer(
            generations[to_index]["text"]
        ):
            return True
        key = stable_hash(
            {
                "model": nli_model_id,
                "premise": texts[from_index],
                "hypothesis": texts[to_index],
            }
        )
        if key not in nli_cache:
            raise KeyError(
                f"Missing cached NLI judgment for {record['id']} "
                f"{from_index}->{to_index}; refusing to run NLI"
            )
        if used_judgments is not None:
            used_judgments[key] = {
                "cache_key": key,
                "record_id": record["id"],
                "from": int(from_index),
                "to": int(to_index),
                **nli_cache[key],
            }
        return nli_cache[key]["label"] == "entailment"

    cluster_ids = [-1] * len(remaining)
    next_id = 0
    for local_i, original_i in enumerate(remaining):
        if cluster_ids[local_i] != -1:
            continue
        cluster_ids[local_i] = next_id
        for local_j in range(local_i + 1, len(remaining)):
            original_j = remaining[local_j]
            if entails(original_i, original_j) and entails(original_j, original_i):
                # Preserve the original pipeline's exact greedy assignment rule.
                cluster_ids[local_j] = next_id
        next_id += 1
    return cluster_ids, remaining


def build_leave_one_out_targets(
    records: list[dict[str, Any]],
    observed_answer_index: int,
    nli_cache: dict[str, dict[str, Any]],
    nli_model_id: str,
    train_indices: np.ndarray,
) -> tuple[list[dict[str, Any]], np.ndarray, float, dict[str, dict[str, Any]]]:
    """Build continuous entropy and train-thresholded binary targets."""

    used: dict[str, dict[str, Any]] = {}
    rows = []
    entropy = []
    for source_index, record in enumerate(records):
        cluster_ids, target_indices = greedy_leave_one_out_clusters(
            record,
            observed_answer_index,
            nli_cache,
            nli_model_id,
            used,
        )
        value = cluster_entropy(cluster_ids)
        entropy.append(value)
        observed = record["generations"][observed_answer_index]
        rows.append(
            {
                "source_index": source_index,
                "id": record["id"],
                "observed_answer_index": int(observed_answer_index),
                "observed_answer_text": observed["text"],
                "observed_answer_token_ids": [int(value) for value in observed["token_ids"]],
                "observed_answer_token_count": int(observed["token_count"]),
                "same_answer_sequence_nll": float(-observed["sequence_logprob"]),
                "same_answer_mean_token_nll": float(-observed["mean_token_logprob"]),
                "target_answer_indices": target_indices,
                "leave_one_out_semantic_ids": cluster_ids,
                "leave_one_out_num_semantic_clusters": int(len(set(cluster_ids))),
                "leave_one_out_semantic_entropy": float(value),
            }
        )
    entropy_array = np.asarray(entropy, dtype=np.float64)
    if not np.all(np.isfinite(entropy_array)) or np.unique(entropy_array).size < 2:
        raise ValueError("Leave-one-out semantic entropy is degenerate or non-finite")
    threshold = best_train_threshold(entropy_array[np.asarray(train_indices, dtype=np.int64)])
    labels = (entropy_array >= threshold).astype(np.int64)
    for row, label in zip(rows, labels):
        row["high_entropy_label"] = int(label)
        row["threshold_fit_on_training_only"] = float(threshold)
    return rows, labels, float(threshold), used


def audit_nli_coverage(
    records: list[dict[str, Any]],
    observed_answer_index: int,
    nli_cache: dict[str, dict[str, Any]],
    nli_model_id: str,
) -> dict[str, Any]:
    """Require all directed unequal answer pairs before any downstream work."""

    required_keys: set[str] = set()
    missing_keys: set[str] = set()
    directed_pair_occurrences = 0
    normalized_equal_pair_occurrences = 0
    for record in records:
        generations = record["generations"]
        remaining = [
            index for index in range(len(generations)) if index != observed_answer_index
        ]
        texts = [f"{record['question']} {generation['text']}" for generation in generations]
        for from_index in remaining:
            for to_index in remaining:
                if from_index == to_index:
                    continue
                if normalize_answer(generations[from_index]["text"]) == normalize_answer(
                    generations[to_index]["text"]
                ):
                    normalized_equal_pair_occurrences += 1
                    continue
                directed_pair_occurrences += 1
                key = stable_hash(
                    {
                        "model": nli_model_id,
                        "premise": texts[from_index],
                        "hypothesis": texts[to_index],
                    }
                )
                required_keys.add(key)
                if key not in nli_cache:
                    missing_keys.add(key)
    if missing_keys:
        raise KeyError(
            f"Global cache is missing {len(missing_keys)} required NLI judgments; "
            "refusing to launch NLI or continue"
        )
    return {
        "observed_answer_index": int(observed_answer_index),
        "directed_nonduplicate_pair_occurrences": int(directed_pair_occurrences),
        "normalized_equal_pair_occurrences": int(normalized_equal_pair_occurrences),
        "unique_required_cached_judgments": int(len(required_keys)),
        "missing_cached_judgments": 0,
        "coverage_complete": True,
        "nli_inference_calls": 0,
    }


def select_answer_representations(
    hidden_states: tuple[torch.Tensor, ...] | list[torch.Tensor],
    prompt_length: int,
    answer_length: int,
    primary_layer: int,
    exploratory_layer: int,
) -> dict[str, np.ndarray]:
    """Select final-token and answer-only mean states from one unpadded sequence."""

    if answer_length <= 0:
        raise ValueError("Cached answer must contain at least one content token")
    answer_start = int(prompt_length)
    answer_stop = answer_start + int(answer_length)
    final_index = answer_stop - 1
    primary = hidden_states[int(primary_layer)][0]
    exploratory = hidden_states[int(exploratory_layer)][0]
    if answer_stop > primary.shape[0] or answer_stop > exploratory.shape[0]:
        raise ValueError("Answer span exceeds hidden-state sequence length")
    final_primary = primary[final_index]
    mean_primary = primary[answer_start:answer_stop].float().mean(dim=0)
    final_exploratory = exploratory[final_index]
    return {
        "layer_14_final_answer_token": final_primary.detach().to("cpu", dtype=torch.float16).numpy(),
        "layer_14_mean_answer_tokens": mean_primary.detach().to("cpu", dtype=torch.float16).numpy(),
        "layer_23_final_answer_token": final_exploratory.detach().to("cpu", dtype=torch.float16).numpy(),
        "answer_start_index": np.asarray(answer_start, dtype=np.int64),
        "answer_stop_index_exclusive": np.asarray(answer_stop, dtype=np.int64),
        "final_answer_token_index": np.asarray(final_index, dtype=np.int64),
    }


def verify_cached_tokenization(
    record: dict[str, Any],
    observed_answer_index: int,
    tokenizer: Any,
    source_dataset_config: dict[str, Any],
    max_prompt_tokens: int,
) -> dict[str, Any]:
    """Reconstruct and verify the exact prompt+cached-answer token sequence."""

    content = ""
    if source_dataset_config.get("include_context", True):
        content += f"Context: {record['context']}\n\n"
    content += f"Question: {record['question']}"
    messages = [
        {"role": "system", "content": source_dataset_config["system_prompt"]},
        {"role": "user", "content": content},
    ]
    rendered = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    if rendered != record["prompt"]:
        raise ValueError(f"Cached prompt text mismatch for {record['id']}")
    prompt_ids = tokenizer(
        record["prompt"], truncation=True, max_length=int(max_prompt_tokens)
    )["input_ids"]
    if len(prompt_ids) != int(record["prompt_token_count"]):
        raise ValueError(f"Prompt token-count mismatch for {record['id']}")
    if int(prompt_ids[-1]) != int(record["final_prompt_token_id"]):
        raise ValueError(f"Final prompt-token mismatch for {record['id']}")

    answer = record["generations"][int(observed_answer_index)]
    answer_ids = [int(value) for value in answer["token_ids"]]
    if not answer_ids or len(answer_ids) != int(answer["token_count"]):
        raise ValueError(f"Invalid cached answer-token sequence for {record['id']}")
    if len(answer_ids) != len(answer["token_logprobs"]):
        raise ValueError(f"Answer token/log-probability mismatch for {record['id']}")
    stop_ids = {
        int(value)
        for value in (tokenizer.eos_token_id, tokenizer.pad_token_id)
        if value is not None
    }
    if any(token_id in stop_ids for token_id in answer_ids):
        raise ValueError(f"EOS or padding appears inside cached answer content for {record['id']}")
    if tokenizer.decode(answer_ids, skip_special_tokens=True).strip() != answer["text"]:
        raise ValueError(f"Cached answer IDs do not decode to cached answer text for {record['id']}")

    full_ids = [int(value) for value in prompt_ids] + answer_ids
    answer_start = len(prompt_ids)
    answer_stop = len(full_ids)
    if full_ids[answer_start:answer_stop] != answer_ids:
        raise RuntimeError("Appended answer token IDs changed unexpectedly")
    if answer_stop - 1 != int(record["prompt_token_count"]) + len(answer_ids) - 1:
        raise RuntimeError("Final answer-token location is inconsistent")
    return {
        "prompt_ids": prompt_ids,
        "answer_ids": answer_ids,
        "full_ids": full_ids,
        "prompt_length": len(prompt_ids),
        "answer_length": len(answer_ids),
        "answer_start_index": answer_start,
        "answer_stop_index_exclusive": answer_stop,
        "final_answer_token_index": answer_stop - 1,
        "prompt_ids_sha256": stable_hash(prompt_ids),
        "answer_ids_sha256": stable_hash(answer_ids),
        "full_ids_sha256": stable_hash(full_ids),
    }


def _state_cache_path(
    config: dict[str, Any],
    state_cache_dir: Path,
    source_index: int,
    record: dict[str, Any],
    observed_answer_index: int,
) -> Path:
    fingerprint = stable_hash(
        {
            "version": 2,
            "id": record["id"],
            "prompt": record["prompt"],
            "answer_token_ids": record["generations"][observed_answer_index]["token_ids"],
            "observed_answer_index": observed_answer_index,
            "layers": [14, 23],
            "model": {
                "id": config["model"]["id"],
                "revision": config["model"]["revision"],
                "attn_implementation": config["model"].get("attn_implementation"),
                "max_prompt_tokens": config["model"]["max_prompt_tokens"],
            },
            "inference_dtype": config["device"]["dtype"],
            "tokenizer_truncation_side": "left",
        }
    )[:16]
    return state_cache_dir / f"answer_{observed_answer_index}" / f"{source_index:04d}_{fingerprint}.npz"


def _load_generator(config: dict[str, Any]) -> tuple[Any, Any, torch.device, torch.dtype]:
    model_config = config["model"]
    device = choose_device(config["device"]["preference"])
    dtype = choose_dtype(config["device"]["dtype"], device)
    cache_dir = _resolve(model_config["hf_cache_dir"])
    repository_cache_name = "models--" + model_config["id"].replace("/", "--")
    snapshot_path = (
        cache_dir
        / repository_cache_name
        / "snapshots"
        / str(model_config["revision"])
    )
    if bool(model_config.get("local_files_only", True)):
        if not snapshot_path.is_dir():
            raise FileNotFoundError(
                f"Pinned local model snapshot is missing: {snapshot_path}; refusing to download"
            )
        model_source = str(snapshot_path)
        revision_kwargs: dict[str, Any] = {}
    else:
        model_source = model_config["id"]
        revision_kwargs = {"revision": model_config["revision"]}
    tokenizer = AutoTokenizer.from_pretrained(
        model_source,
        **revision_kwargs,
        cache_dir=cache_dir,
        local_files_only=bool(model_config.get("local_files_only", True)),
    )
    tokenizer.truncation_side = "left"
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token_id = tokenizer.eos_token_id
    model = AutoModelForCausalLM.from_pretrained(
        model_source,
        **revision_kwargs,
        cache_dir=cache_dir,
        local_files_only=bool(model_config.get("local_files_only", True)),
        trust_remote_code=bool(model_config.get("trust_remote_code", False)),
        dtype=dtype,
        attn_implementation=model_config.get("attn_implementation", "eager"),
        low_cpu_mem_usage=True,
    ).to(device)
    model.eval()
    return tokenizer, model, device, dtype


def extract_post_answer_states(
    config: dict[str, Any],
    records: list[dict[str, Any]],
    source_manifest: dict[str, Any],
    observed_answer_index: int,
    limit: int | None = None,
) -> tuple[dict[str, np.ndarray], list[dict[str, Any]], dict[str, Any]]:
    """Teacher-force cached sequences, saving every completed row for resume."""

    count = len(records) if limit is None else min(int(limit), len(records))
    selected_records = records[:count]
    state_cache_dir = _resolve(config["output"]["resumable_state_cache"])
    primary_layer = int(config["experiment"]["primary_layer"])
    exploratory_layer = int(config["experiment"]["exploratory_layer"])
    if (primary_layer, exploratory_layer) != (14, 23):
        raise ValueError("This frozen Stage 0B implementation expects layers 14 and 23")

    tokenizer, model, device, dtype = _load_generator(config)
    source_dataset = source_manifest["configuration"]["dataset"]
    max_prompt_tokens = int(config["model"]["max_prompt_tokens"])
    hidden_width = int(model.config.hidden_size)
    if int(model.config.num_hidden_layers) < exploratory_layer:
        raise ValueError("Exploratory layer is outside the cached generator")

    final_primary_rows: list[np.ndarray] = []
    mean_primary_rows: list[np.ndarray] = []
    final_exploratory_rows: list[np.ndarray] = []
    metadata_rows: list[dict[str, Any]] = []
    cache_hits = 0
    forward_calls = 0
    started = time.monotonic()
    try:
        for source_index, record in enumerate(selected_records):
            tokens = verify_cached_tokenization(
                record,
                observed_answer_index,
                tokenizer,
                source_dataset,
                max_prompt_tokens,
            )
            cache_path = _state_cache_path(
                config, state_cache_dir, source_index, record, observed_answer_index
            )
            was_cache_hit = cache_path.exists()
            if was_cache_hit:
                with np.load(cache_path) as archive:
                    representations = {
                        "layer_14_final_answer_token": archive[
                            "layer_14_final_answer_token"
                        ].astype(np.float16),
                        "layer_14_mean_answer_tokens": archive[
                            "layer_14_mean_answer_tokens"
                        ].astype(np.float16),
                        "layer_23_final_answer_token": archive[
                            "layer_23_final_answer_token"
                        ].astype(np.float16),
                    }
                    cached_full_hash = str(archive["full_ids_sha256"].item())
                if cached_full_hash != tokens["full_ids_sha256"]:
                    raise ValueError(f"State-cache token fingerprint mismatch for {record['id']}")
                cache_hits += 1
            else:
                input_ids = torch.tensor(
                    [tokens["full_ids"]], dtype=torch.long, device=device
                )
                attention_mask = torch.ones_like(input_ids)
                try:
                    with torch.inference_mode():
                        output = model(
                            input_ids=input_ids,
                            attention_mask=attention_mask,
                            output_hidden_states=True,
                            use_cache=False,
                            return_dict=True,
                        )
                except (RuntimeError, NotImplementedError):
                    if device.type != "mps" or not config["device"].get("allow_cpu_fallback", True):
                        raise
                    del input_ids, attention_mask
                    model = model.to(device="cpu", dtype=torch.float32)
                    device, dtype = torch.device("cpu"), torch.float32
                    clear_device_cache()
                    input_ids = torch.tensor([tokens["full_ids"]], dtype=torch.long)
                    attention_mask = torch.ones_like(input_ids)
                    with torch.inference_mode():
                        output = model(
                            input_ids=input_ids,
                            attention_mask=attention_mask,
                            output_hidden_states=True,
                            use_cache=False,
                            return_dict=True,
                        )
                representations = select_answer_representations(
                    output.hidden_states,
                    tokens["prompt_length"],
                    tokens["answer_length"],
                    primary_layer,
                    exploratory_layer,
                )
                forward_calls += 1
                if not all(
                    np.all(np.isfinite(representations[key]))
                    for key in (
                        "layer_14_final_answer_token",
                        "layer_14_mean_answer_tokens",
                        "layer_23_final_answer_token",
                    )
                ):
                    raise ValueError(f"Non-finite post-answer state for {record['id']}")
                _atomic_npz(
                    cache_path,
                    {
                        **representations,
                        "record_id": np.asarray(str(record["id"])),
                        "source_index": np.asarray(source_index, dtype=np.int64),
                        "observed_answer_index": np.asarray(
                            observed_answer_index, dtype=np.int64
                        ),
                        "full_ids_sha256": np.asarray(tokens["full_ids_sha256"]),
                    },
                )
                del output, input_ids, attention_mask

            final_primary_rows.append(representations["layer_14_final_answer_token"])
            mean_primary_rows.append(representations["layer_14_mean_answer_tokens"])
            final_exploratory_rows.append(representations["layer_23_final_answer_token"])
            metadata_rows.append(
                {
                    "source_index": source_index,
                    "id": record["id"],
                    "observed_answer_index": int(observed_answer_index),
                    "prompt_token_count": int(tokens["prompt_length"]),
                    "answer_token_count": int(tokens["answer_length"]),
                    "answer_start_index": int(tokens["answer_start_index"]),
                    "answer_stop_index_exclusive": int(tokens["answer_stop_index_exclusive"]),
                    "final_answer_token_index": int(tokens["final_answer_token_index"]),
                    "prompt_ids_sha256": tokens["prompt_ids_sha256"],
                    "answer_ids_sha256": tokens["answer_ids_sha256"],
                    "full_ids_sha256": tokens["full_ids_sha256"],
                    "prompt_text_reconstructed_exactly": True,
                    "answer_ids_appended_exactly": True,
                    "pooling_span_excludes_prompt_eos_and_padding": True,
                    "state_cache_hit": bool(was_cache_hit),
                }
            )
            if count > 20 and (source_index + 1) % 100 == 0:
                print(f"post-answer states: {source_index + 1}/{count}", flush=True)
    finally:
        del model, tokenizer
        clear_device_cache()

    arrays = {
        "layer_14_final_answer_token": np.stack(final_primary_rows).astype(np.float16),
        "layer_14_mean_answer_tokens": np.stack(mean_primary_rows).astype(np.float16),
        "layer_23_final_answer_token": np.stack(final_exploratory_rows).astype(np.float16),
        "source_indices": np.arange(count, dtype=np.int64),
        "example_ids": np.asarray([str(record["id"]) for record in selected_records]),
        "observed_answer_indices": np.full(count, observed_answer_index, dtype=np.int16),
        "prompt_token_counts": np.asarray(
            [row["prompt_token_count"] for row in metadata_rows], dtype=np.int16
        ),
        "answer_token_counts": np.asarray(
            [row["answer_token_count"] for row in metadata_rows], dtype=np.int16
        ),
        "final_answer_token_indices": np.asarray(
            [row["final_answer_token_index"] for row in metadata_rows], dtype=np.int16
        ),
    }
    for key in (
        "layer_14_final_answer_token",
        "layer_14_mean_answer_tokens",
        "layer_23_final_answer_token",
    ):
        if arrays[key].shape != (count, hidden_width) or not np.all(np.isfinite(arrays[key])):
            raise ValueError(f"Invalid extracted hidden-state array {key}: {arrays[key].shape}")
    runtime = {
        "device": str(device),
        "dtype": str(dtype).replace("torch.", ""),
        "model_id": config["model"]["id"],
        "model_revision": config["model"]["revision"],
        "hidden_width": hidden_width,
        "examples": count,
        "teacher_forced_forward_calls": int(forward_calls),
        "resumable_state_cache_hits": int(cache_hits),
        "generation_calls": 0,
        "nli_model_calls": 0,
        "elapsed_seconds": float(time.monotonic() - started),
    }
    return arrays, metadata_rows, runtime


def _classifier(c_value: float, seed: int, max_iter: int) -> Any:
    return make_pipeline(
        StandardScaler(),
        LogisticRegression(C=float(c_value), max_iter=int(max_iter), random_state=int(seed)),
    )


def cross_fitted_probe_scores(
    features: np.ndarray,
    labels: np.ndarray,
    groups: np.ndarray,
    train_indices: np.ndarray,
    n_splits: int,
    c_value: float,
    seed: int,
    max_iter: int = 3000,
) -> tuple[np.ndarray, Any, list[dict[str, Any]]]:
    """Return one group-held-out decision score per training row and a full-train model."""

    train_indices = np.asarray(train_indices, dtype=np.int64)
    train_features = np.asarray(features, dtype=np.float32)[train_indices]
    train_labels = np.asarray(labels, dtype=np.int64)[train_indices]
    train_groups = np.asarray(groups)[train_indices]
    if np.unique(train_labels).size != 2:
        raise ValueError("Cross-fitting training labels contain only one class")
    splitter = StratifiedGroupKFold(
        n_splits=int(n_splits), shuffle=True, random_state=int(seed)
    )
    scores = np.full(len(train_indices), np.nan, dtype=np.float64)
    hit_count = np.zeros(len(train_indices), dtype=np.int64)
    ledger = []
    for fold, (fit_local, heldout_local) in enumerate(
        splitter.split(train_features, train_labels, train_groups)
    ):
        overlap = set(train_groups[fit_local].tolist()) & set(
            train_groups[heldout_local].tolist()
        )
        if overlap:
            raise RuntimeError("Cross-fitted probe leaked normalized contexts")
        if np.unique(train_labels[fit_local]).size != 2:
            raise ValueError(f"Cross-fit fold {fold} training data has one class")
        model = _classifier(c_value, seed + fold, max_iter)
        model.fit(train_features[fit_local], train_labels[fit_local])
        scores[heldout_local] = model.decision_function(train_features[heldout_local])
        hit_count[heldout_local] += 1
        ledger.append(
            {
                "fold": fold,
                "fit_source_indices": train_indices[fit_local].tolist(),
                "heldout_source_indices": train_indices[heldout_local].tolist(),
                "fit_size": int(len(fit_local)),
                "heldout_size": int(len(heldout_local)),
                "fit_unique_contexts": int(len(np.unique(train_groups[fit_local]))),
                "heldout_unique_contexts": int(len(np.unique(train_groups[heldout_local]))),
                "context_overlap": 0,
            }
        )
    if not np.all(hit_count == 1) or not np.all(np.isfinite(scores)):
        raise RuntimeError("Cross-fitted score ledger is incomplete")
    final_model = _classifier(c_value, seed, max_iter)
    final_model.fit(train_features, train_labels)
    return scores, final_model, ledger


def _spearman(first: np.ndarray, second: np.ndarray) -> float | None:
    if np.unique(first).size < 2 or np.unique(second).size < 2:
        return None
    statistic = float(spearmanr(first, second).statistic)
    return statistic if np.isfinite(statistic) else None


def _point_metrics(labels: np.ndarray, probabilities: np.ndarray) -> dict[str, Any]:
    probabilities = np.clip(np.asarray(probabilities, dtype=np.float64), 1e-7, 1 - 1e-7)
    predictions = (probabilities >= 0.5).astype(np.int64)
    return {
        "accuracy": float(accuracy_score(labels, predictions)),
        "auroc": float(roc_auc_score(labels, probabilities)),
        "log_loss": float(log_loss(labels, probabilities, labels=[0, 1])),
    }


def _heldout_metrics(
    labels: np.ndarray,
    probabilities: np.ndarray,
    groups: np.ndarray,
    entropy: np.ndarray,
    score_for_spearman: np.ndarray,
    bootstrap_samples: int,
    bootstrap_seed: int,
) -> dict[str, Any]:
    metrics = _point_metrics(labels, probabilities)
    metrics["auroc_context_bootstrap_95"] = grouped_bootstrap_interval(
        labels,
        probabilities,
        groups,
        samples=bootstrap_samples,
        seed=bootstrap_seed,
        metric="auroc",
    )
    metrics["log_loss_context_bootstrap_95"] = grouped_bootstrap_interval(
        labels,
        probabilities,
        groups,
        samples=bootstrap_samples,
        seed=bootstrap_seed + 1,
        metric="log_loss",
    )
    metrics["continuous_entropy_spearman"] = _spearman(entropy, score_for_spearman)
    return metrics


def _fit_scalar_baseline(
    values: np.ndarray,
    labels: np.ndarray,
    train_indices: np.ndarray,
    validation_indices: np.ndarray,
    test_indices: np.ndarray,
    seed: int,
    max_iter: int,
) -> tuple[dict[str, np.ndarray], Any]:
    features = np.asarray(values, dtype=np.float64).reshape(-1, 1)
    model = _classifier(1.0, seed, max_iter)
    model.fit(features[train_indices], labels[train_indices])
    output = {}
    for name, indices in (
        ("validation", validation_indices),
        ("test", test_indices),
    ):
        output[name] = model.predict_proba(features[indices])[:, 1]
    return output, model


def _continuous_ridge_metrics(
    features: np.ndarray,
    entropy: np.ndarray,
    train_indices: np.ndarray,
    validation_indices: np.ndarray,
    test_indices: np.ndarray,
    alpha: float,
) -> dict[str, Any]:
    model = make_pipeline(StandardScaler(), Ridge(alpha=float(alpha), solver="lsqr"))
    model.fit(features[train_indices], entropy[train_indices])
    result = {}
    for name, indices in (("validation", validation_indices), ("test", test_indices)):
        predictions = model.predict(features[indices])
        result[name] = {
            "spearman": _spearman(entropy[indices], predictions),
            "rmse": float(math.sqrt(mean_squared_error(entropy[indices], predictions))),
            "r2": float(r2_score(entropy[indices], predictions)),
        }
    return result


def analyze_answer_states(
    config: dict[str, Any],
    records: list[dict[str, Any]],
    target_rows: list[dict[str, Any]],
    labels: np.ndarray,
    entropy: np.ndarray,
    state_arrays: dict[str, np.ndarray],
    split: dict[str, Any],
    source_semantic_rows: list[dict[str, Any]] | None = None,
) -> tuple[dict[str, Any], dict[str, np.ndarray]]:
    """Fit fixed probes/baselines and score the untouched source test split."""

    analysis = config["analysis"]
    seed = int(analysis["seed"])
    max_iter = int(analysis["max_iter"])
    c_value = float(analysis["classifier_c"])
    bootstrap_samples = int(analysis["bootstrap_samples"])
    bootstrap_seed = int(analysis["bootstrap_seed"])
    train = np.asarray(split["train"], dtype=np.int64)
    validation = np.asarray(split["validation"], dtype=np.int64)
    test = np.asarray(split["test"], dtype=np.int64)
    groups = np.asarray(split["groups"])
    for name, indices in (("train", train), ("validation", validation), ("test", test)):
        if np.unique(labels[indices]).size != 2:
            raise ValueError(f"{name} split contains only one Stage 0B target class")

    same_sequence_nll = np.asarray(
        [row["same_answer_sequence_nll"] for row in target_rows], dtype=np.float64
    )
    same_mean_nll = np.asarray(
        [row["same_answer_mean_token_nll"] for row in target_rows], dtype=np.float64
    )
    answer_length = np.asarray(
        [row["observed_answer_token_count"] for row in target_rows], dtype=np.float64
    )
    answer_text = [row["observed_answer_text"] for row in target_rows]

    prediction_arrays: dict[str, np.ndarray] = {}
    baselines: dict[str, Any] = {}
    scalar_values = {
        "same_answer_sequence_nll": same_sequence_nll,
        "same_answer_mean_token_nll": same_mean_nll,
        "answer_token_length": answer_length,
    }
    for offset, (name, values) in enumerate(scalar_values.items()):
        probabilities, _ = _fit_scalar_baseline(
            values, labels, train, validation, test, seed + offset, max_iter
        )
        prediction_arrays[name] = probabilities["test"]
        baselines[name] = {
            "information_budget": "one observed cached answer",
            "validation": _point_metrics(labels[validation], probabilities["validation"]),
            "test": _heldout_metrics(
                labels[test],
                probabilities["test"],
                groups[test],
                entropy[test],
                values[test],
                bootstrap_samples,
                bootstrap_seed + 100 * offset,
            ),
        }

    train_mean = float(labels[train].mean())
    constant_validation = np.full(len(validation), train_mean, dtype=np.float64)
    constant_test = np.full(len(test), train_mean, dtype=np.float64)
    baselines["constant_train_mean"] = {
        "train_positive_fraction": train_mean,
        "validation": _point_metrics(labels[validation], constant_validation),
        "test": _heldout_metrics(
            labels[test],
            constant_test,
            groups[test],
            entropy[test],
            constant_test,
            bootstrap_samples,
            bootstrap_seed + 300,
        ),
    }

    lexical_values = np.asarray(
        [
            [
                len(text),
                len(text.split()),
                len(set(text.lower().split())),
                sum(character.isdigit() for character in text),
                sum(not character.isalnum() and not character.isspace() for character in text),
            ]
            for text in answer_text
        ],
        dtype=np.float64,
    )
    lexical_model = _classifier(1.0, seed + 20, max_iter)
    lexical_model.fit(lexical_values[train], labels[train])
    lexical_validation = lexical_model.predict_proba(lexical_values[validation])[:, 1]
    lexical_test = lexical_model.predict_proba(lexical_values[test])[:, 1]
    prediction_arrays["simple_lexical_controls"] = lexical_test
    baselines["simple_lexical_controls"] = {
        "features": [
            "character_count",
            "whitespace_word_count",
            "unique_lowercase_word_count",
            "digit_count",
            "punctuation_count",
        ],
        "information_budget": "one observed answer text",
        "validation": _point_metrics(labels[validation], lexical_validation),
        "test": _heldout_metrics(
            labels[test],
            lexical_test,
            groups[test],
            entropy[test],
            lexical_test,
            bootstrap_samples,
            bootstrap_seed + 400,
        ),
    }

    tfidf_model = make_pipeline(
        TfidfVectorizer(
            lowercase=True,
            ngram_range=(1, 2),
            min_df=2,
            max_features=int(analysis["tfidf_max_features"]),
        ),
        LogisticRegression(C=1.0, max_iter=max_iter, random_state=seed + 30),
    )
    tfidf_model.fit([answer_text[index] for index in train], labels[train])
    tfidf_validation = tfidf_model.predict_proba(
        [answer_text[index] for index in validation]
    )[:, 1]
    tfidf_test = tfidf_model.predict_proba([answer_text[index] for index in test])[:, 1]
    prediction_arrays["tfidf_answer_text"] = tfidf_test
    baselines["tfidf_answer_text"] = {
        "information_budget": "one observed answer text; vocabulary fit on training only",
        "validation": _point_metrics(labels[validation], tfidf_validation),
        "test": _heldout_metrics(
            labels[test],
            tfidf_test,
            groups[test],
            entropy[test],
            tfidf_test,
            bootstrap_samples,
            bootstrap_seed + 500,
        ),
    }

    contextual_baselines: dict[str, Any] = {}
    if source_semantic_rows is not None:
        if len(source_semantic_rows) != len(records):
            raise ValueError("Source semantic-entropy rows do not align with generations")
        for offset, field in enumerate(
            ("predictive_entropy", "answer_negative_log_likelihood")
        ):
            values = np.asarray([row[field] for row in source_semantic_rows], dtype=np.float64)
            probabilities, _ = _fit_scalar_baseline(
                values,
                labels,
                train,
                validation,
                test,
                seed + 40 + offset,
                max_iter,
            )
            prediction_arrays[f"contextual_ten_answer_{field}"] = probabilities["test"]
            contextual_baselines[field] = {
                "information_budget": (
                    "all ten sampled answers; larger budget and target-answer overlap; contextual only"
                ),
                "validation": _point_metrics(
                    labels[validation], probabilities["validation"]
                ),
                "test": _heldout_metrics(
                    labels[test],
                    probabilities["test"],
                    groups[test],
                    entropy[test],
                    values[test],
                    bootstrap_samples,
                    bootstrap_seed + 600 + 100 * offset,
                ),
            }

    representations = {
        "layer_14_final_answer_token": {
            "role": "primary",
            "features": state_arrays["layer_14_final_answer_token"].astype(np.float32),
        },
        "layer_14_mean_answer_tokens": {
            "role": "secondary_robustness",
            "features": state_arrays["layer_14_mean_answer_tokens"].astype(np.float32),
        },
        "layer_23_final_answer_token": {
            "role": "exploratory",
            "features": state_arrays["layer_23_final_answer_token"].astype(np.float32),
        },
    }
    probe_results: dict[str, Any] = {}
    fitted_models = {}
    for offset, (name, specification) in enumerate(representations.items()):
        features = specification["features"]
        model = _classifier(c_value, seed + 100 + offset, max_iter)
        model.fit(features[train], labels[train])
        validation_probabilities = model.predict_proba(features[validation])[:, 1]
        test_probabilities = model.predict_proba(features[test])[:, 1]
        test_scores = model.decision_function(features[test])
        prediction_arrays[name] = test_probabilities
        fitted_models[name] = model
        probe_results[name] = {
            "role": specification["role"],
            "layer_selection": "predeclared; no all-layer scan",
            "validation": _point_metrics(labels[validation], validation_probabilities),
            "test": _heldout_metrics(
                labels[test],
                test_probabilities,
                groups[test],
                entropy[test],
                test_scores,
                bootstrap_samples,
                bootstrap_seed + 1000 + 100 * offset,
            ),
            "continuous_ridge": _continuous_ridge_metrics(
                features,
                entropy,
                train,
                validation,
                test,
                float(analysis["ridge_alpha"]),
            ),
        }

    primary_name = "layer_14_final_answer_token"
    primary_features = representations[primary_name]["features"]
    oof_scores, final_primary_model, cross_fit_ledger = cross_fitted_probe_scores(
        primary_features,
        labels,
        groups,
        train,
        int(analysis["cross_fit_folds"]),
        c_value,
        seed + 2000,
        max_iter,
    )
    validation_probe_scores = final_primary_model.decision_function(
        primary_features[validation]
    )
    test_probe_scores = final_primary_model.decision_function(primary_features[test])
    meta_train = np.column_stack([same_sequence_nll[train], oof_scores])
    meta_validation = np.column_stack(
        [same_sequence_nll[validation], validation_probe_scores]
    )
    meta_test = np.column_stack([same_sequence_nll[test], test_probe_scores])
    meta_model = _classifier(1.0, seed + 3000, max_iter)
    meta_model.fit(meta_train, labels[train])
    combined_validation = meta_model.predict_proba(meta_validation)[:, 1]
    combined_test = meta_model.predict_proba(meta_test)[:, 1]
    prediction_arrays["sequence_nll_plus_cross_fitted_probe_score"] = combined_test
    combined = {
        "features": ["same_answer_sequence_nll", "cross_fitted_layer_14_probe_decision_score"],
        "full_hidden_vector_concatenated": False,
        "meta_training_probe_scores": "five-fold context-grouped out-of-fold scores on source training split",
        "validation": _point_metrics(labels[validation], combined_validation),
        "test": _heldout_metrics(
            labels[test],
            combined_test,
            groups[test],
            entropy[test],
            meta_model.decision_function(meta_test),
            bootstrap_samples,
            bootstrap_seed + 2000,
        ),
        "cross_fit": {
            "folds": int(analysis["cross_fit_folds"]),
            "training_rows_scored_once": True,
            "test_rows_used_in_fitting": False,
            "fold_ledger": cross_fit_ledger,
        },
    }

    nll_test = prediction_arrays["same_answer_sequence_nll"]
    paired = {
        "combined_minus_sequence_nll_auroc": grouped_bootstrap_interval(
            labels[test],
            combined_test,
            groups[test],
            samples=bootstrap_samples,
            seed=bootstrap_seed + 3000,
            metric="auroc",
            reference_probabilities=nll_test,
        ),
        "sequence_nll_minus_combined_log_loss": grouped_bootstrap_interval(
            labels[test],
            nll_test,
            groups[test],
            samples=bootstrap_samples,
            seed=bootstrap_seed + 3001,
            metric="log_loss",
            reference_probabilities=combined_test,
        ),
        "hidden_probe_minus_sequence_nll_auroc": grouped_bootstrap_interval(
            labels[test],
            prediction_arrays[primary_name],
            groups[test],
            samples=bootstrap_samples,
            seed=bootstrap_seed + 3002,
            metric="auroc",
            reference_probabilities=nll_test,
        ),
    }

    shuffle_rng = np.random.default_rng(int(analysis["shuffle_seed"]))
    shuffle_values = []
    for repetition in range(int(analysis["shuffle_repetitions"])):
        shuffled_labels = shuffle_rng.permutation(labels[train])
        shuffled_model = _classifier(
            c_value, int(analysis["shuffle_seed"]) + repetition, max_iter
        )
        shuffled_model.fit(primary_features[train], shuffled_labels)
        probabilities = shuffled_model.predict_proba(primary_features[test])[:, 1]
        shuffle_values.append(float(roc_auc_score(labels[test], probabilities)))
    shuffled = np.asarray(shuffle_values, dtype=np.float64)
    shuffled_control = {
        "representation": primary_name,
        "training_labels_only_shuffled": True,
        "test_labels_untouched": True,
        "repetitions": int(len(shuffled)),
        "test_auroc_mean": float(shuffled.mean()),
        "test_auroc_std": float(shuffled.std()),
        "test_auroc_empirical_95": [
            float(np.percentile(shuffled, 2.5)),
            float(np.percentile(shuffled, 97.5)),
        ],
        "test_auroc_values": shuffled.tolist(),
    }

    result = {
        "experiment": "Stage 0B post-answer hidden-state diagnostic",
        "interpretation_scope": (
            "Tests incremental semantic-uncertainty information after one cached answer; "
            "not subjective confidence, causality, steering, or a training-loss validation."
        ),
        "observed_answer_index": int(target_rows[0]["observed_answer_index"]),
        "target": {
            "name": "leave_one_out_nine_answer_semantic_entropy",
            "continuous_entropy_unique_values": int(len(np.unique(entropy))),
            "continuous_entropy_mean": float(entropy.mean()),
            "continuous_entropy_std": float(entropy.std()),
            "threshold_fit_on_training_only": float(
                target_rows[0]["threshold_fit_on_training_only"]
            ),
            "label_distribution": {
                "train": _class_counts(labels, train),
                "validation": _class_counts(labels, validation),
                "test": _class_counts(labels, test),
            },
        },
        "split": split["audit"],
        "baselines": baselines,
        "contextual_multi_sample_baselines": contextual_baselines,
        "probes": probe_results,
        "combined_sequence_nll_plus_scalar_probe": combined,
        "paired_test_differences": paired,
        "shuffled_label_control": shuffled_control,
        "primary_comparison": {
            "same_answer_sequence_nll_test": baselines["same_answer_sequence_nll"]["test"],
            "post_answer_layer_14_probe_test": probe_results[primary_name]["test"],
            "combined_test": combined["test"],
            "combined_minus_sequence_nll_auroc": paired[
                "combined_minus_sequence_nll_auroc"
            ],
            "sequence_nll_minus_combined_log_loss": paired[
                "sequence_nll_minus_combined_log_loss"
            ],
        },
    }
    return result, prediction_arrays


def _load_sources(config: dict[str, Any]) -> dict[str, Any]:
    paths = {
        name: _resolve(config["source"][name])
        for name in (
            "generations",
            "semantic_entropy",
            "probe_metrics",
            "manifest",
            "nli_cache",
        )
    }
    hashes = {}
    for name, path in paths.items():
        if not path.exists():
            raise FileNotFoundError(f"Missing required cached artifact: {path}")
        observed = _sha256(path)
        expected = str(config["source"]["expected_sha256"][name])
        if observed != expected:
            raise ValueError(f"Source hash mismatch for {name}: {observed} != {expected}")
        hashes[name] = observed

    records = _read_jsonl(paths["generations"])
    source_semantic_rows = _read_jsonl(paths["semantic_entropy"])
    with paths["probe_metrics"].open("r", encoding="utf-8") as handle:
        source_probe = json.load(handle)
    with paths["manifest"].open("r", encoding="utf-8") as handle:
        source_manifest = json.load(handle)
    with paths["nli_cache"].open("r", encoding="utf-8") as handle:
        nli_cache = json.load(handle)

    expected_examples = int(config["experiment"]["expected_examples"])
    expected_generations = int(
        config["experiment"]["expected_generations_per_question"]
    )
    if len(records) != expected_examples or len(source_semantic_rows) != expected_examples:
        raise ValueError("Source cached row count differs from the frozen Stage 0B design")
    if any(len(record["generations"]) != expected_generations for record in records):
        raise ValueError("A source question does not contain ten cached generations")
    if [str(record["id"]) for record in records] != [
        str(row["id"]) for row in source_semantic_rows
    ]:
        raise ValueError("Generation and source semantic-entropy row order differs")
    source_generator = source_manifest["configuration"]["models"]["generator"]["id"]
    if source_generator != config["model"]["id"]:
        raise ValueError("Configured generator differs from the source run")
    source_nli_model = source_manifest["configuration"]["models"]["entailment"]["id"]
    split = validate_preserved_split(
        records,
        source_probe,
        config["experiment"].get("expected_split_sizes"),
    )
    return {
        "paths": paths,
        "hashes": hashes,
        "records": records,
        "source_semantic_rows": source_semantic_rows,
        "source_probe": source_probe,
        "source_manifest": source_manifest,
        "nli_cache": nli_cache,
        "nli_model_id": source_nli_model,
        "split": split,
    }


def _plot_comparison(
    config: dict[str, Any], metrics: dict[str, Any]
) -> Path:
    rows = [
        (
            "Same-answer\nsequence NLL",
            metrics["baselines"]["same_answer_sequence_nll"]["test"],
            "tab:gray",
        ),
        (
            "Layer 14\nfinal token",
            metrics["probes"]["layer_14_final_answer_token"]["test"],
            "tab:blue",
        ),
        (
            "NLL + scalar\nprobe score",
            metrics["combined_sequence_nll_plus_scalar_probe"]["test"],
            "tab:green",
        ),
        (
            "Layer 14\nanswer mean",
            metrics["probes"]["layer_14_mean_answer_tokens"]["test"],
            "tab:orange",
        ),
        (
            "Layer 23\nfinal token",
            metrics["probes"]["layer_23_final_answer_token"]["test"],
            "tab:purple",
        ),
    ]
    values = [row[1]["auroc"] for row in rows]
    lowers = [row[1]["auroc_context_bootstrap_95"]["lower_95"] for row in rows]
    uppers = [row[1]["auroc_context_bootstrap_95"]["upper_95"] for row in rows]
    errors = [
        [value - lower for value, lower in zip(values, lowers)],
        [upper - value for value, upper in zip(values, uppers)],
    ]
    figure, axis = plt.subplots(figsize=(8.5, 5.2))
    positions = np.arange(len(rows))
    axis.bar(positions, values, color=[row[2] for row in rows], alpha=0.82)
    axis.errorbar(
        positions,
        values,
        yerr=errors,
        fmt="none",
        ecolor="black",
        capsize=4,
        linewidth=1.3,
    )
    axis.axhline(0.5, color="black", linestyle="--", linewidth=1, alpha=0.65)
    axis.set_xticks(positions, [row[0] for row in rows])
    axis.set_ylabel("Held-out AUROC")
    axis.set_ylim(0.35, 1.0)
    axis.set_title("Stage 0B: predicting nine-answer semantic uncertainty")
    axis.text(
        0.99,
        0.02,
        "Error bars: 95% context-grouped bootstrap intervals",
        transform=axis.transAxes,
        ha="right",
        va="bottom",
        fontsize=9,
        color="dimgray",
    )
    figure.tight_layout()
    path = _resolve(config["output"]["plot"])
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(path, dpi=180)
    plt.close(figure)
    return path


def _versions() -> dict[str, Any]:
    return {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "torch": torch.__version__,
        "transformers": transformers.__version__,
        "numpy": np.__version__,
        "scikit_learn": sklearn.__version__,
        "mps_built": bool(torch.backends.mps.is_built()),
        "mps_available": bool(torch.backends.mps.is_available()),
        "cuda_available": bool(torch.cuda.is_available()),
    }


def run_stage0b(config_path: str | Path, mode: str = "full") -> dict[str, Any]:
    """Run the sanity gate or complete Stage 0B primary answer-index-0 analysis."""

    if mode not in {"sanity", "full"}:
        raise ValueError("mode must be 'sanity' or 'full'")
    started = time.monotonic()
    config = load_stage0b_config(config_path)
    sources = _load_sources(config)
    records = sources["records"]
    split = sources["split"]
    observed_index = int(config["experiment"]["primary_observed_answer_index"])
    nli_path = sources["paths"]["nli_cache"]
    nli_hash_before = _sha256(nli_path)
    coverage = audit_nli_coverage(
        records,
        observed_index,
        sources["nli_cache"],
        sources["nli_model_id"],
    )
    target_rows, labels, threshold, used_judgments = build_leave_one_out_targets(
        records,
        observed_index,
        sources["nli_cache"],
        sources["nli_model_id"],
        split["train"],
    )
    entropy = np.asarray(
        [row["leave_one_out_semantic_entropy"] for row in target_rows],
        dtype=np.float64,
    )
    sanity_count = int(config["experiment"]["sanity_examples"])
    sanity_arrays, sanity_metadata, sanity_runtime = extract_post_answer_states(
        config,
        records,
        sources["source_manifest"],
        observed_index,
        limit=sanity_count,
    )
    nli_hash_after_sanity = _sha256(nli_path)
    sanity_labels = labels[:sanity_count]
    sanity_checks = {
        "no_answer_generation": sanity_runtime["generation_calls"] == 0,
        "no_nli_model_calls": sanity_runtime["nli_model_calls"] == 0,
        "nli_cache_unchanged": nli_hash_before == nli_hash_after_sanity,
        "all_required_nli_judgments_cached": coverage["missing_cached_judgments"] == 0,
        "cached_prompt_reconstructed_and_token_metadata_matched": all(
            row["prompt_text_reconstructed_exactly"] for row in sanity_metadata
        ),
        "cached_answer_ids_appended_exactly": all(
            row["answer_ids_appended_exactly"] for row in sanity_metadata
        ),
        "final_answer_token_locations_correct": all(
            row["final_answer_token_index"]
            == row["prompt_token_count"] + row["answer_token_count"] - 1
            for row in sanity_metadata
        ),
        "layer_14_hidden_states_finite": bool(
            np.all(np.isfinite(sanity_arrays["layer_14_final_answer_token"]))
            and np.all(np.isfinite(sanity_arrays["layer_14_mean_answer_tokens"]))
        ),
        "mean_pooling_excludes_prompt_eos_and_padding": all(
            row["pooling_span_excludes_prompt_eos_and_padding"]
            for row in sanity_metadata
        ),
        "sanity_leave_one_out_entropy_varies": bool(
            np.unique(entropy[:sanity_count]).size > 1
        ),
        "sanity_binary_labels_non_degenerate": bool(np.unique(sanity_labels).size == 2),
        "source_split_membership_preserved": bool(
            split["audit"]["source_membership_reused_exactly"]
        ),
        "source_context_split_has_zero_overlap": all(
            value == 0 for value in split["audit"]["context_overlap_counts"].values()
        ),
    }
    sanity_passed = all(sanity_checks.values())
    results_dir = _resolve(config["output"]["results_dir"])
    results_dir.mkdir(parents=True, exist_ok=True)
    sanity_report = {
        "passed": sanity_passed,
        "checks": sanity_checks,
        "examples": sanity_count,
        "observed_answer_index": observed_index,
        "leave_one_out_threshold_fit_on_full_source_training_split": threshold,
        "sanity_label_distribution": {
            str(key): int(value) for key, value in Counter(sanity_labels.tolist()).items()
        },
        "nli_coverage": coverage,
        "split_audit": split["audit"],
        "runtime": sanity_runtime,
    }
    _atomic_json(results_dir / "sanity_check.json", sanity_report)
    if not sanity_passed:
        raise RuntimeError("Stage 0B sanity gate failed; see sanity_check.json")
    if mode == "sanity":
        return {
            "completed": True,
            "mode": "sanity",
            "passed": True,
            "results_dir": str(results_dir),
            "elapsed_seconds": float(time.monotonic() - started),
            "checks": sanity_checks,
        }

    state_arrays, state_metadata, inference_runtime = extract_post_answer_states(
        config,
        records,
        sources["source_manifest"],
        observed_index,
        limit=None,
    )
    nli_hash_after_full = _sha256(nli_path)
    if nli_hash_after_full != nli_hash_before:
        raise RuntimeError("NLI cache changed during a cache-only Stage 0B run")
    for target_row, metadata in zip(target_rows, state_metadata):
        if target_row["id"] != metadata["id"]:
            raise ValueError("Target and hidden-state metadata row order differs")
        target_row.update(
            {
                key: metadata[key]
                for key in (
                    "prompt_token_count",
                    "answer_start_index",
                    "answer_stop_index_exclusive",
                    "final_answer_token_index",
                    "prompt_ids_sha256",
                    "answer_ids_sha256",
                    "full_ids_sha256",
                )
            }
        )

    _atomic_npz(results_dir / "post_answer_hidden_states.npz", state_arrays)
    _atomic_jsonl(results_dir / "leave_one_out_entropy.jsonl", target_rows)
    _atomic_jsonl(
        results_dir / "used_leave_one_out_nli_judgments.jsonl",
        [used_judgments[key] for key in sorted(used_judgments)],
    )
    metrics, predictions = analyze_answer_states(
        config,
        records,
        target_rows,
        labels,
        entropy,
        state_arrays,
        split,
        sources["source_semantic_rows"],
    )
    _atomic_json(results_dir / "answer_state_probe_metrics.json", metrics)
    _atomic_npz(
        results_dir / "test_predictions.npz",
        {
            **{name: values.astype(np.float64) for name, values in predictions.items()},
            "test_source_indices": np.asarray(split["test"], dtype=np.int64),
            "test_labels": labels[split["test"]].astype(np.int8),
            "test_entropy": entropy[split["test"]].astype(np.float64),
            "test_context_groups": split["groups"][split["test"]].astype(str),
        },
    )
    plot_path = _plot_comparison(config, metrics)

    paired_auc = metrics["paired_test_differences"][
        "combined_minus_sequence_nll_auroc"
    ]
    paired_log_loss = metrics["paired_test_differences"][
        "sequence_nll_minus_combined_log_loss"
    ]
    incremental_supported = bool(
        paired_auc["lower_95"] > 0 or paired_log_loss["lower_95"] > 0
    )
    if incremental_supported:
        conclusion = (
            "After observing one generated answer, its layer-14 representation contains "
            "semantic-uncertainty information not fully captured by the likelihood of that "
            "same answer, under this linear readout and held-out comparison."
        )
    else:
        conclusion = (
            "Under this representation and linear readout, the post-answer hidden state "
            "does not show reliable incremental semantic-uncertainty information beyond "
            "the likelihood of the same answer."
        )

    artifact_paths = {
        "sanity_check": results_dir / "sanity_check.json",
        "hidden_states": results_dir / "post_answer_hidden_states.npz",
        "targets": results_dir / "leave_one_out_entropy.jsonl",
        "used_nli_judgments": results_dir / "used_leave_one_out_nli_judgments.jsonl",
        "metrics": results_dir / "answer_state_probe_metrics.json",
        "test_predictions": results_dir / "test_predictions.npz",
        "plot": plot_path,
    }
    manifest = {
        "experiment": "STAGE 0B — POST-ANSWER HIDDEN-STATE DIAGNOSTIC",
        "completed": True,
        "sanity_gate_passed": True,
        "configuration": config,
        "source_run": config["source"]["run_name"],
        "source_artifact_sha256": sources["hashes"],
        "source_split": split["audit"],
        "observed_answer_index": observed_index,
        "target_construction": (
            "Greedy bidirectional-NLI semantic clustering of the other nine cached answers, "
            "with a new high/low threshold fitted only on the preserved training questions."
        ),
        "representation_construction": {
            "teacher_forced_sequence": "retokenized cached prompt + exact cached answer token_ids",
            "prompt_token_verification": (
                "The source run did not store full prompt token-ID arrays. Stage 0B verifies "
                "exact cached prompt text, pinned-tokenizer reconstruction, cached token count, "
                "and cached final prompt token ID; answer token IDs are compared exactly."
            ),
            "primary": "hidden_states[14] at final cached answer content token",
            "secondary": "mean hidden_states[14] over cached answer-content token span only",
            "exploratory": "hidden_states[23] at final cached answer content token",
            "eos_padding_included": False,
        },
        "information_budget": {
            "primary_hidden_probe": "one observed answer",
            "primary_nll_baseline": "the same one observed answer",
            "combined": "same-answer sequence NLL + scalar cross-fitted hidden-probe score",
            "comparable": True,
            "contextual_old_baselines": "ten answers; explicitly not apples-to-apples",
        },
        "nli_coverage": coverage,
        "runtime": inference_runtime,
        "prohibited_operations": {
            "answer_generation_calls": 0,
            "nli_inference_calls": 0,
            "openai_api_calls": 0,
            "activation_steering": False,
            "confidence_loss_training": False,
        },
        "primary_conclusion": conclusion,
        "incremental_information_supported": incremental_supported,
        "versions": _versions(),
        "elapsed_seconds_total": float(time.monotonic() - started),
        "artifacts": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "sha256": _sha256(path),
            }
            for name, path in artifact_paths.items()
        },
    }
    _atomic_json(results_dir / "manifest.json", manifest)
    return {
        "completed": True,
        "mode": "full",
        "sanity_passed": True,
        "results_dir": str(results_dir),
        "primary_conclusion": conclusion,
        "incremental_information_supported": incremental_supported,
        "same_answer_sequence_nll_test_auroc": metrics["baselines"][
            "same_answer_sequence_nll"
        ]["test"]["auroc"],
        "post_answer_layer_14_test_auroc": metrics["probes"][
            "layer_14_final_answer_token"
        ]["test"]["auroc"],
        "combined_test_auroc": metrics["combined_sequence_nll_plus_scalar_probe"][
            "test"
        ]["auroc"],
        "combined_minus_nll_auroc_95": paired_auc,
        "nll_minus_combined_log_loss_95": paired_log_loss,
        "elapsed_seconds": float(time.monotonic() - started),
    }


def _incremental_conclusion(metrics: dict[str, Any]) -> tuple[bool, str]:
    paired_auc = metrics["paired_test_differences"][
        "combined_minus_sequence_nll_auroc"
    ]
    paired_log_loss = metrics["paired_test_differences"][
        "sequence_nll_minus_combined_log_loss"
    ]
    supported = bool(paired_auc["lower_95"] > 0 or paired_log_loss["lower_95"] > 0)
    if supported:
        conclusion = (
            "This rotation supports incremental semantic-uncertainty information beyond "
            "same-answer sequence NLL under the predeclared linear readout."
        )
    else:
        conclusion = (
            "This rotation does not show reliable incremental semantic-uncertainty "
            "information beyond same-answer sequence NLL under the linear readout."
        )
    return supported, conclusion


def _plot_rotation_summary(config: dict[str, Any], summaries: list[dict[str, Any]]) -> Path:
    ordered = sorted(summaries, key=lambda row: int(row["observed_answer_index"]))
    indices = [int(row["observed_answer_index"]) for row in ordered]
    series = {
        "Same-answer sequence NLL": [row["sequence_nll_auroc"] for row in ordered],
        "Layer-14 final-token probe": [row["layer_14_probe_auroc"] for row in ordered],
        "NLL + scalar probe score": [row["combined_auroc"] for row in ordered],
    }
    figure, axis = plt.subplots(figsize=(7.5, 4.8))
    for name, values in series.items():
        axis.plot(indices, values, marker="o", linewidth=2, label=name)
    axis.axhline(0.5, color="black", linestyle="--", linewidth=1, alpha=0.65)
    axis.set_xticks(indices)
    axis.set_xlabel("Observed cached answer index")
    axis.set_ylabel("Held-out AUROC")
    axis.set_ylim(0.35, 1.0)
    axis.set_title("Stage 0B leave-one-out rotations (question remains the unit)")
    axis.legend(frameon=False)
    figure.tight_layout()
    path = ROOT / "plots" / "run_500_qwen15b_answer_state_rotations.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(path, dpi=180)
    plt.close(figure)
    return path


def run_stage0b_robustness(config_path: str | Path) -> dict[str, Any]:
    """Run predeclared answer-index rotations as separate question-level analyses."""

    started = time.monotonic()
    config = load_stage0b_config(config_path)
    sources = _load_sources(config)
    records = sources["records"]
    split = sources["split"]
    indices = [int(value) for value in config["experiment"]["optional_robustness_indices"]]
    primary_index = int(config["experiment"]["primary_observed_answer_index"])
    if primary_index in indices or len(set(indices)) != len(indices):
        raise ValueError("Robustness indices must be unique and exclude the primary index")
    base_results_dir = _resolve(config["output"]["results_dir"])
    primary_metrics_path = base_results_dir / "answer_state_probe_metrics.json"
    if not primary_metrics_path.exists():
        raise FileNotFoundError("Run the primary index-0 analysis before robustness rotations")
    with primary_metrics_path.open("r", encoding="utf-8") as handle:
        primary_metrics = json.load(handle)

    summaries = [
        {
            "observed_answer_index": primary_index,
            "role": "primary",
            "sequence_nll_auroc": primary_metrics["baselines"][
                "same_answer_sequence_nll"
            ]["test"]["auroc"],
            "layer_14_probe_auroc": primary_metrics["probes"][
                "layer_14_final_answer_token"
            ]["test"]["auroc"],
            "combined_auroc": primary_metrics[
                "combined_sequence_nll_plus_scalar_probe"
            ]["test"]["auroc"],
            "combined_minus_nll_auroc_95": primary_metrics[
                "paired_test_differences"
            ]["combined_minus_sequence_nll_auroc"],
        }
    ]
    nli_path = sources["paths"]["nli_cache"]
    nli_hash_before = _sha256(nli_path)
    rotation_manifests = []
    for observed_index in indices:
        rotation_started = time.monotonic()
        coverage = audit_nli_coverage(
            records,
            observed_index,
            sources["nli_cache"],
            sources["nli_model_id"],
        )
        target_rows, labels, threshold, used_judgments = build_leave_one_out_targets(
            records,
            observed_index,
            sources["nli_cache"],
            sources["nli_model_id"],
            split["train"],
        )
        entropy = np.asarray(
            [row["leave_one_out_semantic_entropy"] for row in target_rows],
            dtype=np.float64,
        )
        state_arrays, state_metadata, runtime = extract_post_answer_states(
            config,
            records,
            sources["source_manifest"],
            observed_index,
            limit=None,
        )
        for target_row, metadata in zip(target_rows, state_metadata):
            if target_row["id"] != metadata["id"]:
                raise ValueError("Rotation target and state row order differs")
            target_row.update(
                {
                    key: metadata[key]
                    for key in (
                        "prompt_token_count",
                        "answer_start_index",
                        "answer_stop_index_exclusive",
                        "final_answer_token_index",
                        "prompt_ids_sha256",
                        "answer_ids_sha256",
                        "full_ids_sha256",
                    )
                }
            )
        metrics, predictions = analyze_answer_states(
            config,
            records,
            target_rows,
            labels,
            entropy,
            state_arrays,
            split,
            sources["source_semantic_rows"],
        )
        rotation_dir = base_results_dir / "robustness" / f"answer_index_{observed_index}"
        _atomic_npz(rotation_dir / "post_answer_hidden_states.npz", state_arrays)
        _atomic_jsonl(rotation_dir / "leave_one_out_entropy.jsonl", target_rows)
        _atomic_jsonl(
            rotation_dir / "used_leave_one_out_nli_judgments.jsonl",
            [used_judgments[key] for key in sorted(used_judgments)],
        )
        _atomic_json(rotation_dir / "answer_state_probe_metrics.json", metrics)
        _atomic_npz(
            rotation_dir / "test_predictions.npz",
            {
                **{name: values.astype(np.float64) for name, values in predictions.items()},
                "test_source_indices": np.asarray(split["test"], dtype=np.int64),
                "test_labels": labels[split["test"]].astype(np.int8),
                "test_entropy": entropy[split["test"]].astype(np.float64),
                "test_context_groups": split["groups"][split["test"]].astype(str),
            },
        )
        rotation_config = copy.deepcopy(config)
        rotation_config["output"]["plot"] = str(
            Path("plots")
            / f"run_500_qwen15b_answer_state_answer_index_{observed_index}.png"
        )
        plot_path = _plot_comparison(rotation_config, metrics)
        supported, conclusion = _incremental_conclusion(metrics)
        manifest = {
            "experiment": "Stage 0B predeclared answer-index robustness rotation",
            "role": "secondary robustness; not a new independent sample",
            "observed_answer_index": observed_index,
            "question_is_statistical_unit": True,
            "pooled_with_other_rotations": False,
            "threshold_fit_on_training_only": threshold,
            "source_split": split["audit"],
            "source_artifact_sha256": sources["hashes"],
            "nli_coverage": coverage,
            "runtime": runtime,
            "incremental_information_supported": supported,
            "conclusion": conclusion,
            "answer_generation_calls": 0,
            "nli_inference_calls": 0,
            "plot": str(plot_path.relative_to(ROOT)),
            "elapsed_seconds": float(time.monotonic() - rotation_started),
        }
        _atomic_json(rotation_dir / "manifest.json", manifest)
        rotation_manifests.append(manifest)
        summaries.append(
            {
                "observed_answer_index": observed_index,
                "role": "predeclared_secondary_robustness",
                "sequence_nll_auroc": metrics["baselines"][
                    "same_answer_sequence_nll"
                ]["test"]["auroc"],
                "layer_14_probe_auroc": metrics["probes"][
                    "layer_14_final_answer_token"
                ]["test"]["auroc"],
                "combined_auroc": metrics[
                    "combined_sequence_nll_plus_scalar_probe"
                ]["test"]["auroc"],
                "combined_minus_nll_auroc_95": metrics[
                    "paired_test_differences"
                ]["combined_minus_sequence_nll_auroc"],
                "incremental_information_supported": supported,
            }
        )
    if _sha256(nli_path) != nli_hash_before:
        raise RuntimeError("NLI cache changed during robustness rotations")
    summary_plot = _plot_rotation_summary(config, summaries)
    summary = {
        "experiment": "Stage 0B predeclared answer-index robustness",
        "primary_index": primary_index,
        "secondary_indices": indices,
        "question_is_statistical_unit": True,
        "rotations_pooled_as_independent_rows": False,
        "results": summaries,
        "summary_plot": str(summary_plot.relative_to(ROOT)),
        "answer_generation_calls": 0,
        "nli_inference_calls": 0,
        "elapsed_seconds": float(time.monotonic() - started),
    }
    _atomic_json(base_results_dir / "robustness_summary.json", summary)
    return {
        "completed": True,
        "mode": "robustness",
        "results": summaries,
        "elapsed_seconds": summary["elapsed_seconds"],
    }
