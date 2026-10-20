"""Interrupted requests are preserved and excluded, never fabricated or retried."""
import copy
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))
import run_campaign as campaign
from cost_accounting import cost_accounting, unreviewed_cost_count
from interruption_defer import create_interruption_defer
from launch_expansion import pending_batches, prepare_resume, prepare_included_quota_resume
from run_expansion import build_request_data, dump, file_sha, fingerprint, request_record, sha
from transport_defer import IDLE_ERROR, create_transport_defer
from subscription_preflight import validate_subscription_preflight


class InterruptionFixture(unittest.TestCase):
    """Only synthetic files in a fresh temporary directory; no provider calls."""

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.batch = "batch_00001"
        self.prefix = self.root / "provider" / self.batch
        self.prompt = "Rewrite the synthetic source with direct and tentative confidence."
        prompt_path = self.root / "prompt.txt"
        prompt_path.write_text(self.prompt, encoding="utf-8")
        self.config = {"model": "claude-haiku-5-5", "batch_size": 5,
                       "max_output_tokens": 10000, "prompt_file": str(prompt_path),
                       "max_call_budget_usd": .12, "target_sources": 10000,
                       "expected_org_name": "Harvard Edu for FAS/SEAS"}
        self.sources = [{"review_id": f"HC{index}", "source_id": f"source-{index}",
                         "question": f"What is synthetic sample {index}?",
                         "original": f"Synthetic sample {index} contains a test fact."}
                        for index in range(1, 11)]
        dump(self.root / "SOURCES.json", self.sources)
        self.request = {"model": self.config["model"], "prompt": self.prompt,
                        "prompt_sha256": sha(self.prompt),
                        "request_sha256": fingerprint(self.config, self.prompt, self.sources[:5]),
                        "started_at_utc": "2026-10-20T01:50:00+00:00", "internal_retries": 0,
                        "account": {"authMethod": "claude.ai", "apiProvider": "firstParty",
                                    "subscriptionType": "enterprise", "orgName": self.config["expected_org_name"]},
                        "data": build_request_data(self.prompt, [request_record(row) for row in self.sources[:5]])}
        self.init = {"type": "system", "subtype": "init", "cwd": str(self.root),
                     "session_id": "11111111-1111-4111-8111-111111111111", "tools": [], "mcp_servers": [],
                     "model": self.config["model"], "apiKeySource": "none", "permissionMode": "dontAsk",
                     "uuid": "22222222-2222-4222-8222-222222222222"}
        dump(self.prefix.with_suffix(".request.json"), self.request)
        self.prefix.with_suffix(".events.jsonl").write_text(json.dumps(self.init) + "\n", encoding="utf-8")
        self.provider = self.patch("run_expansion.provider_stream", side_effect=AssertionError("No provider calls"))
        self.worker = self.patch("run_campaign.worker", side_effect=AssertionError("No worker launches"))

    def patch(self, target, **kwargs):
        patcher = mock.patch(target, **kwargs)
        self.addCleanup(patcher.stop)
        return patcher.start()

    def snapshot(self):
        return {path: path.read_bytes() for path in self.root.rglob("*") if path.is_file()}

    def create_review(self):
        review_path = self.root / "INTERRUPTION_RECOVERIES" / self.batch / "REVIEW.json"
        dump(review_path, {"kind": "reviewed_dead_worker_interruption", "batch": self.batch,
            "request_sha256": self.request["request_sha256"], "all_owned_processes_dead": True,
            "no_orphan_provider_processes": True,
            "provider_files_sha256": {str(path.relative_to(self.root)): file_sha(path)
                for path in self.root.glob("provider*/*") if path.is_file()}})
        return review_path

    def defer(self):
        return create_interruption_defer(self.root, self.batch, self.create_review())


