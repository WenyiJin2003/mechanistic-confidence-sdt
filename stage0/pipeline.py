"""Cached local generation, semantic grouping, and linear-probe analysis."""

from __future__ import annotations

import gc
import copy
import hashlib
import json
import logging
import math
import os
import platform
import re
import string
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any

import datasets
import matplotlib
import numpy as np
import sklearn
import torch
import transformers
import yaml
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, log_loss, roc_auc_score
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from tqdm.auto import tqdm
from transformers import AutoModelForCausalLM, AutoModelForSequenceClassification, AutoTokenizer


matplotlib.use("Agg")
from matplotlib import pyplot as plt  # noqa: E402


LOGGER = logging.getLogger(__name__)


def root_dir() -> Path:
    return Path(__file__).resolve().parents[1]


def load_config(path: str | Path) -> tuple[dict[str, Any], Path]:
    config_path = Path(path).expanduser().resolve()
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    root = root_dir()
    for key in ("cache_dir", "results_dir", "hf_cache_dir"):
        value = Path(config["project"][key]).expanduser()
        if not value.is_absolute():
            value = root / value
        config["project"][key] = str(value.resolve())
    return config, config_path


def stable_hash(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def atomic_json(path: str | Path, value: Any) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(target.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    os.replace(temporary, target)


def write_jsonl(path: str | Path, rows: list[dict[str, Any]]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(target.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    os.replace(temporary, target)


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def choose_device(preference: list[str]) -> torch.device:
    for requested in preference:
        if requested == "mps" and torch.backends.mps.is_available():
            return torch.device("mps")
        if requested == "cuda" and torch.cuda.is_available():
            return torch.device("cuda")
        if requested == "cpu":
            return torch.device("cpu")
    return torch.device("cpu")


def choose_dtype(name: str, device: torch.device) -> torch.dtype:
    if device.type == "cpu":
        return torch.float32
    return {"float16": torch.float16, "bfloat16": torch.bfloat16, "float32": torch.float32}[name]


def clear_device_cache() -> None:
    gc.collect()
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


def normalize_answer(text: str) -> str:
    text = text.lower()
    text = "".join(character for character in text if character not in string.punctuation)
    text = re.sub(r"\b(a|an|the)\b", " ", text)
    return " ".join(text.split())


def squad_exact_match(prediction: str, references: list[str]) -> float:
    normalized_prediction = normalize_answer(prediction)
    return float(any(normalized_prediction == normalize_answer(reference) for reference in references))


def squad_f1(prediction: str, references: list[str]) -> float:
    prediction_tokens = normalize_answer(prediction).split()
    best = 0.0
    for reference in references:
        reference_tokens = normalize_answer(reference).split()
        if not prediction_tokens and not reference_tokens:
            best = max(best, 1.0)
            continue
        if not prediction_tokens or not reference_tokens:
            continue
        common = Counter(prediction_tokens) & Counter(reference_tokens)
        overlap = sum(common.values())
        if overlap == 0:
            continue
        precision = overlap / len(prediction_tokens)
        recall = overlap / len(reference_tokens)
        best = max(best, 2 * precision * recall / (precision + recall))
    return float(best)


def runtime_versions() -> dict[str, Any]:
    return {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "torch": torch.__version__,
        "transformers": transformers.__version__,
        "datasets": datasets.__version__,
        "scikit_learn": sklearn.__version__,
        "numpy": np.__version__,
        "mps_built": torch.backends.mps.is_built(),
        "mps_available": torch.backends.mps.is_available(),
        "cuda_available": torch.cuda.is_available(),
    }


def portable_config(config: dict[str, Any]) -> dict[str, Any]:
    """Remove machine-specific absolute paths from saved, shareable manifests."""
    output = copy.deepcopy(config)
    root = root_dir()
    for key in ("cache_dir", "results_dir", "hf_cache_dir"):
        value = Path(output["project"][key]).resolve()
        try:
            output["project"][key] = str(value.relative_to(root))
        except ValueError:
            output["project"][key] = value.name
    return output


def _normalized_text(value: str) -> str:
    return " ".join(value.lower().split())


def _question_jaccard(left: str, right: str) -> float:
    left_tokens = set(normalize_answer(left).split())
    right_tokens = set(normalize_answer(right).split())
    union = left_tokens | right_tokens
    return len(left_tokens & right_tokens) / len(union) if union else 1.0


def _excluded_dataset_records(config: dict[str, Any]) -> list[dict[str, Any]]:
    records = []
    for run_name in config["dataset"].get("exclude_result_runs", []):
        path = Path(config["project"]["results_dir"]) / run_name / "generations.jsonl"
        if not path.exists():
            raise FileNotFoundError(f"Dataset exclusion source does not exist: {path}")
        records.extend(read_jsonl(path))
    return records


def fixed_dataset(config: dict[str, Any], count: int) -> list[dict[str, Any]]:
    dataset_config = config["dataset"]
    excluded_records = _excluded_dataset_records(config)
    exclusion_identity = {
        "ids": sorted(record["id"] for record in excluded_records),
        "contexts": sorted({_normalized_text(record["context"]) for record in excluded_records}),
        "questions": sorted({_normalized_text(record["question"]) for record in excluded_records}),
        "near_duplicate_threshold": dataset_config.get("exclude_near_duplicate_questions_at_jaccard"),
    }
    cache_identity = {
        "id": dataset_config["id"],
        "split": dataset_config["split"],
        "answerable_only": dataset_config.get("answerable_only", True),
        "selection_seed": int(dataset_config["selection_seed"]),
        "revision": dataset_config.get("revision"),
        "exclusions": stable_hash(exclusion_identity),
    }
    cache_path = (
        Path(config["project"]["cache_dir"])
        / "dataset"
        / f"fixed_subset_{stable_hash(cache_identity)[:16]}.jsonl"
    )
    maximum = max(int(run["num_examples"]) for run in config["runs"].values())
    if cache_path.exists():
        cached = read_jsonl(cache_path)
        if len(cached) >= count:
            return cached[:count]
    dataset = datasets.load_dataset(
        dataset_config["id"],
        split=dataset_config["split"],
        cache_dir=config["project"]["hf_cache_dir"],
        revision=dataset_config.get("revision"),
    )
    excluded_ids = {record["id"] for record in excluded_records}
    excluded_contexts = {_normalized_text(record["context"]) for record in excluded_records}
    excluded_questions = {_normalized_text(record["question"]) for record in excluded_records}
    excluded_question_texts = [record["question"] for record in excluded_records]
    near_duplicate_threshold = dataset_config.get("exclude_near_duplicate_questions_at_jaccard")
    candidates = []
    for row in dataset:
        answers = list(row["answers"]["text"])
        if dataset_config.get("answerable_only", True) and not answers:
            continue
        row_id = str(row["id"])
        question = row["question"]
        context = row.get("context", "")
        if (
            row_id in excluded_ids
            or _normalized_text(context) in excluded_contexts
            or _normalized_text(question) in excluded_questions
        ):
            continue
        if near_duplicate_threshold is not None and any(
            _question_jaccard(question, excluded) >= float(near_duplicate_threshold)
            for excluded in excluded_question_texts
        ):
            continue
        candidates.append(
            {
                "id": row_id,
                "question": question,
                "context": context,
                "answers": answers,
            }
        )
    rng = np.random.default_rng(int(dataset_config["selection_seed"]))
    selected = [candidates[int(index)] for index in rng.permutation(len(candidates))[:maximum]]
    write_jsonl(cache_path, selected)
    return selected[:count]


class LocalGenerator:
    def __init__(self, config: dict[str, Any]):
        model_config = config["models"]["generator"]
        self.model_id = model_config["id"]
        self.device = choose_device(config["device"]["preference"])
        self.dtype = choose_dtype(config["device"]["generator_dtype"], self.device)
        self.max_prompt_tokens = int(model_config["max_prompt_tokens"])
        self.layers = [int(layer) for layer in config["generation"]["layers"]]
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_id,
            cache_dir=config["project"]["hf_cache_dir"],
            trust_remote_code=model_config.get("trust_remote_code", False),
        )
        self.tokenizer.truncation_side = model_config.get("truncation_side", "left")
        if self.tokenizer.pad_token_id is None:
            self.tokenizer.pad_token_id = self.tokenizer.eos_token_id
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_id,
            cache_dir=config["project"]["hf_cache_dir"],
            trust_remote_code=model_config.get("trust_remote_code", False),
            dtype=self.dtype,
            attn_implementation=model_config.get("attn_implementation", "eager"),
            low_cpu_mem_usage=True,
        ).to(self.device)
        self.model.eval()
        layer_count = int(self.model.config.num_hidden_layers)
        if min(self.layers) < 1 or max(self.layers) > layer_count:
            raise ValueError(f"Requested layers {self.layers}; model has {layer_count} transformer blocks")
        self.runtime = {
            "model_id": self.model_id,
            "device": str(self.device),
            "dtype": str(self.dtype).replace("torch.", ""),
            "hidden_size": int(self.model.config.hidden_size),
            "num_hidden_layers": layer_count,
        }

    def prompt(self, example: dict[str, Any], dataset_config: dict[str, Any]) -> str:
        content = ""
        if dataset_config.get("include_context", True):
            content += f"Context: {example['context']}\n\n"
        content += f"Question: {example['question']}"
        messages = [
            {"role": "system", "content": dataset_config["system_prompt"]},
            {"role": "user", "content": content},
        ]
        return self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

    @staticmethod
    def seed(seed: int) -> None:
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
        if torch.backends.mps.is_available():
            torch.mps.manual_seed(seed)

    def run_example(
        self,
        example: dict[str, Any],
        dataset_config: dict[str, Any],
        generation_config: dict[str, Any],
        run_config: dict[str, Any],
        seed: int,
        cached_hidden: np.ndarray | None = None,
    ) -> tuple[dict[str, Any], np.ndarray]:
        rendered = self.prompt(example, dataset_config)
        full_token_ids = self.tokenizer(rendered, truncation=False)["input_ids"]
        full_prompt_token_count = len(full_token_ids)
        inputs = self.tokenizer(
            rendered,
            return_tensors="pt",
            truncation=True,
            max_length=self.max_prompt_tokens,
        ).to(self.device)
        prompt_length = int(inputs["input_ids"].shape[1])
        final_token_id = int(inputs["input_ids"][0, -1].item())
        prompt_was_truncated = full_prompt_token_count > prompt_length
        prompt_suffix_preserved = final_token_id == int(full_token_ids[-1])
        if cached_hidden is None:
            with torch.inference_mode():
                forward = self.model(**inputs, output_hidden_states=True, use_cache=False, return_dict=True)
            hidden = torch.stack(
                [forward.hidden_states[layer][0, -1, :].detach().to("cpu", dtype=torch.float16) for layer in self.layers]
            ).numpy()
            del forward
        else:
            hidden = cached_hidden

        self.seed(seed)
        with torch.inference_mode():
            output = self.model.generate(
                **inputs,
                do_sample=bool(generation_config["do_sample"]),
                temperature=float(generation_config["temperature"]),
                top_p=float(generation_config["top_p"]),
                top_k=int(generation_config["top_k"]),
                max_new_tokens=int(generation_config["max_new_tokens"]),
                num_return_sequences=int(run_config["num_generations"]),
                return_dict_in_generate=True,
                output_scores=True,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
            )
        scores = self.model.compute_transition_scores(
            output.sequences, output.scores, normalize_logits=True
        ).detach().float().cpu()
        sequences = output.sequences.detach().cpu()
        stop_ids = {value for value in (self.tokenizer.eos_token_id, self.tokenizer.pad_token_id) if value is not None}
        generations = []
        for row in range(sequences.shape[0]):
            token_ids = []
            token_logprobs = []
            for position, token_id in enumerate(sequences[row, prompt_length:].tolist()):
                if token_id in stop_ids:
                    break
                token_ids.append(int(token_id))
                if position < scores.shape[1]:
                    token_logprobs.append(float(scores[row, position].item()))
            text = self.tokenizer.decode(token_ids, skip_special_tokens=True).strip()
            generations.append(
                {
                    "text": text,
                    "normalized_text": normalize_answer(text),
                    "exact_match": squad_exact_match(text, example["answers"]),
                    "f1": squad_f1(text, example["answers"]),
                    "token_ids": token_ids,
                    "token_logprobs": token_logprobs,
                    "sequence_logprob": float(np.sum(token_logprobs)) if token_logprobs else -1e9,
                    "mean_token_logprob": float(np.mean(token_logprobs)) if token_logprobs else -1e9,
                    "token_count": len(token_ids),
                }
            )
        del output, scores, sequences, inputs
        record = {
            "id": example["id"],
            "question": example["question"],
            "context": example["context"],
            "reference_answers": example["answers"],
            "prompt": rendered,
            "prompt_token_count": prompt_length,
            "full_prompt_token_count": full_prompt_token_count,
            "prompt_was_truncated": prompt_was_truncated,
            "prompt_suffix_preserved": prompt_suffix_preserved,
            "final_prompt_token_index": prompt_length - 1,
            "final_prompt_token_id": final_token_id,
            "final_prompt_token_text": self.tokenizer.decode([final_token_id]),
            "layers": self.layers,
            "generations": generations,
        }
        return record, hidden

    def hidden_only(
        self,
        example: dict[str, Any],
        dataset_config: dict[str, Any],
    ) -> tuple[np.ndarray, dict[str, Any]]:
        rendered = self.prompt(example, dataset_config)
        full_token_ids = self.tokenizer(rendered, truncation=False)["input_ids"]
        full_prompt_token_count = len(full_token_ids)
        inputs = self.tokenizer(
            rendered,
            return_tensors="pt",
            truncation=True,
            max_length=self.max_prompt_tokens,
        ).to(self.device)
        prompt_length = int(inputs["input_ids"].shape[1])
        final_token_id = int(inputs["input_ids"][0, -1].item())
        with torch.inference_mode():
            forward = self.model(**inputs, output_hidden_states=True, use_cache=False, return_dict=True)
        hidden = torch.stack(
            [forward.hidden_states[layer][0, -1, :].detach().to("cpu", dtype=torch.float16) for layer in self.layers]
        ).numpy()
        del forward, inputs
        metadata = {
            "prompt": rendered,
            "prompt_token_count": prompt_length,
            "full_prompt_token_count": full_prompt_token_count,
            "prompt_was_truncated": full_prompt_token_count > prompt_length,
            "prompt_suffix_preserved": final_token_id == int(full_token_ids[-1]),
            "final_prompt_token_index": prompt_length - 1,
            "final_prompt_token_id": final_token_id,
            "final_prompt_token_text": self.tokenizer.decode([final_token_id]),
            "layers": self.layers,
        }
        return hidden, metadata

    def close(self) -> None:
        del self.model, self.tokenizer
        clear_device_cache()


def _generation_key(config: dict[str, Any], example: dict[str, Any], run_config: dict[str, Any], index: int) -> str:
    generation_config = {key: value for key, value in config["generation"].items() if key != "layers"}
    payload = {
        "model": config["models"]["generator"],
        "dataset_prompt": config["dataset"],
        "generation": generation_config,
        "num_generations": run_config["num_generations"],
        "example": example,
        "seed": int(config["project"]["seed"]) + index,
    }
    return stable_hash(payload)


def _legacy_generation_key(
    config: dict[str, Any],
    example: dict[str, Any],
    run_config: dict[str, Any],
    index: int,
) -> str:
    payload = {
        "model": config["models"]["generator"],
        "dataset_prompt": config["dataset"],
        "generation": config["generation"],
        "num_generations": run_config["num_generations"],
        "example": example,
        "seed": int(config["project"]["seed"]) + index,
    }
    return stable_hash(payload)


def _hidden_key(config: dict[str, Any], example: dict[str, Any]) -> str:
    return stable_hash(
        {
            "model": config["models"]["generator"],
            "dataset_prompt": config["dataset"],
            "layers": config["generation"]["layers"],
            "example": example,
            "token_position": "final_prompt_token_before_generation",
        }
    )


def generate(config: dict[str, Any], run_name: str, examples: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], np.ndarray, dict[str, Any]]:
    run_config = config["runs"][run_name]
    shared_dir = Path(config["project"]["cache_dir"]) / "generations"
    shared_dir.mkdir(parents=True, exist_ok=True)
    generator = LocalGenerator(config)
    records = []
    hidden_rows = []
    started = time.monotonic()
    generation_cache_hits = 0
    legacy_generation_cache_hits = 0
    hidden_cache_hits = 0
    try:
        for index, example in enumerate(tqdm(examples, desc=f"{run_name}: Qwen")):
            key = _generation_key(config, example, run_config, index)
            hidden_key = _hidden_key(config, example)
            json_path = shared_dir / f"{key}.json"
            hidden_path = shared_dir / f"hidden-{hidden_key}.npz"
            if not json_path.exists():
                compatibility = config.get("cache_compatibility", {})
                for layer_set in compatibility.get("legacy_generation_layer_sets", []):
                    legacy_config = copy.deepcopy(config)
                    legacy_config["generation"]["layers"] = [int(layer) for layer in layer_set]
                    legacy_key = _legacy_generation_key(legacy_config, example, run_config, index)
                    legacy_path = shared_dir / f"{legacy_key}.json"
                    if not legacy_path.exists():
                        continue
                    with legacy_path.open("r", encoding="utf-8") as handle:
                        legacy_record = json.load(handle)
                    if int(legacy_record.get("prompt_token_count", generator.max_prompt_tokens)) >= generator.max_prompt_tokens:
                        continue
                    legacy_record["cache_key"] = key
                    legacy_record["reused_from_legacy_cache"] = legacy_key
                    atomic_json(json_path, legacy_record)
                    legacy_generation_cache_hits += 1
                    break

            record = None
            hidden = None
            if json_path.exists():
                with json_path.open("r", encoding="utf-8") as handle:
                    record = json.load(handle)
                generation_cache_hits += 1
            if hidden_path.exists():
                hidden = np.load(hidden_path)["hidden"]
                hidden_cache_hits += 1

            if record is None:
                record, generated_hidden = generator.run_example(
                    example,
                    config["dataset"],
                    config["generation"],
                    run_config,
                    int(config["project"]["seed"]) + index,
                    cached_hidden=hidden,
                )
                if hidden is None:
                    hidden = generated_hidden
            elif hidden is None:
                hidden, prompt_metadata = generator.hidden_only(example, config["dataset"])
                record.update(prompt_metadata)

            for generation in record["generations"]:
                generation["exact_match"] = squad_exact_match(generation["text"], example["answers"])
                generation["f1"] = squad_f1(generation["text"], example["answers"])
            record["layers"] = [int(layer) for layer in config["generation"]["layers"]]
            record.setdefault("full_prompt_token_count", record["prompt_token_count"])
            record.setdefault("prompt_was_truncated", False)
            record.setdefault("prompt_suffix_preserved", True)
            record["cache_key"] = key
            atomic_json(json_path, record)
            if not hidden_path.exists():
                np.savez_compressed(
                    hidden_path,
                    hidden=hidden,
                    layers=np.asarray(record["layers"], dtype=np.int16),
                )
            records.append(record)
            hidden_rows.append(hidden)
            elapsed_minutes = (time.monotonic() - started) / 60.0
            if elapsed_minutes > float(config["project"]["time_limit_minutes"]):
                raise TimeoutError(
                    f"Generation exceeded {config['project']['time_limit_minutes']} minutes; cached {len(records)} examples"
                )
    finally:
        runtime = {
            **generator.runtime,
            "generation_cache_hits": generation_cache_hits,
            "legacy_generation_cache_hits": legacy_generation_cache_hits,
            "hidden_cache_hits": hidden_cache_hits,
            "elapsed_seconds": time.monotonic() - started,
        }
        generator.close()
    return records, np.stack(hidden_rows), runtime


def cluster_entropy(cluster_ids: list[int]) -> float:
    counts = np.bincount(np.asarray(cluster_ids, dtype=np.int64))
    probabilities = counts[counts > 0] / len(cluster_ids)
    return float(-(probabilities * np.log(probabilities)).sum())


class LocalNLI:
    def __init__(self, config: dict[str, Any]):
        model_config = config["models"]["entailment"]
        self.model_id = model_config["id"]
        self.label_order = list(model_config["label_order"])
        self.batch_size = int(model_config["batch_size"])
        self.max_length = int(model_config["max_length"])
        self.allow_cpu_fallback = bool(config["device"]["allow_cpu_fallback"])
        self.device = choose_device(config["device"]["preference"])
        self.dtype = choose_dtype(config["device"]["entailment_dtype"], self.device)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id, cache_dir=config["project"]["hf_cache_dir"])
        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.model_id, cache_dir=config["project"]["hf_cache_dir"], dtype=self.dtype
        ).to(self.device)
        self.model.eval()

    def _batch(self, pairs: list[tuple[str, str]]) -> list[dict[str, Any]]:
        encoded = self.tokenizer(
            [pair[0] for pair in pairs],
            [pair[1] for pair in pairs],
            padding=True,
            truncation=True,
            max_length=self.max_length,
            return_tensors="pt",
        ).to(self.device)
        with torch.inference_mode():
            probabilities = torch.softmax(self.model(**encoded).logits.float(), dim=-1).cpu().numpy()
        return [
            {
                "label": self.label_order[int(np.argmax(row))],
                "probabilities": {label: float(row[index]) for index, label in enumerate(self.label_order)},
            }
            for row in probabilities
        ]

    def predict(self, pairs: list[tuple[str, str]]) -> list[dict[str, Any]]:
        try:
            return [item for start in range(0, len(pairs), self.batch_size) for item in self._batch(pairs[start:start + self.batch_size])]
        except (RuntimeError, NotImplementedError) as error:
            if self.device.type != "mps" or not self.allow_cpu_fallback:
                raise
            LOGGER.warning("NLI MPS operation failed (%s); retrying the NLI stage on CPU", error)
            self.device = torch.device("cpu")
            self.dtype = torch.float32
            self.model = self.model.to(device=self.device, dtype=self.dtype)
            clear_device_cache()
            return [item for start in range(0, len(pairs), self.batch_size) for item in self._batch(pairs[start:start + self.batch_size])]

    def close(self) -> None:
        del self.model, self.tokenizer
        clear_device_cache()


