from __future__ import annotations

import sys
import unittest
from pathlib import Path

import torch


EXPERIMENT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EXPERIMENT / "src"))

import data_contracts as contracts  # noqa: E402


def pair(
    identifier: str,
    source_id: str,
    question_hash: str,
    *,
    confident: str = "It is certainly P.",
    hesitant: str = "It is probably P.",
) -> dict:
    return {
        "id": identifier,
        "source_id": source_id,
        "normalized_question_sha256": question_hash,
        "question": f"Question {identifier}?",
        "confident_response": confident,
        "hesitant_response": hesitant,
        "engineering_only": True,
        "confirmatory_status": "post_exposure_not_confirmatory",
    }


class DataContractsTest(unittest.TestCase):
    def test_role_mapping_uses_exact_paired_answer(self) -> None:
        row = pair("A", "source-a", "hash-a")
        question, answer, target = contracts.select_role_text(row, "confident")
        self.assertEqual(question, row["question"])
        self.assertEqual(answer, row["confident_response"])
        self.assertEqual(target, 1.0)
        _question, answer, target = contracts.select_role_text(row, "hesitant")
        self.assertEqual(answer, row["hesitant_response"])
        self.assertEqual(target, -1.0)

    def test_completion_only_mask_contract(self) -> None:
        input_ids, labels, mask = contracts.completion_only_contract(
            [10, 11],
            [10, 11, 20, 21, 99, 500],
            assistant_end_id=99,
            max_length=8,
        )
        torch.testing.assert_close(input_ids, torch.tensor([10, 11, 20, 21, 99]))
        torch.testing.assert_close(labels, torch.tensor([-100, -100, 20, 21, 99]))
        torch.testing.assert_close(
            mask, torch.tensor([False, False, True, True, False])
        )

    def test_completion_contract_rejects_nonprefix_and_missing_end(self) -> None:
        with self.assertRaisesRegex(ValueError, "exact prefix"):
            contracts.completion_only_contract(
                [1, 2], [1, 3, 4], assistant_end_id=4, max_length=8
            )
        with self.assertRaisesRegex(ValueError, "end marker"):
            contracts.completion_only_contract(
                [1, 2], [1, 2, 3], assistant_end_id=4, max_length=8
            )

    def test_source_disjointness_passes_and_fails_closed(self) -> None:
        left = [pair("A", "source-a", "hash-a")]
        right = [pair("B", "source-b", "hash-b")]
        report = contracts.assert_source_disjoint({"train": left, "dev": right})
        self.assertEqual(report["status"], "PASS")
        with self.assertRaisesRegex(ValueError, "source_id overlap"):
            contracts.assert_source_disjoint(
                {"train": left, "dev": [pair("C", "source-a", "hash-c")]}
            )
        with self.assertRaisesRegex(ValueError, "normalized_question_sha256 overlap"):
            contracts.assert_source_disjoint(
                {"train": left, "dev": [pair("C", "source-c", "hash-a")]}
            )

    def test_real_canary_files_are_pairwise_disjoint(self) -> None:
        data = EXPERIMENT / "data"
        train, report = contracts.validate_disjoint_files(
            data / "lora_train_cf200_156.jsonl",
            [
                data / "lora_dev_cf3_113.jsonl",
                data / "behavior_canary_cue50_46.jsonl",
            ],
        )
        self.assertEqual(len(train), 156)
        self.assertEqual(report["status"], "PASS")
        self.assertTrue(all(item["overlap_count"] == 0 for item in report["checks"]))

    def test_validation_rejects_nonengineering_or_identical_pairs(self) -> None:
        row = pair("A", "source-a", "hash-a")
        row["engineering_only"] = False
        with self.assertRaisesRegex(ValueError, "engineering-only"):
            contracts.validate_paired_rows([row])
        row = pair(
            "A", "source-a", "hash-a", confident="same", hesitant="same"
        )
        with self.assertRaisesRegex(ValueError, "identical"):
            contracts.validate_paired_rows([row])


if __name__ == "__main__":
    unittest.main()
