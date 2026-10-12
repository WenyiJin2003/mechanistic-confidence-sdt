"""Fail-closed, phase-specific quality gate for v3.1 rewrite development.

This module is deliberately offline.  It never calls Claude, Qwen, a remote
tokenizer, or any other model.  Private text is used only to construct a blind
X/Y review packet and to compute aggregate diagnostics.  The public report is
text-free.

V3.1 differs from the preserved v3 audit in four important ways:

* every artifact is bound to the *current* v3.1 generation fingerprint and
  exact ordered batch contract;
* only sources frozen as ``primary_eligible`` may pass the primary smoke or a
  future promoted canary gate (the current candidate pool is non-executable);
* recurring cue concentration is diagnostic at n=8 but a hard gate at n=32;
* an agent review may authorize only the untouched n=32 canary.  Production
  scaling always requires a complete passing human blind review of that canary.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.diverse_pairs_multilayer_v1.src import (
    audit_claude_canary_v3 as v3,
)
from experiments.diverse_pairs_multilayer_v1.src import (
    run_claude_rewrite_batches_v31 as runner,
)


BASE = Path(__file__).resolve().parents[1]
PRIVATE_ROOT = (BASE / "private_data").resolve()
DEFAULT_CONFIG = BASE / "configs" / "claude_rewrite_dev_v31.json"
PUBLIC_REPORTS = BASE / "reports"
AUDIT_VERSION = 1
EXPECTED_COUNTS = {"smoke": 8, "canary": 32}
SOURCE_SUITABILITY_FIELD = "source_suitability_status"
SOURCE_SUITABILITY_VALUES = {
    "primary_eligible",
    "candidate_pending_source_only_semantic_review",
    "transfer",
    "exclude",
}

QualityGateError = v3.QualityGateError


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _sha256(value: Any) -> str:
    return runner.v2.sha256_bytes(_canonical_bytes(value))


def _atomic_json(path: Path, value: Any) -> None:
    v3._atomic_json(path, value)


def _is_private_path(path: Path) -> bool:
    resolved = path.resolve()
    return resolved == PRIVATE_ROOT or PRIVATE_ROOT in resolved.parents


def _expected_batches(identity: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    contract = identity.get("generation_contract")
    batches = contract.get("batches") if isinstance(contract, Mapping) else None
    if not isinstance(batches, list):
        return {}
    result: dict[str, Mapping[str, Any]] = {}
    for batch in batches:
        if not isinstance(batch, Mapping) or not isinstance(batch.get("batch_id"), str):
            return {}
        batch_id = str(batch["batch_id"])
        if batch_id in result:
            return {}
        result[batch_id] = batch
    return result


def _identity_fingerprint_valid(identity: Mapping[str, Any]) -> bool:
    contract = identity.get("generation_contract")
    contract_hash = identity.get("generation_contract_sha256")
    fingerprint = identity.get("generation_fingerprint")
    return bool(
        isinstance(contract, Mapping)
        and isinstance(contract_hash, str)
        and v3.HEX64_RE.fullmatch(contract_hash)
        and isinstance(fingerprint, str)
        and v3.HEX64_RE.fullmatch(fingerprint)
        and contract_hash == runner.v2.sha256_bytes(
            runner._canonical_json_bytes(dict(contract))
        )
        and fingerprint == runner.v2.sha256_text(f"v31:{contract_hash}")
    )


def load_parsed_records(
    output_dir: Path,
    identity: Mapping[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Load only exact, terminal artifacts from the current v3.1 contract."""
    expected = _expected_batches(identity)
    expected_fingerprint = identity.get("generation_fingerprint")
    parsed_dir = output_dir / "parsed"
    paths = sorted(parsed_dir.glob("*.json")) if parsed_dir.exists() else []
    run_manifest = output_dir / "run_manifest.json"
    integrity: dict[str, Any] = {
        "parsed_artifact_count": len(paths),
        "expected_batch_count": len(expected),
        "completed_expected_batch_count": 0,
        "unexpected_batch_artifact_count": 0,
        "duplicate_batch_artifact_count": 0,
        "terminal_artifact_count": 0,
        "records_hash_valid_count": 0,
        "generation_fingerprint_present": False,
        "current_generation_fingerprint_match_count": 0,
        "exact_batch_binding_match_count": 0,
        "run_manifest_present": run_manifest.exists(),
        "run_manifest_matches_current_identity": False,
        "current_generation_contract_verified": False,
        "exact_expected_batch_set": False,
        "batch_validation_issue_count": 0,
        "artifact_readable": True,
        "all_terminal": False,
        "all_record_hashes_valid": False,
    }
    if not _identity_fingerprint_valid(identity) or not expected:
        integrity["artifact_readable"] = False
        return [], integrity
    try:
        if run_manifest.exists():
            manifest_payload = json.loads(run_manifest.read_text(encoding="utf-8"))
            integrity["run_manifest_matches_current_identity"] = manifest_payload == identity
        runner.verify_resume_artifacts(output_dir, dict(identity))
        integrity["current_generation_contract_verified"] = True
    except (OSError, TypeError, ValueError, json.JSONDecodeError):
        integrity["artifact_readable"] = False
        return [], integrity

    records: list[dict[str, Any]] = []
    observed_ids: list[str] = []
    for path in paths:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            integrity["artifact_readable"] = False
            return [], integrity
        batch_id = payload.get("batch_id")
        if not isinstance(batch_id, str) or batch_id not in expected:
            integrity["unexpected_batch_artifact_count"] += 1
            continue
        contract = expected[batch_id]
        batch_records = payload.get("records")
        if not isinstance(batch_records, list) or not all(
            isinstance(record, dict) for record in batch_records
        ):
            integrity["artifact_readable"] = False
            return [], integrity
        fingerprint = payload.get("generation_fingerprint")
        if not isinstance(fingerprint, str) or not v3.HEX64_RE.fullmatch(fingerprint):
            integrity["artifact_readable"] = False
            return [], integrity
        integrity["generation_fingerprint_present"] = True
        integrity["current_generation_fingerprint_match_count"] += int(
            fingerprint == expected_fingerprint
        )
        exact_binding = bool(
            fingerprint == expected_fingerprint
            and payload.get("generation_contract_sha256")
            == identity.get("generation_contract_sha256")
            and payload.get("source_ids") == contract.get("source_ids")
            and payload.get("source_hashes") == contract.get("source_hashes")
            and payload.get("source_suitability_statuses")
            == contract.get("source_suitability_statuses")
            and payload.get("batch_prompt_sha256") == contract.get("prompt_sha256")
            and [record.get("source_id") for record in batch_records]
            == contract.get("source_ids")
        )
        integrity["exact_batch_binding_match_count"] += int(exact_binding)
        integrity["terminal_artifact_count"] += int(payload.get("terminal") is True)
        records_hash = runner.v2.sha256_bytes(
            runner._canonical_json_bytes(batch_records)
        )
        integrity["records_hash_valid_count"] += int(
            payload.get("records_sha256") == records_hash
        )
        issues = payload.get("batch_validation_issues")
        integrity["batch_validation_issue_count"] += (
            len(issues) if isinstance(issues, list) else 1
        )
        observed_ids.append(batch_id)
        records.extend(batch_records)

    observed_counts = Counter(observed_ids)
    integrity["duplicate_batch_artifact_count"] = sum(
        count - 1 for count in observed_counts.values() if count > 1
    )
    integrity["completed_expected_batch_count"] = len(observed_counts)
    integrity["exact_expected_batch_set"] = bool(
        set(observed_counts) == set(expected)
        and integrity["duplicate_batch_artifact_count"] == 0
        and integrity["unexpected_batch_artifact_count"] == 0
    )
    integrity["all_terminal"] = bool(
        paths and integrity["terminal_artifact_count"] == len(paths)
    )
    integrity["all_record_hashes_valid"] = bool(
        paths and integrity["records_hash_valid_count"] == len(paths)
    )
    all_current = bool(
        paths
        and integrity["current_generation_fingerprint_match_count"] == len(paths)
        and integrity["exact_batch_binding_match_count"] == len(paths)
    )
    if not all_current:
        integrity["artifact_readable"] = False
        return [], integrity
    return records, integrity


