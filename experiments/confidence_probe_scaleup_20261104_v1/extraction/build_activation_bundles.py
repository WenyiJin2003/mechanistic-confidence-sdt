#!/usr/bin/env python3
"""Lifecycle wrapper around the immutable v3 bundle builder.

OneDrive normalizes private files from 0600 to 0700. Completed audits also
contain transient lifecycle labels (created versus verified). This wrapper
accepts only those non-scientific lifecycle-label differences on resume. All
bundle bytes remain produced by the immutable, SHA-pinned v3 builder source.
"""

from __future__ import annotations

import importlib.util
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
import tempfile
from typing import Any


FROZEN = Path(__file__).with_name("build_activation_bundles_v3_frozen.py")
FROZEN_SHA256 = "6b6e0642529baf3306031c70b1a06077aee6c61decafe71a70eaa43fb87c4757"


def _read_regular_nonsymlink(path: Path) -> bytes:
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode):
            raise RuntimeError(f"frozen builder is not a regular file: {path}")
        with os.fdopen(descriptor, "rb") as handle:
            descriptor = -1
            return handle.read()
    finally:
        if descriptor >= 0:
            os.close(descriptor)


def _load_verified_frozen_module(path: Path, expected_sha256: str):
    if path.is_symlink():
        raise RuntimeError(f"frozen builder may not be a symlink: {path}")
    source = _read_regular_nonsymlink(path)
    if hashlib.sha256(source).hexdigest() != expected_sha256:
        raise RuntimeError("frozen v3 builder source changed")
    spec = importlib.util.spec_from_file_location("confidence_scaleup_v3_frozen_builder", path)
    if spec is None:
        raise RuntimeError("cannot create frozen v3 builder module")
    module = importlib.util.module_from_spec(spec)
    exec(compile(source, str(path), "exec"), module.__dict__)
    if hashlib.sha256(_read_regular_nonsymlink(path)).hexdigest() != expected_sha256:
        raise RuntimeError("frozen v3 builder source changed during import")
    return module


core = _load_verified_frozen_module(FROZEN, FROZEN_SHA256)


def _strip_lifecycle(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _strip_lifecycle(item) for key, item in value.items()
                if key not in {"lifecycle", "audit_lifecycle"}}
    if isinstance(value, list):
        return [_strip_lifecycle(item) for item in value]
    return value


def _resumable_atomic_json(path: Path, value: Any) -> str:
    payload = core.canonical_json_bytes(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.parent.is_symlink():
        raise core.ExtractionContractError("audit parent may not be a symlink")
    if path.exists() or path.is_symlink():
        if not path.is_file() or path.is_symlink() or not core._private_owner_file(path):
            raise core.ExtractionContractError(f"existing audit is unsafe: {path}")
        existing = path.read_bytes()
        if existing == payload:
            return "verified_existing"
        try:
            old_value = json.loads(existing.decode("utf-8"))
            new_value = json.loads(payload.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise core.ExtractionContractError(f"existing audit differs: {path}") from exc
        if _strip_lifecycle(old_value) != _strip_lifecycle(new_value):
            raise core.ExtractionContractError(f"existing audit differs beyond lifecycle labels: {path}")
        return "verified_existing_lifecycle_equivalent"
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            descriptor = -1
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        return "created"
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        temporary.unlink(missing_ok=True)


def _verify_wrapper_cli(mode: str) -> list[str]:
    expected = [str(core.EXPECTED_PYTHON), str(Path(__file__).resolve()), "--mode", mode]
    observed = [sys.executable, str(Path(sys.argv[0]).resolve()), *sys.argv[1:]]
    if observed != expected:
        raise core.ExtractionContractError(
            "use the exact pinned .venv Python and absolute wrapper argv documented in README")
    return observed


for _name in dir(core):
    if not _name.startswith("__"):
        globals()[_name] = getattr(core, _name)
core._atomic_json = _resumable_atomic_json
core.verify_exact_cli = _verify_wrapper_cli
_atomic_json = _resumable_atomic_json
verify_exact_cli = _verify_wrapper_cli


if __name__ == "__main__":
    core.main()
