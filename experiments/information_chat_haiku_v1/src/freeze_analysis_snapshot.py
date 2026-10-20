"""Freeze an exact, immutable analysis prefix using only existing local cache.

Only selected Parquet source validation lazily imports local PyArrow. This
module never loads the generation runner or invokes a provider, account command,
or network.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
SCHEMA = "haiku-analysis-snapshot-v1"
SELECTOR_SCHEMA = "haiku-analysis-snapshot-selector-v1"
NORMALIZATIONS = (
    "output_normalization", "identical_duplicate_normalization",
    "reviewed_empty_placeholder_normalization", "local_budget_terminal_normalization",
    "missing_status_metadata_normalization",
)


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def sha(value):
    return hashlib.sha256(value).hexdigest()


def file_sha(path):
    result = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise RuntimeError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def _read(path):
    data = Path(path).read_bytes()
    return json.loads(data, object_pairs_hook=_pairs,
                      parse_constant=lambda value: (_ for _ in ()).throw(
                          RuntimeError(f"Invalid JSON constant: {value}"))), data


def _json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")


def _atomic(path, data, *, immutable=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() == data:
            return
        if immutable:
            raise RuntimeError(f"Refusing to overwrite changed frozen artifact: {path}")
    fd, name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        if immutable:
            try:
                os.link(temporary, path)
            except FileExistsError:
                if path.read_bytes() != data:
                    raise RuntimeError(f"Refusing to overwrite changed frozen artifact: {path}") from None
        else:
            temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def _text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise RuntimeError(f"Expected nonempty text: {label}")
    return value


def _digest(value, label):
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
        raise RuntimeError(f"Invalid SHA-256: {label}")
    return value


def _validate_source(source):
    for key in ("review_id", "source_id", "group_id", "question", "original"):
        _text(source.get(key), key)
    raw = source.get("raw_source_row", {})
    messages = raw.get("messages", [])
    if (len(messages) < 2 or [row.get("role") for row in messages[:2]] != ["user", "assistant"]
            or messages[0].get("content") != source["question"]
            or messages[1].get("content") != source["original"]
            or raw.get("prompt_id") != source["source_id"]
            or source["group_id"] != source["source_id"]):
        raise RuntimeError(f"Source text or group changed: {source['review_id']}")
    for key, expected in (("question_sha256", sha(source["question"].encode())),
                          ("original_sha256", sha(source["original"].encode())),
                          ("raw_source_row_sha256", sha(canonical(raw)))):
        if key in source and source[key] != expected:
            raise RuntimeError(f"Source checksum mismatch: {source['review_id']} {key}")


def _answer_texts(answer):
    for role in ("confident", "hesitant"):
        _text(answer.get(role), role)


class _Pins:
    def __init__(self, root):
        self.root, self.entries, self.values = root, {}, {}

    def add(self, path, role, *, expected=None, binary=False):
        path = path.resolve()
        name = os.path.relpath(path, self.root)
        if name in self.entries:
            value, digest = self.values[name], self.entries[name]["sha256"]
        else:
            if binary:
                value, digest = None, file_sha(path)
            else:
                value, data = _read(path)
                digest = sha(data)
            self.values[name] = value
        if expected is not None and digest != expected:
            raise RuntimeError(f"Pinned file checksum mismatch: {path}")
        old = self.entries.get(name)
        if old and old["sha256"] != digest:
            raise RuntimeError(f"Cache changed while freezing: {path}")
        entry = self.entries.setdefault(name, {"path": name, "sha256": digest, "roles": []})
        if role not in entry["roles"]:
            entry["roles"].append(role)
        return value, name

    def verify(self):
        for entry in self.entries.values():
            if file_sha(self.root / entry["path"]) != entry["sha256"]:
                raise RuntimeError(f"Cache changed while freezing: {entry['path']}")


def _verify_source_caches(sources, pins, config):
    """Validate each selected exact raw row; read a Parquet row group once."""
    by_file = {}
    for source in sources:
        if source.get("source_cache_file"):
            path = (pins.root / source["source_cache_file"]).resolve()
            by_file.setdefault(path, []).append(source)
    for path, selected in by_file.items():
        parquet = path.suffix == ".parquet"
        for source in selected:
            _digest(source.get("source_cache_sha256"), "source_cache_sha256")
            if source.get("dataset_revision", config.get("dataset_revision")) != config.get("dataset_revision"):
                raise RuntimeError(f"Source dataset revision changed: {source['review_id']}")
            pins.add(path, "source_cache", expected=source["source_cache_sha256"], binary=parquet)
        if not parquet:
            if any(source.get("transport") == "pinned_parquet" for source in selected):
                raise RuntimeError("Parquet source locator points to a non-Parquet file")
            page, _ = pins.add(path, "source_cache")
            by_index = {}
            for item in page.get("response", {}).get("rows", []):
                by_index.setdefault(item.get("row_idx"), []).append(item.get("row"))
            for source in selected:
                if by_index.get(source.get("row_idx")) != [source["raw_source_row"]]:
                    raise RuntimeError(f"Original source cache row changed: {source['review_id']}")
            continue
        try:
            import pyarrow.parquet as pq
        except ImportError:
            raise RuntimeError("Selected Parquet source validation requires the existing local PyArrow environment") from None
        offsets = {}
        for source in selected:
            offset = source.get("source_shard_row_offset")
            shard = source.get("source_shard_file")
            split = source.get("split")
            if (source.get("transport") != "pinned_parquet" or type(offset) is not int or offset < 0
                    or not isinstance(shard, str) or Path(shard).name != path.name
                    or split not in ("train_sft", "train_gen") or not path.name.startswith(split + "-")):
                raise RuntimeError(f"Invalid Parquet source row locator: {source['review_id']}")
            if offset in offsets:
                raise RuntimeError("Duplicate selected Parquet row locator")
            offsets[offset] = source
        parquet_file = pq.ParquetFile(path)
        if any(offset >= parquet_file.metadata.num_rows for offset in offsets):
            raise RuntimeError("Selected Parquet row offset is out of range")
        start, validated = 0, 0
        for group in range(parquet_file.num_row_groups):
            stop = start + parquet_file.metadata.row_group(group).num_rows
            group_offsets = [offset for offset in offsets if start <= offset < stop]
            if group_offsets:
                table = parquet_file.read_row_group(group, columns=["prompt_id", "prompt", "messages"])
                for offset in group_offsets:
                    source = offsets[offset]
                    row = table.slice(offset - start, 1).to_pylist()[0]
                    if row != source["raw_source_row"]:
                        raise RuntimeError(f"Original Parquet source row changed: {source['review_id']}")
                    validated += 1
                del table
            start = stop
        if validated != len(selected):
            raise RuntimeError("Selected Parquet source row coverage changed")


def _cached_answers(root):
    """Match build_expansion_review: base ok rows, then sorted repair overlays."""
    generated, origins = {}, {}
    seen_base = set()
    paths = [(path, False) for path in sorted((root / "provider").glob("*.parsed.json"))]
    paths += [(path, True) for path in sorted(root.glob("provider_repairs*/*.parsed.json"))]
    for path, repair in paths:
        parsed, data = _read(path)
        seen_file = set()
        for row in parsed["records"]:
            review_id = _text(row.get("id"), "generated id")
            if review_id in seen_file or (not repair and review_id in seen_base):
                raise RuntimeError(f"Duplicate generated ID: {review_id}")
            seen_file.add(review_id)
            if not repair:
                seen_base.add(review_id)
            if row.get("status") not in ("ok", "reject"):
                raise RuntimeError(f"Invalid cached status: {review_id}")
            if row["status"] == "ok":
                _answer_texts(row)
                generated[review_id] = row
                origins[review_id] = (path, parsed, sha(data), repair)
            elif repair:
                generated.pop(review_id, None)
                origins.pop(review_id, None)
    return generated, origins


def _provenance(source, origin, config, pins):
    path, parsed, parsed_sha, repair = origin
    _, parsed_name = pins.add(path, "parsed", expected=parsed_sha)
    request_path = path.with_name(path.name.replace(".parsed.json", ".request.json"))
    request, request_name = pins.add(request_path, "request")
    request_hash = _digest(request.get("request_sha256"), "request_sha256")
    prompt_hash = _digest(request.get("prompt_sha256"), "prompt_sha256")
    if (parsed.get("request_sha256") != request_hash or request.get("model") != config["model"]
            or parsed.get("model") != config["model"]
            or sha(_text(request.get("prompt"), "prompt").encode()) != prompt_hash):
        raise RuntimeError(f"Request/model/prompt provenance mismatch: {source['review_id']}")
    request_rows = request.get("data", {}).get("records", [])
    requested = [row for row in request_rows if row.get("id") == source["review_id"]]
    ids = [row.get("id") for row in request_rows]
    if (len(ids) != len(set(ids)) or len(requested) != 1
            or requested[0].get("question") != source["question"]
            or requested[0].get("original_response") != source["original"]):
        raise RuntimeError(f"Request source text changed: {source['review_id']}")
    provenance = {"request_sha256": request_hash, "prompt_sha256": prompt_hash,
                  "repair_applied": repair, "request_file": request_name, "parsed_file": parsed_name}
    raw_path = path.with_name(path.name.replace(".parsed.json", ".raw.json"))
    if raw_path.is_file():
        pins.add(raw_path, "raw")
    answer = next(row for row in parsed["records"] if row["id"] == source["review_id"])
    if answer.get("generation_cache_source"):
        cache_source = answer["generation_cache_source"]
        pins.add(pins.root / cache_source, "generation_cache_source")
        provenance.update(generation_cache_source=cache_source,
                          cache_recovery_plan=parsed.get("recovery_plan_file"))
        completion = (pins.root / cache_source).with_name(
            Path(cache_source).name.replace(".raw.json", ".request.json"))
        if completion.is_file():
            pins.add(completion, "generation_cache_request")
    if parsed.get("recovery_plan_file"):
        pins.add(pins.root / parsed["recovery_plan_file"], "recovery_plan")
    for key in NORMALIZATIONS:
        if parsed.get(key):
            provenance[key] = parsed[key]
            expected_raw = parsed[key].get("raw_file_sha256")
            if expected_raw:
                pins.add(raw_path, "raw", expected=expected_raw)
    return provenance


def _verify_manifest(root, packet, manifest):
    count = manifest["count"]
    rows = packet["triplets"]
    sources = manifest["selected_sources"]
    if (len(rows) != count or len(sources) != count or packet["total_triplets"] != count
            or packet["target"] != count or packet["reused_canary_triplets"] != 50
            or packet["new_triplets"] != count - 50):
        raise RuntimeError("Frozen snapshot count mismatch")
    if any(value.get(key) is not False for value in (packet, manifest)
           for key in ("human_review_completed", "content_preservation_certified")):
        raise RuntimeError("Frozen snapshot cannot claim content or human certification")
    if sha(canonical(sources)) != manifest["selection"]["selected_sources_sha256"]:
        raise RuntimeError("Selected source snapshot checksum mismatch")
    for key in ("review_id", "source_id", "group_id"):
        ids = [row[key] for row in rows]
        if len(set(ids)) != count:
            raise RuntimeError(f"Duplicate frozen {key}")
    for source, row in zip(sources, rows):
        _validate_source(source)
        _answer_texts(row)
        if any(row.get(key) != value for key, value in source.items()
               if key not in ("audit_flags", "human_item_rating_received",
                              "user_general_canary_feedback", "content_preservation_certified")):
            raise RuntimeError(f"Frozen source text or metadata mismatch: {source['review_id']}")
        if row.get("human_item_rating_received") is not False or row.get("content_preservation_certified") is not False:
            raise RuntimeError("Frozen row cannot claim human certification")
    if sum(bool(row.get("reuse_canary")) for row in rows) != 50:
        raise RuntimeError("Frozen snapshot must include the original 50 reused triplets")
    if [row["review_id"] for row in rows] != manifest["selection"]["selected_review_ids"]:
        raise RuntimeError("Frozen selected IDs mismatch")
    if [row["source_id"] for row in rows] != manifest["selection"]["selected_source_ids"]:
        raise RuntimeError("Frozen selected source IDs mismatch")


def verify_snapshot(path, *, verify_provenance=True):
    """Verify a selector or snapshot directory without consulting mutable SOURCES."""
    path = Path(path).resolve()
    selector = None
    if path.is_file():
        selector, _ = _read(path)
        if selector.get("schema_version") != SELECTOR_SCHEMA:
            raise RuntimeError("Invalid frozen selector schema")
        directory = Path(selector["snapshot_dir"])
    else:
        directory = path
    packet, packet_data = _read(directory / "TRIPLETS.json")
    manifest, manifest_data = _read(directory / "MANIFEST.json")
    if packet.get("schema_version") != SCHEMA or manifest.get("schema_version") != SCHEMA:
        raise RuntimeError("Invalid frozen snapshot schema")
    digest = sha(canonical(packet))
    if digest != manifest["packet_sha256"] or sha(packet_data) != manifest["triplets_file_sha256"]:
        raise RuntimeError("Frozen triplet checksum mismatch")
    root = Path(manifest["expansion_root"])
    _verify_manifest(root, packet, manifest)
    expected = {"schema_version": SELECTOR_SCHEMA, "count": manifest["count"],
                "snapshot_id": directory.name, "snapshot_dir": str(directory),
                "triplets_file": str(directory / "TRIPLETS.json"),
                "triplets_file_sha256": sha(packet_data), "packet_sha256": digest,
                "manifest_file": str(directory / "MANIFEST.json"),
                "manifest_file_sha256": sha(manifest_data),
                "human_review_completed": False, "content_preservation_certified": False}
    if selector is not None and selector != expected:
        raise RuntimeError("Frozen selector checksum or metadata mismatch")
    if verify_provenance:
        for entry in manifest["provider_files"]:
            if file_sha(root / entry["path"]) != entry["sha256"]:
                raise RuntimeError(f"Frozen provenance checksum mismatch: {entry['path']}")
    return expected


def freeze(root, count=5000, config=None, *, base=BASE):
    """Freeze exactly the first count valid triplets, never rewrite an old freeze."""
    if type(count) is not int or count < 50:
        raise RuntimeError("An analysis snapshot must include all original 50 triplets")
    root, base = Path(root).resolve(), Path(base).resolve()
    config = config if config is not None else _read(base / "configs/expansion_10000_v1.json")[0]
    selector_path = root / f"FROZEN_{count:05d}.json"
    if selector_path.exists():
        result = verify_snapshot(selector_path)
        if result["count"] != count:
            raise RuntimeError("Frozen selector has the wrong requested count")
        return result
    sources, source_bytes = _read(root / "SOURCES.json")
    if not isinstance(sources, list):
        raise RuntimeError("SOURCES.json must be a source-order list")
    for key in ("review_id", "source_id", "group_id"):
        ids = [source.get(key) for source in sources]
        if any(not isinstance(value, str) or not value.strip() for value in ids) or len(set(ids)) != len(ids):
            raise RuntimeError(f"Duplicate or invalid source {key}")
    reused = [source for source in sources if source.get("reuse_canary")]
    if len(reused) != 50 or sources[:50] != reused:
        raise RuntimeError("Source prefix must retain the original 50 reused triplets")
    pins = _Pins(root)
    canary_path = base / config["canary_private_dir"] / "review_final_v2/TRIPLETS_50.json"
    canary, canary_name = pins.add(canary_path, "approved_canary_packet")
    approved = canary["triplets"]
    if len(approved) != 50:
        raise RuntimeError("Original canary packet must contain exactly 50 triplets")
    for source, original in zip(reused, approved):
        # prepare_expansion relocates this pointer relative to the expansion
        # root; it must still resolve to the identical immutable source file.
        pointer = original.get("source_cache_file")
        if pointer and (canary_path.parent.parent / pointer).resolve() != (root / source.get("source_cache_file", "")).resolve():
            raise RuntimeError("Original reused canary cache pointer changed")
        if any(source.get(key) != value for key, value in original.items() if key != "source_cache_file"):
            raise RuntimeError("Original reused canary triplet changed")
    generated, origins = _cached_answers(root)
    triplets, selected_sources, provenance_rows = [], [], []
    for source in sources:
        reuse = source.get("reuse_canary", False)
        if not reuse and source["review_id"] not in generated:
            continue
        _validate_source(source)
        answer = source if reuse else generated[source["review_id"]]
        _answer_texts(answer)
        record = {**source, "confident": answer["confident"], "hesitant": answer["hesitant"],
                  "writer": config["model"], "audit_flags": answer.get("audit_flags", {}),
                  "human_item_rating_received": False,
                  "user_general_canary_feedback": "positive" if reuse else "not_yet_reviewed",
                  "content_preservation_certified": False}
        if answer.get("content_review_notes"):
            record["model_assisted_content_review_notes"] = answer["content_review_notes"]
        if not reuse:
            provenance = _provenance(source, origins[source["review_id"]], config, pins)
            record["rewrite_provenance"] = provenance
            provenance_rows.append({"review_id": source["review_id"], "source_id": source["source_id"], **provenance})
        selected_sources.append(source)
        triplets.append(record)
        if len(triplets) == count:
            break
    if len(triplets) < count:
        raise RuntimeError(f"Insufficient valid cached triplets: {len(triplets)} < {count}; no generation was attempted")
    _verify_source_caches(selected_sources, pins, config)
    packet = {"schema_version": SCHEMA, "protocol": config["protocol"], "target": count,
              "model": config["model"], "canary_approval_scope": config.get("canary_approval", {}),
              "human_review_completed": False, "content_preservation_certified": False,
              "new_triplets": count - 50, "reused_canary_triplets": 50,
              "total_triplets": count, "triplets": triplets}
    packet_hash, packet_data = sha(canonical(packet)), _json_bytes(packet)
    snapshot_id = f"n{count:05d}_{packet_hash[:10]}"
    directory = root / "analysis_snapshots" / snapshot_id
    manifest = {"schema_version": SCHEMA, "snapshot_id": snapshot_id, "count": count,
                "expansion_root": str(root), "packet_sha256": packet_hash,
                "triplets_file_sha256": sha(packet_data), "model": config["model"],
                "dataset": {key: config.get(config_key) for key, config_key in (
                    ("id", "dataset_id"), ("revision", "dataset_revision"),
                    ("split", "split"), ("license", "license"))},
                "selection": {"policy": "first_valid_in_sources_order",
                              "selected_review_ids": [row["review_id"] for row in selected_sources],
                              "selected_source_ids": [row["source_id"] for row in selected_sources],
                              "selected_sources_sha256": sha(canonical(selected_sources))},
                "selected_sources": selected_sources, "config_snapshot": config,
                "source_capture_at_freeze": {"file": "SOURCES.json", "sha256": sha(source_bytes),
                    "source_count": len(sources), "informational_only_mutable_generation_index": True},
                "provider_files": sorted(pins.entries.values(), key=lambda entry: entry["path"]),
                "provenance": provenance_rows, "canary": {"packet_file": canary_name, "reused_count": 50},
                "human_review_completed": False, "content_preservation_certified": False}
    _verify_manifest(root, packet, manifest)
    pins.verify()
    _atomic(directory / "TRIPLETS.json", packet_data, immutable=True)
    _atomic(directory / "MANIFEST.json", _json_bytes(manifest), immutable=True)
    result = verify_snapshot(directory)
    _atomic(selector_path, _json_bytes(result), immutable=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=BASE / "configs/expansion_10000_v1.json")
    parser.add_argument("--root", type=Path)
    parser.add_argument("--count", type=int, default=5000)
    args = parser.parse_args()
    config, _ = _read(args.config)
    root = args.root if args.root is not None else BASE / config["private_dir"]
    print(json.dumps(freeze(root, args.count, config), ensure_ascii=False))


if __name__ == "__main__":
    main()
