"""Fit-free evaluation of frozen v1 directions on the preregistered v2 data."""
from __future__ import annotations

import hashlib
from collections import defaultdict
from typing import Any

import numpy as np

from confidence_pilot.analyze_pairs import grouped_pair_metric


REPRESENTATIONS = {
    "layer14_boundary": (0, 0),
    "layer14_final_content": (0, 1),
    "layer14_response_mean": (0, 2),
    "layer23_boundary": (1, 0),
    "confidence_projected": (0, 0),
    "correctness": (0, 0),
}
PRIMARY_ENDPOINTS = ("natural_style", "neutral_qa_supported_vs_omitted")


def _order(margins):
    margins = np.asarray(margins, dtype=np.float64)
    return np.where(margins > 0, 1., np.where(margins < 0, 0., .5))


def _pairs(rows, hidden):
    if hidden.shape != (len(rows), 2, 4, 1536) or not np.all(np.isfinite(hidden)):
        raise ValueError("Expected finite hidden [row,2,4,1536]")
    if not rows:
        raise ValueError("Transfer rows are empty")
    ids = [str(row["variant_id"]) for row in rows]
    if len(set(ids)) != len(ids):
        raise ValueError("Duplicate variant IDs")
    lookup = dict(zip(ids, range(len(rows))))
    by_source = defaultdict(list)
    for i, row in enumerate(rows):
        if row.get("split", "test") != "test":
            raise ValueError("Every v2 row must be test-only")
        for key in ("token_count", "char_count", "sequence_nll", "mean_token_nll"):
            if not np.isfinite(float(row[key])):
                raise ValueError(f"Nonfinite {key}")
        by_source[str(row["source_id"])].append(i)
    endpoints = {"natural_style": []}
    for fmt in ("qa", "document"):
        for other in ("omitted", "conflicting"):
            endpoints[f"neutral_{fmt}_supported_vs_{other}"] = []
    for source, indices in sorted(by_source.items()):
        if len({rows[i]["fact_type"] for i in indices}) != 1:
            raise ValueError(f"Inconsistent fact type in {source}")
        style = [i for i in indices if rows[i]["experiment"] == "natural_style"]
        neutral = [i for i in indices if rows[i]["experiment"] == "neutral_evidence"]
        if len(style) != 4 or len(neutral) != 6 or len(indices) != 10:
            raise ValueError(f"Incomplete source conditions in {source}")
        for correctness in ("correct", "incorrect"):
            cells = {rows[i]["certainty"]: i for i in style if rows[i]["correctness"] == correctness}
            if set(cells) != {"confident", "hedged"} or sum(rows[i]["correctness"] == correctness for i in style) != 2:
                raise ValueError(f"Incomplete natural style pair in {source}")
            positive, negative = cells["confident"], cells["hedged"]
            if lookup.get(str(rows[positive]["paired_variant_id"])) != negative or lookup.get(str(rows[negative]["paired_variant_id"])) != positive:
                raise ValueError("Natural pair links must be reciprocal")
            endpoints["natural_style"].append((positive, negative))
        for fmt in ("qa", "document"):
            group = [i for i in neutral if rows[i]["format"] == fmt]
            cells = {rows[i]["condition"]: i for i in group}
            if len(group) != 3 or set(cells) != {"supported", "omitted", "conflicting"}:
                raise ValueError(f"Missing neutral conditions in {source}/{fmt}")
            for i in group:
                if rows[i]["certainty"] != "neutral" or rows[i]["correctness"] != "correct":
                    raise ValueError("Neutral labels must preserve the hidden-world correct proposition")
                if not rows[i].get("response_ids"):
                    raise ValueError("Neutral response IDs are required")
            for key in ("response_ids", "prompt_token_count", "token_count", "char_count"):
                if any(rows[i][key] != rows[group[0]][key] for i in group[1:]):
                    raise ValueError(f"Neutral {key} differ within {source}/{fmt}")
            if all("response_text" in rows[i] for i in group) and len({rows[i]["response_text"] for i in group}) != 1:
                raise ValueError("Neutral response text differs")
            for other in ("omitted", "conflicting"):
                endpoints[f"neutral_{fmt}_supported_vs_{other}"].append((cells["supported"], cells[other]))
    return endpoints


