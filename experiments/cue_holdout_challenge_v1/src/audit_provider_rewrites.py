"""Audit provider rewrites for content drift and certainty-cue shortcuts.

This screen extends ``validate_rewrites.py``.  It is deliberately mechanical:
it can reject obvious template/identity failures and route suspicious rows to
manual review, but it never certifies semantic equivalence or naturalness.

The same command supports a supplied 10-pair microbatch or the frozen 50-pair
grid.  Row-level output is private and contains hashes/metrics rather than
response text; the public output contains aggregate counts only.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Iterable

import validate_rewrites as base


BASE = Path(__file__).resolve().parents[1]
PRIVATE = BASE / "private_data"

EXPECTED_TASKS = {
    "factual_explanation",
    "math_logic",
    "programming",
    "comparison_analysis",
    "summary_judgment",
}
EXPECTED_FAMILIES = {
    "embedded_stance_predicate",
    "modal_force_scope",
    "compositional_polarity",
    "discourse_level_calibration",
    "contrastive_commitment",
}
EXPECTED_DIRECTIONS = {"confident_longer", "hedged_longer"}

WORD_RE = re.compile(r"\b[\w'-]+\b", re.UNICODE)
SENTENCE_RE = re.compile(r"[^.!?\n]+(?:[.!?]+|$)", re.MULTILINE)

# These phrases describe confidence in an answer as an object rather than
# integrating commitment into the answer's substantive syntax.  They are
# intentionally narrow: "I am confident that 42 is the result" is not caught.
GENERIC_REFERENT_RE = re.compile(
    r"\b(?:this|the|my)\s+(?:answer|response|explanation|account|outline|analysis|"
    r"description|solution|summary|statement|write-?up)\b|\bas presented\b|"
    r"\bwhat i (?:have )?(?:written|said|stated)\b|\bthe above\b",
    re.IGNORECASE,
)
GENERIC_COMMITMENT_RE = re.compile(
    r"\b(?:i\s+(?:am|remain|feel|stand|lean|have|hold|endorse|support)|"
    r"i(?:'m|'ve)|my)\b[^.!?\n]{0,90}\b(?:certain|uncertain|confident|"
    r"unconfident|sure|unsure|doubt|firmly|tentative(?:ly)?|provisional(?:ly)?|"
    r"endorse|stand behind|support)\b",
    re.IGNORECASE,
)
FIXED_GENERIC_PHRASES: list[tuple[str, re.Pattern[str]]] = [
    ("certain_about_this", re.compile(
        r"\bi(?: am|'m) (?:fully |entirely |completely )?(?:certain|confident) "
        r"(?:about|in) (?:this|the|my)\b", re.I)),
    ("uncertain_about_this", re.compile(
        r"\bi(?: am|'m) (?:somewhat |rather |quite )?(?:uncertain|unsure) "
        r"(?:about|of) (?:this|the|my)\b", re.I)),
    ("stand_behind_answer", re.compile(
        r"\bi (?:stand|remain) (?:firmly |fully |completely |entirely )*"
        r"(?:behind|committed to) (?:this|the|my)\b", re.I)),
    ("endorse_answer", re.compile(
        r"\bi (?:fully |firmly |tentatively |provisionally )*endorse "
        r"(?:this|the|my)\b", re.I)),
    ("confidence_as_presented", re.compile(
        r"\bi(?: am|'m| remain)[^.!?\n]{0,50}\b(?:certain|uncertain|confident|"
        r"unsure)\b[^.!?\n]{0,50}\bas presented\b", re.I)),
    ("not_sure_generic", re.compile(
        r"\bi(?: am|'m) not (?:fully |entirely |completely )?(?:sure|certain)\b", re.I)),
    ("tentative_answer", re.compile(
        r"\bmy (?:best guess|tentative (?:answer|view|read(?:ing)?)|"
        r"provisional read(?:ing)?)\b", re.I)),
    ("possible_error_disclaimer", re.compile(
        r"\bi (?:may|might|could) be (?:wrong|mistaken)\b", re.I)),
]

OBVIOUS_SHORTCUT_FLAGS = {
    "shared_body_plus_detachable_generic_cue",
    "confident_detachable_generic_certainty_sentence",
    "hedged_detachable_generic_certainty_sentence",
    "very_high_similarity_sparse_edits",
}

VERY_HIGH_SIMILARITY = 0.97
LOW_CHANGED_WORD_MASS = 24
LOW_CHANGED_WORD_FRACTION = 0.03
LONG_LOCAL_EDIT_MAX_CHANGED_FRACTION = 0.20


def _automatic_shortcut_failure(flags: Iterable[str]) -> bool:
    """Return true for shortcuts forbidden by the direct-rewrite protocol."""
    return bool(set(flags) & OBVIOUS_SHORTCUT_FLAGS) or any(
        "_forbidden_generic_phrase:" in flag or "_forbidden_preface:" in flag
        for flag in flags
    )


def _words(value: str) -> list[str]:
    return [match.group(0).casefold() for match in WORD_RE.finditer(value)]


def _sentences(value: str) -> list[str]:
    return [match.group(0).strip() for match in SENTENCE_RE.finditer(value) if match.group(0).strip()]


def _normalise(value: str) -> str:
    return " ".join(_words(value))


def _generic_sentence(value: str) -> bool:
    words = _words(value)
    if not words or len(words) > 22:
        return False
    return bool(GENERIC_REFERENT_RE.search(value) and GENERIC_COMMITMENT_RE.search(value))


def _strip_generic_sentences(value: str) -> tuple[str, int]:
    sentences = _sentences(value)
    retained = [sentence for sentence in sentences if not _generic_sentence(sentence)]
    return _normalise(" ".join(retained)), len(sentences) - len(retained)


def _fixed_phrase_flags(value: str, label: str) -> list[str]:
    return [
        f"{label}_forbidden_generic_phrase:{name}"
        for name, pattern in FIXED_GENERIC_PHRASES
        if pattern.search(value)
    ]


def _diff_metrics(confident: str, hedged: str) -> dict[str, Any]:
    """Return text-only similarity and edit-distribution diagnostics."""
    a = _words(confident)
    b = _words(hedged)
    matcher = SequenceMatcher(a=a, b=b, autojunk=False)
    changed = [opcode for opcode in matcher.get_opcodes() if opcode[0] != "equal"]

    # Map each change to a joint normalized position.  Changes separated by
    # at least 12 words and 12% of the longer response form distinct regions.
    length = max(len(a), len(b), 1)
    centres: list[float] = []
    changed_words = 0
    for _, i1, i2, j1, j2 in changed:
        centres.append((((i1 + i2) / 2) + ((j1 + j2) / 2)) / (2 * length))
        changed_words += (i2 - i1) + (j2 - j1)
    separation = max(12 / length, 0.12)
    regions = 0
    previous: float | None = None
    for centre in sorted(centres):
        if previous is None or centre - previous >= separation:
            regions += 1
        previous = centre

    stripped_a, generic_a = _strip_generic_sentences(confident)
    stripped_b, generic_b = _strip_generic_sentences(hedged)
    shared_after_strip = bool(
        (generic_a or generic_b) and stripped_a and stripped_a == stripped_b
    )
    return {
        "confident_words": len(a),
        "hedged_words": len(b),
        "sequence_similarity": round(matcher.ratio(), 6),
        "changed_word_mass": changed_words,
        "changed_word_fraction": round(changed_words / max(len(a) + len(b), 1), 6),
        "edit_opcode_count": len(changed),
        "separated_edit_regions": regions,
        "confident_generic_sentence_count": generic_a,
        "hedged_generic_sentence_count": generic_b,
        "shared_body_after_generic_sentence_removal": shared_after_strip,
    }


def _shortcut_flags(confident: str, hedged: str, metrics: dict[str, Any]) -> list[str]:
    flags: list[str] = []
    flags.extend(_fixed_phrase_flags(confident, "confident"))
    flags.extend(_fixed_phrase_flags(hedged, "hedged"))
    if metrics["confident_generic_sentence_count"]:
        flags.append("confident_detachable_generic_certainty_sentence")
    if metrics["hedged_generic_sentence_count"]:
        flags.append("hedged_detachable_generic_certainty_sentence")
    if metrics["shared_body_after_generic_sentence_removal"]:
        flags.append("shared_body_plus_detachable_generic_cue")

    longest = max(metrics["confident_words"], metrics["hedged_words"])
    changed_fraction = metrics["changed_word_fraction"]
    # A single diff region is not itself evidence of a shortcut: two genuine
    # rewrites can appear as one large replacement.  Only call the edit local
    # when most of the long response is still shared.
    if (longest > 80 and metrics["separated_edit_regions"] < 2
            and changed_fraction <= LONG_LOCAL_EDIT_MAX_CHANGED_FRACTION):
        flags.append("long_response_edits_not_distributed")

    # Several tiny substitutions spread through an otherwise identical body
    # are still a shared-body shortcut.  Region count must not let them pass.
    sparse_change = (
        metrics["changed_word_mass"] <= LOW_CHANGED_WORD_MASS
        or changed_fraction <= LOW_CHANGED_WORD_FRACTION
    )
    if (metrics["sequence_similarity"] >= VERY_HIGH_SIMILARITY and sparse_change):
        flags.append("very_high_similarity_sparse_edits")
        if metrics["separated_edit_regions"] <= 1:
            flags.append("very_high_similarity_single_local_edit")
    return flags


def _writer_rows(path: Path) -> list[dict[str, Any]]:
    """Read canonical JSONL or the Chat provider's {pairs:[...]} JSON."""
    raw = path.read_text(encoding="utf-8").strip()
    if not raw:
        return []
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return base.read_jsonl(path)
    if isinstance(parsed, dict) and isinstance(parsed.get("pairs"), list):
        rows = parsed["pairs"]
    elif isinstance(parsed, list):
        rows = parsed
    elif isinstance(parsed, dict):
        rows = [parsed]
    else:
        raise ValueError(f"{path}: expected JSONL, an object, a list, or {{'pairs': [...]}}")
    if not all(isinstance(row, dict) for row in rows):
        raise ValueError(f"{path}: every writer record must be an object")
    return rows


