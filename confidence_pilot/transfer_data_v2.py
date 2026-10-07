"""Scoreless fictional-world transfer data; only the pinned tokenizer is loaded.

World correctness is fixed by construction.  Evidence conditions measure whether
the displayed register supports that world claim, not the model's confidence.
"""
from __future__ import annotations

import argparse
from collections import Counter
import random
import re
from typing import Any

from confidence_pilot.common import (
    load_config, read_jsonl, resolve, stable_hash, write_json, write_jsonl,
)
from confidence_pilot.extract_activations import load_tokenizer, tokenize_variant

VERSION = "paired-confidence-transfer-v2"
DATASET_SEED = 20261008
FACT_TYPES = ("access_code", "room_assignment", "release_year", "material")
CONDITIONS = ("supported", "omitted", "conflicting")
FORMATS = ("qa", "document")
FORBIDDEN_V1_WORDS = (
    "confident", "uncertain", "sure", "doubt", "confidence", "hesitation",
    "settle", "lean", "tentative", "commit", "stand by", "conviction",
    "guess", "established", "provisional", "stake", "cautiously", "definite",
)
FORBIDDEN_CONTEXT_WORDS = ("confirmed", "unknown", "missing", "uncertain")

# These omission labels denote different fields even when values share a type.
# Their fixed ordering is searched for token length only, never model outcomes.
FACT_SPECS = {
    "access_code": {
        "entity_prefix": "Neris-K", "target_label": "Access code",
        "nuisance_label": "Parcel code",
        "omission_labels": ("Ticket code", "Locker code", "Batch code", "Shelf code", "Order code"),
        "claim_subject": "access code", "question": "What is the access code for {entity}?",
        "document_request": "Summarize the access code for {entity} as a factual sentence.",
    },
    "room_assignment": {
        "entity_prefix": "Velen-R", "target_label": "Assigned room",
        "nuisance_label": "Meeting room",
        "omission_labels": ("Storage room", "Display room", "Delivery room", "Visitor room", "Training room"),
        "claim_subject": "assigned room", "question": "What is the assigned room for {entity}?",
        "document_request": "Summarize the assigned room for {entity} as a factual sentence.",
    },
    "release_year": {
        "entity_prefix": "Torin-Y", "target_label": "Release year",
        "nuisance_label": "Archive year",
        "omission_labels": ("Review year", "Audit year", "Catalog year", "Design year", "Planning year"),
        "claim_subject": "release year", "question": "What is the release year for {entity}?",
        "document_request": "Summarize the release year for {entity} as a factual sentence.",
    },
    "material": {
        "entity_prefix": "Savel-M", "target_label": "Main material",
        "nuisance_label": "Crate material",
        "omission_labels": ("Label material", "Box material", "Tray material", "Case material", "Bag material"),
        "claim_subject": "main material", "question": "What is the main material for {entity}?",
        "document_request": "Summarize the main material for {entity} as a factual sentence.",
    },
}

# Each pair preserves a single unquoted proposition.  IDs 01--06 mostly keep
# assertions shorter; IDs 07--12 deliberately make assertions longer, so length
# cannot act as a uniformly aligned cue.  Pair 06 also matches word/token length.
WORDING_PAIRS = (
    ("N01", "{claim}", "I think that {lower_claim}"),
    ("N02", "{claim}", "It seems that {lower_claim}"),
    ("N03", "{claim}", "Perhaps {lower_claim}"),
    ("N04", "{claim}", "{claim} I could be mistaken."),
    ("N05", "My answer is that {lower_claim}", "It seems to me that {lower_claim}"),
    ("N06", "{claim} That is my response.", "{claim} I could be mistaken."),
    ("N07", "{claim} That is the answer I give for this item.", "I think that {lower_claim}"),
    ("N08", "{claim} This is the answer I would give for this item.", "It seems that {lower_claim}"),
    ("N09", "For this item, my answer is that {lower_claim}", "Perhaps {lower_claim}"),
    ("N10", "{claim} I give this as my answer for the item.", "My working answer is that {lower_claim}"),
    ("N11", "{claim} This is my answer to the question for this item.", "I think {lower_claim}"),
    ("N12", "For this item, I give the following answer: {lower_claim}", "It might be that {lower_claim}"),
)
TEMPLATE_REVIEW = (
    "think adds epistemic reservation to the same declarative claim",
    "seems adds epistemic reservation to the same declarative claim",
    "perhaps qualifies only the same declarative claim",
    "could be mistaken qualifies only the same preceding claim",
    "seems to me qualifies the same answer proposition",
    "same-word-count suffixes contrast an answer declaration with fallibility",
    "answer-declaration suffix adds no evidence; think qualifies the same claim",
    "answer-declaration suffix adds no evidence; seems qualifies the same claim",
    "answer framing adds no evidence; perhaps qualifies the same claim",
    "answer-declaration suffix adds no evidence; working answer qualifies the same claim",
    "answer-declaration suffix adds no evidence; think qualifies the same claim",
    "answer framing adds no evidence; might qualifies the same claim",
)


