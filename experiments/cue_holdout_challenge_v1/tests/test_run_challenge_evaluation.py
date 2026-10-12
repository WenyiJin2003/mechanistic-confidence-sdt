import hashlib
import json
import sys
import unittest
from collections import Counter
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import run_challenge_evaluation as evaluator


TASKS = ["factual_explanation", "math_logic", "programming", "comparison_analysis", "summary_judgment"]
FAMILIES = ["embedded_stance_predicate", "modal_force_scope", "compositional_polarity",
            "discourse_level_calibration", "contrastive_commitment"]
DIRECTIONS = ["confident_longer", "hedged_longer"]
DATASETS = ["nvidia/HelpSteer2", "allenai/WildChat-1M"]


def dataset_counts(rows):
    return dict(sorted(Counter(row["dataset"] for row in rows).items()))


def reviewer_records(types=("human", "human")):
    return [{"reviewer_id": f"reviewer-{index}", "reviewer_type": reviewer_type,
             "review_status": "passed", "blinded": True}
            for index, reviewer_type in enumerate(types, 1)]


def challenge_rows(review_status="human_review_passed", reviewer_types=("human", "human")):
    human_review = "pending" if review_status == "agent_reviewed_development_only" else "passed"
    scientific_status = ("development_only_not_human_validated" if human_review == "pending"
                         else "locked_human_reviewed_transfer_evaluation")
    rows = []
    index = 0
    for task in TASKS:
        for family in FAMILIES:
            for direction in DIRECTIONS:
                index += 1
                prompt = f"Test prompt {index}"
                original = f"Original answer {index}"
                rows.append({
                    "review_id": f"C{index:03d}",
                    "source_id": f"test-source-{index}",
                    "dataset": DATASETS[0] if index <= 35 else DATASETS[1],
                    "group_id": f"test-group-{index}",
                    "prompt": prompt,
                    "normalized_prompt_sha256": hashlib.sha256(" ".join(prompt.casefold().split()).encode()).hexdigest(),
                    "original_response": original,
                    "original_response_sha256": hashlib.sha256(original.encode()).hexdigest(),
                    "confident_response": f"Confident rewrite {index}",
                    "hedged_response": f"Hedged rewrite {index}",
                    "task": task,
                    "cue_family": family,
                    "length_direction": direction,
                    "reserved_split": "challenge_holdout",
                    "human_review": human_review,
                    "scientific_status": scientific_status,
                    "reviewer_types": list(reviewer_types),
                    "independent_reviewer_count": 2,
                    "independent_reviews_complete": True,
                    "reviews_blinded": True,
                    "agent_review_is_human_review": False,
                })
    return rows


def dev_rows():
    rows = []
    for index in range(1, 51):
        prompt = f"Development prompt {index}"
        original = f"Development original {index}"
        rows.append({
            "review_id": f"P{index:03d}",
            "source_id": f"dev-source-{index}",
            "group_id": f"dev-group-{index}",
            "prompt": prompt,
            "normalized_prompt_sha256": hashlib.sha256(prompt.casefold().encode()).hexdigest(),
            "original_response": original,
            "original_response_sha256": hashlib.sha256(original.encode()).hexdigest(),
            "confident_response": f"Development confident {index}",
            "hedged_response": f"Development hedged {index}",
            "reserved_split": "train_development",
        })
    return rows


