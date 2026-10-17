"""Build a private blind-review packet for the six mechanically clean v4 pairs.

This is an interim failure-discovery review, not final canary certification.
The complete frozen 12-pair set is validated before the six-row subset is
derived from the hash-bound post-repair validator.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
from typing import Any, Mapping, Sequence


SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import build_factual_rewrite_review as review
from canary_binding import build_artifact_binding, validate_artifact_binding


BASE = Path(__file__).resolve().parents[1]
PRIVATE = (BASE / "private_data").resolve()
DEFAULT_CONFIG = BASE / "configs" / "rewrite_canary_v4_clean_six_review.json"
DEFAULT_SOURCES = PRIVATE / "rewrite_canary_v1" / "frozen_sources_v4.jsonl"
DEFAULT_PAIRS = (
    PRIVATE / "rewrite_canary_v1" / "WRITER_CANARY_12_V4_POST_REPAIR.jsonl"
)
DEFAULT_VALIDATOR = (
    PRIVATE
    / "rewrite_canary_v1"
    / "WRITER_CANARY_12_V4_POST_REPAIR_VALIDATION.json"
)
DEFAULT_PROVENANCE = (
    PRIVATE
    / "rewrite_canary_v1"
    / "WRITER_CANARY_12_V4_POST_REPAIR_PROVENANCE.json"
)
DEFAULT_FREEZE_MANIFEST = (
    PRIVATE / "rewrite_canary_v1" / "FREEZE_MANIFEST_PRIVATE_V4.json"
)
DEFAULT_OUTPUT = PRIVATE / "rewrite_canary_v1" / "blind_review_clean6_v4"
DEFAULT_PUBLIC_SUMMARY = (
    BASE / "results" / "rewrite_canary_v4_clean_six_packet_summary.json"
)


def canonical_sha256(value: Any) -> str:
    payload = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json_object(path: Path, label: str) -> dict[str, Any]:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    return value


def validate_config(config: Mapping[str, Any]) -> None:
    if config.get("schema_version") != "factual-rewrite-clean-subset-review-config-v1":
        raise ValueError("unexpected clean-subset review config schema")
    for field in ("seed", "full_pair_count", "selected_pair_count"):
        value = config.get(field)
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            raise ValueError(f"config {field} must be a positive integer")
    if config["full_pair_count"] != review.EXPECTED_PAIRS:
        raise ValueError("clean-subset review must validate the complete 12-pair set")
    if config["selected_pair_count"] % 2:
        raise ValueError("selected_pair_count must be even for balanced A/B roles")
    counts = config.get("expected_selected_dataset_counts")
    if (
        not isinstance(counts, dict)
        or any(not isinstance(key, str) or not key for key in counts)
        or any(isinstance(value, bool) or not isinstance(value, int) or value < 1 for value in counts.values())
        or sum(counts.values()) != config["selected_pair_count"]
    ):
        raise ValueError("expected_selected_dataset_counts is invalid")
    hashes = config.get("input_sha256")
    if not isinstance(hashes, dict):
        raise ValueError("config input_sha256 must be an object")
    expected_hash_fields = {
        "frozen_sources_v4",
        "post_repair_pairs_v4",
        "post_repair_validator_v4",
        "post_repair_provenance_v4",
        "freeze_manifest_v4",
    }
    if set(hashes) != expected_hash_fields or any(
        not isinstance(value, str)
        or len(value) != 64
        or any(character not in "0123456789abcdef" for character in value)
        for value in hashes.values()
    ):
        raise ValueError("config input hashes are incomplete or invalid")
    for field in (
        "final_canary_certification",
        "human_review_certified",
        "replacement_generation_authorized",
        "activation_extraction_authorized",
        "probe_fitting_authorized",
        "sdt_training_authorized",
    ):
        if config.get(field) is not False:
            raise ValueError(f"config must keep {field} false")


def validate_input_hashes(
    config: Mapping[str, Any], paths: Mapping[str, Path]
) -> dict[str, str]:
    actual = {name: sha256_file(path) for name, path in paths.items()}
    expected = config["input_sha256"]
    for name, digest in actual.items():
        if digest != expected.get(name):
            raise ValueError(f"{name} SHA-256 drifted")
    return actual


def select_clean_subset(
    full_rows: Sequence[dict[str, Any]],
    validator: Mapping[str, Any],
    config: Mapping[str, Any],
) -> list[dict[str, Any]]:
    expected_full = int(config["full_pair_count"])
    expected_selected = int(config["selected_pair_count"])
    if len(full_rows) != expected_full:
        raise ValueError("full joined pair set has the wrong size")
    full_by_id = {str(row.get("source_id")): row for row in full_rows}
    if len(full_by_id) != expected_full or "None" in full_by_id:
        raise ValueError("full joined pair set requires unique source IDs")

    validator_rows = validator.get("rows")
    if not isinstance(validator_rows, list) or len(validator_rows) != expected_full:
        raise ValueError("validator must contain the complete 12-row set")
    validator_by_id: dict[str, Mapping[str, Any]] = {}
    for row in validator_rows:
        if not isinstance(row, dict):
            raise ValueError("every validator row must be an object")
        source_id = row.get("source_id")
        if not isinstance(source_id, str) or not source_id or source_id in validator_by_id:
            raise ValueError("validator source IDs must be nonempty and unique")
        flags = row.get("failure_flags")
        if not isinstance(flags, list) or any(not isinstance(flag, str) for flag in flags):
            raise ValueError(f"{source_id}: failure_flags must be a string list")
        if row.get("mechanical_gate_pass") != (len(flags) == 0):
            raise ValueError(f"{source_id}: mechanical gate and failure flags disagree")
        validator_by_id[source_id] = row
    if set(validator_by_id) != set(full_by_id):
        raise ValueError("validator and full pair source sets differ")
    if validator.get("global_failure_flags") != []:
        raise ValueError("validator has global failure flags")

    expected_binding = validate_artifact_binding(validator.get("artifact_binding"))
    actual_binding = build_artifact_binding(full_rows, full_rows)
    if actual_binding != expected_binding:
        raise ValueError("validator artifact binding does not match the full pair set")

    selected_ids = {
        source_id
        for source_id, row in validator_by_id.items()
        if row["failure_flags"] == []
    }
    if len(selected_ids) != expected_selected:
        raise ValueError("validator does not select the expected clean-subset size")
    selected = [full_by_id[source_id] for source_id in sorted(selected_ids)]
    actual_counts = Counter(str(row["dataset"]) for row in selected)
    if dict(sorted(actual_counts.items())) != dict(
        sorted(config["expected_selected_dataset_counts"].items())
    ):
        raise ValueError("clean-subset dataset counts drifted")
    return selected


def balanced_clean6_a_roles(
    rows: Sequence[dict[str, Any]], seed: int
) -> dict[str, str]:
    """Choose a deterministic 3/3 role split with nuisance balance."""
    if len(rows) != 6:
        raise ValueError("clean-subset review requires exactly six rows")
    ids = tuple(sorted(str(row.get("source_id")) for row in rows))
    if len(set(ids)) != 6 or "None" in ids:
        raise ValueError("clean-subset rows require six unique source IDs")
    row_by_id = {str(row["source_id"]): row for row in rows}

    def groups(field: str) -> dict[str, list[str]]:
        result: dict[str, list[str]] = defaultdict(list)
        for source_id in ids:
            value = row_by_id[source_id].get(field)
            if not isinstance(value, str) or not value:
                raise ValueError(f"every clean-subset row requires {field}")
            result[value].append(source_id)
        return result

    required_three_way = {
        field: groups(field) for field in ("dataset", "length_direction", "draft_order")
    }
    if any(
        sorted(len(members) for members in field_groups.values()) != [3, 3]
        for field_groups in required_three_way.values()
    ):
        raise ValueError("clean-subset nuisance groups must each form a 3/3 split")
    cue_groups = groups("cue_family")

    valid: list[tuple[bytes, set[str]]] = []
    for choice in combinations(ids, 3):
        confident_a = set(choice)
        three_way_balanced = all(
            all(sum(member in confident_a for member in members) in {1, 2} for members in field_groups.values())
            for field_groups in required_three_way.values()
        )
        repeated_cues_balanced = all(
            len(members) != 2 or sum(member in confident_a for member in members) == 1
            for members in cue_groups.values()
        )
        if three_way_balanced and repeated_cues_balanced:
            digest = review._stable_digest(
                seed,
                "factual-review-clean6-a-role",
                *sorted(confident_a),
            )
            valid.append((digest, confident_a))
    if not valid:
        raise ValueError("no clean-subset A/B assignment satisfies nuisance balance")
    confident_a = min(valid, key=lambda item: item[0])[1]
    roles = {
        source_id: "confident" if source_id in confident_a else "hesitant"
        for source_id in ids
    }
    if Counter(roles.values()) != Counter({"confident": 3, "hesitant": 3}):
        raise AssertionError("clean-subset A/B roles are not balanced 3/3")
    return roles


def build_clean6_blinded_rows(
    rows: Sequence[dict[str, Any]], seed: int
) -> tuple[list[dict[str, str]], list[dict[str, Any]]]:
    roles = balanced_clean6_a_roles(rows, seed)
    return review.materialize_blinded_rows(
        rows,
        roles,
        seed,
        review_prefix="C6R",
        order_purpose="factual-review-clean6-packet-order",
    )


def write_clean6_review_bundle(
    full_rows: Sequence[dict[str, Any]],
    selected_rows: Sequence[dict[str, Any]],
    output_dir: Path,
    *,
    seed: int,
    input_hashes: Mapping[str, str],
    config_sha256: str,
    overwrite: bool = False,
    private_root: Path = PRIVATE,
) -> dict[str, Any]:
    if len(full_rows) != 12 or len(selected_rows) != 6:
        raise ValueError("clean-subset writer requires a complete 12-row set and six selected rows")
    full_by_id = {str(row.get("source_id")): row for row in full_rows}
    selected_by_id = {str(row.get("source_id")): row for row in selected_rows}
    if len(full_by_id) != 12 or len(selected_by_id) != 6:
        raise ValueError("full and selected rows require unique source IDs")
    if not set(selected_by_id) <= set(full_by_id) or any(
        row != full_by_id[source_id] for source_id, row in selected_by_id.items()
    ):
        raise ValueError("selected rows must be an exact subset of the full set")
    expected_hash_names = {
        "frozen_sources_v4",
        "post_repair_pairs_v4",
        "post_repair_validator_v4",
        "post_repair_provenance_v4",
        "freeze_manifest_v4",
    }
    if set(input_hashes) != expected_hash_names or any(
        not isinstance(value, str)
        or len(value) != 64
        or any(character not in "0123456789abcdef" for character in value)
        for value in input_hashes.values()
    ):
        raise ValueError("clean-subset writer requires all five valid input hashes")
    if (
        not isinstance(config_sha256, str)
        or len(config_sha256) != 64
        or any(character not in "0123456789abcdef" for character in config_sha256)
    ):
        raise ValueError("clean-subset writer requires a valid config hash")
    output = review.require_private_output(output_dir, private_root)
    output.mkdir(parents=True, exist_ok=True)
    blinded, answer_key = build_clean6_blinded_rows(selected_rows, seed)
    packet_sha256 = review.sha256_value(blinded)
    html_text = review.render_html(
        blinded,
        packet_sha256,
        page_title="Clean-six interim blind review",
        intro=(
            "This packet contains only the six v4 pairs that passed mechanical "
            "checks. It is an interim failure-discovery review, not the final "
            "12-pair canary review."
        ),
        notice=(
            "Judge content preservation, A/B content equivalence, speaker-level "
            "certainty direction, naturalness, formatting, and shortcut cues. "
            "Completing this form does not certify the canary."
        ),
        export_name="factual_rewrite_clean6_interim_review.json",
        export_metadata={
            "schema": "factual-rewrite-clean-subset-review-results-v1",
            "artifact_role": "interim_failure_discovery_only",
            "pair_count": 6,
            "final_canary_certification": False,
            "human_review_certified": False,
        },
    )
    reviewer_dir = output / "reviewer_only"
    key_dir = output / "private_key"
    reviewer_dir.mkdir(parents=True, exist_ok=True)
    key_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "html": reviewer_dir / "BLIND_REVIEW.html",
        "answer_key": key_dir / "BLIND_REVIEW_KEY.json",
        "manifest": output / "BLIND_REVIEW_MANIFEST.json",
    }
    existing = [path for path in paths.values() if path.exists()]
    if existing and not overwrite:
        raise FileExistsError(
            "review bundle already exists: " + ", ".join(str(path) for path in existing)
        )
    paths["html"].write_text(html_text, encoding="utf-8")
    key_payload = {
        "schema": "factual-rewrite-clean-subset-blind-key-v1",
        "seed": seed,
        "packet_sha256": packet_sha256,
        "rows": answer_key,
    }
    review._write_json(paths["answer_key"], key_payload)
    manifest = {
        "schema": "factual-rewrite-clean-subset-blind-review-v1",
        "artifact_role": "interim_failure_discovery_only",
        "final_canary_certification": False,
        "human_review_certified": False,
        "seed": seed,
        "full_pair_count": len(full_rows),
        "pair_count": len(selected_rows),
        "selection_rule": "validator row has an empty failure_flags list",
        "selected_dataset_counts": dict(sorted(Counter(
            str(row["dataset"]) for row in selected_rows
        ).items())),
        "packet_sha256": packet_sha256,
        "html_sha256": review.sha256_file(paths["html"]),
        "answer_key_sha256": review.sha256_file(paths["answer_key"]),
        "version_a_role_counts": dict(sorted(Counter(
            row["version_a_role"] for row in answer_key
        ).items())),
        "version_a_role_counts_by_dataset": {
            dataset: dict(sorted(Counter(
                row["version_a_role"]
                for row in answer_key
                if row["dataset"] == dataset
            ).items()))
            for dataset in sorted({str(row["dataset"]) for row in answer_key})
        },
        "review_fields": list(review.REQUIRED_REVIEW_FIELDS) + ["notes"],
        "blinded": True,
        "answer_key_embedded_in_html": False,
        "distribution_rule": "share only reviewer_only/BLIND_REVIEW.html",
        "full_set_artifact_binding": build_artifact_binding(full_rows, full_rows),
        "selected_subset_artifact_binding": build_artifact_binding(
            selected_rows, selected_rows
        ),
        "input_sha256": dict(sorted(input_hashes.items())),
        "config_sha256": config_sha256,
    }
    review._write_json(paths["manifest"], manifest)
    return {
        "paths": {name: str(path) for name, path in paths.items()},
        "manifest": manifest,
    }


def write_public_packet_summary(
    manifest: Mapping[str, Any], output_path: Path
) -> dict[str, Any]:
    """Write text-free packet-generation metadata for GitHub."""
    summary = {
        "schema": "factual-rewrite-clean-subset-packet-summary-v1",
        "status": "packet_prepared",
        "artifact_role": "interim_failure_discovery_packet",
        "source_set_revision": "v4",
        "full_pair_count": manifest["full_pair_count"],
        "selected_pair_count": manifest["pair_count"],
        "selected_dataset_counts": manifest["selected_dataset_counts"],
        "selection_rule": manifest["selection_rule"],
        "packet_sha256": manifest["packet_sha256"],
        "config_sha256": manifest["config_sha256"],
        "input_sha256": manifest["input_sha256"],
        "review_fields": manifest["review_fields"],
        "blinded": True,
        "answer_key_public": False,
        "review_completion_tracked_here": False,
        "current_review_summary": (
            "rewrite_canary_v4_clean_six_model_review_summary.json"
        ),
        "final_canary_certification": False,
        "human_review_certified": False,
        "authorization": {
            "replacement_generation": False,
            "activation_extraction": False,
            "probe_fitting": False,
            "sdt_training": False,
        },
        "next_action": (
            "Use the separate model-review summary for current review results; "
            "human adjudication remains required before freezing the final "
            "failed-slot set."
        ),
    }
    review._write_json(Path(output_path), summary)
    return summary


def build_review_bundle(
    *,
    config_path: Path = DEFAULT_CONFIG,
    sources_path: Path = DEFAULT_SOURCES,
    pairs_path: Path = DEFAULT_PAIRS,
    validator_path: Path = DEFAULT_VALIDATOR,
    provenance_path: Path = DEFAULT_PROVENANCE,
    freeze_manifest_path: Path = DEFAULT_FREEZE_MANIFEST,
    output_dir: Path = DEFAULT_OUTPUT,
    public_summary_path: Path = DEFAULT_PUBLIC_SUMMARY,
    overwrite: bool = False,
    private_root: Path = PRIVATE,
) -> dict[str, Any]:
    config = read_json_object(config_path, "config")
    validate_config(config)
    paths = {
        "frozen_sources_v4": sources_path,
        "post_repair_pairs_v4": pairs_path,
        "post_repair_validator_v4": validator_path,
        "post_repair_provenance_v4": provenance_path,
        "freeze_manifest_v4": freeze_manifest_path,
    }
    input_hashes = validate_input_hashes(config, paths)
    sources = review.read_records(sources_path)
    pairs = review.read_records(pairs_path)
    full_rows = review.join_sources_and_pairs(sources, pairs)
    validator = read_json_object(validator_path, "validator")
    selected_rows = select_clean_subset(full_rows, validator, config)
    freeze_manifest = read_json_object(freeze_manifest_path, "freeze manifest")
    if (
        freeze_manifest.get("source_set_revision") != config["source_set_revision"]
        or freeze_manifest.get("source_count") != config["full_pair_count"]
        or freeze_manifest.get("frozen_sources_sha256")
        != input_hashes["frozen_sources_v4"]
    ):
        raise ValueError("v4 freeze manifest does not bind the frozen sources")
    result = write_clean6_review_bundle(
        full_rows,
        selected_rows,
        output_dir,
        seed=int(config["seed"]),
        input_hashes=input_hashes,
        config_sha256=sha256_file(config_path),
        overwrite=overwrite,
        private_root=private_root,
    )
    result["public_packet_summary"] = write_public_packet_summary(
        result["manifest"], public_summary_path
    )
    result["public_packet_summary_path"] = str(Path(public_summary_path))
    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--sources", type=Path, default=DEFAULT_SOURCES)
    parser.add_argument("--pairs", type=Path, default=DEFAULT_PAIRS)
    parser.add_argument("--validator", type=Path, default=DEFAULT_VALIDATOR)
    parser.add_argument("--provenance", type=Path, default=DEFAULT_PROVENANCE)
    parser.add_argument("--freeze-manifest", type=Path, default=DEFAULT_FREEZE_MANIFEST)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--public-summary", type=Path, default=DEFAULT_PUBLIC_SUMMARY
    )
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args(argv)
    result = build_review_bundle(
        config_path=args.config,
        sources_path=args.sources,
        pairs_path=args.pairs,
        validator_path=args.validator,
        provenance_path=args.provenance,
        freeze_manifest_path=args.freeze_manifest,
        output_dir=args.output_dir,
        public_summary_path=args.public_summary,
        overwrite=args.overwrite,
    )
    manifest = result["manifest"]
    print(json.dumps({
        "output_dir": str(Path(args.output_dir).resolve()),
        "reviewer_html": result["paths"]["html"],
        "pair_count": manifest["pair_count"],
        "packet_sha256": manifest["packet_sha256"],
        "selected_dataset_counts": manifest["selected_dataset_counts"],
        "final_canary_certification": False,
        "human_review_certified": False,
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
