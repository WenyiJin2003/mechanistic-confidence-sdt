import json
import sys
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))
from build_review import Readback, audit, numbers
from run_haiku import parse_payload

class CanaryTests(unittest.TestCase):
    def test_numbers_ignore_list_markers(self):
        self.assertEqual(numbers("1. 81 points on January 22, 2006."), numbers("81 points on January 22, 2006."))

    def test_numbers_flag_added_dates(self):
        self.assertIn("numeric_token_difference_check_manually", audit("A leap second adjusts UTC.", "A leap second adjusts UTC in 2012."))

    def test_boilerplate_flag(self):
        self.assertIn("detachable_certainty_boilerplate", audit("X is Y.", "X is Y. I stand firmly behind this answer."))

    def test_unknown_writer_rejected(self):
        with self.assertRaises(RuntimeError):
            parse_payload({"modelUsage": {"claude-sonnet-4-6": {"outputTokens": 100}}}, ["HC001"], "claude-haiku-5-5")

    def test_small_auxiliary_haiku_not_mislabeled_writer(self):
        row = {"id": "HC001", "status": "ok", "confident": "X is Y.", "hesitant": "X might be Y.", "reject_reason": None}
        response = {"modelUsage": {"claude-haiku-5-5": {"outputTokens": 100}, "claude-haiku-4-5-20251001": {"outputTokens": 12}}, "result": json.dumps({"records": [row]})}
        self.assertEqual(parse_payload(response, ["HC001"], "claude-haiku-5-5"), [row])

    def test_html_readback_exact(self):
        readback = Readback()
        readback.feed('<div class="response verbatim">X &lt; Y\n  possibly.</div>')
        self.assertEqual(readback.responses, ["X < Y\n  possibly."])

if __name__ == "__main__":
    unittest.main()
