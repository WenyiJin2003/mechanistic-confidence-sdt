"""Source-bundled, cache-only audit of certainty and correctness readouts.

All estimators use v1 train A/B sources only. Test-C and v2 are evaluation
data. Projection removes the estimated subspace from a readout, rather than
claiming to remove every form of correctness information from a representation.
"""
from __future__ import annotations

import hashlib
from collections import defaultdict
from typing import Any

import numpy as np

REPRESENTATIONS = {
    "layer14_boundary": (0, 0),
    "layer14_final_content": (0, 1),
    "layer14_response_mean": (0, 2),
    "layer23_boundary": (1, 0),
}
FAMILIES = ("A", "B", "C")
STYLES = ("confident", "hedged")
CORRECTNESS = ("correct", "incorrect")


def _unit(values):
    values = np.asarray(values, dtype=np.float64)
    norms = np.linalg.norm(values, axis=-1, keepdims=True)
    return np.divide(values, norms, out=np.zeros_like(values), where=norms > 1e-12)


def _order(values):
    values = np.asarray(values, dtype=np.float64)
    return np.where(values > 1e-12, 1., np.where(values < -1e-12, 0., .5))


def _seed(seed, label):
    return (int(seed) + int(hashlib.sha256(str(label).encode()).hexdigest()[:8], 16)) % (2**32 - 1)


def _interval(values):
    low, high = np.percentile(np.asarray(values), [2.5, 97.5])
    return {"lower": float(low), "upper": float(high)}


def _distribution(values):
    values = np.asarray(values, dtype=np.float64)
    return {"mean": float(values.mean()), "median": float(np.median(values)),
            "minimum": float(values.min()), "maximum": float(values.max()),
            "percentile_95": _interval(values), "n_repetitions": len(values)}


def _bootstrap_weights(n, samples, seed):
    if n < 1 or samples < 1:
        raise ValueError("Source bootstrap requires positive source and sample counts")
    draws = np.random.default_rng(seed).integers(n, size=(samples, n))
    offsets = np.arange(samples)[:, None] * n
    return np.bincount((draws + offsets).ravel(), minlength=samples * n).reshape(samples, n) / n


def source_metric(margins, source_ids, samples=1000, seed=20261007):
    """Average comparisons inside each source, then resample entire sources."""
    margins = np.asarray(margins, dtype=np.float64)
    if margins.ndim == 1:
        margins = margins[:, None]
    if margins.ndim != 2 or len(margins) != len(source_ids) or not len(margins):
        raise ValueError("Margins must have one complete bundle per source")
    if len(set(source_ids)) != len(source_ids) or not np.isfinite(margins).all():
        raise ValueError("Source bundles must be unique and finite")
    weights = _bootstrap_weights(len(margins), samples, seed)
    accuracy = _order(margins).mean(axis=1)
    mean_margin = margins.mean(axis=1)
    return {"accuracy": float(accuracy.mean()), "bootstrap_95": _interval(weights @ accuracy),
            "mean_pair_margin": float(mean_margin.mean()),
            "margin_bootstrap_95": _interval(weights @ mean_margin),
            "n_sources": len(margins), "n_pairs": int(margins.size),
            "tie_fraction": float(np.mean(np.abs(margins) <= 1e-12))}


def paired_change(raw, projected, source_ids, samples=1000, seed=20261007):
    raw, projected = np.asarray(raw), np.asarray(projected)
    if raw.shape != projected.shape:
        raise ValueError("Paired changes need identical comparison shapes")
    if raw.ndim == 1:
        raw, projected = raw[:, None], projected[:, None]
    weights = _bootstrap_weights(len(source_ids), samples, seed)
    accuracy_change = (_order(projected) - _order(raw)).mean(axis=1)
    margin_change = (projected - raw).mean(axis=1)
    return {"accuracy_difference": float(accuracy_change.mean()),
            "accuracy_difference_bootstrap_95": _interval(weights @ accuracy_change),
            "mean_margin_difference": float(margin_change.mean()),
            "margin_difference_bootstrap_95": _interval(weights @ margin_change),
            "n_sources": len(source_ids), "n_pairs": int(raw.size),
            "source_paired": True, "normalization": "original confidence unit vector; residual is not renormalized"}


