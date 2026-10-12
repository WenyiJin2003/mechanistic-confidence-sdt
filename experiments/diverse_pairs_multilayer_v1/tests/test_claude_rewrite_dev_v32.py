"""Focused tests for the final frozen v3.2 prompt-development protocol."""
from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import pytest

from experiments.diverse_pairs_multilayer_v1.src import (
    build_rewrite_dev_manifests_v32 as selector,
)
from experiments.diverse_pairs_multilayer_v1.src import (
    run_claude_rewrite_batches_v32 as runner,
)


class FakeTokenizer:
    def __call__(self, text, add_special_tokens=False):
        del add_special_tokens
        return {"input_ids": text.split()}

    def apply_chat_template(self, messages, tokenize=True):
        assert tokenize is True
        return list(range(3 + sum(len(item["content"].split()) for item in messages)))


def _fixture_row() -> dict:
    original = (
        "Water vapor cools in the atmosphere and forms droplets that combine "
        "until gravity pulls them down to the ground as rain."
    )
    row = {
        "source_id": "fixture-v32-source",
        "prompt": "How does rain form?",
        "original_response": original,
        "original_response_sha256": runner.v2.sha256_text(original),
        "dataset": "allenai/WildChat-1M",
        "task": "factual_explanation",
        "length_bin": "short",
        "rewrite_recipe": "A",
        "stance_topology": "distributed",
        "rewrite_output_order": "confident_first",
        "target_longer_member": "confident",
        "source_suitability_status": "primary_eligible",
        "source_word_count": runner._word_count(original),
        "source_editable_token_count": 20,
        "min_substantive_replacements_or_deletions": 3,
        "confident_target_words": runner._word_count(original) + 2,
        "hedged_target_words": runner._word_count(original) - 1,
        "desired_pair_word_gap_min": 1,
        "desired_pair_word_gap_max": 5,
        "dynamic_pair_word_gap_max": 5,
    }
    row["source_record_sha256"] = selector._source_record_hash(row)
    return row


def _local_config(tmp_path: Path) -> runner.RunnerConfig:
    return replace(
        runner.load_config(runner.DEFAULT_CONFIG.resolve(), "smoke"),
        input_path=tmp_path / "SOURCE_SMOKE_8.jsonl",
        public_manifest_path=tmp_path / "rewrite_dev_v32_freeze.json",
        output_dir=tmp_path / "private_data" / "claude_rewrite_dev_v32" / "smoke",
        config_path=tmp_path / "claude_rewrite_dev_v32.json",
        config_sha256="a" * 64,
    )


def _record(source_id: str, status: str = "accepted", **updates) -> dict:
    row = {
        "source_id": source_id,
        "status": status,
        "mechanical_issue_categories": [],
        "retry_eligible_mechanical_only": False,
    }
    row.update(updates)
    return row


def _frozen_context(tmp_path: Path, monkeypatch):
    cfg = replace(
        runner.load_config(runner.DEFAULT_CONFIG.resolve(), "smoke"),
        output_dir=tmp_path / "private_data" / "claude_rewrite_dev_v32" / "smoke",
    )
    rows, public = runner.validate_frozen_input(cfg)
    monkeypatch.setattr(runner.v2, "tokenizer_file_hashes", lambda: {"fixture": "1" * 64})
    monkeypatch.setattr(
        runner.v2,
        "claude_binary_identity",
        lambda *args: {"configured": "claude", "resolved": "/fixture/claude", "sha256": "2" * 64},
    )
    identity = runner.generation_identity(cfg, public, rows)
    batch = runner.make_batches(rows, "smoke", 8)[0]
    cfg.output_dir.mkdir(parents=True, exist_ok=True)
    runner.prepare_run_manifest(cfg.output_dir, identity)
    return cfg, rows, identity, batch


