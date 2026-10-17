"""Deterministic shortcut audit for the factual 12-pair rewrite canary.

The audit is deliberately text-only and model-free.  It rejects construction
shortcuts that previously made confident/hesitant pairs easy to distinguish
without requiring a natural full-response rewrite.  It does *not* certify
semantic equivalence, naturalness, or speaker-certainty direction; those remain
blinded review tasks.

Canonical writer records use ``hesitant_response``.  The historical
``hedged_response`` alias is accepted with an explicit warning so an older
artifact cannot be silently relabelled.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
from canary_binding import build_artifact_binding


BASE = Path(__file__).resolve().parents[1]
PRIVATE = BASE / "private_data"
EXPECTED_CANARY_COUNT = 12

WORD_RE = re.compile(r"\b[^\W_]+(?:[-'’][^\W_]+)*\b", re.UNICODE)
TOKEN_RE = re.compile(r"[^\W_]+(?:[-'’][^\W_]+)*|[^\w\s]", re.UNICODE)
SENTENCE_RE = re.compile(r"[^.!?\n]+(?:[.!?]+|$)", re.MULTILINE)

# A generic self-report names the answer as an object instead of integrating
# the speaker's commitment into its substantive discourse.  The referent and
# commitment expressions must occur in the same short sentence.
GENERIC_REFERENT_RE = re.compile(
    r"\b(?:this|the|my)\s+(?:answer|response|explanation|account|outline|"
    r"analysis|description|solution|summary|statement|write-?up)\b|"
    r"\bas presented\b|\bthe above\b|"
    r"\bwhat i (?:have )?(?:written|said|stated)\b",
    re.IGNORECASE,
)
GENERIC_COMMITMENT_RE = re.compile(
    r"\b(?:i\s+(?:am|remain|feel|stand|lean|have|hold|endorse|support)|"
    r"i(?:'m|'ve|’m|’ve)|my)\b[^.!?\n]{0,100}\b(?:certain|uncertain|"
    r"confident|unconfident|sure|unsure|doubt|firmly|tentative(?:ly)?|"
    r"provisional(?:ly)?|endorse|stand behind|support|best guess)\b",
    re.IGNORECASE,
)
FIXED_GENERIC_RE = re.compile(
    r"\b(?:i (?:may|might|could) be (?:wrong|mistaken)|"
    r"my (?:best guess|tentative (?:answer|view|reading)|provisional reading)|"
    r"i (?:stand|remain) (?:firmly |fully |completely |entirely )*"
    r"(?:behind|committed to) (?:this|the|my)\b)",
    re.IGNORECASE,
)

# This detector is intentionally broad because it is used only to find an
# *exactly reused* novel sentence across independent sources.  A scientific or
# legal modal appearing once is not rejected by this check.
CERTAINTY_CUE_RE = re.compile(
    r"\b(?:certain(?:ly)?|uncertain(?:ly)?|confident(?:ly)?|unconfident|sure|unsure|definitely|"
    r"undoubtedly|clearly|firmly|tentative(?:ly)?|provisional(?:ly)?|"
    r"believe|think|conclude|doubt|lean|likely|probably|perhaps|maybe|"
    r"seem|appear|suggest|may|might|could|must)\b",
    re.IGNORECASE,
)

THRESHOLDS: dict[str, Any] = {
    "expected_canary_pairs": EXPECTED_CANARY_COUNT,
    "very_high_similarity": 0.97,
    "maximum_changed_word_mass_for_sparse_edit": 24,
    "maximum_changed_word_fraction_for_sparse_edit": 0.03,
    "long_response_words": 80,
    "minimum_long_response_edit_regions": 2,
    "maximum_changed_word_fraction_for_single_region_long_edit": 0.20,
    "reused_certainty_sentence_max_sources": 1,
    "label_exclusive_ngram": {
        "1": {"maximum_document_share": 0.50, "minimum_document_count": 3},
        "2": {"maximum_document_share": 0.35, "minimum_document_count": 3},
        "3": {"maximum_document_share": 0.25, "minimum_document_count": 3},
    },
    "expected_length_direction_counts": {
        "confident_longer": 6,
        "hesitant_longer": 6,
    },
    "expected_draft_order_counts": {
        "confident_first": 6,
        "hesitant_first": 6,
    },
    "expected_per_dataset_binary_counts": 2,
}

IDENTITY_FIELDS = (
    "source_hash",
    "original_response_sha256",
    "dataset",
    "cue_family",
    "length_direction",
    "draft_order",
)
ALLOWED_DIRECTIONS = {"confident_longer", "hesitant_longer"}
ALLOWED_DRAFT_ORDERS = {"confident_first", "hesitant_first"}


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _normalize(value: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", value).casefold().split())


def _words(value: str) -> list[str]:
    return [match.group(0).casefold() for match in WORD_RE.finditer(
        unicodedata.normalize("NFKC", value)
    )]


def _token_count(value: str) -> int:
    return len(TOKEN_RE.findall(unicodedata.normalize("NFKC", value)))


def _sentences(value: str) -> list[str]:
    return [
        match.group(0).strip()
        for match in SENTENCE_RE.finditer(value)
        if match.group(0).strip()
    ]


def _ngrams(words: Sequence[str], size: int) -> set[tuple[str, ...]]:
    return {
        tuple(words[index:index + size])
        for index in range(max(0, len(words) - size + 1))
    }


def read_records(path: Path) -> list[dict[str, Any]]:
    """Read JSONL, a JSON list, or a JSON object containing pairs/rewrites."""
    raw = Path(path).read_text(encoding="utf-8").strip()
    if not raw:
        return []
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        rows: list[dict[str, Any]] = []
        for line_number, line in enumerate(raw.splitlines(), 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"{path}:{line_number}: invalid JSON: {exc.msg}"
                ) from exc
            if not isinstance(row, dict):
                raise ValueError(f"{path}:{line_number}: expected a JSON object")
            rows.append(row)
        return rows

    if isinstance(parsed, list):
        rows = parsed
    elif isinstance(parsed, dict) and isinstance(parsed.get("pairs"), list):
        rows = parsed["pairs"]
    elif isinstance(parsed, dict) and isinstance(parsed.get("rewrites"), list):
        rows = parsed["rewrites"]
    elif isinstance(parsed, dict):
        rows = [parsed]
    else:
        raise ValueError(f"{path}: expected JSONL, a list, or an object")
    if not all(isinstance(row, dict) for row in rows):
        raise ValueError(f"{path}: every record must be a JSON object")
    return list(rows)


def _generic_self_report_sentences(value: str) -> int:
    count = 0
    for sentence in _sentences(value):
        if len(_words(sentence)) > 26:
            continue
        if (
            GENERIC_REFERENT_RE.search(sentence)
            and GENERIC_COMMITMENT_RE.search(sentence)
        ) or FIXED_GENERIC_RE.search(sentence):
            count += 1
    return count


def _diff_metrics(confident: str, hesitant: str) -> dict[str, Any]:
    left = _words(confident)
    right = _words(hesitant)
    matcher = SequenceMatcher(a=left, b=right, autojunk=False)
    changed = [opcode for opcode in matcher.get_opcodes() if opcode[0] != "equal"]
    longest = max(len(left), len(right), 1)
    changed_word_mass = 0
    centres: list[float] = []
    for _, left_start, left_end, right_start, right_end in changed:
        changed_word_mass += (left_end - left_start) + (right_end - right_start)
        centres.append(
            (((left_start + left_end) / 2) + ((right_start + right_end) / 2))
            / (2 * longest)
        )
    separation = max(12 / longest, 0.12)
    edit_regions = 0
    previous: float | None = None
    for centre in sorted(centres):
        if previous is None or centre - previous >= separation:
            edit_regions += 1
        previous = centre
    return {
        "confident_words": len(left),
        "hesitant_words": len(right),
        "sequence_similarity": round(matcher.ratio(), 6),
        "changed_word_mass": changed_word_mass,
        "changed_word_fraction": round(
            changed_word_mass / max(len(left) + len(right), 1), 6
        ),
        "edit_opcode_count": len(changed),
        "separated_edit_regions": edit_regions,
    }


def _too_small_edit(metrics: Mapping[str, Any]) -> bool:
    sparse = (
        int(metrics["changed_word_mass"])
        <= int(THRESHOLDS["maximum_changed_word_mass_for_sparse_edit"])
        or float(metrics["changed_word_fraction"])
        <= float(THRESHOLDS["maximum_changed_word_fraction_for_sparse_edit"])
    )
    return (
        float(metrics["sequence_similarity"])
        >= float(THRESHOLDS["very_high_similarity"])
        and sparse
    )


def _sparse_long_edit(metrics: Mapping[str, Any]) -> bool:
    longest = max(
        int(metrics["confident_words"]), int(metrics["hesitant_words"])
    )
    return (
        longest > int(THRESHOLDS["long_response_words"])
        and int(metrics["separated_edit_regions"])
        < int(THRESHOLDS["minimum_long_response_edit_regions"])
        and float(metrics["changed_word_fraction"])
        <= float(THRESHOLDS["maximum_changed_word_fraction_for_single_region_long_edit"])
    )


def _extract_protected_spans(source: Mapping[str, Any]) -> tuple[list[str], bool]:
    """Return literal protected spans and whether semantic review is required.

    ``protected_qualifiers`` are semantic descriptions and are intentionally not
    substring-matched.  Exact matching is performed only for the optional
    ``protected_spans`` field.
    """
    raw_spans = source.get("protected_spans", [])
    if raw_spans is None:
        raw_spans = []
    if not isinstance(raw_spans, list):
        raise ValueError("protected_spans must be a list when supplied")
    spans: list[str] = []
    for item in raw_spans:
        if isinstance(item, str):
            text = item
        elif isinstance(item, Mapping) and isinstance(item.get("text"), str):
            text = str(item["text"])
        else:
            raise ValueError("each protected span must be a string or {text: ...}")
        if not text:
            raise ValueError("protected spans cannot be empty")
        spans.append(text)
    qualifiers = source.get("protected_qualifiers", [])
    review_required = bool(isinstance(qualifiers, list) and qualifiers)
    return spans, review_required


def _protected_span_flags(
    original: str, responses: Mapping[str, str], spans: Sequence[str]
) -> list[str]:
    flags: list[str] = []
    for span in spans:
        expected_count = original.count(span)
        if expected_count == 0:
            flags.append("protected_span_missing_from_source")
            continue
        for label, response in responses.items():
            if response.count(span) != expected_count:
                flags.append(f"{label}_protected_span_count_changed")
    return sorted(set(flags))


def _novel_cue_sentences(original: str, response: str) -> set[str]:
    source_sentences = {_normalize(sentence) for sentence in _sentences(original)}
    return {
        normalized
        for sentence in _sentences(response)
        if (normalized := _normalize(sentence))
        and normalized not in source_sentences
        and CERTAINTY_CUE_RE.search(sentence)
    }


def _novel_ngrams(original: str, response: str, size: int) -> set[tuple[str, ...]]:
    return _ngrams(_words(response), size) - _ngrams(_words(original), size)


def _writer_hesitant_text(writer: Mapping[str, Any]) -> tuple[Any, list[str], list[str]]:
    canonical = writer.get("hesitant_response")
    legacy = writer.get("hedged_response")
    flags: list[str] = []
    warnings: list[str] = []
    if canonical is not None and legacy is not None:
        if canonical != legacy:
            flags.append("conflicting_hesitant_and_hedged_fields")
        else:
            warnings.append("redundant_legacy_hedged_response_alias")
        return canonical, flags, warnings
    if canonical is not None:
        return canonical, flags, warnings
    if legacy is not None:
        warnings.append("legacy_hedged_response_alias_used")
        return legacy, flags, warnings
    return None, flags, warnings


def _identity_flags(source: Mapping[str, Any], writer: Mapping[str, Any]) -> list[str]:
    flags: list[str] = []
    original = source.get("original_response")
    if not isinstance(original, str) or not original.strip():
        return ["source_original_response_missing"]
    computed_digest = sha256_text(original)
    recorded_digest = source.get("original_response_sha256")
    if recorded_digest is not None and recorded_digest != computed_digest:
        flags.append("source_original_response_sha256_invalid")
    if writer.get("original_response_sha256") != computed_digest:
        flags.append("writer_original_response_sha256_mismatch")
    for field in IDENTITY_FIELDS:
        expected = computed_digest if field == "original_response_sha256" else source.get(field)
        observed = writer.get(field)
        if field == "original_response_sha256":
            continue
        if expected is not None and observed != expected:
            flags.append(f"writer_{field}_mismatch")
    return flags


def _base_row(source: Mapping[str, Any], flags: Iterable[str]) -> dict[str, Any]:
    return {
        "source_id": source.get("source_id"),
        "dataset": source.get("dataset"),
        "flags": sorted(set(flags)),
        "warnings": [],
        "pair_metrics": None,
        "length_direction": source.get("length_direction"),
        "actual_length_direction": None,
        "draft_order": source.get("draft_order"),
        "semantic_qualifier_review_required": False,
        "shortcut_status": "reject",
    }


def audit_factual_rewrites(
    source_rows: Sequence[dict[str, Any]],
    writer_rows: Sequence[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[str], dict[str, Any]]:
    """Audit paired rewrites and return private rows, batch flags, diagnostics."""
    source_counts = Counter(str(row.get("source_id") or "") for row in source_rows)
    writer_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for writer in writer_rows:
        writer_groups[str(writer.get("source_id") or "")].append(writer)

    audit_rows: list[dict[str, Any]] = []
    internal: dict[str, dict[str, Any]] = {}
    seen_sources: set[str] = set()
    for source in sorted(source_rows, key=lambda row: str(row.get("source_id") or "")):
        source_id = str(source.get("source_id") or "")
        flags: list[str] = []
        warnings: list[str] = []
        if not source_id:
            flags.append("source_id_missing")
        elif source_id in seen_sources or source_counts[source_id] > 1:
            flags.append("duplicate_source_id")
        seen_sources.add(source_id)
        matches = writer_groups.get(source_id, [])
        if not matches:
            flags.append("writer_record_missing")
            audit_rows.append(_base_row(source, flags))
            continue
        if len(matches) > 1:
            flags.append("duplicate_writer_source_id")
        writer = matches[0]
        flags.extend(_identity_flags(source, writer))

        confident = writer.get("confident_response")
        hesitant, alias_flags, alias_warnings = _writer_hesitant_text(writer)
        flags.extend(alias_flags)
        warnings.extend(alias_warnings)
        responses: dict[str, str] = {}
        for label, value in (("confident", confident), ("hesitant", hesitant)):
            if not isinstance(value, str) or not value.strip():
                flags.append(f"{label}_response_missing")
            else:
                responses[label] = value

        original = source.get("original_response")
        original = original if isinstance(original, str) else ""
        for label, response in responses.items():
            if _normalize(response) == _normalize(original):
                flags.append(f"{label}_verbatim_source")
            generic_count = _generic_self_report_sentences(response)
            if generic_count:
                flags.append(f"{label}_detachable_generic_self_report")

        metrics: dict[str, Any] | None = None
        actual_direction: str | None = None
        if len(responses) == 2:
            if _normalize(responses["confident"]) == _normalize(responses["hesitant"]):
                flags.append("identical_pair")
            metrics = _diff_metrics(responses["confident"], responses["hesitant"])
            if _too_small_edit(metrics):
                flags.append("very_high_similarity_sparse_edit")
            if _sparse_long_edit(metrics):
                flags.append("long_response_sparse_edit_regions")
            confident_tokens = _token_count(responses["confident"])
            hesitant_tokens = _token_count(responses["hesitant"])
            if confident_tokens > hesitant_tokens:
                actual_direction = "confident_longer"
            elif hesitant_tokens > confident_tokens:
                actual_direction = "hesitant_longer"
            else:
                actual_direction = "tie"
            intended_direction = source.get("length_direction")
            if intended_direction is not None:
                if intended_direction not in ALLOWED_DIRECTIONS:
                    flags.append("invalid_length_direction_metadata")
                elif actual_direction != intended_direction:
                    flags.append("length_direction_not_met")

        try:
            protected_spans, semantic_review = _extract_protected_spans(source)
        except ValueError:
            protected_spans, semantic_review = [], bool(source.get("protected_qualifiers"))
            flags.append("invalid_protected_span_schema")
        if responses and protected_spans:
            flags.extend(_protected_span_flags(original, responses, protected_spans))

        if isinstance(writer.get("issues"), list) and writer.get("issues"):
            warnings.append("writer_reported_issues_present")

        row = {
            "source_id": source.get("source_id"),
            "dataset": source.get("dataset"),
            "flags": sorted(set(flags)),
            "warnings": sorted(set(warnings)),
            "pair_metrics": metrics,
            "length_direction": source.get("length_direction"),
            "actual_length_direction": actual_direction,
            "draft_order": source.get("draft_order"),
            "semantic_qualifier_review_required": semantic_review,
            "shortcut_status": "reject" if flags else "pass",
        }
        audit_rows.append(row)
        if len(responses) == 2:
            internal[source_id] = {
                "original": original,
                "confident": responses["confident"],
                "hesitant": responses["hesitant"],
            }

    for source_id, writers in sorted(writer_groups.items()):
        if source_id not in seen_sources:
            for _ in writers:
                audit_rows.append({
                    "source_id": source_id or None,
                    "dataset": None,
                    "flags": ["writer_source_id_unknown" if source_id else "writer_source_id_missing"],
                    "warnings": [],
                    "pair_metrics": None,
                    "length_direction": None,
                    "actual_length_direction": None,
                    "draft_order": None,
                    "semantic_qualifier_review_required": False,
                    "shortcut_status": "reject",
                })

    rows_by_id = {
        str(row.get("source_id")): row
        for row in audit_rows
        if row.get("source_id") is not None
    }
    batch_flags: list[str] = []

    # Reject a certainty-bearing sentence repeated across independent sources.
    sentence_occurrences: dict[str, set[tuple[str, str]]] = defaultdict(set)
    for source_id, texts in internal.items():
        for label in ("confident", "hesitant"):
            for sentence in _novel_cue_sentences(texts["original"], texts[label]):
                sentence_occurrences[sentence].add((source_id, label))
    repeated_sentence_groups = 0
    for occurrences in sentence_occurrences.values():
        sources = {source_id for source_id, _ in occurrences}
        if len(sources) > int(THRESHOLDS["reused_certainty_sentence_max_sources"]):
            repeated_sentence_groups += 1
            for source_id in sources:
                if source_id in rows_by_id:
                    rows_by_id[source_id]["flags"].append("reused_certainty_sentence")
    if repeated_sentence_groups:
        batch_flags.append("reused_certainty_sentence")

    # Detect label-exclusive, source-novel n-grams concentrated across records.
    ngram_diagnostics: dict[str, dict[str, Any]] = {}
    novel_by_label: dict[str, dict[int, dict[str, set[tuple[str, ...]]]]] = {
        label: {size: {} for size in (1, 2, 3)}
        for label in ("confident", "hesitant")
    }
    for source_id, texts in internal.items():
        for label in ("confident", "hesitant"):
            for size in (1, 2, 3):
                novel_by_label[label][size][source_id] = _novel_ngrams(
                    texts["original"], texts[label], size
                )

    for label, other in (("confident", "hesitant"), ("hesitant", "confident")):
        ngram_diagnostics[label] = {}
        for size in (1, 2, 3):
            own_sets = novel_by_label[label][size]
            other_union: set[tuple[str, ...]] = set()
            for values in novel_by_label[other][size].values():
                other_union.update(values)
            frequencies: Counter[tuple[str, ...]] = Counter()
            for values in own_sets.values():
                frequencies.update(values - other_union)
            threshold = THRESHOLDS["label_exclusive_ngram"][str(size)]
            document_count = len(own_sets)
            violating = {
                ngram for ngram, count in frequencies.items()
                if count >= int(threshold["minimum_document_count"])
                and count / max(document_count, 1)
                > float(threshold["maximum_document_share"])
            }
            maximum = max(frequencies.values(), default=0)
            ngram_diagnostics[label][str(size)] = {
                "document_count": document_count,
                "maximum_exclusive_document_frequency": maximum,
                "maximum_exclusive_document_share": round(
                    maximum / max(document_count, 1), 6
                ),
                "violating_ngram_count": len(violating),
                "maximum_allowed_share": threshold["maximum_document_share"],
                "minimum_document_count": threshold["minimum_document_count"],
            }
            if violating:
                unit = {1: "unigram", 2: "bigram", 3: "trigram"}[size]
                flag = f"{label}_label_exclusive_{unit}_concentration"
                batch_flags.append(flag)
                for source_id, values in own_sets.items():
                    if values & violating and source_id in rows_by_id:
                        rows_by_id[source_id]["flags"].append(flag)

    for row in audit_rows:
        row["flags"] = sorted(set(row["flags"]))
        row["shortcut_status"] = "reject" if row["flags"] else "pass"

    # Enforce the preregistered 6/6 longer-member balance only when the complete
    # canary supplies length-direction metadata.  Missing metadata remains
    # visible rather than being inferred from the text.
    direction_values = [row.get("length_direction") for row in source_rows]
    direction_available = bool(direction_values) and all(
        value in ALLOWED_DIRECTIONS for value in direction_values
    )
    direction_partial = any(value is not None for value in direction_values) and not direction_available
    direction_counts = Counter(
        str(value) for value in direction_values if value in ALLOWED_DIRECTIONS
    )
    if direction_partial:
        batch_flags.append("length_direction_metadata_partial_or_invalid")
    if len(source_rows) == EXPECTED_CANARY_COUNT and direction_available:
        expected = Counter(THRESHOLDS["expected_length_direction_counts"])
        if direction_counts != expected:
            batch_flags.append("length_direction_not_6_6")

    datasets = sorted({
        str(row.get("dataset")) for row in source_rows if row.get("dataset") is not None
    })
    direction_by_dataset: dict[str, dict[str, int]] = {}
    if len(source_rows) == EXPECTED_CANARY_COUNT and direction_available:
        expected_per_dataset = Counter({
            value: int(THRESHOLDS["expected_per_dataset_binary_counts"])
            for value in sorted(ALLOWED_DIRECTIONS)
        })
        for dataset in datasets:
            counts = Counter(
                str(row.get("length_direction"))
                for row in source_rows
                if str(row.get("dataset")) == dataset
                and row.get("length_direction") in ALLOWED_DIRECTIONS
            )
            direction_by_dataset[dataset] = dict(sorted(counts.items()))
            if counts != expected_per_dataset:
                batch_flags.append("length_direction_not_2_2_per_dataset")

    draft_values = [row.get("draft_order") for row in source_rows]
    draft_available = bool(draft_values) and all(
        value in ALLOWED_DRAFT_ORDERS for value in draft_values
    )
    draft_partial = any(value is not None for value in draft_values) and not draft_available
    draft_counts = Counter(
        str(value) for value in draft_values if value in ALLOWED_DRAFT_ORDERS
    )
    draft_by_dataset: dict[str, dict[str, int]] = {}
    if draft_partial:
        batch_flags.append("draft_order_metadata_partial_or_invalid")
    if len(source_rows) == EXPECTED_CANARY_COUNT and draft_available:
        expected_draft = Counter(THRESHOLDS["expected_draft_order_counts"])
        if draft_counts != expected_draft:
            batch_flags.append("draft_order_not_6_6")
        expected_per_dataset = Counter({
            value: int(THRESHOLDS["expected_per_dataset_binary_counts"])
            for value in sorted(ALLOWED_DRAFT_ORDERS)
        })
        for dataset in datasets:
            counts = Counter(
                str(row.get("draft_order"))
                for row in source_rows
                if str(row.get("dataset")) == dataset
                and row.get("draft_order") in ALLOWED_DRAFT_ORDERS
            )
            draft_by_dataset[dataset] = dict(sorted(counts.items()))
            if counts != expected_per_dataset:
                batch_flags.append("draft_order_not_2_2_per_dataset")
    if len(source_rows) != EXPECTED_CANARY_COUNT:
        batch_flags.append("canary_source_count_not_12")
    if len(writer_rows) != EXPECTED_CANARY_COUNT:
        batch_flags.append("canary_writer_count_not_12")

    diagnostics = {
        "reused_certainty_sentence_group_count": repeated_sentence_groups,
        "label_exclusive_ngram": ngram_diagnostics,
        "length_direction": {
            "metadata_available": direction_available,
            "metadata_partial_or_invalid": direction_partial,
            "counts": dict(sorted(direction_counts.items())),
            "expected_counts_if_complete": dict(
                THRESHOLDS["expected_length_direction_counts"]
            ),
            "counts_by_dataset": direction_by_dataset,
            "counting_method_for_actual_direction": "unicode_regex_tokens",
        },
        "draft_order": {
            "metadata_available": draft_available,
            "metadata_partial_or_invalid": draft_partial,
            "counts": dict(sorted(draft_counts.items())),
            "expected_counts_if_complete": dict(
                THRESHOLDS["expected_draft_order_counts"]
            ),
            "counts_by_dataset": draft_by_dataset,
        },
    }
    return audit_rows, sorted(set(batch_flags)), diagnostics


def aggregate_summary(
    audit_rows: Sequence[dict[str, Any]],
    batch_flags: Sequence[str],
    diagnostics: Mapping[str, Any],
    source_count: int,
    writer_count: int,
    artifact_binding: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    status_counts = Counter(str(row.get("shortcut_status")) for row in audit_rows)
    flag_counts = Counter(
        str(flag) for row in audit_rows for flag in row.get("flags", [])
    )
    warning_counts = Counter(
        str(warning) for row in audit_rows for warning in row.get("warnings", [])
    )
    complete = source_count == writer_count == EXPECTED_CANARY_COUNT
    automatic_pass = bool(
        complete
        and not batch_flags
        and status_counts.get("reject", 0) == 0
        and len(audit_rows) == EXPECTED_CANARY_COUNT
    )
    semantic_review_required_count = sum(
        bool(row.get("semantic_qualifier_review_required")) for row in audit_rows
    )
    return {
        "audit": "factual_direct_pair_shortcut_audit",
        "audit_version": 1,
        "thresholds": THRESHOLDS,
        "scope": {
            "expected_pairs": EXPECTED_CANARY_COUNT,
            "source_rows": source_count,
            "writer_rows": writer_count,
            "audit_rows": len(audit_rows),
        },
        "artifact_binding": dict(artifact_binding) if artifact_binding else None,
        "status_counts": dict(sorted(status_counts.items())),
        "flag_counts": dict(sorted(flag_counts.items())),
        "warning_counts": dict(sorted(warning_counts.items())),
        "batch_flags": sorted(set(batch_flags)),
        "diagnostics": diagnostics,
        "semantic_qualifier_review_required_count": semantic_review_required_count,
        "decision": {
            "automatic_shortcut_gate_pass": automatic_pass,
            "blind_semantic_and_direction_review_still_required": True,
            "naturalness_certified": False,
            "semantic_equivalence_certified": False,
            "human_review_certified": False,
            "activation_scoring_authorized": False,
        },
        "privacy": {
            "contains_source_or_rewrite_text": False,
            "contains_triggering_phrases_or_ngrams": False,
            "contains_source_ids": False,
            "row_level_report_should_remain_private": True,
        },
    }


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, required=True)
    parser.add_argument("--rewrites", type=Path, action="append", required=True)
    parser.add_argument(
        "--private-output",
        type=Path,
        default=PRIVATE / "factual_rewrite_shortcut_audit.json",
    )
    parser.add_argument(
        "--summary-output",
        type=Path,
        default=BASE / "results" / "factual_rewrite_shortcut_audit_summary.json",
    )
    args = parser.parse_args(argv)

    sources = read_records(args.sources)
    writers = [row for path in args.rewrites for row in read_records(path)]
    rows, batch_flags, diagnostics = audit_factual_rewrites(sources, writers)
    artifact_binding = None
    try:
        artifact_binding = build_artifact_binding(
            sources, writers, require_matching_ids=False
        )
    except ValueError:
        batch_flags = sorted(set((*batch_flags, "artifact_binding_unavailable")))
    summary = aggregate_summary(
        rows,
        batch_flags,
        diagnostics,
        len(sources),
        len(writers),
        artifact_binding=artifact_binding,
    )
    _write_json(args.private_output, {
        "audit": summary["audit"],
        "audit_version": summary["audit_version"],
        "batch_flags": batch_flags,
        "rows": rows,
    })
    _write_json(args.summary_output, summary)
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0 if summary["decision"]["automatic_shortcut_gate_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
