#!/usr/bin/env python3
"""Render saved questions and answers as GitHub-readable Markdown and CSV.

This exporter only reads existing artifacts. It never calls a model, downloads
data, calculates a new readout, or changes a source dataset/result artifact.
Run from any directory: python scripts/export_question_sets.py
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "datasets"
PRIMARY_SCORE = "layer14_boundary"
STAGE_RUNS = (
    "preflight", "run_a", "run_b", "run_200", "run_200_qwen15b",
    "run_500_qwen15b_confirm", "run_50_qwen15b_label_stability",
)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_rows(path: Path, id_key: str) -> list[dict[str, Any]]:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    ids = [row[id_key] for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError(f"Duplicate {id_key} in {path.relative_to(ROOT)}")
    return rows


def rel(path: Path, page: Path) -> str:
    return Path(os.path.relpath(path, page.parent)).as_posix()


def link(label: str, path: Path, page: Path, line: int | None = None) -> str:
    return f"[{label}]({rel(path, page)}{'#L' + str(line) if line else ''})"


def inline(value: Any) -> str:
    return str(value).replace("\n", " ").replace("|", "\\|").replace("[", "\\[").replace("]", "\\]")


def code(value: Any) -> str:
    text = "" if value is None else str(value)
    runs = [len(match.group()) for match in re.finditer(r"`+", text)]
    fence = "`" * max(3, max(runs, default=0) + 1)
    return f"{fence}text\n{text}\n{fence}\n\n"


def scalar(value: Any) -> str:
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(f"Nonfinite saved scalar: {value}")
        return f"{value:.6f}"
    return str(value)


def write_md(path: Path, parts: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(parts).rstrip() + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    """Write exact flat research rows; multiline prose is CSV-quoted, not edited."""
    fields = list(dict.fromkeys(key for row in rows for key in row))
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def base_navigation(page: Path, title: str) -> list[str]:
    return [f"# {title}\n\n", f"{link('Repository', ROOT / 'README.md', page)} · "
            f"{link('All question sets', OUT / 'README.md', page)}\n\n"]


def saved_score_npz(path: Path, expected_ids: set[str], key: str) -> dict[str, float]:
    import numpy as np

    with np.load(path, allow_pickle=False) as data:
        ids = [str(value) for value in data["variant_ids"]]
        values = data[key]
        if len(ids) != len(set(ids)) or set(ids) != expected_ids or values.shape != (len(ids),):
            raise ValueError(f"Score identity/shape mismatch: {path}")
        if not np.all(np.isfinite(values)):
            raise ValueError(f"Nonfinite scores: {path}")
        return {identifier: float(value) for identifier, value in zip(ids, values)}


def saved_score_json(path: Path, expected_ids: set[str], key: str) -> dict[str, float]:
    data = read_json(path)
    ids, values = data["variant_ids"], data["scores"][key]
    if len(ids) != len(set(ids)) or set(ids) != expected_ids or len(ids) != len(values):
        raise ValueError(f"Score identity/shape mismatch: {path}")
    scores = {identifier: float(value) for identifier, value in zip(ids, values)}
    if not all(math.isfinite(value) for value in scores.values()):
        raise ValueError(f"Nonfinite scores: {path}")
    return scores


def response_block(row: dict[str, Any], score: float, raw_path: Path, raw_line: int,
                   page: Path, score_path: Path) -> list[str]:
    identifier = row["variant_id"]
    parts = [f"**{inline(row['correctness'])}, {inline(row['certainty'])}**\n\n", code(row["response_text"])]
    parts.append(f"Saved primary L14 boundary readout: `{scalar(score)}`.\n\n")
    parts.append("<details>\n<summary>Technical details and saved source row</summary>\n\n")
    parts.append(f"Variant ID: `{identifier}`. {link('Saved response row', raw_path, page, raw_line)} · "
                 f"{link('Saved score artifact', score_path, page)}.\n\n")
    parts.append(f"Saved token positions (zero-based): prompt/response start "
                 f"`{row['response_start_position']}`; response stop (exclusive) "
                 f"`{row['response_stop_position_exclusive']}`; final content "
                 f"`{row['final_content_position']}`; boundary `{row['boundary_position']}` "
                 f"(`{row['boundary_token_id']}`, `{row['boundary_token_text']}`). "
                 f"Response tokens: `{row['token_count']}`.\n\n")
    parts.append(f"Sequence NLL: `{scalar(row['sequence_nll'])}`; "
                 f"mean token NLL: `{scalar(row['mean_token_nll'])}`.\n\n</details>\n\n")
    return parts


def verified_variant_join(variants: list[dict[str, Any]], extracted: list[dict[str, Any]]) -> dict[str, tuple[int, dict[str, Any]]]:
    lookup = {row["variant_id"]: (i + 1, row) for i, row in enumerate(extracted)}
    if set(lookup) != {row["variant_id"] for row in variants}:
        raise ValueError("Authored/extracted variant IDs differ")
    for variant in variants:
        measured = lookup[variant["variant_id"]][1]
        for key in ("source_id", "question", "context", "response_text", "correctness", "certainty"):
            if variant.get(key) != measured.get(key):
                raise ValueError(f"Authored/extracted {key} mismatch: {variant['variant_id']}")
    return lookup


def export_authored(kind: str) -> dict[str, int]:
    is_v2 = kind == "frozen-transfer-v2"
    data_dir = ROOT / "data" / ("confidence_transfer_v2" if is_v2 else "paired_confidence")
    result_dir = ROOT / "results" / ("paired_confidence_transfer_v2" if is_v2 else "paired_confidence_phase_b")
    source_path, variant_path = data_dir / "source_items.jsonl", data_dir / "variants.jsonl"
    extraction_path = result_dir / "extraction_rows.jsonl"
    sources = read_rows(source_path, "source_id")
    variants = read_rows(variant_path, "variant_id")
    extracted = read_rows(extraction_path, "variant_id")
    measurements = verified_variant_join(variants, extracted)
    ids = {row["variant_id"] for row in variants}
    score_path = result_dir / ("transfer_metrics.json" if is_v2 else "readout_scores.npz")
    scores = (saved_score_json if is_v2 else saved_score_npz)(score_path, ids, PRIMARY_SCORE)
    source_ids = {row["source_id"] for row in sources}
    if {row["source_id"] for row in variants} != source_ids:
        raise ValueError(f"Source/variant coverage mismatch: {kind}")
    by_source = defaultdict(list)
    for row in variants:
        by_source[row["source_id"]].append(row)
    expected_sources, expected_variants = (48, 480) if is_v2 else (120, 1440)
    if (len(sources), len(variants)) != (expected_sources, expected_variants):
        raise ValueError(f"Unexpected catalog size for {kind}")
    if any(len(by_source[source]) != (10 if is_v2 else 12) for source in source_ids):
        raise ValueError(f"Incomplete authored conditions in {kind}")
    folder, landing = OUT / kind, OUT / kind / "README.md"
    title = "Frozen transfer v2: all questions and authored answers" if is_v2 else "Paired confidence v1: all questions and authored answers"
    parts = base_navigation(landing, title)
    parts.append(f"{len(sources)} source questions and {len(variants)} authored response variants. "
                 "These responses were constructed for controlled experiments and then teacher-forced "
                 "through the model for saved measurements. They are not sampled model answers. "
                 "Correctness and confident/hedged/neutral labels are dataset labels. Wording labels "
                 "do not measure a model's subjective confidence.\n\n")
    parts.append("Every response is shown below its question. Token positions and the saved primary "
                 "layer-14 boundary readout are included. Readout values are experiment scores, not "
                 "probabilities that an answer is true. Markdown rounds numbers to six decimals; CSV "
                 "retains the saved numeric values. No scores were refitted or recalculated.\n\n")
    if is_v2:
        parts.append("The 48 entities are fictional constructed worlds. The true key stays fixed when "
                     "evidence is supported, omitted, or conflicting. A response labeled correct can "
                     "therefore lack support in the supplied context. All 48 sources are test-only.\n\n")
        parts.append("Start with the [access-code example](access_code.md#v2-access_code-01), "
                     "[room-assignment example](room_assignment.md#v2-room_assignment-01), or "
                     "[release-year evidence-order reversal](release_year.md#v2-release_year-02).\n\n")
    else:
        parts.append("Each source has 12 responses: correct/incorrect content × confident/hedged wording "
                     "× rewrite families A/B/C. Phase A uses the marked 24-source subset and families A/B; "
                     "Phase B uses all 120 sources. The two split labels refer to separate experiment "
                     "partitions, not the original benchmark's split. Saved measurements here are Phase B.\n\n")
    group_key = "fact_type" if is_v2 else "domain"
    for group in dict.fromkeys(row[group_key] for row in sources):
        selected = [row for row in sources if row[group_key] == group]
        page = folder / f"{group}.md"
        group_title = "Factual QA" if group == "factual_qa" else group.replace("_", " ").title()
        parts.append(f"- {link(group_title, page, landing)}: "
                     f"{len(selected)} questions, {sum(len(by_source[row['source_id']]) for row in selected)} responses\n")
        content = base_navigation(page, group_title)
        content.append(f"{link('Dataset overview', landing, page)} · "
                       f"{link('Download all response rows (CSV)', folder / 'responses.csv', page)}\n\n")
        content.append(f"All {len(selected)} questions in this group. Responses are authored experiment "
                       "stimuli. All stored variants and their primary scores are included.\n\n")
        for source in selected:
            question = source["qa_question"] if is_v2 else source["question"]
            content.append(f"- [{source['source_id']}](#{source['source_id']}): {inline(question)}\n")
        content.append("\n")
        for source in selected:
            source_id = source["source_id"]
            source_line = next(i + 1 for i, row in enumerate(sources) if row["source_id"] == source_id)
            content.append(f"## {source_id}\n\n{link('Raw source', source_path, page, source_line)}\n\n")
            content.append("Question:\n\n" + code(source["qa_question"] if is_v2 else source["question"]))
            if is_v2:
                content.append("Document-format request:\n\n" + code(source["document_request"]))
                content.append(f"Constructed-world correct key: `{source['true_value']}`. "
                               f"Authored incorrect key: `{source['false_value']}`. "
                               f"Original source: fictional constructed world; external benchmark split: "
                               f"not applicable; experiment split: `{source['split']}`; "
                               f"wording ID: `{source['wording_id']}`.\n\n")
                qa = {row["condition"]: scores[row["variant_id"]] for row in by_source[source_id]
                      if row["experiment"] == "neutral_evidence" and row["format"] == "qa"}
                ordering = ("supported > omitted" if qa["supported"] > qa["omitted"] else
                            "supported < omitted (reversal)" if qa["supported"] < qa["omitted"] else
                            "supported = omitted (tie)")
                content.append(f"Saved neutral QA evidence ordering: **{ordering}**. "
                               f"L14 boundary scores: supported `{scalar(qa['supported'])}`; "
                               f"omitted `{scalar(qa['omitted'])}`.\n\n")
                for condition in ("supported", "omitted", "conflicting"):
                    content.append(f"### {condition.title()} context\n\n" + code(source["contexts"][condition]))
                content.append("### Neutral evidence responses\n\n")
                content.append("The same authored claim is repeated in both request formats and all three "
                               "contexts; only the request/context changes.\n\n")
                for fmt in ("qa", "document"):
                    content.append(f"#### {fmt.upper() if fmt == 'qa' else 'Document'} format\n\n")
                    for condition in ("supported", "omitted", "conflicting"):
                        variant = next(row for row in by_source[source_id] if row["experiment"] == "neutral_evidence" and row["format"] == fmt and row["condition"] == condition)
                        content.append(f"Condition: `{condition}`.\n\n")
                        line_number, measured = measurements[variant["variant_id"]]
                        content.extend(response_block(measured, scores[variant["variant_id"]], extraction_path, line_number, page, score_path))
                content.append("### Natural style responses\n\nSupported context, QA format.\n\n")
                for variant in by_source[source_id]:
                    if variant["experiment"] == "natural_style":
                        line_number, measured = measurements[variant["variant_id"]]
                        content.extend(response_block(measured, scores[variant["variant_id"]], extraction_path, line_number, page, score_path))
            else:
                content.append("Context:\n\n" + (code(source["context"]) if source["context"] is not None else "No supplied passage.\n\n"))
                content.append("Correct key:\n\n" + code(source["correct_answer"]) + "Authored incorrect key:\n\n" + code(source["incorrect_answer"]))
                verification = source["verification"]
                if source["domain"] == "factual_qa":
                    content.append(f"Original source: `{verification['dataset']}`, original ID "
                                   f"`{verification['original_source_id']}`. Original benchmark split: "
                                   "SQuAD validation (cached Stage0 source). Correctness scope: supplied passage.\n\n")
                elif source["domain"] == "academic":
                    content.append(f"Original source: `{verification['dataset']}`, pinned test split, "
                                   f"row `{verification['row_index']}`, subject `{verification['subject']}`, "
                                   f"revision `{verification['revision']}`.\n\n")
                    content.append("Original multiple-choice options:\n\n" + code("\n".join(f"{i}: {option}" for i, option in enumerate(verification["original_choices"]))))
                else:
                    content.append("Original source: constructed integer arithmetic; original benchmark split: "
                                   "not applicable. Key checked with exact arithmetic.\n\n")
                content.append(f"Phase A included: `{str(source['phase_a']).lower()}`; Phase A split: "
                               f"`{source.get('phase_a_split') or 'not included'}`; "
                               f"Phase B split: `{source['phase_b_split']}`.\n\n")
                content.append("Saved key explanation:\n\n" + code(verification["explanation"]))
                for family in ("A", "B", "C"):
                    content.append(f"### Rewrite family {family}\n\n")
                    for variant in by_source[source_id]:
                        if variant["rewrite_family"] == family:
                            line_number, measured = measurements[variant["variant_id"]]
                            content.extend(response_block(measured, scores[variant["variant_id"]], extraction_path, line_number, page, score_path))
            content.append(f"[Back to question list](#{group.replace('_', '-')}) · {link('Dataset overview', landing, page)}\n\n")
        write_md(page, content)
    parts.append("\nDownloads and sources:\n\n")
    for label, path in [("All authored response rows (CSV)", folder / "responses.csv"), ("All source questions (CSV)", folder / "sources.csv"), ("Raw source items", source_path), ("Raw authored variants", variant_path), ("Saved extraction rows", extraction_path), ("Saved primary scores", score_path), ("Results report", ROOT / "reports" / ("CONFIDENCE_TRANSFER_RESULTS_V2.md" if is_v2 else "PAIRED_CONFIDENCE_RESULTS_V1.md")), ("Experiment guide", ROOT / "docs/experiments" / ("CONFIDENCE_TRANSFER_README_V2.md" if is_v2 else "PAIRED_CONFIDENCE_README.md"))]:
        parts.append(f"- {link(label, path, landing)}\n")
    parts.append("\nRegenerate from saved artifacts with `python scripts/export_question_sets.py`. "
                 "Source JSONL and result files remain authoritative.\n")
    write_md(landing, parts)
    source_csv = []
    for source in sources:
        row = {key: value for key, value in source.items() if not isinstance(value, (dict, list))}
        if is_v2:
            row["original_source"] = "constructed_fictional_world"
            row["original_benchmark_split"] = "not_applicable"
            row.update({f"context_{condition}": text for condition, text in source["contexts"].items()})
        else:
            row["original_source"] = source["verification"].get("dataset", "constructed_integer_arithmetic")
            row["original_benchmark_split"] = {"factual_qa": "validation", "academic": "test", "arithmetic": "not_applicable"}[source["domain"]]
            row.update({f"verification_{key}": value for key, value in source["verification"].items() if not isinstance(value, (dict, list))})
        source_csv.append(row)
    response_csv = []
    for variant in variants:
        measured = measurements[variant["variant_id"]][1]
        row = {key: value for key, value in measured.items() if not isinstance(value, (dict, list))}
        row["answer_origin"] = "authored_experiment_stimulus"
        row["saved_primary_layer14_boundary_readout"] = scores[variant["variant_id"]]
        response_csv.append(row)
    write_csv(folder / "sources.csv", source_csv)
    write_csv(folder / "responses.csv", response_csv)
    return {"sources": len(sources), "authored_responses": len(variants)}


def load_answer_state() -> tuple[dict[str, list[tuple[Path, int, dict[str, Any]]]], dict[str, float]]:
    rows_by_id = defaultdict(list)
    folder = ROOT / "results/run_500_qwen15b_answer_state"
    primary = read_rows(folder / "leave_one_out_entropy.jsonl", "id")
    for path in (folder / "leave_one_out_entropy.jsonl", folder / "robustness/answer_index_3/leave_one_out_entropy.jsonl"):
        for i, row in enumerate(read_rows(path, "id")):
            rows_by_id[row["id"]].append((path, i + 1, row))
    if any(len(rows) != 2 or {row[2]["observed_answer_index"] for row in rows} != {0, 3} for rows in rows_by_id.values()):
        raise ValueError("Incomplete Stage0B primary/robustness annotations")
    import numpy as np

    by_index = {row["source_index"]: row for row in primary}
    score_by_id = {}
    with np.load(folder / "test_predictions.npz", allow_pickle=False) as data:
        indices = data["test_source_indices"]
        if len(set(indices.tolist())) != len(indices):
            raise ValueError("Duplicate answer-state test source indices")
        for j, source_index in enumerate(indices):
            row = by_index[int(source_index)]
            if not math.isclose(float(data["test_entropy"][j]), row["leave_one_out_semantic_entropy"], abs_tol=1e-12) or int(data["test_labels"][j]) != row["high_entropy_label"]:
                raise ValueError("Answer-state test identity/target mismatch")
            score_by_id[row["id"]] = float(data["layer_14_final_answer_token"][j])
    return rows_by_id, score_by_id


def export_stage0(chunk_size: int) -> dict[str, dict[str, int]]:
    folder, landing = OUT / "stage0", OUT / "stage0/README.md"
    landing_parts = base_navigation(landing, "Stage0: all saved questions and sampled model answers")
    landing_parts.append("These are sampled model answers, including incorrect, incomplete, repetitive, and "
                         "truncated answers. Every saved sample is shown unchanged. Reference answers are "
                         "benchmark keys. Cluster-assignment entropy is the saved diversity target in nats; "
                         "it is not a probability of correctness or a claim of subjective confidence.\n\n")
    landing_parts.append("Questions repeat across some runs. Run-specific sample IDs keep each saved answer "
                         "traceable. The 500-question confirmation set records a fresh-source exclusion "
                         "audit relative to the earlier 200-question 1.5B run. Stage0B annotations are "
                         "attached to those same 500 questions, avoiding a duplicate question catalog.\n\n")
    summaries = {}
    answer_state, answer_state_scores = load_answer_state()
    confirmation_ids = {row["id"] for row in read_rows(ROOT / "results/run_500_qwen15b_confirm/generations.jsonl", "id")}
    if set(answer_state) != confirmation_ids:
        raise ValueError("Stage0B source coverage mismatch")
    for run in STAGE_RUNS:
        raw_folder = ROOT / "results" / run
        stability = run == "run_50_qwen15b_label_stability"
        generation_path = raw_folder / ("combined_generations.jsonl" if stability else "generations.jsonl")
        entropy_path = raw_folder / ("semantic_entropy_20.jsonl" if stability else "semantic_entropy.jsonl")
        generations = read_rows(generation_path, "id")
        entropies = read_rows(entropy_path, "id")
        entropy_by_id = {row["id"]: (i + 1, row) for i, row in enumerate(entropies)}
        if set(entropy_by_id) != {row["id"] for row in generations}:
            raise ValueError(f"Stage0 entropy/generation coverage mismatch: {run}")
        if stability:
            configuration = read_json(ROOT / "results/run_200_qwen15b/manifest.json")["configuration"]
            model = configuration["models"]["generator"]["id"]
            grouping = "bidirectional_strict_entailment"
            extra_entropy = {n: {row["id"]: row for row in read_rows(raw_folder / f"semantic_entropy_{n}.jsonl", "id")} for n in (5, 10)}
            selection = {row["id"]: row for row in read_json(raw_folder / "selection.json")}
        else:
            manifest = read_json(raw_folder / "manifest.json")
            configuration = manifest["configuration"]
            model = configuration["models"]["generator"]["id"]
            grouping = manifest["grouping_runtime"]["method"]
            extra_entropy, selection = {}, {}
        run_folder, run_landing = folder / run, folder / run / "README.md"
        count = sum(len(row["generations"]) for row in generations)
        summaries[run] = {"questions": len(generations), "sampled_answers": count}
        landing_parts.append(f"- {link(run, run_landing, landing)}: {len(generations)} questions, "
                             f"{count} sampled answers, `{model}`\n")
        parts = base_navigation(run_landing, f"{run}: questions and sampled answers")
        parts.append(f"{link('All Stage0 runs', landing, run_landing)}\n\n")
        parts.append(f"{len(generations)} questions; {count} saved model samples. Model: `{model}`. "
                     f"Source: `{configuration['dataset']['id']}`, original benchmark split: "
                     f"`{configuration['dataset']['split']}`. Grouping: `{grouping}`.\n\n")
        if stability:
            parts.append("This is the stratified 50-question subset from `run_200_qwen15b`, with "
                         "20 saved answers per question. The first five samples are the original run's "
                         "answers. Entropy values for 5, 10, and 20 samples are shown together.\n\n")
        if run == "run_500_qwen15b_confirm":
            parts.append("Each question also has Stage0B leave-one-out entropy for observed answer indices "
                         "0 (primary) and 3 (robustness). The observed sample is excluded from the nine-answer "
                         "entropy target. Primary held-out test probabilities are shown only for the 99 "
                         "rows in the saved test-prediction artifact.\n\n")
        answer_csv = []
        for start in range(0, len(generations), chunk_size):
            end = min(start + chunk_size, len(generations))
            page = run_folder / f"questions-{start + 1:03d}-{end:03d}.md"
            parts.append(f"- {link(f'Questions {start + 1}–{end}', page, run_landing)}\n")
            content = base_navigation(page, f"{run}: questions {start + 1}–{end}")
            content.append(f"{link('Run index', run_landing, page)} · {link('All Stage0 runs', landing, page)}\n\n")
            for row in generations[start:end]:
                content.append(f"- [{row['id']}](#{row['id']}): {inline(row['question'])}\n")
            content.append("\n")
            for offset, record in enumerate(generations[start:end], start):
                identifier = record["id"]
                entropy_line, entropy = entropy_by_id[identifier]
                if len(entropy["semantic_ids"]) != len(record["generations"]):
                    raise ValueError(f"Cluster/sample alignment mismatch: {run}/{identifier}")
                content.append(f"## {identifier}\n\nSaved question {offset + 1}; "
                               f"{link('raw question and samples', generation_path, page, offset + 1)} · "
                               f"{link('raw entropy', entropy_path, page, entropy_line)}\n\n")
                content.append("Question:\n\n" + code(record["question"]) + "Context:\n\n" + code(record.get("context")))
                references = list(dict.fromkeys(record["reference_answers"]))
                content.append("Reference answer(s):\n\n" + code("\n".join(references)))
                content.append(f"Saved cluster-assignment entropy: `{scalar(entropy['cluster_assignment_entropy'])}` nats; "
                               f"semantic clusters: `{entropy['num_semantic_clusters']}`. "
                               f"Predictive entropy: `{scalar(entropy['predictive_entropy'])}`; "
                               f"answer NLL: `{scalar(entropy['answer_negative_log_likelihood'])}`.\n\n")
                content.append(f"Saved prompt tokens: `{record['prompt_token_count']}`; zero-based final prompt "
                               f"position: `{record['final_prompt_token_index']}`; token ID: "
                               f"`{record['final_prompt_token_id']}`; prompt truncated: "
                               f"`{str(record['prompt_was_truncated']).lower() if 'prompt_was_truncated' in record else 'not recorded'}`.\n\n")
                if record.get("prompt_was_truncated"):
                    content.append("<details>\n<summary>Actual saved prompt after truncation</summary>\n\n" + code(record["prompt"]) + "</details>\n\n")
                if stability:
                    content.append(f"Saved entropy by sample count: 5=`{scalar(extra_entropy[5][identifier]['cluster_assignment_entropy'])}`; "
                                   f"10=`{scalar(extra_entropy[10][identifier]['cluster_assignment_entropy'])}`; "
                                   f"20=`{scalar(entropy['cluster_assignment_entropy'])}` nats. "
                                   f"Original 200-run source index: `{selection[identifier]['source_index']}`; "
                                   f"selection stratum: `{selection[identifier]['stratum']}`.\n\n")
                content.append("### All saved model samples\n\n")
                for sample_index, sample in enumerate(record["generations"]):
                    sample_id = f"{run}--{identifier}--sample-{sample_index:02d}"
                    cluster = entropy["semantic_ids"][sample_index]
                    content.append(f"**Sample {sample_index + 1}** (stored index `{sample_index}`, "
                                   f"cluster `{cluster}`; `{sample_id}`)\n\n" + code(sample["text"]))
                    content.append(f"Saved response tokens: `{sample['token_count']}`; mean token log probability: "
                                   f"`{scalar(sample['mean_token_logprob'])}`; sequence log probability: "
                                   f"`{scalar(sample['sequence_logprob'])}`. " +
                                   (f"Exact match: `{scalar(sample['exact_match'])}`; F1: `{scalar(sample['f1'])}`. " if "exact_match" in sample else "") + "\n\n")
                    answer_csv.append({"sample_id": sample_id, "run": run, "source_id": identifier,
                                       "source_dataset": configuration["dataset"]["id"], "source_split": configuration["dataset"]["split"],
                                       "answer_origin": "sampled_model_generation", "model": model,
                                       "question": record["question"], "context": record.get("context"),
                                       "reference_answers": "\n".join(record["reference_answers"]),
                                       "sample_index": sample_index, "response_text": sample["text"],
                                       "semantic_cluster": cluster, "cluster_assignment_entropy": entropy["cluster_assignment_entropy"],
                                       "predictive_entropy": entropy["predictive_entropy"],
                                       "prompt_token_count": record["prompt_token_count"], "final_prompt_token_index": record["final_prompt_token_index"],
                                       "prompt_was_truncated": record.get("prompt_was_truncated"),
                                       **{key: value for key, value in sample.items() if not isinstance(value, (dict, list)) and key not in ("text", "normalized_text")}})
                if run == "run_500_qwen15b_confirm":
                    content.append("### Stage0B answer-state annotations\n\n")
                    for annotation_path, annotation_line, annotation in answer_state[identifier]:
                        observed = annotation["observed_answer_index"]
                        if annotation["id"] != identifier or annotation["observed_answer_text"] != record["generations"][observed]["text"] or annotation["source_index"] != offset:
                            raise ValueError(f"Stage0B sample identity mismatch: {identifier}")
                        content.append(f"Observed stored answer index `{observed}` (sample {observed + 1}): "
                                       f"leave-one-out entropy `{scalar(annotation['leave_one_out_semantic_entropy'])}` nats; "
                                       f"clusters `{annotation['leave_one_out_num_semantic_clusters']}`; "
                                       f"high-entropy target label `{annotation['high_entropy_label']}`; "
                                       f"training-only threshold `{scalar(annotation['threshold_fit_on_training_only'])}`. "
                                       f"Answer token span `[{annotation['answer_start_index']}, "
                                       f"{annotation['answer_stop_index_exclusive']})`; final answer token position "
                                       f"`{annotation['final_answer_token_index']}`. "
                                       f"{link('Saved annotation', annotation_path, page, annotation_line)}.\n\n")
                    if identifier in answer_state_scores:
                        content.append(f"Saved primary L14 final-answer-token probability of the high-entropy "
                                       f"target: `{scalar(answer_state_scores[identifier])}` "
                                       f"({link('held-out test artifact', ROOT / 'results/run_500_qwen15b_answer_state/test_predictions.npz', page)}). "
                                       "This predicts the experiment's entropy label, not answer correctness.\n\n")
                    else:
                        content.append("No primary held-out test prediction is stored for this source.\n\n")
                content.append(f"{link('Back to run index', run_landing, page)}\n\n")
            write_md(page, content)
        if len({row["sample_id"] for row in answer_csv}) != len(answer_csv):
            raise ValueError(f"Duplicate sample IDs: {run}")
        write_csv(run_folder / "samples.csv", answer_csv)
        parts.append("\nDownloads and sources:\n\n")
        for label, path in [("All saved sampled-answer rows (CSV)", run_folder / "samples.csv"), ("Raw questions and samples", generation_path), ("Raw entropy", entropy_path), ("Results report", ROOT / "reports/RESULTS_STAGE0.md"), ("Experiment guide", ROOT / "docs/experiments/README_STAGE0.md")]:
            parts.append(f"- {link(label, path, run_landing)}\n")
        write_md(run_landing, parts)
    landing_parts.append("\n" + link("Stage0 results report", ROOT / "reports/RESULTS_STAGE0.md", landing) + " · " + link("Experiment guide", ROOT / "docs/experiments/README_STAGE0.md", landing) + "\n\n")
    landing_parts.append("Regenerate from saved artifacts with `python scripts/export_question_sets.py`. "
                         "Numeric CSV values retain stored precision; Markdown shows six decimals.\n")
    write_md(landing, landing_parts)
    return summaries


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chunk-size", type=int, default=25, help="Stage0 questions per Markdown file (default: 25)")
    args = parser.parse_args()
    if not 1 <= args.chunk_size <= 50:
        parser.error("--chunk-size must be between 1 and 50")
    summary = {"paired-confidence-v1": export_authored("paired-confidence-v1"),
               "frozen-transfer-v2": export_authored("frozen-transfer-v2"),
               "stage0": export_stage0(args.chunk_size)}
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
