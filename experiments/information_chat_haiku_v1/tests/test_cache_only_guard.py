"""Cache-only repair cannot cross into account inspection or generation."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))
from cache_recovery import (complete_missing, finalize_recovery, main, prepare_recovery,
                            validate_completed_recovery, validate_completion_plan)
from run_expansion import build_request_data, dump, file_sha, fingerprint, request_record, sha


class CacheOnlyGuardTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.batch = "batch_00632"
        self.prefix = self.root / "provider" / self.batch
        self.prompt = "Preserve source claims. Return exactly one record per id."
        prompt_path = self.root / "prompt.txt"
        prompt_path.write_text(self.prompt, encoding="utf-8")
        self.config = {"model": "claude-haiku-5-5", "batch_size": 5, "max_output_tokens": 10000,
                       "max_call_budget_usd": 0.12, "prompt_file": str(prompt_path)}
        self.sources = [{"review_id": f"HC{index}", "source_id": f"source-{index}",
                         "question": f"What is sample {index}?", "original": f"Sample {index} contains two facts."}
                        for index in range(3206, 3211)]
        self.ids = [row["review_id"] for row in self.sources]
        self.records = [{"id": row["review_id"], "status": "ok", "confident": row["original"],
                         "hesitant": row["original"].replace(" contains ", " may contain "), "reject_reason": None}
                        for row in self.sources]
        request = {"model": self.config["model"], "prompt": self.prompt, "prompt_sha256": sha(self.prompt),
                   "request_sha256": fingerprint(self.config, self.prompt, self.sources),
                   "data": build_request_data(self.prompt, [request_record(row) for row in self.sources])}
        dump(self.root / "SOURCES.json", self.sources)
        dump(self.root / "RUN_STATUS.json", {"state": "invalid_provider_output_no_retry"})
        for name in ("JOB.json", "CAMPAIGN_JOB.json"):
            dump(self.root / name, {"state": "finished", "pid": -1})
        dump(self.prefix.with_suffix(".request.json"), request)
        self.write_records([*self.records, self.records[-1]])
        dump(self.prefix.with_suffix(".quota.json"), {"events": [{"status": "allowed", "isUsingOverage": False}]})
        self.prefix.with_suffix(".stderr.txt").write_text("", encoding="utf-8")
        self.process = self.mock("cache_recovery.subprocess.run", side_effect=AssertionError("No subprocess allowed"))
        self.preflight = self.mock("subscription_preflight.capture_subscription_preflight",
                                   side_effect=AssertionError("No account inspection allowed"))
        self.provider = self.mock("run_expansion.provider_stream", side_effect=AssertionError("No provider allowed"))

    def mock(self, name, **kwargs):
        patcher = patch(name, **kwargs)
        self.addCleanup(patcher.stop)
        return patcher.start()

    def write_records(self, records):
        self.raw = {"type": "result", "subtype": "success", "is_error": False, "stop_reason": "end_turn",
                    "modelUsage": {self.config["model"]: {"outputTokens": 200}},
                    "result": json.dumps({"records": records}, ensure_ascii=False), "total_cost_usd": 0.01}
        dump(self.prefix.with_suffix(".raw.json"), self.raw)
        self.write_events(self.events(self.raw))

    def events(self, raw):
        return [{"type": "system", "subtype": "init"},
                {"type": "assistant", "message": {"model": self.config["model"],
                    "content": [{"type": "text", "text": raw["result"]}]}}, raw]

    def write_events(self, events):
        self.prefix.with_suffix(".events.jsonl").write_text(
            "".join(json.dumps(event, ensure_ascii=False) + "\n" for event in events), encoding="utf-8")

    def repair(self, **kwargs):
        return complete_missing(self.root, self.batch, self.config,
                                allow_identical_duplicates=True, cache_only=True, **kwargs)

    def assert_no_calls(self):
        self.process.assert_not_called()
        self.preflight.assert_not_called()
        self.provider.assert_not_called()
        self.assertFalse((self.root / "WORKER_LOCK.json").exists())

    def test_full_cache_repair_binds_complete_attempt_inventory_and_is_idempotent(self):
        before = {path: path.read_bytes() for path in self.root.glob("provider*/*") if path.is_file()}
        manifest_path = self.repair()
        manifest = validate_completed_recovery(self.root, manifest_path, self.config)
        plan_path = self.root / manifest["plan_file"]
        plan = json.loads(plan_path.read_text())
        parsed = json.loads(self.prefix.with_suffix(".parsed.json").read_text())
        expected = {str(path.relative_to(self.root)): file_sha(path) for path in before}
        for value in (plan, manifest, parsed):
            self.assertIs(value["cache_only"], True)
            self.assertEqual(value["cache_only_artifact_file_sha256"], expected)
        self.assertEqual(manifest["completed_missing_ids"], [])
        self.assertEqual(manifest["evidence_file_sha256"], expected)
        self.assertIs(parsed["recovered_from_cached_partial_output"], False)
        self.assertEqual([row["id"] for row in parsed["records"]], self.ids)
        for row, original in zip(parsed["records"], self.records):
            for key, value in original.items():
                self.assertEqual(row[key], value)
        files = {path: path.read_bytes() for path in self.root.rglob("*") if path.is_file()}
        self.assertEqual(self.repair(), manifest_path)
        self.assertEqual({path: path.read_bytes() for path in self.root.rglob("*") if path.is_file()}, files)
        for path, content in before.items():
            self.assertEqual(path.read_bytes(), content)
        self.assert_no_calls()

    def test_missing_record_is_rejected_before_any_preflight_or_provider_even_with_duplicate_mode(self):
        self.write_records([*self.records[:4], self.records[3]])
        with self.assertRaisesRegex(RuntimeError, "every expected record"):
            self.repair()
        self.assertFalse(self.prefix.with_suffix(".parsed.json").exists())
        self.assert_no_calls()

    def test_successful_raw_does_not_override_mismatched_or_unsafe_stream(self):
        good = self.events(self.raw)
        candidates = []
        changed = copy.deepcopy(good)
        changed[1]["message"]["content"][0]["text"] = json.dumps({"records": self.records})
        candidates.append(changed)
        changed = copy.deepcopy(good)
        changed[-1]["is_error"] = True
        candidates.append(changed)
        candidates.extend([
            [good[0], {"type": "assistant", "error": "Usage Policy refusal"}, *good[1:]],
            [good[0], {"type": "api_retry"}, *good[1:]],
            [good[0], {"type": "rate_limit_event", "rate_limit_info": {"status": "rejected"}}, *good[1:]],
            [good[0], {"type": "rate_limit_event", "rate_limit_info": {"status": "allowed", "isUsingOverage": True}}, *good[1:]],
        ])
        for events in candidates:
            with self.subTest(events=events):
                self.write_events(events)
                plan_path = self.root / "CACHE_RECOVERIES" / f"{self.batch}.plan.json"
                plan_path.unlink(missing_ok=True)
                with self.assertRaises(RuntimeError):
                    self.repair()
                self.assertFalse(self.prefix.with_suffix(".parsed.json").exists())
                self.assert_no_calls()

    def test_full_valid_cache_without_normalization_can_use_the_same_no_generation_guard(self):
        self.write_records(self.records)
        manifest_path = complete_missing(self.root, self.batch, self.config, cache_only=True)
        manifest = validate_completed_recovery(self.root, manifest_path, self.config)
        self.assertIs(manifest["cache_only"], True)
        self.assertNotIn("recovery_kind", manifest)
        self.assertEqual(manifest["cached_ids"], self.ids)
        self.assert_no_calls()

    def test_placeholder_cache_only_path_has_the_same_bound_inventory(self):
        placeholder = {"id": self.ids[-1] + "_PLACEHOLDER_REMOVED", "status": "ok",
                       "confident": "", "hesitant": "", "reject_reason": None}
        self.write_records([*self.records, placeholder])
        manifest_path = complete_missing(self.root, self.batch, self.config,
                                         allow_empty_placeholder=True, cache_only=True)
        manifest = validate_completed_recovery(self.root, manifest_path, self.config)
        self.assertEqual(manifest["recovery_kind"], "reviewed_empty_placeholder")
        self.assertIs(manifest["cache_only"], True)
        self.assertEqual(len(manifest["cache_only_artifact_file_sha256"]), 5)
        self.assert_no_calls()

    def test_changed_optional_files_new_inventory_or_tampered_plan_binding_reject(self):
        manifest_path = self.repair()
        manifest = json.loads(manifest_path.read_text())
        plan = json.loads((self.root / manifest["plan_file"]).read_text())
        for suffix in (".quota.json", ".stderr.txt"):
            path = self.prefix.with_suffix(suffix)
            original = path.read_bytes()
            with self.subTest(suffix=suffix):
                path.write_bytes(original + b"\n")
                with self.assertRaises(RuntimeError):
                    validate_completion_plan(self.root, plan, self.config)
                path.write_bytes(original)
        for changed in [{**plan, "cache_only": False}, {**plan, "cache_only": 1},
                        {key: value for key, value in plan.items() if key != "cache_only"},
                        {**plan, "cache_only_artifact_file_sha256": {}}]:
            with self.subTest(changed=changed):
                with self.assertRaises(RuntimeError):
                    validate_completion_plan(self.root, changed, self.config)
        extra = self.prefix.with_suffix(".error.json")
        dump(extra, {})
        with self.assertRaises(RuntimeError):
            validate_completed_recovery(self.root, manifest_path, self.config)
        extra.unlink()
        self.assert_no_calls()

    def test_parsed_and_manifest_cache_only_metadata_are_verified_not_just_plan_hashes(self):
        manifest_path = self.repair()
        manifest = json.loads(manifest_path.read_text())
        parsed_path = self.prefix.with_suffix(".parsed.json")
        parsed = json.loads(parsed_path.read_text())
        for field, value in [("cache_only", False), ("cache_only", 1), ("cache_only_artifact_file_sha256", {})]:
            with self.subTest(field=field, value=value):
                dump(manifest_path, {**manifest, field: value})
                with self.assertRaises(RuntimeError):
                    validate_completed_recovery(self.root, manifest_path, self.config)
                dump(parsed_path, {**parsed, field: value})
                dump(manifest_path, {**manifest, "parsed_file_sha256": file_sha(parsed_path)})
                with self.assertRaises(RuntimeError):
                    validate_completed_recovery(self.root, manifest_path, self.config)
                dump(parsed_path, parsed)
        dump(manifest_path, manifest)
        self.assert_no_calls()

    def test_a_bound_cache_only_plan_cannot_fall_through_to_generation_on_later_default_call(self):
        manifest_path = self.repair()
        self.assertEqual(complete_missing(self.root, self.batch, self.config,
                                         allow_identical_duplicates=True), manifest_path)
        self.assert_no_calls()

    def test_legacy_completed_recovery_is_not_silently_rewritten_as_cache_only(self):
        manifest_path = complete_missing(self.root, self.batch, self.config, allow_identical_duplicates=True)
        before = {path: path.read_bytes() for path in self.root.rglob("*") if path.is_file()}
        with self.assertRaisesRegex(RuntimeError, "already completed legacy"):
            self.repair()
        self.assertEqual({path: path.read_bytes() for path in self.root.rglob("*") if path.is_file()}, before)
        self.assertNotIn("cache_only", json.loads(manifest_path.read_text()))
        self.assert_no_calls()

    def test_cache_only_requires_complete_missing_before_reading_configuration(self):
        with patch.object(sys, "argv", ["cache_recovery.py", "--batch", self.batch, "--cache-only"]), \
                patch("cache_recovery.load") as read:
            with self.assertRaises(SystemExit) as raised:
                main()
        self.assertEqual(raised.exception.code, 2)
        read.assert_not_called()
        self.assert_no_calls()


if __name__ == "__main__":
    unittest.main()
