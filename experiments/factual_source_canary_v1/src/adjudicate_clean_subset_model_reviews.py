"""Aggregate two independent blinded model reviews of the clean-six packet.

The public output contains counts and hashes only. It is a diagnostic gate,
not human certification or authorization for downstream model work.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence


SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
import build_factual_rewrite_review as review


BASE = Path(__file__).resolve().parents[1]
PRIVATE = (BASE / "private_data").resolve()
PACKET_DIR = PRIVATE / "rewrite_canary_v1" / "blind_review_clean6_v4"
DEFAULT_MANIFEST = PACKET_DIR / "BLIND_REVIEW_MANIFEST.json"
DEFAULT_KEY = PACKET_DIR / "private_key" / "BLIND_REVIEW_KEY.json"
DEFAULT_REVIEWS = (
    PACKET_DIR / "model_reviews" / "MODEL_REVIEW_A.json",
    PACKET_DIR / "model_reviews" / "MODEL_REVIEW_B.json",
)
DEFAULT_OUTPUT = (
    BASE / "results" / "rewrite_canary_v4_clean_six_model_review_summary.json"
)
EXPECTED_PAIRS = 6
ALLOWED = {
    "source_fidelity": {
        "both_preserve", "a_drift", "b_drift", "both_drift", "uncertain"
    },
    "pair_content_equivalence": {"equivalent", "different", "uncertain"},
    "qualifier_preservation": {
        "both_preserve", "a_changes", "b_changes", "both_change",
        "not_applicable", "uncertain",
    },
    "speaker_level_scope": {
        "both_speaker_level", "a_object_level_shift", "b_object_level_shift",
        "both_object_level_shift", "uncertain",
    },
    "certainty_a": {"1", "2", "3", "4", "5"},
    "certainty_b": {"1", "2", "3", "4", "5"},
    "stronger_certainty": {"a", "b", "tie", "uncertain"},
    "naturalness_a": {"natural", "minor", "unnatural", "uncertain"},
    "naturalness_b": {"natural", "minor", "unnatural", "uncertain"},
    "formatting_mismatch": {"none", "a", "b", "both", "uncertain"},
    "shortcut_concern": {"none", "a", "b", "both", "uncertain"},
}


def read_object(path: Path) -> dict[str, Any]:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate_manifest(manifest: Mapping[str, Any]) -> tuple[str, str]:
    if manifest.get("schema") != "factual-rewrite-clean-subset-blind-review-v1":
        raise ValueError("unrecognized clean-subset manifest")
    if manifest.get("artifact_role") != "interim_failure_discovery_only":
        raise ValueError("clean-subset manifest has the wrong artifact role")
    if manifest.get("pair_count") != EXPECTED_PAIRS:
        raise ValueError("clean-subset manifest must contain six pairs")
    if (
        manifest.get("blinded") is not True
        or manifest.get("answer_key_embedded_in_html") is not False
        or manifest.get("final_canary_certification") is not False
        or manifest.get("human_review_certified") is not False
    ):
        raise ValueError("clean-subset manifest violates the blinding boundary")
    packet_hash = manifest.get("packet_sha256")
    if not isinstance(packet_hash, str) or len(packet_hash) != 64:
        raise ValueError("clean-subset manifest requires a packet hash")
    answer_key_hash = manifest.get("answer_key_sha256")
    if not isinstance(answer_key_hash, str) or len(answer_key_hash) != 64:
        raise ValueError("clean-subset manifest requires an answer-key hash")
    return packet_hash, answer_key_hash


def validate_input_hashes(
    input_sha256: Mapping[str, Any], expected_answer_key_hash: str
) -> None:
    if input_sha256.get("answer_key") != expected_answer_key_hash:
        raise ValueError("answer key does not match the manifest hash")
    review_hashes = input_sha256.get("model_reviews")
    if (
        not isinstance(review_hashes, list)
        or len(review_hashes) != 2
        or any(not isinstance(value, str) or len(value) != 64 for value in review_hashes)
        or len(set(review_hashes)) != 2
    ):
        raise ValueError("model review files must have two distinct SHA-256 hashes")


def validate_key(key: Mapping[str, Any], packet_hash: str) -> dict[str, Mapping[str, Any]]:
    if key.get("schema") != "factual-rewrite-clean-subset-blind-key-v1":
        raise ValueError("unrecognized clean-subset key")
    if key.get("packet_sha256") != packet_hash:
        raise ValueError("clean-subset key does not match the packet")
    rows = key.get("rows")
    if not isinstance(rows, list) or len(rows) != EXPECTED_PAIRS:
        raise ValueError("clean-subset key must contain six rows")
    result: dict[str, Mapping[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("clean-subset key rows must be objects")
        review_id = row.get("review_id")
        if (
            not isinstance(review_id, str)
            or not review_id.startswith("C6R")
            or review_id in result
        ):
            raise ValueError("clean-subset key review IDs are invalid")
        if row.get("version_a_role") not in {"confident", "hesitant"}:
            raise ValueError("clean-subset key has an invalid Version-A role")
        if row.get("version_b_role") not in {"confident", "hesitant"}:
            raise ValueError("clean-subset key has an invalid Version-B role")
        if row["version_a_role"] == row["version_b_role"]:
            raise ValueError("clean-subset key roles must be opposite")
        result[review_id] = row
    return result


def validate_review(
    result: Mapping[str, Any], packet_hash: str, expected_ids: set[str]
) -> dict[str, Mapping[str, Any]]:
    if result.get("schema") != "factual-rewrite-clean-subset-review-results-v1":
        raise ValueError("unrecognized clean-subset review results")
    if (
        result.get("artifact_role") != "interim_failure_discovery_only"
        or result.get("review_type") != "model_assisted"
        or not isinstance(result.get("independent_context"), str)
        or not result["independent_context"].strip()
        or result.get("pair_count") != EXPECTED_PAIRS
        or result.get("packet_sha256") != packet_hash
        or result.get("blinded") is not True
        or result.get("final_canary_certification") is not False
        or result.get("human_review_certified") is not False
    ):
        raise ValueError("clean-subset review metadata is invalid")
    rows = result.get("reviews")
    if not isinstance(rows, list) or len(rows) != EXPECTED_PAIRS:
        raise ValueError("clean-subset review must contain six rows")
    indexed: dict[str, Mapping[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("clean-subset review rows must be objects")
        review_id = row.get("review_id")
        if not isinstance(review_id, str) or review_id in indexed:
            raise ValueError("clean-subset review IDs are invalid or duplicated")
        for field, allowed in ALLOWED.items():
            if row.get(field) not in allowed:
                raise ValueError(f"{review_id}: invalid {field}")
        indexed[review_id] = row
    if set(indexed) != expected_ids:
        raise ValueError("clean-subset review does not cover the packet")
    return indexed


def row_gates(row: Mapping[str, Any], intended: str) -> dict[str, bool]:
    content = (
        row["source_fidelity"] == "both_preserve"
        and row["pair_content_equivalence"] == "equivalent"
        and row["qualifier_preservation"] in {"both_preserve", "not_applicable"}
        and row["speaker_level_scope"] == "both_speaker_level"
    )
    confident_score = int(row[f"certainty_{intended}"])
    other = "b" if intended == "a" else "a"
    other_score = int(row[f"certainty_{other}"])
    intended_selected = row["stronger_certainty"] == intended
    direction_gap = intended_selected and confident_score - other_score >= 2
    natural = row["naturalness_a"] == row["naturalness_b"] == "natural"
    formatting = row["formatting_mismatch"] == "none"
    no_shortcut = row["shortcut_concern"] == "none"
    return {
        "content": content,
        "intended_selected": intended_selected,
        "direction_gap": direction_gap,
        "natural": natural,
        "formatting": formatting,
        "no_shortcut": no_shortcut,
        "strict_pass": (
            content and direction_gap and natural and formatting and no_shortcut
        ),
    }


def build_summary(
    manifest: Mapping[str, Any],
    key: Mapping[str, Any],
    review_results: Sequence[Mapping[str, Any]],
    *,
    input_sha256: Mapping[str, Any],
) -> dict[str, Any]:
    if len(review_results) != 2:
        raise ValueError("exactly two independent model-assisted reviews are required")
    packet_hash, answer_key_hash = validate_manifest(manifest)
    validate_input_hashes(input_sha256, answer_key_hash)
    contexts = [result.get("independent_context") for result in review_results]
    if len(set(contexts)) != 2:
        raise ValueError("model reviews must have distinct independent contexts")
    key_by_id = validate_key(key, packet_hash)
    expected_ids = set(key_by_id)
    reviews = [
        validate_review(result, packet_hash, expected_ids)
        for result in review_results
    ]

    exact_agreement = Counter()
    unanimous = Counter()
    individual_strict = [0, 0]
    for review_id in sorted(expected_ids):
        rows = [review[review_id] for review in reviews]
        for field in ("pair_content_equivalence", "stronger_certainty"):
            if rows[0][field] == rows[1][field]:
                exact_agreement[field] += 1
        intended = (
            "a" if key_by_id[review_id]["version_a_role"] == "confident" else "b"
        )
        gates = [row_gates(row, intended) for row in rows]
        for gate in gates[0]:
            if gates[0][gate] == gates[1][gate]:
                exact_agreement[f"binary_{gate}"] += 1
            if gates[0][gate] and gates[1][gate]:
                unanimous[gate] += 1
        for index, gate_values in enumerate(gates):
            individual_strict[index] += int(gate_values["strict_pass"])

    strict_passes = unanimous["strict_pass"]
    content_passes = unanimous["content"]
    summary = {
        "schema": "factual-rewrite-clean-subset-model-review-summary-v1",
        "status": "model_assisted_review_complete_pending_human_adjudication",
        "artifact_role": "interim_failure_discovery_only",
        "source_set_revision": "v4",
        "packet_sha256": packet_hash,
        "pair_count": EXPECTED_PAIRS,
        "reviewer_count": 2,
        "review_type": "independent_blinded_model_assisted",
        "agreement_counts": dict(sorted(exact_agreement.items())),
        "unanimous_gate_pass_counts": {
            gate: unanimous[gate]
            for gate in (
                "content",
                "intended_selected",
                "direction_gap",
                "natural",
                "formatting",
                "no_shortcut",
                "strict_pass",
            )
        },
        "reviewer_strict_pass_counts": individual_strict,
        "preliminary_outcome": {
            "strict_pass_pairs": strict_passes,
            "content_or_scope_failure_pairs": EXPECTED_PAIRS - content_passes,
            "content_pass_but_other_gate_failure_pairs": content_passes - strict_passes,
            "all_six_ready_for_final_canary": False,
        },
        "human_review_certified": False,
        "final_canary_certification": False,
        "authorization": {
            "replacement_generation": False,
            "activation_extraction": False,
            "probe_fitting": False,
            "sdt_training": False,
        },
        "interpretation": (
            "The two blinded model reviewers agreed that none of the six pairs "
            "passes every frozen content, direction, naturalness, and shortcut gate."
        ),
        "next_action": (
            "Human-adjudicate the six pairs before freezing the final failed-slot "
            "set; do not extend the v5 replacement plan or generate replacements yet."
        ),
    }
    summary["input_sha256"] = dict(input_sha256)
    return summary


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--answer-key", type=Path, default=DEFAULT_KEY)
    parser.add_argument(
        "--reviews", type=Path, nargs=2, default=list(DEFAULT_REVIEWS)
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    manifest = read_object(args.manifest)
    key = read_object(args.answer_key)
    review_results = [read_object(path) for path in args.reviews]
    summary = build_summary(
        manifest,
        key,
        review_results,
        input_sha256={
            "manifest": sha256_file(args.manifest),
            "answer_key": sha256_file(args.answer_key),
            "model_reviews": [sha256_file(path) for path in args.reviews],
        },
    )
    review._write_json(args.output, summary)
    print(json.dumps({
        "output": str(Path(args.output)),
        "status": summary["status"],
        "strict_pass_pairs": summary["preliminary_outcome"]["strict_pass_pairs"],
        "human_review_certified": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