def v1_bundles(rows, hidden):
    """Return a [source,family,correctness,certainty] row-index cube."""
    hidden = np.asarray(hidden)
    if hidden.ndim != 4 or hidden.shape[:3] != (len(rows), 2, 4) or not np.isfinite(hidden).all():
        raise ValueError("Expected finite hidden [row,2,4,dimension]")
    if not rows:
        raise ValueError("Empty v1 cache")
    ids = [str(row["variant_id"]) for row in rows]
    if len(set(ids)) != len(ids):
        raise ValueError("Duplicate variant IDs")
    id_lookup = dict(zip(ids, range(len(rows))))
    by_source = defaultdict(dict)
    metadata = {}
    for index, row in enumerate(rows):
        source = str(row["source_id"])
        split, domain = row["split"], row["domain"]
        if split not in {"train", "validation", "test"}:
            raise ValueError("Unknown source split")
        if source in metadata and metadata[source] != (split, domain):
            raise ValueError("Source leakage or inconsistent domain")
        metadata[source] = (split, domain)
        cell = (row["rewrite_family"], row["correctness"], row["certainty"])
        if cell[0] not in FAMILIES or cell[1] not in CORRECTNESS or cell[2] not in STYLES:
            raise ValueError("Unknown v1 condition")
        if cell in by_source[source]:
            raise ValueError("Duplicate source condition")
        by_source[source][cell] = index
        partner = id_lookup.get(str(row["paired_variant_id"]))
        if partner is None:
            raise ValueError("Missing certainty partner")
        other = rows[partner]
        if str(other["paired_variant_id"]) != ids[index] or any(
            other[key] != row[key] for key in ("source_id", "domain", "split", "rewrite_family", "correctness")
        ) or other["certainty"] == row["certainty"]:
            raise ValueError("Invalid certainty pair links")
    source_ids = sorted(by_source)
    cube = []
    for source in source_ids:
        if len(by_source[source]) != 12:
            raise ValueError("Incomplete correctness × certainty × family source bundle")
        cube.append([[[by_source[source][(family, correctness, style)]
                       for style in STYLES] for correctness in CORRECTNESS] for family in FAMILIES])
    metadata_rows = [{"source_id": source, "split": metadata[source][0], "domain": metadata[source][1]}
                     for source in source_ids]
    return metadata_rows, np.asarray(cube, dtype=np.int64)


def contrast_bundles(features, cube):
    cells = np.asarray(features, dtype=np.float64)[cube]
    certainty = cells[:, :, :, 0] - cells[:, :, :, 1]
    correctness = cells[:, :, 0] - cells[:, :, 1]
    return certainty, correctness


def training_directions(rows, hidden, frozen=None):
    """Export all four source-balanced train-A/B directions without evaluation."""
    metadata, cube = v1_bundles(rows, hidden)
    train = np.asarray([i for i, row in enumerate(metadata) if row["split"] == "train"])
    if not len(train):
        raise ValueError("No training sources")
    output = {}
    for name, (layer, position) in REPRESENTATIONS.items():
        certainty, correctness = contrast_bundles(hidden[:, layer, position], cube)
        fitted = _unit(certainty[train, :2].mean(axis=(0, 1, 2)))
        if frozen is not None and not np.allclose(fitted, frozen[name], rtol=1e-8, atol=1e-10):
            raise ValueError(f"Frozen v1 confidence mismatch for {name}")
        output[name] = np.asarray(frozen[name]).copy() if frozen is not None else fitted
        output[name + "_correctness"] = _unit(correctness[train, :2].mean(axis=(0, 1, 2)))
    return output


def _cross_readout(certainty, correctness, confidence_direction, correctness_direction,
                   source_ids, samples, seed):
    output = {}
    for readout, direction in (("confidence", confidence_direction), ("correctness", correctness_direction)):
        entry = {}
        for target, contrasts, labels, strata in (
            ("certainty", certainty, CORRECTNESS, "by_correctness"),
            ("correctness", correctness, STYLES, "by_certainty_style"),
        ):
            margins = contrasts @ direction
            metric = source_metric(margins, source_ids, samples, seed)
            metric[strata] = {label: source_metric(margins[:, i:i+1], source_ids, samples, seed)
                              for i, label in enumerate(labels)}
            entry[target] = metric
        output[readout] = entry
    return output


