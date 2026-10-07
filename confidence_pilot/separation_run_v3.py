"""Fit-free, counterfactual evaluation of frozen expressed-certainty readouts."""
from __future__ import annotations

from collections import defaultdict
import csv
import json
from pathlib import Path
import subprocess
from typing import Any

import numpy as np

from confidence_pilot.analyze_pairs import grouped_pair_metric
from confidence_pilot.common import ROOT, file_hash, read_jsonl, resolve, write_json, write_jsonl, write_npz
from confidence_pilot.extract_activations import extract_activations


REPRESENTATIONS = {
    "layer14_boundary": (0, 0),
    "layer14_final_content": (0, 1),
    "layer14_response_mean": (0, 2),
    "layer23_boundary": (1, 0),
}
ENDPOINTS = ("certainty_wording", "neutral_true_vs_false", "neutral_supported_vs_omitted")
PREREGISTRATION = "docs/experiments/CONFIDENCE_SEPARATION_V3_PREREGISTRATION.md"


def _unit(value):
    value = np.asarray(value, dtype=np.float64)
    norm = float(np.linalg.norm(value))
    if norm < 1e-12 or not np.isfinite(norm):
        raise ValueError("Undefined readout direction")
    return value / norm


def verify_design(config, *, require_commit=True):
    if config["analysis"].get("no_v3_fitting") is not True:
        raise ValueError("v3 is test-only")
    if config["analysis"]["primary_candidates"] != ["layer14_final_content", "layer14_response_mean"]:
        raise ValueError("Primary candidates differ from the frozen design")
    if config["analysis"]["endpoints"] != list(ENDPOINTS):
        raise ValueError("Endpoints differ from the frozen design")
    for name, item in config["source_artifacts"].items():
        if file_hash(item["path"]) != item["sha256"]:
            raise ValueError(f"Changed v1 artifact: {name}")
    if require_commit:
        paths = [PREREGISTRATION, "configs/confidence_separation_v3.yaml",
                 "confidence_pilot/separation_data_v3.py", "confidence_pilot/separation_run_v3.py",
                 "confidence_pilot/extract_activations.py", "confidence_pilot/common.py",
                 "scripts/run_confidence_separation_v3.py", *config["data"].values(),
                 "data/confidence_separation_v3/data_audit.json",
                 "data/confidence_separation_v3/manual_audit.md"]
        for path in paths:
            tracked = subprocess.run(["git", "ls-files", "--error-unmatch", path], cwd=ROOT, capture_output=True)
            diff = subprocess.run(["git", "diff", "HEAD", "--", path], cwd=ROOT, capture_output=True)
            if tracked.returncode or diff.stdout:
                raise ValueError(f"Commit the unchanged v3 design before model extraction: {path}")


