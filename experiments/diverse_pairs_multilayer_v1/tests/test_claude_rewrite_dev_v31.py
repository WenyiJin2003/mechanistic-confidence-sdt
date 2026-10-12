"""Focused tests for the fail-closed v3.1 rewrite protocol."""
from __future__ import annotations

import json
from collections import Counter
from dataclasses import replace
from pathlib import Path

import pytest

from experiments.diverse_pairs_multilayer_v1.src import (
    build_rewrite_dev_manifests_v31 as selector,
)
from experiments.diverse_pairs_multilayer_v1.src import (
    run_claude_rewrite_batches_v31 as runner,
)


class FakeTokenizer:
    def __call__(self, text, add_special_tokens=False):
        del add_special_tokens
        return {"input_ids": text.split()}

    def apply_chat_template(self, messages, tokenize=True):
        assert tokenize is True
        return list(range(3 + sum(len(item["content"].split()) for item in messages)))


def source_row(original: str | None = None) -> dict:
    original = original or (
        "Water vapor cools and condenses into droplets in the atmosphere. "
        "The droplets combine until gravity pulls them toward the ground."
    )
    return {
        "source_id": "fixture-source",
        "prompt": "How does rain form?",
        "original_response": original,
        "original_response_sha256": runner.v2.sha256_text(original),
        "pool_partition": "reserve",
        "split": "train",
        "dataset": selector.v3.WILDCHAT,
        "task": "factual_explanation",
        "length_bin": "medium",
        "rewrite_recipe": "A",
        "stance_topology": "early",
        "rewrite_output_order": "confident_first",
        "rewrite_dev_protocol": "symmetric-diverse-v31",
        "rewrite_dev_set": "smoke",
        "source_suitability_status": "primary_eligible",
    }


def local_config(tmp_path: Path) -> runner.RunnerConfig:
    return replace(
        runner.load_config(runner.DEFAULT_CONFIG.resolve(), "smoke"),
        input_path=tmp_path / "input.jsonl",
        public_manifest_path=tmp_path / "freeze.json",
        source_pool_manifest_path=tmp_path / "source-pool.json",
        main_input_path=tmp_path / "main.jsonl",
        legacy_v3_public_manifest_path=tmp_path / "legacy.json",
        legacy_v3_private_manifest_dir=tmp_path / "legacy-private",
        output_dir=tmp_path / "private_data" / "claude_rewrite_dev_v31" / "smoke",
        config_path=tmp_path / "config.json",
        config_sha256="a" * 64,
        expected_sources=1,
        batch_size=1,
        timeout_seconds=30,
    )


def test_freeze_is_deterministic_text_free_and_disjoint_from_every_prior_set():
    legacy_public_path = selector.BASE / "manifests/rewrite_dev_v3_freeze.json"
    legacy_public_before = legacy_public_path.read_bytes()
    legacy_public = json.loads(legacy_public_before)
    legacy_dir = selector.BASE / "private_data/rewrite_dev_v3"
    legacy_files_before = {
        name: (legacy_dir / legacy_public["sets"][name]["file_name"]).read_bytes()
        for name in ("smoke", "canary")
    }
    public_path = selector.BASE / "manifests/rewrite_dev_v31_freeze.json"
    private_dir = selector.BASE / "private_data/rewrite_dev_v31"
    frozen_before = {
        path: path.read_bytes()
        for path in (
            public_path,
            private_dir / "SOURCE_SMOKE_8.jsonl",
            private_dir / "SOURCE_CANARY_CANDIDATE_POOL_45.jsonl",
            private_dir / "SOURCE_SUITABILITY_AUDIT.jsonl",
            private_dir / "SOURCE_CANARY_SOURCE_REVIEW.jsonl",
        )
    }
    first = selector.build()
    second = selector.build()
    assert first == second
    assert {path: path.read_bytes() for path in frozen_before} == frozen_before
    assert legacy_public_path.read_bytes() == legacy_public_before
    assert {
        name: (legacy_dir / legacy_public["sets"][name]["file_name"]).read_bytes()
        for name in ("smoke", "canary")
    } == legacy_files_before

    smoke = selector.v3.read_jsonl(private_dir / "SOURCE_SMOKE_8.jsonl")
    candidates = selector.v3.read_jsonl(
        private_dir / "SOURCE_CANARY_CANDIDATE_POOL_45.jsonl"
    )
    main = selector.v3.read_jsonl(
        selector.BASE / "private_data/source_pool_1000_v1/SOURCE_MANIFEST_MAIN_1000.jsonl"
    )
    prior = [
        row
        for name in ("smoke", "canary")
        for row in selector.v3.read_jsonl(
            legacy_dir / legacy_public["sets"][name]["file_name"]
        )
    ]
    smoke_ids = {row["source_id"] for row in smoke}
    candidate_ids = {row["source_id"] for row in candidates}
    forbidden_ids = {row["source_id"] for row in main + prior}
    assert len(smoke) == 8 and len(candidates) == 45
    assert not smoke_ids & candidate_ids
    assert not (smoke_ids | candidate_ids) & forbidden_ids
    assert all(row["source_suitability_status"] == "primary_eligible" for row in smoke)
    assert all(
        row["source_suitability_status"]
        == "candidate_pending_source_only_semantic_review"
        for row in candidates
    )
    public = json.loads(public_path.read_text())
    assert public["contains_source_text"] is False
    assert public["candidate_pool"]["count"] == 45
    assert public["candidate_pool"]["status"] == (
        "candidate_pending_source_only_semantic_review"
    )
    serialized = json.dumps(public)
    assert '"prompt"' not in serialized and '"original_response"' not in serialized


