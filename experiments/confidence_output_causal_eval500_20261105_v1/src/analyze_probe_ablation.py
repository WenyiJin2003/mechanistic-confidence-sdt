#!/usr/bin/env python3
"""Diagnose internal and behavioral changes from adding probe loss."""

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


def paired(values_a: list[float], values_b: list[float], seed: int) -> dict[str, Any]:
    diffs = [a - b for a, b in zip(values_a, values_b, strict=True)]
    rng = random.Random(seed)
    boot = [statistics.fmean(diffs[rng.randrange(len(diffs))] for _ in diffs) for _ in range(10000)]
    return {
        "guided_mean": statistics.fmean(values_a),
        "ce_only_mean": statistics.fmean(values_b),
        "guided_minus_ce_only": statistics.fmean(diffs),
        "guided_minus_ce_only_95pct_bootstrap_ci": [percentile(boot, 0.025), percentile(boot, 0.975)],
    }


def main() -> None:
    args = parse_args()
    experiment = args.experiment.resolve()
    keys = {row["blind_id"]: row for row in read_jsonl(experiment / "outputs/probe_ablation_blind/PROBE_ABLATION500_KEY.jsonl")}
    results = {row["blind_id"]: row for row in read_jsonl(experiment / "outputs/probe_ablation_judgments/claude_opus_medium_v1/RESULTS.jsonl")}
    run = json.loads((experiment / "outputs/probe_ablation_judgments/claude_opus_medium_v1/RUN_COMPLETE.json").read_text())
    diagnostics: dict[str, Any] = {}
    for role_index, role in enumerate(("confident", "hesitant")):
        guided_id = f"{role}_r010"
        baseline_id = f"{role}_r000"
        guided_rows = read_jsonl(experiment / f"outputs/combined/{guided_id}.jsonl")
        baseline_rows = read_jsonl(experiment / f"outputs/probe_ablation_combined/{baseline_id}.jsonl")
        guided = {row["item_id"]: row for row in guided_rows}
        baseline = {row["item_id"]: row for row in baseline_rows}
        if len(guided) != 500 or set(guided) != set(baseline):
            raise ValueError(f"{role}: generation memberships differ")
        clean = {"desired": 0, "opposite": 0, "tie": 0, "cannot_judge": 0, "rows": 0}
        fluency = {guided_id: 0, baseline_id: 0}
        material = 0
        for blind_id, key in keys.items():
            if key["role"] != role:
                continue
            judgment = results[blind_id]
            material += int(judgment["material_content_difference"])
            if judgment["fluency_issue_A"]:
                fluency[key["A_source"]] += 1
            if judgment["fluency_issue_B"]:
                fluency[key["B_source"]] += 1
            is_clean = not (
                judgment["material_content_difference"]
                or judgment["fluency_issue_A"]
                or judgment["fluency_issue_B"]
                or judgment["length_dominates_judgment"]
            )
            if is_clean:
                clean["rows"] += 1
                decision = judgment["stronger_commitment"]
                selected = key.get(f"{decision}_source") if decision in {"A", "B"} else None
                if selected == key["expected_more_confident"]:
                    clean["desired"] += 1
                elif selected is not None:
                    clean["opposite"] += 1
                elif decision == "tie":
                    clean["tie"] += 1
                else:
                    clean["cannot_judge"] += 1
        ordered_ids = [row["item_id"] for row in guided_rows]
        exact_equal = sum(guided[item]["response"] == baseline[item]["response"] for item in ordered_ids)
        metrics = {}
        for metric_index, field in enumerate(("l14_score", "equal28_score", "generated_token_count", "response_word_count")):
            metrics[field] = paired(
                [float(guided[item][field]) for item in ordered_ids],
                [float(baseline[item][field]) for item in ordered_ids],
                20261105 + role_index * 10 + metric_index,
            )
        diagnostics[role] = {
            "ce_only_hit_max_new_tokens": sum(bool(baseline[item]["hit_max_new_tokens"]) for item in ordered_ids),
            "ce_only_refusal_heuristic": sum(bool(baseline[item]["refusal_heuristic"]) for item in ordered_ids),
            "clean_subset": clean,
            "exact_response_identity": exact_equal,
            "fluency_issue_counts": fluency,
            "guided_hit_max_new_tokens": sum(bool(guided[item]["hit_max_new_tokens"]) for item in ordered_ids),
            "guided_refusal_heuristic": sum(bool(guided[item]["refusal_heuristic"]) for item in ordered_ids),
            "material_content_difference": material,
            "metrics": metrics,
        }
    list_cost = sum(float(batch.get("total_cost_usd_field") or 0.0) for batch in run["batches"])
    output = {
        "claude_canonical_models": sorted({model for batch in run["batches"] for model in (batch.get("model_usage") or {})}),
        "claude_list_cost_usd_fields_sum_not_invoice": list_cost,
        "confident": diagnostics["confident"],
        "hesitant": diagnostics["hesitant"],
        "pairs_per_role": 500,
        "schema": "confidence-output-probe-ablation500-diagnostics-v1",
        "status": "COMPLETE",
    }
    path = experiment / "outputs/PROBE_ABLATION500_DIAGNOSTICS.json"
    if path.exists():
        raise FileExistsError(path)
    path.write_text(json.dumps(output, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, ensure_ascii=False, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