def _grid_flags(source_rows: list[dict[str, Any]], writer_rows: list[dict[str, Any]]) -> list[str]:
    flags: list[str] = []
    triples = [
        (row.get("task"), row.get("cue_family"), row.get("length_direction"))
        for row in source_rows
    ]
    if len(triples) != len(set(triples)):
        flags.append("source_grid_duplicate_task_family_direction")
    if any(task not in EXPECTED_TASKS for task, _, _ in triples):
        flags.append("source_grid_unknown_task")
    if any(family not in EXPECTED_FAMILIES for _, family, _ in triples):
        flags.append("source_grid_unknown_cue_family")
    if any(direction not in EXPECTED_DIRECTIONS for _, _, direction in triples):
        flags.append("source_grid_unknown_length_direction")

    if len(source_rows) == 50:
        expected = {
            (task, family, direction)
            for task in EXPECTED_TASKS
            for family in EXPECTED_FAMILIES
            for direction in EXPECTED_DIRECTIONS
        }
        if set(triples) != expected:
            flags.append("full_source_grid_not_5x5x2")
        if len(writer_rows) != 50:
            flags.append("full_writer_count_not_50")
    elif len(source_rows) == 10:
        directions = Counter(row.get("length_direction") for row in source_rows)
        if directions != Counter({"confident_longer": 5, "hedged_longer": 5}):
            flags.append("microbatch_length_direction_not_5_5")
    return flags


