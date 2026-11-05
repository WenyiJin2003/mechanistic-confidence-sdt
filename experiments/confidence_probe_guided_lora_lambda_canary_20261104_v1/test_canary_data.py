#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import build_canary_data as builder


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


class CanaryDataPreparationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp = tempfile.TemporaryDirectory()
        cls.output_dir = Path(cls.temp.name) / "data"
        cls.manifest = builder.build_outputs(cls.output_dir)
        cls.train = read_jsonl(cls.output_dir / "lora_train_cf200_156.jsonl")
        cls.dev = read_jsonl(cls.output_dir / "lora_dev_cf3_113.jsonl")
        cls.behavior = read_jsonl(cls.output_dir / "behavior_canary_cue50_46.jsonl")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp.cleanup()

    def test_exact_input_hashes_and_counts(self) -> None:
        loaded = builder.verify_and_load_inputs()
        self.assertEqual(
            {name: len(rows) for name, rows in loaded.items()},
            {name: spec["count"] for name, spec in builder.INPUTS.items()},
        )
        for name, spec in builder.INPUTS.items():
            self.assertEqual(
                builder.sha256_file(builder.REPO_ROOT / spec["path"]), spec["sha256"], name
            )

    def test_exact_output_counts(self) -> None:
        self.assertEqual(len(self.train), 156)
        self.assertEqual(len(self.dev), 113)
        self.assertEqual(len(self.behavior), 46)

    def test_pairwise_source_and_question_disjointness(self) -> None:
        named = {
            "train": self.train,
            "dev": self.dev,
            "behavior": self.behavior,
        }
        builder.assert_pairwise_disjoint(named)
        for left, right in (("train", "dev"), ("train", "behavior"), ("dev", "behavior")):
            self.assertFalse(
                {row["source_id"] for row in named[left]}
                & {row["source_id"] for row in named[right]}
            )
            self.assertFalse(
                {row["normalized_question_sha256"] for row in named[left]}
                & {row["normalized_question_sha256"] for row in named[right]}
            )

    def test_role_mapping_and_text_preservation(self) -> None:
        for row in self.train + self.dev + self.behavior:
            self.assertIn(row["target_longer_role"], {"confident", "hesitant"})
            self.assertTrue(row["confident_response"].strip())
            self.assertTrue(row["hesitant_response"].strip())
            self.assertNotEqual(row["confident_response"], row["hesitant_response"])
            self.assertTrue(row["engineering_only"])
            self.assertEqual(row["confirmatory_status"], "post_exposure_not_confirmatory")
        for row in self.behavior:
            expected = (
                "confident" if row["length_direction"] == "confident_longer" else "hesitant"
            )
            self.assertEqual(row["target_longer_role"], expected)

    def test_exact_cue50_exclusions(self) -> None:
        excluded = self.manifest["cue50_exclusions"]
        self.assertEqual(
            tuple(row["pair_id"] for row in excluded), builder.EXPECTED_CUE50_EXCLUSIONS
        )
        self.assertEqual(
            {row["id"] for row in self.behavior},
            {f"C{index:03d}" for index in range(1, 51)}
            - set(builder.EXPECTED_CUE50_EXCLUSIONS),
        )

    def test_deterministic_output_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as second_temp:
            second_dir = Path(second_temp) / "data"
            builder.build_outputs(second_dir)
            for name in (
                "lora_train_cf200_156.jsonl",
                "lora_dev_cf3_113.jsonl",
                "behavior_canary_cue50_46.jsonl",
            ):
                first = (self.output_dir / name).read_bytes()
                second = (second_dir / name).read_bytes()
                self.assertEqual(first, second, name)
                self.assertEqual(hashlib.sha256(first).digest(), hashlib.sha256(second).digest())


if __name__ == "__main__":
    unittest.main()
