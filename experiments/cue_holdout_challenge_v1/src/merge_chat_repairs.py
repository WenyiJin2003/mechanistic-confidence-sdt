"""Apply narrowly scoped Chat repair objects to private writer JSONL files.

Each repair file must be one JSON object with this exact shape::

    {"repairs": [
        {"source_id": "...", "field": "confident_response",
         "revised_response": "..."}
    ]}

Only response text is replaceable. Writer row order and every other field are
preserved. The output is written atomically and must remain inside this
challenge's ignored ``private_data/`` directory.
"""
from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Iterable


BASE = Path(__file__).resolve().parents[1]
PRIVATE = BASE / "private_data"
EDITABLE_FIELDS = frozenset({"confident_response", "hedged_response"})
REPAIR_FIELDS = frozenset({"source_id", "field", "revised_response"})


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    """Read a JSONL file, rejecting non-object records."""
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_number}: invalid JSON: {exc.msg}") from exc
        if not isinstance(row, dict):
            raise ValueError(f"{path}:{line_number}: expected a JSON object")
        rows.append(row)
    return rows


def read_repair_object(path: Path) -> dict[str, Any]:
    """Read one strict ``{repairs: [...]}`` object."""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path}: invalid JSON: {exc.msg}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: repair payload must be a JSON object")
    extra = set(payload) - {"repairs"}
    if extra:
        raise ValueError(f"{path}: unexpected top-level fields: {sorted(extra)}")
    if set(payload) != {"repairs"} or not isinstance(payload["repairs"], list):
        raise ValueError(f"{path}: expected exactly one 'repairs' array")
    return payload


def _writer_index(rows: list[dict[str, Any]]) -> dict[str, int]:
    indexed: dict[str, int] = {}
    for position, row in enumerate(rows):
        source_id = row.get("source_id")
        if not isinstance(source_id, str) or not source_id.strip():
            raise ValueError(f"writer row {position + 1} has missing or invalid source_id")
        if source_id in indexed:
            raise ValueError(f"writer has duplicate source_id: {source_id}")
        indexed[source_id] = position
    return indexed


def merge_repairs(
    writer_rows: list[dict[str, Any]], repair_objects: Iterable[dict[str, Any]]
) -> tuple[list[dict[str, Any]], list[tuple[str, str]]]:
    """Return copied writer rows with validated response-field repairs applied."""
    writer_by_id = _writer_index(writer_rows)
    edits: dict[tuple[str, str], str] = {}

    object_count = 0
    for object_number, payload in enumerate(repair_objects, 1):
        object_count += 1
        if not isinstance(payload, dict) or set(payload) != {"repairs"}:
            raise ValueError(f"repair object {object_number} must contain exactly one 'repairs' field")
        repairs = payload["repairs"]
        if not isinstance(repairs, list):
            raise ValueError(f"repair object {object_number}: 'repairs' must be an array")
        for repair_number, repair in enumerate(repairs, 1):
            label = f"repair object {object_number}, entry {repair_number}"
            if not isinstance(repair, dict):
                raise ValueError(f"{label}: expected an object")
            missing = REPAIR_FIELDS - set(repair)
            extra = set(repair) - REPAIR_FIELDS
            if missing or extra:
                raise ValueError(
                    f"{label}: schema mismatch; missing={sorted(missing)}, extra={sorted(extra)}"
                )

            source_id = repair["source_id"]
            field = repair["field"]
            revised_response = repair["revised_response"]
            if not isinstance(source_id, str) or not source_id.strip():
                raise ValueError(f"{label}: source_id must be a nonempty string")
            if source_id not in writer_by_id:
                raise ValueError(f"{label}: unknown source_id: {source_id}")
            if field not in EDITABLE_FIELDS:
                raise ValueError(
                    f"{label}: field must be confident_response or hedged_response"
                )
            if not isinstance(revised_response, str) or not revised_response.strip():
                raise ValueError(f"{label}: revised_response must be a nonempty string")
            key = (source_id, field)
            if key in edits:
                raise ValueError(f"duplicate repair for source_id/field: {source_id}/{field}")
            edits[key] = revised_response

    if object_count == 0:
        raise ValueError("at least one repair object is required")
    if not edits:
        raise ValueError("repair objects contain no edits")

    merged = [dict(row) for row in writer_rows]
    for (source_id, field), revised_response in edits.items():
        merged[writer_by_id[source_id]][field] = revised_response
    return merged, list(edits)


def dump_jsonl(rows: Iterable[dict[str, Any]]) -> str:
    return "".join(
        json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows
    )


def _inside(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def atomic_write_private(
    path: Path,
    content: str,
    *,
    private_root: Path = PRIVATE,
    overwrite: bool = False,
    protected_inputs: Iterable[Path] = (),
) -> None:
    """Atomically write inside private_data without clobbering inputs."""
    target = path.resolve()
    root = private_root.resolve()
    if not _inside(target, root):
        raise ValueError(f"output must stay under challenge private_data: {root}")
    protected = {Path(item).resolve() for item in protected_inputs}
    if target in protected:
        raise ValueError("output must not overwrite a writer or repair input")
    if target.exists() and not overwrite:
        raise FileExistsError(f"refusing to overwrite existing output: {target}")

    target.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        dir=target.parent, prefix=f".{target.name}.", suffix=".tmp", text=True
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        if overwrite:
            os.replace(temporary, target)
        else:
            # A hard link gives us an atomic no-clobber publish on the same filesystem.
            try:
                os.link(temporary, target)
            except FileExistsError as exc:
                raise FileExistsError(f"refusing to overwrite existing output: {target}") from exc
            temporary.unlink()
        try:
            directory_fd = os.open(target.parent, os.O_RDONLY)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
        except OSError:
            # The content itself is already flushed and published atomically.
            pass
    finally:
        if temporary.exists():
            temporary.unlink()


def _resolve_cli_path(path: Path) -> Path:
    return path if path.is_absolute() else BASE / path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--writer", type=Path, action="append", required=True,
        help="Input writer JSONL; repeat to assemble disjoint batches",
    )
    parser.add_argument(
        "--repairs", type=Path, action="append", required=True,
        help="Chat repair JSON object; repeat for multiple files",
    )
    parser.add_argument("--output", type=Path, required=True, help="Output JSONL under private_data/")
    parser.add_argument("--force", action="store_true", help="Atomically replace an existing output")
    args = parser.parse_args(argv)

    writer_paths = [_resolve_cli_path(path) for path in args.writer]
    repair_paths = [_resolve_cli_path(path) for path in args.repairs]
    output_path = _resolve_cli_path(args.output)
    writer_rows = [row for path in writer_paths for row in read_jsonl(path)]
    repair_objects = [read_repair_object(path) for path in repair_paths]
    merged, applied = merge_repairs(writer_rows, repair_objects)
    atomic_write_private(
        output_path,
        dump_jsonl(merged),
        overwrite=args.force,
        protected_inputs=[*writer_paths, *repair_paths],
    )
    print(json.dumps({
        "writer_inputs": len(writer_paths),
        "writer_rows": len(merged),
        "repairs_applied": len(applied),
        "source_ids_repaired": len({source_id for source_id, _ in applied}),
        "output": str(output_path.resolve()),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
