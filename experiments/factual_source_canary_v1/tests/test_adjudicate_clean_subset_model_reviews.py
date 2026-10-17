import importlib.util
import unittest
from pathlib import Path


BASE = Path(__file__).resolve().parents[1]
MODULE_PATH = BASE / "src" / "adjudicate_clean_subset_model_reviews.py"
SPEC = importlib.util.spec_from_file_location(
    "adjudicate_clean_subset_model_reviews", MODULE_PATH
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def fixture():
    packet_hash = "a" * 64
    answer_key_hash = "b" * 64
    manifest = {
        "schema": "factual-rewrite-clean-subset-blind-review-v1",
        "artifact_role": "interim_failure_discovery_only",
        "pair_count": 6,
        "packet_sha256": packet_hash,
        "answer_key_sha256": answer_key_hash,
        "blinded": True,
        "answer_key_embedded_in_html": False,
        "final_canary_certification": False,
        "human_review_certified": False,
    }
    key = {
        "schema": "factual-rewrite-clean-subset-blind-key-v1",
        "packet_sha256": packet_hash,
        "rows": [
            {
                "review_id": f"C6R{index:03d}",
                "version_a_role": "confident" if index % 2 else "hesitant",
                "version_b_role": "hesitant" if index % 2 else "confident",
            }
            for index in range(1, 7)
        ],
    }
    rows = []
    for index in range(1, 7):
        intended = "a" if index % 2 else "b"
        other = "b" if intended == "a" else "a"
        row = {
            "review_id": f"C6R{index:03d}",
            "source_fidelity": "both_preserve",
            "pair_content_equivalence": "equivalent",
            "qualifier_preservation": "both_preserve",
            "speaker_level_scope": "both_speaker_level",
            "certainty_a": "5" if intended == "a" else "2",
            "certainty_b": "5" if intended == "b" else "2",
            "stronger_certainty": intended,
            "naturalness_a": "natural",
            "naturalness_b": "natural",
            "formatting_mismatch": "none",
            "shortcut_concern": "none",
        }
        assert row[f"certainty_{intended}"] == "5"
        assert row[f"certainty_{other}"] == "2"
        rows.append(row)
    base = {
        "schema": "factual-rewrite-clean-subset-review-results-v1",
        "artifact_role": "interim_failure_discovery_only",
        "review_type": "model_assisted",
        "independent_context": "A",
        "pair_count": 6,
        "packet_sha256": packet_hash,
        "blinded": True,
        "final_canary_certification": False,
        "human_review_certified": False,
        "reviews": rows,
    }
    second = {**base, "independent_context": "B"}
    input_hashes = {
        "manifest": "c" * 64,
        "answer_key": answer_key_hash,
        "model_reviews": ["d" * 64, "e" * 64],
    }
    return manifest, key, base, second, input_hashes


class AdjudicateCleanSubsetModelReviewsTests(unittest.TestCase):
    def test_two_agreeing_reviews_can_pass_all_six_without_certifying(self):
        manifest, key, first, second, input_hashes = fixture()
        summary = MODULE.build_summary(
            manifest, key, [first, second], input_sha256=input_hashes
        )
        self.assertEqual(summary["preliminary_outcome"]["strict_pass_pairs"], 6)
        self.assertFalse(summary["human_review_certified"])
        self.assertFalse(summary["final_canary_certification"])
        self.assertFalse(summary["authorization"]["activation_extraction"])

    def test_content_drift_and_weak_direction_fail_strict_gate(self):
        manifest, key, first, second, input_hashes = fixture()
        second = {**second, "reviews": [dict(row) for row in first["reviews"]]}
        for result in (first, second):
            result["reviews"][0]["pair_content_equivalence"] = "different"
            result["reviews"][1]["certainty_b"] = "3"
        summary = MODULE.build_summary(
            manifest, key, [first, second], input_sha256=input_hashes
        )
        self.assertEqual(summary["preliminary_outcome"]["strict_pass_pairs"], 4)
        self.assertEqual(
            summary["preliminary_outcome"]["content_or_scope_failure_pairs"], 1
        )

    def test_packet_hash_mismatch_is_rejected(self):
        manifest, key, first, second, input_hashes = fixture()
        second = {**second, "packet_sha256": "f" * 64}
        with self.assertRaisesRegex(ValueError, "metadata is invalid"):
            MODULE.build_summary(
                manifest, key, [first, second], input_sha256=input_hashes
            )

    def test_duplicate_review_files_and_contexts_are_rejected(self):
        manifest, key, first, second, input_hashes = fixture()
        duplicate_hashes = {
            **input_hashes,
            "model_reviews": ["d" * 64, "d" * 64],
        }
        with self.assertRaisesRegex(ValueError, "distinct SHA-256"):
            MODULE.build_summary(
                manifest, key, [first, second], input_sha256=duplicate_hashes
            )
        second = {**second, "independent_context": "A"}
        with self.assertRaisesRegex(ValueError, "distinct independent contexts"):
            MODULE.build_summary(
                manifest, key, [first, second], input_sha256=input_hashes
            )

    def test_answer_key_hash_must_match_manifest(self):
        manifest, key, first, second, input_hashes = fixture()
        bad_hashes = {**input_hashes, "answer_key": "f" * 64}
        with self.assertRaisesRegex(ValueError, "answer key"):
            MODULE.build_summary(
                manifest, key, [first, second], input_sha256=bad_hashes
            )


if __name__ == "__main__":
    unittest.main()
