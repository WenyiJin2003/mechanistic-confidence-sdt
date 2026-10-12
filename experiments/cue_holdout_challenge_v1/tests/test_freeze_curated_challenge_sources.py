import contextlib
import copy
import io
import json
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import freeze_curated_challenge_sources as freezer
import select_challenge_sources as selector


def alphabetic_tag(index):
    value = index + 1
    letters = []
    while value:
        value, remainder = divmod(value - 1, 26)
        letters.append(chr(ord("a") + remainder))
    return "".join(reversed(letters))


def source_row(prefix, index, dataset):
    tag = alphabetic_tag(index)
    prompt = f"Explain focal concept {prefix}{tag} with one clear conclusion."
    response = f"SECRET_RESPONSE_{prefix}_{tag} states the focal conclusion and its supporting account."
    prompt_hash = selector.digest(selector.norm(prompt))
    return {
        "source_id": f"{prefix}-source-{tag}",
        "dataset": dataset,
        "dataset_revision": f"{prefix}-pinned-revision",
        "group_id": f"group-{prefix}-{prompt_hash}",
        "normalized_prompt_sha256": prompt_hash,
        "original_response_sha256": selector.digest(response),
        "development_template_group": selector.template_group(prompt),
        "length_bin": ("short", "medium", "long")[index % 3],
        "prompt": prompt,
        "original_response": response,
        "response_tokens": 100,
    }


def replace_prompt(row, prompt):
    row["prompt"] = prompt
    prompt_hash = selector.digest(selector.norm(prompt))
    row["normalized_prompt_sha256"] = prompt_hash
    row["development_template_group"] = selector.template_group(prompt)


def jsonl(rows):
    return "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows)


def fixture(help_counts=None, backups_per_task=2):
    help_counts = help_counts or {task: 5 for task in selector.TASKS}
    development = [
        source_row("development", index, selector.DATASETS[index % 2])
        for index in range(50)
    ]
    candidates = [copy.deepcopy(row) for row in development]
    curation = []
    cursor = 100
    for task in selector.TASKS:
        for rank in range(1, 11):
            dataset = selector.DATASETS[0] if rank <= help_counts[task] else selector.DATASETS[1]
            row = source_row("curated", cursor, dataset)
            candidates.append(row)
            curation.append({
                "source_id": row["source_id"],
                "selected_task": task,
                "dataset": dataset,
                "selection_status": "primary",
                "rank": rank,
                "quality_rationale": f"PRIVATE_RATIONALE_{task}_{rank}",
                "focal_answer_audit": "pass",
            })
            cursor += 1
        for rank in range(1, backups_per_task + 1):
            dataset = selector.DATASETS[(rank - 1) % 2]
            row = source_row("backup", cursor, dataset)
            candidates.append(row)
            curation.append({
                "source_id": row["source_id"],
                "selected_task": task,
                "dataset": dataset,
                "selection_status": "backup",
                "rank": rank,
                "quality_rationale": f"PRIVATE_BACKUP_RATIONALE_{task}_{rank}",
                "focal_answer_audit": "pass",
            })
            cursor += 1
    plan = {
        task: {
            selector.DATASETS[0]: help_counts[task],
            selector.DATASETS[1]: 10 - help_counts[task],
        }
        for task in selector.TASKS
    }
    return candidates, development, curation, plan


