"""Tests for the offline v3.1 phase-specific gate; no model is invoked."""
from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from experiments.diverse_pairs_multilayer_v1.src import (
    audit_claude_canary_v31 as audit,
)
from experiments.diverse_pairs_multilayer_v1.src import (
    build_rewrite_dev_manifests_v3 as selector,
)
from experiments.diverse_pairs_multilayer_v1.src import (
    run_claude_rewrite_batches_v31 as runner,
)


def _suffix(index: int) -> str:
    return chr(97 + index // 26) + chr(97 + index % 26)


def _identity(rows: list[dict], phase: str) -> dict:
    batches = []
    for batch_index, start in enumerate(range(0, len(rows), 8), 1):
        batch_rows = rows[start:start + 8]
        batches.append({
            "batch_id": f"{phase}__batch_{batch_index:02d}__fixture",
            "batch_index": batch_index,
            "source_ids": [row["source_id"] for row in batch_rows],
            "source_hashes": [row["original_response_sha256"] for row in batch_rows],
            "source_suitability_statuses": [
                row["source_suitability_status"] for row in batch_rows
            ],
            "prompt_sha256": f"{batch_index:064x}",
            "schema_sha256": f"{batch_index + 20:064x}",
        })
    contract = {
        "runner_version": "fixture-v3.1",
        "protocol_version": "claude-symmetric-diverse-rewrite-v3.1",
        "phase": phase,
        "batches": batches,
        "validation_contract": {
            "hard_member_word_ratio": [0.8, 1.2],
            "hard_pair_qwen_token_gap": {
                "minimum_tokens": 8, "mean_fraction": 0.1,
            },
        },
    }
    contract_hash = runner.v2.sha256_bytes(runner._canonical_json_bytes(contract))
    return {
        "generation_contract": contract,
        "generation_contract_sha256": contract_hash,
        "generation_fingerprint": runner.v2.sha256_text(f"v31:{contract_hash}"),
    }


def _fixture(count: int, phase: str):
    tasks = sorted(audit.v3.SAFE_DIMENSIONS["task"])
    topologies = ("early", "middle", "late", "distributed")
    lengths = ("short", "medium", "long")
    rows: list[dict] = []
    records: list[dict] = []
    for index in range(count):
        suffix = _suffix(index)
        source_words = [f"source{suffix}{part}" for part in range(20)]
        confident_words = [f"firm{suffix}{part}" for part in range(20)]
        hedged_words = [f"tentative{suffix}{part}" for part in range(20)]
        # Counterbalance which label is one word longer without exceeding any
        # member or pair length bound.
        if index % 2:
            confident_words.append(f"extra{suffix}")
        else:
            hedged_words.append(f"extra{suffix}")
        original = " ".join(source_words)
        confident = " ".join(confident_words)
        hedged = " ".join(hedged_words)
        row = {
            "source_id": f"private-source-{index:03d}",
            "prompt": f"private prompt {suffix} that is never published",
            "original_response": original,
            "original_response_sha256": runner.v2.sha256_text(original),
            "dataset": selector.WILDCHAT if index % 4 else selector.HELPSTEER,
            "task": tasks[index % len(tasks)],
            "length_bin": lengths[index % len(lengths)],
            "rewrite_recipe": "A" if index % 2 == 0 else "B",
            "stance_topology": topologies[index % len(topologies)],
            "rewrite_output_order": (
                "confident_first" if index % 2 == 0 else "hedged_first"
            ),
            "source_suitability_status": "primary_eligible",
        }
        confident_tokens = len(audit.v3._tokens(confident))
        hedged_tokens = len(audit.v3._tokens(hedged))
        gap = abs(confident_tokens - hedged_tokens)
        gap_limit = max(8, int(0.1 * ((confident_tokens + hedged_tokens) / 2) + 0.999999))
        ratio = max(confident_tokens, hedged_tokens) / min(
            confident_tokens, hedged_tokens
        )
        record = {
            "source_id": row["source_id"],
            "original_response_sha256": row["original_response_sha256"],
            "source_suitability_status": row["source_suitability_status"],
            "rewrite_dev_set": phase,
            "rewrite_recipe": row["rewrite_recipe"],
            "stance_topology": row["stance_topology"],
            "rewrite_output_order": row["rewrite_output_order"],
            "confident_response": confident,
            "hedged_response": hedged,
            "status": "accepted",
            "validation_issues": [],
            "writer_issues": [],
            "member_stats": {},
            "pair_stats": {
                "confident_response_tokens": confident_tokens,
                "hedged_response_tokens": hedged_tokens,
                "absolute_token_gap": gap,
                "dynamic_gap_limit": gap_limit,
                "max_min_token_ratio_diagnostic": ratio,
            },
            "human_review": "pending",
        }
        rows.append(row)
        records.append(record)
    return rows, records, _identity(rows, phase)


def _integrity(identity: dict) -> dict:
    count = len(identity["generation_contract"]["batches"])
    return {
        "parsed_artifact_count": count,
        "expected_batch_count": count,
        "completed_expected_batch_count": count,
        "unexpected_batch_artifact_count": 0,
        "duplicate_batch_artifact_count": 0,
        "terminal_artifact_count": count,
        "records_hash_valid_count": count,
        "generation_fingerprint_present": True,
        "current_generation_fingerprint_match_count": count,
        "exact_batch_binding_match_count": count,
        "run_manifest_present": True,
        "run_manifest_matches_current_identity": True,
        "current_generation_contract_verified": True,
        "exact_expected_batch_set": True,
        "batch_validation_issue_count": 0,
        "artifact_readable": True,
        "all_terminal": True,
        "all_record_hashes_valid": True,
        "frozen_manifest_validated": True,
    }


def _completed_review(packet: dict, key: dict, reviewer_type: str) -> dict:
    hidden = {row["review_index"]: row for row in key["rows"]}
    reviews = []
    for row in packet["reviews"]:
        key_row = hidden[row["review_index"]]
        reviews.append({
            "review_index": row["review_index"],
            "content_preservation": "pass",
            "certainty_ordering": (
                "x_more_certain"
                if key_row["x_label"] == "confident"
                else "y_more_certain"
            ),
            "speaker_scope": "pass",
            "confound": "none",
            "formatting": "pass",
            "naturalness": "pass",
            "shortcut": "none",
            "observed_topology_x": key_row["stance_topology"],
            "observed_topology_y": key_row["stance_topology"],
            "reviewer_notes": "private note not allowed in public output",
        })
    return {
        "review_metadata": {
            "packet_id": packet["packet_id"],
            "experiment_binding_id": packet["experiment_binding_id"],
            "blind": True,
            "reviewer_type": reviewer_type,
        },
        "reviews": reviews,
    }


def test_smoke_agent_review_authorizes_only_canary():
    rows, records, identity = _fixture(8, "smoke")
    packet, key = audit.build_blind_review_packet(
        rows, records, phase="smoke", identity=identity, seed=5
    )
    review = _completed_review(packet, key, "agent")
    report = audit.build_public_report(
        rows,
        records,
        phase="smoke",
        identity=identity,
        parsed_integrity=_integrity(identity),
        semantic_review=review,
        review_key=key,
    )
    assert report["decision"]["mechanical_gate_pass"] is True
    assert report["decision"]["canary_authorized"] is True
    assert report["decision"]["scale_authorized"] is False
    assert report["decision"]["agent_review_authorizes_production_scale"] is False


def test_canary_requires_complete_human_review_for_scale():
    rows, records, identity = _fixture(32, "canary")
    packet, key = audit.build_blind_review_packet(
        rows, records, phase="canary", identity=identity, seed=7
    )
    agent = _completed_review(packet, key, "agent")
    agent_report = audit.build_public_report(
        rows,
        records,
        phase="canary",
        identity=identity,
        parsed_integrity=_integrity(identity),
        semantic_review=agent,
        review_key=key,
    )
    assert agent_report["semantic_review"]["semantic_gate_pass"] is True
    assert agent_report["decision"]["scale_authorized"] is False

    human = _completed_review(packet, key, "human")
    human_report = audit.build_public_report(
        rows,
        records,
        phase="canary",
        identity=identity,
        parsed_integrity=_integrity(identity),
        semantic_review=human,
        review_key=key,
    )
    assert human_report["semantic_review"]["human_certified"] is True
    assert human_report["decision"]["scale_authorized"] is True


def test_topology_mismatch_blocks_smoke_canary_authorization():
    rows, records, identity = _fixture(8, "smoke")
    packet, key = audit.build_blind_review_packet(
        rows, records, phase="smoke", identity=identity
    )
    review = _completed_review(packet, key, "agent")
    assigned = key["rows"][0]["stance_topology"]
    review["reviews"][0]["observed_topology_x"] = next(
        value for value in ("early", "middle", "late", "distributed")
        if value != assigned
    )
    report = audit.build_public_report(
        rows,
        records,
        phase="smoke",
        identity=identity,
        parsed_integrity=_integrity(identity),
        semantic_review=review,
        review_key=key,
    )
    assert report["semantic_review"]["semantic_gate_pass"] is False
    assert report["decision"]["canary_authorized"] is False


def test_recurring_cues_are_diagnostic_for_smoke_but_block_canary():
    smoke_rows, smoke_records, smoke_identity = _fixture(8, "smoke")
    canary_rows, canary_records, canary_identity = _fixture(32, "canary")
    for record in smoke_records:
        record["hedged_response"] = "repeated cue " + record["hedged_response"]
    for record in canary_records:
        record["hedged_response"] = "repeated cue " + record["hedged_response"]
    smoke = audit.build_public_report(
        smoke_rows,
        smoke_records,
        phase="smoke",
        identity=smoke_identity,
        parsed_integrity=_integrity(smoke_identity),
    )
    canary = audit.build_public_report(
        canary_rows,
        canary_records,
        phase="canary",
        identity=canary_identity,
        parsed_integrity=_integrity(canary_identity),
    )
    assert smoke["cue_concentration_phase_policy"]["concentration_detected"] is True
    assert smoke["cue_concentration_phase_policy"]["blocks_this_phase"] is False
    assert "recurring_cue_ngram_concentration" not in smoke["decision"][
        "mechanical_blocker_categories"
    ]
    assert "recurring_cue_ngram_concentration" in canary["decision"][
        "mechanical_blocker_categories"
    ]


def test_non_primary_source_suitability_blocks_and_is_only_aggregate():
    rows, records, identity = _fixture(8, "smoke")
    rows[0]["source_suitability_status"] = "transfer"
    report = audit.build_public_report(
        rows,
        records,
        phase="smoke",
        identity=identity,
        parsed_integrity=_integrity(identity),
    )
    assert report["source_suitability"]["counts"]["transfer"] == 1
    assert report["source_suitability"]["all_primary_eligible"] is False
    assert "source_suitability_not_primary_eligible" in report["decision"][
        "mechanical_blocker_categories"
    ]
    serialized = json.dumps(report)
    assert rows[0]["source_id"] not in serialized
    assert rows[0]["prompt"] not in serialized


def test_candidate_canary_is_blocked_until_source_review_promotes_the_freeze():
    rows, records, identity = _fixture(32, "canary")
    for row in rows:
        row["source_suitability_status"] = (
            "candidate_pending_source_only_semantic_review"
        )
    report = audit.build_public_report(
        rows,
        records,
        phase="canary",
        identity=identity,
        parsed_integrity=_integrity(identity),
    )
    assert report["source_suitability"]["counts"][
        "candidate_pending_source_only_semantic_review"
    ] == 32
    assert report["source_suitability"]["all_primary_eligible"] is False
    assert report["decision"]["mechanical_gate_pass"] is False
    assert report["decision"]["scale_authorized"] is False
    assert "source_suitability_not_primary_eligible" in report["decision"][
        "mechanical_blocker_categories"
    ]


def test_stale_identity_and_batch_binding_fail_closed(tmp_path: Path):
    rows, records, identity = _fixture(8, "smoke")
    output = tmp_path / "output"
    parsed = output / "parsed"
    parsed.mkdir(parents=True)
    contract = identity["generation_contract"]["batches"][0]
    stale = "0" * 64
    payload = {
        "generation_fingerprint": stale,
        "generation_contract_sha256": identity["generation_contract_sha256"],
        "batch_id": contract["batch_id"],
        "source_ids": contract["source_ids"],
        "source_hashes": contract["source_hashes"],
        "source_suitability_statuses": contract["source_suitability_statuses"],
        "batch_prompt_sha256": contract["prompt_sha256"],
        "terminal": True,
        "batch_validation_issues": [],
        "records": records,
        "records_sha256": runner.v2.sha256_bytes(
            runner._canonical_json_bytes(records)
        ),
    }
    (parsed / "batch.json").write_text(json.dumps(payload), encoding="utf-8")
    (output / "run_manifest.json").write_text(json.dumps(identity), encoding="utf-8")
    loaded, integrity = audit.load_parsed_records(output, identity)
    assert loaded == []
    assert integrity["artifact_readable"] is False


def test_exact_current_identity_and_ordered_batch_binding_loads(tmp_path: Path):
    rows, records, identity = _fixture(8, "smoke")
    output = tmp_path / "output"
    parsed = output / "parsed"
    parsed.mkdir(parents=True)
    contract = identity["generation_contract"]["batches"][0]
    payload = {
        "generation_fingerprint": identity["generation_fingerprint"],
        "generation_contract_sha256": identity["generation_contract_sha256"],
        "batch_id": contract["batch_id"],
        "source_ids": contract["source_ids"],
        "source_hashes": contract["source_hashes"],
        "source_suitability_statuses": contract["source_suitability_statuses"],
        "batch_prompt_sha256": contract["prompt_sha256"],
        "terminal": True,
        "batch_validation_issues": [],
        "records": records,
        "records_sha256": runner.v2.sha256_bytes(
            runner._canonical_json_bytes(records)
        ),
    }
    (parsed / "batch.json").write_text(json.dumps(payload), encoding="utf-8")
    (output / "run_manifest.json").write_text(json.dumps(identity), encoding="utf-8")
    loaded, integrity = audit.load_parsed_records(output, identity)
    assert loaded == records
    assert integrity["current_generation_contract_verified"] is True
    assert integrity["exact_batch_binding_match_count"] == 1
    assert integrity["exact_expected_batch_set"] is True
    assert integrity["all_terminal"] is True
    assert integrity["all_record_hashes_valid"] is True


def test_empty_and_partial_outputs_produce_blocked_reports():
    rows, records, identity = _fixture(8, "smoke")
    empty = _integrity(identity)
    empty.update({
        "parsed_artifact_count": 0,
        "completed_expected_batch_count": 0,
        "terminal_artifact_count": 0,
        "records_hash_valid_count": 0,
        "generation_fingerprint_present": False,
        "current_generation_fingerprint_match_count": 0,
        "exact_batch_binding_match_count": 0,
        "exact_expected_batch_set": False,
        "all_terminal": False,
        "all_record_hashes_valid": False,
    })
    report = audit.build_public_report(
        rows, [], phase="smoke", identity=identity, parsed_integrity=empty
    )
    assert report["decision"]["mechanical_gate_pass"] is False
    assert report["decision"]["canary_authorized"] is False
    assert "parsed_artifact_integrity" in report["decision"][
        "mechanical_blocker_categories"
    ]

    partial = dict(empty)
    partial.update({
        "parsed_artifact_count": 1,
        "completed_expected_batch_count": 1,
        "terminal_artifact_count": 1,
        "records_hash_valid_count": 1,
        "generation_fingerprint_present": True,
        "current_generation_fingerprint_match_count": 1,
        "exact_batch_binding_match_count": 1,
        "all_terminal": True,
        "all_record_hashes_valid": True,
    })
    partial_report = audit.build_public_report(
        rows,
        records[:4],
        phase="smoke",
        identity=identity,
        parsed_integrity=partial,
    )
    assert partial_report["decision"]["mechanical_gate_pass"] is False
    assert "incomplete_or_misaligned_records" in partial_report["decision"][
        "mechanical_blocker_categories"
    ]
    assert partial_report["decision"]["canary_authorized"] is False


def test_cli_always_writes_blocked_report_when_preparation_fails(
    tmp_path: Path, monkeypatch
):
    public = tmp_path / "blocked.json"
    monkeypatch.setattr(
        audit.runner,
        "load_config",
        lambda path, phase: (_ for _ in ()).throw(ValueError("private failure detail")),
    )
    assert audit.main([
        "--set", "smoke", "--public-output", str(public)
    ]) == 0
    report = json.loads(public.read_text(encoding="utf-8"))
    assert report["decision"]["mechanical_gate_pass"] is False
    assert report["decision"]["canary_authorized"] is False
    assert report["preparation"]["stage"] == "load_config"
    assert "private failure detail" not in json.dumps(report)


def test_public_candidate_pool_is_counted_but_never_authorized(tmp_path: Path):
    manifest = tmp_path / "freeze.json"
    manifest.write_text(json.dumps({
        "candidate_pool": {
            "count": 45,
            "required_promoted_canary_count": 32,
            "status": "candidate_pending_source_only_semantic_review",
            "role": "source_only_review_pool_not_authorized_for_generation",
            "file_name": "private-name-must-not-be-copied.jsonl",
        }
    }), encoding="utf-8")
    config = tmp_path / "config.json"
    config.write_text(json.dumps({
        "public_freeze_manifest_path": str(manifest),
    }), encoding="utf-8")
    summary = audit._candidate_pool_public_summary(config)
    assert summary == {
        "present": True,
        "count": 45,
        "required_promoted_canary_count": 32,
        "status": "candidate_pending_source_only_semantic_review",
        "role": "source_only_review_pool_not_authorized_for_generation",
        "execution_authorized": False,
    }
    assert "private-name" not in json.dumps(summary)


def test_blind_material_is_bound_to_current_identity_and_public_report_is_safe():
    rows, records, identity = _fixture(8, "smoke")
    packet, key = audit.build_blind_review_packet(
        rows, records, phase="smoke", identity=identity
    )
    assert packet["experiment_binding_id"] == key["experiment_binding_id"]
    assert key["generation_binding"]["generation_fingerprint"] == identity[
        "generation_fingerprint"
    ]
    review = _completed_review(packet, key, "agent")
    report = audit.build_public_report(
        rows,
        records,
        phase="smoke",
        identity=identity,
        parsed_integrity=_integrity(identity),
        semantic_review=review,
        review_key=key,
    )
    audit.assert_public_report_safe(report, rows, records, review)
    serialized = json.dumps(report)
    assert identity["generation_fingerprint"] not in serialized
    assert packet["experiment_binding_id"] not in serialized
    assert "private note not allowed" not in serialized


def test_stale_review_binding_is_rejected():
    rows, records, identity = _fixture(8, "smoke")
    packet, key = audit.build_blind_review_packet(
        rows, records, phase="smoke", identity=identity
    )
    review = _completed_review(packet, key, "agent")
    review["review_metadata"]["experiment_binding_id"] = "0" * 64
    try:
        audit.aggregate_semantic_review(
            review, key, identity, phase="smoke"
        )
    except audit.QualityGateError as exc:
        assert "stale_generation_binding" in str(exc)
    else:
        raise AssertionError("stale semantic review unexpectedly passed")


def test_no_non_runner_member_token_ratio_blocker_is_invented():
    rows, records, identity = _fixture(8, "smoke")
    report = audit.build_public_report(
        rows,
        records,
        phase="smoke",
        identity=identity,
        parsed_integrity=_integrity(identity),
    )
    assert "member_token_ratio" not in report["decision"][
        "mechanical_blocker_categories"
    ]
    assert report["runner_hard_checks"]["definitions"]["member_length"] == (
        "runner_unicode_word_count"
    )


def test_not_applicable_empty_row_is_blocking_but_excluded_from_candidate_metrics():
    rows, records, identity = _fixture(8, "smoke")
    records[0] = {
        **records[0],
        "confident_response": "",
        "hedged_response": "",
        "status": "not_applicable",
        "validation_issues": [],
        "writer_issues": ["source cannot support a faithful certainty contrast"],
        "member_stats": {},
        "pair_stats": {},
    }
    report = audit.build_public_report(
        rows,
        records,
        phase="smoke",
        identity=identity,
        parsed_integrity=_integrity(identity),
    )

    assert report["status_counts"]["not_applicable"] == 1
    assert report["scope"]["not_applicable_record_count"] == 1
    assert report["scope"]["candidate_metric_evaluated_pair_count"] == 7
    assert report["candidate_metric_coverage"] == {
        "matched_pair_count": 8,
        "evaluated_pair_count": 7,
        "excluded_not_applicable_count": 1,
        "excluded_statuses": ["not_applicable"],
        "policy": (
            "not_applicable rows remain in status and gate decisions but are excluded "
            "from candidate text, length, preservation, edit, shortcut, and cue metrics"
        ),
    }
    assert report["source_distance_and_edit_parity"][
        "confident_source_distance"
    ]["count"] == 7
    assert report["regex_length_diagnostics"][
        "paired_confident_minus_hedged_word_delta"
    ]["count"] == 7
    assert report["runner_hard_checks"]["protected_member_violation_count"] == 0
    assert report["runner_hard_checks"][
        "missing_or_inconsistent_runner_stats_count"
    ] == 0
    shortcut = report["shortcut_indicators"]
    assert shortcut["identical_pair_member_count"] == 0
    assert shortcut["duplicate_candidate_text_pair_count"] == 0
    assert report["decision"]["mechanical_gate_pass"] is False
    assert "not_all_records_accepted" in report["decision"][
        "mechanical_blocker_categories"
    ]
    assert "not_applicable_record_present" in report["decision"][
        "mechanical_blocker_categories"
    ]
    assert "duplicate_candidate_text" not in report["decision"][
        "mechanical_blocker_categories"
    ]
    assert "hard_preservation_violation" not in report["decision"][
        "mechanical_blocker_categories"
    ]
