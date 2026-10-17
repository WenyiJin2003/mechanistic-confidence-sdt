import hashlib
import importlib.util
import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from unittest import mock


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "build_factual_rewrite_repair_prompt.py"
)
SPEC = importlib.util.spec_from_file_location(
    "build_factual_rewrite_repair_prompt", MODULE_PATH
)
builder = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(builder)


def sha256_text(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def source_row(index):
    original = f"Frozen factual answer {index} preserves every required claim."
    return {
        "source_id": f"source-{index}",
        "dataset": "asqa" if index % 2 else "billsum",
        "group_id": f"group-{index}",
        "source_hash": sha256_text(f"source-{index}"),
        "original_response_sha256": sha256_text(original),
        "profile": "mid_plain",
        "prompt": f"What is answer {index}?",
        "original_response": original,
        "protected_spans": [f"required claim"],
        "cue_family": "embedded_stance_predicate",
        "length_direction": "hesitant_longer" if index % 2 else "confident_longer",
        "draft_order": "hesitant_first" if index % 2 else "confident_first",
        "generation_order": index,
    }


def candidate_row(source, marker):
    return {
        "source_id": source["source_id"],
        "source_hash": source["source_hash"],
        "original_response_sha256": source["original_response_sha256"],
        "dataset": source["dataset"],
        "cue_family": source["cue_family"],
        "length_direction": source["length_direction"],
        "draft_order": source["draft_order"],
        "confident_response": f"Confident prior arm {marker}.",
        "hesitant_response": f"I read the hesitant prior arm {marker}.",
        "issues": [],
    }


def write_jsonl(path, rows):
    path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


class BuildFactualRewriteRepairPromptTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.private_root = self.root / "private_data"
        self.private_root.mkdir()
        self.sources = [source_row(1), source_row(2), source_row(3)]
        self.source_path = self.root / "writer_sources.jsonl"
        self.candidate_path = self.root / "candidates.jsonl"
        write_jsonl(self.source_path, self.sources)
        write_jsonl(
            self.candidate_path,
            [
                candidate_row(self.sources[0], "PRIVATE-CANDIDATE-ONE"),
                candidate_row(self.sources[1], "PRIVATE-CANDIDATE-TWO"),
                candidate_row(self.sources[2], "PRIVATE-CANDIDATE-THREE"),
            ],
        )
        self.spec_path = self.root / "repair_spec.json"
        self.validator_path = self.private_root / "validator.json"
        self.ledger_path = self.private_root / "repair_budget.json"
        self.write_spec(["source-2", "source-1"])

    def tearDown(self):
        self.temporary_directory.cleanup()

    def validator_row(self, source, candidate, **updates):
        if source["length_direction"] == "confident_longer":
            confident_tokens, hesitant_tokens = 110, 104
        else:
            confident_tokens, hesitant_tokens = 104, 110
        row = {
            "source_id": source["source_id"],
            "dataset": source["dataset"],
            "group_id": source["group_id"],
            "source_hash": source["source_hash"],
            "original_response_sha256": source["original_response_sha256"],
            "cue_family": source["cue_family"],
            "length_direction": source["length_direction"],
            "draft_order": source["draft_order"],
            "generation_order": source["generation_order"],
            "confident_response_sha256": sha256_text(
                candidate["confident_response"]
            ),
            "hesitant_response_sha256": sha256_text(candidate["hesitant_response"]),
            "validation_status": "fail",
            "mechanical_gate_pass": False,
            "failure_flags": ["pair_token_gap_over_limit"],
            "token_counts": {
                "source": 100,
                "confident": confident_tokens,
                "hesitant": hesitant_tokens,
                "absolute_gap": 6,
                "allowed_gap": 5.35,
                "direction_correct": True,
            },
        }
        row.update(updates)
        return row

    def write_validator(self, target_ids, row_updates=None):
        row_updates = row_updates or {}
        source_map = {row["source_id"]: row for row in self.sources}
        candidates = builder._read_records(self.candidate_path)
        candidate_map = {row["source_id"]: row for row in candidates}
        rows = [
            self.validator_row(
                source_map[source_id],
                candidate_map[source_id],
                **row_updates.get(source_id, {}),
            )
            for source_id in target_ids
        ]
        self.validator_path.write_text(
            json.dumps(
                {
                    "schema_version": builder.VALIDATOR_SCHEMA_VERSION,
                    "validator": builder.VALIDATOR_NAME,
                    "rows": rows,
                }
            ),
            encoding="utf-8",
        )

    def write_ledger(self, target_ids, repair_stage, entry_updates=None):
        entry_updates = entry_updates or {}
        repair_spec = json.loads(self.spec_path.read_text(encoding="utf-8"))
        source_map = {row["source_id"]: row for row in self.sources}
        candidates = builder._read_records(self.candidate_path)
        candidate_map = {row["source_id"]: row for row in candidates}
        expected_count = 0 if repair_stage == "first_full_pair" else 1
        entries = []
        for source_id in target_ids:
            source = source_map[source_id]
            candidate = candidate_map[source_id]
            entry = {
                "source_id": source_id,
                "source_hash": source["source_hash"],
                "original_response_sha256": source["original_response_sha256"],
                "confident_response_sha256": sha256_text(
                    candidate["confident_response"]
                ),
                "hesitant_response_sha256": sha256_text(
                    candidate["hesitant_response"]
                ),
                "counted_repairs": expected_count,
            }
            entry.update(entry_updates.get(source_id, {}))
            entries.append(entry)
        self.ledger_path.write_text(
            json.dumps(
                {
                    "schema_version": builder.BUDGET_LEDGER_SCHEMA_VERSION,
                    "repair_id": repair_spec["repair_id"],
                    "repair_stage": repair_stage,
                    "entries": entries,
                }
            ),
            encoding="utf-8",
        )

    def write_spec(self, target_ids, **updates):
        payload = {
            "schema_version": builder.SPEC_SCHEMA_VERSION,
            "repair_id": "batch-length-repair",
            "repair_stage": "first_full_pair",
            "target_source_ids": target_ids,
            "failure_codes": ["frozen_length_policy_violation"],
            "banned_surface_forms": [],
        }
        payload.update(updates)
        self.spec_path.write_text(json.dumps(payload), encoding="utf-8")
        stage = payload.get("repair_stage", "first_full_pair")
        self.write_validator(target_ids)
        self.write_ledger(target_ids, stage)

    def build(self, stem="repair", **kwargs):
        prompt_path = self.private_root / f"{stem}.txt"
        manifest_path = self.private_root / f"{stem}.manifest.json"
        manifest = builder.build_repair_prompt_artifacts(
            kwargs.pop("sources_path", self.source_path),
            kwargs.pop("candidate_paths", [self.candidate_path]),
            kwargs.pop("spec_path", self.spec_path),
            kwargs.pop("validator_report_path", self.validator_path),
            kwargs.pop("repair_budget_ledger_path", self.ledger_path),
            prompt_path,
            manifest_path,
            private_root=self.private_root,
            **kwargs,
        )
        return prompt_path, manifest_path, manifest

    def test_grouped_prompt_is_deterministic_and_never_exposes_prior_arms(self):
        first_prompt, _, first_manifest = self.build("first")
        second_prompt, _, second_manifest = self.build("second")

        first_text = first_prompt.read_text(encoding="utf-8")
        second_text = second_prompt.read_text(encoding="utf-8")
        self.assertEqual(first_text, second_text)
        self.assertNotIn("PRIVATE-CANDIDATE-ONE", first_text)
        self.assertNotIn("PRIVATE-CANDIDATE-TWO", first_text)
        self.assertNotIn("Confident prior arm", first_text)
        self.assertNotIn("hesitant prior arm", first_text)
        self.assertIn("Frozen factual answer 1", first_text)
        self.assertIn("Frozen factual answer 2", first_text)
        self.assertNotIn("Frozen factual answer 3", first_text)
        self.assertLess(first_text.index('"source_id":"source-1"'), first_text.index('"source_id":"source-2"'))
        self.assertFalse(
            first_manifest["writer_safety"]["prior_candidate_arms_exposed_in_prompt"]
        )
        self.assertTrue(
            first_manifest["writer_safety"][
                "candidate_response_text_used_for_integrity_checks_only"
            ]
        )
        self.assertFalse(
            first_manifest["writer_safety"]["nonempty_surface_form_bans_allowed"]
        )
        self.assertEqual(first_manifest["repair_stage"], "first_full_pair")
        self.assertEqual(
            first_manifest["output"]["sha256"],
            hashlib.sha256(first_prompt.read_bytes()).hexdigest(),
        )
        self.assertEqual(
            first_manifest["output"]["sha256"], second_manifest["output"]["sha256"]
        )

    def test_isolated_prompt_contains_identity_assignments_constraints_and_schema(self):
        self.write_spec(
            ["source-1"],
            banned_surface_forms=[],
            repair_id="qasper-cue-repair",
        )
        prompt_path, _, manifest = self.build()
        text = prompt_path.read_text(encoding="utf-8")

        self.assertEqual(manifest["target_source_ids"], ["source-1"])
        self.assertIn('"cue_family":"embedded_stance_predicate"', text)
        self.assertIn('"length_direction":"hesitant_longer"', text)
        self.assertIn('"draft_order":"hesitant_first"', text)
        output = json.loads(
            text.split("OUTPUT_SCHEMA_JSON\n", 1)[1].split("\n\nINPUT_RECORDS_JSON", 1)[0]
        )
        self.assertEqual(len(output["pairs"]), 1)
        self.assertEqual(output["pairs"][0]["source_hash"], self.sources[0]["source_hash"])
        self.assertEqual(
            list(output["pairs"][0]).index("hesitant_response")
            < list(output["pairs"][0]).index("confident_response"),
            True,
        )

    def test_length_policy_repair_is_typed_and_writer_safe(self):
        self.write_spec(
            ["source-1", "source-2"],
            repair_id="batch-length-policy-repair",
            failure_codes=["frozen_length_policy_violation"],
            banned_surface_forms=[],
        )

        prompt_path, _, manifest = self.build()
        text = prompt_path.read_text(encoding="utf-8")

        self.assertEqual(
            manifest["failure_codes"], ["frozen_length_policy_violation"]
        )
        self.assertIn("frozen length constraints", text)
        self.assertIn("assigned length_direction strict rather than tied", text)
        self.assertNotIn("PRIVATE-CANDIDATE", text)

    def test_reviewer_only_source_field_is_rejected_without_outputs(self):
        contaminated = [dict(row) for row in self.sources]
        contaminated[0]["protected_qualifiers"] = ["DO-NOT-LEAK-REVIEWER-TEXT"]
        write_jsonl(self.source_path, contaminated)

        with self.assertRaises(builder.RepairPromptError) as caught:
            self.build()

        self.assertTrue(
            any("forbidden_source_field" in error for error in caught.exception.errors)
        )
        self.assertFalse((self.private_root / "repair.txt").exists())
        self.assertFalse((self.private_root / "repair.manifest.json").exists())

    def test_reviewer_only_candidate_field_is_rejected(self):
        candidates = [candidate_row(self.sources[0], "ONE")]
        candidates[0]["evidence"] = "DO-NOT-LEAK-EVIDENCE"
        write_jsonl(self.candidate_path, candidates)
        self.write_spec(["source-1"])

        with self.assertRaises(builder.RepairPromptError) as caught:
            self.build()

        self.assertTrue(
            any("forbidden_candidate_field" in error for error in caught.exception.errors)
        )

    def test_content_checklist_and_freeform_repair_notes_are_rejected(self):
        self.write_spec(
            ["source-1"],
            banned_surface_forms=["I read"],
            content_checklist=["DO-NOT-LEAK"],
            repair_notes="Preserve a reviewer-authored interpretation.",
        )

        with self.assertRaises(builder.RepairPromptError) as caught:
            self.build()

        errors = caught.exception.errors
        self.assertTrue(any("forbidden_repair_spec_field" in error for error in errors))
        self.assertTrue(any("unknown_repair_spec_field:repair_notes" in error for error in errors))

    def test_nonempty_banned_surface_forms_are_forbidden(self):
        self.write_spec(["source-1"], banned_surface_forms=["never generated phrase"])
        with self.assertRaises(builder.RepairPromptError) as caught:
            self.build("nonempty-ban")
        self.assertTrue(
            any(
                "nonempty_banned_surface_forms_forbidden_without_preregistered_lexicon"
                in error
                for error in caught.exception.errors
            )
        )

    def test_unbound_nonlength_failure_codes_are_rejected(self):
        self.write_spec(
            ["source-1"],
            failure_codes=["assigned_cue_family_not_realized"],
        )
        with self.assertRaises(builder.RepairPromptError) as caught:
            self.build("unbound-reason")
        self.assertIn(
            "failure_code_not_allowed:assigned_cue_family_not_realized",
            caught.exception.errors,
        )

    def test_candidate_identity_mismatch_is_rejected(self):
        candidates = [candidate_row(self.sources[0], "ONE")]
        candidates[0]["source_hash"] = sha256_text("different")
        write_jsonl(self.candidate_path, candidates)
        self.write_spec(["source-1"])

        with self.assertRaises(builder.RepairPromptError) as caught:
            self.build()

        self.assertTrue(
            any(
                error == "candidate_identity_mismatch:source-1:source_hash"
                for error in caught.exception.errors
            )
        )

    def test_multiple_candidate_files_never_expose_candidate_text(self):
        first_candidates = self.root / "first_candidates.jsonl"
        second_candidates = self.root / "second_candidates.jsonl"
        all_candidates = builder._read_records(self.candidate_path)
        write_jsonl(first_candidates, [all_candidates[0]])
        write_jsonl(second_candidates, [all_candidates[1]])

        prompt_path, _, manifest = self.build(
            candidate_paths=[first_candidates, second_candidates]
        )

        self.assertEqual(len(manifest["inputs"]["candidate_pairs"]), 2)
        self.assertNotIn("PRIVATE-CANDIDATE", prompt_path.read_text(encoding="utf-8"))

    def test_manifest_binds_private_validator_and_budget_ledger(self):
        _, _, manifest = self.build()

        self.assertEqual(
            manifest["inputs"]["validator_report"]["sha256"],
            hashlib.sha256(self.validator_path.read_bytes()).hexdigest(),
        )
        self.assertEqual(
            manifest["inputs"]["repair_budget_ledger"]["sha256"],
            hashlib.sha256(self.ledger_path.read_bytes()).hexdigest(),
        )
        self.assertEqual(
            set(manifest["inputs"]["target_validator_row_sha256"]),
            {"source-1", "source-2"},
        )
        self.assertEqual(
            set(manifest["inputs"]["target_repair_budget_entry_sha256"]),
            {"source-1", "source-2"},
        )
        self.assertNotIn("banned_surface_form_count", manifest)
        self.assertNotIn("banned_surface_forms_sha256", manifest)

    def test_manifest_hashes_the_same_input_snapshot_that_was_validated(self):
        original_validator = self.validator_path.read_bytes()
        real_validate_budget = builder._validate_budget_ledger

        def mutate_after_validator_snapshot(*args, **kwargs):
            self.validator_path.write_text("{}", encoding="utf-8")
            return real_validate_budget(*args, **kwargs)

        with mock.patch.object(
            builder,
            "_validate_budget_ledger",
            side_effect=mutate_after_validator_snapshot,
        ):
            _, _, manifest = self.build("snapshot-binding")

        self.assertEqual(self.validator_path.read_bytes(), b"{}")
        self.assertEqual(
            manifest["inputs"]["validator_report"]["sha256"],
            hashlib.sha256(original_validator).hexdigest(),
        )
        self.assertNotEqual(
            manifest["inputs"]["validator_report"]["sha256"],
            hashlib.sha256(self.validator_path.read_bytes()).hexdigest(),
        )

    def test_validator_input_must_be_private(self):
        outside = self.root / "validator.json"
        outside.write_bytes(self.validator_path.read_bytes())
        with self.assertRaises(builder.RepairPromptError) as caught:
            self.build("outside-validator", validator_report_path=outside)
        self.assertTrue(
            any(
                "private_input_outside_private_data:validator_report" in error
                for error in caught.exception.errors
            )
        )

        outside_ledger = self.root / "repair_budget.json"
        outside_ledger.write_bytes(self.ledger_path.read_bytes())
        with self.assertRaises(builder.RepairPromptError) as caught:
            self.build(
                "outside-ledger", repair_budget_ledger_path=outside_ledger
            )
        self.assertTrue(
            any(
                "private_input_outside_private_data:repair_budget_ledger" in error
                for error in caught.exception.errors
            )
        )

    def test_validator_identity_and_response_hash_mismatches_are_rejected(self):
        self.write_validator(
            ["source-2", "source-1"],
            {
                "source-1": {
                    "dataset": "wrong",
                    "confident_response_sha256": "0" * 64,
                }
            },
        )
        with self.assertRaises(builder.RepairPromptError) as caught:
            self.build("validator-mismatch")
        self.assertIn(
            "validator_identity_mismatch:source-1:dataset", caught.exception.errors
        )
        self.assertIn(
            "validator_response_hash_mismatch:source-1:confident",
            caught.exception.errors,
        )

    def test_target_must_be_an_actual_validator_failure(self):
        self.write_validator(
            ["source-2", "source-1"],
            {
                "source-1": {
                    "failure_flags": [],
                    "validation_status": "pass",
                    "mechanical_gate_pass": True,
                }
            },
        )
        with self.assertRaises(builder.RepairPromptError) as caught:
            self.build("not-failed")
        self.assertIn(
            "validator_target_failure_flags_invalid:source-1",
            caught.exception.errors,
        )
        self.assertTrue(
            any(
                error.startswith("validator_target_not_failed:source-1")
                for error in caught.exception.errors
            )
        )

    def test_frozen_length_failure_rejects_non_length_flags(self):
        self.write_validator(
            ["source-2", "source-1"],
            {
                "source-1": {
                    "failure_flags": [
                        "pair_token_gap_over_limit",
                        "pair_structure_mismatch",
                    ]
                }
            },
        )
        with self.assertRaises(builder.RepairPromptError) as caught:
            self.build("mixed-failures")
        self.assertTrue(
            any(
                error.startswith("frozen_length_failure_has_non_length_flags:source-1")
                for error in caught.exception.errors
            )
        )

    def test_first_full_pair_requires_zero_counted_repairs(self):
        self.write_ledger(
            ["source-2", "source-1"],
            "first_full_pair",
            {"source-1": {"counted_repairs": 1}},
        )
        with self.assertRaises(builder.RepairPromptError) as caught:
            self.build("bad-first-budget")
        self.assertTrue(
            any(
                error.startswith(
                    "repair_budget_count_mismatch:source-1:first_full_pair:expected_0"
                )
                for error in caught.exception.errors
            )
        )

    def test_budget_ledger_must_bind_repair_id_and_stage(self):
        payload = json.loads(self.ledger_path.read_text(encoding="utf-8"))
        payload["repair_id"] = "different-repair"
        payload["repair_stage"] = "final_length_only"
        self.ledger_path.write_text(json.dumps(payload), encoding="utf-8")
        with self.assertRaises(builder.RepairPromptError) as caught:
            self.build("ledger-request-mismatch")
        self.assertIn(
            "repair_budget_ledger_repair_id_mismatch", caught.exception.errors
        )
        self.assertIn(
            "repair_budget_ledger_repair_stage_mismatch", caught.exception.errors
        )

    def test_budget_ledger_target_and_candidate_hash_mismatch_are_rejected(self):
        self.write_ledger(
            ["source-1"],
            "first_full_pair",
            {"source-1": {"hesitant_response_sha256": "0" * 64}},
        )
        with self.assertRaises(builder.RepairPromptError) as caught:
            self.build("bad-ledger")
        self.assertIn(
            "repair_budget_ledger_target_set_mismatch", caught.exception.errors
        )
        self.assertIn(
            "repair_budget_candidate_hash_mismatch:source-1:hesitant",
            caught.exception.errors,
        )

    def prepare_final_length_only(self, row_updates=None, ledger_updates=None):
        self.write_spec(
            ["source-1"],
            repair_stage="final_length_only",
            repair_id="final-length-only",
        )
        self.write_validator(["source-1"], row_updates or {})
        self.write_ledger(
            ["source-1"], "final_length_only", ledger_updates or {}
        )

    def test_final_length_only_valid_case_is_typed_and_bound(self):
        self.prepare_final_length_only()
        prompt_path, _, manifest = self.build()
        text = prompt_path.read_text(encoding="utf-8")

        self.assertEqual(manifest["repair_stage"], "final_length_only")
        self.assertNotIn("final permitted length-only correction", text)
        self.assertNotIn('"repair_stage"', text)
        self.assertNotIn("counted_repairs", text)
        self.assertNotIn("PRIVATE-CANDIDATE", text)

    def test_repair_stage_and_budget_do_not_change_prompt_bytes(self):
        self.write_spec(["source-1"], repair_id="stage-invariant-repair")
        first_prompt, _, _ = self.build("first-stage")
        first_bytes = first_prompt.read_bytes()

        self.write_spec(
            ["source-1"],
            repair_id="stage-invariant-repair",
            repair_stage="final_length_only",
        )
        final_prompt, _, _ = self.build("final-stage")

        self.assertEqual(first_bytes, final_prompt.read_bytes())

    def test_final_length_only_requires_one_counted_repair(self):
        self.prepare_final_length_only(
            ledger_updates={"source-1": {"counted_repairs": 0}}
        )
        with self.assertRaises(builder.RepairPromptError) as caught:
            self.build("bad-final-budget")
        self.assertTrue(
            any(
                error.startswith(
                    "repair_budget_count_mismatch:source-1:final_length_only:expected_1"
                )
                for error in caught.exception.errors
            )
        )

    def test_final_length_only_requires_only_gap_flag(self):
        self.prepare_final_length_only(
            {"source-1": {"failure_flags": ["pair_token_ratio_over_limit"]}}
        )
        with self.assertRaises(builder.RepairPromptError) as caught:
            self.build("bad-final-flags")
        self.assertIn(
            "final_length_only_failure_flags_invalid:source-1",
            caught.exception.errors,
        )

    def test_final_length_only_requires_correct_direction(self):
        self.prepare_final_length_only(
            {
                "source-1": {
                    "token_counts": {
                        "source": 100,
                        "confident": 110,
                        "hesitant": 104,
                        "absolute_gap": 6,
                        "allowed_gap": 5.5,
                        "direction_correct": False,
                    }
                }
            }
        )
        with self.assertRaises(builder.RepairPromptError) as caught:
            self.build("bad-final-direction")
        self.assertIn(
            "final_length_only_direction_incorrect:source-1",
            caught.exception.errors,
        )

    def test_final_length_only_gap_excess_must_be_at_most_two_tokens(self):
        self.prepare_final_length_only(
            {
                "source-1": {
                    "token_counts": {
                        "source": 100,
                        "confident": 104,
                        "hesitant": 112,
                        "absolute_gap": 8,
                        "allowed_gap": 5.4,
                        "direction_correct": True,
                    }
                }
            }
        )
        with self.assertRaises(builder.RepairPromptError) as caught:
            self.build("bad-final-gap")
        self.assertIn(
            "final_length_only_gap_excess_invalid:source-1",
            caught.exception.errors,
        )

    def test_final_length_only_accepts_exact_two_token_excess(self):
        self.prepare_final_length_only(
            {
                "source-1": {
                    "token_counts": {
                        "source": 100,
                        "confident": 96,
                        "hesitant": 103,
                        "absolute_gap": 7,
                        "allowed_gap": 5.0,
                        "direction_correct": True,
                    }
                }
            }
        )
        _, _, manifest = self.build("exact-two-gap")
        self.assertEqual(manifest["repair_stage"], "final_length_only")

    def test_final_length_only_recomputes_counts_and_metrics(self):
        self.prepare_final_length_only(
            {
                "source-1": {
                    "token_counts": {
                        "absolute_gap": 6,
                        "allowed_gap": 5.35,
                        "direction_correct": True,
                    }
                }
            }
        )
        with self.assertRaises(builder.RepairPromptError) as caught:
            self.build("missing-arm-counts")
        self.assertIn(
            "final_length_only_token_counts_invalid:source-1",
            caught.exception.errors,
        )

        self.prepare_final_length_only(
            {
                "source-1": {
                    "token_counts": {
                        "source": 100,
                        "confident": 104,
                        "hesitant": 110,
                        "absolute_gap": 5,
                        "allowed_gap": 5.35,
                        "direction_correct": True,
                    }
                }
            }
        )
        with self.assertRaises(builder.RepairPromptError) as caught:
            self.build("contradictory-gap")
        self.assertIn(
            "final_length_only_absolute_gap_mismatch:source-1",
            caught.exception.errors,
        )

    def test_final_length_only_rejects_nonfinite_gap_metrics(self):
        self.prepare_final_length_only(
            {
                "source-1": {
                    "token_counts": {
                        "source": 100,
                        "confident": 104,
                        "hesitant": 110,
                        "absolute_gap": 6,
                        "allowed_gap": float("nan"),
                        "direction_correct": True,
                    }
                }
            }
        )
        with self.assertRaises(builder.RepairPromptError) as caught:
            self.build("nonfinite-final-gap")
        self.assertIn(
            "final_length_only_allowed_gap_mismatch:source-1",
            caught.exception.errors,
        )

    def test_final_length_only_requires_only_length_failure_code(self):
        self.write_spec(
            ["source-1"],
            repair_stage="final_length_only",
            failure_codes=["assigned_cue_family_not_realized"],
        )
        with self.assertRaises(builder.RepairPromptError) as caught:
            self.build("bad-final-code")
        self.assertIn(
            "final_length_only_requires_only_frozen_length_policy_violation",
            caught.exception.errors,
        )

    def test_missing_private_evidence_fails_closed(self):
        self.validator_path.unlink()
        with self.assertRaises(builder.RepairPromptError) as caught:
            self.build("missing-validator")
        self.assertTrue(
            any("input_not_found" in error for error in caught.exception.errors)
        )

        self.write_validator(["source-2", "source-1"])
        self.ledger_path.write_text("{}", encoding="utf-8")
        with self.assertRaises(builder.RepairPromptError) as caught:
            self.build("malformed-ledger")
        self.assertTrue(
            any(
                error.startswith("missing_repair_budget_ledger_field")
                for error in caught.exception.errors
            )
        )

    def test_cli_requires_validator_and_budget_inputs(self):
        with redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                builder.parse_args(
                    [
                        "--sources", str(self.source_path),
                        "--candidates", str(self.candidate_path),
                        "--repair-spec", str(self.spec_path),
                        "--prompt-output", str(self.private_root / "out.txt"),
                        "--manifest-output", str(self.private_root / "out.json"),
                    ]
                )

        parsed = builder.parse_args(
            [
                "--sources", str(self.source_path),
                "--candidates", str(self.candidate_path),
                "--repair-spec", str(self.spec_path),
                "--validator-report", str(self.validator_path),
                "--repair-budget-ledger", str(self.ledger_path),
                "--prompt-output", str(self.private_root / "out.txt"),
                "--manifest-output", str(self.private_root / "out.json"),
            ]
        )
        self.assertEqual(parsed.validator_report, self.validator_path)
        self.assertEqual(parsed.repair_budget_ledger, self.ledger_path)

    def test_outputs_must_stay_below_private_root(self):
        outside_prompt = self.root / "public_prompt.txt"
        inside_manifest = self.private_root / "manifest.json"

        with self.assertRaises(builder.RepairPromptError) as caught:
            builder.build_repair_prompt_artifacts(
                self.source_path,
                [self.candidate_path],
                self.spec_path,
                self.validator_path,
                self.ledger_path,
                outside_prompt,
                inside_manifest,
                private_root=self.private_root,
            )

        self.assertTrue(
            any("output_outside_private_data" in error for error in caught.exception.errors)
        )
        self.assertFalse(outside_prompt.exists())
        self.assertFalse(inside_manifest.exists())

    def test_overwrite_transaction_rolls_back_both_outputs_on_commit_failure(self):
        prompt_path, manifest_path, _ = self.build()
        original_prompt = prompt_path.read_bytes()
        original_manifest = manifest_path.read_bytes()
        self.write_spec(
            ["source-1"],
            repair_id="changed-repair",
            banned_surface_forms=[],
        )
        real_replace = builder.os.replace
        call_count = 0

        def fail_fourth_replace(source, target):
            nonlocal call_count
            call_count += 1
            if call_count == 4:
                raise OSError("simulated second-output commit failure")
            return real_replace(source, target)

        with mock.patch.object(builder.os, "replace", side_effect=fail_fourth_replace):
            with self.assertRaises(OSError):
                builder.build_repair_prompt_artifacts(
                    self.source_path,
                    [self.candidate_path],
                    self.spec_path,
                    self.validator_path,
                    self.ledger_path,
                    prompt_path,
                    manifest_path,
                    private_root=self.private_root,
                    overwrite=True,
                )

        self.assertEqual(prompt_path.read_bytes(), original_prompt)
        self.assertEqual(manifest_path.read_bytes(), original_manifest)

    def test_post_commit_backup_cleanup_failure_does_not_report_false_failure(self):
        prompt_path, manifest_path, _ = self.build()
        original_prompt = prompt_path.read_bytes()
        changed_sources = [dict(row) for row in self.sources]
        changed_sources[0]["prompt"] = "A changed writer-visible prompt?"
        write_jsonl(self.source_path, changed_sources)
        real_unlink = builder.Path.unlink
        rollback_unlinks = 0

        def fail_first_post_commit_backup_cleanup(path, *args, **kwargs):
            nonlocal rollback_unlinks
            if str(path).endswith(".rollback"):
                rollback_unlinks += 1
                if rollback_unlinks == 3:
                    raise OSError("simulated non-fatal cleanup failure")
            return real_unlink(path, *args, **kwargs)

        with mock.patch.object(
            builder.Path,
            "unlink",
            new=fail_first_post_commit_backup_cleanup,
        ):
            manifest = builder.build_repair_prompt_artifacts(
                self.source_path,
                [self.candidate_path],
                self.spec_path,
                self.validator_path,
                self.ledger_path,
                prompt_path,
                manifest_path,
                private_root=self.private_root,
                overwrite=True,
            )

        self.assertNotEqual(prompt_path.read_bytes(), original_prompt)
        self.assertEqual(
            manifest["output"]["sha256"],
            hashlib.sha256(prompt_path.read_bytes()).hexdigest(),
        )


if __name__ == "__main__":
    unittest.main()
