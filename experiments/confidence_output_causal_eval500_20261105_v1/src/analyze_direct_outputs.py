#!/usr/bin/env python3
"""Compute paired output, readout, quality, and judge diagnostics."""

from __future__ import annotations

import argparse
import json
import math
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
    index = (len(ordered) - 1) * probability
    lower = int(index)
    upper = min(lower + 1, len(ordered) - 1)
    weight = index - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def paired_summary(confident: list[float], hesitant: list[float], seed: int) -> dict[str, Any]:
    differences = [left - right for left, right in zip(confident, hesitant, strict=True)]
    rng = random.Random(seed)
    boot = []
    for _ in range(10000):
        boot.append(statistics.fmean(differences[rng.randrange(len(differences))] for _ in differences))
    return {
        "confident_mean": statistics.fmean(confident),
        "hesitant_mean": statistics.fmean(hesitant),
        "paired_mean_difference_confident_minus_hesitant": statistics.fmean(differences),
        "paired_difference_95pct_bootstrap_ci": [percentile(boot, 0.025), percentile(boot, 0.975)],
    }


def one_sided_binomial_tail(wins: int, trials: int) -> float:
    return sum(math.comb(trials, k) for k in range(wins, trials + 1)) / (2**trials)


def main() -> None:
    args = parse_args()
    experiment = args.experiment.resolve()
    conf_rows = read_jsonl(experiment / "outputs/combined/confident_r010.jsonl")
    hes_rows = read_jsonl(experiment / "outputs/combined/hesitant_r010.jsonl")
    key_rows = read_jsonl(experiment / "outputs/blind/DIRECT500_KEY.jsonl")
    judge_rows = read_jsonl(experiment / "outputs/judgments/claude_opus_medium_v1/RESULTS.jsonl")
    run = json.loads((experiment / "outputs/judgments/claude_opus_medium_v1/RUN_COMPLETE.json").read_text())
    conf = {row["item_id"]: row for row in conf_rows}
    hes = {row["item_id"]: row for row in hes_rows}
    keys = {row["blind_id"]: row for row in key_rows}
    judgments = {row["blind_id"]: row for row in judge_rows}
    if len(conf) != 500 or set(conf) != set(hes) or len(keys) != 500 or set(keys) != set(judgments):
        raise ValueError("all 500 paired memberships must match")

    exact_equal = sum(conf[item]["response"] == hes[item]["response"] for item in conf)
    normalized_equal = sum(
        " ".join(conf[item]["response"].split()).casefold() == " ".join(hes[item]["response"].split()).casefold()
        for item in conf
    )
    mapped_fluency = {"confident_r010": 0, "hesitant_r010": 0}
    clean_counts = {"confident_win": 0, "hesitant_win": 0, "tie": 0, "cannot_judge": 0}
    clean_rows = 0
    non_tie_confident = 0
    non_tie_hesitant = 0
    for blind_id in sorted(keys):
        key = keys[blind_id]
        judgment = judgments[blind_id]
        if judgment["fluency_issue_A"]:
            mapped_fluency[key["A_source"]] += 1
        if judgment["fluency_issue_B"]:
            mapped_fluency[key["B_source"]] += 1
        decision = judgment["stronger_commitment"]
        chosen = key.get(f"{decision}_source") if decision in {"A", "B"} else None
        if chosen == "confident_r010":
            non_tie_confident += 1
        elif chosen == "hesitant_r010":
            non_tie_hesitant += 1
        clean = not (
            judgment["material_content_difference"]
            or judgment["fluency_issue_A"]
            or judgment["fluency_issue_B"]
            or judgment["length_dominates_judgment"]
        )
        if clean:
            clean_rows += 1
            if chosen == "confident_r010":
                clean_counts["confident_win"] += 1
            elif chosen == "hesitant_r010":
                clean_counts["hesitant_win"] += 1
            elif decision == "tie":
                clean_counts["tie"] += 1
            else:
                clean_counts["cannot_judge"] += 1

    model_usage: dict[str, Any] = {}
    list_cost = 0.0
    for batch in run["batches"]:
        list_cost += float(batch.get("total_cost_usd_field") or 0.0)
        for model_id, usage in (batch.get("model_usage") or {}).items():
            model_usage.setdefault(model_id, {"batches": 0, "input_tokens": 0, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0, "output_tokens": 0, "thinking_tokens": 0})
            target = model_usage[model_id]
            target["batches"] += 1
            target["input_tokens"] += int(usage.get("inputTokens") or 0)
            target["cache_creation_input_tokens"] += int(usage.get("cacheCreationInputTokens") or 0)
            target["cache_read_input_tokens"] += int(usage.get("cacheReadInputTokens") or 0)
            target["output_tokens"] += int(usage.get("outputTokens") or 0)
            target["thinking_tokens"] += int(usage.get("thinkingTokens") or 0)

    numeric = {
        "generated_token_count": ([float(row["generated_token_count"]) for row in conf_rows], [float(row["generated_token_count"]) for row in hes_rows]),
        "response_word_count": ([float(row["response_word_count"]) for row in conf_rows], [float(row["response_word_count"]) for row in hes_rows]),
        "l14_score": ([float(row["l14_score"]) for row in conf_rows], [float(row["l14_score"]) for row in hes_rows]),
        "equal28_score": ([float(row["equal28_score"]) for row in conf_rows], [float(row["equal28_score"]) for row in hes_rows]),
    }
    output = {
        "claude_list_cost_usd_fields_sum": list_cost,
        "claude_model_usage": model_usage,
        "clean_judge_subset": {"rows": clean_rows, **clean_counts},
        "exact_response_identity": {"exact": exact_equal, "normalized": normalized_equal, "pairs": 500},
        "generation_flags": {
            "confident_hit_max_new_tokens": sum(bool(row["hit_max_new_tokens"]) for row in conf_rows),
            "confident_refusal_heuristic": sum(bool(row["refusal_heuristic"]) for row in conf_rows),
            "hesitant_hit_max_new_tokens": sum(bool(row["hit_max_new_tokens"]) for row in hes_rows),
            "hesitant_refusal_heuristic": sum(bool(row["refusal_heuristic"]) for row in hes_rows),
        },
        "mapped_fluency_issue_counts": mapped_fluency,
        "metrics": {name: paired_summary(left, right, 20261105 + index) for index, (name, (left, right)) in enumerate(numeric.items())},
        "non_tie_directional": {
            "confident_wins": non_tie_confident,
            "hesitant_wins": non_tie_hesitant,
            "non_ties": non_tie_confident + non_tie_hesitant,
            "confident_win_rate": non_tie_confident / (non_tie_confident + non_tie_hesitant),
            "one_sided_exact_binomial_p_confident_greater": one_sided_binomial_tail(non_tie_confident, non_tie_confident + non_tie_hesitant),
        },
        "pairs": 500,
        "schema": "confidence-output-direct-eval500-diagnostics-v1",
        "status": "COMPLETE",
    }
    path = experiment / "outputs/DIRECT500_DIAGNOSTICS.json"
    if path.exists():
        raise FileExistsError(path)
    path.write_text(json.dumps(output, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, ensure_ascii=False, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
