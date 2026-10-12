"""Prepare the fixed score-free cross-task rewrite microbatch.

The frozen 50-source inventory already assigns every task, cue family, and
length direction.  This module selects a preregistered ten-cell subset from
that inventory; it does not generate rewrites, run inference, or read scores or
activations.

Running without ``--apply`` validates the frozen input and reports counts only.
Writing the private rewrite input and public text-free manifest requires the
explicit ``--apply`` flag.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


BASE = Path(__file__).resolve().parents[1]
PRIVATE = BASE / "private_data"
MANIFESTS = BASE / "manifests"

DEFAULT_SOURCES = PRIVATE / "challenge_sources_50.jsonl"
DEFAULT_SELECTION_MANIFEST = MANIFESTS / "challenge_selection_manifest.json"
DEFAULT_PRIVATE_OUTPUT = PRIVATE / "rewrite_input_cross_task_microbatch.jsonl"
DEFAULT_PUBLIC_MANIFEST = MANIFESTS / "cross_task_microbatch_manifest.json"

TASKS = [
    "factual_explanation",
    "math_logic",
    "programming",
    "comparison_analysis",
    "summary_judgment",
]
CUE_FAMILIES = [
    "embedded_stance_predicate",
    "modal_force_scope",
    "compositional_polarity",
    "discourse_level_calibration",
    "contrastive_commitment",
]
LENGTH_DIRECTIONS = ["confident_longer", "hedged_longer"]

# The order is part of the frozen protocol and is also the private output order.
CELL_PLAN = [
    ("factual_explanation", "embedded_stance_predicate", "confident_longer"),
    ("factual_explanation", "modal_force_scope", "hedged_longer"),
    ("math_logic", "modal_force_scope", "confident_longer"),
    ("math_logic", "compositional_polarity", "hedged_longer"),
    ("programming", "compositional_polarity", "confident_longer"),
    ("programming", "discourse_level_calibration", "hedged_longer"),
    ("comparison_analysis", "discourse_level_calibration", "confident_longer"),
    ("comparison_analysis", "contrastive_commitment", "hedged_longer"),
    ("summary_judgment", "contrastive_commitment", "confident_longer"),
    ("summary_judgment", "embedded_stance_predicate", "hedged_longer"),
]

PRIVATE_SOURCE_KEYS = [
    "source_id",
    "dataset",
    "dataset_revision",
    "group_id",
    "normalized_prompt_sha256",
    "original_response_sha256",
    "development_template_group",
    "task",
    "length_bin",
    "prompt",
    "original_response",
    "cue_family",
    "length_direction",
]
REWRITE_INPUT_KEYS = [
    "source_id",
    "dataset",
    "original_response_sha256",
    "task",
    "length_bin",
    "prompt",
    "original_response",
    "cue_family",
    "length_direction",
]
PUBLIC_RECORD_KEYS = [
    "source_id",
    "normalized_prompt_sha256",
    "original_response_sha256",
    "task",
    "cue_family",
    "length_direction",
]
FROZEN_PUBLIC_RECORD_KEYS = [
    "source_id",
    "group_id",
    "normalized_prompt_sha256",
    "original_response_sha256",
    "development_template_group",
    "dataset",
    "task",
    "length_bin",
    "cue_family",
    "length_direction",
]
UNIQUE_FIELDS = [
    "source_id",
    "group_id",
    "normalized_prompt_sha256",
    "development_template_group",
]


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_text(value: str) -> str:
    return _sha256_bytes(value.encode("utf-8"))


def _normalize_prompt(value: str) -> str:
    """Match the normalizer used when the frozen source hashes were created."""
    return " ".join(value.casefold().split())


def _dump_jsonl(rows: Iterable[dict[str, Any]]) -> str:
    return "".join(
        json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
        for row in rows
    )


def _dump_json(value: dict[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def load_jsonl(path: Path, label: str) -> tuple[list[dict[str, Any]], bytes]:
    """Load object-only JSONL while retaining the exact bytes for freeze checks."""
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"{label} is not valid UTF-8") from exc
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Invalid {label} JSON on line {line_number}: {exc.msg}"
            ) from exc
        if not isinstance(row, dict):
            raise ValueError(f"{label} line {line_number} must be a JSON object")
        rows.append(row)
    return rows, raw


def load_json(path: Path, label: str) -> tuple[dict[str, Any], bytes]:
    raw = path.read_bytes()
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Invalid {label} JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    return value, raw


def _format_cell(cell: tuple[str, str, str]) -> str:
    return "/".join(cell)


def _validate_row_schema_and_hashes(rows: list[dict[str, Any]]) -> None:
    for index, row in enumerate(rows, 1):
        missing = [key for key in PRIVATE_SOURCE_KEYS if key not in row]
        if missing:
            raise ValueError(f"Frozen source row {index} is missing required fields: {missing}")
        for field in PRIVATE_SOURCE_KEYS:
            if not isinstance(row[field], str) or not row[field]:
                raise ValueError(
                    f"Frozen source row {index} field {field!r} must be a non-empty string"
                )
        expected_response_hash = _sha256_text(row["original_response"])
        if row["original_response_sha256"] != expected_response_hash:
            raise ValueError(
                f"Frozen source row {index} original_response_sha256 does not match its text"
            )
        expected_prompt_hash = _sha256_text(_normalize_prompt(row["prompt"]))
        if row["normalized_prompt_sha256"] != expected_prompt_hash:
            raise ValueError(
                f"Frozen source row {index} normalized_prompt_sha256 does not match its prompt"
            )


def _validate_unique_design(rows: list[dict[str, Any]]) -> None:
    if len(rows) != 50:
        raise ValueError(f"Expected exactly 50 frozen sources; found {len(rows)}")

    for field in UNIQUE_FIELDS:
        counts = Counter(row[field] for row in rows)
        duplicates = sorted(value for value, count in counts.items() if count > 1)
        if duplicates:
            raise ValueError(
                f"Frozen source rows contain duplicate {field}: {duplicates[0]!r}"
            )

    expected_cells = [
        (task, family, direction)
        for task in TASKS
        for family in CUE_FAMILIES
        for direction in LENGTH_DIRECTIONS
    ]
    cell_counts = Counter(
        (row["task"], row["cue_family"], row["length_direction"]) for row in rows
    )
    missing = [cell for cell in expected_cells if cell_counts[cell] == 0]
    duplicate = [cell for cell in expected_cells if cell_counts[cell] > 1]
    unexpected = sorted(cell for cell in cell_counts if cell not in set(expected_cells))
    if missing or duplicate or unexpected:
        details = []
        if missing:
            details.append("missing cells: " + ", ".join(_format_cell(cell) for cell in missing))
        if duplicate:
            details.append(
                "duplicate cells: " + ", ".join(_format_cell(cell) for cell in duplicate)
            )
        if unexpected:
            details.append(
                "unexpected cells: " + ", ".join(_format_cell(cell) for cell in unexpected)
            )
        raise ValueError("Frozen source design mismatch; " + "; ".join(details))

    expected_task_counts = Counter({task: 10 for task in TASKS})
    expected_family_counts = Counter({family: 10 for family in CUE_FAMILIES})
    expected_direction_counts = Counter({direction: 25 for direction in LENGTH_DIRECTIONS})
    if Counter(row["task"] for row in rows) != expected_task_counts:
        raise ValueError("Frozen source design must contain exactly 10 sources per task")
    if Counter(row["cue_family"] for row in rows) != expected_family_counts:
        raise ValueError("Frozen source design must contain exactly 10 sources per cue family")
    if Counter(row["length_direction"] for row in rows) != expected_direction_counts:
        raise ValueError("Frozen source design must contain exactly 25 sources per direction")


def validate_selection_manifest(
    rows: list[dict[str, Any]], source_bytes: bytes, selection_manifest: dict[str, Any]
) -> None:
    """Verify that rows and exact file bytes match the public source freeze."""
    expected_hash = (
        selection_manifest.get("private_output_sha256", {})
        .get("challenge_sources_50.jsonl")
    )
    actual_hash = _sha256_bytes(source_bytes)
    if not isinstance(expected_hash, str) or expected_hash != actual_hash:
        raise ValueError(
            "Frozen challenge_sources_50.jsonl SHA-256 does not match the selection manifest"
        )
    if selection_manifest.get("source_count") != 50:
        raise ValueError("Selection manifest must declare exactly 50 frozen sources")

    records = selection_manifest.get("source_records")
    if not isinstance(records, list) or len(records) != 50:
        raise ValueError("Selection manifest must contain exactly 50 source records")
    if any(not isinstance(record, dict) for record in records):
        raise ValueError("Selection manifest source records must be JSON objects")

    record_ids = [record.get("source_id") for record in records]
    if len(set(record_ids)) != len(record_ids):
        raise ValueError("Selection manifest contains duplicate source IDs")
    records_by_id = {record.get("source_id"): record for record in records}
    rows_by_id = {row["source_id"]: row for row in rows}
    if set(records_by_id) != set(rows_by_id):
        raise ValueError("Frozen source IDs do not match the selection manifest")
    for source_id, row in rows_by_id.items():
        record = records_by_id[source_id]
        for field in FROZEN_PUBLIC_RECORD_KEYS:
            if record.get(field) != row[field]:
                raise ValueError(
                    f"Frozen source {source_id!r} field {field!r} does not match "
                    "the selection manifest"
                )


def validate_frozen_input(
    rows: list[dict[str, Any]], source_bytes: bytes, selection_manifest: dict[str, Any]
) -> None:
    """Validate the complete frozen inventory without selecting or writing."""
    _validate_row_schema_and_hashes(rows)
    _validate_unique_design(rows)
    validate_selection_manifest(rows, source_bytes, selection_manifest)


def select_microbatch(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Select exactly one frozen row for each preregistered cross-task cell."""
    rows_by_cell: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for row in rows:
        cell = (row["task"], row["cue_family"], row["length_direction"])
        rows_by_cell.setdefault(cell, []).append(row)

    selected: list[dict[str, Any]] = []
    for cell in CELL_PLAN:
        matches = rows_by_cell.get(cell, [])
        if not matches:
            raise ValueError(f"Required microbatch cell is missing: {_format_cell(cell)}")
        if len(matches) > 1:
            raise ValueError(f"Required microbatch cell is duplicated: {_format_cell(cell)}")
        selected.append(matches[0].copy())

    if len({row["source_id"] for row in selected}) != 10:
        raise ValueError("Cross-task microbatch must contain ten unique source IDs")
    if Counter(row["task"] for row in selected) != Counter({task: 2 for task in TASKS}):
        raise ValueError("Cross-task microbatch must contain exactly two sources per task")
    if Counter(row["cue_family"] for row in selected) != Counter(
        {family: 2 for family in CUE_FAMILIES}
    ):
        raise ValueError("Cross-task microbatch must contain exactly two sources per cue family")
    if Counter(row["length_direction"] for row in selected) != Counter(
        {direction: 5 for direction in LENGTH_DIRECTIONS}
    ):
        raise ValueError("Cross-task microbatch must have a 5/5 length-direction split")
    return selected


