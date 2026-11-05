#!/usr/bin/env python3

from __future__ import annotations

import hashlib
import importlib.util
import json
import unittest
from collections import Counter
from pathlib import Path


EXPERIMENT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("build_eval_cohort", EXPERIMENT / "build_eval_cohort.py")
assert SPEC and SPEC.loader
builder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(builder)


class EvalCohortTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cohort_path = EXPERIMENT / "private_data/EVAL_COHORT_500.jsonl"
        cls.freeze_path = EXPERIMENT / "COHORT_FREEZE.json"
        with cls.cohort_path.open("r", encoding="utf-8") as handle:
            cls.rows = [json.loads(line) for line in handle if line.strip()]
        cls.freeze = json.loads(cls.freeze_path.read_text(encoding="utf-8"))

    def test_exact_counts_and_bins(self) -> None:
        self.assertEqual(len(self.rows), 500)
        self.assertEqual(len({row["eval_id"] for row in self.rows}), 500)
        self.assertEqual(len({row["question_sha256"] for row in self.rows}), 500)
        self.assertEqual(Counter(row["length_bin"] for row in self.rows), {"short": 167, "medium": 166, "long": 167})

    def test_raw_source_pin(self) -> None:
        self.assertEqual(builder.sha256_file(builder.RAW_SOURCE), builder.RAW_SOURCE_SHA256)

    def test_cohort_hash_pin(self) -> None:
        payload = self.cohort_path.read_bytes()
        self.assertEqual(hashlib.sha256(payload).hexdigest(), self.freeze["cohort_sha256"])
        self.assertEqual(len(payload), self.freeze["cohort_bytes"])

    def test_no_experimental_overlap(self) -> None:
        excluded, _ = builder.load_exclusions()
        selected = {builder.normalize_question(row["question"]) for row in self.rows}
        self.assertFalse(selected & excluded)
        self.assertEqual(self.freeze["normalized_overlap_with_all_exclusion_files"], 0)

    def test_only_questions_and_reference_aliases(self) -> None:
        forbidden_keys = {"response", "response_orig", "response_clean", "confident_response", "hesitant_response"}
        for row in self.rows:
            self.assertFalse(forbidden_keys & set(row))
            self.assertFalse(row["provider_generated_answer"])
            self.assertTrue(row["question"].strip())
            self.assertTrue(row["accepted_answers"])
            self.assertEqual(row["reference_answer"], row["accepted_answers"][0])

    def test_question_hashes(self) -> None:
        for row in self.rows:
            normalized = builder.normalize_question(row["question"])
            expected = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
            self.assertEqual(row["question_sha256"], expected)
            self.assertEqual(row["source_id"], f"triviaqa:{expected[:20]}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