def analyze_transfer(rows: list[dict], hidden: np.ndarray, directions: dict, config: dict) -> dict[str, Any]:
    """Score fixed vectors without fitting, rescaling, or selecting v2 outcomes."""
    hidden = np.asarray(hidden)
    endpoints = _pairs(rows, hidden)
    settings = config.get("analysis", {})
    samples = int(settings.get("bootstrap_samples", 2000))
    seed = int(settings.get("bootstrap_seed", 161803))
    if samples < 1:
        raise ValueError("Source bootstrap samples must be positive")

    def metric(margins, pairs):
        margins = np.asarray(margins, dtype=np.float64)
        result = grouped_pair_metric(_order(margins), [str(rows[a]["source_id"]) for a, _ in pairs], bootstrap_samples=samples, seed=seed)
        result["tie_fraction"] = float(np.mean(margins == 0))
        source_margins = defaultdict(list)
        for margin, (a, _) in zip(margins, pairs):
            source_margins[str(rows[a]["source_id"])].append(float(margin))
        result["mean_pair_margin"] = float(np.mean([np.mean(values) for values in source_margins.values()]))
        return result

    def summarize(scores):
        output = {}
        for endpoint, pairs in endpoints.items():
            margins = np.asarray([scores[a] - scores[b] for a, b in pairs])
            entry = metric(margins, pairs)
            entry["by_fact_type"] = {}
            entry["by_wording_id"] = {}
            fields = [("fact_type", "by_fact_type"), ("wording_id", "by_wording_id")]
            if endpoint == "natural_style":
                entry["by_correctness"] = {}
                fields.append(("correctness", "by_correctness"))
            for field, destination in fields:
                for value in sorted({str(rows[a].get(field, "unspecified")) for a, _ in pairs}):
                    selected = [j for j, (a, _) in enumerate(pairs) if str(rows[a].get(field, "unspecified")) == value]
                    entry[destination][value] = metric(margins[selected], [pairs[j] for j in selected])
            if endpoint == "natural_style":
                deltas = np.asarray([int(rows[a]["token_count"]) - int(rows[b]["token_count"]) for a, b in pairs])
                entry["length_subsets"] = {}
                for label, mask in (("confident_shorter", deltas < 0), ("confident_longer", deltas > 0), ("token_matched_within_one", np.abs(deltas) <= 1)):
                    selected = np.flatnonzero(mask)
                    entry["length_subsets"][label] = metric(margins[selected], [pairs[j] for j in selected]) if len(selected) else {"accuracy": None, "n_pairs": 0, "n_sources": 0, "bootstrap_95": None, "tie_fraction": None, "mean_pair_margin": None}
            output[endpoint] = entry
        return output

    scores = {}
    representations = {}
    frozen_hashes = {}
    for name, (layer, position) in REPRESENTATIONS.items():
        if name not in directions:
            if name == "layer14_boundary":
                raise ValueError("Frozen primary direction is required")
            continue
        vector = np.asarray(directions[name], dtype=np.float64)
        if vector.shape != (1536,) or not np.all(np.isfinite(vector)):
            raise ValueError(f"Invalid frozen direction {name}")
        norm = float(np.linalg.norm(vector))
        if name == "layer14_boundary" and norm <= 1e-12:
            raise ValueError("Frozen primary direction is undefined")
        frozen_hashes[name] = hashlib.sha256(vector.tobytes()).hexdigest()
        row_scores = hidden[:, layer, position].astype(np.float64) @ vector
        scores[name] = row_scores.tolist()
        representations[name] = {"layer": (14, 23)[layer], "position": ("boundary", "final_content", "response_mean", "prompt")[position], "direction_norm": norm, "role": "primary" if name == "layer14_boundary" else "secondary", "endpoints": summarize(row_scores)}

    baseline_inputs = {
        "negative_mean_token_nll": ("mean_token_nll", -1.),
        "negative_sequence_nll": ("sequence_nll", -1.),
        "token_length": ("token_count", 1.),
        "character_length": ("char_count", 1.),
        "text_tfidf": ("tfidf_score", 1.),
        "char_tfidf": ("char_tfidf_score", 1.),
        "frozen_sequence_nll": ("frozen_sequence_nll_score", 1.),
        "frozen_mean_token_nll": ("frozen_mean_token_nll_score", 1.),
    }
    baselines = {}
    for name, (field, orientation) in baseline_inputs.items():
        available = [field in row for row in rows]
        if not any(available):
            baselines[name] = {"available": False, "endpoints": {}}
            continue
        if not all(available):
            raise ValueError(f"Partially supplied baseline {field}")
        row_scores = np.asarray([float(row[field]) * orientation for row in rows])
        if not np.all(np.isfinite(row_scores)):
            raise ValueError(f"Nonfinite baseline {field}")
        if name in {"text_tfidf", "char_tfidf"}:
            for endpoint, pairs in endpoints.items():
                if endpoint.startswith("neutral_") and any(row_scores[a] != row_scores[b] for a, b in pairs):
                    raise ValueError(f"Response-only {field} differs for identical neutral responses")
        scores[name] = row_scores.tolist()
        baselines[name] = {"available": True, "orientation": orientation, "fitted_on_v2": False, "endpoints": summarize(row_scores)}

    controls = {}
    for name in ("random_controls", "shuffled_controls"):
        if name not in directions:
            continue
        vectors = np.asarray(directions[name], dtype=np.float64)
        if vectors.ndim != 2 or vectors.shape[1] != 1536 or not len(vectors) or not np.all(np.isfinite(vectors)):
            raise ValueError(f"Invalid frozen {name}")
        frozen_hashes[name] = hashlib.sha256(vectors.tobytes()).hexdigest()
        control_scores = hidden[:, 0, 0].astype(np.float64) @ vectors.T
        control_endpoints = {}
        for endpoint in PRIMARY_ENDPOINTS:
            pairs = endpoints[endpoint]
            orders = _order(np.stack([control_scores[a] - control_scores[b] for a, b in pairs]))
            sources = np.asarray([str(rows[a]["source_id"]) for a, _ in pairs])
            values = np.stack([orders[sources == source].mean(axis=0) for source in np.unique(sources)]).mean(axis=0)
            control_endpoints[endpoint] = {"count": len(values), "values": values.tolist(), "mean": float(values.mean()), "median": float(np.median(values)), "empirical_95_range": np.percentile(values, [2.5, 97.5]).tolist(), "minimum": float(values.min()), "maximum": float(values.max())}
        controls[name] = {"endpoints": control_endpoints, "interpretation": "Descriptive frozen v1 controls; broad distributions are possible and these are not permutation p-values."}

    primary = {name: representations["layer14_boundary"]["endpoints"][name] for name in PRIMARY_ENDPOINTS}
    comparisons = {}
    for name, row_scores in scores.items():
        if name == "layer14_boundary":
            continue
        comparisons[name] = {}
        for endpoint in PRIMARY_ENDPOINTS:
            pairs = endpoints[endpoint]
            primary_scores = scores["layer14_boundary"]
            primary_orders = _order([primary_scores[a] - primary_scores[b] for a, b in pairs])
            alternative_orders = _order([row_scores[a] - row_scores[b] for a, b in pairs])
            comparison = grouped_pair_metric(alternative_orders - primary_orders, [str(rows[a]["source_id"]) for a, _ in pairs], bootstrap_samples=samples, seed=seed)
            comparison["accuracy_difference"] = comparison.pop("accuracy")
            comparisons[name][endpoint] = comparison
    style, evidence = (primary[name] for name in PRIMARY_ENDPOINTS)
    manipulation = baselines["negative_mean_token_nll"]["endpoints"][PRIMARY_ENDPOINTS[1]]
    ordering_min = float(settings.get("ordering_accuracy_min", .65))
    correctness_min = float(settings.get("natural_correctness_accuracy_min", .60))
    manipulation_min = float(settings.get("nll_manipulation_accuracy_min", .75))
    checks = {
        "natural_style_ordering_at_least_065": style["accuracy"] >= ordering_min,
        "natural_style_lower_bound_above_chance": style["bootstrap_95"]["lower"] > .5,
        "natural_style_both_correctness_cells_at_least_060": all(style["by_correctness"][key]["accuracy"] >= correctness_min for key in ("correct", "incorrect")),
        "natural_style_no_fact_type_below_chance": all(value["accuracy"] >= .5 for value in style["by_fact_type"].values()),
        "neutral_qa_ordering_at_least_065": evidence["accuracy"] >= ordering_min,
        "neutral_qa_lower_bound_above_chance": evidence["bootstrap_95"]["lower"] > .5,
        "neutral_qa_no_fact_type_below_chance": all(value["accuracy"] >= .5 for value in evidence["by_fact_type"].values()),
        "nll_manipulation_ordering_at_least_075": manipulation["accuracy"] >= manipulation_min,
        "nll_manipulation_lower_bound_above_chance": manipulation["bootstrap_95"]["lower"] > .5,
    }
    natural_passed = all(value for key, value in checks.items() if key.startswith("natural_style"))
    evidence_passed = all(value for key, value in checks.items() if key.startswith("neutral_qa"))
    manipulation_passed = all(value for key, value in checks.items() if key.startswith("nll_manipulation"))
    gates = {"checks": checks, "natural_style_passed": natural_passed, "neutral_qa_passed": evidence_passed, "nll_manipulation_passed": manipulation_passed, "evidence_inconclusive": not manipulation_passed, "statistical_passed": natural_passed and evidence_passed, "bridge_promising": natural_passed and evidence_passed and manipulation_passed}
    return {"version": 2, "construct": "expressed certainty and supplied-context evidence sufficiency, not subjective confidence", "fitted_on_v2": False, "variant_ids": [str(row["variant_id"]) for row in rows], "n_sources": len({str(row["source_id"]) for row in rows}), "primary": primary, "representations": representations, "baselines": baselines, "controls": controls, "scores": scores, "paired_comparisons": comparisons, "frozen_direction_sha256": frozen_hashes, "gates": gates, "bootstrap": {"samples": samples, "seed": seed, "unit": "source bundle", "tie_credit": .5}}