class CuratedFreezeTests(unittest.TestCase):
    def test_valid_curated_set_has_exact_design_and_configurable_task_plan(self):
        help_counts = dict(zip(selector.TASKS, (6, 3, 4, 6, 6)))
        candidates, development, curation, plan = fixture(help_counts)
        artifacts = freezer.build_artifacts(
            candidates, development, curation, dataset_plan={"by_task": plan}
        )

        rows = artifacts["assigned_rows"]
        self.assertEqual(len(rows), 50)
        self.assertEqual(Counter(row["task"] for row in rows), Counter({task: 10 for task in selector.TASKS}))
        self.assertEqual(
            Counter(row["dataset"] for row in rows),
            Counter({dataset: 25 for dataset in selector.DATASETS}),
        )
        self.assertEqual(
            Counter(row["cue_family"] for row in rows),
            Counter({family: 10 for family in selector.CUE_FAMILIES}),
        )
        self.assertEqual(
            Counter(row["length_direction"] for row in rows),
            Counter({direction: 25 for direction in selector.LENGTH_DIRECTIONS}),
        )
        self.assertEqual(artifacts["manifest"]["declared_by_task_dataset"], plan)
        self.assertEqual(artifacts["manifest"]["by_task_dataset"], plan)
        self.assertEqual(artifacts["manifest"]["curation_backup_count"], 10)
        selector.validate_assignment(rows)

    def test_assignment_and_public_artifacts_ignore_order_and_rationale(self):
        candidates, development, curation, _ = fixture()
        first = freezer.build_artifacts(candidates, development, curation)
        reordered = list(reversed(copy.deepcopy(curation)))
        for row in reordered:
            row["quality_rationale"] = "A completely different private rationale"
        second = freezer.build_artifacts(candidates, development, reordered)

        mapping = lambda result: {
            row["source_id"]: (row["task"], row["cue_family"], row["length_direction"])
            for row in result["assigned_rows"]
        }
        self.assertEqual(mapping(first), mapping(second))
        self.assertEqual(first["texts"], second["texts"])

    def test_rejects_incomplete_primary_task_group_and_nonpassing_focal_audit(self):
        candidates, development, curation, _ = fixture()
        incomplete = copy.deepcopy(curation)
        incomplete.pop(next(i for i, row in enumerate(incomplete) if row["selection_status"] == "primary"))
        with self.assertRaisesRegex(ValueError, "exactly 10 primary"):
            freezer.build_artifacts(candidates, development, incomplete)

        failed_audit = copy.deepcopy(curation)
        primary = next(row for row in failed_audit if row["selection_status"] == "primary")
        primary["focal_answer_audit"] = "fail"
        with self.assertRaisesRegex(ValueError, "focal_answer_audit"):
            freezer.build_artifacts(candidates, development, failed_audit)

    def test_accepts_overall_imbalance_and_records_truthful_counts(self):
        help_counts = {task: 5 for task in selector.TASKS}
        help_counts[selector.TASKS[0]] = 6
        candidates, development, curation, _ = fixture(help_counts)
        artifacts = freezer.build_artifacts(candidates, development, curation)
        self.assertEqual(
            artifacts["manifest"]["by_dataset"],
            {selector.DATASETS[0]: 26, selector.DATASETS[1]: 24},
        )
        self.assertFalse(artifacts["manifest"]["dataset_balance_exact_25_each"])
        self.assertEqual(
            artifacts["freeze_record"]["overall_dataset_counts"],
            {selector.DATASETS[0]: 26, selector.DATASETS[1]: 24},
        )
        self.assertFalse(artifacts["freeze_record"]["dataset_balance_exact_25_each"])

    def test_nine_one_task_mix_passes_minimum_one_and_fails_minimum_two(self):
        help_counts = {task: 5 for task in selector.TASKS}
        help_counts[selector.TASKS[0]] = 9
        help_counts[selector.TASKS[1]] = 1
        candidates, development, curation, _ = fixture(help_counts)
        accepted = freezer.build_artifacts(
            candidates, development, curation, minimum_per_task_dataset=1
        )
        self.assertEqual(
            accepted["manifest"]["by_task_dataset"][selector.TASKS[0]],
            {selector.DATASETS[0]: 9, selector.DATASETS[1]: 1},
        )
        self.assertEqual(
            accepted["manifest"]["by_task_dataset"][selector.TASKS[1]],
            {selector.DATASETS[0]: 1, selector.DATASETS[1]: 9},
        )
        with self.assertRaisesRegex(ValueError, "underrepresentation"):
            freezer.build_artifacts(
                candidates, development, curation, minimum_per_task_dataset=2
            )

    def test_configurable_dataset_minimum_is_enforced(self):
        help_counts = {task: 5 for task in selector.TASKS}
        help_counts[selector.TASKS[0]] = 2
        candidates, development, curation, _ = fixture(help_counts)
        accepted = freezer.build_artifacts(
            candidates, development, curation, minimum_per_task_dataset=2
        )
        self.assertEqual(accepted["manifest"]["minimum_per_task_dataset"], 2)
        with self.assertRaisesRegex(ValueError, "underrepresentation"):
            freezer.build_artifacts(
                candidates, development, curation, minimum_per_task_dataset=3
            )
        with self.assertRaisesRegex(ValueError, "0 through 5"):
            freezer.build_artifacts(
                candidates, development, curation, minimum_per_task_dataset=-1
            )

    def test_ten_zero_task_mix_passes_minimum_zero_and_fails_minimum_one(self):
        help_counts = {task: 5 for task in selector.TASKS}
        help_counts[selector.TASKS[0]] = 10
        candidates, development, curation, _ = fixture(help_counts)
        accepted = freezer.build_artifacts(
            candidates, development, curation, minimum_per_task_dataset=0
        )
        self.assertEqual(
            accepted["manifest"]["by_task_dataset"][selector.TASKS[0]],
            {selector.DATASETS[0]: 10, selector.DATASETS[1]: 0},
        )
        self.assertEqual(accepted["manifest"]["minimum_per_task_dataset"], 0)
        with self.assertRaisesRegex(ValueError, "underrepresentation"):
            freezer.build_artifacts(
                candidates, development, curation, minimum_per_task_dataset=1
            )

    def test_declared_dataset_plan_must_match_primary_rows(self):
        candidates, development, curation, plan = fixture()
        mismatched = copy.deepcopy(plan)
        first, second = selector.TASKS[:2]
        mismatched[first][selector.DATASETS[0]] += 1
        mismatched[first][selector.DATASETS[1]] -= 1
        mismatched[second][selector.DATASETS[0]] -= 1
        mismatched[second][selector.DATASETS[1]] += 1
        with self.assertRaisesRegex(ValueError, "do not match"):
            freezer.build_artifacts(candidates, development, curation, dataset_plan=mismatched)

    def test_rejects_each_development_overlap_identity(self):
        for field in freezer.IDENTITY_FIELDS:
            with self.subTest(field=field):
                candidates, development, curation, _ = fixture()
                primary_record = next(row for row in curation if row["selection_status"] == "primary")
                selected = next(row for row in candidates if row["source_id"] == primary_record["source_id"])
                blocker = development[0]
                if field == "source_id":
                    primary_record["source_id"] = blocker["source_id"]
                    primary_record["dataset"] = blocker["dataset"]
                elif field == "group_id":
                    selected["group_id"] = blocker["group_id"]
                elif field == "normalized_prompt_sha256":
                    replace_prompt(selected, blocker["prompt"])
                    selected["group_id"] += "-distinct"
                else:
                    replace_prompt(blocker, "Explain templated focal ocean item 100 with a clear conclusion.")
                    replace_prompt(selected, "Explain templated focal ocean item 200 with a clear conclusion.")
                with self.assertRaisesRegex(ValueError, f"development on {field}"):
                    freezer.build_artifacts(candidates, development, curation)

    def test_rejects_existing_exclusion_and_curated_identity_duplicate(self):
        candidates, development, curation, _ = fixture()
        primary_ids = [
            row["source_id"] for row in curation if row["selection_status"] == "primary"
        ]
        excluded = next(row for row in candidates if row["source_id"] == primary_ids[0])
        excluded["response_tokens"] = 59
        with self.assertRaisesRegex(ValueError, "existing exclusion rule"):
            freezer.build_artifacts(candidates, development, curation)

        candidates, development, curation, _ = fixture()
        first = next(row for row in candidates if row["source_id"] == primary_ids[0])
        second = next(row for row in candidates if row["source_id"] == primary_ids[1])
        second["group_id"] = first["group_id"]
        with self.assertRaisesRegex(ValueError, "duplicate group_id"):
            freezer.build_artifacts(candidates, development, curation)

    def test_exclusion_override_is_exact_narrow_private_and_auditable(self):
        reason = "role_setup_without_substantive_source_answer"
        candidates, development, curation, _ = fixture()
        primary = next(row for row in curation if row["selection_status"] == "primary")
        selected = next(row for row in candidates if row["source_id"] == primary["source_id"])
        replace_prompt(
            selected,
            "I want you to act as a careful budget analyst and give one focal conclusion.",
        )

        with self.assertRaisesRegex(ValueError, reason):
            freezer.build_artifacts(candidates, development, curation)

        exact = copy.deepcopy(curation)
        exact_primary = next(row for row in exact if row["source_id"] == primary["source_id"])
        exact_primary["exclusion_override"] = reason
        exact_primary["override_rationale"] = "PRIVATE_OVERRIDE_RATIONALE_CORRECT_BUDGET"
        accepted = freezer.build_artifacts(candidates, development, exact)
        self.assertEqual(accepted["manifest"]["exclusion_override_count"], 1)
        self.assertEqual(
            accepted["manifest"]["exclusion_override_reason_counts"], {reason: 1}
        )
        self.assertEqual(accepted["freeze_record"]["exclusion_override_count"], 1)
        self.assertIn(
            "PRIVATE_OVERRIDE_RATIONALE_CORRECT_BUDGET",
            accepted["texts"]["challenge_sources_50.jsonl"],
        )
        public_text = (
            accepted["texts"]["challenge_selection_manifest.json"]
            + accepted["texts"]["curated_source_replacement_freeze.json"]
        )
        self.assertNotIn("PRIVATE_OVERRIDE_RATIONALE_CORRECT_BUDGET", public_text)
        self.assertFalse(accepted["manifest"]["contains_override_rationale"])
        self.assertFalse(accepted["freeze_record"]["contains_override_rationale"])

        mismatch = copy.deepcopy(exact)
        mismatch_primary = next(
            row for row in mismatch if row["source_id"] == primary["source_id"]
        )
        mismatch_primary["exclusion_override"] = "too_short_for_initial_content_audit"
        with self.assertRaisesRegex(ValueError, "does not exactly match"):
            freezer.build_artifacts(candidates, development, mismatch)

        corrupt_candidates = copy.deepcopy(candidates)
        corrupt_selected = next(
            row for row in corrupt_candidates if row["source_id"] == primary["source_id"]
        )
        corrupt_selected["normalized_prompt_sha256"] = "not-the-prompt-hash"
        with self.assertRaisesRegex(ValueError, "does not match its prompt"):
            freezer.build_artifacts(corrupt_candidates, development, exact)

        candidates, development, unflagged, _ = fixture()
        unflagged_primary = next(
            row for row in unflagged if row["selection_status"] == "primary"
        )
        unflagged_primary["exclusion_override"] = reason
        with self.assertRaisesRegex(ValueError, "no exclusion rule matched"):
            freezer.build_artifacts(candidates, development, unflagged)

    def test_public_outputs_are_text_and_rationale_free(self):
        candidates, development, curation, _ = fixture()
        artifacts = freezer.build_artifacts(candidates, development, curation)
        public_text = (
            artifacts["texts"]["challenge_selection_manifest.json"]
            + artifacts["texts"]["curated_source_replacement_freeze.json"]
        )
        for row in candidates:
            self.assertNotIn(row["prompt"], public_text)
            self.assertNotIn(row["original_response"], public_text)
        for row in curation:
            self.assertNotIn(row["quality_rationale"], public_text)
        self.assertFalse(artifacts["manifest"]["contains_source_text"])
        self.assertFalse(artifacts["manifest"]["contains_curation_rationale"])
        self.assertFalse(artifacts["manifest"]["score_or_activation_used"])
        self.assertFalse(artifacts["manifest"]["model_inference_used"])
        self.assertEqual(
            set(artifacts["manifest"]["source_records"][0]), set(freezer.PUBLIC_SOURCE_KEYS)
        )

    def test_cli_is_no_write_without_apply_then_writes_expected_artifacts(self):
        candidates, development, curation, plan = fixture()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            candidates_path = root / "candidates.jsonl"
            development_path = root / "development.jsonl"
            curation_path = root / "private_curation.jsonl"
            plan_path = root / "dataset_plan.json"
            private_output = root / "private_output"
            manifest_output = root / "public" / "selection.json"
            freeze_output = root / "public" / "freeze.json"
            candidates_path.write_text(jsonl(candidates), encoding="utf-8")
            development_path.write_text(jsonl(development), encoding="utf-8")
            curation_path.write_text(jsonl(curation), encoding="utf-8")
            plan_path.write_text(json.dumps({"by_task": plan}), encoding="utf-8")
            arguments = [
                "--curation-jsonl", str(curation_path),
                "--candidates-jsonl", str(candidates_path),
                "--development-jsonl", str(development_path),
                "--dataset-plan-json", str(plan_path),
                "--private-output-dir", str(private_output),
                "--manifest-output", str(manifest_output),
                "--freeze-record-output", str(freeze_output),
            ]
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(freezer.main(arguments), 0)
            self.assertFalse(private_output.exists())
            self.assertFalse(manifest_output.exists())
            self.assertFalse(freeze_output.exists())

            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(freezer.main(arguments + ["--apply"]), 0)
            self.assertEqual(len(list(private_output.glob("*.jsonl"))), 6)
            self.assertTrue(manifest_output.is_file())
            self.assertTrue(freeze_output.is_file())
            manifest = json.loads(manifest_output.read_text(encoding="utf-8"))
            freeze_record = json.loads(freeze_output.read_text(encoding="utf-8"))
            self.assertEqual(manifest["source_count"], 50)
            self.assertEqual(freeze_record["replacement_scope_source_count"], 50)

    def test_cli_joins_two_private_curation_files_in_memory(self):
        candidates, development, curation, _ = fixture()
        first_tasks = set(selector.TASKS[:2])
        first_curation = [row for row in curation if row["selected_task"] in first_tasks]
        second_curation = [row for row in curation if row["selected_task"] not in first_tasks]
        self.assertLess(
            sum(row["selection_status"] == "primary" for row in first_curation), 50
        )
        self.assertLess(
            sum(row["selection_status"] == "primary" for row in second_curation), 50
        )

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            candidates_path = root / "candidates.jsonl"
            development_path = root / "development.jsonl"
            first_path = root / "curation_fp.jsonl"
            second_path = root / "curation_mcs.jsonl"
            private_output = root / "private_output"
            manifest_output = root / "public" / "selection.json"
            freeze_output = root / "public" / "freeze.json"
            candidates_path.write_text(jsonl(candidates), encoding="utf-8")
            development_path.write_text(jsonl(development), encoding="utf-8")
            first_path.write_text(jsonl(first_curation), encoding="utf-8")
            second_path.write_text(jsonl(second_curation), encoding="utf-8")

            arguments = [
                "--curation-jsonl", str(first_path),
                "--curation-jsonl", str(second_path),
                "--candidates-jsonl", str(candidates_path),
                "--development-jsonl", str(development_path),
                "--private-output-dir", str(private_output),
                "--manifest-output", str(manifest_output),
                "--freeze-record-output", str(freeze_output),
                "--apply",
            ]
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(freezer.main(arguments), 0)

            manifest = json.loads(manifest_output.read_text(encoding="utf-8"))
            self.assertEqual(manifest["source_count"], 50)
            self.assertEqual(manifest["by_task"], {task: 10 for task in selector.TASKS})
            self.assertTrue((private_output / "challenge_sources_50.jsonl").is_file())
            self.assertTrue(freeze_output.is_file())


if __name__ == "__main__":
    unittest.main()
