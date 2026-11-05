#!/usr/bin/env python3
"""Build the provider-free confidence-pair scale-up split.

The script reads frozen JSONL only. It performs no model loading, tokenization,
inference, fitting, or network access.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import re
import unicodedata
from pathlib import Path
from typing import Any, Callable


SCRIPT_PATH = Path(__file__).resolve()
DATA_PREP_DIR = SCRIPT_PATH.parent
REPO_ROOT = SCRIPT_PATH.parents[3]
SEED = "confidence-probe-scaleup-20261104-v1"
TARGETS = {"train": 900, "dev": 200, "internal_test": 189}


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def normalized_question_text(text: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", text)).strip().casefold()


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def relative(path: Path) -> str:
    return str(path.resolve().relative_to(REPO_ROOT.resolve()))


def read_jsonl(path: Path) -> list[tuple[dict[str, Any], str, int]]:
    records: list[tuple[dict[str, Any], str, int]] = []
    with path.open("rb") as handle:
        for index, raw_line in enumerate(handle, start=1):
            if not raw_line.strip():
                continue
            record = json.loads(raw_line)
            if not isinstance(record, dict):
                raise ValueError(f"{path}:{index}: expected JSON object")
            records.append((record, sha256_bytes(raw_line), index))
    return records


def file_pin(path: Path, rows: int | None = None) -> dict[str, Any]:
    payload = path.read_bytes()
    result: dict[str, Any] = {"path": relative(path), "bytes": len(payload), "sha256": sha256_bytes(payload)}
    if rows is not None:
        result["rows"] = rows
    return result


def message_text(messages: Any, role: str, field: str, row_id: str) -> str:
    if not isinstance(messages, list) or len(messages) != 1:
        raise ValueError(f"{row_id}: {field} must have exactly one message")
    message = messages[0]
    if not isinstance(message, dict) or message.get("role") != role or not isinstance(message.get("content"), str):
        raise ValueError(f"{row_id}: invalid {field}")
    return message["content"]


def strict_diagnostic(diagnostic: dict[str, Any]) -> bool:
    return (
        diagnostic.get("status") == "ok"
        and diagnostic.get("length_pass") is True
        and diagnostic.get("missing_number_or_url_inventory", []) == []
    )


def load_diagnostics(path: Path) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    raw = read_jsonl(path)
    mapping: dict[str, dict[str, Any]] = {}
    for record, _, index in raw:
        row_id = record.get("id")
        if not isinstance(row_id, str) or row_id in mapping:
            raise ValueError(f"{path}:{index}: missing/duplicate id")
        mapping[row_id] = record
    return mapping, file_pin(path, len(raw))


def normalize(
    record: dict[str, Any],
    *,
    collection: str,
    atomic_group_id: str,
    source_file: Path,
    source_row: int,
    raw_hash: str,
    diagnostic: dict[str, Any] | None,
) -> dict[str, Any]:
    row_id = record.get("id")
    source_id = record.get("source_id")
    if not isinstance(row_id, str) or not isinstance(source_id, str):
        raise ValueError(f"{source_file}:{source_row}: invalid id/source_id")
    if "prompt" in record:
        question = message_text(record.get("prompt"), "user", "prompt", row_id)
        confident = message_text(record.get("chosen"), "assistant", "chosen", row_id)
        hesitant = message_text(record.get("rejected"), "assistant", "rejected", row_id)
        strict_evidence: dict[str, Any] = {"basis": "frozen_accepted_c1000_pair", "status": "accepted"}
    else:
        question = record.get("question")
        confident = record.get("confident_response")
        hesitant = record.get("hesitant_response")
        if not all(isinstance(item, str) and item for item in (question, confident, hesitant)):
            raise ValueError(f"{row_id}: missing pair text")
        if diagnostic is None:
            raise ValueError(f"{row_id}: missing diagnostic")
        strict_evidence = {
            "basis": "local_status_ok_and_length_pass",
            "status": diagnostic.get("status"),
            "length_pass": diagnostic.get("length_pass"),
            "confident_qwen_tokens": diagnostic.get("confident_qwen_tokens"),
            "hesitant_qwen_tokens": diagnostic.get("hesitant_qwen_tokens"),
            "absolute_gap": diagnostic.get("absolute_gap"),
            "observed_longer_role": diagnostic.get("observed_longer_role"),
            "missing_number_or_url_inventory": diagnostic.get("missing_number_or_url_inventory", []),
        }
    return {
        "id": row_id,
        "source_id": source_id,
        "group_id": None,
        "atomic_group_id": atomic_group_id,
        "question_sha256": sha256_text(question),
        "normalized_question_sha256": sha256_text(normalized_question_text(question)),
        "question": question,
        "confident_response": confident,
        "hesitant_response": hesitant,
        "task": record.get("task"),
        "length_bin": record.get("length_bin"),
        "target_longer_role": record.get("target_longer_role"),
        "source_dataset": record.get("dataset"),
        "source_dataset_revision": record.get("dataset_revision"),
        "source_answer_sha256": record.get("source_answer_sha256"),
        "source_locator": record.get("source_locator"),
        "license": record.get("license"),
        "source_collection": collection,
        "lane": record.get("lane"),
        "document": record.get("document"),
        "source_file": relative(source_file),
        "source_file_row_index": source_row,
        "original_record_sha256": raw_hash,
        "strict_evidence": strict_evidence,
    }


def add_file(
    output: list[dict[str, Any]],
    pins: list[dict[str, Any]],
    *,
    path: Path,
    collection: str,
    atomic_group: Callable[[dict[str, Any]], str],
    diagnostics: dict[str, dict[str, Any]] | None = None,
    strict_only: bool = False,
) -> dict[str, int]:
    raw = read_jsonl(path)
    pins.append(file_pin(path, len(raw)))
    counts = {"raw": len(raw), "included": 0, "excluded": 0}
    for record, raw_hash, source_row in raw:
        diagnostic = None if diagnostics is None else diagnostics.get(record.get("id"))
        if strict_only and (diagnostic is None or not strict_diagnostic(diagnostic)):
            counts["excluded"] += 1
            continue
        output.append(
            normalize(
                record,
                collection=collection,
                atomic_group_id=atomic_group(record),
                source_file=path,
                source_row=source_row,
                raw_hash=raw_hash,
                diagnostic=diagnostic,
            )
        )
        counts["included"] += 1
    return counts


def merge_counts(total: dict[str, int], addition: dict[str, int]) -> None:
    for key in total:
        total[key] += addition[key]


def load_internal() -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    pins: list[dict[str, Any]] = []
    denominators: dict[str, Any] = {}

    c1000 = REPO_ROOT / "experiments/qwen15b_confidence_lora_pilot_20261030"
    c1000_counts = {"raw": 0, "included": 0, "excluded": 0}
    for filename in ("train_700.jsonl", "validation_119.jsonl", "test_119.jsonl"):
        merge_counts(
            c1000_counts,
            add_file(
                rows,
                pins,
                path=c1000 / filename,
                collection="c1000_accepted",
                atomic_group=lambda record: f"c1000:lane_{int(record['lane']):02d}",
            ),
        )
    denominators["c1000_accepted"] = c1000_counts

    cf200 = REPO_ROOT / "experiments/claude_batch_document_factual_200_20261102"
    diagnostics, diagnostic_pin = load_diagnostics(cf200 / "LOCAL_DIAGNOSTICS.jsonl")
    pins.append(diagnostic_pin)
    denominators["cf200_strict"] = add_file(
        rows,
        pins,
        path=cf200 / "MERGED_ALL_ROWS.jsonl",
        collection="cf200_strict",
        atomic_group=lambda record: f"cf200:lane_{int(record['lane']):02d}:document_{int(record['document']):02d}",
        diagnostics=diagnostics,
        strict_only=True,
    )

    cf2_canary = REPO_ROOT / "experiments/claude_batch_document_factual_jsonl20_canary_20261102"
    diagnostics, diagnostic_pin = load_diagnostics(cf2_canary / "LOCAL_DIAGNOSTICS.jsonl")
    pins.append(diagnostic_pin)
    cf2_counts = add_file(
        rows,
        pins,
        path=cf2_canary / "run/MERGED_COMPLETE_ROWS.jsonl",
        collection="cf2_strict",
        atomic_group=lambda record: "cf2:canary_document_01",
        diagnostics=diagnostics,
        strict_only=True,
    )

    cf2_scale = REPO_ROOT / "experiments/claude_batch_document_factual_jsonl180_scale_20261102"
    for shard in range(1, 10):
        shard_dir = cf2_scale / f"shard_{shard:02d}"
        if shard <= 6:
            diagnostic_path = shard_dir / "LOCAL_DIAGNOSTICS.jsonl"
            row_path = shard_dir / "run/MERGED_COMPLETE_ROWS.jsonl"
        else:
            diagnostic_path = shard_dir / "LOCAL_DIAGNOSTICS_REAUTH_01.jsonl"
            row_path = shard_dir / "run_reauth_01/MERGED_COMPLETE_ROWS.jsonl"
        diagnostics, diagnostic_pin = load_diagnostics(diagnostic_path)
        pins.append(diagnostic_pin)
        merge_counts(
            cf2_counts,
            add_file(
                rows,
                pins,
                path=row_path,
                collection="cf2_strict",
                atomic_group=lambda record, shard=shard: f"cf2:scale_shard_{shard:02d}",
                diagnostics=diagnostics,
                strict_only=True,
            ),
        )
    denominators["cf2_strict"] = cf2_counts
    if len(rows) != 1289:
        raise ValueError(f"expected 1289 internal rows, observed {len(rows)}")
    return rows, pins, denominators


def load_external() -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    path = REPO_ROOT / "experiments/claude_batch_document_factual_jsonl120_wave3_20261104_v2/CF3_ALL_120.jsonl"
    raw = read_jsonl(path)
    rows: list[dict[str, Any]] = []
    excluded = 0
    for record, raw_hash, source_row in raw:
        diagnostic = record.get("local_diagnostics")
        if not isinstance(diagnostic, dict) or not strict_diagnostic(diagnostic):
            excluded += 1
            continue
        rows.append(
            normalize(
                record,
                collection="cf3_external_strict",
                atomic_group_id=f"cf3:shard_{int(diagnostic['shard']):02d}",
                source_file=path,
                source_row=source_row,
                raw_hash=raw_hash,
                diagnostic=diagnostic,
            )
        )
    if len(rows) != 113:
        raise ValueError(f"expected 113 external rows, observed {len(rows)}")
    return rows, [file_pin(path, len(raw))], {"cf3_external_strict": {"raw": len(raw), "included": len(rows), "excluded": excluded}}


class UnionFind:
    def __init__(self) -> None:
        self.parent: dict[str, str] = {}

    def add(self, item: str) -> None:
        self.parent.setdefault(item, item)

    def find(self, item: str) -> str:
        if self.parent[item] != item:
            self.parent[item] = self.find(self.parent[item])
        return self.parent[item]

    def union(self, left: str, right: str) -> None:
        left_root, right_root = self.find(left), self.find(right)
        if left_root == right_root:
            return
        if left_root < right_root:
            self.parent[right_root] = left_root
        else:
            self.parent[left_root] = right_root


def components(rows: list[dict[str, Any]], *, atomic_mode: str) -> list[dict[str, Any]]:
    uf = UnionFind()
    source_owner: dict[str, str] = {}
    question_owner: dict[str, str] = {}
    for row in rows:
        if atomic_mode == "provider_batch":
            atomic = row["atomic_group_id"]
        elif atomic_mode == "source_question":
            atomic = f"source_lineage:{row['source_id']}"
        else:
            raise ValueError(f"unsupported atomic_mode: {atomic_mode}")
        uf.add(atomic)
        for identity, owner in ((row["source_id"], source_owner), (row["question_sha256"], question_owner)):
            prior = owner.get(identity)
            if prior is None:
                owner[identity] = atomic
            else:
                uf.union(atomic, prior)
    rows_by_root: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    atomic_by_root: dict[str, set[str]] = collections.defaultdict(set)
    for row in rows:
        atomic = row["atomic_group_id"] if atomic_mode == "provider_batch" else f"source_lineage:{row['source_id']}"
        root = uf.find(atomic)
        rows_by_root[root].append(row)
        atomic_by_root[root].add(atomic)
    result: list[dict[str, Any]] = []
    for root in sorted(rows_by_root):
        member_rows = sorted(rows_by_root[root], key=lambda item: item["id"])
        group_id = "group_" + sha256_text("\n".join(row["id"] for row in member_rows))[:16]
        result.append(
            {
                "group_id": group_id,
                "rows": member_rows,
                "row_count": len(member_rows),
                "atomic_groups": sorted(atomic_by_root[root]),
                "atomic_group_count": len(atomic_by_root[root]),
            }
        )
    return sorted(result, key=lambda item: item["group_id"])


def summarize_components(groups: list[dict[str, Any]]) -> dict[str, Any]:
    ordered = sorted(groups, key=lambda item: (-item["row_count"], item["group_id"]))
    return {
        "component_count": len(groups),
        "atomic_group_count": sum(group["atomic_group_count"] for group in groups),
        "row_count": sum(group["row_count"] for group in groups),
        "largest_component_rows": ordered[0]["row_count"] if ordered else 0,
        "component_row_sizes_desc": [group["row_count"] for group in ordered],
        "components": [
            {
                "group_id": group["group_id"],
                "row_count": group["row_count"],
                "atomic_group_count": group["atomic_group_count"],
                "atomic_groups": group["atomic_groups"],
            }
            for group in ordered
        ],
    }


def compact_component_summary(groups: list[dict[str, Any]]) -> dict[str, Any]:
    summary = summarize_components(groups)
    summary.pop("components")
    sizes = summary.pop("component_row_sizes_desc")
    summary["component_size_histogram"] = {
        str(size): count for size, count in sorted(collections.Counter(sizes).items())
    }
    return summary


def value_counts(rows: list[dict[str, Any]], field: str) -> dict[str, int]:
    counter = collections.Counter("null" if row.get(field) is None else str(row.get(field)) for row in rows)
    return dict(sorted(counter.items()))


def balance_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "count": len(rows),
        "source_collection": value_counts(rows, "source_collection"),
        "task": value_counts(rows, "task"),
        "length_bin": value_counts(rows, "length_bin"),
        "target_longer_role": value_counts(rows, "target_longer_role"),
        "lane": value_counts(rows, "lane"),
        "document": value_counts(rows, "document"),
    }


def collection_overlap_matrix(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    collections_present = sorted({row["source_collection"] for row in rows})
    question_sets = {
        collection: {row["question_sha256"] for row in rows if row["source_collection"] == collection}
        for collection in collections_present
    }
    normalized_question_sets = {
        collection: {row["normalized_question_sha256"] for row in rows if row["source_collection"] == collection}
        for collection in collections_present
    }
    source_sets = {
        collection: {row["source_id"] for row in rows if row["source_collection"] == collection}
        for collection in collections_present
    }
    result: list[dict[str, Any]] = []
    for left_index, left in enumerate(collections_present):
        for right in collections_present[left_index + 1 :]:
            result.append(
                {
                    "left": left,
                    "right": right,
                    "exact_question_overlap": len(question_sets[left] & question_sets[right]),
                    "normalized_question_overlap": len(normalized_question_sets[left] & normalized_question_sets[right]),
                    "source_id_overlap": len(source_sets[left] & source_sets[right]),
                }
            )
    return result


def collection_isolated_alternative(
    rows: list[dict[str, Any]],
    *,
    dev_collection: str,
    test_collection: str,
) -> dict[str, Any]:
    assignment = {
        "train": [row for row in rows if row["source_collection"] == "c1000_accepted"],
        "dev": [row for row in rows if row["source_collection"] == dev_collection],
        "internal_test": [row for row in rows if row["source_collection"] == test_collection],
    }
    if sum(len(split_rows) for split_rows in assignment.values()) != len(rows):
        raise ValueError("collection-isolated assignment did not consume the internal pool")

    retained: dict[str, list[dict[str, Any]]] = {}
    excluded: list[dict[str, Any]] = []
    higher_questions: dict[str, str] = {}
    higher_sources: dict[str, str] = {}
    # Test has highest retention priority, followed by dev, then train. Duplicate
    # rows within one split remain; only cross-split leakage is removed.
    for split in ("internal_test", "dev", "train"):
        kept: list[dict[str, Any]] = []
        for row in assignment[split]:
            conflicts: list[dict[str, str]] = []
            normalized_question_hash = row["normalized_question_sha256"]
            if normalized_question_hash in higher_questions:
                conflicts.append({"identity": "normalized_question_sha256", "higher_priority_split": higher_questions[normalized_question_hash]})
            if row["source_id"] in higher_sources:
                conflicts.append({"identity": "source_id", "higher_priority_split": higher_sources[row["source_id"]]})
            if conflicts:
                excluded.append(
                    {
                        "id": row["id"],
                        "source_id": row["source_id"],
                        "source_collection": row["source_collection"],
                        "would_be_split": split,
                        "question_sha256": row["question_sha256"],
                        "normalized_question_sha256": normalized_question_hash,
                        "conflicts": conflicts,
                    }
                )
            else:
                kept.append(row)
        retained[split] = kept
        for row in kept:
            higher_questions[row["normalized_question_sha256"]] = split
            higher_sources[row["source_id"]] = split

    leakage = {
        "group_overlap": 0,
        "source_id_overlap": 0,
        "question_sha256_overlap": 0,
    }
    for left, right in (("train", "dev"), ("train", "internal_test"), ("dev", "internal_test")):
        left_sources = {row["source_id"] for row in retained[left]}
        right_sources = {row["source_id"] for row in retained[right]}
        left_questions = {row["normalized_question_sha256"] for row in retained[left]}
        right_questions = {row["normalized_question_sha256"] for row in retained[right]}
        leakage["source_id_overlap"] += len(left_sources & right_sources)
        leakage["question_sha256_overlap"] += len(left_questions & right_questions)

    return {
        "name": f"train_c1000__dev_{dev_collection}__test_{test_collection}",
        "priority": ["internal_test", "dev", "train"],
        "pre_dedup_counts": {split: len(split_rows) for split, split_rows in assignment.items()},
        "post_dedup": {split: balance_summary(split_rows) for split, split_rows in retained.items()},
        "excluded_count": len(excluded),
        "excluded_by_would_be_split": dict(sorted(collections.Counter(item["would_be_split"] for item in excluded).items())),
        "excluded_rows": sorted(excluded, key=lambda item: item["id"]),
        "leakage_after_dedup": leakage,
    }


def select_collection_isolated_a(
    rows: list[dict[str, Any]],
) -> tuple[dict[str, list[dict[str, Any]]], list[dict[str, Any]]]:
    initial = {
        "train": [row for row in rows if row["source_collection"] == "c1000_accepted"],
        "dev": [row for row in rows if row["source_collection"] == "cf200_strict"],
        "internal_test": [row for row in rows if row["source_collection"] == "cf2_strict"],
    }
    if {split: len(split_rows) for split, split_rows in initial.items()} != {
        "train": 938,
        "dev": 158,
        "internal_test": 193,
    }:
        raise ValueError("unexpected collection denominators before cross-split dedup")

    retained: dict[str, list[dict[str, Any]]] = {}
    audit: list[dict[str, Any]] = []
    higher_questions: dict[str, list[dict[str, str]]] = collections.defaultdict(list)
    higher_sources: dict[str, list[dict[str, str]]] = collections.defaultdict(list)
    for split in ("internal_test", "dev", "train"):
        kept: list[dict[str, Any]] = []
        for row in sorted(initial[split], key=lambda item: item["id"]):
            question_conflicts = higher_questions.get(row["normalized_question_sha256"], [])
            source_conflicts = higher_sources.get(row["source_id"], [])
            if question_conflicts or source_conflicts:
                excluded = dict(row)
                excluded["exclusion"] = {
                    "reason": "higher_priority_cross_split_identity_collision",
                    "would_be_split": split,
                    "priority": ["internal_test", "dev", "train"],
                    "normalization": "Unicode NFKC, collapse all whitespace to one ASCII space, strip, casefold",
                    "normalized_question_conflicts": question_conflicts,
                    "source_id_conflicts": source_conflicts,
                }
                audit.append(excluded)
                continue
            kept.append(row)
        retained[split] = kept
        for row in kept:
            identity = {"id": row["id"], "split": split}
            higher_questions[row["normalized_question_sha256"]].append(identity)
            higher_sources[row["source_id"]].append(identity)

    observed = {split: len(split_rows) for split, split_rows in retained.items()}
    if observed != {"train": 920, "dev": 156, "internal_test": 193}:
        raise ValueError(f"unexpected selected counts: {observed}")
    if len(audit) != 20:
        raise ValueError(f"expected 20 cross-split audit exclusions, observed {len(audit)}")
    return retained, sorted(audit, key=lambda row: row["id"])


def identity_groups(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    source_ids = [row["source_id"] for row in rows]
    if len(source_ids) != len(set(source_ids)):
        raise ValueError("source ids must be unique within a selected split")
    by_question: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for row in rows:
        by_question[row["normalized_question_sha256"]].append(row)
    groups: list[dict[str, Any]] = []
    for question_hash, member_rows in sorted(by_question.items()):
        member_rows = sorted(member_rows, key=lambda row: row["id"])
        digest_material = question_hash + "\n" + "\n".join(row["source_id"] for row in member_rows)
        group_id = "group_" + sha256_text(digest_material)[:16]
        for row in member_rows:
            row["group_id"] = group_id
        groups.append({"group_id": group_id, "rows": member_rows, "row_count": len(member_rows)})
    return groups


def feature_tokens(row: dict[str, Any]) -> tuple[str, ...]:
    def token(field: str) -> str:
        value = row.get(field)
        return f"{field}={'null' if value is None else value}"

    return (
        token("lane"),
        token("document"),
        token("task"),
        token("length_bin"),
        token("target_longer_role"),
        f"atomic_group_id={row['atomic_group_id']}",
        f"task_x_length={row.get('task')}|{row.get('length_bin')}",
        f"task_x_longer={row.get('task')}|{row.get('target_longer_role')}",
    )


def stable_rank(label: str) -> str:
    return sha256_text(f"{SEED}\n{label}")


def assign_groups_to_capacities(
    groups: list[dict[str, Any]],
    capacities: dict[str, int],
) -> dict[str, list[dict[str, Any]]]:
    total_rows = sum(group["row_count"] for group in groups)
    if sum(capacities.values()) != total_rows:
        raise ValueError("capacity sum does not match group rows")

    global_features: collections.Counter[str] = collections.Counter()
    group_features: dict[str, collections.Counter[str]] = {}
    for group in groups:
        counter: collections.Counter[str] = collections.Counter()
        for row in group["rows"]:
            counter.update(feature_tokens(row))
        group_features[group["group_id"]] = counter
        global_features.update(counter)

    assigned: dict[str, list[dict[str, Any]]] = {name: [] for name in capacities}
    assigned_rows = {name: 0 for name in capacities}
    assigned_features: dict[str, collections.Counter[str]] = {
        name: collections.Counter() for name in capacities
    }
    ordered_groups = sorted(
        groups,
        key=lambda group: (-group["row_count"], stable_rank(group["group_id"]), group["group_id"]),
    )

    for group in ordered_groups:
        size = group["row_count"]
        feature_count = group_features[group["group_id"]]
        candidates = [name for name, capacity in capacities.items() if assigned_rows[name] + size <= capacity]
        if not candidates:
            raise ValueError(f"no remaining capacity for group {group['group_id']} size {size}")

        def incremental_cost(name: str) -> tuple[float, str]:
            capacity = capacities[name]
            before_size = assigned_rows[name]
            target_fraction = capacity / total_rows
            size_scale = max(capacity, 1)
            delta = (((before_size + size - capacity) ** 2) - ((before_size - capacity) ** 2)) / size_scale
            for feature, addition in feature_count.items():
                target = global_features[feature] * target_fraction
                before = assigned_features[name][feature]
                scale = max(target, 1.0)
                delta += (((before + addition - target) ** 2) - ((before - target) ** 2)) / scale
            return delta, stable_rank(f"{group['group_id']}\n{name}")

        chosen = min(candidates, key=incremental_cost)
        assigned[chosen].append(group)
        assigned_rows[chosen] += size
        assigned_features[chosen].update(feature_count)

    if assigned_rows != capacities:
        raise ValueError(f"capacity assignment incomplete: {assigned_rows} != {capacities}")
    return assigned


def ordered_group_rows(groups: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for group in sorted(groups, key=lambda item: (stable_rank(item["group_id"]), item["group_id"])):
        rows.extend(sorted(group["rows"], key=lambda row: (stable_rank(row["id"]), row["id"])))
    return rows


def make_train_order(train_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups = identity_groups(train_rows)
    stages = assign_groups_to_capacities(
        groups,
        {"train_001_200": 200, "train_201_500": 300, "train_501_920": 420},
    )
    ordered: list[dict[str, Any]] = []
    for stage in ("train_001_200", "train_201_500", "train_501_920"):
        stage_rows = ordered_group_rows(stages[stage])
        for row in stage_rows:
            row["nested_train_stage"] = stage
        ordered.extend(stage_rows)
    if len(ordered) != 920:
        raise ValueError("train ordering did not produce 920 rows")
    for boundary in (200, 500):
        left_groups = {row["group_id"] for row in ordered[:boundary]}
        right_groups = {row["group_id"] for row in ordered[boundary:]}
        if left_groups & right_groups:
            raise ValueError(f"nested train boundary {boundary} splits an identity group")
    return ordered


def finalize_split_rows(rows: list[dict[str, Any]], split: str) -> list[dict[str, Any]]:
    finalized: list[dict[str, Any]] = []
    for index, row in enumerate(rows, start=1):
        result = dict(row)
        result["split"] = split
        result["split_row_index"] = index
        finalized.append(result)
    return finalized


def write_exclusive(path: Path, payload: bytes) -> None:
    with path.open("xb") as handle:
        handle.write(payload)


def write_jsonl_exclusive(path: Path, rows: list[dict[str, Any]]) -> None:
    payload = b"".join(canonical_json_bytes(row) for row in rows)
    write_exclusive(path, payload)


def split_leakage_checks(splits: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    internal_names = ("train", "dev", "internal_test")
    overlap_details: list[dict[str, Any]] = []
    for left_index, left in enumerate(internal_names):
        for right in internal_names[left_index + 1 :]:
            for field in ("id", "source_id", "group_id", "question_sha256", "normalized_question_sha256"):
                overlap = {row[field] for row in splits[left]} & {row[field] for row in splits[right]}
                overlap_details.append(
                    {"left": left, "right": right, "field": field, "overlap_count": len(overlap)}
                )
    external_overlaps: list[dict[str, Any]] = []
    for internal in internal_names:
        for field in ("id", "source_id", "question_sha256", "normalized_question_sha256"):
            overlap = {row[field] for row in splits[internal]} & {
                row[field] for row in splits["external_cf3"]
            }
            external_overlaps.append(
                {"left": internal, "right": "external_cf3", "field": field, "overlap_count": len(overlap)}
            )
    all_zero = all(item["overlap_count"] == 0 for item in overlap_details + external_overlaps)
    return {
        "status": "PASS" if all_zero else "FAIL",
        "internal_pairwise": overlap_details,
        "external_vs_internal": external_overlaps,
        "collection_isolation": {
            "train": value_counts(splits["train"], "source_collection"),
            "dev": value_counts(splits["dev"], "source_collection"),
            "internal_test": value_counts(splits["internal_test"], "source_collection"),
            "external_cf3": value_counts(splits["external_cf3"], "source_collection"),
        },
    }


def output_pin(path: Path, count: int) -> dict[str, Any]:
    pin = file_pin(path, count)
    return {"count": count, "path": pin["path"], "bytes": pin["bytes"], "sha256": pin["sha256"]}


def build_readme() -> str:
    return """# Confidence probe scale-up data freeze

