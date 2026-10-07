"""Meaningful isolation, source-grouping, geometry and margin-scale checks."""
import copy
import json
import unittest

import numpy as np

from confidence_pilot.separation_audit import (
    REPRESENTATIONS, analyze_separation, contrast_bundles, correctness_subspace,
    paired_change, source_metric, training_directions, v1_bundles,
)


def fixture():
    rows, vectors = [], []
    for source in range(18):
        split = "train" if source < 12 else "validation" if source < 15 else "test"
        for family in ("A", "B", "C"):
            for correct in ("correct", "incorrect"):
                for certainty in ("confident", "hedged"):
                    prefix = f"s{source}-{family}-{correct}"
                    other = "hedged" if certainty == "confident" else "confident"
                    rows.append({"source_id": f"s{source}", "split": split, "domain": f"domain{source % 3}",
                        "variant_id": f"{prefix}-{certainty}", "paired_variant_id": f"{prefix}-{other}",
                        "correctness": correct, "certainty": certainty, "rewrite_family": family})
                    vector = np.zeros((2, 4, 8), dtype=float)
                    vector[:, :3, 0] = 1. if certainty == "confident" else -1.
                    sign = 1. if correct == "correct" else -1.
                    vector[:, :3, 1] = sign * (1. + source * .01)
                    vector[:, :3, 2] = source / 10
                    vector[:, :3, 3] = sign * .1 * (source % 3 - 1)
                    vector[:, :3, 4] = sign * .03 * (source % 2 - .5)
                    vectors.append(vector)
    v1 = np.stack(vectors)
    v2rows, v2hidden = [], []
    for source in range(6):
        common = {"source_id": f"v2-{source}", "fact_type": f"type{source % 2}", "split": "test",
                  "token_count": 3, "char_count": 12, "prompt_token_count": 10,
                  "response_ids": [1, 2, 3], "response_text": "fixed answer"}
        for correct in ("correct", "incorrect"):
            for certainty in ("confident", "hedged"):
                prefix = f"v2-{source}-{correct}"
                other = "hedged" if certainty == "confident" else "confident"
                v2rows.append({**common, "variant_id": f"{prefix}-{certainty}", "paired_variant_id": f"{prefix}-{other}",
                               "experiment": "natural_style", "correctness": correct, "certainty": certainty})
                vector = np.zeros((2, 4, 8))
                vector[:, :3, 0] = 1. if certainty == "confident" else -1.
                vector[:, :3, 1] = 1. if correct == "correct" else -1.
                v2hidden.append(vector)
        for fmt in ("qa", "document"):
            for condition, value in (("supported", 1.), ("omitted", 0.), ("conflicting", -1.)):
                v2rows.append({**common, "variant_id": f"v2-{source}-{fmt}-{condition}", "experiment": "neutral_evidence",
                               "format": fmt, "condition": condition, "correctness": "correct", "certainty": "neutral"})
                vector = np.zeros((2, 4, 8))
                vector[:, :3, 0] = value
                v2hidden.append(vector)
    frozen = training_directions(rows, v1)
    frozen["correctness"] = frozen["layer14_boundary_correctness"].copy()
    confidence, correctness = frozen["layer14_boundary"], frozen["correctness"]
    residual = confidence - (confidence @ correctness) * correctness
    frozen["confidence_projected"] = residual / np.linalg.norm(residual)
    return rows, v1, v2rows, np.stack(v2hidden), frozen


CONFIG = {"analysis": {"bootstrap_samples": 60, "split_half_repetitions": 30,
                       "random_subspace_repetitions": 20, "seed": 17}}


class SeparationAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = fixture()
        cls.result, cls.directions = analyze_separation(*cls.fixture, CONFIG)

    def test_four_cell_paired_correctness_is_separate_from_certainty(self):
        primary = self.result["representations"]["layer14_boundary"]["cross_readout"]
        self.assertEqual(primary["confidence"]["certainty"]["accuracy"], 1.)
        self.assertEqual(primary["confidence"]["correctness"]["accuracy"], .5)
        self.assertEqual(primary["correctness"]["correctness"]["accuracy"], 1.)
        self.assertEqual(primary["correctness"]["certainty"]["accuracy"], .5)
        for style in ("confident", "hedged"):
            self.assertEqual(primary["correctness"]["correctness"]["by_certainty_style"][style]["accuracy"], 1.)
        self.assertEqual(self.result["scope"]["test_C_rows"], 12)
        self.assertEqual(primary["correctness"]["correctness"]["n_pairs"], 6)
        self.assertEqual(primary["correctness"]["correctness"]["n_sources"], 3)

    def test_test_validation_and_train_C_never_change_fitted_vectors(self):
        rows, hidden, v2rows, v2hidden, frozen = self.fixture
        altered = hidden.copy()
        for i, row in enumerate(rows):
            if row["split"] != "train" or row["rewrite_family"] == "C":
                altered[i, :, :3] = -100 * altered[i, :, :3]
        v2altered = -100 * v2hidden
        result, directions = analyze_separation(rows, altered, v2rows, v2altered, frozen, CONFIG)
        for name in self.directions:
            np.testing.assert_allclose(self.directions[name], directions[name], atol=1e-12, rtol=0)
        self.assertEqual(result["representations"]["layer14_boundary"]["cross_readout"]["confidence"]["certainty"]["accuracy"], 0.)

    def test_source_metric_pairs_do_not_become_independent_units(self):
        first = source_metric(np.asarray([[1., 2.], [-1., -2.]]), ["a", "b"], 100, 10)
        repeated = source_metric(np.asarray([[1., 2.] * 20, [-1., -2.] * 20]), ["a", "b"], 100, 10)
        self.assertEqual(first["accuracy"], .5)
        self.assertEqual(first["bootstrap_95"], repeated["bootstrap_95"])
        self.assertEqual(first["margin_bootstrap_95"], repeated["margin_bootstrap_95"])

    def test_projection_changes_margins_on_the_original_scale(self):
        raw = np.asarray([[2., 4.], [6., 8.]])
        result = paired_change(raw, raw * .5, ["a", "b"], 100, 10)
        self.assertEqual(result["accuracy_difference"], 0.)
        self.assertEqual(result["mean_margin_difference"], -2.5)
        self.assertEqual(result["margin_difference_bootstrap_95"], {"lower": -3.5, "upper": -1.5})

    def test_gram_svd_is_orthonormal_and_uses_uncentered_source_contrasts(self):
        matrix = np.asarray([[3., 1., 0.], [3., -1., 0.], [3., 0., .5]])
        basis, spectrum = correctness_subspace(matrix, 3)
        np.testing.assert_allclose(basis @ basis.T, np.eye(3), atol=1e-12)
        expected = np.linalg.svd(matrix, compute_uv=False)**2 / len(matrix)
        np.testing.assert_allclose(spectrum, expected, atol=1e-12)
        self.assertGreater(abs(basis[0, 0]), .99)

    def test_saved_directions_and_lowrank_projection_leave_fresh_labels_unfitted(self):
        for representation in REPRESENTATIONS:
            self.assertIn(representation + "_correctness", self.directions)
        for rank, entry in self.result["correctness_lowrank_subspace"]["rank_candidates"].items():
            self.assertLess(entry["residual_confidence_norm"], 1. + 1e-12)
            self.assertEqual(entry["matched_rank_random_control"]["n_repetitions"], 20)
        self.assertTrue(self.result["checks"]["no_test_or_v2_fitting"])
        self.assertEqual(self.result["representations"]["layer14_boundary"]["training_and_test_refit_bootstrap"]["n_repetitions"], 60)
        self.assertEqual(self.result["v2_rank1_projection"]["training_and_test_refit_bootstrap"]["n_repetitions"], 60)
        json.dumps(self.result, allow_nan=False)

    def test_missing_cells_bad_links_and_source_leakage_are_rejected(self):
        rows, hidden, *_ = self.fixture
        with self.assertRaises(ValueError):
            v1_bundles(rows[:-1], hidden[:-1])
        changed = copy.deepcopy(rows)
        changed[0]["split"] = "test"
        with self.assertRaisesRegex(ValueError, "Source leakage|pair links"):
            v1_bundles(changed, hidden)
        changed = copy.deepcopy(rows)
        changed[0]["paired_variant_id"] = "missing"
        with self.assertRaisesRegex(ValueError, "Missing certainty partner"):
            v1_bundles(changed, hidden)

    def test_neutral_response_mismatch_and_mutated_frozen_direction_rejected(self):
        rows, hidden, v2rows, v2hidden, frozen = self.fixture
        changed = copy.deepcopy(v2rows)
        changed[5]["response_text"] = "changed answer"
        with self.assertRaisesRegex(ValueError, "response_text"):
            analyze_separation(rows, hidden, changed, v2hidden, frozen, CONFIG)
        bad = copy.deepcopy(frozen)
        bad["layer14_boundary"][0] *= -1
        with self.assertRaisesRegex(ValueError, "Frozen v1 confidence mismatch"):
            analyze_separation(rows, hidden, v2rows, v2hidden, bad, CONFIG)


if __name__ == "__main__":
    unittest.main()
