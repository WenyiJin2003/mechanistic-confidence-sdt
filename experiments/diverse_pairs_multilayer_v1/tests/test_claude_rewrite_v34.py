from __future__ import annotations

from experiments.diverse_pairs_multilayer_v1.src import (
    run_claude_rewrite_batches_v34 as runner,
)


def _row(index: int, recipe: str, topology: str) -> dict:
    response = f"The result is {index}. It may vary under the stated condition."
    return {
        "source_id": f"source-{index}",
        "prompt": "Explain the result.",
        "original_response": response,
        "original_response_sha256": runner.base.sha256_text(response),
        "rewrite_output_order": "confident_first",
        "target_longer_member": "confident",
        "rewrite_recipe": recipe,
        "stance_topology": topology,
    }


def test_prompt_requires_shared_parallel_base_and_modal_lock():
    rows = tuple(
        _row(index, "A", topology)
        for index, topology in enumerate(("early", "middle", "late", "distributed"), 1)
    )
    batch = runner.base.RewriteBatch("fixture", "train", "A", rows)
    prompt = runner.build_prompt(batch)
    assert "SHARED-BASE METHOD" in prompt
    assert "object-level modality" in prompt
    assert "parallel" in prompt
    assert "one to eight words" in prompt


def test_pair_similarity_rewards_parallel_content():
    left = "The answer is 7 because the two values sum directly."
    close = "The answer appears to be 7 because the two values sum directly."
    far = "A completely unrelated discussion changes every substantive detail."
    assert runner._similarity(left, close) > runner._similarity(left, far)
