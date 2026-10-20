"""Identical repeated objects can be removed without inventing or editing text."""
import copy
import json
import sys
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))
from output_contract import normalize_identical_duplicates
from run_haiku import parse_payload


class IdenticalDuplicateTests(unittest.TestCase):
    def setUp(self):
        self.model = "claude-haiku-5-5"
        self.ids = ["HC001", "HC002", "HC003"]
        self.records = [
            {"id": key, "status": "ok", "confident": f"  Full direct answer {key}.\n",
             "hesitant": f"  Full tentative answer {key}.\n", "reject_reason": None}
            for key in self.ids
        ]

    def envelope(self, records=None, structured=False):
        payload = {"records": copy.deepcopy(self.records if records is None else records),
                   "payload_extra": {"preserve": True}}
        return {"type": "result", "subtype": "success", "is_error": False,
                "stop_reason": "end_turn", "modelUsage": {self.model: {"outputTokens": 100}},
                "usage": {"input_tokens": 200}, "total_cost_usd": 0.01,
                "envelope_extra": ["preserve this"],
                **({"structured_output": payload} if structured else {"result": json.dumps(payload)})}

    def test_plain_json_duplicate_removal_keeps_first_order_exact_text_and_all_metadata(self):
        rows = [self.records[1], self.records[0], self.records[1], self.records[2], self.records[0], self.records[1]]
        raw = self.envelope(rows)
        before = copy.deepcopy(raw)
        normalized, metadata = normalize_identical_duplicates(raw, self.ids)
        self.assertEqual(raw, before)
        payload = json.loads(normalized["result"])
        self.assertEqual(payload["records"], [self.records[1], self.records[0], self.records[2]])
        self.assertEqual(payload["payload_extra"], {"preserve": True})
        self.assertEqual(metadata, {
            "normalization": "identical_record_duplicates_only",
            "duplicate_ids": ["HC002", "HC001"], "discarded_indices": [2, 4, 5],
            "returned_ids": [row["id"] for row in rows],
        })
        for key in ("modelUsage", "usage", "total_cost_usd", "envelope_extra", "type", "subtype", "stop_reason"):
            self.assertEqual(normalized[key], raw[key])
        self.assertEqual(parse_payload(normalized, self.ids, self.model), payload["records"])

    def test_structured_output_preserves_first_objects_and_does_not_mutate_input(self):
        raw = self.envelope([self.records[0], self.records[0], *self.records[1:]], structured=True)
        raw["result"] = ""
        before = copy.deepcopy(raw)
        normalized, metadata = normalize_identical_duplicates(raw, self.ids)
        self.assertEqual(normalized["structured_output"]["records"], self.records)
        self.assertEqual(normalized["result"], "")
        self.assertEqual(metadata["discarded_indices"], [1])
        normalized["structured_output"]["records"][0]["confident"] = "Changed copy only"
        normalized["modelUsage"][self.model]["outputTokens"] = 999
        self.assertEqual(raw, before)

    def test_identical_dual_payloads_are_both_updated_and_conflicting_payloads_rejected(self):
        raw = self.envelope([self.records[0], self.records[0], *self.records[1:]], structured=True)
        raw["result"] = json.dumps(raw["structured_output"])
        normalized, _ = normalize_identical_duplicates(raw, self.ids)
        self.assertEqual(normalized["structured_output"], json.loads(normalized["result"]))
        self.assertEqual(len(normalized["structured_output"]["records"]), 3)
        raw["structured_output"]["records"][0]["confident"] += " changed"
        with self.assertRaisesRegex(RuntimeError, "Conflicting structured"):
            normalize_identical_duplicates(raw, self.ids)

    def test_no_duplicates_returns_an_independent_unchanged_envelope(self):
        raw = self.envelope()
        raw["result"] = json.dumps(json.loads(raw["result"]), indent=2)
        normalized, metadata = normalize_identical_duplicates(raw, self.ids)
        self.assertEqual(normalized, raw)
        self.assertIsNot(normalized, raw)
        self.assertEqual(metadata, {
            "normalization": "identical_record_duplicates_only", "duplicate_ids": [],
            "discarded_indices": [], "returned_ids": self.ids,
        })
        normalized["envelope_extra"].append("copy only")
        self.assertEqual(raw["envelope_extra"], ["preserve this"])

    def test_null_structured_output_is_removed_only_from_the_copy(self):
        raw = self.envelope()
        raw["structured_output"] = None
        normalized, _ = normalize_identical_duplicates(raw, self.ids)
        self.assertNotIn("structured_output", normalized)
        self.assertIn("structured_output", raw)
        self.assertEqual(parse_payload(normalized, self.ids, self.model), self.records)

    def test_partial_identical_duplicates_do_not_invent_missing_records(self):
        raw = self.envelope([self.records[0], self.records[0]])
        normalized, metadata = normalize_identical_duplicates(raw, self.ids)
        self.assertEqual(json.loads(normalized["result"])["records"], self.records[:1])
        self.assertEqual(metadata["duplicate_ids"], self.ids[:1])
        with self.assertRaisesRegex(RuntimeError, "Response ID mismatch"):
            parse_payload(normalized, self.ids, self.model)

    def test_conflicts_in_any_record_field_or_whitespace_are_rejected(self):
        for field, value in (("status", "reject"), ("reject_reason", "reason"),
                             ("confident", self.records[0]["confident"].strip()),
                             ("hesitant", self.records[0]["hesitant"] + " "),
                             ("new_field", "extra")):
            with self.subTest(field=field):
                changed = {**self.records[0], field: value}
                raw = self.envelope([self.records[0], changed])
                before = copy.deepcopy(raw)
                with self.assertRaisesRegex(RuntimeError, "Conflicting duplicate"):
                    normalize_identical_duplicates(raw, self.ids)
                self.assertEqual(raw, before)
        missing_field = dict(self.records[0])
        missing_field.pop("reject_reason")
        with self.assertRaisesRegex(RuntimeError, "Conflicting duplicate"):
            normalize_identical_duplicates(self.envelope([self.records[0], missing_field]), self.ids)

    def test_identical_rejected_objects_are_preserved_with_their_reason(self):
        rejected = {"id": self.ids[0], "status": "reject", "confident": None,
                    "hesitant": None, "reject_reason": "  Exact reason.\n"}
        normalized, _ = normalize_identical_duplicates(self.envelope([rejected, rejected]), self.ids)
        self.assertEqual(json.loads(normalized["result"])["records"], [rejected])

    def test_extra_field_type_differences_are_conflicting_duplicates(self):
        for first, second in ((True, 1), (1, 1.0), (False, 0), ({"value": True}, {"value": 1})):
            with self.subTest(first=first, second=second):
                rows = [{**self.records[0], "extra": first}, {**self.records[0], "extra": second}]
                with self.assertRaisesRegex(RuntimeError, "Conflicting duplicate"):
                    normalize_identical_duplicates(self.envelope(rows), self.ids)

    def test_dual_payload_comparison_distinguishes_json_number_and_boolean_types(self):
        for first, second in ((True, 1), (1, 1.0)):
            with self.subTest(first=first, second=second):
                raw = self.envelope(structured=True)
                raw["structured_output"]["records"][0]["extra"] = first
                result = copy.deepcopy(raw["structured_output"])
                result["records"][0]["extra"] = second
                raw["result"] = json.dumps(result)
                with self.assertRaisesRegex(RuntimeError, "Conflicting structured"):
                    normalize_identical_duplicates(raw, self.ids)

    def test_duplicate_json_object_keys_are_rejected_even_with_equal_values(self):
        examples = (
            '{"records": [], "records": []}',
            '{"records": [{"id": "HC001", "id": "HC001"}]}',
            '{"records": [{"id": "HC001", "extra": {"value": 1, "value": 1}}]}',
        )
        for result in examples:
            with self.subTest(result=result):
                with self.assertRaisesRegex(RuntimeError, "Duplicate JSON object keys"):
                    normalize_identical_duplicates({**self.envelope(), "result": result}, self.ids)

    def test_nonfinite_json_numbers_are_rejected_in_plain_and_structured_output(self):
        for value in (float("nan"), float("inf"), -float("inf")):
            for structured in (False, True):
                with self.subTest(value=value, structured=structured):
                    row = {**self.records[0], "extra": value}
                    with self.assertRaises(RuntimeError):
                        normalize_identical_duplicates(self.envelope([row, row], structured=structured), self.ids)
        raw = {**self.envelope(), "result": '{"records": [{"id": "HC001", "extra": 1e999}]}'}
        with self.assertRaises(RuntimeError):
            normalize_identical_duplicates(raw, self.ids)

    def test_non_json_structured_values_raise_runtime_error(self):
        for value in ({"a set"}, object(), b"bytes"):
            with self.subTest(type=type(value).__name__):
                row = {**self.records[0], "extra": value}
                with self.assertRaisesRegex(RuntimeError, "non-JSON"):
                    normalize_identical_duplicates(self.envelope([row, row], structured=True), self.ids)

    def test_refusal_errors_and_incomplete_generation_are_never_normalized(self):
        for change in ({"is_error": True}, {"is_error": None}, {"subtype": "error_max_budget_usd"},
                       {"stop_reason": "refusal"}, {"stop_reason": "max_tokens"}, {"stop_reason": None}):
            with self.subTest(change=change):
                raw = {**self.envelope([self.records[0], self.records[0]]), **change}
                with self.assertRaises(RuntimeError):
                    normalize_identical_duplicates(raw, self.ids)

    def test_unknown_empty_or_malformed_records_are_rejected(self):
        for rows in ([], None, {}, [None], [{"id": "unknown"}], [{"id": ""}], [{"id": " \t"}],
                     [{"id": None}], [{"id": [self.ids[0]]}], [{}]):
            with self.subTest(records=rows):
                raw = self.envelope()
                raw["result"] = json.dumps({"records": rows})
                with self.assertRaises(RuntimeError):
                    normalize_identical_duplicates(raw, self.ids)

    def test_invalid_expected_ids_are_rejected(self):
        for expected in ([], [self.ids[0], self.ids[0]], [None], [""], [" "], [1], "HC001"):
            with self.subTest(expected=expected):
                with self.assertRaises(RuntimeError):
                    normalize_identical_duplicates(self.envelope(), expected)

    def test_malformed_or_ambiguous_payloads_are_rejected(self):
        for change in ({"result": "not JSON"}, {"result": "[]"}, {"result": "null"},
                       {"result": ""}, {"result": {}}, {"result": None},
                       {"structured_output": []}, {"structured_output": "not an object"}):
            with self.subTest(change=change):
                raw = {**self.envelope(), **change}
                with self.assertRaises(RuntimeError):
                    normalize_identical_duplicates(raw, self.ids)


if __name__ == "__main__":
    unittest.main()
