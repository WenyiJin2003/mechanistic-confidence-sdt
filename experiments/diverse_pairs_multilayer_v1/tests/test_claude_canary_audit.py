"""Private-text canary audit tests.  No network or Claude process is used."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

from experiments.diverse_pairs_multilayer_v1.src import audit_claude_canary as audit
from experiments.diverse_pairs_multilayer_v1.src import run_claude_rewrite_batches as runner


class FakeTokenizer:
    def __call__(self, text, add_special_tokens=False):
        del add_special_tokens
        return {"input_ids": text.split()}

    def apply_chat_template(self, messages, tokenize=True):
        assert tokenize is True
        return list(range(3 + sum(len(item["content"].split()) for item in messages)))


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def _insert(original: str, phrase: list[str], position: int) -> str:
    words = original.split()
    return " ".join(words[:position] + phrase + words[position:])


def _fixture(tmp_path: Path):
    unique_words = [f"unique{chr(ord('a') + index)}mark" for index in range(20)]
    confident_roots = ["certain", "believe", "likely", "appears", "settled", "conclude", "must"]
    hedged_roots = ["uncertain", "think", "perhaps", "seems", "provisional", "suspect", "might"]
    rows = []
    pairs = []
    for index, unique in enumerate(unique_words):
        original = (
            f"The {unique} result follows directly from the stated assumptions and preserves "
            "the requested conclusion while retaining every supporting detail condition and "
            "qualification in the explanation for this distinct example."
        )
        target = "confident" if index % 2 == 0 else "hedged"
        order = "confident_first" if index % 3 == 0 else "hedged_first"
        insertion_positions = (4, 12, 21)
        conf_position = insertion_positions[index % len(insertion_positions)]
        hedge_position = insertion_positions[(index + 1) % len(insertion_positions)]
        conf_phrase = [confident_roots[index % len(confident_roots)], unique, "stance"]
        hedge_phrase = [hedged_roots[index % len(hedged_roots)], unique, "calibration"]
        if target == "confident":
            conf_phrase.append("firmly")
        else:
            hedge_phrase.append("moderately")
        confident = _insert(original, conf_phrase, conf_position)
        hedged = _insert(original, hedge_phrase, hedge_position)
        row = {
            "source_id": f"private-source-{index:02d}",
            "prompt": f"private-prompt-{index:02d}-do-not-publish",
            "original_response": original,
            "original_response_sha256": _digest(original),
            "split": "train",
            "rewrite_family": "A",
            "rewrite_recipe": "A",
            "rewrite_output_order": order,
            "target_longer_member": target,
            "task": sorted(audit.TASKS)[index % len(audit.TASKS)],
            "dataset": "allenai/WildChat-1M",
            "length_bin": sorted(audit.LENGTH_BINS)[index % len(audit.LENGTH_BINS)],
        }
        rows.append(row)
        confident_first = order == "confident_first"
        pairs.append({
            "source_id": row["source_id"],
            "original_response_sha256": row["original_response_sha256"],
            "first_label": "confident" if confident_first else "hedged",
            "first_response": confident if confident_first else hedged,
            "second_label": "hedged" if confident_first else "confident",
            "second_response": hedged if confident_first else confident,
            "not_applicable": False,
            "issues": [],
        })
    batch = runner.RewriteBatch("canary-test", "train", "A", tuple(rows))
    config = runner.RunnerConfig(
        protocol_version="test-v1",
        input_path=tmp_path / "input.jsonl",
        input_manifest_path=tmp_path / "manifest.json",
        output_dir=tmp_path / "private_data" / "out",
        expected_sources=20,
        batch_size=20,
        timeout_seconds=30,
    )
    envelope = {
        "structured_output": {"pairs": pairs},
        "is_error": False,
        "modelUsage": {
            "claude-sonnet-4-6": {"outputTokens": 2000},
            "claude-haiku-4-5-20251001": {"outputTokens": 15},
        },
        "usage": {},
    }
    raw = {
        "batch_id": batch.batch_id,
        "source_ids": [row["source_id"] for row in rows],
        "source_hashes": [row["original_response_sha256"] for row in rows],
        "batch_prompt_sha256": runner.sha256_text(runner.build_prompt(batch)),
        "returncode": 0,
        "transport_error": None,
        "provider_environment_scrubbed": True,
        "anthropic_api_key_present": False,
        "stderr": "",
        "stderr_sha256": runner.sha256_text(""),
    }
    _refresh(raw, envelope)
    return batch, config, raw, envelope


def _refresh(raw, envelope):
    stdout = json.dumps(envelope)
    raw["stdout"] = stdout
    raw["stdout_sha256"] = runner.sha256_text(stdout)


def _parsed_fixture(batch, config, envelope):
    records, batch_issues = runner.validate_structured_output(
        batch, envelope["structured_output"], config, FakeTokenizer()
    )
    return {
        "protocol_version": config.protocol_version,
        "batch_id": batch.batch_id,
        "source_ids": [row["source_id"] for row in batch.rows],
        "source_hashes": [row["original_response_sha256"] for row in batch.rows],
        "batch_prompt_sha256": runner.sha256_text(runner.build_prompt(batch)),
        "split": batch.split,
        "rewrite_recipe": batch.recipe,
        "requested_model": config.model,
        "requested_effort": config.effort,
        "terminal": True,
        "processing_failed": False,
        "batch_validation_issues": batch_issues,
        "records": records,
        "records_sha256": runner.sha256_bytes(runner._canonical_json_bytes(records)),
    }


def _pair_by_label(pair, label):
    return "first_response" if pair["first_label"] == label else "second_response"


def test_clean_canary_passes_and_summary_is_private(tmp_path):
    batch, config, raw, _ = _fixture(tmp_path)
    summary, forbidden = audit.audit_batch(batch, raw, config, FakeTokenizer())
    assert summary["decision"]["automated_gate_pass"] is True
    assert summary["transport_and_envelope"]["auxiliary_model_count"] == 1
    assert summary["transport_and_envelope"]["auxiliary_output_tokens"] == 15
    assert summary["runner_validation"]["status_counts"]["accepted"] == 20
    serialized = json.dumps(summary)
    assert not audit.HEX64_RE.search(serialized)
    for value in forbidden:
        if len(value.strip()) >= 12:
            assert value not in serialized
    assert set(summary) == audit.TOP_LEVEL_KEYS


def test_auxiliary_model_gate_is_bounded(tmp_path):
    batch, config, raw, envelope = _fixture(tmp_path)
    envelope["modelUsage"]["claude-haiku-4-5-20251001"]["outputTokens"] = 33
    _refresh(raw, envelope)
    summary, _ = audit.audit_batch(batch, raw, config, FakeTokenizer())
    assert summary["transport_and_envelope"]["auxiliary_usage_within_gate"] is False
    assert summary["issue_counts"]["model_usage_contract"] == 1
    assert summary["decision"]["automated_gate_pass"] is False

    batch, config, raw, envelope = _fixture(tmp_path)
    envelope["modelUsage"]["unexpected-model"] = {"outputTokens": 1}
    _refresh(raw, envelope)
    summary, _ = audit.audit_batch(batch, raw, config, FakeTokenizer())
    assert summary["issue_counts"]["model_usage_contract"] == 1


def test_parsed_artifact_matches_independent_revalidation_and_counts_length_issues(tmp_path):
    batch, config, raw, envelope = _fixture(tmp_path)
    pair = envelope["structured_output"]["pairs"][0]
    hedge_field = _pair_by_label(pair, "hedged")
    pair[hedge_field] += " extraone extratwo extrathree extrafour extrafive"
    _refresh(raw, envelope)
    parsed = _parsed_fixture(batch, config, envelope)

    summary, forbidden = audit.audit_batch(
        batch, raw, config, FakeTokenizer(), parsed=parsed
    )
    artifact = summary["runner_validation"]["parsed_artifact"]
    assert artifact["present"] is True
    assert artifact["records_hash_valid"] is True
    assert artifact["matches_independent_revalidation"] is True
    assert artifact["length_control_issue_record_counts"] == {
        "target_length_direction_not_met": 1,
        "pair_token_gap_over_3": 1,
    }
    assert artifact["length_control_only_failed_record_count"] == 1
    assert artifact["other_validation_issue_record_count"] == 0
    assert summary["issue_counts"]["parsed_artifact_mismatch"] == 0
    serialized = json.dumps(summary)
    for value in forbidden:
        if len(value.strip()) >= 12:
            assert value not in serialized

    mismatched = copy.deepcopy(parsed)
    mismatched["processing_failed"] = True
    summary, _ = audit.audit_batch(
        batch, raw, config, FakeTokenizer(), parsed=mismatched
    )
    assert summary["issue_counts"]["parsed_artifact_mismatch"] == 1
    assert "parsed_artifact_mismatch" in summary["decision"]["blocker_categories"]
    assert summary["decision"]["automated_gate_pass"] is False


def test_pair_level_verbatim_structure_wrapper_ratio_and_leak_checks(tmp_path):
    batch, config, raw, envelope = _fixture(tmp_path)
    pairs = envelope["structured_output"]["pairs"]
    original0 = batch.rows[0]["original_response"]
    pairs[0][_pair_by_label(pairs[0], "confident")] = original0
    original1 = batch.rows[1]["original_response"]
    pairs[1][_pair_by_label(pairs[1], "hedged")] = "I am not fully certain. " + original1
    original2 = batch.rows[2]["original_response"]
    pairs[2][_pair_by_label(pairs[2], "hedged")] = original2 + "\n\nA separate paragraph changes structure."
    pairs[3][_pair_by_label(pairs[3], "hedged")] += " " + " ".join(
        batch.rows[4]["original_response"].split()[:10]
    )
    pairs[5][_pair_by_label(pairs[5], "hedged")] += " " + "extra " * 20
    _refresh(raw, envelope)
    summary, _ = audit.audit_batch(batch, raw, config, FakeTokenizer())
    assert summary["issue_counts"]["verbatim_original"] >= 1
    assert summary["issue_counts"]["generic_wrapper"] >= 1
    assert summary["issue_counts"]["structure_mismatch"] >= 1
    assert summary["issue_counts"]["cross_record_leakage"] >= 1
    assert summary["issue_counts"]["tight_length_ratio"] >= 1
    assert summary["decision"]["automated_gate_pass"] is False


def test_global_reuse_thresholds_are_exact(tmp_path):
    batch, config, raw, envelope = _fixture(tmp_path)
    pairs = envelope["structured_output"]["pairs"]
    for index in range(5):
        field = _pair_by_label(pairs[index], "hedged")
        pairs[index][field] = _insert(
            batch.rows[index]["original_response"],
            ["shared", "three", "tokens"],
            12,
        )
    _refresh(raw, envelope)
    summary, _ = audit.audit_batch(batch, raw, config, FakeTokenizer())
    assert summary["global_shortcut_checks"]["maximum_reused_three_token_span_pair_frequency"] == 5
    assert summary["issue_counts"]["reused_three_token_span"] == 1

    batch, config, raw, envelope = _fixture(tmp_path)
    pairs = envelope["structured_output"]["pairs"]
    for index in range(4):
        field = _pair_by_label(pairs[index], "hedged")
        pairs[index][field] = _insert(
            batch.rows[index]["original_response"],
            ["shared", "four", "token", "template"],
            12,
        )
    _refresh(raw, envelope)
    summary, _ = audit.audit_batch(batch, raw, config, FakeTokenizer())
    assert summary["global_shortcut_checks"]["maximum_reused_four_plus_token_span_pair_frequency"] == 4
    assert summary["issue_counts"]["reused_four_plus_token_span"] == 1


def _semantic_payload(reversed_index=None):
    reviews = []
    for index in range(1, 21):
        reviews.append({
            "review_index": index,
            "content_preserved": "pass",
            "certainty_ordering": "reversed" if index == reversed_index else "correct",
            "speaker_scope": "pass",
            "other_confound": "none",
            "formatting": "pass",
            "naturalness": "pass",
            "shortcut_concern": "none",
            "minor_pattern_group": None,
        })
    return {
        "review_metadata": {"blind": True, "reviewer_type": "agent"},
        "reviews": reviews,
    }


def test_semantic_review_aggregate_has_no_row_details(tmp_path):
    path = tmp_path / "review.json"
    path.write_text(json.dumps(_semantic_payload()))
    result = audit._aggregate_semantic_review(path, 20)
    assert result["semantic_gate_pass"] is True
    assert result["human_certified"] is False
    assert result["reviewed_pairs"] == 20
    assert "reviews" not in result
    assert "review_index" not in json.dumps(result)

    path.write_text(json.dumps(_semantic_payload(reversed_index=7)))
    result = audit._aggregate_semantic_review(path, 20)
    assert result["semantic_gate_pass"] is False
    assert result["counts"]["certainty_ordering"]["reversed"] == 1


def test_cli_failure_message_is_fixed_and_text_free(tmp_path, capsys):
    missing = tmp_path / "missing.json"
    rc = audit.main(["--config", str(missing)])
    captured = capsys.readouterr()
    assert rc == 2
    assert captured.out == ""
    assert json.loads(captured.err) == {
        "error": "canary_audit_failed",
        "private_content_emitted": False,
    }
