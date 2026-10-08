#!/usr/bin/env python3
"""Cache-only correctness/certainty audit; never imports a model runtime."""
from __future__ import annotations

import argparse
import json
import platform
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from confidence_pilot.common import file_hash, load_config, read_jsonl, resolve, write_json, write_npz
from confidence_pilot.separation_audit import analyze_separation


def _load_cache(rows_path, hidden_path):
    rows = read_jsonl(rows_path)
    with np.load(resolve(hidden_path), allow_pickle=False) as cached:
        ids = np.asarray([str(row["variant_id"]) for row in rows])
        if not np.array_equal(ids, cached["variant_ids"]):
            raise ValueError("Cache variant IDs do not match extraction row order")
        if not np.array_equal(cached["layers"], [14, 23]) or not np.array_equal(
            cached["positions"], ["boundary", "final_content", "response_mean", "prompt"]
        ):
            raise ValueError("Unexpected cached layer/position axes")
        return rows, cached["hidden_states"].copy()


def run(config_path="configs/confidence_correctness_audit.yaml"):
    started = time.monotonic()
    config = load_config(config_path)
    inputs = config["inputs"]
    before = {key: file_hash(path) for key, path in inputs.items()}
    v1_rows, v1_hidden = _load_cache(inputs["v1_rows"], inputs["v1_hidden"])
    v2_rows, v2_hidden = _load_cache(inputs["v2_rows"], inputs["v2_hidden"])
    with np.load(resolve(inputs["v1_directions"]), allow_pickle=False) as cached:
        frozen = {key: cached[key].copy() for key in cached.files}
    result, directions = analyze_separation(v1_rows, v1_hidden, v2_rows, v2_hidden, frozen, config)
    after = {key: file_hash(path) for key, path in inputs.items()}
    if before != after:
        raise RuntimeError("A canonical input changed during the cache-only audit")
    result["canonical_inputs_preserved"] = True
    output = resolve(config["output"]["results_dir"])
    write_json(output / "audit_metrics.json", result)
    write_npz(output / "audit_directions.npz", **directions)
    manifest = {
        "experiment": config["experiment"], "configuration": config,
        "input_sha256_before": before, "input_sha256_after": after,
        "canonical_inputs_preserved": True,
        "runtime": {"model_forward_calls": 0, "generation_calls": 0, "api_calls": 0,
                    "nli_calls": 0, "cache_only": True},
        "versions": {"python": platform.python_version(), "numpy": np.__version__},
        "implementation_sha256": {path: file_hash(path) for path in (
            "confidence_pilot/separation_audit.py", "scripts/run_separation_audit.py",
            "tests/test_separation_audit.py", "configs/confidence_correctness_audit.yaml")},
        "artifacts": {name: file_hash(output / name) for name in (
            "audit_metrics.json", "audit_directions.npz")},
        "elapsed_seconds": time.monotonic() - started,
        "interpretation": "Exploratory post-v2 construct audit; no causal intervention and no selection on test outcomes",
    }
    write_json(output / "manifest.json", manifest)
    primary = result["representations"]["layer14_boundary"]
    return {"completed": True, "elapsed_seconds": manifest["elapsed_seconds"],
            "primary_cosine": primary["geometry"]["cosine"],
            "primary_cross_readout": primary["cross_readout"],
            "v2_projection": result["v2_rank1_projection"]["endpoints"],
            "canonical_inputs_preserved": True, "model_calls": 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/confidence_correctness_audit.yaml")
    args = parser.parse_args()
    print(json.dumps(run(args.config), indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