def _joint_refit_bootstrap(train_certainty, train_correctness, test_certainty, test_correctness,
                          samples, seed):
    weights = _bootstrap_weights(len(train_certainty), samples, _seed(seed, "train"))
    test_weights = _bootstrap_weights(len(test_certainty), samples, _seed(seed, "test"))
    confidence = _unit(weights @ train_certainty)
    correctness = _unit(weights @ train_correctness)
    cosines = np.sum(confidence * correctness, axis=1)
    output = {"n_repetitions": samples, "unit": "whole source bundles, independently resampled train and test",
              "both_directions_refitted": True, "cosine_bootstrap_95": _interval(cosines)}
    for readout, directions in (("confidence", confidence), ("correctness", correctness)):
        output[readout] = {}
        for target, contrasts in (("certainty", test_certainty), ("correctness", test_correctness)):
            margins = np.einsum("skd,bd->bsk", contrasts, directions, optimize=True)
            accuracies = np.sum(test_weights * _order(margins).mean(axis=2), axis=1)
            means = np.sum(test_weights * margins.mean(axis=2), axis=1)
            output[readout][target] = {"accuracy_bootstrap_95": _interval(accuracies),
                                       "margin_bootstrap_95": _interval(means)}
            if target == "certainty":
                interaction = np.sum(test_weights * (margins[:, :, 0] - margins[:, :, 1]), axis=1)
                output[readout][target]["correct_minus_incorrect_margin_interaction_95"] = _interval(interaction)
    residual = confidence - cosines[:, None] * correctness
    raw = np.einsum("skd,bd->bsk", test_certainty, confidence, optimize=True)
    projected = np.einsum("skd,bd->bsk", test_certainty, residual, optimize=True)
    output["rank1_projection"] = {
        "certainty_accuracy_change_bootstrap_95": _interval(
            np.sum(test_weights * (_order(projected) - _order(raw)).mean(axis=2), axis=1)),
        "certainty_margin_change_bootstrap_95": _interval(
            np.sum(test_weights * (projected - raw).mean(axis=2), axis=1))}
    return output


