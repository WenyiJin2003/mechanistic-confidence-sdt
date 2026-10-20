"""Reviewed partial-output recovery: reuse cached text, request only missing IDs.

Original provider attempts remain immutable. This is an explicit one-off repair,
not an automatic retry policy, and never applies to refusals/quota/billing stops.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

from build_review import audit
from output_contract import normalize_identical_duplicates
from run_expansion import (
    BASE, batch_prompt_text, build_request_data, dump, file_sha, fingerprint,
    load, request_record, sha, stamp, state,
)
from run_haiku import parse_payload


def same_json(left, right):
    """Keep provenance comparisons type-sensitive, including boolean flags."""
    try:
        return json.dumps(left, sort_keys=True, ensure_ascii=False, allow_nan=False) == json.dumps(
            right, sort_keys=True, ensure_ascii=False, allow_nan=False)
    except (TypeError, ValueError):
        return False


def strict_records(raw, ids, model):
    if raw.get("is_error") is not False or raw.get("subtype") != "success" or raw.get("stop_reason") != "end_turn":
        raise RuntimeError("Only a successful, non-refusal cached response can be recovered")
    envelope = dict(raw)
    if envelope.get("structured_output") is None:
        envelope.pop("structured_output", None)
    records = parse_payload(envelope, ids, model)
    for row in records:
        if row.get("status") not in {"ok", "reject"}:
            raise RuntimeError("Invalid cached writer status")
        if row["status"] == "ok":
            if not all(isinstance(row.get(role), str) and row[role].strip() for role in ["confident", "hesitant"]):
                raise RuntimeError("Cached rewrite text must be nonempty strings")
            if row.get("reject_reason") is not None:
                raise RuntimeError("Successful cached rewrite cannot contain a reject reason")
        elif (any(role not in row or row[role] is not None for role in ["confident", "hesitant"])
                or not isinstance(row.get("reject_reason"), str) or not row["reject_reason"].strip()):
            raise RuntimeError("Rejected cached rewrite requires null texts and a nonempty reject reason")
    return records


def inspect_cached_batch(root, batch_name, config, *, allow_identical_duplicates=False,
                         allow_empty_placeholder=False, allow_local_budget_stream=False,
                         allow_missing_status_metadata=False):
    if sum(bool(value) for value in [allow_identical_duplicates, allow_empty_placeholder,
                                   allow_local_budget_stream, allow_missing_status_metadata]) > 1:
        raise RuntimeError("Choose one explicitly reviewed cache normalization")
    if allow_missing_status_metadata:
        from status_metadata_recovery import inspect_status_cache
        return inspect_status_cache(root, batch_name, config)
    if allow_local_budget_stream:
        from budget_stream_recovery import inspect_budget_cache
        return inspect_budget_cache(root, batch_name, config)
    if allow_empty_placeholder:
        from reviewed_placeholder import inspect_placeholder_cache
        return inspect_placeholder_cache(root, batch_name, config)
    if not re.fullmatch(r"batch_\d{5}", batch_name):
        raise RuntimeError("Invalid recovery batch name")
    prefix = root / "provider" / batch_name
    paths = [prefix.with_suffix(suffix) for suffix in [".request.json", ".raw.json", ".events.jsonl"]]
    if not all(path.is_file() for path in paths):
        raise RuntimeError("Original request, raw result, and stream evidence are required")
    request, raw = load(paths[0]), load(paths[1])
    expected = [row["id"] for row in request["data"]["records"]]
    sources = {row["review_id"]: row for row in load(root / "SOURCES.json")}
    if not expected or len(set(expected)) != len(expected) or any(key not in sources for key in expected):
        raise RuntimeError("Invalid original source IDs")
    selected = [sources[key] for key in expected]
    prompt = batch_prompt_text(config, batch_name)
    if (request["model"] != config["model"] or request["prompt"] != prompt
            or request["prompt_sha256"] != sha(prompt)
            or request["data"] != build_request_data(prompt, [request_record(row) for row in selected])
            or request["request_sha256"] != fingerprint(config, prompt, selected)):
        raise RuntimeError("Original source, model, prompt, or fingerprint changed")
    normalization = None
    if allow_identical_duplicates:
        raw, normalization = normalize_identical_duplicates(raw, expected)
        if not isinstance(normalization, dict) or not normalization.get("duplicate_ids"):
            raise RuntimeError("Identical-duplicate recovery requires a duplicated cached record")
    output = raw.get("structured_output") or raw.get("result")
    if isinstance(output, str):
        output = json.loads(output)
    returned = [row["id"] for row in output["records"]]
    if not returned or len(returned) != len(set(returned)) or not set(returned) <= set(expected):
        raise RuntimeError("Ambiguous, duplicate, or unknown returned IDs cannot be repaired by relabeling")
    records = strict_records(raw, returned, config["model"])
    observed = {"batch": batch_name, "request_sha256": request["request_sha256"],
        "expected_ids": expected, "cached_ids": returned, "cached_records": records,
        "missing_ids": [key for key in expected if key not in returned],
        "original_file_sha256": {str(path.relative_to(root)): file_sha(path) for path in paths}}
    if normalization is not None:
        observed["identical_duplicate_normalization"] = normalization
    return observed


def completion_prompt_text(plan, config):
    """Bind new completions to a format-only prompt; keep legacy plans unchanged."""
    original = batch_prompt_text(config, plan["batch"])
    fields = {"completion_prompt_file", "completion_prompt_sha256"}
    present = fields.intersection(plan)
    if not present:
        return original
    if present != fields or not isinstance(plan["completion_prompt_file"], str):
        raise RuntimeError("Incomplete completion prompt binding")
    prompt = (BASE / plan["completion_prompt_file"]).read_text()
    if sha(prompt) != plan["completion_prompt_sha256"]:
        raise RuntimeError("Bound completion prompt changed")
    if prompt != original:
        marker = "Return exactly"
        if (marker not in original or marker not in prompt
                or original.split(marker, 1)[0] != prompt.split(marker, 1)[0]):
            raise RuntimeError("Completion prompt must preserve the original semantic instructions")
    return prompt


def validate_completion_plan(root, plan, config):
    if ("cache_only" in plan and plan["cache_only"] is not True
            or "cache_only_artifact_file_sha256" in plan and plan.get("cache_only") is not True):
        raise RuntimeError("Invalid cache-only recovery binding")
    kind = plan.get("recovery_kind")
    if kind not in {None, "identical_duplicate_records", "reviewed_empty_placeholder", "completed_local_budget_stream",
                    "reviewed_missing_status_metadata"}:
        raise RuntimeError("Unknown cached-output recovery kind")
    allow_duplicates = kind == "identical_duplicate_records"
    allow_placeholder = kind == "reviewed_empty_placeholder"
    allow_budget = kind == "completed_local_budget_stream"
    allow_status = kind == "reviewed_missing_status_metadata"
    observed = inspect_cached_batch(root, plan["batch"], config,
        allow_identical_duplicates=allow_duplicates, allow_empty_placeholder=allow_placeholder,
        allow_local_budget_stream=allow_budget, allow_missing_status_metadata=allow_status)
    for key in ["request_sha256", "expected_ids", "cached_ids", "cached_records", "original_file_sha256"]:
        if plan.get(key) != observed[key]:
            raise RuntimeError("Partial-cache recovery evidence changed")
    if (plan.get("identical_duplicate_normalization") != observed.get("identical_duplicate_normalization")
            or (allow_duplicates and "identical_duplicate_normalization" not in plan)):
        raise RuntimeError("Identical-duplicate recovery evidence changed")
    if (not same_json(plan.get("reviewed_empty_placeholder_normalization"), observed.get("reviewed_empty_placeholder_normalization"))
            or (allow_placeholder and "reviewed_empty_placeholder_normalization" not in plan)):
        raise RuntimeError("Reviewed empty-placeholder recovery evidence changed")
    if (not same_json(plan.get("local_budget_terminal_normalization"), observed.get("local_budget_terminal_normalization"))
            or (allow_budget and ("local_budget_terminal_normalization" not in plan or plan.get("cache_only") is not True))):
        raise RuntimeError("Completed local-budget stream recovery evidence changed")
    if (not same_json(plan.get("missing_status_metadata_normalization"), observed.get("missing_status_metadata_normalization"))
            or (allow_status and ("missing_status_metadata_normalization" not in plan or plan.get("cache_only") is not True))):
        raise RuntimeError("Missing-status metadata recovery evidence changed")
    if plan.get("ids") != observed["missing_ids"] or plan.get("provider_dir") != "provider_completions_" + observed["batch"]:
        raise RuntimeError("Completion must contain only genuinely missing source IDs")
    completion_prompt_text(plan, config)
    for name, value in plan["preserved_provider_file_sha256"].items():
        if not (root / name).is_file() or file_sha(root / name) != value:
            raise RuntimeError("A previously saved provider artifact changed")
    if plan.get("cache_only") is True:
        pins = cache_only_artifacts(root, plan, observed, config)
        if not same_json(plan.get("cache_only_artifact_file_sha256"), pins):
            raise RuntimeError("Cache-only original attempt inventory changed")
    return observed


def cache_only_artifacts(root, plan, observed, config):
    """Require all requested rows and a consistent successful stream, offline."""
    from reviewed_placeholder import _load, _payload, _pins, _stream
    if (plan.get("ids") != [] or observed["missing_ids"] != []
            or observed["cached_ids"] != observed["expected_ids"]):
        raise RuntimeError("Cache-only recovery requires every expected record; generation is forbidden")
    if plan.get("recovery_kind") in {"completed_local_budget_stream", "reviewed_missing_status_metadata"}:
        # Each specialized inspector verifies its own exact original stream and
        # payload shape; the saved terminal, texts and echoed metadata stay intact.
        return observed["original_file_sha256"]
    prefix = root / "provider" / plan["batch"]
    pins = _pins(root, prefix)
    raw = _load(prefix.with_suffix(".raw.json"))
    _stream(prefix, raw, _payload(raw), config["model"])
    if _pins(root, prefix) != pins:
        raise RuntimeError("Cache-only attempt artifacts changed during inspection")
    return pins


def prepare_recovery(root, batch_name, config, *, allow_identical_duplicates=False,
                     allow_empty_placeholder=False, allow_local_budget_stream=False,
                     allow_missing_status_metadata=False):
    observed = inspect_cached_batch(root, batch_name, config,
        allow_identical_duplicates=allow_identical_duplicates, allow_empty_placeholder=allow_empty_placeholder,
        allow_local_budget_stream=allow_local_budget_stream,
        allow_missing_status_metadata=allow_missing_status_metadata)
    path = root / "CACHE_RECOVERIES" / f"{batch_name}.plan.json"
    if path.exists():
        validate_completion_plan(root, load(path), config)
        return path
    plan = {**observed, "ids": observed["missing_ids"], "provider_dir": "provider_completions_" + batch_name,
        "completion_prompt_file": config["prompt_file"],
        "completion_prompt_sha256": sha((BASE / config["prompt_file"]).read_text()),
        "created_at_utc": stamp(), "explicit_user_authorization": "Recover cached output; generate only absent records, never existing text",
        "preserved_provider_file_sha256": {str(path.relative_to(root)): file_sha(path)
            for path in sorted(root.glob("provider*/*")) if path.is_file()},
        "before_status": load(root / "RUN_STATUS.json"), "no_cached_record_regeneration": True}
    if allow_identical_duplicates:
        plan["recovery_kind"] = "identical_duplicate_records"
    if allow_empty_placeholder:
        plan["recovery_kind"] = "reviewed_empty_placeholder"
        plan["explicit_user_authorization"] = "Reviewed cache-only removal of one exact empty trailing placeholder; never regenerate or discard answer text"
    if allow_local_budget_stream:
        plan["recovery_kind"] = "completed_local_budget_stream"
        plan["explicit_user_authorization"] = "User disabled local estimate guards; recover only complete cached assistant text after the exact local-budget terminal, never regenerate"
        plan["cache_only"] = True
        plan["cache_only_artifact_file_sha256"] = observed["original_file_sha256"]
    if allow_missing_status_metadata:
        plan["recovery_kind"] = "reviewed_missing_status_metadata"
        plan["explicit_user_authorization"] = "Autonomous lossless cache repair authorized: derive writer output-presence metadata from two complete texts and explicit null reject_reason; not content or human approval"
        plan["cache_only"] = True
        plan["cache_only_artifact_file_sha256"] = observed["original_file_sha256"]
    completion_prompt_text(plan, config)
    dump(path, plan)
    return path


def assembled_records(root, plan, config):
    observed = validate_completion_plan(root, plan, config)
    records = {row["id"]: dict(row) for row in observed["cached_records"]}
    origins = {key: f"provider/{plan['batch']}.raw.json" for key in records}
    pins = dict(observed["original_file_sha256"])
    if plan.get("cache_only") is True:
        pins.update(plan["cache_only_artifact_file_sha256"])
    if observed["missing_ids"]:
        prefix = root / plan["provider_dir"] / "batch_00001"
        paths = [prefix.with_suffix(suffix) for suffix in [".request.json", ".raw.json", ".parsed.json"]]
        if not all(path.is_file() for path in paths):
            raise RuntimeError("Missing records have not been completed; do not invent them")
        request, raw, parsed = [load(path) for path in paths]
        sources = {row["review_id"]: row for row in load(root / "SOURCES.json")}
        selected = [sources[key] for key in observed["missing_ids"]]
        prompt = completion_prompt_text(plan, config)
        expected_hash = fingerprint(config, prompt, selected)
        if (request["data"] != build_request_data(prompt, [request_record(row) for row in selected])
                or request["request_sha256"] != expected_hash or parsed["request_sha256"] != expected_hash
                or request["prompt"] != prompt or request.get("prompt_sha256") != sha(prompt)
                or request["model"] != config["model"] or parsed.get("model") != config["model"]):
            raise RuntimeError("Completion request differs or overlaps existing cached text")
        completed_raw = raw
        if "output_normalization" in parsed:
            completed_raw, metadata = normalize_identical_duplicates(raw, observed["missing_ids"])
            expected_normalization = {**metadata, "raw_file_sha256": file_sha(paths[1]),
                                      "cached_text_changed": False, "additional_provider_calls": 0}
            try:
                normalization_matches = (isinstance(parsed["output_normalization"], dict)
                    and json.dumps(parsed["output_normalization"], sort_keys=True, ensure_ascii=False, allow_nan=False)
                    == json.dumps(expected_normalization, sort_keys=True, ensure_ascii=False, allow_nan=False))
            except (TypeError, ValueError):
                normalization_matches = False
            if not metadata.get("duplicate_ids") or not normalization_matches:
                raise RuntimeError("Completion duplicate-normalization evidence changed")
        completed = strict_records(completed_raw, observed["missing_ids"], config["model"])
        # Parsed diagnostics may add fields; the source texts/status must match raw bytes semantically exactly.
        by_id = {row["id"]: row for row in parsed["records"]}
        if len(by_id) != len(completed) or len(parsed["records"]) != len(completed):
            raise RuntimeError("Completion parsed IDs differ")
        for row in completed:
            if any(by_id[row["id"]].get(key) != value for key, value in row.items()):
                raise RuntimeError("Completion parsed text changed from the raw response")
            records[row["id"]] = dict(row)
            origins[row["id"]] = str(paths[1].relative_to(root))
        pins.update({str(path.relative_to(root)): file_sha(path) for path in paths})
    originals = {row["review_id"]: row["original"] for row in load(root / "SOURCES.json")}
    result = []
    for key in observed["expected_ids"]:
        row = records[key]
        row["audit_flags"] = {role: audit(originals[key], row[role]) if row["status"] == "ok" else ["writer_rejected"]
                              for role in ["confident", "hesitant"]}
        row["human_review_completed"] = False
        row["generation_cache_source"] = origins[key]
        if key in plan.get("content_review_notes", {}):
            row["content_review_notes"] = plan["content_review_notes"][key]
            row["content_review_status"] = "flagged_by_assistant_not_human_certified"
            for role in ["confident", "hesitant"]:
                row["audit_flags"][role].append("content_preservation_review_required")
        result.append(row)
    return result, pins


def finalize_recovery(root, plan_path, config):
    plan = load(plan_path)
    records, pins = assembled_records(root, plan, config)
    duplicate_provenance = recovery_provenance(plan)
    parsed_provenance = ({**duplicate_provenance, "recovered_from_cached_partial_output": bool(plan["ids"])}
                         if duplicate_provenance else {})
    parsed_path = root / "provider" / f"{plan['batch']}.parsed.json"
    if parsed_path.exists():
        saved = load(parsed_path)
        if (saved["records"] != records or saved["request_sha256"] != plan["request_sha256"]
                or saved.get("model") != config["model"]
                or any(not same_json(saved.get(key), value) for key, value in parsed_provenance.items())):
            raise RuntimeError("Refusing to overwrite an existing or changed parsed cache")
    else:
        dump(parsed_path, {"request_sha256": plan["request_sha256"], "model": config["model"],
            "records": records, "completed_at_utc": stamp(), "recovered_from_cached_partial_output": True,
            "cached_ids_reused_verbatim": plan["cached_ids"], "only_missing_ids_submitted": plan["ids"],
            "recovery_plan_file": str(plan_path.relative_to(root)), **parsed_provenance})
    manifest_path = root / "CACHE_RECOVERIES" / f"{plan['batch']}.completed.json"
    if manifest_path.exists():
        validate_completed_recovery(root, manifest_path, config)
        return manifest_path
    dump(manifest_path, {"completed": True, "batch": plan["batch"], "completed_at_utc": stamp(),
        "plan_file": str(plan_path.relative_to(root)), "plan_sha256": file_sha(plan_path),
        "cached_ids": plan["cached_ids"], "completed_missing_ids": plan["ids"],
        "parsed_file": str(parsed_path.relative_to(root)), "parsed_file_sha256": file_sha(parsed_path),
        "evidence_file_sha256": pins, "no_cached_text_regenerated": True,
        "new_pairs_human_certified": False, "is_actual_invoice": False, **duplicate_provenance})
    return manifest_path


def validate_completed_recovery(root, manifest_path, config):
    manifest = load(manifest_path)
    plan_path = root / manifest["plan_file"]
    if manifest.get("completed") is not True or file_sha(plan_path) != manifest["plan_sha256"]:
        raise RuntimeError("Completed recovery manifest changed")
    plan = load(plan_path)
    records, pins = assembled_records(root, plan, config)
    parsed = root / manifest["parsed_file"]
    parsed_data = load(parsed)
    duplicate_provenance = recovery_provenance(plan)
    if (manifest.get("batch") != plan["batch"] or manifest["parsed_file"] != f"provider/{plan['batch']}.parsed.json"
            or parsed_data.get("request_sha256") != plan["request_sha256"] or parsed_data.get("model") != config["model"]
            or manifest["cached_ids"] != plan["cached_ids"] or manifest["completed_missing_ids"] != plan["ids"]
            or manifest["evidence_file_sha256"] != pins or file_sha(parsed) != manifest["parsed_file_sha256"]
            or parsed_data["records"] != records
            or any(not same_json(manifest.get(key), value) or not same_json(parsed_data.get(key), value)
                   for key, value in duplicate_provenance.items())
            or (duplicate_provenance and parsed_data.get("recovered_from_cached_partial_output") != bool(plan["ids"]))):
        raise RuntimeError("Recovered output or provenance changed")
    return manifest


def recovery_provenance(plan):
    """Bind each explicitly reviewed cache normalization to its own evidence."""
    keys = {
        "identical_duplicate_records": "identical_duplicate_normalization",
        "reviewed_empty_placeholder": "reviewed_empty_placeholder_normalization",
        "completed_local_budget_stream": "local_budget_terminal_normalization",
        "reviewed_missing_status_metadata": "missing_status_metadata_normalization",
    }
    field = keys.get(plan.get("recovery_kind"))
    result = {"recovery_kind": plan["recovery_kind"], field: plan[field]} if field else {}
    if plan.get("cache_only") is True:
        result.update(cache_only=True, cache_only_artifact_file_sha256=plan["cache_only_artifact_file_sha256"])
    return result


def _check_recovery_owner(root, campaign_owned):
    from launch_expansion import alive
    current_pid = os.getpid()
    campaign_lock = root / "CAMPAIGN_LOCK.json"
    campaign_job = load(root / "CAMPAIGN_JOB.json")
    tranche_job = load(root / "JOB.json")
    if (root / "WORKER_LOCK.json").exists():
        raise RuntimeError("An unresolved worker lock prevents cache recovery")
    if campaign_owned:
        if (not campaign_lock.is_file() or load(campaign_lock).get("pid") != current_pid
                or campaign_job.get("state") != "running" or campaign_job.get("pid") != current_pid
                or tranche_job.get("state") != "finished"
                or (tranche_job.get("pid") != current_pid and alive(tranche_job.get("pid")))):
            raise RuntimeError("Only the active campaign owner may complete its finished tranche")
    elif (campaign_lock.exists() or any(job.get("state") != "finished" or alive(job.get("pid"))
                                      for job in [campaign_job, tranche_job])):
        raise RuntimeError("A live, unfinished, or locked worker prevents standalone cache recovery")


def complete_missing(root, batch_name, config, content_review_notes=None, campaign_owned=False,
                     allow_identical_duplicates=False, allow_empty_placeholder=False, cache_only=False,
                     allow_local_budget_stream=False, allow_missing_status_metadata=False):
    """Preserve cached rows and make at most one reviewed missing-only attempt."""
    if allow_local_budget_stream and not cache_only:
        raise RuntimeError("Completed local-budget stream recovery must be cache-only")
    if allow_missing_status_metadata and not cache_only:
        raise RuntimeError("Missing-status metadata recovery must be cache-only")
    _check_recovery_owner(root, campaign_owned)
    lock = root / "WORKER_LOCK.json"
    fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(fd, "w") as stream:
        json.dump({"pid": os.getpid(), "role": "reviewed_missing_id_completion"}, stream)
    try:
        plan_path = prepare_recovery(root, batch_name, config,
            allow_identical_duplicates=allow_identical_duplicates, allow_empty_placeholder=allow_empty_placeholder,
            allow_local_budget_stream=allow_local_budget_stream,
            allow_missing_status_metadata=allow_missing_status_metadata)
        plan = load(plan_path)
        if cache_only:
            observed = validate_completion_plan(root, plan, config)
            pins = cache_only_artifacts(root, plan, observed, config)
            if plan.get("cache_only") is not True:
                if ((root / "CACHE_RECOVERIES" / f"{batch_name}.completed.json").exists()
                        or (root / "provider" / f"{batch_name}.parsed.json").exists()):
                    raise RuntimeError("Cannot upgrade an already completed legacy recovery to cache-only")
                plan.update(cache_only=True, cache_only_artifact_file_sha256=pins)
                dump(plan_path, plan)
            validate_completion_plan(root, plan, config)
        if content_review_notes:
            if (root / "CACHE_RECOVERIES" / f"{batch_name}.completed.json").exists():
                raise RuntimeError("Cannot alter a completed recovery manifest")
            for key, note in content_review_notes.items():
                if key not in plan["cached_ids"] or not note.strip():
                    raise RuntimeError("Review note must identify an existing cached record")
                plan.setdefault("content_review_notes", {})[key] = note.strip()
            dump(plan_path, plan)
        parsed = root / plan["provider_dir"] / "batch_00001.parsed.json"
        if plan["ids"] and not parsed.exists():
            prefix = parsed.with_name("batch_00001")
            if any(prefix.with_suffix(suffix).exists() for suffix in [
                    ".request.json", ".raw.json", ".events.jsonl", ".stderr.txt", ".quota.json"]):
                raise RuntimeError("A saved missing-only attempt requires review; never resubmit it")
            from subscription_preflight import capture_subscription_preflight
            capture_subscription_preflight(config, root)
            subprocess.run([sys.executable, str(BASE / "src/run_expansion.py"), "--completion-plan", str(plan_path)], check=True)
        return finalize_recovery(root, plan_path, config)
    finally:
        if lock.exists() and load(lock).get("pid") == os.getpid():
            lock.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch", required=True)
    parser.add_argument("--complete-missing", action="store_true")
    parser.add_argument("--cache-only", action="store_true", help="Require all expected records already cached and a verified successful stream; never inspect an account or invoke generation")
    parser.add_argument("--deduplicate-identical", action="store_true", help="Explicitly recover identical cached duplicate records; conflicting duplicates are never accepted")
    parser.add_argument("--reviewed-empty-placeholder", action="store_true", help="Explicit cache-only removal of one exact empty trailing placeholder after full-ID output; never used by the normal generation parser")
    parser.add_argument("--reviewed-local-budget-stream", action="store_true", help="Explicit recovery of complete assistant text after the exact historical local-budget terminal; requires --cache-only")
    parser.add_argument("--reviewed-missing-status-metadata", action="store_true", help="Explicit lossless writer-status metadata recovery for complete paired cached texts; requires --cache-only")
    parser.add_argument("--content-review-note", action="append", default=[], help="Cached ID: model-assisted review concern; no text rewriting")
    args = parser.parse_args()
    if args.cache_only and not args.complete_missing:
        parser.error("--cache-only requires --complete-missing")
    if args.reviewed_local_budget_stream and args.complete_missing and not args.cache_only:
        parser.error("Local-budget stream recovery requires --cache-only")
    if args.reviewed_missing_status_metadata and args.complete_missing and not args.cache_only:
        parser.error("Missing-status metadata recovery requires --cache-only")
    if sum(bool(value) for value in [args.deduplicate_identical, args.reviewed_empty_placeholder,
                                   args.reviewed_local_budget_stream, args.reviewed_missing_status_metadata]) > 1:
        parser.error("Choose one explicitly reviewed cache normalization")
    config = load(BASE / "configs/expansion_10000_v1.json")
    root = BASE / config["private_dir"]
    if not args.complete_missing:
        result = inspect_cached_batch(root, args.batch, config,
            allow_identical_duplicates=args.deduplicate_identical, allow_empty_placeholder=args.reviewed_empty_placeholder,
            allow_local_budget_stream=args.reviewed_local_budget_stream,
            allow_missing_status_metadata=args.reviewed_missing_status_metadata)
        print(json.dumps({key: result[key] for key in ["batch", "cached_ids", "missing_ids"]}))
        return
    notes = dict(item.split(":", 1) for item in args.content_review_note)
    manifest_path = complete_missing(root, args.batch, config, content_review_notes=notes,
        allow_identical_duplicates=args.deduplicate_identical, allow_empty_placeholder=args.reviewed_empty_placeholder,
        cache_only=args.cache_only, allow_local_budget_stream=args.reviewed_local_budget_stream,
        allow_missing_status_metadata=args.reviewed_missing_status_metadata)
    manifest = load(manifest_path)
    result = state(root, config, "cache_recovery_complete", {"batch": args.batch, "manifest": str(manifest_path.relative_to(root))})
    print(json.dumps({"cached_ids_preserved": manifest["cached_ids"], "only_missing_ids_completed": manifest["completed_missing_ids"],
                      "total_generated_triplets": result["total_generated_triplets"], "manifest": str(manifest_path)}))


if __name__ == "__main__":
    main()
