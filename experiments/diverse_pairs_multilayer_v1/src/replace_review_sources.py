"""Retain unusable drafts and use deterministic same-source/task reserves."""
import json
import shutil
from collections import Counter

from prepare_review_sources import BASE, PRIVATE, SEED, digest, norm, write_json, write_jsonl
from select_review_sources import exclusion, task_tag


def main():
    current = [json.loads(x) for x in (PRIVATE / "review_sources_50.jsonl").read_text().splitlines()]
    candidates = [json.loads(x) for x in (PRIVATE / "source_candidates.jsonl").read_text().splitlines()]
    targets = {"P038": "Code-only source offers no editable epistemic explanation; identical pair rejected",
               "P041": "Pure creative sentence task unsuitable; observed frequency change always->might is not content preserving"}
    old_ids = {r["source_id"] for r in current}
    selected_prompts = {r["normalized_prompt_sha256"] for r in current}
    chosen_groups = {r["development_template_group"] for r in current}
    reserves, replacements, rejected = {}, [], []
    for row in candidates:
        if row["source_id"] in old_ids or row["normalized_prompt_sha256"] in selected_prompts or exclusion(row):
            continue
        row["task"] = task_tag(row["prompt"])
        canonical = __import__("re").sub(r"\b(?:antonius|carmen|anthony|ben)\b|\d+(?:\.\d+)?", "<var>", norm(row["prompt"]))
        if "pretend you are a tutor" in canonical: canonical = "factoring_tutor_template"
        if "safetensors" in canonical: canonical = "safetensors_conversion_template"
        row["development_template_group"] = digest(canonical)
        if row["development_template_group"] not in chosen_groups:
            reserves.setdefault((row["dataset"], row["task"]), []).append(row)
    for pool in reserves.values():
        pool.sort(key=lambda r: digest(str(SEED) + r["source_id"]))
    replacement_log = []
    for i, old in enumerate(current):
        if old["review_id"] not in targets: continue
        pool = reserves[(old["dataset"], old["task"])]
        pick = next(r for r in pool if r["development_template_group"] not in chosen_groups)
        new = pick.copy()
        for k in ["review_id", "rewrite_family", "rewrite_output_order"]: new[k] = old[k]
        new.update(human_review="pending", replacement_for_source_id=old["source_id"])
        current[i] = new
        chosen_groups.add(new["development_template_group"])
        replacements.append(new)
        rejected.append({"old_source": old, "reason": targets[old["review_id"]]})
        replacement_log.append({"review_id": old["review_id"], "old_source_id": old["source_id"], "new_source_id": new["source_id"], "reason": targets[old["review_id"]], "reserve_rule": "same source/task, lowest fixed-seed source hash not already selected; no probe scores"})
    backup = PRIVATE / "rewrite_selection_v1"
    backup.mkdir(exist_ok=True)
    for name in ["review_sources_50.jsonl", "PAIRED_RESPONSES_50.jsonl", "PAIR_QA_50.jsonl", "REVIEW_50_PAIRS.html"]:
        if (PRIVATE / name).exists() and not (backup / name).exists(): shutil.copy2(PRIVATE / name, backup / name)
    write_jsonl(PRIVATE / "rejected_rewrite_sources.jsonl", rejected)
    write_jsonl(PRIVATE / "review_sources_50.jsonl", current)
    keys = ["review_id", "source_id", "original_response_sha256", "prompt", "original_response", "rewrite_family", "rewrite_output_order"]
    write_jsonl(PRIVATE / "rewrite_input_replacements.jsonl", [{k: r[k] for k in keys} for r in replacements])
    write_json(BASE / "manifests" / "source_replacements.json", replacement_log)
    manifest_path = BASE / "manifests" / "review_source_inventory.json"
    manifest = json.loads(manifest_path.read_text())
    manifest.update(selection_version=2, rewrite_rejected_sources=2,
                    by_dataset=dict(Counter(r["dataset"] for r in current)), by_task=dict(Counter(r["task"] for r in current)),
                    by_length=dict(Counter(r["length_bin"] for r in current)),
                    source_records=[{k: r[k] for k in ["source_id", "dataset", "dataset_revision", "group_id", "development_template_group", "review_id", "task", "length_bin", "original_response_sha256"]} for r in current])
    write_json(manifest_path, manifest)
    print(json.dumps({"replaced": replacement_log, "sources_retained": len(current), "counts": manifest["by_task"]}))


if __name__ == "__main__": main()
