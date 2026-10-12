"""Focused runner tests. These never call Claude or any network service."""
from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import replace
from pathlib import Path

import pytest

from experiments.diverse_pairs_multilayer_v1.src import run_claude_rewrite_batches as runner
from experiments.diverse_pairs_multilayer_v1.src.run_claude_rewrite_batches import (
    RewriteBatch,
    RunnerConfig,
    completed_sources,
    ensure_private_output_dir,
    generation_identity,
    make_batches,
    minimal_environment,
    run_batch,
    sha256_text,
    validate_structured_output,
    validate_frozen_input,
    verify_resume_artifacts,
    verify_subscription_auth,
)


class FakeTokenizer:
    """Deterministic local token proxy; production loads the pinned Qwen snapshot."""

    def __call__(self, text, add_special_tokens=False):
        del add_special_tokens
        return {"input_ids": text.split()}

    def apply_chat_template(self, messages, tokenize=True):
        assert tokenize is True
        return list(range(3 + sum(len(item["content"].split()) for item in messages)))


def row(i: int, *, split: str = "train", recipe: str = "A", order: str = "confident_first",
        longer: str = "hedged"):
    original = f"The code is {4700 + i}. Use `lookup({i})` at https://example.com/{i}."
    return {
        "source_id": f"source-{i:03d}",
        "prompt": "What is the code?",
        "original_response": original,
        "original_response_sha256": sha256_text(original),
        "split": split,
        "rewrite_recipe": recipe,
        "rewrite_output_order": order,
        "target_longer_member": longer,
    }


def config(tmp_path: Path) -> RunnerConfig:
    return RunnerConfig(
        protocol_version="test-v1",
        input_path=tmp_path / "input.jsonl",
        input_manifest_path=tmp_path / "input.manifest.json",
        output_dir=tmp_path / "output",
        expected_sources=2,
        batch_size=20,
        timeout_seconds=30,
    )


def claude_envelope(rows, *, change_number: bool = False):
    pairs = []
    for source in rows:
        confident = source["original_response"]
        hedged = "Perhaps " + source["original_response"][0].lower() + source["original_response"][1:]
        if change_number:
            hedged = hedged.replace("4700", "9999")
        first_confident = source["rewrite_output_order"] == "confident_first"
        pairs.append({
            "source_id": source["source_id"],
            "original_response_sha256": source["original_response_sha256"],
            "first_label": "confident" if first_confident else "hedged",
            "first_response": confident if first_confident else hedged,
            "second_label": "hedged" if first_confident else "confident",
            "second_response": hedged if first_confident else confident,
            "not_applicable": False,
            "issues": [],
        })
    return json.dumps({
        "structured_output": {"pairs": pairs},
        "usage": {"input_tokens": 123, "output_tokens": 45},
        "modelUsage": {
            "claude-sonnet-4-6": {"inputTokens": 123, "outputTokens": 45}
        },
        "duration_ms": 50,
    })


def test_frozen_input_hash_count_order_and_source_hash(tmp_path):
    rows = [row(0), row(1)]
    input_path = tmp_path / "source_pool_1000.jsonl"
    payload = "".join(json.dumps(value) + "\n" for value in rows).encode()
    input_path.write_bytes(payload)
    manifest_path = tmp_path / "source_pool_1000.manifest.json"
    manifest_path.write_text(json.dumps({
        "file_sha256": hashlib.sha256(payload).hexdigest(),
        "source_count": 2,
        "source_ids_sha256": sha256_text("source-000\nsource-001\n"),
    }))
    loaded, _ = validate_frozen_input(input_path, manifest_path, 2)
    assert [value["source_id"] for value in loaded] == ["source-000", "source-001"]
    input_path.write_bytes(payload + b"\n")
    with pytest.raises(ValueError, match="file hash"):
        validate_frozen_input(input_path, manifest_path, 2)


def test_batches_are_grouped_by_split_and_recipe_and_resume_by_source_id(tmp_path):
    rows = [row(0), row(1), row(2, split="test", recipe="C"), row(3, recipe="B")]
    with pytest.raises(ValueError, match="partial frozen batch"):
        make_batches(rows, {"source-001": rows[1]["original_response_sha256"]}, 20)
    batches = make_batches(rows, {
        value["source_id"]: value["original_response_sha256"] for value in rows[:2]
    }, 20)
    assert [(batch.split, batch.recipe, len(batch.rows)) for batch in batches] == [
        ("train", "B", 1), ("test", "C", 1)
    ]


def test_resume_keeps_later_frozen_batch_ids_and_boundaries():
    rows = [row(index) for index in range(41)]
    original = make_batches(rows, {}, 20)
    completed = {
        value["source_id"]: value["original_response_sha256"]
        for value in original[0].rows
    }
    resumed = make_batches(rows, completed, 20)
    assert [batch.batch_id for batch in resumed] == [
        batch.batch_id for batch in original[1:]
    ]
    assert [batch.rows for batch in resumed] == [batch.rows for batch in original[1:]]