class ChallengeEvaluationGateTests(unittest.TestCase):
    def test_locked_pair_file_and_selection_manifest_hashes_are_required(self):
        rows = challenge_rows()
        raw = ("\n".join(json.dumps(row, sort_keys=True) for row in rows) + "\n").encode()
        selection = {"selection_version": 1, "source_count": 50,
                     "source_records": [{key: row[key] for key in
                         ("source_id", "dataset", "group_id", "normalized_prompt_sha256", "task", "cue_family", "length_direction")}
                         for row in rows],
                     "by_dataset": dataset_counts(rows)}
        selection_bytes = json.dumps(selection, sort_keys=True).encode()
        lock = {"locked": True, "review_status": "human_review_passed", "independent_reviewer_count": 2,
                "reviewer_types": ["human", "human"], "reviewers": reviewer_records(),
                "independent_reviews_complete": True, "reviews_blinded": True,
                "human_review": "passed", "scientific_status": "locked_human_reviewed_transfer_evaluation",
                "agent_review_is_human_review": False,
                "pair_count": 50, "challenge_pairs_sha256": hashlib.sha256(raw).hexdigest(),
                "source_ids_sha256": evaluator.source_ids_sha256(rows),
                "selection_manifest_sha256": hashlib.sha256(selection_bytes).hexdigest(),
                "counts": {"datasets": dataset_counts(rows)}}
        provenance = evaluator.validate_lock_metadata(lock, raw, rows, "human_review_passed", selection_bytes, 2)
        self.assertEqual(provenance["review_status"], "human_review_passed")
        evaluator.validate_challenge_design(rows, TASKS, FAMILIES,
                      {"confident_longer": 25, "hedged_longer": 25}, "human_review_passed",
                      provenance["reviewer_types"], provenance["independent_reviewer_count"],
                      source_datasets=DATASETS)
        dataset_provenance = evaluator.validate_selection_manifest(selection, rows, DATASETS)
        self.assertEqual(dataset_provenance["by_dataset"], {DATASETS[0]: 35, DATASETS[1]: 15})
        broken_counts = dict(lock)
        broken_counts["counts"] = {"datasets": {DATASETS[0]: 34, DATASETS[1]: 16}}
        with self.assertRaisesRegex(ValueError, "dataset counts"):
            evaluator.validate_lock_metadata(
                broken_counts, raw, rows, "human_review_passed", selection_bytes, 2)
        lock["locked"] = False
        with self.assertRaisesRegex(ValueError, "locked=true"):
            evaluator.validate_lock_metadata(lock, raw, rows, "human_review_passed", selection_bytes, 2)

    def test_agent_only_review_is_explicitly_not_human_review(self):
        rows = challenge_rows()
        raw = b"private pair bytes"
        lock = {"locked": True, "review_status": "agent_only_pre_screen", "pair_count": 50,
                "challenge_pairs_sha256": hashlib.sha256(raw).hexdigest(),
                "source_ids_sha256": evaluator.source_ids_sha256(rows)}
        with self.assertRaises(evaluator.ReviewStatusError):
            evaluator.validate_lock_metadata(lock, raw, rows)

    def test_blinded_agent_development_mode_requires_complete_consistent_provenance(self):
        rows = challenge_rows("agent_reviewed_development_only", ("agent", "agent"))
        raw = ("\n".join(json.dumps(row, sort_keys=True) for row in rows) + "\n").encode()
        lock = {"locked": True, "review_status": "agent_reviewed_development_only",
                "reviewer_types": ["agent", "agent"],
                "reviewers": reviewer_records(("agent", "agent")),
                "independent_reviewer_count": 2, "independent_reviews_complete": True,
                "reviews_blinded": True, "human_review": "pending",
                "agent_review_is_human_review": False,
                "scientific_status": "development_only_not_human_validated",
                "pair_count": 50, "challenge_pairs_sha256": hashlib.sha256(raw).hexdigest(),
                "source_ids_sha256": evaluator.source_ids_sha256(rows),
                "counts": {"datasets": dataset_counts(rows)}}
        provenance = evaluator.validate_lock_metadata(lock, raw, rows,
                          "agent_reviewed_development_only", required_independent_reviewers=2)
        self.assertFalse(provenance["human_review"])
        self.assertEqual(provenance["scientific_status"], "development_only_not_human_validated")
        evaluator.validate_challenge_design(rows, TASKS, FAMILIES,
                    {"confident_longer": 25, "hedged_longer": 25},
                    "agent_reviewed_development_only", ["agent", "agent"], 2,
                    source_datasets=DATASETS)

        for update in (
            {"reviewers": reviewer_records(("agent", "human")), "reviewer_types": ["agent", "human"]},
            {"reviewers": reviewer_records(("agent", "mystery")), "reviewer_types": ["agent", "mystery"]},
            {"reviewers": reviewer_records(("agent",)), "reviewer_types": ["agent"],
             "independent_reviewer_count": 1},
            {"reviewers": None},
            {"independent_reviews_complete": False},
            {"independent_reviewer_count": 0},
            {"agent_review_is_human_review": True},
            {"human_review": "passed"},
            {"scientific_status": "locked_human_reviewed_transfer_evaluation"},
        ):
            broken = dict(lock)
            broken.update(update)
            with self.assertRaises(evaluator.ReviewStatusError):
                evaluator.validate_lock_metadata(broken, raw, rows,
                              "agent_reviewed_development_only", required_independent_reviewers=2)

        malformed = [dict(row) for row in rows]
        malformed[0]["human_review"] = "passed"
        with self.assertRaisesRegex(evaluator.ReviewStatusError, "human_review=pending"):
            evaluator.validate_challenge_design(malformed, TASKS, FAMILIES,
                      {"confident_longer": 25, "hedged_longer": 25},
                      "agent_reviewed_development_only", ["agent", "agent"], 2,
                      source_datasets=DATASETS)

    def test_synthetic_assignment_and_development_leakage_gates(self):
        test = challenge_rows()
        dev = dev_rows()
        result = evaluator.validate_challenge_design(test, TASKS, FAMILIES,
                      {"confident_longer": 25, "hedged_longer": 25},
                      source_datasets=DATASETS)
        self.assertEqual(result["pairs"], 50)
        self.assertEqual(result["by_dataset"], {DATASETS[0]: 35, DATASETS[1]: 15})
        self.assertEqual(result["by_task"], {task: 10 for task in TASKS})
        self.assertTrue(all(value == 10 for value in result["by_cue_family"].values()))
        self.assertTrue(evaluator.validate_independence(dev, test)["groups_disjoint"])
        overlapping = [dict(row) for row in test]
        overlapping[0]["source_id"] = dev[0]["source_id"]
        with self.assertRaisesRegex(ValueError, "source ID leakage"):
            evaluator.validate_independence(dev, overlapping)
        with self.assertRaisesRegex(ValueError, "source per length direction"):
            malformed = [dict(row) for row in test]
            malformed[1]["length_direction"] = malformed[0]["length_direction"]
            evaluator.validate_challenge_design(malformed, TASKS, FAMILIES,
                           {"confident_longer": 25, "hedged_longer": 25},
                           source_datasets=DATASETS)

    def test_challenge_dataset_is_required_supported_and_frozen(self):
        rows = challenge_rows()
        missing = [dict(row) for row in rows]
        missing[0].pop("dataset")
        with self.assertRaisesRegex(ValueError, "missing fields: dataset"):
            evaluator.validate_challenge_design(
                missing, TASKS, FAMILIES,
                {"confident_longer": 25, "hedged_longer": 25},
                source_datasets=DATASETS)

        unsupported = [dict(row) for row in rows]
        unsupported[0]["dataset"] = "example/unsupported"
        with self.assertRaisesRegex(ValueError, "unsupported dataset"):
            evaluator.validate_challenge_design(
                unsupported, TASKS, FAMILIES,
                {"confident_longer": 25, "hedged_longer": 25},
                source_datasets=DATASETS)

        records = [{key: row[key] for key in
                    ("source_id", "dataset", "group_id", "normalized_prompt_sha256",
                     "task", "cue_family", "length_direction")} for row in rows]
        selection = {"source_count": 50, "source_records": records,
                     "by_dataset": dataset_counts(rows)}
        records[0]["dataset"] = DATASETS[1]
        with self.assertRaisesRegex(ValueError, "changed frozen dataset"):
            evaluator.validate_selection_manifest(selection, rows, DATASETS)

    def test_dataset_balance_is_not_an_evaluation_gate(self):
        rows = challenge_rows()
        for row in rows:
            row["dataset"] = DATASETS[0]
        design = evaluator.validate_challenge_design(
            rows, TASKS, FAMILIES,
            {"confident_longer": 25, "hedged_longer": 25},
            source_datasets=DATASETS)
        self.assertEqual(design["by_dataset"], {DATASETS[0]: 50, DATASETS[1]: 0})
        records = [{key: row[key] for key in
                    ("source_id", "dataset", "group_id", "normalized_prompt_sha256",
                     "task", "cue_family", "length_direction")} for row in rows]
        selection = {"source_count": 50, "source_records": records,
                     "by_dataset": {DATASETS[0]: 50}}
        provenance = evaluator.validate_selection_manifest(selection, rows, DATASETS)
        self.assertEqual(provenance["by_dataset"], {DATASETS[0]: 50, DATASETS[1]: 0})

    def test_dataset_exploratory_metrics_cover_the_same_methods(self):
        class Indexable:
            def __getitem__(self, indices):
                return self

        methods = {
            "layer14": Indexable(),
            "ensemble": Indexable(),
            "char_tfidf": Indexable(),
            "negative_mean_response_nll": Indexable(),
            "negative_response_token_length": Indexable(),
        }
        with mock.patch.object(evaluator, "_grouped_interval", return_value={"estimate": 0.5}) as interval:
            result = evaluator._exploratory_groups(
                challenge_rows(), "dataset", DATASETS, methods, Indexable(),
                SimpleNamespace(), 500, 20)
        self.assertEqual(set(result), set(DATASETS))
        self.assertTrue(all(set(metrics) == set(methods) for metrics in result.values()))
        self.assertEqual(interval.call_count, len(DATASETS) * len(methods))

    def test_development_agent_acceptance_is_not_mislabeled_human_review(self):
        pairs = dev_rows()
        self.assertTrue(all("dataset" not in row for row in pairs))
        evaluator._validate_pair_text(pairs[0], challenge=False)
        accepted = {row["review_id"] for row in pairs}
        manifest = {"pairs": 50, "final_agent_accepted": 50, "final_agent_rejected_or_pending": 0,
                    "agent_qa_is_human_review": False, "human_review": "pending"}
        provenance = evaluator.validate_development_acceptance(pairs, manifest, accepted, set())
        self.assertEqual(provenance["human_review"], "pending")
        self.assertFalse(provenance["agent_qa_is_human_review"])

    def test_hidden_readouts_fit_development_once_and_score_frozen_test(self):
        dev = object()
        test = object()
        groups = object()
        layer_scores, ensemble_scores = object(), object()
        md_layer_scores, md_ensemble_scores = object(), object()

        class FakePaired:
            def __init__(self, **kwargs):
                self.kwargs = kwargs
                self.fit_calls = []

            def fit(self, X, source_groups):
                self.fit_calls.append((X, source_groups))
                return self

            def decision_function(self, X):
                assert X is test
                return layer_scores

            def equal_scores(self, X):
                assert X is test
                return ensemble_scores

        class FakeMeanDifference(FakePaired):
            def decision_function(self, X):
                assert X is test
                return md_layer_scores

            def equal_scores(self, X):
                assert X is test
                return md_ensemble_scores

        module = SimpleNamespace(PairedLayerReadouts=FakePaired,
                                 MeanDifferenceReadout=FakeMeanDifference)
        result = evaluator.fit_frozen_hidden_readouts(dev, test, groups, module, .1, 2000)
        self.assertEqual(result["paired_model"].fit_calls, [(dev, groups)])
        self.assertEqual(result["mean_difference_model"].fit_calls, [(dev, groups)])
        self.assertIs(result["layer_scores"], layer_scores)
        self.assertIs(result["ensemble_scores"], ensemble_scores)
        self.assertIs(result["mean_difference_layer_scores"], md_layer_scores)
        self.assertIs(result["mean_difference_ensemble_scores"], md_ensemble_scores)


if __name__ == "__main__":
    unittest.main()
