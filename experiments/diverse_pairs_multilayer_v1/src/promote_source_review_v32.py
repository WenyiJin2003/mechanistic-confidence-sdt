"""Promote completed v3.2 source-only reviews to 64 and then 32 rows.

The command fails before writing anything when a review is incomplete or exact
dataset/task/length quotas are infeasible.  It never calls a model and never
assigns rewrite recipe, topology, or confidence labels.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping, Sequence

from experiments.diverse_pairs_multilayer_v1.src import build_source_review_pool_v32 as pool


DEFAULT_CONFIG = pool.DEFAULT_CONFIG
REQUIRED_REVIEW_FIELDS = (
    "review_decision",
    "content_stability",
    "rewrite_suitability",
    "uncertainty_central",
    "high_stakes_or_current",
)
ALLOWED_VALUES = {
    "review_decision": {"eligible", "exclude"},
    "content_stability": {"pass", "fail"},
    "rewrite_suitability": {"pass", "fail"},
    "uncertainty_central": {"yes", "no"},
    "high_stakes_or_current": {"yes", "no"},
}


class PromotionBlocked(RuntimeError):
    def __init__(self, reason: str, details: Mapping[str, Any]):
        super().__init__(reason)
        self.details = dict(details)


def _is_eligible(review: Mapping[str, Any]) -> bool:
    return (
        review["review_decision"] == "eligible"
        and review["content_stability"] == "pass"
        and review["rewrite_suitability"] == "pass"
        and review["uncertainty_central"] == "no"
        and review["high_stakes_or_current"] == "no"
    )


def validate_and_join_reviews(
    candidates: Sequence[dict[str, Any]],
    reviews: Sequence[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    by_id: dict[str, dict[str, Any]] = {}
    duplicate_ids: list[str] = []
    for review in reviews:
        source_id = str(review.get("source_id", ""))
        if source_id in by_id:
            duplicate_ids.append(source_id)
        by_id[source_id] = review
    candidate_ids = {str(row["source_id"]) for row in candidates}
    extra = sorted(set(by_id) - candidate_ids)
    missing = sorted(candidate_ids - set(by_id))
    if duplicate_ids or extra or missing or len(reviews) != len(candidates):
        raise PromotionBlocked(
            "completed review does not match the frozen candidate pool",
            {
                "duplicate_source_ids": len(set(duplicate_ids)),
                "extra_source_ids": len(extra),
                "missing_source_ids": len(missing),
                "expected_rows": len(candidates),
                "received_rows": len(reviews),
            },
        )

    missing_fields: Counter[str] = Counter()
    invalid_fields: Counter[str] = Counter()
    integrity_failures: Counter[str] = Counter()
    joined: list[dict[str, Any]] = []
    for candidate in sorted(candidates, key=lambda row: int(row["candidate_rank"])):
        review = by_id[str(candidate["source_id"])]
        if review.get("original_response_sha256") != candidate.get("original_response_sha256"):
            integrity_failures["original_response_sha256"] += 1
        if review.get("candidate_sort_sha256") != candidate.get("candidate_sort_sha256"):
            integrity_failures["candidate_sort_sha256"] += 1
        for field in REQUIRED_REVIEW_FIELDS:
            value = str(review.get(field, "")).strip().casefold()
            if not value:
                missing_fields[field] += 1
            elif value not in ALLOWED_VALUES[field]:
                invalid_fields[field] += 1
        item = dict(candidate)
        item["source_only_review"] = {
            field: str(review.get(field, "")).strip().casefold()
            for field in REQUIRED_REVIEW_FIELDS
        }
        item["source_only_review_notes"] = str(review.get("review_notes", "")).strip()
        joined.append(item)
    if integrity_failures or missing_fields or invalid_fields:
        raise PromotionBlocked(
            "source-only review is incomplete or invalid",
            {
                "integrity_failures": dict(sorted(integrity_failures.items())),
                "missing_categorical_fields": dict(sorted(missing_fields.items())),
                "invalid_categorical_fields": dict(sorted(invalid_fields.items())),
                "allowed_values": {key: sorted(value) for key, value in ALLOWED_VALUES.items()},
            },
        )
    eligible_count = sum(_is_eligible(row["source_only_review"]) for row in joined)
    return joined, {
        "reviewed_rows": len(joined),
        "eligible_rows": eligible_count,
        "excluded_rows": len(joined) - eligible_count,
    }


def _suffix_counts(
    rows: Sequence[Mapping[str, Any]], field: str
) -> list[Counter[str]]:
    suffix: list[Counter[str]] = [Counter() for _ in range(len(rows) + 1)]
    for index in range(len(rows) - 1, -1, -1):
        suffix[index] = Counter(suffix[index + 1])
        suffix[index][str(rows[index][field])] += 1
    return suffix


def select_lexicographically_exact(
    rows: Sequence[dict[str, Any]],
    quotas: Mapping[str, Mapping[str, int]],
) -> list[dict[str, Any]]:
    """Choose the earliest feasible rows in the frozen candidate hash order."""
    ordered = sorted(rows, key=lambda row: str(row["candidate_sort_sha256"]))
    datasets = tuple(sorted(quotas["dataset_counts"]))
    tasks = tuple(sorted(quotas["task_counts"]))
    lengths = tuple(sorted(quotas["length_counts"]))
    expected = sum(int(value) for value in quotas["dataset_counts"].values())
    if sum(map(int, quotas["task_counts"].values())) != expected or sum(
        map(int, quotas["length_counts"].values())
    ) != expected:
        raise ValueError("Promotion quota margins have different totals")

    suffix_dataset = _suffix_counts(ordered, "dataset")
    suffix_task = _suffix_counts(ordered, "task")
    suffix_length = _suffix_counts(ordered, "length_bin")
    initial = (
        tuple(int(quotas["dataset_counts"][name]) for name in datasets),
        tuple(int(quotas["task_counts"][name]) for name in tasks),
        tuple(int(quotas["length_counts"][name]) for name in lengths),
    )

    @lru_cache(maxsize=None)
    def solve(
        index: int,
        remaining_datasets: tuple[int, ...],
        remaining_tasks: tuple[int, ...],
        remaining_lengths: tuple[int, ...],
    ) -> tuple[int, ...] | None:
        if any(value < 0 for value in remaining_datasets + remaining_tasks + remaining_lengths):
            return None
        remaining_total = sum(remaining_datasets)
        if remaining_total != sum(remaining_tasks) or remaining_total != sum(remaining_lengths):
            return None
        if remaining_total == 0:
            return ()
        if index == len(ordered) or len(ordered) - index < remaining_total:
            return None
        if any(
            remaining_datasets[pos] > suffix_dataset[index][name]
            for pos, name in enumerate(datasets)
        ) or any(
            remaining_tasks[pos] > suffix_task[index][name]
            for pos, name in enumerate(tasks)
        ) or any(
            remaining_lengths[pos] > suffix_length[index][name]
            for pos, name in enumerate(lengths)
        ):
            return None

        row = ordered[index]
        dataset = str(row["dataset"])
        task = str(row["task"])
        length = str(row["length_bin"])
        if dataset in datasets and task in tasks and length in lengths:
            d_pos, t_pos, l_pos = datasets.index(dataset), tasks.index(task), lengths.index(length)
            if (
                remaining_datasets[d_pos] > 0
                and remaining_tasks[t_pos] > 0
                and remaining_lengths[l_pos] > 0
            ):
                next_datasets = list(remaining_datasets)
                next_tasks = list(remaining_tasks)
                next_lengths = list(remaining_lengths)
                next_datasets[d_pos] -= 1
                next_tasks[t_pos] -= 1
                next_lengths[l_pos] -= 1
                suffix = solve(
                    index + 1,
                    tuple(next_datasets),
                    tuple(next_tasks),
                    tuple(next_lengths),
                )
                if suffix is not None:
                    return (index,) + suffix
        return solve(index + 1, remaining_datasets, remaining_tasks, remaining_lengths)

    indices = solve(0, *initial)
    if indices is None:
        details = pool.quota_gap_report(ordered, quotas)
        details["joint_quota_feasible"] = False
        raise PromotionBlocked("exact promotion quotas are infeasible", details)
    selected = [ordered[index] for index in indices]
    if len(selected) != expected:
        raise AssertionError("Promotion selector returned the wrong number of rows")
    return selected


def _counts(rows: Sequence[Mapping[str, Any]], field: str) -> dict[str, int]:
    return dict(sorted(Counter(str(row[field]) for row in rows).items()))


def _summary(
    rows: Sequence[Mapping[str, Any]], path: Path, payload: bytes
) -> dict[str, Any]:
    return {
        "count": len(rows),
        "file_name": path.name,
        "file_sha256": pool.sha256_bytes(payload),
        "source_ids_sha256": pool.source_ids_sha256(rows),
        "dataset_counts": _counts(rows, "dataset"),
        "task_counts": _counts(rows, "task"),
        "length_counts": _counts(rows, "length_bin"),
    }


def promote(config_path: Path = DEFAULT_CONFIG) -> dict[str, Any]:
    config_bytes = config_path.read_bytes()
    config = json.loads(config_bytes)
    if config.get("protocol_version") != pool.PROTOCOL_VERSION:
        raise ValueError("Wrong v3.2 source-review protocol")

    candidate_path = pool.resolve(config["private_candidate_file"])
    review_path = pool.resolve(config["completed_review_file"])
    freeze_path = pool.resolve(config["public_freeze_manifest"])
    if not candidate_path.is_file() or not freeze_path.is_file():
        raise PromotionBlocked(
            "frozen v3.2 candidate pool is missing",
            {"candidate_file_present": candidate_path.is_file(), "freeze_manifest_present": freeze_path.is_file()},
        )
    if not review_path.is_file():
        raise PromotionBlocked(
            "completed source-only review is missing",
            {"completed_review_file": review_path.name},
        )
    freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
    if freeze["candidate_review_pool"]["file_sha256"] != pool.sha256_file(candidate_path):
        raise PromotionBlocked("frozen candidate bytes changed", {})
    candidates = pool.read_jsonl(candidate_path)
    if freeze["candidate_review_pool"]["source_ids_sha256"] != pool.source_ids_sha256(candidates):
        raise PromotionBlocked("frozen candidate identities changed", {})
    reviews = pool.read_jsonl(review_path)
    reviewed, review_summary = validate_and_join_reviews(candidates, reviews)
    eligible = [row for row in reviewed if _is_eligible(row["source_only_review"])]

    targets = config["promotion_targets"]
    try:
        review64 = select_lexicographically_exact(eligible, targets["review_pool_64"])
    except PromotionBlocked as exc:
        details = dict(exc.details)
        details.update({"stage": "review_pool_64", **review_summary})
        raise PromotionBlocked(str(exc), details) from exc
    try:
        canary32 = select_lexicographically_exact(review64, targets["primary_canary_32"])
    except PromotionBlocked as exc:
        details = dict(exc.details)
        details.update({"stage": "primary_canary_32", "review_pool_64_count": len(review64)})
        raise PromotionBlocked(str(exc), details) from exc

    for row in review64:
        row["source_review_promotion"] = "review_pool_64"
    canary_ids = {str(row["source_id"]) for row in canary32}
    for row in review64:
        if str(row["source_id"]) in canary_ids:
            row["source_review_promotion"] = "primary_canary_32"
    # Rebind the canary rows so they contain the final promotion annotation.
    by_id = {str(row["source_id"]): row for row in review64}
    canary32 = [by_id[str(row["source_id"])] for row in canary32]

    review64_path = pool.resolve(config["promoted_review_pool_file"])
    canary32_path = pool.resolve(config["primary_canary_file"])
    review64_payload = pool.jsonl_bytes(review64)
    canary32_payload = pool.jsonl_bytes(canary32)
    # No writes happen before both quota-constrained selections succeed.
    pool.write_once_or_verify(review64_path, review64_payload)
    pool.write_once_or_verify(canary32_path, canary32_payload)

    public = {
        "promotion_version": pool.BUILDER_VERSION,
        "protocol_version": pool.PROTOCOL_VERSION,
        "contains_source_text": False,
        "network_calls": 0,
        "model_calls": 0,
        "rewrite_generation_performed": False,
        "source_only_review_completed": True,
        "review_summary": review_summary,
        "completed_review_file_sha256": pool.sha256_file(review_path),
        "frozen_candidate_file_sha256": pool.sha256_file(candidate_path),
        "review_pool_64": _summary(review64, review64_path, review64_payload),
        "primary_canary_32": _summary(canary32, canary32_path, canary32_payload),
        "selection_method": (
            "lexicographically earliest feasible subset in frozen candidate hash order, "
            "first 64 eligible rows and then a 32-row primary-canary subset"
        ),
        "config_sha256": pool.sha256_bytes(config_bytes),
        "promotion_source_sha256": pool.sha256_file(Path(__file__)),
    }
    public_path = pool.resolve(config["public_promotion_manifest"])
    public_payload = (
        json.dumps(public, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    pool.write_once_or_verify(public_path, public_payload)
    return public


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    args = parser.parse_args(argv)
    try:
        result = promote(args.config.resolve())
    except PromotionBlocked as exc:
        print(
            json.dumps(
                {"status": "blocked", "reason": str(exc), "details": exc.details},
                ensure_ascii=False,
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
