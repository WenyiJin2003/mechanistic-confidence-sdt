"""Recover an ordered source-review result with clerical hash-echo errors.

This performs no model call. It is intentionally narrow: output count, source
IDs, order, raw bytes, and the raw generation fingerprint must all match. Only
the echoed response hashes may be replaced from the frozen input, and every
replacement is recorded in the private parsed artifact.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

from experiments.diverse_pairs_multilayer_v1.src import (
    run_claude_rewrite_batches as transport,
)
from experiments.diverse_pairs_multilayer_v1.src import (
    run_claude_rewrite_batches_v33 as rewrite_v33,
)
from experiments.diverse_pairs_multilayer_v1.src import (
    run_claude_source_review_v33 as review,
)


def main() -> int:
    config = review.load_config(review.DEFAULT_CONFIG)
    rows, _ = rewrite_v33.validate_frozen_input(
        config.input_path, config.input_manifest_path, config.expected_sources
    )
    batches = review.make_batches(rows, config.batch_size)
    fingerprint = review._fingerprint(config, rows)
    recovered = 0
    corrected = 0
    for index, batch in enumerate(batches, 1):
        batch_id = review._batch_id(index, batch)
        raw_path = config.output_dir / "raw" / f"{batch_id}.json"
        parsed_path = config.output_dir / "parsed" / f"{batch_id}.json"
        if not raw_path.exists() or parsed_path.exists():
            continue
        raw = json.loads(raw_path.read_text(encoding="utf-8"))
        ids = [row["source_id"] for row in batch]
        hashes = [row["original_response_sha256"] for row in batch]
        if (
            raw.get("generation_fingerprint") != fingerprint
            or raw.get("source_ids") != ids
            or raw.get("source_hashes") != hashes
            or raw.get("returncode") != 0
            or raw.get("stdout_sha256")
            != transport.sha256_text(str(raw.get("stdout", "")))
            or raw.get("stderr_sha256")
            != transport.sha256_text(str(raw.get("stderr", "")))
        ):
            raise ValueError(f"Raw lineage check failed for {batch_id}")
        structured, metadata = transport.decode_structured(str(raw["stdout"]))
        items = structured.get("reviews")
        if not isinstance(items, list) or len(items) != len(batch):
            raise ValueError(f"Output count mismatch for {batch_id}")
        patched = copy.deepcopy(structured)
        positions = []
        for position, (source, item) in enumerate(zip(batch, patched["reviews"]), 1):
            if not isinstance(item, dict) or item.get("source_id") != source["source_id"]:
                raise ValueError(f"ID/order mismatch at {batch_id}:{position}")
            if item.get("original_response_sha256") != source["original_response_sha256"]:
                item["original_response_sha256"] = source["original_response_sha256"]
                positions.append(position)
        metadata["reported_model_validation"] = transport.verify_reported_model(
            metadata, config.model
        )
        records = review.validate_output(batch, patched)
        parsed = {
            "runner_version": review.RUNNER_VERSION,
            "protocol_version": review.PROTOCOL_VERSION,
            "generation_fingerprint": fingerprint,
            "batch_id": batch_id,
            "source_ids": ids,
            "records": records,
            "records_sha256": transport.sha256_bytes(
                json.dumps(records, sort_keys=True).encode()
            ),
            "metadata": metadata,
            "completed_at": review.utc_now(),
            "recovered_from_raw": raw_path.name,
            "hash_echo_correction_positions": positions,
            "additional_claude_calls": 0,
        }
        transport.atomic_write_json(parsed_path, parsed)
        recovered += 1
        corrected += len(positions)
    manifest = review.write_manifest(config, fingerprint, batches)
    print(json.dumps({
        "recovered_batches": recovered,
        "corrected_hash_echoes": corrected,
        "reviewed_sources": manifest["reviewed_sources"],
        "additional_claude_calls": 0,
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
