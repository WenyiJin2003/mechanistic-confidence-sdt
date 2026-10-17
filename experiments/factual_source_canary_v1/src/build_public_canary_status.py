"""Build a deterministic, text-free status report for the 12-pair canary.

The builder consumes only aggregate mechanical/shortcut summaries plus review
metadata.  It deliberately does not copy record identifiers, source text,
rewrite text, reviewer notes, or row-level decisions into public outputs.

This report is a progress ledger, not a certification step.  Even a completed
blind-review form remains ``awaiting_review_import_and_adjudication`` until a
separate, validated importer applies the preregistered review rules.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
from canary_binding import source_ids_sha256, validate_artifact_binding


BASE = Path(__file__).resolve().parents[1]
PRIVATE = (BASE / "private_data").resolve()
RESULTS = BASE / "results"
EXPECTED_PAIRS = 12
REQUIRED_BLIND_REVIEW_FIELDS = (
    "source_fidelity",
    "qualifier_preservation",
    "speaker_level_scope",
    "certainty_a",
    "certainty_b",
    "stronger_certainty",
    "naturalness_a",
    "naturalness_b",
    "formatting_mismatch",
    "shortcut_concern",
)

PASS_DECISIONS = {"accept", "approved", "pass", "passed"}
REPAIR_DECISIONS = {
    "repair",
    "requires_repair",
    "requires_source_repair",
    "rewrite",
}
REJECT_DECISIONS = {"exclude", "fail", "failed", "reject", "rejected"}
PENDING_DECISIONS = {"", "not_reviewed", "pending"}
PRE_REVIEW_SCHEMA = "factual-rewrite-model-assisted-pre-review-v1"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

BLIND_REVIEW_ENUMS = {
    "source_fidelity": {"both_preserve", "a_drift", "b_drift", "both_drift", "uncertain"},
    "qualifier_preservation": {
        "both_preserve", "a_changes", "b_changes", "both_change",
        "not_applicable", "uncertain",
    },
    "speaker_level_scope": {
        "both_speaker_level", "a_object_level_shift", "b_object_level_shift",
        "both_object_level_shift", "uncertain",
    },
    "certainty_a": {"1", "2", "3", "4", "5"},
    "certainty_b": {"1", "2", "3", "4", "5"},
    "stronger_certainty": {"a", "b", "tie", "uncertain"},
    "naturalness_a": {"natural", "minor", "unnatural", "uncertain"},
    "naturalness_b": {"natural", "minor", "unnatural", "uncertain"},
    "formatting_mismatch": {"none", "a", "b", "both", "uncertain"},
    "shortcut_concern": {"none", "a", "b", "both", "uncertain"},
}


def read_object(path: Path) -> dict[str, Any]:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected a JSON object: {path}")
    return value


def sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _inside(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def _nonnegative_int(value: Any, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError(f"{field} must be a non-negative integer")
    return value


def _optional_nonnegative_int(value: Any, field: str) -> int | None:
    if value is None:
        return None
    return _nonnegative_int(value, field)


def _count_map(value: Any, field: str) -> dict[str, int]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise ValueError(f"{field} must be an object of counts")
    result: dict[str, int] = {}
    for key, count in value.items():
        if not isinstance(key, str):
            raise ValueError(f"{field} keys must be strings")
        result[key] = _nonnegative_int(count, f"{field}.{key}")
    return dict(sorted(result.items()))


def _enum_count_map(value: Any, field: str, allowed: set[str]) -> dict[str, int]:
    result = _count_map(value, field)
    unexpected = set(result) - allowed
    if unexpected:
        raise ValueError(f"{field} contains unexpected categories")
    return result


def _private_code_totals(value: Any, field: str) -> dict[str, int]:
    """Count private reason-code occurrences without copying code strings."""
    counts = _count_map(value, field)
    return {
        "occurrence_count": sum(counts.values()),
        "distinct_code_count": len(counts),
    }


def _private_list_totals(value: Any, field: str) -> dict[str, int]:
    """Count private code-list entries without copying code strings."""
    if value is None:
        items: list[Any] = []
    elif isinstance(value, list):
        items = value
    else:
        raise ValueError(f"{field} must be a list")
    return {
        "occurrence_count": len(items),
        "distinct_code_count": len({json.dumps(item, sort_keys=True) for item in items}),
    }


def summarize_validation(payload: Mapping[str, Any] | None) -> dict[str, Any]:
    if payload is None:
        return {
            "status": "not_run",
            "mechanical_gate_pass": False,
            "expected_pairs": EXPECTED_PAIRS,
        }
    if payload.get("validator") != "factual_direct_pair_rewrite_validator":
        raise ValueError("unrecognized mechanical validator summary")
    gate_pass = payload.get("mechanical_gate_pass")
    if not isinstance(gate_pass, bool):
        raise ValueError("mechanical_gate_pass must be boolean")
    raw_binding = payload.get("artifact_binding")
    if gate_pass and raw_binding is None:
        raise ValueError("passing mechanical summary requires an artifact binding")
    binding = validate_artifact_binding(raw_binding) if raw_binding is not None else None
    expected = _nonnegative_int(payload.get("expected_source_count"), "expected_source_count")
    result = {
        "status": "passed" if gate_pass else "failed",
        "mechanical_gate_pass": gate_pass,
        "expected_pairs": expected,
        "source_rows": _nonnegative_int(payload.get("source_rows"), "source_rows"),
        "pair_rows": _nonnegative_int(payload.get("pair_rows"), "pair_rows"),
        "audit_rows": _nonnegative_int(payload.get("audit_rows"), "audit_rows"),
        "manual_review_required": bool(payload.get("manual_review_required", False)),
        "status_counts": _enum_count_map(
            payload.get("status_counts"),
            "status_counts",
            {"fail", "manual_review", "pass"},
        ),
        "global_failure_flags": _private_list_totals(
            payload.get("global_failure_flags"), "global_failure_flags"
        ),
        "failure_flags": _private_code_totals(
            payload.get("failure_flag_counts"), "failure_flag_counts"
        ),
        "warning_flags": _private_code_totals(
            payload.get("warning_flag_counts"), "warning_flag_counts"
        ),
        "dataset_counts": _enum_count_map(
            payload.get("dataset_counts"),
            "dataset_counts",
            {"<missing>", "asqa", "billsum", "qasper"},
        ),
        "draft_order_counts": _enum_count_map(
            payload.get("draft_order_counts"),
            "draft_order_counts",
            {"confident_first", "hesitant_first"},
        ),
        "length_direction_counts": _enum_count_map(
            payload.get("length_direction_counts"),
            "length_direction_counts",
            {"confident_longer", "hesitant_longer"},
        ),
        "semantic_equivalence_certified": False,
        "naturalness_certified": False,
        "speaker_confidence_direction_certified": False,
        "artifact_binding": binding,
    }
    if gate_pass and not (
        expected == EXPECTED_PAIRS
        and result["source_rows"] == EXPECTED_PAIRS
        and result["pair_rows"] == EXPECTED_PAIRS
        and result["audit_rows"] == EXPECTED_PAIRS
    ):
        raise ValueError("a passing final mechanical summary must cover exactly 12 pairs")
    if gate_pass and (
        result["global_failure_flags"]["occurrence_count"]
        or result["failure_flags"]["occurrence_count"]
        or result["status_counts"].get("fail", 0)
        or sum(result["status_counts"].values()) != EXPECTED_PAIRS
    ):
        raise ValueError("passing mechanical summary contains failure evidence")
    if binding is not None and (
        binding["source_count"] != expected or binding["pair_count"] != expected
    ):
        raise ValueError("mechanical summary coverage does not match its artifact binding")
    return result


def summarize_shortcut(payload: Mapping[str, Any] | None) -> dict[str, Any]:
    if payload is None:
        return {
            "status": "not_run",
            "automatic_shortcut_gate_pass": False,
            "expected_pairs": EXPECTED_PAIRS,
        }
    if payload.get("audit") != "factual_direct_pair_shortcut_audit":
        raise ValueError("unrecognized shortcut-audit summary")
    decision = payload.get("decision")
    scope = payload.get("scope")
    if not isinstance(decision, Mapping) or not isinstance(scope, Mapping):
        raise ValueError("shortcut summary requires decision and scope objects")
    gate_pass = decision.get("automatic_shortcut_gate_pass")
    if not isinstance(gate_pass, bool):
        raise ValueError("automatic_shortcut_gate_pass must be boolean")
    raw_binding = payload.get("artifact_binding")
    if gate_pass and raw_binding is None:
        raise ValueError("passing shortcut summary requires an artifact binding")
    binding = validate_artifact_binding(raw_binding) if raw_binding is not None else None
    result = {
        "status": "passed" if gate_pass else "failed",
        "automatic_shortcut_gate_pass": gate_pass,
        "expected_pairs": _nonnegative_int(scope.get("expected_pairs"), "scope.expected_pairs"),
        "source_rows": _nonnegative_int(scope.get("source_rows"), "scope.source_rows"),
        "writer_rows": _nonnegative_int(scope.get("writer_rows"), "scope.writer_rows"),
        "audit_rows": _nonnegative_int(scope.get("audit_rows"), "scope.audit_rows"),
        "status_counts": _enum_count_map(
            payload.get("status_counts"),
            "status_counts",
            {"pass", "reject"},
        ),
        "flags": _private_code_totals(payload.get("flag_counts"), "flag_counts"),
        "warnings": _private_code_totals(
            payload.get("warning_counts"), "warning_counts"
        ),
        "batch_flags": _private_list_totals(
            payload.get("batch_flags"), "batch_flags"
        ),
        "semantic_qualifier_review_required_count": _optional_nonnegative_int(
            payload.get("semantic_qualifier_review_required_count"),
            "semantic_qualifier_review_required_count",
        ),
        "blind_semantic_and_direction_review_still_required": True,
        "human_review_certified": False,
        "activation_scoring_authorized": False,
        "artifact_binding": binding,
    }
    if gate_pass and not (
        result["expected_pairs"] == EXPECTED_PAIRS
        and result["source_rows"] == EXPECTED_PAIRS
        and result["writer_rows"] == EXPECTED_PAIRS
        and result["audit_rows"] == EXPECTED_PAIRS
    ):
        raise ValueError("a passing final shortcut summary must cover exactly 12 pairs")
    if gate_pass and (
        result["flags"]["occurrence_count"]
        or result["batch_flags"]["occurrence_count"]
        or result["status_counts"].get("reject", 0)
        or sum(result["status_counts"].values()) != EXPECTED_PAIRS
    ):
        raise ValueError("passing shortcut summary contains rejection evidence")
    if binding is not None and (
        binding["source_count"] != result["source_rows"]
        or binding["pair_count"] != result["writer_rows"]
    ):
        raise ValueError("shortcut summary coverage does not match its artifact binding")
    return result


def _records(payload: Mapping[str, Any], names: Sequence[str]) -> list[dict[str, Any]]:
    for name in names:
        value = payload.get(name)
        if value is None:
            continue
        if not isinstance(value, list) or any(not isinstance(item, dict) for item in value):
            raise ValueError(f"{name} must be a list of objects")
        return value
    return []


def _normalize_pre_review_decision(value: Any) -> str:
    if value is None:
        return "pending"
    if not isinstance(value, str):
        raise ValueError("pre-review decisions must be strings")
    normalized = value.strip().casefold().replace("-", "_").replace(" ", "_")
    if normalized in PASS_DECISIONS:
        return "pass"
    if normalized in REPAIR_DECISIONS:
        return "repair"
    if normalized in REJECT_DECISIONS:
        return "reject"
    if normalized in PENDING_DECISIONS:
        return "pending"
    raise ValueError(f"unrecognized pre-review decision: {value}")


def summarize_pre_review(payload: Mapping[str, Any] | None) -> dict[str, Any]:
    if payload is None:
        return {
            "status": "not_run",
            "review_type": "model_assisted",
            "expected_pairs": EXPECTED_PAIRS,
            "reviewed_pairs": 0,
            "complete": False,
            "all_pass": False,
            "human_review_certified": False,
        }
    if payload.get("schema") != PRE_REVIEW_SCHEMA:
        raise ValueError("unrecognized model-assisted pre-review schema")
    reviewer_type = payload.get("review_type", payload.get("reviewer_type"))
    if reviewer_type != "model_assisted":
        raise ValueError("pre-review must use review_type=model_assisted")
    if payload.get("blinded") is not True:
        raise ValueError("model-assisted pre-review must be label-blind")
    binding = validate_artifact_binding(payload.get("artifact_binding"))
    rows = _records(payload, ("records", "rows", "reviews"))
    source_ids = [row.get("source_id") for row in rows]
    if any(not isinstance(source_id, str) or not source_id for source_id in source_ids):
        raise ValueError("every pre-review row requires a nonempty source_id")
    if len(source_ids) != len(set(source_ids)):
        raise ValueError("pre-review contains duplicate source_id values")
    if source_ids and source_ids_sha256(source_ids) != binding["source_ids_sha256"]:
        raise ValueError("pre-review source IDs do not match its artifact binding")
    decisions = [
        _normalize_pre_review_decision(row.get("decision", row.get("review_decision")))
        for row in rows
    ]
    counts = Counter(decisions)
    reviewed = len(rows) - counts.get("pending", 0)
    complete = len(rows) == EXPECTED_PAIRS and reviewed == EXPECTED_PAIRS
    all_pass = complete and counts == Counter({"pass": EXPECTED_PAIRS})
    if complete:
        status = "complete"
    elif rows:
        status = "in_progress"
    else:
        status = "not_run"
    return {
        "status": status,
        "review_type": "model_assisted",
        "blinded": True,
        "expected_pairs": EXPECTED_PAIRS,
        "submitted_rows": len(rows),
        "reviewed_pairs": reviewed,
        "decision_counts": dict(sorted(counts.items())),
        "complete": complete,
        "all_pass": all_pass,
        "human_review_certified": False,
        "artifact_binding": binding,
    }


def _filled(value: Any) -> bool:
    return value is not None and (not isinstance(value, str) or bool(value.strip()))


def summarize_blind_review(
    manifest: Mapping[str, Any] | None,
    results: Mapping[str, Any] | None,
) -> dict[str, Any]:
    if manifest is None:
        if results is not None:
            raise ValueError("blind-review results require their binding manifest")
        return {
            "status": "not_prepared",
            "packet_prepared": False,
            "expected_pairs": EXPECTED_PAIRS,
            "complete_review_rows": 0,
            "human_review_certified": False,
        }
    if manifest.get("schema") != "factual-rewrite-blind-review-v1":
        raise ValueError("unrecognized blind-review manifest")
    binding = validate_artifact_binding(manifest.get("artifact_binding"))
    pair_count = _nonnegative_int(manifest.get("pair_count"), "pair_count")
    packet_sha256 = manifest.get("packet_sha256")
    if not isinstance(packet_sha256, str) or not SHA256_RE.fullmatch(packet_sha256):
        raise ValueError("blind-review packet_sha256 must be a SHA-256 digest")
    blinded = manifest.get("blinded") is True
    answer_key_separate = manifest.get("answer_key_embedded_in_html") is False
    packet_prepared = pair_count == EXPECTED_PAIRS and blinded and answer_key_separate
    if not packet_prepared:
        raise ValueError("blind-review packet is not a valid blinded 12-pair packet")
    if binding["source_count"] != pair_count or binding["pair_count"] != pair_count:
        raise ValueError("blind-review coverage does not match its artifact binding")

    submitted = 0
    complete = 0
    if results is not None:
        if results.get("blinded") is not True:
            raise ValueError("blind-review results must retain blinded=true")
        packet_hash = results.get("packet_sha256")
        if packet_hash != packet_sha256:
            raise ValueError("blind-review results do not match the packet manifest")
        rows = _records(results, ("reviews", "rows"))
        submitted = len(rows)
        if submitted > pair_count:
            raise ValueError("blind-review result count exceeds packet pair count")
        review_ids = [row.get("review_id") for row in rows]
        if any(not isinstance(review_id, str) or not review_id for review_id in review_ids):
            raise ValueError("every blind-review row requires a nonempty review_id")
        if len(review_ids) != len(set(review_ids)):
            raise ValueError("blind-review results contain duplicate review_id values")
        expected_ids = {f"R{index:03d}" for index in range(1, pair_count + 1)}
        if set(review_ids) - expected_ids:
            raise ValueError("blind-review results contain unknown review_id values")
        for row in rows:
            for field, allowed in BLIND_REVIEW_ENUMS.items():
                value = row.get(field)
                if _filled(value) and value not in allowed:
                    raise ValueError(f"blind-review {field} contains an invalid choice")
        complete = sum(
            all(_filled(row.get(field)) for field in REQUIRED_BLIND_REVIEW_FIELDS)
            for row in rows
        )
    if complete == pair_count:
        status = "complete_awaiting_adjudication"
    elif submitted:
        status = "in_progress"
    else:
        status = "prepared_pending"
    return {
        "status": status,
        "packet_prepared": True,
        "expected_pairs": EXPECTED_PAIRS,
        "pair_count": pair_count,
        "blinded": True,
        "answer_key_separate": True,
        "submitted_review_rows": submitted,
        "complete_review_rows": complete,
        "human_review_certified": False,
        "artifact_binding": binding,
        "certification_note": (
            "Completion of the form is not certification; review import and "
            "rule-based adjudication are separate steps."
        ),
    }


def _overall_status(stages: Mapping[str, Mapping[str, Any]]) -> str:
    validation = stages["mechanical_validation"]
    shortcut = stages["shortcut_audit"]
    pre_review = stages["model_assisted_pre_review"]
    blind = stages["blind_review"]
    if validation["status"] == "failed" or shortcut["status"] == "failed":
        return "blocked_by_automatic_gate"
    if not validation["mechanical_gate_pass"] or not shortcut["automatic_shortcut_gate_pass"]:
        return "in_progress"
    if pre_review["status"] == "complete" and not pre_review["all_pass"]:
        return "blocked_by_model_assisted_pre_review"
    if not pre_review["complete"]:
        return "awaiting_model_assisted_pre_review"
    if not blind["packet_prepared"]:
        return "ready_to_prepare_blind_review"
    if blind["status"] == "prepared_pending":
        return "ready_for_blind_review"
    if blind["status"] == "in_progress":
        return "blind_review_in_progress"
    return "awaiting_review_import_and_adjudication"


def build_status_report(
    validation: Mapping[str, Any] | None = None,
    shortcut: Mapping[str, Any] | None = None,
    pre_review: Mapping[str, Any] | None = None,
    blind_manifest: Mapping[str, Any] | None = None,
    blind_results: Mapping[str, Any] | None = None,
    provenance: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    stages = {
        "mechanical_validation": summarize_validation(validation),
        "shortcut_audit": summarize_shortcut(shortcut),
        "model_assisted_pre_review": summarize_pre_review(pre_review),
        "blind_review": summarize_blind_review(blind_manifest, blind_results),
    }
    bindings = [
        stage.pop("artifact_binding")
        for stage in stages.values()
        if stage.get("artifact_binding") is not None
    ]
    if bindings and any(binding != bindings[0] for binding in bindings[1:]):
        raise ValueError("stage artifacts do not bind to the same 12-pair set")
    status = _overall_status(stages)
    return {
        "schema": "factual-rewrite-canary-public-status-v1",
        "canary_pair_count": EXPECTED_PAIRS,
        "status": status,
        "stages": stages,
        "artifact_binding": bindings[0] if bindings else None,
        "decision": {
            "scale_to_120_authorized": False,
            "activation_scoring_authorized": False,
            "probe_training_authorized": False,
            "human_review_certified": False,
            "confidence_representation_established": False,
        },
        "provenance_sha256": dict(sorted((provenance or {}).items())),
        "privacy": {
            "contains_source_text": False,
            "contains_rewrite_text": False,
            "contains_source_ids": False,
            "contains_row_level_review_notes": False,
        },
        "scope_note": (
            "This status report covers data construction only. It does not report "
            "activations, probe performance, causal effects, or a validated "
            "confidence representation."
        ),
    }


def _yes_no(value: bool) -> str:
    return "Pass" if value else "Not passed"


def render_markdown(report: Mapping[str, Any]) -> str:
    stages = report["stages"]
    status = report["status"]
    conclusions = {
        "blocked_by_automatic_gate": "The canary is blocked by an automatic quality gate.",
        "blocked_by_model_assisted_pre_review": (
            "The automatic gates passed, but the model-assisted pre-review found "
            "at least one pair that still needs repair or rejection."
        ),
        "in_progress": "The 12-pair construction gate is still in progress.",
        "awaiting_model_assisted_pre_review": (
            "The automatic gates passed; model-assisted semantic pre-review is next."
        ),
        "ready_to_prepare_blind_review": (
            "The automatic gates and model-assisted pre-review passed; the blind "
            "review packet can now be prepared."
        ),
        "ready_for_blind_review": (
            "The canary passed its automatic and model-assisted pre-review gates "
            "and is ready for blind review."
        ),
        "blind_review_in_progress": "Blind review has started but is not complete.",
        "awaiting_review_import_and_adjudication": (
            "The blind form is complete, but its decisions still need validated "
            "import and adjudication."
        ),
    }
    validation = stages["mechanical_validation"]
    shortcut = stages["shortcut_audit"]
    pre = stages["model_assisted_pre_review"]
    blind = stages["blind_review"]
    lines = [
        "# Factual rewrite canary status",
        "",
        f"**Current conclusion:** {conclusions[status]}",
        "",
        "| Stage | Status | Coverage |",
        "|---|---|---:|",
        (
            "| Mechanical validation | "
            f"{_yes_no(validation['mechanical_gate_pass'])} | "
            f"{validation.get('audit_rows', 0)} / {EXPECTED_PAIRS} pairs |"
        ),
        (
            "| Shortcut audit | "
            f"{_yes_no(shortcut['automatic_shortcut_gate_pass'])} | "
            f"{shortcut.get('audit_rows', 0)} / {EXPECTED_PAIRS} pairs |"
        ),
        (
            "| Model-assisted pre-review | "
            f"{pre['status'].replace('_', ' ')} | "
            f"{pre.get('reviewed_pairs', 0)} / {EXPECTED_PAIRS} pairs |"
        ),
        (
            "| Blind review | "
            f"{blind['status'].replace('_', ' ')} | "
            f"{blind.get('complete_review_rows', 0)} / {EXPECTED_PAIRS} pairs |"
        ),
        "",
        "## Decision boundary",
        "",
        "- **Scaling to 120 pairs is not authorized by this report.**",
        "- **Activation extraction and probe training are not authorized by this report.**",
        "- A completed review form is not automatically a passed review; validated import and adjudication remain separate.",
        "- This report does not establish a confidence representation or a causal mechanism.",
        "",
        "The public report contains aggregate counts and file hashes only. Source text, rewrites, source IDs, and row-level notes remain private.",
        "",
    ]
    return "\n".join(lines)


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validation-summary", type=Path)
    parser.add_argument("--shortcut-summary", type=Path)
    parser.add_argument("--pre-review", type=Path)
    parser.add_argument("--blind-review-manifest", type=Path)
    parser.add_argument("--blind-review-results", type=Path)
    parser.add_argument(
        "--json-output",
        type=Path,
        default=RESULTS / "factual_rewrite_canary_status.json",
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=RESULTS / "FACTUAL_REWRITE_CANARY_STATUS.md",
    )
    args = parser.parse_args(argv)
    if _inside(args.json_output, PRIVATE) or _inside(args.markdown_output, PRIVATE):
        parser.error("public status outputs must be outside private_data")

    inputs = {
        "mechanical_validation": args.validation_summary,
        "shortcut_audit": args.shortcut_summary,
        "model_assisted_pre_review": args.pre_review,
        "blind_review_manifest": args.blind_review_manifest,
        "blind_review_results": args.blind_review_results,
    }
    objects = {
        name: read_object(path) if path is not None else None
        for name, path in inputs.items()
    }
    provenance = {
        name: sha256_file(path)
        for name, path in inputs.items()
        if path is not None
    }
    report = build_status_report(
        validation=objects["mechanical_validation"],
        shortcut=objects["shortcut_audit"],
        pre_review=objects["model_assisted_pre_review"],
        blind_manifest=objects["blind_review_manifest"],
        blind_results=objects["blind_review_results"],
        provenance=provenance,
    )
    _write_json(args.json_output, report)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(render_markdown(report), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
