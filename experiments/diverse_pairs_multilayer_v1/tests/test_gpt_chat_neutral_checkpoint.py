from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

import pytest

from experiments.diverse_pairs_multilayer_v1.src import (
    gpt_chat_neutral_checkpoint as checkpoint,
)


def _source(index: int) -> dict[str, Any]:
    response = (
        f"Synthetic response {index} contains enough neutral words for an "
        "isolated checkpoint unit test."
    )
    return {
        "pool_id": f"M{index:04d}",
        "source_id": f"source-{index:04d}",
        "pool_partition": "main",
        "split": "train",
        "dataset": "synthetic",
        "task": "factual",
        "length_bin": "short",
        "target_longer_member": "confident" if index % 2 == 0 else "hedged",
        "rewrite_family": "sentence_restructure",
        "rewrite_output_order": (
            "confident_first" if index % 2 == 0 else "hedged_first"
        ),
        "prompt": f"Synthetic prompt {index}",
        "original_response": response,
        "original_response_sha256": checkpoint.transport.sha256_text(response),
        "protected_spans": [],
        "human_review": "pending",
    }


def _source_pool() -> list[dict[str, Any]]:
    rows = [_source(index) for index in range(1, 701)]
    # M0042 replaces selected M0121 and must preserve its frozen stratum.
    for field in (
        "dataset",
        "task",
        "length_bin",
        "target_longer_member",
        "rewrite_family",
        "rewrite_output_order",
    ):
        rows[41][field] = rows[120][field]
    return rows


def _cue_bank() -> tuple[dict[str, Any], ...]:
    topologies = {
        "confident": ("early", "middle", "late", "distributed", "distributed"),
        "hedged": ("early", "middle", "middle", "late", "distributed"),
    }
    result = []
    for target, values in topologies.items():
        for index, topology in enumerate(values, 1):
            cue_count = 2 if topology == "distributed" else 1
            result.append(
                {
                    "cue_set_id": f"{target}-{index}",
                    "target_longer_member": target,
                    "stance_topology": topology,
                    "confident_cues": ["I am confident."] * cue_count,
                    "hedged_cues": ["I may be mistaken."] * cue_count,
                }
            )
    return tuple(result)


def _selection_config() -> dict[str, Any]:
    return {
        "source_pool_path": "unused-in-isolated-test.jsonl",
        "selection_start_zero_based": 1,
        "selection_stride": 7,
        "source_count": 100,
        "source_replacements": [
            {
                "selected_pool_id": "M0121",
                "replacement_pool_id": "M0042",
                "reason": "isolated test replacement",
            }
        ],
    }


def _selected_sources(monkeypatch: pytest.MonkeyPatch) -> list[dict[str, Any]]:
    monkeypatch.setattr(
        checkpoint.transport, "read_jsonl", lambda _path: _source_pool()
    )
    return checkpoint.select_sources(_selection_config())