def _claim(fact_type: str, entity: str, value: str) -> str:
    return f"The {FACT_SPECS[fact_type]['claim_subject']} for {entity} is {value}."


def _context(source: dict[str, Any], condition: str, omission_label: str) -> str:
    target_label = omission_label if condition == "omitted" else source["target_label"]
    target_value, nuisance_value = source["true_value"], source["false_value"]
    if condition == "conflicting":
        target_value, nuisance_value = nuisance_value, target_value
    fields = [(target_label, target_value), (source["nuisance_label"], nuisance_value)]
    if source["target_line_order"] == "second":
        fields.reverse()
    return "Item: " + source["entity"] + "\n" + "\n".join(f"{label}: {value}" for label, value in fields)


def _prompt_token_count(context: str, question: str, tokenizer: Any, config: dict[str, Any]) -> int:
    messages = [
        {"role": "system", "content": config["model"]["system_prompt"]},
        {"role": "user", "content": f"Context: {context}\n\nQuestion: {question}"},
    ]
    prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    return len(tokenizer(prompt, add_special_tokens=False)["input_ids"])


def _values(fact_type: str, rng: random.Random) -> list[tuple[str, str]]:
    if fact_type == "access_code":
        values = [str(value) for value in rng.sample(range(100, 1000), 24)]
    elif fact_type == "release_year":
        values = [str(value) for value in rng.sample(range(1980, 2025), 24)]
    elif fact_type == "room_assignment":
        values = [name + " Hall" for name in (
            "Cedar", "Maple", "Laurel", "Birch", "Willow", "Elm", "Pine", "Oak",
            "Aspen", "Hazel", "Alder", "Spruce", "Juniper", "Holly", "Linden",
            "Rowan", "Ash", "Poplar", "Beech", "Cypress", "Fir", "Sequoia", "Yew", "Sycamore",
        )]
        rng.shuffle(values)
    else:
        values = ["wood", "steel", "glass", "copper", "stone", "rubber", "cotton",
                  "wool", "paper", "plastic", "clay", "silk", "bronze", "leather",
                  "linen", "foam", "ceramic", "aluminum", "bamboo", "iron", "felt",
                  "nylon", "cork", "brass"]
        rng.shuffle(values)
    return list(zip(values[::2], values[1::2]))


