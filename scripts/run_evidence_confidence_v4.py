#!/usr/bin/env python3
"""Prepare, freeze, run and reproduce the local evidence-support readout pilot."""
from __future__ import annotations

import argparse
import csv
import json
import platform
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np
import torch
import transformers

from confidence_pilot.common import file_hash, load_config, read_jsonl, resolve, write_json, write_jsonl, write_npz
from confidence_pilot.evidence_behavior_v4 import behavior_tokens, run_behavior
from confidence_pilot.evidence_data_v4 import validate_dataset, write_dataset
from confidence_pilot.evidence_analysis_v4 import analyze, fit_readouts
from confidence_pilot.extract_activations import load_tokenizer
from confidence_pilot.separation_run_v3 import extract_separation

PROTOCOL = "docs/experiments/EVIDENCE_CONFIDENCE_V4_PREREGISTRATION.md"
CONFIG = "configs/evidence_confidence_v4.yaml"
IMPLEMENTATION = [
    "confidence_pilot/evidence_data_v4.py", "confidence_pilot/evidence_analysis_v4.py",
    "confidence_pilot/evidence_behavior_v4.py", "scripts/run_evidence_confidence_v4.py",
    "confidence_pilot/extract_activations.py", "confidence_pilot/common.py",
    "confidence_pilot/separation_run_v3.py", "confidence_pilot/analyze_pairs.py",
]


