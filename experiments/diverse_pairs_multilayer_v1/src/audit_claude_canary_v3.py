"""Offline, privacy-preserving quality gate for v3 rewrite canaries.

This module never invokes Claude, Qwen, a tokenizer, or any other model.  It
reads the frozen private source rows and the v3 runner's parsed artifacts,
creates a private X/Y packet for blind semantic review, and writes a public
report containing aggregate numbers only.

The public report intentionally excludes source IDs, hashes, source or rewrite
text, extracted phrases/ngrams, free-text reviewer notes, and per-example
values.  The X/Y decoding key is stored separately from the reviewer packet,
under the experiment's git-ignored ``private_data`` directory.
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import math
import os
import random
import re
import statistics
import sys
import tempfile
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Mapping, Sequence

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.diverse_pairs_multilayer_v1.src import (
    run_claude_rewrite_batches_v3 as runner,
)


BASE = Path(__file__).resolve().parents[1]
PRIVATE_ROOT = (BASE / "private_data").resolve()
DEFAULT_CONFIG = BASE / "configs" / "claude_rewrite_dev_v3.json"
PUBLIC_REPORTS = BASE / "reports"
AUDIT_VERSION = 1
DEFAULT_REVIEW_SEED = 20261012

SAFE_DIMENSIONS: dict[str, set[str]] = {
    "dataset": {"allenai/WildChat-1M", "nvidia/HelpSteer2"},
    "task": {
        "comparison_analysis", "factual_explanation", "math_logic",
        "programming", "summary_judgment",
    },
    "length_bin": {"short", "medium", "long"},
    "rewrite_recipe": {"A", "B"},
    "stance_topology": {"early", "middle", "late", "distributed"},
    "rewrite_output_order": {"confident_first", "hedged_first"},
}
SAFE_STATUSES = {"accepted", "needs_review", "validation_failed", "not_applicable"}
WORD_RE = re.compile(r"\w+(?:['’]\w+)?", re.UNICODE)
TOKEN_RE = re.compile(r"\w+(?:['’]\w+)?|[^\w\s]", re.UNICODE)
HEX64_RE = re.compile(r"(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])", re.I)

SEMANTIC_VALUES: dict[str, set[str]] = {
    "content_preservation": {"pass", "fail", "uncertain"},
    "certainty_ordering": {"x_more_certain", "y_more_certain", "tie", "uncertain"},
    "speaker_scope": {"pass", "fail", "uncertain"},
    "confound": {"none", "minor", "major", "uncertain"},
    "formatting": {"pass", "mismatch", "uncertain"},
    "naturalness": {"pass", "minor", "fail", "uncertain"},
    "shortcut": {"none", "minor", "major", "uncertain"},
    "observed_topology_x": {"early", "middle", "late", "distributed", "unclear"},
    "observed_topology_y": {"early", "middle", "late", "distributed", "unclear"},
}

CUE_NGRAM_THRESHOLDS = {
    1: {"maximum_document_share": 0.50, "minimum_document_count": 3},
    2: {"maximum_document_share": 0.35, "minimum_document_count": 3},
    3: {"maximum_document_share": 0.25, "minimum_document_count": 3},
}


class QualityGateError(RuntimeError):
    """Raised for invalid or unsafe quality-gate inputs."""


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _normalize(text: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", text).casefold().split())


def _words(text: str) -> list[str]:
    return WORD_RE.findall(unicodedata.normalize("NFKC", text).casefold())


def _tokens(text: str) -> list[str]:
    return TOKEN_RE.findall(unicodedata.normalize("NFKC", text).casefold())


def _safe_name(field: str, value: Any) -> str:
    candidate = str(value)
    return candidate if candidate in SAFE_DIMENSIONS[field] else "other"


def _summary(values: Sequence[float | int]) -> dict[str, int | float | None]:
    if not values:
        return {
            "count": 0, "minimum": None, "median": None,
            "mean": None, "maximum": None,
        }
    numbers = [float(value) for value in values]
    return {
        "count": len(numbers),
        "minimum": round(min(numbers), 6),
        "median": round(statistics.median(numbers), 6),
        "mean": round(statistics.fmean(numbers), 6),
        "maximum": round(max(numbers), 6),
    }


def _is_private_path(path: Path) -> bool:
    resolved = path.resolve()
    return resolved == PRIVATE_ROOT or PRIVATE_ROOT in resolved.parents


def _atomic_json(path: Path, value: Any) -> None:
    data = (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        dir=path.parent, prefix=f".{path.name}.", delete=False
    ) as handle:
        temporary = Path(handle.name)
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def load_parsed_records(
    output_dir: Path,
    identity: Mapping[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Load only artifacts bound to the current frozen generation contract.

    Any stale, malformed, partial, unexpected, or wrong-fingerprint artifact
    makes the result unusable.  The function returns an empty record list and
    text-free failure facts rather than raising, allowing the CLI to publish a
    blocked report for failed or not-yet-started runs.
    """
    parsed_dir = output_dir / "parsed"
    paths = sorted(parsed_dir.glob("*.json")) if parsed_dir.exists() else []
    contract = identity.get("generation_contract", {})
    expected_contracts = contract.get("batches", []) if isinstance(contract, Mapping) else []
    expected_fingerprint = identity.get("generation_fingerprint")
    expected_by_id = {
        str(batch.get("batch_id")): batch
        for batch in expected_contracts
        if isinstance(batch, Mapping) and isinstance(batch.get("batch_id"), str)
    }
    manifest_path = output_dir / "run_manifest.json"
    records: list[dict[str, Any]] = []
    integrity = {
        "parsed_artifact_count": len(paths),
        "expected_batch_count": len(expected_by_id),
        "completed_expected_batch_count": 0,
        "unexpected_batch_artifact_count": 0,
        "duplicate_batch_artifact_count": 0,
        "terminal_artifact_count": 0,
        "records_hash_valid_count": 0,
        "generation_fingerprint_present": False,
        "current_generation_fingerprint_match_count": 0,
        "run_manifest_present": manifest_path.exists(),
        "run_manifest_matches_current_identity": False,
        "current_generation_contract_verified": False,
        "exact_expected_batch_set": False,
        "batch_validation_issue_count": 0,
        "artifact_readable": True,
    }
    try:
        if manifest_path.exists():
            manifest_payload = json.loads(manifest_path.read_text(encoding="utf-8"))
            integrity["run_manifest_matches_current_identity"] = manifest_payload == identity
        runner.verify_resume_artifacts(output_dir, dict(identity))
        integrity["current_generation_contract_verified"] = True
    except (OSError, TypeError, ValueError, json.JSONDecodeError):
        integrity["artifact_readable"] = False
        return [], integrity
    observed_batch_ids: list[str] = []
    for path in paths:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            del exc
            integrity["artifact_readable"] = False
            return [], integrity
        batch_records = payload.get("records")
        if not isinstance(batch_records, list) or not all(
            isinstance(row, dict) for row in batch_records
        ):
            integrity["artifact_readable"] = False
            return [], integrity
        batch_id = payload.get("batch_id")
        if not isinstance(batch_id, str) or batch_id not in expected_by_id:
            integrity["unexpected_batch_artifact_count"] += 1
            continue
        observed_batch_ids.append(batch_id)
        current_fingerprint = payload.get("generation_fingerprint")
        if not isinstance(current_fingerprint, str) or not HEX64_RE.fullmatch(
            current_fingerprint
        ):
            integrity["artifact_readable"] = False
            return [], integrity
        integrity["generation_fingerprint_present"] = True
        integrity["current_generation_fingerprint_match_count"] += int(
            current_fingerprint == expected_fingerprint
        )
        integrity["terminal_artifact_count"] += int(payload.get("terminal") is True)
        expected_hash = runner.v2.sha256_bytes(runner._canonical_json_bytes(batch_records))
        integrity["records_hash_valid_count"] += int(
            payload.get("records_sha256") == expected_hash
        )
        issues = payload.get("batch_validation_issues", [])
        integrity["batch_validation_issue_count"] += (
            len(issues) if isinstance(issues, list) else 1
        )
        records.extend(batch_records)
    observed_counts = Counter(observed_batch_ids)
    integrity["duplicate_batch_artifact_count"] = sum(
        count - 1 for count in observed_counts.values() if count > 1
    )
    integrity["completed_expected_batch_count"] = len(observed_counts)
    integrity["exact_expected_batch_set"] = (
        set(observed_counts) == set(expected_by_id)
        and integrity["duplicate_batch_artifact_count"] == 0
        and integrity["unexpected_batch_artifact_count"] == 0
    )
    integrity["all_terminal"] = (
        len(paths) > 0 and integrity["terminal_artifact_count"] == len(paths)
    )
    integrity["all_record_hashes_valid"] = (
        len(paths) > 0 and integrity["records_hash_valid_count"] == len(paths)
    )
    current_matches = integrity["current_generation_fingerprint_match_count"]
    if current_matches != len(paths):
        integrity["artifact_readable"] = False
        return [], integrity
    return records, integrity


