"""Prospective output formatting must preserve historical cache fingerprints."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import run_expansion as expansion
from launch_expansion import pending_batches
from output_contract import MARKER, build_request_data


class PromptVersionBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.v2 = (ROOT / "prompts" / "rewrite_scale_v2.txt").read_text()
        self.v3 = (ROOT / "prompts" / "rewrite_scale_v3.txt").read_text()
        self.config = {
            "model": "claude-haiku-5-5", "max_output_tokens": 10000, "batch_size": 5,
            "prompt_file": str(ROOT / "prompts" / "rewrite_scale_v3.txt"),
            "legacy_prompt_boundary": 179,
            "legacy_prompt_file": str(ROOT / "prompts" / "rewrite_scale_v2.txt"),
        }
        self.batch = [
            {"review_id": f"HC{index:05d}", "source_id": f"source-{index}",
             "question": f"What is sample {index}?", "original": f"Sample {index} is synthetic."}
            for index in range(1, 6)
        ]

    def legacy_fingerprint(self, prompt, batch):
        return expansion.sha(json.dumps({
            "model": self.config["model"], "effort": "low",
            "max_output_tokens": self.config["max_output_tokens"], "prompt": prompt,
            "batch": [expansion.request_record(row) for row in batch],
        }, sort_keys=True, ensure_ascii=False))

    def test_all_historical_batches_use_v2_and_new_batches_use_v3(self):
        before = copy.deepcopy(self.config)
        for number in (1, 2, 167, 178, 179):
            with self.subTest(number=number):
                self.assertEqual(expansion.batch_prompt_text(self.config, f"batch_{number:05d}"), self.v2)
        for number in (180, 181, 2000):
            with self.subTest(number=number):
                self.assertEqual(expansion.batch_prompt_text(self.config, f"batch_{number:05d}"), self.v3)
        self.assertEqual(self.config, before)

    def test_explicit_overrides_take_precedence_on_both_sides_of_boundary(self):
        with tempfile.TemporaryDirectory() as directory:
            override = Path(directory) / "override.txt"
            override.write_text("Preserved explicit prompt override.", encoding="utf-8")
            config = {**self.config, "prompt_overrides": {
                "batch_00001": str(override), "batch_00180": str(override),
            }}
            for name in config["prompt_overrides"]:
                with self.subTest(batch=name):
                    self.assertEqual(expansion.batch_prompt_text(config, name), override.read_text())
            self.assertEqual(expansion.batch_prompt_text(config, "batch_00179"), self.v2)
            self.assertEqual(expansion.batch_prompt_text(config, "batch_00181"), self.v3)

    def test_no_legacy_boundary_keeps_existing_single_prompt_behavior(self):
        config = {key: value for key, value in self.config.items() if not key.startswith("legacy_prompt_")}
        self.assertEqual(expansion.batch_prompt_text(config, "batch_00001"), self.v3)

    def test_invalid_batch_names_cannot_choose_a_prompt(self):
        for name in ("batch_179", "../batch_00179", "batch_00179.request.json", "", "batch_abcde"):
            with self.subTest(batch=name):
                with self.assertRaises(RuntimeError):
                    expansion.batch_prompt_text(self.config, name)

    def test_v2_fingerprint_is_byte_compatible_with_original_protocol(self):
        self.assertEqual(expansion.fingerprint(self.config, self.v2, self.batch),
                         self.legacy_fingerprint(self.v2, self.batch))
        repair_batch = copy.deepcopy(self.batch)
        repair_batch[0]["previous_versions"] = {"confident": "Prior direct text.", "hesitant": "Prior tentative text."}
        self.assertEqual(expansion.fingerprint(self.config, self.v2, repair_batch),
                         self.legacy_fingerprint(self.v2, repair_batch))

    def test_v3_fingerprint_binds_declared_cardinality_and_ordered_ids(self):
        records = [expansion.request_record(row) for row in self.batch]
        metadata = build_request_data(self.v3, records)["required_output"]
        expected = expansion.sha(json.dumps({
            "model": self.config["model"], "effort": "low",
            "max_output_tokens": self.config["max_output_tokens"], "prompt": self.v3,
            "batch": records, "required_output": metadata,
        }, sort_keys=True, ensure_ascii=False))
        actual = expansion.fingerprint(self.config, self.v3, self.batch)
        self.assertEqual(actual, expected)
        self.assertNotEqual(actual, self.legacy_fingerprint(self.v3, self.batch))
        changed = {"records": records, "required_output": {
            "record_count": 4, "expected_ids": metadata["expected_ids"][:-1],
        }}
        with mock.patch.object(expansion, "build_request_data", return_value=changed):
            self.assertNotEqual(expansion.fingerprint(self.config, self.v3, self.batch), actual)

    def test_pending_check_accepts_legacy_cache_and_leaves_only_new_batch_untouched(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sources = [
                {"review_id": f"HC{index:05d}", "source_id": f"source-{index}",
                 "question": f"What is sample {index}?", "original": f"Sample {index} is synthetic."}
                for index in range(1, 180 * self.config["batch_size"] + 1)
            ]
            expansion.dump(root / "SOURCES.json", sources)
            for number in range(1, 180):
                batch = sources[(number - 1) * 5:number * 5]
                prefix = root / "provider" / f"batch_{number:05d}"
                request_hash = self.legacy_fingerprint(self.v2, batch)
                expansion.dump(prefix.with_suffix(".request.json"), {"request_sha256": request_hash})
                expansion.dump(prefix.with_suffix(".parsed.json"), {"request_sha256": request_hash})
            before = {path: path.read_bytes() for path in (root / "provider").glob("*")}
            with mock.patch.object(expansion, "provider_stream", side_effect=AssertionError("No provider calls")) as provider:
                self.assertEqual(pending_batches(root, self.config), ["batch_00180"])
            provider.assert_not_called()
            self.assertEqual({path: path.read_bytes() for path in (root / "provider").glob("*")}, before)


if __name__ == "__main__":
    unittest.main()
