"""Recover complete local-budget caches offline before guarded continuation."""
import copy
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))
import cache_recovery as recovery
import run_campaign as campaign
from budget_stream_recovery import LOCAL_GUARD_ERROR
from run_expansion import build_request_data, dump, file_sha, fingerprint, request_record, sha


class LocalBudgetCacheResumeTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.batch = "batch_00719"
        self.prefix = self.root / "provider" / self.batch
        self.prompt = "Preserve every source claim. Return exactly one record per id."
        prompt_path = self.root / "prompt.txt"
        prompt_path.write_text(self.prompt, encoding="utf-8")
        self.config = {
            "model": "claude-haiku-5-5", "max_output_tokens": 10000, "batch_size": 5,
            "prompt_file": str(prompt_path), "max_call_budget_usd": 0.12,
            "expected_org_name": "Harvard Edu for FAS/SEAS",
            "campaign": {"enabled": True, "quota_check_interval_seconds": 120},
            "stop_policy": {"stop_on_primary_quota_warning": True, "stop_on_quota_rejection": True,
                "stop_on_overage_use": True, "stop_on_billing_or_credits_prompt": True,
                "enable_extra_usage": False, "account_or_model_fallback": False,
                "internal_provider_retries": 0, "automatic_batch_retries": 0},
            "local_estimate_guard_policy": {"enabled": False, "included_quota_only": True,
                "extra_usage_must_be_disabled": True, "authorized_by_user": True},
        }
        self.sources = [
            {"review_id": f"HC{index}", "source_id": f"source-{index}",
             "question": f"What is sample {index}?", "original": f"Sample {index} contains café facts.  "}
            for index in range(3641, 3646)
        ]
        self.ids = [row["review_id"] for row in self.sources]
        self.records = [
            {"id": row["review_id"], "status": "ok", "confident": row["original"],
             "hesitant": row["original"].replace(" contains ", " may contain "), "reject_reason": None}
            for row in self.sources
        ]
        self.raw = {"type": "result", "subtype": "error_max_budget_usd", "is_error": True,
            "stop_reason": "end_turn", "errors": [LOCAL_GUARD_ERROR], "api_error_status": None,
            "modelUsage": {self.config["model"]: {"outputTokens": 7879}}, "total_cost_usd": 0.12744975}
        dump(self.root / "SOURCES.json", self.sources)
        dump(self.prefix.with_suffix(".request.json"), {
            "model": self.config["model"], "prompt": self.prompt, "prompt_sha256": sha(self.prompt),
            "request_sha256": fingerprint(self.config, self.prompt, self.sources),
            "data": build_request_data(self.prompt, [request_record(row) for row in self.sources]),
        })
        dump(self.prefix.with_suffix(".quota.json"), {"events": [], "quota_reporting": "unreported"})
        self.write_budget_stream()
        self.job = {"state": "finished", "pid": -1, "stop_reason": "per_call_estimate_safety_cap"}
        dump(self.root / "JOB.json", self.job)
        dump(self.root / "CAMPAIGN_JOB.json", self.job)
        self.prior_status = {"state": "per_call_estimate_safety_cap", "detail": {"batch": self.batch},
                             "calls_without_final_cost": 0}
        dump(self.root / "RUN_STATUS.json", self.prior_status)
        dump(self.root / "CAMPAIGN_STATUS.json", self.prior_status)
        dump(self.root / "CAMPAIGN_LAUNCH.json", {"pid": -1, "launched_at_utc": "synthetic launch"})
        self.offline_quota = self.patch("subscription_preflight.capture_subscription_preflight")
        self.submit = self.patch("cache_recovery.subprocess.run", side_effect=AssertionError("No subprocess or generation is permitted"))
        self.model = self.patch("run_expansion.provider_stream", side_effect=AssertionError("No model calls are permitted"))
        self.baseline = self.patch("run_campaign.preserve_baseline")
        self.pending = self.patch("run_campaign.pending_batches", return_value=["batch_00720"])
        self.evidence_path = self.root / "SUBSCRIPTION_PREFLIGHT" / "check_fixture.json"
        self.evidence = {
            "checked_at_utc": datetime.now(timezone.utc).isoformat(), "read_only": True,
            "account": {"loggedIn": True, "authMethod": "claude.ai", "apiProvider": "firstParty",
                        "subscriptionType": "enterprise", "orgName": self.config["expected_org_name"]},
            "usage": {"five_hour": {"utilization": 2, "locked_reason": None},
                      "extra_usage": {"is_enabled": False}},
        }
        dump(self.evidence_path, self.evidence)
        self.fresh_quota = self.patch("run_campaign.capture_subscription_preflight", return_value=self.evidence_path)

    def patch(self, target, **kwargs):
        patcher = mock.patch(target, **kwargs)
        self.addCleanup(patcher.stop)
        return patcher.start()

    def write_budget_stream(self):
        dump(self.prefix.with_suffix(".raw.json"), self.raw)
        events = [
            {"type": "system", "subtype": "init", "model": self.config["model"]},
            {"type": "assistant", "message": {"model": self.config["model"], "stop_reason": None,
                "content": [{"type": "text", "text": json.dumps({"records": self.records}, ensure_ascii=False)}]}},
            self.raw,
        ]
        self.prefix.with_suffix(".events.jsonl").write_text(
            "".join(json.dumps(event, ensure_ascii=False) + "\n" for event in events), encoding="utf-8")

    def recover(self, **kwargs):
        return recovery.complete_missing(self.root, self.batch, self.config,
                                         cache_only=True, allow_local_budget_stream=True, **kwargs)

    def recovered_resume(self):
        manifest_path = self.recover()
        dump(self.root / "RUN_STATUS.json", {"state": "cache_recovery_complete",
            "detail": {"batch": self.batch, "manifest": str(manifest_path.relative_to(self.root))},
            "calls_without_final_cost": 0})
        return manifest_path

    def assert_no_inference(self):
        self.submit.assert_not_called()
        self.model.assert_not_called()
        self.offline_quota.assert_not_called()

    def test_complete_cached_budget_output_recovers_without_any_subprocess_or_account_check(self):
        original = {path: path.read_bytes() for path in self.prefix.parent.glob("*")}
        manifest_path = self.recover()
        manifest = recovery.validate_completed_recovery(self.root, manifest_path, self.config)
        parsed = json.loads(self.prefix.with_suffix(".parsed.json").read_text())
        plan = json.loads((self.root / manifest["plan_file"]).read_text())
        for saved in (plan, manifest, parsed):
            self.assertEqual(saved["recovery_kind"], "completed_local_budget_stream")
            self.assertIs(saved["cache_only"], True)
            self.assertEqual(saved["local_budget_terminal_normalization"], plan["local_budget_terminal_normalization"])
            self.assertEqual(saved["cache_only_artifact_file_sha256"], plan["original_file_sha256"])
        self.assertEqual(plan["ids"], [])
        self.assertEqual(manifest["completed_missing_ids"], [])
        self.assertEqual(manifest["cached_ids"], self.ids)
        self.assertIs(parsed["recovered_from_cached_partial_output"], False)
        for source, actual in zip(self.records, parsed["records"]):
            for key, value in source.items():
                self.assertEqual(actual[key], value)
        for path, value in original.items():
            self.assertEqual(path.read_bytes(), value)
        self.assertIs(json.loads(self.prefix.with_suffix(".raw.json").read_text())["is_error"], True)
        self.assertFalse((self.root / "WORKER_LOCK.json").exists())
        self.fresh_quota.assert_not_called()
        self.assert_no_inference()

    def test_non_cache_only_budget_recovery_is_rejected_before_account_or_provider_work(self):
        with self.assertRaisesRegex(RuntimeError, "cache-only"):
            recovery.complete_missing(self.root, self.batch, self.config, allow_local_budget_stream=True)
        self.assertFalse(self.prefix.with_suffix(".parsed.json").exists())
        self.assertFalse((self.root / "CACHE_RECOVERIES").exists())
        self.assert_no_inference()

    def test_budget_metadata_and_original_artifact_pins_are_validated_for_every_reuse(self):
        manifest_path = self.recover()
        manifest = json.loads(manifest_path.read_text())
        parsed_path = self.prefix.with_suffix(".parsed.json")
        parsed = json.loads(parsed_path.read_text())
        for field, value in (("recovery_kind", "identical_duplicate_records"),
                             ("local_budget_terminal_normalization", {}), ("cache_only", False),
                             ("cache_only_artifact_file_sha256", {})):
            with self.subTest(field=field):
                changed = {**parsed, field: value}
                dump(parsed_path, changed)
                dump(manifest_path, {**manifest, "parsed_file_sha256": file_sha(parsed_path)})
                with self.assertRaises(RuntimeError):
                    recovery.validate_completed_recovery(self.root, manifest_path, self.config)
        dump(parsed_path, parsed)
        dump(manifest_path, manifest)
        raw_path = self.prefix.with_suffix(".raw.json")
        raw_path.write_bytes(raw_path.read_bytes() + b"\n")
        with self.assertRaises(RuntimeError):
            recovery.validate_completed_recovery(self.root, manifest_path, self.config)
        self.assert_no_inference()

    def test_idempotent_cache_recovery_preserves_every_saved_file(self):
        manifest_path = self.recover()
        before = {path: path.read_bytes() for path in self.root.rglob("*") if path.is_file()}
        self.assertEqual(self.recover(), manifest_path)
        self.assertEqual({path: path.read_bytes() for path in self.root.rglob("*") if path.is_file()}, before)
        self.assert_no_inference()

    def test_completed_budget_recovery_resume_requires_disabled_local_guards_and_fresh_quota(self):
        manifest_path = self.recovered_resume()
        before = {path: path.read_bytes() for path in self.root.rglob("*") if path.is_file()}
        name = campaign.prepare_cache_recovery_resume(self.root, self.config, manifest_path)
        history = json.loads((self.root / "CAMPAIGN_HISTORY" / name).read_text())
        self.assertEqual(history["manifest_file"], str(manifest_path.relative_to(self.root)))
        self.assertEqual(history["manifest_sha256"], file_sha(manifest_path))
        self.assertEqual(history["previous_campaign_job"], self.job)
        self.assertEqual(history["previous_tranche_job"], self.job)
        self.assertEqual(history["previous_campaign_status"], self.prior_status)
        self.assertEqual(history["subscription_preflight"], self.evidence)
        self.assertIs(history["extra_usage_activated"], False)
        self.assertIs(history["no_cached_text_regenerated"], True)
        self.fresh_quota.assert_called_once_with(self.config, self.root)
        self.baseline.assert_called_once_with(self.root, self.config)
        self.pending.assert_called_once_with(self.root, self.config)
        for path, value in before.items():
            self.assertEqual(path.read_bytes(), value)
        self.assert_no_inference()

    def test_enabled_or_unauthorized_guard_removal_cannot_resume_budget_stop(self):
        manifest_path = self.recovered_resume()
        configs = []
        legacy = copy.deepcopy(self.config)
        legacy.pop("local_estimate_guard_policy")
        configs.append(legacy)
        enabled = copy.deepcopy(self.config)
        enabled["local_estimate_guard_policy"]["enabled"] = True
        configs.append(enabled)
        unauthorized = copy.deepcopy(self.config)
        unauthorized["local_estimate_guard_policy"]["authorized_by_user"] = False
        configs.append(unauthorized)
        for config in configs:
            with self.subTest(policy=config.get("local_estimate_guard_policy")):
                with self.assertRaises(RuntimeError):
                    campaign.prepare_cache_recovery_resume(self.root, config, manifest_path)
        self.fresh_quota.assert_not_called()
        self.assertFalse((self.root / "CAMPAIGN_HISTORY").exists())
        self.assert_no_inference()

    def test_budget_resume_cannot_bypass_a_different_campaign_tranche_or_status_stop(self):
        manifest_path = self.recovered_resume()
        for filename, original, field in (("CAMPAIGN_JOB.json", self.job, "stop_reason"),
                                          ("JOB.json", self.job, "stop_reason"),
                                          ("CAMPAIGN_STATUS.json", self.prior_status, "state")):
            for phase in ("provider_policy_refusal", "account_quota_rejected", "billing_or_credits_required",
                          "invalid_provider_output_no_retry", "provider_error"):
                with self.subTest(filename=filename, phase=phase):
                    dump(self.root / filename, {**original, field: phase})
                    with self.assertRaises(RuntimeError):
                        campaign.prepare_cache_recovery_resume(self.root, self.config, manifest_path)
                    dump(self.root / filename, original)
        self.fresh_quota.assert_not_called()
        self.assertFalse((self.root / "CAMPAIGN_HISTORY").exists())
        self.assert_no_inference()

    def test_budget_resume_rejects_batch_mismatch_live_workers_or_unresolved_locks(self):
        manifest_path = self.recovered_resume()
        for filename in ("RUN_STATUS.json", "CAMPAIGN_STATUS.json"):
            original = json.loads((self.root / filename).read_text())
            dump(self.root / filename, {**original, "detail": {"batch": "batch_00720"}})
            with self.assertRaises(RuntimeError):
                campaign.prepare_cache_recovery_resume(self.root, self.config, manifest_path)
            dump(self.root / filename, original)
        dump(self.root / "JOB.json", {**self.job, "pid": os.getpid()})
        with self.assertRaises(RuntimeError):
            campaign.prepare_cache_recovery_resume(self.root, self.config, manifest_path)
        dump(self.root / "JOB.json", self.job)
        for filename in ("WORKER_LOCK.json", "CAMPAIGN_LOCK.json"):
            dump(self.root / filename, {"pid": -1})
            with self.assertRaises(RuntimeError):
                campaign.prepare_cache_recovery_resume(self.root, self.config, manifest_path)
            (self.root / filename).unlink()
        self.fresh_quota.assert_not_called()
        self.assert_no_inference()

    def test_fresh_quota_failure_leaves_budget_resume_stopped_without_history(self):
        manifest_path = self.recovered_resume()
        status = (self.root / "RUN_STATUS.json").read_bytes()
        self.fresh_quota.side_effect = RuntimeError("Included quota is locked or extra usage is enabled")
        with self.assertRaises(RuntimeError):
            campaign.prepare_cache_recovery_resume(self.root, self.config, manifest_path)
        self.assertEqual((self.root / "RUN_STATUS.json").read_bytes(), status)
        self.assertFalse((self.root / "CAMPAIGN_HISTORY").exists())
        self.assert_no_inference()

    def test_a_different_missing_cost_attempt_blocks_resume_despite_disabled_estimate_guards(self):
        manifest_path = self.recovered_resume()
        dump(self.root / "provider_other" / "batch_00001.request.json", {"request_sha256": "b" * 64})
        with self.assertRaises(RuntimeError):
            campaign.prepare_cache_recovery_resume(self.root, self.config, manifest_path)
        self.fresh_quota.assert_not_called()
        self.assertFalse((self.root / "CAMPAIGN_HISTORY").exists())
        self.assert_no_inference()

    def test_budget_terminal_without_reported_cost_cannot_be_recovered_offline(self):
        self.raw.pop("total_cost_usd")
        self.write_budget_stream()
        with self.assertRaises(RuntimeError):
            self.recover()
        self.assertFalse(self.prefix.with_suffix(".parsed.json").exists())
        self.assert_no_inference()


if __name__ == "__main__":
    unittest.main()
