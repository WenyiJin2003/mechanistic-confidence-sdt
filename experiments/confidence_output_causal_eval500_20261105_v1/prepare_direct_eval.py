#!/usr/bin/env python3
"""Freeze five private 100-question shards for the direct r010 comparison."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any


EXPERIMENT = Path(__file__).resolve().parent
REPO = EXPERIMENT.parents[1]
COHORT = EXPERIMENT / "private_data/EVAL_COHORT_500.jsonl"
COHORT_SHA256 = "694da55371f52132b662000bf187ee32cfdcb6e0f1e196683f904b7e4877c79c"
RUN_MANIFEST = REPO / (
    "experiments/confidence_probe_guided_lora_lambda_canary_20261104_v1/"
    "outputs/lambda_canary_20261104_run01/EVALUATION_MANIFEST.json"
)
RUN_MANIFEST_SHA256 = "0a40275708bce5df991ecfd82de0a493ced13ab56ca0a590513161e225fa41b5"
PROBE = REPO / "experiments/confidence_probe_scaleup_20261104_v1/results_primary_v1/paired_probe_size_920.npz"
PROBE_SHA256 = "b3ae72757c1e9d32b6c182b8653749fc96dc88e74afaff8edb5b6e93c66b9749"
RUNS = {
    "confident_r010": {
        "role": "confident",
        "target_aux_gradient_ratio": 0.10,
        "adapter_config_sha256": "1e129d08fc9bba0fd54764f44321d6ef3d9a0744b13b796f0b9d4fc6ae28bf00",
        "adapter_weights_sha256": "1a944c6abfbf2a7b8765d11257a27f60f8023c76d67ee3a5d994e5d7151dc830",
        "run_config_sha256": "3ec5158148a6531a0731447200f7ddc58ce672ea5895cbb8b6ad9ed78dbecd59",
        "smoke_reload_sha256": "400840e0216968d73326a43a74b6bafb5a3f52aec939629f5535da26ad2f70bf",
    },
    "hesitant_r010": {
        "role": "hesitant",
        "target_aux_gradient_ratio": 0.10,
        "adapter_config_sha256": "dcb3de6d68eab186adb9728a7075aac5e5096141c972841844d9677efecb834b",
        "adapter_weights_sha256": "703cdc160c12d20534c176107992c78ce452b2b01d4e91cd48286380cf90077a",
        "run_config_sha256": "e53a6e2c1557c8f2b3593a90e7fe69780714eea975697a6676c8b63a716fdca7",
        "smoke_reload_sha256": "454e047df5c5feba592f328c5936c9041d35e804e3b13e6a645b5adb4381b25b",
    },
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def json_line(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def exclusive_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())


def main() -> None:
    pins = ((COHORT, COHORT_SHA256), (RUN_MANIFEST, RUN_MANIFEST_SHA256), (PROBE, PROBE_SHA256))
    for path, expected in pins:
        observed = sha256_file(path)
        if observed != expected:
            raise RuntimeError(f"hash mismatch for {path}: {observed}")
    rows = [json.loads(line) for line in COHORT.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(rows) != 500 or len({row["eval_id"] for row in rows}) != 500:
        raise ValueError("cohort must contain exactly 500 unique eval IDs")
    shard_dir = EXPERIMENT / "private_data/direct_eval_shards"
    shard_records = []
    for shard_index in range(5):
        shard_rows = rows[shard_index * 100 : (shard_index + 1) * 100]
        payload = b"".join(json_line(row) for row in shard_rows)
        path = shard_dir / f"EVAL_SHARD_{shard_index:02d}.jsonl"
        exclusive_write(path, payload)
        shard_records.append(
            {
                "first_eval_id": shard_rows[0]["eval_id"],
                "last_eval_id": shard_rows[-1]["eval_id"],
                "path": str(path.relative_to(EXPERIMENT)),
                "rows": len(shard_rows),
                "sha256": hashlib.sha256(payload).hexdigest(),
                "shard_index": shard_index,
            }
        )
    authority = {
        "allowed_run_ids": sorted(RUNS),
        "cohort_file": str(COHORT.relative_to(EXPERIMENT)),
        "cohort_rows": 500,
        "cohort_sha256": COHORT_SHA256,
        "decoding": {"do_sample": False, "max_new_tokens": 256},
        "evaluation_manifest_relative_to_repo": str(RUN_MANIFEST.relative_to(REPO)),
        "evaluation_manifest_sha256": RUN_MANIFEST_SHA256,
        "expected_answer_rows": 1000,
        "jobs": 10,
        "max_parallel_gpu_jobs": 8,
        "model_id": "Qwen/Qwen2.5-1.5B-Instruct",
        "model_revision": "989aa7980e4cf806f80c7fef2b1adb7bc71aa306",
        "neutral_prompt": "single source question; no confidence instruction",
        "probe_artifact_relative_to_repo": str(PROBE.relative_to(REPO)),
        "probe_artifact_sha256": PROBE_SHA256,
        "research_status": "SOURCE_DISJOINT_DIRECT_BEHAVIORAL_EVALUATION; PUBLIC_BENCHMARK_PRETRAINING_NONCONTAMINATION_NOT_CLAIMED",
        "runs": RUNS,
        "schema": "confidence-output-direct-eval500-authority-v1",
        "shards": shard_records,
        "status": "READY_FOR_ONCE_ONLY_TEN_JOB_GENERATION",
    }
    exclusive_write(EXPERIMENT / "DIRECT_EVAL_AUTHORITY.json", json_line(authority))
    print(json.dumps(authority, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
