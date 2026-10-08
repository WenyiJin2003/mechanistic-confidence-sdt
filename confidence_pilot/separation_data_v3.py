"""Fresh, score-blind, fully crossed fictional record stimuli for v3.

The A/B worlds swap *roles*, while both candidate values keep their written
positions.  Correctness means agreement with the displayed world's reference;
it is not an independently manipulated epistemic or real-world truth label.
Only the pinned tokenizer is used here.  No model, probe, or outcome is loaded.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from confidence_pilot.common import (
    load_config, read_jsonl, resolve, stable_hash, write_json, write_jsonl,
)

VERSION = "confidence-separation-v3"
FACT_TYPES = ("access_code", "room_assignment", "release_year", "material")
WORLDS = ("A", "B")
ANSWER_KEYS = ("A", "B")
CERTAINTIES = ("confident", "hedged", "neutral")
NUM_SOURCES = 48
EXPECTED_RESPONSES = 672
DEFAULT_OUTPUT_DIR = "data/confidence_separation_v3"

# These lists are authored explicitly rather than sampled from prior stimuli.
# Candidate ordering, family assignment, and every value pair are fixed before
# tokenization.  All records describe benign, expressly fictional objects.
CATALOG = {
    "access_code": (
        ("Larkspur Depot", "4712", "8635"),
        ("Cobalt Depot", "5928", "7146"),
        ("Merryn Depot", "6384", "9251"),
        ("Brindle Depot", "2579", "4863"),
        ("Auburn Depot", "8194", "3627"),
        ("Ternwick Depot", "7432", "1586"),
        ("Nettle Depot", "9264", "5731"),
        ("Plover Depot", "3847", "6192"),
        ("Rillbank Depot", "1658", "9423"),
        ("Fenlight Depot", "8276", "4539"),
        ("Mossfield Depot", "6913", "2784"),
        ("Kestrel Depot", "5326", "8971"),
    ),
    "room_assignment": (
        ("Lantern Workshop", "Amber Studio", "Azure Studio"),
        ("Ripple Workshop", "Indigo Studio", "Scarlet Studio"),
        ("Harbor Workshop", "Ivory Studio", "Sienna Studio"),
        ("Pebble Workshop", "Coral Studio", "Ochre Studio"),
        ("Saffron Workshop", "Silver Studio", "Golden Studio"),
        ("Tinsel Workshop", "Violet Studio", "Crimson Studio"),
        ("Loom Workshop", "Honey Studio", "Rust Studio"),
        ("Marigold Workshop", "Pearl Studio", "Teal Studio"),
        ("Copperleaf Workshop", "Olive Studio", "Plum Studio"),
        ("Sorrel Workshop", "Rose Studio", "Mint Studio"),
        ("Velvet Workshop", "Slate Studio", "Navy Studio"),
        ("Hearth Workshop", "Blush Studio", "Cyan Studio"),
    ),
    "release_year": (
        ("Moonwake Almanac", "2041", "2058"),
        ("Duskwell Almanac", "2042", "2069"),
        ("Glassfin Almanac", "2043", "2074"),
        ("Waystone Almanac", "2044", "2081"),
        ("Thistlebay Almanac", "2045", "2062"),
        ("Sundrift Almanac", "2046", "2077"),
        ("Lindenmark Almanac", "2047", "2088"),
        ("Rainforge Almanac", "2048", "2053"),
        ("Tidebell Almanac", "2049", "2064"),
        ("Wrenpath Almanac", "2050", "2071"),
        ("Cloudmere Almanac", "2051", "2086"),
        ("Starling Almanac", "2052", "2067"),
    ),
    "material": (
        ("Petal Lamp", "granite", "marble"),
        ("Moraine Lamp", "sandstone", "limestone"),
        ("Fable Lamp", "oak veneer", "ash veneer"),
        ("Compass Lamp", "beech timber", "pine timber"),
        ("Seabrook Lamp", "mohair", "cashmere"),
        ("Bramble Lamp", "hemp canvas", "jute canvas"),
        ("Hollow Lamp", "polyester", "acrylic"),
        ("Bellweather Lamp", "titanium", "nickel"),
        ("Aster Lamp", "slate", "travertine"),
        ("Rook Lamp", "suede", "denim"),
        ("Dapple Lamp", "porcelain", "terracotta"),
        ("Wisp Lamp", "rattan", "fiberglass"),
    ),
}

FACT_SPECS = {
    "access_code": {
        "record_kind": "depot", "target_role": "entry code",
        "distractor_role": "parcel code",
        "omission_roles": ("ticket code", "basket code", "receipt code", "invoice code"),
        "question": "Which code opens the entry gate at {entity}?",
        "claim": "{entity} uses {value} as its entry gate code.",
    },
    "room_assignment": {
        "record_kind": "workshop", "target_role": "event room",
        "distractor_role": "staff room",
        "omission_roles": ("break room", "supply room", "reading room", "practice room"),
        "question": "In which room does {entity} hold its event?",
        "claim": "The event for {entity} takes place in {value}.",
    },
    "release_year": {
        "record_kind": "publication", "target_role": "first release",
        "distractor_role": "site survey",
        "omission_roles": ("early sketch", "draft review", "cover design", "index update"),
        "question": "In which year was {entity} first released?",
        "claim": "{entity} was first released in {value}.",
    },
    "material": {
        "record_kind": "lamp", "target_role": "outer shell",
        "distractor_role": "display stand",
        "omission_roles": ("packing sleeve", "shipping cover", "display banner", "storage liner"),
        "question": "What material forms the outer shell of {entity}?",
        "claim": "{entity} has an outer shell made of {value}.",
    },
}

# Certainty is an authored language manipulation, never a model-internal label.
# F1 makes the assertive response shorter; F2 holds word length exactly equal;
# F3 makes it longer.  Each family receives four sources per fact type.
WORDING_FAMILIES = {
    "F1": {
        "confident": "Unequivocally, {lower_claim}",
        "hedged": "As far as I can tell, {lower_claim}",
        "review": "Unequivocally endorses the proposition; as far as I can tell qualifies that same proposition. Neither supplies new evidence.",
    },
    "F2": {
        "confident": "{claim} I have no reservations about that answer.",
        "hedged": "{claim} I have some reservations about that answer.",
        "review": "No versus some reservations changes the epistemic qualification of the preceding proposition without adding evidence or an alternative answer.",
    },
    "F3": {
        "confident": "{claim} I would give that answer without any further qualification.",
        "hedged": "My answer, subject to revision, is that {lower_claim}",
        "review": "Without further qualification endorses the proposition; subject to revision qualifies the same proposition. Neither supplies new evidence.",
    },
}


def _claim(fact_type: str, entity: str, value: str) -> str:
    return FACT_SPECS[fact_type]["claim"].format(entity=entity, value=value)


def _response(claim: str, wording_id: str, certainty: str) -> str:
    if certainty == "neutral":
        return claim
    # Lower the ordinary article when embedding a sentence, never a proper name.
    lower_claim = "the " + claim[4:] if claim.startswith("The ") else claim
    return WORDING_FAMILIES[wording_id][certainty].format(
        claim=claim, lower_claim=lower_claim,
    )


def _context(source: dict[str, Any], world: str, omission_role: str) -> str:
    """Keep each candidate at one fixed written position across all contexts."""
    roles = {
        "A": {"A": source["target_role"], "B": source["distractor_role"]},
        "B": {"A": source["distractor_role"], "B": source["target_role"]},
        "omitted": {"A": omission_role, "B": source["distractor_role"]},
    }[world]
    lines = [f"Fictional {source['record_kind']} record: {source['entity']}.",
             "Each line names a value and the separate field it belongs to."]
    for key in source["candidate_order"]:
        lines.append(f"{source['candidate_values'][key]}: {roles[key]}")
    return "\n".join(lines)


def _tokenizer(config: dict[str, Any], tokenizer: Any | None) -> Any:
    if tokenizer is not None:
        return tokenizer
    from confidence_pilot.extract_activations import load_tokenizer
    return load_tokenizer(config)


def _tokens(row: dict[str, Any], tokenizer: Any, config: dict[str, Any]) -> dict[str, Any]:
    from confidence_pilot.extract_activations import tokenize_variant
    return tokenize_variant(row, tokenizer, config)


def _prompt_count(source: dict[str, Any], context: str, tokenizer: Any,
                  config: dict[str, Any]) -> int:
    row = {"variant_id": source["source_id"] + "--tokenizer-audit",
           "question": source["question"], "context": context,
           "response_text": _claim(source["fact_type"], source["entity"], source["value_A"])}
    return _tokens(row, tokenizer, config)["prompt_length"]


def _construct_sources(config: dict[str, Any], tokenizer: Any) -> list[dict[str, Any]]:
    sources = []
    for fact_type in FACT_TYPES:
        spec = FACT_SPECS[fact_type]
        for index, (entity, value_a, value_b) in enumerate(CATALOG[fact_type]):
            source = {
                "source_id": f"v3-{fact_type}-{index + 1:02d}",
                "base_source_id": f"v3-{fact_type}-{index + 1:02d}",
                "fact_type": fact_type, "entity": entity,
                "record_kind": spec["record_kind"], "value_A": value_a, "value_B": value_b,
                "candidate_values": {"A": value_a, "B": value_b},
                "candidate_order": ["A", "B"] if index % 2 == 0 else ["B", "A"],
                "target_role": spec["target_role"], "distractor_role": spec["distractor_role"],
                "question": spec["question"].format(entity=entity),
                "wording_id": f"F{index % 3 + 1}", "wording_family": f"F{index % 3 + 1}", "split": "test",
                "dataset_version": VERSION,
                "world_references": {
                    "A": {"correct_answer_key": "A", "correct_value": value_a},
                    "B": {"correct_answer_key": "B", "correct_value": value_b},
                },
                "provenance": {"method": "independently_authored_fictional_records",
                    "real_world_entity": False, "external_dataset": None,
                    "sampling_used": False, "ground_truth_scope": "displayed_world_reference",
                    "selection_uses_model_scores": False,
                    "configured_dataset_seed_samples_facts": False,
                    "omission_role_edit_counts_from_supporting_world": {"A": 1, "B": 2}},
            }
            attempts = []
            for omission_role in spec["omission_roles"]:
                contexts = {world: _context(source, world, omission_role)
                            for world in (*WORLDS, "omitted")}
                counts = {world: _prompt_count(source, context, tokenizer, config)
                          for world, context in contexts.items()}
                attempts.append({"omission_role": omission_role, "prompt_token_counts": counts})
                if len(set(counts.values())) == 1:
                    source.update({"omission_role": omission_role, "contexts": contexts,
                        "tokenization_audit": {
                            "selection_method": "first_predeclared_unrelated_role_with_exact_prompt_token_match",
                            "attempted_roles": attempts, "prompt_token_counts": counts,
                            "model_scoring_calls": 0,
                        }})
                    break
            else:
                raise ValueError(f"No tokenizer-only omission role matches for {source['source_id']}: {attempts}")
            sources.append(source)
    return sources


def _answer_positions(row: dict[str, Any], tokens: dict[str, Any], tokenizer: Any) -> dict[str, Any]:
    response = row["response_text"]
    answer = row["answer_span_text"]
    if response.count(answer) != 1:
        raise ValueError(f"Answer span must appear once: {row['variant_id']}")
    encoded = tokenizer(response, add_special_tokens=False, return_offsets_mapping=True)
    if encoded["input_ids"] != tokens["response_ids"]:
        raise ValueError(f"Standalone response tokenization changed: {row['variant_id']}")
    start = response.index(answer)
    stop = start + len(answer)
    relative = [index for index, (left, right) in enumerate(encoded["offset_mapping"])
                if left < stop and right > start]
    if not relative:
        raise ValueError(f"No answer-token span: {row['variant_id']}")
    absolute = [tokens["response_start"] + index for index in relative]
    return {"answer_char_start": start, "answer_char_stop_exclusive": stop,
            "answer_token_positions": absolute,
            "answer_start_position": absolute[0],
            "answer_stop_position_exclusive": absolute[-1] + 1}


def _construct_rows(sources: list[dict[str, Any]], tokenizer: Any,
                    config: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for source in sources:
        for world in (*WORLDS, "omitted"):
            certainties = ("neutral",) if world == "omitted" else CERTAINTIES
            for answer_key in ANSWER_KEYS:
                value = source["candidate_values"][answer_key]
                claim = _claim(source["fact_type"], source["entity"], value)
                correct = None if world == "omitted" else answer_key == world
                for certainty in certainties:
                    response = _response(claim, source["wording_id"], certainty)
                    support = "absent" if correct is None else "supported" if correct else "contradicted"
                    row = {
                        "variant_id": f"{source['source_id']}--{world}--answer-{answer_key}--{certainty}",
                        "source_id": source["source_id"], "base_source_id": source["source_id"],
                        "prompt_group_id": f"{source['source_id']}--{world}",
                        "content_id": f"{source['source_id']}--answer-{answer_key}",
                        "fact_type": source["fact_type"], "entity": source["entity"],
                        "experiment": "omitted_control" if world == "omitted" else "world_factorial",
                        "format": "qa", "world": world, "answer_key": answer_key,
                        "correctness": None if correct is None else "correct" if correct else "incorrect",
                        "supplied_support": support, "condition": support,
                        "certainty": certainty, "certainty_label_scope": "authored_language_style",
                        "wording_id": source["wording_id"], "wording_family": source["wording_id"],
                        "question": source["question"], "context": source["contexts"][world],
                        "response_text": response, "answer_span_text": value, "world_claim": claim,
                        "reference_world": None if world == "omitted" else world,
                        "world_correct_value": None if world == "omitted" else source["candidate_values"][world],
                        "ground_truth_scope": "displayed_world_reference" if world != "omitted" else "not_defined",
                        "split": "test", "dataset_version": VERSION,
                    }
                    tokens = _tokens(row, tokenizer, config)
                    row.update({"prompt_token_count": tokens["prompt_length"],
                        "token_count": len(tokens["response_ids"]),
                        "char_count": len(response), "word_count": len(response.split()),
                        "response_ids": tokens["response_ids"],
                        "response_start_position": tokens["response_start"],
                        "response_stop_position_exclusive": tokens["response_stop"],
                        "boundary_position": tokens["boundary_position"],
                        "final_content_position": tokens["final_content_position"]})
                    row.update(_answer_positions(row, tokens, tokenizer))
                    rows.append(row)
    return rows


def _freshness(sources: list[dict[str, Any]], rows: list[dict[str, Any]],
               config: dict[str, Any]) -> dict[str, Any]:
    paths = config.get("freshness_sources", {
        "v1": "data/paired_confidence/source_items.jsonl",
        "v2": "data/confidence_transfer_v2/source_items.jsonl",
    })
    records = {}
    for name, path in paths.items():
        old = read_jsonl(path)
        old_text = "\n".join(str(record) for record in old)
        overlaps = {
            "source_ids": sorted({source["source_id"] for source in sources}
                                 & {record["source_id"] for record in old}),
            "entities": [source["entity"] for source in sources if source["entity"] in old_text],
            "questions": sorted({source["question"] for source in sources}
                                & {record.get("question", record.get("qa_question")) for record in old}),
            "contexts": sorted({context for source in sources for context in source["contexts"].values()}
                               & {record.get("context") for record in old}),
        }
        records[name] = {"path": str(path), "source_count": len(old), "overlaps": overlaps}
    previous_rows = []
    for path in ("data/paired_confidence/variants.jsonl", "data/confidence_transfer_v2/variants.jsonl"):
        if resolve(path).exists():
            previous_rows.extend(read_jsonl(path))
    response_overlap = sorted({row["response_text"] for row in rows}
                              & {row["response_text"] for row in previous_rows})
    return {"catalogs": records, "prior_response_exact_overlap": response_overlap,
            "all_keys_new": not response_overlap and not any(
                items for record in records.values() for items in record["overlaps"].values()),
            "shared_fact_types_are_intentional": True,
            "exact_answer_vocabulary_overlap_not_a_freshness_failure": True}


def validate_separation_dataset(sources: list[dict[str, Any]], rows: list[dict[str, Any]],
                                config: dict[str, Any], tokenizer: Any | None = None) -> dict[str, Any]:
    """Reject incomplete crossings, truth relabeling, and unmatched positions."""
    tokenizer = _tokenizer(config, tokenizer)
    errors = []
    expected_sources = _construct_sources(config, tokenizer)
    expected_rows = _construct_rows(expected_sources, tokenizer, config)
    if sources != expected_sources:
        errors.append("Source catalog differs from the explicitly authored, token-matched design.")
    by_id = {row["variant_id"]: row for row in rows}
    if len(by_id) != len(rows):
        errors.append("Duplicate variant IDs.")
    expected_by_id = {row["variant_id"]: row for row in expected_rows}
    if set(by_id) != set(expected_by_id):
        errors.append("Incomplete or unexpected variant catalog.")
    for variant_id, expected in expected_by_id.items():
        if variant_id in by_id and any(by_id[variant_id].get(key) != value for key, value in expected.items()):
            errors.append(f"Written content, label, or token metadata differs: {variant_id}")

    grouped = defaultdict(list)
    for row in rows:
        grouped[row["source_id"]].append(row)
    world_checks, style_checks, omitted_checks = [], [], []
    for source in sources:
        chosen = grouped[source["source_id"]]
        lookup = {(row["world"], row["answer_key"], row["certainty"]): row for row in chosen}
        for key in ANSWER_KEYS:
            for certainty in CERTAINTIES:
                pair = [lookup.get((world, key, certainty)) for world in WORLDS]
                if any(row is None for row in pair):
                    continue
                world_checks.append({"source_id": source["source_id"], "answer_key": key,
                    "certainty": certainty,
                    "response_text_identical": pair[0]["response_text"] == pair[1]["response_text"],
                    "response_ids_identical": pair[0]["response_ids"] == pair[1]["response_ids"],
                    "prompt_token_count_identical": pair[0]["prompt_token_count"] == pair[1]["prompt_token_count"],
                    "answer_positions_identical": pair[0]["answer_token_positions"] == pair[1]["answer_token_positions"],
                    "boundary_positions_identical": pair[0]["boundary_position"] == pair[1]["boundary_position"],
                    "correctness_flips": {row["correctness"] for row in pair} == {"correct", "incorrect"}})
            support = lookup.get((key, key, "neutral"))
            omitted = lookup.get(("omitted", key, "neutral"))
            if support is not None and omitted is not None:
                omitted_checks.append({"source_id": source["source_id"], "answer_key": key,
                    "role_label_edits_from_supporting_world": 1 if key == "A" else 2,
                    "response_text_identical": support["response_text"] == omitted["response_text"],
                    "response_ids_identical": support["response_ids"] == omitted["response_ids"],
                    "answer_positions_identical": support["answer_token_positions"] == omitted["answer_token_positions"],
                    "prompt_token_count_identical": support["prompt_token_count"] == omitted["prompt_token_count"],
                    "omitted_correctness_undefined": omitted["correctness"] is None})
            for world in WORLDS:
                confident = lookup.get((world, key, "confident"))
                hedged = lookup.get((world, key, "hedged"))
                if confident is not None and hedged is not None:
                    style_checks.append({"source_id": source["source_id"], "world": world,
                        "answer_key": key, "wording_id": source["wording_id"],
                        "claim_identical": confident["world_claim"] == hedged["world_claim"],
                        "prompt_identical": confident["context"] == hedged["context"],
                        "correctness_identical": confident["correctness"] == hedged["correctness"],
                        "token_length_delta_confident_minus_hedged": confident["token_count"] - hedged["token_count"],
                        "word_length_delta_confident_minus_hedged": confident["word_count"] - hedged["word_count"],
                        "char_length_delta_confident_minus_hedged": confident["char_count"] - hedged["char_count"]})
    for checks, name in ((world_checks, "World identity"), (omitted_checks, "Omission identity")):
        if any(value is False for check in checks for value in check.values()):
            errors.append(f"{name} gate failed.")
    if any(value is False for check in style_checks for value in check.values()):
        errors.append("Style proposition/prompt gate failed.")
    if len(world_checks) != 288 or len(style_checks) != 192 or len(omitted_checks) != 96:
        errors.append("Pair-count gate failed.")
    freshness = _freshness(sources, rows, config)
    if not freshness["all_keys_new"]:
        errors.append("A source ID, entity, question, context, or full response overlaps a prior catalog.")
    role_lengths = {source["source_id"]: source["tokenization_audit"]["prompt_token_counts"] for source in sources}
    return {
        "passed": not errors, "errors": errors, "dataset_version": VERSION,
        "num_sources": len(sources), "num_rows": len(rows),
        "fact_type_counts": dict(Counter(source["fact_type"] for source in sources)),
        "wording_family_source_counts": dict(Counter(source["wording_id"] for source in sources)),
        "candidate_order_counts": dict(Counter("-".join(source["candidate_order"]) for source in sources)),
        "world_row_counts": dict(Counter(row["world"] for row in rows)),
        "certainty_row_counts": dict(Counter(row["certainty"] for row in rows)),
        "correctness_row_counts": dict(Counter(str(row["correctness"]) for row in rows)),
        "supplied_support_row_counts": dict(Counter(row["supplied_support"] for row in rows)),
        "primary_neutral_world_pair_count": 96,
        "all_certainty_world_pair_count": len(world_checks),
        "confidence_pair_count": len(style_checks), "support_omission_pair_count": len(omitted_checks),
        "world_identity_checks": world_checks, "style_checks": style_checks,
        "omission_identity_checks": omitted_checks, "prompt_token_counts": role_lengths,
        "source_freshness": freshness, "wording_families": WORDING_FAMILIES,
        "tokenizer_called": True, "model_scoring_calls": 0, "model_generation_calls": 0,
        "nli_calls": 0, "openai_api_calls": 0, "downloads": 0,
        "catalog_sha256": stable_hash({"sources": sources, "rows": rows}),
        "interpretation_limit": "Correctness is defined by the displayed fictional world and covaries with supplied support. This cannot isolate factual truth from contextual evidence or identify model-internal confidence.",
        "omission_role_edit_counts_by_answer_key": {"A": 1, "B": 2},
        "wording_diversity_limit": "Three fixed wording families offer less linguistic diversity than the twelve v2 pairs.",
        "dataset_seed_role": "The facts, names, order, and family assignments are explicitly authored. The configured dataset seed does not sample this catalog.",
    }


def build_dataset(config: dict[str, Any], tokenizer: Any | None = None):
    """Build all 672 stimuli and pass scoreless gates before any extraction."""
    tokenizer = _tokenizer(config, tokenizer)
    sources = _construct_sources(config, tokenizer)
    rows = _construct_rows(sources, tokenizer, config)
    audit = validate_separation_dataset(sources, rows, config, tokenizer)
    if not audit["passed"]:
        raise ValueError("V3 dataset gates failed: " + "; ".join(audit["errors"]))
    return sources, rows, audit


def _manual_audit(sources: list[dict[str, Any]], audit: dict[str, Any]) -> str:
    lines = ["# Confidence separation v3: scoreless dataset audit", "",
        "The 48 expressly fictional records are newly authored. Both candidate values stay at fixed written positions in worlds A, B, and the omitted view. World A assigns candidate A to the queried role; world B assigns candidate B to that role. The other value belongs to an unrelated role. The omitted view assigns both values to unrelated roles and defines no correctness label.", "",
        "Correctness means agreement with the displayed world reference. It changes together with supplied support, so this study cannot distinguish factual correctness from consistency with contextual evidence. Confident and hedged labels refer to authored wording, not measured model-internal confidence.", "",
        "The single omitted context changes one role label from supporting world A and two from supporting world B. Supported-to-omitted comparisons therefore differ in role-edit count by answer key; both keys are balanced and reported separately. This endpoint does not isolate absence of evidence from every incidental role-label change.", "",
        "Each complete world contains both answer propositions in all three language styles. The primary neutral truth-swap comparisons use byte-identical responses and response token IDs, with equal rendered prompt lengths and answer/boundary positions. Support-to-omission neutral comparisons use the same controls. No model outcome was consulted in authoring or choosing the first predeclared token-matched unrelated role.", "",
        "## Fixed style families", "",
        "| Family | Confident | Hedged | Scoreless semantic review |", "| --- | --- | --- | --- |"]
    for family, wording in WORDING_FAMILIES.items():
        lines.append(f"| {family} | {wording['confident']} | {wording['hedged']} | {wording['review']} |")
    lines.extend(["", "Neutral wording is the single unqualified declarative claim. Each family is assigned to 16 sources: four per fact type. F1 makes assertive wording shorter, F2 matches word length, and F3 makes it longer. Wording length is deliberately varied; this design does not remove every linguistic cue to certainty. The three families provide less language diversity than the twelve v2 pairs.", "",
        "## Complete fictional world key", "",
        "| Source | Entity | A value | B value | Queried role | Unrelated role | Omitted replacement | Fixed value order | Family | A/B/omitted prompt tokens |", "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"])
    for source in sources:
        counts = source["tokenization_audit"]["prompt_token_counts"]
        lines.append(f"| {source['source_id']} | {source['entity']} | {source['value_A']} | {source['value_B']} | {source['target_role']} | {source['distractor_role']} | {source['omission_role']} | {' then '.join(source['candidate_order'])} | {source['wording_id']} | {counts['A']}/{counts['B']}/{counts['omitted']} |")
    lines.extend(["", "## Scoreless gates", "",
        f"- Sources: {audit['num_sources']}; rows: {audit['num_rows']}; all held out for this confirmatory experiment.",
        "- Main neutral identity comparisons: 96 pairs from 48 independent base sources.",
        "- Confidence wording comparisons: 192 pairs from the same 48 base sources.",
        "- Supported versus absent neutral comparisons: 96 pairs from the same 48 base sources.",
        "- All 288 A/B identity pairs pass identical response text, response IDs, prompt lengths, answer positions, and boundary positions.",
        "- Candidate order is balanced 24 A-first / 24 B-first, and remains fixed across all three contexts within a source.",
        "- Omitted rows have correctness=null and supplied_support=absent; they are not silently treated as true or false.",
        "- All 14 rows must remain together for source-clustered analysis. Extraction checks identical prompts within prompt_group_id, not across the three different worlds.",
        "- Prior v1/v2 source IDs, entity names, exact questions, exact contexts, and full responses have no overlap.",
        "- Names, facts, order, and family assignments are explicit fixed lists; the configured dataset seed does not sample the catalog.",
        "- Generation, model scoring, NLI, API calls, and downloads: zero.",
        f"- Catalog SHA-256: `{audit['catalog_sha256']}`.", ""])
    return "\n".join(lines)


def write_separation_dataset(config: dict[str, Any]) -> dict[str, Any]:
    """Write only the new v3 directory; previous experiment files are protected."""
    data = config.get("data", {})
    source_path = resolve(data.get("source_items", f"{DEFAULT_OUTPUT_DIR}/source_items.jsonl"))
    row_path = resolve(data.get("variants", f"{DEFAULT_OUTPUT_DIR}/variants.jsonl"))
    expected_dir = resolve(DEFAULT_OUTPUT_DIR)
    if source_path.parent != expected_dir or row_path.parent != expected_dir:
        raise ValueError("Only data/confidence_separation_v3 outputs are permitted; prior files are protected.")
    sources, rows, audit = build_dataset(config)
    write_jsonl(source_path, sources)
    write_jsonl(row_path, rows)
    write_json(expected_dir / "data_audit.json", audit)
    write_json(expected_dir / "wording_families.json", WORDING_FAMILIES)
    (expected_dir / "manual_audit.md").write_text(_manual_audit(sources, audit), encoding="utf-8")
    return audit


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/confidence_separation_v3.yaml")
    args = parser.parse_args()
    audit = write_separation_dataset(load_config(args.config))
    print(f"V3 scoreless dataset: {audit['num_sources']} sources, {audit['num_rows']} rows; gates passed={audit['passed']}")


if __name__ == "__main__":
    main()