class InterruptionPendingIntegrationTests(InterruptionFixture):
    def assert_read_only_rejected(self, config=None):
        before = self.snapshot()
        with self.assertRaises(RuntimeError):
            pending_batches(self.root, self.config if config is None else config)
        self.assertEqual(self.snapshot(), before)
        self.provider.assert_not_called()
        self.worker.assert_not_called()

    def test_only_explicitly_reviewed_init_only_request_is_skipped_without_new_answers(self):
        self.assert_read_only_rejected()
        originals = self.snapshot()
        entry = self.defer()
        before = self.snapshot()
        self.assertEqual(pending_batches(self.root, self.config), ["batch_00002"])
        self.assertEqual(self.snapshot(), before)
        for path, data in originals.items():
            self.assertEqual(path.read_bytes(), data)
        self.assertEqual(entry["source_ids"], [row["review_id"] for row in self.sources[:5]])
        self.assertEqual(entry["usage_reporting"], "unreported")
        self.assertFalse(self.prefix.with_suffix(".raw.json").exists())
        self.assertFalse(self.prefix.with_suffix(".parsed.json").exists())
        self.provider.assert_not_called()
        self.worker.assert_not_called()

    def test_changed_sources_prompt_model_request_or_review_cannot_be_skipped(self):
        entry = self.defer()
        for config in ({**self.config, "model": "unapproved-model"},
                       {**self.config, "max_output_tokens": 9999}):
            with self.subTest(config=config):
                self.assert_read_only_rejected(config)
        sources = copy.deepcopy(self.sources)
        sources[0]["original"] += " Changed factual content."
        dump(self.root / "SOURCES.json", sources)
        self.assert_read_only_rejected()
        dump(self.root / "SOURCES.json", self.sources)
        path = self.prefix.with_suffix(".request.json")
        original = path.read_bytes()
        path.write_bytes(original + b"\n")
        self.assert_read_only_rejected()
        path.write_bytes(original)
        review = self.root / entry["review_file"]
        review.write_bytes(review.read_bytes() + b"\n")
        self.assert_read_only_rejected()

    def test_later_partial_final_or_unknown_artifacts_invalidate_deferral(self):
        self.defer()
        for suffix, value in ((".raw.json", {}), (".parsed.json", {
                                  "request_sha256": self.request["request_sha256"], "records": []}),
                              (".quota.json", {"events": []}), (".unexpected.json", {})):
            path = self.prefix.with_suffix(suffix)
            with self.subTest(suffix=suffix):
                dump(path, value)
                try:
                    self.assert_read_only_rejected()
                finally:
                    path.unlink()

    def test_conflicting_policy_or_transport_exclusions_cannot_hide_interrupted_request(self):
        self.defer()
        for folder in ("QUARANTINED_BATCHES", "DEFERRED_TRANSPORT_BATCHES"):
            path = self.root / folder / (self.batch + ".json")
            with self.subTest(folder=folder):
                dump(path, {})
                self.assert_read_only_rejected()
                path.unlink()


