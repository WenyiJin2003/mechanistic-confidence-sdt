from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

import numpy as np


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("baseline_runner", HERE / "run_baseline_comparison.py")
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def row(index: int, confident: str, hesitant: str) -> dict:
    return {
        "id": f"p{index}", "source_id": f"s{index}", "group_id": f"g{index}",
        "atomic_group_id": f"a{index}", "question": f"Question {index}?",
        "confident_response": confident, "hesitant_response": hesitant,
        "task": "factual_explanation", "length_bin": "short",
        "target_longer_role": "confident", "source_collection": "synthetic",
        "strict_evidence": {
            "confident_qwen_tokens": len(confident.split()),
            "hesitant_qwen_tokens": len(hesitant.split()),
        },
    }


class BaselineTests(unittest.TestCase):
    def test_registry_is_exactly_six_frozen_methods(self) -> None:
        self.assertEqual(
            MODULE.TEXT_METHOD_ORDER,
            (
                "char_wb3_5__answer_only", "char_wb3_5__system_question_answer",
                "char3_5__answer_only", "char3_5__system_question_answer",
                "word1_2__answer_only", "word1_2__system_question_answer",
            ),
        )
        self.assertEqual(len(MODULE.TEXT_RECIPES), 6)
        self.assertEqual(MODULE.CLASSIFIER_PARAMETERS["C"], 0.01)
        self.assertEqual(MODULE.CLASSIFIER_PARAMETERS["solver"], "liblinear")

    def test_candidate_order_is_confident_block_then_hesitant_block(self) -> None:
        rows = [row(1, "certain alpha", "maybe alpha"), row(2, "certain beta", "maybe beta")]
        self.assertEqual(
            MODULE.candidate_documents(rows, "answer_only"),
            ["certain alpha", "certain beta", "maybe alpha", "maybe beta"],
        )

    def test_system_question_answer_formatter_is_exact(self) -> None:
        observed = MODULE.format_candidate("Q?", "A.", "system_question_answer")
        self.assertEqual(observed, "SYSTEM\nYou are a helpful assistant.\nQUESTION\nQ?\nANSWER\nA.")

    def test_fit_is_prefix_only_and_scores_pair_order(self) -> None:
        train = [
            row(i, f"definitely fact token{i}", f"perhaps fact token{i}")
            for i in range(8)
        ]
        recipe = MODULE._recipe("word1_2", "answer_only")
        vectorizer, classifier, audit = MODULE.fit_text_control(train[:5], recipe)
        self.assertEqual(audit["training_pairs"], 5)
        self.assertEqual(audit["candidate_document_order"], "all_confident_then_all_hesitant")
        scores = MODULE.score_text_control(vectorizer, classifier, train[5:], recipe.access)
        self.assertEqual(scores.shape, (3, 2))
        self.assertTrue(np.isfinite(scores).all())

    def test_length_rules_are_exact_and_role_ordered(self) -> None:
        rows = [row(1, "one two three", "one two")]
        rows[0]["strict_evidence"] = {
            "confident_qwen_tokens": 7, "hesitant_qwen_tokens": 5
        }
        scores = MODULE.score_length_controls(rows)
        np.testing.assert_array_equal(
            scores["negative_response_token_length"], [[-7.0, -5.0]]
        )
        np.testing.assert_array_equal(
            scores["negative_response_word_length"], [[-3.0, -2.0]]
        )
        np.testing.assert_array_equal(
            scores["negative_response_character_length"], [[-13.0, -7.0]]
        )

    def test_missing_frozen_token_count_fails_closed(self) -> None:
        rows = [row(1, "one", "two")]
        rows[0]["strict_evidence"] = {"confident_qwen_tokens": 1}
        with self.assertRaises(MODULE.BaselineContractError):
            MODULE.score_length_controls(rows)

    def test_fit_restores_global_numpy_rng(self) -> None:
        train = [row(i, f"certain fact {i}", f"uncertain fact {i}") for i in range(8)]
        recipe = MODULE._recipe("char3_5", "answer_only")
        np.random.seed(77)
        before = np.random.get_state()
        MODULE.fit_text_control(train, recipe)
        after = np.random.get_state()
        self.assertEqual(before[0], after[0])
        np.testing.assert_array_equal(before[1], after[1])
        self.assertEqual(before[2:], after[2:])

    def test_artifact_record_rejects_sha_tamper(self) -> None:
        with tempfile.TemporaryDirectory(dir=MODULE.PROJECT_ROOT) as directory:
            path = Path(directory) / "artifact.bin"
            path.write_bytes(b"exact bytes")
            relative = str(path.resolve().relative_to(MODULE.PROJECT_ROOT.resolve()))
            bad = {"path": relative, "sha256": "0" * 64, "bytes": len(b"exact bytes")}
            with self.assertRaises(MODULE.BaselineContractError):
                MODULE.authenticate_file_record(
                    path, bad, label="synthetic_fit", require_bytes=True
                )

    def test_artifact_record_rejects_path_tamper(self) -> None:
        with tempfile.TemporaryDirectory(dir=MODULE.PROJECT_ROOT) as directory:
            path = Path(directory) / "activation.npz"
            path.write_bytes(b"exact activation")
            good_sha = MODULE.file_sha256(path)
            bad = {"path": "different/activation.npz", "sha256": good_sha}
            with self.assertRaises(MODULE.BaselineContractError):
                MODULE.authenticate_file_record(
                    path, bad, label="synthetic_activation", require_bytes=False
                )


if __name__ == "__main__":
    unittest.main()