def _counts(rows: list[dict[str, Any]], field: str) -> dict[str, int]:
    return dict(sorted(Counter(row[field] for row in rows).items()))


def build_artifacts(
    source_rows: list[dict[str, Any]],
    source_bytes: bytes,
    selection_manifest: dict[str, Any],
    selection_manifest_bytes: bytes | None = None,
) -> dict[str, Any]:
    """Build validated private/public artifacts entirely in memory."""
    validate_frozen_input(source_rows, source_bytes, selection_manifest)
    selected = select_microbatch(source_rows)
    private_rows = [
        {key: row[key] for key in REWRITE_INPUT_KEYS}
        for row in selected
    ]
    private_dump = _dump_jsonl(private_rows)
    if selection_manifest_bytes is None:
        selection_manifest_bytes = _dump_json(selection_manifest).encode("utf-8")

    manifest: dict[str, Any] = {
        "manifest_version": 1,
        "stage": "pre_rewrite_cross_task_microbatch",
        "selection_method": "fixed score-free cross-task cell plan",
        "source_count": len(selected),
        "frozen_source_count": len(source_rows),
        "source_ids": [row["source_id"] for row in selected],
        "frozen_source_input_sha256": _sha256_bytes(source_bytes),
        "selection_manifest_sha256": _sha256_bytes(selection_manifest_bytes),
        "private_output_sha256": _sha256_text(private_dump),
        "by_task": _counts(selected, "task"),
        "by_cue_family": _counts(selected, "cue_family"),
        "by_length_direction": _counts(selected, "length_direction"),
        "cell_plan": [
            {
                "task": task,
                "cue_family": family,
                "length_direction": direction,
            }
            for task, family, direction in CELL_PLAN
        ],
        "source_records": [
            {key: row[key] for key in PUBLIC_RECORD_KEYS}
            for row in selected
        ],
        "contains_source_text": False,
        "rewrites_generated": False,
        "score_or_activation_used": False,
        "model_inference_used": False,
    }
    manifest_dump = _dump_json(manifest)
    return {
        "selected_rows": selected,
        "private_rows": private_rows,
        "manifest": manifest,
        "texts": {
            "rewrite_input_cross_task_microbatch.jsonl": private_dump,
            "cross_task_microbatch_manifest.json": manifest_dump,
        },
    }


