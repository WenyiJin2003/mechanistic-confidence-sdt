import copy
import hashlib
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))
from cache_recovery import (
    complete_missing,
    completion_prompt_text,
    finalize_recovery,
    inspect_cached_batch,
    prepare_recovery,
    validate_completed_recovery,
    validate_completion_plan,
)
from run_expansion import build_request_data, dump, fingerprint, request_record, sha
from run_campaign import prepare_cache_recovery_resume
from output_contract import normalize_identical_duplicates


def file_sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class CacheRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.batch_name = "batch_00167"
        self.prefix = self.root / "provider" / self.batch_name
        self.prompt = "Create confident and hesitant versions of each supplied response."
        self.prompt_path = self.root / "prompt.txt"
        self.prompt_path.write_text(self.prompt, encoding="utf-8")
        self.config = {
            "model": "claude-haiku-5-5",
            "max_output_tokens": 10000,
            "max_call_budget_usd": 0.12,
            "batch_size": 5,
            "prompt_file": str(self.prompt_path),
        }
        self.sources = [
            {
                "review_id": f"HC{number}",
                "source_id": f"synthetic-{number}",
                "question": f"What is sample {number}?",
                "original": f"Sample {number} is a synthetic test source.",
            }
            for number in range(881, 886)
        ]
        self.ids = [row["review_id"] for row in self.sources]
        self.records = [
            {
                "id": row["review_id"],
                "status": "ok",
                "confident": row["original"],
                "hesitant": row["original"].replace(" is ", " may be "),
                "reject_reason": None,
            }
            for row in self.sources
        ]
        dump(self.root / "SOURCES.json", self.sources)
        dump(self.root / "RUN_STATUS.json", {"state": "invalid_provider_output_no_retry"})
        dump(self.root / "JOB.json", {"state": "finished", "pid": -1})
        dump(self.root / "CAMPAIGN_JOB.json", {"state": "finished", "pid": -1})
        self.request = self.request_for(self.sources)
        dump(self.prefix.with_suffix(".request.json"), self.request)
        self.raw = self.envelope(self.records[:1])
        self.write_original_raw(self.raw)

    def request_for(self, sources, prompt=None, config=None):
        prompt = self.prompt if prompt is None else prompt
        config = self.config if config is None else config
        return {
            "request_sha256": fingerprint(config, prompt, sources),
            "model": config["model"],
            "prompt": prompt,
            "prompt_sha256": sha(prompt),
            "data": build_request_data(prompt, [request_record(row) for row in sources]),
        }

    def envelope(self, records):
        return {
            "type": "result",
            "subtype": "success",
            "is_error": False,
            "stop_reason": "end_turn",
            "modelUsage": {self.config["model"]: {"outputTokens": 120}},
            "result": json.dumps({"records": records}),
            "total_cost_usd": 0.01,
        }

    def write_original_raw(self, raw):
        dump(self.prefix.with_suffix(".raw.json"), raw)
        self.prefix.with_suffix(".events.jsonl").write_text(
            json.dumps(raw) + "\n", encoding="utf-8"
        )

    def original_bytes(self):
        return {
            path: path.read_bytes()
            for path in (self.root / "provider").glob("*")
            if path.suffix != ".pending"
        }

    def prepare_with_completion(self):
        plan_path = prepare_recovery(self.root, self.batch_name, self.config)
        plan = json.loads(plan_path.read_text())
        completion = self.root / plan["provider_dir"] / "batch_00001"
        request = self.request_for(self.sources[1:])
        dump(completion.with_suffix(".request.json"), request)
        dump(completion.with_suffix(".raw.json"), self.envelope(self.records[1:]))
        dump(
            completion.with_suffix(".parsed.json"),
            {
                "request_sha256": request["request_sha256"],
                "model": self.config["model"],
                "records": self.records[1:],
            },
        )
        return plan_path, completion

    def test_inspection_and_plan_preserve_the_cached_record_and_original_evidence(self):
        before = self.original_bytes()
        inspected = inspect_cached_batch(self.root, self.batch_name, self.config)
        self.assertEqual(inspected["expected_ids"], self.ids)
        self.assertEqual(inspected["cached_ids"], self.ids[:1])
        self.assertEqual(inspected["missing_ids"], self.ids[1:])
        self.assertEqual(inspected["cached_records"], self.records[:1])
        expected_pins = {
            str(path.relative_to(self.root)): hashlib.sha256(data).hexdigest()
            for path, data in before.items()
        }
        self.assertEqual(inspected["original_file_sha256"], expected_pins)

        plan_path = prepare_recovery(self.root, self.batch_name, self.config)
        plan = json.loads(plan_path.read_text())
        self.assertEqual(plan_path, self.root / "CACHE_RECOVERIES" / f"{self.batch_name}.plan.json")
        self.assertEqual(plan["ids"], self.ids[1:])
        self.assertEqual(plan["cached_records"], self.records[:1])
        self.assertEqual(plan["provider_dir"], "provider_completions_" + self.batch_name)
        self.assertEqual(plan["completion_prompt_file"], self.config["prompt_file"])
        self.assertEqual(plan["completion_prompt_sha256"], sha(self.prompt))
        self.assertEqual(plan["preserved_provider_file_sha256"], expected_pins)
        self.assertEqual(self.original_bytes(), before)

    def test_inspection_rejects_unsuccessful_or_malformed_cached_output(self):
        invalid_records = [
            [{**self.records[0], "id": "HC999"}],
            self.records[:1] * 2,
            [{**self.records[0], "status": "unknown"}],
            [{**self.records[0], "confident": ""}],
            [{**self.records[0], "hesitant": 42}],
            [{**self.records[0], "reject_reason": "Unexpected rejection reason."}],
            [{**self.records[0], "reject_reason": ""}],
        ]
        rejected = {"id": self.ids[0], "status": "reject", "confident": None, "hesitant": None}
        invalid_records.extend([
            [rejected],
            [{**rejected, "reject_reason": None}],
            [{**rejected, "reject_reason": "  "}],
            [{**rejected, "reject_reason": 42}],
            [{**rejected, "reject_reason": "Cannot preserve source.", "confident": "Existing text."}],
            [{**rejected, "reject_reason": "Cannot preserve source.", "hesitant": "Existing text."}],
        ])
        changes = [
            {"is_error": True},
            {"stop_reason": "refusal"},
            {"stop_reason": "max_tokens"},
            {"subtype": "error_max_budget_usd"},
            {"modelUsage": {"another-model": {"outputTokens": 120}}},
            *[{"result": json.dumps({"records": records})} for records in invalid_records],
        ]
        for change in changes:
            with self.subTest(change=change):
                self.write_original_raw({**self.raw, **change})
                with self.assertRaises(RuntimeError):
                    inspect_cached_batch(self.root, self.batch_name, self.config)

    def test_legacy_success_without_reject_reason_and_valid_rejection_remain_recoverable(self):
        legacy = dict(self.records[0])
        legacy.pop("reject_reason")
        rejected = {"id": self.ids[0], "status": "reject", "confident": None,
                    "hesitant": None, "reject_reason": "Cannot preserve all source claims."}
        for row in (legacy, rejected):
            with self.subTest(status=row["status"]):
                self.write_original_raw(self.envelope([row]))
                inspected = inspect_cached_batch(self.root, self.batch_name, self.config)
                self.assertEqual(inspected["cached_records"], [row])

    def test_inspection_binds_frozen_sources_prompt_and_request_fingerprint(self):
        changed_source = copy.deepcopy(self.sources)
        changed_source[0]["original"] = "A different source."
        changes = [
            ("source", changed_source),
            ("request", {**self.request, "request_sha256": "0" * 64}),
            ("request", {**self.request, "prompt": "A different instruction."}),
            ("request", {**self.request, "prompt_sha256": "1" * 64}),
            ("request", {**self.request, "model": "another-model"}),
            ("request", {**self.request, "data": {**self.request["data"], "unexpected": True}}),
        ]
        for kind, changed in changes:
            with self.subTest(kind=kind, changed=changed):
                dump(self.root / "SOURCES.json", self.sources)
                dump(self.prefix.with_suffix(".request.json"), self.request)
                destination = self.root / "SOURCES.json" if kind == "source" else self.prefix.with_suffix(".request.json")
                dump(destination, changed)
                with self.assertRaises(RuntimeError):
                    inspect_cached_batch(self.root, self.batch_name, self.config)

    def test_finalize_combines_only_missing_records_and_preserves_existing_text(self):
        before = self.original_bytes()
        plan_path, completion = self.prepare_with_completion()
        manifest_path = finalize_recovery(self.root, plan_path, self.config)
        manifest = json.loads(manifest_path.read_text())
        parsed_path = self.prefix.with_suffix(".parsed.json")
        parsed = json.loads(parsed_path.read_text())

        self.assertEqual(manifest_path, self.root / "CACHE_RECOVERIES" / f"{self.batch_name}.completed.json")
        self.assertIs(manifest["completed"], True)
        self.assertEqual(manifest["cached_ids"], self.ids[:1])
        self.assertEqual(manifest["completed_missing_ids"], self.ids[1:])
        self.assertEqual(manifest["parsed_file_sha256"], file_sha256(parsed_path))
        self.assertEqual(parsed["request_sha256"], self.request["request_sha256"])
        self.assertEqual([row["id"] for row in parsed["records"]], self.ids)
        self.assertEqual(parsed["records"][0]["confident"], self.records[0]["confident"])
        self.assertEqual(parsed["records"][0]["hesitant"], self.records[0]["hesitant"])
        self.assertEqual(
            parsed["records"][0]["generation_cache_source"],
            f"provider/{self.batch_name}.raw.json",
        )
        self.assertTrue(all(
            row["generation_cache_source"] == str(completion.with_suffix(".raw.json").relative_to(self.root))
            for row in parsed["records"][1:]
        ))
        for path, data in before.items():
            self.assertEqual(path.read_bytes(), data)
        self.assertEqual(
            validate_completed_recovery(self.root, manifest_path, self.config)["cached_ids"],
            self.ids[:1],
        )
        files_before_validation = {
            path: path.read_bytes() for path in self.root.rglob("*") if path.is_file()
        }
        validate_completed_recovery(self.root, manifest_path, self.config)
        self.assertEqual(
            {path: path.read_bytes() for path in self.root.rglob("*") if path.is_file()},
            files_before_validation,
        )
        self.assertTrue(completion.with_suffix(".raw.json").is_file())

    def test_finalize_rejects_completion_for_cached_ids_or_a_different_request(self):
        plan_path, completion = self.prepare_with_completion()
        request_path = completion.with_suffix(".request.json")
        parsed_path = completion.with_suffix(".parsed.json")
        raw_path = completion.with_suffix(".raw.json")
        baseline = {path: json.loads(path.read_text()) for path in (request_path, parsed_path, raw_path)}
        invalid_request = copy.deepcopy(baseline[request_path])
        invalid_request["data"]["records"][0]["original_response"] = "Changed source."
        invalid_prompt = {**baseline[request_path], "prompt": "Use different instructions."}
        invalid_prompt_hash = {**baseline[request_path], "prompt_sha256": "d" * 64}
        invalid_data = {**baseline[request_path], "data": {**baseline[request_path]["data"], "unexpected": True}}
        invalid_parsed = {**baseline[parsed_path], "request_sha256": "f" * 64}
        duplicate_parsed = {
            **baseline[parsed_path],
            "records": [*self.records[1:], self.records[1]],
        }
        changed = [
            (raw_path, self.envelope([self.records[0], *self.records[2:]])),
            (request_path, invalid_request),
            (request_path, invalid_prompt),
            (request_path, invalid_prompt_hash),
            (request_path, invalid_data),
            (parsed_path, invalid_parsed),
            (parsed_path, duplicate_parsed),
            (raw_path, {**baseline[raw_path], "modelUsage": {"another-model": {"outputTokens": 120}}}),
        ]
        for path, value in changed:
            with self.subTest(path=path.name, value=value):
                self.prefix.with_suffix(".parsed.json").unlink(missing_ok=True)
                (self.root / "CACHE_RECOVERIES" / f"{self.batch_name}.completed.json").unlink(missing_ok=True)
                for restore_path, original in baseline.items():
                    dump(restore_path, original)
                dump(path, value)
                with self.assertRaises(RuntimeError):
                    finalize_recovery(self.root, plan_path, self.config)
                self.assertFalse(self.prefix.with_suffix(".parsed.json").exists())

    def test_finalize_rejects_changed_original_evidence_after_planning(self):
        plan_path, _ = self.prepare_with_completion()
        for suffix in (".request.json", ".raw.json", ".events.jsonl"):
            path = self.prefix.with_suffix(suffix)
            original = path.read_bytes()
            with self.subTest(path=path.name):
                path.write_bytes(original + b"\n")
                with self.assertRaises(RuntimeError):
                    finalize_recovery(self.root, plan_path, self.config)
                self.assertFalse(self.prefix.with_suffix(".parsed.json").exists())
                path.write_bytes(original)

    def test_finalize_never_overwrites_an_existing_parsed_cache(self):
        plan_path, _ = self.prepare_with_completion()
        parsed_path = self.prefix.with_suffix(".parsed.json")
        dump(parsed_path, {
            "request_sha256": "e" * 64,
            "records": [],
            "sentinel": "an existing cache must survive",
        })
        before = parsed_path.read_bytes()
        with self.assertRaises(RuntimeError):
            finalize_recovery(self.root, plan_path, self.config)
        self.assertEqual(parsed_path.read_bytes(), before)

    def test_completed_validation_detects_manifest_and_provider_file_tampering(self):
        plan_path, completion = self.prepare_with_completion()
        manifest_path = finalize_recovery(self.root, plan_path, self.config)
        original_manifest = json.loads(manifest_path.read_text())
        files = [
            self.prefix.with_suffix(".parsed.json"),
            self.prefix.with_suffix(".raw.json"),
            completion.with_suffix(".raw.json"),
        ]
        for path in files:
            original = path.read_bytes()
            with self.subTest(path=path.name):
                path.write_bytes(original + b"\n")
                before = path.read_bytes()
                with self.assertRaises(RuntimeError):
                    validate_completed_recovery(self.root, manifest_path, self.config)
                self.assertEqual(path.read_bytes(), before)
                path.write_bytes(original)
        for field, value in (("completed", False), ("cached_ids", []), ("parsed_file_sha256", "0" * 64)):
            with self.subTest(field=field):
                dump(manifest_path, {**original_manifest, field: value})
                with self.assertRaises(RuntimeError):
                    validate_completed_recovery(self.root, manifest_path, self.config)
        dump(manifest_path, original_manifest)
        parsed_path = self.prefix.with_suffix(".parsed.json")
        original_parsed = json.loads(parsed_path.read_text())
        for field, value in (("request_sha256", "e" * 64), ("model", "another-model")):
            with self.subTest(parsed_field=field):
                dump(parsed_path, {**original_parsed, field: value})
                dump(manifest_path, {**original_manifest, "parsed_file_sha256": file_sha256(parsed_path)})
                with self.assertRaises(RuntimeError):
                    validate_completed_recovery(self.root, manifest_path, self.config)
        dump(parsed_path, original_parsed)
        dump(manifest_path, original_manifest)

    def migration_fixture(self):
        self.prompt += " Return exactly one record per supplied id."
        self.prompt_path.write_text(self.prompt, encoding="utf-8")
        self.request = self.request_for(self.sources)
        dump(self.prefix.with_suffix(".request.json"), self.request)
        next_prompt = self.prompt.split("Return exactly", 1)[0] + "Return exactly the complete batch. OUTPUT CONTRACT V3"
        next_path = self.root / "prompt_v3.txt"
        next_path.write_text(next_prompt, encoding="utf-8")
        config = {**self.config, "prompt_file": str(next_path),
                  "legacy_prompt_file": str(self.prompt_path), "legacy_prompt_boundary": 179}
        return config, next_path, next_prompt

    def test_format_only_migration_pins_completion_prompt_and_full_output_contract(self):
        config, next_path, next_prompt = self.migration_fixture()
        before = self.original_bytes()
        plan_path = prepare_recovery(self.root, self.batch_name, config)
        plan = json.loads(plan_path.read_text())
        self.assertEqual(plan["completion_prompt_file"], str(next_path))
        self.assertEqual(plan["completion_prompt_sha256"], sha(next_prompt))
        self.assertEqual(completion_prompt_text(plan, config), next_prompt)
        completion = self.root / plan["provider_dir"] / "batch_00001"
        request = self.request_for(self.sources[1:], prompt=next_prompt, config=config)
        self.assertEqual(request["data"]["required_output"], {"record_count": 4, "expected_ids": self.ids[1:]})
        dump(completion.with_suffix(".request.json"), request)
        dump(completion.with_suffix(".raw.json"), self.envelope(self.records[1:]))
        dump(completion.with_suffix(".parsed.json"), {
            "request_sha256": request["request_sha256"], "model": config["model"], "records": self.records[1:],
        })
        changed_request = copy.deepcopy(request)
        changed_request["data"]["required_output"]["record_count"] = 1
        dump(completion.with_suffix(".request.json"), changed_request)
        with self.assertRaises(RuntimeError):
            finalize_recovery(self.root, plan_path, config)
        dump(completion.with_suffix(".request.json"), request)
        manifest = finalize_recovery(self.root, plan_path, config)
        self.assertEqual(validate_completed_recovery(self.root, manifest, config)["cached_ids"], self.ids[:1])
        for path, data in before.items():
            self.assertEqual(path.read_bytes(), data)

    def test_bound_completion_prompt_rejects_pin_tampering_and_semantic_changes(self):
        config, next_path, next_prompt = self.migration_fixture()
        plan_path = prepare_recovery(self.root, self.batch_name, config)
        plan = json.loads(plan_path.read_text())
        next_path.write_text(next_prompt + " changed", encoding="utf-8")
        with self.assertRaisesRegex(RuntimeError, "Bound completion prompt changed"):
            validate_completion_plan(self.root, plan, config)
        next_path.write_text(next_prompt, encoding="utf-8")
        changed_semantics = "Change source facts. Return exactly a complete batch. OUTPUT CONTRACT V3"
        next_path.write_text(changed_semantics, encoding="utf-8")
        with self.assertRaisesRegex(RuntimeError, "semantic instructions"):
            validate_completion_plan(self.root, {**plan, "completion_prompt_sha256": sha(changed_semantics)}, config)
        next_path.write_text(next_prompt, encoding="utf-8")
        for key in ("completion_prompt_file", "completion_prompt_sha256"):
            incomplete = dict(plan)
            incomplete.pop(key)
            with self.assertRaisesRegex(RuntimeError, "Incomplete completion prompt binding"):
                validate_completion_plan(self.root, incomplete, config)

    def test_legacy_plan_uses_original_batch_prompt_after_migration(self):
        config, _, _ = self.migration_fixture()
        plan_path = prepare_recovery(self.root, self.batch_name, self.config)
        plan = json.loads(plan_path.read_text())
        plan.pop("completion_prompt_file")
        plan.pop("completion_prompt_sha256")
        dump(plan_path, plan)
        self.assertEqual(completion_prompt_text(plan, config), self.prompt)
        self.assertEqual(validate_completion_plan(self.root, plan, config)["cached_ids"], self.ids[:1])

    def test_complete_missing_preserves_cached_text_and_records_review_notes(self):
        plan_path, _ = self.prepare_with_completion()
        before = self.original_bytes()
        with patch("cache_recovery.subprocess.run") as provider, patch(
                "subscription_preflight.capture_subscription_preflight") as preflight:
            manifest = complete_missing(self.root, self.batch_name, self.config,
                                        content_review_notes={self.ids[0]: "Review this cached pair without rewriting."})
        provider.assert_not_called()
        preflight.assert_not_called()
        self.assertTrue(manifest.is_file())
        self.assertFalse((self.root / "WORKER_LOCK.json").exists())
        plan = json.loads(plan_path.read_text())
        self.assertIn(self.ids[0], plan["content_review_notes"])
        first = json.loads(self.prefix.with_suffix(".parsed.json").read_text())["records"][0]
        self.assertEqual(first["confident"], self.records[0]["confident"])
        self.assertEqual(first["hesitant"], self.records[0]["hesitant"])
        self.assertIn("content_preservation_review_required", first["audit_flags"]["hesitant"])
        for path, data in before.items():
            self.assertEqual(path.read_bytes(), data)

    def test_complete_missing_never_resubmits_a_saved_completion_attempt(self):
        plan_path = prepare_recovery(self.root, self.batch_name, self.config)
        plan = json.loads(plan_path.read_text())
        request = self.root / plan["provider_dir"] / "batch_00001.request.json"
        dump(request, self.request_for(self.sources[1:]))
        before = request.read_bytes()
        with patch("cache_recovery.subprocess.run") as provider, patch(
                "subscription_preflight.capture_subscription_preflight") as preflight:
            with self.assertRaisesRegex(RuntimeError, "never resubmit"):
                complete_missing(self.root, self.batch_name, self.config)
        provider.assert_not_called()
        preflight.assert_not_called()
        self.assertEqual(request.read_bytes(), before)
        self.assertFalse((self.root / "WORKER_LOCK.json").exists())

    def test_standalone_completion_rejects_live_unfinished_or_locked_jobs(self):
        self.prepare_with_completion()
        cases = [
            ("JOB.json", {"state": "running", "pid": -1}),
            ("CAMPAIGN_JOB.json", {"state": "failed", "pid": -1}),
            ("JOB.json", {"state": "finished", "pid": os.getpid()}),
            ("CAMPAIGN_JOB.json", {"state": "finished", "pid": os.getpid()}),
            ("CAMPAIGN_LOCK.json", {"pid": -1}),
            ("WORKER_LOCK.json", {"pid": -1}),
        ]
        for filename, value in cases:
            with self.subTest(filename=filename, value=value):
                dump(self.root / "JOB.json", {"state": "finished", "pid": -1})
                dump(self.root / "CAMPAIGN_JOB.json", {"state": "finished", "pid": -1})
                for name in ("CAMPAIGN_LOCK.json", "WORKER_LOCK.json"):
                    (self.root / name).unlink(missing_ok=True)
                dump(self.root / filename, value)
                with self.assertRaises(RuntimeError):
                    complete_missing(self.root, self.batch_name, self.config)

    def test_campaign_completion_requires_exact_lock_owner_and_finished_tranche(self):
        self.prepare_with_completion()
        owner = os.getpid()
        cases = [
            ({"pid": -1}, {"state": "running", "pid": owner}, {"state": "finished", "pid": owner}),
            ({"pid": owner}, {"state": "running", "pid": -1}, {"state": "finished", "pid": owner}),
            ({"pid": owner}, {"state": "finished", "pid": owner}, {"state": "finished", "pid": owner}),
            ({"pid": owner}, {"state": "running", "pid": owner}, {"state": "running", "pid": owner}),
        ]
        for lock, campaign, tranche in cases:
            with self.subTest(lock=lock, campaign=campaign, tranche=tranche):
                dump(self.root / "CAMPAIGN_LOCK.json", lock)
                dump(self.root / "CAMPAIGN_JOB.json", campaign)
                dump(self.root / "JOB.json", tranche)
                with self.assertRaises(RuntimeError):
                    complete_missing(self.root, self.batch_name, self.config, campaign_owned=True)
                self.assertFalse((self.root / "WORKER_LOCK.json").exists())
        dump(self.root / "CAMPAIGN_LOCK.json", {"pid": owner})
        dump(self.root / "CAMPAIGN_JOB.json", {"state": "running", "pid": owner})
        for tranche_pid in (owner, -1):
            with self.subTest(tranche_pid=tranche_pid):
                dump(self.root / "JOB.json", {"state": "finished", "pid": tranche_pid})
                with patch("cache_recovery.subprocess.run") as provider:
                    manifest = complete_missing(self.root, self.batch_name, self.config, campaign_owned=True)
                provider.assert_not_called()
                self.assertTrue(manifest.is_file())
                self.assertEqual(json.loads((self.root / "CAMPAIGN_LOCK.json").read_text())["pid"], owner)
                self.assertFalse((self.root / "WORKER_LOCK.json").exists())

    def test_identical_duplicate_recovery_is_explicit_cached_only_and_idempotent(self):
        returned = [*self.records, self.records[-1]]
        self.write_original_raw(self.envelope(returned))
        before = self.original_bytes()
        with self.assertRaises(RuntimeError):
            inspect_cached_batch(self.root, self.batch_name, self.config)
        observed = inspect_cached_batch(self.root, self.batch_name, self.config, allow_identical_duplicates=True)
        self.assertEqual(observed["cached_ids"], self.ids)
        self.assertEqual(observed["cached_records"], self.records)
        self.assertEqual(observed["missing_ids"], [])
        self.assertEqual(observed["identical_duplicate_normalization"], {
            "duplicate_ids": self.ids[-1:],
            "discarded_indices": [5],
            "returned_ids": [*self.ids, self.ids[-1]],
            "normalization": "identical_record_duplicates_only",
        })
        with patch("cache_recovery.subprocess.run") as provider, patch(
                "subscription_preflight.capture_subscription_preflight") as preflight:
            manifest_path = complete_missing(self.root, self.batch_name, self.config,
                                             allow_identical_duplicates=True)
            all_files = {path: path.read_bytes() for path in self.root.rglob("*") if path.is_file()}
            repeated = complete_missing(self.root, self.batch_name, self.config,
                                        allow_identical_duplicates=True)
        self.assertEqual(repeated, manifest_path)
        self.assertEqual({path: path.read_bytes() for path in self.root.rglob("*") if path.is_file()}, all_files)
        provider.assert_not_called()
        preflight.assert_not_called()
        manifest = json.loads(manifest_path.read_text())
        self.assertEqual(manifest["cached_ids"], self.ids)
        self.assertEqual(manifest["completed_missing_ids"], [])
        plan = json.loads((self.root / manifest["plan_file"]).read_text())
        self.assertEqual(plan["recovery_kind"], "identical_duplicate_records")
        self.assertEqual(plan["identical_duplicate_normalization"], observed["identical_duplicate_normalization"])
        self.assertEqual(manifest["recovery_kind"], plan["recovery_kind"])
        self.assertEqual(manifest["identical_duplicate_normalization"], plan["identical_duplicate_normalization"])
        parsed = json.loads(self.prefix.with_suffix(".parsed.json").read_text())
        self.assertEqual([row["id"] for row in parsed["records"]], self.ids)
        self.assertEqual(parsed["recovery_kind"], plan["recovery_kind"])
        self.assertEqual(parsed["identical_duplicate_normalization"], plan["identical_duplicate_normalization"])
        self.assertIs(parsed["recovered_from_cached_partial_output"], False)
        for cached, original in zip(parsed["records"], self.records):
            for key, value in original.items():
                self.assertEqual(cached[key], value)
        for path, data in before.items():
            self.assertEqual(path.read_bytes(), data)
        self.assertTrue(validate_completed_recovery(self.root, manifest_path, self.config)["completed"])

    def test_duplicate_recovery_rejects_conflicting_fields_whitespace_and_unknown_ids(self):
        changes = [
            {"status": "reject"},
            {"confident": self.records[-1]["confident"] + " "},
            {"hesitant": self.records[-1]["hesitant"] + " "},
            {"reject_reason": "A different reason."},
            {"extra_field": "Unexpected payload field."},
            {"id": "HC999"},
        ]
        for change in changes:
            with self.subTest(change=change):
                raw = self.envelope([*self.records, {**self.records[-1], **change}])
                self.write_original_raw(raw)
                with self.assertRaises(RuntimeError):
                    inspect_cached_batch(self.root, self.batch_name, self.config, allow_identical_duplicates=True)
        missing_field = dict(self.records[-1])
        missing_field.pop("reject_reason")
        self.write_original_raw(self.envelope([*self.records, missing_field]))
        with self.assertRaises(RuntimeError):
            inspect_cached_batch(self.root, self.batch_name, self.config, allow_identical_duplicates=True)

    def test_duplicate_manifest_and_parsed_provenance_cannot_be_changed(self):
        self.write_original_raw(self.envelope([*self.records, self.records[-1]]))
        manifest_path = complete_missing(self.root, self.batch_name, self.config,
                                         allow_identical_duplicates=True)
        manifest = json.loads(manifest_path.read_text())
        parsed_path = self.prefix.with_suffix(".parsed.json")
        parsed = json.loads(parsed_path.read_text())
        changed_manifest = copy.deepcopy(manifest)
        changed_manifest["identical_duplicate_normalization"]["discarded_indices"] = []
        dump(manifest_path, changed_manifest)
        with self.assertRaises(RuntimeError):
            validate_completed_recovery(self.root, manifest_path, self.config)
        dump(manifest_path, manifest)
        for field, value in [
            ("recovery_kind", "unknown"),
            ("identical_duplicate_normalization", {}),
            ("recovered_from_cached_partial_output", True),
        ]:
            with self.subTest(field=field):
                dump(parsed_path, {**parsed, field: value})
                dump(manifest_path, {**manifest, "parsed_file_sha256": file_sha256(parsed_path)})
                with self.assertRaises(RuntimeError):
                    validate_completed_recovery(self.root, manifest_path, self.config)
        dump(parsed_path, parsed)
        dump(manifest_path, manifest)

    def test_duplicate_recovery_rejects_refusals_truncation_and_wrong_model(self):
        baseline = self.envelope([*self.records, self.records[-1]])
        for change in [
            {"is_error": True}, {"subtype": "error"}, {"stop_reason": "refusal"},
            {"stop_reason": "max_tokens"}, {"modelUsage": {"another-model": {"outputTokens": 120}}},
        ]:
            with self.subTest(change=change):
                self.write_original_raw({**baseline, **change})
                with self.assertRaises(RuntimeError):
                    inspect_cached_batch(self.root, self.batch_name, self.config, allow_identical_duplicates=True)

    def test_duplicate_mode_requires_an_actual_duplicate_and_is_bound_to_evidence(self):
        with self.assertRaises(RuntimeError):
            inspect_cached_batch(self.root, self.batch_name, self.config, allow_identical_duplicates=True)
        self.write_original_raw(self.envelope([*self.records, self.records[-1]]))
        plan_path = prepare_recovery(self.root, self.batch_name, self.config, allow_identical_duplicates=True)
        plan = json.loads(plan_path.read_text())
        changed_metadata = copy.deepcopy(plan)
        changed_metadata["identical_duplicate_normalization"]["discarded_indices"] = [4]
        for changed in [
            changed_metadata,
            {**plan, "recovery_kind": "unknown"},
            {key: value for key, value in plan.items() if key != "recovery_kind"},
            {key: value for key, value in plan.items() if key != "identical_duplicate_normalization"},
        ]:
            with self.subTest(changed=changed):
                with self.assertRaises(RuntimeError):
                    validate_completion_plan(self.root, changed, self.config)
        for suffix in (".request.json", ".raw.json", ".events.jsonl"):
            path = self.prefix.with_suffix(suffix)
            original = path.read_bytes()
            with self.subTest(path=path.name):
                path.write_bytes(original + b"\n")
                with self.assertRaises(RuntimeError):
                    finalize_recovery(self.root, plan_path, self.config)
                self.assertFalse(self.prefix.with_suffix(".parsed.json").exists())
                path.write_bytes(original)

    def prepare_with_normalized_completion(self):
        plan_path, completion = self.prepare_with_completion()
        raw_path = completion.with_suffix(".raw.json")
        raw = self.envelope([*self.records[1:], self.records[-1]])
        dump(raw_path, raw)
        _, metadata = normalize_identical_duplicates(raw, self.ids[1:])
        metadata.update(raw_file_sha256=file_sha256(raw_path), cached_text_changed=False,
                        additional_provider_calls=0)
        parsed_path = completion.with_suffix(".parsed.json")
        parsed = json.loads(parsed_path.read_text())
        parsed["output_normalization"] = metadata
        dump(parsed_path, parsed)
        return plan_path, completion, parsed

    def test_missing_only_completion_accepts_pinned_identical_duplicate_normalization(self):
        plan_path, completion, parsed = self.prepare_with_normalized_completion()
        before = {path: path.read_bytes() for path in self.root.glob("provider*/*") if path.is_file()}
        with patch("cache_recovery.subprocess.run") as provider, patch(
                "subscription_preflight.capture_subscription_preflight") as preflight:
            manifest_path = finalize_recovery(self.root, plan_path, self.config)
            manifest = validate_completed_recovery(self.root, manifest_path, self.config)
        provider.assert_not_called()
        preflight.assert_not_called()
        self.assertEqual(manifest["completed_missing_ids"], self.ids[1:])
        self.assertEqual(manifest["evidence_file_sha256"][str(completion.with_suffix(".raw.json").relative_to(self.root))],
                         parsed["output_normalization"]["raw_file_sha256"])
        combined = json.loads(self.prefix.with_suffix(".parsed.json").read_text())["records"]
        self.assertEqual([row["id"] for row in combined], self.ids)
        for row, original in zip(combined, self.records):
            for field, value in original.items():
                self.assertEqual(row[field], value)
        for path, data in before.items():
            self.assertEqual(path.read_bytes(), data)

    def test_completion_duplicate_normalization_rejects_every_metadata_tamper(self):
        plan_path, completion, parsed = self.prepare_with_normalized_completion()
        parsed_path = completion.with_suffix(".parsed.json")
        normalization = parsed["output_normalization"]
        candidates = [None, [], "identical_record_duplicates_only", {},
                      {**normalization, "unexpected": True}]
        for field in normalization:
            candidates.append({key: value for key, value in normalization.items() if key != field})
        for field, value in [
            ("normalization", "different"), ("duplicate_ids", []), ("discarded_indices", [3]),
            ("discarded_indices", [False]), ("returned_ids", self.ids[1:]),
            ("raw_file_sha256", "0" * 64), ("cached_text_changed", True),
            ("cached_text_changed", 0), ("additional_provider_calls", 1),
            ("additional_provider_calls", False),
        ]:
            candidates.append({**normalization, field: value})
        for candidate in candidates:
            with self.subTest(metadata=candidate):
                dump(parsed_path, {**parsed, "output_normalization": candidate})
                with self.assertRaises(RuntimeError):
                    finalize_recovery(self.root, plan_path, self.config)
                self.assertFalse(self.prefix.with_suffix(".parsed.json").exists())
        dump(parsed_path, {key: value for key, value in parsed.items() if key != "output_normalization"})
        with self.assertRaises(RuntimeError):
            finalize_recovery(self.root, plan_path, self.config)

    def test_completion_normalization_rejects_conflicting_or_missing_duplicates_and_raw_changes(self):
        plan_path, completion, parsed = self.prepare_with_normalized_completion()
        raw_path = completion.with_suffix(".raw.json")
        parsed_path = completion.with_suffix(".parsed.json")
        baseline = raw_path.read_bytes()
        raw_path.write_bytes(baseline + b"\n")
        with self.assertRaises(RuntimeError):
            finalize_recovery(self.root, plan_path, self.config)
        raw_path.write_bytes(baseline)
        for records in [
            [*self.records[1:], {**self.records[-1], "hesitant": self.records[-1]["hesitant"] + " "}],
            self.records[1:],
        ]:
            with self.subTest(records=records):
                dump(raw_path, self.envelope(records))
                changed = copy.deepcopy(parsed)
                changed["output_normalization"]["raw_file_sha256"] = file_sha256(raw_path)
                dump(parsed_path, changed)
                with self.assertRaises(RuntimeError):
                    finalize_recovery(self.root, plan_path, self.config)
                self.assertFalse(self.prefix.with_suffix(".parsed.json").exists())


class CampaignCacheRecoveryResumeTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.config = {"model": "claude-haiku-5-5", "max_call_budget_usd": 0.12}
        self.batch_name = "batch_00167"
        self.manifest_path = self.root / "CACHE_RECOVERIES" / f"{self.batch_name}.completed.json"
        self.manifest = {"completed": True, "batch": self.batch_name}
        dump(self.manifest_path, self.manifest)
        self.campaign_job = {
            "pid": -1,
            "state": "finished",
            "stop_reason": "invalid_provider_output_no_retry",
        }
        self.current = {
            "state": "cache_recovery_complete",
            "detail": {"batch": self.batch_name},
            "calls_without_final_cost": 0,
        }
        self.campaign_status = {
            "state": "invalid_provider_output_no_retry",
            "detail": {"batch": self.batch_name},
        }
        dump(self.root / "CAMPAIGN_JOB.json", self.campaign_job)
        dump(self.root / "JOB.json", {"pid": -1, "state": "finished"})
        dump(self.root / "RUN_STATUS.json", self.current)
        dump(self.root / "CAMPAIGN_STATUS.json", self.campaign_status)
        dump(self.root / "CAMPAIGN_LAUNCH.json", {})
        dump(self.root / "provider" / f"{self.batch_name}.raw.json", {"result": "cached source"})
        dump(self.root / "provider" / f"{self.batch_name}.parsed.json", {"records": [{"id": "HC881"}]})
        self.evidence_path = self.root / "subscription_preflight.json"
        self.evidence = {"captured_at_utc": "synthetic fixture", "extra_usage_enabled": False}
        dump(self.evidence_path, self.evidence)
        self.validate = self.mock_dependency(
            "cache_recovery.validate_completed_recovery", return_value=self.manifest
        )
        self.baseline = self.mock_dependency("run_campaign.preserve_baseline")
        self.pending = self.mock_dependency("run_campaign.pending_batches", return_value=[])
        self.capture = self.mock_dependency(
            "run_campaign.capture_subscription_preflight", return_value=self.evidence_path
        )

    def mock_dependency(self, target, **kwargs):
        patcher = patch(target, **kwargs)
        self.addCleanup(patcher.stop)
        return patcher.start()

    def test_valid_resume_archives_reviewed_recovery_without_changing_saved_evidence(self):
        before = {path: path.read_bytes() for path in self.root.rglob("*") if path.is_file()}
        name = prepare_cache_recovery_resume(self.root, self.config, self.manifest_path)
        history_path = self.root / "CAMPAIGN_HISTORY" / name
        history = json.loads(history_path.read_text())

        self.assertEqual(history["manifest_file"], str(self.manifest_path.relative_to(self.root)))
        self.assertEqual(history["manifest_sha256"], file_sha256(self.manifest_path))
        self.assertEqual(history["previous_campaign_job"], self.campaign_job)
        self.assertEqual(history["current_status"], self.current)
        self.assertEqual(history["subscription_preflight"], self.evidence)
        self.assertIs(history["no_cached_text_regenerated"], True)
        self.assertIs(history["extra_usage_activated"], False)
        self.assertEqual(history["preserved_provider_file_sha256"], {
            str(path.relative_to(self.root)): hashlib.sha256(data).hexdigest()
            for path, data in before.items() if path.parent.name == "provider"
        })
        for path, data in before.items():
            self.assertEqual(path.read_bytes(), data)
        self.validate.assert_called_once_with(self.root, self.manifest_path, self.config)
        self.baseline.assert_called_once_with(self.root, self.config)
        self.pending.assert_called_once_with(self.root, self.config)
        self.capture.assert_called_once_with(self.config, self.root)

    def test_resume_cannot_bypass_other_campaign_stops_or_unresolved_quota_and_cost(self):
        for stop_reason in (
            "account_quota_rejected",
            "billing_or_credits_required",
            "provider_policy_refusal",
            "provider_error",
        ):
            with self.subTest(stop_reason=stop_reason):
                dump(self.root / "CAMPAIGN_JOB.json", {**self.campaign_job, "stop_reason": stop_reason})
                with self.assertRaises(RuntimeError):
                    prepare_cache_recovery_resume(self.root, self.config, self.manifest_path)
        dump(self.root / "CAMPAIGN_JOB.json", self.campaign_job)
        for changed in (
            {"state": "account_quota_rejected"},
            {"calls_without_final_cost": 1},
        ):
            with self.subTest(changed=changed):
                dump(self.root / "RUN_STATUS.json", {**self.current, **changed})
                with self.assertRaises(RuntimeError):
                    prepare_cache_recovery_resume(self.root, self.config, self.manifest_path)
        self.baseline.assert_not_called()
        self.pending.assert_not_called()
        self.capture.assert_not_called()
        self.assertFalse((self.root / "CAMPAIGN_HISTORY").exists())

    def test_resume_rejects_batch_mismatch_and_unresolved_worker_locks(self):
        for filename, original in (
            ("RUN_STATUS.json", self.current),
            ("CAMPAIGN_STATUS.json", self.campaign_status),
        ):
            with self.subTest(filename=filename):
                dump(self.root / filename, {**original, "detail": {"batch": "batch_00168"}})
                with self.assertRaises(RuntimeError):
                    prepare_cache_recovery_resume(self.root, self.config, self.manifest_path)
                dump(self.root / filename, original)
        for filename in ("WORKER_LOCK.json", "CAMPAIGN_LOCK.json"):
            with self.subTest(lock=filename):
                dump(self.root / filename, {"pid": -1})
                with self.assertRaises(RuntimeError):
                    prepare_cache_recovery_resume(self.root, self.config, self.manifest_path)
                (self.root / filename).unlink()
        self.baseline.assert_not_called()
        self.pending.assert_not_called()
        self.capture.assert_not_called()
        self.assertFalse((self.root / "CAMPAIGN_HISTORY").exists())


if __name__ == "__main__":
    unittest.main()
