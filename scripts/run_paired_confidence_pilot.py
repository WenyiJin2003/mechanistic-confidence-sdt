#!/usr/bin/env python3
"""Build, audit, sanity-check, or run Paired Confidence Pilot v1."""
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
from confidence_pilot.common import load_config, read_jsonl, resolve, file_hash, write_json, write_jsonl, write_npz
from confidence_pilot.extract_activations import extract_activations, tokenize_variant, load_tokenizer

def selected_data(config):
    sources = read_jsonl(config["data"]["source_items"])
    variants = read_jsonl(config["data"]["variants"])
    phase = config["phase"].lower()
    selected = [s for s in sources if phase == "b" or s["phase_a"]]
    source_ids = {s["source_id"] for s in selected}
    rows = [{**v, "split": v[f"phase_{phase}_split"]} for v in variants
            if v["source_id"] in source_ids and v["rewrite_family"] in config["dataset"]["families"]]
    padding_rows = [v for v in variants if v["source_id"] in source_ids]
    return selected, rows, padding_rows

def validate_data(config, sources, rows):
    from confidence_pilot.data_validation import validate_dataset
    return validate_dataset(sources, rows, config)

def sanity(config, sources, rows, padding_rows):
    chosen = []
    for domain in ("factual_qa", "arithmetic", "academic"):
        chosen.append(next(s["source_id"] for s in sources if s["domain"] == domain))
    chosen.append(next(s["source_id"] for s in sources if s["source_id"] not in chosen))
    ids = set(chosen)
    subset = [row for row in rows if row["source_id"] in ids]
    references = [row for row in padding_rows if row["source_id"] in ids]
    first_rows, first_hidden, first_runtime = extract_activations(subset, config, references)
    second_rows, second_hidden, second_runtime = extract_activations(subset, config, references)
    token_boundaries_ok = all(
        row["boundary_position"] == row["response_stop_position_exclusive"]
        and row["final_content_position"] == row["boundary_position"] - 1
        and row["response_start_position"] == row["prompt_token_count"]
        and row["token_count"] == len(row["response_ids"])
        and row["boundary_token_id"] == 151645
        for row in first_rows
    )
    checks = {
        "four_sources_checked": len(ids) == 4,
        "no_model_generation": first_runtime["generation_calls"] == second_runtime["generation_calls"] == 0,
        "no_nli_or_api_calls": first_runtime["nli_calls"] == first_runtime["openai_api_calls"] == 0,
        "identical_question_context_ids": first_runtime["prompt_ids_identical_within_source"],
        "response_boundaries_correct": token_boundaries_ok,
        "fixed_post_response_token": first_runtime["boundary_token_id"] == 151645,
        "finite_states_correct_layers_width": first_hidden.shape == (len(subset), 2, 4, 1536)
            and bool(np.all(np.isfinite(first_hidden))),
        "final_prompt_negative_control_identical": first_runtime["max_prompt_state_difference"] <= config["model"]["prompt_control_atol"],
        "resumable_cache_zero_second_pass_forwards": second_runtime["forward_calls"] == 0
            and second_runtime["cache_hits"] == len(subset),
        "resume_exact_same_hidden_states": bool(np.array_equal(first_hidden, second_hidden)),
    }
    report = {"passed": all(checks.values()), "checks": checks, "source_ids": chosen,
              "first_pass_runtime": first_runtime, "resume_runtime": second_runtime}
    write_json(resolve(config["output"]["results_dir"]) / "sanity_check.json", report)
    if not report["passed"]:
        raise RuntimeError("Four-source extraction gate failed; full extraction is blocked")
    return report

