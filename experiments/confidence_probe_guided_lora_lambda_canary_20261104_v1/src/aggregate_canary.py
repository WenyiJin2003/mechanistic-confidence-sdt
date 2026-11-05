#!/usr/bin/env python3
"""Aggregate six lambda-canary runs and build a deterministic blind A/B packet."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
from pathlib import Path
from typing import Any


ROLES = ("confident", "hesitant")
RATIOS = (0.0, 0.05, 0.10)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-manifest", type=Path, required=True)
    parser.add_argument("--evaluation-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--blind-seed", default="confidence-lambda-canary-20261104-v1")
    return parser.parse_args()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def load_grid(manifest_path: Path, evaluation_dir: Path) -> dict[tuple[str, float], dict[tuple[str, str], dict[str, Any]]]:
    document = json.loads(manifest_path.read_text(encoding="utf-8"))
    runs = document.get("runs")
    if not isinstance(runs, list) or len(runs) != 6:
        raise ValueError("manifest must contain exactly six runs")
    grid: dict[tuple[str, float], dict[tuple[str, str], dict[str, Any]]] = {}
    reference_keys: set[tuple[str, str]] | None = None
    for run in runs:
        role, ratio, run_id = run.get("role"), float(run.get("target_aux_gradient_ratio")), run.get("run_id")
        if role not in ROLES or ratio not in RATIOS or not isinstance(run_id, str):
            raise ValueError("invalid run manifest cell")
        cell = (role, ratio)
        if cell in grid:
            raise ValueError(f"duplicate run cell: {cell}")
        rows = read_jsonl(evaluation_dir / f"{run_id}.jsonl")
        by_key: dict[tuple[str, str], dict[str, Any]] = {}
        for row in rows:
            key = (row["split"], row["item_id"])
            if key in by_key:
                raise ValueError(f"{run_id}: duplicate item {key}")
            if row.get("run_id") != run_id or row.get("role") != role or float(row.get("target_aux_gradient_ratio")) != ratio:
                raise ValueError(f"{run_id}: row binding mismatch")
            by_key[key] = row
        if not by_key:
            raise ValueError(f"{run_id}: empty evaluation")
        keys = set(by_key)
        if reference_keys is None:
            reference_keys = keys
        elif keys != reference_keys:
            missing = sorted(reference_keys - keys)
            extra = sorted(keys - reference_keys)
            raise ValueError(f"{run_id}: item mismatch; missing={missing[:3]} extra={extra[:3]}")
        grid[cell] = by_key
    expected = {(role, ratio) for role in ROLES for ratio in RATIOS}
    if set(grid) != expected:
        raise ValueError("evaluation grid is incomplete")
    return grid


def mean(values: list[float]) -> float:
    if not values or any(not math.isfinite(value) for value in values):
        raise ValueError("summary values must be finite and nonempty")
    return float(statistics.fmean(values))


def comparison_summary(
    baseline: dict[tuple[str, str], dict[str, Any]],
    guided: dict[tuple[str, str], dict[str, Any]],
    role: str,
    ratio: float,
) -> dict[str, Any]:
    rows = []
    for key in sorted(baseline):
        left, right = baseline[key], guided[key]
        if left.get("l14_score") is None or right.get("l14_score") is None:
            raise ValueError(f"missing score for {key}")
        rows.append(
            {
                "key": key,
                "l14_delta_guided_minus_baseline": float(right["l14_score"] - left["l14_score"]),
                "equal28_delta_guided_minus_baseline": float(right["equal28_score"] - left["equal28_score"]),
                "token_delta_guided_minus_baseline": int(right["response_token_count"] - left["response_token_count"]),
                "word_delta_guided_minus_baseline": int(right["response_word_count"] - left["response_word_count"]),
                "character_delta_guided_minus_baseline": int(right["response_character_count"] - left["response_character_count"]),
                "identical_response": right["response"] == left["response"],
            }
        )
    by_split: dict[str, dict[str, Any]] = {}
    for split in sorted({key[0] for key in baseline}):
        subset = [row for row in rows if row["key"][0] == split]
        by_split[split] = {
            "rows": len(subset),
            "mean_l14_delta_guided_minus_baseline": mean([row["l14_delta_guided_minus_baseline"] for row in subset]),
            "mean_equal28_delta_guided_minus_baseline": mean([row["equal28_delta_guided_minus_baseline"] for row in subset]),
            "mean_token_delta_guided_minus_baseline": mean([float(row["token_delta_guided_minus_baseline"]) for row in subset]),
            "identical_responses": sum(row["identical_response"] for row in subset),
        }
    return {
        "role": role,
        "guided_ratio": ratio,
        "expected_direction": "guided_more_confident" if role == "confident" else "guided_more_hesitant",
        "rows": len(rows),
        "mean_l14_delta_guided_minus_baseline": mean([row["l14_delta_guided_minus_baseline"] for row in rows]),
        "mean_equal28_delta_guided_minus_baseline": mean([row["equal28_delta_guided_minus_baseline"] for row in rows]),
        "mean_token_delta_guided_minus_baseline": mean([float(row["token_delta_guided_minus_baseline"]) for row in rows]),
        "mean_word_delta_guided_minus_baseline": mean([float(row["word_delta_guided_minus_baseline"]) for row in rows]),
        "mean_character_delta_guided_minus_baseline": mean([float(row["character_delta_guided_minus_baseline"]) for row in rows]),
        "identical_responses": sum(row["identical_response"] for row in rows),
        "baseline_empty": sum(row["empty_response"] for row in baseline.values()),
        "guided_empty": sum(row["empty_response"] for row in guided.values()),
        "baseline_refusal_heuristic": sum(row["refusal_heuristic"] for row in baseline.values()),
        "guided_refusal_heuristic": sum(row["refusal_heuristic"] for row in guided.values()),
        "baseline_capped": sum(row.get("hit_max_new_tokens", False) for row in baseline.values()),
        "guided_capped": sum(row.get("hit_max_new_tokens", False) for row in guided.values()),
        "by_split": by_split,
    }


def blind_assignment(seed: str, role: str, ratio: float, split: str, item_id: str) -> bool:
    payload = f"{seed}|{role}|{ratio:.2f}|{split}|{item_id}".encode("utf-8")
    return hashlib.sha256(payload).digest()[0] % 2 == 0


def direct_separation_summary(
    grid: dict[tuple[str, float], dict[tuple[str, str], dict[str, Any]]]
) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    baseline_gaps: dict[tuple[str, str], dict[str, float]] = {}
    for ratio in RATIOS:
        confident = grid[("confident", ratio)]
        hesitant = grid[("hesitant", ratio)]
        rows: list[dict[str, Any]] = []
        for key in sorted(confident):
            high, low = confident[key], hesitant[key]
            row = {
                "key": key,
                "l14_gap_confident_minus_hesitant": float(high["l14_score"] - low["l14_score"]),
                "equal28_gap_confident_minus_hesitant": float(high["equal28_score"] - low["equal28_score"]),
                "token_gap_confident_minus_hesitant": int(high["response_token_count"] - low["response_token_count"]),
                "confident_capped": bool(high.get("hit_max_new_tokens", False)),
                "hesitant_capped": bool(low.get("hit_max_new_tokens", False)),
                "identical_response": high["response"] == low["response"],
            }
            rows.append(row)
            if ratio == 0.0:
                baseline_gaps[key] = {
                    "l14": row["l14_gap_confident_minus_hesitant"],
                    "equal28": row["equal28_gap_confident_minus_hesitant"],
                }
        if ratio == 0.0:
            l14_changes = [0.0] * len(rows)
            equal28_changes = [0.0] * len(rows)
        else:
            l14_changes = [
                row["l14_gap_confident_minus_hesitant"] - baseline_gaps[row["key"]]["l14"]
                for row in rows
            ]
            equal28_changes = [
                row["equal28_gap_confident_minus_hesitant"] - baseline_gaps[row["key"]]["equal28"]
                for row in rows
            ]
        by_split = {}
        for split in sorted({key[0] for key in confident}):
            indices = [index for index, row in enumerate(rows) if row["key"][0] == split]
            by_split[split] = {
                "rows": len(indices),
                "mean_l14_gap_confident_minus_hesitant": mean(
                    [rows[index]["l14_gap_confident_minus_hesitant"] for index in indices]
                ),
                "mean_equal28_gap_confident_minus_hesitant": mean(
                    [rows[index]["equal28_gap_confident_minus_hesitant"] for index in indices]
                ),
                "mean_l14_gap_change_vs_ratio0": mean([l14_changes[index] for index in indices]),
                "mean_equal28_gap_change_vs_ratio0": mean([equal28_changes[index] for index in indices]),
                "confident_capped": sum(rows[index]["confident_capped"] for index in indices),
                "hesitant_capped": sum(rows[index]["hesitant_capped"] for index in indices),
                "confident_empty": sum(
                    confident[rows[index]["key"]]["empty_response"] for index in indices
                ),
                "hesitant_empty": sum(
                    hesitant[rows[index]["key"]]["empty_response"] for index in indices
                ),
            }
        summaries.append(
            {
                "ratio": ratio,
                "rows": len(rows),
                "mean_l14_gap_confident_minus_hesitant": mean(
                    [row["l14_gap_confident_minus_hesitant"] for row in rows]
                ),
                "mean_equal28_gap_confident_minus_hesitant": mean(
                    [row["equal28_gap_confident_minus_hesitant"] for row in rows]
                ),
                "mean_l14_gap_change_vs_ratio0": mean(l14_changes),
                "mean_equal28_gap_change_vs_ratio0": mean(equal28_changes),
                "mean_absolute_token_gap": mean(
                    [float(abs(row["token_gap_confident_minus_hesitant"])) for row in rows]
                ),
                "identical_responses": sum(row["identical_response"] for row in rows),
                "confident_capped": sum(row["confident_capped"] for row in rows),
                "hesitant_capped": sum(row["hesitant_capped"] for row in rows),
                "confident_empty": sum(confident[key]["empty_response"] for key in confident),
                "hesitant_empty": sum(hesitant[key]["empty_response"] for key in hesitant),
                "by_split": by_split,
            }
        )
    return summaries


def build_decomposition_blind_packet(
    grid: dict[tuple[str, float], dict[tuple[str, str], dict[str, Any]]], seed: str
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    packet: list[dict[str, Any]] = []
    key_rows: list[dict[str, Any]] = []
    for role in ROLES:
        baseline = grid[(role, 0.0)]
        for ratio in RATIOS[1:]:
            guided = grid[(role, ratio)]
            for split, item_id in sorted(baseline):
                base_row, guided_row = baseline[(split, item_id)], guided[(split, item_id)]
                guided_is_a = blind_assignment(seed, role, ratio, split, item_id)
                response_a = guided_row["response"] if guided_is_a else base_row["response"]
                response_b = base_row["response"] if guided_is_a else guided_row["response"]
                blind_id = hashlib.sha256(
                    f"{seed}|{role}|{ratio:.2f}|{split}|{item_id}|blind".encode("utf-8")
                ).hexdigest()[:20]
                packet.append(
                    {
                        "schema": "confidence-lambda-canary-blind-judge-item-v1",
                        "blind_id": blind_id,
                        "question": base_row["question"],
                        "response_A": response_a,
                        "response_B": response_b,
                        "judge_instruction": (
                            "Which response expresses stronger commitment to its substantive answer? "
                            "Judge expressed certainty, not correctness, helpfulness, length, or preference. "
                            "Return A, B, tie, or cannot_judge; separately flag material content or fluency differences."
                        ),
                    }
                )
                key_rows.append(
                    {
                        "blind_id": blind_id,
                        "role": role,
                        "guided_ratio": ratio,
                        "split": split,
                        "item_id": item_id,
                        "A_source": "guided" if guided_is_a else "baseline",
                        "B_source": "baseline" if guided_is_a else "guided",
                        "expected_effect": "guided_more_confident" if role == "confident" else "guided_more_hesitant",
                        "baseline_run_id": base_row["run_id"],
                        "guided_run_id": guided_row["run_id"],
                    }
                )
    if len({row["blind_id"] for row in packet}) != len(packet):
        raise RuntimeError("blind IDs collided")
    return packet, key_rows


def build_primary_direct_blind_packet(
    grid: dict[tuple[str, float], dict[tuple[str, str], dict[str, Any]]], seed: str
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    packet: list[dict[str, Any]] = []
    key_rows: list[dict[str, Any]] = []
    for ratio in RATIOS:
        confident = grid[("confident", ratio)]
        hesitant = grid[("hesitant", ratio)]
        for split, item_id in sorted(confident):
            high, low = confident[(split, item_id)], hesitant[(split, item_id)]
            confident_is_a = blind_assignment(seed + "|direct", "direct", ratio, split, item_id)
            response_a = high["response"] if confident_is_a else low["response"]
            response_b = low["response"] if confident_is_a else high["response"]
            blind_id = hashlib.sha256(
                f"{seed}|direct|{ratio:.2f}|{split}|{item_id}".encode("utf-8")
            ).hexdigest()[:20]
            packet.append(
                {
                    "schema": "confidence-lambda-canary-primary-blind-item-v1",
                    "blind_id": blind_id,
                    "question": high["question"],
                    "response_A": response_a,
                    "response_B": response_b,
                    "judge_instruction": (
                        "Which response expresses stronger commitment to its substantive answer? "
                        "Judge expressed certainty, not correctness, helpfulness, length, or preference. "
                        "Return A, B, tie, or cannot_judge; separately flag material content or fluency differences."
                    ),
                }
            )
            key_rows.append(
                {
                    "blind_id": blind_id,
                    "comparison_kind": "direct_confident_vs_hesitant",
                    "ratio": ratio,
                    "split": split,
                    "item_id": item_id,
                    "A_source": "confident" if confident_is_a else "hesitant",
                    "B_source": "hesitant" if confident_is_a else "confident",
                    "confident_run_id": high["run_id"],
                    "hesitant_run_id": low["run_id"],
                }
            )
    if len({row["blind_id"] for row in packet}) != len(packet):
        raise RuntimeError("primary blind IDs collided")
    return packet, key_rows


def write_jsonl_exclusive(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("x", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def main() -> None:
    args = parse_args()
    if args.output_dir.exists():
        raise FileExistsError(f"refuse to overwrite aggregation directory: {args.output_dir}")
    grid = load_grid(args.run_manifest.resolve(), args.evaluation_dir.resolve())
    comparisons = []
    for role in ROLES:
        for ratio in RATIOS[1:]:
            comparisons.append(comparison_summary(grid[(role, 0.0)], grid[(role, ratio)], role, ratio))
    direct_separation = direct_separation_summary(grid)
    primary_packet, primary_key = build_primary_direct_blind_packet(grid, args.blind_seed)
    decomposition_packet, decomposition_key = build_decomposition_blind_packet(grid, args.blind_seed)
    args.output_dir.mkdir(parents=True)
    write_jsonl_exclusive(args.output_dir / "PRIMARY_BLIND_JUDGE_PACKET.jsonl", primary_packet)
    write_jsonl_exclusive(args.output_dir / "PRIMARY_BLINDING_KEY.jsonl", primary_key)
    write_jsonl_exclusive(
        args.output_dir / "DECOMPOSITION_BLIND_JUDGE_PACKET.jsonl", decomposition_packet
    )
    write_jsonl_exclusive(args.output_dir / "DECOMPOSITION_BLINDING_KEY.jsonl", decomposition_key)
    summary = {
        "schema": "confidence-probe-lambda-canary-aggregate-v1",
        "status": "COMPLETE",
        "research_status": "ENGINEERING_DEV_CANARY_ONLY_NOT_CONFIRMATORY",
        "primary_endpoint": (
            "direct same-question confident-vs-hesitant blind judgment at each ratio, "
            "and directional-credit gap change versus ratio0; not yet executed"
        ),
        "mechanistic_endpoints_secondary": ["L14", "equal28"],
        "direct_confident_vs_hesitant": direct_separation,
        "same_role_decomposition": comparisons,
        "primary_blind_items": len(primary_packet),
        "decomposition_blind_items": len(decomposition_packet),
        "blind_seed": args.blind_seed,
        "missing_rows": 0,
        "excluded_rows": 0,
    }
    with (args.output_dir / "AGGREGATE_SUMMARY.json").open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2) + "\n")


if __name__ == "__main__":
    main()
