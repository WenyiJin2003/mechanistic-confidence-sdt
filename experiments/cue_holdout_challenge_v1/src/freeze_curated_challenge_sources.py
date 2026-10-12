"""Validate and freeze a manually curated, score-free challenge source set.

The private curation file or files may contain primary and backup records, but
only the ten primaries for each task are frozen. Source text is resolved from
the existing candidate pool; curation rationale is never copied to an output.
This module does not import inference code or read scores or activations.

Running the command without ``--apply`` is validation-only.  Writing the
private source inventory, rewrite inputs, and public text-free records requires
both an explicit ``--curation-jsonl`` input and the explicit ``--apply`` flag.
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

import select_challenge_sources as selector


SELECTION_VERSION = 2
PRIMARY_STATUS = "primary"
BACKUP_STATUS = "backup"
CURATION_STATUSES = {PRIMARY_STATUS, BACKUP_STATUS}
DEFAULT_MIN_PER_TASK_DATASET = 0
PUBLIC_FREEZE_RECORD = "manifests/curated_source_replacement_freeze.json"

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
PUBLIC_SOURCE_KEYS = [
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
IDENTITY_FIELDS = [
    "source_id",
    "group_id",
    "normalized_prompt_sha256",
    "development_template_group",
]


def load_jsonl(path: Path, label: str) -> list[dict[str, Any]]:
    """Load object-only JSONL and report the offending line on failure."""
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid {label} JSON on line {line_number}: {exc.msg}") from exc
        if not isinstance(row, dict):
            raise ValueError(f"{label} line {line_number} must be a JSON object")
        rows.append(row)
    return rows


def _require_fields(row: dict[str, Any], fields: Iterable[str], label: str) -> None:
    missing = [field for field in fields if field not in row]
    if missing:
        raise ValueError(f"{label} is missing required fields: {missing}")


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _dump_jsonl(rows: Iterable[dict[str, Any]]) -> str:
    return "".join(
        json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
        for row in rows
    )


def _dump_json(value: dict[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _prepared_source(
    row: dict[str, Any],
    label: str,
    *,
    apply_exclusion: bool,
    exclusion_override: str | None = None,
) -> dict[str, Any]:
    """Validate source metadata and derive the canonical template identity."""
    required = [
        "source_id",
        "dataset",
        "dataset_revision",
        "group_id",
        "normalized_prompt_sha256",
        "original_response_sha256",
        "length_bin",
        "prompt",
        "original_response",
    ]
    if apply_exclusion:
        required.append("response_tokens")
    _require_fields(row, required, label)
    if row["dataset"] not in selector.DATASETS:
        raise ValueError(f"{label} has unsupported dataset {row['dataset']!r}")
    if not isinstance(row["prompt"], str) or not row["prompt"].strip():
        raise ValueError(f"{label} has an empty or non-string prompt")
    if not isinstance(row["original_response"], str) or not row["original_response"].strip():
        raise ValueError(f"{label} has an empty or non-string original_response")

    expected_prompt_hash = selector.digest(selector.norm(row["prompt"]))
    if row["normalized_prompt_sha256"] != expected_prompt_hash:
        raise ValueError(f"{label} normalized_prompt_sha256 does not match its prompt")
    expected_response_hash = selector.digest(row["original_response"])
    if row["original_response_sha256"] != expected_response_hash:
        raise ValueError(f"{label} original_response_sha256 does not match its response")

    prepared = row.copy()
    computed_template = selector.template_group(row["prompt"])
    stored_template = prepared.get("development_template_group")
    if stored_template is not None and stored_template != computed_template:
        raise ValueError(f"{label} development_template_group does not match its prompt")
    prepared["development_template_group"] = computed_template
    if apply_exclusion:
        reason = selector.exclusion(prepared)
        if reason and exclusion_override is None:
            raise ValueError(f"{label} fails existing exclusion rule: {reason}")
        if reason and exclusion_override != reason:
            raise ValueError(
                f"{label} exclusion_override does not exactly match actual reason {reason!r}"
            )
        if reason is None and exclusion_override is not None:
            raise ValueError(f"{label} supplies exclusion_override but no exclusion rule matched")
        if reason is not None:
            prepared["exclusion_override"] = reason
    return prepared


def _index_candidates(candidates: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for position, row in enumerate(candidates, 1):
        _require_fields(row, ["source_id"], f"candidate row {position}")
        source_id = row["source_id"]
        if not isinstance(source_id, str) or not source_id:
            raise ValueError(f"candidate row {position} has an empty or non-string source_id")
        if source_id in index:
            raise ValueError(f"Candidate pool contains duplicate source_id {source_id}")
        index[source_id] = row
    return index


def _normalize_curation(curation: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Validate curation metadata and split primary from backup records."""
    if not curation:
        raise ValueError("Curation file is empty")
    seen_ids: set[str] = set()
    primaries: list[dict[str, Any]] = []
    backups: list[dict[str, Any]] = []
    ranks: dict[tuple[str, str], list[int]] = {}
    any_rank = any("rank" in row for row in curation)

    for position, row in enumerate(curation, 1):
        label = f"curation row {position}"
        _require_fields(row, ["source_id", "selected_task"], label)
        source_id = row["source_id"]
        task = row["selected_task"]
        status = row.get("selection_status", PRIMARY_STATUS)
        if not isinstance(source_id, str) or not source_id:
            raise ValueError(f"{label} has an empty or non-string source_id")
        if source_id in seen_ids:
            raise ValueError(f"Curation contains duplicate source_id {source_id}")
        seen_ids.add(source_id)
        if task not in selector.TASKS:
            raise ValueError(f"{label} has unknown selected_task {task!r}")
        if status not in CURATION_STATUSES:
            raise ValueError(f"{label} has invalid selection_status {status!r}")
        if status == PRIMARY_STATUS and row.get("focal_answer_audit") != "pass":
            raise ValueError(
                f"{label} must record focal_answer_audit='pass' for a primary source"
            )
        if "focal_answer_audit" in row and row["focal_answer_audit"] != "pass":
            raise ValueError(f"{label} has non-passing focal_answer_audit")
        if "exclusion_override" in row:
            override = row["exclusion_override"]
            if not isinstance(override, str) or not override:
                raise ValueError(f"{label} exclusion_override must be a non-empty string")
        if "override_rationale" in row:
            if "exclusion_override" not in row:
                raise ValueError(f"{label} override_rationale requires exclusion_override")
            if not isinstance(row["override_rationale"], str):
                raise ValueError(f"{label} override_rationale must be a string")
        if any_rank:
            if "rank" not in row or isinstance(row["rank"], bool) or not isinstance(row["rank"], int):
                raise ValueError("If any curation row has rank, every row must have an integer rank")
            if row["rank"] < 1:
                raise ValueError(f"{label} rank must be positive")
            ranks.setdefault((task, status), []).append(row["rank"])
        normalized = {
            "source_id": source_id,
            "selected_task": task,
            "selection_status": status,
        }
        if "dataset" in row:
            normalized["dataset"] = row["dataset"]
        if "exclusion_override" in row:
            normalized["exclusion_override"] = row["exclusion_override"]
        if "override_rationale" in row:
            normalized["override_rationale"] = row["override_rationale"]
        (primaries if status == PRIMARY_STATUS else backups).append(normalized)

    primary_counts = Counter(row["selected_task"] for row in primaries)
    expected = Counter({task: 10 for task in selector.TASKS})
    if primary_counts != expected:
        raise ValueError(
            "Curation must contain exactly 10 primary sources per task; "
            f"observed={dict(sorted(primary_counts.items()))}"
        )
    if any_rank:
        for task in selector.TASKS:
            observed = sorted(ranks.get((task, PRIMARY_STATUS), []))
            if observed != list(range(1, 11)):
                raise ValueError(f"Primary ranks for {task} must be exactly 1 through 10")
        for task in selector.TASKS:
            observed = sorted(ranks.get((task, BACKUP_STATUS), []))
            if observed and observed != list(range(1, len(observed) + 1)):
                raise ValueError(f"Backup ranks for {task} must be contiguous from 1")
    return primaries, backups


