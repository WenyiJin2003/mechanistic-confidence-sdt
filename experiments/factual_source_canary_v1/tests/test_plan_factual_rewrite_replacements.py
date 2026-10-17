import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "src" / "plan_factual_rewrite_replacements.py"
SPEC = importlib.util.spec_from_file_location(
    "plan_factual_rewrite_replacements", MODULE_PATH
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def jsonl_bytes(rows):
    return "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows).encode()


def source_row(source_id, role, words, sentences, qualifiers):
    return {
        "source_id": source_id,
        "source_hash": MODULE.sha256_text(f"source:{source_id}"),
        "dataset": "demo",
        "selection_role": role,
        "word_count": words,
        "sentence_count": sentences,
        "protected_qualifiers": qualifiers,
        "original_response": (
            "Synthetic source response containing private one, private two, "
            "private three, and private four. "
            + " ".join(qualifiers)
        ),
        "model_review_decision": "accept",
        "heuristic_pass": True,
        "blocking_flags": [],
    }


def frozen_slot(source, target, generation_order):
    profiles = {1: "short_simple", 2: "mid_plain"}
    return {
        **source,
        "profile": profiles[generation_order],
        "selection_features": [0.1, 0.1, 0.1],
        "selection_target": target,
        "selection_distance": 0.0,
        "cue_family": "embedded_stance_predicate",
        "length_direction": "confident_longer",
        "draft_order": "confident_first",
        "batch_id": "batch_01",
        "batch_position": generation_order,
        "generation_order": generation_order,
    }


class PlanFactualRewriteReplacementsTests(unittest.TestCase):
    def make_fixture(self, directory: Path, *, audit_complete=True, mapping=None):
        rows = [
            source_row("demo:s1", "core", 1, 1, []),
            source_row("demo:s2", "core", 10, 5, ["core q1", "core q2", "core q3"]),
            source_row("demo:b1", "backup", 2, 1, []),
            source_row("demo:b2", "backup", 8, 4, ["b2 q1", "b2 q2", "b2 q3"]),
            source_row("demo:b3", "backup", 4, 2, ["b3 q1"]),
        ]
        slots = [
            frozen_slot(rows[0], [0.2, 0.2, 0.2], 1),
            frozen_slot(rows[1], [0.8, 0.8, 0.8], 2),
        ]
        validator = {
            "global_failure_flags": [],
            "rows": [
                {"source_id": "demo:s1", "mechanical_gate_pass": False},
                {"source_id": "demo:s2", "mechanical_gate_pass": False},
            ],
        }
        source_path = directory / "sources.jsonl"
        frozen_path = directory / "frozen.jsonl"
        validator_path = directory / "validator.json"
        source_path.write_bytes(jsonl_bytes(rows))
        frozen_path.write_bytes(jsonl_bytes(slots))
        validator_path.write_text(json.dumps(validator, sort_keys=True), encoding="utf-8")

        backup_audits = [
            {
                "source_id": row["source_id"],
                "source_hash": row["source_hash"],
                "audit_complete": audit_complete,
                "review_type": "model_assisted_independent",
                "human_certified": False,
                "decision": "accept",
                "reason_codes": ["independent_source_review_accept"],
                "source_accepted": True,
            }
            for row in rows
            if row["selection_role"] == "backup"
        ]
        audit_artifact = {
            "schema_version": MODULE.AUDIT_ARTIFACT_SCHEMA,
            "review_type": "model_assisted_independent",
            "human_certified": False,
            "review_run_id": "synthetic-independent-review-v1",
            "decisions": [
                {
                    "source_id": row["source_id"],
                    "source_hash": row["source_hash"],
                    "decision": row["decision"],
                    "reason_codes": list(row["reason_codes"]),
                }
                for row in backup_audits
            ],
        }
        audit_artifact_path = directory / "independent_audit.json"
        audit_artifact_path.write_text(
            json.dumps(audit_artifact, sort_keys=True), encoding="utf-8"
        )
        ledger = {
            "schema_version": MODULE.LEDGER_SCHEMA,
            "audit_complete": audit_complete,
            "source_pool_sha256": MODULE.sha256_bytes(source_path.read_bytes()),
            "feature_universe_sha256": MODULE.source_universe_hash(rows),
            "audit_provenance": {
                "artifact_filename": audit_artifact_path.name,
                "artifact_sha256": MODULE.sha256_bytes(
                    audit_artifact_path.read_bytes()
                ),
                "review_run_id": audit_artifact["review_run_id"],
                "review_type": audit_artifact["review_type"],
                "human_certified": audit_artifact["human_certified"],
            },
            "backup_audits": backup_audits,
            "qualifier_corrections": [
                {
                    "source_id": row["source_id"],
                    "source_hash": row["source_hash"],
                    "audit_complete": True,
                    "expected_old_descriptor_sha256": MODULE.descriptor_hashes(
                        row["protected_qualifiers"]
                    ),
                    "corrected_protected_qualifiers": list(
                        row["protected_qualifiers"]
                    ),
                    "corrected_descriptor_sha256": MODULE.descriptor_hashes(
                        row["protected_qualifiers"]
                    ),
                }
                for row in rows
                if row["selection_role"] == "backup"
            ],
        }
        ledger_path = directory / "ledger.json"
        ledger_path.write_text(json.dumps(ledger, sort_keys=True), encoding="utf-8")

        expected_mapping = mapping or {
            "demo:s1": "demo:b1",
            "demo:s2": "demo:b2",
        }
        config = {
            "schema_version": MODULE.CONFIG_SCHEMA,
            "plan_revision": "v5",
            "seed": 7,
            "source_pool": {
                "expected_sha256": MODULE.sha256_bytes(source_path.read_bytes()),
                "datasets": ["demo"],
                "core_role": "core",
                "candidate_role": "backup",
                "acceptance_requirements": {
                    "model_review_decision": "accept",
                    "heuristic_pass": True,
                    "blocking_flags": [],
                },
                "expected_core_per_dataset": 2,
                "expected_accepted_unused_backups_by_dataset": {"demo": 3},
                "expected_hold_source_ids": [],
                "used_backup_source_ids": [],
            },
            "failed_slots": {
                "expected_count": 2,
                "expected_source_ids": ["demo:s1", "demo:s2"],
                "frozen_slots_expected_sha256": MODULE.sha256_bytes(
                    frozen_path.read_bytes()
                ),
                "post_repair_validator_expected_sha256": MODULE.sha256_bytes(
                    validator_path.read_bytes()
                ),
            },
            "features": {
                "names": [
                    "word_count_candidate_included_midrank",
                    "sentence_count_candidate_included_midrank",
                    "corrected_qualifier_count_candidate_included_midrank",
                ],
                "reference_pool": MODULE.REFERENCE_POOL_TEMPLATE.format(core_count=2),
                "midrank_formula": "(count_less + (count_equal + 1) / 2) / n",
                "bounded_interval": "(0, 1]",
                "distance": "squared_euclidean",
                "distance_round_digits": 8,
            },
            "assignment": {
                "method": "global_one_to_one_minimum_total_distance_per_dataset",
                "tie_breaker": MODULE.TIE_BREAK_DESCRIPTION,
                "key_namespace": "test",
                "same_dataset_required": True,
                "preserved_slot_fields": [
                    "profile",
                    "selection_features",
                    "selection_target",
                    "selection_distance",
                    "cue_family",
                    "length_direction",
                    "draft_order",
                    "batch_id",
                    "batch_position",
                    "generation_order",
                ],
            },
            "metadata_correction_ledger": {
                "required": True,
                "private_filename": ledger_path.name,
                "private_audit_artifact_filename": audit_artifact_path.name,
                "required_schema_version": MODULE.LEDGER_SCHEMA,
                "expected_sha256": MODULE.sha256_bytes(ledger_path.read_bytes()),
                "audit_complete_required": True,
            },
            "expected_mapping": {
                "audit_complete": True,
                "mapping_sha256": MODULE.mapping_sha256(expected_mapping),
                "failed_to_replacement": expected_mapping,
            },
            "authorization": {
                "generation_on_verified_plan": False,
                "activation_extraction": False,
                "probe_fitting": False,
                "sdt_training": False,
            },
        }
        config_path = directory / "config.json"
        config_path.write_text(json.dumps(config, sort_keys=True), encoding="utf-8")
        return {
            "rows": rows,
            "slots": slots,
            "ledger": ledger,
            "config": config,
            "config_path": config_path,
            "source_path": source_path,
            "frozen_path": frozen_path,
            "validator_path": validator_path,
            "ledger_path": ledger_path,
            "audit_artifact": audit_artifact,
            "audit_artifact_path": audit_artifact_path,
        }

    def build(self, fixture):
        return MODULE.build_plan(
            config_path=fixture["config_path"],
            source_pool_path=fixture["source_path"],
            frozen_slots_path=fixture["frozen_path"],
            validator_path=fixture["validator_path"],
            ledger_path=fixture["ledger_path"],
            audit_artifact_path=fixture["audit_artifact_path"],
        )

    def rebind_ledger(self, fixture):
        fixture["ledger_path"].write_text(
            json.dumps(fixture["ledger"], sort_keys=True), encoding="utf-8"
        )
        fixture["config"]["metadata_correction_ledger"]["expected_sha256"] = (
            MODULE.sha256_bytes(fixture["ledger_path"].read_bytes())
        )
        fixture["config_path"].write_text(
            json.dumps(fixture["config"], sort_keys=True), encoding="utf-8"
        )

    def rebind_audit_artifact(self, fixture):
        fixture["audit_artifact_path"].write_text(
            json.dumps(fixture["audit_artifact"], sort_keys=True), encoding="utf-8"
        )
        provenance = fixture["ledger"]["audit_provenance"]
        provenance["artifact_sha256"] = MODULE.sha256_bytes(
            fixture["audit_artifact_path"].read_bytes()
        )
        self.rebind_ledger(fixture)

    def test_verified_plan_is_global_same_dataset_and_preserves_every_slot_field(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(Path(temporary))
            plan = self.build(fixture)
        self.assertEqual(plan["status"], "verified_plan")
        self.assertFalse(plan["authorization"]["replacement_generation"])
        self.assertEqual(plan["counts"]["planned_replacements"], 2)
        actual = {
            row["failed_source_id"]: row["replacement_source_id"]
            for row in plan["assignments"]
        }
        self.assertEqual(
            actual,
            {"demo:s1": "demo:b1", "demo:s2": "demo:b2"},
        )
        by_id = {row["source_id"]: row for row in fixture["slots"]}
        for assignment in plan["assignments"]:
            source = by_id[assignment["failed_source_id"]]
            self.assertEqual(
                assignment["preserved_slot"],
                {
                    field: source[field]
                    for field in fixture["config"]["assignment"][
                        "preserved_slot_fields"
                    ]
                },
            )

    def test_global_solver_can_outperform_slotwise_greedy_assignment(self):
        slots = [
            {"source_id": "slot:a", "selection_target": [6.0, 0.0, 0.0]},
            {"source_id": "slot:b", "selection_target": [10.0, 0.0, 0.0]},
        ]
        candidates = [{"source_id": "candidate:x"}, {"source_id": "candidate:y"}]
        features = {
            "candidate:x": [7.0, 0.0, 0.0],
            "candidate:y": [0.0, 0.0, 0.0],
        }
        mapping, _, total, _ = MODULE.solve_dataset_assignment(
            dataset="demo",
            slots=slots,
            candidates=candidates,
            features_by_id=features,
            seed=1,
            namespace="test",
            round_digits=8,
        )
        self.assertEqual(mapping, {"slot:a": "candidate:y", "slot:b": "candidate:x"})
        self.assertEqual(total, 45.0)

    def test_tied_assignments_use_a_deterministic_full_mapping_hash(self):
        slots = [
            {"source_id": "slot:a", "selection_target": [0.5, 0.5, 0.5]},
            {"source_id": "slot:b", "selection_target": [0.5, 0.5, 0.5]},
        ]
        candidates = [{"source_id": "candidate:x"}, {"source_id": "candidate:y"}]
        features = {
            "candidate:x": [0.5, 0.5, 0.5],
            "candidate:y": [0.5, 0.5, 0.5],
        }
        first = MODULE.solve_dataset_assignment(
            dataset="demo",
            slots=slots,
            candidates=candidates,
            features_by_id=features,
            seed=1,
            namespace="test",
            round_digits=8,
        )
        second = MODULE.solve_dataset_assignment(
            dataset="demo",
            slots=reversed(slots),
            candidates=reversed(candidates),
            features_by_id=features,
            seed=1,
            namespace="test",
            round_digits=8,
        )
        self.assertEqual(first[0], second[0])
        self.assertEqual(first[3], second[3])

    def test_candidate_included_midrank_is_bounded(self):
        self.assertEqual(MODULE.midrank_percentile(4, [1, 2, 4]), 1.0)
        with self.assertRaisesRegex(ValueError, "candidate must be included"):
            MODULE.midrank_percentile(4, [1, 2, 3])

    def test_private_metadata_correction_is_applied_before_features(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(Path(temporary))
            rows = fixture["rows"]
            b1 = next(row for row in rows if row["source_id"] == "demo:b1")
            correction = {
                "source_id": b1["source_id"],
                "source_hash": b1["source_hash"],
                "audit_complete": True,
                "expected_old_descriptor_sha256": [],
                "corrected_protected_qualifiers": [
                    "private one",
                    "private two",
                    "private three",
                    "private four",
                ],
                "corrected_descriptor_sha256": [
                    MODULE.sha256_text(value)
                    for value in (
                        "private one",
                        "private two",
                        "private three",
                        "private four",
                    )
                ],
            }
            ledger = copy.deepcopy(fixture["ledger"])
            ledger["qualifier_corrections"] = [
                correction
                if row["source_id"] == "demo:b1"
                else row
                for row in ledger["qualifier_corrections"]
            ]
            source_by_id = {row["source_id"]: row for row in rows}
            backups = [row for row in rows if row["selection_role"] == "backup"]
            counts, _ = MODULE.validate_and_apply_ledger(
                ledger=ledger,
                source_rows=rows,
                source_by_id=source_by_id,
                backup_rows=backups,
                source_pool_sha256=ledger["source_pool_sha256"],
                config=fixture["config"],
                audit_artifact=fixture["audit_artifact"],
                audit_artifact_sha256=MODULE.sha256_bytes(
                    fixture["audit_artifact_path"].read_bytes()
                ),
                audit_artifact_filename=fixture["audit_artifact_path"].name,
            )
            core_plus_candidate = [
                row for row in rows if row["selection_role"] == "core"
            ] + [b1]
            features = MODULE.candidate_features(b1, core_plus_candidate, counts)
        self.assertEqual(counts["demo:b1"], 4)
        self.assertEqual(features[2], 1.0)

    def test_incomplete_audit_emits_pending_artifact_and_never_authorizes(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(Path(temporary), audit_complete=False)
            plan = self.build(fixture)
        self.assertEqual(plan["status"], "audit_pending")
        self.assertIn("metadata_audit_incomplete", plan["reason_codes"])
        self.assertEqual(plan["counts"]["planned_replacements"], 0)
        self.assertFalse(plan["authorization"]["replacement_generation"])

    def test_missing_unfrozen_ledger_emits_explicit_pending_artifact(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            fixture = self.make_fixture(directory)
            config = fixture["config"]
            config["metadata_correction_ledger"]["expected_sha256"] = None
            config["expected_mapping"] = {
                "audit_complete": False,
                "mapping_sha256": None,
                "failed_to_replacement": {},
            }
            fixture["config_path"].write_text(
                json.dumps(config, sort_keys=True), encoding="utf-8"
            )
            fixture["ledger_path"].unlink()
            plan = self.build(fixture)
        self.assertEqual(plan["status"], "audit_pending")
        self.assertEqual(
            set(plan["reason_codes"]),
            {
                "private_metadata_ledger_hash_not_frozen",
                "expected_mapping_not_frozen",
                "private_metadata_ledger_missing",
            },
        )
        self.assertFalse(
            plan["review_provenance_requirement"]["private_ledger_validated"]
        )

    def test_valid_ledger_can_compute_mapping_before_mapping_freeze(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(Path(temporary))
            fixture["config"]["expected_mapping"] = {
                "audit_complete": False,
                "mapping_sha256": None,
                "failed_to_replacement": {},
            }
            fixture["config_path"].write_text(
                json.dumps(fixture["config"], sort_keys=True), encoding="utf-8"
            )
            plan = self.build(fixture)
        self.assertEqual(plan["status"], "mapping_freeze_pending")
        self.assertEqual(plan["reason_codes"], ["expected_mapping_not_frozen"])
        self.assertEqual(
            {
                row["failed_source_id"]: row["replacement_source_id"]
                for row in plan["assignments"]
            },
            {"demo:s1": "demo:b1", "demo:s2": "demo:b2"},
        )
        self.assertEqual(
            plan["mapping_sha256"],
            MODULE.mapping_sha256(
                {"demo:s1": "demo:b1", "demo:s2": "demo:b2"}
            ),
        )
        self.assertTrue(plan["review_provenance"]["private_ledger_validated"])
        self.assertFalse(plan["authorization"]["replacement_generation"])

    def test_expected_mapping_drift_fails_closed(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            wrong = {"demo:s1": "demo:b2", "demo:s2": "demo:b1"}
            fixture = self.make_fixture(directory, mapping=wrong)
            with self.assertRaisesRegex(ValueError, "mapping drifted"):
                self.build(fixture)

    def test_correction_that_changes_global_optimum_triggers_mapping_drift(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            fixture = self.make_fixture(directory)
            b1 = next(
                row for row in fixture["rows"] if row["source_id"] == "demo:b1"
            )
            corrected = ["private one", "private two", "private three", "private four"]
            ledger = fixture["ledger"]
            changed = {
                    "source_id": b1["source_id"],
                    "source_hash": b1["source_hash"],
                    "audit_complete": True,
                    "expected_old_descriptor_sha256": [],
                    "corrected_protected_qualifiers": corrected,
                    "corrected_descriptor_sha256": [
                        MODULE.sha256_text(value) for value in corrected
                    ],
                }
            ledger["qualifier_corrections"] = [
                changed
                if row["source_id"] == "demo:b1"
                else row
                for row in ledger["qualifier_corrections"]
            ]
            self.rebind_ledger(fixture)
            with self.assertRaisesRegex(ValueError, "mapping drifted"):
                self.build(fixture)

    def test_independent_review_cannot_claim_human_certification(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(Path(temporary))
            fixture["ledger"]["backup_audits"][0]["human_certified"] = True
            self.rebind_ledger(fixture)
            with self.assertRaisesRegex(ValueError, "cannot claim human certification"):
                self.build(fixture)

    def test_review_type_and_decision_acceptance_consistency_are_enforced(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(Path(temporary))
            fixture["ledger"]["backup_audits"][0]["review_type"] = "human"
            self.rebind_ledger(fixture)
            with self.assertRaisesRegex(ValueError, "review_type"):
                self.build(fixture)
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(Path(temporary))
            audit = fixture["ledger"]["backup_audits"][0]
            audit["decision"] = "hold_for_source_repair"
            audit["source_accepted"] = True
            self.rebind_ledger(fixture)
            with self.assertRaisesRegex(ValueError, "disagrees with decision"):
                self.build(fixture)

    def test_every_backup_requires_exactly_one_literal_qualifier_row(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(Path(temporary))
            fixture["ledger"]["qualifier_corrections"].pop()
            self.rebind_ledger(fixture)
            with self.assertRaisesRegex(ValueError, "every frozen backup"):
                self.build(fixture)
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(Path(temporary))
            correction = fixture["ledger"]["qualifier_corrections"][0]
            correction["corrected_protected_qualifiers"] = ["PRIVATE ONE"]
            correction["corrected_descriptor_sha256"] = [
                MODULE.sha256_text("PRIVATE ONE")
            ]
            self.rebind_ledger(fixture)
            with self.assertRaisesRegex(ValueError, "case-sensitive source substring"):
                self.build(fixture)

    def test_held_backup_is_excluded_and_dataset_specific_count_is_enforced(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(Path(temporary))
            held_id = "demo:b3"
            audit = next(
                row
                for row in fixture["ledger"]["backup_audits"]
                if row["source_id"] == held_id
            )
            audit.update(
                decision="hold_for_source_repair",
                source_accepted=False,
                reason_codes=["source_repair_required"],
            )
            audit_decision = next(
                row
                for row in fixture["audit_artifact"]["decisions"]
                if row["source_id"] == held_id
            )
            audit_decision.update(
                decision="hold_for_source_repair",
                reason_codes=["source_repair_required"],
            )
            fixture["config"]["source_pool"]["expected_hold_source_ids"] = [
                held_id
            ]
            fixture["config"]["source_pool"][
                "expected_accepted_unused_backups_by_dataset"
            ] = {"demo": 2}
            self.rebind_audit_artifact(fixture)
            plan = self.build(fixture)
        self.assertEqual(plan["status"], "verified_plan")
        self.assertEqual(plan["counts"]["accepted_unused_backups"], 2)
        self.assertNotIn(
            held_id,
            {row["replacement_source_id"] for row in plan["assignments"]},
        )

    def test_independent_audit_artifact_is_immutably_bound(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(Path(temporary))
            artifact = fixture["audit_artifact"]
            artifact["review_run_id"] = "different-review-run"
            fixture["audit_artifact_path"].write_text(
                json.dumps(artifact, sort_keys=True), encoding="utf-8"
            )
            with self.assertRaisesRegex(ValueError, "artifact SHA-256 drifted"):
                self.build(fixture)

    def test_dataset_specific_candidate_count_cannot_hide_config_drift(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(Path(temporary))
            fixture["config"]["source_pool"][
                "expected_accepted_unused_backups_by_dataset"
            ] = {"demo": 2}
            fixture["config_path"].write_text(
                json.dumps(fixture["config"], sort_keys=True), encoding="utf-8"
            )
            with self.assertRaisesRegex(ValueError, "disagrees with hold/use sets"):
                self.build(fixture)

    def test_preserved_slot_fields_cannot_be_extended_with_private_text(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(Path(temporary))
            config = fixture["config"]
            config["assignment"]["preserved_slot_fields"].append(
                "protected_qualifiers"
            )
            with self.assertRaisesRegex(ValueError, "public-safe list"):
                MODULE.validate_config(config)

    def test_public_method_description_must_match_computation(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(Path(temporary))
            config = fixture["config"]
            config["features"]["reference_pool"] = "all backup candidates"
            with self.assertRaisesRegex(ValueError, "reference-pool description"):
                MODULE.validate_config(config)

    def test_frozen_slot_identity_must_match_source_pool(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(Path(temporary))
            frozen_rows = fixture["slots"]
            frozen_rows[0]["source_hash"] = MODULE.sha256_text("different source")
            fixture["frozen_path"].write_bytes(jsonl_bytes(frozen_rows))
            fixture["config"]["failed_slots"]["frozen_slots_expected_sha256"] = (
                MODULE.sha256_bytes(fixture["frozen_path"].read_bytes())
            )
            fixture["config_path"].write_text(
                json.dumps(fixture["config"], sort_keys=True), encoding="utf-8"
            )
            with self.assertRaisesRegex(ValueError, "source_hash disagrees"):
                self.build(fixture)

    def test_public_slot_values_are_schema_checked_before_publication(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(Path(temporary))
            frozen_rows = fixture["slots"]
            frozen_rows[0]["profile"] = "private source text"
            fixture["frozen_path"].write_bytes(jsonl_bytes(frozen_rows))
            fixture["config"]["failed_slots"]["frozen_slots_expected_sha256"] = (
                MODULE.sha256_bytes(fixture["frozen_path"].read_bytes())
            )
            fixture["config_path"].write_text(
                json.dumps(fixture["config"], sort_keys=True), encoding="utf-8"
            )
            with self.assertRaisesRegex(ValueError, "public-safe profile"):
                self.build(fixture)

    def test_generation_authorization_requires_a_real_boolean(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(Path(temporary))
            config = fixture["config"]
            config["authorization"]["generation_on_verified_plan"] = "false"
            with self.assertRaisesRegex(ValueError, "must remain false"):
                MODULE.validate_config(config)

    def test_source_pool_hash_drift_fails_closed(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            fixture = self.make_fixture(directory)
            fixture["source_path"].write_bytes(
                fixture["source_path"].read_bytes() + b"\n"
            )
            with self.assertRaisesRegex(ValueError, "source pool SHA-256 drifted"):
                self.build(fixture)

    def test_public_plan_does_not_leak_private_text_or_qualifiers(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(Path(temporary))
            plan = self.build(fixture)
        serialized = json.dumps(plan, sort_keys=True)
        for forbidden in (
            "core q1",
            "b2 q1",
            "original_response",
            "protected_qualifiers",
            "corrected_protected_qualifiers",
        ):
            self.assertNotIn(forbidden, serialized)
        self.assertFalse(plan["privacy"]["source_or_rewrite_text_included"])
        self.assertFalse(plan["privacy"]["qualifier_text_included"])

    def test_default_config_builds_reproducible_verified_plan(self):
        required = [
            MODULE.DEFAULT_CONFIG,
            MODULE.DEFAULT_SOURCE_POOL,
            MODULE.DEFAULT_FROZEN_SLOTS,
            MODULE.DEFAULT_VALIDATOR,
            MODULE.DEFAULT_LEDGER,
            MODULE.DEFAULT_AUDIT_ARTIFACT,
        ]
        if not all(path.exists() for path in required):
            self.skipTest("ignored private v4/v5 inputs are unavailable")
        plan = MODULE.build_plan()
        committed = json.loads(MODULE.DEFAULT_OUTPUT.read_text(encoding="utf-8"))
        self.assertEqual(committed, plan)
        self.assertEqual(plan["status"], "verified_plan")
        self.assertEqual(plan["counts"]["failed_slots"], 6)
        self.assertEqual(plan["counts"]["accepted_unused_backups"], 18)
        self.assertEqual(plan["counts"]["planned_replacements"], 6)
        self.assertEqual(plan["reason_codes"], [])
        self.assertEqual(
            plan["mapping_sha256"],
            "39f92cc98bfae1d66f55bf8dc7dbdebc8887b159b9232efed3b338edaa7e22ba",
        )
        self.assertEqual(
            {
                row["failed_source_id"]: row["replacement_source_id"]
                for row in plan["assignments"]
            },
            {
                "asqa:5767411579190718767": "asqa:5634464892410080253",
                "asqa:-9159547197550283952": "asqa:-6693893977926520813",
                "qasper-paper:1702.03274": "qasper-paper:1712.09127",
                "asqa:-4867406118701628228": "asqa:-5199777322387956321",
                "asqa:2074116551547919110": "asqa:5446132515703113969",
                "billsum:1b0226a63ea123f1": "billsum:4256aad1fff88860",
            },
        )
        self.assertFalse(plan["authorization"]["replacement_generation"])
        self.assertFalse(plan["authorization"]["activation_extraction"])
        self.assertFalse(plan["authorization"]["probe_fitting"])
        self.assertFalse(plan["authorization"]["sdt_training"])


if __name__ == "__main__":
    unittest.main()
