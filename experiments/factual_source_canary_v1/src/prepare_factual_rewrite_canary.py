#!/usr/bin/env python3
"""Freeze a deterministic 12-source factual confident/hesitant rewrite canary.

This script prepares source records and writer prompts only. It does not call a
rewrite model, inspect activations, fit a probe, or evaluate any model output.
Full source text and prompts are written only below ``private_data/``.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Sequence


ROOT = Path(__file__).resolve().parents[1]
PRIVATE_ROOT = ROOT / "private_data"
DEFAULT_CONFIG = ROOT / "configs" / "rewrite_canary_v1.json"
DEFAULT_SOURCE = (
    PRIVATE_ROOT / "expanded_pool_v2" / "selected_core_sources_v1.jsonl"
)
DEFAULT_PUBLIC_SOURCE = ROOT / "results" / "selected_core_sources_v1_manifest.jsonl"
DEFAULT_PRIVATE_OUTPUT = PRIVATE_ROOT / "rewrite_canary_v1"
DEFAULT_PUBLIC_MANIFEST = ROOT / "results" / "rewrite_canary_v1_source_manifest.jsonl"
DEFAULT_PUBLIC_SUMMARY = ROOT / "results" / "rewrite_canary_v1_freeze_summary.json"

DESIGN: dict[str, Any]
VERSION: str
SEED: int
DATASETS: tuple[str, ...]
PROFILES: tuple[tuple[str, tuple[float, float, float]], ...]
CUE_FAMILY_TARGETS: tuple[tuple[str, int], ...]
LENGTH_DIRECTIONS: tuple[str, ...]
DRAFT_ORDERS: tuple[str, ...]
BATCH_LAYOUT: tuple[tuple[tuple[str, str], ...], ...]

PRIVATE_TEXT_FIELDS = {
    "prompt",
    "question",
    "original_response",
    "evidence",
    "source_locator",
    "protected_qualifiers",
    "protected_spans",
    "metadata",
    "model_review_notes",
    "source_repair_log",
}


def configure(config: dict[str, Any]) -> None:
    """Load and validate the frozen design into module-level constants."""
    global DESIGN, VERSION, SEED, DATASETS, PROFILES
    global CUE_FAMILY_TARGETS, LENGTH_DIRECTIONS, DRAFT_ORDERS, BATCH_LAYOUT

    selection = config["selection"]
    profiles = tuple(
        (str(item["name"]), tuple(float(value) for value in item["target"]))
        for item in selection["profiles"]
    )
    if any(len(target) != 3 for _, target in profiles):
        raise ValueError("each selection profile must have three target values")
    cue_targets = tuple(
        (str(item["name"]), int(item["count"]))
        for item in config["cue_assignment"]["target_counts"]
    )
    layout = tuple(
        tuple((str(cell[0]), str(cell[1])) for cell in batch)
        for batch in config["batching"]["layout"]
    )
    datasets = tuple(str(value) for value in selection["datasets"])
    directions = tuple(str(value) for value in config["length_assignment"]["directions"])
    draft_orders = tuple(
        str(value) for value in config["draft_order_assignment"]["orders"]
    )
    selected_count = len(datasets) * len(profiles)
    if sum(count for _, count in cue_targets) != selected_count:
        raise ValueError("cue-family target counts must cover every selected source")
    if len(directions) != 2:
        raise ValueError("exactly two length directions are required")
    if len(draft_orders) != 2:
        raise ValueError("exactly two draft orders are required")
    if sum(len(batch) for batch in layout) != selected_count:
        raise ValueError("batch layout must cover every selected source exactly once")
    if any(len(batch) != int(config["batching"]["batch_size"]) for batch in layout):
        raise ValueError("batch layout does not match configured batch size")

    DESIGN = config
    VERSION = str(config["version"])
    SEED = int(config["seed"])
    DATASETS = datasets
    PROFILES = profiles
    CUE_FAMILY_TARGETS = cue_targets
    LENGTH_DIRECTIONS = directions
    DRAFT_ORDERS = draft_orders
    BATCH_LAYOUT = layout


def load_config(path: Path) -> dict[str, Any]:
    config = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(config, dict):
        raise ValueError(f"{path}: expected a JSON object")
    configure(config)
    return config


load_config(DEFAULT_CONFIG)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument(
        "--public-source-manifest", type=Path, default=DEFAULT_PUBLIC_SOURCE
    )
    parser.add_argument("--private-output-dir", type=Path, default=DEFAULT_PRIVATE_OUTPUT)
    parser.add_argument("--public-manifest", type=Path, default=DEFAULT_PUBLIC_MANIFEST)
    parser.add_argument("--public-summary", type=Path, default=DEFAULT_PUBLIC_SUMMARY)
    return parser.parse_args(argv)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        if not isinstance(row, dict):
            raise ValueError(f"{path}:{line_number}: expected an object")
        rows.append(row)
    return rows


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stable_hash(*parts: object) -> str:
    return hashlib.sha256("|".join(str(part) for part in parts).encode("utf-8")).hexdigest()


def require_private_output(path: Path, private_root: Path = PRIVATE_ROOT) -> Path:
    output = path.resolve()
    root = private_root.resolve()
    if output != root and root not in output.parents:
        raise ValueError(f"Private rewrite output must stay below {root}")
    return output


def midrank_percentile(value: int, values: Sequence[int]) -> float:
    """Return average 1-based rank divided by n, with tied values sharing a rank."""
    if not values:
        raise ValueError("cannot compute a mid-rank for an empty sequence")
    below = sum(candidate < value for candidate in values)
    equal = sum(candidate == value for candidate in values)
    if equal == 0:
        raise ValueError(f"value {value} is absent from the reference values")
    return (below + (equal + 1) / 2) / len(values)


def qualifier_descriptors(row: dict[str, Any]) -> list[str]:
    raw = row.get("protected_qualifiers") or []
    if not isinstance(raw, list) or not all(isinstance(item, str) for item in raw):
        raise ValueError(f"{row.get('source_id')}: protected_qualifiers must be strings")
    return [item.strip() for item in raw if item.strip()]


def literal_protected_spans(response: str, descriptors: Sequence[str]) -> list[str]:
    """Recover only descriptor strings that occur literally in the source response.

    Reviewers sometimes recorded semantic paraphrases as protected qualifiers.
    Those remain useful guidance, but they are not represented as exact spans.
    """
    spans: list[str] = []
    seen: set[str] = set()
    for descriptor in descriptors:
        match = re.search(re.escape(descriptor), response, flags=re.IGNORECASE)
        if match is None:
            continue
        span = response[match.start() : match.end()]
        if span not in seen:
            seen.add(span)
            spans.append(span)
    return spans


def feature_vector(row: dict[str, Any], dataset_rows: Sequence[dict[str, Any]]) -> tuple[float, float, float]:
    words = [int(candidate["word_count"]) for candidate in dataset_rows]
    sentences = [int(candidate["sentence_count"]) for candidate in dataset_rows]
    qualifier_counts = [len(qualifier_descriptors(candidate)) for candidate in dataset_rows]
    return (
        midrank_percentile(int(row["word_count"]), words),
        midrank_percentile(int(row["sentence_count"]), sentences),
        midrank_percentile(len(qualifier_descriptors(row)), qualifier_counts),
    )


def squared_distance(features: Sequence[float], target: Sequence[float]) -> float:
    return sum((feature - expected) ** 2 for feature, expected in zip(features, target))


def select_canary_sources(rows: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    """Select four metadata-balanced core records per dataset without model outcomes."""
    selected: list[dict[str, Any]] = []
    expected_core = int(DESIGN["selection"]["expected_core_per_dataset"])
    eligible_role = str(DESIGN["selection"]["eligible_role"])
    for dataset in DATASETS:
        pool = [
            dict(row)
            for row in rows
            if row.get("dataset") == dataset
            and row.get("selection_role") == eligible_role
        ]
        if len(pool) != expected_core:
            raise ValueError(
                f"{dataset}: expected {expected_core} frozen {eligible_role} records, "
                f"found {len(pool)}"
            )
        if len({row.get("source_id") for row in pool}) != expected_core:
            raise ValueError(f"{dataset}: duplicate core source IDs")

        used: set[str] = set()
        for profile, target in PROFILES:
            candidates = [row for row in pool if row["source_id"] not in used]

            def key(row: dict[str, Any]) -> tuple[float, str]:
                features = feature_vector(row, pool)
                distance = round(
                    squared_distance(features, target),
                    int(DESIGN["selection"]["distance_round_digits"]),
                )
                tie_breaker = stable_hash(
                    SEED,
                    DESIGN["selection"]["key_namespace"],
                    dataset,
                    profile,
                    row["source_id"],
                )
                return distance, tie_breaker

            chosen = min(candidates, key=key)
            chosen["profile"] = profile
            chosen["selection_features"] = feature_vector(chosen, pool)
            chosen["selection_target"] = target
            chosen["selection_distance"] = key(chosen)[0]
            selected.append(chosen)
            used.add(chosen["source_id"])
    return selected


def verify_against_public_manifest(
    selected: Sequence[dict[str, Any]], public_rows: Sequence[dict[str, Any]]
) -> None:
    public_by_id = {row.get("source_id"): row for row in public_rows}
    if len(public_by_id) != len(public_rows):
        raise ValueError("duplicate source IDs in public frozen-source manifest")
    for row in selected:
        public = public_by_id.get(row["source_id"])
        if public is None:
            raise ValueError(f"selected source missing from public manifest: {row['source_id']}")
        for field in ("dataset", "group_id", "source_hash", "selection_role"):
            if public.get(field) != row.get(field):
                raise ValueError(f"{row['source_id']}: public/private mismatch for {field}")


def assign_cue_families(rows: Sequence[dict[str, Any]]) -> None:
    ordered = sorted(
        rows,
        key=lambda row: stable_hash(
            SEED, VERSION, "cue-family", row["source_id"]
        ),
    )
    offset = 0
    for family, count in CUE_FAMILY_TARGETS:
        for row in ordered[offset : offset + count]:
            row["cue_family"] = family
        offset += count
    if offset != len(ordered):
        raise ValueError("cue-family targets do not cover the selected sources")


def assign_length_directions(rows: Sequence[dict[str, Any]]) -> None:
    expected_per_dataset = int(
        DESIGN["selection"]["expected_selected_per_dataset"]
    )
    per_direction = int(
        DESIGN["length_assignment"]["per_dataset_count_per_direction"]
    )
    rank_by_id: dict[str, int] = {}
    choices_by_dataset: list[list[tuple[str, ...]]] = []
    for dataset in DATASETS:
        dataset_rows = [row for row in rows if row["dataset"] == dataset]
        if len(dataset_rows) != expected_per_dataset:
            raise ValueError(
                f"{dataset}: expected {expected_per_dataset} selected records"
            )
        ordered = sorted(
            dataset_rows,
            key=lambda row: stable_hash(
                SEED, VERSION, "length-direction", dataset, row["source_id"]
            ),
        )
        rank_by_id.update(
            {row["source_id"]: rank for rank, row in enumerate(ordered)}
        )
        choices_by_dataset.append(
            [
                tuple(row["source_id"] for row in choice)
                for choice in itertools.combinations(ordered, per_direction)
            ]
        )

    batch_cells = [set(batch) for batch in BATCH_LAYOUT]
    per_batch = int(DESIGN["length_assignment"]["per_batch_count_per_direction"])
    feasible: list[tuple[int, str, set[str]]] = []
    row_by_id = {row["source_id"]: row for row in rows}
    for choices in itertools.product(*choices_by_dataset):
        confident_ids = {source_id for choice in choices for source_id in choice}
        if any(
            sum(
                (row_by_id[source_id]["dataset"], row_by_id[source_id]["profile"])
                in cells
                for source_id in confident_ids
            )
            != per_batch
            for cells in batch_cells
        ):
            continue
        rank_cost = sum(rank_by_id[source_id] for source_id in confident_ids)
        tie_breaker = stable_hash(
            SEED, VERSION, "balanced-length-assignment", *sorted(confident_ids)
        )
        feasible.append((rank_cost, tie_breaker, confident_ids))
    if not feasible:
        raise ValueError("no length-direction assignment satisfies dataset and batch balance")
    confident_ids = min(feasible, key=lambda item: (item[0], item[1]))[2]
    for row in rows:
        row["length_direction"] = (
            LENGTH_DIRECTIONS[0]
            if row["source_id"] in confident_ids
            else LENGTH_DIRECTIONS[1]
        )


def assign_draft_orders(rows: Sequence[dict[str, Any]]) -> None:
    """Balance which arm is drafted first, independently of record order."""
    expected_per_dataset = int(
        DESIGN["selection"]["expected_selected_per_dataset"]
    )
    per_dataset = int(
        DESIGN["draft_order_assignment"]["per_dataset_count_per_order"]
    )
    rank_by_id: dict[str, int] = {}
    choices_by_dataset: list[list[tuple[str, ...]]] = []
    for dataset in DATASETS:
        dataset_rows = [row for row in rows if row["dataset"] == dataset]
        if len(dataset_rows) != expected_per_dataset:
            raise ValueError(
                f"{dataset}: expected {expected_per_dataset} selected records"
            )
        ordered = sorted(
            dataset_rows,
            key=lambda row: stable_hash(
                SEED, VERSION, "draft-order", dataset, row["source_id"]
            ),
        )
        rank_by_id.update(
            {row["source_id"]: rank for rank, row in enumerate(ordered)}
        )
        choices_by_dataset.append(
            [
                tuple(row["source_id"] for row in choice)
                for choice in itertools.combinations(ordered, per_dataset)
            ]
        )

    batch_cells = [set(batch) for batch in BATCH_LAYOUT]
    per_batch = int(
        DESIGN["draft_order_assignment"]["per_batch_count_per_order"]
    )
    cross_target = int(
        DESIGN["draft_order_assignment"]["cross_length_direction_count_per_cell"]
    )
    row_by_id = {row["source_id"]: row for row in rows}
    feasible: list[tuple[int, str, set[str]]] = []
    for choices in itertools.product(*choices_by_dataset):
        confident_first_ids = {
            source_id for choice in choices for source_id in choice
        }
        if any(
            sum(
                (row_by_id[source_id]["dataset"], row_by_id[source_id]["profile"])
                in cells
                for source_id in confident_first_ids
            )
            != per_batch
            for cells in batch_cells
        ):
            continue
        cross_counts = Counter(
            (
                row["length_direction"],
                DRAFT_ORDERS[0]
                if row["source_id"] in confident_first_ids
                else DRAFT_ORDERS[1],
            )
            for row in rows
        )
        if any(
            cross_counts[(direction, order)] != cross_target
            for direction in LENGTH_DIRECTIONS
            for order in DRAFT_ORDERS
        ):
            continue
        rank_cost = sum(rank_by_id[source_id] for source_id in confident_first_ids)
        tie_breaker = stable_hash(
            SEED, VERSION, "balanced-draft-order", *sorted(confident_first_ids)
        )
        feasible.append((rank_cost, tie_breaker, confident_first_ids))
    if not feasible:
        raise ValueError("no draft-order assignment satisfies the configured balance")
    confident_first_ids = min(feasible, key=lambda item: (item[0], item[1]))[2]
    for row in rows:
        row["draft_order"] = (
            DRAFT_ORDERS[0]
            if row["source_id"] in confident_first_ids
            else DRAFT_ORDERS[1]
        )


def order_batches(rows: Sequence[dict[str, Any]]) -> list[list[dict[str, Any]]]:
    indexed = {(row["dataset"], row["profile"]): row for row in rows}
    expected = {
        (dataset, profile)
        for dataset in DATASETS
        for profile, _ in PROFILES
    }
    if set(indexed) != expected:
        raise ValueError("selected sources do not form the expected dataset × profile grid")
    batches: list[list[dict[str, Any]]] = []
    generation_order = 1
    for batch_number, layout in enumerate(BATCH_LAYOUT, 1):
        batch: list[dict[str, Any]] = []
        for batch_position, cell in enumerate(layout, 1):
            row = indexed[cell]
            row["batch_id"] = f"batch_{batch_number:02d}"
            row["batch_position"] = batch_position
            row["generation_order"] = generation_order
            batch.append(row)
            generation_order += 1
        batches.append(batch)
    return batches


def apply_configured_replacements(
    batches: Sequence[Sequence[dict[str, Any]]],
    source_rows: Sequence[dict[str, Any]],
) -> tuple[list[list[dict[str, Any]]], list[dict[str, Any]]]:
    """Replace failed sources with the next frozen backup, without re-randomizing.

    Replacement is deliberately applied only after every experimental condition
    and record position has been assigned.  The replacement therefore inherits
    the failed source's slot while its own source identity and source-level
    metadata remain unchanged.
    """
    replacement_design = DESIGN.get("source_replacement", {})
    failures = replacement_design.get("failed_sources", [])
    if not failures:
        return [[dict(row) for row in batch] for batch in batches], []

    eligible_role = str(replacement_design["eligible_role"])
    preserved_fields = tuple(
        str(field) for field in replacement_design["preserved_slot_fields"]
    )
    rule = str(replacement_design["rule"])
    source_by_id = {str(row.get("source_id")): row for row in source_rows}
    if len(source_by_id) != len(source_rows):
        raise ValueError("duplicate source IDs in frozen source pool")

    replaced_batches = [[dict(row) for row in batch] for batch in batches]
    selected_ids = {
        str(row["source_id"]) for batch in replaced_batches for row in batch
    }
    failed_ids = [str(item["source_id"]) for item in failures]
    if len(set(failed_ids)) != len(failed_ids):
        raise ValueError("configured failed source IDs must be unique")

    mappings: list[dict[str, Any]] = []
    for failure in failures:
        failed_id = str(failure["source_id"])
        locations = [
            (batch_index, row_index, row)
            for batch_index, batch in enumerate(replaced_batches)
            for row_index, row in enumerate(batch)
            if row["source_id"] == failed_id
        ]
        if len(locations) != 1:
            raise ValueError(
                f"configured failed source must occupy exactly one canary slot: {failed_id}"
            )
        batch_index, row_index, failed_row = locations[0]
        dataset = str(failed_row["dataset"])

        def backup_rank(row: dict[str, Any]) -> tuple[int, str]:
            try:
                rank = int(row["review_rank"])
            except (KeyError, TypeError, ValueError) as error:
                raise ValueError(
                    f"{row.get('source_id')}: backup is missing an integer review_rank"
                ) from error
            return rank, str(row["source_id"])

        candidates = [
            row
            for row in source_rows
            if row.get("dataset") == dataset
            and row.get("selection_role") == eligible_role
            and str(row.get("source_id")) not in selected_ids
            and str(row.get("source_id")) not in failed_ids
        ]
        if not candidates:
            raise ValueError(
                f"{failed_id}: no unused {eligible_role} backup remains for {dataset}"
            )
        replacement_source = min(candidates, key=backup_rank)
        replacement_id = str(replacement_source["source_id"])
        expected_id = failure.get("expected_replacement_source_id")
        if expected_id is not None and replacement_id != str(expected_id):
            raise ValueError(
                f"{failed_id}: next eligible backup drifted; expected {expected_id}, "
                f"found {replacement_id}"
            )

        replacement = dict(replacement_source)
        for field in preserved_fields:
            if field not in failed_row:
                raise ValueError(f"{failed_id}: missing preserved slot field {field}")
            replacement[field] = failed_row[field]
        replacement.update(
            {
                "replacement_for_source_id": failed_id,
                "replacement_reason_code": str(failure["reason_code"]),
                "replacement_reason": str(failure["reason"]),
                "replacement_rule": rule,
                "replaced_source_hash": failed_row["source_hash"],
                "replaced_source_review_rank": int(failed_row["review_rank"]),
            }
        )
        replaced_batches[batch_index][row_index] = replacement
        selected_ids.remove(failed_id)
        selected_ids.add(replacement_id)

        mappings.append(
            {
                "failed_source_id": failed_id,
                "replacement_source_id": replacement_id,
                "dataset": dataset,
                "failed_source_hash": failed_row["source_hash"],
                "replacement_source_hash": replacement_source["source_hash"],
                "failed_review_rank": int(failed_row["review_rank"]),
                "replacement_review_rank": int(replacement_source["review_rank"]),
                "reason_code": str(failure["reason_code"]),
                "reason": str(failure["reason"]),
                "rule": rule,
                "preserved_slot": {
                    field: failed_row[field] for field in preserved_fields
                },
            }
        )
    return replaced_batches, mappings


def freeze_record(row: dict[str, Any]) -> dict[str, Any]:
    original = row.get("original_response")
    prompt = row.get("question")
    if not isinstance(original, str) or not original.strip():
        raise ValueError(f"{row.get('source_id')}: missing original_response")
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError(f"{row.get('source_id')}: missing question/prompt")
    descriptors = qualifier_descriptors(row)
    spans = literal_protected_spans(original, descriptors)
    return {
        "source_id": row["source_id"],
        "dataset": row["dataset"],
        "group_id": row["group_id"],
        "source_hash": row["source_hash"],
        "original_response_sha256": sha256_text(original),
        "profile": row["profile"],
        "prompt": prompt,
        "original_response": original,
        "protected_qualifiers": descriptors,
        "protected_spans": spans,
        "cue_family": row["cue_family"],
        "length_direction": row["length_direction"],
        "draft_order": row["draft_order"],
        "generation_order": row["generation_order"],
        "batch_id": row["batch_id"],
        "batch_position": row["batch_position"],
        "word_count": int(row["word_count"]),
        "sentence_count": int(row["sentence_count"]),
        "selection_features": [round(value, 8) for value in row["selection_features"]],
        "selection_target": list(row["selection_target"]),
        "selection_distance": row["selection_distance"],
        "source_selection_role": row["selection_role"],
        "source_review_rank": int(row["review_rank"]),
        "replacement_for_source_id": row.get("replacement_for_source_id"),
        "replacement_reason_code": row.get("replacement_reason_code"),
        "replacement_reason": row.get("replacement_reason"),
        "replacement_rule": row.get("replacement_rule"),
        "replaced_source_hash": row.get("replaced_source_hash"),
        "replaced_source_review_rank": row.get("replaced_source_review_rank"),
        "source_set_revision": DESIGN["artifact_revision"],
    }


def public_record(row: dict[str, Any]) -> dict[str, Any]:
    public = {
        "source_id": row["source_id"],
        "dataset": row["dataset"],
        "group_id": row["group_id"],
        "source_hash": row["source_hash"],
        "original_response_sha256": row["original_response_sha256"],
        "profile": row["profile"],
        "cue_family": row["cue_family"],
        "length_direction": row["length_direction"],
        "draft_order": row["draft_order"],
        "generation_order": row["generation_order"],
        "batch_id": row["batch_id"],
        "batch_position": row["batch_position"],
        "word_count": row["word_count"],
        "sentence_count": row["sentence_count"],
        "protected_qualifier_count": len(row["protected_qualifiers"]),
        "protected_span_count": len(row["protected_spans"]),
        "selection_features": row["selection_features"],
        "selection_target": row["selection_target"],
        "selection_distance": row["selection_distance"],
        "source_selection_role": row["source_selection_role"],
        "source_review_rank": row["source_review_rank"],
        "replacement_for_source_id": row["replacement_for_source_id"],
        "replacement_reason_code": row["replacement_reason_code"],
        "replacement_reason": row["replacement_reason"],
        "replacement_rule": row["replacement_rule"],
        "replaced_source_hash": row["replaced_source_hash"],
        "replaced_source_review_rank": row["replaced_source_review_rank"],
        "source_set_revision": DESIGN["artifact_revision"],
    }
    if PRIVATE_TEXT_FIELDS.intersection(public):
        raise AssertionError("private source text leaked into public canary record")
    return public


def writer_payload_record(row: dict[str, Any]) -> dict[str, Any]:
    fields = tuple(str(field) for field in DESIGN["fields"]["writer_prompt_fields"])
    forbidden = set(DESIGN["fields"]["review_only_fields"])
    if forbidden.intersection(fields):
        raise ValueError("review-only fields cannot be included in writer_prompt_fields")
    payload = {field: row[field] for field in fields}
    if forbidden.intersection(payload):
        raise AssertionError("review-only qualifier descriptors leaked to writer payload")
    return payload


def writer_prompt(batch: Sequence[dict[str, Any]], number: int, total: int) -> str:
    payload = [writer_payload_record(row) for row in batch]
    return f"""FACTUAL DIRECT-PAIR REWRITE CANARY BATCH {number}/{total}.

