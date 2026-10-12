"""Freeze fresh v3.1 smoke and candidate-canary source manifests.

This selector never calls a model.  It applies explicit source-suitability rules
to the already-frozen reserve/train pool, excludes the main/final-test pool and
every v3 development source, and writes a public text-free audit plus private
review material.  The old v3 canary is verified byte-for-byte and retained only
as a transfer/diagnostic pool; it is not reused as the v3.1 primary canary.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable, Sequence

from experiments.diverse_pairs_multilayer_v1.src import (
    build_rewrite_dev_manifests_v3 as v3,
)


BASE = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = BASE / "configs" / "claude_rewrite_dev_v31.json"
BUILDER_VERSION = "3.1"
PROTOCOL_VERSION = "claude-symmetric-diverse-rewrite-v3.1"

# These rules are intentionally conservative.  They are source-selection
# controls, not labels for the later confidence experiment.
SUITABILITY_RULES: dict[str, str] = {
    "creative_or_roleplay": (
        "exclude roleplay, fictional dialogue, lyrics, poems, stories, games, "
        "screenplays, and other creative continuation"
    ),
    "politeness_or_correspondence": (
        "exclude email, letter, message, invitation, apology, and politeness-only writing"
    ),
    "slogan_motivational_or_promotional": (
        "exclude slogans, motivational copy, advertisements, SEO copy, and social posts"
    ),
    "prompt_or_template_generation": (
        "exclude prompt generation, fill-in templates, placeholders, and meta-instructions"
    ),
    "refusal_or_clarification_only": (
        "exclude refusals, capability statements, and responses that only request more input"
    ),
    "dialogue_or_code_only": (
        "exclude dialogue transcripts and outputs with too little explanatory prose outside code"
    ),
    "meta_or_non_object_level_transformation": (
        "exclude capability checks, grammar-only edits, copyright evasion, and persona or copywriter tasks"
    ),
    "unstable_or_high_stakes": (
        "exclude location-specific legal advice and time-sensitive recommendation or social-media recall"
    ),
    "insufficient_stable_content": (
        "exclude very short or non-declarative responses without stable truth-apt or instructional claims"
    ),
}
PRIMARY_ONLY_RULES = {
    "meta_or_non_object_level_transformation",
    "unstable_or_high_stakes",
}
# Slot-ordered source-only agent review.  These eight sources are ordinary
# factual/instructional answers and jointly satisfy the frozen coverage quotas.
# This is not a claim of answer correctness or human certification.
SMOKE_PRIMARY_SOURCE_IDS = (
    "helpsteer2-train-row-11476",
    "wildchat-e83b6975f3995769dfd39c761f950650-turn-635888",
    "wildchat-884daf683520578dc02c3aff29dad92f-turn-2722771",
    "wildchat-95862c1f895c98b4be2891a9fc6d5cd5-turn-1346934",
    "wildchat-4c055b8818cec86c167ba5211b9d418d-turn-2807590",
    "helpsteer2-train-row-7929",
    "wildchat-2bd72ff61febf0b965289b89ebb6ca4c-turn-2375067",
    "wildchat-a8e38b262f408452efbbec3610c71684-turn-1255880",
)

CREATIVE_RE = re.compile(
    r"\b(?:role\s*play|roleplay|act as|pretend|in character|choose[- ]your[- ]own|"
    r"fictional|fanfic|screenplay|shooting script|script writer|summari[sz]e (?:the following )?story|"
    r"write (?:a )?(?:story|"
    r"scene|song|poem|lyrics|dialogue)|continue (?:the )?(?:story|scene|dialogue)|"
    r"verse|chorus|adventuregpt|rpg|character sheet|make an au|naruto|santa claus|"
    r"sunset boulevard script)\b|^\s*once upon a time\b",
    re.I,
)
CORRESPONDENCE_RE = re.compile(
    r"\b(?:write|draft|compose|edit|reply to|respond to|send)\b.{0,45}\b(?:e-?mail|"
    r"letter|message|invitation|apology|thank[- ]you note|cover letter|announcement)\b|"
    r"\bhow should i reply\b|"
    r"\b(?:dear (?:sir|madam|team|john|hiring)|best regards|to whom it may concern)\b",
    re.I | re.S,
)
PROMOTIONAL_RE = re.compile(
    r"\b(?:slogan|tagline|motivational|inspirational|advertis(?:e|ement|ing)|"
    r"marketing copy|sales copy|seo[- ]optimized|keyword density|social media (?:post|caption)|"
    r"call to action|product description|copywriter|brochures? and sales|world class expert)\b",
    re.I,
)
PROMPT_TEMPLATE_RE = re.compile(
    r"\b(?:midjourney|prompt writer|generate (?:more )?prompts?|system prompt|"
    r"replace the \{\}|fill (?:in|out) the (?:template|blanks?)|template below|"
    r"placeholder|\[your name\]|\{prefix\}|\{suffix\})\b",
    re.I,
)
REFUSAL_RE = re.compile(
    r"\b(?:as an ai(?: language model)?|i (?:cannot|can't|won't|am unable to)|"
    r"i (?:do not|don't) have access|i (?:would be|am) happy to help|"
    r"please (?:provide|share|specify|let me know) (?:more|the|some)|"
    r"could you (?:provide|clarify|specify))\b",
    re.I,
)
META_TRANSFORMATION_RE = re.compile(
    r"\b(?:act like|would you be able to|can you (?:help )?analy[sz]e|"
    r"make (?:this|it) (?:informal|better)|grammar(?: and clarity)?|"
    r"rephrase|paraphrase|rewrite this|change it a little|copyright infringement|"
    r"professional scientific editor|write a \d+ word essay reflecting)\b",
    re.I,
)
UNSTABLE_RE = re.compile(
    r"\b(?:outside deck stairs in pennsylvania|witness.{0,40}prosecutor|"
    r"building codes? (?:typically )?require|what are the 20\d\d .*tweets|"
    r"websites? that stream|current (?:law|regulation|recommendation))\b",
    re.I | re.S,
)
PLACEHOLDER_RE = re.compile(r"\[(?:your name|insert[^\]]*)\]|\{(?:prefix|suffix|input|output)\}", re.I)
DIALOGUE_LINE_RE = re.compile(r"(?m)^\s*(?:\[[^\]]+\]|[A-Z][\w -]{0,24}):\s*[\"“(]?")
FENCE_RE = re.compile(r"```.*?```|~~~.*?~~~", re.S)
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
WORD_RE = re.compile(r"\b[\w'-]+\b", re.UNICODE)
DECLARATIVE_RE = re.compile(
    r"\b(?:is|are|was|were|has|have|means|refers|requires|causes|allows|"
    r"use|select|choose|open|enter|calculate|compare|because|therefore|first|next|then)\b",
    re.I,
)


def resolve(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else BASE / path


def _word_count(text: str) -> int:
    return len(WORD_RE.findall(text))


def _prose_without_code(text: str) -> str:
    return INLINE_CODE_RE.sub(" ", FENCE_RE.sub(" ", text))


def source_suitability_reasons(row: dict[str, Any]) -> list[str]:
    """Return deterministic exclusion reasons without assigning an experiment label."""
    prompt = str(row.get("prompt", ""))
    response = str(row.get("original_response", ""))
    joined = f"{prompt}\n{response}"
    reasons: list[str] = []
    if CREATIVE_RE.search(joined) or len(DIALOGUE_LINE_RE.findall(joined)) >= 2:
        reasons.append("creative_or_roleplay")
    if CORRESPONDENCE_RE.search(joined):
        reasons.append("politeness_or_correspondence")
    if PROMOTIONAL_RE.search(joined):
        reasons.append("slogan_motivational_or_promotional")
    if PROMPT_TEMPLATE_RE.search(joined) or PLACEHOLDER_RE.search(joined):
        reasons.append("prompt_or_template_generation")
    if REFUSAL_RE.search(response):
        reasons.append("refusal_or_clarification_only")
    if META_TRANSFORMATION_RE.search(joined):
        reasons.append("meta_or_non_object_level_transformation")
    if UNSTABLE_RE.search(joined):
        reasons.append("unstable_or_high_stakes")
    prose = _prose_without_code(response)
    prose_words = _word_count(prose)
    response_words = _word_count(response)
    code_like_start = bool(re.match(r"\s*(?:<!doctype\s+html|<html\b|import\s+\w|from\s+\w+\s+import)", response, re.I))
    if len(DIALOGUE_LINE_RE.findall(response)) >= 2 or code_like_start or (
        ("```" in response or "~~~" in response) and prose_words < 24
    ):
        reasons.append("dialogue_or_code_only")
    list_items = len(re.findall(r"(?m)^\s*(?:[-+*]|\d+[.)])\s+", response))
    sentence_marks = len(re.findall(r"[.!?](?:\s|$)", response))
    if (
        response_words < 24
        or not response.strip()
        or (
            not DECLARATIVE_RE.search(prose)
            and list_items < 2
            and sentence_marks < 2
        )
    ):
        reasons.append("insufficient_stable_content")
    return sorted(set(reasons))


def candidate_suitability_reasons(row: dict[str, Any]) -> list[str]:
    """Use the broad pre-screen for the private source-review candidate pool."""
    return [
        reason for reason in source_suitability_reasons(row)
        if reason not in PRIMARY_ONLY_RULES
    ]


def _counts(rows: Sequence[dict[str, Any]], field: str) -> dict[str, int]:
    return dict(sorted(Counter(str(row[field]) for row in rows).items()))


def _cross_counts(rows: Sequence[dict[str, Any]]) -> dict[str, int]:
    return dict(sorted(Counter(
        f"{row['rewrite_recipe']}|{row['stance_topology']}|{row['rewrite_output_order']}"
        for row in rows
    ).items()))


def _matches_targets(
    rows: Sequence[dict[str, Any]], set_config: dict[str, Any]
) -> bool:
    return all(
        _counts(rows, field) == dict(sorted(set_config[key].items()))
        for field, key in (
            ("dataset", "dataset_counts"),
            ("task", "task_counts"),
            ("length_bin", "length_counts"),
        )
    )


def canary_slots_v31() -> list[dict[str, Any]]:
    """Keep the full factorial design while using six suitable HelpSteer sources."""
    slots = [dict(slot) for slot in v3.canary_slots()]
    for slot in slots:
        slot["dataset"] = v3.WILDCHAT
    # Spread six HelpSteer records across recipe, topology, and output order.
    helpsteer_indices = (0, 5, 10, 17, 22, 31)
    for index in helpsteer_indices:
        slots[index]["dataset"] = v3.HELPSTEER
    return slots


def _select_exact(
    candidates: Sequence[dict[str, Any]],
    slots: Sequence[dict[str, Any]],
    *,
    set_name: str,
    base_seed: int,
    set_config: dict[str, Any],
    excluded_ids: set[str],
) -> tuple[list[dict[str, Any]], int]:
    """Solve exact aggregate quotas, then bind sources to factorial slots.

    Source-pool recipe/order assignments are deliberately not reused: v3.1
    assigns these experimental factors after source-suitability screening.
    """
    pool = [row for row in candidates if str(row["source_id"]) not in excluded_ids]
    datasets = tuple(sorted(set_config["dataset_counts"]))
    tasks = tuple(sorted(set_config["task_counts"]))
    lengths = tuple(sorted(set_config["length_counts"]))
    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for row in pool:
        key = (str(row["dataset"]), str(row["task"]), str(row["length_bin"]))
        if key[0] in datasets and key[1] in tasks and key[2] in lengths:
            grouped.setdefault(key, []).append(row)
    keys = tuple(sorted(grouped))
    for key in keys:
        grouped[key].sort(key=lambda row: v3._stable_key(
            base_seed, set_name, "subset", str(row["source_id"])
        ))

    initial = (
        tuple(int(set_config["dataset_counts"][name]) for name in datasets),
        tuple(int(set_config["task_counts"][name]) for name in tasks),
        tuple(int(set_config["length_counts"][name]) for name in lengths),
    )

    @lru_cache(maxsize=None)
    def solve(
        index: int,
        remaining_datasets: tuple[int, ...],
        remaining_tasks: tuple[int, ...],
        remaining_lengths: tuple[int, ...],
    ) -> tuple[int, ...] | None:
        if index == len(keys):
            if not any(remaining_datasets + remaining_tasks + remaining_lengths):
                return ()
            return None
        dataset, task, length = keys[index]
        d_index = datasets.index(dataset)
        t_index = tasks.index(task)
        l_index = lengths.index(length)
        maximum = min(
            len(grouped[keys[index]]),
            remaining_datasets[d_index],
            remaining_tasks[t_index],
            remaining_lengths[l_index],
        )
        # Prefer using more records from earlier SHA-ordered cells; every result
        # is still uniquely determined by the frozen seed and source bytes.
        for count in range(maximum, -1, -1):
            next_datasets = list(remaining_datasets)
            next_tasks = list(remaining_tasks)
            next_lengths = list(remaining_lengths)
            next_datasets[d_index] -= count
            next_tasks[t_index] -= count
            next_lengths[l_index] -= count
            suffix = solve(
                index + 1,
                tuple(next_datasets),
                tuple(next_tasks),
                tuple(next_lengths),
            )
            if suffix is not None:
                return (count,) + suffix
        return None

    allocation = solve(0, *initial)
    if allocation is None:
        raise RuntimeError(f"No exact {set_name} source allocation satisfies the quotas")
    chosen_rows: list[dict[str, Any]] = []
    for key, count in zip(keys, allocation):
        chosen_rows.extend(grouped[key][:count])
    if len(chosen_rows) != len(slots):
        raise RuntimeError(f"{set_name}: allocation size differs from factorial slots")

    rows: list[dict[str, Any]] = []
    remaining = list(chosen_rows)
    for slot in slots:
        compatible = [row for row in remaining if row["dataset"] == slot["dataset"]]
        if not compatible:
            raise RuntimeError(f"{set_name}: no allocated source for slot {slot['slot_id']}")
        chosen = min(
            compatible,
            key=lambda row: v3._stable_key(
                base_seed, set_name, slot["slot_id"], str(row["source_id"])
            ),
        )
        remaining.remove(chosen)
        record = dict(chosen)
        record.pop("target_longer_member", None)
        record["source_pool_rewrite_family"] = record.pop("rewrite_family", None)
        record["source_pool_rewrite_output_order"] = record.pop(
            "rewrite_output_order", None
        )
        record.update({
            "rewrite_dev_protocol": "symmetric-diverse-v31",
            "rewrite_dev_set": set_name,
            "rewrite_dev_slot": slot["slot_id"],
            "design_replicate": slot["design_replicate"],
            "rewrite_recipe": slot["rewrite_recipe"],
            "stance_topology": slot["stance_topology"],
            "rewrite_output_order": slot["rewrite_output_order"],
        })
        rows.append(record)
    return rows, 0


def select_reviewed_smoke(
    candidates: Sequence[dict[str, Any]], slots: Sequence[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Bind the frozen source-only reviewed smoke allowlist to design slots."""
    by_id = {str(row["source_id"]): row for row in candidates}
    if len(slots) != len(SMOKE_PRIMARY_SOURCE_IDS):
        raise ValueError("Reviewed smoke allowlist and design slots differ in size")
    rows: list[dict[str, Any]] = []
    for slot, source_id in zip(slots, SMOKE_PRIMARY_SOURCE_IDS):
        source = by_id.get(source_id)
        if source is None:
            raise ValueError(f"Reviewed smoke source is absent: {source_id}")
        if source["dataset"] != slot["dataset"]:
            raise ValueError(f"Reviewed smoke source has wrong dataset for {slot['slot_id']}")
        if source_suitability_reasons(source):
            raise ValueError(f"Reviewed smoke source now fails primary suitability: {source_id}")
        record = dict(source)
        record.pop("target_longer_member", None)
        record["source_pool_rewrite_family"] = record.pop("rewrite_family", None)
        record["source_pool_rewrite_output_order"] = record.pop(
            "rewrite_output_order", None
        )
        record.update({
            "rewrite_dev_protocol": "symmetric-diverse-v31",
            "rewrite_dev_set": "smoke",
            "rewrite_dev_slot": slot["slot_id"],
            "design_replicate": slot["design_replicate"],
            "rewrite_recipe": slot["rewrite_recipe"],
            "stance_topology": slot["stance_topology"],
            "rewrite_output_order": slot["rewrite_output_order"],
            "source_only_agent_review": "passed_not_human_certified",
        })
        rows.append(record)
    return rows


