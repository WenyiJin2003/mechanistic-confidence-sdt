"""Run the frozen v3.2 eight-source rewrite smoke through Antigravity.

This is a transport-only pilot.  It reuses the frozen v3.2 sources, prompt,
schema, tokenizer, and mechanical validator without changing the Claude v3.2
namespace.  Outputs stay in an ignored Gemini-specific private directory and
the public report contains aggregates only.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

if __package__ in {None, ""}:  # pragma: no cover
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from experiments.diverse_pairs_multilayer_v1.src import (
    run_claude_rewrite_batches_v32 as v32,
)


BASE = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = BASE / "configs" / "gemini_rewrite_dev_v32g.json"
PROTOCOL_VERSION = "gemini-symmetric-diverse-rewrite-v3.2g-textonly"
RUNNER_VERSION = "3"
AGENT_NAME = "confidence-rewriter"
AGENT_FILE = (
    Path(__file__).resolve().parents[3]
    / ".agents/agents/confidence-rewriter/agent.md"
)
v2 = v32.v2


@dataclass(frozen=True)
class Config:
    config_path: Path
    config_sha256: str
    source_config: Path
    output_root: Path
    public_report: Path
    model: str
    effort: str
    agy_binary: Path
    max_transport_retries: int
    timeout_seconds: int


def _resolve(value: str) -> Path:
    path = Path(value).expanduser()
    return path if path.is_absolute() else BASE / path


def load_config(path: Path) -> Config:
    raw_bytes = path.read_bytes()
    raw = json.loads(raw_bytes)
    if raw.get("protocol_version") != PROTOCOL_VERSION:
        raise ValueError("Wrong Gemini v3.2g protocol")
    config = Config(
        config_path=path.resolve(),
        config_sha256=v2.sha256_bytes(raw_bytes),
        source_config=_resolve(str(raw["source_config"])),
        output_root=_resolve(str(raw["output_root"])).resolve(),
        public_report=_resolve(str(raw["public_report"])).resolve(),
        model=str(raw["model"]),
        effort=str(raw["effort"]),
        agy_binary=Path(str(raw["agy_binary"])).expanduser().resolve(),
        max_transport_retries=int(raw["max_transport_retries"]),
        timeout_seconds=int(raw["timeout_seconds"]),
    )
    expected_output = (
        BASE / "private_data/gemini_rewrite_dev_v32g_textonly/smoke"
    ).resolve()
    expected_report = (
        BASE / "reports/gemini_smoke_v32g_textonly_quality_gate.json"
    ).resolve()
    if config.source_config.resolve() != v32.DEFAULT_CONFIG.resolve():
        raise ValueError("Gemini v3.2g must reuse the frozen v3.2 source config")
    if config.output_root != expected_output or config.public_report != expected_report:
        raise ValueError("Gemini v3.2g output namespace changed")
    if config.model != "gemini-3.8-flash-low" or config.effort != "low":
        raise ValueError("Gemini v3.2g model or effort changed")
    if config.max_transport_retries != 0 or config.timeout_seconds != 1200:
        raise ValueError("Gemini v3.2g transport policy changed")
    if not config.agy_binary.is_file():
        raise FileNotFoundError(f"Antigravity CLI not found: {config.agy_binary}")
    if not AGENT_FILE.is_file():
        raise FileNotFoundError(f"Zero-tool Antigravity agent not found: {AGENT_FILE}")
    return config


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _immutable_json(path: Path, value: Any) -> None:
    data = _canonical(value) + b"\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError(f"Refusing to overwrite changed artifact: {path}")
        return
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
        handle.write(data)
        temp_path = Path(handle.name)
    os.replace(temp_path, path)


def _binary_identity(config: Config) -> dict[str, Any]:
    result = subprocess.run(
        [str(config.agy_binary), "--version"],
        text=True,
        capture_output=True,
        timeout=30,
        env=v2.minimal_environment(),
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError("Could not identify Antigravity CLI")
    return {
        "resolved": str(config.agy_binary),
        "file_sha256": v2.sha256_file(config.agy_binary),
        "version": result.stdout.strip(),
    }


def _prompt(batch: v32.RewriteBatch) -> str:
    no_tools = (
        "Do not call any tools or commands. Do not read or write files. All required "
        "data is already present below. Produce the structured JSON directly."
    )
    return (
        v32.SYSTEM_PROMPT + "\n" + no_tools + "\n\n"
        + v32.build_prompt(batch, generation_attempt=0)
    )


def generation_identity(
    config: Config,
    source_config: v32.RunnerConfig,
    public: Mapping[str, Any],
    rows: Sequence[Mapping[str, Any]],
    batch: v32.RewriteBatch,
) -> dict[str, Any]:
    schema = v32.output_schema(batch)
    prompt = _prompt(batch)
    contract = {
        "protocol_version": PROTOCOL_VERSION,
        "runner_version": RUNNER_VERSION,
        "config_sha256": config.config_sha256,
        "source_protocol_version": source_config.protocol_version,
        "source_config_sha256": source_config.config_sha256,
        "source_file_sha256": public["sets"]["smoke"]["file_sha256"],
        "source_records_sha256": public["sets"]["smoke"]["source_records_sha256"],
        "ordered_source_records_sha256": v2.sha256_bytes(_canonical(list(rows))),
        "prompt_sha256": v2.sha256_text(prompt),
        "schema_sha256": v2.sha256_bytes(_canonical(schema)),
        "model": config.model,
        "effort": config.effort,
        "transport": {
            "binary": _binary_identity(config),
            "agent_name": AGENT_NAME,
            "agent_file_sha256": v2.sha256_file(AGENT_FILE),
            "agent_tools": [],
            "headless": True,
            "sandbox": True,
            "max_attempts": config.max_transport_retries + 1,
            "timeout_seconds": config.timeout_seconds,
        },
        "validation": {
            "implementation_sha256": v2.sha256_file(Path(v32.__file__)),
            "tokenizer": v2.TOKENIZER_ID,
            "tokenizer_file_sha256": v2.tokenizer_file_hashes(),
            "same_v32_prompt_schema_and_mechanical_gate": True,
        },
        "batch": {
            "batch_id": batch.batch_id,
            "source_ids": [row["source_id"] for row in batch.rows],
            "source_hashes": [row["original_response_sha256"] for row in batch.rows],
        },
    }
    contract_sha = v2.sha256_bytes(_canonical(contract))
    return {
        "generation_contract": contract,
        "generation_contract_sha256": contract_sha,
        "generation_fingerprint": v2.sha256_text("v32g:" + contract_sha),
    }


def _command(config: Config, prompt: str, schema: Mapping[str, Any]) -> list[str]:
    return [
        str(config.agy_binary),
        "-p", prompt,
        "--model", config.model,
        "--agent", AGENT_NAME,
        "--effort", config.effort,
        "--output-format", "json",
        "--json-schema", json.dumps(schema, ensure_ascii=False, separators=(",", ":")),
        "--print-timeout", "20m",
        "--disable-slash-commands",
        "--sandbox",
    ]


def _response_json(response: str) -> dict[str, Any]:
    fenced = re.findall(r"```(?:json)?\s*\n?(.*?)```", response, flags=re.DOTALL | re.IGNORECASE)
    candidates: list[dict[str, Any]] = []
    for block in fenced:
        try:
            value = json.loads(block.strip())
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            candidates.append(value)
    if not candidates:
        try:
            value = json.loads(response.strip())
        except json.JSONDecodeError as exc:
            raise ValueError("Antigravity response contained no parseable JSON object") from exc
        if not isinstance(value, dict):
            raise ValueError("Antigravity response JSON is not an object")
        candidates = [value]
    first = candidates[0]
    if any(candidate != first for candidate in candidates[1:]):
        raise ValueError("Antigravity returned conflicting repeated JSON objects")
    return first


def _decode(stdout: str, expected_schema: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    envelope = json.loads(stdout)
    if not isinstance(envelope, dict) or envelope.get("status") != "SUCCESS":
        raise ValueError("Antigravity did not return a SUCCESS envelope")
    structured = envelope.get("structured_output")
    if not isinstance(structured, dict):
        response = envelope.get("response")
        if not isinstance(response, str) or not response.strip():
            raise ValueError("Antigravity envelope omitted structured output and JSON text")
        structured = _response_json(response)
    if envelope.get("json_schema") != expected_schema:
        raise ValueError("Antigravity echoed a different JSON schema")
    usage = envelope.get("usage")
    if not isinstance(usage, dict):
        raise ValueError("Antigravity envelope omitted usage")
    for key in ("input_tokens", "output_tokens", "thinking_tokens", "total_tokens"):
        value = usage.get(key)
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise ValueError(f"Invalid Antigravity usage field: {key}")
    metadata = {
        "conversation_id": envelope.get("conversation_id"),
        "status": envelope.get("status"),
        "duration_seconds": envelope.get("duration_seconds"),
        "num_turns": envelope.get("num_turns"),
        "usage": usage,
    }
    return structured, metadata


def _parse_and_validate(
    raw_path: Path,
    raw: Mapping[str, Any],
    batch: v32.RewriteBatch,
    source_config: v32.RunnerConfig,
    tokenizer: Any,
    identity: Mapping[str, Any],
) -> dict[str, Any]:
    schema = v32.output_schema(batch)
    structured, metadata = _decode(str(raw["stdout"]), schema)
    records, batch_issues = v32.validate_structured_output(
        batch, structured, source_config, tokenizer
    )
    fingerprint = str(identity["generation_fingerprint"])
    for record in records:
        record["generation_attempt"] = 0
        record["attempt_fingerprint"] = fingerprint
    return {
        "protocol_version": PROTOCOL_VERSION,
        "generation_contract_sha256": identity["generation_contract_sha256"],
        "generation_fingerprint": fingerprint,
        "terminal": True,
        "source_raw_artifact": raw_path.name,
        "source_raw_artifact_sha256": v2.sha256_file(raw_path),
        "structured_output_sha256": v2.sha256_bytes(_canonical(structured)),
        "metadata": metadata,
        "batch_validation_issues": batch_issues,
        "records": records,
        "records_sha256": v2.sha256_bytes(_canonical(records)),
    }


def _summary(parsed: Mapping[str, Any], config: Config) -> dict[str, Any]:
    records = list(parsed["records"])
    counts = Counter(str(record.get("status")) for record in records)
    status_counts = {
        name: counts.get(name, 0)
        for name in ("accepted", "needs_review", "not_applicable", "validation_failed")
    }
    batch_issues = list(parsed.get("batch_validation_issues", []))
    gate_pass = (
        status_counts == {
            "accepted": 8,
            "needs_review": 0,
            "not_applicable": 0,
            "validation_failed": 0,
        }
        and not batch_issues
    )
    return {
        "protocol_version": PROTOCOL_VERSION,
        "source_count": len(records),
        "model": config.model,
        "effort": config.effort,
        "status_counts": status_counts,
        "batch_validation_issue_count": len(batch_issues),
        "mechanical_smoke_gate_pass": gate_pass,
        "semantic_human_review_required_before_scale": True,
        "scale_authorized": False,
        "generation_contract_sha256": parsed["generation_contract_sha256"],
        "generation_fingerprint": parsed["generation_fingerprint"],
        "contains_source_text": False,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args(argv)
    config = load_config(args.config.resolve())
    source_config = v32.load_config(config.source_config, "smoke")
    rows, public = v32.validate_frozen_input(source_config)
    batch = v32.make_batches(rows, "smoke", 8)[0]
    identity = generation_identity(config, source_config, public, rows, batch)
    manifest_path = config.output_root / "run_manifest.json"
    _immutable_json(manifest_path, identity)
    plan = {
        "execute": bool(args.execute),
        "source_count": len(rows),
        "model": config.model,
        "effort": config.effort,
        "output_root": str(config.output_root),
        "generation_contract_sha256": identity["generation_contract_sha256"],
    }
    if not args.execute:
        print(json.dumps(plan, sort_keys=True))
        return 0

    tokenizer = v2.load_pinned_tokenizer(
        identity["generation_contract"]["validation"]["tokenizer_file_sha256"]
    )
    raw_path = config.output_root / "raw" / "attempt_0.json"
    parsed_path = config.output_root / "parsed" / "attempt_0.json"
    parsed: dict[str, Any]
    if parsed_path.exists():
        parsed = json.loads(parsed_path.read_text(encoding="utf-8"))
        if parsed.get("generation_contract_sha256") != identity["generation_contract_sha256"]:
            raise ValueError("Cached Gemini parsed artifact belongs to another contract")
    else:
        if raw_path.exists():
            raw = json.loads(raw_path.read_text(encoding="utf-8"))
            if raw.get("generation_contract_sha256") != identity["generation_contract_sha256"]:
                raise ValueError("Cached Gemini raw artifact belongs to another contract")
            if int(raw.get("returncode", 1)) != 0:
                raise RuntimeError("Cached Gemini transport failed; preserve it for diagnosis")
        else:
            prompt = _prompt(batch)
            schema = v32.output_schema(batch)
            command = _command(config, prompt, schema)
            with tempfile.TemporaryDirectory(prefix="gemini-v32g-") as temp_name:
                temp_root = Path(temp_name)
                temp_agent = (
                    temp_root / ".agents/agents" / AGENT_NAME / "agent.md"
                )
                temp_agent.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(AGENT_FILE, temp_agent)
                result = subprocess.run(
                    command,
                    text=True,
                    capture_output=True,
                    timeout=config.timeout_seconds,
                    cwd=temp_root,
                    env=v2.minimal_environment(),
                    check=False,
                )
            raw = {
                "protocol_version": PROTOCOL_VERSION,
                "generation_contract_sha256": identity["generation_contract_sha256"],
                "generation_fingerprint": identity["generation_fingerprint"],
                "transport_attempt": 1,
                "command": [
                    (
                        "<prompt>" if index > 0 and command[index - 1] == "-p"
                        else "<json-schema>" if index > 0 and command[index - 1] == "--json-schema"
                        else value
                    )
                    for index, value in enumerate(command)
                ],
                "returncode": int(result.returncode),
                "stdout": str(result.stdout),
                "stderr": str(result.stderr),
                "stdout_sha256": v2.sha256_text(str(result.stdout)),
                "stderr_sha256": v2.sha256_text(str(result.stderr)),
            }
            _immutable_json(raw_path, raw)
            if result.returncode != 0:
                raise RuntimeError(f"Antigravity transport failed with code {result.returncode}")
        parsed = _parse_and_validate(
            raw_path, raw, batch, source_config, tokenizer, identity
        )
        _immutable_json(parsed_path, parsed)

    summary = _summary(parsed, config)
    _immutable_json(config.public_report, summary)
    print(json.dumps(summary, sort_keys=True))
    return 0 if summary["mechanical_smoke_gate_pass"] else 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
