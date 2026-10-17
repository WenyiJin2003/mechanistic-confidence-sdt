#!/usr/bin/env python3
"""Build deterministic private review queues and text-free public manifests."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--private-output", type=Path, required=True)
    parser.add_argument("--public-output", type=Path, required=True)
    parser.add_argument("--batch-size", type=int, default=20)
    return parser.parse_args()


def stable_hash(*values: Any) -> str:
    payload = "\n\x1f\n".join(str(value).strip() for value in values)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def write_jsonl(path: Path, records: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def build_queue(
    candidates: list[dict[str, Any]], seed: int, batch_size: int
) -> list[dict[str, Any]]:
    if batch_size < 1:
        raise ValueError("batch_size must be positive")
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for candidate in candidates:
        grouped[candidate["dataset"]].append(candidate)

    queue: list[dict[str, Any]] = []
    for dataset in sorted(grouped):
        ordered = sorted(
            grouped[dataset],
            key=lambda item: (
                not item["heuristic_pass"],
                stable_hash(seed, dataset, item["source_id"]),
            ),
        )
        for index, item in enumerate(ordered, start=1):
            queued = dict(item)
            queued.update(
                {
                    "review_rank": index,
                    "review_batch": (index - 1) // batch_size + 1,
                    "model_review_decision": "pending",
                    "model_review_reason_codes": [],
                    "protected_qualifiers": [],
                    "source_repair_log": [],
                    "second_review_status": "not_applicable",
                }
            )
            queue.append(queued)
    return queue


def public_record(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "dataset": item["dataset"],
        "source_id": item["source_id"],
        "group_id": item["group_id"],
        "source_hash": item["source_hash"],
        "review_rank": item["review_rank"],
        "review_batch": item["review_batch"],
        "word_count": item["word_count"],
        "sentence_count": item["sentence_count"],
        "evidence_word_count": item["evidence_word_count"],
        "blocking_flags": item["blocking_flags"],
        "review_flags": item["review_flags"],
        "heuristic_pass": item["heuristic_pass"],
    }


def main() -> None:
    args = parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    queue = build_queue(read_jsonl(args.candidates), int(config["seed"]), args.batch_size)
    write_jsonl(args.private_output, queue)
    write_jsonl(args.public_output, (public_record(item) for item in queue))
    counts = CounterByDataset.from_records(queue)
    print(json.dumps(counts.as_dict(), indent=2, sort_keys=True))


class CounterByDataset:
    def __init__(self) -> None:
        self._counts: dict[str, int] = defaultdict(int)

    @classmethod
    def from_records(cls, records: Iterable[dict[str, Any]]) -> "CounterByDataset":
        counter = cls()
        for record in records:
            counter._counts[record["dataset"]] += 1
        return counter

    def as_dict(self) -> dict[str, int]:
        return dict(sorted(self._counts.items()))


if __name__ == "__main__":
    main()
