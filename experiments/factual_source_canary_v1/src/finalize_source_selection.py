#!/usr/bin/env python3
"""Validate source reviews and freeze accepted core sources plus backups."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
PRIVATE_FIELDS = {
    "question",
    "original_response",
    "evidence",
    "source_locator",
    "metadata",
    "notes",
    "protected_qualifiers",
    "source_repair_log",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--queue", type=Path, required=True)
    parser.add_argument("--reviews", type=Path, nargs="+", required=True)
    parser.add_argument("--secondary-reviews", type=Path, nargs="*", default=[])
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--private-output", type=Path, required=True)
    parser.add_argument("--public-output", type=Path, required=True)
    parser.add_argument("--summary-output", type=Path, required=True)
    parser.add_argument("--allow-incomplete", action="store_true")
    return parser.parse_args()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def write_jsonl(path: Path, records: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def audit_order_key(prefix: str, source_id: str) -> str:
    return hashlib.sha256(f"{prefix}{source_id}".encode("utf-8")).hexdigest()


def index_unique(records: Iterable[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for record in records:
        value = str(record[key])
        if value in indexed:
            raise ValueError(f"duplicate {key}: {value}")
        indexed[value] = record
    return indexed


def validate_review(review: dict[str, Any], source: dict[str, Any]) -> None:
    if review["dataset"] != source["dataset"]:
        raise ValueError(f"dataset mismatch for {review['source_id']}")
    if int(review["review_rank"]) != int(source["review_rank"]):
        raise ValueError(f"review-rank mismatch for {review['source_id']}")
    if review["decision"] not in {"accept", "requires_source_repair", "reject"}:
        raise ValueError(f"invalid decision for {review['source_id']}: {review['decision']}")
    if review["decision"] == "accept":
        for field in ("evidence_support", "self_contained", "rewrite_suitable"):
            if review.get(field) is not True:
                raise ValueError(f"accepted record fails {field}: {review['source_id']}")


def public_record(record: dict[str, Any]) -> dict[str, Any]:
    public = {
        "dataset": record["dataset"],
        "source_id": record["source_id"],
        "group_id": record["group_id"],
        "source_hash": record["source_hash"],
        "review_rank": record["review_rank"],
        "review_batch": record["review_batch"],
        "selection_role": record["selection_role"],
        "word_count": record["word_count"],
        "sentence_count": record["sentence_count"],
        "evidence_word_count": record["evidence_word_count"],
        "model_review_decision": record["model_review_decision"],
        "model_review_reason_codes": record["model_review_reason_codes"],
        "secondary_audit_status": record.get("secondary_audit_status", "not_sampled"),
    }
    if PRIVATE_FIELDS.intersection(public):
        raise AssertionError("private field leaked into public selection record")
    return public


def finalize(
    queue: list[dict[str, Any]],
    reviews: list[dict[str, Any]],
    plan: dict[str, Any],
    allow_incomplete: bool,
    secondary_reviews: list[dict[str, Any]] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    secondary_reviews = secondary_reviews or []
    queue_by_id = index_unique(queue, "source_id")
    reviews_by_id = index_unique(reviews, "source_id")
    for source_id, review in reviews_by_id.items():
        if source_id not in queue_by_id:
            raise ValueError(f"reviewed source missing from queue: {source_id}")
        validate_review(review, queue_by_id[source_id])

    secondary_by_id = index_unique(secondary_reviews, "source_id")
    valid_secondary_decisions = {
        "confirm_accept",
        "downgrade_repair",
        "downgrade_reject",
    }
    for source_id, secondary in secondary_by_id.items():
        primary = reviews_by_id.get(source_id)
        if primary is None:
            raise ValueError(f"secondary source missing from primary reviews: {source_id}")
        if primary["decision"] != "accept":
            raise ValueError(f"secondary audit targets non-accept: {source_id}")
        if secondary.get("primary_decision") != "accept":
            raise ValueError(f"secondary primary-decision mismatch: {source_id}")
        if secondary.get("secondary_decision") not in valid_secondary_decisions:
            raise ValueError(f"invalid secondary decision: {source_id}")

    quotas = plan["core"]["quota_by_dataset"]
    backup_target = int(plan["core"]["backup_target_by_dataset"])
    selected: list[dict[str, Any]] = []
    by_dataset: dict[str, Any] = {}
    complete = True
    for dataset, quota_value in quotas.items():
        quota = int(quota_value)
        dataset_reviews = [
            review for review in reviews if review["dataset"] == dataset
        ]
        primary_accepts = [
            review for review in dataset_reviews if review["decision"] == "accept"
        ]
        accepts = sorted(
            (
                review
                for review in primary_accepts
                if secondary_by_id.get(review["source_id"], {}).get(
                    "secondary_decision", "confirm_accept"
                )
                == "confirm_accept"
            ),
            key=lambda review: int(review["review_rank"]),
        )
        secondary_config = plan.get("secondary_audit")
        final_secondary_sample: list[dict[str, Any]] = []
        if secondary_config:
            sample_size = int(secondary_config["sample_size_per_dataset"])
            hash_prefix = str(secondary_config["hash_prefix"])
            expected_sample = sorted(
                accepts,
                key=lambda review: audit_order_key(
                    hash_prefix, review["source_id"]
                ),
            )[:sample_size]
            final_secondary_sample = [
                secondary
                for secondary in secondary_reviews
                if queue_by_id[secondary["source_id"]]["dataset"] == dataset
                and secondary.get("in_final_sample") is True
            ]
            actual_ids = {
                secondary["source_id"] for secondary in final_secondary_sample
            }
            expected_ids = {review["source_id"] for review in expected_sample}
            if actual_ids != expected_ids:
                raise ValueError(
                    f"{dataset} secondary sample does not match the locked effective-accept sample"
                )
            if secondary_config.get("require_final_sample_confirmation") and any(
                secondary["secondary_decision"] != "confirm_accept"
                for secondary in final_secondary_sample
            ):
                raise ValueError(
                    f"{dataset} final secondary sample contains a downgrade"
                )
        required = quota + backup_target
        dataset_complete = len(accepts) >= required
        complete = complete and dataset_complete
        if not dataset_complete and not allow_incomplete:
            raise ValueError(
                f"{dataset} has {len(accepts)} accepts; {required} are required"
            )
        chosen = accepts[:required]
        for index, review in enumerate(chosen):
            source = dict(queue_by_id[review["source_id"]])
            source.update(
                {
                    "selection_role": "core" if index < quota else "backup",
                    "model_review_decision": review["decision"],
                    "model_review_reason_codes": review["reason_codes"],
                    "protected_qualifiers": review.get("protected_qualifiers", []),
                    "model_review_notes": review.get("notes", ""),
                    "model_reviewer": review.get("reviewer", ""),
                    "secondary_audit_status": secondary_by_id.get(
                        review["source_id"], {}
                    ).get("secondary_decision", "not_sampled"),
                }
            )
            selected.append(source)
        decision_counts = Counter(review["decision"] for review in dataset_reviews)
        dataset_secondary = [
            review
            for review in secondary_reviews
            if queue_by_id[review["source_id"]]["dataset"] == dataset
        ]
        secondary_counts = Counter(
            review["secondary_decision"] for review in dataset_secondary
        )
        by_dataset[dataset] = {
            "reviewed_count": len(dataset_reviews),
            "decision_counts": dict(sorted(decision_counts.items())),
            "accepted_count": len(accepts),
            "primary_accept_count": len(primary_accepts),
            "secondary_audit_counts": dict(sorted(secondary_counts.items())),
            "final_secondary_sample_count": len(final_secondary_sample),
            "core_selected_count": min(len(accepts), quota),
            "backup_selected_count": min(max(len(accepts) - quota, 0), backup_target),
            "required_accept_count": required,
            "gate_complete": dataset_complete,
            "highest_reviewed_rank": max(
                (int(review["review_rank"]) for review in dataset_reviews), default=0
            ),
        }
    role_order = {"core": 0, "backup": 1}
    selected.sort(
        key=lambda item: (
            item["dataset"],
            role_order[item["selection_role"]],
            item["review_rank"],
        )
    )
    return selected, {"gate_complete": complete, "by_dataset": by_dataset}


def main() -> None:
    args = parse_args()
    queue = read_jsonl(args.queue)
    reviews: list[dict[str, Any]] = []
    for review_path in args.reviews:
        reviews.extend(read_jsonl(review_path))
    secondary_reviews: list[dict[str, Any]] = []
    for review_path in args.secondary_reviews:
        secondary_reviews.extend(read_jsonl(review_path))
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    selected, summary = finalize(
        queue,
        reviews,
        plan,
        args.allow_incomplete,
        secondary_reviews=secondary_reviews,
    )
    summary.update(
        {
            "version": "factual-source-core-selection-v1",
            "selection_policy": "first accepted records in locked deterministic review order",
            "reviewer_type": "model_assisted_primary_not_independent_human_review",
            "queue_sha256": file_sha256(args.queue),
            "review_file_sha256": {
                path.name: file_sha256(path) for path in args.reviews
            },
            "secondary_review_file_sha256": {
                path.name: file_sha256(path) for path in args.secondary_reviews
            },
        }
    )
    write_jsonl(args.private_output, selected)
    write_jsonl(args.public_output, (public_record(record) for record in selected))
    args.summary_output.parent.mkdir(parents=True, exist_ok=True)
    args.summary_output.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
