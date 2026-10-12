from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from experiments.diverse_pairs_multilayer_v1.src import (
    run_claude_two_stage_rewrite_v37 as runner,
)


class WordTokenizer:
    def __call__(self, text, add_special_tokens=False):
        return {"input_ids": text.split()}

    def apply_chat_template(self, messages, tokenize=True):
        return " ".join(message["content"] for message in messages).split()


def test_frozen_input_and_public_cue_bank_are_aligned():
    config = runner.load_config(runner.DEFAULT_CONFIG)
    rows = runner.load_frozen_sources(config)
    cues = runner.load_cue_bank(config, rows)
    assert len(rows) == len(cues) == 10
    assert len({row["source_id"] for row in rows}) == 10
    assert [item["stance_topology"] for item in cues] == [
        row["stance_topology"] for row in rows
    ]
    assert [item["target_longer_member"] for item in cues] == [
        row["target_longer_member"] for row in rows
    ]


def test_prompt_requests_only_neutral_templates_and_schema_has_no_cues():
    config = runner.load_config(runner.DEFAULT_CONFIG)
    rows = runner.load_frozen_sources(config)
    cues = runner.load_cue_bank(config, rows)
    prompt = runner.build_prompt(rows, cues)
    schema = json.dumps(runner.output_schema(rows), sort_keys=True)
    assert "return ONLY one neutral shared paraphrase" in prompt
    assert "Do not generate, suggest, quote, or evaluate any confident" in prompt
    assert "at least 8% meaningful lexical change" in prompt
    assert "on a line by itself" in prompt
    assert "confident_cues" not in schema
    assert "hedged_cues" not in schema


def test_local_rendering_reuses_v35_checks_and_keeps_content_locked():
    source = {
        "source_id": "source-1",
        "original_response_sha256": runner.transport.sha256_text(
            "the method reviews all available options before comparing their likely "
            "consequences. it then chooses the option that best satisfies the stated "
            "objective while keeping the relevant constraints, tradeoffs, and "
            "assumptions visible throughout the decision process."
        ),
        "original_response": (
            "the method reviews all available options before comparing their likely "
            "consequences. it then chooses the option that best satisfies the stated "
            "objective while keeping the relevant constraints, tradeoffs, and "
            "assumptions visible throughout the decision process."
        ),
        "prompt": "explain the method",
        "production_slot": "PTEST",
        "rewrite_recipe": "A",
        "stance_topology": "early",
        "rewrite_output_order": "confident_first",
        "target_longer_member": "hedged",
        "task": "factual_explanation",
    }
    cues = {
        "cue_set_id": "test-cue",
        "stance_topology": "early",
        "target_longer_member": "hedged",
        "confident_cues": ["Overall, this answer is solid."],
        "hedged_cues": [
            "Overall, I endorse this answer, though I retain some uncertainty."
        ],
    }
    template = (
        "<STANCE_1>\nBefore choosing, the approach surveys every available "
        "alternative and weighs its likely consequences. It selects the alternative "
        "that most closely fulfills the stated objective while leaving the applicable "
        "constraints, tradeoffs, and assumptions explicit throughout the reasoning."
    )
    structured = {
        "templates": [
            {
                "source_id": source["source_id"],
                "original_response_sha256": source["original_response_sha256"],
                "shared_template": template,
                "not_applicable": False,
                "issues": [],
            }
        ]
    }
    config = SimpleNamespace(
        min_word_ratio=0.5,
        max_word_ratio=2.0,
        minimum_source_edit_fraction=0.08,
    )
    records, corrected = runner.validate_output(
        (source,), (cues,), structured, config, WordTokenizer()
    )
    assert corrected == []
    record = records[0]
    assert record["status"] == "accepted"
    confident = record["confident_response"]
    hedged = record["hedged_response"]
    assert confident.replace(cues["confident_cues"][0], "") == hedged.replace(
        cues["hedged_cues"][0], ""
    )
    assert "insufficient_replacement_fraction" not in " ".join(
        record["validation_issues"]
    )
    assert record["cue_set_id"] == "test-cue"