class InterruptionAccountingIntegrationTests(InterruptionFixture):
    def add_reviewed_transport(self):
        prefix = self.root / "provider" / "batch_00450"
        raw = {"type": "result", "subtype": "success", "is_error": True,
               "stop_reason": "stop_sequence", "result": IDLE_ERROR,
               "modelUsage": {}, "total_cost_usd": 0, "api_error_status": None}
        request = {"model": self.config["model"], "request_sha256": "a" * 64,
                   "data": {"records": [{"id": f"OLD{index}"} for index in range(5)]}}
        dump(prefix.with_suffix(".request.json"), request)
        dump(prefix.with_suffix(".raw.json"), raw)
        events = [{"type": "system", "subtype": "init", "model": self.config["model"]},
                  {"type": "assistant", "message": {"model": self.config["model"],
                   "content": [{"type": "thinking", "thinking": "", "signature": ""}]}},
                  {"type": "assistant", "message": {"model": "<synthetic>",
                   "content": [{"type": "text", "text": IDLE_ERROR}]}}, raw]
        prefix.with_suffix(".events.jsonl").write_text(
            "".join(json.dumps(event) + "\n" for event in events), encoding="utf-8")
        create_transport_defer(self.root, prefix.name)

    def test_reviewed_interruption_retains_unknown_usage_and_does_not_clear_old_unknowns(self):
        self.add_reviewed_transport()
        before = cost_accounting(self.root, self.config)
        self.assertEqual(before["calls_without_final_cost"], 2)
        self.assertEqual(before["unreviewed_calls_without_final_cost"], 1)
        self.defer()
        ledger = cost_accounting(self.root, self.config)
        self.assertEqual(ledger["calls_without_final_cost"], 2)
        self.assertEqual(ledger["unreviewed_calls_without_final_cost"], 0)
        self.assertEqual(ledger["reviewed_deferred_transport_calls_without_final_cost"], 1)
        self.assertEqual(ledger["reviewed_deferred_interruption_calls_without_final_cost"], 1)
        self.assertEqual(ledger["unknown_cli_estimate_reserve_usd"], .24)
        self.assertTrue(ledger["uncertain_usage_estimates_not_invoices"])
        self.assertEqual(unreviewed_cost_count(self.root, self.config, {"calls_without_final_cost": 1}), 0)
        self.assertEqual(unreviewed_cost_count(self.root, self.config, {"calls_without_final_cost": 3}), 1)
        dump(self.root / "provider" / "batch_00003.request.json", {"request_sha256": "b" * 64})
        self.assertEqual(unreviewed_cost_count(self.root, self.config, {"calls_without_final_cost": 2}), 1)
        self.provider.assert_not_called()
        self.worker.assert_not_called()

    def test_forged_status_review_credit_and_tampered_manifest_cannot_clear_unknown_attempt(self):
        status = {"calls_without_final_cost": 1,
                  "reviewed_deferred_interruption_calls_without_final_cost": 999,
                  "reviewed_deferred_transport_calls_without_final_cost": 999}
        self.assertEqual(unreviewed_cost_count(self.root, self.config, status), 1)
        self.defer()
        path = self.root / "DEFERRED_INTERRUPTED_BATCHES" / (self.batch + ".json")
        entry = json.loads(path.read_text())
        dump(path, {**entry, "request_sha256": "f" * 64})
        with self.assertRaises(RuntimeError):
            cost_accounting(self.root, self.config)
        with self.assertRaises(RuntimeError):
            unreviewed_cost_count(self.root, self.config, status)


class InterruptionAlternativeResumeGuards(InterruptionFixture):
    def setUp(self):
        super().setUp()
        self.job = {"pid": 2147483000, "state": "running", "started_at_utc": "2026-10-20T01:40:00+00:00"}
        self.status = {"state": "running", "detail": {"batch": self.batch}, "calls_without_final_cost": 1}
        for name in ("JOB.json", "CAMPAIGN_JOB.json"):
            dump(self.root / name, self.job)
        for name in ("WORKER_LOCK.json", "CAMPAIGN_LOCK.json"):
            dump(self.root / name, {"pid": self.job["pid"], "started_at_utc": self.job["started_at_utc"]})
        dump(self.root / "RUN_STATUS.json", self.status)
        dump(self.root / "CAMPAIGN_STATUS.json", self.status)
        dump(self.root / "CAMPAIGN_LAUNCH.json", {"pid": self.job["pid"]})
        dump(self.root / "LAUNCH.json", {"pid": self.job["pid"]})
        self.evidence = {"checked_at_utc": datetime.now(timezone.utc).isoformat(), "read_only": True,
            "account": {"loggedIn": True, "authMethod": "claude.ai", "apiProvider": "firstParty",
                        "subscriptionType": "enterprise", "orgName": self.config["expected_org_name"]},
            "usage": {"five_hour": {"utilization": 2, "locked_reason": None},
                      "extra_usage": {"is_enabled": False}},
            "model_calls": 0, "billing_settings_changed": False}
        self.evidence_path = self.root / "SUBSCRIPTION_PREFLIGHT" / "fresh.json"
        dump(self.evidence_path, self.evidence)
        self.capture = self.patch("run_campaign.capture_subscription_preflight",
                                  side_effect=AssertionError("Wrong resume must not call accounts"))

    def test_existing_resume_paths_cannot_bypass_dead_running_records_and_owned_locks(self):
        calls = [lambda: campaign.prepare_refusal_resume(self.root, self.config, self.batch),
                 lambda: campaign.prepare_transport_defer_resume(self.root, self.config, self.batch),
                 lambda: campaign.prepare_verified_preflight_resume(self.root, self.config, self.evidence_path),
                 lambda: prepare_resume(self.root, self.config),
                 lambda: prepare_included_quota_resume(self.root, self.config, self.evidence_path)]
        before = self.snapshot()
        with mock.patch("run_campaign.alive", return_value=False), mock.patch("launch_expansion.alive", return_value=False):
            for index, resume in enumerate(calls):
                with self.subTest(path=index):
                    with self.assertRaises(RuntimeError):
                        resume()
                    self.assertEqual(self.snapshot(), before)
        self.capture.assert_not_called()
        self.provider.assert_not_called()
        self.worker.assert_not_called()

    def test_default_campaign_launch_does_not_treat_dead_running_state_as_restart_permission(self):
        config = {**self.config, "private_dir": ".", "campaign": {"enabled": True}}
        dump(self.root / "configs" / "expansion_10000_v1.json", config)
        before = self.snapshot()
        with mock.patch.object(campaign, "BASE", self.root), mock.patch.object(campaign, "alive", return_value=False), \
             mock.patch.object(sys, "argv", ["run_campaign.py"]), mock.patch("run_campaign.subprocess.Popen") as launch:
            with self.assertRaisesRegex(RuntimeError, "previous campaign stopped"):
                campaign.main()
            launch.assert_not_called()
        self.assertEqual(self.snapshot(), before)
        self.capture.assert_not_called()


