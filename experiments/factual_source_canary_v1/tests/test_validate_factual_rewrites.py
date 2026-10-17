from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import validate_factual_rewrites as validator


class WordTokenizer:
    def __call__(self, text: str, add_special_tokens: bool = False):
        return {"input_ids": list(range(len(text.split())))}

    def apply_chat_template(self, messages, tokenize: bool = True):
        joined = " ".join(message["content"] for message in messages)
        return list(range(len(joined.split())))


def make_source(index: int, dataset: str, within_dataset: int) -> dict:
    number = 100 + index
    prompt = f"Summarize factual record {number}."
    original = (
        f"The report concludes that the recorded value may be {number} units, based on "
        f"the listed method at https://example.test/item/{number} and the archived "
        "measurement. Use `marker` for the reference record."
    )
    evidence = f"Evidence supporting factual record {number}."
    direction = "confident_longer" if within_dataset < 2 else "hesitant_longer"
    draft_order = "confident_first" if within_dataset in (0, 3) else "hesitant_first"
    return {
        "source_id": f"{dataset}:{index}",
        "dataset": dataset,
        "group_id": f"{dataset}-group-{index}",
        "source_hash": validator.stable_source_hash(dataset, prompt, original, evidence),
        "original_response_sha256": validator.sha256_text(original),
        "prompt": prompt,
        "original_response": original,
        "evidence": evidence,
        "protected_qualifiers": [],
        "protected_spans": [f"may be {number} units"],
        "cue_family": f"cue-{index % 5}",
        "length_direction": direction,
        "draft_order": draft_order,
        "generation_order": index,
    }


def make_pair(source: dict) -> dict:
    original = source["original_response"]
    if source["length_direction"] == "confident_longer":
        confident = original.replace(
            "The report concludes", "The report firmly and confidently concludes", 1
        )
        hesitant = original.replace("The report concludes", "The report tentatively concludes", 1)
    else:
        confident = original.replace("The report concludes", "The report firmly concludes", 1)
        hesitant = original.replace(
            "The report concludes", "The report tentatively and cautiously concludes", 1
        )
    return {
        "source_id": source["source_id"],
        "source_hash": source["source_hash"],
        "original_response_sha256": source["original_response_sha256"],
        "dataset": source["dataset"],
        "cue_family": source["cue_family"],
        "length_direction": source["length_direction"],
        "draft_order": source["draft_order"],
        "confident_response": confident,
        "hesitant_response": hesitant,
        "issues": [],
    }


def make_batch() -> tuple[list[dict], list[dict]]:
    sources: list[dict] = []
    index = 1
    for dataset in ("asqa", "billsum", "qasper"):
        for within_dataset in range(4):
            sources.append(make_source(index, dataset, within_dataset))
            index += 1
    return sources, [make_pair(source) for source in sources]


def row_for(report: dict, source_id: str) -> dict:
    return next(row for row in report["rows"] if row["source_id"] == source_id)