def test_subprocess_is_isolated_keyless_structured_and_atomic(tmp_path, monkeypatch):
    rows = [row(0), row(1, order="hedged_first")]
    batch = RewriteBatch("batch-test", "train", "A", tuple(rows))
    cfg = config(tmp_path)
    calls = []

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        assert kwargs["cwd"] != Path.cwd()
        assert "ANTHROPIC_API_KEY" not in kwargs["env"]
        assert kwargs["input"].endswith(json.dumps([
            {
                "source_id": value["source_id"],
                "original_response_sha256": value["original_response_sha256"],
                "rewrite_output_order": value["rewrite_output_order"],
                "target_longer_member": value["target_longer_member"],
                "prompt": value["prompt"],
                "original_response": value["original_response"],
                "protected_spans": runner.derived_protected_spans(value),
            } for value in rows
        ], ensure_ascii=False))
        assert command[command.index("--model") + 1] == "claude-sonnet-4-6"
        assert command[command.index("--effort") + 1] == "low"
        for flag in ["--json-schema", "--tools", "--system-prompt", "--no-chrome", "--no-session-persistence", "--strict-mcp-config"]:
            assert flag in command
        assert command[command.index("--tools") + 1] == ""
        assert "split 'train'" not in kwargs["input"]
        assert "reporting, judgment, or conclusion" in kwargs["input"]
        return subprocess.CompletedProcess(command, 0, claude_envelope(rows), "")

    monkeypatch.setenv("ANTHROPIC_API_KEY", "must-not-leak")
    parsed = run_batch(
        batch, cfg, run_subprocess=fake_run, sleeper=lambda _: None,
        tokenizer=FakeTokenizer(),
    )
    assert len(calls) == 1
    assert [record["status"] for record in parsed["records"]] == ["accepted", "accepted"]
    raw_path = next((cfg.output_dir / "raw").glob("batch-test__attempt_*.json"))
    assert json.loads(raw_path.read_text())["anthropic_api_key_present"] is False
    assert json.loads((cfg.output_dir / "parsed" / "batch-test.json").read_text())["metadata"]["usage"]["input_tokens"] == 123
    assert completed_sources(cfg.output_dir) == {value["source_id"]: value["original_response_sha256"] for value in rows}
    assert not list((cfg.output_dir / "parsed").glob(".*.tmp"))


def test_two_transport_retries_then_success(tmp_path):
    rows = [row(0)]
    batch = RewriteBatch("retry-test", "train", "A", tuple(rows))
    cfg = config(tmp_path)
    calls = 0

    def fake_run(command, **kwargs):
        nonlocal calls
        calls += 1
        if calls < 3:
            return subprocess.CompletedProcess(command, 75, "", "temporary failure")
        return subprocess.CompletedProcess(command, 0, claude_envelope(rows), "")

    parsed = run_batch(
        batch, cfg, run_subprocess=fake_run, sleeper=lambda _: None,
        tokenizer=FakeTokenizer(),
    )
    assert calls == 3
    assert parsed["transport_attempts"] == 3
    assert len(list((cfg.output_dir / "raw").glob("retry-test__attempt_*.json"))) == 3


def test_content_failure_is_marked_without_content_retry(tmp_path):
    rows = [row(0)]
    batch = RewriteBatch("content-test", "train", "A", tuple(rows))
    cfg = config(tmp_path)
    calls = 0

    def fake_run(command, **kwargs):
        nonlocal calls
        calls += 1
        return subprocess.CompletedProcess(command, 0, claude_envelope(rows, change_number=True), "")

    parsed = run_batch(
        batch, cfg, run_subprocess=fake_run, sleeper=lambda _: None,
        tokenizer=FakeTokenizer(),
    )
    assert calls == 1
    assert parsed["records"][0]["status"] == "validation_failed"
    assert "hedged:protected_numbers_changed" in parsed["records"][0]["validation_issues"]
    assert completed_sources(cfg.output_dir)["source-000"] == rows[0]["original_response_sha256"]


def test_id_hash_order_count_and_target_length_are_checked(tmp_path):
    rows = [row(0), row(1, longer="confident")]
    batch = RewriteBatch("validation-test", "train", "A", tuple(rows))
    cfg = config(tmp_path)
    structured = json.loads(claude_envelope(rows))["structured_output"]
    structured["pairs"][0], structured["pairs"][1] = structured["pairs"][1], structured["pairs"][0]
    # Also corrupt the hash and omit the second record so all protocol checks are exercised.
    structured["pairs"][0]["original_response_sha256"] = "0" * 64
    structured["pairs"] = structured["pairs"][:1]

    def fake_run(command, **kwargs):
        return subprocess.CompletedProcess(
            command, 0, json.dumps({
                "structured_output": structured,
                "usage": {},
                "modelUsage": {"claude-sonnet-4-6": {"outputTokens": 45}},
            }), ""
        )

    parsed = run_batch(
        batch, cfg, run_subprocess=fake_run, sleeper=lambda _: None,
        tokenizer=FakeTokenizer(),
    )
    assert "output_count_mismatch" in parsed["batch_validation_issues"]
    assert "source_id_or_order_mismatch" in parsed["records"][0]["validation_issues"]
    assert "source_hash_mismatch" in parsed["records"][0]["validation_issues"]
    assert "batch:output_count_mismatch" in parsed["records"][0]["validation_issues"]
    assert parsed["records"][1]["status"] == "validation_failed"

    wrong_length_rows = [row(2, longer="confident")]
    wrong_length_batch = RewriteBatch("length-direction-test", "train", "A", tuple(wrong_length_rows))

    def wrong_length_run(command, **kwargs):
        return subprocess.CompletedProcess(command, 0, claude_envelope(wrong_length_rows), "")

    length_parsed = run_batch(
        wrong_length_batch, cfg, run_subprocess=wrong_length_run,
        sleeper=lambda _: None, tokenizer=FakeTokenizer(),
    )
    assert "target_length_direction_not_met" in length_parsed["records"][0]["validation_issues"]


