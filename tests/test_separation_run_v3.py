"""Test factorial pairing and fixed-readout scoring without a language model."""
import copy
import unittest

import numpy as np

from confidence_pilot.separation_run_v3 import ENDPOINTS, REPRESENTATIONS, analyze_separation, endpoint_pairs


def fixture():
    rows, features = [], []
    for source, kind in enumerate(("access_code", "room_assignment", "release_year", "material")):
        for world in ("A", "B", "omitted"):
            for answer in ("A", "B"):
                styles = ("neutral",) if world == "omitted" else ("confident", "hedged", "neutral")
                for style in styles:
                    supported = world == answer
                    correctness = None if world == "omitted" else ("correct" if supported else "incorrect")
                    text = answer + ":" + style
                    rows.append({"source_id": str(source), "variant_id": f"{source}-{world}-{answer}-{style}",
                        "fact_type": kind, "wording_family": "F1", "world": world, "answer_key": answer,
                        "certainty": style, "correctness": correctness, "supplied_support": "absent" if world == "omitted" else ("supported" if supported else "contradicted"),
                        "response_text": text, "response_ids": [1 if answer == "A" else 2],
                        "prompt_token_count": 10, "response_start_position": 10,
                        "final_content_position": 11, "boundary_position": 12, "token_count": 2,
                        "mean_token_nll": 1. if supported else (2. if world == "omitted" else 3.)})
                    h = np.zeros(1536)
                    h[0] = 1 if style == "confident" else (-1 if style == "hedged" else 0)
                    h[1] = 0 if world == "omitted" else (1 if supported else -1)
                    h[2] = 1 if supported else 0
                    features.append(np.tile(h, (2, 4, 1)))
    vectors = {}
    v = np.zeros(1536)
    v[:3] = 1 / np.sqrt(3)
    c = np.zeros(1536)
    c[1] = 1
    residual = v - (v @ c) * c
    for name in REPRESENTATIONS:
        vectors[name] = v.copy()
        vectors[name + "_correctness"] = c.copy()
        vectors[name + "_projected"] = residual / np.linalg.norm(residual)
        vectors[name + "_projected_common_scale"] = residual.copy()
    vectors["random_controls"] = np.stack((c, -c))
    config = {"experiment": "unit_fixture", "analysis": {"bootstrap_seed": 7, "bootstrap_samples": 100,
        "ordering_accuracy_min": .65, "nll_manipulation_accuracy_min": .75,
        "primary_candidates": ["layer14_final_content", "layer14_response_mean"]}}
    return rows, np.stack(features), vectors, config


class SeparationRunTests(unittest.TestCase):
    def test_exact_answer_counterfactual_pairing(self):
        rows, _, _, _ = fixture()
        pairs = endpoint_pairs(rows)
        self.assertEqual({key: len(value) for key, value in pairs.items()},
                         {"certainty_wording": 16, "neutral_true_vs_false": 8, "neutral_supported_vs_omitted": 8})
        for a, b in pairs["neutral_true_vs_false"]:
            self.assertEqual(rows[a]["response_text"], rows[b]["response_text"])
            self.assertEqual(rows[a]["correctness"], "correct")
            self.assertEqual(rows[b]["correctness"], "incorrect")
        for _, b in pairs["neutral_supported_vs_omitted"]:
            self.assertIsNone(rows[b]["correctness"])

    def test_absolute_position_mismatch_rejected(self):
        rows, _, _, _ = fixture()
        rows[0]["boundary_position"] = 99  # wording rows are allowed to vary in length
        neutral = next(row for row in rows if row["world"] == "omitted")
        neutral["boundary_position"] = 99
        with self.assertRaisesRegex(ValueError, "token gate"):
            endpoint_pairs(rows)

    def test_content_mismatch_rejected(self):
        rows, _, _, _ = fixture()
        next(row for row in rows if row["world"] == "omitted")["response_ids"] = [999]
        with self.assertRaisesRegex(ValueError, "token gate"):
            endpoint_pairs(rows)

    def test_incomplete_or_duplicate_cells_rejected(self):
        rows, _, _, _ = fixture()
        with self.assertRaisesRegex(ValueError, "Incomplete"):
            endpoint_pairs(rows[:-1])
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            endpoint_pairs(rows + [copy.deepcopy(rows[0])])

    def test_fixed_readout_metrics_and_source_grouping(self):
        rows, hidden, vectors, config = fixture()
        result = analyze_separation(rows, hidden, vectors, config)
        self.assertTrue(result["manipulation_passed"])
        self.assertTrue(all(x["passed"] for x in result["gates"].values()))
        for name in config["analysis"]["primary_candidates"]:
            for endpoint in ENDPOINTS:
                metric = result["representations"][name][endpoint]
                self.assertEqual(metric["accuracy"], 1.)
                self.assertEqual(metric["n_sources"], 4)
                self.assertEqual(metric["tie_fraction"], 0.)
            null = result["representations"][name]["random_control_distribution"]["neutral_true_vs_false"]
            self.assertAlmostEqual(null["mean"], .5)
        # A response-only predictor must tie when response IDs and positions match.
        self.assertEqual(result["baselines"]["token_length"]["neutral_true_vs_false"]["tie_fraction"], 1.)

    def test_representation_position_is_respected(self):
        rows, hidden, vectors, config = fixture()
        hidden[:, 0, 1] = 0
        result = analyze_separation(rows, hidden, vectors, config)
        self.assertFalse(result["gates"]["layer14_final_content"]["passed"])
        self.assertTrue(result["gates"]["layer14_response_mean"]["passed"])

    def test_common_scale_residual_is_not_renormalized(self):
        rows, hidden, vectors, config = fixture()
        result = analyze_separation(rows, hidden, vectors, config)
        name = "layer14_boundary"
        projected = np.array(result["row_scores"][name + "_projected"])
        common = np.array(result["row_scores"][name + "_projected_common_scale"])
        self.assertTrue(np.allclose(common, projected * np.linalg.norm(vectors[name + "_projected_common_scale"])))


if __name__ == "__main__":
    unittest.main()
