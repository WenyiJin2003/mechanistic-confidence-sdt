#!/usr/bin/env python3
"""Build a deterministic, text-private audit of factual source datasets."""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import random
import re
import statistics
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
DATASET_SERVER = "https://datasets-server.huggingface.co/rows"
WORD_RE = re.compile(r"\b[\w][\w'\-’]*\b", re.UNICODE)
SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")
SPACE_RE = re.compile(r"\s+")
SOURCE_HEDGE_RE = re.compile(
    r"\b(?:may|might|could|possibly|perhaps|unclear|uncertain|unknown|"
    r"suggests?|appears?|approximately|estimated?|likely|unlikely)\b",
    re.IGNORECASE,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument(
        "--output-tag",
        help=(
            "Write a separate private candidate directory and prefixed public artifacts. "
            "Omit this option to reproduce the locked pilot audit paths."
        ),
    )
    return parser.parse_args()


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    text = html.unescape(str(value)).replace("\u00a0", " ")
    text = re.sub(r"(?<=[a-z0-9)])\.(?=[A-Z])", ". ", text)
    return SPACE_RE.sub(" ", text).strip()


def stable_hash(*values: Any) -> str:
    payload = "\n\x1f\n".join(normalize_text(value) for value in values)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def word_count(text: str) -> int:
    return len(WORD_RE.findall(text))


def sentence_count(text: str) -> int:
    text = normalize_text(text)
    if not text:
        return 0
    return max(1, len([part for part in SENTENCE_RE.split(text) if part.strip()]))


def percentile(values: list[int], q: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    position = (len(ordered) - 1) * q
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return round(ordered[lower] * (1 - fraction) + ordered[upper] * fraction, 2)


def fetch_json(url: str, cache_path: Path, refresh: bool) -> dict[str, Any]:
    if cache_path.exists() and not refresh:
        return json.loads(cache_path.read_text(encoding="utf-8"))
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={"User-Agent": "source-audit-v1"})
    with urllib.request.urlopen(request, timeout=120) as response:
        payload = json.load(response)
    cache_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return payload


def row_url(spec: dict[str, Any], offset: int, length: int) -> str:
    query = urllib.parse.urlencode(
        {
            "dataset": spec["hub_id"],
            "config": spec["config"],
            "split": spec["split"],
            "offset": offset,
            "length": length,
        }
    )
    return f"{DATASET_SERVER}?{query}"


def fetch_dataset_rows(
    name: str,
    spec: dict[str, Any],
    seed: int,
    raw_dir: Path,
    refresh: bool,
) -> list[tuple[int, dict[str, Any]]]:
    first_path = raw_dir / f"{name}_probe.json"
    first = fetch_json(row_url(spec, 0, 1), first_path, refresh)
    total = int(first["num_rows_total"])
    chunk_length = min(int(spec["chunk_length"]), total)
    rng = random.Random(f"{seed}:{name}")
    max_start = max(0, total - chunk_length)
    starts = {0}
    while len(starts) < min(int(spec["chunk_count"]), max_start + 1):
        starts.add(rng.randint(0, max_start))

    rows: dict[int, dict[str, Any]] = {}
    for start in sorted(starts):
        cache_path = raw_dir / f"{name}_rows_{start}_{chunk_length}.json"
        payload = fetch_json(row_url(spec, start, chunk_length), cache_path, refresh)
        for entry in payload.get("rows", []):
            rows[int(entry["row_idx"])] = entry["row"]
    return sorted(rows.items())


def flatten_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        cleaned = normalize_text(value)
        return [cleaned] if cleaned else []
    if isinstance(value, dict):
        result: list[str] = []
        for child in value.values():
            result.extend(flatten_strings(child))
        return result
    if isinstance(value, (list, tuple)):
        result = []
        for child in value:
            result.extend(flatten_strings(child))
        return result
    return []


def candidate(
    *,
    dataset: str,
    source_id: str,
    group_id: str,
    question: str,
    response: str,
    evidence: str,
    source_locator: str,
    license_name: str,
    metadata: dict[str, Any],
) -> dict[str, Any]:
    response = normalize_text(response)
    evidence = normalize_text(evidence)
    return {
        "dataset": dataset,
        "source_id": source_id,
        "group_id": group_id,
        "question": normalize_text(question),
        "original_response": response,
        "evidence": evidence,
        "source_locator": normalize_text(source_locator),
        "license": license_name,
        "metadata": metadata,
    }


def parse_asqa(row_idx: int, row: dict[str, Any], spec: dict[str, Any]) -> Iterable[dict[str, Any]]:
    annotations = row.get("annotations") or []
    if not annotations:
        return
    answer = annotations[0].get("long_answer", "")
    knowledge = annotations[0].get("knowledge") or []
    evidence_parts = [piece.get("content") for piece in knowledge if piece.get("content")]
    qa_pairs = row.get("qa_pairs") or []
    for pair in qa_pairs:
        disambiguated_question = normalize_text(pair.get("question"))
        short_answers = "; ".join(flatten_strings(pair.get("short_answers") or []))
        context = normalize_text(pair.get("context"))
        qa_evidence = f"Question: {disambiguated_question} Answer: {short_answers}"
        if context and context.lower() != "no context provided":
            qa_evidence += f" Context: {context}"
        evidence_parts.append(qa_evidence)
    pages = sorted(
        {
            normalize_text(page.get("title"))
            for page in (row.get("wikipages") or [])
            if page.get("title")
        }
    )
    page_key = "|".join(pages) or str(row.get("sample_id", row_idx))
    yield candidate(
        dataset="asqa",
        source_id=f"asqa:{row.get('sample_id', row_idx)}",
        group_id=f"asqa-pages:{stable_hash(page_key)[:16]}",
        question=row.get("ambiguous_question", ""),
        response=answer,
        evidence="\n".join(filter(None, evidence_parts)),
        source_locator="; ".join(pages),
        license_name=spec["license"],
        metadata={"row_idx": row_idx, "wikipedia_pages": pages},
    )


def parse_fetaqa(row_idx: int, row: dict[str, Any], spec: dict[str, Any]) -> Iterable[dict[str, Any]]:
    table = row.get("table_array") or []
    highlighted = row.get("highlighted_cell_ids") or []
    highlighted_by_row: dict[int, list[int]] = {}
    for coordinate in highlighted:
        try:
            r, c = int(coordinate[0]), int(coordinate[1])
            _ = table[r][c]
            highlighted_by_row.setdefault(r, []).append(c)
        except (IndexError, TypeError, ValueError):
            continue
    prefix_rows: list[str] = []
    if table:
        first_selected_row = min(highlighted_by_row, default=1)
        prefix_limit = min(max(first_selected_row, 1), 2, len(table))
        for prefix_idx in range(prefix_limit):
            prefix_values = " | ".join(
                f"[{c}] {normalize_text(value)}" for c, value in enumerate(table[prefix_idx])
            )
            prefix_rows.append(f"Table prefix row {prefix_idx}: {prefix_values}")
    evidence_rows: list[str] = []
    for r, selected_columns in sorted(highlighted_by_row.items()):
        full_row = " | ".join(
            f"[{c}] {normalize_text(value)}" for c, value in enumerate(table[r])
        )
        selected = ",".join(str(c) for c in sorted(set(selected_columns)))
        evidence_rows.append(f"Selected row {r} (highlighted columns {selected}): {full_row}")
    table_descriptor = ": ".join(
        filter(
            None,
            [normalize_text(row.get("table_page_title")), normalize_text(row.get("table_section_title"))],
        )
    )
    table_source = normalize_text(row.get("table_source_json")) or f"row-{row_idx}"
    yield candidate(
        dataset="fetaqa",
        source_id=f"fetaqa:{row.get('feta_id', row_idx)}",
        group_id=f"fetaqa-table:{stable_hash(table_source)[:16]}",
        question=row.get("question", ""),
        response=row.get("answer", ""),
        evidence=f"Table {table_descriptor}. " + " ".join(prefix_rows + evidence_rows),
        source_locator=row.get("page_wikipedia_url", ""),
        license_name=spec["license"],
        metadata={
            "row_idx": row_idx,
            "table_source": table_source,
            "table_title": row.get("table_page_title", ""),
            "table_section": row.get("table_section_title", ""),
        },
    )


def parse_qasper(row_idx: int, row: dict[str, Any], spec: dict[str, Any]) -> Iterable[dict[str, Any]]:
    paper_id = normalize_text(row.get("id")) or f"row-{row_idx}"
    title = normalize_text(row.get("title"))
    abstract = normalize_text(row.get("abstract"))
    full_text = "\n".join(flatten_strings(row.get("full_text") or {}))
    if not abstract or not full_text:
        return
    yield candidate(
        dataset="qasper",
        source_id=f"qasper-paper:{paper_id}",
        group_id=f"qasper-paper:{paper_id}",
        question=f"What does the paper titled '{title}' report?",
        response=abstract,
        evidence=full_text,
        source_locator=f"arXiv:{paper_id}",
        license_name=spec["license"],
        metadata={
            "row_idx": row_idx,
            "paper_id": paper_id,
            "paper_title": title,
            "source_response_type": "author_abstract",
        },
    )


def parse_billsum(row_idx: int, row: dict[str, Any], spec: dict[str, Any]) -> Iterable[dict[str, Any]]:
    title = normalize_text(row.get("title"))
    bill_text = normalize_text(row.get("text"))
    bill_hash = stable_hash(title, bill_text)[:16]
    yield candidate(
        dataset="billsum",
        source_id=f"billsum:{bill_hash}",
        group_id=f"billsum-bill:{bill_hash}",
        question=f"What does this bill do? {title}",
        response=row.get("summary", ""),
        evidence=bill_text,
        source_locator=title,
        license_name=spec["license"],
        metadata={"row_idx": row_idx, "title": title},
    )


PARSERS = {
    "asqa": parse_asqa,
    "fetaqa": parse_fetaqa,
    "qasper": parse_qasper,
    "billsum": parse_billsum,
}


def enrich(item: dict[str, Any], screen: dict[str, Any]) -> dict[str, Any]:
    words = word_count(item["original_response"])
    sentences = sentence_count(item["original_response"])
    evidence_words = word_count(item["evidence"])
    blocking_flags: list[str] = []
    review_flags: list[str] = []
    if words < int(screen["minimum_words"]):
        blocking_flags.append("short_response")
    if words > int(screen["maximum_words"]):
        blocking_flags.append("long_response")
    if sentences < int(screen["minimum_sentences"]):
        blocking_flags.append("single_sentence")
    if screen.get("require_evidence") and evidence_words == 0:
        blocking_flags.append("missing_evidence")
    if SOURCE_HEDGE_RE.search(item["original_response"]):
        review_flags.append("preserve_source_qualification")
    flags = blocking_flags + review_flags
    item.update(
        {
            "word_count": words,
            "sentence_count": sentences,
            "evidence_word_count": evidence_words,
            "source_hash": stable_hash(
                item["dataset"], item["question"], item["original_response"], item["evidence"]
            ),
            "heuristic_flags": flags,
            "blocking_flags": blocking_flags,
            "review_flags": review_flags,
            "heuristic_pass": not blocking_flags,
            "human_decision": "pending",
            "human_claim_count": "",
            "human_content_self_contained": "",
            "human_evidence_support": "",
            "human_rewrite_suitability": "",
            "human_notes": "",
        }
    )
    return item


def choose_candidates(
    name: str,
    parsed: list[dict[str, Any]],
    limit: int,
    seed: int,
) -> list[dict[str, Any]]:
    by_source: dict[str, dict[str, Any]] = {}
    for item in parsed:
        by_source.setdefault(item["source_id"], item)
    values = list(by_source.values())
    values.sort(
        key=lambda item: (
            not item["heuristic_pass"],
            stable_hash(seed, name, item["source_id"]),
        )
    )
    return values[:limit]


def write_jsonl(path: Path, records: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def build_summary(
    config: dict[str, Any],
    candidates: list[dict[str, Any]],
    fetched_counts: dict[str, int],
    full_text_location: str,
) -> dict[str, Any]:
    by_dataset: dict[str, Any] = {}
    for name in config["datasets"]:
        rows = [item for item in candidates if item["dataset"] == name]
        lengths = [item["word_count"] for item in rows]
        flag_counts = Counter(flag for item in rows for flag in item["heuristic_flags"])
        blocking_flag_counts = Counter(flag for item in rows for flag in item["blocking_flags"])
        review_flag_counts = Counter(flag for item in rows for flag in item["review_flags"])
        group_counts = Counter(item["group_id"] for item in rows)
        by_dataset[name] = {
            "fetched_source_rows": fetched_counts.get(name, 0),
            "candidate_count": len(rows),
            "heuristic_pass_count": sum(item["heuristic_pass"] for item in rows),
            "heuristic_pass_rate": round(
                sum(item["heuristic_pass"] for item in rows) / len(rows), 4
            ) if rows else None,
            "response_words": {
                "min": min(lengths) if lengths else None,
                "p25": percentile(lengths, 0.25),
                "median": statistics.median(lengths) if lengths else None,
                "p75": percentile(lengths, 0.75),
                "max": max(lengths) if lengths else None,
            },
            "flag_counts": dict(sorted(flag_counts.items())),
            "blocking_flag_counts": dict(sorted(blocking_flag_counts.items())),
            "review_flag_counts": dict(sorted(review_flag_counts.items())),
            "unique_group_count": len(group_counts),
            "maximum_candidates_per_group": max(group_counts.values()) if group_counts else 0,
            "provisional_target": config["provisional_final_targets"][name],
        }
    return {
        "version": config["version"],
        "seed": config["seed"],
        "candidate_count": len(candidates),
        "full_text_location": full_text_location,
        "human_review_status": "pending",
        "interpretation": (
            "Heuristic screening describes source suitability only. It does not certify "
            "content preservation, confidence labels, or a confidence representation."
        ),
        "by_dataset": by_dataset,
    }


def write_review_csv(path: Path, candidates: list[dict[str, Any]]) -> None:
    fields = [
        "dataset",
        "source_id",
        "group_id",
        "question",
        "original_response",
        "evidence",
        "source_locator",
        "license",
        "word_count",
        "sentence_count",
        "evidence_word_count",
        "heuristic_flags",
        "blocking_flags",
        "review_flags",
        "human_decision",
        "human_claim_count",
        "human_content_self_contained",
        "human_evidence_support",
        "human_rewrite_suitability",
        "human_notes",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for item in candidates:
            row = {field: item.get(field, "") for field in fields}
            row["heuristic_flags"] = ";".join(item["heuristic_flags"])
            row["blocking_flags"] = ";".join(item["blocking_flags"])
            row["review_flags"] = ";".join(item["review_flags"])
            writer.writerow(row)


def write_report(path: Path, summary: dict[str, Any], expanded_pool: bool = False) -> None:
    title = "# Factual Source Pool Expansion v2" if expanded_pool else "# Factual Source Audit v1"
    if expanded_pool:
        status_lines = [
            "**Expanded source retrieval and mechanical screening are complete; final source review is pending.**",
            "No confident/hesitant rewrites, hidden-state extraction, or probe fitting has been run.",
        ]
    else:
        status_lines = [
            "**Source retrieval and mechanical screening are complete. A fixed 10-record-per-dataset model-assisted diagnostic is also complete; final source review is pending.**",
            "No confident/hesitant rewrites, hidden-state extraction, or probe fitting has been run.",
            "",
            "See `MODEL_ASSISTED_SOURCE_REVIEW.md` for the record-level diagnostic, revised",
            "source roles, and the gate before rewriting.",
        ]
    lines = [
        title,
        "",
        "## Status",
        "",
        *status_lines,
        "",
        "## Mechanical audit",
        "",
        "| Dataset | Candidates | Heuristic pass | Median words | Main flags |",
        "|---|---:|---:|---:|---|",
    ]
    for name, values in summary["by_dataset"].items():
        main_flags = ", ".join(
            f"{flag}: {count}" for flag, count in values["flag_counts"].items()
        ) or "none"
        lines.append(
            f"| {name} | {values['candidate_count']} | "
            f"{values['heuristic_pass_count']} | {values['response_words']['median']} | {main_flags} |"
        )
    lines.extend(
        [
            "",
            "The screen is intentionally provisional: 40–220 words, at least two sentences,",
            "and non-empty evidence. It is a triage rule, not a scientific label.",
            "",
            "## Revised next gate",
            "",
            "Expand each long-form candidate pool to 100 and review fixed blocks until",
            "ASQA, QASPER, and BillSum each contain 40 accepted sources plus 8 accepted",
            "backups. Keep FeTaQA as a separate short-response test. Freeze the accepted",
            "sources and protected factual qualifiers before confidence rewriting.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    private_root = ROOT / "private_data"
    raw_dir = private_root / "raw"
    private_dir = private_root / args.output_tag if args.output_tag else private_root
    results_dir = ROOT / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    private_dir.mkdir(parents=True, exist_ok=True)

    if args.output_tag:
        public_stem = args.output_tag
        manifest_path = results_dir / f"{public_stem}_candidate_manifest.jsonl"
        summary_path = results_dir / f"{public_stem}_summary.json"
        report_path = results_dir / f"{public_stem.upper()}_REPORT.md"
        full_text_location = f"private_data/{args.output_tag}/source_candidates.jsonl"
    else:
        manifest_path = results_dir / "source_candidate_manifest.jsonl"
        summary_path = results_dir / "source_audit_summary.json"
        report_path = results_dir / "SOURCE_AUDIT_REPORT.md"
        full_text_location = "private_data/source_candidates.jsonl"

    all_candidates: list[dict[str, Any]] = []
    fetched_counts: dict[str, int] = {}
    for name, spec in config["datasets"].items():
        rows = fetch_dataset_rows(name, spec, int(config["seed"]), raw_dir, args.refresh)
        fetched_counts[name] = len(rows)
        parsed: list[dict[str, Any]] = []
        for row_idx, row in rows:
            parsed.extend(PARSERS[name](row_idx, row, spec))
        enriched = [enrich(item, config["screen"]) for item in parsed]
        selected = choose_candidates(
            name,
            enriched,
            int(
                config.get("candidate_limit_by_dataset", {}).get(
                    name, config["candidate_limit_per_dataset"]
                )
            ),
            int(config["seed"]),
        )
        all_candidates.extend(selected)

    all_candidates.sort(key=lambda item: (item["dataset"], item["source_id"]))
    write_jsonl(private_dir / "source_candidates.jsonl", all_candidates)
    write_review_csv(private_dir / "source_audit_template.csv", all_candidates)

    public_manifest = [
        {
            "dataset": item["dataset"],
            "source_id": item["source_id"],
            "group_id": item["group_id"],
            "source_hash": item["source_hash"],
            "word_count": item["word_count"],
            "sentence_count": item["sentence_count"],
            "evidence_word_count": item["evidence_word_count"],
            "heuristic_flags": item["heuristic_flags"],
            "blocking_flags": item["blocking_flags"],
            "review_flags": item["review_flags"],
            "heuristic_pass": item["heuristic_pass"],
        }
        for item in all_candidates
    ]
    write_jsonl(manifest_path, public_manifest)
    summary = build_summary(config, all_candidates, fetched_counts, full_text_location)
    summary_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    write_report(report_path, summary, expanded_pool=bool(args.output_tag))
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
