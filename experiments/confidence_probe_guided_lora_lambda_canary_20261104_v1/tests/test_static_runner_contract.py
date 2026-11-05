from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


EXPERIMENT = Path(__file__).resolve().parents[1]


class StaticRunnerContractTest(unittest.TestCase):
    def test_six_task_array_is_complete_and_unique(self) -> None:
        launcher = (EXPERIMENT / "slurm/train_lambda_array.sbatch").read_text()
        self.assertIn("#SBATCH --array=0-5%6", launcher)
        labels = re.findall(r'LABEL="([^"]+)"', launcher)
        self.assertEqual(
            labels,
            [
                "confident_r000",
                "hesitant_r000",
                "confident_r005",
                "hesitant_r005",
                "confident_r010",
                "hesitant_r010",
            ],
        )
        self.assertEqual(launcher.count('--margin 0.5'), 1)
        matrix = json.loads((EXPERIMENT / "config/SIX_RUN_MATRIX.json").read_text())
        self.assertEqual(
            [arm["label"] for arm in matrix["arms"]], labels
        )

    def test_runner_never_reads_reserved_final_test(self) -> None:
        runner = (EXPERIMENT / "src/train_lambda_canary.py").read_text()
        launcher = (EXPERIMENT / "slurm/train_lambda_array.sbatch").read_text()
        for forbidden in ("internal_test_193", "test_193", "final_test"):
            self.assertNotIn(forbidden, runner)
            self.assertNotIn(forbidden, launcher)

    def test_ratio_zero_uses_same_training_forward_path(self) -> None:
        runner = (EXPERIMENT / "src/train_lambda_canary.py").read_text()
        loop = runner.split('with log_path.open("w", encoding="utf-8") as log:', 1)[1]
        loop = loop.split("model.save_pretrained", 1)[0]
        self.assertIn("centered_losses(", loop)
        self.assertNotIn("if ratio == 0", loop)
        self.assertIn("combined_objective(", loop)

    def test_fixed_base_references_are_precomputed_before_calibration(self) -> None:
        runner = (EXPERIMENT / "src/train_lambda_canary.py").read_text()
        precompute = runner.index("base_reference_record = precompute_base_references")
        calibrate = runner.index("auxiliary_weight, calibration = calibrate_lambda")
        training = runner.index('with log_path.open("w", encoding="utf-8") as log:')
        self.assertLess(precompute, calibrate)
        self.assertLess(calibrate, training)
        self.assertIn("ordered_id_and_float_hex_sha256", runner)

    def test_reported_literal_duplicates_are_absent(self) -> None:
        runner = (EXPERIMENT / "src/train_lambda_canary.py").read_text()
        self.assertEqual(
            runner.count('raise ValueError("fixed base-reference score is absent or nonfinite")'),
            1,
        )
        log_section = runner.split("record = {", 1)[1].split("}", 1)[0]
        self.assertEqual(log_section.count('"adapter_z"'), 1)

    def test_calibration_set_has_frozen_stratified_coverage(self) -> None:
        config = json.loads((EXPERIMENT / "config/calibration_ids.json").read_text())
        rows = {
            row["id"]: row
            for row in (
                json.loads(line)
                for line in (
                    EXPERIMENT / "data/lora_train_cf200_156.jsonl"
                ).read_text().splitlines()
                if line
            )
        }
        ids = config["ids"]
        self.assertEqual(len(ids), 4)
        self.assertEqual(len(set(ids)), 4)
        self.assertEqual([item["id"] for item in config["coverage"]], ids)
        self.assertEqual(
            {rows[identifier]["length_bin"] for identifier in ids},
            {"short", "medium", "long"},
        )
        directions = [rows[identifier]["target_longer_role"] for identifier in ids]
        self.assertEqual(directions.count("confident"), 2)
        self.assertEqual(directions.count("hesitant"), 2)


if __name__ == "__main__":
    unittest.main()
