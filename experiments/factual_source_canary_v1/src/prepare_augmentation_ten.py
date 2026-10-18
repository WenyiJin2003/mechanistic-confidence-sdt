"""Prepare one ten-pair augmentation preview, or render saved writer output.

This makes no model calls and does not open a browser. Old artifacts stay intact.
"""
import argparse
import hashlib
import html
import json
import random
import re
from collections import Counter
from pathlib import Path

from prepare_epistemic_preview import render_preview
from build_factual_rewrite_review import _write_json, sha256_value

BASE = Path(__file__).resolve().parents[1]
FROZEN = BASE / "private_data" / "rewrite_canary_v1"
OUTPUT = FROZEN / "augmentation_ten_v1"
CONFIG = BASE / "configs" / "augmentation_ten_v1.json"
PROMPT = BASE / "prompts" / "augmentation_ten_v1.txt"
MARKERS = {
    "may": r"\bmay\b", "might": r"\bmight\b", "could": r"\bcould\b",
    "perhaps": r"\bperhaps\b", "possibly": r"\bpossibly\b",
    "possible_that": r"\bpossible that\b", "one_possibility": r"\bone possibility\b",
    "seem_appear": r"\b(?:seem|seems|seemed|appear|appears|appeared)\b",
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def numeric_details(text):
    return Counter(re.findall(r"\b\d+(?:[.,]\d+)*\b", text))


def select_sources(rows, quotas):
    counts, selected = Counter(), []
    for row in rows:
        dataset = row["dataset"]
        if counts[dataset] < quotas.get(dataset, 0):
            selected.append(row)
            counts[dataset] += 1
    if dict(counts) != quotas:
        raise ValueError("source quotas not met")
    if len({r["source_id"] for r in selected}) != sum(quotas.values()):
        raise ValueError("duplicate sources")
    if len({r["group_id"] for r in selected}) != len(selected):
        raise ValueError("source groups must be distinct in this preview")
    return selected


def check_pairs(sources, pairs):
    by_id = {p["preview_id"]: p for p in pairs}
    if len(by_id) != len(pairs) or set(by_id) != {s["preview_id"] for s in sources}:
        raise ValueError("pairs must cover each input source exactly once")
    for pair in pairs:
        for role in ("confident", "hesitant"):
            value = pair.get(role + "_response")
            if not isinstance(value, str) or not value.strip():
                raise ValueError("missing response")
        if not isinstance(pair.get("primary_uncertainty_construction"), str):
            raise ValueError("writer construction description missing")
    return by_id


def prepare():
    if OUTPUT.exists():
        raise FileExistsError("packet exists; do not overwrite or regenerate")
    config = json.loads(CONFIG.read_text())
    source_path = FROZEN / "frozen_sources_v4.jsonl"
    freeze_path = FROZEN / "FREEZE_MANIFEST_PRIVATE_V4.json"
    freeze = json.loads(freeze_path.read_text())
    if digest(source_path) != freeze["frozen_sources_sha256"]:
        raise ValueError("frozen source hash mismatch")
    rows = select_sources([json.loads(x) for x in source_path.read_text().splitlines()],
                          config["source_count_by_dataset"])
    sources, bindings = [], []
    for i, row in enumerate(rows, 1):
        identifier = f"DA{i:03d}"
        sources.append({"preview_id": identifier, "prompt": row["prompt"],
                        "original_response": row["original_response"]})
        bindings.append({"preview_id": identifier, **{k: row[k] for k in
                        ("source_id", "source_hash", "dataset", "group_id", "original_response_sha256")}})
    OUTPUT.mkdir(parents=True)
    _write_json(OUTPUT / "SOURCE_ONLY.json", {"sources": sources})
    _write_json(OUTPUT / "SOURCE_BINDINGS_PRIVATE.json", {"rows": bindings})
    writer_prompt = PROMPT.read_text() + "\nINPUT_JSON\n" + json.dumps({"sources": sources}, ensure_ascii=False, separators=(",", ":")) + "\n"
    (OUTPUT / "WRITER_PROMPT.txt").write_text(writer_prompt, encoding="utf-8")
    paths = {"sources": OUTPUT / "SOURCE_ONLY.json", "bindings": OUTPUT / "SOURCE_BINDINGS_PRIVATE.json",
             "writer_prompt": OUTPUT / "WRITER_PROMPT.txt", "config": CONFIG, "prompt_template": PROMPT,
             "frozen_sources": source_path, "freeze_manifest": freeze_path}
    _write_json(OUTPUT / "INPUT_MANIFEST_PRIVATE.json", {
        "writer_model": config["writer_model"], "reasoning_effort": config["reasoning_effort"],
        "source_count": len(sources), "input_sha256": {k: digest(v) for k, v in paths.items()}})
    print(json.dumps({"prepared_sources": len(sources), "source_words": sum(len(s["original_response"].split()) for s in sources),
                      "writer_model": config["writer_model"], "model_calls_made": 0}))


def prepare_repair():
    if (OUTPUT / "REPAIR_INPUT_MANIFEST.json").exists():
        raise FileExistsError("bounded repair already prepared; no retry loop")
    identifiers = {"DA001", "DA002", "DA006", "DA007", "DA008", "DA009"}
    sources = json.loads((OUTPUT / "SOURCE_ONLY.json").read_text())["sources"]
    subset = [s for s in sources if s["preview_id"] in identifiers]
    if len(subset) != 6:
        raise ValueError("expected six explicitly selected repair sources")
    addendum = BASE / "prompts" / "augmentation_ten_repair_addendum.txt"
    text = PROMPT.read_text() + "\n" + addendum.read_text() + "\nINPUT_JSON\n" + json.dumps({"sources": subset}, ensure_ascii=False, separators=(",", ":")) + "\n"
    _write_json(OUTPUT / "REPAIR_SOURCE_ONLY.json", {"sources": subset})
    (OUTPUT / "REPAIR_PROMPT.txt").write_text(text, encoding="utf-8")
    _write_json(OUTPUT / "REPAIR_INPUT_MANIFEST.json", {
        "repair_ids": sorted(identifiers), "writer_model": "gpt-6-luna", "reasoning_effort": "medium",
        "maximum_repair_batches": 1, "source_only": True,
        "raw_initial_draft_sha256": digest(OUTPUT / "DRAFT_PAIRS.json"),
        "source_subset_sha256": digest(OUTPUT / "REPAIR_SOURCE_ONLY.json"),
        "writer_prompt_sha256": digest(OUTPUT / "REPAIR_PROMPT.txt"),
        "addendum_sha256": digest(addendum),
        "parent_diagnosis_not_sent_to_writer": ["inconsistent whole-response commitment", "conditional would is not epistemic doubt",
                                                  "record condition scope drift", "uncertainty on reporting rather than main finding"]})
    print(json.dumps({"repair_source_count": 6, "prior_candidates_exposed_to_writer": False, "model_calls_made": 0}))


def render():
    manifest = json.loads((OUTPUT / "INPUT_MANIFEST_PRIVATE.json").read_text())
    for key, path in {"sources": OUTPUT / "SOURCE_ONLY.json", "bindings": OUTPUT / "SOURCE_BINDINGS_PRIVATE.json",
                      "writer_prompt": OUTPUT / "WRITER_PROMPT.txt", "config": CONFIG, "prompt_template": PROMPT}.items():
        if digest(path) != manifest["input_sha256"][key]:
            raise ValueError(f"input changed: {key}")
    sources = json.loads((OUTPUT / "SOURCE_ONLY.json").read_text())["sources"]
    raw = OUTPUT / "DRAFT_PAIRS.json"
    pairs = json.loads(raw.read_text())["pairs"]
    by_id = check_pairs(sources, pairs)
    repair_provenance = None
    if (OUTPUT / "REPAIR_INPUT_MANIFEST.json").exists():
        repair_provenance = json.loads((OUTPUT / "REPAIR_INPUT_MANIFEST.json").read_text())
        for key, path in {"raw_initial_draft_sha256": raw, "source_subset_sha256": OUTPUT / "REPAIR_SOURCE_ONLY.json",
                          "writer_prompt_sha256": OUTPUT / "REPAIR_PROMPT.txt",
                          "addendum_sha256": BASE / "prompts" / "augmentation_ten_repair_addendum.txt"}.items():
            if digest(path) != repair_provenance[key]:
                raise ValueError(f"repair input changed: {key}")
        subset = json.loads((OUTPUT / "REPAIR_SOURCE_ONLY.json").read_text())["sources"]
        if subset != [s for s in sources if s["preview_id"] in repair_provenance["repair_ids"]]:
            raise ValueError("repair sources are not the exact original subset")
        repaired = json.loads((OUTPUT / "REPAIRED_SIX.json").read_text())["pairs"]
        by_id.update(check_pairs(subset, repaired))
        pairs = [by_id[s["preview_id"]] for s in sources]
    _write_json(OUTPUT / "REVIEW_PAIRS.json", {"pairs": pairs})
    config = json.loads(CONFIG.read_text())
    roles = ["confident"] * 5 + ["hesitant"] * 5
    random.Random(config["review_seed"]).shuffle(roles)
    cards, key, diagnostics = [], [], []
    marker_pairs = Counter()
    families = Counter()
    for source, a_role in zip(sources, roles):
        identifier = source["preview_id"]
        pair = by_id[identifier]
        b_role = "hesitant" if a_role == "confident" else "confident"
        cards.append({"review_id": identifier, "question": source["prompt"], "original_response": source["original_response"],
                      "version_a": pair[a_role + "_response"], "version_b": pair[b_role + "_response"]})
        key.append({"preview_id": identifier, "version_a_role": a_role})
        family = pair["primary_uncertainty_construction"].strip().lower()
        families[family] += 1
        row = {"preview_id": identifier, "word_counts": {}, "numeric_details_match": {}, "added_hesitant_markers": {}}
        for role in ("confident", "hesitant"):
            text = pair[role + "_response"]
            row["word_counts"][role] = len(text.split())
            row["numeric_details_match"][role] = numeric_details(text) == numeric_details(source["original_response"])
        for name, pattern in MARKERS.items():
            count = max(0, len(re.findall(pattern, pair["hesitant_response"], re.I)) - len(re.findall(pattern, source["original_response"], re.I)))
            row["added_hesitant_markers"][name] = count
            marker_pairs[name] += int(count > 0)
        diagnostics.append(row)
    warning_path = OUTPUT / "PARENT_REVIEW_WARNINGS.json"
    warnings = json.loads(warning_path.read_text())["notes"] if warning_path.exists() else {}
    packet_hash = sha256_value({"cards": cards, "parent_warnings": warnings})
    warning_intro = "Parent checks found unresolved problems, shown next to affected pairs; other pairs are not certified either. " if warnings else "Researcher review is pending. "
    may_intro = f'New may wording occurs in {marker_pairs["may"]} hesitant texts; the requested maximum is three. '
    page = render_preview(cards, packet_hash, title="Ten varied confidence rewrite examples",
        intro="Ten development drafts: four factual QA responses, three bill summaries and three paper abstracts. The prompt requests varied wording and syntax in both arms. These are NOT accepted training data. " + warning_intro + may_intro + "Version labels are randomized. No new probe was trained.",
        export_name="augmentation_ten_feedback.json", feedback_schema="augmentation-ten-feedback-v1")
    for identifier, note in warnings.items():
        if identifier not in by_id:
            raise ValueError("warning refers to an unknown pair")
        heading = f"<h2>{identifier}</h2>"
        page = page.replace(heading, heading + '<p style="background:#fff4d6;padding:12px"><strong>Needs attention:</strong> ' + html.escape(note) + "</p>", 1)
    (OUTPUT / "reviewer_only").mkdir(exist_ok=True)
    (OUTPUT / "reviewer_only" / "BLIND_REVIEW.html").write_text(page, encoding="utf-8")
    (OUTPUT / "private_key").mkdir(exist_ok=True)
    _write_json(OUTPUT / "private_key" / "KEY.json", {"packet_sha256": packet_hash, "rows": key})
    _write_json(OUTPUT / "CONSTRUCTION_DIAGNOSTICS_PRIVATE.json", {"rows": diagnostics, "writer_reported_constructions": dict(families)})
    status = {"schema": "augmentation-ten-status-v1", "pair_count": len(pairs),
        "status": "drafts_pending_researcher_review", "artifact_role": "development_preview",
        "writer_model": config["writer_model"], "reasoning_effort": config["reasoning_effort"],
        "writer_contexts": 2 if repair_provenance else 1, "initial_generation_batches": 1,
        "bounded_source_only_repair_batches": int(repair_provenance is not None),
        "revised_pair_count": len(repair_provenance["repair_ids"]) if repair_provenance else 0,
        "automatic_retries": 0, "editorial_changes": 0,
        "dataset_counts": config["source_count_by_dataset"], "input_sha256": manifest["input_sha256"],
        "raw_draft_sha256": digest(raw), "packet_sha256": packet_hash,
        "review_pairs_sha256": digest(OUTPUT / "REVIEW_PAIRS.json"),
        "hesitant_texts_with_added_marker": dict(marker_pairs),
        "marker_count_note": "Regex count increases versus the source, not semantic interpretation; may include permission or capability uses.",
        "writer_reported_unique_construction_descriptions": len(families),
        "writer_reported_construction_note": "Self-reported labels, not independently verified syntactic families.",
        "requested_may_presence_cap": 3, "requested_may_presence_cap_met": marker_pairs["may"] <= 3,
        "parent_flagged_pair_count": len(warnings), "parent_check_blinded": False,
        "parent_check_note": "Warnings shown on review page; known content issues are not accepted data.",
        "accepted_training_pairs": 0,
        "numeric_detail_mismatch_pairs": sum(not all(d["numeric_details_match"].values()) for d in diagnostics),
        "word_counts": [d["word_counts"] for d in diagnostics], "word_count_unit": "whitespace_words_not_model_tokens",
        "length_balanced": False, "human_review_certified": False, "independent_blind_review_completed": False,
        "old_experiments_regenerated": False, "old_v4_budget_modified": False,
        "activation_extraction_started": False, "probe_fitting_started": False, "sdt_training_started": False,
        "limitations": ["Previously inspected development sources; not a held-out evaluation.",
                        "Lexical and syntactic variety does not establish freedom from lexical shortcuts.",
                        "Factual core, certainty contrast and naturalness require researcher review."]}
    if repair_provenance:
        status["repair_manifest_sha256"] = digest(OUTPUT / "REPAIR_INPUT_MANIFEST.json")
        status["raw_repaired_six_sha256"] = digest(OUTPUT / "REPAIRED_SIX.json")
        status["original_batch_preserved"] = True
    if warnings:
        status["parent_warnings_sha256"] = digest(warning_path)
    _write_json(BASE / "results" / "augmentation_ten_v1_status.json", status)
    print(json.dumps({k: status[k] for k in ("pair_count", "status", "hesitant_texts_with_added_marker", "numeric_detail_mismatch_pairs")}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument("--render", action="store_true")
    actions.add_argument("--prepare-repair", action="store_true")
    args = parser.parse_args()
    if args.render:
        render()
    elif args.prepare_repair:
        prepare_repair()
    else:
        prepare()
