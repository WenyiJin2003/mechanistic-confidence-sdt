"""Synthetic cache-only coverage for exact immutable analysis snapshots."""
import copy
import json
import socket
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))
import freeze_analysis_snapshot as frozen


class FreezeAnalysisTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.root = self.base / "private_data/expansion"
        self.config = {"model": "claude-haiku-5-5", "protocol": "synthetic-expansion-v1",
                       "private_dir": "private_data/expansion", "canary_private_dir": "private_data/canary",
                       "dataset_id": "test/dataset", "dataset_revision": "fixture-revision",
                       "split": "train_sft", "license": "MIT", "max_output_tokens": 10000,
                       "canary_approval": {"individual_item_ratings_received": False}}
        self.sources = [self.source(index) for index in range(1, 66)]
        self.write_sources()
        self.save(self.base / "private_data/canary/review_final_v2/TRIPLETS_50.json",
                  {"triplets": [{key: value for key, value in source.items() if key != "reuse_canary"}
                                for source in self.sources[:50]]})
        self.write_batch("provider/batch_00001", self.sources[50:])

    @staticmethod
    def source(index):
        question, answer = f"  Question {index}?\n", f"Exact original {index}.\n  Last line."
        raw = {"prompt_id": f"group-{index}", "messages": [
            {"role": "user", "content": question}, {"role": "assistant", "content": answer}]}
        source = {"review_id": f"HC{index:03d}", "source_id": f"group-{index}", "group_id": f"group-{index}",
                  "row_idx": index, "question": question, "original": answer, "raw_source_row": raw,
                  "question_sha256": frozen.sha(question.encode()),
                  "original_sha256": frozen.sha(answer.encode()),
                  "raw_source_row_sha256": frozen.sha(frozen.canonical(raw)), "reuse_canary": index <= 50}
        if index <= 50:
            source.update(confident=f"Canary confident {index}.  ", hesitant=f"Canary hesitant {index}.\n")
        return source

    def save(self, path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(frozen._json_bytes(value))

    def read(self, path):
        return json.loads(path.read_bytes())

    def write_sources(self):
        self.save(self.root / "SOURCES.json", self.sources)

    def write_batch(self, prefix, sources, *, reject=(), repair=False):
        prompt = "Synthetic rewrite prompt.\n" + ("Minimal repair." if repair else "")
        request_hash = frozen.sha(prefix.encode())
        request = {"request_sha256": request_hash, "model": self.config["model"],
                   "prompt_sha256": frozen.sha(prompt.encode()), "prompt": prompt,
                   "data": {"records": [{"id": source["review_id"], "question": source["question"],
                                          "original_response": source["original"]} for source in sources]}}
        rows = []
        for source in sources:
            key = source["review_id"]
            rows.append({"id": key, "status": "reject" if key in reject else "ok",
                         "confident": None if key in reject else f"Exact confident {key}.  \n",
                         "hesitant": None if key in reject else f"Exact hesitant {key}.\n ",
                         "reject_reason": "fixture rejected" if key in reject else None,
                         "audit_flags": {"confident": [], "hesitant": []}})
        parsed = {"request_sha256": request_hash, "model": self.config["model"], "records": rows}
        self.save(self.root / f"{prefix}.request.json", request)
        self.save(self.root / f"{prefix}.parsed.json", parsed)
        self.save(self.root / f"{prefix}.raw.json", {"result": json.dumps({"records": rows})})
        return parsed

    def freeze(self, count=60):
        return frozen.freeze(self.root, count, self.config, base=self.base)

    def files(self):
        return {str(path.relative_to(self.root)): path.read_bytes()
                for path in self.root.rglob("*") if path.is_file() and "analysis_snapshots" not in path.parts
                and not path.name.startswith("FROZEN_")}

    def test_exact_count_source_order_text_and_cache_unchanged_without_calls(self):
        before = self.files()
        with mock.patch.object(subprocess, "run", side_effect=AssertionError("provider/account call")), \
                mock.patch.object(socket, "create_connection", side_effect=AssertionError("network call")):
            selector = self.freeze()
        packet = self.read(Path(selector["triplets_file"]))
        self.assertEqual(packet["total_triplets"], 60)
        self.assertEqual(packet["new_triplets"], 10)
        self.assertEqual(packet["reused_canary_triplets"], 50)
        self.assertEqual([row["review_id"] for row in packet["triplets"]], [source["review_id"] for source in self.sources[:60]])
        self.assertEqual(packet["triplets"][0]["confident"], self.sources[0]["confident"])
        self.assertEqual(packet["triplets"][50]["confident"], "Exact confident HC051.  \n")
        self.assertTrue(all(row["human_item_rating_received"] is False and row["content_preservation_certified"] is False
                            for row in packet["triplets"]))
        self.assertNotIn("review_records", packet)
        self.assertEqual(self.files(), before)
        self.assertEqual(frozen.verify_snapshot(self.root / "FROZEN_00060.json"), selector)

    def test_rejects_skipped_then_repair_overlays_match_review_selection(self):
        self.write_batch("provider/batch_00001", self.sources[50:], reject=("HC051", "HC053"))
        repaired = self.write_batch("provider_repairs_v1/batch_00001", self.sources[50:51], repair=True)
        repaired["records"][0]["confident"] = "Repaired exact text.  "
        self.save(self.root / "provider_repairs_v1/batch_00001.parsed.json", repaired)
        self.write_batch("provider_repairs_v2/batch_00001", self.sources[51:52], reject=("HC052",), repair=True)
        selector = self.freeze(52)
        rows = self.read(Path(selector["triplets_file"]))["triplets"]
        self.assertEqual([row["review_id"] for row in rows[-2:]], ["HC051", "HC054"])
        self.assertEqual(rows[-2]["confident"], "Repaired exact text.  ")
        self.assertTrue(rows[-2]["rewrite_provenance"]["repair_applied"])

    def test_insufficient_cache_does_not_create_selector(self):
        with self.assertRaisesRegex(RuntimeError, "Insufficient valid cached"):
            self.freeze(66)
        self.assertFalse((self.root / "FROZEN_00066.json").exists())
        self.assertFalse((self.root / "analysis_snapshots").exists())

    def test_duplicate_sources_and_generated_ids_fail(self):
        self.sources[-1]["source_id"] = self.sources[-2]["source_id"]
        self.write_sources()
        with self.assertRaisesRegex(RuntimeError, "Duplicate"):
            self.freeze()
        self.sources[-1] = self.source(65)
        self.write_sources()
        parsed = self.read(self.root / "provider/batch_00001.parsed.json")
        parsed["records"].append(copy.deepcopy(parsed["records"][0]))
        self.save(self.root / "provider/batch_00001.parsed.json", parsed)
        with self.assertRaisesRegex(RuntimeError, "Duplicate generated"):
            self.freeze()

    def test_empty_rewrite_source_mismatch_and_bad_request_hash_fail(self):
        path = self.root / "provider/batch_00001.parsed.json"
        original = self.read(path)
        malformed = copy.deepcopy(original)
        malformed["records"][0]["confident"] = " \n"
        self.save(path, malformed)
        with self.assertRaisesRegex(RuntimeError, "nonempty"):
            self.freeze()
        self.save(path, original)
        self.sources[50]["question"] = "Altered source"
        self.write_sources()
        with self.assertRaisesRegex(RuntimeError, "Source text"):
            self.freeze()
        self.sources[50] = self.source(51)
        self.write_sources()
        request_path = self.root / "provider/batch_00001.request.json"
        request = self.read(request_path)
        request["prompt"] += "Changed"
        self.save(request_path, request)
        with self.assertRaisesRegex(RuntimeError, "provenance mismatch"):
            self.freeze()

    def test_original_canary_must_be_verbatim_and_all_50_included(self):
        self.sources[0]["confident"] += "changed"
        self.write_sources()
        with self.assertRaisesRegex(RuntimeError, "canary triplet changed"):
            self.freeze()
        self.sources[0] = self.source(1)
        self.sources[49]["reuse_canary"] = False
        self.write_sources()
        with self.assertRaisesRegex(RuntimeError, "original 50"):
            self.freeze()

    def test_append_generation_keeps_existing_snapshot_and_pins_valid(self):
        selector = self.freeze()
        frozen_bytes = Path(selector["triplets_file"]).read_bytes()
        self.sources.append(self.source(66))
        self.write_sources()
        self.write_batch("provider/batch_00002", self.sources[-1:])
        self.assertEqual(self.freeze(), selector)
        self.assertEqual(Path(selector["triplets_file"]).read_bytes(), frozen_bytes)
        self.assertEqual(frozen.verify_snapshot(Path(selector["snapshot_dir"])), selector)

    def test_changed_snapshot_or_selected_provenance_fails_and_never_overwrites(self):
        selector = self.freeze()
        path = Path(selector["triplets_file"])
        original = path.read_bytes()
        path.write_bytes(original + b" ")
        with self.assertRaisesRegex(RuntimeError, "checksum mismatch"):
            self.freeze()
        self.assertEqual(path.read_bytes(), original + b" ")
        path.write_bytes(original)
        request_path = self.root / "provider/batch_00001.request.json"
        request_path.write_bytes(request_path.read_bytes() + b" ")
        with self.assertRaisesRegex(RuntimeError, "provenance checksum mismatch"):
            frozen.verify_snapshot(self.root / "FROZEN_00060.json")

    def test_source_cache_checksum_and_row_bound_to_snapshot(self):
        cache = self.root / "source_cache/page.json"
        self.save(cache, {"response": {"rows": [{"row_idx": 51, "row": self.sources[50]["raw_source_row"]}]}})
        self.sources[50].update(source_cache_file="source_cache/page.json",
                                source_cache_sha256=frozen.sha(cache.read_bytes()))
        self.write_sources()
        selector = self.freeze()
        manifest = self.read(Path(selector["manifest_file"]))
        self.assertTrue(any("source_cache" in entry["roles"] for entry in manifest["provider_files"]))
        cache.write_bytes(cache.read_bytes() + b" ")
        with self.assertRaisesRegex(RuntimeError, "provenance checksum"):
            frozen.verify_snapshot(self.root / "FROZEN_00060.json")

    def test_canary_cache_relative_pointer_may_relocate_to_same_file(self):
        canary_root = self.base / self.config["canary_private_dir"]
        cache = canary_root / "source_cache/page.json"
        self.save(cache, {"response": {"rows": [{"row_idx": 1, "row": self.sources[0]["raw_source_row"]}]}})
        digest = frozen.sha(cache.read_bytes())
        canary_path = canary_root / "review_final_v2/TRIPLETS_50.json"
        packet = self.read(canary_path)
        packet["triplets"][0].update(source_cache_file="source_cache/page.json", source_cache_sha256=digest)
        self.save(canary_path, packet)
        self.sources[0].update(source_cache_file="../canary/source_cache/page.json", source_cache_sha256=digest)
        self.write_sources()
        self.assertEqual(self.freeze()["count"], 60)

    def parquet_sources(self):
        try:
            import pyarrow as pa
            import pyarrow.parquet as pq
        except ImportError:
            self.skipTest("Local PyArrow environment is required for binary source fixtures")
        path = self.root / "source_cache/pinned_parquet/train_sft-fixture.parquet"
        path.parent.mkdir(parents=True, exist_ok=True)
        rows = []
        for index in (50, 51):
            source = self.sources[index]
            source["raw_source_row"]["prompt"] = source["question"]
            source["raw_source_row_sha256"] = frozen.sha(frozen.canonical(source["raw_source_row"]))
            rows.append(copy.deepcopy(source["raw_source_row"]))
        rows.extend([self.source(80)["raw_source_row"], self.source(81)["raw_source_row"]])
        pq.write_table(pa.Table.from_pylist(rows), path, row_group_size=2)
        digest = frozen.file_sha(path)
        for offset, index in enumerate((50, 51)):
            self.sources[index].update(source_cache_file=str(path.relative_to(self.root)),
                                       source_cache_sha256=digest, transport="pinned_parquet",
                                       source_shard_file="data/" + path.name,
                                       source_shard_row_offset=offset, split="train_sft",
                                       dataset_revision=self.config["dataset_revision"])
        self.write_sources()
        return path, pq

    def test_binary_parquet_is_pinned_and_only_selected_row_group_loaded_once(self):
        path, pq = self.parquet_sources()
        original_factory = pq.ParquetFile
        reads = []

        class TrackingParquet:
            def __init__(self, value):
                self.inner = original_factory(value)
                self.metadata = self.inner.metadata
                self.num_row_groups = self.inner.num_row_groups

            def read_row_group(self, group, **kwargs):
                reads.append(group)
                return self.inner.read_row_group(group, **kwargs)

        with mock.patch.object(pq, "ParquetFile", TrackingParquet), \
                mock.patch.object(subprocess, "run", side_effect=AssertionError("provider/account call")), \
                mock.patch.object(socket, "create_connection", side_effect=AssertionError("network call")):
            selector = self.freeze(52)
        self.assertEqual(reads, [0])
        packet = self.read(Path(selector["triplets_file"]))
        self.assertEqual(packet["triplets"][-1]["raw_source_row"], self.sources[51]["raw_source_row"])
        manifest = self.read(Path(selector["manifest_file"]))
        pins = [entry for entry in manifest["provider_files"] if entry["path"].endswith(".parquet")]
        self.assertEqual(len(pins), 1)
        self.assertEqual(pins[0]["sha256"], frozen.file_sha(path))
        self.assertEqual(frozen.verify_snapshot(self.root / "FROZEN_00052.json"), selector)

    def test_parquet_wrong_offset_row_shard_or_digest_fail_closed(self):
        path, _ = self.parquet_sources()
        original = copy.deepcopy(self.sources)
        for changes, pattern in (({"source_shard_row_offset": 3}, "Parquet source row changed"),
                                 ({"source_shard_row_offset": 40}, "out of range"),
                                 ({"source_shard_row_offset": -1}, "Invalid Parquet"),
                                 ({"source_shard_file": "data/other.parquet"}, "Invalid Parquet"),
                                 ({"source_cache_sha256": "0" * 64}, "checksum mismatch"),
                                 ({"split": "test_sft"}, "Invalid Parquet"),
                                 ({"dataset_revision": "changed"}, "revision changed")):
            with self.subTest(changes=changes):
                self.sources = copy.deepcopy(original)
                self.sources[50].update(changes)
                self.write_sources()
                with self.assertRaisesRegex(RuntimeError, pattern):
                    self.freeze(52)
                self.assertFalse((self.root / "FROZEN_00052.json").exists())
        self.sources = copy.deepcopy(original)
        self.write_sources()
        selector = self.freeze(52)
        with path.open("ab") as handle:
            handle.write(b"changed")
        with self.assertRaisesRegex(RuntimeError, "provenance checksum mismatch"):
            frozen.verify_snapshot(self.root / "FROZEN_00052.json")

    def test_duplicate_parquet_locator_rejected(self):
        self.parquet_sources()
        self.sources[51]["source_shard_row_offset"] = self.sources[50]["source_shard_row_offset"]
        self.write_sources()
        with self.assertRaisesRegex(RuntimeError, "Duplicate selected Parquet"):
            self.freeze(52)

    def test_exact_5000_not_batch_rounded_up(self):
        self.sources = [self.source(index) for index in range(1, 5006)]
        self.write_sources()
        self.write_batch("provider/batch_00001", self.sources[50:])
        selector = self.freeze(5000)
        packet = self.read(Path(selector["triplets_file"]))
        self.assertEqual(len(packet["triplets"]), 5000)
        self.assertEqual(packet["triplets"][-1]["review_id"], "HC5000")
        self.assertEqual(selector["count"], 5000)
        self.assertTrue((self.root / "FROZEN_05000.json").is_file())
        self.assertNotIn("HC5001", [row["review_id"] for row in packet["triplets"]])


if __name__ == "__main__":
    unittest.main()
