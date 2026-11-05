#!/usr/bin/env python3
"""Build a deterministic 500-question factual evaluation cohort.

Only TriviaQA questions and accepted-answer aliases are retained. Generated
response fields in the LACIE cache are never copied to the output.
"""

from __future__ import annotations

import hashlib
import html
import json
import os
import re
import tempfile
import unicodedata
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable


REPO = Path(__file__).resolve().parents[2]
EXPERIMENT = Path(__file__).resolve().parent
RAW_SOURCE = REPO / (
    "experiments/factual_source_canary_v1/private_data/"
    "lacie_stanford_original40_review_v1/raw/"
    "LACIE_tqa_10000_mistral_generator_mistral_evaluator.jsonl"
)
RAW_SOURCE_SHA256 = "b6db83dcd94c8781ae7740422928d3f70e8d7b9a836e7f6b0a240232ab718c0c"
SELECTION_SEED = "confidence-output-causal-eval500-20261105-v1"
TARGET_ROWS = 500

EXCLUSION_FILES = (
    "experiments/confidence_probe_scaleup_20261104_v1/data_prep/train_920.jsonl",
    "experiments/confidence_probe_scaleup_20261104_v1/data_prep/dev_156.jsonl",
    "experiments/confidence_probe_scaleup_20261104_v1/data_prep/internal_test_193.jsonl",
    "experiments/confidence_probe_scaleup_20261104_v1/data_prep/external_cf3_113.jsonl",
    "experiments/confidence_probe_guided_lora_lambda_canary_20261104_v1/data/behavior_canary_cue50_46.jsonl",
    "experiments/factual_source_canary_v1/private_data/lacie_stanford_original40_review_v1/LACIE_SOURCE_PAIRS.json",
    "experiments/factual_source_canary_v1/private_data/lacie_stanford_original40_review_v1/LACIE_SOURCE_PAIRS_SCREENED20.json",
    "experiments/factual_source_canary_v1/private_data/linguistic_cas_share_v1/SELECTED_PAIRS.jsonl",
    "experiments/factual_source_canary_v1/private_data/linguistic_cas_share_v1/screening/ONE_PAIR_PER_FACT.jsonl",
    "experiments/factual_source_canary_v1/private_data/linguistic_raw10000_screen_v1/results/ONE_PAIR_PER_FACT.jsonl",
    "experiments/factual_source_canary_v1/private_data/linguistic_raw10000_screen_v1/content_checked_review/ONE_PAIR_PER_FACT.jsonl",
    "experiments/factual_source_canary_v1/private_data/linguistic_raw10000_screen_v1/content_checked_review/FOUR_OF_FIVE_ONE_PAIR_PER_FACT.jsonl",
)

QUESTION_RE = re.compile(r"(?:^|\n)Question:\s*(.+?)\s*\nResponse:", re.DOTALL)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def normalize_question(text: str) -> str:
    text = html.unescape(text)
    text = unicodedata.normalize("NFKC", text)
    return " ".join(text.split()).strip().casefold()


def question_from_prompt(text: str) -> str | None:
    match = QUESTION_RE.search(text)
    if not match:
        return None
    return " ".join(match.group(1).split()).strip()


def read_json_records(path: Path) -> Iterable[Any]:
    if path.suffix == ".jsonl":
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    yield json.loads(line)
    else:
        with path.open("r", encoding="utf-8") as handle:
            yield json.load(handle)


def extract_questions(value: Any) -> Iterable[str]:
    if isinstance(value, dict):
        for key, item in value.items():
            key_norm = key.casefold()
            if isinstance(item, str) and key_norm in {
                "question",
                "source_question",
                "original_question",
            }:
                if item.strip():
                    yield item
            elif isinstance(item, str) and key_norm in {"prompt", "full_prompt"}:
                parsed = question_from_prompt(item)
                if parsed:
                    yield parsed
            else:
                yield from extract_questions(item)
    elif isinstance(value, list):
        for item in value:
            yield from extract_questions(item)


