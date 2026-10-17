import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "src" / "audit_factual_rewrites.py"
SPEC = importlib.util.spec_from_file_location("audit_factual_rewrites", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def source(
    source_id: str = "s1",
    text: str = "The source states that the result contains forty two units.",
    direction: str = "confident_longer",
    dataset: str = "asqa",
    draft_order: str = "confident_first",
) -> dict:
    return {
        "source_id": source_id,
        "source_hash": f"source-hash-{source_id}",
        "original_response_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "dataset": dataset,
        "cue_family": "embedded_stance_predicate",
        "length_direction": direction,
        "draft_order": draft_order,
        "original_response": text,
        "protected_qualifiers": [],
    }


def writer(src: dict, confident: str, hesitant: str, *, legacy: bool = False) -> dict:
    row = {
        "source_id": src["source_id"],
        "source_hash": src["source_hash"],
        "original_response_sha256": src["original_response_sha256"],
        "dataset": src["dataset"],
        "cue_family": src["cue_family"],
        "length_direction": src["length_direction"],
        "draft_order": src["draft_order"],
        "confident_response": confident,
        "issues": [],
    }
    row["hedged_response" if legacy else "hesitant_response"] = hesitant
    return row


class FactualRewriteAuditTests(unittest.TestCase):
    def test_verbatim_arm_is_rejected(self) -> None:
        src = source()
        row = writer(
            src,
            src["original_response"],
            "I tentatively infer that the stated result contains forty two units.",
        )
        audits, _, _ = MODULE.audit_factual_rewrites([src], [row])
        self.assertIn("confident_verbatim_source", audits[0]["flags"])
        self.assertEqual(audits[0]["shortcut_status"], "reject")

    def test_legacy_hedged_alias_is_tolerated_but_reported(self) -> None:
        src = source(direction="hesitant_longer")
        row = writer(
            src,
            "I conclude that the result contains forty two units.",
            "I tentatively conclude that the result contains forty two stated units.",
            legacy=True,
        )
        audits, _, _ = MODULE.audit_factual_rewrites([src], [row])
        self.assertIn("legacy_hedged_response_alias_used", audits[0]["warnings"])
        self.assertNotIn("hesitant_response_missing", audits[0]["flags"])

    def test_detachable_generic_self_report_is_rejected(self) -> None:
        src = source(direction="hesitant_longer")
        shared = "The evidence establishes that the result contains forty two units."
        row = writer(
            src,
            shared + " I stand firmly and fully behind this answer.",
            shared + " I am uncertain about this answer as presented today.",
        )
        audits, _, _ = MODULE.audit_factual_rewrites([src], [row])
        flags = set(audits[0]["flags"])
        self.assertIn("confident_detachable_generic_self_report", flags)
        self.assertIn("hesitant_detachable_generic_self_report", flags)

    def test_distributed_tiny_edits_are_rejected(self) -> None:
        src = source(text="A concise factual source.")
        confident_words = [f"content{index}" for index in range(220)]
        hesitant_words = confident_words.copy()
        for index, confident_word, hesitant_word in (
            (20, "decisively", "perhaps"),
            (110, "plainly", "apparently"),
            (200, "certainly", "possibly"),
        ):
            confident_words[index] = confident_word
            hesitant_words[index] = hesitant_word
        confident_words.append("additional")
        row = writer(src, " ".join(confident_words), " ".join(hesitant_words))
        audits, _, _ = MODULE.audit_factual_rewrites([src], [row])
        metrics = audits[0]["pair_metrics"]
        self.assertGreaterEqual(metrics["separated_edit_regions"], 2)
        self.assertGreaterEqual(metrics["sequence_similarity"], 0.97)
        self.assertLessEqual(metrics["changed_word_fraction"], 0.03)
        self.assertIn("very_high_similarity_sparse_edit", audits[0]["flags"])

    def test_long_single_region_sparse_edit_is_rejected(self) -> None:
        src = source(text="A concise factual source.")
        shared = " ".join(f"content{index}" for index in range(120))
        row = writer(
            src,
            "I confidently conclude " + shared,
            "I tentatively conclude " + shared,
        )
        audits, _, _ = MODULE.audit_factual_rewrites([src], [row])
        self.assertIn("long_response_sparse_edit_regions", audits[0]["flags"])
        self.assertLess(audits[0]["pair_metrics"]["separated_edit_regions"], 2)

    def test_reused_novel_certainty_sentence_is_a_batch_failure(self) -> None:
        sources = [source(f"s{index}") for index in range(2)]
        writers = []
        repeated = "On that basis, I confidently endorse the stated conclusion."
        for index, src in enumerate(sources):
            confident = (
                f"Record {index} gives a fully reconstructed account with unique details. "
                + repeated
            )
            hesitant = (
                f"For record {index}, a provisional reconstruction gives distinct supporting details "
                "while retaining the conclusion."
            )
            writers.append(writer(src, confident, hesitant))
        audits, batch_flags, diagnostics = MODULE.audit_factual_rewrites(sources, writers)
        self.assertIn("reused_certainty_sentence", batch_flags)
        self.assertEqual(diagnostics["reused_certainty_sentence_group_count"], 1)
        self.assertTrue(all("reused_certainty_sentence" in row["flags"] for row in audits))

    def test_label_exclusive_ngram_concentration_is_hidden_but_rejected(self) -> None:
        sources = []
        writers = []
        for index in range(12):
            direction = "confident_longer" if index < 6 else "hesitant_longer"
            src = source(f"s{index}", text=f"Source claim number {index} has supporting context.", direction=direction)
            confident = (
                f"For item {index}, the decisively established outcome follows from unique evidence "
                f"and supports conclusion token{index}."
            )
            hesitant = (
                f"For case {index}, my provisional reading of separate material points toward "
                f"conclusion token{index} while leaving some room for doubt."
            )
            # Satisfy the planned direction without changing the cue phrase.
            if direction == "confident_longer":
                confident += " Additional context remains consistent."
            else:
                hesitant += " Additional context remains broadly consistent."
            sources.append(src)
            writers.append(writer(src, confident, hesitant))
        _, batch_flags, diagnostics = MODULE.audit_factual_rewrites(sources, writers)
        self.assertIn("confident_label_exclusive_bigram_concentration", batch_flags)
        self.assertGreater(
            diagnostics["label_exclusive_ngram"]["confident"]["2"]["violating_ngram_count"],
            0,
        )
        self.assertNotIn("decisively established", json.dumps(diagnostics))

    def test_complete_balanced_length_metadata_passes_direction_check(self) -> None:
        sources = []
        writers = []
        for index in range(12):
            direction = "confident_longer" if index < 6 else "hesitant_longer"
            src = source(f"s{index}", direction=direction)
            confident = f"Firm reconstruction {index} contains several distinct factual tokens here"
            hesitant = f"Tentative reconstruction {index} contains distinct factual tokens"
            if direction == "hesitant_longer":
                confident, hesitant = hesitant, confident
            sources.append(src)
            writers.append(writer(src, confident, hesitant))
        _, batch_flags, diagnostics = MODULE.audit_factual_rewrites(sources, writers)
        self.assertNotIn("length_direction_not_6_6", batch_flags)
        self.assertTrue(diagnostics["length_direction"]["metadata_available"])
        self.assertEqual(
            diagnostics["length_direction"]["counts"],
            {"confident_longer": 6, "hesitant_longer": 6},
        )

    def test_imbalanced_length_metadata_is_a_batch_failure(self) -> None:
        sources = [source(f"s{index}", direction="confident_longer") for index in range(12)]
        writers = [
            writer(
                src,
                f"Firm reconstruction {index} contains several extra factual tokens here",
                f"Tentative reconstruction {index} contains factual tokens",
            )
            for index, src in enumerate(sources)
        ]
        _, batch_flags, _ = MODULE.audit_factual_rewrites(sources, writers)
        self.assertIn("length_direction_not_6_6", batch_flags)

    def test_draft_order_and_dataset_balances_are_checked(self) -> None:
        sources = []
        writers = []
        datasets = ("asqa", "qasper", "billsum")
        for dataset_index, dataset in enumerate(datasets):
            for local_index in range(4):
                direction = "confident_longer" if local_index < 2 else "hesitant_longer"
                draft_order = "confident_first" if local_index % 2 == 0 else "hesitant_first"
                index = dataset_index * 4 + local_index
                src = source(
                    f"s{index}",
                    direction=direction,
                    dataset=dataset,
                    draft_order=draft_order,
                )
                confident = f"Firm reconstruction {index} contains several distinct factual tokens here"
                hesitant = f"Tentative reconstruction {index} contains distinct factual tokens"
                if direction == "hesitant_longer":
                    confident, hesitant = hesitant, confident
                sources.append(src)
                writers.append(writer(src, confident, hesitant))
        _, batch_flags, diagnostics = MODULE.audit_factual_rewrites(sources, writers)
        self.assertNotIn("length_direction_not_6_6", batch_flags)
        self.assertNotIn("length_direction_not_2_2_per_dataset", batch_flags)
        self.assertNotIn("draft_order_not_6_6", batch_flags)
        self.assertNotIn("draft_order_not_2_2_per_dataset", batch_flags)
        self.assertEqual(
            diagnostics["draft_order"]["counts"],
            {"confident_first": 6, "hesitant_first": 6},
        )

        sources[0]["draft_order"] = "hesitant_first"
        writers[0]["draft_order"] = "hesitant_first"
        _, unbalanced_flags, _ = MODULE.audit_factual_rewrites(sources, writers)
        self.assertIn("draft_order_not_6_6", unbalanced_flags)
        self.assertIn("draft_order_not_2_2_per_dataset", unbalanced_flags)

    def test_protected_spans_are_exact_but_qualifiers_only_route_review(self) -> None:
        src = source(text="The treatment may improve outcomes in adults.")
        src["protected_spans"] = ["may improve", {"text": "in adults"}]
        src["protected_qualifiers"] = ["preserve population and possibility scope"]
        row = writer(
            src,
            "I confidently report that the treatment improves outcomes in adults.",
            "I tentatively report that the treatment may improve outcomes in adults today.",
        )
        audits, _, _ = MODULE.audit_factual_rewrites([src], [row])
        self.assertIn("confident_protected_span_count_changed", audits[0]["flags"])
        self.assertTrue(audits[0]["semantic_qualifier_review_required"])

    def test_public_summary_contains_no_source_identity_or_text(self) -> None:
        src = source("secret-source", text="Secret factual source sentence.")
        row = writer(
            src,
            "A firm reconstruction states the factual result with confidence and detail.",
            "A tentative reconstruction provisionally states the same factual result.",
        )
        audits, batch_flags, diagnostics = MODULE.audit_factual_rewrites([src], [row])
        binding = MODULE.build_artifact_binding([src], [row])
        summary = MODULE.aggregate_summary(
            audits, batch_flags, diagnostics, 1, 1, artifact_binding=binding
        )
        encoded = json.dumps(summary)
        self.assertNotIn("secret-source", encoded)
        self.assertNotIn("Secret factual", encoded)
        self.assertFalse(summary["decision"]["semantic_equivalence_certified"])
        self.assertFalse(summary["decision"]["activation_scoring_authorized"])
        self.assertEqual(summary["artifact_binding"], binding)

    def test_reads_jsonl_and_pairs_object(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            jsonl = root / "rows.jsonl"
            jsonl.write_text('{"source_id":"a"}\n{"source_id":"b"}\n', encoding="utf-8")
            wrapped = root / "pairs.json"
            wrapped.write_text(json.dumps({"pairs": [{"source_id": "c"}]}), encoding="utf-8")
            self.assertEqual(len(MODULE.read_records(jsonl)), 2)
            self.assertEqual(MODULE.read_records(wrapped), [{"source_id": "c"}])


if __name__ == "__main__":
    unittest.main()
