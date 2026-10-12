"""Deterministically select a score-free, source-independent cue-holdout set.

This scaffold selects source records and freezes rewrite conditions only. It
does not generate response rewrites, run inference, or read model scores.
Source text and rewrite inputs are written under ignored private_data/.
"""
from __future__ import annotations

import ast
import hashlib
import itertools
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[3]
CHALLENGE = REPO / "experiments" / "cue_holdout_challenge_v1"
PRIVATE = CHALLENGE / "private_data"
CANDIDATES = REPO / "experiments" / "diverse_pairs_multilayer_v1" / "private_data" / "source_candidates.jsonl"
CURRENT = REPO / "experiments" / "diverse_pairs_multilayer_v1" / "private_data" / "review_sources_50.jsonl"
HELPERS = REPO / "experiments" / "diverse_pairs_multilayer_v1" / "src"
SEED = 20261012
TASKS = ["factual_explanation", "math_logic", "programming", "comparison_analysis", "summary_judgment"]
DATASETS = ["nvidia/HelpSteer2", "allenai/WildChat-1M"]
CUE_FAMILIES = [
    "embedded_stance_predicate",
    "modal_force_scope",
    "compositional_polarity",
    "discourse_level_calibration",
    "contrastive_commitment",
]
LENGTH_DIRECTIONS = ["confident_longer", "hedged_longer"]


def _load_score_free_helpers() -> dict[str, Any]:
    """Reuse helper definitions verbatim without importing scoring dependencies."""
    sources = {
        "selection": (HELPERS / "select_review_sources.py").read_text(encoding="utf-8"),
        "preparation": (HELPERS / "prepare_review_sources.py").read_text(encoding="utf-8"),
    }
    wanted = {"task_tag", "classify", "exclusion", "digest", "norm"}
    nodes = []
    for source in sources.values():
        tree = ast.parse(source)
        nodes.extend(node for node in tree.body
                     if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in wanted)
    found = {node.name for node in nodes}
    if found != wanted:
        raise RuntimeError(f"Could not load score-free helper definitions: missing {sorted(wanted - found)}")
    namespace: dict[str, Any] = {"re": re, "hashlib": hashlib}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), "existing_score_free_helpers", "exec"), namespace)
    return namespace


_HELPERS = _load_score_free_helpers()
# The preparation-stage classifier has broader coverage than the later review
# selector's narrow tags, which is needed to make ten sources per task feasible.
task_tag = _HELPERS["classify"]
exclusion = _HELPERS["exclusion"]
digest = _HELPERS["digest"]
norm = _HELPERS["norm"]


def template_group(prompt: str) -> str:
    """Apply the existing development selector's canonical template rule."""
    canonical = re.sub(r"\b(?:antonius|carmen|anthony|ben)\b|\d+(?:\.\d+)?", "<var>", norm(prompt))
    if "pretend you are a tutor" in canonical:
        canonical = "factoring_tutor_template"
    if "safetensors" in canonical:
        canonical = "safetensors_conversion_template"
    return digest(canonical)


def screen_candidates(candidates: list[dict], current: list[dict]) -> tuple[list[dict], Counter]:
    """Filter existing task exclusions and every current source/group/hash/template overlap."""
    current_ids = {row["source_id"] for row in current}
    current_groups = {row["group_id"] for row in current}
    current_prompts = {row["normalized_prompt_sha256"] for row in current}
    current_templates = {row.get("development_template_group") or template_group(row["prompt"])
                         for row in current}
    screened: list[dict] = []
    rejected: Counter = Counter()
    for candidate in candidates:
        row = candidate.copy()
        reason = exclusion(row)
        row_template = template_group(row["prompt"])
        if reason:
            rejected["existing_exclusion:" + reason] += 1
        elif row["source_id"] in current_ids:
            rejected["source_id_overlap"] += 1
        elif row["group_id"] in current_groups:
            rejected["group_id_overlap"] += 1
        elif row["normalized_prompt_sha256"] in current_prompts:
            rejected["prompt_hash_overlap"] += 1
        elif row_template in current_templates:
            rejected["template_group_overlap"] += 1
        else:
            row["task"] = task_tag(row["prompt"])
            row["development_template_group"] = row_template
            screened.append(row)
    return screened, rejected


def _stable_key(row: dict) -> str:
    return digest(f"{SEED}:{row['source_id']}")