def test_smoke_has_exact_coverage_and_new_source_suitability_exclusions():
    smoke = selector.v3.read_jsonl(
        selector.BASE / "private_data/rewrite_dev_v31/SOURCE_SMOKE_8.jsonl"
    )
    assert Counter(row["dataset"] for row in smoke) == {
        selector.v3.WILDCHAT: 6,
        selector.v3.HELPSTEER: 2,
    }
    assert Counter(row["task"] for row in smoke) == {
        "factual_explanation": 4,
        "math_logic": 1,
        "programming": 1,
        "comparison_analysis": 1,
        "summary_judgment": 1,
    }
    assert Counter(row["length_bin"] for row in smoke) == {
        "short": 2,
        "medium": 3,
        "long": 3,
    }
    assert Counter(row["rewrite_recipe"] for row in smoke) == {"A": 4, "B": 4}
    assert Counter(row["stance_topology"] for row in smoke) == {
        "early": 2,
        "middle": 2,
        "late": 2,
        "distributed": 2,
    }
    examples = (
        ("Act as a fictional hero and continue this roleplay story.", "Once upon a time...", "creative_or_roleplay"),
        ("Write an email to my manager.", "Dear Manager, best regards.", "politeness_or_correspondence"),
        ("Create an inspirational slogan for this advertisement.", "Dream bigger today.", "slogan_motivational_or_promotional"),
        ("Can you analyze a conversation if I provide it?", "Yes, I can help analyze it.", "meta_or_non_object_level_transformation"),
    )
    for prompt, response, expected in examples:
        reasons = selector.source_suitability_reasons({
            "prompt": prompt,
            "original_response": response,
        })
        assert expected in reasons


def test_prompt_has_v31_lengths_occurrences_topology_and_no_appended_caveat_contract():
    row = source_row("The archive stores code 4712. Staff use code 4712 after maintenance.")
    batch = runner.RewriteBatch("smoke", 1, "fixture", (row,))
    prompt = runner.build_prompt(batch)
    assert "90%-110%" in prompt
    assert "max(5 words, 8% of source words)" in prompt
    assert "substitution and grammatical calibration" in prompt
    assert "never append a caveat" in prompt
    assert "every non-stance proposition" in prompt
    assert "one-for-one" in prompt
    assert "Do not add examples, generalizations" in prompt
    assert "primary and only intended contrast region" in prompt
    assert "exactly two or three separated" in prompt
    assert "Do not repeat distinctive new wording" in prompt
    records = json.loads(prompt.split("INPUT_RECORDS_JSON\n", 1)[1])
    record = records[0]
    assert record["original_word_count"] == runner._word_count(row["original_response"])
    assert record["target_word_count_min"] == pytest.approx(
        __import__("math").ceil(0.9 * record["original_word_count"])
    )
    protected = record["protected_spans_with_occurrence_counts"]
    assert any(item["required_occurrences"] == 2 for item in protected)


