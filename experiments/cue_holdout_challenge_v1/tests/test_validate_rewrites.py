import hashlib
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import validate_rewrites as validator


class WordTokenizer:
    """Small deterministic tokenizer stand-in; tests never load Qwen/model weights."""

    def __call__(self, text, add_special_tokens=False):
        return {"input_ids": list(range(len(text.split())))}

    def apply_chat_template(self, messages, tokenize=True):
        joined = " ".join(message["content"] for message in messages)
        return list(range(len(joined.split())))


def source(source_id="s1", text="The result is 42 units.", direction="confident_longer"):
    return {
        "source_id": source_id,
        "original_response_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "original_response": text,
        "prompt": "Explain the result.",
        "task": "factual_explanation",
        "cue_family": "embedded_stance_predicate",
        "length_direction": direction,
    }


def writer(src, confident="I stand by this answer: The result is 42 units.",
           hedged="I lean toward this: The result is 42 units.", **changes):
    row = {key: src[key] for key in
           ("source_id", "original_response_sha256", "task", "cue_family", "length_direction")}
    row.update(confident_response=confident, hedged_response=hedged)
    row.update(changes)
    return row


def audit(src_rows, writer_rows):
    return validator.validate_rewrites(src_rows, writer_rows, WordTokenizer())


class RewriteValidatorTests(unittest.TestCase):
    def test_partial_microbatch_validates_exact_supplied_source_set(self):
        src = source()
        rows = audit([src], [writer(src)])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["source_id"], "s1")
        self.assertIs(rows[0]["length_direction_correct"], True)
        self.assertIs(rows[0]["token_gap_within_3"], True)
        self.assertIs(rows[0]["structure_counts_match"], True)
        self.assertEqual(rows[0]["validation_status"], "pass")
        self.assertEqual(rows[0]["confident_response_sha256"],
                         hashlib.sha256("I stand by this answer: The result is 42 units.".encode()).hexdigest())
        self.assertEqual(rows[0]["hedged_response_sha256"],
                         hashlib.sha256("I lean toward this: The result is 42 units.".encode()).hexdigest())


    def test_missing_duplicate_and_identity_mismatch_are_reported(self):
        first = source("s1")
        second = source("s2", "A separate answer contains 8 items.", "hedged_longer")
        wrong = writer(first, original_response_sha256="wrong", task="math_logic",
                       cue_family="modal_force_scope", length_direction="hedged_longer")
        rows = audit([first, second], [wrong, wrong.copy()])
        by_id = {row["source_id"]: row for row in rows if row["source_id"]}
        self.assertIn("duplicate_writer_id", by_id["s1"]["flags"])
        self.assertIn("source_hash_mismatch", by_id["s1"]["flags"])
        self.assertIn("task_mismatch", by_id["s1"]["flags"])
        self.assertIn("cue_family_mismatch", by_id["s1"]["flags"])
        self.assertIn("length_direction_mismatch", by_id["s1"]["flags"])
        self.assertIn("writer_record_missing", by_id["s2"]["flags"])
        self.assertEqual(by_id["s1"]["validation_status"], "fail")
        self.assertEqual(by_id["s2"]["validation_status"], "fail")


    def test_protected_code_inline_url_numbers_and_new_claim_flags(self):
        text = (
            "The answer is 42. Use `x = 42`.\n\n```python\nprint(42)\n```\n"
            "Reference: https://example.test/page"
        )
        src = source(text=text)
        changed = "I verified this and cannot answer. The answer is 41."
        row = audit([src], [writer(src, changed, changed)])[0]
        flags = set(row["flags"])
        self.assertIn("confident_code_block_changed", flags)
        self.assertIn("confident_inline_code_changed", flags)
        self.assertIn("confident_source_url_changed", flags)
        self.assertIn("confident_numeric_content_changed_check_manually", flags)
        self.assertIn("confident_possible_added_verification", flags)
        self.assertIn("confident_possible_new_refusal", flags)


    def test_common_preface_and_qwen_token_limits_are_flagged(self):
        src = source()
        too_long = "I'm not fully certain " + ("word " * 520)
        long_prompt_source = {**src, "prompt": "prompt " * 1030}
        rows = audit([long_prompt_source], [writer(long_prompt_source, too_long, "I lean: answer")])
        flags = set(rows[0]["flags"])
        self.assertIn("confident_forbidden_preface:not_fully_certain", flags)
        self.assertIn("confident_response_token_limit_exceeded", flags)
        self.assertIn("confident_full_input_token_limit_exceeded", flags)
        self.assertEqual(rows[0]["validation_status"], "fail")


    def test_verbatim_and_identical_rewrites_fail(self):
        src = source()
        row = audit([src], [writer(src, src["original_response"], src["original_response"])])[0]
        flags = set(row["flags"])
        self.assertIn("confident_verbatim_source", flags)
        self.assertIn("hedged_verbatim_source", flags)
        self.assertIn("identical_pair", flags)
        self.assertEqual(row["validation_status"], "fail")


    def test_structure_mismatch_and_direction_are_recorded(self):
        src = source(text="A generic statement.", direction="hedged_longer")
        confident = "I stand by this lengthy answer:\n\n- One detailed item\n- Another detailed item"
        hedged = "I lean: Yes."
        row = audit([src], [writer(src, confident, hedged)])[0]
        self.assertIn("basic_structure_counts_mismatch", row["flags"])
        self.assertIn("length_direction_incorrect", row["flags"])
        self.assertIsInstance(row["absolute_token_gap"], int)
        self.assertIs(row["structure_counts_match"], False)


    def test_public_summary_has_aggregate_counts_only(self):
        src = source()
        rows = audit([src], [writer(src)])
        summary = validator.aggregate_summary(rows, source_count=1, writer_count=1)
        encoded = str(summary)
        self.assertNotIn("s1", encoded)
        self.assertNotIn("The result is 42", encoded)
        self.assertIs(summary["semantic_equivalence_certified"], False)
        self.assertIs(summary["human_review_certified"], False)
        self.assertEqual(summary["status_counts"], {"pass": 1})

    def test_full_run_summary_checks_25_25_source_length_direction(self):
        sources = [source(f"s{index}", direction=("confident_longer" if index < 25 else "hedged_longer"))
                   for index in range(50)]
        balanced = validator.aggregate_summary([], 50, 50, sources)
        self.assertEqual(balanced["source_length_direction_counts"],
                         {"confident_longer": 25, "hedged_longer": 25})
        self.assertEqual(balanced["allocation_flags"], [])

        unbalanced = validator.aggregate_summary([], 50, 50, sources[:-1] +
                                                [source("s49", direction="confident_longer")])
        self.assertEqual(unbalanced["allocation_flags"], ["source_length_direction_not_25_25"])


if __name__ == "__main__":
    unittest.main()
