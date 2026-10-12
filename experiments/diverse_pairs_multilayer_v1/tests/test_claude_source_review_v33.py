from __future__ import annotations

from experiments.diverse_pairs_multilayer_v1.src import (
    run_claude_source_review_v33 as review,
)


def _row(index: int) -> dict:
    return {
        "production_slot": f"P{index:04d}",
        "source_id": f"source-{index}",
        "original_response_sha256": f"{index:064x}",
        "task": "factual_explanation",
        "prompt": "Explain the result.",
        "original_response": "A complete, ordinary explanation.",
    }


def test_batches_are_fixed_by_production_slot():
    rows = [_row(index) for index in range(1, 81)]
    batches = review.make_batches(list(reversed(rows)), 40)
    assert len(batches) == 2
    assert batches[0][0]["production_slot"] == "P0001"
    assert batches[1][-1]["production_slot"] == "P0080"


def test_prompt_is_source_only_and_conservative():
    batch = (_row(1),)
    prompt = review.build_prompt(batch)
    assert "Do not rewrite it" in prompt
    assert "obvious math/reasoning error" in prompt
    assert "speaker's commitment" in prompt


def test_validation_requires_exact_order_and_positive_code():
    batch = (_row(1),)
    structured = {"reviews": [{
        "source_id": "source-1",
        "original_response_sha256": f"{1:064x}",
        "decision": "eligible",
        "reason_codes": ["safe_coherent_self_contained"],
        "brief_reason": "Coherent and suitable for a meaning-preserving rewrite.",
    }]}
    records = review.validate_output(batch, structured)
    assert records[0]["decision"] == "eligible"
