import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "src" / "build_review_queue.py"
SPEC = importlib.util.spec_from_file_location("build_review_queue", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class ReviewQueueTests(unittest.TestCase):
    def test_queue_is_deterministic_and_passes_come_first(self) -> None:
        candidates = [
            {
                "dataset": "demo",
                "source_id": "b",
                "group_id": "b",
                "source_hash": "b",
                "heuristic_pass": False,
            },
            {
                "dataset": "demo",
                "source_id": "a",
                "group_id": "a",
                "source_hash": "a",
                "heuristic_pass": True,
            },
            {
                "dataset": "demo",
                "source_id": "c",
                "group_id": "c",
                "source_hash": "c",
                "heuristic_pass": True,
            },
        ]
        first = MODULE.build_queue(candidates, seed=7, batch_size=2)
        second = MODULE.build_queue(candidates, seed=7, batch_size=2)
        self.assertEqual(first, second)
        self.assertTrue(first[0]["heuristic_pass"])
        self.assertTrue(first[1]["heuristic_pass"])
        self.assertFalse(first[2]["heuristic_pass"])
        self.assertEqual([item["review_rank"] for item in first], [1, 2, 3])
        self.assertEqual([item["review_batch"] for item in first], [1, 1, 2])

    def test_public_record_omits_text(self) -> None:
        item = {
            "dataset": "demo",
            "source_id": "x",
            "group_id": "g",
            "source_hash": "h",
            "review_rank": 1,
            "review_batch": 1,
            "word_count": 10,
            "sentence_count": 1,
            "evidence_word_count": 20,
            "blocking_flags": [],
            "review_flags": [],
            "heuristic_pass": True,
            "question": "private",
            "original_response": "private",
            "evidence": "private",
        }
        public = MODULE.public_record(item)
        self.assertNotIn("question", public)
        self.assertNotIn("original_response", public)
        self.assertNotIn("evidence", public)


if __name__ == "__main__":
    unittest.main()
