"""Prepare five Chat batches from the exact successful Work 50-source set.

The resulting rewrites are a provider-quality replication only. The original
challenge has already been scored, so these new responses must not be treated
as an independent test set or used to update the reported probe result.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any


BASE = Path(__file__).resolve().parents[1]
PRIVATE = BASE / "private_data"
DEFAULT_SOURCE = BASE / "private_data/challenge_sources_50.jsonl"
DEFAULT_OUTPUT = BASE / "private_data/chat_provider_replication_50"
REWRITE_SPEC = BASE / "REWRITE_SPEC.md"
TASKS = [
    "factual_explanation",
    "math_logic",
    "programming",
    "comparison_analysis",
    "summary_judgment",
]
CUE_FAMILIES = [
    "embedded_stance_predicate",
    "modal_force_scope",
    "compositional_polarity",
    "discourse_level_calibration",
    "contrastive_commitment",
]
DIRECTIONS = ["confident_longer", "hedged_longer"]


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        if not isinstance(row, dict):
            raise ValueError(f"{path}:{line_number}: expected an object")
        rows.append(row)
    return rows


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require_private_output(output_dir: Path, private_root: Path = PRIVATE) -> Path:
    """Resolve an output directory and refuse writes outside private_data."""
    output = output_dir.resolve()
    root = private_root.resolve()
    if output != root and root not in output.parents:
        raise ValueError(f"Provider replication output must stay under private_data: {root}")
    return output


def validate_source_grid(rows: list[dict[str, Any]]) -> dict[tuple[str, str, str], dict[str, Any]]:
    if len(rows) != 50 or len({row.get("source_id") for row in rows}) != 50:
        raise ValueError("Expected 50 distinct frozen sources")
    indexed: dict[tuple[str, str, str], dict[str, Any]] = {}
    for row in rows:
        required = {
            "source_id",
            "original_response_sha256",
            "task",
            "cue_family",
            "length_direction",
            "prompt",
            "original_response",
        }
        missing = sorted(required - row.keys())
        if missing:
            raise ValueError(f"{row.get('source_id')}: missing {missing}")
        digest = hashlib.sha256(row["original_response"].encode("utf-8")).hexdigest()
        if digest != row["original_response_sha256"]:
            raise ValueError(f"{row['source_id']}: source hash mismatch")
        key = (row["task"], row["cue_family"], row["length_direction"])
        if key in indexed:
            raise ValueError(f"Duplicate frozen allocation cell: {key}")
        indexed[key] = row
    expected = {
        (task, family, direction)
        for task in TASKS
        for family in CUE_FAMILIES
        for direction in DIRECTIONS
    }
    if set(indexed) != expected:
        raise ValueError("Frozen source allocation is not the expected 5 x 5 x 2 grid")
    return indexed


def make_batches(indexed: dict[tuple[str, str, str], dict[str, Any]]) -> list[list[dict[str, Any]]]:
    batches: list[list[dict[str, Any]]] = []
    for batch_index in range(5):
        batch: list[dict[str, Any]] = []
        for task_index, task in enumerate(TASKS):
            family = CUE_FAMILIES[(batch_index + task_index) % 5]
            for direction in DIRECTIONS:
                batch.append(indexed[(task, family, direction)])
        batches.append(batch)
    expected_ids = Counter(row["source_id"] for row in indexed.values())
    actual_ids = Counter(row["source_id"] for batch in batches for row in batch)
    if actual_ids != expected_ids:
        raise AssertionError("Batch plan does not cover every source exactly once")
    return batches


def writer_prompt(batch: list[dict[str, Any]], number: int, total: int = 5) -> str:
    payload = [
        {
            "source_id": row["source_id"],
            "original_response_sha256": row["original_response_sha256"],
            "task": row["task"],
            "cue_family": row["cue_family"],
            "length_direction": row["length_direction"],
            "prompt": row["prompt"],
            "original_response": row["original_response"],
        }
        for row in batch
    ]
    return f"""FRESH DIRECT-PAIR REWRITE BATCH {number}/{total}.

This is a provider replication of the earlier successful 50-pair Work algorithm. Ignore every neutral-template, <STANCE_*>, and local cue-insertion instruction from earlier turns. For each record, directly write TWO COMPLETE natural rewrites of the full answer: one confident and one hesitant.

NON-NEGOTIABLE RULES

