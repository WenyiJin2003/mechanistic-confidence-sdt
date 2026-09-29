"""Sampling-budget reliability for cached semantic-entropy labels."""

from __future__ import annotations

import copy
import hashlib
import json
import time
from pathlib import Path
from typing import Any, Callable

import matplotlib
import numpy as np
import yaml
from scipy.stats import spearmanr

from stage0.pipeline import (
    LocalGenerator,
    atomic_json,
    load_config,
    read_jsonl,
    root_dir,
    semantic_rows_nli,
    stable_hash,
    write_jsonl,
)


matplotlib.use("Agg")
from matplotlib import pyplot as plt  # noqa: E402


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def select_rank_stratified(
    entropy: np.ndarray,
    ids: list[str],
    strata: int,
    per_stratum: int,
    seed: int,
) -> list[dict[str, Any]]:
    """Sample equally from deterministic entropy-rank strata."""
    if strata * per_stratum > len(entropy):
        raise ValueError("Requested stratified sample is larger than the source run")
    order = np.asarray(sorted(range(len(entropy)), key=lambda i: (float(entropy[i]), ids[i])))
    bins = np.array_split(order, strata)
    rng = np.random.default_rng(seed)
    selected: list[dict[str, Any]] = []
    for stratum, candidates in enumerate(bins):
        if len(candidates) < per_stratum:
            raise ValueError(f"Stratum {stratum} is too small")
        chosen = sorted(rng.choice(candidates, size=per_stratum, replace=False).tolist())
        for index in chosen:
            selected.append(
                {
                    "source_index": int(index),
                    "id": ids[index],
                    "stratum": int(stratum),
                    "entropy_5": float(entropy[index]),
                }
            )
    return sorted(selected, key=lambda row: row["source_index"])


def _metric_estimates(first: np.ndarray, reference: np.ndarray, threshold: float) -> dict[str, float]:
    first_labels = first >= threshold
    reference_labels = reference >= threshold
    if np.unique(first).size < 2 or np.unique(reference).size < 2:
        rho = float("nan")
    else:
        rho = float(spearmanr(first, reference).statistic)
    observed = float(np.mean(first_labels == reference_labels))
    first_high = float(np.mean(first_labels))
    reference_high = float(np.mean(reference_labels))
    expected = first_high * reference_high + (1 - first_high) * (1 - reference_high)
    kappa = (observed - expected) / (1 - expected) if expected < 1 else float("nan")
    return {
        "label_agreement": observed,
        "cohen_kappa": float(kappa),
        "spearman": rho,
        "mean_absolute_entropy_difference": float(np.mean(np.abs(first - reference))),
    }


def _stratified_bootstrap(
    first: np.ndarray,
    reference: np.ndarray,
    strata: np.ndarray,
    threshold: float,
    samples: int,
    seed: int,
) -> dict[str, dict[str, Any]]:
    rng = np.random.default_rng(seed)
    unique_strata = np.unique(strata)
    values: dict[str, list[float]] = {
        "label_agreement": [],
        "cohen_kappa": [],
        "spearman": [],
        "mean_absolute_entropy_difference": [],
    }
    for _ in range(samples):
        sample = np.concatenate(
            [
                rng.choice(indices, size=len(indices), replace=True)
                for group in unique_strata
                for indices in [np.flatnonzero(strata == group)]
            ]
        )
        metrics = _metric_estimates(first[sample], reference[sample], threshold)
        for name, value in metrics.items():
            if np.isfinite(value):
                values[name].append(value)
    result = {}
    for name, metric_values in values.items():
        array = np.asarray(metric_values, dtype=np.float64)
        result[name] = {
            "lower_95": float(np.percentile(array, 2.5)),
            "median": float(np.median(array)),
            "upper_95": float(np.percentile(array, 97.5)),
            "valid_resamples": int(array.size),
        }
    return result


