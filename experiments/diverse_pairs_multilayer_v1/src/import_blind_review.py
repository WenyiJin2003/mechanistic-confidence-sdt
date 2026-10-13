"""Validate and import the generic five-field blind human-review export.

The reviewer-facing page deliberately omits the intended confidence labels. This
importer joins an export to the separately stored answer key only after checking
the packet hash, row hashes, and exact review-ID set. Reviewer choices never
create or modify labels: labels come exclusively from ``UNBLIND_KEY.json``.

Text-bearing and identity-bearing outputs are restricted to ``private_data``.
The separate aggregate contains only packet-level metadata and counts, so it is
safe to inspect without exposing source IDs, prompts, responses, or comments.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any


BASE = Path(__file__).resolve().parents[1]
PRIVATE = BASE / "private_data"

REVIEW_FIELDS = (
    "content_equivalence",
    "certainty_contrast",
    "naturalness",
    "cue_scope",
    "decision",
)
ENUMS = {
    "content_equivalence": {
        "",
        "both_match",
        "a_changes",
        "b_changes",
        "both_change",
        "uncertain",
    },
    "certainty_contrast": {
        "",
        "a_more_certain",
        "b_more_certain",
        "no_clear_contrast",
        "uncertain",
    },
    "naturalness": {
        "",
        "both_natural",
        "a_unnatural",
        "b_unnatural",
        "both_unnatural",
        "uncertain",
    },
    "cue_scope": {
        "",
        "both_global",
        "a_local_only",
        "b_local_only",
        "both_local_only",
        "uncertain",
    },
    "decision": {"", "accept", "reject", "discuss"},
}
TOP_LEVEL_KEYS = {"packet_sha256", "reviewed_at", "blinded", "reviews"}
REVIEW_KEYS = {"review_id", *REVIEW_FIELDS, "comment", "updated_at"}
KEY_FIELDS = {
    "review_id",
    "source_id",
    "cohort",
    "version_a_label",
    "version_b_label",
    "source_response_sha256",
    "version_a_sha256",
    "version_b_sha256",
}


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_text(value: str) -> str:
    return sha256_bytes(value.encode("utf-8"))


def _is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _is_timestamp(value: Any) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    candidate = value.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError:
        return False
    return parsed.tzinfo is not None


def _load_object(path: Path, name: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Cannot read valid {name} JSON: {path}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"{name} must be a JSON object")
    return payload


def _load_jsonl(path: Path, name: str) -> list[dict[str, Any]]:
    rows = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
        for line_number, line in enumerate(lines, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ValueError(f"{name} line {line_number} must be an object")
            rows.append(row)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Cannot read valid {name} JSONL: {path}") from exc
    return rows


def _require_private_path(path: Path, base: Path) -> Path:
    resolved = path.resolve()
    private = (base / "private_data").resolve()
    try:
        resolved.relative_to(private)
    except ValueError as exc:
        raise ValueError("Private review artifacts must stay under private_data") from exc
    return resolved


def _validate_packet(
    packet_dir: Path,
) -> tuple[str, list[str], dict[str, dict[str, Any]], dict[str, Any]]:
    manifest_path = packet_dir / "MANIFEST.json"
    key_path = packet_dir / "UNBLIND_KEY.json"
    rows_path = packet_dir / "BLINDED_ROWS.jsonl"
    manifest = _load_object(manifest_path, "packet manifest")
    key = _load_object(key_path, "unblind key")
    rows = _load_jsonl(rows_path, "blinded rows")

    packet_hash = manifest.get("packet_sha256")
    if not _is_sha256(packet_hash):
        raise ValueError("Manifest packet_sha256 is missing or invalid")
    if key.get("packet_sha256") != packet_hash:
        raise ValueError("UNBLIND_KEY packet hash is stale or mismatched")
    key_file_hash = manifest.get("unblind_key_sha256")
    if not _is_sha256(key_file_hash):
        raise ValueError("Manifest unblind_key_sha256 is missing or invalid")
    if sha256_bytes(key_path.read_bytes()) != key_file_hash:
        raise ValueError("UNBLIND_KEY file hash is stale or mismatched")
    if sha256_bytes(rows_path.read_bytes()) != packet_hash:
        raise ValueError("BLINDED_ROWS packet hash is stale or mismatched")
    if manifest.get("blinded") is not True:
        raise ValueError("Manifest must identify a blinded packet")
    if manifest.get("review_dimensions") != list(REVIEW_FIELDS):
        raise ValueError("Manifest review dimensions do not match the five-field schema")

    key_rows = key.get("pairs")
    if not isinstance(key_rows, list) or not key_rows:
        raise ValueError("UNBLIND_KEY must contain a nonempty pairs list")
    if manifest.get("pairs") != len(key_rows) or len(rows) != len(key_rows):
        raise ValueError("Manifest, unblind key, and blinded-row counts disagree")

    expected_ids: list[str] = []
    key_by_id: dict[str, dict[str, Any]] = {}
    for index, entry in enumerate(key_rows):
        if not isinstance(entry, dict) or not KEY_FIELDS.issubset(entry):
            raise ValueError(f"Unblind key entry {index} is incomplete")
        review_id = entry.get("review_id")
        if not isinstance(review_id, str) or not review_id:
            raise ValueError(f"Unblind key entry {index} has an invalid review_id")
        if review_id in key_by_id:
            raise ValueError(f"Duplicate review_id in unblind key: {review_id}")
        if not isinstance(entry.get("source_id"), str) or not entry["source_id"]:
            raise ValueError(f"Unblind key entry {review_id} has an invalid source_id")
        if not isinstance(entry.get("cohort"), str) or not entry["cohort"]:
            raise ValueError(f"Unblind key entry {review_id} has an invalid cohort")
        if {entry.get("version_a_label"), entry.get("version_b_label")} != {
            "confident",
            "hedged",
        }:
            raise ValueError(f"Unblind key labels are invalid for {review_id}")
        for hash_field in (
            "source_response_sha256",
            "version_a_sha256",
            "version_b_sha256",
        ):
            if not _is_sha256(entry.get(hash_field)):
                raise ValueError(f"Invalid {hash_field} for {review_id}")
        expected_ids.append(review_id)
        key_by_id[review_id] = entry

    row_by_id: dict[str, dict[str, Any]] = {}
    for index, row in enumerate(rows):
        review_id = row.get("review_id")
        if not isinstance(review_id, str) or not review_id:
            raise ValueError(f"Blinded row {index} has an invalid review_id")
        if review_id in row_by_id:
            raise ValueError(f"Duplicate review_id in blinded rows: {review_id}")
        for field in ("source_response", "version_a", "version_b"):
            if not isinstance(row.get(field), str):
                raise ValueError(f"Blinded row {review_id} is missing {field}")
        row_by_id[review_id] = row

    if set(row_by_id) != set(expected_ids):
        raise ValueError("Blinded-row review IDs do not match the unblind key")
    for review_id in expected_ids:
        row = row_by_id[review_id]
        entry = key_by_id[review_id]
        checks = {
            "source_response_sha256": sha256_text(row["source_response"]),
            "version_a_sha256": sha256_text(row["version_a"]),
            "version_b_sha256": sha256_text(row["version_b"]),
        }
        for field, actual in checks.items():
            if entry[field] != actual:
                raise ValueError(f"Stale {field} for {review_id}")
    return packet_hash, expected_ids, key_by_id, manifest


def _normalize_review(entry: dict[str, Any]) -> dict[str, Any]:
    unknown = set(entry) - REVIEW_KEYS
    if unknown:
        raise ValueError(
            f"Unknown fields for review {entry.get('review_id')}: {sorted(unknown)}"
        )
    normalized: dict[str, Any] = {}
    for field in REVIEW_FIELDS:
        value = entry.get(field, "")
        if not isinstance(value, str) or value not in ENUMS[field]:
            raise ValueError(f"Invalid {field} value for {entry.get('review_id')}")
        normalized[field] = value
    comment = entry.get("comment", "")
    if not isinstance(comment, str):
        raise ValueError(f"Comment must be text for {entry.get('review_id')}")
    normalized["comment"] = comment
    if "updated_at" in entry:
        if not _is_timestamp(entry["updated_at"]):
            raise ValueError(f"updated_at must be a timezone-aware ISO timestamp for {entry.get('review_id')}")
        normalized["updated_at"] = entry["updated_at"]
    return normalized


def validate_and_decode(
    packet_dir: Path, review_export: Path, *, base: Path = BASE
) -> tuple[dict[str, Any], dict[str, Any], bytes]:
    """Return private decoded data, a text-free aggregate, and raw export bytes."""
    packet_dir = _require_private_path(packet_dir, base)
    packet_hash, expected_ids, key_by_id, _manifest = _validate_packet(packet_dir)
    raw_export = review_export.read_bytes()
    export = _load_object(review_export, "review export")
    unknown_top = set(export) - TOP_LEVEL_KEYS
    if unknown_top:
        raise ValueError(f"Unknown top-level review-export fields: {sorted(unknown_top)}")
    if export.get("packet_sha256") != packet_hash:
        raise ValueError("Review export packet hash is stale or mismatched")
    if export.get("blinded") is not True:
        raise ValueError("Review export must retain blinded=true")
    if not _is_timestamp(export.get("reviewed_at")):
        raise ValueError("Review export reviewed_at must be a timezone-aware ISO timestamp")
    entries = export.get("reviews")
    if not isinstance(entries, list):
        raise ValueError("Review export reviews must be a list")

    normalized_by_id: dict[str, dict[str, Any]] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("Every review must be an object")
        review_id = entry.get("review_id")
        if not isinstance(review_id, str) or not review_id:
            raise ValueError("Every review must have a nonempty review_id")
        if review_id in normalized_by_id:
            raise ValueError(f"Duplicate review_id in export: {review_id}")
        normalized_by_id[review_id] = _normalize_review(entry)

    expected_set = set(expected_ids)
    actual_set = set(normalized_by_id)
    if actual_set != expected_set:
        missing = sorted(expected_set - actual_set)
        extra = sorted(actual_set - expected_set)
        raise ValueError(f"Review IDs do not match packet; missing={missing}, extra={extra}")

    decoded_records = []
    field_counts = {field: Counter() for field in REVIEW_FIELDS}
    alignment_counts: Counter[str] = Counter()
    complete_count = 0
    for review_id in expected_ids:
        review = normalized_by_id[review_id]
        key_entry = key_by_id[review_id]
        complete = all(review[field] != "" for field in REVIEW_FIELDS)
        complete_count += int(complete)
        for field in REVIEW_FIELDS:
            field_counts[field][review[field] or "missing"] += 1

        intended_choice = (
            "a_more_certain"
            if key_entry["version_a_label"] == "confident"
            else "b_more_certain"
        )
        observed_choice = review["certainty_contrast"]
        if not observed_choice:
            alignment = "missing"
        elif observed_choice == intended_choice:
            alignment = "matches_key"
        elif observed_choice in {"a_more_certain", "b_more_certain"}:
            alignment = "contradicts_key"
        else:
            alignment = observed_choice
        alignment_counts[alignment] += 1

        decoded_records.append(
            {
                "review_id": review_id,
                "source_id": key_entry["source_id"],
                "cohort": key_entry["cohort"],
                "answer_key": {
                    "version_a_label": key_entry["version_a_label"],
                    "version_b_label": key_entry["version_b_label"],
                    "source_response_sha256": key_entry["source_response_sha256"],
                    "version_a_sha256": key_entry["version_a_sha256"],
                    "version_b_sha256": key_entry["version_b_sha256"],
                },
                "review": review,
                "all_five_fields_complete": complete,
                "intended_certainty_choice_from_key": intended_choice,
                "certainty_alignment_with_key": alignment,
            }
        )

    total = len(expected_ids)
    decoded = {
        "schema_version": 1,
        "packet_sha256": packet_hash,
        "reviewed_at": export["reviewed_at"],
        "blinded_review": True,
        "label_provenance": (
            "Confidence labels come only from UNBLIND_KEY.json; reviewer choices "
            "never create or modify labels."
        ),
        "records": decoded_records,
    }
    aggregate = {
        "schema_version": 1,
        "packet_sha256": packet_hash,
        "pairs": total,
        "complete_pairs": complete_count,
        "incomplete_pairs": total - complete_count,
        "gate_completed": complete_count == total,
        "counts": {
            field: dict(sorted(counter.items()))
            for field, counter in field_counts.items()
        },
        "certainty_alignment_counts": dict(sorted(alignment_counts.items())),
    }
    return decoded, aggregate, raw_export


def _atomic_new_bytes(path: Path, content: bytes) -> None:
    path = path.resolve()
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite existing file: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temp_name, path)
    finally:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass


def _json_bytes(payload: dict[str, Any]) -> bytes:
    return (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def import_review(
    packet_dir: Path,
    review_export: Path,
    private_output_dir: Path,
    aggregate_output: Path,
    *,
    base: Path = BASE,
) -> dict[str, Any]:
    private_output_dir = _require_private_path(private_output_dir, base)
    aggregate_output = aggregate_output.resolve()
    decoded, aggregate, raw_export = validate_and_decode(
        packet_dir, review_export, base=base
    )
    raw_path = private_output_dir / "RAW_REVIEW_EXPORT.json"
    decoded_path = private_output_dir / "DECODED_REVIEW.json"
    manifest_path = private_output_dir / "IMPORT_MANIFEST.json"
    protected = {
        packet_dir.resolve() / "MANIFEST.json",
        packet_dir.resolve() / "UNBLIND_KEY.json",
        packet_dir.resolve() / "BLINDED_ROWS.jsonl",
        review_export.resolve(),
    }
    destinations = {raw_path.resolve(), decoded_path.resolve(), manifest_path.resolve(), aggregate_output}
    if len(destinations) != 4 or destinations & protected:
        raise ValueError("Import outputs must be distinct from packet and export inputs")
    for path in destinations:
        if path.exists():
            raise FileExistsError(f"Refusing to overwrite existing file: {path}")

    decoded_bytes = _json_bytes(decoded)
    aggregate_bytes = _json_bytes(aggregate)
    import_manifest = {
        "schema_version": 1,
        "packet_sha256": aggregate["packet_sha256"],
        "raw_export_sha256": sha256_bytes(raw_export),
        "decoded_review_sha256": sha256_bytes(decoded_bytes),
        "aggregate_sha256": sha256_bytes(aggregate_bytes),
        "private_files": [raw_path.name, decoded_path.name],
        "aggregate_file": str(aggregate_output),
    }
    _atomic_new_bytes(raw_path, raw_export)
    _atomic_new_bytes(decoded_path, decoded_bytes)
    _atomic_new_bytes(aggregate_output, aggregate_bytes)
    _atomic_new_bytes(manifest_path, _json_bytes(import_manifest))
    return aggregate


def _resolve(base: Path, path: Path) -> Path:
    return path if path.is_absolute() else base / path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet-dir", required=True, type=Path)
    parser.add_argument("--reviews", required=True, type=Path)
    parser.add_argument("--private-output-dir", required=True, type=Path)
    parser.add_argument("--aggregate-output", required=True, type=Path)
    args = parser.parse_args(argv)
    aggregate = import_review(
        _resolve(BASE, args.packet_dir),
        _resolve(BASE, args.reviews),
        _resolve(BASE, args.private_output_dir),
        _resolve(BASE, args.aggregate_output),
    )
    print(json.dumps(aggregate, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