def _geometry(train_confidence, train_correctness, confidence, correctness, samples, halves, seed):
    rng = np.random.default_rng(_seed(seed, "split_half"))
    n = len(train_confidence)
    confidence_cosines, correctness_cosines, between = [], [], []
    for _ in range(halves):
        order = rng.permutation(n)
        first, second = order[:n//2], order[n//2:]
        a, b = _unit(train_confidence[first].mean(axis=0)), _unit(train_confidence[second].mean(axis=0))
        c, d = _unit(train_correctness[first].mean(axis=0)), _unit(train_correctness[second].mean(axis=0))
        confidence_cosines.append(a @ b)
        correctness_cosines.append(c @ d)
        between.extend((a @ c, b @ d))
    cos = float(confidence @ correctness)
    return {"cosine": cos, "angle_degrees": float(np.degrees(np.arccos(np.clip(cos, -1, 1)))),
            "confidence_squared_overlap": cos**2, "residual_norm": float(np.sqrt(max(0., 1 - cos**2))),
            "confidence_train_source_mean_norm": float(np.linalg.norm(train_confidence.mean(axis=0))),
            "correctness_train_source_mean_norm": float(np.linalg.norm(train_correctness.mean(axis=0))),
            "split_half": {"n_source_halves": [n//2, n-n//2],
                "confidence_reliability": _distribution(confidence_cosines),
                "correctness_reliability": _distribution(correctness_cosines),
                "within_half_cross_cosines": _distribution(between)},
            "estimator": "Euclidean source-balanced differences; no whitening or test-dependent axis selection"}


def _interaction(certainty_margins, source_ids, samples, seed):
    source_differences = certainty_margins[:, 0] - certainty_margins[:, 1]
    weights = _bootstrap_weights(len(source_ids), samples, seed)
    accuracy_differences = _order(certainty_margins[:, 0]) - _order(certainty_margins[:, 1])
    return {"contrast": "certainty margin for correct content minus certainty margin for incorrect content",
            "mean_margin_interaction": float(source_differences.mean()),
            "margin_interaction_bootstrap_95": _interval(weights @ source_differences),
            "accuracy_interaction": float(accuracy_differences.mean()),
            "accuracy_interaction_bootstrap_95": _interval(weights @ accuracy_differences),
            "n_sources": len(source_ids), "source_paired": True}


def _domain_audit(metadata, train_indices, certainty, correctness, samples, seed):
    output = {}
    domains = sorted({row["domain"] for row in metadata})
    for fitted_domain in domains:
        train = [i for i in train_indices if metadata[i]["domain"] == fitted_domain]
        confidence = _unit(certainty[train, :2].mean(axis=(0, 1, 2)))
        correct = _unit(correctness[train, :2].mean(axis=(0, 1, 2)))
        tests = {}
        for evaluated_domain in domains:
            test = [i for i, row in enumerate(metadata) if row["split"] == "test" and row["domain"] == evaluated_domain]
            ids = [metadata[i]["source_id"] for i in test]
            tests[evaluated_domain] = _cross_readout(certainty[test, 2], correctness[test, 2], confidence, correct, ids, samples, seed)
        other = [i for i, row in enumerate(metadata) if row["split"] == "test" and row["domain"] != fitted_domain]
        output[fitted_domain] = {"n_train_sources": len(train), "train_families": ["A", "B"],
            "cosine": float(confidence @ correct), "test_C_by_domain": tests,
            "test_C_other_domains": _cross_readout(certainty[other, 2], correctness[other, 2], confidence, correct,
                [metadata[i]["source_id"] for i in other], samples, seed)}
    return output


def v2_contrasts(rows, hidden):
    """Validate and gather complete new style/evidence source bundles."""
    hidden = np.asarray(hidden)
    if hidden.ndim != 4 or hidden.shape[:3] != (len(rows), 2, 4) or not np.isfinite(hidden).all():
        raise ValueError("Invalid v2 hidden states")
    variant_ids = [str(row["variant_id"]) for row in rows]
    if len(set(variant_ids)) != len(variant_ids):
        raise ValueError("Duplicate v2 variant IDs")
    id_lookup = dict(zip(variant_ids, range(len(rows))))
    by_source = defaultdict(list)
    for i, row in enumerate(rows):
        if row["split"] != "test":
            raise ValueError("v2 must be evaluation only")
        by_source[str(row["source_id"])].append(i)
    source_ids = sorted(by_source)
    endpoints = {"natural_style": [], "natural_correctness": []}
    for fmt in ("qa", "document"):
        for other in ("omitted", "conflicting"):
            endpoints[f"neutral_{fmt}_supported_vs_{other}"] = []
    for source in source_ids:
        indices = by_source[source]
        if len(indices) != 10:
            raise ValueError("Incomplete v2 source bundle")
        if len({rows[i]["fact_type"] for i in indices}) != 1:
            raise ValueError("Inconsistent v2 fact type")
        style = {(rows[i]["correctness"], rows[i]["certainty"]): i for i in indices
                 if rows[i]["experiment"] == "natural_style"}
        if set(style) != {(correct, certainty) for correct in CORRECTNESS for certainty in STYLES}:
            raise ValueError("Incomplete v2 natural style cells")
        for correct in CORRECTNESS:
            a, b = style[(correct, "confident")], style[(correct, "hedged")]
            if id_lookup.get(str(rows[a]["paired_variant_id"])) != b or id_lookup.get(str(rows[b]["paired_variant_id"])) != a:
                raise ValueError("Invalid v2 natural-style pair links")
        endpoints["natural_style"].append([(style[(correct, "confident")], style[(correct, "hedged")]) for correct in CORRECTNESS])
        endpoints["natural_correctness"].append([(style[("correct", certainty)], style[("incorrect", certainty)]) for certainty in STYLES])
        for fmt in ("qa", "document"):
            neutral = {rows[i]["condition"]: i for i in indices
                       if rows[i]["experiment"] == "neutral_evidence" and rows[i]["format"] == fmt}
            if set(neutral) != {"supported", "omitted", "conflicting"}:
                raise ValueError("Incomplete v2 evidence cells")
            group = [rows[i] for i in neutral.values()]
            for key in ("response_ids", "response_text", "token_count", "char_count", "prompt_token_count"):
                if any(row[key] != group[0][key] for row in group[1:]):
                    raise ValueError(f"v2 neutral {key} differ within source/format")
            for other in ("omitted", "conflicting"):
                endpoints[f"neutral_{fmt}_supported_vs_{other}"].append([(neutral["supported"], neutral[other])])
    return source_ids, {name: np.asarray(pairs, dtype=int) for name, pairs in endpoints.items()}


def _endpoint_contrasts(features, endpoints):
    return {name: features[pairs[:, :, 0]] - features[pairs[:, :, 1]] for name, pairs in endpoints.items()}


def _projection_endpoints(contrasts, raw_direction, residual, correctness, source_ids, samples, seed):
    output = {}
    for name, differences in contrasts.items():
        raw, projected = differences @ raw_direction, differences @ residual
        entry = {"raw": source_metric(raw, source_ids, samples, seed),
                 "projected_common_scale": source_metric(projected, source_ids, samples, seed),
                 "correctness_readout": source_metric(differences @ correctness, source_ids, samples, seed),
                 "projected_minus_raw": paired_change(raw, projected, source_ids, samples, seed)}
        if name == "natural_style":
            entry["by_correctness"] = {label: {
                "raw": source_metric(raw[:, i:i+1], source_ids, samples, seed),
                "projected_common_scale": source_metric(projected[:, i:i+1], source_ids, samples, seed),
                "projected_minus_raw": paired_change(raw[:, i:i+1], projected[:, i:i+1], source_ids, samples, seed)}
                for i, label in enumerate(CORRECTNESS)}
        if name == "natural_correctness":
            entry["by_certainty_style"] = {label: {
                "raw": source_metric(raw[:, i:i+1], source_ids, samples, seed),
                "projected_common_scale": source_metric(projected[:, i:i+1], source_ids, samples, seed),
                "correctness_readout": source_metric((differences @ correctness)[:, i:i+1], source_ids, samples, seed)}
                for i, label in enumerate(STYLES)}
        output[name] = entry
    return output


def _v2_refit_bootstrap(train_certainty, train_correctness, contrasts, samples, seed):
    """Propagate both old training-source and new evaluation-source sampling."""
    train_weights = _bootstrap_weights(len(train_certainty), samples, _seed(seed, "v2_train"))
    n_test = len(next(iter(contrasts.values())))
    test_weights = _bootstrap_weights(n_test, samples, _seed(seed, "v2_test"))
    confidence, correctness = _unit(train_weights @ train_certainty), _unit(train_weights @ train_correctness)
    residual = confidence - np.sum(confidence * correctness, axis=1)[:, None] * correctness
    output = {}
    for name, differences in contrasts.items():
        raw = np.einsum("skd,bd->bsk", differences, confidence, optimize=True)
        projected = np.einsum("skd,bd->bsk", differences, residual, optimize=True)
        correct = np.einsum("skd,bd->bsk", differences, correctness, optimize=True)
        entry = {}
        for label, margins in (("raw", raw), ("projected_common_scale", projected), ("correctness_readout", correct)):
            entry[label] = {"accuracy_bootstrap_95": _interval(np.sum(test_weights * _order(margins).mean(axis=2), axis=1)),
                            "margin_bootstrap_95": _interval(np.sum(test_weights * margins.mean(axis=2), axis=1))}
        entry["projected_minus_raw"] = {
            "accuracy_difference_bootstrap_95": _interval(np.sum(test_weights * (_order(projected) - _order(raw)).mean(axis=2), axis=1)),
            "margin_difference_bootstrap_95": _interval(np.sum(test_weights * (projected - raw).mean(axis=2), axis=1))}
        output[name] = entry
    return {"n_repetitions": samples, "both_directions_refitted": True,
            "unit": "whole v1 training source bundles and independent whole v2 evaluation source bundles", "endpoints": output}


def correctness_subspace(source_contrasts, max_rank=3):
    """Uncentered source-contrast SVD through the small source Gram matrix."""
    matrix = np.asarray(source_contrasts, dtype=np.float64)
    eigenvalues, left = np.linalg.eigh(matrix @ matrix.T / len(matrix))
    order = np.argsort(eigenvalues)[::-1]
    positive = order[eigenvalues[order] > 1e-12]
    selected = positive[:max_rank]
    basis = _unit((left[:, selected].T @ matrix))
    spectrum = np.maximum(eigenvalues[order], 0.)
    return basis, spectrum


def _ridge_contrast_direction(training, alpha):
    """Fixed-alpha paired regression, trained on source mean contrasts only."""
    rms = float(np.sqrt(np.mean(np.sum(training**2, axis=1))))
    if rms <= 1e-12:
        return np.zeros(training.shape[-1])
    scaled = training / rms
    dual = np.linalg.solve(scaled @ scaled.T + alpha * np.eye(len(scaled)), np.ones(len(scaled)))
    return _unit(scaled.T @ dual)


def _subspace_audit(train_correctness, test_certainty, test_correctness, confidence,
                    correctness, test_ids, v2, v2_ids, config, samples, seed):
    settings = config.get("analysis", {})
    ranks = tuple(int(value) for value in settings.get("subspace_ranks", (1, 2, 3)))
    basis, spectrum = correctness_subspace(train_correctness, max(ranks))
    output = {"construction": "uncentered SVD of 72 train-A/B source-balanced correctness contrasts via source Gram matrix",
              "available_rank": len(basis), "total_contrast_energy": float(spectrum.sum()),
              "leading_eigenvalues": spectrum[:10].tolist(), "rank_candidates": {},
              "interpretation": "Readout projection removes a finite estimated subspace; residual readout/decoder success can reveal remaining correctness information."}
    saved = {"layer14_boundary_correctness_svd_basis": basis}
    raw_ridge = _ridge_contrast_direction(train_correctness, float(settings.get("ridge_alpha", 1.)))
    output["unprojected_ridge_correctness"] = source_metric(test_correctness @ raw_ridge, test_ids, samples, seed)
    output["ridge_estimator"] = {"alpha": float(settings.get("ridge_alpha", 1.)),
        "normalization": "source-contrast RMS fitted on train sources only", "targets": "each source correct-minus-wrong contrast maps to +1; antisymmetric paired regression",
        "fit_families": ["A", "B"], "fit_split": "train", "test_family": "C"}
    rng = np.random.default_rng(_seed(seed, "random_subspaces"))
    random_count = int(settings.get("random_subspace_repetitions", 200))
    random_matrices = rng.normal(size=(random_count, confidence.size, max(ranks)))
    random_bases = np.stack([np.linalg.qr(matrix, mode="reduced")[0].T for matrix in random_matrices])
    for rank in ranks:
        if rank > len(basis):
            continue
        axes = basis[:rank]
        residual = confidence - (confidence @ axes.T) @ axes
        residual_training = train_correctness - (train_correctness @ axes.T) @ axes
        redecoded = _ridge_contrast_direction(residual_training, float(settings.get("ridge_alpha", 1.)))
        test_residual_correctness = test_correctness - (test_correctness @ axes.T) @ axes
        entry = {"correctness_contrast_energy_fraction": float(spectrum[:rank].sum() / spectrum.sum()),
                 "confidence_squared_overlap": float(np.sum((confidence @ axes.T)**2)),
                 "residual_confidence_norm": float(np.linalg.norm(residual)),
                 "v1_test_C": _projection_endpoints({"certainty": test_certainty, "correctness": test_correctness},
                        confidence, residual, correctness, test_ids, samples, seed),
                 "v2": _projection_endpoints(v2, confidence, residual, correctness, v2_ids, samples, seed),
                 "heldout_correctness_redecode": source_metric(test_residual_correctness @ redecoded, test_ids, samples, seed),
                 "heldout_correctness_redecode_by_style": {style: source_metric((test_residual_correctness @ redecoded)[:, i:i+1], test_ids, samples, seed)
                    for i, style in enumerate(STYLES)}}
        random_axes = random_bases[:, :rank]
        coefficients = np.einsum("d,bkd->bk", confidence, random_axes)
        random_residual = confidence[None] - np.einsum("bk,bkd->bd", coefficients, random_axes)
        entry["matched_rank_random_control"] = {"n_repetitions": random_count,
            "confidence_squared_overlap": _distribution(np.sum(coefficients**2, axis=1)), "endpoints": {}}
        for label, contrasts in {"v1_test_C_certainty": test_certainty, "v1_test_C_correctness": test_correctness,
                                 **{"v2_" + key: value for key, value in v2.items()}}.items():
            margins = np.einsum("skd,bd->bsk", contrasts, random_residual, optimize=True)
            raw_margins = contrasts @ confidence
            entry["matched_rank_random_control"]["endpoints"][label] = {
                "accuracy": _distribution(_order(margins).mean(axis=(1, 2))),
                "accuracy_change": _distribution((_order(margins) - _order(raw_margins)[None]).mean(axis=(1, 2))),
                "mean_margin_change": _distribution((margins - raw_margins[None]).mean(axis=(1, 2)))}
        output["rank_candidates"][str(rank)] = entry
        saved[f"layer14_boundary_confidence_remove_svd_rank{rank}"] = residual
        saved[f"layer14_boundary_correctness_redecode_rank{rank}"] = redecoded
    return output, saved


def analyze_separation(v1_rows, v1_hidden, v2_rows, v2_hidden, frozen, config):
    settings = config.get("analysis", {})
    if settings.get("primary", "layer14_boundary") != "layer14_boundary":
        raise ValueError("Audit primary must remain the existing v1 layer14_boundary")
    if settings.get("fit_splits", ["train"]) != ["train"] or settings.get("fit_families", ["A", "B"]) != ["A", "B"]:
        raise ValueError("Fitting is restricted to v1 train A/B")
    samples = int(settings.get("bootstrap_samples", 1000))
    halves = int(settings.get("split_half_repetitions", 250))
    seed = int(settings.get("seed", 20261007))
    metadata, cube = v1_bundles(v1_rows, v1_hidden)
    train = np.asarray([i for i, row in enumerate(metadata) if row["split"] == "train"])
    test = np.asarray([i for i, row in enumerate(metadata) if row["split"] == "test"])
    if not len(train) or not len(test):
        raise ValueError("Missing train or held-out test sources")
    train_ids, test_ids = ([metadata[i]["source_id"] for i in indices] for indices in (train, test))
    if set(train_ids) & set(test_ids):
        raise ValueError("Training and test sources overlap")
    directions = training_directions(v1_rows, v1_hidden, frozen)
    v2_ids, v2_pairs = v2_contrasts(v2_rows, v2_hidden)
    result = {"experiment": "exploratory confidence/correctness separation audit", "primary": "layer14_boundary",
        "scope": {"train_sources": len(train), "test_C_sources": len(test), "test_C_rows": 4 * len(test),
                  "certainty_comparisons": 2 * len(test), "correctness_comparisons": 2 * len(test),
                  "cross_readout_target_comparisons": 4 * len(test), "fit_families": ["A", "B"],
                  "fit_split": "train", "evaluation_family": "C", "v2_sources": len(v2_ids)},
        "representations": {},
        "limitations": ["Correctness labels change answer content; v1 can retain lexical/content and answer-position shortcuts.",
            "These are teacher-forced expressed-certainty readouts, not measured subjective beliefs.",
            "Uncertainty intervals resample sources, with four correlated cells bundled per source.",
            "Projecting a direction or rank-1/2/3 subspace does not erase all correctness information.",
            "This audit was designed after v1/v2 outcomes were observed and is exploratory.",
            "The three domain and four representation comparisons are descriptive; no multiplicity-adjusted confirmatory claims."]}
    primary_data = None
    for name, (layer, position) in REPRESENTATIONS.items():
        features = v1_hidden[:, layer, position].astype(np.float64)
        certainty, correct = contrast_bundles(features, cube)
        train_certainty = certainty[train, :2].mean(axis=(1, 2))
        train_correct = correct[train, :2].mean(axis=(1, 2))
        conf, corr = directions[name], directions[name + "_correctness"]
        residual = conf - float(conf @ corr) * corr
        directions[name + "_confidence_remove_correctness_rank1"] = residual
        cross = _cross_readout(certainty[test, 2], correct[test, 2], conf, corr, test_ids, samples, seed)
        entry = {"role": "primary" if name == "layer14_boundary" else "predefined_secondary",
            "cross_readout": cross,
            "geometry": _geometry(train_certainty, train_correct, conf, corr, samples, halves, seed),
            "training_and_test_refit_bootstrap": _joint_refit_bootstrap(train_certainty, train_correct,
                certainty[test, 2], correct[test, 2], samples, _seed(seed, name)),
            "confidence_correctness_interaction": _interaction(certainty[test, 2] @ conf, test_ids, samples, seed),
            "v1_rank1_projection": _projection_endpoints({"certainty": certainty[test, 2], "correctness": correct[test, 2]},
                    conf, residual, corr, test_ids, samples, seed),
            "domain_transfer": _domain_audit(metadata, train, certainty, correct, samples, seed)}
        entry["geometry"]["cosine_bootstrap_95"] = entry["training_and_test_refit_bootstrap"]["cosine_bootstrap_95"]
        result["representations"][name] = entry
        for domain in sorted({row["domain"] for row in metadata}):
            domain_train = [i for i in train if metadata[i]["domain"] == domain]
            directions[f"{name}_train_{domain}_confidence"] = _unit(certainty[domain_train, :2].mean(axis=(0, 1, 2)))
            directions[f"{name}_train_{domain}_correctness"] = _unit(correct[domain_train, :2].mean(axis=(0, 1, 2)))
        if name == "layer14_boundary":
            primary_data = train_certainty, train_correct, certainty[test, 2], correct[test, 2], conf, corr, residual
    train_certainty, train_correct, test_certainty, test_correct, conf, corr, residual = primary_data
    if not np.allclose(corr, frozen["correctness"], rtol=1e-8, atol=1e-10):
        raise ValueError("Recomputed primary correctness direction differs from canonical v1")
    old_norm = float(np.linalg.norm(residual))
    if old_norm > 1e-12 and not np.allclose(residual, frozen["confidence_projected"] * old_norm, rtol=1e-8, atol=1e-10):
        raise ValueError("Saved normalized projection does not recover the common-scale residual")
    v2 = _endpoint_contrasts(v2_hidden[:, 0, 0].astype(np.float64), v2_pairs)
    result["v2_rank1_projection"] = {"direction_source": "v1 train A/B only; exact existing L14 boundary confidence and correctness",
        "normalization": "Original confidence direction norm=1; rank-1 residual is not renormalized",
        "old_saved_projection_rescale_factor": old_norm,
        "endpoints": _projection_endpoints(v2, conf, residual, corr, v2_ids, samples, seed),
        "training_and_test_refit_bootstrap": _v2_refit_bootstrap(train_certainty, train_correct, v2, samples, seed)}
    result["correctness_lowrank_subspace"], additional = _subspace_audit(train_correct, test_certainty, test_correct,
            conf, corr, test_ids, v2, v2_ids, config, samples, seed)
    directions.update(additional)
    directions["correctness"] = corr.copy()
    directions["confidence_projected_common_scale"] = residual.copy()
    result["checks"] = {"frozen_four_confidence_vectors_reproduced_from_train_AB": True,
        "primary_correctness_vector_reproduced_from_train_AB": True, "old_projection_rescaling_verified": True,
        "train_test_sources_disjoint": True, "all_v1_source_cells_complete": True,
        "v2_fixed_neutral_response_text_and_tokens_verified": True, "no_test_or_v2_fitting": True,
        "source_group_bootstrap": True, "model_calls": 0}
    return result, directions
