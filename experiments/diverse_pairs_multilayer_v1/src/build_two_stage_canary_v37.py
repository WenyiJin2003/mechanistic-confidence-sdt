"""Freeze the audited ten-source input for the v3.7 two-stage canary.

The input reuses the frozen v3.6 second batch, replacing the truncated P0020
source with the independently audited P0086 reserve.  The replacement keeps
its own source identity and response hash while inheriting only the four
experimental assignments from P0020.  Source text is written only below the
ignored ``private_data`` tree; the public manifest contains hashes and counts.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from copy import deepcopy
from pathlib import Path
from typing import Any, Sequence

if __package__ in {None, ""}:  # pragma: no cover
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from experiments.diverse_pairs_multilayer_v1.src import (
    run_claude_component_rewrite_v36 as v36,
)
from experiments.diverse_pairs_multilayer_v1.src import (
    run_claude_rewrite_batches as transport,
)


BASE = Path(__file__).resolve().parents[1]
ASSIGNED_POOL = (
    BASE
    / "private_data"
    / "gpt_rewrite_dev_v33"
    / "SOURCE_BATCH_200_ASSIGNED.jsonl"
)
PRIVATE_OUTPUT = (
    BASE / "private_data" / "rewrite_dev_v37" / "SOURCE_CANARY_10.jsonl"
)
PUBLIC_MANIFEST = BASE / "manifests" / "rewrite_dev_v37_freeze.json"

DONOR_SLOT = "P0020"
REPLACEMENT_SLOT = "P0086"
EXPECTED_DONOR_SOURCE_ID = (
    "wildchat-348d0c1117fa672dcb023a0f722f9117-turn-713731"
)
EXPECTED_DONOR_RESPONSE_SHA256 = (
    "ad463383a0c2d698047b8907889c0231d4b41b93c0b1377a49ab34ebee1a3256"
)
EXPECTED_REPLACEMENT_SOURCE_ID = (
    "wildchat-939c9085c8aa74f90fa903d92b866122-turn-577141"
)
EXPECTED_REPLACEMENT_RESPONSE_SHA256 = (
    "f419bcfcdd1e7ac4fe372ffe69e9b20911a32a63123ba835aeb349018e18c10b"
)
ASSIGNMENT_FIELDS = (
    "stance_topology",
    "rewrite_recipe",
    "rewrite_output_order",
    "target_longer_member",
)


def _response_hashes_sha256(rows: Sequence[dict[str, Any]]) -> str:
    joined = "\n".join(str(row["original_response_sha256"]) for row in rows)
    return transport.sha256_bytes(joined.encode("utf-8"))


def _write_jsonl(path: Path, rows: Sequence[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "".join(
        json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows
    )
    path.write_text(text, encoding="utf-8")


def build_rows() -> list[dict[str, Any]]:
    config = v36.load_config(v36.DEFAULT_CONFIG)
    old_batch = list(v36.load_frozen_batch(config))
    donors = [row for row in old_batch if row.get("production_slot") == DONOR_SLOT]
    if len(donors) != 1:
        raise ValueError("Frozen v3.6 batch must contain exactly one P0020 donor")
    donor = donors[0]
    if (
        donor.get("source_id") != EXPECTED_DONOR_SOURCE_ID
        or donor.get("original_response_sha256")
        != EXPECTED_DONOR_RESPONSE_SHA256
    ):
        raise ValueError("P0020 donor identity changed")

    pool = transport.read_jsonl(ASSIGNED_POOL)
    replacements = [
        row for row in pool if row.get("production_slot") == REPLACEMENT_SLOT
    ]
    if len(replacements) != 1:
        raise ValueError("Assigned pool must contain exactly one P0086 replacement")
    replacement = deepcopy(replacements[0])
    if (
        replacement.get("source_id") != EXPECTED_REPLACEMENT_SOURCE_ID
        or replacement.get("original_response_sha256")
        != EXPECTED_REPLACEMENT_RESPONSE_SHA256
    ):
        raise ValueError("P0086 replacement identity changed")
    if (
        transport.sha256_text(str(replacement.get("original_response", "")))
        != EXPECTED_REPLACEMENT_RESPONSE_SHA256
    ):
        raise ValueError("P0086 response text no longer matches its frozen hash")

    for field in ASSIGNMENT_FIELDS:
        replacement[field] = donor[field]
    replacement["v37_assignment_donor_slot"] = DONOR_SLOT
    replacement["v37_source_audit"] = (
        "eligible_in_source_review_and_independent_semantic_audit"
    )

    result: list[dict[str, Any]] = []
    for row in old_batch:
        result.append(replacement if row is donor else deepcopy(row))
    if len(result) != 10 or len({row["source_id"] for row in result}) != 10:
        raise ValueError("V3.7 source set must contain ten unique identities")
    if any(row.get("source_id") == EXPECTED_DONOR_SOURCE_ID for row in result):
        raise ValueError("Truncated P0020 source was not removed")
    if sum(row.get("source_id") == EXPECTED_REPLACEMENT_SOURCE_ID for row in result) != 1:
        raise ValueError("Audited P0086 replacement was not inserted exactly once")
    return result


def main() -> int:
    rows = build_rows()
    _write_jsonl(PRIVATE_OUTPUT, rows)
    assignment_counts = {
        field: dict(sorted(Counter(str(row[field]) for row in rows).items()))
        for field in ASSIGNMENT_FIELDS
    }
    manifest = {
        "protocol_version": "claude-two-stage-paraphrase-v3.7",
        "contains_source_text": False,
        "selected_source_count": len(rows),
        "selected_file_name": PRIVATE_OUTPUT.name,
        "selected_file_sha256": transport.sha256_file(PRIVATE_OUTPUT),
        "selected_source_ids_sha256": transport.source_ids_sha256(rows),
        "selected_response_hashes_sha256": _response_hashes_sha256(rows),
        "source_construction": (
            "v3.6_second_batch_with_one_independently_audited_replacement"
        ),
        "replacement": {
            "removed_production_slot": DONOR_SLOT,
            "inserted_source_production_slot": REPLACEMENT_SLOT,
            "copied_assignment_fields": list(ASSIGNMENT_FIELDS),
            "source_identity_and_response_hash_preserved": True,
            "independent_semantic_audit_decision": "eligible",
        },
        "assignment_counts": assignment_counts,
        "source_text_human_certified": False,
        "model_calls_for_selection": 0,
    }
    transport.atomic_write_json(PUBLIC_MANIFEST, manifest)
    print(
        json.dumps(
            {
                "selected": len(rows),
                "file_sha256": manifest["selected_file_sha256"],
                "source_ids_sha256": manifest["selected_source_ids_sha256"],
                "response_hashes_sha256": manifest[
                    "selected_response_hashes_sha256"
                ],
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
