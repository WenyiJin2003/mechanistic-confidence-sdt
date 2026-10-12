from __future__ import annotations

from experiments.diverse_pairs_multilayer_v1.src import (
    run_claude_component_rewrite_v35 as runner,
)


def test_component_rendering_keeps_shared_content_identical():
    template = "The calculation gives <STANCE_1> seven under the stated condition."
    confident = runner._replace_cues(template, ["a clear answer of"])
    hedged = runner._replace_cues(template, ["what appears to be"])
    assert confident.replace("a clear answer of", "") == hedged.replace("what appears to be", "")


def test_topology_boundaries():
    assert runner._topology_ok("early", [0.1])
    assert runner._topology_ok("middle", [0.5])
    assert runner._topology_ok("late", [0.9])
    assert runner._topology_ok("distributed", [0.2, 0.8])
    assert not runner._topology_ok("late", [0.2])


def test_prompt_forbids_facts_inside_cues():
    row = {
        "source_id": "source-1", "original_response_sha256": "0" * 64,
        "target_longer_member": "confident", "stance_topology": "early",
        "rewrite_recipe": "A", "prompt": "Question", "original_response": "Answer",
        "task": "factual_explanation",
    }
    prompt = runner.build_prompt((row,))
    assert "Do not write two full responses" in prompt
    assert "carries no answer fact" in prompt
    assert "object-level" in prompt
