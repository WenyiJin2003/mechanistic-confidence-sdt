#!/usr/bin/env python3
"""Score blinded confident-r010 versus hesitant-r010 judgments."""

from __future__ import annotations

import argparse
import json
import random
import statistics
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--key", type=Path, required=True)
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def percentile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    index = (len(ordered) - 1) * probability
    lower = int(index)
    upper = min(lower + 1, len(ordered) - 1)
    weight = index - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def main() -> None:
    args = parse_args()
    packet = {row["blind_id"]: row for row in read_jsonl(args.packet)}
    key = {row["blind_id"]: row for row in read_jsonl(args.key)}
    results = {row["blind_id"]: row for row in read_jsonl(args.results)}
    if len(packet) != 500 or set(packet) != set(key) or set(packet) != set(results):
        raise ValueError("packet, key, and result memberships must match all 500 pairs")
    credits = []
    decisions = {"confident_win": 0, "hesitant_win": 0, "tie": 0, "cannot_judge": 0}
    quality = {"material_content_difference": 0, "fluency_issue_A": 0, "fluency_issue_B": 0, "length_dominates_judgment": 0}
    for blind_id in sorted(packet):
        result = results[blind_id]
        decision = result["stronger_commitment"]
        if decision in {"A", "B"}:
            source = key[blind_id][f"{decision}_source"]
            if source == "confident_r010":
                credits.append(1.0)
                decisions["confident_win"] += 1
            else:
                credits.append(0.0)
                decisions["hesitant_win"] += 1
        elif decision == "tie":
            credits.append(0.5)
            decisions["tie"] += 1
        elif decision == "cannot_judge":
            credits.append(0.5)
            decisions["cannot_judge"] += 1
        else:
            raise ValueError(f"unexpected decision for {blind_id}: {decision}")
        for field in quality:
            quality[field] += int(bool(result[field]))
    rng = random.Random(20261105)
    boot = []
    for _ in range(10000):
        boot.append(statistics.fmean(credits[rng.randrange(len(credits))] for _ in credits))
    score = {
        "bootstrap_seed": 20261105,
        "bootstrap_samples": 10000,
        "decision_counts": decisions,
        "directional_credit": statistics.fmean(credits),
        "directional_credit_95pct_bootstrap_ci": [percentile(boot, 0.025), percentile(boot, 0.975)],
        "excluded_rows": 0,
        "missing_rows": 0,
        "pairs": 500,
        "quality_flag_counts": quality,
        "schema": "confidence-output-direct-eval500-score-v1",
        "status": "COMPLETE",
        "tie_and_cannot_credit": 0.5,
    }
    if args.output.exists():
        raise FileExistsError(args.output)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(score, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(score, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
