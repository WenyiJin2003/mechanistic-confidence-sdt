"""Bounded engineering benchmark; explicitly not a research probe experiment."""
from __future__ import annotations

import argparse
import json
import time
from collections import Counter
from pathlib import Path

import numpy as np

from extraction import extract_rows, load_config, resolve, write_json, write_npz


def choose_pairs(pairs, count):
    if count < 1 or count > len(pairs):
        raise ValueError("Requested pair count is outside the available development pool")
    if len({p["source_id"] for p in pairs}) != len(pairs):
        raise ValueError("Duplicate source pairs in engineering pool")
    ordered = sorted(pairs, key=lambda p: (max(v["full_input_tokens"] for v in p["token_stats"].values()), p["review_id"]))
    # Fixed evenly spaced ranks include the shortest and longest actual inputs.
    ranks = np.linspace(0, len(ordered) - 1, count).round().astype(int)
    return [ordered[i] for i in ranks]


def flatten_pairs(pairs):
    rows = []
    for pair in pairs:
        if pair.get("reserved_split") != "train_development":
            raise ValueError("This preflight only reads reserved development material")
        for variant in ["confident", "hedged"]:
            rows.append({"source_id": pair["source_id"], "group_id": pair["group_id"],
                         "review_id": pair["review_id"], "variant": variant,
                         "prompt": pair["prompt"], "response_text": pair[variant + "_response"],
                         "human_review": pair.get("human_review", "pending")})
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=str(Path(__file__).resolve().parents[1] / "configs/diverse_pairs_multilayer_v1.yaml"))
    parser.add_argument("--pairs", type=int, default=20)
    args = parser.parse_args()
    config = load_config(args.config)
    if args.pairs > config["runtime"]["max_pairs"]:
        parser.error("Requested count exceeds the configured engineering cap")
    source_file = resolve(config, config["data"]["pairs"])
    pairs = [json.loads(line) for line in source_file.read_text().splitlines() if line.strip()]
    chosen = choose_pairs(pairs, args.pairs)
    rows = flatten_pairs(chosen)
    target = resolve(config, config["output"]["sanity"])
    started = time.monotonic()
    try:
        enriched, states, audit = extract_rows(rows, config, check_padding=True)
        # Resume must neither load the model nor call it. Array equality is exact
        # because both paths use the serialized FP16 pooled vectors.
        remaining = config["runtime"]["max_seconds"] - (time.monotonic() - started)
        if remaining <= 0:
            raise TimeoutError("No time left to validate cache-only resume")
        resume_config = {**config, "runtime": {**config["runtime"], "max_seconds": remaining}}
        _, resumed, resume = extract_rows(rows, resume_config, check_padding=False)
        if resume["forward_calls"] != 0 or resume["cache_hits"] != len(rows) or not np.array_equal(states, resumed):
            raise ValueError("Cache-only rerun did not exactly recover all states")
        private_file = resolve(config, config["output"]["private_rows"])
        private_file.parent.mkdir(parents=True, exist_ok=True)
        temp = private_file.with_name(private_file.name + ".tmp")
        temp.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in enriched), encoding="utf-8")
        temp.replace(private_file)
        write_npz(resolve(config, config["output"]["private_states"]),
                  states=states, layer_ids=np.asarray(config["model"]["layers"]), positions=np.asarray(audit["positions"]),
                  source_ids=np.asarray([r["source_id"] for r in rows]), variants=np.asarray([r["variant"] for r in rows]))
        all_counts = [max(v["full_input_tokens"] for v in p["token_stats"].values()) for p in pairs]
        rate = audit["forward_tokens_per_second"]
        # Rough linear token budget, not a full-pass prediction or authorization.
        estimate = None
        if rate:
            per_response = np.percentile(all_counts, [25, 75]).tolist()
            estimate = {"scope": "2000 responses only; excludes template baseline, rewriting and review",
                        "token_linear_minutes_q25_to_q75": [2000 * t / rate / 60 for t in per_response],
                        "limitations": "40 responses and SDPA timing do not capture all nonlinear length effects or memory pressure; benchmark is not population-random"}
        audit.update(status="passed", phase="engineering_only", pairs=args.pairs,
                     review_ids=[p["review_id"] for p in chosen], selection=f"{args.pairs} evenly spaced ranks of current full-input lengths; fixed before forward",
                     task_coverage=dict(Counter(p["task"] for p in chosen)),
                     source_coverage=dict(Counter(p["dataset"] for p in chosen)),
                     actual_token_range=[min(len(t["tokens"]["input_ids"]) for t in enriched), max(len(t["tokens"]["input_ids"]) for t in enriched)],
                     response_token_range=[min(len(t["tokens"]["response_ids"]) for t in enriched), max(len(t["tokens"]["response_ids"]) for t in enriched)],
                     cache_resume={"forward_calls": resume["forward_calls"], "cache_hits": resume["cache_hits"], "exact_arrays": True, "seconds": resume["elapsed_seconds"]},
                     total_elapsed_seconds=time.monotonic() - started,
                     pooled_uncompressed_bytes=int(states.nbytes), rough_forward_budget=estimate,
                     final_test_scored=False, original_packet_changed=False)
        # Public aggregates omit absolute local snapshot paths and all token/text
        # content. Cache provenance stores hashes, not private source bodies.
        audit["settings"]["model"] = {k: v for k, v in audit["settings"]["model"].items() if k != "snapshot"}
        write_json(target, audit)
        print(json.dumps({k: audit[k] for k in ["status", "pairs", "device", "dtype", "forward_calls", "cache_hits", "total_elapsed_seconds", "peak_process_rss_bytes", "max_prompt_state_difference", "cache_resume"]}), flush=True)
    except Exception as error:
        write_json(target, {"status": "failed", "phase": "engineering_only", "error_type": type(error).__name__,
                            "error": str(error)[:400], "elapsed_seconds": time.monotonic() - started,
                            "human_review": "pending", "scientific_probe_fitted": False,
                            "partial_cache_retained": True})
        raise


if __name__ == "__main__":
    main()