class InterruptionControllerResumeTests(InterruptionFixture):
    def setUp(self):
        super().setUp()
        self.config["campaign"] = {"enabled": True, "interruption_recovery": {
            "enabled": True, "user_authorized": True, "init_only_no_resubmission": True}}
        self.pid = 2147483000
        self.job = {"pid": self.pid, "state": "running", "started_at_utc": "2026-10-20T01:45:00+00:00"}
        self.status = {"state": "running", "detail": {"batch": self.batch},
                       "updated_at_utc": "2026-10-20T01:50:05+00:00", "calls_without_final_cost": 0,
                       "total_generated_triplets": 50}
        self.campaign_status = {**self.status, "state": "generating", "campaign_state": "generating"}
        self.launch = {"pid": self.pid, "launched_at_utc": "2026-10-20T01:44:59+00:00"}
        self.lock = {"pid": self.pid, "started_at_utc": self.job["started_at_utc"]}
        self.restore_lifecycle()
        interruption = "KeyboardInterrupt: Read-only stop requested; do not submit further provider calls\n"
        for name in ("CAMPAIGN.log", "BACKGROUND.log"):
            (self.root / name).write_text("Synthetic streaming traceback.\n" + interruption, encoding="utf-8")
        self.evidence = {"checked_at_utc": datetime.now(timezone.utc).isoformat(), "read_only": True,
            "account": {"loggedIn": True, "authMethod": "claude.ai", "apiProvider": "firstParty",
                        "subscriptionType": "enterprise", "orgName": self.config["expected_org_name"]},
            "usage": {"five_hour": {"utilization": 2, "locked_reason": None},
                      "extra_usage": {"is_enabled": False}},
            "model_calls": 0, "billing_settings_changed": False}
        self.evidence_path = self.root / "SUBSCRIPTION_PREFLIGHT" / "fresh.json"
        dump(self.evidence_path, self.evidence)
        self.baseline = self.patch("run_campaign.preserve_baseline")
        self.alive = self.patch("run_campaign.alive", return_value=False)
        self.scan = self.patch("run_campaign.inspect_interruption_processes", return_value={
            "all_owned_processes_dead": True, "no_orphan_provider_processes": True,
            "recorded_pids": [self.pid]})
        self.capture = self.patch("run_campaign.capture_subscription_preflight", return_value=self.evidence_path)
        self.validator = self.patch("subscription_preflight.validate_subscription_preflight",
                                    wraps=validate_subscription_preflight)
        self.state = self.patch("run_campaign.state", side_effect=self.write_ready_status)

    def restore_lifecycle(self):
        for name in ("CAMPAIGN_JOB.json", "JOB.json"):
            dump(self.root / name, self.job)
        for name in ("CAMPAIGN_LOCK.json", "WORKER_LOCK.json"):
            dump(self.root / name, self.lock)
        dump(self.root / "RUN_STATUS.json", self.status)
        dump(self.root / "CAMPAIGN_STATUS.json", self.campaign_status)
        dump(self.root / "CAMPAIGN_LAUNCH.json", self.launch)
        dump(self.root / "LAUNCH.json", self.launch)

    def write_ready_status(self, root, config, phase, detail):
        self.assertEqual((root, config, phase), (self.root, self.config, "reviewed_interruption_deferred"))
        self.capture.assert_called_once_with(self.config, self.root)
        self.validator.assert_called_once_with(self.evidence_path, self.config)
        self.assertTrue((self.root / "CAMPAIGN_HISTORY" / detail["history"]).is_file())
        self.assertFalse((root / "CAMPAIGN_LOCK.json").exists())
        self.assertFalse((root / "WORKER_LOCK.json").exists())
        result = {**self.status, **cost_accounting(root, config), "state": phase, "detail": detail}
        dump(root / "RUN_STATUS.json", result)
        return result

    def resume(self, batch=None):
        return campaign.prepare_interruption_resume(self.root, self.config,
                                                     self.batch if batch is None else batch)

    def assert_no_mutation_on_failure(self):
        before = self.snapshot()
        with self.assertRaises(RuntimeError):
            self.resume()
        self.assertEqual(self.snapshot(), before)
        self.state.assert_not_called()
        self.provider.assert_not_called()
        self.worker.assert_not_called()

    def test_reviewed_dead_interruption_archives_exact_locks_and_evidence_before_safe_ready_state(self):
        before = self.snapshot()
        history_name = self.resume()
        event = json.loads((self.root / "CAMPAIGN_HISTORY" / history_name).read_text())
        self.assertEqual(event["previous_jobs"], {"CAMPAIGN_JOB.json": self.job, "JOB.json": self.job})
        self.assertEqual(event["previous_status"], self.status)
        self.assertEqual(event["previous_campaign_status"], self.campaign_status)
        self.assertEqual(event["previous_launch"], self.launch)
        self.assertEqual(event["deferred_interruption_entry"]["request_sha256"], self.request["request_sha256"])
        marker = self.root / event["deferred_interruption_file"]
        self.assertEqual(event["deferred_interruption_sha256"], file_sha(marker))
        self.assertEqual(event["deferred_interruption_entry"]["usage_reporting"], "unreported")
        self.assertIs(event["deferred_interruption_entry"]["zero_cost_claimed"], False)
        self.assertEqual(event["cost_accounting"]["calls_without_final_cost"], 1)
        self.assertEqual(event["cost_accounting"]["unknown_cli_estimate_reserve_usd"], .12)
        self.assertEqual(len(event["archived_locks"]), 2)
        archive = self.root / "INTERRUPTION_RECOVERIES" / self.batch
        self.assertTrue((archive / "REVIEW.json").is_file())
        released = archive / "released_locks"
        self.assertEqual({path.name: path.read_bytes() for path in released.iterdir()}, {
            name: before[self.root / name] for name in ("CAMPAIGN_LOCK.json", "WORKER_LOCK.json")})
        for name in ("CAMPAIGN_JOB.json", "JOB.json"):
            job = json.loads((self.root / name).read_text())
            self.assertEqual(job["state"], "finished")
            self.assertEqual(job["stop_reason"], "reviewed_interruption_deferred")
        for path, original in before.items():
            if path.parent.name.startswith("provider") or path.name in {"CAMPAIGN.log", "BACKGROUND.log", "SOURCES.json"}:
                self.assertEqual(path.read_bytes(), original)
        self.assertEqual(event["preserved_provider_file_sha256"], {
            str(path.relative_to(self.root)): file_sha(path)
            for path in before if path.parent.name.startswith("provider")})
        self.assertIn("reviewed_interruption_deferred", campaign.CONTINUABLE)
        self.baseline.assert_called_once_with(self.root, self.config)
        self.capture.assert_called_once_with(self.config, self.root)
        self.provider.assert_not_called()
        self.worker.assert_not_called()
        self.assertFalse(self.prefix.with_suffix(".raw.json").exists())
        self.assertFalse(self.prefix.with_suffix(".parsed.json").exists())
        after = self.snapshot()
        with self.assertRaises(RuntimeError):
            self.resume()
        self.assertEqual(self.snapshot(), after)
        self.capture.assert_called_once_with(self.config, self.root)

    def test_same_positive_owner_pid_is_required_across_both_jobs_locks_and_launch(self):
        for filename in ("CAMPAIGN_JOB.json", "JOB.json", "CAMPAIGN_LOCK.json", "WORKER_LOCK.json", "CAMPAIGN_LAUNCH.json"):
            for pid in (0, -1, None, True, self.pid - 1):
                with self.subTest(filename=filename, pid=pid):
                    self.restore_lifecycle()
                    value = json.loads((self.root / filename).read_text())
                    dump(self.root / filename, {**value, "pid": pid})
                    self.assert_no_mutation_on_failure()
        self.capture.assert_not_called()

    def test_running_stale_lifecycle_and_exact_allowed_states_cannot_mask_other_failures(self):
        for filename, field, values in (
                ("CAMPAIGN_JOB.json", "state", ["finished", "failed"]),
                ("JOB.json", "state", ["finished", "failed"]),
                ("RUN_STATUS.json", "state", ["provider_policy_refusal", "provider_error", "account_quota_rejected", "billing_or_credits_required"]),
                ("CAMPAIGN_STATUS.json", "state", ["provider_policy_refusal", "provider_error", "account_quota_rejected", "billing_or_credits_required"])):
            for value in values:
                with self.subTest(filename=filename, value=value):
                    self.restore_lifecycle()
                    record = json.loads((self.root / filename).read_text())
                    dump(self.root / filename, {**record, field: value})
                    self.assert_no_mutation_on_failure()
        self.capture.assert_not_called()

    def test_mismatched_lock_start_times_and_launch_after_job_start_are_rejected(self):
        for filename, key, timestamp in (
                ("CAMPAIGN_LOCK.json", "started_at_utc", "2026-10-20T01:45:10+00:00"),
                ("WORKER_LOCK.json", "started_at_utc", "2026-10-20T01:45:10+00:00"),
                ("CAMPAIGN_LAUNCH.json", "launched_at_utc", "2026-10-20T01:45:10+00:00"),
                ("JOB.json", "started_at_utc", "not-a-time")):
            with self.subTest(filename=filename):
                self.restore_lifecycle()
                value = json.loads((self.root / filename).read_text())
                dump(self.root / filename, {**value, key: timestamp})
                self.assert_no_mutation_on_failure()
        self.capture.assert_not_called()

    def test_a_live_owner_any_orphan_or_failed_process_scan_prevents_quota_check_and_lock_removal(self):
        self.alive.return_value = True
        self.assert_no_mutation_on_failure()
        self.alive.return_value = False
        for observed in ({"all_owned_processes_dead": False, "no_orphan_provider_processes": True},
                         {"all_owned_processes_dead": True, "no_orphan_provider_processes": False}):
            self.scan.return_value = observed
            self.assert_no_mutation_on_failure()
        self.scan.side_effect = RuntimeError("Synthetic process inventory is unavailable")
        self.assert_no_mutation_on_failure()
        self.capture.assert_not_called()

    def test_no_terminal_interrupt_signature_or_nonempty_provider_output_is_not_this_recovery(self):
        for name in ("CAMPAIGN.log", "BACKGROUND.log"):
            (self.root / name).write_text("Synthetic unexplained exit.\n", encoding="utf-8")
        self.assert_no_mutation_on_failure()
        self.capture.assert_not_called()

    def test_new_raw_partial_or_quota_artifact_is_never_accepted_as_init_only(self):
        for suffix, value in ((".raw.json", {}), (".quota.json", {"events": []}),
                              (".parsed.json", {"records": []})):
            path = self.prefix.with_suffix(suffix)
            with self.subTest(suffix=suffix):
                dump(path, value)
                try:
                    self.assert_no_mutation_on_failure()
                finally:
                    path.unlink()
        self.capture.assert_not_called()

    def test_scope_flags_must_all_be_exact_true_before_interruption_continuation(self):
        flags = self.config["campaign"]["interruption_recovery"]
        for key in flags:
            for value in (False, None, 1):
                with self.subTest(key=key, value=value):
                    self.config["campaign"]["interruption_recovery"] = {**flags, key: value}
                    self.assert_no_mutation_on_failure()
        self.capture.assert_not_called()

    def test_baseline_integrity_failure_does_not_touch_stale_owned_locks_or_output(self):
        self.baseline.side_effect = RuntimeError("Synthetic preserved baseline mismatch")
        self.assert_no_mutation_on_failure()
        self.capture.assert_not_called()

    def test_failed_fresh_quota_check_never_releases_locks_or_marks_continuation_ready(self):
        self.capture.side_effect = RuntimeError("Synthetic fresh included-quota check failed")
        self.assert_no_mutation_on_failure()
        self.capture.assert_called_once_with(self.config, self.root)
        self.validator.assert_not_called()

    def test_extra_usage_exhausted_quota_wrong_org_or_stale_evidence_never_release_locks(self):
        cases = []
        for enabled in (True, None):
            value = copy.deepcopy(self.evidence)
            value["usage"]["extra_usage"]["is_enabled"] = enabled
            cases.append(value)
        value = copy.deepcopy(self.evidence)
        value["usage"]["five_hour"]["utilization"] = 100
        cases.append(value)
        value = copy.deepcopy(self.evidence)
        value["account"]["orgName"] = "Not Harvard"
        cases.append(value)
        cases.append({**self.evidence, "checked_at_utc":
                      (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat()})
        for index, evidence in enumerate(cases):
            with self.subTest(case=index):
                dump(self.evidence_path, evidence)
                self.assert_no_mutation_on_failure()

    def test_another_unreviewed_attempt_or_larger_cached_unknown_count_blocks_this_allowance(self):
        path = self.root / "provider" / "batch_00003.request.json"
        dump(path, {"request_sha256": "b" * 64})
        self.assert_no_mutation_on_failure()
        path.unlink()
        dump(self.root / "RUN_STATUS.json", {**self.status, "calls_without_final_cost": 2})
        self.assert_no_mutation_on_failure()

    def test_existing_interruption_archive_is_not_overwritten_or_used_for_a_second_attempt(self):
        path = self.root / "INTERRUPTION_RECOVERIES" / self.batch / "prior-evidence.txt"
        path.parent.mkdir(parents=True)
        path.write_text("Preserve this earlier diagnostic evidence.\n", encoding="utf-8")
        self.assert_no_mutation_on_failure()
        self.capture.assert_not_called()

    def test_second_process_check_must_still_prove_all_owned_processes_dead(self):
        valid = self.scan.return_value
        self.scan.side_effect = [valid, {**valid, "all_owned_processes_dead": False}]
        self.assert_no_mutation_on_failure()
        self.capture.assert_called_once_with(self.config, self.root)

    def test_second_process_check_must_still_prove_no_orphan_provider_stream(self):
        valid = self.scan.return_value
        self.scan.side_effect = [valid, {**valid, "no_orphan_provider_processes": False}]
        self.assert_no_mutation_on_failure()
        self.capture.assert_called_once_with(self.config, self.root)

    def test_final_process_check_failure_preserves_locks_and_jobs_despite_saved_diagnostic_archive(self):
        valid = self.scan.return_value
        self.scan.side_effect = [valid, valid, {**valid, "all_owned_processes_dead": False}]
        before = self.snapshot()
        with self.assertRaises(RuntimeError):
            self.resume()
        for name in ("CAMPAIGN_LOCK.json", "WORKER_LOCK.json", "JOB.json", "CAMPAIGN_JOB.json",
                     "RUN_STATUS.json", "CAMPAIGN_STATUS.json"):
            self.assertEqual((self.root / name).read_bytes(), before[self.root / name])
        for path, value in before.items():
            if path.parent.name.startswith("provider"):
                self.assertEqual(path.read_bytes(), value)
        self.assertFalse(any((self.root / "CAMPAIGN_HISTORY").glob("*.json")))
        self.state.assert_not_called()
        self.provider.assert_not_called()
        self.worker.assert_not_called()


class InterruptionProcessInventoryTests(InterruptionFixture):
    def setUp(self):
        super().setUp()
        self.pid = 2147483000
        self.alive = self.patch("run_campaign.alive", return_value=False)
        self.processes = self.patch("run_campaign.subprocess.run")

    def scan(self, extra=""):
        self.processes.return_value = mock.Mock(
            stdout=f"{os.getpid()} 0 python synthetic-current-check\n" + extra)
        return campaign.inspect_interruption_processes(self.root, self.batch, self.pid)

    def test_recorded_owner_must_be_dead_and_offline_scan_never_terminates_any_process(self):
        self.alive.return_value = True
        with self.assertRaises(RuntimeError):
            self.scan()
        self.provider.assert_not_called()
        self.worker.assert_not_called()

    def test_no_matching_live_process_produces_narrow_dead_owner_evidence(self):
        evidence = self.scan("8001 1 python /tmp/unrelated-research/script.py\n")
        self.assertTrue(evidence["all_owned_processes_dead"])
        self.assertTrue(evidence["no_orphan_provider_processes"])
        self.assertEqual(evidence["recorded_pids"], [self.pid])
        self.assertEqual(self.processes.call_args.args[0], ["ps", "-axo", "pid=,ppid=,command="])
        self.provider.assert_not_called()
        self.worker.assert_not_called()

    def test_matching_worker_or_direct_descendant_blocks_resume_without_killing_it(self):
        script = str((campaign.BASE / "src" / "run_campaign.py").resolve())
        for line in (f'8001 1 python "{script}" --worker\n',
                     f"8001 {self.pid} python synthetic-orphan-child\n"):
            with self.subTest(line=line):
                with self.assertRaises(RuntimeError):
                    self.scan(line)
        self.provider.assert_not_called()
        self.worker.assert_not_called()

    def test_provider_stream_matching_session_or_workspace_is_an_orphan_blocker(self):
        for selector in (f"--session-id {self.init['session_id']}", f'--cwd "{self.root}"'):
            with self.subTest(selector=selector):
                with self.assertRaises(RuntimeError):
                    self.scan(f"8001 1 /bin/claude --print --output-format stream-json {selector}\n")
        self.provider.assert_not_called()

    def test_workers_and_streams_for_another_project_do_not_block_this_exact_interruption(self):
        lines = ("8001 1 python /tmp/other-project/src/run_campaign.py --worker\n"
                 "8002 1 /bin/claude --print --output-format stream-json "
                 "--session-id 33333333-3333-4333-8333-333333333333 --cwd /tmp/other-project\n")
        evidence = self.scan(lines)
        self.assertTrue(evidence["all_owned_processes_dead"])
        self.assertTrue(evidence["no_orphan_provider_processes"])
        self.provider.assert_not_called()

    def test_process_inventory_failure_is_not_treated_as_no_orphans(self):
        self.processes.side_effect = RuntimeError("Synthetic operating-system process inventory unavailable")
        with self.assertRaises(RuntimeError):
            campaign.inspect_interruption_processes(self.root, self.batch, self.pid)
        self.provider.assert_not_called()
        self.worker.assert_not_called()


if __name__ == "__main__":
    unittest.main()