def compare_prefixes(
    entropy_by_prefix: dict[int, np.ndarray],
    strata: np.ndarray,
    threshold: float,
    bootstrap_samples: int,
    bootstrap_seed: int,
) -> dict[str, Any]:
    reference_prefix = max(entropy_by_prefix)
    reference = entropy_by_prefix[reference_prefix]
    comparisons = {}
    for prefix in sorted(entropy_by_prefix):
        if prefix == reference_prefix:
            continue
        first = entropy_by_prefix[prefix]
        first_labels = first >= threshold
        reference_labels = reference >= threshold
        comparisons[f"{prefix}_vs_{reference_prefix}"] = {
            **_metric_estimates(first, reference, threshold),
            "bootstrap_95": _stratified_bootstrap(
                first,
                reference,
                strata,
                threshold,
                bootstrap_samples,
                bootstrap_seed + prefix,
            ),
            "label_flips": {
                "low_to_high": int(np.sum((~first_labels) & reference_labels)),
                "high_to_low": int(np.sum(first_labels & (~reference_labels))),
                "total": int(np.sum(first_labels != reference_labels)),
            },
        }
    return comparisons


def _plot(
    entropy_by_prefix: dict[int, np.ndarray],
    strata: np.ndarray,
    threshold: float,
    path: Path,
) -> None:
    entropy_5 = entropy_by_prefix[5]
    entropy_10 = entropy_by_prefix[10]
    entropy_20 = entropy_by_prefix[20]
    labels_5 = entropy_5 >= threshold
    labels_20 = entropy_20 >= threshold
    flipped = labels_5 != labels_20

    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.2))
    axes[0].scatter(entropy_20[~flipped], entropy_5[~flipped], s=32, alpha=0.75, label="same label")
    axes[0].scatter(entropy_20[flipped], entropy_5[flipped], s=52, marker="x", color="#d62728", label="label flip")
    limit = max(float(entropy_20.max()), float(entropy_5.max()), threshold) * 1.05
    axes[0].plot([0, limit], [0, limit], color="0.65", linestyle="--", linewidth=1)
    axes[0].axhline(threshold, color="0.35", linestyle=":", linewidth=1)
    axes[0].axvline(threshold, color="0.35", linestyle=":", linewidth=1)
    axes[0].set(xlabel="semantic entropy (20 samples)", ylabel="semantic entropy (5 samples)", xlim=(-0.03, limit), ylim=(-0.03, limit))
    axes[0].legend(frameon=False, fontsize=9)

    positions = np.arange(len(np.unique(strata)))
    widths = 0.35
    agreement_5 = []
    agreement_10 = []
    labels_10 = entropy_10 >= threshold
    for group in np.unique(strata):
        indices = strata == group
        agreement_5.append(np.mean(labels_5[indices] == labels_20[indices]))
        agreement_10.append(np.mean(labels_10[indices] == labels_20[indices]))
    axes[1].bar(positions - widths / 2, agreement_5, widths, label="5 vs 20")
    axes[1].bar(positions + widths / 2, agreement_10, widths, label="10 vs 20")
    axes[1].set(xlabel="original entropy-rank stratum", ylabel="fixed-label agreement", ylim=(0, 1.05), xticks=positions)
    axes[1].legend(frameon=False, fontsize=9)
    fig.suptitle("Qwen2.5-1.5B semantic-entropy sampling reliability (n=50)")
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def _resolve(root: Path, value: str) -> Path:
    path = Path(value).expanduser()
    return path if path.is_absolute() else root / path


def _load_experiment_config(path: str | Path) -> tuple[dict[str, Any], dict[str, Any], Path]:
    experiment_path = Path(path).expanduser().resolve()
    with experiment_path.open("r", encoding="utf-8") as handle:
        experiment = yaml.safe_load(handle)
    base_path = _resolve(root_dir(), experiment["base_config"])
    base, _ = load_config(base_path)
    return experiment, base, experiment_path


