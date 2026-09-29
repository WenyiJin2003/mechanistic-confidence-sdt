"""Repeated grouped-split diagnostics over cached Stage 0 artifacts."""

from __future__ import annotations

import copy
import hashlib
import time
from collections import Counter
from pathlib import Path
from typing import Any

import matplotlib
import numpy as np
import yaml
from scipy.stats import spearmanr
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from stage0.pipeline import (
    atomic_json,
    audit_split,
    best_train_threshold,
    bootstrap_auroc,
    fixed_group_split,
    load_config,
    probe_model,
    read_jsonl,
    root_dir,
    stable_hash,
)


matplotlib.use("Agg")
from matplotlib import pyplot as plt  # noqa: E402


def summarize_scores(values: list[float]) -> dict[str, Any]:
    array = np.asarray(values, dtype=np.float64)
    array = array[np.isfinite(array)]
    if array.size == 0:
        return {"count": 0}
    return {
        "count": int(array.size),
        "mean": float(array.mean()),
        "median": float(np.median(array)),
        "q1": float(np.percentile(array, 25)),
        "q3": float(np.percentile(array, 75)),
        "minimum": float(array.min()),
        "maximum": float(array.max()),
        "empirical_2.5": float(np.percentile(array, 2.5)),
        "empirical_97.5": float(np.percentile(array, 97.5)),
        "fraction_above_0.5": float(np.mean(array > 0.5)),
        "fraction_at_least_0.6": float(np.mean(array >= 0.6)),
        "values": array.tolist(),
    }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _class_counts(labels: np.ndarray, indices: np.ndarray) -> dict[str, int]:
    return {
        str(key): int(value)
        for key, value in Counter(labels[indices].tolist()).items()
    }


def _auc(labels: np.ndarray, probabilities: np.ndarray) -> float:
    return float(roc_auc_score(labels, probabilities))


def _scalar_probe(
    values: np.ndarray,
    labels: np.ndarray,
    train: np.ndarray,
    validation: np.ndarray,
    test: np.ndarray,
    seed: int,
) -> dict[str, float]:
    model = make_pipeline(
        StandardScaler(),
        LogisticRegression(max_iter=2000, random_state=seed),
    )
    model.fit(values[train], labels[train])
    return {
        "validation_auroc": _auc(labels[validation], model.predict_proba(values[validation])[:, 1]),
        "test_auroc": _auc(labels[test], model.predict_proba(values[test])[:, 1]),
    }


def _continuous_probe(
    features: np.ndarray,
    entropy: np.ndarray,
    train: np.ndarray,
    validation: np.ndarray,
    test: np.ndarray,
) -> dict[str, float]:
    model = make_pipeline(StandardScaler(), Ridge(alpha=1.0))
    model.fit(features[train], entropy[train])
    validation_score = spearmanr(entropy[validation], model.predict(features[validation])).statistic
    test_score = spearmanr(entropy[test], model.predict(features[test])).statistic
    return {
        "validation_spearman": float(validation_score),
        "test_spearman": float(test_score),
    }


def _bootstrap_auc_difference(
    labels: np.ndarray,
    first: np.ndarray,
    second: np.ndarray,
    groups: np.ndarray,
    samples: int,
    seed: int,
) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    unique_groups = np.unique(groups)
    differences = []
    for _ in range(samples):
        sampled_groups = rng.choice(unique_groups, size=len(unique_groups), replace=True)
        indices = np.concatenate([np.flatnonzero(groups == group) for group in sampled_groups])
        if np.unique(labels[indices]).size < 2:
            continue
        differences.append(
            _auc(labels[indices], first[indices]) - _auc(labels[indices], second[indices])
        )
    values = np.asarray(differences, dtype=np.float64)
    return {
        "estimate": _auc(labels, first) - _auc(labels, second),
        "lower_95": float(np.percentile(values, 2.5)),
        "median": float(np.median(values)),
        "upper_95": float(np.percentile(values, 97.5)),
        "valid_resamples": int(values.size),
    }


