"""Capture a pinned public source sample and extend an immutable source prefix.

This prepares source data only.  It does not call a rewrite provider.  The default
run stops at a 300-source feasibility sample; requesting more never relaxes the
original canary's source_screen filters.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import copy
import hashlib
import json
import math
import os
import random
import re
import tempfile
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from prepare_sources import source_screen

BASE = Path(__file__).resolve().parents[1]
REVISION = "8049631c405ae6576f93f445c6b8166f76f5505a"
DATASET = "HuggingFaceH4/ultrachat_200k"
DEFAULT_SAMPLE = 300


def digest(value):
    if not isinstance(value, bytes):
        value = value.encode("utf-8")
    return hashlib.sha256(value).hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def atomic_json(path, value):
    """Replace one JSON file atomically; callers enforce append-only semantics."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def fetch(url):
    request = urllib.request.Request(
        url, headers={"User-Agent": "information-chat-source-expansion/1.0"}
    )
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                return json.load(response)
        except (urllib.error.URLError, TimeoutError) as error:
            # A rate limit is a stop signal, including metadata requests.  A
            # later invocation can reuse all successfully pinned pages.
            if isinstance(error, urllib.error.HTTPError) and error.code not in (500, 502, 503, 504):
                raise
            if attempt == 3:
                raise
            time.sleep(2 ** attempt)


def validate_config(config):
    expected = {
        "dataset_id": DATASET, "dataset_revision": REVISION,
        "split": "train_sft", "answer_words_min": 40,
        "answer_words_max": 180, "question_chars_max": 1600,
        "target_sources": 10000,
    }
    for key, value in expected.items():
        if config.get(key) != value:
            raise ValueError(f"{key} must remain {value!r}; source filters are frozen")
    if not isinstance(config.get("page_size"), int) or not 1 <= config["page_size"] <= 100:
        raise ValueError("page_size must be between 1 and 100")
    if not isinstance(config.get("seed"), int):
        raise ValueError("seed must be an integer")
    for key in ("private_dir", "canary_private_dir"):
        path = Path(config.get(key, ""))
        if not config.get(key) or path.is_absolute() or ".." in path.parts:
            raise ValueError(f"{key} must be a relative private directory")


def checked_metadata(config, fetcher):
    metadata = fetcher("https://huggingface.co/api/datasets/" + config["dataset_id"])
    if metadata.get("sha") != config["dataset_revision"]:
        raise RuntimeError("Dataset revision differs from the frozen revision; capture stopped")
    return metadata


def page_url(config, offset):
    params = {"dataset": config["dataset_id"], "config": "default",
              "split": config["split"], "offset": offset, "length": config["page_size"]}
    return "https://datasets-server.huggingface.co/rows?" + urllib.parse.urlencode(params)


def page_details(url, config):
    parsed = urllib.parse.urlparse(url)
    query = urllib.parse.parse_qs(parsed.query)
    required = {"dataset": config["dataset_id"], "config": "default", "split": config["split"]}
    if parsed.scheme != "https" or parsed.netloc != "datasets-server.huggingface.co" or parsed.path != "/rows":
        raise RuntimeError("Unexpected source cache URL")
    if any(query.get(key) != [value] for key, value in required.items()):
        raise RuntimeError("Source cache dataset or split does not match")
    return int(query["offset"][0]), int(query["length"][0])


def validate_response(response, offset, length, total=None):
    rows = response.get("rows")
    count = response.get("num_rows_total")
    if not isinstance(count, int) or count <= 0 or (total is not None and count != total):
        raise RuntimeError("Unexpected dataset row count")
    expected = list(range(offset, min(offset + length, count)))
    if response.get("partial") or not isinstance(rows, list) or [item.get("row_idx") for item in rows] != expected:
        raise RuntimeError("Dataset page is partial, missing, duplicated, or out of order")
    if any(item.get("truncated_cells") or not isinstance(item.get("row"), dict) for item in rows):
        raise RuntimeError("Dataset page contains truncated or invalid source rows")
    return count


