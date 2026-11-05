#!/usr/bin/env python3
"""Run one frozen model/shard cell using the validated lambda evaluator."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path


EXPERIMENT = Path(__file__).resolve().parents[1]
REPO = EXPERIMENT.parents[1]
EVALUATOR_PATH = REPO / (
    "experiments/confidence_probe_guided_lora_lambda_canary_20261104_v1/"
    "src/evaluate_adapters.py"
)
SPEC = importlib.util.spec_from_file_location("lambda_evaluator", EVALUATOR_PATH)
assert SPEC and SPEC.loader
evaluator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(evaluator)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--authority", type=Path, required=True)
    parser.add_argument("--run-manifest", type=Path, required=True)
    parser.add_argument("--probe-artifact", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--shard-index", type=int, required=True)
    parser.add_argument("--shard-file", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    authority = json.loads(args.authority.read_text(encoding="utf-8"))
    if authority.get("schema") != "confidence-output-direct-eval500-authority-v1":
        raise ValueError("unexpected authority schema")
    if authority.get("status") != "READY_FOR_ONCE_ONLY_TEN_JOB_GENERATION":
        raise ValueError("authority is not active")
    if args.run_id not in authority["allowed_run_ids"]:
        raise ValueError("run is outside frozen authority")
    if args.shard_index not in range(5):
        raise ValueError("shard index must be 0..4")
    shard_record = authority["shards"][args.shard_index]
    if evaluator.file_sha256(args.shard_file) != shard_record["sha256"]:
        raise ValueError("shard hash mismatch")
    if evaluator.file_sha256(args.run_manifest) != authority["evaluation_manifest_sha256"]:
        raise ValueError("evaluation manifest hash mismatch")
    if evaluator.file_sha256(args.probe_artifact) != authority["probe_artifact_sha256"]:
        raise ValueError("probe artifact hash mismatch")
    all_runs = evaluator.load_run_manifest(args.run_manifest.resolve())
    selected = [run for run in all_runs if run["run_id"] == args.run_id]
    if len(selected) != 1:
        raise ValueError("frozen run ID is missing or ambiguous")
    raw_rows = evaluator.read_json_rows(args.shard_file)
    questions = []
    observed = set()
    for row in raw_rows:
        eval_id = row.get("eval_id")
        question = row.get("question")
        if not isinstance(eval_id, str) or not eval_id or eval_id in observed:
            raise ValueError("shard eval IDs must be unique nonempty strings")
        if not isinstance(question, str) or not question.strip():
            raise ValueError(f"{eval_id}: question is missing")
        observed.add(eval_id)
        questions.append({"split": f"eval500_shard_{args.shard_index:02d}", "item_id": eval_id, "question": question})
    if len(questions) != 100:
        raise ValueError("each frozen shard must contain exactly 100 rows")
    probe = evaluator.load_probe(args.probe_artifact.resolve())
    args.output_dir.mkdir(parents=True, exist_ok=True)
    evaluator.evaluate_run(
        selected[0],
        questions,
        probe,
        args.output_dir.resolve(),
        args.run_manifest.resolve(),
        {f"eval500_shard_{args.shard_index:02d}": args.shard_file.resolve()},
        int(authority["decoding"]["max_new_tokens"]),
    )


if __name__ == "__main__":
    main()
