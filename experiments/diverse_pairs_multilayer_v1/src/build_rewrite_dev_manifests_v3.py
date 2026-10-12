"""Freeze the v3 smoke and canary source manifests without calling a model.

Only reserve/train sources from the already-frozen 1,200-source pool are used.
The eight-source smoke set is selected first; the 32-source canary is fresh and
disjoint. Public output contains hashes and aggregate counts, never source text.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Sequence


BASE = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = BASE / "configs" / "claude_rewrite_dev_v3.json"
BUILDER_VERSION = "3.0"
RECIPES = ("A", "B")
TOPOLOGIES = ("early", "middle", "late", "distributed")
ORDERS = ("confident_first", "hedged_first")
WILDCHAT = "allenai/WildChat-1M"
HELPSTEER = "nvidia/HelpSteer2"


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


def jsonl_bytes(rows: Iterable[dict[str, Any]]) -> bytes:
    return "".join(
        json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
        for row in rows
    ).encode("utf-8")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def resolve(path: str) -> Path:
    value = Path(path)
    return value if value.is_absolute() else BASE / value


def write_once_or_verify(path: Path, data: bytes) -> bool:
    """Write an immutable freeze artifact, or verify identical existing bytes."""
    if path.exists():
        if path.read_bytes() != data:
            raise FileExistsError(f"Refusing to replace non-identical frozen file: {path}")
        return True
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(data)
    temporary.replace(path)
    return False


def source_ids_sha256(rows: Sequence[dict[str, Any]]) -> str:
    return sha256_text("".join(f"{row['source_id']}\n" for row in rows))


def _stable_key(seed: int, set_name: str, slot_id: str, source_id: str) -> str:
    return sha256_text(f"{seed}:{set_name}:{slot_id}:{source_id}")


def smoke_slots() -> list[dict[str, Any]]:
    slots: list[dict[str, Any]] = []
    for topology_index, topology in enumerate(TOPOLOGIES):
        for replicate in range(2):
            recipe = RECIPES[(topology_index + replicate) % 2]
            order = ORDERS[replicate]
            helpsteer = (topology_index, replicate) in {(0, 0), (2, 1)}
            dataset = HELPSTEER if helpsteer else WILDCHAT
            slots.append({
                "slot_id": f"smoke-{len(slots) + 1:02d}",
                "design_replicate": replicate + 1,
                "rewrite_recipe": recipe,
                "stance_topology": topology,
                "rewrite_output_order": order,
                "dataset": dataset,
            })
    return slots


def canary_slots() -> list[dict[str, Any]]:
    """Return a full 2 recipe x 4 topology x 2 order x 2 replicate design."""
    slots: list[dict[str, Any]] = []
    for recipe_index, recipe in enumerate(RECIPES):
        for topology_index, topology in enumerate(TOPOLOGIES):
            for order_index, order in enumerate(ORDERS):
                for replicate in range(2):
                    # Eight of 32 slots are HelpSteer2, balanced across recipe,
                    # topology, and output order; the other 24 are WildChat.
                    use_helpsteer = (
                        replicate == 0
                        and (recipe_index + topology_index + order_index) % 2 == 0
                    )
                    slots.append({
                        "slot_id": f"canary-{len(slots) + 1:02d}",
                        "design_replicate": replicate + 1,
                        "rewrite_recipe": recipe,
                        "stance_topology": topology,
                        "rewrite_output_order": order,
                        "dataset": HELPSTEER if use_helpsteer else WILDCHAT,
                    })
    return slots


def _selection_penalty(
    row: dict[str, Any],
    task_counts: Counter[str],
    length_counts: Counter[str],
    target_tasks: dict[str, int],
    target_lengths: dict[str, int],
) -> tuple[Fraction, Fraction]:
    """Prefer choices that keep aggregate task and length counts near targets."""
    next_tasks = Counter(task_counts)
    next_lengths = Counter(length_counts)
    next_tasks[str(row["task"])] += 1
    next_lengths[str(row["length_bin"])] += 1
    task_penalty = sum(
        Fraction((next_tasks[name] - int(target)) ** 2, max(1, int(target)))
        for name, target in target_tasks.items()
    )
    length_penalty = sum(
        Fraction((next_lengths[name] - int(target)) ** 2, max(1, int(target)))
        for name, target in target_lengths.items()
    )
    return task_penalty, length_penalty


def select_for_slots(
    candidates: Sequence[dict[str, Any]],
    slots: Sequence[dict[str, Any]],
    *,
    set_name: str,
    seed: int,
    target_tasks: dict[str, int],
    target_lengths: dict[str, int],
    excluded_ids: set[str],
) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    task_counts: Counter[str] = Counter()
    length_counts: Counter[str] = Counter()
    used = set(excluded_ids)
    for slot in slots:
        eligible = [
            row for row in candidates
            if row["source_id"] not in used
            and row["dataset"] == slot["dataset"]
            and row["rewrite_family"] == slot["rewrite_recipe"]
            and row["rewrite_output_order"] == slot["rewrite_output_order"]
        ]
        if not eligible:
            raise RuntimeError(f"No source is available for design slot {slot['slot_id']}")
        chosen = min(
            eligible,
            key=lambda row: (
                *_selection_penalty(
                    row, task_counts, length_counts, target_tasks, target_lengths
                ),
                _stable_key(seed, set_name, slot["slot_id"], row["source_id"]),
            ),
        )
        record = dict(chosen)
        # The old asymmetric target-length assignment is deliberately absent.
        record.pop("target_longer_member", None)
        record.update({
            "rewrite_dev_protocol": "symmetric-diverse-v3",
            "rewrite_dev_set": set_name,
            "rewrite_dev_slot": slot["slot_id"],
            "design_replicate": slot["design_replicate"],
            "rewrite_recipe": slot["rewrite_recipe"],
            "stance_topology": slot["stance_topology"],
            "rewrite_output_order": slot["rewrite_output_order"],
        })
        selected.append(record)
        used.add(record["source_id"])
        task_counts[str(record["task"])] += 1
        length_counts[str(record["length_bin"])] += 1
    return selected


def _counts(rows: Sequence[dict[str, Any]], field: str) -> dict[str, int]:
    return dict(sorted(Counter(str(row[field]) for row in rows).items()))


def _cross_counts(rows: Sequence[dict[str, Any]]) -> dict[str, int]:
    counts = Counter(
        f"{row['rewrite_recipe']}|{row['stance_topology']}|{row['rewrite_output_order']}"
        for row in rows
    )
    return dict(sorted(counts.items()))


def validate_set(
    rows: Sequence[dict[str, Any]],
    *,
    set_name: str,
    expected_count: int,
    main_ids: set[str],
) -> None:
    ids = [str(row["source_id"]) for row in rows]
    if len(rows) != expected_count or len(set(ids)) != expected_count:
        raise ValueError(f"{set_name}: expected {expected_count} unique sources")
    if set(ids) & main_ids:
        raise ValueError(f"{set_name}: overlaps the main/final-test source pool")
    for row in rows:
        if row.get("pool_partition") != "reserve" or row.get("split") != "train":
            raise ValueError(f"{set_name}: source is not reserve/train")
        if row.get("rewrite_recipe") not in RECIPES or row.get("rewrite_family") not in RECIPES:
            raise ValueError(f"{set_name}: recipe C or an unknown recipe is forbidden")
        if row.get("rewrite_recipe") != row.get("rewrite_family"):
            raise ValueError(f"{set_name}: assigned recipe drifted from frozen family")
        if row.get("stance_topology") not in TOPOLOGIES:
            raise ValueError(f"{set_name}: invalid stance topology")
        if "target_longer_member" in row:
            raise ValueError(f"{set_name}: asymmetric target-longer field must be absent")
        if sha256_text(str(row["original_response"])) != row.get("original_response_sha256"):
            raise ValueError(f"{set_name}: original response hash mismatch")
    expected_recipe = expected_count // 2
    expected_order = expected_count // 2
    expected_topology = expected_count // 4
    if _counts(rows, "rewrite_recipe") != {"A": expected_recipe, "B": expected_recipe}:
        raise ValueError(f"{set_name}: recipes are not exactly balanced")
    if _counts(rows, "rewrite_output_order") != {
        "confident_first": expected_order,
        "hedged_first": expected_order,
    }:
        raise ValueError(f"{set_name}: output order is not exactly balanced")
    if _counts(rows, "stance_topology") != {
        topology: expected_topology for topology in sorted(TOPOLOGIES)
    }:
        raise ValueError(f"{set_name}: topologies are not exactly balanced")
    if set_name == "canary" and any(count != 2 for count in _cross_counts(rows).values()):
        raise ValueError("canary: each recipe x topology x order cell must have two rows")


def build(config_path: Path = DEFAULT_CONFIG) -> dict[str, Any]:
    config_bytes = config_path.read_bytes()
    config = json.loads(config_bytes)
    if config.get("protocol_version") != "claude-symmetric-diverse-rewrite-v3":
        raise ValueError("Wrong v3 rewrite configuration")
    reserve_path = resolve(config["reserve_input_path"])
    main_path = resolve(config["main_input_path"])
    source_manifest_path = resolve(config["source_pool_manifest_path"])
    source_manifest = json.loads(source_manifest_path.read_text(encoding="utf-8"))
    expected_hashes = source_manifest["private_output_sha256"]
    if sha256_file(reserve_path) != expected_hashes[reserve_path.name]:
        raise ValueError("Reserve source manifest does not match the frozen source pool")
    if sha256_file(main_path) != expected_hashes[main_path.name]:
        raise ValueError("Main source manifest does not match the frozen source pool")
    reserve_rows = read_jsonl(reserve_path)
    main_rows = read_jsonl(main_path)
    main_ids = {str(row["source_id"]) for row in main_rows}
    reserve_ids = {str(row["source_id"]) for row in reserve_rows}
    if main_ids & reserve_ids:
        raise ValueError("Frozen main and reserve pools overlap")
    candidates = [
        row for row in reserve_rows
        if row.get("pool_partition") == "reserve"
        and row.get("split") == "train"
        and row.get("rewrite_family") in RECIPES
    ]
    seed = int(config["selection_seed"])
    selected: dict[str, list[dict[str, Any]]] = {}
    used: set[str] = set()
    for set_name, slots in (("smoke", smoke_slots()), ("canary", canary_slots())):
        set_config = config["sets"][set_name]
        rows = select_for_slots(
            candidates,
            slots,
            set_name=set_name,
            seed=seed,
            target_tasks=set_config["task_counts"],
            target_lengths=set_config["length_counts"],
            excluded_ids=used,
        )
        validate_set(
            rows,
            set_name=set_name,
            expected_count=int(set_config["count"]),
            main_ids=main_ids,
        )
        for field, config_key in (
            ("dataset", "dataset_counts"),
            ("task", "task_counts"),
            ("length_bin", "length_counts"),
        ):
            if _counts(rows, field) != dict(sorted(set_config[config_key].items())):
                raise ValueError(
                    f"{set_name}: selected {field} coverage differs from the frozen target"
                )
        selected[set_name] = rows
        used.update(str(row["source_id"]) for row in rows)
    if set(row["source_id"] for row in selected["smoke"]) & set(
        row["source_id"] for row in selected["canary"]
    ):
        raise ValueError("Smoke and canary source sets overlap")

    private_dir = resolve(config["private_manifest_dir"])
    set_summaries: dict[str, Any] = {}
    for set_name, rows in selected.items():
        set_config = config["sets"][set_name]
        output_path = private_dir / set_config["input_file"]
        payload = jsonl_bytes(rows)
        write_once_or_verify(output_path, payload)
        set_summaries[set_name] = {
            "count": len(rows),
            "file_name": output_path.name,
            "file_sha256": sha256_bytes(payload),
            "source_ids_sha256": source_ids_sha256(rows),
            "dataset_counts": _counts(rows, "dataset"),
            "task_counts": _counts(rows, "task"),
            "length_counts": _counts(rows, "length_bin"),
            "recipe_counts": _counts(rows, "rewrite_recipe"),
            "topology_counts": _counts(rows, "stance_topology"),
            "output_order_counts": _counts(rows, "rewrite_output_order"),
            "recipe_topology_order_counts": _cross_counts(rows),
            "private_file_write_policy": "write_once_or_verify_identical_bytes",
        }

    public = {
        "freeze_version": BUILDER_VERSION,
        "protocol_version": config["protocol_version"],
        "contains_source_text": False,
        "rewrite_generation_performed": False,
        "selection_seed": seed,
        "selection_scope": "frozen reserve/train only; recipe C excluded",
        "main_and_final_test_excluded": True,
        "smoke_canary_disjoint": True,
        "target_longer_constraint_present": False,
        "config_sha256": sha256_bytes(config_bytes),
        "builder_source_sha256": sha256_file(Path(__file__)),
        "selection_algorithm": (
            "deterministic exact factorial slots with exact-rational task/length "
            "coverage penalty and SHA-256 tie breaking"
        ),
        "source_pool_manifest_sha256": sha256_file(source_manifest_path),
        "source_input_sha256": {
            main_path.name: sha256_file(main_path),
            reserve_path.name: sha256_file(reserve_path),
        },
        "sets": set_summaries,
    }
    public_path = resolve(config["public_freeze_manifest_path"])
    public_bytes = (
        json.dumps(public, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    write_once_or_verify(public_path, public_bytes)
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
