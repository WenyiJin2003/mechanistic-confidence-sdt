#!/usr/bin/env python3
"""Cache-only, source-paired all-layer probe learning curves.

This module never imports transformers or loads a language model.  It consumes
already-pooled response-mean activations and fits the preregistered symmetric
paired logistic readout independently at each of Qwen's 28 layers.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any, Iterable, Mapping, Sequence
import unicodedata

import numpy as np
import sklearn
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler


MODEL_ID = "Qwen/Qwen2.5-1.5B-Instruct"
MODEL_REVISION = "989aa7980e4cf806f80c7fef2b1adb7bc71aa306"
FEATURE_SETTINGS_SHA256 = "636f0513795e9ed72f0c0b65f50d91e614bfb2c624d9e20ec13dd169146d5138"
SPLIT_FREEZE_SHA256 = "84391340c85ced2863d8b2c4181a12c724ba96a138afb488de8bf5f6444733ea"
EXPECTED_LAYER_IDS = tuple(range(1, 29))
EXPECTED_HIDDEN_SIZE = 1536
# The final maximum is read from the separately frozen split manifest.  The
# current freeze is 200/500/920, but the runner binds the manifest rather than
# trusting a command-line count.
TRAIN_PREFIXES = (200, 500)
PRIMARY_LAYER_ID = 14
ENSEMBLE_NAME = "equal28_train_standardized_scores"
ENSEMBLE_LAYER_IDS = EXPECTED_LAYER_IDS
LOGISTIC_C = 0.01
LOGISTIC_MAX_ITER = 2000
BOOTSTRAP_REPLICATES = 2000
BOOTSTRAP_SEED = 20261104
SPLIT_ORDER = ("train", "dev", "internal_test", "external_cf3")
PROJECT_ROOT = Path(__file__).resolve().parents[3]


class ContractError(ValueError):
    """Raised when a frozen input or leakage invariant is violated."""


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def pair_content_sha256(row: Mapping[str, Any]) -> str:
    """Bind a pair ID to the exact prompt and ordered response texts."""
    payload = {
        "id": row["id"], "source_id": row["source_id"],
        "question": row["question"],
        "confident_response": row["confident_response"],
        "hesitant_response": row["hesitant_response"],
    }
    return hashlib.sha256(canonical_json_bytes(payload)).hexdigest()


def response_content_sha256(row: Mapping[str, Any], role: str) -> str:
    if role not in ("confident", "hesitant"):
        raise ContractError("response role must be confident or hesitant")
    payload = {
        "id": row["id"], "source_id": row["source_id"],
        "question": row["question"], "role": role,
        "response": row[f"{role}_response"],
    }
    return hashlib.sha256(canonical_json_bytes(payload)).hexdigest()


def state_binding_sha256(state: np.ndarray, response_hash: str) -> str:
    """Bind one pooled state tensor to its declared exact response."""
    contiguous = np.ascontiguousarray(state)
    header = canonical_json_bytes({
        "response_content_sha256": response_hash,
        "dtype": contiguous.dtype.str,
        "shape": list(contiguous.shape),
    })
    return hashlib.sha256(header + contiguous.tobytes(order="C")).hexdigest()


def normalized_question(value: str) -> str:
    """The frozen exact-question identity: NFKC, whitespace collapse, casefold."""
    return " ".join(unicodedata.normalize("NFKC", value).split()).casefold()


def atomic_write_json(path: Path, value: Any) -> None:
    payload = canonical_json_bytes(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"refusing to overwrite existing output: {path}")
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            descriptor = -1
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        temporary.unlink(missing_ok=True)


def load_jsonl(path: Path, split_name: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ContractError(f"invalid JSON at {path}:{line_number}") from exc
        if type(row) is not dict:
            raise ContractError(f"row at {path}:{line_number} must be a plain object")
        required = ("id", "source_id", "group_id", "question",
                    "confident_response", "hesitant_response",
                    "source_collection", "atomic_group_id",
                    "original_record_sha256")
        for key in required:
            value = row.get(key)
            if not isinstance(value, str) or not value.strip():
                raise ContractError(f"{split_name} row {line_number} has invalid {key}")
        if row["confident_response"] == row["hesitant_response"]:
            raise ContractError(f"{split_name} pair {row['id']} has identical responses")
        rows.append(row)
    if not rows:
        raise ContractError(f"{split_name} is empty")
    return rows


def load_split_freeze(
    path: Path,
    data_paths: Mapping[str, Path],
) -> tuple[dict[str, int], tuple[int, ...], dict[str, Any]]:
    """Authenticate dynamic counts and the preregistered nested train sizes."""
    observed_freeze_sha256 = file_sha256(path)
    if observed_freeze_sha256 != SPLIT_FREEZE_SHA256:
        raise ContractError("split-freeze SHA-256 differs from the exact frozen manifest")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ContractError("split freeze is not valid JSON") from exc
    if type(value) is not dict or value.get("schema") != "confidence-probe-scaleup-split-freeze-v1":
        raise ContractError("unexpected split-freeze schema")
    declared = value.get("splits")
    required_records = set(SPLIT_ORDER) | {"train_200", "train_500"}
    if type(declared) is not dict or set(declared) != required_records:
        raise ContractError(f"split freeze must contain exactly {sorted(required_records)}")
    counts: dict[str, int] = {}
    file_audit: dict[str, Any] = {}
    for split in SPLIT_ORDER:
        record = declared.get(split)
        if type(record) is not dict:
            raise ContractError(f"split freeze record missing for {split}")
        count, wanted_hash = record.get("count"), record.get("sha256")
        if type(count) is not int or count <= 0:
            raise ContractError(f"invalid frozen count for {split}")
        if not isinstance(wanted_hash, str) or len(wanted_hash) != 64:
            raise ContractError(f"invalid frozen SHA-256 for {split}")
        observed = file_sha256(data_paths[split])
        if observed != wanted_hash:
            raise ContractError(f"{split} JSONL differs from split freeze")
        counts[split] = count
        file_audit[split] = {"count": count, "sha256": observed}
    train_sizes_raw = value.get("nested_train_sizes")
    if not isinstance(train_sizes_raw, list) or any(type(x) is not int for x in train_sizes_raw):
        raise ContractError("split freeze needs integer nested_train_sizes")
    train_sizes = tuple(train_sizes_raw)
    expected_sizes = TRAIN_PREFIXES + (counts["train"],)
    if train_sizes != expected_sizes or counts["train"] < 500:
        raise ContractError(f"nested_train_sizes must be {expected_sizes}")
    prefix_hashes: dict[str, str] = {}
    for size, record_name in ((200, "train_200"), (500, "train_500")):
        record = declared[record_name]
        if type(record) is not dict or record.get("count") != size:
            raise ContractError(f"invalid {record_name} freeze record")
        raw_path = Path(str(record.get("path", "")))
        prefix_path = raw_path if raw_path.is_absolute() else PROJECT_ROOT / raw_path
        if not prefix_path.is_file() or file_sha256(prefix_path) != record.get("sha256"):
            raise ContractError(f"{record_name} file differs from split freeze")
        prefix_rows = load_jsonl(prefix_path, record_name)
        if len(prefix_rows) != size:
            raise ContractError(f"{record_name} row count changed")
        ids = [str(row["id"]) for row in prefix_rows]
        prefix_hashes[str(size)] = hashlib.sha256(
            ("\n".join(ids) + "\n").encode("utf-8")).hexdigest()
    # The max prefix is the complete frozen train file.
    max_rows = load_jsonl(data_paths["train"], "train")
    max_ids = [str(row["id"]) for row in max_rows]
    prefix_hashes[str(counts["train"])] = hashlib.sha256(
        ("\n".join(max_ids) + "\n").encode("utf-8")).hexdigest()
    return counts, train_sizes, {
        "path": str(path), "sha256": observed_freeze_sha256, "files": file_audit,
        "nested_train_id_sha256": prefix_hashes,
    }


def _duplicates(values: Iterable[str]) -> set[str]:
    seen: set[str] = set()
    duplicate: set[str] = set()
    for value in values:
        if value in seen:
            duplicate.add(value)
        seen.add(value)
    return duplicate


def validate_split_rows(
    splits: Mapping[str, Sequence[Mapping[str, Any]]],
    *,
    expected_counts: Mapping[str, int] | None = None,
    train_sizes: Sequence[int] = (200, 500, 920),
    expected_prefix_hashes: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    if tuple(splits) != SPLIT_ORDER:
        raise ContractError(f"splits must be supplied in order {SPLIT_ORDER}")
    if sorted(train_sizes) != list(train_sizes) or len(set(train_sizes)) != len(train_sizes):
        raise ContractError("train sizes must be distinct and increasing")
    if any(size <= 0 for size in train_sizes):
        raise ContractError("train sizes must be positive")
    if expected_counts is not None:
        for split, expected in expected_counts.items():
            if len(splits[split]) != expected:
                raise ContractError(f"{split} count {len(splits[split])} != {expected}")
    if max(train_sizes) > len(splits["train"]):
        raise ContractError("largest train size exceeds the frozen train split")

    audit: dict[str, Any] = {"counts": {}, "train_sizes": list(train_sizes)}
    for name, rows in splits.items():
        ids = [str(row["id"]) for row in rows]
        sources = [str(row["source_id"]) for row in rows]
        if _duplicates(ids):
            raise ContractError(f"duplicate pair IDs within {name}")
        if _duplicates(sources):
            raise ContractError(f"duplicate source IDs within {name}")
        audit["counts"][name] = len(rows)

    # No source, row, or construction group may cross a split boundary.
    for left_index, left in enumerate(SPLIT_ORDER):
        for right in SPLIT_ORDER[left_index + 1:]:
            for key in ("id", "source_id", "group_id", "atomic_group_id", "source_collection",
                        "original_record_sha256"):
                if not all(row.get(key) not in (None, "") for row in splits[left]):
                    if key == "original_record_sha256":
                        continue
                    raise ContractError(f"{left} is missing required leakage key {key}")
                if not all(row.get(key) not in (None, "") for row in splits[right]):
                    if key == "original_record_sha256":
                        continue
                    raise ContractError(f"{right} is missing required leakage key {key}")
                overlap = ({str(row[key]) for row in splits[left]} &
                           {str(row[key]) for row in splits[right]})
                if overlap:
                    example = sorted(overlap)[0]
                    raise ContractError(f"{key} leakage between {left} and {right}: {example}")
            left_questions = {normalized_question(str(row["question"])) for row in splits[left]}
            right_questions = {normalized_question(str(row["question"])) for row in splits[right]}
            question_overlap = left_questions & right_questions
            if question_overlap:
                raise ContractError(f"exact normalized-question leakage between {left} and {right}")

    nested = [tuple(str(row["id"]) for row in splits["train"][:size])
              for size in train_sizes]
    for previous, current in zip(nested, nested[1:]):
        if current[:len(previous)] != previous:
            raise ContractError("train cohorts are not strict prefixes")
    for size in train_sizes[:-1]:
        prefix_groups = {str(row["group_id"]) for row in splits["train"][:size]}
        suffix_groups = {str(row["group_id"]) for row in splits["train"][size:]}
        if prefix_groups & suffix_groups:
            raise ContractError(f"train prefix {size} splits an identity group")
    audit["nested_prefix_sha256"] = {
        str(size): hashlib.sha256(("\n".join(ids) + "\n").encode("utf-8")).hexdigest()
        for size, ids in zip(train_sizes, nested)
    }
    if expected_prefix_hashes is not None and audit["nested_prefix_sha256"] != dict(expected_prefix_hashes):
        raise ContractError("nested train ID prefixes differ from the split freeze")
    return audit


def _scalar_text(array: np.ndarray, key: str) -> str:
    if array.shape != ():
        raise ContractError(f"activation bundle {key} must be scalar")
    return str(array.item())


def load_activation_bundle(
    path: Path,
    rows: Sequence[Mapping[str, Any]],
    *,
    expected_layers: Sequence[int] = EXPECTED_LAYER_IDS,
    expected_hidden_size: int = EXPECTED_HIDDEN_SIZE,
    expected_settings_sha256: str = FEATURE_SETTINGS_SHA256,
    expected_model_revision: str = MODEL_REVISION,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Load and reorder a consolidated activation bundle to JSONL row order.

    Required NPZ keys are ``pair_ids``, ``states``, ``layer_ids``, ``position``,
    ``settings_sha256``, and ``model_revision``.  ``states`` has shape
    ``[N, 2, L, D]`` with response axis ``[confident, hesitant]``.
    """
    required = {
        "pair_ids", "pair_content_sha256", "pair_order",
        "response_content_sha256", "state_binding_sha256", "states",
        "layer_ids", "position", "settings_sha256", "model_id", "model_revision",
    }
    with np.load(path, allow_pickle=False) as saved:
        missing = required - set(saved.files)
        if missing:
            raise ContractError(f"activation bundle missing keys: {sorted(missing)}")
        pair_ids = [str(value) for value in saved["pair_ids"].tolist()]
        content_hashes = [str(value) for value in saved["pair_content_sha256"].tolist()]
        pair_order = tuple(str(value) for value in saved["pair_order"].tolist())
        response_hashes = np.asarray(saved["response_content_sha256"]).astype(str)
        state_bindings = np.asarray(saved["state_binding_sha256"]).astype(str)
        states = np.asarray(saved["states"])
        layer_ids = tuple(int(value) for value in saved["layer_ids"].tolist())
        position = _scalar_text(saved["position"], "position")
        settings = _scalar_text(saved["settings_sha256"], "settings_sha256")
        model_id = _scalar_text(saved["model_id"], "model_id")
        revision = _scalar_text(saved["model_revision"], "model_revision")
    if _duplicates(pair_ids):
        raise ContractError("activation bundle contains duplicate pair IDs")
    if pair_order != ("confident", "hesitant"):
        raise ContractError("activation response axis must be [confident, hesitant]")
    if states.ndim != 4 or states.shape[1] != 2:
        raise ContractError("states must have shape [N, 2, L, D]")
    if states.shape[0] != len(pair_ids):
        raise ContractError("pair ID count does not match activation rows")
    if len(content_hashes) != len(pair_ids):
        raise ContractError("pair content-hash count does not match activation rows")
    if response_hashes.shape != (len(pair_ids), 2):
        raise ContractError("response content hashes must have shape [N, 2]")
    if state_bindings.shape != (len(pair_ids), 2):
        raise ContractError("state bindings must have shape [N, 2]")
    if layer_ids != tuple(expected_layers) or states.shape[2] != len(expected_layers):
        raise ContractError("activation layers differ from frozen 1..28 convention")
    if states.shape[3] != expected_hidden_size:
        raise ContractError("activation hidden size differs from frozen model")
    if position != "response_mean":
        raise ContractError("only ordinary assistant response-mean states are permitted")
    if settings != expected_settings_sha256:
        raise ContractError("activation feature settings fingerprint changed")
    if model_id != MODEL_ID:
        raise ContractError("activation model ID changed")
    if revision != expected_model_revision:
        raise ContractError("activation model revision changed")
    if not np.issubdtype(states.dtype, np.floating) or not np.isfinite(states).all():
        raise ContractError("states must be finite floating-point values")
    for pair_index in range(len(pair_ids)):
        for response_index in range(2):
            observed_binding = state_binding_sha256(
                states[pair_index, response_index], response_hashes[pair_index, response_index])
            if observed_binding != state_bindings[pair_index, response_index]:
                raise ContractError("activation state/response binding mismatch")

    wanted = [str(row["id"]) for row in rows]
    if set(wanted) != set(pair_ids) or len(wanted) != len(pair_ids):
        missing_ids = sorted(set(wanted) - set(pair_ids))[:3]
        extra_ids = sorted(set(pair_ids) - set(wanted))[:3]
        raise ContractError(f"activation IDs do not match rows; missing={missing_ids}, extra={extra_ids}")
    index = {pair_id: i for i, pair_id in enumerate(pair_ids)}
    expected_hashes = {str(row["id"]): pair_content_sha256(row) for row in rows}
    observed_hashes = {pair_id: content_hashes[i] for i, pair_id in enumerate(pair_ids)}
    if observed_hashes != expected_hashes:
        raise ContractError("activation pair-content hashes do not match exact JSONL text")
    expected_response_hashes = {
        str(row["id"]): (
            response_content_sha256(row, "confident"),
            response_content_sha256(row, "hesitant"),
        ) for row in rows
    }
    observed_response_hashes = {
        pair_id: tuple(response_hashes[i].tolist()) for i, pair_id in enumerate(pair_ids)
    }
    if observed_response_hashes != expected_response_hashes:
        raise ContractError("activation response hashes do not match role-ordered exact text")
    ordered = states[[index[pair_id] for pair_id in wanted]]
    return ordered, {
        "path": str(path), "sha256": file_sha256(path), "pairs": len(pair_ids),
        "shape": list(ordered.shape), "dtype": str(ordered.dtype),
        "layer_ids": list(layer_ids), "position": position,
        "pair_order": list(pair_order),
        "settings_sha256": settings, "model_id": model_id, "model_revision": revision,
    }


