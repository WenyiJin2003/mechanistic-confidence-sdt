"""Validate challenge rewrites without model inference or semantic certification.

Input source JSONL rows use the frozen selector schema. Writer JSONL rows must
carry source_id, original_response_sha256, task, cue_family, length_direction,
confident_response, and hedged_response. A microbatch is validated by passing
the matching source subset; a full run uses all 50 source rows.

Row-level output is private and contains IDs/flags/counts, never response text.
The public summary contains aggregate counts and flag types only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


BASE = Path(__file__).resolve().parents[1]
PRIVATE = BASE / "private_data"
TOKENIZER_SNAPSHOT_ID = "989aa7980e4cf806f80c7fef2b1adb7bc71aa306"
TOKENIZER_SNAPSHOT = (
    BASE.parents[2]
    / "semantic-entropy-probes-stage0/cache/huggingface/models--Qwen--Qwen2.5-1.5B-Instruct"
    / "snapshots"
    / TOKENIZER_SNAPSHOT_ID
)
SYSTEM_PROMPT = "You are a helpful assistant."

NUMBER_RE = re.compile(r"(?<!\w)[+-]?\d+(?:\.\d+)?%?")
URL_RE = re.compile(r"https?://[^\s<>]+", re.IGNORECASE)
FENCED_CODE_RE = re.compile(r"```[\s\S]*?```")
INLINE_CODE_RE = re.compile(r"(?<!`)`[^`\n]+`(?!`)")
VERIFY_RE = re.compile(r"\b(?:I verified|I checked|I confirmed|I tested|I ran the code)\b", re.I)
REFUSAL_RE = re.compile(r"\b(?:cannot answer|can't answer|unable to answer)\b", re.I)

# These openings are deliberately broad enough to catch common variants of the
# previous recipe, but are only flags: novel natural constructions are allowed.
FORBIDDEN_PREFACES = [
    ("not_fully_certain", re.compile(r"^\s*i(?:'|’)m not fully certain\b", re.I)),
    ("not_entirely_certain", re.compile(r"^\s*i(?:'|’)m not entirely certain\b", re.I)),
    ("not_sure", re.compile(r"^\s*i(?:'|’)m not sure\b", re.I)),
    ("i_am_not_certain", re.compile(r"^\s*i am not (?:(?:fully|entirely|completely) )?certain\b", re.I)),
    ("i_am_not_sure", re.compile(r"^\s*i am not (?:fully |entirely |completely )?sure\b", re.I)),
    ("im_unsure", re.compile(r"^\s*i(?:'|’)m unsure\b", re.I)),
    ("cant_be_certain", re.compile(r"^\s*i can(?:not|'t|’t) be (?:(?:fully|entirely) )?certain\b", re.I)),
    ("understanding_preface", re.compile(r"^\s*my understanding is\b", re.I)),
    ("tentative_answer_preface", re.compile(r"^\s*my tentative (?:answer|view|description|read(?:ing)?)\b", re.I)),
    ("best_guess_preface", re.compile(r"^\s*my best guess is\b", re.I)),
    ("provisional_read_preface", re.compile(r"^\s*my provisional read(?:ing)? is\b", re.I)),
    ("may_be_wrong_preface", re.compile(r"^\s*i may be wrong\b", re.I)),
    ("could_be_mistaken_preface", re.compile(r"^\s*i could be mistaken\b", re.I)),
]

HARD_FLAGS = {
    "source_id_missing", "source_id_unknown", "source_duplicate_id",
    "duplicate_writer_id", "writer_record_missing", "source_hash_invalid",
    "source_hash_mismatch", "task_mismatch", "cue_family_mismatch",
    "length_direction_mismatch", "pair_id_mismatch", "empty_confident_response",
    "empty_hedged_response", "identical_pair", "confident_verbatim_source",
    "hedged_verbatim_source", "confident_response_token_limit_exceeded",
    "hedged_response_token_limit_exceeded", "confident_full_input_token_limit_exceeded",
    "hedged_full_input_token_limit_exceeded", "length_direction_incorrect",
}


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_number}: invalid JSON: {exc.msg}") from exc
        if not isinstance(row, dict):
            raise ValueError(f"{path}:{line_number}: each JSONL row must be an object")
        rows.append(row)
    return rows


def _counter(pattern: re.Pattern[str], value: str) -> Counter[str]:
    return Counter(pattern.findall(value))


def _protected_flags(original: str, changed: str, label: str) -> list[str]:
    """Return source-preservation and added-claim checks for one rewrite."""
    flags: list[str] = []
    source_fences = _counter(FENCED_CODE_RE, original)
    rewrite_fences = _counter(FENCED_CODE_RE, changed)
    if source_fences - rewrite_fences:
        flags.append(f"{label}_code_block_changed")
    if rewrite_fences - source_fences:
        flags.append(f"{label}_added_code_block")

    source_inline = _counter(INLINE_CODE_RE, original)
    rewrite_inline = _counter(INLINE_CODE_RE, changed)
    if source_inline - rewrite_inline:
        flags.append(f"{label}_inline_code_changed")
    if rewrite_inline - source_inline:
        flags.append(f"{label}_added_inline_code")

    source_urls = _counter(URL_RE, original)
    rewrite_urls = _counter(URL_RE, changed)
    if source_urls - rewrite_urls:
        flags.append(f"{label}_source_url_changed")
    if rewrite_urls - source_urls:
        flags.append(f"{label}_added_url")

    if _counter(NUMBER_RE, original) != _counter(NUMBER_RE, changed):
        flags.append(f"{label}_numeric_content_changed_check_manually")
    if VERIFY_RE.search(changed) and not VERIFY_RE.search(original):
        flags.append(f"{label}_possible_added_verification")
    if REFUSAL_RE.search(changed) and not REFUSAL_RE.search(original):
        flags.append(f"{label}_possible_new_refusal")
    return flags


def _preface_flags(value: str, label: str) -> list[str]:
    return [f"{label}_forbidden_preface:{name}"
            for name, pattern in FORBIDDEN_PREFACES if pattern.search(value)]


def basic_structure_counts(value: str) -> dict[str, int]:
    """Count lightweight structure markers for within-pair matching only."""
    lines = value.splitlines()
    paragraphs = [part for part in re.split(r"\n\s*\n", value.strip()) if part.strip()]
    return {
        "paragraphs": len(paragraphs),
        "headings": sum(bool(re.match(r"^\s{0,3}#{1,6}\s+", line)) for line in lines),
        "unordered_items": sum(bool(re.match(r"^\s*[-*+]\s+", line)) for line in lines),
        "ordered_items": sum(bool(re.match(r"^\s*\d+[.)]\s+", line)) for line in lines),
        "table_rows": sum(bool(re.match(r"^\s*\|", line)) for line in lines),
        "fenced_code_blocks": len(FENCED_CODE_RE.findall(value)),
        "inline_code_spans": len(INLINE_CODE_RE.findall(value)),
    }


def _token_count(tokenizer: Any, value: str) -> int:
    return len(tokenizer(value, add_special_tokens=False)["input_ids"])


def _full_input_count(tokenizer: Any, prompt: str, response: str) -> int:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
        {"role": "assistant", "content": response},
    ]
    return len(tokenizer.apply_chat_template(messages, tokenize=True))


def _base_audit_row(source: dict[str, Any], flags: Iterable[str], status: str,
                    pair_id: str | None = None) -> dict[str, Any]:
    return {
        "pair_id": pair_id or source.get("pair_id") or source.get("source_id"),
        "source_id": source.get("source_id"),
        "original_response_sha256": source.get("original_response_sha256"),
        "task": source.get("task"),
        "cue_family": source.get("cue_family"),
        "length_direction": source.get("length_direction"),
        "validation_status": status,
        "flags": sorted(set(flags)),
    }


def validate_rewrites(source_rows: list[dict[str, Any]], writer_rows: list[dict[str, Any]],
                      tokenizer: Any) -> list[dict[str, Any]]:
    """Validate one source set against one or more writer microbatches.

    The source file defines the expected batch: provide a subset for a
    microbatch or the full 50-row source file for full coverage. This function
    checks mechanical invariants only; it never certifies semantic equivalence
    or human review.
    """
    source_by_id: dict[str, dict[str, Any]] = {}
    source_counts = Counter(str(row.get("source_id", "")) for row in source_rows)
    for row in source_rows:
        source_id = str(row.get("source_id", ""))
        if source_id and source_id not in source_by_id:
            source_by_id[source_id] = row

    writer_by_id: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in writer_rows:
        writer_by_id[str(row.get("source_id", ""))].append(row)

    audits: list[dict[str, Any]] = []
    for source_id, source in source_by_id.items():
        flags: list[str] = []
        if not source_id:
            flags.append("source_id_missing")
        if source_counts[source_id] > 1:
            flags.append("source_duplicate_id")
        source_text = source.get("original_response")
        source_digest = source.get("original_response_sha256")
        if not isinstance(source_text, str) or not source_digest or sha256_text(source_text) != source_digest:
            flags.append("source_hash_invalid")

        matches = writer_by_id.get(source_id, [])
        if not matches:
            flags.append("writer_record_missing")
            audits.append(_base_audit_row(source, flags, "fail"))
            continue
        if len(matches) > 1:
            flags.append("duplicate_writer_id")
        writer = matches[0]

        if writer.get("original_response_sha256") != source_digest:
            flags.append("source_hash_mismatch")
        for identity_key, flag in (
            ("task", "task_mismatch"),
            ("cue_family", "cue_family_mismatch"),
            ("length_direction", "length_direction_mismatch"),
        ):
            if writer.get(identity_key) != source.get(identity_key):
                flags.append(flag)
        if source.get("pair_id") is not None and writer.get("pair_id") != source.get("pair_id"):
            flags.append("pair_id_mismatch")

        texts: dict[str, str] = {}
        tokens: dict[str, int | None] = {"confident": None, "hedged": None}
        full_counts: dict[str, int | None] = {"confident": None, "hedged": None}
        for label, field in (("confident", "confident_response"), ("hedged", "hedged_response")):
            value = writer.get(field)
            if not isinstance(value, str) or not value.strip():
                flags.append(f"empty_{label}_response")
                continue
            texts[label] = value
            flags.extend(_protected_flags(source_text if isinstance(source_text, str) else "", value, label))
            flags.extend(_preface_flags(value, label))
            response_count = _token_count(tokenizer, value)
            full_count = _full_input_count(tokenizer, str(source.get("prompt", "")), value)
            tokens[label] = response_count
            full_counts[label] = full_count
            if response_count > 512:
                flags.append(f"{label}_response_token_limit_exceeded")
            if full_count > 1024:
                flags.append(f"{label}_full_input_token_limit_exceeded")
            if value == source_text:
                flags.append(f"{label}_verbatim_source")

        if len(texts) == 2 and texts["confident"] == texts["hedged"]:
            flags.append("identical_pair")

        direction_correct: bool | None = None
        token_gap: int | None = None
        gap_within_3: bool | None = None
        if tokens["confident"] is not None and tokens["hedged"] is not None:
            confident_count, hedged_count = tokens["confident"], tokens["hedged"]
            token_gap = abs(confident_count - hedged_count)
            gap_within_3 = token_gap <= 3
            direction = source.get("length_direction")
            if direction == "confident_longer":
                direction_correct = confident_count > hedged_count
            elif direction == "hedged_longer":
                direction_correct = hedged_count > confident_count
            else:
                direction_correct = False
            if not direction_correct:
                flags.append("length_direction_incorrect")
            if not gap_within_3:
                flags.append("token_gap_over_3_check_practicality")

        structure_counts = {label: basic_structure_counts(text) for label, text in texts.items()}
        structure_match = (len(structure_counts) == 2 and
                           structure_counts["confident"] == structure_counts["hedged"])
        if len(structure_counts) == 2 and not structure_match:
            flags.append("basic_structure_counts_mismatch")

        hard_failure = bool(set(flags) & HARD_FLAGS)
        status = "fail" if hard_failure else ("flagged" if flags else "pass")
        audit = _base_audit_row(source, flags, status)
        audit.update({
            "confident_response_sha256": sha256_text(texts["confident"]) if "confident" in texts else None,
            "hedged_response_sha256": sha256_text(texts["hedged"]) if "hedged" in texts else None,
            "token_counts": tokens,
            "full_input_token_counts": full_counts,
            "length_direction_correct": direction_correct,
            "absolute_token_gap": token_gap,
            "token_gap_within_3": gap_within_3,
            "structure_counts": structure_counts,
            "structure_counts_match": structure_match if len(structure_counts) == 2 else None,
            "mechanical_only_not_semantic_or_human_review": True,
        })
        audits.append(audit)

    for index, source in enumerate((row for row in source_rows if not row.get("source_id")), 1):
        audits.append({
            "pair_id": source.get("pair_id") or f"source-row-{index}",
            "source_id": None,
            "task": source.get("task"),
            "cue_family": source.get("cue_family"),
            "length_direction": source.get("length_direction"),
            "validation_status": "fail",
            "flags": ["source_id_missing"],
            "mechanical_only_not_semantic_or_human_review": True,
        })

    # Keep unmatched writer rows visible in the private QA record, without
    # copying their response text into any output.
    for source_id, matches in writer_by_id.items():
        if source_id not in source_by_id:
            for index, writer in enumerate(matches):
                audits.append({
                    "pair_id": writer.get("pair_id") or source_id or f"unknown-{index + 1}",
                    "source_id": source_id or None,
                    "task": writer.get("task"),
                    "cue_family": writer.get("cue_family"),
                    "length_direction": writer.get("length_direction"),
                    "validation_status": "fail",
                    "flags": ["source_id_missing" if not source_id else "source_id_unknown"],
                    "mechanical_only_not_semantic_or_human_review": True,
                })
    return audits


def aggregate_summary(audits: list[dict[str, Any]], source_count: int,
                      writer_count: int,
                      source_rows: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    statuses = Counter(row["validation_status"] for row in audits)
    flags = Counter(flag for row in audits for flag in row.get("flags", []))
    source_directions = Counter(row.get("length_direction", "missing") for row in source_rows or [])
    correct_directions = Counter(
        row.get("length_direction") for row in audits if row.get("length_direction_correct") is True
    )
    allocation_flags = []
    if source_count == 50 and source_directions != Counter({"confident_longer": 25, "hedged_longer": 25}):
        allocation_flags.append("source_length_direction_not_25_25")
        flags["source_length_direction_not_25_25"] += 1
    return {
        "validator": "cue_holdout_rewrite_validator",
        "validator_version": 1,
        "tokenizer": "Qwen2.5-1.5B-Instruct",
        "tokenizer_snapshot_id": TOKENIZER_SNAPSHOT_ID,
        "source_rows": source_count,
        "writer_rows": writer_count,
        "audit_rows": len(audits),
        "status_counts": dict(sorted(statuses.items())),
        "flag_counts": dict(sorted(flags.items())),
        "source_length_direction_counts": dict(sorted(source_directions.items())),
        "correct_length_direction_counts": dict(sorted(correct_directions.items())),
        "allocation_flags": allocation_flags,
        "semantic_equivalence_certified": False,
        "human_review_certified": False,
    }


def load_pinned_tokenizer() -> Any:
    if not TOKENIZER_SNAPSHOT.is_dir():
        raise FileNotFoundError(f"Pinned local tokenizer snapshot not found: {TOKENIZER_SNAPSHOT}")
    from transformers import AutoTokenizer

    return AutoTokenizer.from_pretrained(str(TOKENIZER_SNAPSHOT), local_files_only=True)


def _write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
                    encoding="utf-8")


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8")


def _inside(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, required=True,
                        help="Frozen source JSONL; use a microbatch subset or the full 50 rows")
    parser.add_argument("--writer", type=Path, action="append", required=True,
                        help="Writer JSONL; repeat for multiple microbatch files")
    parser.add_argument("--private-output", type=Path,
                        default=PRIVATE / "rewrite_validation.jsonl")
    parser.add_argument("--summary-output", type=Path,
                        default=BASE / "reports" / "rewrite_validation_summary.json")
    args = parser.parse_args(argv)

    private_output = args.private_output if args.private_output.is_absolute() else BASE / args.private_output
    summary_output = args.summary_output if args.summary_output.is_absolute() else BASE / args.summary_output
    if not _inside(private_output, PRIVATE):
        parser.error("row-level output must be written under challenge private_data/")
    if _inside(summary_output, PRIVATE):
        parser.error("aggregate summary must be written outside private_data/")

    sources = read_jsonl(args.sources)
    writers = [row for path in args.writer for row in read_jsonl(path)]
    tokenizer = load_pinned_tokenizer()
    audits = validate_rewrites(sources, writers, tokenizer)
    summary = aggregate_summary(audits, len(sources), len(writers), sources)
    _write_jsonl(private_output, audits)
    _write_json(summary_output, summary)
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 1 if summary["status_counts"].get("fail", 0) or summary["allocation_flags"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
