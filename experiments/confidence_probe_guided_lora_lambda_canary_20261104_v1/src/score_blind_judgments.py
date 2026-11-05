#!/usr/bin/env python3
"""Strictly score blind judgments and apply the frozen DEV lambda rule."""
from __future__ import annotations

import argparse
import json
import math
import statistics
from pathlib import Path
from typing import Any


ALLOWED_DECISIONS = {"A", "B", "tie", "cannot_judge"}
REQUIRED_RESULT_FIELDS = {
    "blind_id",
    "stronger_commitment",
    "material_content_difference",
    "fluency_issue_A",
    "fluency_issue_B",
    "length_dominates_judgment",
    "notes",
}
RATIOS = (0.0, 0.05, 0.10)
DEV_SPLIT = "lora_dev"
MIN_DIRECT_IMPROVEMENT = 0.05
MIN_DECOMPOSITION_CREDIT = 0.55
MAX_QUALITY_RATE_INCREASE = 0.05


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--primary-packet", type=Path, required=True)
    parser.add_argument("--primary-key", type=Path, required=True)
    parser.add_argument("--primary-results", type=Path, required=True)
    parser.add_argument("--decomposition-packet", type=Path, required=True)
    parser.add_argument("--decomposition-key", type=Path, required=True)
    parser.add_argument("--decomposition-results", type=Path, required=True)
    parser.add_argument("--aggregate-summary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not rows:
        raise ValueError(f"empty JSONL: {path}")
    return rows


def index_unique(rows: list[dict[str, Any]], label: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for row in rows:
        identifier = row.get("blind_id")
        if not isinstance(identifier, str) or not identifier or identifier in result:
            raise ValueError(f"{label}: blind IDs must be unique nonempty strings")
        result[identifier] = row
    return result


def validate_results(
    packet_rows: list[dict[str, Any]],
    key_rows: list[dict[str, Any]],
    result_rows: list[dict[str, Any]],
    label: str,
) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    packet = index_unique(packet_rows, f"{label} packet")
    key = index_unique(key_rows, f"{label} key")
    results = index_unique(result_rows, f"{label} results")
    if set(packet) != set(key) or set(packet) != set(results):
        raise ValueError(f"{label}: packet/key/results blind-ID sets differ")
    joined = []
    for blind_id in sorted(packet):
        result = results[blind_id]
        if set(result) != REQUIRED_RESULT_FIELDS:
            raise ValueError(f"{label} {blind_id}: result fields differ from frozen schema")
        if result["stronger_commitment"] not in ALLOWED_DECISIONS:
            raise ValueError(f"{label} {blind_id}: invalid stronger_commitment")
        for field in (
            "material_content_difference",
            "fluency_issue_A",
            "fluency_issue_B",
            "length_dominates_judgment",
        ):
            if type(result[field]) is not bool:
                raise ValueError(f"{label} {blind_id}: {field} must be boolean")
        if not isinstance(result["notes"], str) or len(result["notes"]) > 1000:
            raise ValueError(f"{label} {blind_id}: invalid notes")
        joined.append((key[blind_id], result))
    return joined


def chosen_source(key: dict[str, Any], result: dict[str, Any]) -> str | None:
    decision = result["stronger_commitment"]
    if decision == "A":
        return key["A_source"]
    if decision == "B":
        return key["B_source"]
    return None


def quality_flags(result: dict[str, Any]) -> dict[str, float]:
    return {
        "material": float(result["material_content_difference"]),
        "fluency": float(result["fluency_issue_A"] or result["fluency_issue_B"]),
        "length_dominated": float(result["length_dominates_judgment"]),
    }


def summarize_credits(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        raise ValueError("cannot summarize an empty judgment cell")
    return {
        "rows": len(rows),
        "directional_credit_all_rows": float(statistics.fmean(row["credit"] for row in rows)),
        "wins": sum(row["credit"] == 1.0 for row in rows),
        "losses": sum(row["credit"] == 0.0 for row in rows),
        "ties": sum(row["decision"] == "tie" for row in rows),
        "cannot_judge": sum(row["decision"] == "cannot_judge" for row in rows),
        "material_content_difference_rate": float(statistics.fmean(row["material"] for row in rows)),
        "fluency_issue_rate": float(statistics.fmean(row["fluency"] for row in rows)),
        "length_dominated_rate": float(statistics.fmean(row["length_dominated"] for row in rows)),
    }


def score_primary(joined: list[tuple[dict[str, Any], dict[str, Any]]]) -> dict[tuple[float, str], dict[str, Any]]:
    cells: dict[tuple[float, str], list[dict[str, Any]]] = {}
    for key, result in joined:
        ratio = float(key["ratio"])
        split = key["split"]
        source = chosen_source(key, result)
        credit = 1.0 if source == "confident" else 0.0 if source == "hesitant" else 0.5
        flags = quality_flags(result)
        cells.setdefault((ratio, split), []).append(
            {"credit": credit, "decision": result["stronger_commitment"], **flags}
        )
    return {cell: summarize_credits(rows) for cell, rows in cells.items()}


def score_decomposition(
    joined: list[tuple[dict[str, Any], dict[str, Any]]]
) -> dict[tuple[str, float, str], dict[str, Any]]:
    cells: dict[tuple[str, float, str], list[dict[str, Any]]] = {}
    for key, result in joined:
        role = key["role"]
        ratio = float(key["guided_ratio"])
        split = key["split"]
        source = chosen_source(key, result)
        expected_stronger = "guided" if role == "confident" else "baseline"
        credit = 1.0 if source == expected_stronger else 0.0 if source is not None else 0.5
        flags = quality_flags(result)
        cells.setdefault((role, ratio, split), []).append(
            {"credit": credit, "decision": result["stronger_commitment"], **flags}
        )
    return {cell: summarize_credits(rows) for cell, rows in cells.items()}


def direct_mechanical_gate(aggregate: dict[str, Any], ratio: float) -> dict[str, Any]:
    records = aggregate.get("direct_confident_vs_hesitant", [])
    record = next((row for row in records if float(row.get("ratio", -1)) == ratio), None)
    if record is None:
        raise ValueError(f"aggregate summary lacks direct ratio {ratio}")
    dev = record.get("by_split", {}).get(DEV_SPLIT)
    if not isinstance(dev, dict):
        raise ValueError(f"aggregate summary lacks {DEV_SPLIT} for ratio {ratio}")
    capped = int(dev.get("confident_capped", -1)) + int(dev.get("hesitant_capped", -1))
    empty = int(dev.get("confident_empty", -1)) + int(dev.get("hesitant_empty", -1))
    return {"capped": capped, "empty": empty, "pass": capped == 0 and empty == 0}


def select_ratio(
    primary: dict[tuple[float, str], dict[str, Any]],
    decomposition: dict[tuple[str, float, str], dict[str, Any]],
    aggregate: dict[str, Any],
) -> dict[str, Any]:
    baseline = primary[(0.0, DEV_SPLIT)]
    candidates = []
    selected = None
    for ratio in RATIOS[1:]:
        direct = primary[(ratio, DEV_SPLIT)]
        conf = decomposition[("confident", ratio, DEV_SPLIT)]
        hes = decomposition[("hesitant", ratio, DEV_SPLIT)]
        mechanical = direct_mechanical_gate(aggregate, ratio)
        improvement = direct["directional_credit_all_rows"] - baseline["directional_credit_all_rows"]
        quality_pass = all(
            direct[field] <= baseline[field] + MAX_QUALITY_RATE_INCREASE + 1e-12
            for field in (
                "material_content_difference_rate",
                "fluency_issue_rate",
                "length_dominated_rate",
            )
        )
        passes = (
            improvement >= MIN_DIRECT_IMPROVEMENT
            and conf["directional_credit_all_rows"] >= MIN_DECOMPOSITION_CREDIT
            and hes["directional_credit_all_rows"] >= MIN_DECOMPOSITION_CREDIT
            and quality_pass
            and mechanical["pass"]
        )
        candidates.append(
            {
                "ratio": ratio,
                "direct_credit": direct["directional_credit_all_rows"],
                "direct_improvement_vs_ratio0": improvement,
                "confident_decomposition_credit": conf["directional_credit_all_rows"],
                "hesitant_decomposition_credit": hes["directional_credit_all_rows"],
                "quality_noninferiority_pass": quality_pass,
                "mechanical_gate": mechanical,
                "passes_frozen_rule": passes,
            }
        )
        if passes and selected is None:
            selected = ratio
    return {
        "selection_split": DEV_SPLIT,
        "behavior_canary_used_for_selection": False,
        "rule": {
            "choose": "smallest positive candidate satisfying every gate; otherwise no_selection",
            "min_direct_improvement": MIN_DIRECT_IMPROVEMENT,
            "min_each_same_role_decomposition_credit": MIN_DECOMPOSITION_CREDIT,
            "max_quality_rate_increase_vs_ratio0": MAX_QUALITY_RATE_INCREASE,
            "capped_or_empty_allowed": 0,
            "tie_and_cannot_judge_credit": 0.5,
        },
        "baseline_ratio0": baseline,
        "candidates": candidates,
        "decision": "SELECT" if selected is not None else "NO_SELECTION",
        "selected_ratio": selected,
    }


def serialize_cells(cells: dict[tuple[Any, ...], dict[str, Any]]) -> list[dict[str, Any]]:
    output = []
    for key, value in sorted(cells.items(), key=lambda item: tuple(str(x) for x in item[0])):
        if len(key) == 2:
            ratio, split = key
            output.append({"ratio": ratio, "split": split, **value})
        else:
            role, ratio, split = key
            output.append({"role": role, "ratio": ratio, "split": split, **value})
    return output


def main() -> None:
    args = parse_args()
    if args.output.exists():
        raise FileExistsError(f"refuse to overwrite score output: {args.output}")
    primary_joined = validate_results(
        read_jsonl(args.primary_packet),
        read_jsonl(args.primary_key),
        read_jsonl(args.primary_results),
        "primary",
    )
    decomposition_joined = validate_results(
        read_jsonl(args.decomposition_packet),
        read_jsonl(args.decomposition_key),
        read_jsonl(args.decomposition_results),
        "decomposition",
    )
    primary = score_primary(primary_joined)
    decomposition = score_decomposition(decomposition_joined)
    aggregate = json.loads(args.aggregate_summary.read_text(encoding="utf-8"))
    if aggregate.get("status") != "COMPLETE" or aggregate.get("missing_rows") != 0:
        raise ValueError("aggregate summary is not complete")
    selection = select_ratio(primary, decomposition, aggregate)
    output = {
        "schema": "confidence-probe-lambda-canary-blind-score-v1",
        "status": "COMPLETE",
        "research_status": "ENGINEERING_DEV_CANARY_ONLY_NOT_CONFIRMATORY",
        "all_judged_rows_retained": True,
        "primary_direct_confident_vs_hesitant": serialize_cells(primary),
        "same_role_decomposition": serialize_cells(decomposition),
        "lambda_selection": selection,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(output, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
