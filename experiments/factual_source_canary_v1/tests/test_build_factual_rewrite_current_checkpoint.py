import copy
import importlib.util
import json
import math
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "src" / "build_factual_rewrite_current_checkpoint.py"
SPEC = importlib.util.spec_from_file_location(
    "build_factual_rewrite_current_checkpoint", MODULE_PATH
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class BuildFactualRewriteCurrentCheckpointTests(unittest.TestCase):
    def require_private_inputs(self) -> None:
        paths = [
            *MODULE.DEFAULT_INITIAL_VALIDATIONS,
            *MODULE.DEFAULT_REPAIR_MANIFESTS,
            MODULE.DEFAULT_POST_REPAIR_VALIDATION,
            MODULE.DEFAULT_POST_REPAIR_PAIRS,
            MODULE.DEFAULT_POST_REPAIR_PROVENANCE,
        ]
        if not all(path.exists() for path in paths):
            self.skipTest("ignored private v4 checkpoint inputs are unavailable")

    def test_real_checkpoint_has_expected_current_progress(self) -> None:
        path = ROOT / "results" / "rewrite_canary_v4_current_checkpoint.json"
        checkpoint = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(checkpoint["artifact_role"], "current_progress_checkpoint")
        self.assertEqual(checkpoint["source_set_revision"], "v4")
        self.assertEqual(
            checkpoint["counts"],
            {
                "source_pairs": 12,
                "initial_mechanically_clean": 2,
                "initial_mechanical_failures": 10,
                "repaired_pairs": 10,
                "post_repair_mechanically_clean": 6,
                "post_repair_mechanical_failures": 6,
                "final_length_repair_eligible": 0,
            },
        )
        self.assertEqual(checkpoint["writer"]["writer_model"], "gpt-6-luna")
        self.assertEqual(checkpoint["writer"]["reasoning_effort"], "low")
        self.assertEqual(checkpoint["writer"]["initial_isolated_context_count"], 3)
        self.assertEqual(checkpoint["writer"]["repair_isolated_context_count"], 3)
        self.assertEqual(
            checkpoint["next_action"]["action"],
            "audit_and_freeze_profile_aware_same_dataset_replacement_rule",
        )
        self.assertEqual(checkpoint["next_action"]["source_count"], 6)
        self.assertTrue(checkpoint["next_action"]["same_dataset_required"])
        self.assertFalse(
            checkpoint["next_action"]["replacement_generation_authorized"]
        )
        self.assertFalse(checkpoint["authorization"]["activation_extraction"])
        self.assertFalse(checkpoint["authorization"]["probe_fitting"])

    def test_committed_checkpoint_is_reproducible_and_text_free(self) -> None:
        self.require_private_inputs()
        expected = MODULE.build_checkpoint()
        path = ROOT / "results" / "rewrite_canary_v4_current_checkpoint.json"
        actual = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(actual, expected)
        serialized = json.dumps(actual, sort_keys=True)
        for forbidden in (
            "source_id",
            "original_response",
            "confident_response",
            "hesitant_response",
            "reviewer_semantic_qualifiers",
        ):
            self.assertNotIn(forbidden, serialized)

    def test_public_summary_is_bound_to_full_validator_and_pair_artifact(self) -> None:
        self.require_private_inputs()
        checkpoint = MODULE.build_checkpoint()
        bindings = checkpoint["artifact_bindings"]
        self.assertEqual(
            bindings["post_repair_validator"]["full_artifact_sha256"],
            MODULE.sha256_file(MODULE.DEFAULT_POST_REPAIR_VALIDATION),
        )
        self.assertEqual(
            bindings["post_repair_validator"]["public_summary_sha256"],
            MODULE.sha256_file(MODULE.DEFAULT_POST_REPAIR_PUBLIC_SUMMARY),
        )
        self.assertEqual(
            bindings["post_repair_pair_artifact"]["sha256"],
            MODULE.sha256_file(MODULE.DEFAULT_POST_REPAIR_PAIRS),
        )

    def test_rejects_repair_manifest_that_does_not_cover_every_failure_once(self) -> None:
        self.require_private_inputs()
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            paths = list(MODULE.DEFAULT_REPAIR_MANIFESTS)
            bad = json.loads(paths[0].read_text(encoding="utf-8"))
            bad["target_source_ids"] = bad["target_source_ids"][:-1]
            bad["target_count"] -= 1
            bad_path = directory / "bad.json"
            bad_path.write_text(json.dumps(bad), encoding="utf-8")
            paths[0] = bad_path
            with self.assertRaisesRegex(ValueError, "each initial failure exactly once"):
                MODULE.build_checkpoint(repair_manifest_paths=paths)

    def test_final_length_repair_exception_requires_only_small_gap_failure(self) -> None:
        row = {
            "mechanical_gate_pass": False,
            "failure_flags": ["pair_token_gap_over_limit"],
            "length_direction": "confident_longer",
            "token_counts": {
                "source": 160,
                "confident": 165,
                "hesitant": 155,
                "absolute_gap": 10,
                "allowed_gap": 8.0,
                "direction_correct": True,
            },
        }
        self.assertTrue(MODULE.final_length_repair_eligible(row))
        too_far = copy.deepcopy(row)
        too_far["token_counts"].update(
            confident=165,
            hesitant=154,
            absolute_gap=11,
            allowed_gap=7.975,
        )
        self.assertFalse(MODULE.final_length_repair_eligible(too_far))
        wrong_direction = copy.deepcopy(row)
        wrong_direction["failure_flags"].append("length_direction_incorrect")
        self.assertFalse(MODULE.final_length_repair_eligible(wrong_direction))

    def test_final_length_repair_exception_fails_closed_on_stale_or_invalid_metrics(self) -> None:
        row = {
            "mechanical_gate_pass": False,
            "failure_flags": ["pair_token_gap_over_limit"],
            "length_direction": "confident_longer",
            "token_counts": {
                "source": 160,
                "confident": 165,
                "hesitant": 155,
                "absolute_gap": 10,
                "allowed_gap": 8.0,
                "direction_correct": True,
            },
        }
        cases = []
        no_positive_excess = copy.deepcopy(row)
        no_positive_excess["token_counts"].update(
            confident=162,
            hesitant=158,
            absolute_gap=4,
            allowed_gap=8.0,
        )
        cases.append(no_positive_excess)
        stale_gap = copy.deepcopy(row)
        stale_gap["token_counts"]["absolute_gap"] = 9
        cases.append(stale_gap)
        stale_allowance = copy.deepcopy(row)
        stale_allowance["token_counts"]["allowed_gap"] = 5.0
        cases.append(stale_allowance)
        false_direction = copy.deepcopy(row)
        false_direction["token_counts"]["direction_correct"] = False
        cases.append(false_direction)
        nonfinite_allowance = copy.deepcopy(row)
        nonfinite_allowance["token_counts"]["allowed_gap"] = math.nan
        cases.append(nonfinite_allowance)
        boolean_gap = copy.deepcopy(row)
        boolean_gap["token_counts"]["absolute_gap"] = True
        cases.append(boolean_gap)
        out_of_bounds_arm = copy.deepcopy(row)
        out_of_bounds_arm["token_counts"].update(
            source=200,
            confident=165,
            hesitant=155,
        )
        cases.append(out_of_bounds_arm)
        for case in cases:
            with self.subTest(case=case):
                self.assertFalse(MODULE.final_length_repair_eligible(case))

    def test_replacement_plan_is_an_explicit_generation_hold(self) -> None:
        execution = {
            "replacement_plan": {
                "action": MODULE.EXPECTED_REPLACEMENT_ACTION,
                "source_count": 6,
                "same_dataset_required": True,
                "preserve_preregistered_experimental_slot": True,
                "replacement_generation_authorized": False,
            }
        }
        self.assertFalse(
            MODULE.validate_replacement_plan(
                execution, remaining_failures=6
            )["replacement_generation_authorized"]
        )
        execution["replacement_plan"]["replacement_generation_authorized"] = True
        with self.assertRaisesRegex(ValueError, "current audit hold"):
            MODULE.validate_replacement_plan(execution, remaining_failures=6)


if __name__ == "__main__":
    unittest.main()
