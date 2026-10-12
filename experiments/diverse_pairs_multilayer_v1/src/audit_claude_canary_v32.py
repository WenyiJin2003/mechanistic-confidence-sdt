"""Offline, fail-closed quality gate for the v3.2 rewrite smoke.

The gate binds the frozen v3.2 generation contract, attempt 0, the optional
single mechanical retry, and the canonical earliest-passing selection.  It
never invokes a model.  Private text is used only for aggregate diagnostics
and a blinded X/Y semantic-review packet; the public report is text-free.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.diverse_pairs_multilayer_v1.src import (
    audit_claude_canary_v31 as v31audit,
)
from experiments.diverse_pairs_multilayer_v1.src import (
    run_claude_rewrite_batches_v32 as runner,
)


BASE = Path(__file__).resolve().parents[1]
PRIVATE_ROOT = (BASE / "private_data").resolve()
DEFAULT_CONFIG = BASE / "configs" / "claude_rewrite_dev_v32.json"
PUBLIC_REPORTS = BASE / "reports"
EXPECTED_COUNT = 8
AUDIT_VERSION = 1

QualityGateError = v31audit.QualityGateError


@dataclass(frozen=True)
class AuditArtifacts:
    attempt0_records: tuple[dict[str, Any], ...]
    retry_records: tuple[dict[str, Any], ...]
    canonical_records: tuple[dict[str, Any], ...]
    retry_plan: dict[str, Any] | None
    retry_identity: dict[str, Any] | None
    canonical_payload: dict[str, Any] | None
    integrity: dict[str, Any]


def _canonical_bytes(value: Any) -> bytes:
    return runner._canonical_json_bytes(value)


def _sha256(value: Any) -> str:
    return runner.v2.sha256_bytes(_canonical_bytes(value))


def _atomic_json(path: Path, value: Any) -> None:
    v31audit._atomic_json(path, value)


def _is_private_path(path: Path) -> bool:
    resolved = path.resolve()
    return resolved == PRIVATE_ROOT or PRIVATE_ROOT in resolved.parents


def _identity_valid(identity: Mapping[str, Any]) -> bool:
    contract = identity.get("generation_contract")
    contract_hash = identity.get("generation_contract_sha256")
    fingerprint = identity.get("generation_fingerprint")
    if not (
        isinstance(contract, Mapping)
        and isinstance(contract_hash, str)
        and v31audit.v3.HEX64_RE.fullmatch(contract_hash)
        and isinstance(fingerprint, str)
        and v31audit.v3.HEX64_RE.fullmatch(fingerprint)
        and contract_hash == _sha256(dict(contract))
        and fingerprint == runner.v2.sha256_text(f"v32:{contract_hash}")
    ):
        return False
    if (
        contract.get("runner_version") != runner.RUNNER_VERSION
        or contract.get("protocol_version") != runner.PROTOCOL_VERSION
        or contract.get("phase") != "smoke"
    ):
        return False
    expected_runtime_hashes = {
        "run_claude_rewrite_batches_v32": runner.v2.sha256_file(Path(runner.__file__)),
        "build_rewrite_dev_manifests_v32": runner.v2.sha256_file(
            Path(runner.selector.__file__)
        ),
        "run_claude_rewrite_batches_v31": runner.v2.sha256_file(
            Path(runner.v31.__file__)
        ),
        "build_rewrite_dev_manifests_v31": runner.v2.sha256_file(
            Path(runner.v31.selector.__file__)
        ),
        "run_claude_rewrite_batches_v3": runner.v2.sha256_file(
            Path(runner.v3.__file__)
        ),
        "build_rewrite_dev_manifests_v3": runner.v2.sha256_file(
            Path(runner.v3.selector.__file__)
        ),
        "run_claude_rewrite_batches": runner.v2.sha256_file(
            Path(runner.v2.__file__)
        ),
    }
    if contract.get("runtime_module_sha256") != expected_runtime_hashes:
        return False
    for value_name, hash_name in (
        ("prompt_contract", "prompt_contract_sha256"),
        ("validation_contract", "validation_contract_sha256"),
        ("retry_contract", "retry_contract_sha256"),
    ):
        value = contract.get(value_name)
        nested_hash = contract.get(hash_name)
        if not (
            isinstance(value, Mapping)
            and isinstance(nested_hash, str)
            and v31audit.v3.HEX64_RE.fullmatch(nested_hash)
            and nested_hash == _sha256(dict(value))
        ):
            return False
    retry_contract = contract["retry_contract"]
    if not (
        retry_contract.get("max_full_pair_retries") == 1
        and retry_contract.get("semantic_or_NA_retry") is False
        and retry_contract.get("canonical_selection")
        == "earliest_passing_attempt"
    ):
        return False
    batches = contract.get("batches")
    if not isinstance(batches, list) or len(batches) != 1:
        return False
    batch = batches[0]
    if not isinstance(batch, Mapping):
        return False
    list_fields = (
        "source_ids", "source_hashes", "source_record_hashes",
        "source_suitability_statuses", "target_longer_members",
        "confident_target_words", "hedged_target_words",
    )
    if any(
        not isinstance(batch.get(field), list) or len(batch[field]) != EXPECTED_COUNT
        for field in list_fields
    ):
        return False
    if (
        len(set(batch["source_ids"])) != EXPECTED_COUNT
        or set(batch["source_suitability_statuses"]) != {"primary_eligible"}
        or Counter(batch["target_longer_members"])
        != {"confident": 4, "hedged": 4}
    ):
        return False
    attempt_fingerprint = batch.get("attempt_fingerprint")
    binding = {
        key: value for key, value in batch.items() if key != "attempt_fingerprint"
    }
    return bool(
        isinstance(attempt_fingerprint, str)
        and v31audit.v3.HEX64_RE.fullmatch(attempt_fingerprint)
        and attempt_fingerprint == runner.v2.sha256_text(
            "v32-attempt0:" + _sha256(binding)
        )
        and batch.get("generation_attempt") == 0
    )


def _status_counts(records: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    allowed = ("accepted", "needs_review", "not_applicable", "validation_failed")
    counts = Counter(
        str(record.get("status"))
        if record.get("status") in allowed else "other"
        for record in records
    )
    return {status: counts.get(status, 0) for status in (*allowed, "other")}


def _empty_integrity() -> dict[str, Any]:
    return {
        "run_manifest_present": False,
        "run_manifest_matches_current_identity": False,
        "identity_self_consistent": False,
        "runner_full_raw_replay_verified": False,
        "attempt0_parsed_artifact_count": 0,
        "attempt0_artifact_present": False,
        "attempt0_artifact_valid": False,
        "attempt0_terminal": False,
        "attempt0_records_hash_valid": False,
        "attempt0_record_binding_valid": False,
        "attempt0_closed_mechanical_categories": False,
        "attempt0_batch_validation_issue_count": 0,
        "retry_expected": False,
        "retry_artifact_file_count": 0,
        "unexpected_retry_namespace_count": 0,
        "unexpected_attempt_namespace_count": 0,
        "retry_parsed_artifact_count": 0,
        "retry_manifest_present": False,
        "retry_manifest_valid": False,
        "retry_artifact_present": False,
        "retry_artifact_valid": False,
        "retry_terminal": False,
        "retry_records_hash_valid": False,
        "retry_record_binding_valid": False,
        "retry_closed_mechanical_categories": False,
        "retry_batch_validation_issue_count": 0,
        "retry_protocol_valid": False,
        "canonical_present": False,
        "canonical_records_hash_valid": False,
        "canonical_earliest_passing_valid": False,
        "canonical_status_file_present": False,
        "canonical_status_file_valid": False,
        "artifact_readable": True,
        "overall_artifact_integrity_pass": False,
    }


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise QualityGateError("artifact_not_object")
    return payload


def _mechanical_categories_valid(record: Mapping[str, Any]) -> bool:
    categories = record.get("mechanical_issue_categories")
    if not isinstance(categories, list) or not all(
        isinstance(value, str) for value in categories
    ):
        return False
    if categories != sorted(set(categories)):
        return False
    if any(value not in runner.MECHANICAL_ISSUE_CATEGORIES for value in categories):
        return False
    issues = record.get("validation_issues")
    if not isinstance(issues, list) or not all(
        isinstance(value, str) for value in issues
    ):
        return False
    status = record.get("status")
    eligible = record.get("retry_eligible_mechanical_only")
    expected_categories = (
        runner.mechanical_issue_categories(issues)
        if status == "validation_failed" else []
    )
    if categories != expected_categories:
        return False
    if eligible is not bool(status == "validation_failed" and categories):
        return False
    if status == "accepted" and issues:
        return False
    if status == "needs_review" and issues != ["writer_reported_issue"]:
        return False
    return True


def _records_bind(
    records: Sequence[Mapping[str, Any]],
    rows: Sequence[Mapping[str, Any]],
    *,
    generation_attempt: int,
    attempt_fingerprint: str,
) -> bool:
    if len(records) != len(rows):
        return False
    fields = (
        "source_id", "original_response_sha256", "source_record_sha256",
        "source_suitability_status", "rewrite_recipe", "stance_topology",
        "rewrite_output_order", "target_longer_member",
        "confident_target_words", "hedged_target_words",
    )
    for record, source in zip(records, rows):
        if any(record.get(field) != source.get(field) for field in fields):
            return False
        if (
            record.get("generation_attempt") != generation_attempt
            or record.get("attempt_fingerprint") != attempt_fingerprint
            or not _mechanical_categories_valid(record)
        ):
            return False
    return True


def _payload_records(
    payload: Mapping[str, Any],
) -> tuple[list[dict[str, Any]], bool]:
    records = payload.get("records")
    if not isinstance(records, list) or not all(isinstance(row, dict) for row in records):
        return [], False
    valid = payload.get("records_sha256") == _sha256(records)
    return list(records), valid


def _attempt0_payload_valid(
    payload: Mapping[str, Any],
    identity: Mapping[str, Any],
    rows: Sequence[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, bool]]:
    contract = identity["generation_contract"]["batches"][0]
    records, hash_valid = _payload_records(payload)
    binding_valid = bool(
        payload.get("parent_generation_fingerprint")
        == identity.get("generation_fingerprint")
        and payload.get("parent_generation_contract_sha256")
        == identity.get("generation_contract_sha256")
        and payload.get("generation_attempt") == 0
        and payload.get("attempt_fingerprint") == contract.get("attempt_fingerprint")
        and payload.get("attempt_contract_sha256")
        == identity.get("generation_contract_sha256")
        and payload.get("batch_id") == contract.get("batch_id")
        and payload.get("source_ids") == contract.get("source_ids")
        and payload.get("source_hashes") == contract.get("source_hashes")
        and payload.get("source_record_hashes") == contract.get("source_record_hashes")
        and payload.get("source_suitability_statuses")
        == contract.get("source_suitability_statuses")
        and payload.get("target_longer_members") == contract.get("target_longer_members")
        and payload.get("confident_target_words")
        == contract.get("confident_target_words")
        and payload.get("hedged_target_words")
        == contract.get("hedged_target_words")
        and payload.get("batch_prompt_sha256") == contract.get("prompt_sha256")
        and payload.get("retry_issue_categories_by_source") == {}
    )
    record_binding = _records_bind(
        records,
        rows,
        generation_attempt=0,
        attempt_fingerprint=str(contract.get("attempt_fingerprint", "")),
    )
    categories_valid = all(_mechanical_categories_valid(record) for record in records)
    batch_issues = payload.get("batch_validation_issues")
    return records, {
        "terminal": payload.get("terminal") is True,
        "records_hash": hash_valid,
        "binding": binding_valid and record_binding,
        "categories": categories_valid,
        "batch_issues": isinstance(batch_issues, list) and not batch_issues,
    }


def _retry_payload_valid(
    payload: Mapping[str, Any],
    identity: Mapping[str, Any],
    retry_identity: Mapping[str, Any],
    retry_rows: Sequence[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, bool]]:
    contract = retry_identity["attempt_contract"]
    records, hash_valid = _payload_records(payload)
    binding_valid = bool(
        payload.get("parent_generation_fingerprint")
        == identity.get("generation_fingerprint")
        and payload.get("parent_generation_contract_sha256")
        == identity.get("generation_contract_sha256")
        and payload.get("generation_attempt") == 1
        and payload.get("attempt_fingerprint")
        == retry_identity.get("attempt_fingerprint")
        and payload.get("attempt_contract_sha256")
        == retry_identity.get("attempt_contract_sha256")
        and payload.get("batch_id") == contract.get("batch_id")
        and payload.get("source_ids") == contract.get("source_ids")
        and payload.get("source_hashes") == contract.get("source_hashes")
        and payload.get("source_record_hashes") == contract.get("source_record_hashes")
        and payload.get("source_suitability_statuses")
        == contract.get("source_suitability_statuses")
        and payload.get("target_longer_members") == contract.get("target_longer_members")
        and payload.get("confident_target_words")
        == contract.get("confident_target_words")
        and payload.get("hedged_target_words")
        == contract.get("hedged_target_words")
        and payload.get("batch_prompt_sha256") == contract.get("prompt_sha256")
        and payload.get("retry_issue_categories_by_source")
        == contract.get("retry_issue_categories_by_source")
    )
    record_binding = _records_bind(
        records,
        retry_rows,
        generation_attempt=1,
        attempt_fingerprint=str(retry_identity.get("attempt_fingerprint", "")),
    )
    categories_valid = all(_mechanical_categories_valid(record) for record in records)
    batch_issues = payload.get("batch_validation_issues")
    return records, {
        "terminal": payload.get("terminal") is True,
        "records_hash": hash_valid,
        "binding": binding_valid and record_binding,
        "categories": categories_valid,
        "batch_issues": isinstance(batch_issues, list) and not batch_issues,
    }


def load_audit_artifacts(
    output_dir: Path,
    identity: Mapping[str, Any],
    rows: Sequence[dict[str, Any]],
    *,
    config: runner.RunnerConfig | None = None,
    tokenizer: Any = None,
    _allow_synthetic_fixture_without_raw_replay: bool = False,
) -> AuditArtifacts:
    """Validate the complete attempt/retry/canonical chain without model calls."""
    integrity = _empty_integrity()
    attempt0_records: list[dict[str, Any]] = []
    retry_records: list[dict[str, Any]] = []
    canonical_records: list[dict[str, Any]] = []
    retry_plan: dict[str, Any] | None = None
    retry_identity: dict[str, Any] | None = None
    canonical_payload: dict[str, Any] | None = None
    try:
        integrity["identity_self_consistent"] = _identity_valid(identity)
        if not integrity["identity_self_consistent"]:
            raise QualityGateError("identity_invalid")
        manifest_path = output_dir / "run_manifest.json"
        integrity["run_manifest_present"] = manifest_path.exists()
        if manifest_path.exists():
            integrity["run_manifest_matches_current_identity"] = (
                _read_json(manifest_path) == identity
            )
        execution_artifacts_exist = runner._execution_artifacts_exist(output_dir)
        if execution_artifacts_exist and config is not None and tokenizer is not None:
            runner.verify_resume_artifacts(
                output_dir,
                dict(identity),
                config=config,
                rows=rows,
                tokenizer=tokenizer,
            )
            integrity["runner_full_raw_replay_verified"] = True
        elif execution_artifacts_exist and _allow_synthetic_fixture_without_raw_replay:
            # Unit fixtures exercise the independent audit logic without
            # constructing fake model transports. Production callers cannot
            # select this private escape hatch through the CLI.
            integrity["runner_full_raw_replay_verified"] = False
        elif execution_artifacts_exist:
            raise QualityGateError("runner_raw_replay_verification_required")
        if not integrity["run_manifest_matches_current_identity"]:
            raise QualityGateError("run_manifest_stale")

        unexpected_attempt_namespaces = [
            path for path in output_dir.glob("attempt_*")
            if path.is_dir() and path.name != "attempt_0"
        ]
        unexpected_retry_namespaces = [
            path for path in output_dir.glob("retry_*")
            if path.is_dir() and path.name != "retry_1"
        ]
        integrity["unexpected_attempt_namespace_count"] = len(
            unexpected_attempt_namespaces
        )
        integrity["unexpected_retry_namespace_count"] = len(
            unexpected_retry_namespaces
        )
        if unexpected_attempt_namespaces or unexpected_retry_namespaces:
            raise QualityGateError("unexpected_attempt_namespace")

        attempt0_paths = sorted((output_dir / "attempt_0" / "parsed").glob("*.json"))
        integrity["attempt0_parsed_artifact_count"] = len(attempt0_paths)
        integrity["attempt0_artifact_present"] = len(attempt0_paths) == 1
        if len(attempt0_paths) != 1:
            raise QualityGateError("attempt0_missing_or_duplicated")
        attempt0_payload = _read_json(attempt0_paths[0])
        attempt0_records, checks = _attempt0_payload_valid(
            attempt0_payload, identity, rows
        )
        integrity["attempt0_terminal"] = checks["terminal"]
        integrity["attempt0_records_hash_valid"] = checks["records_hash"]
        integrity["attempt0_record_binding_valid"] = checks["binding"]
        integrity["attempt0_closed_mechanical_categories"] = checks["categories"]
        integrity["attempt0_batch_validation_issue_count"] = (
            0 if checks["batch_issues"] else 1
        )
        integrity["attempt0_artifact_valid"] = all(checks.values())
        if not integrity["attempt0_artifact_valid"]:
            raise QualityGateError("attempt0_invalid")

        retry_plan = runner.attempt0_retry_plan(attempt0_records)
        integrity["retry_expected"] = retry_plan.get("retry_authorized") is True
        retry_paths = sorted((output_dir / "retry_1" / "parsed").glob("*.json"))
        retry_manifest_path = output_dir / "retry_1" / "retry_manifest.json"
        retry_files = [
            path for path in (output_dir / "retry_1").rglob("*") if path.is_file()
        ]
        integrity["retry_artifact_file_count"] = len(retry_files)
        integrity["retry_parsed_artifact_count"] = len(retry_paths)
        integrity["retry_manifest_present"] = retry_manifest_path.exists()

        if integrity["retry_expected"]:
            attempt0_batch = runner.make_batches(rows, "smoke", 8)[0]
            retry_batch = runner.make_retry_batch(attempt0_batch, retry_plan)
            retry_identity = runner.retry_attempt_identity(
                dict(identity), retry_batch, retry_plan
            )
            integrity["retry_manifest_valid"] = bool(
                retry_manifest_path.exists()
                and _read_json(retry_manifest_path) == retry_identity
            )
            integrity["retry_artifact_present"] = len(retry_paths) == 1
            if len(retry_paths) != 1:
                raise QualityGateError("retry_missing_or_duplicated")
            retry_payload = _read_json(retry_paths[0])
            retry_records, retry_checks = _retry_payload_valid(
                retry_payload,
                identity,
                retry_identity,
                list(retry_batch.rows),
            )
            integrity["retry_terminal"] = retry_checks["terminal"]
            integrity["retry_records_hash_valid"] = retry_checks["records_hash"]
            integrity["retry_record_binding_valid"] = retry_checks["binding"]
            integrity["retry_closed_mechanical_categories"] = retry_checks["categories"]
            integrity["retry_batch_validation_issue_count"] = (
                0 if retry_checks["batch_issues"] else 1
            )
            integrity["retry_artifact_valid"] = all(retry_checks.values())
            integrity["retry_protocol_valid"] = bool(
                integrity["retry_manifest_valid"]
                and integrity["retry_artifact_valid"]
                and len(retry_records) == 1
            )
            if not integrity["retry_protocol_valid"]:
                raise QualityGateError("retry_invalid")
        else:
            integrity["retry_protocol_valid"] = bool(
                not retry_files and not retry_manifest_path.exists()
            )
            if not integrity["retry_protocol_valid"]:
                raise QualityGateError("unauthorized_retry_present")

        canonical_path = output_dir / "canonical" / "selected.json"
        status_path = output_dir / "status.json"
        integrity["canonical_present"] = canonical_path.exists()
        integrity["canonical_status_file_present"] = status_path.exists()
        if not canonical_path.exists() or not status_path.exists():
            raise QualityGateError("canonical_missing")
        canonical_payload = _read_json(canonical_path)
        canonical_records_raw = canonical_payload.get("records")
        if not isinstance(canonical_records_raw, list) or not all(
            isinstance(record, dict) for record in canonical_records_raw
        ):
            raise QualityGateError("canonical_records_invalid")
        canonical_records = list(canonical_records_raw)
        expected_canonical = runner.select_canonical_records(
            attempt0_records, retry_records
        )
        integrity["canonical_records_hash_valid"] = bool(
            canonical_payload.get("records_sha256") == _sha256(canonical_records)
            and expected_canonical["records_sha256"] == _sha256(canonical_records)
        )
        core_fields = (
            "selection_rule", "attempt0_accepted", "final_accepted",
            "final_not_applicable", "stop_go_passed", "output_blocked",
            "records", "records_sha256",
        )
        expected_attempt0_relpath = str(
            attempt0_paths[0].relative_to(output_dir)
        )
        expected_retry_relpath = (
            str(retry_paths[0].relative_to(output_dir)) if retry_paths else None
        )
        integrity["canonical_earliest_passing_valid"] = bool(
            all(canonical_payload.get(field) == expected_canonical.get(field)
                for field in core_fields)
            and canonical_payload.get("terminal") is True
            and canonical_payload.get("generation_fingerprint")
            == identity.get("generation_fingerprint")
            and canonical_payload.get("generation_contract_sha256")
            == identity.get("generation_contract_sha256")
            and canonical_payload.get("attempt_0_parsed_artifact")
            == expected_attempt0_relpath
            and canonical_payload.get("attempt_0_parsed_artifact_sha256")
            == runner.v2.sha256_file(attempt0_paths[0])
            and canonical_payload.get("retry_plan") == retry_plan
            and canonical_payload.get("retry_attempt_identity") == retry_identity
            and canonical_payload.get("retry_parsed_artifact")
            == expected_retry_relpath
            and canonical_payload.get("retry_parsed_artifact_sha256")
            == (
                runner.v2.sha256_file(retry_paths[0]) if retry_paths else None
            )
        )
        expected_status = {
            key: value for key, value in canonical_payload.items() if key != "records"
        }
        expected_status["canonical_artifact_sha256"] = runner.v2.sha256_file(
            canonical_path
        )
        integrity["canonical_status_file_valid"] = (
            _read_json(status_path) == expected_status
        )
        integrity["overall_artifact_integrity_pass"] = bool(
            integrity["run_manifest_matches_current_identity"]
            and integrity["attempt0_artifact_valid"]
            and integrity["retry_protocol_valid"]
            and integrity["canonical_records_hash_valid"]
            and integrity["canonical_earliest_passing_valid"]
            and integrity["canonical_status_file_valid"]
        )
    except (OSError, TypeError, ValueError, KeyError, json.JSONDecodeError, QualityGateError):
        integrity["artifact_readable"] = False
        integrity["overall_artifact_integrity_pass"] = False

    return AuditArtifacts(
        attempt0_records=tuple(attempt0_records),
        retry_records=tuple(retry_records),
        canonical_records=tuple(canonical_records),
        retry_plan=retry_plan,
        retry_identity=retry_identity,
        canonical_payload=canonical_payload,
        integrity=integrity,
    )


def _experiment_binding(
    identity: Mapping[str, Any], artifacts: AuditArtifacts
) -> dict[str, Any]:
    if not _identity_valid(identity):
        raise QualityGateError("generation_identity_invalid")
    batch = identity["generation_contract"]["batches"][0]
    canonical = artifacts.canonical_payload
    if not isinstance(canonical, Mapping):
        raise QualityGateError("canonical_binding_missing")
    retry_fingerprint = None
    if artifacts.retry_identity is not None:
        retry_fingerprint = artifacts.retry_identity.get("attempt_fingerprint")
    return {
        "protocol_version": identity["generation_contract"].get("protocol_version"),
        "generation_fingerprint": identity.get("generation_fingerprint"),
        "generation_contract_sha256": identity.get("generation_contract_sha256"),
        "attempt0_fingerprint": batch.get("attempt_fingerprint"),
        "retry_attempt_fingerprint": retry_fingerprint,
        "canonical_records_sha256": canonical.get("records_sha256"),
        "canonical_selection": "earliest_passing_attempt",
    }


def build_blind_review_packet(
    source_rows: Sequence[dict[str, Any]],
    records: Sequence[dict[str, Any]],
    *,
    identity: Mapping[str, Any],
    artifacts: AuditArtifacts,
    seed: int = v31audit.v3.DEFAULT_REVIEW_SEED,
) -> tuple[dict[str, Any], dict[str, Any]]:
    packet, key = v31audit.v3.build_blind_review_packet(
        source_rows, records, phase="smoke", seed=seed
    )
    binding = _experiment_binding(identity, artifacts)
    binding_id = _sha256(binding)
    core = {
        name: value for name, value in packet.items()
        if name not in {"packet_id", "review_metadata", "schema", "version"}
    }
    core.update({
        "schema": "v32-blind-semantic-review",
        "version": 1,
        "experiment_binding_id": binding_id,
    })
    packet_id = _sha256(core)
    packet = {
        "packet_id": packet_id,
        "review_metadata": {
            "packet_id": packet_id,
            "experiment_binding_id": binding_id,
            "blind": True,
            "reviewer_type": None,
        },
        **core,
    }
    key = {
        **key,
        "schema": "v32-blind-semantic-review-key",
        "version": 1,
        "packet_id": packet_id,
        "experiment_binding_id": binding_id,
        "generation_binding": binding,
    }
    return packet, key


def write_blind_review_packet(
    packet_path: Path,
    key_path: Path,
    packet: Mapping[str, Any],
    key: Mapping[str, Any],
) -> None:
    v31audit.write_blind_review_packet(
        packet_path, key_path, dict(packet), dict(key)
    )


def aggregate_semantic_review(
    review: Mapping[str, Any] | None,
    key: Mapping[str, Any],
    identity: Mapping[str, Any],
    artifacts: AuditArtifacts,
) -> dict[str, Any]:
    if review is None:
        return v31audit.v3._semantic_pending()
    expected_binding = _experiment_binding(identity, artifacts)
    expected_id = _sha256(expected_binding)
    metadata = review.get("review_metadata")
    if not isinstance(metadata, Mapping):
        raise QualityGateError("semantic_review_invalid")
    if (
        key.get("generation_binding") != expected_binding
        or key.get("experiment_binding_id") != expected_id
        or metadata.get("experiment_binding_id") != expected_id
    ):
        raise QualityGateError("semantic_review_stale_generation_binding")
    aggregate = v31audit.v3.aggregate_semantic_review(review, key)
    counts = aggregate.get("counts", {})
    count = int(aggregate.get("reviewed_pair_count", 0))
    topology = aggregate.get("topology_assignment_check", {})

    def exact(field: str, value: str) -> bool:
        values = counts.get(field, {})
        return isinstance(values, Mapping) and values.get(value) == EXPECTED_COUNT

    strict_pass = bool(
        aggregate.get("semantic_review_complete") is True
        and count == EXPECTED_COUNT
        and exact("content_preservation", "pass")
        and counts.get("certainty_ordering", {}).get("correct") == EXPECTED_COUNT
        and exact("speaker_scope", "pass")
        and exact("confound", "none")
        and exact("formatting", "pass")
        and exact("naturalness", "pass")
        and exact("shortcut", "none")
        and topology.get("all_candidates_match_assignment") is True
    )
    aggregate["semantic_gate_pass"] = strict_pass
    aggregate["strict_all_eight_required"] = True
    aggregate["human_certified"] = bool(
        strict_pass and aggregate.get("reviewer_type") == "human"
    )
    return aggregate


def _length_direction_summary(
    source_rows: Sequence[dict[str, Any]],
    records: Sequence[dict[str, Any]],
) -> dict[str, Any]:
    record_by_id = {str(record.get("source_id")): record for record in records}
    assigned = Counter(str(row.get("target_longer_member")) for row in source_rows)
    observed = Counter()
    exact_target_count = 0
    match_count = 0
    tie_count = 0
    evaluated = 0
    for source in source_rows:
        record = record_by_id.get(str(source.get("source_id")))
        if not isinstance(record, Mapping) or record.get("status") == "not_applicable":
            continue
        confident = record.get("confident_response")
        hedged = record.get("hedged_response")
        if not isinstance(confident, str) or not isinstance(hedged, str):
            continue
        confident_words = runner._word_count(confident)
        hedged_words = runner._word_count(hedged)
        direction = (
            "confident" if confident_words > hedged_words
            else "hedged" if hedged_words > confident_words else "tie"
        )
        observed[direction] += 1
        tie_count += int(direction == "tie")
        match_count += int(direction == source.get("target_longer_member"))
        exact_target_count += int(
            confident_words == source.get("confident_target_words")
            and hedged_words == source.get("hedged_target_words")
        )
        evaluated += 1
    return {
        "assignment_counts": {
            "confident": assigned.get("confident", 0),
            "hedged": assigned.get("hedged", 0),
            "other": sum(
                count for label, count in assigned.items()
                if label not in {"confident", "hedged"}
            ),
        },
        "assignment_exact_4_4": bool(
            assigned.get("confident", 0) == 4
            and assigned.get("hedged", 0) == 4
            and sum(assigned.values()) == 8
        ),
        "evaluated_pair_count": evaluated,
        "observed_longer_counts": {
            "confident": observed.get("confident", 0),
            "hedged": observed.get("hedged", 0),
            "tie": observed.get("tie", 0),
        },
        "exact_target_word_count_pair_count": exact_target_count,
        "direction_match_count": match_count,
        "direction_mismatch_count": evaluated - match_count,
        "tie_count": tie_count,
        "all_final_pairs_match_assignment": bool(
            evaluated == EXPECTED_COUNT
            and match_count == EXPECTED_COUNT
            and exact_target_count == EXPECTED_COUNT
            and tie_count == 0
        ),
    }


def _v31_compat_integrity(passed: bool) -> dict[str, Any]:
    value = bool(passed)
    return {
        "parsed_artifact_count": 1 if value else 0,
        "expected_batch_count": 1,
        "completed_expected_batch_count": 1 if value else 0,
        "unexpected_batch_artifact_count": 0,
        "duplicate_batch_artifact_count": 0,
        "terminal_artifact_count": 1 if value else 0,
        "records_hash_valid_count": 1 if value else 0,
        "generation_fingerprint_present": value,
        "current_generation_fingerprint_match_count": 1 if value else 0,
        "exact_batch_binding_match_count": 1 if value else 0,
        "run_manifest_present": value,
        "run_manifest_matches_current_identity": value,
        "current_generation_contract_verified": value,
        "exact_expected_batch_set": value,
        "batch_validation_issue_count": 0,
        "artifact_readable": value,
        "all_terminal": value,
        "all_record_hashes_valid": value,
        "frozen_manifest_validated": value,
    }


def build_public_report(
    source_rows: Sequence[dict[str, Any]],
    artifacts: AuditArtifacts,
    *,
    identity: Mapping[str, Any],
    semantic_review: Mapping[str, Any] | None = None,
    review_key: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    final_records = list(artifacts.canonical_records)
    artifact_pass = artifacts.integrity.get("overall_artifact_integrity_pass") is True
    base = v31audit.build_public_report(
        source_rows,
        final_records,
        phase="smoke",
        identity=identity,
        parsed_integrity=_v31_compat_integrity(artifact_pass),
    )
    if semantic_review is None:
        semantic = v31audit.v3._semantic_pending()
    elif review_key is None:
        raise QualityGateError("semantic_review_requires_private_key")
    else:
        semantic = aggregate_semantic_review(
            semantic_review, review_key, identity, artifacts
        )

    attempt0_counts = _status_counts(artifacts.attempt0_records)
    final_counts = _status_counts(final_records)
    attempt0_length = _length_direction_summary(
        source_rows, artifacts.attempt0_records
    )
    final_length = _length_direction_summary(source_rows, final_records)
    retry_plan = artifacts.retry_plan or {
        "attempt0_accepted": attempt0_counts["accepted"],
        "attempt0_failed": EXPECTED_COUNT - attempt0_counts["accepted"],
        "attempt0_not_applicable": attempt0_counts["not_applicable"],
        "retry_authorized": False,
        "attempt0_threshold_met": attempt0_counts["accepted"] >= 7,
    }
    retry_category_counts = Counter()
    for record in artifacts.attempt0_records:
        for category in record.get("mechanical_issue_categories", []):
            if category in runner.MECHANICAL_ISSUE_CATEGORIES:
                retry_category_counts[str(category)] += 1

    blockers = set(base["decision"]["mechanical_blocker_categories"])
    if not artifact_pass:
        blockers.add("v32_attempt_retry_canonical_integrity")
    if attempt0_counts["accepted"] < 7:
        blockers.add("attempt0_acceptance_below_7_of_8")
    if final_counts["accepted"] != EXPECTED_COUNT:
        blockers.add("final_not_all_8_accepted")
    if final_counts["not_applicable"]:
        blockers.add("final_not_applicable_present")
    if not final_length["assignment_exact_4_4"]:
        blockers.add("target_length_direction_assignment_not_4_4")
    if not final_length["all_final_pairs_match_assignment"]:
        blockers.add("realized_target_length_direction_mismatch")
    blockers = sorted(blockers)
    mechanical_pass = not blockers
    semantic_pass = semantic.get("semantic_gate_pass") is True
    canary_development_authorized = bool(mechanical_pass and semantic_pass)

    safe_integrity = {
        key: value for key, value in artifacts.integrity.items()
        if isinstance(value, (bool, int)) and not isinstance(value, str)
    }
    base["audit"] = "claude_symmetric_diverse_rewrite_v32_quality_gate"
    base["audit_version"] = AUDIT_VERSION
    base["artifact_integrity"] = safe_integrity
    base["scope"].update({
        "attempt0_record_count": len(artifacts.attempt0_records),
        "retry_record_count": len(artifacts.retry_records),
        "final_canonical_record_count": len(final_records),
    })
    base["attempt_status"] = {
        "attempt0": attempt0_counts,
        "final_canonical": final_counts,
        "attempt0_threshold_met": attempt0_counts["accepted"] >= 7,
        "retry_authorized_by_frozen_policy": retry_plan.get("retry_authorized") is True,
        "retry_executed": bool(artifacts.retry_records),
        "retry_record_count": len(artifacts.retry_records),
        "retry_mechanical_category_counts": {
            category: retry_category_counts.get(category, 0)
            for category in runner.MECHANICAL_ISSUE_CATEGORIES
        },
        "canonical_generation_attempt_counts": {
            "attempt_0": sum(
                record.get("canonical_generation_attempt") == 0
                for record in final_records
            ),
            "retry_1": sum(
                record.get("canonical_generation_attempt") == 1
                for record in final_records
            ),
            "other": sum(
                record.get("canonical_generation_attempt") not in {0, 1}
                for record in final_records
            ),
        },
        "stop_go_requirements": {
            "attempt0_at_least_7_accepted": attempt0_counts["accepted"] >= 7,
            "final_exactly_8_accepted": final_counts["accepted"] == 8,
            "final_zero_not_applicable": final_counts["not_applicable"] == 0,
        },
    }
    base["target_length_direction"] = {
        "attempt0": attempt0_length,
        "final_canonical": final_length,
        "ties_are_diagnostic_but_block_progression": True,
    }
    base["semantic_review"] = semantic
    base["decision"] = {
        "mechanical_gate_pass": mechanical_pass,
        "mechanical_blocker_categories": blockers,
        "semantic_review_required": True,
        "blind_packet_requires_final_8_accepted": True,
        "agent_review_may_authorize_canary_development": True,
        "agent_review_authorizes_production": False,
        "canary_development_authorized": canary_development_authorized,
        "production_scale_authorized": False,
    }
    return base


def build_blocked_report(stage: str) -> dict[str, Any]:
    return {
        "audit": "claude_symmetric_diverse_rewrite_v32_quality_gate",
        "audit_version": AUDIT_VERSION,
        "privacy": {
            "contains_source_or_candidate_text": False,
            "contains_source_ids": False,
            "contains_hashes": False,
            "contains_phrases_or_ngrams": False,
            "contains_reviewer_notes": False,
            "per_example_values_published": False,
            "raw_text_location": "private_data_only",
        },
        "scope": {
            "phase": "smoke", "expected_pair_count": 8,
            "attempt0_record_count": 0, "retry_record_count": 0,
            "final_canonical_record_count": 0,
        },
        "preparation": {"stage": stage, "status": "blocked"},
        "artifact_integrity": _empty_integrity(),
        "attempt_status": {
            "attempt0": _status_counts([]),
            "final_canonical": _status_counts([]),
        },
        "semantic_review": v31audit.v3._semantic_pending(),
        "decision": {
            "mechanical_gate_pass": False,
            "mechanical_blocker_categories": ["quality_gate_preparation_failure"],
            "semantic_review_required": True,
            "blind_packet_requires_final_8_accepted": True,
            "agent_review_may_authorize_canary_development": True,
            "agent_review_authorizes_production": False,
            "canary_development_authorized": False,
            "production_scale_authorized": False,
        },
    }


def assert_public_report_safe(
    report: Mapping[str, Any],
    source_rows: Sequence[dict[str, Any]],
    records: Sequence[dict[str, Any]],
    semantic_review: Mapping[str, Any] | None = None,
) -> None:
    v31audit.assert_public_report_safe(report, source_rows, records, semantic_review)


def _load_review(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    if not _is_private_path(path):
        raise QualityGateError("semantic_review_must_stay_under_private_data")
    return v31audit.v3._load_review(path)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--set", dest="phase", choices=("smoke",), required=True)
    parser.add_argument("--review", type=Path)
    parser.add_argument("--review-seed", type=int, default=v31audit.v3.DEFAULT_REVIEW_SEED)
    parser.add_argument("--public-output", type=Path)
    parser.add_argument("--packet-output", type=Path)
    parser.add_argument("--key-output", type=Path)
    args = parser.parse_args(argv)

    public_path = (
        args.public_output or PUBLIC_REPORTS / "claude_smoke_v32_quality_gate.json"
    ).resolve()
    if _is_private_path(public_path):
        raise QualityGateError("public_report_must_not_use_private_output_path")
    report = build_blocked_report("initialization")
    _atomic_json(public_path, report)
    source_rows: list[dict[str, Any]] = []
    artifacts = AuditArtifacts((), (), (), None, None, None, _empty_integrity())
    packet_path: Path | None = None
    key_path: Path | None = None
    packet_written = False
    stage = "load_config"
    try:
        config = runner.load_config(args.config.resolve(), args.phase)
        stage = "validate_frozen_input"
        source_rows, public_manifest = runner.validate_frozen_input(config)
        stage = "build_generation_identity"
        identity = runner.generation_identity(config, public_manifest, source_rows)
        tokenizer = None
        if runner._execution_artifacts_exist(config.output_dir):
            stage = "load_pinned_tokenizer_for_raw_replay"
            tokenizer = runner.v2.load_pinned_tokenizer(
                identity["generation_contract"]["validation_contract"][
                    "tokenizer_file_sha256"
                ]
            )
        stage = "load_attempt_retry_canonical_artifacts"
        artifacts = load_audit_artifacts(
            config.output_dir,
            identity,
            source_rows,
            config=config,
            tokenizer=tokenizer,
        )
        stage = "build_aggregate_report"
        report = build_public_report(source_rows, artifacts, identity=identity)
        assert_public_report_safe(report, source_rows, artifacts.canonical_records)
        _atomic_json(public_path, report)

        final_counts = _status_counts(artifacts.canonical_records)
        reviewable = bool(
            artifacts.integrity.get("overall_artifact_integrity_pass") is True
            and final_counts["accepted"] == 8
            and final_counts["not_applicable"] == 0
            and all(
                isinstance(record.get("confident_response"), str)
                and record["confident_response"].strip()
                and isinstance(record.get("hedged_response"), str)
                and record["hedged_response"].strip()
                for record in artifacts.canonical_records
            )
        )
        if reviewable:
            stage = "build_blind_review_packet"
            packet, key = build_blind_review_packet(
                source_rows,
                artifacts.canonical_records,
                identity=identity,
                artifacts=artifacts,
                seed=args.review_seed,
            )
            review_dir = config.output_dir / "review"
            packet_path = (
                args.packet_output or review_dir / "blind_review_packet.json"
            ).resolve()
            key_path = (
                args.key_output or review_dir / "blind_review_key.json"
            ).resolve()
            review_path = args.review.resolve() if args.review else None
            review = _load_review(review_path)
            if review is not None and review_path == packet_path:
                if not _is_private_path(packet_path) or not _is_private_path(key_path):
                    raise QualityGateError(
                        "blind_review_artifacts_must_stay_under_private_data"
                    )
                _atomic_json(key_path, key)
            else:
                write_blind_review_packet(packet_path, key_path, packet, key)
            packet_written = True
            if review is not None:
                stage = "ingest_semantic_review"
                report = build_public_report(
                    source_rows,
                    artifacts,
                    identity=identity,
                    semantic_review=review,
                    review_key=key,
                )
                assert_public_report_safe(
                    report, source_rows, artifacts.canonical_records, review
                )
                _atomic_json(public_path, report)
    except Exception:  # fail closed without publishing exception text
        report = build_blocked_report(stage)
        assert_public_report_safe(report, source_rows, artifacts.canonical_records)
        _atomic_json(public_path, report)

    print(json.dumps({
        "mechanical_gate_pass": report["decision"]["mechanical_gate_pass"],
        "canary_development_authorized": report["decision"][
            "canary_development_authorized"
        ],
        "production_scale_authorized": False,
        "public_report": str(public_path),
        "private_review_packet": str(packet_path) if packet_written else None,
        "private_review_key": str(key_path) if packet_written else None,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