def audit_provider_rewrites(source_rows: list[dict[str, Any]],
                            writer_rows: list[dict[str, Any]],
                            tokenizer: Any) -> tuple[list[dict[str, Any]], list[str]]:
    mechanical = base.validate_rewrites(source_rows, writer_rows, tokenizer)
    writer_by_id = {str(row.get("source_id", "")): row for row in writer_rows}
    output: list[dict[str, Any]] = []
    for row in mechanical:
        source_id = str(row.get("source_id") or "")
        writer = writer_by_id.get(source_id)
        extra_flags: list[str] = []
        metrics: dict[str, Any] | None = None
        if writer:
            confident = writer.get("confident_response")
            hedged = writer.get("hedged_response")
            if isinstance(confident, str) and confident.strip() and isinstance(hedged, str) and hedged.strip():
                metrics = _diff_metrics(confident, hedged)
                extra_flags = _shortcut_flags(confident, hedged, metrics)

        all_flags = sorted(set(row.get("flags", [])) | set(extra_flags))
        base_failed = row.get("validation_status") == "fail"
        shortcut_failed = _automatic_shortcut_failure(all_flags)
        if base_failed or shortcut_failed:
            screen_status = "reject"
        elif all_flags:
            screen_status = "manual_review"
        else:
            screen_status = "pass"
        output.append({
            **row,
            "provider_screen_status": screen_status,
            "flags": all_flags,
            "pair_diff_metrics": metrics,
            "semantic_equivalence_certified": False,
            "naturalness_certified": False,
            "human_review_certified": False,
        })
    return output, _grid_flags(source_rows, writer_rows)