class ValidateFactualRewritesTests(unittest.TestCase):
    def setUp(self):
        self.tokenizer = WordTokenizer()

    def test_valid_balanced_twelve_passes_mechanical_gate(self):
        sources, pairs = make_batch()
        report = validator.validate_factual_rewrites(sources, pairs, self.tokenizer)
        self.assertTrue(report["mechanical_gate_pass"])
        self.assertFalse(report["manual_review_required"])
        self.assertEqual(report["status_counts"], {"pass": 12})
        self.assertEqual(report["global_failure_flags"], [])
        self.assertEqual(
            report["draft_order_counts"],
            {"confident_first": 6, "hesitant_first": 6},
        )
        self.assertEqual(
            report["length_direction_counts"],
            {"confident_longer": 6, "hesitant_longer": 6},
        )

    def test_semantic_qualifier_is_manual_not_literal_check(self):
        sources, pairs = make_batch()
        private_descriptor = "limited to the population and time period described by the evidence"
        sources[0]["protected_qualifiers"] = [private_descriptor]
        report = validator.validate_factual_rewrites(sources, pairs, self.tokenizer)
        audit = row_for(report, sources[0]["source_id"])
        self.assertTrue(report["mechanical_gate_pass"])
        self.assertTrue(report["manual_review_required"])
        self.assertEqual(audit["validation_status"], "manual_review")
        self.assertEqual(
            audit["manual_review_flags"],
            ["semantic_protected_qualifiers_require_manual_review"],
        )
        encoded = json.dumps(report)
        self.assertNotIn(private_descriptor, encoded)
        self.assertFalse(any("protected_span" in flag for flag in audit["failure_flags"]))

    def test_number_url_code_and_protected_span_drift_fail(self):
        sources, pairs = make_batch()
        pair = pairs[0]
        pair["confident_response"] = (
            pair["confident_response"]
            .replace("101 units", "999 units")
            .replace("https://example.test/item/101", "https://other.test/item/999")
            .replace("`marker`", "`changed`")
        )
        report = validator.validate_factual_rewrites(sources, pairs, self.tokenizer)
        audit = row_for(report, sources[0]["source_id"])
        self.assertFalse(report["mechanical_gate_pass"])
        self.assertEqual(audit["validation_status"], "fail")
        flags = set(audit["failure_flags"])
        self.assertIn("confident_numbers_changed", flags)
        self.assertIn("confident_urls_changed", flags)
        self.assertIn("confident_inline_code_changed", flags)
        self.assertIn("confident_protected_span_1_count_changed", flags)

    def test_identity_hash_and_nonverbatim_checks(self):
        sources, pairs = make_batch()
        pair = pairs[0]
        pair["source_hash"] = "0" * 64
        pair["original_response_sha256"] = "1" * 64
        pair["confident_response"] = sources[0]["original_response"]
        report = validator.validate_factual_rewrites(sources, pairs, self.tokenizer)
        flags = set(row_for(report, sources[0]["source_id"])["failure_flags"])
        self.assertIn("pair_source_hash_mismatch", flags)
        self.assertIn("pair_original_response_sha256_mismatch", flags)
        self.assertIn("confident_response_verbatim_source", flags)

    def test_legacy_hedged_alias_is_tolerated_and_flagged(self):
        sources, pairs = make_batch()
        pair = pairs[0]
        pair["hedged_response"] = pair.pop("hesitant_response")
        report = validator.validate_factual_rewrites(sources, pairs, self.tokenizer)
        audit = row_for(report, sources[0]["source_id"])
        self.assertTrue(report["mechanical_gate_pass"])
        self.assertEqual(audit["validation_status"], "pass")
        self.assertIn("legacy_hedged_response_alias_used", audit["warning_flags"])

    def test_length_policy_and_direction_are_enforced(self):
        sources, pairs = make_batch()
        pair = pairs[0]
        pair["confident_response"], pair["hesitant_response"] = (
            pair["hesitant_response"],
            pair["confident_response"],
        )
        report = validator.validate_factual_rewrites(sources, pairs, self.tokenizer)
        flags = set(row_for(report, sources[0]["source_id"])["failure_flags"])
        self.assertIn("length_direction_incorrect", flags)

        sources, pairs = make_batch()
        pairs[0]["confident_response"] += " Extra filler words that make this arm too long."
        report = validator.validate_factual_rewrites(sources, pairs, self.tokenizer)
        flags = set(row_for(report, sources[0]["source_id"])["failure_flags"])
        self.assertTrue(
            {"confident_source_token_ratio_out_of_bounds", "pair_token_ratio_over_limit", "pair_token_gap_over_limit"}
            & flags
        )

    def test_source_hash_is_recomputed_when_evidence_is_present(self):
        sources, pairs = make_batch()
        sources[0]["source_hash"] = "f" * 64
        pairs[0]["source_hash"] = "f" * 64
        report = validator.validate_factual_rewrites(sources, pairs, self.tokenizer)
        flags = set(row_for(report, sources[0]["source_id"])["failure_flags"])
        self.assertIn("source_hash_content_mismatch", flags)

    def test_allocation_and_draft_order_echo_are_validated(self):
        sources, pairs = make_batch()
        sources[0]["draft_order"] = "hesitant_first"
        pairs[0]["draft_order"] = "confident_first"
        report = validator.validate_factual_rewrites(sources, pairs, self.tokenizer)
        self.assertIn("draft_order_not_globally_balanced", report["global_failure_flags"])
        self.assertIn("draft_order_not_2_2_within_dataset", report["global_failure_flags"])
        flags = set(row_for(report, sources[0]["source_id"])["failure_flags"])
        self.assertIn("pair_draft_order_mismatch", flags)

    def test_missing_and_unknown_pair_ids_fail_closed(self):
        sources, pairs = make_batch()
        missing_id = pairs[0]["source_id"]
        unknown = dict(pairs.pop(0), source_id="unknown-source")
        pairs.append(unknown)
        report = validator.validate_factual_rewrites(sources, pairs, self.tokenizer)
        self.assertFalse(report["mechanical_gate_pass"])
        self.assertIn("source_pair_id_set_mismatch", report["global_failure_flags"])
        self.assertIn("pair_record_missing", row_for(report, missing_id)["failure_flags"])
        self.assertIn(
            "pair_source_id_unknown",
            row_for(report, "unknown-source")["failure_flags"],
        )

    def test_malformed_dataset_is_reported_without_sort_failure(self):
        sources, pairs = make_batch()
        del sources[0]["dataset"]
        report = validator.validate_factual_rewrites(sources, pairs, self.tokenizer)
        self.assertEqual(report["dataset_counts"]["<missing>"], 1)
        self.assertIn(
            "source_dataset_missing",
            row_for(report, sources[0]["source_id"])["failure_flags"],
        )

    def test_public_summary_removes_row_level_material(self):
        sources, pairs = make_batch()
        report = validator.validate_factual_rewrites(sources, pairs, self.tokenizer)
        summary = validator.public_summary(report)
        encoded = json.dumps(summary)
        self.assertNotIn("rows", summary)
        self.assertNotIn(sources[0]["source_id"], encoded)
        self.assertNotIn(sources[0]["original_response"], json.dumps(report))
        self.assertNotIn(pairs[0]["confident_response"], json.dumps(report))

    def test_inputs_are_not_mutated(self):
        sources, pairs = make_batch()
        source_copy = copy.deepcopy(sources)
        pair_copy = copy.deepcopy(pairs)
        validator.validate_factual_rewrites(sources, pairs, self.tokenizer)
        self.assertEqual(sources, source_copy)
        self.assertEqual(pairs, pair_copy)


if __name__ == "__main__":
    unittest.main()