def _na_envelope(batch) -> str:
    pairs = []
    for row in batch.rows:
        labels = (
            ("confident", "hedged")
            if row["rewrite_output_order"] == "confident_first"
            else ("hedged", "confident")
        )
        pairs.append({
            "source_id": row["source_id"],
            "original_response_sha256": row["original_response_sha256"],
            "source_record_sha256": row["source_record_sha256"],
            "rewrite_recipe": row["rewrite_recipe"],
            "stance_topology": row["stance_topology"],
            "target_longer_member": row["target_longer_member"],
            "confident_target_words": row["confident_target_words"],
            "hedged_target_words": row["hedged_target_words"],
            "first_label": labels[0],
            "first_response": "",
            "second_label": labels[1],
            "second_response": "",
            "not_applicable": True,
            "issues": ["fixture terminal N/A"],
        })
    return json.dumps({
        "structured_output": {"pairs": pairs},
        "usage": {"output_tokens": 20},
        "modelUsage": {"claude-sonnet-4-6": {"outputTokens": 20}},
        "duration_ms": 1,
        "duration_api_ms": 1,
        "num_turns": 1,
        "is_error": False,
    })


def _write_valid_attempt0(tmp_path: Path, monkeypatch):
    cfg, rows, identity, batch = _frozen_context(tmp_path, monkeypatch)

    def fake_run(*args, **kwargs):
        del args, kwargs
        return SimpleNamespace(returncode=0, stdout=_na_envelope(batch), stderr="")

    payload = runner._execute_attempt(
        batch, cfg, identity, FakeTokenizer(), generation_attempt=0,
        run_subprocess=fake_run,
    )
    return cfg, rows, identity, batch, payload


def test_v32_freeze_is_deterministic_text_free_and_preserves_v3_v31_bytes():
    old_paths = [
        selector.BASE / "manifests/rewrite_dev_v3_freeze.json",
        selector.BASE / "manifests/rewrite_dev_v31_freeze.json",
        selector.BASE / "private_data/rewrite_dev_v3/SOURCE_SMOKE_8.jsonl",
        selector.BASE / "private_data/rewrite_dev_v3/SOURCE_CANARY_32.jsonl",
        selector.BASE / "private_data/rewrite_dev_v31/SOURCE_SMOKE_8.jsonl",
        selector.BASE / "private_data/rewrite_dev_v31/SOURCE_CANARY_CANDIDATE_POOL_45.jsonl",
    ]
    old_bytes = {path: path.read_bytes() for path in old_paths}
    public_path = selector.BASE / "manifests/rewrite_dev_v32_freeze.json"
    private_dir = selector.BASE / "private_data/rewrite_dev_v32"
    v32_paths = [
        public_path,
        private_dir / "SOURCE_SMOKE_8.jsonl",
        private_dir / "SOURCE_SMOKE_SELECTION_REVIEW.json",
        private_dir / "SOURCE_SUITABILITY_STATUS.json",
    ]
    v32_bytes = {path: path.read_bytes() for path in v32_paths}
    first = selector.build()
    second = selector.build()
    assert first == second
    assert {path: path.read_bytes() for path in v32_paths} == v32_bytes
    assert {path: path.read_bytes() for path in old_paths} == old_bytes
    assert first["contains_source_text"] is False
    serialized = json.dumps(first)
    assert '"prompt"' not in serialized and '"original_response"' not in serialized


def test_v32_smoke_is_fresh_reviewed_and_has_exact_prespecified_quotas():
    config = json.loads(selector.DEFAULT_CONFIG.read_text())
    rows = runner.v2.read_jsonl(
        selector.BASE / "private_data/rewrite_dev_v32/SOURCE_SMOKE_8.jsonl"
    )
    forbidden = [
        row
        for name in config["forbidden_source_inputs"]
        for row in runner.v2.read_jsonl(selector.resolve(name))
    ]
    forbidden_identity = selector._forbidden_identity(forbidden)
    for row in rows:
        assert row["source_suitability_status"] == "primary_eligible"
        assert row["source_only_semantic_review"] == "passed_by_agent_not_human_certified"
        assert selector.v31.source_suitability_reasons(row) == []
        for field, values in forbidden_identity.items():
            value = row.get(field)
            assert not value or value not in values
        assert selector._source_record_hash(row) == row["source_record_sha256"]
        assert abs(row["confident_target_words"] - row["hedged_target_words"]) == 3
        assert 0.9 <= row["confident_target_words"] / row["source_word_count"] <= 1.1
        assert 0.9 <= row["hedged_target_words"] / row["source_word_count"] <= 1.1
    assert Counter(row["dataset"] for row in rows) == {
        "allenai/WildChat-1M": 6, "nvidia/HelpSteer2": 2
    }
    assert Counter(row["task"] for row in rows) == {
        "factual_explanation": 4, "math_logic": 1, "programming": 1,
        "summary_judgment": 1, "comparison_analysis": 1,
    }
    assert Counter(row["length_bin"] for row in rows) == {
        "short": 2, "medium": 3, "long": 3
    }
    assert Counter(row["target_longer_member"] for row in rows) == {
        "confident": 4, "hedged": 4
    }
    assert Counter(row["rewrite_recipe"] for row in rows) == {"A": 4, "B": 4}
    assert Counter(row["stance_topology"] for row in rows) == {
        "early": 2, "middle": 2, "late": 2, "distributed": 2
    }


