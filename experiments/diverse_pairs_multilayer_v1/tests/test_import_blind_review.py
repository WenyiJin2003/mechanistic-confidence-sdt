"""Focused tests for the generic five-field blind-review importer."""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest


SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

import build_blind_review_packet as builder
import import_blind_review as importer


def _write_packet(tmp_path: Path, pair_count: int = 3) -> Path:
    base = tmp_path
    private = base / "private_data"
    private.mkdir()
    sources = []
    pairs = []
    for index in range(pair_count):
        source_id = f"source-{index:03d}"
        original = f"Original answer {index}."
        source_hash = builder.sha256_text(original)
        sources.append(
            {
                "source_id": source_id,
                "original_response": original,
                "original_response_sha256": source_hash,
                "prompt": f"Question {index}?",
                "task": "fixture",
                "dataset": "fixture",
            }
        )
        pairs.append(
            {
                "source_id": source_id,
                "original_response_sha256": source_hash,
                "confident_response": f"Definitely, the answer is {index}.",
                "hedged_response": f"I think the answer may be {index}.",
                "status": "accepted",
            }
        )

    source_path = private / "sources.jsonl"
    source_path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in sources),
        encoding="utf-8",
    )
    records_hash = builder.sha256_text(json.dumps(pairs, sort_keys=True))
    pair_path = private / "pairs.json"
    pair_path.write_text(
        json.dumps({"records": pairs, "records_sha256": records_hash}),
        encoding="utf-8",
    )
    config = {
        "title": "Fixture blind review",
        "seed": 17,
        "expected_pairs": pair_count,
        "source_files": [
            {
                "path": "private_data/sources.jsonl",
                "file_sha256": builder.sha256_file(source_path),
            }
        ],
        "pair_batches": [
            {
                "cohort": "fixture",
                "path": "private_data/pairs.json",
                "file_sha256": builder.sha256_file(pair_path),
                "records_sha256": records_hash,
            }
        ],
        "output_dir": "private_data/review_packet",
    }
    config_path = base / "packet_config.json"
    config_path.write_text(json.dumps(config), encoding="utf-8")
    builder.build_packet(config_path, base)
    return private / "review_packet"


def _export_for(packet_dir: Path, *, complete: bool = True) -> dict:
    manifest = json.loads((packet_dir / "MANIFEST.json").read_text(encoding="utf-8"))
    key = json.loads((packet_dir / "UNBLIND_KEY.json").read_text(encoding="utf-8"))
    reviews = []
    for index, entry in enumerate(key["pairs"]):
        review = {"review_id": entry["review_id"]}
        if complete or index:
            review.update(
                {
                    "content_equivalence": "both_match",
                    "certainty_contrast": (
                        "a_more_certain"
                        if entry["version_a_label"] == "confident"
                        else "b_more_certain"
                    ),
                    "naturalness": "both_natural",
                    "cue_scope": "both_global",
                    "decision": "accept",
                    "comment": "private reviewer comment",
                    "updated_at": "2026-10-13T12:00:00Z",
                }
            )
        reviews.append(review)
    return {
        "packet_sha256": manifest["packet_sha256"],
        "reviewed_at": "2026-10-13T12:01:00Z",
        "blinded": True,
        "reviews": reviews,
    }


def _write_export(path: Path, payload: dict) -> bytes:
    raw = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    path.write_bytes(raw)
    return raw


def test_complete_import_preserves_raw_decodes_from_key_and_writes_text_free_counts(tmp_path):
    packet_dir = _write_packet(tmp_path)
    export_path = tmp_path / "review_export.json"
    raw = _write_export(export_path, _export_for(packet_dir))
    private_output = tmp_path / "private_data" / "review_import"
    aggregate_path = tmp_path / "reports" / "review_aggregate.json"

    aggregate = importer.import_review(
        packet_dir,
        export_path,
        private_output,
        aggregate_path,
        base=tmp_path,
    )

    assert (private_output / "RAW_REVIEW_EXPORT.json").read_bytes() == raw
    decoded = json.loads((private_output / "DECODED_REVIEW.json").read_text())
    key = json.loads((packet_dir / "UNBLIND_KEY.json").read_text())
    assert decoded["records"][0]["answer_key"]["version_a_label"] == key["pairs"][0]["version_a_label"]
    assert "reviewer choices never create or modify labels" in decoded["label_provenance"]
    assert aggregate["complete_pairs"] == 3
    assert aggregate["gate_completed"] is True
    assert aggregate["certainty_alignment_counts"] == {"matches_key": 3}

    public_text = aggregate_path.read_text(encoding="utf-8")
    assert "source_id" not in public_text
    assert "Original answer" not in public_text
    assert "private reviewer comment" not in public_text
    assert "review_id" not in public_text


def test_incomplete_export_is_valid_but_cannot_complete_gate(tmp_path):
    packet_dir = _write_packet(tmp_path)
    export_path = tmp_path / "review_export.json"
    _write_export(export_path, _export_for(packet_dir, complete=False))
    decoded, aggregate, _ = importer.validate_and_decode(
        packet_dir, export_path, base=tmp_path
    )
    assert len(decoded["records"]) == 3
    assert aggregate["complete_pairs"] == 2
    assert aggregate["incomplete_pairs"] == 1
    assert aggregate["gate_completed"] is False
    assert aggregate["counts"]["decision"]["missing"] == 1