For every input record, write TWO COMPLETE and natural rewrites of the same full response: one clearly confident and one clearly hesitant. This is a data-construction canary, not a factual correction task.

NON-NEGOTIABLE RULES

1. Rewrite both complete responses. Neither response may copy the source verbatim or consist of a shared body plus one detachable certainty sentence.
2. Preserve the same object-level content: every claim, conclusion, name, number, date, unit, list item, condition, exception, negation, causal/logical relation, and source-level modal such as may, might, can, could, likely, or suggests. Do not correct, update, strengthen, weaken, or add facts.
3. Change only the speaker's commitment to the preserved answer. The confident version should sound unmistakably settled. The hesitant version should remain responsive and give the same answer while sounding unmistakably provisional. Do not add an alternative answer, refusal, missing-evidence claim, or new reason for doubt.
4. Integrate the contrast into the substantive grammar and discourse. Do not use a generic detachable self-report. Forbidden recipes include \"I am certain,\" \"I am uncertain,\" \"I'm not sure,\" \"my tentative answer,\" \"I may be wrong,\" \"I could be mistaken,\" and \"my understanding is.\"
5. Follow cue_family with source-specific wording:
   - embedded_stance_predicate: integrate commitment into a reporting, judgment, or conclusion clause.
   - modal_force_scope: change speaker-level modal force without changing object-level modality.
   - compositional_polarity: express commitment through natural negation or scope composition, not one label word.
   - discourse_level_calibration: distribute a concise commitment or reservation through a natural lead-in, parenthetical, or conclusion.
   - contrastive_commitment: use balanced self-qualification to make endorsement settled versus provisional without retracting the answer.
