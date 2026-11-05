#!/usr/bin/env python3
"""Materialize the provider-free data inputs for the probe-guided LoRA canary.

This builder intentionally creates an engineering/post-exposure canary only.
It does not create a new confirmatory test set and it never imports or runs a
model, tokenizer, provider client, or training implementation.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


EXPERIMENT_NAME = "confidence_probe_guided_lora_lambda_canary_20261104_v1"
SCHEMA = "confidence-probe-guided-lora-lambda-canary-data-v1"

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parent / "data"

INPUTS = {
    "probe_train_audit": {
        "path": "experiments/confidence_probe_scaleup_20261104_v1/data_prep/train_920.jsonl",
        "sha256": "b29d12db51ea202d161fbd20d8347e02bf71e186a1afeafbb4cd9e34951e54e3",
        "count": 920,
        "use": "overlap audit only; never emitted or used for LoRA training",
    },
    "lora_train": {
        "path": "experiments/confidence_probe_scaleup_20261104_v1/data_prep/dev_156.jsonl",
        "sha256": "5bea7ef9980ff0e14abc6a8ef5a049461666a14182e5cd6a243694daa3b03154",
        "count": 156,
        "use": "LoRA canary training pairs",
    },
    "lora_dev": {
        "path": "experiments/confidence_probe_scaleup_20261104_v1/data_prep/external_cf3_113.jsonl",
        "sha256": "4e81457ad4ec7b41965f4660ad5013e65b67e9bffd7f19009aa4ac83300d9f01",
        "count": 113,
        "use": "lambda calibration and engineering-quality checks only",
    },
    "probe_internal_test_audit": {
        "path": "experiments/confidence_probe_scaleup_20261104_v1/data_prep/internal_test_193.jsonl",
        "sha256": "26157511a230f3695f25adc530488712607468d2b2cac8a97519d9c7640cd9ff",
        "count": 193,
        "use": "overlap audit only; preserved from LoRA training and dev",
    },
    "cue50": {
        "path": "deliverables/controlled_certainty_probe_2026-10-27/paired_two_versions.csv",
        "sha256": "627d14f8ef8501b7872d93c4fcd07080b77084758bcfd9a06710c577c3a64e0a",
        "count": 50,
        "use": "post-exposure behavioral canary after overlap exclusions",
    },
}

EXPECTED_CUE50_EXCLUSIONS = ("C002", "C018", "C021", "C026")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_question(text: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", text).split()).casefold()


def normalized_question_sha256(text: str) -> str:
    return hashlib.sha256(normalize_question(text).encode("utf-8")).hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def display_path(path: Path) -> str:
    """Use repository-relative paths for real artifacts and absolute temp paths in tests."""
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ValueError(f"{path}:{line_number} is not a JSON object")
            rows.append(row)
    return rows


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def verify_and_load_inputs(repo_root: Path = REPO_ROOT) -> dict[str, list[dict[str, Any]]]:
    loaded: dict[str, list[dict[str, Any]]] = {}
    for name, spec in INPUTS.items():
        path = repo_root / spec["path"]
        if sha256_file(path) != spec["sha256"]:
            raise ValueError(f"input hash mismatch for {name}: {path}")
        rows = load_csv(path) if path.suffix == ".csv" else load_jsonl(path)
        if len(rows) != spec["count"]:
            raise ValueError(
                f"input count mismatch for {name}: expected {spec['count']}, got {len(rows)}"
            )
        loaded[name] = rows
    return loaded


def _require_nonempty(row: dict[str, Any], fields: Iterable[str], label: str) -> None:
    for field in fields:
        if not isinstance(row.get(field), str) or not row[field].strip():
            raise ValueError(f"{label} has missing/empty {field}")


def materialize_pair_row(
    row: dict[str, Any], *, data_role: str, input_name: str
) -> dict[str, Any]:
    _require_nonempty(
        row,
        ("id", "source_id", "question", "confident_response", "hesitant_response"),
        data_role,
    )
    target_longer_role = row.get("target_longer_role")
    if target_longer_role not in {"confident", "hesitant"}:
        raise ValueError(f"{data_role} row {row['id']} has invalid target_longer_role")
    expected_norm_hash = normalized_question_sha256(row["question"])
    if row.get("normalized_question_sha256") != expected_norm_hash:
        raise ValueError(f"{data_role} row {row['id']} has invalid normalized question hash")

    preserved_fields = (
        "id",
        "source_id",
        "group_id",
        "atomic_group_id",
        "question",
        "question_sha256",
        "normalized_question_sha256",
        "confident_response",
        "hesitant_response",
        "target_longer_role",
        "length_bin",
        "task",
        "source_collection",
        "source_dataset",
        "source_dataset_revision",
        "source_file",
        "source_file_row_index",
        "original_record_sha256",
        "document",
        "lane",
        "strict_evidence",
    )
    output = {field: row.get(field) for field in preserved_fields}
    output.update(
        {
            "schema": SCHEMA,
            "data_role": data_role,
            "input_name": input_name,
            "engineering_only": True,
            "confirmatory_status": "post_exposure_not_confirmatory",
        }
    )
    return output


def materialize_cue50_row(row: dict[str, str]) -> dict[str, Any]:
    _require_nonempty(
        row,
        ("pair_id", "source_id", "prompt", "confident_response", "hesitant_response"),
        "behavior_canary",
    )
    mapping = {
        "confident_longer": "confident",
        "hedged_longer": "hesitant",
    }
    if row.get("length_direction") not in mapping:
        raise ValueError(f"Cue50 row {row['pair_id']} has invalid length_direction")
    question = row["prompt"]
    return {
        "schema": SCHEMA,
        "data_role": "behavior_canary",
        "input_name": "cue50",
        "id": row["pair_id"],
        "source_id": row["source_id"],
        "question": question,
        "normalized_question_sha256": normalized_question_sha256(question),
        "confident_response": row["confident_response"],
        "hesitant_response": row["hesitant_response"],
        "target_longer_role": mapping[row["length_direction"]],
        "length_direction": row["length_direction"],
        "length_bin": None,
        "task": row.get("task"),
        "source_collection": "cue50_reference",
        "source_dataset": row.get("dataset"),
        "cue_family": row.get("cue_family"),
        "any_minor_shortcut_concern": row.get("any_minor_shortcut_concern"),
        "review_status": row.get("review_status"),
        "engineering_only": True,
        "confirmatory_status": "post_exposure_not_confirmatory",
    }


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> dict[str, Any]:
    payload = b"".join(canonical_json_bytes(row) for row in rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    return {
        "path": display_path(path),
        "count": len(rows),
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
    }


def _identity_sets(rows: list[dict[str, Any]]) -> dict[str, set[str]]:
    return {
        "source_id": {str(row["source_id"]) for row in rows},
        "normalized_question_sha256": {
            str(row["normalized_question_sha256"]) for row in rows
        },
    }


def assert_pairwise_disjoint(named_rows: dict[str, list[dict[str, Any]]]) -> None:
    names = list(named_rows)
    identities = {name: _identity_sets(rows) for name, rows in named_rows.items()}
    for index, left in enumerate(names):
        for right in names[index + 1 :]:
            for field in ("source_id", "normalized_question_sha256"):
                overlap = identities[left][field] & identities[right][field]
                if overlap:
                    raise ValueError(
                        f"{field} overlap between {left} and {right}: {len(overlap)}"
                    )


def build_outputs(
    output_dir: Path = DEFAULT_OUTPUT_DIR, *, repo_root: Path = REPO_ROOT
) -> dict[str, Any]:
    loaded = verify_and_load_inputs(repo_root)

    train_rows = [
        materialize_pair_row(row, data_role="lora_train", input_name="lora_train")
        for row in loaded["lora_train"]
    ]
    dev_rows = [
        materialize_pair_row(row, data_role="lora_dev", input_name="lora_dev")
        for row in loaded["lora_dev"]
    ]

    audit_question_hashes = {
        normalized_question_sha256(row["question"])
        for name in (
            "probe_train_audit",
            "lora_train",
            "lora_dev",
            "probe_internal_test_audit",
        )
        for row in loaded[name]
    }
    audit_source_ids = {
        str(row["source_id"])
        for name in (
            "probe_train_audit",
            "lora_train",
            "lora_dev",
            "probe_internal_test_audit",
        )
        for row in loaded[name]
    }

    cue50_excluded: list[dict[str, str]] = []
    behavior_rows: list[dict[str, Any]] = []
    for row in loaded["cue50"]:
        question_hash = normalized_question_sha256(row["prompt"])
        reasons: list[str] = []
        if question_hash in audit_question_hashes:
            reasons.append("normalized_question_overlap_with_frozen_probe_collection")
        if row["source_id"] in audit_source_ids:
            reasons.append("source_id_overlap_with_frozen_probe_collection")
        if reasons:
            cue50_excluded.append(
                {
                    "pair_id": row["pair_id"],
                    "source_id": row["source_id"],
                    "reasons": reasons,
                }
            )
        else:
            behavior_rows.append(materialize_cue50_row(row))

    actual_exclusions = tuple(row["pair_id"] for row in cue50_excluded)
    if actual_exclusions != EXPECTED_CUE50_EXCLUSIONS:
        raise ValueError(
            f"Cue50 exclusion mismatch: expected {EXPECTED_CUE50_EXCLUSIONS}, "
            f"got {actual_exclusions}"
        )

    expected_counts = {"lora_train": 156, "lora_dev": 113, "behavior_canary": 46}
    actual_counts = {
        "lora_train": len(train_rows),
        "lora_dev": len(dev_rows),
        "behavior_canary": len(behavior_rows),
    }
    if actual_counts != expected_counts:
        raise ValueError(f"output count mismatch: {actual_counts}")

    assert_pairwise_disjoint(
        {
            "lora_train": train_rows,
            "lora_dev": dev_rows,
            "behavior_canary": behavior_rows,
        }
    )

    artifacts = {
        "lora_train": write_jsonl(output_dir / "lora_train_cf200_156.jsonl", train_rows),
        "lora_dev": write_jsonl(output_dir / "lora_dev_cf3_113.jsonl", dev_rows),
        "behavior_canary": write_jsonl(
            output_dir / "behavior_canary_cue50_46.jsonl", behavior_rows
        ),
    }

    manifest: dict[str, Any] = {
        "schema": SCHEMA,
        "experiment": EXPERIMENT_NAME,
        "created_date": "2026-11-04",
        "status": "provider_free_data_preparation_complete",
        "scope": "engineering lambda canary only",
        "confirmatory_status": "post_exposure_not_confirmatory",
        "limitations": [
            "CF200 and CF3 were previously used in probe development or robustness evaluation.",
            "Cue50 was previously exposed during method development and manual inspection.",
            "CF3 does not have completed human review.",
            "The retained 46-question Cue50 cohort is a behavioral canary, not a fresh final test.",
            "No model, tokenizer, forward pass, provider, LoRA training, or scoring ran in this phase.",
        ],
        "design": {
            "lora_train": "156 strict CF200 confidence pairs",
            "lora_dev": "113 CF3 post-exposure pairs for lambda/stability checks",
            "behavior_canary": "46 Cue50 prompts after frozen-overlap exclusion",
            "preserved_from_lora_training": "internal_test_193.jsonl",
            "lambda_candidates": [0.0, 0.05, 0.1],
        },
        "input_files": {
            name: {
                "path": spec["path"],
                "sha256": spec["sha256"],
                "count": spec["count"],
                "use": spec["use"],
            }
            for name, spec in INPUTS.items()
        },
        "cue50_exclusions": cue50_excluded,
        "artifacts": artifacts,
        "balance": {
            name: {
                "count": len(rows),
                "task": dict(sorted(Counter(row.get("task") for row in rows).items())),
                "target_longer_role": dict(
                    sorted(Counter(row.get("target_longer_role") for row in rows).items())
                ),
                "length_bin": {
                    str(key): value
                    for key, value in sorted(
                        Counter(row.get("length_bin") for row in rows).items(),
                        key=lambda item: str(item[0]),
                    )
                },
            }
            for name, rows in {
                "lora_train": train_rows,
                "lora_dev": dev_rows,
                "behavior_canary": behavior_rows,
            }.items()
        },
        "leakage_checks": {
            "fields": ["source_id", "normalized_question_sha256"],
            "pairwise_output_overlap": 0,
            "status": "PASS",
        },
    }
    manifest_path = output_dir.parent / "DATA_PREPARATION_MANIFEST.json"
    manifest_path.write_bytes(canonical_json_bytes(manifest))
    manifest["manifest"] = {
        "path": display_path(manifest_path),
        "bytes": manifest_path.stat().st_size,
        "sha256": sha256_file(manifest_path),
    }
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    manifest = build_outputs(args.output_dir)
    print(json.dumps(manifest["manifest"], ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
