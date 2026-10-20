"""Explicit included-quota policy changes dollar caps without weakening other stops."""
import copy
import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))
import run_expansion as expansion


class EstimateGuardPolicyTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.folder = Path(temporary.name).resolve()
        self.root = self.folder / "run"
        self.prompt = "Preserve source claims and create confident and hesitant versions."
        self.prompt_path = self.folder / "prompt.txt"
        self.prompt_path.write_text(self.prompt, encoding="utf-8")
        self.config_path = self.folder / "config.json"
        self.config = {
            "model": "claude-haiku-5-5", "max_output_tokens": 10000, "batch_size": 5,
            "target_sources": 10000, "max_call_budget_usd": 0.12,
            "max_incremental_cli_estimate_usd": 1, "timeout_seconds": 240,
            "expected_org_name": "Harvard Edu for FAS/SEAS", "private_dir": str(self.root),
            "prompt_file": str(self.prompt_path), "canary_approval": {"scope": "synthetic test"},
            "campaign": {"enabled": True, "quota_check_interval_seconds": 120},
            "stop_policy": {
                "stop_on_primary_quota_warning": True, "stop_on_quota_rejection": True,
                "stop_on_overage_use": True, "stop_on_billing_or_credits_prompt": True,
                "internal_provider_retries": 0, "automatic_batch_retries": 0,
                "enable_extra_usage": False, "account_or_model_fallback": False,
            },
        }
        self.disabled = {"enabled": False, "included_quota_only": True,
                         "extra_usage_must_be_disabled": True, "authorized_by_user": True}
        self.sources = [{"source_id": f"synthetic-{index}", "review_id": f"HC{index:05d}",
                         "question": f"What is synthetic sample {index}?",
                         "original": f"Synthetic sample {index} contains test facts."}
                        for index in range(1, 6)]
        expansion.dump(self.root / "SOURCES.json", self.sources)
        self.identity = {"loggedIn": True, "authMethod": "claude.ai", "apiProvider": "firstParty",
                         "subscriptionType": "enterprise", "orgName": self.config["expected_org_name"]}

    def disabled_config(self):
        return {**copy.deepcopy(self.config), "local_estimate_guard_policy": copy.deepcopy(self.disabled)}

    def run_main(self, config, args=(), *, preflight_error=None, identity=None, reason=None, unreviewed=0):
        expansion.dump(self.config_path, config)
        phases = []

        def record_state(root, received_config, phase, detail=None):
            self.assertEqual((root, received_config), (self.root, config))
            phases.append(phase)
            return {"state": phase, "detail": detail, "total_generated_triplets": 0,
                    "conservative_cli_estimate_reserved_usd": 999,
                    "incremental_cli_estimate_usd": 999, "new_generated_triplets": 0,
                    "new_sources_flagged_by_simple_checks": 0}

        with mock.patch.object(sys, "argv", ["run_expansion.py", "--config", str(self.config_path), *args]), \
                mock.patch.object(expansion.signal, "signal"), \
                mock.patch.object(expansion, "state", side_effect=record_state), \
                mock.patch.object(expansion, "unreviewed_cost_count", return_value=unreviewed), \
                mock.patch("subscription_preflight.ensure_subscription_preflight") as preflight, \
                mock.patch.object(expansion.subprocess, "run") as auth, \
                mock.patch.object(expansion, "provider_stream") as provider, \
                redirect_stdout(io.StringIO()):
            if preflight_error is not None:
                preflight.side_effect = RuntimeError(preflight_error)
            auth.return_value = SimpleNamespace(returncode=0,
                stdout=json.dumps(self.identity if identity is None else identity))
            if reason is None:
                provider.side_effect = AssertionError("No real provider call is permitted in policy tests")
            else:
                provider.return_value = (None, reason, 0)
            expansion.main()
            return phases, preflight, auth, provider

    def test_absent_or_explicitly_enabled_policy_preserves_default_guards(self):
        self.assertIs(expansion.local_estimate_guards_enabled({}), True)
        self.assertIs(expansion.local_estimate_guards_enabled(self.config), True)
        self.assertIs(expansion.local_estimate_guards_enabled({
            "local_estimate_guard_policy": {"enabled": True}}), True)
        self.assertIs(expansion.local_estimate_guards_enabled(self.disabled_config()), False)

    def test_malformed_policy_or_ambiguous_enabled_value_fails_closed(self):
        for policy in (None, [], "false", False, 0, {}, {"enabled": None},
                       {"enabled": 0}, {"enabled": 1}, {"enabled": "false"}):
            with self.subTest(policy=policy):
                with self.assertRaises(RuntimeError):
                    expansion.local_estimate_guards_enabled({**self.config, "local_estimate_guard_policy": policy})

    def test_disabling_requires_strict_explicit_authorization_and_included_quota_scope(self):
        for field in ("included_quota_only", "extra_usage_must_be_disabled", "authorized_by_user"):
            for value in (False, None, 1, "true"):
                with self.subTest(field=field, value=value):
                    config = self.disabled_config()
                    config["local_estimate_guard_policy"][field] = value
                    with self.assertRaises(RuntimeError):
                        expansion.local_estimate_guards_enabled(config)
            config = self.disabled_config()
            del config["local_estimate_guard_policy"][field]
            with self.assertRaises(RuntimeError):
                expansion.local_estimate_guards_enabled(config)

    def test_disabled_caps_require_enabled_campaign_and_the_approved_org(self):
        for campaign in (None, {}, {"enabled": False}, {"enabled": 1}, {"enabled": "true"}):
            with self.subTest(campaign=campaign):
                with self.assertRaises(RuntimeError):
                    expansion.local_estimate_guards_enabled({**self.disabled_config(), "campaign": campaign})
        for organization in (None, "Other synthetic organization", ""):
            with self.subTest(organization=organization):
                with self.assertRaises(RuntimeError):
                    expansion.local_estimate_guards_enabled({**self.disabled_config(), "expected_org_name": organization})

    def test_each_quota_billing_or_overage_stop_must_remain_strictly_enabled(self):
        fields = ("stop_on_primary_quota_warning", "stop_on_quota_rejection",
                  "stop_on_overage_use", "stop_on_billing_or_credits_prompt")
        for field in fields:
            for value in (False, None, 1, "true"):
                with self.subTest(field=field, value=value):
                    config = self.disabled_config()
                    config["stop_policy"][field] = value
                    with self.assertRaises(RuntimeError):
                        expansion.local_estimate_guards_enabled(config)
            config = self.disabled_config()
            del config["stop_policy"][field]
            with self.assertRaises(RuntimeError):
                expansion.local_estimate_guards_enabled(config)

    def test_disabling_caps_cannot_allow_stale_or_invalid_quota_check_intervals(self):
        for interval in (None, False, 0, -1, 121, "120", float("nan"), float("inf")):
            with self.subTest(interval=interval):
                config = self.disabled_config()
                config["campaign"]["quota_check_interval_seconds"] = interval
                with self.assertRaises(RuntimeError):
                    expansion.local_estimate_guards_enabled(config)

    def test_paid_usage_fallback_and_noninteger_or_nonzero_retries_are_rejected(self):
        for field in ("enable_extra_usage", "account_or_model_fallback"):
            for value in (True, None, 0, "false"):
                with self.subTest(field=field, value=value):
                    config = self.disabled_config()
                    config["stop_policy"][field] = value
                    with self.assertRaises(RuntimeError):
                        expansion.local_estimate_guards_enabled(config)
        for field in ("internal_provider_retries", "automatic_batch_retries"):
            for value in (False, None, 0.0, 1, -1, "0"):
                with self.subTest(field=field, value=value):
                    config = self.disabled_config()
                    config["stop_policy"][field] = value
                    with self.assertRaises(RuntimeError):
                        expansion.local_estimate_guards_enabled(config)
        for stop in (None, {}, []):
            with self.subTest(stop=stop):
                with self.assertRaises(RuntimeError):
                    expansion.local_estimate_guards_enabled({**self.disabled_config(), "stop_policy": stop})

    def test_provider_command_changes_only_the_local_dollar_cap_arguments(self):
        settings = self.folder / "synthetic_settings.json"
        original = expansion.provider_command(self.config, self.prompt, settings)
        uncapped = expansion.provider_command(self.disabled_config(), self.prompt, settings)
        self.assertEqual(original[-2:], ["--max-budget-usd", "0.12"])
        self.assertEqual(uncapped, original[:-2])
        self.assertNotIn("--max-budget-usd", uncapped)
        for option, value in (("--model", "claude-haiku-5-5"), ("--effort", "low"),
                              ("--tools", ""), ("--permission-mode", "dontAsk"),
                              ("--mcp-config", '{"mcpServers":{}}')):
            self.assertEqual(uncapped[uncapped.index(option) + 1], value)
        for option in ("--strict-mcp-config", "--disable-slash-commands", "--no-chrome", "--no-session-persistence"):
            self.assertIn(option, uncapped)

    def test_policy_change_does_not_change_existing_request_fingerprints(self):
        before = expansion.fingerprint(self.config, self.prompt, self.sources)
        self.assertEqual(expansion.fingerprint(self.disabled_config(), self.prompt, self.sources), before)
        changed_tokens = {**self.disabled_config(), "max_output_tokens": 9999}
        self.assertNotEqual(expansion.fingerprint(changed_tokens, self.prompt, self.sources), before)

    def test_cumulative_local_guard_still_stops_by_default(self):
        phases, preflight, auth, provider = self.run_main(self.config, ["--max-batches", "0"])
        self.assertEqual(phases[-1], "incremental_estimate_safety_cap")
        preflight.assert_not_called()
        auth.assert_not_called()
        provider.assert_not_called()

    def test_authorized_policy_bypasses_only_the_cumulative_estimate_comparison(self):
        phases, preflight, auth, provider = self.run_main(self.disabled_config(), ["--max-batches", "0"])
        self.assertEqual(phases[-1], "bounded_precheck_complete")
        self.assertNotIn("incremental_estimate_safety_cap", phases)
        preflight.assert_not_called()
        auth.assert_not_called()
        provider.assert_not_called()

    def test_unknown_attempt_cost_review_remains_required_when_caps_are_disabled(self):
        phases, preflight, auth, provider = self.run_main(self.disabled_config(), unreviewed=1)
        self.assertEqual(phases[-1], "unresolved_attempt_or_cost_requires_review")
        preflight.assert_not_called()
        auth.assert_not_called()
        provider.assert_not_called()

    def test_disabled_local_caps_do_not_bypass_failed_subscription_quota_checks(self):
        phases, preflight, auth, provider = self.run_main(
            self.disabled_config(), preflight_error="Synthetic included quota exhausted")
        self.assertEqual(phases[-1], "included_quota_preflight_failed")
        preflight.assert_called_once_with(self.disabled_config(), self.root)
        auth.assert_not_called()
        provider.assert_not_called()

    def test_disabled_local_caps_do_not_bypass_account_identity_verification(self):
        wrong = {**self.identity, "orgName": "Other synthetic organization"}
        phases, preflight, auth, provider = self.run_main(self.disabled_config(), identity=wrong)
        self.assertEqual(phases[-1], "account_verification_failed_no_fallback")
        preflight.assert_called_once()
        auth.assert_called_once()
        provider.assert_not_called()
        self.assertFalse((self.root / "provider" / "batch_00001.request.json").exists())

    def test_disabled_caps_preserve_token_timeout_environment_and_provider_stop_handling(self):
        with mock.patch.dict(os.environ, {"ANTHROPIC_API_KEY": "synthetic-secret-not-used",
                                         "CLAUDE_CODE_MAX_RETRIES": "99"}):
            phases, preflight, auth, provider = self.run_main(
                self.disabled_config(), reason="billing_or_credits_required")
        self.assertEqual(phases[-1], "billing_or_credits_required")
        preflight.assert_called_once()
        auth.assert_called_once()
        provider.assert_called_once()
        command, env, _, _, _, timeout = provider.call_args.args
        self.assertNotIn("--max-budget-usd", command)
        self.assertNotIn("ANTHROPIC_API_KEY", env)
        self.assertEqual(env["CLAUDE_CODE_MAX_RETRIES"], "0")
        self.assertEqual(env["MAX_THINKING_TOKENS"], "0")
        self.assertEqual(env["CLAUDE_CODE_MAX_OUTPUT_TOKENS"], "10000")
        self.assertEqual(timeout, 240)
        request = json.loads((self.root / "provider" / "batch_00001.request.json").read_text())
        self.assertEqual(request["internal_retries"], 0)
        self.assertEqual(request["account"]["orgName"], self.config["expected_org_name"])

    def test_future_provider_budget_errors_quota_billing_refusal_and_retry_events_still_stop(self):
        cases = [
            ({"type": "result", "is_error": True, "subtype": "error_max_budget_usd"},
             "per_call_estimate_safety_cap"),
            ({"type": "result", "is_error": True, "result": "Payment required"}, "billing_or_credits_required"),
            ({"type": "result", "is_error": True, "stop_reason": "refusal"}, "provider_policy_refusal"),
            ({"type": "rate_limit_event", "rate_limit_info": {"status": "rejected"}}, "account_quota_rejected"),
            ({"type": "rate_limit_event", "rate_limit_info": {"status": "allowed_warning"}}, "account_quota_warning"),
            ({"type": "rate_limit_event", "rate_limit_info": {"status": "allowed", "isUsingOverage": True}}, "overage_use_reported"),
            ({"type": "system", "subtype": "api_retry"}, "provider_retry_requested_no_retry_permitted"),
        ]
        self.assertIs(expansion.local_estimate_guards_enabled(self.disabled_config()), False)
        for event, reason in cases:
            with self.subTest(reason=reason):
                self.assertEqual(expansion.stop_signal(event), reason)

    def test_status_keeps_estimates_and_records_the_disabled_policy_without_claiming_an_invoice(self):
        config = self.disabled_config()
        status = expansion.state(self.root, config, "synthetic")
        self.assertIs(status["local_estimate_guards_enabled"], False)
        self.assertIs(status["cli_estimate_values_are_not_invoices"], True)
        self.assertIs(status["is_actual_invoice"], False)
        self.assertIn("incremental_cli_estimate_usd", status)
        self.assertEqual(status["incremental_cli_estimate_safety_cap_usd"], 1)
        self.assertIs(status["extra_usage_enabled_by_this_run"], False)
        self.assertIs(status["automatic_retry"], False)
        self.assertIs(status["account_fallback"], False)

    def test_invalid_disabled_policy_fails_before_runtime_artifact_writes_or_any_calls(self):
        config = self.disabled_config()
        config["stop_policy"]["enable_extra_usage"] = True
        expansion.dump(self.config_path, config)
        before = {path: path.read_bytes() for path in self.folder.rglob("*") if path.is_file()}
        with mock.patch.object(sys, "argv", ["run_expansion.py", "--config", str(self.config_path)]), \
                mock.patch.object(expansion.signal, "signal"), \
                mock.patch("subscription_preflight.ensure_subscription_preflight") as preflight, \
                mock.patch.object(expansion.subprocess, "run") as auth, \
                mock.patch.object(expansion, "provider_stream") as provider:
            with self.assertRaises(RuntimeError):
                expansion.main()
            preflight.assert_not_called()
            auth.assert_not_called()
            provider.assert_not_called()
        self.assertEqual({path: path.read_bytes() for path in self.folder.rglob("*") if path.is_file()}, before)


if __name__ == "__main__":
    unittest.main()
