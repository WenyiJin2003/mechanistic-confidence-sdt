from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


EXPERIMENT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EXPERIMENT / "src"))

import validate_six_runs as validator  # noqa: E402


class SixRunValidatorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.matrix_path = EXPERIMENT / "config/SIX_RUN_MATRIX.json"
        self.matrix = json.loads(self.matrix_path.read_text())
        for arm in self.matrix["arms"]:
            directory = self.root / arm["label"]
            directory.mkdir()
            ratio = float(arm["target_gradient_ratio"])
            run = {
                "role": arm["role"],
                "target_gradient_ratio": ratio,
                "base_model_revision": validator.EXPECTED_MODEL_REVISION,
                "train_file_sha256": validator.EXPECTED_TRAIN_SHA256,
                "probe_artifact_sha256": validator.EXPECTED_PROBE_SHA256,
                "probe_layer": 14,
                "margin": 0.5,
                "all_trainable_parameters_lora_only": True,
                "scientific_claim_authority": False,
                "source_disjointness": {
                    "status": "PASS",
                    "files": [
                        {
                            "name": "train",
                            "path": "/synthetic/lora_train_cf200_156.jsonl",
                            "sha256": validator.EXPECTED_TRAIN_SHA256,
                        },
                        {
                            "name": "preserved_1",
                            "path": "/synthetic/lora_dev_cf3_113.jsonl",
                            "sha256": validator.EXPECTED_PRESERVED_COHORTS[
                                "lora_dev_cf3_113.jsonl"
                            ],
                        },
                        {
                            "name": "preserved_2",
                            "path": "/synthetic/behavior_canary_cue50_46.jsonl",
                            "sha256": validator.EXPECTED_PRESERVED_COHORTS[
                                "behavior_canary_cue50_46.jsonl"
                            ],
                        },
                    ],
                },
                "lambda": 0.0 if ratio == 0 else ratio * 0.4,
                "calibration": {"achieved_median_ratio": ratio},
                "base_reference_record": {
                    "count": 156,
                    "ordered_id_and_float_hex_sha256": (
                        "a" * 64 if arm["role"] == "confident" else "b" * 64
                    ),
                },
                "train_rows": 156,
                "epochs": 2,
                "optimizer_steps": 39,
                "learning_rate": 1e-4,
                "physical_batch_size": 1,
                "gradient_accumulation": 8,
                "max_length": 1024,
                "precision": "bf16",
                "cuda_runtime": {
                    "device_name": "synthetic-a100",
                    "compute_capability": [8, 0],
                    "torch_cuda_runtime_version": "12.8",
                    "cudnn_version": 91002,
                    "total_memory_bytes": 85899345920,
                },
                "seed": 20261104,
                "lora": {
                    "r": 8,
                    "alpha": 16,
                    "dropout": 0.05,
                    "targets": ["q_proj", "k_proj", "v_proj", "o_proj"],
                    "bias": "none",
                },
            }
            (directory / "RUN_CONFIG.json").write_text(json.dumps(run))
            (directory / "RUN_STARTED.json").write_text("{}")
            (directory / "TRAIN_LOG.jsonl").write_text("{}\n")
            (directory / "SMOKE_RELOAD_CHECK.json").write_text(
                json.dumps({"status": "PASS", "reload_exact_text_match": True})
            )
            (directory / "adapter_config.json").write_text("{}")
            (directory / "adapter_model.safetensors").write_bytes(b"test")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_complete_six_run_lifecycle_passes(self) -> None:
        result = validator.validate_six_runs(self.root, self.matrix_path)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["arm_count"], 6)
        self.assertFalse(result["reserved_final_test_read"])
        self.assertTrue(all(Path(run["adapter_dir"]).is_absolute() for run in result["arms"]))

    def test_within_role_reference_mismatch_fails(self) -> None:
        path = self.root / "confident_r010/RUN_CONFIG.json"
        run = json.loads(path.read_text())
        run["base_reference_record"]["ordered_id_and_float_hex_sha256"] = "c" * 64
        path.write_text(json.dumps(run))
        with self.assertRaisesRegex(ValueError, "base-reference digest differs"):
            validator.validate_six_runs(self.root, self.matrix_path)


if __name__ == "__main__":
    unittest.main()
