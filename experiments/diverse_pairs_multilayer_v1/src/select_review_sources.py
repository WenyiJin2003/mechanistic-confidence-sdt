"""Stricter score-free selection from the already acquired bounded source pool."""
from __future__ import annotations

import json
import re
import shutil
from collections import Counter
from pathlib import Path

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp

from prepare_review_sources import BASE, PRIVATE, SEED, TASKS, digest, norm, write_json, write_jsonl


def task_tag(prompt: str) -> str:
    p = prompt.casefold()
    if re.search(r"\b(?:summari[sz]e|summary|summaries|synopsis|summrize|main.idea|classif)\w*\b", p):
        return "summary_judgment"
    if re.search(r"\bc\+\+|\b(?:python|javascript|typescript|sql|debug|safetensors|pytorch|regex|programming)\b|\b(?:write|implement|create)\b.{0,30}\b(?:code|function|program)\b", p):
        return "programming"
    if re.search(r"\b(?:calculate|solve|equation|arithmetic|algebra|probability|mathematical|math|factor|integral|derivative|cournot|oligopoly|vectors|orthogonal)\b|\d\s*[+*/=]\s*\d", p):
        return "math_logic"
    if re.search(r"\b(?:compare|comparison|contrast|versus|pros.and.cons|advantages|disadvantages|analy[sz]e|argument|trade.off|better|evaluate|review|assess)\b", p):
        return "comparison_analysis"
    return "factual_explanation"


def exclusion(row: dict) -> str | None:
    p, r = row["prompt"].casefold(), row["original_response"].casefold()
    if row["response_tokens"] < 60:
        return "too_short_for_initial_content_audit"
    if re.search(r"\b(?:rewrite|rephrase|resume|synopsis|email|greetings|invoice|finalists|comebacks)\b", p):
        return "social_or_editorial_task_deferred_from_initial_pilot"
    if re.search(r"\b(?:my.palm|wrist.fracture|6th.grade|named.lincoln|i.am.tired|my.boss|theoretical.food|controversial.era|military.capabilities)\b", p):
        return "personal_or_underspecified_or_inapplicable_initial_task"
    if re.search(r"\b(?:give|write|create|make)\b.{0,35}\bsentences?\b.{0,50}\b(?:end|word|include)\b", p):
        return "pure_creative_or_surface_word_task"
    if "i want you to act as" in p and "code" not in p[p.find("i will provide") + 1:]:
        return "role_setup_without_substantive_source_answer"
    if re.match(r"\s*(?:sure|certainly|of course)[!,.]?\s+i(?:'d| would| can| will)\s", r) and len(r.split()) < 70:
        return "acknowledgment_without_substantive_answer"
    return None


