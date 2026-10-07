#!/usr/bin/env python3
"""Run the registered frozen-readout transfer test; never train on v2."""
from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import sklearn
import torch
import transformers

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from confidence_pilot.common import load_config, resolve, read_jsonl, file_hash, write_json, write_jsonl, write_npz
from confidence_pilot.transfer_data_v2 import validate_transfer_dataset, write_transfer_dataset, FACT_TYPES
from confidence_pilot.transfer_run_v2 import verify_frozen_inputs, extract_transfer, prepare_frozen_controls


def sanity(rows, sources, config):
    chosen = [next(source["source_id"] for source in sources if source["fact_type"] == kind)
              for kind in FACT_TYPES]
    subset = [row for row in rows if row["source_id"] in chosen]
    first_rows, first_hidden, first_runtime = extract_transfer(subset, config)
    second_rows, second_hidden, second_runtime = extract_transfer(subset, config)
    checks = {
        "four_fact_types_checked": len(chosen) == 4 and len(subset) == 40,
        "no_generation_nli_or_api": all(first_runtime[name] == second_runtime[name] == 0
            for name in ("generation_calls", "nli_calls", "openai_api_calls")),
        "finite_hidden_shape": first_hidden.shape == (40, 2, 4, 1536) and bool(np.isfinite(first_hidden).all()),
        "exact_cache_resume": second_runtime["forward_calls"] == 0 and second_runtime["cache_hits"] == 40
            and bool(np.array_equal(first_hidden, second_hidden)) and first_rows == second_rows,
        "within_prompt_group_invariance": first_runtime["prompt_ids_identical_within_extraction_group"]
            and first_runtime["max_prompt_state_difference"] <= config["model"]["prompt_control_atol"],
        "intended_token_positions": all(row["boundary_position"] == row["response_stop_position_exclusive"]
            and row["final_content_position"] == row["boundary_position"] - 1
            and row["response_start_position"] == row["prompt_token_count"]
            and row["token_count"] == len(row["response_ids"])
            and row["boundary_token_id"] == 151645 for row in first_rows),
    }
    neutral = [row for row in first_rows if row["experiment"] == "neutral_evidence"]
    checks["neutral_response_and_absolute_position_match"] = all(
        len({tuple(row["response_ids"]) for row in neutral if row["source_id"] == source and row["format"] == view}) == 1
        and len({row["boundary_position"] for row in neutral if row["source_id"] == source and row["format"] == view}) == 1
        for source in chosen for view in ("qa", "document"))
    report = {"passed": all(checks.values()), "checks": checks, "source_ids": chosen,
              "first_pass_runtime": first_runtime, "resume_runtime": second_runtime,
              "outcome_scores_inspected": False}
    write_json(resolve(config["output"]["results_dir"]) / "sanity_check.json", report)
    if not report["passed"]:
        raise RuntimeError("Engineering gate failed; full v2 extraction is blocked")
    return report


def plot(result, config):
    import matplotlib
    matplotlib.use("Agg")
    from matplotlib import pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.4), sharey=True)
    names = [("Frozen L14", result["representations"]["layer14_boundary"]["endpoints"]),
             ("Word TF-IDF", result["baselines"]["text_tfidf"]["endpoints"]),
             ("Char TF-IDF", result["baselines"]["char_tfidf"]["endpoints"]),
             ("Raw likelihood", result["baselines"]["negative_mean_token_nll"]["endpoints"])]
    for ax, endpoint, title in zip(axes,
            ("natural_style", "neutral_qa_supported_vs_omitted"),
            ("New wording: confident > hedged", "Same answer: supported > omitted")):
        metrics = [entry[endpoint] for _, entry in names]
        values = [item["accuracy"] for item in metrics]
        errors = [[max(0, item["accuracy"] - item["bootstrap_95"]["lower"]) for item in metrics],
                  [max(0, item["bootstrap_95"]["upper"] - item["accuracy"]) for item in metrics]]
        ax.bar(range(len(names)), values, color=["#32678e", "#a0a0a0", "#a0a0a0", "#588264"])
        ax.errorbar(range(len(names)), values, yerr=errors, fmt="none", ecolor="black", capsize=3)
        ax.axhline(.5, color="black", ls="--", lw=1)
        ax.set_xticks(range(len(names)), [name.replace(" ", "\n", 1) for name, _ in names], fontsize=9)
        ax.set_title(title, fontsize=11)
        ax.set_ylim(0, 1.06)
    axes[0].set_ylabel("Paired ordering accuracy (ties = 0.5)")
    fig.suptitle("Frozen-readout transfer v2: 48 new fictional sources", fontsize=12)
    fig.text(.5, .015, "95% intervals resample sources. Text controls use response only; no refitting on v2.",
             ha="center", fontsize=8)
    fig.tight_layout(rect=[0, .055, 1, .94])
    for path in (resolve(config["output"]["plot"]), resolve(config["output"]["results_dir"]) / "transfer_results.png"):
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, dpi=180)
    plt.close(fig)


