import numpy as np

from stage0.pipeline import (
    best_train_threshold,
    cluster_entropy,
    fixed_group_split,
    normalize_answer,
    squad_exact_match,
    squad_f1,
)
from stage0.stability import summarize_scores
from stage0.label_stability import compare_prefixes, select_rank_stratified


def test_normalize_answer():
    assert normalize_answer(" The Eiffel Tower. ") == "eiffel tower"


def test_cluster_entropy():
    assert np.isclose(cluster_entropy([0, 0, 1, 1]), np.log(2))
    assert cluster_entropy([0, 0, 0]) == 0.0


def test_squad_correctness_metrics():
    references = ["The Eiffel Tower", "Eiffel Tower"]
    assert squad_exact_match("Eiffel Tower.", references) == 1.0
    assert squad_exact_match("Paris", references) == 0.0
    assert np.isclose(squad_f1("Eiffel", references), 2 / 3)


def test_group_split_keeps_contexts_disjoint():
    records = [
        {"context": f"context {group}", "id": f"{group}-{repeat}"}
        for group in range(20)
        for repeat in range(2)
    ]
    train, validation, test = fixed_group_split(
        records,
        {
            "validation_fraction": 0.2,
            "test_fraction": 0.2,
            "split_seed": 42,
        },
    )
    context_sets = [
        {records[index]["context"] for index in indices}
        for indices in (train, validation, test)
    ]
    assert context_sets[0].isdisjoint(context_sets[1])
    assert context_sets[0].isdisjoint(context_sets[2])
    assert context_sets[1].isdisjoint(context_sets[2])


def test_training_threshold_is_nondegenerate():
    values = np.asarray([0.0, 0.0, 0.63, 0.63, 1.09, 1.09])
    threshold = best_train_threshold(values)
    labels = values >= threshold
    assert labels.any() and (~labels).any()


def test_stability_score_summary():
    summary = summarize_scores([0.4, 0.6, 0.7, 0.8])
    assert summary["count"] == 4
    assert np.isclose(summary["median"], 0.65)
    assert np.isclose(summary["fraction_above_0.5"], 0.75)


def test_rank_stratified_selection_is_balanced_and_reproducible():
    entropy = np.arange(20, dtype=np.float64)
    ids = [f"id-{index}" for index in range(20)]
    first = select_rank_stratified(entropy, ids, strata=4, per_stratum=2, seed=7)
    second = select_rank_stratified(entropy, ids, strata=4, per_stratum=2, seed=7)
    assert first == second
    assert len(first) == 8
    assert {stratum: sum(row["stratum"] == stratum for row in first) for stratum in range(4)} == {
        0: 2,
        1: 2,
        2: 2,
        3: 2,
    }


def test_prefix_comparison_detects_one_label_flip():
    entropy = {
        5: np.asarray([0.0, 0.7, 0.2, 0.8]),
        10: np.asarray([0.0, 0.7, 0.6, 0.8]),
        20: np.asarray([0.0, 0.7, 0.7, 0.8]),
    }
    result = compare_prefixes(
        entropy,
        strata=np.asarray([0, 0, 1, 1]),
        threshold=0.5,
        bootstrap_samples=20,
        bootstrap_seed=3,
    )
    assert np.isclose(result["5_vs_20"]["label_agreement"], 0.75)
    assert result["5_vs_20"]["label_flips"]["low_to_high"] == 1
    assert np.isclose(result["10_vs_20"]["label_agreement"], 1.0)
