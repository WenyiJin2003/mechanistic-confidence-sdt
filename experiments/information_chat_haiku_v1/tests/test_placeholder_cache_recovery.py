"""Reviewed placeholder removal reuses complete cached text without provider work."""
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
from cache_recovery import (complete_missing, finalize_recovery, inspect_cached_batch,
                            prepare_recovery, validate_completed_recovery,
                            validate_completion_plan)
from run_expansion import (build_request_data, dump, file_sha, fingerprint,
                           request_record, sha)


class PlaceholderCacheRecoveryTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.batch = "batch_00632"
        self.prefix = self.root / "provider" / self.batch
        self.prompt = "Create confident and hesitant versions. Return exactly one record per supplied id."
        self.prompt_path = self.root / "prompt.txt"
        self.prompt_path.write_text(self.prompt, encoding="utf-8")
        self.config = {"model": "claude-haiku-5-5", "max_output_tokens": 10000,
                       "max_call_budget_usd": 0.12, "batch_size": 5,
                       "prompt_file": str(self.prompt_path)}
        self.sources = [{"review_id": f"HC{index:05d}", "source_id": f"synthetic-{index}",
                         "question": f"What is synthetic sample {index}?",
                         "original": f"Synthetic sample {index} contains two source facts."}
                        for index in range(3156, 3161)]
        self.ids = [row["review_id"] for row in self.sources]
        self.records = [{"id": row["review_id"], "status": "ok",
                         "confident": f"Sample {index}: café facts.\nThe second fact is direct.  ",
                         "hesitant": f"Sample {index} seems to contain café facts.\nThe second fact may hold.  ",
                         "reject_reason": None}
                        for index, row in enumerate(self.sources, start=1)]
        self.placeholder = {"id": self.ids[-1] + "_PLACEHOLDER_REMOVED", "status": "ok",
                            "confident": "", "hesitant": "", "reject_reason": None}
        self.request = {
            "request_sha256": fingerprint(self.config, self.prompt, self.sources),
            "model": self.config["model"], "prompt": self.prompt, "prompt_sha256": sha(self.prompt),
            "data": build_request_data(self.prompt, [request_record(row) for row in self.sources]),
        }
        dump(self.root / "SOURCES.json", self.sources)
        dump(self.root / "RUN_STATUS.json", {"state": "invalid_provider_output_no_retry",
             "detail": {"batch": self.batch}, "calls_without_final_cost": 0})
        for name in ("JOB.json", "CAMPAIGN_JOB.json"):
            dump(self.root / name, {"state": "finished", "pid": -1,
                                   "stop_reason": "invalid_provider_output_no_retry"})
        dump(self.prefix.with_suffix(".request.json"), self.request)
        self.write_payload([*self.records, self.placeholder])
        dump(self.prefix.with_suffix(".quota.json"), {
            "events": [{"status": "allowed", "isUsingOverage": False}]})
        self.prefix.with_suffix(".stderr.txt").write_text("", encoding="utf-8")
        dump(self.root / "provider" / "batch_00631.parsed.json", {
            "records": [{"id": "HC03155", "confident": "Previously cached direct text.",
                         "hesitant": "Previously cached tentative text."}]})
        dump(self.root / "provider_completions_batch_00179" / "batch_00001.raw.json", {
            "result": "Previously cached completion text.", "total_cost_usd": 0.001})
        self.provider = self.patch("run_expansion.provider_stream")
        self.provider.side_effect = AssertionError("Reviewed placeholder recovery must never call a provider")
        self.process = self.patch("cache_recovery.subprocess.run")
        self.process.side_effect = AssertionError("Complete cached output must never launch generation")
        self.preflight = self.patch("subscription_preflight.capture_subscription_preflight")
        self.preflight.side_effect = AssertionError("Cache-only recovery must not inspect an account")

    def patch(self, target, **kwargs):
        patcher = mock.patch(target, **kwargs)
        self.addCleanup(patcher.stop)
        return patcher.start()

    def write_payload(self, records):
        payload = json.dumps({"records": records}, ensure_ascii=False)
        self.raw = {"type": "result", "subtype": "success", "is_error": False,
                    "stop_reason": "end_turn", "modelUsage": {
                        self.config["model"]: {"outputTokens": 600}},
                    "result": payload, "total_cost_usd": 0.01}
        events = [{"type": "system", "subtype": "init", "model": self.config["model"]},
                  {"type": "assistant", "message": {"model": self.config["model"],
                       "content": [{"type": "text", "text": payload}]}}, self.raw]
        dump(self.prefix.with_suffix(".raw.json"), self.raw)
        self.prefix.with_suffix(".events.jsonl").write_text(
            "".join(json.dumps(event, ensure_ascii=False) + "\n" for event in events), encoding="utf-8")

    def snapshot(self):
        return {path: path.read_bytes() for path in self.root.rglob("*") if path.is_file()}

    def provider_bytes(self):
        return {path: path.read_bytes() for path in self.root.glob("provider*/*") if path.is_file()}

    def assert_no_provider_work(self):
        self.provider.assert_not_called()
        self.process.assert_not_called()
        self.preflight.assert_not_called()
        self.assertFalse((self.root / "WORKER_LOCK.json").exists())

    def prepare(self):
        return prepare_recovery(self.root, self.batch, self.config, allow_empty_placeholder=True)

    def finish(self):
        plan_path = self.prepare()
        return plan_path, finalize_recovery(self.root, plan_path, self.config)

    def test_default_paths_still_reject_unknown_ids_without_writing_a_recovery(self):
        before = self.snapshot()
        for operation in (inspect_cached_batch, prepare_recovery, complete_missing):
            with self.subTest(operation=operation.__name__):
                with self.assertRaises(RuntimeError):
                    operation(self.root, self.batch, self.config)
                self.assertEqual(self.snapshot(), before)
                self.assert_no_provider_work()
        self.assertFalse((self.root / "CACHE_RECOVERIES").exists())
        self.assertFalse(self.prefix.with_suffix(".parsed.json").exists())

    def test_explicit_inspection_retains_all_five_records_and_identifies_no_missing_ids(self):
        before = self.snapshot()
        inspected = inspect_cached_batch(self.root, self.batch, self.config, allow_empty_placeholder=True)
        self.assertEqual(inspected["expected_ids"], self.ids)
        self.assertEqual(inspected["cached_ids"], self.ids)
        self.assertEqual(inspected["missing_ids"], [])
        self.assertEqual(inspected["cached_records"], self.records)
        metadata = inspected["reviewed_empty_placeholder_normalization"]
        self.assertEqual(metadata["normalization"], "reviewed_empty_placeholder_only")
        self.assertEqual(metadata["discarded_index"], 5)
        self.assertEqual(metadata["discarded_id"], self.placeholder["id"])
        self.assertEqual(metadata["returned_ids"], [*self.ids, self.placeholder["id"]])
        self.assertIs(metadata["cached_text_changed"], False)
        self.assertEqual(metadata["additional_provider_calls"], 0)
        self.assertRegex(metadata["discarded_payload_sha256"], r"^[0-9a-f]{64}$")
        originals = {path: data for path, data in before.items()
                     if path.parent == self.prefix.parent and path.name.startswith(self.batch + ".")}
        self.assertEqual(inspected["original_file_sha256"], {
            str(path.relative_to(self.root)): hashlib.sha256(data).hexdigest()
            for path, data in originals.items()})
        self.assertEqual(self.snapshot(), before)
        self.assert_no_provider_work()

    def test_reviewed_plan_binds_kind_metadata_and_all_previous_provider_bytes(self):
        before = self.provider_bytes()
        plan_path = self.prepare()
        plan = json.loads(plan_path.read_text())
        self.assertEqual(plan["recovery_kind"], "reviewed_empty_placeholder")
        self.assertEqual(plan["cached_ids"], self.ids)
        self.assertEqual(plan["cached_records"], self.records)
        self.assertEqual(plan["ids"], [])
        self.assertEqual(plan["missing_ids"], [])
        self.assertEqual(plan["preserved_provider_file_sha256"], {
            str(path.relative_to(self.root)): hashlib.sha256(data).hexdigest()
            for path, data in before.items()})
        self.assertEqual(validate_completion_plan(self.root, plan, self.config)["cached_records"], self.records)
        self.assertEqual(self.provider_bytes(), before)
        self.assert_no_provider_work()

    def test_finalize_and_completed_validation_preserve_exact_text_with_no_generation(self):
        original_provider = self.provider_bytes()
        plan_path, manifest_path = self.finish()
        plan = json.loads(plan_path.read_text())
        manifest = validate_completed_recovery(self.root, manifest_path, self.config)
        parsed_path = self.prefix.with_suffix(".parsed.json")
        parsed = json.loads(parsed_path.read_text())
        metadata = plan["reviewed_empty_placeholder_normalization"]
        for value in (plan, manifest, parsed):
            self.assertEqual(value["recovery_kind"], "reviewed_empty_placeholder")
            self.assertEqual(value["reviewed_empty_placeholder_normalization"], metadata)
        self.assertEqual(manifest["cached_ids"], self.ids)
        self.assertEqual(manifest["completed_missing_ids"], [])
        self.assertEqual(manifest["parsed_file_sha256"], file_sha(parsed_path))
        self.assertIs(manifest["no_cached_text_regenerated"], True)
        self.assertIs(manifest["new_pairs_human_certified"], False)
        self.assertIs(parsed["recovered_from_cached_partial_output"], False)
        self.assertEqual(parsed["cached_ids_reused_verbatim"], self.ids)
        self.assertEqual(parsed["only_missing_ids_submitted"], [])
        self.assertEqual([row["id"] for row in parsed["records"]], self.ids)
        for saved, original in zip(parsed["records"], self.records):
            for field in ("id", "status", "confident", "hesitant", "reject_reason"):
                self.assertEqual(saved[field], original[field])
            self.assertEqual(saved["generation_cache_source"], f"provider/{self.batch}.raw.json")
            self.assertIs(saved["human_review_completed"], False)
        for path, data in original_provider.items():
            self.assertEqual(path.read_bytes(), data)
        self.assertFalse((self.root / f"provider_completions_{self.batch}").exists())
        before_validation = self.snapshot()
        self.assertEqual(validate_completed_recovery(self.root, manifest_path, self.config), manifest)
        self.assertEqual(finalize_recovery(self.root, plan_path, self.config), manifest_path)
        self.assertEqual(self.snapshot(), before_validation)
        self.assert_no_provider_work()

    def test_complete_missing_with_explicit_review_is_entirely_cache_only(self):
        before = self.provider_bytes()
        manifest_path = complete_missing(self.root, self.batch, self.config, allow_empty_placeholder=True)
        manifest = validate_completed_recovery(self.root, manifest_path, self.config)
        self.assertEqual(manifest["cached_ids"], self.ids)
        self.assertEqual(manifest["completed_missing_ids"], [])
        self.assertEqual(manifest["recovery_kind"], "reviewed_empty_placeholder")
        for path, data in before.items():
            self.assertEqual(path.read_bytes(), data)
        self.assert_no_provider_work()

    def test_explicit_review_does_not_allow_other_unknown_ids_or_nonempty_placeholders(self):
        changes = [{"id": "OTHER_UNKNOWN_ID"}, {"confident": "Generated text."},
                   {"hesitant": "Generated text."}, {"status": "reject"},
                   {"reject_reason": "Not an empty placeholder."}]
        for change in changes:
            with self.subTest(change=change):
                self.write_payload([*self.records, {**self.placeholder, **change}])
                before = self.snapshot()
                with self.assertRaises(RuntimeError):
                    self.prepare()
                self.assertEqual(self.snapshot(), before)
                self.assert_no_provider_work()

    def test_placeholder_review_requires_all_five_real_ids_in_original_order(self):
        reordered = [self.records[1], self.records[0], *self.records[2:]]
        duplicated = [self.records[0], self.records[0], *self.records[2:]]
        for records in (self.records[:-1], reordered, duplicated):
            with self.subTest(ids=[row["id"] for row in records]):
                self.write_payload([*records, self.placeholder])
                before = self.snapshot()
                with self.assertRaises(RuntimeError):
                    complete_missing(self.root, self.batch, self.config, allow_empty_placeholder=True)
                self.assertEqual(self.snapshot(), before)
                self.assert_no_provider_work()

    def test_placeholder_review_cannot_be_combined_with_identical_duplicate_recovery(self):
        before = self.snapshot()
        for operation in (inspect_cached_batch, prepare_recovery, complete_missing):
            with self.subTest(operation=operation.__name__):
                with self.assertRaises(RuntimeError):
                    operation(self.root, self.batch, self.config,
                              allow_empty_placeholder=True, allow_identical_duplicates=True)
                self.assertEqual(self.snapshot(), before)
                self.assert_no_provider_work()

    def test_plan_metadata_kind_hash_or_cached_record_tampering_blocks_finalization(self):
        plan_path = self.prepare()
        original = json.loads(plan_path.read_text())
        changed_records = copy.deepcopy(original["cached_records"])
        changed_records[0]["confident"] = "Changed cached text."
        changes = [("recovery_kind", "unknown_recovery"),
                   ("reviewed_empty_placeholder_normalization", {}),
                   ("original_file_sha256", {}), ("cached_records", changed_records),
                   ("cached_ids", self.ids[:-1]), ("ids", self.ids[:1])]
        for key, value in changes:
            with self.subTest(field=key):
                dump(plan_path, {**original, key: value})
                with self.assertRaises(RuntimeError):
                    finalize_recovery(self.root, plan_path, self.config)
                self.assertFalse(self.prefix.with_suffix(".parsed.json").exists())
                self.assert_no_provider_work()
        missing_metadata = copy.deepcopy(original)
        del missing_metadata["reviewed_empty_placeholder_normalization"]
        dump(plan_path, missing_metadata)
        with self.assertRaises(RuntimeError):
            finalize_recovery(self.root, plan_path, self.config)
        self.assertFalse(self.prefix.with_suffix(".parsed.json").exists())

    def test_each_original_attempt_file_remains_pinned_after_review(self):
        plan_path = self.prepare()
        for suffix in (".request.json", ".raw.json", ".events.jsonl", ".quota.json", ".stderr.txt"):
            path = self.prefix.with_suffix(suffix)
            original = path.read_bytes()
            with self.subTest(suffix=suffix):
                path.write_bytes(original + b"\n")
                try:
                    with self.assertRaises(RuntimeError):
                        finalize_recovery(self.root, plan_path, self.config)
                    self.assertFalse(self.prefix.with_suffix(".parsed.json").exists())
                    self.assert_no_provider_work()
                finally:
                    path.write_bytes(original)

    def test_completed_metadata_or_text_tampering_is_rejected_even_with_updated_parsed_hash(self):
        _, manifest_path = self.finish()
        parsed_path = self.prefix.with_suffix(".parsed.json")
        original_manifest = json.loads(manifest_path.read_text())
        original_parsed = json.loads(parsed_path.read_text())
        changed_records = copy.deepcopy(original_parsed["records"])
        changed_records[0]["hesitant"] = "Changed cached tentative text."
        for field, value in (("recovery_kind", "unknown_recovery"),
                             ("reviewed_empty_placeholder_normalization", {}),
                             ("records", changed_records)):
            with self.subTest(parsed_field=field):
                dump(parsed_path, {**original_parsed, field: value})
                dump(manifest_path, {**original_manifest, "parsed_file_sha256": file_sha(parsed_path)})
                before = self.snapshot()
                with self.assertRaises(RuntimeError):
                    validate_completed_recovery(self.root, manifest_path, self.config)
                self.assertEqual(self.snapshot(), before)
                self.assert_no_provider_work()
        dump(parsed_path, original_parsed)
        for field, value in (("recovery_kind", "unknown_recovery"),
                             ("reviewed_empty_placeholder_normalization", {}),
                             ("plan_sha256", "0" * 64), ("evidence_file_sha256", {})):
            with self.subTest(manifest_field=field):
                dump(manifest_path, {**original_manifest, field: value})
                before = self.snapshot()
                with self.assertRaises(RuntimeError):
                    validate_completed_recovery(self.root, manifest_path, self.config)
                self.assertEqual(self.snapshot(), before)
                self.assert_no_provider_work()


if __name__ == "__main__":
    unittest.main()
