"""Summarize a blinded development review and text-construction diagnostics.

No hidden states are extracted and no probe or classifier is fitted.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

import build_factual_rewrite_review as review


BASE = Path(__file__).resolve().parents[1]
PRIVATE = BASE / "private_data" / "rewrite_canary_v1" / "epistemic_preview_v1"


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def summarize(rows: list[dict], key_rows: list[dict], pairs: list[dict]) -> dict:
    allowed = {
        "factual_core": {"preserved", "changed", "uncertain"},
        "more_confident": {"a", "b", "tie", "uncertain"},
        "contrast": {"clear", "weak", "uncertain"},
        "naturalness_a": {"natural", "minor_issues", "major_issues"},
        "naturalness_b": {"natural", "minor_issues", "major_issues"},
    }
    indexed = {row["review_id"]: row for row in rows}
    key = {row["preview_id"]: row for row in key_rows}
    drafts = {row["preview_id"]: row for row in pairs}
    if (len(rows) != 6 or len(key_rows) != 6 or len(pairs) != 6
            or len(indexed) != 6 or set(indexed) != set(key) or set(indexed) != set(drafts)):
        raise ValueError("review, key and drafts must cover the same six IDs exactly once")
    if Counter(row["version_a_role"] for row in key_rows) != {"confident": 3, "hesitant": 3}:
        raise ValueError("Version-A roles must be balanced 3/3")
    direction = natural = no_major = clear = content = 0
    length_counts = Counter()
    word_totals = Counter()
    shorter_rule_correct = 0
    for identifier, row in indexed.items():
        if any(row.get(field) not in values for field, values in allowed.items()):
            raise ValueError("review contains an invalid or missing assessment")
        intended = "a" if key[identifier]["version_a_role"] == "confident" else "b"
        direction += row["more_confident"] == intended
        content += row["factual_core"] == "preserved"
        clear += row["contrast"] == "clear"
        natural += row["naturalness_a"] == row["naturalness_b"] == "natural"
        no_major += "major_issues" not in (row["naturalness_a"], row["naturalness_b"])
        lengths = {role: len(drafts[identifier][role + "_response"].split())
                   for role in ("confident", "hesitant")}
        word_totals.update(lengths)
        length_counts["hesitant_longer" if lengths["hesitant"] > lengths["confident"]
                      else "confident_longer" if lengths["confident"] > lengths["hesitant"]
                      else "equal"] += 1
        shorter_rule_correct += lengths["confident"] < lengths["hesitant"]
    return {
        "review_counts": {
            "factual_core_preserved": content,
            "intended_confident_version_selected": direction,
            "clear_certainty_contrast": clear,
            "both_versions_natural": natural,
            "neither_version_has_major_naturalness_issues": no_major,
        },
        "construction_diagnostics": {
            "length_measure": "whitespace_words_not_model_tokens",
            "length_direction_counts": dict(length_counts),
            "total_words_by_role": dict(word_totals),
            "shorter_text_selects_intended_confident_pairs": shorter_rule_correct,
            "diagnostic_is_not_probe_performance": True,
        },
    }


def main() -> None:
    paths = {
        "preview_status": BASE / "results" / "epistemic_preview_v1_status.json",
        "source": PRIVATE / "SOURCE_ONLY.json",
        "draft": PRIVATE / "DRAFT_PAIRS.json",
        "reviewer_html": PRIVATE / "reviewer_only" / "BLIND_REVIEW.html",
        "answer_key": PRIVATE / "private_key" / "KEY.json",
        "model_review": PRIVATE / "model_review" / "MODEL_REVIEW.json",
    }
    frozen = read(paths["preview_status"])
    for artifact in ("source", "draft"):
        if digest(paths[artifact]) != frozen[artifact + "_sha256"]:
            raise ValueError(f"{artifact} differs from the saved preview")
    result = read(paths["model_review"])
    if (result.get("schema") != "epistemic-preview-model-review-v1"
            or result.get("review_type") != "blinded_model_assisted"
            or result.get("pair_count") != 6
            or result.get("human_review_certified") is not False
            or result.get("packet_sha256") != frozen["packet_sha256"]
            or result.get("html_sha256") != digest(paths["reviewer_html"])):
        raise ValueError("review metadata does not bind the saved HTML packet")
    sources = read(paths["source"])["sources"]
    pairs = read(paths["draft"])["pairs"]
    key = read(paths["answer_key"])["rows"]
    pairs_by_id = {r["preview_id"]: r for r in pairs}
    key_by_id = {r["preview_id"]: r for r in key}
    blinded = []
    for source in sources:
        identifier = source["preview_id"]
        a = key_by_id[identifier]["version_a_role"]
        b = "hesitant" if a == "confident" else "confident"
        blinded.append({"review_id": identifier, "question": source["prompt"],
                        "original_response": source["original_response"],
                        "version_a": pairs_by_id[identifier][a + "_response"],
                        "version_b": pairs_by_id[identifier][b + "_response"]})
    if review.sha256_value(blinded) != frozen["packet_sha256"]:
        raise ValueError("answer key or saved packet binding changed")
    summary = {
        "schema": "epistemic-preview-model-review-summary-v1",
        "status": "model_review_complete_researcher_feedback_pending",
        "artifact_role": "development_preview", "pair_count": 6,
        "reviewer_count": 1, "review_type": "blinded_model_assisted",
        "packet_sha256": frozen["packet_sha256"],
        "input_sha256": {name: digest(path) for name, path in paths.items()},
        "human_review_certified": False,
        "activation_extraction_started": False, "probe_fitting_started": False,
        "sdt_training_started": False,
        **summarize(result["rows"], key, pairs),
        "interpretation": "These are reviewer judgments and text-construction diagnostics, not model-confidence or probe-performance measurements.",
        "next_action": "Review the six drafts, then improve length counterbalancing and wording diversity before a larger construction run. Ordinary epistemic hedging remains allowed.",
    }
    review._write_json(BASE / "results" / "epistemic_preview_v1_model_review_summary.json", summary)
    print(json.dumps({"pair_count": 6, **summary["review_counts"],
                      "construction_diagnostics": summary["construction_diagnostics"]}))


if __name__ == "__main__":
    main()
