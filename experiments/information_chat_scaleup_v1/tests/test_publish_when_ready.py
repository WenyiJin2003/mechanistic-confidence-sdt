"""Offline publication boundary tests; never invoke Git, models or providers."""
from datetime import datetime, timedelta, timezone
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest


SCRIPT = Path(__file__).resolve().parents[1] / "src/publish_when_ready.py"
SPEC = importlib.util.spec_from_file_location("haiku5000_publish_when_ready", SCRIPT)
publish = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(publish)


@pytest.fixture
def sandbox(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    base = repo / "experiments/information_chat_scaleup_v1"
    run = base / "private_data/run_5000_v1"
    run.mkdir(parents=True)
    monkeypatch.setattr(publish, "REPO", repo)
    monkeypatch.setattr(publish, "BASE", base)
    monkeypatch.setattr(publish, "RUN", run)
    state = {"branch": publish.BRANCH, "remote": publish.REMOTE, "staged": [], "commands": [],
             "head": "f" * 40, "remote_head": "f" * 40}

    def fake_git(*args):
        if args == ("branch", "--show-current"):
            return state["branch"]
        if args == ("remote", "get-url", "stage0"):
            return state["remote"]
        if args == ("diff", "--cached", "--name-only"):
            return "\n".join(state["staged"])
        if args == ("rev-parse", "HEAD"):
            return state["head"]
        if args == ("rev-parse", f"stage0/{publish.BRANCH}"):
            return state["remote_head"]
        raise AssertionError(f"Unexpected Git query: {args}")

    def fake_run(command, **kwargs):
        state["commands"].append(command)
        if command[:3] == ["git", "add", "--"]:
            state["staged"] = command[3:]
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(publish, "git", fake_git)
    monkeypatch.setattr(publish.subprocess, "run", fake_run)
    monkeypatch.setattr(publish.time, "sleep", lambda _: pytest.fail("Unexpected wait"))
    return repo, run, state


@pytest.mark.parametrize("field,value", [
    ("branch", "main"),
    ("remote", "https://example.invalid/unapproved.git"),
    ("staged", ["private_data/response.json"]),
])
def test_publication_rejects_wrong_branch_remote_or_existing_stage(sandbox, field, value):
    _, _, state = sandbox
    state[field] = value
    with pytest.raises(RuntimeError):
        publish.check_git()
    assert state["commands"] == []


@pytest.mark.parametrize("analysis,locked", [
    ({"state": "running", "phase": "local_extraction"}, False),
    ({"state": "finished", "phase": "requires_attention", "outcome": "requires_attention"}, False),
    ({"state": "finished", "phase": "complete", "outcome": "failed"}, False),
    ({"state": "finished", "phase": "incomplete", "outcome": "complete"}, False),
    ({"state": "finished", "phase": "complete", "outcome": "complete"}, True),
])
def test_unfinished_failed_or_locked_analysis_never_builds_or_publishes(sandbox, analysis, locked):
    _, run, state = sandbox
    (run / "RUN_JOB.json").write_text(json.dumps(analysis), encoding="utf-8")
    if locked:
        (run / "RUN_LOCK.json").write_text("{}", encoding="utf-8")
    with pytest.raises(RuntimeError):
        publish.worker(datetime.now(timezone.utc) - timedelta(seconds=1))
    job = json.loads((run / "REPORT_PUBLISH_JOB.json").read_text(encoding="utf-8"))
    assert job["state"] == "requires_attention"
    assert state["commands"] == []
    assert not (run / "REPORT_PUBLISH_LOCK.json").exists()


def ready_run(sandbox):
    repo, run, _ = sandbox
    (run / "RUN_JOB.json").write_text(json.dumps({
        "state": "finished", "phase": "complete", "outcome": "complete",
    }), encoding="utf-8")
    (run / "RESULTS.json").write_text(json.dumps({"status": "complete", "candidate_pairs": 5000}), encoding="utf-8")
    (run / "REPORT_PUBLISH_LAUNCH.json").write_text(json.dumps({"baseline_head": "f" * 40}), encoding="utf-8")
    for name in publish.FILES:
        path = repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"synthetic public aggregate")


