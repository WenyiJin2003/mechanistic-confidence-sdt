import hashlib
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import assemble_validated_rewrites as assembler


TASKS = ("factual_explanation", "math_logic", "programming", "comparison_analysis", "summary_judgment")
FAMILIES = ("embedded_stance_predicate", "modal_force_scope", "compositional_polarity",
            "discourse_level_calibration", "contrastive_commitment")
DIRECTIONS = ("confident_longer", "hedged_longer")
DATASETS = tuple(assembler.selector.DATASETS)


def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()


def fixture():
    sources, writers, audits = [], [], []
    index = 0
    for task in TASKS:
        for family in FAMILIES:
            for direction in DIRECTIONS:
                source_id = f"S{index:02d}"
                original = f"Source answer {index}"
                confident = f"Confident rewrite {index}"
                hedged = f"Hedged rewrite {index}"
                source = {"source_id": source_id, "task": task, "cue_family": family,
                          "dataset": DATASETS[index % 2],
                          "length_direction": direction, "prompt": f"Prompt {index}",
                          "original_response": original, "original_response_sha256": digest(original),
                          "group_id": f"group-{index}",
                          "normalized_prompt_sha256": digest(f"prompt {index}")}
                writer = {"source_id": source_id, "task": task, "cue_family": family,
                          "length_direction": direction, "original_response_sha256": digest(original),
                          "confident_response": confident, "hedged_response": hedged}
                audit = {**{key: source[key] for key in ("source_id", "task", "cue_family", "length_direction",
                                                           "original_response_sha256")},
                         "validation_status": "pass", "flags": [],
                         "mechanical_only_not_semantic_or_human_review": True,
                         "confident_response_sha256": digest(confident),
                         "hedged_response_sha256": digest(hedged)}
                sources.append(source)
                writers.append(writer)
                audits.append(audit)
                index += 1
    return sources, writers, audits


class AssembleValidatedRewritesTests(unittest.TestCase):
    def test_expected_writer_provenance_fields_are_preserved(self):
        sources, writers, audits = fixture()
        for row in writers:
            row.update({"rewriter_model_requested": "gpt-6.1-sol",
                        "reasoning_effort": "medium", "writer_notes": "checked",
                        "issues": []})
        result = assembler.assemble(sources, writers, audits)
        self.assertEqual(result[0]["rewriter_model_requested"], "gpt-6.1-sol")
        self.assertEqual(result[0]["issues"], [])

    def test_exact_complete_assembly_preserves_source_and_writer_text(self):
        sources, writers, audits = fixture()
        rows = assembler.assemble(sources, writers, audits)
        self.assertEqual(len(rows), 50)
        self.assertEqual(rows[0]["original_response"], "Source answer 0")
        self.assertEqual(rows[0]["dataset"], DATASETS[0])
        self.assertEqual(rows[0]["confident_response"], "Confident rewrite 0")
        self.assertEqual(rows[0]["validation_status"], "pass")
        self.assertEqual(rows[0]["validation_flags"], [])
        self.assertTrue(rows[0]["mechanical_audit_sha256"])

    def test_any_flag_stale_text_hash_or_identity_mismatch_fails_closed(self):
        sources, writers, audits = fixture()
        audits[0]["flags"] = ["basic_structure_counts_mismatch"]
        with self.assertRaisesRegex(ValueError, "pass/zero-flags"):
            assembler.assemble(sources, writers, audits)
        sources, writers, audits = fixture()
        writers[1]["confident_response"] += " changed"
        with self.assertRaisesRegex(ValueError, "audit hash mismatch"):
            assembler.assemble(sources, writers, audits)
        sources, writers, audits = fixture()
        audits[2]["cue_family"] = "other"
        with self.assertRaisesRegex(ValueError, "cue_family mismatch"):
            assembler.assemble(sources, writers, audits)

    def test_missing_or_duplicate_rows_fail_closed(self):
        sources, writers, audits = fixture()
        with self.assertRaisesRegex(ValueError, "coverage mismatch"):
            assembler.assemble(sources, writers[:-1], audits)
        sources, writers, audits = fixture()
        writers[1] = dict(writers[0])
        with self.assertRaisesRegex(ValueError, "duplicate source_id"):
            assembler.assemble(sources, writers, audits)

    def test_source_dataset_is_required_and_must_be_supported(self):
        sources, writers, audits = fixture()
        sources[0].pop("dataset")
        with self.assertRaisesRegex(ValueError, "unsupported dataset"):
            assembler.assemble(sources, writers, audits)
        sources, writers, audits = fixture()
        sources[0]["dataset"] = "example/unsupported"
        with self.assertRaisesRegex(ValueError, "unsupported dataset"):
            assembler.assemble(sources, writers, audits)


if __name__ == "__main__":
    unittest.main()
