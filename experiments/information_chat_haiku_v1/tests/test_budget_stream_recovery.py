import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))
from budget_stream_recovery import LOCAL_GUARD_ERROR, inspect_budget_cache
from run_expansion import build_request_data, dump, fingerprint, request_record, sha


class BudgetStreamRecoveryTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.batch = "batch_00719"
        self.prefix = self.root / "provider" / self.batch
        self.prompt = "Preserve every source claim. Return exactly one record per id."
        path = self.root / "prompt.txt"
        path.write_text(self.prompt, encoding="utf-8")
        self.config = {"model": "claude-haiku-5-5", "max_output_tokens": 10000,
                       "batch_size": 5, "prompt_file": str(path)}
        self.sources = [{"review_id": f"HC{index}", "source_id": f"source-{index}",
                         "question": f"What is sample {index}?", "original": f"Sample {index} contains café facts.  "}
                        for index in range(3641, 3646)]
        self.ids = [row["review_id"] for row in self.sources]
        self.records = [{"id": row["review_id"], "status": "ok", "confident": row["original"],
                         "hesitant": row["original"].replace(" contains ", " may contain "), "reject_reason": None}
                        for row in self.sources]
        self.request = {"model": self.config["model"], "prompt": self.prompt, "prompt_sha256": sha(self.prompt),
                        "request_sha256": fingerprint(self.config, self.prompt, self.sources),
                        "data": build_request_data(self.prompt, [request_record(row) for row in self.sources])}
        self.raw = {"type": "result", "subtype": "error_max_budget_usd", "is_error": True,
                    "stop_reason": "end_turn", "errors": [LOCAL_GUARD_ERROR],
                    "modelUsage": {self.config["model"]: {"outputTokens": 7879}},
                    "total_cost_usd": 0.12744975, "api_error_status": None}
        dump(self.root / "SOURCES.json", self.sources)
        dump(self.prefix.with_suffix(".request.json"), self.request)
        dump(self.prefix.with_suffix(".quota.json"), {"events": [], "quota_reporting": "unreported"})
        self.write()

    def events(self, raw=None, payload=None, assistant_stop_reason=None):
        raw = self.raw if raw is None else raw
        payload = json.dumps({"records": self.records}, ensure_ascii=False) if payload is None else payload
        return [
            {"type": "system", "subtype": "init", "model": self.config["model"]},
            {"type": "assistant", "message": {"model": self.config["model"], "stop_reason": None,
                "content": [{"type": "thinking", "thinking": "", "signature": ""}]}},
            {"type": "assistant", "message": {"model": self.config["model"], "stop_reason": assistant_stop_reason,
                "content": [{"type": "text", "text": payload}]}}, raw,
        ]

    def write(self, raw=None, events=None, payload=None):
        raw = self.raw if raw is None else raw
        dump(self.prefix.with_suffix(".raw.json"), raw)
        events = self.events(raw, payload) if events is None else events
        self.prefix.with_suffix(".events.jsonl").write_text(
            "".join(json.dumps(event, ensure_ascii=False) + "\n" for event in events), encoding="utf-8")

    def inspect(self):
        return inspect_budget_cache(self.root, self.batch, self.config)

    def test_full_cached_text_is_returned_unchanged_while_original_terminal_stays_an_error(self):
        before = {path: path.read_bytes() for path in self.root.rglob("*") if path.is_file()}
        observed = self.inspect()
        self.assertEqual(observed["cached_ids"], self.ids)
        self.assertEqual(observed["expected_ids"], self.ids)
        self.assertEqual(observed["cached_records"], self.records)
        self.assertEqual(observed["missing_ids"], [])
        self.assertEqual(len(observed["original_file_sha256"]), 4)
        metadata = observed["local_budget_terminal_normalization"]
        self.assertEqual(metadata["normalization"], "reviewed_local_budget_terminal_only")
        self.assertIsNone(metadata["assistant_stop_reason"])
        self.assertEqual(metadata["final_stop_reason"], "end_turn")
        self.assertEqual(metadata["original_terminal_subtype"], "error_max_budget_usd")
        self.assertIs(metadata["original_terminal_is_error"], True)
        self.assertIs(metadata["raw_terminal_preserved"], True)
        self.assertIs(metadata["cached_text_changed"], False)
        self.assertEqual(metadata["additional_provider_calls"], 0)
        self.assertEqual(metadata["quota_reporting"], "unreported")
        self.assertIs(metadata["cli_estimate_not_invoice"], True)
        observed["cached_records"][0]["confident"] = "Changed only in memory"
        self.assertEqual(self.inspect()["cached_records"], self.records)
        self.assertEqual({path: path.read_bytes() for path in self.root.rglob("*") if path.is_file()}, before)
        self.assertIs(json.loads(self.prefix.with_suffix(".raw.json").read_text())["is_error"], True)

    def test_assistant_none_or_end_turn_is_explicit_but_no_other_stop_reason_is_accepted(self):
        self.write(events=self.events(assistant_stop_reason="end_turn"))
        self.assertEqual(self.inspect()["local_budget_terminal_normalization"]["assistant_stop_reason"], "end_turn")
        for reason in ("refusal", "max_tokens", "stop_sequence", "timeout"):
            with self.subTest(reason=reason):
                self.write(events=self.events(assistant_stop_reason=reason))
                with self.assertRaises(RuntimeError):
                    self.inspect()

    def test_only_exact_local_terminal_and_positive_sole_model_usage_are_accepted(self):
        changes = [
            {"is_error": False}, {"subtype": "success"}, {"stop_reason": "max_tokens"},
            {"stop_reason": "refusal"}, {"errors": [LOCAL_GUARD_ERROR, "billing required"]},
            {"errors": ["Reached maximum budget ($0.24)"]}, {"errors": []},
            {"result": '{"records":[]}'}, {"structured_output": {"records": []}},
            {"total_cost_usd": 0}, {"total_cost_usd": False},
            {"modelUsage": {}}, {"modelUsage": {"another-model": {"outputTokens": 7879}}},
            {"modelUsage": {self.config["model"]: {"outputTokens": 0}}},
            {"modelUsage": {self.config["model"]: {"outputTokens": True}}},
            {"api_error_status": 429},
        ]
        for change in changes:
            with self.subTest(change=change):
                self.write(raw={**self.raw, **change})
                with self.assertRaises(RuntimeError):
                    self.inspect()

    def test_partial_malformed_duplicate_unknown_or_empty_records_are_never_recovered(self):
        candidates = [
            self.records[:4], [*self.records, self.records[-1]],
            [self.records[1], self.records[0], *self.records[2:]],
            [self.records[0], self.records[0], *self.records[2:]],
            [*self.records[:-1], {**self.records[-1], "id": "unknown"}],
            [*self.records[:-1], {**self.records[-1], "confident": ""}],
            [*self.records[:-1], {**self.records[-1], "extra": True}],
        ]
        for records in candidates:
            with self.subTest(records=records):
                self.write(payload=json.dumps({"records": records}))
                with self.assertRaises(RuntimeError):
                    self.inspect()
        for payload in ['{"records":[', '{"records":[],"records":[]}', '{"records":NaN}', "null"]:
            with self.subTest(payload=payload):
                self.write(payload=payload)
                with self.assertRaises(RuntimeError):
                    self.inspect()

    def test_policy_billing_timeout_retry_quota_or_ambiguous_stream_fails_closed(self):
        base = self.events()
        extra_events = [
            {"type": "system", "subtype": "api_retry"},
            {"type": "assistant", "error": "billing_error"},
            {"type": "system", "subtype": "init", "errors": ["Usage Policy refusal"]},
            {"type": "system", "subtype": "init", "diagnostics": {"error": "Stream idle timeout"}},
            {"type": "rate_limit_event", "rate_limit_info": {"status": "rejected"}},
            {"type": "rate_limit_event", "rate_limit_info": {"status": "allowed", "isUsingOverage": True}},
        ]
        candidates = [[*base[:-1], event, base[-1]] for event in extra_events]
        changed = copy.deepcopy(base)
        changed[2]["message"]["model"] = "another-model"
        candidates.append(changed)
        candidates.extend([base[:-1], [*base, self.raw], [*base[:-1], base[2], base[-1]],
                           [*base[:-1], {**self.raw, "stop_reason": "different"}]])
        for events in candidates:
            with self.subTest(events=events):
                self.write(events=events)
                with self.assertRaises(RuntimeError):
                    self.inspect()

    def test_original_request_sources_and_prompt_fingerprint_cannot_change(self):
        for change in [{"request_sha256": "b" * 64}, {"prompt_sha256": "c" * 64},
                       {"model": "another-model"}, {"data": {**self.request["data"], "extra": True}}]:
            with self.subTest(change=change):
                dump(self.prefix.with_suffix(".request.json"), {**self.request, **change})
                with self.assertRaises(RuntimeError):
                    self.inspect()
        dump(self.prefix.with_suffix(".request.json"), self.request)
        changed = copy.deepcopy(self.sources)
        changed[0]["original"] = "A changed original"
        dump(self.root / "SOURCES.json", changed)
        with self.assertRaises(RuntimeError):
            self.inspect()

    def test_saved_quota_may_be_unreported_but_cannot_warn_or_use_overage(self):
        path = self.prefix.with_suffix(".quota.json")
        dump(path, {"events": [{"status": "allowed", "isUsingOverage": False}]})
        self.assertEqual(self.inspect()["local_budget_terminal_normalization"]["quota_reporting"], "allowed_no_overage")
        for saved in [{}, {"events": [{"status": "warning", "isUsingOverage": False}]},
                      {"events": [{"status": "allowed", "isUsingOverage": True}]}]:
            with self.subTest(saved=saved):
                dump(path, saved)
                with self.assertRaises(RuntimeError):
                    self.inspect()

    def test_unknown_artifacts_stderr_nonfinite_raw_and_malformed_stream_are_rejected(self):
        path = self.prefix.with_suffix(".error.json")
        dump(path, {})
        with self.assertRaises(RuntimeError):
            self.inspect()
        path.unlink()
        path = self.prefix.with_suffix(".stderr.txt")
        path.write_text("A transport or billing warning", encoding="utf-8")
        with self.assertRaises(RuntimeError):
            self.inspect()
        path.unlink()
        raw_path = self.prefix.with_suffix(".raw.json")
        raw_path.write_text('{"total_cost_usd":NaN}', encoding="utf-8")
        with self.assertRaises(RuntimeError):
            self.inspect()
        self.write()
        event_path = self.prefix.with_suffix(".events.jsonl")
        for text in ["[]\n", "not JSON\n", '{"type":"result","type":"result"}\n']:
            with self.subTest(text=text):
                event_path.write_text(text, encoding="utf-8")
                with self.assertRaises(RuntimeError):
                    self.inspect()


if __name__ == "__main__":
    unittest.main()