def test_derived_code_spans_cover_fences_indentation_and_programming_lines(tmp_path):
    original = (
        "Intro text.\n"
        "```python\n"
        "x = 1\n"
        "```\n"
        "```single_line()```\n"
        "~~~sql\n"
        "SELECT * FROM widgets;\n"
        "~~~\n"
        "~~~single_tilde()~~~\n"
        "Use `inline_call()` and ``two_ticks()``.\n"
        "    indented = 2\n"
        "\tprint(\"tabbed\")\n"
        "value = compute(3)\n"
        "print(value)\n"
    )
    source = dict(
        row(0), task="programming", original_response=original,
        original_response_sha256=sha256_text(original),
    )
    spans = runner.derived_protected_spans(source)
    assert "```python\nx = 1\n```" in spans
    assert "```single_line()```" in spans
    assert "~~~sql\nSELECT * FROM widgets;\n~~~" in spans
    assert "~~~single_tilde()~~~" in spans
    assert "`inline_call()`" in spans
    assert "``two_ticks()``" in spans
    assert any(span.startswith("    indented = 2\n\tprint") for span in spans)
    assert "value = compute(3)" in spans
    assert "print(value)" in spans

    batch = RewriteBatch("code-protection", "train", "A", (source,))
    prompt_records = json.loads(
        runner.build_prompt(batch).split("INPUT_RECORDS_JSON\n", 1)[1]
    )
    assert prompt_records[0]["protected_spans"] == spans

    changed = original.replace("value = compute(3)", "value = compute(4)")
    issues = runner.mechanical_issues(source, changed, 0.65, 1.45)
    assert "protected_code_changed" in issues
    assert "protected_span_changed" in issues


def test_batch_extra_record_invalidates_every_expected_record(tmp_path):
    source = row(0)
    batch = RewriteBatch("extra-record", "train", "A", (source,))
    structured = json.loads(claude_envelope([source]))["structured_output"]
    structured["pairs"].append(dict(structured["pairs"][0], source_id="unexpected"))
    records, batch_issues = validate_structured_output(
        batch, structured, config(tmp_path), FakeTokenizer()
    )
    assert batch_issues == ["output_count_mismatch", "unexpected_extra_records"]
    assert records[0]["status"] == "validation_failed"
    assert "batch:output_count_mismatch" in records[0]["validation_issues"]
    assert "batch:unexpected_extra_records" in records[0]["validation_issues"]


def test_environment_is_allowlisted_and_auth_requires_first_party_claude_ai(tmp_path):
    poisoned = {
        "PATH": "/safe/bin",
        "HOME": "/safe/home",
        "LANG": "C.UTF-8",
        "ANTHROPIC_API_KEY": "secret-a",
        "ANTHROPIC_BASE_URL": "https://evil.invalid",
        "CLAUDE_CODE_OAUTH_TOKEN": "secret-oauth",
        "CLAUDE_CODE_USE_BEDROCK": "1",
        "AWS_SECRET_ACCESS_KEY": "secret-aws",
        "GOOGLE_APPLICATION_CREDENTIALS": "/secret/google.json",
        "VERTEX_REGION": "elsewhere",
        "AZURE_API_KEY": "secret-azure",
        "OPENAI_BASE_URL": "https://provider.invalid",
        "HTTPS_PROXY": "http://proxy-user:proxy-secret@evil.invalid",
        "NODE_EXTRA_CA_CERTS": "/secret/mitm-ca.pem",
        "UNRELATED_SECRET": "also-not-needed",
    }
    child_env = minimal_environment(poisoned)
    assert child_env == {
        "PATH": "/safe/bin",
        "HOME": "/safe/home",
        "LANG": "C.UTF-8",
        "CLAUDE_CODE_DISABLE_AUTO_MEMORY": "1",
    }

    seen = []

    def fake_auth(command, **kwargs):
        seen.append((command, kwargs))
        return subprocess.CompletedProcess(command, 0, json.dumps({
            "loggedIn": True,
            "authMethod": "claude.ai",
            "apiProvider": "firstParty",
            "subscriptionType": "enterprise",
        }), "")

    status = verify_subscription_auth(config(tmp_path), child_env, fake_auth)
    assert status["subscriptionType"] == "enterprise"
    assert seen[0][1]["env"] is child_env
    assert seen[0][0][-3:] == ["auth", "status", "--json"]


@pytest.mark.parametrize("status", [
    {"loggedIn": False, "authMethod": "claude.ai", "apiProvider": "firstParty"},
    {"loggedIn": True, "authMethod": "apiKey", "apiProvider": "firstParty"},
    {"loggedIn": True, "authMethod": "claude.ai", "apiProvider": "bedrock"},
])
def test_auth_preflight_fails_closed(tmp_path, status):
    def fake_auth(command, **kwargs):
        return subprocess.CompletedProcess(command, 0, json.dumps(status), "")

    with pytest.raises(RuntimeError, match="loggedIn=true"):
        verify_subscription_auth(config(tmp_path), {"PATH": "/bin"}, fake_auth)