def _cross_fitted_fixed_layer(
    config: dict[str, Any],
    records: list[dict[str, Any]],
    semantic_rows: list[dict[str, Any]],
    hidden: np.ndarray,
    layers: list[int],
    fixed_layer: int,
    folds: int,
    seed: int,
    bootstrap_samples: int,
) -> dict[str, Any]:
    entropy = np.asarray(
        [row["cluster_assignment_entropy"] for row in semantic_rows], dtype=np.float64
    )
    answer_nll = np.asarray(
        [row["answer_negative_log_likelihood"] for row in semantic_rows], dtype=np.float64
    ).reshape(-1, 1)
    correctness = np.asarray(
        [row["any_sample_exact_match"] for row in semantic_rows], dtype=np.int64
    )
    groups = np.asarray(
        [stable_hash(" ".join(record["context"].lower().split())) for record in records]
    )
    features = hidden[:, layers.index(fixed_layer), :].astype(np.float32)
    splitter = GroupKFold(n_splits=folds, shuffle=True, random_state=seed)
    labels = np.full(len(records), -1, dtype=np.int64)
    probabilities = np.full(len(records), np.nan, dtype=np.float64)
    nll_probabilities = np.full(len(records), np.nan, dtype=np.float64)
    fold_rows = []
    for fold, (train, test) in enumerate(splitter.split(features, groups=groups)):
        threshold = best_train_threshold(entropy[train])
        fold_labels = (entropy >= threshold).astype(np.int64)
        if np.unique(fold_labels[train]).size < 2 or np.unique(fold_labels[test]).size < 2:
            raise ValueError(f"Cross-fit fold {fold} has a single class")
        model = probe_model(config, seed + fold)
        model.fit(features[train], fold_labels[train])
        scalar = make_pipeline(
            StandardScaler(),
            LogisticRegression(max_iter=2000, random_state=seed + fold),
        )
        scalar.fit(answer_nll[train], fold_labels[train])
        labels[test] = fold_labels[test]
        probabilities[test] = model.predict_proba(features[test])[:, 1]
        nll_probabilities[test] = scalar.predict_proba(answer_nll[test])[:, 1]
        fold_rows.append(
            {
                "fold": fold,
                "train_size": int(len(train)),
                "test_size": int(len(test)),
                "threshold": float(threshold),
                "test_auroc": _auc(fold_labels[test], probabilities[test]),
                "test_label_counts": _class_counts(fold_labels, test),
            }
        )
    if np.any(labels < 0) or np.any(~np.isfinite(probabilities)):
        raise RuntimeError("Cross-fitted predictions are incomplete")
    probe_ci = bootstrap_auroc(
        labels, probabilities, bootstrap_samples, seed + 10000, groups
    )
    correctness_ci = bootstrap_auroc(
        correctness, 1 - probabilities, bootstrap_samples, seed + 20000, groups
    )
    return {
        "folds": fold_rows,
        "auroc": _auc(labels, probabilities),
        "auroc_context_bootstrap_95": probe_ci,
        "correctness_auroc_from_low_entropy_score": _auc(correctness, 1 - probabilities),
        "correctness_auroc_context_bootstrap_95": correctness_ci,
        "answer_nll_auroc": _auc(labels, nll_probabilities),
        "probe_minus_answer_nll_auroc": _bootstrap_auc_difference(
            labels,
            probabilities,
            nll_probabilities,
            groups,
            bootstrap_samples,
            seed + 30000,
        ),
    }


