"""Canonical text-free bindings for one frozen factual-rewrite pair set."""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Mapping, Sequence


BINDING_SCHEMA = "factual-rewrite-artifact-binding-v1"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
IDENTITY_FIELDS = (
    "source_id",
    "source_hash",
    "original_response_sha256",
    "dataset",
    "cue_family",
    "length_direction",
    "draft_order",
    "generation_order",
)
PAIR_IDENTITY_FIELDS = tuple(
    field for field in IDENTITY_FIELDS if field != "generation_order"
)


def _canonical_sha256(value: Any) -> str:
    payload = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _text_sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _unique_rows(rows: Sequence[Mapping[str, Any]], label: str) -> list[Mapping[str, Any]]:
    ordered: list[Mapping[str, Any]] = []
    seen: set[str] = set()
    for row in rows:
        source_id = row.get("source_id")
        if not isinstance(source_id, str) or not source_id:
            raise ValueError(f"{label}: every row requires source_id")
        if source_id in seen:
            raise ValueError(f"{label}: duplicate source_id")
        seen.add(source_id)
        ordered.append(row)
    return sorted(ordered, key=lambda row: str(row["source_id"]))


def source_ids_sha256(source_ids: Sequence[str]) -> str:
    if any(not isinstance(value, str) or not value for value in source_ids):
        raise ValueError("source IDs must be nonempty strings")
    if len(source_ids) != len(set(source_ids)):
        raise ValueError("source IDs must be unique")
    return _canonical_sha256(sorted(source_ids))


def build_artifact_binding(
    source_rows: Sequence[Mapping[str, Any]],
    pair_rows: Sequence[Mapping[str, Any]],
    *,
    require_matching_ids: bool = True,
) -> dict[str, Any]:
    """Hash identities and rewrite text without returning either."""
    sources = _unique_rows(source_rows, "sources")
    pairs = _unique_rows(pair_rows, "pairs")
    if require_matching_ids and {str(row["source_id"]) for row in sources} != {
        str(row["source_id"]) for row in pairs
    }:
        raise ValueError("source and pair ID sets do not match")

    # Bind the full frozen source record, including prompt text, the actual
    # original response, protected constraints, and allocation metadata. The
    # review builder joins pair text onto source rows, so only pair-only fields
    # are excluded. Public artifacts receive only the resulting digest.
    pair_only_fields = {
        "confident_response",
        "hesitant_response",
        "hedged_response",
        "issues",
    }
    source_projection = [
        {
            key: value
            for key, value in row.items()
            if key not in pair_only_fields
        }
        for row in sources
    ]
    pair_projection: list[dict[str, Any]] = []
    for row in pairs:
        confident = row.get("confident_response")
        hesitant = row.get("hesitant_response", row.get("hedged_response"))
        if not isinstance(confident, str) or not confident:
            raise ValueError("pairs: every row requires confident_response")
        if not isinstance(hesitant, str) or not hesitant:
            raise ValueError("pairs: every row requires hesitant_response")
        item = {field: row.get(field) for field in PAIR_IDENTITY_FIELDS}
        item["confident_response_sha256"] = _text_sha256(confident)
        item["hesitant_response_sha256"] = _text_sha256(hesitant)
        pair_projection.append(item)

    ids = [str(row["source_id"]) for row in sources]
    return {
        "schema": BINDING_SCHEMA,
        "source_count": len(sources),
        "pair_count": len(pairs),
        "source_ids_sha256": source_ids_sha256(ids),
        "source_set_sha256": _canonical_sha256(source_projection),
        "pair_set_sha256": _canonical_sha256(pair_projection),
    }


def validate_artifact_binding(value: Any) -> dict[str, Any]:
    if not isinstance(value, Mapping) or value.get("schema") != BINDING_SCHEMA:
        raise ValueError("missing or invalid artifact binding")
    result = {"schema": BINDING_SCHEMA}
    for field in ("source_count", "pair_count"):
        item = value.get(field)
        if not isinstance(item, int) or isinstance(item, bool) or item < 0:
            raise ValueError(f"artifact binding {field} must be a non-negative integer")
        result[field] = item
    for field in ("source_ids_sha256", "source_set_sha256", "pair_set_sha256"):
        item = value.get(field)
        if not isinstance(item, str) or not SHA256_RE.fullmatch(item):
            raise ValueError(f"artifact binding {field} must be a SHA-256 digest")
        result[field] = item
    return result