def run_label_stability(
    config_path: str | Path,
    progress: Callable[[str], None] | None = print,
) -> dict[str, Any]:
    started = time.monotonic()
    experiment, config, resolved_config_path = _load_experiment_config(config_path)
    analysis = experiment["analysis"]
    root = root_dir()
    source_dir = Path(config["project"]["results_dir"]) / experiment["source_run"]
    output_dir = _resolve(root, analysis["output_dir"])
    cache_dir = _resolve(root, analysis["cache_dir"])
    plot_path = _resolve(root, analysis["plot_path"])
    output_dir.mkdir(parents=True, exist_ok=True)
    cache_dir.mkdir(parents=True, exist_ok=True)

    records = read_jsonl(source_dir / "generations.jsonl")
    semantic_5_all = read_jsonl(source_dir / "semantic_entropy.jsonl")
    if [record["id"] for record in records] != [row["id"] for row in semantic_5_all]:
        raise ValueError("Source generations and semantic rows are not aligned")
    existing = int(analysis["existing_generations"])
    if any(len(record["generations"]) != existing for record in records):
        raise ValueError("Source generation count does not match the experiment configuration")

    entropy_all = np.asarray([row["cluster_assignment_entropy"] for row in semantic_5_all])
    selected = select_rank_stratified(
        entropy_all,
        [record["id"] for record in records],
        int(analysis["rank_strata"]),
        int(analysis["questions_per_stratum"]),
        int(analysis["selection_seed"]),
    )
    if len(selected) != int(analysis["num_questions"]):
        raise ValueError("Rank-stratified selection size is inconsistent")
    atomic_json(output_dir / "selection.json", selected)

    if progress:
        progress(f"Generating {analysis['additional_generations']} additional answers for {len(selected)} cached questions")
    generator = LocalGenerator(config)
    extra_records = []
    generation_cache_hits = 0
    try:
        for position, selection in enumerate(selected):
            source_index = selection["source_index"]
            source_record = records[source_index]
            example = {
                "id": source_record["id"],
                "question": source_record["question"],
                "context": source_record["context"],
                "answers": source_record["reference_answers"],
            }
            seed = int(config["project"]["seed"]) + source_index + int(analysis["extra_seed_offset"])
            cache_key = stable_hash(
                {
                    "model": config["models"]["generator"],
                    "generation": {key: value for key, value in config["generation"].items() if key != "layers"},
                    "id": example["id"],
                    "seed": seed,
                    "num_generations": int(analysis["additional_generations"]),
                }
            )
            cache_path = cache_dir / f"{cache_key}.json"
            if cache_path.exists():
                with cache_path.open("r", encoding="utf-8") as handle:
                    extra_record = json.load(handle)
                generation_cache_hits += 1
            else:
                extra_record, _ = generator.run_example(
                    example,
                    config["dataset"],
                    config["generation"],
                    {"num_generations": int(analysis["additional_generations"])},
                    seed,
                    cached_hidden=np.empty((len(config["generation"]["layers"]), 0), dtype=np.float16),
                )
                atomic_json(cache_path, extra_record)
            extra_records.append(extra_record)
            if progress and (position + 1) % 10 == 0:
                progress(f"Additional generation: {position + 1}/{len(selected)} questions cached")
    finally:
        generator_runtime = {
            **generator.runtime,
            "cache_hits": generation_cache_hits,
        }
        generator.close()

    combined_records = []
    for selection, extra_record in zip(selected, extra_records):
        base_record = copy.deepcopy(records[selection["source_index"]])
        base_record["generations"] = base_record["generations"] + extra_record["generations"]
        base_record["label_stability_extra_seed_offset"] = int(analysis["extra_seed_offset"])
        combined_records.append(base_record)
    write_jsonl(output_dir / "additional_generations.jsonl", extra_records)
    write_jsonl(output_dir / "combined_generations.jsonl", combined_records)

    selected_semantic_5 = [semantic_5_all[item["source_index"]] for item in selected]
    semantic_by_prefix: dict[int, list[dict[str, Any]]] = {existing: selected_semantic_5}
    entailment_judgments = []
    nli_runtime = {}
    for prefix in sorted(int(value) for value in analysis["prefixes"]):
        if prefix == existing:
            continue
        if progress:
            progress(f"Clustering the first {prefix} answers per question")
        prefix_records = []
        for record in combined_records:
            prefix_record = copy.deepcopy(record)
            prefix_record["generations"] = prefix_record["generations"][:prefix]
            prefix_records.append(prefix_record)
        rows, judgments, runtime = semantic_rows_nli(config, prefix_records)
        semantic_by_prefix[prefix] = rows
        entailment_judgments = judgments
        nli_runtime[str(prefix)] = runtime
        write_jsonl(output_dir / f"semantic_entropy_{prefix}.jsonl", rows)
    write_jsonl(output_dir / "semantic_entropy_5.jsonl", selected_semantic_5)
    write_jsonl(output_dir / "entailment_judgments_20.jsonl", entailment_judgments)

    entropy_by_prefix = {
        prefix: np.asarray([row["cluster_assignment_entropy"] for row in rows], dtype=np.float64)
        for prefix, rows in semantic_by_prefix.items()
    }
    threshold = float(analysis["fixed_entropy_threshold"])
    strata = np.asarray([row["stratum"] for row in selected], dtype=np.int64)
    comparisons = compare_prefixes(
        entropy_by_prefix,
        strata,
        threshold,
        int(analysis["bootstrap_samples"]),
        int(analysis["bootstrap_seed"]),
    )
    prefix_summaries = {}
    for prefix, entropy in entropy_by_prefix.items():
        rows = semantic_by_prefix[prefix]
        prefix_summaries[str(prefix)] = {
            "mean_entropy": float(entropy.mean()),
            "median_entropy": float(np.median(entropy)),
            "high_entropy_fraction": float(np.mean(entropy >= threshold)),
            "mean_semantic_clusters": float(np.mean([row["num_semantic_clusters"] for row in rows])),
            "minimum_entropy": float(entropy.min()),
            "maximum_entropy": float(entropy.max()),
        }

    gates = experiment["success_gates"]
    gate_results = {
        "label_agreement_5_vs_20": comparisons["5_vs_20"]["label_agreement"] >= float(gates["label_agreement_5_vs_20_min"]),
        "cohen_kappa_5_vs_20": comparisons["5_vs_20"]["cohen_kappa"] >= float(gates["cohen_kappa_5_vs_20_min"]),
        "spearman_5_vs_20": comparisons["5_vs_20"]["spearman"] >= float(gates["spearman_5_vs_20_min"]),
        "label_agreement_10_vs_20": comparisons["10_vs_20"]["label_agreement"] >= float(gates["label_agreement_10_vs_20_min"]),
    }
    _plot(entropy_by_prefix, strata, threshold, plot_path)

    result = {
        "experiment": "semantic_entropy_sampling_reliability",
        "passed": bool(all(gate_results.values())),
        "gate_results": gate_results,
        "success_gates": gates,
        "num_questions": len(selected),
        "selection": {
            "method": "equal allocation from five deterministic original-entropy rank strata",
            "seed": int(analysis["selection_seed"]),
            "stratum_counts": {str(group): int(np.sum(strata == group)) for group in np.unique(strata)},
        },
        "fixed_entropy_threshold": threshold,
        "prefix_summaries": prefix_summaries,
        "comparisons": comparisons,
        "runtime": {
            "elapsed_seconds": time.monotonic() - started,
            "generator": generator_runtime,
            "nli": nli_runtime,
        },
        "source": {
            "run": experiment["source_run"],
            "generations_sha256": _sha256(source_dir / "generations.jsonl"),
            "semantic_entropy_sha256": _sha256(source_dir / "semantic_entropy.jsonl"),
        },
        "config_path": str(resolved_config_path.relative_to(root)),
        "plot_path": str(plot_path.relative_to(root)),
    }
    atomic_json(output_dir / "label_stability_metrics.json", result)
    return result
