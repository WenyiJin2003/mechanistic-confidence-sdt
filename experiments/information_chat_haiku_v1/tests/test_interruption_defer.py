import copy
import hashlib
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))
from interruption_defer import (DECISION, create_interruption_defer, interrupted_batches,
                                observed_interruption, validate_interruption_defer)


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


class InterruptionDeferTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.batch = "batch_00938"
        self.prefix = self.root / "provider" / self.batch
        self.ids = [f"HC{number}" for number in range(4736, 4741)]
        self.prompt = "Rewrite faithfully with distinct confidence and hesitation."
        self.request = {"request_sha256": "a" * 64, "started_at_utc": "2026-10-20T01:58:29+00:00",
            "model": "claude-haiku-5-5", "prompt": self.prompt,
            "prompt_sha256": hashlib.sha256(self.prompt.encode()).hexdigest(),
            "data": {"records": [{"id": key, "question": "A source question?",
                "original_response": "The original factual source."} for key in self.ids]},
            "account": {"authMethod": "claude.ai", "apiProvider": "firstParty",
                "subscriptionType": "enterprise", "orgName": "Harvard Edu for FAS/SEAS"},
            "internal_retries": 0}
        self.init = {"type": "system", "subtype": "init", "cwd": "/private/tmp/no-tools-init",
            "session_id": "9ae8e53a-9c55-4b0b-80ae-51548b0be71f", "tools": [],
            "mcp_servers": [], "model": "claude-haiku-5-5", "permissionMode": "dontAsk",
            "slash_commands": [], "apiKeySource": "none", "claude_code_version": "2.1.117",
            "output_style": "default", "agents": ["Explore"], "skills": ["debug"],
            "plugins": [], "uuid": "7ec50833-8d3d-4ccd-ac2f-e85e7d9096ad", "fast_mode_state": "off"}
        dump(self.prefix.with_suffix(".request.json"), self.request)
        self.write_events([self.init])
        self.review_path = self.root / "INTERRUPTION_RECOVERIES" / (self.batch + "_reviewed_1") / "REVIEW.json"
        self.review = {"kind": "reviewed_dead_worker_interruption", "batch": self.batch,
            "request_sha256": self.request["request_sha256"],
            "provider_files_sha256": self.attempt_pins(),
            "all_owned_processes_dead": True, "no_orphan_provider_processes": True}
        dump(self.review_path, self.review)

    def write_events(self, events):
        self.prefix.with_suffix(".events.jsonl").write_text(
            "".join(json.dumps(event) + "\n" for event in events), encoding="utf-8")

    def attempt_pins(self):
        return {str(path.relative_to(self.root)): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in sorted(self.prefix.parent.glob(self.batch + ".*"))}

    def snapshot(self):
        return {path: path.read_bytes() for path in self.root.rglob("*") if path.is_file()}

    def create(self):
        return create_interruption_defer(self.root, self.batch, self.review_path)

    def test_init_only_attempt_is_preserved_and_no_backend_usage_claim_is_made(self):
        before = self.snapshot()
        observed = observed_interruption(self.prefix)
        entry = self.create()
        self.assertEqual({key: entry[key] for key in observed}, observed)
        self.assertEqual(entry["decision"], DECISION)
        self.assertTrue(entry["no_resubmission"])
        self.assertEqual(entry["usage_reporting"], "unreported")
        self.assertIs(entry["zero_cost_claimed"], False)
        self.assertEqual(entry["additional_provider_calls"], 0)
        self.assertEqual(entry["review_file"], str(self.review_path.relative_to(self.root)))
        self.assertEqual(entry["review_file_sha256"], hashlib.sha256(self.review_path.read_bytes()).hexdigest())
        self.assertEqual(entry["source_ids"], self.ids)
        for path, value in before.items():
            self.assertEqual(path.read_bytes(), value)
        after = self.snapshot()
        self.assertEqual(self.create(), entry)
        self.assertEqual(validate_interruption_defer(self.prefix, entry,
            self.request["request_sha256"], self.ids), entry)
        self.assertEqual(interrupted_batches(self.root), [entry])
        self.assertEqual(self.snapshot(), after)

    def test_all_additional_artifacts_including_empty_stderr_or_quota_fail_closed(self):
        for suffix in (".raw.json", ".parsed.json", ".quota.json", ".stderr.txt", ".unknown"):
            with self.subTest(suffix=suffix):
                path = self.prefix.with_suffix(suffix)
                path.write_text("", encoding="utf-8")
                with self.assertRaises(RuntimeError):
                    self.create()
                path.unlink()

    def test_assistant_partial_text_empty_thinking_errors_results_and_quota_are_never_deferred(self):
        for event in (
            {"type": "assistant", "message": {"content": [{"type": "text", "text": "Answer"}]}},
            {"type": "assistant", "message": {"content": [{"type": "thinking", "thinking": ""}]}},
            {"type": "result", "is_error": False},
            {"type": "system", "subtype": "api_retry"},
            {"type": "error", "error": "refusal"},
            {"type": "rate_limit_event", "rate_limit_info": {"status": "allowed"}},
        ):
            with self.subTest(event=event):
                self.write_events([self.init, event])
                with self.assertRaises(RuntimeError):
                    observed_interruption(self.prefix)

    def test_ambiguous_trailing_lines_and_malformed_json_are_not_ignored(self):
        path = self.prefix.with_suffix(".events.jsonl")
        for text in ("", json.dumps(self.init) + "\n\n", json.dumps(self.init) + "\npartial",
                     '{"type":"system","type":"assistant"}\n',
                     '{"type":"system","subtype":"init","extra":NaN}\n', "[]\n"):
            with self.subTest(text=text):
                path.write_text(text, encoding="utf-8")
                with self.assertRaises(RuntimeError):
                    observed_interruption(self.prefix)

    def test_unknown_control_metadata_cannot_hide_refusal_retry_billing_or_generated_output(self):
        for extra in ({"error": "billing"}, {"refusal": "policy"}, {"retry_after": 1},
                      {"diagnostics": {"text": "answer"}}, {"output": []},
                      {"api_error_status": 429}, {"rate_limit_info": {"status": "allowed"}}):
            with self.subTest(extra=extra):
                self.write_events([{**self.init, **extra}])
                with self.assertRaises(RuntimeError):
                    observed_interruption(self.prefix)

    def test_wrong_model_identity_retries_prompt_fingerprint_or_source_shape_is_rejected(self):
        bad = [
            {"model": "claude-sonnet"}, {"request_sha256": "not-a-hash"},
            {"prompt_sha256": "b" * 64}, {"prompt": ""}, {"internal_retries": 1},
            {"internal_retries": False}, {"account": {**self.request["account"], "orgName": "Personal"}},
            {"data": {"records": self.request["data"]["records"][:4]}},
            {"data": {"records": [self.request["data"]["records"][0]] * 5}},
            {"extra_retry": True},
        ]
        for change in bad:
            with self.subTest(change=change):
                dump(self.prefix.with_suffix(".request.json"), {**self.request, **change})
                with self.assertRaises(RuntimeError):
                    observed_interruption(self.prefix)

    def test_initialization_requires_recorded_session_working_directory_and_no_tools_or_api_key(self):
        for change in ({"cwd": "relative"}, {"cwd": ""}, {"session_id": None}, {"uuid": "not-uuid"},
                       {"model": "other"}, {"tools": ["Bash"]}, {"mcp_servers": ["server"]},
                       {"apiKeySource": "environment"}, {"permissionMode": "default"},
                       {"agents": {}}, {"skills": [1]}):
            with self.subTest(change=change):
                self.write_events([{**self.init, **change}])
                with self.assertRaises(RuntimeError):
                    observed_interruption(self.prefix)

    def test_review_cannot_falsify_dead_processes_batch_request_or_exact_artifact_inventory(self):
        for change in ({"kind": "other"}, {"batch": "batch_00939"}, {"request_sha256": "b" * 64},
                       {"all_owned_processes_dead": 1}, {"no_orphan_provider_processes": False},
                       {"provider_files_sha256": {}},
                       {"provider_files_sha256": {**self.review["provider_files_sha256"],
                            "provider/batch_00938.raw.json": "a" * 64}},
                       {"provider_files_sha256": {**self.review["provider_files_sha256"],
                            "../outside": "a" * 64}}):
            with self.subTest(change=change):
                dump(self.review_path, {**self.review, **change})
                with self.assertRaises(RuntimeError):
                    self.create()

    def test_review_must_be_the_expected_root_relative_immutable_batch_archive(self):
        for path in (self.root / "arbitrary.json", self.root / "INTERRUPTION_RECOVERIES" / "other" / "REVIEW.json",
                     self.root / "INTERRUPTION_RECOVERIES" / self.batch / "OTHER.json"):
            with self.subTest(path=path):
                dump(path, self.review)
                with self.assertRaises(RuntimeError):
                    create_interruption_defer(self.root, self.batch, path)

    def test_changed_request_review_or_added_artifact_invalidates_existing_marker(self):
        entry = self.create()
        for path, text in ((self.prefix.with_suffix(".request.json"), json.dumps({**self.request, "prompt": "altered"})),
                           (self.review_path, json.dumps({**self.review, "new_note": "changed archive"})),
                           (self.prefix.with_suffix(".raw.json"), "{}")):
            with self.subTest(path=path):
                previous = path.read_bytes() if path.exists() else None
                path.write_text(text, encoding="utf-8")
                with self.assertRaises(RuntimeError):
                    validate_interruption_defer(self.prefix, entry)
                if previous is None:
                    path.unlink()
                else:
                    path.write_bytes(previous)

    def test_marker_safety_types_and_current_source_order_are_exact(self):
        entry = self.create()
        for change in ({"decision": "retry"}, {"no_resubmission": 1}, {"usage_reporting": "zero"},
                       {"zero_cost_claimed": 0}, {"additional_provider_calls": False},
                       {"review_file_sha256": "c" * 64},
                       {"review_file": "INTERRUPTION_RECOVERIES/../REVIEW.json"}):
            with self.subTest(change=change):
                with self.assertRaises(RuntimeError):
                    validate_interruption_defer(self.prefix, {**entry, **change})
        with self.assertRaises(RuntimeError):
            validate_interruption_defer(self.prefix, entry, request_hash="b" * 64)
        with self.assertRaises(RuntimeError):
            validate_interruption_defer(self.prefix, entry, source_ids=list(reversed(self.ids)))

    def test_symlink_artifacts_review_parents_or_marker_directory_are_forbidden(self):
        path = self.prefix.with_suffix(".events.jsonl")
        original = path.read_bytes()
        outside = self.root / "elsewhere.jsonl"
        outside.write_bytes(original)
        path.unlink()
        path.symlink_to(outside)
        with self.assertRaises(RuntimeError):
            observed_interruption(self.prefix)
        path.unlink()
        path.write_bytes(original)
        review_bytes = self.review_path.read_bytes()
        review_target = self.root / "elsewhere-review.json"
        review_target.write_bytes(review_bytes)
        self.review_path.unlink()
        self.review_path.symlink_to(review_target)
        with self.assertRaises(RuntimeError):
            self.create()
        self.review_path.unlink()
        self.review_path.write_bytes(review_bytes)
        target = self.root / "outside-markers"
        target.mkdir()
        (self.root / "DEFERRED_INTERRUPTED_BATCHES").symlink_to(target, target_is_directory=True)
        with self.assertRaises(RuntimeError):
            self.create()
        with self.assertRaises(RuntimeError):
            interrupted_batches(self.root)

    def test_unknown_or_duplicate_json_keys_in_review_and_request_fail_closed(self):
        for path, text in ((self.review_path, '{"kind":"x","kind":"reviewed_dead_worker_interruption"}'),
                           (self.prefix.with_suffix(".request.json"), '{"model":"x","model":"claude-haiku-5-5"}')):
            with self.subTest(path=path):
                original = path.read_bytes()
                path.write_text(text, encoding="utf-8")
                with self.assertRaises(RuntimeError):
                    self.create()
                path.write_bytes(original)

    def test_duplicate_marker_names_and_invalid_unknown_files_fail_closed(self):
        self.create()
        directory = self.root / "DEFERRED_INTERRUPTED_BATCHES"
        (directory / "unrelated.txt").write_text("unknown", encoding="utf-8")
        with self.assertRaises(RuntimeError):
            interrupted_batches(self.root)

    def test_config_validation_binds_actual_preserved_sources_and_full_request_fingerprint(self):
        sources = [{"review_id": key, "question": "A source question?", "original": "The original factual source."}
                   for key in self.ids]
        dump(self.root / "SOURCES.json", sources)
        fake = types.SimpleNamespace(batch_prompt_text=lambda cfg, batch: self.prompt,
            build_request_data=lambda prompt, records: {"records": records},
            fingerprint=lambda cfg, prompt, batch: "a" * 64,
            request_record=lambda row: {"id": row["review_id"], "question": row["question"],
                                        "original_response": row["original"]})
        with mock.patch.dict(sys.modules, {"run_expansion": fake}):
            self.assertEqual(observed_interruption(self.prefix, {"model": "claude-haiku-5-5"})["source_ids"], self.ids)
            sources[0]["original"] = "Changed original source"
            dump(self.root / "SOURCES.json", sources)
            with self.assertRaises(RuntimeError):
                observed_interruption(self.prefix, {"model": "claude-haiku-5-5"})

    def test_create_never_replaces_an_existing_marker_with_a_new_review_archive(self):
        self.create()
        other = self.root / "INTERRUPTION_RECOVERIES" / (self.batch + "_other") / "REVIEW.json"
        dump(other, self.review)
        with self.assertRaises(RuntimeError):
            create_interruption_defer(self.root, self.batch, other)


if __name__ == "__main__":
    unittest.main()
