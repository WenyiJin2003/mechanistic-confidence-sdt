import hashlib
import importlib.util
import json
import tempfile
import unittest
from collections import Counter, defaultdict
from pathlib import Path


BASE = Path(__file__).resolve().parents[1]
MODULE_PATH = BASE / "src" / "build_factual_rewrite_clean_subset_review.py"
SPEC = importlib.util.spec_from_file_location(
    "build_factual_rewrite_clean_subset_review", MODULE_PATH
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def text_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def fixture() -> tuple[list[dict], dict, dict]:
    clean_design = (
        ("billsum", "confident_longer", "confident_first", "modal"),
        ("billsum", "hesitant_longer", "hesitant_first", "embedded"),
        ("billsum", "hesitant_longer", "confident_first", "discourse"),
        ("qasper", "confident_longer", "confident_first", "modal"),
        ("qasper", "hesitant_longer", "hesitant_first", "embedded"),
        ("qasper", "confident_longer", "hesitant_first", "polarity"),
    )
    sources: list[dict] = []
    pairs: list[dict] = []
    validator_rows: list[dict] = []
    for index in range(12):
        if index < 6:
            dataset, length, draft, cue = clean_design[index]
            failure_flags: list[str] = []
        else:
            dataset = "asqa"
            length = "confident_longer" if index % 2 else "hesitant_longer"
            draft = "confident_first" if index % 2 else "hesitant_first"
            cue = f"dirty-cue-{index}"
            failure_flags = ["mechanical_failure"]
        source_id = f"private-{index:02d}"
        original = f"Original response {index} with fixed factual content."
        identity = {
            "source_id": source_id,
            "source_hash": text_sha256(f"source-{index}"),
            "original_response_sha256": text_sha256(original),
            "dataset": dataset,
            "cue_family": cue,
            "length_direction": length,
            "draft_order": draft,
        }
        sources.append({
            **identity,
            "prompt": f"Question {index}?",
            "original_response": original,
            "protected_spans": [],
            "protected_qualifiers": [],
        })
        pairs.append({
            **identity,
            "confident_response": f"Confident complete response {index}.",
            "hesitant_response": f"Hesitant complete response {index}.",
        })
        validator_rows.append({
            **identity,
            "mechanical_gate_pass": not failure_flags,
            "failure_flags": failure_flags,
        })
    full_rows = MODULE.review.join_sources_and_pairs(sources, pairs)
    validator = {
        "rows": validator_rows,
        "global_failure_flags": [],
        "artifact_binding": MODULE.build_artifact_binding(full_rows, full_rows),
    }
    config = {
        "full_pair_count": 12,
        "selected_pair_count": 6,
        "expected_selected_dataset_counts": {"billsum": 3, "qasper": 3},
    }
    return full_rows, validator, config


class CleanSubsetReviewTests(unittest.TestCase):
    def test_selects_only_six_mechanical_pass_rows_from_complete_set(self) -> None:
        full_rows, validator, config = fixture()
        selected = MODULE.select_clean_subset(full_rows, validator, config)
        self.assertEqual(len(selected), 6)
        self.assertEqual(
            Counter(row["dataset"] for row in selected),
            Counter({"billsum": 3, "qasper": 3}),
        )

    def test_validator_must_cover_full_bound_set(self) -> None:
        full_rows, validator, config = fixture()
        validator["rows"][0]["source_id"] = "unknown"
        with self.assertRaisesRegex(ValueError, "source sets differ"):
            MODULE.select_clean_subset(full_rows, validator, config)

    def test_mechanical_boolean_must_match_failure_flags(self) -> None:
        full_rows, validator, config = fixture()
        validator["rows"][0]["mechanical_gate_pass"] = False
        with self.assertRaisesRegex(ValueError, "mechanical gate"):
            MODULE.select_clean_subset(full_rows, validator, config)

    def test_clean6_roles_are_deterministic_and_nuisance_balanced(self) -> None:
        full_rows, validator, config = fixture()
        selected = MODULE.select_clean_subset(full_rows, validator, config)
        roles = MODULE.balanced_clean6_a_roles(selected, seed=20261017)
        reversed_roles = MODULE.balanced_clean6_a_roles(
            list(reversed(selected)), seed=20261017
        )
        self.assertEqual(roles, reversed_roles)
        self.assertEqual(
            Counter(roles.values()), Counter({"confident": 3, "hesitant": 3})
        )
        for field in ("dataset", "length_direction", "draft_order"):
            groups: dict[str, list[dict]] = defaultdict(list)
            for row in selected:
                groups[row[field]].append(row)
            for rows in groups.values():
                counts = Counter(roles[row["source_id"]] for row in rows)
                self.assertEqual(sorted(counts.values()), [1, 2])
        cue_groups: dict[str, list[dict]] = defaultdict(list)
        for row in selected:
            cue_groups[row["cue_family"]].append(row)
        for rows in cue_groups.values():
            if len(rows) == 2:
                self.assertEqual(
                    Counter(roles[row["source_id"]] for row in rows),
                    Counter({"confident": 1, "hesitant": 1}),
                )

    def test_clean6_bundle_is_separate_private_and_label_blind(self) -> None:
        full_rows, validator, config = fixture()
        selected = MODULE.select_clean_subset(full_rows, validator, config)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            private = root / "private_data"
            output = private / "clean6"
            result = MODULE.write_clean6_review_bundle(
                full_rows,
                selected,
                output,
                seed=20261017,
                input_hashes={
                    "frozen_sources_v4": "0" * 64,
                    "post_repair_pairs_v4": "1" * 64,
                    "post_repair_validator_v4": "2" * 64,
                    "post_repair_provenance_v4": "3" * 64,
                    "freeze_manifest_v4": "4" * 64,
                },
                config_sha256="1" * 64,
                private_root=private,
            )
            manifest = result["manifest"]
            page = (output / "reviewer_only" / "BLIND_REVIEW.html").read_text(
                encoding="utf-8"
            )
            key = json.loads(
                (output / "private_key" / "BLIND_REVIEW_KEY.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(
                manifest["schema"],
                "factual-rewrite-clean-subset-blind-review-v1",
            )
            self.assertEqual(manifest["artifact_role"], "interim_failure_discovery_only")
            self.assertFalse(manifest["final_canary_certification"])
            self.assertFalse(manifest["human_review_certified"])
            self.assertIn("pair_content_equivalence", manifest["review_fields"])
            self.assertIn("Clean-six interim blind review", page)
            self.assertIn("factual-rewrite-clean-subset-review-results-v1", page)
            self.assertIn("interim_failure_discovery_only", page)
            self.assertEqual(len(key["rows"]), 6)
            self.assertTrue(all(row["review_id"].startswith("C6R") for row in key["rows"]))
            for row in key["rows"]:
                self.assertNotIn(row["source_id"], page)
                self.assertNotIn(row["source_hash"], page)
            for forbidden in (
                '"source_id"',
                '"dataset"',
                '"cue_family"',
                '"length_direction"',
                '"version_a_role"',
                '"mechanical_gate_pass"',
            ):
                self.assertNotIn(forbidden, page)

            public_path = root / "packet-summary.json"
            status = MODULE.write_public_packet_summary(manifest, public_path)
            encoded = public_path.read_text(encoding="utf-8")
            self.assertEqual(status["status"], "packet_prepared")
            self.assertFalse(status["review_completion_tracked_here"])
            self.assertEqual(
                status["current_review_summary"],
                "rewrite_canary_v4_clean_six_model_review_summary.json",
            )
            self.assertFalse(status["final_canary_certification"])
            self.assertFalse(status["human_review_certified"])
            for row in key["rows"]:
                self.assertNotIn(row["source_id"], encoded)
                self.assertNotIn(row["source_hash"], encoded)

    def test_bundle_writer_rejects_non_subset_and_incomplete_hash_binding(self) -> None:
        full_rows, validator, config = fixture()
        selected = MODULE.select_clean_subset(full_rows, validator, config)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            private = root / "private_data"
            tampered = [dict(row) for row in selected]
            tampered[0]["prompt"] = "Different private prompt"
            with self.assertRaisesRegex(ValueError, "exact subset"):
                MODULE.write_clean6_review_bundle(
                    full_rows,
                    tampered,
                    private / "bad-subset",
                    seed=20261017,
                    input_hashes={
                        "frozen_sources_v4": "0" * 64,
                        "post_repair_pairs_v4": "1" * 64,
                        "post_repair_validator_v4": "2" * 64,
                        "post_repair_provenance_v4": "3" * 64,
                        "freeze_manifest_v4": "4" * 64,
                    },
                    config_sha256="5" * 64,
                    private_root=private,
                )
            with self.assertRaisesRegex(ValueError, "all five valid input hashes"):
                MODULE.write_clean6_review_bundle(
                    full_rows,
                    selected,
                    private / "bad-hashes",
                    seed=20261017,
                    input_hashes={"only_one": "0" * 64},
                    config_sha256="5" * 64,
                    private_root=private,
                )


if __name__ == "__main__":
    unittest.main()
