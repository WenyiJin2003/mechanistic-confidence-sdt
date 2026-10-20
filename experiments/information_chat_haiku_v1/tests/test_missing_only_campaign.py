"""Campaign recovery is limited to validated, successful partial batches."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))
import cache_recovery as recovery
import run_campaign as campaign
from run_expansion import dump, fingerprint, request_record, sha


class MissingOnlyCampaignTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.batch = "batch_00167"
        self.prefix = self.root / "provider" / self.batch
        self.prompt = "Create confident and hesitant versions of each supplied response."
        prompt_path = self.root / "prompt.txt"
        prompt_path.write_text(self.prompt, encoding="utf-8")
        self.config = {
            "model": "claude-haiku-5-5",
            "max_output_tokens": 10000,
            "max_call_budget_usd": 0.12,
            "batch_size": 5,
            "target_sources": 10000,
            "prompt_file": str(prompt_path),
            "campaign": {"missing_id_completion": {
                "enabled": True, "max_additional_calls_per_batch": 1,
            }},
        }
        self.sources = [
            {"review_id": f"HC{index}", "source_id": f"source-{index}",
             "question": f"What is sample {index}?",
             "original": f"Sample {index} is a synthetic source."}
            for index in range(881, 886)
        ]
        self.records = [
            {"id": row["review_id"], "status": "ok", "confident": row["original"],
             "hesitant": row["original"].replace(" is ", " may be "), "reject_reason": None}
            for row in self.sources
        ]
        self.raw = {
            "type": "result", "subtype": "success", "is_error": False,
            "stop_reason": "end_turn", "result": json.dumps({"records": self.records[:1]}),
            "modelUsage": {self.config["model"]: {"outputTokens": 100}},
            "total_cost_usd": 0.01,
        }
        dump(self.root / "SOURCES.json", self.sources)
        dump(self.prefix.with_suffix(".request.json"), {
            "request_sha256": fingerprint(self.config, self.prompt, self.sources),
            "model": self.config["model"], "prompt": self.prompt,
            "prompt_sha256": sha(self.prompt),
            "data": {"records": [request_record(row) for row in self.sources]},
        })
        self.write_raw(self.raw)
        self.write_status()
        self.manifest = self.root / "CACHE_RECOVERIES" / f"{self.batch}.completed.json"
        self.state_calls = []

        def save_state(root, config, phase, detail=None):
            self.state_calls.append((phase, detail))
            value = {"state": phase, "detail": detail}
            dump(root / "RUN_STATUS.json", value)
            return value

        state_patch = mock.patch.object(campaign, "state", side_effect=save_state)
        state_patch.start()
        self.addCleanup(state_patch.stop)
        provider_patch = mock.patch("run_expansion.provider_stream", side_effect=AssertionError("No provider calls in tests"))
        self.provider = provider_patch.start()
        self.addCleanup(provider_patch.stop)

    def write_status(self, phase="invalid_provider_output_no_retry", detail=None):
        dump(self.root / "RUN_STATUS.json", {
            "state": phase, "detail": {"batch": self.batch} if detail is None else detail,
            "calls_without_final_cost": 0,
        })

    def write_raw(self, value):
        dump(self.prefix.with_suffix(".raw.json"), value)
        self.prefix.with_suffix(".events.jsonl").write_text(json.dumps(value) + "\n", encoding="utf-8")

    def complete_patch(self, **kwargs):
        return mock.patch.object(recovery, "complete_missing", create=True,
                                 return_value=self.manifest, **kwargs)

    def test_successful_partial_batch_completes_once_with_campaign_ownership(self):
        before = {path: path.read_bytes() for path in self.prefix.parent.glob("*")}
        with self.complete_patch() as complete:
            self.assertTrue(campaign.maybe_complete_partial(self.root, self.config))
        complete.assert_called_once_with(self.root, self.batch, self.config, campaign_owned=True)
        self.assertEqual(self.state_calls[-1][0], "cache_recovery_complete")
        self.assertEqual(self.state_calls[-1][1]["batch"], self.batch)
        self.assertEqual(self.state_calls[-1][1]["manifest"], str(self.manifest.relative_to(self.root)))
        self.assertEqual({path: path.read_bytes() for path in self.prefix.parent.glob("*")}, before)
        self.provider.assert_not_called()

    def test_unrelated_stop_reasons_never_inspect_or_complete(self):
        for phase in ("provider_policy_refusal", "account_quota_rejected", "account_quota_or_rate_limit",
                      "billing_or_credits_required", "provider_timeout_no_retry", "provider_error",
                      "overage_use_reported", "target_generated"):
            with self.subTest(phase=phase):
                self.write_status(phase)
                with mock.patch.object(recovery, "inspect_cached_batch") as inspect, self.complete_patch() as complete:
                    self.assertFalse(campaign.maybe_complete_partial(self.root, self.config))
                inspect.assert_not_called()
                complete.assert_not_called()
        self.assertEqual(self.state_calls, [])

    def test_missing_or_nonboolean_enablement_never_inspects_or_completes(self):
        for setting in (None, {}, {"enabled": False}, {"enabled": 1}, {"enabled": "true"}):
            with self.subTest(setting=setting):
                config = copy.deepcopy(self.config)
                if setting is None:
                    config.pop("campaign")
                else:
                    config["campaign"]["missing_id_completion"] = setting
                with mock.patch.object(recovery, "inspect_cached_batch") as inspect, self.complete_patch() as complete:
                    self.assertFalse(campaign.maybe_complete_partial(self.root, config))
                inspect.assert_not_called()
                complete.assert_not_called()

    def test_invalid_batch_detail_never_completes(self):
        for detail in ({}, {"batch": "../batch_00167"}, {"batch": "batch_167"}, {"batch": None}):
            with self.subTest(detail=detail):
                self.write_status(detail=detail)
                with self.complete_patch() as complete:
                    self.assertFalse(campaign.maybe_complete_partial(self.root, self.config))
                complete.assert_not_called()

    def test_additional_call_limit_must_be_exactly_one(self):
        for limit in (None, 0, 2, -1, True, "1"):
            with self.subTest(limit=limit):
                self.write_status()
                config = copy.deepcopy(self.config)
                setting = config["campaign"]["missing_id_completion"]
                if limit is None:
                    setting.pop("max_additional_calls_per_batch")
                else:
                    setting["max_additional_calls_per_batch"] = limit
                with self.complete_patch() as complete:
                    self.assertFalse(campaign.maybe_complete_partial(self.root, config))
                complete.assert_not_called()

    def test_unresolved_call_cost_never_inspects_or_completes(self):
        for unresolved in (1, None):
            with self.subTest(unresolved=unresolved):
                dump(self.root / "RUN_STATUS.json", {
                    "state": "invalid_provider_output_no_retry", "detail": {"batch": self.batch},
                    "calls_without_final_cost": unresolved,
                })
                with mock.patch.object(recovery, "inspect_cached_batch") as inspect, self.complete_patch() as complete:
                    self.assertFalse(campaign.maybe_complete_partial(self.root, self.config))
                inspect.assert_not_called()
                complete.assert_not_called()

    def test_empty_or_complete_output_is_never_submitted(self):
        for records in ([], self.records):
            with self.subTest(records=len(records)):
                self.write_status()
                self.write_raw({**self.raw, "result": json.dumps({"records": records})})
                with self.complete_patch() as complete:
                    self.assertFalse(campaign.maybe_complete_partial(self.root, self.config))
                complete.assert_not_called()

    def test_refusal_quota_billing_timeout_and_invalid_partial_cache_are_never_submitted(self):
        invalid = (
            {"is_error": True, "stop_reason": "refusal"},
            {"is_error": True, "result": "Quota limit reached"},
            {"is_error": True, "result": "Billing credits required"},
            {"stop_reason": "max_tokens"},
            {"subtype": "error_during_execution"},
            {"result": "not JSON"},
            {"result": json.dumps({"records": self.records[:1] * 2})},
            {"result": json.dumps({"records": [{**self.records[0], "id": "unknown"}]})},
            {"result": json.dumps({"records": [{**self.records[0], "status": "unknown"}]})},
            {"result": json.dumps({"records": [{**self.records[0], "confident": ""}]})},
        )
        for change in invalid:
            with self.subTest(change=change):
                self.write_status()
                self.write_raw({**self.raw, **change})
                with self.complete_patch() as complete:
                    self.assertFalse(campaign.maybe_complete_partial(self.root, self.config))
                complete.assert_not_called()
        self.provider.assert_not_called()

    def test_completion_runtime_error_marks_attention_when_status_is_unchanged(self):
        with self.complete_patch(side_effect=RuntimeError("Completion needs review")) as complete:
            self.assertFalse(campaign.maybe_complete_partial(self.root, self.config))
        complete.assert_called_once()
        self.assertEqual(json.loads((self.root / "RUN_STATUS.json").read_text())["state"],
                         "missing_id_completion_requires_attention")

    def test_saved_completion_attempt_without_parsed_output_never_resubmits(self):
        plan_path = recovery.prepare_recovery(self.root, self.batch, self.config)
        plan = json.loads(plan_path.read_text())
        prefix = self.root / plan["provider_dir"] / "batch_00001"
        prefix.parent.mkdir()
        for suffix in (".request.json", ".raw.json", ".events.jsonl", ".stderr.txt", ".quota.json"):
            with self.subTest(suffix=suffix):
                self.write_status()
                artifact = prefix.with_suffix(suffix)
                artifact.write_text("saved attempt evidence\n", encoding="utf-8")
                try:
                    with mock.patch.object(recovery, "_check_recovery_owner"), \
                         mock.patch("subscription_preflight.capture_subscription_preflight") as preflight, \
                         mock.patch.object(recovery.subprocess, "run") as submit:
                        self.assertFalse(campaign.maybe_complete_partial(self.root, self.config))
                    preflight.assert_not_called()
                    submit.assert_not_called()
                    self.assertEqual(artifact.read_text(), "saved attempt evidence\n")
                    self.assertFalse((self.root / "WORKER_LOCK.json").exists())
                finally:
                    artifact.unlink()

    def test_completion_runtime_error_preserves_specific_provider_failure(self):
        for phase in ("account_quota_rejected", "billing_or_credits_required", "provider_policy_refusal",
                      "provider_timeout_no_retry", "provider_error"):
            with self.subTest(phase=phase):
                self.write_status()
                self.state_calls.clear()

                def fail(*args, **kwargs):
                    self.write_status(phase, {"batch": self.batch, "error": "specific provider stop"})
                    raise RuntimeError("Completion stopped")

                with self.complete_patch(side_effect=fail):
                    self.assertFalse(campaign.maybe_complete_partial(self.root, self.config))
                saved = json.loads((self.root / "RUN_STATUS.json").read_text())
                self.assertEqual(saved["state"], phase)
                self.assertEqual(saved["detail"]["error"], "specific provider stop")
                self.assertEqual(self.state_calls, [])


if __name__ == "__main__":
    unittest.main()
