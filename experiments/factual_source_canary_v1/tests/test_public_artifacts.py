import json
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


class PublicArtifactTests(unittest.TestCase):
    def test_public_manifests_do_not_contain_source_text(self) -> None:
        forbidden = {"question", "original_response", "evidence", "source_locator"}
        for filename, expected_count in [
            ("source_candidate_manifest.jsonl", 200),
            ("expanded_pool_v2_candidate_manifest.jsonl", 350),
            ("expanded_pool_v2_review_queue_manifest.jsonl", 350),
            ("selected_core_sources_v1_manifest.jsonl", 144),
        ]:
            records = read_jsonl(RESULTS / filename)
            self.assertEqual(len(records), expected_count)
            self.assertTrue(all(forbidden.isdisjoint(record) for record in records))

    def test_model_assisted_review_is_locked_to_ten_per_dataset(self) -> None:
        review = json.loads(
            (RESULTS / "model_assisted_review.json").read_text(encoding="utf-8")
        )
        records = review["records"]
        self.assertEqual(len(records), 40)
        self.assertEqual(
            Counter(record["dataset"] for record in records),
            Counter({"asqa": 10, "billsum": 10, "fetaqa": 10, "qasper": 10}),
        )

    def test_selection_plan_has_balanced_120_source_core(self) -> None:
        plan = json.loads(
            (ROOT / "configs" / "source_selection_plan_v1.json").read_text(
                encoding="utf-8"
            )
        )
        quotas = plan["core"]["quota_by_dataset"]
        self.assertEqual(quotas, {"asqa": 40, "qasper": 40, "billsum": 40})
        self.assertEqual(sum(quotas.values()), 120)
        self.assertEqual(plan["external_control"]["source_count"], 20)

    def test_expanded_pool_has_requested_candidate_counts(self) -> None:
        summary = json.loads(
            (RESULTS / "expanded_pool_v2_summary.json").read_text(encoding="utf-8")
        )
        counts = {
            name: values["candidate_count"]
            for name, values in summary["by_dataset"].items()
        }
        self.assertEqual(
            counts,
            {"asqa": 100, "billsum": 100, "fetaqa": 50, "qasper": 100},
        )

    def test_source_selection_gate_is_complete(self) -> None:
        summary = json.loads(
            (RESULTS / "source_selection_v1_summary.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertTrue(summary["gate_complete"])
        for dataset in ("asqa", "billsum", "qasper"):
            values = summary["by_dataset"][dataset]
            self.assertEqual(values["accepted_count"], 48)
            self.assertEqual(values["core_selected_count"], 40)
            self.assertEqual(values["backup_selected_count"], 8)
            self.assertEqual(values["final_secondary_sample_count"], 12)


if __name__ == "__main__":
    unittest.main()