def _record_map(
    source_rows: Sequence[dict[str, Any]], records: Sequence[dict[str, Any]]
) -> tuple[list[tuple[dict[str, Any], dict[str, Any]]], dict[str, Any]]:
    source_ids = [str(row.get("source_id", "")) for row in source_rows]
    record_ids = [str(row.get("source_id", "")) for row in records]
    sources_unique = len(source_ids) == len(set(source_ids)) and all(source_ids)
    records_unique = len(record_ids) == len(set(record_ids)) and all(record_ids)
    source_by_id = {str(row.get("source_id", "")): row for row in source_rows}
    record_by_id = {str(row.get("source_id", "")): row for row in records}
    matched: list[tuple[dict[str, Any], dict[str, Any]]] = []
    identity_mismatches = 0
    for source_id in source_ids:
        record = record_by_id.get(source_id)
        if record is None:
            continue
        source = source_by_id[source_id]
        if record.get("original_response_sha256") != source.get("original_response_sha256"):
            identity_mismatches += 1
        if any(
            record.get(field) != source.get(field)
            for field in (
                "rewrite_recipe", "stance_topology", "rewrite_output_order"
            )
        ):
            identity_mismatches += 1
        matched.append((source, record))
    integrity = {
        "source_count": len(source_rows),
        "record_count": len(records),
        "matched_count": len(matched),
        "missing_record_count": len(set(source_ids) - set(record_ids)),
        "unexpected_record_count": len(set(record_ids) - set(source_ids)),
        "duplicate_source_identity_count": len(source_ids) - len(set(source_ids)),
        "duplicate_record_identity_count": len(record_ids) - len(set(record_ids)),
        "identity_or_design_mismatch_count": identity_mismatches,
        "complete_and_aligned": bool(
            sources_unique
            and records_unique
            and len(source_rows) == len(records) == len(matched)
            and identity_mismatches == 0
        ),
    }
    return matched, integrity


