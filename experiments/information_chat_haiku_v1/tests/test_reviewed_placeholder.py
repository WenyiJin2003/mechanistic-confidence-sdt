import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))
from reviewed_placeholder import inspect_placeholder_cache
from run_expansion import build_request_data, dump, fingerprint, request_record, sha


class ReviewedPlaceholderTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.batch = "batch_00632"
        self.prefix = self.root / "provider" / self.batch
        self.prompt = "Preserve each response. Return exactly one record per id."
        prompt_path = self.root / "prompt.txt"
        prompt_path.write_text(self.prompt, encoding="utf-8")
        self.config = {"model": "claude-haiku-5-5", "max_output_tokens": 10000,
                       "batch_size": 5, "prompt_file": str(prompt_path)}
        self.sources = [{"review_id": f"HC{number}", "source_id": f"source-{number}",
                         "question": f"What is sample {number}?", "original": f"Sample {number} is synthetic."}
                        for number in range(3206, 3211)]
        self.ids = [row["review_id"] for row in self.sources]
        self.records = [{"id": row["review_id"], "status": "ok", "confident": row["original"],
                         "hesitant": row["original"].replace(" is ", " may be "), "reject_reason": None}
                        for row in self.sources]
        self.placeholder = {"id": self.ids[-1] + "_PLACEHOLDER_REMOVED", "status": "ok",
                            "confident": "", "hesitant": "", "reject_reason": None}
        self.request = {"model": self.config["model"], "prompt": self.prompt,
                        "prompt_sha256": sha(self.prompt),
                        "request_sha256": fingerprint(self.config, self.prompt, self.sources),
                        "data": build_request_data(self.prompt, [request_record(row) for row in self.sources])}
        self.raw = {"type": "result", "subtype": "success", "is_error": False, "stop_reason": "end_turn",
                    "modelUsage": {self.config["model"]: {"outputTokens": 120}},
                    "result": json.dumps({"records": [*self.records, self.placeholder]})}
        self.quota = {"status": "allowed", "isUsingOverage": False, "rateLimitType": "five_hour",
                      "overageStatus": "rejected", "overageDisabledReason": "org_level_disabled"}
        dump(self.root / "SOURCES.json", self.sources)
        dump(self.prefix.with_suffix(".request.json"), self.request)
        self.write_result(self.raw)
        dump(self.prefix.with_suffix(".quota.json"), {"events": [self.quota]})
        self.prefix.with_suffix(".stderr.txt").write_text("", encoding="utf-8")

    def events(self, raw):
        return [
            {"type": "system", "subtype": "init", "model": self.config["model"]},
            {"type": "assistant", "message": {"model": self.config["model"], "content": [
                {"type": "thinking", "thinking": "", "signature": ""}]}},
            {"type": "assistant", "message": {"model": self.config["model"],
                "content": [{"type": "text", "text": raw["result"]}]}},
            {"type": "rate_limit_event", "rate_limit_info": self.quota},
            raw,
        ]

    def write_result(self, raw=None, events=None):
        raw = self.raw if raw is None else raw
        dump(self.prefix.with_suffix(".raw.json"), raw)
        self.prefix.with_suffix(".events.jsonl").write_text(
            "".join(json.dumps(event) + "\n" for event in (self.events(raw) if events is None else events)),
            encoding="utf-8")

    def inspect(self):
        return inspect_placeholder_cache(self.root, self.batch, self.config)

    def test_only_exact_final_empty_placeholder_is_removed_in_memory_with_all_original_pins(self):
        before = {path: path.read_bytes() for path in self.root.rglob("*") if path.is_file()}
        observed = self.inspect()
        self.assertEqual(observed["expected_ids"], self.ids)
        self.assertEqual(observed["cached_ids"], self.ids)
        self.assertEqual(observed["cached_records"], self.records)
        self.assertEqual(observed["missing_ids"], [])
        expected_pins = {str(path.relative_to(self.root)): hashlib.sha256(data).hexdigest()
                         for path, data in before.items() if path.parent.name == "provider"}
        self.assertEqual(observed["original_file_sha256"], expected_pins)
        metadata = observed["reviewed_empty_placeholder_normalization"]
        canonical = json.dumps(self.placeholder, sort_keys=True, ensure_ascii=False,
                               separators=(",", ":"), allow_nan=False)
        self.assertEqual(metadata, {"normalization": "reviewed_empty_placeholder_only", "discarded_index": 5,
            "discarded_id": self.placeholder["id"],
            "discarded_payload_sha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
            "returned_ids": [*self.ids, self.placeholder["id"]],
            "cached_text_changed": False, "additional_provider_calls": 0})
        observed["cached_records"][0]["confident"] = "Only the returned in-memory copy changed."
        self.assertEqual(self.inspect()["cached_records"], self.records)
        self.assertEqual({path: path.read_bytes() for path in self.root.rglob("*") if path.is_file()}, before)

    def test_nonempty_whitespace_or_differently_shaped_placeholder_is_never_ignored(self):
        changes = [{"confident": " "}, {"hesitant": "Nonempty answer"}, {"confident": None},
                   {"status": "reject"}, {"reject_reason": "A reason"}, {"extra": 0},
                   {"id": self.ids[-1] + "_OTHER"}, {"id": self.ids[0] + "_PLACEHOLDER_REMOVED"}]
        for change in changes:
            with self.subTest(change=change):
                raw = {**self.raw, "result": json.dumps({"records": [*self.records, {**self.placeholder, **change}]})}
                self.write_result(raw)
                with self.assertRaises(RuntimeError):
                    self.inspect()
        missing = dict(self.placeholder)
        missing.pop("reject_reason")
        self.write_result({**self.raw, "result": json.dumps({"records": [*self.records, missing]})})
        with self.assertRaises(RuntimeError):
            self.inspect()

    def test_all_expected_records_must_be_complete_unique_and_in_original_order(self):
        candidates = [
            self.records,
            [*self.records, self.placeholder, self.placeholder],
            [self.placeholder, *self.records],
            [self.records[1], self.records[0], *self.records[2:], self.placeholder],
            [self.records[0], self.records[0], *self.records[2:], self.placeholder],
            [*self.records[:-1], {**self.records[-1], "id": "unknown"}, self.placeholder],
            [*self.records[:-1], {**self.records[-1], "confident": ""}, self.placeholder],
            [*self.records[:-1], {**self.records[-1], "hesitant": self.records[-1]["confident"]}, self.placeholder],
            [*self.records[:-1], {**self.records[-1], "extra": True}, self.placeholder],
        ]
        for records in candidates:
            with self.subTest(records=records):
                self.write_result({**self.raw, "result": json.dumps({"records": records})})
                with self.assertRaises(RuntimeError):
                    self.inspect()

    def test_refusal_error_truncation_wrong_model_and_conflicting_structured_payload_reject(self):
        changes = [{"is_error": True}, {"stop_reason": "refusal"}, {"stop_reason": "max_tokens"},
                   {"subtype": "error"}, {"modelUsage": {"another-model": {"outputTokens": 120}}},
                   {"structured_output": {"records": self.records}}]
        for change in changes:
            with self.subTest(change=change):
                self.write_result({**self.raw, **change})
                with self.assertRaises(RuntimeError):
                    self.inspect()

    def test_request_source_prompt_data_and_fingerprint_are_bound(self):
        changes = [
            {"request_sha256": "b" * 64}, {"prompt": "Different semantic instructions"},
            {"prompt_sha256": "c" * 64}, {"model": "another-model"},
            {"data": {**self.request["data"], "unexpected": True}},
        ]
        for change in changes:
            with self.subTest(change=change):
                dump(self.prefix.with_suffix(".request.json"), {**self.request, **change})
                with self.assertRaises(RuntimeError):
                    self.inspect()
        dump(self.prefix.with_suffix(".request.json"), self.request)
        changed = copy.deepcopy(self.sources)
        changed[0]["original"] = "Changed frozen source"
        dump(self.root / "SOURCES.json", changed)
        with self.assertRaises(RuntimeError):
            self.inspect()

    def test_stream_text_final_result_quota_and_event_types_must_be_consistent(self):
        changes = []
        events = self.events(self.raw)
        changed = copy.deepcopy(events)
        changed[2]["message"]["content"][0]["text"] = json.dumps({"records": self.records})
        changes.append(changed)
        changed = copy.deepcopy(events)
        changed[-1]["stop_reason"] = "different"
        changes.append(changed)
        changed = copy.deepcopy(events)
        changed[2]["message"]["model"] = "<synthetic>"
        changes.append(changed)
        changed = copy.deepcopy(events)
        changed[3]["rate_limit_info"]["isUsingOverage"] = True
        changes.append(changed)
        changed = copy.deepcopy(events)
        changed[3]["rate_limit_info"]["status"] = "warning"
        changes.append(changed)
        changes.extend([events[:-1], [*events[:-1], {"type": "api_retry"}, events[-1]],
                        [*events[:-1], {"type": "assistant", "error": "billing_error"}, events[-1]]])
        for events in changes:
            with self.subTest(events=events):
                self.write_result(events=events)
                with self.assertRaises(RuntimeError):
                    self.inspect()

    def test_duplicate_keys_nonfinite_numbers_and_malformed_events_reject(self):
        raw_path = self.prefix.with_suffix(".raw.json")
        for result in ['{"records":[],"records":[]}', '{"records":NaN}']:
            with self.subTest(result=result):
                self.write_result({**self.raw, "result": result})
                with self.assertRaises(RuntimeError):
                    self.inspect()
        self.write_result()
        raw_text = raw_path.read_text()
        raw_path.write_text('{"is_error":false,' + raw_text.lstrip()[1:], encoding="utf-8")
        with self.assertRaises(RuntimeError):
            self.inspect()
        self.write_result()
        event_path = self.prefix.with_suffix(".events.jsonl")
        for text in ["not JSON\n", "[]\n", "null\n", "\n", '{"type":"system","type":"result"}\n']:
            with self.subTest(text=text):
                event_path.write_text(text, encoding="utf-8")
                with self.assertRaises(RuntimeError):
                    self.inspect()

    def test_original_inventory_pins_optional_artifacts_and_ignores_only_derived_parsed(self):
        original = self.inspect()["original_file_sha256"]
        dump(self.prefix.with_suffix(".parsed.json"), {"derived": "validated separately by recovery"})
        self.assertEqual(self.inspect()["original_file_sha256"], original)
        dump(self.prefix.with_suffix(".error.json"), {})
        with self.assertRaises(RuntimeError):
            self.inspect()
        self.prefix.with_suffix(".error.json").unlink()
        self.prefix.with_suffix(".quota.json").unlink()
        updated = self.inspect()["original_file_sha256"]
        self.assertNotEqual(updated, original)
        self.prefix.with_suffix(".stderr.txt").write_text("unclassified error", encoding="utf-8")
        with self.assertRaises(RuntimeError):
            self.inspect()


if __name__ == "__main__":
    unittest.main()
