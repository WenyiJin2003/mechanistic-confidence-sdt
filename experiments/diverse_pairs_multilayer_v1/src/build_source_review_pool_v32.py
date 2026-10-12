"""Build the offline v3.2 source-only review pool.

This stage reads only pinned local acquisition caches.  It never downloads a
dataset, calls a language model, assigns a confidence label, or authorizes a
source for generation.  Regexes below are conservative prefilters; passing
them means only that a source should be shown to a reviewer.
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import re
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


BASE = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = BASE / "configs" / "source_review_v32.json"
PROTOCOL_VERSION = "source-only-review-v3.2"
BUILDER_VERSION = "3.2"

DATASETS = ("allenai/WildChat-1M", "nvidia/HelpSteer2")
TASKS = (
    "factual_explanation",
    "math_logic",
    "programming",
    "comparison_analysis",
    "summary_judgment",
)
LENGTHS = ("short", "medium", "long")

IDENTITY_FIELDS = (
    "source_id",
    "conversation_hash",
    "group_id",
    "development_template_group",
    "legacy_template_group",
    "normalized_prompt_sha256",
    "canonical_prompt_sha256",
    "original_response_sha256",
    "normalized_response_sha256",
)

PREFILTER_DESCRIPTIONS = {
    "roleplay_or_creative": (
        "direct requests or outputs for roleplay, fiction, dialogue, poetry, lyrics, "
        "screenplays, or other creative continuation"
    ),
    "email_or_correspondence": (
        "direct email, letter, message, invitation, apology, or cover-letter writing"
    ),
    "copywriting_or_promotion": (
        "advertising, marketing, SEO, slogans, social posts, or promotional copy"
    ),
    "refusal_or_clarification_only": (
        "assistant refusals, capability disclaimers, or responses that only request input"
    ),
    "meta_transformation": (
        "prompt generation, template filling, grammar-only editing, paraphrasing, or persona tasks"
    ),
    "code_only": (
        "responses dominated by code with too little explanatory prose for a content-preserving rewrite"
    ),
    "fixed_span_dominated": (
        "responses dominated by code, equations, URLs, quoted blocks, or tables that must remain fixed"
    ),
    "current_or_time_sensitive": (
        "requests explicitly tied to current, latest, live, recent, or date-dependent facts"
    ),
    "legal_guidance": (
        "personal or actionable legal, liability, litigation, contract, or regulatory guidance"
    ),
    "medical_guidance": (
        "personal diagnosis, treatment, dosage, medication, symptom, or emergency guidance"
    ),
    "uncertainty_central": (
        "the response's main content is inability to determine, missing information, or a future prediction"
    ),
}

ROLEPLAY_CREATIVE_RE = re.compile(
    r"\b(?:role\s*play|roleplay|act as (?:a|an|the)|pretend (?:you are|to be)|in character|"
    r"write (?:me )?(?:a |an )?(?:story|poem|song|lyrics|scene|screenplay|dialogue|fanfic)|"
    r"continue (?:the )?(?:story|scene|dialogue)|fictional character|choose[- ]your[- ]own|"
    r"bedtime story|verse|chorus|rpg adventure)\b",
    re.I,
)
CORRESPONDENCE_RE = re.compile(
    r"\b(?:write|draft|compose|edit|reply to|respond to|send)\b.{0,50}\b(?:e-?mail|letter|"
    r"message|invitation|apology|thank[- ]you note|cover letter)\b|"
    r"\b(?:dear (?:sir|madam|hiring manager|team)|to whom it may concern|best regards)\b",
    re.I | re.S,
)
COPYWRITING_RE = re.compile(
    r"\b(?:copywriting|copywriter|advertis(?:e|ement|ing)|marketing copy|sales copy|"
    r"promotional copy|seo[- ]optimized|keyword density|slogan|tagline|social media "
    r"(?:post|caption)|call to action|product description)\b",
    re.I,
)
REFUSAL_RE = re.compile(
    r"^\s*(?:i(?:'m| am) sorry[,;:]?\s+but|as an ai(?: language model)?|"
    r"i (?:cannot|can't|won't|am unable to)|i (?:do not|don't) have access|"
    r"please (?:provide|share|specify) (?:more|the|some)|could you (?:provide|clarify|specify))\b",
    re.I,
)
META_RE = re.compile(
    r"\b(?:generate (?:a |some |more )?prompts?|system prompt|prompt template|"
    r"fill (?:in|out) the (?:template|blanks?)|rewrite this|rephrase this|paraphrase this|"
    r"fix (?:the )?grammar|grammar and clarity|make (?:this|it) (?:more |less )?"
    r"(?:formal|informal|professional)|act like (?:a|an)|persona)\b",
    re.I,
)
CURRENT_RE = re.compile(
    r"\b(?:latest|most recent|right now|today(?:'s)?|live update|up[- ]to[- ]date|"
    r"as of (?:20\d{2}|today)|current (?:price|weather|news|president|prime minister|law|"
    r"regulation|schedule|ranking|version|release|market|exchange rate)|"
    r"in the (?:last|past) \d+ (?:hours?|days?|weeks?|months?))\b",
    re.I,
)
LEGAL_RE = re.compile(
    r"\b(?:legal advice|should i sue|can i sue|am i liable|could i be liable|"
    r"what are my legal rights|is it legal for me|my attorney|hire (?:an |a )?(?:attorney|lawyer)|"
    r"file (?:a )?(?:lawsuit|claim)|criminal charges|court order|breach of contract|"
    r"sign this contract|immigration status)\b",
    re.I,
)
MEDICAL_RE = re.compile(
    r"\b(?:diagnose (?:me|my)|do i have|what illness do i have|should i take|"
    r"what (?:dose|dosage)|increase (?:my )?dose|stop taking|prescribe|treat my|"
    r"my symptoms|medical emergency|chest pain|suicidal|self[- ]harm|"
    r"drug interaction|medication interaction)\b",
    re.I,
)
UNCERTAINTY_OPENING_RE = re.compile(
    r"^\s*(?:it (?:is|would be) (?:impossible|not possible|difficult) to "
    r"(?:know|determine|say|predict)|there (?:is|are) (?:not enough|insufficient) "
    r"(?:information|data)|(?:without|based on) (?:more|the provided) (?:information|context)[, ]+"
    r"(?:it|we) (?:cannot|can't)|i (?:cannot|can't) (?:know|determine|predict)|"
    r"the (?:answer|outcome) depends entirely on)\b",
    re.I,
)
FUTURE_PREDICTION_RE = re.compile(
    r"\b(?:will (?:the|my|i|it) .{0,45}\?|predict (?:the )?(?:future|outcome)|"
    r"what are the chances (?:that|of)|how likely is it that)\b",
    re.I | re.S,
)

FENCED_RE = re.compile(r"```.*?```|~~~.*?~~~", re.S)
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
DISPLAY_MATH_RE = re.compile(r"\$\$.*?\$\$|\\\[.*?\\\]", re.S)
URL_RE = re.compile(r"https?://\S+|www\.\S+", re.I)
QUOTE_BLOCK_RE = re.compile(r"(?m)(?:^\s*>.*(?:\n|$)){2,}")
TABLE_BLOCK_RE = re.compile(r"(?m)(?:^\s*\|.*\|\s*(?:\n|$)){2,}")
WORD_RE = re.compile(r"\b[\w'-]+\b", re.UNICODE)


class QuotaError(RuntimeError):
    """Raised when exact aggregate quotas cannot be met."""

    def __init__(self, message: str, details: Mapping[str, Any]):
        super().__init__(message)
        self.details = dict(details)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def jsonl_bytes(rows: Iterable[Mapping[str, Any]]) -> bytes:
    return "".join(
        json.dumps(dict(row), ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
        for row in rows
    ).encode("utf-8")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    # Iterate on physical ``\n`` records. ``str.splitlines`` would also split
    # U+2028/U+2029 characters that can legally appear inside a JSON string.
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def resolve(value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else BASE / path


def write_once_or_verify(path: Path, data: bytes) -> bool:
    if path.exists():
        if path.read_bytes() != data:
            raise FileExistsError(f"Refusing to replace non-identical frozen file: {path}")
        return True
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(data)
    temporary.replace(path)
    return False


def source_ids_sha256(rows: Sequence[Mapping[str, Any]]) -> str:
    return sha256_text("".join(f"{row['source_id']}\n" for row in rows))


def _counts(rows: Sequence[Mapping[str, Any]], field: str) -> dict[str, int]:
    return dict(sorted(Counter(str(row[field]) for row in rows).items()))


def _nonspace_length(text: str) -> int:
    return len(re.sub(r"\s+", "", text))


def _span_coverage(text: str, patterns: Sequence[re.Pattern[str]]) -> int:
    covered: set[int] = set()
    for pattern in patterns:
        for match in pattern.finditer(text):
            covered.update(range(match.start(), match.end()))
    return sum(not text[index].isspace() for index in covered)


def prefilter_reasons(row: Mapping[str, Any]) -> list[str]:
    """Return high-precision review exclusions; an empty result is not approval."""
    prompt = str(row.get("prompt", ""))
    response = str(row.get("original_response", ""))
    joined = f"{prompt}\n{response}"
    reasons: list[str] = []
    if ROLEPLAY_CREATIVE_RE.search(joined):
        reasons.append("roleplay_or_creative")
    if CORRESPONDENCE_RE.search(joined):
        reasons.append("email_or_correspondence")
    if COPYWRITING_RE.search(joined):
        reasons.append("copywriting_or_promotion")
    if REFUSAL_RE.search(response):
        reasons.append("refusal_or_clarification_only")
    if META_RE.search(prompt):
        reasons.append("meta_transformation")
    prose = FENCED_RE.sub(" ", response)
    prose = INLINE_CODE_RE.sub(" ", prose)
    prose_words = len(WORD_RE.findall(prose))
    code_chars = _span_coverage(response, (FENCED_RE, INLINE_CODE_RE))
    nonspace_chars = max(1, _nonspace_length(response))
    if code_chars / nonspace_chars >= 0.70 and prose_words < 30:
        reasons.append("code_only")
    fixed_chars = _span_coverage(
        response,
        (FENCED_RE, INLINE_CODE_RE, DISPLAY_MATH_RE, URL_RE, QUOTE_BLOCK_RE, TABLE_BLOCK_RE),
    )
    if fixed_chars / nonspace_chars >= 0.58:
        reasons.append("fixed_span_dominated")
    if CURRENT_RE.search(prompt):
        reasons.append("current_or_time_sensitive")
    if LEGAL_RE.search(joined):
        reasons.append("legal_guidance")
    if MEDICAL_RE.search(joined):
        reasons.append("medical_guidance")
    if UNCERTAINTY_OPENING_RE.search(response[:500]) or FUTURE_PREDICTION_RE.search(prompt):
        reasons.append("uncertainty_central")
    return sorted(set(reasons))


def _identity_values(row: Mapping[str, Any]) -> dict[str, str]:
    return {
        field: str(row[field])
        for field in IDENTITY_FIELDS
        if row.get(field) not in (None, "")
    }


def _load_exclusion_index(paths: Sequence[Path]) -> tuple[dict[str, set[str]], list[dict[str, Any]]]:
    index = {field: set() for field in IDENTITY_FIELDS}
    summaries: list[dict[str, Any]] = []
    for path in paths:
        if not path.is_file():
            raise FileNotFoundError(f"Required exclusion anchor is missing: {path}")
        rows = read_jsonl(path)
        for row in rows:
            for field, value in _identity_values(row).items():
                index[field].add(value)
        summaries.append({
            "file_name": path.name,
            "file_sha256": sha256_file(path),
            "row_count": len(rows),
        })
    return index, summaries


def exclusion_match_fields(row: Mapping[str, Any], index: Mapping[str, set[str]]) -> list[str]:
    return sorted(
        field
        for field, value in _identity_values(row).items()
        if value in index.get(field, set())
    )


def _expand_cache_paths(patterns: Sequence[str]) -> list[Path]:
    paths: list[Path] = []
    for pattern in patterns:
        resolved = resolve(pattern)
        matches = sorted(Path(value) for value in glob.glob(str(resolved)))
        if not matches:
            raise FileNotFoundError(f"Local cache pattern matched no files: {pattern}")
        paths.extend(matches)
    unique = sorted(set(paths))
    if not unique:
        raise FileNotFoundError("No local acquisition caches were configured")
    return unique


def _load_verified_caches(config: Mapping[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    summaries: list[dict[str, Any]] = []
    expected_fingerprint = str(config["expected_acquisition_fingerprint"])
    expected_revisions = dict(config["dataset_revisions"])
    for path in _expand_cache_paths(config["cache_patterns"]):
        metadata_path = path.with_name(path.name + ".meta.json")
        if not metadata_path.is_file():
            raise FileNotFoundError(f"Cache metadata is missing: {metadata_path}")
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        actual_hash = sha256_file(path)
        if metadata.get("acquisition_fingerprint") != expected_fingerprint:
            raise ValueError(f"Acquisition fingerprint drifted for {path}")
        if metadata.get("jsonl_sha256") != actual_hash:
            raise ValueError(f"Cache hash mismatch for {path}")
        cache_rows = read_jsonl(path)
        if int(metadata.get("source_count", -1)) != len(cache_rows):
            raise ValueError(f"Cache row count mismatch for {path}")
        for row in cache_rows:
            dataset = str(row.get("dataset", ""))
            if dataset not in expected_revisions:
                raise ValueError(f"Unexpected dataset in cache: {dataset}")
            if row.get("dataset_revision") != expected_revisions[dataset]:
                raise ValueError(f"Dataset revision drifted in {path}")
            response = str(row.get("original_response", ""))
            if sha256_text(response) != row.get("original_response_sha256"):
                raise ValueError(f"Source response hash mismatch in {path}")
        rows.extend(cache_rows)
        summaries.append({
            "file_name": path.name,
            "file_sha256": actual_hash,
            "row_count": len(cache_rows),
        })
    return rows, summaries


def quota_gap_report(
    rows: Sequence[Mapping[str, Any]], quotas: Mapping[str, Mapping[str, int]]
) -> dict[str, Any]:
    fields = {
        "dataset": "dataset_counts",
        "task": "task_counts",
        "length_bin": "length_counts",
    }
    report: dict[str, Any] = {}
    for field, quota_name in fields.items():
        available = Counter(str(row[field]) for row in rows)
        required = {str(key): int(value) for key, value in quotas[quota_name].items()}
        report[quota_name] = {
            "required": dict(sorted(required.items())),
            "available": {key: available[key] for key in sorted(required)},
            "deficit": {
                key: max(0, required[key] - available[key]) for key in sorted(required)
            },
        }
    return report


def select_exact_margins_by_cells(
    rows: Sequence[dict[str, Any]],
    quotas: Mapping[str, Mapping[str, int]],
) -> list[dict[str, Any]]:
    """Select deterministic exact margins, preferring earlier frozen hash cells."""
    datasets = tuple(sorted(quotas["dataset_counts"]))
    tasks = tuple(sorted(quotas["task_counts"]))
    lengths = tuple(sorted(quotas["length_counts"]))
    expected = sum(int(value) for value in quotas["dataset_counts"].values())
    if sum(map(int, quotas["task_counts"].values())) != expected or sum(
        map(int, quotas["length_counts"].values())
    ) != expected:
        raise ValueError("Quota margins have different totals")

    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        key = (str(row["dataset"]), str(row["task"]), str(row["length_bin"]))
        if key[0] in datasets and key[1] in tasks and key[2] in lengths:
            grouped[key].append(row)
    for values in grouped.values():
        values.sort(key=lambda row: str(row["candidate_sort_sha256"]))
    keys = tuple(sorted(grouped, key=lambda key: (grouped[key][0]["candidate_sort_sha256"], key)))

    suffix_dataset: list[Counter[str]] = [Counter() for _ in range(len(keys) + 1)]
    suffix_task: list[Counter[str]] = [Counter() for _ in range(len(keys) + 1)]
    suffix_length: list[Counter[str]] = [Counter() for _ in range(len(keys) + 1)]
    for index in range(len(keys) - 1, -1, -1):
        suffix_dataset[index] = Counter(suffix_dataset[index + 1])
        suffix_task[index] = Counter(suffix_task[index + 1])
        suffix_length[index] = Counter(suffix_length[index + 1])
        dataset, task, length = keys[index]
        count = len(grouped[keys[index]])
        suffix_dataset[index][dataset] += count
        suffix_task[index][task] += count
        suffix_length[index][length] += count

    initial = (
        tuple(int(quotas["dataset_counts"][name]) for name in datasets),
        tuple(int(quotas["task_counts"][name]) for name in tasks),
        tuple(int(quotas["length_counts"][name]) for name in lengths),
    )

    @lru_cache(maxsize=None)
    def solve(
        index: int,
        remaining_datasets: tuple[int, ...],
        remaining_tasks: tuple[int, ...],
        remaining_lengths: tuple[int, ...],
    ) -> tuple[int, ...] | None:
        if any(value < 0 for value in remaining_datasets + remaining_tasks + remaining_lengths):
            return None
        if sum(remaining_datasets) != sum(remaining_tasks) or sum(remaining_tasks) != sum(remaining_lengths):
            return None
        if any(
            remaining_datasets[pos] > suffix_dataset[index][name]
            for pos, name in enumerate(datasets)
        ) or any(
            remaining_tasks[pos] > suffix_task[index][name]
            for pos, name in enumerate(tasks)
        ) or any(
            remaining_lengths[pos] > suffix_length[index][name]
            for pos, name in enumerate(lengths)
        ):
            return None
        if index == len(keys):
            return () if not any(
                remaining_datasets + remaining_tasks + remaining_lengths
            ) else None
        dataset, task, length = keys[index]
        d_pos, t_pos, l_pos = datasets.index(dataset), tasks.index(task), lengths.index(length)
        maximum = min(
            len(grouped[keys[index]]),
            remaining_datasets[d_pos],
            remaining_tasks[t_pos],
            remaining_lengths[l_pos],
        )
        for count in range(maximum, -1, -1):
            next_datasets = list(remaining_datasets)
            next_tasks = list(remaining_tasks)
            next_lengths = list(remaining_lengths)
            next_datasets[d_pos] -= count
            next_tasks[t_pos] -= count
            next_lengths[l_pos] -= count
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
        details = quota_gap_report(rows, quotas)
        details["joint_quota_feasible"] = False
        raise QuotaError("No exact joint allocation satisfies all candidate quotas", details)
    selected: list[dict[str, Any]] = []
    for key, count in zip(keys, allocation):
        selected.extend(grouped[key][:count])
    selected.sort(key=lambda row: str(row["candidate_sort_sha256"]))
    if len(selected) != expected:
        raise AssertionError("Exact quota selector returned the wrong row count")
    return selected


def _review_packet(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    packet: list[dict[str, Any]] = []
    for row in rows:
        packet.append({
            "candidate_rank": row["candidate_rank"],
            "candidate_sort_sha256": row["candidate_sort_sha256"],
            "source_id": row["source_id"],
            "original_response_sha256": row["original_response_sha256"],
            "dataset": row["dataset"],
            "task": row["task"],
            "length_bin": row["length_bin"],
            "prompt": row["prompt"],
            "original_response": row["original_response"],
            "automated_prefilter_reasons": [],
            "automated_prefilter_status": "passed_for_review_not_human_approved",
            "review_decision": "",
            "content_stability": "",
            "rewrite_suitability": "",
            "uncertainty_central": "",
            "high_stakes_or_current": "",
            "review_notes": "",
        })
    return packet


def _validate_exact_counts(
    rows: Sequence[Mapping[str, Any]], quotas: Mapping[str, Mapping[str, int]]
) -> None:
    expected = {
        "dataset": dict(sorted((str(k), int(v)) for k, v in quotas["dataset_counts"].items())),
        "task": dict(sorted((str(k), int(v)) for k, v in quotas["task_counts"].items())),
        "length_bin": dict(sorted((str(k), int(v)) for k, v in quotas["length_counts"].items())),
    }
    for field, target in expected.items():
        if _counts(rows, field) != target:
            raise ValueError(f"Selected {field} counts differ from the frozen quota")


def build(config_path: Path = DEFAULT_CONFIG) -> dict[str, Any]:
    config_bytes = config_path.read_bytes()
    config = json.loads(config_bytes)
    if config.get("protocol_version") != PROTOCOL_VERSION:
        raise ValueError("Wrong v3.2 source-review protocol")
    seed = int(config["selection_seed"])

    raw_rows, cache_summaries = _load_verified_caches(config)
    exclusion_paths = [resolve(value) for value in config["required_exclusion_paths"]]
    exclusion_index, exclusion_summaries = _load_exclusion_index(exclusion_paths)

    exclusion_match_counts: Counter[str] = Counter()
    prefilter_counts: Counter[str] = Counter()
    duplicate_counts: Counter[str] = Counter()
    seen = {field: set() for field in IDENTITY_FIELDS}
    eligible: list[dict[str, Any]] = []
    ordered = sorted(
        raw_rows,
        key=lambda row: sha256_text(
            f"{seed}:source-review-v32:{row.get('source_id')}:{row.get('original_response_sha256')}"
        ),
    )
    for source in ordered:
        match_fields = exclusion_match_fields(source, exclusion_index)
        if match_fields:
            exclusion_match_counts.update(match_fields)
            continue
        duplicate_fields = [
            field
            for field, value in _identity_values(source).items()
            if value in seen[field]
        ]
        if duplicate_fields:
            duplicate_counts.update(duplicate_fields)
            continue
        reasons = prefilter_reasons(source)
        if reasons:
            prefilter_counts.update(reasons)
            continue
        if source.get("dataset") not in DATASETS or source.get("task") not in TASKS or source.get("length_bin") not in LENGTHS:
            prefilter_counts["outside_frozen_strata"] += 1
            continue
        item = dict(source)
        item["candidate_sort_sha256"] = sha256_text(
            f"{seed}:source-review-v32:{source['source_id']}:{source['original_response_sha256']}"
        )
        item["source_review_protocol"] = PROTOCOL_VERSION
        item["automated_prefilter_status"] = "passed_for_review_not_human_approved"
        item["human_source_review_status"] = "pending"
        eligible.append(item)
        for field, value in _identity_values(source).items():
            seen[field].add(value)

    quotas = config["candidate_quotas"]
    selected = select_exact_margins_by_cells(eligible, quotas)
    for rank, row in enumerate(selected, start=1):
        row["candidate_rank"] = rank
    _validate_exact_counts(selected, quotas)
    if len({row["source_id"] for row in selected}) != len(selected):
        raise ValueError("Candidate review pool contains duplicate source IDs")
    if any(exclusion_match_fields(row, exclusion_index) for row in selected):
        raise ValueError("Candidate review pool overlaps a required exclusion anchor")

    candidate_path = resolve(config["private_candidate_file"])
    review_path = resolve(config["private_review_packet"])
    candidate_payload = jsonl_bytes(selected)
    review_payload = jsonl_bytes(_review_packet(selected))
    write_once_or_verify(candidate_path, candidate_payload)
    write_once_or_verify(review_path, review_payload)

    public = {
        "freeze_version": BUILDER_VERSION,
        "protocol_version": PROTOCOL_VERSION,
        "contains_source_text": False,
        "network_calls": 0,
        "model_calls": 0,
        "rewrite_generation_performed": False,
        "selection_seed": seed,
        "human_source_review_status": "pending",
        "heuristic_pass_is_human_approval": False,
        "prefilter_rules": PREFILTER_DESCRIPTIONS,
        "cache_inputs": cache_summaries,
        "raw_cached_row_count": len(raw_rows),
        "required_exclusion_anchors": exclusion_summaries,
        "excluded_by_anchor_field_nonexclusive": dict(sorted(exclusion_match_counts.items())),
        "removed_cache_duplicates_by_field_nonexclusive": dict(sorted(duplicate_counts.items())),
        "prefilter_exclusion_reason_counts_nonexclusive": dict(sorted(prefilter_counts.items())),
        "eligible_after_automated_prefilters_not_human_approved": len(eligible),
        "candidate_review_pool": {
            "count": len(selected),
            "status": "pending_source_only_human_review_not_authorized_for_generation",
            "file_name": candidate_path.name,
            "file_sha256": sha256_bytes(candidate_payload),
            "source_ids_sha256": source_ids_sha256(selected),
            "dataset_counts": _counts(selected, "dataset"),
            "task_counts": _counts(selected, "task"),
            "length_counts": _counts(selected, "length_bin"),
        },
        "review_packet": {
            "count": len(selected),
            "file_name": review_path.name,
            "blank_template_sha256": sha256_bytes(review_payload),
            "required_categorical_fields": [
                "review_decision",
                "content_stability",
                "rewrite_suitability",
                "uncertainty_central",
                "high_stakes_or_current",
            ],
            "instructions": (
                "Copy this immutable blank packet to the configured completed-review file; "
                "fill every categorical field. Automated prefilter passage is not approval."
            ),
        },
        "promotion_targets": config["promotion_targets"],
        "config_sha256": sha256_bytes(config_bytes),
        "builder_source_sha256": sha256_file(Path(__file__)),
    }
    public_path = resolve(config["public_freeze_manifest"])
    public_bytes = (
        json.dumps(public, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    write_once_or_verify(public_path, public_bytes)
    return public


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    args = parser.parse_args(argv)
    try:
        result = build(args.config.resolve())
    except QuotaError as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc), "details": exc.details}, sort_keys=True))
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
