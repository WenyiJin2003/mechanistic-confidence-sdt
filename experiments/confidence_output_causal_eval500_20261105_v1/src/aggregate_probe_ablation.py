#!/usr/bin/env python3
"""Aggregate r000 outputs and blind same-role probe-loss comparisons."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


BLIND_SEED = "confidence-output-probe-ablation500-blind-v1"
ROLES = ("confident", "hesitant")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--experiment", type=Path, required=True)
    return parser.parse_args()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
    authority = json.loads((experiment / "PROBE_ABLATION_AUTHORITY.json").read_text(encoding="utf-8"))
    cohort = read_jsonl(experiment / authority["cohort_file"])
    expected = [row["eval_id"] for row in cohort]
    if len(expected) != 500 or len(set(expected)) != 500:
        raise ValueError("cohort membership is not 500 unique rows")

    all_outputs: dict[str, list[dict[str, Any]]] = {}
    cells = []
    for run_id in ("confident_r000", "hesitant_r000"):
        rows = []
        for shard_index in range(5):
            cell = experiment / f"outputs/probe_ablation_generation/{run_id}/shard_{shard_index:02d}"
            data_path = cell / f"{run_id}.jsonl"
            summary_path = cell / f"{run_id}.summary.json"
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            shard_rows = read_jsonl(data_path)
            if summary.get("status") != "COMPLETE" or len(shard_rows) != 100 or summary.get("rows") != 100:
                raise ValueError(f"incomplete cell: {run_id} shard {shard_index}")
            if sha256(data_path) != summary.get("output_jsonl_sha256"):
                raise ValueError(f"output hash mismatch: {data_path}")
            rows.extend(shard_rows)
            cells.append({"run_id": run_id, "shard_index": shard_index, "summary_sha256": sha256(summary_path)})
        by_id = {row["item_id"]: row for row in rows}
        if len(rows) != 500 or set(by_id) != set(expected):
            raise ValueError(f"membership mismatch for {run_id}")
        all_outputs[run_id] = [by_id[item_id] for item_id in expected]
        write_jsonl(experiment / f"outputs/probe_ablation_combined/{run_id}.jsonl", all_outputs[run_id])

    for run_id in ("confident_r010", "hesitant_r010"):
        path = experiment / f"outputs/combined/{run_id}.jsonl"
        rows = read_jsonl(path)
        by_id = {row["item_id"]: row for row in rows}
        if len(rows) != 500 or set(by_id) != set(expected):
            raise ValueError(f"existing r010 membership mismatch for {run_id}")
        all_outputs[run_id] = [by_id[item_id] for item_id in expected]

    packet = []
    key = []
    for role in ROLES:
        guided_id = f"{role}_r010"
        baseline_id = f"{role}_r000"
        for index, source in enumerate(cohort, start=1):
            eval_id = source["eval_id"]
            guided = all_outputs[guided_id][index - 1]
            baseline = all_outputs[baseline_id][index - 1]
            guided_is_a = int(hashlib.sha256(f"{BLIND_SEED}\0{role}\0{eval_id}".encode()).hexdigest(), 16) % 2 == 0
            answer_a, answer_b = (guided, baseline) if guided_is_a else (baseline, guided)
            blind_id = f"{role.upper()}-ABLATE500-{index:04d}"
            packet.append({"blind_id": blind_id, "question": source["question"], "response_A": answer_a["response"], "response_B": answer_b["response"]})
            key.append(
                {
                    "A_source": guided_id if guided_is_a else baseline_id,
                    "B_source": baseline_id if guided_is_a else guided_id,
                    "baseline_source": baseline_id,
                    "blind_id": blind_id,
                    "eval_id": eval_id,
                    "expected_more_confident": guided_id if role == "confident" else baseline_id,
                    "guided_source": guided_id,
                    "role": role,
                }
            )
    packet_path = experiment / "outputs/probe_ablation_blind/PROBE_ABLATION500_PACKET.jsonl"
    key_path = experiment / "outputs/probe_ablation_blind/PROBE_ABLATION500_KEY.jsonl"
    write_jsonl(packet_path, packet)
    write_jsonl(key_path, key)
    summary = {
        "blind_pairs": 1000,
        "blinding_seed": BLIND_SEED,
        "generation_cells": cells,
        "key_sha256": sha256(key_path),
        "missing_pairs": 0,
        "packet_sha256": sha256(packet_path),
        "schema": "confidence-output-probe-ablation500-aggregation-v1",
        "status": "READY_FOR_BLIND_JUDGE",
    }
    (experiment / "outputs/PROBE_ABLATION_AGGREGATION.json").write_text(
        json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
