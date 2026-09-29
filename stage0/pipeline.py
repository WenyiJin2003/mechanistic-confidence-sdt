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
from sklearn.model_selection import train_test_split
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


def fixed_dataset(config: dict[str, Any], count: int) -> list[dict[str, Any]]:
    cache_path = Path(config["project"]["cache_dir"]) / "dataset" / "squad_v2_fixed_subset.jsonl"
    maximum = max(int(run["num_examples"]) for run in config["runs"].values())
    if cache_path.exists():
        cached = read_jsonl(cache_path)
        if len(cached) >= count:
            return cached[:count]
    dataset_config = config["dataset"]
    dataset = datasets.load_dataset(
        dataset_config["id"],
        split=dataset_config["split"],
        cache_dir=config["project"]["hf_cache_dir"],
    )
    candidates = []
    for row in dataset:
        answers = list(row["answers"]["text"])
        if dataset_config.get("answerable_only", True) and not answers:
            continue
        candidates.append(
            {
                "id": str(row["id"]),
                "question": row["question"],
                "context": row.get("context", ""),
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
        inputs = self.tokenizer(
            rendered,
            return_tensors="pt",
            truncation=True,
            max_length=self.max_prompt_tokens,
        ).to(self.device)
        prompt_length = int(inputs["input_ids"].shape[1])
        final_token_id = int(inputs["input_ids"][0, -1].item())
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
            "final_prompt_token_index": prompt_length - 1,
            "final_prompt_token_id": final_token_id,
            "final_prompt_token_text": self.tokenizer.decode([final_token_id]),
            "layers": self.layers,
            "generations": generations,
        }
        return record, hidden

    def close(self) -> None:
        del self.model, self.tokenizer
        clear_device_cache()


def _generation_key(config: dict[str, Any], example: dict[str, Any], run_config: dict[str, Any], index: int) -> str:
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
    hidden_cache_hits = 0
    try:
        for index, example in enumerate(tqdm(examples, desc=f"{run_name}: Qwen")):
            key = _generation_key(config, example, run_config, index)
            hidden_key = _hidden_key(config, example)
            json_path = shared_dir / f"{key}.json"
            hidden_path = shared_dir / f"hidden-{hidden_key}.npz"
            if not hidden_path.exists():
                for previous_run in config["runs"].values():
                    legacy_key = _generation_key(config, example, previous_run, index)
                    legacy_path = shared_dir / f"{legacy_key}.npz"
                    if legacy_path.exists():
                        legacy_hidden = np.load(legacy_path)["hidden"]
                        np.savez_compressed(
                            hidden_path,
                            hidden=legacy_hidden,
                            layers=np.asarray(config["generation"]["layers"], dtype=np.int16),
                        )
                        break
            if json_path.exists() and hidden_path.exists():
                with json_path.open("r", encoding="utf-8") as handle:
                    record = json.load(handle)
                hidden = np.load(hidden_path)["hidden"]
                generation_cache_hits += 1
                hidden_cache_hits += 1
            else:
                cached_hidden = np.load(hidden_path)["hidden"] if hidden_path.exists() else None
                if cached_hidden is not None:
                    hidden_cache_hits += 1
                record, hidden = generator.run_example(
                    example,
                    config["dataset"],
                    config["generation"],
                    run_config,
                    int(config["project"]["seed"]) + index,
                    cached_hidden=cached_hidden,
                )
                record["cache_key"] = key
                atomic_json(json_path, record)
                np.savez_compressed(hidden_path, hidden=hidden, layers=np.asarray(record["layers"], dtype=np.int16))
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
        predictions = nli.predict([needed[key] for key in keys])
        runtime["device"] = str(nli.device)
        runtime["dtype"] = str(nli.dtype).replace("torch.", "")
        for key, prediction in zip(keys, predictions):
            premise, hypothesis = needed[key]
            cache[key] = {"premise": premise, "hypothesis": hypothesis, **prediction}
        atomic_json(cache_path, cache)
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
    return {
        "id": record["id"],
        "semantic_ids": cluster_ids,
        "num_semantic_clusters": len(set(cluster_ids)),
        "cluster_assignment_entropy": cluster_entropy(cluster_ids),
        "predictive_entropy": float(-np.mean(mean_logprobs)),
        "answer_negative_log_likelihood": float(-np.mean(sequence_logprobs)),
        "mean_answer_length": float(np.mean(lengths)),
        "prompt_length": int(record["prompt_token_count"]),
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
    predictions = (probabilities >= 0.5).astype(np.int64)
    return {
        "accuracy": float(accuracy_score(labels, predictions)),
        "auroc": float(roc_auc_score(labels, probabilities)) if np.unique(labels).size == 2 else None,
        "log_loss": float(log_loss(labels, np.column_stack([1 - probabilities, probabilities]), labels=[0, 1])),
    }


def train_probe(config: dict[str, Any], hidden: np.ndarray, semantic_rows: list[dict[str, Any]]) -> dict[str, Any]:
    entropy = np.asarray([row["cluster_assignment_entropy"] for row in semantic_rows], dtype=np.float64)
    indices = np.arange(len(entropy))
    train_indices, test_indices = train_test_split(
        indices,
        test_size=float(config["probe"]["test_fraction"]),
        random_state=int(config["probe"]["split_seed"]),
    )
    threshold = best_train_threshold(entropy[train_indices])
    labels = (entropy >= threshold).astype(np.int64)
    if np.unique(labels[train_indices]).size < 2:
        raise ValueError("Probe training split has one class")
    layers = [int(value) for value in config["generation"]["layers"]]
    layer_results = []
    shuffled_results = []
    shuffled_labels = np.random.default_rng(int(config["probe"]["shuffle_seed"])).permutation(labels[train_indices])
    for position, layer in enumerate(layers):
        features = hidden[:, position, :].astype(np.float32)
        model = make_pipeline(
            StandardScaler(),
            LogisticRegression(
                C=float(config["probe"]["c"]),
                max_iter=int(config["probe"]["max_iter"]),
                random_state=int(config["probe"]["split_seed"]),
            ),
        )
        model.fit(features[train_indices], labels[train_indices])
        probabilities = model.predict_proba(features[test_indices])[:, 1]
        layer_results.append({"layer": layer, **safe_metrics(labels[test_indices], probabilities)})

        shuffled = make_pipeline(
            StandardScaler(),
            LogisticRegression(
                C=float(config["probe"]["c"]),
                max_iter=int(config["probe"]["max_iter"]),
                random_state=int(config["probe"]["split_seed"]),
            ),
        )
        shuffled.fit(features[train_indices], shuffled_labels)
        shuffled_probabilities = shuffled.predict_proba(features[test_indices])[:, 1]
        shuffled_results.append({"layer": layer, **safe_metrics(labels[test_indices], shuffled_probabilities)})

    train_mean = float(labels[train_indices].mean())
    baselines = {"constant_train_mean": safe_metrics(labels[test_indices], np.full(len(test_indices), train_mean))}
    for name in ("predictive_entropy", "answer_negative_log_likelihood", "mean_answer_length", "prompt_length"):
        values = np.asarray([row[name] for row in semantic_rows], dtype=np.float64).reshape(-1, 1)
        scalar = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000, random_state=42))
        scalar.fit(values[train_indices], labels[train_indices])
        baselines[name] = safe_metrics(labels[test_indices], scalar.predict_proba(values[test_indices])[:, 1])
    return {
        "threshold_fit_on_training_only": threshold,
        "train_indices": train_indices.tolist(),
        "test_indices": test_indices.tolist(),
        "label_distribution": {
            "train": {str(key): int(value) for key, value in Counter(labels[train_indices].tolist()).items()},
            "test": {str(key): int(value) for key, value in Counter(labels[test_indices].tolist()).items()},
        },
        "layers": layer_results,
        "shuffled_label_layers": shuffled_results,
        "baselines": baselines,
    }


