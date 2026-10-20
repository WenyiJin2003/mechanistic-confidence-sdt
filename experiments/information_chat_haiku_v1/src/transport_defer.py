"""Explicitly defer an empty-output transport failure without resubmitting it."""
from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

IDLE_ERROR = "API Error: Stream idle timeout - partial response received"
DECISION = "defer_transport_failure_without_retry"
SUFFIXES = (".request.json", ".raw.json", ".events.jsonl", ".quota.json", ".stderr.txt")
REQUIRED_SUFFIXES = SUFFIXES[:3]
FORBIDDEN = re.compile(
    r"refusal|usage.?policy|billing|payment|credits?|out.of.credits|extra.usage|"
    r"account.on.hold|quota|rate.?limit|api.?retry|retry.requested|insufficient.balance", re.I)


def _object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON object key")
        result[key] = value
    return result


def _json(text):
    def invalid_constant(value):
        raise ValueError("Nonfinite JSON constant")
    try:
        return json.loads(text, object_pairs_hook=_object, parse_constant=invalid_constant)
    except (ValueError, TypeError) as exc:
        raise RuntimeError("Malformed transport evidence JSON") from exc


def _load(path):
    try:
        return _json(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError) as exc:
        raise RuntimeError("Transport evidence is missing or unreadable") from exc


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _prefix(prefix):
    prefix = Path(prefix)
    if prefix.parent.name != "provider" or not re.fullmatch(r"batch_\d{5}", prefix.name):
        raise RuntimeError("Invalid transport-defer batch path")
    return prefix


def _artifacts(prefix):
    paths = sorted(prefix.parent.glob(prefix.name + ".*"))
    expected = {prefix.with_suffix(suffix) for suffix in SUFFIXES}
    if prefix.with_suffix(".parsed.json").exists():
        raise RuntimeError("A deferred transport failure cannot have parsed output")
    if any(path not in expected or not path.is_file() or path.is_symlink() for path in paths):
        raise RuntimeError("Unknown or nonregular transport attempt artifact")
    if any(not prefix.with_suffix(suffix).is_file() for suffix in REQUIRED_SUFFIXES):
        raise RuntimeError("Original request, raw result, and full stream are required")
    return {str(path.relative_to(prefix.parent.parent)): _sha(path) for path in paths}


def _controls(value):
    """Inspect control metadata, excluding content blocks checked separately."""
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "content":
                continue
            if "retry" in key.lower() and child not in (None, False, 0, "", [], {}):
                raise RuntimeError("A provider retry signal cannot be deferred")
            if key == "rate_limit_info":
                _quota(child)
            if key == "api_error_status" and child is not None:
                raise RuntimeError("A classified API error is outside the narrow idle signature")
            if (re.search(r"refusal|billing|credit", key, re.I)
                    and child not in (None, False, 0, "", [], {})):
                raise RuntimeError("Policy or billing control metadata cannot be deferred")
            if key in {"error", "error_code", "error_type", "result", "stop_reason", "subtype"}:
                if _forbidden_signal(child):
                    raise RuntimeError("Policy, quota, billing, or retry evidence cannot be deferred")
            if key == "type" and isinstance(child, str) and re.search(r"retry|refusal", child, re.I):
                raise RuntimeError("A provider retry event cannot be deferred")
            _controls(child)
    elif isinstance(value, list):
        for child in value:
            _controls(child)


def _forbidden_signal(value):
    if isinstance(value, str):
        return bool(FORBIDDEN.search(value))
    if isinstance(value, dict):
        return any(_forbidden_signal(child) for child in value.values())
    if isinstance(value, list):
        return any(_forbidden_signal(child) for child in value)
    return False


def _unexpected_output(value, path=()):
    if isinstance(value, dict):
        for key, child in value.items():
            if path == ("message",) and key == "content":
                continue
            if (key in {"text", "thinking", "content", "delta", "partial_response", "partial_output", "output", "completion"}
                    and child not in (None, "", [], {})):
                raise RuntimeError("Unclassified nested output cannot prove an empty response")
            _unexpected_output(child, (*path, key))
    elif isinstance(value, list):
        for child in value:
            _unexpected_output(child, path)


def _quota(info):
    if (not isinstance(info, dict) or info.get("status") != "allowed"
            or info.get("isUsingOverage", False) is not False
            or re.search(r"overage|extra", str(info.get("rateLimitType", "")), re.I)):
        raise RuntimeError("Rejected, warning, or overage quota evidence cannot be deferred")


