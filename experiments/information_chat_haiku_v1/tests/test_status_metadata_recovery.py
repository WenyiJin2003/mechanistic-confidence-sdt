import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))
from status_metadata_recovery import inspect_status_cache
from run_expansion import build_request_data, dump, fingerprint, request_record, sha


class StatusMetadataRecoveryTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.batch = "batch_00847"
        self.prefix = self.root / "provider" / self.batch
        self.prompt = "Preserve every claim. Return exactly one response per id. OUTPUT CONTRACT V3"
        prompt_path = self.root / "prompt.txt"
        prompt_path.write_text(self.prompt, encoding="utf-8")
        self.config = {"model": "claude-haiku-5-5", "max_output_tokens": 10000,
                       "batch_size": 5, "prompt_file": str(prompt_path)}
        self.sources = [{"review_id": f"HC{index}", "source_id": f"source-{index}",
                         "question": f"What is sample {index}?", "original": f"Sample {index} is a café fact.  "}
                        for index in range(4281, 4286)]
        self.ids = [row["review_id"] for row in self.sources]
        self.records = [{"id": row["review_id"], "confident": row["original"],
                         "hesitant": row["original"].replace(" is ", " may be "), "reject_reason": None}
                        for row in self.sources]
        self.request = {"model": self.config["model"], "prompt": self.prompt, "prompt_sha256": sha(self.prompt),
                        "request_sha256": fingerprint(self.config, self.prompt, self.sources),
                        "data": build_request_data(self.prompt, [request_record(row) for row in self.sources])}
        self.payload = {"records": self.records, "required_output": {"record_count": 5}}
        self.raw = {"type": "result", "subtype": "success", "is_error": False,
                    "stop_reason": "end_turn", "modelUsage": {self.config["model"]: {"outputTokens": 800}}}
        dump(self.root / "SOURCES.json", self.sources)
        dump(self.prefix.with_suffix(".request.json"), self.request)
        dump(self.prefix.with_suffix(".quota.json"), {"events": [{"status": "allowed", "isUsingOverage": False}]})
        self.write()

    def events(self, raw):
        return [{"type": "system", "subtype": "init"},
                {"type": "assistant", "message": {"model": self.config["model"],
                    "content": [{"type": "text", "text": raw["result"]}]}}, raw]

    def write(self, payload=None, raw_changes=None, events=None):
        raw = {**self.raw, "result": json.dumps(self.payload if payload is None else payload, ensure_ascii=False),
               **(raw_changes or {})}
        dump(self.prefix.with_suffix(".raw.json"), raw)
        self.prefix.with_suffix(".events.jsonl").write_text(
            "".join(json.dumps(event, ensure_ascii=False) + "\n" for event in (self.events(raw) if events is None else events)),
            encoding="utf-8")
        return raw

    def inspect(self):
        return inspect_status_cache(self.root, self.batch, self.config)

    def test_count_only_echo_and_missing_status_are_normalized_only_in_memory(self):
        before = {path: path.read_bytes() for path in self.root.rglob("*") if path.is_file()}
        observed = self.inspect()
        self.assertEqual(observed["expected_ids"], self.ids)
        self.assertEqual(observed["cached_ids"], self.ids)
        self.assertEqual(observed["missing_ids"], [])
        self.assertEqual(observed["cached_records"], [{**row, "status": "ok"} for row in self.records])
        metadata = observed["missing_status_metadata_normalization"]
        self.assertEqual(metadata["echo_variant"], "record_count_only")
        self.assertEqual(metadata["added_field_ids"], self.ids)
        self.assertEqual(metadata["added_field"], "status")
        self.assertEqual(metadata["added_value"], "ok")
        self.assertIs(metadata["writer_schema_metadata_only"], True)
        self.assertIs(metadata["confidence_correctness_or_human_approval_claimed"], False)
        self.assertIs(metadata["cached_text_changed"], False)
        self.assertEqual(metadata["additional_provider_calls"], 0)
        canonical = lambda value: json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
        self.assertEqual(metadata["original_payload_semantic_sha256"], hashlib.sha256(canonical(self.payload).encode()).hexdigest())
        normalized = {**self.payload, "records": [{**row, "status": "ok"} for row in self.records]}
        self.assertEqual(metadata["normalized_payload_semantic_sha256"], hashlib.sha256(canonical(normalized).encode()).hexdigest())
        self.assertEqual({path: path.read_bytes() for path in self.root.rglob("*") if path.is_file()}, before)

    def test_full_echo_is_also_accepted_but_any_other_partial_or_type_change_rejects(self):
        full = copy.deepcopy(self.request["data"]["required_output"])
        self.write({**self.payload, "required_output": full})
        self.assertEqual(self.inspect()["missing_status_metadata_normalization"]["echo_variant"], "full_request_echo")
        for echo in [None, {}, {"record_count": 5.0}, {"record_count": True},
                     {"record_count": 4}, {"expected_ids": self.ids},
                     {"record_count": 5, "extra": True},
                     {"record_count": 5, "expected_ids": list(reversed(self.ids))}]:
            with self.subTest(echo=echo):
                self.write({**self.payload, "required_output": echo})
                with self.assertRaises(RuntimeError):
                    self.inspect()

    def test_explicit_status_of_any_value_missing_fields_or_other_fields_are_never_repaired(self):
        for status in ("ok", "reject", "unknown", None, False):
            with self.subTest(status=status):
                changed = copy.deepcopy(self.records)
                changed[0]["status"] = status
                self.write({**self.payload, "records": changed})
                with self.assertRaises(RuntimeError):
                    self.inspect()
        for change in [{"reject_reason": "Rejected"}, {"confident": " "}, {"hesitant": None}, {"extra": 0}]:
            with self.subTest(change=change):
                changed = copy.deepcopy(self.records)
                changed[-1].update(change)
                self.write({**self.payload, "records": changed})
                with self.assertRaises(RuntimeError):
                    self.inspect()

    def test_all_five_existing_ids_must_be_unique_complete_and_ordered(self):
        for records in [self.records[:4], [*self.records, self.records[-1]],
                        [self.records[0], self.records[0], *self.records[2:]],
                        list(reversed(self.records)), [*self.records[:-1], {**self.records[-1], "id": "unknown"}]]:
            with self.subTest(records=records):
                self.write({**self.payload, "records": records})
                with self.assertRaises(RuntimeError):
                    self.inspect()

    def test_terminal_model_payload_and_stream_evidence_must_agree(self):
        for change in [{"is_error": True}, {"stop_reason": "refusal"}, {"stop_reason": "max_tokens"},
                       {"subtype": "error_max_budget_usd"}, {"modelUsage": {"other-model": {}}},
                       {"structured_output": {"records": self.records}}]:
            with self.subTest(change=change):
                self.write(raw_changes=change)
                with self.assertRaises(RuntimeError):
                    self.inspect()
        raw = self.write()
        events = self.events(raw)
        events[1]["message"]["content"][0]["text"] = json.dumps({"records": self.records})
        self.write(events=events)
        with self.assertRaises(RuntimeError):
            self.inspect()

    def test_request_prompt_sources_and_original_data_fingerprint_are_bound(self):
        for change in [{"request_sha256": "b" * 64}, {"prompt": "changed"}, {"prompt_sha256": "c" * 64},
                       {"data": {**self.request["data"], "extra": 0}}]:
            with self.subTest(change=change):
                dump(self.prefix.with_suffix(".request.json"), {**self.request, **change})
                with self.assertRaises(RuntimeError):
                    self.inspect()
        dump(self.prefix.with_suffix(".request.json"), self.request)
        changed = copy.deepcopy(self.sources)
        changed[0]["original"] = "Changed source"
        dump(self.root / "SOURCES.json", changed)
        with self.assertRaises(RuntimeError):
            self.inspect()

    def test_duplicate_json_keys_nonfinite_and_extra_top_payload_fields_reject(self):
        for result in ['{"records":[],"records":[]}', '{"records":NaN}']:
            with self.subTest(result=result):
                self.write(raw_changes={"result": result})
                with self.assertRaises(RuntimeError):
                    self.inspect()
        self.write({**self.payload, "unexpected": True})
        with self.assertRaises(RuntimeError):
            self.inspect()

    def test_inventory_quota_and_stderr_are_pinned_and_unsafe_metadata_rejects(self):
        observed = self.inspect()
        self.assertEqual(len(observed["original_file_sha256"]), 4)
        quota_path = self.prefix.with_suffix(".quota.json")
        for quota in [{"events": [{"status": "warning", "isUsingOverage": False}]},
                      {"events": [{"status": "allowed", "isUsingOverage": True}]}]:
            with self.subTest(quota=quota):
                dump(quota_path, quota)
                with self.assertRaises(RuntimeError):
                    self.inspect()
        dump(quota_path, {"events": [{"status": "allowed", "isUsingOverage": False}]})
        extra = self.prefix.with_suffix(".error.json")
        dump(extra, {})
        with self.assertRaises(RuntimeError):
            self.inspect()
        extra.unlink()
        self.prefix.with_suffix(".stderr.txt").write_text("billing warning", encoding="utf-8")
        with self.assertRaises(RuntimeError):
            self.inspect()

    def test_success_flags_do_not_override_raw_billing_status_or_retry_controls(self):
        for change in [
            {"errors": ["billing_error: credits required"]},
            {"api_error_status": 402}, {"api_error_status": 429}, {"retry_after": 1},
            {"diagnostics": {"errors": ["quota exceeded"]}},
            {"diagnostics": {"provider_retry": True}},
        ]:
            with self.subTest(change=change):
                self.write(raw_changes=change)
                with self.assertRaises(RuntimeError):
                    self.inspect()

    def test_nested_stream_error_and_retry_controls_cannot_hide_behind_valid_payload(self):
        for control in [
            {"errors": ["billing required"]}, {"api_error_status": 402},
            {"diagnostics": {"errors": ["transport timeout"]}}, {"retry_count": 1},
        ]:
            with self.subTest(control=control):
                raw = self.write()
                events = self.events(raw)
                events[0].update(control)
                self.write(events=events)
                with self.assertRaises(RuntimeError):
                    self.inspect()
        raw = self.write()
        events = self.events(raw)
        events[1]["message"]["diagnostics"] = {"api_error_status": 429}
        self.write(events=events)
        with self.assertRaises(RuntimeError):
            self.inspect()

    def test_quoted_answer_text_about_credits_and_quota_is_not_a_provider_control(self):
        payload = copy.deepcopy(self.payload)
        payload["records"][0]["confident"] = "Credits and quota are terms in the source explanation."
        payload["records"][0]["hesitant"] = "Credits and quota may be terms in the source explanation."
        self.write(payload, raw_changes={"structured_output": payload})
        observed = self.inspect()
        self.assertEqual(observed["cached_records"][0]["confident"], payload["records"][0]["confident"])
        self.assertEqual(observed["cached_records"][0]["hesitant"], payload["records"][0]["hesitant"])


if __name__ == "__main__":
    unittest.main()
