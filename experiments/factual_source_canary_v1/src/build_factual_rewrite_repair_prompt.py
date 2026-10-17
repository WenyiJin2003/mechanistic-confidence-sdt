#!/usr/bin/env python3
"""Build a deterministic, writer-safe factual rewrite repair prompt.

The builder accepts writer-visible frozen source rows, prior candidate pairs,
a private validator report, a private repair-budget ledger, and a narrowly
typed repair specification.  Candidate responses are used only for integrity
checks.  They are never serialized into the output prompt.  Reviewer-only
metadata, free-form repair instructions, and ad-hoc surface-form bans are
rejected before any output is written.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import tempfile
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PRIVATE_ROOT = ROOT / "private_data"
SPEC_SCHEMA_VERSION = "factual-rewrite-repair-spec-v2"
MANIFEST_SCHEMA_VERSION = "factual-rewrite-repair-prompt-manifest-v2"
BUDGET_LEDGER_SCHEMA_VERSION = "factual-rewrite-repair-budget-ledger-v1"
VALIDATOR_NAME = "factual_direct_pair_rewrite_validator"
VALIDATOR_SCHEMA_VERSION = 1
SOURCE_RATIO_MIN = 0.85
SOURCE_RATIO_MAX = 1.15
PAIR_RATIO_MAX = 1.08
PAIR_GAP_MIN_ALLOWANCE = 5.0
PAIR_GAP_MEAN_FRACTION = 0.05

SOURCE_FIELDS = (
    "source_id",
    "dataset",
    "group_id",
    "source_hash",
    "original_response_sha256",
    "profile",
    "prompt",
    "original_response",
    "protected_spans",
    "cue_family",
    "length_direction",
    "draft_order",
    "generation_order",
)
SOURCE_REQUIRED_FIELDS = frozenset(SOURCE_FIELDS)
CANDIDATE_ALLOWED_FIELDS = frozenset(
    {
        "source_id",
        "source_hash",
        "original_response_sha256",
        "dataset",
        "cue_family",
        "length_direction",
        "draft_order",
        "generation_order",
        "confident_response",
        "hesitant_response",
        "issues",
    }
)
IDENTITY_FIELDS = (
    "source_hash",
    "original_response_sha256",
    "dataset",
    "cue_family",
    "length_direction",
    "draft_order",
)
VALIDATOR_IDENTITY_FIELDS = (
    "dataset",
    "group_id",
    "source_hash",
    "original_response_sha256",
    "cue_family",
    "length_direction",
    "draft_order",
    "generation_order",
)
SPEC_FIELDS = frozenset(
    {
        "schema_version",
        "repair_id",
        "repair_stage",
        "target_source_ids",
        "failure_codes",
        "banned_surface_forms",
    }
)
REPAIR_STAGES = frozenset({"first_full_pair", "final_length_only"})
BUDGET_LEDGER_FIELDS = frozenset(
    {"schema_version", "repair_id", "repair_stage", "entries"}
)
BUDGET_ENTRY_FIELDS = frozenset(
    {
        "source_id",
        "source_hash",
        "original_response_sha256",
        "confident_response_sha256",
        "hesitant_response_sha256",
        "counted_repairs",
    }
)
FORBIDDEN_FIELD_NAMES = frozenset(
    {
        "protected_qualifiers",
        "reviewer_semantic_qualifiers",
        "reviewer_metadata_correction",
        "content_checklist",
        "content_checklists",
        "evidence",
        "supporting_evidence",
        "source_locator",
        "model_review_notes",
        "source_repair_log",
        "metadata",
        "reviewer_notes",
        "semantic_checklist",
    }
)
ALLOWED_FAILURE_CODES = frozenset(
    {
        "frozen_length_policy_violation",
    }
)
FROZEN_LENGTH_FAILURE_FLAGS = frozenset(
    {
        "confident_source_token_ratio_out_of_bounds",
        "hesitant_source_token_ratio_out_of_bounds",
        "pair_token_ratio_over_limit",
        "pair_token_gap_over_limit",
        "length_direction_incorrect",
    }
)
FAILURE_REASON_TEXT = {
    "frozen_length_policy_violation": (
        "The earlier candidate violated one or more frozen length constraints. "
        "Rebuild both arms from the frozen source, keep each within 0.85 to 1.15 "
        "times the source-token length, keep the longer/shorter ratio at most 1.08, "
        "keep the absolute gap within max(5 tokens, 5% of the pair mean), and make "
        "the assigned length_direction strict rather than tied."
    ),
}

SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class RepairPromptError(ValueError):
    """Raised before output when a repair prompt is not writer-safe."""

    def __init__(self, errors: Sequence[str]):
        self.errors = tuple(errors)
        super().__init__("repair prompt validation failed: " + "; ".join(self.errors))


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_text(value: str) -> str:
    return _sha256_bytes(value.encode("utf-8"))


def _sha256_json(value: Any) -> str:
    return _sha256_bytes(
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    )


def _normalized_key(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(value).casefold()).strip("_")


def _forbidden_paths(value: Any, path: str = "$") -> list[str]:
    failures: list[str] = []
    if isinstance(value, Mapping):
        for key, nested in value.items():
            normalized = _normalized_key(key)
            child = f"{path}.{key}"
            if normalized in FORBIDDEN_FIELD_NAMES:
                failures.append(child)
            failures.extend(_forbidden_paths(nested, child))
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            failures.extend(_forbidden_paths(nested, f"{path}[{index}]"))
    return failures


def _read_bytes(path: Path) -> bytes:
    if not path.is_file():
        raise RepairPromptError([f"input_not_found:{path}"])
    try:
        return path.read_bytes()
    except OSError as error:
        raise RepairPromptError([f"input_read_failed:{path}:{error}"]) from error


def _load_json_bytes(path: Path, payload: bytes) -> Any:
    try:
        return json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise RepairPromptError([f"invalid_json:{path}:{error}"]) from error


def _load_json(path: Path) -> Any:
    return _load_json_bytes(path, _read_bytes(path))


def _read_records_bytes(path: Path, payload: bytes) -> list[dict[str, Any]]:
    if path.suffix.casefold() == ".jsonl":
        rows: list[Any] = []
        try:
            text = payload.decode("utf-8")
        except UnicodeDecodeError as error:
            raise RepairPromptError([f"invalid_json:{path}:{error}"]) from error
        for line_number, line in enumerate(text.splitlines(), 1):
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as error:
                raise RepairPromptError(
                    [f"invalid_json:{path}:{line_number}:{error.msg}"]
                ) from error
    else:
        document = _load_json_bytes(path, payload)
        if isinstance(document, list):
            rows = document
        elif isinstance(document, dict):
            keys = [
                key
                for key in ("pairs", "rows", "rewrites")
                if isinstance(document.get(key), list)
            ]
            if len(keys) != 1:
                raise RepairPromptError([f"json_rows_not_found:{path}"])
            rows = document[keys[0]]
        else:
            raise RepairPromptError([f"json_rows_not_found:{path}"])
    if any(not isinstance(row, dict) for row in rows):
        raise RepairPromptError([f"row_not_object:{path}"])
    return rows


def _read_records(path: Path) -> list[dict[str, Any]]:
    return _read_records_bytes(path, _read_bytes(path))


def _index_rows(
    rows: Sequence[dict[str, Any]], label: str, errors: list[str]
) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for position, row in enumerate(rows, 1):
        source_id = row.get("source_id")
        if not isinstance(source_id, str) or not source_id:
            errors.append(f"source_id_missing:{label}:{position}")
            continue
        if source_id in indexed:
            errors.append(f"duplicate_source_id:{label}:{source_id}")
            continue
        indexed[source_id] = row
    return indexed


def _validate_spec(payload: Any) -> tuple[str, str, list[str], list[str]]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        raise RepairPromptError(["repair_spec_not_object"])
    forbidden = _forbidden_paths(payload)
    errors.extend(f"forbidden_repair_spec_field:{path}" for path in forbidden)
    unknown = sorted(set(payload) - SPEC_FIELDS)
    missing = sorted(SPEC_FIELDS - set(payload))
    errors.extend(f"unknown_repair_spec_field:{field}" for field in unknown)
    errors.extend(f"missing_repair_spec_field:{field}" for field in missing)
    if errors:
        raise RepairPromptError(errors)

    if payload.get("schema_version") != SPEC_SCHEMA_VERSION:
        errors.append("repair_spec_schema_version_invalid")
    repair_id = payload.get("repair_id")
    if not isinstance(repair_id, str) or not SLUG_RE.fullmatch(repair_id):
        errors.append("repair_id_invalid")
    repair_stage = payload.get("repair_stage")
    if repair_stage not in REPAIR_STAGES:
        errors.append("repair_stage_invalid")

    target_ids = payload.get("target_source_ids")
    if (
        not isinstance(target_ids, list)
        or not target_ids
        or any(not isinstance(value, str) or not value for value in target_ids)
    ):
        errors.append("target_source_ids_invalid")
        target_ids = []
    elif len(target_ids) != len(set(target_ids)):
        errors.append("target_source_ids_duplicate")

    failure_codes = payload.get("failure_codes")
    if (
        not isinstance(failure_codes, list)
        or not failure_codes
        or any(not isinstance(value, str) for value in failure_codes)
    ):
        errors.append("failure_codes_invalid")
        failure_codes = []
    else:
        unknown_codes = sorted(set(failure_codes) - ALLOWED_FAILURE_CODES)
        errors.extend(f"failure_code_not_allowed:{code}" for code in unknown_codes)
        if len(failure_codes) != len(set(failure_codes)):
            errors.append("failure_codes_duplicate")

    raw_forms = payload.get("banned_surface_forms")
    if not isinstance(raw_forms, list) or any(not isinstance(value, str) for value in raw_forms):
        errors.append("banned_surface_forms_invalid")
        raw_forms = []
    elif raw_forms:
        errors.append("nonempty_banned_surface_forms_forbidden_without_preregistered_lexicon")

    if repair_stage == "final_length_only" and failure_codes != [
        "frozen_length_policy_violation"
    ]:
        errors.append("final_length_only_requires_only_frozen_length_policy_violation")

    if errors:
        raise RepairPromptError(errors)
    return str(repair_id), str(repair_stage), list(target_ids), sorted(failure_codes)


def _validate_inputs(
    source_rows: Sequence[dict[str, Any]],
    candidate_rows: Sequence[dict[str, Any]],
    target_ids: Sequence[str],
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    errors: list[str] = []
    for position, row in enumerate(source_rows, 1):
        forbidden = _forbidden_paths(row)
        errors.extend(
            f"forbidden_source_field:{position}:{path}" for path in forbidden
        )
        unknown = sorted(set(row) - SOURCE_REQUIRED_FIELDS)
        missing = sorted(SOURCE_REQUIRED_FIELDS - set(row))
        errors.extend(
            f"unknown_writer_source_field:{position}:{field}" for field in unknown
        )
        errors.extend(
            f"missing_writer_source_field:{position}:{field}" for field in missing
        )
        source_id = row.get("source_id")
        for field in (
            "source_id",
            "dataset",
            "group_id",
            "source_hash",
            "original_response_sha256",
            "profile",
            "prompt",
            "original_response",
            "cue_family",
            "length_direction",
            "draft_order",
        ):
            if not isinstance(row.get(field), str) or not row[field].strip():
                errors.append(f"writer_source_string_invalid:{position}:{field}")
        if isinstance(row.get("source_hash"), str) and not SHA256_RE.fullmatch(
            row["source_hash"]
        ):
            errors.append(f"writer_source_hash_invalid:{position}")
        response_digest = row.get("original_response_sha256")
        if isinstance(response_digest, str) and not SHA256_RE.fullmatch(response_digest):
            errors.append(f"writer_response_hash_invalid:{position}")
        elif isinstance(row.get("original_response"), str) and response_digest != hashlib.sha256(
            row["original_response"].encode("utf-8")
        ).hexdigest():
            errors.append(f"writer_response_hash_mismatch:{source_id}")
        if row.get("length_direction") not in {
            "confident_longer",
            "hesitant_longer",
        }:
            errors.append(f"writer_length_direction_invalid:{source_id}")
        if row.get("draft_order") not in {"confident_first", "hesitant_first"}:
            errors.append(f"writer_draft_order_invalid:{source_id}")
        order = row.get("generation_order")
        if isinstance(order, bool) or not isinstance(order, int) or order < 1:
            errors.append(f"writer_generation_order_invalid:{source_id}")
        spans = row.get("protected_spans")
        if not isinstance(spans, list) or any(
            not isinstance(span, str) or not span for span in spans
        ):
            errors.append(f"writer_protected_spans_invalid:{source_id}")
        elif isinstance(row.get("original_response"), str):
            for span in spans:
                if span not in row["original_response"]:
                    errors.append(f"writer_protected_span_not_in_source:{source_id}")
    for position, row in enumerate(candidate_rows, 1):
        forbidden = _forbidden_paths(row)
        errors.extend(
            f"forbidden_candidate_field:{position}:{path}" for path in forbidden
        )
        unknown = sorted(set(row) - CANDIDATE_ALLOWED_FIELDS)
        errors.extend(
            f"unknown_candidate_field:{position}:{field}" for field in unknown
        )
        if "issues" in row and row.get("issues") != []:
            errors.append(f"candidate_issues_not_empty:{position}")

    sources = _index_rows(source_rows, "sources", errors)
    candidates = _index_rows(candidate_rows, "candidates", errors)
    for source_id in target_ids:
        source = sources.get(source_id)
        candidate = candidates.get(source_id)
        if source is None:
            errors.append(f"target_source_missing:{source_id}")
            continue
        if candidate is None:
            errors.append(f"target_candidate_missing:{source_id}")
            continue
        for field in IDENTITY_FIELDS:
            if candidate.get(field) != source.get(field):
                errors.append(f"candidate_identity_mismatch:{source_id}:{field}")
        if "generation_order" in candidate and candidate.get("generation_order") != source.get(
            "generation_order"
        ):
            errors.append(f"candidate_identity_mismatch:{source_id}:generation_order")
        for arm in ("confident_response", "hesitant_response"):
            if not isinstance(candidate.get(arm), str) or not candidate[arm].strip():
                errors.append(f"candidate_arm_missing:{source_id}:{arm}")

    if errors:
        raise RepairPromptError(errors)
    ordered = sorted(
        (sources[source_id] for source_id in target_ids),
        key=lambda row: int(row["generation_order"]),
    )
    return ordered, candidates


def _validate_validator_report(
    payload: Any,
    sources: Sequence[Mapping[str, Any]],
    candidates: Mapping[str, Mapping[str, Any]],
    failure_codes: Sequence[str],
    repair_stage: str,
) -> dict[str, str]:
    """Validate and hash the target rows of a private mechanical report."""

    errors: list[str] = []
    if not isinstance(payload, dict):
        raise RepairPromptError(["validator_report_not_object"])
    if payload.get("schema_version") != VALIDATOR_SCHEMA_VERSION:
        errors.append("validator_report_schema_version_invalid")
    if payload.get("validator") != VALIDATOR_NAME:
        errors.append("validator_report_validator_invalid")
    rows = payload.get("rows")
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        errors.append("validator_report_rows_invalid")
        rows = []
    indexed = _index_rows(rows, "validator_report", errors)
    target_row_hashes: dict[str, str] = {}
    length_only_failure = "frozen_length_policy_violation" in failure_codes

    for source in sources:
        source_id = str(source["source_id"])
        candidate = candidates[source_id]
        row = indexed.get(source_id)
        if row is None:
            errors.append(f"target_validator_row_missing:{source_id}")
            continue
        target_row_hashes[source_id] = _sha256_json(row)
        for field in VALIDATOR_IDENTITY_FIELDS:
            if row.get(field) != source.get(field):
                errors.append(f"validator_identity_mismatch:{source_id}:{field}")
        for arm in ("confident", "hesitant"):
            row_hash = row.get(f"{arm}_response_sha256")
            expected_hash = _sha256_text(str(candidate[f"{arm}_response"]))
            if not isinstance(row_hash, str) or not SHA256_RE.fullmatch(row_hash):
                errors.append(f"validator_response_hash_invalid:{source_id}:{arm}")
            elif row_hash != expected_hash:
                errors.append(f"validator_response_hash_mismatch:{source_id}:{arm}")

        flags = row.get("failure_flags")
        if (
            not isinstance(flags, list)
            or not flags
            or any(not isinstance(flag, str) or not flag for flag in flags)
        ):
            errors.append(f"validator_target_failure_flags_invalid:{source_id}")
            flags = []
        elif len(flags) != len(set(flags)):
            errors.append(f"validator_target_failure_flags_duplicate:{source_id}")
        if row.get("validation_status") != "fail":
            errors.append(f"validator_target_not_failed:{source_id}:validation_status")
        if row.get("mechanical_gate_pass") is not False:
            errors.append(f"validator_target_not_failed:{source_id}:mechanical_gate_pass")

        if length_only_failure:
            non_length = sorted(set(flags) - FROZEN_LENGTH_FAILURE_FLAGS)
            if non_length:
                errors.append(
                    f"frozen_length_failure_has_non_length_flags:{source_id}:"
                    + ",".join(non_length)
                )

        if repair_stage == "final_length_only":
            if flags != ["pair_token_gap_over_limit"]:
                errors.append(f"final_length_only_failure_flags_invalid:{source_id}")
            counts = row.get("token_counts")
            if not isinstance(counts, dict):
                errors.append(f"final_length_only_token_counts_missing:{source_id}")
                continue
            source_tokens = counts.get("source")
            confident_tokens = counts.get("confident")
            hesitant_tokens = counts.get("hesitant")
            absolute_gap = counts.get("absolute_gap")
            allowed_gap = counts.get("allowed_gap")
            integer_counts = (source_tokens, confident_tokens, hesitant_tokens)
            if any(
                isinstance(value, bool)
                or not isinstance(value, int)
                or value <= 0
                for value in integer_counts
            ):
                errors.append(f"final_length_only_token_counts_invalid:{source_id}")
                continue
            expected_gap = abs(confident_tokens - hesitant_tokens)
            pair_mean = (confident_tokens + hesitant_tokens) / 2
            expected_allowed_gap = max(
                PAIR_GAP_MIN_ALLOWANCE, PAIR_GAP_MEAN_FRACTION * pair_mean
            )
            computed_direction = (
                source.get("length_direction") == "confident_longer"
                and confident_tokens > hesitant_tokens
            ) or (
                source.get("length_direction") == "hesitant_longer"
                and hesitant_tokens > confident_tokens
            )
            if counts.get("direction_correct") is not computed_direction:
                errors.append(
                    f"final_length_only_direction_metric_mismatch:{source_id}"
                )
            if not computed_direction:
                errors.append(f"final_length_only_direction_incorrect:{source_id}")
            if absolute_gap != expected_gap:
                errors.append(f"final_length_only_absolute_gap_mismatch:{source_id}")
            if (
                isinstance(allowed_gap, bool)
                or not isinstance(allowed_gap, (int, float))
                or not math.isfinite(float(allowed_gap))
                or abs(float(allowed_gap) - round(expected_allowed_gap, 6)) > 1e-9
            ):
                errors.append(f"final_length_only_allowed_gap_mismatch:{source_id}")
            confident_ratio = confident_tokens / source_tokens
            hesitant_ratio = hesitant_tokens / source_tokens
            pair_ratio = max(confident_tokens, hesitant_tokens) / min(
                confident_tokens, hesitant_tokens
            )
            if not (
                SOURCE_RATIO_MIN <= confident_ratio <= SOURCE_RATIO_MAX
                and SOURCE_RATIO_MIN <= hesitant_ratio <= SOURCE_RATIO_MAX
                and pair_ratio <= PAIR_RATIO_MAX
            ):
                errors.append(
                    f"final_length_only_other_length_constraint_failed:{source_id}"
                )
            if not isinstance(absolute_gap, int) or isinstance(absolute_gap, bool):
                errors.append(f"final_length_only_gap_metrics_invalid:{source_id}")
            else:
                excess = expected_gap - expected_allowed_gap
                if excess <= 0 or excess > 2.0:
                    errors.append(f"final_length_only_gap_excess_invalid:{source_id}")

    if errors:
        raise RepairPromptError(errors)
    return target_row_hashes


def _validate_budget_ledger(
    payload: Any,
    sources: Sequence[Mapping[str, Any]],
    candidates: Mapping[str, Mapping[str, Any]],
    repair_id: str,
    repair_stage: str,
) -> dict[str, str]:
    """Validate a per-repair private budget ledger and hash its target entries."""

    errors: list[str] = []
    if not isinstance(payload, dict):
        raise RepairPromptError(["repair_budget_ledger_not_object"])
    unknown = sorted(set(payload) - BUDGET_LEDGER_FIELDS)
    missing = sorted(BUDGET_LEDGER_FIELDS - set(payload))
    errors.extend(f"unknown_repair_budget_ledger_field:{field}" for field in unknown)
    errors.extend(f"missing_repair_budget_ledger_field:{field}" for field in missing)
    if payload.get("schema_version") != BUDGET_LEDGER_SCHEMA_VERSION:
        errors.append("repair_budget_ledger_schema_version_invalid")
    if payload.get("repair_id") != repair_id:
        errors.append("repair_budget_ledger_repair_id_mismatch")
    if payload.get("repair_stage") != repair_stage:
        errors.append("repair_budget_ledger_repair_stage_mismatch")
    entries = payload.get("entries")
    if not isinstance(entries, list) or not entries or any(
        not isinstance(entry, dict) for entry in entries
    ):
        errors.append("repair_budget_ledger_entries_invalid")
        entries = []
    for position, entry in enumerate(entries, 1):
        unknown_entry = sorted(set(entry) - BUDGET_ENTRY_FIELDS)
        missing_entry = sorted(BUDGET_ENTRY_FIELDS - set(entry))
        errors.extend(
            f"unknown_repair_budget_entry_field:{position}:{field}"
            for field in unknown_entry
        )
        errors.extend(
            f"missing_repair_budget_entry_field:{position}:{field}"
            for field in missing_entry
        )
    indexed = _index_rows(entries, "repair_budget_ledger", errors)
    target_ids = {str(source["source_id"]) for source in sources}
    if set(indexed) != target_ids:
        errors.append("repair_budget_ledger_target_set_mismatch")
    expected_count = 0 if repair_stage == "first_full_pair" else 1
    target_entry_hashes: dict[str, str] = {}
    for source in sources:
        source_id = str(source["source_id"])
        candidate = candidates[source_id]
        entry = indexed.get(source_id)
        if entry is None:
            continue
        target_entry_hashes[source_id] = _sha256_json(entry)
        for field in ("source_hash", "original_response_sha256"):
            value = entry.get(field)
            if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
                errors.append(f"repair_budget_hash_invalid:{source_id}:{field}")
            elif value != source.get(field):
                errors.append(f"repair_budget_identity_mismatch:{source_id}:{field}")
        for arm in ("confident", "hesitant"):
            field = f"{arm}_response_sha256"
            value = entry.get(field)
            expected = _sha256_text(str(candidate[f"{arm}_response"]))
            if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
                errors.append(f"repair_budget_hash_invalid:{source_id}:{field}")
            elif value != expected:
                errors.append(f"repair_budget_candidate_hash_mismatch:{source_id}:{arm}")
        count = entry.get("counted_repairs")
        if isinstance(count, bool) or not isinstance(count, int) or count < 0:
            errors.append(f"repair_budget_count_invalid:{source_id}")
        elif count != expected_count:
            errors.append(
                f"repair_budget_count_mismatch:{source_id}:{repair_stage}:"
                f"expected_{expected_count}:actual_{count}"
            )
    if errors:
        raise RepairPromptError(errors)
    return target_entry_hashes


def _output_pair_template(source: Mapping[str, Any]) -> dict[str, Any]:
    fixed = {
        "source_id": source["source_id"],
        "source_hash": source["source_hash"],
        "original_response_sha256": source["original_response_sha256"],
        "dataset": source["dataset"],
        "cue_family": source["cue_family"],
        "length_direction": source["length_direction"],
        "draft_order": source["draft_order"],
    }
    if source["draft_order"] == "hesitant_first":
        fixed["hesitant_response"] = "..."
        fixed["confident_response"] = "..."
    elif source["draft_order"] == "confident_first":
        fixed["confident_response"] = "..."
        fixed["hesitant_response"] = "..."
    else:
        raise RepairPromptError(
            [f"source_draft_order_invalid:{source['source_id']}"]
        )
    fixed["issues"] = []
    return fixed


def build_prompt(
    sources: Sequence[Mapping[str, Any]],
    failure_codes: Sequence[str],
) -> str:
    reasons = [FAILURE_REASON_TEXT[code] for code in failure_codes]
    payload = []
    for source in sources:
        record = {field: source[field] for field in SOURCE_FIELDS}
        record["repair_constraints"] = {
            "failure_codes": list(failure_codes),
            "generic_reasons": reasons,
            "banned_surface_forms_case_insensitive": [],
        }
        payload.append(record)
    output_schema = {"pairs": [_output_pair_template(source) for source in sources]}
    return f"""FACTUAL DIRECT-PAIR REWRITE CANARY: WRITER-SAFE REPAIR.

