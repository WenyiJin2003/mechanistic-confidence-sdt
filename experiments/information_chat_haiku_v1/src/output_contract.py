"""Build rewrite request data without changing source records."""

import copy
import json

MARKER = "OUTPUT CONTRACT V3"


def build_request_data(prompt: str, records: list[dict]) -> dict:
    """Keep legacy payloads intact and declare the complete v3 output batch."""
    data = {"records": records}
    if MARKER not in prompt:
        return data

    expected_ids = []
    seen = set()
    for record in records:
        source_id = record.get("id")
        if not isinstance(source_id, str) or not source_id.strip():
            raise ValueError("OUTPUT CONTRACT V3 requires a nonempty string id for every record")
        if source_id in seen:
            raise ValueError(f"OUTPUT CONTRACT V3 requires unique ids; duplicate id: {source_id!r}")
        seen.add(source_id)
        expected_ids.append(source_id)

    data["required_output"] = {
        "record_count": len(records),
        "expected_ids": expected_ids,
    }
    return data


def _unique_json_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise RuntimeError("Duplicate JSON object keys are ambiguous")
        result[key] = value
    return result


def _reject_json_constant(value):
    raise RuntimeError("Nonfinite JSON numbers are invalid")


def _canonical_json(value):
    try:
        return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False)
    except (ValueError, TypeError, RecursionError):
        raise RuntimeError("Output contains non-JSON values") from None


def normalize_identical_duplicates(raw, expected_ids):
    """Collapse only equal repeated record objects in a successful response copy."""
    if (not isinstance(expected_ids, (list, tuple)) or not expected_ids
            or any(not isinstance(key, str) or not key.strip() for key in expected_ids)
            or len(set(expected_ids)) != len(expected_ids)):
        raise RuntimeError("Expected IDs must be nonempty, unique strings")
    if (not isinstance(raw, dict) or raw.get("subtype") != "success"
            or raw.get("is_error") is not False or raw.get("stop_reason") != "end_turn"):
        raise RuntimeError("Only successful end_turn responses can normalize identical duplicates")

    structured = raw.get("structured_output")
    if structured is not None and not isinstance(structured, dict):
        raise RuntimeError("Structured output must be an object")
    result = raw.get("result")
    result_payload = None
    if result is not None and result != "":
        if not isinstance(result, str):
            raise RuntimeError("Result output must be JSON text")
        try:
            result_payload = json.loads(result, object_pairs_hook=_unique_json_object,
                                        parse_constant=_reject_json_constant)
        except (ValueError, TypeError, RecursionError):
            raise RuntimeError("Result output is not valid JSON") from None
        if not isinstance(result_payload, dict):
            raise RuntimeError("Result output must contain an object")
    if (structured is not None and result_payload is not None
            and _canonical_json(structured) != _canonical_json(result_payload)):
        raise RuntimeError("Conflicting structured and result output")
    payload = structured if structured is not None else result_payload
    if not isinstance(payload, dict):
        raise RuntimeError("A JSON output object is required")
    _canonical_json(payload)
    records = payload.get("records")
    if not isinstance(records, list) or not records:
        raise RuntimeError("Output records must be a nonempty list")

    expected = set(expected_ids)
    seen = {}
    retained = []
    duplicate_ids = []
    discarded_indices = []
    returned_ids = []
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise RuntimeError("Each output record must be an object")
        key = record.get("id")
        if not isinstance(key, str) or not key.strip() or key not in expected:
            raise RuntimeError("Output contains an empty or unknown ID")
        returned_ids.append(key)
        canonical_record = _canonical_json(record)
        if key in seen:
            if canonical_record != seen[key]:
                raise RuntimeError("Conflicting duplicate output record")
            if key not in duplicate_ids:
                duplicate_ids.append(key)
            discarded_indices.append(index)
        else:
            seen[key] = canonical_record
            retained.append(record)

    normalized = copy.deepcopy(raw)
    if normalized.get("structured_output") is None:
        normalized.pop("structured_output", None)
    if discarded_indices:
        normalized_payload = copy.deepcopy(payload)
        normalized_payload["records"] = copy.deepcopy(retained)
        if structured is not None:
            normalized["structured_output"] = normalized_payload
        if result_payload is not None:
            normalized["result"] = json.dumps(normalized_payload, ensure_ascii=False)
    metadata = {
        "normalization": "identical_record_duplicates_only",
        "duplicate_ids": duplicate_ids,
        "discarded_indices": discarded_indices,
        "returned_ids": returned_ids,
    }
    return normalized, metadata
