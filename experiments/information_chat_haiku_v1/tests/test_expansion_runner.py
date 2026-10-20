import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))
from run_expansion import dump, fingerprint, state, stop_signal


class ExpansionRunnerTests(unittest.TestCase):
    def test_normal_allowance_is_not_a_quota_failure(self):
        self.assertIsNone(stop_signal({"type": "rate_limit_event", "rate_limit_info": {"status": "allowed", "overageStatus": "rejected"}}))

    def test_quota_warning_stops(self):
        self.assertEqual(stop_signal({"type": "rate_limit_event", "rate_limit_info": {"status": "allowed_warning"}}), "account_quota_warning")

    def test_quota_rejection_stops(self):
        self.assertEqual(stop_signal({"type": "rate_limit_event", "rate_limit_info": {"status": "rejected"}}), "account_quota_rejected")

    def test_overage_stops(self):
        self.assertEqual(stop_signal({"type": "rate_limit_event", "rate_limit_info": {"status": "allowed", "isUsingOverage": True}}), "overage_use_reported")

    def test_internal_retry_stops(self):
        self.assertEqual(stop_signal({"type": "system", "subtype": "api_retry", "error_status": 429}), "provider_retry_requested_no_retry_permitted")

    def test_success_text_is_not_parsed_for_billing_words(self):
        self.assertIsNone(stop_signal({"type": "result", "subtype": "success", "is_error": False, "result": "The term billing means payment."}))

    def test_success_subtype_with_error_still_stops(self):
        self.assertEqual(stop_signal({"type": "result", "subtype": "success", "is_error": True, "result": "Usage credits required"}), "billing_or_credits_required")

    def test_call_cap_distinct_from_account_quota(self):
        self.assertEqual(stop_signal({"type": "result", "is_error": True, "subtype": "error_max_budget_usd"}), "per_call_estimate_safety_cap")

    def test_protocol_fingerprint_includes_output_cap(self):
        conf = {"model": "claude-haiku-5-5", "max_output_tokens": 10000}
        batch = [{"review_id": "HC051", "question": "What is X?", "original": "X is Y."}]
        original = fingerprint(conf, "prompt", batch)
        self.assertNotEqual(original, fingerprint({**conf, "max_output_tokens": 20000}, "prompt", batch))
        self.assertNotEqual(original, fingerprint(conf, "different", batch))

    def test_repair_costs_and_rejections_are_not_hidden(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            conf = {"target_sources": 10000, "max_call_budget_usd": .12, "max_incremental_cli_estimate_usd": 5}
            dump(root / "SOURCES.json", [{"reuse_canary": True}, {"reuse_canary": False}])
            for name, status, cost in [("provider", "ok", .1), ("provider_repairs_v1", "reject", .2)]:
                prefix = root / name / "batch_00001"
                dump(prefix.with_suffix(".parsed.json"), {"records": [{"id": "HC051", "status": status, "audit_flags": {}}]})
                dump(prefix.with_suffix(".request.json"), {})
                dump(prefix.with_suffix(".raw.json"), {"total_cost_usd": cost})
            current = state(root, conf, "test")
            self.assertEqual(current["total_generated_triplets"], 1)
            self.assertEqual(current["new_rejected_sources"], 1)
            self.assertAlmostEqual(current["incremental_cli_estimate_usd"], .3)


if __name__ == "__main__":
    unittest.main()
