"""Apply exact private text repairs to the completed v3.7 canary.

The public script contains no response text. Replacement fragments and their
reasons live in an ignored private patch file. Every edit is hash-tied to the
prior shared template and the full v3.7 validator is rerun with zero model calls.
"""
from __future__ import annotations

import argparse
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
    run_claude_rewrite_batches as transport,
)
from experiments.diverse_pairs_multilayer_v1.src import (
    run_claude_two_stage_rewrite_v37 as v37,
)


BASE = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = BASE / "configs" / "local_template_repairs_v37.json"
PROTOCOL_VERSION = "local-template-repairs-v3.7"
RUNNER_VERSION = "1.0"


@dataclass(frozen=True)
class Config:
    protocol_version: str
    base_config_path: Path
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
        patch_path=_resolve(raw["patch_path"]),
        output_path=_resolve(raw["output_path"]),
    )
    if config.protocol_version != PROTOCOL_VERSION:
        raise ValueError("Wrong v3.7 local-repair protocol")
    transport.ensure_private_output_dir(config.output_path.parent)
    return config


def apply_template_patch(
    record: dict[str, Any], patch: dict[str, Any]
) -> dict[str, Any]:
    template = str(record["shared_template"])
    if transport.sha256_text(template) != patch["prior_template_sha256"]:
        raise ValueError(f"Prior template hash mismatch for {record['production_slot']}")
    for replacement in patch.get("template_replacements", []):
        old = str(replacement["old"])
        new = str(replacement["new"])
        if old == new or template.count(old) != 1:
            raise ValueError(
                f"Template replacement is not unique for {record['production_slot']}"
            )
        template = template.replace(old, new, 1)
    updated = dict(record)
    updated["shared_template"] = template
    updated["local_repair_lineage"] = {
        "protocol": PROTOCOL_VERSION,
        "prior_template_sha256": patch["prior_template_sha256"],
        "reason": str(patch["reason"]),
        "model_calls": 0,
    }
    return updated


def apply_patches(
    records: Sequence[dict[str, Any]], patches: Sequence[dict[str, Any]]
) -> list[dict[str, Any]]:
    by_slot = {str(item["production_slot"]): item for item in patches}
    if len(by_slot) != len(patches):
        raise ValueError("Duplicate v3.7 repair slot")
    known = {str(record["production_slot"]) for record in records}
    if not set(by_slot).issubset(known):
        raise ValueError("V3.7 patch references an unknown slot")
    return [
        apply_template_patch(record, by_slot[str(record["production_slot"])])
        if str(record["production_slot"]) in by_slot
        else dict(record)
        for record in records
    ]


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    args = parser.parse_args(argv)
    config = load_config(args.config.resolve())
    base_config = v37.load_config(config.base_config_path)
    rows = v37.load_frozen_sources(base_config)
    cue_sets = v37.load_cue_bank(base_config, rows)
    fingerprint = v37._fingerprint(base_config, rows, cue_sets)
    parsed_path = (
        base_config.output_dir
        / "parsed"
        / f"{v37._batch_id(rows)}.json"
    )
    parsed = v37._load_parsed(
        parsed_path,
        fingerprint,
        rows,
        base_config.accepted_legacy_cache_fingerprints,
    )
    if parsed is None:
        raise FileNotFoundError("The v3.7 canary has not completed")
    records = parsed["records"]
    records_sha256 = transport.sha256_bytes(
        json.dumps(records, sort_keys=True).encode("utf-8")
    )
    if parsed["records_sha256"] != records_sha256:
        raise ValueError("V3.7 base records hash mismatch")

    private_patch = json.loads(config.patch_path.read_text(encoding="utf-8"))
    if private_patch.get("protocol_version") != PROTOCOL_VERSION:
        raise ValueError("V3.7 private patch protocol mismatch")
    if private_patch.get("base_records_sha256") != records_sha256:
        raise ValueError("V3.7 private patch is tied to another checkpoint")
    patches = private_patch.get("repairs")
    if not isinstance(patches, list):
        raise ValueError("V3.7 private patch list is invalid")
    patched = apply_patches(records, patches)

    structured = {"templates": [{
        "source_id": record["source_id"],
        "original_response_sha256": record["original_response_sha256"],
        "shared_template": record["shared_template"],
        "not_applicable": False,
        "issues": [],
    } for record in patched]}
    tokenizer = transport.load_pinned_tokenizer(transport.tokenizer_file_hashes())
    validated, corrected = v37.validate_output(
        rows, cue_sets, structured, base_config, tokenizer
    )
    if corrected:
        raise ValueError("Local v3.7 validation must not correct source hashes")
    prior_by_slot = {str(record["production_slot"]): record for record in patched}
    for record in validated:
        prior = prior_by_slot[str(record["production_slot"])]
        if "local_repair_lineage" in prior:
            record["local_repair_lineage"] = prior["local_repair_lineage"]

    output = {
        "runner_version": RUNNER_VERSION,
        "protocol_version": PROTOCOL_VERSION,
        "generation_fingerprint": fingerprint,
        "base_records_sha256": records_sha256,
        "patch_sha256": transport.sha256_file(config.patch_path),
        "records": validated,
        "records_sha256": transport.sha256_bytes(
            json.dumps(validated, sort_keys=True).encode("utf-8")
        ),
        "status_counts": dict(Counter(record["status"] for record in validated)),
        "local_repair_count": len(patches),
        "model_calls": 0,
        "semantic_review": "pending_after_repair",
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
