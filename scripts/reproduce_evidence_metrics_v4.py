#!/usr/bin/env python3
"""Recompute published v4 metrics without a tokenizer, weights or model calls."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np

from confidence_pilot.common import file_hash, load_config, read_jsonl, resolve
from confidence_pilot.evidence_analysis_v4 import analyze, fit_readouts


def equivalent(left, right):
    if isinstance(left, dict) and isinstance(right, dict):
        return left.keys() == right.keys() and all(equivalent(left[k], right[k]) for k in left)
    if isinstance(left, list) and isinstance(right, list):
        return len(left) == len(right) and all(equivalent(a, b) for a, b in zip(left, right))
    if isinstance(left, bool) or isinstance(right, bool):
        return left == right
    if isinstance(left, (int, float, np.number)) and isinstance(right, (int, float, np.number)):
        return math.isclose(float(left), float(right), rel_tol=1e-12, abs_tol=1e-12)
    return left == right


def run(config_path):
    start = time.monotonic()
    config = load_config(config_path)
    output = resolve(config["output"]["results_dir"])
    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    for name in ("extraction_rows.jsonl", "hidden_states.npz", "behavior_outputs.jsonl", "metrics.json"):
        if file_hash(output / name) != manifest["artifacts"][name]:
            raise ValueError(f"Published artifact hash differs: {name}")
    for path in config["data"].values():
        if file_hash(path) != manifest["freeze_sha256"][path]:
            raise ValueError(f"Frozen input hash differs: {path}")
    rows = read_jsonl(output / "extraction_rows.jsonl")
    variants = read_jsonl(config["data"]["variants"])
    if len(rows) != len(variants):
        raise ValueError("Frozen inputs and extracted rows differ in length")
    for expected, actual in zip(variants, rows):
        if any(actual.get(key) != value for key, value in expected.items()):
            raise ValueError("An extracted input differs from the frozen data")
    with np.load(output / "hidden_states.npz") as archive:
        hidden = archive["hidden_states"]
        if archive["variant_ids"].tolist() != [r["variant_id"] for r in rows]:
            raise ValueError("Hidden states are misaligned with row IDs")
    fitted = fit_readouts(rows, hidden, config)
    behavior = read_jsonl(output / "behavior_outputs.jsonl")
    metrics = analyze(rows, hidden, fitted, behavior, config)
    expected = json.loads((output / "metrics.json").read_text(encoding="utf-8"))
    if not equivalent(metrics, expected):
        raise ValueError("Recomputed metric differs from the published result")
    return {"passed": True, "all_metrics_and_gates_reproduced": True,
            "response_rows": len(rows), "behavior_prompts": len(behavior),
            "model_calls": 0, "model_weights_required": False, "files_changed": 0,
            "elapsed_seconds": time.monotonic() - start}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/evidence_confidence_v4.yaml")
    print(json.dumps(run(parser.parse_args().config), indent=2))