def test_prompt_freezes_exact_targets_substantive_edits_and_all_v31_protections():
    row = _fixture_row()
    batch = runner.RewriteBatch("smoke", 1, "fixture", (row,))
    prompt = runner.build_prompt(batch)
    for phrase in (
        "one-for-one",
        "Do not add examples, generalizations",
        "Do not delete a proposition",
        "do not pad either response",
        "substantive source-token replacements or deletions",
        "max(3, 10% of editable source tokens)",
        "one maximal run of non-whitespace characters",
        "counting uses the returned text exactly without normalization",
        "hedged_target_words_exact",
        "target_longer_member",
        "desired 1-5 word bounds",
        "substitution and grammatical calibration",
        "never append a caveat",
        "primary and only intended confidence-contrast region",
        "exactly two or three separated substantive regions",
        "byte-for-byte",
        "Do not repeat distinctive new wording",
    ):
        assert phrase in prompt
    payload = json.loads(prompt.split("INPUT_RECORDS_JSON\n", 1)[1])[0]
    assert payload["original_word_count"] == row["source_word_count"]
    assert payload["confident_target_words_exact"] == row["confident_target_words"]
    assert payload["hedged_target_words_exact"] == row["hedged_target_words"]
    assert payload["minimum_substantive_replacements_or_deletions_per_arm"] == 3


def test_retry_prompt_gets_categories_only_and_never_prior_generated_text():
    row = _fixture_row()
    batch = runner.RewriteBatch("smoke", 1, "retry-fixture", (row,))
    marker = "THIS PRIOR FAILED OUTPUT MUST NEVER APPEAR"
    prompt = runner.build_prompt(
        batch,
        generation_attempt=1,
        retry_issue_categories={row["source_id"]: ["word_target", "structure"]},
    )
    assert "one prespecified full-pair mechanical retry" in prompt
    assert "No earlier generated wording is supplied" in prompt
    assert '"retry_issue_categories": ["word_target", "structure"]' in prompt
    assert marker not in prompt
    with pytest.raises(ValueError, match="unknown categories"):
        runner.build_prompt(
            batch,
            generation_attempt=1,
            retry_issue_categories={row["source_id"]: ["semantic_failure"]},
        )
    with pytest.raises(ValueError, match="Attempt 0"):
        runner.build_prompt(
            batch,
            generation_attempt=0,
            retry_issue_categories={row["source_id"]: ["word_target"]},
        )


def test_member_and_pair_contracts_enforce_exact_counts_edits_direction_and_gap(tmp_path):
    row = _fixture_row()
    cfg = _local_config(tmp_path)
    too_close = row["original_response"] + " clearly today"
    issues, stats = runner.member_issues(row, too_close, "confident", cfg, FakeTokenizer())
    assert "insufficient_replacements_or_deletions" in issues
    assert stats["exact_word_target_met"] is True

    member_stats = {
        "confident": {"token_stats": {"response_tokens": 22}, "paragraph_blocks": 1},
        "hedged": {"token_stats": {"response_tokens": 19}, "paragraph_blocks": 1},
    }
    confident = "one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty twentyone twentytwo"
    hedged = "one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen"
    issues, stats = runner._pair_issues(row, confident, hedged, cfg, member_stats)
    assert "target_length_direction_mismatch" not in issues
    assert stats["observed_longer_member"] == "confident"
    reversed_row = dict(row, target_longer_member="hedged")
    issues, _ = runner._pair_issues(reversed_row, confident, hedged, cfg, member_stats)
    assert "target_length_direction_mismatch" in issues