Generate a fresh confident/hesitant pair for every supplied frozen source. The earlier candidate text is deliberately not shown. Work only from each original_response and the generic, nonsemantic repair constraints below.

NON-NEGOTIABLE RULES

1. Rewrite both complete responses. Do not copy the source verbatim, make a local patch, or use a shared body plus a detachable certainty sentence.
2. Preserve exactly the same object-level content in both arms: every claim, conclusion, entity, name, number, date, unit, list item, condition, exception, negation, comparison, causal or logical relation, and source-level modal. The original_response is the sole content authority. Do not correct, update, infer, add, omit, strengthen, or weaken facts.
3. Change only the speaker's commitment to the preserved answer. The confident arm must sound clearly settled. The hesitant arm must remain responsive and informative while sounding clearly provisional. Do not add alternative answers, refusals, missing-evidence claims, or invented reasons for doubt.
4. Follow the assigned cue_family and integrate the contrast into substantive grammar and discourse. Do not add a generic certainty label or detachable self-report. Use source-specific syntax and do not replace a banned form with one new stock phrase shared across records.
5. Every protected_span is an exact source substring and must occur verbatim in both arms. No reviewer-only semantic descriptors or content checklists are provided; do not infer any.
6. Treat banned_surface_forms_case_insensitive as surface-form exclusions only. Preserve all underlying source content. None of those forms may appear in either new arm, regardless of capitalization.
7. Match formatting, detail, helpfulness, structure, and answer quality within each pair. Keep each arm between 0.85 and 1.15 times the source-token length, the longer/shorter ratio at most 1.08, and the absolute pair gap no more than max(5 tokens, 5% of the pair mean). Respect length_direction and never delete or repeat content to force length.
8. Respect draft_order in the serialized field order. Echo all fixed identity and assignment fields exactly. Preserve the supplied record order. If a faithful pair is genuinely impossible, return empty response strings and a concise issue; otherwise issues must be [].

