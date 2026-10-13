"""Tests for the generic label-blind human review packet builder."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from build_blind_review_packet import (
    assignment,
    balanced_assignments,
    build_packet,
    sha256_file,
    sha256_text,
)


class BlindReviewPacketTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        (self.base / "private_data").mkdir()
        source_text = "The code is 4712."
        self.source = {
            "source_id": "source-1",
            "original_response": source_text,
            "original_response_sha256": sha256_text(source_text),
            "prompt": "What is the code?",
            "task": "qa",
            "dataset": "fixture",
        }
        pair = {
            "source_id": "source-1",
            "original_response_sha256": self.source["original_response_sha256"],
            "confident_response": "The code is definitely 4712.",
            "hedged_response": "I think the code may be 4712.",
            "status": "accepted",
        }
        source_path = self.base / "private_data" / "sources.jsonl"
        source_path.write_text(json.dumps(self.source) + "\n")
        pair_records_hash = sha256_text(json.dumps([pair], sort_keys=True))
        pair_path = self.base / "private_data" / "pairs.json"
        pair_path.write_text(json.dumps({"records": [pair], "records_sha256": pair_records_hash}))
        self.config_path = self.base / "config.json"
        self.config_path.write_text(json.dumps({
            "seed": 17,
            "expected_pairs": 1,
            "source_files": [{
                "path": "private_data/sources.jsonl",
                "file_sha256": sha256_file(source_path),
            }],
            "pair_batches": [{
                "cohort": "test",
                "path": "private_data/pairs.json",
                "file_sha256": sha256_file(pair_path),
                "records_sha256": pair_records_hash,
            }],
            "output_dir": "private_data/review",
        }))

    def tearDown(self):
        self.temp.cleanup()

    def test_packet_is_blind_and_has_all_review_dimensions(self):
        manifest = build_packet(self.config_path, self.base)
        page = (self.base / "private_data/review/BLIND_REVIEW.html").read_text()
        key_path = self.base / "private_data/review/UNBLIND_KEY.json"
        key = json.loads(key_path.read_text())
        self.assertNotIn("confident_response", page)
        self.assertNotIn("hedged_response", page)
        self.assertNotIn("version_a_label", page)
        self.assertNotIn("source-1", page)
        for field in ["content_equivalence", "certainty_contrast", "naturalness", "cue_scope", "decision", "comment"]:
            self.assertIn(f'data-field="{field}"', page)
        self.assertIn("blind_human_review_1.json", page)
        self.assertNotIn("blind_human_review_20.json", page)
        self.assertEqual(key["pairs"][0]["version_a_label"], assignment(17, "source-1")[0])
        self.assertEqual(set(key), {"packet_sha256", "seed", "pairs"})
        self.assertEqual(manifest["pairs"], 1)
        self.assertTrue(manifest["blinded"])
        self.assertNotIn("review_schema_id", manifest)
        self.assertNotIn("review_schema_sha256", manifest)
        self.assertNotIn("packet_hash_mode", manifest)
        self.assertNotIn('data-field="structure_format"', page)
        rows_path = self.base / "private_data/review/BLINDED_ROWS.jsonl"
        self.assertEqual(manifest["packet_sha256"], sha256_file(rows_path))
        self.assertEqual(
            manifest["unblind_key_sha256"],
            sha256_file(key_path),
        )

    def test_optional_structure_schema_is_visible_required_and_hash_bound(self):
        legacy = build_packet(self.config_path, self.base)
        config = json.loads(self.config_path.read_text())
        config["review_schema"] = {
            "schema_id": "fixture-six-field-v1",
            "include_structure_format": True,
        }
        config["output_dir"] = "private_data/review_structure"
        structure_config = self.base / "structure_config.json"
        structure_config.write_text(json.dumps(config))
        manifest = build_packet(structure_config, self.base)
        page = (self.base / "private_data/review_structure/BLIND_REVIEW.html").read_text()
        self.assertIn('data-field="structure_format"', page)
        self.assertIn('"structure_format"', page)
        self.assertEqual(
            manifest["review_dimensions"],
            ["content_equivalence", "certainty_contrast", "naturalness", "cue_scope", "structure_format", "decision"],
        )
        self.assertEqual(manifest["review_schema_id"], "fixture-six-field-v1")
        self.assertEqual(
            manifest["packet_hash_mode"],
            "schema-keycore-and-blinded-rows-sha256-v3",
        )
        self.assertEqual(
            json.loads((self.base / "private_data/review_structure/UNBLIND_KEY.json").read_text())["review_schema_sha256"],
            manifest["review_schema_sha256"],
        )
        self.assertEqual(
            json.loads((self.base / "private_data/review_structure/UNBLIND_KEY.json").read_text())["key_core_sha256"],
            manifest["key_core_sha256"],
        )
        self.assertNotEqual(manifest["packet_sha256"], legacy["packet_sha256"])

    def test_same_seed_reproduces_packet(self):
        first = build_packet(self.config_path, self.base)
        second = build_packet(self.config_path, self.base)
        self.assertEqual(first["packet_sha256"], second["packet_sha256"])

    def test_ab_positions_are_balanced_within_even_cohort(self):
        mapping = balanced_assignments(17, {"cohort": [f"source-{i}" for i in range(10)]})
        a_labels = [labels[0] for labels in mapping.values()]
        self.assertEqual(a_labels.count("confident"), 5)
        self.assertEqual(a_labels.count("hedged"), 5)

    def test_refuses_public_output(self):
        config = json.loads(self.config_path.read_text())
        config["output_dir"] = "reports/review"
        self.config_path.write_text(json.dumps(config))
        with self.assertRaisesRegex(ValueError, "private_data"):
            build_packet(self.config_path, self.base)

    def test_refuses_changed_bound_input(self):
        pair_path = self.base / "private_data/pairs.json"
        pair_path.write_text(pair_path.read_text() + "\n")
        with self.assertRaisesRegex(ValueError, "file hash mismatch"):
            build_packet(self.config_path, self.base)

    def test_refuses_to_overwrite_different_packet_without_flag(self):
        build_packet(self.config_path, self.base)
        config = json.loads(self.config_path.read_text())
        config["seed"] = 24
        self.config_path.write_text(json.dumps(config))
        with self.assertRaisesRegex(ValueError, "Refusing to overwrite"):
            build_packet(self.config_path, self.base)

    def test_source_hash_mismatch_is_rejected(self):
        changed = dict(self.source, original_response="The code is 9999.")
        source_path = self.base / "private_data/sources.jsonl"
        source_path.write_text(json.dumps(changed) + "\n")
        config = json.loads(self.config_path.read_text())
        config["source_files"][0]["file_sha256"] = sha256_file(source_path)
        self.config_path.write_text(json.dumps(config))
        with self.assertRaisesRegex(ValueError, "Source hash mismatch"):
            build_packet(self.config_path, self.base)


if __name__ == "__main__":
    unittest.main()