def test_retry_policy_is_exactly_one_mechanical_failure_after_seven_passes():
    accepted = [_record(f"s{i}") for i in range(7)]
    mechanical = _record(
        "s7", "validation_failed",
        mechanical_issue_categories=["word_target"],
        retry_eligible_mechanical_only=True,
    )
    plan = runner.attempt0_retry_plan(accepted + [mechanical])
    assert plan["retry_authorized"] is True
    assert plan["retry_source_id"] == "s7"
    assert plan["retry_issue_categories_by_source"] == {"s7": ["word_target"]}

    six_pass = accepted[:6] + [mechanical, _record("s8", "validation_failed")]
    assert runner.attempt0_retry_plan(six_pass)["retry_authorized"] is False
    na = accepted + [_record("s7", "not_applicable")]
    assert runner.attempt0_retry_plan(na)["retry_authorized"] is False
    semantic = accepted + [_record(
        "s7", "needs_review", mechanical_issue_categories=[],
        retry_eligible_mechanical_only=False,
    )]
    assert runner.attempt0_retry_plan(semantic)["retry_authorized"] is False


def test_retry_fingerprint_is_separate_and_canonical_selection_is_earliest_passing(
    monkeypatch,
):
    cfg = runner.load_config(runner.DEFAULT_CONFIG.resolve(), "smoke")
    rows, public = runner.validate_frozen_input(cfg)
    monkeypatch.setattr(
        runner.v2, "tokenizer_file_hashes",
        lambda: {"tokenizer.json": "1" * 64, "tokenizer_config.json": "2" * 64},
    )
    monkeypatch.setattr(
        runner.v2, "claude_binary_identity",
        lambda *args: {"configured": "claude", "resolved": "/fixture/claude", "sha256": "3" * 64},
    )
    identity = runner.generation_identity(cfg, public, rows)
    batch = runner.make_batches(rows, "smoke", 8)[0]
    attempt0 = [_record(row["source_id"]) for row in rows[:7]] + [_record(
        rows[7]["source_id"], "validation_failed",
        mechanical_issue_categories=["word_target"],
        retry_eligible_mechanical_only=True,
    )]
    plan = runner.attempt0_retry_plan(attempt0)
    retry_batch = runner.make_retry_batch(batch, plan)
    first = runner.retry_attempt_identity(identity, retry_batch, plan)
    second = runner.retry_attempt_identity(identity, retry_batch, plan)
    assert first == second
    assert first["attempt_fingerprint"] != identity["generation_fingerprint"]
    assert first["attempt_contract"]["generation_attempt"] == 1
    retry = [_record(rows[7]["source_id"])]
    canonical = runner.select_canonical_records(attempt0, retry)
    assert canonical["attempt0_accepted"] == 7
    assert canonical["final_accepted"] == 8
    assert canonical["stop_go_passed"] is True
    assert [row["canonical_generation_attempt"] for row in canonical["records"]] == [0] * 7 + [1]


def test_generation_identity_binds_4_4_directions_record_hashes_and_retry_rules(
    monkeypatch,
):
    cfg = runner.load_config(runner.DEFAULT_CONFIG.resolve(), "smoke")
    rows, public = runner.validate_frozen_input(cfg)
    monkeypatch.setattr(runner.v2, "tokenizer_file_hashes", lambda: {"fixture": "1" * 64})
    monkeypatch.setattr(
        runner.v2, "claude_binary_identity", lambda *args: {"configured": "claude"}
    )
    identity = runner.generation_identity(cfg, public, rows)
    contract = identity["generation_contract"]
    batch = contract["batches"][0]
    assert Counter(batch["target_longer_members"]) == {"confident": 4, "hedged": 4}
    assert batch["source_record_hashes"] == [row["source_record_sha256"] for row in rows]
    assert batch["attempt_fingerprint"].startswith("0") is False or len(batch["attempt_fingerprint"]) == 64
    assert contract["retry_contract"]["semantic_or_NA_retry"] is False
    assert contract["retry_contract"]["canonical_selection"] == "earliest_passing_attempt"
    assert identity["generation_fingerprint"] == runner.v2.sha256_text(
        "v32:" + identity["generation_contract_sha256"]
    )
    runtime_hashes = contract["runtime_module_sha256"]
    assert set(runtime_hashes) == {
        "run_claude_rewrite_batches_v32",
        "build_rewrite_dev_manifests_v32",
        "run_claude_rewrite_batches_v31",
        "build_rewrite_dev_manifests_v31",
        "run_claude_rewrite_batches_v3",
        "build_rewrite_dev_manifests_v3",
        "run_claude_rewrite_batches",
    }
    assert all(len(value) == 64 for value in runtime_hashes.values())