def plot_probe(config: dict[str, Any], probe: dict[str, Any]) -> Path:
    output = root_dir() / "plots" / "probe_performance_by_layer.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    layers = [row["layer"] for row in probe["layers"]]
    probe_auc = [row["auroc"] if row["auroc"] is not None else 0.5 for row in probe["layers"]]
    shuffled_auc = [row["auroc"] if row["auroc"] is not None else 0.5 for row in probe["shuffled_label_layers"]]
    figure, axis = plt.subplots(figsize=(7.2, 4.6))
    axis.plot(layers, probe_auc, marker="o", linewidth=2, label="Linear probe")
    axis.plot(layers, shuffled_auc, marker="o", linestyle="--", label="Shuffled labels")
    for name, color in (("constant_train_mean", "gray"), ("predictive_entropy", "tab:green"), ("answer_negative_log_likelihood", "tab:orange")):
        value = probe["baselines"][name]["auroc"]
        if value is not None:
            axis.axhline(value, linestyle=":", color=color, label=name.replace("_", " "))
    axis.set(xlabel="Transformer block", ylabel="Held-out AUROC", title="Stage 0 probe performance by layer", ylim=(0, 1))
    axis.set_xticks(layers)
    axis.grid(alpha=0.25)
    axis.legend(fontsize=8, ncol=2)
    figure.tight_layout()
    figure.savefig(output, dpi=180)
    plt.close(figure)
    return output


