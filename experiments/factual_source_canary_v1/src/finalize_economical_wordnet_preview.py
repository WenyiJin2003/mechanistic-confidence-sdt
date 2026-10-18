"""Validate one economical writer batch and render a private development page.

Checks are mechanical diagnostics, not semantic or human certification.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
from collections import Counter
from pathlib import Path

import build_factual_rewrite_review as review
from prepare_epistemic_preview import render_preview


BASE = Path(__file__).resolve().parents[1]
PRIVATE = BASE / "private_data" / "rewrite_canary_v1" / "wordnet_luna_preview_v1"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def wordnet_selection_valid(selection: dict, hints: list[dict], arms: list[str]) -> bool:
    for hint in hints:
        if selection.get("source_word") != hint["source_word"]:
            continue
        for sense in hint["senses"]:
            if (selection.get("synset") == sense["synset"]
                    and selection.get("replacement") in sense["candidates"]):
                pattern = r"(?<!\w)" + re.escape(selection["replacement"]) + r"(?!\w)"
                return all(re.search(pattern, arm, re.I) for arm in arms)
    return False


def main() -> None:
    global PRIVATE
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refinement", action="store_true")
    args = parser.parse_args()
    if args.refinement:
        PRIVATE = PRIVATE.with_name("wordnet_luna_preview_v2")
    manifest_path = PRIVATE / "INPUT_MANIFEST_PRIVATE.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    quality_path = PRIVATE / "QUALITATIVE_CHECK.json"
    quality = json.loads(quality_path.read_text(encoding="utf-8")) if quality_path.exists() else None
    for name, filename in (("source_only", "SOURCE_ONLY.json"), ("writer_prompt", "WRITER_PROMPT.txt")):
        if digest(PRIVATE / filename) != manifest[name + "_sha256"]:
            raise ValueError("writer input differs from its saved manifest")
    source_rows = json.loads((PRIVATE / "SOURCE_ONLY.json").read_text(encoding="utf-8"))["sources"]
    draft_path = PRIVATE / "DRAFT_PAIRS.json"
    drafts = json.loads(draft_path.read_text(encoding="utf-8"))["pairs"]
    draft_by_id = {r["preview_id"]: r for r in drafts}
    if len(drafts) != 3 or len(draft_by_id) != 3 or set(draft_by_id) != {r["preview_id"] for r in source_rows}:
        raise ValueError("writer must return exactly the same three source IDs")
    roles = ["confident", "hesitant", "confident"]
    random.Random(20261018).shuffle(roles)
    cards, key, rows = [], [], []
    actual_length_directions = Counter()
    used_count = 0
    for source, a_role in zip(source_rows, roles):
        identifier = source["preview_id"]
        pair = draft_by_id[identifier]
        arms = [pair.get(role + "_response") for role in ("confident", "hesitant")]
        if any(not isinstance(arm, str) or not arm.strip() for arm in arms):
            raise ValueError("missing complete response")
        flags = []
        numbers = Counter(re.findall(r"\b\d+(?:[.,]\d+)*\b", source["original_response"]))
        for role, arm in zip(("confident", "hesitant"), arms):
            if Counter(re.findall(r"\b\d+(?:[.,]\d+)*\b", arm)) != numbers:
                flags.append(role + "_numeric_details_need_review")
            source_cues = Counter(re.findall(r"\b(?:seem|seems|appear|appears)\b", source["original_response"].lower()))
            arm_cues = Counter(re.findall(r"\b(?:seem|seems|appear|appears)\b", arm.lower()))
            if any(arm_cues[word] > source_cues[word] for word in arm_cues):
                flags.append(role + "_new_seem_appear_cue")
        selections = pair.get("wordnet_used", [])
        if not isinstance(selections, list) or any(
            not isinstance(s, dict) or not wordnet_selection_valid(s, source["optional_wordnet_hints"], arms)
            for s in selections
        ):
            raise ValueError("claimed WordNet choice is not supplied or shared by both arms")
        used_count += len(selections)
        counts = {role: len(arm.split()) for role, arm in zip(("confident", "hesitant"), arms)}
        direction = ("confident_longer" if counts["confident"] > counts["hesitant"]
                     else "hesitant_longer" if counts["hesitant"] > counts["confident"] else "equal")
        actual_length_directions[direction] += 1
        if direction != source["length_direction"]:
            flags.append("assigned_length_direction_not_met")
        b_role = "hesitant" if a_role == "confident" else "confident"
        cards.append({"review_id": identifier, "question": source["prompt"],
                      "original_response": source["original_response"],
                      "version_a": pair[a_role + "_response"], "version_b": pair[b_role + "_response"]})
        key.append({"preview_id": identifier, "version_a_role": a_role})
        rows.append({"preview_id": identifier, "word_counts": counts,
                     "assigned_length_direction": source["length_direction"],
                     "actual_length_direction": direction, "wordnet_choices": len(selections),
                     "mechanical_flags": flags, "writer_issues": pair.get("issues", [])})
    packet_hash = review.sha256_value(cards)
    reviewer = PRIVATE / "reviewer_only" / "BLIND_REVIEW.html"
    reviewer.parent.mkdir(parents=True, exist_ok=True)
    reviewer.write_text(render_preview(cards, packet_hash,
        title="Three-pair Luna and WordNet development preview",
        intro="Three previously frozen factual sources: ASQA, BillSum and QASPER. The writer is GPT-6 Luna at low reasoning effort; WordNet supplied optional neutral vocabulary hints shared by both arms. These are drafts, not a held-out experiment.",
        export_name="wordnet_luna_three_feedback.json",
        feedback_schema="wordnet-luna-human-feedback-v1"), encoding="utf-8")
    (PRIVATE / "private_key").mkdir(exist_ok=True)
    review._write_json(PRIVATE / "private_key" / "KEY.json", {"packet_sha256": packet_hash, "rows": key})
    review._write_json(PRIVATE / "MECHANICAL_DIAGNOSTICS.json", {"rows": rows})
    summary = {
        "schema": "economical-wordnet-preview-status-v1", "status": "drafts_pending_researcher_review",
        "source_count": 3, "dataset_counts": {"asqa": 1, "billsum": 1, "qasper": 1},
        "writer_model": manifest["writer_model"], "reasoning_effort": manifest["reasoning_effort"],
        "execution": "one isolated source-only Codex writer context", "generation_batches": 1,
        "paid_api_calls": 0, "orchestrator_generation_retries": 0,
        "prompt_revision": manifest.get("prompt_revision", "v1_initial"),
        "wordnet_context_screen": manifest.get("wordnet_context_screen", "unscreened candidate senses; optional only"),
        "writer_self_correction": "No post-handoff editing reported for this context." if args.refinement else "Writer initially reported new seem/appear cues, then edited those phrases in the same context before final handoff; this was not a clean first-pass result.",
        "exact_model_snapshot": "not exposed by the session", "sampling_seed": "not exposed",
        "wordnet_version": manifest["wordnet_version"], "nltk_version": manifest["nltk_version"],
        "wordnet_role": manifest["wordnet_role"], "wordnet_automatic_substitution": False,
        "wordnet_reported_choices_shared_by_both_arms": used_count,
        "length_measure": "whitespace_words_not_model_tokens",
        "actual_length_direction_counts": dict(actual_length_directions),
        "mechanical_flag_counts": dict(Counter(flag for row in rows for flag in row["mechanical_flags"])),
        "writer_reported_issue_count": sum(len(row["writer_issues"]) for row in rows),
        "numeric_checks_are_not_semantic_certification": True,
        "wordnet_use_is_not_a_controlled_augmentation_ablation": True,
        "human_review_certified": False, "probe_fitting_started": False,
        "activation_extraction_started": False, "sdt_training_started": False,
        "packet_sha256": packet_hash,
        "input_sha256": {"manifest": digest(manifest_path), "draft": digest(draft_path),
                         "writer_prompt": digest(PRIVATE / "WRITER_PROMPT.txt"),
                         "reviewer_html": digest(reviewer)},
    }
    if quality is not None:
        if {row["preview_id"] for row in quality["findings"]} != set(draft_by_id):
            raise ValueError("qualitative findings must cover the same three drafts")
        summary["status"] = "needs_revision_under_unblinded_model_diagnostic"
        summary["qualitative_review_type"] = quality["review_type"]
        summary["qualitative_finding_counts"] = dict(Counter(
            code for row in quality["findings"] for code in row["codes"]
        ))
        summary["input_sha256"]["qualitative_check"] = digest(quality_path)
    status_name = "wordnet_luna_preview_v2_status.json" if args.refinement else "wordnet_luna_preview_v1_status.json"
    review._write_json(BASE / "results" / status_name, summary)
    print(json.dumps({"source_count": 3, "writer_model": summary["writer_model"],
                      "wordnet_choices": used_count, "length_directions": dict(actual_length_directions),
                      "flags": summary["mechanical_flag_counts"], "word_counts": [r["word_counts"] for r in rows]}))


if __name__ == "__main__":
    main()
