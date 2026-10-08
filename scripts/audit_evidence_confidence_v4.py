#!/usr/bin/env python3
"""Independently reproduce v4 from local artifacts, without model inference.

This auditor deliberately does not import production fitting, dataset, analysis,
behavior, or extraction functions. It reconstructs chat tokenization with the
pinned local tokenizer, compares per-input caches, refits sklearn estimators,
and recomputes source-bundled statistics. It never loads model weights.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from zoneinfo import ZoneInfo

import numpy as np
from scipy.stats import spearmanr
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import yaml

ROOT = Path(__file__).resolve().parents[1]
PRIMARY = "layer14_response_mean_paired_logistic"
SECONDARY = "layer14_final_content_paired_logistic"
REPRESENTATIONS = {
    PRIMARY: (0, 2), SECONDARY: (0, 1),
    "layer14_response_mean_mean_contrast": (0, 2),
    "layer14_response_mean_frozen_certainty": (0, 2),
    "layer14_final_content_frozen_certainty": (0, 1),
    "layer14_prompt_candidateblind": (0, 3),
}
ENDPOINTS = (
    "neutral_supported_vs_contradicted", "neutral_supported_vs_omitted",
    "neutral_omitted_vs_contradicted", "confident_supported_vs_contradicted",
    "hedged_supported_vs_contradicted",
)
WORLDS = ("A", "B", "omitted")
POSITIONS = ["boundary", "final_content", "response_mean", "prompt"]
SCHEMAS = ("access_code", "room_assignment", "release_year", "material")
PROTECTED_PREFIXES = (
    "data/paired_confidence", "data/confidence_transfer_v2", "data/confidence_separation_v3",
    "results/paired_confidence_phase_b", "results/confidence_transfer_v2",
    "results/confidence_separation_v3", "results/correctness_geometry_audit",
)


def path(value):
    value = Path(value)
    return value if value.is_absolute() else ROOT / value


def read_json(value):
    return json.loads(path(value).read_text(encoding="utf-8"))


def read_rows(value):
    return [json.loads(line) for line in path(value).read_text(encoding="utf-8").splitlines() if line.strip()]


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def file_digest(value):
    hasher = hashlib.sha256()
    with path(value).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1048576), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


class Audit:
    def __init__(self):
        self.checks = []
        self.compared_scalars = 0
        self.maximum_absolute_difference = 0.

    def check(self, name, passed, detail=None):
        entry = {"name": name, "passed": bool(passed)}
        if detail is not None:
            entry["detail"] = detail
        self.checks.append(entry)
        if not passed:
            raise AssertionError(name + (": " + str(detail) if detail is not None else ""))

    def equal(self, expected, saved, name, *, atol=1e-10):
        """Compare independently recomputed numeric trees, tolerating roundoff only."""
        if isinstance(expected, dict):
            for key, value in expected.items():
                if key not in saved:
                    raise AssertionError(f"Missing saved result: {name}/{key}")
                self.equal(value, saved[key], f"{name}/{key}", atol=atol)
        elif isinstance(expected, (list, tuple, np.ndarray)):
            if len(expected) != len(saved):
                raise AssertionError(f"Result length differs: {name}")
            for index, value in enumerate(expected):
                self.equal(value, saved[index], f"{name}/{index}", atol=atol)
        elif isinstance(expected, (float, int, np.number)) and not isinstance(expected, bool):
            if not np.isfinite(expected) or not np.isfinite(saved):
                raise AssertionError(f"Nonfinite result: {name}")
            difference = abs(float(expected) - float(saved))
            self.compared_scalars += 1
            self.maximum_absolute_difference = max(self.maximum_absolute_difference, difference)
            if not np.isclose(expected, saved, atol=atol, rtol=1e-10):
                raise AssertionError(f"Numeric result differs: {name}: {expected} versus {saved}")
        elif expected != saved:
            raise AssertionError(f"Result differs: {name}: {expected} versus {saved}")


def unit(value, allow_zero=False):
    value = np.asarray(value, dtype=np.float64)
    norm = float(np.linalg.norm(value))
    if not np.isfinite(norm) or (norm < 1e-12 and not allow_zero):
        raise AssertionError("Undefined independent fitted direction")
    return value / norm if norm > 1e-12 else np.zeros_like(value), norm


def ordering(margins):
    margins = np.asarray(margins)
    return np.where(margins > 0, 1., np.where(margins < 0, 0., .5))


def grouped_metric(values, groups, samples, seed):
    values, groups = np.asarray(values, dtype=float), np.asarray(groups, dtype=str)
    if not len(values):
        return {"accuracy": None, "n_pairs": 0, "n_sources": 0, "bootstrap_95": None}
    unique = np.unique(groups)
    means = np.asarray([values[groups == group].mean() for group in unique])
    rng = np.random.default_rng(seed)
    interval = None
    if samples:
        draws = means[rng.integers(0, len(unique), size=(samples, len(unique)))].mean(axis=1)
        lower, upper = np.percentile(draws, [2.5, 97.5])
        interval = {"lower": float(lower), "upper": float(upper)}
    return {"accuracy": float(means.mean()), "n_pairs": len(values), "n_sources": len(unique),
            "bootstrap_95": interval, "source_mean_minimum": float(means.min()),
            "source_mean_maximum": float(means.max())}


def statistic(margins, pairs, rows, samples, seed):
    groups = [rows[a]["source_id"] for a, _ in pairs]
    result = grouped_metric(ordering(margins), groups, samples, seed)
    continuous = grouped_metric(margins, groups, samples, seed)
    continuous["estimate"] = continuous.pop("accuracy")
    result["mean_margin"] = continuous
    result["tie_fraction"] = float(np.mean(np.asarray(margins) == 0)) if len(margins) else None
    return result


def endpoint_pairs(cells, splits, split):
    selected = {name: [] for name in ENDPOINTS}
    for source in sorted(cells):
        if splits[source] != split:
            continue
        lookup = cells[source]
        for answer, opposite in (("A", "B"), ("B", "A")):
            good = lookup[answer, answer, "neutral"]
            bad = lookup[opposite, answer, "neutral"]
            omitted = lookup["omitted", answer, "neutral"]
            for name, pair in zip(ENDPOINTS[:3], ((good, bad), (good, omitted), (omitted, bad))):
                selected[name].append(pair)
            for style, name in zip(("confident", "hedged"), ENDPOINTS[3:]):
                if (answer, answer, style) in lookup and (opposite, answer, style) in lookup:
                    selected[name].append((lookup[answer, answer, style], lookup[opposite, answer, style]))
    return selected


def summarize(scores, pairs, rows, samples, seed):
    result = {}
    for endpoint, chosen in pairs.items():
        margins = np.asarray([scores[a] - scores[b] for a, b in chosen])
        item = statistic(margins, chosen, rows, samples, seed)
        for output, field in (("fact_type", "fact_type"), ("candidate", "answer_key"),
                              ("heldout_template", "context_template")):
            item["by_" + output] = {}
            for value in sorted({str(rows[a][field]) for a, _ in chosen}):
                indices = [j for j, (a, _) in enumerate(chosen) if str(rows[a][field]) == value]
                item["by_" + output][value] = statistic(margins[indices], [chosen[j] for j in indices], rows, samples, seed)
        result[endpoint] = item
    return result


def style_stats(scores, cells, splits, rows, samples, seed):
    neutral = [i for i, row in enumerate(rows) if row["split"] == "test" and row["certainty"] == "neutral"]
    standard_deviation = float(np.std(scores[neutral]))
    scale = standard_deviation if standard_deviation > 1e-12 else None
    result = {"standardization": "test neutral-row score standard deviation; descriptive only",
              "neutral_score_standard_deviation": standard_deviation, "by_evidence_condition": {}}
    shifts = []
    for condition in ("supported", "contradicted", "omitted"):
        output = {}
        for high, low in (("confident", "neutral"), ("hedged", "neutral"), ("confident", "hedged")):
            chosen = []
            for source in cells:
                if splits[source] != "test":
                    continue
                for answer, opposite in (("A", "B"), ("B", "A")):
                    world = answer if condition == "supported" else opposite if condition == "contradicted" else "omitted"
                    chosen.append((cells[source][world, answer, high], cells[source][world, answer, low]))
            margins = np.asarray([scores[a] - scores[b] for a, b in chosen])
            item = grouped_metric(margins, [rows[a]["source_id"] for a, _ in chosen], samples, seed)
            item["estimate"] = item.pop("accuracy")
            item["standardized_mean_shift"] = item["estimate"] / scale if scale is not None else None
            if item["standardized_mean_shift"] is not None:
                shifts.append(abs(item["standardized_mean_shift"]))
            output[high + "_minus_" + low] = item
        result["by_evidence_condition"][condition] = output
    chosen = endpoint_pairs(cells, splits, "test")[ENDPOINTS[0]]
    effect = grouped_metric([scores[a] - scores[b] for a, b in chosen],
                            [rows[a]["source_id"] for a, _ in chosen], 0, seed)["accuracy"]
    evidence_shift = effect / scale if scale is not None else None
    maximum = max(shifts) if shifts else None
    result.update({"neutral_evidence_standardized_mean_shift": evidence_shift,
                   "maximum_absolute_standardized_style_shift": maximum,
                   "max_style_to_evidence_mean_shift_ratio": maximum / abs(evidence_shift)
                       if maximum is not None and evidence_shift is not None and abs(evidence_shift) > 1e-12 else None,
                   "used_as_gate": False})
    return result


def center(values, keys):
    values, keys = np.asarray(values), np.asarray(keys)
    means = {key: values[keys == key].mean() for key in set(keys)}
    return np.asarray([value - means[key] for value, key in zip(values, keys)])


def rho(first, second):
    if len(first) < 3 or np.ptp(first) < 1e-12 or np.ptp(second) < 1e-12:
        return None
    result = float(spearmanr(first, second).statistic)
    return result if np.isfinite(result) else None


def correlation(first, second, groups, samples, seed, keys=None):
    first, second, groups = np.asarray(first), np.asarray(second), np.asarray(groups)
    keys = None if keys is None else np.asarray(keys)
    point = rho(first, second) if keys is None else rho(center(first, keys), center(second, keys))
    unique = np.unique(groups)
    lookup = {source: np.flatnonzero(groups == source) for source in unique}
    rng, estimates = np.random.default_rng(seed), []
    if point is not None:
        for _ in range(samples):
            selected = np.concatenate([lookup[source] for source in rng.choice(unique, len(unique), replace=True)])
            x, y = first[selected], second[selected]
            if keys is not None:
                x, y = center(x, keys[selected]), center(y, keys[selected])
            value = rho(x, y)
            if value is not None:
                estimates.append(value)
    interval = None
    if estimates:
        low, high = np.percentile(estimates, [2.5, 97.5])
        interval = {"lower": float(low), "upper": float(high)}
    return {"spearman": point, "bootstrap_95": interval, "n_prompts": len(first), "n_sources": len(unique),
            "valid_bootstrap_draws": len(estimates), "requested_bootstrap_draws": samples,
            "bootstrap_unit": "whole source, including all evidence worlds"}


def parse(text, candidates):
    text = text.strip().casefold()
    if re.search(r"\b(unknown|unspecified|insufficient)\b|not (specified|provided|listed)|cannot determine", text):
        return "unknown"
    mentions = [key for key, value in candidates.items()
                if re.search(r"(?<!\w)" + re.escape(value.casefold()) + r"(?!\w)", text)]
    return mentions[0] if len(mentions) == 1 else "other"


def strict_choice(text, candidates):
    value = text.strip().rstrip(".")
    matches = [key for key, answer in candidates.items() if value == answer]
    return matches[0] if len(matches) == 1 else "other"


def tokenized(row, tokenizer, config):
    user = f"Context: {row['context']}\n\nQuestion: {row['question']}"
    messages = [{"role": "system", "content": config["model"]["system_prompt"]}, {"role": "user", "content": user}]
    prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    full = tokenizer.apply_chat_template(messages + [{"role": "assistant", "content": row["response_text"]}],
                                         tokenize=False, add_generation_prompt=False)
    prompt_ids = tokenizer(prompt, add_special_tokens=False)["input_ids"]
    full_ids = tokenizer(full, add_special_tokens=False)["input_ids"]
    if full_ids[:len(prompt_ids)] != prompt_ids:
        raise AssertionError("Chat prompt prefix changed")
    boundary_id = config["model"]["boundary_token_id"]
    end = len(prompt_ids) + full_ids[len(prompt_ids):].index(boundary_id)
    response = full_ids[len(prompt_ids):end]
    if not response or any(token in tokenizer.all_special_ids for token in response):
        raise AssertionError("Empty response or special content token")
    if tokenizer.decode(response, skip_special_tokens=False) != row["response_text"]:
        raise AssertionError("Response does not decode to supplied text")
    return {"prompt_ids": prompt_ids, "input_ids": full_ids[:end + 1], "response_ids": response,
            "prompt_length": len(prompt_ids), "response_start": len(prompt_ids),
            "response_stop": end, "boundary_position": end, "final_content_position": end - 1}


def behavior_tokenized(row, tokenizer, config):
    user = f"Context: {row['context']}\n\nQuestion: {row['question']}"
    messages = [{"role": "system", "content": config["model"]["system_prompt"]}, {"role": "user", "content": user}]
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    prompt = tokenizer(text, add_special_tokens=False)["input_ids"]
    candidates = {}
    for key, value in row["candidate_answers"].items():
        ids = tokenizer(text + value, add_special_tokens=False)["input_ids"]
        if ids[:len(prompt)] != prompt:
            raise AssertionError("Behavior candidate prefix changed")
        candidates[key] = ids[len(prompt):]
        if tokenizer.decode(candidates[key], skip_special_tokens=False) != value:
            raise AssertionError("Behavior candidate decoding mismatch")
    return {"prompt_ids": prompt, "candidate_ids": candidates,
            "prompt_length": len(prompt), "prompt_ids_sha256": digest(prompt)}


def context_from_source(source, world):
    roles = {"A": {"A": source["target_role"], "B": source["distractor_role"]},
             "B": {"A": source["distractor_role"], "B": source["target_role"]},
             "omitted": dict(zip(("A", "B"), source["omission_roles"]))}[world]
    template = source["context_template"]
    headers = {"T1": f"Fictional registry for {source['entity']}. Values and assigned fields:",
               "T2": f"Record for {source['entity']} (invented). The entries specify separate fields:",
               "T3": f"The following registry describes fictional {source['entity']}. Each value has its own field:",
               "T4": f"This entry concerns fictional {source['entity']}. Values are assigned to distinct fields:"}
    lines = {"T1": "{value} | {role}", "T2": "Listed value {value} belongs to field {role}.",
             "T3": "{value} is listed under {role}.", "T4": "Value: {value}; field: {role}."}
    return "\n".join([headers[template]] + [lines[template].format(value=source["candidate_values"][key], role=roles[key])
                                            for key in source["candidate_order"]])


def response_from_source(source, answer, style):
    role, entity, value = source["target_role"], source["entity"], source["candidate_values"][answer]
    template = source["context_template"]
    neutral = {"T1": f"The {role} for {entity} is {value}.",
               "T2": f"The registry assigns {value} as the {role} for {entity}.",
               "T3": f"For {entity}, the {role} is {value}.",
               "T4": f"{value} is the {role} recorded for {entity}."}[template]
    if style == "neutral":
        return neutral
    if template == "T3":
        return ("I am certain about this answer. " if style == "confident" else "I am uncertain about this answer. ") + neutral
    return neutral + (" I can state this with confidence." if style == "confident" else " I can only suggest this tentatively.")


def old_values(rows):
    values = set()
    for row in rows:
        for field in ("value_A", "value_B", "true_value", "false_value", "correct_answer", "incorrect_answer",
                      "answer", "correct_value", "wrong_value"):
            if isinstance(row.get(field), str):
                values.add(row[field])
        for field in ("candidate_values", "answers"):
            collection = row.get(field, {})
            entries = collection.values() if isinstance(collection, dict) else collection if isinstance(collection, list) else []
            values.update(item for item in entries if isinstance(item, str))
    return values


def layout_diagnostics(sources):
    test = [source for source in sources if source["split"] == "test"]
    context = Counter(source["context_template"] + ":" + "-".join(source["candidate_order"]) for source in test)
    behavior = Counter(source["behavior_template"] + ":" + "-".join(source["candidate_order"]) for source in test)
    schema_context = Counter(source["fact_type"] + ":" + source["context_template"] + ":" + "-".join(source["candidate_order"]) for source in test)
    numerical = all(int(re.findall(r"\d+", source["candidate_values"]["A"])[-1])
                    < int(re.findall(r"\d+", source["candidate_values"]["B"])[-1]) for source in sources)
    return {"test_context_template_candidate_order_counts": dict(context),
            "test_behavior_template_candidate_order_counts": dict(behavior),
            "test_schema_context_template_candidate_order_counts": dict(schema_context),
            "context_template_order_fully_crossed": set(context) == {"T3:A-B", "T3:B-A", "T4:A-B", "T4:B-A"}
                and len(set(context.values())) == 1,
            "behavior_template_order_coupled": set(behavior) == {"B1:A-B", "B2:B-A"},
            "candidate_A_numeric_suffix_always_smaller_than_B": numerical,
            "used_as_new_gate": False,
            "interpretation": "T3/T4 context templates are crossed with candidate order within every schema. Independent behavior B1/B2 templates are coupled to candidate order; their separate effects cannot be identified. A/B numeric magnitude is consistently ordered, so transfer to reversed-magnitude candidates is untested. Both supplied answers and swapped evidence worlds are retained, so magnitude/order alone cannot predict the same-answer support label."}


def audit_data(audit, config, sources, rows, prompts, augmented, hidden, tokenizer):
    audit.check("fixed_catalog_sizes", (len(sources), len(rows), len(prompts)) == (168, 1584, 144))
    audit.check("source_ids_unique", len({s["source_id"] for s in sources}) == 168)
    source_lookup = {s["source_id"]: s for s in sources}
    audit.check("fixed_source_split_counts", Counter(s["split"] for s in sources) == {"train": 96, "validation": 24, "test": 48})
    audit.check("schema_balance", all(Counter(s["split"] for s in sources if s["fact_type"] == kind)
                                      == {"train": 24, "validation": 6, "test": 12} for kind in SCHEMAS))
    sets = {}
    for split in ("train", "validation", "test"):
        chosen = [s for s in sources if s["split"] == split]
        sets[split] = {"entities": {s["entity"] for s in chosen},
                       "values": {v for s in chosen for v in s["candidate_values"].values()},
                       "templates": {s["context_template"] for s in chosen}}
    audit.check("split_entity_value_template_disjointness", all(not (sets[a][field] & sets[b][field])
              for a, b in (("train", "validation"), ("train", "test"), ("validation", "test")) for field in sets[a]))
    audit.check("template_families_frozen", sets["train"]["templates"] == {"T1"} and sets["validation"]["templates"] == {"T2"}
                and sets["test"]["templates"] == {"T3", "T4"})
    new_values = set().union(*(entry["values"] for entry in sets.values()))
    freshness_counts = {}
    for catalog in ("paired_confidence", "confidence_transfer_v2", "confidence_separation_v3"):
        earlier = read_rows(f"data/{catalog}/source_items.jsonl")
        earlier_text = "\n".join(str(row) for row in earlier)
        overlapping = new_values & old_values(earlier)
        audit.check("prior_catalog_freshness_" + catalog,
                    not overlapping and all(s["entity"] not in earlier_text for s in sources)
                    and not ({s["source_id"] for s in sources} & {r.get("source_id") for r in earlier}),
                    {"prior_sources": len(earlier), "overlapping_values": sorted(overlapping)})
        freshness_counts[catalog] = len(earlier)
    for source in sources:
        locations = []
        for world in WORLDS:
            context = context_from_source(source, world)
            if source["contexts"][world] != context:
                raise AssertionError("Source context differs from frozen role crossing")
            encoded = tokenizer(context, add_special_tokens=False, return_offsets_mapping=True)
            positions = {}
            for key, value in source["candidate_values"].items():
                if context.count(value) != 1:
                    raise AssertionError("Candidate value not unique in context")
                start, stop = context.index(value), context.index(value) + len(value)
                positions[key] = [i for i, (left, right) in enumerate(encoded["offset_mapping"]) if left < stop and right > start]
            locations.append(positions)
            if source["tokenization_audit"]["candidate_context_token_positions"][world] != positions:
                raise AssertionError("Stored context candidate token locations differ")
        if any(location != locations[0] for location in locations):
            raise AssertionError("Candidate locations move across evidence contexts")
    audit.check("candidate_context_locations_and_role_crossings", True)
    audit.check("original_input_fields_preserved", len(rows) == len(augmented) and all(
        all(cached.get(key) == value for key, value in original.items()) for original, cached in zip(rows, augmented)))
    audit.check("hidden_shape_and_finite", hidden.shape == (1584, 2, 4, 1536) and np.isfinite(hidden).all())
    cells, splits, tokens = defaultdict(dict), {}, []
    for index, row in enumerate(rows):
        source = source_lookup[row["source_id"]]
        key = (row["world"], row["answer_key"], row["certainty"])
        if key in cells[row["source_id"]]:
            raise AssertionError("Duplicate factorial cell")
        cells[row["source_id"]][key] = index
        splits[row["source_id"]] = row["split"]
        if source["split"] != row["split"] or source["question"] != row["question"]:
            raise AssertionError("Source metadata changes across rows")
        context = context_from_source(source, row["world"])
        correct = None if row["world"] == "omitted" else row["world"] == row["answer_key"]
        truth = None if correct is None else "correct" if correct else "incorrect"
        support = "absent" if correct is None else "supported" if correct else "contradicted"
        if row["correctness"] != truth or row["supplied_support"] != support:
            raise AssertionError("Authored support/correctness label differs from role assignment")
        if row["context"] != context or row["response_text"] != response_from_source(source, row["answer_key"], row["certainty"]):
            raise AssertionError("Supplied text differs from frozen source crossing")
        token = tokenized(row, tokenizer, config)
        comparisons = {"prompt_token_count": token["prompt_length"], "response_ids": token["response_ids"],
            "response_start_position": token["response_start"], "response_stop_position_exclusive": token["response_stop"],
            "boundary_position": token["boundary_position"], "final_content_position": token["final_content_position"],
            "prompt_ids_sha256": digest(token["prompt_ids"]), "input_ids_sha256": digest(token["input_ids"]),
            "token_count": len(token["response_ids"])}
        if any(row.get(field) != value for field, value in comparisons.items()):
            raise AssertionError("Fresh tokenizer reconstruction differs: " + row["variant_id"])
        answer = source["candidate_values"][row["answer_key"]]
        if row["answer_span_text"] != answer or row["response_text"].count(answer) != 1:
            raise AssertionError("Answer span not unique or incorrect")
        begin = row["response_text"].index(answer)
        stop = begin + len(answer)
        response_encoding = tokenizer(row["response_text"], add_special_tokens=False, return_offsets_mapping=True)
        answer_positions = [token["response_start"] + i for i, (left, right) in enumerate(response_encoding["offset_mapping"])
                            if left < stop and right > begin]
        spans = {"answer_char_start": begin, "answer_char_stop_exclusive": stop,
                 "answer_token_positions": answer_positions, "answer_start_position": answer_positions[0],
                 "answer_stop_position_exclusive": answer_positions[-1] + 1}
        if response_encoding["input_ids"] != token["response_ids"] or any(row.get(field) != value for field, value in spans.items()):
            raise AssertionError("Answer token/character spans differ")
        if len(token["input_ids"]) > config["model"]["max_tokens"]:
            raise AssertionError("A row exceeds token budget")
        tokens.append(token)
    audit.check("variant_ids_unique", len({r["variant_id"] for r in rows}) == len(rows))
    for sid, lookup in cells.items():
        styles = ("neutral", "confident", "hedged") if splits[sid] == "test" else ("neutral",)
        expected = {(world, answer, style) for world in WORLDS for answer in ("A", "B") for style in styles}
        if set(lookup) != expected:
            raise AssertionError("Incomplete or extra source crossing")
        for answer in ("A", "B"):
            for style in styles:
                indices = [lookup[world, answer, style] for world in WORLDS]
                for field in ("response_text", "response_ids", "prompt_token_count", "response_start_position",
                              "answer_token_positions", "boundary_position", "final_content_position"):
                    if any(rows[i][field] != rows[indices[0]][field] for i in indices):
                        raise AssertionError("Same-answer context token/position mismatch")
    audit.check("source_crossings_and_label_truth", True)
    audit.check("pinned_tokenizer_and_same_answer_positions", True, {"reconstructed_rows": len(tokens), "model_calls": 0})
    audit.check("candidate_order_balanced_by_schema_split", all(
        Counter(tuple(s["candidate_order"]) for s in sources if s["fact_type"] == kind and s["split"] == split)
        == {("A", "B"): count // 2, ("B", "A"): count // 2}
        for kind in SCHEMAS for split, count in (("train", 24), ("validation", 6), ("test", 12))))
    prompt_groups = defaultdict(list)
    for index, row in enumerate(rows):
        prompt_groups[row["prompt_group_id"]].append(index)
    maximum = 0.
    for indices in prompt_groups.values():
        if any(tokens[i]["prompt_ids"] != tokens[indices[0]]["prompt_ids"] for i in indices):
            raise AssertionError("Prompt group IDs conceal different inputs")
        maximum = max(maximum, float(np.max(np.abs(hidden[indices, :, 3].astype(float) - hidden[indices[0], :, 3].astype(float)))))
    audit.check("candidate_blind_prompt_states_invariant", maximum <= config["model"]["prompt_control_atol"],
                {"prompt_groups": len(prompt_groups), "maximum_state_difference": maximum})
    return cells, splits, tokens


def audit_freeze(audit, config, manifest):
    audit.check("manifest_configuration_matches_yaml", manifest["configuration"] == config)
    commit = manifest.get("first_run_runtime", {}).get("implementation_commit", manifest["implementation_commit"])
    subprocess.run(["git", "cat-file", "-e", commit + "^{commit}"], cwd=ROOT, check=True, capture_output=True)
    hashes = manifest["freeze_sha256"]
    for filename, expected in hashes.items():
        original = subprocess.check_output(["git", "show", f"{commit}:{filename}"], cwd=ROOT)
        audit.check("freeze_" + filename, file_digest(filename) == expected == hashlib.sha256(original).hexdigest())
    audit.check("protocol_and_data_committed_at_inference", all(name in hashes for name in (
        "docs/experiments/EVIDENCE_CONFIDENCE_V4_PREREGISTRATION.md", "configs/evidence_confidence_v4.yaml",
        *config["data"].values())))
    for name, artifact in config["source_artifacts"].items():
        audit.check("original_reference_sha256_" + name, file_digest(artifact["path"]) == artifact["sha256"])
    protocol = "docs/experiments/EVIDENCE_CONFIDENCE_V4_PREREGISTRATION.md"
    introductions = subprocess.check_output(["git", "log", "--diff-filter=A", "--format=%H", commit, "--", protocol],
                                             cwd=ROOT, text=True).splitlines()
    baseline = subprocess.check_output(["git", "rev-parse", introductions[-1] + "^"], cwd=ROOT, text=True).strip()
    protected = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", commit, "--", *PROTECTED_PREFIXES], cwd=ROOT, text=True).splitlines()
    for filename in protected:
        original = subprocess.check_output(["git", "show", f"{commit}:{filename}"], cwd=ROOT)
        if not path(filename).exists() or file_digest(filename) != hashlib.sha256(original).hexdigest():
            raise AssertionError("Previous scientific artifact changed: " + filename)
        before_v4 = subprocess.check_output(["git", "show", f"{baseline}:{filename}"], cwd=ROOT)
        if original != before_v4:
            raise AssertionError("Previous scientific artifact was changed in the v4 freeze: " + filename)
    audit.check("previous_artifacts_unchanged_since_inference_freeze", bool(protected), {"files_checked": len(protected), "freeze_commit": commit})
    audit.check("previous_artifacts_unchanged_from_pre_v4_commit", bool(protected), {"files_checked": len(protected), "baseline_commit": baseline})
    output = path(config["output"]["results_dir"])
    checked = 0
    for filename, expected in manifest["artifacts"].items():
        if filename == "independent_audit.json":
            continue
        audit.check("artifact_sha256_" + filename, file_digest(output / filename) == expected)
        checked += 1
    return {"implementation_commit": commit, "pre_v4_baseline_commit": baseline,
            "protected_previous_files": len(protected), "result_artifacts": checked}


def audit_caches(audit, config, manifest, rows, tokens, hidden, prompts, behavior, tokenizer):
    output = path(config["output"]["cache_dir"])
    runtime = manifest.get("first_run_runtime", {}).get("runtime", manifest["runtime"])
    settings = {"version": 1, "model": config["model"], "positions": POSITIONS,
                "device": runtime["device"], "dtype": "torch." + runtime["dtype"].removeprefix("torch."), "padding_side": "right"}
    maximum_lengths = defaultdict(int)
    for row, token in zip(rows, tokens):
        maximum_lengths[row["prompt_group_id"]] = max(maximum_lengths[row["prompt_group_id"]], len(token["input_ids"]))
    for index, (row, token) in enumerate(zip(rows, tokens)):
        payload = {"settings": settings, "input_ids": token["input_ids"], "padded_length": maximum_lengths[row["prompt_group_id"]]}
        key = digest(payload)
        if row["cache_fingerprint"] != key:
            raise AssertionError("Activation cache filename fingerprint differs")
        with np.load(output / (key + ".npz"), allow_pickle=False) as cache:
            if cache["input_ids"].tolist() != token["input_ids"] or str(cache["model_fingerprint"].item()) != digest(settings):
                raise AssertionError("Activation cache input/model fingerprint differs")
            if not np.array_equal(cache["hidden"], hidden[index]):
                raise AssertionError("Aggregate hidden states differ from per-input cache")
            if float(cache["sequence_nll"]) != row["sequence_nll"] or float(cache["mean_token_nll"]) != row["mean_token_nll"]:
                raise AssertionError("Aggregate NLL differs from per-input cache")
    audit.check("activation_cache_row_id_states_likelihood_fingerprints", True, {"input_caches_checked": len(rows)})
    runtime = manifest.get("first_run_runtime", {}).get("behavior_runtime", manifest["behavior_runtime"])
    settings = {"version": 1, "model": config["model"], "behavior": config["behavior"], "device": runtime["device"],
                "dtype": "torch." + runtime["dtype"].removeprefix("torch.")}
    if len(prompts) != len(behavior):
        raise AssertionError("Behavior output count differs from input count")
    reconstruction = []
    for original, row in zip(prompts, behavior):
        if any(row.get(field) != value for field, value in original.items()):
            raise AssertionError("Behavior input fields changed")
        token = behavior_tokenized(original, tokenizer, config)
        key = digest({"settings": settings, "tokens": token})
        if row["cache_fingerprint"] != key or original["prompt_ids"] != token["prompt_ids"]:
            raise AssertionError("Behavior cache key/prompt changed")
        if row["behavior_prompt_ids"] != token["prompt_ids"] or row["behavior_candidate_ids"] != token["candidate_ids"]:
            raise AssertionError("Behavior saved token reconstruction differs")
        if original["candidate_response_ids"] != token["candidate_ids"]:
            raise AssertionError("Behavior bare-answer tokens changed")
        if len(token["candidate_ids"]["A"]) != len(token["candidate_ids"]["B"]):
            raise AssertionError("Behavior candidate lengths differ")
        if original["question"] == original["extraction_question"]:
            raise AssertionError("Behavior prompt is not independently phrased")
        cached = read_json(path(config["output"]["behavior_cache_dir"]) / (key + ".json"))
        if cached["tokens"] != token or cached["settings_fingerprint"] != digest(settings):
            raise AssertionError("Behavior cache fingerprint differs")
        if any(row.get(field) != value for field, value in cached["outputs"].items()):
            raise AssertionError("Saved behavior outputs differ from per-input cache")
        decoded = tokenizer.decode(row["greedy_token_ids"], skip_special_tokens=True).strip()
        if not 0 < len(row["greedy_token_ids"]) <= config["behavior"]["max_new_tokens"]:
            raise AssertionError("Generation token budget differs")
        parsed = parse(decoded, row["candidate_answers"])
        exact = strict_choice(decoded, row["candidate_answers"]) in {"A", "B"}
        if row["greedy_text"] != decoded or row["parsed_choice"] != parsed or row["exact_candidate_value_match"] != exact:
            raise AssertionError("Behavior generation decoding/parsing differs")
        if row["candidate_log_odds_A_minus_B"] != row["candidate_sequence_logpA"] - row["candidate_sequence_logpB"]:
            raise AssertionError("Saved behavior log odds differ from full-sequence log probabilities")
        reconstruction.append(token)
    audit.check("behavior_cache_tokens_generation_parser_likelihood_fingerprints", True,
                {"input_caches_checked": len(behavior), "model_calls": 0})
    groups = defaultdict(list)
    for row, token in zip(prompts, reconstruction):
        groups[row["source_id"]].append((row, token))
    for items in groups.values():
        if len(items) != 3 or {r["world"] for r, _ in items} != set(WORLDS):
            raise AssertionError("Incomplete independent behavior worlds")
        if len({t["prompt_length"] for _, t in items}) != 1 or any(t["candidate_ids"] != items[0][1]["candidate_ids"] for _, t in items):
            raise AssertionError("Behavior world token/position gates differ")
    audit.check("behavior_independent_prompt_three_world_gates", len(groups) == 48)


def independent_fits(audit, config, rows, cells, splits, hidden, saved, provenance):
    pairs, groups = [], []
    for source in sorted(cells):
        if splits[source] == "train":
            for answer, opposite in (("A", "B"), ("B", "A")):
                pairs.append((cells[source][answer, answer, "neutral"], cells[source][opposite, answer, "neutral"]))
                groups.append(source)
    groups = np.asarray(groups)
    unique = np.unique(groups)
    audit.check("fit_pool_train_only_neutral_sources", len(pairs) == 192 and len(unique) == 96
                and all(rows[a]["split"] == rows[b]["split"] == "train" for a, b in pairs))
    audit.equal([[rows[a]["variant_id"], rows[b]["variant_id"]] for a, b in pairs], provenance["training_pair_variant_ids"], "fitting/pair_ids")
    audit.equal(unique.tolist(), provenance["training_source_ids"], "fitting/train_sources")
    settings = config["analysis"]
    seed, max_iter = settings["seed"], settings["max_iter"]
    if settings["pairwise_logistic_C"] != .01:
        raise AssertionError("Registered regularization changed")

    def fit(differences, scaler, signs=None, allow_zero=False):
        x = differences if signs is None else differences * signs[:, None]
        x = scaler.transform(np.concatenate((x, -x)))
        labels = np.concatenate((np.ones(len(differences), dtype=int), np.zeros(len(differences), dtype=int)))
        model = LogisticRegression(C=.01, fit_intercept=False, solver="liblinear", tol=1e-6,
                                   max_iter=max_iter, random_state=seed).fit(x, labels)
        if np.any(model.n_iter_ >= max_iter):
            raise AssertionError("Independent logistic refit did not converge")
        raw = model.coef_[0] / scaler.scale_
        direction, norm = unit(raw, allow_zero)
        return direction, norm, model

    directions, scales = {}, {}
    primary_differences = None
    for name in (PRIMARY, SECONDARY):
        layer, position = REPRESENTATIONS[name]
        features = hidden[:, layer, position].astype(float)
        differences = np.stack([features[a] - features[b] for a, b in pairs])
        scaler = StandardScaler().fit(np.concatenate((differences, -differences)))
        direction, norm, estimator = fit(differences, scaler)
        directions[name] = direction
        for suffix, value in (("scaler_scale", scaler.scale_), ("scaler_mean", scaler.mean_),
                              ("raw_coefficient", direction * norm),
                              ("scaled_coefficient", direction * norm * scaler.scale_)):
            np.testing.assert_allclose(value, saved[name + "__" + suffix], atol=1e-10, rtol=1e-10)
        audit.equal({"raw_coefficient_norm": norm, "n_iter": int(estimator.n_iter_[0]),
                     "scaler_mean_max_abs": float(np.max(np.abs(scaler.mean_))),
                     "scaler_scale_sha256": digest(scaler.scale_.tolist())}, provenance["fits"][name], "fitting/" + name)
        if name == PRIMARY:
            primary_differences, scales[name] = differences, scaler
    source_means = np.stack([primary_differences[groups == source].mean(0) for source in unique])
    directions["layer14_response_mean_mean_contrast"] = unit(source_means.mean(0))[0]
    directions["layer14_prompt_candidateblind"] = directions[PRIMARY].copy()
    with np.load(path(config["source_artifacts"]["directions"]["path"]), allow_pickle=False) as previous:
        for position in ("response_mean", "final_content"):
            directions["layer14_" + position + "_frozen_certainty"] = previous["layer14_" + position].astype(float)
    for name, value in directions.items():
        np.testing.assert_allclose(value, saved[name], atol=1e-10, rtol=1e-10)
    rng = np.random.default_rng(settings["null_seed"])
    controls, signs_ledger = [], []
    for _ in range(settings["null_repetitions"]):
        source_signs = rng.choice((-1., 1.), len(unique))
        signs = source_signs[np.searchsorted(unique, groups)]
        controls.append(fit(primary_differences, scales[PRIMARY], signs, allow_zero=True)[0])
        signs_ledger.append(source_signs.tolist())
    shuffled = np.stack(controls)
    count = settings["random_directions"]
    random = rng.standard_normal((count // 2, 1536))
    random /= np.linalg.norm(random, axis=1)[:, None]
    random = np.concatenate((random, -random))
    np.testing.assert_allclose(shuffled, saved["shuffled_controls"], atol=1e-10, rtol=1e-10)
    np.testing.assert_array_equal(random, saved["random_controls"])
    audit.equal(signs_ledger, provenance["shuffled_controls"]["source_bundled_sign_flips"], "controls/sign_bundles")
    audit.check("independent_train_only_readout_scaler_coefficients", True,
                {"training_pairs": len(pairs), "mirrored_training_rows": 2 * len(pairs), "C": .01,
                 "fit_intercept": False, "validation_test_behavior_fit_rows": 0})
    audit.check("independent_bundled_sign_and_random_controls", True,
                {"sign_control_refits": len(shuffled), "random_directions": len(random),
                 "interpretation": "Conditional descriptive controls; not permutation p-values"})
    return directions, {"shuffled_controls": shuffled, "random_controls": random}


def independent_behavior(scores, rows, cells, behavior, samples, seed):
    groups, worlds, schemas, margins, logodds, choices, exacts, stricts = [], [], [], [], [], [], [], []
    parsing_differences, unknown_exact, traces = [], [], []
    for record in sorted(behavior, key=lambda row: (row["source_id"], row["world"])):
        sid, world = record["source_id"], record["world"]
        a, b = cells[sid][world, "A", "neutral"], cells[sid][world, "B", "neutral"]
        groups.append(sid); worlds.append(world); schemas.append(rows[a]["fact_type"])
        margins.append(scores[a] - scores[b])
        logodds.append(record["candidate_sequence_logpA"] - record["candidate_sequence_logpB"])
        choice = parse(record["greedy_text"], record["candidate_answers"])
        strict = strict_choice(record["greedy_text"], record["candidate_answers"])
        choices.append(choice); stricts.append(strict); exacts.append(strict in {"A", "B"})
        exact_unknown = record["greedy_text"].strip().rstrip(".").casefold() == record.get("unknown_answer", "unknown").casefold()
        unknown_exact.append(exact_unknown)
        traces.append({"source_id": sid, "world": world, "fact_type": rows[a]["fact_type"],
            "probe_margin_A_minus_B": float(scores[a] - scores[b]),
            "candidate_logp_margin_A_minus_B": record["candidate_sequence_logpA"] - record["candidate_sequence_logpB"],
            "probe_choice": "A" if scores[a] > scores[b] else "B" if scores[a] < scores[b] else "tie",
            "parsed_choice": choice, "greedy_text": record["greedy_text"], "candidate_answers": record["candidate_answers"],
            "exact_candidate_value_match": strict in {"A", "B"},
            "exact_value_world_correct": None if world == "omitted" else float(strict == world),
            "exact_unknown_output": exact_unknown, "world_correct": None if world == "omitted" else float(choice == world)})
        if choice in {"A", "B"} and choice != strict:
            parsing_differences.append({"behavior_id": record["behavior_id"], "world": world,
                "parsed_choice": choice, "strict_candidate_choice": strict, "greedy_text": record["greedy_text"]})
    margins, logodds = np.asarray(margins), np.asarray(logodds)
    groups, worlds, schemas, choices, stricts = map(np.asarray, (groups, worlds, schemas, choices, stricts))
    predicted = np.where(margins > 0, "A", np.where(margins < 0, "B", "tie"))
    coverage = np.isin(choices, ("A", "B"))
    known = worlds != "omitted"
    global_correlation = correlation(margins, logodds, groups, samples, seed)
    keys = np.asarray([world + ":" + kind for world, kind in zip(worlds, schemas)])
    centered = correlation(margins, logodds, groups, samples, seed, keys)
    result = {"global_candidate_likelihood_correlation": global_correlation,
              "condition_fact_type_centered_correlation": centered,
              "candidate_choice_coverage": grouped_metric(coverage.astype(float), groups, samples, seed),
              "known_world_candidate_choice_coverage": grouped_metric(coverage[known].astype(float), groups[known], samples, seed),
              "known_world_generative_correctness": grouped_metric((choices[known] == worlds[known]).astype(float), groups[known], samples, seed),
              "greedy_agreement_unconditional": grouped_metric((predicted == choices).astype(float), groups, samples, seed),
              "greedy_agreement_conditional_on_candidate_choice": grouped_metric((predicted[coverage] == choices[coverage]).astype(float), groups[coverage], samples, seed),
              "omitted_choice_counts": {choice: int(np.sum((worlds == "omitted") & (choices == choice))) for choice in ("A", "B", "other", "unknown")},
              "by_evidence_world": {}, "by_fact_type": {}}
    for labels, destination in ((worlds, "by_evidence_world"), (schemas, "by_fact_type")):
        for value in sorted(set(labels)):
            selected = labels == value
            result[destination][str(value)] = correlation(margins[selected], logodds[selected], groups[selected], samples, seed)
    correctness = result["known_world_generative_correctness"]
    checks = {"global_correlation_lower_gt_zero": global_correlation["bootstrap_95"] is not None and global_correlation["bootstrap_95"]["lower"] > 0,
              "centered_correlation_lower_gt_zero": centered["bootstrap_95"] is not None and centered["bootstrap_95"]["lower"] > 0,
              "known_world_accuracy_ge_065_and_lower_gt_05": correctness["accuracy"] >= .65 and correctness["bootstrap_95"]["lower"] > .5,
              "known_world_candidate_coverage_ge_075": result["known_world_candidate_choice_coverage"]["accuracy"] >= .75}
    result["checks"], result["passed"] = checks, all(checks.values())
    strict_accuracy = grouped_metric((stricts[known] == worlds[known]).astype(float), groups[known], samples, seed)
    exact_unknown_metric = grouped_metric(np.asarray(unknown_exact, dtype=float)[~known], groups[~known], samples, seed)
    result["known_world_exact_value_correctness"] = strict_accuracy
    result["omitted_exact_unknown_rate"] = exact_unknown_metric
    result["trace"] = traces
    nonexact = ~np.asarray(exacts, dtype=bool)
    result["output_parsing_audit"] = {
        "ambiguous_or_other_output_count": int(np.sum(choices == "other")),
        "non_exact_candidate_output_count": int(np.sum(nonexact)),
        "known_world_non_exact_candidate_output_count": int(np.sum(nonexact & known)),
        "ambiguous_or_non_exact_output_count": int(np.sum((choices == "other") | nonexact)),
        "by_world": {world: {"ambiguous_or_other": int(np.sum((worlds == world) & (choices == "other"))),
                             "non_exact_candidate": int(np.sum((worlds == world) & nonexact))} for world in WORLDS}}
    strict_coverage = grouped_metric(np.isin(stricts[known], ("A", "B")).astype(float), groups[known], samples, seed)
    diagnostics = {"parsed_known_world_correctness": correctness, "strict_exact_known_world_correctness": strict_accuracy,
                   "strict_exact_known_world_candidate_coverage": strict_coverage,
                   "parsed_minus_strict_accuracy": correctness["accuracy"] - strict_accuracy["accuracy"],
                   "parsing_difference_count": len(parsing_differences), "parsing_differences": parsing_differences,
                   "known_prompts": int(known.sum()), "all_prompts": len(known),
                   "strict_rule": "strip whitespace and trailing period; otherwise require complete candidate value",
                   "mention_parser_risk": "An explicit candidate mention alone does not prove affirmation; all strict disagreements are listed."}
    return result, diagnostics


def independent_analysis(audit, config, rows, hidden, cells, splits, directions, controls, saved, behavior):
    samples, seed = config["analysis"]["bootstrap_samples"], config["analysis"]["bootstrap_seed"]
    pairs = endpoint_pairs(cells, splits, "test")
    audit.check("test_endpoint_counts_and_source_bundles", all(len(chosen) == 96 and len({rows[a]["source_id"] for a, _ in chosen}) == 48 for chosen in pairs.values()))
    readouts, scores = {}, {}
    for name, (layer, position) in REPRESENTATIONS.items():
        value = hidden[:, layer, position].astype(float) @ directions[name]
        scores[name] = value
        readouts[name] = summarize(value, pairs, rows, samples, seed)
        readouts[name]["style_diagnostics"] = style_stats(value, cells, splits, rows, samples, seed)
        audit.equal(value, saved["row_scores"][name], "scores/" + name)
        audit.equal(readouts[name], saved["readouts"][name], "readouts/" + name)
    baselines = {}
    for name, value in (("constant", np.zeros(len(rows))),
                        ("negative_mean_token_nll", -np.asarray([r["mean_token_nll"] for r in rows])),
                        ("negative_sequence_nll", -np.asarray([r["sequence_nll"] for r in rows])),
                        ("response_token_length", np.asarray([r["token_count"] for r in rows]))):
        baselines[name] = summarize(value, pairs, rows, samples, seed)
        audit.equal(value, saved["row_scores"][name], "scores/" + name)
        audit.equal(baselines[name], saved["baselines"][name], "baselines/" + name)
    nulls = {}
    features = hidden[:, 0, 2].astype(float)
    for name, vectors in controls.items():
        nulls[name] = {}
        for endpoint, chosen in pairs.items():
            differences = np.stack([features[a] - features[b] for a, b in chosen])
            indicators = ordering(differences @ vectors.T)
            groups = np.asarray([rows[a]["source_id"] for a, _ in chosen])
            accuracies = np.stack([indicators[groups == source].mean(0) for source in np.unique(groups)]).mean(0)
            item = {"count": len(accuracies), "mean": float(accuracies.mean()),
                    "central_95": np.percentile(accuracies, [2.5, 97.5]).tolist(),
                    "upper_95th_percentile": float(np.percentile(accuracies, 95)), "accuracies": accuracies.tolist()}
            nulls[name][endpoint] = item
            audit.equal(item, saved["controls"][name][endpoint], "controls/" + name + "/" + endpoint)
    validation = endpoint_pairs(cells, splits, "validation")
    for name in (PRIMARY, SECONDARY, "layer14_response_mean_mean_contrast"):
        audit.equal(summarize(scores[name], validation, rows, samples, seed),
                    saved["metrics"]["validation_descriptive_only"][name], "validation/" + name)
    audit.equal(readouts[PRIMARY], saved["metrics"]["primary"], "primary")
    audit.check("independent_scores_endpoint_strata_bootstraps_and_baselines", True,
                {"representations": len(readouts), "endpoints_per_readout": len(pairs), "whole_source_bootstrap_draws": samples})
    behavior_result, parsing = independent_behavior(scores[PRIMARY], rows, cells, behavior, samples, seed)
    audit.equal(behavior_result, saved["behavior"], "behavior")
    audit.check("independent_output_behavior_and_recentered_source_bootstraps", True,
                {"test_sources": 48, "output_prompts": len(behavior), "whole_source_bootstrap_draws": samples})
    primary = readouts[PRIMARY]
    neutral_checks = {endpoint: {"accuracy_ge_065": primary[endpoint]["accuracy"] >= .65,
        "source_bootstrap_lower_gt_05": primary[endpoint]["bootstrap_95"]["lower"] > .5,
        "no_fact_type_below_05": all(item["accuracy"] >= .5 for item in primary[endpoint]["by_fact_type"].values())} for endpoint in ENDPOINTS[:3]}
    support = all(all(item.values()) for item in neutral_checks.values())
    style_checks = {endpoint: {"accuracy_ge_065": primary[endpoint]["accuracy"] >= .65,
        "source_bootstrap_lower_gt_05": primary[endpoint]["bootstrap_95"]["lower"] > .5} for endpoint in ENDPOINTS[3:]}
    style = all(all(item.values()) for item in style_checks.values())
    likelihood = baselines["negative_mean_token_nll"][ENDPOINTS[0]]
    likelihood_checks = {"accuracy_ge_075": likelihood["accuracy"] >= .75,
                         "source_bootstrap_lower_gt_05": likelihood["bootstrap_95"]["lower"] > .5}
    shuffled = primary[ENDPOINTS[0]]["accuracy"] > nulls["shuffled_controls"][ENDPOINTS[0]]["upper_95th_percentile"]
    evidence = support and style and all(likelihood_checks.values()) and shuffled
    gates = {"neutral_evidence_ordering": {"passed": support, "checks": neutral_checks},
             "style_stress": {"passed": style, "checks": style_checks},
             "same_response_likelihood_manipulation": {"passed": all(likelihood_checks.values()), "checks": likelihood_checks},
             "shuffled_control": {"passed": shuffled},
             "evidence_support_generalization": {"passed": evidence},
             "independent_behavior_alignment": {"passed": behavior_result["passed"], "checks": behavior_result["checks"]},
             "pilot_construct_validation": {"passed": evidence and behavior_result["passed"]}}
    audit.equal(gates, saved["gates"], "gates")
    audit.check("independent_preregistered_gate_decisions", True)
    return {"primary": {endpoint: {key: value for key, value in primary[endpoint].items()
                                    if key in {"accuracy", "bootstrap_95", "n_pairs", "n_sources", "tie_fraction"}} for endpoint in ENDPOINTS},
            "gates": gates, "behavior_parsing": parsing,
            "behavior_correlations": {key: behavior_result[key] for key in (
                "global_candidate_likelihood_correlation", "condition_fact_type_centered_correlation")}}


def run(config_path):
    audit = Audit()
    config = yaml.safe_load(path(config_path).read_text(encoding="utf-8"))
    output = path(config["output"]["results_dir"])
    report = {"audit": "independent-evidence-confidence-v4", "completed_at": datetime.now(ZoneInfo("America/New_York")).isoformat(),
              "model_forward_calls": 0, "generation_calls": 0, "nli_calls": 0, "openai_api_calls": 0,
              "production_fit_or_analysis_imports": False, "checks": audit.checks,
              "limits": ["Tokenizer-only reconstruction does not independently rerun hidden-state computation.",
                         "Cache equality and frozen extraction code verify aggregation provenance, not causal validity.",
                         "A passing pilot concerns contextual evidence support, not subjective belief or a validated SDT objective."]}
    try:
        required = ("manifest.json", "extraction_rows.jsonl", "hidden_states.npz", "behavior_outputs.jsonl",
                    "readout_directions.npz", "fitting_provenance.json", "metrics.json")
        audit.check("all_completed_run_artifacts_exist", all((output / name).exists() for name in required))
        manifest = read_json(output / "manifest.json")
        report["freeze_integrity"] = audit_freeze(audit, config, manifest)
        sources = read_rows(config["data"]["source_items"])
        rows = read_rows(config["data"]["variants"])
        prompts = read_rows(config["data"]["behavior_prompts"])
        augmented = read_rows(output / "extraction_rows.jsonl")
        behavior = read_rows(output / "behavior_outputs.jsonl")
        report["design_layout_diagnostics"] = layout_diagnostics(sources)
        report["limits"].extend([
            "Independent behavior question template B1/B2 is coupled with candidate display order.",
            "Candidate A always has a smaller numeric suffix than B; reversing this convention was not tested."])
        with np.load(output / "hidden_states.npz", allow_pickle=False) as archive:
            hidden = archive["hidden_states"].copy()
            audit.check("hidden_archive_row_ids", archive["variant_ids"].tolist() == [row["variant_id"] for row in rows])
        snapshot = path(config["runtime"]["shared_repo"]) / config["model"]["snapshot"]
        audit.check("pinned_snapshot_revision", snapshot.name == config["model"]["revision"])
        from transformers import AutoTokenizer
        tokenizer = AutoTokenizer.from_pretrained(str(snapshot), local_files_only=True)
        audit.check("pinned_boundary_token", tokenizer.convert_tokens_to_ids(config["model"]["boundary_token"]) == config["model"]["boundary_token_id"])
        cells, splits, tokens = audit_data(audit, config, sources, rows, prompts, augmented, hidden, tokenizer)
        audit_caches(audit, config, manifest, augmented, tokens, hidden, prompts, behavior, tokenizer)
        with np.load(output / "readout_directions.npz", allow_pickle=False) as archive:
            fitted = {name: archive[name].copy() for name in archive.files}
        provenance = read_json(output / "fitting_provenance.json")
        directions, controls = independent_fits(audit, config, augmented, cells, splits, hidden, fitted, provenance)
        report["recomputed"] = independent_analysis(audit, config, augmented, hidden, cells, splits,
                                                     directions, controls, read_json(output / "metrics.json"), behavior)
        report.update({"passed": True, "source_count": len(sources), "response_count": len(rows),
                       "behavior_prompt_count": len(prompts), "numeric_scalars_compared": audit.compared_scalars,
                       "maximum_absolute_numeric_difference": audit.maximum_absolute_difference,
                       "auditor_sha256": file_digest(Path(__file__))})
    except Exception as error:
        report.update({"passed": False, "error_type": type(error).__name__, "error": str(error),
                       "numeric_scalars_compared": audit.compared_scalars,
                       "maximum_absolute_numeric_difference": audit.maximum_absolute_difference})
    output.mkdir(parents=True, exist_ok=True)
    destination = output / "independent_audit.json"
    destination.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/evidence_confidence_v4.yaml")
    args = parser.parse_args()
    result = run(args.config)
    print(json.dumps({key: result.get(key) for key in ("passed", "source_count", "response_count", "behavior_prompt_count",
          "numeric_scalars_compared", "maximum_absolute_numeric_difference", "error")}, indent=2, allow_nan=False))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
