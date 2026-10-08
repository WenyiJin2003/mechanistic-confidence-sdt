"""Score-blind, source/template-disjoint evidence-support stimuli for v4.

Labels describe supplied contextual evidence, not subjective model confidence.
Only the pinned local tokenizer is consulted when choosing values and roles.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from copy import deepcopy
from itertools import combinations
from typing import Any

from confidence_pilot.common import read_jsonl, stable_hash, write_json, write_jsonl

VERSION = "evidence-sensitive-readout-v4"
FACT_TYPES = ("access_code", "room_assignment", "release_year", "material")
WORLDS = ("A", "B", "omitted")
ANSWER_KEYS = ("A", "B")
CERTAINTIES = ("neutral", "confident", "hedged")
SPLIT_COUNTS = {"train": 24, "validation": 6, "test": 12}
NUM_SOURCES = 168
EXPECTED_RESPONSES = 1584
EXPECTED_BEHAVIOR_PROMPTS = 144
DEFAULT_FRESHNESS = {
    "v1": "data/paired_confidence/source_items.jsonl",
    "v2": "data/confidence_transfer_v2/source_items.jsonl",
    "v3": "data/confidence_separation_v3/source_items.jsonl",
}
FACT_SPECS = {
    "access_code": {
        "entity_kind": "Vault", "target_role": "access code", "distractor_role": "locker code",
        "omission_roles": ("parcel code", "ticket code", "basket code", "receipt code", "invoice code"),
        "value_format": "{number}", "value_start": 620000,
        "questions": {
            "T1": "Which access code is assigned to {entity}?",
            "T2": "What access code does the registry give for {entity}?",
            "T3": "According to this record, what is the access code for {entity}?",
            "T4": "Find the code for access to {entity} in this registry.",
            "B1": "What value belongs to the access-code field at {entity}?",
            "B2": "Give the registry's access code for {entity}.",
        },
    },
    "room_assignment": {
        "entity_kind": "Academy", "target_role": "seminar room", "distractor_role": "storage room",
        "omission_roles": ("meeting room", "reading room", "practice room", "supply room", "break room"),
        "value_format": "Suite {number}", "value_start": 7100,
        "questions": {
            "T1": "Which seminar room is assigned to {entity}?",
            "T2": "What seminar room does the registry give for {entity}?",
            "T3": "According to this record, what is the seminar room for {entity}?",
            "T4": "Find the room for seminars at {entity} in this registry.",
            "B1": "What room hosts seminars at {entity} according to the fields?",
            "B2": "Give the registry's seminar venue for {entity}.",
        },
    },
    "release_year": {
        "entity_kind": "Gazette", "target_role": "release year", "distractor_role": "survey year",
        "omission_roles": ("review year", "design year", "sketch year", "draft year", "planning year"),
        "value_format": "{number}", "value_start": 3100,
        "questions": {
            "T1": "Which release year is assigned to {entity}?",
            "T2": "What release year does the registry give for {entity}?",
            "T3": "According to this record, what is the release year for {entity}?",
            "T4": "Find the year of release for {entity} in this registry.",
            "B1": "In what year was {entity} released according to the fields?",
            "B2": "Give the registry's publication-release year for {entity}.",
        },
    },
    "material": {
        "entity_kind": "Beacon", "target_role": "shell material", "distractor_role": "stand material",
        "omission_roles": ("cover material", "lining material", "packing material", "banner material", "sleeve material"),
        "value_format": "ceramic mix {number}", "value_start": 8200,
        "questions": {
            "T1": "Which shell material is assigned to {entity}?",
            "T2": "What shell material does the registry give for {entity}?",
            "T3": "According to this record, what is the shell material for {entity}?",
            "T4": "Find the material for the shell of {entity} in this registry.",
            "B1": "What forms the outer shell of {entity} according to the fields?",
            "B2": "Give the registry's outer-shell composition for {entity}.",
        },
    },
}


def _tokenizer(config, tokenizer=None):
    if tokenizer is not None:
        return tokenizer
    from confidence_pilot.extract_activations import load_tokenizer
    return load_tokenizer(config)


def _tokens(row, tokenizer, config):
    from confidence_pilot.extract_activations import tokenize_variant
    return tokenize_variant(row, tokenizer, config)


def _old_catalogs(config):
    records = {}
    for name, path in config.get("freshness_sources", DEFAULT_FRESHNESS).items():
        records[name] = {"path": str(path), "rows": read_jsonl(path)}
    return records


def _values(record):
    """Read known answer fields without treating arbitrary words as values."""
    result = set()
    for field in ("value_A", "value_B", "true_value", "false_value", "correct_answer", "incorrect_answer", "answer", "correct_value", "wrong_value"):
        value = record.get(field)
        if isinstance(value, str):
            result.add(value)
    for field in ("candidate_values", "answers"):
        values = record.get(field, {})
        if isinstance(values, dict):
            result.update(value for value in values.values() if isinstance(value, str))
        elif isinstance(values, list):
            result.update(value for value in values if isinstance(value, str))
    return result


def _context(source, world, omission_roles):
    roles = {
        "A": {"A": source["target_role"], "B": source["distractor_role"]},
        "B": {"A": source["distractor_role"], "B": source["target_role"]},
        "omitted": {"A": omission_roles[0], "B": omission_roles[1]},
    }[world]
    template = source["context_template"]
    headers = {
        "T1": f"Fictional registry for {source['entity']}. Values and assigned fields:",
        "T2": f"Record for {source['entity']} (invented). The entries specify separate fields:",
        "T3": f"The following registry describes fictional {source['entity']}. Each value has its own field:",
        "T4": f"This entry concerns fictional {source['entity']}. Values are assigned to distinct fields:",
    }
    line_templates = {
        "T1": "{value} | {role}",
        "T2": "Listed value {value} belongs to field {role}.",
        "T3": "{value} is listed under {role}.",
        "T4": "Value: {value}; field: {role}.",
    }
    return "\n".join([headers[template]] + [
        line_templates[template].format(value=source["candidate_values"][key], role=roles[key])
        for key in source["candidate_order"]
    ])


def _claim(source, answer_key):
    entity, role, value = source["entity"], source["target_role"], source["candidate_values"][answer_key]
    return {
        "T1": f"The {role} for {entity} is {value}.",
        "T2": f"The registry assigns {value} as the {role} for {entity}.",
        "T3": f"For {entity}, the {role} is {value}.",
        "T4": f"{value} is the {role} recorded for {entity}.",
    }[source["context_template"]]


def _response(source, answer_key, certainty):
    claim = _claim(source, answer_key)
    if certainty == "neutral":
        return claim
    if source["context_template"] == "T3":
        prefix = "I am certain about this answer. " if certainty == "confident" else "I am uncertain about this answer. "
        return prefix + claim
    suffix = " I can state this with confidence." if certainty == "confident" else " I can only suggest this tentatively."
    return claim + suffix


def _behavior_question(source):
    question = FACT_SPECS[source["fact_type"]]["questions"][source["behavior_template"]].format(entity=source["entity"])
    return question + " Reply briefly with the value only. If the record does not establish the requested field, reply unknown."


def _value_positions(context, values, tokenizer):
    encoding = tokenizer(context, add_special_tokens=False, return_offsets_mapping=True)
    positions = {}
    for key, value in values.items():
        if context.count(value) != 1:
            raise ValueError("Each candidate must occur once in its context")
        start, stop = context.index(value), context.index(value) + len(value)
        positions[key] = [i for i, (left, right) in enumerate(encoding["offset_mapping"]) if left < stop and right > start]
    return positions


def _construct_sources(config, tokenizer):
    old_values = set().union(*[_values(row) for catalog in _old_catalogs(config).values() for row in catalog["rows"]])
    sources = []
    for fact_type in FACT_TYPES:
        spec = FACT_SPECS[fact_type]
        value_pool = [spec["value_format"].format(number=spec["value_start"] + i) for i in range(2048)]
        value_pool = [value for value in value_pool if value not in old_values]
        cursor = index = 0
        for split, count in SPLIT_COUNTS.items():
            for within_split in range(count):
                index += 1
                template = "T1" if split == "train" else "T2" if split == "validation" else "T3" if within_split < 6 else "T4"
                # Values come from predeclared numeric pools; tokenizer length is the only selection criterion.
                while True:
                    if cursor + 1 >= len(value_pool):
                        raise ValueError("Predeclared candidate pool exhausted")
                    value_a, value_b = value_pool[cursor:cursor + 2]
                    cursor += 2
                    if len(tokenizer(value_a, add_special_tokens=False)["input_ids"]) == len(tokenizer(value_b, add_special_tokens=False)["input_ids"]):
                        break
                source_id = f"v4-{fact_type}-{index:03d}"
                source = {
                    "source_id": source_id, "base_source_id": source_id,
                    "fact_type": fact_type, "entity": f"Avelune {spec['entity_kind']} {index:03d}",
                    "split": split, "context_template": template, "template_id": template,
                    "wording_id": template, "wording_family": template,
                    "behavior_template": "B1" if within_split % 2 == 0 else "B2",
                    "candidate_values": {"A": value_a, "B": value_b}, "value_A": value_a, "value_B": value_b,
                    "candidate_order": ["A", "B"] if within_split % 2 == 0 else ["B", "A"],
                    "target_role": spec["target_role"], "distractor_role": spec["distractor_role"],
                    "question": spec["questions"][template].format(entity=f"Avelune {spec['entity_kind']} {index:03d}"),
                    "dataset_version": VERSION,
                    "world_references": {key: {"correct_answer_key": key, "correct_value": value} for key, value in (("A", value_a), ("B", value_b))},
                    "provenance": {"method": "deterministic_fictional_registry", "real_world_entity": False,
                        "external_dataset": None, "selection_uses_model_scores": False,
                        "ground_truth_scope": "supplied_contextual_support", "model_calls": 0},
                }
                attempts = []
                for omission_roles in combinations(spec["omission_roles"], 2):
                    contexts = {world: _context(source, world, omission_roles) for world in WORLDS}
                    neutral_counts, behavior_counts, value_locations = {}, {}, {}
                    answer_counts = {}
                    for world, context in contexts.items():
                        row = {"variant_id": source_id + "--gate", "question": source["question"], "context": context, "response_text": _claim(source, "A")}
                        neutral_counts[world] = _tokens(row, tokenizer, config)["prompt_length"]
                        value_locations[world] = _value_positions(context, source["candidate_values"], tokenizer)
                        if split == "test":
                            for key in ANSWER_KEYS:
                                behavior = {**row, "question": _behavior_question(source), "response_text": source["candidate_values"][key]}
                                token = _tokens(behavior, tokenizer, config)
                                behavior_counts[world] = token["prompt_length"]
                                answer_counts[f"{world}-{key}"] = len(token["response_ids"])
                    success = len(set(neutral_counts.values())) == 1 and all(location == value_locations["A"] for location in value_locations.values())
                    if split == "test":
                        success &= len(set(behavior_counts.values())) == 1 and len(set(answer_counts.values())) == 1
                    attempts.append({"omission_roles": list(omission_roles), "extraction_prompt_counts": neutral_counts,
                        "behavior_prompt_counts": behavior_counts, "behavior_candidate_counts": answer_counts,
                        "candidate_context_token_positions": value_locations, "passed": bool(success)})
                    if success:
                        source.update({"omission_roles": list(omission_roles), "contexts": contexts,
                            "tokenization_audit": {"selection_method": "first_predeclared_role_pair_passing_exact_token_gates",
                                "attempts": attempts, "prompt_token_counts": neutral_counts,
                                "candidate_context_token_positions": value_locations, "model_calls": 0}})
                        break
                else:
                    raise ValueError(f"No tokenizer-matched omission roles for {source_id}: {attempts}")
                sources.append(source)
    return sources


def _row_token_metadata(row, tokenizer, config):
    tokens = _tokens(row, tokenizer, config)
    response, answer = row["response_text"], row["answer_span_text"]
    if response.count(answer) != 1:
        raise ValueError("Answer span must occur exactly once")
    encoded = tokenizer(response, add_special_tokens=False, return_offsets_mapping=True)
    if encoded["input_ids"] != tokens["response_ids"]:
        raise ValueError("Response encoding differs at chat boundary")
    start, stop = response.index(answer), response.index(answer) + len(answer)
    relative = [i for i, (left, right) in enumerate(encoded["offset_mapping"]) if left < stop and right > start]
    positions = [tokens["response_start"] + i for i in relative]
    return {
        "prompt_token_count": tokens["prompt_length"], "token_count": len(tokens["response_ids"]),
        "char_count": len(response), "word_count": len(response.split()), "response_ids": tokens["response_ids"],
        "response_start_position": tokens["response_start"], "response_stop_position_exclusive": tokens["response_stop"],
        "boundary_position": tokens["boundary_position"], "final_content_position": tokens["final_content_position"],
        "answer_char_start": start, "answer_char_stop_exclusive": stop, "answer_token_positions": positions,
        "answer_start_position": positions[0], "answer_stop_position_exclusive": positions[-1] + 1,
        "prompt_ids_sha256": stable_hash(tokens["prompt_ids"]), "input_ids_sha256": stable_hash(tokens["input_ids"]),
    }


def _construct_rows(sources, tokenizer, config):
    rows = []
    for source in sources:
        styles = CERTAINTIES if source["split"] == "test" else ("neutral",)
        for world in WORLDS:
            for key in ANSWER_KEYS:
                correct = None if world == "omitted" else key == world
                support = "absent" if correct is None else "supported" if correct else "contradicted"
                for certainty in styles:
                    row = {
                        "variant_id": f"{source['source_id']}--{world}--answer-{key}--{certainty}",
                        "source_id": source["source_id"], "base_source_id": source["source_id"],
                        "prompt_group_id": f"{source['source_id']}--{world}",
                        "content_id": f"{source['source_id']}--answer-{key}",
                        "fact_type": source["fact_type"], "entity": source["entity"], "split": source["split"],
                        "context_template": source["context_template"], "template_id": source["template_id"],
                        "wording_id": source["wording_id"], "wording_family": source["wording_family"],
                        "question": source["question"], "context": source["contexts"][world],
                        "world": world, "answer_key": key, "certainty": certainty,
                        "certainty_label_scope": "authored_language_style",
                        "response_text": _response(source, key, certainty), "answer_span_text": source["candidate_values"][key],
                        "world_claim": _claim(source, key), "supplied_support": support, "condition": support,
                        "correctness": None if correct is None else "correct" if correct else "incorrect",
                        "reference_world": None if world == "omitted" else world,
                        "world_correct_value": None if world == "omitted" else source["candidate_values"][world],
                        "ground_truth_scope": "supplied_contextual_support", "format": "qa", "dataset_version": VERSION,
                    }
                    row.update(_row_token_metadata(row, tokenizer, config))
                    rows.append(row)
    return rows


def _construct_behavior(sources, tokenizer, config):
    prompts = []
    for source in sources:
        if source["split"] != "test":
            continue
        for world in WORLDS:
            candidate_tokens = {}
            for key in ANSWER_KEYS:
                row = {"variant_id": f"{source['source_id']}--behavior-{world}--answer-{key}",
                    "question": _behavior_question(source), "context": source["contexts"][world],
                    "response_text": source["candidate_values"][key]}
                candidate_tokens[key] = _tokens(row, tokenizer, config)
            token = candidate_tokens["A"]
            prompts.append({
                "behavior_id": f"{source['source_id']}--behavior-{world}",
                "source_id": source["source_id"], "base_source_id": source["source_id"],
                "prompt_group_id": f"{source['source_id']}--behavior-{world}",
                "fact_type": source["fact_type"], "entity": source["entity"], "split": "test", "world": world,
                "context_template": source["context_template"], "template_id": source["template_id"],
                "behavior_template": source["behavior_template"], "question": _behavior_question(source),
                "extraction_question": source["question"], "context": source["contexts"][world],
                "candidate_answers": deepcopy(source["candidate_values"]), "candidate_order": source["candidate_order"],
                "correct_answer_key": None if world == "omitted" else world,
                "correct_value": None if world == "omitted" else source["candidate_values"][world],
                "expected_abstention": world == "omitted", "unknown_answer": "unknown",
                "prompt_ids": token["prompt_ids"], "prompt_ids_sha256": stable_hash(token["prompt_ids"]),
                "prompt_token_count": token["prompt_length"],
                "candidate_response_ids": {key: candidate_tokens[key]["response_ids"] for key in ANSWER_KEYS},
                "candidate_token_counts": {key: len(candidate_tokens[key]["response_ids"]) for key in ANSWER_KEYS},
                "dataset_version": VERSION,
                "interpretation_limit": "Two-candidate normalized likelihood is preference among these values, not calibrated confidence; unknown and other generations are retained.",
            })
    return prompts


def _freshness(sources, rows, behavior, config):
    catalogs = {}
    for name, catalog in _old_catalogs(config).items():
        old = catalog["rows"]
        old_text = "\n".join(str(row) for row in old)
        old_values = set().union(*[_values(row) for row in old])
        overlaps = {
            "source_ids": sorted({source["source_id"] for source in sources} & {str(row.get("source_id")) for row in old}),
            "entities": [source["entity"] for source in sources if source["entity"] in old_text],
            "questions": sorted(({row["question"] for row in rows} | {row["question"] for row in behavior}) & {row.get("question", row.get("qa_question")) for row in old}),
            "candidate_values": sorted({value for source in sources for value in source["candidate_values"].values()} & old_values),
        }
        catalogs[name] = {"path": catalog["path"], "source_count": len(old), "overlaps": overlaps}
    split_sets = {}
    for split in SPLIT_COUNTS:
        chosen = [source for source in sources if source["split"] == split]
        split_sets[split] = {"source_ids": {source["source_id"] for source in chosen},
            "entities": {source["entity"] for source in chosen},
            "candidate_values": {value for source in chosen for value in source["candidate_values"].values()},
            "templates": {source["context_template"] for source in chosen}}
    split_overlaps = {f"{left}--{right}": {field: sorted(split_sets[left][field] & split_sets[right][field]) for field in split_sets[left]}
        for left, right in combinations(SPLIT_COUNTS, 2)}
    all_new = not any(values for catalog in catalogs.values() for values in catalog["overlaps"].values())
    all_new &= not any(values for overlap in split_overlaps.values() for values in overlap.values())
    return {"catalogs": catalogs, "split_overlaps": split_overlaps, "all_keys_new": bool(all_new),
        "split_candidate_value_counts": {split: len(values["candidate_values"]) for split, values in split_sets.items()},
        "shared_fact_schemas_intentional": True, "numeric_value_pools_are_disjoint_from_prior_answers": True}


def validate_dataset(sources, rows, behavior_prompts, config, tokenizer=None):
    """Validate complete crossings, source splits, token identities, and authored labels."""
    tokenizer = _tokenizer(config, tokenizer)
    errors = []
    expected_sources = _construct_sources(config, tokenizer)
    expected_rows = _construct_rows(expected_sources, tokenizer, config)
    expected_behavior = _construct_behavior(expected_sources, tokenizer, config)
    for supplied, expected, description in ((sources, expected_sources, "source catalog"), (rows, expected_rows, "variant catalog"), (behavior_prompts, expected_behavior, "behavior catalog")):
        if supplied != expected:
            errors.append(f"The {description} differs from the deterministic tokenizer-gated design.")
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["source_id"]].append(row)
    world_checks = []
    for source in sources:
        lookup = {(row["world"], row["answer_key"], row["certainty"]): row for row in grouped[source["source_id"]]}
        styles = CERTAINTIES if source["split"] == "test" else ("neutral",)
        for key in ANSWER_KEYS:
            for style in styles:
                chosen = [lookup.get((world, key, style)) for world in WORLDS]
                if any(row is None for row in chosen):
                    errors.append(f"Incomplete three-world answer/style crossing: {source['source_id']}")
                    continue
                fields = ("response_text", "response_ids", "prompt_token_count", "response_start_position", "answer_token_positions", "boundary_position", "final_content_position")
                identity = {field: all(row[field] == chosen[0][field] for row in chosen) for field in fields}
                world_checks.append({"source_id": source["source_id"], "answer_key": key, "certainty": style, **identity})
                if not all(identity.values()):
                    errors.append(f"Token/position identity gate failed: {source['source_id']} {key} {style}")
    behavior_groups = defaultdict(list)
    for row in behavior_prompts:
        behavior_groups[row["source_id"]].append(row)
    behavior_checks = []
    for source_id, group in behavior_groups.items():
        passed = len(group) == 3 and {row["world"] for row in group} == set(WORLDS)
        passed &= len({row["prompt_token_count"] for row in group}) == 1
        passed &= len({count for row in group for count in row["candidate_token_counts"].values()}) == 1
        passed &= all(row["question"] != row["extraction_question"] for row in group)
        passed &= all(row["candidate_response_ids"] == group[0]["candidate_response_ids"] for row in group)
        behavior_checks.append({"source_id": source_id, "passed": bool(passed)})
        if not passed:
            errors.append(f"Behavior prompt/candidate gate failed: {source_id}")
    freshness = _freshness(sources, rows, behavior_prompts, config)
    if not freshness["all_keys_new"]:
        errors.append("Source/entity/question/value/template overlap with earlier catalogs or another split.")
    if (len(sources), len(rows), len(behavior_prompts)) != (NUM_SOURCES, EXPECTED_RESPONSES, EXPECTED_BEHAVIOR_PROMPTS):
        errors.append("Source, response, or behavior count differs from the fixed design.")
    return {
        "passed": not errors, "errors": errors, "dataset_version": VERSION,
        "num_sources": len(sources), "num_rows": len(rows), "num_behavior_prompts": len(behavior_prompts),
        "source_split_counts": dict(Counter(source["split"] for source in sources)),
        "source_fact_split_counts": {fact: dict(Counter(source["split"] for source in sources if source["fact_type"] == fact)) for fact in FACT_TYPES},
        "source_template_counts": dict(Counter(source["context_template"] for source in sources)),
        "candidate_order_counts": dict(Counter("-".join(source["candidate_order"]) for source in sources)),
        "certainty_row_counts": dict(Counter(row["certainty"] for row in rows)),
        "world_row_counts": dict(Counter(row["world"] for row in rows)),
        "correctness_row_counts": dict(Counter(str(row["correctness"]) for row in rows)),
        "world_identity_checks": world_checks, "behavior_checks": behavior_checks,
        "source_freshness": freshness, "model_scoring_calls": 0, "model_generation_calls": 0,
        "nli_calls": 0, "openai_api_calls": 0, "downloads": 0,
        "catalog_sha256": stable_hash({"sources": sources, "rows": rows, "behavior_prompts": behavior_prompts}),
        "omission_role_edit_counts_by_answer_key": {"A": 2, "B": 2},
        "interpretation_limit": "A contextual evidence-support classifier is not by itself a validated measure of subjective confidence. Behavioral agreement is convergent validation, not causality or calibrated belief.",
    }


def build_dataset(config, tokenizer=None):
    """Return sources, authored rows, independent behavior prompts, and scoreless audit."""
    tokenizer = _tokenizer(config, tokenizer)
    sources = _construct_sources(config, tokenizer)
    rows = _construct_rows(sources, tokenizer, config)
    behavior = _construct_behavior(sources, tokenizer, config)
    audit = validate_dataset(sources, rows, behavior, config, tokenizer)
    if not audit["passed"]:
        raise ValueError("V4 dataset gates failed: " + "; ".join(audit["errors"]))
    return sources, rows, behavior, audit


def write_dataset(config, tokenizer=None):
    """Write atomic local data artifacts; no model weights are loaded or changed."""
    sources, rows, behavior, audit = build_dataset(config, tokenizer)
    data = config.get("data", {})
    write_jsonl(data.get("source_items", "data/evidence_readout_v4/source_items.jsonl"), sources)
    write_jsonl(data.get("variants", "data/evidence_readout_v4/variants.jsonl"), rows)
    write_jsonl(data.get("behavior_prompts", "data/evidence_readout_v4/behavior_prompts.jsonl"), behavior)
    write_json(data.get("audit", "data/evidence_readout_v4/data_audit.json"), audit)
    return sources, rows, behavior, audit