def test_reviewer_certainty_choice_never_changes_key_label(tmp_path):
    packet_dir = _write_packet(tmp_path)
    payload = _export_for(packet_dir)
    key = json.loads((packet_dir / "UNBLIND_KEY.json").read_text())
    expected_label = key["pairs"][0]["version_a_label"]
    payload["reviews"][0]["certainty_contrast"] = (
        "b_more_certain"
        if payload["reviews"][0]["certainty_contrast"] == "a_more_certain"
        else "a_more_certain"
    )
    export_path = tmp_path / "review_export.json"
    _write_export(export_path, payload)

    decoded, aggregate, _ = importer.validate_and_decode(
        packet_dir, export_path, base=tmp_path
    )

    assert decoded["records"][0]["answer_key"]["version_a_label"] == expected_label
    assert decoded["records"][0]["certainty_alignment_with_key"] == "contradicts_key"
    assert aggregate["certainty_alignment_counts"]["contradicts_key"] == 1


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda payload: payload["reviews"][0].update(decision="maybe"), "Invalid decision"),
        (
            lambda payload: payload["reviews"].append(copy.deepcopy(payload["reviews"][0])),
            "Duplicate review_id",
        ),
        (lambda payload: payload["reviews"].pop(), "Review IDs do not match"),
        (
            lambda payload: payload["reviews"].append(
                {"review_id": "R999"}
            ),
            "Review IDs do not match",
        ),
        (lambda payload: payload.update(packet_sha256="0" * 64), "packet hash is stale"),
        (lambda payload: payload.update(reviewed_at="yesterday"), "timezone-aware ISO timestamp"),
        (
            lambda payload: payload["reviews"][0].update(updated_at="2026-10-13"),
            "timezone-aware ISO timestamp",
        ),
    ],
)
def test_rejects_invalid_values_duplicate_missing_extra_ids_and_stale_export_hash(
    tmp_path, mutation, message
):
    packet_dir = _write_packet(tmp_path)
    payload = _export_for(packet_dir)
    mutation(payload)
    export_path = tmp_path / "review_export.json"
    _write_export(export_path, payload)
    with pytest.raises(ValueError, match=message):
        importer.validate_and_decode(packet_dir, export_path, base=tmp_path)


def test_rejects_stale_unblind_key_hash(tmp_path):
    packet_dir = _write_packet(tmp_path)
    key_path = packet_dir / "UNBLIND_KEY.json"
    key = json.loads(key_path.read_text())
    key["packet_sha256"] = "0" * 64
    key_path.write_text(json.dumps(key), encoding="utf-8")
    export_path = tmp_path / "review_export.json"
    _write_export(export_path, _export_for(packet_dir))
    with pytest.raises(ValueError, match="UNBLIND_KEY packet hash"):
        importer.validate_and_decode(packet_dir, export_path, base=tmp_path)


def test_rejects_unblind_key_label_swap_against_manifest_hash(tmp_path):
    packet_dir = _write_packet(tmp_path)
    key_path = packet_dir / "UNBLIND_KEY.json"
    key = json.loads(key_path.read_text())
    first = key["pairs"][0]
    first["version_a_label"], first["version_b_label"] = (
        first["version_b_label"],
        first["version_a_label"],
    )
    key_path.write_text(json.dumps(key, indent=2) + "\n", encoding="utf-8")
    export_path = tmp_path / "review_export.json"
    _write_export(export_path, _export_for(packet_dir))
    with pytest.raises(ValueError, match="UNBLIND_KEY file hash"):
        importer.validate_and_decode(packet_dir, export_path, base=tmp_path)


def test_rejects_stale_blinded_rows_hash(tmp_path):
    packet_dir = _write_packet(tmp_path)
    rows_path = packet_dir / "BLINDED_ROWS.jsonl"
    rows_path.write_text(rows_path.read_text() + "\n", encoding="utf-8")
    export_path = tmp_path / "review_export.json"
    _write_export(export_path, _export_for(packet_dir))
    with pytest.raises(ValueError, match="BLINDED_ROWS packet hash"):
        importer.validate_and_decode(packet_dir, export_path, base=tmp_path)


def test_refuses_public_decoded_output_and_overwrite(tmp_path):
    packet_dir = _write_packet(tmp_path)
    export_path = tmp_path / "review_export.json"
    _write_export(export_path, _export_for(packet_dir))
    with pytest.raises(ValueError, match="private_data"):
        importer.import_review(
            packet_dir,
            export_path,
            tmp_path / "public_decoded",
            tmp_path / "reports" / "aggregate.json",
            base=tmp_path,
        )

    private_output = tmp_path / "private_data" / "review_import"
    aggregate_path = tmp_path / "reports" / "aggregate.json"
    importer.import_review(
        packet_dir, export_path, private_output, aggregate_path, base=tmp_path
    )
    with pytest.raises(FileExistsError, match="Refusing to overwrite"):
        importer.import_review(
            packet_dir, export_path, private_output, aggregate_path, base=tmp_path
        )


def test_existing_twenty_pair_packet_schema_is_supported(tmp_path):
    packet_dir = _write_packet(tmp_path, pair_count=20)
    export_path = tmp_path / "review_export.json"
    _write_export(export_path, _export_for(packet_dir))
    decoded, aggregate, _ = importer.validate_and_decode(
        packet_dir, export_path, base=tmp_path
    )
    assert len(decoded["records"]) == 20
    assert aggregate["pairs"] == 20
    assert aggregate["gate_completed"] is True