def aggregate_summary(rows: list[dict[str, Any]], source_rows: list[dict[str, Any]],
                      writer_count: int, grid_flags: list[str]) -> dict[str, Any]:
    status_counts = Counter(row["provider_screen_status"] for row in rows)
    flag_counts = Counter(flag for row in rows for flag in row.get("flags", []))
    metrics = [row["pair_diff_metrics"] for row in rows if row.get("pair_diff_metrics")]
    def safe_counts(field: str, allowed: set[str]) -> dict[str, int]:
        labels = []
        for row in source_rows:
            value = row.get(field)
            if value in allowed:
                labels.append(value)
            elif value is None or value == "":
                labels.append("<missing>")
            else:
                labels.append("<unknown>")
        return dict(sorted(Counter(labels).items()))

    return {
        "auditor": "provider_rewrite_shortcut_auditor",
        "auditor_version": 2,
        "mode": "full_50" if len(source_rows) == 50 else "partial_batch",
        "source_rows": len(source_rows),
        "writer_rows": writer_count,
        "audit_rows": len(rows),
        "screen_status_counts": dict(sorted(status_counts.items())),
        "flag_counts": dict(sorted(flag_counts.items())),
        "grid_flags": sorted(set(grid_flags)),
        "task_counts": safe_counts("task", EXPECTED_TASKS),
        "cue_family_counts": safe_counts("cue_family", EXPECTED_FAMILIES),
        "length_direction_counts": safe_counts("length_direction", EXPECTED_DIRECTIONS),
        "token_gap_over_3_pairs": sum(
            row.get("absolute_token_gap") is not None and row["absolute_token_gap"] > 3
            for row in rows
        ),
        "long_pairs_with_fewer_than_2_edit_regions": sum(
            metric["confident_words"] > 80 or metric["hedged_words"] > 80
            for metric in metrics
            if metric["separated_edit_regions"] < 2
        ),
        "semantic_equivalence_certified": False,
        "naturalness_certified": False,
        "human_review_certified": False,
    }


def _write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, required=True)
    parser.add_argument("--writer", type=Path, action="append", required=True)
    parser.add_argument("--private-output", type=Path,
                        default=PRIVATE / "provider_rewrite_audit.jsonl")
    parser.add_argument("--summary-output", type=Path,
                        default=BASE / "reports/provider_rewrite_audit_summary.json")
    args = parser.parse_args(argv)

    private_output = args.private_output if args.private_output.is_absolute() else BASE / args.private_output
    summary_output = args.summary_output if args.summary_output.is_absolute() else BASE / args.summary_output
    if not base._inside(private_output, PRIVATE):
        parser.error("row-level output must be written under challenge private_data/")
    if base._inside(summary_output, PRIVATE):
        parser.error("aggregate summary must be written outside private_data/")

    sources = base.read_jsonl(args.sources)
    writers = [row for path in args.writer for row in _writer_rows(path)]
    tokenizer = base.load_pinned_tokenizer()
    rows, grid_flags = audit_provider_rewrites(sources, writers, tokenizer)
    summary = aggregate_summary(rows, sources, len(writers), grid_flags)
    _write_jsonl(private_output, rows)
    _write_json(summary_output, summary)
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 1 if summary["screen_status_counts"].get("reject", 0) or grid_flags else 0


if __name__ == "__main__":
    raise SystemExit(main())
