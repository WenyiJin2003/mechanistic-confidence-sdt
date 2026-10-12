import numpy as np
import pytest

from experiments.diverse_pairs_multilayer_v1.src.readouts import (
    MeanDifferenceReadout,
    PairedLayerReadouts,
    grouped_bootstrap_accuracy,
    grouped_bootstrap_difference,
    paired_accuracy,
)


def synthetic(seed=7, n=80, layers=3, features=5):
    rng = np.random.default_rng(seed)
    base = rng.normal(size=(n, layers, features))
    delta = rng.normal(scale=0.2, size=(n, layers, features))
    delta[:, :, 0] += 1.5
    X = np.stack([base + delta / 2, base - delta / 2], axis=1)
    return X, np.arange(n) // 2


def test_paired_logistic_separates_and_has_expected_shapes():
    X, groups = synthetic()
    model = PairedLayerReadouts().fit(X, groups)
    raw = model.decision_function(X)
    scaled = model.scaled_scores(X)
    assert raw.shape == (len(X), 2, X.shape[2])
    assert model.equal_scores(X).shape == (len(X), 2)
    assert np.mean(model.equal_scores(X)[:, 0] > model.equal_scores(X)[:, 1]) > 0.9
    assert np.mean(raw[:, 0, :] > raw[:, 1, :]) > 0.9
    assert all(m.fit_intercept is False for m in model.models_)
    assert np.allclose(model.models_[0].classes_, [0, 1])


def test_frozen_feature_and_score_transforms_ignore_evaluation_data():
    X, groups = synthetic()
    model = PairedLayerReadouts().fit(X[:50], groups[:50])
    means = np.array([s.mean_.copy() for s in model.scalers_])
    train_means, train_stds = model.train_score_mean_.copy(), model.train_score_std_.copy()
    altered = X[50:].copy() * 1000 + 321
    model.scaled_scores(altered)
    assert np.array_equal(means, np.array([s.mean_ for s in model.scalers_]))
    assert np.array_equal(train_means, model.train_score_mean_)
    assert np.array_equal(train_stds, model.train_score_std_)


def test_constant_scores_are_zero_and_flagged():
    X = np.zeros((8, 2, 2, 3))
    model = PairedLayerReadouts().fit(X)
    assert model.zero_std_layers_.all()
    assert np.array_equal(model.scaled_scores(X), np.zeros((8, 2, 2)))


def test_mean_difference_baseline_shape_and_direction():
    X, groups = synthetic()
    model = MeanDifferenceReadout().fit(X, groups)
    assert model.decision_function(X).shape == (len(X), 2, X.shape[2])
    assert model.equal_scores(X).shape == (len(X), 2)
    assert model.equal_scores(X)[:, 0].mean() > model.equal_scores(X)[:, 1].mean()


def test_pair_order_and_exact_ties_count_half():
    scores = np.array([[2, 0], [0, 2], [3, 3], [-1, -1]])
    assert paired_accuracy(scores) == pytest.approx(0.5)
    assert paired_accuracy(scores[:, ::-1]) == pytest.approx(0.5)


def test_group_bootstrap_is_reproducible_and_resamples_whole_groups():
    # Every member of a group has the same outcome, so cluster resampling has
    # only two possible bootstrap statistics; row-wise resampling would not.
    scores = np.array([[1, 0]] * 4 + [[0, 1]] * 4, dtype=float)
    groups = np.array(["a"] * 4 + ["b"] * 4)
    result = grouped_bootstrap_accuracy(scores, groups, n_boot=500, seed=3)
    assert set(np.unique(result["samples"])) <= {0.0, 0.5, 1.0}
    again = grouped_bootstrap_accuracy(scores, groups, n_boot=500, seed=3)
    assert np.array_equal(result["samples"], again["samples"])
    reverse = grouped_bootstrap_accuracy(scores[:, ::-1], groups, n_boot=500, seed=3)
    assert np.allclose(result["samples"] + reverse["samples"], 1.0)


def test_difference_bootstrap_uses_same_sampled_groups():
    a = np.array([[0, 1]] * 4 + [[1, 0]] * 4, float)
    b = a.copy()
    groups = np.array(["a"] * 4 + ["b"] * 4)
    result = grouped_bootstrap_difference(a, b, groups, n_boot=200, seed=12)
    assert result["estimate"] == 0
    assert np.array_equal(result["samples"], np.zeros(200))


def test_group_bootstrap_weights_groups_equally_when_sizes_differ():
    # One correct pair in group a and nine incorrect pairs in group b.
    scores = np.array([[1, 0]] + [[0, 1]] * 9, float)
    groups = np.array(["a"] + ["b"] * 9)
    result = grouped_bootstrap_accuracy(scores, groups, n_boot=20, seed=2)
    assert result["estimate"] == pytest.approx(0.5)
    assert set(np.unique(result["samples"])) <= {0.0, 0.5, 1.0}


@pytest.mark.parametrize("bad", [np.zeros((5, 2, 3)), np.zeros((5, 3, 2, 3)),
                                   np.full((5, 2, 1, 2), np.nan)])
def test_invalid_activation_shapes_and_values_rejected(bad):
    with pytest.raises(ValueError):
        PairedLayerReadouts().fit(bad)


def test_group_length_validation():
    X, _ = synthetic()
    with pytest.raises(ValueError, match="groups"):
        PairedLayerReadouts().fit(X, [1, 2])
