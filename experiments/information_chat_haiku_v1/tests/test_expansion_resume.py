import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))
from run_expansion import (
    create_refusal_quarantine,
    dump,
    state,
    stop_signal,
    validate_refusal_quarantine,
)
from launch_expansion import prepare_resume


def file_sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ExpansionResumeTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.prefix = self.root / "provider" / "batch_00027"
        self.request_path = self.prefix.with_suffix(".request.json")
        self.raw_path = self.prefix.with_suffix(".raw.json")
        self.parsed_path = self.prefix.with_suffix(".parsed.json")
        self.request_hash = "a" * 64
        self.ids = [f"HC{number}" for number in range(181, 186)]
        self.request = {
            "request_sha256": self.request_hash,
            "model": "claude-haiku-5-5",
            "data": {
                "records": [
                    {
                        "id": source_id,
                        "question": "What is this ordinary source about?",
                        "original_response": "This is a synthetic unit-test source.",
                    }
                    for source_id in self.ids
                ]
            },
        }
        self.refusal = {
            "type": "result",
            "subtype": "success",
            "is_error": True,
            "stop_reason": "refusal",
            "result": "Provider usage-policy refusal.",
            "total_cost_usd": 0.0097461,
        }
        dump(self.request_path, self.request)
        dump(self.raw_path, self.refusal)

    def quarantine(self):
        return create_refusal_quarantine(self.root, self.prefix.name)

    def validate(self, entry):
        return validate_refusal_quarantine(
            self.prefix,
            entry,
            request_hash=self.request_hash,
            source_ids=self.ids,
        )

    def prepare_resume_files(self, reason="provider_error", cap=5):
        dump(
            self.root / "JOB.json",
            {"pid": -1, "state": "finished", "stop_reason": reason},
        )
        dump(
            self.root / "RUN_STATUS.json",
            {
                "state": reason,
                "detail": {"batch": "batch_00027"},
                "incremental_cli_estimate_safety_cap_usd": cap,
            },
        )
        dump(self.root / "LAUNCH.json", {"pid": -1, "launched_at_utc": "fixture"})
        dump(self.root / "SOURCES.json", [{"review_id": source_id} for source_id in self.ids])
        return {"max_incremental_cli_estimate_usd": cap}

    def test_quarantine_preserves_saved_evidence_and_binds_exact_request(self):
        request_bytes = self.request_path.read_bytes()
        raw_bytes = self.raw_path.read_bytes()
        entry = self.quarantine()

        manifest = self.root / "QUARANTINED_BATCHES" / "batch_00027.json"
        self.assertEqual(json.loads(manifest.read_text()), entry)
        self.assertEqual(entry["batch"], "batch_00027")
        self.assertEqual(entry["request_sha256"], self.request_hash)
        self.assertEqual(entry["request_file_sha256"], file_sha256(self.request_path))
        self.assertEqual(entry["raw_file_sha256"], file_sha256(self.raw_path))
        self.assertEqual(entry["source_ids"], self.ids)
        validated = self.validate(entry)
        self.assertIsInstance(validated, dict)
        self.assertEqual(validated["source_ids"], self.ids)
        self.assertEqual(self.request_path.read_bytes(), request_bytes)
        self.assertEqual(self.raw_path.read_bytes(), raw_bytes)
        self.assertFalse(self.parsed_path.exists())

    def test_validation_rejects_altered_manifest_hashes_and_ids(self):
        entry = self.quarantine()
        for field, value in (
            ("batch", "batch_00028"),
            ("request_sha256", "b" * 64),
            ("request_file_sha256", "c" * 64),
            ("raw_file_sha256", "d" * 64),
            ("source_ids", [*self.ids[:-1], "HC186"]),
            ("source_ids", list(reversed(self.ids))),
        ):
            with self.subTest(field=field, value=value):
                with self.assertRaises(RuntimeError):
                    self.validate({**entry, field: value})

    def test_validation_rejects_current_batch_fingerprint_or_id_changes(self):
        entry = self.quarantine()
        with self.assertRaises(RuntimeError):
            validate_refusal_quarantine(
                self.prefix, entry, request_hash="b" * 64, source_ids=self.ids
            )
        with self.assertRaises(RuntimeError):
            validate_refusal_quarantine(
                self.prefix,
                entry,
                request_hash=self.request_hash,
                source_ids=[*self.ids[:-1], "HC186"],
            )

    def test_validation_rejects_changed_saved_request_bytes(self):
        entry = self.quarantine()
        changed = json.loads(self.request_path.read_text())
        changed["data"]["records"][0]["original_response"] = "Changed source."
        dump(self.request_path, changed)
        with self.assertRaises(RuntimeError):
            self.validate(entry)

    def test_validation_rejects_changed_saved_raw_bytes(self):
        entry = self.quarantine()
        dump(self.raw_path, {**self.refusal, "result": "Changed refusal text."})
        with self.assertRaises(RuntimeError):
            self.validate(entry)

    def test_only_actual_provider_refusal_can_be_quarantined(self):
        for changed in (
            {"is_error": False},
            {"stop_reason": "end_turn"},
            {"stop_reason": None},
        ):
            with self.subTest(changed=changed):
                dump(self.raw_path, {**self.refusal, **changed})
                with self.assertRaises(RuntimeError):
                    self.quarantine()

    def test_success_subtype_policy_refusal_is_distinct_from_quota_rejection(self):
        self.assertEqual(stop_signal(self.refusal), "provider_policy_refusal")
        self.assertEqual(
            stop_signal({"type": "rate_limit_event", "rate_limit_info": {"status": "rejected"}}),
            "account_quota_rejected",
        )

    def test_validation_rechecks_refusal_even_with_matching_file_hash(self):
        entry = self.quarantine()
        dump(self.raw_path, {**self.refusal, "stop_reason": "end_turn"})
        changed_entry = {**entry, "raw_file_sha256": file_sha256(self.raw_path)}
        with self.assertRaises(RuntimeError):
            self.validate(changed_entry)

    def test_creation_and_validation_reject_refused_batch_with_parsed_output(self):
        entry = self.quarantine()
        dump(self.parsed_path, {"request_sha256": self.request_hash, "records": []})
        with self.assertRaises(RuntimeError):
            self.validate(entry)
        with self.assertRaises(RuntimeError):
            self.quarantine()

    def test_creation_requires_both_original_evidence_files(self):
        for missing in (self.request_path, self.raw_path):
            with self.subTest(missing=missing.name):
                saved_bytes = missing.read_bytes()
                missing.unlink()
                try:
                    with self.assertRaises(RuntimeError):
                        self.quarantine()
                finally:
                    # Restore only this temporary fixture for the next subtest.
                    dump(missing, json.loads(saved_bytes))

    def test_state_counts_quarantine_separately_and_keeps_refusal_cost(self):
        conf = {
            "target_sources": 10000,
            "max_call_budget_usd": 0.12,
            "max_incremental_cli_estimate_usd": 5,
        }
        dump(
            self.root / "SOURCES.json",
            [
                {
                    "review_id": f"HC{number:03d}",
                    "source_id": f"source-{number:03d}",
                    "reuse_canary": number <= 50,
                }
                for number in range(1, 191)
            ],
        )
        completed_cost = 1.73492565
        for batch_number in range(1, 27):
            prefix = self.root / "provider" / f"batch_{batch_number:05d}"
            first_id = 51 + (batch_number - 1) * 5
            dump(prefix.with_suffix(".request.json"), {})
            dump(
                prefix.with_suffix(".raw.json"),
                {"total_cost_usd": completed_cost / 26},
            )
            dump(
                prefix.with_suffix(".parsed.json"),
                {
                    "records": [
                        {"id": f"HC{number:03d}", "status": "ok", "audit_flags": {}}
                        for number in range(first_id, first_id + 5)
                    ]
                },
            )

        self.quarantine()
        current = state(self.root, conf, "test")

        self.assertEqual(current["reused_canary_triplets"], 50)
        self.assertEqual(current["new_generated_triplets"], 130)
        self.assertEqual(current["total_generated_triplets"], 180)
        self.assertEqual(current["new_rejected_sources"], 0)
        self.assertEqual(current["quarantined_source_count"], 5)
        self.assertEqual(current["quarantined_source_ids"], self.ids)
        self.assertEqual(current["calls_without_final_cost"], 0)
        self.assertAlmostEqual(current["incremental_cli_estimate_usd"], 1.74467175)
        self.assertAlmostEqual(
            current["conservative_cli_estimate_reserved_usd"], 1.74467175
        )
        self.assertFalse(self.parsed_path.exists())

    def test_resume_archives_hashes_without_changing_provider_or_status_evidence(self):
        self.quarantine()
        conf = self.prepare_resume_files()
        completed = self.root / "provider" / "batch_00026.parsed.json"
        dump(completed, {"request_sha256": "e" * 64, "records": [{"id": "HC180", "status": "ok"}]})
        preserved = [
            self.request_path,
            self.raw_path,
            completed,
            self.root / "SOURCES.json",
            self.root / "JOB.json",
            self.root / "RUN_STATUS.json",
            self.root / "LAUNCH.json",
        ]
        prior_bytes = {path: path.read_bytes() for path in preserved}

        name = prepare_resume(self.root, conf)
        history = json.loads((self.root / "RESUME_HISTORY" / name).read_text())

        for path, expected_bytes in prior_bytes.items():
            with self.subTest(path=path.name):
                self.assertEqual(path.read_bytes(), expected_bytes)
        for path in (self.request_path, self.raw_path, completed):
            relative = str(path.relative_to(self.root))
            self.assertEqual(history["preserved_file_sha256"][relative], file_sha256(path))
        self.assertEqual(history["sources_sha256"], file_sha256(self.root / "SOURCES.json"))
        self.assertEqual(history["previous_status"]["state"], "provider_error")
        self.assertEqual(history["quarantine"]["source_ids"], self.ids)
        self.assertTrue(history["no_completed_batch_retry"])
        self.assertTrue(history["no_cap_increase"])
        self.assertTrue(history["no_extra_usage_activation"])

    def test_resume_cannot_bypass_quota_billing_budget_or_format_stops(self):
        self.quarantine()
        for reason in (
            "account_quota_warning",
            "account_quota_rejected",
            "account_quota_or_rate_limit",
            "overage_use_reported",
            "billing_or_credits_required",
            "incremental_estimate_safety_cap",
            "per_call_estimate_safety_cap",
            "provider_retry_requested_no_retry_permitted",
            "invalid_provider_output_no_retry",
        ):
            with self.subTest(reason=reason):
                conf = self.prepare_resume_files(reason=reason)
                with self.assertRaises(RuntimeError):
                    prepare_resume(self.root, conf)
                self.assertFalse((self.root / "RESUME_HISTORY").exists())

    def test_resume_rejects_increased_cumulative_budget_cap(self):
        self.quarantine()
        conf = self.prepare_resume_files()
        with self.assertRaises(RuntimeError):
            prepare_resume(self.root, {**conf, "max_incremental_cli_estimate_usd": 6})
        self.assertFalse((self.root / "RESUME_HISTORY").exists())

    def test_resume_rejects_unresolved_worker_lock(self):
        self.quarantine()
        conf = self.prepare_resume_files()
        dump(self.root / "WORKER_LOCK.json", {"pid": -1})
        with self.assertRaises(RuntimeError):
            prepare_resume(self.root, conf)
        self.assertFalse((self.root / "RESUME_HISTORY").exists())


if __name__ == "__main__":
    unittest.main()