def test_auth_preflight_rejects_nonzero_and_malformed_json(tmp_path):
    def nonzero(command, **kwargs):
        return subprocess.CompletedProcess(command, 7, "", "secret diagnostic")

    with pytest.raises(RuntimeError, match="exited 7"):
        verify_subscription_auth(config(tmp_path), {}, nonzero)

    def malformed(command, **kwargs):
        return subprocess.CompletedProcess(command, 0, "not json", "")

    with pytest.raises(RuntimeError, match="invalid JSON"):
        verify_subscription_auth(config(tmp_path), {}, malformed)


def test_generation_fingerprint_covers_sources_prompts_and_contract(tmp_path, monkeypatch):
    rows = [row(0), row(1)]
    cfg = config(tmp_path)
    manifest = {
        "file_sha256": "a" * 64,
        "source_ids_sha256": sha256_text("source-000\nsource-001\n"),
    }
    first = generation_identity(cfg, manifest, rows)
    assert generation_identity(cfg, manifest, rows) == first
    changed_prompt = [dict(rows[0], prompt="Different prompt"), rows[1]]
    assert generation_identity(cfg, manifest, changed_prompt)["generation_fingerprint"] != first["generation_fingerprint"]
    assert generation_identity(
        replace(cfg, min_word_ratio=0.66), manifest, rows
    )["generation_fingerprint"] != first["generation_fingerprint"]
    assert generation_identity(
        cfg, dict(manifest, file_sha256="b" * 64), rows
    )["generation_fingerprint"] != first["generation_fingerprint"]
    for changed_rows in (
        [dict(rows[0], rewrite_family="B", rewrite_recipe="B"), rows[1]],
        [dict(rows[0], rewrite_output_order="hedged_first"), rows[1]],
        [dict(rows[0], target_longer_member="confident"), rows[1]],
        list(reversed(rows)),
    ):
        assert generation_identity(
            cfg, manifest, changed_rows
        )["generation_fingerprint"] != first["generation_fingerprint"]
    for changed_config in (
        replace(cfg, model="different-model"),
        replace(cfg, effort="medium"),
        replace(cfg, protocol_version="test-v2"),
        replace(cfg, claude_binary="different-claude"),
    ):
        assert generation_identity(
            changed_config, manifest, rows
        )["generation_fingerprint"] != first["generation_fingerprint"]
    with monkeypatch.context() as scoped:
        scoped.setattr(runner, "SYSTEM_PROMPT", "changed system instruction")
        assert generation_identity(cfg, manifest, rows)["generation_fingerprint"] != first["generation_fingerprint"]
    with monkeypatch.context() as scoped:
        scoped.setitem(runner.RECIPE_INSTRUCTIONS, "A", "changed recipe")
        assert generation_identity(cfg, manifest, rows)["generation_fingerprint"] != first["generation_fingerprint"]
    with monkeypatch.context() as scoped:
        scoped.setattr(runner, "RUNNER_VERSION", "changed-runner")
        assert generation_identity(cfg, manifest, rows)["generation_fingerprint"] != first["generation_fingerprint"]
    assert first["generation_contract"]["system_prompt"] == runner.SYSTEM_PROMPT
    assert first["generation_contract"]["recipe_instructions"] == runner.RECIPE_INSTRUCTIONS


def test_resume_rejects_wrong_fingerprint_unknown_and_duplicate_records(tmp_path):
    source = row(0)
    parsed = tmp_path / "out" / "parsed"
    parsed.mkdir(parents=True)
    record = {
        "source_id": source["source_id"],
        "original_response_sha256": source["original_response_sha256"],
        "status": "accepted",
    }
    (parsed / "one.json").write_text(json.dumps({
        "generation_fingerprint": "correct",
        "terminal": True,
        "records": [record],
    }))
    assert completed_sources(tmp_path / "out", "correct", [source]) == {
        source["source_id"]: source["original_response_sha256"]
    }
    with pytest.raises(ValueError, match="fingerprint"):
        completed_sources(tmp_path / "out", "wrong", [source])
    (parsed / "two.json").write_text(json.dumps({
        "generation_fingerprint": "correct",
        "terminal": True,
        "records": [record],
    }))
    with pytest.raises(ValueError, match="Duplicate"):
        completed_sources(tmp_path / "out", "correct", [source])


def test_output_dir_must_remain_under_experiment_private_data(tmp_path):
    assert ensure_private_output_dir(runner.PRIVATE_DATA / "claude-test").is_relative_to(
        runner.PRIVATE_DATA.resolve()
    )
    with pytest.raises(ValueError, match="private_data"):
        ensure_private_output_dir(tmp_path / "public-output")


