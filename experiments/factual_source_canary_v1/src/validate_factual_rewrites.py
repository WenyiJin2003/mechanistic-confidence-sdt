#!/usr/bin/env python3
"""Validate factual confident/hesitant rewrites without semantic overclaiming.

The validator is intentionally independent of the earlier 50-pair task grid.
It checks the frozen 12-source canary, exact source/pair identity, protected
literal spans, formatting/content invariants, and the preregistered token-length
policy.  Semantic protected qualifiers are routed to blinded manual review;
they are never treated as literal strings unless separately listed in
``protected_spans``.

Row-level reports contain identifiers, hashes, counts, and flags, but never
source or rewrite text.  Mechanical success does not certify semantic
equivalence, naturalness, or confidence direction.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / "private_data"
RESULTS = ROOT / "results"

EXPECTED_SOURCE_COUNT = 12
SYSTEM_PROMPT = "You are a helpful assistant."
TOKENIZER_SNAPSHOT_ID = "989aa7980e4cf806f80c7fef2b1adb7bc71aa306"
DEFAULT_TOKENIZER_PATH = (
    ROOT.parents[2]
    / "semantic-entropy-probes-stage0/cache/huggingface/"
    "models--Qwen--Qwen2.5-1.5B-Instruct/snapshots"
    / TOKENIZER_SNAPSHOT_ID
)

LENGTH_DIRECTIONS = frozenset({"confident_longer", "hesitant_longer"})
DRAFT_ORDERS = frozenset({"confident_first", "hesitant_first"})

# Frozen before generation.  These values are reported with every run and are
# deliberately not inferred from the generated batch.
SOURCE_RATIO_MIN = 0.85
SOURCE_RATIO_MAX = 1.15
PAIR_RATIO_MAX = 1.08
PAIR_GAP_MIN_ALLOWANCE = 5.0
PAIR_GAP_MEAN_FRACTION = 0.05
MAX_RESPONSE_TOKENS = 512
MAX_FULL_INPUT_TOKENS = 1024

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
SPACE_RE = re.compile(r"\s+")
NUMBER_RE = re.compile(r"(?<!\w)[+-]?\d+(?:[,.]\d+)*%?")
URL_RE = re.compile(r"https?://[^\s<>]+", re.IGNORECASE)
FENCED_CODE_RE = re.compile(r"```[\s\S]*?```")
INLINE_CODE_RE = re.compile(r"(?<!`)`[^`\n]+`(?!`)")
VERIFY_RE = re.compile(r"\b(?:I verified|I checked|I confirmed|I tested|I ran the code)\b", re.I)
REFUSAL_RE = re.compile(r"\b(?:cannot answer|can't answer|unable to answer)\b", re.I)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def normalize_text(value: Any) -> str:
    """Match source-audit normalization for optional source-hash verification."""
    if value is None:
        return ""
    text = html.unescape(str(value)).replace("\u00a0", " ")
    text = re.sub(r"(?<=[a-z0-9])\.(?=[A-Z])", ". ", text)
    return SPACE_RE.sub(" ", text).strip()


def stable_source_hash(dataset: str, prompt: str, response: str, evidence: str) -> str:
    payload = "\n\x1f\n".join(
        normalize_text(value) for value in (dataset, prompt, response, evidence)
    )
    return sha256_text(payload)


def read_jsonl(paths: Iterable[Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in paths:
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSON: {exc.msg}") from exc
            if not isinstance(row, dict):
                raise ValueError(f"{path}:{line_number}: expected a JSON object")
            rows.append(row)
    return rows


def _counter(pattern: re.Pattern[str], value: str) -> Counter[str]:
    return Counter(pattern.findall(value))


def _normalized_body(value: str) -> str:
    return SPACE_RE.sub(" ", value).strip().casefold()


def basic_structure_counts(value: str) -> dict[str, int]:
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


def _source_prompt(source: dict[str, Any]) -> tuple[str | None, list[str], list[str]]:
    failures: list[str] = []
    warnings: list[str] = []
    prompt = source.get("prompt")
    question = source.get("question")
    if isinstance(prompt, str) and prompt.strip():
        if isinstance(question, str) and question.strip() and question != prompt:
            failures.append("source_prompt_question_mismatch")
        return prompt, failures, warnings
    if isinstance(question, str) and question.strip():
        warnings.append("source_question_alias_used")
        return question, failures, warnings
    failures.append("source_prompt_missing")
    return None, failures, warnings


def _validate_protected_span_spec(
    value: Any, position: int
) -> tuple[dict[str, Any] | None, str | None]:
    if isinstance(value, str):
        if not value:
            return None, f"protected_span_{position}_empty"
        return {"text": value, "case_sensitive": True, "exact_count": None}, None
    if not isinstance(value, dict):
        return None, f"protected_span_{position}_invalid_type"
    allowed = {"text", "case_sensitive", "exact_count"}
    if set(value) - allowed:
        return None, f"protected_span_{position}_unexpected_fields"
    text = value.get("text")
    case_sensitive = value.get("case_sensitive", True)
    exact_count = value.get("exact_count")
    if not isinstance(text, str) or not text:
        return None, f"protected_span_{position}_text_invalid"
    if not isinstance(case_sensitive, bool):
        return None, f"protected_span_{position}_case_sensitive_invalid"
    if exact_count is not None and (
        isinstance(exact_count, bool) or not isinstance(exact_count, int) or exact_count < 1
    ):
        return None, f"protected_span_{position}_exact_count_invalid"
    return {
        "text": text,
        "case_sensitive": case_sensitive,
        "exact_count": exact_count,
    }, None


def _span_count(value: str, spec: dict[str, Any]) -> int:
    text = spec["text"]
    if spec["case_sensitive"]:
        return value.count(text)
    return value.casefold().count(text.casefold())


def _protected_span_flags(
    source_text: str, changed: str, label: str, raw_spans: Any
) -> tuple[list[str], int]:
    failures: list[str] = []
    if raw_spans is None:
        return failures, 0
    if not isinstance(raw_spans, list):
        return ["source_protected_spans_not_list"], 0
    valid_count = 0
    for position, raw in enumerate(raw_spans, 1):
        spec, problem = _validate_protected_span_spec(raw, position)
        if problem:
            failures.append(problem)
            continue
        assert spec is not None
        valid_count += 1
        source_count = _span_count(source_text, spec)
        expected = spec["exact_count"] if spec["exact_count"] is not None else source_count
        if source_count == 0:
            failures.append(f"source_protected_span_{position}_missing")
            continue
        if source_count != expected:
            failures.append(f"source_protected_span_{position}_count_mismatch")
        if _span_count(changed, spec) != expected:
            failures.append(f"{label}_protected_span_{position}_count_changed")
    return failures, valid_count


def _protected_content_flags(original: str, changed: str, label: str) -> list[str]:
    failures: list[str] = []
    for name, pattern in (
        ("numbers", NUMBER_RE),
        ("urls", URL_RE),
        ("fenced_code", FENCED_CODE_RE),
        ("inline_code", INLINE_CODE_RE),
    ):
        if _counter(pattern, original) != _counter(pattern, changed):
            failures.append(f"{label}_{name}_changed")
    if VERIFY_RE.search(changed) and not VERIFY_RE.search(original):
        failures.append(f"{label}_added_verification_claim")
    if REFUSAL_RE.search(changed) and not REFUSAL_RE.search(original):
        failures.append(f"{label}_added_refusal")
    return failures


def _response_aliases(pair: dict[str, Any]) -> tuple[Any, list[str], list[str]]:
    """Return canonical hesitant text plus failure and warning flags."""
    canonical = pair.get("hesitant_response")
    legacy = pair.get("hedged_response")
    failures: list[str] = []
    warnings: list[str] = []
    if canonical is not None and legacy is not None and canonical != legacy:
        failures.append("ambiguous_hesitant_response_alias")
        return canonical, failures, warnings
    if canonical is None and legacy is not None:
        canonical = legacy
        warnings.append("legacy_hedged_response_alias_used")
    return canonical, failures, warnings


def _source_identity_flags(source: dict[str, Any]) -> tuple[list[str], list[str], str | None]:
    failures: list[str] = []
    warnings: list[str] = []
    prompt, prompt_failures, prompt_warnings = _source_prompt(source)
    failures.extend(prompt_failures)
    warnings.extend(prompt_warnings)
    for field in ("source_id", "dataset", "group_id", "source_hash"):
        if not isinstance(source.get(field), str) or not source[field].strip():
            failures.append(f"source_{field}_missing")
    original = source.get("original_response")
    if not isinstance(original, str) or not original.strip():
        failures.append("source_original_response_missing")
    digest = source.get("original_response_sha256")
    if not isinstance(digest, str) or not SHA256_RE.fullmatch(digest):
        failures.append("source_original_response_sha256_invalid")
    elif isinstance(original, str) and sha256_text(original) != digest:
        failures.append("source_original_response_sha256_mismatch")
    source_hash = source.get("source_hash")
    if not isinstance(source_hash, str) or not SHA256_RE.fullmatch(source_hash):
        failures.append("source_hash_invalid")
    evidence = source.get("evidence")
    if (
        isinstance(source_hash, str)
        and SHA256_RE.fullmatch(source_hash)
        and isinstance(prompt, str)
        and isinstance(original, str)
        and isinstance(evidence, str)
    ):
        expected = stable_source_hash(str(source.get("dataset", "")), prompt, original, evidence)
        if source_hash != expected:
            failures.append("source_hash_content_mismatch")
    else:
        warnings.append("source_hash_not_recomputed_without_evidence")
    direction = source.get("length_direction")
    if direction not in LENGTH_DIRECTIONS:
        failures.append("source_length_direction_invalid")
    draft_order = source.get("draft_order")
    if draft_order not in DRAFT_ORDERS:
        failures.append("source_draft_order_invalid")
    generation_order = source.get("generation_order")
    if isinstance(generation_order, bool) or not isinstance(generation_order, int) or generation_order < 1:
        failures.append("source_generation_order_invalid")
    qualifiers = source.get("protected_qualifiers", [])
    if not isinstance(qualifiers, list) or any(not isinstance(item, str) or not item for item in qualifiers):
        failures.append("source_protected_qualifiers_invalid")
    spans = source.get("protected_spans", [])
    if not isinstance(spans, list):
        failures.append("source_protected_spans_not_list")
    return failures, warnings, prompt


def _identity_match_flags(source: dict[str, Any], pair: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    for field in (
        "source_hash",
        "original_response_sha256",
        "dataset",
        "cue_family",
        "length_direction",
    ):
        if pair.get(field) != source.get(field):
            failures.append(f"pair_{field}_mismatch")
    if "draft_order" in pair and pair.get("draft_order") != source.get("draft_order"):
        failures.append("pair_draft_order_mismatch")
    issues = pair.get("issues")
    if not isinstance(issues, list):
        failures.append("pair_issues_not_list")
    elif issues:
        failures.append("pair_generation_issues_nonempty")
    return failures


def _length_flags(
    source_tokens: int,
    confident_tokens: int,
    hesitant_tokens: int,
    direction: Any,
) -> tuple[list[str], dict[str, Any]]:
    failures: list[str] = []
    confident_ratio = confident_tokens / source_tokens
    hesitant_ratio = hesitant_tokens / source_tokens
    pair_ratio = max(confident_tokens, hesitant_tokens) / min(confident_tokens, hesitant_tokens)
    gap = abs(confident_tokens - hesitant_tokens)
    pair_mean = (confident_tokens + hesitant_tokens) / 2
    gap_limit = max(PAIR_GAP_MIN_ALLOWANCE, PAIR_GAP_MEAN_FRACTION * pair_mean)
    if not SOURCE_RATIO_MIN <= confident_ratio <= SOURCE_RATIO_MAX:
        failures.append("confident_source_token_ratio_out_of_bounds")
    if not SOURCE_RATIO_MIN <= hesitant_ratio <= SOURCE_RATIO_MAX:
        failures.append("hesitant_source_token_ratio_out_of_bounds")
    if pair_ratio > PAIR_RATIO_MAX:
        failures.append("pair_token_ratio_over_limit")
    if gap > gap_limit:
        failures.append("pair_token_gap_over_limit")
    direction_correct = (
        direction == "confident_longer" and confident_tokens > hesitant_tokens
    ) or (
        direction == "hesitant_longer" and hesitant_tokens > confident_tokens
    )
    if not direction_correct:
        failures.append("length_direction_incorrect")
    return failures, {
        "source": source_tokens,
        "confident": confident_tokens,
        "hesitant": hesitant_tokens,
        "confident_source_ratio": round(confident_ratio, 6),
        "hesitant_source_ratio": round(hesitant_ratio, 6),
        "pair_ratio": round(pair_ratio, 6),
        "absolute_gap": gap,
        "allowed_gap": round(gap_limit, 6),
        "direction_correct": direction_correct,
    }


def _audit_known_pair(
    source: dict[str, Any],
    pair: dict[str, Any] | None,
    tokenizer: Any,
    *,
    duplicate_source: bool,
    duplicate_pair: bool,
) -> dict[str, Any]:
    failures, warnings, prompt = _source_identity_flags(source)
    manual: list[str] = []
    source_id = str(source.get("source_id", ""))
    if duplicate_source:
        failures.append("duplicate_source_id")
    if pair is None:
        failures.append("pair_record_missing")
        return _audit_result(source, failures, manual, warnings)
    if duplicate_pair:
        failures.append("duplicate_pair_id")
    failures.extend(_identity_match_flags(source, pair))
    hesitant, alias_failures, alias_warnings = _response_aliases(pair)
    failures.extend(alias_failures)
    warnings.extend(alias_warnings)
    confident = pair.get("confident_response")
    for label, value in (("confident", confident), ("hesitant", hesitant)):
        if not isinstance(value, str) or not value.strip():
            failures.append(f"{label}_response_missing")
    if not isinstance(confident, str) or not confident.strip() or not isinstance(hesitant, str) or not hesitant.strip():
        return _audit_result(source, failures, manual, warnings)
    original = source.get("original_response")
    if not isinstance(original, str) or not original.strip():
        return _audit_result(source, failures, manual, warnings)
    if _normalized_body(confident) == _normalized_body(hesitant):
        failures.append("pair_responses_identical")
    if _normalized_body(confident) == _normalized_body(original):
        failures.append("confident_response_verbatim_source")
    if _normalized_body(hesitant) == _normalized_body(original):
        failures.append("hesitant_response_verbatim_source")

    source_structure = basic_structure_counts(original)
    structures = {"source": source_structure}
    protected_span_count = 0
    for label, value in (("confident", confident), ("hesitant", hesitant)):
        failures.extend(_protected_content_flags(original, value, label))
        span_failures, count = _protected_span_flags(
            original, value, label, source.get("protected_spans", [])
        )
        failures.extend(span_failures)
        protected_span_count = max(protected_span_count, count)
        structures[label] = basic_structure_counts(value)
        if structures[label] != source_structure:
            failures.append(f"{label}_structure_changed")
    if structures["confident"] != structures["hesitant"]:
        failures.append("pair_structure_mismatch")

    qualifiers = source.get("protected_qualifiers", [])
    if isinstance(qualifiers, list) and qualifiers:
        manual.append("semantic_protected_qualifiers_require_manual_review")

    source_tokens = _token_count(tokenizer, original)
    confident_tokens = _token_count(tokenizer, confident)
    hesitant_tokens = _token_count(tokenizer, hesitant)
    if min(source_tokens, confident_tokens, hesitant_tokens) <= 0:
        failures.append("token_count_zero")
        token_counts: dict[str, Any] | None = None
    else:
        length_failures, token_counts = _length_flags(
            source_tokens,
            confident_tokens,
            hesitant_tokens,
            source.get("length_direction"),
        )
        failures.extend(length_failures)
        if confident_tokens > MAX_RESPONSE_TOKENS:
            failures.append("confident_response_token_limit_exceeded")
        if hesitant_tokens > MAX_RESPONSE_TOKENS:
            failures.append("hesitant_response_token_limit_exceeded")

    full_input_counts: dict[str, int] | None = None
    if isinstance(prompt, str):
        full_input_counts = {
            "confident": _full_input_count(tokenizer, prompt, confident),
            "hesitant": _full_input_count(tokenizer, prompt, hesitant),
        }
        for label, count in full_input_counts.items():
            if count > MAX_FULL_INPUT_TOKENS:
                failures.append(f"{label}_full_input_token_limit_exceeded")

    return _audit_result(
        source,
        failures,
        manual,
        warnings,
        confident_response_sha256=sha256_text(confident),
        hesitant_response_sha256=sha256_text(hesitant),
        token_counts=token_counts,
        full_input_token_counts=full_input_counts,
        structure_counts=structures,
        protected_span_count=protected_span_count,
        semantic_protected_qualifier_count=len(qualifiers) if isinstance(qualifiers, list) else None,
    )


def _audit_result(
    source: dict[str, Any],
    failures: Iterable[str],
    manual: Iterable[str],
    warnings: Iterable[str],
    **extra: Any,
) -> dict[str, Any]:
    failure_flags = sorted(set(failures))
    manual_flags = sorted(set(manual))
    warning_flags = sorted(set(warnings))
    status = "fail" if failure_flags else ("manual_review" if manual_flags else "pass")
    return {
        "source_id": source.get("source_id"),
        "dataset": source.get("dataset"),
        "group_id": source.get("group_id"),
        "source_hash": source.get("source_hash"),
        "original_response_sha256": source.get("original_response_sha256"),
        "cue_family": source.get("cue_family"),
        "length_direction": source.get("length_direction"),
        "draft_order": source.get("draft_order"),
        "generation_order": source.get("generation_order"),
        "validation_status": status,
        "mechanical_gate_pass": not failure_flags,
        "failure_flags": failure_flags,
        "manual_review_flags": manual_flags,
        "warning_flags": warning_flags,
        "semantic_equivalence_certified": False,
        "naturalness_certified": False,
        "speaker_confidence_direction_certified": False,
        **extra,
    }


def validate_factual_rewrites(
    source_rows: list[dict[str, Any]],
    pair_rows: list[dict[str, Any]],
    tokenizer: Any,
    *,
    expected_source_count: int = EXPECTED_SOURCE_COUNT,
) -> dict[str, Any]:
    """Return a text-free machine-readable validation report."""
    global_flags: list[str] = []
    source_counts = Counter(str(row.get("source_id", "")) for row in source_rows)
    pair_counts = Counter(str(row.get("source_id", "")) for row in pair_rows)
    sources: dict[str, dict[str, Any]] = {}
    pairs: dict[str, dict[str, Any]] = {}
    for row in source_rows:
        source_id = str(row.get("source_id", ""))
        if source_id and source_id not in sources:
            sources[source_id] = row
    for row in pair_rows:
        source_id = str(row.get("source_id", ""))
        if source_id and source_id not in pairs:
            pairs[source_id] = row

    if len(source_rows) != expected_source_count:
        global_flags.append("source_row_count_mismatch")
    if len(sources) != expected_source_count:
        global_flags.append("unique_source_count_mismatch")
    if len(pair_rows) != expected_source_count:
        global_flags.append("pair_row_count_mismatch")
    if len(pairs) != expected_source_count:
        global_flags.append("unique_pair_count_mismatch")
    if source_counts.get("", 0):
        global_flags.append("source_id_missing")
    if pair_counts.get("", 0):
        global_flags.append("pair_source_id_missing")
    if set(sources) != set(pairs):
        global_flags.append("source_pair_id_set_mismatch")

    group_counts = Counter(
        str(row.get("group_id", "")) for row in source_rows if row.get("group_id")
    )
    if any(count > 1 for count in group_counts.values()):
        global_flags.append("duplicate_source_group_id")
    generation_orders = [
        row.get("generation_order")
        for row in source_rows
        if isinstance(row.get("generation_order"), int)
        and not isinstance(row.get("generation_order"), bool)
    ]
    if sorted(generation_orders) != list(range(1, expected_source_count + 1)):
        global_flags.append("generation_order_not_exact_sequence")

    draft_counts = Counter(row.get("draft_order") for row in source_rows)
    expected_half = expected_source_count // 2
    if expected_source_count % 2 or draft_counts != Counter(
        {"confident_first": expected_half, "hesitant_first": expected_half}
    ):
        global_flags.append("draft_order_not_globally_balanced")
    length_counts = Counter(row.get("length_direction") for row in source_rows)
    if expected_source_count % 2 or length_counts != Counter(
        {"confident_longer": expected_half, "hesitant_longer": expected_half}
    ):
        global_flags.append("length_direction_not_globally_balanced")

    by_dataset: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in source_rows:
        if isinstance(row.get("dataset"), str) and row["dataset"]:
            by_dataset[row["dataset"]].append(row)
    for rows in by_dataset.values():
        if len(rows) != 4:
            global_flags.append("dataset_source_count_not_4")
        if Counter(row.get("draft_order") for row in rows) != Counter(
            {"confident_first": 2, "hesitant_first": 2}
        ):
            global_flags.append("draft_order_not_2_2_within_dataset")
        if Counter(row.get("length_direction") for row in rows) != Counter(
            {"confident_longer": 2, "hesitant_longer": 2}
        ):
            global_flags.append("length_direction_not_2_2_within_dataset")

    rows = [
        _audit_known_pair(
            source,
            pairs.get(source_id),
            tokenizer,
            duplicate_source=source_counts[source_id] > 1,
            duplicate_pair=pair_counts[source_id] > 1,
        )
        for source_id, source in sorted(sources.items())
    ]
    for source_id, pair in sorted(pairs.items()):
        if source_id in sources:
            continue
        rows.append({
            "source_id": source_id or None,
            "dataset": pair.get("dataset"),
            "validation_status": "fail",
            "mechanical_gate_pass": False,
            "failure_flags": ["pair_source_id_unknown"],
            "manual_review_flags": [],
            "warning_flags": [],
            "semantic_equivalence_certified": False,
            "naturalness_certified": False,
            "speaker_confidence_direction_certified": False,
        })

    statuses = Counter(row["validation_status"] for row in rows)
    failure_counts = Counter(flag for row in rows for flag in row["failure_flags"])
    manual_counts = Counter(flag for row in rows for flag in row["manual_review_flags"])
    warning_counts = Counter(flag for row in rows for flag in row["warning_flags"])
    global_flags = sorted(set(global_flags))
    report = {
        "schema_version": 1,
        "validator": "factual_direct_pair_rewrite_validator",
        "expected_source_count": expected_source_count,
        "source_rows": len(source_rows),
        "pair_rows": len(pair_rows),
        "audit_rows": len(rows),
        "mechanical_gate_pass": not global_flags and not failure_counts,
        "manual_review_required": bool(manual_counts),
        "global_failure_flags": global_flags,
        "status_counts": dict(sorted(statuses.items())),
        "failure_flag_counts": dict(sorted(failure_counts.items())),
        "manual_review_flag_counts": dict(sorted(manual_counts.items())),
        "warning_flag_counts": dict(sorted(warning_counts.items())),
        "dataset_counts": dict(
            sorted(
                Counter(
                    row.get("dataset")
                    if isinstance(row.get("dataset"), str) and row.get("dataset")
                    else "<missing>"
                    for row in source_rows
                ).items()
            )
        ),
        "draft_order_counts": dict(sorted(draft_counts.items(), key=lambda item: str(item[0]))),
        "length_direction_counts": dict(sorted(length_counts.items(), key=lambda item: str(item[0]))),
        "length_policy": {
            "arm_to_source_ratio": [SOURCE_RATIO_MIN, SOURCE_RATIO_MAX],
            "maximum_pair_ratio": PAIR_RATIO_MAX,
            "maximum_absolute_gap": f"max({PAIR_GAP_MIN_ALLOWANCE:g}, {PAIR_GAP_MEAN_FRACTION:g} * pair_mean)",
            "maximum_response_tokens": MAX_RESPONSE_TOKENS,
            "maximum_full_input_tokens": MAX_FULL_INPUT_TOKENS,
        },
        "tokenizer": {
            "model": "Qwen/Qwen2.5-1.5B-Instruct",
            "snapshot_id": TOKENIZER_SNAPSHOT_ID,
        },
        "rows": rows,
        "semantic_equivalence_certified": False,
        "naturalness_certified": False,
        "speaker_confidence_direction_certified": False,
    }
    return report


def public_summary(report: dict[str, Any]) -> dict[str, Any]:
    """Remove row-level identities while retaining aggregate gate evidence."""
    return {key: value for key, value in report.items() if key != "rows"}


def load_tokenizer(path: Path | None = None) -> Any:
    tokenizer_path = (path or DEFAULT_TOKENIZER_PATH).resolve()
    if not tokenizer_path.is_dir():
        raise FileNotFoundError(f"Pinned local tokenizer snapshot not found: {tokenizer_path}")
    from transformers import AutoTokenizer

    return AutoTokenizer.from_pretrained(str(tokenizer_path), local_files_only=True)


def _inside(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, required=True)
    parser.add_argument("--pairs", type=Path, action="append", required=True)
    parser.add_argument("--tokenizer-path", type=Path)
    parser.add_argument("--expected-source-count", type=int, default=EXPECTED_SOURCE_COUNT)
    parser.add_argument(
        "--private-report",
        type=Path,
        default=PRIVATE / "rewrite_canary_12/rewrite_validation_report.json",
    )
    parser.add_argument(
        "--summary-output",
        type=Path,
        default=RESULTS / "rewrite_canary_12_validation_summary.json",
    )
    args = parser.parse_args(argv)
    if args.expected_source_count < 1:
        parser.error("--expected-source-count must be positive")
    if not _inside(args.private_report, PRIVATE):
        parser.error("--private-report must stay under factual_source_canary_v1/private_data")
    if _inside(args.summary_output, PRIVATE):
        parser.error("--summary-output must be outside private_data")

    tokenizer = load_tokenizer(args.tokenizer_path)
    report = validate_factual_rewrites(
        read_jsonl([args.sources]),
        read_jsonl(args.pairs),
        tokenizer,
        expected_source_count=args.expected_source_count,
    )
    _write_json(args.private_report, report)
    _write_json(args.summary_output, public_summary(report))
    print(json.dumps(public_summary(report), ensure_ascii=False, sort_keys=True))
    return 0 if report["mechanical_gate_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