def build_blind_review_packet(
    source_rows: Sequence[dict[str, Any]],
    records: Sequence[dict[str, Any]],
    *,
    phase: str,
    seed: int = DEFAULT_REVIEW_SEED,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Create a reviewer packet and a separate private decoding key.

    The reviewer packet contains the source prompt/response and candidates X/Y,
    but contains no source identity, confidence label, recipe, assigned topology,
    or generation output order.  The separate key is required to score observed
    X/Y certainty ordering after review.
    """
    matched, integrity = _record_map(source_rows, records)
    if not integrity["complete_and_aligned"]:
        raise QualityGateError("cannot_build_blind_packet_from_incomplete_records")
    rng = random.Random(seed)
    staged: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for source, record in matched:
        confident = record.get("confident_response")
        hedged = record.get("hedged_response")
        if not isinstance(confident, str) or not confident.strip():
            raise QualityGateError("cannot_review_empty_candidate")
        if not isinstance(hedged, str) or not hedged.strip():
            raise QualityGateError("cannot_review_empty_candidate")
        x_is_confident = bool(rng.getrandbits(1))
        reviewer_row = {
            "source_prompt": str(source.get("prompt", "")),
            "source_response": str(source.get("original_response", "")),
            "candidate_x": confident if x_is_confident else hedged,
            "candidate_y": hedged if x_is_confident else confident,
            **{field: None for field in SEMANTIC_VALUES},
            "reviewer_notes": "",
        }
        key_row = {
            "source_id": source["source_id"],
            "original_response_sha256": source["original_response_sha256"],
            "x_label": "confident" if x_is_confident else "hedged",
            "y_label": "hedged" if x_is_confident else "confident",
            "rewrite_recipe": source["rewrite_recipe"],
            "stance_topology": source["stance_topology"],
            "rewrite_output_order": source["rewrite_output_order"],
        }
        staged.append((reviewer_row, key_row))
    rng.shuffle(staged)
    reviews: list[dict[str, Any]] = []
    keys: list[dict[str, Any]] = []
    for review_index, (reviewer_row, key_row) in enumerate(staged, 1):
        reviews.append({"review_index": review_index, **reviewer_row})
        keys.append({"review_index": review_index, **key_row})
    packet_core = {
        "schema": "v3-blind-semantic-review",
        "version": 1,
        "phase": phase,
        "blind": True,
        "candidate_labels_hidden": True,
        "recipe_hidden": True,
        "topology_assignment_hidden": True,
        "generation_output_order_hidden": True,
        "instructions": (
            "Review content preservation and style without guessing the hidden labels. "
            "For certainty_ordering, record x_more_certain, y_more_certain, tie, or "
            "uncertain. Independently record where the confidence-bearing wording is "
            "realized in candidate X and candidate Y as early, middle, late, "
            "distributed, or unclear; the assigned topology is intentionally hidden. "
            "Put any prose only in reviewer_notes."
        ),
        "allowed_values": {
            field: sorted(values) for field, values in SEMANTIC_VALUES.items()
        },
        "reviews": reviews,
    }
    packet_id = _sha256(packet_core)
    packet = {
        "packet_id": packet_id,
        "review_metadata": {
            "packet_id": packet_id,
            "blind": True,
            "reviewer_type": None,
        },
        **packet_core,
    }
    key = {
        "schema": "v3-blind-semantic-review-key",
        "version": 1,
        "phase": phase,
        "packet_id": packet_id,
        "do_not_share_with_reviewer": True,
        "rows": keys,
    }
    return packet, key


def write_blind_review_packet(
    packet_path: Path,
    key_path: Path,
    packet: dict[str, Any],
    key: dict[str, Any],
) -> None:
    if not _is_private_path(packet_path) or not _is_private_path(key_path):
        raise QualityGateError("blind_review_artifacts_must_stay_under_private_data")
    if packet_path.resolve() == key_path.resolve():
        raise QualityGateError("blind_packet_and_key_must_be_separate")
    _atomic_json(packet_path, packet)
    _atomic_json(key_path, key)


def _sequence_distance(left: str, right: str) -> float:
    return 1.0 - difflib.SequenceMatcher(
        None, _words(left), _words(right), autojunk=False
    ).ratio()


def _edit_profile(original: str, rewritten: str) -> dict[str, Any]:
    source = _tokens(original)
    target = _tokens(rewritten)
    matcher = difflib.SequenceMatcher(None, source, target, autojunk=False)
    shape: list[tuple[str, int, int, int]] = []
    delta: list[str] = []
    boundary_only = True
    changed = 0
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        changed += max(i2 - i1, j2 - j1)
        position_bin = min(9, int(10 * i1 / max(1, len(source))))
        shape.append((tag, position_bin, i2 - i1, j2 - j1))
        delta.extend(f"-{token}" for token in source[i1:i2])
        delta.extend(f"+{token}" for token in target[j1:j2])
        if i1 not in {0, len(source)} or i2 not in {0, len(source)}:
            boundary_only = False
    insertion_only = bool(shape) and all(item[0] == "insert" for item in shape)
    return {
        "shape": tuple(shape),
        "delta": tuple(delta),
        "boundary_wrapper": insertion_only and boundary_only,
        "changed_fraction": changed / max(1, len(source)),
    }


def _ngrams(tokens: Sequence[str], size: int) -> set[tuple[str, ...]]:
    if size <= 0 or len(tokens) < size:
        return set()
    return {
        tuple(tokens[index:index + size])
        for index in range(len(tokens) - size + 1)
    }


def _cue_concentration(
    documents_by_label: Mapping[str, Mapping[int, Sequence[set[tuple[str, ...]]]]]
) -> tuple[dict[str, Any], bool]:
    """Summarize recurring novel candidate n-grams without returning their text."""
    aggregate: dict[str, Any] = {}
    blocked = False
    all_ngrams: dict[str, dict[int, set[tuple[str, ...]]]] = {
        label: {
            size: set().union(*documents_by_label[label][size])
            if documents_by_label[label][size] else set()
            for size in CUE_NGRAM_THRESHOLDS
        }
        for label in ("confident", "hedged")
    }
    for label in ("confident", "hedged"):
        other = "hedged" if label == "confident" else "confident"
        label_summary: dict[str, Any] = {}
        for size, threshold in CUE_NGRAM_THRESHOLDS.items():
            documents = list(documents_by_label[label][size])
            document_count = len(documents)
            frequencies = Counter(
                gram for document in documents for gram in document
            )
            recurrent = {gram for gram, count in frequencies.items() if count >= 2}
            maximum_frequency = max(frequencies.values(), default=0)
            maximum_share = maximum_frequency / document_count if document_count else 0.0
            exclusive_frequencies = {
                gram: count for gram, count in frequencies.items()
                if gram not in all_ngrams[other][size]
            }
            maximum_exclusive_frequency = max(exclusive_frequencies.values(), default=0)
            maximum_exclusive_share = (
                maximum_exclusive_frequency / document_count if document_count else 0.0
            )
            label_summary[f"{size}_gram"] = {
                "candidate_count": document_count,
                "unique_novel_type_count": len(frequencies),
                "recurrent_novel_type_count": len(recurrent),
                "maximum_document_frequency": maximum_frequency,
                "maximum_document_share": round(maximum_share, 6),
                "candidate_count_with_any_recurrent_ngram": sum(
                    bool(document & recurrent) for document in documents
                ),
                "maximum_label_exclusive_document_frequency": (
                    maximum_exclusive_frequency
                ),
                "maximum_label_exclusive_document_share": round(
                    maximum_exclusive_share, 6
                ),
                "gate_maximum_document_share": threshold["maximum_document_share"],
                "gate_minimum_document_count": threshold["minimum_document_count"],
            }
            if (
                maximum_frequency >= threshold["minimum_document_count"]
                and maximum_share > threshold["maximum_document_share"]
            ) or (
                maximum_exclusive_frequency >= threshold["minimum_document_count"]
                and maximum_exclusive_share > threshold["maximum_document_share"]
            ):
                blocked = True
        aggregate[label] = label_summary
    return aggregate, blocked


def _largest_cluster(items: Sequence[Sequence[str]], threshold: float = 0.85) -> tuple[int, int]:
    """Return number of near-duplicate pairs and largest connected component."""
    parents = list(range(len(items)))

    def find(index: int) -> int:
        while parents[index] != index:
            parents[index] = parents[parents[index]]
            index = parents[index]
        return index

    def union(left: int, right: int) -> None:
        left_root, right_root = find(left), find(right)
        if left_root != right_root:
            parents[right_root] = left_root

    near_pairs = 0
    for left in range(len(items)):
        if not items[left]:
            continue
        for right in range(left + 1, len(items)):
            if not items[right]:
                continue
            ratio = difflib.SequenceMatcher(
                None, list(items[left]), list(items[right]), autojunk=False
            ).ratio()
            if ratio >= threshold:
                near_pairs += 1
                union(left, right)
    sizes = Counter(find(index) for index, value in enumerate(items) if value)
    return near_pairs, max(sizes.values(), default=0)


def _duplicate_pair_count(values: Sequence[Any]) -> int:
    counts = Counter(values)
    return sum(count * (count - 1) // 2 for count in counts.values() if count > 1)


def _group_acceptance(
    matched: Sequence[tuple[dict[str, Any], dict[str, Any]]], field: str
) -> list[dict[str, int | float | str]]:
    totals: Counter[str] = Counter()
    accepted: Counter[str] = Counter()
    for source, record in matched:
        group = _safe_name(field, source.get(field))
        totals[group] += 1
        accepted[group] += int(record.get("status") == "accepted")
    return [
        {
            "group": group,
            "total": totals[group],
            "accepted": accepted[group],
            "acceptance_rate": round(accepted[group] / totals[group], 6),
        }
        for group in sorted(totals)
    ]


def _semantic_pending() -> dict[str, Any]:
    return {
        "status": "pending",
        "blind": False,
        "reviewer_type": "none",
        "reviewed_pair_count": 0,
        "semantic_review_complete": False,
        "semantic_gate_pass": False,
        "human_certified": False,
        "topology_assignment_check": {
            "candidate_match_count": 0,
            "candidate_mismatch_count": 0,
            "candidate_unclear_count": 0,
            "pair_both_match_count": 0,
            "pair_not_both_match_count": 0,
            "all_candidates_match_assignment": False,
        },
    }


def aggregate_semantic_review(
    review: Mapping[str, Any] | None,
    key: Mapping[str, Any],
) -> dict[str, Any]:
    """Validate blind ratings and return counts only; notes are never returned."""
    if review is None:
        return _semantic_pending()
    metadata = review.get("review_metadata")
    rows = review.get("reviews")
    key_rows = key.get("rows")
    if not isinstance(metadata, Mapping) or not isinstance(rows, list):
        raise QualityGateError("semantic_review_invalid")
    if not isinstance(key_rows, list):
        raise QualityGateError("semantic_review_key_invalid")
    if metadata.get("packet_id") != key.get("packet_id"):
        raise QualityGateError("semantic_review_packet_mismatch")
    reviewer_type = metadata.get("reviewer_type")
    if reviewer_type not in {"human", "agent"} or metadata.get("blind") is not True:
        raise QualityGateError("semantic_review_must_be_blind_and_typed")
    expected = {
        int(row["review_index"]): row for row in key_rows if isinstance(row, Mapping)
    }
    if len(expected) != len(key_rows):
        raise QualityGateError("semantic_review_key_invalid")
    seen: set[int] = set()
    counts: dict[str, Counter[str]] = {
        field: Counter() for field in SEMANTIC_VALUES if field != "certainty_ordering"
    }
    certainty: Counter[str] = Counter()
    topology_candidates: Counter[str] = Counter()
    topology_pairs: Counter[str] = Counter()
    for row in rows:
        if not isinstance(row, Mapping):
            raise QualityGateError("semantic_review_invalid")
        index = row.get("review_index")
        if not isinstance(index, int) or index not in expected or index in seen:
            raise QualityGateError("semantic_review_index_invalid")
        seen.add(index)
        for field, allowed in SEMANTIC_VALUES.items():
            value = row.get(field)
            if value not in allowed:
                raise QualityGateError(f"semantic_review_value_invalid:{field}")
            if field != "certainty_ordering":
                counts[field][str(value)] += 1
        observed = str(row["certainty_ordering"])
        expected_x = expected[index].get("x_label") == "confident"
        if observed == "tie":
            certainty["tie"] += 1
        elif observed == "uncertain":
            certainty["uncertain"] += 1
        elif (observed == "x_more_certain") == expected_x:
            certainty["correct"] += 1
        else:
            certainty["reversed"] += 1
        assigned_topology = expected[index].get("stance_topology")
        if assigned_topology not in SAFE_DIMENSIONS["stance_topology"]:
            raise QualityGateError("semantic_review_key_invalid")
        observed_topologies = (
            str(row["observed_topology_x"]),
            str(row["observed_topology_y"]),
        )
        pair_matches: list[bool] = []
        pair_unclear = False
        for observed_topology in observed_topologies:
            if observed_topology == "unclear":
                topology_candidates["unclear"] += 1
                pair_unclear = True
                pair_matches.append(False)
            elif observed_topology == assigned_topology:
                topology_candidates["match"] += 1
                pair_matches.append(True)
            else:
                topology_candidates["mismatch"] += 1
                pair_matches.append(False)
        if all(pair_matches):
            topology_pairs["both_match"] += 1
        elif pair_unclear:
            topology_pairs["unclear_or_partial"] += 1
        else:
            topology_pairs["mismatch_or_partial"] += 1
    complete = seen == set(expected) and len(rows) == len(expected)
    count = len(expected)
    minor_limit = max(1, math.floor(0.10 * count)) if count else 0
    safe_counts = {
        field: {value: field_counts.get(value, 0) for value in sorted(SEMANTIC_VALUES[field])}
        for field, field_counts in counts.items()
    }
    safe_counts["certainty_ordering"] = {
        value: certainty.get(value, 0)
        for value in ("correct", "reversed", "tie", "uncertain")
    }
    topology_check = {
        "candidate_match_count": topology_candidates.get("match", 0),
        "candidate_mismatch_count": topology_candidates.get("mismatch", 0),
        "candidate_unclear_count": topology_candidates.get("unclear", 0),
        "pair_both_match_count": topology_pairs.get("both_match", 0),
        "pair_not_both_match_count": (
            topology_pairs.get("unclear_or_partial", 0)
            + topology_pairs.get("mismatch_or_partial", 0)
        ),
        "all_candidates_match_assignment": bool(
            complete and topology_candidates.get("match", 0) == 2 * count
        ),
    }
    semantic_pass = bool(
        complete
        and safe_counts["content_preservation"]["pass"] == count
        and safe_counts["certainty_ordering"]["correct"] == count
        and safe_counts["speaker_scope"]["pass"] == count
        and safe_counts["confound"]["none"] == count
        and safe_counts["formatting"]["pass"] == count
        and safe_counts["naturalness"]["fail"] == 0
        and safe_counts["naturalness"]["uncertain"] == 0
        and safe_counts["naturalness"]["minor"] <= minor_limit
        and safe_counts["shortcut"]["major"] == 0
        and safe_counts["shortcut"]["uncertain"] == 0
        and safe_counts["shortcut"]["minor"] <= minor_limit
        and topology_check["all_candidates_match_assignment"]
    )
    return {
        "status": "complete" if complete else "incomplete",
        "blind": True,
        "reviewer_type": reviewer_type,
        "reviewed_pair_count": len(rows),
        "semantic_review_complete": complete,
        "counts": safe_counts,
        "minor_allowance": minor_limit,
        "topology_assignment_check": topology_check,
        "semantic_gate_pass": semantic_pass,
        "human_certified": semantic_pass and reviewer_type == "human",
    }


def build_public_report(
    source_rows: Sequence[dict[str, Any]],
    records: Sequence[dict[str, Any]],
    *,
    phase: str,
    parsed_integrity: Mapping[str, Any] | None = None,
    semantic_review: Mapping[str, Any] | None = None,
    review_key: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a text-free aggregate report and conservative decision."""
    if phase not in {"smoke", "canary"}:
        raise QualityGateError("unknown_phase")
    matched, alignment = _record_map(source_rows, records)
    parsed_safe = {
        "parsed_artifact_count": int((parsed_integrity or {}).get("parsed_artifact_count", 0)),
        "expected_batch_count": int((parsed_integrity or {}).get("expected_batch_count", 0)),
        "completed_expected_batch_count": int(
            (parsed_integrity or {}).get("completed_expected_batch_count", 0)
        ),
        "unexpected_batch_artifact_count": int(
            (parsed_integrity or {}).get("unexpected_batch_artifact_count", 0)
        ),
        "duplicate_batch_artifact_count": int(
            (parsed_integrity or {}).get("duplicate_batch_artifact_count", 0)
        ),
        "terminal_artifact_count": int((parsed_integrity or {}).get("terminal_artifact_count", 0)),
        "records_hash_valid_count": int((parsed_integrity or {}).get("records_hash_valid_count", 0)),
        "generation_fingerprint_present": bool(
            (parsed_integrity or {}).get("generation_fingerprint_present", False)
        ),
        "current_generation_fingerprint_match_count": int(
            (parsed_integrity or {}).get("current_generation_fingerprint_match_count", 0)
        ),
        "run_manifest_present": bool(
            (parsed_integrity or {}).get("run_manifest_present", False)
        ),
        "run_manifest_matches_current_identity": bool(
            (parsed_integrity or {}).get("run_manifest_matches_current_identity", False)
        ),
        "current_generation_contract_verified": bool(
            (parsed_integrity or {}).get("current_generation_contract_verified", False)
        ),
        "exact_expected_batch_set": bool(
            (parsed_integrity or {}).get("exact_expected_batch_set", False)
        ),
        "frozen_manifest_validated": bool(
            (parsed_integrity or {}).get("frozen_manifest_validated", False)
        ),
        "artifact_readable": bool(
            (parsed_integrity or {}).get("artifact_readable", False)
        ),
        "batch_validation_issue_count": int(
            (parsed_integrity or {}).get("batch_validation_issue_count", 0)
        ),
        "all_terminal": bool((parsed_integrity or {}).get("all_terminal", False)),
        "all_record_hashes_valid": bool(
            (parsed_integrity or {}).get("all_record_hashes_valid", False)
        ),
    }
    statuses = Counter(
        str(record.get("status")) if record.get("status") in SAFE_STATUSES else "other"
        for record in records
    )
    status_counts = {
        status: statuses.get(status, 0) for status in sorted(SAFE_STATUSES | {"other"})
    }
    composition = {
        field: dict(sorted(Counter(
            _safe_name(field, source.get(field)) for source in source_rows
        ).items()))
        for field in SAFE_DIMENSIONS
    }
    acceptance = {
        field: _group_acceptance(matched, field) for field in SAFE_DIMENSIONS
    }

    label_distances: dict[str, list[float]] = defaultdict(list)
    label_changed: dict[str, list[float]] = defaultdict(list)
    word_deltas: dict[str, list[int]] = defaultdict(list)
    token_deltas: dict[str, list[int]] = defaultdict(list)
    paired_word_deltas: list[int] = []
    paired_token_deltas: list[int] = []
    paired_distance_deltas: list[float] = []
    pair_word_gaps: list[int] = []
    pair_token_gaps: list[int] = []
    pair_word_ratios: list[float] = []
    pair_token_ratios: list[float] = []
    confident_longer_words = 0
    confident_longer_tokens = 0
    word_ties = 0
    token_ties = 0
    member_word_ratio_violations = 0
    member_token_ratio_violations = 0
    dynamic_gap_violations = 0
    wrapper_counts = Counter()
    shapes: dict[str, list[Any]] = defaultdict(list)
    deltas: dict[str, list[Sequence[str]]] = defaultdict(list)
    novel_ngrams: dict[str, dict[int, list[set[tuple[str, ...]]]]] = {
        label: {size: [] for size in CUE_NGRAM_THRESHOLDS}
        for label in ("confident", "hedged")
    }
    candidate_texts: list[str] = []
    pair_equal_count = 0
    order_rows: dict[str, list[dict[str, float]]] = defaultdict(list)

    for source, record in matched:
        original = str(source.get("original_response", ""))
        original_word_tokens = _words(original)
        original_words = len(original_word_tokens)
        original_tokens = len(_tokens(original))
        label_values: dict[str, dict[str, float | int]] = {}
        for label in ("confident", "hedged"):
            rewritten = record.get(f"{label}_response")
            rewritten = rewritten if isinstance(rewritten, str) else ""
            rewritten_word_tokens = _words(rewritten)
            candidate_texts.append(_normalize(rewritten))
            words = len(rewritten_word_tokens)
            tokens = len(_tokens(rewritten))
            distance = _sequence_distance(original, rewritten)
            profile = _edit_profile(original, rewritten)
            label_distances[label].append(distance)
            label_changed[label].append(float(profile["changed_fraction"]))
            word_deltas[label].append(words - original_words)
            token_deltas[label].append(tokens - original_tokens)
            member_word_ratio_violations += int(
                not 0.8 <= words / max(1, original_words) <= 1.2
            )
            member_token_ratio_violations += int(
                not 0.8 <= tokens / max(1, original_tokens) <= 1.2
            )
            wrapper_counts[label] += int(bool(profile["boundary_wrapper"]))
            shapes[label].append(profile["shape"])
            deltas[label].append(profile["delta"])
            for size in CUE_NGRAM_THRESHOLDS:
                novel_ngrams[label][size].append(
                    _ngrams(rewritten_word_tokens, size)
                    - _ngrams(original_word_tokens, size)
                )
            label_values[label] = {
                "words": words, "tokens": tokens, "distance": distance,
            }
        confident = label_values["confident"]
        hedged = label_values["hedged"]
        word_delta = int(confident["words"]) - int(hedged["words"])
        token_delta = int(confident["tokens"]) - int(hedged["tokens"])
        distance_delta = float(confident["distance"]) - float(hedged["distance"])
        paired_word_deltas.append(word_delta)
        paired_token_deltas.append(token_delta)
        paired_distance_deltas.append(distance_delta)
        confident_longer_words += int(word_delta > 0)
        confident_longer_tokens += int(token_delta > 0)
        word_ties += int(word_delta == 0)
        token_ties += int(token_delta == 0)
        pair_word_gaps.append(abs(word_delta))
        pair_token_gaps.append(abs(token_delta))
        pair_word_ratios.append(
            max(int(confident["words"]), int(hedged["words"]))
            / max(1, min(int(confident["words"]), int(hedged["words"])))
        )
        pair_token_ratios.append(
            max(int(confident["tokens"]), int(hedged["tokens"]))
            / max(1, min(int(confident["tokens"]), int(hedged["tokens"])))
        )
        mean_tokens = (int(confident["tokens"]) + int(hedged["tokens"])) / 2
        dynamic_gap_violations += int(abs(token_delta) > max(8, math.ceil(0.10 * mean_tokens)))
        pair_equal_count += int(
            _normalize(str(record.get("confident_response", "")))
            == _normalize(str(record.get("hedged_response", "")))
        )
        order = _safe_name("rewrite_output_order", source.get("rewrite_output_order"))
        order_rows[order].append({
            "accepted": float(record.get("status") == "accepted"),
            "confident_minus_hedged_word_delta": float(word_delta),
            "confident_minus_hedged_token_delta": float(token_delta),
            "confident_minus_hedged_source_distance": distance_delta,
        })

    source_distance_mean_gap = abs(
        statistics.fmean(label_distances["confident"] or [0.0])
        - statistics.fmean(label_distances["hedged"] or [0.0])
    )
    word_non_ties = len(matched) - word_ties
    token_non_ties = len(matched) - token_ties
    confident_longer_word_share = (
        confident_longer_words / word_non_ties if word_non_ties else None
    )
    confident_longer_token_share = (
        confident_longer_tokens / token_non_ties if token_non_ties else None
    )

    duplicate_shapes = {
        label: {
            "duplicate_pair_count": _duplicate_pair_count(shapes[label]),
            "largest_identical_group": max(Counter(shapes[label]).values(), default=0),
        }
        for label in ("confident", "hedged")
    }
    delta_stats: dict[str, dict[str, int]] = {}
    for label in ("confident", "hedged"):
        near_pairs, largest_cluster = _largest_cluster(deltas[label])
        delta_stats[label] = {
            "exact_duplicate_pair_count": _duplicate_pair_count(deltas[label]),
            "near_duplicate_pair_count": near_pairs,
            "largest_near_duplicate_cluster": largest_cluster,
        }
    duplicate_candidate_pairs = _duplicate_pair_count(candidate_texts)
    cue_concentration, cue_concentration_blocked = _cue_concentration(novel_ngrams)
    order_effects = {}
    for order in sorted(order_rows):
        rows = order_rows[order]
        order_effects[order] = {
            "count": len(rows),
            "acceptance_rate": round(statistics.fmean(row["accepted"] for row in rows), 6),
            "mean_confident_minus_hedged_word_delta": round(
                statistics.fmean(row["confident_minus_hedged_word_delta"] for row in rows), 6
            ),
            "mean_confident_minus_hedged_token_delta": round(
                statistics.fmean(row["confident_minus_hedged_token_delta"] for row in rows), 6
            ),
            "mean_confident_minus_hedged_source_distance": round(
                statistics.fmean(row["confident_minus_hedged_source_distance"] for row in rows), 6
            ),
        }

    if semantic_review is None:
        semantic = _semantic_pending()
    elif review_key is None:
        raise QualityGateError("semantic_review_requires_private_key")
    else:
        semantic = aggregate_semantic_review(semantic_review, review_key)

    n = len(matched)
    max_repeated_cluster = max(2, math.ceil(0.10 * n)) if n else 0
    blockers: list[str] = []
    if not alignment["complete_and_aligned"]:
        blockers.append("incomplete_or_misaligned_records")
    if not (
        parsed_safe["frozen_manifest_validated"]
        and parsed_safe["artifact_readable"]
        and parsed_safe["run_manifest_present"]
        and parsed_safe["run_manifest_matches_current_identity"]
        and parsed_safe["current_generation_contract_verified"]
        and parsed_safe["exact_expected_batch_set"]
        and parsed_safe["parsed_artifact_count"] == parsed_safe["expected_batch_count"]
        and parsed_safe["completed_expected_batch_count"] == parsed_safe["expected_batch_count"]
        and parsed_safe["all_terminal"]
        and parsed_safe["all_record_hashes_valid"]
        and parsed_safe["generation_fingerprint_present"]
        and parsed_safe["current_generation_fingerprint_match_count"]
        == parsed_safe["expected_batch_count"]
        and parsed_safe["batch_validation_issue_count"] == 0
    ):
        blockers.append("parsed_artifact_integrity")
    if statuses.get("accepted", 0) != len(source_rows):
        blockers.append("not_all_records_accepted")
    if member_word_ratio_violations or member_token_ratio_violations:
        blockers.append("member_length_ratio")
    if dynamic_gap_violations or any(value > 1.2 for value in pair_token_ratios):
        blockers.append("pair_length_balance")
    if sum(wrapper_counts.values()):
        blockers.append("boundary_wrapper")
    if pair_equal_count or duplicate_candidate_pairs:
        blockers.append("duplicate_candidate_text")
    if source_distance_mean_gap > 0.05:
        blockers.append("source_distance_label_imbalance")
    for share in (confident_longer_word_share, confident_longer_token_share):
        if share is not None and not 0.25 <= share <= 0.75:
            blockers.append("label_length_direction_imbalance")
            break
    # Edit *shape* repetition is diagnostic only: unrelated full rewrites can all
    # have the same coarse "replace one region" shape.  Scaling is blocked only
    # when the actual (privately compared) edit deltas form a repeated cluster.
    if any(
        delta_stats[label]["largest_near_duplicate_cluster"] > max_repeated_cluster
        for label in ("confident", "hedged")
    ):
        blockers.append("repeated_edit_pattern")
    if cue_concentration_blocked:
        blockers.append("recurring_cue_ngram_concentration")
    blockers = sorted(set(blockers))
    mechanical_pass = not blockers
    scale_authorized = bool(
        phase == "canary"
        and mechanical_pass
        and semantic.get("semantic_review_complete") is True
        and semantic.get("semantic_gate_pass") is True
        and semantic.get("human_certified") is True
    )
    canary_authorized = bool(
        phase == "smoke"
        and mechanical_pass
        and semantic.get("semantic_review_complete") is True
        and semantic.get("semantic_gate_pass") is True
    )

    report = {
        "audit": "claude_symmetric_diverse_rewrite_v3_quality_gate",
        "audit_version": AUDIT_VERSION,
        "privacy": {
            "contains_source_or_candidate_text": False,
            "contains_source_ids": False,
            "contains_hashes": False,
            "contains_phrases_or_ngrams": False,
            "contains_reviewer_notes": False,
            "per_example_values_published": False,
            "raw_text_location": "private_data_only",
        },
        "scope": {
            "phase": phase,
            "expected_pair_count": len(source_rows),
            "observed_record_count": len(records),
            "matched_pair_count": len(matched),
        },
        "artifact_integrity": {**alignment, **parsed_safe},
        "status_counts": status_counts,
        "source_composition": composition,
        "acceptance_by_group": acceptance,
        "source_distance_and_edit_parity": {
            "definition": "word_sequence_distance_and_aggregate_edit_fraction",
            "confident_source_distance": _summary(label_distances["confident"]),
            "hedged_source_distance": _summary(label_distances["hedged"]),
            "paired_confident_minus_hedged_source_distance": _summary(
                paired_distance_deltas
            ),
            "absolute_mean_source_distance_gap": round(source_distance_mean_gap, 6),
            "confident_changed_fraction": _summary(label_changed["confident"]),
            "hedged_changed_fraction": _summary(label_changed["hedged"]),
        },
        "length_parity": {
            "counting_method": "unicode_word_and_token_regex_no_model_call",
            "confident_minus_source_word_delta": _summary(word_deltas["confident"]),
            "hedged_minus_source_word_delta": _summary(word_deltas["hedged"]),
            "confident_minus_source_token_delta": _summary(token_deltas["confident"]),
            "hedged_minus_source_token_delta": _summary(token_deltas["hedged"]),
            "paired_confident_minus_hedged_word_delta": _summary(paired_word_deltas),
            "paired_confident_minus_hedged_token_delta": _summary(paired_token_deltas),
            "confident_longer_word_share_among_non_ties": (
                None if confident_longer_word_share is None
                else round(confident_longer_word_share, 6)
            ),
            "confident_longer_token_share_among_non_ties": (
                None if confident_longer_token_share is None
                else round(confident_longer_token_share, 6)
            ),
            "word_tie_count": word_ties,
            "token_tie_count": token_ties,
            "pair_absolute_word_gap": _summary(pair_word_gaps),
            "pair_absolute_token_gap": _summary(pair_token_gaps),
            "pair_max_min_word_ratio": _summary(pair_word_ratios),
            "pair_max_min_token_ratio": _summary(pair_token_ratios),
            "member_word_ratio_violation_count": member_word_ratio_violations,
            "member_token_ratio_violation_count": member_token_ratio_violations,
            "dynamic_pair_token_gap_violation_count": dynamic_gap_violations,
        },
        "output_order_effects": order_effects,
        "shortcut_indicators": {
            "boundary_wrapper_count_by_label": {
                label: wrapper_counts[label] for label in ("confident", "hedged")
            },
            "identical_pair_member_count": pair_equal_count,
            "duplicate_candidate_text_pair_count": duplicate_candidate_pairs,
            "edit_shape_repetition_by_label": duplicate_shapes,
            "delta_repetition_by_label": delta_stats,
            "recurring_novel_cue_ngram_concentration_by_label": cue_concentration,
            "allowed_largest_repeated_cluster": max_repeated_cluster,
        },
        "semantic_review": semantic,
        "decision": {
            "mechanical_gate_pass": mechanical_pass,
            "mechanical_blocker_categories": blockers,
            "semantic_review_required": True,
            "human_review_required_for_scale": True,
            "canary_authorized": canary_authorized,
            "scale_authorized": scale_authorized,
        },
    }
    return report


def assert_public_report_safe(
    report: Mapping[str, Any],
    source_rows: Sequence[dict[str, Any]],
    records: Sequence[dict[str, Any]],
    semantic_review: Mapping[str, Any] | None = None,
) -> None:
    """Fail closed if an aggregate report contains any private literal."""
    serialized = json.dumps(report, ensure_ascii=False, sort_keys=True)
    if HEX64_RE.search(serialized):
        raise QualityGateError("public_report_contains_hash")
    forbidden: list[str] = []
    for row in source_rows:
        forbidden.extend(str(row.get(field, "")) for field in (
            "source_id", "prompt", "original_response", "original_response_sha256"
        ))
    for row in records:
        forbidden.extend(str(row.get(field, "")) for field in (
            "source_id", "original_response_sha256", "confident_response", "hedged_response"
        ))
        writer_issues = row.get("writer_issues", [])
        if isinstance(writer_issues, list):
            forbidden.extend(str(value) for value in writer_issues)
    if semantic_review is not None:
        reviews = semantic_review.get("reviews", [])
        if isinstance(reviews, list):
            forbidden.extend(
                str(row.get("reviewer_notes", ""))
                for row in reviews if isinstance(row, Mapping)
            )
    for value in forbidden:
        if len(value.strip()) >= 8 and value in serialized:
            raise QualityGateError("public_report_contains_private_literal")


def _load_review(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise QualityGateError("semantic_review_invalid") from exc
    if not isinstance(payload, dict):
        raise QualityGateError("semantic_review_invalid")
    return payload


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--set", dest="phase", choices=("smoke", "canary"), required=True)
    parser.add_argument("--review", type=Path)
    parser.add_argument("--review-seed", type=int, default=DEFAULT_REVIEW_SEED)
    parser.add_argument("--public-output", type=Path)
    parser.add_argument("--packet-output", type=Path)
    parser.add_argument("--key-output", type=Path)
    args = parser.parse_args(argv)

    config = runner.load_config(args.config.resolve(), args.phase)
    source_rows, public_manifest = runner.validate_frozen_input(config)
    identity = runner.generation_identity(config, public_manifest, source_rows)
    records, parsed_integrity = load_parsed_records(config.output_dir, identity)
    parsed_integrity["frozen_manifest_validated"] = True
    review_dir = config.output_dir / "review"
    packet_path = (args.packet_output or review_dir / "blind_review_packet.json").resolve()
    key_path = (args.key_output or review_dir / "blind_review_key.json").resolve()
    public_path = (
        args.public_output
        or PUBLIC_REPORTS / f"claude_{args.phase}_v3_quality_gate.json"
    ).resolve()
    if _is_private_path(public_path):
        raise QualityGateError("public_report_must_not_use_private_output_path")

    # Always publish a conservative blocked/pending report first.  This makes an
    # empty, failed, partial, or stale generation auditable without requiring a
    # review packet to exist.
    report = build_public_report(
        source_rows,
        records,
        phase=args.phase,
        parsed_integrity=parsed_integrity,
    )
    assert_public_report_safe(report, source_rows, records)
    _atomic_json(public_path, report)

    packet_written = False
    matched, alignment = _record_map(source_rows, records)
    reviewable = bool(
        alignment["complete_and_aligned"]
        and matched
        and parsed_integrity.get("artifact_readable") is True
        and parsed_integrity.get("run_manifest_matches_current_identity") is True
        and parsed_integrity.get("current_generation_contract_verified") is True
        and parsed_integrity.get("exact_expected_batch_set") is True
        and parsed_integrity.get("all_terminal") is True
        and parsed_integrity.get("all_record_hashes_valid") is True
        and parsed_integrity.get("generation_fingerprint_present") is True
        and parsed_integrity.get("current_generation_fingerprint_match_count")
        == parsed_integrity.get("expected_batch_count")
        and all(
            isinstance(record.get("confident_response"), str)
            and record["confident_response"].strip()
            and isinstance(record.get("hedged_response"), str)
            and record["hedged_response"].strip()
            for _, record in matched
        )
    )
    if reviewable:
        packet, key = build_blind_review_packet(
            source_rows, records, phase=args.phase, seed=args.review_seed
        )
        review_path = args.review.resolve() if args.review else None
        review = _load_review(review_path)
        if review is not None and review_path == packet_path:
            # A reviewer may fill the packet in place.  Never erase those
            # ratings while auditing them; refresh only the separate key.
            if not _is_private_path(packet_path) or not _is_private_path(key_path):
                raise QualityGateError("blind_review_artifacts_must_stay_under_private_data")
            _atomic_json(key_path, key)
        else:
            write_blind_review_packet(packet_path, key_path, packet, key)
        packet_written = True
        if review is not None:
            report = build_public_report(
                source_rows,
                records,
                phase=args.phase,
                parsed_integrity=parsed_integrity,
                semantic_review=review,
                review_key=key,
            )
            assert_public_report_safe(report, source_rows, records, review)
            _atomic_json(public_path, report)
    print(json.dumps({
        "phase": args.phase,
        "mechanical_gate_pass": report["decision"]["mechanical_gate_pass"],
        "canary_authorized": report["decision"]["canary_authorized"],
        "scale_authorized": report["decision"]["scale_authorized"],
        "public_report": str(public_path),
        "private_review_packet": str(packet_path) if packet_written else None,
        "private_review_key": str(key_path) if packet_written else None,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
