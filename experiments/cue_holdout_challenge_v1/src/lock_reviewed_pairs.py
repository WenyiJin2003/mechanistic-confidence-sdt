"""Lock the 50-pair challenge only after two complete blinded reviews pass.

The rewrite JSONL must contain complete text rows plus a successful validator
marker (validation_status='pass', or an empty automatic_flags/validation_flags
list). The mapping is private output from prepare_blind_review.py. Reviewer
JSONL rows contain only blind_id, content_preservation, stronger_commitment,
formatting_mismatch, shortcut_concern, and optional notes. Reviewer type is
supplied separately on the CLI as agent or human and is never inferred.

This gate performs no model scoring or inference and does not claim semantic
equivalence beyond the recorded reviewer decisions.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

import select_challenge_sources as selector


CHALLENGE = Path(__file__).resolve().parents[1]
PRIVATE = CHALLENGE / "private_data"
TASKS = (
    "factual_explanation", "math_logic", "programming",
    "comparison_analysis", "summary_judgment",
)
CUE_FAMILIES = (
    "embedded_stance_predicate", "modal_force_scope", "compositional_polarity",
    "discourse_level_calibration", "contrastive_commitment",
)
LENGTH_DIRECTIONS = ("confident_longer", "hedged_longer")
REWRITE_REQUIRED = {
    "source_id", "dataset", "task", "cue_family", "length_direction", "prompt",
    "original_response", "confident_response", "hedged_response",
    "original_response_sha256",
}
MAPPING_REQUIRED = {
    "blind_id", "source_id", "task", "cue_family", "intended_length_direction",
    "a_role", "b_role", "original_response_sha256",
    "confident_response_sha256", "hedged_response_sha256",
}
REVIEW_REQUIRED = {
    "blind_id", "content_preservation", "stronger_commitment",
    "formatting_mismatch", "shortcut_concern",
}
REVIEW_ALLOWED = REVIEW_REQUIRED | {"notes"}
REVIEW_VALUES = {
    "content_preservation": {"pass", "fail", "uncertain"},
    "stronger_commitment": {"A", "B", "tie", "uncertain"},
    "formatting_mismatch": {"no", "yes", "uncertain"},
    # minor means a noted concern that does not require repair.
    "shortcut_concern": {"none", "minor", "repair", "uncertain"},
}


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_text(value: str) -> str:
    return sha256_bytes(value.encode("utf-8"))


def normalized_prompt_sha256(prompt: str) -> str:
    return sha256_text(" ".join(prompt.casefold().split()))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
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


def _dump_jsonl(rows: Iterable[dict[str, Any]]) -> str:
    return "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows)


def _index(rows: list[dict[str, Any]], key: str) -> tuple[dict[str, dict[str, Any]], Counter[str]]:
    indexed: dict[str, dict[str, Any]] = {}
    counts: Counter[str] = Counter()
    for row in rows:
        value = row.get(key)
        identifier = str(value) if value is not None else ""
        counts[identifier] += 1
        if identifier and identifier not in indexed:
            indexed[identifier] = row
    return indexed, counts


def _required_missing(row: dict[str, Any], required: set[str]) -> list[str]:
    return sorted(key for key in required if key not in row)


def _safe_label(value: Any) -> str:
    return value if isinstance(value, str) and value else "<invalid-or-missing>"


def _add_issue(issues: dict[tuple[str, str], set[str]], blind_id: Any,
               source_id: Any, reason: str) -> None:
    blind_key = str(blind_id) if blind_id not in (None, "") else ""
    source_key = str(source_id) if source_id not in (None, "") else ""
    issues.setdefault((blind_key, source_key), set()).add(reason)


def _remediation_rows(issues: dict[tuple[str, str], set[str]]) -> list[dict[str, Any]]:
    return [
        {"blind_id": blind_id or None, "source_id": source_id or None,
         "reasons": sorted(reasons)}
        for (blind_id, source_id), reasons in sorted(issues.items())
    ]


def _pair_counts(rows: list[dict[str, Any]]) -> dict[str, Any]:
    datasets = Counter(_safe_label(row.get("dataset")) for row in rows)
    tasks = Counter(_safe_label(row.get("task")) for row in rows)
    families = Counter(_safe_label(row.get("cue_family")) for row in rows)
    directions = Counter(_safe_label(row.get("length_direction")) for row in rows)
    cells = Counter((_safe_label(row.get("task")), _safe_label(row.get("cue_family"))) for row in rows)
    return {
        "pairs": len(rows),
        "datasets": dict(sorted(datasets.items())),
        "tasks": dict(sorted(tasks.items())),
        "cue_families": dict(sorted(families.items())),
        "length_directions": dict(sorted(directions.items())),
        "task_family_cells": {
            f"{task}|{family}": cells[(task, family)]
            for task in TASKS for family in CUE_FAMILIES
        },
    }


def _check_allocation(rows: list[dict[str, Any]], mapping_by_source: dict[str, dict[str, Any]],
                      issues: dict[tuple[str, str], set[str]]) -> dict[str, Any]:
    counts = _pair_counts(rows)
    sources = [str(row.get("source_id", "")) for row in rows]
    duplicate_sources = {source for source, count in Counter(sources).items() if source and count > 1}
    if len(rows) != 50:
        _add_issue(issues, None, None, f"rewrite_row_count_not_50:{len(rows)}")
    for source_id in duplicate_sources:
        mapping = mapping_by_source.get(source_id, {})
        _add_issue(issues, mapping.get("blind_id"), source_id, "duplicate_source_id")
    if len(set(sources) - {""}) != 50:
        _add_issue(issues, None, None, "unique_source_count_not_50")

    for task in TASKS:
        if counts["tasks"].get(task, 0) != 10:
            for row in rows:
                if row.get("task") == task:
                    _add_issue(issues, mapping_by_source.get(str(row.get("source_id", "")), {}).get("blind_id"),
                               row.get("source_id"), f"task_count_not_10:{task}")
            _add_issue(issues, None, None, f"task_count_not_10:{task}")
    for family in CUE_FAMILIES:
        if counts["cue_families"].get(family, 0) != 10:
            for row in rows:
                if row.get("cue_family") == family:
                    _add_issue(issues, mapping_by_source.get(str(row.get("source_id", "")), {}).get("blind_id"),
                               row.get("source_id"), f"cue_family_count_not_10:{family}")
            _add_issue(issues, None, None, f"cue_family_count_not_10:{family}")
    for task in TASKS:
        for family in CUE_FAMILIES:
            cell_key = f"{task}|{family}"
            if counts["task_family_cells"][cell_key] != 2:
                for row in rows:
                    if row.get("task") == task and row.get("cue_family") == family:
                        _add_issue(issues, mapping_by_source.get(str(row.get("source_id", "")), {}).get("blind_id"),
                                   row.get("source_id"), f"task_family_cell_not_2:{task}:{family}")
                _add_issue(issues, None, None, f"task_family_cell_not_2:{task}:{family}")
    for direction in LENGTH_DIRECTIONS:
        if counts["length_directions"].get(direction, 0) != 25:
            for row in rows:
                if row.get("length_direction") == direction:
                    _add_issue(issues, mapping_by_source.get(str(row.get("source_id", "")), {}).get("blind_id"),
                               row.get("source_id"), f"length_direction_count_not_25:{direction}")
            _add_issue(issues, None, None, f"length_direction_count_not_25:{direction}")
    for row in rows:
        source_id = str(row.get("source_id", ""))
        mapping = mapping_by_source.get(source_id, {})
        if row.get("task") not in TASKS:
            _add_issue(issues, mapping.get("blind_id"), source_id, "unknown_task")
        if row.get("dataset") not in selector.DATASETS:
            _add_issue(issues, mapping.get("blind_id"), source_id, "unknown_dataset")
        if row.get("cue_family") not in CUE_FAMILIES:
            _add_issue(issues, mapping.get("blind_id"), source_id, "unknown_cue_family")
        if row.get("length_direction") not in LENGTH_DIRECTIONS:
            _add_issue(issues, mapping.get("blind_id"), source_id, "unknown_length_direction")
    return counts


def _check_rewrite_validation(row: dict[str, Any], blind_id: str | None,
                              issues: dict[tuple[str, str], set[str]]) -> None:
    source_id = row.get("source_id")
    status = row.get("validation_status")
    marker_present = status is not None or any(key in row for key in ("automatic_flags", "validation_flags"))
    if not marker_present:
        _add_issue(issues, blind_id, source_id, "rewrite_not_marked_validated")
    if status is not None and status != "pass":
        _add_issue(issues, blind_id, source_id, f"rewrite_validation_status_not_pass:{status}")
    for key in ("automatic_flags", "validation_flags", "flags"):
        flags = row.get(key)
        if flags:
            _add_issue(issues, blind_id, source_id, f"rewrite_has_validation_flags:{key}")


def _reviewer_issues(decisions: list[dict[str, Any]], reviewer_number: int,
                     mapping_by_blind: dict[str, dict[str, Any]],
                     reviewer_type: str,
                     issues: dict[tuple[str, str], set[str]]) -> dict[str, dict[str, Any]]:
    indexed, counts = _index(decisions, "blind_id")
    source_by_blind = mapping_by_blind
    if len(decisions) != 50:
        _add_issue(issues, None, None, f"reviewer_{reviewer_number}_row_count_not_50:{len(decisions)}")
    for blind_id, count in counts.items():
        if not blind_id:
            _add_issue(issues, None, None, f"reviewer_{reviewer_number}_blind_id_missing")
        elif count > 1:
            mapping = source_by_blind.get(blind_id, {})
            _add_issue(issues, blind_id, mapping.get("source_id"), f"reviewer_{reviewer_number}_duplicate_blind_id")
        elif blind_id not in source_by_blind:
            _add_issue(issues, blind_id, None, f"reviewer_{reviewer_number}_unknown_blind_id")
    for blind_id, mapping in source_by_blind.items():
        if counts.get(blind_id, 0) == 0:
            _add_issue(issues, blind_id, mapping.get("source_id"), f"reviewer_{reviewer_number}_decision_missing")

    for blind_id, row in indexed.items():
        mapping = source_by_blind.get(blind_id)
        if mapping is None:
            continue
        source_id = mapping.get("source_id")
        extra = set(row) - REVIEW_ALLOWED
        missing = REVIEW_REQUIRED - set(row)
        if extra:
            _add_issue(issues, blind_id, source_id,
                       f"reviewer_{reviewer_number}_unexpected_fields:{','.join(sorted(extra))}")
        if missing:
            _add_issue(issues, blind_id, source_id,
                       f"reviewer_{reviewer_number}_missing_fields:{','.join(sorted(missing))}")
        if "notes" in row and not isinstance(row["notes"], str):
            _add_issue(issues, blind_id, source_id, f"reviewer_{reviewer_number}_notes_not_string")
        for field, allowed in REVIEW_VALUES.items():
            value = row.get(field)
            if not isinstance(value, str) or value not in allowed:
                _add_issue(issues, blind_id, source_id,
                           f"reviewer_{reviewer_number}_invalid_{field}")

        if row.get("content_preservation") != "pass":
            _add_issue(issues, blind_id, source_id, f"reviewer_{reviewer_number}_content_not_pass")
        if row.get("formatting_mismatch") != "no":
            _add_issue(issues, blind_id, source_id, f"reviewer_{reviewer_number}_formatting_mismatch_or_unclear")
        if row.get("shortcut_concern") in ("repair", "uncertain"):
            _add_issue(issues, blind_id, source_id, f"reviewer_{reviewer_number}_shortcut_requires_resolution")
        expected = "A" if mapping.get("a_role") == "confident" else "B"
        if not isinstance(mapping.get("a_role"), str) or mapping.get("a_role") not in {"confident", "hedged"} or mapping.get("b_role") != (
                "hedged" if mapping.get("a_role") == "confident" else "confident"):
            _add_issue(issues, blind_id, source_id, "mapping_roles_invalid")
        elif row.get("stronger_commitment") != expected:
            _add_issue(issues, blind_id, source_id,
                       f"reviewer_{reviewer_number}_stronger_commitment_wrong_or_unclear")
    return indexed


def evaluate_lock(rewrite_rows: list[dict[str, Any]], mapping_rows: list[dict[str, Any]],
                  reviewer1_rows: list[dict[str, Any]], reviewer2_rows: list[dict[str, Any]],
                  reviewer_types: tuple[str, str],
                  selection_manifest: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return lock rows or a private remediation list; never write files here."""
    if len(reviewer_types) != 2 or any(value not in {"agent", "human"} for value in reviewer_types):
        raise ValueError("Exactly two reviewer types, each agent or human, are required")
    issues: dict[tuple[str, str], set[str]] = {}
    if reviewer_types[0] != reviewer_types[1]:
        _add_issue(issues, None, None, "mixed_reviewer_types_not_supported")
    rewrite_by_source, rewrite_counts = _index(rewrite_rows, "source_id")
    mapping_by_source, mapping_source_counts = _index(mapping_rows, "source_id")
    mapping_by_blind, mapping_blind_counts = _index(mapping_rows, "blind_id")

    selected_records = selection_manifest.get("source_records", []) if isinstance(selection_manifest, dict) else []
    selected_by_source, selected_counts = _index(selected_records, "source_id")
    if (not isinstance(selection_manifest, dict) or selection_manifest.get("source_count") != 50
            or len(selected_records) != 50):
        _add_issue(issues, None, None, "selection_manifest_not_exactly_50")
    if any(count > 1 for count in selected_counts.values()):
        for source_id, count in selected_counts.items():
            if source_id and count > 1:
                _add_issue(issues, mapping_by_source.get(source_id, {}).get("blind_id"), source_id,
                           "duplicate_selection_source_id")

    if len(rewrite_rows) != 50:
        _add_issue(issues, None, None, f"rewrite_row_count_not_50:{len(rewrite_rows)}")
    if len(mapping_rows) != 50:
        _add_issue(issues, None, None, f"mapping_row_count_not_50:{len(mapping_rows)}")
    for source_id, count in rewrite_counts.items():
        if not source_id:
            _add_issue(issues, None, None, "rewrite_source_id_missing")
        elif count > 1:
            mapping = mapping_by_source.get(source_id, {})
            _add_issue(issues, mapping.get("blind_id"), source_id, "duplicate_rewrite_source_id")
    for source_id, count in mapping_source_counts.items():
        if not source_id:
            _add_issue(issues, None, None, "mapping_source_id_missing")
        elif count > 1:
            _add_issue(issues, mapping_by_source.get(source_id, {}).get("blind_id"), source_id,
                       "duplicate_mapping_source_id")
    for blind_id, count in mapping_blind_counts.items():
        if not blind_id:
            _add_issue(issues, None, None, "mapping_blind_id_missing")
        elif count > 1:
            _add_issue(issues, blind_id, mapping_by_blind.get(blind_id, {}).get("source_id"),
                       "duplicate_mapping_blind_id")

    rewrite_ids = set(rewrite_by_source)
    mapping_ids = set(mapping_by_source)
    selected_ids = set(selected_by_source)
    for source_id in mapping_ids - rewrite_ids:
        mapping = mapping_by_source[source_id]
        _add_issue(issues, mapping.get("blind_id"), source_id, "rewrite_row_missing")
    for source_id in rewrite_ids - mapping_ids:
        _add_issue(issues, None, source_id, "rewrite_source_not_in_mapping")
    for source_id in selected_ids - rewrite_ids:
        _add_issue(issues, mapping_by_source.get(source_id, {}).get("blind_id"), source_id,
                   "selection_source_missing_from_rewrites")
    for source_id in rewrite_ids - selected_ids:
        _add_issue(issues, mapping_by_source.get(source_id, {}).get("blind_id"), source_id,
                   "rewrite_source_not_in_selection_manifest")

    for source_id, row in rewrite_by_source.items():
        mapping = mapping_by_source.get(source_id)
        blind_id = mapping.get("blind_id") if mapping else None
        missing = _required_missing(row, REWRITE_REQUIRED)
        if missing:
            _add_issue(issues, blind_id, source_id, f"rewrite_fields_missing:{','.join(missing)}")
        _check_rewrite_validation(row, blind_id, issues)
        if mapping:
            for rewrite_key, mapping_key in (
                ("task", "task"), ("cue_family", "cue_family"),
                ("length_direction", "intended_length_direction"),
                ("original_response_sha256", "original_response_sha256"),
            ):
                if row.get(rewrite_key) != mapping.get(mapping_key):
                    _add_issue(issues, blind_id, source_id, f"rewrite_mapping_mismatch:{rewrite_key}")
            for field in ("prompt", "original_response", "confident_response", "hedged_response"):
                if not isinstance(row.get(field), str) or not row[field].strip():
                    _add_issue(issues, blind_id, source_id, f"rewrite_text_missing:{field}")
            if (isinstance(row.get("original_response"), str) and
                    isinstance(row.get("confident_response"), str) and
                    row["confident_response"] == row["original_response"]):
                _add_issue(issues, blind_id, source_id, "confident_response_verbatim_source")
            if (isinstance(row.get("original_response"), str) and
                    isinstance(row.get("hedged_response"), str) and
                    row["hedged_response"] == row["original_response"]):
                _add_issue(issues, blind_id, source_id, "hedged_response_verbatim_source")
            if (isinstance(row.get("confident_response"), str) and
                    isinstance(row.get("hedged_response"), str) and
                    row["confident_response"] == row["hedged_response"]):
                _add_issue(issues, blind_id, source_id, "identical_rewrites")
            if isinstance(row.get("original_response"), str):
                digest = sha256_text(row["original_response"])
                if row.get("original_response_sha256") != digest or mapping.get("original_response_sha256") != digest:
                    _add_issue(issues, blind_id, source_id, "original_text_hash_mismatch")
            selected = selected_by_source.get(source_id)
            if selected:
                for field in ("dataset", "task", "cue_family", "length_direction", "original_response_sha256"):
                    if row.get(field) != selected.get(field):
                        _add_issue(issues, blind_id, source_id, f"rewrite_selection_mismatch:{field}")
                if isinstance(row.get("prompt"), str):
                    if selected.get("normalized_prompt_sha256") != normalized_prompt_sha256(row["prompt"]):
                        _add_issue(issues, blind_id, source_id, "normalized_prompt_hash_mismatch")
            for field, map_field in (("confident_response", "confident_response_sha256"),
                                     ("hedged_response", "hedged_response_sha256")):
                if isinstance(row.get(field), str) and mapping.get(map_field) != sha256_text(row[field]):
                    _add_issue(issues, blind_id, source_id, f"{field}_hash_mismatch")

    counts = _check_allocation(rewrite_rows, mapping_by_source, issues)

    # Verify mapping metadata and every reviewer decision against the opaque A/B map.
    for blind_id, mapping in mapping_by_blind.items():
        missing = _required_missing(mapping, MAPPING_REQUIRED)
        if missing:
            _add_issue(issues, blind_id, mapping.get("source_id"),
                       f"mapping_fields_missing:{','.join(missing)}")
        if (not isinstance(mapping.get("a_role"), str) or mapping.get("a_role") not in {"confident", "hedged"}
                or not isinstance(mapping.get("b_role"), str) or mapping.get("b_role") not in {"confident", "hedged"}):
            _add_issue(issues, blind_id, mapping.get("source_id"), "mapping_roles_invalid")
        if mapping.get("a_role") == mapping.get("b_role"):
            _add_issue(issues, blind_id, mapping.get("source_id"), "mapping_roles_not_complementary")
        source = rewrite_by_source.get(str(mapping.get("source_id", "")))
        if source:
            for field, source_field in (("task", "task"), ("cue_family", "cue_family"),
                                        ("intended_length_direction", "length_direction")):
                if mapping.get(field) != source.get(source_field):
                    _add_issue(issues, blind_id, mapping.get("source_id"), f"mapping_rewrite_mismatch:{field}")

    group_ids = [str(row.get("group_id", "")) for row in selected_records]
    group_counts = Counter(group_ids)
    for group_id, count in group_counts.items():
        if not group_id or count > 1:
            affected = [row for row in selected_records if str(row.get("group_id", "")) == group_id]
            for selected in affected:
                source_id = str(selected.get("source_id", ""))
                _add_issue(issues, mapping_by_source.get(source_id, {}).get("blind_id"), source_id,
                           "selection_group_id_missing" if not group_id else "duplicate_selection_group_id")

    for source_id, selected in selected_by_source.items():
        rewrite = rewrite_by_source.get(source_id)
        mapping = mapping_by_source.get(source_id)
        if rewrite is None or mapping is None:
            continue
        prompt = rewrite.get("prompt")
        if not isinstance(prompt, str) or not selected.get("normalized_prompt_sha256"):
            _add_issue(issues, mapping.get("blind_id"), source_id, "selection_prompt_hash_missing")
        elif selected.get("normalized_prompt_sha256") != normalized_prompt_sha256(prompt):
            _add_issue(issues, mapping.get("blind_id"), source_id, "normalized_prompt_hash_mismatch")

    reviewer1 = _reviewer_issues(reviewer1_rows, 1, mapping_by_blind, reviewer_types[0], issues)
    reviewer2 = _reviewer_issues(reviewer2_rows, 2, mapping_by_blind, reviewer_types[1], issues)

    remediation = _remediation_rows(issues)
    if remediation:
        return {"locked": False, "locked_rows": [], "remediation": remediation,
                "counts": counts, "reviewer_types": list(reviewer_types)}

    locked_rows: list[dict[str, Any]] = []
    for source_id in sorted(rewrite_by_source):
        row = rewrite_by_source[source_id]
        mapping = mapping_by_source[source_id]
        blind_id = str(mapping["blind_id"])
        locked_rows.append({
            "source_id": source_id,
            "review_id": row.get("review_id") or f"C{len(locked_rows) + 1:03d}",
            "blind_id": blind_id,
            "group_id": selected_by_source[source_id]["group_id"],
            "normalized_prompt_sha256": selected_by_source[source_id]["normalized_prompt_sha256"],
            "dataset": row["dataset"],
            "task": row["task"],
            "cue_family": row["cue_family"],
            "length_direction": row["length_direction"],
            "prompt": row["prompt"],
            "original_response": row["original_response"],
            "confident_response": row["confident_response"],
            "hedged_response": row["hedged_response"],
            "original_response_sha256": row["original_response_sha256"],
            "confident_response_sha256": mapping["confident_response_sha256"],
            "hedged_response_sha256": mapping["hedged_response_sha256"],
            "a_role": mapping["a_role"],
            "b_role": mapping["b_role"],
            "reviewer_types": list(reviewer_types),
            "human_review": "passed" if reviewer_types == ("human", "human") else "pending",
            "scientific_status": (
                "locked_human_reviewed_transfer_evaluation" if reviewer_types == ("human", "human")
                else "development_only_not_human_validated"
            ),
            "independent_reviewer_count": 2,
            "independent_reviews_complete": True,
            "reviews_blinded": True,
            "agent_review_is_human_review": False,
            "reserved_split": "locked_challenge",
            "reviewer_decisions": [
                {"reviewer_type": reviewer_types[0], **{key: reviewer1[blind_id][key] for key in REVIEW_REQUIRED - {"blind_id"}}},
                {"reviewer_type": reviewer_types[1], **{key: reviewer2[blind_id][key] for key in REVIEW_REQUIRED - {"blind_id"}}},
            ],
        })
    return {"locked": True, "locked_rows": locked_rows, "remediation": [],
            "counts": counts, "reviewer_types": list(reviewer_types)}


