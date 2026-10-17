import importlib.util
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "build_public_canary_status.py"
)
SPEC = importlib.util.spec_from_file_location("build_public_canary_status", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def validation(passed: bool = True) -> dict:
    return {
        "validator": "factual_direct_pair_rewrite_validator",
        "expected_source_count": 12,
        "source_rows": 12,
        "pair_rows": 12,
        "audit_rows": 12,
        "mechanical_gate_pass": passed,
        "manual_review_required": True,
        "global_failure_flags": [] if passed else ["length_direction_not_globally_balanced"],
        "status_counts": {"manual_review": 12} if passed else {"fail": 1, "manual_review": 11},
        "failure_flag_counts": {} if passed else {"length_direction_incorrect": 1},
        "warning_flag_counts": {},
        "dataset_counts": {"asqa": 4, "billsum": 4, "qasper": 4},
        "draft_order_counts": {"confident_first": 6, "hesitant_first": 6},
        "length_direction_counts": {"confident_longer": 6, "hesitant_longer": 6},
        "artifact_binding": binding(),
    }


def shortcut(passed: bool = True) -> dict:
    return {
        "audit": "factual_direct_pair_shortcut_audit",
        "scope": {
            "expected_pairs": 12,
            "source_rows": 12,
            "writer_rows": 12,
            "audit_rows": 12,
        },
        "status_counts": {"pass": 12} if passed else {"pass": 11, "reject": 1},
        "flag_counts": {} if passed else {"verbatim_source": 1},
        "warning_counts": {},
        "batch_flags": [],
        "semantic_qualifier_review_required_count": 5,
        "decision": {"automatic_shortcut_gate_pass": passed},
        "artifact_binding": binding(),
    }


def source_ids() -> list[str]:
    return [f"secret-source-{index}" for index in range(12)]


def binding() -> dict:
    return {
        "schema": "factual-rewrite-artifact-binding-v1",
        "source_count": 12,
        "pair_count": 12,
        "source_ids_sha256": MODULE.source_ids_sha256(source_ids()),
        "source_set_sha256": "1" * 64,
        "pair_set_sha256": "2" * 64,
    }


def pre_review(decision: str = "pass") -> dict:
    return {
        "schema": "factual-rewrite-model-assisted-pre-review-v1",
        "review_type": "model_assisted",
        "blinded": True,
        "artifact_binding": binding(),
        "records": [
            {
                "source_id": source_ids()[index],
                "decision": decision,
                "notes": f"Secret reviewer note {index}",
                "source_text": f"Third-party source text {index}",
            }
            for index in range(12)
        ],
    }


def blind_manifest() -> dict:
    return {
        "schema": "factual-rewrite-blind-review-v2",
        "pair_count": 12,
        "packet_sha256": "3" * 64,
        "blinded": True,
        "answer_key_embedded_in_html": False,
        "human_review_certified": False,
        "artifact_binding": binding(),
    }


def completed_blind_results() -> dict:
    fields = {
        "source_fidelity": "both_preserve",
        "pair_content_equivalence": "equivalent",
        "qualifier_preservation": "both_preserve",
        "speaker_level_scope": "both_speaker_level",
        "certainty_a": "2",
        "certainty_b": "5",
        "stronger_certainty": "b",
        "naturalness_a": "natural",
        "naturalness_b": "natural",
        "formatting_mismatch": "none",
        "shortcut_concern": "none",
    }
    return {
        "schema": "factual-rewrite-blind-review-results-v2",
        "artifact_role": "final_12_pair_human_review_form",
        "pair_count": 12,
        "final_canary_certification": False,
        "human_review_certified": False,
        "packet_sha256": "3" * 64,
        "blinded": True,
        "reviews": [
            {
                "review_id": f"R{index + 1:03d}",
                **fields,
                "notes": f"Secret blind note {index}",
                "version_a": "Private rewrite text",
            }
            for index in range(12)
        ],
    }


class PublicCanaryStatusTests(unittest.TestCase):
    def test_ready_report_is_text_free_and_not_certified(self) -> None:
        report = MODULE.build_status_report(
            validation(), shortcut(), pre_review(), blind_manifest()
        )
        self.assertEqual(report["status"], "ready_for_blind_review")
        encoded = json.dumps(report)
        for secret in (
            "secret-source",
            "Secret reviewer note",
            "Third-party source text",
            "R001",
            "Private rewrite text",
            "length_direction_incorrect",
        ):
            self.assertNotIn(secret, encoded)
        self.assertFalse(report["decision"]["human_review_certified"])
        self.assertFalse(report["decision"]["activation_scoring_authorized"])
        self.assertFalse(report["decision"]["scale_to_120_authorized"])

    def test_missing_inputs_make_an_explicit_progress_report(self) -> None:
        report = MODULE.build_status_report()
        self.assertEqual(report["status"], "in_progress")
        self.assertEqual(
            report["stages"]["blind_review"]["status"], "not_prepared"
        )

    def test_pre_review_failure_does_not_imply_unrun_automatic_gates_passed(self) -> None:
        report = MODULE.build_status_report(pre_review=pre_review("repair"))
        self.assertEqual(report["status"], "in_progress")
        rendered = MODULE.render_markdown(report)
        self.assertNotIn("automatic gates passed", rendered)

    def test_automatic_failure_blocks_progress(self) -> None:
        report = MODULE.build_status_report(
            validation(False), shortcut(), pre_review(), blind_manifest()
        )
        self.assertEqual(report["status"], "blocked_by_automatic_gate")

    def test_nonpassing_pre_review_blocks_progress(self) -> None:
        report = MODULE.build_status_report(
            validation(), shortcut(), pre_review("repair"), blind_manifest()
        )
        self.assertEqual(
            report["status"], "blocked_by_model_assisted_pre_review"
        )
        self.assertEqual(
            report["stages"]["model_assisted_pre_review"]["decision_counts"],
            {"repair": 12},
        )

    def test_completed_blind_form_awaits_import_and_is_not_certified(self) -> None:
        report = MODULE.build_status_report(
            validation(),
            shortcut(),
            pre_review(),
            blind_manifest(),
            completed_blind_results(),
        )
        self.assertEqual(
            report["status"], "awaiting_review_import_and_adjudication"
        )
        self.assertEqual(
            report["stages"]["blind_review"]["complete_review_rows"], 12
        )
        self.assertFalse(
            report["stages"]["blind_review"]["human_review_certified"]
        )
        encoded = json.dumps(report)
        self.assertNotIn("R001", encoded)
        self.assertNotIn("Secret blind note", encoded)

    def test_pre_review_must_be_labelled_model_assisted(self) -> None:
        with self.assertRaisesRegex(ValueError, "model_assisted"):
            MODULE.summarize_pre_review(
                {
                    "schema": "factual-rewrite-model-assisted-pre-review-v1",
                    "review_type": "human",
                    "blinded": True,
                    "artifact_binding": binding(),
                    "records": [],
                }
            )

    def test_blind_results_must_match_packet(self) -> None:
        results = completed_blind_results()
        results["packet_sha256"] = "wrong"
        with self.assertRaisesRegex(ValueError, "do not match"):
            MODULE.summarize_blind_review(blind_manifest(), results)

    def test_stage_binding_mismatch_is_rejected(self) -> None:
        mismatched = shortcut()
        mismatched["artifact_binding"] = {
            **binding(),
            "pair_set_sha256": "9" * 64,
        }
        with self.assertRaisesRegex(ValueError, "same 12-pair set"):
            MODULE.build_status_report(
                validation(), mismatched, pre_review(), blind_manifest()
            )

    def test_pre_review_requires_complete_unique_ids_and_blinding(self) -> None:
        missing_id = pre_review()
        del missing_id["records"][0]["source_id"]
        with self.assertRaisesRegex(ValueError, "requires a nonempty source_id"):
            MODULE.summarize_pre_review(missing_id)
        unblinded = pre_review()
        unblinded["blinded"] = False
        with self.assertRaisesRegex(ValueError, "label-blind"):
            MODULE.summarize_pre_review(unblinded)

    def test_blind_review_rejects_invalid_choice_and_unknown_id(self) -> None:
        invalid = completed_blind_results()
        invalid["reviews"][0]["certainty_a"] = "pass"
        with self.assertRaisesRegex(ValueError, "invalid choice"):
            MODULE.summarize_blind_review(blind_manifest(), invalid)
        unknown = completed_blind_results()
        unknown["reviews"][0]["review_id"] = "private-review-0"
        with self.assertRaisesRegex(ValueError, "unknown review_id"):
            MODULE.summarize_blind_review(blind_manifest(), unknown)

    def test_inconsistent_passing_boolean_is_rejected(self) -> None:
        inconsistent = validation(True)
        inconsistent["failure_flag_counts"] = {"hidden_failure": 1}
        with self.assertRaisesRegex(ValueError, "failure evidence"):
            MODULE.summarize_validation(inconsistent)
        inconsistent_shortcut = shortcut(True)
        inconsistent_shortcut["status_counts"] = {"pass": 11, "reject": 1}
        with self.assertRaisesRegex(ValueError, "rejection evidence"):
            MODULE.summarize_shortcut(inconsistent_shortcut)

    def test_private_reason_codes_are_reduced_to_counts(self) -> None:
        failed = validation(False)
        failed["failure_flag_counts"] = {"source_id:secret-123": 1}
        failed["global_failure_flags"] = ["source_id:secret-123"]
        summary = MODULE.summarize_validation(failed)
        encoded = json.dumps(summary)
        self.assertNotIn("secret-123", encoded)
        self.assertEqual(
            summary["failure_flags"],
            {"occurrence_count": 1, "distinct_code_count": 1},
        )

    def test_markdown_states_scope_and_decision_boundary(self) -> None:
        report = MODULE.build_status_report(
            validation(), shortcut(), pre_review(), blind_manifest()
        )
        rendered = MODULE.render_markdown(report)
        self.assertIn("**Current conclusion:**", rendered)
        self.assertIn("Scaling to 120 pairs is not authorized", rendered)
        self.assertIn("confidence representation", rendered)

    def test_cli_writes_only_sanitized_aggregates(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            inputs = {
                "validation.json": validation(),
                "shortcut.json": shortcut(),
                "pre.json": pre_review(),
                "manifest.json": blind_manifest(),
            }
            for filename, payload in inputs.items():
                (root / filename).write_text(json.dumps(payload), encoding="utf-8")
            json_output = root / "status.json"
            markdown_output = root / "status.md"
            with redirect_stdout(io.StringIO()):
                return_code = MODULE.main([
                    "--validation-summary", str(root / "validation.json"),
                    "--shortcut-summary", str(root / "shortcut.json"),
                    "--pre-review", str(root / "pre.json"),
                    "--blind-review-manifest", str(root / "manifest.json"),
                    "--json-output", str(json_output),
                    "--markdown-output", str(markdown_output),
                ])
            self.assertEqual(return_code, 0)
            encoded = json_output.read_text(encoding="utf-8")
            self.assertNotIn("secret-source", encoded)
            self.assertNotIn("Secret reviewer note", encoded)
            self.assertIn("ready_for_blind_review", encoded)
            self.assertIn("Current conclusion", markdown_output.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
