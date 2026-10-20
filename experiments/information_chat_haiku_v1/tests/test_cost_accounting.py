"""Unknown transport usage stays reserved and only pinned review can clear gates."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))
from cost_accounting import IDLE_TRANSPORT_ERROR, cost_accounting, unreviewed_cost_count


class CostAccountingTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.config = {"max_call_budget_usd": 0.12}
        self.deferrals_patch = mock.patch("transport_defer.deferred_transport_batches", return_value=[])
        self.deferrals = self.deferrals_patch.start()
        self.addCleanup(self.deferrals_patch.stop)

    def save(self, path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding="utf-8")

    def attempt(self, batch="batch_00450", directory="provider", raw=None, missing_raw=False):
        prefix = self.root / directory / batch
        self.save(prefix.with_suffix(".request.json"), {"request_sha256": "a" * 64})
        if not missing_raw:
            self.save(prefix.with_suffix(".raw.json"), {"total_cost_usd": 0.01} if raw is None else raw)
        return prefix.with_suffix(".request.json")

    def idle_failure(self, **change):
        return {"type": "result", "is_error": True, "result": IDLE_TRANSPORT_ERROR,
                "stop_reason": "stop_sequence", "modelUsage": {}, "total_cost_usd": 0, **change}

    def test_zero_reported_idle_failure_is_unknown_before_review(self):
        request = self.attempt(raw=self.idle_failure())
        before = {path: path.read_bytes() for path in request.parent.glob("*")}
        ledger = cost_accounting(self.root, self.config)
        self.assertEqual(ledger["incremental_cli_estimate_usd"], 0)
        self.assertEqual(ledger["calls_without_final_cost"], 1)
        self.assertEqual(ledger["reviewed_deferred_transport_calls_without_final_cost"], 0)
        self.assertEqual(ledger["unreviewed_calls_without_final_cost"], 1)
        self.assertEqual(ledger["unknown_cli_estimate_reserve_usd"], 0.12)
        self.assertEqual(ledger["conservative_cli_estimate_reserved_usd"], 0.12)
        self.assertEqual(ledger["uncertain_usage_attempts"], [str(request.relative_to(self.root))])
        self.assertIs(ledger["uncertain_usage_estimates_not_invoices"], True)
        self.assertEqual({path: path.read_bytes() for path in request.parent.glob("*")}, before)

    def test_reviewed_idle_failure_remains_unknown_and_reserved_but_can_clear_its_gate(self):
        self.attempt(raw=self.idle_failure())
        self.deferrals.return_value = [{"batch": "batch_00450"}]
        ledger = cost_accounting(self.root, self.config)
        self.assertEqual(ledger["calls_without_final_cost"], 1)
        self.assertEqual(ledger["reviewed_deferred_transport_calls_without_final_cost"], 1)
        self.assertEqual(ledger["unreviewed_calls_without_final_cost"], 0)
        self.assertEqual(ledger["conservative_cli_estimate_reserved_usd"], 0.12)
        self.assertEqual(unreviewed_cost_count(self.root, self.config, {"calls_without_final_cost": 1}), 0)

    def test_reviewed_failure_never_clears_another_unresolved_attempt(self):
        self.attempt(raw=self.idle_failure())
        self.attempt(batch="batch_00451", missing_raw=True)
        self.deferrals.return_value = [{"batch": "batch_00450"}]
        ledger = cost_accounting(self.root, self.config)
        self.assertEqual(ledger["calls_without_final_cost"], 2)
        self.assertEqual(ledger["reviewed_deferred_transport_calls_without_final_cost"], 1)
        self.assertEqual(ledger["unreviewed_calls_without_final_cost"], 1)
        self.assertEqual(ledger["unknown_cli_estimate_reserve_usd"], 0.24)
        self.assertEqual(unreviewed_cost_count(self.root, self.config, {"calls_without_final_cost": 2}), 1)

    def test_forged_cached_review_count_cannot_bypass_fresh_unknown_attempts(self):
        self.attempt(raw=self.idle_failure())
        status = {"calls_without_final_cost": 0, "reviewed_deferred_transport_calls_without_final_cost": 999,
                  "unreviewed_calls_without_final_cost": 0}
        before = copy.deepcopy(status)
        self.assertEqual(unreviewed_cost_count(self.root, self.config, status), 1)
        self.assertEqual(status, before)

    def test_legacy_cached_unknown_count_is_not_reduced_to_the_new_ledger_count(self):
        self.attempt(raw=self.idle_failure())
        self.deferrals.return_value = [{"batch": "batch_00450"}]
        self.assertEqual(unreviewed_cost_count(self.root, self.config, {"calls_without_final_cost": 4}), 3)

    def test_every_manifest_is_validated_and_validation_failure_is_fail_closed(self):
        self.attempt(raw={"total_cost_usd": 0.1})
        self.deferrals.side_effect = RuntimeError("Transport deferral artifact hash changed")
        with self.assertRaisesRegex(RuntimeError, "hash changed"):
            cost_accounting(self.root, self.config)
        with self.assertRaisesRegex(RuntimeError, "hash changed"):
            unreviewed_cost_count(self.root, self.config, {"calls_without_final_cost": 0})
        self.assertEqual(self.deferrals.call_count, 2)

    def test_real_reviewed_deferral_keeps_unknown_reserve_and_pin_tampering_fails_closed(self):
        from transport_defer import create_transport_defer

        self.deferrals_patch.stop()
        raw = self.idle_failure(subtype="success")
        request = self.attempt(raw=raw)
        self.save(request, {"request_sha256": "a" * 64, "data": {"records": [{"id": "HC02296"}]}})
        prefix = request.with_name(request.name.removesuffix(".request.json"))
        assistant = {"type": "assistant", "isApiErrorMessage": True,
                     "message": {"role": "assistant", "model": "<synthetic>",
                                 "content": [{"type": "text", "text": IDLE_TRANSPORT_ERROR}]}}
        prefix.with_suffix(".events.jsonl").write_text(json.dumps(assistant) + "\n" + json.dumps(raw) + "\n", encoding="utf-8")
        before = cost_accounting(self.root, self.config)
        self.assertEqual(before["calls_without_final_cost"], 1)
        self.assertEqual(before["unreviewed_calls_without_final_cost"], 1)
        create_transport_defer(self.root, "batch_00450")
        after = cost_accounting(self.root, self.config)
        self.assertEqual(after["calls_without_final_cost"], 1)
        self.assertEqual(after["reviewed_deferred_transport_calls_without_final_cost"], 1)
        self.assertEqual(after["unreviewed_calls_without_final_cost"], 0)
        self.assertEqual(after["unknown_cli_estimate_reserve_usd"], 0.12)
        self.assertEqual(unreviewed_cost_count(self.root, self.config, {"calls_without_final_cost": 1}), 0)
        raw_path = prefix.with_suffix(".raw.json")
        raw_path.write_bytes(raw_path.read_bytes() + b"\n")
        with self.assertRaises(RuntimeError):
            cost_accounting(self.root, self.config)
        with self.assertRaises(RuntimeError):
            unreviewed_cost_count(self.root, self.config, {"calls_without_final_cost": 1})

    def test_invalid_reported_costs_are_unknown_and_never_included_in_reported_sum(self):
        values = (None, True, False, -1, "0.01", float("nan"), float("inf"), -float("inf"))
        for index, value in enumerate(values):
            self.attempt(batch=f"batch_{index + 1:05d}", raw={"total_cost_usd": value})
        ledger = cost_accounting(self.root, self.config)
        self.assertEqual(ledger["incremental_cli_estimate_usd"], 0)
        self.assertEqual(ledger["calls_without_final_cost"], len(values))
        self.assertAlmostEqual(ledger["unknown_cli_estimate_reserve_usd"], len(values) * 0.12)

    def test_old_reported_cost_sum_is_compatible_even_without_usage_metadata(self):
        costs = [0, 0.1, 0.2, 2]
        for index, value in enumerate(costs):
            self.attempt(batch=f"batch_{index + 1:05d}", raw={"total_cost_usd": value})
        ledger = cost_accounting(self.root, self.config)
        self.assertEqual(ledger["incremental_cli_estimate_usd"], sum(costs))
        self.assertEqual(ledger["conservative_cli_estimate_reserved_usd"], sum(costs))
        self.assertEqual(ledger["calls_without_final_cost"], 0)
        self.assertEqual(ledger["uncertain_usage_attempts"], [])

    def test_missing_cost_and_idle_signature_count_only_once_and_preserve_reported_value(self):
        self.attempt(raw={key: value for key, value in self.idle_failure().items() if key != "total_cost_usd"})
        self.attempt(batch="batch_00451", raw=self.idle_failure(total_cost_usd=0.03))
        ledger = cost_accounting(self.root, self.config)
        self.assertEqual(ledger["calls_without_final_cost"], 2)
        self.assertEqual(ledger["incremental_cli_estimate_usd"], 0.03)
        self.assertAlmostEqual(ledger["conservative_cli_estimate_reserved_usd"], 0.27)

    def test_missing_usage_on_exact_idle_error_and_unreadable_raw_remain_unknown(self):
        raw = self.idle_failure()
        raw.pop("modelUsage")
        self.attempt(raw=raw)
        request = self.attempt(batch="batch_00451")
        request.with_name(request.name.removesuffix(".request.json") + ".raw.json").write_text("not JSON", encoding="utf-8")
        ledger = cost_accounting(self.root, self.config)
        self.assertEqual(ledger["calls_without_final_cost"], 2)
        self.assertEqual(ledger["incremental_cli_estimate_usd"], 0)
        self.assertEqual(ledger["unknown_cli_estimate_reserve_usd"], 0.24)

    def test_narrow_signature_does_not_reclassify_other_success_or_error_envelopes(self):
        cases = (
            {"is_error": False, "result": IDLE_TRANSPORT_ERROR, "modelUsage": {}, "total_cost_usd": 0},
            {"is_error": True, "result": IDLE_TRANSPORT_ERROR + ".", "modelUsage": {}, "total_cost_usd": 0},
            {"is_error": True, "result": "A different provider error", "modelUsage": {}, "total_cost_usd": 0},
            self.idle_failure(modelUsage={"claude-haiku-5-5": {"outputTokens": 100}}),
        )
        for index, raw in enumerate(cases):
            self.attempt(batch=f"batch_{index + 1:05d}", raw=raw)
        ledger = cost_accounting(self.root, self.config)
        self.assertEqual(ledger["calls_without_final_cost"], 0)

    def test_review_credit_is_limited_to_specific_base_provider_idle_attempt(self):
        self.attempt(raw=self.idle_failure(), directory="provider_completions_batch_00450")
        self.attempt(raw={"result": "Different failure"})
        self.deferrals.return_value = [{"batch": "batch_00450"}, {"batch": "batch_00450"}]
        ledger = cost_accounting(self.root, self.config)
        self.assertEqual(ledger["calls_without_final_cost"], 2)
        self.assertEqual(ledger["reviewed_deferred_transport_calls_without_final_cost"], 0)
        self.assertEqual(ledger["unreviewed_calls_without_final_cost"], 2)

    def test_invalid_cached_unknown_count_or_per_call_reserve_is_rejected(self):
        for value in (None, True, False, -1, "1", 1.0):
            with self.subTest(cached=value):
                with self.assertRaises(RuntimeError):
                    unreviewed_cost_count(self.root, self.config, {"calls_without_final_cost": value})
        with self.assertRaises(RuntimeError):
            unreviewed_cost_count(self.root, self.config, {})
        for value in (None, True, -1, "0.12", float("nan"), float("inf")):
            with self.subTest(reserve=value):
                with self.assertRaises(RuntimeError):
                    cost_accounting(self.root, {"max_call_budget_usd": value})


if __name__ == "__main__":
    unittest.main()
