import copy
import hashlib
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))
from run_campaign import prepare_verified_preflight_resume
from run_expansion import dump


def file_sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class VerifiedPreflightResumeTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.config = {"expected_org_name": "Harvard Edu for FAS/SEAS", "max_call_budget_usd": 0.12}
        now = datetime.now(timezone.utc)
        self.prior = {
            "state": "included_quota_preflight_failed",
            "updated_at_utc": (now - timedelta(seconds=60)).isoformat(),
            "detail": "Read-only subscription usage endpoint HTTP 429; no inference attempted",
            "calls_without_final_cost": 0,
        }
        self.job = {"state": "finished", "pid": -1, "stop_reason": self.prior["state"]}
        self.evidence = {
            "checked_at_utc": now.isoformat(),
            "read_only": True,
            "account": {
                "loggedIn": True,
                "authMethod": "claude.ai",
                "apiProvider": "firstParty",
                "subscriptionType": "enterprise",
                "orgName": self.config["expected_org_name"],
            },
            "usage": {
                "five_hour": {"utilization": 40, "locked_reason": None},
                "extra_usage": {"is_enabled": False},
            },
            "model_calls": 0,
            "billing_settings_changed": False,
        }
        self.evidence_path = self.root / "SUBSCRIPTION_PREFLIGHT" / "check_verified.json"
        self.marker = self.root / "LAST_SUBSCRIPTION_PREFLIGHT.json"
        dump(self.evidence_path, self.evidence)
        dump(self.root / "RUN_STATUS.json", self.prior)
        dump(self.root / "JOB.json", self.job)
        dump(self.root / "CAMPAIGN_JOB.json", self.job)
        dump(self.root / "CAMPAIGN_STATUS.json", {"state": self.prior["state"]})
        dump(self.root / "CAMPAIGN_LAUNCH.json", {"scope": "included quota only"})
        dump(self.root / "provider" / "batch_00179.raw.json", {"result": "immutable cached source"})
        dump(self.root / "provider_completions_batch_00179" / "batch_00001.raw.json", {"result": "immutable completion"})
        self.baseline = self.mock_dependency("run_campaign.preserve_baseline")
        self.pending = self.mock_dependency("run_campaign.pending_batches", return_value=["batch_00180"])
        self.state = self.mock_dependency("run_campaign.state", side_effect=self.write_verified_status)
        self.capture = self.mock_dependency("subscription_preflight.capture_subscription_preflight")
        self.provider = self.mock_dependency("run_campaign.subprocess.run")

    def mock_dependency(self, target, **kwargs):
        patcher = patch(target, **kwargs)
        self.addCleanup(patcher.stop)
        return patcher.start()

    def write_verified_status(self, root, config, reason, detail):
        self.assertEqual(root, self.root)
        self.assertEqual(config, self.config)
        self.assertEqual(reason, "included_quota_preflight_verified")
        self.assertTrue((root / "CAMPAIGN_HISTORY" / detail["history"]).is_file())
        updated = {**self.prior, "state": reason, "detail": detail}
        dump(root / "RUN_STATUS.json", updated)
        return updated

    def assert_rejected(self, evidence_path=None):
        before = {path: path.read_bytes() for path in self.root.rglob("*") if path.is_file()}
        with self.assertRaises(RuntimeError):
            prepare_verified_preflight_resume(self.root, self.config, evidence_path or self.evidence_path)
        self.baseline.assert_not_called()
        self.pending.assert_not_called()
        self.state.assert_not_called()
        self.capture.assert_not_called()
        self.provider.assert_not_called()
        self.assertFalse((self.root / "CAMPAIGN_HISTORY").exists())
        self.assertEqual({path: path.read_bytes() for path in self.root.rglob("*") if path.is_file()}, before)

    def test_fresh_verified_evidence_archives_cache_pins_then_marks_continuation_ready(self):
        before = {path: path.read_bytes() for path in self.root.rglob("*") if path.is_file()}
        name = prepare_verified_preflight_resume(self.root, self.config, self.evidence_path)
        history = json.loads((self.root / "CAMPAIGN_HISTORY" / name).read_text())
        self.assertEqual(history["previous_status"], self.prior)
        self.assertEqual(history["previous_jobs"], {"CAMPAIGN_JOB.json": self.job, "JOB.json": self.job})
        self.assertEqual(history["preflight_file"], str(self.evidence_path.relative_to(self.root)))
        self.assertEqual(history["preflight_sha256"], file_sha256(self.evidence_path))
        self.assertEqual(history["pending_batches"], ["batch_00180"])
        self.assertIs(history["extra_usage_activated"], False)
        self.assertIs(history["no_cached_text_regenerated"], True)
        self.assertEqual(history["preserved_provider_file_sha256"], {
            str(path.relative_to(self.root)): hashlib.sha256(data).hexdigest()
            for path, data in before.items() if path.parent.name.startswith("provider")
        })
        for path, data in before.items():
            if path.name != "RUN_STATUS.json":
                self.assertEqual(path.read_bytes(), data)
        self.assertEqual(json.loads((self.root / "RUN_STATUS.json").read_text())["state"],
                         "included_quota_preflight_verified")
        self.baseline.assert_called_once_with(self.root, self.config)
        self.pending.assert_called_once_with(self.root, self.config)
        self.state.assert_called_once_with(self.root, self.config, "included_quota_preflight_verified", {"history": name})
        self.capture.assert_not_called()
        self.provider.assert_not_called()

    def test_latest_verified_marker_must_pin_the_same_fresh_evidence(self):
        dump(self.marker, {"state": "verified", "evidence_sha256": file_sha256(self.evidence_path)})
        marker_before = self.marker.read_bytes()
        name = prepare_verified_preflight_resume(self.root, self.config, self.evidence_path)
        self.assertTrue((self.root / "CAMPAIGN_HISTORY" / name).is_file())
        self.assertEqual(self.marker.read_bytes(), marker_before)
        self.capture.assert_not_called()
        self.provider.assert_not_called()

    def test_evidence_must_be_newer_than_the_stopped_check_and_still_fresh(self):
        timestamps = [
            self.prior["updated_at_utc"],
            (datetime.fromisoformat(self.prior["updated_at_utc"]) - timedelta(seconds=1)).isoformat(),
            (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat(),
        ]
        for timestamp in timestamps:
            with self.subTest(timestamp=timestamp):
                dump(self.evidence_path, {**self.evidence, "checked_at_utc": timestamp})
                self.assert_rejected()

    def test_evidence_outside_this_runs_private_directory_is_rejected(self):
        alternate = self.root / "elsewhere" / "check_verified.json"
        dump(alternate, self.evidence)
        self.assert_rejected(alternate)

    def test_paid_extra_usage_or_exhausted_included_quota_cannot_resume(self):
        for usage in [
            {**self.evidence["usage"], "extra_usage": {"is_enabled": True}},
            {**self.evidence["usage"], "extra_usage": {}},
            {**self.evidence["usage"], "five_hour": {"utilization": 100, "locked_reason": None}},
        ]:
            with self.subTest(usage=usage):
                dump(self.evidence_path, {**self.evidence, "usage": usage})
                self.assert_rejected()

    def test_other_terminal_failures_and_mismatched_job_stops_cannot_resume(self):
        for reason in [
            "provider_policy_refusal", "account_quota_rejected", "billing_or_credits_required",
            "invalid_provider_output_no_retry", "provider_error",
        ]:
            with self.subTest(reason=reason):
                dump(self.root / "RUN_STATUS.json", {**self.prior, "state": reason})
                dump(self.root / "JOB.json", {**self.job, "stop_reason": reason})
                dump(self.root / "CAMPAIGN_JOB.json", {**self.job, "stop_reason": reason})
                self.assert_rejected()
        dump(self.root / "RUN_STATUS.json", self.prior)
        for filename in ("JOB.json", "CAMPAIGN_JOB.json"):
            with self.subTest(mismatched_job=filename):
                dump(self.root / "JOB.json", self.job)
                dump(self.root / "CAMPAIGN_JOB.json", self.job)
                dump(self.root / filename, {**self.job, "stop_reason": "account_quota_rejected"})
                self.assert_rejected()

    def test_locks_unfinished_jobs_and_live_jobs_prevent_resume(self):
        for filename in ("WORKER_LOCK.json", "CAMPAIGN_LOCK.json"):
            with self.subTest(lock=filename):
                dump(self.root / filename, {"pid": -1})
                self.assert_rejected()
                (self.root / filename).unlink()
        for filename in ("JOB.json", "CAMPAIGN_JOB.json"):
            for changes in ({"state": "running"}, {"state": "failed"}, {"pid": os.getpid()}):
                with self.subTest(job=filename, changes=changes):
                    dump(self.root / filename, {**self.job, **changes})
                    self.assert_rejected()
                    dump(self.root / filename, self.job)

    def test_unresolved_or_unknown_provider_costs_prevent_resume(self):
        for value in (1, None):
            with self.subTest(calls_without_final_cost=value):
                dump(self.root / "RUN_STATUS.json", {**self.prior, "calls_without_final_cost": value})
                self.assert_rejected()
        missing = dict(self.prior)
        missing.pop("calls_without_final_cost")
        dump(self.root / "RUN_STATUS.json", missing)
        self.assert_rejected()

    def test_latest_failed_marker_wrong_hash_and_tampered_evidence_prevent_resume(self):
        for marker in [
            {"state": "failed", "evidence_sha256": file_sha256(self.evidence_path)},
            {"state": "verified", "evidence_sha256": "0" * 64},
            {"state": "verified"},
        ]:
            with self.subTest(marker=marker):
                dump(self.marker, marker)
                self.assert_rejected()
        dump(self.marker, {"state": "verified", "evidence_sha256": file_sha256(self.evidence_path)})
        modified = copy.deepcopy(self.evidence)
        modified["usage"]["five_hour"]["utilization"] = 41
        dump(self.evidence_path, modified)
        self.assert_rejected()


if __name__ == "__main__":
    unittest.main()
