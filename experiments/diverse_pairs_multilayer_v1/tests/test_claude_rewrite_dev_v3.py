"""Focused tests for the isolated v3 symmetric-diverse rewrite protocol."""
from __future__ import annotations

import hashlib
import json
import subprocess
from collections import Counter
from dataclasses import replace
from pathlib import Path

import pytest

from experiments.diverse_pairs_multilayer_v1.src import (
    build_rewrite_dev_manifests_v3 as selector,
)
from experiments.diverse_pairs_multilayer_v1.src import (
    run_claude_rewrite_batches_v3 as runner,
)


class FakeTokenizer:
    def __call__(self, text, add_special_tokens=False):
        del add_special_tokens
        return {"input_ids": text.split()}

    def apply_chat_template(self, messages, tokenize=True):
        assert tokenize is True
        return list(range(3 + sum(len(item["content"].split()) for item in messages)))


def source_row(
    index: int = 0,
    *,
    recipe: str = "A",
    topology: str = "early",
    order: str = "confident_first",
) -> dict:
    original = (
        "The archive stores code 4712 for the eastern terminal, and staff use it "
        "after the nightly maintenance window closes."
    )
    return {
        "source_id": f"source-{index:03d}",
        "prompt": "Which code do staff use at the eastern terminal?",
        "original_response": original,
        "original_response_sha256": runner.v2.sha256_text(original),
        "pool_partition": "reserve",
        "split": "train",
        "dataset": selector.WILDCHAT,
        "task": "factual_explanation",
        "length_bin": "medium",
        "rewrite_family": recipe,
        "rewrite_recipe": recipe,
        "stance_topology": topology,
        "rewrite_output_order": order,
        "rewrite_dev_set": "smoke",
    }


def valid_responses() -> tuple[str, str]:
    confident = (
        "Staff use code 4712 for the eastern terminal after the nightly maintenance "
        "window closes; the archive lists that exact value."
    )
    hedged = (
        "The archive appears to list code 4712 for the eastern terminal, which staff "
        "likely use once the nightly maintenance window closes."
    )
    return confident, hedged


def config(tmp_path: Path, *, expected_sources: int = 1) -> runner.RunnerConfig:
    return runner.RunnerConfig(
        protocol_version="claude-symmetric-diverse-rewrite-v3",
        phase="smoke",
        input_path=tmp_path / "input.jsonl",
        public_manifest_path=tmp_path / "freeze.json",
        source_pool_manifest_path=tmp_path / "source_pool_freeze.json",
        main_input_path=tmp_path / "main.jsonl",
        output_dir=tmp_path / "private_data" / "claude_rewrite_dev_v3" / "smoke",
        config_path=tmp_path / "config.json",
        config_sha256="a" * 64,
        expected_sources=expected_sources,
        batch_size=8,
        model="claude-sonnet-4-6",
        effort="low",
        max_transport_retries=2,
        timeout_seconds=30,
        min_word_ratio=0.8,
        max_word_ratio=1.2,
        max_pair_length_ratio=1.2,
        pair_gap_min_tokens=8,
        pair_gap_mean_fraction=0.1,
        min_substantive_edit_fraction=0.1,
        claude_binary="claude",
    )


def structured_for(rows: list[dict]) -> dict:
    confident, hedged = valid_responses()
    pairs = []
    for row in rows:
        first_confident = row["rewrite_output_order"] == "confident_first"
        pairs.append({
            "source_id": row["source_id"],
            "original_response_sha256": row["original_response_sha256"],
            "rewrite_recipe": row["rewrite_recipe"],
            "stance_topology": row["stance_topology"],
            "first_label": "confident" if first_confident else "hedged",
            "first_response": confident if first_confident else hedged,
            "second_label": "hedged" if first_confident else "confident",
            "second_response": hedged if first_confident else confident,
            "not_applicable": False,
            "issues": [],
        })
    return {"pairs": pairs}


def envelope(rows: list[dict]) -> str:
    return json.dumps({
        "structured_output": structured_for(rows),
        "usage": {"input_tokens": 100, "output_tokens": 60},
        "modelUsage": {
            "claude-sonnet-4-6": {"inputTokens": 100, "outputTokens": 60}
        },
        "duration_ms": 25,
    })