def semantic_rows_exact(records: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    rows = []
    for record in records:
        mapping: dict[str, int] = {}
        cluster_ids = []
        for generation in record["generations"]:
            normalized = generation["normalized_text"]
            if normalized not in mapping:
                mapping[normalized] = len(mapping)
            cluster_ids.append(mapping[normalized])
        rows.append(_semantic_row(record, cluster_ids))
    return rows, [], {"method": "normalized_exact_match", "model_id": None, "device": None}


def semantic_rows_nli(config: dict[str, Any], records: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    cache_path = Path(config["project"]["cache_dir"]) / "entailment" / "nli_cache.json"
    if cache_path.exists():
        with cache_path.open("r", encoding="utf-8") as handle:
            cache = json.load(handle)
    else:
        cache = {}
    model_id = config["models"]["entailment"]["id"]
    needed: dict[str, tuple[str, str]] = {}
    texts_by_record = []
    for record in records:
        texts = [f"{record['question']} {generation['text']}" for generation in record["generations"]]
        texts_by_record.append(texts)
        for i, premise in enumerate(texts):
            for j, hypothesis in enumerate(texts):
                if i == j or normalize_answer(record["generations"][i]["text"]) == normalize_answer(record["generations"][j]["text"]):
                    continue
                key = stable_hash({"model": model_id, "premise": premise, "hypothesis": hypothesis})
                if key not in cache:
                    needed[key] = (premise, hypothesis)
    runtime = {"method": "bidirectional_strict_entailment", "model_id": model_id, "device": "cached"}
    if needed:
        nli = LocalNLI(config)
        keys = list(needed)
        checkpoint_size = max(nli.batch_size * 4, nli.batch_size)
        runtime["new_judgments"] = len(keys)
        for start in range(0, len(keys), checkpoint_size):
            batch_keys = keys[start:start + checkpoint_size]
            predictions = nli.predict([needed[key] for key in batch_keys])
            for key, prediction in zip(batch_keys, predictions):
                premise, hypothesis = needed[key]
                cache[key] = {
                    "premise": premise,
                    "hypothesis": hypothesis,
                    **prediction,
                }
            atomic_json(cache_path, cache)
        runtime["device"] = str(nli.device)
        runtime["dtype"] = str(nli.dtype).replace("torch.", "")
        nli.close()

    used = {}
    rows = []
    for record, texts in zip(records, texts_by_record):
        answers = [generation["text"] for generation in record["generations"]]

        def entails(i: int, j: int) -> bool:
            if normalize_answer(answers[i]) == normalize_answer(answers[j]):
                return True
            key = stable_hash({"model": model_id, "premise": texts[i], "hypothesis": texts[j]})
            used[key] = {"record_id": record["id"], "from": i, "to": j, **cache[key]}
            return cache[key]["label"] == "entailment"

        cluster_ids = [-1] * len(texts)
        next_id = 0
        for i in range(len(texts)):
            if cluster_ids[i] != -1:
                continue
            cluster_ids[i] = next_id
            for j in range(i + 1, len(texts)):
                if entails(i, j) and entails(j, i):
                    cluster_ids[j] = next_id
            next_id += 1
        rows.append(_semantic_row(record, cluster_ids))
    return rows, list(used.values()), runtime


def _semantic_row(record: dict[str, Any], cluster_ids: list[int]) -> dict[str, Any]:
    mean_logprobs = [generation["mean_token_logprob"] for generation in record["generations"]]
    sequence_logprobs = [generation["sequence_logprob"] for generation in record["generations"]]
    lengths = [generation["token_count"] for generation in record["generations"]]
    exact_matches = [generation["exact_match"] for generation in record["generations"]]
    f1_scores = [generation["f1"] for generation in record["generations"]]
    return {
        "id": record["id"],
        "semantic_ids": cluster_ids,
        "num_semantic_clusters": len(set(cluster_ids)),
        "cluster_assignment_entropy": cluster_entropy(cluster_ids),
        "predictive_entropy": float(-np.mean(mean_logprobs)),
        "answer_negative_log_likelihood": float(-np.mean(sequence_logprobs)),
        "mean_answer_length": float(np.mean(lengths)),
        "prompt_length": int(record["prompt_token_count"]),
        "sample_mean_exact_match": float(np.mean(exact_matches)),
        "sample_mean_f1": float(np.mean(f1_scores)),
        "any_sample_exact_match": bool(np.max(exact_matches) > 0),
        "all_samples_exact_match": bool(np.min(exact_matches) > 0),
    }


def best_train_threshold(values: np.ndarray) -> float:
    unique = np.unique(values)
    if unique.size < 2:
        raise ValueError("Training semantic entropy is degenerate")
    candidates = (unique[:-1] + unique[1:]) / 2.0
    scores = []
    for threshold in candidates:
        low, high = values[values < threshold], values[values >= threshold]
        scores.append(float(((low - low.mean()) ** 2).sum() + ((high - high.mean()) ** 2).sum()))
    return float(candidates[int(np.argmin(scores))])


def safe_metrics(labels: np.ndarray, probabilities: np.ndarray) -> dict[str, Any]:
    probabilities = np.clip(np.asarray(probabilities, dtype=np.float64), 1e-7, 1 - 1e-7)
    predictions = (probabilities >= 0.5).astype(np.int64)
    return {
        "accuracy": float(accuracy_score(labels, predictions)),
        "auroc": float(roc_auc_score(labels, probabilities)) if np.unique(labels).size == 2 else None,
        "log_loss": float(log_loss(labels, np.column_stack([1 - probabilities, probabilities]), labels=[0, 1])),
    }


def bootstrap_auroc(
    labels: np.ndarray,
    probabilities: np.ndarray,
    samples: int,
    seed: int,
    groups: np.ndarray | None = None,
) -> dict[str, Any] | None:
    if np.unique(labels).size < 2:
        return None
    rng = np.random.default_rng(seed)
    values = []
    unique_groups = np.unique(groups) if groups is not None else None
    for _ in range(samples):
        if unique_groups is None:
            sample = rng.integers(0, len(labels), size=len(labels))
        else:
            sampled_groups = rng.choice(unique_groups, size=len(unique_groups), replace=True)
            sample = np.concatenate(
                [np.flatnonzero(groups == group) for group in sampled_groups]
            )
        if np.unique(labels[sample]).size < 2:
            continue
        values.append(float(roc_auc_score(labels[sample], probabilities[sample])))
    if not values:
        return None
    return {
        "lower_95": float(np.percentile(values, 2.5)),
        "median": float(np.median(values)),
        "upper_95": float(np.percentile(values, 97.5)),
        "valid_resamples": len(values),
    }


def bootstrap_auroc_difference(
    labels: np.ndarray,
    first_probabilities: np.ndarray,
    second_probabilities: np.ndarray,
    samples: int,
    seed: int,
    groups: np.ndarray | None = None,
) -> dict[str, Any] | None:
    if np.unique(labels).size < 2:
        return None
    rng = np.random.default_rng(seed)
    unique_groups = np.unique(groups) if groups is not None else None
    differences = []
    for _ in range(samples):
        if unique_groups is None:
            indices = rng.integers(0, len(labels), size=len(labels))
        else:
            sampled_groups = rng.choice(unique_groups, size=len(unique_groups), replace=True)
            indices = np.concatenate(
                [np.flatnonzero(groups == group) for group in sampled_groups]
            )
        if np.unique(labels[indices]).size < 2:
            continue
        differences.append(
            float(
                roc_auc_score(labels[indices], first_probabilities[indices])
                - roc_auc_score(labels[indices], second_probabilities[indices])
            )
        )
    if not differences:
        return None
    values = np.asarray(differences, dtype=np.float64)
    return {
        "estimate": float(
            roc_auc_score(labels, first_probabilities)
            - roc_auc_score(labels, second_probabilities)
        ),
        "lower_95": float(np.percentile(values, 2.5)),
        "median": float(np.median(values)),
        "upper_95": float(np.percentile(values, 97.5)),
        "valid_resamples": int(values.size),
    }


def fixed_group_split(
    records: list[dict[str, Any]],
    probe_config: dict[str, Any],
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    indices = np.arange(len(records))
    groups = np.asarray(
        [stable_hash(" ".join(record["context"].lower().split())) for record in records]
    )
    validation_fraction = float(probe_config.get("validation_fraction", 0.0))
    test_fraction = float(probe_config["test_fraction"])
    holdout_fraction = validation_fraction + test_fraction
    if not 0 < holdout_fraction < 1:
        raise ValueError("validation_fraction + test_fraction must be between zero and one")
    outer = GroupShuffleSplit(
        n_splits=1,
        test_size=holdout_fraction,
        random_state=int(probe_config["split_seed"]),
    )
    train_indices, holdout_indices = next(outer.split(indices, groups=groups))
    if validation_fraction == 0:
        return train_indices, np.asarray([], dtype=np.int64), holdout_indices
    relative_test_fraction = test_fraction / holdout_fraction
    inner = GroupShuffleSplit(
        n_splits=1,
        test_size=relative_test_fraction,
        random_state=int(probe_config["split_seed"]) + 1,
    )
    validation_local, test_local = next(
        inner.split(holdout_indices, groups=groups[holdout_indices])
    )
    return (
        train_indices,
        holdout_indices[validation_local],
        holdout_indices[test_local],
    )


def probe_model(config: dict[str, Any], random_state: int) -> Any:
    return make_pipeline(
        StandardScaler(),
        LogisticRegression(
            C=float(config["probe"]["c"]),
            max_iter=int(config["probe"]["max_iter"]),
            random_state=random_state,
        ),
    )


def class_counts(labels: np.ndarray, indices: np.ndarray) -> dict[str, int]:
    return {
        str(key): int(value)
        for key, value in Counter(labels[indices].tolist()).items()
    }


def train_probe(
    config: dict[str, Any],
    hidden: np.ndarray,
    semantic_rows: list[dict[str, Any]],
    records: list[dict[str, Any]],
) -> dict[str, Any]:
    probe_config = config["probe"]
    entropy = np.asarray(
        [row["cluster_assignment_entropy"] for row in semantic_rows],
        dtype=np.float64,
    )
    train_indices, validation_indices, test_indices = fixed_group_split(records, probe_config)
    threshold = best_train_threshold(entropy[train_indices])
    labels = (entropy >= threshold).astype(np.int64)
    for split_name, split_indices in (
        ("training", train_indices),
        ("validation", validation_indices),
        ("test", test_indices),
    ):
        if len(split_indices) and np.unique(labels[split_indices]).size < 2:
            raise ValueError(f"Probe {split_name} split has one class")

    layers = [int(value) for value in config["generation"]["layers"]]
    nll = np.asarray(
        [row["answer_negative_log_likelihood"] for row in semantic_rows],
        dtype=np.float32,
    ).reshape(-1, 1)
    correctness = np.asarray(
        [row["any_sample_exact_match"] for row in semantic_rows],
        dtype=np.int64,
    )
    bootstrap_samples = int(probe_config.get("bootstrap_samples", 1000))
    bootstrap_seed = int(probe_config.get("bootstrap_seed", 271828))
    test_groups = np.asarray(
        [
            stable_hash(" ".join(records[index]["context"].lower().split()))
            for index in test_indices
        ]
    )
    layer_results = []
    combined_results = []
    layer_test_probabilities: dict[int, np.ndarray] = {}
    combined_test_probabilities_by_layer: dict[int, np.ndarray] = {}
    baseline_test_probabilities: dict[str, np.ndarray] = {}

    for position, layer in enumerate(layers):
        features = hidden[:, position, :].astype(np.float32)
        model = probe_model(config, int(probe_config["split_seed"]))
        model.fit(features[train_indices], labels[train_indices])
        validation_probabilities = (
            model.predict_proba(features[validation_indices])[:, 1]
            if len(validation_indices)
            else np.asarray([], dtype=np.float64)
        )
        test_probabilities = model.predict_proba(features[test_indices])[:, 1]
        layer_test_probabilities[layer] = test_probabilities
        test_metrics = safe_metrics(labels[test_indices], test_probabilities)
        test_metrics["auroc_bootstrap_95"] = bootstrap_auroc(
            labels[test_indices],
            test_probabilities,
            bootstrap_samples,
            bootstrap_seed + layer,
            test_groups,
        )
        test_metrics["correctness_auroc_from_low_entropy_score"] = (
            float(roc_auc_score(correctness[test_indices], 1 - test_probabilities))
            if np.unique(correctness[test_indices]).size == 2
            else None
        )
        layer_results.append(
            {
                "layer": layer,
                "validation": (
                    safe_metrics(labels[validation_indices], validation_probabilities)
                    if len(validation_indices)
                    else None
                ),
                "test": test_metrics,
            }
        )

        combined_features = np.column_stack([features, nll])
        combined = probe_model(config, int(probe_config["split_seed"]))
        combined.fit(combined_features[train_indices], labels[train_indices])
        combined_probabilities = combined.predict_proba(
            combined_features[test_indices]
        )[:, 1]
        combined_test_probabilities_by_layer[layer] = combined_probabilities
        combined_results.append(
            {
                "layer": layer,
                "validation": (
                    safe_metrics(
                        labels[validation_indices],
                        combined.predict_proba(combined_features[validation_indices])[:, 1],
                    )
                    if len(validation_indices)
                    else None
                ),
                "test": safe_metrics(labels[test_indices], combined_probabilities),
            }
        )

    selection_split = "validation" if len(validation_indices) else "test"
    selected = max(
        layer_results,
        key=lambda row: (
            row[selection_split]["auroc"]
            if row[selection_split]["auroc"] is not None
            else -1.0
        ),
    )
    selected_layer = int(selected["layer"])

    train_mean = float(labels[train_indices].mean())
    constant_validation = np.full(len(validation_indices), train_mean)
    constant_test = np.full(len(test_indices), train_mean)
    baselines: dict[str, Any] = {
        "constant_train_mean": {
            "validation": (
                safe_metrics(labels[validation_indices], constant_validation)
                if len(validation_indices)
                else None
            ),
            "test": safe_metrics(labels[test_indices], constant_test),
        }
    }
    for name in (
        "predictive_entropy",
        "answer_negative_log_likelihood",
        "mean_answer_length",
        "prompt_length",
    ):
        values = np.asarray(
            [row[name] for row in semantic_rows],
            dtype=np.float64,
        ).reshape(-1, 1)
        scalar = make_pipeline(
            StandardScaler(),
            LogisticRegression(max_iter=2000, random_state=int(probe_config["split_seed"])),
        )
        scalar.fit(values[train_indices], labels[train_indices])
        validation_probabilities = (
            scalar.predict_proba(values[validation_indices])[:, 1]
            if len(validation_indices)
            else np.asarray([], dtype=np.float64)
        )
        test_probabilities = scalar.predict_proba(values[test_indices])[:, 1]
        baseline_test_probabilities[name] = test_probabilities
        baselines[name] = {
            "validation": (
                safe_metrics(labels[validation_indices], validation_probabilities)
                if len(validation_indices)
                else None
            ),
            "test": safe_metrics(labels[test_indices], test_probabilities),
        }
        baselines[name]["test"]["auroc_bootstrap_95"] = bootstrap_auroc(
            labels[test_indices],
            test_probabilities,
            bootstrap_samples,
            bootstrap_seed + int(stable_hash(name)[:8], 16) % 10000,
            test_groups,
        )

    predeclared_analysis = None
    if "primary_layer" in probe_config:
        primary_layer = int(probe_config["primary_layer"])
        if primary_layer not in layers:
            raise ValueError(f"Predeclared primary layer {primary_layer} is not among {layers}")
        primary_row = next(row for row in layer_results if row["layer"] == primary_layer)
        combined_row = next(row for row in combined_results if row["layer"] == primary_layer)
        answer_nll_probabilities = baseline_test_probabilities[
            "answer_negative_log_likelihood"
        ]
        predeclared_analysis = {
            "primary_layer": primary_layer,
            "secondary_layers": [int(value) for value in probe_config.get("secondary_layers", [])],
            "primary_layer_test": primary_row["test"],
            "primary_hidden_plus_answer_nll_test": combined_row["test"],
            "answer_nll_test": baselines["answer_negative_log_likelihood"]["test"],
            "primary_minus_answer_nll_auroc": bootstrap_auroc_difference(
                labels[test_indices],
                layer_test_probabilities[primary_layer],
                answer_nll_probabilities,
                bootstrap_samples,
                bootstrap_seed + 40000,
                test_groups,
            ),
            "primary_hidden_plus_answer_nll_minus_answer_nll_auroc": bootstrap_auroc_difference(
                labels[test_indices],
                combined_test_probabilities_by_layer[primary_layer],
                answer_nll_probabilities,
                bootstrap_samples,
                bootstrap_seed + 50000,
                test_groups,
            ),
        }

    shuffle_repetitions = int(probe_config.get("shuffle_repetitions", 20))
    shuffle_rng = np.random.default_rng(int(probe_config["shuffle_seed"]))
    shuffled_by_layer: dict[int, list[float]] = {layer: [] for layer in layers}
    for repetition in range(shuffle_repetitions):
        shuffled_labels = shuffle_rng.permutation(labels[train_indices])
        for position, layer in enumerate(layers):
            features = hidden[:, position, :].astype(np.float32)
            shuffled = probe_model(config, int(probe_config["shuffle_seed"]) + repetition)
            shuffled.fit(features[train_indices], shuffled_labels)
            probabilities = shuffled.predict_proba(features[test_indices])[:, 1]
            shuffled_by_layer[layer].append(
                float(roc_auc_score(labels[test_indices], probabilities))
            )
    shuffled_results = []
    for layer in layers:
        values = np.asarray(shuffled_by_layer[layer], dtype=np.float64)
        shuffled_results.append(
            {
                "layer": layer,
                "repetitions": shuffle_repetitions,
                "test_auroc_mean": float(values.mean()),
                "test_auroc_std": float(values.std()),
                "test_auroc_interval_95": [
                    float(np.percentile(values, 2.5)),
                    float(np.percentile(values, 97.5)),
                ],
                "test_auroc_values": values.tolist(),
            }
        )

    sample_f1 = np.asarray(
        [row["sample_mean_f1"] for row in semantic_rows],
        dtype=np.float64,
    )
    entropy_f1_correlation = (
        float(np.corrcoef(entropy[test_indices], sample_f1[test_indices])[0, 1])
        if np.std(entropy[test_indices]) > 0 and np.std(sample_f1[test_indices]) > 0
        else None
    )
    correctness_diagnostics = {
        "test_any_sample_exact_match_rate": float(correctness[test_indices].mean()),
        "test_mean_sample_f1": float(sample_f1[test_indices].mean()),
        "test_entropy_vs_sample_f1_pearson": entropy_f1_correlation,
        "test_semantic_entropy_auroc_for_all_samples_incorrect": (
            float(roc_auc_score(1 - correctness[test_indices], entropy[test_indices]))
            if np.unique(correctness[test_indices]).size == 2
            else None
        ),
        "selected_probe_correctness_auroc": next(
            row["test"]["correctness_auroc_from_low_entropy_score"]
            for row in layer_results
            if row["layer"] == selected_layer
        ),
        "raw_answer_log_likelihood_correctness_auroc": (
            float(
                roc_auc_score(
                    correctness[test_indices],
                    -nll[test_indices, 0],
                )
            )
            if np.unique(correctness[test_indices]).size == 2
            else None
        ),
    }

    return {
        "threshold_fit_on_training_only": threshold,
        "split_method": "fixed_group_split_by_normalized_context",
        "selection_split": selection_split,
        "selected_layer": selected_layer,
        "train_indices": train_indices.tolist(),
        "validation_indices": validation_indices.tolist(),
        "test_indices": test_indices.tolist(),
        "label_distribution": {
            "train": class_counts(labels, train_indices),
            "validation": class_counts(labels, validation_indices),
            "test": class_counts(labels, test_indices),
        },
        "layers": layer_results,
        "combined_hidden_plus_answer_nll": combined_results,
        "shuffled_label_null": shuffled_results,
        "baselines": baselines,
        "correctness_diagnostics": correctness_diagnostics,
        "predeclared_analysis": predeclared_analysis,
    }


def plot_probe(config: dict[str, Any], probe: dict[str, Any], run_name: str) -> Path:
    output = root_dir() / "plots" / f"{run_name}_probe_performance_by_layer.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    layers = [row["layer"] for row in probe["layers"]]
    probe_auc = [row["test"]["auroc"] for row in probe["layers"]]
    combined_auc = [
        row["test"]["auroc"]
        for row in probe["combined_hidden_plus_answer_nll"]
    ]
    shuffled_auc = [
        row["test_auroc_mean"]
        for row in probe["shuffled_label_null"]
    ]
    shuffled_lower = [
        row["test_auroc_interval_95"][0]
        for row in probe["shuffled_label_null"]
    ]
    shuffled_upper = [
        row["test_auroc_interval_95"][1]
        for row in probe["shuffled_label_null"]
    ]
    lower_error = [
        max(0.0, value - row["test"]["auroc_bootstrap_95"]["lower_95"])
        for value, row in zip(probe_auc, probe["layers"])
    ]
    upper_error = [
        max(0.0, row["test"]["auroc_bootstrap_95"]["upper_95"] - value)
        for value, row in zip(probe_auc, probe["layers"])
    ]

    figure, axis = plt.subplots(figsize=(8.0, 5.0))
    axis.errorbar(
        layers,
        probe_auc,
        yerr=[lower_error, upper_error],
        marker="o",
        linewidth=2,
        capsize=3,
        label="Hidden-state probe (95% bootstrap CI)",
    )
    axis.plot(
        layers,
        combined_auc,
        marker="s",
        linestyle="-.",
        label="Hidden state + answer NLL",
    )
    axis.plot(
        layers,
        shuffled_auc,
        marker="o",
        linestyle="--",
        color="tab:red",
        label="Shuffled-label mean",
    )
    axis.fill_between(
        layers,
        shuffled_lower,
        shuffled_upper,
        color="tab:red",
        alpha=0.12,
        label="Shuffled-label 95% interval",
    )
    for name, color in (
        ("constant_train_mean", "gray"),
        ("predictive_entropy", "tab:green"),
        ("answer_negative_log_likelihood", "tab:orange"),
    ):
        value = probe["baselines"][name]["test"]["auroc"]
        if value is not None:
            axis.axhline(
                value,
                linestyle=":",
                color=color,
                label=name.replace("_", " "),
            )
    axis.axvline(
        probe["selected_layer"],
        color="black",
        alpha=0.18,
        linewidth=1,
        label="Validation-selected layer",
    )
    predeclared = probe.get("predeclared_analysis")
    if predeclared is not None:
        axis.axvline(
            predeclared["primary_layer"],
            color="tab:purple",
            alpha=0.65,
            linewidth=1.5,
            linestyle="--",
            label="Predeclared primary layer",
        )
    axis.set(
        xlabel="Transformer block",
        ylabel="Held-out test AUROC",
        title=f"Stage 0 confidence-probe stability — {run_name}",
        ylim=(0, 1),
    )
    axis.set_xticks(layers)
    axis.grid(alpha=0.25)
    axis.legend(fontsize=8, ncol=2)
    figure.tight_layout()
    figure.savefig(output, dpi=180)
    plt.close(figure)
    return output


def audit_split(records: list[dict[str, Any]], probe: dict[str, Any]) -> dict[str, Any]:
    split_indices = {
        "train": probe["train_indices"],
        "validation": probe.get("validation_indices", []),
        "test": probe["test_indices"],
    }

    def normalized(value: str) -> str:
        return " ".join(value.lower().split())

    split_values = {}
    for split_name, indices in split_indices.items():
        split_values[split_name] = {
            "ids": {records[index]["id"] for index in indices},
            "contexts": {normalized(records[index]["context"]) for index in indices},
            "questions": {normalized(records[index]["question"]) for index in indices},
        }

    pairwise = {}
    split_pairs = (
        ("train", "validation"),
        ("train", "test"),
        ("validation", "test"),
    )
    for left_name, right_name in split_pairs:
        left_indices = split_indices[left_name]
        right_indices = split_indices[right_name]
        near_duplicates = []
        for left_index in left_indices:
            left_tokens = set(normalize_answer(records[left_index]["question"]).split())
            for right_index in right_indices:
                right_tokens = set(normalize_answer(records[right_index]["question"]).split())
                union = left_tokens | right_tokens
                similarity = len(left_tokens & right_tokens) / len(union) if union else 1.0
                if similarity >= 0.9:
                    near_duplicates.append(
                        {
                            "left_index": left_index,
                            "right_index": right_index,
                            "token_jaccard": similarity,
                        }
                    )
        left_values = split_values[left_name]
        right_values = split_values[right_name]
        pairwise[f"{left_name}_vs_{right_name}"] = {
            "id_overlap_count": len(left_values["ids"] & right_values["ids"]),
            "exact_question_overlap_count": len(
                left_values["questions"] & right_values["questions"]
            ),
            "exact_context_overlap_count": len(
                left_values["contexts"] & right_values["contexts"]
            ),
            "near_duplicate_question_pairs_at_jaccard_0.9": near_duplicates,
        }

    result = {
        "split_sizes": {
            name: len(indices)
            for name, indices in split_indices.items()
        },
        "unique_context_counts": {
            name: len(split_values[name]["contexts"])
            for name in split_indices
        },
        "pairwise": pairwise,
    }
    result["passed"] = all(
        audit["id_overlap_count"] == 0
        and audit["exact_question_overlap_count"] == 0
        and audit["exact_context_overlap_count"] == 0
        and not audit["near_duplicate_question_pairs_at_jaccard_0.9"]
        for audit in pairwise.values()
    )
    return result


def audit_dataset_exclusions(
    config: dict[str, Any], records: list[dict[str, Any]]
) -> dict[str, Any] | None:
    excluded_records = _excluded_dataset_records(config)
    if not excluded_records:
        return None
    threshold = config["dataset"].get("exclude_near_duplicate_questions_at_jaccard")
    excluded_ids = {record["id"] for record in excluded_records}
    excluded_contexts = {_normalized_text(record["context"]) for record in excluded_records}
    excluded_questions = {_normalized_text(record["question"]) for record in excluded_records}
    near_duplicates = []
    if threshold is not None:
        for index, record in enumerate(records):
            for excluded_index, excluded in enumerate(excluded_records):
                similarity = _question_jaccard(record["question"], excluded["question"])
                if similarity >= float(threshold):
                    near_duplicates.append(
                        {
                            "index": index,
                            "excluded_index": excluded_index,
                            "token_jaccard": similarity,
                        }
                    )
    result = {
        "excluded_result_runs": config["dataset"].get("exclude_result_runs", []),
        "excluded_record_count": len(excluded_records),
        "id_overlap_count": sum(record["id"] in excluded_ids for record in records),
        "exact_context_overlap_count": sum(
            _normalized_text(record["context"]) in excluded_contexts for record in records
        ),
        "exact_question_overlap_count": sum(
            _normalized_text(record["question"]) in excluded_questions for record in records
        ),
        "near_duplicate_question_pairs": near_duplicates,
    }
    result["passed"] = (
        result["id_overlap_count"] == 0
        and result["exact_context_overlap_count"] == 0
        and result["exact_question_overlap_count"] == 0
        and not near_duplicates
    )
    return result


def evaluate_confirmation_gates(
    config: dict[str, Any], probe: dict[str, Any]
) -> dict[str, Any] | None:
    gates = config.get("confirmation_gates")
    analysis = probe.get("predeclared_analysis")
    if not gates or analysis is None:
        return None
    primary_layer = int(analysis["primary_layer"])
    primary = analysis["primary_layer_test"]
    shuffled = next(
        row for row in probe["shuffled_label_null"] if int(row["layer"]) == primary_layer
    )
    incremental = analysis[
        "primary_hidden_plus_answer_nll_minus_answer_nll_auroc"
    ]
    signal_results = {
        "primary_test_auroc": primary["auroc"]
        >= float(gates["primary_test_auroc_min"]),
        "primary_test_auroc_lower_95": primary["auroc_bootstrap_95"]["lower_95"]
        >= float(gates["primary_test_auroc_lower_95_min"]),
        "primary_above_shuffled_upper_95": primary["auroc"]
        > float(shuffled["test_auroc_interval_95"][1]),
    }
    incremental_results = {
        "hidden_plus_nll_minus_nll_lower_95": incremental is not None
        and incremental["lower_95"]
        > float(gates["hidden_plus_nll_minus_nll_lower_95_min"]),
    }
    return {
        "primary_layer": primary_layer,
        "thresholds": gates,
        "signal_gate_results": signal_results,
        "incremental_gate_results": incremental_results,
        "measurement_signal_passed": bool(all(signal_results.values())),
        "incremental_information_passed": bool(all(incremental_results.values())),
        "ready_for_mechanistic_loss": bool(
            all(signal_results.values()) and all(incremental_results.values())
        ),
    }


def checks_for_run(
    run_name: str,
    config: dict[str, Any],
    records: list[dict[str, Any]],
    hidden: np.ndarray,
    semantic_rows: list[dict[str, Any]],
    probe: dict[str, Any] | None,
) -> dict[str, Any]:
    expected = int(config["runs"][run_name]["num_examples"])
    expected_generations = int(config["runs"][run_name]["num_generations"])
    generations = [generation for record in records for generation in record["generations"]]
    nonempty_fraction = float(np.mean([bool(generation["normalized_text"]) for generation in generations]))
    distinct_answers = len({generation["normalized_text"] for generation in generations if generation["normalized_text"]})
    entropy = np.asarray([row["cluster_assignment_entropy"] for row in semantic_rows])
    clusters = np.asarray([row["num_semantic_clusters"] for row in semantic_rows])
    individual = {
        "model_and_examples_completed": len(records) == expected,
        "generation_count_correct": all(len(record["generations"]) == expected_generations for record in records),
        "answers_nonempty": nonempty_fraction >= 0.8,
        "answers_not_globally_identical": distinct_answers > 1,
        "final_prompt_token_verified": all(record["final_prompt_token_index"] == record["prompt_token_count"] - 1 for record in records),
        "prompt_suffix_preserved": all(record["prompt_suffix_preserved"] for record in records),
        "hidden_shape_verified": hidden.shape[:2] == (expected, len(config["generation"]["layers"])),
        "hidden_finite": bool(np.isfinite(hidden).all()),
        "correctness_metrics_finite": bool(np.isfinite([generation["f1"] for generation in generations]).all()),
        "semantic_entropy_finite": bool(np.isfinite(entropy).all()),
        "semantic_entropy_varies": bool(np.ptp(entropy) > 1e-8),
        "cluster_count_varies": bool(np.ptp(clusters) > 0),
        "probe_trained": probe is not None,
        "split_leakage_audit_passed": probe is None or probe["split_audit"]["passed"],
    }
    required = [
        "model_and_examples_completed",
        "generation_count_correct",
        "answers_nonempty",
        "answers_not_globally_identical",
        "final_prompt_token_verified",
        "prompt_suffix_preserved",
        "hidden_shape_verified",
        "hidden_finite",
        "correctness_metrics_finite",
        "semantic_entropy_finite",
    ]
    if run_name != "preflight":
        required += ["semantic_entropy_varies", "cluster_count_varies", "probe_trained", "split_leakage_audit_passed"]
    return {
        "passed": all(individual[name] for name in required),
        "checks": individual,
        "diagnostics": {
            "nonempty_generation_fraction": nonempty_fraction,
            "distinct_normalized_answers": distinct_answers,
            "truncated_prompt_count": sum(bool(record["prompt_was_truncated"]) for record in records),
            "sample_exact_match_rate": float(np.mean([generation["exact_match"] for generation in generations])),
            "sample_mean_f1": float(np.mean([generation["f1"] for generation in generations])),
            "semantic_entropy_mean": float(entropy.mean()),
            "semantic_entropy_std": float(entropy.std()),
            "semantic_entropy_values": sorted({float(value) for value in entropy}),
            "cluster_count_distribution": {str(key): int(value) for key, value in Counter(clusters.tolist()).items()},
            "hidden_shape": list(hidden.shape),
            "hidden_dtype": str(hidden.dtype),
        },
    }


def run(config: dict[str, Any], run_name: str) -> dict[str, Any]:
    if run_name not in config["runs"]:
        raise ValueError(f"Unknown run: {run_name}")
    run_config = config["runs"][run_name]
    results_dir = Path(config["project"]["results_dir"]) / run_name
    results_dir.mkdir(parents=True, exist_ok=True)
    examples = fixed_dataset(config, int(run_config["num_examples"]))
    records, hidden, generator_runtime = generate(config, run_name, examples)
    if run_config["grouping"] == "exact_match":
        semantic_rows, judgments, grouping_runtime = semantic_rows_exact(records)
    elif run_config["grouping"] == "nli":
        semantic_rows, judgments, grouping_runtime = semantic_rows_nli(config, records)
    else:
        raise ValueError(f"Unknown grouping mode: {run_config['grouping']}")
    write_jsonl(results_dir / "generations.jsonl", records)
    write_jsonl(results_dir / "semantic_entropy.jsonl", semantic_rows)
    write_jsonl(results_dir / "entailment_judgments.jsonl", judgments)
    np.savez_compressed(
        results_dir / "hidden_states.npz",
        hidden_states=hidden,
        layers=np.asarray(config["generation"]["layers"], dtype=np.int16),
        example_ids=np.asarray([record["id"] for record in records]),
    )
    probe = None
    probe_error = None
    if run_config.get("train_probe", False):
        try:
            probe = train_probe(config, hidden, semantic_rows, records)
            probe["split_audit"] = audit_split(records, probe)
            probe["confirmation_gates"] = evaluate_confirmation_gates(config, probe)
            atomic_json(results_dir / "probe_metrics.json", probe)
            plot_probe(config, probe, run_name)
        except ValueError as error:
            probe_error = str(error)
            LOGGER.warning("Probe could not be trained: %s", error)
    checks = checks_for_run(run_name, config, records, hidden, semantic_rows, probe)
    exclusion_audit = audit_dataset_exclusions(config, records)
    if exclusion_audit is not None:
        checks["checks"]["fresh_dataset_exclusion_passed"] = exclusion_audit["passed"]
        checks["passed"] = bool(checks["passed"] and exclusion_audit["passed"])
    manifest = {
        "run": run_name,
        "configuration": portable_config(config),
        "versions": runtime_versions(),
        "generator_runtime": generator_runtime,
        "grouping_runtime": grouping_runtime,
        "checks": checks,
        "source_exclusion_audit": exclusion_audit,
        "probe_error": probe_error,
    }
    atomic_json(results_dir / "manifest.json", manifest)
    return manifest
