import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from output_contract import MARKER, build_request_data


class OutputContractTests(unittest.TestCase):
    def records(self, count):
        return [
            {
                "id": f"HC{index:03d}",
                "question": "What is this source about?",
                "original_response": "A synthetic source.",
                "context": {"quoted": ["Keep this unchanged."]},
            }
            for index in range(1, count + 1)
        ]

    def test_v2_payload_is_unchanged(self):
        prompt = (ROOT / "prompts" / "rewrite_scale_v2.txt").read_text()
        records = self.records(5)
        self.assertNotIn(MARKER, prompt)
        self.assertEqual(build_request_data(prompt, records), {"records": records})

    def test_v2_does_not_apply_v3_id_validation(self):
        records = [{"id": ""}, {"id": "duplicate"}, {"id": "duplicate"}, {}]
        self.assertEqual(build_request_data("legacy prompt", records), {"records": records})

    def test_v3_declares_every_id_in_input_order_for_full_and_partial_batches(self):
        prompt = (ROOT / "prompts" / "rewrite_scale_v3.txt").read_text()
        for count in (4, 5, 1):
            with self.subTest(count=count):
                records = list(reversed(self.records(count)))
                data = build_request_data(prompt, records)
                self.assertEqual(data["records"], records)
                self.assertEqual(
                    data["required_output"],
                    {
                        "record_count": count,
                        "expected_ids": [record["id"] for record in records],
                    },
                )

    def test_builder_does_not_mutate_nested_records(self):
        for prompt in ("legacy prompt", MARKER):
            with self.subTest(prompt=prompt):
                records = self.records(5)
                before = copy.deepcopy(records)
                build_request_data(prompt, records)
                self.assertEqual(records, before)

    def test_v3_rejects_missing_nonstring_empty_and_blank_ids(self):
        for bad_record in ({}, {"id": None}, {"id": 3}, {"id": ""}, {"id": " \t\n"}):
            with self.subTest(record=bad_record):
                records = [*self.records(1), bad_record]
                before = copy.deepcopy(records)
                with self.assertRaises(ValueError):
                    build_request_data(MARKER, records)
                self.assertEqual(records, before)

    def test_v3_rejects_duplicate_ids_without_mutation(self):
        records = self.records(5)
        records[-1]["id"] = records[0]["id"]
        before = copy.deepcopy(records)
        with self.assertRaisesRegex(ValueError, "duplicate"):
            build_request_data(MARKER, records)
        self.assertEqual(records, before)

    def test_v3_preserves_v2_semantic_instructions_byte_for_byte(self):
        v2 = (ROOT / "prompts" / "rewrite_scale_v2.txt").read_bytes()
        v3 = (ROOT / "prompts" / "rewrite_scale_v3.txt").read_bytes()
        self.assertEqual(v2.split(b"Return exactly", 1)[0], v3.split(b"Return exactly", 1)[0])
        self.assertIn(MARKER.encode(), v3)


if __name__ == "__main__":
    unittest.main()