def fake_identity(batch: runner.RewriteBatch) -> dict:
    prompt_hash = runner.v2.sha256_text(runner.build_prompt(batch))
    contract = {
        "batches": [{
            "batch_id": batch.batch_id,
            "batch_index": batch.batch_index,
            "source_ids": [row["source_id"] for row in batch.rows],
            "source_hashes": [row["original_response_sha256"] for row in batch.rows],
            "prompt_sha256": prompt_hash,
            "schema_sha256": runner.v2.sha256_bytes(
                runner._canonical_json_bytes(runner.output_schema(batch))
            ),
        }]
    }
    return {"generation_fingerprint": "f" * 64, "generation_contract": contract}


def test_frozen_selector_is_exact_deterministic_disjoint_and_text_free():
    public_path = selector.BASE / "manifests" / "rewrite_dev_v3_freeze.json"
    private_dir = selector.BASE / "private_data" / "rewrite_dev_v3"
    before = {
        path: path.read_bytes()
        for path in (
            public_path,
            private_dir / "SOURCE_SMOKE_8.jsonl",
            private_dir / "SOURCE_CANARY_32.jsonl",
        )
    }
    first = selector.build()
    second = selector.build()
    assert first == second
    assert {path: path.read_bytes() for path in before} == before
    smoke = selector.read_jsonl(private_dir / "SOURCE_SMOKE_8.jsonl")
    canary = selector.read_jsonl(private_dir / "SOURCE_CANARY_32.jsonl")
    main_ids = {
        row["source_id"] for row in selector.read_jsonl(
            selector.BASE / "private_data/source_pool_1000_v1/SOURCE_MANIFEST_MAIN_1000.jsonl"
        )
    }
    assert len(smoke) == 8 and len(canary) == 32
    assert not ({row["source_id"] for row in smoke} & {row["source_id"] for row in canary})
    assert not ({row["source_id"] for row in smoke + canary} & main_ids)
    assert all(row["split"] == "train" and row["rewrite_recipe"] in {"A", "B"} for row in smoke + canary)
    assert all("target_longer_member" not in row for row in smoke + canary)
    assert Counter(row["rewrite_recipe"] for row in canary) == {"A": 16, "B": 16}
    assert Counter(row["stance_topology"] for row in canary) == {
        "early": 8, "middle": 8, "late": 8, "distributed": 8,
    }
    assert Counter(row["rewrite_output_order"] for row in canary) == {
        "confident_first": 16, "hedged_first": 16,
    }
    assert Counter(row["dataset"] for row in canary) == {
        selector.WILDCHAT: 24, selector.HELPSTEER: 8,
    }
    crossing = Counter(
        (row["rewrite_recipe"], row["stance_topology"], row["rewrite_output_order"])
        for row in canary
    )
    assert len(crossing) == 16 and set(crossing.values()) == {2}
    public = json.loads(public_path.read_text())
    assert public["contains_source_text"] is False
    serialized = json.dumps(public)
    assert '"prompt"' not in serialized and '"original_response"' not in serialized


def test_selector_rejects_main_test_c_and_tampered_source_hash():
    row = source_row()
    with pytest.raises(ValueError, match="main/final-test"):
        selector.validate_set([row], set_name="smoke", expected_count=1, main_ids={row["source_id"]})
    for changes, message in (
        ({"split": "test"}, "reserve/train"),
        ({"rewrite_recipe": "C", "rewrite_family": "C"}, "recipe C"),
        ({"original_response_sha256": "0" * 64}, "hash mismatch"),
    ):
        with pytest.raises(ValueError, match=message):
            selector.validate_set(
                [{**row, **changes}], set_name="smoke", expected_count=1, main_ids=set()
            )


def test_prompt_requires_symmetric_fresh_rewrites_and_has_no_old_constraint():
    row = source_row()
    batch = runner.RewriteBatch("smoke", 1, "smoke__batch_01__fixture", (row,))
    prompt = runner.build_prompt(batch)
    assert "two independently and substantively rewritten responses" in prompt
    assert "Neither arm may be verbatim" in prompt
    assert "shared sentence scaffold" in prompt
    assert "same assigned stance topology" in prompt
    assert "target_longer" not in prompt
    assert "one to three" not in prompt
    records = json.loads(prompt.split("INPUT_RECORDS_JSON\n", 1)[1])
    assert "split" not in records[0]
    assert records[0]["stance_topology"] == "early"