def test_local_rendering_rejects_inline_marker():
    source = {
        "source_id": "source-1",
        "original_response_sha256": runner.transport.sha256_text(
            "a sufficiently long neutral response with several words for testing"
        ),
        "original_response": (
            "a sufficiently long neutral response with several words for testing"
        ),
        "prompt": "question",
        "production_slot": "PTEST",
        "rewrite_recipe": "A",
        "stance_topology": "early",
        "rewrite_output_order": "confident_first",
        "target_longer_member": "hedged",
        "task": "factual_explanation",
    }
    cues = {
        "cue_set_id": "test-cue",
        "stance_topology": "early",
        "target_longer_member": "hedged",
        "confident_cues": ["Overall, this answer is solid."],
        "hedged_cues": [
            "Overall, I endorse this answer, though I retain some uncertainty."
        ],
    }
    structured = {
        "templates": [
            {
                "source_id": source["source_id"],
                "original_response_sha256": source["original_response_sha256"],
                "shared_template": (
                    "<STANCE_1> a substantially reworded neutral response with "
                    "several different terms for this validation test"
                ),
                "not_applicable": False,
                "issues": [],
            }
        ]
    }
    config = SimpleNamespace(
        min_word_ratio=0.25,
        max_word_ratio=3.0,
        minimum_source_edit_fraction=0.08,
    )
    records, _ = runner.validate_output(
        (source,), (cues,), structured, config, WordTokenizer()
    )
    assert records[0]["status"] == "validation_failed"
    assert "placeholder_1_not_standalone_line" in records[0][
        "validation_issues"
    ]


def test_eight_percent_edit_floor_applies_to_neutral_template_not_cues():
    original = (
        "this neutral source answer contains enough ordinary words to show that "
        "adding only a confidence sentence is not a genuine paraphrase"
    )
    source = {
        "source_id": "source-1",
        "original_response_sha256": runner.transport.sha256_text(original),
        "original_response": original,
        "prompt": "question",
        "production_slot": "PTEST",
        "rewrite_recipe": "A",
        "stance_topology": "late",
        "rewrite_output_order": "confident_first",
        "target_longer_member": "hedged",
        "task": "factual_explanation",
    }
    cues = {
        "cue_set_id": "test-cue",
        "stance_topology": "late",
        "target_longer_member": "hedged",
        "confident_cues": ["Overall, this answer is solid."],
        "hedged_cues": [
            "Overall, I endorse this answer, though I retain some uncertainty."
        ],
    }
    structured = {
        "templates": [
            {
                "source_id": "source-1",
                "original_response_sha256": source["original_response_sha256"],
                "shared_template": original + "\n<STANCE_1>",
                "not_applicable": False,
                "issues": [],
            }
        ]
    }
    config = SimpleNamespace(
        min_word_ratio=0.5,
        max_word_ratio=2.0,
        minimum_source_edit_fraction=0.08,
    )
    records, _ = runner.validate_output(
        (source,), (cues,), structured, config, WordTokenizer()
    )
    assert records[0]["status"] == "validation_failed"
    assert "shared_template:insufficient_replacement_fraction" in records[0][
        "validation_issues"
    ]


def test_cached_record_hash_is_verified(tmp_path):
    path = tmp_path / "parsed.json"
    payload = {
        "generation_fingerprint": "frozen",
        "source_ids": ["source-1"],
        "records": [{"source_id": "source-1"}],
        "records_sha256": "0" * 64,
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="cached record bytes changed"):
        runner._load_parsed(
            path,
            "frozen",
            [{"source_id": "source-1", "original_response_sha256": "1" * 64}],
        )


def test_dry_run_never_executes_claude(monkeypatch, capsys):
    monkeypatch.setattr(
        runner,
        "run_one",
        lambda *args, **kwargs: pytest.fail("dry run called Claude execution path"),
    )
    assert runner.main(["--config", str(runner.DEFAULT_CONFIG)]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["execute"] is False
    assert output["planned_claude_calls"] == 1
    assert output["claude_outputs_cues"] is False