def test_worker_stages_only_public_allowlist_and_never_restarts_analysis(sandbox):
    ready_run(sandbox)
    _, run, state = sandbox
    publish.worker(datetime.now(timezone.utc) + timedelta(minutes=1))
    commands = state["commands"]
    additions = [row for row in commands if row[:3] == ["git", "add", "--"]]
    assert additions == [["git", "add", "--", *publish.FILES]]
    assert not any("private_data" in name for name in publish.FILES)
    assert len(commands) == 5
    assert Path(commands[0][1]).name == "build_reports.py"
    assert commands[-1] == ["git", "push", "stage0", f"HEAD:refs/heads/{publish.BRANCH}"]
    job = json.loads((run / "REPORT_PUBLISH_JOB.json").read_text(encoding="utf-8"))
    assert job["state"] == "complete"
    assert job["cloud_model_calls"] == 0
    assert set(job["artifact_sha256"]) == set(publish.FILES)


def test_unexpected_concurrently_staged_file_prevents_commit_and_push(sandbox, monkeypatch):
    ready_run(sandbox)
    _, _, state = sandbox
    original = publish.subprocess.run

    def inject_unrelated_stage(command, **kwargs):
        result = original(command, **kwargs)
        if command[:3] == ["git", "add", "--"]:
            state["staged"].append("private_data/do-not-publish.json")
        return result

    monkeypatch.setattr(publish.subprocess, "run", inject_unrelated_stage)
    with pytest.raises(RuntimeError, match="Unexpected staged publication files"):
        publish.worker(datetime.now(timezone.utc) + timedelta(minutes=1))
    assert not any(row[:2] in (["git", "commit"], ["git", "push"]) for row in state["commands"])


@pytest.mark.parametrize("changed", ["head", "remote_head"])
def test_worker_rejects_changed_or_unpushed_history_before_report_build(sandbox, changed):
    ready_run(sandbox)
    _, _, state = sandbox
    state[changed] = "a" * 40
    with pytest.raises(RuntimeError):
        publish.worker(datetime.now(timezone.utc) + timedelta(minutes=1))
    assert state["commands"] == []


@pytest.mark.parametrize("record", ["REPORT_PUBLISH_LAUNCH.json", "REPORT_PUBLISH_JOB.json", "REPORT_PUBLISH_LOCK.json"])
def test_existing_publication_record_blocks_relaunch(sandbox, monkeypatch, record):
    _, run, _ = sandbox
    (run / record).write_text("{}", encoding="utf-8")
    monkeypatch.setattr(publish.sys, "argv", [str(SCRIPT)])
    monkeypatch.setattr(publish.subprocess, "Popen", lambda *a, **k: pytest.fail("Unexpected launch"))
    with pytest.raises(RuntimeError, match="already launched"):
        publish.main()


def test_main_launches_once_and_second_invocation_is_rejected(sandbox, monkeypatch):
    _, run, _ = sandbox
    (run / "LAUNCH.json").write_text("{}", encoding="utf-8")
    calls = []

    def fake_popen(command, **kwargs):
        reservation = json.loads((run / "REPORT_PUBLISH_LAUNCH.json").read_text(encoding="utf-8"))
        assert reservation["state"] == "launch_reserved"
        assert reservation["baseline_head"] == "f" * 40
        assert reservation["pid"] is None
        calls.append(command)
        return SimpleNamespace(pid=123456)

    monkeypatch.setattr(publish.sys, "argv", [str(SCRIPT)])
    monkeypatch.setattr(publish.subprocess, "Popen", fake_popen)
    publish.main()
    with pytest.raises(RuntimeError, match="already launched"):
        publish.main()
    assert len(calls) == 1
    assert calls[0][2] == "--worker"
    launch = json.loads((run / "REPORT_PUBLISH_LAUNCH.json").read_text(encoding="utf-8"))
    assert launch["pid"] == 123456
    assert launch["cloud_model_calls"] == 0