@dataclass
class FittedReadouts:
    feature_mean: np.ndarray       # [L, D]
    feature_scale: np.ndarray      # [L, D]
    coef: np.ndarray               # [L, D], standardized-feature space
    train_score_mean: np.ndarray   # [L]
    train_score_std: np.ndarray    # [L]

    @property
    def raw_directions(self) -> np.ndarray:
        """Directions in unstandardized hidden-state coordinates."""
        return self.coef / self.feature_scale


def fit_paired_layer_readouts(
    states: np.ndarray,
    *,
    C: float = LOGISTIC_C,
    max_iter: int = LOGISTIC_MAX_ITER,
) -> FittedReadouts:
    x = np.asarray(states)
    if x.ndim != 4 or x.shape[1] != 2 or x.shape[0] < 2:
        raise ContractError("training states must be [N>=2, 2, L, D]")
    if not np.isfinite(x).all():
        raise ContractError("training states contain nonfinite values")
    n, _, layers, features = x.shape
    means = np.empty((layers, features), dtype=np.float64)
    scales = np.empty((layers, features), dtype=np.float64)
    coefs = np.empty((layers, features), dtype=np.float64)
    score_means = np.empty(layers, dtype=np.float64)
    score_stds = np.empty(layers, dtype=np.float64)
    labels = np.concatenate([np.ones(n), np.zeros(n)])
    sample_weights = np.full(2 * n, 0.5, dtype=np.float64)

    for layer in range(layers):
        response_states = np.asarray(x[:, :, layer, :], dtype=np.float64).reshape(-1, features)
        scaler = StandardScaler().fit(response_states)
        z = scaler.transform(response_states).reshape(n, 2, features)
        delta = z[:, 0, :] - z[:, 1, :]
        symmetric = np.concatenate([delta, -delta], axis=0)
        model = LogisticRegression(
            C=C, fit_intercept=False, solver="lbfgs", max_iter=max_iter,
            random_state=0,
        ).fit(symmetric, labels, sample_weight=sample_weights)
        scores = model.decision_function(z.reshape(-1, features))
        means[layer] = scaler.mean_
        scales[layer] = scaler.scale_
        coefs[layer] = model.coef_[0]
        score_means[layer] = float(scores.mean())
        score_stds[layer] = float(scores.std(ddof=0))

    return FittedReadouts(means, scales, coefs, score_means, score_stds)