def _normalize_dataset_plan(
    plan: dict[str, Any], *, minimum_per_task_dataset: int
) -> dict[str, dict[str, int]]:
    """Validate a task-level plan with 10/task and a configurable source floor."""
    if (
        isinstance(minimum_per_task_dataset, bool)
        or not isinstance(minimum_per_task_dataset, int)
        or minimum_per_task_dataset < DEFAULT_MIN_PER_TASK_DATASET
        or minimum_per_task_dataset > 5
    ):
        raise ValueError("minimum_per_task_dataset must be an integer from 0 through 5")
    if "by_task" in plan:
        plan = plan["by_task"]
    if not isinstance(plan, dict) or set(plan) != set(selector.TASKS):
        raise ValueError("Dataset plan must contain exactly the five challenge tasks")
    normalized: dict[str, dict[str, int]] = {}
    for task in selector.TASKS:
        counts = plan[task]
        if not isinstance(counts, dict) or set(counts) != set(selector.DATASETS):
            raise ValueError(f"Dataset plan for {task} must contain exactly both source datasets")
        task_counts: dict[str, int] = {}
        for dataset in selector.DATASETS:
            count = counts[dataset]
            if isinstance(count, bool) or not isinstance(count, int):
                raise ValueError(f"Dataset plan count for {task}/{dataset} must be an integer")
            if count < minimum_per_task_dataset:
                raise ValueError(
                    f"Dataset underrepresentation for {task}: {dataset} has {count}, "
                    f"minimum is {minimum_per_task_dataset}"
                )
            task_counts[dataset] = count
        if sum(task_counts.values()) != 10:
            raise ValueError(f"Dataset plan for {task} must sum to 10")
        normalized[task] = task_counts
    return normalized


