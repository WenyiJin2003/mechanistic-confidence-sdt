"""Offline fixtures for immutable, deduplicated pinned-Parquet source selection."""
import copy
import io
import json
import sys
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))
import prepare_bulk_sources as bulk


def row(index, question=None, answer=None, group=None):
    question = question or f"What is the scientific process numbered {index}?"
    answer = answer or " ".join([f"Process{index}"] + ["explanation"] * 39)
    return {"prompt_id": group or f"group-{index}", "prompt": question,
            "messages": [{"role": "user", "content": question},
                         {"role": "assistant", "content": answer}]}


class BulkSourceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.config = {"dataset_id": bulk.DATASET, "dataset_revision": bulk.REVISION,
                       "split": "train_sft", "page_size": 100, "seed": 20261019,
                       "answer_words_min": 40, "answer_words_max": 180,
                       "question_chars_max": 1600, "target_sources": 10000,
                       "private_dir": "private_data/expansion", "canary_private_dir": "private_data/canary"}
        self.root = self.base / self.config["private_dir"]
        self.canary = self.base / self.config["canary_private_dir"]
        self.sources = []
        for index in range(50):
            raw = row(index)
            screened = bulk.source_screen(raw, self.config)
            self.sources.append({"review_id": f"HC{index + 1:03d}", "source_id": raw["prompt_id"],
                                 "group_id": raw["prompt_id"], "row_idx": index,
                                 "source_cache_file": "legacy.json", "raw_source_row": raw, **screened,
                                 "question_sha256": bulk.digest(screened["question"]),
                                 "original_sha256": bulk.digest(screened["original"]),
                                 "confident": "preserve approved confident", "hesitant": "preserve approved hesitant"})
        bulk.atomic_json(self.root / "SOURCES.json", self.sources)
        bulk.atomic_json(self.root / "SOURCE_CONFIG.json", self.config)
        bulk.atomic_json(self.canary / "review_final_v2/TRIPLETS_50.json", {
            "dataset": bulk.DATASET, "revision": bulk.REVISION, "triplets": self.sources})
        bulk.atomic_json(self.root / "SOURCE_CAPTURE_MANIFEST.json", {
            "source_screen_implementation_sha256": bulk.file_hash(SRC / "prepare_sources.py"),
            "sources_sha256": bulk.file_hash(self.root / "SOURCES.json"),
            "approved_packet_sha256": bulk.file_hash(self.canary / "review_final_v2/TRIPLETS_50.json")})
        self.pins = [{"split": split, "path": f"data/{split}-0.parquet", "size": 4,
                      "sha256": bulk.digest(b"test"), "url": f"https://example.test/{split}"}
                     for split in bulk.SPLITS]
        self.rows = {"train_sft": [row(index) for index in range(50, 55)],
                     "train_gen": [row(index) for index in range(55, 60)]}
        self.download_calls, self.row_visits = [], []
        self.patches = [mock.patch.object(bulk, "training_files", return_value=self.pins),
                        mock.patch.object(bulk, "checked_tree", return_value={"url": "fixture", "response": []}),
                        mock.patch.object(bulk, "ensure_file", side_effect=self.ensure_file),
                        mock.patch.object(bulk, "iter_rows", side_effect=self.iter_rows),
                        mock.patch.object(bulk, "SPLIT_ROWS", {"train_sft": 5, "train_gen": 5})]
        for patch in self.patches:
            patch.start()
            self.addCleanup(patch.stop)

    def ensure_file(self, root, pin):
        self.download_calls.append(pin["split"])
        path = root / "source_cache/pinned_parquet" / Path(pin["path"]).name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()
        return path

    def iter_rows(self, path, start):
        split = next(pin["split"] for pin in self.pins if Path(pin["path"]).name == path.name)
        for offset, raw in enumerate(self.rows[split]):
            if offset >= start:
                self.row_visits.append((split, offset))
                yield offset, copy.deepcopy(raw)

    def prepare(self, count, **kwargs):
        return bulk.prepare_bulk(self.config, base=self.base, freeze_count=count, **kwargs)

    def read_sources(self):
        return bulk.read_json(self.root / "SOURCES.json")

    def test_training_order_provenance_and_exact_stop_then_resume(self):
        result = self.prepare(53, max_new_files=1)
        sources = self.read_sources()
        self.assertEqual(sources[:50], self.sources)
        self.assertEqual([source["source_id"] for source in sources[50:]], ["group-50", "group-51", "group-52"])
        self.assertEqual(result["cursor"], {"file_index": 0, "row_offset": 3, "split_row_idx": 3})
        self.assertEqual(sources[-1]["transport"], "pinned_parquet")
        self.assertEqual(sources[-1]["source_shard_row_offset"], 2)
        self.assertEqual(sources[-1]["source_cache_sha256"], self.pins[0]["sha256"])
        self.prepare(57)
        extended = self.read_sources()
        self.assertEqual(extended[:53], sources)
        self.assertEqual(extended[-1]["split"], "train_gen")
        self.assertEqual(extended[-1]["global_row_idx"], 6)
        self.assertEqual(extended[-1]["review_id"], "HC057")
        self.assertNotIn(("train_sft", 0), self.row_visits[3:])

    def test_global_dedupe_includes_legacy_and_other_split(self):
        self.rows["train_sft"] = [row(100, group="group-0"), row(101, question=self.sources[1]["question"].upper()),
                                  row(102, answer="  " + self.sources[2]["original"].upper()), row(103), row(104)]
        self.rows["train_gen"] = [row(103), row(105), row(106), row(107), row(108)]
        result = self.prepare(100)
        self.assertTrue(result["exhausted"])
        self.assertEqual([source["source_id"] for source in self.read_sources()[50:]],
                         ["group-103", "group-104", "group-105", "group-106", "group-107", "group-108"])

    def test_same_screen_and_first_turn_only(self):
        self.rows["train_sft"][0] = row(50, question="Write a story.")
        self.rows["train_sft"][0]["messages"].extend(row(200)["messages"])
        self.rows["train_sft"][1] = row(51, answer="too short")
        self.rows["train_sft"][2] = row(52, answer=" ".join(["long"] * 181))
        self.prepare(51)
        self.assertEqual(self.read_sources()[-1]["source_id"], "group-53")

    def test_tampered_committed_prefix_and_canary_are_rejected(self):
        self.prepare(52)
        sources = self.read_sources()
        sources[-1]["manual_source_selection"] = "tampered"
        bulk.atomic_json(self.root / "SOURCES.json", sources)
        with self.assertRaisesRegex(RuntimeError, "Committed bulk source prefix"):
            self.prepare(53)
        self.assertEqual(len(self.download_calls), 1)

    def test_canary_and_quality_hash_are_checked_before_capture(self):
        packet_path = self.canary / "review_final_v2/TRIPLETS_50.json"
        packet = bulk.read_json(packet_path)
        packet["triplets"][0]["confident"] = "changed"
        bulk.atomic_json(packet_path, packet)
        with self.assertRaisesRegex(RuntimeError, "canary source or rewrite"):
            self.prepare(51)
        self.assertEqual(self.download_calls, [])
        packet["triplets"] = self.sources
        bulk.atomic_json(packet_path, packet)
        bulk.atomic_json(self.root / "SOURCE_CAPTURE_MANIFEST.json", {"source_screen_implementation_sha256": "changed"})
        with self.assertRaisesRegex(RuntimeError, "Source-screen implementation"):
            self.prepare(51)

    def test_crash_after_append_before_cursor_replays_without_skips(self):
        real_atomic = bulk.atomic_json
        def crash(path, value):
            if Path(path).name == "BULK_SOURCE_STATE.json":
                raise RuntimeError("simulated state commit interruption")
            real_atomic(path, value)
        with mock.patch.object(bulk, "atomic_json", side_effect=crash):
            with self.assertRaisesRegex(RuntimeError, "simulated"):
                self.prepare(52)
        appended = self.read_sources()
        self.assertEqual(len(appended), 52)
        self.prepare(54)
        recovered = self.read_sources()
        self.assertEqual(recovered[:52], appended)
        self.assertEqual([source["source_id"] for source in recovered[50:]],
                         ["group-50", "group-51", "group-52", "group-53"])

    def test_download_bound_and_pool_can_exceed_triplet_target(self):
        result = self.prepare(10005, max_new_files=0)
        self.assertFalse(result["requested_prefix_complete"])
        self.assertFalse(result["exhausted"])
        self.assertEqual(self.download_calls, [])
        result = self.prepare(10005, max_new_files=1)
        self.assertEqual(result["frozen_sources"], 55)
        self.assertEqual(result["downloads_this_run"], 1)
        self.assertFalse(result["exhausted"])
        result = self.prepare(10005)
        self.assertTrue(result["exhausted"])
        self.assertEqual(result["frozen_sources"], 60)


