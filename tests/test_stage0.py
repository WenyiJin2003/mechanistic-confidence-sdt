import numpy as np

from stage0.pipeline import (
    best_train_threshold,
    cluster_entropy,
    fixed_group_split,
    normalize_answer,
    squad_exact_match,
    squad_f1,
)


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