def layer_scores(fitted: FittedReadouts, states: np.ndarray) -> np.ndarray:
    x = np.asarray(states, dtype=np.float64)
    if x.ndim != 4 or x.shape[1] != 2 or x.shape[2:] != fitted.coef.shape:
        raise ContractError("score-state shape does not match fitted readouts")
    z = (x - fitted.feature_mean[None, None, :, :]) / fitted.feature_scale[None, None, :, :]
    return np.einsum("npld,ld->npl", z, fitted.coef, optimize=True)


def train_standardized_scores(fitted: FittedReadouts, scores: np.ndarray) -> np.ndarray:
    values = np.asarray(scores, dtype=np.float64)
    if values.ndim != 3 or values.shape[2] != len(fitted.train_score_std):
        raise ContractError("layer score shape changed")
    output = np.zeros_like(values)
    usable = fitted.train_score_std >= 1e-12
    output[:, :, usable] = (
        values[:, :, usable] - fitted.train_score_mean[None, None, usable]
    ) / fitted.train_score_std[None, None, usable]
    return output


def equal28_scores(fitted: FittedReadouts, states: np.ndarray) -> np.ndarray:
    """Preregistered ensemble: equal mean of all 28 train-standardized scores."""
    scores = train_standardized_scores(fitted, layer_scores(fitted, states))
    if scores.shape[2] != 28:
        raise ContractError("equal28 ensemble requires exactly 28 layers")
    return scores.mean(axis=2)


