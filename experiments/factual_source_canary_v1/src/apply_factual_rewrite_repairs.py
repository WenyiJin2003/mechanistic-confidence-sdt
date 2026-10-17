#!/usr/bin/env python3
"""Apply explicit rewrite repairs to one complete, frozen factual pair batch.

Repairs are matched only by exact ``source_id``.  Frozen identity fields cannot
change, and the output is always ordered by the source manifest's authoritative
``generation_order``.  Validation completes before any output is staged.
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
DEFAULT_PRIVATE_ROOT = Path(__file__).resolve().parents[1] / "private_data"


class RepairOverlayError(ValueError):
    """Raised before output when a repair overlay is not identity-safe."""

    def __init__(self, errors: Sequence[str]):
        self.errors = tuple(errors)
        super().__init__("repair overlay validation failed: " + "; ".join(self.errors))


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_rows(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        raise RepairOverlayError([f"input_not_found:{path}"])
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
                        raise RepairOverlayError(
                            [f"invalid_json:{path}:{line_number}:{error.msg}"]
                        ) from error
        else:
            with path.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
            if isinstance(payload, list):
                rows = payload
            elif isinstance(payload, dict):
                keys = [
                    key
                    for key in ("rows", "pairs", "repairs", "sources")
                    if isinstance(payload.get(key), list)
                ]
                if len(keys) != 1:
                    raise RepairOverlayError([f"json_rows_not_found:{path}"])
                rows = payload[keys[0]]
            else:
                raise RepairOverlayError([f"json_rows_not_found:{path}"])
    except OSError as error:
        raise RepairOverlayError([f"input_read_failed:{path}:{error}"]) from error
    except json.JSONDecodeError as error:
        raise RepairOverlayError([f"invalid_json:{path}:{error.msg}"]) from error

    bad_rows = [str(index) for index, row in enumerate(rows, start=1) if not isinstance(row, dict)]
    if bad_rows:
        raise RepairOverlayError([f"row_not_object:{path}:{','.join(bad_rows)}"])
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
    base_path: Path,
    repair_paths: Sequence[Path],
    output_path: Path,
    provenance_path: Path | None,
    private_root: Path,
    *,
    overwrite: bool,
) -> None:
    errors: list[str] = []
    resolved_inputs = [
        sources_path.resolve(),
        base_path.resolve(),
        *(path.resolve() for path in repair_paths),
    ]
    resolved_output = output_path.resolve()
    resolved_provenance = provenance_path.resolve() if provenance_path is not None else None
    resolved_private_root = private_root.resolve()

    if not repair_paths:
        errors.append("no_repair_inputs")
    if len({path.resolve() for path in repair_paths}) != len(repair_paths):
        errors.append("duplicate_repair_path")
    if resolved_output in set(resolved_inputs):
        errors.append("output_overwrites_input")
    if resolved_provenance is not None and resolved_provenance in set(resolved_inputs):
        errors.append("provenance_overwrites_input")
    if resolved_provenance == resolved_output:
        errors.append("output_and_provenance_paths_match")
    for label, path in (("output", resolved_output), ("provenance", resolved_provenance)):
        if path is None:
            continue
        try:
            path.relative_to(resolved_private_root)
        except ValueError:
            errors.append(f"{label}_outside_private_data:{path}")
    if not overwrite and output_path.exists():
        errors.append(f"output_exists:{output_path}")
    if provenance_path is not None and not overwrite and provenance_path.exists():
        errors.append(f"provenance_exists:{provenance_path}")
    if errors:
        raise RepairOverlayError(errors)


def _index_rows(
    rows: Sequence[dict[str, Any]], label: str, errors: list[str]
) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for row_number, row in enumerate(rows, start=1):
        source_id = row.get("source_id")
        if not isinstance(source_id, str) or not source_id:
            errors.append(f"source_id_missing:{label}:{row_number}")
            continue
        if source_id in indexed:
            errors.append(f"duplicate_source_id:{label}:{source_id}")
            continue
        indexed[source_id] = row
    return indexed


def _validate_and_overlay(
    source_rows: Sequence[dict[str, Any]],
    base_rows: Sequence[dict[str, Any]],
    repair_batches: Sequence[tuple[Path, Sequence[dict[str, Any]]]],
) -> tuple[list[dict[str, Any]], list[str]]:
    errors: list[str] = []
    sources = _index_rows(source_rows, "manifest", errors)
    base = _index_rows(base_rows, "base", errors)
    generation_order: dict[str, int] = {}

    for source_id, source in sources.items():
        order = source.get("generation_order")
        if not isinstance(order, int) or isinstance(order, bool):
            errors.append(f"invalid_generation_order:{source_id}")
        else:
            generation_order[source_id] = order
        for field in IDENTITY_FIELDS:
            if field not in source:
                errors.append(f"source_identity_field_missing:{source_id}:{field}")

    orders = list(generation_order.values())
    if len(orders) != len(set(orders)):
        errors.append("duplicate_generation_order:manifest")
    if orders:
        sorted_orders = sorted(orders)
        if sorted_orders != list(range(sorted_orders[0], sorted_orders[0] + len(orders))):
            errors.append("generation_order_not_consecutive:manifest")

    source_ids = set(sources)
    base_ids = set(base)
    for source_id in sorted(source_ids - base_ids):
        errors.append(f"missing_base_source_id:{source_id}")
    for source_id in sorted(base_ids - source_ids):
        errors.append(f"unexpected_base_source_id:{source_id}")

    for source_id in sorted(source_ids & base_ids):
        source = sources[source_id]
        row = base[source_id]
        for field in IDENTITY_FIELDS:
            if row.get(field) != source.get(field):
                errors.append(f"stale_base_identity:{source_id}:{field}")
        if "generation_order" in row and row.get("generation_order") != source.get(
            "generation_order"
        ):
            errors.append(f"stale_base_identity:{source_id}:generation_order")

    repairs: dict[str, dict[str, Any]] = {}
    for repair_path, rows in repair_batches:
        for row_number, repair in enumerate(rows, start=1):
            source_id = repair.get("source_id")
            location = f"{repair_path}:{row_number}"
            if not isinstance(source_id, str) or not source_id:
                errors.append(f"source_id_missing:repair:{location}")
                continue
            if source_id in repairs:
                errors.append(f"duplicate_repair_source_id:{source_id}:{location}")
                continue
            repairs[source_id] = repair
            source = sources.get(source_id)
            base_row = base.get(source_id)
            if source is None or base_row is None:
                errors.append(f"unknown_repair_source_id:{source_id}:{location}")
                continue
            for field in IDENTITY_FIELDS:
                if field not in repair:
                    errors.append(f"repair_identity_field_missing:{source_id}:{field}:{location}")
                elif repair.get(field) != source.get(field) or repair.get(
                    field
                ) != base_row.get(field):
                    errors.append(f"changed_repair_identity:{source_id}:{field}:{location}")
            if "generation_order" in repair and repair.get("generation_order") != source.get(
                "generation_order"
            ):
                errors.append(f"changed_repair_identity:{source_id}:generation_order:{location}")

    if not repairs:
        errors.append("no_repair_rows")
    if errors:
        raise RepairOverlayError(errors)

    output_rows: list[dict[str, Any]] = []
    for source_id in sorted(source_ids, key=generation_order.__getitem__):
        original = base[source_id]
        if source_id not in repairs:
            output_rows.append(dict(original))
            continue
        overlaid = dict(original)
        overlaid.update(repairs[source_id])
        if "generation_order" in original or "generation_order" in repairs[source_id]:
            overlaid["generation_order"] = generation_order[source_id]
        output_rows.append(overlaid)
    return output_rows, sorted(repairs)


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


def _commit(staged_targets: Sequence[tuple[Path, Path]], *, overwrite: bool) -> None:
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
        rollback_errors: list[str] = []
        for target in reversed(committed):
            try:
                target.unlink(missing_ok=True)
            except OSError as rollback_error:
                rollback_errors.append(f"remove_new:{target}:{rollback_error}")
        for target, backup in reversed(tuple(backups.items())):
            if backup.exists():
                try:
                    os.replace(backup, target)
                except OSError as rollback_error:
                    rollback_errors.append(f"restore_old:{target}:{rollback_error}")
        if rollback_errors:
            raise RuntimeError(
                "repair overlay commit failed and rollback was incomplete: "
                + "; ".join(rollback_errors)
            ) from error
        raise
    else:
        for backup in backups.values():
            backup.unlink(missing_ok=True)


def apply_factual_rewrite_repairs(
    sources_path: Path | str,
    base_path: Path | str,
    repair_paths: Sequence[Path | str],
    output_path: Path | str,
    *,
    provenance_path: Path | str | None = None,
    overwrite: bool = False,
    private_root: Path | str | None = None,
) -> dict[str, Any]:
    """Validate repairs and atomically write the overlaid complete batch."""

    sources_path = Path(sources_path)
    base_path = Path(base_path)
    repair_paths = [Path(path) for path in repair_paths]
    output_path = Path(output_path)
    provenance_path = Path(provenance_path) if provenance_path is not None else None
    private_root = DEFAULT_PRIVATE_ROOT if private_root is None else Path(private_root)
    _validate_paths(
        sources_path,
        base_path,
        repair_paths,
        output_path,
        provenance_path,
        private_root,
        overwrite=overwrite,
    )

    source_rows = _read_rows(sources_path)
    base_rows = _read_rows(base_path)
    repair_batches = [(path, _read_rows(path)) for path in repair_paths]
    output_rows, repaired_ids = _validate_and_overlay(
        source_rows, base_rows, repair_batches
    )
    output_payload = _jsonl_bytes(output_rows)
    provenance: dict[str, Any] = {
        "schema_version": 1,
        "hash_algorithm": "sha256",
        "source_manifest": {
            "sha256": _sha256_file(sources_path),
            "row_count": len(source_rows),
        },
        "base_batch": {
            "sha256": _sha256_file(base_path),
            "row_count": len(base_rows),
        },
        "repair_inputs": [
            {"sha256": _sha256_file(path), "row_count": len(rows)}
            for path, rows in repair_batches
        ],
        "repair_count": len(repaired_ids),
        "repaired_source_ids_sha256": _sha256_bytes(
            ("\n".join(repaired_ids) + "\n").encode("utf-8")
        ),
        "output": {
            "sha256": _sha256_bytes(output_payload),
            "row_count": len(output_rows),
        },
    }

    staged: list[tuple[Path, Path]] = []
    try:
        staged.append((_stage_bytes(output_path, output_payload), output_path))
        if provenance_path is not None:
            staged.append(
                (_stage_bytes(provenance_path, _json_bytes(provenance)), provenance_path)
            )
        _commit(staged, overwrite=overwrite)
    finally:
        for temporary_path, _ in staged:
            temporary_path.unlink(missing_ok=True)
    return provenance


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, required=True)
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--repairs", type=Path, nargs="+", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--provenance-output", type=Path)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    try:
        provenance = apply_factual_rewrite_repairs(
            args.sources,
            args.base,
            args.repairs,
            args.output,
            provenance_path=args.provenance_output,
            overwrite=args.overwrite,
        )
    except RepairOverlayError as error:
        for item in error.errors:
            print(f"ERROR: {item}")
        return 1
    print(
        f"Applied {provenance['repair_count']} repairs to "
        f"{provenance['output']['row_count']} rows; "
        f"sha256={provenance['output']['sha256']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
