import contextlib
import copy
import hashlib
import io
import json
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import prepare_cross_task_microbatch as preparer


def sha256_text(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def jsonl(rows):
    return "".join(
        json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
        for row in rows
    )


def source_fixture():
    rows = []
    index = 0
    for task in preparer.TASKS:
        for family in preparer.CUE_FAMILIES:
            for direction in preparer.LENGTH_DIRECTIONS:
                prompt = f"PRIVATE_PROMPT_{index} Explain the focal conclusion."
                response = f"PRIVATE_RESPONSE_{index} gives the focal answer."
                rows.append({
                    "source_id": f"source-{index:02d}",
                    "dataset": "fixture/dataset",
                    "dataset_revision": "fixture-revision",
                    "group_id": f"group-{index:02d}",
                    "normalized_prompt_sha256": sha256_text(
                        preparer._normalize_prompt(prompt)
                    ),
                    "original_response_sha256": sha256_text(response),
                    "development_template_group": f"template-{index:02d}",
                    "task": task,
                    "length_bin": ("short", "medium", "long")[index % 3],
                    "prompt": prompt,
                    "original_response": response,
                    "cue_family": family,
                    "length_direction": direction,
                })
                index += 1
    return rows


def selection_manifest(rows, source_bytes):
    return {
        "selection_version": 2,
        "source_count": 50,
        "private_output_sha256": {
            "challenge_sources_50.jsonl": hashlib.sha256(source_bytes).hexdigest(),
        },
        "source_records": [
            {key: row[key] for key in preparer.FROZEN_PUBLIC_RECORD_KEYS}
            for row in rows
        ],
    }


def fixture_artifacts(rows=None):
    rows = rows or source_fixture()
    source_bytes = jsonl(rows).encode("utf-8")
    manifest = selection_manifest(rows, source_bytes)
    manifest_bytes = (json.dumps(manifest, sort_keys=True) + "\n").encode("utf-8")
    return preparer.build_artifacts(rows, source_bytes, manifest, manifest_bytes)


class CrossTaskMicrobatchTests(unittest.TestCase):
    def test_exact_selection_is_reproducible_and_balanced(self):
        rows = source_fixture()
        artifacts = fixture_artifacts(rows)
        selected = artifacts["selected_rows"]

        self.assertEqual(
            [
                (row["task"], row["cue_family"], row["length_direction"])
                for row in selected
            ],
            preparer.CELL_PLAN,
        )
        self.assertEqual(len(selected), 10)
        self.assertEqual(
            Counter(row["task"] for row in selected),
            Counter({task: 2 for task in preparer.TASKS}),
        )
        self.assertEqual(
            Counter(row["cue_family"] for row in selected),
            Counter({family: 2 for family in preparer.CUE_FAMILIES}),
        )
        self.assertEqual(
            Counter(row["length_direction"] for row in selected),
            Counter({direction: 5 for direction in preparer.LENGTH_DIRECTIONS}),
        )
        self.assertEqual(
            set(artifacts["private_rows"][0]), set(preparer.REWRITE_INPUT_KEYS)
        )
        self.assertEqual(
            artifacts["manifest"]["private_output_sha256"],
            sha256_text(
                artifacts["texts"]["rewrite_input_cross_task_microbatch.jsonl"]
            ),
        )

        reversed_rows = list(reversed(rows))
        reversed_artifacts = fixture_artifacts(reversed_rows)
        self.assertEqual(
            artifacts["texts"]["rewrite_input_cross_task_microbatch.jsonl"],
            reversed_artifacts["texts"]["rewrite_input_cross_task_microbatch.jsonl"],
        )

    def test_missing_and_duplicate_design_cells_are_rejected(self):
        rows = source_fixture()
        missing = copy.deepcopy(rows)
        missing_row = next(
            row
            for row in missing
            if (row["task"], row["cue_family"], row["length_direction"])
            == preparer.CELL_PLAN[0]
        )
        missing_row["cue_family"] = "unregistered_family"
        missing_bytes = jsonl(missing).encode("utf-8")
        with self.assertRaisesRegex(ValueError, "missing cells"):
            preparer.build_artifacts(
                missing,
                missing_bytes,
                selection_manifest(missing, missing_bytes),
            )

        duplicate = copy.deepcopy(rows)
        duplicate_row = next(
            row
            for row in duplicate
            if (row["task"], row["cue_family"], row["length_direction"])
            == preparer.CELL_PLAN[1]
        )
        duplicate_row["task"], duplicate_row["cue_family"], duplicate_row[
            "length_direction"
        ] = preparer.CELL_PLAN[0]
        duplicate_bytes = jsonl(duplicate).encode("utf-8")
        with self.assertRaisesRegex(ValueError, "duplicate cells"):
            preparer.build_artifacts(
                duplicate,
                duplicate_bytes,
                selection_manifest(duplicate, duplicate_bytes),
            )

    def test_row_and_frozen_file_hash_mismatches_are_rejected(self):
        rows = source_fixture()
        corrupted = copy.deepcopy(rows)
        corrupted[0]["original_response"] += " changed"
        corrupted_bytes = jsonl(corrupted).encode("utf-8")
        with self.assertRaisesRegex(ValueError, "original_response_sha256"):
            preparer.build_artifacts(
                corrupted,
                corrupted_bytes,
                selection_manifest(corrupted, corrupted_bytes),
            )

        source_bytes = jsonl(rows).encode("utf-8")
        bad_manifest = selection_manifest(rows, source_bytes)
        bad_manifest["private_output_sha256"]["challenge_sources_50.jsonl"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "selection manifest"):
            preparer.build_artifacts(rows, source_bytes, bad_manifest)

    def test_cli_defaults_to_no_write_and_apply_writes_both_outputs(self):
        rows = source_fixture()
        source_text = jsonl(rows)
        source_bytes = source_text.encode("utf-8")
        manifest = selection_manifest(rows, source_bytes)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sources = root / "private" / "challenge_sources_50.jsonl"
            source_manifest = root / "public" / "challenge_selection_manifest.json"
            private_output = root / "private" / "rewrite_input_cross_task_microbatch.jsonl"
            public_output = root / "public" / "cross_task_microbatch_manifest.json"
            sources.parent.mkdir(parents=True)
            source_manifest.parent.mkdir(parents=True)
            sources.write_text(source_text, encoding="utf-8")
            source_manifest.write_text(
                json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
            arguments = [
                "--sources", str(sources),
                "--selection-manifest", str(source_manifest),
                "--private-output", str(private_output),
                "--manifest-output", str(public_output),
            ]

            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(preparer.main(arguments), 0)
            self.assertFalse(private_output.exists())
            self.assertFalse(public_output.exists())
            self.assertFalse(json.loads(output.getvalue())["applied"])

            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(preparer.main(arguments + ["--apply"]), 0)
            self.assertTrue(private_output.is_file())
            self.assertTrue(public_output.is_file())
            self.assertEqual(
                len([line for line in private_output.read_text().splitlines() if line]), 10
            )
            self.assertTrue(json.loads(output.getvalue())["applied"])

    def test_public_manifest_contains_metadata_but_no_private_text(self):
        rows = source_fixture()
        artifacts = fixture_artifacts(rows)
        manifest = artifacts["manifest"]
        public_text = artifacts["texts"]["cross_task_microbatch_manifest.json"]

        self.assertEqual(manifest["source_count"], 10)
        self.assertEqual(len(manifest["source_ids"]), 10)
        self.assertEqual(len(manifest["source_records"]), 10)
        self.assertEqual(len(manifest["cell_plan"]), 10)
        self.assertFalse(manifest["contains_source_text"])
        self.assertFalse(manifest["score_or_activation_used"])
        self.assertFalse(manifest["model_inference_used"])
        self.assertNotIn('"prompt"', public_text)
        self.assertNotIn('"original_response"', public_text)
        for row in rows:
            self.assertNotIn(row["prompt"], public_text)
            self.assertNotIn(row["original_response"], public_text)
        self.assertEqual(
            set(manifest["source_records"][0]), set(preparer.PUBLIC_RECORD_KEYS)
        )


if __name__ == "__main__":
    unittest.main()