def test_no_legacy_namespace_or_legacy_manifest_is_accepted(tmp_path):
    raw = json.loads(runner.DEFAULT_CONFIG.read_text())
    raw["output_root"] = "private_data/claude_rewrite_dev_v31"
    bad = tmp_path / "bad-v32.json"
    bad.write_text(json.dumps(raw), encoding="utf-8")
    with pytest.raises(ValueError, match="legacy output namespace"):
        runner.load_config(bad, "smoke")

    output = tmp_path / "private_data/claude_rewrite_dev_v32/smoke"
    output.mkdir(parents=True)
    (output / "run_manifest.json").write_text(
        json.dumps({"generation_fingerprint": "v31-legacy"}), encoding="utf-8"
    )
    with pytest.raises(ValueError, match="different contract"):
        runner.verify_resume_artifacts(output, {"generation_fingerprint": "v32-new"})

    (output / "run_manifest.json").write_text(
        json.dumps({"generation_fingerprint": "v32-new"}), encoding="utf-8"
    )
    (output / "raw").mkdir()
    with pytest.raises(ValueError, match="Legacy flat output layout"):
        runner.verify_resume_artifacts(output, {"generation_fingerprint": "v32-new"})


def test_output_schema_requires_frozen_record_and_length_assignment_echoes():
    batch = runner.RewriteBatch("smoke", 1, "fixture", (_fixture_row(),))
    item = runner.output_schema(batch)["properties"]["pairs"]["items"]
    for field in (
        "source_record_sha256", "target_longer_member",
        "confident_target_words", "hedged_target_words",
    ):
        assert field in item["required"]
        assert field in item["properties"]


def test_public_v32_code_config_and_freeze_do_not_reidentify_reviewed_sources():
    private_review = json.loads((
        selector.BASE / "private_data/rewrite_dev_v32/SOURCE_SMOKE_SELECTION_REVIEW.json"
    ).read_text())
    public_paths = (
        Path(selector.__file__),
        selector.DEFAULT_CONFIG,
        selector.BASE / "manifests/rewrite_dev_v32_freeze.json",
    )
    public_text = "\n".join(path.read_text(encoding="utf-8") for path in public_paths)
    for record in private_review["records"]:
        assert record["source_id"] not in public_text
        assert record["review_notes"] not in public_text
    assert "SMOKE_SOURCE_IDS" not in Path(selector.__file__).read_text(encoding="utf-8")
    assert "SOURCE_REVIEW =" not in Path(selector.__file__).read_text(encoding="utf-8")


def test_private_review_provenance_is_hash_bound_and_fail_closed(tmp_path):
    config = json.loads(selector.DEFAULT_CONFIG.read_text(encoding="utf-8"))
    original = json.loads(selector.resolve(config["private_selection_review_path"]).read_text())
    original["records"][0]["checklist"]["not_roleplay_or_fiction"] = False
    tampered = tmp_path / "SOURCE_SMOKE_SELECTION_REVIEW.json"
    tampered.write_text(json.dumps(original), encoding="utf-8")
    config["private_selection_review_path"] = str(tampered)
    config["private_selection_review_sha256"] = selector._sha256_file(tampered)
    with pytest.raises(ValueError, match="unmet suitability check"):
        selector._load_completed_review(config)

    original["records"][0]["checklist"]["not_roleplay_or_fiction"] = True
    original["reviewer_type"] = "builder"
    tampered.write_text(json.dumps(original), encoding="utf-8")
    config["private_selection_review_sha256"] = selector._sha256_file(tampered)
    with pytest.raises(ValueError, match="reviewer_type"):
        selector._load_completed_review(config)


def test_direct_file_invocation_is_supported_without_execution():
    result = subprocess.run(
        [sys.executable, str(Path(runner.__file__)), "--help"],
        text=True,
        capture_output=True,
        check=False,
        cwd=runner.BASE,
    )
    assert result.returncode == 0, result.stderr
    assert "--execute" in result.stdout


