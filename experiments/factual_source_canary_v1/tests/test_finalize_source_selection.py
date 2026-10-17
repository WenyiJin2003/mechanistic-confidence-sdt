import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "src" / "finalize_source_selection.py"
SPEC = importlib.util.spec_from_file_location("finalize_source_selection", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def source(dataset: str, source_id: str, rank: int) -> dict:
    return {
        "dataset": dataset,
        "source_id": source_id,
        "group_id": source_id,
        "source_hash": source_id,
        "review_rank": rank,
        "review_batch": 1,
        "word_count": 50,
        "sentence_count": 2,
        "evidence_word_count": 100,
        "question": "private",
        "original_response": "private",
        "evidence": "private",
    }


def review(dataset: str, source_id: str, rank: int, decision: str = "accept") -> dict:
    accepted = decision == "accept"
    return {
        "dataset": dataset,
        "source_id": source_id,
        "review_rank": rank,
        "decision": decision,
        "reason_codes": [],
        "protected_qualifiers": [],
        "evidence_support": accepted,
        "self_contained": accepted,
        "rewrite_suitable": accepted,
        "notes": "",
        "reviewer": "test",
    }


class FinalizeSelectionTests(unittest.TestCase):
    def test_selects_core_then_backup_in_review_order(self) -> None:
        queue = [source("demo", f"s{rank}", rank) for rank in range(1, 5)]
        reviews = [review("demo", f"s{rank}", rank) for rank in range(1, 5)]
        plan = {
            "core": {
                "quota_by_dataset": {"demo": 2},
                "backup_target_by_dataset": 1,
            }
        }
        selected, summary = MODULE.finalize(queue, reviews, plan, False)
        self.assertTrue(summary["gate_complete"])
        self.assertEqual([item["source_id"] for item in selected], ["s1", "s2", "s3"])
        self.assertEqual(
            [item["selection_role"] for item in selected],
            ["core", "core", "backup"],
        )

    def test_incomplete_gate_fails_closed(self) -> None:
        queue = [source("demo", "s1", 1)]
        reviews = [review("demo", "s1", 1)]
        plan = {
            "core": {
                "quota_by_dataset": {"demo": 1},
                "backup_target_by_dataset": 1,
            }
        }
        with self.assertRaisesRegex(ValueError, "2 are required"):
            MODULE.finalize(queue, reviews, plan, False)

    def test_secondary_downgrade_removes_primary_accept(self) -> None:
        queue = [source("demo", f"s{rank}", rank) for rank in range(1, 4)]
        reviews = [review("demo", f"s{rank}", rank) for rank in range(1, 4)]
        secondary = [
            {
                "source_id": "s1",
                "primary_decision": "accept",
                "secondary_decision": "downgrade_repair",
            }
        ]
        plan = {
            "core": {
                "quota_by_dataset": {"demo": 1},
                "backup_target_by_dataset": 1,
            }
        }
        selected, summary = MODULE.finalize(
            queue, reviews, plan, False, secondary_reviews=secondary
        )
        self.assertEqual([item["source_id"] for item in selected], ["s2", "s3"])
        self.assertEqual(summary["by_dataset"]["demo"]["accepted_count"], 2)

    def test_locked_secondary_sample_must_match_effective_accepts(self) -> None:
        queue = [source("demo", f"s{rank}", rank) for rank in range(1, 4)]
        reviews = [review("demo", f"s{rank}", rank) for rank in range(1, 4)]
        secondary = [
            {
                "source_id": "s1",
                "primary_decision": "accept",
                "secondary_decision": "confirm_accept",
                "in_final_sample": True,
            }
        ]
        plan = {
            "core": {
                "quota_by_dataset": {"demo": 1},
                "backup_target_by_dataset": 1,
            },
            "secondary_audit": {
                "sample_size_per_dataset": 1,
                "hash_prefix": "test:",
                "require_final_sample_confirmation": True,
            },
        }
        expected = min(
            reviews,
            key=lambda item: MODULE.audit_order_key("test:", item["source_id"]),
        )["source_id"]
        secondary[0]["source_id"] = expected
        selected, summary = MODULE.finalize(
            queue, reviews, plan, False, secondary_reviews=secondary
        )
        self.assertEqual(summary["by_dataset"]["demo"]["final_secondary_sample_count"], 1)
        secondary[0]["source_id"] = "s1" if expected != "s1" else "s2"
        with self.assertRaisesRegex(ValueError, "secondary sample"):
            MODULE.finalize(queue, reviews, plan, False, secondary_reviews=secondary)

    def test_accept_requires_all_quality_checks(self) -> None:
        queued = source("demo", "s1", 1)
        reviewed = review("demo", "s1", 1)
        reviewed["evidence_support"] = False
        with self.assertRaisesRegex(ValueError, "evidence_support"):
            MODULE.validate_review(reviewed, queued)

    def test_public_record_excludes_text_and_notes(self) -> None:
        record = source("demo", "s1", 1)
        record.update(
            {
                "selection_role": "core",
                "model_review_decision": "accept",
                "model_review_reason_codes": [],
                "notes": "private",
                "protected_qualifiers": ["private"],
            }
        )
        public = MODULE.public_record(record)
        for key in MODULE.PRIVATE_FIELDS:
            self.assertNotIn(key, public)


if __name__ == "__main__":
    unittest.main()
