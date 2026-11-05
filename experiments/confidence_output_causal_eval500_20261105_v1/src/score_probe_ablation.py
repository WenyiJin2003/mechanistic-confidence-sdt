#!/usr/bin/env python3
"""Score same-role probe-loss versus CE-only confidence comparisons."""

from __future__ import annotations

import argparse
import json
import random
import statistics
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--experiment", type=Path, required=True)
    return parser.parse_args()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def percentile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def summarize(rows: list[dict[str, Any]], seed: int) -> dict[str, Any]:
    credits = [row["credit"] for row in rows]
    rng = random.Random(seed)
    boot = [statistics.fmean(credits[rng.randrange(len(credits))] for _ in credits) for _ in range(10000)]
    return {
        "cannot_judge": sum(row["decision"] == "cannot_judge" for row in rows),
        "desired_direction_wins": sum(row["credit"] == 1.0 for row in rows),
        "directional_credit": statistics.fmean(credits),
        "directional_credit_95pct_bootstrap_ci": [percentile(boot, 0.025), percentile(boot, 0.975)],
        "material_content_difference": sum(row["material"] for row in rows),
        "opposite_direction_wins": sum(row["credit"] == 0.0 for row in rows),
        "pairs": len(rows),
        "ties": sum(row["decision"] == "tie" for row in rows),
    }


def main() -> None:
    args = parse_args()
    experiment = args.experiment.resolve()
    keys = {row["blind_id"]: row for row in read_jsonl(experiment / "outputs/probe_ablation_blind/PROBE_ABLATION500_KEY.jsonl")}
    results = {row["blind_id"]: row for row in read_jsonl(experiment / "outputs/probe_ablation_judgments/claude_opus_medium_v1/RESULTS.jsonl")}
    if len(keys) != 1000 or set(keys) != set(results):
        raise ValueError("all 1,000 blind comparisons must be present")
    by_role: dict[str, list[dict[str, Any]]] = {"confident": [], "hesitant": []}
    for blind_id in sorted(keys):
        key = keys[blind_id]
        result = results[blind_id]
        decision = result["stronger_commitment"]
        selected = key.get(f"{decision}_source") if decision in {"A", "B"} else None
        credit = 1.0 if selected == key["expected_more_confident"] else 0.0 if selected is not None else 0.5
        by_role[key["role"]].append(
            {
                "credit": credit,
                "decision": decision,
                "material": int(result["material_content_difference"]),
            }
        )
    confident = summarize(by_role["confident"], 20261105)
    hesitant = summarize(by_role["hesitant"], 20261106)
    combined = summarize(by_role["confident"] + by_role["hesitant"], 20261107)
    output = {
        "combined_target_direction": combined,
        "confident_probe_loss_vs_ce_only": confident,
        "excluded": 0,
        "hesitant_probe_loss_vs_ce_only": hesitant,
        "interpretation_rule": {
            "confident": "desired win means confident_r010 judged more confident than confident_r000",
            "hesitant": "desired win means hesitant_r000 judged more confident than hesitant_r010",
            "tie_and_cannot_credit": 0.5,
        },
        "missing": 0,
        "schema": "confidence-output-probe-ablation500-score-v1",
        "status": "COMPLETE",
    }
    path = experiment / "outputs/PROBE_ABLATION500_SCORE.json"
    if path.exists():
        raise FileExistsError(path)
    path.write_text(json.dumps(output, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
