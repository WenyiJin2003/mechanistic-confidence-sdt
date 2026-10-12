"""Build a blinded content/tone review packet from completed rewrite JSONL.

This module only reads rewrite text and assignment metadata. It never reads
scores or activations and does not assert that any reviewer is human. It is
safe to call with a partial subset of source rows; --require-full opts into a
50-source completeness check once all rewrites are ready.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Iterable


CHALLENGE = Path(__file__).resolve().parents[1]
PRIVATE = CHALLENGE / "private_data"
DEFAULT_SEED = 20261012
REQUIRED_TEXT_FIELDS = ("source_id", "prompt", "original_response", "confident_response", "hedged_response")
SOURCE_IDENTITY_FIELDS = ("original_response_sha256", "task", "cue_family", "length_direction")
ALLOWED_DIRECTIONS = {"confident_longer", "hedged_longer"}


def _stable_hash(seed: int, purpose: str, source_id: str) -> str:
    material = f"{seed}\0{purpose}\0{source_id}".encode("utf-8")
    return hashlib.sha256(material).hexdigest()


def load_rewrite_rows(paths: Iterable[Path], require_full: bool = False) -> list[dict]:
    """Load one or more completed rewrite JSONL batches; partial batches are valid."""
    rows: list[dict] = []
    seen: set[str] = set()
    for path in paths:
        with Path(path).open(encoding="utf-8") as stream:
            for line_number, line in enumerate(stream, 1):
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"Invalid JSON in {path}:{line_number}: {exc.msg}") from exc
                _validate_row(row, f"{path}:{line_number}")
                source_id = row["source_id"]
                if source_id in seen:
                    raise ValueError(f"Duplicate source_id across rewrite inputs: {source_id}")
                seen.add(source_id)
                rows.append(row)
    if not rows:
        raise ValueError("No rewrite records found")
    if len(rows) > 50:
        raise ValueError(f"Expected at most 50 source records; found {len(rows)}")
    if require_full and len(rows) != 50:
        raise ValueError(f"Full packet requires exactly 50 source records; found {len(rows)}")
    return rows


def load_and_join_rows(source_path: Path, rewrite_paths: Iterable[Path],
                       require_full: bool = False) -> list[dict]:
    """Join compact writer outputs to frozen source text by exact identity."""
    sources = []
    for line_number, line in enumerate(Path(source_path).read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON in {source_path}:{line_number}: {exc.msg}") from exc
        if not isinstance(row, dict) or not isinstance(row.get("source_id"), str):
            raise ValueError(f"Invalid source row at {source_path}:{line_number}")
        sources.append(row)
    source_by_id = {row["source_id"]: row for row in sources}
    if len(source_by_id) != len(sources):
        raise ValueError("Duplicate source_id in source input")

    joined = []
    seen = set()
    for path in rewrite_paths:
        for line_number, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                writer = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON in {path}:{line_number}: {exc.msg}") from exc
            source_id = writer.get("source_id") if isinstance(writer, dict) else None
            if not isinstance(source_id, str) or source_id not in source_by_id:
                raise ValueError(f"Unknown or missing source_id at {path}:{line_number}")
            if source_id in seen:
                raise ValueError(f"Duplicate source_id across rewrite inputs: {source_id}")
            seen.add(source_id)
            source = source_by_id[source_id]
            for field in SOURCE_IDENTITY_FIELDS:
                if writer.get(field) != source.get(field):
                    raise ValueError(f"{field} mismatch for {source_id}")
            row = {**source, **writer}
            _validate_row(row, f"{path}:{line_number}")
            joined.append(row)
    if not joined:
        raise ValueError("No rewrite records found")
    if len(joined) > 50:
        raise ValueError(f"Expected at most 50 source records; found {len(joined)}")
    if require_full and (len(joined) != 50 or set(seen) != set(source_by_id)):
        raise ValueError(f"Full packet requires exactly all 50 source records; found {len(joined)}")
    return joined


def _validate_row(row: dict, location: str) -> None:
    if not isinstance(row, dict):
        raise ValueError(f"Expected a JSON object at {location}")
    missing = [field for field in REQUIRED_TEXT_FIELDS if not isinstance(row.get(field), str) or not row[field].strip()]
    if missing:
        raise ValueError(f"Missing or blank required fields at {location}: {', '.join(missing)}")
    if row["confident_response"] == row["hedged_response"]:
        raise ValueError(f"Confident and hedged text are identical at {location}")
    if not isinstance(row.get("cue_family"), str) or not row["cue_family"]:
        raise ValueError(f"Missing cue_family at {location}")
    if row.get("length_direction") not in ALLOWED_DIRECTIONS:
        raise ValueError(f"Invalid length_direction at {location}")


def build_blind_packet(rows: list[dict], seed: int = DEFAULT_SEED) -> tuple[list[dict], list[dict]]:
    """Return randomized A/B packet rows and a private source/condition mapping."""
    if not 1 <= len(rows) <= 50:
        raise ValueError("Packet size must be between 1 and 50 source records")
    packet: list[dict] = []
    mapping: list[dict] = []
    for row in rows:
        _validate_row(row, row.get("source_id", "<unknown>"))
        source_id = row["source_id"]
        ab_order = _stable_hash(seed, "ab-order", source_id)
        blind_id = "B" + _stable_hash(seed, "blind-id", source_id)[:12]
        confident_is_a = int(ab_order[0], 16) % 2 == 0
        response_a = row["confident_response"] if confident_is_a else row["hedged_response"]
        response_b = row["hedged_response"] if confident_is_a else row["confident_response"]
        packet.append({
            "blind_id": blind_id,
            "prompt": row["prompt"],
            "original_response": row["original_response"],
            "response_a": response_a,
            "response_b": response_b,
        })
        mapping.append({
            "blind_id": blind_id,
            "source_id": source_id,
            "review_id": row.get("review_id"),
            "task": row.get("task"),
            "cue_family": row["cue_family"],
            "intended_length_direction": row["length_direction"],
            "a_role": "confident" if confident_is_a else "hedged",
            "b_role": "hedged" if confident_is_a else "confident",
            "original_response_sha256": row.get("original_response_sha256"),
            "confident_response_sha256": hashlib.sha256(row["confident_response"].encode("utf-8")).hexdigest(),
            "hedged_response_sha256": hashlib.sha256(row["hedged_response"].encode("utf-8")).hexdigest(),
        })
    packet.sort(key=lambda item: _stable_hash(seed, "packet-order", item["blind_id"]))
    mapping_by_id = {item["blind_id"]: item for item in mapping}
    mapping = [mapping_by_id[item["blind_id"]] for item in packet]
    return packet, mapping


def build_response_template(packet: list[dict]) -> list[dict]:
    """Create blank review fields keyed only by opaque blinded IDs."""
    return [{
        "blind_id": row["blind_id"],
        "content_preservation": "",
        "stronger_commitment": "",
        "formatting_mismatch": "",
        "shortcut_concern": "",
        "notes": "",
    } for row in packet]


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
                    encoding="utf-8")


def write_private_packet(rows: list[dict], output_dir: Path = PRIVATE, stem: str = "blind_review",
                         seed: int = DEFAULT_SEED, include_template: bool = False) -> dict[str, Path]:
    packet, mapping = build_blind_packet(rows, seed=seed)
    output_dir = Path(output_dir).resolve()
    private_root = PRIVATE.resolve()
    if output_dir != private_root and private_root not in output_dir.parents:
        raise ValueError(f"Review packet outputs must stay under {private_root}")
    paths = {
        "packet": output_dir / f"{stem}_packet.jsonl",
        "mapping": output_dir / f"{stem}_mapping.jsonl",
    }
    _write_jsonl(paths["packet"], packet)
    _write_jsonl(paths["mapping"], mapping)
    if include_template:
        paths["response_template"] = output_dir / f"{stem}_response_template.jsonl"
        _write_jsonl(paths["response_template"], build_response_template(packet))
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", nargs="+", required=True, type=Path,
                        help="Completed rewrite JSONL batch file(s); partial subsets are accepted")
    parser.add_argument("--sources", type=Path,
                        help="Frozen source JSONL to join with compact writer outputs")
    parser.add_argument("--require-full", action="store_true",
                        help="Require all 50 challenge sources in the combined input")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--stem", default="blind_review", help="Output filename stem for this packet")
    parser.add_argument("--response-template", action="store_true",
                        help="Also write a blank response-form JSONL")
    args = parser.parse_args()
    rows = (load_and_join_rows(args.sources, args.input, require_full=args.require_full)
            if args.sources else load_rewrite_rows(args.input, require_full=args.require_full))
    paths = write_private_packet(rows, stem=args.stem, seed=args.seed,
                                 include_template=args.response_template)
    print(json.dumps({"packet_rows": len(rows), "files": {key: str(value) for key, value in paths.items()},
                      "reviewer_identity_asserted": False}))


if __name__ == "__main__":
    main()
