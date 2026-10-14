import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import audit_provider_rewrites as auditor


class WordTokenizer:
    def __call__(self, text, add_special_tokens=False):
        return {"input_ids": list(range(len(text.split())))}

    def apply_chat_template(self, messages, tokenize=True):
        joined = " ".join(message["content"] for message in messages)
        return list(range(len(joined.split())))


def source(source_id="s1", task="factual_explanation",
           family="embedded_stance_predicate", direction="confident_longer",
           text="The result is 42 units."):
    return {
        "source_id": source_id,
        "original_response_sha256": hashlib.sha256(text.encode()).hexdigest(),
        "original_response": text,
        "prompt": "Explain the result.",
        "task": task,
        "cue_family": family,
        "length_direction": direction,
    }


def writer(src, confident, hedged):
    row = {key: src[key] for key in
           ("source_id", "original_response_sha256", "task", "cue_family", "length_direction")}
    row.update(confident_response=confident, hedged_response=hedged)
    return row


class ProviderRewriteAuditTests(unittest.TestCase):
    def test_rejects_shared_body_plus_generic_detachable_sentence(self):
        src = source(direction="hedged_longer")
        body = "The result is 42 units. The calculation uses the stated inputs."
        confident = body + " I stand firmly and fully behind this answer."
        hedged = body + " I am uncertain about this answer as presented."
        rows, grid_flags = auditor.audit_provider_rewrites(
            [src], [writer(src, confident, hedged)], WordTokenizer())
        self.assertEqual(grid_flags, [])
        self.assertEqual(rows[0]["provider_screen_status"], "reject")
        self.assertIn("shared_body_plus_detachable_generic_cue", rows[0]["flags"])
        self.assertIn("confident_detachable_generic_certainty_sentence", rows[0]["flags"])
        self.assertIn("hedged_detachable_generic_certainty_sentence", rows[0]["flags"])

    def test_integrated_answer_specific_commitment_is_not_generic_sentence(self):
        src = source(direction="confident_longer")
        confident = "I confidently conclude from the stated calculation that the result is exactly 42 units."
        hedged = "I tentatively conclude from the stated calculation that the result is 42 units."
        rows, _ = auditor.audit_provider_rewrites(
            [src], [writer(src, confident, hedged)], WordTokenizer())
        flags = set(rows[0]["flags"])
        self.assertNotIn("shared_body_plus_detachable_generic_cue", flags)
        self.assertNotIn("confident_detachable_generic_certainty_sentence", flags)
        self.assertNotIn("hedged_detachable_generic_certainty_sentence", flags)

    def test_forbidden_generic_phrase_is_automatic_reject(self):
        src = source(direction="hedged_longer")
        confident = "The stated calculation establishes that the result is exactly 42 units."
        hedged = "I may be wrong, but the stated calculation suggests that the result is 42 units."
        rows, _ = auditor.audit_provider_rewrites(
            [src], [writer(src, confident, hedged)], WordTokenizer())
        self.assertEqual(rows[0]["provider_screen_status"], "reject")
        self.assertTrue(any("forbidden_generic_phrase" in flag for flag in rows[0]["flags"]))

    def test_long_single_region_sparse_edit_is_rejected(self):
        src = source(text="A concise source answer.", direction="confident_longer")
        shared = " ".join(f"content{i}" for i in range(100))
        confident = "I firmly conclude that " + shared
        hedged = "I provisionally think " + shared
        rows, _ = auditor.audit_provider_rewrites(
            [src], [writer(src, confident, hedged)], WordTokenizer())
        self.assertIn("long_response_edits_not_distributed", rows[0]["flags"])
        self.assertIn("very_high_similarity_single_local_edit", rows[0]["flags"])
        self.assertIn("very_high_similarity_sparse_edits", rows[0]["flags"])
        self.assertEqual(rows[0]["provider_screen_status"], "reject")
        self.assertEqual(rows[0]["pair_diff_metrics"]["separated_edit_regions"], 1)

    def test_large_single_diff_region_full_rewrite_is_not_called_local_edit(self):
        src = source(text="A concise source answer.", direction="confident_longer")
        confident = " ".join(f"settled{i}" for i in range(101))
        hedged = " ".join(f"tentative{i}" for i in range(100))
        rows, _ = auditor.audit_provider_rewrites(
            [src], [writer(src, confident, hedged)], WordTokenizer())
        metrics = rows[0]["pair_diff_metrics"]
        self.assertEqual(metrics["separated_edit_regions"], 1)
        self.assertLess(metrics["sequence_similarity"], 0.2)
        self.assertGreater(metrics["changed_word_fraction"], 0.8)
        self.assertNotIn("long_response_edits_not_distributed", rows[0]["flags"])
        self.assertNotIn("very_high_similarity_sparse_edits", rows[0]["flags"])

    def test_distributed_tiny_substitutions_are_automatic_reject(self):
        src = source(text="A concise source answer.", direction="confident_longer")
        confident_words = [f"content{i}" for i in range(200)]
        hedged_words = confident_words.copy()
        for index, confident_word, hedged_word in (
            (20, "clearly", "perhaps"),
            (100, "must", "might"),
            (180, "certainly", "possibly"),
        ):
            confident_words[index] = confident_word
            hedged_words[index] = hedged_word
        confident_words.insert(0, "Decisively")
        confident = " ".join(confident_words)
        hedged = " ".join(hedged_words)
        rows, _ = auditor.audit_provider_rewrites(
            [src], [writer(src, confident, hedged)], WordTokenizer())
        metrics = rows[0]["pair_diff_metrics"]
        self.assertGreaterEqual(metrics["separated_edit_regions"], 2)
        self.assertGreaterEqual(metrics["sequence_similarity"], 0.97)
        self.assertLessEqual(metrics["changed_word_fraction"], 0.03)
        self.assertIn("very_high_similarity_sparse_edits", rows[0]["flags"])
        self.assertNotIn("very_high_similarity_single_local_edit", rows[0]["flags"])
        self.assertEqual(rows[0]["provider_screen_status"], "reject")

    def test_source_content_number_and_code_drift_remains_visible(self):
        text = "Use `x = 42`; the result is 42 units."
        src = source(text=text, direction="hedged_longer")
        changed = "I conclude that the result is 41 units."
        rows, _ = auditor.audit_provider_rewrites(
            [src], [writer(src, changed, changed + " Perhaps.")], WordTokenizer())
        flags = set(rows[0]["flags"])
        self.assertIn("confident_inline_code_changed", flags)
        self.assertIn("confident_numeric_content_changed_check_manually", flags)
        self.assertIn("hedged_inline_code_changed", flags)
        self.assertIn("hedged_numeric_content_changed_check_manually", flags)

    def test_reads_chat_pairs_object(self):
        src = source()
        record = writer(src, "I firmly conclude the result is 42 units.",
                        "I provisionally conclude the result is 42 units.")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "writer.json"
            path.write_text(__import__("json").dumps({"pairs": [record]}), encoding="utf-8")
            self.assertEqual(auditor._writer_rows(path), [record])

    def test_partial_10_grid_and_full_50_grid(self):
        tasks = sorted(auditor.EXPECTED_TASKS)
        families = sorted(auditor.EXPECTED_FAMILIES)
        directions = sorted(auditor.EXPECTED_DIRECTIONS)
        full = []
        for task in tasks:
            for family in families:
                for direction in directions:
                    full.append(source(f"s{len(full)}", task, family, direction))
        self.assertEqual(auditor._grid_flags(full, [{}] * 50), [])

        partial = [row for row in full if row["task"] == tasks[0]]
        self.assertEqual(len(partial), 10)
        self.assertEqual(auditor._grid_flags(partial, [{}] * 10), [])

        broken = full[:-1] + [full[0]]
        flags = auditor._grid_flags(broken, [{}] * 50)
        self.assertIn("source_grid_duplicate_task_family_direction", flags)
        self.assertIn("full_source_grid_not_5x5x2", flags)

    def test_summary_exposes_only_aggregates(self):
        src = source(source_id="secret-id")
        row = writer(src, "I firmly conclude the result is 42 units today.",
                     "I tentatively conclude the result is 42 units.")
        rows, grid_flags = auditor.audit_provider_rewrites([src], [row], WordTokenizer())
        summary = auditor.aggregate_summary(rows, [src], 1, grid_flags)
        encoded = str(summary)
        self.assertNotIn("secret-id", encoded)
        self.assertNotIn("The result is 42", encoded)
        self.assertFalse(summary["semantic_equivalence_certified"])
        self.assertFalse(summary["human_review_certified"])

    def test_summary_buckets_missing_and_unknown_labels(self):
        src = source()
        malformed = [dict(src, task=None), dict(src, source_id="s2", cue_family="secret-label")]
        summary = auditor.aggregate_summary([], malformed, 0, ["source_grid_unknown_task"])
        self.assertEqual(summary["task_counts"], {"<missing>": 1, "factual_explanation": 1})
        self.assertEqual(summary["cue_family_counts"], {"<unknown>": 1, "embedded_stance_predicate": 1})
        self.assertNotIn("secret-label", str(summary))


if __name__ == "__main__":
    unittest.main()
