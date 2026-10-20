"""Append unchanged UltraChat first turns from checksum-pinned training Parquet.

No rewrite provider is called. Existing source pages, configuration and records
are never replaced. Test splits remain reserved. A failed download is not retried.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import urllib.request
from pathlib import Path

from prepare_expansion import (BASE, DATASET, REVISION, atomic_json, canonical,
                               dedupe_sources, digest, read_json, source_keys,
                               validate_config)
from prepare_sources import source_screen

SPLITS = ("train_sft", "train_gen")
SPLIT_ROWS = {"train_sft": 207865, "train_gen": 256032}
SHARDS = [
    ("train_sft", "train_sft-00000-of-00003-a3ecf92756993583.parquet", 243999189, "afa8fa7426081b2a0e732fb50dbb5cd402a28ad5f0dbe66c0d996d63e7220727"),
    ("train_sft", "train_sft-00001-of-00003-0a1804bcb6ae68c6.parquet", 243897199, "c8230190bc8b29084c974ff32f05589b458fad1908fc4b2fb2b9e1e9f7921f03"),
    ("train_sft", "train_sft-00002-of-00003-ee46ed25cfae92c6.parquet", 244131731, "6fe7d2a5e95cf660f972ecaf304aa5632d7f53384e4b0e0d0f44d9c96733c03e"),
    ("train_gen", "train_gen-00000-of-00003-a6c9fb894be3e50b.parquet", 243687391, "8172417116ff18bb0d1ecc2166a658ebabf79a6c9cf02d8cad411fa764548663"),
    ("train_gen", "train_gen-00001-of-00003-d6a0402e417f35ca.parquet", 243300397, "8b9e9ce202df576400e6727fcabb027bc92449767bec00871190d81f1b330de1"),
    ("train_gen", "train_gen-00002-of-00003-c0db75b92a2f48fd.parquet", 243497356, "1fe9ba24c1bc2be447041e93aaca4689342e25470e6dedd4101019decf151922"),
]


def file_hash(path):
    hasher = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def training_files():
    return [{"split": split, "path": "data/" + name, "size": size, "sha256": sha,
             "url": f"https://huggingface.co/datasets/{DATASET}/resolve/{REVISION}/data/{name}"}
            for split, name, size, sha in SHARDS]


def checked_tree():
    url = f"https://huggingface.co/api/datasets/{DATASET}/tree/{REVISION}/data?recursive=false&expand=false"
    request = urllib.request.Request(url, headers={"User-Agent": "information-chat-pinned-parquet/2.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        tree = json.load(response)
    by_path = {entry["path"]: entry for entry in tree}
    for pin in training_files():
        entry = by_path.get(pin["path"], {})
        if (entry.get("type") != "file" or entry.get("size") != pin["size"]
                or entry.get("lfs", {}).get("oid") != pin["sha256"]
                or entry.get("lfs", {}).get("size") != pin["size"]):
            raise RuntimeError("Pinned Hugging Face training-shard metadata changed")
    return {"url": url, "response": tree, "response_sha256": digest(canonical(tree))}


def ensure_file(root, pin):
    """One HTTP attempt; retain incomplete bytes for explicit manual attention."""
    path = root / "source_cache" / "pinned_parquet" / Path(pin["path"]).name
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        partial = path.with_suffix(path.suffix + ".partial")
        if partial.exists():
            raise RuntimeError(f"Incomplete public-source download requires manual attention: {partial}")
        request = urllib.request.Request(pin["url"], headers={"User-Agent": "information-chat-pinned-parquet/2.0"})
        with urllib.request.urlopen(request, timeout=60) as response, partial.open("xb") as stream:
            count = 0
            for chunk in iter(lambda: response.read(1024 * 1024), b""):
                count += len(chunk)
                if count > pin["size"]:
                    raise RuntimeError("Public-source download exceeded its pinned size")
                stream.write(chunk)
            stream.flush()
            os.fsync(stream.fileno())
        if partial.stat().st_size != pin["size"] or file_hash(partial) != pin["sha256"]:
            raise RuntimeError("Public-source download size or SHA256 mismatch; partial retained")
        partial.replace(path)
    if path.stat().st_size != pin["size"] or file_hash(path) != pin["sha256"]:
        raise RuntimeError("Cached public Parquet size or SHA256 mismatch")
    return path


def iter_rows(path, start):
    import pyarrow.parquet as pq
    offset = 0
    for batch in pq.ParquetFile(path).iter_batches(batch_size=256, columns=["prompt_id", "prompt", "messages"]):
        for row in batch.to_pylist():
            if offset >= start:
                yield offset, row
            offset += 1


def prepare_bulk(config, *, base=BASE, freeze_count: int, max_new_files: int | None = None):
    validate_config(config)
    if not isinstance(freeze_count, int) or freeze_count < 50:
        raise ValueError("freeze_count must be an integer of at least 50")
    if max_new_files is not None and (not isinstance(max_new_files, int) or max_new_files < 0):
        raise ValueError("max_new_files must be nonnegative")
    base = Path(base)
    root, canary = base / config["private_dir"], base / config["canary_private_dir"]
    source_path = root / "SOURCES.json"
    sources = read_json(source_path)
    if len(sources) > freeze_count:
        raise ValueError("freeze_count cannot shrink the immutable source prefix")
    old_config = read_json(root / "SOURCE_CONFIG.json")
    if any(config.get(key) != value for key, value in old_config.items()):
        raise RuntimeError("Legacy source configuration changed")
    packet_path = canary / "review_final_v2" / "TRIPLETS_50.json"
    packet = read_json(packet_path)
    approved = packet.get("triplets", [])
    if (packet.get("dataset") != DATASET or packet.get("revision") != REVISION
            or len(approved) != 50 or len(sources) < 50):
        raise RuntimeError("Frozen canary packet changed")
    for original, selected in zip(approved, sources[:50]):
        if any(selected.get(key) != value for key, value in original.items() if key != "source_cache_file"):
            raise RuntimeError("Frozen canary source or rewrite changed")
    dedupe_sources([], sources)
    for number, source in enumerate(sources, 1):
        screened = source_screen(source["raw_source_row"], config)
        if (source.get("review_id") != f"HC{number:03d}" or source.get("group_id") != source.get("source_id")
                or screened is None or any(source.get(key) != value for key, value in screened.items())
                or source.get("question_sha256") != digest(source["question"])
                or source.get("original_sha256") != digest(source["original"])):
            raise RuntimeError("Frozen source text, IDs, quality screen, or hashes changed")
    screen_hash = file_hash(Path(__file__).with_name("prepare_sources.py"))
    legacy_manifest = read_json(root / "SOURCE_CAPTURE_MANIFEST.json")
    if legacy_manifest.get("source_screen_implementation_sha256") != screen_hash:
        raise RuntimeError("Source-screen implementation changed")
    if legacy_manifest.get("approved_packet_sha256") != file_hash(packet_path):
        raise RuntimeError("Approved canary packet hash changed")
    coverage_path, state_path = root / "COVERAGE_CONFIG_v2.json", root / "BULK_SOURCE_STATE.json"
    coverage = {"protocol": "pinned-parquet-training-only-v2", "dataset": DATASET, "revision": REVISION,
                "splits": list(SPLITS), "files": training_files(), "filters_relaxed": False,
                "source_screen_implementation_sha256": screen_hash,
                "canary_packet_sha256": file_hash(packet_path),
                "legacy_source_config_sha256": file_hash(root / "SOURCE_CONFIG.json"),
                "legacy_capture_manifest_sha256": file_hash(root / "SOURCE_CAPTURE_MANIFEST.json"),
                "selection_is_purposive_not_representative": True}
    if coverage_path.exists():
        frozen_coverage = read_json(coverage_path)
        count = frozen_coverage["initial_prefix_count"]
        coverage.update(initial_prefix_count=count, initial_prefix_sha256=digest(canonical(sources[:count])))
        if coverage != frozen_coverage:
            raise RuntimeError("Coverage configuration, canary packet, or original source prefix changed")
    else:
        if legacy_manifest.get("sources_sha256") != file_hash(source_path):
            raise RuntimeError("Initial frozen source file differs from its capture manifest")
        coverage.update(initial_prefix_count=len(sources), initial_prefix_sha256=digest(canonical(sources)))
        atomic_json(coverage_path, coverage)
    state = read_json(state_path) if state_path.exists() else {
        "coverage_config_sha256": digest(canonical(coverage)),
        "cursor": {"file_index": 0, "row_offset": 0, "split_row_idx": 0},
        "committed_sources": len(sources), "sources_prefix_sha256": digest(canonical(sources)), "exhausted": False}
    if (state["coverage_config_sha256"] != digest(canonical(coverage))
            or state["committed_sources"] > len(sources)
            or state["sources_prefix_sha256"] != digest(canonical(sources[:state["committed_sources"]]))):
        raise RuntimeError("Committed bulk source prefix or coverage configuration changed")
    initial_count, downloads = len(sources), 0
    seen = [set(values) for values in zip(*(source_keys(source) for source in sources))]
    cursor, files = state["cursor"], training_files()
    if (set(cursor) != {"file_index", "row_offset", "split_row_idx"}
            or any(not isinstance(value, int) or value < 0 for value in cursor.values())
            or cursor["file_index"] > len(files)):
        raise RuntimeError("Invalid bulk source cursor")

    def checkpoint():
        # Sources are committed first. A crash before state commit replays rows;
        # global dedupe includes already-appended records, so replay cannot skip.
        atomic_json(source_path, sources)
        state.update(committed_sources=len(sources), sources_prefix_sha256=digest(canonical(sources)),
                     exhausted=cursor["file_index"] >= len(files))
        atomic_json(state_path, state)

    manifest_path = root / "BULK_DOWNLOAD_MANIFEST.json"
    manifest = read_json(manifest_path) if manifest_path.exists() else {
        "dataset": DATASET, "revision": REVISION, "files": files, "downloads": {}}
    if manifest.get("dataset") != DATASET or manifest.get("revision") != REVISION or manifest.get("files") != files:
        raise RuntimeError("Pinned bulk download manifest changed")
    tree = None
    pending = 0
    while len(sources) < freeze_count and cursor["file_index"] < len(files):
        pin = files[cursor["file_index"]]
        cache = root / "source_cache" / "pinned_parquet" / Path(pin["path"]).name
        new_file = not cache.exists()
        if new_file and max_new_files is not None and downloads >= max_new_files:
            break
        if tree is None:
            tree = checked_tree()
            manifest["tree_pin"] = tree
        cache = ensure_file(root, pin)
        downloads += int(new_file)
        manifest["downloads"][pin["path"]] = {**pin, "cache_file": str(cache.relative_to(root)), "verified": True}
        atomic_json(manifest_path, manifest)
        ended = True
        for offset, row in iter_rows(cache, cursor["row_offset"]):
            if offset != cursor["row_offset"]:
                raise RuntimeError("Parquet iterator skipped or repeated a row")
            split_row = cursor["split_row_idx"]
            screened = source_screen(row, config)
            if screened is not None and isinstance(row.get("prompt_id"), str) and row["prompt_id"]:
                source = {"source_id": row["prompt_id"], "group_id": row["prompt_id"],
                          "review_id": f"HC{len(sources) + 1:03d}", "split": pin["split"],
                          "row_idx": split_row, "global_row_idx": split_row + (SPLIT_ROWS["train_sft"] if pin["split"] == "train_gen" else 0),
                          "source_shard_file": pin["path"], "source_shard_row_offset": offset,
                          "source_url": pin["url"], "source_cache_file": str(cache.relative_to(root)),
                          "source_cache_sha256": pin["sha256"], "dataset_revision": REVISION,
                          "transport": "pinned_parquet", "raw_source_row": row, **screened,
                          "question_sha256": digest(screened["question"]), "original_sha256": digest(screened["original"]),
                          "raw_source_row_sha256": digest(canonical(row)), "reuse_canary": False,
                          "manual_source_selection": "source_screen_pass_not_fact_certified"}
                keys = source_keys(source)
                if not any(key in used for key, used in zip(keys, seen)):
                    sources.append(source)
                    for key, used in zip(keys, seen):
                        used.add(key)
                    pending += 1
            cursor.update(row_offset=offset + 1, split_row_idx=split_row + 1)
            if pending >= 100 or len(sources) >= freeze_count:
                checkpoint()
                pending = 0
            if len(sources) >= freeze_count:
                ended = False
                break
        if ended:
            cursor.update(file_index=cursor["file_index"] + 1, row_offset=0)
            if cursor["file_index"] == len(files) or files[cursor["file_index"]]["split"] != pin["split"]:
                if cursor["split_row_idx"] != SPLIT_ROWS[pin["split"]]:
                    raise RuntimeError("Pinned split row count differs from the dataset card")
                cursor["split_row_idx"] = 0
            checkpoint()
            pending = 0
    checkpoint()
    result = {"frozen_sources": len(sources), "added_sources": len(sources) - initial_count,
              "requested_freeze_count": freeze_count, "requested_prefix_complete": len(sources) >= freeze_count,
              "exhausted": state["exhausted"], "all_training_files_exhausted": state["exhausted"],
              "downloads_this_run": downloads, "cursor": dict(cursor), "filters_relaxed": False,
              "source_splits": list(SPLITS), "transport": "pinned_parquet", "test_splits_reserved": True,
              "selection_is_purposive_not_representative": True}
    print(json.dumps(result, sort_keys=True), flush=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=BASE / "configs/expansion_10000_v1.json")
    parser.add_argument("--freeze-count", type=int, required=True)
    parser.add_argument("--max-new-files", type=int)
    args = parser.parse_args()
    prepare_bulk(read_json(args.config), freeze_count=args.freeze_count, max_new_files=args.max_new_files)


if __name__ == "__main__":
    main()
