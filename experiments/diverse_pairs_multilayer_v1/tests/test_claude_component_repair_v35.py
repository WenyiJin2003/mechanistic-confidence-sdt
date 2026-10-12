from __future__ import annotations

from experiments.diverse_pairs_multilayer_v1.src import (
    run_claude_component_repair_v35 as repair,
)


def test_repair_set_is_frozen_to_five_slots():
    assert tuple(repair.REPAIR_INSTRUCTIONS) == (
        "P0007", "P0016", "P0072", "P0082", "P0158"
    )


def test_repair_prompt_targets_global_confidence_not_answer_content():
    source = {
        "source_id": "source-1",
        "original_response_sha256": "0" * 64,
        "production_slot": "P0007",
        "stance_topology": "late",
        "target_longer_member": "confident",
        "prompt": "Question",
        "original_response": "Answer with a qualification.",
    }
    record = {
        "shared_template": "Answer <STANCE_1>",
        "confident_cues": ["clearly"],
        "hedged_cues": ["perhaps"],
        "validation_issues": ["target_length_direction_not_met"],
    }
    prompt = repair.build_prompt((source,), {"P0007": record})
    assert "speaker's global commitment" in prompt
    assert "Never correct, verify, add, omit, or strengthen object-level content" in prompt
    assert "Cue-only repair" in prompt


def test_merge_preserves_batch_order_and_marks_lineage():
    batch = (
        {"production_slot": "P0001"},
        {"production_slot": "P0007"},
    )
    base = {
        "P0001": {"production_slot": "P0001", "status": "accepted"},
        "P0007": {"production_slot": "P0007", "status": "validation_failed"},
    }
    repaired = [{"production_slot": "P0007", "status": "accepted"}]
    merged = repair.merge_records(batch, base, repaired)
    assert [record["production_slot"] for record in merged] == ["P0001", "P0007"]
    assert not merged[0]["repair_lineage"]["replaced_original_v35_components"]
    assert merged[1]["repair_lineage"]["replaced_original_v35_components"]