def _observed_dataset_plan(rows: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    return {
        task: {
            dataset: sum(row["task"] == task and row["dataset"] == dataset for row in rows)
            for dataset in selector.DATASETS
        }
        for task in selector.TASKS
    }


def _validate_unique(rows: list[dict[str, Any]], label: str) -> None:
    for field in IDENTITY_FIELDS:
        counts = Counter(row[field] for row in rows)
        duplicates = sorted(str(value) for value, count in counts.items() if count > 1)
        if duplicates:
            raise ValueError(f"{label} contains duplicate {field}: {duplicates[0]}")


def _resolve_curation_rows(
    records: list[dict[str, Any]],
    candidate_index: dict[str, dict[str, Any]],
    development_values: dict[str, set[Any]],
    *,
    selected: bool,
) -> list[dict[str, Any]]:
    resolved: list[dict[str, Any]] = []
    for record in records:
        source_id = record["source_id"]
        if source_id not in candidate_index:
            raise ValueError(f"Curated source_id is absent from the full candidate pool: {source_id}")
        row = _prepared_source(
            candidate_index[source_id],
            f"curated candidate {source_id}",
            apply_exclusion=True,
            exclusion_override=record.get("exclusion_override"),
        )
        for field in IDENTITY_FIELDS:
            if row[field] in development_values[field]:
                raise ValueError(f"Curated candidate {source_id} overlaps development on {field}")
        if "dataset" in record and record["dataset"] != row["dataset"]:
            raise ValueError(f"Curation dataset disagrees with candidate pool for {source_id}")
        if selected:
            row["task"] = record["selected_task"]
        if "override_rationale" in record:
            row["override_rationale"] = record["override_rationale"]
        resolved.append(row)
    _validate_unique(resolved, "Curated primary set" if selected else "Curated backup set")
    return resolved


def assign_conditions(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Assign conditions by frozen seed and source ID, independent of curation order."""
    counts = Counter(row["task"] for row in rows)
    if counts != Counter({task: 10 for task in selector.TASKS}):
        raise ValueError("Condition assignment requires exactly 10 primary sources per task")
    assigned: list[dict[str, Any]] = []
    for task in selector.TASKS:
        pool = sorted(
            (row.copy() for row in rows if row["task"] == task),
            key=lambda row: (selector._stable_key(row), row["source_id"]),
        )
        for index, family in enumerate(selector.CUE_FAMILIES):
            for direction, row in zip(
                selector.LENGTH_DIRECTIONS, pool[index * 2:index * 2 + 2]
            ):
                row["cue_family"] = family
                row["length_direction"] = direction
                assigned.append(row)
    return assigned


def validate_final_selection(
    rows: list[dict[str, Any]],
    declared_plan: dict[str, dict[str, int]],
    *,
    minimum_per_task_dataset: int,
) -> None:
    if len(rows) != 50:
        raise ValueError(f"Expected exactly 50 assigned sources; found {len(rows)}")
    _validate_unique(rows, "Final challenge selection")
    task_counts = Counter(row["task"] for row in rows)
    if task_counts != Counter({task: 10 for task in selector.TASKS}):
        raise ValueError(f"Task quotas not met: {dict(task_counts)}")
    if any(row["dataset"] not in selector.DATASETS for row in rows):
        raise ValueError("Final selection contains an unsupported dataset")
    combinations = Counter((row["task"], row["cue_family"]) for row in rows)
    if combinations != Counter(
        {(task, family): 2 for task in selector.TASKS for family in selector.CUE_FAMILIES}
    ):
        raise ValueError("Each task x cue-family cell must contain exactly two sources")
    directions = Counter(
        (row["task"], row["cue_family"], row["length_direction"]) for row in rows
    )
    if directions != Counter({
        (task, family, direction): 1
        for task in selector.TASKS
        for family in selector.CUE_FAMILIES
        for direction in selector.LENGTH_DIRECTIONS
    }):
        raise ValueError("Each task x cue-family cell must have one source per length direction")
    observed = _observed_dataset_plan(rows)
    validated_observed = _normalize_dataset_plan(
        observed, minimum_per_task_dataset=minimum_per_task_dataset
    )
    if validated_observed != declared_plan:
        raise ValueError(
            "Primary source dataset counts do not match the declared task-level plan; "
            f"declared={declared_plan}, observed={validated_observed}"
        )


def _public_records(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{key: row[key] for key in PUBLIC_SOURCE_KEYS} for row in rows]


def _count_manifest(rows: list[dict[str, Any]]) -> dict[str, Any]:
    cell_counts = Counter(
        (row["task"], row["cue_family"], row["length_direction"]) for row in rows
    )
    dataset_counts = Counter(row["dataset"] for row in rows)
    return {
        "by_dataset": dict(sorted(dataset_counts.items())),
        "dataset_balance_exact_25_each": dataset_counts == Counter(
            {dataset: 25 for dataset in selector.DATASETS}
        ),
        "by_task": dict(sorted(Counter(row["task"] for row in rows).items())),
        "by_task_dataset": _observed_dataset_plan(rows),
        "by_length_bin": dict(sorted(Counter(row["length_bin"] for row in rows).items())),
        "by_cue_family": dict(sorted(Counter(row["cue_family"] for row in rows).items())),
        "by_length_direction": dict(
            sorted(Counter(row["length_direction"] for row in rows).items())
        ),
        "task_family_direction_counts": [
            {
                "task": task,
                "cue_family": family,
                "length_direction": direction,
                "count": cell_counts[(task, family, direction)],
            }
            for task in selector.TASKS
            for family in selector.CUE_FAMILIES
            for direction in selector.LENGTH_DIRECTIONS
        ],
    }


def build_artifacts(
    candidates: list[dict[str, Any]],
    development_rows: list[dict[str, Any]],
    curation: list[dict[str, Any]],
    *,
    dataset_plan: dict[str, Any] | None = None,
    minimum_per_task_dataset: int = DEFAULT_MIN_PER_TASK_DATASET,
) -> dict[str, Any]:
    """Build fully validated private/public artifacts without writing any files."""
    if len(development_rows) != 50:
        raise ValueError(f"Expected exactly 50 development sources; found {len(development_rows)}")
    development = [
        _prepared_source(row, f"development row {index}", apply_exclusion=False)
        for index, row in enumerate(development_rows, 1)
    ]
    _validate_unique(development, "Development source set")
    development_values = {
        field: {row[field] for row in development} for field in IDENTITY_FIELDS
    }

    candidate_index = _index_candidates(candidates)
    primary_records, backup_records = _normalize_curation(curation)
    primaries = _resolve_curation_rows(
        primary_records, candidate_index, development_values, selected=True
    )
    # Backups are not written, but validating them now prevents a nominal reserve
    # from bypassing the same score-free eligibility and independence contract.
    backups = _resolve_curation_rows(
        backup_records, candidate_index, development_values, selected=False
    )
    combined_curated = primaries + backups
    _validate_unique(combined_curated, "Full curated primary/backup set")

    if dataset_plan is None:
        declared_plan = _normalize_dataset_plan(
            _observed_dataset_plan(primaries),
            minimum_per_task_dataset=minimum_per_task_dataset,
        )
        plan_source = "curation_primary_rows"
    else:
        declared_plan = _normalize_dataset_plan(
            dataset_plan, minimum_per_task_dataset=minimum_per_task_dataset
        )
        plan_source = "explicit_dataset_plan"

    assigned = assign_conditions(primaries)
    assigned.sort(
        key=lambda row: (
            selector.TASKS.index(row["task"]),
            selector.CUE_FAMILIES.index(row["cue_family"]),
            selector.LENGTH_DIRECTIONS.index(row["length_direction"]),
        )
    )
    validate_final_selection(
        assigned,
        declared_plan,
        minimum_per_task_dataset=minimum_per_task_dataset,
    )

    private_rows = []
    for row in assigned:
        private_row = {key: row[key] for key in PRIVATE_SOURCE_KEYS}
        for key in ("exclusion_override", "override_rationale"):
            if key in row:
                private_row[key] = row[key]
        private_rows.append(private_row)
    rewrite_rows = {
        task: [
            {key: row[key] for key in REWRITE_INPUT_KEYS}
            for row in assigned
            if row["task"] == task
        ]
        for task in selector.TASKS
    }
    private_dump = _dump_jsonl(private_rows)
    rewrite_dumps = {task: _dump_jsonl(rows) for task, rows in rewrite_rows.items()}
    override_reason_counts = dict(
        sorted(Counter(
            row["exclusion_override"] for row in assigned if "exclusion_override" in row
        ).items())
    )
    override_count = sum(override_reason_counts.values())

    manifest: dict[str, Any] = {
        "selection_version": SELECTION_VERSION,
        "seed": selector.SEED,
        "selection_method": (
            "manual score-free source curation followed by deterministic seeded "
            "cue-family and length-direction assignment"
        ),
        "source_count": len(assigned),
        "candidate_pool_source_count": len(candidates),
        "development_source_count": len(development),
        "curation_primary_count": len(primary_records),
        "curation_backup_count": len(backup_records),
        "dataset_plan_source": plan_source,
        "declared_by_task_dataset": declared_plan,
        "minimum_per_task_dataset": minimum_per_task_dataset,
        "existing_exclusion_rules_validated": True,
        "exclusion_override_count": override_count,
        "exclusion_override_reason_counts": override_reason_counts,
        "contains_override_rationale": False,
        "development_overlap_fields_validated": IDENTITY_FIELDS,
        "condition_assignment_uses_curation_order_or_rationale": False,
        "focal_answer_applicability_required": True,
        "semantic_source_quality_status": "agent_audited_development_qa_not_human_validation",
        "human_validation": False,
        "score_or_activation_used": False,
        "model_inference_used": False,
        "contains_source_text": False,
        "contains_curation_rationale": False,
        "replacement_freeze_record": PUBLIC_FREEZE_RECORD,
        "private_output_sha256": {
            "challenge_sources_50.jsonl": _sha256_text(private_dump),
            "rewrite_inputs": {
                task: _sha256_text(rewrite_dumps[task]) for task in selector.TASKS
            },
        },
        **_count_manifest(assigned),
        "source_records": _public_records(assigned),
    }
    manifest_dump = _dump_json(manifest)
    freeze_record = {
        "record_version": 1,
        "stage": "pre_activation",
        "action": "replace_and_freeze_full_challenge_source_inventory",
        "selection_version": SELECTION_VERSION,
        "seed": selector.SEED,
        "replacement_scope_source_count": 50,
        "primary_source_count": len(assigned),
        "backup_source_count_validated_not_frozen": len(backups),
        "condition_assignment": "sha256(seed:source_id), then five cue families x two directions",
        "condition_assignment_uses_curation_order_or_rationale": False,
        "declared_by_task_dataset": declared_plan,
        "overall_dataset_counts": dict(
            sorted(Counter(row["dataset"] for row in assigned).items())
        ),
        "dataset_balance_exact_25_each": Counter(row["dataset"] for row in assigned)
        == Counter({dataset: 25 for dataset in selector.DATASETS}),
        "minimum_per_task_dataset": minimum_per_task_dataset,
        "focal_answer_applicability_required": True,
        "exclusion_override_count": override_count,
        "exclusion_override_reason_counts": override_reason_counts,
        "contains_override_rationale": False,
        "semantic_source_quality_status": "agent_audited_development_qa_not_human_validation",
        "human_validation": False,
        "score_or_activation_used": False,
        "model_inference_used": False,
        "contains_source_text": False,
        "contains_curation_rationale": False,
        "selection_manifest_sha256": _sha256_text(manifest_dump),
        "private_output_sha256": manifest["private_output_sha256"],
        "frozen_source_records": _public_records(assigned),
    }
    return {
        "assigned_rows": assigned,
        "private_rows": private_rows,
        "rewrite_rows": rewrite_rows,
        "manifest": manifest,
        "freeze_record": freeze_record,
        "texts": {
            "challenge_sources_50.jsonl": private_dump,
            **{
                f"rewrite_input_{task}.jsonl": rewrite_dumps[task]
                for task in selector.TASKS
            },
            "challenge_selection_manifest.json": manifest_dump,
            "curated_source_replacement_freeze.json": _dump_json(freeze_record),
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
    private_output_dir: Path,
    manifest_output: Path,
    freeze_record_output: Path,
    protected_inputs: Iterable[Path] = (),
) -> list[Path]:
    """Write validated outputs atomically per file, refusing input/output aliasing."""
    texts = artifacts["texts"]
    targets = {
        private_output_dir / "challenge_sources_50.jsonl": texts["challenge_sources_50.jsonl"],
        **{
            private_output_dir / f"rewrite_input_{task}.jsonl": texts[f"rewrite_input_{task}.jsonl"]
            for task in selector.TASKS
        },
        manifest_output: texts["challenge_selection_manifest.json"],
        freeze_record_output: texts["curated_source_replacement_freeze.json"],
    }
    resolved_targets = [path.resolve() for path in targets]
    if len(set(resolved_targets)) != len(resolved_targets):
        raise ValueError("Output paths must be distinct")
    protected = {path.resolve() for path in protected_inputs}
    collisions = sorted(str(path) for path in set(resolved_targets) & protected)
    if collisions:
        raise ValueError(f"Refusing to overwrite an input file: {collisions[0]}")
    for path, content in targets.items():
        _atomic_write_text(path, content)
    return list(targets)


def _load_dataset_plan(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("Dataset plan JSON must be an object")
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--curation-jsonl",
        type=Path,
        action="append",
        required=True,
        help=(
            "Private manual curation JSONL; repeat the flag to join separately audited "
            "files in memory. At least one explicit input is always required."
        ),
    )
    parser.add_argument("--candidates-jsonl", type=Path, default=selector.CANDIDATES)
    parser.add_argument("--development-jsonl", type=Path, default=selector.CURRENT)
    parser.add_argument(
        "--dataset-plan-json",
        type=Path,
        help=(
            "Optional declared task-level dataset plan. If omitted, the primary curation "
            "rows define the plan; either form must satisfy 10/task and the configured per-dataset floor."
        ),
    )
    parser.add_argument(
        "--minimum-per-task-dataset",
        type=int,
        default=DEFAULT_MIN_PER_TASK_DATASET,
        help="Minimum primary sources from each dataset in every task (default: 0)",
    )
    parser.add_argument("--private-output-dir", type=Path, default=selector.PRIVATE)
    parser.add_argument(
        "--manifest-output",
        type=Path,
        default=selector.CHALLENGE / "manifests" / "challenge_selection_manifest.json",
    )
    parser.add_argument(
        "--freeze-record-output",
        type=Path,
        default=selector.CHALLENGE / PUBLIC_FREEZE_RECORD,
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write outputs after validation. Omit for a no-write validation run.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    candidates = load_jsonl(args.candidates_jsonl, "candidate pool")
    development = load_jsonl(args.development_jsonl, "development source")
    curation = [
        row
        for path in args.curation_jsonl
        for row in load_jsonl(path, f"curation ({path})")
    ]
    artifacts = build_artifacts(
        candidates,
        development,
        curation,
        dataset_plan=_load_dataset_plan(args.dataset_plan_json),
        minimum_per_task_dataset=args.minimum_per_task_dataset,
    )
    written: list[Path] = []
    if args.apply:
        inputs = [args.candidates_jsonl, args.development_jsonl, *args.curation_jsonl]
        if args.dataset_plan_json is not None:
            inputs.append(args.dataset_plan_json)
        written = write_artifacts(
            artifacts,
            private_output_dir=args.private_output_dir,
            manifest_output=args.manifest_output,
            freeze_record_output=args.freeze_record_output,
            protected_inputs=inputs,
        )
    manifest = artifacts["manifest"]
    print(
        json.dumps(
            {
                "validated": True,
                "applied": args.apply,
                "written_file_count": len(written),
                "source_count": manifest["source_count"],
                "by_dataset": manifest["by_dataset"],
                "by_task": manifest["by_task"],
                "by_task_dataset": manifest["by_task_dataset"],
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
