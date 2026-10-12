"""Acquire, de-duplicate, split, and freeze the 1,000-source study pool.

The selected source text is private and untrusted. This program never executes
dataset content. Public outputs contain provenance hashes and aggregate coverage
only. It does not generate rewrites, run the representation model, or train a
probe.

Acquisition is resumable at the dataset/shard level. Existing complete files are
validated and reused byte-for-byte; an existing file with different bytes is
never overwritten. The earlier 50-pair development and challenge files are read
only as exclusion anchors.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
import random
import re
import unicodedata
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

import yaml


BASE = Path(__file__).resolve().parents[1]
REPO = BASE.parents[1]
DEFAULT_CONFIG = BASE / "configs" / "source_pool_1000.yaml"
TASKS = [
    "factual_explanation",
    "math_logic",
    "programming",
    "comparison_analysis",
    "summary_judgment",
]
LENGTHS = ["short", "medium", "long"]
DATASETS = ["allenai/WildChat-1M", "nvidia/HelpSteer2"]
SPLITS = ["train", "validation", "test"]
PARTITIONS = ["main", "reserve"]

PII = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    r"|\b\d{3}-\d{2}-\d{4}\b|\b(?:\+?\d[\d ()-]{7,}\d)\b"
)
EXCLUDED = re.compile(
    r"\b(?:suicide|self.harm|sexual|porn|explosive|weapon|malware|ransomware|"
    r"phishing|credit.card|passport|social.security|home.address)\b",
    re.I,
)
CREATIVE = re.compile(
    r"\b(?:write|compose|create)\b.{0,55}\b(?:poem|song|lyrics|fictional.story|"
    r"bedtime.story|erotic)\b",
    re.I | re.S,
)
REFUSAL = re.compile(
    r"^\s*(?:I(?:'m| am) sorry|I cannot assist|I can't assist|I cannot provide|As an AI)",
    re.I,
)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def normalize(text: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", text).casefold().split())


def canonical_prompt(text: str) -> str:
    """Collapse common variable slots without reducing a prompt to its task tag."""
    value = normalize(text)
    value = re.sub(r"https?://\S+|www\.\S+", "<url>", value)
    value = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", "<email>", value)
    value = re.sub(r"\b[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}\b", "<uuid>", value)
    value = re.sub(r"\b0x[0-9a-f]+\b|\b\d+(?:[.,]\d+)*\b", "<num>", value)
    value = re.sub(r"\s+", " ", value).strip()
    if "pretend you are a tutor" in value:
        return "factoring_tutor_template"
    if "safetensors" in value and "convert" in value:
        return "safetensors_conversion_template"
    return value


def legacy_template_group(prompt: str) -> str:
    value = re.sub(
        r"\b(?:antonius|carmen|anthony|ben)\b|\d+(?:\.\d+)?",
        "<var>",
        normalize(prompt),
    )
    if "pretend you are a tutor" in value:
        value = "factoring_tutor_template"
    if "safetensors" in value:
        value = "safetensors_conversion_template"
    return sha256_text(value)


def shingles(text: str, size: int) -> frozenset[str]:
    words = re.findall(r"\w+", normalize(text), re.UNICODE)
    return frozenset(" ".join(words[i:i + size]) for i in range(max(0, len(words) - size + 1)))


def classify(prompt: str) -> str:
    """Score-free heuristic tag used only for coverage stratification."""
    p = prompt.casefold()
    if re.search(
        r"\b(?:python|javascript|typescript|java|c\+\+|sql|html|css|programming|"
        r"debug|function|algorithm|code|script|regex|program)\b",
        p,
    ):
        return "programming"
    if re.search(
        r"\b(?:calculate|solve|equation|arithmetic|algebra|probability|mathematical|"
        r"math|logic|proof|integral|derivative|factor|vectors|orthogonal)\b|"
        r"\d\s*[+*/=]\s*\d",
        p,
    ):
        return "math_logic"
    if re.search(
        r"\b(?:summari[sz]e|summary|summaries|synopsis|assess|evaluate|review|"
        r"classify|identify.the.main|main.idea)\b",
        p,
    ):
        return "summary_judgment"
    if re.search(
        r"\b(?:compare|comparison|contrast|versus|pros.and.cons|advantages|"
        r"disadvantages|analy[sz]e|argument|trade.off|better)\b",
        p,
    ):
        return "comparison_analysis"
    return "factual_explanation"


def stable_key(seed: int, salt: str, value: str) -> str:
    return sha256_text(f"{seed}:{salt}:{value}")


def jsonl_bytes(rows: Iterable[dict]) -> bytes:
    return "".join(
        json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
        for row in rows
    ).encode("utf-8")


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(data)
    temporary.replace(path)


def write_once_or_verify(path: Path, data: bytes) -> bool:
    """Return True when an identical existing file was reused."""
    if path.exists():
        if path.read_bytes() != data:
            raise FileExistsError(f"Refusing to overwrite non-identical frozen file: {path}")
        return True
    atomic_write(path, data)
    return False


def load_config(path: Path = DEFAULT_CONFIG) -> tuple[dict, str]:
    raw = path.read_bytes()
    config = yaml.safe_load(raw)
    if config.get("phase") != "freeze_source_pool_1000":
        raise ValueError("Wrong source-pool configuration phase")
    return config, sha256_bytes(raw)


def acquisition_fingerprint(config: dict) -> str:
    """Hash only fields that determine cached candidate contents."""
    payload = {
        "seed": config["seed"],
        "datasets": config["datasets"],
        "screening": config["screening"],
        "acquisition": config["acquisition"],
        "tokenizer": config["representation_tokenizer"],
    }
    return sha256_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")))


def read_candidate_cache(path: Path, config: dict) -> list[dict] | None:
    if not path.exists():
        return None
    metadata_path = path.with_name(path.name + ".meta.json")
    if not metadata_path.exists():
        raise ValueError(f"Candidate cache has no fingerprint metadata: {path}")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if metadata.get("acquisition_fingerprint") != acquisition_fingerprint(config):
        raise ValueError(f"Candidate cache was built under a different acquisition config: {path}")
    if metadata.get("jsonl_sha256") != sha256_file(path):
        raise ValueError(f"Candidate cache hash mismatch: {path}")
    return read_jsonl(path)


def write_candidate_cache(path: Path, rows: list[dict], config: dict, provenance: dict) -> None:
    data = jsonl_bytes(rows)
    write_once_or_verify(path, data)
    metadata = {
        "acquisition_fingerprint": acquisition_fingerprint(config),
        "jsonl_sha256": sha256_bytes(data),
        "source_count": len(rows),
        **provenance,
    }
    metadata_bytes = (json.dumps(metadata, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")
    write_once_or_verify(path.with_name(path.name + ".meta.json"), metadata_bytes)


def resolve_path(value: str, repo: Path = REPO) -> Path:
    path = Path(value)
    return path if path.is_absolute() else repo / path


def validate_legacy_pins(config: dict) -> None:
    """Fail if this config drifts from the already published pilot pins."""
    source = (BASE / "src" / "prepare_review_sources.py").read_text(encoding="utf-8")
    expected = {
        "allenai/WildChat-1M": re.search(r'^WILD_REV = "([0-9a-f]+)"', source, re.M).group(1),
        "nvidia/HelpSteer2": re.search(r'^HELP_REV = "([0-9a-f]+)"', source, re.M).group(1),
    }
    for dataset, revision in expected.items():
        if config["datasets"][dataset]["revision"] != revision:
            raise ValueError(f"{dataset} revision drifted from prepare_review_sources.py")
    tokenizer_revision = config["representation_tokenizer"]["revision"]
    if tokenizer_revision not in source:
        raise ValueError("Tokenizer snapshot drifted from prepare_review_sources.py")


def _eligible(prompt: str, response: str, tokenizer: Any, config: dict) -> tuple[bool, str, int, int]:
    rules = config["screening"]
    if not isinstance(prompt, str) or not isinstance(response, str) or not prompt.strip() or not response.strip():
        return False, "empty", 0, 0
    text = prompt + "\n" + response
    if "<extra_id_1>" in text or "<|" in text:
        return False, "encoded_or_special_context", 0, 0
    if PII.search(text):
        return False, "possible_pii", 0, 0
    if EXCLUDED.search(text) or CREATIVE.search(prompt) or REFUSAL.search(response):
        return False, "not_applicable", 0, 0
    if len(response.split()) < rules["min_response_words"]:
        return False, "too_short", 0, 0
    letters = re.findall(r"[^\W\d_]", text, re.UNICODE)
    if not letters or sum(character.isascii() for character in letters) / len(letters) < 0.94:
        return False, "language_screen", 0, 0
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt},
        {"role": "assistant", "content": response},
    ]
    total = len(tokenizer.apply_chat_template(messages, tokenize=True))
    response_tokens = len(tokenizer(response, add_special_tokens=False)["input_ids"])
    if total > rules["max_input_tokens"] or response_tokens > rules["max_response_tokens"]:
        return False, "length_reserve_for_rewrites", total, response_tokens
    return True, "eligible", total, response_tokens


def prepare_candidate(raw: dict, tokenizer: Any, config: dict) -> tuple[dict | None, str]:
    prompt = raw.get("prompt", "")
    response = raw.get("original_response", "")
    ok, reason, total, response_tokens = _eligible(prompt, response, tokenizer, config)
    if not ok:
        return None, reason
    prompt_hash = sha256_text(normalize(prompt))
    canonical_hash = sha256_text(canonical_prompt(prompt))
    rules = config["screening"]
    if response_tokens <= rules["short_max_tokens"]:
        length = "short"
    elif response_tokens <= rules["medium_max_tokens"]:
        length = "medium"
    else:
        length = "long"
    row = dict(raw)
    row.update(
        normalized_prompt_sha256=prompt_hash,
        normalized_response_sha256=sha256_text(normalize(response)),
        original_response_sha256=sha256_text(response),
        canonical_prompt_sha256=canonical_hash,
        development_template_group=canonical_hash,
        legacy_template_group=legacy_template_group(prompt),
        group_id="group-" + canonical_hash,
        task=classify(prompt),
        task_label_method="keyword_heuristic_pending_human_review",
        target_input_tokens=total,
        response_tokens=response_tokens,
        length_bin=length,
        human_review="pending",
    )
    return row, "eligible"


class NearIndex:
    def __init__(self, size: int, threshold: float):
        self.size = size
        self.threshold = threshold
        self.values: list[frozenset[str]] = []
        self.inverted: dict[str, set[int]] = defaultdict(set)

    def overlaps(self, text: str) -> bool:
        value = shingles(text, self.size)
        if not value:
            return False
        possible: set[int] = set()
        for item in value:
            possible.update(self.inverted.get(item, ()))
        for index in possible:
            other = self.values[index]
            if len(value & other) / max(1, len(value | other)) >= self.threshold:
                return True
        return False

    def add(self, text: str) -> None:
        value = shingles(text, self.size)
        if not value:
            return
        index = len(self.values)
        self.values.append(value)
        for item in value:
            self.inverted[item].add(index)


class DuplicateIndex:
    """Unified identity/hash/group and near-text leakage screen."""

    def __init__(self, config: dict):
        rules = config["screening"]
        self.identities: set[str] = set()
        self.groups: set[str] = set()
        self.prompt_hashes: set[str] = set()
        self.response_hashes: set[str] = set()
        self.prompts = NearIndex(rules["near_prompt_shingle_size"], rules["near_prompt_jaccard"])
        self.responses = NearIndex(rules["near_response_shingle_size"], rules["near_response_jaccard"])

    @staticmethod
    def _values(row: dict, fields: Iterable[str]) -> set[str]:
        return {str(row[field]) for field in fields if row.get(field) not in (None, "")}

    def anchors(self, row: dict) -> tuple[set[str], set[str], set[str], set[str]]:
        identities = self._values(row, ["source_id", "conversation_hash"])
        groups = self._values(
            row,
            ["group_id", "development_template_group", "legacy_template_group", "canonical_prompt_sha256"],
        )
        prompt_hashes = self._values(row, ["normalized_prompt_sha256"])
        response_hashes = self._values(row, ["original_response_sha256", "normalized_response_sha256"])
        prompt = row.get("prompt")
        response = row.get("original_response")
        if isinstance(prompt, str) and prompt:
            normalized_hash = sha256_text(normalize(prompt))
            canonical_hash = sha256_text(canonical_prompt(prompt))
            prompt_hashes.add(normalized_hash)
            groups.update({"group-" + normalized_hash, canonical_hash, legacy_template_group(prompt)})
        if isinstance(response, str) and response:
            response_hashes.update({sha256_text(response), sha256_text(normalize(response))})
        return identities, groups, prompt_hashes, response_hashes

    def duplicate_reason(self, row: dict) -> str | None:
        identities, groups, prompt_hashes, response_hashes = self.anchors(row)
        if identities & self.identities:
            return "identity_overlap"
        if groups & self.groups:
            return "group_or_canonical_prompt_overlap"
        if prompt_hashes & self.prompt_hashes:
            return "exact_prompt_overlap"
        if response_hashes & self.response_hashes:
            return "exact_response_overlap"
        prompt = row.get("prompt")
        response = row.get("original_response")
        if isinstance(prompt, str) and self.prompts.overlaps(prompt):
            return "near_prompt_overlap"
        if isinstance(response, str) and self.responses.overlaps(response):
            return "near_response_overlap"
        return None

    def add(self, row: dict) -> None:
        identities, groups, prompt_hashes, response_hashes = self.anchors(row)
        self.identities.update(identities)
        self.groups.update(groups)
        self.prompt_hashes.update(prompt_hashes)
        self.response_hashes.update(response_hashes)
        if isinstance(row.get("prompt"), str):
            self.prompts.add(row["prompt"])
        if isinstance(row.get("original_response"), str):
            self.responses.add(row["original_response"])


def load_old_exclusions(config: dict, repo: Path = REPO) -> list[dict]:
    rows: list[dict] = []
    for value in config["exclusions"]["old_jsonl"]:
        path = resolve_path(value, repo)
        if path.exists():
            rows.extend(read_jsonl(path))
    for value in config["exclusions"]["old_manifests"]:
        path = resolve_path(value, repo)
        if path.exists():
            payload = json.loads(path.read_text(encoding="utf-8"))
            rows.extend(payload.get("source_records", []))
    unique_ids = {row.get("source_id") for row in rows if row.get("source_id")}
    minimum = config["exclusions"].get("minimum_old_source_ids", 0)
    if len(unique_ids) < minimum:
        raise RuntimeError(
            f"Only {len(unique_ids)} old source IDs were found; need at least {minimum} to prevent leakage"
        )
    return rows


def screen_and_deduplicate(
    candidates: list[dict], old_rows: list[dict], config: dict
) -> tuple[list[dict], Counter]:
    index = DuplicateIndex(config)
    for row in old_rows:
        index.add(row)
    seed = config["seed"]
    accepted: list[dict] = []
    rejected: Counter = Counter()
    for row in sorted(candidates, key=lambda item: stable_key(seed, "candidate", item["source_id"])):
        reason = index.duplicate_reason(row)
        if reason:
            rejected[reason] += 1
            continue
        index.add(row)
        accepted.append(dict(row))
    return accepted, rejected


def weighted_counts(total: int, weights: dict[str, float], salt: str, seed: int) -> dict[str, int]:
    if total < 0 or not weights or any(weight < 0 for weight in weights.values()):
        raise ValueError("Invalid weighted allocation")
    scale = sum(weights.values())
    if scale <= 0:
        raise ValueError("Allocation weights must sum to a positive value")
    raw = {key: total * value / scale for key, value in weights.items()}
    result = {key: math.floor(value) for key, value in raw.items()}
    remainder = total - sum(result.values())
    order = sorted(
        weights,
        key=lambda key: (-(raw[key] - result[key]), stable_key(seed, salt, key)),
    )
    for key in order[:remainder]:
        result[key] += 1
    return result


def required_task_counts(config: dict, dataset: str) -> Counter:
    """Exact task totals implied by every main/reserve bucket for one source."""
    result: Counter = Counter()
    for partition in PARTITIONS:
        for split in SPLITS:
            count = config["quotas"][partition][split][dataset]
            result.update(weighted_counts(
                count,
                config["stratification"]["tasks"],
                f"task:{partition}:{split}:{dataset}",
                config["seed"],
            ))
    return result


def wildchat_stop_targets(config: dict) -> Counter:
    required = required_task_counts(config, "allenai/WildChat-1M")
    multiplier = config["acquisition"]["wildchat_stop_buffer_multiplier"]
    minimum = config["acquisition"]["wildchat_stop_buffer_minimum"]
    return Counter({task: math.ceil(count * multiplier) + minimum for task, count in required.items()})


def _pick_bucket(
    available: list[dict],
    count: int,
    dataset: str,
    partition: str,
    split: str,
    config: dict,
) -> list[dict]:
    seed = config["seed"]
    task_targets = weighted_counts(
        count,
        config["stratification"]["tasks"],
        f"task:{partition}:{split}:{dataset}",
        seed,
    )
    length_targets = weighted_counts(
        count,
        config["stratification"]["lengths"],
        f"length:{partition}:{split}:{dataset}",
        seed,
    )
    selected: list[dict] = []
    length_counts: Counter = Counter()
    remaining = list(available)
    task_order = sorted(TASKS, key=lambda task: stable_key(seed, f"task-order:{partition}:{split}:{dataset}", task))
    for task in task_order:
        needed = task_targets.get(task, 0)
        pool = [row for row in remaining if row["task"] == task]
        if len(pool) < needed:
            raise RuntimeError(
                f"Insufficient {dataset}/{task} candidates for {partition}/{split}: "
                f"need {needed}, have {len(pool)}"
            )
        for _ in range(needed):
            pool.sort(
                key=lambda row: (
                    length_counts[row["length_bin"]] / max(1, length_targets[row["length_bin"]]),
                    stable_key(seed, f"pick:{partition}:{split}:{dataset}", row["source_id"]),
                )
            )
            item = pool.pop(0)
            selected.append(item)
            length_counts[item["length_bin"]] += 1
            remaining.remove(item)
    if len(selected) != count:
        raise AssertionError("Weighted task allocation did not fill the bucket")
    return selected


def _balanced_labels(rows: list[dict], labels: list[str], seed: int, salt: str) -> dict[str, str]:
    ordered = sorted(rows, key=lambda row: stable_key(seed, salt, row["source_id"]))
    return {row["source_id"]: labels[index % len(labels)] for index, row in enumerate(ordered)}


def assign_rewrite_conditions(rows: list[dict], config: dict) -> None:
    """Freeze counterbalanced runner fields without generating any rewrite."""
    seed = config["seed"]
    for partition in PARTITIONS:
        for split in SPLITS:
            for task in TASKS:
                for length in LENGTHS:
                    bucket = [
                        row for row in rows
                        if row["pool_partition"] == partition
                        and row["split"] == split
                        and row["task"] == task
                        and row["length_bin"] == length
                    ]
                    if not bucket:
                        continue
                    # Family C is a genuinely held-out test recipe. A/B are
                    # restricted to train and validation by construction.
                    family_labels = ["C"] if split == "test" else ["A", "B"]
                    cell = f"{partition}:{split}:{task}:{length}"
                    families = _balanced_labels(bucket, family_labels, seed, f"family:{cell}")
                    orders = _balanced_labels(
                        bucket,
                        ["confident_first", "hedged_first"],
                        seed,
                        f"order:{cell}",
                    )
                    longer = _balanced_labels(
                        bucket,
                        ["confident", "hedged"],
                        seed,
                        f"longer:{cell}",
                    )
                    for row in bucket:
                        row["rewrite_family"] = families[row["source_id"]]
                        row["rewrite_output_order"] = orders[row["source_id"]]
                        row["target_longer_member"] = longer[row["source_id"]]


def select_frozen_pool(candidates: list[dict], config: dict) -> list[dict]:
    """Apply exact source/split quotas with deterministic task/length balance."""
    seed = config["seed"]
    remaining = {dataset: [row for row in candidates if row["dataset"] == dataset] for dataset in DATASETS}
    for dataset in DATASETS:
        remaining[dataset].sort(key=lambda row: stable_key(seed, "selection-pool", row["source_id"]))
    selected: list[dict] = []
    # Protect held-out coverage before filling the much larger training buckets.
    order = [
        ("main", "validation"),
        ("main", "test"),
        ("reserve", "validation"),
        ("reserve", "test"),
        ("main", "train"),
        ("reserve", "train"),
    ]
    for partition, split in order:
        for dataset in DATASETS:
            target = config["quotas"][partition][split][dataset]
            chosen = _pick_bucket(remaining[dataset], target, dataset, partition, split, config)
            chosen_ids = {row["source_id"] for row in chosen}
            remaining[dataset] = [row for row in remaining[dataset] if row["source_id"] not in chosen_ids]
            for row in chosen:
                item = dict(row)
                item.update(pool_partition=partition, split=split, source_pool_version=1)
                selected.append(item)
    selected.sort(
        key=lambda row: (
            PARTITIONS.index(row["pool_partition"]),
            SPLITS.index(row["split"]),
            DATASETS.index(row["dataset"]),
            stable_key(seed, "frozen-order", row["source_id"]),
        )
    )
    main_index = reserve_index = 0
    for row in selected:
        if row["pool_partition"] == "main":
            main_index += 1
            row["pool_id"] = f"M{main_index:04d}"
        else:
            reserve_index += 1
            row["pool_id"] = f"R{reserve_index:04d}"
    assign_rewrite_conditions(selected, config)
    validate_frozen_pool(selected, config)
    return selected


def validate_frozen_pool(rows: list[dict], config: dict) -> None:
    expected_total = sum(
        config["quotas"][partition][split][dataset]
        for partition in PARTITIONS for split in SPLITS for dataset in DATASETS
    )
    if len(rows) != expected_total:
        raise ValueError(f"Expected {expected_total} frozen rows, found {len(rows)}")
    for field in [
        "pool_id", "source_id", "prompt", "original_response", "original_response_sha256",
        "split", "pool_partition", "dataset", "task", "length_bin", "group_id",
        "rewrite_family", "rewrite_output_order", "target_longer_member",
    ]:
        if any(row.get(field) in (None, "") for row in rows):
            raise ValueError(f"Missing required frozen field: {field}")
    if len({row["pool_id"] for row in rows}) != len(rows):
        raise ValueError("Duplicate pool IDs")
    for field in [
        "source_id", "group_id", "normalized_prompt_sha256", "canonical_prompt_sha256",
        "original_response_sha256", "normalized_response_sha256",
    ]:
        if len({row[field] for row in rows}) != len(rows):
            raise ValueError(f"Duplicate leakage anchor in frozen pool: {field}")
    for row in rows:
        if sha256_text(row["original_response"]) != row["original_response_sha256"]:
            raise ValueError(f"Response hash mismatch for {row['pool_id']}")
        expected_families = {"C"} if row["split"] == "test" else {"A", "B"}
        if row["rewrite_family"] not in expected_families:
            raise ValueError(
                f"Rewrite family {row['rewrite_family']} is invalid for {row['split']} split"
            )
    for partition in PARTITIONS:
        for split in SPLITS:
            for dataset in DATASETS:
                actual = sum(
                    row["pool_partition"] == partition
                    and row["split"] == split
                    and row["dataset"] == dataset
                    for row in rows
                )
                expected = config["quotas"][partition][split][dataset]
                if actual != expected:
                    raise ValueError(
                        f"Quota mismatch for {partition}/{split}/{dataset}: {actual} != {expected}"
                    )
    for split in config["stratification"]["require_every_task_in_main_splits"]:
        values = {row["task"] for row in rows if row["pool_partition"] == "main" and row["split"] == split}
        if values != set(TASKS):
            raise ValueError(f"Main {split} lacks task coverage: {sorted(set(TASKS) - values)}")
    for split in config["stratification"]["require_every_length_in_main_splits"]:
        values = {row["length_bin"] for row in rows if row["pool_partition"] == "main" and row["split"] == split}
        if values != set(LENGTHS):
            raise ValueError(f"Main {split} lacks length coverage: {sorted(set(LENGTHS) - values)}")


def _nested_counts(rows: list[dict], fields: list[str]) -> list[dict]:
    counts = Counter(tuple(row[field] for field in fields) for row in rows)
    return [
        {**{field: value for field, value in zip(fields, key)}, "count": count}
        for key, count in sorted(counts.items())
    ]


def build_coverage(rows: list[dict], rejections: Counter) -> dict:
    return {
        "source_count": len(rows),
        "main_count": sum(row["pool_partition"] == "main" for row in rows),
        "reserve_count": sum(row["pool_partition"] == "reserve" for row in rows),
        "by_partition_split_dataset": _nested_counts(rows, ["pool_partition", "split", "dataset"]),
        "by_partition_split_task": _nested_counts(rows, ["pool_partition", "split", "task"]),
        "by_partition_split_length": _nested_counts(rows, ["pool_partition", "split", "length_bin"]),
        "deduplication_rejections": dict(sorted(rejections.items())),
        "contains_source_text": False,
    }


def _public_record(row: dict) -> dict:
    return {
        "pool_id": row["pool_id"],
        "source_key_sha256": sha256_text(row["source_id"]),
        "dataset": row["dataset"],
        "dataset_revision": row["dataset_revision"],
        "pool_partition": row["pool_partition"],
        "split": row["split"],
        "task": row["task"],
        "length_bin": row["length_bin"],
        "group_id": row["group_id"],
        "normalized_prompt_sha256": row["normalized_prompt_sha256"],
        "canonical_prompt_sha256": row["canonical_prompt_sha256"],
        "original_response_sha256": row["original_response_sha256"],
        "rewrite_family": row["rewrite_family"],
        "rewrite_output_order": row["rewrite_output_order"],
        "target_longer_member": row["target_longer_member"],
    }


def build_manifest(
    rows: list[dict],
    config: dict,
    config_sha256: str,
    private_hashes: dict[str, str],
    coverage_sha256: str,
    tokenizer_hashes: dict[str, str],
    main_file_sha256: str,
    main_source_ids_sha256: str,
) -> dict:
    main_count = sum(row["pool_partition"] == "main" for row in rows)
    return {
        "freeze_version": 1,
        "seed": config["seed"],
        "config_sha256": config_sha256,
        "source_count": len(rows),
        "main_count": main_count,
        "main_source_count": main_count,
        "reserve_count": sum(row["pool_partition"] == "reserve" for row in rows),
        "main_file_sha256": main_file_sha256,
        "main_source_ids_sha256": main_source_ids_sha256,
        # Alias consumed by the Claude rewrite runner. It intentionally hashes
        # the ordered 1,000 main source IDs, not the 200 reserves.
        "source_ids_sha256": main_source_ids_sha256,
        "dataset_revisions": {
            dataset: config["datasets"][dataset]["revision"] for dataset in DATASETS
        },
        "selection_method": (
            "deterministic score-free source selection with exact split/source quotas, "
            "task/length stratification, and global identity/hash/group/near-text deduplication"
        ),
        "excluded_prior_sets": "50-pair development and 50-pair cue-holdout challenge",
        "old_overlap_anchor_fields": [
            "source_id", "conversation_hash", "group_id", "development_template_group",
            "legacy_template_group", "normalized_prompt_sha256", "canonical_prompt_sha256",
            "original_response_sha256", "normalized_response_sha256",
        ],
        "near_duplicate_thresholds": {
            "prompt_5gram_jaccard": config["screening"]["near_prompt_jaccard"],
            "response_5gram_jaccard": config["screening"]["near_response_jaccard"],
        },
        "tokenizer": {
            "id": config["representation_tokenizer"]["id"],
            "revision": config["representation_tokenizer"]["revision"],
            "file_sha256": tokenizer_hashes,
        },
        "private_output_sha256": private_hashes,
        "coverage_sha256": coverage_sha256,
        "contains_source_text": False,
        "score_or_activation_used": False,
        "rewrite_generation_performed": False,
        "human_source_review": config["scientific_guards"]["human_source_review"],
        "source_records": [_public_record(row) for row in rows],
    }


def freeze_outputs(
    rows: list[dict],
    config: dict,
    config_sha256: str,
    rejections: Counter,
    tokenizer_hashes: dict[str, str],
    repo: Path = REPO,
) -> dict:
    validate_frozen_pool(rows, config)
    output = config["outputs"]
    private = resolve_path(output["private_directory"], repo)
    paths = {
        "main": private / output["main_file"],
        "reserve": private / output["reserve_file"],
        "all": private / output["all_file"],
    }
    main_rows = [row for row in rows if row["pool_partition"] == "main"]
    reserve_rows = [row for row in rows if row["pool_partition"] == "reserve"]
    payloads = {"main": jsonl_bytes(main_rows), "reserve": jsonl_bytes(reserve_rows), "all": jsonl_bytes(rows)}
    private_hashes = {paths[key].name: sha256_bytes(value) for key, value in payloads.items()}
    ordered_main_ids = "".join(row["source_id"] + "\n" for row in main_rows).encode("utf-8")
    main_source_ids_sha256 = sha256_bytes(ordered_main_ids)
    coverage = build_coverage(rows, rejections)
    coverage_bytes = (json.dumps(coverage, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    manifest = build_manifest(
        rows,
        config,
        config_sha256,
        private_hashes,
        sha256_bytes(coverage_bytes),
        tokenizer_hashes,
        private_hashes[paths["main"].name],
        main_source_ids_sha256,
    )
    manifest_bytes = (json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    public_paths = {
        "coverage": resolve_path(output["public_coverage"], repo),
        "manifest": resolve_path(output["public_manifest"], repo),
    }
    reused = []
    for key in ["main", "reserve", "all"]:
        reused.append(write_once_or_verify(paths[key], payloads[key]))
    reused.append(write_once_or_verify(public_paths["coverage"], coverage_bytes))
    reused.append(write_once_or_verify(public_paths["manifest"], manifest_bytes))
    return {
        "sources": len(rows),
        "main": len(main_rows),
        "reserve": len(reserve_rows),
        "all_outputs_reused": all(reused),
        "private_manifest": str(paths["all"]),
        "public_manifest": str(public_paths["manifest"]),
    }


def reuse_complete_freeze(config: dict, config_sha256: str, repo: Path = REPO) -> dict | None:
    output = config["outputs"]
    private = resolve_path(output["private_directory"], repo)
    all_path = private / output["all_file"]
    manifest_path = resolve_path(output["public_manifest"], repo)
    coverage_path = resolve_path(output["public_coverage"], repo)
    main_path = private / output["main_file"]
    reserve_path = private / output["reserve_file"]
    paths = [all_path, main_path, reserve_path, manifest_path, coverage_path]
    if not any(path.exists() for path in paths):
        return None
    if not all(path.exists() for path in paths):
        return None  # Acquisition caches and deterministic writes safely resume the partial freeze.
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("config_sha256") != config_sha256:
        raise FileExistsError("A complete freeze exists under a different configuration; refusing overwrite")
    for path in [all_path, main_path, reserve_path]:
        expected = manifest["private_output_sha256"].get(path.name)
        if expected != sha256_file(path):
            raise ValueError(f"Frozen private output hash mismatch: {path}")
    if manifest.get("coverage_sha256") != sha256_file(coverage_path):
        raise ValueError("Frozen public coverage hash mismatch")
    rows = read_jsonl(all_path)
    validate_frozen_pool(rows, config)
    return {
        "sources": len(rows),
        "main": sum(row["pool_partition"] == "main" for row in rows),
        "reserve": sum(row["pool_partition"] == "reserve" for row in rows),
        "all_outputs_reused": True,
        "network_calls": 0,
        "model_loads": 0,
        "private_manifest": str(all_path),
        "public_manifest": str(manifest_path),
    }


def _download_once(url: str, path: Path, timeout: int) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    with urllib.request.urlopen(url, timeout=timeout) as source, temporary.open("wb") as target:
        while block := source.read(1024 * 1024):
            target.write(block)
    temporary.replace(path)


def acquire_helpsteer(config: dict, tokenizer: Any, private: Path) -> tuple[list[dict], Counter]:
    cache = private / "acquisition" / "helpsteer2_candidates.jsonl"
    cached = read_candidate_cache(cache, config)
    if cached is not None:
        rows = cached
        if any(row.get("dataset_revision") != config["datasets"]["nvidia/HelpSteer2"]["revision"] for row in rows):
            raise ValueError("Stale HelpSteer2 acquisition cache")
        return rows, Counter()
    revision = config["datasets"]["nvidia/HelpSteer2"]["revision"]
    url = f"https://huggingface.co/datasets/nvidia/HelpSteer2/resolve/{revision}/train.jsonl.gz"
    shared = BASE / "private_data" / "downloads" / "helpsteer2_train.jsonl.gz"
    _download_once(url, shared, config["acquisition"]["request_timeout_seconds"])
    candidates: list[dict] = []
    rejected: Counter = Counter()
    with gzip.open(shared, "rt", encoding="utf-8") as stream:
        for index, line in enumerate(stream):
            source = json.loads(line)
            raw = {
                "source_id": f"helpsteer2-train-row-{index}",
                "dataset": "nvidia/HelpSteer2",
                "dataset_revision": revision,
                "original_split": "train",
                "original_row_index": index,
                "source_url": url,
                "source_license": config["datasets"]["nvidia/HelpSteer2"]["license"],
                "source_author": "existing corpus response; author model not specified per row",
                "prompt": source["prompt"],
                "original_response": source["response"],
                "source_quality_metadata": {
                    key: source[key]
                    for key in ["helpfulness", "correctness", "coherence", "complexity", "verbosity"]
                    if key in source
                },
            }
            prepared, reason = prepare_candidate(raw, tokenizer, config)
            if prepared is None:
                rejected[reason] += 1
            else:
                candidates.append(prepared)
    limit = config["acquisition"]["helpsteer_eligible_cap"]
    candidates.sort(key=lambda row: stable_key(config["seed"], "helpsteer-acquisition", row["source_id"]))
    candidates = candidates[:limit]
    write_candidate_cache(
        cache,
        candidates,
        config,
        {"dataset": "nvidia/HelpSteer2", "dataset_revision": revision},
    )
    return candidates, rejected


def _wildchat_shards(config: dict, private: Path) -> list[str]:
    revision = config["datasets"]["allenai/WildChat-1M"]["revision"]
    metadata_path = private / "acquisition" / "wildchat_revision_metadata.json"
    if metadata_path.exists():
        wrapper = json.loads(metadata_path.read_text(encoding="utf-8"))
        if wrapper.get("dataset_revision") != revision:
            raise ValueError("WildChat metadata cache is pinned to a different revision")
        metadata = wrapper["payload"]
    else:
        url = f"https://huggingface.co/api/datasets/allenai/WildChat-1M/revision/{revision}"
        with urllib.request.urlopen(url, timeout=config["acquisition"]["request_timeout_seconds"]) as stream:
            metadata = json.load(stream)
        atomic_write(
            metadata_path,
            (json.dumps(
                {"dataset_revision": revision, "payload": metadata},
                ensure_ascii=False,
                sort_keys=True,
            ) + "\n").encode("utf-8"),
        )
    paths = [
        item["rfilename"] for item in metadata["siblings"]
        if item["rfilename"].startswith("data/") and item["rfilename"].endswith(".parquet")
    ]
    return sorted(paths, key=lambda value: stable_key(config["seed"], "wildchat-shard", value))


def acquire_wildchat(
    config: dict,
    tokenizer: Any,
    private: Path,
    old_rows: list[dict] | None = None,
) -> tuple[list[dict], Counter, list[str]]:
    # Imports are deliberately lazy: unit tests exercise all selection logic
    # without loading a dataset client or model/tokenizer.
    from datasets import DownloadConfig, load_dataset

    revision = config["datasets"]["allenai/WildChat-1M"]["revision"]
    shard_paths = _wildchat_shards(config, private)
    candidates: list[dict] = []
    rejected: Counter = Counter()
    visited_shards: list[str] = []
    stop_targets = wildchat_stop_targets(config)
    for shard in shard_paths:
        visited_shards.append(shard)
        shard_key = sha256_text(shard)[:16]
        cache = private / "acquisition" / "wildchat" / f"{shard_key}.jsonl"
        cached = read_candidate_cache(cache, config)
        if cached is not None:
            shard_rows = cached
            if any(row.get("dataset_revision") != revision for row in shard_rows):
                raise ValueError(f"Stale WildChat acquisition cache for {shard}")
            candidates.extend(shard_rows)
        else:
            url = f"https://huggingface.co/datasets/allenai/WildChat-1M/resolve/{revision}/{shard}"
            stream = load_dataset(
                "parquet",
                data_files={"train": [url]},
                split="train",
                streaming=True,
                download_config=DownloadConfig(max_retries=config["acquisition"]["max_retries"]),
            )
            shard_rows = []
            for row_index, source in enumerate(stream):
                if row_index >= config["acquisition"]["wildchat_max_rows_per_shard"]:
                    break
                conversation_hash = str(source.get("conversation_hash", ""))
                if not conversation_hash:
                    rejected["missing_conversation_hash"] += 1
                    continue
                turns = source.get("conversation") or []
                if len(turns) < 2 or turns[0].get("role") != "user" or turns[1].get("role") != "assistant":
                    rejected["missing_first_user_assistant_pair"] += 1
                    continue
                if source.get("toxic") or source.get("redacted") or any(
                    turn.get("toxic") or turn.get("redacted") for turn in turns[:2]
                ):
                    rejected["toxic_or_redacted"] += 1
                    continue
                if any(turn.get("language") != "English" for turn in turns[:2]):
                    rejected["non_english_metadata"] += 1
                    continue
                # Rare task families need a denser deterministic sample than the
                # abundant factual stratum. This decision uses only the source
                # prompt heuristic, never a probe score or rewrite outcome.
                task_hint = classify(str(turns[0].get("content", "")))
                modulus = (
                    config["acquisition"]["wildchat_prefilter_modulus"]
                    if task_hint == "factual_explanation"
                    else config["acquisition"]["wildchat_rare_prefilter_modulus"]
                )
                bucket = int(stable_key(config["seed"], shard, conversation_hash)[:16], 16)
                if bucket % modulus != config["acquisition"]["wildchat_prefilter_bucket"]:
                    continue
                target_turn = turns[1]
                source_id = f"wildchat-{conversation_hash}-turn-{target_turn.get('turn_identifier')}"
                raw = {
                    "source_id": source_id,
                    "dataset": "allenai/WildChat-1M",
                    "dataset_revision": revision,
                    "original_split": "train",
                    "conversation_hash": conversation_hash,
                    "target_turn_index": 1,
                    "target_turn_identifier": target_turn.get("turn_identifier"),
                    "source_author": source.get("model"),
                    "source_url": f"https://huggingface.co/datasets/allenai/WildChat-1M/tree/{revision}/{shard}",
                    "source_license": config["datasets"]["allenai/WildChat-1M"]["license"],
                    "prompt": turns[0].get("content", ""),
                    "original_response": target_turn.get("content", ""),
                }
                prepared, reason = prepare_candidate(raw, tokenizer, config)
                if prepared is None:
                    rejected[reason] += 1
                else:
                    shard_rows.append(prepared)
            shard_rows.sort(key=lambda row: stable_key(config["seed"], f"wildchat:{shard}", row["source_id"]))
            shard_rows = shard_rows[:config["acquisition"]["wildchat_eligible_cap_per_shard"]]
            write_candidate_cache(
                cache,
                shard_rows,
                config,
                {"dataset": "allenai/WildChat-1M", "dataset_revision": revision, "shard": shard},
            )
            candidates.extend(shard_rows)
        task_counts = Counter(row["task"] for row in candidates)
        if (
            len(visited_shards) >= config["acquisition"]["wildchat_min_shards"]
            and all(task_counts[task] >= stop_targets[task] for task in TASKS)
        ):
            # Count after the actual global old-set/near-duplicate screen before
            # stopping; raw task counts alone can overstate usable coverage.
            usable = candidates
            if old_rows is not None:
                usable, _ = screen_and_deduplicate(candidates, old_rows, config)
            usable_counts = Counter(row["task"] for row in usable)
            if all(usable_counts[task] >= stop_targets[task] for task in TASKS):
                break
    return candidates, rejected, visited_shards


def tokenizer_file_hashes(snapshot: Path) -> dict[str, str]:
    names = ["tokenizer.json", "tokenizer_config.json"]
    missing = [name for name in names if not (snapshot / name).is_file()]
    if missing:
        raise FileNotFoundError(f"Tokenizer snapshot is incomplete: {missing}")
    return {name: sha256_file(snapshot / name) for name in names}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    args = parser.parse_args(argv)
    config, config_sha256 = load_config(args.config)
    reused = reuse_complete_freeze(config, config_sha256)
    if reused is not None:
        print(json.dumps(reused, ensure_ascii=False, sort_keys=True))
        return 0
    validate_legacy_pins(config)
    old_rows = load_old_exclusions(config)
    snapshot = (REPO / config["representation_tokenizer"]["snapshot_relative_to_repo"]).resolve()
    hashes = tokenizer_file_hashes(snapshot)
    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(str(snapshot), local_files_only=True)
    private = resolve_path(config["outputs"]["private_directory"])
    help_rows, help_rejected = acquire_helpsteer(config, tokenizer, private)
    wild_rows, wild_rejected, shards = acquire_wildchat(config, tokenizer, private, old_rows)
    screened, dedup_rejected = screen_and_deduplicate(wild_rows + help_rows, old_rows, config)
    selected = select_frozen_pool(screened, config)
    rejections = help_rejected + wild_rejected + dedup_rejected
    result = freeze_outputs(selected, config, config_sha256, rejections, hashes)
    result.update(
        eligible_before_dedup=len(wild_rows) + len(help_rows),
        eligible_after_dedup=len(screened),
        wildchat_shards_visited=len(shards),
        old_source_ids_excluded=len({row.get("source_id") for row in old_rows if row.get("source_id")}),
        network_acquisition_completed=True,
        rewrite_calls=0,
        model_forwards=0,
    )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
