import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "src" / "build_source_audit.py"
SPEC = importlib.util.spec_from_file_location("build_source_audit", MODULE_PATH)
audit = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(audit)


class SourceAuditTests(unittest.TestCase):
    def test_normalize_text_repairs_html_and_missing_sentence_space(self):
        self.assertEqual(
            audit.normalize_text("alpha&nbsp;beta.Directs action"),
            "alpha beta. Directs action",
        )

    def test_asqa_keeps_annotation_and_disambiguated_qa_evidence(self):
        row = {
            "sample_id": "x",
            "ambiguous_question": "When?",
            "annotations": [
                {
                    "long_answer": "It happened in 1999 and again in 2001.",
                    "knowledge": [{"content": "General background.", "wikipage": "Page"}],
                }
            ],
            "qa_pairs": [
                {
                    "question": "When was the first event?",
                    "short_answers": ["1999"],
                    "context": "The first event happened in 1999.",
                }
            ],
            "wikipages": [{"title": "Page", "url": "https://example.test"}],
        }
        item = list(audit.parse_asqa(0, row, {"license": "test"}))[0]
        self.assertIn("General background", item["evidence"])
        self.assertIn("When was the first event?", item["evidence"])
        self.assertIn("1999", item["evidence"])

    def test_fetaqa_preserves_multilevel_table_context(self):
        row = {
            "feta_id": 1,
            "table_source_json": "table.json",
            "page_wikipedia_url": "https://example.test",
            "table_page_title": "Player",
            "table_section_title": "Career",
            "table_array": [
                ["-", "Regular season", "Regular season"],
                ["Season", "GP", "Pts"],
                ["2020", "10", "25"],
            ],
            "highlighted_cell_ids": [[2, 0], [2, 1], [2, 2]],
            "question": "What were the results?",
            "answer": "The player appeared in 10 games and scored 25 points.",
        }
        item = list(audit.parse_fetaqa(0, row, {"license": "test"}))[0]
        self.assertIn("Table prefix row 0", item["evidence"])
        self.assertIn("Table prefix row 1", item["evidence"])
        self.assertIn("Selected row 2", item["evidence"])
        self.assertIn("[1] 10", item["evidence"])
        self.assertIn("[2] 25", item["evidence"])

    def test_qasper_uses_author_abstract_and_full_text(self):
        row = {
            "id": "1234.5678",
            "title": "A Paper",
            "abstract": "We introduce a method. It improves the measured result.",
            "full_text": {
                "section_name": ["Results"],
                "paragraphs": [["The result improved."]],
            },
        }
        item = list(audit.parse_qasper(0, row, {"license": "test"}))[0]
        self.assertEqual(item["metadata"]["source_response_type"], "author_abstract")
        self.assertTrue(item["original_response"].startswith("We introduce"))
        self.assertIn("The result improved", item["evidence"])

    def test_source_qualification_is_review_only(self):
        item = {
            "dataset": "x",
            "question": "q",
            "original_response": "The evidence suggests one result. A second result may follow.",
            "evidence": "Supporting evidence is present.",
        }
        enriched = audit.enrich(
            item,
            {
                "minimum_words": 1,
                "maximum_words": 100,
                "minimum_sentences": 2,
                "require_evidence": True,
            },
        )
        self.assertTrue(enriched["heuristic_pass"])
        self.assertEqual(enriched["blocking_flags"], [])
        self.assertEqual(enriched["review_flags"], ["preserve_source_qualification"])


if __name__ == "__main__":
    unittest.main()