This directory contains a provider-free, collection-isolated split of existing confidence pairs. No model, tokenizer, forward pass, probe, or classifier was run to create it.

## Frozen files

| File | Rows | Role |
|---|---:|---|
| `train_200.jsonl` | 200 | Small nested training prefix |
| `train_500.jsonl` | 500 | Medium nested training prefix |
| `train_920.jsonl` | 920 | Full training set: accepted C1000 only |
| `dev_156.jsonl` | 156 | Development set: strict CF200 only |
| `internal_test_193.jsonl` | 193 | Untouched internal test: strict CF2 only |
| `external_cf3_113.jsonl` | 113 | Separate post-exposure robustness set |
| `EXCLUDED_CROSS_SPLIT_DUPLICATES_20.jsonl` | 20 | Complete audit of lower-priority duplicate exclusions |

`train_200` is the exact first 200 rows of `train_500`, which is the exact first 500 rows of `train_920`. Identity groups never cross either prefix boundary.

## Selection and leakage control

The priority is internal test > dev > train. Questions are normalized using Unicode NFKC, collapse of all whitespace to one ASCII space, trim, then Unicode casefold. A lower-priority row is audit-excluded if its normalized question or source ID occurs in a higher-priority split. This removes 20 rows: two from CF200 and 18 from C1000. All exclusions remain unchanged in the audit JSONL.