def paired_credit(scores: np.ndarray) -> np.ndarray:
    scores = np.asarray(scores, dtype=np.float64)
    if scores.ndim != 2 or scores.shape[1] != 2 or not np.isfinite(scores).all():
        raise ContractError("scores must be finite [N, 2]")
    margin = scores[:, 0] - scores[:, 1]
    return (margin > 0).astype(np.float64) + 0.5 * (margin == 0)


def grouped_bootstrap_interval(
    credit: np.ndarray,
    groups: Sequence[str],
    *,
    replicates: int = BOOTSTRAP_REPLICATES,
    seed: int = BOOTSTRAP_SEED,
) -> list[float] | None:
    group_values = np.asarray([str(value) for value in groups])
    unique = np.unique(group_values)
    if len(unique) < 2 or replicates < 1:
        return None
    sums = np.asarray([credit[group_values == group].sum() for group in unique])
    counts = np.asarray([(group_values == group).sum() for group in unique])
    rng = np.random.default_rng(seed)
    draws = rng.integers(0, len(unique), size=(replicates, len(unique)))
    values = sums[draws].sum(axis=1) / counts[draws].sum(axis=1)
    return [float(value) for value in np.quantile(values, [0.025, 0.975])]


def score_metrics(
    scores: np.ndarray,
    rows: Sequence[Mapping[str, Any]],
    *,
    bootstrap_replicates: int = BOOTSTRAP_REPLICATES,
    bootstrap_seed: int = BOOTSTRAP_SEED,
) -> dict[str, Any]:
    values = np.asarray(scores, dtype=np.float64)
    if len(values) != len(rows):
        raise ContractError("score count differs from row count")
    credit = paired_credit(values)
    margin = values[:, 0] - values[:, 1]
    wins = int(np.count_nonzero(margin > 0))
    ties = int(np.count_nonzero(margin == 0))
    losses = int(np.count_nonzero(margin < 0))
    labels = np.tile(np.asarray([1, 0]), len(values))
    auc = float(roc_auc_score(labels, values.reshape(-1)))
    groups = [str(row["group_id"]) for row in rows]
    provider_groups: list[str] | None = None
    if all(isinstance(row.get("atomic_group_id"), str)
           and str(row["atomic_group_id"]).strip() for row in rows):
        provider_groups = [str(row["atomic_group_id"]) for row in rows]
    return {
        "pairs": len(values), "wins": wins, "ties": ties, "losses": losses,
        "paired_accuracy": float(credit.mean()),
        "answer_level_roc_auc": auc,
        "mean_paired_margin": float(margin.mean()),
        "median_paired_margin": float(np.median(margin)),
        "group_count": len(set(groups)),
        "grouped_bootstrap_95_ci": grouped_bootstrap_interval(
            credit, groups, replicates=bootstrap_replicates, seed=bootstrap_seed),
        "grouped_bootstrap_scope": (
            "conditional_on_item_or_source_lineage_groups; not provider-batch uncertainty"
        ),
        "provider_batch_group_count": len(set(provider_groups)) if provider_groups else None,
        "provider_batch_bootstrap_95_ci_descriptive": (
            grouped_bootstrap_interval(
                credit, provider_groups, replicates=bootstrap_replicates,
                seed=bootstrap_seed + 10000)
            if provider_groups is not None else None
        ),
        "provider_batch_bootstrap_scope": (
            "descriptive_sensitivity_by_frozen_atomic_generation_group; "
            "few_batches_and_not_an_independent_generator"
        ),
    }