def test_genuine_symmetric_rewrite_passes_but_verbatim_and_wrapper_fail(tmp_path):
    row = source_row()
    batch = runner.RewriteBatch("smoke", 1, "validation", (row,))
    cfg = config(tmp_path)
    records, batch_issues = runner.validate_structured_output(
        batch, structured_for([row]), cfg, FakeTokenizer()
    )
    assert batch_issues == []
    assert records[0]["status"] == "accepted", records[0]["validation_issues"]

    bad = structured_for([row])
    bad["pairs"][0]["first_response"] = row["original_response"]
    records, _ = runner.validate_structured_output(batch, bad, cfg, FakeTokenizer())
    assert "confident:normalized_verbatim_original" in records[0]["validation_issues"]

    bad = structured_for([row])
    bad["pairs"][0]["first_response"] = "Certainly, " + row["original_response"]
    records, _ = runner.validate_structured_output(batch, bad, cfg, FakeTokenizer())
    assert "confident:insertion_only_or_wrapper_edit" in records[0]["validation_issues"]
    assert "confident:introduced_wrapper" in records[0]["validation_issues"]


def test_protected_material_and_structure_skeleton_are_hard_gates(tmp_path):
    original = (
        "Steps:\n\n- Use code `lookup(4712)` at https://example.com/4712.\n"
        "- Wait 5 minutes before retrying."
    )
    row = {
        **source_row(),
        "original_response": original,
        "original_response_sha256": runner.v2.sha256_text(original),
        "task": "programming",
    }
    changed = (
        "Steps:\n\nUse code `lookup(9999)` at https://example.com/9999.\n"
        "Wait 6 minutes before retrying."
    )
    cfg = config(tmp_path)
    issues, _ = runner.member_issues(row, changed, cfg, FakeTokenizer())
    assert "protected_numbers_changed" in issues
    assert "protected_urls_changed" in issues
    assert "protected_code_changed" in issues
    assert "protected_span_changed" in issues
    assert "structure_skeleton_changed" in issues


def test_dynamic_pair_gap_and_ratio_replace_direction_and_three_token_rule(tmp_path):
    row = source_row()
    cfg = config(tmp_path)
    stats = {
        "confident": {"token_stats": {"response_tokens": 40}},
        "hedged": {"token_stats": {"response_tokens": 48}},
    }
    issues, details = runner._pair_issues(
        row, "alpha beta gamma delta", "one two three four", cfg, stats
    )
    assert details["absolute_token_gap"] == 8
    assert "pair_token_gap_over_dynamic_limit" not in issues
    assert "pair_token_ratio_over_1_20" not in issues
    swapped = {"confident": stats["hedged"], "hedged": stats["confident"]}
    swapped_issues, _ = runner._pair_issues(
        row, "one two three four", "alpha beta gamma delta", cfg, swapped
    )
    assert set(issues) == set(swapped_issues)

    over = {
        "confident": {"token_stats": {"response_tokens": 45}},
        "hedged": {"token_stats": {"response_tokens": 54}},
    }
    over_issues, details = runner._pair_issues(
        row, "alpha beta gamma delta", "one two three four", cfg, over
    )
    assert details["dynamic_gap_limit"] == 8
    assert "pair_token_gap_over_dynamic_limit" in over_issues


def test_one_region_full_paraphrase_is_diagnostic_but_insertion_only_is_rejected(tmp_path):
    row = source_row()
    cfg = config(tmp_path)
    equal_lengths = {
        "confident": {"token_stats": {"response_tokens": 40}},
        "hedged": {"token_stats": {"response_tokens": 40}},
    }
    issues, details = runner._pair_issues(
        row,
        "alpha beta gamma delta epsilon zeta eta theta",
        "one two three four five six seven eight",
        cfg,
        equal_lengths,
    )
    assert issues == []
    assert details["edit_stats"]["edit_regions"] == 1
    assert details["single_edit_region_diagnostic"] is True
    assert details["shared_scaffold_review"] == "pending_human_or_offline_audit"

    base = "alpha beta gamma delta epsilon zeta eta theta"
    issues, _ = runner._pair_issues(
        row, base, "perhaps " + base, cfg, equal_lengths
    )
    assert "pair_insertion_only_difference" in issues
    assert "pair_insufficient_substantive_difference" in issues