def main():
    rows = [json.loads(x) for x in (PRIVATE / "source_candidates.jsonl").read_text().splitlines()]
    screened, rejected = [], []
    for row in rows:
        reason = exclusion(row)
        if reason:
            rejected.append({"source_id": row["source_id"], "reason": reason})
            continue
        row["task"] = task_tag(row["prompt"])
        # Group recurring problem/editorial templates despite number/name changes.
        canonical = re.sub(r"\b(?:antonius|carmen|anthony|ben)\b|\d+(?:\.\d+)?", "<var>", norm(row["prompt"]))
        if "pretend you are a tutor" in canonical:
            canonical = "factoring_tutor_template"
        if "safetensors" in canonical:
            canonical = "safetensors_conversion_template"
        row["development_template_group"] = digest(canonical)
        screened.append(row)
    n = len(screened)
    constraints, lower, upper = [], [], []
    def add(mask, lo, hi):
        constraints.append(np.asarray(mask, dtype=float)); lower.append(lo); upper.append(hi)
    add([1] * n, 50, 50)
    add([r["dataset"] == "allenai/WildChat-1M" for r in screened], 38, 38)
    for task in TASKS:
        add([r["task"] == task for r in screened], 6, 20)
    for length in ["short", "medium", "long"]:
        add([r["length_bin"] == length for r in screened], 6, 30)
    for group in {r["development_template_group"] for r in screened}:
        indices = [i for i, r in enumerate(screened) if r["development_template_group"] == group]
        if len(indices) > 1:
            add([i in indices for i in range(n)], 0, 1)
    cost = np.array([int(digest(str(SEED) + r["source_id"])[:12], 16) / 16**12 for r in screened])
    result = milp(cost, integrality=np.ones(n), bounds=Bounds(0, 1),
                  constraints=LinearConstraint(np.asarray(constraints), lower, upper),
                  options={"time_limit": 15})
    if result.x is None:
        raise RuntimeError("Coverage constraints infeasible; keep original inventory and request design decision")
    chosen = [r.copy() for r, flag in zip(screened, result.x) if flag > 0.5]
    if len(chosen) != 50:
        raise ValueError("Unexpected source count")
    pools = {task: sorted([r for r in chosen if r["task"] == task], key=lambda r: digest(str(SEED) + r["source_id"])) for task in TASKS}
    # Interleave task groups without treating scarce tasks as an exact quota.
    chosen = [pool[rank] for rank in range(max(map(len, pools.values()))) for task in TASKS
              if rank < len(pool := pools[task])]
    import random
    orders = ["confident_first"] * 25 + ["hedged_first"] * 25
    random.Random(SEED).shuffle(orders)
    for i, row in enumerate(chosen, 1):
        row.update(review_id=f"P{i:03d}", rewrite_family="A" if i % 2 else "B",
                   rewrite_output_order=orders[i - 1], human_review="pending")
    backup = PRIVATE / "selection_v0"
    backup.mkdir(exist_ok=True)
    for name in ["review_sources_50.jsonl", "rewrite_input_batch_1.jsonl", "rewrite_input_batch_2.jsonl", "rewrite_input_batch_3.jsonl"]:
        if (PRIVATE / name).exists() and not (backup / name).exists():
            shutil.copy2(PRIVATE / name, backup / name)
    write_jsonl(PRIVATE / "review_sources_50.jsonl", chosen)
    for batch, a, b in [(1, 0, 17), (2, 17, 34), (3, 34, 50)]:
        keys = ["review_id", "source_id", "original_response_sha256", "prompt", "original_response", "rewrite_family", "rewrite_output_order"]
        write_jsonl(PRIVATE / f"rewrite_input_batch_{batch}.jsonl", [{k: r[k] for k in keys} for r in chosen[a:b]])
    write_jsonl(PRIVATE / "selection_extra_rejections.jsonl", rejected)
    old_manifest = BASE / "manifests" / "review_source_inventory.json"
    old = json.loads(old_manifest.read_text())
    if not (BASE / "manifests" / "review_source_inventory_v0.json").exists():
        write_json(BASE / "manifests" / "review_source_inventory_v0.json", old)
    old.update(selection_version=1, selection_rule="deterministic constrained selection, score-free; social/private/incomplete tasks excluded; task tags are heuristics",
               by_dataset=dict(Counter(r["dataset"] for r in chosen)), by_task=dict(Counter(r["task"] for r in chosen)),
               by_length=dict(Counter(r["length_bin"] for r in chosen)), extra_screened_out=len(rejected),
               grouping=old["grouping"] + "; prompt 5-gram >=0.85 screen; one per recurring tutoring/conversion template",
               source_records=[{k: r[k] for k in ["source_id", "dataset", "dataset_revision", "group_id", "development_template_group", "review_id", "task", "length_bin", "original_response_sha256"]} for r in chosen])
    write_json(old_manifest, old)
    print(json.dumps({"sources": 50, "by_source": old["by_dataset"], "by_task": old["by_task"],
                      "by_length": old["by_length"], "extra_screened_out": len(rejected), "rewrite_calls": 0}))


if __name__ == "__main__":
    main()
