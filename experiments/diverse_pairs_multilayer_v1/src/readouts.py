"""CPU readouts for paired confident/hedged multilayer activations.

All fitted transforms use training responses only. The input pair order is
fixed: column 0 is confident and column 1 is hedged.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler


def _validate_x(X: np.ndarray, *, fitted_layers: int | None = None) -> np.ndarray:
    X = np.asarray(X, dtype=np.float64)
    if X.ndim != 4 or X.shape[1] != 2:
        raise ValueError("X must have shape [N_pairs, 2, L, D]")
    if X.shape[0] == 0 or X.shape[2] == 0 or X.shape[3] == 0:
        raise ValueError("X must contain pairs, layers, and features")
    if not np.isfinite(X).all():
        raise ValueError("X must contain only finite values")
    if fitted_layers is not None and X.shape[2] != fitted_layers:
        raise ValueError(f"expected {fitted_layers} layers, got {X.shape[2]}")
    return X


def _validate_groups(groups: Any, n: int) -> np.ndarray:
    if groups is None:
        return np.arange(n)
    g = np.asarray(groups)
    if g.ndim != 1 or len(g) != n:
        raise ValueError("groups must be a one-dimensional ID per source pair")
    if any(x is None for x in g):
        raise ValueError("group IDs may not be None")
    return g


@dataclass
class PairedLayerReadouts:
    """One symmetric paired logistic classifier per layer, fit on CPU."""

    C: float = 0.01
    max_iter: int = 2000

    def fit(self, X: np.ndarray, groups: Any = None) -> "PairedLayerReadouts":
        X = _validate_x(X)
        self.groups_ = _validate_groups(groups, len(X)).copy()
        self.n_layers_, self.n_features_ = X.shape[2:]
        self.scalers_ = []
        self.models_ = []
        self.train_score_mean_ = np.empty(self.n_layers_)
        self.train_score_std_ = np.empty(self.n_layers_)
        self.zero_std_layers_ = np.zeros(self.n_layers_, dtype=bool)
        weights = np.full(2 * len(X), 0.5)
        for layer in range(self.n_layers_):
            # Fit feature scaling on both train responses, each with equal mass.
            scaler = StandardScaler()
            train = X[:, :, layer, :].reshape(-1, self.n_features_)
            scaler.fit(train)
            z = scaler.transform(train).reshape(len(X), 2, self.n_features_)
            delta = z[:, 0, :] - z[:, 1, :]
            symmetric = np.concatenate([delta, -delta], axis=0)
            labels = np.concatenate([np.ones(len(X)), np.zeros(len(X))])
            model = LogisticRegression(C=self.C, fit_intercept=False,
                                       max_iter=self.max_iter, solver="lbfgs")
            model.fit(symmetric, labels, sample_weight=weights)
            self.scalers_.append(scaler)
            self.models_.append(model)
            train_scores = model.decision_function(z.reshape(-1, self.n_features_))
            mean = float(train_scores.mean())
            std = float(train_scores.std(ddof=0))
            self.train_score_mean_[layer] = mean
            self.train_score_std_[layer] = std
            self.zero_std_layers_[layer] = std < 1e-12
        return self

    def _require_fit(self):
        if not hasattr(self, "models_"):
            raise RuntimeError("fit must be called first")

    def _raw_scores(self, X: np.ndarray) -> np.ndarray:
        self._require_fit()
        X = _validate_x(X, fitted_layers=self.n_layers_)
        out = np.empty((len(X), 2, self.n_layers_))
        for l, (scaler, model) in enumerate(zip(self.scalers_, self.models_)):
            z = scaler.transform(X[:, :, l, :].reshape(-1, self.n_features_))
            out[:, :, l] = model.decision_function(z).reshape(len(X), 2)
        return out

    def decision_function(self, X: np.ndarray) -> np.ndarray:
        """Return per-response layer scores with shape [N_pairs, 2, L]."""
        return self._raw_scores(X)

    def scaled_scores(self, X: np.ndarray) -> np.ndarray:
        """Standardize each layer using only its training response scores."""
        raw = self.decision_function(X)
        out = np.zeros_like(raw)
        good = ~self.zero_std_layers_
        out[:, :, good] = ((raw[:, :, good] - self.train_score_mean_[good]) /
                           self.train_score_std_[good])
        return out

    def equal_scores(self, X: np.ndarray) -> np.ndarray:
        """Equal-weight mean of frozen standardized layer scores [N, 2]."""
        return self.scaled_scores(X).mean(axis=2)


@dataclass
class MeanDifferenceReadout:
    """Baseline using the mean train confident-minus-hedged feature vector."""

    def fit(self, X: np.ndarray, groups: Any = None) -> "MeanDifferenceReadout":
        X = _validate_x(X)
        self.groups_ = _validate_groups(groups, len(X)).copy()
        self.n_layers_, self.n_features_ = X.shape[2:]
        self.scalers_ = []
        self.weights_ = []
        self.means_ = []
        self.stds_ = []
        for layer in range(self.n_layers_):
            scaler = StandardScaler().fit(X[:, :, layer, :].reshape(-1, self.n_features_))
            z = scaler.transform(X[:, :, layer, :].reshape(-1, self.n_features_))
            z = z.reshape(len(X), 2, self.n_features_)
            w = (z[:, 0, :] - z[:, 1, :]).mean(axis=0)
            self.scalers_.append(scaler)
            self.weights_.append(w)
            s = z @ w
            scores = s.reshape(-1)
            self.means_.append(float(scores.mean()))
            self.stds_.append(float(scores.std()))
        self.means_ = np.asarray(self.means_)
        self.stds_ = np.asarray(self.stds_)
        self.zero_std_layers_ = self.stds_ < 1e-12
        return self

    def decision_function(self, X: np.ndarray) -> np.ndarray:
        if not hasattr(self, "weights_"):
            raise RuntimeError("fit must be called first")
        X = _validate_x(X, fitted_layers=self.n_layers_)
        out = np.empty((len(X), 2, self.n_layers_))
        for l, (scaler, w) in enumerate(zip(self.scalers_, self.weights_)):
            z = scaler.transform(X[:, :, l, :].reshape(-1, self.n_features_))
            z = z.reshape(len(X), 2, self.n_features_)
            out[:, :, l] = z @ w
        return out

    def scaled_scores(self, X: np.ndarray) -> np.ndarray:
        raw = self.decision_function(X)
        out = np.zeros_like(raw)
        good = ~self.zero_std_layers_
        out[:, :, good] = ((raw[:, :, good] - self.means_[good]) / self.stds_[good])
        return out

    def equal_scores(self, X: np.ndarray) -> np.ndarray:
        return self.scaled_scores(X).mean(axis=2)


def paired_accuracy(scores: np.ndarray) -> float:
    """Fraction where confident score exceeds hedged; exact ties count 0.5."""
    scores = np.asarray(scores, dtype=float)
    if scores.ndim != 2 or scores.shape[1] != 2 or not np.isfinite(scores).all():
        raise ValueError("scores must be finite [N_pairs, 2]")
    if len(scores) == 0:
        raise ValueError("scores must contain at least one pair")
    delta = scores[:, 0] - scores[:, 1]
    return float((np.count_nonzero(delta > 0) + 0.5 * np.count_nonzero(delta == 0)) / len(delta))


def grouped_bootstrap_accuracy(scores: np.ndarray, groups: Any, *, n_boot: int = 2000,
                                seed: int = 0, confidence: float = 0.95) -> dict[str, Any]:
    """Bootstrap source groups, retaining every pair in a sampled group."""
    scores = np.asarray(scores, dtype=float)
    if scores.ndim != 2 or scores.shape[1] != 2 or len(scores) == 0 or not np.isfinite(scores).all():
        raise ValueError("scores must be nonempty finite [N_pairs, 2]")
    g = _validate_groups(groups, len(scores))
    unique = np.unique(g)
    if len(unique) < 2:
        raise ValueError("at least two distinct groups are needed for bootstrap")
    if n_boot < 1 or not 0 < confidence < 1:
        raise ValueError("n_boot must be positive and confidence must be in (0, 1)")
    indices = {key: np.flatnonzero(g == key) for key in unique}
    rng = np.random.default_rng(seed)
    group_scores = {key: paired_accuracy(scores[indices[key]]) for key in unique}
    estimate = float(np.mean(list(group_scores.values())))
    vals = np.empty(n_boot)
    for b in range(n_boot):
        sampled = rng.choice(unique, size=len(unique), replace=True)
        vals[b] = float(np.mean([group_scores[key] for key in sampled]))
    alpha = (1 - confidence) / 2
    return {"estimate": estimate, "samples": vals,
            "ci": tuple(np.quantile(vals, [alpha, 1 - alpha])),
            "groups": int(len(unique)), "n_boot": int(n_boot)}


def grouped_bootstrap_difference(scores_a: np.ndarray, scores_b: np.ndarray,
                                 groups: Any, *, n_boot: int = 2000,
                                 seed: int = 0, confidence: float = 0.95) -> dict[str, Any]:
    """Paired accuracy(B - A) interval using identical resampled source groups."""
    a, b = np.asarray(scores_a, float), np.asarray(scores_b, float)
    if a.shape != b.shape or a.ndim != 2 or a.shape[1] != 2:
        raise ValueError("scores_a and scores_b must have matching [N_pairs, 2] shapes")
    g = _validate_groups(groups, len(a))
    if not np.isfinite(a).all() or not np.isfinite(b).all() or n_boot < 1 or not 0 < confidence < 1:
        raise ValueError("scores must be finite, n_boot positive, and confidence in (0, 1)")
    unique = np.unique(g)
    if len(unique) < 2:
        raise ValueError("at least two distinct groups are needed for bootstrap")
    indices = {key: np.flatnonzero(g == key) for key in unique}
    group_differences = {key: paired_accuracy(b[indices[key]]) - paired_accuracy(a[indices[key]])
                         for key in unique}
    rng = np.random.default_rng(seed)
    vals = np.empty(n_boot)
    for i in range(n_boot):
        sampled = rng.choice(unique, size=len(unique), replace=True)
        vals[i] = float(np.mean([group_differences[key] for key in sampled]))
    alpha = (1 - confidence) / 2
    return {"estimate": float(np.mean(list(group_differences.values()))), "samples": vals,
            "ci": tuple(np.quantile(vals, [alpha, 1 - alpha])),
            "groups": int(len(unique)), "n_boot": int(n_boot)}
