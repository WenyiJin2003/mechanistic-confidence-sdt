#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


EXPERIMENT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("aggregate_and_blind", EXPERIMENT / "src/aggregate_and_blind.py")
assert SPEC and SPEC.loader
aggregate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(aggregate)


class DirectEvaluationContractTest(unittest.TestCase):
    def test_blinding_is_deterministic_and_balanced_enough(self) -> None:
        sides = []
        for index in range(1, 501):
            eval_id = f"TQA500-{index:04d}"
            confident_is_a = int(
                __import__("hashlib").sha256(f"{aggregate.BLIND_SEED}\0{eval_id}".encode()).hexdigest(), 16
            ) % 2 == 0
            sides.append(confident_is_a)
        self.assertGreaterEqual(sum(sides), 225)
        self.assertLessEqual(sum(sides), 275)

    def test_frozen_authority(self) -> None:
        authority = json.loads((EXPERIMENT / "DIRECT_EVAL_AUTHORITY.json").read_text(encoding="utf-8"))
        self.assertEqual(authority["allowed_run_ids"], ["confident_r010", "hesitant_r010"])
        self.assertEqual(authority["cohort_rows"], 500)
        self.assertEqual(authority["expected_answer_rows"], 1000)
        self.assertEqual(len(authority["shards"]), 5)
        self.assertTrue(all(shard["rows"] == 100 for shard in authority["shards"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