def jsonable(value):
    if isinstance(value, dict):
        return {str(k): jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(x) for x in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    return value


def freeze_paths(config):
    paths = [PROTOCOL, CONFIG, *IMPLEMENTATION, *config["data"].values(),
             "data/evidence_confidence_v4/data_audit.json"]
    return list(dict.fromkeys(paths))


def verify_freeze(config, require_commit=True):
    for item in config["source_artifacts"].values():
        if file_hash(item["path"]) != item["sha256"]:
            raise ValueError("The frozen v1 reference artifact changed")
    if config["analysis"]["primary_position"] != "response_mean" or config["analysis"]["primary_layer"] != 14:
        raise ValueError("The primary representation differs from the registered design")
    if config["analysis"]["pairwise_logistic_C"] != 0.01:
        raise ValueError("Regularization differs from the registered design")
    if require_commit:
        for path in freeze_paths(config):
            tracked = subprocess.run(["git", "ls-files", "--error-unmatch", path], cwd=ROOT, capture_output=True)
            diff = subprocess.run(["git", "diff", "HEAD", "--", path], cwd=ROOT, capture_output=True)
            if tracked.returncode or diff.stdout:
                raise ValueError(f"Commit the unchanged protocol and implementation before inference: {path}")


def save_fitted(readouts, output):
    arrays = {key: np.asarray(value) for key, value in readouts["vectors"].items()}
    for key in ("random_controls", "shuffled_controls"):
        if key in readouts:
            arrays[key] = np.asarray(readouts[key])
    for key, values in readouts.get("scaler_arrays", {}).items():
        arrays[key] = np.asarray(values)
    write_npz(output / "readout_directions.npz", **arrays)
    write_json(output / "fitting_provenance.json", jsonable(readouts["provenance"]))


def export_browser(sources, rows, behavior, result, config):
    target = resolve(config["output"]["browser_dir"])
    target.mkdir(parents=True, exist_ok=True)
    score_table = result.get("row_scores", {})
    primary = config["analysis"]["primary_readout"]
    scores = score_table.get(primary, [])
    csv_rows = []
    for index, row in enumerate(rows):
        item = {key: row.get(key) for key in (
            "source_id", "variant_id", "split", "fact_type", "context_template", "world",
            "answer_key", "certainty", "correctness", "supplied_support", "question", "context",
            "response_text", "token_count", "sequence_nll", "mean_token_nll", "prompt_token_count",
            "response_start_position", "final_content_position", "boundary_position")}
        item["primary_score"] = float(scores[index]) if len(scores) else None
        csv_rows.append(item)
    with (target / "responses.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(csv_rows[0]))
        writer.writeheader()
        writer.writerows(csv_rows)
    behavior_fields = ["source_id", "world", "question", "context", "correct_answer_key", "greedy_text",
                       "parsed_choice", "candidate_sequence_logpA", "candidate_sequence_logpB",
                       "candidate_log_odds_A_minus_B", "exact_candidate_value_match"]
    with (target / "generated_answers.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=behavior_fields)
        writer.writeheader()
        writer.writerows({key: row.get(key) for key in behavior_fields} for row in behavior)
    lookup = defaultdict(list)
    for index, row in enumerate(rows):
        lookup[row["source_id"]].append((index, row))
    answers = {(row["source_id"], row["world"]): row for row in behavior}
    for kind in config["dataset"]["fact_types"]:
        lines = [f"# Evidence readout v4: {kind.replace('_', ' ')}", "",
                 "Supplied answers are experimental inputs. Greedy answers below are independent model outputs.", ""]
        for source in (s for s in sources if s["fact_type"] == kind):
            sid = source["source_id"]
            lines += [f"## {sid}", "", f"Split: **{source['split']}**. Extraction question: {source['question']}", "",
                      f"Candidate A: `{source['candidate_values']['A']}`; candidate B: `{source['candidate_values']['B']}`.", ""]
            for world, context in source["contexts"].items():
                lines += [f"### Context {world}", "", "```text", context, "```", "",
                          "| Supplied response | Style | Support | Readout score |",
                          "|---|---|---|---:|"]
                for index, row in lookup[sid]:
                    if row["world"] != world:
                        continue
                    score = f"{float(scores[index]):.4f}" if len(scores) else "—"
                    response = row["response_text"].replace("|", "\\|")
                    lines.append(f"| {response} | {row['certainty']} | {row['supplied_support']} | {score} |")
                lines.append("")
                if (sid, world) in answers:
                    item = answers[sid, world]
                    lines += [f"Independent question: {item['question']}", "", "**Qwen's greedy answer:**", "",
                              "```text", item["greedy_text"], "```", "",
                              f"Parsed choice: `{item['parsed_choice']}`. Candidate log odds A−B: "
                              f"`{item['candidate_log_odds_A_minus_B']:.4f}`.", ""]
        (target / f"{kind}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    index = ["# Evidence-Sensitive Readout v4: Inputs and Model Answers", "",
             "168 new fictional records: 96 train, 24 validation, 48 test. Source identities and "
             "question/context/neutral-response templates are held out by split.", "",
             "The 1,584 supplied responses are teacher-forced inputs; they were not generated by Qwen. "
             "The separate 144 greedy answers are Qwen outputs on independently phrased test questions.", "",
             "- [All supplied responses and scores (CSV)](responses.csv)",
             "- [Every generated answer and candidate likelihood (CSV)](generated_answers.csv)",
             "- [Report](../../reports/EVIDENCE_CONFIDENCE_RESULTS_V4.md)",
             "- [Registered design](../../docs/experiments/EVIDENCE_CONFIDENCE_V4_PREREGISTRATION.md)", ""]
    index += [f"- [{kind.replace('_', ' ').title()}]({kind}.md)" for kind in config["dataset"]["fact_types"]]
    (target / "README.md").write_text("\n".join(index) + "\n", encoding="utf-8")


def plot_result(result, config):
    import matplotlib
    matplotlib.use("Agg")
    from matplotlib import pyplot as plt

    readouts = result["readouts"]
    primary = config["analysis"]["primary_readout"]
    candidates = [primary, "layer14_response_mean_mean_contrast", "layer14_response_mean_frozen_certainty"]
    candidates = [name for name in candidates if name in readouts]
    endpoints = ["neutral_supported_vs_contradicted", "neutral_supported_vs_omitted", "neutral_omitted_vs_contradicted"]
    # New-run metric schemas are explicitly passed through; fail rather than invent labels.
    aliases = {"neutral_supported_vs_contradicted": "supported_vs_contradicted",
               "neutral_supported_vs_omitted": "supported_vs_omitted",
               "neutral_omitted_vs_contradicted": "omitted_vs_contradicted"}
    titles = ["Supported > contradicted", "Supported > omitted", "Omitted > contradicted"]
    labels = ["New paired\nlinear probe", "Mean\ncontrast", "Old certainty\nreadout"]
    fig, axes = plt.subplots(1, 3, figsize=(10.4, 4.2), sharey=True)
    for ax, endpoint, title in zip(axes, endpoints, titles):
        entries = []
        for name in candidates:
            item = readouts[name]
            if endpoint not in item and "neutral" in item:
                item = item["neutral"]
            key = endpoint if endpoint in item else aliases[endpoint]
            entries.append(item[key])
        values = np.array([item["accuracy"] for item in entries])
        error = np.array([[max(0, item["accuracy"] - item["bootstrap_95"]["lower"]) for item in entries],
                          [max(0, item["bootstrap_95"]["upper"] - item["accuracy"]) for item in entries]])
        ax.bar(range(len(values)), values, color=["#256f8e", "#79a5ac", "#aaaaaa"][:len(values)])
        ax.errorbar(range(len(values)), values, yerr=error, fmt="none", capsize=3, ecolor="black")
        ax.axhline(.5, color="black", linestyle="--", linewidth=.8)
        ax.set_xticks(range(len(values)), labels[:len(values)], fontsize=8)
        ax.set_title(title, fontsize=10)
        ax.set_ylim(0, 1.07)
    axes[0].set_ylabel("Paired ordering; 48 held-out source records")
    fig.suptitle("Evidence-support readout: fresh facts and held-out wording", fontsize=12)
    fig.text(.5, .01, "New probe fits neutral training responses only. Intervals resample whole records.", ha="center", fontsize=8)
    fig.tight_layout(rect=[0, .04, 1, .93])
    path = resolve(config["output"]["plot"])
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=180)
    plt.close(fig)


def run(config_path, mode):
    started = time.monotonic()
    config = load_config(config_path)
    if mode == "build":
        sources, rows, prompts, audit = write_dataset(config)
        tokenizer = load_tokenizer(config)
        for prompt in prompts:
            behavior_tokens(prompt, tokenizer, config)
        return {"built": True, "sources": len(sources), "responses": len(rows),
                "behavior_prompts": len(prompts), "audit_passed": audit["passed"]}
    sources = read_jsonl(config["data"]["source_items"])
    rows = read_jsonl(config["data"]["variants"])
    prompts = read_jsonl(config["data"]["behavior_prompts"])
    audit = validate_dataset(sources, rows, prompts, config, tokenizer=load_tokenizer(config))
    if not audit["passed"]:
        raise ValueError("The input audit failed")
    verify_freeze(config, require_commit=mode != "audit")
    if mode == "audit":
        return {"passed": True, "sources": len(sources), "responses": len(rows),
                "behavior_prompts": len(prompts)}
    output = resolve(config["output"]["results_dir"])
    if mode == "analyze":
        augmented = read_jsonl(output / "extraction_rows.jsonl")
        behavior = read_jsonl(output / "behavior_outputs.jsonl")
        if len(augmented) != len(rows):
            raise ValueError("Cached extraction has the wrong number of rows")
        for expected, cached in zip(rows, augmented):
            for key, value in expected.items():
                if cached.get(key) != value:
                    raise ValueError(f"Cached row differs from frozen input: {expected['variant_id']}/{key}")
        if (output / "manifest.json").exists():
            previous = json.loads((output / "manifest.json").read_text())
            for name in ("extraction_rows.jsonl", "hidden_states.npz", "behavior_outputs.jsonl"):
                if file_hash(output / name) != previous["artifacts"][name]:
                    raise ValueError(f"Saved artifact integrity check failed: {name}")
        with np.load(output / "hidden_states.npz") as data:
            hidden = data["hidden_states"]
            if data["variant_ids"].tolist() != [r["variant_id"] for r in augmented]:
                raise ValueError("Hidden archive row alignment mismatch")
        runtime = {"cache_only_analysis": True, "generation_calls": 0}
        behavior_runtime = {"cache_only_analysis": True, "generation_calls": 0}
        sanity = json.loads((output / "sanity_check.json").read_text())
    else:
        selected = [next(s["source_id"] for s in sources if s["split"] == "train" and s["fact_type"] == kind)
                    for kind in config["dataset"]["fact_types"]]
        tiny = [r for r in rows if r["source_id"] in selected]
        first, states, first_runtime = extract_separation(tiny, config, rows)
        second, again, second_runtime = extract_separation(tiny, config, rows)
        checks = {"four_training_records": len(selected) == 4 and len(tiny) == 24,
                  "finite_states": states.shape == (24, 2, 4, 1536) and bool(np.isfinite(states).all()),
                  "exact_resume": first == second and bool(np.array_equal(states, again))
                     and second_runtime["forward_calls"] == 0 and second_runtime["cache_hits"] == 24,
                  "same_prompt_group": first_runtime["max_prompt_state_difference"] <= config["model"]["prompt_control_atol"]}
        sanity = {"passed": all(checks.values()), "checks": checks, "source_ids": selected,
                  "scores_inspected": False, "initial_runtime": first_runtime, "resume_runtime": second_runtime}
        write_json(output / "sanity_check.json", sanity)
        if not sanity["passed"]:
            raise ValueError("The score-blind extraction sanity check failed")
        if mode == "sanity":
            return sanity
        augmented, hidden, runtime = extract_separation(rows, config, rows)
        write_jsonl(output / "extraction_rows.jsonl", augmented)
        write_npz(output / "hidden_states.npz", hidden_states=hidden,
                  variant_ids=np.asarray([r["variant_id"] for r in augmented]))
        behavior, behavior_runtime = run_behavior(prompts, config)
        write_jsonl(output / "behavior_outputs.jsonl", behavior)
    readouts = fit_readouts(augmented, hidden, config)
    save_fitted(readouts, output)
    result = analyze(augmented, hidden, readouts, behavior, config)
    write_json(output / "metrics.json", jsonable(result))
    write_json(output / "data_audit.json", jsonable(audit))
    export_browser(sources, augmented, behavior, result, config)
    plot_result(result, config)
    manifest = {"experiment": config["experiment"], "configuration": config,
                "implementation_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                "freeze_sha256": {p: file_hash(p) for p in freeze_paths(config)},
                "runtime": runtime, "behavior_runtime": behavior_runtime, "sanity": sanity,
                "versions": {"python": platform.python_version(), "numpy": np.__version__,
                             "torch": torch.__version__, "transformers": transformers.__version__},
                "artifacts": {p.name: file_hash(p) for p in output.iterdir() if p.is_file() and p.name != "manifest.json"},
                "elapsed_seconds": time.monotonic() - started, "gates": result["gates"], "scope": result["scope"]}
    # Preserve first-run compute accounting when only replotting/reanalyzing cached artifacts.
    if mode == "analyze" and (output / "manifest.json").exists():
        original = json.loads((output / "manifest.json").read_text())
        manifest["first_run_runtime"] = original.get("first_run_runtime", {
            "runtime": original["runtime"], "behavior_runtime": original["behavior_runtime"],
            "elapsed_seconds": original["elapsed_seconds"], "implementation_commit": original["implementation_commit"]})
    write_json(output / "manifest.json", jsonable(manifest))
    return {"completed": True, "sources": len(sources), "responses": len(rows),
            "behavior_prompts": len(prompts), "elapsed_seconds": time.monotonic() - started,
            "gates": result["gates"],
            "primary": {key: {field: value[field] for field in ("accuracy", "bootstrap_95")}
                        for key, value in result["metrics"]["primary"].items()
                        if isinstance(value, dict) and "accuracy" in value}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=CONFIG)
    parser.add_argument("--mode", choices=("build", "audit", "sanity", "run", "analyze"), default="run")
    args = parser.parse_args()
    print(json.dumps(jsonable(run(args.config, args.mode)), indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
