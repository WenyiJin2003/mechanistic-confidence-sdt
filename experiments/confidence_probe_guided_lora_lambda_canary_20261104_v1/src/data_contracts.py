"""Provider-free data and completion-mask contracts for the lambda canary."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable, Mapping

import torch

from lambda_objective import file_sha256, role_target


IDENTITY_FIELDS = ("source_id", "normalized_question_sha256")
ROLES = ("confident", "hesitant")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ValueError(f"{path}:{line_number} is not a JSON object")
            rows.append(row)
    if not rows:
        raise ValueError(f"empty JSONL file: {path}")
    return rows


def validate_paired_rows(rows: list[dict[str, Any]], *, expected_role: str | None = None) -> None:
    if expected_role is not None and expected_role not in ROLES:
        raise ValueError(f"role must be one of {ROLES}")
    ids: set[str] = set()
    for index, row in enumerate(rows):
        label = str(row.get("id", f"row-{index}"))
        required = (
            "id",
            "source_id",
            "normalized_question_sha256",
            "question",
            "confident_response",
            "hesitant_response",
        )
        for field in required:
            if not isinstance(row.get(field), str) or not row[field].strip():
                raise ValueError(f"{label}: missing or empty {field}")
        if row["id"] in ids:
            raise ValueError(f"duplicate row id: {row['id']}")
        ids.add(row["id"])
        if row["confident_response"] == row["hesitant_response"]:
            raise ValueError(f"{label}: confident and hesitant responses are identical")
        if row.get("engineering_only") is not True:
            raise ValueError(f"{label}: this runner accepts only engineering-only canary rows")
        if row.get("confirmatory_status") != "post_exposure_not_confirmatory":
            raise ValueError(f"{label}: confirmatory status is not the frozen canary label")


def select_role_text(row: Mapping[str, Any], role: str) -> tuple[str, str, float]:
    if role not in ROLES:
        raise ValueError(f"role must be one of {ROLES}")
    question = row.get("question")
    answer = row.get(f"{role}_response")
    if not isinstance(question, str) or not question.strip():
        raise ValueError(f"{row.get('id')}: empty question")
    if not isinstance(answer, str) or not answer.strip():
        raise ValueError(f"{row.get('id')}: empty {role} response")
    opposite = row.get("hesitant_response" if role == "confident" else "confident_response")
    if answer == opposite:
        raise ValueError(f"{row.get('id')}: paired responses are identical")
    return question, answer, role_target(role)


def identity_inventory(rows: Iterable[Mapping[str, Any]]) -> dict[str, set[str]]:
    inventory = {field: set() for field in IDENTITY_FIELDS}
    for row in rows:
        for field in IDENTITY_FIELDS:
            value = row.get(field)
            if not isinstance(value, str) or not value:
                raise ValueError(f"{row.get('id')}: missing identity field {field}")
            inventory[field].add(value)
    return inventory


def assert_source_disjoint(
    named_rows: Mapping[str, list[dict[str, Any]]]
) -> dict[str, Any]:
    """Fail closed on source or normalized-question overlap between cohorts."""

    if len(named_rows) < 2:
        raise ValueError("at least two named cohorts are required for a disjointness check")
    inventories = {
        name: identity_inventory(rows) for name, rows in named_rows.items()
    }
    checks: list[dict[str, Any]] = []
    names = list(named_rows)
    for left_index, left in enumerate(names):
        for right in names[left_index + 1 :]:
            for field in IDENTITY_FIELDS:
                overlap = inventories[left][field] & inventories[right][field]
                checks.append(
                    {
                        "left": left,
                        "right": right,
                        "field": field,
                        "overlap_count": len(overlap),
                    }
                )
                if overlap:
                    sample = sorted(overlap)[:3]
                    raise ValueError(
                        f"{field} overlap between {left} and {right}: "
                        f"{len(overlap)}; sample={sample}"
                    )
    return {
        "status": "PASS",
        "fields": list(IDENTITY_FIELDS),
        "cohort_counts": {name: len(rows) for name, rows in named_rows.items()},
        "checks": checks,
    }


def validate_disjoint_files(
    train_path: Path, comparison_paths: list[Path]
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    train_rows = read_jsonl(train_path)
    validate_paired_rows(train_rows)
    named_rows: dict[str, list[dict[str, Any]]] = {"train": train_rows}
    file_records = [
        {
            "name": "train",
            "path": str(train_path.resolve()),
            "sha256": file_sha256(train_path),
            "rows": len(train_rows),
        }
    ]
    for index, path in enumerate(comparison_paths, start=1):
        name = f"preserved_{index}"
        rows = read_jsonl(path)
        validate_paired_rows(rows)
        named_rows[name] = rows
        file_records.append(
            {
                "name": name,
                "path": str(path.resolve()),
                "sha256": file_sha256(path),
                "rows": len(rows),
            }
        )
    report = assert_source_disjoint(named_rows) if comparison_paths else {
        "status": "NOT_RUN_NO_COMPARISON_FILES",
        "fields": list(IDENTITY_FIELDS),
        "cohort_counts": {"train": len(train_rows)},
        "checks": [],
    }
    report["files"] = file_records
    return train_rows, report


def completion_only_contract(
    prompt_ids: list[int],
    full_ids: list[int],
    *,
    assistant_end_id: int,
    max_length: int,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """Build token IDs, CE labels, and ordinary-response mask.

    CE includes the assistant end marker.  The probe pool excludes it, as well
    as every system/user/prompt token.
    """

    if not prompt_ids or len(full_ids) <= len(prompt_ids):
        raise ValueError("prompt/full token sequences are empty or malformed")
    if full_ids[: len(prompt_ids)] != prompt_ids:
        raise ValueError("prompt tokens are not an exact prefix of full tokens")
    start = len(prompt_ids)
    try:
        stop = start + full_ids[start:].index(assistant_end_id)
    except ValueError as error:
        raise ValueError("assistant end marker is absent") from error
    if stop <= start:
        raise ValueError("assistant response has no ordinary content tokens")
    ids = full_ids[: stop + 1]
    if len(ids) > max_length:
        raise ValueError("tokenized row exceeds max_length")
    labels = [-100] * start + ids[start:]
    response_mask = [False] * len(ids)
    response_mask[start:stop] = [True] * (stop - start)
    return (
        torch.tensor(ids, dtype=torch.long),
        torch.tensor(labels, dtype=torch.long),
        torch.tensor(response_mask, dtype=torch.bool),
    )
