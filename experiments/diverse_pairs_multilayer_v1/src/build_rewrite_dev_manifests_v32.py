"""Freeze the independent v3.2 prompt-development smoke source set.

This builder is deliberately offline and text-safe in public artifacts.  It
reads only the already-cached acquisition candidates, excludes every frozen
source and development set named in the v3.2 configuration, and binds eight
source-only reviewed records to a fully prespecified design.  It never calls a
model and never edits any v3/v3.1 file or output.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Sequence

from experiments.diverse_pairs_multilayer_v1.src import (
    build_rewrite_dev_manifests_v31 as v31,
)
from experiments.diverse_pairs_multilayer_v1.src import (
    run_claude_rewrite_batches_v3 as v3_runner,
)


BASE = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = BASE / "configs" / "claude_rewrite_dev_v32.json"
BUILDER_VERSION = "3.2"
PROTOCOL_VERSION = "claude-symmetric-diverse-rewrite-v3.2"

# These generic checks are public protocol, while the actual source identities,
# design-cell assignments, and topic-level review notes remain in the ignored,
# hash-bound independent review artifact.
REQUIRED_REVIEW_CHECKS = (
    "ordinary_assistant_response",
    "stable_truth_apt_or_instructional_claims",
    "not_roleplay_or_fiction",
    "not_correspondence_or_politeness_only",
    "not_promotional_or_motivational_copy",
    "not_refusal_or_meta_request",
    "not_unstable_or_high_stakes",
    "task_label_defensible",
    "content_suitable_for_paired_rewrite",
)
REVIEW_PROTOCOL_VERSION = "v32-source-suitability-review-1"


def resolve(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else BASE / path


def _canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _word_count(text: str) -> int:
    return len(re.findall(r"\S+", text))


def _jsonl_bytes(rows: Iterable[dict[str, Any]]) -> bytes:
    return b"".join(
        json.dumps(row, ensure_ascii=False, sort_keys=True).encode("utf-8") + b"\n"
        for row in rows
    )


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line.decode("utf-8"))
        for line in path.read_bytes().splitlines()
        if line.strip()
    ]


def _counts(rows: Sequence[dict[str, Any]], field: str) -> dict[str, int]:
    return dict(sorted(Counter(str(row[field]) for row in rows).items()))


def _directory_inventory(root: Path) -> dict[str, Any]:
    files = sorted(path for path in root.rglob("*") if path.is_file())
    entries = [
        {"path": path.relative_to(root).as_posix(), "sha256": _sha256_file(path)}
        for path in files
    ]
    return {
        "root_name": root.name,
        "file_count": len(entries),
        "inventory_sha256": _sha256_bytes(_canonical_json_bytes(entries)),
    }


def _forbidden_identity(rows: Sequence[dict[str, Any]]) -> dict[str, set[str]]:
    return {
        "source_id": {str(row.get("source_id", "")) for row in rows if row.get("source_id")},
        "canonical_prompt_sha256": {
            str(row.get("canonical_prompt_sha256", ""))
            for row in rows if row.get("canonical_prompt_sha256")
        },
        "normalized_response_sha256": {
            str(row.get("normalized_response_sha256", ""))
            for row in rows if row.get("normalized_response_sha256")
        },
        "group_id": {str(row.get("group_id", "")) for row in rows if row.get("group_id")},
    }


def _source_record_hash(row: dict[str, Any]) -> str:
    payload = {key: value for key, value in row.items() if key != "source_record_sha256"}
    return _sha256_bytes(_canonical_json_bytes(payload))


def _load_completed_review(
    config: dict[str, Any],
) -> tuple[Path, dict[str, Any], list[dict[str, Any]]]:
    path = resolve(str(config["private_selection_review_path"]))
    expected_hash = str(config["private_selection_review_sha256"])
    if _sha256_file(path) != expected_hash:
        raise ValueError("Private v3.2 selection/review artifact hash mismatch")
    review = json.loads(path.read_text(encoding="utf-8"))
    required_header = {
        "review_protocol_version": REVIEW_PROTOCOL_VERSION,
        "reviewer_type": "agent",
        "review_independent_of_builder": True,
        "generation_outputs_seen": False,
        "source_count": 8,
    }
    for key, expected in required_header.items():
        if review.get(key) != expected:
            raise ValueError(f"Private v3.2 source review has invalid {key}")
    marker = review.get("review_completion_marker")
    if not isinstance(marker, str) or not marker.strip():
        raise ValueError("Private v3.2 source review is not marked complete")
    records = review.get("records")
    if not isinstance(records, list) or len(records) != 8:
        raise ValueError("Private v3.2 source review must contain exactly eight rows")
    if len({str(row.get("source_id", "")) for row in records}) != 8:
        raise ValueError("Private v3.2 source review contains duplicate source IDs")
    for index, row in enumerate(records, start=1):
        if row.get("review_index") != index:
            raise ValueError("Private v3.2 source review order changed")
        if row.get("decision") != "primary_eligible":
            raise ValueError("Every selected v3.2 source must be independently eligible")
        checklist = row.get("checklist")
        if not isinstance(checklist, dict) or set(checklist) != set(REQUIRED_REVIEW_CHECKS):
            raise ValueError("Private v3.2 source-review checklist fields changed")
        if any(checklist[key] is not True for key in REQUIRED_REVIEW_CHECKS):
            raise ValueError("Private v3.2 source review has an unmet suitability check")
        for key in (
            "source_id", "original_response_sha256", "canonical_prompt_sha256",
            "normalized_response_sha256", "group_id", "rewrite_dev_slot",
            "review_notes",
        ):
            if not isinstance(row.get(key), str) or not str(row[key]).strip():
                raise ValueError(f"Private v3.2 source review is missing {key}")
        if row.get("rewrite_recipe") not in {"A", "B"}:
            raise ValueError("Private v3.2 recipe assignment changed")
        if row.get("stance_topology") not in {"early", "middle", "late", "distributed"}:
            raise ValueError("Private v3.2 topology assignment changed")
        if row.get("rewrite_output_order") not in {"confident_first", "hedged_first"}:
            raise ValueError("Private v3.2 output-order assignment changed")
        if row.get("target_longer_member") not in {"confident", "hedged"}:
            raise ValueError("Private v3.2 length-direction assignment changed")
    return path, review, records


def _decorate(source: dict[str, Any], reviewed: dict[str, Any]) -> dict[str, Any]:
    row = dict(source)
    original = str(row["original_response"])
    review_notes = str(reviewed["review_notes"]).rstrip(".")
    review_basis = review_notes[:1].lower() + review_notes[1:]
    row.update({
        key: reviewed[key] for key in (
            "rewrite_dev_slot", "rewrite_recipe", "stance_topology",
            "rewrite_output_order", "target_longer_member",
        )
    })
    row.update({
        "pool_partition": "v32_cached_candidate_expansion",
        "split": str(row.get("original_split", "train")),
        "rewrite_dev_protocol": "symmetric-diverse-v32",
        "rewrite_dev_set": "smoke",
        "source_suitability_status": "primary_eligible",
        "source_suitability_rule_version": BUILDER_VERSION,
        "source_only_semantic_review": "passed_by_agent_not_human_certified",
        "source_only_semantic_review_basis": review_basis,
    })
    source_words = _word_count(original)
    editable_tokens = int(v3_runner._edit_stats(row, original, original)["left_tokens"])
    target_longer = str(row["target_longer_member"])
    longer_words, shorter_words = source_words + 2, source_words - 1
    row.update({
        "source_word_count": source_words,
        "source_editable_token_count": editable_tokens,
        "min_substantive_replacements_or_deletions": max(
            3, math.ceil(0.10 * max(1, editable_tokens))
        ),
        "confident_target_words": longer_words if target_longer == "confident" else shorter_words,
        "hedged_target_words": longer_words if target_longer == "hedged" else shorter_words,
        "desired_pair_word_gap_min": 1,
        "desired_pair_word_gap_max": 5,
        "dynamic_pair_word_gap_max": max(5, math.ceil(0.08 * source_words)),
    })
    row["source_record_sha256"] = _source_record_hash(row)
    return row


def _validate_selected(
    rows: Sequence[dict[str, Any]],
    set_config: dict[str, Any],
    forbidden: dict[str, set[str]],
) -> None:
    if len(rows) != 8 or len({row["source_id"] for row in rows}) != 8:
        raise ValueError("V3.2 smoke must contain eight unique frozen sources")
    for row in rows:
        for field, values in forbidden.items():
            value = str(row.get(field, ""))
            if value and value in values:
                raise ValueError(f"V3.2 source overlaps prior data by {field}")
        if row.get("source_suitability_status") != "primary_eligible":
            raise ValueError("Every executable v3.2 source must be primary_eligible")
        if row.get("source_only_semantic_review") != "passed_by_agent_not_human_certified":
            raise ValueError("V3.2 smoke requires explicit source-only review status")
        if v31.source_suitability_reasons(row):
            raise ValueError(f"V3.2 source now fails suitability rules: {row['source_id']}")
        if row.get("original_split") != "train" or row.get("split") != "train":
            raise ValueError("V3.2 smoke is restricted to cached train sources")
        if _sha256_bytes(str(row["original_response"]).encode("utf-8")) != row.get(
            "original_response_sha256"
        ):
            raise ValueError("Original response hash mismatch")
        if _source_record_hash(row) != row.get("source_record_sha256"):
            raise ValueError("V3.2 source-record hash mismatch")
        if abs(int(row["confident_target_words"]) - int(row["hedged_target_words"])) != 3:
            raise ValueError("V3.2 exact word targets must differ by three words")
        for key in ("confident_target_words", "hedged_target_words"):
            ratio = int(row[key]) / int(row["source_word_count"])
            if not 0.9 <= ratio <= 1.1:
                raise ValueError("V3.2 exact word target is outside 90%-110%")
    for field, key in (
        ("dataset", "dataset_counts"),
        ("task", "task_counts"),
        ("length_bin", "length_counts"),
        ("target_longer_member", "target_longer_member_counts"),
    ):
        if _counts(rows, field) != dict(sorted(set_config[key].items())):
            raise ValueError(f"V3.2 {field} quota mismatch")
    if _counts(rows, "rewrite_recipe") != {"A": 4, "B": 4}:
        raise ValueError("V3.2 recipe allocation must be 4/4")
    if _counts(rows, "stance_topology") != {
        "distributed": 2, "early": 2, "late": 2, "middle": 2
    }:
        raise ValueError("V3.2 topology allocation must be exactly balanced")
    if _counts(rows, "rewrite_output_order") != {
        "confident_first": 4, "hedged_first": 4
    }:
        raise ValueError("V3.2 output order must be 4/4")


def build(config_path: Path = DEFAULT_CONFIG) -> dict[str, Any]:
    config_bytes = config_path.read_bytes()
    config = json.loads(config_bytes)
    if config.get("protocol_version") != PROTOCOL_VERSION:
        raise ValueError("Wrong v3.2 rewrite configuration")
    review_path, source_review, reviewed_records = _load_completed_review(config)

    cache_paths = [resolve(value) for value in config["cached_candidate_inputs"]]
    if len(cache_paths) != len(set(cache_paths)):
        raise ValueError("Cached v3.2 candidate inputs must be unique")
    cache_rows: list[dict[str, Any]] = []
    source_cache_path: dict[str, str] = {}
    for path in cache_paths:
        for row in _read_jsonl(path):
            cache_rows.append(row)
            source_cache_path[str(row["source_id"])] = path.relative_to(BASE).as_posix()
    if len(cache_rows) > int(config["max_cached_candidate_rows"]):
        raise ValueError("Bounded cached-candidate row limit exceeded")

    forbidden_paths = [resolve(value) for value in config["forbidden_source_inputs"]]
    forbidden_rows = [row for path in forbidden_paths for row in _read_jsonl(path)]
    forbidden = _forbidden_identity(forbidden_rows)
    by_id = {str(row["source_id"]): row for row in cache_rows}
    if len(by_id) != len(cache_rows):
        raise ValueError("Cached source IDs are not unique")
    reviewed_ids = [str(row["source_id"]) for row in reviewed_records]
    missing = [source_id for source_id in reviewed_ids if source_id not in by_id]
    if missing:
        raise ValueError(f"Reviewed v3.2 smoke sources missing from cache: {missing}")

    rows: list[dict[str, Any]] = []
    for reviewed in reviewed_records:
        source_id = str(reviewed["source_id"])
        source = dict(by_id[source_id])
        for field in (
            "original_response_sha256", "canonical_prompt_sha256",
            "normalized_response_sha256", "group_id",
        ):
            if source.get(field) != reviewed.get(field):
                raise ValueError(
                    f"Reviewed v3.2 source identity mismatch for private field {field}"
                )
        source["source_cache_file"] = source_cache_path[source_id]
        rows.append(_decorate(source, reviewed))
    set_config = config["sets"]["smoke"]
    _validate_selected(rows, set_config, forbidden)

    private_dir = resolve(config["private_manifest_dir"])
    smoke_path = private_dir / set_config["input_file"]
    smoke_bytes = _jsonl_bytes(rows)
    v31.v3.write_once_or_verify(smoke_path, smoke_bytes)

    eligible_after_automatic_rules = [
        row for row in cache_rows
        if str(row.get("source_id", "")) not in forbidden["source_id"]
        and row.get("original_split") == "train"
        and not v31.source_suitability_reasons(row)
    ]
    status = {
        "protocol_version": PROTOCOL_VERSION,
        "cached_rows_scanned": len(cache_rows),
        "bounded_row_limit": int(config["max_cached_candidate_rows"]),
        "automatic_primary_eligible_after_id_exclusion": len(eligible_after_automatic_rules),
        "selected_source_count": len(rows),
        "selected_source_ids": [row["source_id"] for row in rows],
        "selected_review_status": "passed_by_agent_not_human_certified",
        "human_certification": False,
        "execution_source_gate": "ready",
    }
    status_path = private_dir / "SOURCE_SUITABILITY_STATUS.json"
    status_bytes = (json.dumps(status, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    v31.v3.write_once_or_verify(status_path, status_bytes)

    legacy_manifests = [resolve(value) for value in config["legacy_public_manifests"]]
    legacy_outputs = [resolve(value) for value in config["legacy_output_roots"]]
    public = {
        "freeze_version": BUILDER_VERSION,
        "protocol_version": PROTOCOL_VERSION,
        "contains_source_text": False,
        "rewrite_generation_performed": False,
        "source_selection_ready": True,
        "source_review_status": "passed_by_agent_not_human_certified",
        "human_source_certification": False,
        "selection_seed": int(config["selection_seed"]),
        "selection_scope": "bounded offline cached acquisition expansion; train split only",
        "main_final_and_frozen_pool_excluded": True,
        "all_v3_v31_smoke_canary_candidate_sources_excluded": True,
        "duplicate_identity_exclusions": [
            "source_id", "canonical_prompt_sha256", "normalized_response_sha256", "group_id"
        ],
        "cached_candidate_inputs": {
            path.relative_to(BASE).as_posix(): _sha256_file(path) for path in cache_paths
        },
        "cached_rows_scanned": len(cache_rows),
        "cached_row_limit": int(config["max_cached_candidate_rows"]),
        "forbidden_source_inputs": {
            path.relative_to(BASE).as_posix(): _sha256_file(path) for path in forbidden_paths
        },
        "forbidden_unique_source_ids": len(forbidden["source_id"]),
        "legacy_public_manifest_sha256": {
            path.name: _sha256_file(path) for path in legacy_manifests
        },
        "legacy_output_inventory": [_directory_inventory(path) for path in legacy_outputs],
        "legacy_files_modified": False,
        "config_sha256": _sha256_bytes(config_bytes),
        "builder_source_sha256": _sha256_file(Path(__file__)),
        "private_source_review": {
            "file_name": review_path.name,
            "file_sha256": _sha256_file(review_path),
            "review_protocol_version": source_review["review_protocol_version"],
            "reviewer_type": source_review["reviewer_type"],
            "review_independent_of_builder": source_review["review_independent_of_builder"],
            "generation_outputs_seen": source_review["generation_outputs_seen"],
            "review_completion_marker": source_review["review_completion_marker"],
            "decision_counts": {"primary_eligible": len(reviewed_records)},
            "status_file_name": status_path.name,
            "status_file_sha256": _sha256_bytes(status_bytes),
        },
        "sets": {
            "smoke": {
                "count": len(rows),
                "file_name": smoke_path.name,
                "file_sha256": _sha256_bytes(smoke_bytes),
                "source_ids_sha256": _sha256_bytes(
                    _canonical_json_bytes([row["source_id"] for row in rows])
                ),
                "source_records_sha256": _sha256_bytes(
                    _canonical_json_bytes([row["source_record_sha256"] for row in rows])
                ),
                "source_suitability_status": "primary_eligible",
                "dataset_counts": _counts(rows, "dataset"),
                "task_counts": _counts(rows, "task"),
                "length_counts": _counts(rows, "length_bin"),
                "recipe_counts": _counts(rows, "rewrite_recipe"),
                "topology_counts": _counts(rows, "stance_topology"),
                "output_order_counts": _counts(rows, "rewrite_output_order"),
                "target_longer_member_counts": _counts(rows, "target_longer_member"),
                "target_word_gap_counts": dict(sorted(Counter(
                    str(abs(row["confident_target_words"] - row["hedged_target_words"]))
                    for row in rows
                ).items())),
                "private_file_write_policy": "write_once_or_verify_identical_bytes",
            }
        },
    }
    public_path = resolve(config["public_freeze_manifest_path"])
    public_bytes = (json.dumps(public, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    v31.v3.write_once_or_verify(public_path, public_bytes)
    return public


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    args = parser.parse_args(argv)
    result = build(args.config.resolve())
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
