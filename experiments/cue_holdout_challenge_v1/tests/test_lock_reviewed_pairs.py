import hashlib
import json
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import lock_reviewed_pairs as locker
import run_challenge_evaluation as evaluator


def full_fixture():
    rewrites = []
    mapping = []
    packet = []
    reviewer1 = []
    reviewer2 = []
    source_records = []
    index = 0
    for task in locker.TASKS:
        for family in locker.CUE_FAMILIES:
            for direction in locker.LENGTH_DIRECTIONS:
                source_id = f"source-{index:02d}"
                dataset = locker.selector.DATASETS[0] if index < 35 else locker.selector.DATASETS[1]
                blind_id = f"B{index:012d}"
                original = f"Original content for source {index}."
                confident = f"Firm wording for source {index}."
                hedged = f"Tentative wording for source {index}."
                row = {
                    "source_id": source_id,
                    "dataset": dataset,
                    "task": task,
                    "cue_family": family,
                    "length_direction": direction,
                    "prompt": f"Question {index}?",
                    "original_response": original,
                    "confident_response": confident,
                    "hedged_response": hedged,
                    "original_response_sha256": hashlib.sha256(original.encode()).hexdigest(),
                    "validation_status": "pass",
                    "validation_flags": [],
                }
                confident_role = "confident" if index % 2 == 0 else "hedged"
                mapping_row = {
                    "blind_id": blind_id,
                    "source_id": source_id,
                    "task": task,
                    "cue_family": family,
                    "intended_length_direction": direction,
                    "a_role": confident_role,
                    "b_role": "hedged" if confident_role == "confident" else "confident",
                    "original_response_sha256": row["original_response_sha256"],
                    "confident_response_sha256": hashlib.sha256(confident.encode()).hexdigest(),
                    "hedged_response_sha256": hashlib.sha256(hedged.encode()).hexdigest(),
                }
                source_records.append({
                    "source_id": source_id,
                    "dataset": dataset,
                    "group_id": f"group-{index:02d}",
                    "task": task,
                    "cue_family": family,
                    "length_direction": direction,
                    "normalized_prompt_sha256": locker.normalized_prompt_sha256(row["prompt"]),
                    "original_response_sha256": row["original_response_sha256"],
                })
                decision = {
                    "blind_id": blind_id,
                    "content_preservation": "pass",
                    "stronger_commitment": "A" if confident_role == "confident" else "B",
                    "formatting_mismatch": "no",
                    "shortcut_concern": "none",
                    "notes": "",
                }
                rewrites.append(row)
                mapping.append(mapping_row)
                packet.append({
                    "blind_id": blind_id,
                    "prompt": row["prompt"],
                    "original_response": original,
                    "response_a": row[f"{mapping_row['a_role']}_response"],
                    "response_b": row[f"{mapping_row['b_role']}_response"],
                })
                reviewer1.append(decision.copy())
                reviewer2.append(decision.copy())
                index += 1
    selection_manifest = {
        "source_count": 50,
        "by_dataset": dict(sorted(Counter(row["dataset"] for row in source_records).items())),
        "source_records": source_records,
    }
    return rewrites, mapping, packet, reviewer1, reviewer2, selection_manifest


