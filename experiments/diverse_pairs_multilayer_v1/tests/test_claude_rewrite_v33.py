from __future__ import annotations

import json
from pathlib import Path

from experiments.diverse_pairs_multilayer_v1.src import (
    run_claude_rewrite_batches_v33 as runner,
)


def _row(index: int, topology: str = "early") -> dict:
    response = f"The result is {index}. This explanation preserves the supplied condition."
    return {
        "source_id": f"source-{index}",
        "prompt": f"What is result {index}?",
        "original_response": response,
        "original_response_sha256": runner.base.sha256_text(response),
        "rewrite_output_order": "confident_first",
        "target_longer_member": "confident",
        "rewrite_recipe": "A",
        "stance_topology": topology,
        "source_suitability_status": "passed_automated_prefilter_not_human_certified",
        "dataset": "fixture",
        "task": "factual_explanation",
        "length_bin": "short",
    }


def test_prompt_contains_invariance_rewrite_and_per_row_topology():
    rows = tuple(_row(i, topology) for i, topology in enumerate(
        ("early", "middle", "late", "distributed"), 1
    ))
    batch = runner.base.RewriteBatch("fixture", "train", "A", rows)
    prompt = runner.build_prompt(batch)
    assert "CONTENT INVARIANCE" in prompt
    assert "REAL REWRITES" in prompt
    assert "speaker's commitment to the answer as a whole" in prompt
    for topology in runner.TOPOLOGY_INSTRUCTIONS:
        assert f'"stance_topology": "{topology}"' in prompt


def test_frozen_input_rejects_changed_bytes(tmp_path: Path):
    rows = [_row(1)]
    source = tmp_path / "source.jsonl"
    source.write_text(json.dumps(rows[0]) + "\n", encoding="utf-8")
    manifest = {
        "protocol_version": runner.PROTOCOL_VERSION,
        "contains_source_text": False,
        "file_sha256": runner.base.sha256_file(source),
        "source_count": 1,
        "source_ids_sha256": runner.base.source_ids_sha256(rows),
        "dataset_counts": {"fixture": 1},
        "task_counts": {"factual_explanation": 1},
        "length_counts": {"short": 1},
        "stance_topology_counts": {"early": 1},
        "rewrite_output_order_counts": {"confident_first": 1},
        "target_longer_member_counts": {"confident": 1},
        "rewrite_recipe_counts": {"A": 1},
    }
    freeze = tmp_path / "freeze.json"
    freeze.write_text(json.dumps(manifest), encoding="utf-8")
    loaded, _ = runner.validate_frozen_input(source, freeze, 1)
    assert loaded == rows
    source.write_text(source.read_text() + "\n", encoding="utf-8")
    try:
        runner.validate_frozen_input(source, freeze, 1)
    except ValueError as exc:
        assert "does not match its freeze" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("changed bytes were accepted")


def test_local_helpers_detect_copy_and_duplicate_paragraph():
    original = "One two three four five six seven eight nine ten."
    assert runner._replacement_fraction(original, original) == 0.0
    assert runner._duplicate_paragraph("A useful paragraph here.\n\nA useful paragraph here.")