def _stratum_metrics(
    scores: np.ndarray,
    rows: Sequence[Mapping[str, Any]],
    key: str,
) -> dict[str, Any]:
    values = sorted({str(row[key]) for row in rows if row.get(key) not in (None, "")})
    result: dict[str, Any] = {}
    for value in values:
        indices = [i for i, row in enumerate(rows) if str(row.get(key)) == value]
        result[value] = score_metrics(scores[indices], [rows[i] for i in indices],
                                      bootstrap_replicates=0)
    return result


def evaluate_fitted(
    fitted: FittedReadouts,
    split_states: Mapping[str, np.ndarray],
    split_rows: Mapping[str, Sequence[Mapping[str, Any]]],
    *,
    bootstrap_replicates: int = BOOTSTRAP_REPLICATES,
) -> dict[str, Any]:
    output: dict[str, Any] = {"layerwise": {}, "ensemble": {}, "primary_layer": {}}
    primary_index = PRIMARY_LAYER_ID - 1
    for split in SPLIT_ORDER:
        raw = layer_scores(fitted, split_states[split])
        output["layerwise"][split] = {
            str(layer_id): score_metrics(
                raw[:, :, layer_id - 1], split_rows[split],
                bootstrap_replicates=bootstrap_replicates,
                bootstrap_seed=BOOTSTRAP_SEED + layer_id,
            )
            for layer_id in EXPECTED_LAYER_IDS
        }
        primary = raw[:, :, primary_index]
        ensemble = train_standardized_scores(fitted, raw).mean(axis=2)
        output["primary_layer"][split] = score_metrics(
            primary, split_rows[split], bootstrap_replicates=bootstrap_replicates)
        output["ensemble"][split] = score_metrics(
            ensemble, split_rows[split], bootstrap_replicates=bootstrap_replicates)
        if split != "train":
            output["primary_layer"][split]["strata"] = {
                key: _stratum_metrics(primary, split_rows[split], key)
                for key in ("task", "length_bin", "target_longer_role", "source_collection")
            }
            output["ensemble"][split]["strata"] = {
                key: _stratum_metrics(ensemble, split_rows[split], key)
                for key in ("task", "length_bin", "target_longer_role", "source_collection")
            }
    return output