def run(config_path, mode):
    start = time.monotonic()
    config = load_config(config_path)
    if mode == "build":
        return write_transfer_dataset(config)
    sources = read_jsonl(config["data"]["source_items"])
    rows = read_jsonl(config["data"]["variants"])
    audit = validate_transfer_dataset(sources, rows, config)
    if not audit["passed"]:
        raise ValueError("The complete scoreless catalog failed validation")
    verify_frozen_inputs(config, require_commit=mode not in {"audit"})
    if mode == "audit":
        return {"passed": True, "sources": len(sources), "rows": len(rows), "catalog_sha256": audit["catalog_sha256"]}
    output = resolve(config["output"]["results_dir"])
    write_json(output / "data_audit.json", audit)
    sanity_report = sanity(rows, sources, config)
    if mode == "sanity":
        return {"passed": True, "checks": sanity_report["checks"]}
    augmented, hidden, runtime = extract_transfer(rows, config)
    augmented, directions = prepare_frozen_controls(augmented, config)
    write_jsonl(output / "extraction_rows.jsonl", augmented)
    write_npz(output / "hidden_states.npz", hidden_states=hidden,
              variant_ids=np.asarray([row["variant_id"] for row in augmented]),
              layers=np.asarray([14, 23]), positions=np.asarray(["boundary", "final_content", "response_mean", "prompt"]))
    from confidence_pilot.transfer_analysis_v2 import analyze_transfer
    result = analyze_transfer(augmented, hidden, directions, config)
    write_json(output / "transfer_metrics.json", result)
    plot(result, config)
    artifact_files = [path for path in output.iterdir() if path.is_file() and path.name != "manifest.json"]
    code_files = [ROOT / "scripts/run_confidence_transfer_v2.py", *sorted((ROOT / "confidence_pilot").glob("*.py"))]
    manifest = {"experiment": "Frozen confidence-readout transfer v2", "configuration": config,
        "runtime": runtime, "sanity_passed": True, "data_gate_passed": True,
        "implementation_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "implementation_sha256": {str(path.relative_to(ROOT)): file_hash(path) for path in code_files},
        "preregistration_sha256": file_hash("CONFIDENCE_TRANSFER_PREREGISTRATION_V2.md"),
        "data_sha256": {str(path.relative_to(ROOT)): file_hash(path) for path in sorted(resolve("data/confidence_transfer_v2").iterdir())},
        "artifacts": {path.name: file_hash(path) for path in sorted(artifact_files)},
        "versions": {"python": platform.python_version(), "numpy": np.__version__, "torch": torch.__version__,
                     "transformers": transformers.__version__, "sklearn": sklearn.__version__, "platform": platform.platform()},
        "elapsed_seconds": time.monotonic() - start, "statistical_gates": result["gates"],
        "scope": "Construct-validation only; no generation, fine-tuning, steering or SDT loss"}
    write_json(output / "manifest.json", manifest)
    return {"completed": True, "primary": result["primary"], "gates": result["gates"],
            "elapsed_seconds": time.monotonic() - start}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/paired_confidence_transfer_v2.yaml")
    parser.add_argument("--mode", choices=("build", "audit", "sanity", "run"), default="run")
    args = parser.parse_args()
    print(json.dumps(run(args.config, args.mode), sort_keys=True, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