1. Rewrite both complete responses from the original. Neither member may be the verbatim source. Do not create a shared body and then add, prepend, append, or swap one detachable sentence such as \"I am certain/uncertain about this answer.\"
2. Preserve exactly the same object-level answer: every proposition, conclusion, list item, number, date, unit, entity, condition, exception, example, code/formula, URL, citation, negation, causal/logical step, and original object-level modal such as may/might/can/could/likely. Never correct the source, even if it appears wrong.
3. Change only the speaker's commitment to that same answer. The confident response should sound naturally settled; the hesitant response should remain responsive and give the same answer while sounding naturally provisional. Never introduce another candidate answer, refusal, new evidence, new reason for doubt, or factual qualification.
4. Integrate certainty into the substantive grammar and discourse. For responses longer than 80 words, distribute natural stance differences across at least two separated clauses or regions. For shorter responses, restructure the main answer sentence. Deleting one sentence must not make the pair otherwise identical.
5. Follow the assigned abstract cue_family with source-specific wording. Vary predicate, syntax, and position. Do not use a fixed opener/closer or generic standalone self-report. Forbidden recipes include \"I am certain,\" \"I am uncertain,\" \"I'm not sure,\" \"my tentative answer,\" \"I may be wrong,\" \"I could be mistaken,\" and \"my understanding is.\"
6. Keep formatting, paragraph/list structure, code fences, equations, notation, politeness, helpfulness, authority, detail, and answer quality matched within the pair. Protected code/formulas/URLs/numbers must remain exact.
7. Keep both responses near the source length and target an absolute within-pair difference of at most three tokenizer tokens. Respect length_direction: confident_longer means confident is slightly longer; hedged_longer means hesitant is slightly longer. Do not pad, repeat, or delete answer content to force length.
8. If a faithful pair is genuinely impossible, return empty response strings and a brief issue. Otherwise issues must be [].

CUE FAMILY MEANINGS
- embedded_stance_predicate: integrate commitment/tentativeness into a reporting, judgment, or conclusion clause.
- modal_force_scope: vary speaker-level modal force without changing any object-level condition or probability.
- compositional_polarity: use negation/scope composition; a single word such as certain must not by itself reveal the label.
- discourse_level_calibration: integrate a concise commitment/reservation into a natural lead-in, parenthetical, or conclusion; never as a detachable generic label.
- contrastive_commitment: use balanced self-qualification to make endorsement settled versus provisional without qualifying or retracting the answer itself.

Return ONLY one valid JSON object, in the supplied order:
{{"pairs":[{{"source_id":"...","original_response_sha256":"...","task":"...","cue_family":"...","length_direction":"...","confident_response":"...","hedged_response":"...","issues":[]}}]}}

No Markdown fences, commentary, rationale, scores, or omitted records.

INPUT_RECORDS_JSON
{json.dumps(payload, ensure_ascii=False, separators=(",", ":"))}
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)

    source_path = args.source.resolve()
    output_dir = require_private_output(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = read_jsonl(source_path)
    batches = make_batches(validate_source_grid(rows))
    for number, batch in enumerate(batches, 1):
        (output_dir / f"PROMPT_BATCH_{number:02d}.txt").write_text(
            writer_prompt(batch, number, len(batches)), encoding="utf-8"
        )
        (output_dir / f"SOURCE_BATCH_{number:02d}.jsonl").write_text(
            "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in batch),
            encoding="utf-8",
        )

    # Five records keep each Chat response below the connector's per-message
    # retrieval limit. These are transport chunks only; the scientific design
    # and first-stage QA gate remain the five balanced ten-record batches above.
    transport_chunks = [
        batch[offset : offset + 5]
        for batch in batches
        for offset in range(0, len(batch), 5)
    ]
    for number, chunk in enumerate(transport_chunks, 1):
        (output_dir / f"PROMPT_CHUNK_{number:02d}.txt").write_text(
            writer_prompt(chunk, number, len(transport_chunks)), encoding="utf-8"
        )
        (output_dir / f"SOURCE_CHUNK_{number:02d}.jsonl").write_text(
            "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in chunk),
            encoding="utf-8",
        )

    manifest = {
        "protocol": "chat-provider-replication-of-work-50-v1",
        "purpose": "rewrite_provider_quality_check_only",
        "independent_probe_test": False,
        "score_exposed_sources": True,
        "may_update_reported_probe_result": False,
        "source_count": 50,
        "batch_count": 5,
        "batch_size": 10,
        "transport_chunk_count": len(transport_chunks),
        "transport_chunk_size": 5,
        "task_counts": dict(sorted(Counter(row["task"] for row in rows).items())),
        "cue_family_counts": dict(sorted(Counter(row["cue_family"] for row in rows).items())),
        "length_direction_counts": dict(
            sorted(Counter(row["length_direction"] for row in rows).items())
        ),
        "source_file_sha256": sha256_file(source_path),
        "rewrite_spec_sha256": sha256_file(REWRITE_SPEC),
        "local_cue_insertion": False,
        "generation_provider": "existing ChatGPT chat thread; exact model slug not exposed",
        "activations_inspected": False,
        "human_review": "pending",
    }
    (output_dir / "FREEZE_MANIFEST_PRIVATE.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