def _public_manifest(outcome: dict[str, Any], locked_dump: str,
                     rewrite_paths: list[Path], mapping_path: Path,
                     reviewer_paths: tuple[Path, Path],
                     selection_manifest_path: Path) -> dict[str, Any]:
    types = outcome["reviewer_types"]
    if types == ["human", "human"]:
        review_status = "human_review_passed"
        human_review = "passed"
        scientific_status = "locked_human_reviewed_transfer_evaluation"
    elif types == ["agent", "agent"]:
        review_status = "agent_reviewed_development_only"
        human_review = "pending"
        scientific_status = "development_only_not_human_validated"
    else:
        raise ValueError("Mixed reviewer types cannot produce a lock manifest")
    reviewers = []
    for index, (reviewer_type, path) in enumerate(zip(types, reviewer_paths), 1):
        digest = sha256_bytes(path.read_bytes())
        reviewer_id = f"reviewer-{index}-{sha256_text(f'{index}:{digest}')[:12]}"
        reviewers.append({"reviewer_id": reviewer_id, "reviewer_type": reviewer_type,
                          "blinded": True, "review_status": "passed"})
    locked_bytes = locked_dump.encode("utf-8")
    source_ids = sorted(row["source_id"] for row in outcome["locked_rows"])
    return {
        "locked": True,
        "review_status": review_status,
        "scientific_status": scientific_status,
        "independent_reviewer_count": 2,
        "independent_reviews_complete": True,
        "reviews_blinded": True,
        "reviewers": reviewers,
        "human_review": human_review,
        "agent_review_is_human_review": False,
        "pair_count": len(outcome["locked_rows"]),
        "challenge_pairs_sha256": sha256_bytes(locked_bytes),
        "source_ids_sha256": sha256_text("\n".join(source_ids)),
        "selection_manifest_sha256": sha256_bytes(selection_manifest_path.read_bytes()),
        "hashes": {
            "locked_pairs_sha256": sha256_bytes(locked_bytes),
            "rewrite_inputs_sha256": [sha256_bytes(path.read_bytes()) for path in rewrite_paths],
            "blind_mapping_sha256": sha256_bytes(mapping_path.read_bytes()),
            "reviewer_decisions_sha256": [
                {"type": types[index], "sha256": sha256_bytes(path.read_bytes())}
                for index, path in enumerate(reviewer_paths)
            ],
        },
        "counts": outcome["counts"],
        "reviewer_files": 2,
        "reviewer_types": types,
        "reviewer_type_counts": dict(sorted(Counter(types).items())),
    }


