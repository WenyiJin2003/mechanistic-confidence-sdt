from __future__ import annotations

import json
import subprocess
from dataclasses import replace

import pytest

from experiments.diverse_pairs_multilayer_v1.src import (
    run_claude_component_repair_v35 as repair_v35,
)
from experiments.diverse_pairs_multilayer_v1.src import (
    run_claude_component_rewrite_v35 as rewrite_v35,
)
from experiments.diverse_pairs_multilayer_v1.src import (
    run_claude_component_rewrite_v36 as rewrite_v36,
)
from experiments.diverse_pairs_multilayer_v1.src import (
    run_claude_source_review_v33 as source_review,
)
from experiments.diverse_pairs_multilayer_v1.src import (
    run_claude_two_stage_rewrite_v37 as rewrite_v37,
)


def _source() -> dict:
    return {
        "source_id": "source-1",
        "original_response_sha256": "1" * 64,
        "production_slot": "P0001",
        "task": "factual_explanation",
        "prompt": "Question",
        "original_response": "Answer",
    }


@pytest.mark.parametrize(
    ("loader", "hash_fn"),
    [
        (source_review._load_existing, source_review._records_sha256),
        (rewrite_v35._load_parsed, rewrite_v35._records_sha256),
        (rewrite_v36._load_parsed, rewrite_v36._records_sha256),
    ],
)
def test_cached_records_require_hash_and_frozen_row_binding(
    tmp_path, loader, hash_fn
):
    source = _source()
    records = [{
        "source_id": source["source_id"],
        "original_response_sha256": source["original_response_sha256"],
    }]
    payload = {
        "generation_fingerprint": "current",
        "source_ids": [source["source_id"]],
        "records": records,
        "records_sha256": hash_fn(records),
    }
    path = tmp_path / "cache.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    assert loader(path, "current", [source]) == payload

    payload.pop("records_sha256")
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="record bytes changed"):
        loader(path, "current", [source])


def test_v37_and_repair_cache_reject_wrong_frozen_hash(tmp_path):
    source = _source()
    bad_records = [{
        "source_id": source["source_id"],
        "original_response_sha256": "2" * 64,
    }]
    payload = {
        "generation_fingerprint": "current",
        "source_ids": [source["source_id"]],
        "records": bad_records,
        "records_sha256": rewrite_v37.transport.sha256_bytes(
            json.dumps(bad_records, sort_keys=True).encode("utf-8")
        ),
    }
    path = tmp_path / "v37.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="cached lineage mismatch"):
        rewrite_v37._load_parsed(path, "current", [source])
    with pytest.raises(ValueError, match="Cached repair lineage mismatch"):
        repair_v35._validate_cached_parsed(payload, "current", [source])


def test_actual_passed_config_path_is_hashed(monkeypatch, tmp_path):
    config = source_review.load_config(source_review.DEFAULT_CONFIG)
    custom_path = tmp_path / "custom.json"
    custom_path.write_text("{}\n", encoding="utf-8")
    config = replace(config, config_path=custom_path)
    seen = []
    original = source_review.transport.sha256_file

    def recording_hash(path):
        seen.append(path)
        return original(path)

    monkeypatch.setattr(source_review.transport, "sha256_file", recording_hash)
    source_review._fingerprint(config, [_source()])
    assert custom_path in seen


def test_source_review_rejects_negative_max_batches():
    with pytest.raises(SystemExit):
        source_review.main(["--max-batches", "-1"])


def test_v35_rejects_negative_max_batches():
    with pytest.raises(SystemExit):
        rewrite_v35.main(["--max-batches", "-1"])


def test_timeout_checkpoint_blocks_automatic_retry(monkeypatch, tmp_path):
    config = replace(
        source_review.load_config(source_review.DEFAULT_CONFIG),
        output_dir=tmp_path,
        timeout_seconds=1,
    )
    batch = (_source(),)
    calls = 0

    def timeout(*args, **kwargs):
        nonlocal calls
        calls += 1
        raise subprocess.TimeoutExpired(args[0], 1, output="partial")

    monkeypatch.setattr(source_review.subprocess, "run", timeout)
    with pytest.raises(RuntimeError, match="automatic retry is disabled"):
        source_review.run_one(
            config, batch, "batch", "f" * 64, {}
        )
    assert calls == 1
    assert (tmp_path / "raw" / "batch.json").exists()
    assert (tmp_path / "failures" / "batch.json").exists()

    with pytest.raises(RuntimeError, match="blocks an automatic retry"):
        source_review.run_one(
            config, batch, "batch", "f" * 64, {}
        )
    assert calls == 1