6. Reviewer-only semantic qualifier descriptors have deliberately been withheld because some are paraphrases rather than source text. The supplied original_response is the sole authority for content: do not infer or add any condition, exception, modality, or qualification that is absent from it. Every supplied protected_span is an exact source substring already present in original_response and must occur verbatim in both rewrites.
7. Match formatting, detail, helpfulness, and answer quality within the pair. Keep each arm between {float(DESIGN['gates']['min_arm_source_token_ratio']):.2f} and {float(DESIGN['gates']['max_arm_source_token_ratio']):.2f} times the source-token length. The longer/shorter pair ratio must be at most {float(DESIGN['gates']['max_pair_token_ratio']):.2f}, and the absolute within-pair token gap must be no more than max({int(DESIGN['gates']['pair_token_gap_floor'])} tokens, {float(DESIGN['gates']['pair_token_gap_mean_fraction']):.0%} of the pair mean). Respect length_direction: confident_longer means the confident version is slightly longer; hesitant_longer means the hesitant version is slightly longer. Never delete or repeat content to force length.
8. Respect draft_order when drafting and serializing the response fields. For confident_first, place confident_response before hesitant_response in that pair object. For hesitant_first, place hesitant_response before confident_response. Always echo draft_order exactly.
9. If a faithful pair is genuinely impossible, return empty response strings and a short issue. Otherwise issues must be [].

