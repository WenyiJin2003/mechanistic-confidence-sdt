"""Checks for source weighting, fitting isolation and paired control semantics."""

import copy
import json
import unittest

import numpy as np

from confidence_pilot.analyze_pairs import analyze_pairs, grouped_pair_metric


def synthetic_dataset(families=("A", "B", "C")):
    rows = []
    vectors = []
    for source_index in range(12):
        source_id = f"source-{source_index}"
        split = "train" if source_index < 6 else "validation" if source_index < 9 else "test"
        domain = ("factual_qa", "arithmetic", "academic")[source_index % 3]
        for family in families:
            for correctness in ("correct", "incorrect"):
                prefix = f"{source_id}-{family}-{correctness}"
                for certainty in ("confident", "hedged"):
                    variant_id = f"{prefix}-{certainty}"
                    other = "hedged" if certainty == "confident" else "confident"
                    style = "I am confident answer" if certainty == "confident" else "I am uncertain answer"
                    text = f"{style} {source_index} {correctness}"
                    rows.append({
                        "variant_id": variant_id,
                        "paired_variant_id": f"{prefix}-{other}",
                        "source_id": source_id,
                        "split": split,
                        "domain": domain,
                        "correctness": correctness,
                        "certainty": certainty,
                        "rewrite_family": family,
                        "subtype": f"{family}-{source_index % 2}",
                        "response_text": text,
                        "token_count": 8,
                        "char_count": len(text),
                        "sequence_nll": 2.0 if certainty == "confident" else 4.0,
                        "mean_token_nll": 0.25 if certainty == "confident" else 0.5,
                    })
                    vector = np.zeros((2, 4, 1536), dtype=np.float32)
                    # Confidence and correctness occupy independent dimensions.
                    vector[:, :3, 0] = 1 if certainty == "confident" else -1
                    vector[:, :3, 1] = 2 if correctness == "correct" else -2
                    vector[:, :, 2] = source_index / 10
                    vector[:, 3, 0] = 0
                    vector[:, 3, 1] = 0
                    vectors.append(vector)
    return rows, np.stack(vectors)


def fast_config(phase="A"):
    return {"phase": phase, "analysis": {
        "seed": 42, "bootstrap_seed": 43, "bootstrap_samples": 60,
        "null_repetitions": 40, "random_directions": 40,
        "minimum_length_subset_sources": 2,
    }}


class GroupedMetricTests(unittest.TestCase):
    def test_unequal_pair_counts_do_not_weight_large_source_more(self):
        values = np.asarray([1.] * 20 + [0.])
        sources = ["large"] * 20 + ["small"]
        result = grouped_pair_metric(values, sources, bootstrap_samples=200, seed=3)
        self.assertEqual(result["accuracy"], 0.5)
        self.assertEqual(result["n_sources"], 2)
        self.assertEqual(result["bootstrap_95"], {"lower": 0., "upper": 1.})

    def test_difference_metric_uses_same_source_bundles(self):
        result = grouped_pair_metric(np.asarray([0.25, -0.25]), ["a", "b"], bootstrap_samples=100)
        self.assertEqual(result["accuracy"], 0.)
        self.assertEqual(result["bootstrap_95"]["lower"], -0.25)
        self.assertEqual(result["bootstrap_95"]["upper"], 0.25)


class PairedAnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows, cls.hidden = synthetic_dataset()
        cls.result = analyze_pairs(cls.rows, cls.hidden, fast_config())

    def test_perfect_known_direction_and_correctness_strata(self):
        result = self.result
        self.assertEqual(result["primary"]["primary"]["accuracy"], 1.)
        self.assertEqual(result["primary"]["primary"]["n_sources"], 3)
        self.assertEqual(result["primary"]["primary"]["n_pairs"], 12)
        for correctness in ("correct", "incorrect"):
            self.assertEqual(result["primary"]["primary_strata"]["correctness"][correctness]["accuracy"], 1.)
        direction = np.asarray(result["directions"]["layer14_boundary"])
        np.testing.assert_array_equal(direction[:3], [1., 0., 0.])

    def test_prompt_control_ties_and_random_antipodes(self):
        prompt = self.result["controls"]["negative_prompt"]
        self.assertTrue(prompt["identical_within_tolerance"])
        self.assertFalse(prompt["direction_defined"])
        self.assertEqual(prompt["metrics"]["primary"]["accuracy"], 0.5)
        random = self.result["controls"]["matched_random_antipodal"]
        self.assertEqual(random["mean"], 0.5)
        # Fixed-template nulls are allowed to be perfect and perfectly wrong.
        self.assertEqual(random["minimum"], 0.)
        self.assertEqual(random["maximum"], 1.)

    def test_orthogonal_correctness_projection_preserves_signal(self):
        projection = self.result["correctness_projection"]
        self.assertEqual(projection["cosine_similarity"], 0.)
        self.assertEqual(projection["metrics"]["primary"]["accuracy"], 1.)
        self.assertEqual(projection["projected_minus_original"]["accuracy_difference"], 0.)

    def test_no_test_or_family_C_information_enters_fitted_direction(self):
        modified = self.hidden.copy()
        for i, row in enumerate(self.rows):
            if row["split"] != "train" or row["rewrite_family"] == "C":
                modified[i, :, :3, 0] *= -1
                modified[i, :, :3, 1] += 100
        result = analyze_pairs(self.rows, modified, fast_config())
        for name in self.result["directions"]:
            np.testing.assert_array_equal(result["directions"][name], self.result["directions"][name])
        self.assertEqual(result["primary"]["primary"]["accuracy"], 0.)

    def test_phase_B_uses_unseen_C_on_fresh_test_sources(self):
        modified = self.hidden.copy()
        for i, row in enumerate(self.rows):
            if row["rewrite_family"] == "C":
                modified[i, :, :3, 0] *= -1
        result = analyze_pairs(self.rows, modified, fast_config("B"))
        self.assertEqual(result["primary_endpoint"]["families"], ["C"])
        self.assertEqual(result["primary"]["primary"]["n_pairs"], 6)
        self.assertEqual(result["primary"]["primary"]["accuracy"], 0.)
        self.assertEqual(result["primary"]["by_split"]["test"]["by_family"]["A"]["accuracy"], 1.)
        self.assertFalse(result["gates"]["statistical_passed"])

    def test_numeric_and_text_baselines_do_not_fit_C_or_test_rows(self):
        modified = copy.deepcopy(self.rows)
        for row in modified:
            if row["split"] != "train" or row["rewrite_family"] == "C":
                row["response_text"] = "unseenword " * 20
                row["sequence_nll"] += 1000
                row["mean_token_nll"] += 100
                row["token_count"] += 200
                row["char_count"] += 2000
        result = analyze_pairs(modified, self.hidden, fast_config())
        train_indices = [i for i, row in enumerate(self.rows) if row["split"] == "train" and row["rewrite_family"] in {"A", "B"}]
        for name in self.result["baselines"]:
            np.testing.assert_allclose(
                np.asarray(result["scores"][name])[train_indices],
                np.asarray(self.result["scores"][name])[train_indices],
                rtol=0, atol=1e-12,
            )
        self.assertEqual(result["baselines"]["text_tfidf"]["vocabulary_size"], self.result["baselines"]["text_tfidf"]["vocabulary_size"])

    def test_collinear_correctness_projection_becomes_tied(self):
        modified = self.hidden.copy()
        modified[:, :, :3, 0] += modified[:, :, :3, 1]
        modified[:, :, :3, 1] = 0
        result = analyze_pairs(self.rows, modified, fast_config())
        projection = result["correctness_projection"]
        self.assertEqual(projection["cosine_similarity"], 1.)
        self.assertFalse(projection["projected_direction_defined"])
        self.assertEqual(projection["metrics"]["primary"]["accuracy"], 0.5)

    def test_gate_rejects_confidence_signal_only_for_correct_answers(self):
        modified = self.hidden.copy()
        for i, row in enumerate(self.rows):
            if row["correctness"] == "incorrect":
                modified[i, :, :3, 0] = 0
        result = analyze_pairs(self.rows, modified, fast_config())
        self.assertEqual(result["primary"]["primary_strata"]["correctness"]["incorrect"]["accuracy"], 0.5)
        self.assertFalse(result["gates"]["checks"]["both_correctness_cells_above_chance"])

    def test_prompt_variation_is_flagged_even_if_pair_mean_cancels(self):
        modified = self.hidden.copy()
        modified[0, 0, 3, 0] += 0.1
        result = analyze_pairs(self.rows, modified, fast_config())
        self.assertFalse(result["controls"]["negative_prompt"]["identical_within_tolerance"])
        self.assertFalse(result["gates"]["checks"]["prompt_negative_control_passed"])

    def test_source_leakage_and_bad_pair_links_rejected(self):
        rows = copy.deepcopy(self.rows)
        rows[0]["split"] = "test"
        with self.assertRaisesRegex(ValueError, "Source leakage"):
            analyze_pairs(rows, self.hidden, fast_config())
        rows = copy.deepcopy(self.rows)
        rows[0]["paired_variant_id"] = "missing"
        with self.assertRaisesRegex(ValueError, "Missing partner"):
            analyze_pairs(rows, self.hidden, fast_config())

    def test_json_serialization_and_row_aligned_scores(self):
        json.dumps(self.result, allow_nan=False)
        self.assertEqual(self.result["variant_ids"], [row["variant_id"] for row in self.rows])
        for scores in self.result["scores"].values():
            self.assertEqual(len(scores), len(self.rows))


if __name__ == "__main__":
    unittest.main()
