"""Prepare and validate a resumable ordinary-Chat neutral-paraphrase checkpoint.

The Chat model writes only a neutral shared template with stance markers.  A
frozen local cue bank then renders the confident and hedged responses, keeping
all non-cue text identical.  Source text and model output remain under the
ignored ``private_data`` tree; the public manifest contains only hashes and
aggregate counts.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Sequence

if __package__ in {None, ""}:  # pragma: no cover
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from experiments.diverse_pairs_multilayer_v1.src import (
    run_claude_rewrite_batches as transport,
)
from experiments.diverse_pairs_multilayer_v1.src import (
    run_claude_two_stage_rewrite_v37 as v37,
)
from experiments.diverse_pairs_multilayer_v1.src import (
    apply_local_template_repairs_v37 as local_repairs,
)


BASE = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = BASE / "configs" / "gpt56_chat_neutral_100_v37.json"
SUMMARY_MANIFEST = BASE / "manifests" / "gpt56_chat_neutral_100_v37_summary.json"
PROTOCOL_VERSION = "gpt56-ordinary-chat-neutral-paraphrase-v3.7"


def _resolve(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else BASE / path


def load_config(path: Path) -> dict[str, Any]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if raw.get("protocol_version") != PROTOCOL_VERSION:
        raise ValueError("Wrong ordinary-Chat checkpoint protocol")
    if raw.get("chat_surface") != "ordinary_chat":
        raise ValueError("Checkpoint must use ordinary Chat")
    if int(raw.get("source_count", 0)) != 100:
        raise ValueError("This checkpoint is frozen to 100 sources")
    if int(raw.get("batch_size", 0)) != 20:
        raise ValueError("This checkpoint is frozen to five batches of 20")
    if int(raw.get("transport_chunk_size", 0)) != 10:
        raise ValueError("Ordinary-Chat transport is frozen to ten records per message")
    if int(raw.get("selection_start_zero_based", -1)) != 1:
        raise ValueError("Frozen selection must begin at M0002")
    if int(raw.get("selection_stride", 0)) != 7:
        raise ValueError("Frozen selection stride must remain seven")
    source_pool_path = _resolve(str(raw["source_pool_path"]))
    if transport.sha256_file(source_pool_path) != raw.get("source_pool_sha256"):
        raise ValueError("Frozen source pool changed")
    for field in (
        "selected_source_ids_sha256",
        "selected_response_hashes_sha256",
    ):
        if not isinstance(raw.get(field), str) or len(raw[field]) != 64:
            raise ValueError(f"Missing frozen {field}")
    cue_path = _resolve(str(raw["cue_bank_path"]))
    if transport.sha256_file(cue_path) != raw.get("cue_bank_sha256"):
        raise ValueError("Frozen v3.7 cue bank changed")
    return raw


def _cue_bank(config: dict[str, Any]) -> tuple[dict[str, Any], ...]:
    value = json.loads(
        _resolve(str(config["cue_bank_path"])).read_text(encoding="utf-8")
    )
    if value.get("protocol_version") != v37.CUE_BANK_PROTOCOL:
        raise ValueError("Wrong cue-bank protocol")
    cue_sets = value.get("cue_sets")
    if not isinstance(cue_sets, list) or len(cue_sets) != 10:
        raise ValueError("Expected the ten frozen v3.7 cue sets")
    return tuple(cue_sets)


def select_sources(config: dict[str, Any]) -> list[dict[str, Any]]:
    rows = transport.read_jsonl(_resolve(str(config["source_pool_path"])))
    train = [
        row
        for row in rows
        if row.get("pool_partition") == "main" and row.get("split") == "train"
    ]
    if len(train) != 700 or train[0].get("pool_id") != "M0001":
        raise ValueError("Frozen main/train source pool changed")
    start = int(config["selection_start_zero_based"])
    stride = int(config["selection_stride"])
    count = int(config["source_count"])
    selected = [dict(train[start + stride * index]) for index in range(count)]
    expected_last = start + stride * (count - 1)
    if selected[0].get("pool_id") != "M0002" or selected[-1].get("pool_id") != "M0695":
        raise ValueError("Frozen stride no longer selects M0002 through M0695")
    if expected_last >= len(train) or len({row["source_id"] for row in selected}) != count:
        raise ValueError("Invalid or duplicate frozen source selection")
    by_pool_id = {str(row["pool_id"]): row for row in train}
    replacements = config.get("source_replacements", [])
    for replacement in replacements:
        selected_pool_id = str(replacement["selected_pool_id"])
        replacement_pool_id = str(replacement["replacement_pool_id"])
        positions = [
            index
            for index, row in enumerate(selected)
            if row.get("pool_id") == selected_pool_id
        ]
        if len(positions) != 1 or replacement_pool_id not in by_pool_id:
            raise ValueError("Invalid frozen source replacement")
        if any(row.get("pool_id") == replacement_pool_id for row in selected):
            raise ValueError("Replacement source is already selected")
        prior = selected[positions[0]]
        new = dict(by_pool_id[replacement_pool_id])
        matched_fields = (
            "dataset",
            "task",
            "length_bin",
            "target_longer_member",
            "rewrite_family",
        )
        if any(prior[field] != new[field] for field in matched_fields):
            raise ValueError("Replacement does not preserve the frozen source stratum")
        new["replacement_lineage"] = {
            "selected_pool_id": selected_pool_id,
            "replacement_pool_id": replacement_pool_id,
            "reason": str(replacement["reason"]),
        }
        selected[positions[0]] = new
    if len({row["source_id"] for row in selected}) != count:
        raise ValueError("Source replacement introduced a duplicate")
    if config.get("selected_source_ids_sha256") and (
        transport.source_ids_sha256(selected)
        != config["selected_source_ids_sha256"]
    ):
        raise ValueError("Frozen selected source IDs changed")
    selected_response_hashes = transport.sha256_bytes(
        "\n".join(
            str(row["original_response_sha256"]) for row in selected
        ).encode("utf-8")
    )
    if config.get("selected_response_hashes_sha256") and (
        selected_response_hashes
        != config["selected_response_hashes_sha256"]
    ):
        raise ValueError("Frozen selected source responses changed")
    if any(row.get("human_review") not in {"pending", None} for row in selected):
        raise ValueError("Unexpected human-review state in source pool")
    return selected


def assign_cues(
    rows: Sequence[dict[str, Any]], cue_bank: Sequence[dict[str, Any]]
) -> list[dict[str, Any]]:
    by_target = {
        target: [item for item in cue_bank if item["target_longer_member"] == target]
        for target in ("confident", "hedged")
    }
    if any(len(items) != 5 for items in by_target.values()):
        raise ValueError("Cue bank must contain five families per length target")
    offsets = Counter()
    assigned: list[dict[str, Any]] = []
    for position, source in enumerate(rows, 1):
        target = str(source["target_longer_member"])
        cues = by_target[target][offsets[target] % len(by_target[target])]
        offsets[target] += 1
        row = dict(source)
        row.update(
            {
                "production_slot": f"G{position:04d}",
                "rewrite_recipe": str(source["rewrite_family"]),
                "stance_topology": str(cues["stance_topology"]),
                "cue_set_id": str(cues["cue_set_id"]),
                "ordinary_chat_source_review": "automated_only_human_pending",
            }
        )
        assigned.append(row)
    return assigned


def assigned_cues(
    rows: Sequence[dict[str, Any]], cue_bank: Sequence[dict[str, Any]]
) -> list[dict[str, Any]]:
    by_id = {str(item["cue_set_id"]): item for item in cue_bank}
    cues = [by_id[str(row["cue_set_id"])] for row in rows]
    for row, item in zip(rows, cues):
        if row["stance_topology"] != item["stance_topology"]:
            raise ValueError("Source/cue topology mismatch")
        if row["target_longer_member"] != item["target_longer_member"]:
            raise ValueError("Source/cue length target mismatch")
    return cues


def _jsonl_bytes(rows: Sequence[dict[str, Any]]) -> bytes:
    return "".join(
        json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows
    ).encode("utf-8")


def _counts(rows: Sequence[dict[str, Any]], field: str) -> dict[str, int]:
    return dict(sorted(Counter(str(row[field]) for row in rows).items()))


def prepare(config_path: Path) -> dict[str, Any]:
    config = load_config(config_path)
    output_dir = _resolve(str(config["output_dir"]))
    transport.ensure_private_output_dir(output_dir)
    source_path = output_dir / "SOURCE_BATCH_100.jsonl"
    prompt_dir = output_dir / "prompts"
    prompt_dir.mkdir(parents=True, exist_ok=True)

    cue_bank = _cue_bank(config)
    rows = assign_cues(select_sources(config), cue_bank)
    source_path.write_bytes(_jsonl_bytes(rows))
    cues = assigned_cues(rows, cue_bank)
    batch_size = int(config["batch_size"])
    transport_chunk_size = int(config["transport_chunk_size"])
    for start in range(0, len(rows), batch_size):
        batch_number = start // batch_size + 1
        batch_rows = rows[start : start + batch_size]
        batch_cues = cues[start : start + batch_size]
        (prompt_dir / f"batch_{batch_number:02d}.txt").write_text(
            v37.build_prompt(batch_rows, batch_cues), encoding="utf-8"
        )
        for chunk_start in range(0, batch_size, transport_chunk_size):
            chunk_number = chunk_start // transport_chunk_size + 1
            chunk_rows = batch_rows[
                chunk_start : chunk_start + transport_chunk_size
            ]
            chunk_cues = batch_cues[
                chunk_start : chunk_start + transport_chunk_size
            ]
            (prompt_dir / f"batch_{batch_number:02d}_part_{chunk_number:02d}.txt").write_text(
                v37.build_prompt(chunk_rows, chunk_cues), encoding="utf-8"
            )

    manifest = {
        "protocol_version": PROTOCOL_VERSION,
        "contains_source_or_response_text": False,
        "chat_surface": config["chat_surface"],
        "model_family_requested": config["model_family_requested"],
        "exact_model_slug": "unavailable_from_thread_interface",
        "source_count": len(rows),
        "batch_size": batch_size,
        "batch_count": len(rows) // batch_size,
        "transport_chunk_size": transport_chunk_size,
        "transport_chunk_count": len(rows) // transport_chunk_size,
        "transport_events": config.get("transport_events", {}),
        "transport_note": (
            "The first 20-record call completed but exceeded the thread read limit; "
            "later calls use ten records to avoid re-emitting completed output."
        ),
        "source_file_sha256": transport.sha256_file(source_path),
        "source_pool_sha256": config["source_pool_sha256"],
        "source_ids_sha256": transport.source_ids_sha256(rows),
        "source_response_hashes_sha256": transport.sha256_bytes(
            "\n".join(str(row["original_response_sha256"]) for row in rows).encode()
        ),
        "cue_bank_sha256": config["cue_bank_sha256"],
        "selection": {
            "partition": "main",
            "split": "train",
            "first_pool_id": rows[0]["pool_id"],
            "last_pool_id": rows[-1]["pool_id"],
            "zero_based_start": config["selection_start_zero_based"],
            "stride": config["selection_stride"],
            "replacements": config.get("source_replacements", []),
        },
        "counts": {
            field: _counts(rows, field)
            for field in (
                "dataset",
                "task",
                "length_bin",
                "rewrite_recipe",
                "rewrite_output_order",
                "target_longer_member",
                "stance_topology",
                "cue_set_id",
            )
        },
        "source_review": "automated_screening_only_human_review_pending",
        "semantic_review": "pending",
        "human_pair_review": "pending",
        "decision": "development_expansion_checkpoint_not_validated_training_data",
    }
    public_manifest = _resolve(str(config["public_manifest_path"]))
    transport.atomic_write_json(public_manifest, manifest)
    return manifest


def _decode_response(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8").strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```") and lines[-1].strip() == "```":
            text = "\n".join(lines[1:-1])
    value = json.loads(text)
    if not isinstance(value, dict):
        raise ValueError("Chat response must be one JSON object")
    return value


def validate_batch(
    config_path: Path, batch_number: int, response_path: Path
) -> dict[str, Any]:
    config = load_config(config_path)
    if batch_number < 1 or batch_number > 5:
        raise ValueError("Batch number must be 1 through 5")
    output_dir = _resolve(str(config["output_dir"]))
    source_path = output_dir / "SOURCE_BATCH_100.jsonl"
    if not source_path.exists():
        raise FileNotFoundError("Run prepare before validating Chat output")
    all_rows = transport.read_jsonl(source_path)
    batch_size = int(config["batch_size"])
    start = (batch_number - 1) * batch_size
    rows = all_rows[start : start + batch_size]
    cue_bank = _cue_bank(config)
    cues = assigned_cues(rows, cue_bank)
    structured = _decode_response(response_path)
    tokenizer = transport.load_pinned_tokenizer(transport.tokenizer_file_hashes())
    validator_config = SimpleNamespace(
        min_word_ratio=float(config["min_word_ratio"]),
        max_word_ratio=float(config["max_word_ratio"]),
        minimum_source_edit_fraction=float(config["minimum_source_edit_fraction"]),
    )
    records, corrected = v37.validate_output(
        rows, cues, structured, validator_config, tokenizer
    )
    parsed = {
        "protocol_version": PROTOCOL_VERSION,
        "batch_number": batch_number,
        "source_ids": [row["source_id"] for row in rows],
        "raw_response_sha256": transport.sha256_file(response_path),
        "hash_echo_correction_positions": corrected,
        "records": records,
        "records_sha256": transport.sha256_bytes(
            json.dumps(records, sort_keys=True).encode()
        ),
        "status_counts": dict(Counter(row["status"] for row in records)),
        "semantic_review": "pending",
        "human_review": "pending",
    }
    parsed_dir = output_dir / "parsed"
    parsed_dir.mkdir(parents=True, exist_ok=True)
    parsed_path = parsed_dir / f"batch_{batch_number:02d}.json"
    transport.atomic_write_json(parsed_path, parsed)
    return parsed


def merge_transport_parts(config_path: Path, batch_number: int) -> dict[str, Any]:
    config = load_config(config_path)
    if batch_number < 1 or batch_number > 5:
        raise ValueError("Batch number must be 1 through 5")
    output_dir = _resolve(str(config["output_dir"]))
    all_rows = transport.read_jsonl(output_dir / "SOURCE_BATCH_100.jsonl")
    batch_size = int(config["batch_size"])
    chunk_size = int(config["transport_chunk_size"])
    start = (batch_number - 1) * batch_size
    rows = all_rows[start : start + batch_size]
    items: list[dict[str, Any]] = []
    part_hashes = []
    for part_number in range(1, batch_size // chunk_size + 1):
        path = output_dir / "raw" / f"batch_{batch_number:02d}_part_{part_number:02d}.json"
        structured = _decode_response(path)
        part = structured.get("templates")
        if not isinstance(part, list) or len(part) != chunk_size:
            raise ValueError(f"Transport part {part_number} has the wrong count")
        items.extend(part)
        part_hashes.append(transport.sha256_file(path))
    for position, (row, item) in enumerate(zip(rows, items), 1):
        if (
            item.get("source_id") != row["source_id"]
            or item.get("original_response_sha256")
            != row["original_response_sha256"]
        ):
            raise ValueError(f"Transport source mismatch at batch position {position}")
    output_path = output_dir / "raw" / f"batch_{batch_number:02d}.json"
    transport.atomic_write_json(output_path, {"templates": items})
    return {
        "batch_number": batch_number,
        "records": len(items),
        "part_sha256": part_hashes,
        "output_path": str(output_path),
        "output_sha256": transport.sha256_file(output_path),
    }


def apply_repair_spec(config_path: Path, spec_path: Path) -> dict[str, Any]:
    config = load_config(config_path)
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    if spec.get("protocol_version") != "gpt56-chat-batch-repairs-v1":
        raise ValueError("Wrong ordinary-Chat repair protocol")
    batch_number = int(spec["batch_number"])
    if batch_number < 1 or batch_number > 5:
        raise ValueError("Repair batch number must be 1 through 5")
    base_path = _resolve(str(spec["base_response_path"]))
    replacement_path = _resolve(str(spec["replacement_response_path"]))
    if transport.sha256_file(base_path) != spec["base_response_sha256"]:
        raise ValueError("Repair base response hash changed")
    if transport.sha256_file(replacement_path) != spec["replacement_response_sha256"]:
        raise ValueError("Repair replacement response hash changed")

    output_dir = _resolve(str(config["output_dir"]))
    all_rows = transport.read_jsonl(output_dir / "SOURCE_BATCH_100.jsonl")
    batch_size = int(config["batch_size"])
    start = (batch_number - 1) * batch_size
    rows = all_rows[start : start + batch_size]
    base_items = _decode_response(base_path).get("templates")
    replacement_items = _decode_response(replacement_path).get("templates")
    if not isinstance(base_items, list) or len(base_items) != batch_size:
        raise ValueError("Repair base response must contain one complete batch")
    if not isinstance(replacement_items, list):
        raise ValueError("Repair replacement response is invalid")
    raw_replacement_slots = spec.get("replacement_slots")
    if not isinstance(raw_replacement_slots, list):
        raise ValueError("Repair replacement_slots must be a list")
    replacement_slots = [str(value) for value in raw_replacement_slots]
    if len(set(replacement_slots)) != len(replacement_slots):
        raise ValueError("Duplicate repair replacement slot")
    rows_by_slot = {str(row["production_slot"]): row for row in rows}
    if len(rows_by_slot) != len(rows):
        raise ValueError("Batch contains duplicate production slots")
    if set(replacement_slots) - set(rows_by_slot):
        raise ValueError("Repair replacement slot is outside the batch")
    if any(not isinstance(item, dict) for item in replacement_items):
        raise ValueError("Repair replacement response item is not an object")
    expected_replacement_ids = [
        str(rows_by_slot[slot]["source_id"]) for slot in replacement_slots
    ]
    actual_replacement_ids = [
        str(item.get("source_id")) for item in replacement_items
    ]
    if actual_replacement_ids != expected_replacement_ids:
        raise ValueError(
            "Repair replacement response IDs must exactly match designated rows"
        )
    replacement_by_id = {
        str(item["source_id"]): item for item in replacement_items
    }
    replacement_slot_set = set(replacement_slots)
    patches = {
        str(item["production_slot"]): item
        for item in spec.get("template_repairs", [])
    }
    if len(patches) != len(spec.get("template_repairs", [])):
        raise ValueError("Duplicate template repair slot")

    final_items = []
    for row, base_item in zip(rows, base_items):
        slot = str(row["production_slot"])
        if slot in replacement_slot_set:
            item = replacement_by_id.get(str(row["source_id"]))
            if item is None:
                raise ValueError(f"Missing replacement for {slot}")
        else:
            item = base_item
        if (
            item.get("source_id") != row["source_id"]
            or item.get("original_response_sha256")
            != row["original_response_sha256"]
        ):
            raise ValueError(f"Repair source identity mismatch at {slot}")
        updated = dict(item)
        if slot in patches:
            updated = local_repairs.apply_template_patch(
                {
                    **updated,
                    "production_slot": slot,
                    "shared_template": str(updated.get("shared_template", "")),
                },
                patches[slot],
            )
        final_items.append(updated)
    if set(patches) - {str(row["production_slot"]) for row in rows}:
        raise ValueError("Repair spec references a slot outside the batch")
    output_path = _resolve(str(spec["output_path"]))
    transport.ensure_private_output_dir(output_path.parent)
    repair_lineage = {
        "protocol_version": str(spec["protocol_version"]),
        "repair_spec_sha256": transport.sha256_file(spec_path),
        "base_response_sha256": str(spec["base_response_sha256"]),
        "replacement_response_sha256": str(
            spec["replacement_response_sha256"]
        ),
        "model_regenerated_templates": [
            {
                "production_slot": slot,
                "source_id": str(rows_by_slot[slot]["source_id"]),
            }
            for slot in replacement_slots
        ],
        "local_template_repairs": [
            {
                "production_slot": slot,
                "source_id": str(rows_by_slot[slot]["source_id"]),
                "prior_template_sha256": str(
                    patches[slot]["prior_template_sha256"]
                ),
                "reason": str(patches[slot]["reason"]),
                "model_calls": 0,
            }
            for slot in sorted(patches)
        ],
    }
    transport.atomic_write_json(
        output_path,
        {"templates": final_items, "repair_lineage": repair_lineage},
    )
    return {
        "batch_number": batch_number,
        "records": len(final_items),
        "template_repairs": len(patches),
        "model_regenerated_templates": len(replacement_slots),
        "output_path": str(output_path),
        "output_sha256": transport.sha256_file(output_path),
    }


def _repair_slots(
    lineage: Any,
    rows_by_slot: dict[str, dict[str, Any]],
) -> tuple[set[str], set[str]]:
    """Return validated model/local repair slots from one final raw artifact."""
    if lineage is None:
        return set(), set()
    if not isinstance(lineage, dict):
        raise ValueError("Final raw repair_lineage must be an object")

    def slots_for(field: str) -> set[str]:
        entries = lineage.get(field, [])
        if not isinstance(entries, list) or any(
            not isinstance(entry, dict) for entry in entries
        ):
            raise ValueError(f"Final raw {field} lineage must be a list of objects")
        slots = [str(entry.get("production_slot", "")) for entry in entries]
        if len(slots) != len(set(slots)):
            raise ValueError(f"Duplicate slot in final raw {field} lineage")
        for entry, slot in zip(entries, slots):
            row = rows_by_slot.get(slot)
            if row is None:
                raise ValueError(f"Unknown slot in final raw {field} lineage")
            if str(entry.get("source_id", "")) != str(row["source_id"]):
                raise ValueError(f"Source mismatch in final raw {field} lineage")
        return set(slots)

    return (
        slots_for("model_regenerated_templates"),
        slots_for("local_template_repairs"),
    )


def _assert_public_summary_text_free(manifest: dict[str, Any]) -> None:
    """Reject per-example content fields before a summary becomes public."""
    if manifest.get("contains_source_or_response_text") is not False:
        raise ValueError("Public summary must declare that it contains no text")
    forbidden = {
        "prompt",
        "original_response",
        "shared_template",
        "confident_response",
        "hedged_response",
        "confident_cues",
        "hedged_cues",
        "writer_issues",
        "validation_issues",
    }

    def visit(value: Any) -> None:
        if isinstance(value, dict):
            overlap = forbidden.intersection(str(key) for key in value)
            if overlap:
                raise ValueError(
                    "Public summary contains a forbidden text field: "
                    + ", ".join(sorted(overlap))
                )
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(manifest)


def finalize(config_path: Path) -> dict[str, Any]:
    """Combine five accepted batches and publish aggregate, text-free metadata."""
    config = load_config(config_path)
    output_dir = _resolve(str(config["output_dir"]))
    transport.ensure_private_output_dir(output_dir)
    source_path = output_dir / "SOURCE_BATCH_100.jsonl"
    if not source_path.is_file():
        raise FileNotFoundError("Run prepare before finalizing the checkpoint")
    rows = transport.read_jsonl(source_path)
    if len(rows) != int(config["source_count"]):
        raise ValueError("Final checkpoint source count is not 100")

    expected_rows = assign_cues(select_sources(config), _cue_bank(config))
    if _jsonl_bytes(rows) != _jsonl_bytes(expected_rows):
        raise ValueError("Prepared source batch does not match the frozen config")
    slots = [str(row["production_slot"]) for row in rows]
    source_ids = [str(row["source_id"]) for row in rows]
    if len(set(slots)) != len(rows) or len(set(source_ids)) != len(rows):
        raise ValueError("Final checkpoint sources are not unique")

    batch_size = int(config["batch_size"])
    batch_count = len(rows) // batch_size
    if batch_count != 5 or len(rows) % batch_size:
        raise ValueError("Finalize requires exactly five complete logical batches")

    all_records: list[dict[str, Any]] = []
    all_model_slots: set[str] = set()
    all_local_slots: set[str] = set()
    batch_summaries: list[dict[str, Any]] = []
    for batch_number in range(1, batch_count + 1):
        start = (batch_number - 1) * batch_size
        batch_rows = rows[start : start + batch_size]
        rows_by_slot = {
            str(row["production_slot"]): row for row in batch_rows
        }
        final_raw_path = output_dir / "raw" / f"batch_{batch_number:02d}_final.json"
        parsed_path = output_dir / "parsed" / f"batch_{batch_number:02d}.json"
        if not final_raw_path.is_file() or not parsed_path.is_file():
            raise FileNotFoundError(
                f"Batch {batch_number} is missing its final raw or parsed artifact"
            )

        final_raw = _decode_response(final_raw_path)
        templates = final_raw.get("templates")
        if (
            not isinstance(templates, list)
            or len(templates) != batch_size
            or any(not isinstance(template, dict) for template in templates)
        ):
            raise ValueError(f"Batch {batch_number} final raw artifact is incomplete")
        parsed = json.loads(parsed_path.read_text(encoding="utf-8"))
        if not isinstance(parsed, dict):
            raise ValueError(f"Batch {batch_number} parsed artifact is invalid")
        records = parsed.get("records")
        if (
            not isinstance(records, list)
            or len(records) != batch_size
            or any(not isinstance(record, dict) for record in records)
        ):
            raise ValueError(f"Batch {batch_number} parsed artifact is incomplete")
        expected_ids = [str(row["source_id"]) for row in batch_rows]
        if parsed.get("batch_number") != batch_number or parsed.get("source_ids") != expected_ids:
            raise ValueError(f"Batch {batch_number} parsed identity mismatch")
        if parsed.get("raw_response_sha256") != transport.sha256_file(final_raw_path):
            raise ValueError(f"Batch {batch_number} parsed result is not tied to final raw")
        records_sha256 = transport.sha256_bytes(
            json.dumps(records, sort_keys=True).encode("utf-8")
        )
        if parsed.get("records_sha256") != records_sha256:
            raise ValueError(f"Batch {batch_number} parsed records hash changed")
        if parsed.get("status_counts") != {"accepted": batch_size} or any(
            record.get("status") != "accepted" for record in records
        ):
            raise ValueError(f"Batch {batch_number} is not mechanically accepted")

        for row, template, record in zip(batch_rows, templates, records):
            identity = (
                str(row["source_id"]),
                str(row["original_response_sha256"]),
            )
            if (
                str(template.get("source_id")),
                str(template.get("original_response_sha256")),
            ) != identity or (
                str(record.get("source_id")),
                str(record.get("original_response_sha256")),
            ) != identity:
                raise ValueError(f"Batch {batch_number} source lineage mismatch")
            if str(record.get("production_slot")) != str(row["production_slot"]):
                raise ValueError(f"Batch {batch_number} production slot mismatch")
            if record.get("shared_template") != template.get("shared_template"):
                raise ValueError(f"Batch {batch_number} parsed template is stale")

        model_slots, local_slots = _repair_slots(
            final_raw.get("repair_lineage"), rows_by_slot
        )
        if all_model_slots.intersection(model_slots) or all_local_slots.intersection(
            local_slots
        ):
            raise ValueError("Repair lineage repeats a production slot across batches")
        all_model_slots.update(model_slots)
        all_local_slots.update(local_slots)
        batch_repaired = model_slots | local_slots
        batch_summaries.append(
            {
                "batch_number": batch_number,
                "final_mechanical_counts": {"accepted": batch_size},
                "records_without_recorded_repair": batch_size - len(batch_repaired),
                "model_regenerated_templates": len(model_slots),
                "local_template_repairs": len(local_slots),
                "records_with_both_model_and_local_repair": len(
                    model_slots & local_slots
                ),
                "final_raw_sha256": transport.sha256_file(final_raw_path),
                "parsed_records_sha256": records_sha256,
            }
        )
        all_records.extend(records)

    repaired_slots = all_model_slots | all_local_slots
    private_final = {
        "protocol_version": PROTOCOL_VERSION,
        "source_count": len(rows),
        "batch_count": batch_count,
        "records": all_records,
        "records_sha256": transport.sha256_bytes(
            json.dumps(all_records, sort_keys=True).encode("utf-8")
        ),
        "semantic_review": "pending",
        "human_review": "pending",
        "decision": "development_expansion_checkpoint_not_validated_training_data",
    }
    final_path = output_dir / "FINAL_100.json"

    manifest = {
        "protocol_version": PROTOCOL_VERSION,
        "contains_source_or_response_text": False,
        "chat_surface": str(config["chat_surface"]),
        "model_family_requested": str(config["model_family_requested"]),
        "exact_model_slug": "unavailable_from_thread_interface",
        "source_count": len(rows),
        "batch_count": batch_count,
        "transport_chunk_size": int(config["transport_chunk_size"]),
        "transport_chunk_count": len(rows) // int(config["transport_chunk_size"]),
        "transport_events": config.get("transport_events", {}),
        "initial_mechanical_counts_available": False,
        "final_mechanical_counts": {"accepted": len(all_records)},
        "repair_counts": {
            "records_without_recorded_repair": len(rows) - len(repaired_slots),
            "model_regenerated_templates": len(all_model_slots),
            "local_template_repairs": len(all_local_slots),
            "repaired_unique_records": len(repaired_slots),
            "records_with_both_model_and_local_repair": len(
                all_model_slots & all_local_slots
            ),
            "source_pool_replacements": len(config.get("source_replacements", [])),
        },
        "balance_counts": {
            field: _counts(rows, field)
            for field in (
                "dataset",
                "task",
                "length_bin",
                "rewrite_recipe",
                "rewrite_output_order",
                "target_longer_member",
                "stance_topology",
                "cue_set_id",
            )
        },
        "hashes": {
            "config_sha256": transport.sha256_file(config_path),
            "cue_bank_sha256": str(config["cue_bank_sha256"]),
            "source_file_sha256": transport.sha256_file(source_path),
            "source_ids_sha256": transport.source_ids_sha256(rows),
            "source_response_hashes_sha256": transport.sha256_bytes(
                "\n".join(
                    str(row["original_response_sha256"]) for row in rows
                ).encode("utf-8")
            ),
            "combined_records_sha256": private_final["records_sha256"],
        },
        "per_batch": batch_summaries,
        "semantic_review": "pending",
        "human_pair_review": "pending",
        "source_review": "automated_screening_only_human_review_pending",
        "decision": "development_expansion_checkpoint_not_validated_training_data",
    }
    _assert_public_summary_text_free(manifest)
    transport.atomic_write_json(final_path, private_final)
    manifest["hashes"]["private_final_file_sha256"] = transport.sha256_file(
        final_path
    )
    _assert_public_summary_text_free(manifest)
    transport.atomic_write_json(SUMMARY_MANIFEST, manifest)
    return manifest


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("prepare")
    validate = subparsers.add_parser("validate")
    validate.add_argument("--batch", type=int, required=True)
    validate.add_argument("--response", type=Path, required=True)
    repair = subparsers.add_parser("repair")
    repair.add_argument("--spec", type=Path, required=True)
    merge = subparsers.add_parser("merge")
    merge.add_argument("--batch", type=int, required=True)
    subparsers.add_parser("finalize")
    args = parser.parse_args(argv)
    config_path = args.config.resolve()
    if args.command == "prepare":
        result = prepare(config_path)
        print(json.dumps({
            "sources": result["source_count"],
            "batches": result["batch_count"],
            "counts": result["counts"],
        }, ensure_ascii=False))
        return 0
    if args.command == "repair":
        result = apply_repair_spec(config_path, args.spec.resolve())
        print(json.dumps(result, ensure_ascii=False))
        return 0
    if args.command == "merge":
        result = merge_transport_parts(config_path, args.batch)
        print(json.dumps(result, ensure_ascii=False))
        return 0
    if args.command == "finalize":
        result = finalize(config_path)
        print(json.dumps({
            "sources": result["source_count"],
            "final_mechanical_counts": result["final_mechanical_counts"],
            "repair_counts": result["repair_counts"],
        }, ensure_ascii=False))
        return 0
    result = validate_batch(config_path, args.batch, args.response.resolve())
    print(json.dumps({
        "batch": args.batch,
        "status_counts": result["status_counts"],
    }))
    return 0 if result["status_counts"] == {"accepted": 20} else 1


if __name__ == "__main__":
    raise SystemExit(main())
