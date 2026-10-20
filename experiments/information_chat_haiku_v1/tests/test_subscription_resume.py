"""Subscription-only continuation guards; fixtures never call a provider."""
import copy
import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

from subscription_preflight import validate_subscription_preflight
from launch_expansion import prepare_included_quota_resume
from run_expansion import dump, file_sha


class SubscriptionPreflightTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.path = self.root / "SUBSCRIPTION_PREFLIGHT.json"
        self.config = {"expected_org_name": "Harvard Edu for FAS/SEAS"}
        self.evidence = {
            "checked_at_utc": datetime.now(timezone.utc).isoformat(),
            "read_only": True,
            "account": {
                "loggedIn": True,
                "authMethod": "claude.ai",
                "apiProvider": "firstParty",
                "subscriptionType": "enterprise",
                "orgName": self.config["expected_org_name"],
            },
            "usage": {
                "five_hour": {"utilization": 2.0, "locked_reason": None},
                "extra_usage": {"is_enabled": False, "user_disabled": True},
            },
        }

    def save(self, evidence=None):
        self.path.write_text(json.dumps(evidence or self.evidence), encoding="utf-8")
        return self.path

    def validate(self, evidence=None):
        self.save(evidence)
        return validate_subscription_preflight(self.path, self.config)

    def test_fresh_included_quota_with_disabled_extra_usage_is_allowed(self):
        self.save()
        before = self.path.read_bytes()
        result = validate_subscription_preflight(self.path, self.config)
        self.assertIsInstance(result, dict)
        self.assertEqual(result["usage"]["five_hour"]["utilization"], 2.0)
        self.assertIs(result["usage"]["extra_usage"]["is_enabled"], False)
        self.assertEqual(self.path.read_bytes(), before)

    def test_stale_future_or_missing_timestamp_is_rejected(self):
        for checked in (
            (datetime.now(timezone.utc) - timedelta(minutes=6)).isoformat(),
            (datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat(),
            datetime.now().isoformat(),
            "not-a-time",
            None,
        ):
            with self.subTest(checked_at_utc=checked):
                changed = copy.deepcopy(self.evidence)
                changed["checked_at_utc"] = checked
                with self.assertRaises(RuntimeError):
                    self.validate(changed)

    def test_wrong_or_unknown_account_cannot_enable_continuation(self):
        for key, value in (
            ("loggedIn", False),
            ("authMethod", "apiKey"),
            ("apiProvider", "thirdParty"),
            ("subscriptionType", "pro"),
            ("orgName", "Different organization"),
            ("orgName", None),
        ):
            with self.subTest(key=key, value=value):
                changed = copy.deepcopy(self.evidence)
                changed["account"][key] = value
                with self.assertRaises(RuntimeError):
                    self.validate(changed)

    def test_extra_usage_must_be_explicitly_disabled(self):
        for value in (True, None, "false", 0):
            with self.subTest(is_enabled=value):
                changed = copy.deepcopy(self.evidence)
                changed["usage"]["extra_usage"]["is_enabled"] = value
                with self.assertRaises(RuntimeError):
                    self.validate(changed)
        changed = copy.deepcopy(self.evidence)
        del changed["usage"]["extra_usage"]
        with self.assertRaises(RuntimeError):
            self.validate(changed)

    def test_locked_or_exhausted_or_unknown_quota_is_rejected(self):
        for utilization in (100, 110, -1, float("nan"), float("inf"), None, "2.0", True):
            with self.subTest(utilization=utilization):
                changed = copy.deepcopy(self.evidence)
                changed["usage"]["five_hour"]["utilization"] = utilization
                with self.assertRaises(RuntimeError):
                    self.validate(changed)
        changed = copy.deepcopy(self.evidence)
        changed["usage"]["five_hour"]["locked_reason"] = "quota_exhausted"
        with self.assertRaises(RuntimeError):
            self.validate(changed)
        changed = copy.deepcopy(self.evidence)
        del changed["usage"]["five_hour"]["locked_reason"]
        with self.assertRaises(RuntimeError):
            self.validate(changed)
        changed = copy.deepcopy(self.evidence)
        del changed["usage"]["five_hour"]
        with self.assertRaises(RuntimeError):
            self.validate(changed)

    def test_evidence_must_be_a_read_only_preflight(self):
        for value in (False, None, "true", 1):
            with self.subTest(read_only=value):
                changed = copy.deepcopy(self.evidence)
                changed["read_only"] = value
                with self.assertRaises(RuntimeError):
                    self.validate(changed)

    def test_available_or_absent_weekly_buckets_allow_included_quota(self):
        for bucket in (None, {"utilization": 12.0, "locked_reason": None}, {"utilization": 12.0}):
            with self.subTest(bucket=bucket):
                changed = copy.deepcopy(self.evidence)
                changed["usage"]["seven_day"] = bucket
                changed["usage"]["seven_day_haiku"] = bucket
                self.assertIsInstance(self.validate(changed), dict)

    def test_exhausted_locked_or_unknown_non_null_weekly_bucket_is_rejected(self):
        for name in ("seven_day", "seven_day_haiku", "seven_day_sonnet"):
            for bucket in (
                {"utilization": 100, "locked_reason": None},
                {"utilization": 2.0, "locked_reason": "weekly_limit"},
                {"utilization": None, "locked_reason": None},
                {"utilization": True, "locked_reason": None},
                {"utilization": float("nan"), "locked_reason": None},
                "unknown",
            ):
                with self.subTest(name=name, bucket=bucket):
                    changed = copy.deepcopy(self.evidence)
                    changed["usage"][name] = bucket
                    with self.assertRaises(RuntimeError):
                        self.validate(changed)

    def test_missing_evidence_is_rejected_without_writing_a_replacement(self):
        with self.assertRaises((RuntimeError, FileNotFoundError)):
            validate_subscription_preflight(self.path, self.config)
        self.assertFalse(self.path.exists())


class IncludedQuotaResumeTests(unittest.TestCase):
    def setUp(self):
        SubscriptionPreflightTests.setUp(self)
        self.config.update({
            "max_incremental_cli_estimate_usd": 5.0,
            "max_call_budget_usd": 0.12,
            "batch_size": 5,
            "target_sources": 10000,
        })
        self.job_path = self.root / "JOB.json"
        self.status_path = self.root / "RUN_STATUS.json"
        self.launch_path = self.root / "LAUNCH.json"
        self.sources_path = self.root / "SOURCES.json"
        dump(self.job_path, {
            "pid": -1, "state": "finished",
            "stop_reason": "incremental_estimate_safety_cap",
        })
        dump(self.status_path, {
            "state": "incremental_estimate_safety_cap",
            "incremental_cli_estimate_safety_cap_usd": 5.0,
            "conservative_cli_estimate_reserved_usd": 4.93177815,
            "calls_without_final_cost": 0,
            "total_generated_triplets": 455,
        })
        dump(self.launch_path, {"pid": -1, "resume_history": None})
        dump(self.sources_path, [])
        self.completed = self.root / "provider" / "batch_00082.parsed.json"
        dump(self.completed, {"request_sha256": "a" * 64, "records": []})
        SubscriptionPreflightTests.save(self)
        self.pending = [f"batch_{i:05d}" for i in range(83, 109)]

    def resume(self):
        with patch("launch_expansion.pending_batches", return_value=self.pending):
            return prepare_included_quota_resume(self.root, self.config, self.path)

    def test_cap_is_finite_for_only_untouched_pool_and_evidence_is_preserved(self):
        originals = {path: path.read_bytes() for path in (
            self.job_path, self.status_path, self.launch_path,
            self.sources_path, self.completed, self.path,
        )}
        original_config = copy.deepcopy(self.config)
        name, changed = self.resume()
        history = json.loads((self.root / "RESUME_HISTORY" / name).read_text())

        self.assertEqual(changed["max_incremental_cli_estimate_usd"], 8.06)
        self.assertEqual(self.config, original_config)
        self.assertEqual(history["previous_config"], original_config)
        self.assertEqual(history["previous_status"]["total_generated_triplets"], 455)
        self.assertEqual(history["sources_sha256"], file_sha(self.sources_path))
        self.assertEqual(history["preserved_file_sha256"]["provider/batch_00082.parsed.json"], file_sha(self.completed))
        self.assertEqual(changed["subscription_only_continuation"]["pending_batches"], self.pending)
        self.assertTrue(changed["subscription_only_continuation"]["this_is_not_payment_authorization"])
        self.assertTrue(history["no_completed_batch_retry"])
        self.assertTrue(history["no_extra_usage_activation"])
        for path, value in originals.items():
            with self.subTest(path=path.name):
                self.assertEqual(path.read_bytes(), value)

    def test_quota_billing_refusal_and_format_stops_cannot_use_local_guard_path(self):
        original = json.loads(self.status_path.read_text())
        for reason in (
            "account_quota_warning", "account_quota_rejected", "account_quota_or_rate_limit",
            "overage_use_reported", "billing_or_credits_required", "provider_policy_refusal",
            "provider_error", "invalid_provider_output_no_retry", "prepared_source_pool_exhausted",
        ):
            with self.subTest(reason=reason):
                dump(self.status_path, {**original, "state": reason})
                with self.assertRaises(RuntimeError):
                    self.resume()
                self.assertFalse((self.root / "RESUME_HISTORY").exists())

    def test_live_or_unresolved_worker_cannot_resume(self):
        with patch("launch_expansion.alive", return_value=True):
            with self.assertRaises(RuntimeError):
                self.resume()
        dump(self.root / "WORKER_LOCK.json", {"pid": -1})
        with self.assertRaises(RuntimeError):
            self.resume()
        self.assertFalse((self.root / "RESUME_HISTORY").exists())

    def test_unknown_cost_or_changed_existing_cap_requires_review(self):
        original = json.loads(self.status_path.read_text())
        for field, value in (
            ("calls_without_final_cost", 1),
            ("incremental_cli_estimate_safety_cap_usd", 6.0),
        ):
            with self.subTest(field=field):
                dump(self.status_path, {**original, field: value})
                with self.assertRaises(RuntimeError):
                    self.resume()
                self.assertFalse((self.root / "RESUME_HISTORY").exists())

    def test_no_pending_work_does_not_increase_cap(self):
        self.pending = []
        with self.assertRaises(RuntimeError):
            self.resume()
        self.assertFalse((self.root / "RESUME_HISTORY").exists())

    def test_stale_preflight_cannot_authorize_launcher(self):
        self.evidence["checked_at_utc"] = (datetime.now(timezone.utc) - timedelta(minutes=6)).isoformat()
        SubscriptionPreflightTests.save(self)
        with self.assertRaises(RuntimeError):
            self.resume()
        self.assertFalse((self.root / "RESUME_HISTORY").exists())


if __name__ == "__main__":
    unittest.main()
