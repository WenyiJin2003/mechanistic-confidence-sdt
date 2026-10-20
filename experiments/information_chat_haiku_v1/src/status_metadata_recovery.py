"""Explicitly infer missing writer-schema metadata from complete paired text.

The inferred status is not a confidence, correctness, or human-approval claim.
No source, generated text, echoed contract, or original terminal is rewritten.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
from pathlib import Path

MISSING_STATUS_FIELDS = {"id", "confident", "hesitant", "reject_reason"}


def _validate_control_metadata(event):
    """Inspect provider controls without interpreting quoted answer contents."""
    from budget_stream_recovery import _no_nonterminal_errors
    from transport_defer import _controls
    if not isinstance(event, dict):
        raise RuntimeError("Every provider control event must be an object")
    control = copy.deepcopy(event)
    control.pop("result", None)
    control.pop("structured_output", None)
    message = control.get("message")
    if isinstance(message, dict):
        message.pop("content", None)
    _no_nonterminal_errors(control)
    _controls(control)


def inspect_status_cache(root, batch_name, config):
    """Return complete unchanged pairs with status added only in memory."""
    from cache_recovery import strict_records
    from reviewed_placeholder import _canonical, _decode, _load, _pins, _stream
    from run_expansion import batch_prompt_text, build_request_data, fingerprint, request_record, sha

    root = Path(root)
    if not isinstance(batch_name, str) or not re.fullmatch(r"batch_\d{5}", batch_name):
        raise RuntimeError("Invalid missing-status recovery batch")
    prefix = root / "provider" / batch_name
    pins = _pins(root, prefix)
    request, raw, sources = [_load(path) for path in [prefix.with_suffix(".request.json"),
                                                    prefix.with_suffix(".raw.json"), root / "SOURCES.json"]]
    if (not isinstance(request, dict) or not isinstance(raw, dict) or not isinstance(sources, list)
            or raw.get("subtype") != "success" or raw.get("is_error") is not False
            or raw.get("stop_reason") != "end_turn"):
        raise RuntimeError("Only successful non-refusal end_turn output can infer writer metadata")
    _validate_control_metadata(raw)
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
    model = config["model"]
    prompt = batch_prompt_text(config, batch_name)
    if (request.get("model") != model or request.get("prompt") != prompt
            or request.get("prompt_sha256") != sha(prompt)
            or request["data"] != build_request_data(prompt, [request_record(row) for row in selected])
            or request.get("request_sha256") != fingerprint(config, prompt, selected)):
        raise RuntimeError("Original source, model, prompt, request data, or fingerprint changed")
    usage = raw.get("modelUsage")
    if not isinstance(usage, dict) or set(usage) != {model}:
        raise RuntimeError("Only the sole requested model may supply the cached output")
    structured = raw.get("structured_output")
    if structured is not None and not isinstance(structured, dict):
        raise RuntimeError("Structured output must be an object")
    result = raw.get("result")
    decoded = None
    if result is not None and result != "":
        if not isinstance(result, str):
            raise RuntimeError("Result output must be JSON text")
        decoded = _decode(result)
    if structured is not None and decoded is not None and _canonical(structured) != _canonical(decoded):
        raise RuntimeError("Conflicting structured and result output")
    payload = structured if structured is not None else decoded
    if not isinstance(payload, dict) or set(payload) != {"records", "required_output"}:
        raise RuntimeError("Only records and the exact echoed output contract may be present")
    contract = request["data"].get("required_output")
    if not isinstance(contract, dict) or _canonical(contract) != _canonical({"record_count": 5, "expected_ids": expected}):
        raise RuntimeError("Original request contract must bind all five expected IDs")
    echo = payload["required_output"]
    if _canonical(echo) == _canonical(contract):
        echo_variant = "full_request_echo"
    elif isinstance(echo, dict) and set(echo) == {"record_count"} and type(echo["record_count"]) is int and echo["record_count"] == 5:
        echo_variant = "record_count_only"
    else:
        raise RuntimeError("Only the exact full request echo or integer record-count-only echo is allowed")
    records = payload["records"]
    if (not isinstance(records, list) or len(records) != 5
            or any(not isinstance(row, dict) or set(row) != MISSING_STATUS_FIELDS for row in records)
            or [row.get("id") for row in records] != expected):
        raise RuntimeError("Exactly five ordered records must omit only the status field")
    for row in records:
        if (row["reject_reason"] is not None
                or not all(isinstance(row[role], str) and row[role].strip() for role in ["confident", "hesitant"])):
            raise RuntimeError("Missing status may be inferred only from nonempty paired text and null reject reason")
    try:
        lines = prefix.with_suffix(".events.jsonl").read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise RuntimeError("Original provider control stream is unreadable") from exc
    for line in lines:
        _validate_control_metadata(_decode(line))
    _stream(prefix, raw, payload, model)
    normalized_payload = copy.deepcopy(payload)
    for row in normalized_payload["records"]:
        row["status"] = "ok"
    envelope = copy.deepcopy(raw)
    if envelope.get("structured_output") is not None:
        envelope["structured_output"] = normalized_payload
    else:
        envelope.pop("structured_output", None)
    if envelope.get("result"):
        envelope["result"] = json.dumps(normalized_payload, ensure_ascii=False)
    retained = strict_records(envelope, expected, model)
    if _pins(root, prefix) != pins:
        raise RuntimeError("Original attempt artifacts changed during inspection")
    metadata = {"normalization": "reviewed_missing_status_metadata_only", "added_field": "status",
                "added_value": "ok", "added_field_ids": expected,
                "echo_variant": echo_variant,
                "inference_basis": "nonempty paired texts with null reject_reason",
                "original_payload_semantic_sha256": hashlib.sha256(_canonical(payload).encode("utf-8")).hexdigest(),
                "normalized_payload_semantic_sha256": hashlib.sha256(_canonical(normalized_payload).encode("utf-8")).hexdigest(),
                "writer_schema_metadata_only": True, "confidence_correctness_or_human_approval_claimed": False,
                "raw_terminal_preserved": True, "cached_text_changed": False, "additional_provider_calls": 0}
    return {"batch": batch_name, "request_sha256": request["request_sha256"], "expected_ids": expected,
            "cached_ids": expected, "cached_records": retained, "missing_ids": [],
            "original_file_sha256": pins, "missing_status_metadata_normalization": metadata}
