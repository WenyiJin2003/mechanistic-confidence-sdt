from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np
import torch


EXPERIMENT = Path(__file__).resolve().parents[1]
REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(EXPERIMENT / "src"))

import lambda_objective as objective  # noqa: E402


class FrozenProbeLoaderTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.artifact = (
            REPO
            / "experiments/confidence_probe_scaleup_20261104_v1/results_primary_v1/paired_probe_size_920.npz"
        )

    def test_exact_920_probe_selects_layer_14(self) -> None:
        loaded = objective.load_frozen_l14_probe(self.artifact)
        self.assertEqual(loaded["sha256"], objective.EXPECTED_PROBE_SHA256)
        self.assertEqual(loaded["layer_id"], 14)
        self.assertEqual(loaded["layer_index"], 13)
        self.assertEqual(loaded["train_size"], 920)
        self.assertEqual(loaded["arrays"]["coef"].shape, (1536,))
        self.assertEqual(loaded["arrays"]["coef"].dtype, np.float64)

    def test_hash_mismatch_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            objective.load_frozen_l14_probe(
                self.artifact, expected_sha256="0" * 64
            )


class ObjectiveTest(unittest.TestCase):
    def test_masked_mean_excludes_prompt_and_end_marker(self) -> None:
        hidden = torch.tensor([[[100.0], [2.0], [4.0], [999.0]]])
        mask = torch.tensor([[False, True, True, False]])
        actual = objective.masked_response_mean(hidden, mask)
        torch.testing.assert_close(actual, torch.tensor([[3.0]]))

    def test_reference_center_detaches_base(self) -> None:
        adapter = torch.tensor([0.25], requires_grad=True)
        base = torch.tensor([-0.75], requires_grad=True)
        delta = objective.reference_centered_delta(adapter, base)
        loss = objective.bounded_margin_loss(
            delta, torch.tensor([1.0]), margin=0.5
        )
        loss.backward()
        self.assertIsNotNone(adapter.grad)
        self.assertIsNone(base.grad)

    def test_margin_orientation_and_sign_symmetry(self) -> None:
        delta = torch.tensor([-1.0, 0.0, 0.25, 0.5, 1.0])
        positive = torch.ones_like(delta)
        loss = objective.bounded_margin_loss(delta, positive, margin=0.5)
        expected = torch.tensor([(1.5**2), (0.5**2), (0.25**2), 0.0, 0.0]).mean()
        torch.testing.assert_close(loss, expected)
        mirrored = objective.bounded_margin_loss(-delta, -positive, margin=0.5)
        torch.testing.assert_close(loss, mirrored)

    def test_margin_stops_overpush_but_keeps_wrong_direction_gradient(self) -> None:
        reached = torch.tensor([0.75], requires_grad=True)
        reached_loss = objective.bounded_margin_loss(
            reached, torch.tensor([1.0]), margin=0.5
        )
        reached_loss.backward()
        self.assertEqual(float(reached_loss), 0.0)
        self.assertEqual(float(reached.grad), 0.0)

        wrong = torch.tensor([-10.0], requires_grad=True)
        wrong_loss = objective.bounded_margin_loss(
            wrong, torch.tensor([1.0]), margin=0.5
        )
        wrong_loss.backward()
        self.assertGreater(float(wrong_loss), 100.0)
        self.assertLess(float(wrong.grad), 0.0)

    def test_zero_ratio_is_exact_ce_control_on_identical_path(self) -> None:
        ce = torch.tensor(1.25, requires_grad=True)
        aux = torch.tensor(9.0, requires_grad=True)
        combined = objective.combined_objective(ce, aux, 0.0)
        self.assertEqual(float(combined), float(ce))
        combined.backward()
        self.assertEqual(float(ce.grad), 1.0)
        self.assertEqual(float(aux.grad), 0.0)
        weight, record = objective.calibrated_aux_weight_from_microbatches(
            [], [], target_ratio=0.0
        )
        self.assertEqual(weight, 0.0)
        self.assertEqual(record["achieved_median_ratio"], 0.0)

    def test_gradient_ratio_targets_are_exact(self) -> None:
        ce = [1.0, 2.0, 4.0, 8.0]
        aux = [2.0, 2.0, 2.0, 2.0]
        weight_005, record_005 = objective.calibrated_aux_weight_from_microbatches(
            ce, aux, target_ratio=0.05
        )
        weight_010, record_010 = objective.calibrated_aux_weight_from_microbatches(
            ce, aux, target_ratio=0.10
        )
        self.assertAlmostEqual(weight_010, 2 * weight_005)
        self.assertAlmostEqual(record_005["achieved_median_ratio"], 0.05)
        self.assertAlmostEqual(record_010["achieved_median_ratio"], 0.10)
        with self.assertRaises(ValueError):
            objective.validate_gradient_ratio(0.20)

    def test_role_sign_mapping(self) -> None:
        self.assertEqual(objective.role_target("confident"), 1.0)
        self.assertEqual(objective.role_target("hesitant"), -1.0)
        with self.assertRaises(ValueError):
            objective.role_target("unknown")

    def test_only_lora_parameters_may_be_trainable(self) -> None:
        lora_a = torch.nn.Parameter(torch.tensor(1.0))
        lora_b = torch.nn.Parameter(torch.tensor(1.0))
        frozen = torch.nn.Parameter(torch.tensor(1.0), requires_grad=False)
        names = objective.assert_lora_only_trainable(
            [
                ("base.q_proj.lora_A.default.weight", lora_a),
                ("base.q_proj.lora_B.default.weight", lora_b),
                ("base.weight", frozen),
            ]
        )
        self.assertEqual(len(names), 2)
        with self.assertRaisesRegex(ValueError, "non-LoRA"):
            objective.assert_lora_only_trainable(
                [("base.weight", torch.nn.Parameter(torch.tensor(1.0)))]
            )


if __name__ == "__main__":
    unittest.main()