def _match_omission_label(source: dict[str, Any], tokenizer: Any, config: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    candidates = FACT_SPECS[source["fact_type"]]["omission_labels"]
    attempted = []
    for label in candidates:
        lengths = {
            view: {condition: _prompt_token_count(_context(source, condition, label),
                    source["qa_question" if view == "qa" else "document_request"], tokenizer, config)
                   for condition in CONDITIONS}
            for view in FORMATS
        }
        attempted.append({"label": label, "prompt_token_counts": lengths})
        if all(len(set(view_lengths.values())) == 1 for view_lengths in lengths.values()):
            return label, {"selection_method": "first_predeclared_semantic_label_with_exact_prompt_token_match",
                           "model_scoring_calls": 0, "attempted_labels": attempted,
                           "prompt_token_counts": lengths}
    raise ValueError(f"No tokenizer-only omission label matches all conditions/views for {source['source_id']}: {attempted}")


def _construct_sources(config: dict[str, Any], tokenizer: Any) -> list[dict[str, Any]]:
    seed = int(config.get("dataset", {}).get("seed", DATASET_SEED))
    if seed != DATASET_SEED:
        raise ValueError(f"v2 fictional catalog seed must remain {DATASET_SEED}")
    rng = random.Random(seed)
    sources = []
    for fact_type in FACT_TYPES:
        spec = FACT_SPECS[fact_type]
        for index, (true_value, false_value) in enumerate(_values(fact_type, rng)):
            entity = f"{spec['entity_prefix']}{index + 1:02d}"
            source = {
                "source_id": f"v2-{fact_type}-{index + 1:02d}", "fact_type": fact_type,
                "entity": entity, "true_value": true_value, "false_value": false_value,
                "world_claim": _claim(fact_type, entity, true_value),
                "qa_question": spec["question"].format(entity=entity),
                "document_request": spec["document_request"].format(entity=entity),
                "wording_id": WORDING_PAIRS[index][0], "target_label": spec["target_label"],
                "nuisance_label": spec["nuisance_label"],
                "target_line_order": "first" if index % 2 == 0 else "second",
                "split": "test", "dataset_version": VERSION,
                "provenance": {"method": "constructed_fictional_world", "seed": seed,
                               "real_world_entity": False, "external_dataset": None,
                               "ground_truth_scope": "constructed_world_key",
                               "target_value_constant_across_conditions": True},
            }
            label, selection = _match_omission_label(source, tokenizer, config)
            source["omission_label"] = label
            source["contexts"] = {condition: _context(source, condition, label) for condition in CONDITIONS}
            source["tokenization_audit"] = selection
            sources.append(source)
    return sources


def _row(source: dict[str, Any], *, experiment: str, view: str, condition: str,
         correctness: str, certainty: str, response: str, answer: str,
         variant_id: str, paired_variant_id: str | None,
         tokenizer: Any, config: dict[str, Any]) -> dict[str, Any]:
    row = {
        "variant_id": variant_id, "source_id": source["source_id"],
        "fact_type": source["fact_type"], "experiment": experiment,
        "format": view, "condition": condition, "correctness": correctness,
        "certainty": certainty, "wording_id": source["wording_id"],
        "paired_variant_id": paired_variant_id,
        "question": source["qa_question" if view == "qa" else "document_request"],
        "context": source["contexts"][condition], "response_text": response,
        "answer_span_text": answer, "world_claim": source["world_claim"],
        "split": "test", "dataset_version": VERSION,
        "ground_truth_scope": "constructed_world_key",
    }
    tokens = tokenize_variant(row, tokenizer, config)
    row.update({"prompt_token_count": tokens["prompt_length"],
                "token_count": len(tokens["response_ids"]),
                "char_count": len(response), "word_count": len(response.split()),
                "response_ids": tokens["response_ids"]})
    return row


def _construct_rows(sources: list[dict[str, Any]], tokenizer: Any,
                    config: dict[str, Any]) -> list[dict[str, Any]]:
    by_wording = {wording_id: (assertive, hedged) for wording_id, assertive, hedged in WORDING_PAIRS}
    rows = []
    for source in sources:
        source_id = source["source_id"]
        for view in FORMATS:
            for condition in CONDITIONS:
                rows.append(_row(source, experiment="neutral_evidence", view=view,
                    condition=condition, correctness="correct", certainty="neutral",
                    response=source["world_claim"], answer=source["true_value"],
                    variant_id=f"{source_id}--neutral--{view}--{condition}",
                    paired_variant_id=None, tokenizer=tokenizer, config=config))
        for correctness, value in (("correct", source["true_value"]), ("incorrect", source["false_value"])):
            claim = _claim(source["fact_type"], source["entity"], value)
            lower_claim = claim[0].lower() + claim[1:]
            for certainty, template in zip(("confident", "hedged"), by_wording[source["wording_id"]]):
                partner = "hedged" if certainty == "confident" else "confident"
                rows.append(_row(source, experiment="natural_style", view="qa", condition="supported",
                    correctness=correctness, certainty=certainty,
                    response=template.format(claim=claim, lower_claim=lower_claim), answer=value,
                    variant_id=f"{source_id}--natural--{correctness}--{certainty}",
                    paired_variant_id=f"{source_id}--natural--{correctness}--{partner}",
                    tokenizer=tokenizer, config=config))
    return rows


def _contains_word(text: str, words: tuple[str, ...]) -> bool:
    # Include concatenated "standby" in the historical-word exclusion.
    terms = tuple(words) + (("standby",) if words == FORBIDDEN_V1_WORDS else ())
    return any(re.search(r"\b" + re.escape(word) + r"\b", text, re.IGNORECASE) for word in terms)


def _freshness(sources: list[dict[str, Any]], config: dict[str, Any]) -> dict[str, Any]:
    old_path = config.get("data", {}).get("v1_source_items", "data/paired_confidence/source_items.jsonl")
    old_sources = read_jsonl(old_path)
    source_overlap = sorted({s["source_id"] for s in sources} & {s["source_id"] for s in old_sources})
    old_serialized = "\n".join(str(s.get(key, "")) for s in old_sources
                               for key in ("question", "context", "source_id"))
    entity_overlap = [s["entity"] for s in sources if s["entity"] in old_serialized]
    return {"v1_catalog_path": str(old_path), "v1_source_count": len(old_sources),
            "v2_source_id_overlap": source_overlap, "v2_entity_overlap": entity_overlap,
            "all_keys_new": not source_overlap and not entity_overlap,
            "construction_prevents_real_world_reference_answers": True}


def validate_transfer_dataset(sources: list[dict[str, Any]], rows: list[dict[str, Any]],
                              config: dict[str, Any], tokenizer: Any | None = None) -> dict[str, Any]:
    """Recheck the fixed design and matched prompts without any model inference."""
    if tokenizer is None:
        tokenizer = load_tokenizer(config)
    errors = []
    expected_sources = _construct_sources(config, tokenizer)
    if sources != expected_sources:
        errors.append("Source records differ from the fixed fictional-world construction.")
    expected_rows = _construct_rows(expected_sources, tokenizer, config)
    by_id = {row["variant_id"]: row for row in rows}
    if len(by_id) != len(rows):
        errors.append("Duplicate variant IDs.")
    if set(by_id) != {row["variant_id"] for row in expected_rows}:
        errors.append("Variant catalog is incomplete or contains unexpected IDs.")
    for expected in expected_rows:
        actual = by_id.get(expected["variant_id"])
        if actual is not None and any(actual.get(key) != value for key, value in expected.items()):
            errors.append(f"Written/tokenized content differs from fixed design: {expected['variant_id']}")
    if any(row["response_text"].count(row["answer_span_text"]) != 1 for row in rows):
        errors.append("An answer span is absent or occurs more than once.")
    if any('"' in row["response_text"] or "'" in row["response_text"] for row in rows):
        errors.append("A response contains quotation marks.")
    if any(_contains_word(row["response_text"], FORBIDDEN_V1_WORDS) for row in rows):
        errors.append("A response reuses excluded v1 certainty vocabulary.")
    if any(_contains_word(context, FORBIDDEN_CONTEXT_WORDS)
           for source in sources for context in source["contexts"].values()):
        errors.append("A context explicitly labels evidence certainty.")
    freshness = _freshness(sources, config)
    if not freshness["all_keys_new"]:
        errors.append("Source or entity keys overlap the v1 catalog.")

    neutral_checks = []
    neutral = [row for row in rows if row["experiment"] == "neutral_evidence"]
    for source in sources:
        for view in FORMATS:
            selected = [row for row in neutral if row["source_id"] == source["source_id"] and row["format"] == view]
            texts = {row["response_text"] for row in selected}
            ids = {tuple(row["response_ids"]) for row in selected}
            lengths = {row["condition"]: row["prompt_token_count"] for row in selected}
            check = {
                "source_id": source["source_id"], "format": view,
                "conditions_complete": set(lengths) == set(CONDITIONS) and len(selected) == 3,
                "response_text_identical": len(texts) == 1,
                "response_ids_identical": len(ids) == 1,
                "response_ids_sha256": stable_hash(list(next(iter(ids)))) if len(ids) == 1 else None,
                "prompt_token_counts": lengths, "prompt_token_counts_equal": len(set(lengths.values())) == 1,
            }
            neutral_checks.append(check)
            if not all(check[key] for key in ("conditions_complete", "response_text_identical",
                       "response_ids_identical", "prompt_token_counts_equal")):
                errors.append(f"Neutral evidence matching failed: {source['source_id']}/{view}")

    natural = [row for row in rows if row["experiment"] == "natural_style"]
    lengths = []
    for row in natural:
        if row["certainty"] != "confident":
            continue
        partner = by_id.get(row["paired_variant_id"])
        if partner is None:
            errors.append(f"Missing natural-style partner for {row['variant_id']}")
            continue
        deltas = {name: row[name] - partner[name] for name in ("token_count", "word_count", "char_count")}
        lengths.append({"source_id": row["source_id"], "correctness": row["correctness"],
                        "wording_id": row["wording_id"], "confident_variant_id": row["variant_id"],
                        "hedged_variant_id": partner["variant_id"],
                        "confident_minus_hedged": deltas,
                        "token_length_matched": deltas["token_count"] == 0,
                        "word_length_matched": deltas["word_count"] == 0,
                        "char_length_matched": deltas["char_count"] == 0,
                        "assertion_longer_all_lengths": all(value > 0 for value in deltas.values()),
                        "assertion_shorter_all_lengths": all(value < 0 for value in deltas.values())})
        if any(row[key] != partner[key] for key in ("source_id", "question", "context", "answer_span_text",
                                                   "correctness", "condition", "format", "wording_id")):
            errors.append(f"Natural-style pair changes content or prompt: {row['variant_id']}")
    if not any(item["assertion_longer_all_lengths"] for item in lengths):
        errors.append("No natural pairs reverse the usual assertion-shorter length relation.")
    if not any(item["assertion_shorter_all_lengths"] for item in lengths):
        errors.append("No natural pairs have the assertion-shorter relation.")
    if not any(item["token_length_matched"] and item["word_length_matched"] for item in lengths):
        errors.append("No natural pairs match both response token and word length.")
    if not any(item["token_length_matched"] and item["word_length_matched"] and item["char_length_matched"]
               for item in lengths):
        errors.append("No natural pairs match response token, word, and character length.")

    template_audit = [{"wording_id": pair[0], "confident_template": pair[1],
                      "hedged_template": pair[2], "scoreless_review": reason,
                      "single_same_proposition": True, "additional_evidence": False,
                      "additional_answer": False, "quote_free": True,
                      "excluded_v1_words_absent": not _contains_word(" ".join(pair[1:]), FORBIDDEN_V1_WORDS),
                      "assigned_source_count": sum(s["wording_id"] == pair[0] for s in sources),
                      "assigned_fact_types": sorted(s["fact_type"] for s in sources if s["wording_id"] == pair[0])}
                     for pair, reason in zip(WORDING_PAIRS, TEMPLATE_REVIEW)]
    return {
        "version": VERSION, "passed": not errors, "errors": errors,
        "seed": DATASET_SEED, "source_count": len(sources), "variant_count": len(rows),
        "fact_type_source_counts": dict(Counter(s["fact_type"] for s in sources)),
        "experiment_variant_counts": dict(Counter(row["experiment"] for row in rows)),
        "format_variant_counts": dict(Counter(row["format"] for row in rows)),
        "condition_variant_counts": dict(Counter(row["condition"] for row in rows)),
        "natural_pair_count": len(lengths), "neutral_comparison_count_per_format": {
            view: sum(check["format"] == view for check in neutral_checks) for view in FORMATS},
        "all_sources_test_only": all(s["split"] == "test" for s in sources),
        "all_rows_test_only": all(row["split"] == "test" for row in rows),
        "truth_definition": "World correctness is fixed by the fictional key for every evidence condition.",
        "evidence_definition": "supported/omitted/conflicting label evidence sufficiency, not true or internal confidence.",
        "omitted_true_value_present": all(s["true_value"] in s["contexts"]["omitted"] for s in sources),
        "candidate_value_presence_all_conditions": all(
            context.count(s["true_value"]) == context.count(s["false_value"]) == 1
            for s in sources for context in s["contexts"].values()),
        "target_line_order_counts": dict(Counter(s["target_line_order"] for s in sources)),
        "value_order_balanced_per_condition": {
            condition: dict(Counter("true_first" if s["contexts"][condition].index(s["true_value"]) <
                s["contexts"][condition].index(s["false_value"]) else "false_first" for s in sources))
            for condition in CONDITIONS},
        "model_generation_calls": 0, "model_scoring_calls": 0, "downloads": 0,
        "label_selection_uses_tokenizer_only": True, "source_freshness": freshness,
        "template_pairs": template_audit, "neutral_evidence_checks": neutral_checks,
        "natural_pair_length_checks": lengths,
        "length_subsets": {name: [item["confident_variant_id"] for item in lengths if item[name]]
            for name in ("token_length_matched", "word_length_matched", "char_length_matched",
                         "assertion_longer_all_lengths", "assertion_shorter_all_lengths")},
        "catalog_sha256": stable_hash({"sources": sources, "rows": rows}),
    }


def build_transfer_dataset(config: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    tokenizer = load_tokenizer(config)
    sources = _construct_sources(config, tokenizer)
    rows = _construct_rows(sources, tokenizer, config)
    audit = validate_transfer_dataset(sources, rows, config, tokenizer)
    if not audit["passed"]:
        raise ValueError("v2 scoreless data gate failed: " + "; ".join(audit["errors"]))
    return sources, rows, audit


def _audit_table(sources: list[dict[str, Any]], audit: dict[str, Any]) -> str:
    lines = [
        "# Transfer v2 scoreless data audit", "",
        "All 48 records are constructed fictional worlds; their true values are fixed by the key below.",
        "Supported and omitted contexts share the same world truth. Evidence labels describe the displayed register, not model confidence.",
        "All label choices use only the pinned local tokenizer. This audit contains no activation or outcome scores.", "",
        "## Natural wording review", "",
        "`{claim}` is the single world-key claim (or its one-value incorrect counterpart); `{lower_claim}` changes only sentence-initial capitalization.",
        "Each pair is assigned to four sources, one per fact type. All rows are quote-free and keep the answer span exactly once.", "",
        "| ID | Assertion | Hedge | Scoreless semantic review | Sources |",
        "| --- | --- | --- | --- | --- |",
    ]
    for item in audit["template_pairs"]:
        lines.append(f"| {item['wording_id']} | {item['confident_template']} | {item['hedged_template']} | {item['scoreless_review']}; no new evidence or second answer | {item['assigned_source_count']} |")
    lines.extend([
        "", "## World key and context review", "",
        "The first value is the world truth; the second is the foil. Supported assigns truth to the target and foil to the nuisance field; omitted assigns truth to the unrelated replacement field; conflicting swaps the target/nuisance values. Both values and the entity occur in every condition.",
        "QA and document prompts each have exactly equal token lengths across the three contexts. Correct/wrong natural-style responses use the same supported context and QA question.", "",
        "| Source | Entity | Target field | True | Foil | Nuisance field | Omitted replacement | Target line | Wording | QA tokens S/O/C | Doc tokens S/O/C | Review |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ])
    for source in sources:
        counts = source["tokenization_audit"]["prompt_token_counts"]
        qa = "/".join(str(counts["qa"][condition]) for condition in CONDITIONS)
        document = "/".join(str(counts["document"][condition]) for condition in CONDITIONS)
        lines.append(f"| {source['source_id']} | {source['entity']} | {source['target_label']} | {source['true_value']} | {source['false_value']} | {source['nuisance_label']} | {source['omission_label']} | {source['target_line_order']} | {source['wording_id']} | {qa} | {document} | key/context/answer mapping checked |")
    lines.extend([
        "", "## Gates and length controls", "",
        f"- Sources: {audit['source_count']}; all test-only; four fact types with 12 sources each.",
        f"- Rows: {audit['variant_count']}; 192 natural-style rows (96 pairs), 288 neutral-evidence rows (48 comparisons per format).",
        "- Neutral responses and response-token IDs are identical within every source/format across supported, omitted, and conflicting.",
        "- True/foil order is balanced 24/24 in each condition; target line order is balanced 24/24.",
        "- The word/character/token length deltas and exact matched/reversed subsets are recorded in `data_audit.json` before scoring.",
    ])
    for name, ids in audit["length_subsets"].items():
        lines.append(f"- {name}: {len(ids)} pairs.")
    lines.extend(["- The v1 source IDs and entity keys have no overlap with v2.",
                  "- No generation, model scoring, downloads, or external reference-answer lookup is used.", ""])
    return "\n".join(lines)


def write_transfer_dataset(config: dict[str, Any]) -> dict[str, Any]:
    """Write the auditable data products; this must precede feature extraction."""
    data = config.get("data", {})
    defaults = {"source_items": "source_items.jsonl", "variants": "variants.jsonl",
                "audit": "data_audit.json", "wording_pairs": "wording_pairs.json",
                "audit_table": "manual_audit.md"}
    target_root = resolve("data/confidence_transfer_v2")
    paths = {key: resolve(data.get(key, target_root / filename)) for key, filename in defaults.items()}
    if any(not path.is_relative_to(target_root) for path in paths.values()):
        raise ValueError("v2 data artifacts must stay under data/confidence_transfer_v2; v1 files are protected")
    sources, rows, audit = build_transfer_dataset(config)
    write_jsonl(paths["source_items"], sources)
    write_jsonl(paths["variants"], rows)
    write_json(paths["audit"], audit)
    write_json(paths["wording_pairs"], audit["template_pairs"])
    table = paths["audit_table"]
    table.parent.mkdir(parents=True, exist_ok=True)
    table.write_text(_audit_table(sources, audit), encoding="utf-8")
    return audit


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    audit = write_transfer_dataset(load_config(args.config))
    print(f"v2 scoreless gate passed: {audit['source_count']} sources, {audit['variant_count']} rows")


if __name__ == "__main__":
    main()
