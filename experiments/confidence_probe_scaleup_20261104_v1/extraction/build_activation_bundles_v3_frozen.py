#!/usr/bin/env python3
"""Pinned, provider-free activation extraction and bundle materialization.

The only model operation implemented here is teacher-forced reading of frozen
answer text through the existing, byte-pinned Qwen extraction implementation.
No answer is generated and no language-model weight is updated.  Per-response
caches make an interrupted main extraction resumable.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import stat
import sys
import tempfile
from typing import Any, Mapping, Sequence
import zipfile

import numpy as np


REPO = Path(__file__).resolve().parents[3]
EXP = Path(__file__).resolve().parents[1]
DATA = EXP / "data_prep"

SPLIT_FREEZE = DATA / "SPLIT_FREEZE.json"
SPLIT_FREEZE_SHA256 = "84391340c85ced2863d8b2c4181a12c724ba96a138afb488de8bf5f6444733ea"
EXTRACTION_SOURCE = REPO / "experiments/diverse_pairs_multilayer_v1/src/extraction.py"
EXTRACTION_SOURCE_SHA256 = "cee9f9613cfcc1098dd21785c5f17052eea8bd1fe7860cd0df06d43c2932f4d5"
REFERENCE_CONFIG = REPO / "experiments/diverse_pairs_multilayer_v1/configs/diverse_pairs_multilayer_v1.yaml"
REFERENCE_CONFIG_SHA256 = "1c8f857b2ba62d236e3eec55c7647285bc5aa673935ab824b97bc57f835fae9a"
FEATURE_SETTINGS_SHA256 = "636f0513795e9ed72f0c0b65f50d91e614bfb2c624d9e20ec13dd169146d5138"
EXPECTED_PYTHON_VERSION = (3, 11, 14)
EXPECTED_TORCH_VERSION = "2.14.0"
EXPECTED_TRANSFORMERS_VERSION = "4.57.6"
EXPECTED_DEVICE = "mps"
EXPECTED_DTYPE = "float16"
EXPECTED_CHAT_TEMPLATE_SHA256 = "2e2d2512cfe46af53dc1eed45368ecaab26ac4461c480e6b69fe571cf0ceaa75"
EXPECTED_MODEL_CONFIG_SHA256 = "98d2ff8cc47488d08a2b0b3acf4eb99ef210779b42bd48605f6b8e36acdbf670"
EXPECTED_WEIGHT_SHA256 = "dd924a11b4c220f385b51ffa522daea7c9f3d850e31b162bb5661df483c6d3ee"
EXPECTED_WEIGHT_BYTES = 3087467144
EXPECTED_TOKENIZER_SHA256 = "c0382117ea329cdf097041132f6d735924b697924d6f6fc3945713e96ce87539"
EXPECTED_TOKENIZER_CONFIG_SHA256 = "5b5d4f65d0acd3b2d56a35b56d374a36cbc1c8fa5cf3b3febbbfabf22f359583"
MODEL_ID = "Qwen/Qwen2.5-1.5B-Instruct"
MODEL_REVISION = "989aa7980e4cf806f80c7fef2b1adb7bc71aa306"
LAYER_IDS = tuple(range(1, 29))
HIDDEN_SIZE = 1536
POSITIONS = ("response_mean", "final_response_token", "final_prompt_token")
PAIR_ORDER = ("confident", "hesitant")

DATA_FILES = {
    "train": DATA / "train_920.jsonl",
    "dev": DATA / "dev_156.jsonl",
    "internal_test": DATA / "internal_test_193.jsonl",
    "external_cf3": DATA / "external_cf3_113.jsonl",
}
EXPECTED_COUNTS = {"train": 920, "dev": 156, "internal_test": 193, "external_cf3": 113}
MAIN_SPLITS = ("train", "dev", "internal_test")
EXPECTED_NEW_MAIN_FORWARDS = 2 * sum(EXPECTED_COUNTS[name] for name in MAIN_SPLITS)

CF3_CACHE = REPO / "experiments/cf3_transfer_all11_all28_v1/cache/cf3_qwen_states"
MAIN_CACHE = EXP / "extraction/cache/main_response_states"
BUNDLE_DIR = EXP / "extraction/bundles_v3"
AUDIT_DIR = EXP / "extraction/audits_v3"
V1_BUNDLE_DIR = EXP / "extraction/bundles"
V1_AUDIT_DIR = EXP / "extraction/audits"
V1_FAILURE_RECORD = EXP / "extraction/V1_BUNDLE_SERIALIZATION_FAILURE.json"
V2_PARTIAL_RECORD = EXP / "extraction/V2_PARTIAL_LIFECYCLE_RECORD.json"
V1_ARTIFACT_SHA256 = {
    "bundles/dev_156_activations.npz": "129e970b2d40b62cd615b2112f43ea986e761963c85b2346edcdab856f4bf115",
    "bundles/external_cf3_113_activations.npz": "8ff9409396c0f3a2ffa6a958549f34ec28da4b2241cdee1376c2143018ae29ce",
    "bundles/internal_test_193_activations.npz": "bd70975db26961f781fa0d309468dd7ddf562ff45e70b3802c9f466f1af50bb9",
    "bundles/train_920_activations.npz": "41f85b8d7a88d61e02742a6f974bf8c6b4effb8af4028cd09fddcb428663f8d1",
    "audits/CF3_BUNDLE_AUDIT.json": "10674d3f74610fd0f48ae3081a087af2c37f89bde38daa92ba9a809b116c7946",
    "audits/MAIN_EXTRACTION_AUDIT.json": "ec1be4d2b0b07dd703930e63069d1848ae68ba3e12c2cb2360b356db6a7bfdc5",
}
RUNNER_SOURCE = EXP / "runner_prep/run_probe_learning_curve.py"
RUNNER_SHA256 = "12e94409c637ab9a55780fbbfa9478aaa8b384664cef22d30faa1a2b5efef89c"
PREREGISTRATION = EXP / "runner_prep/PREREGISTRATION.json"
PREREGISTRATION_SHA256 = "48accc0639181dd28b9734a901517ecc6412333c30255600942d767a37a8f38c"
EXPECTED_PYTHON = REPO.parent / "semantic-entropy-probes-stage0/.venv/bin/python"
V2_PARTIAL_SHA256 = {
    "bundles_v2/dev_156_activations.npz": "883d5ce0bfc4784b48f84486e428e29430f529f1bf35c7e912692ed16bf5fcae",
    "bundles_v2/internal_test_193_activations.npz": "11ee94ee6ee3ed27e1f2d06fedd3d448dad9dbd19e799f1c37297edbda80df4f",
    "bundles_v2/train_920_activations.npz": "4b0fbca46316857df0a2e68300b44581f463022b02c91e41dd7f452e0989d20d",
    "audits_v2/MAIN_EXTRACTION_AUDIT.json": "40c70a52f6f8c6aee71af2cc08fb0d2feab7b905726dae40faa5dbca14456dc1",
}


class ExtractionContractError(RuntimeError):
    pass


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def pair_content_sha256(row: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_json_bytes({
        "id": row["id"], "source_id": row["source_id"],
        "question": row["question"],
        "confident_response": row["confident_response"],
        "hesitant_response": row["hesitant_response"],
    })).hexdigest()


def response_content_sha256(row: Mapping[str, Any], role: str) -> str:
    if role not in PAIR_ORDER:
        raise ExtractionContractError("unknown response role")
    return hashlib.sha256(canonical_json_bytes({
        "id": row["id"], "source_id": row["source_id"],
        "question": row["question"], "role": role,
        "response": row[f"{role}_response"],
    })).hexdigest()


def state_binding_sha256(state: np.ndarray, response_hash: str) -> str:
    contiguous = np.ascontiguousarray(state)
    header = canonical_json_bytes({
        "response_content_sha256": response_hash,
        "dtype": contiguous.dtype.str,
        "shape": list(contiguous.shape),
    })
    return hashlib.sha256(header + contiguous.tobytes(order="C")).hexdigest()


def _strict_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        value = json.loads(line)
        if type(value) is not dict:
            raise ExtractionContractError(f"non-object row at {path}:{number}")
        for key in ("id", "source_id", "group_id", "question",
                    "confident_response", "hesitant_response"):
            if not isinstance(value.get(key), str) or not value[key]:
                raise ExtractionContractError(f"invalid {key} at {path}:{number}")
        rows.append(value)
    return rows


def authenticate_inputs() -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any]]:
    if file_sha256(SPLIT_FREEZE) != SPLIT_FREEZE_SHA256:
        raise ExtractionContractError("split freeze changed")
    freeze = json.loads(SPLIT_FREEZE.read_text(encoding="utf-8"))
    if freeze.get("schema") != "confidence-probe-scaleup-split-freeze-v1":
        raise ExtractionContractError("unexpected split freeze schema")
    rows: dict[str, list[dict[str, Any]]] = {}
    for name, path in DATA_FILES.items():
        record = freeze["splits"][name]
        if file_sha256(path) != record["sha256"]:
            raise ExtractionContractError(f"{name} JSONL changed")
        rows[name] = _strict_rows(path)
        if len(rows[name]) != EXPECTED_COUNTS[name] or record["count"] != EXPECTED_COUNTS[name]:
            raise ExtractionContractError(f"{name} count changed")
    ids = [row["id"] for split in rows.values() for row in split]
    if len(ids) != len(set(ids)):
        raise ExtractionContractError("pair IDs overlap across frozen splits")
    return rows, freeze


def import_pinned_extraction() -> Any:
    if file_sha256(EXTRACTION_SOURCE) != EXTRACTION_SOURCE_SHA256:
        raise ExtractionContractError("pinned extraction implementation changed")
    if file_sha256(REFERENCE_CONFIG) != REFERENCE_CONFIG_SHA256:
        raise ExtractionContractError("pinned extraction config changed")
    spec = importlib.util.spec_from_file_location("confidence_scaleup_pinned_extraction", EXTRACTION_SOURCE)
    if spec is None or spec.loader is None:
        raise ExtractionContractError("cannot import pinned extraction implementation")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if file_sha256(EXTRACTION_SOURCE) != EXTRACTION_SOURCE_SHA256:
        raise ExtractionContractError("extraction implementation changed during import")
    return module


def authenticate_runner_pins(
    runner_path: Path = RUNNER_SOURCE,
    preregistration_path: Path = PREREGISTRATION,
    runner_sha256: str = RUNNER_SHA256,
    preregistration_sha256: str = PREREGISTRATION_SHA256,
) -> dict[str, str]:
    if not runner_path.is_file() or runner_path.is_symlink() or file_sha256(runner_path) != runner_sha256:
        raise ExtractionContractError("final probe runner pin changed")
    if (not preregistration_path.is_file() or preregistration_path.is_symlink()
            or file_sha256(preregistration_path) != preregistration_sha256):
        raise ExtractionContractError("final preregistration pin changed")
    return {"runner_sha256": runner_sha256,
            "preregistration_sha256": preregistration_sha256}


def verify_runtime_versions(extraction: Any) -> None:
    if tuple(sys.version_info[:3]) != EXPECTED_PYTHON_VERSION:
        raise ExtractionContractError("Python runtime differs from the pinned environment")
    if extraction.torch.__version__ != EXPECTED_TORCH_VERSION:
        raise ExtractionContractError("PyTorch runtime differs from the pinned environment")
    if extraction.transformers.__version__ != EXPECTED_TRANSFORMERS_VERSION:
        raise ExtractionContractError("Transformers runtime differs from the pinned environment")


def feature_identity_preflight(extraction: Any, config: dict[str, Any]) -> dict[str, Any]:
    """Reconstruct the extraction fingerprint before any model can load."""
    verify_runtime_versions(extraction)
    device = extraction.choose_device(config)
    dtype_name = config["runtime"]["cpu_dtype" if device.type == "cpu" else "accelerator_dtype"]
    tokenizer = extraction.load_tokenizer(config)
    try:
        snapshot = extraction.local_snapshot(config)
        settings = {
            "version": 1, "model": config["model"],
            "torch": extraction.torch.__version__,
            "transformers": extraction.transformers.__version__,
            "positions": extraction.POSITIONS,
            "device": str(device), "dtype": dtype_name, "cache_dtype": "float16",
            "padding": "right; same padded length within each source",
            "chat_template_sha256": extraction.digest(tokenizer.chat_template),
            "implementation_sha256": file_sha256(EXTRACTION_SOURCE),
            "model_config_sha256": file_sha256(snapshot / "config.json"),
            "weight_size_bytes": (snapshot / "model.safetensors").stat().st_size,
            "weight_sha256": file_sha256(snapshot / "model.safetensors"),
            "tokenizer_file_sha256": file_sha256(snapshot / "tokenizer.json"),
            "tokenizer_config_sha256": file_sha256(snapshot / "tokenizer_config.json"),
            "layer_convention": extraction.layer_convention(config),
        }
    finally:
        del tokenizer
    exact = {
        "device": EXPECTED_DEVICE,
        "dtype": EXPECTED_DTYPE,
        "chat_template_sha256": EXPECTED_CHAT_TEMPLATE_SHA256,
        "implementation_sha256": EXTRACTION_SOURCE_SHA256,
        "model_config_sha256": EXPECTED_MODEL_CONFIG_SHA256,
        "weight_size_bytes": EXPECTED_WEIGHT_BYTES,
        "weight_sha256": EXPECTED_WEIGHT_SHA256,
        "tokenizer_file_sha256": EXPECTED_TOKENIZER_SHA256,
        "tokenizer_config_sha256": EXPECTED_TOKENIZER_CONFIG_SHA256,
    }
    for key, wanted in exact.items():
        if settings.get(key) != wanted:
            raise ExtractionContractError(f"pre-forward feature setting differs: {key}")
    fingerprint = extraction.digest(settings)
    if fingerprint != FEATURE_SETTINGS_SHA256:
        raise ExtractionContractError("pre-forward feature fingerprint differs")
    return {"settings_sha256": fingerprint, "settings": settings}


def verify_exact_cli(mode: str) -> list[str]:
    expected = [str(EXPECTED_PYTHON), str(Path(__file__).resolve()), "--mode", mode]
    observed = [sys.executable, str(Path(sys.argv[0]).resolve()), *sys.argv[1:]]
    if observed != expected:
        raise ExtractionContractError(
            "use the exact pinned .venv Python and absolute script argv documented in README")
    return observed


def flat_rows(pairs: Sequence[Mapping[str, Any]]) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    for pair in pairs:
        for role, variant in (("confident", "confident"), ("hesitant", "hedged")):
            result.append({
                "source_id": str(pair["source_id"]),
                "group_id": str(pair["group_id"]),
                "variant": variant,
                "prompt": str(pair["question"]),
                "response_text": str(pair[f"{role}_response"]),
                "human_review": "pending",
            })
    return result


def _write_deterministic_npz(path: Path, arrays: Mapping[str, np.ndarray]) -> None:
    """Write deterministic NPZ bytes to an already chosen temporary path."""
    with zipfile.ZipFile(path, mode="w", compression=zipfile.ZIP_DEFLATED,
                         compresslevel=6, allowZip64=True) as archive:
        for key in sorted(arrays):
            # ``np.ascontiguousarray`` promotes a 0-D scalar to shape (1,).
            # Preserve scalar metadata exactly; only normalize non-scalars.
            array = np.asarray(arrays[key])
            if array.ndim > 0:
                array = np.ascontiguousarray(array)
            stream = io.BytesIO()
            np.lib.format.write_array(stream, array, allow_pickle=False)
            info = zipfile.ZipInfo(f"{key}.npy", date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o600 & 0xFFFF) << 16
            archive.writestr(info, stream.getvalue(), compress_type=zipfile.ZIP_DEFLATED,
                             compresslevel=6)


def _private_owner_file(path: Path) -> bool:
    """Accept 0600 or OneDrive-normalized 0700; never group/other access."""
    mode = stat.S_IMODE(path.stat().st_mode)
    return (mode & 0o600) == 0o600 and (mode & 0o077) == 0


def _atomic_npz(path: Path, **arrays: np.ndarray) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.parent.is_symlink():
        raise ExtractionContractError("bundle parent may not be a symlink")
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".npz", dir=path.parent)
    os.close(descriptor)
    temporary = Path(temporary_name)
    try:
        _write_deterministic_npz(temporary, arrays)
        os.chmod(temporary, 0o600)
        staged_sha = file_sha256(temporary)
        if path.exists() or path.is_symlink():
            if (not path.is_file() or path.is_symlink() or file_sha256(path) != staged_sha
                    or path.stat().st_size != temporary.stat().st_size):
                raise ExtractionContractError(f"existing bundle differs: {path}")
            if not _private_owner_file(path):
                raise ExtractionContractError(f"existing bundle mode differs: {path}")
            return "verified_existing"
        os.replace(temporary, path)
        return "created"
    finally:
        temporary.unlink(missing_ok=True)


def _atomic_json(path: Path, value: Any) -> str:
    payload = canonical_json_bytes(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.parent.is_symlink():
        raise ExtractionContractError("audit parent may not be a symlink")
    if path.exists() or path.is_symlink():
        if (not path.is_file() or path.is_symlink() or path.read_bytes() != payload
                or not _private_owner_file(path)):
            raise ExtractionContractError(f"existing audit differs: {path}")
        return "verified_existing"
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


def build_bundle_arrays(rows: Sequence[Mapping[str, Any]], states: np.ndarray) -> dict[str, np.ndarray]:
    states = np.asarray(states)
    expected = (len(rows), 2, len(LAYER_IDS), HIDDEN_SIZE)
    if states.shape != expected or not np.isfinite(states).all():
        raise ExtractionContractError(f"activation shape/values differ: {states.shape} != {expected}")
    # The saved tensor and its binding must use identical bytes even if a
    # caller hands us a wider floating dtype.
    states = np.ascontiguousarray(states.astype(np.float16, copy=False))
    pair_hashes = [pair_content_sha256(row) for row in rows]
    response_hashes = np.asarray([
        [response_content_sha256(row, role) for role in PAIR_ORDER] for row in rows
    ])
    bindings = np.empty((len(rows), 2), dtype="<U64")
    for i in range(len(rows)):
        for j in range(2):
            bindings[i, j] = state_binding_sha256(states[i, j], response_hashes[i, j])
    return {
        "pair_ids": np.asarray([row["id"] for row in rows]),
        "pair_content_sha256": np.asarray(pair_hashes),
        "pair_order": np.asarray(PAIR_ORDER),
        "response_content_sha256": response_hashes,
        "state_binding_sha256": bindings,
        "states": states,
        "layer_ids": np.asarray(LAYER_IDS, dtype=np.int64),
        "position": np.asarray("response_mean"),
        "settings_sha256": np.asarray(FEATURE_SETTINGS_SHA256),
        "model_id": np.asarray(MODEL_ID),
        "model_revision": np.asarray(MODEL_REVISION),
        "split_freeze_sha256": np.asarray(SPLIT_FREEZE_SHA256),
        "runner_sha256": np.asarray(RUNNER_SHA256),
        "preregistration_sha256": np.asarray(PREREGISTRATION_SHA256),
        "bundle_schema_version": np.asarray("v3_scalar_metadata_private_mode"),
        "bundle_builder_sha256": np.asarray(file_sha256(Path(__file__))),
    }


def authenticate_and_record_v1_failure() -> dict[str, Any]:
    """Preserve and fingerprint the invalid v1 publication before v2 output."""
    observed: dict[str, str] = {}
    for relative, wanted in V1_ARTIFACT_SHA256.items():
        path = EXP / "extraction" / relative
        if not path.is_file() or path.is_symlink() or file_sha256(path) != wanted:
            raise ExtractionContractError(f"preserved v1 artifact changed: {relative}")
        observed[relative] = wanted
    scalar_shapes: dict[str, dict[str, list[int]]] = {}
    scalar_keys = ("position", "settings_sha256", "model_id", "model_revision",
                   "split_freeze_sha256", "runner_sha256", "preregistration_sha256")
    for path in sorted(V1_BUNDLE_DIR.glob("*.npz")):
        with np.load(path, allow_pickle=False) as saved:
            shapes = {key: list(saved[key].shape) for key in scalar_keys}
        if any(shape != [1] for shape in shapes.values()):
            raise ExtractionContractError("v1 failure signature changed")
        scalar_shapes[path.name] = shapes
    record = {
        "schema": "confidence-probe-scaleup-v1-bundle-serialization-failure-v1",
        "status": "terminal_preserved_not_valid_for_runner",
        "model_forwards_already_completed": 2538,
        "response_caches_preserved": 2538,
        "cause": "deterministic NPZ writer applied np.ascontiguousarray to 0-D scalar metadata, promoting required shape () to (1,)",
        "runner_failure": "scalar metadata keys must have shape ()",
        "no_model_forward_retry_required": True,
        "v1_artifact_sha256": observed,
        "observed_scalar_shapes": scalar_shapes,
        "replacement_output": "bundles_v2 and audits_v2 from authenticated caches only",
    }
    lifecycle = _atomic_json(V1_FAILURE_RECORD, record)
    return {"record": str(V1_FAILURE_RECORD.relative_to(REPO)),
            "sha256": file_sha256(V1_FAILURE_RECORD), "lifecycle": lifecycle}


def authenticate_and_record_v2_partial() -> dict[str, Any]:
    observed: dict[str, str] = {}
    for relative, wanted in V2_PARTIAL_SHA256.items():
        path = EXP / "extraction" / relative
        if not path.is_file() or path.is_symlink() or file_sha256(path) != wanted:
            raise ExtractionContractError(f"preserved v2 artifact changed: {relative}")
        observed[relative] = wanted
    record = {
        "schema": "confidence-probe-scaleup-v2-partial-lifecycle-record-v1",
        "status": "terminal_preserved_superseded_by_complete_v3",
        "main_bundles_runner_valid": True,
        "main_cache_rematerialization": {"new_forwards": 0, "cache_hits": 2538},
        "cf3_bundle_present": False,
        "reason": "v2 main repaired scalar metadata, but exact-0600 resume checks conflicted with OneDrive owner-only 0700 normalization before the CF3 v2 bundle could publish",
        "not_final_complete_bundle_set": True,
        "v2_artifact_sha256": observed,
        "replacement_output": "complete bundles_v3 and audits_v3 from authenticated caches only",
    }
    lifecycle = _atomic_json(V2_PARTIAL_RECORD, record)
    return {"record": str(V2_PARTIAL_RECORD.relative_to(REPO)),
            "sha256": file_sha256(V2_PARTIAL_RECORD), "lifecycle": lifecycle}


def _validate_response_cache(path: Path, token: Mapping[str, Any], extraction: Any) -> np.ndarray:
    if not path.is_file() or path.is_symlink():
        raise ExtractionContractError(f"missing/unsafe response cache: {path}")
    with np.load(path, allow_pickle=False) as saved:
        required = {"pooled", "input_ids", "response_mask", "layer_ids", "positions", "settings_sha256"}
        if not required <= set(saved.files):
            raise ExtractionContractError("response cache is incomplete")
        if str(saved["settings_sha256"].item()) != FEATURE_SETTINGS_SHA256:
            raise ExtractionContractError("response cache feature identity changed")
        if saved["input_ids"].tolist() != list(token["input_ids"]):
            raise ExtractionContractError("response cache token identity changed")
        wanted_mask = np.zeros(len(token["input_ids"]), dtype=np.bool_)
        wanted_mask[int(token["response_start"]):int(token["response_stop"])] = True
        if not np.array_equal(saved["response_mask"], wanted_mask):
            raise ExtractionContractError("response cache span changed")
        if tuple(saved["layer_ids"].tolist()) != LAYER_IDS:
            raise ExtractionContractError("response cache layers changed")
        if tuple(saved["positions"].tolist()) != POSITIONS:
            raise ExtractionContractError("response cache positions changed")
        pooled = saved["pooled"].copy()
    if pooled.shape != (28, 3, HIDDEN_SIZE) or not np.isfinite(pooled).all():
        raise ExtractionContractError("response cache pooled tensor invalid")
    return pooled


def _tokenize_pairs(pairs: Sequence[Mapping[str, Any]], extraction: Any, config: dict[str, Any]) -> tuple[list[dict[str, Any]], list[int]]:
    flattened = flat_rows(pairs)
    tokenizer = extraction.load_tokenizer(config)
    try:
        tokens = [extraction.tokenize_response(row, tokenizer, config) for row in flattened]
    finally:
        del tokenizer
    padded: list[int] = []
    for i in range(0, len(tokens), 2):
        length = max(len(tokens[i]["input_ids"]), len(tokens[i + 1]["input_ids"]))
        padded.extend([length, length])
    return tokens, padded


def build_cf3_from_existing_cache(rows: Sequence[Mapping[str, Any]], extraction: Any,
                                  config: dict[str, Any]) -> tuple[np.ndarray, dict[str, Any]]:
    tokens, padded = _tokenize_pairs(rows, extraction, config)
    flat_states: list[np.ndarray] = []
    paths: list[str] = []
    for token, padded_length in zip(tokens, padded):
        key = extraction.digest({
            "settings": FEATURE_SETTINGS_SHA256,
            "input_ids": token["input_ids"],
            "padded_length": padded_length,
        })
        path = CF3_CACHE / f"{key}.npz"
        flat_states.append(_validate_response_cache(path, token, extraction))
        paths.append(path.name)
    state = np.stack(flat_states).reshape(len(rows), 2, 28, 3, HIDDEN_SIZE)[:, :, :, 0, :]
    return state, {
        "pairs": len(rows), "responses": 2 * len(rows), "new_forwards": 0,
        "reused_response_caches": 2 * len(rows),
        "cache_inventory_sha256": hashlib.sha256(("\n".join(paths) + "\n").encode()).hexdigest(),
    }


def prepare_config(extraction: Any, *, cache_dir: Path) -> dict[str, Any]:
    config = extraction.load_config(REFERENCE_CONFIG)
    config["runtime"]["max_pairs"] = sum(EXPECTED_COUNTS[name] for name in MAIN_SPLITS)
    config["runtime"]["max_seconds"] = 7200
    config["runtime"]["max_rss_gib"] = 16
    config["runtime"]["cache_dir"] = str(cache_dir)
    config["data"]["phase"] = "train_development_engineering_only"
    return config


def tokenizer_preflight(rows_by_split: Mapping[str, Sequence[Mapping[str, Any]]],
                        extraction: Any, config: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for name, rows in rows_by_split.items():
        tokens, _ = _tokenize_pairs(rows, extraction, config)
        result[name] = {
            "pairs": len(rows), "responses": len(tokens),
            "max_total_input_tokens": max(len(value["input_ids"]) for value in tokens),
            "max_response_tokens": max(len(value["response_ids"]) for value in tokens),
        }
    return result


def load_main_from_existing_cache(
    rows_by_split: Mapping[str, Sequence[Mapping[str, Any]]],
    extraction: Any,
    config: dict[str, Any],
    feature: Mapping[str, Any],
) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    """Authenticate and load all main states without any model-loading path."""
    combined_pairs = [row for name in MAIN_SPLITS for row in rows_by_split[name]]
    if not MAIN_CACHE.is_dir() or MAIN_CACHE.is_symlink():
        raise ExtractionContractError("main response-cache directory is unsafe")
    if feature.get("settings_sha256") != FEATURE_SETTINGS_SHA256:
        raise ExtractionContractError("missing authenticated pre-forward feature identity")
    tokens, padded = _tokenize_pairs(combined_pairs, extraction, config)
    if len(tokens) != EXPECTED_NEW_MAIN_FORWARDS:
        raise ExtractionContractError("main cache denominator changed")
    flat: list[np.ndarray] = []
    paths: list[str] = []
    for token, padded_length in zip(tokens, padded):
        key = extraction.digest({
            "settings": FEATURE_SETTINGS_SHA256,
            "input_ids": token["input_ids"],
            "padded_length": padded_length,
        })
        path = MAIN_CACHE / f"{key}.npz"
        flat.append(_validate_response_cache(path, token, extraction))
        paths.append(path.name)
    flat_states = np.stack(flat)
    response_mean = flat_states[:, :, 0, :]
    bundles: dict[str, np.ndarray] = {}
    cursor = 0
    for name in MAIN_SPLITS:
        responses = 2 * len(rows_by_split[name])
        bundles[name] = response_mean[cursor:cursor + responses].reshape(
            len(rows_by_split[name]), 2, 28, HIDDEN_SIZE)
        cursor += responses
    return bundles, {
        "pairs": sum(len(rows_by_split[name]) for name in MAIN_SPLITS),
        "responses": EXPECTED_NEW_MAIN_FORWARDS,
        "new_forwards_this_run": 0,
        "reused_response_caches_this_run": EXPECTED_NEW_MAIN_FORWARDS,
        "model_loads_this_run": 0,
        "settings_sha256": FEATURE_SETTINGS_SHA256,
        "cache_inventory_sha256": hashlib.sha256(
            ("\n".join(paths) + "\n").encode("utf-8")).hexdigest(),
    }


SCALAR_METADATA_KEYS = (
    "position", "settings_sha256", "model_id", "model_revision",
    "split_freeze_sha256", "runner_sha256", "preregistration_sha256",
)


def validate_v2_against_v1(name: str, v2_path: Path) -> dict[str, Any]:
    v1_path = V1_BUNDLE_DIR / f"{name}_activations.npz"
    if not v1_path.is_file() or v1_path.is_symlink():
        raise ExtractionContractError("preserved v1 comparison bundle is missing")
    with np.load(v1_path, allow_pickle=False) as old, np.load(v2_path, allow_pickle=False) as new:
        for key in old.files:
            if key not in new.files:
                raise ExtractionContractError(f"v2 bundle lost v1 key: {key}")
            if key in SCALAR_METADATA_KEYS:
                if old[key].shape != (1,) or new[key].shape != () or old[key][0] != new[key].item():
                    raise ExtractionContractError(f"v2 scalar repair differs in value: {key}")
            elif not np.array_equal(old[key], new[key]):
                raise ExtractionContractError(f"v2 non-scalar array differs from v1: {key}")
    return {"v1_sha256": file_sha256(v1_path), "all_v1_non_scalars_exact": True,
            "all_v1_scalar_values_exact_with_shape_repaired": True}


def write_bundle(name: str, rows: Sequence[Mapping[str, Any]], states: np.ndarray) -> dict[str, Any]:
    path = BUNDLE_DIR / f"{name}_activations.npz"
    arrays = build_bundle_arrays(rows, states)
    lifecycle = _atomic_npz(path, **arrays)
    comparison = validate_v2_against_v1(name, path)
    return {"path": str(path.relative_to(REPO)), "bytes": path.stat().st_size,
            "sha256": file_sha256(path), "pairs": len(rows), "lifecycle": lifecycle,
            "v1_comparison": comparison}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", required=True, choices=("preflight", "cf3-only", "main"))
    args = parser.parse_args()
    argv = verify_exact_cli(args.mode)
    rows_by_split, _ = authenticate_inputs()
    pins = authenticate_runner_pins()
    extraction = import_pinned_extraction()
    config = prepare_config(extraction, cache_dir=MAIN_CACHE)
    feature = feature_identity_preflight(extraction, config)

    if args.mode == "preflight":
        result = {
            "schema": "confidence-probe-scaleup-extraction-preflight-v1",
            "split_freeze_sha256": SPLIT_FREEZE_SHA256,
            "expected_new_main_forwards": EXPECTED_NEW_MAIN_FORWARDS,
            "tokenizer": tokenizer_preflight(rows_by_split, extraction, config),
            "runtime_argv": argv,
            "runner_pins": pins,
            "feature_settings_sha256": feature["settings_sha256"],
            "model_forward_calls": 0,
        }
        print(json.dumps(result, sort_keys=True, ensure_ascii=False))
        return

    if args.mode == "cf3-only":
        v1_failure = authenticate_and_record_v1_failure()
        v2_partial = authenticate_and_record_v2_partial()
        states, audit = build_cf3_from_existing_cache(rows_by_split["external_cf3"], extraction, config)
        bundle = write_bundle("external_cf3_113", rows_by_split["external_cf3"], states)
        result = {**audit, "bundle": bundle, "runtime_argv": argv,
                  "runner_pins": pins, "feature_settings_sha256": feature["settings_sha256"],
                  "bundle_version": 3, "bundle_builder_sha256": file_sha256(Path(__file__)),
                  "preserved_v1_failure": v1_failure, "preserved_v2_partial": v2_partial}
        lifecycle = _atomic_json(AUDIT_DIR / "CF3_BUNDLE_AUDIT.json", result)
        print(json.dumps({**result, "audit_lifecycle": lifecycle}, sort_keys=True))
        return

    v1_failure = authenticate_and_record_v1_failure()
    v2_partial = authenticate_and_record_v2_partial()
    states, audit = load_main_from_existing_cache(rows_by_split, extraction, config, feature)
    if audit["new_forwards_this_run"] != 0 or audit["reused_response_caches_this_run"] != 2538:
        raise ExtractionContractError("v2 rematerialization must be cache-only 0/2538")
    records = {
        name: write_bundle({"train": "train_920", "dev": "dev_156",
                            "internal_test": "internal_test_193"}[name],
                           rows_by_split[name], states[name])
        for name in MAIN_SPLITS
    }
    result = {**audit, "bundles": records, "runtime_argv": argv,
              "runner_pins": pins, "feature_settings_sha256": feature["settings_sha256"],
              "bundle_version": 3, "bundle_builder_sha256": file_sha256(Path(__file__)),
              "preserved_v1_failure": v1_failure, "preserved_v2_partial": v2_partial}
    lifecycle = _atomic_json(AUDIT_DIR / "MAIN_EXTRACTION_AUDIT.json", result)
    print(json.dumps({**result, "audit_lifecycle": lifecycle}, sort_keys=True))


if __name__ == "__main__":
    main()
