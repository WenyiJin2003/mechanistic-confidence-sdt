import pytest

from experiments.diverse_pairs_multilayer_v1.src import (
    run_gemini_rewrite_smoke_v32g as runner,
)


def test_repeated_identical_fenced_json_is_accepted() -> None:
    response = (
        '```json\n{"pairs": []}\n```\n'
        '```json\n{"pairs": []}\n```'
    )
    assert runner._response_json(response) == {"pairs": []}


def test_conflicting_repeated_json_fails_closed() -> None:
    response = (
        '```json\n{"pairs": []}\n```\n'
        '```json\n{"pairs": [{"x": 1}]}\n```'
    )
    with pytest.raises(ValueError, match="conflicting"):
        runner._response_json(response)


def test_text_only_agent_has_no_tools() -> None:
    text = runner.AGENT_FILE.read_text(encoding="utf-8")
    assert "tools: []" in text
    assert "commandExecutionPolicy: off" in text