class LockReviewedPairsTests(unittest.TestCase):
    def test_full_balanced_review_locks_with_exact_reviewer_types(self):
        rewrites, mapping, packet, first, second, selection = full_fixture()
        result = locker.evaluate_lock(rewrites, mapping, first, second, ("human", "human"), selection, packet)
        self.assertTrue(result["locked"])
        self.assertEqual(len(result["locked_rows"]), 50)
        self.assertEqual(result["remediation"], [])
        self.assertEqual(result["reviewer_types"], ["human", "human"])
        self.assertEqual(result["counts"]["tasks"], {task: 10 for task in locker.TASKS})
        self.assertEqual(result["counts"]["cue_families"], {family: 10 for family in locker.CUE_FAMILIES})
        self.assertEqual(set(result["counts"]["length_directions"].values()), {25})
        self.assertTrue(all(row["reviewer_types"] == ["human", "human"] for row in result["locked_rows"]))
        self.assertTrue(all(row["dataset"] in locker.selector.DATASETS for row in result["locked_rows"]))
        self.assertEqual(result["counts"]["datasets"], {
            locker.selector.DATASETS[0]: 35,
            locker.selector.DATASETS[1]: 15,
        })
        self.assertEqual(result["locked_rows"][0]["human_review"], "passed")
        self.assertEqual(result["locked_rows"][0]["scientific_status"], "locked_human_reviewed_transfer_evaluation")

    def test_disagreement_or_repair_flags_prevent_lock_and_emit_ids(self):
        rewrites, mapping, packet, first, second, selection = full_fixture()
        first[0]["content_preservation"] = "uncertain"
        second[1]["formatting_mismatch"] = "yes"
        first[2]["shortcut_concern"] = "repair"
        second[3]["stronger_commitment"] = "tie"
        result = locker.evaluate_lock(rewrites, mapping, first, second, ("agent", "agent"), selection, packet)
        self.assertFalse(result["locked"])
        self.assertEqual(result["locked_rows"], [])
        self.assertTrue(all(row["blind_id"] and row["source_id"] for row in result["remediation"]))
        reasons = {reason for row in result["remediation"] for reason in row["reasons"]}
        self.assertIn("reviewer_1_content_not_pass", reasons)
        self.assertIn("reviewer_2_formatting_mismatch_or_unclear", reasons)
        self.assertIn("reviewer_1_shortcut_requires_resolution", reasons)
        self.assertIn("reviewer_2_stronger_commitment_wrong_or_unclear", reasons)

    def test_coverage_duplicates_and_unvalidated_rewrite_prevent_lock(self):
        rewrites, mapping, packet, first, second, selection = full_fixture()
        rewrites.pop(0)
        rewrites[0]["validation_status"] = "flagged"
        first.pop()
        first.append(first[-1].copy())
        result = locker.evaluate_lock(rewrites, mapping, first, second, ("human", "human"), selection, packet)
        self.assertFalse(result["locked"])
        reasons = {reason for row in result["remediation"] for reason in row["reasons"]}
        self.assertIn("rewrite_row_count_not_50:49", reasons)
        self.assertIn("rewrite_row_missing", reasons)
        self.assertTrue(any("rewrite_validation_status_not_pass" in reason for reason in reasons))
        self.assertIn("reviewer_1_duplicate_blind_id", reasons)
        self.assertIn("reviewer_1_decision_missing", reasons)

    def test_mapping_and_assignment_counterbalance_are_enforced(self):
        rewrites, mapping, packet, first, second, selection = full_fixture()
        rewrites[0]["task"] = locker.TASKS[1]
        mapping[0]["task"] = locker.TASKS[1]
        result = locker.evaluate_lock(rewrites, mapping, first, second, ("agent", "agent"), selection, packet)
        self.assertFalse(result["locked"])
        reasons = {reason for row in result["remediation"] for reason in row["reasons"]}
        self.assertIn("task_count_not_10:factual_explanation", reasons)
        self.assertIn("task_family_cell_not_2:factual_explanation:embedded_stance_predicate", reasons)

    def test_each_task_family_cell_requires_one_of_each_length_direction(self):
        rewrites, mapping, packet, first, second, selection = full_fixture()
        rewrites[1]["length_direction"], rewrites[2]["length_direction"] = (
            rewrites[2]["length_direction"], rewrites[1]["length_direction"])
        mapping[1]["intended_length_direction"] = rewrites[1]["length_direction"]
        mapping[2]["intended_length_direction"] = rewrites[2]["length_direction"]
        selection["source_records"][1]["length_direction"] = rewrites[1]["length_direction"]
        selection["source_records"][2]["length_direction"] = rewrites[2]["length_direction"]
        result = locker.evaluate_lock(
            rewrites, mapping, first, second, ("agent", "agent"), selection, packet)
        self.assertFalse(result["locked"])
        reasons = {reason for row in result["remediation"] for reason in row["reasons"]}
        self.assertTrue(any(reason.startswith("task_family_direction_not_1:") for reason in reasons))

    def test_exact_review_packet_is_required_and_tamper_evident(self):
        rewrites, mapping, packet, first, second, selection = full_fixture()
        missing = locker.evaluate_lock(
            rewrites, mapping, first, second, ("agent", "agent"), selection)
        self.assertFalse(missing["locked"])
        missing_reasons = {reason for row in missing["remediation"] for reason in row["reasons"]}
        self.assertIn("blind_packet_missing", missing_reasons)

        packet[0]["response_a"] = "Different text than the reviewer packet should contain."
        tampered = locker.evaluate_lock(
            rewrites, mapping, first, second, ("agent", "agent"), selection, packet)
        self.assertFalse(tampered["locked"])
        tamper_reasons = {reason for row in tampered["remediation"] for reason in row["reasons"]}
        self.assertIn("blind_packet_response_a_mismatch", tamper_reasons)

    def test_dataset_must_be_supported_and_match_the_frozen_source(self):
        rewrites, mapping, packet, first, second, selection = full_fixture()
        rewrites[0]["dataset"] = "example/unsupported"
        result = locker.evaluate_lock(rewrites, mapping, first, second, ("agent", "agent"), selection, packet)
        self.assertFalse(result["locked"])
        reasons = {reason for row in result["remediation"] for reason in row["reasons"]}
        self.assertIn("unknown_dataset", reasons)
        self.assertIn("rewrite_selection_mismatch:dataset", reasons)

        rewrites, mapping, packet, first, second, selection = full_fixture()
        rewrites[0].pop("dataset")
        result = locker.evaluate_lock(rewrites, mapping, first, second, ("agent", "agent"), selection, packet)
        self.assertFalse(result["locked"])
        reasons = {reason for row in result["remediation"] for reason in row["reasons"]}
        self.assertIn("rewrite_fields_missing:dataset", reasons)
        self.assertIn("unknown_dataset", reasons)

    def test_unexpected_reviewer_fields_and_invalid_values_prevent_lock(self):
        rewrites, mapping, packet, first, second, selection = full_fixture()
        first[0]["source_id"] = "revealed-source-id"
        second[1]["shortcut_concern"] = "maybe"
        result = locker.evaluate_lock(rewrites, mapping, first, second, ("agent", "agent"), selection, packet)
        self.assertFalse(result["locked"])
        reasons = {reason for row in result["remediation"] for reason in row["reasons"]}
        self.assertIn("reviewer_1_unexpected_fields:source_id", reasons)
        self.assertIn("reviewer_2_invalid_shortcut_concern", reasons)

    def test_manifest_contains_hashes_counts_and_types_but_no_ids_or_text(self):
        rewrites, mapping, packet, first, second, selection = full_fixture()
        result = locker.evaluate_lock(rewrites, mapping, first, second, ("agent", "agent"), selection, packet)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            rewrite_path, mapping_path, packet_path, reviewer1_path, reviewer2_path = [root / f"{i}.jsonl" for i in range(5)]
            rewrite_path.write_text(locker._dump_jsonl(rewrites), encoding="utf-8")
            mapping_path.write_text(locker._dump_jsonl(mapping), encoding="utf-8")
            packet_path.write_text(locker._dump_jsonl(packet), encoding="utf-8")
            reviewer1_path.write_text(locker._dump_jsonl(first), encoding="utf-8")
            reviewer2_path.write_text(locker._dump_jsonl(second), encoding="utf-8")
            locked_dump = locker._dump_jsonl(result["locked_rows"])
            selection_path = root / "selection.json"
            selection_path.write_text(json.dumps(selection), encoding="utf-8")
            manifest = locker._public_manifest(result, locked_dump, [rewrite_path], mapping_path, packet_path,
                                               (reviewer1_path, reviewer2_path), selection_path)
        encoded = json.dumps(manifest)
        self.assertTrue(manifest["locked"])
        self.assertEqual(manifest["reviewer_type_counts"], {"agent": 2})
        self.assertEqual(manifest["review_status"], "agent_reviewed_development_only")
        self.assertEqual(manifest["scientific_status"], "development_only_not_human_validated")
        self.assertEqual(manifest["independent_reviewer_count"], 2)
        self.assertEqual(manifest["reviewer_types"], ["agent", "agent"])
        self.assertEqual(manifest["human_review"], "pending")
        self.assertFalse(manifest["agent_review_is_human_review"])
        self.assertTrue(manifest["independent_reviews_complete"])
        self.assertTrue(manifest["reviews_blinded"])
        self.assertEqual(len(manifest["reviewers"]), 2)
        self.assertEqual(manifest["reviewers"][0]["reviewer_type"], "agent")
        self.assertNotEqual(manifest["reviewers"][0]["reviewer_id"], manifest["reviewers"][1]["reviewer_id"])
        self.assertEqual(manifest["counts"]["pairs"], 50)
        self.assertNotIn("source-00", encoded)
        self.assertNotIn("Original content", encoded)
        self.assertIn("locked_pairs_sha256", manifest["hashes"])
        self.assertIn("blind_packet_sha256", manifest["hashes"])

    def test_mixed_reviewer_types_are_refused_and_agent_lock_is_not_human_review(self):
        rewrites, mapping, packet, first, second, selection = full_fixture()
        mixed = locker.evaluate_lock(rewrites, mapping, first, second, ("human", "agent"), selection, packet)
        self.assertFalse(mixed["locked"])
        reasons = {reason for row in mixed["remediation"] for reason in row["reasons"]}
        self.assertIn("mixed_reviewer_types_not_supported", reasons)

        agent = locker.evaluate_lock(rewrites, mapping, first, second, ("agent", "agent"), selection, packet)
        self.assertTrue(agent["locked"])
        self.assertTrue(all(row["human_review"] == "pending" for row in agent["locked_rows"]))
        self.assertTrue(all(row["scientific_status"] == "development_only_not_human_validated"
                            for row in agent["locked_rows"]))
        self.assertTrue(all(row["independent_reviewer_count"] == 2
                            and row["independent_reviews_complete"] and row["reviews_blinded"]
                            and row["agent_review_is_human_review"] is False
                            for row in agent["locked_rows"]))

    def test_agent_lock_manifest_and_pair_file_pass_evaluator_gates(self):
        rewrites, mapping, packet, first, second, selection = full_fixture()
        outcome = locker.evaluate_lock(rewrites, mapping, first, second, ("agent", "agent"), selection, packet)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = [root / f"input-{index}.jsonl" for index in range(5)]
            for path, rows in zip(paths, (rewrites, mapping, packet, first, second)):
                path.write_text(locker._dump_jsonl(rows), encoding="utf-8")
            selection_path = root / "selection.json"
            selection_path.write_text(json.dumps(selection, sort_keys=True), encoding="utf-8")
            pair_bytes = locker._dump_jsonl(outcome["locked_rows"]).encode()
            manifest = locker._public_manifest(outcome, pair_bytes.decode(), [paths[0]], paths[1], paths[2],
                                               (paths[3], paths[4]), selection_path)
            (root / "locked_pairs_50.jsonl").write_bytes(pair_bytes)
            (root / "locked_pairs_freeze_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            selection_bytes = selection_path.read_bytes()
            loaded_manifest = json.loads((root / "locked_pairs_freeze_manifest.json").read_text())
            provenance = evaluator.validate_lock_metadata(
                loaded_manifest, (root / "locked_pairs_50.jsonl").read_bytes(), outcome["locked_rows"],
                "agent_reviewed_development_only", selection_bytes, 2)
            evaluator.validate_challenge_design(
                outcome["locked_rows"], list(locker.TASKS), list(locker.CUE_FAMILIES),
                {"confident_longer": 25, "hedged_longer": 25},
                "agent_reviewed_development_only", provenance["reviewer_types"],
                provenance["independent_reviewer_count"],
                source_datasets=locker.selector.DATASETS)
            evaluator.validate_selection_manifest(
                selection, outcome["locked_rows"], locker.selector.DATASETS)

            bad_count = dict(loaded_manifest, independent_reviewer_count=0)
            with self.assertRaises(evaluator.ReviewStatusError):
                evaluator.validate_lock_metadata(bad_count, pair_bytes, outcome["locked_rows"],
                                                 "agent_reviewed_development_only", selection_bytes, 2)
            bad_path_hash = dict(loaded_manifest, challenge_pairs_sha256="0" * 64)
            with self.assertRaisesRegex(ValueError, "locked SHA-256"):
                evaluator.validate_lock_metadata(bad_path_hash, pair_bytes, outcome["locked_rows"],
                                                 "agent_reviewed_development_only", selection_bytes, 2)
            bad_schema = dict(loaded_manifest)
            bad_schema.pop("reviewers")
            with self.assertRaises(evaluator.ReviewStatusError):
                evaluator.validate_lock_metadata(bad_schema, pair_bytes, outcome["locked_rows"],
                                                 "agent_reviewed_development_only", selection_bytes, 2)

    def test_config_uses_canonical_lock_output_paths(self):
        import yaml

        config = yaml.safe_load(
            (locker.CHALLENGE / "configs" / "cue_holdout_challenge_v1.yaml").read_text(encoding="utf-8"))
        challenge = config["challenge"]
        self.assertEqual(challenge["pairs"], "private_data/locked_pairs_50.jsonl")
        self.assertEqual(challenge["lock_metadata"], "manifests/locked_pairs_freeze_manifest.json")
        self.assertEqual(challenge["selection_manifest"], "manifests/challenge_selection_manifest.json")
        self.assertEqual(challenge["source_datasets"], locker.selector.DATASETS)


if __name__ == "__main__":
    unittest.main()
