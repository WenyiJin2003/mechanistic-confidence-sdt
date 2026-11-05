#!/usr/bin/env python3
"""Aggregate ten GPU outputs and build the deterministic A/B packet."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROLES = ("confident_r010", "hesitant_r010")
BLIND_SEED = "confidence-output-direct-eval500-blind-v1"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--experiment", type=Path, required=True)
    return parser.parse_args()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    if path.exists():
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def main() -> None:
    args = parse_args()
    experiment = args.experiment.resolve()
    authority = json.loads((experiment / "DIRECT_EVAL_AUTHORITY.json").read_text(encoding="utf-8"))
    cohort = read_jsonl(experiment / authority["cohort_file"])
    cohort_by_id = {row["eval_id"]: row for row in cohort}
    expected_ids = set(cohort_by_id)
    if len(cohort) != 500 or len(expected_ids) != 500:
        raise ValueError("authority cohort is not exactly 500 unique rows")
    combined: dict[str, list[dict[str, Any]]] = {}
    summaries = []
    for run_id in ROLES:
        rows = []
        for shard_index in range(5):
            cell_dir = experiment / f"outputs/generation/{run_id}/shard_{shard_index:02d}"
            data_path = cell_dir / f"{run_id}.jsonl"
            summary_path = cell_dir / f"{run_id}.summary.json"
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            shard_rows = read_jsonl(data_path)
            if summary.get("status") != "COMPLETE" or summary.get("rows") != 100 or len(shard_rows) != 100:
                raise ValueError(f"incomplete generation cell: {run_id} shard {shard_index}")
            if sha256(data_path) != summary.get("output_jsonl_sha256"):
                raise ValueError(f"generation hash mismatch: {data_path}")
            rows.extend(shard_rows)
            summaries.append({"run_id": run_id, "shard_index": shard_index, "summary_sha256": sha256(summary_path)})
        by_id = {row["item_id"]: row for row in rows}
        if len(rows) != 500 or set(by_id) != expected_ids:
            raise ValueError(f"{run_id}: output membership does not match the 500-row cohort")
        ordered = [by_id[row["eval_id"]] for row in cohort]
        combined[run_id] = ordered
        write_jsonl(experiment / f"outputs/combined/{run_id}.jsonl", ordered)

    packet = []
    key = []
    for index, source in enumerate(cohort, start=1):
        eval_id = source["eval_id"]
        conf = combined["confident_r010"][index - 1]
        hes = combined["hesitant_r010"][index - 1]
        confident_is_a = int(hashlib.sha256(f"{BLIND_SEED}\0{eval_id}".encode()).hexdigest(), 16) % 2 == 0
        answer_a, answer_b = (conf, hes) if confident_is_a else (hes, conf)
        blind_id = f"DIRECT500-{index:04d}"
        packet.append(
            {
                "blind_id": blind_id,
                "question": source["question"],
                "response_A": answer_a["response"],
                "response_B": answer_b["response"],
            }
        )
        key.append(
            {
                "A_source": "confident_r010" if confident_is_a else "hesitant_r010",
                "B_source": "hesitant_r010" if confident_is_a else "confident_r010",
                "blind_id": blind_id,
                "eval_id": eval_id,
            }
        )
    packet_path = experiment / "outputs/blind/DIRECT500_PACKET.jsonl"
    key_path = experiment / "outputs/blind/DIRECT500_KEY.jsonl"
    write_jsonl(packet_path, packet)
    write_jsonl(key_path, key)
    aggregate = {
        "answer_rows": 1000,
        "blind_pairs": 500,
        "blinding_seed": BLIND_SEED,
        "cohort_sha256": authority["cohort_sha256"],
        "generation_cells": summaries,
        "missing_pairs": 0,
        "packet_sha256": sha256(packet_path),
        "key_sha256": sha256(key_path),
        "schema": "confidence-output-direct-eval500-aggregation-v1",
        "status": "READY_FOR_BLIND_JUDGE",
    }
    (experiment / "outputs/AGGREGATION.json").write_text(
        json.dumps(aggregate, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(aggregate, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
