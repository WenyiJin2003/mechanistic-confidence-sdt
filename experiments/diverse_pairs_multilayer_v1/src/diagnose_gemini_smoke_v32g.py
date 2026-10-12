"""Diagnose the cached Gemini v3.2g smoke without another model call.

Gemini returned all eight records as a fenced top-level array with transparent
field aliases and trailing prose.  This script maps only those known aliases to
the frozen v3.2 schema, reruns the unchanged v3.2 mechanical validator, and
keeps transport-format compliance separate from content diagnostics.  The
adapter can never authorize scaling.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

if __package__ in {None, ""}:  # pragma: no cover
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from experiments.diverse_pairs_multilayer_v1.src import (
    run_claude_rewrite_batches_v32 as v32,
)
from experiments.diverse_pairs_multilayer_v1.src import (
    run_gemini_rewrite_smoke_v32g as gemini,
)


BASE = Path(__file__).resolve().parents[1]
RAW_PATH = (
    BASE
    / "private_data/gemini_rewrite_dev_v32g_textonly/smoke/raw/attempt_0.json"
)
PRIVATE_REPORT = (
    BASE
    / "private_data/gemini_rewrite_dev_v32g_textonly/smoke/diagnostic/normalized.json"
)
PUBLIC_REPORT = BASE / "reports/gemini_smoke_v32g_textonly_diagnostic.json"
EXPECTED_KEYS = {
    "source_id",
    "original_response_sha256",
    "source_record_sha256",
    "recipe",
    "topology",
    "target_direction",
    "confident_target_words_exact",
    "hedged_target_words_exact",
    "not_applicable",
    "issue_description",
    "confident_response",
    "hedged_response",
}


def _extract_array(response: str) -> tuple[list[dict[str, Any]], int]:
    value_text = response.lstrip()
    if value_text.lower().startswith("```json"):
        value_text = value_text[7:].lstrip()
    value, end = json.JSONDecoder().raw_decode(value_text)
    if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
        raise ValueError("Diagnostic adapter accepts only a top-level object array")
    trailing = value_text[end:].strip()
    return list(value), len(trailing)


def _map_item(item: Mapping[str, Any], source: Mapping[str, Any]) -> dict[str, Any]:
    if set(item) != EXPECTED_KEYS:
        raise ValueError(
            f"Unexpected Gemini field set for {source['source_id']}: "
            f"{sorted(set(item) ^ EXPECTED_KEYS)}"
        )
    direction = {
        "confident_longer": "confident",
        "hedged_longer": "hedged",
    }.get(item["target_direction"])
    if direction is None:
        raise ValueError("Unexpected Gemini target_direction")
    issue = item["issue_description"]
    if not isinstance(issue, str):
        raise ValueError("Gemini issue_description is not a string")
    responses = {
        "confident": item["confident_response"],
        "hedged": item["hedged_response"],
    }
    order = str(source["rewrite_output_order"])
    first = "confident" if order == "confident_first" else "hedged"
    second = "hedged" if first == "confident" else "confident"
    return {
        "source_id": item["source_id"],
        "original_response_sha256": item["original_response_sha256"],
        "source_record_sha256": item["source_record_sha256"],
        "rewrite_recipe": item["recipe"],
        "stance_topology": item["topology"],
        "target_longer_member": direction,
        "confident_target_words": item["confident_target_words_exact"],
        "hedged_target_words": item["hedged_target_words_exact"],
        "first_label": first,
        "first_response": responses[first],
        "second_label": second,
        "second_response": responses[second],
        "not_applicable": item["not_applicable"],
        "issues": [issue] if issue.strip() else [],
    }


def main(argv: Sequence[str] | None = None) -> int:
    del argv
    raw = json.loads(RAW_PATH.read_text(encoding="utf-8"))
    envelope = json.loads(str(raw["stdout"]))
    response = envelope.get("response")
    if not isinstance(response, str) or not response.strip():
        raise ValueError("Cached Gemini response is empty")
    items, trailing_chars = _extract_array(response)
    source_config = v32.load_config(v32.DEFAULT_CONFIG, "smoke")
    rows, _ = v32.validate_frozen_input(source_config)
    if len(items) != len(rows) or len(rows) != 8:
        raise ValueError("Gemini diagnostic count differs from frozen smoke count")
    mapped = [_map_item(item, source) for item, source in zip(items, rows)]
    batch = v32.make_batches(rows, "smoke", 8)[0]
    tokenizer = v32.v2.load_pinned_tokenizer(v32.v2.tokenizer_file_hashes())
    records, batch_issues = v32.validate_structured_output(
        batch, {"pairs": mapped}, source_config, tokenizer
    )
    for record in records:
        record["generation_attempt"] = 0
        record["attempt_fingerprint"] = raw["generation_fingerprint"]
    deviations = [
        "missing_structured_output_envelope",
        "top_level_array_instead_of_pairs_object",
        "known_field_aliases_required",
    ]
    if trailing_chars:
        deviations.append("trailing_non_json_text")
    private = {
        "diagnostic_only": True,
        "scale_authorized": False,
        "source_raw_artifact": str(RAW_PATH.relative_to(BASE)),
        "source_raw_artifact_sha256": v32.v2.sha256_file(RAW_PATH),
        "generation_contract_sha256": raw["generation_contract_sha256"],
        "transport_format_deviations": deviations,
        "trailing_non_json_chars": trailing_chars,
        "batch_validation_issues": batch_issues,
        "records": records,
        "records_sha256": v32.v2.sha256_bytes(gemini._canonical(records)),
    }
    gemini._immutable_json(PRIVATE_REPORT, private)
    counts = Counter(str(record["status"]) for record in records)
    public = {
        "protocol_version": gemini.PROTOCOL_VERSION,
        "diagnostic_only": True,
        "source_count": len(records),
        "status_counts_after_declared_alias_mapping": {
            name: counts.get(name, 0)
            for name in (
                "accepted",
                "needs_review",
                "not_applicable",
                "validation_failed",
            )
        },
        "batch_validation_issue_count": len(batch_issues),
        "transport_format_deviations": deviations,
        "strict_smoke_gate_pass": False,
        "scale_authorized": False,
        "semantic_human_review_required": True,
        "contains_source_text": False,
        "generation_contract_sha256": raw["generation_contract_sha256"],
    }
    gemini._immutable_json(PUBLIC_REPORT, public)
    print(json.dumps(public, sort_keys=True))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