def test_writer_issues_not_applicable_reason_and_token_gap_are_enforced(tmp_path):
    source = row(0)
    batch = RewriteBatch("validation", "train", "A", (source,))
    cfg = config(tmp_path)
    structured = json.loads(claude_envelope([source]))["structured_output"]
    structured["pairs"][0]["issues"] = ["The wording may still be awkward"]
    records, _ = validate_structured_output(batch, structured, cfg, FakeTokenizer())
    assert records[0]["status"] == "needs_review"
    assert "writer_reported_issue" in records[0]["validation_issues"]

    item = structured["pairs"][0]
    item.update(first_response="", second_response="", not_applicable=True, issues=[])
    records, _ = validate_structured_output(batch, structured, cfg, FakeTokenizer())
    assert records[0]["status"] == "validation_failed"
    assert "not_applicable_missing_reason" in records[0]["validation_issues"]
    item["issues"] = ["The source contains no assertive answer"]
    records, _ = validate_structured_output(batch, structured, cfg, FakeTokenizer())
    assert records[0]["status"] == "not_applicable"

    item.update(
        first_response=source["original_response"],
        second_response="Perhaps " + source["original_response"],
        not_applicable="false",
        issues=[],
    )
    records, _ = validate_structured_output(batch, structured, cfg, FakeTokenizer())
    assert records[0]["status"] == "validation_failed"
    assert "not_applicable_not_boolean" in records[0]["validation_issues"]

    structured = json.loads(claude_envelope([source]))["structured_output"]
    structured["pairs"][0]["second_response"] = "Possibly perhaps maybe arguably " + source["original_response"]
    records, _ = validate_structured_output(batch, structured, cfg, FakeTokenizer())
    assert "pair_token_gap_over_3" in records[0]["validation_issues"]


def test_qwen_response_and_full_chat_limits_are_hard_failures(tmp_path):
    source = row(0)
    batch = RewriteBatch("limits", "train", "A", (source,))
    cfg = config(tmp_path)
    structured = json.loads(claude_envelope([source]))["structured_output"]
    structured["pairs"][0]["second_response"] = "word " * 513
    records, _ = validate_structured_output(batch, structured, cfg, FakeTokenizer())
    assert "hedged:response_token_limit_exceeded" in records[0]["validation_issues"]

    long_prompt_source = dict(source, prompt="prompt " * 1015)
    long_batch = RewriteBatch("full-limit", "train", "A", (long_prompt_source,))
    structured = json.loads(claude_envelope([long_prompt_source]))["structured_output"]
    records, _ = validate_structured_output(long_batch, structured, cfg, FakeTokenizer())
    assert any("full_input_token_limit_exceeded" in issue for issue in records[0]["validation_issues"])


def test_numbers_attached_to_units_and_identifiers_are_protected(tmp_path):
    original = "Use GPT-4 with v2.1 and lift 5kg."
    source = {
        **row(0),
        "original_response": original,
        "original_response_sha256": sha256_text(original),
    }
    batch = RewriteBatch("numeric-identifiers", "train", "A", (source,))
    structured = json.loads(claude_envelope([source]))["structured_output"]
    structured["pairs"][0]["second_response"] = "Perhaps use GPT-5 with v2.2 and lift 6kg."
    records, _ = validate_structured_output(
        batch, structured, config(tmp_path), FakeTokenizer()
    )
    assert "hedged:protected_numbers_changed" in records[0]["validation_issues"]


