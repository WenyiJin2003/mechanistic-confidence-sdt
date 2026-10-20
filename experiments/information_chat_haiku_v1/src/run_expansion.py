"""Resumable Haiku-only expansion with live quota/overage stop signals.

Uses the existing Claude subscription only. Never activates extra usage,
refreshes a token manually, retries a failed batch, or changes an account.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import selectors
import signal
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

from build_review import audit
from run_haiku import SAFE_ENV, parse_payload
from output_contract import build_request_data, normalize_identical_duplicates
from cost_accounting import cost_accounting, unreviewed_cost_count
from transport_defer import deferred_transport_batches, validate_transport_defer
from interruption_defer import interrupted_batches, validate_interruption_defer

BASE = Path(__file__).resolve().parents[1]


def local_estimate_guards_enabled(config):
    """Remove dollar-estimate caps only for the explicitly authorized subscription policy."""
    if "local_estimate_guard_policy" not in config:
        return True
    policy = config["local_estimate_guard_policy"]
    if not isinstance(policy, dict) or type(policy.get("enabled")) is not bool:
        raise RuntimeError("Local estimate guard policy must explicitly enable or disable the guards")
    if policy["enabled"]:
        return True
    if any(policy.get(key) is not True for key in (
            "included_quota_only", "extra_usage_must_be_disabled", "authorized_by_user")):
        raise RuntimeError("Disabling local estimate guards requires explicit included-quota authorization")
    campaign = config.get("campaign")
    stop = config.get("stop_policy")
    if (not isinstance(campaign, dict) or campaign.get("enabled") is not True
            or not isinstance(stop, dict)
            or config.get("expected_org_name") != "Harvard Edu for FAS/SEAS"):
        raise RuntimeError("Disabled local estimate guards require the approved included-quota campaign")
    interval = campaign.get("quota_check_interval_seconds")
    if type(interval) not in (int, float) or not 0 < interval <= 120:
        raise RuntimeError("Included-quota checks must remain fresh at intervals of at most 120 seconds")
    if any(stop.get(key) is not True for key in (
            "stop_on_primary_quota_warning", "stop_on_quota_rejection",
            "stop_on_overage_use", "stop_on_billing_or_credits_prompt")):
        raise RuntimeError("Quota, overage, and billing stops must remain enabled")
    if (stop.get("enable_extra_usage") is not False
            or stop.get("account_or_model_fallback") is not False
            or any(type(stop.get(key)) is not int or stop[key] != 0 for key in (
                "internal_provider_retries", "automatic_batch_retries"))):
        raise RuntimeError("Extra usage, retries, and account or model fallback must remain disabled")
    return False


def provider_command(config, prompt, settings):
    """Build the unchanged inference command, with optional local dollar-estimate caps."""
    command = ["claude", "--print", "--model", config["model"], "--effort", "low", "--system-prompt", prompt,
               "--output-format", "stream-json", "--verbose", "--input-format", "text", "--tools", "", "--disable-slash-commands", "--no-chrome",
               "--no-session-persistence", "--permission-mode", "dontAsk", "--setting-sources", "", "--settings", str(settings),
               "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}']
    if local_estimate_guards_enabled(config):
        command.extend(["--max-budget-usd", str(config["max_call_budget_usd"])])
    return command


def stamp():
    return datetime.now(timezone.utc).isoformat()


def sha(value):
    return hashlib.sha256(value.encode()).hexdigest()


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".pending")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def file_sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_refusal_quarantine(prefix, entry, request_hash=None, source_ids=None):
    """Verify an explicitly reviewed exclusion; never turn a refusal into output."""
    if not re.fullmatch(r"batch_\d{5}", prefix.name) or entry.get("batch") != prefix.name:
        raise RuntimeError("Invalid quarantined batch name")
    request_path = prefix.with_suffix(".request.json")
    raw_path = prefix.with_suffix(".raw.json")
    if not request_path.is_file() or not raw_path.is_file():
        raise RuntimeError("Quarantine requires the original request and refusal evidence")
    if prefix.with_suffix(".parsed.json").exists():
        raise RuntimeError("A refused batch cannot also have parsed output")
    request, raw = load(request_path), load(raw_path)
    if raw.get("is_error") is not True or raw.get("stop_reason") != "refusal":
        raise RuntimeError("Only a verified provider policy refusal may be quarantined")
    ids = [row["id"] for row in request["data"]["records"]]
    if not ids or len(set(ids)) != len(ids):
        raise RuntimeError("Invalid refused source IDs")
    checks = {
        "request_sha256": request["request_sha256"],
        "request_file_sha256": file_sha(request_path),
        "raw_file_sha256": file_sha(raw_path),
        "source_ids": ids,
    }
    if any(entry.get(key) != value for key, value in checks.items()):
        raise RuntimeError("Quarantine evidence changed; manual review is required")
    if request_hash is not None and request_hash != checks["request_sha256"]:
        raise RuntimeError("Current request differs from the quarantined request")
    if source_ids is not None and source_ids != ids:
        raise RuntimeError("Current sources differ from the quarantined sources")
    if entry.get("decision") != "exclude_without_retry":
        raise RuntimeError("Quarantine must explicitly exclude, not retry, the refused sources")
    return entry


def create_refusal_quarantine(root, batch_name):
    """Called only after reviewing a refusal, never automatically by the runner."""
    if not re.fullmatch(r"batch_\d{5}", batch_name):
        raise RuntimeError("Invalid quarantined batch name")
    prefix = root / "provider" / batch_name
    request_path, raw_path = prefix.with_suffix(".request.json"), prefix.with_suffix(".raw.json")
    if not request_path.is_file() or not raw_path.is_file():
        raise RuntimeError("Original request/refusal evidence is missing")
    path = root / "QUARANTINED_BATCHES" / f"{batch_name}.json"
    if path.exists():
        return validate_refusal_quarantine(prefix, load(path))
    request = load(request_path)
    entry = {"batch": batch_name, "request_sha256": request["request_sha256"],
             "request_file_sha256": file_sha(request_path), "raw_file_sha256": file_sha(raw_path),
             "source_ids": [row["id"] for row in request["data"]["records"]],
             "decision": "exclude_without_retry", "created_at_utc": stamp(),
             "reason": "Reviewed batch-level policy refusal; trigger cannot be assigned to an individual source.",
             "no_rephrase_split_model_or_account_fallback": True}
    validate_refusal_quarantine(prefix, entry)
    dump(path, entry)
    return entry


def quarantined_batches(root):
    return [validate_refusal_quarantine(root / "provider" / path.stem, load(path))
            for path in sorted((root / "QUARANTINED_BATCHES").glob("batch_*.json"))]


def stop_signal(event):
    """Only provider metadata/errors, never arbitrary quoted source text."""
    if event.get("type") == "rate_limit_event":
        info = event.get("rate_limit_info", {})
        if info.get("isUsingOverage") or info.get("is_using_overage") or info.get("rateLimitType", info.get("rate_limit_type")) == "overage":
            return "overage_use_reported"
        state = info.get("status")
        if state == "rejected":
            return "account_quota_rejected"
        if state == "allowed_warning":
            return "account_quota_warning"
        # overageStatus=rejected alone does not exhaust an allowed subscription.
    if event.get("type") == "system" and event.get("subtype") == "api_retry":
        return "provider_retry_requested_no_retry_permitted"
    if event.get("type") == "result" and event.get("is_error"):
        if event.get("stop_reason") == "refusal":
            return "provider_policy_refusal"
        error = " ".join(str(event.get(k, "")) for k in ["result", "errors", "subtype", "api_error_status", "terminal_reason"])
        if re.search(r"max.?budget", error, re.I):
            return "per_call_estimate_safety_cap"
        if re.search(r"429|rate.?limit|quota|usage limit|resets?\b", error, re.I):
            return "account_quota_or_rate_limit"
        if re.search(r"billing|credit|payment|overage|account.on.hold|balance|extra usage", error, re.I):
            return "billing_or_credits_required"
        return "provider_error"
    return None


def fingerprint(config, prompt, batch):
    records = [request_record(r) for r in batch]
    payload = {"model": config["model"], "effort": "low", "max_output_tokens": config["max_output_tokens"],
               "prompt": prompt, "batch": records}
    data = build_request_data(prompt, records)
    if "required_output" in data:
        payload["required_output"] = data["required_output"]
    return sha(json.dumps(payload, sort_keys=True, ensure_ascii=False))


def batch_prompt_text(config, batch_name):
    """Version only untouched batches; historic request fingerprints stay valid."""
    if not re.fullmatch(r"batch_\d{5}", batch_name):
        raise RuntimeError("Invalid batch name for prompt selection")
    path = config.get("prompt_overrides", {}).get(batch_name)
    if path is None:
        number = int(batch_name.removeprefix("batch_"))
        path = (config["legacy_prompt_file"] if number <= config.get("legacy_prompt_boundary", 0)
                else config["prompt_file"])
    return (BASE / path).read_text()


def request_record(row):
    record = {"id": row["review_id"], "question": row["question"], "original_response": row["original"]}
    if "previous_versions" in row:
        record.update(previous_confident=row["previous_versions"]["confident"], previous_hesitant=row["previous_versions"]["hesitant"])
    return record


def parse_generation_response(result, ids, config):
    """Validate all required records; optionally collapse exact repeated objects."""
    envelope = result
    normalization = None
    policy = config.get("campaign", {}).get("identical_duplicate_normalization", {})
    if policy.get("enabled") is True:
        envelope, metadata = normalize_identical_duplicates(result, ids)
        if metadata["duplicate_ids"]:
            normalization = metadata
    records = parse_payload(envelope, ids, config["model"])
    for record in records:
        if record.get("status") not in {"ok", "reject"}:
            raise RuntimeError("Invalid writer status")
        if record["status"] == "ok":
            if not all(isinstance(record.get(k), str) and record[k].strip() for k in ["confident", "hesitant"]):
                raise RuntimeError("Rewrite text must be nonempty strings")
            if record.get("reject_reason") is not None:
                raise RuntimeError("Successful rewrite must not have a rejection reason")
        elif (any(k not in record or record[k] is not None for k in ["confident", "hesitant"])
              or not isinstance(record.get("reject_reason"), str) or not record["reject_reason"].strip()):
            raise RuntimeError("Rejected source requires null texts and a nonempty rejection reason")
    return records, normalization


def provider_stream(command, env, cwd, request_text, prefix, timeout):
    process = subprocess.Popen(command, cwd=cwd, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, start_new_session=True)
    process.stdin.write(request_text.encode())
    process.stdin.close()
    selector = selectors.DefaultSelector()
    selector.register(process.stdout, selectors.EVENT_READ, "out")
    selector.register(process.stderr, selectors.EVENT_READ, "err")
    pending = b""
    stderr = bytearray()
    result = None
    reason = None
    terminate_at = None
    quota_events = []
    deadline = time.monotonic() + timeout
    event_path = prefix.with_suffix(".events.jsonl")
    try:
        with event_path.open("ab") as saved:
            while selector.get_map():
                if time.monotonic() > deadline and reason is None:
                    reason = "provider_timeout"
                if reason and process.poll() is None:
                    if terminate_at is None:
                        terminate_at = time.monotonic()
                        os.killpg(process.pid, signal.SIGTERM)
                for key, _ in selector.select(timeout=1):
                    chunk = os.read(key.fileobj.fileno(), 65536)
                    if not chunk:
                        selector.unregister(key.fileobj)
                        continue
                    if key.data == "err":
                        stderr.extend(chunk)
                        if re.search(rb"(?:billing[ _-]?error|payment required|insufficient (?:credits|balance)|usage credits required|extra usage|out.of.credits|account.on.hold|(?:buy|purchase|add|top.?up)[^\n]{0,35}credits)", stderr, re.I):
                            reason = reason or "billing_or_credits_required"
                        continue
                    pending += chunk
                    while b"\n" in pending:
                        line, pending = pending.split(b"\n", 1)
                        if not line.strip():
                            continue
                        saved.write(line + b"\n")
                        saved.flush()
                        try:
                            event = json.loads(line)
                        except json.JSONDecodeError:
                            reason = reason or "invalid_provider_stream"
                            continue
                        reason = reason or stop_signal(event)
                        if event.get("type") == "rate_limit_event":
                            quota_events.append(event.get("rate_limit_info", {}))
                        if event.get("type") == "result":
                            result = event
                if terminate_at is not None and process.poll() is None and time.monotonic() > terminate_at + 5:
                    os.killpg(process.pid, signal.SIGKILL)
            if pending.strip():
                saved.write(pending + b"\n")
                try:
                    event = json.loads(pending)
                    reason = reason or stop_signal(event)
                    if event.get("type") == "result":
                        result = event
                except json.JSONDecodeError:
                    reason = reason or "invalid_provider_stream"
        exit_code = process.wait(timeout=5)
    finally:
        selector.close()
        if process.poll() is None:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()
    if stderr:
        prefix.with_suffix(".stderr.txt").write_bytes(stderr)
        if not result and re.search(rb"billing|credit|payment|overage|account.on.hold|balance|extra usage", stderr, re.I):
            reason = "billing_or_credits_required"
        elif not result and re.search(rb"429|rate.?limit|quota|usage limit", stderr, re.I):
            reason = "account_quota_or_rate_limit"
    dump(prefix.with_suffix(".quota.json"), {"events": quota_events, "quota_reporting": "reported" if quota_events else "unreported", "no_event_does_not_prove_free_usage": True})
    if result is not None:
        dump(prefix.with_suffix(".raw.json"), result)
    if not result and reason is None:
        reason = "missing_provider_result"
    elif result and result.get("subtype") != "success" and reason is None:
        reason = "provider_unsuccessful_result"
    return result, reason, exit_code


def state(root, config, reason, detail=None):
    estimate_guards_enabled = local_estimate_guards_enabled(config)
    sources = load(root / "SOURCES.json")
    reused = [r for r in sources if r.get("reuse_canary")]
    current_records = {}
    paths = sorted((root / "provider").glob("*.parsed.json")) + sorted(root.glob("provider_repairs*/*.parsed.json"))
    for p in paths:
        for r in load(p)["records"]:
            current_records[r["id"]] = r
    generated = [k for k, r in current_records.items() if r["status"] == "ok"]
    rejected = [k for k, r in current_records.items() if r["status"] != "ok"]
    flags = [k for k, r in current_records.items() if any(r.get("audit_flags", {}).values())]
    simple_flags = [key for key, row in current_records.items()
                    if any(any(flag != "content_preservation_review_required" for flag in values)
                           for values in row.get("audit_flags", {}).values())]
    content_review_flags = [key for key, row in current_records.items() if row.get("content_review_notes")]
    exclusions = quarantined_batches(root)
    excluded_ids = [source_id for entry in exclusions for source_id in entry["source_ids"]]
    if set(excluded_ids) & set(current_records):
        raise RuntimeError("Quarantined sources must not be counted as generated")
    deferred = deferred_transport_batches(root)
    deferred_ids = [source_id for entry in deferred for source_id in entry["source_ids"]]
    if (set(deferred_ids) & (set(current_records) | set(excluded_ids))
            or len(deferred_ids) != len(set(deferred_ids))):
        raise RuntimeError("Transport-deferred sources must remain separate from generated or policy-excluded records")
    interruptions = interrupted_batches(root)
    interruption_ids = [source_id for entry in interruptions for source_id in entry["source_ids"]]
    if (set(interruption_ids) & (set(current_records) | {row.get("review_id") for row in reused}
                                 | set(excluded_ids) | set(deferred_ids))
            or len(interruption_ids) != len(set(interruption_ids))):
        raise RuntimeError("Interruption-deferred sources must remain separate from all generated or excluded records")
    accounting = cost_accounting(root, config)
    current = {"updated_at_utc": stamp(), "target_triplets": config["target_sources"], "prepared_sources": len(sources),
               "reused_canary_triplets": len(reused), "new_generated_triplets": len(generated), "total_generated_triplets": len(reused) + len(generated),
               "new_rejected_sources": len(rejected), "new_sources_flagged_by_simple_checks": len(simple_flags), "flagged_ids": flags,
               "content_review_flagged_ids": content_review_flags,
               "new_sources_with_assistant_content_review_notes": len(content_review_flags),
               "quarantined_source_count": len(excluded_ids), "quarantined_source_ids": excluded_ids,
               "quarantined_batches": [entry["batch"] for entry in exclusions],
               "transport_deferred_source_count": len(deferred_ids), "transport_deferred_source_ids": deferred_ids,
               "transport_deferred_batches": [entry["batch"] for entry in deferred],
               "interruption_deferred_source_count": len(interruption_ids),
               "interruption_deferred_source_ids": interruption_ids,
               "interruption_deferred_batches": [entry["batch"] for entry in interruptions],
               **accounting,
               "incremental_cli_estimate_safety_cap_usd": config["max_incremental_cli_estimate_usd"],
               "local_estimate_guards_enabled": estimate_guards_enabled,
               "cli_estimate_values_are_not_invoices": True, "is_actual_invoice": False,
               "state": reason, "detail": detail, "human_item_ratings_received": False, "new_pairs_semantically_certified": False,
               "account_quota_remaining": "unknown; local dollar estimate is not account headroom",
               "extra_usage_enabled_by_this_run": False, "automatic_retry": False, "account_fallback": False}
    dump(root / "RUN_STATUS.json", current)
    return current


def main():
    def interrupt(signum, frame):
        raise KeyboardInterrupt("Read-only stop requested; do not submit further provider calls")
    signal.signal(signal.SIGTERM, interrupt)
    signal.signal(signal.SIGINT, interrupt)
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", type=Path, default=BASE / "configs/expansion_10000_v1.json")
    ap.add_argument("--max-batches", type=int)
    ap.add_argument("--repair-plan", type=Path)
    ap.add_argument("--completion-plan", type=Path)
    args = ap.parse_args()
    if args.repair_plan and args.completion_plan:
        ap.error("Choose either repair or reviewed missing-ID completion")
    config = load(args.config)
    estimate_guards_enabled = local_estimate_guards_enabled(config)
    root = BASE / config["private_dir"]
    root.mkdir(parents=True, exist_ok=True)
    plan = load(args.repair_plan or args.completion_plan) if args.repair_plan or args.completion_plan else None
    if args.completion_plan:
        from cache_recovery import validate_completion_plan
        validate_completion_plan(root, plan, config)
    folder = plan.get("provider_dir", "provider_repairs") if plan else "provider"
    if not folder.startswith("provider") or "/" in folder or ".." in folder:
        raise RuntimeError("Invalid provider cache path")
    provider = root / folder
    provider.mkdir(exist_ok=True)
    sources = load(root / "SOURCES.json")
    if len({r["source_id"] for r in sources}) != len(sources) or len({r["review_id"] for r in sources}) != len(sources):
        raise RuntimeError("Duplicate source or review ID")
    prompt = (BASE / config["prompt_file"]).read_text()
    frozen = root / f"REWRITE_PROTOCOL_{config.get('rewrite_protocol_version', 'v1')}.json"
    protocol = {"model": config["model"], "prompt_sha256": sha(prompt), "prompt_overrides": {k: sha((BASE / v).read_text()) for k, v in config.get("prompt_overrides", {}).items()}, "effort": "low", "max_output_tokens": config["max_output_tokens"], "batch_size": config["batch_size"]}
    if "legacy_prompt_boundary" in config:
        protocol.update(legacy_prompt_boundary=config["legacy_prompt_boundary"],
                        legacy_prompt_sha256=sha((BASE / config["legacy_prompt_file"]).read_text()))
    if frozen.exists() and load(frozen) != protocol:
        raise RuntimeError("Rewrite protocol changed; do not mix cached generations")
    dump(frozen, protocol)
    dump(root / "APPROVAL_SCOPE.json", config["canary_approval"])
    env = {k: v for k, v in os.environ.items() if k in SAFE_ENV}
    env.update({"CLAUDE_CODE_DISABLE_AUTO_MEMORY": "1", "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1", "CLAUDE_CODE_ENABLE_PROMPT_SUGGESTION": "false",
                "CLAUDE_CODE_MAX_RETRIES": "0", "MAX_THINKING_TOKENS": "0", "CLAUDE_CODE_MAX_OUTPUT_TOKENS": str(config["max_output_tokens"])})
    fresh = [r for r in sources if not r.get("reuse_canary")]
    if args.completion_plan:
        from cache_recovery import completion_prompt_text
        prompt = completion_prompt_text(plan, config)
        wanted = set(plan["ids"])
        fresh = [row for row in fresh if row["review_id"] in wanted]
        if {row["review_id"] for row in fresh} != wanted:
            raise RuntimeError("Completion names an unknown source")
    elif plan:
        old = {}
        for p in (root / "provider").glob("*.parsed.json"):
            old.update({r["id"]: r for r in load(p)["records"]})
        wanted = set(plan["ids"])
        fresh = [{**r, "previous_versions": old[r["review_id"]]} for r in fresh if r["review_id"] in wanted]
        if {r["review_id"] for r in fresh} != wanted:
            raise RuntimeError("Repair plan names an unknown or ungenerated source")
        prompt += "\nMINIMAL REPAIR PASS: " + json.dumps(plan["corrections"], ensure_ascii=False) + " Return both full versions. Change only the identified errors, preserving every other substantive claim and a clear contrast."
    count = 0
    next_subscription_check = 0.
    if not plan:
        interrupted_batches(root)
    for offset in range(0, len(fresh), config["batch_size"]):
        batch = fresh[offset:offset + config["batch_size"]]
        # Do not submit a partial trailing batch: its future extension must not change fingerprints.
        if len(batch) < config["batch_size"] and not plan:
            break
        prefix = provider / f"batch_{offset // config['batch_size'] + 1:05d}"
        parsed = prefix.with_suffix(".parsed.json")
        request_file = prefix.with_suffix(".request.json")
        batch_prompt = batch_prompt_text(config, prefix.name) if not plan else prompt
        request_hash = fingerprint(config, batch_prompt, batch)
        interrupted = root / "DEFERRED_INTERRUPTED_BATCHES" / f"{prefix.name}.json"
        if not plan and interrupted.exists():
            if ((root / "QUARANTINED_BATCHES" / f"{prefix.name}.json").exists()
                    or (root / "DEFERRED_TRANSPORT_BATCHES" / f"{prefix.name}.json").exists()):
                raise RuntimeError("An interruption cannot also be a policy or transport exclusion")
            validate_interruption_defer(prefix, load(interrupted), request_hash,
                                        [row["review_id"] for row in batch])
            continue
        if parsed.exists():
            if load(parsed)["request_sha256"] != request_hash:
                raise RuntimeError("Cached request differs")
            continue
        quarantine = root / "QUARANTINED_BATCHES" / f"{prefix.name}.json"
        if not plan and quarantine.exists():
            validate_refusal_quarantine(prefix, load(quarantine), request_hash, [r["review_id"] for r in batch])
            continue
        deferred = root / "DEFERRED_TRANSPORT_BATCHES" / f"{prefix.name}.json"
        if not plan and deferred.exists():
            validate_transport_defer(prefix, load(deferred), request_hash, [r["review_id"] for r in batch])
            continue
        status = state(root, config, "preflight")
        if unreviewed_cost_count(root, config, status) != 0:
            print(json.dumps(state(root, config, "unresolved_attempt_or_cost_requires_review")), flush=True)
            return
        if not plan and status["total_generated_triplets"] >= config["target_sources"]:
            print(json.dumps(state(root, config, "target_generated")), flush=True)
            return
        if (estimate_guards_enabled and status["conservative_cli_estimate_reserved_usd"] + config["max_call_budget_usd"]
                > config["max_incremental_cli_estimate_usd"]):
            print(json.dumps(state(root, config, "incremental_estimate_safety_cap", f"This is the local ${config['max_incremental_cli_estimate_usd']:g} estimate safety guard, NOT proof the Harvard quota was reached.")), flush=True)
            return
        if request_file.exists():
            # A failed/incomplete attempt is never silently repeated on resume.
            print(json.dumps(state(root, config, "saved_failed_or_incomplete_attempt_requires_review", prefix.name)), flush=True)
            return
        if args.max_batches is not None and count >= args.max_batches:
            print(json.dumps(state(root, config, "bounded_precheck_complete")), flush=True)
            return
        if config.get("campaign", {}).get("enabled") and time.monotonic() >= next_subscription_check:
            from subscription_preflight import ensure_subscription_preflight
            try:
                ensure_subscription_preflight(config, root)
            except RuntimeError as exc:
                print(json.dumps(state(root, config, "included_quota_preflight_failed", str(exc)[:300])), flush=True)
                return
            next_subscription_check = time.monotonic() + config["campaign"]["quota_check_interval_seconds"]
        with tempfile.TemporaryDirectory(prefix="haiku-expansion-no-tools-") as temp:
            temp = Path(temp)
            settings = temp / "settings.json"
            dump(settings, {"disableAllHooks": True, "hooks": {}, "enabledPlugins": {}, "alwaysThinkingEnabled": False, "promptSuggestionEnabled": False})
            auth = subprocess.run(["claude", "auth", "status", "--json"], cwd=temp, env=env, text=True, capture_output=True, timeout=30)
            identity = json.loads(auth.stdout)
            if auth.returncode or not identity.get("loggedIn") or identity.get("authMethod") != "claude.ai" or identity.get("apiProvider") != "firstParty" or identity.get("subscriptionType") != "enterprise" or identity.get("orgName") != config["expected_org_name"]:
                print(json.dumps(state(root, config, "account_verification_failed_no_fallback")), flush=True)
                return
            data = build_request_data(batch_prompt, [request_record(r) for r in batch])
            dump(request_file, {"request_sha256": request_hash, "started_at_utc": stamp(), "model": config["model"], "prompt_sha256": sha(batch_prompt), "prompt": batch_prompt, "data": data,
                                "account": {k: identity[k] for k in ["authMethod", "apiProvider", "subscriptionType", "orgName"]}, "internal_retries": 0})
            command = provider_command(config, batch_prompt, settings)
            print(json.dumps({"batch": prefix.name, "state": "calling", "ids": [r["review_id"] for r in batch]}), flush=True)
            result, reason, code = provider_stream(command, env, temp, json.dumps(data, ensure_ascii=False), prefix, config["timeout_seconds"])
            if reason or code:
                print(json.dumps(state(root, config, reason or "provider_nonzero_exit", {"batch": prefix.name, "exit_code": code})), flush=True)
                return
            try:
                records, normalization = parse_generation_response(result, [r["review_id"] for r in batch], config)
            except (ValueError, KeyError, TypeError, RuntimeError) as exc:
                print(json.dumps(state(root, config, "invalid_provider_output_no_retry", {"batch": prefix.name, "error": str(exc)[:400]})), flush=True)
                return
            originals = {r["review_id"]: r["original"] for r in batch}
            for r in records:
                r["audit_flags"] = {role: audit(originals[r["id"]], r[role]) if r["status"] == "ok" else ["writer_rejected"] for role in ["confident", "hesitant"]}
                r["human_review_completed"] = False
            parsed_value = {"request_sha256": request_hash, "model": config["model"], "records": records,
                            "cli_cost_estimate_usd": result.get("total_cost_usd"), "model_usage": result.get("modelUsage"), "completed_at_utc": stamp()}
            if normalization is not None:
                parsed_value["output_normalization"] = {**normalization,
                    "raw_file_sha256": file_sha(prefix.with_suffix(".raw.json")),
                    "cached_text_changed": False, "additional_provider_calls": 0}
            dump(parsed, parsed_value)
            count += 1
            current = state(root, config, "running")
            print(json.dumps({k: current[k] for k in ["total_generated_triplets", "new_generated_triplets", "incremental_cli_estimate_usd", "new_sources_flagged_by_simple_checks"]}), flush=True)
    current = state(root, config, "bounded_completion_complete" if args.completion_plan else "bounded_repair_complete" if plan else "prepared_source_pool_exhausted")
    if current["total_generated_triplets"] >= config["target_sources"]:
        current = state(root, config, "target_generated")
    elif len(sources) >= config["target_sources"]:
        current = state(root, config, "prepared_sources_processed_with_rejections")
    print(json.dumps(current), flush=True)


if __name__ == "__main__":
    main()
