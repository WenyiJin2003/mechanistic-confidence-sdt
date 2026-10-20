import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))
from transport_defer import (IDLE_ERROR, create_transport_defer,
                             deferred_transport_batches, validate_transport_defer)


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


class TransportDeferTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.batch = "batch_00450"
        self.prefix = self.root / "provider" / self.batch
        self.ids = [f"HC{number}" for number in range(2296, 2301)]
        self.request = {"request_sha256": "a" * 64, "model": "claude-haiku-5-5",
                        "data": {"records": [{"id": key} for key in self.ids]}}
        self.raw = {"type": "result", "subtype": "success", "is_error": True,
                    "stop_reason": "stop_sequence", "result": IDLE_ERROR,
                    "modelUsage": {}, "usage": {"input_tokens": 0, "output_tokens": 0},
                    "total_cost_usd": 0, "terminal_reason": "completed", "api_error_status": None}
        self.events = [
            {"type": "system", "subtype": "init", "model": "claude-haiku-5-5"},
            {"type": "assistant", "message": {"model": "claude-haiku-5-5", "role": "assistant",
                "stop_reason": None, "usage": {"output_tokens": 2},
                "content": [{"type": "thinking", "thinking": "", "signature": ""}]}},
            {"type": "assistant", "error": "unknown", "message": {"model": "<synthetic>",
                "role": "assistant", "stop_reason": "stop_sequence",
                "content": [{"type": "text", "text": IDLE_ERROR}]}},
            copy.deepcopy(self.raw),
        ]
        write_json(self.prefix.with_suffix(".request.json"), self.request)
        self.write_raw_and_events()
        write_json(self.prefix.with_suffix(".quota.json"), {"events": [], "quota_reporting": "unreported"})
        self.prefix.with_suffix(".stderr.txt").write_text("", encoding="utf-8")

    def write_raw_and_events(self, raw=None, events=None):
        raw = self.raw if raw is None else raw
        events = self.events if events is None else events
        write_json(self.prefix.with_suffix(".raw.json"), raw)
        self.prefix.with_suffix(".events.jsonl").write_text(
            "".join(json.dumps(event, ensure_ascii=False) + "\n" for event in events), encoding="utf-8")

    def snapshot(self):
        return {path: path.read_bytes() for path in self.root.rglob("*") if path.is_file()}

    def assert_cannot_create(self):
        with self.assertRaises(RuntimeError):
            create_transport_defer(self.root, self.batch)
        self.assertFalse((self.root / "DEFERRED_TRANSPORT_BATCHES" / f"{self.batch}.json").exists())

    def test_exact_empty_transport_error_is_pinned_without_claiming_free_usage_or_salvage(self):
        originals = self.snapshot()
        entry = create_transport_defer(self.root, self.batch)
        self.assertEqual(entry["batch"], self.batch)
        self.assertEqual(entry["source_ids"], self.ids)
        self.assertEqual(entry["request_sha256"], self.request["request_sha256"])
        self.assertEqual(entry["decision"], "defer_transport_failure_without_retry")
        self.assertIs(entry["no_cache_salvage"], True)
        self.assertIs(entry["no_resubmission"], True)
        self.assertEqual(entry["usage_reporting"], "unreported")
        self.assertEqual(entry["provider_reported_cost_usd"], 0)
        self.assertIs(entry["zero_report_not_invoice"], True)
        self.assertEqual(entry["reviewed_narrow_transport_signature"], "v1")
        self.assertEqual(entry["artifact_file_sha256"], {
            str(path.relative_to(self.root)): hashlib.sha256(data).hexdigest() for path, data in originals.items()})
        for path, data in originals.items():
            self.assertEqual(path.read_bytes(), data)
        before = self.snapshot()
        self.assertEqual(create_transport_defer(self.root, self.batch), entry)
        self.assertEqual(validate_transport_defer(self.prefix, entry, self.request["request_sha256"], self.ids), entry)
        self.assertEqual(deferred_transport_batches(self.root), [entry])
        self.assertEqual(self.snapshot(), before)

    def test_different_errors_refusals_or_reported_cost_are_not_this_transport_signature(self):
        for change in [
            {"is_error": False}, {"stop_reason": "refusal"}, {"stop_reason": "max_tokens"},
            {"result": "API Error: provider refused the request"},
            {"result": IDLE_ERROR + " extra"}, {"total_cost_usd": 0.001},
            {"total_cost_usd": False}, {"total_cost_usd": None},
        ]:
            with self.subTest(change=change):
                raw = {**self.raw, **change}
                self.write_raw_and_events(raw, [*self.events[:-1], raw])
                self.assert_cannot_create()

    def test_quota_warning_rejection_overage_billing_and_retry_events_are_rejected(self):
        controls = [
            {"type": "rate_limit_event", "rate_limit_info": {"status": "rejected"}},
            {"type": "rate_limit_event", "rate_limit_info": {"status": "warning"}},
            {"type": "rate_limit_event", "rate_limit_info": {"status": "allowed", "isUsingOverage": True}},
            {"type": "rate_limit_event", "rate_limit_info": {"status": "allowed", "rateLimitType": "overage"}},
            {"type": "system", "subtype": "api_retry"},
            {"type": "api_retry"},
            {"type": "system", "subtype": "init", "retry_after": 1},
            {"type": "system", "subtype": "init", "error": "billing_error: payment required"},
            {"type": "system", "subtype": "init", "error": "insufficient credits"},
            {"type": "system", "subtype": "init", "error": "Usage Policy refusal"},
            {"type": "system", "subtype": "init", "error": {"message": "billing_error"}},
            {"type": "system", "subtype": "init", "diagnostics": {"refusal": "policy"}},
            {"type": "system", "subtype": "init", "api_error_status": 429},
            {"type": "system", "subtype": "init", "rate_limit_info": {"status": "warning"}},
        ]
        for event in controls:
            with self.subTest(event=event):
                self.write_raw_and_events(events=[*self.events[:-1], event, self.raw])
                self.assert_cannot_create()

    def test_unclassified_nested_partial_output_is_not_hidden_by_an_empty_content_block(self):
        for payload in [
            {"partial_response": '{"records":['}, {"delta": {"text": "Partial response"}},
            {"diagnostics": {"text": "Partial response"}}, {"content": [{"text": "Partial response"}]},
        ]:
            with self.subTest(payload=payload):
                events = copy.deepcopy(self.events)
                events[1]["message"].update(payload)
                self.write_raw_and_events(events=events)
                self.assert_cannot_create()

    def test_optional_quota_and_stderr_cannot_hide_quota_billing_or_generated_output(self):
        quota_path = self.prefix.with_suffix(".quota.json")
        for quota in [None, {}, {"events": [{"status": "rejected"}]},
                      {"events": [{"status": "allowed", "isUsingOverage": True}]}]:
            with self.subTest(quota=quota):
                write_json(quota_path, quota)
                self.assert_cannot_create()
        write_json(quota_path, {"events": []})
        for stderr in ["billing_error: credits required", '{"records":[', "Unclassified warning"]:
            with self.subTest(stderr=stderr):
                self.prefix.with_suffix(".stderr.txt").write_text(stderr, encoding="utf-8")
                self.assert_cannot_create()

    def test_real_generated_text_or_unknown_partial_blocks_are_never_salvaged(self):
        for block in [
            {"type": "text", "text": "Partial response"},
            {"type": "text", "text": '{"records":[{"id":"HC2296"'},
            {"type": "text", "text": json.dumps({"records": [{"id": self.ids[0], "status": "ok"}]})},
            {"type": "text", "text": IDLE_ERROR},
            {"type": "thinking", "thinking": "Nonempty generated content", "signature": ""},
            {"type": "thinking", "thinking": "", "extra_text": "Partial response"},
            {"type": "tool_use", "input": {}},
        ]:
            with self.subTest(block=block):
                generated = {"type": "assistant", "message": {
                    "model": self.request["model"], "content": [block]}}
                self.write_raw_and_events(events=[self.events[0], generated, *self.events[2:]])
                self.assert_cannot_create()

    def test_only_exact_synthetic_error_text_is_allowed(self):
        for content in [
            [{"type": "text", "text": IDLE_ERROR + " partial output"}],
            [{"type": "text", "text": IDLE_ERROR, "partial_text": "response"}],
            [{"type": "thinking", "thinking": ""}],
        ]:
            with self.subTest(content=content):
                changed = copy.deepcopy(self.events)
                changed[2]["message"]["content"] = content
                self.write_raw_and_events(events=changed)
                self.assert_cannot_create()

    def test_malformed_or_incomplete_streams_and_wrong_model_metadata_fail_closed(self):
        event_path = self.prefix.with_suffix(".events.jsonl")
        for text in ["", "not JSON\n", "[]\n", "null\n", "{}\n\n", '{"type":"result","type":"result"}\n']:
            with self.subTest(text=text):
                event_path.write_text(text, encoding="utf-8")
                self.assert_cannot_create()
        for events in [self.events[:-1], [*self.events, self.raw], [self.events[0], self.raw],
                       [*self.events[:-1], {**self.raw, "terminal_reason": "different"}]]:
            with self.subTest(events=events):
                self.write_raw_and_events(events=events)
                self.assert_cannot_create()
        changed = copy.deepcopy(self.events)
        changed[1]["message"]["model"] = "another-model"
        self.write_raw_and_events(events=changed)
        self.assert_cannot_create()

    def test_original_evidence_pins_and_manifest_metadata_cannot_be_changed(self):
        entry = create_transport_defer(self.root, self.batch)
        for suffix in (".request.json", ".raw.json", ".events.jsonl", ".quota.json", ".stderr.txt"):
            path = self.prefix.with_suffix(suffix)
            before = path.read_bytes()
            with self.subTest(path=path.name):
                path.write_bytes(before + b"\n")
                with self.assertRaises(RuntimeError):
                    validate_transport_defer(self.prefix, entry)
                path.write_bytes(before)
        for field, value in [
            ("batch", "batch_00451"), ("request_sha256", "b" * 64),
            ("source_ids", ["unknown"]), ("artifact_file_sha256", {}), ("decision", "retry"),
            ("no_cache_salvage", False), ("no_resubmission", False), ("usage_reporting", "free"),
            ("provider_reported_cost_usd", False), ("zero_report_not_invoice", False),
            ("reviewed_narrow_transport_signature", "v2"),
        ]:
            with self.subTest(field=field):
                with self.assertRaises(RuntimeError):
                    validate_transport_defer(self.prefix, {**entry, field: value})
        with self.assertRaises(RuntimeError):
            validate_transport_defer(self.prefix, entry, request_hash="c" * 64)
        with self.assertRaises(RuntimeError):
            validate_transport_defer(self.prefix, entry, source_ids=["unknown"])

    def test_new_artifacts_deleted_artifacts_and_parsed_output_invalidate_deferral(self):
        entry = create_transport_defer(self.root, self.batch)
        for suffix in (".parsed.json", ".error.json", ".request.json.pending"):
            path = self.prefix.with_suffix(suffix)
            with self.subTest(path=path.name):
                write_json(path, {})
                with self.assertRaises(RuntimeError):
                    validate_transport_defer(self.prefix, entry)
                path.unlink()
        path = self.prefix.with_suffix(".quota.json")
        before = path.read_bytes()
        path.unlink()
        with self.assertRaises(RuntimeError):
            validate_transport_defer(self.prefix, entry)
        path.write_bytes(before)

    def test_optional_artifact_created_after_review_is_not_silently_accepted(self):
        quota = self.prefix.with_suffix(".quota.json")
        quota.unlink()
        entry = create_transport_defer(self.root, self.batch)
        write_json(quota, {"events": []})
        with self.assertRaises(RuntimeError):
            validate_transport_defer(self.prefix, entry)

    def test_duplicate_empty_or_invalid_request_ids_missing_evidence_and_parsed_cache_reject(self):
        for ids in [[], [self.ids[0], self.ids[0]], [""], [None], [1]]:
            with self.subTest(ids=ids):
                request = {**self.request, "data": {"records": [{"id": key} for key in ids]}}
                write_json(self.prefix.with_suffix(".request.json"), request)
                self.assert_cannot_create()
        write_json(self.prefix.with_suffix(".request.json"), self.request)
        write_json(self.prefix.with_suffix(".parsed.json"), {"records": []})
        self.assert_cannot_create()
        self.prefix.with_suffix(".parsed.json").unlink()
        self.prefix.with_suffix(".events.jsonl").unlink()
        self.assert_cannot_create()

    def test_listing_revalidates_saved_manifests_and_rejects_malformed_batch_names(self):
        entry = create_transport_defer(self.root, self.batch)
        manifest = self.root / "DEFERRED_TRANSPORT_BATCHES" / f"{self.batch}.json"
        write_json(manifest, {**entry, "no_resubmission": False})
        with self.assertRaises(RuntimeError):
            deferred_transport_batches(self.root)
        for name in ("../batch_00450", "batch_450", "batch_00450.raw.json"):
            with self.subTest(name=name):
                with self.assertRaises(RuntimeError):
                    create_transport_defer(self.root, name)


if __name__ == "__main__":
    unittest.main()
