from __future__ import annotations

import tempfile
from pathlib import Path
import unittest

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

import run_probe_learning_curve as runner


def rows(prefix: str, n: int, group_offset: int) -> list[dict]:
    return [
        {
            "id": f"{prefix}-{i:04d}",
            "source_id": f"source-{prefix}-{i:04d}",
            "group_id": f"group-{group_offset + i // 2:04d}",
            "question": f"Question {prefix} {i}?",
            "confident_response": "This is the confident response.",
            "hesitant_response": "This may be the hesitant response.",
            "task": "factual_explanation",
            "length_bin": ("short", "medium", "long")[i % 3],
            "target_longer_role": ("confident", "hesitant")[i % 2],
            "source_collection": prefix,
            "atomic_group_id": f"atomic-{prefix}-{i // 4:03d}",
            "original_record_sha256": f"{group_offset + i:064x}",
        }
        for i in range(n)
    ]


def synthetic_states(n: int, seed: int, dimensions: int = 10) -> np.ndarray:
    rng = np.random.default_rng(seed)
    base = rng.normal(size=(n, 1, 28, dimensions))
    states = np.repeat(base, 2, axis=1)
    # Every split shares the same latent confidence direction; only examples
    # and noise differ across split seeds.
    direction = np.random.default_rng(999).normal(size=(28, dimensions))
    direction /= np.linalg.norm(direction, axis=1, keepdims=True)
    strengths = np.linspace(0.35, 1.0, 28)[None, None, :, None]
    states[:, 0:1] += strengths * direction[None, None]
    states[:, 1:2] -= strengths * direction[None, None]
    states += rng.normal(scale=0.18, size=states.shape)
    return states.astype(np.float32)


def bundle_arrays(rows_: list[dict], states: np.ndarray) -> dict[str, np.ndarray]:
    response_hashes = np.asarray([
        [runner.response_content_sha256(row, "confident"),
         runner.response_content_sha256(row, "hesitant")]
        for row in rows_
    ])
    bindings = np.asarray([
        [runner.state_binding_sha256(states[i, axis], response_hashes[i, axis])
         for axis in range(2)]
        for i in range(len(rows_))
    ])
    return {
        "pair_ids": np.asarray([row["id"] for row in rows_]),
        "pair_content_sha256": np.asarray([
            runner.pair_content_sha256(row) for row in rows_]),
        "pair_order": np.asarray(["confident", "hesitant"]),
        "response_content_sha256": response_hashes,
        "state_binding_sha256": bindings,
        "states": states,
        "layer_ids": np.arange(1, 29),
        "position": np.asarray("response_mean"),
        "settings_sha256": np.asarray(runner.FEATURE_SETTINGS_SHA256),
        "model_id": np.asarray(runner.MODEL_ID),
        "model_revision": np.asarray(runner.MODEL_REVISION),
    }


class RunnerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.split_rows = {
            "train": rows("train", 30, 0),
            "dev": rows("dev", 12, 100),
            "internal_test": rows("test", 10, 200),
            "external_cf3": rows("external", 8, 300),
        }
        self.split_states = {
            "train": synthetic_states(30, 1),
            "dev": synthetic_states(12, 2),
            "internal_test": synthetic_states(10, 3),
            "external_cf3": synthetic_states(8, 4),
        }

    def test_learning_curve_and_equal28(self) -> None:
        result = runner.run_learning_curve(
            self.split_rows, self.split_states,
            train_sizes=(10, 20, 30), bootstrap_replicates=25,
        )
        self.assertEqual(set(result["learning_curves"]), {"10", "20", "30"})
        final = result["learning_curves"]["30"]
        self.assertEqual(len(final["layerwise"]["dev"]), 28)
        self.assertGreater(final["ensemble"]["dev"]["paired_accuracy"], 0.8)
        self.assertGreater(final["primary_layer"]["internal_test"]["paired_accuracy"], 0.7)
        self.assertIn("10_vs_30", result["direction_stability"])

    def test_exact_symmetric_logistic_and_equal28_formula(self) -> None:
        states = self.split_states["train"][:20]
        fitted = runner.fit_paired_layer_readouts(states)
        layer = 13
        response_states = states[:, :, layer, :].astype(np.float64).reshape(-1, states.shape[-1])
        scaler = StandardScaler().fit(response_states)
        z = scaler.transform(response_states).reshape(len(states), 2, states.shape[-1])
        delta = z[:, 0] - z[:, 1]
        symmetric = np.concatenate([delta, -delta])
        labels = np.concatenate([np.ones(len(states)), np.zeros(len(states))])
        expected_model = LogisticRegression(
            C=0.01, fit_intercept=False, solver="lbfgs", max_iter=2000,
            random_state=0,
        ).fit(symmetric, labels, sample_weight=np.full(2 * len(states), 0.5))
        np.testing.assert_allclose(fitted.feature_mean[layer], scaler.mean_, rtol=0, atol=0)
        np.testing.assert_allclose(fitted.feature_scale[layer], scaler.scale_, rtol=0, atol=0)
        np.testing.assert_allclose(fitted.coef[layer], expected_model.coef_[0], rtol=1e-12, atol=1e-12)
        all_scores = runner.layer_scores(fitted, self.split_states["dev"])
        manual_equal = runner.train_standardized_scores(fitted, all_scores).mean(axis=2)
        np.testing.assert_allclose(
            runner.equal28_scores(fitted, self.split_states["dev"]),
            manual_equal, rtol=0, atol=0)

    def test_zero_train_score_std_contributes_zero(self) -> None:
        fitted = runner.FittedReadouts(
            feature_mean=np.zeros((28, 2)), feature_scale=np.ones((28, 2)),
            coef=np.ones((28, 2)), train_score_mean=np.arange(28, dtype=float),
            train_score_std=np.ones(28),
        )
        fitted.train_score_std[7] = 0.0
        scores = np.ones((3, 2, 28)) * 4.0
        standardized = runner.train_standardized_scores(fitted, scores)
        np.testing.assert_array_equal(standardized[:, :, 7], 0.0)
        np.testing.assert_allclose(standardized[:, :, 0], 4.0)

    def test_provider_batch_sensitivity_uses_atomic_group(self) -> None:
        subset = self.split_rows["dev"]
        scores = np.column_stack([np.ones(len(subset)), np.zeros(len(subset))])
        metrics = runner.score_metrics(scores, subset, bootstrap_replicates=10)
        self.assertEqual(
            metrics["provider_batch_group_count"],
            len({row["atomic_group_id"] for row in subset}),
        )
        self.assertEqual(metrics["provider_batch_group_count"], 3)

    def test_split_freeze_digest_tamper_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "SPLIT_FREEZE.json"
            path.write_text("{}\n", encoding="utf-8")
            with self.assertRaisesRegex(runner.ContractError, "SHA-256"):
                runner.load_split_freeze(path, {})

    def test_split_leakage_fails_closed(self) -> None:
        self.split_rows["dev"][0]["group_id"] = self.split_rows["train"][0]["group_id"]
        with self.assertRaisesRegex(runner.ContractError, "group_id leakage"):
            runner.validate_split_rows(
                self.split_rows, expected_counts=None, train_sizes=(10, 20, 30))

    def test_exact_question_leakage_fails_closed(self) -> None:
        self.split_rows["train"][0]["question"] = "Question Ａ?"
        self.split_rows["dev"][0]["question"] = "  QUESTION A? "
        with self.assertRaisesRegex(runner.ContractError, "normalized-question leakage"):
            runner.validate_split_rows(
                self.split_rows, expected_counts=None, train_sizes=(10, 20, 30))

    def test_activation_bundle_reorders_by_pair_id(self) -> None:
        subset = self.split_rows["dev"]
        states = self.split_states["dev"]
        order = np.arange(len(subset))[::-1]
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "bundle.npz"
            shuffled_rows = [subset[i] for i in order]
            np.savez_compressed(path, **bundle_arrays(shuffled_rows, states[order]))
            loaded, audit = runner.load_activation_bundle(
                path, subset, expected_hidden_size=states.shape[-1])
        np.testing.assert_array_equal(loaded, states)
        self.assertEqual(audit["pairs"], len(subset))

    def test_activation_id_mismatch_fails_closed(self) -> None:
        subset = self.split_rows["external_cf3"]
        states = self.split_states["external_cf3"]
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "bundle.npz"
            arrays = bundle_arrays(subset, states)
            arrays["pair_ids"] = arrays["pair_ids"].copy()
            arrays["pair_ids"][0] = "wrong-id"
            np.savez_compressed(path, **arrays)
            with self.assertRaisesRegex(runner.ContractError, "IDs do not match"):
                runner.load_activation_bundle(path, subset, expected_hidden_size=states.shape[-1])

    def test_activation_exact_text_mismatch_fails_closed(self) -> None:
        subset = self.split_rows["dev"]
        states = self.split_states["dev"]
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "bundle.npz"
            np.savez_compressed(path, **bundle_arrays(subset, states))
            changed = [dict(row) for row in subset]
            changed[0]["hesitant_response"] += " Changed."
            with self.assertRaisesRegex(runner.ContractError, "content hashes"):
                runner.load_activation_bundle(path, changed, expected_hidden_size=states.shape[-1])

    def test_activation_axis_swap_fails_closed(self) -> None:
        subset = self.split_rows["internal_test"]
        states = self.split_states["internal_test"]
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "bundle.npz"
            arrays = bundle_arrays(subset, states)
            arrays["states"] = states[:, ::-1].copy()
            np.savez_compressed(path, **arrays)
            with self.assertRaisesRegex(runner.ContractError, "state/response binding"):
                runner.load_activation_bundle(path, subset, expected_hidden_size=states.shape[-1])

    def test_activation_pair_order_tamper_fails_closed(self) -> None:
        subset = self.split_rows["external_cf3"]
        states = self.split_states["external_cf3"]
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "bundle.npz"
            arrays = bundle_arrays(subset, states)
            arrays["pair_order"] = np.asarray(["hesitant", "confident"])
            np.savez_compressed(path, **arrays)
            with self.assertRaisesRegex(runner.ContractError, "response axis"):
                runner.load_activation_bundle(path, subset, expected_hidden_size=states.shape[-1])


if __name__ == "__main__":
    unittest.main()
