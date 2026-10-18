import importlib.util
import sys
import unittest
from pathlib import Path


SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))
SPEC = importlib.util.spec_from_file_location("wordnet_preview_finalizer", SRC / "finalize_economical_wordnet_preview.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class WordNetPreviewTests(unittest.TestCase):
    def test_a_choice_must_match_the_supplied_sense_and_both_arms(self):
        hints = [{"source_word": "later", "senses": [
            {"synset": "subsequently.r.01", "candidates": ["afterward"]}
        ]}]
        choice = {"source_word": "later", "synset": "subsequently.r.01", "replacement": "afterward"}
        self.assertTrue(MODULE.wordnet_selection_valid(choice, hints, ["This happened afterward.", "It might have happened afterward."]))
        self.assertFalse(MODULE.wordnet_selection_valid(choice, hints, ["This happened afterward.", "It might have happened later."]))
        self.assertFalse(MODULE.wordnet_selection_valid({**choice, "synset": "by_and_by.r.01"}, hints, ["afterward", "afterward"]))
        self.assertFalse(MODULE.wordnet_selection_valid({**choice, "replacement": "recently"}, hints, ["recently", "recently"]))

    def test_three_pair_page_exports_three_and_keeps_key_private(self):
        from prepare_epistemic_preview import render_preview
        cards = [{"review_id": f"fixture{i}", "question": "Question?",
                  "original_response": "Source text.", "version_a": "A text.",
                  "version_b": "B text."} for i in range(3)]
        page = render_preview(cards, "a" * 64, title="Three pairs", export_name="three.json")
        self.assertEqual(page.count("<article "), 3)
        self.assertIn("pair_count:3", page)
        self.assertIn('a.download="three.json"', page)
        self.assertNotIn("version_a_role", page)


if __name__ == "__main__":
    unittest.main()
