import importlib.util
import json
import tempfile
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "src" / "prepare_factual_rewrite_canary.py"
SPEC = importlib.util.spec_from_file_location("prepare_factual_rewrite_canary", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


BASE_EXPECTED_IDS = {
    "asqa": {
        "short_simple": "asqa:5767411579190718767",
        "mid_plain": "asqa:2074116551547919110",
        "long_complex": "asqa:-4867406118701628228",
        "qualifier_sensitive": "asqa:-9159547197550283952",
    },
    "qasper": {
        "short_simple": "qasper-paper:1702.03274",
        "mid_plain": "qasper-paper:1801.07537",
        "long_complex": "qasper-paper:2001.06286",
        "qualifier_sensitive": "qasper-paper:2003.02639",
    },
    "billsum": {
        "short_simple": "billsum:38e284eb53182859",
        "mid_plain": "billsum:44172515b22eaae0",
        "long_complex": "billsum:a6050ac8d28cdeb0",
        "qualifier_sensitive": "billsum:1b0226a63ea123f1",
    },
}

EXPECTED_IDS = {
    **BASE_EXPECTED_IDS,
    "billsum": {
        **BASE_EXPECTED_IDS["billsum"],
        "long_complex": "billsum:fa9b594a589c0757",
    },
}


def prompt_row() -> dict:
    return {
        "source_id": "demo:1",
        "dataset": "demo",
        "group_id": "group:1",
        "source_hash": "a" * 64,
        "original_response_sha256": "b" * 64,
        "profile": "short_simple",
        "prompt": "What is the answer?",
        "original_response": "The measured result may be five.",
        "protected_qualifiers": ["may be five", "conditional estimate"],
        "protected_spans": ["may be five"],
        "cue_family": "embedded_stance_predicate",
        "length_direction": "confident_longer",
        "draft_order": "confident_first",
        "generation_order": 1,
        "batch_id": "batch_01",
        "batch_position": 1,
        "word_count": 6,
        "sentence_count": 1,
        "selection_features": [0.2, 0.2, 0.2],
        "selection_target": [0.2, 0.2, 0.2],
        "selection_distance": 0.0,
        "source_selection_role": "core",
        "source_review_rank": 1,
        "replacement_for_source_id": None,
        "replacement_reason_code": None,
        "replacement_reason": None,
        "replacement_rule": None,
        "replaced_source_hash": None,
        "replaced_source_review_rank": None,
    }


class PrepareFactualRewriteCanaryTests(unittest.TestCase):
    def setUp(self) -> None:
        MODULE.load_config(MODULE.DEFAULT_CONFIG)

    def test_midrank_uses_average_one_based_rank_divided_by_n(self) -> None:
        values = [1, 1, 2, 4]
        self.assertEqual(MODULE.midrank_percentile(1, values), 0.375)
        self.assertEqual(MODULE.midrank_percentile(2, values), 0.75)
        self.assertEqual(MODULE.midrank_percentile(4, values), 1.0)

    def test_literal_protected_spans_exclude_paraphrased_descriptors(self) -> None:
        response = "The numerical Results Suggest that the value may rise."
        descriptors = ["results suggest", "may rise", "conditional estimate"]
        self.assertEqual(
            MODULE.literal_protected_spans(response, descriptors),
            ["Results Suggest", "may rise"],
        )

    def test_default_private_source_reproduces_locked_base_twelve_ids(self) -> None:
        if not MODULE.DEFAULT_SOURCE.exists():
            self.skipTest("ignored private frozen-source file is unavailable")
        selected = MODULE.select_canary_sources(MODULE.read_jsonl(MODULE.DEFAULT_SOURCE))
        actual = {
            row["dataset"]: {
                candidate["profile"]: candidate["source_id"]
                for candidate in selected
                if candidate["dataset"] == row["dataset"]
            }
            for row in selected
        }
        self.assertEqual(actual, BASE_EXPECTED_IDS)

    def test_failed_source_uses_next_ranked_backup_and_preserves_slot(self) -> None:
        if not MODULE.DEFAULT_SOURCE.exists():
            self.skipTest("ignored private frozen-source file is unavailable")
        source_rows = MODULE.read_jsonl(MODULE.DEFAULT_SOURCE)
        selected = MODULE.select_canary_sources(source_rows)
        MODULE.assign_cue_families(selected)
        MODULE.assign_length_directions(selected)
        MODULE.assign_draft_orders(selected)
        batches = MODULE.order_batches(selected)
        failed = next(
            row
            for batch in batches
            for row in batch
            if row["source_id"] == "billsum:a6050ac8d28cdeb0"
        )
        replaced, mappings = MODULE.apply_configured_replacements(
            batches, source_rows
        )
        effective_rows = [row for batch in replaced for row in batch]
        replacement = next(
            row
            for row in effective_rows
            if row["source_id"] == "billsum:fa9b594a589c0757"
        )
        eligible = sorted(
            (
                row
                for row in source_rows
                if row["dataset"] == "billsum"
                and row["selection_role"] == "backup"
                and row["source_id"] not in {
                    candidate["source_id"]
                    for batch in batches
                    for candidate in batch
                }
            ),
            key=lambda row: (int(row["review_rank"]), row["source_id"]),
        )
        self.assertEqual(replacement["source_id"], eligible[0]["source_id"])
        self.assertNotIn(
            "billsum:a6050ac8d28cdeb0",
            {row["source_id"] for row in effective_rows},
        )
        for field in MODULE.DESIGN["source_replacement"]["preserved_slot_fields"]:
            self.assertEqual(replacement[field], failed[field])
        self.assertEqual(len(mappings), 1)
        self.assertEqual(
            mappings[0]["replacement_source_id"], "billsum:fa9b594a589c0757"
        )
        self.assertEqual(
            mappings[0]["reason_code"],
            "pair_validation_failed_after_allowed_repairs",
        )

    def test_effective_default_canary_reproduces_locked_replacement_ids(self) -> None:
        if not MODULE.DEFAULT_SOURCE.exists():
            self.skipTest("ignored private frozen-source file is unavailable")
        source_rows = MODULE.read_jsonl(MODULE.DEFAULT_SOURCE)
        selected = MODULE.select_canary_sources(source_rows)
        MODULE.assign_cue_families(selected)
        MODULE.assign_length_directions(selected)
        MODULE.assign_draft_orders(selected)
        batches, _ = MODULE.apply_configured_replacements(
            MODULE.order_batches(selected), source_rows
        )
        actual = {
            row["dataset"]: {
                candidate["profile"]: candidate["source_id"]
                for batch in batches
                for candidate in batch
                if candidate["dataset"] == row["dataset"]
            }
            for batch in batches
            for row in batch
        }
        self.assertEqual(actual, EXPECTED_IDS)

    def test_assignments_are_balanced_and_batches_cover_grid(self) -> None:
        if not MODULE.DEFAULT_SOURCE.exists():
            self.skipTest("ignored private frozen-source file is unavailable")
        selected = MODULE.select_canary_sources(MODULE.read_jsonl(MODULE.DEFAULT_SOURCE))
        MODULE.assign_cue_families(selected)
        MODULE.assign_length_directions(selected)
        MODULE.assign_draft_orders(selected)
        batches, _ = MODULE.apply_configured_replacements(
            MODULE.order_batches(selected), MODULE.read_jsonl(MODULE.DEFAULT_SOURCE)
        )
        frozen = [[MODULE.freeze_record(row) for row in batch] for batch in batches]
        rows = [row for batch in frozen for row in batch]
        MODULE.validate_design(rows, frozen)
        self.assertEqual(
            Counter(row["cue_family"] for row in rows),
            Counter(dict(MODULE.CUE_FAMILY_TARGETS)),
        )
        self.assertEqual(
            Counter(row["length_direction"] for row in rows),
            Counter({"confident_longer": 6, "hesitant_longer": 6}),
        )
        for dataset in MODULE.DATASETS:
            self.assertEqual(
                Counter(
                    row["length_direction"]
                    for row in rows
                    if row["dataset"] == dataset
                ),
                Counter({"confident_longer": 2, "hesitant_longer": 2}),
            )
            self.assertEqual(
                Counter(
                    row["draft_order"]
                    for row in rows
                    if row["dataset"] == dataset
                ),
                Counter({"confident_first": 2, "hesitant_first": 2}),
            )
        for batch in frozen:
            self.assertEqual(
                Counter(row["length_direction"] for row in batch),
                Counter({"confident_longer": 2, "hesitant_longer": 2}),
            )
            self.assertEqual(
                Counter(row["draft_order"] for row in batch),
                Counter({"confident_first": 2, "hesitant_first": 2}),
            )

    def test_public_record_contains_counts_but_no_private_text(self) -> None:
        public = MODULE.public_record(prompt_row())
        self.assertEqual(public["protected_qualifier_count"], 2)
        self.assertEqual(public["protected_span_count"], 1)
        self.assertEqual(public["source_selection_role"], "core")
        self.assertTrue(MODULE.PRIVATE_TEXT_FIELDS.isdisjoint(public))

    def test_writer_prompt_uses_canonical_hesitant_response_field(self) -> None:
        text = MODULE.writer_prompt([prompt_row()], 1, 1)
        self.assertIn('"hesitant_response"', text)
        self.assertNotIn('"hedged_response"', text)
        self.assertIn('"draft_order"', text)
        self.assertIn("Reviewer-only semantic qualifier descriptors", text)
        self.assertIn("sole authority for content", text)
        self.assertIn("exact source substring", text)
        self.assertIn("max(5 tokens, 5% of the pair mean)", text)

    def test_writer_payload_withholds_descriptor_only_qualifiers(self) -> None:
        row = prompt_row()
        text = MODULE.writer_prompt([row], 1, 1)
        payload = json.loads(text.split("INPUT_RECORDS_JSON\n", 1)[1])
        self.assertNotIn("protected_qualifiers", payload[0])
        self.assertNotIn("conditional estimate", text)
        self.assertEqual(payload[0]["protected_spans"], ["may be five"])
        self.assertEqual(
            row["protected_qualifiers"],
            ["may be five", "conditional estimate"],
        )

    def test_private_output_guard_rejects_public_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "private_data"
            root.mkdir()
            accepted = MODULE.require_private_output(root / "canary", root)
            self.assertEqual(accepted, (root / "canary").resolve())
            with self.assertRaisesRegex(ValueError, "must stay below"):
                MODULE.require_private_output(Path(directory) / "results", root)

    def test_generated_public_manifest_is_text_free_when_present(self) -> None:
        path = ROOT / "results" / "rewrite_canary_v1_source_manifest.jsonl"
        if not path.exists():
            self.skipTest("generated public canary manifest is unavailable")
        rows = MODULE.read_jsonl(path)
        self.assertEqual(len(rows), 12)
        self.assertTrue(all(MODULE.PRIVATE_TEXT_FIELDS.isdisjoint(row) for row in rows))
        self.assertEqual(
            {row["source_id"] for row in rows},
            {source_id for mapping in EXPECTED_IDS.values() for source_id in mapping.values()},
        )
        replacement = next(
            row for row in rows if row["source_id"] == "billsum:fa9b594a589c0757"
        )
        self.assertEqual(
            replacement["replacement_for_source_id"],
            "billsum:a6050ac8d28cdeb0",
        )
        self.assertEqual(replacement["source_selection_role"], "backup")
        self.assertTrue(replacement["replacement_rule"])

    def test_v2_writer_and_validation_batches_separate_private_review_fields(self) -> None:
        output = ROOT / "private_data" / "rewrite_canary_v1"
        writer_path = output / "SOURCE_BATCH_01_V2.jsonl"
        validation_path = output / "SOURCE_BATCH_01_VALIDATION_V2.jsonl"
        if not writer_path.exists() or not validation_path.exists():
            self.skipTest("generated private v2 canary batches are unavailable")
        writer_rows = MODULE.read_jsonl(writer_path)
        validation_rows = MODULE.read_jsonl(validation_path)
        self.assertEqual(len(writer_rows), len(validation_rows))
        self.assertTrue(
            all("protected_qualifiers" not in row for row in writer_rows)
        )
        self.assertTrue(
            all("protected_qualifiers" in row for row in validation_rows)
        )
        self.assertTrue(
            all(row["source_set_revision"] == "v2" for row in validation_rows)
        )
        self.assertEqual(
            [row["source_id"] for row in writer_rows],
            [row["source_id"] for row in validation_rows],
        )

    def test_public_summary_records_v2_replacement_provenance(self) -> None:
        path = ROOT / "results" / "rewrite_canary_v1_freeze_summary.json"
        if not path.exists():
            self.skipTest("generated public canary summary is unavailable")
        summary = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(summary["source_set_revision"], "v2")
        replacements = summary["source_replacements"]
        self.assertEqual(replacements["count"], 1)
        mapping = replacements["mappings"][0]
        self.assertEqual(
            mapping["failed_source_id"], "billsum:a6050ac8d28cdeb0"
        )
        self.assertEqual(
            mapping["replacement_source_id"], "billsum:fa9b594a589c0757"
        )
        self.assertEqual(
            mapping["reason_code"], "pair_validation_failed_after_allowed_repairs"
        )

    def test_config_declares_canonical_writer_fields(self) -> None:
        config = json.loads(MODULE.DEFAULT_CONFIG.read_text(encoding="utf-8"))
        fields = config["fields"]["writer_output_fields"]
        prompt_fields = config["fields"]["writer_prompt_fields"]
        self.assertIn("hesitant_response", fields)
        self.assertNotIn("hedged_response", fields)
        self.assertIn("draft_order", fields)
        self.assertIn("protected_spans", prompt_fields)
        self.assertNotIn("protected_qualifiers", prompt_fields)
        self.assertEqual(
            config["fields"]["review_only_fields"], ["protected_qualifiers"]
        )
        self.assertEqual(config["fields"]["legacy_output_alias"], "hedged_response")
        replacement = config["source_replacement"]
        self.assertEqual(replacement["eligible_role"], "backup")
        self.assertEqual(
            replacement["failed_sources"][0]["expected_replacement_source_id"],
            "billsum:fa9b594a589c0757",
        )


if __name__ == "__main__":
    unittest.main()