def _atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    file_descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent, prefix=f".{path.name}.", suffix=".tmp"
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(file_descriptor, "w", encoding="utf-8", newline="") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        temporary_path.replace(path)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()


def write_artifacts(
    artifacts: dict[str, Any],
    *,
    private_output: Path,
    manifest_output: Path,
    protected_inputs: Iterable[Path] = (),
) -> list[Path]:
    """Write both outputs atomically per file after all validation succeeds."""
    targets = {
        private_output: artifacts["texts"]["rewrite_input_cross_task_microbatch.jsonl"],
        manifest_output: artifacts["texts"]["cross_task_microbatch_manifest.json"],
    }
    resolved_targets = [path.resolve() for path in targets]
    if len(set(resolved_targets)) != len(resolved_targets):
        raise ValueError("Private output and public manifest paths must be distinct")
    protected = {path.resolve() for path in protected_inputs}
    collisions = sorted(str(path) for path in set(resolved_targets) & protected)
    if collisions:
        raise ValueError(f"Refusing to overwrite an input file: {collisions[0]}")
    for path, content in targets.items():
        _atomic_write_text(path, content)
    return list(targets)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sources",
        type=Path,
        default=DEFAULT_SOURCES,
        help="Frozen private challenge_sources_50.jsonl",
    )
    parser.add_argument(
        "--selection-manifest",
        type=Path,
        default=DEFAULT_SELECTION_MANIFEST,
        help="Public manifest that freezes the exact 50-source input hash and metadata",
    )
    parser.add_argument(
        "--private-output",
        type=Path,
        default=DEFAULT_PRIVATE_OUTPUT,
    )
    parser.add_argument(
        "--manifest-output",
        type=Path,
        default=DEFAULT_PUBLIC_MANIFEST,
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write outputs after validation. Omit for a no-write validation run.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    source_rows, source_bytes = load_jsonl(args.sources, "frozen challenge source")
    selection_manifest, selection_manifest_bytes = load_json(
        args.selection_manifest, "source-selection manifest"
    )
    artifacts = build_artifacts(
        source_rows,
        source_bytes,
        selection_manifest,
        selection_manifest_bytes,
    )
    written: list[Path] = []
    if args.apply:
        written = write_artifacts(
            artifacts,
            private_output=args.private_output,
            manifest_output=args.manifest_output,
            protected_inputs=(args.sources, args.selection_manifest),
        )

    manifest = artifacts["manifest"]
    print(
        json.dumps(
            {
                "validated": True,
                "applied": args.apply,
                "written_file_count": len(written),
                "source_count": manifest["source_count"],
                "by_task": manifest["by_task"],
                "by_cue_family": manifest["by_cue_family"],
                "by_length_direction": manifest["by_length_direction"],
                "rewrite_generation": "not run",
                "inference": "not run",
                "score_or_activation_used": False,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
