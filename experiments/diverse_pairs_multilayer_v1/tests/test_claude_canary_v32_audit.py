"""Focused tests for the offline v3.2 attempt/retry/canonical gate."""
from __future__ import annotations

import json
from pathlib import Path

from experiments.diverse_pairs_multilayer_v1.src import (
    audit_claude_canary_v32 as audit,
)
from experiments.diverse_pairs_multilayer_v1.src import (
    run_claude_rewrite_batches_v32 as runner,
)


def _alpha_tag(index: int) -> str:
    return chr(ord("a") + index // 26) + chr(ord("a") + index % 26)


def _words(prefix: str, count: int) -> str:
    return " ".join(f"{prefix}{_alpha_tag(index)}" for index in range(count))


def _fixture():
    rows = []
    records = []
    for index in range(8):
        source_tag = _alpha_tag(index)
        original = _words(f"source{source_tag}x", 20)
        longer = "confident" if index < 4 else "hedged"
        confident_count = 21 if longer == "confident" else 18
        hedged_count = 18 if longer == "confident" else 21
        row = {
            "source_id": f"private-v32-source-{index}",
            "prompt": f"private prompt {index}",
            "original_response": original,
            "original_response_sha256": runner.v2.sha256_text(original),
            "source_record_sha256": runner.v2.sha256_text(f"record-{index}"),
            "dataset": (
                "nvidia/HelpSteer2" if index in {0, 4}
                else "allenai/WildChat-1M"
            ),
            "original_split": "train",
            "task": (
                "factual_explanation" if index < 4 else
                ("math_logic", "programming", "comparison_analysis", "summary_judgment")[
                    index - 4
                ]
            ),
            "length_bin": ("short", "medium", "long")[index % 3],
            "rewrite_recipe": "A" if index % 2 == 0 else "B",
            "stance_topology": ("early", "middle", "late", "distributed")[index % 4],
            "rewrite_output_order": (
                "confident_first" if index % 2 == 0 else "hedged_first"
            ),
            "target_longer_member": longer,
            "source_suitability_status": "primary_eligible",
            "source_suitability_reasons": [],
            "source_word_count": 20,
            "source_editable_token_count": 20,
            "min_substantive_replacements_or_deletions": 3,
            "confident_target_words": confident_count,
            "hedged_target_words": hedged_count,
            "desired_pair_word_gap_min": 1,
            "desired_pair_word_gap_max": 5,
            "dynamic_pair_word_gap_max": 5,
        }
        confident = _words(f"firm{source_tag}x", confident_count)
        hedged = _words(f"tentative{source_tag}x", hedged_count)
        gap = abs(confident_count - hedged_count)
        record = {
            "source_id": row["source_id"],
            "original_response_sha256": row["original_response_sha256"],
            "source_record_sha256": row["source_record_sha256"],
            "source_suitability_status": "primary_eligible",
            "rewrite_dev_set": "smoke",
            "rewrite_recipe": row["rewrite_recipe"],
            "stance_topology": row["stance_topology"],
            "rewrite_output_order": row["rewrite_output_order"],
            "target_longer_member": longer,
            "confident_target_words": confident_count,
            "hedged_target_words": hedged_count,
            "confident_response": confident,
            "hedged_response": hedged,
            "status": "accepted",
            "validation_issues": [],
            "writer_issues": [],
            "member_stats": {},
            "pair_stats": {
                "confident_response_tokens": confident_count,
                "hedged_response_tokens": hedged_count,
                "absolute_token_gap": gap,
                "dynamic_gap_limit": 8,
                "max_min_token_ratio_diagnostic": (
                    max(confident_count, hedged_count)
                    / min(confident_count, hedged_count)
                ),
                "observed_longer_member": longer,
            },
            "mechanical_issue_categories": [],
            "retry_eligible_mechanical_only": False,
            "human_review": "pending",
        }
        rows.append(row)
        records.append(record)
    identity = _identity(rows)
    return rows, records, identity


def _identity(rows: list[dict]) -> dict:
    batch_id = "v32_smoke__attempt_0__fixture"
    binding = {
        "batch_id": batch_id,
        "batch_index": 1,
        "generation_attempt": 0,
        "source_ids": [row["source_id"] for row in rows],
        "source_hashes": [row["original_response_sha256"] for row in rows],
        "source_record_hashes": [row["source_record_sha256"] for row in rows],
        "source_suitability_statuses": [
            row["source_suitability_status"] for row in rows
        ],
        "target_longer_members": [row["target_longer_member"] for row in rows],
        "confident_target_words": [row["confident_target_words"] for row in rows],
        "hedged_target_words": [row["hedged_target_words"] for row in rows],
        "prompt_sha256": "1" * 64,
        "schema_sha256": "2" * 64,
    }
    binding["attempt_fingerprint"] = runner.v2.sha256_text(
        "v32-attempt0:" + runner.v2.sha256_bytes(
            runner._canonical_json_bytes(binding)
        )
    )
    prompt_contract = {"fixture": "prompt"}
    validation_contract = {
        "hard_member_word_ratio": [0.8, 1.2],
        "hard_pair_qwen_token_gap": {
            "minimum_tokens": 8, "mean_fraction": 0.1,
        },
    }
    retry_contract = {
        "max_full_pair_retries": 1,
        "semantic_or_NA_retry": False,
        "canonical_selection": "earliest_passing_attempt",
    }
    contract = {
        "runner_version": runner.RUNNER_VERSION,
        "runtime_module_sha256": {
            "run_claude_rewrite_batches_v32": runner.v2.sha256_file(
                Path(runner.__file__)
            ),
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
        },
        "protocol_version": runner.PROTOCOL_VERSION,
        "phase": "smoke",
        "prompt_contract": prompt_contract,
        "prompt_contract_sha256": runner.v2.sha256_bytes(
            runner._canonical_json_bytes(prompt_contract)
        ),
        "validation_contract": validation_contract,
        "validation_contract_sha256": runner.v2.sha256_bytes(
            runner._canonical_json_bytes(validation_contract)
        ),
        "retry_contract": retry_contract,
        "retry_contract_sha256": runner.v2.sha256_bytes(
            runner._canonical_json_bytes(retry_contract)
        ),
        "batches": [binding],
    }
    contract_hash = runner.v2.sha256_bytes(runner._canonical_json_bytes(contract))
    return {
        "generation_contract": contract,
        "generation_contract_sha256": contract_hash,
        "generation_fingerprint": runner.v2.sha256_text(f"v32:{contract_hash}"),
    }


def _bound_attempt0(records: list[dict], identity: dict) -> list[dict]:
    fingerprint = identity["generation_contract"]["batches"][0][
        "attempt_fingerprint"
    ]
    return [
        {**record, "generation_attempt": 0, "attempt_fingerprint": fingerprint}
        for record in records
    ]


def _write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def _attempt_payload(records: list[dict], identity: dict) -> dict:
    batch = identity["generation_contract"]["batches"][0]
    return {
        "parent_generation_fingerprint": identity["generation_fingerprint"],
        "parent_generation_contract_sha256": identity[
            "generation_contract_sha256"
        ],
        "generation_attempt": 0,
        "attempt_fingerprint": batch["attempt_fingerprint"],
        "attempt_contract_sha256": identity["generation_contract_sha256"],
        "batch_id": batch["batch_id"],
        "source_ids": batch["source_ids"],
        "source_hashes": batch["source_hashes"],
        "source_record_hashes": batch["source_record_hashes"],
        "source_suitability_statuses": batch["source_suitability_statuses"],
        "target_longer_members": batch["target_longer_members"],
        "confident_target_words": batch["confident_target_words"],
        "hedged_target_words": batch["hedged_target_words"],
        "batch_prompt_sha256": batch["prompt_sha256"],
        "retry_issue_categories_by_source": {},
        "terminal": True,
        "transport_attempts": 1,
        "batch_validation_issues": [],
        "metadata": {},
        "records": records,
        "records_sha256": runner.v2.sha256_bytes(
            runner._canonical_json_bytes(records)
        ),
    }


def _write_artifacts(
    root: Path,
    rows: list[dict],
    attempt0_records: list[dict],
    identity: dict,
    *,
    retry_record: dict | None = None,
) -> audit.AuditArtifacts:
    _write_json(root / "run_manifest.json", identity)
    attempt0_records = _bound_attempt0(attempt0_records, identity)
    attempt_payload = _attempt_payload(attempt0_records, identity)
    attempt0_path = root / "attempt_0" / "parsed" / "attempt0.json"
    _write_json(attempt0_path, attempt_payload)
    plan = runner.attempt0_retry_plan(attempt0_records)
    retry_records: list[dict] = []
    retry_identity = None
    if plan["retry_authorized"]:
        assert retry_record is not None
        batch = runner.make_batches(rows, "smoke", 8)[0]
        retry_batch = runner.make_retry_batch(batch, plan)
        retry_identity = runner.retry_attempt_identity(identity, retry_batch, plan)
        retry_record = {
            **retry_record,
            "generation_attempt": 1,
            "attempt_fingerprint": retry_identity["attempt_fingerprint"],
        }
        retry_records = [retry_record]
        _write_json(root / "retry_1" / "retry_manifest.json", retry_identity)
        contract = retry_identity["attempt_contract"]
        retry_payload = {
            "parent_generation_fingerprint": identity["generation_fingerprint"],
            "parent_generation_contract_sha256": identity[
                "generation_contract_sha256"
            ],
            "generation_attempt": 1,
            "attempt_fingerprint": retry_identity["attempt_fingerprint"],
            "attempt_contract_sha256": retry_identity["attempt_contract_sha256"],
            "batch_id": contract["batch_id"],
            "source_ids": contract["source_ids"],
            "source_hashes": contract["source_hashes"],
            "source_record_hashes": contract["source_record_hashes"],
            "source_suitability_statuses": contract["source_suitability_statuses"],
            "target_longer_members": contract["target_longer_members"],
            "confident_target_words": contract["confident_target_words"],
            "hedged_target_words": contract["hedged_target_words"],
            "batch_prompt_sha256": contract["prompt_sha256"],
            "retry_issue_categories_by_source": contract[
                "retry_issue_categories_by_source"
            ],
            "terminal": True,
            "transport_attempts": 1,
            "batch_validation_issues": [],
            "metadata": {},
            "records": retry_records,
            "records_sha256": runner.v2.sha256_bytes(
                runner._canonical_json_bytes(retry_records)
            ),
        }
        retry_path = root / "retry_1" / "parsed" / "retry.json"
        _write_json(retry_path, retry_payload)
    else:
        retry_path = None

    canonical = runner.select_canonical_records(attempt0_records, retry_records)
    canonical.update({
        "terminal": True,
        "generation_fingerprint": identity["generation_fingerprint"],
        "generation_contract_sha256": identity["generation_contract_sha256"],
        "attempt_0_parsed_artifact": str(attempt0_path.relative_to(root)),
        "attempt_0_parsed_artifact_sha256": runner.v2.sha256_file(
            attempt0_path
        ),
        "retry_plan": plan,
        "retry_attempt_identity": retry_identity,
        "retry_parsed_artifact": (
            str(retry_path.relative_to(root)) if retry_path is not None else None
        ),
        "retry_parsed_artifact_sha256": (
            runner.v2.sha256_file(retry_path) if retry_path is not None else None
        ),
        "auth": {"fixture": True},
    })
    canonical_path = root / "canonical" / "selected.json"
    _write_json(canonical_path, canonical)
    status = {key: value for key, value in canonical.items() if key != "records"}
    status["canonical_artifact_sha256"] = runner.v2.sha256_file(canonical_path)
    _write_json(
        root / "status.json",
        status,
    )
    return audit.load_audit_artifacts(
        root,
        identity,
        rows,
        _allow_synthetic_fixture_without_raw_replay=True,
    )


def _mechanical_failure(record: dict) -> dict:
    return {
        **record,
        "status": "validation_failed",
        "validation_issues": ["confident:exact_word_target_mismatch"],
        "mechanical_issue_categories": ["word_target"],
        "retry_eligible_mechanical_only": True,
    }


def _completed_review(packet: dict, key: dict, reviewer_type: str = "agent") -> dict:
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
            "reviewer_notes": "private note not for the public report",
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


def test_legitimate_single_mechanical_retry_and_earliest_canonical_pass(tmp_path):
    rows, records, identity = _fixture()
    attempt0 = list(records)
    attempt0[7] = _mechanical_failure(attempt0[7])
    artifacts = _write_artifacts(
        tmp_path, rows, attempt0, identity, retry_record=records[7]
    )
    assert artifacts.integrity["overall_artifact_integrity_pass"] is True
    assert artifacts.integrity["retry_expected"] is True
    assert artifacts.integrity["retry_protocol_valid"] is True
    assert artifacts.integrity["canonical_earliest_passing_valid"] is True
    strict_without_raw_replay = audit.load_audit_artifacts(
        tmp_path, identity, rows
    )
    assert strict_without_raw_replay.integrity[
        "overall_artifact_integrity_pass"
    ] is False
    report = audit.build_public_report(rows, artifacts, identity=identity)
    assert report["attempt_status"]["attempt0"]["accepted"] == 7
    assert report["attempt_status"]["final_canonical"]["accepted"] == 8
    assert report["attempt_status"]["canonical_generation_attempt_counts"] == {
        "attempt_0": 7, "retry_1": 1, "other": 0,
    }
    assert report["decision"]["mechanical_gate_pass"] is True
    assert report["decision"]["canary_development_authorized"] is False


def test_na_or_semantic_failure_never_authorizes_retry(tmp_path):
    rows, records, identity = _fixture()
    attempt0 = list(records)
    attempt0[7] = {
        **attempt0[7],
        "status": "not_applicable",
        "confident_response": "",
        "hedged_response": "",
        "writer_issues": ["not applicable"],
        "pair_stats": {},
    }
    artifacts = _write_artifacts(tmp_path, rows, attempt0, identity)
    assert artifacts.retry_plan["retry_authorized"] is False
    # Any retry artifact, even a raw-only invocation without a manifest,
    # invalidates this chain.
    _write_json(tmp_path / "retry_1" / "raw" / "unauthorized.json", {})
    blocked = audit.load_audit_artifacts(
        tmp_path,
        identity,
        rows,
        _allow_synthetic_fixture_without_raw_replay=True,
    )
    assert blocked.integrity["retry_protocol_valid"] is False
    assert blocked.integrity["overall_artifact_integrity_pass"] is False
    report = audit.build_public_report(rows, artifacts, identity=identity)
    assert report["candidate_metric_coverage"]["excluded_not_applicable_count"] == 1
    assert report["decision"]["mechanical_gate_pass"] is False
    assert "final_not_applicable_present" in report["decision"][
        "mechanical_blocker_categories"
    ]


def test_semantic_needs_review_and_disguised_semantic_issue_never_retry(tmp_path):
    rows, records, identity = _fixture()
    needs_review = list(records)
    needs_review[7] = {
        **needs_review[7],
        "status": "needs_review",
        "validation_issues": ["writer_reported_issue"],
    }
    artifacts = _write_artifacts(tmp_path / "semantic", rows, needs_review, identity)
    assert artifacts.retry_plan["retry_authorized"] is False
    assert artifacts.integrity["overall_artifact_integrity_pass"] is True
    report = audit.build_public_report(rows, artifacts, identity=identity)
    assert report["decision"]["mechanical_gate_pass"] is False

    disguised = list(records)
    disguised[7] = {
        **disguised[7],
        "status": "validation_failed",
        "validation_issues": ["semantic_failure"],
        "mechanical_issue_categories": ["word_target"],
        "retry_eligible_mechanical_only": True,
    }
    invalid = _write_artifacts(
        tmp_path / "disguised",
        rows,
        disguised,
        identity,
        retry_record=records[7],
    )
    assert invalid.integrity["attempt0_closed_mechanical_categories"] is False
    assert invalid.integrity["overall_artifact_integrity_pass"] is False


def test_canonical_must_use_earliest_passing_attempt(tmp_path):
    rows, records, identity = _fixture()
    attempt0 = list(records)
    attempt0[7] = _mechanical_failure(attempt0[7])
    artifacts = _write_artifacts(
        tmp_path, rows, attempt0, identity, retry_record=records[7]
    )
    assert artifacts.integrity["overall_artifact_integrity_pass"] is True
    canonical_path = tmp_path / "canonical" / "selected.json"
    canonical = json.loads(canonical_path.read_text())
    canonical["records"][7] = dict(artifacts.attempt0_records[7])
    canonical["records"][7]["canonical_generation_attempt"] = 0
    canonical["records_sha256"] = runner.v2.sha256_bytes(
        runner._canonical_json_bytes(canonical["records"])
    )
    _write_json(canonical_path, canonical)
    _write_json(
        tmp_path / "status.json",
        {key: value for key, value in canonical.items() if key != "records"},
    )
    invalid = audit.load_audit_artifacts(
        tmp_path,
        identity,
        rows,
        _allow_synthetic_fixture_without_raw_replay=True,
    )
    assert invalid.integrity["canonical_records_hash_valid"] is False
    assert invalid.integrity["canonical_earliest_passing_valid"] is False
    assert invalid.integrity["overall_artifact_integrity_pass"] is False


def test_attempt0_below_seven_blocks_even_with_valid_canonical_artifact(tmp_path):
    rows, records, identity = _fixture()
    attempt0 = list(records)
    attempt0[6] = _mechanical_failure(attempt0[6])
    attempt0[7] = _mechanical_failure(attempt0[7])
    artifacts = _write_artifacts(tmp_path, rows, attempt0, identity)
    assert artifacts.integrity["overall_artifact_integrity_pass"] is True
    report = audit.build_public_report(rows, artifacts, identity=identity)
    assert report["attempt_status"]["attempt0"]["accepted"] == 6
    assert report["attempt_status"]["attempt0_threshold_met"] is False
    assert "attempt0_acceptance_below_7_of_8" in report["decision"][
        "mechanical_blocker_categories"
    ]
    assert report["decision"]["mechanical_gate_pass"] is False


def test_reversed_realized_length_direction_is_a_hard_blocker(tmp_path):
    rows, records, identity = _fixture()
    reversed_records = [dict(record) for record in records]
    first = reversed_records[0]
    first["confident_response"], first["hedged_response"] = (
        first["hedged_response"], first["confident_response"]
    )
    first["pair_stats"] = {
        **first["pair_stats"],
        "confident_response_tokens": 18,
        "hedged_response_tokens": 21,
        "observed_longer_member": "hedged",
    }
    artifacts = _write_artifacts(tmp_path, rows, reversed_records, identity)
    assert artifacts.integrity["overall_artifact_integrity_pass"] is True
    report = audit.build_public_report(rows, artifacts, identity=identity)
    final = report["target_length_direction"]["final_canonical"]
    assert final["assignment_exact_4_4"] is True
    assert final["direction_mismatch_count"] == 1
    assert final["all_final_pairs_match_assignment"] is False
    assert "realized_target_length_direction_mismatch" in report["decision"][
        "mechanical_blocker_categories"
    ]


def test_agent_blind_semantic_pass_authorizes_canary_development_only(tmp_path):
    rows, records, identity = _fixture()
    artifacts = _write_artifacts(tmp_path, rows, records, identity)
    packet, key = audit.build_blind_review_packet(
        rows, artifacts.canonical_records, identity=identity, artifacts=artifacts
    )
    review = _completed_review(packet, key, "agent")
    report = audit.build_public_report(
        rows,
        artifacts,
        identity=identity,
        semantic_review=review,
        review_key=key,
    )
    audit.assert_public_report_safe(
        report, rows, artifacts.canonical_records, review
    )
    assert report["semantic_review"]["semantic_gate_pass"] is True
    assert report["decision"]["mechanical_gate_pass"] is True
    assert report["decision"]["canary_development_authorized"] is True
    assert report["decision"]["agent_review_authorizes_production"] is False
    assert report["decision"]["production_scale_authorized"] is False


def test_stale_generation_identity_fails_closed(tmp_path):
    rows, records, identity = _fixture()
    artifacts = _write_artifacts(tmp_path, rows, records, identity)
    assert artifacts.integrity["overall_artifact_integrity_pass"] is True
    stale = dict(identity)
    stale["generation_fingerprint"] = "0" * 64
    loaded = audit.load_audit_artifacts(
        tmp_path,
        stale,
        rows,
        _allow_synthetic_fixture_without_raw_replay=True,
    )
    assert loaded.integrity["identity_self_consistent"] is False
    assert loaded.integrity["overall_artifact_integrity_pass"] is False


def test_exact_four_four_assignment_and_ties_are_hard_checked(tmp_path):
    rows, records, identity = _fixture()
    artifacts = _write_artifacts(tmp_path, rows, records, identity)
    report = audit.build_public_report(rows, artifacts, identity=identity)
    length = report["target_length_direction"]["final_canonical"]
    assert length["assignment_counts"] == {
        "confident": 4, "hedged": 4, "other": 0,
    }
    assert length["assignment_exact_4_4"] is True
    assert length["tie_count"] == 0
    assert length["all_final_pairs_match_assignment"] is True