def test_raw_success_is_recovered_without_another_call_or_overwrite(tmp_path):
    rows = [row(0)]
    batch = RewriteBatch("recover", "train", "A", tuple(rows))
    cfg = config(tmp_path)
    fingerprint = "f" * 64
    calls = 0

    def first_run(command, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 1:
            return subprocess.CompletedProcess(command, 75, "", "temporary")
        return subprocess.CompletedProcess(command, 0, claude_envelope(rows), "")

    run_batch(
        batch, cfg, run_subprocess=first_run, sleeper=lambda _: None,
        tokenizer=FakeTokenizer(), generation_fingerprint=fingerprint,
    )
    raw_paths = list((cfg.output_dir / "raw").glob("recover__attempt_*.json"))
    raw_bytes = {path: path.read_bytes() for path in raw_paths}
    (cfg.output_dir / "parsed" / "recover.json").unlink()

    def forbidden_call(command, **kwargs):
        raise AssertionError("a recoverable raw success must not call Claude again")

    recovered = run_batch(
        batch, cfg, run_subprocess=forbidden_call, sleeper=lambda _: None,
        tokenizer=FakeTokenizer(), generation_fingerprint=fingerprint,
    )
    assert calls == 2
    assert recovered["transport_attempts"] == 2
    assert recovered["recovered_from_raw"].endswith(".json")
    assert list((cfg.output_dir / "raw").glob("recover__attempt_*.json")) == raw_paths
    assert {path: path.read_bytes() for path in raw_paths} == raw_bytes


def test_legacy_raw_is_revalidated_into_new_namespace_with_exact_lineage(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(runner, "PRIVATE_DATA", tmp_path)
    rows = [row(0)]
    batch = make_batches(rows, {}, 20)[0]
    new_cfg = config(tmp_path)
    new_cfg = replace(new_cfg, output_dir=tmp_path / "new")
    manifest = {
        "file_sha256": "a" * 64,
        "source_ids_sha256": sha256_text("source-000\n"),
    }
    identity = generation_identity(new_cfg, manifest, rows)
    identity["generation_contract"]["claude_binary_identity"] = {
        "configured": "claude",
        "resolved": "/fixture/claude",
        "file_sha256": "b" * 64,
    }
    identity["generation_fingerprint"] = runner.sha256_bytes(
        runner._canonical_json_bytes(identity["generation_contract"])
    )

    legacy_contract = json.loads(json.dumps(identity["generation_contract"]))
    legacy_contract["runner_version"] = "2.0"
    legacy_contract["runner_source_sha256"] = "c" * 64
    legacy_contract["validation_contract"].pop("reported_model_policy")
    legacy_fingerprint = runner.sha256_bytes(
        runner._canonical_json_bytes(legacy_contract)
    )
    legacy_dir = tmp_path / "legacy"
    raw_dir = legacy_dir / "raw"
    parsed_dir = legacy_dir / "parsed"
    raw_dir.mkdir(parents=True)
    parsed_dir.mkdir()
    settings_path = Path("/fixture/legacy-settings.json")
    command = runner.claude_command(
        replace(new_cfg, claude_binary="/fixture/claude"), batch, settings_path
    )
    completed = subprocess.CompletedProcess(
        command, 0, claude_envelope(rows), ""
    )
    raw = runner._transport_record(
        batch, 1, command, completed, generation_fingerprint=legacy_fingerprint
    )
    raw["runner_version"] = "2.0"
    raw_path = raw_dir / f"{batch.batch_id}__attempt_000001__fixture.json"
    raw_path.write_text(json.dumps(raw))
    legacy_failure_path = parsed_dir / f"{batch.batch_id}.json"
    legacy_failure_path.write_text(json.dumps({
        "runner_version": "2.0",
        "generation_fingerprint": legacy_fingerprint,
        "batch_id": batch.batch_id,
        "terminal": False,
        "processing_failed": True,
        "records": [],
    }))
    (legacy_dir / "run_manifest.json").write_text(json.dumps({
        "runner_version": "2.0",
        "protocol_version": "claude-diverse-rewrite-v1",
        "generation_fingerprint": legacy_fingerprint,
        "generation_contract": legacy_contract,
    }))
    legacy_bytes = {
        path: path.read_bytes()
        for path in (raw_path, legacy_failure_path, legacy_dir / "run_manifest.json")
    }

    recovered = runner.recover_legacy_batch(
        batch, new_cfg, FakeTokenizer(), identity, legacy_dir
    )
    assert recovered["terminal"] is True
    assert recovered["processing_failed"] is False
    assert len(recovered["records"]) == 1
    provenance = recovered["recovered_from_legacy"]
    assert provenance["generation_fingerprint"] == legacy_fingerprint
    assert provenance["additional_claude_calls"] == 0
    assert provenance["raw_artifact_sha256"] == runner.sha256_file(raw_path)
    assert not (new_cfg.output_dir / "raw").exists()
    assert {
        path: path.read_bytes() for path in legacy_bytes
    } == legacy_bytes
    verify_resume_artifacts(new_cfg.output_dir, identity)


def test_legacy_recovery_rejects_changed_request_contract(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, "PRIVATE_DATA", tmp_path)
    rows = [row(0)]
    cfg = replace(config(tmp_path), output_dir=tmp_path / "new")
    manifest = {
        "file_sha256": "a" * 64,
        "source_ids_sha256": sha256_text("source-000\n"),
    }
    identity = generation_identity(cfg, manifest, rows)
    legacy_dir = tmp_path / "legacy"
    legacy_dir.mkdir()
    incompatible = json.loads(json.dumps(identity["generation_contract"]))
    incompatible["system_prompt"] = "changed generation instruction"
    (legacy_dir / "run_manifest.json").write_text(json.dumps({
        "generation_fingerprint": "d" * 64,
        "generation_contract": incompatible,
    }))
    with pytest.raises(ValueError, match="not byte-equivalent"):
        runner.recover_legacy_batch(
            make_batches(rows, {}, 20)[0], cfg, FakeTokenizer(), identity, legacy_dir
        )


def test_resume_verifier_rejects_tampered_raw_content(tmp_path):
    rows = [row(0)]
    cfg = config(tmp_path)
    manifest = {
        "file_sha256": "a" * 64,
        "source_ids_sha256": sha256_text("source-000\n"),
    }
    identity = generation_identity(cfg, manifest, rows)
    batch = make_batches(rows, {}, 20)[0]

    def fake_run(command, **kwargs):
        return subprocess.CompletedProcess(command, 0, claude_envelope(rows), "")

    run_batch(
        batch, cfg, run_subprocess=fake_run, sleeper=lambda _: None,
        tokenizer=FakeTokenizer(),
        generation_fingerprint=identity["generation_fingerprint"],
    )
    verify_resume_artifacts(cfg.output_dir, identity)
    raw_path = next((cfg.output_dir / "raw").glob("*.json"))
    raw = json.loads(raw_path.read_text())
    raw["stdout"] += " "
    raw_path.write_text(json.dumps(raw))
    with pytest.raises(ValueError, match="raw artifact content hash"):
        verify_resume_artifacts(cfg.output_dir, identity)


def test_error_envelope_is_processing_failure_without_content_retry(tmp_path):
    rows = [row(0)]
    batch = RewriteBatch("error-envelope", "train", "A", tuple(rows))
    cfg = config(tmp_path)
    calls = 0

    def fake_run(command, **kwargs):
        nonlocal calls
        calls += 1
        return subprocess.CompletedProcess(
            command, 0, json.dumps({"is_error": True, "result": "failure"}), ""
        )

    parsed = run_batch(
        batch, cfg, run_subprocess=fake_run, sleeper=lambda _: None,
        tokenizer=FakeTokenizer(), generation_fingerprint="e" * 64,
    )
    assert calls == 1
    assert parsed["terminal"] is False
    assert parsed["processing_failed"] is True
    assert parsed["records"] == []

    def forbidden_retry(command, **kwargs):
        raise AssertionError("semantic/content failures must not be retried")

    assert run_batch(
        batch, cfg, run_subprocess=forbidden_retry, sleeper=lambda _: None,
        tokenizer=FakeTokenizer(), generation_fingerprint="e" * 64,
    )["processing_failed"] is True


@pytest.mark.parametrize("model_usage", [
    {},
    {"different-model": {"inputTokens": 1}},
])
def test_missing_or_wrong_reported_model_is_processing_failure(tmp_path, model_usage):
    rows = [row(0)]
    batch = RewriteBatch("reported-model", "train", "A", tuple(rows))
    cfg = config(tmp_path)
    envelope = json.loads(claude_envelope(rows))
    envelope["modelUsage"] = model_usage

    def fake_run(command, **kwargs):
        return subprocess.CompletedProcess(command, 0, json.dumps(envelope), "")

    parsed = run_batch(
        batch, cfg, run_subprocess=fake_run, sleeper=lambda _: None,
        tokenizer=FakeTokenizer(), generation_fingerprint="m" * 64,
    )
    assert parsed["processing_failed"] is True
    assert parsed["terminal"] is False


def test_small_allowlisted_internal_helper_is_accepted_and_recorded(tmp_path):
    rows = [row(0)]
    batch = RewriteBatch("helper-model", "train", "A", tuple(rows))
    cfg = config(tmp_path)
    envelope = json.loads(claude_envelope(rows))
    envelope["usage"]["output_tokens"] = 13_988
    envelope["modelUsage"] = {
        "claude-haiku-4-5-20251001": {
            "inputTokens": 13_900, "outputTokens": 15,
        },
        "claude-sonnet-4-6": {
            "inputTokens": 4, "outputTokens": 13_988,
        },
    }

    def fake_run(command, **kwargs):
        return subprocess.CompletedProcess(command, 0, json.dumps(envelope), "")

    parsed = run_batch(
        batch, cfg, run_subprocess=fake_run, sleeper=lambda _: None,
        tokenizer=FakeTokenizer(), generation_fingerprint="h" * 64,
    )
    assert parsed["terminal"] is True
    validation = parsed["metadata"]["reported_model_validation"]
    assert validation["policy_passed"] is True
    assert validation["requested_output_tokens"] == 13_988
    assert validation["internal_helper_output_tokens"] == {
        "claude-haiku-4-5-20251001": 15
    }
    assert validation["internal_helper_output_share"] < 0.01


@pytest.mark.parametrize("model_usage,aggregate_output", [
    ({
        "claude-sonnet-4-6": {"outputTokens": 10_000},
        "unapproved-helper": {"outputTokens": 1},
    }, 10_000),
    ({
        "claude-sonnet-4-6": {"outputTokens": 10_000},
        "claude-haiku-4-5-20251001": {"outputTokens": 65},
    }, 10_000),
    ({
        "claude-sonnet-4-6": {"outputTokens": 989},
        "claude-haiku-4-5-20251001": {"outputTokens": 11},
    }, 989),
    ({"claude-sonnet-4-6": {"outputTokens": 0}}, 0),
    ({"claude-sonnet-4-6": {"outputTokens": True}}, True),
    ({"claude-sonnet-4-6": {}}, None),
])
def test_untrusted_or_substantive_helper_model_usage_is_rejected(
    tmp_path, model_usage, aggregate_output
):
    rows = [row(0)]
    batch = RewriteBatch("bad-helper-model", "train", "A", tuple(rows))
    cfg = config(tmp_path)
    envelope = json.loads(claude_envelope(rows))
    envelope["modelUsage"] = model_usage
    if aggregate_output is None:
        envelope["usage"].pop("output_tokens")
    else:
        envelope["usage"]["output_tokens"] = aggregate_output

    def fake_run(command, **kwargs):
        return subprocess.CompletedProcess(command, 0, json.dumps(envelope), "")

    parsed = run_batch(
        batch, cfg, run_subprocess=fake_run, sleeper=lambda _: None,
        tokenizer=FakeTokenizer(), generation_fingerprint="u" * 64,
    )
    assert parsed["processing_failed"] is True
    assert parsed["terminal"] is False


def test_transport_retry_budget_is_global_across_resume(tmp_path):
    rows = [row(0)]
    batch = RewriteBatch("retry-budget", "train", "A", tuple(rows))
    cfg = config(tmp_path)
    calls = 0

    def always_fail(command, **kwargs):
        nonlocal calls
        calls += 1
        return subprocess.CompletedProcess(command, 75, "", "temporary")

    first = run_batch(
        batch, cfg, run_subprocess=always_fail, sleeper=lambda _: None,
        tokenizer=FakeTokenizer(), generation_fingerprint="r" * 64,
    )
    assert first["transport_exhausted"] is True
    assert calls == 3

    def forbidden_retry(command, **kwargs):
        raise AssertionError("the two-retry production budget was already exhausted")

    second = run_batch(
        batch, cfg, run_subprocess=forbidden_retry, sleeper=lambda _: None,
        tokenizer=FakeTokenizer(), generation_fingerprint="r" * 64,
    )
    assert second["transport_exhausted"] is True
    assert calls == 3


def _write_main_fixture(tmp_path: Path, monkeypatch) -> Path:
    private = tmp_path / "private_data"
    manifests = tmp_path / "manifests"
    configs = tmp_path / "configs"
    private.mkdir()
    manifests.mkdir()
    configs.mkdir()
    rows = [row(0)]
    payload = "".join(json.dumps(value) + "\n" for value in rows).encode()
    (private / "input.jsonl").write_bytes(payload)
    (manifests / "freeze.json").write_text(json.dumps({
        "file_sha256": hashlib.sha256(payload).hexdigest(),
        "source_count": 1,
        "source_ids_sha256": sha256_text("source-000\n"),
    }))
    config_path = configs / "runner.json"
    config_path.write_text(json.dumps({
        "protocol_version": "test-v1",
        "input_path": "private_data/input.jsonl",
        "input_manifest_path": "manifests/freeze.json",
        "output_dir": "private_data/output",
        "expected_sources": 1,
        "batch_size": 20,
        "model": "claude-sonnet-4-6",
        "effort": "low",
        "max_transport_retries": 2,
        "timeout_seconds": 30,
        "min_word_ratio": 0.65,
        "max_word_ratio": 1.45,
        "claude_binary": "claude",
    }))
    monkeypatch.setattr(runner, "PRIVATE_DATA", private)
    return config_path


@pytest.mark.parametrize("failure", [
    {"processing_failed": True, "transport_exhausted": False},
    {"processing_failed": False, "transport_exhausted": True},
])
def test_main_shares_scrubbed_env_and_returns_nonzero_on_batch_failure(
    tmp_path, monkeypatch, failure
):
    config_path = _write_main_fixture(tmp_path, monkeypatch)
    observed = {}

    def fake_auth(cfg, child_env):
        observed["auth_env"] = child_env
        return {"loggedIn": True, "authMethod": "claude.ai", "apiProvider": "firstParty"}

    def fake_batch(batch, cfg, **kwargs):
        observed["batch_env"] = kwargs["child_env"]
        return failure

    monkeypatch.setenv("ANTHROPIC_API_KEY", "never-forward-this")
    monkeypatch.setattr(runner, "verify_subscription_auth", fake_auth)
    monkeypatch.setattr(runner, "load_pinned_tokenizer", lambda *_: FakeTokenizer())
    monkeypatch.setattr(runner, "run_batch", fake_batch)
    rc = runner.main(["--config", str(config_path), "--execute", "--max-batches", "1"])
    assert rc == 1
    assert observed["auth_env"] is observed["batch_env"]
    assert "ANTHROPIC_API_KEY" not in observed["auth_env"]


def test_main_auth_failure_is_nonzero_and_creates_no_output(tmp_path, monkeypatch):
    config_path = _write_main_fixture(tmp_path, monkeypatch)

    def reject_auth(cfg, child_env):
        raise RuntimeError("not first-party")

    monkeypatch.setattr(runner, "verify_subscription_auth", reject_auth)
    monkeypatch.setattr(
        runner, "load_pinned_tokenizer",
        lambda *_: (_ for _ in ()).throw(AssertionError("auth must run first")),
    )
    assert runner.main(["--config", str(config_path), "--execute"]) == 2
    assert not (tmp_path / "private_data" / "output").exists()


def test_main_recover_only_never_checks_auth_or_invokes_generation(tmp_path, monkeypatch):
    config_path = _write_main_fixture(tmp_path, monkeypatch)
    legacy_dir = tmp_path / "private_data" / "legacy"
    legacy_dir.mkdir()
    seen = []

    monkeypatch.setattr(runner, "load_pinned_tokenizer", lambda *_: FakeTokenizer())

    def fake_recover(batch, cfg, tokenizer, identity, source_dir):
        seen.append((batch.batch_id, source_dir))
        return {"terminal": True, "processing_failed": False}

    monkeypatch.setattr(runner, "recover_legacy_batch", fake_recover)
    monkeypatch.setattr(runner, "verify_subscription_auth", lambda *_: (
        _ for _ in ()
    ).throw(AssertionError("recover-only must not check Claude auth")))
    monkeypatch.setattr(runner, "run_batch", lambda *_args, **_kwargs: (
        _ for _ in ()
    ).throw(AssertionError("recover-only must not invoke Claude")))
    monkeypatch.setattr(runner, "write_run_manifest", lambda *_args, **_kwargs: {
        "generation_fingerprint": "f" * 64,
        "terminal_sources": 20,
        "remaining_sources": 980,
        "status_counts": {"accepted": 20},
    })

    rc = runner.main([
        "--config", str(config_path),
        "--recover-only",
        "--recover-from-output-dir", str(legacy_dir),
        "--max-batches", "1",
    ])
    assert rc == 0
    assert len(seen) == 1
    assert seen[0][1] == legacy_dir.resolve()
