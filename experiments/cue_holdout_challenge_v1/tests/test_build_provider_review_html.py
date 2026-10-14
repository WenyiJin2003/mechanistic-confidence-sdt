from __future__ import annotations

import json
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import build_provider_review_html as builder


def make_row(index: int, task: str = "qa", cue_family: str = "modal") -> dict:
    return {
        "source_id": f"source-{index}",
        "prompt": f"Question {index}?",
        "original_response": f"Original answer {index}.",
        "original_response_sha256": f"source-digest-{index}",
        "confident_response": f"The result is clearly answer {index}.",
        "hedged_response": f"The result appears to be answer {index}.",
        "task": task,
        "cue_family": cue_family,
        "length_direction": "confident_longer" if index % 2 else "hedged_longer",
    }


class ProviderReviewHtmlTests(unittest.TestCase):
    def test_packet_omits_original_identity_and_roles(self):
        rows = [make_row(index) for index in range(1, 7)]
        packet, key = builder.build_blinded_rows(rows, seed=17)
        self.assertEqual(packet, builder.build_blinded_rows(rows, seed=17)[0])
        self.assertEqual(len(packet), 6)
        self.assertEqual(
            set(packet[0]), {"review_id", "prompt", "source_answer", "version_a", "version_b"}
        )
        page = builder.render_html(packet, "a" * 64, "Fixture review")
        self.assertIn("Original answer", page)
        self.assertIn("Source answer / 原始回答", page)
        self.assertNotIn("source-", page)
        self.assertNotIn("version_a_role", page)
        self.assertNotIn("confident_response", page)
        self.assertNotIn("hedged_response", page)
        self.assertIn("Prompt / 问题", page)
        for field in builder.REVIEW_FIELDS:
            self.assertIn(f'data-field="{field}"', page)
        self.assertIn("localStorage", page)
        self.assertIn("Download review JSON", page)
        self.assertEqual({item["source_id"] for item in key}, {row["source_id"] for row in rows})

    def test_full_5x5x2_design_cross_balances_length_direction(self):
        rows = []
        index = 0
        for task in [f"task-{n}" for n in range(5)]:
            for cue_family in [f"cue-{n}" for n in range(5)]:
                for direction in ("confident_longer", "hedged_longer"):
                    index += 1
                    row = make_row(index, task=task, cue_family=cue_family)
                    row["length_direction"] = direction
                    rows.append(row)
        assignments = builder.balanced_role_assignments(rows, seed=builder.DEFAULT_SEED)
        cross = {}
        for direction in ("confident_longer", "hedged_longer"):
            cross[direction] = sum(
                assignments[row["source_id"]][0] == "confident"
                for row in rows
                if row["length_direction"] == direction
            )
        self.assertEqual(sum(cross.values()), 25)
        self.assertLessEqual(abs(cross["confident_longer"] - cross["hedged_longer"]), 1)

    def test_actual_frozen_50_cross_balances_when_private_fixture_exists(self):
        source_path = Path(__file__).resolve().parents[1] / "private_data/challenge_sources_50.jsonl"
        if not source_path.exists():
            self.skipTest("private frozen-50 fixture is intentionally absent")
        rows = [json.loads(line) for line in source_path.read_text(encoding="utf-8").splitlines()
                if line.strip()]
        assignments = builder.balanced_role_assignments(rows, seed=builder.DEFAULT_SEED)
        cross = Counter(
            (row["length_direction"], assignments[row["source_id"]][0])
            for row in rows
        )
        self.assertEqual(sum(cross.values()), 50)
        for direction in ("confident_longer", "hedged_longer"):
            self.assertLessEqual(
                abs(cross[(direction, "confident")] - cross[(direction, "hedged")]), 1
            )

    def test_even_design_cells_balance_hidden_a_roles(self):
        rows = []
        index = 0
        for task in ("qa", "code"):
            for cue_family in ("modal", "epistemic"):
                for _ in range(2):
                    index += 1
                    rows.append(make_row(index, task=task, cue_family=cue_family))
        assignments = builder.balanced_role_assignments(rows, seed=23)
        for task in ("qa", "code"):
            for cue_family in ("modal", "epistemic"):
                source_ids = [
                    row["source_id"]
                    for row in rows
                    if row["task"] == task and row["cue_family"] == cue_family
                ]
                a_roles = [assignments[source_id][0] for source_id in source_ids]
                self.assertEqual(sorted(a_roles), ["confident", "hedged"])

    def test_bundle_is_private_and_contains_required_fields(self):
        rows = [make_row(index) for index in range(1, 5)]
        with tempfile.TemporaryDirectory() as tmp:
            private_root = Path(tmp) / "private_data"
            output = private_root / "provider_review"
            manifest = builder.write_review_bundle(
                rows, output, seed=31, private_root=private_root
            )
            self.assertEqual(manifest["pairs"], 4)
            self.assertTrue(manifest["shows_original_response"])
            self.assertEqual(manifest["review_fields"], list(builder.REVIEW_FIELDS))
            self.assertTrue((output / "BLIND_REVIEW.html").exists())
            page = (output / "BLIND_REVIEW.html").read_text(encoding="utf-8")
            self.assertIn("Original answer", page)
            self.assertNotIn("source-1", page)
            key = json.loads((output / "UNBLIND_KEY.json").read_text(encoding="utf-8"))
            self.assertEqual(len(key["pairs"]), 4)

            with self.assertRaisesRegex(ValueError, "private_data"):
                builder.write_review_bundle(
                    rows, Path(tmp) / "public", private_root=private_root
                )


if __name__ == "__main__":
    unittest.main()
