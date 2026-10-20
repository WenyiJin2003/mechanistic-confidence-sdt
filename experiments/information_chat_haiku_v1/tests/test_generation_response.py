"""Provider-free acceptance tests for exact-duplicate-only normalization."""
import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from run_expansion import parse_generation_response


class GenerationResponseTests(unittest.TestCase):
    def setUp(self):
        self.ids = ["HC1", "HC2"]
        self.rows = [{"id": key, "status": "ok", "confident": f"Fact {key} holds.",
                      "hesitant": f"Fact {key} might hold.", "reject_reason": None} for key in self.ids]
        self.config = {"model": "claude-haiku-5-5", "campaign": {
            "identical_duplicate_normalization": {"enabled": True}}}

    def envelope(self, rows):
        return {"subtype": "success", "is_error": False, "stop_reason": "end_turn",
                "modelUsage": {"claude-haiku-5-5": {"outputTokens": 100}},
                "result": json.dumps({"records": rows})}

    def test_full_duplicate_is_collapsed_without_text_or_input_changes(self):
        raw = self.envelope(self.rows + self.rows[-1:])
        before = copy.deepcopy(raw)
        rows, note = parse_generation_response(raw, self.ids, self.config)
        self.assertEqual(rows, self.rows)
        self.assertEqual(raw, before)
        self.assertEqual(note["duplicate_ids"], ["HC2"])
        self.assertEqual(note["discarded_indices"], [2])

    def test_normal_response_has_no_normalization_annotation(self):
        rows, note = parse_generation_response(self.envelope(self.rows), self.ids, self.config)
        self.assertEqual(rows, self.rows)
        self.assertIsNone(note)

    def test_policy_is_opt_in_and_exact_boolean(self):
        raw = self.envelope(self.rows + self.rows[-1:])
        for value in (False, None, "true", 1):
            config = copy.deepcopy(self.config)
            config["campaign"]["identical_duplicate_normalization"]["enabled"] = value
            with self.subTest(value=value), self.assertRaises(RuntimeError):
                parse_generation_response(raw, self.ids, config)

    def test_conflicts_or_partial_coverage_are_not_accepted(self):
        cases = [self.rows + [{**self.rows[-1], "hesitant": "A different answer."}],
                 self.rows[:1] * 2,
                 self.rows + [{**self.rows[-1], "id": "HC999"}]]
        for rows in cases:
            with self.subTest(rows=rows), self.assertRaises(RuntimeError):
                parse_generation_response(self.envelope(rows), self.ids, self.config)

    def test_normalization_does_not_bypass_model_provenance_or_provider_errors(self):
        base = self.envelope(self.rows + self.rows[-1:])
        for change in ({"modelUsage": {"another-model": {"outputTokens": 100}}},
                       {"is_error": True}, {"stop_reason": "refusal"}, {"stop_reason": "max_tokens"}):
            with self.subTest(change=change), self.assertRaises(RuntimeError):
                parse_generation_response({**base, **change}, self.ids, self.config)

    def test_rejection_and_text_validation_are_unchanged(self):
        malformed = [{**self.rows[0], "status": "reject", "confident": None, "hesitant": None},
                     {**self.rows[0], "confident": " "},
                     {**self.rows[0], "reject_reason": "Invalid combination."}]
        for row in malformed:
            with self.subTest(row=row), self.assertRaises(RuntimeError):
                parse_generation_response(self.envelope([row, self.rows[1]]), self.ids, self.config)
        valid = {"id": "HC1", "status": "reject", "confident": None, "hesitant": None,
                 "reject_reason": "Cannot preserve the source."}
        rows, note = parse_generation_response(self.envelope([valid, self.rows[1]]), self.ids, self.config)
        self.assertEqual(rows[0], valid)
        self.assertIsNone(note)


if __name__ == "__main__":
    unittest.main()
