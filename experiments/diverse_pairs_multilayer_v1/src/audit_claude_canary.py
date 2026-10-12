"""Audit one private Claude rewrite canary without publishing private text.

The audit reads the frozen private source manifest and one immutable raw Claude
artifact.  It deliberately bypasses the runner's strict single-model metadata
check so a bounded Claude-internal helper can be recorded without discarding a
valid structured result.  All source and rewrite text remains in memory.  The
only file written by this program is a text-free aggregate JSON report.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sys
import tempfile
import unicodedata
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Iterable, Sequence

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.diverse_pairs_multilayer_v1.src import run_claude_rewrite_batches as runner


BASE = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = BASE / "configs" / "claude_rewrite_1000.json"
DEFAULT_OUTPUT = BASE / "reports" / "claude_canary_20_audit.json"
AUDIT_VERSION = 2
EXPECTED_PAIRS = 20

THRESHOLDS: dict[str, int | float] = {
    "expected_pairs": EXPECTED_PAIRS,
    "minimum_word_ratio": 0.80,
    "maximum_word_ratio": 1.20,
    "minimum_source_token_similarity": 0.75,
    "minimum_pair_token_similarity": 0.80,
    "maximum_auxiliary_models": 1,
    "maximum_auxiliary_output_tokens": 32,
    "maximum_auxiliary_output_share": 0.01,
    "maximum_reused_three_token_span_pairs": 4,
    "maximum_reused_four_plus_token_span_pairs": 3,
    "maximum_edit_signature_pairs": 3,
    "maximum_near_duplicate_delta_cluster": 3,
    "maximum_first_edit_position_bin_pairs": 14,
    "maximum_stance_family_pairs": 8,
    "maximum_generic_wrapper_responses": 0,
    "maximum_cross_record_leak_pairs": 0,
    "maximum_structure_mismatch_pairs": 0,
    "maximum_verbatim_responses": 0,
}

TASKS = {
    "comparison_analysis", "factual_explanation", "math_logic",
    "programming", "summary_judgment",
}
DATASETS = {"allenai/WildChat-1M", "nvidia/HelpSteer2"}
LENGTH_BINS = {"short", "medium", "long"}
OUTPUT_ORDERS = {"confident_first", "hedged_first"}
LONGER_MEMBERS = {"confident", "hedged"}
ALLOWED_AUXILIARY_MODELS = {"claude-haiku-4-5-20251001"}

TOKEN_RE = re.compile(r"\w+(?:['’]\w+)?|[^\w\s]", re.UNICODE)
WORD_RE = re.compile(r"\w+(?:['’]\w+)?", re.UNICODE)
HEX64_RE = re.compile(r"(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])", re.I)
FENCED_CODE_RE = re.compile(
    r"^[ \t]*(?P<fence>`{3,}|~{3,})[^\n]*\n.*?"
    r"^[ \t]*(?P=fence)[ \t]*(?=\n|$)",
    re.MULTILINE | re.DOTALL,
)
INLINE_CODE_RE = re.compile(r"(?<!`)`+[^\n]+?`+(?!`)")

ADDED_PATTERN_GROUPS = {
    "added_verification": re.compile(
        r"\b(?:i (?:verified|checked|confirmed|tested|ran)|we (?:verified|checked|confirmed|tested))\b",
        re.I,
    ),
    "added_refusal": re.compile(
        r"\b(?:cannot answer|can't answer|unable to answer|cannot help|can't help)\b",
        re.I,
    ),
    "added_authority": re.compile(
        r"\b(?:research (?:shows|proves)|studies (?:show|prove)|experts (?:say|agree)|"
        r"according to (?:research|studies|experts|authorities)|it is well[- ]established)\b",
        re.I,
    ),
}

FORBIDDEN_PREFACES = (
    re.compile(r"^\s*i(?:'|’)m not (?:fully |entirely |completely )?(?:certain|sure)\b", re.I),
    re.compile(r"^\s*i am not (?:fully |entirely |completely )?(?:certain|sure)\b", re.I),
    re.compile(r"^\s*i(?:'|’)m unsure\b", re.I),
    re.compile(r"^\s*my (?:best guess|understanding|tentative answer|provisional read(?:ing)?) is\b", re.I),
    re.compile(r"^\s*i (?:may be wrong|could be mistaken)\b", re.I),
)

STANCE_FAMILIES: dict[str, tuple[str, ...]] = {
    "certainty": ("certain", "sure", "confident", "definite", "unquestion", "settled"),
    "belief": ("believe", "think", "view", "read", "understand", "interpret"),
    "likelihood": ("likely", "probably", "plausib", "possible", "possibly", "perhaps"),
    "appearance": ("seem", "appear", "suggest", "indicat"),
    "tentative": ("tentative", "provisional", "uncertain", "unsure", "caveat"),
    "conclusion": ("conclude", "demonstrat", "establish", "show", "suspect"),
    "modal": ("may", "might", "could", "must", "arguably"),
}

PAIR_ISSUE_CATEGORIES = {
    "runner_validation",
    "tight_length_ratio",
    "low_source_similarity",
    "low_pair_similarity",
    "structure_mismatch",
    "verbatim_original",
    "cross_record_leakage",
    "schema_leakage",
    "added_verification",
    "added_refusal",
    "added_authority",
    "generic_wrapper",
}

GLOBAL_ISSUE_CATEGORIES = {
    "reused_three_token_span",
    "reused_four_plus_token_span",
    "repeated_edit_signature",
    "near_duplicate_delta_cluster",
    "edit_position_concentration",
    "stance_family_concentration",
}

ARTIFACT_ISSUE_CATEGORIES = {"parsed_artifact_mismatch"}

TOP_LEVEL_KEYS = {
    "audit", "audit_version", "privacy", "scope", "source_composition",
    "transport_and_envelope", "thresholds", "runner_validation",
    "pair_checks", "global_shortcut_checks", "semantic_review",
    "issue_counts", "decision",
}


class CanaryAuditError(RuntimeError):
    """An intentionally text-free audit failure."""


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _normalize(value: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", value).casefold().split())


def _tokens(value: str) -> list[str]:
    return TOKEN_RE.findall(unicodedata.normalize("NFKC", value).casefold())


def _lexical(tokens: Iterable[str]) -> list[str]:
    return [token for token in tokens if WORD_RE.fullmatch(token)]


def _word_count(value: str) -> int:
    return len(re.findall(r"\S+", value))


def _token_similarity(left: str, right: str) -> float:
    return SequenceMatcher(None, _tokens(left), _tokens(right), autojunk=False).ratio()


def _numeric_summary(values: Sequence[float | int]) -> dict[str, float | int | None]:
    if not values:
        return {"minimum": None, "median": None, "maximum": None}
    ordered = sorted(values)
    midpoint = len(ordered) // 2
    median = (
        ordered[midpoint]
        if len(ordered) % 2
        else (ordered[midpoint - 1] + ordered[midpoint]) / 2
    )

    def clean(value: float | int) -> float | int:
        if isinstance(value, int):
            return value
        return round(float(value), 6)

    return {
        "minimum": clean(ordered[0]),
        "median": clean(median),
        "maximum": clean(ordered[-1]),
    }


def _safe_counter(rows: Sequence[dict[str, Any]], field: str,
                  allowed: set[str]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for row in rows:
        value = str(row.get(field, ""))
        counts[value if value in allowed else "other"] += 1
    return dict(sorted(counts.items()))


def _structure(value: str) -> dict[str, int]:
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


def _ngrams(tokens: Sequence[str], size: int) -> set[tuple[str, ...]]:
    if size <= 0 or len(tokens) < size:
        return set()
    return {tuple(tokens[index:index + size]) for index in range(len(tokens) - size + 1)}


def _delta_profile(original: str, rewritten: str) -> dict[str, Any]:
    source_tokens = _tokens(original)
    rewrite_tokens = _tokens(rewritten)
    matcher = SequenceMatcher(None, source_tokens, rewrite_tokens, autojunk=False)
    spans: list[list[str]] = []
    operations: list[tuple[str, int, tuple[str, ...]]] = []
    first_position: float | None = None
    equal_source_tokens = 0
    boundary_only = True
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            equal_source_tokens += i2 - i1
            continue
        if first_position is None:
            first_position = i1 / max(1, len(source_tokens))
        output_tokens = _lexical(rewrite_tokens[j1:j2])
        if output_tokens:
            spans.append(output_tokens)
        position_decile = min(9, int(10 * i1 / max(1, len(source_tokens))))
        operations.append((tag, position_decile, tuple(output_tokens)))
        if not (i1 == 0 or i2 == len(source_tokens)):
            boundary_only = False
    delta_tokens = [token for span in spans for token in span]
    equal_coverage = equal_source_tokens / max(1, len(source_tokens))
    stance_present = bool(_stance_families(delta_tokens))
    forbidden_preface = any(pattern.search(rewritten) for pattern in FORBIDDEN_PREFACES)
    generic_wrapper = (
        forbidden_preface
        or (
            boundary_only
            and equal_coverage >= 0.85
            and len(delta_tokens) >= 2
            and stance_present
        )
    )
    return {
        "delta_tokens": delta_tokens,
        "signature": tuple(operations),
        "first_position": first_position,
        "generic_wrapper": generic_wrapper,
    }


def _stance_families(tokens: Sequence[str]) -> set[str]:
    families: set[str] = set()
    for token in tokens:
        for family, roots in STANCE_FAMILIES.items():
            if any(token.startswith(root) for root in roots):
                families.add(family)
    return families


def _position_bin(position: float | None) -> str | None:
    if position is None:
        return None
    if position < 0.25:
        return "early"
    if position <= 0.75:
        return "middle"
    return "late"


def _char_trigrams(tokens: Sequence[str]) -> Counter[str]:
    text = " ".join(tokens)
    if len(text) < 3:
        return Counter()
    return Counter(text[index:index + 3] for index in range(len(text) - 2))


def _cosine(left: Counter[str], right: Counter[str]) -> float:
    if not left or not right:
        return 0.0
    numerator = sum(value * right.get(key, 0) for key, value in left.items())
    left_norm = math.sqrt(sum(value * value for value in left.values()))
    right_norm = math.sqrt(sum(value * value for value in right.values()))
    return numerator / (left_norm * right_norm) if left_norm and right_norm else 0.0


def _jaccard(left: Sequence[str], right: Sequence[str]) -> float:
    left_set, right_set = set(left), set(right)
    if not left_set or not right_set:
        return 0.0
    return len(left_set & right_set) / len(left_set | right_set)


def _largest_delta_cluster(delta_rows: Sequence[Sequence[str]]) -> int:
    parents = list(range(len(delta_rows)))

    def find(index: int) -> int:
        while parents[index] != index:
            parents[index] = parents[parents[index]]
            index = parents[index]
        return index

    def union(left: int, right: int) -> None:
        left_root, right_root = find(left), find(right)
        if left_root != right_root:
            parents[right_root] = left_root

    trigram_counters = [_char_trigrams(tokens) for tokens in delta_rows]
    for left in range(len(delta_rows)):
        if not delta_rows[left]:
            continue
        for right in range(left + 1, len(delta_rows)):
            if not delta_rows[right]:
                continue
            if (
                _jaccard(delta_rows[left], delta_rows[right]) >= 0.80
                or _cosine(trigram_counters[left], trigram_counters[right]) >= 0.90
            ):
                union(left, right)
    sizes = Counter(find(index) for index in range(len(delta_rows)) if delta_rows[index])
    return max(sizes.values(), default=0)


def _runner_issue_group(issue: str) -> str:
    if any(term in issue for term in ("source_id", "source_hash", "output_order", "batch:")):
        return "identity_or_schema"
    if "protected_" in issue:
        return "protected_content"
    if any(term in issue for term in ("length", "token_limit", "token_gap")):
        return "length_or_token"
    if any(term in issue for term in ("empty_response", "identical_pair", "response_not_string")):
        return "empty_or_identical"
    if "writer" in issue:
        return "writer_reported"
    if "not_applicable" in issue:
        return "not_applicable"
    return "other"


def _decode_raw(raw: dict[str, Any], batch: runner.RewriteBatch,
                config: runner.RunnerConfig) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], set[str]]:
    issues: set[str] = set()
    stdout = raw.get("stdout")
    stderr = raw.get("stderr")
    if not isinstance(stdout, str) or not isinstance(stderr, str):
        raise CanaryAuditError("raw_envelope_invalid")
    if raw.get("stdout_sha256") != _sha256_text(stdout):
        issues.add("raw_content_integrity")
    if raw.get("stderr_sha256") != _sha256_text(stderr):
        issues.add("raw_content_integrity")
    expected_ids = [str(row["source_id"]) for row in batch.rows]
    expected_hashes = [str(row["original_response_sha256"]) for row in batch.rows]
    if (
        raw.get("batch_id") != batch.batch_id
        or raw.get("source_ids") != expected_ids
        or raw.get("source_hashes") != expected_hashes
        or raw.get("batch_prompt_sha256") != runner.sha256_text(runner.build_prompt(batch))
    ):
        issues.add("raw_batch_identity")
    if (
        raw.get("returncode") != 0
        or raw.get("transport_error") is not None
        or raw.get("provider_environment_scrubbed") is not True
        or raw.get("anthropic_api_key_present") is not False
    ):
        issues.add("raw_transport_or_isolation")
    try:
        envelope = json.loads(stdout)
    except (json.JSONDecodeError, TypeError) as exc:
        raise CanaryAuditError("raw_envelope_invalid") from exc
    if not isinstance(envelope, dict) or envelope.get("is_error") is True:
        raise CanaryAuditError("raw_envelope_invalid")
    structured = envelope.get("structured_output")
    if structured is None:
        structured = envelope.get("result")
    if isinstance(structured, str):
        try:
            structured = json.loads(structured)
        except json.JSONDecodeError as exc:
            raise CanaryAuditError("structured_output_invalid") from exc
    if not isinstance(structured, dict):
        raise CanaryAuditError("structured_output_invalid")

    model_usage = envelope.get("modelUsage", envelope.get("model_usage", {}))
    if not isinstance(model_usage, dict):
        model_usage = {}
    requested_present = config.model in model_usage
    requested_value = model_usage.get(config.model, {})
    requested_output_tokens = (
        requested_value.get("outputTokens", requested_value.get("output_tokens", 0))
        if isinstance(requested_value, dict) else 0
    )
    requested_output_valid = (
        not isinstance(requested_output_tokens, bool)
        and isinstance(requested_output_tokens, (int, float))
        and requested_output_tokens > 0
    )
    auxiliary = [
        (name, value) for name, value in model_usage.items() if name != config.model
    ]
    auxiliary_output_tokens = 0
    auxiliary_shape_valid = True
    for name, value in auxiliary:
        if name not in ALLOWED_AUXILIARY_MODELS or not isinstance(value, dict):
            auxiliary_shape_valid = False
            continue
        token_value = value.get("outputTokens", value.get("output_tokens", 0))
        if isinstance(token_value, bool) or not isinstance(token_value, (int, float)):
            auxiliary_shape_valid = False
            continue
        auxiliary_output_tokens += int(token_value)
    total_output_tokens = (
        float(requested_output_tokens) + auxiliary_output_tokens
        if requested_output_valid else auxiliary_output_tokens
    )
    auxiliary_output_share = (
        auxiliary_output_tokens / total_output_tokens if total_output_tokens > 0 else 1.0
    )
    auxiliary_within_gate = (
        requested_present
        and requested_output_valid
        and auxiliary_shape_valid
        and len(auxiliary) <= int(THRESHOLDS["maximum_auxiliary_models"])
        and auxiliary_output_tokens <= int(THRESHOLDS["maximum_auxiliary_output_tokens"])
        and auxiliary_output_share <= float(THRESHOLDS["maximum_auxiliary_output_share"])
    )
    if not auxiliary_within_gate:
        issues.add("model_usage_contract")
    pairs = structured.get("pairs")
    pair_count = len(pairs) if isinstance(pairs, list) else 0
    raw_summary = {
        "returncode_zero": raw.get("returncode") == 0,
        "transport_error_count": int(raw.get("transport_error") is not None),
        "provider_environment_scrubbed": raw.get("provider_environment_scrubbed") is True,
        "provider_key_absent": raw.get("anthropic_api_key_present") is False,
        "requested_model_reported": requested_present,
        "auxiliary_model_count": len(auxiliary),
        "auxiliary_output_tokens": auxiliary_output_tokens,
        "auxiliary_output_share": round(auxiliary_output_share, 6),
        "auxiliary_usage_within_gate": auxiliary_within_gate,
        "structured_pair_count": pair_count,
    }
    return structured, envelope, raw_summary, issues


def _crosscheck_parsed_artifact(
    parsed: dict[str, Any] | None,
    batch: runner.RewriteBatch,
    config: runner.RunnerConfig,
    raw: dict[str, Any],
    independently_validated_records: Sequence[dict[str, Any]],
    independently_validated_batch_issues: Sequence[str],
    selected_raw_sha256: str | None,
) -> tuple[dict[str, Any], set[str], list[str]]:
    """Reconcile a persisted parsed artifact without returning private fields."""
    missing = {
        "present": False,
        "terminal": False,
        "processing_failed": False,
        "record_count": 0,
        "batch_identity_valid": False,
        "records_hash_valid": False,
        "configuration_valid": False,
        "legacy_recovery_present": False,
        "legacy_lineage_valid": False,
        "selected_raw_matches_lineage": False,
        "matches_independent_revalidation": False,
        "length_control_only_failed_record_count": 0,
        "length_control_issue_record_counts": {
            "target_length_direction_not_met": 0,
            "pair_token_gap_over_3": 0,
        },
        "other_validation_issue_record_count": 0,
    }
    if parsed is None:
        return missing, {"parsed_artifact_mismatch"}, []

    expected_ids = [str(row["source_id"]) for row in batch.rows]
    expected_hashes = [str(row["original_response_sha256"]) for row in batch.rows]
    parsed_records = parsed.get("records")
    record_list = parsed_records if isinstance(parsed_records, list) else []
    well_shaped_records = all(isinstance(record, dict) for record in record_list)
    records_hash_valid = (
        well_shaped_records
        and parsed.get("records_sha256")
        == runner.sha256_bytes(runner._canonical_json_bytes(record_list))
    )
    batch_identity_valid = (
        parsed.get("batch_id") == batch.batch_id
        and parsed.get("source_ids") == expected_ids
        and parsed.get("source_hashes") == expected_hashes
        and parsed.get("batch_prompt_sha256")
        == runner.sha256_text(runner.build_prompt(batch))
    )
    configuration_valid = (
        parsed.get("protocol_version") == config.protocol_version
        and parsed.get("requested_model") == config.model
        and parsed.get("requested_effort") == config.effort
        and parsed.get("split") == batch.split
        and parsed.get("rewrite_recipe") == batch.recipe
    )
    matches_independent = (
        well_shaped_records
        and record_list == list(independently_validated_records)
        and parsed.get("batch_validation_issues")
        == list(independently_validated_batch_issues)
    )

    recovery = parsed.get("recovered_from_legacy")
    recovery_present = isinstance(recovery, dict)
    lineage_valid = not recovery_present
    selected_raw_matches = not recovery_present
    if recovery_present:
        try:
            runner._verify_recovery_lineage(parsed)
        except (OSError, TypeError, ValueError, json.JSONDecodeError):
            lineage_valid = False
        else:
            lineage_valid = True
        selected_raw_matches = (
            recovery.get("additional_claude_calls") == 0
            and recovery.get("stdout_sha256") == raw.get("stdout_sha256")
            and selected_raw_sha256 is not None
            and recovery.get("raw_artifact_sha256") == selected_raw_sha256
        )

    direction_count = 0
    gap_count = 0
    other_issue_records = 0
    length_only_failures = 0
    safe_issue_names = {
        "target_length_direction_not_met",
        "pair_token_gap_over_3",
    }
    parsed_forbidden: list[str] = []
    if well_shaped_records:
        for record in record_list:
            issues = record.get("validation_issues", [])
            issue_set = set(issues) if isinstance(issues, list) else set()
            direction_count += int("target_length_direction_not_met" in issue_set)
            gap_count += int("pair_token_gap_over_3" in issue_set)
            other_issue_records += int(bool(issue_set - safe_issue_names))
            length_only_failures += int(
                record.get("status") == "validation_failed"
                and bool(issue_set)
                and issue_set <= safe_issue_names
            )
            for field in (
                "source_id", "original_response_sha256",
                "confident_response", "hedged_response",
            ):
                value = record.get(field)
                if isinstance(value, str):
                    parsed_forbidden.append(value)
            writer_issues = record.get("writer_issues", [])
            if isinstance(writer_issues, list):
                parsed_forbidden.extend(
                    value for value in writer_issues if isinstance(value, str)
                )

    artifact_valid = all((
        parsed.get("terminal") is True,
        parsed.get("processing_failed") is False,
        len(record_list) == len(batch.rows),
        batch_identity_valid,
        records_hash_valid,
        configuration_valid,
        lineage_valid,
        selected_raw_matches,
        matches_independent,
    ))
    summary = {
        "present": True,
        "terminal": parsed.get("terminal") is True,
        "processing_failed": parsed.get("processing_failed") is True,
        "record_count": len(record_list),
        "batch_identity_valid": batch_identity_valid,
        "records_hash_valid": records_hash_valid,
        "configuration_valid": configuration_valid,
        "legacy_recovery_present": recovery_present,
        "legacy_lineage_valid": lineage_valid,
        "selected_raw_matches_lineage": selected_raw_matches,
        "matches_independent_revalidation": matches_independent,
        "length_control_only_failed_record_count": length_only_failures,
        "length_control_issue_record_counts": {
            "target_length_direction_not_met": direction_count,
            "pair_token_gap_over_3": gap_count,
        },
        "other_validation_issue_record_count": other_issue_records,
    }
    return (
        summary,
        set() if artifact_valid else {"parsed_artifact_mismatch"},
        parsed_forbidden,
    )


def _cross_record_leakage(batch: runner.RewriteBatch,
                          rewritten_by_pair: Sequence[Sequence[str]]) -> set[int]:
    source_grams = [
        _ngrams(_lexical(_tokens(str(row["original_response"]))), 8)
        for row in batch.rows
    ]
    owners: dict[tuple[str, ...], set[int]] = defaultdict(set)
    for index, grams in enumerate(source_grams):
        for gram in grams:
            owners[gram].add(index)
    leaked: set[int] = set()
    for index, responses in enumerate(rewritten_by_pair):
        own = source_grams[index]
        for response in responses:
            rewrite_grams = _ngrams(_lexical(_tokens(response)), 8)
            novel = rewrite_grams - own
            if any(len(owners.get(gram, set())) == 1 and index not in owners[gram] for gram in novel):
                leaked.add(index)
                break
    return leaked


def _aggregate_semantic_review(path: Path | None, expected_pairs: int) -> dict[str, Any]:
    pending = {
        "status": "pending",
        "blind": False,
        "reviewer_count": 0,
        "human_reviewer_count": 0,
        "agent_reviewer_count": 0,
        "reviewed_pairs": 0,
        "semantic_gate_pass": False,
        "human_certified": False,
    }
    if path is None:
        return pending
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CanaryAuditError("semantic_review_invalid") from exc
    if not isinstance(payload, dict) or not isinstance(payload.get("reviews"), list):
        raise CanaryAuditError("semantic_review_invalid")
    metadata = payload.get("review_metadata", {})
    if not isinstance(metadata, dict):
        raise CanaryAuditError("semantic_review_invalid")
    reviews = payload["reviews"]
    indices = [row.get("review_index") for row in reviews if isinstance(row, dict)]
    if (
        len(reviews) != expected_pairs
        or len(indices) != expected_pairs
        or set(indices) != set(range(1, expected_pairs + 1))
    ):
        raise CanaryAuditError("semantic_review_invalid")
    allowed = {
        "content_preserved": {"pass", "fail", "uncertain"},
        "certainty_ordering": {"correct", "reversed", "tie", "uncertain"},
        "speaker_scope": {"pass", "fail", "uncertain"},
        "other_confound": {"none", "minor", "repair", "uncertain"},
        "formatting": {"pass", "mismatch", "uncertain"},
        "naturalness": {"pass", "minor", "fail"},
        "shortcut_concern": {"none", "minor", "repair", "uncertain"},
    }
    counts: dict[str, dict[str, int]] = {}
    for field, values in allowed.items():
        field_counts: Counter[str] = Counter()
        for row in reviews:
            if not isinstance(row, dict) or row.get(field) not in values:
                raise CanaryAuditError("semantic_review_invalid")
            field_counts[str(row[field])] += 1
        counts[field] = {value: field_counts.get(value, 0) for value in sorted(values)}
    minor_groups = Counter(
        row.get("minor_pattern_group")
        for row in reviews
        if row.get("shortcut_concern") == "minor" and row.get("minor_pattern_group") is not None
    )
    repeated_minor_groups = sum(count > 1 for count in minor_groups.values())
    reviewer_type = metadata.get("reviewer_type")
    if reviewer_type not in {"human", "agent"} or metadata.get("blind") is not True:
        raise CanaryAuditError("semantic_review_invalid")
    hard_pass = (
        counts["content_preserved"]["pass"] == expected_pairs
        and counts["certainty_ordering"]["correct"] == expected_pairs
        and counts["speaker_scope"]["pass"] == expected_pairs
        and counts["other_confound"]["none"] == expected_pairs
        and counts["formatting"]["pass"] == expected_pairs
        and counts["naturalness"]["fail"] == 0
        and counts["naturalness"]["minor"] <= 2
        and counts["shortcut_concern"]["repair"] == 0
        and counts["shortcut_concern"]["uncertain"] == 0
        and counts["shortcut_concern"]["minor"] <= 2
        and repeated_minor_groups == 0
    )
    return {
        "status": "complete",
        "blind": True,
        "reviewer_count": 1,
        "human_reviewer_count": int(reviewer_type == "human"),
        "agent_reviewer_count": int(reviewer_type == "agent"),
        "reviewed_pairs": expected_pairs,
        "counts": counts,
        "repeated_minor_shortcut_group_count": repeated_minor_groups,
        "semantic_gate_pass": hard_pass,
        "human_certified": hard_pass and reviewer_type == "human",
    }


def audit_batch(batch: runner.RewriteBatch, raw: dict[str, Any],
                config: runner.RunnerConfig, tokenizer: Any,
                semantic_review_path: Path | None = None,
                parsed: dict[str, Any] | None = None,
                selected_raw_sha256: str | None = None) -> tuple[dict[str, Any], list[str]]:
    structured, envelope, raw_summary, raw_issues = _decode_raw(raw, batch, config)
    records, batch_issues = runner.validate_structured_output(
        batch, structured, config, tokenizer
    )
    parsed_summary, parsed_issues, parsed_forbidden = _crosscheck_parsed_artifact(
        parsed, batch, config, raw, records, batch_issues, selected_raw_sha256
    ) if parsed is not None else (
        {
            "present": False,
            "terminal": False,
            "processing_failed": False,
            "record_count": 0,
            "batch_identity_valid": False,
            "records_hash_valid": False,
            "configuration_valid": False,
            "legacy_recovery_present": False,
            "legacy_lineage_valid": False,
            "selected_raw_matches_lineage": False,
            "matches_independent_revalidation": False,
            "length_control_only_failed_record_count": 0,
            "length_control_issue_record_counts": {
                "target_length_direction_not_met": 0,
                "pair_token_gap_over_3": 0,
            },
            "other_validation_issue_record_count": 0,
        },
        set(),
        [],
    )
    status_counts = Counter(str(record.get("status", "unknown")) for record in records)
    runner_issue_groups: Counter[str] = Counter()
    writer_issue_records = 0
    for record in records:
        groups = {
            _runner_issue_group(str(issue))
            for issue in record.get("validation_issues", [])
        }
        runner_issue_groups.update(groups)
        if record.get("writer_issues"):
            writer_issue_records += 1

    pair_issues: list[set[str]] = [set() for _ in batch.rows]
    word_ratios: list[float] = []
    source_similarities: list[float] = []
    pair_similarities: list[float] = []
    token_gaps: list[int] = []
    structure_match_count = 0
    verbatim_counts: Counter[str] = Counter()
    target_direction_matches = 0
    rewritten_by_pair: list[list[str]] = []
    delta_profiles: list[dict[str, dict[str, Any]]] = []
    schema_secrets = [
        str(value)
        for row in batch.rows
        for value in (row.get("source_id"), row.get("original_response_sha256"))
        if isinstance(value, str) and value
    ]

    for index, (source, record) in enumerate(zip(batch.rows, records)):
        if record.get("status") != "accepted":
            pair_issues[index].add("runner_validation")
        original = str(source["original_response"])
        confident = record.get("confident_response", "")
        hedged = record.get("hedged_response", "")
        confident = confident if isinstance(confident, str) else ""
        hedged = hedged if isinstance(hedged, str) else ""
        rewritten_by_pair.append([confident, hedged])
        profiles = {
            "confident": _delta_profile(original, confident),
            "hedged": _delta_profile(original, hedged),
        }
        delta_profiles.append(profiles)
        original_words = max(1, _word_count(original))
        for label, rewritten in (("confident", confident), ("hedged", hedged)):
            ratio = _word_count(rewritten) / original_words
            word_ratios.append(ratio)
            if not (
                float(THRESHOLDS["minimum_word_ratio"])
                <= ratio
                <= float(THRESHOLDS["maximum_word_ratio"])
            ):
                pair_issues[index].add("tight_length_ratio")
            similarity = _token_similarity(original, rewritten)
            source_similarities.append(similarity)
            if similarity < float(THRESHOLDS["minimum_source_token_similarity"]):
                pair_issues[index].add("low_source_similarity")
            if _normalize(rewritten) == _normalize(original):
                verbatim_counts[label] += 1
                pair_issues[index].add("verbatim_original")
            for category, pattern in ADDED_PATTERN_GROUPS.items():
                if pattern.search(rewritten) and not pattern.search(original):
                    pair_issues[index].add(category)
            if profiles[label]["generic_wrapper"]:
                pair_issues[index].add("generic_wrapper")
            newly_exposed_schema = (
                any(secret in rewritten and secret not in original for secret in schema_secrets)
                or any(marker in rewritten and marker not in original for marker in (
                    "INPUT_RECORDS_JSON", "original_response_sha256", "source_id"
                ))
                or (HEX64_RE.search(rewritten) is not None and HEX64_RE.search(original) is None)
            )
            if newly_exposed_schema:
                pair_issues[index].add("schema_leakage")
        pair_similarity = _token_similarity(confident, hedged)
        pair_similarities.append(pair_similarity)
        if pair_similarity < float(THRESHOLDS["minimum_pair_token_similarity"]):
            pair_issues[index].add("low_pair_similarity")
        structures = {_canonical(_structure(value)) for value in (original, confident, hedged)}
        if len(structures) == 1:
            structure_match_count += 1
        else:
            pair_issues[index].add("structure_mismatch")
        stats = record.get("token_stats", {})
        if isinstance(stats, dict):
            confident_stats = stats.get("confident_response", {})
            hedged_stats = stats.get("hedged_response", {})
            if isinstance(confident_stats, dict) and isinstance(hedged_stats, dict):
                confident_tokens = confident_stats.get("response_tokens")
                hedged_tokens = hedged_stats.get("response_tokens")
                if isinstance(confident_tokens, int) and isinstance(hedged_tokens, int):
                    token_gaps.append(abs(confident_tokens - hedged_tokens))
                    target = str(source["target_longer_member"])
                    if (
                        (target == "confident" and confident_tokens > hedged_tokens)
                        or (target == "hedged" and hedged_tokens > confident_tokens)
                    ):
                        target_direction_matches += 1

    for index in _cross_record_leakage(batch, rewritten_by_pair):
        pair_issues[index].add("cross_record_leakage")

    three_token_df: Counter[tuple[str, ...]] = Counter()
    four_plus_df: Counter[tuple[str, ...]] = Counter()
    signature_counts: Counter[Any] = Counter()
    position_counts = {
        "confident": Counter(),
        "hedged": Counter(),
    }
    stance_counts = {
        "confident": Counter(),
        "hedged": Counter(),
    }
    combined_delta_rows: list[list[str]] = []
    generic_wrapper_responses = 0
    for profiles in delta_profiles:
        pair_three: set[tuple[str, ...]] = set()
        pair_four_plus: set[tuple[str, ...]] = set()
        combined: list[str] = []
        pair_signature = []
        for label in ("confident", "hedged"):
            profile = profiles[label]
            delta_tokens = profile["delta_tokens"]
            combined.extend(delta_tokens)
            pair_signature.append(profile["signature"])
            pair_three.update(_ngrams(delta_tokens, 3))
            for size in range(4, min(12, len(delta_tokens)) + 1):
                pair_four_plus.update(_ngrams(delta_tokens, size))
            position = _position_bin(profile["first_position"])
            if position is not None:
                position_counts[label][position] += 1
            for family in _stance_families(delta_tokens):
                stance_counts[label][family] += 1
            generic_wrapper_responses += int(profile["generic_wrapper"])
        three_token_df.update(pair_three)
        four_plus_df.update(pair_four_plus)
        signature_counts[tuple(pair_signature)] += 1
        combined_delta_rows.append(combined)

    max_three = max(three_token_df.values(), default=0)
    max_four_plus = max(four_plus_df.values(), default=0)
    max_signature = max(signature_counts.values(), default=0)
    max_cluster = _largest_delta_cluster(combined_delta_rows)
    max_position_bin = max(
        (count for counts in position_counts.values() for count in counts.values()),
        default=0,
    )
    max_stance_family = max(
        (count for counts in stance_counts.values() for count in counts.values()),
        default=0,
    )
    global_issues: set[str] = set()
    if max_three > int(THRESHOLDS["maximum_reused_three_token_span_pairs"]):
        global_issues.add("reused_three_token_span")
    if max_four_plus > int(THRESHOLDS["maximum_reused_four_plus_token_span_pairs"]):
        global_issues.add("reused_four_plus_token_span")
    if max_signature > int(THRESHOLDS["maximum_edit_signature_pairs"]):
        global_issues.add("repeated_edit_signature")
    if max_cluster > int(THRESHOLDS["maximum_near_duplicate_delta_cluster"]):
        global_issues.add("near_duplicate_delta_cluster")
    if max_position_bin > int(THRESHOLDS["maximum_first_edit_position_bin_pairs"]):
        global_issues.add("edit_position_concentration")
    if max_stance_family > int(THRESHOLDS["maximum_stance_family_pairs"]):
        global_issues.add("stance_family_concentration")

    issue_counts: Counter[str] = Counter()
    for categories in pair_issues:
        issue_counts.update(categories)
    issue_counts.update({category: 1 for category in global_issues})
    issue_counts.update({category: 1 for category in raw_issues})
    issue_counts.update({category: 1 for category in parsed_issues})
    if batch_issues:
        issue_counts["batch_protocol"] += 1
    if generic_wrapper_responses > int(THRESHOLDS["maximum_generic_wrapper_responses"]):
        issue_counts["generic_wrapper"] = max(
            issue_counts["generic_wrapper"],
            sum("generic_wrapper" in categories for categories in pair_issues),
        )

    accepted_count = status_counts.get("accepted", 0)
    blockers = sorted(category for category, count in issue_counts.items() if count)
    automated_gate_pass = (
        len(records) == EXPECTED_PAIRS
        and accepted_count == EXPECTED_PAIRS
        and not batch_issues
        and not blockers
    )
    semantic_review = _aggregate_semantic_review(semantic_review_path, EXPECTED_PAIRS)
    summary: dict[str, Any] = {
        "audit": "claude_rewrite_canary_aggregate",
        "audit_version": AUDIT_VERSION,
        "privacy": {
            "text_free_public_summary": True,
            "contains_source_text": False,
            "contains_rewrite_text": False,
            "contains_source_identifiers": False,
            "contains_hashes": False,
            "contains_extracted_phrases": False,
        },
        "scope": {
            "expected_pairs": EXPECTED_PAIRS,
            "received_pairs": len(records),
            "split": batch.split if batch.split in {"train", "validation", "test"} else "other",
            "recipe": batch.recipe if batch.recipe in {"A", "B", "C"} else "other",
        },
        "source_composition": {
            "dataset_counts": _safe_counter(batch.rows, "dataset", DATASETS),
            "task_counts": _safe_counter(batch.rows, "task", TASKS),
            "length_bin_counts": _safe_counter(batch.rows, "length_bin", LENGTH_BINS),
            "rewrite_output_order_counts": _safe_counter(
                batch.rows, "rewrite_output_order", OUTPUT_ORDERS
            ),
            "target_longer_member_counts": _safe_counter(
                batch.rows, "target_longer_member", LONGER_MEMBERS
            ),
        },
        "transport_and_envelope": raw_summary,
        "thresholds": dict(THRESHOLDS),
        "runner_validation": {
            "status_counts": {
                status: status_counts.get(status, 0)
                for status in sorted(runner.TERMINAL_STATUSES | {"unknown"})
            },
            "batch_issue_count": len(batch_issues),
            "writer_issue_record_count": writer_issue_records,
            "issue_group_counts": {
                category: runner_issue_groups.get(category, 0)
                for category in (
                    "identity_or_schema", "protected_content", "length_or_token",
                    "empty_or_identical", "writer_reported", "not_applicable", "other",
                )
            },
            "parsed_artifact": parsed_summary,
        },
        "pair_checks": {
            "word_ratio_summary": _numeric_summary(word_ratios),
            "source_token_similarity_summary": _numeric_summary(source_similarities),
            "pair_token_similarity_summary": _numeric_summary(pair_similarities),
            "absolute_token_gap_summary": _numeric_summary(token_gaps),
            "target_length_direction_match_count": target_direction_matches,
            "structure_match_count": structure_match_count,
            "verbatim_confident_count": verbatim_counts.get("confident", 0),
            "verbatim_hedged_count": verbatim_counts.get("hedged", 0),
            "cross_record_leak_pair_count": sum(
                "cross_record_leakage" in categories for categories in pair_issues
            ),
            "schema_leak_pair_count": sum(
                "schema_leakage" in categories for categories in pair_issues
            ),
            "generic_wrapper_response_count": generic_wrapper_responses,
        },
        "global_shortcut_checks": {
            "maximum_reused_three_token_span_pair_frequency": max_three,
            "maximum_reused_four_plus_token_span_pair_frequency": max_four_plus,
            "maximum_edit_signature_frequency": max_signature,
            "maximum_near_duplicate_delta_cluster_size": max_cluster,
            "first_edit_position_counts": {
                label: {
                    position: position_counts[label].get(position, 0)
                    for position in ("early", "middle", "late")
                }
                for label in ("confident", "hedged")
            },
            "maximum_first_edit_position_bin_count": max_position_bin,
            "maximum_stance_family_pair_frequency": max_stance_family,
        },
        "semantic_review": semantic_review,
        "issue_counts": {
            category: issue_counts.get(category, 0)
            for category in sorted(
                PAIR_ISSUE_CATEGORIES
                | GLOBAL_ISSUE_CATEGORIES
                | ARTIFACT_ISSUE_CATEGORIES
                | {
                    "raw_content_integrity", "raw_batch_identity",
                    "raw_transport_or_isolation", "model_usage_contract",
                    "batch_protocol",
                }
            )
        },
        "decision": {
            "automated_gate_pass": automated_gate_pass,
            "semantic_gate_pass": semantic_review["semantic_gate_pass"],
            "human_certified": semantic_review["human_certified"],
            "scale_authorized": (
                automated_gate_pass
                and semantic_review["semantic_gate_pass"]
                and semantic_review["human_certified"]
            ),
            "blocker_categories": blockers,
        },
    }
    forbidden_values = schema_secrets + parsed_forbidden + [
        str(row.get(field, ""))
        for row in batch.rows
        for field in ("prompt", "original_response")
    ]
    pairs = structured.get("pairs", [])
    if isinstance(pairs, list):
        for item in pairs:
            if not isinstance(item, dict):
                continue
            forbidden_values.extend(
                str(item.get(field, ""))
                for field in ("first_response", "second_response")
            )
            writer_issues = item.get("issues", [])
            if isinstance(writer_issues, list):
                forbidden_values.extend(str(value) for value in writer_issues)
    assert_public_safe(summary, forbidden_values)
    return summary, forbidden_values


def assert_public_safe(summary: dict[str, Any], forbidden_values: Iterable[str]) -> None:
    if set(summary) != TOP_LEVEL_KEYS:
        raise CanaryAuditError("unsafe_summary_shape")
    serialized = json.dumps(summary, ensure_ascii=False, sort_keys=True)
    if HEX64_RE.search(serialized):
        raise CanaryAuditError("unsafe_summary_content")
    for value in forbidden_values:
        if not isinstance(value, str):
            continue
        normalized = value.strip()
        if len(normalized) >= 12 and normalized in serialized:
            raise CanaryAuditError("unsafe_summary_content")


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CanaryAuditError("input_json_invalid") from exc
    if not isinstance(value, dict):
        raise CanaryAuditError("input_json_invalid")
    return value


def _discover_parsed(config: runner.RunnerConfig,
                     first_batch: runner.RewriteBatch) -> Path:
    path = config.output_dir / "parsed" / f"{first_batch.batch_id}.json"
    if not path.is_file():
        raise CanaryAuditError("parsed_artifact_selection_failed")
    return path


def _discover_raw(config: runner.RunnerConfig, first_batch: runner.RewriteBatch,
                  parsed: dict[str, Any] | None = None) -> Path:
    recovery = parsed.get("recovered_from_legacy") if isinstance(parsed, dict) else None
    if isinstance(recovery, dict):
        output_dir = recovery.get("output_dir")
        raw_artifact = recovery.get("raw_artifact")
        if isinstance(output_dir, str) and isinstance(raw_artifact, str):
            private_root = runner.PRIVATE_DATA.resolve()
            candidate = (private_root / output_dir / "raw" / raw_artifact).resolve()
            try:
                candidate.relative_to(private_root)
            except ValueError as exc:
                raise CanaryAuditError("raw_artifact_selection_failed") from exc
            if candidate.is_file():
                return candidate

    candidates: list[Path] = []
    raw_dirs = [config.output_dir / "raw"]
    if not raw_dirs[0].exists():
        raw_dirs.extend(sorted(
            path / "raw"
            for path in config.output_dir.parent.glob("claude_rewrite_1000*")
            if (path / "raw").is_dir()
        ))
    paths = sorted({path for directory in raw_dirs for path in directory.glob("*.json")})
    for path in paths:
        try:
            payload = _read_json(path)
        except CanaryAuditError:
            continue
        if (
            payload.get("batch_id") == first_batch.batch_id
            and payload.get("returncode") == 0
            and payload.get("transport_error") is None
            and isinstance(payload.get("stdout"), str)
            and payload["stdout"].strip()
        ):
            candidates.append(path)
    if len(candidates) != 1:
        raise CanaryAuditError("raw_artifact_selection_failed")
    return candidates[0]


def atomic_write_summary(path: Path, summary: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    with tempfile.NamedTemporaryFile(
        dir=path.parent, prefix=f".{path.name}.", delete=False
    ) as handle:
        temporary = Path(handle.name)
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def audit_files(config_path: Path, raw_path: Path | None, output_path: Path,
                semantic_review_path: Path | None = None,
                parsed_path: Path | None = None) -> dict[str, Any]:
    config = runner.load_config(config_path.resolve())
    rows, _ = runner.validate_frozen_input(
        config.input_path, config.input_manifest_path, config.expected_sources
    )
    batches = runner.make_batches(rows, {}, config.batch_size)
    if not batches or len(batches[0].rows) != EXPECTED_PAIRS:
        raise CanaryAuditError("first_batch_invalid")
    first_batch = batches[0]
    selected_parsed = (
        parsed_path.resolve()
        if parsed_path is not None
        else _discover_parsed(config, first_batch)
    )
    parsed = _read_json(selected_parsed)
    selected_raw = (
        raw_path.resolve()
        if raw_path is not None
        else _discover_raw(config, first_batch, parsed)
    )
    raw = _read_json(selected_raw)
    tokenizer = runner.load_pinned_tokenizer()
    summary, _ = audit_batch(
        first_batch,
        raw,
        config,
        tokenizer,
        semantic_review_path,
        parsed,
        runner.sha256_file(selected_raw),
    )
    atomic_write_summary(output_path.resolve(), summary)
    return summary


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--raw", type=Path, default=None)
    parser.add_argument("--parsed", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--semantic-review", type=Path, default=None)
    args = parser.parse_args(argv)
    try:
        summary = audit_files(
            args.config, args.raw, args.output, args.semantic_review, args.parsed
        )
    except Exception:
        print(json.dumps({
            "error": "canary_audit_failed",
            "private_content_emitted": False,
        }), file=sys.stderr)
        return 2
    print(json.dumps({
        "audit": summary["audit"],
        "automated_gate_pass": summary["decision"]["automated_gate_pass"],
        "semantic_review_status": summary["semantic_review"]["status"],
        "scale_authorized": summary["decision"]["scale_authorized"],
        "private_content_emitted": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