def normalized(text):
    """Independent question and answer keys, not a combined pair key."""
    text = unicodedata.normalize("NFKC", text).casefold()
    return re.sub(r"\s+", " ", text).strip()


def source_keys(record):
    return (record["group_id"], normalized(record["question"]), normalized(record["original"]))


def dedupe_sources(records, prefix=()):
    seen = [set(), set(), set()]
    result, rejected = [], {"duplicate_group": 0, "duplicate_question": 0, "duplicate_answer": 0}
    reasons = list(rejected)
    for record in prefix:
        keys = source_keys(record)
        if any(key in used for key, used in zip(keys, seen)):
            raise RuntimeError("Frozen prefix contains a duplicate conversation, question, or answer")
        for key, used in zip(keys, seen):
            used.add(key)
    for record in records:
        keys = source_keys(record)
        clashes = [key in used for key, used in zip(keys, seen)]
        if any(clashes):
            rejected[reasons[clashes.index(True)]] += 1
            continue
        for key, used in zip(keys, seen):
            used.add(key)
        result.append(record)
    return result, rejected


def make_page_plan(total, page_size, seed, canary_offsets):
    """A seeded page order whose existing prefix is independent of sample size."""
    if any(offset % page_size for offset in canary_offsets):
        raise ValueError("Canary page offsets must align with page_size")
    offsets = [offset for offset in range(0, total, page_size) if offset not in set(canary_offsets)]
    random.Random(seed).shuffle(offsets)
    return list(canary_offsets) + offsets


def source_record(item, pin, root, cache_path, config):
    row = item["row"]
    screened = source_screen(row, config)
    if screened is None:
        return None
    if not isinstance(row.get("prompt_id"), str) or not row["prompt_id"]:
        return None
    return {
        "source_id": row["prompt_id"], "group_id": row["prompt_id"],
        "row_idx": item["row_idx"], "source_url": pin["url"],
        "source_cache_file": os.path.relpath(cache_path, root),
        "source_cache_sha256": pin["sha256"], "dataset_revision": config["dataset_revision"],
        "raw_source_row": row, **screened,
        "question_sha256": digest(screened["question"]),
        "original_sha256": digest(screened["original"]),
        "raw_source_row_sha256": digest(canonical(row)),
        "reuse_canary": False, "manual_source_selection": "source_screen_pass_not_fact_certified",
    }


def verify_prefix(existing, proposed):
    if not isinstance(existing, list) or len(existing) > len(proposed) or existing != proposed[:len(existing)]:
        raise RuntimeError("Existing SOURCES.json prefix changed; refusing to overwrite frozen records")


def estimate_feasibility(eligible, screened, total, target):
    rate = eligible / screened if screened else 0
    # Wilson interval is descriptive: the purposive canary and clustered pages are
    # not an independent random sample, so this is not a population guarantee.
    if screened:
        z = 1.96
        denom = 1 + z * z / screened
        center = (rate + z * z / (2 * screened)) / denom
        radius = z * math.sqrt(rate * (1 - rate) / screened + z * z / (4 * screened ** 2)) / denom
    else:
        center = radius = 0
    return {
        "observed_eligible_fraction": rate,
        "descriptive_wilson_95_fraction": [max(0, center - radius), min(1, center + radius)],
        "projected_eligible_full_split": math.floor(total * rate),
        "estimated_rows_needed_for_target": math.ceil(target / rate) if rate else None,
        "required_full_split_fraction": target / total,
        "target_feasible_at_observed_yield": rate * total >= target,
        "projection_is_not_a_guarantee": True,
        "filters_relaxed": False,
    }


