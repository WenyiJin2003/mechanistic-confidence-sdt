"""Inspect one explicitly reviewed empty extra placeholder without changing text."""
from __future__ import annotations

import copy
import hashlib
import json
import re
from pathlib import Path

ARTIFACT_SUFFIXES = (".request.json", ".raw.json", ".events.jsonl", ".quota.json", ".stderr.txt")
RECORD_FIELDS = {"id", "status", "confident", "hesitant", "reject_reason"}


def _object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise RuntimeError("Duplicate JSON object keys are ambiguous")
        result[key] = value
    return result


def _constant(value):
    raise RuntimeError("Nonfinite JSON numbers are invalid")


def _decode(text):
    try:
        return json.loads(text, object_pairs_hook=_object, parse_constant=_constant)
    except (ValueError, TypeError, RecursionError) as exc:
        raise RuntimeError("Malformed placeholder-recovery JSON evidence") from exc


def _load(path):
    try:
        return _decode(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError) as exc:
        raise RuntimeError("Placeholder-recovery evidence is missing or unreadable") from exc


def _canonical(value):
    try:
        return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    except (TypeError, ValueError, RecursionError) as exc:
        raise RuntimeError("Placeholder evidence contains non-JSON values") from exc


def _payload(raw):
    structured = raw.get("structured_output")
    if structured is not None and not isinstance(structured, dict):
        raise RuntimeError("Structured output must be an object")
    result = raw.get("result")
    decoded = None
    if result is not None and result != "":
        if not isinstance(result, str):
            raise RuntimeError("Result output must be JSON text")
        decoded = _decode(result)
        if not isinstance(decoded, dict):
            raise RuntimeError("Result output must contain an object")
    if structured is not None and decoded is not None and _canonical(structured) != _canonical(decoded):
        raise RuntimeError("Conflicting structured and result output")
    payload = structured if structured is not None else decoded
    if not isinstance(payload, dict) or set(payload) != {"records"}:
        raise RuntimeError("Placeholder recovery requires only a records output object")
    _canonical(payload)
    return payload


def _pins(root, prefix):
    paths = sorted(prefix.parent.glob(prefix.name + ".*"))
    allowed = {prefix.with_suffix(suffix) for suffix in ARTIFACT_SUFFIXES}
    parsed = prefix.with_suffix(".parsed.json")
    if any(path != parsed and (path not in allowed or not path.is_file() or path.is_symlink()) for path in paths):
        raise RuntimeError("Unexpected original placeholder attempt artifact")
    if any(not prefix.with_suffix(suffix).is_file() for suffix in ARTIFACT_SUFFIXES[:3]):
        raise RuntimeError("Original request, raw result, and stream evidence are required")
    return {str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in paths if path in allowed}


def _quota(info):
    if (not isinstance(info, dict) or info.get("status") != "allowed"
            or info.get("isUsingOverage") is not False
            or re.search(r"overage|extra", str(info.get("rateLimitType", "")), re.I)):
        raise RuntimeError("Quota must explicitly allow included usage without overage")


def _stream(prefix, raw, payload, model):
    try:
        lines = prefix.with_suffix(".events.jsonl").read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise RuntimeError("Original stream evidence is unreadable") from exc
    if not lines or any(not line.strip() for line in lines):
        raise RuntimeError("Original stream must contain complete JSON events")
    events = [_decode(line) for line in lines]
    if any(not isinstance(event, dict) for event in events):
        raise RuntimeError("Every original stream event must be an object")
    texts, results, quotas = [], [], []
    for event in events:
        if event.get("error") not in (None, "", False):
            raise RuntimeError("Provider error stream cannot be recovered as a placeholder")
        kind = event.get("type")
        if kind == "system":
            if event.get("subtype") != "init":
                raise RuntimeError("Unknown system event cannot be recovered")
        elif kind == "assistant":
            message = event.get("message")
            if (not isinstance(message, dict) or message.get("model") != model
                    or message.get("stop_reason") not in (None, "end_turn")
                    or not isinstance(message.get("content"), list)):
                raise RuntimeError("Assistant model or completion metadata changed")
            for block in message["content"]:
                if not isinstance(block, dict):
                    raise RuntimeError("Malformed assistant content block")
                if block.get("type") == "thinking":
                    if not isinstance(block.get("thinking"), str) or not set(block) <= {"type", "thinking", "signature"}:
                        raise RuntimeError("Malformed thinking content block")
                elif block.get("type") == "text" and set(block) <= {"type", "text"} and isinstance(block.get("text"), str):
                    texts.append(block["text"])
                else:
                    raise RuntimeError("Unknown assistant content cannot be silently discarded")
        elif kind == "rate_limit_event":
            info = event.get("rate_limit_info")
            _quota(info)
            quotas.append(info)
        elif kind == "result":
            results.append(event)
        else:
            raise RuntimeError("Unknown or retry stream event cannot be recovered")
    if (len(results) != 1 or _canonical(events[-1]) != _canonical(raw)
            or _canonical(results[0]) != _canonical(raw) or len(texts) != 1
            or _canonical(_decode(texts[0])) != _canonical(payload)):
        raise RuntimeError("Assistant text, stream result, and saved raw payload must match")
    quota_path = prefix.with_suffix(".quota.json")
    if quota_path.exists():
        saved = _load(quota_path)
        if not isinstance(saved, dict) or not isinstance(saved.get("events"), list):
            raise RuntimeError("Malformed saved quota evidence")
        for info in saved["events"]:
            _quota(info)
            quotas.append(info)
    if not quotas:
        raise RuntimeError("Included quota permission must be reported for reviewed recovery")
    stderr_path = prefix.with_suffix(".stderr.txt")
    if stderr_path.exists() and stderr_path.read_text(encoding="utf-8").strip():
        raise RuntimeError("Nonempty stderr needs separate review")


