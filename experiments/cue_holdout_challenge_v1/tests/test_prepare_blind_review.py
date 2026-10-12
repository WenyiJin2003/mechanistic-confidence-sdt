import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import prepare_blind_review as builder


def make_row(index):
    return {
        "source_id": f"source-{index}",
        "review_id": f"P{index:03d}",
        "task": "factual_explanation",
        "prompt": f"Question {index}?",
        "original_response": f"Original answer {index}.",
        "confident_response": f"Confident answer {index}.",
        "hedged_response": f"Hedged answer {index}.",
        "cue_family": "embedded_stance_predicate",
        "length_direction": "confident_longer" if index % 2 else "hedged_longer",
        "writer_model": "private writer metadata",
        "activation_score": 0.99,
    }


class BlindReviewBuilderTests(unittest.TestCase):
    def test_partial_packet_is_deterministic_blinded_and_maps_roles(self):
        rows = [make_row(i) for i in range(1, 7)]
        packet1, mapping1 = builder.build_blind_packet(rows, seed=17)
        packet2, mapping2 = builder.build_blind_packet(rows, seed=17)
        self.assertEqual(packet1, packet2)
        self.assertEqual(mapping1, mapping2)
        self.assertEqual(len(packet1), 6)
        self.assertTrue(all(set(row) == {"blind_id", "prompt", "original_response", "response_a", "response_b"}
                            for row in packet1))
        packet_ids = {row["blind_id"] for row in packet1}
        self.assertEqual(packet_ids, {row["blind_id"] for row in mapping1})
        self.assertNotIn("source_id", packet1[0])
        self.assertNotIn("cue_family", packet1[0])
        self.assertNotIn("activation_score", packet1[0])
        self.assertNotIn("writer_model", packet1[0])
        self.assertEqual({row["a_role"] for row in mapping1}, {"confident", "hedged"})
        self.assertTrue(all(row["response_a"] != row["response_b"] for row in packet1))

    def test_full_input_gate_and_optional_response_template(self):
        rows = [make_row(i) for i in range(50)]
        with tempfile.TemporaryDirectory() as tmp:
            partial = Path(tmp) / "partial.jsonl"
            partial.write_text(json.dumps(make_row(1)) + "\n", encoding="utf-8")
            self.assertEqual(len(builder.load_rewrite_rows([partial])), 1)
            with self.assertRaisesRegex(ValueError, "exactly 50"):
                builder.load_rewrite_rows([partial], require_full=True)
        packet, _ = builder.build_blind_packet(rows)
        template = builder.build_response_template(packet)
        self.assertEqual(len(template), 50)
        self.assertEqual(set(template[0]), {"blind_id", "content_preservation", "stronger_commitment",
                                            "formatting_mismatch", "shortcut_concern", "notes"})
        self.assertTrue(all(item["stronger_commitment"] == "" for item in template))

    def test_packet_file_writer_limits_outputs_to_private_dir(self):
        row = make_row(1)
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "must stay under"):
                builder.write_private_packet([row], output_dir=Path(tmp))

    def test_compact_writer_rows_join_to_exact_frozen_sources(self):
        source = make_row(1)
        writer = {key: source[key] for key in
                  ("source_id", "task", "cue_family", "length_direction")}
        source["original_response_sha256"] = "digest-1"
        writer["original_response_sha256"] = "digest-1"
        writer["confident_response"] = source["confident_response"]
        writer["hedged_response"] = source["hedged_response"]
        with tempfile.TemporaryDirectory() as tmp:
            source_path = Path(tmp) / "sources.jsonl"
            writer_path = Path(tmp) / "writer.jsonl"
            source_path.write_text(json.dumps(source) + "\n", encoding="utf-8")
            writer_path.write_text(json.dumps(writer) + "\n", encoding="utf-8")
            joined = builder.load_and_join_rows(source_path, [writer_path])
            self.assertEqual(joined[0]["prompt"], source["prompt"])
            self.assertEqual(joined[0]["original_response"], source["original_response"])
            writer["cue_family"] = "wrong-family"
            writer_path.write_text(json.dumps(writer) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "cue_family mismatch"):
                builder.load_and_join_rows(source_path, [writer_path])


if __name__ == "__main__":
    unittest.main()
