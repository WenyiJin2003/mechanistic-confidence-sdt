"""Explicit transport review preserves cached evidence and needs fresh quota checks."""
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
from launch_expansion import pending_batches as real_pending_batches
from run_expansion import dump, file_sha, fingerprint, request_record
from subscription_preflight import validate_subscription_preflight
from transport_defer import IDLE_ERROR, create_transport_defer


class TransportCampaignResumeTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.batch = "batch_00450"
        self.deferred = self.root / "DEFERRED_TRANSPORT_BATCHES" / f"{self.batch}.json"
        self.config = {"model": "claude-haiku-5-5", "batch_size": 5,
                       "target_sources": 10000, "expected_org_name": "Harvard Edu for FAS/SEAS"}
        self.sources = [{"review_id": f"HC{index:05d}", "source_id": f"source-{index}",
                         "question": f"What is synthetic sample {index}?",
                         "original": f"Synthetic sample {index} has no private content."}
                        for index in range(2246, 2251)]
        dump(self.root / "SOURCES.json", self.sources)
        self.prefix = self.root / "provider" / self.batch
        dump(self.prefix.with_suffix(".request.json"), {
            "request_sha256": "a" * 64,
            "data": {"records": [{"id": row["review_id"]} for row in self.sources]},
        })
        self.prefix.with_suffix(".events.jsonl").write_text(
            json.dumps({"type": "system", "subtype": "init"}) + "\n", encoding="utf-8")
        self.prefix.with_suffix(".stderr.txt").write_text(
            "Synthetic transport failure before a final result.\n", encoding="utf-8")
        dump(self.prefix.with_suffix(".quota.json"), {"events": []})
        dump(self.root / "provider" / "batch_00449.parsed.json", {
            "records": [{"id": "HC02245", "status": "ok", "confident": "Existing direct text.",
                         "hesitant": "Existing tentative text."}],
        })
        dump(self.root / "provider_completions_batch_00179" / "batch_00001.raw.json", {
            "result": "Existing cached completion text.", "total_cost_usd": 0.001,
        })
        self.entry = {"batch": self.batch, "source_ids": [row["review_id"] for row in self.sources],
                      "decision": "defer_without_retry", "request_sha256": "a" * 64}
        self.job = {"pid": -1, "state": "finished", "stop_reason": "provider_error"}
        self.status = {"state": "provider_error", "detail": {"batch": self.batch},
                       "calls_without_final_cost": 1, "total_generated_triplets": 2240}
        self.campaign_status = {**self.status, "campaign_state": "stopped",
                                "campaign_detail": "provider_error"}
        self.launch = {"pid": -1, "launched_at_utc": "synthetic previous launch"}
        self.restore_status()
        self.evidence = {
            "checked_at_utc": datetime.now(timezone.utc).isoformat(), "read_only": True,
            "account": {"loggedIn": True, "authMethod": "claude.ai", "apiProvider": "firstParty",
                        "subscriptionType": "enterprise", "orgName": self.config["expected_org_name"]},
            "usage": {"five_hour": {"utilization": 2, "locked_reason": None},
                      "extra_usage": {"is_enabled": False}},
            "model_calls": 0, "billing_settings_changed": False,
        }
        self.evidence_path = self.root / "SUBSCRIPTION_PREFLIGHT" / "check_fresh_fixture.json"
        dump(self.evidence_path, self.evidence)
        self.ledger = {"calls_without_final_cost": 1, "reviewed_deferred_transport_calls_without_final_cost": 1,
                       "unreviewed_calls_without_final_cost": 0}
        self.order = mock.Mock()
        self.baseline = self.patch("run_campaign.preserve_baseline")
        self.defer = self.patch("transport_defer.create_transport_defer", side_effect=self.save_deferred)
        self.pending = self.patch("run_campaign.pending_batches", return_value=["batch_00451"])
        self.cost = self.patch("run_campaign.unreviewed_cost_count", return_value=0)
        self.accounting = self.patch("run_campaign.cost_accounting", return_value=self.ledger)
        self.capture = self.patch("run_campaign.capture_subscription_preflight", return_value=self.evidence_path)
        self.validator = self.patch("subscription_preflight.validate_subscription_preflight",
                                    wraps=validate_subscription_preflight)
        self.state = self.patch("run_campaign.state", side_effect=self.write_resume_state)
        self.provider = self.patch("run_expansion.provider_stream",
                                   side_effect=AssertionError("Resume tests must never call a provider"))
        self.worker = self.patch("run_campaign.worker",
                                 side_effect=AssertionError("Resume preparation must not launch a worker"))
        for name in ("baseline", "defer", "pending", "cost", "capture", "validator", "state"):
            self.order.attach_mock(getattr(self, name), name)

    def patch(self, target, **kwargs):
        patcher = mock.patch(target, **kwargs)
        self.addCleanup(patcher.stop)
        return patcher.start()

    def restore_status(self):
        for filename in ("CAMPAIGN_JOB.json", "JOB.json"):
            dump(self.root / filename, self.job)
        dump(self.root / "RUN_STATUS.json", self.status)
        dump(self.root / "CAMPAIGN_STATUS.json", self.campaign_status)
        dump(self.root / "CAMPAIGN_LAUNCH.json", self.launch)

    def save_deferred(self, root, batch):
        self.assertEqual((root, batch), (self.root, self.batch))
        dump(self.deferred, self.entry)
        return self.entry

    def write_resume_state(self, root, config, phase, detail):
        self.assertEqual((root, config, phase), (self.root, self.config, "reviewed_transport_deferred"))
        self.assertTrue((root / "CAMPAIGN_HISTORY" / detail["history"]).is_file())
        self.capture.assert_called_once_with(self.config, self.root)
        self.validator.assert_called_once_with(self.evidence_path, self.config)
        result = {**self.status, "state": phase, "detail": detail}
        dump(root / "RUN_STATUS.json", result)
        return result

    def resume(self, batch=None):
        return campaign.prepare_transport_defer_resume(self.root, self.config,
                                                       self.batch if batch is None else batch)

    def provider_bytes(self):
        return {path: path.read_bytes() for path in self.root.glob("provider*/*") if path.is_file()}

    def assert_no_resume(self):
        self.assertFalse(any((self.root / "CAMPAIGN_HISTORY").glob("*.json")))
        self.state.assert_not_called()
        self.provider.assert_not_called()
        self.worker.assert_not_called()
        self.assertEqual(json.loads((self.root / "RUN_STATUS.json").read_text()), self.status)

    def test_reviewed_transport_failure_is_archived_without_resubmission_or_cache_changes(self):
        provider_before = self.provider_bytes()
        preserved_names = ("CAMPAIGN_JOB.json", "JOB.json", "CAMPAIGN_LAUNCH.json", "CAMPAIGN_STATUS.json", "SOURCES.json")
        preserved = {name: (self.root / name).read_bytes() for name in preserved_names}
        history_name = self.resume()
        history = json.loads((self.root / "CAMPAIGN_HISTORY" / history_name).read_text())
        self.assertEqual(history["deferred_transport_entry"], self.entry)
        self.assertEqual(history["deferred_transport_file"], str(self.deferred.relative_to(self.root)))
        self.assertEqual(history["deferred_transport_sha256"], file_sha(self.deferred))
        self.assertEqual(history["previous_jobs"], {"CAMPAIGN_JOB.json": self.job, "JOB.json": self.job})
        self.assertEqual(history["previous_status"], self.status)
        self.assertEqual(history["previous_campaign_status"], self.campaign_status)
        self.assertEqual(history["previous_launch"], self.launch)
        self.assertEqual(history["sources_sha256"], file_sha(self.root / "SOURCES.json"))
        self.assertEqual(history["preflight_file"], str(self.evidence_path.relative_to(self.root)))
        self.assertEqual(history["preflight_sha256"], file_sha(self.evidence_path))
        self.assertEqual(history["subscription_preflight"], self.evidence)
        self.assertEqual(history["pending_batches"], ["batch_00451"])
        self.assertEqual(history["cost_accounting"], self.ledger)
        for flag in ("no_cached_text_regenerated", "no_failed_content_resubmitted", "no_refused_content_resubmitted"):
            self.assertIs(history[flag], True)
        self.assertIs(history["extra_usage_activated"], False)
        self.assertEqual(history["preserved_provider_file_sha256"], {
            str(path.relative_to(self.root)): file_sha(path) for path in provider_before})
        self.assertEqual(self.provider_bytes(), provider_before)
        for name, expected in preserved.items():
            self.assertEqual((self.root / name).read_bytes(), expected)
        self.baseline.assert_called_once_with(self.root, self.config)
        self.defer.assert_called_once_with(self.root, self.batch)
        self.pending.assert_called_once_with(self.root, self.config)
        self.cost.assert_called_once_with(self.root, self.config, self.status)
        self.capture.assert_called_once_with(self.config, self.root)
        phases = [call[0] for call in self.order.mock_calls]
        self.assertLess(phases.index("defer"), phases.index("cost"))
        self.assertLess(phases.index("pending"), phases.index("capture"))
        self.assertLess(phases.index("cost"), phases.index("capture"))
        self.assertLess(phases.index("validator"), phases.index("state"))
        status = json.loads((self.root / "RUN_STATUS.json").read_text())
        self.assertEqual(status["state"], "reviewed_transport_deferred")
        self.assertEqual(status["detail"], {"batch": self.batch,
            "deferred_transport": str(self.deferred.relative_to(self.root)), "history": history_name})
        self.assertIn("reviewed_transport_deferred", campaign.CONTINUABLE)
        self.assertNotIn("provider_error", campaign.CONTINUABLE)
        self.assertFalse(self.prefix.with_suffix(".parsed.json").exists())
        self.provider.assert_not_called()
        self.worker.assert_not_called()

    def test_wrong_or_malformed_batch_is_rejected_before_review_or_quota_check(self):
        for batch in ("batch_00449", "batch_450", "../batch_00450", "batch_00450.raw.json", ""):
            with self.subTest(batch=batch):
                with self.assertRaises((RuntimeError, ValueError)):
                    self.resume(batch)
                self.assert_no_resume()
        self.baseline.assert_not_called()
        self.defer.assert_not_called()
        self.capture.assert_not_called()

    def test_both_job_stops_and_status_states_must_be_the_exact_provider_error(self):
        for filename, field in (("CAMPAIGN_JOB.json", "stop_reason"), ("JOB.json", "stop_reason"),
                                ("RUN_STATUS.json", "state"), ("CAMPAIGN_STATUS.json", "state")):
            for phase in ("provider_policy_refusal", "billing_or_credits_required", "account_quota_rejected",
                          "invalid_provider_output_no_retry", "included_quota_preflight_failed"):
                with self.subTest(filename=filename, phase=phase):
                    self.restore_status()
                    value = json.loads((self.root / filename).read_text())
                    value[field] = phase
                    dump(self.root / filename, value)
                    with self.assertRaises(RuntimeError):
                        self.resume()
                    self.assertFalse(any((self.root / "CAMPAIGN_HISTORY").glob("*.json")))
                    self.state.assert_not_called()
        self.defer.assert_not_called()
        self.capture.assert_not_called()
        self.provider.assert_not_called()
        self.worker.assert_not_called()

    def test_status_batch_details_must_match_the_explicit_transport_review(self):
        for filename in ("RUN_STATUS.json", "CAMPAIGN_STATUS.json"):
            for detail in ({"batch": "batch_00449"}, {}, None, "batch_00450"):
                with self.subTest(filename=filename, detail=detail):
                    self.restore_status()
                    value = json.loads((self.root / filename).read_text())
                    value["detail"] = detail
                    dump(self.root / filename, value)
                    with self.assertRaises(RuntimeError):
                        self.resume()
                    self.assertFalse(any((self.root / "CAMPAIGN_HISTORY").glob("*.json")))
                    self.state.assert_not_called()
        self.defer.assert_not_called()
        self.capture.assert_not_called()

    def test_live_unfinished_jobs_or_either_unresolved_lock_block_review(self):
        for filename in ("CAMPAIGN_JOB.json", "JOB.json"):
            for changes in ({"state": "running"}, {"state": "failed"}, {"pid": os.getpid()}):
                with self.subTest(filename=filename, changes=changes):
                    self.restore_status()
                    dump(self.root / filename, {**self.job, **changes})
                    with self.assertRaises(RuntimeError):
                        self.resume()
                    self.assert_no_resume()
        self.restore_status()
        for filename in ("CAMPAIGN_LOCK.json", "WORKER_LOCK.json"):
            with self.subTest(lock=filename):
                dump(self.root / filename, {"pid": -1})
                try:
                    with self.assertRaises(RuntimeError):
                        self.resume()
                    self.assert_no_resume()
                finally:
                    (self.root / filename).unlink()
        self.baseline.assert_not_called()
        self.defer.assert_not_called()
        self.capture.assert_not_called()

    def test_any_other_unreviewed_or_unknown_cost_blocks_continuation_after_review(self):
        for count in (1, 2, None):
            with self.subTest(unreviewed_costs=count):
                self.cost.return_value = count
                with self.assertRaises(RuntimeError):
                    self.resume()
                self.assertTrue(self.deferred.is_file())
                self.assert_no_resume()
        self.assertEqual(self.defer.call_count, 3)
        self.assertEqual(self.cost.call_count, 3)
        self.capture.assert_not_called()

    def test_baseline_integrity_failure_prevents_creating_a_review_entry(self):
        self.baseline.side_effect = RuntimeError("Synthetic baseline hash mismatch")
        with self.assertRaises(RuntimeError):
            self.resume()
        self.defer.assert_not_called()
        self.capture.assert_not_called()
        self.assert_no_resume()

    def test_nontransport_or_tampered_evidence_failure_never_authorizes_resume(self):
        self.defer.side_effect = RuntimeError("Synthetic cached attempt is not a valid transport failure")
        before = self.provider_bytes()
        with self.assertRaises(RuntimeError):
            self.resume()
        self.pending.assert_not_called()
        self.capture.assert_not_called()
        self.assertEqual(self.provider_bytes(), before)
        self.assert_no_resume()

    def test_pending_source_or_cache_integrity_failure_never_authorizes_resume(self):
        self.pending.side_effect = RuntimeError("Synthetic frozen source or cache hash mismatch")
        before = self.provider_bytes()
        with self.assertRaises(RuntimeError):
            self.resume()
        self.capture.assert_not_called()
        self.assertEqual(self.provider_bytes(), before)
        self.assert_no_resume()

    def test_failed_fresh_preflight_does_not_reuse_old_evidence_or_change_the_stop(self):
        dump(self.root / "LAST_SUBSCRIPTION_PREFLIGHT.json", {
            "state": "verified", "evidence_sha256": file_sha(self.evidence_path),
            "evidence_file": str(self.evidence_path.relative_to(self.root)),
        })
        self.capture.side_effect = RuntimeError("Synthetic fresh usage check failed")
        before = self.provider_bytes()
        with self.assertRaises(RuntimeError):
            self.resume()
        self.capture.assert_called_once_with(self.config, self.root)
        self.validator.assert_not_called()
        self.assertTrue(self.deferred.is_file())
        self.assertEqual(self.provider_bytes(), before)
        self.assert_no_resume()

    def test_paid_extra_usage_unknown_quota_wrong_account_or_stale_capture_cannot_resume(self):
        invalid = []
        for extra in (True, None):
            evidence = copy.deepcopy(self.evidence)
            evidence["usage"]["extra_usage"]["is_enabled"] = extra
            invalid.append(evidence)
        for primary in ({"utilization": 100, "locked_reason": None},
                        {"utilization": 2, "locked_reason": "locked"}, {}):
            evidence = copy.deepcopy(self.evidence)
            evidence["usage"]["five_hour"] = primary
            invalid.append(evidence)
        evidence = copy.deepcopy(self.evidence)
        evidence["account"]["orgName"] = "Different synthetic organization"
        invalid.append(evidence)
        invalid.append({**self.evidence, "read_only": False})
        invalid.append({**self.evidence, "checked_at_utc":
                        (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat()})
        for index, evidence in enumerate(invalid):
            with self.subTest(evidence=index):
                dump(self.evidence_path, evidence)
                with self.assertRaises(RuntimeError):
                    self.resume()
                self.assert_no_resume()
        self.assertEqual(self.capture.call_count, len(invalid))
        self.assertEqual(self.validator.call_count, len(invalid))


class TransportPendingIntegrationTests(unittest.TestCase):
    """Use real saved-evidence validation and current request fingerprints."""

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.batch = "batch_00001"
        self.prefix = self.root / "provider" / self.batch
        self.prompt_path = self.root / "prompt.txt"
        self.prompt = "Rewrite each synthetic source with direct and tentative confidence."
        self.prompt_path.write_text(self.prompt, encoding="utf-8")
        self.config = {"model": "claude-haiku-5-5", "batch_size": 5,
                       "max_output_tokens": 10000, "prompt_file": str(self.prompt_path)}
        self.sources = [{"review_id": f"HC{index:05d}", "source_id": f"synthetic-{index}",
                         "question": f"What is synthetic sample {index}?",
                         "original": f"Synthetic sample {index} contains test facts."}
                        for index in range(1, 11)]
        dump(self.root / "SOURCES.json", self.sources)
        self.request = {"model": self.config["model"], "prompt": self.prompt,
                        "request_sha256": fingerprint(self.config, self.prompt, self.sources[:5]),
                        "data": {"records": [request_record(row) for row in self.sources[:5]]}}
        self.raw = {"type": "result", "subtype": "success", "is_error": True,
                    "stop_reason": "stop_sequence", "result": IDLE_ERROR,
                    "modelUsage": {}, "usage": {"input_tokens": 0, "output_tokens": 0},
                    "total_cost_usd": 0, "api_error_status": None}
        self.events = [
            {"type": "system", "subtype": "init", "model": self.config["model"]},
            {"type": "assistant", "message": {"model": self.config["model"],
                "content": [{"type": "thinking", "thinking": "", "signature": ""}]}},
            {"type": "assistant", "message": {"model": "<synthetic>",
                "content": [{"type": "text", "text": IDLE_ERROR}]}},
            self.raw,
        ]
        dump(self.prefix.with_suffix(".request.json"), self.request)
        dump(self.prefix.with_suffix(".raw.json"), self.raw)
        self.prefix.with_suffix(".events.jsonl").write_text(
            "".join(json.dumps(event) + "\n" for event in self.events), encoding="utf-8")
        dump(self.prefix.with_suffix(".quota.json"), {"events": []})
        self.prefix.with_suffix(".stderr.txt").write_text("", encoding="utf-8")
        self.provider = self.patch("run_expansion.provider_stream")
        self.provider.side_effect = AssertionError("Pending validation must not call a provider")
        self.worker = self.patch("launch_expansion.worker")
        self.worker.side_effect = AssertionError("Pending validation must not launch a worker")

    def patch(self, target, **kwargs):
        patcher = mock.patch(target, **kwargs)
        self.addCleanup(patcher.stop)
        return patcher.start()

    def snapshot(self):
        return {path: path.read_bytes() for path in self.root.rglob("*") if path.is_file()}

    def assert_read_only_pending_rejection(self, config=None, message=None):
        before = self.snapshot()
        context = self.assertRaisesRegex(RuntimeError, message) if message else self.assertRaises(RuntimeError)
        with context:
            real_pending_batches(self.root, self.config if config is None else config)
        self.assertEqual(self.snapshot(), before)
        self.provider.assert_not_called()
        self.worker.assert_not_called()

    def test_real_pending_skips_only_reviewed_exact_batch_and_preserves_every_saved_byte(self):
        self.assert_read_only_pending_rejection(message="unresolved cached attempt")
        original_attempt = self.snapshot()
        entry = create_transport_defer(self.root, self.batch)
        for path, data in original_attempt.items():
            self.assertEqual(path.read_bytes(), data)
        before = self.snapshot()
        self.assertEqual(real_pending_batches(self.root, self.config), ["batch_00002"])
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(entry["request_sha256"], self.request["request_sha256"])
        self.assertEqual(entry["source_ids"], [row["review_id"] for row in self.sources[:5]])
        self.assertEqual(self.prefix.with_suffix(".raw.json").read_bytes(),
                         original_attempt[self.prefix.with_suffix(".raw.json")])
        self.assertFalse(self.prefix.with_suffix(".parsed.json").exists())
        self.provider.assert_not_called()
        self.worker.assert_not_called()

    def test_changed_current_request_settings_or_prompt_cannot_reuse_a_deferral(self):
        create_transport_defer(self.root, self.batch)
        for config in ({**self.config, "model": "different-synthetic-model"},
                       {**self.config, "max_output_tokens": 9999}):
            with self.subTest(config=config):
                self.assert_read_only_pending_rejection(config, "Current request differs")
        self.prompt_path.write_text(self.prompt + " Changed instructions.", encoding="utf-8")
        self.assert_read_only_pending_rejection(message="Current request differs")

    def test_changed_frozen_source_content_ids_or_order_cannot_be_skipped(self):
        create_transport_defer(self.root, self.batch)
        for change in ("content", "id", "order"):
            with self.subTest(change=change):
                sources = copy.deepcopy(self.sources)
                if change == "content":
                    sources[0]["original"] += " Changed fact."
                elif change == "id":
                    sources[0]["review_id"] = "HC99999"
                else:
                    sources[0], sources[1] = sources[1], sources[0]
                dump(self.root / "SOURCES.json", sources)
                self.assert_read_only_pending_rejection(message="Current request differs")

    def test_current_source_ids_are_checked_even_when_request_fingerprint_matches(self):
        create_transport_defer(self.root, self.batch)
        sources = copy.deepcopy(self.sources)
        sources[0]["review_id"] = "HC99999"
        dump(self.root / "SOURCES.json", sources)
        with mock.patch("launch_expansion.fingerprint", return_value=self.request["request_sha256"]):
            self.assert_read_only_pending_rejection(message="Current sources differ")

    def test_changed_original_request_or_raw_artifact_invalidates_review_before_skip(self):
        create_transport_defer(self.root, self.batch)
        request_path = self.prefix.with_suffix(".request.json")
        request_before = request_path.read_bytes()
        changed = copy.deepcopy(self.request)
        changed["data"]["records"][0]["id"] = "HC99999"
        dump(request_path, changed)
        self.assert_read_only_pending_rejection(message="evidence or file inventory changed")
        request_path.write_bytes(request_before)
        raw_path = self.prefix.with_suffix(".raw.json")
        raw_path.write_bytes(raw_path.read_bytes() + b"\n")
        self.assert_read_only_pending_rejection(message="evidence or file inventory changed")


if __name__ == "__main__":
    unittest.main()