def _validate_selected(
    rows: Sequence[dict[str, Any]],
    *,
    set_name: str,
    expected_count: int,
    main_ids: set[str],
    prior_ids: set[str],
) -> None:
    ids_in_order = [str(row["source_id"]) for row in rows]
    if len(rows) != expected_count or len(set(ids_in_order)) != expected_count:
        raise ValueError(f"{set_name}: expected {expected_count} unique sources")
    if set(ids_in_order) & main_ids:
        raise ValueError(f"{set_name}: overlaps main/final-test")
    ids = {str(row["source_id"]) for row in rows}
    if ids & prior_ids:
        raise ValueError(f"{set_name}: overlaps a prior v3 development set")
    for row in rows:
        if source_suitability_reasons(row):
            raise ValueError(f"{set_name}: selected source fails suitability rules")
        if row.get("rewrite_dev_protocol") != "symmetric-diverse-v31":
            raise ValueError(f"{set_name}: wrong v3.1 source protocol")
        if row.get("pool_partition") != "reserve" or row.get("split") != "train":
            raise ValueError(f"{set_name}: source is not reserve/train")
        if row.get("rewrite_recipe") not in v3.RECIPES:
            raise ValueError(f"{set_name}: invalid assigned recipe")
        if row.get("stance_topology") not in v3.TOPOLOGIES:
            raise ValueError(f"{set_name}: invalid assigned topology")
        if row.get("rewrite_output_order") not in v3.ORDERS:
            raise ValueError(f"{set_name}: invalid assigned output order")
        if v3.sha256_text(str(row["original_response"])) != row.get("original_response_sha256"):
            raise ValueError(f"{set_name}: source response hash mismatch")
    if _counts(rows, "rewrite_recipe") != {"A": expected_count // 2, "B": expected_count // 2}:
        raise ValueError(f"{set_name}: recipe assignment is not balanced")
    if _counts(rows, "stance_topology") != {
        topology: expected_count // 4 for topology in sorted(v3.TOPOLOGIES)
    }:
        raise ValueError(f"{set_name}: topology assignment is not balanced")
    if _counts(rows, "rewrite_output_order") != {
        "confident_first": expected_count // 2,
        "hedged_first": expected_count // 2,
    }:
        raise ValueError(f"{set_name}: output-order assignment is not balanced")
    if set_name == "canary" and any(value != 2 for value in _cross_counts(rows).values()):
        raise ValueError("canary: factorial cells must each contain two records")


def _jsonl_bytes(rows: Iterable[dict[str, Any]]) -> bytes:
    return v3.jsonl_bytes(rows)


def _audit_rows(
    rows: Sequence[dict[str, Any]], excluded_ids: set[str]
) -> tuple[list[dict[str, Any]], Counter[str]]:
    audit: list[dict[str, Any]] = []
    reason_counts: Counter[str] = Counter()
    for row in rows:
        primary_reasons = source_suitability_reasons(row)
        candidate_reasons = candidate_suitability_reasons(row)
        if str(row["source_id"]) in excluded_ids:
            primary_reasons = sorted(set(primary_reasons + ["previously_frozen_source"]))
            candidate_reasons = sorted(set(candidate_reasons + ["previously_frozen_source"]))
        reason_counts.update(primary_reasons)
        audit.append({
            "source_id": row["source_id"],
            "original_response_sha256": row["original_response_sha256"],
            "dataset": row["dataset"],
            "task": row["task"],
            "length_bin": row["length_bin"],
            "rewrite_family": row["rewrite_family"],
            "rewrite_output_order": row["rewrite_output_order"],
            "primary_eligible": not primary_reasons,
            "primary_exclusion_reasons": primary_reasons,
            "candidate_pool_eligible": not candidate_reasons,
            "candidate_pool_exclusion_reasons": candidate_reasons,
        })
    return audit, reason_counts


def _decorate(
    rows: Sequence[dict[str, Any]], set_name: str, status: str
) -> list[dict[str, Any]]:
    decorated: list[dict[str, Any]] = []
    for row in rows:
        item = dict(row)
        item["rewrite_dev_protocol"] = "symmetric-diverse-v31"
        item["rewrite_dev_set"] = set_name
        item["source_suitability_status"] = status
        item["source_suitability_rule_version"] = BUILDER_VERSION
        decorated.append(item)
    return decorated


def _review_packet(rows: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    packet = []
    for index, row in enumerate(rows, start=1):
        packet.append({
            "review_index": index,
            "source_id": row["source_id"],
            "original_response_sha256": row["original_response_sha256"],
            "dataset": row["dataset"],
            "task": row["task"],
            "length_bin": row["length_bin"],
            "prompt": row["prompt"],
            "original_response": row["original_response"],
            "automated_primary_suitability_reasons": source_suitability_reasons(row),
            "automated_candidate_pool_reasons": candidate_suitability_reasons(row),
            "source_only_semantic_review": "pending",
            "source_only_semantic_review_notes": "",
        })
    return packet


def build(config_path: Path = DEFAULT_CONFIG) -> dict[str, Any]:
    config_bytes = config_path.read_bytes()
    config = json.loads(config_bytes)
    if config.get("protocol_version") != PROTOCOL_VERSION:
        raise ValueError("Wrong v3.1 rewrite configuration")

    reserve_path = resolve(config["reserve_input_path"])
    main_path = resolve(config["main_input_path"])
    source_pool_manifest_path = resolve(config["source_pool_manifest_path"])
    source_pool_manifest = json.loads(source_pool_manifest_path.read_text(encoding="utf-8"))
    frozen_hashes = source_pool_manifest["private_output_sha256"]
    if v3.sha256_file(reserve_path) != frozen_hashes[reserve_path.name]:
        raise ValueError("Reserve bytes differ from the frozen source pool")
    if v3.sha256_file(main_path) != frozen_hashes[main_path.name]:
        raise ValueError("Main bytes differ from the frozen source pool")

    legacy_public_path = resolve(config["legacy_v3_public_manifest_path"])
    legacy_public = json.loads(legacy_public_path.read_text(encoding="utf-8"))
    legacy_dir = resolve(config["legacy_v3_private_manifest_dir"])
    legacy_rows: dict[str, list[dict[str, Any]]] = {}
    for name in ("smoke", "canary"):
        entry = legacy_public["sets"][name]
        path = legacy_dir / entry["file_name"]
        if v3.sha256_file(path) != entry["file_sha256"]:
            raise ValueError(f"Legacy v3 {name} bytes changed")
        rows = v3.read_jsonl(path)
        if v3.source_ids_sha256(rows) != entry["source_ids_sha256"]:
            raise ValueError(f"Legacy v3 {name} identities changed")
        legacy_rows[name] = rows

    reserve_rows = v3.read_jsonl(reserve_path)
    main_rows = v3.read_jsonl(main_path)
    main_ids = {str(row["source_id"]) for row in main_rows}
    prior_ids = {
        str(row["source_id"])
        for rows in legacy_rows.values()
        for row in rows
    }
    base_candidates = [
        row for row in reserve_rows
        if row.get("pool_partition") == "reserve"
        and row.get("split") == "train"
        and row.get("rewrite_family") in v3.RECIPES
    ]
    audit, reason_counts = _audit_rows(base_candidates, main_ids | prior_ids)
    primary_eligible = [
        row for row in base_candidates
        if str(row["source_id"]) not in main_ids | prior_ids
        and not source_suitability_reasons(row)
    ]

    seed = int(config["selection_seed"])
    selected: dict[str, list[dict[str, Any]]] = {}
    search_attempts: dict[str, int] = {}
    used = set(main_ids | prior_ids)
    for set_name, slots in (("smoke", v3.smoke_slots()),):
        set_config = config["sets"][set_name]
        rows = select_reviewed_smoke(primary_eligible, slots)
        attempt = 0
        rows = _decorate(rows, set_name, str(set_config["source_suitability_status"]))
        _validate_selected(
            rows,
            set_name=set_name,
            expected_count=int(set_config["count"]),
            main_ids=main_ids,
            prior_ids=prior_ids,
        )
        if not _matches_targets(rows, set_config):
            raise ValueError(f"{set_name}: exact quotas changed after decoration")
        selected[set_name] = rows
        search_attempts[set_name] = attempt
        used.update(str(row["source_id"]) for row in rows)
    smoke_ids = {str(row["source_id"]) for row in selected["smoke"]}

    candidate_config = config["canary_candidate_pool"]
    candidate_rows = [
        row for row in base_candidates
        if str(row["source_id"]) not in main_ids | prior_ids | smoke_ids
        and not candidate_suitability_reasons(row)
    ]
    candidate_rows.sort(key=lambda row: v3._stable_key(
        seed, "canary_candidate_pool", "source_review", str(row["source_id"])
    ))
    if len(candidate_rows) != int(candidate_config["count"]):
        raise ValueError(
            "Canary candidate-pool count changed; update the frozen review-pool configuration"
        )
    decorated_candidates: list[dict[str, Any]] = []
    for index, row in enumerate(candidate_rows, start=1):
        item = dict(row)
        item.pop("target_longer_member", None)
        item["source_suitability_status"] = candidate_config["source_suitability_status"]
        item["source_suitability_rule_version"] = BUILDER_VERSION
        item["canary_candidate_rank"] = index
        item["rewrite_dev_protocol"] = "symmetric-diverse-v31-source-review"
        item["rewrite_dev_set"] = "canary_candidate_pool"
        decorated_candidates.append(item)
    candidate_rows = decorated_candidates

    private_dir = resolve(config["private_manifest_dir"])
    set_summaries: dict[str, Any] = {}
    for set_name, rows in selected.items():
        set_config = config["sets"][set_name]
        output_path = private_dir / set_config["input_file"]
        payload = _jsonl_bytes(rows)
        v3.write_once_or_verify(output_path, payload)
        set_summaries[set_name] = {
            "count": len(rows),
            "file_name": output_path.name,
            "file_sha256": v3.sha256_bytes(payload),
            "source_ids_sha256": v3.source_ids_sha256(rows),
            "source_suitability_status": set_config["source_suitability_status"],
            "dataset_counts": _counts(rows, "dataset"),
            "task_counts": _counts(rows, "task"),
            "length_counts": _counts(rows, "length_bin"),
            "recipe_counts": _counts(rows, "rewrite_recipe"),
            "topology_counts": _counts(rows, "stance_topology"),
            "output_order_counts": _counts(rows, "rewrite_output_order"),
            "recipe_topology_order_counts": _cross_counts(rows),
            "selection_search_attempt": search_attempts[set_name],
            "private_file_write_policy": "write_once_or_verify_identical_bytes",
        }

    candidate_path = private_dir / candidate_config["input_file"]
    candidate_payload = _jsonl_bytes(candidate_rows)
    v3.write_once_or_verify(candidate_path, candidate_payload)

    audit_path = private_dir / "SOURCE_SUITABILITY_AUDIT.jsonl"
    audit_payload = _jsonl_bytes(audit)
    v3.write_once_or_verify(audit_path, audit_payload)
    review_path = private_dir / "SOURCE_CANARY_SOURCE_REVIEW.jsonl"
    review_payload = _jsonl_bytes(_review_packet(candidate_rows))
    v3.write_once_or_verify(review_path, review_payload)

    public = {
        "freeze_version": BUILDER_VERSION,
        "protocol_version": PROTOCOL_VERSION,
        "contains_source_text": False,
        "rewrite_generation_performed": False,
        "selection_seed": seed,
        "selection_scope": (
            "frozen reserve/train only; main/final-test, all v3 development sources, "
            "and recipe C excluded"
        ),
        "main_and_final_test_excluded": True,
        "all_v3_sources_excluded": True,
        "smoke_canary_disjoint": True,
        "source_suitability": {
            "rule_version": BUILDER_VERSION,
            "rules": SUITABILITY_RULES,
            "reserve_train_candidates": len(base_candidates),
            "previously_frozen_sources": sum(
                1 for row in base_candidates if str(row["source_id"]) in main_ids | prior_ids
            ),
            "primary_eligible_after_rules_and_exclusions": len(primary_eligible),
            "exclusion_reason_counts_nonexclusive": dict(sorted(reason_counts.items())),
            "private_audit_file_name": audit_path.name,
            "private_audit_file_sha256": v3.sha256_bytes(audit_payload),
            "private_canary_review_file_name": review_path.name,
            "private_canary_review_file_sha256": v3.sha256_bytes(review_payload),
        },
        "legacy_v3_canary": {
            "role": "transfer_or_diagnostic_only_not_v31_primary",
            "count": len(legacy_rows["canary"]),
            "file_sha256": legacy_public["sets"]["canary"]["file_sha256"],
            "source_ids_sha256": legacy_public["sets"]["canary"]["source_ids_sha256"],
            "bytes_modified": False,
        },
        "candidate_pool": {
            "count": len(candidate_rows),
            "status": candidate_config["source_suitability_status"],
            "role": "source_only_review_pool_not_authorized_for_generation",
            "file_name": candidate_path.name,
            "file_sha256": v3.sha256_bytes(candidate_payload),
            "source_ids_sha256": v3.source_ids_sha256(candidate_rows),
            "dataset_counts": _counts(candidate_rows, "dataset"),
            "task_counts": _counts(candidate_rows, "task"),
            "length_counts": _counts(candidate_rows, "length_bin"),
            "required_promoted_canary_count": 32,
        },
        "new_primary_canary_status": (
            "candidate_frozen_pending_source_only_semantic_review_not_authorized_for_generation"
        ),
        "config_sha256": v3.sha256_bytes(config_bytes),
        "builder_source_sha256": v3.sha256_file(Path(__file__)),
        "selection_algorithm": (
            "explicit suitability exclusions plus source-only agent-reviewed smoke "
            "allowlist, exact factorial slots, and exact coverage checks"
        ),
        "source_pool_manifest_sha256": v3.sha256_file(source_pool_manifest_path),
        "legacy_v3_public_manifest_sha256": v3.sha256_file(legacy_public_path),
        "source_input_sha256": {
            main_path.name: v3.sha256_file(main_path),
            reserve_path.name: v3.sha256_file(reserve_path),
        },
        "sets": set_summaries,
    }
    public_path = resolve(config["public_freeze_manifest_path"])
    public_bytes = (
        json.dumps(public, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    v3.write_once_or_verify(public_path, public_bytes)
    return public


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    args = parser.parse_args(argv)
    result = build(args.config.resolve())
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