The top-level split is fully collection-isolated. Source IDs, normalized questions, exact questions, and identity groups have zero overlap across train/dev/internal-test. The original frozen input files and every generated file are byte- and SHA-256-pinned in `SPLIT_FREEZE.json`.

## Important limitation

Both dev and internal test contain only `factual_explanation` pairs. They can evaluate factual confidence-pair transfer, but they cannot support task-wide GO claims for programming, math, comparison, or summary tasks. CF3 was previously scored and has no completed human review, so it is labeled post-exposure robustness, not untouched confirmation.
"""


def verify_materialized(
    paths: dict[str, Path],
    splits: dict[str, list[dict[str, Any]]],
    audit: list[dict[str, Any]],
) -> None:
    expected_counts = {
        "train_200": 200,
        "train_500": 500,
        "train": 920,
        "dev": 156,
        "internal_test": 193,
        "external_cf3": 113,
        "audit": 20,
    }
    for name, expected in expected_counts.items():
        observed = len(read_jsonl(paths[name]))
        if observed != expected:
            raise ValueError(f"{name}: expected {expected} rows after write, observed {observed}")
    train_payload = paths["train"].read_bytes()
    if not train_payload.startswith(paths["train_200"].read_bytes()):
        raise ValueError("train_200 is not an exact byte prefix of train_920")
    if not train_payload.startswith(paths["train_500"].read_bytes()):
        raise ValueError("train_500 is not an exact byte prefix of train_920")
    checks = split_leakage_checks(splits)
    if checks["status"] != "PASS":
        raise ValueError("post-write leakage checks failed")
    retained_ids = {row["id"] for name in ("train", "dev", "internal_test") for row in splits[name]}
    audit_ids = {row["id"] for row in audit}
    if retained_ids & audit_ids:
        raise ValueError("audit ids overlap retained ids")
    if len(retained_ids) != 1269 or len(audit_ids) != 20 or len(retained_ids | audit_ids) != 1289:
        raise ValueError("retained plus cross-split audit rows do not reconstruct the 1289 strict internal pool")
    for boundary in (200, 500):
        left = {row["group_id"] for row in splits["train"][:boundary]}
        right = {row["group_id"] for row in splits["train"][boundary:]}
        if left & right:
            raise ValueError(f"identity group crosses nested train boundary {boundary}")


def materialize(
    internal_rows: list[dict[str, Any]],
    external_rows: list[dict[str, Any]],
    internal_pins: list[dict[str, Any]],
    external_pins: list[dict[str, Any]],
    internal_denominators: dict[str, Any],
    external_denominators: dict[str, Any],
) -> dict[str, Any]:
    selected, audit = select_collection_isolated_a(internal_rows)
    train_order = make_train_order(selected["train"])
    dev_groups = identity_groups(selected["dev"])
    test_groups = identity_groups(selected["internal_test"])
    external_groups = identity_groups(external_rows)
    audit_groups = identity_groups(audit)

    splits = {
        "train": finalize_split_rows(train_order, "train"),
        "dev": finalize_split_rows(ordered_group_rows(dev_groups), "dev"),
        "internal_test": finalize_split_rows(ordered_group_rows(test_groups), "internal_test"),
        "external_cf3": finalize_split_rows(ordered_group_rows(external_groups), "external_cf3_post_exposure"),
    }
    audit_rows = finalize_split_rows(ordered_group_rows(audit_groups), "excluded_cross_split_duplicate_audit")
    leakage = split_leakage_checks(splits)
    if leakage["status"] != "PASS":
        raise ValueError("pre-write leakage checks failed")

    paths = {
        "train_200": DATA_PREP_DIR / "train_200.jsonl",
        "train_500": DATA_PREP_DIR / "train_500.jsonl",
        "train": DATA_PREP_DIR / "train_920.jsonl",
        "dev": DATA_PREP_DIR / "dev_156.jsonl",
        "internal_test": DATA_PREP_DIR / "internal_test_193.jsonl",
        "external_cf3": DATA_PREP_DIR / "external_cf3_113.jsonl",
        "audit": DATA_PREP_DIR / "EXCLUDED_CROSS_SPLIT_DUPLICATES_20.jsonl",
        "readme": DATA_PREP_DIR / "README.md",
        "manifest": DATA_PREP_DIR / "SPLIT_FREEZE.json",
        "manifest_sha": DATA_PREP_DIR / "SPLIT_FREEZE.sha256",
    }
    for path in paths.values():
        if path.exists():
            raise FileExistsError(f"refusing to overwrite existing artifact: {path}")

    write_jsonl_exclusive(paths["train_200"], splits["train"][:200])
    write_jsonl_exclusive(paths["train_500"], splits["train"][:500])
    write_jsonl_exclusive(paths["train"], splits["train"])
    write_jsonl_exclusive(paths["dev"], splits["dev"])
    write_jsonl_exclusive(paths["internal_test"], splits["internal_test"])
    write_jsonl_exclusive(paths["external_cf3"], splits["external_cf3"])
    write_jsonl_exclusive(paths["audit"], audit_rows)
    write_exclusive(paths["readme"], build_readme().encode("utf-8"))

    raw_overlap = collection_overlap_matrix(internal_rows)
    provider_components = summarize_components(components(internal_rows, atomic_mode="provider_batch"))
    provider_components.pop("components")
    manifest: dict[str, Any] = {
        "schema": "confidence-probe-scaleup-split-freeze-v1",
        "seed": SEED,
        "created_date": "2026-11-04",
        "builder": file_pin(SCRIPT_PATH),
        "normalization": {
            "name": "normalized_question_v1",
            "ordered_steps": [
                "Unicode NFKC",
                "replace every maximal Unicode-whitespace run with one ASCII space",
                "strip leading and trailing whitespace",
                "Unicode casefold",
            ],
        },
        "design": {
            "selection": "collection-isolated A",
            "priority": ["internal_test", "dev", "train"],
            "collection_assignment": {
                "train": "c1000_accepted",
                "dev": "cf200_strict",
                "internal_test": "cf2_strict",
                "external_cf3": "cf3_external_strict",
            },
            "nested_train_sizes": [200, 500, 920],
            "nested_train_selection": "fixed-seed metadata-balanced group assignment; no probe, text-model, reviewer-score, or outcome selection",
            "factual_only_dev_test": True,
            "factual_only_limitation": "Dev and internal test cannot support task-wide GO claims outside factual_explanation.",
            "external_cf3_status": "post-exposure robustness only; not untouched confirmation; human review incomplete",
            "provider_batch_atomic_attempt": {
                "status": "INFEASIBLE_FOR_THREE_WAY_SPLIT",
                "component_row_sizes_desc": provider_components["component_row_sizes_desc"],
                "largest_component_rows": provider_components["largest_component_rows"],
                "reason": "Whole C1000 lanes plus provider documents/shards, unioned by exact question/source lineage, form a 1251-row giant component.",
            },
        },
        "denominators": {
            "internal_strict_pool": internal_denominators,
            "external_strict_pool": external_denominators,
            "cross_split_dedup": {
                "pre_dedup_internal_rows": 1289,
                "retained_internal_rows": 1269,
                "audit_excluded_rows": 20,
                "excluded_by_would_be_split": {
                    "dev": sum(row["exclusion"]["would_be_split"] == "dev" for row in audit_rows),
                    "train": sum(row["exclusion"]["would_be_split"] == "train" for row in audit_rows),
                },
            },
        },
        "pre_dedup_collection_overlap": raw_overlap,
        "leakage_checks": leakage,
        "balance": {name: balance_summary(rows) for name, rows in splits.items()},
        "input_files": sorted(internal_pins + external_pins, key=lambda pin: pin["path"]),
        "splits": {
            "train_200": output_pin(paths["train_200"], 200),
            "train_500": output_pin(paths["train_500"], 500),
            "train": output_pin(paths["train"], 920),
            "dev": output_pin(paths["dev"], 156),
            "internal_test": output_pin(paths["internal_test"], 193),
            "external_cf3": output_pin(paths["external_cf3"], 113),
        },
        "nested_train_sizes": [200, 500, 920],
        "artifacts": {
            "cross_split_exclusion_audit": output_pin(paths["audit"], 20),
            "readme": file_pin(paths["readme"]),
        },
    }
    write_exclusive(paths["manifest"], canonical_json_bytes(manifest))
    manifest_hash = sha256_bytes(paths["manifest"].read_bytes())
    write_exclusive(paths["manifest_sha"], f"{manifest_hash}  SPLIT_FREEZE.json\n".encode("ascii"))

    verify_materialized(paths, splits, audit_rows)
    frozen_manifest = json.loads(paths["manifest"].read_text(encoding="utf-8"))
    if frozen_manifest != manifest:
        raise ValueError("manifest readback mismatch")
    return {
        "status": "PASS",
        "manifest": relative(paths["manifest"]),
        "manifest_sha256": manifest_hash,
        "counts": {"train": 920, "dev": 156, "internal_test": 193, "external_cf3": 113, "audit": 20},
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--analyze-only", action="store_true")
    parser.add_argument("--summary-only", action="store_true")
    parser.add_argument("--materialize", action="store_true")
    args = parser.parse_args()
    if args.analyze_only == args.materialize:
        raise SystemExit("choose exactly one of --analyze-only or --materialize")
    internal_rows, internal_pins, internal_denominators = load_internal()
    external_rows, external_pins, external_denominators = load_external()
    analysis = {
        "schema": "confidence-probe-scaleup-component-analysis-v1",
        "seed": SEED,
        "targets": TARGETS,
        "internal_denominators": internal_denominators,
        "external_denominators": external_denominators,
        "internal_provider_batch_components": summarize_components(components(internal_rows, atomic_mode="provider_batch")),
        "internal_source_question_components": compact_component_summary(components(internal_rows, atomic_mode="source_question")),
        "external_provider_batch_components": summarize_components(components(external_rows, atomic_mode="provider_batch")),
        "external_source_question_components": compact_component_summary(components(external_rows, atomic_mode="source_question")),
        "collection_exact_identity_overlap": collection_overlap_matrix(internal_rows),
        "collection_isolated_alternatives": [
            collection_isolated_alternative(
                internal_rows,
                dev_collection="cf200_strict",
                test_collection="cf2_strict",
            ),
            collection_isolated_alternative(
                internal_rows,
                dev_collection="cf2_strict",
                test_collection="cf200_strict",
            ),
        ],
        "input_file_count": len(internal_pins) + len(external_pins),
    }
    if args.analyze_only:
        if args.summary_only:
            for alternative in analysis["collection_isolated_alternatives"]:
                alternative.pop("excluded_rows", None)
            analysis["internal_provider_batch_components"].pop("components", None)
            analysis["external_provider_batch_components"].pop("components", None)
        print(json.dumps(analysis, ensure_ascii=False, indent=2, sort_keys=True))
        return
    result = materialize(
        internal_rows,
        external_rows,
        internal_pins,
        external_pins,
        internal_denominators,
        external_denominators,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
