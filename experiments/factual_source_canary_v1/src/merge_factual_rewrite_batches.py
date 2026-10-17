#!/usr/bin/env python3
"""Merge explicitly named factual-rewrite batches against a frozen manifest.

The merger is deliberately narrow: it performs identity and coverage checks, orders
rows by the authoritative source ``generation_order``, and writes deterministic
JSONL plus a hash-only provenance sidecar.  It does not replace the mechanical or
human-review gates.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Iterable, Sequence


IDENTITY_FIELDS = (
    "source_hash",
    "original_response_sha256",
    "dataset",
    "cue_family",
    "length_direction",
    "draft_order",
)


class MergeValidationError(ValueError):
    """Raised before any output is written when batch identity is invalid."""

    def __init__(self, errors: Sequence[str]):
        self.errors = tuple(errors)
        super().__init__("rewrite merge validation failed: " + "; ".join(self.errors))


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_json_rows(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        raise MergeValidationError([f"input_not_found:{path}"])

    try:
        if path.suffix.lower() == ".jsonl":
            rows: list[Any] = []
            with path.open("r", encoding="utf-8") as handle:
                for line_number, line in enumerate(handle, start=1):
                    if not line.strip():
                        continue
                    try:
                        rows.append(json.loads(line))
                    except json.JSONDecodeError as error:
                        raise MergeValidationError(
                            [f"invalid_json:{path}:{line_number}:{error.msg}"]
                        ) from error
        else:
            with path.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
            if isinstance(payload, list):
                rows = payload
            elif isinstance(payload, dict) and isinstance(payload.get("rows"), list):
                rows = payload["rows"]
            else:
                raise MergeValidationError([f"json_rows_not_found:{path}"])
    except OSError as error:
        raise MergeValidationError([f"input_read_failed:{path}:{error}"]) from error
    except json.JSONDecodeError as error:
        raise MergeValidationError([f"invalid_json:{path}:{error.msg}"]) from error

    bad_indices = [str(index) for index, row in enumerate(rows, start=1) if not isinstance(row, dict)]
    if bad_indices:
        raise MergeValidationError(
            [f"row_not_object:{path}:{','.join(bad_indices)}"]
        )
    return rows


def _jsonl_bytes(rows: Iterable[dict[str, Any]]) -> bytes:
    lines = [
        json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        for row in rows
    ]
    return (("\n".join(lines) + "\n") if lines else "").encode("utf-8")


def _json_bytes(payload: dict[str, Any]) -> bytes:
    return (json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode(
        "utf-8"
    )


def _validate_paths(
    sources_path: Path,
    input_paths: Sequence[Path],
    output_path: Path,
    provenance_path: Path,
    *,
    overwrite: bool,
) -> None:
    errors: list[str] = []
    resolved_sources = sources_path.resolve()
    resolved_inputs = [path.resolve() for path in input_paths]
    resolved_output = output_path.resolve()
    resolved_provenance = provenance_path.resolve()

    if not input_paths:
        errors.append("no_input_batches")
    if len(set(resolved_inputs)) != len(resolved_inputs):
        errors.append("duplicate_input_path")
    protected_inputs = {resolved_sources, *resolved_inputs}
    if resolved_output in protected_inputs:
        errors.append("output_overwrites_input")
    if resolved_provenance in protected_inputs:
        errors.append("provenance_overwrites_input")
    if resolved_output == resolved_provenance:
        errors.append("output_and_provenance_paths_match")
    if not overwrite and output_path.exists():
        errors.append(f"output_exists:{output_path}")
    if not overwrite and provenance_path.exists():
        errors.append(f"provenance_exists:{provenance_path}")
    if errors:
        raise MergeValidationError(errors)


def _validate_and_order(
    source_rows: Sequence[dict[str, Any]],
    batches: Sequence[tuple[Path, Sequence[dict[str, Any]]]],
) -> list[dict[str, Any]]:
    errors: list[str] = []
    source_by_id: dict[str, dict[str, Any]] = {}
    order_by_id: dict[str, int] = {}
    seen_groups: dict[str, str] = {}
    generation_orders: list[int] = []

    for row_number, source in enumerate(source_rows, start=1):
        source_id = source.get("source_id")
        if not isinstance(source_id, str) or not source_id:
            errors.append(f"source_id_missing:manifest:{row_number}")
            continue
        if source_id in source_by_id:
            errors.append(f"duplicate_source_id:manifest:{source_id}")
            continue
        source_by_id[source_id] = source

        generation_order = source.get("generation_order")
        if not isinstance(generation_order, int) or isinstance(generation_order, bool):
            errors.append(f"invalid_generation_order:{source_id}")
        else:
            order_by_id[source_id] = generation_order
            generation_orders.append(generation_order)

        group_id = source.get("group_id")
        if isinstance(group_id, str) and group_id:
            if group_id in seen_groups:
                errors.append(
                    f"duplicate_group_id:manifest:{group_id}:{seen_groups[group_id]}:{source_id}"
                )
            else:
                seen_groups[group_id] = source_id

        for field in IDENTITY_FIELDS:
            if field not in source:
                errors.append(f"source_identity_field_missing:{source_id}:{field}")

    if len(generation_orders) != len(set(generation_orders)):
        errors.append("duplicate_generation_order:manifest")
    if generation_orders:
        sorted_orders = sorted(generation_orders)
        expected_orders = list(range(sorted_orders[0], sorted_orders[0] + len(sorted_orders)))
        if sorted_orders != expected_orders:
            errors.append("generation_order_not_consecutive:manifest")

    writer_by_id: dict[str, dict[str, Any]] = {}
    for input_path, rows in batches:
        for row_number, writer in enumerate(rows, start=1):
            source_id = writer.get("source_id")
            location = f"{input_path}:{row_number}"
            if not isinstance(source_id, str) or not source_id:
                errors.append(f"source_id_missing:writer:{location}")
                continue
            if source_id in writer_by_id:
                errors.append(f"duplicate_writer_source_id:{source_id}:{location}")
                continue
            writer_by_id[source_id] = writer
            source = source_by_id.get(source_id)
            if source is None:
                errors.append(f"unknown_writer_source_id:{source_id}:{location}")
                continue

            for field in IDENTITY_FIELDS:
                if writer.get(field) != source.get(field):
                    errors.append(f"stale_identity:{source_id}:{field}:{location}")
            if "generation_order" in writer and writer.get("generation_order") != source.get(
                "generation_order"
            ):
                errors.append(f"stale_identity:{source_id}:generation_order:{location}")

    expected_ids = set(source_by_id)
    writer_ids = set(writer_by_id)
    for source_id in sorted(expected_ids - writer_ids):
        errors.append(f"missing_writer_source_id:{source_id}")
    for source_id in sorted(writer_ids - expected_ids):
        # Unknown IDs are already reported with their input location.  This aggregate
        # flag makes the final set mismatch explicit without exposing response text.
        errors.append(f"unexpected_writer_source_id:{source_id}")

    if errors:
        raise MergeValidationError(errors)

    return [writer_by_id[source_id] for source_id in sorted(expected_ids, key=order_by_id.__getitem__)]


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


def merge_factual_rewrite_batches(
    sources_path: Path | str,
    input_paths: Sequence[Path | str],
    output_path: Path | str,
    provenance_path: Path | str,
    *,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Validate and atomically merge writer rows in frozen generation order."""

    sources_path = Path(sources_path)
    normalized_inputs = [Path(path) for path in input_paths]
    output_path = Path(output_path)
    provenance_path = Path(provenance_path)
    _validate_paths(
        sources_path,
        normalized_inputs,
        output_path,
        provenance_path,
        overwrite=overwrite,
    )

    source_rows = _read_json_rows(sources_path)
    batches = [(path, _read_json_rows(path)) for path in normalized_inputs]
    ordered_rows = _validate_and_order(source_rows, batches)
    output_payload = _jsonl_bytes(ordered_rows)

    provenance: dict[str, Any] = {
        "schema_version": 1,
        "hash_algorithm": "sha256",
        "source_manifest": {
            "path": str(sources_path),
            "sha256": _sha256_file(sources_path),
            "row_count": len(source_rows),
        },
        "input_batches": [
            {
                "path": str(path),
                "sha256": _sha256_file(path),
                "row_count": len(rows),
            }
            for path, rows in batches
        ],
        "output": {
            "path": str(output_path),
            "sha256": _sha256_bytes(output_payload),
            "row_count": len(ordered_rows),
        },
        "canonical_source_ids_sha256": _sha256_bytes(
            ("\n".join(row["source_id"] for row in ordered_rows) + "\n").encode("utf-8")
        ),
    }
    provenance_payload = _json_bytes(provenance)

    staged_output: Path | None = None
    staged_provenance: Path | None = None
    try:
        staged_output = _stage_bytes(output_path, output_payload)
        staged_provenance = _stage_bytes(provenance_path, provenance_payload)
        os.replace(staged_output, output_path)
        staged_output = None
        os.replace(staged_provenance, provenance_path)
        staged_provenance = None
    finally:
        if staged_output is not None:
            staged_output.unlink(missing_ok=True)
        if staged_provenance is not None:
            staged_provenance.unlink(missing_ok=True)

    return provenance


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, required=True)
    parser.add_argument("--inputs", type=Path, nargs="+", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--provenance-output", type=Path, required=True)
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Atomically replace existing output/provenance files.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    try:
        provenance = merge_factual_rewrite_batches(
            args.sources,
            args.inputs,
            args.output,
            args.provenance_output,
            overwrite=args.overwrite,
        )
    except MergeValidationError as error:
        for item in error.errors:
            print(f"ERROR: {item}")
        return 1
    print(
        "Merged "
        f"{provenance['output']['row_count']} rows; "
        f"sha256={provenance['output']['sha256']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