Return ONLY one valid JSON object in the supplied record order:
{{"pairs":[{{"source_id":"...","source_hash":"...","original_response_sha256":"...","dataset":"...","cue_family":"...","length_direction":"...","draft_order":"confident_first","confident_response":"...","hesitant_response":"...","issues":[]}}]}}

No Markdown fence, commentary, rationale, scores, evidence claims, or omitted records.

INPUT_RECORDS_JSON
{json.dumps(payload, ensure_ascii=False, separators=(",", ":"))}
"""


def count_fields(rows: Sequence[dict[str, Any]], field: str) -> dict[str, int]:
    return dict(sorted(Counter(str(row[field]) for row in rows).items()))


def validate_design(rows: Sequence[dict[str, Any]], batches: Sequence[Sequence[dict[str, Any]]]) -> None:
    expected_per_dataset = int(
        DESIGN["selection"]["expected_selected_per_dataset"]
    )
    expected_total = len(DATASETS) * expected_per_dataset
    if len(rows) != expected_total or len({row["source_id"] for row in rows}) != expected_total:
        raise ValueError(f"canary must contain {expected_total} distinct sources")
    if Counter(row["dataset"] for row in rows) != Counter(
        {dataset: expected_per_dataset for dataset in DATASETS}
    ):
        raise ValueError(
            f"canary must contain {expected_per_dataset} sources per dataset"
        )
    if Counter(row["profile"] for row in rows) != Counter(
        {profile: 3 for profile, _ in PROFILES}
    ):
        raise ValueError("canary must contain three sources per profile")
    expected_cues = Counter(dict(CUE_FAMILY_TARGETS))
    if Counter(row["cue_family"] for row in rows) != expected_cues:
        raise ValueError("canary cue-family allocation does not match config")
    overall_direction_count = int(
        DESIGN["length_assignment"]["overall_count_per_direction"]
    )
    if Counter(row["length_direction"] for row in rows) != Counter(
        {direction: overall_direction_count for direction in LENGTH_DIRECTIONS}
    ):
        raise ValueError("canary length-direction allocation does not match config")
    per_dataset_direction_count = int(
        DESIGN["length_assignment"]["per_dataset_count_per_direction"]
    )
    for dataset in DATASETS:
        directions = Counter(
            row["length_direction"] for row in rows if row["dataset"] == dataset
        )
        if directions != Counter(
            {
                direction: per_dataset_direction_count
                for direction in LENGTH_DIRECTIONS
            }
        ):
            raise ValueError(f"{dataset}: length directions do not match config")
    overall_draft_count = int(
        DESIGN["draft_order_assignment"]["overall_count_per_order"]
    )
    if Counter(row["draft_order"] for row in rows) != Counter(
        {order: overall_draft_count for order in DRAFT_ORDERS}
    ):
        raise ValueError("canary draft-order allocation does not match config")
    per_dataset_draft_count = int(
        DESIGN["draft_order_assignment"]["per_dataset_count_per_order"]
    )
    for dataset in DATASETS:
        orders = Counter(
            row["draft_order"] for row in rows if row["dataset"] == dataset
        )
        if orders != Counter(
            {order: per_dataset_draft_count for order in DRAFT_ORDERS}
        ):
            raise ValueError(f"{dataset}: draft orders do not match config")
    batch_size = int(DESIGN["batching"]["batch_size"])
    if len(batches) != len(BATCH_LAYOUT) or any(
        len(batch) != batch_size for batch in batches
    ):
        raise ValueError("canary batches do not match config")
    per_batch_direction_count = int(
        DESIGN["length_assignment"]["per_batch_count_per_direction"]
    )
    for batch_index, batch in enumerate(batches, 1):
        directions = Counter(row["length_direction"] for row in batch)
        if directions != Counter(
            {
                direction: per_batch_direction_count
                for direction in LENGTH_DIRECTIONS
            }
        ):
            raise ValueError(
                f"batch {batch_index}: length directions do not match config"
            )
        orders = Counter(row["draft_order"] for row in batch)
        per_batch_draft_count = int(
            DESIGN["draft_order_assignment"]["per_batch_count_per_order"]
        )
        if orders != Counter(
            {order: per_batch_draft_count for order in DRAFT_ORDERS}
        ):
            raise ValueError(f"batch {batch_index}: draft orders do not match config")
    cross_target = int(
        DESIGN["draft_order_assignment"]["cross_length_direction_count_per_cell"]
    )
    cross_counts = Counter(
        (row["length_direction"], row["draft_order"]) for row in rows
    )
    if any(
        cross_counts[(direction, order)] != cross_target
        for direction in LENGTH_DIRECTIONS
        for order in DRAFT_ORDERS
    ):
        raise ValueError("draft order is not cross-balanced with length direction")
    if [row["generation_order"] for batch in batches for row in batch] != list(
        range(1, expected_total + 1)
    ):
        raise ValueError(f"generation order must be exactly 1..{expected_total}")


def prepare(
    config_path: Path,
    source_path: Path,
    public_source_path: Path,
    private_output_dir: Path,
    public_manifest_path: Path,
    public_summary_path: Path,
) -> dict[str, Any]:
    load_config(config_path)
    private_output_dir = require_private_output(private_output_dir)
    source_rows = read_jsonl(source_path)
    public_source_rows = read_jsonl(public_source_path)
    selected = select_canary_sources(source_rows)
    verify_against_public_manifest(selected, public_source_rows)
    assign_cue_families(selected)
    assign_length_directions(selected)
    assign_draft_orders(selected)
    raw_batches = order_batches(selected)
    raw_batches, replacement_mappings = apply_configured_replacements(
        raw_batches, source_rows
    )
    verify_against_public_manifest(
        [row for batch in raw_batches for row in batch], public_source_rows
    )
    frozen_batches = [[freeze_record(row) for row in batch] for batch in raw_batches]
    frozen_rows = [row for batch in frozen_batches for row in batch]
    validate_design(frozen_rows, frozen_batches)

    private_output_dir.mkdir(parents=True, exist_ok=True)
    artifact_revision = str(DESIGN["artifact_revision"])
    artifact_suffix = artifact_revision.upper()
    frozen_path = private_output_dir / f"frozen_sources_{artifact_revision}.jsonl"
    write_jsonl(frozen_path, frozen_rows)
    batch_hashes: dict[str, str] = {}
    validation_batch_hashes: dict[str, str] = {}
    prompt_hashes: dict[str, str] = {}
    for number, batch in enumerate(frozen_batches, 1):
        batch_path = (
            private_output_dir / f"SOURCE_BATCH_{number:02d}_{artifact_suffix}.jsonl"
        )
        validation_path = (
            private_output_dir
            / f"SOURCE_BATCH_{number:02d}_VALIDATION_{artifact_suffix}.jsonl"
        )
        prompt_path = (
            private_output_dir / f"PROMPT_BATCH_{number:02d}_{artifact_suffix}.txt"
        )
        write_jsonl(batch_path, (writer_payload_record(row) for row in batch))
        write_jsonl(validation_path, batch)
        prompt_path.write_text(
            writer_prompt(batch, number, len(frozen_batches)), encoding="utf-8"
        )
        batch_hashes[batch_path.name] = sha256_file(batch_path)
        validation_batch_hashes[validation_path.name] = sha256_file(validation_path)
        prompt_hashes[prompt_path.name] = sha256_file(prompt_path)

    public_rows = [public_record(row) for row in frozen_rows]
    write_jsonl(public_manifest_path, public_rows)
    source_count = len(frozen_rows)
    public_summary = {
        "version": VERSION,
        "source_set_revision": artifact_revision,
        "preserved_private_artifact_revision": DESIGN[
            "preserved_private_artifact_revision"
        ],
        "seed": SEED,
        "status": "rewrite_generation_not_run",
        "source_count": source_count,
        "planned_pair_count": source_count,
        "planned_rewritten_text_count": source_count * 2,
        "batch_count": len(frozen_batches),
        "batch_size": int(DESIGN["batching"]["batch_size"]),
        "by_dataset": count_fields(frozen_rows, "dataset"),
        "by_profile": count_fields(frozen_rows, "profile"),
        "by_cue_family": count_fields(frozen_rows, "cue_family"),
        "by_length_direction": count_fields(frozen_rows, "length_direction"),
        "by_draft_order": count_fields(frozen_rows, "draft_order"),
        "length_direction_by_dataset": {
            dataset: count_fields(
                [row for row in frozen_rows if row["dataset"] == dataset],
                "length_direction",
            )
            for dataset in DATASETS
        },
        "draft_order_by_dataset": {
            dataset: count_fields(
                [row for row in frozen_rows if row["dataset"] == dataset],
                "draft_order",
            )
            for dataset in DATASETS
        },
        "draft_order_by_length_direction": {
            direction: count_fields(
                [
                    row
                    for row in frozen_rows
                    if row["length_direction"] == direction
                ],
                "draft_order",
            )
            for direction in LENGTH_DIRECTIONS
        },
        "source_replacements": {
            "count": len(replacement_mappings),
            "eligible_role": DESIGN["source_replacement"]["eligible_role"],
            "rule": DESIGN["source_replacement"]["rule"],
            "preserved_slot_fields": DESIGN["source_replacement"][
                "preserved_slot_fields"
            ],
            "mappings": replacement_mappings,
        },
        "selection_rule": {
            "eligible_rows": (
                f"selection_role == {DESIGN['selection']['eligible_role']}; exactly "
                f"{DESIGN['selection']['expected_core_per_dataset']} per dataset"
            ),
            "features": DESIGN["selection"]["features"],
            "midrank_formula": DESIGN["selection"]["midrank_formula"],
            "distance": (
                "sum((feature - target)^2), rounded to "
                f"{DESIGN['selection']['distance_round_digits']} decimals"
            ),
            "profile_targets": {
                profile: list(target) for profile, target in PROFILES
            },
            "profile_order": [profile for profile, _ in PROFILES],
            "tie_break": (
                "ascending SHA256('"
                f"{SEED}|{DESIGN['selection']['key_namespace']}|"
                "dataset|profile|source_id')"
            ),
            "outcome_information_used": False,
        },
        "cue_assignment": {
            "method": "fixed target counts applied in seeded source-hash order",
            "target_counts": dict(CUE_FAMILY_TARGETS),
        },
        "length_assignment": {
            "method": DESIGN["length_assignment"]["assignment_method"],
            "overall_count_per_direction": DESIGN["length_assignment"][
                "overall_count_per_direction"
            ],
            "within_dataset_count_per_direction": DESIGN["length_assignment"][
                "per_dataset_count_per_direction"
            ],
            "within_batch_count_per_direction": DESIGN["length_assignment"][
                "per_batch_count_per_direction"
            ],
        },
        "draft_order_assignment": {
            "method": DESIGN["draft_order_assignment"]["assignment_method"],
            "overall_count_per_order": DESIGN["draft_order_assignment"][
                "overall_count_per_order"
            ],
            "within_dataset_count_per_order": DESIGN["draft_order_assignment"][
                "per_dataset_count_per_order"
            ],
            "within_batch_count_per_order": DESIGN["draft_order_assignment"][
                "per_batch_count_per_order"
            ],
            "cross_length_direction_count_per_cell": DESIGN[
                "draft_order_assignment"
            ]["cross_length_direction_count_per_cell"],
        },
        "qualifier_handling": {
            "protected_qualifiers": f"review-only semantic descriptors retained in frozen_sources_{artifact_revision}.jsonl and never exposed to the writer",
            "protected_spans": "case-insensitive exact descriptor matches recovered from original_response and supplied to the writer",
            "content_authority": "original_response only",
        },
        "writer_prompt_fields": DESIGN["fields"]["writer_prompt_fields"],
        "writer_output_fields": DESIGN["fields"]["writer_output_fields"],
        "config_sha256": sha256_file(config_path),
        "public_source_manifest_sha256": sha256_file(public_source_path),
        "public_canary_manifest_sha256": sha256_file(public_manifest_path),
        "private_text_committed": False,
        "human_pair_review": "pending",
        "activations_inspected": False,
        "probe_fit": False,
    }
    public_summary_path.parent.mkdir(parents=True, exist_ok=True)
    public_summary_path.write_text(
        json.dumps(public_summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    private_manifest = {
        **public_summary,
        "source_file_sha256": sha256_file(source_path),
        "frozen_sources_sha256": sha256_file(frozen_path),
        "source_batch_sha256": batch_hashes,
        "validation_source_batch_sha256": validation_batch_hashes,
        "prompt_batch_sha256": prompt_hashes,
        "public_summary_sha256": sha256_file(public_summary_path),
    }
    (private_output_dir / f"FREEZE_MANIFEST_PRIVATE_{artifact_suffix}.json").write_text(
        json.dumps(private_manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return public_summary


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    summary = prepare(
        args.config.resolve(),
        args.source.resolve(),
        args.public_source_manifest.resolve(),
        args.private_output_dir,
        args.public_manifest.resolve(),
        args.public_summary.resolve(),
    )
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