def cosine_similarity(left: np.ndarray, right: np.ndarray) -> float | None:
    denominator = float(np.linalg.norm(left) * np.linalg.norm(right))
    if denominator < 1e-15:
        return None
    return float(np.dot(left, right) / denominator)


def direction_stability(fits: Mapping[int, FittedReadouts]) -> dict[str, Any]:
    sizes = sorted(fits)
    comparisons: dict[str, Any] = {}
    for left, right in zip(sizes, sizes[1:]):
        cosines = [
            cosine_similarity(fits[left].raw_directions[layer], fits[right].raw_directions[layer])
            for layer in range(len(EXPECTED_LAYER_IDS))
        ]
        finite = [value for value in cosines if value is not None]
        comparisons[f"{left}_vs_{right}"] = {
            "per_layer": {str(layer_id): value for layer_id, value in zip(EXPECTED_LAYER_IDS, cosines)},
            "mean": float(np.mean(finite)) if finite else None,
            "median": float(np.median(finite)) if finite else None,
            "minimum": float(np.min(finite)) if finite else None,
            "zero_direction_layers": int(len(cosines) - len(finite)),
        }
    if len(sizes) > 2:
        left, right = sizes[0], sizes[-1]
        cosines = [
            cosine_similarity(fits[left].raw_directions[layer], fits[right].raw_directions[layer])
            for layer in range(len(EXPECTED_LAYER_IDS))
        ]
        finite = [value for value in cosines if value is not None]
        comparisons[f"{left}_vs_{right}"] = {
            "per_layer": {str(layer_id): value for layer_id, value in zip(EXPECTED_LAYER_IDS, cosines)},
            "mean": float(np.mean(finite)) if finite else None,
            "median": float(np.median(finite)) if finite else None,
            "minimum": float(np.min(finite)) if finite else None,
            "zero_direction_layers": int(len(cosines) - len(finite)),
        }
    return comparisons