def plot(result, config):
    import matplotlib
    matplotlib.use("Agg")
    from matplotlib import pyplot as plt
    entries = [
        ("Boundary L14", result["primary"]["primary"]),
        ("Content-last L14", result["representations"]["layer14_final_content"]["metrics"]["primary"]),
        ("Response-mean L14", result["representations"]["layer14_response_mean"]["metrics"]["primary"]),
        ("Boundary L23", result["representations"]["layer23_boundary"]["metrics"]["primary"]),
        ("Text TF-IDF", result["baselines"]["text_tfidf"]["metrics"]["primary"]),
        ("Length", result["baselines"]["length"]["metrics"]["primary"]),
        ("Response NLL", result["baselines"]["sequence_nll"]["metrics"]["primary"]),
    ]
    fig, ax = plt.subplots(figsize=(9, 5))
    values = [m["accuracy"] for _, m in entries]
    errors = [[max(0, m["accuracy"] - m["bootstrap_95"]["lower"]) for _, m in entries],
              [max(0, m["bootstrap_95"]["upper"] - m["accuracy"]) for _, m in entries]]
    ax.bar(range(len(entries)), values, color=["#287b55"] + ["#687ba5"] * 3 + ["#8b8b8b"] * 3)
    ax.errorbar(range(len(entries)), values, yerr=errors, fmt="none", ecolor="black", capsize=3)
    ax.axhline(.5, color="black", linewidth=1, linestyle="--")
    ax.set_xticks(range(len(entries)), [name.replace(" ", "\n", 1) for name, _ in entries])
    ax.set_ylim(0, 1.08)
    ax.set_ylabel("Confident > hedged paired ordering accuracy")
    families = "/".join(result["primary_endpoint"]["families"])
    ax.set_title(f"Paired Confidence Pilot v1: Phase {result['phase']}, test sources, family {families}")
    fig.text(.5, .015, "95% intervals resample source questions. All-success intervals are saturated; target is expressed certainty.",
             ha="center", fontsize=8.5)
    fig.tight_layout(rect=[0, .055, 1, 1])
    path = resolve(config["output"]["plot"])
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=180)
    fig.savefig(resolve(config["output"]["results_dir"]) / "pairwise_results.png", dpi=180)
    plt.close(fig)

