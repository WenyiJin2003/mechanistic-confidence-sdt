import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import select_challenge_sources as selector


class SelectionInvariantTests(unittest.TestCase):
    def candidate(self, source_id, group_id, prompt_hash, prompt, dataset="nvidia/HelpSteer2"):
        return {
            "source_id": source_id,
            "group_id": group_id,
            "normalized_prompt_sha256": prompt_hash,
            "prompt": prompt,
            "original_response": "A substantive source response with enough words to pass the initial length screen. " * 10,
            "response_tokens": 100,
            "dataset": dataset,
            "length_bin": "medium",
        }

    def test_screen_excludes_each_current_overlap_key(self):
        prompt = "Explain a stable factual concept clearly"
        current = [{
            "source_id": "old-id", "group_id": "old-group", "normalized_prompt_sha256": "old-hash",
            "development_template_group": selector.template_group("Old unrelated prompt"), "prompt": "Old unrelated prompt",
        }]
        duplicate_template_prompt = "Explain another stable factual concept clearly"
        candidates = [
            self.candidate("old-id", "g1", "h1", prompt),
            self.candidate("new-id", "old-group", "h2", prompt + " now"),
            self.candidate("new-id2", "g2", "old-hash", prompt + " again"),
            self.candidate("new-id3", "g3", "h3", "Old unrelated prompt"),
            self.candidate("valid-id", "valid-group", "valid-hash", duplicate_template_prompt),
        ]
        screened, rejected = selector.screen_candidates(candidates, current)
        self.assertEqual([row["source_id"] for row in screened], ["valid-id"])
        self.assertEqual(sum(rejected.values()), 4)
        self.assertEqual(rejected["source_id_overlap"], 1)
        self.assertEqual(rejected["group_id_overlap"], 1)
        self.assertEqual(rejected["prompt_hash_overlap"], 1)
        self.assertEqual(rejected["template_group_overlap"], 1)

    def test_condition_assignment_has_exact_cell_counterbalance(self):
        rows = []
        for task_index, task in enumerate(selector.TASKS):
            for index in range(10):
                rows.append({
                    "source_id": f"s-{task_index}-{index}",
                    "group_id": f"g-{task_index}-{index}",
                    "normalized_prompt_sha256": f"p-{task_index}-{index}",
                    "task": task,
                    "dataset": selector.DATASETS[(task_index + index) % 2],
                    "length_bin": ["short", "medium", "long"][index % 3],
                    "development_template_group": f"template-{task_index}-{index}",
                })
        assigned = selector.assign_conditions(rows)
        selector.validate_assignment(assigned)
        for task in selector.TASKS:
            for family in selector.CUE_FAMILIES:
                cell = [row for row in assigned if row["task"] == task and row["cue_family"] == family]
                self.assertEqual(len(cell), 2)
                self.assertEqual({row["length_direction"] for row in cell}, set(selector.LENGTH_DIRECTIONS))


if __name__ == "__main__":
    unittest.main()
