"""Run the frozen local extraction and its analysis without cloud-model calls."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone

from run_cached_analysis import BASE, REPO, atomic_json, load_run, read_json


def stamp():
    return datetime.now(timezone.utc).isoformat()


def alive(pid):
    if type(pid) is not int or pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False


def worker(run):
    lock = run / "RUN_LOCK.json"
    fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(fd, "w") as stream:
        json.dump({"pid": os.getpid(), "started_at_utc": stamp()}, stream)
    job = {"pid": os.getpid(), "state": "running", "started_at_utc": stamp(),
           "scope": "frozen5000_candidate_label_development_analysis", "cloud_model_calls": 0}
    atomic_json(run / "RUN_JOB.json", job)
    script = BASE / "src/run_cached_analysis.py"
    try:
        job["phase"] = "local_extraction"
        atomic_json(run / "RUN_JOB.json", job)
        code = subprocess.run([sys.executable, str(script), "extract", "--run-dir", str(run),
            "--permit-local-forward", "--max-seconds", "7200", "--pairs-per-batch", "1"],
            cwd=REPO, stdin=subprocess.DEVNULL).returncode
        if code:
            raise RuntimeError(f"Local extraction stopped with exit code {code}; committed pairs preserved")
        job["phase"] = "per_layer_analysis"
        atomic_json(run / "RUN_JOB.json", job)
        code = subprocess.run([sys.executable, str(script), "evaluate", "--run-dir", str(run)],
            cwd=REPO, stdin=subprocess.DEVNULL).returncode
        if code:
            raise RuntimeError(f"Analysis stopped with exit code {code}; cached states preserved")
        result = read_json(run / "RESULTS.json")
        if result.get("status") != "complete" or result.get("candidate_pairs") != 5000:
            raise RuntimeError("Expected complete exact-5000 diagnostic result")
        job.update(state="finished", phase="complete", outcome="complete",
                   results_file=str(run / "RESULTS.json"), plot_file=str(run / "ALL_28_LAYERS.png"))
    except BaseException as exc:
        job.update(state="finished", phase="requires_attention", outcome="requires_attention",
                   error_type=type(exc).__name__, error=str(exc)[:500])
        raise
    finally:
        job["finished_at_utc"] = stamp()
        atomic_json(run / "RUN_JOB.json", job)
        if lock.exists() and read_json(lock).get("pid") == os.getpid():
            lock.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--worker", action="store_true")
    args = parser.parse_args()
    run, _, _ = load_run(args.run_dir)
    if args.worker:
        worker(run)
        return
    if (run / "RUN_LOCK.json").exists():
        raise RuntimeError("Existing analysis lock: inspect it, do not start a duplicate")
    job_path = run / "RUN_JOB.json"
    if job_path.exists():
        old = read_json(job_path)
        if alive(old.get("pid")):
            print(json.dumps({"already_running": True, "pid": old["pid"]}))
            return
        raise RuntimeError("An earlier analysis launch requires review before continuation")
    log = run / "BACKGROUND.log"
    with log.open("ab") as stream:
        process = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "--worker",
            "--run-dir", str(run)], cwd=REPO, stdin=subprocess.DEVNULL,
            stdout=stream, stderr=subprocess.STDOUT, start_new_session=True)
    atomic_json(run / "LAUNCH.json", {"pid": process.pid, "launched_at_utc": stamp(),
                "log_file": str(log), "scope": "local_only_frozen5000_then_evaluate", "cloud_model_calls": 0})
    print(json.dumps({"launched": True, "pid": process.pid, "log_file": str(log)}))


if __name__ == "__main__":
    main()