def save_fit(path: Path, fitted: FittedReadouts, train_size: int) -> dict[str, Any]:
    if path.exists():
        raise FileExistsError(f"refusing to overwrite fit: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp.npz")
    np.savez_compressed(
        temporary,
        feature_mean=fitted.feature_mean,
        feature_scale=fitted.feature_scale,
        coef=fitted.coef,
        train_score_mean=fitted.train_score_mean,
        train_score_std=fitted.train_score_std,
        raw_direction=fitted.raw_directions,
        train_size=np.asarray(train_size, dtype=np.int64),
        layer_ids=np.asarray(EXPECTED_LAYER_IDS, dtype=np.int64),
        C=np.asarray(LOGISTIC_C, dtype=np.float64),
        max_iter=np.asarray(LOGISTIC_MAX_ITER, dtype=np.int64),
        primary_layer_id=np.asarray(PRIMARY_LAYER_ID, dtype=np.int64),
        ensemble_name=np.asarray(ENSEMBLE_NAME),
    )
    os.replace(temporary, path)
    return {"path": str(path), "sha256": file_sha256(path), "bytes": path.stat().st_size}


def run_learning_curve(
    split_rows: Mapping[str, Sequence[Mapping[str, Any]]],
    split_states: Mapping[str, np.ndarray],
    *,
    train_sizes: Sequence[int] = (200, 500, 920),
    bootstrap_replicates: int = BOOTSTRAP_REPLICATES,
    output_dir: Path | None = None,
) -> dict[str, Any]:
    validate_split_rows(split_rows, expected_counts=None, train_sizes=train_sizes)
    for split in SPLIT_ORDER:
        states = np.asarray(split_states[split])
        if states.shape[0] != len(split_rows[split]) or states.shape[1] != 2:
            raise ContractError(f"{split} activation/row count mismatch")
        if states.shape[2] != 28:
            raise ContractError(f"{split} does not contain all 28 layers")
    fits: dict[int, FittedReadouts] = {}
    curves: dict[str, Any] = {}
    artifacts: dict[str, Any] = {}
    for size in train_sizes:
        fitted = fit_paired_layer_readouts(split_states["train"][:size])
        fits[int(size)] = fitted
        states_for_size = dict(split_states)
        rows_for_size = dict(split_rows)
        states_for_size["train"] = split_states["train"][:size]
        rows_for_size["train"] = split_rows["train"][:size]
        curves[str(size)] = evaluate_fitted(
            fitted, states_for_size, rows_for_size,
            bootstrap_replicates=bootstrap_replicates,
        )
        if output_dir is not None:
            artifacts[str(size)] = save_fit(
                output_dir / f"paired_probe_size_{size}.npz", fitted, int(size))
    return {
        "learning_curves": curves,
        "direction_stability": direction_stability(fits),
        "fit_artifacts": artifacts,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split-freeze", required=True, type=Path)
    for split in SPLIT_ORDER:
        option = split.replace("_", "-")
        parser.add_argument(f"--{option}-data", required=True, type=Path)
        parser.add_argument(f"--{option}-activations", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--validate-only", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    data_paths = {
        split: getattr(args, f"{split}_data") for split in SPLIT_ORDER
    }
    activation_paths = {
        split: getattr(args, f"{split}_activations") for split in SPLIT_ORDER
    }
    split_rows = {split: load_jsonl(data_paths[split], split) for split in SPLIT_ORDER}
    expected_counts, train_sizes, freeze_audit = load_split_freeze(args.split_freeze, data_paths)
    split_audit = validate_split_rows(
        split_rows, expected_counts=expected_counts, train_sizes=train_sizes,
        expected_prefix_hashes=freeze_audit["nested_train_id_sha256"],
    )
    split_states: dict[str, np.ndarray] = {}
    bundle_audit: dict[str, Any] = {}
    for split in SPLIT_ORDER:
        split_states[split], bundle_audit[split] = load_activation_bundle(
            activation_paths[split], split_rows[split])

    common = {
        "schema": "confidence-probe-scaleup-learning-curve-v1",
        "status": "validated_only" if args.validate_only else "complete",
        "model": {
            "id": MODEL_ID, "revision": MODEL_REVISION,
            "feature_settings_sha256": FEATURE_SETTINGS_SHA256,
            "layers": list(EXPECTED_LAYER_IDS), "hidden_size": EXPECTED_HIDDEN_SIZE,
            "pooling": "mean ordinary assistant-response tokens excluding prompt and im_end",
        },
        "fit": {
            "train_sizes": list(train_sizes),
            "pair_order": ["confident", "hesitant"],
            "feature_scaler": "StandardScaler_fit_on_both_training_responses_only",
            "classifier": "symmetric_paired_LogisticRegression",
            "C": LOGISTIC_C, "fit_intercept": False,
            "max_iter": LOGISTIC_MAX_ITER, "solver": "lbfgs",
            "sample_weight_per_symmetric_row": 0.5,
            "primary_layer_id": PRIMARY_LAYER_ID,
            "primary_multilayer_ensemble": ENSEMBLE_NAME,
            "ensemble_layers": list(ENSEMBLE_LAYER_IDS),
            "selection_on_dev_or_test": False,
        },
        "bootstrap": {"unit": "group_id", "replicates": BOOTSTRAP_REPLICATES,
                      "seed": BOOTSTRAP_SEED},
        "input_files": {
            split: {"data": str(data_paths[split]), "data_sha256": file_sha256(data_paths[split]),
                    "activations": bundle_audit[split]}
            for split in SPLIT_ORDER
        },
        "split_audit": split_audit,
        "split_freeze": freeze_audit,
        "runtime": {
            "python": os.sys.version.split()[0], "numpy": np.__version__,
            "scikit_learn": sklearn.__version__,
        },
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    if args.validate_only:
        atomic_write_json(args.output_dir / "VALIDATION_ONLY.json", common)
        return 0
    result = run_learning_curve(
        split_rows, split_states, train_sizes=train_sizes, output_dir=args.output_dir)
    common.update(result)
    atomic_write_json(args.output_dir / "PROBE_LEARNING_CURVE_RESULTS.json", common)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