def prepare(config, *, base=BASE, pages=None, freeze_count=DEFAULT_SAMPLE, fetcher=fetch):
    validate_config(config)
    if pages is not None and pages < 0:
        raise ValueError("--pages must be nonnegative")
    if not 50 <= freeze_count <= config["target_sources"]:
        raise ValueError("--freeze-count must be between 50 and target_sources")
    base = Path(base)
    root, canary = base / config["private_dir"], base / config["canary_private_dir"]
    root.mkdir(parents=True, exist_ok=True)
    snapshot = {key: config[key] for key in ("dataset_id", "dataset_revision", "split", "page_size", "seed",
                "answer_words_min", "answer_words_max", "question_chars_max", "target_sources", "private_dir", "canary_private_dir")}
    snapshot_path = root / "SOURCE_CONFIG.json"
    if snapshot_path.exists() and read_json(snapshot_path) != snapshot:
        raise RuntimeError("Source configuration changed after capture began")
    if not snapshot_path.exists():
        atomic_json(snapshot_path, snapshot)
    original_manifest = read_json(canary / "SOURCE_CAPTURE_MANIFEST.json")
    if original_manifest.get("dataset") != DATASET or original_manifest.get("revision") != REVISION:
        raise RuntimeError("Canary capture is not pinned to the required dataset revision")
    packet_path = canary / "review_final_v2" / "TRIPLETS_50.json"
    packet = read_json(packet_path)
    approved = packet.get("triplets", [])
    if packet.get("dataset") != DATASET or packet.get("revision") != REVISION or len(approved) != 50:
        raise RuntimeError("Expected exactly 50 approved triplets at the frozen revision")
    for number, record in enumerate(approved, 1):
        if record.get("review_id") != f"HC{number:03d}" or record.get("group_id") != record.get("source_id"):
            raise RuntimeError("Frozen review IDs or group IDs changed")
    index_path = root / "CACHE_INDEX.json"
    index = read_json(index_path) if index_path.exists() else {"dataset": DATASET, "revision": REVISION, "pages": []}
    if index.get("dataset") != DATASET or index.get("revision") != REVISION:
        raise RuntimeError("Expansion cache index revision changed")
    indexed = {entry["offset"]: entry for entry in index["pages"]}
    if len(indexed) != len(index["pages"]):
        raise RuntimeError("Duplicate cache page pins")
    metadata_dir = root / "source_cache" / "metadata"
    phases = []

    def metadata_pin(value):
        hash_value = digest(canonical(value))
        path = metadata_dir / (hash_value + ".json")
        if path.exists() and read_json(path) != value:
            raise RuntimeError("Metadata pin changed")
        if not path.exists():
            atomic_json(path, value)
        return {"file": str(path.relative_to(root)), "sha256": digest(path.read_bytes()), "dataset_sha": value["sha"]}

    def start_phase(label):
        return {"phase": label, "before": metadata_pin(checked_metadata(config, fetcher))}

    def finish_phase(phase):
        phase["after"] = metadata_pin(checked_metadata(config, fetcher))
        phases.append(phase)
        return phase

    phase = start_phase("validate_reused_canary_and_existing_cache")
    canary_offsets, all_pages, total = [], {}, None
    for entry in original_manifest["cache_files"]:
        path = canary / entry["file"]
        if digest(path.read_bytes()) != entry["sha256"]:
            raise RuntimeError(f"Canary cache hash mismatch: {entry['file']}")
        cached = read_json(path)
        offset, length = page_details(cached["source_url"], config)
        if length != config["page_size"] or cached.get("dataset_revision_checked") != REVISION or cached["source_url"] != entry["url"]:
            raise RuntimeError("Canary page pin mismatch")
        total = validate_response(cached["response"], offset, length, total)
        pin = {"offset": offset, "file": os.path.relpath(path, root), "sha256": entry["sha256"],
               "url": entry["url"], "dataset_revision": REVISION, "reused_canary_cache": True,
               "original_manifest_sha256": digest((canary / "SOURCE_CAPTURE_MANIFEST.json").read_bytes())}
        if offset in indexed and indexed[offset] != pin:
            raise RuntimeError("Previously pinned canary cache changed")
        indexed[offset] = pin
        canary_offsets.append(offset)
        all_pages[offset] = (cached["response"], pin, path)
    if len(canary_offsets) != len(set(canary_offsets)) or total is None:
        raise RuntimeError("Canary cache pages are missing or duplicated")
    for offset, pin in indexed.items():
        if offset in all_pages:
            continue
        path = root / pin["file"]
        if digest(path.read_bytes()) != pin["sha256"]:
            raise RuntimeError(f"Expansion cache hash mismatch: {pin['file']}")
        cached = read_json(path)
        if pin.get("dataset_revision") != REVISION or cached.get("dataset_revision_checked") != REVISION:
            raise RuntimeError("Expansion page revision mismatch")
        parsed_offset, length = page_details(cached["source_url"], config)
        if parsed_offset != offset or length != config["page_size"] or cached["source_url"] != pin["url"]:
            raise RuntimeError("Expansion page URL mismatch")
        for side in ("before", "after"):
            meta_pin = cached["revision_checks"][side]
            meta_path = root / meta_pin["file"]
            if digest(meta_path.read_bytes()) != meta_pin["sha256"] or read_json(meta_path).get("sha") != REVISION:
                raise RuntimeError("Page revision-check metadata hash mismatch")
        validate_response(cached["response"], offset, length, total)
        all_pages[offset] = (cached["response"], pin, path)
    finish_phase(phase)
    plan = make_page_plan(total, config["page_size"], config["seed"], canary_offsets)
    plan_value = {"dataset": DATASET, "revision": REVISION, "total_rows": total,
                  "page_size": config["page_size"], "seed": config["seed"], "offsets": plan}
    plan_path = root / "SOURCE_PAGE_PLAN.json"
    if plan_path.exists() and read_json(plan_path) != plan_value:
        raise RuntimeError("Previously frozen page plan changed")
    if not plan_path.exists():
        atomic_json(plan_path, plan_value)

    def save_index():
        index["pages"] = [indexed[offset] for offset in plan if offset in indexed]
        atomic_json(index_path, index)

    save_index()
    frozen = []
    by_row = {item["row_idx"]: (item, pin, path) for response, pin, path in all_pages.values() for item in response["rows"]}
    for original in approved:
        found = by_row.get(original["row_idx"])
        if found is None:
            raise RuntimeError("Approved source is absent from the verified canary cache")
        item, pin, path = found
        screened = source_record(item, pin, root, path, config)
        if screened is None or any(original.get(key) != screened[key] for key in ("source_id", "group_id", "question", "original", "word_count", "raw_source_row")):
            raise RuntimeError("Approved source no longer matches its exact first-turn cache row")
        record = copy.deepcopy(original)
        record.update({key: screened[key] for key in ("source_cache_file", "source_cache_sha256", "dataset_revision", "raw_source_row_sha256")})
        record["reuse_canary"] = True
        frozen.append(record)
    dedupe_sources([], frozen)

    def candidates_from_cache():
        screened, rows_screened, failures = [], 0, 0
        for offset in plan:
            if offset not in all_pages:
                continue
            response, pin, path = all_pages[offset]
            rows_screened += len(response["rows"])
            for item in response["rows"]:
                candidate = source_record(item, pin, root, path, config)
                if candidate is None:
                    failures += 1
                else:
                    screened.append(candidate)
        unique, rejected = dedupe_sources(screened, frozen)
        return unique, rows_screened, failures, rejected

    existing_path = root / "SOURCES.json"
    existing = read_json(existing_path) if existing_path.exists() else []
    if freeze_count < len(existing):
        raise ValueError("--freeze-count cannot shrink the existing immutable prefix")
    if pages is not None and pages < len(canary_offsets):
        raise ValueError(f"--pages includes the {len(canary_offsets)} reused canary pages and cannot be smaller")
    if pages is not None and pages > len(plan):
        raise ValueError(f"--pages exceeds the {len(plan)} pages in this split")
    limit = pages if pages is not None else len(plan)
    while True:
        candidates, rows_screened, filter_failures, rejected = candidates_from_cache()
        if pages is None and len(frozen) + len(candidates) >= freeze_count:
            break
        remaining = [offset for offset in plan[:limit] if offset not in all_pages]
        if not remaining:
            break
        batch = remaining[:4]
        phase = start_phase("capture_pages_" + "_".join(map(str, batch)))
        def capture(offset):
            url = page_url(config, offset)
            response = fetcher(url)
            validate_response(response, offset, config["page_size"], total)
            return offset, url, response
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            fetched = list(pool.map(capture, batch))
        finish_phase(phase)
        for offset, url, response in fetched:
            path = root / "source_cache" / f"rows_{offset:06d}.json"
            if path.exists():
                raise RuntimeError(f"Unpinned cache file exists: {path}; refusing to replace it")
            wrapper = {"source_url": url, "fetched_at": datetime.now(timezone.utc).isoformat(),
                       "dataset_revision_checked": REVISION, "revision_checks": {"before": phase["before"], "after": phase["after"]},
                       "response": response}
            atomic_json(path, wrapper)
            pin = {"offset": offset, "file": str(path.relative_to(root)), "sha256": digest(path.read_bytes()),
                   "url": url, "dataset_revision": REVISION, "reused_canary_cache": False,
                   "revision_checks": wrapper["revision_checks"]}
            indexed[offset] = pin
            all_pages[offset] = (response, pin, path)
        save_index()
        print(json.dumps({"capture_pages": len(all_pages), "rows_screened": rows_screened + sum(len(r[2]["rows"]) for r in fetched),
                          "eligible_before_new_batch_screen": len(frozen) + len(candidates)}, sort_keys=True), flush=True)
    proposed = frozen + candidates[:max(0, freeze_count - len(frozen))]
    for number, record in enumerate(proposed, 1):
        if "review_id" not in record:
            record["review_id"] = f"HC{number:03d}"
    verify_prefix(existing, proposed)
    if proposed != existing:
        atomic_json(existing_path, proposed)
    candidate_records = frozen + candidates
    for number, record in enumerate(candidate_records, 1):
        record.setdefault("review_id", f"HC{number:03d}")
    atomic_json(root / "CANDIDATES.json", candidate_records)
    summary = {
        "dataset": DATASET, "revision": REVISION, "split": config["split"],
        "target_sources": config["target_sources"], "requested_freeze_count": freeze_count,
        "frozen_sources": len(proposed), "eligible_unique_sources": len(frozen) + len(candidates),
        "target_complete": len(proposed) == config["target_sources"],
        "requested_prefix_complete": len(proposed) >= freeze_count,
        "status": "target_complete" if len(proposed) == config["target_sources"] else "partial_source_sample",
        "rows_screened": rows_screened, "total_split_rows": total, "pages_captured": len(all_pages),
        "source_screen_rejections": filter_failures, "deduplication_rejections": rejected,
        "reused_approved_sources": 50, "reused_canary_rows": sum(len(all_pages[o][0]["rows"]) for o in canary_offsets),
        "all_split_pages_captured": len(all_pages) == len(plan),
        "source_filters": {key: config[key] for key in ("answer_words_min", "answer_words_max", "question_chars_max")},
        "source_screen_implementation_sha256": digest((BASE / "src" / "prepare_sources.py").read_bytes()),
        "approved_packet_sha256": digest(packet_path.read_bytes()),
        "sources_sha256": digest(existing_path.read_bytes()), "cache_files": index["pages"],
        "revision_check_phases": phases,
        "feasibility": estimate_feasibility(len(frozen) + len(candidates), rows_screened, total, config["target_sources"]),
        "selection_is_purposive_not_representative": True,
        "factual_correctness_certified": False,
    }
    atomic_json(root / "SOURCE_CAPTURE_MANIFEST.json", summary)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=BASE / "configs" / "expansion_10000_v1.json")
    parser.add_argument("--pages", type=int, help="total page-plan prefix including the 40 reused canary pages")
    parser.add_argument("--freeze-count", type=int, default=DEFAULT_SAMPLE, help="extend source prefix up to this count (default: 300)")
    args = parser.parse_args()
    config = read_json(args.config)
    summary = prepare(config, pages=args.pages, freeze_count=args.freeze_count)
    print(json.dumps({key: summary[key] for key in ("status", "frozen_sources", "eligible_unique_sources", "rows_screened", "pages_captured", "target_complete", "requested_prefix_complete", "feasibility")}, indent=2))


if __name__ == "__main__":
    main()
