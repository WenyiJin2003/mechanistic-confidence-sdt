"""Explicit cache-only recovery may add writer status metadata without changing text."""
import copy
import hashlib
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from unittest import mock

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))
import cache_recovery as recovery
from run_expansion import (build_request_data, dump, file_sha, fingerprint,
                           parse_generation_response, request_record, sha)

METADATA = "missing_status_metadata_normalization"


class MissingStatusCacheRecoveryTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.batch = "batch_00847"
        self.prefix = self.root / "provider" / self.batch
        self.prompt = "Preserve source claims. OUTPUT CONTRACT V3 Return exactly one record per supplied id."
        self.prompt_path = self.root / "prompt.txt"
        self.prompt_path.write_text(self.prompt, encoding="utf-8")
        self.config = {"model": "claude-haiku-5-5", "max_output_tokens": 10000,
                       "max_call_budget_usd": 0.12, "batch_size": 5,
                       "prompt_file": str(self.prompt_path), "private_dir": str(self.root)}
        self.sources = [{"review_id": f"HC{index:05d}", "source_id": f"synthetic-{index}",
                         "question": f"What is synthetic sample {index}?",
                         "original": f"Synthetic sample {index} contains test facts."}
                        for index in range(4231, 4236)]
        self.ids = [row["review_id"] for row in self.sources]
        self.records = [{"id": row["review_id"],
                         "confident": f"Sample {index} contains café facts.\nThe conclusion follows.  ",
                         "hesitant": f"Sample {index} may contain café facts.\nThe conclusion seems to follow.  ",
                         "reject_reason": None}
                        for index, row in enumerate(self.sources, start=1)]
        self.normalized = [{**row, "status": "ok"} for row in self.records]
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
        self.payload = {"records": self.records,
                        "required_output": copy.deepcopy(self.request["data"]["required_output"])}
        self.write_payload(self.payload)
        dump(self.prefix.with_suffix(".quota.json"), {
            "events": [{"status": "allowed", "isUsingOverage": False}]})
        self.prefix.with_suffix(".stderr.txt").write_text("", encoding="utf-8")
        dump(self.root / "provider" / "batch_00846.parsed.json", {
            "records": [{"id": "HC04230", "confident": "Previously cached direct text.",
                         "hesitant": "Previously cached tentative text."}]})
        dump(self.root / "provider_completions_batch_00179" / "batch_00001.raw.json", {
            "result": "Previously cached completion text.", "total_cost_usd": 0.001})
        self.provider = self.patch("run_expansion.provider_stream",
                                   side_effect=AssertionError("No provider calls in cache-only recovery tests"))
        self.process = self.patch("cache_recovery.subprocess.run",
                                  side_effect=AssertionError("No subprocess in cache-only recovery tests"))
        self.preflight = self.patch("subscription_preflight.capture_subscription_preflight",
                                    side_effect=AssertionError("No account inspection in cache-only recovery tests"))

    def patch(self, target, **kwargs):
        patcher = mock.patch(target, **kwargs)
        self.addCleanup(patcher.stop)
        return patcher.start()

    def write_payload(self, payload):
        text = json.dumps(payload, ensure_ascii=False)
        self.raw = {"type": "result", "subtype": "success", "is_error": False,
                    "stop_reason": "end_turn", "modelUsage": {
                        self.config["model"]: {"outputTokens": 600}},
                    "result": text, "total_cost_usd": 0.01}
        self.events = [{"type": "system", "subtype": "init", "model": self.config["model"]},
                       {"type": "assistant", "message": {"model": self.config["model"],
                            "content": [{"type": "text", "text": text}]}}, self.raw]
        dump(self.prefix.with_suffix(".raw.json"), self.raw)
        self.write_events(self.events)

    def write_events(self, events):
        self.prefix.with_suffix(".events.jsonl").write_text(
            "".join(json.dumps(event, ensure_ascii=False) + "\n" for event in events), encoding="utf-8")

    def snapshot(self):
        return {path: path.read_bytes() for path in self.root.rglob("*") if path.is_file()}

    def provider_bytes(self):
        return {path: path.read_bytes() for path in self.root.glob("provider*/*") if path.is_file()}

    def assert_no_calls(self):
        self.provider.assert_not_called()
        self.process.assert_not_called()
        self.preflight.assert_not_called()
        self.assertFalse((self.root / "WORKER_LOCK.json").exists())

    def inspect(self):
        return recovery.inspect_cached_batch(self.root, self.batch, self.config,
                                             allow_missing_status_metadata=True)

    def prepare(self):
        return recovery.prepare_recovery(self.root, self.batch, self.config,
                                         allow_missing_status_metadata=True)

    def finish(self):
        return recovery.complete_missing(self.root, self.batch, self.config,
                                          allow_missing_status_metadata=True, cache_only=True)

    def test_default_inspection_generation_parser_and_recovery_still_reject_missing_status(self):
        before = self.snapshot()
        operations = [lambda: recovery.inspect_cached_batch(self.root, self.batch, self.config),
                      lambda: recovery.prepare_recovery(self.root, self.batch, self.config),
                      lambda: recovery.complete_missing(self.root, self.batch, self.config, cache_only=True),
                      lambda: parse_generation_response(self.raw, self.ids, self.config)]
        for operation in operations:
            with self.subTest(operation=operation):
                with self.assertRaises((RuntimeError, KeyError)):
                    operation()
                self.assertEqual(self.snapshot(), before)
                self.assert_no_calls()
        self.assertFalse((self.root / "CACHE_RECOVERIES").exists())

    def test_explicit_inspection_adds_only_status_and_retains_all_five_ids_without_missing_rows(self):
        before = self.snapshot()
        observed = self.inspect()
        self.assertEqual(observed["expected_ids"], self.ids)
        self.assertEqual(observed["cached_ids"], self.ids)
        self.assertEqual(observed["missing_ids"], [])
        self.assertEqual(observed["cached_records"], self.normalized)
        metadata = observed[METADATA]
        self.assertEqual(metadata["normalization"], "reviewed_missing_status_metadata_only")
        self.assertEqual(metadata["added_field"], "status")
        self.assertEqual(metadata["added_value"], "ok")
        self.assertEqual(metadata["added_field_ids"], self.ids)
        self.assertEqual(metadata["inference_basis"], "nonempty paired texts with null reject_reason")
        self.assertEqual(metadata["echo_variant"], "full_request_echo")
        for field in ("original_payload_semantic_sha256", "normalized_payload_semantic_sha256"):
            self.assertRegex(metadata[field], r"^[0-9a-f]{64}$")
        self.assertNotEqual(metadata["original_payload_semantic_sha256"], metadata["normalized_payload_semantic_sha256"])
        for field in ("writer_schema_metadata_only", "raw_terminal_preserved"):
            self.assertIs(metadata[field], True)
        for field in ("confidence_correctness_or_human_approval_claimed", "cached_text_changed"):
            self.assertIs(metadata[field], False)
        self.assertEqual(metadata["additional_provider_calls"], 0)
        original_attempt = {path: data for path, data in before.items()
                            if path.parent == self.prefix.parent and path.name.startswith(self.batch + ".")}
        self.assertEqual(observed["original_file_sha256"], {
            str(path.relative_to(self.root)): hashlib.sha256(data).hexdigest()
            for path, data in original_attempt.items()})
        self.assertEqual(self.snapshot(), before)
        self.assert_no_calls()

    def test_completion_requires_cache_only_before_any_mutation_or_account_access(self):
        before = self.snapshot()
        with self.assertRaisesRegex(RuntimeError, "cache.only"):
            recovery.complete_missing(self.root, self.batch, self.config, allow_missing_status_metadata=True)
        self.assertEqual(self.snapshot(), before)
        self.assert_no_calls()

    def test_cli_completion_requires_cache_only_before_reading_configuration(self):
        argv = ["cache_recovery.py", "--batch", self.batch, "--complete-missing",
                "--reviewed-missing-status-metadata"]
        with mock.patch.object(sys, "argv", argv), mock.patch.object(recovery, "load") as read, \
                redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as raised:
                recovery.main()
        self.assertEqual(raised.exception.code, 2)
        read.assert_not_called()
        self.assert_no_calls()

    def test_reviewed_plan_has_cache_only_provenance_and_pins_all_previous_provider_bytes(self):
        before = self.provider_bytes()
        plan_path = self.prepare()
        plan = json.loads(plan_path.read_text())
        self.assertEqual(plan["recovery_kind"], "reviewed_missing_status_metadata")
        self.assertIs(plan["cache_only"], True)
        self.assertEqual(plan["cached_records"], self.normalized)
        self.assertEqual(plan["cached_ids"], self.ids)
        self.assertEqual(plan["ids"], [])
        self.assertEqual(plan["missing_ids"], [])
        self.assertEqual(plan["preserved_provider_file_sha256"], {
            str(path.relative_to(self.root)): hashlib.sha256(data).hexdigest()
            for path, data in before.items()})
        observed = recovery.validate_completion_plan(self.root, plan, self.config)
        self.assertEqual(plan["cache_only_artifact_file_sha256"], observed["original_file_sha256"])
        self.assertEqual(plan[METADATA], observed[METADATA])
        self.assertEqual(self.provider_bytes(), before)
        self.assert_no_calls()

    def test_full_recovery_preserves_exact_text_and_all_old_provider_bytes_and_is_idempotent(self):
        before = self.provider_bytes()
        manifest_path = self.finish()
        manifest = recovery.validate_completed_recovery(self.root, manifest_path, self.config)
        plan_path = self.root / manifest["plan_file"]
        plan = json.loads(plan_path.read_text())
        parsed_path = self.prefix.with_suffix(".parsed.json")
        parsed = json.loads(parsed_path.read_text())
        for value in (plan, manifest, parsed):
            self.assertEqual(value["recovery_kind"], "reviewed_missing_status_metadata")
            self.assertEqual(value[METADATA], plan[METADATA])
            self.assertIs(value["cache_only"], True)
            self.assertEqual(value["cache_only_artifact_file_sha256"], plan["original_file_sha256"])
        self.assertEqual(manifest["cached_ids"], self.ids)
        self.assertEqual(manifest["completed_missing_ids"], [])
        self.assertIs(manifest["no_cached_text_regenerated"], True)
        self.assertIs(manifest["new_pairs_human_certified"], False)
        self.assertIs(parsed["recovered_from_cached_partial_output"], False)
        self.assertEqual(parsed["cached_ids_reused_verbatim"], self.ids)
        self.assertEqual(parsed["only_missing_ids_submitted"], [])
        for saved, original in zip(parsed["records"], self.records):
            self.assertEqual(saved["status"], "ok")
            for field, value in original.items():
                self.assertEqual(saved[field], value)
            self.assertIs(saved["human_review_completed"], False)
            self.assertEqual(saved["generation_cache_source"], f"provider/{self.batch}.raw.json")
        self.assertEqual(len(parsed["records"]), 5)
        for path, data in before.items():
            self.assertEqual(path.read_bytes(), data)
        self.assertFalse((self.root / f"provider_completions_{self.batch}").exists())
        completed = self.snapshot()
        self.assertEqual(self.finish(), manifest_path)
        self.assertEqual(recovery.finalize_recovery(self.root, plan_path, self.config), manifest_path)
        self.assertEqual(self.snapshot(), completed)
        self.assert_no_calls()

    def test_count_only_contract_echo_is_explicitly_recorded_and_still_recovers_all_exact_ids(self):
        self.write_payload({"records": self.records, "required_output": {"record_count": 5}})
        self.assertEqual(self.inspect()[METADATA]["echo_variant"], "record_count_only")
        manifest_path = self.finish()
        manifest = recovery.validate_completed_recovery(self.root, manifest_path, self.config)
        self.assertEqual(manifest[METADATA]["echo_variant"], "record_count_only")
        self.assertEqual(manifest["cached_ids"], self.ids)
        self.assertEqual(manifest["completed_missing_ids"], [])
        self.assert_no_calls()

    def test_status_inference_does_not_accept_other_schema_text_or_id_changes(self):
        changed_record_sets = []
        for change in ({"status": None}, {"status": "ok"}, {"reject_reason": ""},
                       {"confident": "  "}, {"hesitant": None}, {"id": "UNKNOWN"}, {"extra": True}):
            records = copy.deepcopy(self.records)
            records[0].update(change)
            changed_record_sets.append(records)
        changed_record_sets.extend((self.records[:-1], [self.records[1], self.records[0], *self.records[2:]],
                                    [self.records[0], self.records[0], *self.records[2:]]))
        for records in changed_record_sets:
            with self.subTest(records=records):
                self.write_payload({**self.payload, "records": records})
                before = self.snapshot()
                with self.assertRaises(RuntimeError):
                    self.finish()
                self.assertEqual(self.snapshot(), before)
                self.assert_no_calls()

    def test_missing_conflicting_or_unknown_contract_echo_fails_closed(self):
        echoes = [None, {}, {"record_count": 4}, {"record_count": True},
                  {"record_count": 5, "extra": True},
                  {"record_count": 5, "expected_ids": list(reversed(self.ids))}]
        for echo in echoes:
            with self.subTest(echo=echo):
                self.write_payload({"records": self.records, "required_output": echo})
                before = self.snapshot()
                with self.assertRaises(RuntimeError):
                    self.inspect()
                self.assertEqual(self.snapshot(), before)
                self.assert_no_calls()

    def test_missing_status_mode_cannot_be_combined_with_other_reviewed_normalizations(self):
        for option in ("allow_identical_duplicates", "allow_empty_placeholder", "allow_local_budget_stream"):
            with self.subTest(option=option):
                before = self.snapshot()
                with self.assertRaises(RuntimeError):
                    recovery.inspect_cached_batch(self.root, self.batch, self.config,
                        allow_missing_status_metadata=True, **{option: True})
                self.assertEqual(self.snapshot(), before)
                self.assert_no_calls()

    def test_plan_metadata_hash_cached_records_or_cache_only_tampering_blocks_finalization(self):
        path = self.prepare()
        plan = json.loads(path.read_text())
        changed_records = copy.deepcopy(plan["cached_records"])
        changed_records[0]["confident"] = "Changed existing cached text."
        wrong_metadata = {**plan[METADATA], "cached_text_changed": 0}
        wrong_hash = {**plan[METADATA], "original_payload_semantic_sha256": "0" * 64}
        for field, value in (("recovery_kind", "unknown"), (METADATA, {}),
                             (METADATA, wrong_metadata), (METADATA, wrong_hash),
                             ("cached_records", changed_records), ("cache_only", False),
                             ("original_file_sha256", {}), ("cache_only_artifact_file_sha256", {})):
            with self.subTest(field=field, value=value):
                dump(path, {**plan, field: value})
                with self.assertRaises(RuntimeError):
                    recovery.finalize_recovery(self.root, path, self.config)
                self.assertFalse(self.prefix.with_suffix(".parsed.json").exists())
                self.assert_no_calls()

    def test_original_evidence_and_completed_metadata_or_text_cannot_be_tampered_with(self):
        manifest_path = self.finish()
        manifest = json.loads(manifest_path.read_text())
        parsed_path = self.prefix.with_suffix(".parsed.json")
        parsed = json.loads(parsed_path.read_text())
        for suffix in (".request.json", ".raw.json", ".events.jsonl", ".quota.json", ".stderr.txt"):
            path = self.prefix.with_suffix(suffix)
            original = path.read_bytes()
            with self.subTest(suffix=suffix):
                path.write_bytes(original + b"\n")
                try:
                    with self.assertRaises(RuntimeError):
                        recovery.validate_completed_recovery(self.root, manifest_path, self.config)
                    self.assert_no_calls()
                finally:
                    path.write_bytes(original)
        changed_records = copy.deepcopy(parsed["records"])
        changed_records[0]["hesitant"] = "Changed existing tentative text."
        for field, value in (("recovery_kind", "unknown"), (METADATA, {}),
                             ("cache_only", False), ("records", changed_records)):
            with self.subTest(parsed_field=field):
                dump(parsed_path, {**parsed, field: value})
                dump(manifest_path, {**manifest, "parsed_file_sha256": file_sha(parsed_path)})
                before = self.snapshot()
                with self.assertRaises(RuntimeError):
                    recovery.validate_completed_recovery(self.root, manifest_path, self.config)
                self.assertEqual(self.snapshot(), before)
                self.assert_no_calls()
        dump(parsed_path, parsed)
        for field, value in (("recovery_kind", "unknown"), (METADATA, {}),
                             ("cache_only", False), ("plan_sha256", "0" * 64)):
            with self.subTest(manifest_field=field):
                dump(manifest_path, {**manifest, field: value})
                with self.assertRaises(RuntimeError):
                    recovery.validate_completed_recovery(self.root, manifest_path, self.config)
                self.assert_no_calls()


if __name__ == "__main__":
    unittest.main()
