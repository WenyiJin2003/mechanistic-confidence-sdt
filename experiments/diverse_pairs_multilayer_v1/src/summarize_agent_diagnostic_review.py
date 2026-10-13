"""Validate and aggregate a label-blind agent diagnostic review.

The input contains per-example review IDs and issue categories, so it must stay
under ``private_data``.  The returned/public artifact contains only aggregate
counts and cryptographic bindings to the exact blind packet and NLI report.

This diagnostic is deliberately distinct from the human-review gate.  An agent
review can reveal construction problems, but it cannot certify the pairs as
training data.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any


BASE = Path(__file__).resolve().parents[1]
PRIVATE = BASE / "private_data"

DECISIONS = {"accept", "discuss", "reject"}
STRATA = {"nli_flagged", "nli_unflagged_sample"}
CONTENT_VALUES = {"preserved", "not_preserved", "uncertain"}
CONTRAST_VALUES = {"clear", "not_clear", "uncertain"}
NATURALNESS_VALUES = {"clearly_natural", "not_clearly_natural", "uncertain"}
SCOPE_VALUES = {"global", "ambiguous", "local_only", "uncertain"}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
    ).hexdigest()


def _is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _load_object(path: Path, name: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Cannot read valid {name} JSON: {path}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"{name} must be a JSON object")
    return payload


def _require_private(path: Path, base: Path) -> Path:
    resolved = path.resolve()
    private = (base / "private_data").resolve()
    try:
        resolved.relative_to(private)
    except ValueError as exc:
        raise ValueError("Per-example diagnostic review must stay under private_data") from exc
    return resolved


def _load_packet(packet_dir: Path) -> tuple[str, dict[str, str]]:
    manifest_path = packet_dir / "MANIFEST.json"
    rows_path = packet_dir / "BLINDED_ROWS.jsonl"
    key_path = packet_dir / "UNBLIND_KEY.json"
    manifest = _load_object(manifest_path, "packet manifest")
    key = _load_object(key_path, "unblind key")
    packet_hash = manifest.get("packet_sha256")
    if not _is_sha256(packet_hash):
        raise ValueError("Packet manifest has an invalid packet_sha256")
    if sha256_file(rows_path) != packet_hash:
        raise ValueError("Blind packet rows do not match packet_sha256")
    key_file_hash = manifest.get("unblind_key_sha256")
    if not _is_sha256(key_file_hash) or sha256_file(key_path) != key_file_hash:
        raise ValueError("UNBLIND_KEY does not match the packet manifest")
    rows_by_id: dict[str, dict[str, Any]] = {}
    for line_number, line in enumerate(rows_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid blinded-row JSON at line {line_number}") from exc
        review_id = row.get("review_id") if isinstance(row, dict) else None
        if not isinstance(review_id, str) or not review_id:
            raise ValueError(f"Invalid review_id in blinded-row line {line_number}")
        if review_id in rows_by_id:
            raise ValueError(f"Duplicate review_id in blind packet: {review_id}")
        for field in ("source_response", "version_a", "version_b"):
            if not isinstance(row.get(field), str):
                raise ValueError(f"Blind packet row {review_id} is missing {field}")
        rows_by_id[review_id] = row
    if manifest.get("pairs") != len(rows_by_id):
        raise ValueError("Blind packet manifest and row count disagree")

    if key.get("packet_sha256") != packet_hash or not isinstance(key.get("pairs"), list):
        raise ValueError("UNBLIND_KEY is stale or malformed")
    review_to_source: dict[str, str] = {}
    seen_sources: set[str] = set()
    for entry in key["pairs"]:
        if not isinstance(entry, dict):
            raise ValueError("UNBLIND_KEY entries must be objects")
        review_id = entry.get("review_id")
        source_id = entry.get("source_id")
        if review_id not in rows_by_id or not isinstance(source_id, str) or not source_id:
            raise ValueError("UNBLIND_KEY review/source identity is invalid")
        if review_id in review_to_source or source_id in seen_sources:
            raise ValueError("UNBLIND_KEY review and source identities must be unique")
        row = rows_by_id[review_id]
        expected_hashes = {
            "source_response_sha256": hashlib.sha256(
                row["source_response"].encode("utf-8")
            ).hexdigest(),
            "version_a_sha256": hashlib.sha256(
                row["version_a"].encode("utf-8")
            ).hexdigest(),
            "version_b_sha256": hashlib.sha256(
                row["version_b"].encode("utf-8")
            ).hexdigest(),
        }
        if any(entry.get(field) != value for field, value in expected_hashes.items()):
            raise ValueError(f"UNBLIND_KEY text hash is stale for {review_id}")
        review_to_source[review_id] = source_id
        seen_sources.add(source_id)
    if set(review_to_source) != set(rows_by_id):
        raise ValueError("UNBLIND_KEY identities do not match the blind packet")
    return packet_hash, review_to_source


def _load_private_nli_membership(
    private_nli_path: Path,
    public_nli: dict[str, Any],
    expected_source_ids: set[str],
    *,
    base: Path,
) -> tuple[dict[str, bool], str]:
    private_nli_path = _require_private(private_nli_path, base)
    private_nli = _load_object(private_nli_path, "private NLI triage")
    required = {
        "schema": "local-nli-semantic-triage-private-v1",
        "status": "complete",
        "semantic_certification": False,
    }
    for field, expected in required.items():
        if private_nli.get(field) != expected:
            raise ValueError(f"Private NLI triage requires {field}={expected!r}")
    if private_nli.get("protocol_version") != public_nli.get("protocol_version"):
        raise ValueError("Private and public NLI protocol versions disagree")
    if private_nli.get("public_report_sha256") != canonical_sha256(public_nli):
        raise ValueError("Private NLI public_report_sha256 is stale or mismatched")
    if private_nli.get("bindings") != public_nli.get("bindings"):
        raise ValueError("Private and public NLI bindings disagree")
    if private_nli.get("aggregate") != public_nli.get("counts"):
        raise ValueError("Private and public NLI aggregate counts disagree")

    records = private_nli.get("records")
    if not isinstance(records, list):
        raise ValueError("Private NLI triage records must be a list")
    membership: dict[str, bool] = {}
    for record in records:
        source_id = record.get("source_id") if isinstance(record, dict) else None
        flagged = record.get("triage_flagged") if isinstance(record, dict) else None
        if not isinstance(source_id, str) or not source_id or not isinstance(flagged, bool):
            raise ValueError("Private NLI triage contains an invalid source record")
        if source_id in membership:
            raise ValueError("Private NLI triage contains duplicate source IDs")
        membership[source_id] = flagged
    if set(membership) != expected_source_ids:
        raise ValueError("Private NLI source identities do not match the blind packet")
    counts = public_nli.get("counts", {})
    if sum(membership.values()) != counts.get("flagged_pair_count"):
        raise ValueError("Private NLI flagged membership disagrees with public counts")
    if len(membership) - sum(membership.values()) != counts.get(
        "not_flagged_pair_count"
    ):
        raise ValueError("Private NLI unflagged membership disagrees with public counts")
    return membership, sha256_file(private_nli_path)


def _validate_issue_categories(value: Any, review_id: str) -> None:
    if not isinstance(value, list) or any(
        not isinstance(item, str) or not item or item.lower() != item or " " in item
        for item in value
    ):
        raise ValueError(f"Invalid issue_categories for {review_id}")


def build_public_summary(
    private_review_path: Path,
    packet_dir: Path,
    nli_report_path: Path,
    private_nli_path: Path,
    *,
    base: Path = BASE,
) -> dict[str, Any]:
    """Validate a private diagnostic and return a text-free public summary."""
    private_review_path = _require_private(private_review_path, base)
    review = _load_object(private_review_path, "private diagnostic review")
    packet_hash, review_to_source = _load_packet(packet_dir)
    nli_report = _load_object(nli_report_path, "NLI report")
    nli_report_hash = sha256_file(nli_report_path)
    nli_membership, private_nli_hash = _load_private_nli_membership(
        private_nli_path,
        nli_report,
        set(review_to_source.values()),
        base=base,
    )

    required_metadata = {
        "schema": "agent-blind-diagnostic-private-v2",
        "reviewer_type": "agent",
        "human_certified": False,
        "blinded": True,
        "semantic_certification": False,
        "certainty_direction_relative_to_intended_labels": "not_captured_or_verified",
    }
    for field, expected in required_metadata.items():
        if review.get(field) != expected:
            raise ValueError(f"Private diagnostic requires {field}={expected!r}")
    if review.get("packet_sha256") != packet_hash:
        raise ValueError("Private diagnostic packet hash is stale or mismatched")
    if review.get("nli_report_sha256") != nli_report_hash:
        raise ValueError("Private diagnostic NLI report hash is stale or mismatched")
    if review.get("private_nli_triage_sha256") != private_nli_hash:
        raise ValueError("Private diagnostic detailed NLI hash is stale or mismatched")
    key_hash = sha256_file(packet_dir / "UNBLIND_KEY.json")
    if review.get("unblind_key_sha256") != key_hash:
        raise ValueError("Private diagnostic unblind-key hash is stale or mismatched")
    if nli_report.get("status") != "complete":
        raise ValueError("NLI report is not complete")

    records = review.get("reviews")
    if not isinstance(records, list) or not records:
        raise ValueError("Private diagnostic reviews must be a nonempty list")
    seen: set[str] = set()
    counts = {
        "decision": Counter(),
        "content_preservation": Counter(),
        "certainty_contrast": Counter(),
        "naturalness": Counter(),
        "cue_scope": Counter(),
    }
    by_stratum: dict[str, Counter[str]] = {
        stratum: Counter() for stratum in sorted(STRATA)
    }
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("Every private diagnostic review must be an object")
        review_id = record.get("review_id")
        if not isinstance(review_id, str) or not review_id:
            raise ValueError("Every private diagnostic review needs a review_id")
        if review_id in seen:
            raise ValueError(f"Duplicate private diagnostic review_id: {review_id}")
        if review_id not in review_to_source:
            raise ValueError(f"Private diagnostic review_id is not in packet: {review_id}")
        seen.add(review_id)

        checks = {
            "decision": DECISIONS,
            "stratum": STRATA,
            "content_preservation": CONTENT_VALUES,
            "certainty_contrast": CONTRAST_VALUES,
            "naturalness": NATURALNESS_VALUES,
            "cue_scope": SCOPE_VALUES,
        }
        for field, allowed in checks.items():
            if record.get(field) not in allowed:
                raise ValueError(f"Invalid {field} for {review_id}")
        _validate_issue_categories(record.get("issue_categories"), review_id)
        if "comment" in record or "source_id" in record:
            raise ValueError("Use issue categories only; comments and source IDs are forbidden")

        for field in counts:
            counts[field][record[field]] += 1
        by_stratum[record["stratum"]][record["decision"]] += 1
        expected_stratum = (
            "nli_flagged"
            if nli_membership[review_to_source[review_id]]
            else "nli_unflagged_sample"
        )
        if record["stratum"] != expected_stratum:
            raise ValueError(
                f"Declared NLI stratum disagrees with detailed triage for {review_id}"
            )

    design = review.get("sampling_design")
    if not isinstance(design, dict):
        raise ValueError("Private diagnostic requires sampling_design")
    expected_by_stratum = design.get("expected_reviewed_by_stratum")
    if not isinstance(expected_by_stratum, dict) or set(expected_by_stratum) != STRATA:
        raise ValueError("sampling_design must specify both review strata")
    if design.get("nli_unflagged_selection") != (
        "task- and dataset-balanced diagnostic sample"
    ):
        raise ValueError(
            "sampling_design must describe the task- and dataset-balanced sample"
        )
    observed_by_stratum = Counter(record["stratum"] for record in records)
    if dict(observed_by_stratum) != expected_by_stratum:
        raise ValueError("Observed review strata do not match sampling_design")
    nli_counts = nli_report.get("counts", {})
    if expected_by_stratum["nli_flagged"] != nli_counts.get("flagged_pair_count"):
        raise ValueError("Diagnostic must include every NLI-flagged pair")
    if expected_by_stratum["nli_unflagged_sample"] > nli_counts.get(
        "not_flagged_pair_count", -1
    ):
        raise ValueError("Unflagged diagnostic sample exceeds the available stratum")
    all_flagged_review_ids = {
        review_id
        for review_id, source_id in review_to_source.items()
        if nli_membership[source_id]
    }
    reviewed_flagged_ids = {
        record["review_id"]
        for record in records
        if record["stratum"] == "nli_flagged"
    }
    if reviewed_flagged_ids != all_flagged_review_ids:
        raise ValueError("Diagnostic must review the exact complete NLI-flagged set")

    total = len(records)
    public = {
        "schema": "agent-blind-diagnostic-public-v2",
        "status": "complete",
        "purpose": "label_blind_model_assisted_construction_diagnostic",
        "reviewer_type": "agent",
        "human_certified": False,
        "blinded": True,
        "semantic_certification": False,
        "certainty_direction_relative_to_intended_labels": (
            "not_captured_or_verified"
        ),
        "training_data_validated": False,
        "authorizes_probe_scoring": False,
        "authorizes_sdt_training": False,
        "bindings": {
            "packet_sha256": packet_hash,
            "packet_manifest_sha256": sha256_file(packet_dir / "MANIFEST.json"),
            "unblind_key_sha256": key_hash,
            "nli_report_sha256": nli_report_hash,
            "private_nli_triage_sha256": private_nli_hash,
            "private_diagnostic_sha256": sha256_file(private_review_path),
        },
        "sampling_design": {
            "packet_pair_count": len(review_to_source),
            "reviewed_pair_count": total,
            "nli_flagged": {
                "available": nli_counts["flagged_pair_count"],
                "reviewed": observed_by_stratum["nli_flagged"],
                "selection": "complete_stratum",
            },
            "nli_unflagged": {
                "available": nli_counts["not_flagged_pair_count"],
                "reviewed": observed_by_stratum["nli_unflagged_sample"],
                "selection": "task- and dataset-balanced diagnostic sample",
            },
            "representative_of_full_packet": False,
        },
        "counts": {
            field: dict(sorted(counter.items())) for field, counter in counts.items()
        },
        "decision_counts_by_sampling_stratum": {
            stratum: {
                decision: by_stratum[stratum].get(decision, 0)
                for decision in ("accept", "discuss", "reject")
            }
            for stratum in sorted(STRATA)
        },
        "decision": "repair_or_regenerate_before_probe_scoring_or_scale_up",
        "limitations": [
            "This is a label-blind model-assisted diagnostic, not a human-certified review.",
            "Only 24 of 100 pairs were reviewed; all 14 NLI-flagged pairs were intentionally oversampled, while 10 of 86 unflagged pairs formed a task- and dataset-balanced diagnostic sample.",
            "The aggregate decision rates are therefore nonrepresentative and must not be interpreted as full-dataset pass rates.",
            "NLI-based sampling makes between-stratum comparisons descriptive rather than an independent estimate of NLI screening accuracy.",
            "The review recorded whether a clear certainty contrast was present, but not which version was more certain; direction relative to intended confident/hedged labels was not captured or verified.",
            "Preserved content and a clear certainty contrast do not compensate for unnatural wording or ambiguous cue scope.",
            "This diagnostic does not validate training data and does not authorize probe scoring, loss training, or activation steering.",
        ],
        "privacy": {
            "per_example_records": False,
            "identity_bearing_fields": False,
            "source_or_response_text": False,
            "reviewer_comments": False,
        },
    }
    return public


def write_public_summary(output_path: Path, summary: dict[str, Any], *, overwrite: bool = False) -> None:
    if output_path.exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing public summary: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def _resolve(base: Path, path: Path) -> Path:
    return path if path.is_absolute() else base / path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--private-review", required=True, type=Path)
    parser.add_argument("--packet-dir", required=True, type=Path)
    parser.add_argument("--nli-report", required=True, type=Path)
    parser.add_argument("--private-nli-triage", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args(argv)
    summary = build_public_summary(
        _resolve(BASE, args.private_review),
        _resolve(BASE, args.packet_dir),
        _resolve(BASE, args.nli_report),
        _resolve(BASE, args.private_nli_triage),
    )
    write_public_summary(_resolve(BASE, args.output), summary, overwrite=args.overwrite)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
