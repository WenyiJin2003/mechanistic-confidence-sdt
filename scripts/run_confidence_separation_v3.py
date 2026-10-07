#!/usr/bin/env python3
"""Run the score-blind, frozen-readout counterfactual separation experiment."""
from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import torch
import transformers

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from confidence_pilot.common import file_hash, load_config, read_jsonl, resolve, write_json
from confidence_pilot.extract_activations import load_tokenizer
from confidence_pilot.separation_run_v3 import (PREREGISTRATION, analyze_separation, endpoint_pairs,
    export_browser, extract_separation, frozen_directions, plot_separation, save_artifacts, verify_design)


def run(config_path, mode):
    from confidence_pilot.separation_data_v3 import validate_separation_dataset, write_separation_dataset
    start = time.monotonic()
    config = load_config(config_path)
    if mode == "build":
        return write_separation_dataset(config)
    sources, rows = (read_jsonl(config["data"][name]) for name in ("source_items", "variants"))
    tokenizer = load_tokenizer(config)
    audit = validate_separation_dataset(sources, rows, config, tokenizer=tokenizer)
    if not audit["passed"]:
        raise ValueError("Scoreless data audit failed")
    verify_design(config, require_commit=mode not in {"audit"})
    if mode == "audit":
        return {"passed": True, "sources": len(sources), "responses": len(rows), "audit": audit}
    output = resolve(config["output"]["results_dir"])
    write_json(output / "data_audit.json", audit)
    chosen = [next(s["source_id"] for s in sources if s["fact_type"] == kind) for kind in config["dataset"]["fact_types"]]
    subset = [r for r in rows if r["source_id"] in chosen]
    first_rows, first_hidden, first_runtime = extract_separation(subset, config, rows)
    second_rows, second_hidden, second_runtime = extract_separation(subset, config, rows)
    pairs = endpoint_pairs(first_rows)
    checks = {
        "four_fact_types": len(chosen) == 4 and len(subset) == 56,
        "finite_states": first_hidden.shape == (56, 2, 4, 1536) and bool(np.isfinite(first_hidden).all()),
        "exact_resume": second_runtime["forward_calls"] == 0 and second_runtime["cache_hits"] == 56
            and first_rows == second_rows and bool(np.array_equal(first_hidden, second_hidden)),
        "same_answer_positions": len(pairs["neutral_true_vs_false"]) == len(pairs["neutral_supported_vs_omitted"]) == 8,
        "same_prompt_group_invariance": first_runtime["max_prompt_state_difference"] <= config["model"]["prompt_control_atol"],
        "no_generation_nli_or_api": all(first_runtime[key] == second_runtime[key] == 0
            for key in ("generation_calls", "nli_calls", "openai_api_calls")),
    }
    sanity = {"passed": all(checks.values()), "checks": checks, "source_ids": chosen,
              "initial_runtime": first_runtime, "resume_runtime": second_runtime, "scores_inspected": False}
    write_json(output / "sanity_check.json", sanity)
    if not sanity["passed"]:
        raise ValueError("Engineering gate failed")
    if mode == "sanity":
        return sanity
    augmented, hidden, runtime = extract_separation(rows, config, rows)
    vectors, provenance = frozen_directions(config)
    result = analyze_separation(augmented, hidden, vectors, config)
    save_artifacts(augmented, hidden, vectors, provenance, result, runtime, config)
    plot_separation(result, config)
    export_browser(sources, augmented, result, config)
    protected = [PREREGISTRATION, "configs/confidence_separation_v3.yaml",
        "confidence_pilot/separation_data_v3.py", "confidence_pilot/separation_run_v3.py",
        "confidence_pilot/extract_activations.py", "confidence_pilot/common.py", "scripts/run_confidence_separation_v3.py"]
    manifest = {"experiment": config["experiment"], "configuration": config, "runtime": runtime,
        "sanity_check": checks, "implementation_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "implementation_sha256": {path: file_hash(path) for path in protected},
        "data_sha256": {path: file_hash(path) for path in config["data"].values()},
        "artifacts": {p.name: file_hash(p) for p in sorted(output.iterdir()) if p.is_file() and p.name != "manifest.json"},
        "versions": {"python": platform.python_version(), "numpy": np.__version__, "torch": torch.__version__, "transformers": transformers.__version__},
        "elapsed_seconds": time.monotonic() - start, "gates": result["gates"],
        "scope": result["scope"]}
    write_json(output / "manifest.json", manifest)
    return {"completed": True, "responses": len(rows), "gates": result["gates"],
        "manipulation_passed": result["manipulation_passed"], "elapsed_seconds": time.monotonic() - start,
        "primary": {name: {key: result["representations"][name][key]["accuracy"] for key in config["analysis"]["endpoints"]}
                    for name in config["analysis"]["primary_candidates"]}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/confidence_separation_v3.yaml")
    parser.add_argument("--mode", choices=("build", "audit", "sanity", "run"), default="run")
    args = parser.parse_args()
    print(json.dumps(run(args.config, args.mode), indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