def _task_dataset_quotas(screened: list[dict]) -> list[dict[str, int]]:
    available = Counter((row["task"], row["dataset"]) for row in screened)
    possibilities = []
    for helps in itertools.product(range(11), repeat=len(TASKS)):
        quota = {}
        feasible = True
        for task, help_count in zip(TASKS, helps):
            wild_count = 10 - help_count
            if help_count > available[(task, DATASETS[0])] or wild_count > available[(task, DATASETS[1])]:
                feasible = False
                break
            quota[task] = help_count
        if feasible:
            possibilities.append(quota)
    # Try 25/25 first; if unavailable, use the closest feasible total, then
    # prefer near-even per-task balance. Task order breaks remaining ties.
    possibilities.sort(key=lambda q: (abs(sum(q.values()) - 25),
                                      sum(abs(q[t] - 5) for t in TASKS),
                                      tuple(q[t] for t in TASKS)))
    return possibilities


def _pick_for_quotas(screened: list[dict], quota: dict[str, int]) -> list[dict] | None:
    selected: list[dict] = []
    used_templates: set[str] = set()
    for task in TASKS:
        task_rows = [row for row in screened if row["task"] == task]
        # Fill per-source-dataset quotas while distributing short/medium/long rows.
        task_selected: list[dict] = []
        length_counts: Counter = Counter()
        target_lengths = {"short": 3, "medium": 3, "long": 4}
        for dataset in DATASETS:
            needed = quota[task] if dataset == DATASETS[0] else 10 - quota[task]
            pool = sorted((row for row in task_rows
                           if row["dataset"] == dataset
                           and row["development_template_group"] not in used_templates), key=_stable_key)
            for _ in range(needed):
                if not pool:
                    return None
                pool.sort(key=lambda row: (
                    length_counts[row["length_bin"]] >= target_lengths.get(row["length_bin"], 0),
                    length_counts[row["length_bin"]] - target_lengths.get(row["length_bin"], 0),
                    _stable_key(row),
                ))
                pick = pool.pop(0)
                task_selected.append(pick)
                used_templates.add(pick["development_template_group"])
                length_counts[pick["length_bin"]] += 1
                pool = [row for row in pool if row["development_template_group"] != pick["development_template_group"]]
        if len(task_selected) != 10:
            return None
        selected.extend(task_selected)
    return selected if len(selected) == 50 else None


def assign_conditions(selected: list[dict]) -> list[dict]:
    """Assign each task × cue family two sources, one per length direction."""
    if len(selected) != 50:
        raise ValueError("Exactly 50 selected sources are required")
    counts = Counter(row["task"] for row in selected)
    if any(counts[task] != 10 for task in TASKS) or set(counts) != set(TASKS):
        raise ValueError("Selection must contain exactly 10 sources per task")
    assigned = []
    for task in TASKS:
        pool = sorted((row.copy() for row in selected if row["task"] == task), key=_stable_key)
        for family_index, family in enumerate(CUE_FAMILIES):
            pair = pool[family_index * 2: family_index * 2 + 2]
            for direction, row in zip(LENGTH_DIRECTIONS, pair):
                row["cue_family"] = family
                row["length_direction"] = direction
                assigned.append(row)
    return assigned


def validate_assignment(rows: list[dict], allow_dataset_imbalance: bool = False) -> None:
    if len(rows) != 50:
        raise ValueError("Expected exactly 50 assigned sources")
    if len({row["source_id"] for row in rows}) != 50:
        raise ValueError("Duplicate source IDs in selection")
    if len({row["development_template_group"] for row in rows}) != 50:
        raise ValueError("More than one source from a canonical template group")
    task_counts = Counter(row["task"] for row in rows)
    if task_counts != Counter({task: 10 for task in TASKS}):
        raise ValueError(f"Task quotas not met: {dict(task_counts)}")
    dataset_counts = Counter(row["dataset"] for row in rows)
    if dataset_counts != Counter({dataset: 25 for dataset in DATASETS}):
        gap = abs(dataset_counts[DATASETS[0]] - dataset_counts[DATASETS[1]])
        if not allow_dataset_imbalance or gap > 2:
            raise ValueError(f"Dataset quotas not met: {dict(dataset_counts)}")
    if len({row["group_id"] for row in rows}) != 50:
        raise ValueError("Duplicate source group IDs in selection")
    if len({row["normalized_prompt_sha256"] for row in rows}) != 50:
        raise ValueError("Duplicate prompt hashes in selection")
    combinations = Counter((row["task"], row["cue_family"]) for row in rows)
    if combinations != Counter({(task, family): 2 for task in TASKS for family in CUE_FAMILIES}):
        raise ValueError("Each task × cue-family cell must contain exactly two sources")
    directions = Counter((row["task"], row["cue_family"], row["length_direction"]) for row in rows)
    if directions != Counter({(task, family, direction): 1 for task in TASKS
                              for family in CUE_FAMILIES for direction in LENGTH_DIRECTIONS}):
        raise ValueError("Each task × cue-family cell must have one source per length direction")
    if any(row["cue_family"] not in CUE_FAMILIES for row in rows):
        raise ValueError("Unknown cue family")


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
                    encoding="utf-8")


