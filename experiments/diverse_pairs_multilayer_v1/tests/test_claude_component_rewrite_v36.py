from __future__ import annotations

from experiments.diverse_pairs_multilayer_v1.src import (
    run_claude_component_rewrite_v36 as runner,
)


def test_prompt_requires_standalone_global_sentences_and_preserves_modality():
    row = {
        "source_id": "source-1",
        "original_response_sha256": "0" * 64,
        "target_longer_member": "confident",
        "stance_topology": "early",
        "rewrite_recipe": "A",
        "prompt": "Question",
        "original_response": "The value may vary.",
        "task": "factual_explanation",
    }
    prompt = runner.build_prompt((row,))
    assert "line by itself" in prompt
    assert "complete sentence of at most 14 words" in prompt
    assert "explicitly refer to the whole answer" in prompt
    assert "preserve every object-level uncertainty" in prompt
    assert "Never turn a qualified claim into a certain one" in prompt


def test_standalone_marker_check_rejects_inline_marker():
    assert runner._standalone_marker("Before\n<STANCE_1>\nAfter", "<STANCE_1>")
    assert not runner._standalone_marker(
        "Before <STANCE_1> after", "<STANCE_1>"
    )
    assert not runner._standalone_marker(
        "Before\n <STANCE_1>\nAfter", "<STANCE_1>"
    )


def test_complete_sentence_and_global_scope_checks():
    cue = "Overall, I remain confident in this answer."
    assert runner._complete_cue_sentence(cue)
    assert runner._cue_has_global_scope(cue)
    assert not runner._complete_cue_sentence("overall I remain confident")
    assert not runner._cue_has_global_scope("I am entirely certain.")


def test_config_freezes_only_the_second_ten_source_batch():
    config = runner.load_config(runner.DEFAULT_CONFIG)
    batch = runner.load_frozen_batch(config)
    assert len(batch) == 10
    assert config.frozen_batch_number == 2
    assert (
        runner.transport.source_ids_sha256(batch)
        == config.expected_batch_source_ids_sha256
    )