def _experiment_binding(identity: Mapping[str, Any], phase: str) -> dict[str, Any]:
    contract = identity.get("generation_contract")
    if not isinstance(contract, Mapping) or not _identity_fingerprint_valid(identity):
        raise QualityGateError("generation_contract_invalid")
    fingerprint = identity.get("generation_fingerprint")
    if not isinstance(fingerprint, str) or not v3.HEX64_RE.fullmatch(fingerprint):
        raise QualityGateError("generation_fingerprint_invalid")
    return {
        "protocol_version": contract.get("protocol_version"),
        "phase": phase,
        "generation_fingerprint": fingerprint,
        "ordered_batch_contracts_sha256": _sha256(contract.get("batches")),
    }


def build_blind_review_packet(
    source_rows: Sequence[dict[str, Any]],
    records: Sequence[dict[str, Any]],
    *,
    phase: str,
    identity: Mapping[str, Any],
    seed: int = v3.DEFAULT_REVIEW_SEED,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Create private X/Y materials bound to the exact generation contract."""
    packet, key = v3.build_blind_review_packet(
        source_rows, records, phase=phase, seed=seed
    )
    binding = _experiment_binding(identity, phase)
    binding_id = _sha256(binding)
    core = {
        name: value
        for name, value in packet.items()
        if name not in {"packet_id", "review_metadata", "schema", "version"}
    }
    core.update({
        "schema": "v31-blind-semantic-review",
        "version": 1,
        "experiment_binding_id": binding_id,
    })
    packet_id = _sha256(core)
    new_packet = {
        "packet_id": packet_id,
        "review_metadata": {
            "packet_id": packet_id,
            "experiment_binding_id": binding_id,
            "blind": True,
            "reviewer_type": None,
        },
        **core,
    }
    new_key = {
        **key,
        "schema": "v31-blind-semantic-review-key",
        "version": 1,
        "packet_id": packet_id,
        "experiment_binding_id": binding_id,
        "generation_binding": binding,
    }
    return new_packet, new_key


def write_blind_review_packet(
    packet_path: Path,
    key_path: Path,
    packet: Mapping[str, Any],
    key: Mapping[str, Any],
) -> None:
    if not _is_private_path(packet_path) or not _is_private_path(key_path):
        raise QualityGateError("blind_review_artifacts_must_stay_under_private_data")
    if packet_path.resolve() == key_path.resolve():
        raise QualityGateError("blind_packet_and_key_must_be_separate")
    _atomic_json(packet_path, packet)
    _atomic_json(key_path, key)


def aggregate_semantic_review(
    review: Mapping[str, Any] | None,
    key: Mapping[str, Any],
    identity: Mapping[str, Any],
    *,
    phase: str,
) -> dict[str, Any]:
    """Decode a complete blind review and enforce the strict v3.1 semantic gate."""
    if review is None:
        return v3._semantic_pending()
    expected_binding = _experiment_binding(identity, phase)
    expected_binding_id = _sha256(expected_binding)
    metadata = review.get("review_metadata")
    if not isinstance(metadata, Mapping):
        raise QualityGateError("semantic_review_invalid")
    if (
        key.get("generation_binding") != expected_binding
        or key.get("experiment_binding_id") != expected_binding_id
        or metadata.get("experiment_binding_id") != expected_binding_id
    ):
        raise QualityGateError("semantic_review_stale_generation_binding")
    aggregate = v3.aggregate_semantic_review(review, key)
    counts = aggregate.get("counts", {})
    count = int(aggregate.get("reviewed_pair_count", 0))
    topology = aggregate.get("topology_assignment_check", {})

    def exact(field: str, value: str) -> bool:
        field_counts = counts.get(field, {})
        return isinstance(field_counts, Mapping) and field_counts.get(value) == count

    strict_pass = bool(
        aggregate.get("semantic_review_complete") is True
        and count == EXPECTED_COUNTS[phase]
        and exact("content_preservation", "pass")
        and counts.get("certainty_ordering", {}).get("correct") == count
        and exact("speaker_scope", "pass")
        and exact("confound", "none")
        and exact("formatting", "pass")
        and exact("naturalness", "pass")
        and exact("shortcut", "none")
        and topology.get("all_candidates_match_assignment") is True
    )
    aggregate["semantic_gate_pass"] = strict_pass
    aggregate["human_certified"] = bool(
        strict_pass and aggregate.get("reviewer_type") == "human"
    )
    aggregate["strict_all_pairs_required"] = True
    return aggregate


def _source_suitability(source_rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    counts = Counter()
    for row in source_rows:
        status = row.get(SOURCE_SUITABILITY_FIELD)
        counts[str(status) if status in SOURCE_SUITABILITY_VALUES else "other"] += 1
    coverage = sum(counts.values()) - counts.get("other", 0)
    total = len(source_rows)
    return {
        "field": SOURCE_SUITABILITY_FIELD,
        "counts": {
            status: counts.get(status, 0)
            for status in (
                "primary_eligible",
                "candidate_pending_source_only_semantic_review",
                "transfer",
                "exclude",
                "other",
            )
        },
        "covered_count": coverage,
        "coverage_complete": coverage == total,
        "all_primary_eligible": bool(
            total and counts.get("primary_eligible", 0) == total
        ),
    }


def _candidate_pool_public_summary(config_path: Path) -> dict[str, Any]:
    """Read only allowlisted aggregate facts from the public freeze manifest."""
    default = {
        "present": False,
        "count": 0,
        "required_promoted_canary_count": EXPECTED_COUNTS["canary"],
        "status": "unavailable",
        "role": "source_only_review_pool_not_authorized_for_generation",
        "execution_authorized": False,
    }
    try:
        raw_config = json.loads(config_path.read_text(encoding="utf-8"))
        relative = raw_config.get("public_freeze_manifest_path")
        if not isinstance(relative, str):
            return default
        manifest_path = Path(relative)
        if not manifest_path.is_absolute():
            manifest_path = BASE / manifest_path
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        pool = manifest.get("candidate_pool")
        if not isinstance(pool, Mapping):
            return default
        status = pool.get("status")
        role = pool.get("role")
        if status != "candidate_pending_source_only_semantic_review":
            status = "other"
        if role != "source_only_review_pool_not_authorized_for_generation":
            role = "other"
        count = pool.get("count")
        required = pool.get("required_promoted_canary_count")
        if not isinstance(count, int) or count < 0:
            count = 0
        if not isinstance(required, int) or required < 0:
            required = EXPECTED_COUNTS["canary"]
        return {
            "present": True,
            "count": count,
            "required_promoted_canary_count": required,
            "status": status,
            "role": role,
            "execution_authorized": False,
        }
    except (OSError, TypeError, ValueError, json.JSONDecodeError):
        return default


def _artifact_integrity_pass(integrity: Mapping[str, Any]) -> bool:
    expected = int(integrity.get("expected_batch_count", 0))
    return bool(
        integrity.get("frozen_manifest_validated") is True
        and integrity.get("artifact_readable") is True
        and integrity.get("run_manifest_present") is True
        and integrity.get("run_manifest_matches_current_identity") is True
        and integrity.get("current_generation_contract_verified") is True
        and integrity.get("exact_expected_batch_set") is True
        and int(integrity.get("parsed_artifact_count", 0)) == expected
        and int(integrity.get("completed_expected_batch_count", 0)) == expected
        and integrity.get("all_terminal") is True
        and integrity.get("all_record_hashes_valid") is True
        and integrity.get("generation_fingerprint_present") is True
        and int(integrity.get("current_generation_fingerprint_match_count", 0))
        == expected
        and int(integrity.get("exact_batch_binding_match_count", 0)) == expected
        and int(integrity.get("batch_validation_issue_count", 0)) == 0
    )


def _runner_hard_checks(
    matched: Sequence[tuple[dict[str, Any], dict[str, Any]]],
    identity: Mapping[str, Any],
) -> dict[str, Any]:
    """Recheck non-model preservation and use runner-native length definitions."""
    contract = identity.get("generation_contract", {})
    validation = contract.get("validation_contract", {}) if isinstance(contract, Mapping) else {}
    word_bounds = validation.get("hard_member_word_ratio", [0.8, 1.2])
    pair_gap = validation.get("hard_pair_qwen_token_gap", {})
    try:
        word_min, word_max = float(word_bounds[0]), float(word_bounds[1])
        minimum_gap = int(pair_gap.get("minimum_tokens", 8))
        mean_fraction = float(pair_gap.get("mean_fraction", 0.1))
    except (TypeError, ValueError, IndexError, AttributeError):
        word_min, word_max, minimum_gap, mean_fraction = 0.8, 1.2, 8, 0.1

    protected = 0
    word_ratio = 0
    pair_length = 0
    missing_runner_stats = 0
    nonempty_issue_records = 0
    suitability_record_mismatches = 0
    confident_longer = 0
    hedged_longer = 0
    ties = 0
    for source, record in matched:
        original = str(source.get("original_response", ""))
        programming = str(source.get("task", "")) == "programming"
        validation_issues = record.get("validation_issues")
        if not isinstance(validation_issues, list) or validation_issues:
            nonempty_issue_records += 1
        suitability_record_mismatches += int(
            record.get("source_suitability_status")
            != source.get("source_suitability_status")
        )
        counts: dict[str, int] = {}
        for label in ("confident", "hedged"):
            rewritten = record.get(f"{label}_response")
            rewritten = rewritten if isinstance(rewritten, str) else ""
            member_bad = False
            for pattern in (runner.v2.NUMBER_RE, runner.v2.URL_RE):
                if runner.v2._counter(pattern, original) != runner.v2._counter(
                    pattern, rewritten
                ):
                    member_bad = True
            if Counter(runner.v2.extract_code_spans(original, programming=programming)) != Counter(
                runner.v2.extract_code_spans(rewritten, programming=programming)
            ):
                member_bad = True
            for span in runner.v2.derived_protected_spans(source):
                if original.count(span) != rewritten.count(span):
                    member_bad = True
                    break
            protected += int(member_bad)
            words = runner._word_count(rewritten)
            counts[label] = words
            ratio = words / max(1, runner._word_count(original))
            word_ratio += int(not word_min <= ratio <= word_max)

        if counts["confident"] > counts["hedged"]:
            confident_longer += 1
        elif counts["hedged"] > counts["confident"]:
            hedged_longer += 1
        else:
            ties += 1

        pair_stats = record.get("pair_stats")
        if not isinstance(pair_stats, Mapping):
            missing_runner_stats += 1
            continue
        try:
            confident_tokens = int(pair_stats["confident_response_tokens"])
            hedged_tokens = int(pair_stats["hedged_response_tokens"])
            observed_gap = int(pair_stats["absolute_token_gap"])
            observed_limit = int(pair_stats["dynamic_gap_limit"])
            observed_ratio = float(pair_stats["max_min_token_ratio_diagnostic"])
        except (KeyError, TypeError, ValueError):
            missing_runner_stats += 1
            continue
        expected_gap = abs(confident_tokens - hedged_tokens)
        expected_limit = max(
            minimum_gap,
            math.ceil(mean_fraction * ((confident_tokens + hedged_tokens) / 2)),
        )
        expected_ratio = max(confident_tokens, hedged_tokens) / max(
            1, min(confident_tokens, hedged_tokens)
        )
        stats_match = bool(
            observed_gap == expected_gap
            and observed_limit == expected_limit
            and math.isclose(observed_ratio, expected_ratio, rel_tol=0.0, abs_tol=1e-9)
        )
        if not stats_match:
            missing_runner_stats += 1
        pair_length += int(expected_gap > expected_limit)

    non_ties = confident_longer + hedged_longer
    confident_share = confident_longer / non_ties if non_ties else None
    label_length_imbalance = bool(
        confident_share is not None and not 0.25 <= confident_share <= 0.75
    )
    return {
        "definitions": {
            "member_length": "runner_unicode_word_count",
            "pair_length": "runner_cached_tokenizer_response_tokens",
            "member_word_ratio_bounds": [word_min, word_max],
            "pair_token_gap_minimum": minimum_gap,
            "pair_token_gap_mean_fraction": mean_fraction,
            "pair_token_ratio": "diagnostic_only_not_a_blocker",
        },
        "protected_member_violation_count": protected,
        "member_word_ratio_violation_count": word_ratio,
        "pair_token_contract_violation_count": pair_length,
        "missing_or_inconsistent_runner_stats_count": missing_runner_stats,
        "record_with_nonempty_or_invalid_validation_issues_count": nonempty_issue_records,
        "source_suitability_record_mismatch_count": suitability_record_mismatches,
        "confident_longer_word_count": confident_longer,
        "hedged_longer_word_count": hedged_longer,
        "word_tie_count": ties,
        "confident_longer_word_share_among_non_ties": (
            None if confident_share is None else round(confident_share, 6)
        ),
        "label_length_direction_imbalance": label_length_imbalance,
    }


def _cue_concentration_blocked(report: Mapping[str, Any]) -> bool:
    shortcut = report.get("shortcut_indicators", {})
    cue = shortcut.get("recurring_novel_cue_ngram_concentration_by_label", {})
    if not isinstance(cue, Mapping):
        return True
    for label in ("confident", "hedged"):
        sizes = cue.get(label, {})
        if not isinstance(sizes, Mapping):
            return True
        for size in (1, 2, 3):
            values = sizes.get(f"{size}_gram", {})
            if not isinstance(values, Mapping):
                return True
            frequency = int(values.get("maximum_document_frequency", 0))
            share = float(values.get("maximum_document_share", 0.0))
            exclusive_frequency = int(
                values.get("maximum_label_exclusive_document_frequency", 0)
            )
            exclusive_share = float(
                values.get("maximum_label_exclusive_document_share", 0.0)
            )
            minimum = int(values.get("gate_minimum_document_count", 0))
            maximum = float(values.get("gate_maximum_document_share", 0.0))
            if (
                frequency >= minimum and share > maximum
            ) or (
                exclusive_frequency >= minimum and exclusive_share > maximum
            ):
                return True
    return False


def _repeated_template_blocked(report: Mapping[str, Any]) -> bool:
    shortcut = report.get("shortcut_indicators", {})
    deltas = shortcut.get("delta_repetition_by_label", {})
    allowed = int(shortcut.get("allowed_largest_repeated_cluster", 0))
    if not isinstance(deltas, Mapping):
        return True
    return any(
        int((deltas.get(label) or {}).get("largest_near_duplicate_cluster", 0))
        > allowed
        for label in ("confident", "hedged")
    )


def build_public_report(
    source_rows: Sequence[dict[str, Any]],
    records: Sequence[dict[str, Any]],
    *,
    phase: str,
    identity: Mapping[str, Any],
    parsed_integrity: Mapping[str, Any] | None = None,
    semantic_review: Mapping[str, Any] | None = None,
    review_key: Mapping[str, Any] | None = None,
    candidate_pool: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a privacy-safe aggregate report with phase-specific decisions."""
    if phase not in EXPECTED_COUNTS:
        raise QualityGateError("unknown_phase")
    integrity = dict(parsed_integrity or {})
    matched, alignment = v3._record_map(source_rows, records)
    # A legitimate ``not_applicable`` record has no candidate text.  It still
    # participates in artifact integrity, status, composition, acceptance, and
    # the fail-closed decision, but it must not be treated as an empty rewrite
    # for candidate-level diagnostics.
    evaluable_matched = [
        (source, record)
        for source, record in matched
        if record.get("status") != "not_applicable"
    ]
    evaluable_sources = [source for source, _ in evaluable_matched]
    evaluable_records = [record for _, record in evaluable_matched]
    not_applicable_count = sum(
        record.get("status") == "not_applicable" for record in records
    )
    base = v3.build_public_report(
        source_rows,
        records,
        phase=phase,
        parsed_integrity=integrity,
    )
    metric_base = v3.build_public_report(
        evaluable_sources,
        evaluable_records,
        phase=phase,
        parsed_integrity={},
    )
    if semantic_review is None:
        semantic = v3._semantic_pending()
    elif review_key is None:
        raise QualityGateError("semantic_review_requires_private_key")
    else:
        semantic = aggregate_semantic_review(
            semantic_review, review_key, identity, phase=phase
        )

    suitability = _source_suitability(source_rows)
    hard = _runner_hard_checks(evaluable_matched, identity)
    statuses = Counter(record.get("status") for record in records)
    shortcut = metric_base.get("shortcut_indicators", {})
    wrappers = shortcut.get("boundary_wrapper_count_by_label", {})
    wrapper_count = sum(int(wrappers.get(label, 0)) for label in ("confident", "hedged"))
    duplicate_count = int(shortcut.get("identical_pair_member_count", 0)) + int(
        shortcut.get("duplicate_candidate_text_pair_count", 0)
    )
    source_distance_gap = float(
        metric_base.get("source_distance_and_edit_parity", {}).get(
            "absolute_mean_source_distance_gap", 0.0
        )
    )
    cue_blocked = _cue_concentration_blocked(metric_base)
    repeated_templates = _repeated_template_blocked(metric_base)

    blockers: list[str] = []
    expected_count = EXPECTED_COUNTS[phase]
    if len(source_rows) != expected_count:
        blockers.append("wrong_phase_source_count")
    if not alignment.get("complete_and_aligned"):
        blockers.append("incomplete_or_misaligned_records")
    if not _artifact_integrity_pass(integrity):
        blockers.append("parsed_artifact_integrity")
    if not suitability["coverage_complete"] or not suitability["all_primary_eligible"]:
        blockers.append("source_suitability_not_primary_eligible")
    if statuses.get("accepted", 0) != expected_count or len(records) != expected_count:
        blockers.append("not_all_records_accepted")
    if not_applicable_count:
        blockers.append("not_applicable_record_present")
    if hard["record_with_nonempty_or_invalid_validation_issues_count"]:
        blockers.append("runner_validation_issues_present")
    if hard["source_suitability_record_mismatch_count"]:
        blockers.append("source_suitability_record_mismatch")
    if hard["protected_member_violation_count"]:
        blockers.append("hard_preservation_violation")
    if hard["member_word_ratio_violation_count"]:
        blockers.append("member_word_ratio")
    if (
        hard["pair_token_contract_violation_count"]
        or hard["missing_or_inconsistent_runner_stats_count"]
    ):
        blockers.append("pair_token_length_contract")
    if hard["label_length_direction_imbalance"]:
        blockers.append("label_length_direction_imbalance")
    if wrapper_count:
        blockers.append("boundary_wrapper")
    if duplicate_count:
        blockers.append("duplicate_candidate_text")
    if repeated_templates:
        blockers.append("repeated_exact_or_near_duplicate_template")
    if source_distance_gap > 0.05:
        blockers.append("source_distance_label_imbalance")
    if phase == "canary" and cue_blocked:
        blockers.append("recurring_cue_ngram_concentration")
    blockers = sorted(set(blockers))
    mechanical_pass = not blockers
    semantic_pass = semantic.get("semantic_gate_pass") is True
    canary_authorized = bool(
        phase == "smoke" and mechanical_pass and semantic_pass
    )
    scale_authorized = bool(
        phase == "canary"
        and mechanical_pass
        and semantic_pass
        and semantic.get("human_certified") is True
    )

    base["audit"] = "claude_symmetric_diverse_rewrite_v31_quality_gate"
    base["audit_version"] = AUDIT_VERSION
    base["scope"] = {
        "phase": phase,
        "expected_pair_count": expected_count,
        "frozen_source_count": len(source_rows),
        "observed_record_count": len(records),
        "matched_pair_count": len(matched),
        "candidate_metric_evaluated_pair_count": len(evaluable_matched),
        "not_applicable_record_count": not_applicable_count,
    }
    base["artifact_integrity"] = {**alignment, **{
        key: value for key, value in integrity.items()
        if isinstance(value, (bool, int, float)) and not isinstance(value, str)
    }}
    base["source_suitability"] = suitability
    if candidate_pool is not None:
        base["candidate_pool"] = dict(candidate_pool)
    base["runner_hard_checks"] = hard
    base["candidate_metric_coverage"] = {
        "matched_pair_count": len(matched),
        "evaluated_pair_count": len(evaluable_matched),
        "excluded_not_applicable_count": not_applicable_count,
        "excluded_statuses": ["not_applicable"],
        "policy": (
            "not_applicable rows remain in status and gate decisions but are excluded "
            "from candidate text, length, preservation, edit, shortcut, and cue metrics"
        ),
    }
    base["source_distance_and_edit_parity"] = metric_base[
        "source_distance_and_edit_parity"
    ]
    base["output_order_effects"] = metric_base["output_order_effects"]
    base["shortcut_indicators"] = metric_base["shortcut_indicators"]
    # Regex token counts remain useful diagnostics, but they are not the runner
    # contract and therefore never create a v3.1 blocker.
    base.pop("length_parity", None)
    base["regex_length_diagnostics"] = metric_base.get("length_parity", {})
    base["semantic_review"] = semantic
    base["cue_concentration_phase_policy"] = {
        "mode": "diagnostic_only_small_n" if phase == "smoke" else "hard_gate",
        "concentration_detected": cue_blocked,
        "blocks_this_phase": bool(phase == "canary" and cue_blocked),
    }
    base["decision"] = {
        "mechanical_gate_pass": mechanical_pass,
        "mechanical_blocker_categories": blockers,
        "semantic_review_required": True,
        "smoke_agent_review_may_authorize_canary_only": True,
        "human_review_required_for_scale": True,
        "agent_review_authorizes_production_scale": False,
        "canary_authorized": canary_authorized,
        "scale_authorized": scale_authorized,
    }
    return base


def build_blocked_report(
    *,
    phase: str,
    blocker: str,
    preparation_stage: str,
    candidate_pool: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Minimal text-free report written even when preparation cannot be read."""
    expected = EXPECTED_COUNTS.get(phase, 0)
    report = {
        "audit": "claude_symmetric_diverse_rewrite_v31_quality_gate",
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
            "phase": phase,
            "expected_pair_count": expected,
            "frozen_source_count": 0,
            "observed_record_count": 0,
            "matched_pair_count": 0,
        },
        "preparation": {"stage": preparation_stage, "status": "blocked"},
        "source_suitability": {
            "field": SOURCE_SUITABILITY_FIELD,
            "counts": {
                "primary_eligible": 0,
                "candidate_pending_source_only_semantic_review": 0,
                "transfer": 0,
                "exclude": 0,
                "other": 0,
            },
            "covered_count": 0,
            "coverage_complete": False,
            "all_primary_eligible": False,
        },
        "semantic_review": v3._semantic_pending(),
        "decision": {
            "mechanical_gate_pass": False,
            "mechanical_blocker_categories": [blocker],
            "semantic_review_required": True,
            "smoke_agent_review_may_authorize_canary_only": True,
            "human_review_required_for_scale": True,
            "agent_review_authorizes_production_scale": False,
            "canary_authorized": False,
            "scale_authorized": False,
        },
    }
    if candidate_pool is not None:
        report["candidate_pool"] = dict(candidate_pool)
    return report


def assert_public_report_safe(
    report: Mapping[str, Any],
    source_rows: Sequence[dict[str, Any]],
    records: Sequence[dict[str, Any]],
    semantic_review: Mapping[str, Any] | None = None,
) -> None:
    v3.assert_public_report_safe(report, source_rows, records, semantic_review)


def _load_review(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    if not _is_private_path(path):
        raise QualityGateError("semantic_review_must_stay_under_private_data")
    return v3._load_review(path)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--set", dest="phase", choices=("smoke", "canary"), required=True)
    parser.add_argument("--review", type=Path)
    parser.add_argument("--review-seed", type=int, default=v3.DEFAULT_REVIEW_SEED)
    parser.add_argument("--public-output", type=Path)
    parser.add_argument("--packet-output", type=Path)
    parser.add_argument("--key-output", type=Path)
    args = parser.parse_args(argv)

    public_path = (
        args.public_output
        or PUBLIC_REPORTS / f"claude_{args.phase}_v31_quality_gate.json"
    ).resolve()
    if _is_private_path(public_path):
        raise QualityGateError("public_report_must_not_use_private_output_path")

    candidate_pool = _candidate_pool_public_summary(args.config.resolve())

    # Establish an auditable failure artifact before reading any private input.
    report = build_blocked_report(
        phase=args.phase,
        blocker="preparation_incomplete",
        preparation_stage="initialization",
        candidate_pool=candidate_pool,
    )
    _atomic_json(public_path, report)
    source_rows: list[dict[str, Any]] = []
    records: list[dict[str, Any]] = []
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
        stage = "load_parsed_records"
        records, parsed_integrity = load_parsed_records(config.output_dir, identity)
        parsed_integrity["frozen_manifest_validated"] = True
        review_dir = config.output_dir / "review"
        packet_path = (args.packet_output or review_dir / "blind_review_packet.json").resolve()
        key_path = (args.key_output or review_dir / "blind_review_key.json").resolve()

        stage = "build_aggregate_report"
        report = build_public_report(
            source_rows,
            records,
            phase=args.phase,
            identity=identity,
            parsed_integrity=parsed_integrity,
            candidate_pool=candidate_pool,
        )
        assert_public_report_safe(report, source_rows, records)
        _atomic_json(public_path, report)

        matched, alignment = v3._record_map(source_rows, records)
        reviewable = bool(
            alignment.get("complete_and_aligned")
            and matched
            and _artifact_integrity_pass(parsed_integrity)
            and all(
                record.get("status") == "accepted"
                and isinstance(record.get("confident_response"), str)
                and record["confident_response"].strip()
                and isinstance(record.get("hedged_response"), str)
                and record["hedged_response"].strip()
                for _, record in matched
            )
        )
        if reviewable:
            stage = "build_blind_review_packet"
            packet, key = build_blind_review_packet(
                source_rows,
                records,
                phase=args.phase,
                identity=identity,
                seed=args.review_seed,
            )
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
                    records,
                    phase=args.phase,
                    identity=identity,
                    parsed_integrity=parsed_integrity,
                    semantic_review=review,
                    review_key=key,
                    candidate_pool=candidate_pool,
                )
                assert_public_report_safe(report, source_rows, records, review)
                _atomic_json(public_path, report)
    except Exception:  # fail closed without publishing exception text
        report = build_blocked_report(
            phase=args.phase,
            blocker="quality_gate_preparation_failure",
            preparation_stage=stage,
            candidate_pool=candidate_pool,
        )
        assert_public_report_safe(report, source_rows, records)
        _atomic_json(public_path, report)

    print(json.dumps({
        "phase": args.phase,
        "mechanical_gate_pass": report["decision"]["mechanical_gate_pass"],
        "canary_authorized": report["decision"]["canary_authorized"],
        "scale_authorized": report["decision"]["scale_authorized"],
        "public_report": str(public_path),
        "private_review_packet": str(packet_path) if packet_written else None,
        "private_review_key": str(key_path) if packet_written else None,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
