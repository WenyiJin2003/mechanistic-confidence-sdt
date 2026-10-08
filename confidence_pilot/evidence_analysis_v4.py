"""Train-only paired readouts and independent behavior checks for evidence v4.

The readout is an ordering score, never a calibrated confidence probability.
Supported/contradicted labels describe agreement with a displayed fictional
record. A successful probe does not alone identify subjective belief.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Any

import numpy as np
from scipy.stats import spearmanr
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

from confidence_pilot.analyze_pairs import grouped_pair_metric
from confidence_pilot.common import file_hash, resolve, stable_hash


PRIMARY = "layer14_response_mean_paired_logistic"
SECONDARY = "layer14_final_content_paired_logistic"
REPRESENTATIONS = {
    PRIMARY: (0, 2),
    SECONDARY: (0, 1),
    "layer14_response_mean_mean_contrast": (0, 2),
    "layer14_response_mean_frozen_certainty": (0, 2),
    "layer14_final_content_frozen_certainty": (0, 1),
    "layer14_prompt_candidateblind": (0, 3),
}
NEUTRAL_ENDPOINTS = (
    "neutral_supported_vs_contradicted",
    "neutral_supported_vs_omitted",
    "neutral_omitted_vs_contradicted",
)
STYLE_ENDPOINTS = (
    "confident_supported_vs_contradicted",
    "hedged_supported_vs_contradicted",
)
WORLDS = ("A", "B", "omitted")
ANSWER_KEYS = ("A", "B")


def _unit(vector, *, allow_zero=False):
    vector = np.asarray(vector, dtype=np.float64)
    norm = float(np.linalg.norm(vector))
    if not np.isfinite(norm) or (norm < 1e-12 and not allow_zero):
        raise ValueError("Undefined evidence readout direction")
    return (vector / norm if norm > 1e-12 else np.zeros_like(vector)), norm


def _order(values):
    values = np.asarray(values, dtype=np.float64)
    return np.where(values > 0, 1., np.where(values < 0, 0., .5))


def _template(row):
    for field in ("context_template", "context_template_family", "template_family", "template_id", "context_family"):
        if field in row:
            return str(row[field])
    return "unspecified"


def _catalog(rows, hidden, config):
    hidden = np.asarray(hidden)
    if not rows or hidden.shape != (len(rows), 2, 4, 1536) or not np.isfinite(hidden).all():
        raise ValueError("Expected finite hidden states [row,2,4,1536]")
    variants, splits, cells = set(), {}, defaultdict(dict)
    for i, row in enumerate(rows):
        variant = str(row["variant_id"])
        if variant in variants:
            raise ValueError("Duplicate variant IDs")
        variants.add(variant)
        source, split = str(row["source_id"]), row["split"]
        if split not in {"train", "validation", "test"}:
            raise ValueError("Invalid source split")
        if source in splits and splits[source] != split:
            raise ValueError("Source leakage across splits")
        splits[source] = split
        key = (row["world"], row["answer_key"], row["certainty"])
        if key[0] not in WORLDS or key[1] not in ANSWER_KEYS or key[2] not in {"neutral", "confident", "hedged"}:
            raise ValueError("Invalid evidence factorial cell")
        if key in cells[source]:
            raise ValueError("Duplicate evidence factorial cell")
        cells[source][key] = i
        if split != "test" and row["certainty"] != "neutral":
            raise ValueError("Non-neutral training/validation response")
        if row["world"] == "omitted" and row.get("correctness") is not None:
            raise ValueError("Omission has no ground-truth correctness label")
    expected = config.get("analysis", {}).get("expected_split_sources", {"train": 96, "validation": 24, "test": 48})
    observed = {split: sum(value == split for value in splits.values()) for split in ("train", "validation", "test")}
    if observed != {key: int(value) for key, value in expected.items()}:
        raise ValueError(f"Unexpected source split counts: {observed}")
    neutral = {(world, answer, "neutral") for world in WORLDS for answer in ANSWER_KEYS}
    for source, lookup in cells.items():
        if not neutral.issubset(lookup):
            raise ValueError(f"Incomplete neutral factorial: {source}")
        if splits[source] != "test" and set(lookup) != neutral:
            raise ValueError("Training/validation must contain exactly neutral rows")
        indices = list(lookup.values())
        if len({rows[i]["fact_type"] for i in indices}) != 1:
            raise ValueError("Fact type changes within a source")
        for answer in ANSWER_KEYS:
            for style in ("neutral", "confident", "hedged"):
                selected = [lookup[(world, answer, style)] for world in WORLDS if (world, answer, style) in lookup]
                if not selected:
                    continue
                if style == "neutral" and len(selected) != 3:
                    raise ValueError("Neutral evidence condition is missing")
                for field in ("response_text", "response_ids", "prompt_token_count", "response_start_position", "final_content_position", "boundary_position"):
                    present = [field in rows[i] for i in selected]
                    if any(present) and (not all(present) or any(rows[i][field] != rows[selected[0]][field] for i in selected)):
                        raise ValueError(f"Identical-answer token/position gate failed: {source}/{field}")
    return cells, splits, observed


def _train_pairs(rows, cells, splits):
    pairs, sources = [], []
    for source in sorted(cells):
        if splits[source] != "train":
            continue
        for answer, other in (("A", "B"), ("B", "A")):
            pairs.append((cells[source][answer, answer, "neutral"], cells[source][other, answer, "neutral"]))
            sources.append(source)
    return pairs, np.asarray(sources, dtype=str)


def _paired_fit(differences, c_value, seed, max_iter, *, scaler=None, signs=None, allow_zero=False):
    differences = np.asarray(differences, dtype=np.float64)
    mirror = np.concatenate((differences, -differences))
    if scaler is None:
        scaler = StandardScaler().fit(mirror)
    if not np.allclose(scaler.mean_, 0, rtol=0, atol=1e-10):
        raise ValueError("Mirrored difference center is not zero")
    chosen = differences if signs is None else differences * np.asarray(signs)[:, None]
    features = scaler.transform(np.concatenate((chosen, -chosen)))
    labels = np.concatenate((np.ones(len(chosen), dtype=int), np.zeros(len(chosen), dtype=int)))
    model = LogisticRegression(C=float(c_value), fit_intercept=False, solver="liblinear", tol=1e-6,
                               max_iter=int(max_iter), random_state=int(seed))
    model.fit(features, labels)
    if np.any(model.n_iter_ >= max_iter):
        raise RuntimeError("Paired logistic regression did not converge")
    raw = model.coef_[0] / scaler.scale_
    vector, norm = _unit(raw, allow_zero=allow_zero)
    return vector, scaler, {"raw_coefficient_norm": norm, "n_iter": int(model.n_iter_[0]),
                            "scaler_mean_max_abs": float(np.max(np.abs(scaler.mean_))),
                            "scaler_scale_sha256": stable_hash(scaler.scale_.tolist())}


def fit_readouts(rows, hidden, config):
    """Fit fixed-C directions on neutral train source differences only.

    Returned vectors and controls are NPZ-ready arrays. The provenance and all
    other metadata are JSON-serializable. Validation/test rows never enter fits.
    """
    cells, splits, counts = _catalog(rows, hidden, config)
    pairs, groups = _train_pairs(rows, cells, splits)
    settings = config.get("analysis", {})
    c_value = float(settings.get("pairwise_logistic_C", .01))
    if c_value != .01:
        raise ValueError("The preregistered paired-logistic C must remain 0.01")
    seed = int(settings.get("seed", 20261010))
    max_iter = int(settings.get("max_iter", 3000))
    vectors, fitted, differences_by_name, scalers = {}, {}, {}, {}
    for name in (PRIMARY, SECONDARY):
        layer, position = REPRESENTATIONS[name]
        features = np.asarray(hidden[:, layer, position], dtype=np.float64)
        differences = np.stack([features[a] - features[b] for a, b in pairs])
        vector, scaler, audit = _paired_fit(differences, c_value, seed, max_iter)
        vectors[name], fitted[name] = vector, audit
        differences_by_name[name], scalers[name] = differences, scaler
    differences = differences_by_name[PRIMARY]
    source_means = np.stack([differences[groups == source].mean(0) for source in np.unique(groups)])
    vectors["layer14_response_mean_mean_contrast"], _ = _unit(source_means.mean(0))
    vectors["layer14_prompt_candidateblind"] = vectors[PRIMARY].copy()
    source = config.get("source_artifacts", {}).get("directions", {})
    source_path = source.get("path", "results/paired_confidence_phase_b/readout_directions.npz")
    if source.get("sha256") and file_hash(source_path) != source["sha256"]:
        raise ValueError("Frozen certainty direction artifact changed")
    with np.load(resolve(source_path)) as archive:
        for position in ("response_mean", "final_content"):
            original = np.asarray(archive["layer14_" + position], dtype=np.float64)
            if original.shape != (1536,) or not np.isfinite(original).all() or not np.isclose(np.linalg.norm(original), 1, atol=1e-10):
                raise ValueError("Invalid frozen v1 certainty vector")
            vectors["layer14_" + position + "_frozen_certainty"] = original.copy()
    null_seed = int(settings.get("null_seed", seed))
    random_count = int(settings.get("random_directions", 200))
    repetitions = int(settings.get("null_repetitions", 200))
    if random_count < 2 or random_count % 2 or repetitions < 1:
        raise ValueError("Need positive shuffled controls and even antipodal random controls")
    rng = np.random.default_rng(null_seed)
    unique_sources = np.unique(groups)
    shuffled, signs_ledger = [], []
    for repetition in range(repetitions):
        source_signs = rng.choice((-1., 1.), size=len(unique_sources))
        signs = np.asarray([source_signs[np.searchsorted(unique_sources, group)] for group in groups])
        vector, _, _ = _paired_fit(differences, c_value, seed, max_iter, scaler=scalers[PRIMARY], signs=signs, allow_zero=True)
        shuffled.append(vector)
        signs_ledger.append(source_signs.tolist())
    random = rng.standard_normal((random_count // 2, 1536))
    random /= np.linalg.norm(random, axis=1)[:, None]
    return {
        "vectors": vectors,
        "scaler_arrays": {
            key: value.copy()
            for name in (PRIMARY, SECONDARY)
            for key, value in (
                (name + "__scaler_scale", scalers[name].scale_),
                (name + "__scaler_mean", scalers[name].mean_),
                (name + "__raw_coefficient", vectors[name] * fitted[name]["raw_coefficient_norm"]),
                (name + "__scaled_coefficient", vectors[name] * fitted[name]["raw_coefficient_norm"] * scalers[name].scale_),
            )
        },
        "shuffled_controls": np.stack(shuffled),
        "random_controls": np.concatenate((random, -random)),
        "provenance": {
            "split_sources": counts, "training_source_ids": unique_sources.tolist(),
            "training_pairs": len(pairs), "mirrored_training_rows": 2 * len(pairs),
            "training_pair_variant_ids": [[rows[a]["variant_id"], rows[b]["variant_id"]] for a, b in pairs],
            "fit_rows": "neutral train only; supported-minus-contradicted same-answer differences",
            "source_weighting": "two pair differences per source, each mirrored with its negative",
            "C": c_value, "fit_intercept": False, "solver": "liblinear", "seed": seed,
            "max_iter": max_iter, "unit_vectors": True, "fits": fitted,
            "selection_used_validation_test_or_behavior": False,
            "frozen_certainty_artifact": {"path": source_path, "sha256": file_hash(source_path)},
            "shuffled_controls": {"count": repetitions, "seed": null_seed,
                "source_bundled_sign_flips": signs_ledger, "frozen_train_scaler": True,
                "interpretation": "Conditional descriptive controls; not permutation p-values"},
            "random_controls": {"count": random_count, "antipodal": True, "unit_norm": True},
        },
    }


def _endpoint_pairs(cells, splits, *, split):
    pairs = {endpoint: [] for endpoint in (*NEUTRAL_ENDPOINTS, *STYLE_ENDPOINTS)}
    for source in sorted(cells):
        if splits[source] != split:
            continue
        lookup = cells[source]
        for answer, other in (("A", "B"), ("B", "A")):
            support = lookup[answer, answer, "neutral"]
            contra = lookup[other, answer, "neutral"]
            omit = lookup["omitted", answer, "neutral"]
            pairs[NEUTRAL_ENDPOINTS[0]].append((support, contra))
            pairs[NEUTRAL_ENDPOINTS[1]].append((support, omit))
            pairs[NEUTRAL_ENDPOINTS[2]].append((omit, contra))
            for style, endpoint in zip(("confident", "hedged"), STYLE_ENDPOINTS):
                positive, negative = (answer, answer, style), (other, answer, style)
                if positive in lookup and negative in lookup:
                    pairs[endpoint].append((lookup[positive], lookup[negative]))
    return pairs


def _metric(margins, pairs, rows, samples, seed):
    margins = np.asarray(margins, dtype=np.float64)
    sources = [str(rows[a]["source_id"]) for a, _ in pairs]
    result = grouped_pair_metric(_order(margins), sources, bootstrap_samples=samples, seed=seed)
    continuous = grouped_pair_metric(margins, sources, bootstrap_samples=samples, seed=seed)
    continuous["estimate"] = continuous.pop("accuracy")
    result.update({"mean_margin": continuous, "tie_fraction": float(np.mean(margins == 0)) if len(margins) else None})
    return result


def _summarize(scores, pairs, rows, samples, seed):
    output = {}
    for endpoint, selected in pairs.items():
        margins = np.asarray([scores[a] - scores[b] for a, b in selected])
        entry = _metric(margins, selected, rows, samples, seed)
        for field, function in (("fact_type", lambda r: str(r["fact_type"])),
                                ("candidate", lambda r: str(r["answer_key"])),
                                ("heldout_template", _template)):
            entry["by_" + field] = {}
            for value in sorted({function(rows[a]) for a, _ in selected}):
                positions = [j for j, (a, _) in enumerate(selected) if function(rows[a]) == value]
                entry["by_" + field][value] = _metric(margins[positions], [selected[j] for j in positions], rows, samples, seed)
        output[endpoint] = entry
    return output


def _style_diagnostics(scores, cells, splits, rows, samples, seed):
    neutral = [i for i, row in enumerate(rows) if row["split"] == "test" and row["certainty"] == "neutral"]
    standard_deviation = float(np.std(np.asarray(scores)[neutral]))
    scale = standard_deviation if standard_deviation > 1e-12 else None
    result = {"standardization": "test neutral-row score standard deviation; descriptive only",
              "neutral_score_standard_deviation": standard_deviation, "by_evidence_condition": {}}
    standardized = []
    for condition in ("supported", "contradicted", "omitted"):
        entry = {}
        for high, low in (("confident", "neutral"), ("hedged", "neutral"), ("confident", "hedged")):
            selected = []
            for source, lookup in cells.items():
                if splits[source] != "test":
                    continue
                for answer, other in (("A", "B"), ("B", "A")):
                    world = answer if condition == "supported" else other if condition == "contradicted" else "omitted"
                    if (world, answer, high) in lookup and (world, answer, low) in lookup:
                        selected.append((lookup[world, answer, high], lookup[world, answer, low]))
            margins = np.asarray([scores[a] - scores[b] for a, b in selected])
            sources = [str(rows[a]["source_id"]) for a, _ in selected]
            metric = grouped_pair_metric(margins, sources, bootstrap_samples=samples, seed=seed)
            metric["estimate"] = metric.pop("accuracy")
            estimate = metric["estimate"]
            metric["standardized_mean_shift"] = estimate / scale if scale is not None and estimate is not None else None
            if metric["standardized_mean_shift"] is not None:
                standardized.append(abs(metric["standardized_mean_shift"]))
            entry[high + "_minus_" + low] = metric
        result["by_evidence_condition"][condition] = entry
    selected = _endpoint_pairs(cells, splits, split="test")[NEUTRAL_ENDPOINTS[0]]
    evidence = grouped_pair_metric(np.asarray([scores[a] - scores[b] for a, b in selected]),
                                  [str(rows[a]["source_id"]) for a, _ in selected], bootstrap_samples=0)["accuracy"]
    evidence_shift = evidence / scale if scale is not None else None
    maximum = max(standardized) if standardized else None
    result.update({"neutral_evidence_standardized_mean_shift": evidence_shift,
                   "maximum_absolute_standardized_style_shift": maximum,
                   "max_style_to_evidence_mean_shift_ratio": maximum / abs(evidence_shift)
                       if maximum is not None and evidence_shift is not None and abs(evidence_shift) > 1e-12 else None,
                   "used_as_gate": False})
    return result


def _rho(first, second):
    first, second = np.asarray(first, dtype=float), np.asarray(second, dtype=float)
    if len(first) < 3 or np.ptp(first) < 1e-12 or np.ptp(second) < 1e-12:
        return None
    value = float(spearmanr(first, second).statistic)
    return value if np.isfinite(value) else None


def _correlation(first, second, sources, *, samples, seed, centering_keys=None):
    first, second, sources = np.asarray(first, dtype=float), np.asarray(second, dtype=float), np.asarray(sources, dtype=str)
    centering_keys = None if centering_keys is None else np.asarray(centering_keys, dtype=str)
    point = _rho(first, second) if centering_keys is None else _rho(_center(first, centering_keys), _center(second, centering_keys))
    unique = np.unique(sources)
    rng = np.random.default_rng(seed)
    groups = {source: np.flatnonzero(sources == source) for source in unique}
    estimates = []
    if point is not None:
        for _ in range(samples):
            indices = np.concatenate([groups[source] for source in rng.choice(unique, size=len(unique), replace=True)])
            if centering_keys is None:
                value = _rho(first[indices], second[indices])
            else:
                value = _rho(_center(first[indices], centering_keys[indices]), _center(second[indices], centering_keys[indices]))
            if value is not None:
                estimates.append(value)
    interval = None
    if estimates:
        lower, upper = np.percentile(estimates, [2.5, 97.5])
        interval = {"lower": float(lower), "upper": float(upper)}
    return {"spearman": point, "bootstrap_95": interval, "n_prompts": len(first), "n_sources": len(unique),
            "valid_bootstrap_draws": len(estimates), "requested_bootstrap_draws": samples,
            "bootstrap_unit": "whole source, including all evidence worlds"}


def _center(values, keys):
    values, keys = np.asarray(values, dtype=float), np.asarray(keys, dtype=str)
    return np.asarray([value - values[keys == key].mean() for value, key in zip(values, keys)])


def _behavior(scores, rows, cells, splits, behavior, samples, seed):
    test_sources = {source for source, split in splits.items() if split == "test"}
    if not behavior:
        return {"present": False, "passed": False, "reason": "Independent generation behavior is missing"}
    indexed = {}
    for row in behavior:
        key = (str(row["source_id"]), row["world"])
        if key in indexed:
            raise ValueError("Duplicate independent behavior prompt")
        if key[0] not in test_sources or key[1] not in WORLDS:
            raise ValueError("Behavior uses a non-test source or invalid world")
        indexed[key] = row
    if set(indexed) != {(source, world) for source in test_sources for world in WORLDS}:
        raise ValueError("Incomplete independent behavior factorial")
    margins, likelihoods, groups, worlds, kinds, choices, world_correct = [], [], [], [], [], [], []
    exact_correct, exact_candidate, exact_unknown = [], [], []
    trace = []
    for (source, world), row in sorted(indexed.items()):
        first, second = cells[source][world, "A", "neutral"], cells[source][world, "B", "neutral"]
        margin = float(scores[first] - scores[second])
        logp_a, logp_b = float(row["candidate_sequence_logpA"]), float(row["candidate_sequence_logpB"])
        if not np.isfinite(logp_a + logp_b):
            raise ValueError("Nonfinite independent candidate likelihood")
        choice = str(row["parsed_choice"])
        if choice not in {"A", "B", "other", "unknown"}:
            raise ValueError("Invalid generated-answer parser output")
        predicted = "A" if margin > 0 else "B" if margin < 0 else "tie"
        correct = None if world == "omitted" else float(choice == world)
        generated_text = str(row.get("greedy_text", ""))
        normalized_text = generated_text.strip().rstrip(".")
        candidates = row.get("candidate_answers", {})
        exact_match = bool(row.get("exact_candidate_value_match", any(normalized_text == value for value in candidates.values())))
        strict_correct = None if world == "omitted" else float(world in candidates and normalized_text == candidates[world])
        exact_abstention = normalized_text.casefold() == str(row.get("unknown_answer", "unknown")).casefold()
        margins.append(margin); likelihoods.append(logp_a - logp_b); groups.append(source)
        worlds.append(world); kinds.append(str(rows[first]["fact_type"])); choices.append(choice); world_correct.append(correct)
        exact_correct.append(strict_correct); exact_candidate.append(exact_match); exact_unknown.append(exact_abstention)
        trace.append({"source_id": source, "world": world, "fact_type": kinds[-1],
                      "probe_margin_A_minus_B": margin, "candidate_logp_margin_A_minus_B": logp_a - logp_b,
                      "probe_choice": predicted, "parsed_choice": choice, "greedy_text": generated_text,
                      "candidate_answers": candidates, "exact_candidate_value_match": exact_match,
                      "exact_value_world_correct": strict_correct, "exact_unknown_output": exact_abstention,
                      "world_correct": correct})
    margins, likelihoods, groups = np.asarray(margins), np.asarray(likelihoods), np.asarray(groups)
    worlds, kinds, choices = np.asarray(worlds), np.asarray(kinds), np.asarray(choices)
    global_correlation = _correlation(margins, likelihoods, groups, samples=samples, seed=seed)
    joint_keys = np.asarray([world + ":" + kind for world, kind in zip(worlds, kinds)])
    centered = _correlation(margins, likelihoods, groups, samples=samples, seed=seed, centering_keys=joint_keys)
    centered["centering_groups"] = "evidence world × fact type; recomputed within each source-bootstrap draw"
    by_condition, by_kind = {}, {}
    for key, destination, labels in (("world", by_condition, worlds), ("fact_type", by_kind, kinds)):
        for value in sorted(set(labels)):
            selected = labels == value
            destination[str(value)] = _correlation(margins[selected], likelihoods[selected], groups[selected], samples=samples, seed=seed)
    coverage = np.isin(choices, ANSWER_KEYS)
    predicted = np.where(margins > 0, "A", np.where(margins < 0, "B", "tie"))
    agreement = (predicted == choices).astype(float)
    unconditional = grouped_pair_metric(agreement, groups, bootstrap_samples=samples, seed=seed)
    conditional = grouped_pair_metric(agreement[coverage], groups[coverage], bootstrap_samples=samples, seed=seed)
    coverage_metric = grouped_pair_metric(coverage.astype(float), groups, bootstrap_samples=samples, seed=seed)
    known = worlds != "omitted"
    known_coverage = grouped_pair_metric(coverage[known].astype(float), groups[known], bootstrap_samples=samples, seed=seed)
    correctness = grouped_pair_metric((choices[known] == worlds[known]).astype(float), groups[known], bootstrap_samples=samples, seed=seed)
    correctness["ground_truth_scope"] = "displayed fictional record; unavailable in omitted condition"
    exact_correctness = grouped_pair_metric(np.asarray([float(value) for value, use in zip(exact_correct, known) if use]),
                                           groups[known], bootstrap_samples=samples, seed=seed)
    exact_correctness["normalization"] = "strip surrounding whitespace and trailing periods; exact case-sensitive candidate value"
    exact_correctness["used_as_gate"] = False
    omitted = ~known
    exact_unknown_metric = grouped_pair_metric(np.asarray(exact_unknown, dtype=float)[omitted], groups[omitted],
                                              bootstrap_samples=samples, seed=seed)
    exact_unknown_metric["normalization"] = "strip surrounding whitespace and trailing periods; case-insensitive exact unknown word"
    exact_unknown_metric["used_as_gate"] = False
    nonexact = ~np.asarray(exact_candidate, dtype=bool)
    output_audit = {"ambiguous_or_other_output_count": int(np.sum(choices == "other")),
                    "non_exact_candidate_output_count": int(np.sum(nonexact)),
                    "known_world_non_exact_candidate_output_count": int(np.sum(nonexact & known)),
                    "ambiguous_or_non_exact_output_count": int(np.sum((choices == "other") | nonexact)),
                    "by_world": {world: {"ambiguous_or_other": int(np.sum((worlds == world) & (choices == "other"))),
                                         "non_exact_candidate": int(np.sum((worlds == world) & nonexact))}
                                 for world in WORLDS},
                    "interpretation": "Non-exact candidate outputs include unknown abstentions; all exact texts and candidate values remain in trace"}
    global_correlation_passed = global_correlation["bootstrap_95"] is not None and global_correlation["bootstrap_95"]["lower"] > 0
    centered_correlation_passed = centered["bootstrap_95"] is not None and centered["bootstrap_95"]["lower"] > 0
    correlation_passed = global_correlation_passed and centered_correlation_passed
    correct_passed = correctness["accuracy"] >= .65 and correctness["bootstrap_95"]["lower"] > .5
    coverage_passed = known_coverage["accuracy"] >= .75
    return {"present": True, "passed": correlation_passed and correct_passed and coverage_passed,
            "global_candidate_likelihood_correlation": global_correlation,
            "condition_fact_type_centered_correlation": centered,
            "by_evidence_world": by_condition, "by_fact_type": by_kind,
            "candidate_choice_coverage": coverage_metric, "greedy_agreement_unconditional": unconditional,
            "known_world_candidate_choice_coverage": known_coverage,
            "greedy_agreement_conditional_on_candidate_choice": conditional,
            "known_world_generative_correctness": correctness,
            "known_world_exact_value_correctness": exact_correctness,
            "omitted_exact_unknown_rate": exact_unknown_metric,
            "output_parsing_audit": output_audit,
            "omitted_choice_counts": {choice: int(np.sum((worlds == "omitted") & (choices == choice)))
                                     for choice in ("A", "B", "other", "unknown")},
            "checks": {"global_correlation_lower_gt_zero": global_correlation_passed,
                       "centered_correlation_lower_gt_zero": centered_correlation_passed,
                       "known_world_accuracy_ge_065_and_lower_gt_05": correct_passed,
                       "known_world_candidate_coverage_ge_075": coverage_passed},
            "selection_or_fitting_uses_behavior": False, "trace": trace,
            "interpretation": "Independent behavioral alignment; candidate likelihood is not calibrated belief"}


def analyze(rows, hidden, readouts, behavior, config):
    """Evaluate fixed readouts and controls without outcome-based selection."""
    cells, splits, counts = _catalog(rows, hidden, config)
    settings = config.get("analysis", {})
    samples, seed = int(settings.get("bootstrap_samples", 2000)), int(settings.get("bootstrap_seed", 271828))
    if samples < 1:
        raise ValueError("Source bootstrap samples must be positive")
    pairs = _endpoint_pairs(cells, splits, split="test")
    expected_style_pairs = counts["test"] * 2
    if any(len(pairs[endpoint]) != expected_style_pairs for endpoint in STYLE_ENDPOINTS):
        raise ValueError("Incomplete test confident/hedged stress pairs")
    summaries, scores = {}, {}
    for name, (layer, position) in REPRESENTATIONS.items():
        vector = np.asarray(readouts["vectors"][name], dtype=np.float64)
        if vector.shape != (1536,) or not np.isfinite(vector).all():
            raise ValueError("Invalid fitted/frozen readout vector")
        values = np.asarray(hidden[:, layer, position], dtype=np.float64) @ vector
        scores[name] = values.tolist()
        summaries[name] = _summarize(values, pairs, rows, samples, seed)
        summaries[name]["style_diagnostics"] = _style_diagnostics(values, cells, splits, rows, samples, seed)
    baselines = {}
    for name, values in (("constant", np.zeros(len(rows))),
                         ("negative_mean_token_nll", -np.asarray([row["mean_token_nll"] for row in rows])),
                         ("negative_sequence_nll", -np.asarray([row["sequence_nll"] for row in rows])),
                         ("response_token_length", np.asarray([row["token_count"] for row in rows]))):
        if not np.isfinite(values).all():
            raise ValueError("Nonfinite scalar baseline")
        baselines[name] = _summarize(values, pairs, rows, samples, seed)
        scores[name] = values.tolist()
    controls = {}
    features = np.asarray(hidden[:, 0, 2], dtype=np.float64)
    for name in ("shuffled_controls", "random_controls"):
        vectors = np.asarray(readouts[name], dtype=np.float64)
        if vectors.ndim != 2 or vectors.shape[1] != 1536 or not np.isfinite(vectors).all():
            raise ValueError("Invalid control vectors")
        endpoint_results = {}
        for endpoint, selected in pairs.items():
            differences = np.stack([features[a] - features[b] for a, b in selected])
            orderings = _order(differences @ vectors.T)
            groups = np.asarray([str(rows[a]["source_id"]) for a, _ in selected])
            source_means = np.stack([orderings[groups == source].mean(0) for source in np.unique(groups)])
            accuracies = source_means.mean(0)
            endpoint_results[endpoint] = {"count": len(accuracies), "mean": float(accuracies.mean()),
                "central_95": np.percentile(accuracies, [2.5, 97.5]).tolist(),
                "upper_95th_percentile": float(np.percentile(accuracies, 95)), "accuracies": accuracies.tolist(),
                "interpretation": "Conditional descriptive training-sign controls; not permutation p-values"
                    if name == "shuffled_controls" else "Descriptive unit random directions"}
        controls[name] = endpoint_results
    primary = summaries[PRIMARY]
    neutral_checks = {}
    for endpoint in NEUTRAL_ENDPOINTS:
        metric = primary[endpoint]
        neutral_checks[endpoint] = {
            "accuracy_ge_065": metric["accuracy"] >= .65,
            "source_bootstrap_lower_gt_05": metric["bootstrap_95"]["lower"] > .5,
            "no_fact_type_below_05": all(value["accuracy"] >= .5 for value in metric["by_fact_type"].values()),
        }
    support_passed = all(all(checks.values()) for checks in neutral_checks.values())
    style_checks = {endpoint: {
        "accuracy_ge_065": primary[endpoint]["accuracy"] >= .65,
        "source_bootstrap_lower_gt_05": primary[endpoint]["bootstrap_95"]["lower"] > .5,
    } for endpoint in STYLE_ENDPOINTS}
    style_passed = all(all(checks.values()) for checks in style_checks.values())
    likelihood_metric = baselines["negative_mean_token_nll"][NEUTRAL_ENDPOINTS[0]]
    likelihood_checks = {
        "accuracy_ge_075": likelihood_metric["accuracy"] >= .75,
        "source_bootstrap_lower_gt_05": likelihood_metric["bootstrap_95"]["lower"] > .5,
    }
    likelihood_passed = all(likelihood_checks.values())
    observed = primary[NEUTRAL_ENDPOINTS[0]]["accuracy"]
    upper = controls["shuffled_controls"][NEUTRAL_ENDPOINTS[0]]["upper_95th_percentile"]
    shuffle_passed = observed > upper
    behavior_result = _behavior(np.asarray(scores[PRIMARY]), rows, cells, splits, behavior, samples, seed)
    support_gate = support_passed and style_passed and shuffle_passed and likelihood_passed
    overall = support_gate and behavior_result["passed"]
    validation = {}
    validation_pairs = _endpoint_pairs(cells, splits, split="validation")
    for name in (PRIMARY, SECONDARY, "layer14_response_mean_mean_contrast"):
        validation[name] = _summarize(np.asarray(scores[name]), validation_pairs, rows, samples, seed)
    return {
        "metrics": {"primary": primary, "fixed_primary": PRIMARY, "validation_descriptive_only": validation},
        "readouts": summaries, "baselines": baselines, "controls": controls,
        "gates": {
            "neutral_evidence_ordering": {"passed": support_passed, "checks": neutral_checks},
            "style_stress": {"passed": style_passed, "checks": style_checks},
            "same_response_likelihood_manipulation": {"passed": likelihood_passed, "checks": likelihood_checks,
                                                       "metric": likelihood_metric},
            "shuffled_control": {"passed": shuffle_passed, "observed": observed, "upper_95th_percentile": upper,
                                  "interpretation": "Conditional descriptive gate, not a permutation p-value"},
            "evidence_support_generalization": {"passed": support_gate},
            "independent_behavior_alignment": {"passed": behavior_result["passed"], "checks": behavior_result.get("checks", {})},
            "pilot_construct_validation": {"passed": overall,
                "interpretation": "Bounded pilot evidence only; no subjective-belief or causal-mechanism claim"},
        },
        "behavior": behavior_result, "row_scores": scores, "split_sources": counts,
        "scope": "Evidence-support ordering in teacher-forced answers, wording stress tests, and independent behavior; not subjective confidence, causality, or training-loss efficacy",
        "conclusion": "Controlled evidence-support measurement; graded-evidence validation next" if overall else
                      "Evidence-support readout generalizes, but construct validation remains insufficient" if support_gate else
                      "Evidence-sensitive readout does not pass the preregistered generalization gates",
    }