def audit_split(records: list[dict[str, Any]], probe: dict[str, Any]) -> dict[str, Any]:
    train_indices = probe["train_indices"]
    test_indices = probe["test_indices"]

    def normalized(value: str) -> str:
        return " ".join(value.lower().split())

    train_ids = {records[index]["id"] for index in train_indices}
    test_ids = {records[index]["id"] for index in test_indices}
    train_contexts = {normalized(records[index]["context"]) for index in train_indices}
    test_contexts = {normalized(records[index]["context"]) for index in test_indices}
    train_questions = {normalized(records[index]["question"]) for index in train_indices}
    test_questions = {normalized(records[index]["question"]) for index in test_indices}
    near_duplicate_pairs = []
    for train_index in train_indices:
        left = set(normalize_answer(records[train_index]["question"]).split())
        for test_index in test_indices:
            right = set(normalize_answer(records[test_index]["question"]).split())
            union = left | right
            similarity = len(left & right) / len(union) if union else 1.0
            if similarity >= 0.9:
                near_duplicate_pairs.append(
                    {"train_index": train_index, "test_index": test_index, "token_jaccard": similarity}
                )
    result = {
        "id_overlap_count": len(train_ids & test_ids),
        "exact_question_overlap_count": len(train_questions & test_questions),
        "exact_context_overlap_count": len(train_contexts & test_contexts),
        "near_duplicate_question_pairs_at_jaccard_0.9": near_duplicate_pairs,
    }
    result["passed"] = all(
        [
            result["id_overlap_count"] == 0,
            result["exact_question_overlap_count"] == 0,
            result["exact_context_overlap_count"] == 0,
            len(near_duplicate_pairs) == 0,
        ]
    )
    return result


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
        "hidden_shape_verified": hidden.shape[:2] == (expected, len(config["generation"]["layers"])),
        "hidden_finite": bool(np.isfinite(hidden).all()),
        "semantic_entropy_finite": bool(np.isfinite(entropy).all()),
        "semantic_entropy_varies": bool(np.ptp(entropy) > 1e-8),
        "cluster_count_varies": bool(np.ptp(clusters) > 0),
        "probe_trained": probe is not None,
    }
    required = [
        "model_and_examples_completed",
        "generation_count_correct",
        "answers_nonempty",
        "answers_not_globally_identical",
        "final_prompt_token_verified",
        "hidden_shape_verified",
        "hidden_finite",
        "semantic_entropy_finite",
    ]
    if run_name != "preflight":
        required += ["semantic_entropy_varies", "cluster_count_varies", "probe_trained"]
    return {
        "passed": all(individual[name] for name in required),
        "checks": individual,
        "diagnostics": {
            "nonempty_generation_fraction": nonempty_fraction,
            "distinct_normalized_answers": distinct_answers,
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
            probe = train_probe(config, hidden, semantic_rows)
            probe["split_audit"] = audit_split(records, probe)
            atomic_json(results_dir / "probe_metrics.json", probe)
            plot_probe(config, probe)
        except ValueError as error:
            probe_error = str(error)
            LOGGER.warning("Probe could not be trained: %s", error)
    checks = checks_for_run(run_name, config, records, hidden, semantic_rows, probe)
    manifest = {
        "run": run_name,
        "configuration": portable_config(config),
        "versions": runtime_versions(),
        "generator_runtime": generator_runtime,
        "grouping_runtime": grouping_runtime,
        "checks": checks,
        "probe_error": probe_error,
    }
    atomic_json(results_dir / "manifest.json", manifest)
    return manifest