def load_exclusions() -> tuple[set[str], dict[str, int]]:
    excluded: set[str] = set()
    counts: dict[str, int] = {}
    for relative in EXCLUSION_FILES:
        path = REPO / relative
        if not path.exists():
            raise FileNotFoundError(f"required exclusion file is missing: {path}")
        before = len(excluded)
        for record in read_json_records(path):
            for question in extract_questions(record):
                normalized = normalize_question(question)
                if normalized:
                    excluded.add(normalized)
        counts[relative] = len(excluded) - before
    return excluded, counts


def load_source_questions() -> tuple[list[dict[str, Any]], dict[str, int]]:
    groups: dict[str, dict[str, Any]] = {}
    raw_rows = 0
    parse_failures = 0
    invalid_questions = 0
    inconsistent_alias_groups = 0

    with RAW_SOURCE.open("r", encoding="utf-8") as handle:
        for zero_index, line in enumerate(handle):
            if not line.strip():
                continue
            raw_rows += 1
            record = json.loads(line)
            question = question_from_prompt(record.get("prompt", ""))
            try:
                aliases_raw = json.loads(record.get("correct_answers", "[]"))
            except json.JSONDecodeError:
                parse_failures += 1
                continue
            aliases = tuple(dict.fromkeys(str(alias).strip() for alias in aliases_raw if str(alias).strip()))
            if not question or len(question) < 5 or len(question) > 300 or not aliases:
                invalid_questions += 1
                continue
            normalized = normalize_question(question)
            alias_key = tuple(sorted(normalize_question(alias) for alias in aliases))
            if normalized not in groups:
                groups[normalized] = {
                    "question": question,
                    "normalized_question": normalized,
                    "accepted_answers": list(aliases),
                    "alias_key": alias_key,
                    "first_raw_line_index": zero_index,
                    "raw_response_rows": 1,
                    "consistent": True,
                }
            else:
                group = groups[normalized]
                group["raw_response_rows"] += 1
                if group["alias_key"] != alias_key:
                    group["consistent"] = False

    candidates: list[dict[str, Any]] = []
    for group in groups.values():
        if not group["consistent"]:
            inconsistent_alias_groups += 1
            continue
        group.pop("consistent")
        group.pop("alias_key")
        candidates.append(group)

    stats = {
        "raw_rows": raw_rows,
        "unique_normalized_questions": len(groups),
        "eligible_consistent_questions": len(candidates),
        "answer_parse_failures": parse_failures,
        "invalid_question_or_answer_rows": invalid_questions,
        "inconsistent_alias_groups": inconsistent_alias_groups,
    }
    return candidates, stats


def assign_length_bins(candidates: list[dict[str, Any]]) -> None:
    ordered = sorted(candidates, key=lambda row: (len(row["question"]), row["normalized_question"]))
    total = len(ordered)
    for index, row in enumerate(ordered):
        if index < total / 3:
            row["length_bin"] = "short"
        elif index < 2 * total / 3:
            row["length_bin"] = "medium"
        else:
            row["length_bin"] = "long"


def selection_rank(normalized_question: str) -> str:
    return hashlib.sha256(f"{SELECTION_SEED}\0{normalized_question}".encode("utf-8")).hexdigest()


def select_balanced(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    assign_length_bins(candidates)
    targets = {"short": 167, "medium": 166, "long": 167}
    selected: list[dict[str, Any]] = []
    for label in ("short", "medium", "long"):
        bucket = [row for row in candidates if row["length_bin"] == label]
        bucket.sort(key=lambda row: (selection_rank(row["normalized_question"]), row["normalized_question"]))
        if len(bucket) < targets[label]:
            raise RuntimeError(f"insufficient {label} candidates: {len(bucket)}")
        selected.extend(bucket[: targets[label]])
    selected.sort(key=lambda row: (selection_rank(row["normalized_question"]), row["normalized_question"]))
    if len(selected) != TARGET_ROWS:
        raise AssertionError(f"selected {len(selected)} rows instead of {TARGET_ROWS}")
    return selected


def output_row(index: int, row: dict[str, Any]) -> dict[str, Any]:
    normalized = row["normalized_question"]
    question_hash = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    return {
        "accepted_answers": row["accepted_answers"],
        "dataset": "triviaqa_via_lacie",
        "eval_id": f"TQA500-{index:04d}",
        "length_bin": row["length_bin"],
        "provider_generated_answer": False,
        "question": row["question"],
        "question_sha256": question_hash,
        "raw_duplicate_response_rows": row["raw_response_rows"],
        "raw_first_line_index": row["first_raw_line_index"],
        "raw_source_sha256": RAW_SOURCE_SHA256,
        "reference_answer": row["accepted_answers"][0],
        "research_role": "source_disjoint_behavioral_evaluation_only",
        "source_id": f"triviaqa:{question_hash[:20]}",
    }


def exclusive_write(path: Path, payload: bytes, mode: int = 0o600) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, mode)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
    except Exception:
        path.unlink(missing_ok=True)
        raise