def test_execute_attempt_replays_valid_cache_without_another_model_call(
    tmp_path, monkeypatch,
):
    cfg, rows, identity, batch, payload = _write_valid_attempt0(tmp_path, monkeypatch)
    runner.verify_resume_artifacts(
        cfg.output_dir, identity, config=cfg, rows=rows, tokenizer=FakeTokenizer()
    )

    def must_not_run(*args, **kwargs):
        raise AssertionError("cache resume attempted another model call")

    resumed = runner._execute_attempt(
        batch, cfg, identity, FakeTokenizer(), generation_attempt=0,
        run_subprocess=must_not_run,
    )
    assert resumed == payload


def test_resume_rejects_tampered_raw_stdout_even_if_parsed_is_present(
    tmp_path, monkeypatch,
):
    cfg, rows, identity, batch, _ = _write_valid_attempt0(tmp_path, monkeypatch)
    raw_path = next((cfg.output_dir / "attempt_0/raw").glob("*.json"))
    raw = json.loads(raw_path.read_text())
    raw["stdout"] += " "
    raw_path.write_text(json.dumps(raw), encoding="utf-8")
    with pytest.raises(ValueError, match="stdout hash mismatch"):
        runner.verify_resume_artifacts(
            cfg.output_dir, identity, config=cfg, rows=rows, tokenizer=FakeTokenizer()
        )


def test_resume_rejects_rehashed_parsed_record_that_differs_from_raw_replay(
    tmp_path, monkeypatch,
):
    cfg, rows, identity, batch, _ = _write_valid_attempt0(tmp_path, monkeypatch)
    parsed_path = cfg.output_dir / "attempt_0/parsed" / f"{batch.batch_id}.json"
    parsed = json.loads(parsed_path.read_text())
    parsed["records"][0]["status"] = "accepted"
    parsed["records_sha256"] = runner.v2.sha256_bytes(
        runner._canonical_json_bytes(parsed["records"])
    )
    parsed_path.write_text(json.dumps(parsed), encoding="utf-8")
    with pytest.raises(ValueError, match="differs from raw-output replay"):
        runner.verify_resume_artifacts(
            cfg.output_dir, identity, config=cfg, rows=rows, tokenizer=FakeTokenizer()
        )


def test_resume_recursively_verifies_canonical_and_status_artifacts(
    tmp_path, monkeypatch,
):
    cfg, rows, identity, batch, attempt0 = _write_valid_attempt0(tmp_path, monkeypatch)
    retry_plan = runner.attempt0_retry_plan(attempt0["records"])
    canonical = runner.select_canonical_records(attempt0["records"])
    canonical.update({
        "terminal": True,
        "generation_fingerprint": identity["generation_fingerprint"],
        "generation_contract_sha256": identity["generation_contract_sha256"],
        "attempt_0_parsed_artifact": f"attempt_0/parsed/{batch.batch_id}.json",
        "attempt_0_parsed_artifact_sha256": runner.v2.sha256_file(
            cfg.output_dir / "attempt_0/parsed" / f"{batch.batch_id}.json"
        ),
        "retry_plan": retry_plan,
        "retry_attempt_identity": None,
        "retry_parsed_artifact": None,
        "retry_parsed_artifact_sha256": None,
        "auth": {
            "loggedIn": True,
            "authMethod": "claude.ai",
            "apiProvider": "firstParty",
            "subscriptionType": "fixture",
        },
    })
    canonical_path = cfg.output_dir / "canonical/selected.json"
    runner._immutable_json(canonical_path, canonical)
    status = {key: value for key, value in canonical.items() if key != "records"}
    status["canonical_artifact_sha256"] = runner.v2.sha256_file(canonical_path)
    runner._immutable_json(cfg.output_dir / "status.json", status)
    runner.verify_resume_artifacts(
        cfg.output_dir, identity, config=cfg, rows=rows, tokenizer=FakeTokenizer()
    )

    canonical["output_blocked"] = False
    canonical_path.write_text(json.dumps(canonical), encoding="utf-8")
    with pytest.raises(ValueError, match="canonical v3.2 mismatch"):
        runner.verify_resume_artifacts(
            cfg.output_dir, identity, config=cfg, rows=rows, tokenizer=FakeTokenizer()
        )


