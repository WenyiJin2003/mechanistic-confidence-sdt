"""Focused tests for the offline v3 quality gate; no model is invoked."""
from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from experiments.diverse_pairs_multilayer_v1.src import (
    audit_claude_canary_v3 as audit,
)
from experiments.diverse_pairs_multilayer_v1.src import (
    build_rewrite_dev_manifests_v3 as selector,
)
from experiments.diverse_pairs_multilayer_v1.src import (
    run_claude_rewrite_batches_v3 as runner,
)


def _letters(index: int) -> str:
    return chr(ord("a") + index // 26) + chr(ord("a") + index % 26)


def _fixture(count: int = 32):
    tasks = sorted(audit.SAFE_DIMENSIONS["task"])
    lengths = ("short", "medium", "long")
    topologies = ("early", "middle", "late", "distributed")
    rows = []
    records = []
    for index in range(count):
        suffix = _letters(index)
        source_terms = [f"source{suffix}{chr(97 + part)}" for part in range(12)]
        confident_terms = [f"firm{suffix}{chr(97 + part)}" for part in range(12)]
        hedged_terms = [f"tentative{suffix}{chr(97 + part)}" for part in range(12)]
        original = " ".join(source_terms)
        confident = " ".join(confident_terms)
        hedged = " ".join(hedged_terms)
        order = "confident_first" if index % 2 == 0 else "hedged_first"
        row = {
            "source_id": f"private-source-{index:03d}",
            "prompt": f"private prompt {suffix} that must never be public",
            "original_response": original,
            "original_response_sha256": runner.v2.sha256_text(original),
            "dataset": selector.WILDCHAT if index % 4 else selector.HELPSTEER,
            "task": tasks[index % len(tasks)],
            "length_bin": lengths[index % len(lengths)],
            "rewrite_recipe": "A" if index % 2 == 0 else "B",
            "stance_topology": topologies[index % len(topologies)],
            "rewrite_output_order": order,
        }
        rows.append(row)
        records.append({
            "source_id": row["source_id"],
            "original_response_sha256": row["original_response_sha256"],
            "rewrite_dev_set": "canary" if count == 32 else "smoke",
            "rewrite_recipe": row["rewrite_recipe"],
            "stance_topology": row["stance_topology"],
            "rewrite_output_order": order,
            "confident_response": confident,
            "hedged_response": hedged,
            "status": "accepted",
            "validation_issues": [],
            "writer_issues": [],
            "member_stats": {},
            "pair_stats": {},
            "human_review": "pending",
        })
    return rows, records


def _integrity(batch_count: int = 4) -> dict:
    return {
        "parsed_artifact_count": batch_count,
        "expected_batch_count": batch_count,
        "completed_expected_batch_count": batch_count,
        "unexpected_batch_artifact_count": 0,
        "duplicate_batch_artifact_count": 0,
        "terminal_artifact_count": batch_count,
        "records_hash_valid_count": batch_count,
        "generation_fingerprint_present": True,
        "current_generation_fingerprint_match_count": batch_count,
        "run_manifest_present": True,
        "run_manifest_matches_current_identity": True,
        "current_generation_contract_verified": True,
        "exact_expected_batch_set": True,
        "frozen_manifest_validated": True,
        "artifact_readable": True,
        "batch_validation_issue_count": 0,
        "all_terminal": True,
        "all_record_hashes_valid": True,
    }


def _completed_review(packet: dict, key: dict, reviewer_type: str) -> dict:
    key_by_index = {row["review_index"]: row for row in key["rows"]}
    reviews = []
    for packet_row in packet["reviews"]:
        index = packet_row["review_index"]
        observed = (
            "x_more_certain"
            if key_by_index[index]["x_label"] == "confident"
            else "y_more_certain"
        )
        reviews.append({
            "review_index": index,
            "content_preservation": "pass",
            "certainty_ordering": observed,
            "speaker_scope": "pass",
            "confound": "none",
            "formatting": "pass",
            "naturalness": "pass",
            "shortcut": "none",
            "observed_topology_x": key_by_index[index]["stance_topology"],
            "observed_topology_y": key_by_index[index]["stance_topology"],
            "reviewer_notes": "private semantic note that must never be published",
        })
    return {
        "review_metadata": {
            "packet_id": packet["packet_id"],
            "blind": True,
            "reviewer_type": reviewer_type,
        },
        "reviews": reviews,
    }


def test_blind_packet_hides_labels_recipe_topology_order_and_identity():
    rows, records = _fixture(8)
    first_packet, first_key = audit.build_blind_review_packet(
        rows, records, phase="smoke", seed=7
    )
    second_packet, second_key = audit.build_blind_review_packet(
        rows, records, phase="smoke", seed=7
    )
    assert first_packet == second_packet and first_key == second_key
    serialized = json.dumps(first_packet)
    for forbidden in (
        "source_id", "original_response_sha256", "rewrite_recipe",
        "stance_topology", "rewrite_output_order", '"x_label"', '"y_label"',
    ):
        assert forbidden not in serialized
    for row in rows:
        assert row["source_id"] not in serialized
    assert all(
        {
            "source_prompt", "source_response", "candidate_x", "candidate_y",
            "content_preservation", "certainty_ordering", "speaker_scope",
            "confound", "formatting", "naturalness", "shortcut",
            "observed_topology_x", "observed_topology_y",
        }
        <= set(row)
        for row in first_packet["reviews"]
    )
    assert all(
        {"x_label", "y_label", "rewrite_recipe", "stance_topology", "rewrite_output_order"}
        <= set(row)
        for row in first_key["rows"]
    )


def test_blind_packet_and_key_can_only_be_written_under_private_data(tmp_path):
    rows, records = _fixture(8)
    packet, key = audit.build_blind_review_packet(rows, records, phase="smoke")
    with pytest.raises(audit.QualityGateError, match="private_data"):
        audit.write_blind_review_packet(
            tmp_path / "public_packet.json", tmp_path / "public_key.json", packet, key
        )


def test_public_report_is_text_free_and_pending_review_blocks_scale():
    rows, records = _fixture(32)
    report = audit.build_public_report(
        rows, records, phase="canary", parsed_integrity=_integrity()
    )
    audit.assert_public_report_safe(report, rows, records)
    serialized = json.dumps(report)
    assert report["decision"]["scale_authorized"] is False
    assert report["semantic_review"]["status"] == "pending"
    assert report["privacy"]["contains_phrases_or_ngrams"] is False
    for row, record in zip(rows, records):
        for value in (
            row["source_id"], row["prompt"], row["original_response"],
            row["original_response_sha256"], record["confident_response"],
            record["hedged_response"],
        ):
            assert value not in serialized
    assert not audit.HEX64_RE.search(serialized)


def test_required_mechanical_summaries_and_all_breakdowns_are_present():
    rows, records = _fixture(32)
    report = audit.build_public_report(
        rows, records, phase="canary", parsed_integrity=_integrity()
    )
    assert report["decision"]["mechanical_gate_pass"] is True
    assert set(report["acceptance_by_group"]) == set(audit.SAFE_DIMENSIONS)
    assert "paired_confident_minus_hedged_source_distance" in report[
        "source_distance_and_edit_parity"
    ]
    assert "paired_confident_minus_hedged_token_delta" in report["length_parity"]
    assert "confident_longer_token_share_among_non_ties" in report["length_parity"]
    assert set(report["output_order_effects"]) == {
        "confident_first", "hedged_first"
    }
    shortcuts = report["shortcut_indicators"]
    assert "edit_shape_repetition_by_label" in shortcuts
    assert "delta_repetition_by_label" in shortcuts
    assert "duplicate_candidate_text_pair_count" in shortcuts
    assert "recurring_novel_cue_ngram_concentration_by_label" in shortcuts


def test_recurring_candidate_cue_ngram_concentration_is_aggregate_and_blocking():
    rows, records = _fixture(32)
    repeated_phrase = ["commoncue", "perhaps", "uncertainly"]
    for record in records[:20]:
        words = record["hedged_response"].split()
        record["hedged_response"] = " ".join(repeated_phrase + words[3:])
    report = audit.build_public_report(
        rows, records, phase="canary", parsed_integrity=_integrity()
    )
    assert "recurring_cue_ngram_concentration" in report["decision"][
        "mechanical_blocker_categories"
    ]
    cue_stats = report["shortcut_indicators"][
        "recurring_novel_cue_ngram_concentration_by_label"
    ]["hedged"]["3_gram"]
    assert cue_stats["maximum_document_frequency"] >= 20
    serialized = json.dumps(report)
    assert "commoncue" not in serialized
    assert "perhaps uncertainly" not in serialized
    audit.assert_public_report_safe(report, rows, records)


def test_agent_review_can_pass_semantics_but_only_human_can_authorize_scale():
    rows, records = _fixture(32)
    packet, key = audit.build_blind_review_packet(
        rows, records, phase="canary", seed=99
    )
    agent_review = _completed_review(packet, key, "agent")
    agent_report = audit.build_public_report(
        rows,
        records,
        phase="canary",
        parsed_integrity=_integrity(),
        semantic_review=agent_review,
        review_key=key,
    )
    assert agent_report["semantic_review"]["semantic_gate_pass"] is True
    assert agent_report["semantic_review"]["human_certified"] is False
    assert agent_report["decision"]["scale_authorized"] is False

    human_review = _completed_review(packet, key, "human")
    human_report = audit.build_public_report(
        rows,
        records,
        phase="canary",
        parsed_integrity=_integrity(),
        semantic_review=human_review,
        review_key=key,
    )
    audit.assert_public_report_safe(human_report, rows, records, human_review)
    assert human_report["semantic_review"]["human_certified"] is True
    assert human_report["semantic_review"]["topology_assignment_check"][
        "all_candidates_match_assignment"
    ] is True
    assert human_report["decision"]["scale_authorized"] is True


def test_semantic_failure_and_mechanical_wrapper_block_authorization():
    rows, records = _fixture(32)
    packet, key = audit.build_blind_review_packet(rows, records, phase="canary")
    review = _completed_review(packet, key, "human")
    review["reviews"][0]["speaker_scope"] = "fail"
    report = audit.build_public_report(
        rows,
        records,
        phase="canary",
        parsed_integrity=_integrity(),
        semantic_review=review,
        review_key=key,
    )
    assert report["semantic_review"]["semantic_gate_pass"] is False
    assert report["decision"]["scale_authorized"] is False

    bad_records = [dict(record) for record in records]
    bad_records[0]["confident_response"] = (
        "certainly " + rows[0]["original_response"]
    )
    bad_records[0]["status"] = "accepted"
    bad_report = audit.build_public_report(
        rows, bad_records, phase="canary", parsed_integrity=_integrity()
    )
    assert "boundary_wrapper" in bad_report["decision"]["mechanical_blocker_categories"]
    assert bad_report["decision"]["mechanical_gate_pass"] is False


def test_blind_observed_topology_must_match_hidden_assignment():
    rows, records = _fixture(32)
    packet, key = audit.build_blind_review_packet(rows, records, phase="canary")
    review = _completed_review(packet, key, "human")
    assigned = key["rows"][0]["stance_topology"]
    review["reviews"][0]["observed_topology_x"] = next(
        value for value in ("early", "middle", "late", "distributed")
        if value != assigned
    )
    report = audit.build_public_report(
        rows,
        records,
        phase="canary",
        parsed_integrity=_integrity(),
        semantic_review=review,
        review_key=key,
    )
    topology = report["semantic_review"]["topology_assignment_check"]
    assert topology["candidate_mismatch_count"] == 1
    assert topology["all_candidates_match_assignment"] is False
    assert report["semantic_review"]["semantic_gate_pass"] is False
    assert report["decision"]["scale_authorized"] is False


def test_semantic_review_index_and_value_validation_is_fail_closed():
    rows, records = _fixture(8)
    packet, key = audit.build_blind_review_packet(rows, records, phase="smoke")
    review = _completed_review(packet, key, "human")
    review["reviews"][0]["certainty_ordering"] = "confident"
    with pytest.raises(audit.QualityGateError, match="certainty_ordering"):
        audit.aggregate_semantic_review(review, key)


def test_load_parsed_records_checks_terminal_and_record_hashes(tmp_path: Path):
    rows, records = _fixture(8)
    parsed = tmp_path / "out" / "parsed"
    parsed.mkdir(parents=True)
    batch_id = "smoke__batch_01__fixture"
    fingerprint = "f" * 64
    contract = {
        "batch_id": batch_id,
        "source_ids": [row["source_id"] for row in rows],
        "source_hashes": [row["original_response_sha256"] for row in rows],
        "prompt_sha256": "p" * 64,
    }
    identity = {
        "generation_fingerprint": fingerprint,
        "generation_contract": {"batches": [contract]},
    }
    payload = {
        "generation_fingerprint": fingerprint,
        "batch_id": batch_id,
        "source_ids": contract["source_ids"],
        "source_hashes": contract["source_hashes"],
        "batch_prompt_sha256": contract["prompt_sha256"],
        "terminal": True,
        "batch_validation_issues": [],
        "records": records,
        "records_sha256": runner.v2.sha256_bytes(
            runner._canonical_json_bytes(records)
        ),
    }
    (parsed / "batch.json").write_text(json.dumps(payload), encoding="utf-8")
    (tmp_path / "out" / "run_manifest.json").write_text(
        json.dumps(identity), encoding="utf-8"
    )
    loaded, integrity = audit.load_parsed_records(tmp_path / "out", identity)
    assert loaded == records
    assert integrity["all_terminal"] is True
    assert integrity["all_record_hashes_valid"] is True
    assert integrity["exact_expected_batch_set"] is True
    assert integrity["run_manifest_matches_current_identity"] is True


@pytest.mark.parametrize("bad_fingerprint", [None, 7, "0" * 64])
def test_wrong_or_missing_generation_fingerprint_fails_closed(
    tmp_path: Path, bad_fingerprint
):
    rows, records = _fixture(8)
    output = tmp_path / "out"
    parsed = output / "parsed"
    parsed.mkdir(parents=True)
    batch_id = "smoke__batch_01__fixture"
    identity = {
        "generation_fingerprint": "f" * 64,
        "generation_contract": {"batches": [{
            "batch_id": batch_id,
            "source_ids": [row["source_id"] for row in rows],
            "source_hashes": [row["original_response_sha256"] for row in rows],
            "prompt_sha256": "p" * 64,
        }]},
    }
    payload = {
        "generation_fingerprint": bad_fingerprint,
        "batch_id": batch_id,
        "source_ids": identity["generation_contract"]["batches"][0]["source_ids"],
        "source_hashes": identity["generation_contract"]["batches"][0]["source_hashes"],
        "batch_prompt_sha256": "p" * 64,
        "terminal": True,
        "batch_validation_issues": [],
        "records": records,
        "records_sha256": runner.v2.sha256_bytes(runner._canonical_json_bytes(records)),
    }
    (parsed / "batch.json").write_text(json.dumps(payload), encoding="utf-8")
    (output / "run_manifest.json").write_text(json.dumps(identity), encoding="utf-8")
    loaded, integrity = audit.load_parsed_records(output, identity)
    assert loaded == []
    assert integrity["artifact_readable"] is False


def test_missing_expected_batch_blocks_exact_contract(tmp_path: Path):
    identity = {
        "generation_fingerprint": "f" * 64,
        "generation_contract": {"batches": [
            {"batch_id": "one", "source_ids": [], "source_hashes": [], "prompt_sha256": "a"},
            {"batch_id": "two", "source_ids": [], "source_hashes": [], "prompt_sha256": "b"},
        ]},
    }
    output = tmp_path / "out"
    output.mkdir()
    (output / "run_manifest.json").write_text(json.dumps(identity), encoding="utf-8")
    loaded, integrity = audit.load_parsed_records(output, identity)
    assert loaded == []
    assert integrity["expected_batch_count"] == 2
    assert integrity["completed_expected_batch_count"] == 0
    assert integrity["exact_expected_batch_set"] is False


def test_cli_writes_blocked_public_report_before_any_packet_for_empty_output(
    tmp_path: Path, monkeypatch
):
    rows, _ = _fixture(8)
    identity = {
        "generation_fingerprint": "f" * 64,
        "generation_contract": {"batches": [{"batch_id": "expected"}]},
    }
    empty_integrity = {
        "parsed_artifact_count": 0,
        "expected_batch_count": 1,
        "completed_expected_batch_count": 0,
        "unexpected_batch_artifact_count": 0,
        "duplicate_batch_artifact_count": 0,
        "terminal_artifact_count": 0,
        "records_hash_valid_count": 0,
        "generation_fingerprint_present": False,
        "current_generation_fingerprint_match_count": 0,
        "run_manifest_present": True,
        "run_manifest_matches_current_identity": True,
        "current_generation_contract_verified": True,
        "exact_expected_batch_set": False,
        "batch_validation_issue_count": 0,
        "artifact_readable": True,
        "all_terminal": False,
        "all_record_hashes_valid": False,
    }
    output_dir = tmp_path / "empty-private-output"
    monkeypatch.setattr(
        audit.runner,
        "load_config",
        lambda path, phase: SimpleNamespace(output_dir=output_dir),
    )
    monkeypatch.setattr(
        audit.runner, "validate_frozen_input", lambda config: (rows, {"sets": {}})
    )
    monkeypatch.setattr(
        audit.runner, "generation_identity", lambda config, public, source: identity
    )
    monkeypatch.setattr(
        audit, "load_parsed_records", lambda output, current: ([], dict(empty_integrity))
    )
    public_output = tmp_path / "blocked_report.json"
    assert audit.main([
        "--set", "smoke", "--public-output", str(public_output)
    ]) == 0
    report = json.loads(public_output.read_text())
    assert report["scope"]["observed_record_count"] == 0
    assert report["decision"]["mechanical_gate_pass"] is False
    assert report["decision"]["canary_authorized"] is False
    assert not (output_dir / "review" / "blind_review_packet.json").exists()


def test_cli_does_not_create_packet_for_complete_but_wrong_identity(
    tmp_path: Path, monkeypatch
):
    rows, records = _fixture(8)
    identity = {
        "generation_fingerprint": "f" * 64,
        "generation_contract": {"batches": [{"batch_id": "expected"}]},
    }
    stale_integrity = _integrity(1)
    stale_integrity["run_manifest_matches_current_identity"] = False
    output_dir = tmp_path / "stale-private-output"
    monkeypatch.setattr(
        audit.runner,
        "load_config",
        lambda path, phase: SimpleNamespace(output_dir=output_dir),
    )
    monkeypatch.setattr(
        audit.runner, "validate_frozen_input", lambda config: (rows, {"sets": {}})
    )
    monkeypatch.setattr(
        audit.runner, "generation_identity", lambda config, public, source: identity
    )
    monkeypatch.setattr(
        audit, "load_parsed_records", lambda output, current: (records, stale_integrity)
    )
    monkeypatch.setattr(
        audit,
        "build_blind_review_packet",
        lambda *args, **kwargs: pytest.fail("stale artifacts must not create a packet"),
    )
    public_output = tmp_path / "stale_report.json"
    assert audit.main([
        "--set", "smoke", "--public-output", str(public_output)
    ]) == 0
    report = json.loads(public_output.read_text())
    assert report["decision"]["mechanical_gate_pass"] is False
    assert "parsed_artifact_integrity" in report["decision"][
        "mechanical_blocker_categories"
    ]