def main() -> None:
    actual_hash = sha256_file(RAW_SOURCE)
    if actual_hash != RAW_SOURCE_SHA256:
        raise RuntimeError(f"raw source hash mismatch: {actual_hash}")

    excluded, exclusion_counts = load_exclusions()
    candidates, source_stats = load_source_questions()
    overlap_count = sum(row["normalized_question"] in excluded for row in candidates)
    fresh = [row for row in candidates if row["normalized_question"] not in excluded]
    selected = select_balanced(fresh)
    rows = [output_row(index, row) for index, row in enumerate(selected, start=1)]

    if len({row["eval_id"] for row in rows}) != TARGET_ROWS:
        raise AssertionError("evaluation IDs are not unique")
    if len({row["question_sha256"] for row in rows}) != TARGET_ROWS:
        raise AssertionError("questions are not unique")
    if any(normalize_question(row["question"]) in excluded for row in rows):
        raise AssertionError("selected cohort overlaps an exclusion source")
    if any(row["provider_generated_answer"] for row in rows):
        raise AssertionError("generated answers entered the source cohort")

    cohort_payload = b"".join(canonical_json_bytes(row) for row in rows)
    cohort_hash = hashlib.sha256(cohort_payload).hexdigest()
    bins = {label: sum(row["length_bin"] == label for row in rows) for label in ("short", "medium", "long")}
    freeze = {
        "cohort_bytes": len(cohort_payload),
        "cohort_file": "private_data/EVAL_COHORT_500.jsonl",
        "cohort_sha256": cohort_hash,
        "exclusion_file_new_unique_question_counts": exclusion_counts,
        "exclusion_files": list(EXCLUSION_FILES),
        "fresh_candidate_questions_after_exclusion": len(fresh),
        "length_bin_counts": bins,
        "license_note": "Retain LACIE and TriviaQA attribution; raw cohort remains local/private.",
        "normalized_overlap_with_all_exclusion_files": 0,
        "overlapping_source_questions_excluded": overlap_count,
        "provider_answer_text_imported": False,
        "raw_source_file": str(RAW_SOURCE.relative_to(REPO)),
        "raw_source_sha256": actual_hash,
        "research_role": "source_disjoint_behavioral_evaluation_only",
        "rows": len(rows),
        "selection_seed": SELECTION_SEED,
        "selection_strategy": "stable SHA-256 rank within full-pool question-length tertiles; short/medium/long=167/166/167",
        "source_stats": source_stats,
        "status": "FROZEN_LOCAL_COHORT_READY_FOR_MODEL_OUTPUT_GENERATION",
        "unique_eval_ids": len({row["eval_id"] for row in rows}),
        "unique_normalized_questions": len({normalize_question(row["question"]) for row in rows}),
        "warning": "Public benchmark questions may have appeared in base-model pretraining; this is source-disjoint from the current experiment, not a pretraining non-contamination claim.",
    }

    private_dir = EXPERIMENT / "private_data"
    private_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(private_dir, 0o700)
    cohort_path = private_dir / "EVAL_COHORT_500.jsonl"
    freeze_path = EXPERIMENT / "COHORT_FREEZE.json"
    exclusive_write(cohort_path, cohort_payload)
    exclusive_write(freeze_path, canonical_json_bytes(freeze))
    print(json.dumps({"cohort": str(cohort_path), "freeze": str(freeze_path), **freeze}, indent=2))


if __name__ == "__main__":
    main()
