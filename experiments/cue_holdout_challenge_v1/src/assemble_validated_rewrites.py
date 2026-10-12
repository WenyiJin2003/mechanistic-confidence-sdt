"""Join frozen sources, compact rewrites, and exact mechanical audits privately.

Only a complete 50-row set whose source, writer, and audit identities and hashes
agree is assembled. This is a mechanical gate, not semantic or human review.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

import select_challenge_sources as selector

BASE = Path(__file__).resolve().parents[1]
PRIVATE = BASE / "private_data"
IDENTITY = ("source_id", "task", "cue_family", "length_direction", "original_response_sha256")
TEXTS = ("confident_response", "hedged_response")
WRITER_FIELDS = set(IDENTITY) | set(TEXTS) | {
    "pair_id", "rewriter_model_requested", "reasoning_effort",
    "writer_notes", "issues",
}


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_jsonl(paths: Iterable[Path]) -> list[dict[str, Any]]:
    rows = []
    for path in paths:
        for line_number, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSON: {exc.msg}") from exc
            if not isinstance(row, dict):
                raise ValueError(f"{path}:{line_number}: expected object")
            rows.append(row)
    return rows


def _index(rows: list[dict[str, Any]], label: str) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for row in rows:
        source_id = row.get("source_id")
        if not isinstance(source_id, str) or not source_id:
            raise ValueError(f"{label} row has missing source_id")
        if source_id in indexed:
            raise ValueError(f"{label} has duplicate source_id: {source_id}")
        indexed[source_id] = row
    return indexed


def assemble(source_rows: list[dict[str, Any]], writer_rows: list[dict[str, Any]],
             audit_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    sources = _index(source_rows, "source")
    writers = _index(writer_rows, "writer")
    audits = _index(audit_rows, "audit")
    expected = set(sources)
    if len(expected) != 50:
        raise ValueError(f"Frozen source set must contain exactly 50 unique rows; found {len(expected)}")
    for label, indexed in (("writer", writers), ("audit", audits)):
        missing, extra = expected - set(indexed), set(indexed) - expected
        if missing or extra:
            raise ValueError(f"{label} coverage mismatch: missing={len(missing)}, extra={len(extra)}")

    result = []
    for source_id in sorted(expected):
        source, writer, audit = sources[source_id], writers[source_id], audits[source_id]
        if set(writer) - WRITER_FIELDS:
            raise ValueError(f"Unexpected compact writer fields for {source_id}")
        if "issues" in writer and not isinstance(writer["issues"], list):
            raise ValueError(f"Writer issues must be a list for {source_id}")
        if "writer_notes" in writer and not isinstance(writer["writer_notes"], str):
            raise ValueError(f"Writer notes must be a string for {source_id}")
        if source.get("dataset") not in selector.DATASETS:
            raise ValueError(f"Frozen source has unsupported dataset for {source_id}")
        if not isinstance(source.get("prompt"), str) or not source["prompt"].strip():
            raise ValueError(f"Frozen source prompt missing: {source_id}")
        if not isinstance(source.get("group_id"), str) or not source["group_id"]:
            raise ValueError(f"Frozen source group_id missing: {source_id}")
        prompt_hash = sha256_text(" ".join(source["prompt"].casefold().split()))
        if source.get("normalized_prompt_sha256") != prompt_hash:
            raise ValueError(f"Frozen source prompt/hash mismatch: {source_id}")
        original = source.get("original_response")
        if not isinstance(original, str) or not original.strip() or sha256_text(original) != source.get("original_response_sha256"):
            raise ValueError(f"Frozen source response/hash mismatch: {source_id}")
        for field in IDENTITY:
            if writer.get(field) != source.get(field) or audit.get(field) != source.get(field):
                raise ValueError(f"{field} mismatch for {source_id}")
        if audit.get("validation_status") != "pass" or audit.get("flags") != []:
            raise ValueError(f"Mechanical audit is not pass/zero-flags: {source_id}")
        if audit.get("mechanical_only_not_semantic_or_human_review") is not True:
            raise ValueError(f"Mechanical audit provenance missing: {source_id}")
        for field in TEXTS:
            value = writer.get(field)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"Missing/blank {field}: {source_id}")
            digest_field = f"{field}_sha256"
            if audit.get(digest_field) != sha256_text(value):
                raise ValueError(f"{field} audit hash mismatch: {source_id}")
        if writer["confident_response"] == writer["hedged_response"]:
            raise ValueError(f"Identical rewrite variants: {source_id}")
        if source.get("confident_response") or source.get("hedged_response"):
            raise ValueError(f"Unexpected rewritten text in frozen source record: {source_id}")
        joined = {**source, **writer,
                  "validation_status": "pass", "validation_flags": [],
                  "mechanical_audit_sha256": sha256_text(json.dumps(audit, ensure_ascii=False,
                                                                     sort_keys=True, separators=(",", ":")))}
        result.append(joined)
    return result


def _dump_jsonl(rows: list[dict[str, Any]]) -> str:
    return "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows)


def _write_private(path: Path, text: str) -> None:
    resolved, private = path.resolve(), PRIVATE.resolve()
    if resolved != private and private not in resolved.parents:
        raise ValueError("Assembler output must stay under private_data/")
    if resolved.exists():
        raise FileExistsError(f"Refusing to overwrite existing assembled output: {resolved}")
    resolved.parent.mkdir(parents=True, exist_ok=True)
    resolved.write_text(text, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, required=True)
    parser.add_argument("--writer", type=Path, action="append", required=True)
    parser.add_argument("--audit", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path, default=PRIVATE / "validated_rewrites_50.jsonl")
    args = parser.parse_args(argv)
    output = args.output if args.output.is_absolute() else BASE / args.output
    rows = assemble(read_jsonl([args.sources]), read_jsonl(args.writer), read_jsonl(args.audit))
    _write_private(output, _dump_jsonl(rows))
    print(json.dumps({"assembled": len(rows), "mechanical_only": True,
                      "semantic_equivalence_certified": False, "output": str(output)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
