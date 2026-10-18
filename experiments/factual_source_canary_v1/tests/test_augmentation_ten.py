import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from prepare_augmentation_ten import check_pairs, numeric_details, select_sources
from prepare_epistemic_preview import render_preview


class AugmentationTenTests(unittest.TestCase):
    def test_source_selection_is_in_frozen_order_and_meets_quotas(self):
        rows = [{"source_id": str(i), "group_id": str(i), "dataset": d}
                for i, d in enumerate(["a", "b", "a", "b", "a"])]
        self.assertEqual([r["source_id"] for r in select_sources(rows, {"a": 2, "b": 1})], ["0", "1", "2"])
        with self.assertRaises(ValueError):
            select_sources(rows, {"a": 4, "b": 1})

    def test_source_and_group_duplicates_are_rejected(self):
        row = {"source_id": "x", "group_id": "g", "dataset": "a"}
        with self.assertRaises(ValueError):
            select_sources([row, row], {"a": 2})
        with self.assertRaises(ValueError):
            select_sources([row, {**row, "source_id": "y"}], {"a": 2})

    def test_pair_coverage_and_nonempty_arms(self):
        sources = [{"preview_id": "a"}]
        pair = {"preview_id": "a", "confident_response": "Text.", "hesitant_response": "Perhaps text.",
                "primary_uncertainty_construction": "perhaps"}
        self.assertEqual(set(check_pairs(sources, [pair])), {"a"})
        for invalid in ([], [pair, pair], [{**pair, "hesitant_response": ""}], [{**pair, "preview_id": "b"}]):
            with self.assertRaises(ValueError):
                check_pairs(sources, invalid)

    def test_numeric_details_are_multisets_not_just_sets(self):
        self.assertEqual(numeric_details("1984; 1984; 2.5"), {"1984": 2, "2.5": 1})
        self.assertNotEqual(numeric_details("1984; 1984"), numeric_details("1984"))

    def test_ten_card_page_does_not_embed_role_key(self):
        cards = [{"review_id": f"DA{i:03d}", "question": "Question?", "original_response": "Source.",
                  "version_a": "A.", "version_b": "B."} for i in range(1, 11)]
        page = render_preview(cards, "a" * 64, export_name="ten.json", feedback_schema="ten-v1")
        self.assertEqual(page.count("<article "), 10)
        self.assertIn("pair_count:10", page)
        self.assertNotIn("version_a_role", page)


if __name__ == "__main__":
    unittest.main()
