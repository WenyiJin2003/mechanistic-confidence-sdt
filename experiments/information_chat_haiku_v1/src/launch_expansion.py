"""Start one bounded local expansion worker and build its final review snapshot."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from math import ceil
from pathlib import Path

from run_expansion import BASE, batch_prompt_text, dump, file_sha, fingerprint, load, stamp, state, validate_refusal_quarantine
from cost_accounting import unreviewed_cost_count
from transport_defer import validate_transport_defer
from interruption_defer import interrupted_batches, validate_interruption_defer


def alive(pid):
    if not isinstance(pid, int) or pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except (ProcessLookupError, TypeError, ValueError):
        return False


def prepare_resume(root, config):
    """Resume unrelated work only after an exact refused batch was excluded."""
    job, prior = load(root / "JOB.json"), load(root / "RUN_STATUS.json")
    if alive(job.get("pid")) or (root / "WORKER_LOCK.json").exists():
        raise RuntimeError("A live worker or unresolved lock prevents resuming")
    if job.get("state") not in {"finished", "failed"}:
        raise RuntimeError("Previous worker status needs review")
    if prior.get("state") not in {"provider_error", "provider_policy_refusal"}:
        raise RuntimeError("This resume path cannot bypass quota, billing, format, or budget stops")
    detail = prior.get("detail")
    batch = detail.get("batch") if isinstance(detail, dict) else None
    if not batch:
        raise RuntimeError("Stopped batch is not identified")
    entry = validate_refusal_quarantine(root / "provider" / batch,
                                        load(root / "QUARANTINED_BATCHES" / f"{batch}.json"))
    if config["max_incremental_cli_estimate_usd"] != prior["incremental_cli_estimate_safety_cap_usd"]:
        raise RuntimeError("Resume must preserve the cumulative estimate safety cap")
    history = {"created_at_utc": stamp(), "reason": "Continue unrelated sources after reviewed refusal exclusion",
               "quarantine": entry, "previous_job": job, "previous_status": prior,
               "previous_launch": load(root / "LAUNCH.json"),
               "preserved_file_sha256": {str(path.relative_to(root)): file_sha(path)
                   for path in sorted(root.glob("provider*/*")) if path.is_file()},
               "sources_sha256": file_sha(root / "SOURCES.json"),
               "no_completed_batch_retry": True, "no_cap_increase": True, "no_extra_usage_activation": True}
    name = "resume_" + history["created_at_utc"].replace(":", "").replace("+", "_") + ".json"
    dump(root / "RESUME_HISTORY" / name, history)
    return name


def pending_batches(root, config):
    """Validate every completed/skipped request before counting untouched work."""
    sources = load(root / "SOURCES.json")
    # This validates the manifest directory and symlink-free archive references,
    # even when someone has added a parsed file beside an excluded attempt.
    interrupted_batches(root)
    for request in root.glob("provider*/*.request.json"):
        prefix = request.with_name(request.name.removesuffix(".request.json"))
        quarantine = root / "QUARANTINED_BATCHES" / f"{prefix.name}.json"
        deferred = root / "DEFERRED_TRANSPORT_BATCHES" / f"{prefix.name}.json"
        interrupted = root / "DEFERRED_INTERRUPTED_BATCHES" / f"{prefix.name}.json"
        if prefix.parent.name == "provider" and interrupted.exists():
            if quarantine.exists() or deferred.exists():
                raise RuntimeError("An interruption cannot also be a policy or transport exclusion")
            validate_interruption_defer(prefix, load(interrupted))
            continue
        if prefix.with_suffix(".parsed.json").exists():
            continue
        if prefix.parent.name != "provider":
            raise RuntimeError("An unresolved cached attempt requires review, not retry")
        if quarantine.exists() and deferred.exists():
            raise RuntimeError("A batch cannot be both a policy refusal and a transport deferral")
        if quarantine.exists():
            validate_refusal_quarantine(prefix, load(quarantine))
        elif deferred.exists():
            validate_transport_defer(prefix, load(deferred))
        else:
            raise RuntimeError("An unresolved cached attempt requires review, not retry")
    fresh = [row for row in sources if not row.get("reuse_canary")]
    pending = []
    for offset in range(0, len(fresh), config["batch_size"]):
        batch = fresh[offset:offset + config["batch_size"]]
        if len(batch) < config["batch_size"]:
            break
        name = f"batch_{offset // config['batch_size'] + 1:05d}"
        prefix = root / "provider" / name
        request_hash = fingerprint(config, batch_prompt_text(config, name), batch)
        parsed, request = prefix.with_suffix(".parsed.json"), prefix.with_suffix(".request.json")
        interrupted = root / "DEFERRED_INTERRUPTED_BATCHES" / f"{name}.json"
        if interrupted.exists():
            if ((root / "QUARANTINED_BATCHES" / f"{name}.json").exists()
                    or (root / "DEFERRED_TRANSPORT_BATCHES" / f"{name}.json").exists()):
                raise RuntimeError("An interruption cannot also be a policy or transport exclusion")
            validate_interruption_defer(prefix, load(interrupted), request_hash,
                                        [row["review_id"] for row in batch])
            continue
        if parsed.exists():
            if load(parsed)["request_sha256"] != request_hash or not request.exists() or load(request)["request_sha256"] != request_hash:
                raise RuntimeError("Completed request changed; no regeneration permitted")
            continue
        quarantine = root / "QUARANTINED_BATCHES" / f"{name}.json"
        if quarantine.exists():
            validate_refusal_quarantine(prefix, load(quarantine), request_hash, [row["review_id"] for row in batch])
            continue
        deferred = root / "DEFERRED_TRANSPORT_BATCHES" / f"{name}.json"
        if deferred.exists():
            validate_transport_defer(prefix, load(deferred), request_hash, [row["review_id"] for row in batch])
            continue
        if any(prefix.with_suffix(suffix).exists() for suffix in [".request.json", ".raw.json", ".events.jsonl"]):
            raise RuntimeError("An unresolved provider attempt prevents subscription-only continuation")
        pending.append(name)
    return pending


def prepare_included_quota_resume(root, config, evidence_path):
    from subscription_preflight import validate_subscription_preflight
    evidence = validate_subscription_preflight(evidence_path, config)
    job, prior, launch = load(root / "JOB.json"), load(root / "RUN_STATUS.json"), load(root / "LAUNCH.json")
    if alive(job.get("pid")) or (root / "WORKER_LOCK.json").exists() or job.get("state") != "finished":
        raise RuntimeError("A live worker, unresolved lock, or unfinished job prevents resuming")
    if prior.get("state") != "incremental_estimate_safety_cap" or job.get("stop_reason") != prior["state"]:
        raise RuntimeError("Only a local estimate-guard stop can use this explicit continuation")
    if config["max_incremental_cli_estimate_usd"] != prior["incremental_cli_estimate_safety_cap_usd"]:
        raise RuntimeError("Configuration changed before reviewed continuation")
    if unreviewed_cost_count(root, config, prior) != 0:
        raise RuntimeError("Unresolved provider costs require review")
    if launch.get("resume_history"):
        old = load(root / "RESUME_HISTORY" / launch["resume_history"])
        if file_sha(root / "SOURCES.json") != old["sources_sha256"]:
            raise RuntimeError("Frozen source selection changed")
        for name, value in old["preserved_file_sha256"].items():
            if file_sha(root / name) != value:
                raise RuntimeError("Previously preserved provider artifact changed")
    pending = pending_batches(root, config)
    if not pending:
        raise RuntimeError("No untouched prepared batches remain")
    # Finite reserve for this frozen source pool, not a new paid-usage budget.
    new_config = dict(config)
    new_cap = ceil((prior["conservative_cli_estimate_reserved_usd"] + len(pending) * config["max_call_budget_usd"]) * 100) / 100
    new_config["max_incremental_cli_estimate_usd"] = new_cap
    new_config["subscription_only_continuation"] = {
        "approved_date": "2026-10-19", "scope": "existing_frozen_sources_only",
        "preflight_file": str(evidence_path.relative_to(root)), "preflight_sha256": file_sha(evidence_path),
        "prepared_sources_sha256": file_sha(root / "SOURCES.json"), "pending_batches": pending,
        "previous_local_estimate_cap_usd": config["max_incremental_cli_estimate_usd"],
        "this_is_not_payment_authorization": True}
    history = {"created_at_utc": stamp(), "reason": "User authorized included-quota continuation after local estimate guard",
        "subscription_preflight": evidence, "previous_config": config, "next_config": new_config,
        "previous_job": job, "previous_status": prior, "previous_launch": launch,
        "preserved_file_sha256": {str(path.relative_to(root)): file_sha(path)
            for path in sorted(root.glob("provider*/*")) if path.is_file()},
        "preserved_protocol_file_sha256": {str(path.relative_to(root)): file_sha(path)
            for path in sorted(root.glob("REWRITE_PROTOCOL_*.json"))},
        "preserved_canary_file_sha256": {str(path.relative_to(BASE)): file_sha(path)
            for path in sorted((BASE / config["canary_private_dir"]).rglob("*.json"))}
            if config.get("canary_private_dir") else {},
        "sources_sha256": file_sha(root / "SOURCES.json"), "no_completed_batch_retry": True,
        "no_extra_usage_activation": True, "estimate_only_cap_adjustment": True}
    name = "included_quota_" + history["created_at_utc"].replace(":", "").replace("+", "_") + ".json"
    dump(root / "RESUME_HISTORY" / name, history)
    return name, new_config


def worker(config, root):
    lock = root / "WORKER_LOCK.json"
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        raise RuntimeError("A worker lock exists; do not launch duplicate provider calls")
    with os.fdopen(fd, "w") as stream:
        json.dump({"pid": os.getpid(), "started_at_utc": stamp()}, stream)
    job = root / "JOB.json"
    try:
        dump(job, {"pid": os.getpid(), "state": "running", "started_at_utc": stamp(), "target": config["target_sources"]})
        run = subprocess.run([sys.executable, str(BASE / "src/run_expansion.py")], cwd=BASE.parents[1])
        if run.returncode:
            state(root, config, "worker_error", f"Runner exited with code {run.returncode}; no automatic retry")
        review = subprocess.run([sys.executable, str(BASE / "src/build_expansion_review.py")], cwd=BASE.parents[1])
        final = load(root / "RUN_STATUS.json")
        dump(job, {"pid": os.getpid(), "state": "finished", "finished_at_utc": stamp(), "stop_reason": final["state"],
                   "total_generated_triplets": final["total_generated_triplets"], "review_build_exit_code": review.returncode})
    except BaseException as exc:
        state(root, config, "worker_error", str(exc)[:400])
        dump(job, {"pid": os.getpid(), "state": "failed", "finished_at_utc": stamp(), "error": str(exc)[:400]})
        raise
    finally:
        if lock.exists() and load(lock).get("pid") == os.getpid():
            lock.unlink()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--worker", action="store_true")
    ap.add_argument("--resume", action="store_true", help="Resume only after verified, explicitly reviewed refusal exclusion")
    ap.add_argument("--resume-included-quota", action="store_true", help="Explicit user-authorized continuation after a local estimate guard; extra usage must be disabled")
    args = ap.parse_args()
    if args.resume and args.resume_included_quota:
        ap.error("Choose one reviewed continuation path")
    config = load(BASE / "configs/expansion_10000_v1.json")
    root = BASE / config["private_dir"]
    root.mkdir(parents=True, exist_ok=True)
    job = root / "JOB.json"
    resume_history = None
    if args.worker:
        worker(config, root)
        return
    if job.exists():
        old = load(job)
        if old.get("state") == "running" and alive(old.get("pid")):
            print(json.dumps({"already_running": True, **old}))
            return
        if args.resume_included_quota:
            from subscription_preflight import capture_subscription_preflight
            evidence = capture_subscription_preflight(config, root)
            resume_history, config = prepare_included_quota_resume(root, config, evidence)
            dump(BASE / "configs/expansion_10000_v1.json", config)
        elif args.resume:
            resume_history = prepare_resume(root, config)
        elif old.get("state") in {"finished", "failed"} or old.get("state") == "running":
            raise RuntimeError("Previous worker stopped; inspect its reason before authorizing a new launch")
    elif args.resume or args.resume_included_quota:
        raise RuntimeError("Cannot resume without a prior job")
    if (root / "WORKER_LOCK.json").exists():
        raise RuntimeError("An unresolved worker lock prevents launching")
    log = root / "BACKGROUND.log"
    with log.open("ab") as stream:
        process = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "--worker"], cwd=BASE.parents[1],
                                   stdin=subprocess.DEVNULL, stdout=stream, stderr=subprocess.STDOUT, start_new_session=True)
    dump(root / "LAUNCH.json", {"pid": process.pid, "launched_at_utc": stamp(), "log": str(log), "incremental_cli_estimate_cap_usd": config["max_incremental_cli_estimate_usd"], "resume_history": resume_history})
    print(json.dumps({"pid": process.pid, "launched": True, "log": str(log)}))


if __name__ == "__main__":
    main()
