"""Append unchanged-screen UltraChat sources and rewrite only untouched batches.

User-authorized included-quota campaign. A strictly validated successful partial
response may receive one missing-ID-only completion. Other failures stop work;
never repeats cached text or enables usage credits. Dollars remain estimates.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
import time
import urllib.error
from math import ceil
from pathlib import Path
from datetime import datetime

from launch_expansion import alive, pending_batches, worker
from run_expansion import BASE, dump, file_sha, load, sha, stamp, state
from subscription_preflight import capture_subscription_preflight, ensure_subscription_preflight
from cost_accounting import cost_accounting, unreviewed_cost_count

CONTINUABLE = {"prepared_source_pool_exhausted", "prepared_sources_processed_with_rejections",
               "incremental_estimate_safety_cap", "target_generated", "cache_recovery_complete",
               "included_quota_preflight_verified", "reviewed_refusal_excluded", "reviewed_transport_deferred",
               "reviewed_interruption_deferred"}


def inspect_interruption_processes(root, batch, owner_pid):
    """Fail closed on live workers or orphaned model streams; never kill one."""
    from interruption_defer import observed_interruption
    observed_interruption(root / "provider" / batch)
    init = json.loads((root / "provider" / (batch + ".events.jsonl")).read_text())
    table = subprocess.run(["ps", "-axo", "pid=,ppid=,command="], capture_output=True,
                           text=True, check=True).stdout
    rows = {}
    for line in table.splitlines():
        parts = line.strip().split(None, 2)
        if len(parts) == 3 and parts[0].isdigit() and parts[1].isdigit():
            rows[int(parts[0])] = (int(parts[1]), parts[2])
    ignored, current = {os.getpid()}, os.getpid()
    while current in rows and rows[current][0] not in ignored:
        current = rows[current][0]
        ignored.add(current)
    scripts = {str((BASE / "src" / name).resolve())
               for name in ("run_campaign.py", "run_expansion.py")}
    if alive(owner_pid):
        raise RuntimeError("Recorded campaign owner is still alive")
    for pid, (parent, command) in rows.items():
        if pid in ignored:
            continue
        try:
            words = shlex.split(command)
        except ValueError:
            words = command.split()
        # ps renders argv without shell quoting: these workspace paths contain spaces.
        own_worker = (any(word in scripts for word in words)
                      or any(re.search(r"(?:^|\s)" + re.escape(script) + r"(?=\s|$)", command)
                             for script in scripts))
        provider = ("--print" in words and "stream-json" in words
                    and any("claude" in word.lower() for word in words[:2]))
        own_stream = provider and (init["cwd"] in command or init["session_id"] in command)
        if own_worker or own_stream or parent == owner_pid:
            raise RuntimeError("A matching worker or orphaned provider process is alive")
    return {"all_owned_processes_dead": True, "no_orphan_provider_processes": True,
            "recorded_pids": [owner_pid], "checked_at_utc": stamp()}


def _exclusive_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(fd, "w") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.flush()
        os.fsync(stream.fileno())


def _dead_interruption_evidence(root, batch, owner):
    result = inspect_interruption_processes(root, batch, owner)
    if (not isinstance(result, dict) or any(result.get(key) is not True for key in
            ("all_owned_processes_dead", "no_orphan_provider_processes"))):
        raise RuntimeError("Dead-worker proof failed")
    return result


def prepare_interruption_resume(root, config, batch_name):
    """Archive proven stale ownership and defer an init-only attempt, never retry it."""
    from interruption_defer import observed_interruption, create_interruption_defer
    from subscription_preflight import validate_subscription_preflight
    policy = config.get("campaign", {}).get("interruption_recovery", {})
    if (not config.get("campaign", {}).get("enabled") or not re.fullmatch(r"batch_\d{5}", batch_name)
            or any(policy.get(key) is not True for key in
                   ("enabled", "user_authorized", "init_only_no_resubmission"))):
        raise RuntimeError("Init-only interruption recovery requires explicit standing authorization")
    archive = root / "INTERRUPTION_RECOVERIES" / batch_name
    if archive.exists():
        raise RuntimeError("Existing interruption archive needs reconciliation, not another invocation")
    names = ("CAMPAIGN_JOB.json", "JOB.json", "CAMPAIGN_LAUNCH.json", "LAUNCH.json",
             "RUN_STATUS.json", "CAMPAIGN_STATUS.json", "CAMPAIGN_LOCK.json", "WORKER_LOCK.json")
    try:
        if any((root / name).is_symlink() for name in names):
            raise RuntimeError("Lifecycle evidence must not be symbolic links")
        originals = {name: (root / name).read_bytes() for name in names}
        records = {name: json.loads(value) for name, value in originals.items()}
    except (OSError, ValueError) as exc:
        raise RuntimeError("Missing or invalid stopped lifecycle evidence") from exc
    jobs = {name: records[name] for name in ("CAMPAIGN_JOB.json", "JOB.json")}
    owner = jobs["CAMPAIGN_JOB.json"].get("pid")
    locks = ("CAMPAIGN_LOCK.json", "WORKER_LOCK.json")
    if (type(owner) is not int or owner <= 0
            or any(job.get("state") != "running" or job.get("pid") != owner for job in jobs.values())
            or records["CAMPAIGN_LAUNCH.json"].get("pid") != owner
            or any(records[name].get("pid") != owner for name in locks)):
        raise RuntimeError("Stale lifecycle ownership is inconsistent")
    try:
        for lock, job in zip(locks, jobs.values()):
            lock_time = datetime.fromisoformat(records[lock]["started_at_utc"])
            job_time = datetime.fromisoformat(job["started_at_utc"])
            if lock_time.tzinfo is None or job_time.tzinfo is None or abs((lock_time - job_time).total_seconds()) > 1:
                raise RuntimeError("Stale lock does not match the recorded job start")
        launch_time = datetime.fromisoformat(records["CAMPAIGN_LAUNCH.json"]["launched_at_utc"])
        if (launch_time.tzinfo is None
                or launch_time > datetime.fromisoformat(jobs["CAMPAIGN_JOB.json"]["started_at_utc"])):
            raise RuntimeError("Campaign launch is newer than its recorded worker")
    except (ValueError, KeyError, TypeError) as exc:
        raise RuntimeError("Lifecycle timestamp evidence is invalid") from exc
    current, prior = records["RUN_STATUS.json"], records["CAMPAIGN_STATUS.json"]
    if (current.get("state") not in {"preflight", "running"}
            or prior.get("campaign_state") != "generating"
            or prior.get("state") not in {"preflight", "running", "generating", "prepared_source_pool_exhausted"}):
        raise RuntimeError("Interruption continuation cannot bypass another terminal failure")
    log_path = root / "CAMPAIGN.log"
    log_bytes = log_path.read_bytes()
    last = log_bytes.decode("utf-8", errors="strict").rstrip().splitlines()[-1:]
    if last != ["KeyboardInterrupt: Read-only stop requested; do not submit further provider calls"]:
        raise RuntimeError("No exact signal-interruption evidence at the stopped log tail")
    observed = observed_interruption(root / "provider" / batch_name, config)
    requests = sorted((root / "provider").glob("batch_*.request.json"))
    if not requests or requests[-1].stem != batch_name + ".request":
        raise RuntimeError("Interrupted batch is not the latest attempted request")
    if alive(owner):
        raise RuntimeError("Recorded owner is still alive")
    process_evidence = _dead_interruption_evidence(root, batch_name, owner)
    if unreviewed_cost_count(root, config, current) != 1:
        raise RuntimeError("Only this one validated interrupted attempt may have unreviewed usage")
    preserve_baseline(root, config)
    provider_pins = {str(p.relative_to(root)): file_sha(p)
                     for p in sorted(root.glob("provider*/*")) if p.is_file()}
    # Account verification must succeed before locks, states, or deferrals change.
    evidence = capture_subscription_preflight(config, root)
    verified = validate_subscription_preflight(evidence, config)
    if (any((root / name).read_bytes() != value for name, value in originals.items())
            or log_path.read_bytes() != log_bytes
            or {str(p.relative_to(root)): file_sha(p) for p in sorted(root.glob("provider*/*"))
                if p.is_file()} != provider_pins):
        raise RuntimeError("Stopped campaign changed during interruption review")
    _dead_interruption_evidence(root, batch_name, owner)
    archive.mkdir(parents=True, exist_ok=False)
    (archive / "original").mkdir()
    for name, value in originals.items():
        target = archive / "original" / name
        with target.open("xb") as stream:
            stream.write(value)
    with (archive / "CAMPAIGN.log").open("xb") as stream:
        stream.write(log_bytes)
    review = {"kind": "reviewed_dead_worker_interruption", **observed, **process_evidence,
              "provider_files_sha256": provider_pins, "reviewed_at_utc": stamp(),
              "original_files_sha256": {name: file_sha(archive / "original" / name) for name in names},
              "interruption_log_sha256": file_sha(archive / "CAMPAIGN.log"),
              "usage_reporting": "unreported", "zero_cost_claimed": False,
              "extra_usage_activated": False, "no_interrupted_content_resubmitted": True}
    review_path = archive / "REVIEW.json"
    _exclusive_json(review_path, review)
    entry = create_interruption_defer(root, batch_name, review_path)
    pending = pending_batches(root, config)
    ledger = cost_accounting(root, config)
    if unreviewed_cost_count(root, config, current) != 0:
        raise RuntimeError("Other unreviewed attempts prevent interruption continuation")
    # Recheck ownership and exact lock bytes immediately before recoverable moves.
    _dead_interruption_evidence(root, batch_name, owner)
    if any((root / name).read_bytes() != originals[name] for name in names):
        raise RuntimeError("Lifecycle changed before stale-lock archive")
    release_dir = archive / "released_locks"
    release_dir.mkdir()
    moved = []
    try:
        for name in locks:
            target = release_dir / name
            if target.exists():
                raise RuntimeError("Archived lock already exists")
            (root / name).rename(target)
            moved.append(name)
    except Exception:
        for name in reversed(moved):
            if not (root / name).exists():
                (release_dir / name).rename(root / name)
        raise
    event = {"at_utc": stamp(), "reason": "Reviewed dead-worker interruption; skip its sources without retry",
        "deferred_interruption_entry": entry,
        "deferred_interruption_file": str((root / "DEFERRED_INTERRUPTED_BATCHES" / (batch_name + ".json")).relative_to(root)),
        "deferred_interruption_sha256": file_sha(root / "DEFERRED_INTERRUPTED_BATCHES" / (batch_name + ".json")),
        "previous_jobs": jobs, "previous_status": current, "previous_campaign_status": prior,
        "previous_launch": records["CAMPAIGN_LAUNCH.json"], "preserved_provider_file_sha256": provider_pins,
        "review_file": str(review_path.relative_to(root)), "review_sha256": file_sha(review_path),
        "archived_locks": [str((release_dir / name).relative_to(root)) for name in locks],
        "preflight_file": str(evidence.relative_to(root)), "preflight_sha256": file_sha(evidence),
        "subscription_preflight": verified, "pending_batches": pending, "cost_accounting": ledger,
        "no_cached_text_regenerated": True, "no_failed_content_resubmitted": True, "extra_usage_activated": False}
    name = "resume_interruption_" + event["at_utc"].replace(":", "").replace("+", "_") + ".json"
    _exclusive_json(root / "CAMPAIGN_HISTORY" / name, event)
    for job_name, job in jobs.items():
        dump(root / job_name, {**job, "state": "finished", "finished_at_utc": stamp(),
                              "stop_reason": "reviewed_interruption_deferred", "recovery_history": name})
    state(root, config, "reviewed_interruption_deferred", {"batch": batch_name, "history": name})
    dump(root / "CAMPAIGN_STATUS.json", {**load(root / "RUN_STATUS.json"),
         "campaign_state": "stopped", "campaign_detail": "reviewed_interruption_deferred"})
    return name


def prepare_cache_recovery_resume(root, config, manifest_path):
    """Explicitly reviewed cache recovery cannot bypass other terminal failures."""
    from cache_recovery import validate_completed_recovery
    manifest_path = manifest_path.resolve()
    if manifest_path.resolve().parent != (root / "CACHE_RECOVERIES").resolve():
        raise RuntimeError("Recovery manifest must be in the private recovery directory")
    manifest = validate_completed_recovery(root, manifest_path, config)
    campaign_job, tranche_job = load(root / "CAMPAIGN_JOB.json"), load(root / "JOB.json")
    previous_campaign_status = load(root / "CAMPAIGN_STATUS.json")
    current = load(root / "RUN_STATUS.json")
    budget_recovery = manifest.get("recovery_kind") == "completed_local_budget_stream"
    expected_stop = "per_call_estimate_safety_cap" if budget_recovery else "invalid_provider_output_no_retry"
    if budget_recovery:
        from run_expansion import local_estimate_guards_enabled
        if local_estimate_guards_enabled(config):
            raise RuntimeError("Historical local-budget recovery requires explicit user-authorized estimate-guard removal")
        if (tranche_job.get("stop_reason") != expected_stop
                or previous_campaign_status.get("state") != expected_stop):
            raise RuntimeError("Historical local-budget recovery cannot bypass a different stop")
    if any(alive(job.get("pid")) or job.get("state") != "finished" for job in [campaign_job, tranche_job]):
        raise RuntimeError("A worker is active or its stop needs attention")
    if (root / "CAMPAIGN_LOCK.json").exists() or (root / "WORKER_LOCK.json").exists():
        raise RuntimeError("An unresolved lock prevents campaign continuation")
    if (campaign_job.get("stop_reason") != expected_stop
            or current.get("state") != "cache_recovery_complete"
            or current.get("detail", {}).get("batch") != manifest["batch"]
            or previous_campaign_status.get("detail", {}).get("batch") != manifest["batch"]
            or unreviewed_cost_count(root, config, current) != 0):
        raise RuntimeError("Only this completed cache recovery is authorized for continuation")
    preserve_baseline(root, config)
    pending_batches(root, config)
    evidence = capture_subscription_preflight(config, root)
    event = {"at_utc": stamp(), "manifest_file": str(manifest_path.relative_to(root)),
        "manifest_sha256": file_sha(manifest_path), "subscription_preflight": load(evidence),
        "previous_campaign_job": campaign_job, "previous_tranche_job": tranche_job,
        "previous_campaign_status": previous_campaign_status,
        "previous_launch": load(root / "CAMPAIGN_LAUNCH.json"), "current_status": current,
        "preserved_provider_file_sha256": {str(p.relative_to(root)): file_sha(p)
            for p in sorted(root.glob("provider*/*")) if p.is_file()},
        "no_cached_text_regenerated": True, "extra_usage_activated": False}
    name = "resume_cache_" + event["at_utc"].replace(":", "").replace("+", "_") + ".json"
    dump(root / "CAMPAIGN_HISTORY" / name, event)
    return name


def prepare_verified_preflight_resume(root, config, evidence_path):
    """Explicit continuation after a fresh check resolves an earlier read failure."""
    from subscription_preflight import validate_subscription_preflight
    evidence_path = evidence_path.resolve()
    if evidence_path.parent != (root / "SUBSCRIPTION_PREFLIGHT").resolve():
        raise RuntimeError("Quota evidence must be in the private preflight directory")
    evidence = validate_subscription_preflight(evidence_path, config)
    jobs = {name: load(root / name) for name in ["CAMPAIGN_JOB.json", "JOB.json"]}
    prior = load(root / "RUN_STATUS.json")
    if (any(job.get("state") != "finished" or alive(job.get("pid")) for job in jobs.values())
            or any((root / name).exists() for name in ["CAMPAIGN_LOCK.json", "WORKER_LOCK.json"])):
        raise RuntimeError("A live worker or unresolved lock prevents verified continuation")
    if (prior.get("state") != "included_quota_preflight_failed"
            or jobs["CAMPAIGN_JOB.json"].get("stop_reason") != prior["state"]
            or jobs["JOB.json"].get("stop_reason") != prior["state"]
            or unreviewed_cost_count(root, config, prior) != 0):
        raise RuntimeError("Verified-preflight resume cannot bypass other terminal failures")
    if evidence["checked_at_utc"] <= prior["updated_at_utc"]:
        raise RuntimeError("Quota evidence must be newer than the stopped check")
    marker = root / "LAST_SUBSCRIPTION_PREFLIGHT.json"
    if marker.exists():
        latest = load(marker)
        if latest.get("state") != "verified" or latest.get("evidence_sha256") != file_sha(evidence_path):
            raise RuntimeError("The latest quota check must be the verified evidence")
    preserve_baseline(root, config)
    pending = pending_batches(root, config)
    event = {"at_utc": stamp(), "reason": "Fresh included quota verified after read-only usage-check failure",
        "previous_status": prior, "previous_jobs": jobs,
        "previous_campaign_status": load(root / "CAMPAIGN_STATUS.json"),
        "previous_launch": load(root / "CAMPAIGN_LAUNCH.json"),
        "preflight_file": str(evidence_path.relative_to(root)), "preflight_sha256": file_sha(evidence_path),
        "pending_batches": pending, "extra_usage_activated": False, "no_cached_text_regenerated": True,
        "preserved_provider_file_sha256": {str(p.relative_to(root)): file_sha(p)
            for p in sorted(root.glob("provider*/*")) if p.is_file()}}
    name = "resume_preflight_" + event["at_utc"].replace(":", "").replace("+", "_") + ".json"
    dump(root / "CAMPAIGN_HISTORY" / name, event)
    state(root, config, "included_quota_preflight_verified", {"history": name})
    return name


def prepare_refusal_resume(root, config, batch_name):
    """Exclude one explicitly reviewed refused batch; continue unrelated sources."""
    from run_expansion import create_refusal_quarantine
    jobs = {name: load(root / name) for name in ["CAMPAIGN_JOB.json", "JOB.json"]}
    current = load(root / "RUN_STATUS.json")
    prior_campaign = load(root / "CAMPAIGN_STATUS.json")
    if (any(job.get("state") != "finished" or alive(job.get("pid")) for job in jobs.values())
            or any((root / name).exists() for name in ["CAMPAIGN_LOCK.json", "WORKER_LOCK.json"])):
        raise RuntimeError("A live worker or unresolved lock prevents refusal exclusion")
    if (current.get("state") != "provider_policy_refusal"
            or prior_campaign.get("state") != "provider_policy_refusal"
            or any(job.get("stop_reason") != "provider_policy_refusal" for job in jobs.values())
            or not isinstance(current.get("detail"), dict)
            or not isinstance(prior_campaign.get("detail"), dict)
            or current["detail"].get("batch") != batch_name
            or prior_campaign["detail"].get("batch") != batch_name
            or unreviewed_cost_count(root, config, current) != 0):
        raise RuntimeError("Only the explicitly reviewed stopped policy refusal may be excluded")
    preserve_baseline(root, config)
    entry = create_refusal_quarantine(root, batch_name)
    pending = pending_batches(root, config)
    evidence = capture_subscription_preflight(config, root)
    quarantine_path = root / "QUARANTINED_BATCHES" / f"{batch_name}.json"
    event = {"at_utc": stamp(), "reason": "User authorized exclusion of this refused batch, never retrying its content",
        "quarantine": entry, "quarantine_file": str(quarantine_path.relative_to(root)),
        "quarantine_sha256": file_sha(quarantine_path), "previous_jobs": jobs,
        "previous_status": current, "previous_campaign_status": prior_campaign,
        "previous_launch": load(root / "CAMPAIGN_LAUNCH.json"),
        "sources_sha256": file_sha(root / "SOURCES.json"),
        "preflight_file": str(evidence.relative_to(root)), "preflight_sha256": file_sha(evidence),
        "subscription_preflight": load(evidence), "pending_batches": pending,
        "preserved_provider_file_sha256": {str(p.relative_to(root)): file_sha(p)
            for p in sorted(root.glob("provider*/*")) if p.is_file()},
        "no_cached_text_regenerated": True, "no_refused_content_resubmitted": True,
        "no_rephrase_split_model_or_account_fallback": True, "extra_usage_activated": False}
    name = "resume_refusal_" + event["at_utc"].replace(":", "").replace("+", "_") + ".json"
    dump(root / "CAMPAIGN_HISTORY" / name, event)
    state(root, config, "reviewed_refusal_excluded", {"batch": batch_name,
        "quarantine": str(quarantine_path.relative_to(root)), "history": name})
    return name


def prepare_transport_defer_resume(root, config, batch_name):
    """Defer one reviewed idle-stream failure without salvaging or resubmitting it."""
    from transport_defer import create_transport_defer
    from subscription_preflight import validate_subscription_preflight
    jobs = {name: load(root / name) for name in ["CAMPAIGN_JOB.json", "JOB.json"]}
    current = load(root / "RUN_STATUS.json")
    prior_campaign = load(root / "CAMPAIGN_STATUS.json")
    if (any(job.get("state") != "finished" or alive(job.get("pid")) for job in jobs.values())
            or any((root / name).exists() for name in ["CAMPAIGN_LOCK.json", "WORKER_LOCK.json"])):
        raise RuntimeError("A live worker or unresolved lock prevents transport deferral")
    if (current.get("state") != "provider_error" or prior_campaign.get("state") != "provider_error"
            or any(job.get("stop_reason") != "provider_error" for job in jobs.values())
            or not isinstance(current.get("detail"), dict)
            or not isinstance(prior_campaign.get("detail"), dict)
            or current["detail"].get("batch") != batch_name
            or prior_campaign["detail"].get("batch") != batch_name):
        raise RuntimeError("Only this explicitly reviewed stopped transport failure may be deferred")
    preserve_baseline(root, config)
    entry = create_transport_defer(root, batch_name)
    pending = pending_batches(root, config)
    if unreviewed_cost_count(root, config, current) != 0:
        raise RuntimeError("Other unreviewed attempts or costs prevent transport continuation")
    evidence = capture_subscription_preflight(config, root)
    verified = validate_subscription_preflight(evidence, config)
    deferred_path = root / "DEFERRED_TRANSPORT_BATCHES" / f"{batch_name}.json"
    event = {"at_utc": stamp(), "reason": "User-authorized reviewed transport deferral; continue only untouched sources",
        "deferred_transport_entry": entry, "deferred_transport_file": str(deferred_path.relative_to(root)),
        "deferred_transport_sha256": file_sha(deferred_path), "previous_jobs": jobs,
        "previous_status": current, "previous_campaign_status": prior_campaign,
        "previous_launch": load(root / "CAMPAIGN_LAUNCH.json"),
        "sources_sha256": file_sha(root / "SOURCES.json"),
        "preflight_file": str(evidence.relative_to(root)), "preflight_sha256": file_sha(evidence),
        "subscription_preflight": verified, "pending_batches": pending,
        "cost_accounting": cost_accounting(root, config),
        "preserved_provider_file_sha256": {str(p.relative_to(root)): file_sha(p)
            for p in sorted(root.glob("provider*/*")) if p.is_file()},
        "no_cached_text_regenerated": True, "no_failed_content_resubmitted": True,
        "no_refused_content_resubmitted": True, "extra_usage_activated": False}
    name = "resume_transport_" + event["at_utc"].replace(":", "").replace("+", "_") + ".json"
    dump(root / "CAMPAIGN_HISTORY" / name, event)
    state(root, config, "reviewed_transport_deferred", {"batch": batch_name,
        "deferred_transport": str(deferred_path.relative_to(root)), "history": name})
    return name


def next_source_count(source_count, pending_rows, generated_count, target, chunk_size, batch_size):
    if min(source_count, pending_rows, generated_count) < 0 or min(target, chunk_size, batch_size) <= 0:
        raise ValueError("Invalid campaign counts")
    needed = min(chunk_size, max(0, target - generated_count))
    addition = max(0, needed - pending_rows)
    return source_count + ceil(addition / batch_size) * batch_size


def campaign_source_count(source_count, pending_rows, generated_count, config):
    """Optionally consume eligible cached sources before another source request."""
    planned = next_source_count(source_count, pending_rows, generated_count, config["target_sources"],
        config["campaign"]["source_chunk_size"], config["batch_size"])
    if (config["campaign"].get("consume_prepared_sources_first") is True
            and pending_rows >= config["batch_size"]):
        return source_count
    return planned


def prefix_sha(sources):
    return sha(json.dumps(sources, sort_keys=True, ensure_ascii=False, separators=(",", ":")))


def preserve_baseline(root, config):
    path = root / "CAMPAIGN_BASELINE.json"
    sources = load(root / "SOURCES.json")
    if path.exists():
        baseline = load(path)
        snapshot = root / baseline["source_snapshot_file"]
        if not snapshot.is_file() or file_sha(snapshot) != baseline["source_snapshot_file_sha256"]:
            raise RuntimeError("Recoverable original source snapshot changed")
        if prefix_sha(sources[:baseline["source_count"]]) != baseline["source_prefix_sha256"]:
            raise RuntimeError("Original source prefix changed")
        for name, value in baseline["preserved_file_sha256"].items():
            target = root / name
            if not target.is_file() or file_sha(target) != value:
                raise RuntimeError("An original provider/protocol artifact changed")
        for name, value in baseline["preserved_canary_file_sha256"].items():
            target = BASE / name
            if not target.is_file() or file_sha(target) != value:
                raise RuntimeError("An original canary artifact changed")
        return baseline
    snapshot = root / "CAMPAIGN_BASELINE_SOURCES.json"
    if snapshot.exists() and load(snapshot) != sources:
        raise RuntimeError("Original source snapshot already exists with different records")
    if not snapshot.exists():
        dump(snapshot, sources)
    pins = sorted(root.glob("provider*/*")) + sorted(root.glob("REWRITE_PROTOCOL_*.json"))
    baseline = {"created_at_utc": stamp(), "source_count": len(sources),
        "source_prefix_sha256": prefix_sha(sources), "source_file_sha256": file_sha(root / "SOURCES.json"),
        "source_snapshot_file": snapshot.name, "source_snapshot_file_sha256": file_sha(snapshot),
        "previous_status": load(root / "RUN_STATUS.json"), "previous_config": config,
        "preserved_file_sha256": {str(p.relative_to(root)): file_sha(p) for p in pins if p.is_file()},
        "preserved_canary_file_sha256": {str(p.relative_to(BASE)): file_sha(p)
            for p in sorted((BASE / config["canary_private_dir"]).rglob("*.json"))}
            if config.get("canary_private_dir") else {},
        "original_texts_regenerated": False, "provider_attempts_retried": False}
    dump(path, baseline)
    return baseline


def campaign_status(root, config, phase, detail=None):
    current = load(root / "RUN_STATUS.json")
    result = {**current, "campaign_updated_at_utc": stamp(), "campaign_state": phase,
              "campaign_detail": detail, "campaign_pid": os.getpid(),
              "target_triplets": config["target_sources"], "source_splits": ["train_sft", "train_gen"],
              "extra_usage_activated": False, "automatic_provider_retry": False,
              "new_pairs_human_certified": False}
    dump(root / "CAMPAIGN_STATUS.json", result)
    return result


def maybe_complete_partial(root, config):
    """One new request for absent IDs only, never a retry of a saved attempt."""
    policy = config.get("campaign", {}).get("missing_id_completion", {})
    current = load(root / "RUN_STATUS.json")
    if (policy.get("enabled") is not True or type(policy.get("max_additional_calls_per_batch")) is not int
            or policy.get("max_additional_calls_per_batch") != 1
            or current.get("state") != "invalid_provider_output_no_retry"):
        return False
    try:
        if unreviewed_cost_count(root, config, current) != 0:
            return False
    except (RuntimeError, ValueError, KeyError, TypeError, OSError):
        return False
    from cache_recovery import complete_missing, inspect_cached_batch
    detail = current.get("detail")
    batch = detail.get("batch") if isinstance(detail, dict) else None
    try:
        observed = inspect_cached_batch(root, batch, config)
        if not observed["cached_ids"] or not observed["missing_ids"]:
            return False
    except (RuntimeError, ValueError, KeyError, TypeError, OSError):
        # Malformed, ambiguous, unknown-ID or non-success output needs review.
        return False
    campaign_status(root, config, "completing_missing_ids", {
        "batch": batch, "cached_ids_preserved": observed["cached_ids"], "only_missing_ids": observed["missing_ids"]})
    try:
        manifest = complete_missing(root, batch, config, campaign_owned=True)
        state(root, config, "cache_recovery_complete", {"batch": batch, "manifest": str(manifest.relative_to(root))})
        return True
    except (RuntimeError, ValueError, KeyError, TypeError, OSError, subprocess.SubprocessError) as exc:
        final = load(root / "RUN_STATUS.json")
        if final.get("state") in {"invalid_provider_output_no_retry", "preflight", "running", "bounded_completion_complete"}:
            state(root, config, "missing_id_completion_requires_attention", {
                "batch": batch, "error_type": type(exc).__name__, "error": str(exc)[:300]})
        return False


def run(config, root):
    from prepare_bulk_sources import prepare_bulk
    lock = root / "CAMPAIGN_LOCK.json"
    fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(fd, "w") as stream:
        json.dump({"pid": os.getpid(), "started_at_utc": stamp()}, stream)
    job = root / "CAMPAIGN_JOB.json"
    dump(job, {"pid": os.getpid(), "state": "running", "started_at_utc": stamp(), "target_triplets": config["target_sources"]})
    try:
        # An already-running tranche owns its source snapshot and worker lock.
        while (root / "WORKER_LOCK.json").exists():
            old = load(root / "JOB.json")
            if not alive(old.get("pid")):
                raise RuntimeError("Stale worker lock needs attention; no automatic restart")
            campaign_status(root, config, "waiting_for_existing_worker")
            time.sleep(5)
        prior_job, prior_status = load(root / "JOB.json"), load(root / "RUN_STATUS.json")
        if prior_job.get("state") != "finished" or prior_status["state"] not in CONTINUABLE:
            raise RuntimeError("Previous worker needs review; this campaign cannot bypass its stop reason")
        preserve_baseline(root, config)
        while True:
            current = load(root / "RUN_STATUS.json")
            if current["total_generated_triplets"] >= config["target_sources"]:
                campaign_status(root, config, "target_generated")
                break
            if current["state"] not in CONTINUABLE:
                campaign_status(root, config, "stopped", current["state"])
                break
            if unreviewed_cost_count(root, config, current) != 0:
                raise RuntimeError("Unresolved provider attempt or cost requires review")
            campaign_status(root, config, "checking_included_quota")
            evidence = ensure_subscription_preflight(config, root)
            preserve_baseline(root, config)
            pending = pending_batches(root, config)
            sources = load(root / "SOURCES.json")
            requested = campaign_source_count(len(sources), len(pending) * config["batch_size"],
                current["total_generated_triplets"], config)
            summary = None
            if requested > len(sources):
                campaign_status(root, config, "screening_sources", {"previous_sources": len(sources), "requested_sources": requested})
                summary = prepare_bulk(config, freeze_count=requested)
                preserve_baseline(root, config)
                pending = pending_batches(root, config)
            if not pending:
                state(root, config, "eligible_training_source_pool_exhausted", summary)
                campaign_status(root, config, "stopped", "eligible_training_source_pool_exhausted")
                break
            # Source capture can take time; verify quota again immediately before inference.
            evidence = ensure_subscription_preflight(config, root)
            prior_config = config
            config = dict(config)
            config["max_incremental_cli_estimate_usd"] = ceil(
                (current["conservative_cli_estimate_reserved_usd"] + len(pending) * config["max_call_budget_usd"]) * 100) / 100
            config["subscription_only_continuation"] = {
                "scope": "ultrachat_training_splits_toward_10000", "preflight_file": str(evidence.relative_to(root)),
                "preflight_sha256": file_sha(evidence), "prepared_sources_sha256": file_sha(root / "SOURCES.json"),
                "pending_batches": pending, "this_is_not_payment_authorization": True}
            event = {"at_utc": stamp(), "previous_config": prior_config, "next_config": config,
                "sources_count": len(load(root / "SOURCES.json")), "sources_sha256": file_sha(root / "SOURCES.json"),
                "pending_batches": pending, "source_summary": summary, "no_failed_attempt_retry": True}
            name = "stage_" + event["at_utc"].replace(":", "").replace("+", "_") + ".json"
            dump(root / "CAMPAIGN_HISTORY" / name, event)
            dump(BASE / "configs/expansion_10000_v1.json", config)
            campaign_status(root, config, "generating", {"pending_batches": len(pending)})
            worker(config, root)
            preserve_baseline(root, config)
            maybe_complete_partial(root, config)
            final = load(root / "RUN_STATUS.json")
            if final["state"] not in CONTINUABLE:
                campaign_status(root, config, "stopped", final["state"])
                break
    except KeyboardInterrupt:
        state(root, config, "campaign_interrupted", "No further provider calls authorized after interruption")
        campaign_status(root, config, "stopped", "campaign_interrupted")
    except urllib.error.HTTPError as exc:
        reason = "huggingface_download_throttled" if exc.code == 429 else "source_http_error"
        state(root, config, reason, {"http_status": exc.code, "provider_retry": False})
        campaign_status(root, config, "stopped", reason)
    except Exception as exc:
        # No provider resubmission, account fallback, or credits activation follows errors.
        state(root, config, "campaign_requires_attention", {"error_type": type(exc).__name__, "error": str(exc)[:300]})
        campaign_status(root, config, "stopped", "campaign_requires_attention")
    finally:
        final = load(root / "CAMPAIGN_STATUS.json") if (root / "CAMPAIGN_STATUS.json").exists() else {}
        try:
            review = subprocess.run([sys.executable, str(BASE / "src/build_expansion_review.py")], cwd=BASE.parents[1], check=False)
            dump(job, {"pid": os.getpid(), "state": "finished", "finished_at_utc": stamp(),
                "stop_reason": final.get("campaign_detail") or final.get("campaign_state"),
                "review_build_exit_code": review.returncode,
                "total_generated_triplets": load(root / "RUN_STATUS.json")["total_generated_triplets"]})
        finally:
            if lock.exists() and load(lock).get("pid") == os.getpid():
                lock.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("--resume-cache-recovery", type=Path)
    parser.add_argument("--resume-verified-preflight", type=Path)
    parser.add_argument("--resume-refusal", help="Explicitly reviewed refused batch to exclude without retry")
    parser.add_argument("--resume-transport-defer", help="Explicitly reviewed idle-stream failure to defer without retry")
    parser.add_argument("--resume-interruption", help="Archive proven dead ownership; defer init-only sources without retry")
    args = parser.parse_args()
    if sum(bool(value) for value in [args.resume_cache_recovery, args.resume_verified_preflight,
                                   args.resume_refusal, args.resume_transport_defer, args.resume_interruption]) > 1:
        parser.error("Choose one reviewed continuation path")
    config = load(BASE / "configs/expansion_10000_v1.json")
    if not config.get("campaign", {}).get("enabled"):
        raise RuntimeError("Campaign continuation has not been authorized in configuration")
    root = BASE / config["private_dir"]
    if args.worker:
        run(config, root)
        return
    prior = root / "CAMPAIGN_JOB.json"
    resume_history = None
    if prior.exists():
        old = load(prior)
        if old.get("state") == "running" and alive(old.get("pid")):
            print(json.dumps({"already_running": True, **old}))
            return
        if args.resume_cache_recovery:
            resume_history = prepare_cache_recovery_resume(root, config, args.resume_cache_recovery)
        elif args.resume_verified_preflight:
            resume_history = prepare_verified_preflight_resume(root, config, args.resume_verified_preflight)
        elif args.resume_refusal:
            resume_history = prepare_refusal_resume(root, config, args.resume_refusal)
        elif args.resume_transport_defer:
            resume_history = prepare_transport_defer_resume(root, config, args.resume_transport_defer)
        elif args.resume_interruption:
            resume_history = prepare_interruption_resume(root, config, args.resume_interruption)
        else:
            raise RuntimeError("A previous campaign stopped; inspect its outcome before any explicit resume")
    elif (args.resume_cache_recovery or args.resume_verified_preflight or args.resume_refusal
          or args.resume_transport_defer or args.resume_interruption):
        raise RuntimeError("No previous campaign is available to resume")
    if (root / "CAMPAIGN_LOCK.json").exists():
        raise RuntimeError("An unresolved campaign lock prevents launching")
    log = root / "CAMPAIGN.log"
    with log.open("ab") as stream:
        process = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "--worker"],
            cwd=BASE.parents[1], stdin=subprocess.DEVNULL, stdout=stream,
            stderr=subprocess.STDOUT, start_new_session=True)
    dump(root / "CAMPAIGN_LAUNCH.json", {"pid": process.pid, "launched_at_utc": stamp(),
        "log": str(log), "target_triplets": config["target_sources"], "extra_usage_allowed": False,
        "resume_history": resume_history})
    print(json.dumps({"pid": process.pid, "launched": True, "log": str(log)}))


if __name__ == "__main__":
    main()
