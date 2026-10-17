#!/usr/bin/env python3
"""Plan v5 source replacements without generating or exposing source text.

The planner replaces each failed v4 experimental slot with an accepted, unused
backup from the same dataset.  It applies an audited private metadata ledger
before calculating three bounded midrank features, then solves the assignment
globally within each dataset.  The public artifact contains identifiers,
numeric features, hashes, and preregistered slot metadata only.

This script never edits the source pool, generates rewrites, extracts
activations, fits probes, or starts training.  Until both the private metadata
audit and the expected mapping are frozen, it emits an explicit audit-pending
artifact with every downstream authorization set to false.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / "private_data"
DEFAULT_CONFIG = ROOT / "configs" / "rewrite_canary_v5_replacement.json"
DEFAULT_SOURCE_POOL = PRIVATE / "expanded_pool_v2" / "selected_core_sources_v1.jsonl"
DEFAULT_FROZEN_SLOTS = PRIVATE / "rewrite_canary_v1" / "frozen_sources_v4.jsonl"
DEFAULT_FREEZE_MANIFEST = (
    PRIVATE / "rewrite_canary_v1" / "FREEZE_MANIFEST_PRIVATE_V4.json"
)
DEFAULT_VALIDATOR = (
    PRIVATE
    / "rewrite_canary_v1"
    / "WRITER_CANARY_12_V4_POST_REPAIR_VALIDATION.json"
)
DEFAULT_LEDGER = (
    PRIVATE / "rewrite_canary_v1" / "REPLACEMENT_METADATA_CORRECTIONS_V5.json"
)
DEFAULT_AUDIT_ARTIFACT = (
    PRIVATE / "rewrite_canary_v1" / "REPLACEMENT_SOURCE_SEMANTIC_AUDIT_V5.json"
)
DEFAULT_OUTPUT = ROOT / "results" / "rewrite_canary_v5_replacement_plan.json"

CONFIG_SCHEMA = "factual-rewrite-replacement-plan-config-v1"
LEDGER_SCHEMA = "factual-rewrite-replacement-metadata-ledger-v1"
AUDIT_ARTIFACT_SCHEMA = "factual-rewrite-independent-source-audit-v1"
OUTPUT_SCHEMA = "factual-rewrite-replacement-plan-v1"
HEX_DIGITS = set("0123456789abcdef")
SAFE_PRESERVED_SLOT_FIELDS = [
    "profile",
    "selection_features",
    "selection_target",
    "selection_distance",
    "cue_family",
    "length_direction",
    "draft_order",
    "batch_id",
    "batch_position",
    "generation_order",
]
SAFE_PROFILES = {
    "short_simple",
    "mid_plain",
    "long_complex",
    "qualifier_sensitive",
}
SAFE_CUE_FAMILIES = {
    "embedded_stance_predicate",
    "modal_force_scope",
    "compositional_polarity",
    "discourse_level_calibration",
    "contrastive_commitment",
}
SAFE_LENGTH_DIRECTIONS = {"confident_longer", "hesitant_longer"}
SAFE_DRAFT_ORDERS = {"confident_first", "hesitant_first"}
SAFE_BATCH_IDS = {"batch_01", "batch_02", "batch_03"}
REFERENCE_POOL_TEMPLATE = (
    "the same dataset's {core_count} frozen accepted core rows plus the "
    "candidate itself; selected-core qualifier counts come from the hash-bound "
    "frozen v4 rows, and backup qualifier counts come from the audited v5 ledger"
)
TIE_BREAK_DESCRIPTION = (
    "sha256 of seed, namespace, dataset, and the canonical full mapping"
)


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_text(value: str) -> str:
    return sha256_bytes(value.encode("utf-8"))


def is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in HEX_DIGITS for character in value)
    )


def stable_hash(*parts: object) -> str:
    return sha256_text("|".join(str(part) for part in parts))


def read_json_object_bytes(path: Path) -> tuple[dict[str, Any], bytes]:
    raw = Path(path).read_bytes()
    value = json.loads(raw.decode("utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected a JSON object: {path}")
    return value, raw


def read_jsonl_bytes(path: Path) -> tuple[list[dict[str, Any]], bytes]:
    raw = Path(path).read_bytes()
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(raw.decode("utf-8").splitlines(), 1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{line_number}: expected a JSON object")
        rows.append(value)
    return rows, raw


def write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(value, indent=2, sort_keys=True) + "\n"
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(serialized, encoding="utf-8")
    temporary.replace(path)


def normalize_descriptors(row: Mapping[str, Any]) -> list[str]:
    raw = row.get("protected_qualifiers") or []
    if not isinstance(raw, list) or not all(isinstance(item, str) for item in raw):
        raise ValueError(
            f"{row.get('source_id')}: protected_qualifiers must be a list of strings"
        )
    return [item.strip() for item in raw if item.strip()]


def descriptor_hashes(descriptors: Sequence[str]) -> list[str]:
    return [sha256_text(value) for value in descriptors]


def source_universe_hash(rows: Sequence[Mapping[str, Any]]) -> str:
    payload = [
        {
            "source_id": row["source_id"],
            "source_hash": row["source_hash"],
            "protected_qualifier_sha256": descriptor_hashes(
                normalize_descriptors(row)
            ),
        }
        for row in sorted(rows, key=lambda item: str(item["source_id"]))
    ]
    return sha256_text(canonical_json(payload))


def validate_config(config: Mapping[str, Any]) -> None:
    if config.get("schema_version") != CONFIG_SCHEMA:
        raise ValueError("unexpected replacement-plan config schema")
    if config.get("plan_revision") != "v5":
        raise ValueError("replacement plan must target revision v5")
    seed = config.get("seed")
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise ValueError("replacement-plan seed must be an integer")
    source = config.get("source_pool")
    failed = config.get("failed_slots")
    features = config.get("features")
    assignment = config.get("assignment")
    ledger = config.get("metadata_correction_ledger")
    expected = config.get("expected_mapping")
    authorization = config.get("authorization")
    if not all(
        isinstance(item, dict)
        for item in (source, failed, features, assignment, ledger, expected, authorization)
    ):
        raise ValueError("replacement-plan config is missing a required section")
    if not is_sha256(source.get("expected_sha256")):
        raise ValueError("source pool must have a frozen SHA-256")
    datasets = source.get("datasets")
    if not isinstance(datasets, list) or not datasets or len(datasets) != len(set(datasets)):
        raise ValueError("source datasets must be a unique non-empty list")
    failed_ids = failed.get("expected_source_ids")
    if (
        not isinstance(failed_ids, list)
        or len(failed_ids) != int(failed.get("expected_count", -1))
        or len(failed_ids) != len(set(failed_ids))
    ):
        raise ValueError("failed-slot IDs must be unique and match expected_count")
    expected_total_frozen = failed.get("expected_total_frozen_slots")
    if (
        isinstance(expected_total_frozen, bool)
        or not isinstance(expected_total_frozen, int)
        or expected_total_frozen < len(failed_ids)
    ):
        raise ValueError("expected_total_frozen_slots must cover all failed slots")
    for field in (
        "frozen_slots_expected_sha256",
        "freeze_manifest_expected_sha256",
        "post_repair_validator_expected_sha256",
    ):
        if not is_sha256(failed.get(field)):
            raise ValueError(f"failed slots require a valid {field}")
    if features.get("names") != [
        "word_count_candidate_included_midrank",
        "sentence_count_candidate_included_midrank",
        "corrected_qualifier_count_candidate_included_midrank",
    ]:
        raise ValueError("unexpected replacement feature set")
    if features.get("midrank_formula") != "(count_less + (count_equal + 1) / 2) / n":
        raise ValueError("unexpected midrank formula")
    expected_reference_pool = REFERENCE_POOL_TEMPLATE.format(
        core_count=source.get("expected_core_per_dataset")
    )
    if features.get("reference_pool") != expected_reference_pool:
        raise ValueError("unexpected replacement reference-pool description")
    if features.get("bounded_interval") != "(0, 1]":
        raise ValueError("unexpected replacement feature interval")
    if features.get("distance") != "squared_euclidean":
        raise ValueError("unexpected distance metric")
    round_digits = features.get("distance_round_digits")
    if (
        isinstance(round_digits, bool)
        or not isinstance(round_digits, int)
        or not 0 <= round_digits <= 15
    ):
        raise ValueError("distance_round_digits must be an integer from 0 to 15")
    if assignment.get("method") != "global_one_to_one_minimum_total_distance_per_dataset":
        raise ValueError("unexpected replacement-assignment method")
    if assignment.get("tie_breaker") != TIE_BREAK_DESCRIPTION:
        raise ValueError("unexpected replacement-assignment tie-break description")
    namespace = assignment.get("key_namespace")
    if not isinstance(namespace, str) or not namespace.strip():
        raise ValueError("replacement-assignment key namespace must be non-empty")
    if assignment.get("same_dataset_required") is not True:
        raise ValueError("replacement assignment must remain within dataset")
    preserved = assignment.get("preserved_slot_fields")
    if preserved != SAFE_PRESERVED_SLOT_FIELDS:
        raise ValueError("preserved slot fields must match the frozen public-safe list")
    if ledger.get("required") is not True or ledger.get("audit_complete_required") is not True:
        raise ValueError("the private correction ledger and completed audit are required")
    if ledger.get("required_schema_version") != LEDGER_SCHEMA:
        raise ValueError("unexpected private correction-ledger schema")
    audit_filename = ledger.get("private_audit_artifact_filename")
    if (
        not isinstance(audit_filename, str)
        or not audit_filename
        or Path(audit_filename).name != audit_filename
        or not audit_filename.endswith(".json")
    ):
        raise ValueError("private audit artifact filename must be a plain JSON filename")
    if expected.get("audit_complete") not in (True, False):
        raise ValueError("expected_mapping.audit_complete must be boolean")
    if expected["audit_complete"] is True:
        if not is_sha256(expected.get("mapping_sha256")):
            raise ValueError("frozen expected mapping requires a valid mapping SHA-256")
        if not is_sha256(expected.get("assignment_input_sha256")):
            raise ValueError(
                "frozen expected mapping requires a valid assignment-input SHA-256"
            )
        frozen_mapping = expected.get("failed_to_replacement")
        if not isinstance(frozen_mapping, dict) or set(frozen_mapping) != set(failed_ids):
            raise ValueError("frozen expected mapping must cover every failed slot")
    elif (
        expected.get("mapping_sha256") is not None
        or expected.get("assignment_input_sha256") is not None
        or expected.get("failed_to_replacement") != {}
    ):
        raise ValueError("unfrozen expected mapping must not contain frozen values")
    expected_counts = source.get("expected_accepted_unused_backups_by_dataset")
    if (
        not isinstance(expected_counts, dict)
        or set(expected_counts) != set(datasets)
        or any(
            isinstance(value, bool) or not isinstance(value, int) or value < 1
            for value in expected_counts.values()
        )
    ):
        raise ValueError(
            "accepted unused backup counts must be positive integers keyed by dataset"
        )
    held = source.get("expected_hold_source_ids")
    if not isinstance(held, list) or len(held) != len(set(held)):
        raise ValueError("expected held backup IDs must be a unique list")
    for key in ("activation_extraction", "probe_fitting", "sdt_training"):
        if authorization.get(key) is not False:
            raise ValueError(f"{key} cannot be authorized by source replacement planning")
    if authorization.get("generation_on_verified_plan") is not False:
        raise ValueError("generation_on_verified_plan must remain false")


def validate_bound_bytes(raw: bytes, expected_sha256: str, label: str) -> str:
    actual = sha256_bytes(raw)
    if actual != expected_sha256:
        raise ValueError(
            f"{label} SHA-256 drifted: expected {expected_sha256}, found {actual}"
        )
    return actual


def accepted_by_frozen_review(
    row: Mapping[str, Any], requirements: Mapping[str, Any]
) -> bool:
    return all(row.get(field) == expected for field, expected in requirements.items())


def validate_source_pool(
    rows: Sequence[dict[str, Any]], config: Mapping[str, Any]
) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]]]:
    source = config["source_pool"]
    datasets = set(source["datasets"])
    required = {
        "source_id",
        "source_hash",
        "dataset",
        "selection_role",
        "word_count",
        "sentence_count",
        "protected_qualifiers",
        "original_response",
    }
    indexed: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not required.issubset(row):
            raise ValueError("source pool row is missing required replacement fields")
        source_id = row["source_id"]
        if not isinstance(source_id, str) or not source_id or source_id in indexed:
            raise ValueError("source pool has an invalid or duplicate source_id")
        if row["dataset"] not in datasets:
            raise ValueError(f"{source_id}: unexpected dataset")
        if not is_sha256(row["source_hash"]):
            raise ValueError(f"{source_id}: invalid source_hash")
        for field in ("word_count", "sentence_count"):
            value = row[field]
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"{source_id}: {field} must be a positive integer")
        normalize_descriptors(row)
        indexed[source_id] = row

    core_role = source["core_role"]
    expected_core = int(source["expected_core_per_dataset"])
    requirements = source["acceptance_requirements"]
    for dataset in datasets:
        core = [
            row
            for row in rows
            if row["dataset"] == dataset and row["selection_role"] == core_role
        ]
        if len(core) != expected_core:
            raise ValueError(f"{dataset}: expected {expected_core} core rows")
        if not all(accepted_by_frozen_review(row, requirements) for row in core):
            raise ValueError(f"{dataset}: core reference pool contains an unaccepted row")
    backups = [
        row for row in rows if row["selection_role"] == source["candidate_role"]
    ]
    unexpected_roles = {
        row["selection_role"]
        for row in rows
        if row["selection_role"] not in {core_role, source["candidate_role"]}
    }
    if unexpected_roles:
        raise ValueError("source pool contains an unexpected selection role")
    backup_ids = {row["source_id"] for row in backups}
    held_ids = set(source["expected_hold_source_ids"])
    used_ids = set(source["used_backup_source_ids"])
    if len(used_ids) != len(source["used_backup_source_ids"]):
        raise ValueError("used backup IDs must be unique")
    if not held_ids.issubset(backup_ids):
        raise ValueError("expected hold set contains a non-backup source")
    if not used_ids.issubset(backup_ids):
        raise ValueError("used backup set contains a non-backup source")
    if held_ids & used_ids:
        raise ValueError("held and used backup sets must not overlap")
    expected_counts = source["expected_accepted_unused_backups_by_dataset"]
    for dataset in datasets:
        dataset_backup_ids = {
            row["source_id"] for row in backups if row["dataset"] == dataset
        }
        expected_available = len(
            dataset_backup_ids - held_ids - used_ids
        )
        if int(expected_counts[dataset]) != expected_available:
            raise ValueError(
                f"{dataset}: accepted-unused backup count disagrees with hold/use sets"
            )
    return indexed, backups


def failed_slot_rows(
    frozen_rows: Sequence[dict[str, Any]],
    validator: Mapping[str, Any],
    config: Mapping[str, Any],
) -> tuple[list[dict[str, Any]], set[str]]:
    expected_ids = set(config["failed_slots"]["expected_source_ids"])
    validator_rows = validator.get("rows")
    if not isinstance(validator_rows, list):
        raise ValueError("post-repair validator is missing rows")
    expected_total = int(config["failed_slots"]["expected_total_frozen_slots"])
    validator_ids = [
        row.get("source_id") for row in validator_rows if isinstance(row, dict)
    ]
    if (
        len(validator_rows) != expected_total
        or len(validator_ids) != expected_total
        or any(not isinstance(source_id, str) or not source_id for source_id in validator_ids)
        or len(set(validator_ids)) != expected_total
    ):
        raise ValueError(
            "post-repair validator must contain one unique row per frozen source"
        )
    actual_failed = {
        row.get("source_id")
        for row in validator_rows
        if isinstance(row, dict) and row.get("mechanical_gate_pass") is False
    }
    if actual_failed != expected_ids:
        raise ValueError("post-repair failure set drifted from the frozen v5 config")
    if validator.get("global_failure_flags"):
        raise ValueError("post-repair validator has global failures")
    frozen_by_id = {row.get("source_id"): row for row in frozen_rows}
    if len(frozen_by_id) != len(frozen_rows):
        raise ValueError("frozen v4 slots contain duplicate source IDs")
    if set(validator_ids) != set(frozen_by_id):
        raise ValueError("post-repair validator and frozen v4 source sets differ")
    preserved = config["assignment"]["preserved_slot_fields"]
    slots: list[dict[str, Any]] = []
    for source_id in expected_ids:
        row = frozen_by_id.get(source_id)
        if row is None:
            raise ValueError(f"failed slot is absent from frozen v4 rows: {source_id}")
        missing = [field for field in preserved if field not in row]
        if missing:
            raise ValueError(f"{source_id}: missing preserved slot fields {missing}")
        for field in ("selection_features", "selection_target"):
            vector = row.get(field)
            if (
                not isinstance(vector, list)
                or len(vector) != 3
                or any(
                    isinstance(value, bool)
                    or not isinstance(value, (int, float))
                    or not math.isfinite(float(value))
                    or not 0 <= float(value) <= 1
                    for value in vector
                )
            ):
                raise ValueError(f"{source_id}: invalid public-safe {field}")
        distance = row.get("selection_distance")
        if (
            isinstance(distance, bool)
            or not isinstance(distance, (int, float))
            or not math.isfinite(float(distance))
            or float(distance) < 0
        ):
            raise ValueError(f"{source_id}: invalid public-safe selection_distance")
        enum_requirements = {
            "profile": SAFE_PROFILES,
            "cue_family": SAFE_CUE_FAMILIES,
            "length_direction": SAFE_LENGTH_DIRECTIONS,
            "draft_order": SAFE_DRAFT_ORDERS,
            "batch_id": SAFE_BATCH_IDS,
        }
        for field, allowed in enum_requirements.items():
            if row.get(field) not in allowed:
                raise ValueError(f"{source_id}: invalid public-safe {field}")
        for field, lower, upper in (
            ("batch_position", 1, 4),
            ("generation_order", 1, 12),
        ):
            value = row.get(field)
            if (
                isinstance(value, bool)
                or not isinstance(value, int)
                or not lower <= value <= upper
            ):
                raise ValueError(f"{source_id}: invalid public-safe {field}")
        slots.append(row)
    return sorted(slots, key=lambda row: int(row["generation_order"])), set(frozen_by_id)


def apply_frozen_core_qualifier_counts(
    corrected_counts: Mapping[str, int],
    frozen_rows: Sequence[Mapping[str, Any]],
    source_by_id: Mapping[str, Mapping[str, Any]],
    *,
    core_role: str,
) -> dict[str, int]:
    """Use the hash-bound v4 metadata for selected core rows.

    The source-selection pool predates three reviewer-only qualifier corrections
    applied during the v4 freeze. Word/sentence metadata and source identity must
    remain identical; only the qualifier list may differ.
    """
    result = dict(corrected_counts)
    seen: set[str] = set()
    for frozen in frozen_rows:
        source_id = frozen.get("source_id")
        if not isinstance(source_id, str) or not source_id or source_id in seen:
            raise ValueError("frozen v4 rows contain an invalid or duplicate source_id")
        seen.add(source_id)
        source = source_by_id.get(source_id)
        if source is None:
            raise ValueError(f"{source_id}: frozen v4 row is absent from the source pool")
        if source.get("selection_role") != core_role:
            raise ValueError(f"{source_id}: frozen v4 row is not a core source")
        for field in ("dataset", "source_hash", "word_count", "sentence_count"):
            if frozen.get(field) != source.get(field):
                raise ValueError(
                    f"{source_id}: frozen v4 {field} disagrees with source pool"
                )
        result[source_id] = len(normalize_descriptors(frozen))
    return result


def audit_pending_artifact(
    *,
    config: Mapping[str, Any],
    reason_codes: Sequence[str],
    config_sha256: str,
    source_pool_sha256: str,
    frozen_slots_sha256: str,
    freeze_manifest_sha256: str,
    validator_sha256: str,
    failed_slots: Sequence[Mapping[str, Any]],
    ledger_sha256: str | None = None,
) -> dict[str, Any]:
    dataset_counts = Counter(str(row["dataset"]) for row in failed_slots)
    return {
        "schema_version": OUTPUT_SCHEMA,
        "artifact_role": "public_text_free_replacement_plan",
        "plan_revision": config["plan_revision"],
        "status": "audit_pending",
        "reason_codes": sorted(set(reason_codes)),
        "method": {
            "same_dataset": True,
            "features": list(config["features"]["names"]),
            "reference_pool": config["features"]["reference_pool"],
            "distance": config["features"]["distance"],
            "assignment": config["assignment"]["method"],
            "full_mapping_hash_tie_break": True,
        },
        "counts": {
            "failed_slots": len(failed_slots),
            "failed_slots_by_dataset": dict(sorted(dataset_counts.items())),
            "planned_replacements": 0,
        },
        "artifact_bindings": {
            "config_sha256": config_sha256,
            "source_pool_sha256": source_pool_sha256,
            "frozen_slots_sha256": frozen_slots_sha256,
            "v4_freeze_manifest_sha256": freeze_manifest_sha256,
            "post_repair_validator_sha256": validator_sha256,
            "private_metadata_ledger_sha256": ledger_sha256,
        },
        "authorization": {
            "replacement_generation": False,
            "activation_extraction": False,
            "probe_fitting": False,
            "sdt_training": False,
        },
        "privacy": {
            "source_or_rewrite_text_included": False,
            "qualifier_text_included": False,
        },
        "review_provenance_requirement": {
            "required_review_type": "model_assisted_independent",
            "human_certification_claim_allowed": False,
            "private_ledger_validated": False,
        },
    }


def validate_and_apply_ledger(
    *,
    ledger: Mapping[str, Any],
    source_rows: Sequence[dict[str, Any]],
    source_by_id: Mapping[str, dict[str, Any]],
    backup_rows: Sequence[dict[str, Any]],
    source_pool_sha256: str,
    config: Mapping[str, Any],
    audit_artifact: Mapping[str, Any],
    audit_artifact_sha256: str,
    audit_artifact_filename: str,
) -> tuple[dict[str, int], set[str]]:
    required_top = {
        "schema_version",
        "audit_complete",
        "source_pool_sha256",
        "feature_universe_sha256",
        "audit_provenance",
        "backup_audits",
        "qualifier_corrections",
    }
    if set(ledger) != required_top:
        raise ValueError("private metadata ledger has unexpected or missing fields")
    if ledger["schema_version"] != LEDGER_SCHEMA:
        raise ValueError("unexpected private metadata ledger schema")
    if ledger["source_pool_sha256"] != source_pool_sha256:
        raise ValueError("private metadata ledger is bound to a different source pool")
    expected_universe_hash = source_universe_hash(source_rows)
    if ledger["feature_universe_sha256"] != expected_universe_hash:
        raise ValueError("private metadata ledger feature-universe binding drifted")
    provenance = ledger["audit_provenance"]
    expected_provenance_keys = {
        "artifact_filename",
        "artifact_sha256",
        "review_run_id",
        "review_type",
        "human_certified",
    }
    if not isinstance(provenance, dict) or set(provenance) != expected_provenance_keys:
        raise ValueError("audit provenance has unexpected or missing fields")
    configured_filename = config["metadata_correction_ledger"][
        "private_audit_artifact_filename"
    ]
    if (
        provenance["artifact_filename"] != configured_filename
        or audit_artifact_filename != configured_filename
    ):
        raise ValueError("independent audit artifact filename drifted")
    if provenance["artifact_sha256"] != audit_artifact_sha256:
        raise ValueError("independent audit artifact SHA-256 drifted")
    if (
        not isinstance(provenance["review_run_id"], str)
        or not provenance["review_run_id"]
    ):
        raise ValueError("independent audit review_run_id must be non-empty")
    if provenance["review_type"] != "model_assisted_independent":
        raise ValueError("independent audit provenance has the wrong review type")
    if provenance["human_certified"] is not False:
        raise ValueError("independent audit provenance cannot claim human certification")

    expected_audit_top = {
        "schema_version",
        "review_type",
        "human_certified",
        "review_run_id",
        "decisions",
    }
    if set(audit_artifact) != expected_audit_top:
        raise ValueError("independent audit artifact has unexpected or missing fields")
    if audit_artifact["schema_version"] != AUDIT_ARTIFACT_SCHEMA:
        raise ValueError("unexpected independent audit artifact schema")
    for field in ("review_type", "human_certified", "review_run_id"):
        if audit_artifact[field] != provenance[field]:
            raise ValueError(f"independent audit artifact {field} drifted")

    audits = ledger["backup_audits"]
    if not isinstance(audits, list):
        raise ValueError("backup_audits must be a list")
    audits_by_id: dict[str, Mapping[str, Any]] = {}
    expected_audit_keys = {
        "source_id",
        "source_hash",
        "audit_complete",
        "review_type",
        "human_certified",
        "decision",
        "reason_codes",
        "source_accepted",
    }
    for audit in audits:
        if not isinstance(audit, dict) or set(audit) != expected_audit_keys:
            raise ValueError("backup audit has unexpected or missing fields")
        source_id = audit["source_id"]
        if source_id in audits_by_id:
            raise ValueError("private metadata ledger has duplicate backup audits")
        audits_by_id[source_id] = audit
    backup_ids = {row["source_id"] for row in backup_rows}
    if set(audits_by_id) != backup_ids:
        raise ValueError("private metadata ledger must audit every frozen backup")
    audit_decisions = audit_artifact["decisions"]
    if not isinstance(audit_decisions, list):
        raise ValueError("independent audit decisions must be a list")
    decisions_by_id: dict[str, Mapping[str, Any]] = {}
    expected_decision_keys = {
        "source_id",
        "source_hash",
        "decision",
        "reason_codes",
    }
    for decision in audit_decisions:
        if not isinstance(decision, dict) or set(decision) != expected_decision_keys:
            raise ValueError("independent audit decision has unexpected or missing fields")
        source_id = decision["source_id"]
        if source_id in decisions_by_id:
            raise ValueError("independent audit artifact has duplicate source decisions")
        decisions_by_id[source_id] = decision
    if set(decisions_by_id) != backup_ids:
        raise ValueError("independent audit artifact must decide every frozen backup")
    for source_id, audit in audits_by_id.items():
        source = source_by_id[source_id]
        if audit["source_hash"] != source["source_hash"]:
            raise ValueError(f"{source_id}: backup audit source hash drifted")
        if audit["audit_complete"] not in (True, False):
            raise ValueError(f"{source_id}: audit_complete must be boolean")
        if audit["review_type"] != "model_assisted_independent":
            raise ValueError(
                f"{source_id}: review_type must be model_assisted_independent"
            )
        if audit["human_certified"] is not False:
            raise ValueError(f"{source_id}: model audit cannot claim human certification")
        if audit["decision"] not in {"accept", "hold_for_source_repair"}:
            raise ValueError(f"{source_id}: invalid independent review decision")
        reason_codes = audit["reason_codes"]
        if (
            not isinstance(reason_codes, list)
            or not reason_codes
            or len(reason_codes) != len(set(reason_codes))
            or not all(isinstance(value, str) and value for value in reason_codes)
        ):
            raise ValueError(f"{source_id}: reason_codes must be unique non-empty strings")
        if audit["source_accepted"] not in (True, False):
            raise ValueError(f"{source_id}: source_accepted must be boolean")
        expected_acceptance = audit["decision"] == "accept"
        if audit["source_accepted"] is not expected_acceptance:
            raise ValueError(f"{source_id}: source_accepted disagrees with decision")
        decision = decisions_by_id[source_id]
        if decision["source_hash"] != source["source_hash"]:
            raise ValueError(f"{source_id}: independent audit source hash drifted")
        for field in ("decision", "reason_codes"):
            if decision[field] != audit[field]:
                raise ValueError(
                    f"{source_id}: ledger {field} disagrees with bound audit artifact"
                )

    corrections = ledger["qualifier_corrections"]
    if not isinstance(corrections, list):
        raise ValueError("qualifier_corrections must be a list")
    corrected_counts = {
        row["source_id"]: len(normalize_descriptors(row)) for row in source_rows
    }
    seen_corrections: set[str] = set()
    expected_correction_keys = {
        "source_id",
        "source_hash",
        "audit_complete",
        "expected_old_descriptor_sha256",
        "corrected_protected_qualifiers",
        "corrected_descriptor_sha256",
    }
    for correction in corrections:
        if not isinstance(correction, dict) or set(correction) != expected_correction_keys:
            raise ValueError("qualifier correction has unexpected or missing fields")
        source_id = correction["source_id"]
        if source_id in seen_corrections or source_id not in source_by_id:
            raise ValueError("qualifier correction has a duplicate or unknown source_id")
        seen_corrections.add(source_id)
        source = source_by_id[source_id]
        if correction["source_hash"] != source["source_hash"]:
            raise ValueError(f"{source_id}: qualifier correction source hash drifted")
        if correction["audit_complete"] is not True:
            raise ValueError(f"{source_id}: qualifier correction is not audited")
        old_hashes = descriptor_hashes(normalize_descriptors(source))
        if correction["expected_old_descriptor_sha256"] != old_hashes:
            raise ValueError(f"{source_id}: pre-correction qualifier hashes drifted")
        corrected = correction["corrected_protected_qualifiers"]
        if (
            not isinstance(corrected, list)
            or not all(isinstance(value, str) and value.strip() for value in corrected)
            or corrected != [value.strip() for value in corrected]
        ):
            raise ValueError(f"{source_id}: corrected qualifier list is invalid")
        corrected_hashes = descriptor_hashes(corrected)
        if correction["corrected_descriptor_sha256"] != corrected_hashes:
            raise ValueError(f"{source_id}: corrected qualifier hashes drifted")
        if len(corrected) != len(set(corrected)):
            raise ValueError(f"{source_id}: corrected qualifiers must be unique")
        response = source["original_response"]
        if not isinstance(response, str) or not response:
            raise ValueError(f"{source_id}: original_response must be non-empty")
        if any(descriptor not in response for descriptor in corrected):
            raise ValueError(
                f"{source_id}: every corrected qualifier must be an exact "
                "case-sensitive source substring"
            )
        corrected_counts[source_id] = len(corrected)

    if seen_corrections != backup_ids:
        raise ValueError(
            "private metadata ledger must contain exactly one qualifier correction "
            "for every frozen backup"
        )

    if ledger["audit_complete"] is not True:
        raise RuntimeError("metadata_audit_incomplete")
    if not all(audit["audit_complete"] is True for audit in audits_by_id.values()):
        raise RuntimeError("backup_source_audit_incomplete")
    accepted_ids = {
        source_id
        for source_id, audit in audits_by_id.items()
        if audit["source_accepted"] is True
    }
    held_ids = set(audits_by_id) - accepted_ids
    expected_held_ids = set(config["source_pool"]["expected_hold_source_ids"])
    if held_ids != expected_held_ids:
        raise ValueError("independent-review hold set drifted from the frozen config")
    return corrected_counts, accepted_ids


def midrank_percentile(value: int, values: Sequence[int]) -> float:
    """Return the frozen one-based midrank, requiring candidate inclusion."""
    if not values:
        raise ValueError("cannot compute a midrank from an empty reference pool")
    below = sum(candidate < value for candidate in values)
    equal = sum(candidate == value for candidate in values)
    if equal < 1:
        raise ValueError("candidate must be included in its midrank reference pool")
    result = (below + (equal + 1) / 2) / len(values)
    if not (0 < result <= 1):
        raise ValueError("candidate-included midrank fell outside (0, 1]")
    return result


def candidate_features(
    row: Mapping[str, Any],
    reference_rows: Sequence[Mapping[str, Any]],
    corrected_counts: Mapping[str, int],
) -> tuple[float, float, float]:
    if row["source_id"] not in {candidate["source_id"] for candidate in reference_rows}:
        raise ValueError("candidate is absent from its feature reference pool")
    return (
        midrank_percentile(
            int(row["word_count"]),
            [int(candidate["word_count"]) for candidate in reference_rows],
        ),
        midrank_percentile(
            int(row["sentence_count"]),
            [int(candidate["sentence_count"]) for candidate in reference_rows],
        ),
        midrank_percentile(
            int(corrected_counts[row["source_id"]]),
            [int(corrected_counts[candidate["source_id"]]) for candidate in reference_rows],
        ),
    )


def squared_distance(features: Sequence[float], target: Sequence[float]) -> float:
    if len(features) != len(target):
        raise ValueError("feature and target dimensions differ")
    return sum((float(value) - float(expected)) ** 2 for value, expected in zip(features, target))


def mapping_payload(mapping: Mapping[str, str]) -> list[dict[str, str]]:
    return [
        {"failed_source_id": failed, "replacement_source_id": mapping[failed]}
        for failed in sorted(mapping)
    ]


def mapping_sha256(mapping: Mapping[str, str]) -> str:
    return sha256_text(canonical_json(mapping_payload(mapping)))


def assignment_input_sha256(
    *,
    config: Mapping[str, Any],
    slots: Sequence[Mapping[str, Any]],
    candidates: Sequence[Mapping[str, Any]],
    features_by_id: Mapping[str, Sequence[float]],
) -> str:
    """Bind every public-safe target and corrected candidate feature."""
    payload = {
        "method": {
            "seed": config["seed"],
            "feature_names": list(config["features"]["names"]),
            "reference_pool": config["features"]["reference_pool"],
            "distance": config["features"]["distance"],
            "distance_round_digits": config["features"]["distance_round_digits"],
            "assignment": config["assignment"]["method"],
            "tie_breaker": config["assignment"]["tie_breaker"],
            "key_namespace": config["assignment"]["key_namespace"],
            "same_dataset_required": config["assignment"]["same_dataset_required"],
        },
        "slots": [
            {
                "source_id": row["source_id"],
                "source_hash": row["source_hash"],
                "dataset": row["dataset"],
                "selection_target": [float(value) for value in row["selection_target"]],
            }
            for row in sorted(slots, key=lambda item: str(item["source_id"]))
        ],
        "candidates": [
            {
                "source_id": row["source_id"],
                "source_hash": row["source_hash"],
                "dataset": row["dataset"],
                "features": [
                    round(float(value), 12)
                    for value in features_by_id[row["source_id"]]
                ],
            }
            for row in sorted(candidates, key=lambda item: str(item["source_id"]))
        ],
    }
    return sha256_text(canonical_json(payload))


def solve_dataset_assignment(
    *,
    dataset: str,
    slots: Sequence[Mapping[str, Any]],
    candidates: Sequence[Mapping[str, Any]],
    features_by_id: Mapping[str, Sequence[float]],
    seed: int,
    namespace: str,
    round_digits: int,
) -> tuple[dict[str, str], dict[tuple[str, str], float], float, str]:
    ordered_slots = sorted(slots, key=lambda row: str(row["source_id"]))
    ordered_candidates = sorted(candidates, key=lambda row: str(row["source_id"]))
    if len(ordered_candidates) < len(ordered_slots):
        raise ValueError(f"{dataset}: too few accepted unused backups")
    edge_costs = {
        (slot["source_id"], candidate["source_id"]): round(
            squared_distance(features_by_id[candidate["source_id"]], slot["selection_target"]),
            round_digits,
        )
        for slot in ordered_slots
        for candidate in ordered_candidates
    }
    feasible: list[tuple[float, str, dict[str, str]]] = []
    for replacements in itertools.permutations(ordered_candidates, len(ordered_slots)):
        mapping = {
            slot["source_id"]: candidate["source_id"]
            for slot, candidate in zip(ordered_slots, replacements, strict=True)
        }
        total = round(
            sum(edge_costs[(failed, replacement)] for failed, replacement in mapping.items()),
            round_digits,
        )
        canonical = canonical_json(mapping_payload(mapping))
        tie_break = stable_hash(seed, namespace, dataset, canonical)
        feasible.append((total, tie_break, mapping))
    total, tie_break, chosen = min(feasible, key=lambda item: (item[0], item[1]))
    return chosen, edge_costs, total, tie_break


def build_verified_plan(
    *,
    config: Mapping[str, Any],
    source_rows: Sequence[dict[str, Any]],
    backups: Sequence[dict[str, Any]],
    slots: Sequence[dict[str, Any]],
    frozen_selected_ids: set[str],
    corrected_counts: Mapping[str, int],
    audited_accepted_backup_ids: set[str],
    bindings: Mapping[str, str],
) -> dict[str, Any]:
    source = config["source_pool"]
    requirements = source["acceptance_requirements"]
    used_ids = set(source["used_backup_source_ids"])
    if used_ids & frozen_selected_ids:
        raise ValueError("used backup list overlaps the frozen selected slots")
    candidates = [
        row
        for row in backups
        if row["source_id"] in audited_accepted_backup_ids
        and row["source_id"] not in used_ids
        and row["source_id"] not in frozen_selected_ids
        and accepted_by_frozen_review(row, requirements)
    ]
    expected_by_dataset = source["expected_accepted_unused_backups_by_dataset"]
    candidate_counts = Counter(row["dataset"] for row in candidates)
    if any(
        candidate_counts[dataset] != int(expected_by_dataset[dataset])
        for dataset in source["datasets"]
    ):
        raise RuntimeError("accepted_backup_count_not_frozen")

    frozen_core_rows = [
        row
        for row in source_rows
        if row["selection_role"] == source["core_role"]
    ]
    features_by_id: dict[str, tuple[float, float, float]] = {}
    for candidate in candidates:
        reference = [
            row
            for row in frozen_core_rows
            if row["dataset"] == candidate["dataset"]
        ] + [candidate]
        features_by_id[candidate["source_id"]] = candidate_features(
            candidate, reference, corrected_counts
        )
    actual_assignment_input_hash = assignment_input_sha256(
        config=config,
        slots=slots,
        candidates=candidates,
        features_by_id=features_by_id,
    )

    full_mapping: dict[str, str] = {}
    full_edge_costs: dict[tuple[str, str], float] = {}
    dataset_summaries: dict[str, dict[str, Any]] = {}
    for dataset in source["datasets"]:
        dataset_slots = [row for row in slots if row["dataset"] == dataset]
        if not dataset_slots:
            continue
        dataset_candidates = [row for row in candidates if row["dataset"] == dataset]
        mapping, edge_costs, total, tie_break = solve_dataset_assignment(
            dataset=dataset,
            slots=dataset_slots,
            candidates=dataset_candidates,
            features_by_id=features_by_id,
            seed=int(config["seed"]),
            namespace=str(config["assignment"]["key_namespace"]),
            round_digits=int(config["features"]["distance_round_digits"]),
        )
        full_mapping.update(mapping)
        full_edge_costs.update(edge_costs)
        dataset_summaries[dataset] = {
            "failed_slots": len(dataset_slots),
            "accepted_unused_backups": len(dataset_candidates),
            "minimum_total_squared_distance": total,
            "winning_full_mapping_tie_break_sha256": tie_break,
        }

    expected_ids = set(config["failed_slots"]["expected_source_ids"])
    if set(full_mapping) != expected_ids or len(set(full_mapping.values())) != len(full_mapping):
        raise ValueError("global assignment did not cover failed slots one-to-one")
    for failed, replacement in full_mapping.items():
        slot = next(row for row in slots if row["source_id"] == failed)
        candidate = next(row for row in candidates if row["source_id"] == replacement)
        if slot["dataset"] != candidate["dataset"]:
            raise ValueError("global assignment crossed datasets")

    actual_mapping_hash = mapping_sha256(full_mapping)
    expected = config["expected_mapping"]
    mapping_is_frozen = expected["audit_complete"] is True
    if mapping_is_frozen:
        expected_mapping = expected.get("failed_to_replacement")
        if expected_mapping != full_mapping:
            raise ValueError("computed replacement mapping drifted from the frozen mapping")
        if expected.get("mapping_sha256") != actual_mapping_hash:
            raise ValueError("computed replacement mapping hash drifted")
        if expected.get("assignment_input_sha256") != actual_assignment_input_hash:
            raise ValueError("computed assignment-input hash drifted")

    preserved = config["assignment"]["preserved_slot_fields"]
    slot_by_id = {row["source_id"]: row for row in slots}
    candidate_by_id = {row["source_id"]: row for row in candidates}
    assignments = []
    for failed, replacement in sorted(
        full_mapping.items(), key=lambda item: int(slot_by_id[item[0]]["generation_order"])
    ):
        slot = slot_by_id[failed]
        candidate = candidate_by_id[replacement]
        assignments.append(
            {
                "failed_source_id": failed,
                "failed_source_hash": slot["source_hash"],
                "replacement_source_id": replacement,
                "replacement_source_hash": candidate["source_hash"],
                "dataset": slot["dataset"],
                "replacement_features": [
                    round(value, 12) for value in features_by_id[replacement]
                ],
                "squared_distance_to_slot_target": full_edge_costs[(failed, replacement)],
                "preserved_slot": {field: slot[field] for field in preserved},
            }
        )

    generation_authorized = False
    return {
        "schema_version": OUTPUT_SCHEMA,
        "artifact_role": "public_text_free_replacement_plan",
        "plan_revision": config["plan_revision"],
        "status": "verified_plan" if mapping_is_frozen else "mapping_freeze_pending",
        "reason_codes": [] if mapping_is_frozen else ["expected_mapping_not_frozen"],
        "method": {
            "same_dataset": True,
            "features": list(config["features"]["names"]),
            "reference_pool": config["features"]["reference_pool"],
            "distance": config["features"]["distance"],
            "assignment": config["assignment"]["method"],
            "full_mapping_hash_tie_break": True,
        },
        "counts": {
            "failed_slots": len(slots),
            "accepted_unused_backups": len(candidates),
            "planned_replacements": len(assignments),
        },
        "dataset_assignment_summary": dataset_summaries,
        "mapping_sha256": actual_mapping_hash,
        "assignment_input_sha256": actual_assignment_input_hash,
        "assignments": assignments,
        "artifact_bindings": dict(bindings),
        "authorization": {
            "replacement_generation": generation_authorized,
            "activation_extraction": False,
            "probe_fitting": False,
            "sdt_training": False,
        },
        "privacy": {
            "source_or_rewrite_text_included": False,
            "qualifier_text_included": False,
        },
        "review_provenance": {
            "review_type": "model_assisted_independent",
            "human_certified": False,
            "private_ledger_validated": True,
        },
    }


def build_plan(
    *,
    config_path: Path = DEFAULT_CONFIG,
    source_pool_path: Path = DEFAULT_SOURCE_POOL,
    frozen_slots_path: Path = DEFAULT_FROZEN_SLOTS,
    freeze_manifest_path: Path = DEFAULT_FREEZE_MANIFEST,
    validator_path: Path = DEFAULT_VALIDATOR,
    ledger_path: Path = DEFAULT_LEDGER,
    audit_artifact_path: Path = DEFAULT_AUDIT_ARTIFACT,
) -> dict[str, Any]:
    config, config_raw = read_json_object_bytes(config_path)
    validate_config(config)
    source_rows, source_raw = read_jsonl_bytes(source_pool_path)
    frozen_rows, frozen_raw = read_jsonl_bytes(frozen_slots_path)
    freeze_manifest, freeze_manifest_raw = read_json_object_bytes(
        freeze_manifest_path
    )
    validator, validator_raw = read_json_object_bytes(validator_path)

    source_sha = validate_bound_bytes(
        source_raw, config["source_pool"]["expected_sha256"], "source pool"
    )
    frozen_sha = validate_bound_bytes(
        frozen_raw,
        config["failed_slots"]["frozen_slots_expected_sha256"],
        "frozen v4 slots",
    )
    freeze_manifest_sha = validate_bound_bytes(
        freeze_manifest_raw,
        config["failed_slots"]["freeze_manifest_expected_sha256"],
        "private v4 freeze manifest",
    )
    if freeze_manifest.get("source_set_revision") != "v4":
        raise ValueError("private freeze manifest must bind source-set revision v4")
    if freeze_manifest.get("frozen_sources_sha256") != frozen_sha:
        raise ValueError("private freeze manifest does not bind frozen v4 slots")
    if freeze_manifest.get("source_file_sha256") != source_sha:
        raise ValueError("private freeze manifest does not bind the source pool")
    expected_frozen_count = int(config["failed_slots"]["expected_total_frozen_slots"])
    if (
        freeze_manifest.get("source_count") != expected_frozen_count
        or len(frozen_rows) != expected_frozen_count
    ):
        raise ValueError("private freeze manifest must bind the complete v4 grid")
    correction_provenance = freeze_manifest.get("reviewer_metadata_corrections")
    if (
        not isinstance(correction_provenance, dict)
        or correction_provenance.get("writer_visible_artifacts_unchanged") is not True
    ):
        raise ValueError("private freeze manifest lacks correction provenance")
    validator_sha = validate_bound_bytes(
        validator_raw,
        config["failed_slots"]["post_repair_validator_expected_sha256"],
        "post-repair validator",
    )
    source_by_id, backups = validate_source_pool(source_rows, config)
    slots, frozen_selected_ids = failed_slot_rows(
        frozen_rows, validator, config
    )
    bindings = {
        "config_sha256": sha256_bytes(config_raw),
        "source_pool_sha256": source_sha,
        "frozen_slots_sha256": frozen_sha,
        "v4_freeze_manifest_sha256": freeze_manifest_sha,
        "post_repair_validator_sha256": validator_sha,
    }

    ledger_config = config["metadata_correction_ledger"]
    expected_ledger_sha = ledger_config.get("expected_sha256")
    pending_reasons: list[str] = []
    if expected_ledger_sha is None:
        pending_reasons.append("private_metadata_ledger_hash_not_frozen")
    elif not is_sha256(expected_ledger_sha):
        raise ValueError("private metadata ledger expected SHA-256 is invalid")
    expected_mapping = config["expected_mapping"]
    mapping_is_frozen = expected_mapping["audit_complete"] is True
    if not Path(ledger_path).exists():
        pending_reasons.append("private_metadata_ledger_missing")
    if pending_reasons:
        if not mapping_is_frozen:
            pending_reasons.append("expected_mapping_not_frozen")
        return audit_pending_artifact(
            config=config,
            reason_codes=pending_reasons,
            config_sha256=bindings["config_sha256"],
            source_pool_sha256=source_sha,
            frozen_slots_sha256=frozen_sha,
            freeze_manifest_sha256=freeze_manifest_sha,
            validator_sha256=validator_sha,
            failed_slots=slots,
        )

    ledger, ledger_raw = read_json_object_bytes(ledger_path)
    ledger_sha = validate_bound_bytes(
        ledger_raw, expected_ledger_sha, "private metadata ledger"
    )
    if not Path(audit_artifact_path).exists():
        return audit_pending_artifact(
            config=config,
            reason_codes=["private_independent_audit_artifact_missing"],
            config_sha256=bindings["config_sha256"],
            source_pool_sha256=source_sha,
            frozen_slots_sha256=frozen_sha,
            freeze_manifest_sha256=freeze_manifest_sha,
            validator_sha256=validator_sha,
            failed_slots=slots,
            ledger_sha256=ledger_sha,
        )
    audit_artifact, audit_artifact_raw = read_json_object_bytes(audit_artifact_path)
    audit_artifact_sha = sha256_bytes(audit_artifact_raw)
    try:
        corrected_counts, accepted_backup_ids = validate_and_apply_ledger(
            ledger=ledger,
            source_rows=source_rows,
            source_by_id=source_by_id,
            backup_rows=backups,
            source_pool_sha256=source_sha,
            config=config,
            audit_artifact=audit_artifact,
            audit_artifact_sha256=audit_artifact_sha,
            audit_artifact_filename=Path(audit_artifact_path).name,
        )
        corrected_counts = apply_frozen_core_qualifier_counts(
            corrected_counts,
            frozen_rows,
            source_by_id,
            core_role=str(config["source_pool"]["core_role"]),
        )
        bindings["private_metadata_ledger_sha256"] = ledger_sha
        bindings["private_independent_audit_artifact_sha256"] = (
            audit_artifact_sha
        )
        return build_verified_plan(
            config=config,
            source_rows=source_rows,
            backups=backups,
            slots=slots,
            frozen_selected_ids=frozen_selected_ids,
            corrected_counts=corrected_counts,
            audited_accepted_backup_ids=accepted_backup_ids,
            bindings=bindings,
        )
    except RuntimeError as error:
        reason = str(error)
        allowed = {
            "metadata_audit_incomplete",
            "backup_source_audit_incomplete",
            "accepted_backup_count_not_frozen",
            "expected_mapping_not_frozen",
        }
        if reason not in allowed:
            raise
        return audit_pending_artifact(
            config=config,
            reason_codes=[reason],
            config_sha256=bindings["config_sha256"],
            source_pool_sha256=source_sha,
            frozen_slots_sha256=frozen_sha,
            freeze_manifest_sha256=freeze_manifest_sha,
            validator_sha256=validator_sha,
            failed_slots=slots,
            ledger_sha256=ledger_sha,
        )


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--source-pool", type=Path, default=DEFAULT_SOURCE_POOL)
    parser.add_argument("--frozen-slots", type=Path, default=DEFAULT_FROZEN_SLOTS)
    parser.add_argument(
        "--freeze-manifest", type=Path, default=DEFAULT_FREEZE_MANIFEST
    )
    parser.add_argument("--post-repair-validator", type=Path, default=DEFAULT_VALIDATOR)
    parser.add_argument("--metadata-ledger", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument(
        "--independent-audit-artifact",
        type=Path,
        default=DEFAULT_AUDIT_ARTIFACT,
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    plan = build_plan(
        config_path=args.config,
        source_pool_path=args.source_pool,
        frozen_slots_path=args.frozen_slots,
        freeze_manifest_path=args.freeze_manifest,
        validator_path=args.post_repair_validator,
        ledger_path=args.metadata_ledger,
        audit_artifact_path=args.independent_audit_artifact,
    )
    write_json(args.output, plan)
    print(
        json.dumps(
            {
                "status": plan["status"],
                "planned_replacements": plan["counts"]["planned_replacements"],
                "replacement_generation_authorized": plan["authorization"][
                    "replacement_generation"
                ],
                "output": str(args.output),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