def _plot(summary: dict[str, Any], layers: list[int], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    figure, axes = plt.subplots(1, 2, figsize=(10.5, 4.8))
    layer_values = [summary["per_layer"][str(layer)]["test_auroc"]["values"] for layer in layers]
    axes[0].boxplot(layer_values, tick_labels=[str(layer) for layer in layers], showfliers=False)
    axes[0].axhline(0.5, color="gray", linestyle=":", label="chance")
    axes[0].axvline(layers.index(summary["fixed_primary_layer"]) + 1, color="black", alpha=0.18)
    axes[0].set(
        xlabel="Transformer block",
        ylabel="Test AUROC across grouped splits",
        title="Fixed-layer split sensitivity",
        ylim=(0, 1),
    )
    axes[0].grid(alpha=0.2)
    axes[0].legend(fontsize=8)

    comparison_names = [
        "fixed layer 14",
        "validation selected",
        "predictive entropy",
        "answer NLL",
        "shuffled layer 14",
    ]
    comparison_values = [
        summary["fixed_layer"]["test_auroc"]["values"],
        summary["validation_selected"]["test_auroc"]["values"],
        summary["baselines"]["predictive_entropy"]["test_auroc"]["values"],
        summary["baselines"]["answer_negative_log_likelihood"]["test_auroc"]["values"],
        summary["fixed_layer"]["shuffled_test_auroc"]["values"],
    ]
    axes[1].boxplot(comparison_values, tick_labels=comparison_names, showfliers=False)
    axes[1].axhline(0.5, color="gray", linestyle=":")
    axes[1].set(
        ylabel="Test AUROC across grouped splits",
        title="Probe and controls",
        ylim=(0, 1),
    )
    axes[1].tick_params(axis="x", rotation=25)
    axes[1].grid(alpha=0.2)
    figure.suptitle("Qwen 1.5B cached split-stability audit")
    figure.tight_layout()
    figure.savefig(output, dpi=180)
    plt.close(figure)


def run_stability(config_path: str | Path) -> dict[str, Any]:
    started = time.monotonic()
    path = Path(config_path).expanduser().resolve()
    with path.open("r", encoding="utf-8") as handle:
        stability_config = yaml.safe_load(handle)
    root = root_dir()
    base_path = Path(stability_config["base_config"])
    if not base_path.is_absolute():
        base_path = root / base_path
    config, _ = load_config(base_path)
    source_run = stability_config["source_run"]
    source_dir = Path(config["project"]["results_dir"]) / source_run
    generation_path = source_dir / "generations.jsonl"
    semantic_path = source_dir / "semantic_entropy.jsonl"
    hidden_path = source_dir / "hidden_states.npz"
    records = read_jsonl(generation_path)
    semantic_rows = read_jsonl(semantic_path)
    with np.load(hidden_path) as archive:
        hidden = archive["hidden_states"]
        layers = [int(value) for value in archive["layers"].tolist()]
        example_ids = archive["example_ids"].astype(str).tolist()
    if len(records) != len(semantic_rows) or hidden.shape[0] != len(records):
        raise ValueError("Cached artifact row counts do not match")
    if example_ids != [record["id"] for record in records]:
        raise ValueError("Hidden-state example order does not match generation records")

    analysis = stability_config["analysis"]
    first_seed = int(analysis["split_seeds"]["start"])
    seed_count = int(analysis["split_seeds"]["count"])
    seeds = list(range(first_seed, first_seed + seed_count))
    fixed_layer = int(analysis["fixed_primary_layer"])
    if fixed_layer not in layers:
        raise ValueError(f"Fixed primary layer {fixed_layer} is not cached")
    minimum_class_count = int(analysis["minimum_class_count_per_test_split"])
    shuffle_repetitions = int(analysis["shuffled_labels_per_seed"])
    entropy = np.asarray(
        [row["cluster_assignment_entropy"] for row in semantic_rows], dtype=np.float64
    )
    baseline_values = {
        name: np.asarray([row[name] for row in semantic_rows], dtype=np.float64).reshape(-1, 1)
        for name in ("predictive_entropy", "answer_negative_log_likelihood")
    }
    correctness = np.asarray(
        [row["any_sample_exact_match"] for row in semantic_rows], dtype=np.int64
    )
    split_rows = []
    invalid_splits = []
    for seed in seeds:
        probe_config = copy.deepcopy(config["probe"])
        probe_config["split_seed"] = seed
        train, validation, test = fixed_group_split(records, probe_config)
        threshold = best_train_threshold(entropy[train])
        labels = (entropy >= threshold).astype(np.int64)
        counts = {
            "train": _class_counts(labels, train),
            "validation": _class_counts(labels, validation),
            "test": _class_counts(labels, test),
        }
        if any(len(split_counts) < 2 for split_counts in counts.values()):
            invalid_splits.append({"seed": seed, "reason": "single class", "label_counts": counts})
            continue
        if min(counts["test"].values()) < minimum_class_count:
            invalid_splits.append(
                {"seed": seed, "reason": "minimum test class count", "label_counts": counts}
            )
            continue
        layer_rows = []
        shuffled_labels_by_repetition = []
        shuffle_rng = np.random.default_rng(int(config["probe"]["shuffle_seed"]) + seed)
        for _ in range(shuffle_repetitions):
            shuffled_labels_by_repetition.append(shuffle_rng.permutation(labels[train]))
        for position, layer in enumerate(layers):
            features = hidden[:, position, :].astype(np.float32)
            model = probe_model(config, seed)
            model.fit(features[train], labels[train])
            validation_probabilities = model.predict_proba(features[validation])[:, 1]
            test_probabilities = model.predict_proba(features[test])[:, 1]
            shuffled_scores = []
            for repetition, shuffled_labels in enumerate(shuffled_labels_by_repetition):
                shuffled = probe_model(config, int(config["probe"]["shuffle_seed"]) + seed + repetition)
                shuffled.fit(features[train], shuffled_labels)
                shuffled_scores.append(
                    _auc(labels[test], shuffled.predict_proba(features[test])[:, 1])
                )
            continuous = _continuous_probe(features, entropy, train, validation, test)
            layer_rows.append(
                {
                    "layer": layer,
                    "validation_auroc": _auc(labels[validation], validation_probabilities),
                    "test_auroc": _auc(labels[test], test_probabilities),
                    "shuffled_test_auroc": float(np.mean(shuffled_scores)),
                    "test_correctness_auroc_from_low_entropy_score": (
                        _auc(correctness[test], 1 - test_probabilities)
                        if np.unique(correctness[test]).size == 2
                        else None
                    ),
                    **continuous,
                }
            )
        selected = max(layer_rows, key=lambda row: row["validation_auroc"])
        fixed = next(row for row in layer_rows if row["layer"] == fixed_layer)
        baselines = {
            name: _scalar_probe(values, labels, train, validation, test, seed)
            for name, values in baseline_values.items()
        }
        split_audit = audit_split(
            records,
            {
                "train_indices": train.tolist(),
                "validation_indices": validation.tolist(),
                "test_indices": test.tolist(),
            },
        )
        split_rows.append(
            {
                "seed": seed,
                "threshold_fit_on_training_only": float(threshold),
                "split_sizes": {
                    "train": int(len(train)),
                    "validation": int(len(validation)),
                    "test": int(len(test)),
                },
                "label_counts": counts,
                "split_audit_passed": bool(split_audit["passed"]),
                "selected_layer": int(selected["layer"]),
                "selected_validation_auroc": float(selected["validation_auroc"]),
                "selected_test_auroc": float(selected["test_auroc"]),
                "fixed_layer": fixed,
                "layers": layer_rows,
                "baselines": baselines,
            }
        )

    def layer_summary(layer: int) -> dict[str, Any]:
        rows = [
            next(item for item in split["layers"] if item["layer"] == layer)
            for split in split_rows
        ]
        return {
            "validation_auroc": summarize_scores([row["validation_auroc"] for row in rows]),
            "test_auroc": summarize_scores([row["test_auroc"] for row in rows]),
            "shuffled_test_auroc": summarize_scores(
                [row["shuffled_test_auroc"] for row in rows]
            ),
            "test_spearman": summarize_scores([row["test_spearman"] for row in rows]),
            "test_correctness_auroc_from_low_entropy_score": summarize_scores(
                [
                    row["test_correctness_auroc_from_low_entropy_score"]
                    for row in rows
                    if row["test_correctness_auroc_from_low_entropy_score"] is not None
                ]
            ),
        }

    per_layer = {str(layer): layer_summary(layer) for layer in layers}
    selection_counts = Counter(split["selected_layer"] for split in split_rows)
    summary = {
        "fixed_primary_layer": fixed_layer,
        "valid_split_count": len(split_rows),
        "invalid_split_count": len(invalid_splits),
        "all_split_audits_passed": all(split["split_audit_passed"] for split in split_rows),
        "thresholds": summarize_scores(
            [split["threshold_fit_on_training_only"] for split in split_rows]
        ),
        "fixed_layer": per_layer[str(fixed_layer)],
        "validation_selected": {
            "test_auroc": summarize_scores(
                [split["selected_test_auroc"] for split in split_rows]
            ),
            "validation_auroc": summarize_scores(
                [split["selected_validation_auroc"] for split in split_rows]
            ),
            "layer_frequency": {
                str(layer): int(selection_counts.get(layer, 0)) for layer in layers
            },
        },
        "per_layer": per_layer,
        "baselines": {
            name: {
                "validation_auroc": summarize_scores(
                    [split["baselines"][name]["validation_auroc"] for split in split_rows]
                ),
                "test_auroc": summarize_scores(
                    [split["baselines"][name]["test_auroc"] for split in split_rows]
                ),
            }
            for name in baseline_values
        },
    }
    cross_fitted = _cross_fitted_fixed_layer(
        config,
        records,
        semantic_rows,
        hidden,
        layers,
        fixed_layer,
        int(analysis["cross_fit_folds"]),
        int(analysis["cross_fit_seed"]),
        int(analysis["cross_fit_bootstrap_samples"]),
    )
    gates = stability_config["success_gates"]
    middle_layers = {int(value) for value in gates["middle_layers"]}
    middle_fraction = sum(selection_counts.get(layer, 0) for layer in middle_layers) / max(
        len(split_rows), 1
    )
    gate_results = {
        "valid_split_count": len(split_rows) == int(gates["valid_split_count"]),
        "all_split_audits_passed": summary["all_split_audits_passed"],
        "fixed_layer_median_test_auroc": (
            summary["fixed_layer"]["test_auroc"]["median"]
            >= float(gates["fixed_layer_median_test_auroc_min"])
        ),
        "fixed_layer_fraction_above_chance": (
            summary["fixed_layer"]["test_auroc"]["fraction_above_0.5"]
            >= float(gates["fixed_layer_fraction_above_chance_min"])
        ),
        "cross_fitted_auroc_lower_95": (
            cross_fitted["auroc_context_bootstrap_95"]["lower_95"]
            > float(gates["cross_fitted_auroc_lower_95_min"])
        ),
        "middle_layer_selection_fraction": (
            middle_fraction >= float(gates["middle_layer_selection_fraction_min"])
        ),
    }
    summary["middle_layer_selection_fraction"] = float(middle_fraction)
    result = {
        "analysis_name": "run_200_qwen15b_split_stability",
        "source_run": source_run,
        "source_artifact_sha256": {
            "generations.jsonl": _sha256(generation_path),
            "semantic_entropy.jsonl": _sha256(semantic_path),
            "hidden_states.npz": _sha256(hidden_path),
        },
        "protocol": {
            "split_method": "100 fixed context-grouped repeated holdouts",
            "split_seeds": seeds,
            "fixed_primary_layer": fixed_layer,
            "validation_selected_analysis": "secondary",
            "threshold": "fit on each training split only",
            "feature_scaling": "fit on each training split only",
            "regularization_c": float(config["probe"]["c"]),
            "minimum_class_count_per_test_split": minimum_class_count,
            "notes": [
                "Repeated test sets overlap; empirical split percentiles are sensitivity ranges, not confidence intervals.",
                "Cross-fitted confidence intervals use context-group bootstrap resampling.",
                "This analysis reuses cached examples and cannot replace fresh-data confirmation.",
            ],
        },
        "success_gates": gates,
        "gate_results": gate_results,
        "passed": all(gate_results.values()),
        "summary": summary,
        "cross_fitted_fixed_layer": cross_fitted,
        "invalid_splits": invalid_splits,
        "splits": split_rows,
        "elapsed_seconds": float(time.monotonic() - started),
    }
    output_dir = Path(analysis["output_dir"])
    if not output_dir.is_absolute():
        output_dir = root / output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    atomic_json(output_dir / "stability_metrics.json", result)
    plot_path = Path(analysis["plot_path"])
    if not plot_path.is_absolute():
        plot_path = root / plot_path
    _plot(summary, layers, plot_path)
    return result
