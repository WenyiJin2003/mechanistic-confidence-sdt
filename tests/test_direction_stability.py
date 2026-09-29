import json
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from stage0.direction_stability import (
    grouped_bootstrap_interval,
    load_cached_audit_data,
    raw_logistic_direction,
    run_nested_stacking,
    run_split_half_stability,
    select_c_one_se,
)


ROOT = Path(__file__).resolve().parents[1]
AUDIT_CONFIG = ROOT / "configs" / "stage0_qwen15b_direction_stability.yaml"
SOURCE_DIR = ROOT / "results" / "run_500_qwen15b_confirm"


def test_one_se_selects_strongest_regularization_within_one_se():
    # Every context contains both labels and the first feature perfectly orders
    # them, so all C values attain the same inner-CV AUROC.
    groups = np.repeat(np.arange(20), 2)
    labels = np.tile([0, 1], 20)
    features = np.column_stack(
        [2 * labels - 1, np.sin(np.arange(len(labels), dtype=np.float64))]
    )
    c_grid = [0.0001, 0.01, 1.0]

    result = select_c_one_se(
        features,
        labels,
        groups,
        c_grid=c_grid,
        n_splits=4,
        seed=29,
    )

    assert all(row["mean_auroc"] == 1.0 for row in result["c_results"])
    assert result["selected_c"] == min(c_grid)
    assert result["selected_c"] <= result["best_mean_c"]


def test_raw_logistic_parameters_reconstruct_pipeline_decision_scores():
    rng = np.random.default_rng(17)
    features = rng.normal(size=(96, 5))
    labels = (features @ np.asarray([1.4, -0.8, 0.2, 0.6, -1.1]) > 0.15).astype(int)
    model = make_pipeline(
        StandardScaler(),
        LogisticRegression(C=0.7, max_iter=2000, random_state=9),
    )
    model.fit(features, labels)

    direction = raw_logistic_direction(model, verification_features=features)
    reconstructed = features @ direction["raw_weight"] + direction["raw_intercept"]

    assert direction["raw_weight"].shape == (features.shape[1],)
    assert np.isclose(np.linalg.norm(direction["unit_direction"]), 1.0)
    assert direction["maximum_decision_reconstruction_error"] < 1e-12
    np.testing.assert_allclose(
        reconstructed,
        model.decision_function(features),
        rtol=1e-12,
        atol=1e-12,
    )


def test_grouped_bootstrap_is_deterministic_and_resamples_whole_groups():
    labels = np.asarray([0, 1, 0, 0, 1, 1, 0, 1, 1, 0])
    probabilities = np.asarray([0.1, 0.8, 0.2, 0.4, 0.7, 0.9, 0.3, 0.6, 0.75, 0.25])
    groups = np.asarray(["a", "a", "b", "b", "b", "c", "d", "d", "d", "d"])
    samples = 24
    seed = 271828

    first = grouped_bootstrap_interval(
        labels, probabilities, groups, samples=samples, seed=seed, metric="log_loss"
    )
    second = grouped_bootstrap_interval(
        labels, probabilities, groups, samples=samples, seed=seed, metric="log_loss"
    )

    # Independently replay whole-group draws. A row bootstrap produces different
    # quantiles for these unequal group sizes.
    unique_groups = np.unique(groups)
    group_indices = {group: np.flatnonzero(groups == group) for group in unique_groups}
    rng = np.random.default_rng(seed)
    manual_values = []
    for _ in range(samples):
        sampled_groups = rng.choice(unique_groups, size=len(unique_groups), replace=True)
        indices = np.concatenate([group_indices[group] for group in sampled_groups])
        manual_values.append(log_loss(labels[indices], probabilities[indices], labels=[0, 1]))

    assert first == second
    assert first["resampling_unit"] == "normalized context"
    assert first["valid_resamples"] == samples
    assert np.isclose(first["lower_95"], np.percentile(manual_values, 2.5))
    assert np.isclose(first["median"], np.median(manual_values))
    assert np.isclose(first["upper_95"], np.percentile(manual_values, 97.5))


def test_locked_loader_uses_only_real_cached_development_rows():
    locked = load_cached_audit_data(AUDIT_CONFIG)
    metrics = json.loads((SOURCE_DIR / "probe_metrics.json").read_text(encoding="utf-8"))
    records = [
        json.loads(line)
        for line in (SOURCE_DIR / "generations.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    source_indices = np.asarray(locked["development_original_indices"], dtype=int)
    reserved_indices = np.asarray(locked["reserved_original_indices"], dtype=int)
    expected_development = set(metrics["train_indices"]) | set(metrics["validation_indices"])

    assert len(source_indices) == 401
    assert len(reserved_indices) == 99
    assert set(source_indices) == expected_development
    assert set(reserved_indices) == set(metrics["test_indices"])
    assert set(source_indices).isdisjoint(reserved_indices)
    assert len(locked["groups"]) == len(locked["labels"]) == len(source_indices)
    assert all(
        len(layer_features) == len(source_indices)
        for layer_features in locked["features"].values()
    )
    assert locked["split_validation"]["development_reserved_index_overlap"] == 0
    assert locked["split_validation"]["development_reserved_context_overlap"] == 0
    assert "reserved_features" not in locked
    assert "reserved_labels" not in locked

    normalize_context = lambda value: " ".join(value.lower().split())
    development_contexts = {
        normalize_context(records[index]["context"]) for index in source_indices
    }
    reserved_contexts = {
        normalize_context(records[index]["context"]) for index in reserved_indices
    }
    assert development_contexts.isdisjoint(reserved_contexts)


def test_split_half_stability_reports_disjoint_group_partitions():
    groups = np.repeat(np.asarray([f"group-{index}" for index in range(15)]), 4)
    labels = np.tile([0, 1, 0, 1], 15)
    rng = np.random.default_rng(41)
    features = np.column_stack(
        [2 * labels - 1 + rng.normal(scale=0.05, size=len(labels)), rng.normal(size=len(labels))]
    )

    result = run_split_half_stability(
        features,
        labels,
        groups,
        c_grid=[0.1],
        inner_folds=2,
        repetitions=1,
        shuffle_repetitions=1,
        seed=20260929,
        shuffle_seed=271828,
    )

    split = result["splits"][0]
    assert split["pairwise_context_overlap"] == 0
    assert (
        split["first_train_size"]
        + split["second_train_size"]
        + split["common_evaluation_size"]
        == len(groups)
    )


def test_nested_stacking_uses_complete_outer_oof_ledger():
    groups = np.repeat(np.asarray([f"group-{index}" for index in range(30)]), 4)
    labels = np.tile([0, 1, 0, 1], 30)
    rng = np.random.default_rng(77)
    features = rng.normal(size=(len(labels), 5))
    features[:, 0] += labels
    answer_nll = 0.2 + labels + rng.normal(scale=0.2, size=len(labels))

    result = run_nested_stacking(
        features,
        labels,
        answer_nll,
        groups,
        c_grid=[0.01, 0.1],
        outer_folds=3,
        outer_repeats=1,
        inner_folds=2,
        seed=41,
        meta_c=1.0,
        bootstrap_samples=20,
        bootstrap_seed=42,
    )

    assert result["reserved_test_examples_used"] is False
    assert result["prediction_count_min"] == result["prediction_count_max"] == 1
    assert all(row["outer_context_overlap"] == 0 for row in result["folds"])
    assert all(
        row["outer_heldout_excluded_from_probe_and_meta_fit"] for row in result["folds"]
    )
    assert all(
        "C selected inside each inner-training subset"
        in row["meta_training_probe_scores"]
        for row in result["folds"]
    )
