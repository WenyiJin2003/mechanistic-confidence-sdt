"""Plot the frozen cue-holdout layer profile from the public result JSON."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


BASE = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = BASE / "results" / "challenge_evaluation.json"
DEFAULT_OUTPUT = BASE / "results" / "CUE_HOLDOUT_LAYER_TRANSFER.png"


def load_metrics(path: Path) -> dict:
    result = json.loads(path.read_text(encoding="utf-8"))
    if result.get("status") != "complete":
        raise ValueError("Challenge result is not complete")
    metrics = result.get("metrics")
    rows = metrics.get("per_layer") if isinstance(metrics, dict) else None
    if not isinstance(rows, list) or [row.get("layer") for row in rows] != list(range(1, 29)):
        raise ValueError("Expected one frozen result for each of layers 1 through 28")
    return metrics


def plot(metrics: dict, output: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    from matplotlib import pyplot as plt

    rows = metrics["per_layer"]
    layers = [row["layer"] for row in rows]
    estimates = [row["estimate"] for row in rows]
    lower = [row["ci95"][0] for row in rows]
    upper = [row["ci95"][1] for row in rows]
    layer14 = metrics["layer14"]
    ensemble = metrics["equal_28_layer_ensemble"]
    controls = metrics["controls"]

    fig, ax = plt.subplots(figsize=(10, 5.8))
    ax.fill_between(layers, lower, upper, color="#2478b5", alpha=.14,
                    label="95% source-bootstrap interval")
    ax.plot(layers, estimates, color="#2478b5", marker="o", markersize=4.8,
            linewidth=1.8, label="Per-layer paired linear readout")
    ax.axhline(.5, color="#777777", linestyle="--", linewidth=1.2,
               label="Chance / constant baseline")
    ax.axhline(ensemble["estimate"], color="#16856a", linewidth=2,
               label=f"Equal 28-layer ensemble: {ensemble['estimate']:.0%}")
    ax.scatter([14], [layer14["estimate"]], s=90, color="#b73535", zorder=5,
               label=f"Preregistered layer 14: {layer14['estimate']:.0%}")
    ax.set(
        xlabel="Qwen hidden-state layer",
        ylabel="Held-out pair ordering rate",
        title="Cue-holdout transfer of expressed-certainty ordering\n"
              "Frozen development-trained readouts; 50 new source pairs",
        xlim=(.5, 28.5),
        ylim=(.45, 1.02),
        xticks=range(2, 29, 2),
    )
    ax.text(
        .015, .035,
        "Train-only controls\n"
        f"Character TF-IDF: {controls['char_tfidf']['estimate']:.0%}\n"
        f"Answer likelihood (negative NLL): {controls['negative_mean_response_nll']['estimate']:.0%}\n"
        f"Response length: {controls['negative_response_token_length']['estimate']:.0%}",
        transform=ax.transAxes, ha="left", va="bottom", fontsize=9,
        bbox={"boxstyle": "round,pad=.5", "facecolor": "white",
              "edgecolor": "#c8c8c8", "alpha": .96},
    )
    ax.grid(axis="y", alpha=.22)
    ax.legend(frameon=False, loc="lower right", fontsize=9)
    fig.text(
        .5, .01,
        "Development-only agent-reviewed challenge. This measures expressed certainty, "
        "not correctness, subjective belief, or causal mechanism.",
        ha="center", va="bottom", fontsize=8.5, color="#555555",
    )
    fig.tight_layout(rect=(0, .035, 1, 1))
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=200)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    metrics = load_metrics(args.input)
    plot(metrics, args.output)
    print(json.dumps({"input": str(args.input), "output": str(args.output), "layers": 28}))


if __name__ == "__main__":
    main()