def select_sources(candidates: list[dict], current: list[dict]) -> tuple[list[dict], Counter]:
    screened, rejected = screen_candidates(candidates, current)
    quotas = _task_dataset_quotas(screened)
    if not quotas:
        counts = Counter((row["task"], row["dataset"]) for row in screened)
        raise RuntimeError(f"Infeasible 50-source/10-per-task/25-per-dataset quotas; available={dict(counts)}")
    selected = None
    for quota in quotas:
        selected = _pick_for_quotas(screened, quota)
        if selected is not None:
            break
    if selected is None:
        raise RuntimeError("Exact quotas were feasible by count but no unique-template selection was found")
    assigned = assign_conditions(selected)
    dataset_counts = Counter(row["dataset"] for row in assigned)
    validate_assignment(assigned, allow_dataset_imbalance=dataset_counts != Counter({dataset: 25 for dataset in DATASETS}))
    return assigned, rejected


def _public_manifest(rows: list[dict], rejected: Counter) -> dict:
    dataset_counts = Counter(row["dataset"] for row in rows)
    task_counts = Counter(row["task"] for row in rows)
    length_counts = Counter(row["length_bin"] for row in rows)
    family_counts = Counter(row["cue_family"] for row in rows)
    direction_counts = Counter(row["length_direction"] for row in rows)
    cell_counts = Counter((row["task"], row["cue_family"], row["length_direction"]) for row in rows)
    keys = ["source_id", "group_id", "normalized_prompt_sha256", "original_response_sha256",
            "development_template_group", "dataset", "task", "length_bin", "cue_family", "length_direction"]
    return {
        "selection_version": 1,
        "seed": SEED,
        "selection_method": "deterministic score-free constrained selection; existing preparation-stage classify and selector exclusion helpers reused",
        "source_count": len(rows),
        "by_dataset": dict(sorted(dataset_counts.items())),
        "dataset_balance_exact_25_each": dataset_counts == Counter({dataset: 25 for dataset in DATASETS}),
        "by_task": dict(sorted(task_counts.items())),
        "by_length_bin": dict(sorted(length_counts.items())),
        "by_cue_family": dict(sorted(family_counts.items())),
        "by_length_direction": dict(sorted(direction_counts.items())),
        "task_family_direction_counts": [
            {"task": task, "cue_family": family, "length_direction": direction,
             "count": cell_counts[(task, family, direction)]}
            for task in TASKS for family in CUE_FAMILIES for direction in LENGTH_DIRECTIONS
        ],
        "screened_out_counts": dict(sorted(rejected.items())),
        "source_records": [{key: row[key] for key in keys} for row in rows],
    }


def main() -> None:
    candidates = [json.loads(line) for line in CANDIDATES.read_text(encoding="utf-8").splitlines() if line.strip()]
    current = [json.loads(line) for line in CURRENT.read_text(encoding="utf-8").splitlines() if line.strip()]
    assigned, rejected = select_sources(candidates, current)
    assigned.sort(key=lambda row: (TASKS.index(row["task"]), CUE_FAMILIES.index(row["cue_family"]),
                                   LENGTH_DIRECTIONS.index(row["length_direction"])))
    # Full source records and prompt/answer text remain private.
    private_keys = ["source_id", "dataset", "dataset_revision", "group_id", "normalized_prompt_sha256",
                    "original_response_sha256", "development_template_group", "task", "length_bin",
                    "prompt", "original_response", "cue_family", "length_direction"]
    _write_jsonl(PRIVATE / "challenge_sources_50.jsonl", [{key: row[key] for key in private_keys} for row in assigned])
    for task in TASKS:
        batch_keys = ["source_id", "dataset", "original_response_sha256", "task", "length_bin",
                      "prompt", "original_response", "cue_family", "length_direction"]
        batch = [{key: row[key] for key in batch_keys} for row in assigned if row["task"] == task]
        _write_jsonl(PRIVATE / f"rewrite_input_{task}.jsonl", batch)
    manifest = _public_manifest(assigned, rejected)
    manifest_path = CHALLENGE / "manifests" / "challenge_selection_manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                             encoding="utf-8")
    print(json.dumps({"source_count": len(assigned), "by_dataset": manifest["by_dataset"],
                      "by_task": manifest["by_task"], "by_length_bin": manifest["by_length_bin"],
                      "cue_family_direction_cells": len(manifest["task_family_direction_counts"]),
                      "rewrite_generation": "not run", "inference": "not run"}))


if __name__ == "__main__":
    main()
