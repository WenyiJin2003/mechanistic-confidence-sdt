#!/usr/bin/env python3
"""Build the text-free current checkpoint for factual rewrite canary v4.

This is a progress ledger, not a certification artifact. It derives counts
from validator outputs and repair manifests, verifies that the public validator
summary is an exact row-free projection of the full private report, and binds
the public result to file and pair-set hashes. It never serializes source IDs or
source/rewrite text.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / "private_data" / "rewrite_canary_v1"
RESULTS = ROOT / "results"

DEFAULT_EXECUTION = ROOT / "configs" / "rewrite_canary_v4_execution.json"
DEFAULT_INITIAL_VALIDATIONS = tuple(
    PRIVATE / f"BATCH_{index:02d}_V4_INITIAL_VALIDATION.jsonl"
    for index in range(1, 4)
)
DEFAULT_REPAIR_MANIFESTS = tuple(
    PRIVATE / f"PROMPT_BATCH_{index:02d}_LENGTH_REPAIR_V4.manifest.json"
    for index in range(1, 4)
)
DEFAULT_POST_REPAIR_VALIDATION = (
    PRIVATE / "WRITER_CANARY_12_V4_POST_REPAIR_VALIDATION.json"
)
DEFAULT_POST_REPAIR_PUBLIC_SUMMARY = (
    RESULTS / "rewrite_canary_v4_post_repair_validation_summary.json"
)
DEFAULT_POST_REPAIR_PAIRS = PRIVATE / "WRITER_CANARY_12_V4_POST_REPAIR.jsonl"
DEFAULT_POST_REPAIR_PROVENANCE = (
    PRIVATE / "WRITER_CANARY_12_V4_POST_REPAIR_PROVENANCE.json"
)
DEFAULT_OUTPUT = RESULTS / "rewrite_canary_v4_current_checkpoint.json"

EXPECTED_PAIRS = 12
EXPECTED_BATCHES = 3
EXPECTED_WRITER_MODEL = "gpt-6-luna"
EXPECTED_REASONING_EFFORT = "low"
EXPECTED_REPLACEMENT_ACTION = (
    "audit_and_freeze_profile_aware_same_dataset_replacement_rule"
)
SOURCE_RATIO_MIN = 0.85
SOURCE_RATIO_MAX = 1.15
PAIR_RATIO_MAX = 1.08
PAIR_GAP_MIN_ALLOWANCE = 5.0
PAIR_GAP_MEAN_FRACTION = 0.05


def sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_object(path: Path) -> dict[str, Any]:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected a JSON object: {path}")
    return value


def validator_rows(report: Mapping[str, Any], *, expected_count: int) -> list[dict[str, Any]]:
    rows = report.get("rows")
    if not isinstance(rows, list) or len(rows) != expected_count:
        raise ValueError(f"validator report must contain exactly {expected_count} rows")
    if report.get("pair_rows") != expected_count:
        raise ValueError("validator pair count does not match its rows")
    if report.get("audit_rows") != expected_count:
        raise ValueError("validator audit count does not match its rows")
    if report.get("global_failure_flags"):
        raise ValueError("checkpoint cannot be built from a globally invalid report")
    required = {"source_id", "mechanical_gate_pass", "failure_flags", "token_counts"}
    for row in rows:
        if not isinstance(row, dict) or not required.issubset(row):
            raise ValueError("validator row is missing required checkpoint fields")
        if not isinstance(row["source_id"], str) or not row["source_id"]:
            raise ValueError("validator source_id must be non-empty")
        if not isinstance(row["mechanical_gate_pass"], bool):
            raise ValueError("mechanical_gate_pass must be boolean")
        if not isinstance(row["failure_flags"], list):
            raise ValueError("failure_flags must be a list")
    if len({row["source_id"] for row in rows}) != expected_count:
        raise ValueError("validator report contains duplicate source IDs")
    return rows


def clean_count(rows: Sequence[Mapping[str, Any]]) -> int:
    return sum(bool(row["mechanical_gate_pass"]) for row in rows)


def final_length_repair_eligible(row: Mapping[str, Any]) -> bool:
    """Fail closed while recomputing the final length-repair exception."""
    if row["mechanical_gate_pass"]:
        return False
    if row["failure_flags"] != ["pair_token_gap_over_limit"]:
        return False
    counts = row["token_counts"]
    if not isinstance(counts, Mapping):
        return False
    source_tokens = counts.get("source")
    confident_tokens = counts.get("confident")
    hesitant_tokens = counts.get("hesitant")
    absolute_gap = counts.get("absolute_gap")
    allowed_gap = counts.get("allowed_gap")
    if any(
        isinstance(value, bool) or not isinstance(value, int) or value <= 0
        for value in (source_tokens, confident_tokens, hesitant_tokens)
    ):
        return False
    if isinstance(absolute_gap, bool) or not isinstance(absolute_gap, int):
        return False
    if (
        isinstance(allowed_gap, bool)
        or not isinstance(allowed_gap, (int, float))
        or not math.isfinite(float(allowed_gap))
    ):
        return False

    expected_gap = abs(confident_tokens - hesitant_tokens)
    pair_mean = (confident_tokens + hesitant_tokens) / 2
    expected_allowed_gap = max(
        PAIR_GAP_MIN_ALLOWANCE,
        PAIR_GAP_MEAN_FRACTION * pair_mean,
    )
    if absolute_gap != expected_gap:
        return False
    if abs(float(allowed_gap) - round(expected_allowed_gap, 6)) > 1e-9:
        return False

    length_direction = row.get("length_direction")
    direction_correct = (
        length_direction == "confident_longer"
        and confident_tokens > hesitant_tokens
    ) or (
        length_direction == "hesitant_longer"
        and hesitant_tokens > confident_tokens
    )
    if not direction_correct or counts.get("direction_correct") is not True:
        return False

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
        return False

    excess = expected_gap - expected_allowed_gap
    return 0 < excess <= 2.0


def validate_execution(execution: Mapping[str, Any]) -> dict[str, Any]:
    if execution.get("source_set_revision") != "v4":
        raise ValueError("execution metadata must target source-set revision v4")
    if execution.get("writer_model") != EXPECTED_WRITER_MODEL:
        raise ValueError("unexpected writer model")
    if execution.get("reasoning_effort") != EXPECTED_REASONING_EFFORT:
        raise ValueError("unexpected writer reasoning effort")

    initial_labels = execution.get("initial_generation", {}).get(
        "isolated_context_labels"
    )
    repair = execution.get("repair_generation", {})
    repair_labels = repair.get("isolated_context_labels")
    for name, labels in (
        ("initial", initial_labels),
        ("repair", repair_labels),
    ):
        if not isinstance(labels, list) or len(labels) != EXPECTED_BATCHES:
            raise ValueError(f"{name} generation must record three contexts")
        if len(set(labels)) != EXPECTED_BATCHES or not all(
            isinstance(label, str) and label for label in labels
        ):
            raise ValueError(f"{name} context labels must be unique non-empty strings")
    if set(initial_labels) & set(repair_labels):
        raise ValueError("initial and repair contexts must be isolated from each other")
    if repair.get("policy") != "one_full_pair_repair_for_each_initial_mechanical_failure":
        raise ValueError("unexpected repair policy")
    return {
        "writer_model": execution["writer_model"],
        "reasoning_effort": execution["reasoning_effort"],
        "initial_isolated_context_count": len(initial_labels),
        "repair_isolated_context_count": len(repair_labels),
    }


def validate_replacement_plan(
    execution: Mapping[str, Any], *, remaining_failures: int
) -> dict[str, Any]:
    plan = execution.get("replacement_plan")
    if not isinstance(plan, dict):
        raise ValueError("execution metadata must contain a replacement plan")
    expected = {
        "action": EXPECTED_REPLACEMENT_ACTION,
        "source_count": remaining_failures,
        "same_dataset_required": True,
        "preserve_preregistered_experimental_slot": True,
        "replacement_generation_authorized": False,
    }
    if plan != expected:
        raise ValueError("replacement plan does not match the current audit hold")
    return dict(plan)


def build_checkpoint(
    *,
    execution_path: Path = DEFAULT_EXECUTION,
    initial_validation_paths: Sequence[Path] = DEFAULT_INITIAL_VALIDATIONS,
    repair_manifest_paths: Sequence[Path] = DEFAULT_REPAIR_MANIFESTS,
    post_repair_validation_path: Path = DEFAULT_POST_REPAIR_VALIDATION,
    post_repair_public_summary_path: Path = DEFAULT_POST_REPAIR_PUBLIC_SUMMARY,
    post_repair_pair_path: Path = DEFAULT_POST_REPAIR_PAIRS,
    post_repair_provenance_path: Path = DEFAULT_POST_REPAIR_PROVENANCE,
) -> dict[str, Any]:
    if len(initial_validation_paths) != EXPECTED_BATCHES:
        raise ValueError("expected three initial validation summaries")
    if len(repair_manifest_paths) != EXPECTED_BATCHES:
        raise ValueError("expected three repair manifests")

    execution = read_object(execution_path)
    writer = validate_execution(execution)

    initial_reports = [read_object(path) for path in initial_validation_paths]
    initial_rows: list[dict[str, Any]] = []
    initial_bindings: list[dict[str, Any]] = []
    for path, report in zip(initial_validation_paths, initial_reports, strict=True):
        rows = validator_rows(report, expected_count=4)
        initial_rows.extend(rows)
        binding = report.get("artifact_binding")
        if not isinstance(binding, dict) or binding.get("pair_count") != 4:
            raise ValueError("initial validator is missing its four-pair binding")
        initial_bindings.append(
            {
                "artifact": Path(path).name,
                "sha256": sha256_file(path),
                "pair_count": 4,
                "pair_set_sha256": binding.get("pair_set_sha256"),
            }
        )
    if len({row["source_id"] for row in initial_rows}) != EXPECTED_PAIRS:
        raise ValueError("initial validation batches do not cover 12 unique pairs")

    initial_failed_ids = {
        row["source_id"] for row in initial_rows if not row["mechanical_gate_pass"]
    }
    repair_target_ids: set[str] = set()
    repair_bindings: list[dict[str, Any]] = []
    for path in repair_manifest_paths:
        manifest = read_object(path)
        targets = manifest.get("target_source_ids")
        if not isinstance(targets, list) or len(targets) != manifest.get("target_count"):
            raise ValueError("repair manifest target count is inconsistent")
        if not all(isinstance(value, str) and value for value in targets):
            raise ValueError("repair target IDs must be non-empty strings")
        overlap = repair_target_ids & set(targets)
        if overlap:
            raise ValueError("a pair appears in more than one repair manifest")
        repair_target_ids.update(targets)
        repair_bindings.append(
            {
                "artifact": Path(path).name,
                "sha256": sha256_file(path),
                "target_count": len(targets),
            }
        )
    if repair_target_ids != initial_failed_ids:
        raise ValueError("repair manifests must cover each initial failure exactly once")

    post_report = read_object(post_repair_validation_path)
    post_rows = validator_rows(post_report, expected_count=EXPECTED_PAIRS)
    if {row["source_id"] for row in post_rows} != {
        row["source_id"] for row in initial_rows
    }:
        raise ValueError("post-repair validation changed the source set")

    public_summary = read_object(post_repair_public_summary_path)
    row_free_report = {key: value for key, value in post_report.items() if key != "rows"}
    if public_summary != row_free_report:
        raise ValueError("public validator summary is not the exact row-free projection")

    pair_provenance = read_object(post_repair_provenance_path)
    pair_output = pair_provenance.get("output")
    if not isinstance(pair_output, dict):
        raise ValueError("post-repair pair provenance is missing its output binding")
    if pair_output.get("row_count") != EXPECTED_PAIRS:
        raise ValueError("post-repair pair provenance must bind 12 rows")
    pair_sha256 = sha256_file(post_repair_pair_path)
    if pair_output.get("sha256") != pair_sha256:
        raise ValueError("post-repair pair artifact changed after provenance was written")

    post_clean = clean_count(post_rows)
    remaining_failures = EXPECTED_PAIRS - post_clean
    eligible = sum(final_length_repair_eligible(row) for row in post_rows)
    replacement_plan = validate_replacement_plan(
        execution, remaining_failures=remaining_failures
    )
    post_binding = post_report.get("artifact_binding")
    if not isinstance(post_binding, dict) or post_binding.get("pair_count") != EXPECTED_PAIRS:
        raise ValueError("post-repair validator is missing its 12-pair binding")

    return {
        "schema_version": "factual-rewrite-canary-current-checkpoint-v1",
        "artifact_role": "current_progress_checkpoint",
        "source_set_revision": "v4",
        "checkpoint_stage": "post_initial_generation_and_one_repair_per_initial_failure",
        "writer": writer,
        "counts": {
            "source_pairs": EXPECTED_PAIRS,
            "initial_mechanically_clean": clean_count(initial_rows),
            "initial_mechanical_failures": len(initial_failed_ids),
            "repaired_pairs": len(repair_target_ids),
            "post_repair_mechanically_clean": post_clean,
            "post_repair_mechanical_failures": remaining_failures,
            "final_length_repair_eligible": eligible,
        },
        "next_action": replacement_plan,
        "authorization": {
            "activation_extraction": False,
            "probe_fitting": False,
            "scale_up_to_120_sources": False,
        },
        "human_pair_review": "pending_for_mechanically_clean_pairs",
        "private_text_committed": False,
        "artifact_bindings": {
            "execution_metadata": {
                "artifact": Path(execution_path).name,
                "sha256": sha256_file(execution_path),
            },
            "initial_validation_summaries": initial_bindings,
            "repair_manifests": repair_bindings,
            "post_repair_validator": {
                "full_artifact_sha256": sha256_file(post_repair_validation_path),
                "public_summary_sha256": sha256_file(post_repair_public_summary_path),
                "pair_count": EXPECTED_PAIRS,
                "pair_set_sha256": post_binding.get("pair_set_sha256"),
            },
            "post_repair_pair_artifact": {
                "sha256": pair_sha256,
                "pair_count": EXPECTED_PAIRS,
            },
            "post_repair_pair_provenance": {
                "sha256": sha256_file(post_repair_provenance_path),
            },
        },
        "scope_note": (
            "Mechanical data-quality progress only; this checkpoint does not "
            "establish semantic equivalence, naturalness, a confidence "
            "representation, probe performance, or a causal result."
        ),
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    checkpoint = build_checkpoint()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(checkpoint, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