def _check_stream(prefix, raw, requested_model):
    try:
        lines = prefix.with_suffix(".events.jsonl").read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise RuntimeError("Transport stream is missing or unreadable") from exc
    if not lines or any(not line.strip() for line in lines):
        raise RuntimeError("Transport stream must contain complete JSON events")
    events = [_json(line) for line in lines]
    if any(not isinstance(event, dict) for event in events):
        raise RuntimeError("Every transport stream event must be an object")
    results, synthetic_errors = [], 0
    for event in events:
        _controls(event)
        _unexpected_output(event)
        kind = event.get("type")
        if kind == "result":
            results.append(event)
        elif kind == "system":
            if event.get("subtype") != "init":
                raise RuntimeError("Unknown system stream event cannot be deferred")
        elif kind == "rate_limit_event":
            _quota(event.get("rate_limit_info"))
        elif kind == "assistant":
            message = event.get("message")
            if not isinstance(message, dict) or not isinstance(message.get("content"), list):
                raise RuntimeError("Malformed assistant stream content")
            model = message.get("model")
            if model != "<synthetic>" and (not isinstance(model, str) or not model
                    or (requested_model and model != requested_model)):
                raise RuntimeError("Unexpected model metadata in transport stream")
            for block in message["content"]:
                if not isinstance(block, dict):
                    raise RuntimeError("Malformed assistant content block")
                if (block.get("type") == "thinking" and model != "<synthetic>"
                        and block.get("thinking") == ""
                        and set(block) <= {"type", "thinking", "signature"}):
                    continue
                if (block.get("type") == "text" and model == "<synthetic>"
                        and block.get("text") == IDLE_ERROR and set(block) <= {"type", "text"}):
                    synthetic_errors += 1
                    continue
                raise RuntimeError("Generated or unknown assistant content cannot be deferred")
        else:
            raise RuntimeError("Unknown transport stream event cannot be deferred")
    if len(results) != 1 or events[-1] != raw or results[0] != raw or not synthetic_errors:
        raise RuntimeError("Stream must end with the exact saved transport error result")


def _observed(prefix):
    artifacts = _artifacts(prefix)
    request, raw = [_load(prefix.with_suffix(suffix)) for suffix in (".request.json", ".raw.json")]
    if not isinstance(request, dict) or not isinstance(raw, dict):
        raise RuntimeError("Request and result evidence must be objects")
    records = request.get("data", {}).get("records") if isinstance(request.get("data"), dict) else None
    if not isinstance(records, list) or not records or any(not isinstance(row, dict) for row in records):
        raise RuntimeError("Transport request must contain source records")
    ids = [row.get("id") for row in records]
    if any(not isinstance(key, str) or not key.strip() for key in ids) or len(set(ids)) != len(ids):
        raise RuntimeError("Transport request IDs must be nonempty unique strings")
    request_hash = request.get("request_sha256")
    if not isinstance(request_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", request_hash):
        raise RuntimeError("Transport request fingerprint is missing or malformed")
    if (raw.get("is_error") is not True or raw.get("stop_reason") != "stop_sequence"
            or raw.get("result") != IDLE_ERROR
            or type(raw.get("total_cost_usd")) not in (int, float) or raw["total_cost_usd"] != 0):
        raise RuntimeError("Only the exact unreported-cost stream idle failure may be deferred")
    _controls(raw)
    _check_stream(prefix, raw, request.get("model"))
    quota_path = prefix.with_suffix(".quota.json")
    if quota_path.exists():
        quota = _load(quota_path)
        if not isinstance(quota, dict) or not isinstance(quota.get("events"), list):
            raise RuntimeError("Malformed saved quota evidence")
        for info in quota["events"]:
            _quota(info)
    stderr_path = prefix.with_suffix(".stderr.txt")
    if stderr_path.exists():
        try:
            stderr = stderr_path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            raise RuntimeError("Unreadable transport stderr evidence") from exc
        if any(line.strip() and line.strip() != IDLE_ERROR for line in stderr.splitlines()):
            raise RuntimeError("Unclassified stderr cannot prove an empty transport response")
    return {"batch": prefix.name, "request_sha256": request_hash, "source_ids": ids,
            "artifact_file_sha256": artifacts}


def validate_transport_defer(prefix, entry, request_hash=None, source_ids=None):
    """Read and pin all original evidence; never infer success or resubmit it."""
    prefix = _prefix(prefix)
    if not isinstance(entry, dict):
        raise RuntimeError("Transport-defer manifest must be an object")
    observed = _observed(prefix)
    for key, value in observed.items():
        if entry.get(key) != value:
            raise RuntimeError("Deferred transport evidence or file inventory changed")
    required = {"decision": DECISION, "no_cache_salvage": True, "no_resubmission": True,
                "usage_reporting": "unreported", "provider_reported_cost_usd": 0,
                "zero_report_not_invoice": True, "reviewed_narrow_transport_signature": "v1"}
    if any(type(entry.get(key)) is not type(value) or entry.get(key) != value for key, value in required.items()):
        raise RuntimeError("Transport-defer decision or safety metadata changed")
    if request_hash is not None and request_hash != observed["request_sha256"]:
        raise RuntimeError("Current request differs from the deferred request")
    if source_ids is not None and source_ids != observed["source_ids"]:
        raise RuntimeError("Current sources differ from the deferred sources")
    return entry


def create_transport_defer(root, batch_name):
    """Record an explicitly reviewed empty transport failure, without retry."""
    root = Path(root)
    prefix = _prefix(root / "provider" / batch_name)
    path = root / "DEFERRED_TRANSPORT_BATCHES" / f"{batch_name}.json"
    if path.exists():
        return validate_transport_defer(prefix, _load(path))
    entry = {**_observed(prefix), "decision": DECISION, "no_cache_salvage": True,
             "no_resubmission": True, "usage_reporting": "unreported", "provider_reported_cost_usd": 0,
             "zero_report_not_invoice": True, "reviewed_narrow_transport_signature": "v1",
             "created_at_utc": datetime.now(timezone.utc).isoformat()}
    validate_transport_defer(prefix, entry)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        return validate_transport_defer(prefix, _load(path))
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        json.dump(entry, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    return entry


def deferred_transport_batches(root):
    root = Path(root)
    return [validate_transport_defer(root / "provider" / path.stem, _load(path))
            for path in sorted((root / "DEFERRED_TRANSPORT_BATCHES").glob("batch_*.json"))]
