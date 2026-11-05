#!/usr/bin/env python3
"""Bind six validated training outputs into one immutable evaluation manifest."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from evaluate_adapters import BEHAVIOR_SHA256, DEV_SHA256, PROBE_SHA256, TRAIN_SHA256, file_sha256
from validate_six_runs import validate_six_runs


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--training-output-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--matrix", type=Path, default=root / "config/SIX_RUN_MATRIX.json")
    parser.add_argument("--dev-file", type=Path, default=root / "data/lora_dev_cf3_113.jsonl")
    parser.add_argument("--behavior-file", type=Path, default=root / "data/behavior_canary_cue50_46.jsonl")
    return parser.parse_args()


def canonical_sha256(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def build_manifest(
    training_output_root: Path,
    matrix_path: Path,
    dev_file: Path,
    behavior_file: Path,
) -> dict[str, Any]:
    training_output_root = training_output_root.resolve()
    matrix_path = matrix_path.resolve()
    dev_file = dev_file.resolve()
    behavior_file = behavior_file.resolve()
    if file_sha256(dev_file) != DEV_SHA256 or file_sha256(behavior_file) != BEHAVIOR_SHA256:
        raise ValueError("evaluation data hashes do not match the frozen canary")
    lifecycle = validate_six_runs(training_output_root, matrix_path)
    if lifecycle.get("status") != "PASS" or lifecycle.get("arm_count") != 6:
        raise ValueError("six-run lifecycle validation did not pass")
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    runs: list[dict[str, Any]] = []
    resolved_dirs: set[str] = set()
    for arm in matrix["arms"]:
        adapter_dir = (training_output_root / arm["label"]).resolve()
        resolved = str(adapter_dir)
        if resolved in resolved_dirs:
            raise ValueError("resolved adapter directories are not unique")
        resolved_dirs.add(resolved)
        run_config = adapter_dir / "RUN_CONFIG.json"
        smoke = adapter_dir / "SMOKE_RELOAD_CHECK.json"
        adapter_config = adapter_dir / "adapter_config.json"
        weights = sorted(adapter_dir.glob("adapter_model.*"))
        if len(weights) != 1:
            raise ValueError(f"{arm['label']}: expected exactly one adapter weight file")
        run_document = json.loads(run_config.read_text(encoding="utf-8"))
        smoke_document = json.loads(smoke.read_text(encoding="utf-8"))
        if run_document.get("schema") != "confidence-probe-guided-lora-lambda-run-v1":
            raise ValueError(f"{arm['label']}: run schema mismatch")
        if smoke_document.get("schema") != "confidence-probe-guided-lora-lambda-reload-v1":
            raise ValueError(f"{arm['label']}: smoke schema mismatch")
        if run_document.get("train_file_sha256") != TRAIN_SHA256:
            raise ValueError(f"{arm['label']}: training hash mismatch")
        if run_document.get("probe_artifact_sha256") != PROBE_SHA256:
            raise ValueError(f"{arm['label']}: probe hash mismatch")
        runs.append(
            {
                "run_id": arm["label"],
                "role": arm["role"],
                "target_aux_gradient_ratio": float(arm["target_gradient_ratio"]),
                "adapter_dir": resolved,
                "run_config_sha256": file_sha256(run_config),
                "smoke_reload_sha256": file_sha256(smoke),
                "adapter_config_sha256": file_sha256(adapter_config),
                "adapter_weights_sha256": file_sha256(weights[0]),
            }
        )
    lifecycle_digest = canonical_sha256(lifecycle)
    return {
        "schema": "confidence-probe-lambda-canary-evaluation-manifest-v1",
        "status": "READY_AFTER_SIX_RUN_VALIDATION_PASS",
        "research_status": "ENGINEERING_DEV_CANARY_ONLY_NOT_CONFIRMATORY",
        "training_output_root": str(training_output_root),
        "matrix": str(matrix_path),
        "matrix_sha256": file_sha256(matrix_path),
        "lifecycle_validation_canonical_sha256": lifecycle_digest,
        "train_file_sha256": TRAIN_SHA256,
        "probe_artifact_sha256": PROBE_SHA256,
        "dev_file": str(dev_file),
        "dev_file_sha256": DEV_SHA256,
        "behavior_file": str(behavior_file),
        "behavior_file_sha256": BEHAVIOR_SHA256,
        "runs": runs,
    }


def main() -> None:
    args = parse_args()
    if args.output.exists():
        raise FileExistsError(f"refuse to overwrite evaluation manifest: {args.output}")
    result = build_manifest(args.training_output_root, args.matrix, args.dev_file, args.behavior_file)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