def test_resume_recursively_verifies_retry_manifest_and_retry_raw_binding(
    tmp_path, monkeypatch,
):
    cfg, rows, identity, batch = _frozen_context(tmp_path, monkeypatch)

    def fake_validate(active_batch, structured, config, tokenizer):
        del structured, config, tokenizer
        records = []
        for index, source in enumerate(active_batch.rows):
            failed = len(active_batch.rows) == 8 and index == 7
            records.append({
                "source_id": source["source_id"],
                "original_response_sha256": source["original_response_sha256"],
                "source_record_sha256": source["source_record_sha256"],
                "source_suitability_status": source["source_suitability_status"],
                "target_longer_member": source["target_longer_member"],
                "confident_target_words": source["confident_target_words"],
                "hedged_target_words": source["hedged_target_words"],
                "confident_response": "fixture confident",
                "hedged_response": "fixture hedged",
                "status": "validation_failed" if failed else "accepted",
                "validation_issues": ["exact_word_target_mismatch"] if failed else [],
                "mechanical_issue_categories": ["word_target"] if failed else [],
                "retry_eligible_mechanical_only": failed,
            })
        return records, []

    monkeypatch.setattr(runner, "validate_structured_output", fake_validate)

    def fake_run(active_batch):
        def run(*args, **kwargs):
            del args, kwargs
            return SimpleNamespace(
                returncode=0, stdout=_na_envelope(active_batch), stderr=""
            )
        return run

    attempt0 = runner._execute_attempt(
        batch, cfg, identity, FakeTokenizer(), generation_attempt=0,
        run_subprocess=fake_run(batch),
    )
    plan = runner.attempt0_retry_plan(attempt0["records"])
    assert plan["retry_authorized"] is True
    retry_batch = runner.make_retry_batch(batch, plan)
    retry_identity = runner.retry_attempt_identity(identity, retry_batch, plan)
    runner._immutable_json(
        cfg.output_dir / "retry_1/retry_manifest.json", retry_identity
    )
    runner._execute_attempt(
        retry_batch, cfg, identity, FakeTokenizer(), generation_attempt=1,
        retry_identity=retry_identity,
        retry_issue_categories=plan["retry_issue_categories_by_source"],
        run_subprocess=fake_run(retry_batch),
    )
    runner.verify_resume_artifacts(
        cfg.output_dir, identity, config=cfg, rows=rows, tokenizer=FakeTokenizer()
    )

    raw_path = next((cfg.output_dir / "retry_1/raw").glob("*.json"))
    raw = json.loads(raw_path.read_text())
    raw["source_hashes"] = ["0" * 64]
    raw_path.write_text(json.dumps(raw), encoding="utf-8")
    with pytest.raises(ValueError, match="binding mismatch for source_hashes"):
        runner.verify_resume_artifacts(
            cfg.output_dir, identity, config=cfg, rows=rows, tokenizer=FakeTokenizer()
        )


def test_execute_attempt_rejects_fake_parsed_artifact_without_raw_parent(
    tmp_path, monkeypatch,
):
    cfg, rows, identity, batch = _frozen_context(tmp_path, monkeypatch)
    expected = runner._attempt_binding(identity, batch, 0)
    fake = {
        **expected,
        "terminal": True,
        "records": [],
        "records_sha256": runner.v2.sha256_bytes(runner._canonical_json_bytes([])),
    }
    parsed_path = cfg.output_dir / "attempt_0/parsed" / f"{batch.batch_id}.json"
    parsed_path.parent.mkdir(parents=True)
    parsed_path.write_text(json.dumps(fake), encoding="utf-8")

    def must_not_run(*args, **kwargs):
        raise AssertionError("invalid cache attempted a model call")

    with pytest.raises(ValueError, match="record count mismatch"):
        runner._execute_attempt(
            batch, cfg, identity, FakeTokenizer(), generation_attempt=0,
            run_subprocess=must_not_run,
        )


def test_prepare_manifest_archives_only_manifest_only_dry_runs(tmp_path):
    output = tmp_path / "private_data/claude_rewrite_dev_v32/smoke"
    output.mkdir(parents=True)
    old = {"generation_fingerprint": "old-dry-run"}
    runner._immutable_json(output / "run_manifest.json", old)
    current = {"generation_fingerprint": "new-dry-run"}
    runner.prepare_run_manifest(output, current)
    assert json.loads((output / "run_manifest.json").read_text()) == current
    archives = list((output / "superseded_dry_run_manifests").glob("*.json"))
    assert len(archives) == 1
    assert json.loads(archives[0].read_text()) == old

    (output / "attempt_0").mkdir()
    with pytest.raises(ValueError, match="different contract"):
        runner.prepare_run_manifest(output, {"generation_fingerprint": "third"})