def _write_private(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _inside(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rewrites", nargs="+", type=Path, required=True,
                        help="Full rewrite rows merged with successful private validation status")
    parser.add_argument("--mapping", type=Path, required=True,
                        help="Private blinded mapping JSONL")
    parser.add_argument("--selection-manifest", type=Path,
                        default=CHALLENGE / "manifests" / "challenge_selection_manifest.json",
                        help="Frozen public source-selection manifest")
    parser.add_argument("--reviewer-1", type=Path, required=True)
    parser.add_argument("--reviewer-1-type", choices=("agent", "human"), required=True)
    parser.add_argument("--reviewer-2", type=Path, required=True)
    parser.add_argument("--reviewer-2-type", choices=("agent", "human"), required=True)
    parser.add_argument("--locked-output", type=Path, default=PRIVATE / "locked_pairs_50.jsonl")
    parser.add_argument("--manifest-output", type=Path,
                        default=CHALLENGE / "manifests" / "locked_pairs_freeze_manifest.json")
    parser.add_argument("--remediation-output", type=Path,
                        default=PRIVATE / "pair_lock_remediation.jsonl")
    args = parser.parse_args(argv)

    def resolve_output(path: Path) -> Path:
        return path if path.is_absolute() else CHALLENGE / path

    locked_path = resolve_output(args.locked_output)
    manifest_path = resolve_output(args.manifest_output)
    remediation_path = resolve_output(args.remediation_output)
    if not _inside(locked_path, PRIVATE) or not _inside(remediation_path, PRIVATE):
        parser.error("locked and remediation JSONL files must stay under private_data/")
    if _inside(manifest_path, PRIVATE):
        parser.error("public freeze manifest must be outside private_data/")
    if args.reviewer_1.resolve() == args.reviewer_2.resolve():
        parser.error("the two reviewer decision inputs must be separate files")

    rewrites = [row for path in args.rewrites for row in read_jsonl(path)]
    mapping = read_jsonl(args.mapping)
    selection_manifest = json.loads(args.selection_manifest.read_text(encoding="utf-8"))
    reviewer1 = read_jsonl(args.reviewer_1)
    reviewer2 = read_jsonl(args.reviewer_2)
    types = (args.reviewer_1_type, args.reviewer_2_type)
    outcome = evaluate_lock(rewrites, mapping, reviewer1, reviewer2, types, selection_manifest)

    if not outcome["locked"]:
        _write_private(remediation_path, _dump_jsonl(outcome["remediation"]))
        print(json.dumps({"locked": False, "remediation_count": len(outcome["remediation"]),
                          "reviewer_types": types}, sort_keys=True))
        return 1
    if locked_path.exists() or manifest_path.exists():
        _write_private(remediation_path, _dump_jsonl([
            {"blind_id": None, "source_id": None, "reasons": ["lock_output_already_exists_refusing_overwrite"]}
        ]))
        print(json.dumps({"locked": False, "remediation_count": 1,
                          "reviewer_types": types}, sort_keys=True))
        return 1

    locked_dump = _dump_jsonl(outcome["locked_rows"])
    manifest = _public_manifest(outcome, locked_dump, args.rewrites, args.mapping,
                                (args.reviewer_1, args.reviewer_2), args.selection_manifest)
    _write_private(locked_path, locked_dump)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                             encoding="utf-8")
    _write_private(remediation_path, "")
    print(json.dumps({"locked": True, "pairs": len(outcome["locked_rows"]),
                      "reviewer_types": types}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