def inspect_placeholder_cache(root, batch_name, config):
    """Remove only one exact final empty sentinel in an in-memory response copy."""
    from cache_recovery import strict_records
    from run_expansion import batch_prompt_text, build_request_data, fingerprint, request_record, sha

    root = Path(root)
    if not isinstance(batch_name, str) or not re.fullmatch(r"batch_\d{5}", batch_name):
        raise RuntimeError("Invalid reviewed-placeholder batch name")
    prefix = root / "provider" / batch_name
    pins = _pins(root, prefix)
    request, raw, sources = [_load(path) for path in [prefix.with_suffix(".request.json"),
                                                    prefix.with_suffix(".raw.json"), root / "SOURCES.json"]]
    if (not isinstance(request, dict) or not isinstance(raw, dict) or not isinstance(sources, list)
            or raw.get("subtype") != "success" or raw.get("is_error") is not False
            or raw.get("stop_reason") != "end_turn"):
        raise RuntimeError("Only a successful non-refusal end_turn response can be reviewed")
    supplied = request.get("data", {}).get("records") if isinstance(request.get("data"), dict) else None
    if not isinstance(supplied, list) or len(supplied) != 5 or any(not isinstance(row, dict) for row in supplied):
        raise RuntimeError("Exactly five source records are required")
    expected = [row.get("id") for row in supplied]
    if any(not isinstance(key, str) or not key.strip() for key in expected) or len(set(expected)) != 5:
        raise RuntimeError("Expected source IDs must be five unique nonempty strings")
    if any(not isinstance(row, dict) or not isinstance(row.get("review_id"), str) for row in sources):
        raise RuntimeError("Malformed frozen source pool")
    by_id = {row["review_id"]: row for row in sources}
    if len(by_id) != len(sources) or any(key not in by_id for key in expected):
        raise RuntimeError("Unknown or duplicate frozen source IDs")
    selected = [by_id[key] for key in expected]
    prompt = batch_prompt_text(config, batch_name)
    if (request.get("model") != config["model"] or request.get("prompt") != prompt
            or request.get("prompt_sha256") != sha(prompt)
            or request["data"] != build_request_data(prompt, [request_record(row) for row in selected])
            or request.get("request_sha256") != fingerprint(config, prompt, selected)):
        raise RuntimeError("Original source, model, prompt, request data, or fingerprint changed")
    payload = _payload(raw)
    records = payload["records"]
    if (not isinstance(records, list) or len(records) != 6
            or any(not isinstance(row, dict) for row in records)
            or [row.get("id") for row in records[:5]] != expected
            or any(set(row) != RECORD_FIELDS or row.get("status") != "ok" for row in records[:5])):
        raise RuntimeError("Five complete expected records must precede exactly one extra placeholder")
    placeholder = {"id": expected[-1] + "_PLACEHOLDER_REMOVED", "status": "ok",
                   "confident": "", "hesitant": "", "reject_reason": None}
    if _canonical(records[-1]) != _canonical(placeholder):
        raise RuntimeError("Only the exact final empty placeholder may be removed")
    _stream(prefix, raw, payload, config["model"])
    normalized = copy.deepcopy(raw)
    retained_payload = {"records": copy.deepcopy(records[:5])}
    if normalized.get("structured_output") is not None:
        normalized["structured_output"] = retained_payload
    else:
        normalized.pop("structured_output", None)
    if normalized.get("result"):
        normalized["result"] = json.dumps(retained_payload, ensure_ascii=False)
    retained = strict_records(normalized, expected, config["model"])
    if _pins(root, prefix) != pins:
        raise RuntimeError("Original attempt artifacts changed during inspection")
    metadata = {"normalization": "reviewed_empty_placeholder_only", "discarded_index": 5,
                "discarded_id": placeholder["id"],
                "discarded_payload_sha256": hashlib.sha256(_canonical(placeholder).encode("utf-8")).hexdigest(),
                "returned_ids": [row["id"] for row in records],
                "cached_text_changed": False, "additional_provider_calls": 0}
    return {"batch": batch_name, "request_sha256": request["request_sha256"],
            "expected_ids": expected, "cached_ids": expected, "cached_records": retained,
            "missing_ids": [], "original_file_sha256": pins,
            "reviewed_empty_placeholder_normalization": metadata}
