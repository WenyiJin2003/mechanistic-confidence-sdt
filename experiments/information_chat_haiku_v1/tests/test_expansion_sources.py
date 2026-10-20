"""In-memory network fixtures exercise source immutability and capture guards."""
import copy
import json
import sys
import tempfile
import unittest
from unittest import mock
import urllib.error
import urllib.parse
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))
import prepare_expansion as expansion


def source(index, eligible=True):
    question = f"What is the underlying process numbered {index}?" if eligible else "Write a story."
    answer = " ".join([f"Process{index}"] + ["explanation"] * 39)
    return {"prompt_id": f"group-{index}", "prompt": question,
            "messages": [{"role": "user", "content": question},
                         {"role": "assistant", "content": answer},
                         {"role": "user", "content": "What is another question?"},
                         {"role": "assistant", "content": "Later turns must never become sources."}]}


class ExpansionSourceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.config = {"dataset_id": expansion.DATASET, "dataset_revision": expansion.REVISION,
                       "split": "train_sft", "page_size": 100, "answer_words_min": 40,
                       "answer_words_max": 180, "question_chars_max": 1600, "target_sources": 10000,
                       "private_dir": "private_data/expansion", "canary_private_dir": "private_data/canary",
                       "seed": 12}
        self.canary = self.base / self.config["canary_private_dir"]
        self.root = self.base / self.config["private_dir"]
        self.metadata_calls = 0
        self.row_calls = []
        self.metadata_sha = expansion.REVISION
        response = self.response(0)
        for item in response["rows"][50:]:
            item["row"] = source(item["row_idx"], False)
        url = expansion.page_url(self.config, 0)
        cache_path = self.canary / "source_cache/rows_000000.json"
        expansion.atomic_json(cache_path, {"source_url": url, "dataset_revision_checked": expansion.REVISION,
                                           "response": response})
        expansion.atomic_json(self.canary / "SOURCE_CAPTURE_MANIFEST.json", {
            "dataset": expansion.DATASET, "revision": expansion.REVISION, "rows_screened": 100,
            "cache_files": [{"file": "source_cache/rows_000000.json", "url": url,
                             "sha256": expansion.digest(cache_path.read_bytes())}]})
        records = []
        for item in response["rows"][:50]:
            row = item["row"]
            records.append({"source_id": row["prompt_id"], "group_id": row["prompt_id"],
                            "review_id": f"HC{item['row_idx'] + 1:03d}", "row_idx": item["row_idx"],
                            "question": row["messages"][0]["content"], "original": row["messages"][1]["content"],
                            "word_count": 40, "raw_source_row": row, "confident": "approved confident",
                            "hesitant": "approved hesitant"})
        self.approved = copy.deepcopy(records)
        expansion.atomic_json(self.canary / "review_final_v2/TRIPLETS_50.json", {
            "dataset": expansion.DATASET, "revision": expansion.REVISION, "triplets": records})

    @staticmethod
    def response(offset):
        return {"num_rows_total": 1000, "partial": False,
                "rows": [{"row_idx": index, "row": source(index), "truncated_cells": []}
                         for index in range(offset, offset + 100)]}

    def fetcher(self, url):
        if "api/datasets/" in url:
            self.metadata_calls += 1
            return {"sha": self.metadata_sha, "id": expansion.DATASET}
        offset = int(urllib.parse.parse_qs(urllib.parse.urlparse(url).query)["offset"][0])
        self.row_calls.append(offset)
        return self.response(offset)

    def run_prepare(self, **kwargs):
        return expansion.prepare(self.config, base=self.base, fetcher=self.fetcher, **kwargs)

    def test_sample_extends_prefix_and_retains_approved_answers(self):
        first = self.run_prepare(pages=2, freeze_count=55)
        sources = expansion.read_json(self.root / "SOURCES.json")
        first_bytes = (self.root / "SOURCES.json").read_bytes()
        self.assertEqual(len(sources), 55)
        self.assertEqual(sources[-1]["review_id"], "HC055")
        for approved, selected in zip(self.approved, sources):
            self.assertTrue(selected["reuse_canary"])
            for key, value in approved.items():
                self.assertEqual(selected[key], value)
        self.assertFalse(sources[50]["reuse_canary"])
        self.assertFalse(first["target_complete"])
        self.assertEqual(first["status"], "partial_source_sample")
        self.assertEqual(first["rows_screened"], 200)
        self.assertEqual(self.metadata_calls, 4)  # before/after reuse and before/after new capture
        self.assertEqual(len(self.row_calls), 1)
        self.run_prepare(pages=2, freeze_count=55)
        self.assertEqual((self.root / "SOURCES.json").read_bytes(), first_bytes)
        self.assertEqual(len(self.row_calls), 1)
        self.run_prepare(pages=3, freeze_count=155)
        extended = expansion.read_json(self.root / "SOURCES.json")
        self.assertEqual(extended[:55], sources)
        self.assertEqual(extended[154]["review_id"], "HC155")

    def test_conversation_question_and_answer_are_independent_dedupe_keys(self):
        def record(group, question, answer):
            return {"group_id": group, "question": question, "original": answer}
        prefix = [record("g1", "What IS   energy?", "First answer.")]
        rows = [record("g1", "New question", "New answer"),
                record("g2", "what is energy?", "Changed answer"),
                record("g3", "Different question", " FIRST answer. "),
                record("g4", "Unique question", "Unique answer")]
        unique, rejected = expansion.dedupe_sources(rows, prefix)
        self.assertEqual([row["group_id"] for row in unique], ["g4"])
        self.assertEqual(rejected, {"duplicate_group": 1, "duplicate_question": 1, "duplicate_answer": 1})

    def test_tampered_canary_cache_stops_before_new_capture(self):
        path = self.canary / "source_cache/rows_000000.json"
        path.write_text(path.read_text() + " ", encoding="utf-8")
        with self.assertRaisesRegex(RuntimeError, "Canary cache hash mismatch"):
            self.run_prepare(pages=2, freeze_count=55)
        self.assertFalse(self.row_calls)
        self.assertFalse((self.root / "SOURCES.json").exists())

    def test_tampered_expansion_cache_is_rejected(self):
        self.run_prepare(pages=2, freeze_count=55)
        path = next(path for path in (self.root / "source_cache").glob("rows_*.json"))
        path.write_text(path.read_text() + " ", encoding="utf-8")
        with self.assertRaisesRegex(RuntimeError, "Expansion cache hash mismatch"):
            self.run_prepare(pages=2, freeze_count=55)

    def test_changed_frozen_prefix_is_never_overwritten(self):
        self.run_prepare(pages=2, freeze_count=55)
        path = self.root / "SOURCES.json"
        sources = expansion.read_json(path)
        sources[0]["question"] = "Tampered frozen question"
        expansion.atomic_json(path, sources)
        before = path.read_bytes()
        with self.assertRaisesRegex(RuntimeError, "prefix changed"):
            self.run_prepare(pages=2, freeze_count=55)
        self.assertEqual(path.read_bytes(), before)

    def test_revision_change_during_capture_does_not_freeze_pages_or_sources(self):
        def changing_fetcher(url):
            result = self.fetcher(url)
            if "api/datasets/" in url and self.metadata_calls == 4:
                return {"sha": "changed"}
            return result
        with self.assertRaisesRegex(RuntimeError, "revision differs"):
            expansion.prepare(self.config, base=self.base, pages=2, freeze_count=55, fetcher=changing_fetcher)
        self.assertFalse((self.root / "SOURCES.json").exists())
        self.assertFalse(list((self.root / "source_cache").glob("rows_*.json")))

    def test_only_first_turn_and_existing_filters_are_used(self):
        item = {"row_idx": 9, "row": source(9, False)}
        item["row"]["messages"][2:] = source(99)["messages"][:2]
        pin = {"url": "unused", "sha256": "unused"}
        self.assertIsNone(expansion.source_record(item, pin, self.root, self.canary / "cache", self.config))
        changed = dict(self.config, answer_words_max=200)
        with self.assertRaisesRegex(ValueError, "source filters are frozen"):
            expansion.validate_config(changed)

    def test_incomplete_requested_count_is_explicit(self):
        summary = self.run_prepare(pages=1, freeze_count=300)
        self.assertEqual(summary["frozen_sources"], 50)
        self.assertFalse(summary["requested_prefix_complete"])
        self.assertFalse(summary["target_complete"])
        self.assertEqual(summary["pages_captured"], 1)
        self.assertEqual(self.row_calls, [])

    def test_page_plan_does_not_depend_on_requested_prefix_size(self):
        first = expansion.make_page_plan(207865, 100, 20261019, [1000, 3000])
        second = expansion.make_page_plan(207865, 100, 20261019, [1000, 3000])
        self.assertEqual(first, second)
        self.assertEqual(first[:2], [1000, 3000])
        self.assertEqual(len(first), len(set(first)))
        self.assertEqual(len(first), 2079)

    def test_low_yield_projection_does_not_claim_full_target_feasible(self):
        estimate = expansion.estimate_feasibility(110, 4000, 207865, 10000)
        self.assertEqual(estimate["estimated_rows_needed_for_target"], 363637)
        self.assertFalse(estimate["target_feasible_at_observed_yield"])
        self.assertFalse(estimate["filters_relaxed"])

    def test_public_source_rate_limit_stops_without_retry(self):
        error = urllib.error.HTTPError("https://example.test", 429, "rate limited", {"Retry-After": "18"}, None)
        self.addCleanup(error.close)
        with mock.patch.object(expansion.urllib.request, "urlopen", side_effect=error) as request:
            with mock.patch.object(expansion.time, "sleep") as sleep:
                with self.assertRaises(urllib.error.HTTPError):
                    expansion.fetch("https://example.test")
                self.assertEqual(request.call_count, 1)
                sleep.assert_not_called()


if __name__ == "__main__":
    unittest.main()