Return ONLY one valid JSON object matching OUTPUT_SCHEMA_JSON exactly. Do not return Markdown, commentary, rationale, scores, evidence claims, extra keys, or omitted records.

OUTPUT_SCHEMA_JSON
{json.dumps(output_schema, ensure_ascii=False, separators=(",", ":"))}

INPUT_RECORDS_JSON
{json.dumps(payload, ensure_ascii=False, separators=(",", ":"))}
"""


def _json_bytes(payload: Mapping[str, Any]) -> bytes:
    return (
        json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    ).encode("utf-8")


def _stage_bytes(path: Path, payload: bytes) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
    except BaseException:
        temporary_path.unlink(missing_ok=True)
        raise
    return temporary_path


def _commit(staged_targets: Sequence[tuple[Path, Path]], overwrite: bool) -> None:
    backups: dict[Path, Path] = {}
    committed: list[Path] = []
    try:
        for _, target in staged_targets:
            if not target.exists():
                continue
            if not overwrite:
                raise FileExistsError(f"refusing to overwrite {target}")
            descriptor, backup_name = tempfile.mkstemp(
                prefix=f".{target.name}.", suffix=".rollback", dir=target.parent
            )
            os.close(descriptor)
            backup = Path(backup_name)
            backup.unlink()
            os.replace(target, backup)
            backups[target] = backup
        for staged, target in staged_targets:
            os.replace(staged, target)
            committed.append(target)
    except BaseException as error:
        for target in reversed(committed):
            target.unlink(missing_ok=True)
        for target, backup in reversed(tuple(backups.items())):
            if backup.exists():
                os.replace(backup, target)
        raise error
    else:
        for backup in backups.values():
            try:
                backup.unlink(missing_ok=True)
            except OSError:
                # Both target replacements have committed. A stale hidden backup is
                # preferable to reporting failure after the transaction succeeded.
                pass


def _require_private_output(path: Path, private_root: Path) -> Path:
    resolved = path.resolve()
    root = private_root.resolve()
    if resolved != root and root not in resolved.parents:
        raise RepairPromptError([f"output_outside_private_data:{resolved}"])
    return resolved


def _require_private_input(path: Path, private_root: Path, label: str) -> Path:
    resolved = path.resolve()
    root = private_root.resolve()
    if resolved != root and root not in resolved.parents:
        raise RepairPromptError(
            [f"private_input_outside_private_data:{label}:{resolved}"]
        )
    return resolved


def build_repair_prompt_artifacts(
    sources_path: Path | str,
    candidate_paths: Sequence[Path | str],
    spec_path: Path | str,
    validator_report_path: Path | str,
    repair_budget_ledger_path: Path | str,
    prompt_output_path: Path | str,
    manifest_output_path: Path | str,
    *,
    private_root: Path | str = DEFAULT_PRIVATE_ROOT,
    overwrite: bool = False,
) -> dict[str, Any]:
    sources_path = Path(sources_path)
    candidate_paths = [Path(path) for path in candidate_paths]
    spec_path = Path(spec_path)
    validator_report_path = Path(validator_report_path)
    repair_budget_ledger_path = Path(repair_budget_ledger_path)
    prompt_output_path = Path(prompt_output_path)
    manifest_output_path = Path(manifest_output_path)
    private_root = Path(private_root)

    errors: list[str] = []
    if not candidate_paths:
        errors.append("candidate_inputs_empty")
    if len({path.resolve() for path in candidate_paths}) != len(candidate_paths):
        errors.append("candidate_input_duplicate")
    inputs = {
        sources_path.resolve(),
        spec_path.resolve(),
        validator_report_path.resolve(),
        repair_budget_ledger_path.resolve(),
        *(path.resolve() for path in candidate_paths),
    }
    outputs = {prompt_output_path.resolve(), manifest_output_path.resolve()}
    if len(outputs) != 2:
        errors.append("prompt_and_manifest_outputs_match")
    if inputs & outputs:
        errors.append("output_overwrites_input")
    if not overwrite:
        for output in (prompt_output_path, manifest_output_path):
            if output.exists():
                errors.append(f"output_exists:{output}")
    if errors:
        raise RepairPromptError(errors)
    _require_private_output(prompt_output_path, private_root)
    _require_private_output(manifest_output_path, private_root)
    _require_private_input(validator_report_path, private_root, "validator_report")
    _require_private_input(
        repair_budget_ledger_path, private_root, "repair_budget_ledger"
    )

    source_bytes = _read_bytes(sources_path)
    candidate_bytes = [_read_bytes(path) for path in candidate_paths]
    spec_bytes = _read_bytes(spec_path)
    validator_report_bytes = _read_bytes(validator_report_path)
    repair_budget_ledger_bytes = _read_bytes(repair_budget_ledger_path)

    source_rows = _read_records_bytes(sources_path, source_bytes)
    candidate_rows = [
        row
        for path, payload in zip(candidate_paths, candidate_bytes)
        for row in _read_records_bytes(path, payload)
    ]
    spec_payload = _load_json_bytes(spec_path, spec_bytes)
    validator_report_payload = _load_json_bytes(
        validator_report_path, validator_report_bytes
    )
    repair_budget_ledger_payload = _load_json_bytes(
        repair_budget_ledger_path, repair_budget_ledger_bytes
    )
    repair_id, repair_stage, target_ids, failure_codes = _validate_spec(spec_payload)
    ordered_sources, candidates = _validate_inputs(
        source_rows, candidate_rows, target_ids
    )
    target_validator_row_hashes = _validate_validator_report(
        validator_report_payload,
        ordered_sources,
        candidates,
        failure_codes,
        repair_stage,
    )
    target_budget_entry_hashes = _validate_budget_ledger(
        repair_budget_ledger_payload,
        ordered_sources,
        candidates,
        repair_id,
        repair_stage,
    )
    prompt = build_prompt(ordered_sources, failure_codes)
    prompt_bytes = prompt.encode("utf-8")

    candidate_pair_hashes = {
        source_id: _sha256_bytes(
            json.dumps(
                {
                    key: candidates[source_id].get(key)
                    for key in sorted(CANDIDATE_ALLOWED_FIELDS)
                    if key in candidates[source_id]
                },
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        )
        for source_id in target_ids
    }
    manifest = {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "repair_id": repair_id,
        "repair_stage": repair_stage,
        "target_source_ids": [row["source_id"] for row in ordered_sources],
        "target_count": len(ordered_sources),
        "failure_codes": failure_codes,
        "inputs": {
            "writer_sources": {
                "path": str(sources_path),
                "sha256": _sha256_bytes(source_bytes),
            },
            "candidate_pairs": [
                {"path": str(path), "sha256": _sha256_bytes(payload)}
                for path, payload in zip(candidate_paths, candidate_bytes)
            ],
            "repair_spec": {
                "path": str(spec_path),
                "sha256": _sha256_bytes(spec_bytes),
            },
            "validator_report": {
                "path": str(validator_report_path),
                "sha256": _sha256_bytes(validator_report_bytes),
            },
            "repair_budget_ledger": {
                "path": str(repair_budget_ledger_path),
                "sha256": _sha256_bytes(repair_budget_ledger_bytes),
            },
            "target_candidate_pair_sha256": candidate_pair_hashes,
            "target_validator_row_sha256": target_validator_row_hashes,
            "target_repair_budget_entry_sha256": target_budget_entry_hashes,
        },
        "output": {
            "path": str(prompt_output_path),
            "sha256": _sha256_bytes(prompt_bytes),
        },
        "writer_safety": {
            "writer_source_field_allowlist_enforced": True,
            "candidate_field_allowlist_enforced": True,
            "repair_spec_field_allowlist_enforced": True,
            "reviewer_only_fields_rejected": True,
            "freeform_repair_instructions_allowed": False,
            "prior_candidate_arms_exposed_in_prompt": False,
            "candidate_response_text_used_for_integrity_checks_only": True,
            "nonempty_surface_form_bans_allowed": False,
            "validator_report_required_private_and_bound": True,
            "repair_budget_ledger_required_private_and_bound": True,
        },
    }
    manifest_bytes = _json_bytes(manifest)

    staged: list[Path] = []
    try:
        staged_prompt = _stage_bytes(prompt_output_path, prompt_bytes)
        staged.append(staged_prompt)
        staged_manifest = _stage_bytes(manifest_output_path, manifest_bytes)
        staged.append(staged_manifest)
        _commit(
            (
                (staged_prompt, prompt_output_path),
                (staged_manifest, manifest_output_path),
            ),
            overwrite,
        )
    except BaseException:
        for path in staged:
            path.unlink(missing_ok=True)
        raise
    return manifest


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, required=True)
    parser.add_argument("--candidates", type=Path, action="append", required=True)
    parser.add_argument("--repair-spec", type=Path, required=True)
    parser.add_argument("--validator-report", type=Path, required=True)
    parser.add_argument("--repair-budget-ledger", type=Path, required=True)
    parser.add_argument("--prompt-output", type=Path, required=True)
    parser.add_argument("--manifest-output", type=Path, required=True)
    parser.add_argument("--private-root", type=Path, default=DEFAULT_PRIVATE_ROOT)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    manifest = build_repair_prompt_artifacts(
        args.sources,
        args.candidates,
        args.repair_spec,
        args.validator_report,
        args.repair_budget_ledger,
        args.prompt_output,
        args.manifest_output,
        private_root=args.private_root,
        overwrite=args.overwrite,
    )
    print(json.dumps(manifest, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
