"""Fresh quota evidence is reused only while the latest check stays verified."""
import copy
import io
import json
import sys
import tempfile
import unittest
import urllib.error
from contextlib import ExitStack
from datetime import datetime, timedelta, timezone
from email.message import Message
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))
import subscription_preflight as preflight
from run_expansion import dump, file_sha


class PreflightFreshCacheTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.config = {"expected_org_name": "Harvard Edu for FAS/SEAS",
                       "campaign": {"quota_check_interval_seconds": 120}}
        self.account = {"loggedIn": True, "authMethod": "claude.ai", "apiProvider": "firstParty",
                        "subscriptionType": "enterprise", "orgName": self.config["expected_org_name"]}
        self.usage = {"five_hour": {"utilization": 2.0, "locked_reason": None},
                      "extra_usage": {"is_enabled": False}}
        self.marker = self.root / preflight.LAST_PREFLIGHT_FILE
        self.path = self.root / "SUBSCRIPTION_PREFLIGHT" / "check_fixture.json"

    def verified_fixture(self, age=20, evidence_change=None):
        evidence = {"checked_at_utc": (datetime.now(timezone.utc) - timedelta(seconds=age)).isoformat(),
                    "read_only": True, "account": copy.deepcopy(self.account), "usage": copy.deepcopy(self.usage)}
        if evidence_change:
            evidence_change(evidence)
        dump(self.path, evidence)
        dump(self.marker, {"state": "verified", "checked_at_utc": evidence["checked_at_utc"],
                           "evidence_file": str(self.path.relative_to(self.root)),
                           "evidence_sha256": file_sha(self.path)})
        return evidence

    def transport(self, *, error=None, usage=None, auth_error=False):
        stack = ExitStack()
        self.addCleanup(stack.close)
        secret = "SYNTHETIC-TOKEN-NEVER-SAVE"

        def command(args, **kwargs):
            if args[0] == "claude":
                self.assertEqual(json.loads(self.marker.read_text())["state"], "checking")
                return SimpleNamespace(returncode=1 if auth_error else 0, stdout=json.dumps(self.account))
            self.assertEqual(args[:2], ["security", "find-generic-password"])
            return SimpleNamespace(returncode=0, stdout=json.dumps({"claudeAiOauth": {"accessToken": secret}}))

        commands = stack.enter_context(mock.patch.object(preflight.subprocess, "run", side_effect=command))
        opener = mock.Mock()
        if error:
            opener.open.side_effect = error
        else:
            opener.open.side_effect = lambda *args, **kwargs: io.StringIO(json.dumps(self.usage if usage is None else usage))
        stack.enter_context(mock.patch.object(preflight.urllib.request, "build_opener", return_value=opener))
        return commands, opener

    def test_fresh_marked_verified_evidence_is_reused_without_api_or_writes(self):
        self.verified_fixture()
        before = {path: path.read_bytes() for path in self.root.rglob("*") if path.is_file()}
        with mock.patch.object(preflight, "capture_subscription_preflight") as fresh, \
             mock.patch.object(preflight.subprocess, "run") as commands, \
             mock.patch.object(preflight.urllib.request, "build_opener") as network:
            self.assertEqual(preflight.ensure_subscription_preflight(self.config, self.root), self.path)
        fresh.assert_not_called()
        commands.assert_not_called()
        network.assert_not_called()
        self.assertEqual({path: path.read_bytes() for path in self.root.rglob("*") if path.is_file()}, before)

    def test_stale_evidence_performs_one_fresh_check_and_marks_new_evidence(self):
        self.verified_fixture(age=121)
        commands, opener = self.transport()
        result = preflight.ensure_subscription_preflight(self.config, self.root)
        self.assertNotEqual(result, self.path)
        self.assertEqual(commands.call_count, 2)
        opener.open.assert_called_once()
        marker = json.loads(self.marker.read_text())
        self.assertEqual(marker["state"], "verified")
        self.assertEqual(marker["evidence_file"], str(result.relative_to(self.root)))
        self.assertEqual(marker["evidence_sha256"], file_sha(result))
        self.assertEqual(preflight.ensure_subscription_preflight(self.config, self.root), result)
        opener.open.assert_called_once()

    def test_configured_interval_and_120_second_ceiling_both_limit_reuse(self):
        for interval, age in ((30, 45), (300, 121), (0, 1)):
            with self.subTest(interval=interval, age=age):
                self.verified_fixture(age=age)
                config = {**self.config, "campaign": {"quota_check_interval_seconds": interval}}
                with mock.patch.object(preflight, "capture_subscription_preflight", return_value=self.root / "fresh.json") as fresh:
                    self.assertEqual(preflight.ensure_subscription_preflight(config, self.root), self.root / "fresh.json")
                fresh.assert_called_once_with(config, self.root)

    def test_failed_or_checking_marker_prevents_fallback_to_recent_success(self):
        for state in ("failed", "checking"):
            with self.subTest(state=state):
                self.verified_fixture()
                old_evidence = self.path.read_bytes()
                dump(self.marker, {"state": state})
                with mock.patch.object(preflight, "capture_subscription_preflight", side_effect=RuntimeError("Fresh check failed")) as fresh:
                    with self.assertRaisesRegex(RuntimeError, "Fresh check failed"):
                        preflight.ensure_subscription_preflight(self.config, self.root)
                fresh.assert_called_once_with(self.config, self.root)
                self.assertEqual(self.path.read_bytes(), old_evidence)

    def test_unmarked_evidence_cannot_be_used_as_a_cache(self):
        self.verified_fixture()
        self.marker.unlink()
        with mock.patch.object(preflight, "capture_subscription_preflight", return_value=self.root / "fresh.json") as fresh:
            self.assertEqual(preflight.ensure_subscription_preflight(self.config, self.root), self.root / "fresh.json")
        fresh.assert_called_once()

    def test_changed_hash_timestamp_path_or_malformed_marker_forces_fresh_check(self):
        for change in ("evidence", "hash", "timestamp", "outside_path", "malformed"):
            with self.subTest(change=change):
                self.verified_fixture()
                marker = json.loads(self.marker.read_text())
                if change == "evidence":
                    evidence = json.loads(self.path.read_text())
                    evidence["usage"]["five_hour"]["utilization"] = 3.0
                    dump(self.path, evidence)
                elif change == "hash":
                    marker["evidence_sha256"] = "0" * 64
                    dump(self.marker, marker)
                elif change == "timestamp":
                    marker["checked_at_utc"] = datetime.now(timezone.utc).isoformat()
                    dump(self.marker, marker)
                elif change == "outside_path":
                    marker["evidence_file"] = "../outside.json"
                    dump(self.marker, marker)
                else:
                    self.marker.write_text("not JSON", encoding="utf-8")
                with mock.patch.object(preflight, "capture_subscription_preflight", return_value=self.root / "fresh.json") as fresh:
                    self.assertEqual(preflight.ensure_subscription_preflight(self.config, self.root), self.root / "fresh.json")
                fresh.assert_called_once()

    def test_locked_exhausted_extra_usage_or_wrong_account_even_with_valid_hash_forces_fresh_check(self):
        changes = (
            lambda value: value["usage"]["five_hour"].update(locked_reason="locked"),
            lambda value: value["usage"]["five_hour"].update(utilization=100),
            lambda value: value["usage"]["extra_usage"].update(is_enabled=True),
            lambda value: value["account"].update(orgName="Different organization"),
        )
        for change in changes:
            with self.subTest(change=change):
                self.verified_fixture(evidence_change=change)
                with mock.patch.object(preflight, "capture_subscription_preflight", return_value=self.root / "fresh.json") as fresh:
                    self.assertEqual(preflight.ensure_subscription_preflight(self.config, self.root), self.root / "fresh.json")
                fresh.assert_called_once()

    def test_explicit_capture_always_checks_fresh_despite_verified_cache(self):
        self.verified_fixture()
        commands, opener = self.transport()
        first = preflight.capture_subscription_preflight(self.config, self.root)
        second = preflight.capture_subscription_preflight(self.config, self.root)
        self.assertNotEqual(first, self.path)
        self.assertNotEqual(first, second)
        self.assertEqual(commands.call_count, 4)
        self.assertEqual(opener.open.call_count, 2)

    def test_http_429_marks_failure_and_saves_only_numeric_retry_delay(self):
        self.verified_fixture()
        headers = Message()
        headers["Retry-After"] = "12"
        headers["X-Sensitive-Test"] = "DO-NOT-SAVE-HEADERS"
        error = urllib.error.HTTPError(preflight.USAGE_URL, 429, "DO-NOT-SAVE-ERROR-BODY", headers, None)
        self.addCleanup(error.close)
        _, opener = self.transport(error=error)
        with self.assertRaises(preflight.SubscriptionPreflightHTTPError) as raised:
            preflight.capture_subscription_preflight(self.config, self.root)
        self.assertEqual(raised.exception.http_status, 429)
        self.assertEqual(raised.exception.retry_after_seconds, 12)
        opener.open.assert_called_once()
        marker = json.loads(self.marker.read_text())
        self.assertEqual(marker["state"], "failed")
        self.assertEqual(marker["http_status"], 429)
        self.assertEqual(marker["retry_after_seconds"], 12)
        self.assertNotIn("evidence_file", marker)
        saved = self.marker.read_text()
        for sensitive in ("SYNTHETIC-TOKEN-NEVER-SAVE", "DO-NOT-SAVE-HEADERS", "DO-NOT-SAVE-ERROR-BODY", "Authorization"):
            self.assertNotIn(sensitive, saved)
        with mock.patch.object(preflight, "capture_subscription_preflight", side_effect=RuntimeError("No fallback")) as fresh:
            with self.assertRaisesRegex(RuntimeError, "No fallback"):
                preflight.ensure_subscription_preflight(self.config, self.root)
        fresh.assert_called_once()

    def test_invalid_retry_after_is_omitted_and_never_retried(self):
        for delay in ("not-a-number", "-2", "NaN", "Infinity", "Mon, 19 Oct 2026 12:00:00 GMT"):
            with self.subTest(delay=delay):
                with mock.patch.object(preflight, "_capture_subscription_preflight",
                                       side_effect=preflight.SubscriptionPreflightHTTPError(429, preflight._retry_after_seconds(delay))) as fresh:
                    with self.assertRaises(preflight.SubscriptionPreflightHTTPError):
                        preflight.capture_subscription_preflight(self.config, self.root)
                fresh.assert_called_once()
                self.assertNotIn("retry_after_seconds", json.loads(self.marker.read_text()))

    def test_auth_failure_and_locked_fresh_response_leave_failed_marker(self):
        for auth_error in (True, False):
            with self.subTest(auth_error=auth_error):
                self.verified_fixture()
                locked = copy.deepcopy(self.usage)
                locked["five_hour"]["locked_reason"] = "quota_exhausted"
                commands, opener = self.transport(auth_error=auth_error, usage=locked)
                with self.assertRaises(RuntimeError):
                    preflight.capture_subscription_preflight(self.config, self.root)
                self.assertEqual(json.loads(self.marker.read_text())["state"], "failed")
                self.assertEqual(opener.open.call_count, 0 if auth_error else 1)


if __name__ == "__main__":
    unittest.main()
