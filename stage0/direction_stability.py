"""Cached-only probe-direction stability and leakage-safe stacking audit.

This module deliberately avoids importing the generation pipeline.  It reads the
already-saved 500-example artifacts, restricts every analysis to the locked
train+validation development pool, and leaves the original test indices unused.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import time
from collections import Counter
from pathlib import Path
from typing import Any, Callable

import matplotlib
import numpy as np
import yaml
from scipy.stats import spearmanr
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, roc_auc_score
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import StandardScaler


matplotlib.use("Agg")
from matplotlib import pyplot as plt  # noqa: E402


def _root_dir() -> Path:
    return Path(__file__).resolve().parents[1]


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")
    os.replace(temporary, path)


def _atomic_npz(path: Path, arrays: dict[str, np.ndarray]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp.npz")
    np.savez_compressed(temporary, **arrays)
    os.replace(temporary, path)


def _resolve(root: Path, value: str | Path) -> Path:
    path = Path(value).expanduser()
    return (root / path).resolve() if not path.is_absolute() else path.resolve()


def _shareable_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(_root_dir()))
    except ValueError:
        return str(path.resolve())


def _normalized_context(value: str) -> str:
    return " ".join(value.lower().split())


def _context_group(value: str) -> str:
    return hashlib.sha256(_normalized_context(value).encode("utf-8")).hexdigest()


def _summary(values: list[float] | np.ndarray) -> dict[str, Any]:
    array = np.asarray(values, dtype=np.float64)
    array = array[np.isfinite(array)]
    if not len(array):
        return {"count": 0, "values": []}
    return {
        "count": int(len(array)),
        "mean": float(array.mean()),
        "median": float(np.median(array)),
        "minimum": float(array.min()),
        "maximum": float(array.max()),
        "empirical_2.5": float(np.percentile(array, 2.5)),
        "empirical_97.5": float(np.percentile(array, 97.5)),
        "fraction_positive": float(np.mean(array > 0)),
        "fraction_at_least_0.5": float(np.mean(array >= 0.5)),
        "values": array.tolist(),
    }


def _validate_binary(labels: np.ndarray, where: str) -> None:
    if np.unique(labels).size != 2:
        raise ValueError(f"{where} has only one label class")


def _pipeline(c_value: float, seed: int, max_iter: int = 3000) -> Pipeline:
    return make_pipeline(
        StandardScaler(),
        LogisticRegression(C=float(c_value), max_iter=max_iter, random_state=int(seed)),
    )


def _splitter(n_splits: int, seed: int) -> StratifiedGroupKFold:
    return StratifiedGroupKFold(n_splits=int(n_splits), shuffle=True, random_state=int(seed))


def _check_group_disjoint(groups: np.ndarray, train: np.ndarray, test: np.ndarray) -> None:
    overlap = set(groups[train].tolist()) & set(groups[test].tolist())
    if overlap:
        raise RuntimeError(f"Grouped split leaked {len(overlap)} context groups")


def load_cached_audit_data(config_path: str | Path) -> dict[str, Any]:
    """Load and validate only the cached inputs declared by the frozen config."""

    root = _root_dir()
    path = _resolve(root, config_path)
    with path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    artifact_paths: dict[str, Path] = {}
    artifact_hashes: dict[str, str] = {}
    for name, specification in config["source_artifacts"].items():
        artifact = _resolve(root, specification["path"])
        if not artifact.exists():
            raise FileNotFoundError(f"Missing cached source artifact: {artifact}")
        observed = _sha256(artifact)
        expected = str(specification["sha256"])
        if observed != expected:
            raise ValueError(f"Cached source hash mismatch for {name}: {observed} != {expected}")
        artifact_paths[name] = artifact
        artifact_hashes[name] = observed

    records = _read_jsonl(artifact_paths["generations"])
    semantic_rows = _read_jsonl(artifact_paths["semantic_entropy"])
    with artifact_paths["probe_metrics"].open("r", encoding="utf-8") as handle:
        source_probe = json.load(handle)
    with np.load(artifact_paths["hidden_states"]) as archive:
        hidden = archive["hidden_states"].astype(np.float32)
        cached_layers = [int(value) for value in archive["layers"].tolist()]
        hidden_ids = archive["example_ids"].astype(str).tolist()

    row_count = len(records)
    record_ids = [str(record["id"]) for record in records]
    semantic_ids = [str(row["id"]) for row in semantic_rows]
    if not (row_count == len(semantic_rows) == hidden.shape[0]):
        raise ValueError("Cached artifact row counts disagree")
    if record_ids != semantic_ids or record_ids != hidden_ids:
        raise ValueError("Cached artifact example IDs or order disagree")
    if hidden.ndim != 3:
        raise ValueError(f"Expected [example, layer, hidden] cache, got {hidden.shape}")
    if hidden.shape[1] != len(cached_layers) or not np.all(np.isfinite(hidden)):
        raise ValueError("Hidden-state cache has an invalid layer axis or non-finite values")

    locked = config["locked_data"]
    development_parts = [str(value) for value in locked["development_parts"]]
    development = np.asarray(
        [index for field in development_parts for index in source_probe[field]], dtype=np.int64
    )
    reserved = np.asarray(source_probe[str(locked["reserved_part"])], dtype=np.int64)
    if len(development) != int(locked["expected_development_size"]):
        raise ValueError("Locked development size changed")
    if len(reserved) != int(locked["expected_reserved_size"]):
        raise ValueError("Locked reserved size changed")
    if len(np.unique(development)) != len(development) or len(np.unique(reserved)) != len(reserved):
        raise ValueError("Locked split contains duplicate row indices")
    if np.intersect1d(development, reserved).size:
        raise ValueError("Locked development and reserved indices overlap")
    if set(development.tolist()) | set(reserved.tolist()) != set(range(row_count)):
        raise ValueError("Locked split does not partition all cached rows")

    all_groups = np.asarray([_context_group(record["context"]) for record in records])
    group_overlap = set(all_groups[development].tolist()) & set(all_groups[reserved].tolist())
    if group_overlap:
        raise ValueError("Locked development and reserved sets share normalized contexts")

    threshold_field = str(locked["threshold_source_field"])
    threshold = float(source_probe[threshold_field])
    if not math.isclose(threshold, float(locked["expected_threshold"]), rel_tol=0, abs_tol=1e-12):
        raise ValueError("Frozen semantic-entropy threshold changed")
    all_entropy = np.asarray(
        [row["cluster_assignment_entropy"] for row in semantic_rows], dtype=np.float64
    )
    all_nll = np.asarray(
        [row["answer_negative_log_likelihood"] for row in semantic_rows], dtype=np.float64
    )
    if not np.all(np.isfinite(all_entropy)) or not np.all(np.isfinite(all_nll)):
        raise ValueError("Semantic entropy or answer NLL contains non-finite values")
    labels = (all_entropy >= threshold).astype(np.int64)
    _validate_binary(labels[development], "locked development pool")

    layer_block = config["analysis"].get("layers", {})
    primary_layer = int(layer_block.get("primary", config["analysis"]["primary_layer"]))
    challenger_layer = int(
        layer_block.get("challenger", config["analysis"]["challenger_layer"])
    )
    for layer in (primary_layer, challenger_layer):
        if layer not in cached_layers:
            raise ValueError(f"Requested layer {layer} is absent from cache {cached_layers}")
    layer_features = {
        layer: hidden[development, cached_layers.index(layer), :].copy()
        for layer in (primary_layer, challenger_layer)
    }

    return {
        "config": config,
        "config_path": str(path),
        "source_artifact_sha256": artifact_hashes,
        "row_count": row_count,
        "cached_layers": cached_layers,
        "hidden_width": int(hidden.shape[2]),
        "primary_layer": primary_layer,
        "challenger_layer": challenger_layer,
        "development_original_indices": development,
        "reserved_original_indices": reserved,
        "development_example_ids": np.asarray(record_ids)[development],
        "features": layer_features,
        "labels": labels[development],
        "entropy": all_entropy[development],
        "answer_nll": all_nll[development],
        "groups": all_groups[development],
        "frozen_threshold": threshold,
        "split_validation": {
            "development_size": int(len(development)),
            "reserved_size": int(len(reserved)),
            "development_reserved_index_overlap": 0,
            "development_reserved_context_overlap": 0,
            "development_label_counts": {
                str(key): int(value)
                for key, value in Counter(labels[development].tolist()).items()
            },
            "development_unique_contexts": int(len(np.unique(all_groups[development]))),
            "reserved_unique_contexts": int(len(np.unique(all_groups[reserved]))),
            "reserved_access_policy": "indices and group hashes validated; features and outcomes not returned",
        },
    }


def select_c_one_se(
    features: np.ndarray,
    labels: np.ndarray,
    groups: np.ndarray,
    c_grid: list[float] | np.ndarray,
    n_splits: int,
    seed: int,
    max_iter: int = 3000,
) -> dict[str, Any]:
    """Select the strongest regularization within one SE of the best inner AUROC."""

    labels = np.asarray(labels, dtype=np.int64)
    groups = np.asarray(groups)
    _validate_binary(labels, "C-selection input")
    splits = list(_splitter(n_splits, seed).split(features, labels, groups))
    rows = []
    for c_value in sorted(float(value) for value in c_grid):
        scores = []
        for fold, (train, validation) in enumerate(splits):
            _check_group_disjoint(groups, train, validation)
            _validate_binary(labels[train], f"C-selection train fold {fold}")
            _validate_binary(labels[validation], f"C-selection validation fold {fold}")
            model = _pipeline(c_value, seed + fold, max_iter)
            model.fit(features[train], labels[train])
            probabilities = model.predict_proba(features[validation])[:, 1]
            scores.append(float(roc_auc_score(labels[validation], probabilities)))
        array = np.asarray(scores, dtype=np.float64)
        rows.append(
            {
                "c": c_value,
                "mean_auroc": float(array.mean()),
                "standard_error": float(array.std(ddof=1) / math.sqrt(len(array)))
                if len(array) > 1
                else 0.0,
                "fold_aurocs": array.tolist(),
            }
        )
    best = max(rows, key=lambda row: row["mean_auroc"])
    cutoff = float(best["mean_auroc"] - best["standard_error"])
    eligible = [row for row in rows if row["mean_auroc"] >= cutoff - 1e-12]
    selected = min(eligible, key=lambda row: row["c"])
    return {
        "selected_c": float(selected["c"]),
        "best_mean_c": float(best["c"]),
        "best_mean_auroc": float(best["mean_auroc"]),
        "one_se_cutoff": cutoff,
        "selection_rule": "smallest C with mean AUROC within one SE of best mean",
        "c_results": rows,
    }


def raw_logistic_direction(
    model: Pipeline,
    verification_features: np.ndarray | None = None,
) -> dict[str, Any]:
    """Convert a standardized logistic model into raw hidden-state coordinates."""

    scaler: StandardScaler = model.named_steps["standardscaler"]
    logistic: LogisticRegression = model.named_steps["logisticregression"]
    coefficient = logistic.coef_[0].astype(np.float64)
    scale = scaler.scale_.astype(np.float64)
    mean = scaler.mean_.astype(np.float64)
    raw_weight = coefficient / scale
    raw_intercept = float(logistic.intercept_[0] - np.dot(coefficient, mean / scale))
    norm = float(np.linalg.norm(raw_weight))
    if not np.isfinite(norm) or norm == 0:
        raise ValueError("Logistic probe has a zero or non-finite raw direction")
    maximum_error = None
    if verification_features is not None:
        direct = np.asarray(verification_features, dtype=np.float64) @ raw_weight + raw_intercept
        pipeline_scores = model.decision_function(verification_features)
        maximum_error = float(np.max(np.abs(direct - pipeline_scores)))
        if maximum_error > 1e-5:
            raise RuntimeError(f"Raw-direction reconstruction error is {maximum_error}")
    return {
        "raw_weight": raw_weight,
        "raw_intercept": raw_intercept,
        "unit_direction": raw_weight / norm,
        "raw_norm": norm,
        "maximum_decision_reconstruction_error": maximum_error,
    }


def _safe_spearman(first: np.ndarray, second: np.ndarray) -> float:
    value = float(spearmanr(first, second).statistic)
    return value if np.isfinite(value) else 0.0


def _metric_value(labels: np.ndarray, probabilities: np.ndarray, metric: str) -> float:
    probabilities = np.clip(np.asarray(probabilities, dtype=np.float64), 1e-7, 1 - 1e-7)
    if metric == "auroc":
        _validate_binary(labels, "AUROC resample")
        return float(roc_auc_score(labels, probabilities))
    if metric == "log_loss":
        return float(log_loss(labels, probabilities, labels=[0, 1]))
    raise ValueError(f"Unknown metric {metric}")


def grouped_bootstrap_interval(
    labels: np.ndarray,
    probabilities: np.ndarray,
    groups: np.ndarray,
    samples: int,
    seed: int,
    metric: str = "auroc",
    reference_probabilities: np.ndarray | None = None,
) -> dict[str, Any]:
    """Context-grouped bootstrap for one metric or first-minus-reference."""

    labels = np.asarray(labels, dtype=np.int64)
    probabilities = np.asarray(probabilities, dtype=np.float64)
    groups = np.asarray(groups)
    reference = (
        None
        if reference_probabilities is None
        else np.asarray(reference_probabilities, dtype=np.float64)
    )

    def statistic(indices: np.ndarray) -> float:
        first = _metric_value(labels[indices], probabilities[indices], metric)
        if reference is None:
            return first
        return first - _metric_value(labels[indices], reference[indices], metric)

    full = np.arange(len(labels), dtype=np.int64)
    estimate = statistic(full)
    unique_groups = np.unique(groups)
    group_indices = {group: np.flatnonzero(groups == group) for group in unique_groups}
    rng = np.random.default_rng(seed)
    values = []
    for _ in range(int(samples)):
        sampled = rng.choice(unique_groups, size=len(unique_groups), replace=True)
        indices = np.concatenate([group_indices[group] for group in sampled])
        if metric == "auroc" and np.unique(labels[indices]).size < 2:
            continue
        values.append(statistic(indices))
    if not values:
        raise RuntimeError("No valid grouped bootstrap resamples")
    array = np.asarray(values, dtype=np.float64)
    return {
        "estimate": float(estimate),
        "lower_95": float(np.percentile(array, 2.5)),
        "median": float(np.median(array)),
        "upper_95": float(np.percentile(array, 97.5)),
        "valid_resamples": int(len(array)),
        "resampling_unit": "normalized context",
    }


def _pairwise_cosines(directions: list[np.ndarray]) -> list[float]:
    return [
        float(np.dot(directions[left], directions[right]))
        for left in range(len(directions))
        for right in range(left + 1, len(directions))
    ]


def run_repeated_nested_cv(
    features: np.ndarray,
    labels: np.ndarray,
    groups: np.ndarray,
    entropy: np.ndarray,
    c_grid: list[float],
    outer_folds: int,
    outer_repeats: int,
    inner_folds: int,
    seed: int,
    bootstrap_samples: int,
    bootstrap_seed: int,
) -> dict[str, Any]:
    """Repeated nested grouped CV with a prediction for every row per repeat."""

    size = len(labels)
    probability_sum = np.zeros(size, dtype=np.float64)
    score_sum = np.zeros(size, dtype=np.float64)
    prediction_counts = np.zeros(size, dtype=np.int64)
    fold_rows = []
    directions: list[np.ndarray] = []
    maximum_reconstruction_error = 0.0
    for repetition in range(int(outer_repeats)):
        outer_seed = int(seed + repetition * 1000)
        splits = list(_splitter(outer_folds, outer_seed).split(features, labels, groups))
        repetition_hits = np.zeros(size, dtype=np.int64)
        for fold, (train, test) in enumerate(splits):
            _check_group_disjoint(groups, train, test)
            tuning = select_c_one_se(
                features[train],
                labels[train],
                groups[train],
                c_grid,
                inner_folds,
                outer_seed + 100 + fold,
            )
            model = _pipeline(tuning["selected_c"], outer_seed + fold)
            model.fit(features[train], labels[train])
            probability_sum[test] += model.predict_proba(features[test])[:, 1]
            score_sum[test] += model.decision_function(features[test])
            prediction_counts[test] += 1
            repetition_hits[test] += 1
            direction = raw_logistic_direction(model, features[test])
            maximum_reconstruction_error = max(
                maximum_reconstruction_error,
                float(direction["maximum_decision_reconstruction_error"] or 0.0),
            )
            directions.append(direction["unit_direction"])
            fold_rows.append(
                {
                    "repetition": repetition,
                    "fold": fold,
                    "train_size": int(len(train)),
                    "heldout_size": int(len(test)),
                    "train_unique_contexts": int(len(np.unique(groups[train]))),
                    "heldout_unique_contexts": int(len(np.unique(groups[test]))),
                    "context_overlap": 0,
                    "selected_c": float(tuning["selected_c"]),
                    "inner_selection": tuning,
                    "heldout_auroc": float(
                        roc_auc_score(labels[test], model.predict_proba(features[test])[:, 1])
                    ),
                }
            )
        if not np.all(repetition_hits == 1):
            raise RuntimeError("An outer repetition did not score every development row once")
    if not np.all(prediction_counts == int(outer_repeats)):
        raise RuntimeError("Repeated OOF prediction ledger is incomplete")
    probabilities = probability_sum / prediction_counts
    scores = score_sum / prediction_counts
    auc = float(roc_auc_score(labels, probabilities))
    bootstrap = grouped_bootstrap_interval(
        labels,
        probabilities,
        groups,
        bootstrap_samples,
        bootstrap_seed,
        metric="auroc",
    )
    return {
        "oof_auroc": auc,
        "oof_auroc_context_bootstrap_95": bootstrap,
        "continuous_entropy_spearman": _safe_spearman(entropy, scores),
        "outer_repeats": int(outer_repeats),
        "outer_folds": int(outer_folds),
        "prediction_count_min": int(prediction_counts.min()),
        "prediction_count_max": int(prediction_counts.max()),
        "selected_c_frequency": {
            str(key): int(value)
            for key, value in sorted(Counter(row["selected_c"] for row in fold_rows).items())
        },
        "overlapping_outer_direction_cosines_sensitivity_only": _summary(
            _pairwise_cosines(directions)
        ),
        "maximum_raw_decision_reconstruction_error": float(maximum_reconstruction_error),
        "oof_probabilities": probabilities.tolist(),
        "oof_decision_scores": scores.tolist(),
        "folds": fold_rows,
    }


def _fit_direction(
    features: np.ndarray,
    labels: np.ndarray,
    indices: np.ndarray,
    c_value: float,
    seed: int,
) -> tuple[Pipeline, dict[str, Any]]:
    _validate_binary(labels[indices], "direction fit")
    model = _pipeline(c_value, seed)
    model.fit(features[indices], labels[indices])
    return model, raw_logistic_direction(model, features[indices[: min(32, len(indices))]])


def run_split_half_stability(
    features: np.ndarray,
    labels: np.ndarray,
    groups: np.ndarray,
    c_grid: list[float],
    inner_folds: int,
    repetitions: int,
    shuffle_repetitions: int,
    seed: int,
    shuffle_seed: int,
    folds_per_repetition: int = 5,
    train_a_folds: tuple[int, ...] | list[int] = (0, 1),
    train_b_folds: tuple[int, ...] | list[int] = (2, 3),
    common_evaluation_fold: int = 4,
) -> dict[str, Any]:
    """Compare independently trained directions on disjoint context-group halves."""

    requested_folds = [
        *[int(value) for value in train_a_folds],
        *[int(value) for value in train_b_folds],
        int(common_evaluation_fold),
    ]
    if sorted(requested_folds) != list(range(int(folds_per_repetition))):
        raise ValueError("Split-half fold assignments must partition every configured fold once")
    rows = []
    split_cache = []
    for repetition in range(int(repetitions)):
        split_seed = seed + repetition * 1000
        heldout_folds = [
            test
            for _, test in _splitter(folds_per_repetition, split_seed).split(
                features, labels, groups
            )
        ]
        first = np.concatenate([heldout_folds[index] for index in train_a_folds])
        second = np.concatenate([heldout_folds[index] for index in train_b_folds])
        evaluation = heldout_folds[int(common_evaluation_fold)]
        if (
            set(groups[first]) & set(groups[second])
            or set(groups[first]) & set(groups[evaluation])
            or set(groups[second]) & set(groups[evaluation])
        ):
            raise RuntimeError("Split-half stability sets share a context")
        first_tuning = select_c_one_se(
            features[first], labels[first], groups[first], c_grid, inner_folds, split_seed + 101
        )
        second_tuning = select_c_one_se(
            features[second], labels[second], groups[second], c_grid, inner_folds, split_seed + 202
        )
        first_model, first_direction = _fit_direction(
            features, labels, first, first_tuning["selected_c"], split_seed + 1
        )
        second_model, second_direction = _fit_direction(
            features, labels, second, second_tuning["selected_c"], split_seed + 2
        )
        first_scores = first_model.decision_function(features[evaluation])
        second_scores = second_model.decision_function(features[evaluation])
        rows.append(
            {
                "repetition": repetition,
                "first_train_size": int(len(first)),
                "second_train_size": int(len(second)),
                "common_evaluation_size": int(len(evaluation)),
                "pairwise_context_overlap": 0,
                "first_selected_c": float(first_tuning["selected_c"]),
                "second_selected_c": float(second_tuning["selected_c"]),
                "raw_direction_cosine": float(
                    np.dot(first_direction["unit_direction"], second_direction["unit_direction"])
                ),
                "common_evaluation_score_spearman": _safe_spearman(first_scores, second_scores),
                "first_common_evaluation_auroc": float(
                    roc_auc_score(labels[evaluation], first_model.predict_proba(features[evaluation])[:, 1])
                ),
                "second_common_evaluation_auroc": float(
                    roc_auc_score(labels[evaluation], second_model.predict_proba(features[evaluation])[:, 1])
                ),
            }
        )
        split_cache.append((first, second, evaluation, first_tuning, second_tuning))

    shuffled_median_cosines = []
    shuffled_pair_cosines = []
    rng = np.random.default_rng(shuffle_seed)
    attempts = 0
    while len(shuffled_median_cosines) < int(shuffle_repetitions):
        shuffle = len(shuffled_median_cosines)
        attempts += 1
        if attempts > int(shuffle_repetitions) * 10:
            raise RuntimeError("Could not construct all valid shuffled-label null repetitions")
        shuffled_labels = rng.permutation(labels)
        permutation_cosines = []
        valid = True
        for split_index, (first, second, _, first_tuning, second_tuning) in enumerate(
            split_cache
        ):
            if (
                np.unique(shuffled_labels[first]).size < 2
                or np.unique(shuffled_labels[second]).size < 2
            ):
                valid = False
                break
            first_model, first_direction = _fit_direction(
                features,
                shuffled_labels,
                first,
                first_tuning["selected_c"],
                shuffle_seed + shuffle * 1000 + split_index * 2,
            )
            second_model, second_direction = _fit_direction(
                features,
                shuffled_labels,
                second,
                second_tuning["selected_c"],
                shuffle_seed + shuffle * 1000 + split_index * 2 + 1,
            )
            permutation_cosines.append(
                float(
                    np.dot(
                        first_direction["unit_direction"],
                        second_direction["unit_direction"],
                    )
                )
            )
        if not valid:
            continue
        shuffled_pair_cosines.extend(permutation_cosines)
        shuffled_median_cosines.append(float(np.median(permutation_cosines)))

    cosine_summary = _summary([row["raw_direction_cosine"] for row in rows])
    score_summary = _summary([row["common_evaluation_score_spearman"] for row in rows])
    null_summary = _summary(shuffled_median_cosines)
    empirical_p = (
        1
        + sum(value >= cosine_summary["median"] for value in shuffled_median_cosines)
    ) / (len(shuffled_median_cosines) + 1)
    return {
        "method": "disjoint 40%/40% context-group training sets with a common 20% holdout",
        "repetitions": int(repetitions),
        "raw_direction_cosine": cosine_summary,
        "common_evaluation_score_spearman": score_summary,
        "first_common_evaluation_auroc": _summary(
            [row["first_common_evaluation_auroc"] for row in rows]
        ),
        "second_common_evaluation_auroc": _summary(
            [row["second_common_evaluation_auroc"] for row in rows]
        ),
        "shuffled_control": {
            "repetitions": int(len(shuffled_median_cosines)),
            "raw_direction_cosine": null_summary,
            "pair_level_raw_direction_cosine": _summary(shuffled_pair_cosines),
            "empirical_p_for_real_median_cosine": float(empirical_p),
            "permutation": "one global sample-label permutation shared by both disjoint fits",
            "null_statistic": "median raw-direction cosine across every real split pattern",
            "c_policy": "reuse the corresponding real split's selected C",
        },
        "splits": rows,
    }


def run_adjacent_c_robustness(
    features: np.ndarray,
    labels: np.ndarray,
    groups: np.ndarray,
    c_grid: list[float],
    inner_folds: int,
    seed: int,
) -> dict[str, Any]:
    tuning = select_c_one_se(features, labels, groups, c_grid, inner_folds, seed)
    ordered = sorted(float(value) for value in c_grid)
    selected = float(tuning["selected_c"])
    position = ordered.index(selected)
    comparison_cs = ordered[max(0, position - 1) : min(len(ordered), position + 2)]
    models = {}
    directions = {}
    direction_details = {}
    for offset, c_value in enumerate(comparison_cs):
        model, direction = _fit_direction(
            features, labels, np.arange(len(labels)), c_value, seed + offset + 1
        )
        models[c_value] = model
        directions[c_value] = direction["unit_direction"]
        direction_details[c_value] = direction
    selected_direction = directions[selected]
    cosine_by_c = {
        str(c_value): float(np.dot(selected_direction, directions[c_value]))
        for c_value in comparison_cs
    }
    neighbor_values = [value for c_value, value in cosine_by_c.items() if float(c_value) != selected]
    selected_model = models[selected]
    selected_scaler: StandardScaler = selected_model.named_steps["standardscaler"]
    selected_logistic: LogisticRegression = selected_model.named_steps["logisticregression"]
    return {
        "selected_c": selected,
        "selection": tuning,
        "compared_c_values": comparison_cs,
        "cosine_with_selected_direction": cosine_by_c,
        "minimum_adjacent_c_cosine": float(min(neighbor_values)) if neighbor_values else 1.0,
        "_frozen_probe_arrays": {
            "selected_c": np.asarray(selected, dtype=np.float64),
            "raw_weight": direction_details[selected]["raw_weight"].astype(np.float64),
            "unit_raw_direction": direction_details[selected]["unit_direction"].astype(
                np.float64
            ),
            "raw_intercept": np.asarray(
                direction_details[selected]["raw_intercept"], dtype=np.float64
            ),
            "scaler_mean": selected_scaler.mean_.astype(np.float64),
            "scaler_scale": selected_scaler.scale_.astype(np.float64),
            "standardized_coefficient": selected_logistic.coef_[0].astype(np.float64),
            "standardized_intercept": selected_logistic.intercept_.astype(np.float64),
        },
    }


def _meta_model(c_value: float, seed: int) -> Pipeline:
    return make_pipeline(
        StandardScaler(),
        LogisticRegression(C=float(c_value), max_iter=3000, random_state=seed),
    )


def run_nested_stacking(
    features: np.ndarray,
    labels: np.ndarray,
    answer_nll: np.ndarray,
    groups: np.ndarray,
    c_grid: list[float],
    outer_folds: int,
    outer_repeats: int,
    inner_folds: int,
    seed: int,
    meta_c: float,
    bootstrap_samples: int,
    bootstrap_seed: int,
) -> dict[str, Any]:
    """Leakage-safe scalar stacking entirely within the locked development pool."""

    size = len(labels)
    names = ("answer_nll", "probe_score", "combined")
    probability_sums = {name: np.zeros(size, dtype=np.float64) for name in names}
    counts = np.zeros(size, dtype=np.int64)
    fold_rows = []
    for repetition in range(int(outer_repeats)):
        outer_seed = seed + repetition * 1000
        splits = list(_splitter(outer_folds, outer_seed).split(features, labels, groups))
        repetition_hits = np.zeros(size, dtype=np.int64)
        for fold, (train, test) in enumerate(splits):
            _check_group_disjoint(groups, train, test)
            tuning = select_c_one_se(
                features[train],
                labels[train],
                groups[train],
                c_grid,
                inner_folds,
                outer_seed + 100 + fold,
            )
            selected_c = float(tuning["selected_c"])
            train_probe_scores = np.full(len(train), np.nan, dtype=np.float64)
            inner_hits = np.zeros(len(train), dtype=np.int64)
            meta_oof_c_values = []
            inner_splits = list(
                _splitter(inner_folds, outer_seed + 200 + fold).split(
                    features[train], labels[train], groups[train]
                )
            )
            for inner_fold, (inner_train_local, inner_test_local) in enumerate(inner_splits):
                _check_group_disjoint(groups[train], inner_train_local, inner_test_local)
                meta_tuning = select_c_one_se(
                    features[train[inner_train_local]],
                    labels[train[inner_train_local]],
                    groups[train[inner_train_local]],
                    c_grid,
                    inner_folds,
                    outer_seed + 3000 + fold * 100 + inner_fold,
                )
                meta_selected_c = float(meta_tuning["selected_c"])
                meta_oof_c_values.append(meta_selected_c)
                base = _pipeline(
                    meta_selected_c, outer_seed + 300 + fold * 10 + inner_fold
                )
                base.fit(features[train[inner_train_local]], labels[train[inner_train_local]])
                train_probe_scores[inner_test_local] = base.decision_function(
                    features[train[inner_test_local]]
                )
                inner_hits[inner_test_local] += 1
            if not np.all(inner_hits == 1) or not np.all(np.isfinite(train_probe_scores)):
                raise RuntimeError("Nested stacking inner OOF ledger is incomplete")

            base = _pipeline(selected_c, outer_seed + 400 + fold)
            base.fit(features[train], labels[train])
            test_probe_scores = base.decision_function(features[test])
            training_meta = {
                "answer_nll": answer_nll[train].reshape(-1, 1),
                "probe_score": train_probe_scores.reshape(-1, 1),
                "combined": np.column_stack([answer_nll[train], train_probe_scores]),
            }
            test_meta = {
                "answer_nll": answer_nll[test].reshape(-1, 1),
                "probe_score": test_probe_scores.reshape(-1, 1),
                "combined": np.column_stack([answer_nll[test], test_probe_scores]),
            }
            for position, name in enumerate(names):
                meta = _meta_model(meta_c, outer_seed + 500 + fold * 10 + position)
                meta.fit(training_meta[name], labels[train])
                probability_sums[name][test] += meta.predict_proba(test_meta[name])[:, 1]
            counts[test] += 1
            repetition_hits[test] += 1
            fold_rows.append(
                {
                    "repetition": repetition,
                    "fold": fold,
                    "outer_train_size": int(len(train)),
                    "outer_heldout_size": int(len(test)),
                    "outer_context_overlap": 0,
                    "selected_probe_c": selected_c,
                    "meta_oof_probe_c_frequency": {
                        str(key): int(value)
                        for key, value in sorted(Counter(meta_oof_c_values).items())
                    },
                    "meta_training_probe_scores": (
                        "inner grouped out-of-fold; C selected inside each inner-training subset"
                    ),
                    "outer_heldout_excluded_from_probe_and_meta_fit": True,
                }
            )
        if not np.all(repetition_hits == 1):
            raise RuntimeError("A stacking outer repetition did not score every row once")
    if not np.all(counts == int(outer_repeats)):
        raise RuntimeError("Stacking OOF prediction ledger is incomplete")
    probabilities = {name: values / counts for name, values in probability_sums.items()}
    metrics = {
        name: {
            "auroc": float(roc_auc_score(labels, values)),
            "log_loss": float(log_loss(labels, np.clip(values, 1e-7, 1 - 1e-7), labels=[0, 1])),
        }
        for name, values in probabilities.items()
    }
    log_loss_improvement = grouped_bootstrap_interval(
        labels,
        probabilities["answer_nll"],
        groups,
        bootstrap_samples,
        bootstrap_seed,
        metric="log_loss",
        reference_probabilities=probabilities["combined"],
    )
    auroc_difference = grouped_bootstrap_interval(
        labels,
        probabilities["combined"],
        groups,
        bootstrap_samples,
        bootstrap_seed + 1,
        metric="auroc",
        reference_probabilities=probabilities["answer_nll"],
    )
    return {
        "method": "nested grouped OOF scalar stacking",
        "reserved_test_examples_used": False,
        "meta_c": float(meta_c),
        "prediction_count_min": int(counts.min()),
        "prediction_count_max": int(counts.max()),
        "metrics": metrics,
        "nll_minus_combined_log_loss": log_loss_improvement,
        "combined_minus_nll_auroc": auroc_difference,
        "oof_probabilities": {name: values.tolist() for name, values in probabilities.items()},
        "folds": fold_rows,
    }


def _plot(result: dict[str, Any], path: Path) -> None:
    layers = [result["primary_layer"], result["challenger_layer"]]
    layer_results = [result["layers"][str(layer)] for layer in layers]
    figure, axes = plt.subplots(1, 2, figsize=(10.5, 4.5))
    aucs = [row["nested_cv"]["oof_auroc"] for row in layer_results]
    lower = [row["nested_cv"]["oof_auroc_context_bootstrap_95"]["lower_95"] for row in layer_results]
    upper = [row["nested_cv"]["oof_auroc_context_bootstrap_95"]["upper_95"] for row in layer_results]
    axes[0].errorbar(
        [str(layer) for layer in layers],
        aucs,
        yerr=[np.asarray(aucs) - np.asarray(lower), np.asarray(upper) - np.asarray(aucs)],
        fmt="o",
        capsize=4,
        linewidth=2,
    )
    axes[0].axhline(0.5, color="gray", linestyle=":")
    axes[0].axhline(0.65, color="tab:blue", linestyle="--", alpha=0.5)
    axes[0].set(xlabel="Transformer block", ylabel="Development OOF AUROC", ylim=(0, 1))
    axes[0].set_title("Nested grouped prediction")
    axes[0].grid(alpha=0.2)

    primary = layer_results[0]["split_half"]
    axes[1].scatter(
        [1],
        [primary["raw_direction_cosine"]["median"]],
        marker="D",
        s=55,
        color="tab:blue",
        label="Observed median",
        zorder=3,
    )
    axes[1].boxplot(
        [primary["shuffled_control"]["raw_direction_cosine"]["values"]],
        positions=[2],
        widths=0.6,
        showfliers=False,
    )
    axes[1].axhline(0.0, color="gray", linestyle=":")
    axes[1].axhline(0.5, color="tab:blue", linestyle="--", alpha=0.5)
    axes[1].set(
        ylabel="Median raw-space cosine similarity",
        ylim=(-1, 1),
        xticks=[1, 2],
        xticklabels=["Layer 14 observed", "Shuffled null"],
    )
    axes[1].set_title("Matched direction-stability null test")
    axes[1].grid(alpha=0.2)
    axes[1].legend(fontsize=8)
    figure.suptitle("Qwen2.5-1.5B cached direction audit")
    figure.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(path, dpi=180)
    plt.close(figure)


def run_direction_stability(
    config_path: str | Path,
    progress: Callable[[str], None] | None = print,
) -> dict[str, Any]:
    """Execute the preregistered cached audit and save its JSON and plot."""

    started = time.monotonic()
    data = load_cached_audit_data(config_path)
    config = data["config"]
    analysis = config["analysis"]
    nested = analysis["nested_cv"]
    direction = analysis["direction_stability"]
    shuffled = analysis["shuffled_control"]
    bootstrap = analysis["bootstrap"]
    stacking_config = analysis["stacking"]
    seed = int(analysis["seed"])
    c_grid = [float(value) for value in nested["c_grid"]]
    if progress:
        progress("Validated frozen hashes and locked 401/99 split; reserved test remains unused.")

    layer_results = {}
    for layer in (data["primary_layer"], data["challenger_layer"]):
        if progress:
            role = "primary" if layer == data["primary_layer"] else "exploratory challenger"
            progress(f"Running cached nested CV and direction audit for layer {layer} ({role}).")
        features = data["features"][layer]
        nested_result = run_repeated_nested_cv(
            features,
            data["labels"],
            data["groups"],
            data["entropy"],
            c_grid,
            int(nested["outer_folds"]),
            int(nested["outer_repeats"]),
            int(nested["inner_folds"]),
            seed,
            int(bootstrap["samples"]),
            int(bootstrap["seed"]),
        )
        split_half = run_split_half_stability(
            features,
            data["labels"],
            data["groups"],
            c_grid,
            int(nested["inner_folds"]),
            int(direction["repetitions"]),
            int(shuffled["repetitions"]),
            seed + 30000,
            int(shuffled["seed"]),
            int(direction["folds_per_repetition"]),
            [int(value) for value in direction["train_a_folds"]],
            [int(value) for value in direction["train_b_folds"]],
            int(direction["common_evaluation_fold"]),
        )
        adjacent = run_adjacent_c_robustness(
            features,
            data["labels"],
            data["groups"],
            c_grid,
            int(nested["inner_folds"]),
            seed + 60000,
        )
        layer_results[str(layer)] = {
            "role": "primary" if layer == data["primary_layer"] else "exploratory_challenger",
            "nested_cv": nested_result,
            "split_half": split_half,
            "adjacent_c_robustness": adjacent,
        }

    output_dir = _resolve(_root_dir(), analysis["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    frozen_arrays: dict[str, np.ndarray] = {
        "primary_layer": np.asarray(data["primary_layer"], dtype=np.int64),
        "challenger_layer": np.asarray(data["challenger_layer"], dtype=np.int64),
        "semantic_entropy_threshold": np.asarray(data["frozen_threshold"], dtype=np.float64),
    }
    for layer in (data["primary_layer"], data["challenger_layer"]):
        arrays = layer_results[str(layer)]["adjacent_c_robustness"].pop(
            "_frozen_probe_arrays"
        )
        for name, value in arrays.items():
            frozen_arrays[f"layer_{layer}_{name}"] = np.asarray(value)
    frozen_path = output_dir / "frozen_probe_directions.npz"
    _atomic_npz(frozen_path, frozen_arrays)
    frozen_artifact = {
        "path": _shareable_path(frozen_path),
        "sha256": _sha256(frozen_path),
        "primary_direction_key": f"layer_{data['primary_layer']}_unit_raw_direction",
        "positive_direction": "higher semantic entropy",
    }

    if progress:
        progress("Running corrected nested scalar stacking for primary layer 14.")
    stacking = run_nested_stacking(
        data["features"][data["primary_layer"]],
        data["labels"],
        data["answer_nll"],
        data["groups"],
        c_grid,
        int(nested["outer_folds"]),
        int(nested["outer_repeats"]),
        int(nested["inner_folds"]),
        seed + 900000,
        float(stacking_config["meta_c"]),
        int(bootstrap["samples"]),
        int(bootstrap["seed"]) + 900,
    )

    primary = layer_results[str(data["primary_layer"])]
    gates = config["success_gates"]
    primary_gate_results = {
        "nested_oof_auroc": primary["nested_cv"]["oof_auroc"]
        >= float(gates["primary_nested_oof_auroc_min"]),
        "nested_oof_auroc_lower_95": primary["nested_cv"]["oof_auroc_context_bootstrap_95"][
            "lower_95"
        ]
        > float(gates["primary_nested_oof_auroc_lower_95_min"]),
        "raw_cosine_median": primary["split_half"]["raw_direction_cosine"]["median"]
        >= float(gates["primary_raw_cosine_median_min"]),
        "raw_cosine_positive_fraction": primary["split_half"]["raw_direction_cosine"][
            "fraction_positive"
        ]
        >= float(gates["primary_raw_cosine_positive_fraction_min"]),
        "raw_cosine_empirical_lower_95": primary["split_half"]["raw_direction_cosine"][
            "empirical_2.5"
        ]
        > float(gates["primary_raw_cosine_empirical_lower_95_min"]),
        "common_holdout_score_spearman_median": primary["split_half"][
            "common_evaluation_score_spearman"
        ]["median"]
        >= float(gates["primary_common_holdout_score_spearman_median_min"]),
        "adjacent_c_cosine": primary["adjacent_c_robustness"]["minimum_adjacent_c_cosine"]
        >= float(gates["primary_adjacent_c_cosine_min"]),
        "cosine_above_shuffled_upper_95": (
            not bool(gates["primary_cosine_must_exceed_shuffled_upper_95"])
            or primary["split_half"]["raw_direction_cosine"]["median"]
            > primary["split_half"]["shuffled_control"]["raw_direction_cosine"][
                "empirical_97.5"
            ]
        ),
    }
    incremental_gate_results = {
        "nll_minus_combined_log_loss_lower_95": stacking[
            "nll_minus_combined_log_loss"
        ]["lower_95"]
        > float(gates["incremental_nll_minus_combined_log_loss_lower_95_min"])
    }
    direction_passed = bool(all(primary_gate_results.values()))
    incremental_passed = bool(all(incremental_gate_results.values()))
    result = {
        "analysis_name": "run_500_qwen15b_direction_stability",
        "analysis_type": "cached-only preregistered direction and incremental-information audit",
        "source_run": config["source_run"],
        "source_artifact_sha256": data["source_artifact_sha256"],
        "config_path": _shareable_path(Path(data["config_path"])),
        "frozen_threshold": data["frozen_threshold"],
        "primary_layer": data["primary_layer"],
        "challenger_layer": data["challenger_layer"],
        "cached_layers": data["cached_layers"],
        "hidden_width": data["hidden_width"],
        "frozen_probe_direction_artifact": frozen_artifact,
        "split_validation": data["split_validation"],
        "protocol": {
            "development_pool": "source train_indices + validation_indices (401 examples)",
            "reserved_pool": "source test_indices (99 examples), never fit or scored in this audit",
            "labels": "source frozen semantic-entropy threshold; high entropy is positive",
            "selection": "nested StratifiedGroupKFold; one-SE rule; smallest eligible C",
            "direction_coordinates": "coef / StandardScaler.scale_, unit L2 normalized",
            "direction_stability": direction["method"],
            "stacking": stacking_config["method"],
            "bootstrap_unit": bootstrap["unit"],
            "interpretation": [
                "Layer 14 is the only primary gate; layer 23 is exploratory and cannot rescue it.",
                "Passing this audit permits a small activation-steering diagnostic, not a mechanistic loss.",
                "The locked 99-example set was previously reported and is not a pristine confirmation set.",
            ],
        },
        "success_gates": gates,
        "primary_direction_gate_results": primary_gate_results,
        "primary_direction_stability_passed": direction_passed,
        "incremental_information_gate_results": incremental_gate_results,
        "incremental_information_passed": incremental_passed,
        "eligible_for_activation_steering": direction_passed,
        "ready_for_mechanistic_loss": False,
        "layers": layer_results,
        "primary_layer_nested_stacking": stacking,
        "elapsed_seconds": float(time.monotonic() - started),
    }
    _atomic_json(output_dir / "direction_stability_metrics.json", result)
    plot_path = _resolve(_root_dir(), analysis["plot_path"])
    _plot(result, plot_path)
    if progress:
        progress(
            "Cached audit complete: "
            f"direction gate={'PASS' if direction_passed else 'FAIL'}, "
            f"incremental gate={'PASS' if incremental_passed else 'FAIL'}."
        )
    return result
