"""Frozen paired-certainty readouts with source-level uncertainty estimates.

This module fits readouts on training sources in rewrite families A/B only.
It does not import or run a language model.  The target is expressed certainty
in a teacher-forced response; these statistics do not identify subjective belief.
"""

from __future__ import annotations

import hashlib
from collections import Counter, defaultdict
from typing import Any

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


LAYERS = (14, 23)
POSITIONS = ("boundary", "final_content", "response_mean", "prompt")
REPRESENTATIONS = {
    "layer14_boundary": (0, 0),
    "layer14_final_content": (0, 1),
    "layer14_response_mean": (0, 2),
    "layer23_boundary": (1, 0),
}


def _unit(vector: np.ndarray) -> tuple[np.ndarray, float]:
    vector = np.asarray(vector, dtype=np.float64)
    norm = float(np.linalg.norm(vector))
    return (vector / norm if norm > 1e-12 else np.zeros_like(vector)), norm


def _ordering(margins: np.ndarray) -> np.ndarray:
    margins = np.asarray(margins, dtype=np.float64)
    return np.where(margins > 0, 1.0, np.where(margins < 0, 0.0, 0.5))


def _seed(seed: int, label: str) -> int:
    suffix = int(hashlib.sha256(label.encode("utf-8")).hexdigest()[:8], 16)
    return (int(seed) + suffix) % (2**32 - 1)


def grouped_pair_metric(
    values: np.ndarray,
    source_ids: list[str] | np.ndarray,
    *,
    bootstrap_samples: int = 2000,
    seed: int = 20261007,
) -> dict[str, Any]:
    """Average pairs within sources, then sources equally; resample bundles.

    Values may also be paired differences of two ordering indicators, allowing
    paired bootstrap contrasts without resampling either model independently.
    """
    values = np.asarray(values, dtype=np.float64)
    groups = np.asarray(source_ids, dtype=str)
    if values.ndim != 1 or groups.shape != values.shape:
        raise ValueError("Pair values and source IDs must be aligned vectors")
    if not np.all(np.isfinite(values)):
        raise ValueError("Pair metrics contain non-finite values")
    if not len(values):
        return {"accuracy": None, "n_pairs": 0, "n_sources": 0, "bootstrap_95": None}
    unique = np.unique(groups)
    source_means = np.asarray([values[groups == group].mean() for group in unique])
    if bootstrap_samples > 0:
        rng = np.random.default_rng(seed)
        samples = source_means[
            rng.integers(0, len(unique), size=(int(bootstrap_samples), len(unique)))
        ].mean(axis=1)
        lower, upper = np.percentile(samples, [2.5, 97.5])
        interval = {"lower": float(lower), "upper": float(upper)}
    else:
        interval = None
    return {
        "accuracy": float(source_means.mean()),
        "n_pairs": int(len(values)),
        "n_sources": int(len(unique)),
        "bootstrap_95": interval,
        "source_mean_minimum": float(source_means.min()),
        "source_mean_maximum": float(source_means.max()),
    }


