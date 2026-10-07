"""Focused checks for frozen transfer evaluation and source-level gates."""
import copy
import json
import unittest

import numpy as np

from confidence_pilot.transfer_analysis_v2 import analyze_transfer


def fixture():
    rows, hidden = [], []
    for source in range(8):
        common = {"source_id": f"s{source}", "fact_type": f"type{source % 4}", "split": "test", "wording_id": f"w{source % 2}", "format": "qa", "token_count": 5, "char_count": 20, "prompt_token_count": 40, "response_ids": [1, 2, 3, 4, 5]}
        for correctness in ("correct", "incorrect"):
            for certainty in ("confident", "hedged"):
                prefix = f"s{source}-{correctness}"
                other = "hedged" if certainty == "confident" else "confident"
                row = {**common, "variant_id": f"{prefix}-{certainty}", "paired_variant_id": f"{prefix}-{other}", "experiment": "natural_style", "correctness": correctness, "certainty": certainty, "sequence_nll": 1., "mean_token_nll": .2, "tfidf_score": float(certainty == "confident"), "char_tfidf_score": float(certainty == "confident")}
                rows.append(row)
                vector = np.zeros((2, 4, 1536), dtype=np.float32)
                vector[:, :3, 0] = 1. if certainty == "confident" else -1.
                hidden.append(vector)
        for fmt in ("qa", "document"):
            for condition, score, nll in (("supported", 1., .1), ("omitted", 0., .3), ("conflicting", -1., .5)):
                rows.append({**common, "variant_id": f"s{source}-{fmt}-{condition}", "experiment": "neutral_evidence", "format": fmt, "condition": condition, "correctness": "correct", "certainty": "neutral", "sequence_nll": nll * 5, "mean_token_nll": nll, "tfidf_score": .7, "char_tfidf_score": .9})
                vector = np.zeros((2, 4, 1536), dtype=np.float32)
                vector[:, :3, 0] = score
                # Context-dependent prompt states are expected and permitted.
                vector[:, 3, 0] = score
                hidden.append(vector)
    direction = np.zeros(1536)
    direction[0] = 1.
    directions = {key: direction.copy() for key in ("layer14_boundary", "layer14_final_content", "layer14_response_mean", "layer23_boundary", "confidence_projected", "correctness")}
    directions["random_controls"] = np.stack([direction, -direction])
    directions["shuffled_controls"] = np.stack([direction, -direction])
    return rows, np.stack(hidden), directions


CONFIG = {"analysis": {"bootstrap_samples": 100, "bootstrap_seed": 43}}


class TransferAnalysisTests(unittest.TestCase):
    def test_source_units_ties_baselines_nulls_and_serialization(self):
        rows, hidden, directions = fixture()
        result = analyze_transfer(rows, hidden, directions, CONFIG)
        self.assertTrue(result["gates"]["bridge_promising"])
        self.assertEqual(result["primary"]["natural_style"]["n_pairs"], 16)
        self.assertEqual(result["primary"]["natural_style"]["n_sources"], 8)
        self.assertEqual(result["primary"]["neutral_qa_supported_vs_omitted"]["n_pairs"], 8)
        for name in ("text_tfidf", "char_tfidf", "token_length", "character_length"):
            self.assertEqual(result["baselines"][name]["endpoints"]["neutral_qa_supported_vs_omitted"]["accuracy"], .5)
        self.assertEqual(result["controls"]["random_controls"]["endpoints"]["natural_style"]["values"], [1., 0.])
        self.assertEqual(result["paired_comparisons"]["text_tfidf"]["neutral_qa_supported_vs_omitted"]["accuracy_difference"], -.5)
        self.assertEqual(result["primary"]["natural_style"]["length_subsets"]["token_matched_within_one"]["n_sources"], 8)
        json.dumps(result, allow_nan=False)
        for scores in result["scores"].values():
            self.assertEqual(len(scores), len(rows))

    def test_new_outcomes_do_not_change_frozen_vectors(self):
        rows, hidden, directions = fixture()
        before = copy.deepcopy(directions)
        first = analyze_transfer(rows, hidden, directions, CONFIG)
        altered = hidden.copy()
        altered[:, :, :3, 0] *= -1
        second = analyze_transfer(rows, altered, directions, CONFIG)
        self.assertEqual(first["frozen_direction_sha256"], second["frozen_direction_sha256"])
        self.assertEqual(second["primary"]["natural_style"]["accuracy"], 0.)
        self.assertFalse(second["gates"]["bridge_promising"])
        for key in directions:
            np.testing.assert_array_equal(directions[key], before[key])

    def test_failed_likelihood_manipulation_is_inconclusive(self):
        rows, hidden, directions = fixture()
        for row in rows:
            row["mean_token_nll"] = .2
        result = analyze_transfer(rows, hidden, directions, CONFIG)
        self.assertTrue(result["gates"]["statistical_passed"])
        self.assertTrue(result["gates"]["evidence_inconclusive"])
        self.assertFalse(result["gates"]["bridge_promising"])

    def test_missing_neutral_condition_fails(self):
        rows, hidden, directions = fixture()
        with self.assertRaisesRegex(ValueError, "Incomplete source conditions"):
            analyze_transfer(rows[:-1], hidden[:-1], directions, CONFIG)
        changed = copy.deepcopy(rows)
        changed[6]["condition"] = "supported"
        with self.assertRaisesRegex(ValueError, "Missing neutral conditions"):
            analyze_transfer(changed, hidden, directions, CONFIG)

    def test_matching_ids_lengths_and_test_only_requirement(self):
        rows, hidden, directions = fixture()
        for field, value in (("response_ids", [9]), ("prompt_token_count", 41), ("split", "train")):
            changed = copy.deepcopy(rows)
            changed[5][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                analyze_transfer(changed, hidden, directions, CONFIG)

    def test_incorrect_style_cannot_be_rescued_by_secondary_positions(self):
        rows, hidden, directions = fixture()
        for i, row in enumerate(rows):
            if row["experiment"] == "natural_style" and row["correctness"] == "incorrect":
                hidden[i, 0, 0, 0] = 0.
        result = analyze_transfer(rows, hidden, directions, CONFIG)
        self.assertFalse(result["gates"]["natural_style_passed"])
        self.assertEqual(result["representations"]["layer14_final_content"]["endpoints"]["natural_style"]["accuracy"], 1.)


if __name__ == "__main__":
    unittest.main()
