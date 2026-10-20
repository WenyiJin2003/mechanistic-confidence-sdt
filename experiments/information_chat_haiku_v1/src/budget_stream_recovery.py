"""Inspect complete cached text followed only by the historical local CLI guard.

The original terminal remains an error. No provider request or account operation
is performed, and the CLI estimate is never represented as a paid invoice.
"""
from __future__ import annotations

import copy
import json
import math
import re
from pathlib import Path

LOCAL_GUARD_ERROR = "Reached maximum budget ($0.12)"
HISTORICAL_GUARD_USD = 0.12
RECORD_FIELDS = {"id", "status", "confident", "hesitant", "reject_reason"}


def _no_nonterminal_errors(value):
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "content":
                continue
            if key in {"error", "errors", "error_code", "error_type"} and child not in (None, False, "", [], {}):
                raise RuntimeError("Nonterminal provider error metadata cannot be ignored")
            _no_nonterminal_errors(child)
    elif isinstance(value, list):
        for child in value:
            _no_nonterminal_errors(child)


def inspect_budget_cache(root, batch_name, config):
    """Return five unchanged records from one exact, explicitly reviewed case."""
    from cache_recovery import strict_records
    from reviewed_placeholder import _canonical, _decode, _load, _pins, _quota
    from run_expansion import batch_prompt_text, build_request_data, fingerprint, request_record, sha
    from transport_defer import _controls, _unexpected_output

    root = Path(root)
    if not isinstance(batch_name, str) or not re.fullmatch(r"batch_\d{5}", batch_name):
        raise RuntimeError("Invalid local-budget recovery batch")
    prefix = root / "provider" / batch_name
    pins = _pins(root, prefix)
    request, raw, sources = [_load(path) for path in [prefix.with_suffix(".request.json"),
                                                    prefix.with_suffix(".raw.json"), root / "SOURCES.json"]]
    if not isinstance(request, dict) or not isinstance(raw, dict) or not isinstance(sources, list):
        raise RuntimeError("Original request, result, and source pool must have valid shapes")
    if (raw.get("type") != "result" or raw.get("subtype") != "error_max_budget_usd"
            or raw.get("is_error") is not True or raw.get("stop_reason") != "end_turn"
            or raw.get("errors") != [LOCAL_GUARD_ERROR]
            or raw.get("result") is not None or raw.get("structured_output") is not None):
        raise RuntimeError("Only the exact historical local estimate terminal is recoverable")
    cost = raw.get("total_cost_usd")
    if type(cost) not in (int, float) or not math.isfinite(cost) or cost < HISTORICAL_GUARD_USD:
        raise RuntimeError("Historical local guard estimate is missing or inconsistent")
    model = config["model"]
    usage = raw.get("modelUsage")
    if (not isinstance(usage, dict) or set(usage) != {model} or not isinstance(usage[model], dict)
            or type(usage[model].get("outputTokens")) is not int or usage[model]["outputTokens"] <= 0):
        raise RuntimeError("Positive output usage for the sole requested model is required")
    _controls(raw)
    _unexpected_output(raw)

    supplied = request.get("data", {}).get("records") if isinstance(request.get("data"), dict) else None
    if not isinstance(supplied, list) or len(supplied) != 5 or any(not isinstance(row, dict) for row in supplied):
        raise RuntimeError("Exactly five frozen source records are required")
    expected = [row.get("id") for row in supplied]
    if any(not isinstance(key, str) or not key.strip() for key in expected) or len(set(expected)) != 5:
        raise RuntimeError("Five unique nonempty expected IDs are required")
    if any(not isinstance(row, dict) or not isinstance(row.get("review_id"), str) for row in sources):
        raise RuntimeError("Malformed frozen source pool")
    by_id = {row["review_id"]: row for row in sources}
    if len(by_id) != len(sources) or any(key not in by_id for key in expected):
        raise RuntimeError("Unknown or duplicate frozen source IDs")
    selected = [by_id[key] for key in expected]
    prompt = batch_prompt_text(config, batch_name)
    if (request.get("model") != model or request.get("prompt") != prompt
            or request.get("prompt_sha256") != sha(prompt)
            or request["data"] != build_request_data(prompt, [request_record(row) for row in selected])
            or request.get("request_sha256") != fingerprint(config, prompt, selected)):
        raise RuntimeError("Original source, model, prompt, request data, or fingerprint changed")

    try:
        lines = prefix.with_suffix(".events.jsonl").read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise RuntimeError("Original model stream is unreadable") from exc
    if not lines or any(not line.strip() for line in lines):
        raise RuntimeError("Original stream must contain complete JSON events")
    events = [_decode(line) for line in lines]
    if any(not isinstance(event, dict) for event in events):
        raise RuntimeError("Every stream event must be an object")
    text_blocks, results, quotas = [], [], []
    for event in events:
        _controls(event)
        _unexpected_output(event)
        if event.get("error") not in (None, False, ""):
            raise RuntimeError("A model or transport error occurred before the local terminal")
        kind = event.get("type")
        if kind != "result":
            _no_nonterminal_errors(event)
        if kind == "system":
            if event.get("subtype") != "init":
                raise RuntimeError("Unexpected or retry system event")
        elif kind == "assistant":
            message = event.get("message")
            if (not isinstance(message, dict) or message.get("model") != model
                    or message.get("stop_reason") not in (None, "end_turn")
                    or not isinstance(message.get("content"), list)):
                raise RuntimeError("Unexpected assistant model or stop metadata")
            for block in message["content"]:
                if not isinstance(block, dict):
                    raise RuntimeError("Malformed assistant block")
                if (block.get("type") == "thinking" and isinstance(block.get("thinking"), str)
                        and set(block) <= {"type", "thinking", "signature"}):
                    continue
                if (block.get("type") == "text" and isinstance(block.get("text"), str)
                        and set(block) <= {"type", "text"}):
                    text_blocks.append((block["text"], message.get("stop_reason")))
                else:
                    raise RuntimeError("Unknown or partial assistant content cannot be discarded")
        elif kind == "rate_limit_event":
            info = event.get("rate_limit_info")
            _quota(info)
            quotas.append(info)
        elif kind == "result":
            results.append(event)
        else:
            raise RuntimeError("Unknown or retry stream event cannot be recovered")
    if (len(results) != 1 or _canonical(events[-1]) != _canonical(raw)
            or _canonical(results[0]) != _canonical(raw) or len(text_blocks) != 1):
        raise RuntimeError("One complete text block and the exact final local terminal are required")
    text, assistant_stop_reason = text_blocks[0]
    payload = _decode(text)
    if not isinstance(payload, dict) or set(payload) != {"records"}:
        raise RuntimeError("Cached text must be a complete records JSON object")
    records = payload["records"]
    if (not isinstance(records, list) or len(records) != 5
            or any(not isinstance(row, dict) or set(row) != RECORD_FIELDS or row.get("status") != "ok" for row in records)
            or [row.get("id") for row in records] != expected):
        raise RuntimeError("Cached text must contain all five expected records exactly once in order")
    quota_path = prefix.with_suffix(".quota.json")
    if quota_path.exists():
        saved = _load(quota_path)
        if not isinstance(saved, dict) or not isinstance(saved.get("events"), list):
            raise RuntimeError("Malformed saved quota evidence")
        for info in saved["events"]:
            _quota(info)
            quotas.append(info)
    stderr_path = prefix.with_suffix(".stderr.txt")
    if stderr_path.exists() and stderr_path.read_text(encoding="utf-8").strip():
        raise RuntimeError("Nonempty stderr requires separate review")

    # This copy is only a parser input. It never replaces the saved terminal.
    envelope = copy.deepcopy(raw)
    envelope.update(subtype="success", is_error=False, result=text)
    envelope.pop("structured_output", None)
    envelope.pop("errors", None)
    retained = strict_records(envelope, expected, model)
    if _pins(root, prefix) != pins:
        raise RuntimeError("Original attempt inventory changed during inspection")
    metadata = {"normalization": "reviewed_local_budget_terminal_only",
                "assistant_stop_reason": assistant_stop_reason, "final_stop_reason": raw["stop_reason"],
                "original_terminal_subtype": raw["subtype"], "original_terminal_is_error": raw["is_error"],
                "historical_per_call_estimate_guard_usd": HISTORICAL_GUARD_USD,
                "provider_reported_cli_estimate_usd": cost,
                "quota_reporting": "allowed_no_overage" if quotas else "unreported",
                "raw_terminal_preserved": True, "cached_text_changed": False,
                "additional_provider_calls": 0, "cli_estimate_not_invoice": True}
    return {"batch": batch_name, "request_sha256": request["request_sha256"],
            "expected_ids": expected, "cached_ids": expected, "cached_records": retained, "missing_ids": [],
            "original_file_sha256": pins, "local_budget_terminal_normalization": metadata}
