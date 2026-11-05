#!/usr/bin/env python3
"""Freeze the same-role probe-loss versus no-probe comparison."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path


EXPERIMENT = Path(__file__).resolve().parent
DIRECT_AUTHORITY = EXPERIMENT / "DIRECT_EVAL_AUTHORITY.json"
RUNS = {
    "confident_r000": {
        "adapter_config_sha256": "b3b59cbf6dd21dac2c8fa62c1e1302051e02fba7c4da5ce19d013515f9345eba",
        "adapter_weights_sha256": "6ecd0a634a1caf888f7c18ec68600d949e779d8cd59f95fe1dfde15bb8ae8f38",
        "role": "confident",
        "run_config_sha256": "2cecc16292c7f4709153bc0c93c64413c28684ae3650da8514299b8d3ec8b152",
        "smoke_reload_sha256": "ac725d5fefe114097bd66da3040bb3fe2c97d1e1c4fe4b179131de1f716d0e8d",
        "target_aux_gradient_ratio": 0.0,
    },
    "hesitant_r000": {
        "adapter_config_sha256": "0a29ac06229d67bbded0f20511972fe4afb265b9f5f4f96808a719812207143b",
        "adapter_weights_sha256": "23c00571b8d4b2424e55f58405187c01afd6da3582ab9bb2b774421f1cc03ca0",
        "role": "hesitant",
        "run_config_sha256": "51ac52a42d9e93f856276f43f045f3d588f4d4add12d4815e7a96039d178116a",
        "smoke_reload_sha256": "a9fe1d0566a8f78fa77ad048550da2c3790f6af838e82f59ffbcbc9f97f67764",
        "target_aux_gradient_ratio": 0.0,
    },
}


def exclusive_write(path: Path, value: dict) -> None:
    payload = (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())


def main() -> None:
    direct = json.loads(DIRECT_AUTHORITY.read_text(encoding="utf-8"))
    if direct.get("status") != "READY_FOR_ONCE_ONLY_TEN_JOB_GENERATION":
        raise ValueError("direct evaluation authority is not the frozen parent")
    authority = {
        **{key: direct[key] for key in (
            "cohort_file",
            "cohort_rows",
            "cohort_sha256",
            "decoding",
            "evaluation_manifest_relative_to_repo",
            "evaluation_manifest_sha256",
            "model_id",
            "model_revision",
            "neutral_prompt",
            "probe_artifact_relative_to_repo",
            "probe_artifact_sha256",
            "shards",
        )},
        "allowed_run_ids": sorted(RUNS),
        "comparison": {
            "confident": "confident_r010 (probe loss) versus confident_r000 (same-role CE-only)",
            "hesitant": "hesitant_r010 (probe loss) versus hesitant_r000 (same-role CE-only)",
        },
        "direct_parent_authority_sha256": hashlib.sha256(DIRECT_AUTHORITY.read_bytes()).hexdigest(),
        "expected_new_answer_rows": 1000,
        "jobs": 10,
        "max_parallel_gpu_jobs": 8,
        "research_question": "Does adding the frozen L14 auxiliary loss change same-role free-generation confidence beyond otherwise matched CE-only SFT?",
        "runs": RUNS,
        "schema": "confidence-output-probe-ablation-eval500-authority-v1",
        "status": "READY_FOR_ONCE_ONLY_NO_PROBE_BASELINE_GENERATION",
    }
    exclusive_write(EXPERIMENT / "PROBE_ABLATION_AUTHORITY.json", authority)
    print(json.dumps(authority, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
