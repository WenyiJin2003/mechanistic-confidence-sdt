"""Publish only aggregate meeting artifacts after the frozen analysis completes.

This supervisor never starts extraction, evaluation, generation or account calls.
Its explicit file allowlist excludes all private model and provider artifacts.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

REPO = Path(__file__).resolve().parents[3]
BASE = REPO / "experiments/information_chat_scaleup_v1"
RUN = BASE / "private_data/run_5000_v1"
BRANCH = "codex/haiku-analysis-5000"
REMOTE = "https://github.com/WenyiJin2003/mechanistic-confidence-sdt.git"
FILES = (
    "README.md",
    "experiments/information_chat_scaleup_v1/results/RESULTS_5000.md",
    "experiments/information_chat_scaleup_v1/results/SUMMARY_5000.json",
    "experiments/information_chat_scaleup_v1/results/ALL_28_LAYERS.png",
    "experiments/information_chat_scaleup_v1/reports/MEETING_BRIEF_10MIN.md",
)


def stamp():
    return datetime.now(timezone.utc).isoformat()


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def git(*args):
    return subprocess.check_output(["git", *args], cwd=REPO, text=True).strip()


def check_git():
    if git("branch", "--show-current") != BRANCH:
        raise RuntimeError("Refuse publication from a different branch")
    if git("remote", "get-url", "stage0") != REMOTE:
        raise RuntimeError("Unexpected publication remote")
    if git("diff", "--cached", "--name-only"):
        raise RuntimeError("Existing staged changes require review")


def worker(deadline):
    job_path = RUN / "REPORT_PUBLISH_JOB.json"
    lock = RUN / "REPORT_PUBLISH_LOCK.json"
    descriptor = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w") as stream:
        json.dump({"pid": os.getpid(), "started_at_utc": stamp()}, stream)
    job = {"pid": os.getpid(), "state": "waiting_for_analysis", "started_at_utc": stamp(),
           "deadline_utc": deadline.isoformat(), "cloud_model_calls": 0,
           "allowed_files": list(FILES)}
    write(job_path, job)
    try:
        while True:
            analysis = read(RUN / "RUN_JOB.json")
            if analysis.get("state") == "finished":
                if analysis.get("outcome") != "complete" or analysis.get("phase") != "complete":
                    raise RuntimeError("Analysis needs attention; no results published")
                if not (RUN / "RUN_LOCK.json").exists():
                    break
            if datetime.now(timezone.utc) >= deadline:
                raise RuntimeError("Meeting report deadline reached before confirmed analysis completion")
            time.sleep(30)
        check_git()
        launch = read(RUN / "REPORT_PUBLISH_LAUNCH.json")
        if git("rev-parse", "HEAD") != launch["baseline_head"]:
            raise RuntimeError("Checkout history changed after publication launch")
        if git("rev-parse", f"stage0/{BRANCH}") != launch["baseline_head"]:
            raise RuntimeError("Baseline history is not the already-pushed analysis branch")
        result = read(RUN / "RESULTS.json")
        if result.get("status") != "complete" or result.get("candidate_pairs") != 5000:
            raise RuntimeError("Missing complete exact-5000 result")
        job["state"] = "assembling_cached_aggregates"
        job["results_sha256"] = hashlib.sha256((RUN / "RESULTS.json").read_bytes()).hexdigest()
        write(job_path, job)
        subprocess.run([sys.executable, str(BASE / "src/build_reports.py"), "--run-dir", str(RUN),
                        "--predictions", str(RUN / "PREDICTIONS.npz")],
                       cwd=REPO, check=True, stdin=subprocess.DEVNULL)
        if not all((REPO / name).is_file() for name in FILES):
            raise RuntimeError("The complete report allowlist was not produced")
        # A concurrently prepared unrelated change must not enter this commit.
        check_git()
        subprocess.run(["git", "add", "--", *FILES], cwd=REPO, check=True)
        staged = set(git("diff", "--cached", "--name-only").splitlines())
        if not staged or not staged.issubset(set(FILES)):
            raise RuntimeError("Unexpected staged publication files")
        subprocess.run(["git", "diff", "--cached", "--check"], cwd=REPO, check=True)
        subprocess.run(["git", "commit", "-m", "Report frozen 5000-group confidence diagnostic and meeting brief"],
                       cwd=REPO, check=True)
        job.update(state="pushing_aggregate_reports", commit=git("rev-parse", "HEAD"))
        write(job_path, job)
        subprocess.run(["git", "push", "stage0", f"HEAD:refs/heads/{BRANCH}"], cwd=REPO, check=True)
        job.update(state="complete", github_branch=f"https://github.com/WenyiJin2003/mechanistic-confidence-sdt/tree/{BRANCH}",
                   artifact_sha256={name: hashlib.sha256((REPO / name).read_bytes()).hexdigest() for name in FILES})
    except BaseException as exc:
        job.update(state="requires_attention", error_type=type(exc).__name__, error=str(exc)[:800])
        raise
    finally:
        job["finished_at_utc"] = stamp()
        write(job_path, job)
        if lock.exists() and read(lock).get("pid") == os.getpid():
            lock.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--deadline-utc", default="2026-10-20T14:50:00+00:00")
    parser.add_argument("--worker", action="store_true")
    args = parser.parse_args()
    deadline = datetime.fromisoformat(args.deadline_utc)
    if deadline.tzinfo is None:
        raise ValueError("Publication deadline must include a timezone")
    if args.worker:
        worker(deadline)
        return
    check_git()
    for name in ("REPORT_PUBLISH_LAUNCH.json", "REPORT_PUBLISH_JOB.json", "REPORT_PUBLISH_LOCK.json"):
        if (RUN / name).exists():
            raise RuntimeError("Publication already launched; reconcile the existing record instead")
    if not (RUN / "LAUNCH.json").exists():
        raise RuntimeError("Expected an already launched analysis")
    baseline = git("rev-parse", "HEAD")
    if git("rev-parse", f"stage0/{BRANCH}") != baseline:
        raise RuntimeError("Push reviewed implementation before launching report publication")
    launch_path = RUN / "REPORT_PUBLISH_LAUNCH.json"
    descriptor = os.open(launch_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    launch = {"pid": None, "state": "launch_reserved", "launched_at_utc": stamp(),
              "baseline_head": baseline, "deadline_utc": deadline.isoformat(),
              "scope": "cached_aggregate_reports_only", "cloud_model_calls": 0}
    with os.fdopen(descriptor, "w") as stream:
        json.dump(launch, stream, indent=2)
    log = RUN / "REPORT_PUBLISH.log"
    with log.open("ab") as stream:
        process = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "--worker",
            "--deadline-utc", deadline.isoformat()], cwd=REPO, stdin=subprocess.DEVNULL,
            stdout=stream, stderr=subprocess.STDOUT, start_new_session=True)
    launch.update(pid=process.pid, state="launched")
    write(launch_path, launch)
    print(json.dumps({"launched": True, "pid": process.pid, "log": str(log)}))


if __name__ == "__main__":
    main()
