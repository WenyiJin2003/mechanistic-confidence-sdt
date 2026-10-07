"""Small shared artifact/config helpers for the paired pilot."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
from typing import Any
import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]

def resolve(value: str | Path) -> Path:
    path = Path(value).expanduser()
    return path.resolve() if path.is_absolute() else (ROOT / path).resolve()

def load_config(path: str | Path) -> dict[str, Any]:
    with resolve(path).open(encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    return config

def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    with resolve(path).open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]

def stable_hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def file_hash(path: str | Path) -> str:
    digest = hashlib.sha256()
    with resolve(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1048576), b""):
            digest.update(chunk)
    return digest.hexdigest()

def write_json(path: str | Path, value: Any) -> None:
    target = resolve(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False)
        handle.write("\n")
    os.replace(temporary, target)

def write_jsonl(path: str | Path, rows: list[dict[str, Any]]) -> None:
    target = resolve(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True, allow_nan=False) + "\n")
    os.replace(temporary, target)

def write_npz(path: str | Path, **arrays: np.ndarray) -> None:
    target = resolve(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + ".tmp.npz")
    np.savez_compressed(temporary, **arrays)
    os.replace(temporary, target)
