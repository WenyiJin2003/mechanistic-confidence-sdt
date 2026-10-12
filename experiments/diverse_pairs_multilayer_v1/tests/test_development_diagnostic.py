import sys
from pathlib import Path

import numpy as np
import pytest

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE / "src"))
from readouts import paired_accuracy
from run_development_diagnostic import cv_hidden_predictions, cv_text_predictions, interval, make_folds


def synthetic(seed=9, n=50, layers=4, features=8):
    rng = np.random.default_rng(seed)
    base = rng.normal(size=(n, layers, features))
    direction = np.zeros((layers, features)); direction[:, 0] = 2
    X = np.stack([base + direction / 2, base - direction / 2], axis=1)
    tasks = np.asarray([f"task-{i % 5}" for i in range(n)])
    groups = np.asarray([f"g-{i}" for i in range(n)])
    return X, tasks, groups


def test_folds_are_complete_and_group_disjoint():
    _, tasks, groups = synthetic()
    seen = []
    for train, test in make_folds(tasks, groups):
        assert not set(groups[train]) & set(groups[test])
        seen.extend(test.tolist())
    assert sorted(seen) == list(range(len(groups)))


def test_cross_validated_hidden_predictions_have_correct_direction():
    X, tasks, groups = synthetic()
    layers, ensemble, folds = cv_hidden_predictions(X, tasks, groups)
    assert layers.shape == (len(X), 2, X.shape[2])
    assert ensemble.shape == (len(X), 2)
    assert set(folds) == set(range(5))
    assert paired_accuracy(ensemble) > .9


def test_random_training_orientations_reduce_signal():
    X, tasks, groups = synthetic()
    rng = np.random.default_rng(11)
    orientation = rng.random(len(X)) < .5
    _, shuffled, _ = cv_hidden_predictions(X, tasks, groups, orientations=orientation)
    assert paired_accuracy(shuffled) < .8


def test_duplicate_groups_refused():
    X, tasks, groups = synthetic()
    groups[1] = groups[0]
    with pytest.raises(ValueError, match="independent"):
        cv_hidden_predictions(X, tasks, groups)


def test_text_baseline_uses_training_folds_and_returns_paired_scores():
    _, tasks, groups = synthetic()
    pairs = [{"confident_response": f"The answer is certainly item {i}.",
              "hedged_response": f"I might be mistaken, but the answer may be item {i}."}
             for i in range(len(groups))]
    scores = cv_text_predictions(pairs, tasks, groups)
    assert scores.shape == (len(pairs), 2)
    assert np.isfinite(scores).all()
    assert paired_accuracy(scores) > .9


def test_interval_reports_exact_pair_outcomes():
    scores = np.asarray([[2, 1], [1, 1], [0, 1]], dtype=float)
    result = interval(scores, np.asarray(["a", "b", "c"]), seed=1, draws=20)
    assert (result["wins"], result["ties"], result["losses"]) == (1, 1, 1)
    assert result["estimate"] == .5