def _validate_and_pair(
    rows: list[dict[str, Any]], hidden: np.ndarray
) -> list[dict[str, Any]]:
    if not rows:
        raise ValueError("The paired dataset is empty")
    if hidden.ndim != 4 or hidden.shape != (len(rows), 2, 4, 1536):
        raise ValueError(f"Expected hidden [row,2,4,1536], got {hidden.shape}")
    if not np.all(np.isfinite(hidden)):
        raise ValueError("Hidden states contain non-finite values")
    ids = [str(row["variant_id"]) for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("Variant IDs are not unique")
    lookup = {variant_id: i for i, variant_id in enumerate(ids)}
    source_splits: dict[str, str] = {}
    for row in rows:
        source_id = str(row["source_id"])
        split = str(row["split"])
        if split not in {"train", "validation", "test"}:
            raise ValueError(f"Invalid split: {split}")
        if source_id in source_splits and source_splits[source_id] != split:
            raise ValueError(f"Source leakage across splits: {source_id}")
        source_splits[source_id] = split
        if row["certainty"] not in {"confident", "hedged"}:
            raise ValueError("Invalid certainty label")
        if row["correctness"] not in {"correct", "incorrect"}:
            raise ValueError("Invalid correctness label")
        if row["rewrite_family"] not in {"A", "B", "C"}:
            raise ValueError("Invalid rewrite family")
        for key in ("token_count", "char_count", "sequence_nll", "mean_token_nll"):
            if not np.isfinite(float(row[key])):
                raise ValueError(f"Non-finite {key}")
    pairs = []
    used = set()
    for index, row in enumerate(rows):
        if row["certainty"] != "confident":
            continue
        partner_id = str(row["paired_variant_id"])
        if partner_id not in lookup:
            raise ValueError(f"Missing partner for {row['variant_id']}")
        partner_index = lookup[partner_id]
        partner = rows[partner_index]
        if partner["certainty"] != "hedged":
            raise ValueError("Pair partner must have opposite certainty")
        if str(partner["paired_variant_id"]) != str(row["variant_id"]):
            raise ValueError("Pair links must be reciprocal")
        for key in ("source_id", "domain", "correctness", "rewrite_family", "split"):
            if row[key] != partner[key]:
                raise ValueError(f"Paired variants disagree on {key}")
        if index in used or partner_index in used:
            raise ValueError("Variant appears in multiple pairs")
        used.update((index, partner_index))
        pairs.append({
            "confident_index": index,
            "hedged_index": partner_index,
            "source_id": str(row["source_id"]),
            "split": row["split"],
            "domain": row["domain"],
            "correctness": row["correctness"],
            "family": row["rewrite_family"],
            "subtype": str(row.get("subtype", row.get("template_id", row["rewrite_family"]))),
            "token_delta": int(row["token_count"]) - int(partner["token_count"]),
            "char_delta": int(row["char_count"]) - int(partner["char_count"]),
        })
    if len(used) != len(rows):
        raise ValueError("Some variants are not in exactly one complete pair")
    return pairs


def _selection(pairs: list[dict[str, Any]], **fields: Any) -> np.ndarray:
    indices = []
    for i, pair in enumerate(pairs):
        matches = True
        for key, desired in fields.items():
            choices = desired if isinstance(desired, (set, tuple, list)) else (desired,)
            if pair[key] not in choices:
                matches = False
                break
        if matches:
            indices.append(i)
    return np.asarray(indices, dtype=np.int64)


def _source_means(values: np.ndarray, pairs: list[dict[str, Any]], indices: np.ndarray):
    groups = np.asarray([pairs[i]["source_id"] for i in indices])
    unique = np.unique(groups)
    means = np.stack([values[indices[groups == group]].mean(axis=0) for group in unique])
    return unique, means


def _all_metrics(
    margins: np.ndarray,
    pairs: list[dict[str, Any]],
    primary_indices: np.ndarray,
    samples: int,
    seed: int,
) -> dict[str, Any]:
    ordering = _ordering(margins)

    def metric(indices: np.ndarray, label: str) -> dict[str, Any]:
        result = grouped_pair_metric(
            ordering[indices], [pairs[i]["source_id"] for i in indices],
            bootstrap_samples=samples, seed=_seed(seed, label),
        )
        result["tie_fraction"] = float(np.mean(margins[indices] == 0)) if len(indices) else None
        result["mean_pair_margin"] = float(np.mean(margins[indices])) if len(indices) else None
        return result

    output = {"primary": metric(primary_indices, "primary"), "by_split": {}}
    for split in ("train", "validation", "test"):
        split_indices = _selection(pairs, split=split)
        entry = {"all": metric(split_indices, split), "by_correctness": {}, "by_domain": {}, "by_family": {}}
        for field, destination in (("correctness", "by_correctness"), ("domain", "by_domain"), ("family", "by_family")):
            for value in sorted({pairs[i][field] for i in split_indices}):
                indices = _selection(pairs, split=split, **{field: value})
                result = metric(indices, f"{split}/{field}/{value}")
                if field == "family":
                    result["by_correctness"] = {
                        correctness: metric(
                            _selection(pairs, split=split, family=value, correctness=correctness),
                            f"{split}/{value}/{correctness}",
                        ) for correctness in ("correct", "incorrect")
                    }
                    result["by_domain"] = {
                        domain: metric(
                            _selection(pairs, split=split, family=value, domain=domain),
                            f"{split}/{value}/{domain}",
                        ) for domain in sorted({pairs[i]["domain"] for i in indices})
                    }
                entry[destination][value] = result
        output["by_split"][split] = entry
    output["primary_strata"] = {}
    for field in ("correctness", "domain", "family", "subtype"):
        output["primary_strata"][field] = {
            value: metric(
                primary_indices[[pairs[i][field] == value for i in primary_indices]],
                f"primary/{field}/{value}",
            ) for value in sorted({pairs[i][field] for i in primary_indices})
        }
    return output


def _null_summary(values: np.ndarray, observed: float | None) -> dict[str, Any]:
    values = np.asarray(values, dtype=np.float64)
    if not len(values):
        return {"count": 0, "mean": None, "values": [], "observed_midrank_percentile": None}
    return {
        "count": int(len(values)),
        "mean": float(values.mean()),
        "median": float(np.median(values)),
        "minimum": float(values.min()),
        "maximum": float(values.max()),
        "empirical_95_range": np.percentile(values, [2.5, 97.5]).tolist(),
        "observed_midrank_percentile": None if observed is None else float(
            (np.sum(values < observed) + 0.5 * np.sum(values == observed)) / len(values)
        ),
        "values": values.tolist(),
    }


def _phase(config: dict[str, Any]) -> str:
    value = str(config.get("phase", config.get("experiment", {}).get("phase", "A"))).lower()
    if value in {"a", "phase_a", "phase a"}:
        return "A"
    if value in {"b", "phase_b", "phase b"}:
        return "B"
    raise ValueError(f"Unknown phase: {value}")


def analyze_pairs(rows: list[dict], hidden: np.ndarray, config: dict) -> dict:
    """Return a JSON-serializable, leakage-safe paired analysis.

    Row order must exactly match hidden shape [row, layer(14,23),
    position(boundary,final_content,response_mean,prompt), 1536].  Each row
    carries split, numeric response baselines and reciprocal paired_variant_id.
    """
    hidden = np.asarray(hidden)
    pairs = _validate_and_pair(rows, hidden)
    settings = config.get("analysis", {})
    seed = int(settings.get("seed", 20261007))
    bootstrap_seed = int(settings.get("bootstrap_seed", seed + 1))
    samples = int(settings.get("bootstrap_samples", 2000))
    null_repetitions = int(settings.get("null_repetitions", 200))
    random_count = int(settings.get("random_directions", 200))
    if random_count % 2 or random_count < 2:
        raise ValueError("random_directions must be an even number >=2 for antipodal controls")
    if null_repetitions < 1:
        raise ValueError("null_repetitions must be positive")
    phase = _phase(config)
    families = ("A", "B") if phase == "A" else ("C",)
    primary_indices = _selection(pairs, split="test", family=families)
    train_pairs = _selection(pairs, split="train", family=("A", "B"))
    if not len(primary_indices) or not len(train_pairs):
        raise ValueError("Training A/B or primary held-out test pairs are missing")
    confident_indices = np.asarray([pair["confident_index"] for pair in pairs])
    hedged_indices = np.asarray([pair["hedged_index"] for pair in pairs])
    train_rows = np.asarray([
        i for i, row in enumerate(rows)
        if row["split"] == "train" and row["rewrite_family"] in {"A", "B"}
    ])
    train_labels = np.asarray([rows[i]["certainty"] == "confident" for i in train_rows], dtype=int)
    count_by_source = Counter(str(rows[i]["source_id"]) for i in train_rows)
    train_weights = np.asarray([1 / count_by_source[str(rows[i]["source_id"])] for i in train_rows])
    train_weights *= len(train_weights) / train_weights.sum()
    scores: dict[str, list[float]] = {}
    directions: dict[str, list[float]] = {}
    representations = {}
    primary_differences = None
    primary_direction = None
    primary_order = None
    primary_source_differences = None
    for name, (layer_axis, position_axis) in REPRESENTATIONS.items():
        features = hidden[:, layer_axis, position_axis].astype(np.float64)
        differences = features[confident_indices] - features[hedged_indices]
        _, source_differences = _source_means(differences, pairs, train_pairs)
        direction, norm = _unit(source_differences.mean(axis=0))
        row_scores = features @ direction
        margins = differences @ direction
        metrics = _all_metrics(margins, pairs, primary_indices, samples, bootstrap_seed)
        representations[name] = {
            "layer": LAYERS[layer_axis], "position": POSITIONS[position_axis],
            "role": "primary" if name == "layer14_boundary" else "exploratory",
            "train_mean_difference_norm": norm,
            "direction_defined": norm > 1e-12,
            "metrics": metrics,
        }
        scores[name] = row_scores.tolist()
        directions[name] = direction.tolist()
        if name == "layer14_boundary":
            primary_differences = differences
            primary_direction = direction
            primary_order = _ordering(margins)
            primary_source_differences = source_differences
    primary_metrics = representations["layer14_boundary"]["metrics"]
    observed = primary_metrics["primary"]["accuracy"]

    # Frozen numeric and lexical controls use training A/B only, even when
    # family-C variants of the same training sources are available in the cache.
    baselines = {}
    numeric = {
        "length": ("token_count", "char_count"),
        "sequence_nll": ("sequence_nll",),
        "mean_token_nll": ("mean_token_nll",),
        "nll_plus_length": ("sequence_nll", "mean_token_nll", "token_count", "char_count"),
    }
    c_value = float(settings.get("logistic_c", 1.0))
    max_iter = int(settings.get("max_iter", 2000))
    for name, fields in numeric.items():
        features = np.asarray([[float(row[field]) for field in fields] for row in rows])
        model = make_pipeline(StandardScaler(), LogisticRegression(
            C=c_value, max_iter=max_iter, random_state=seed, solver="liblinear"
        ))
        model.fit(features[train_rows], train_labels, logisticregression__sample_weight=train_weights)
        row_scores = model.decision_function(features)
        scores[name] = row_scores.tolist()
        baselines[name] = {
            "features": list(fields), "C": c_value, "training_families": ["A", "B"],
            "metrics": _all_metrics(
                row_scores[confident_indices] - row_scores[hedged_indices],
                pairs, primary_indices, samples, bootstrap_seed,
            ),
        }
    texts = [str(row["response_text"]) for row in rows]
    text_model = make_pipeline(
        TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_features=5000, lowercase=True),
        LogisticRegression(C=c_value, max_iter=max_iter, random_state=seed, solver="liblinear"),
    )
    text_model.fit([texts[i] for i in train_rows], train_labels, logisticregression__sample_weight=train_weights)
    text_scores = text_model.decision_function(texts)
    scores["text_tfidf"] = text_scores.tolist()
    vectorizer = text_model.named_steps["tfidfvectorizer"]
    coefficients = text_model.named_steps["logisticregression"].coef_[0]
    names = vectorizer.get_feature_names_out()
    largest = np.argsort(np.abs(coefficients))[::-1][:20]
    baselines["text_tfidf"] = {
        "training_families": ["A", "B"], "C": c_value,
        "vocabulary_size": int(len(names)),
        "top_terms": [{"term": str(names[i]), "coefficient": float(coefficients[i])} for i in largest],
        "metrics": _all_metrics(
            text_scores[confident_indices] - text_scores[hedged_indices],
            pairs, primary_indices, samples, bootstrap_seed,
        ),
    }

    # Null directions can have wide, even bimodal, ordering distributions on
    # shared templates.  Their ensemble expectation is chance; no per-vector
    # narrow chance band or permutation p-value is asserted here.
    rng = np.random.default_rng(seed)
    signs = rng.choice((-1.0, 1.0), size=(null_repetitions, len(primary_source_differences)))
    shuffled = signs @ primary_source_differences / len(primary_source_differences)
    norms = np.linalg.norm(shuffled, axis=1)
    shuffled = np.divide(shuffled, norms[:, None], out=np.zeros_like(shuffled), where=norms[:, None] > 1e-12)
    half_random = rng.standard_normal((random_count // 2, hidden.shape[-1]))
    half_random /= np.linalg.norm(half_random, axis=1)[:, None]
    random_vectors = np.concatenate((half_random, -half_random))

    def null_accuracy(vectors: np.ndarray) -> np.ndarray:
        orders = _ordering(primary_differences[primary_indices] @ vectors.T)
        source_ids = np.asarray([pairs[i]["source_id"] for i in primary_indices])
        return np.stack([orders[source_ids == source].mean(axis=0) for source in np.unique(source_ids)]).mean(axis=0)

    shuffled_summary = _null_summary(null_accuracy(shuffled), observed)
    random_summary = _null_summary(null_accuracy(random_vectors), observed)
    prompt_features = hidden[:, 0, 3].astype(np.float64)
    prompt_differences = prompt_features[confident_indices] - prompt_features[hedged_indices]
    _, prompt_source_means = _source_means(prompt_differences, pairs, train_pairs)
    prompt_direction, prompt_norm = _unit(prompt_source_means.mean(axis=0))
    maximum_prompt_difference = 0.0
    for source in sorted({str(row["source_id"]) for row in rows}):
        indices = [i for i, row in enumerate(rows) if str(row["source_id"]) == source]
        maximum_prompt_difference = max(maximum_prompt_difference, float(
            np.max(np.abs(prompt_features[indices] - prompt_features[indices[0]]))
        ))
    prompt_tolerance = float(settings.get("prompt_atol", 1e-5))
    scores["negative_prompt"] = (prompt_features @ prompt_direction).tolist()
    directions["negative_prompt"] = prompt_direction.tolist()
    controls = {
        "shuffled_source_signs": shuffled_summary,
        "matched_random_antipodal": random_summary,
        "null_interpretation": "Ensemble means target 0.5. Individual null directions may be strong on shared templates; their percentile is descriptive, not a permutation p-value.",
        "negative_prompt": {
            "maximum_within_source_absolute_difference": maximum_prompt_difference,
            "tolerance": prompt_tolerance,
            "identical_within_tolerance": maximum_prompt_difference <= prompt_tolerance,
            "direction_defined": prompt_norm > 1e-12,
            "train_mean_difference_norm": prompt_norm,
            "metrics": _all_metrics(prompt_differences @ prompt_direction, pairs, primary_indices, samples, bootstrap_seed),
        },
    }

    # Average styles within correctness first, then contents/families within
    # each source.  This removes the simple imbalance of certainty labels.
    features = hidden[:, 0, 0].astype(np.float64)
    source_correctness_differences = []
    for source in sorted(count_by_source):
        family_differences = []
        for family in ("A", "B"):
            correct = [i for i in train_rows if str(rows[i]["source_id"]) == source and rows[i]["rewrite_family"] == family and rows[i]["correctness"] == "correct"]
            wrong = [i for i in train_rows if str(rows[i]["source_id"]) == source and rows[i]["rewrite_family"] == family and rows[i]["correctness"] == "incorrect"]
            if not correct or not wrong:
                raise ValueError("Correctness ablation needs both correctness cells in every training family/source")
            family_differences.append(features[correct].mean(axis=0) - features[wrong].mean(axis=0))
        source_correctness_differences.append(np.mean(family_differences, axis=0))
    correctness_direction, correctness_norm = _unit(np.mean(source_correctness_differences, axis=0))
    cosine = float(primary_direction @ correctness_direction) if correctness_norm > 1e-12 else None
    projected, projected_norm = _unit(primary_direction - float(primary_direction @ correctness_direction) * correctness_direction)
    projected_margins = primary_differences @ projected
    projected_order = _ordering(projected_margins)
    projection_metrics = _all_metrics(projected_margins, pairs, primary_indices, samples, bootstrap_seed)
    projection_difference = grouped_pair_metric(
        (projected_order - primary_order)[primary_indices],
        [pairs[i]["source_id"] for i in primary_indices],
        bootstrap_samples=samples, seed=bootstrap_seed,
    )
    projection_difference["accuracy_difference"] = projection_difference.pop("accuracy")
    directions["correctness"] = correctness_direction.tolist()
    directions["confidence_projected"] = projected.tolist()
    scores["confidence_projected"] = (features @ projected).tolist()
    projection = {
        "correctness_direction_defined": correctness_norm > 1e-12,
        "correctness_mean_difference_norm": correctness_norm,
        "cosine_similarity": cosine,
        "projected_direction_defined": projected_norm > 1e-12,
        "projected_direction_norm_before_renormalization": projected_norm,
        "metrics": projection_metrics,
        "projected_minus_original": projection_difference,
        "interpretation": "Removing one estimated correctness direction does not prove semantic independence or remove all correctness information.",
    }

    # Diagnose whether success persists without the training-set length sign.
    train_token_sign = int(np.sign(np.mean([pairs[i]["token_delta"] for i in train_pairs])))
    length_subsets = {
        "token_matched_within_one": primary_indices[[abs(pairs[i]["token_delta"]) <= 1 for i in primary_indices]],
        "confident_shorter": primary_indices[[pairs[i]["token_delta"] < 0 for i in primary_indices]],
        "confident_longer": primary_indices[[pairs[i]["token_delta"] > 0 for i in primary_indices]],
        "reversed_training_length_sign": primary_indices[[pairs[i]["token_delta"] * train_token_sign < 0 for i in primary_indices]],
    }
    length_metrics = {
        name: grouped_pair_metric(primary_order[indices], [pairs[i]["source_id"] for i in indices], bootstrap_samples=samples, seed=_seed(bootstrap_seed, name))
        for name, indices in length_subsets.items()
    }
    primary_metrics["length_subsets"] = length_metrics
    primary_metrics["training_mean_token_delta_sign"] = train_token_sign
    primary_correct = primary_metrics["primary_strata"]["correctness"]
    primary_domains = primary_metrics["primary_strata"]["domain"]
    primary_families = primary_metrics["primary_strata"]["family"]

    def above(metric: dict[str, Any], threshold: float, inclusive: bool = False) -> bool:
        value = metric.get("accuracy")
        return value is not None and (value >= threshold if inclusive else value > threshold)

    checks: dict[str, bool] = {
        "primary_direction_defined": representations["layer14_boundary"]["direction_defined"],
        "prompt_negative_control_passed": controls["negative_prompt"]["identical_within_tolerance"],
        "shuffled_ensemble_mean_near_chance": 0.4 <= shuffled_summary["mean"] <= 0.6,
        "random_ensemble_mean_near_chance": 0.4 <= random_summary["mean"] <= 0.6,
    }
    if phase == "A":
        checks.update({
            "primary_accuracy_at_least_0.625": above(primary_metrics["primary"], 0.625, True),
            "both_correctness_cells_above_chance": all(above(primary_correct.get(k, {}), 0.5) for k in ("correct", "incorrect")),
            "both_training_families_above_chance": all(above(primary_families.get(k, {}), 0.5) for k in ("A", "B")),
            "at_least_two_domains_above_chance": sum(above(metric, 0.5) for metric in primary_domains.values()) >= 2,
        })
    else:
        interval = primary_metrics["primary"]["bootstrap_95"]
        eligible_lengths = [
            metric for key, metric in length_metrics.items()
            if key in {"token_matched_within_one", "reversed_training_length_sign"}
            and metric["n_sources"] >= int(settings.get("minimum_length_subset_sources", 4))
        ]
        eligible_subtypes = [metric for metric in primary_metrics["primary_strata"]["subtype"].values() if metric["n_sources"] >= 2]
        checks.update({
            "primary_accuracy_at_least_0.65": above(primary_metrics["primary"], 0.65, True),
            "source_bootstrap_lower_above_chance": interval is not None and interval["lower"] > 0.5,
            "both_correctness_cells_at_least_0.60": all(above(primary_correct.get(k, {}), 0.6, True) for k in ("correct", "incorrect")),
            "no_domain_below_chance": bool(primary_domains) and all(above(metric, 0.5, True) for metric in primary_domains.values()),
            "projected_ordering_above_chance": above(projection_metrics["primary"], 0.5),
            "length_robust_subset_testable": bool(eligible_lengths),
            "length_robust_subset_above_chance": any(above(metric, 0.5) for metric in eligible_lengths),
            "multiple_C_subtypes_above_chance": sum(above(metric, 0.5) for metric in eligible_subtypes) >= 2,
        })
    gates = {
        "checks": checks,
        "statistical_passed": bool(all(checks.values())),
        "requires_separate_data_and_extraction_gates": True,
        "interpretation": "Phase A is an engineering progression screen. Phase B validates at most expressed certainty; no loss training or causal claim follows from these gates.",
    }
    source_split_counts = {split: len({str(row["source_id"]) for row in rows if row["split"] == split}) for split in ("train", "validation", "test")}
    return {
        "phase": phase,
        "primary_endpoint": {"split": "test", "families": list(families), "representation": "layer14_boundary", "unit": "source-equal paired ordering accuracy", "ties": 0.5},
        "counts": {"responses": len(rows), "pairs": len(pairs), "sources": len({str(row["source_id"]) for row in rows}), "source_split_counts": source_split_counts, "training_pairs": len(train_pairs), "training_families": ["A", "B"]},
        "analysis_settings": {"seed": seed, "bootstrap_seed": bootstrap_seed, "bootstrap_samples": samples, "null_repetitions": null_repetitions, "random_directions": random_count, "logistic_c": c_value, "max_iter": max_iter},
        "primary": primary_metrics,
        "representations": representations,
        "baselines": baselines,
        "controls": controls,
        "correctness_projection": projection,
        "gates": gates,
        "directions": directions,
        "scores": scores,
        "variant_ids": [str(row["variant_id"]) for row in rows],
        "pair_metadata": pairs,
    }