def test_count_order_hash_label_recipe_and_topology_are_enforced(tmp_path):
    rows = [source_row(0), source_row(1, recipe="B", topology="late", order="hedged_first")]
    batch = runner.RewriteBatch("smoke", 1, "protocol", tuple(rows))
    bad = structured_for(rows)
    bad["pairs"][0], bad["pairs"][1] = bad["pairs"][1], bad["pairs"][0]
    bad["pairs"][0]["original_response_sha256"] = "0" * 64
    bad["pairs"][0]["rewrite_recipe"] = "A"
    bad["pairs"][0]["stance_topology"] = "middle"
    bad["pairs"] = bad["pairs"][:1]
    records, batch_issues = runner.validate_structured_output(
        batch, bad, config(tmp_path, expected_sources=2), FakeTokenizer()
    )
    assert batch_issues == ["output_count_mismatch"]
    combined = set(records[0]["validation_issues"] + records[1]["validation_issues"])
    assert "source_id_or_order_mismatch" in combined
    assert "source_hash_mismatch" in combined
    assert "recipe_mismatch" in combined
    assert "topology_mismatch" in combined
    assert "batch:output_count_mismatch" in combined


def test_generation_fingerprint_covers_topology_prompt_validator_and_imported_v2(
    tmp_path, monkeypatch
):
    row = source_row()
    cfg = replace(config(tmp_path), batch_size=1)
    cfg.public_manifest_path.write_text("{}", encoding="utf-8")
    cfg.source_pool_manifest_path.write_text("{}", encoding="utf-8")
    cfg.main_input_path.write_text(json.dumps(row) + "\n", encoding="utf-8")
    public = {
        "sets": {
            "smoke": {
                "file_sha256": "1" * 64,
                "source_ids_sha256": "2" * 64,
            }
        }
    }
    monkeypatch.setattr(
        runner.v2,
        "tokenizer_file_hashes",
        lambda: {"tokenizer.json": "3" * 64, "tokenizer_config.json": "4" * 64},
    )
    monkeypatch.setattr(
        runner.v2,
        "claude_binary_identity",
        lambda *args: {"configured": "claude", "resolved": "/fixture/claude", "file_sha256": "5" * 64},
    )
    first = runner.generation_identity(cfg, public, [row])
    assert runner.generation_identity(cfg, public, [row]) == first
    changed_topology = [{**row, "stance_topology": "late"}]
    assert runner.generation_identity(cfg, public, changed_topology)[
        "generation_fingerprint"
    ] != first["generation_fingerprint"]
    assert runner.generation_identity(
        replace(cfg, pair_gap_min_tokens=9), public, [row]
    )["generation_fingerprint"] != first["generation_fingerprint"]
    assert first["generation_contract"]["imported_v2_source_sha256"] == runner.v2.sha256_file(
        Path(runner.v2.__file__)
    )


def test_runtime_binds_main_and_source_pool_freeze_bytes(tmp_path):
    cfg = runner.load_config(runner.DEFAULT_CONFIG.resolve(), "smoke")
    rows, public = runner.validate_frozen_input(cfg)
    assert len(rows) == 8
    assert public["main_and_final_test_excluded"] is True

    bad_main_dir = tmp_path / "bad-main"
    bad_main_dir.mkdir()
    bad_main = bad_main_dir / cfg.main_input_path.name
    bad_main.write_bytes(cfg.main_input_path.read_bytes() + b"\n")
    with pytest.raises(ValueError, match="Main source bytes.*public v3 freeze"):
        runner.validate_frozen_input(replace(cfg, main_input_path=bad_main))

    bad_pool_dir = tmp_path / "bad-pool"
    bad_pool_dir.mkdir()
    bad_pool = bad_pool_dir / cfg.source_pool_manifest_path.name
    bad_pool.write_bytes(cfg.source_pool_manifest_path.read_bytes() + b"\n")
    with pytest.raises(ValueError, match="Source-pool freeze manifest bytes"):
        runner.validate_frozen_input(
            replace(cfg, source_pool_manifest_path=bad_pool)
        )