def frozen_directions(config):
    """Reproduce correctness contrasts using exclusively old v1 train/A-B data."""
    old = read_jsonl(config["source_artifacts"]["extraction_rows"]["path"])
    with np.load(resolve(config["source_artifacts"]["hidden_states"]["path"])) as archive:
        hidden = archive["hidden_states"]
        if archive["variant_ids"].tolist() != [row["variant_id"] for row in old]:
            raise ValueError("Old row/state IDs differ")
    with np.load(resolve(config["source_artifacts"]["directions"]["path"])) as archive:
        original = {key: archive[key].astype(np.float64) for key in archive.files}
    fitting = [i for i, row in enumerate(old) if row["split"] == "train" and row["rewrite_family"] in {"A", "B"}]
    sources = sorted({old[i]["source_id"] for i in fitting})
    if len(sources) != 72 or len(fitting) != 576:
        raise ValueError("Unexpected v1 fitting pool")
    vectors = {}
    provenance = {"training_sources": sources, "training_rows": 576, "training_families": ["A", "B"],
                  "v3_fitting_rows": 0, "representations": {}}
    for name, (layer, position) in REPRESENTATIONS.items():
        features = hidden[:, layer, position].astype(np.float64)
        by_source = []
        for source in sources:
            by_family = []
            for family in ("A", "B"):
                ids = [i for i in fitting if old[i]["source_id"] == source and old[i]["rewrite_family"] == family]
                correct = [i for i in ids if old[i]["correctness"] == "correct"]
                wrong = [i for i in ids if old[i]["correctness"] == "incorrect"]
                if len(correct) != 2 or len(wrong) != 2:
                    raise ValueError("Unbalanced old correctness cells")
                by_family.append(features[correct].mean(0) - features[wrong].mean(0))
            by_source.append(np.mean(by_family, axis=0))
        c = _unit(np.mean(by_source, axis=0))
        v = original[name]
        if not np.isclose(np.linalg.norm(v), 1, atol=1e-12):
            raise ValueError("Confidence vector must retain its original unit scale")
        if name == "layer14_boundary" and not np.allclose(c, original["correctness"], rtol=0, atol=1e-12):
            raise ValueError("Old primary correctness direction was not reproduced")
        cosine = float(v @ c)
        residual = v - cosine * c
        vectors[name] = v.copy()
        vectors[name + "_correctness"] = c
        vectors[name + "_projected"] = _unit(residual)
        vectors[name + "_projected_common_scale"] = residual
        provenance["representations"][name] = {"cosine": cosine,
            "projected_norm_before_renormalization": float(np.linalg.norm(residual))}
    rng = np.random.default_rng(config["analysis"]["null_seed"])
    count = int(config["analysis"]["random_directions"])
    if count < 2 or count % 2:
        raise ValueError("Random controls must contain antipodal pairs")
    random = rng.normal(size=(count // 2, 1536))
    random /= np.linalg.norm(random, axis=1, keepdims=True)
    vectors["random_controls"] = np.concatenate((random, -random))
    provenance["random_controls"] = {"seed": config["analysis"]["null_seed"], "count": count,
                                    "interpretation": "Descriptive; no permutation p-values"}
    return vectors, provenance


def extract_separation(rows, config, reference_rows=None):
    def grouped(items):
        return [{**row, "base_source_id": row["source_id"], "source_id": row["prompt_group_id"]} for row in items]
    augmented, hidden, runtime = extract_activations(grouped(rows), config, grouped(reference_rows or rows))
    restored = [{**row, "extraction_prompt_group": row["source_id"], "source_id": row["base_source_id"]}
                for row in augmented]
    runtime["prompt_invariance_scope"] = "base entity + counterfactual world"
    return restored, hidden, runtime


def endpoint_pairs(rows):
    by_source = defaultdict(dict)
    for i, row in enumerate(rows):
        key = (row["world"], row["answer_key"], row["certainty"])
        if key in by_source[row["source_id"]]:
            raise ValueError("Duplicate factorial cell")
        by_source[row["source_id"]][key] = i
    pairs = {name: [] for name in ENDPOINTS}
    for source, cells in sorted(by_source.items()):
        if len(cells) != 14:
            raise ValueError(f"Incomplete source: {source}")
        for world in ("A", "B"):
            for answer in ("A", "B"):
                pairs["certainty_wording"].append((cells[world, answer, "confident"], cells[world, answer, "hedged"]))
        for answer, other in (("A", "B"), ("B", "A")):
            positive = cells[answer, answer, "neutral"]
            for endpoint, negative_world in (("neutral_true_vs_false", other), ("neutral_supported_vs_omitted", "omitted")):
                negative = cells[negative_world, answer, "neutral"]
                for field in ("response_text", "response_ids", "prompt_token_count", "response_start_position",
                              "final_content_position", "boundary_position"):
                    if rows[positive][field] != rows[negative][field]:
                        raise ValueError(f"Identical-answer token gate failed for {source}/{field}")
                pairs[endpoint].append((positive, negative))
    return pairs


def analyze_separation(rows, hidden, vectors, config):
    if hidden.shape != (len(rows), 2, 4, 1536) or not np.isfinite(hidden).all():
        raise ValueError("Invalid hidden-state archive")
    pairs = endpoint_pairs(rows)
    seed = int(config["analysis"]["bootstrap_seed"])
    draws = int(config["analysis"]["bootstrap_samples"])

    def metric(margins, selected):
        margins = np.asarray(margins, dtype=np.float64)
        ids = [rows[a]["source_id"] for a, _ in selected]
        order = np.where(margins > 0, 1., np.where(margins < 0, 0., .5))
        result = grouped_pair_metric(order, ids, bootstrap_samples=draws, seed=seed)
        margin_metric = grouped_pair_metric(margins, ids, bootstrap_samples=draws, seed=seed)
        margin_metric["estimate"] = margin_metric.pop("accuracy")
        result["mean_margin"] = margin_metric
        result["tie_fraction"] = float(np.mean(margins == 0))
        return result

    def summarize(scores):
        output = {}
        for endpoint, selected in pairs.items():
            margins = np.array([scores[a] - scores[b] for a, b in selected])
            entry = metric(margins, selected)
            for field in ("fact_type", "wording_family", "answer_key"):
                strata = {}
                for value in sorted({str(rows[a][field]) for a, _ in selected}):
                    ix = [j for j, (a, _) in enumerate(selected) if str(rows[a][field]) == value]
                    strata[value] = metric(margins[ix], [selected[j] for j in ix])
                entry["by_" + field] = strata
            if endpoint == "certainty_wording":
                entry["by_correctness"] = {}
                for label in ("correct", "incorrect"):
                    ix = [j for j, (a, _) in enumerate(selected) if rows[a]["correctness"] == label]
                    entry["by_correctness"][label] = metric(margins[ix], [selected[j] for j in ix])
                source_correct, source_wrong = defaultdict(list), defaultdict(list)
                for margin, (a, _) in zip(margins, selected):
                    destination = source_correct if rows[a]["correctness"] == "correct" else source_wrong
                    destination[rows[a]["source_id"]].append(float(margin))
                ids = sorted(source_correct)
                interaction = np.array([np.mean(source_correct[s]) - np.mean(source_wrong[s]) for s in ids])
                entry["certainty_by_correctness_interaction"] = grouped_pair_metric(
                    interaction, ids, bootstrap_samples=draws, seed=seed)
                entry["certainty_by_correctness_interaction"]["estimate"] = entry["certainty_by_correctness_interaction"].pop("accuracy")
                entry["certainty_by_correctness_interaction"]["interpretation"] = "Correct-minus-wrong difference in certainty margins; not an accuracy"
            output[endpoint] = entry
        return output

    results, scores = {}, {}
    for name, (layer, position) in REPRESENTATIONS.items():
        features = hidden[:, layer, position].astype(np.float64)
        for suffix in ("", "_correctness", "_projected", "_projected_common_scale"):
            key = name + suffix
            values = features @ vectors[key]
            scores[key] = values.tolist()
            results[key] = summarize(values)
        nulls = {}
        for endpoint, selected in pairs.items():
            margins = np.stack([features[a] - features[b] for a, b in selected]) @ vectors["random_controls"].T
            orders = np.where(margins > 0, 1., np.where(margins < 0, 0., .5))
            ids = np.array([rows[a]["source_id"] for a, _ in selected])
            accuracy = np.stack([orders[ids == source].mean(0) for source in np.unique(ids)]).mean(0)
            observed = results[name][endpoint]["accuracy"]
            nulls[endpoint] = {"mean": float(accuracy.mean()), "central_95": np.percentile(accuracy, [2.5, 97.5]).tolist(),
                "at_least_observed": int(np.sum(accuracy >= observed)), "count": len(accuracy),
                "accuracies": accuracy.tolist(), "interpretation": "Descriptive random-vector distribution; not a permutation test"}
        results[name]["random_control_distribution"] = nulls
    baselines = {}
    for name, values in (("negative_mean_token_nll", -np.array([r["mean_token_nll"] for r in rows])),
                         ("token_length", np.array([r["token_count"] for r in rows]))):
        baselines[name] = summarize(values)
        scores[name] = values.tolist()
    projection_changes = {}
    for name in REPRESENTATIONS:
        original = np.asarray(scores[name])
        residual = np.asarray(scores[name + "_projected_common_scale"])
        projection_changes[name] = {}
        for endpoint, selected in pairs.items():
            ids = [rows[a]["source_id"] for a, _ in selected]
            raw_margins = np.array([original[a] - original[b] for a, b in selected])
            residual_margins = np.array([residual[a] - residual[b] for a, b in selected])
            order = lambda x: np.where(x > 0, 1., np.where(x < 0, 0., .5))
            delta_order = grouped_pair_metric(order(residual_margins) - order(raw_margins), ids,
                bootstrap_samples=draws, seed=seed)
            delta_order["estimate"] = delta_order.pop("accuracy")
            delta_margin = grouped_pair_metric(residual_margins - raw_margins, ids,
                bootstrap_samples=draws, seed=seed)
            delta_margin["estimate"] = delta_margin.pop("accuracy")
            projection_changes[name][endpoint] = {"paired_ordering_difference": delta_order,
                "paired_common_scale_margin_difference": delta_margin}
    threshold = float(config["analysis"]["ordering_accuracy_min"])
    gates = {}
    for name in config["analysis"]["primary_candidates"]:
        entry = results[name]
        checks = {}
        for endpoint in ENDPOINTS:
            value = entry[endpoint]
            checks[endpoint + "_pooled"] = value["accuracy"] >= threshold and value["bootstrap_95"]["lower"] > .5
            checks[endpoint + "_no_fact_type_below_chance"] = all(x["accuracy"] >= .5 for x in value["by_fact_type"].values())
        checks["wording_both_correctness_cells_above_chance"] = all(
            x["accuracy"] > .5 for x in entry["certainty_wording"]["by_correctness"].values())
        gates[name] = {"checks": checks, "passed": all(checks.values())}
    nll = baselines["negative_mean_token_nll"]
    manipulation = {key: nll[key]["accuracy"] >= config["analysis"]["nll_manipulation_accuracy_min"]
                    and nll[key]["bootstrap_95"]["lower"] > .5 for key in ENDPOINTS[1:]}
    return {"experiment": config["experiment"], "source_count": len({r["source_id"] for r in rows}),
        "response_count": len(rows), "endpoint_pair_counts": {key: len(value) for key, value in pairs.items()},
        "representations": results, "baselines": baselines, "gates": gates,
        "projection_changes": projection_changes,
        "manipulation_checks": manipulation, "manipulation_passed": all(manipulation.values()),
        "row_scores": scores, "variant_ids": [r["variant_id"] for r in rows],
        "pair_ids": {key: [[rows[a]["variant_id"], rows[b]["variant_id"]] for a, b in values] for key, values in pairs.items()},
        "scope": "Context-defined correctness and authored certainty; not internal belief or causal control"}


def plot_separation(result, config):
    import matplotlib
    matplotlib.use("Agg")
    from matplotlib import pyplot as plt
    names = ["layer14_boundary", "layer14_final_content", "layer14_response_mean"]
    labels = ["End marker\nreference", "Final response\ncontent token", "Response-content\nmean", "Likelihood"]
    titles = ["Confident > hedged", "Same answer: true > false", "Same answer: supported > omitted"]
    fig, axes = plt.subplots(1, 3, figsize=(12, 4.4), sharey=True)
    for ax, endpoint, title in zip(axes, ENDPOINTS, titles):
        items = [result["representations"][name][endpoint] for name in names]
        items.append(result["baselines"]["negative_mean_token_nll"][endpoint])
        values = np.array([x["accuracy"] for x in items])
        error = np.array([[max(0, x["accuracy"] - x["bootstrap_95"]["lower"]) for x in items],
                          [max(0, x["bootstrap_95"]["upper"] - x["accuracy"]) for x in items]])
        ax.bar(range(4), values, color=["#aaa", "#3478a1", "#688baf", "#588264"])
        ax.errorbar(range(4), values, yerr=error, fmt="none", ecolor="black", capsize=3)
        ax.axhline(.5, color="black", linestyle="--", linewidth=1)
        ax.set_xticks(range(4), labels, fontsize=8)
        ax.set_title(title, fontsize=10)
        ax.set_ylim(0, 1.06)
    axes[0].set_ylabel("Paired ordering (ties = 0.5)")
    fig.suptitle("Confidence–correctness separation: 48 fresh counterfactual records", fontsize=12)
    fig.text(.5, .012, "Frozen v1 vectors. Intervals resample base records; worlds and answer variants stay grouped.", ha="center", fontsize=8)
    fig.tight_layout(rect=[0, .04, 1, .93])
    target = resolve(config["output"]["plot"])
    target.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(target, dpi=180)
    plt.close(fig)


def export_browser(sources, rows, result, config):
    """Publish the exact scored inputs; inference outputs are authored stimuli."""
    target = resolve(config["output"]["browser_dir"])
    target.mkdir(parents=True, exist_ok=True)
    labels = ["layer14_boundary", "layer14_final_content", "layer14_response_mean"]
    by_source = defaultdict(list)
    for i, row in enumerate(rows):
        by_source[row["source_id"]].append((i, row))
    csv_rows = []
    for i, row in enumerate(rows):
        csv_rows.append({**{key: row.get(key) for key in ("source_id", "variant_id", "fact_type", "wording_family", "world", "answer_key",
            "correctness", "supplied_support", "certainty", "question", "context", "response_text", "token_count", "mean_token_nll",
            "response_start_position", "final_content_position", "boundary_position", "answer_span_text",
            "answer_start_position", "answer_stop_position_exclusive")},
            **{name + "_score": result["row_scores"][name][i] for name in labels}})
    with (target / "responses.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(csv_rows[0]))
        writer.writeheader()
        writer.writerows(csv_rows)
    with (target / "sources.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["source_id", "fact_type", "question", "world_A_correct", "world_B_correct"])
        writer.writeheader()
        for source in sources:
            group = by_source[source["source_id"]]
            world_answers = {}
            for _, row in group:
                if row["certainty"] == "neutral" and row["correctness"] == "correct":
                    world_answers[row["world"]] = row["response_text"]
            writer.writerow({"source_id": source["source_id"], "fact_type": source["fact_type"],
                "question": group[0][1]["question"], "world_A_correct": world_answers["A"], "world_B_correct": world_answers["B"]})
    for kind in config["dataset"]["fact_types"]:
        lines = [f"# Confidence–Correctness Separation v3: {kind}", "", "All answers below are authored test stimuli, not generated responses.", "",
                 "Scores are frozen v1 readouts, not probabilities. Correctness refers to the supplied fictional world.", ""]
        for source in sources:
            if source["fact_type"] != kind:
                continue
            group = by_source[source["source_id"]]
            lines += [f"## {source['source_id']}", "", f"**Question:** {group[0][1]['question']}", ""]
            for world in ("A", "B", "omitted"):
                selected = [(i, row) for i, row in group if row["world"] == world]
                lines += [f"### World {world}", "", selected[0][1]["context"], ""]
                for i, row in selected:
                    correctness = row["correctness"] or "not labelled"
                    lines += [f"**{row['answer_key']} / {row['certainty']} / {correctness}:** {row['response_text']}", "",
                        "Scores: " + "; ".join(f"{name.replace('layer14_', '')} {result['row_scores'][name][i]:.6f}" for name in labels) + ".", "",
                        "<details>", "<summary>Tokens and exact row ID</summary>", "",
                        f"`{row['variant_id']}` · final content position {row['final_content_position']} · boundary position {row['boundary_position']} · mean-token NLL {row['mean_token_nll']:.6f}", "", "</details>", ""]
        (target / (kind + ".md")).write_text("\n".join(lines), encoding="utf-8")
    overview = ["# Confidence–Correctness Separation v3: questions and answers", "",
        "48 new fictional records, each with two counterfactual worlds and an omitted-role context; 672 authored responses.", "",
        "The same answer sentence is correct in one world and incorrect in the other. All answer versions and failures are retained.", "",
        "| Fact type | Full question and answer collection |", "|---|---|"]
    overview += [f"| {kind} | [{kind}.md]({kind}.md) |" for kind in config["dataset"]["fact_types"]]
    overview += ["", "Downloads: [sources.csv](sources.csv), [responses.csv](responses.csv).", "",
        "[Results](../../reports/CONFIDENCE_SEPARATION_RESULTS_V3.md) · [Registered design](../../docs/experiments/CONFIDENCE_SEPARATION_V3_PREREGISTRATION.md)", ""]
    (target / "README.md").write_text("\n".join(overview), encoding="utf-8")


def save_artifacts(rows, hidden, vectors, provenance, result, runtime, config):
    output = resolve(config["output"]["results_dir"])
    write_jsonl(output / "extraction_rows.jsonl", rows)
    write_npz(output / "hidden_states.npz", hidden_states=hidden,
        variant_ids=np.array([r["variant_id"] for r in rows]), layers=np.array([14, 23]),
        positions=np.array(["boundary", "final_content", "response_mean", "prompt"]))
    write_npz(output / "frozen_directions.npz", **vectors)
    write_json(output / "frozen_direction_provenance.json", provenance)
    write_json(output / "separation_metrics.json", result)
    write_json(output / "runtime.json", runtime)
