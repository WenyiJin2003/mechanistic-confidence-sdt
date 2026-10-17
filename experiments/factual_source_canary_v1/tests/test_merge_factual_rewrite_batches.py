import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = (
    Path(__file__).resolve().parents[1] / "src" / "merge_factual_rewrite_batches.py"
)
SPEC = importlib.util.spec_from_file_location("merge_factual_rewrite_batches", MODULE_PATH)
merger = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(merger)


def sha256_text(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def make_source(index):
    return {
        "source_id": f"source-{index}",
        "group_id": f"group-{index}",
        "source_hash": sha256_text(f"source-record-{index}"),
        "original_response_sha256": sha256_text(f"original-response-{index}"),
        "dataset": ("asqa", "billsum", "qasper")[index % 3],
        "cue_family": f"cue-{index % 2}",
        "length_direction": (
            "confident_longer" if index % 2 else "hesitant_longer"
        ),
        "draft_order": "confident_first" if index in (1, 4) else "hesitant_first",
        "generation_order": index,
    }


def make_writer(source):
    return {
        "source_id": source["source_id"],
        "source_hash": source["source_hash"],
        "original_response_sha256": source["original_response_sha256"],
        "dataset": source["dataset"],
        "cue_family": source["cue_family"],
        "length_direction": source["length_direction"],
        "draft_order": source["draft_order"],
        "confident_response": f"Confident rewrite {source['source_id']}.",
        "hesitant_response": f"Hesitant rewrite {source['source_id']}.",
        "issues": [],
    }


def write_jsonl(path, rows):
    path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


class MergeFactualRewriteBatchesTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.sources = [make_source(index) for index in range(1, 5)]
        self.source_path = self.root / "sources.jsonl"
        write_jsonl(self.source_path, self.sources)
        self.output_path = self.root / "merged.jsonl"
        self.provenance_path = self.root / "provenance.json"

    def tearDown(self):
        self.temporary_directory.cleanup()

    def write_batch(self, name, rows):
        path = self.root / name
        write_jsonl(path, rows)
        return path

    def merge(self, inputs):
        return merger.merge_factual_rewrite_batches(
            self.source_path,
            inputs,
            self.output_path,
            self.provenance_path,
        )

    def test_duplicate_source_id_across_inputs_is_rejected(self):
        first = self.write_batch(
            "first.jsonl", [make_writer(self.sources[0]), make_writer(self.sources[1])]
        )
        second = self.write_batch(
            "second.jsonl",
            [
                make_writer(self.sources[1]),
                make_writer(self.sources[2]),
                make_writer(self.sources[3]),
            ],
        )

        with self.assertRaises(merger.MergeValidationError) as caught:
            self.merge([first, second])

        self.assertTrue(
            any("duplicate_writer_source_id:source-2" in error for error in caught.exception.errors)
        )
        self.assertFalse(self.output_path.exists())

    def test_missing_source_id_is_rejected(self):
        batch = self.write_batch(
            "batch.jsonl", [make_writer(source) for source in self.sources[:-1]]
        )

        with self.assertRaises(merger.MergeValidationError) as caught:
            self.merge([batch])

        self.assertIn("missing_writer_source_id:source-4", caught.exception.errors)

    def test_unknown_source_id_is_rejected(self):
        writers = [make_writer(source) for source in self.sources[:-1]]
        unknown_source = make_source(99)
        writers.append(make_writer(unknown_source))
        batch = self.write_batch("batch.jsonl", writers)

        with self.assertRaises(merger.MergeValidationError) as caught:
            self.merge([batch])

        self.assertTrue(
            any("unknown_writer_source_id:source-99" in error for error in caught.exception.errors)
        )
        self.assertIn("unexpected_writer_source_id:source-99", caught.exception.errors)

    def test_stale_identity_is_rejected(self):
        writers = [make_writer(source) for source in self.sources]
        writers[2]["source_hash"] = sha256_text("stale-source")
        batch = self.write_batch("batch.jsonl", writers)

        with self.assertRaises(merger.MergeValidationError) as caught:
            self.merge([batch])

        self.assertTrue(
            any("stale_identity:source-3:source_hash" in error for error in caught.exception.errors)
        )

    def test_output_is_ordered_by_manifest_generation_order_with_hash_provenance(self):
        write_jsonl(
            self.source_path,
            [self.sources[1], self.sources[3], self.sources[0], self.sources[2]],
        )
        first = self.write_batch(
            "first.jsonl", [make_writer(self.sources[2]), make_writer(self.sources[0])]
        )
        second = self.write_batch(
            "second.jsonl", [make_writer(self.sources[3]), make_writer(self.sources[1])]
        )

        provenance = self.merge([first, second])

        merged_rows = [
            json.loads(line)
            for line in self.output_path.read_text(encoding="utf-8").splitlines()
        ]
        self.assertEqual(
            [row["source_id"] for row in merged_rows],
            ["source-1", "source-2", "source-3", "source-4"],
        )
        actual_output_hash = hashlib.sha256(self.output_path.read_bytes()).hexdigest()
        self.assertEqual(provenance["output"]["sha256"], actual_output_hash)
        self.assertEqual(provenance["source_manifest"]["sha256"], hashlib.sha256(self.source_path.read_bytes()).hexdigest())
        self.assertEqual(
            [item["sha256"] for item in provenance["input_batches"]],
            [
                hashlib.sha256(first.read_bytes()).hexdigest(),
                hashlib.sha256(second.read_bytes()).hexdigest(),
            ],
        )
        self.assertEqual(
            json.loads(self.provenance_path.read_text(encoding="utf-8")), provenance
        )

    def test_validation_failure_leaves_no_partial_or_temporary_output(self):
        writers = [make_writer(source) for source in self.sources]
        writers[0]["dataset"] = "wrong-dataset"
        batch = self.write_batch("batch.jsonl", writers)

        with self.assertRaises(merger.MergeValidationError):
            self.merge([batch])

        self.assertFalse(self.output_path.exists())
        self.assertFalse(self.provenance_path.exists())
        self.assertEqual(list(self.root.glob(".merged.jsonl.*.tmp")), [])
        self.assertEqual(list(self.root.glob(".provenance.json.*.tmp")), [])


if __name__ == "__main__":
    unittest.main()
