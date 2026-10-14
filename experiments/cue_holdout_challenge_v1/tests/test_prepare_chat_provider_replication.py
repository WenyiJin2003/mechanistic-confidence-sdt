from __future__ import annotations

import hashlib
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import prepare_chat_provider_replication as preparer


def make_sources() -> list[dict]:
    rows = []
    for task in preparer.TASKS:
        for family in preparer.CUE_FAMILIES:
            for direction in preparer.DIRECTIONS:
                source_id = f"{task}-{family}-{direction}"
                response = f"Answer for {source_id}."
                rows.append({
                    "source_id": source_id,
                    "original_response_sha256": hashlib.sha256(response.encode()).hexdigest(),
                    "task": task,
                    "cue_family": family,
                    "length_direction": direction,
                    "prompt": f"Prompt for {source_id}?",
                    "original_response": response,
                })
    return rows


class PrepareChatProviderReplicationTests(unittest.TestCase):
    def test_grid_and_batch_plan_cover_each_source_once(self):
        rows = make_sources()
        batches = preparer.make_batches(preparer.validate_source_grid(rows))
        self.assertEqual([len(batch) for batch in batches], [10] * 5)
        expected = Counter(row["source_id"] for row in rows)
        actual = Counter(row["source_id"] for batch in batches for row in batch)
        self.assertEqual(actual, expected)
        for batch in batches:
            self.assertEqual(
                Counter(row["length_direction"] for row in batch),
                Counter({"confident_longer": 5, "hedged_longer": 5}),
            )

    def test_output_directory_must_remain_under_private_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            private = Path(tmp) / "private_data"
            inside = private / "provider_run"
            outside = Path(tmp) / "public"
            self.assertEqual(
                preparer.require_private_output(inside, private_root=private),
                inside.resolve(),
            )
            with self.assertRaisesRegex(ValueError, "private_data"):
                preparer.require_private_output(outside, private_root=private)

    def test_writer_prompt_requests_complete_direct_rewrites(self):
        batch = preparer.make_batches(preparer.validate_source_grid(make_sources()))[0]
        prompt = preparer.writer_prompt(batch, 1)
        self.assertIn("TWO COMPLETE natural rewrites", prompt)
        self.assertIn("Neither member may be the verbatim source", prompt)
        self.assertIn("Ignore every neutral-template, <STANCE_*>", prompt)


if __name__ == "__main__":
    unittest.main()
