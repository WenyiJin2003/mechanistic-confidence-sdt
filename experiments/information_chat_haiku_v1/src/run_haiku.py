"""Bounded, resumable Haiku-only rewrite calls through the logged-in Claude CLI.

Public source texts only. No tools, browser, MCP, hooks, agent delegation,
workspace access, provider credentials, or alternate-model fallback are enabled.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
SAFE_ENV = {"PATH", "HOME", "USER", "LOGNAME", "SHELL", "TMPDIR", "TMP", "TEMP", "LANG", "LANGUAGE", "LC_ALL", "LC_CTYPE", "TERM", "NO_COLOR", "__CF_USER_TEXT_ENCODING"}

def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def text_hash(value):
    return hashlib.sha256(value.encode()).hexdigest()

def schema(ids):
    item = {"type": "object", "additionalProperties": False,
            "properties": {"id": {"type": "string", "enum": ids}, "status": {"type": "string", "enum": ["ok", "reject"]},
                           "confident": {"type": ["string", "null"]}, "hesitant": {"type": ["string", "null"]}, "reject_reason": {"type": ["string", "null"]}},
            "required": ["id", "status", "confident", "hesitant", "reject_reason"]}
    return {"type": "object", "additionalProperties": False, "properties": {"records": {"type": "array", "minItems": len(ids), "maxItems": len(ids), "items": item}}, "required": ["records"]}

def parse_payload(envelope, ids, requested):
    if envelope.get("is_error"):
        raise RuntimeError("Provider returned an error: " + str(envelope.get("result", ""))[:500])
    usage = envelope.get("modelUsage", {})
    if not usage or requested not in usage:
        raise RuntimeError("Model provenance mismatch: " + ", ".join(usage))
    helper = {name: v for name, v in usage.items() if name != requested}
    helper_output = sum(v.get("outputTokens", 0) for v in helper.values())
    if any(name != "claude-haiku-4-5-20251001" for name in helper) or helper_output > 64:
        raise RuntimeError("Unexpected provider helper usage; do not call this a single-writer canary")
    output = envelope.get("structured_output", envelope.get("result"))
    if isinstance(output, str):
        output = json.loads(output)
    records = output.get("records", [])
    if len(records) != len(ids) or set(r["id"] for r in records) != set(ids):
        returned = [r["id"] for r in records]
        raise RuntimeError("Response ID mismatch: " + json.dumps({
            "missing": [key for key in ids if key not in returned],
            "unexpected": [key for key in returned if key not in ids],
            "duplicates": sorted({key for key in returned if returned.count(key) > 1})}))
    for r in records:
        if r["status"] == "ok" and (not r["confident"] or not r["hesitant"] or r["confident"] == r["hesitant"]):
            raise RuntimeError("Empty or identical rewrite")
        if r["status"] == "reject" and (r["confident"] is not None or r["hesitant"] is not None):
            raise RuntimeError("Rejected row contains a rewrite")
    return records

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", type=int, help="One-based batch number; omission processes missing batches sequentially")
    parser.add_argument("--repair-plan", type=Path, help="Explicit bounded content-preservation repairs, in a separate cache")
    args = parser.parse_args()
    config = json.loads((BASE / "config.json").read_text())
    if not config["model"].startswith("claude-haiku-"):
        raise RuntimeError("This canary authorizes Haiku only")
    root = BASE / config["private_dir"]
    sources = json.loads((root / "SOURCES_50.json").read_text())
    if len(sources) != 50 or len({r["source_id"] for r in sources}) != 50:
        raise RuntimeError("Expected exactly 50 distinct frozen sources")
    prompt = (BASE / config["prompt_file"]).read_text()
    plan = None
    if args.repair_plan:
        plan = json.loads(args.repair_plan.read_text())
        reasons = {r["id"]: r["reason"] for r in plan["repairs"]}
        if len(reasons) != len(plan["repairs"]):
            raise RuntimeError("Duplicate repair IDs")
        originals = {}
        for p in (root / config["provider_dir"]).glob("*.parsed.json"):
            originals.update({r["id"]: r for r in json.loads(p.read_text())["records"]})
        prior_dirs = plan.get("prior_provider_dirs", ["provider_repairs_v1"] if plan.get("provider_dir") == "provider_repairs_v2" else [])
        for dirname in prior_dirs:
            if not dirname.startswith("provider_repairs_") or "/" in dirname:
                raise RuntimeError("Invalid prior repair cache")
            for p in (root / dirname).glob("*.parsed.json"):
                originals.update({r["id"]: r for r in json.loads(p.read_text())["records"]})
        sources = [{**r, "repair_reason": reasons[r["review_id"]], "previous_versions": originals[r["review_id"]]} for r in sources if r["review_id"] in reasons]
        if len(sources) != len(reasons):
            raise RuntimeError("Unknown repair IDs")
        prompt += "\nREPAIR PASS: " + plan["instruction"] + " Preserve the existing phrasing where possible; make only the requested content corrections, while maintaining the confident/hesitant contrast. Per-record repair_reason is an editor's correction instruction, not source factual content."
    env = {k: v for k, v in os.environ.items() if k in SAFE_ENV}
    env.update({"CLAUDE_CODE_DISABLE_AUTO_MEMORY": "1", "MAX_THINKING_TOKENS": "0", "CLAUDE_CODE_MAX_OUTPUT_TOKENS": "10000"})
    size = config["batch_size"]
    batches = [(i // size + 1, sources[i:i+size]) for i in range(0, len(sources), size)]
    if args.batch is not None:
        batches = [b for b in batches if b[0] == args.batch]
        if not batches:
            raise RuntimeError("Invalid batch number")
    for index, batch in batches:
        outdir = root / (plan.get("provider_dir", "provider_repairs_v1") if plan else config.get("provider_dir", "provider"))
        if outdir.parent != root or not outdir.name.startswith("provider"):
            raise RuntimeError("Invalid provider cache path")
        parsed_path = outdir / f"batch_{index:02d}.parsed.json"
        raw_path = outdir / f"batch_{index:02d}.raw.json"
        ids = [r["review_id"] for r in batch]
        data = {"records": [{"id": r["review_id"], "question": r["question"], "original_response": r["original"]} for r in batch]}
        if plan:
            for d, r in zip(data["records"], batch):
                d.update(repair_reason=r["repair_reason"], previous_confident=r["previous_versions"]["confident"], previous_hesitant=r["previous_versions"]["hesitant"])
                if plan.get("omit_question_context"):
                    del d["question"]
        fingerprint = text_hash(json.dumps({"data": data, "prompt": prompt, "model": config["model"]}, sort_keys=True, ensure_ascii=False))
        if parsed_path.exists():
            if json.loads(parsed_path.read_text())["request_sha256"] != fingerprint:
                raise RuntimeError("Cached request differs; create a new run, do not overwrite")
            print(json.dumps({"batch": index, "status": "cached"}), flush=True)
            continue
        if raw_path.exists():
            request = json.loads((outdir / f"batch_{index:02d}.request.json").read_text())
            if request["request_sha256"] != fingerprint:
                raise RuntimeError("Saved raw response does not match current request")
            envelope = json.loads(raw_path.read_text())
            records = parse_payload(envelope, ids, config["model"])
            write_json(parsed_path, {"request_sha256": fingerprint, "model": config["model"], "records": records,
                                     "usage": envelope.get("usage"), "model_usage": envelope.get("modelUsage"), "api_equivalent_usd": envelope.get("total_cost_usd"),
                                     "human_review_completed": False, "source_contents_fact_checked": False, "recovered_from_saved_response_without_provider_call": True})
            print(json.dumps({"batch": index, "status": "recovered_cached_response_no_call"}), flush=True)
            continue
        spent = sum(json.loads(p.read_text()).get("total_cost_usd", 0) for p in root.glob("provider*/*.raw.json"))
        if spent + config["max_call_budget_usd"] > config["max_total_api_equivalent_usd"]:
            raise RuntimeError("Canary API-equivalent budget guard reached")
        with tempfile.TemporaryDirectory(prefix="haiku-rewrite-no-tools-") as tmp:
            sandbox = Path(tmp)
            settings = sandbox / "settings.json"
            write_json(settings, {"hooks": {}, "disableAllHooks": True, "enabledPlugins": {}, "alwaysThinkingEnabled": False})
            status = subprocess.run(["claude", "auth", "status", "--json"], cwd=sandbox, env=env, capture_output=True, text=True, timeout=30)
            auth = json.loads(status.stdout)
            if status.returncode or auth.get("loggedIn") is not True or auth.get("authMethod") != "claude.ai" or auth.get("apiProvider") != "firstParty":
                raise RuntimeError("No approved first-party Claude subscription session")
            command = ["claude", "--print", "--model", config["model"], "--effort", "low", "--system-prompt", prompt,
                       "--output-format", "json", "--input-format", "text",
                       "--tools", "", "--disable-slash-commands", "--no-chrome", "--no-session-persistence", "--permission-mode", "dontAsk",
                       "--setting-sources", "", "--settings", str(settings), "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}',
                       "--max-budget-usd", str(config["max_call_budget_usd"])]
            print(json.dumps({"batch": index, "status": "calling", "model": config["model"], "sources": ids}), flush=True)
            write_json(outdir / f"batch_{index:02d}.request.json", {"request_sha256": fingerprint, "model": config["model"], "data": data, "prompt": prompt, "prompt_sha256": text_hash(prompt), "started_at": datetime.now(timezone.utc).isoformat()})
            try:
                result = subprocess.run(command, input=json.dumps(data, ensure_ascii=False), cwd=sandbox, env=env, capture_output=True, text=True, timeout=config["timeout_seconds"])
            except subprocess.TimeoutExpired as exc:
                write_json(outdir / f"batch_{index:02d}.error.json", {"request_sha256": fingerprint, "status": "timeout", "automatic_retry": False})
                raise RuntimeError("Provider timed out; no automatic retry") from exc
            try:
                envelope = json.loads(result.stdout)
            except json.JSONDecodeError:
                write_json(outdir / f"batch_{index:02d}.error.json", {"exit_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr})
                raise RuntimeError("Provider response was not JSON")
            write_json(raw_path, envelope)
            records = parse_payload(envelope, ids, config["model"])
            write_json(parsed_path, {"request_sha256": fingerprint, "model": config["model"], "records": records,
                                     "usage": envelope.get("usage"), "model_usage": envelope.get("modelUsage"), "api_equivalent_usd": envelope.get("total_cost_usd"),
                                     "human_review_completed": False, "source_contents_fact_checked": False})
            print(json.dumps({"batch": index, "status": "completed", "records": len(records), "api_equivalent_usd": envelope.get("total_cost_usd"), "models": list(envelope.get("modelUsage", {}))}), flush=True)

if __name__ == "__main__":
    main()
