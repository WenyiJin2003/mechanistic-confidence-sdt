#!/usr/bin/env python3
"""Render the saved v3 endpoints without extraction, fitting, or score changes."""
from pathlib import Path
import json
import sys

import matplotlib
matplotlib.use("Agg")
from matplotlib import pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from confidence_pilot.common import load_config, resolve


def main():
    config = load_config("configs/confidence_separation_v3.yaml")
    with (resolve(config["output"]["results_dir"]) / "separation_metrics.json").open() as handle:
        result = json.load(handle)
    names = ["layer14_boundary", "layer14_final_content", "layer14_response_mean"]
    labels = ["End marker\n(reference)", "Final response\ntoken", "Response\nmean", "Likelihood"]
    endpoints = config["analysis"]["endpoints"]
    titles = ["Confident vs. hedged wording", "Same answer: true vs. false", "Same answer: supported vs. omitted"]
    fig, axes = plt.subplots(1, 3, figsize=(12.5, 4.6), sharey=True)
    for ax, endpoint, title in zip(axes, endpoints, titles):
        items = [result["representations"][name][endpoint] for name in names]
        items.append(result["baselines"]["negative_mean_token_nll"][endpoint])
        values = np.array([item["accuracy"] for item in items])
        errors = np.array([[max(0, item["accuracy"] - item["bootstrap_95"]["lower"]) for item in items],
                           [max(0, item["bootstrap_95"]["upper"] - item["accuracy"]) for item in items]])
        ax.bar(range(4), values, width=.62, color=["#aaa", "#3478a1", "#688baf", "#588264"])
        ax.errorbar(range(4), values, yerr=errors, fmt="none", color="black", capsize=3)
        for i, value in enumerate(values):
            ax.text(i, max(value, items[i]["bootstrap_95"]["upper"]) + .025,
                    f"{value:.1%}", ha="center", fontsize=9)
        ax.axhline(.5, color="#444", linestyle="--", linewidth=1)
        ax.set_xticks(range(4), labels, fontsize=8.5)
        ax.tick_params(axis="x", length=0, pad=8)
        ax.set_title(title, fontsize=11, pad=12)
        ax.set_ylim(0, 1.15)
        ax.set_yticks(np.arange(0, 1.01, .2))
        ax.spines[["top", "right"]].set_visible(False)
    axes[0].set_ylabel("Paired ordering rate (ties = 0.5)")
    fig.suptitle("Frozen confidence readouts on 48 new counterfactual records", fontsize=13)
    fig.text(.5, .015, "95% intervals resample whole records. Final token excludes the end marker; mean covers all response content.",
             ha="center", fontsize=8.5)
    fig.tight_layout(rect=[0, .055, 1, .93], w_pad=2)
    fig.savefig(resolve(config["output"]["plot"]), dpi=180)
    plt.close(fig)


if __name__ == "__main__":
    main()
