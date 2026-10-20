"""Campaign planning and frozen-evidence checks never contact a provider."""
import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))
import run_campaign as campaign


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


class CampaignSourcePlanningTests(unittest.TestCase):
    def test_cache_first_mode_uses_pending_sources_before_fetching_more(self):
        config = {"target_sources": 10000, "batch_size": 5,
                  "campaign": {"source_chunk_size": 500, "consume_prepared_sources_first": True}}
        self.assertEqual(campaign.campaign_source_count(1650, 35, 1603, config), 1650)
        self.assertEqual(campaign.campaign_source_count(1650, 0, 1638, config), 2150)
        self.assertEqual(campaign.campaign_source_count(1650, 4, 1638, config), 2150)
        self.assertEqual(campaign.campaign_source_count(10000, 0, 9998, config), 10005)

    def test_cache_first_mode_is_opt_in_and_does_not_relax_validation(self):
        config = {"target_sources": 10000, "batch_size": 5,
                  "campaign": {"source_chunk_size": 500}}
        for value in [None, False, "true", 1]:
            config["campaign"]["consume_prepared_sources_first"] = value
            self.assertEqual(campaign.campaign_source_count(1650, 35, 1603, config), 2115)
        config["campaign"]["consume_prepared_sources_first"] = True
        with self.assertRaises(ValueError):
            campaign.campaign_source_count(-1, 35, 1603, config)

    def test_next_pool_adds_only_missing_fresh_rows_in_full_batches(self):
        cases = (
            # Existing five quarantined sources do not count toward the target.
            (590, 0, 585, 10000, 500, 5, 1090),
            (10000, 0, 9995, 10000, 500, 5, 10005),
            # Untouched prepared rows are consumed before fetching more sources.
            (590, 130, 455, 10000, 500, 5, 960),
            (590, 497, 85, 10000, 500, 5, 595),
            (590, 500, 85, 10000, 500, 5, 590),
            (590, 505, 80, 10000, 500, 5, 590),
            # A final small remainder needs just one fresh batch.
            (10000, 0, 9998, 10000, 500, 5, 10005),
            (10000, 3, 9998, 10000, 500, 5, 10000),
            # Neither a completed target nor a larger pool is shrunk.
            (590, 0, 10000, 10000, 500, 5, 590),
            (10005, 0, 10005, 10000, 500, 5, 10005),
            # Round the append size, including a non-aligned chunk, upward.
            (590, 0, 585, 10000, 503, 5, 1095),
        )
        for source_count, pending, generated, target, chunk, batch, expected in cases:
            with self.subTest(source_count=source_count, pending=pending, generated=generated, chunk=chunk):
                actual = campaign.next_source_count(source_count, pending, generated, target, chunk, batch)
                self.assertEqual(actual, expected)
                self.assertGreaterEqual(actual, source_count)
                self.assertEqual((actual - source_count) % batch, 0)


class CampaignBaselineTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.root = self.base / "private_data" / "expansion"
        self.canary = self.base / "private_data" / "canary"
        self.config = {"canary_private_dir": "private_data/canary"}
        self.sources = [
            {"review_id": f"HC{index:03d}", "source_id": f"frozen-{index}",
             "question": f"What is process {index}?", "original": f"Original answer {index}.",
             "reuse_canary": index == 1}
            for index in range(1, 4)
        ]
        write_json(self.root / "SOURCES.json", self.sources)
        write_json(self.root / "RUN_STATUS.json", {"state": "prepared_source_pool_exhausted",
            "total_generated_triplets": 2, "calls_without_final_cost": 0})
        self.original_files = {
            self.root / "provider/batch_00001.request.json": {"request_sha256": "request-one"},
            self.root / "provider/batch_00001.raw.json": {"result": "original provider result"},
            self.root / "provider/batch_00001.parsed.json": {"records": [{"id": "HC002"}]},
            self.root / "provider_repairs_v1/repair_00001.raw.json": {"result": "original repair"},
            self.root / "REWRITE_PROTOCOL_v2.json": {"prompt_sha256": "unchanged-quality"},
            self.canary / "review_final_v2/TRIPLETS_50.json": {"triplets": [self.sources[0]]},
            self.canary / "SOURCE_CAPTURE_MANIFEST.json": {"dataset_revision": "fixed-revision"},
        }
        for path, value in self.original_files.items():
            write_json(path, value)
        events = self.root / "provider/batch_00001.events.jsonl"
        events.write_text('{"type":"result","subtype":"success"}\n', encoding="utf-8")
        stderr = self.root / "provider/batch_00001.stderr.txt"
        stderr.write_text("original stderr evidence\n", encoding="utf-8")
        self.original_files[events] = None
        self.original_files[stderr] = None
        self.original_bytes = {path: path.read_bytes() for path in self.original_files}
        self.original_sources_bytes = (self.root / "SOURCES.json").read_bytes()
        patcher = mock.patch.object(campaign, "BASE", self.base)
        patcher.start()
        self.addCleanup(patcher.stop)

    def preserve(self):
        return campaign.preserve_baseline(self.root, self.config)

    def test_initial_baseline_snapshots_sources_and_all_existing_evidence(self):
        baseline = self.preserve()
        saved = self.root / "CAMPAIGN_BASELINE.json"
        self.assertEqual(json.loads(saved.read_text(encoding="utf-8")), baseline)
        encoded = json.dumps(baseline, ensure_ascii=False)
        self.assertEqual(baseline["source_count"], len(self.sources))
        self.assertEqual(baseline["source_prefix_sha256"], campaign.prefix_sha(self.sources))
        self.assertEqual(baseline["source_file_sha256"],
                         hashlib.sha256(self.original_sources_bytes).hexdigest())
        for path, original in self.original_bytes.items():
            with self.subTest(path=path.relative_to(self.base)):
                self.assertIn(hashlib.sha256(original).hexdigest(), encoded)
                self.assertEqual(path.read_bytes(), original)
        self.assertEqual((self.root / "SOURCES.json").read_bytes(), self.original_sources_bytes)

    def test_baseline_is_idempotent_and_is_not_replaced_on_append(self):
        original_baseline = self.preserve()
        baseline_path = self.root / "CAMPAIGN_BASELINE.json"
        original_bytes = baseline_path.read_bytes()
        self.assertEqual(self.preserve(), original_baseline)
        self.assertEqual(baseline_path.read_bytes(), original_bytes)

        write_json(self.root / "SOURCES.json", [*self.sources, {
            "review_id": "HC004", "source_id": "new-source", "original": "Fresh answer."}])
        write_json(self.root / "provider/batch_00002.raw.json", {"result": "fresh result"})
        write_json(self.root / "provider_repairs_v2/repair_00002.raw.json", {"result": "fresh repair"})

        self.assertEqual(self.preserve(), original_baseline)
        self.assertEqual(baseline_path.read_bytes(), original_bytes)
        for path, original in self.original_bytes.items():
            self.assertEqual(path.read_bytes(), original)

    def test_original_source_prefix_cannot_be_changed_reordered_or_shortened(self):
        self.preserve()
        changed = copy.deepcopy(self.sources)
        changed[1]["original"] = "Changed frozen answer."
        for sources in (changed, list(reversed(self.sources)), self.sources[:-1]):
            with self.subTest(sources=sources):
                write_json(self.root / "SOURCES.json", sources)
                before = (self.root / "SOURCES.json").read_bytes()
                with self.assertRaises(RuntimeError):
                    self.preserve()
                self.assertEqual((self.root / "SOURCES.json").read_bytes(), before)

    def test_every_original_provider_protocol_and_canary_file_remains_pinned(self):
        self.preserve()
        baseline_path = self.root / "CAMPAIGN_BASELINE.json"
        baseline_bytes = baseline_path.read_bytes()
        for path, original in self.original_bytes.items():
            with self.subTest(path=path.relative_to(self.base), change="modified"):
                path.write_bytes(original + b" ")
                try:
                    with self.assertRaises(RuntimeError):
                        self.preserve()
                    self.assertEqual(baseline_path.read_bytes(), baseline_bytes)
                finally:
                    path.write_bytes(original)
            with self.subTest(path=path.relative_to(self.base), change="missing"):
                path.unlink()
                try:
                    with self.assertRaises(RuntimeError):
                        self.preserve()
                    self.assertEqual(baseline_path.read_bytes(), baseline_bytes)
                finally:
                    path.write_bytes(original)

    def test_canary_is_optional_for_a_temporary_fixture(self):
        self.config = {}
        baseline = self.preserve()
        self.assertEqual(self.preserve(), baseline)


if __name__ == "__main__":
    unittest.main()