def test_frozen_selection_and_cue_balance(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sources = _selected_sources(monkeypatch)
    assert len(sources) == 100
    assert sources[0]["pool_id"] == "M0002"
    assert sources[-1]["pool_id"] == "M0695"
    assert sources[17]["pool_id"] == "M0042"
    assert sources[17]["replacement_lineage"]["selected_pool_id"] == "M0121"
    assert {row["split"] for row in sources} == {"train"}
    assert len({row["source_id"] for row in sources}) == 100

    rows = checkpoint.assign_cues(sources, _cue_bank())
    assert Counter(row["target_longer_member"] for row in rows) == {
        "confident": 50,
        "hedged": 50,
    }
    assert Counter(row["rewrite_output_order"] for row in rows) == {
        "confident_first": 50,
        "hedged_first": 50,
    }
    assert set(Counter(row["cue_set_id"] for row in rows).values()) == {10}
    assert Counter(row["stance_topology"] for row in rows) == {
        "distributed": 30,
        "early": 20,
        "late": 20,
        "middle": 30,
    }


def test_prompt_is_twenty_records_and_contains_no_local_cues(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    rows = checkpoint.assign_cues(_selected_sources(monkeypatch), _cue_bank())[:20]
    cues = checkpoint.assigned_cues(rows, _cue_bank())
    prompt = checkpoint.v37.build_prompt(rows, cues)
    assert prompt.count('"source_id"') == 20
    assert "Overall, I stand firmly and fully behind this answer." not in prompt
    assert "Do not generate, suggest, quote, or evaluate any confident" in prompt


def test_public_manifest_is_text_free_after_isolated_prepare(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output_dir = tmp_path / "private-output"
    public_path = tmp_path / "public-manifest.json"
    config = {
        **_selection_config(),
        "chat_surface": "ordinary_chat",
        "model_family_requested": "test-model",
        "source_pool_sha256": "test-source-pool-hash",
        "output_dir": str(output_dir),
        "public_manifest_path": str(public_path),
        "cue_bank_sha256": "test-cue-bank-hash",
        "batch_size": 20,
        "transport_chunk_size": 10,
    }
    monkeypatch.setattr(checkpoint, "load_config", lambda _path: config)
    monkeypatch.setattr(checkpoint, "_cue_bank", lambda _config: _cue_bank())
    monkeypatch.setattr(
        checkpoint.transport, "read_jsonl", lambda _path: _source_pool()
    )
    monkeypatch.setattr(
        checkpoint.transport, "ensure_private_output_dir", lambda path: path
    )

    manifest = checkpoint.prepare(tmp_path / "config.json")
    assert manifest["contains_source_or_response_text"] is False
    assert manifest["source_count"] == 100
    assert manifest["batch_count"] == 5
    assert manifest["transport_chunk_size"] == 10
    assert manifest["transport_chunk_count"] == 10
    assert manifest["source_review"].endswith("human_review_pending")
    text = public_path.read_text(encoding="utf-8")
    assert '"prompt"' not in text
    assert '"original_response"' not in text
    assert (output_dir / "prompts" / "batch_05_part_02.txt").is_file()


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def _repair_fixture(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    *,
    replacement_slots: list[str],
    replacement_source_ids: list[str],
) -> tuple[Path, Path]:
    output_dir = tmp_path / "private-output"
    rows = checkpoint.assign_cues(_source_pool()[:100], _cue_bank())
    source_path = output_dir / "SOURCE_BATCH_100.jsonl"
    source_path.parent.mkdir(parents=True, exist_ok=True)
    source_path.write_bytes(checkpoint._jsonl_bytes(rows))

    base_items = [
        {
            "source_id": row["source_id"],
            "original_response_sha256": row["original_response_sha256"],
            "shared_template": f"base template {index}\n<STANCE_1>",
            "not_applicable": False,
            "issues": [],
        }
        for index, row in enumerate(rows[:20], 1)
    ]
    rows_by_id = {str(row["source_id"]): row for row in rows[:20]}
    replacement_items = [
        {
            "source_id": source_id,
            "original_response_sha256": rows_by_id[source_id][
                "original_response_sha256"
            ],
            "shared_template": f"regenerated template {index}\n<STANCE_1>",
            "not_applicable": False,
            "issues": [],
        }
        for index, source_id in enumerate(replacement_source_ids, 1)
    ]
    base_path = output_dir / "raw" / "base.json"
    replacement_path = output_dir / "raw" / "replacement.json"
    final_path = output_dir / "raw" / "final.json"
    _write_json(base_path, {"templates": base_items})
    _write_json(replacement_path, {"templates": replacement_items})

    first_template = base_items[0]["shared_template"]
    spec = {
        "protocol_version": "gpt56-chat-batch-repairs-v1",
        "batch_number": 1,
        "base_response_path": str(base_path),
        "base_response_sha256": checkpoint.transport.sha256_file(base_path),
        "replacement_response_path": str(replacement_path),
        "replacement_response_sha256": checkpoint.transport.sha256_file(
            replacement_path
        ),
        "replacement_slots": replacement_slots,
        "template_repairs": [
            {
                "production_slot": "G0001",
                "prior_template_sha256": checkpoint.transport.sha256_text(
                    first_template
                ),
                "reason": "isolated local repair",
                "template_replacements": [
                    {"old": "base", "new": "locally repaired"}
                ],
            }
        ],
        "output_path": str(final_path),
    }
    spec_path = tmp_path / "repair-spec.json"
    _write_json(spec_path, spec)
    config = {"output_dir": str(output_dir), "batch_size": 20}
    monkeypatch.setattr(checkpoint, "load_config", lambda _path: config)
    monkeypatch.setattr(
        checkpoint.transport, "ensure_private_output_dir", lambda path: path
    )
    return spec_path, final_path


def test_repair_preserves_lineage_and_counts_model_regeneration(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    spec_path, final_path = _repair_fixture(
        tmp_path,
        monkeypatch,
        replacement_slots=["G0002", "G0004"],
        replacement_source_ids=["source-0002", "source-0004"],
    )
    result = checkpoint.apply_repair_spec(tmp_path / "config.json", spec_path)
    assert result["model_regenerated_templates"] == 2
    assert "source_replacements" not in result

    output = json.loads(final_path.read_text(encoding="utf-8"))
    assert output["templates"][0]["local_repair_lineage"] == {
        "protocol": checkpoint.local_repairs.PROTOCOL_VERSION,
        "prior_template_sha256": checkpoint.transport.sha256_text(
            "base template 1\n<STANCE_1>"
        ),
        "reason": "isolated local repair",
        "model_calls": 0,
    }
    assert [
        item["production_slot"]
        for item in output["repair_lineage"]["model_regenerated_templates"]
    ] == ["G0002", "G0004"]
    assert output["repair_lineage"]["local_template_repairs"][0][
        "production_slot"
    ] == "G0001"


@pytest.mark.parametrize(
    ("replacement_slots", "replacement_source_ids", "message"),
    [
        (["G0002", "G0002"], ["source-0002"], "Duplicate"),
        (["G9999"], ["source-0002"], "outside the batch"),
        (["G0002"], ["source-0003"], "must exactly match"),
        (["G0002"], ["source-0002", "source-0003"], "must exactly match"),
    ],
)
def test_repair_rejects_invalid_replacement_contract(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    replacement_slots: list[str],
    replacement_source_ids: list[str],
    message: str,
) -> None:
    spec_path, _ = _repair_fixture(
        tmp_path,
        monkeypatch,
        replacement_slots=replacement_slots,
        replacement_source_ids=replacement_source_ids,
    )
    with pytest.raises(ValueError, match=message):
        checkpoint.apply_repair_spec(tmp_path / "config.json", spec_path)


def _finalize_fixture(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> tuple[Path, Path, Path]:
    output_dir = tmp_path / "private-output"
    summary_path = tmp_path / "public-summary.json"
    config_path = tmp_path / "config.json"
    _write_json(config_path, {})
    selected = _source_pool()[:100]
    rows = checkpoint.assign_cues(selected, _cue_bank())
    source_path = output_dir / "SOURCE_BATCH_100.jsonl"
    source_path.parent.mkdir(parents=True, exist_ok=True)
    source_path.write_bytes(checkpoint._jsonl_bytes(rows))
    config = {
        "output_dir": str(output_dir),
        "source_count": 100,
        "batch_size": 20,
        "transport_chunk_size": 10,
        "chat_surface": "ordinary_chat",
        "model_family_requested": "test-model",
        "cue_bank_sha256": "a" * 64,
        "source_replacements": [
            {"selected_pool_id": "M0001", "replacement_pool_id": "M0701"},
            {"selected_pool_id": "M0002", "replacement_pool_id": "M0702"},
        ],
    }
    monkeypatch.setattr(checkpoint, "load_config", lambda _path: config)
    monkeypatch.setattr(checkpoint, "_cue_bank", lambda _config: _cue_bank())
    monkeypatch.setattr(
        checkpoint, "select_sources", lambda _config: list(selected)
    )
    monkeypatch.setattr(
        checkpoint.transport, "ensure_private_output_dir", lambda path: path
    )
    monkeypatch.setattr(checkpoint, "SUMMARY_MANIFEST", summary_path)

    for batch_number in range(1, 6):
        start = (batch_number - 1) * 20
        batch_rows = rows[start : start + 20]
        templates = [
            {
                "source_id": row["source_id"],
                "original_response_sha256": row["original_response_sha256"],
                "shared_template": (
                    f"neutral template for {row['production_slot']}\n<STANCE_1>"
                ),
                "not_applicable": False,
                "issues": [],
            }
            for row in batch_rows
        ]
        lineage: dict[str, Any] = {
            "model_regenerated_templates": [],
            "local_template_repairs": [],
        }
        if batch_number == 1:
            by_slot = {str(row["production_slot"]): row for row in batch_rows}
            lineage = {
                "model_regenerated_templates": [
                    {
                        "production_slot": slot,
                        "source_id": by_slot[slot]["source_id"],
                    }
                    for slot in ("G0001", "G0002")
                ],
                "local_template_repairs": [
                    {
                        "production_slot": slot,
                        "source_id": by_slot[slot]["source_id"],
                    }
                    for slot in ("G0002", "G0003")
                ],
            }
        raw_path = output_dir / "raw" / f"batch_{batch_number:02d}_final.json"
        _write_json(
            raw_path,
            {"templates": templates, "repair_lineage": lineage},
        )
        records = [
            {
                "source_id": row["source_id"],
                "original_response_sha256": row["original_response_sha256"],
                "production_slot": row["production_slot"],
                "shared_template": template["shared_template"],
                "status": "accepted",
            }
            for row, template in zip(batch_rows, templates)
        ]
        _write_json(
            output_dir / "parsed" / f"batch_{batch_number:02d}.json",
            {
                "protocol_version": checkpoint.PROTOCOL_VERSION,
                "batch_number": batch_number,
                "source_ids": [row["source_id"] for row in batch_rows],
                "raw_response_sha256": checkpoint.transport.sha256_file(raw_path),
                "records": records,
                "records_sha256": checkpoint.transport.sha256_bytes(
                    json.dumps(records, sort_keys=True).encode("utf-8")
                ),
                "status_counts": {"accepted": 20},
            },
        )
    return config_path, output_dir, summary_path


def test_finalize_combines_only_accepted_batches_and_counts_overlap_once(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config_path, output_dir, summary_path = _finalize_fixture(
        tmp_path, monkeypatch
    )
    manifest = checkpoint.finalize(config_path)

    assert manifest["final_mechanical_counts"] == {"accepted": 100}
    assert manifest["repair_counts"] == {
        "records_without_recorded_repair": 97,
        "model_regenerated_templates": 2,
        "local_template_repairs": 2,
        "repaired_unique_records": 3,
        "records_with_both_model_and_local_repair": 1,
        "source_pool_replacements": 2,
    }
    assert manifest["per_batch"][0]["records_without_recorded_repair"] == 17
    assert manifest["per_batch"][0][
        "records_with_both_model_and_local_repair"
    ] == 1
    assert manifest["initial_mechanical_counts_available"] is False
    private_final = json.loads(
        (output_dir / "FINAL_100.json").read_text(encoding="utf-8")
    )
    assert len(private_final["records"]) == 100
    assert private_final["semantic_review"] == "pending"
    assert private_final["human_review"] == "pending"
    public_text = summary_path.read_text(encoding="utf-8")
    assert "neutral template" not in public_text
    assert '"prompt"' not in public_text
    assert '"shared_template"' not in public_text
    assert manifest["decision"].endswith("not_validated_training_data")


@pytest.mark.parametrize("failure", ["missing_final", "rejected_record"])
def test_finalize_refuses_incomplete_or_unaccepted_checkpoint(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    failure: str,
) -> None:
    config_path, output_dir, summary_path = _finalize_fixture(
        tmp_path, monkeypatch
    )
    if failure == "missing_final":
        (output_dir / "raw" / "batch_05_final.json").unlink()
        expected = FileNotFoundError
    else:
        parsed_path = output_dir / "parsed" / "batch_03.json"
        parsed = json.loads(parsed_path.read_text(encoding="utf-8"))
        parsed["records"][0]["status"] = "validation_failed"
        parsed["records_sha256"] = checkpoint.transport.sha256_bytes(
            json.dumps(parsed["records"], sort_keys=True).encode("utf-8")
        )
        parsed["status_counts"] = {"accepted": 19, "validation_failed": 1}
        _write_json(parsed_path, parsed)
        expected = ValueError

    with pytest.raises(expected):
        checkpoint.finalize(config_path)
    assert not (output_dir / "FINAL_100.json").exists()
    assert not summary_path.exists()


def test_public_summary_guard_rejects_per_example_text() -> None:
    with pytest.raises(ValueError, match="forbidden text field"):
        checkpoint._assert_public_summary_text_free(
            {
                "contains_source_or_response_text": False,
                "nested": {"prompt": "private prompt"},
            }
        )
