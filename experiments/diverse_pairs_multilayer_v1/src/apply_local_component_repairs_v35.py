"""Apply audited local edits to a private v3.5 component checkpoint.

The public script contains no response text. Exact replacement fragments live in
an ignored private patch file with hashes tying every edit to its prior record.
No model call is made. The unchanged v3.5 validator rechecks the full batch.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

if __package__ in {None, ""}:  # pragma: no cover
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from experiments.diverse_pairs_multilayer_v1.src import (
    run_claude_component_rewrite_v35 as component,
)
from experiments.diverse_pairs_multilayer_v1.src import (
    run_claude_rewrite_batches as transport,
)


BASE = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = BASE / "configs" / "local_component_repairs_v35.json"
PROTOCOL_VERSION = "local-component-repairs-v3.5"
RUNNER_VERSION = "1.0"


@dataclass(frozen=True)
class Config:
    protocol_version: str
    base_config_path: Path
    input_path: Path
    patch_path: Path
    output_path: Path


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _resolve(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else BASE / path


def load_config(path: Path) -> Config:
    raw = json.loads(path.read_text(encoding="utf-8"))
    config = Config(
        protocol_version=str(raw["protocol_version"]),
        base_config_path=_resolve(raw["base_config_path"]),
        input_path=_resolve(raw["input_path"]),
        patch_path=_resolve(raw["patch_path"]),
        output_path=_resolve(raw["output_path"]),
    )
    if config.protocol_version != PROTOCOL_VERSION:
        raise ValueError("Wrong local component-repair protocol")
    transport.ensure_private_output_dir(config.output_path.parent)
    return config


def component_sha256(record: dict[str, Any]) -> str:
    value = {
        "shared_template": record["shared_template"],
        "confident_cues": record["confident_cues"],
        "hedged_cues": record["hedged_cues"],
    }
    return transport.sha256_bytes(json.dumps(value, sort_keys=True).encode())


def apply_patch_to_record(
    record: dict[str, Any], patch: dict[str, Any]
) -> dict[str, Any]:
    if component_sha256(record) != patch["prior_component_sha256"]:
        raise ValueError(f"Prior component hash mismatch for {record['production_slot']}")
    updated = dict(record)
    template = str(updated["shared_template"])
    for replacement in patch.get("template_replacements", []):
        old = str(replacement["old"])
        new = str(replacement["new"])
        if old == new or template.count(old) != 1:
            raise ValueError(
                f"Replacement is not unique for {record['production_slot']}"
            )
        template = template.replace(old, new, 1)
    updated["shared_template"] = template
    for field in ("confident_cues", "hedged_cues"):
        if field in patch:
            value = patch[field]
            if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
                raise ValueError(f"Invalid {field} patch for {record['production_slot']}")
            updated[field] = value
    updated["local_repair_lineage"] = {
        "protocol": PROTOCOL_VERSION,
        "prior_component_sha256": patch["prior_component_sha256"],
        "reason": str(patch["reason"]),
        "model_calls": 0,
    }
    return updated


def apply_patches(
    records: Sequence[dict[str, Any]], patches: Sequence[dict[str, Any]]
) -> list[dict[str, Any]]:
    patch_by_slot = {str(patch["production_slot"]): patch for patch in patches}
    if len(patch_by_slot) != len(patches):
        raise ValueError("Duplicate local repair slot")
    known_slots = {str(record["production_slot"]) for record in records}
    if not set(patch_by_slot).issubset(known_slots):
        raise ValueError("Local repair references an unknown slot")
    return [
        apply_patch_to_record(record, patch_by_slot[str(record["production_slot"])])
        if str(record["production_slot"]) in patch_by_slot
        else dict(record)
        for record in records
    ]


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    args = parser.parse_args(argv)
    config = load_config(args.config.resolve())
    base_config = component.load_config(config.base_config_path)
    rows, _ = component.load_sources(base_config)
    first_batch = component.make_batches(rows)[0]
    source_ids = [row["source_id"] for row in first_batch]

    original = json.loads(config.input_path.read_text(encoding="utf-8"))
    records = original.get("records")
    if not isinstance(records, list) or [record["source_id"] for record in records] != source_ids:
        raise ValueError("Local repair input does not match the frozen first batch")
    records_sha256 = transport.sha256_bytes(json.dumps(records, sort_keys=True).encode())
    if original.get("records_sha256") != records_sha256:
        raise ValueError("Local repair input record hash mismatch")

    private_patch = json.loads(config.patch_path.read_text(encoding="utf-8"))
    if private_patch.get("protocol_version") != PROTOCOL_VERSION:
        raise ValueError("Private patch protocol mismatch")
    if private_patch.get("base_records_sha256") != records_sha256:
        raise ValueError("Private patch is not tied to this input checkpoint")
    patches = private_patch.get("repairs")
    if not isinstance(patches, list):
        raise ValueError("Private repair list is invalid")
    patched = apply_patches(records, patches)

    structured = {"pairs": [{
        "source_id": record["source_id"],
        "original_response_sha256": record["original_response_sha256"],
        "shared_template": record["shared_template"],
        "confident_cues": record["confident_cues"],
        "hedged_cues": record["hedged_cues"],
        "not_applicable": False,
        "issues": [],
    } for record in patched]}
    tokenizer = transport.load_pinned_tokenizer(transport.tokenizer_file_hashes())
    validated, corrected = component.validate_output(
        first_batch, structured, base_config, tokenizer
    )
    if corrected:
        raise ValueError("Local validation must not correct source hashes")
    previous = {str(record["production_slot"]): record for record in patched}
    for record in validated:
        prior = previous[str(record["production_slot"])]
        if "repair_lineage" in prior:
            record["repair_lineage"] = prior["repair_lineage"]
        if "local_repair_lineage" in prior:
            record["local_repair_lineage"] = prior["local_repair_lineage"]

    output = {
        "runner_version": RUNNER_VERSION,
        "protocol_version": PROTOCOL_VERSION,
        "base_records_sha256": records_sha256,
        "patch_sha256": transport.sha256_file(config.patch_path),
        "records": validated,
        "records_sha256": transport.sha256_bytes(
            json.dumps(validated, sort_keys=True).encode()
        ),
        "status_counts": dict(Counter(record["status"] for record in validated)),
        "local_repair_count": len(patches),
        "model_calls": 0,
        "semantic_review": "pending",
        "completed_at": utc_now(),
    }
    transport.atomic_write_json(config.output_path, output)
    print(json.dumps({
        "records": len(validated),
        "local_repairs": len(patches),
        "status_counts": output["status_counts"],
        "semantic_review": output["semantic_review"],
    }))
    return 0 if output["status_counts"] == {"accepted": len(validated)} else 1


if __name__ == "__main__":
    raise SystemExit(main())
