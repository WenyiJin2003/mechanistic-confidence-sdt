#!/usr/bin/env python3
"""Provider-free lifecycle validation for the six lambda-canary outputs."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from lambda_objective import EXPECTED_PROBE_SHA256


EXPECTED_TRAIN_SHA256 = (
    "68da0932903a2b702f5f8506167399adc74ae511e691523ef8a8227f2b85867e"
)
EXPECTED_MODEL_REVISION = "989aa7980e4cf806f80c7fef2b1adb7bc71aa306"
EXPECTED_PRESERVED_COHORTS = {
    "lora_dev_cf3_113.jsonl": (
        "1bb24b7aef0e891f99bc8371c0c65412ae66115771a0aca566ca3c5e816b3c06"
    ),
    "behavior_canary_cue50_46.jsonl": (
        "ea92c2691b4ba73247925d2f400411f2e39c184fbe2dfc65515c598dc26e1585"
    ),
}


def parse_args() -> argparse.Namespace:
    experiment = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--result-file", type=Path, required=True)
    parser.add_argument(
        "--matrix",
        type=Path,
        default=experiment / "config/SIX_RUN_MATRIX.json",
    )
    return parser.parse_args()


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def validate_six_runs(output_root: Path, matrix_path: Path) -> dict[str, Any]:
    matrix = read_json(matrix_path)
    arms = matrix.get("arms")
    if not isinstance(arms, list) or len(arms) != 6:
        raise ValueError("run matrix must contain exactly six arms")
    labels = [arm.get("label") for arm in arms]
    if len(set(labels)) != 6:
        raise ValueError("run matrix labels are not unique")

    records: list[dict[str, Any]] = []
    invariant_snapshots: list[dict[str, Any]] = []
    reference_digests: dict[str, set[str]] = {"confident": set(), "hesitant": set()}
    for arm in arms:
        arm_dir = output_root / arm["label"]
        required = [arm_dir / name for name in matrix["required_per_arm_outputs"]]
        missing = [str(path) for path in required if not path.is_file()]
        if missing:
            raise ValueError(f"{arm['label']}: missing required outputs: {missing}")
        run = read_json(arm_dir / "RUN_CONFIG.json")
        reload_check = read_json(arm_dir / "SMOKE_RELOAD_CHECK.json")
        if run.get("role") != arm["role"]:
            raise ValueError(f"{arm['label']}: role mismatch")
        if float(run.get("target_gradient_ratio", -1)) != float(
            arm["target_gradient_ratio"]
        ):
            raise ValueError(f"{arm['label']}: gradient-ratio mismatch")
        if run.get("base_model_revision") != EXPECTED_MODEL_REVISION:
            raise ValueError(f"{arm['label']}: model revision mismatch")
        if run.get("train_file_sha256") != EXPECTED_TRAIN_SHA256:
            raise ValueError(f"{arm['label']}: train hash mismatch")
        if run.get("probe_artifact_sha256") != EXPECTED_PROBE_SHA256:
            raise ValueError(f"{arm['label']}: probe hash mismatch")
        if run.get("probe_layer") != 14 or run.get("margin") != 0.5:
            raise ValueError(f"{arm['label']}: probe layer or margin mismatch")
        if run.get("all_trainable_parameters_lora_only") is not True:
            raise ValueError(f"{arm['label']}: non-LoRA trainables were not excluded")
        if run.get("scientific_claim_authority") is not False:
            raise ValueError(f"{arm['label']}: canary claim status changed")
        if run.get("source_disjointness", {}).get("status") != "PASS":
            raise ValueError(f"{arm['label']}: source-disjointness did not pass")
        preserved = {
            Path(record["path"]).name: record["sha256"]
            for record in run["source_disjointness"].get("files", [])
            if record.get("name") != "train"
        }
        if preserved != EXPECTED_PRESERVED_COHORTS:
            raise ValueError(f"{arm['label']}: preserved cohort hashes changed")
        cuda_runtime = run.get("cuda_runtime")
        required_cuda_fields = {
            "device_name",
            "compute_capability",
            "torch_cuda_runtime_version",
            "cudnn_version",
            "total_memory_bytes",
        }
        if not isinstance(cuda_runtime, dict) or not required_cuda_fields.issubset(
            cuda_runtime
        ):
            raise ValueError(f"{arm['label']}: CUDA/runtime metadata is incomplete")
        if reload_check.get("status") != "PASS" or reload_check.get(
            "reload_exact_text_match"
        ) is not True:
            raise ValueError(f"{arm['label']}: save/reload check did not pass")

        ratio = float(arm["target_gradient_ratio"])
        weight = float(run.get("lambda", -1))
        if ratio == 0.0 and weight != 0.0:
            raise ValueError(f"{arm['label']}: zero-ratio lambda is not zero")
        if ratio > 0:
            if weight <= 0:
                raise ValueError(f"{arm['label']}: positive-ratio lambda is not positive")
            achieved = float(run.get("calibration", {}).get("achieved_median_ratio", -1))
            if abs(achieved - ratio) > 1e-10:
                raise ValueError(f"{arm['label']}: achieved calibration ratio changed")

        reference = run.get("base_reference_record", {})
        if reference.get("count") != 156:
            raise ValueError(f"{arm['label']}: base-reference count mismatch")
        digest = reference.get("ordered_id_and_float_hex_sha256")
        if not isinstance(digest, str) or len(digest) != 64:
            raise ValueError(f"{arm['label']}: invalid base-reference digest")
        reference_digests[arm["role"]].add(digest)
        invariant_snapshots.append(
            {
                "base_model_revision": run["base_model_revision"],
                "train_file_sha256": run["train_file_sha256"],
                "probe_artifact_sha256": run["probe_artifact_sha256"],
                "probe_layer": run["probe_layer"],
                "margin": run["margin"],
                "train_rows": run["train_rows"],
                "epochs": run["epochs"],
                "optimizer_steps": run["optimizer_steps"],
                "learning_rate": run["learning_rate"],
                "physical_batch_size": run["physical_batch_size"],
                "gradient_accumulation": run["gradient_accumulation"],
                "max_length": run["max_length"],
                "precision": run["precision"],
                "cuda_device_name": cuda_runtime["device_name"],
                "cuda_compute_capability": cuda_runtime["compute_capability"],
                "seed": run["seed"],
                "lora": run["lora"],
            }
        )
        records.append(
            {
                "label": arm["label"],
                "adapter_dir": str(arm_dir.resolve()),
                "role": arm["role"],
                "target_gradient_ratio": ratio,
                "lambda": weight,
                "base_reference_digest": digest,
                "cuda_runtime": cuda_runtime,
                "reload_status": reload_check["status"],
            }
        )

    canonical_invariants = json.dumps(
        invariant_snapshots[0], sort_keys=True, separators=(",", ":")
    )
    if any(
        json.dumps(snapshot, sort_keys=True, separators=(",", ":"))
        != canonical_invariants
        for snapshot in invariant_snapshots[1:]
    ):
        raise ValueError("non-objective training invariants differ across arms")
    if any(len(digests) != 1 for digests in reference_digests.values()):
        raise ValueError("fixed base-reference digest differs within a role")

    return {
        "schema": "confidence-probe-guided-lora-six-run-validation-v1",
        "status": "PASS",
        "scope": "training lifecycle only; no behavioral or final-test evaluation",
        "output_root": str(output_root.resolve()),
        "matrix": str(matrix_path.resolve()),
        "arm_count": len(records),
        "arms": records,
        "base_reference_digest_by_role": {
            role: next(iter(digests)) for role, digests in reference_digests.items()
        },
        "reserved_final_test_read": False,
        "scientific_claim_authority": False,
    }


def main() -> None:
    args = parse_args()
    if args.result_file.exists():
        raise FileExistsError(f"refuse to overwrite result: {args.result_file}")
    result = validate_six_runs(args.output_root.resolve(), args.matrix.resolve())
    args.result_file.parent.mkdir(parents=True, exist_ok=True)
    args.result_file.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