def run(config_path, mode):
    started = time.monotonic()
    config = load_config(config_path)
    if mode == "build":
        from confidence_pilot.data_validation import build_dataset
        source_items, variants = build_dataset(config)
        write_jsonl(config["data"]["source_items"], source_items)
        write_jsonl(config["data"]["variants"], variants)
    sources, rows, padding_rows = selected_data(config)
    audit = validate_data(config, sources, rows)
    results_dir = resolve(config["output"]["results_dir"])
    write_json(results_dir / "data_audit.json", audit)
    if not audit.get("passed", False):
        raise RuntimeError("Data gate failed before activation extraction")
    # Token lengths are recorded before extraction and cannot influence any fit.
    tokenizer = load_tokenizer(config)
    lengths = {row["variant_id"]: len(tokenize_variant(row, tokenizer, config)["response_ids"]) for row in rows}
    write_json(results_dir / "response_token_counts.json", lengths)
    del tokenizer
    if mode in {"build", "audit"}:
        return {"phase": config["phase"], "mode": mode, "data_gate_passed": True,
                "sources": len(sources), "responses": len(rows)}
    if config["phase"].lower() == "b":
        a_result = resolve("results/paired_confidence_phase_a/pair_metrics.json")
        if not a_result.exists() or not json.loads(a_result.read_text())["gates"]["statistical_passed"]:
            raise RuntimeError("Phase B blocked: Phase A progression screen has not passed")
        a_manifest_path = resolve("results/paired_confidence_phase_a/manifest.json")
        if not a_manifest_path.exists():
            raise RuntimeError("Phase B blocked: Phase A engineering manifest is missing")
        a_manifest = json.loads(a_manifest_path.read_text())
        if not a_manifest["data_gate_passed"] or not a_manifest["sanity_passed"]:
            raise RuntimeError("Phase B blocked: Phase A data/extraction gates failed")
        current_data_hashes = {key: file_hash(value) for key, value in config["data"].items()}
        if a_manifest["data_sha256"] != current_data_hashes:
            raise RuntimeError("Phase B blocked: the paired dataset changed after Phase A")
        if a_manifest["configuration"]["model"] != config["model"]:
            raise RuntimeError("Phase B blocked: extraction settings changed after Phase A")
        if a_manifest["preregistration_sha256"] != file_hash("PAIRED_CONFIDENCE_PREREGISTRATION_V1.md"):
            raise RuntimeError("Phase B blocked: preregistration changed after Phase A")
        if file_hash(a_result) != a_manifest["artifacts"]["pair_metrics.json"]:
            raise RuntimeError("Phase B blocked: Phase A result hash no longer matches")
        prereg = resolve("PAIRED_CONFIDENCE_PREREGISTRATION_V1.md")
        tracked = subprocess.run(["git", "ls-files", "--error-unmatch", str(prereg.relative_to(ROOT))],
                                 cwd=ROOT, capture_output=True)
        diff = subprocess.run(["git", "diff", "HEAD", "--", str(prereg.relative_to(ROOT))],
                              cwd=ROOT, capture_output=True)
        if tracked.returncode or diff.stdout:
            raise RuntimeError("Phase B requires an unchanged committed preregistration")
    sanity_report = sanity(config, sources, rows, padding_rows)
    if mode == "sanity":
        return {"phase": config["phase"], "mode": mode, "sanity_passed": sanity_report["passed"]}
    augmented, hidden, runtime = extract_activations(rows, config, padding_rows)
    write_jsonl(results_dir / "extraction_rows.jsonl", augmented)
    write_npz(results_dir / "hidden_states.npz", hidden_states=hidden,
              variant_ids=np.asarray([r["variant_id"] for r in augmented]),
              layers=np.asarray([14, 23]), positions=np.asarray(["boundary", "final_content", "response_mean", "prompt"]))
    from confidence_pilot.analyze_pairs import analyze_pairs
    result = analyze_pairs(augmented, hidden, config)
    directions, scores = result.pop("directions"), result.pop("scores")
    write_npz(results_dir / "readout_directions.npz", **{key: np.asarray(value) for key, value in directions.items()})
    write_npz(results_dir / "readout_scores.npz", **{key: np.asarray(value) for key, value in scores.items()},
              variant_ids=np.asarray(result["variant_ids"]))
    write_json(results_dir / "pair_metrics.json", result)
    plot(result, config)
    files = ["data_audit.json", "sanity_check.json", "hidden_states.npz", "extraction_rows.jsonl",
             "readout_directions.npz", "readout_scores.npz", "pair_metrics.json", "pairwise_results.png"]
    manifest = {
        "experiment": "Paired Confidence Pilot v1", "phase": config["phase"], "configuration": config,
        "data_gate_passed": True, "sanity_passed": True, "runtime": runtime,
        "data_sha256": {key: file_hash(value) for key, value in config["data"].items()},
        "preregistration_sha256": file_hash("PAIRED_CONFIDENCE_PREREGISTRATION_V1.md"),
        "implementation_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "implementation_sha256": {str(path.relative_to(ROOT)): file_hash(path) for path in (ROOT/"confidence_pilot").glob("*.py")},
        "versions": {"python": platform.python_version(), "numpy": np.__version__,
                     "torch": torch.__version__, "transformers": transformers.__version__,
                     "sklearn": sklearn.__version__, "platform": platform.platform()},
        "artifacts": {name: file_hash(results_dir/name) for name in files},
        "elapsed_seconds": time.monotonic() - started,
        "statistical_gates": result["gates"],
        "interpretation_scope": "candidate expressed-certainty readout; no causal intervention or SDT training",
    }
    write_json(results_dir / "manifest.json", manifest)
    return {"phase": config["phase"], "completed": True, "primary": result["primary"]["primary"],
            "correctness": result["primary"]["primary_strata"]["correctness"], "gates": result["gates"],
            "elapsed_seconds": time.monotonic() - started}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/paired_confidence_phase_a.yaml")
    parser.add_argument("--mode", choices=["build", "audit", "sanity", "run"], default="run")
    args = parser.parse_args()
    print(json.dumps(run(args.config, args.mode), sort_keys=True, indent=2, allow_nan=False))

if __name__ == "__main__": main()
