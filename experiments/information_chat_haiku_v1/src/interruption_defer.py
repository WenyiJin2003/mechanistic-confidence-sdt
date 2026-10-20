"""Pin an init-only interrupted attempt without claiming success or retrying it.

This module makes no provider, account, process-control, or network calls.  A
separate lifecycle controller must review dead workers before creating a marker.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

DECISION = "defer_interrupted_attempt_without_retry"
MODEL = "claude-haiku-5-5"
HASH = re.compile(r"[0-9a-f]{64}")
BATCH = re.compile(r"batch_\d{5}")
INIT_FIELDS = {
    "type", "subtype", "cwd", "session_id", "tools", "mcp_servers", "model",
    "permissionMode", "slash_commands", "apiKeySource", "claude_code_version",
    "output_style", "agents", "skills", "plugins", "uuid", "fast_mode_state",
}


def _object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON object key")
        result[key] = value
    return result


def _json(text):
    def nonfinite(value):
        raise ValueError("Nonfinite JSON constant")
    try:
        return json.loads(text, object_pairs_hook=_object, parse_constant=nonfinite)
    except (ValueError, TypeError) as exc:
        raise RuntimeError("Malformed interruption evidence JSON") from exc


def _load(path):
    try:
        return _json(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError) as exc:
        raise RuntimeError("Missing or unreadable interruption evidence") from exc


def _sha(path):
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        raise RuntimeError("Missing or unreadable interruption artifact") from exc


def _regular_under(root, path, *, directory=False):
    """Reject traversal and symlink components without following outside root."""
    root, path = Path(root), Path(path)
    if not root.is_absolute() or any(part in {".", ".."} for part in root.parts):
        raise RuntimeError("Interruption root must be an absolute canonical path")
    try:
        relative = path.relative_to(root)
    except ValueError as exc:
        raise RuntimeError("Interruption artifact lies outside its root") from exc
    if any(part in {".", ".."} for part in relative.parts):
        raise RuntimeError("Interruption artifact path traversal is forbidden")
    for component in (root, *(root / Path(*relative.parts[:n])
                              for n in range(1, len(relative.parts) + 1))):
        if component.is_symlink():
            raise RuntimeError("Symlink interruption evidence is forbidden")
    if not (path.is_dir() if directory else path.is_file()):
        raise RuntimeError("Interruption evidence must be a regular file or directory")
    return path


def _prefix(prefix):
    prefix = Path(prefix)
    if prefix.parent.name != "provider" or not BATCH.fullmatch(prefix.name):
        raise RuntimeError("Invalid interrupted batch path")
    root = prefix.parent.parent
    _regular_under(root, prefix.parent, directory=True)
    return root, prefix


def _inventory(root, prefix):
    paths = sorted(prefix.parent.glob(prefix.name + ".*"))
    expected = {prefix.with_suffix(suffix) for suffix in (".request.json", ".events.jsonl")}
    if set(paths) != expected:
        raise RuntimeError("Only original request and init-only stream may be deferred")
    return {str(_regular_under(root, path).relative_to(root)): _sha(path) for path in paths}


def _init_only(prefix, requested_model):
    try:
        lines = prefix.with_suffix(".events.jsonl").read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise RuntimeError("Missing or unreadable interruption stream") from exc
    if len(lines) != 1 or not lines[0].strip():
        raise RuntimeError("An interruption must contain exactly one initialization event")
    event = _json(lines[0])
    if (not isinstance(event, dict) or not set(event) <= INIT_FIELDS
            or event.get("type") != "system" or event.get("subtype") != "init"
            or event.get("model") != requested_model
            or not isinstance(event.get("cwd"), str) or not event["cwd"]
            or not Path(event["cwd"]).is_absolute()
            or event.get("apiKeySource") != "none"
            or event.get("permissionMode") != "dontAsk"
            or event.get("tools") != [] or event.get("mcp_servers") != []):
        raise RuntimeError("Unknown or active provider metadata is not an init-only interruption")
    for key in ("session_id", "uuid"):
        try:
            if not isinstance(event.get(key), str) or str(uuid.UUID(event[key])) != event[key]:
                raise ValueError("Invalid UUID")
        except (ValueError, TypeError, AttributeError) as exc:
            raise RuntimeError("Interruption initialization must record its session UUID") from exc
    for key in ("slash_commands", "agents", "skills", "plugins"):
        if key in event and (not isinstance(event[key], list)
                             or any(not isinstance(value, str) for value in event[key])):
            raise RuntimeError("Malformed initialization capability metadata")
    for key in ("claude_code_version", "output_style", "fast_mode_state"):
        if key in event and (not isinstance(event[key], str) or not event[key]):
            raise RuntimeError("Malformed initialization metadata")


def observed_interruption(prefix, config=None):
    """Prove an unchanged request plus one init event, not absence of backend use."""
    root, prefix = _prefix(prefix)
    artifacts = _inventory(root, prefix)
    request = _load(prefix.with_suffix(".request.json"))
    if (not isinstance(request, dict) or request.get("model") != MODEL
            or not set(request) <= {"request_sha256", "started_at_utc", "model", "prompt_sha256",
                                   "prompt", "data", "account", "internal_retries"}):
        raise RuntimeError("Interrupted request must use the approved Haiku model")
    if (not isinstance(request.get("request_sha256"), str)
            or not HASH.fullmatch(request["request_sha256"])
            or not isinstance(request.get("prompt"), str) or not request["prompt"]
            or request.get("prompt_sha256") != hashlib.sha256(request["prompt"].encode()).hexdigest()
            or type(request.get("internal_retries")) is not int or request["internal_retries"] != 0
            or request.get("account") != {"authMethod": "claude.ai", "apiProvider": "firstParty",
                "subscriptionType": "enterprise", "orgName": "Harvard Edu for FAS/SEAS"}):
        raise RuntimeError("Interrupted request fingerprint or included-quota identity is invalid")
    data = request.get("data")
    records = data.get("records") if isinstance(data, dict) else None
    if not isinstance(records, list) or len(records) != 5 or any(not isinstance(row, dict) for row in records):
        raise RuntimeError("Only the original complete five-source request can be deferred")
    ids = [row.get("id") for row in records]
    if any(not isinstance(key, str) or not key.strip() for key in ids) or len(set(ids)) != 5:
        raise RuntimeError("Interrupted request IDs must be five unique nonempty strings")
    for row in records:
        if (not set(row) <= {"id", "question", "original_response", "previous_confident", "previous_hesitant"}
                or any(not isinstance(row.get(key), str) or not row[key].strip()
                       for key in ("question", "original_response"))):
            raise RuntimeError("Malformed interrupted source record")
    _init_only(prefix, request["model"])
    if config is not None:
        # Lazy import: the campaign imports this module while building its planner.
        from run_expansion import batch_prompt_text, build_request_data, fingerprint, request_record
        sources_list = _load(_regular_under(root, root / "SOURCES.json"))
        if not isinstance(sources_list, list) or any(not isinstance(row, dict) for row in sources_list):
            raise RuntimeError("Malformed interruption source inventory")
        keys = [row.get("review_id") for row in sources_list]
        if any(not isinstance(key, str) or not key for key in keys) or len(set(keys)) != len(keys):
            raise RuntimeError("Source inventory IDs are not unique")
        sources = dict(zip(keys, sources_list))
        if any(key not in sources for key in ids):
            raise RuntimeError("Interrupted source IDs are missing from the preserved source pool")
        selected = [sources[key] for key in ids]
        prompt = batch_prompt_text(config, prefix.name)
        if (request["model"] != config["model"] or request["prompt"] != prompt
                or data != build_request_data(prompt, [request_record(row) for row in selected])
                or request["request_sha256"] != fingerprint(config, prompt, selected)):
            raise RuntimeError("Original source, model, prompt, or request fingerprint changed")
    if _inventory(root, prefix) != artifacts:
        raise RuntimeError("Interrupted attempt changed during inspection")
    return {"batch": prefix.name, "request_sha256": request["request_sha256"],
            "source_ids": ids, "artifact_file_sha256": artifacts}


def _review(root, batch, request_hash, artifacts, relative):
    if not isinstance(relative, str):
        raise RuntimeError("An immutable lifecycle review path is required")
    rel = PurePosixPath(relative)
    if (rel.is_absolute() or len(rel.parts) != 3 or rel.parts[0] != "INTERRUPTION_RECOVERIES"
            or not re.fullmatch(re.escape(batch) + r"(?:_[A-Za-z0-9_-]+)?", rel.parts[1])
            or rel.parts[2] != "REVIEW.json" or str(rel) != relative):
        raise RuntimeError("Interruption review must be in its own immutable batch archive")
    path = _regular_under(root, root / Path(*rel.parts))
    review = _load(path)
    if (not isinstance(review, dict) or review.get("kind") != "reviewed_dead_worker_interruption"
            or review.get("batch") != batch or review.get("request_sha256") != request_hash
            or review.get("all_owned_processes_dead") is not True
            or review.get("no_orphan_provider_processes") is not True):
        raise RuntimeError("Dead-worker interruption lifecycle review is invalid")
    pins = review.get("provider_files_sha256")
    if (not isinstance(pins, dict) or any(not isinstance(key, str) or not isinstance(value, str)
            or not HASH.fullmatch(value) for key, value in pins.items())):
        raise RuntimeError("Lifecycle review must preserve original provider artifact hashes")
    for key in pins:
        item = PurePosixPath(key)
        if (item.is_absolute() or len(item.parts) != 2
                or not re.fullmatch(r"provider(?:_[A-Za-z0-9_-]+)?", item.parts[0])
                or any(part in {".", ".."} for part in item.parts) or str(item) != key):
            raise RuntimeError("Invalid lifecycle provider artifact path")
    attempt = {key: value for key, value in pins.items()
               if PurePosixPath(key).parent == PurePosixPath("provider")
               and PurePosixPath(key).name.startswith(batch + ".")}
    if attempt != artifacts:
        raise RuntimeError("Lifecycle review does not pin the exact interrupted attempt inventory")
    return path, _sha(path)


def validate_interruption_defer(prefix, entry, request_hash=None, source_ids=None):
    root, prefix = _prefix(prefix)
    if not isinstance(entry, dict):
        raise RuntimeError("Interrupted-attempt deferral must be an object")
    observed = observed_interruption(prefix)
    if any(entry.get(key) != value for key, value in observed.items()):
        raise RuntimeError("Interrupted attempt or original artifact inventory changed")
    required = {"decision": DECISION, "no_resubmission": True, "usage_reporting": "unreported",
                "zero_cost_claimed": False, "additional_provider_calls": 0}
    if any(type(entry.get(key)) is not type(value) or entry.get(key) != value
           for key, value in required.items()):
        raise RuntimeError("Interrupted-attempt safety decision changed")
    _, review_hash = _review(root, prefix.name, observed["request_sha256"],
                             observed["artifact_file_sha256"], entry.get("review_file"))
    if entry.get("review_file_sha256") != review_hash:
        raise RuntimeError("Interrupted-attempt lifecycle archive changed")
    if request_hash is not None and request_hash != observed["request_sha256"]:
        raise RuntimeError("Current request differs from the interrupted request")
    if source_ids is not None and source_ids != observed["source_ids"]:
        raise RuntimeError("Current sources differ from the interrupted sources")
    return entry


def create_interruption_defer(root, batch, review_file):
    """Create only a reviewed, exclusive deferral marker; never produce answers."""
    root = Path(root)
    _, prefix = _prefix(root / "provider" / batch)
    directory = root / "DEFERRED_INTERRUPTED_BATCHES"
    path = directory / f"{batch}.json"
    if directory.exists():
        _regular_under(root, directory, directory=True)
    review_file = Path(review_file)
    if not review_file.is_absolute():
        review_file = root / review_file
    try:
        relative = str(review_file.relative_to(root))
    except ValueError as exc:
        raise RuntimeError("Lifecycle review lies outside the campaign root") from exc
    if path.exists() or path.is_symlink():
        existing = validate_interruption_defer(prefix, _load(_regular_under(root, path)))
        if existing["review_file"] != relative:
            raise RuntimeError("Existing interrupted-attempt review must not be replaced")
        return existing
    observed = observed_interruption(prefix)
    _, review_hash = _review(root, batch, observed["request_sha256"],
                             observed["artifact_file_sha256"], relative)
    entry = {**observed, "decision": DECISION, "no_resubmission": True,
             "usage_reporting": "unreported", "zero_cost_claimed": False,
             "additional_provider_calls": 0, "review_file": relative,
             "review_file_sha256": review_hash,
             "created_at_utc": datetime.now(timezone.utc).isoformat()}
    validate_interruption_defer(prefix, entry)
    directory.mkdir(exist_ok=True)
    _regular_under(root, directory, directory=True)
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        existing = validate_interruption_defer(prefix, _load(_regular_under(root, path)))
        if existing["review_file"] != relative:
            raise RuntimeError("Existing interrupted-attempt review must not be replaced")
        return existing
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        json.dump(entry, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    return entry


def interrupted_batches(root):
    root = Path(root)
    directory = root / "DEFERRED_INTERRUPTED_BATCHES"
    if not directory.exists() and not directory.is_symlink():
        return []
    _regular_under(root, directory, directory=True)
    entries = []
    for path in sorted(directory.iterdir()):
        if not re.fullmatch(r"batch_\d{5}\.json", path.name):
            raise RuntimeError("Unknown interrupted-attempt manifest file")
        entries.append(validate_interruption_defer(root / "provider" / path.stem,
            _load(_regular_under(root, path))))
    ids = [key for entry in entries for key in entry["source_ids"]]
    if len(set(ids)) != len(ids):
        raise RuntimeError("Interrupted-attempt deferrals overlap source IDs")
    return entries
