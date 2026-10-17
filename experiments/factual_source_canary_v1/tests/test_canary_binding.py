import importlib.util
import json
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "src" / "canary_binding.py"
SPEC = importlib.util.spec_from_file_location("canary_binding_standalone", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def fixture() -> tuple[list[dict], list[dict]]:
    sources = []
    pairs = []
    for index in range(3):
        identity = {
            "source_id": f"private-source-{index}",
            "source_hash": f"private-source-hash-{index}",
            "original_response_sha256": str(index) * 64,
            "dataset": "asqa",
            "cue_family": "test",
            "length_direction": "confident_longer",
            "draft_order": "confident_first",
        }
        sources.append({
            **identity,
            "generation_order": index + 1,
            "group_id": f"private-group-{index}",
            "profile": "short_simple",
            "batch_id": "batch_01",
            "prompt": f"Private prompt {index}",
            "original_response": "secret",
            "protected_spans": ["literal span"],
            "protected_qualifiers": ["semantic constraint"],
        })
        pairs.append({
            **identity,
            "confident_response": f"Private confident rewrite {index}",
            "hesitant_response": f"Private hesitant rewrite {index}",
        })
    return sources, pairs


class CanaryBindingTests(unittest.TestCase):
    def test_binding_is_order_independent_and_text_free(self) -> None:
        sources, pairs = fixture()
        first = MODULE.build_artifact_binding(sources, pairs)
        second = MODULE.build_artifact_binding(
            list(reversed(sources)), list(reversed(pairs))
        )
        self.assertEqual(first, second)
        encoded = json.dumps(first)
        self.assertNotIn("private-source", encoded)
        self.assertNotIn("Private confident", encoded)

    def test_pair_text_change_changes_only_pair_binding(self) -> None:
        sources, pairs = fixture()
        first = MODULE.build_artifact_binding(sources, pairs)
        pairs[0]["confident_response"] += " changed"
        second = MODULE.build_artifact_binding(sources, pairs)
        self.assertEqual(first["source_set_sha256"], second["source_set_sha256"])
        self.assertEqual(first["source_ids_sha256"], second["source_ids_sha256"])
        self.assertNotEqual(first["pair_set_sha256"], second["pair_set_sha256"])

    def test_every_review_relevant_source_change_changes_source_binding(self) -> None:
        for field, changed_value in (
            ("prompt", "Changed private prompt"),
            ("original_response", "Changed original response"),
            ("protected_spans", ["changed literal span"]),
            ("protected_qualifiers", ["changed semantic constraint"]),
            ("profile", "changed_profile"),
            ("batch_id", "changed_batch"),
            ("group_id", "changed_group"),
        ):
            sources, pairs = fixture()
            baseline = MODULE.build_artifact_binding(sources, pairs)
            sources[0][field] = changed_value
            changed = MODULE.build_artifact_binding(sources, pairs)
            self.assertNotEqual(
                baseline["source_set_sha256"],
                changed["source_set_sha256"],
                field,
            )

    def test_duplicate_ids_and_invalid_binding_are_rejected(self) -> None:
        sources, pairs = fixture()
        sources[1]["source_id"] = sources[0]["source_id"]
        with self.assertRaisesRegex(ValueError, "duplicate source_id"):
            MODULE.build_artifact_binding(sources, pairs)
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            MODULE.validate_artifact_binding({
                "schema": MODULE.BINDING_SCHEMA,
                "source_count": 12,
                "pair_count": 12,
                "source_ids_sha256": "bad",
                "source_set_sha256": "1" * 64,
                "pair_set_sha256": "2" * 64,
            })


if __name__ == "__main__":
    unittest.main()