class TransportTests(unittest.TestCase):
    def test_pinned_hash_download_and_cached_tamper(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            pin = {"path": "data/source.parquet", "url": "https://example.test/source", "size": 4,
                   "sha256": bulk.digest(b"test")}
            with mock.patch.object(bulk.urllib.request, "urlopen", return_value=io.BytesIO(b"test")) as request:
                path = bulk.ensure_file(root, pin)
            self.assertEqual(request.call_count, 1)
            self.assertEqual(path.read_bytes(), b"test")
            with path.open("ab") as stream:
                stream.write(b"x")
            with self.assertRaisesRegex(RuntimeError, "Cached public Parquet"):
                bulk.ensure_file(root, pin)

    def test_rate_limit_has_one_attempt_and_partial_requires_attention(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            pin = {"path": "data/source.parquet", "url": "https://example.test/source", "size": 4,
                   "sha256": bulk.digest(b"test")}
            for code in (403, 429):
                error = urllib.error.HTTPError(pin["url"], code, "stopped", {}, None)
                with mock.patch.object(bulk.urllib.request, "urlopen", side_effect=error) as request:
                    with self.assertRaises(urllib.error.HTTPError):
                        bulk.ensure_file(root, pin)
                self.assertEqual(request.call_count, 1)
                error.close()
            with mock.patch.object(bulk.urllib.request, "urlopen", return_value=io.BytesIO(b"bad")):
                with self.assertRaisesRegex(RuntimeError, "partial retained"):
                    bulk.ensure_file(root, pin)
            with mock.patch.object(bulk.urllib.request, "urlopen") as request:
                with self.assertRaisesRegex(RuntimeError, "manual attention"):
                    bulk.ensure_file(root, pin)
            request.assert_not_called()


if __name__ == "__main__":
    unittest.main()