def test_paragraph_difference_is_diagnostic_but_list_and_protected_occurrences_are_hard(
    tmp_path,
):
    original = (
        "Rain forms when water vapor cools and condenses in the atmosphere. "
        "Droplets combine until gravity draws them toward the ground.\n\n"
        "Cloud temperature and humidity influence how quickly this process develops."
    )
    row = source_row(original)
    rewritten = (
        "Water vapor cools in the atmosphere and condenses into droplets. Those "
        "droplets merge until gravity pulls them groundward, while cloud temperature "
        "and humidity affect how quickly the process develops."
    )
    issues, stats = runner.member_issues(row, rewritten, local_config(tmp_path), FakeTokenizer())
    assert "hard_structure_changed" not in issues
    assert stats["paragraph_block_difference_from_source"] == -1

    listed = "Steps:\n\n- Keep code `4712`.\n- Retry code `4712`."
    listed_row = source_row(listed)
    changed = "Steps:\n\nKeep code `4712` and retry it."
    issues, _ = runner.member_issues(
        listed_row, changed, local_config(tmp_path), FakeTokenizer()
    )
    assert "hard_structure_changed" in issues
    assert "protected_code_changed" in issues or "protected_span_occurrence_changed" in issues


def test_canary_fails_closed_and_old_output_or_namespace_cannot_resume(tmp_path):
    with pytest.raises(ValueError, match="candidate_pending_source_only_semantic_review"):
        runner.load_config(runner.DEFAULT_CONFIG.resolve(), "canary")

    cfg = local_config(tmp_path)
    cfg.output_dir.mkdir(parents=True)
    identity = {
        "generation_fingerprint": "v31-fingerprint",
        "generation_contract_sha256": "c" * 64,
        "generation_contract": {
            "batches": [{
                "batch_id": "v31_smoke__batch_01__fixture",
                "source_ids": ["fixture-source"],
                "source_hashes": ["a" * 64],
                "source_suitability_statuses": ["primary_eligible"],
                "prompt_sha256": "b" * 64,
            }]
        },
    }
    (cfg.output_dir / "run_manifest.json").write_text(
        json.dumps({**identity, "generation_fingerprint": "old-v3-fingerprint"}),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="different contract"):
        runner.verify_resume_artifacts(cfg.output_dir, identity)

    raw = json.loads(runner.DEFAULT_CONFIG.read_text())
    raw["output_root"] = "private_data/claude_rewrite_dev_v3"
    bad_config = tmp_path / "bad-config.json"
    bad_config.write_text(json.dumps(raw), encoding="utf-8")
    with pytest.raises(ValueError, match="v1/v2/v3 output namespace"):
        runner.load_config(bad_config, "smoke")


def test_generation_identity_binds_prompt_contract_status_and_new_fingerprint(
    monkeypatch,
):
    cfg = runner.load_config(runner.DEFAULT_CONFIG.resolve(), "smoke")
    rows, public = runner.validate_frozen_input(cfg)
    monkeypatch.setattr(
        runner.v2,
        "tokenizer_file_hashes",
        lambda: {"tokenizer.json": "1" * 64, "tokenizer_config.json": "2" * 64},
    )
    monkeypatch.setattr(
        runner.v2,
        "claude_binary_identity",
        lambda *args: {
            "configured": "claude",
            "resolved": "/fixture/claude",
            "file_sha256": "3" * 64,
        },
    )
    identity = runner.generation_identity(cfg, public, rows)
    contract = identity["generation_contract"]
    assert len(contract["prompt_contract_sha256"]) == 64
    assert len(contract["validation_contract_sha256"]) == 64
    assert len(contract["output_schema_contract_sha256"]) == 64
    assert identity["generation_contract_sha256"] != identity["generation_fingerprint"]
    assert contract["batches"][0]["source_suitability_statuses"] == [
        "primary_eligible"
    ] * 8
    assert contract["canary_generation_authorized"] is False
    assert contract["candidate_pool_count"] == 45


def test_dry_run_is_one_smoke_batch_and_never_authenticates(monkeypatch, capsys, tmp_path):
    real_load = runner.load_config

    def isolated(path, phase):
        return replace(
            real_load(path, phase),
            output_dir=tmp_path / "private_data" / "claude_rewrite_dev_v31" / "smoke",
        )

    def forbidden(*args, **kwargs):
        raise AssertionError("dry run must not authenticate or call Claude")

    monkeypatch.setattr(runner, "load_config", isolated)
    monkeypatch.setattr(runner.v2, "verify_subscription_auth", forbidden)
    assert runner.main(["--set", "smoke"]) == 0
    plan = json.loads(capsys.readouterr().out.splitlines()[-1])
    assert plan["execute"] is False
    assert plan["source_count"] == 8
    assert plan["batch_count"] == 1
    assert plan["candidate_pool_count"] == 45
    assert plan["canary_generation_authorized"] is False
