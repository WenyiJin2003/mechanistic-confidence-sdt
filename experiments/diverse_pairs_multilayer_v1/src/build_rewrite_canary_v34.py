"""Freeze a balanced 20-source canary from v3.3 source-review eligibles."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp

from experiments.diverse_pairs_multilayer_v1.src import (
    run_claude_rewrite_batches as helpers,
)
from experiments.diverse_pairs_multilayer_v1.src import (
    run_claude_rewrite_batches_v33 as rewrite_v33,
)
from experiments.diverse_pairs_multilayer_v1.src import (
    run_claude_source_review_v33 as source_review,
)


BASE = Path(__file__).resolve().parents[1]
PRIVATE_OUTPUT = BASE / "private_data" / "rewrite_dev_v34" / "SOURCE_CANARY_20.jsonl"
PUBLIC_MANIFEST = BASE / "manifests" / "rewrite_dev_v34_freeze.json"

QUOTAS = {
    ("dataset", "allenai/WildChat-1M"): 15,
    ("dataset", "nvidia/HelpSteer2"): 5,
    ("task", "factual_explanation"): 8,
    ("task", "math_logic"): 4,
    ("task", "programming"): 3,
    ("task", "summary_judgment"): 3,
    ("task", "comparison_analysis"): 2,
    ("length_bin", "short"): 4,
    ("length_bin", "medium"): 8,
    ("length_bin", "long"): 8,
    ("stance_topology", "early"): 5,
    ("stance_topology", "middle"): 5,
    ("stance_topology", "late"): 5,
    ("stance_topology", "distributed"): 5,
    ("rewrite_recipe", "A"): 10,
    ("rewrite_recipe", "B"): 10,
    ("rewrite_output_order", "confident_first"): 10,
    ("rewrite_output_order", "hedged_first"): 10,
    ("target_longer_member", "confident"): 10,
    ("target_longer_member", "hedged"): 10,
}


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    config = source_review.load_config(source_review.DEFAULT_CONFIG)
    rows, _ = rewrite_v33.validate_frozen_input(
        config.input_path, config.input_manifest_path, config.expected_sources
    )
    fingerprint = source_review._fingerprint(config, rows)
    batches = source_review.make_batches(rows, config.batch_size)
    review_by_id = {}
    review_hashes = {}
    for index, batch in enumerate(batches, 1):
        path = config.output_dir / "parsed" / f"{source_review._batch_id(index, batch)}.json"
        parsed = source_review._load_existing(
            path,
            fingerprint,
            batch,
            config.accepted_legacy_cache_fingerprints,
        )
        if parsed is None:
            raise ValueError("All five source-review batches must be complete")
        review_hashes[path.name] = helpers.sha256_file(path)
        for record in parsed["records"]:
            review_by_id[record["source_id"]] = record

    candidates = [
        row for row in rows
        if review_by_id[row["source_id"]]["decision"] == "eligible"
    ]
    if len(candidates) != 74:
        raise ValueError("The frozen v3.3 source review must contain 74 eligibles")
    matrix = []
    targets = []
    for (field, value), quota in QUOTAS.items():
        matrix.append([1.0 if str(row[field]) == value else 0.0 for row in candidates])
        targets.append(float(quota))
    # The tiny increasing objective deterministically picks the earliest feasible
    # production slots without changing the exact balance constraints.
    result = milp(
        c=np.arange(len(candidates), dtype=float) * 1e-6,
        integrality=np.ones(len(candidates)),
        bounds=Bounds(0, 1),
        constraints=LinearConstraint(
            np.asarray(matrix), np.asarray(targets), np.asarray(targets)
        ),
        options={"time_limit": 30},
    )
    if not result.success:
        raise RuntimeError(f"Balanced v3.4 canary is infeasible: {result.message}")
    selected = [row for row, value in zip(candidates, result.x) if value > 0.5]
    selected.sort(key=lambda row: int(str(row["production_slot"])[1:]))
    if len(selected) != 20:
        raise ValueError("V3.4 canary selection did not contain 20 sources")
    observed = {
        f"{field}:{value}": sum(str(row[field]) == value for row in selected)
        for field, value in QUOTAS
    }
    expected = {f"{field}:{value}": quota for (field, value), quota in QUOTAS.items()}
    if observed != expected:
        raise ValueError("V3.4 canary quotas were not met exactly")

    _write_jsonl(PRIVATE_OUTPUT, selected)
    manifest = {
        "protocol_version": "claude-symmetric-diverse-rewrite-v3.4",
        "contains_source_text": False,
        "source_review_protocol": source_review.PROTOCOL_VERSION,
        "source_review_generation_fingerprint": fingerprint,
        "source_review_decision_counts": {
            "eligible": 74, "needs_human_review": 16, "reject": 110
        },
        "source_review_human_certified": False,
        "selection_rule": "deterministic_binary_milp_earliest_feasible_slots",
        "selected_source_count": len(selected),
        "selected_file_name": PRIVATE_OUTPUT.name,
        "selected_file_sha256": helpers.sha256_file(PRIVATE_OUTPUT),
        "selected_source_ids_sha256": helpers.source_ids_sha256(selected),
        "quota_counts": observed,
        "private_source_review_artifact_sha256": dict(sorted(review_hashes.items())),
        "model_calls_for_selection": 0,
    }
    helpers.atomic_write_json(PUBLIC_MANIFEST, manifest)
    print(json.dumps({
        "selected": len(selected),
        "eligible_pool": len(candidates),
        "file_sha256": manifest["selected_file_sha256"],
        "source_ids_sha256": manifest["selected_source_ids_sha256"],
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
