import importlib.util
import unittest
from pathlib import Path


SPEC = importlib.util.spec_from_file_location(
    "summarize_epistemic_preview_review",
    Path(__file__).resolve().parents[1] / "src" / "summarize_epistemic_preview_review.py",
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def fixture():
    rows, keys, pairs = [], [], []
    for index in range(6):
        identifier = f"fixture{index}"
        a_confident = index < 3
        keys.append({"preview_id": identifier, "version_a_role": "confident" if a_confident else "hesitant"})
        pairs.append({"preview_id": identifier, "confident_response": "Fixed fact.",
                      "hesitant_response": "Possibly this fixed fact."})
        rows.append({"review_id": identifier, "factual_core": "preserved",
                     "more_confident": "a" if a_confident else "b", "contrast": "clear",
                     "naturalness_a": "natural", "naturalness_b": "natural"})
    return rows, keys, pairs


class SummaryTests(unittest.TestCase):
    def test_review_counts_and_length_diagnostic_are_distinct(self):
        rows, keys, pairs = fixture()
        rows[0]["more_confident"] = "b"
        rows[1]["naturalness_b"] = "minor_issues"
        result = MODULE.summarize(rows, keys, pairs)
        self.assertEqual(result["review_counts"]["intended_confident_version_selected"], 5)
        self.assertEqual(result["review_counts"]["both_versions_natural"], 5)
        self.assertEqual(result["review_counts"]["neither_version_has_major_naturalness_issues"], 6)
        self.assertEqual(result["construction_diagnostics"]["shorter_text_selects_intended_confident_pairs"], 6)
        self.assertTrue(result["construction_diagnostics"]["diagnostic_is_not_probe_performance"])

    def test_incomplete_duplicate_or_invalid_review_is_rejected(self):
        rows, keys, pairs = fixture()
        with self.assertRaises(ValueError):
            MODULE.summarize(rows[:-1], keys, pairs)
        rows[-1]["review_id"] = rows[0]["review_id"]
        with self.assertRaises(ValueError):
            MODULE.summarize(rows, keys, pairs)
        rows, keys, pairs = fixture()
        rows[0]["factual_core"] = "automatic_pass"
        with self.assertRaises(ValueError):
            MODULE.summarize(rows, keys, pairs)


if __name__ == "__main__":
    unittest.main()
