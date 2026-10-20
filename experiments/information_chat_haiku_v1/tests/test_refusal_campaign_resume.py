"""Explicit refusal exclusion preserves evidence and never retries refused sources."""
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
import run_campaign as campaign
from launch_expansion import pending_batches as real_pending_batches
from run_expansion import create_refusal_quarantine, dump, file_sha, fingerprint, request_record, sha


class RefusalCampaignResumeTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.batch = "batch_00313"
        self.prefix = self.root / "provider" / self.batch
        self.quarantine = self.root / "QUARANTINED_BATCHES" / f"{self.batch}.json"
        self.prompt = "Create paired confident and hesitant rewrites without changing source claims."
        prompt_path = self.root / "prompt.txt"
        prompt_path.write_text(self.prompt, encoding="utf-8")
        self.config = {
            "model": "claude-haiku-5-5", "batch_size": 5, "max_output_tokens": 10000,
            "target_sources": 10000, "max_call_budget_usd": 0.12,
            "max_incremental_cli_estimate_usd": 5, "prompt_file": str(prompt_path),
            "expected_org_name": "Harvard Edu for FAS/SEAS",
        }
        self.sources = [
            {"review_id": f"HC{index:05d}", "source_id": f"source-{index}",
             "question": f"What is sample {index}?", "original": f"Sample {index} is synthetic."}
            for index in range(1561, 1566)
        ]
        self.ids = [row["review_id"] for row in self.sources]
        self.request = {
            "request_sha256": fingerprint(self.config, self.prompt, self.sources),
            "model": self.config["model"], "prompt": self.prompt, "prompt_sha256": sha(self.prompt),
            "data": {"records": [request_record(row) for row in self.sources]},
        }
        self.raw = {"type": "result", "subtype": "success", "is_error": True,
                    "stop_reason": "refusal", "result": "Synthetic provider policy refusal.",
                    "total_cost_usd": 0.006, "modelUsage": {self.config["model"]: {"outputTokens": 0}}}
        dump(self.root / "SOURCES.json", self.sources)
        dump(self.prefix.with_suffix(".request.json"), self.request)
        dump(self.prefix.with_suffix(".raw.json"), self.raw)
        self.prefix.with_suffix(".events.jsonl").write_text(json.dumps(self.raw) + "\n", encoding="utf-8")
        self.prefix.with_suffix(".stderr.txt").write_text("Synthetic stderr evidence.\n", encoding="utf-8")
        dump(self.prefix.with_suffix(".quota.json"), {"events": []})
        old_prefix = self.root / "provider" / "batch_00312"
        dump(old_prefix.with_suffix(".request.json"), {"request_sha256": "a" * 64})
        dump(old_prefix.with_suffix(".raw.json"), {"type": "result", "is_error": False,
                                                  "total_cost_usd": 0.01})
        dump(old_prefix.with_suffix(".parsed.json"), {
            "request_sha256": "a" * 64, "records": [{"id": "HC01560", "status": "ok",
                "confident": "Existing direct text.", "hesitant": "Existing tentative text."}],
        })
        self.job = {"pid": -1, "state": "finished", "stop_reason": "provider_policy_refusal"}
        self.status = {"state": "provider_policy_refusal", "detail": {"batch": self.batch},
                       "calls_without_final_cost": 0, "total_generated_triplets": 1560}
        self.campaign_status = {**self.status, "campaign_state": "stopped", "campaign_detail": "provider_policy_refusal"}
        self.launch = {"pid": -1, "launched_at_utc": "synthetic previous launch"}
        self.restore_status()
        self.evidence = {
            "checked_at_utc": datetime.now(timezone.utc).isoformat(), "read_only": True,
            "account": {"loggedIn": True, "authMethod": "claude.ai", "apiProvider": "firstParty",
                        "subscriptionType": "enterprise", "orgName": self.config["expected_org_name"]},
            "usage": {"five_hour": {"utilization": 2, "locked_reason": None},
                      "extra_usage": {"is_enabled": False}},
        }
        self.evidence_path = self.root / "SUBSCRIPTION_PREFLIGHT" / "check_fixture.json"
        dump(self.evidence_path, self.evidence)
        self.baseline = self.patch("run_campaign.preserve_baseline")
        self.pending = self.patch("run_campaign.pending_batches", return_value=["batch_00314"])
        self.preflight = self.patch("run_campaign.capture_subscription_preflight", return_value=self.evidence_path)
        self.provider = self.patch("run_expansion.provider_stream", side_effect=AssertionError("No provider calls in resume tests"))
        self.worker = self.patch("run_campaign.worker", side_effect=AssertionError("Resume preparation must not start a worker"))

        def save_state(root, config, phase, detail=None):
            value = {**json.loads((root / "RUN_STATUS.json").read_text()), "state": phase, "detail": detail}
            dump(root / "RUN_STATUS.json", value)
            return value

        self.state = self.patch("run_campaign.state", side_effect=save_state)

    def patch(self, target, **kwargs):
        patcher = mock.patch(target, **kwargs)
        self.addCleanup(patcher.stop)
        return patcher.start()

    def restore_status(self):
        dump(self.root / "CAMPAIGN_JOB.json", self.job)
        dump(self.root / "JOB.json", self.job)
        dump(self.root / "RUN_STATUS.json", self.status)
        dump(self.root / "CAMPAIGN_STATUS.json", self.campaign_status)
        dump(self.root / "CAMPAIGN_LAUNCH.json", self.launch)

    def resume(self, batch=None):
        return campaign.prepare_refusal_resume(self.root, self.config, self.batch if batch is None else batch)

    def provider_bytes(self):
        return {path: path.read_bytes() for path in self.root.glob("provider*/*") if path.is_file()}

    def assert_no_resume(self):
        self.assertFalse(any((self.root / "CAMPAIGN_HISTORY").glob("*.json")))
        self.state.assert_not_called()
        self.provider.assert_not_called()
        self.worker.assert_not_called()

    def test_reviewed_refusal_is_excluded_and_archived_without_rewriting_existing_output(self):
        before = self.provider_bytes()
        previous_jobs = {name: (self.root / name).read_bytes() for name in ("CAMPAIGN_JOB.json", "JOB.json", "CAMPAIGN_LAUNCH.json", "CAMPAIGN_STATUS.json")}
        history_name = self.resume()
        history = json.loads((self.root / "CAMPAIGN_HISTORY" / history_name).read_text())
        entry = json.loads(self.quarantine.read_text())
        self.assertEqual(entry["source_ids"], self.ids)
        self.assertEqual(entry["decision"], "exclude_without_retry")
        self.assertEqual(entry["request_sha256"], self.request["request_sha256"])
        self.assertEqual(entry["request_file_sha256"], file_sha(self.prefix.with_suffix(".request.json")))
        self.assertEqual(entry["raw_file_sha256"], file_sha(self.prefix.with_suffix(".raw.json")))
        self.assertEqual(history["quarantine_file"], str(self.quarantine.relative_to(self.root)))
        self.assertEqual(history["quarantine_sha256"], file_sha(self.quarantine))
        self.assertEqual(history["previous_jobs"], {"CAMPAIGN_JOB.json": self.job, "JOB.json": self.job})
        self.assertEqual(history["previous_campaign_status"], self.campaign_status)
        self.assertEqual(history["previous_launch"], self.launch)
        self.assertEqual(history["previous_status"], self.status)
        self.assertEqual(history["quarantine"], entry)
        self.assertEqual(history["sources_sha256"], file_sha(self.root / "SOURCES.json"))
        self.assertEqual(history["preflight_file"], str(self.evidence_path.relative_to(self.root)))
        self.assertEqual(history["preflight_sha256"], file_sha(self.evidence_path))
        self.assertEqual(history["subscription_preflight"], self.evidence)
        self.assertEqual(history["pending_batches"], ["batch_00314"])
        self.assertIs(history["extra_usage_activated"], False)
        self.assertIs(history["no_cached_text_regenerated"], True)
        self.assertIs(history["no_refused_content_resubmitted"], True)
        self.assertIs(history["no_rephrase_split_model_or_account_fallback"], True)
        expected_pins = {str(path.relative_to(self.root)): file_sha(path) for path in before}
        self.assertEqual(history["preserved_provider_file_sha256"], expected_pins)
        self.baseline.assert_called_once_with(self.root, self.config)
        self.pending.assert_called_once_with(self.root, self.config)
        self.preflight.assert_called_once_with(self.config, self.root)
        self.assertEqual(self.provider_bytes(), before)
        for path, expected in previous_jobs.items():
            self.assertEqual((self.root / path).read_bytes(), expected)
        final = json.loads((self.root / "RUN_STATUS.json").read_text())
        self.assertEqual(final["state"], "reviewed_refusal_excluded")
        self.assertEqual(final["detail"]["batch"], self.batch)
        self.assertEqual(final["detail"]["quarantine"], str(self.quarantine.relative_to(self.root)))
        self.assertIn("reviewed_refusal_excluded", campaign.CONTINUABLE)
        self.assertFalse(self.prefix.with_suffix(".parsed.json").exists())
        self.provider.assert_not_called()
        self.worker.assert_not_called()

    def test_wrong_or_malformed_batch_cannot_resume(self):
        for batch in ("batch_00312", "batch_313", "../batch_00313", "batch_00313.raw.json", ""):
            with self.subTest(batch=batch):
                with self.assertRaises((RuntimeError, ValueError)):
                    self.resume(batch)
                self.assert_no_resume()
        self.preflight.assert_not_called()

    def test_every_job_and_status_must_match_the_exact_refusal_stop(self):
        for filename, key in (("CAMPAIGN_JOB.json", "stop_reason"), ("JOB.json", "stop_reason"),
                              ("RUN_STATUS.json", "state"), ("CAMPAIGN_STATUS.json", "state")):
            for phase in ("account_quota_rejected", "billing_or_credits_required", "invalid_provider_output_no_retry", "provider_error"):
                with self.subTest(filename=filename, phase=phase):
                    self.restore_status()
                    value = json.loads((self.root / filename).read_text())
                    value[key] = phase
                    dump(self.root / filename, value)
                    with self.assertRaises(RuntimeError):
                        self.resume()
                    self.assert_no_resume()
        self.preflight.assert_not_called()

    def test_status_batch_details_must_match_the_reviewed_refusal(self):
        for filename in ("RUN_STATUS.json", "CAMPAIGN_STATUS.json"):
            for detail in ({"batch": "batch_00312"}, {}, None, "batch_00313"):
                with self.subTest(filename=filename, detail=detail):
                    self.restore_status()
                    value = json.loads((self.root / filename).read_text())
                    value["detail"] = detail
                    dump(self.root / filename, value)
                    with self.assertRaises(RuntimeError):
                        self.resume()
                    self.assert_no_resume()

    def test_live_or_unfinished_jobs_and_unresolved_locks_block_resume(self):
        for filename in ("CAMPAIGN_JOB.json", "JOB.json"):
            for change in ({"state": "running"}, {"state": "failed"}, {"pid": os.getpid()}):
                with self.subTest(filename=filename, change=change):
                    self.restore_status()
                    dump(self.root / filename, {**self.job, **change})
                    with self.assertRaises(RuntimeError):
                        self.resume()
                    self.assert_no_resume()
        for filename in ("CAMPAIGN_LOCK.json", "WORKER_LOCK.json"):
            with self.subTest(lock=filename):
                self.restore_status()
                dump(self.root / filename, {"pid": -1})
                try:
                    with self.assertRaises(RuntimeError):
                        self.resume()
                    self.assert_no_resume()
                finally:
                    (self.root / filename).unlink()
        self.preflight.assert_not_called()

    def test_unknown_or_unresolved_provider_cost_blocks_resume(self):
        for unresolved in (None, 1):
            with self.subTest(unresolved=unresolved):
                dump(self.root / "RUN_STATUS.json", {**self.status, "calls_without_final_cost": unresolved})
                with self.assertRaises(RuntimeError):
                    self.resume()
                self.assert_no_resume()
        self.preflight.assert_not_called()

    def test_non_refusal_provider_evidence_or_existing_parsed_output_cannot_be_excluded(self):
        for change in ({"is_error": False}, {"stop_reason": "end_turn"}, {"stop_reason": "max_tokens"},
                       {"stop_reason": None}, {"stop_reason": "quota"}):
            with self.subTest(change=change):
                dump(self.prefix.with_suffix(".raw.json"), {**self.raw, **change})
                with self.assertRaises(RuntimeError):
                    self.resume()
                self.assert_no_resume()
        dump(self.prefix.with_suffix(".raw.json"), self.raw)
        dump(self.prefix.with_suffix(".parsed.json"), {"records": []})
        with self.assertRaises(RuntimeError):
            self.resume()
        self.assert_no_resume()

    def test_changed_existing_quarantine_hashes_or_source_ids_are_rejected(self):
        original = create_refusal_quarantine(self.root, self.batch)
        for field, value in (("request_sha256", "b" * 64), ("request_file_sha256", "c" * 64),
                             ("raw_file_sha256", "d" * 64), ("source_ids", list(reversed(self.ids))),
                             ("decision", "retry")):
            with self.subTest(field=field):
                dump(self.quarantine, {**original, field: value})
                with self.assertRaises(RuntimeError):
                    self.resume()
                self.assert_no_resume()
        dump(self.quarantine, original)
        request = copy.deepcopy(self.request)
        request["data"]["records"][0]["id"] = "unknown"
        dump(self.prefix.with_suffix(".request.json"), request)
        with self.assertRaises(RuntimeError):
            self.resume()
        self.assert_no_resume()

    def test_duplicate_request_ids_or_missing_original_evidence_are_rejected(self):
        request = copy.deepcopy(self.request)
        request["data"]["records"][1]["id"] = request["data"]["records"][0]["id"]
        dump(self.prefix.with_suffix(".request.json"), request)
        with self.assertRaises(RuntimeError):
            self.resume()
        self.assert_no_resume()
        dump(self.prefix.with_suffix(".request.json"), self.request)
        self.prefix.with_suffix(".raw.json").unlink()
        with self.assertRaises(RuntimeError):
            self.resume()
        self.assert_no_resume()

    def test_preflight_baseline_or_pending_integrity_failure_never_authorizes_resume(self):
        for dependency in (self.baseline, self.pending, self.preflight):
            with self.subTest(dependency=dependency):
                self.restore_status()
                dependency.side_effect = RuntimeError("Synthetic verification failure")
                try:
                    with self.assertRaises(RuntimeError):
                        self.resume()
                    self.assert_no_resume()
                    self.assertEqual(json.loads((self.root / "RUN_STATUS.json").read_text()), self.status)
                finally:
                    dependency.side_effect = None

    def test_real_pending_validation_rejects_request_ids_inconsistent_with_frozen_source_order(self):
        earlier = [
            {"review_id": f"HC{index:05d}", "source_id": f"source-{index}",
             "question": f"What is sample {index}?", "original": f"Sample {index} is synthetic."}
            for index in range(1, 1561)
        ]
        dump(self.root / "SOURCES.json", [*earlier, *self.sources])
        # The unrelated cached fixture is removed only within this temporary test root.
        for suffix in (".request.json", ".parsed.json"):
            (self.root / "provider" / "batch_00312").with_suffix(suffix).unlink()
        changed = copy.deepcopy(self.request)
        changed["data"]["records"][0]["id"] = earlier[0]["review_id"]
        dump(self.prefix.with_suffix(".request.json"), changed)
        self.pending.side_effect = real_pending_batches
        with self.assertRaises(RuntimeError):
            self.resume()
        self.assert_no_resume()
        self.preflight.assert_not_called()


if __name__ == "__main__":
    unittest.main()
