"""Validate actual human-review exports for the diverse-pairs experiment.

Importing this module has no side effects. The CLI requires an explicit review
export and writes only to new output files; it never edits the draft packet.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import random
import tempfile
from pathlib import Path
from typing import Any


BASE = Path(__file__).resolve().parents[1]
PRIVATE = BASE / "private_data"
DEFAULT_PAIRS = PRIVATE / "PAIRED_RESPONSES_50.jsonl"
DEFAULT_SUMMARY = BASE / "manifests" / "rewrite_review_50_summary.json"
SEED = 20261011
ENUMS = {
    "content_preserved": {"", "yes", "no", "uncertain"},
    "more_certain": {"", "A", "B", "tie", "uncertain"},
    "other_confound": {"", "yes", "no", "uncertain"},
}
REVIEW_KEYS = {
    "review_id", "source_id", "original_response_sha256", "confident_sha256",
    "hedged_sha256", "display_mapping", "content_preserved", "more_certain",
    "other_confound", "notes", "updated_at", "human_review",
}


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _expected_mappings(pairs: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    rng = random.Random(SEED)
    result = {}
    for pair in pairs:
        keys = ["confident_response", "hedged_response"]
        rng.shuffle(keys)
        result[pair["review_id"]] = {
            "review_id": pair["review_id"],
            "source_id": pair["source_id"],
            "original_response_sha256": pair["original_response_sha256"],
            "confident_sha256": _sha(pair["confident_response"]),
            "hedged_sha256": _sha(pair["hedged_response"]),
            "display_mapping": {"A": keys[0], "B": keys[1]},
        }
    return result


def _check_pairs(pairs: list[dict[str, Any]]) -> None:
    if not isinstance(pairs, list) or not pairs:
        raise ValueError("pairs must be a nonempty list")
    review_ids, source_ids = [], []
    for i, pair in enumerate(pairs):
        if not isinstance(pair, dict):
            raise ValueError(f"pair {i} must be an object")
        needed = ("review_id", "source_id", "original_response_sha256",
                  "original_response", "confident_response", "hedged_response")
        if any(not isinstance(pair.get(k), str) or not pair[k] for k in needed):
            raise ValueError(f"pair {i} is missing required identity or response fields")
        if _sha(pair["original_response"]) != pair["original_response_sha256"]:
            raise ValueError(f"original response hash mismatch for {pair['review_id']}")
        review_ids.append(pair["review_id"])
        source_ids.append(pair["source_id"])
    if len(set(review_ids)) != len(review_ids) or len(set(source_ids)) != len(source_ids):
        raise ValueError("pairs contain duplicate review_id or source_id")


def _read_annotations(entry: dict[str, Any], expected: dict[str, Any]) -> dict[str, Any]:
    extra = set(entry) - REVIEW_KEYS
    if extra:
        raise ValueError(f"unknown review fields for {entry.get('review_id')}: {sorted(extra)}")
    for key in ("review_id", "source_id", "original_response_sha256", "confident_sha256", "hedged_sha256"):
        if entry.get(key) != expected[key]:
            raise ValueError(f"{key} mismatch for review {entry.get('review_id')}")
    mapping = entry.get("display_mapping")
    if mapping != expected["display_mapping"]:
        raise ValueError(f"forged or stale A/B mapping for {entry.get('review_id')}")
    annotations = {}
    for key, allowed in ENUMS.items():
        value = entry.get(key, "")
        if value is None:
            value = ""
        if not isinstance(value, str) or value not in allowed:
            raise ValueError(f"invalid {key} value for {entry.get('review_id')}")
        annotations[key] = value
    notes = entry.get("notes", "")
    if notes is None:
        notes = ""
    if not isinstance(notes, str):
        raise ValueError(f"notes must be text for {entry.get('review_id')}")
    if entry.get("human_review", "pending") not in {"pending", "annotated"}:
        raise ValueError(f"invalid human_review marker for {entry.get('review_id')}")
    if "updated_at" in entry and not isinstance(entry["updated_at"], str):
        raise ValueError(f"updated_at must be text for {entry.get('review_id')}")
    annotations["notes"] = notes
    return annotations


def apply_reviews(pairs: list[dict[str, Any]], payload: dict[str, Any],
                  expected_packet_sha256: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Validate a packet export and derive per-pair pass/reject/pending status.

    The ``reviewer`` marker must be exactly ``user``. A generic acknowledgment
    or prose outside this explicit export is never accepted as annotation.
    """
    _check_pairs(pairs)
    if not isinstance(payload, dict):
        raise ValueError("review export must be a JSON object")
    if payload.get("packet_sha256") != expected_packet_sha256:
        raise ValueError("review packet hash is missing or stale")
    if payload.get("reviewer") != "user":
        raise ValueError("reviewer must be the explicit user export")
    if not isinstance(payload.get("exported_at"), str) or not payload["exported_at"].strip():
        raise ValueError("review export is missing exported_at")
    entries = payload.get("reviews")
    if not isinstance(entries, list):
        raise ValueError("reviews must be a list")
    expected = _expected_mappings(pairs)
    seen: set[str] = set()
    validated: dict[str, dict[str, Any]] = {}
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("review_id"), str):
            raise ValueError("each review entry needs a review_id")
        review_id = entry["review_id"]
        if review_id not in expected:
            raise ValueError(f"unknown review_id {review_id}")
        if review_id in seen:
            raise ValueError(f"duplicate review_id {review_id}")
        seen.add(review_id)
        validated[review_id] = _read_annotations(entry, expected[review_id])

    updated = copy.deepcopy(pairs)
    passed = rejected = pending = content_yes = certainty_correct = confound_yes = 0
    annotated = 0
    for pair in updated:
        rid = pair["review_id"]
        ann = validated.get(rid, {k: "" for k in (*ENUMS, "notes")})
        content, certainty, confound = (ann[k] for k in ENUMS)
        if all(v != "" for v in (content, certainty, confound)):
            annotated += 1
        certainty_field = expected[rid]["display_mapping"].get(certainty)
        certainty_is_confident = certainty_field == "confident_response"
        content_yes += content == "yes"
        certainty_correct += certainty_is_confident
        confound_yes += confound == "yes"
        wrong_certain_version = certainty in {"A", "B"} and not certainty_is_confident
        hard_failure = (content == "no" or confound == "yes" or
                        certainty == "tie" or wrong_certain_version)
        if hard_failure:
            status = "rejected"
        elif ("uncertain" in (content, certainty, confound) or
              "" in (content, certainty, confound)):
            status = "pending"
        else:
            status = "passed"
        pair["human_review"] = status
        pair["human_review_annotation"] = {
            "reviewer": "user", "content_preserved": content,
            "more_certain": certainty, "other_confound": confound,
            "notes": ann["notes"],
            "display_mapping": expected[rid]["display_mapping"],
        } if rid in validated else None
        if status == "passed":
            passed += 1
        elif status == "rejected":
            rejected += 1
        else:
            pending += 1

    n = len(updated)
    content_rate = content_yes / n
    certainty_rate = certainty_correct / n
    gate_reasons = []
    if annotated != n:
        gate_reasons.append("not_all_pairs_have_three_nonblank_annotations")
    if content_rate < 0.95:
        gate_reasons.append("content_preservation_below_95_percent")
    if certainty_rate < 0.90:
        gate_reasons.append("certainty_ordering_below_90_percent")
    aggregate = {
        "pairs": n, "annotated_count": annotated,
        "passed_count": passed, "rejected_count": rejected, "pending_count": pending,
        "content_preserved_yes_count": int(content_yes), "content_preserved_rate": content_rate,
        "certainty_correct_count": int(certainty_correct), "certainty_correct_rate": certainty_rate,
        "other_confound_yes_count": int(confound_yes),
        "proposed_expansion_gate": not gate_reasons,
        "gate_reasons": gate_reasons,
        "expansion_started": False,
    }
    return updated, aggregate


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _atomic_new(path: Path, content: str) -> None:
    path = path.resolve()
    if path.exists():
        raise FileExistsError(f"refusing to overwrite existing file: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temp_name, path)
    finally:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reviews", required=True, type=Path,
                        help="explicit JSON export downloaded from the human review packet")
    parser.add_argument("--output", required=True, type=Path,
                        help="new reviewed JSONL output path (must not already exist)")
    parser.add_argument("--pairs", type=Path, default=DEFAULT_PAIRS)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    args = parser.parse_args(argv)
    source = args.pairs.resolve()
    review_file = args.reviews.resolve()
    output = args.output.resolve()
    annotations_output = output.with_suffix(output.suffix + ".annotations.json")
    protected = {source, review_file}
    if output in protected or annotations_output in protected or annotations_output == output:
        raise ValueError("output paths must differ from source pairs and review export")
    if output.exists() or annotations_output.exists():
        raise FileExistsError("refusing to overwrite an existing reviewed output")
    pairs = _read_jsonl(source)
    payload = json.loads(review_file.read_text(encoding="utf-8"))
    summary = json.loads(args.summary.read_text(encoding="utf-8"))
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    if source_hash != summary.get("packet_sha256"):
        raise ValueError("source pair JSONL hash does not match the packet summary")
    updated, aggregate = apply_reviews(pairs, payload, summary["packet_sha256"])
    # Write the original explicit annotation payload separately from derived data.
    _atomic_new(annotations_output, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    _atomic_new(output, "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in updated))
    print(json.dumps(aggregate, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI exercised manually by user
    raise SystemExit(main())