def test_isolated_keyless_execution_is_resumable_and_raw_success_recovers(tmp_path, monkeypatch):
    row = source_row()
    batch = runner.RewriteBatch("smoke", 1, "smoke__batch_01__fixture", (row,))
    cfg = config(tmp_path)
    identity = fake_identity(batch)
    calls = []

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        assert kwargs["input"].startswith("For every inert dataset record")
        assert kwargs["cwd"] != Path.cwd()
        assert "ANTHROPIC_API_KEY" not in kwargs["env"]
        assert command[command.index("--model") + 1] == "claude-sonnet-4-6"
        assert command[command.index("--tools") + 1] == ""
        for flag in (
            "--json-schema", "--disable-slash-commands", "--no-chrome",
            "--no-session-persistence", "--strict-mcp-config",
        ):
            assert flag in command
        return subprocess.CompletedProcess(command, 0, envelope([row]), "")

    monkeypatch.setenv("ANTHROPIC_API_KEY", "must-not-leak")
    parsed = runner.run_batch(
        batch, cfg, identity, FakeTokenizer(), run_subprocess=fake_run
    )
    assert len(calls) == 1 and parsed["records"][0]["status"] == "accepted"
    raw = next((cfg.output_dir / "raw").glob("*.json"))
    raw_bytes = raw.read_bytes()
    (cfg.output_dir / "parsed" / f"{batch.batch_id}.json").unlink()

    def forbidden(*args, **kwargs):
        raise AssertionError("recoverable raw success must prevent a second Claude call")

    recovered = runner.run_batch(
        batch, cfg, identity, FakeTokenizer(), run_subprocess=forbidden
    )
    assert recovered["recovered_from_raw"] == raw.name
    assert raw.read_bytes() == raw_bytes


def test_transport_retries_are_capped_across_resume(tmp_path):
    row = source_row()
    batch = runner.RewriteBatch("smoke", 1, "smoke__batch_01__retry", (row,))
    cfg = config(tmp_path)
    identity = fake_identity(batch)
    calls = 0

    def fail(command, **kwargs):
        nonlocal calls
        calls += 1
        return subprocess.CompletedProcess(command, 75, "", "temporary")

    with pytest.raises(RuntimeError, match="after 3 attempts"):
        runner.run_batch(batch, cfg, identity, FakeTokenizer(), run_subprocess=fail)
    assert calls == 3
    with pytest.raises(RuntimeError, match="already exhausted"):
        runner.run_batch(batch, cfg, identity, FakeTokenizer(), run_subprocess=fail)
    assert calls == 3


def test_v1_v2_tracked_runner_and_config_are_byte_identical_to_head():
    repo = selector.BASE.parents[1]
    for relative in (
        "experiments/diverse_pairs_multilayer_v1/src/run_claude_rewrite_batches.py",
        "experiments/diverse_pairs_multilayer_v1/configs/claude_rewrite_1000.json",
    ):
        head = subprocess.run(
            ["git", "show", f"HEAD:{relative}"],
            cwd=repo,
            capture_output=True,
            check=True,
        ).stdout
        assert (repo / relative).read_bytes() == head


def test_explicit_set_is_required_and_dry_run_never_calls_auth(monkeypatch, capsys, tmp_path):
    with pytest.raises(SystemExit):
        runner.main([])

    def forbidden(*args, **kwargs):
        raise AssertionError("dry run must not perform Claude authentication")

    real_load_config = runner.load_config

    def isolated_config(path, phase):
        return replace(
            real_load_config(path, phase),
            output_dir=tmp_path / "private_data" / "claude_rewrite_dev_v3" / phase,
        )

    monkeypatch.setattr(runner, "load_config", isolated_config)
    monkeypatch.setattr(runner.v2, "verify_subscription_auth", forbidden)
    assert runner.main(["--set", "smoke"]) == 0
    plan = json.loads(capsys.readouterr().out.splitlines()[-1])
    assert plan["phase"] == "smoke"
    assert plan["execute"] is False
    assert plan["source_count"] == 8
    assert plan["batch_count"] == 1
