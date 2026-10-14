import json
import sys
import tempfile
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import merge_chat_repairs as merger


def writer_rows():
    return [
        {
            "source_id": "s1",
            "task": "factual_explanation",
            "confident_response": "old confident one",
            "hedged_response": "old hedged one",
            "issues": ["keep me"],
        },
        {
            "source_id": "s2",
            "task": "math_logic",
            "confident_response": "old confident two",
            "hedged_response": "old hedged two",
            "custom_metadata": {"nested": True},
        },
    ]


class MergeChatRepairsTests(unittest.TestCase):
    def test_applies_two_fields_without_changing_order_or_metadata(self):
        original = writer_rows()
        repairs = [{"repairs": [
            {"source_id": "s2", "field": "hedged_response", "revised_response": "new hedged two"},
            {"source_id": "s1", "field": "confident_response", "revised_response": "new confident one"},
            {"source_id": "s1", "field": "hedged_response", "revised_response": "new hedged one"},
        ]}]
        merged, applied = merger.merge_repairs(original, repairs)

        self.assertEqual([row["source_id"] for row in merged], ["s1", "s2"])
        self.assertEqual(merged[0]["confident_response"], "new confident one")
        self.assertEqual(merged[0]["hedged_response"], "new hedged one")
        self.assertEqual(merged[0]["issues"], ["keep me"])
        self.assertEqual(merged[1]["custom_metadata"], {"nested": True})
        self.assertEqual(merged[1]["confident_response"], "old confident two")
        self.assertEqual(len(applied), 3)
        self.assertEqual(original[0]["confident_response"], "old confident one")

    def test_rejects_unknown_or_duplicate_writer_ids(self):
        with self.assertRaisesRegex(ValueError, "unknown source_id"):
            merger.merge_repairs(writer_rows(), [{"repairs": [{
                "source_id": "missing", "field": "confident_response", "revised_response": "new"
            }]}])
        duplicate = writer_rows() + [dict(writer_rows()[0])]
        with self.assertRaisesRegex(ValueError, "duplicate source_id"):
            merger.merge_repairs(duplicate, [{"repairs": [{
                "source_id": "s1", "field": "confident_response", "revised_response": "new"
            }]}])

    def test_rejects_duplicate_same_field_but_allows_both_fields(self):
        both = [{"repairs": [
            {"source_id": "s1", "field": "confident_response", "revised_response": "new c"},
            {"source_id": "s1", "field": "hedged_response", "revised_response": "new h"},
        ]}]
        merged, _ = merger.merge_repairs(writer_rows(), both)
        self.assertEqual((merged[0]["confident_response"], merged[0]["hedged_response"]),
                         ("new c", "new h"))

        duplicate = [both[0], {"repairs": [{
            "source_id": "s1", "field": "confident_response", "revised_response": "again"
        }]}]
        with self.assertRaisesRegex(ValueError, "duplicate repair"):
            merger.merge_repairs(writer_rows(), duplicate)

    def test_rejects_bad_fields_blank_text_and_schema_drift(self):
        bad_cases = [
            {"source_id": "s1", "field": "task", "revised_response": "new"},
            {"source_id": "s1", "field": "confident_response", "revised_response": "  \n"},
            {"source_id": "s1", "field": "confident_response", "revised_response": "new", "x": 1},
        ]
        for repair in bad_cases:
            with self.subTest(repair=repair):
                with self.assertRaises(ValueError):
                    merger.merge_repairs(writer_rows(), [{"repairs": [repair]}])
        with self.assertRaisesRegex(ValueError, "no edits"):
            merger.merge_repairs(writer_rows(), [{"repairs": []}])

    def test_read_repair_object_requires_exact_top_level_schema(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "repairs.json"
            path.write_text(json.dumps({"repairs": [], "commentary": "unexpected"}), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unexpected top-level fields"):
                merger.read_repair_object(path)

    def test_private_atomic_write_refuses_escape_alias_and_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "private_data"
            protected = root / "writer.jsonl"
            protected.parent.mkdir(parents=True)
            protected.write_text("input\n", encoding="utf-8")

            outside = Path(tmp) / "outside.jsonl"
            with self.assertRaisesRegex(ValueError, "private_data"):
                merger.atomic_write_private(outside, "x\n", private_root=root)
            with self.assertRaisesRegex(ValueError, "must not overwrite"):
                merger.atomic_write_private(
                    protected, "x\n", private_root=root, protected_inputs=[protected]
                )

            output = root / "nested" / "repaired.jsonl"
            merger.atomic_write_private(output, "first\n", private_root=root)
            self.assertEqual(output.read_text(encoding="utf-8"), "first\n")
            with self.assertRaisesRegex(FileExistsError, "refusing to overwrite"):
                merger.atomic_write_private(output, "second\n", private_root=root)
            merger.atomic_write_private(output, "second\n", private_root=root, overwrite=True)
            self.assertEqual(output.read_text(encoding="utf-8"), "second\n")
            self.assertEqual(list(output.parent.glob("*.tmp")), [])

    def test_jsonl_round_trip_preserves_unicode_and_row_order(self):
        rows = writer_rows()
        rows[0]["confident_response"] = "确定的回答"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "rows.jsonl"
            path.write_text(merger.dump_jsonl(rows), encoding="utf-8")
            loaded = merger.read_jsonl(path)
        self.assertEqual(loaded, rows)


if __name__ == "__main__":
    unittest.main()
