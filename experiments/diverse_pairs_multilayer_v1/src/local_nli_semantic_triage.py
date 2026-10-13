"""Offline, cacheable NLI triage for the 100-source Chat checkpoint.

This module is intentionally a *triage* tool, not a semantic-certification
system.  It compares each frozen original response with the marker-stripped
shared neutral paraphrase.  Long documents are divided into bounded chunks;
every source/template chunk combination is compared in both entailment
directions.  A local DeBERTa NLI model can then flag cases
for label-blind human review.

Source text, per-example scores, and the prediction cache remain under the
ignored ``private_data`` tree.  The public report contains aggregate numbers
and immutable input/model bindings only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence


BASE = Path(__file__).resolve().parents[1]
PRIVATE_ROOT = (BASE / "private_data").resolve()
REPORT_ROOT = (BASE / "reports").resolve()
DEFAULT_CONFIG = BASE / "configs" / "local_nli_semantic_triage_chat_100_v37.json"
PROTOCOL_VERSION = "local-nli-semantic-triage-v1"
CACHE_SCHEMA = "local-nli-semantic-triage-cache-v1"
PRIVATE_SCHEMA = "local-nli-semantic-triage-private-v1"
PUBLIC_SCHEMA = "local-nli-semantic-triage-public-v1"

HEX64_RE = re.compile(r"^[0-9a-f]{64}$")
MARKER_LINE_RE = re.compile(r"(?m)^[ \t]*<STANCE_([12])>[ \t]*(?:\r?\n|$)")
UNKNOWN_MARKER_RE = re.compile(r"<STANCE_[^>]*>")
WORD_RE = re.compile(r"[^\W_]+(?:['’][^\W_]+)?", re.UNICODE)
FENCE_OPEN_RE = re.compile(r"^[ \t]*(?P<fence>`{3,}|~{3,})(?P<tail>.*)$")
CODE_PLACEHOLDER_RE = re.compile(r"PROTECTED_CODE_[0-9a-f]{16}")
TOKENIZER_CANDIDATE_FILES = (
    "tokenizer.json",
    "tokenizer_config.json",
    "special_tokens_map.json",
    "spm.model",
    "added_tokens.json",
    "tokenizer.model",
    "vocab.json",
    "merges.txt",
    "chat_template.jinja",
)


class TriageError(RuntimeError):
    """Raised when a frozen binding or no-truncation invariant is violated."""


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_text(value: str) -> str:
    return sha256_bytes(value.encode("utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: Any) -> str:
    return sha256_bytes(
        json.dumps(
            value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
    )


def _resolve(value: str) -> Path:
    path = Path(value)
    return path.resolve() if path.is_absolute() else (BASE / path).resolve()


def _inside(path: Path, root: Path) -> bool:
    resolved = path.resolve()
    return resolved == root or root in resolved.parents


def _atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    with tempfile.NamedTemporaryFile(
        dir=path.parent, prefix=f".{path.name}.", delete=False
    ) as handle:
        temporary = Path(handle.name)
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), 1
    ):
        if not line.strip():
            continue
        row = json.loads(line)
        if not isinstance(row, dict):
            raise TriageError(f"{path}:{line_number}: expected an object")
        rows.append(row)
    return rows


def _require_hash(value: Any, field: str) -> str:
    candidate = str(value)
    if not HEX64_RE.fullmatch(candidate):
        raise TriageError(f"Invalid or missing hash: {field}")
    return candidate


def _file_binding(spec: Mapping[str, Any], field: str) -> tuple[Path, str]:
    if not isinstance(spec, Mapping) or not spec.get("path"):
        raise TriageError(f"Missing file binding: {field}")
    path = _resolve(str(spec["path"]))
    expected = _require_hash(spec.get("file_sha256"), f"{field}.file_sha256")
    if not path.is_file():
        raise TriageError(f"Bound file is missing: {field}")
    if sha256_file(path) != expected:
        raise TriageError(f"Bound file hash changed: {field}")
    return path, expected


def load_config(path: Path = DEFAULT_CONFIG) -> dict[str, Any]:
    """Load a fail-closed configuration and verify every immutable binding."""
    config_path = path.resolve()
    raw = json.loads(config_path.read_text(encoding="utf-8"))
    if raw.get("protocol_version") != PROTOCOL_VERSION:
        raise TriageError("Wrong local NLI triage protocol")
    expected_pairs = int(raw.get("expected_pairs", 0))
    if expected_pairs <= 0:
        raise TriageError("expected_pairs must be positive")

    source_path, source_file_sha = _file_binding(raw.get("source_input", {}), "source_input")
    final_path, final_file_sha = _file_binding(raw.get("final_input", {}), "final_input")
    expected_records_sha = _require_hash(
        raw["final_input"].get("records_sha256"),
        "final_input.records_sha256",
    )

    model = raw.get("model")
    if not isinstance(model, Mapping):
        raise TriageError("Missing local model configuration")
    model_id = str(model.get("id", ""))
    revision = str(model.get("revision", ""))
    if not model_id or not revision:
        raise TriageError("Model ID and revision must be pinned")
    if model.get("local_files_only") is not True:
        raise TriageError("Local NLI triage forbids network model loading")
    if model.get("dtype") != "float32":
        raise TriageError("Local NLI triage is frozen to float32")
    if model.get("device_preference") != ["mps", "cuda", "cpu"]:
        raise TriageError("Device preference must be MPS, CUDA, then CPU")
    if int(model.get("batch_size", 0)) <= 0:
        raise TriageError("NLI batch_size must be positive")
    snapshot = _resolve(str(model.get("snapshot", "")))
    if not snapshot.is_dir() or snapshot.name != revision:
        raise TriageError("Pinned model snapshot is missing or has the wrong revision")
    for filename, hash_field in (
        ("config.json", "config_sha256"),
        ("model.safetensors", "weights_sha256"),
    ):
        expected = _require_hash(model.get(hash_field), f"model.{hash_field}")
        model_file = snapshot / filename
        if not model_file.is_file() or sha256_file(model_file) != expected:
            raise TriageError(f"Pinned model file changed: {filename}")
    tokenizer_files = model.get("tokenizer_files_sha256")
    if not isinstance(tokenizer_files, Mapping):
        raise TriageError("Every local tokenizer artifact must be hash-pinned")
    present_tokenizer_files = {
        name for name in TOKENIZER_CANDIDATE_FILES if (snapshot / name).is_file()
    }
    if set(str(name) for name in tokenizer_files) != present_tokenizer_files:
        raise TriageError("Pinned tokenizer artifact set changed")
    for filename in sorted(present_tokenizer_files):
        expected = _require_hash(
            tokenizer_files.get(filename),
            f"model.tokenizer_files_sha256.{filename}",
        )
        if sha256_file(snapshot / filename) != expected:
            raise TriageError(f"Pinned tokenizer file changed: {filename}")
    if tokenizer_files.get("tokenizer.json") != model.get("tokenizer_sha256"):
        raise TriageError("tokenizer.json hash aliases disagree")
    tokenizer_bundle_sha256 = canonical_sha256(dict(sorted(tokenizer_files.items())))
    chunking = raw.get("chunking")
    if not isinstance(chunking, Mapping):
        raise TriageError("Missing chunking configuration")
    chunk_tokens = int(chunking.get("target_wordpiece_tokens", 0))
    counterpart_selection = str(chunking.get("counterpart_selection", ""))
    max_length = int(model.get("max_length", 0))
    if not 32 <= chunk_tokens <= 240:
        raise TriageError("Chunk target must be between 32 and 240 tokens")
    if counterpart_selection != "all_chunk_cross_product":
        raise TriageError("This protocol requires the full chunk cross-product")
    if max_length < 2 * chunk_tokens + 4:
        raise TriageError("Model max_length cannot hold two full chunks")

    thresholds = raw.get("triage_thresholds")
    if not isinstance(thresholds, Mapping):
        raise TriageError("Missing triage thresholds")
    for field in ("minimum_best_entailment", "maximum_best_contradiction"):
        value = float(thresholds.get(field, -1.0))
        if not 0.0 <= value <= 1.0:
            raise TriageError(f"Invalid triage threshold: {field}")

    cache_path = _resolve(str(raw.get("cache_path", "")))
    private_output = _resolve(str(raw.get("private_output_path", "")))
    public_output = _resolve(str(raw.get("public_report_path", "")))
    if not _inside(cache_path, PRIVATE_ROOT) or not _inside(private_output, PRIVATE_ROOT):
        raise TriageError("Prediction cache and detailed output must remain private")
    if not _inside(public_output, REPORT_ROOT):
        raise TriageError("Aggregate report must remain under reports/")

    source_rows = _read_jsonl(source_path)
    final_payload = json.loads(final_path.read_text(encoding="utf-8"))
    records = final_payload.get("records") if isinstance(final_payload, dict) else None
    if not isinstance(records, list):
        raise TriageError("Final input has no records array")
    computed_records_sha = sha256_bytes(
        json.dumps(records, sort_keys=True).encode("utf-8")
    )
    if (
        final_payload.get("records_sha256") != expected_records_sha
        or computed_records_sha != expected_records_sha
    ):
        raise TriageError("Final records hash changed")
    if len(source_rows) != expected_pairs or len(records) != expected_pairs:
        raise TriageError("Bound inputs have the wrong pair count")

    expected_source_ids_sha = _require_hash(
        raw["source_input"].get("source_ids_sha256"),
        "source_input.source_ids_sha256",
    )
    actual_source_ids_sha = sha256_text(
        "".join(f"{row.get('source_id', '')}\n" for row in source_rows)
    )
    if actual_source_ids_sha != expected_source_ids_sha:
        raise TriageError("Source identity order changed")
    expected_response_hashes_sha = _require_hash(
        raw["source_input"].get("response_hashes_sha256"),
        "source_input.response_hashes_sha256",
    )
    actual_response_hashes_sha = sha256_text(
        "\n".join(str(row.get("original_response_sha256", "")) for row in source_rows)
    )
    if actual_response_hashes_sha != expected_response_hashes_sha:
        raise TriageError("Source response-hash order changed")

    seen: set[str] = set()
    for position, (source, record) in enumerate(zip(source_rows, records), 1):
        source_id = str(source.get("source_id", ""))
        if not source_id or source_id in seen:
            raise TriageError("Source identities must be unique")
        seen.add(source_id)
        original = source.get("original_response")
        if not isinstance(original, str) or sha256_text(original) != source.get(
            "original_response_sha256"
        ):
            raise TriageError(f"Source response hash mismatch at position {position}")
        if (
            not isinstance(record, Mapping)
            or record.get("source_id") != source_id
            or record.get("original_response_sha256")
            != source.get("original_response_sha256")
            or record.get("status") != "accepted"
        ):
            raise TriageError(f"Source/final record mismatch at position {position}")
        if record.get("stance_topology") not in {
            "early",
            "middle",
            "late",
            "distributed",
        }:
            raise TriageError(f"Invalid stance topology at position {position}")

    return {
        **raw,
        "config_path": config_path,
        "config_sha256": sha256_file(config_path),
        "source_path": source_path,
        "source_file_sha256": source_file_sha,
        "final_path": final_path,
        "final_file_sha256": final_file_sha,
        "records_sha256": expected_records_sha,
        "model_snapshot": snapshot,
        "tokenizer_bundle_sha256": tokenizer_bundle_sha256,
        "cache_path_resolved": cache_path,
        "private_output_path_resolved": private_output,
        "public_report_path_resolved": public_output,
        "source_rows": source_rows,
        "records": records,
    }


def strip_stance_markers(template: str, topology: str) -> tuple[str, int]:
    """Remove only standalone v3.7 markers and reject hidden/unknown markers."""
    if not isinstance(template, str) or not template.strip():
        raise TriageError("Shared template is empty")
    if topology not in {"early", "middle", "late", "distributed"}:
        raise TriageError("Invalid stance topology")
    markers = MARKER_LINE_RE.findall(template)
    expected_markers = Counter({"1": 1, "2": 1}) if topology == "distributed" else Counter({"1": 1})
    if Counter(markers) != expected_markers:
        raise TriageError("Unexpected stance-marker identity or count")
    stripped = MARKER_LINE_RE.sub("", template).strip()
    if not stripped or UNKNOWN_MARKER_RE.search(stripped):
        raise TriageError("Shared template contains an invalid stance marker")
    return stripped, len(markers)


def mask_fenced_code(text: str) -> tuple[str, dict[str, int]]:
    """Replace complete fenced blocks by stable placeholders before chunking.

    Exact code preservation is already enforced mechanically.  Masking keeps a
    protected block intact and prevents code tokens from dominating either the
    lexical matcher or the NLI model.  An unmatched opening fence conservatively
    protects the remainder of the response.
    """
    lines = text.splitlines(keepends=True)
    output: list[str] = []
    index = 0
    block_count = 0
    block_hashes: list[str] = []
    unmatched = 0
    while index < len(lines):
        opening = lines[index].rstrip("\r\n")
        match = FENCE_OPEN_RE.fullmatch(opening)
        if match is None:
            output.append(lines[index])
            index += 1
            continue
        fence = match.group("fence")
        fence_char = fence[0]
        closing = re.compile(rf"^[ \t]*{re.escape(fence_char)}{{{len(fence)},}}[ \t]*$")
        cursor = index + 1
        tail = match.group("tail")
        if re.search(rf"{re.escape(fence_char)}{{{len(fence)},}}[ \t]*$", tail):
            cursor = index
        else:
            while cursor < len(lines):
                if closing.fullmatch(lines[cursor].rstrip("\r\n")):
                    break
                cursor += 1
        if cursor >= len(lines):
            cursor = len(lines) - 1
            unmatched += 1
        block = "".join(lines[index : cursor + 1])
        block_hash = sha256_text(block)
        placeholder = f"[[PROTECTED_CODE_{block_hash[:16]}]]"
        suffix = "\n" if block.endswith(("\n", "\r")) else ""
        output.append(placeholder + suffix)
        block_count += 1
        block_hashes.append(block_hash)
        index = cursor + 1
    return "".join(output), {
        "fenced_code_block_count": block_count,
        "unmatched_fence_count": unmatched,
        "fenced_code_sha256": block_hashes,
    }


def _token_ids(tokenizer: Any, text: str) -> list[int]:
    encoded = tokenizer(text, add_special_tokens=False)
    ids = encoded["input_ids"] if isinstance(encoded, Mapping) else encoded.input_ids
    if ids and isinstance(ids[0], list):
        ids = ids[0]
    return [int(value) for value in ids]


def _split_long_atom(atom: str, tokenizer: Any, maximum: int) -> list[str]:
    """Split an oversized prose atom at tokenizer offsets, never by byte index."""
    try:
        encoded = tokenizer(
            atom,
            add_special_tokens=False,
            return_offsets_mapping=True,
        )
        offsets = encoded["offset_mapping"]
        if offsets and isinstance(offsets[0], list):
            offsets = offsets[0]
        parts = []
        for start in range(0, len(offsets), maximum):
            group = offsets[start : start + maximum]
            if not group:
                continue
            left = int(group[0][0])
            right = int(group[-1][1])
            piece = atom[left:right].strip()
            if piece:
                parts.append(piece)
        if parts:
            return parts
    except (KeyError, TypeError, ValueError, NotImplementedError):
        pass

    words = atom.split()
    parts: list[str] = []
    current: list[str] = []
    for word in words:
        candidate = " ".join([*current, word])
        if current and len(_token_ids(tokenizer, candidate)) > maximum:
            parts.append(" ".join(current))
            current = [word]
        else:
            current.append(word)
    if current:
        parts.append(" ".join(current))
    if any(len(_token_ids(tokenizer, part)) > maximum for part in parts):
        raise TriageError("Unable to split a prose atom below the token limit")
    return parts


def _prose_atoms(text: str) -> list[str]:
    atoms: list[str] = []
    for paragraph in re.split(r"\n\s*\n", text):
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        for line in paragraph.splitlines():
            line = line.strip()
            if not line:
                continue
            sentences = re.split(r"(?<=[.!?])\s+(?=\S)", line)
            atoms.extend(value.strip() for value in sentences if value.strip())
    return atoms


def chunk_text(text: str, tokenizer: Any, maximum: int) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """Create approximately ``maximum``-wordpiece chunks without truncation."""
    masked, code_stats = mask_fenced_code(text)
    atoms: list[str] = []
    forced_split_count = 0
    for atom in _prose_atoms(masked):
        if len(_token_ids(tokenizer, atom)) <= maximum:
            atoms.append(atom)
        else:
            pieces = _split_long_atom(atom, tokenizer, maximum)
            forced_split_count += max(0, len(pieces) - 1)
            atoms.extend(pieces)
    if not atoms:
        raise TriageError("Cannot build chunks from empty text")

    chunks: list[str] = []
    current: list[str] = []
    for atom in atoms:
        candidate = "\n".join([*current, atom])
        if current and len(_token_ids(tokenizer, candidate)) > maximum:
            chunks.append("\n".join(current))
            current = [atom]
        else:
            current.append(atom)
    if current:
        chunks.append("\n".join(current))

    result = []
    for index, value in enumerate(chunks):
        token_count = len(_token_ids(tokenizer, value))
        if token_count > maximum:
            raise TriageError("Chunk exceeds the frozen wordpiece budget")
        result.append(
            {
                "index": index,
                "text": value,
                "text_sha256": sha256_text(value),
                "token_count": token_count,
                "protected_code_placeholder_count": len(
                    CODE_PLACEHOLDER_RE.findall(value)
                ),
            }
        )
    return result, {**code_stats, "forced_prose_split_count": forced_split_count}


def _lexical_counter(text: str) -> Counter[str]:
    words = [
        word.casefold()
        for word in WORD_RE.findall(CODE_PLACEHOLDER_RE.sub(" ", text))
        if len(word) > 1
    ]
    return Counter(words)


def lexical_overlap(left: str, right: str) -> float:
    """Cosine overlap over case-folded word counts; code placeholders excluded."""
    a = _lexical_counter(left)
    b = _lexical_counter(right)
    if not a or not b:
        return 0.0
    numerator = sum(value * b.get(key, 0) for key, value in a.items())
    denominator = math.sqrt(sum(value * value for value in a.values())) * math.sqrt(
        sum(value * value for value in b.values())
    )
    return float(numerator / denominator) if denominator else 0.0


def _cache_key(config: Mapping[str, Any], premise: str, hypothesis: str) -> str:
    return _cache_key_from_hashes(
        config, sha256_text(premise), sha256_text(hypothesis)
    )


def _cache_key_from_hashes(
    config: Mapping[str, Any], premise_sha256: str, hypothesis_sha256: str
) -> str:
    model = config["model"]
    return canonical_sha256(
        {
            "model_id": model["id"],
            "model_revision": model["revision"],
            "model_config_sha256": model["config_sha256"],
            "model_weights_sha256": model["weights_sha256"],
            "tokenizer_sha256": model["tokenizer_sha256"],
            "tokenizer_bundle_sha256": config.get(
                "tokenizer_bundle_sha256",
                canonical_sha256(model.get("tokenizer_files_sha256", {})),
            ),
            "max_length": int(model["max_length"]),
            "premise_sha256": premise_sha256,
            "hypothesis_sha256": hypothesis_sha256,
        }
    )


def build_queries(
    source_chunks: Sequence[dict[str, Any]],
    template_chunks: Sequence[dict[str, Any]],
    config: Mapping[str, Any],
) -> list[dict[str, Any]]:
    """Compare the exhaustive chunk cross-product in both directions."""
    queries: list[dict[str, Any]] = []

    def add_direction(
        direction: str,
        premises: Sequence[dict[str, Any]],
        hypotheses: Sequence[dict[str, Any]],
    ) -> None:
        for hypothesis in hypotheses:
            denominator_h = max(1, len(hypotheses) - 1)
            hypothesis_position = int(hypothesis["index"]) / denominator_h
            candidates = []
            for premise in premises:
                denominator_p = max(1, len(premises) - 1)
                premise_position = int(premise["index"]) / denominator_p
                overlap = lexical_overlap(str(premise["text"]), str(hypothesis["text"]))
                candidates.append(
                    (
                        -overlap,
                        abs(premise_position - hypothesis_position),
                        int(premise["index"]),
                        premise,
                        overlap,
                    )
                )
            candidates.sort(key=lambda value: value[:3])
            for rank, (_, _, _, premise, overlap) in enumerate(
                candidates, 1
            ):
                premise_text = str(premise["text"])
                hypothesis_text = str(hypothesis["text"])
                queries.append(
                    {
                        "direction": direction,
                        "hypothesis_chunk_index": int(hypothesis["index"]),
                        "premise_chunk_index": int(premise["index"]),
                        "candidate_rank": rank,
                        "lexical_overlap": overlap,
                        "premise_text": premise_text,
                        "hypothesis_text": hypothesis_text,
                        "premise_sha256": premise["text_sha256"],
                        "hypothesis_sha256": hypothesis["text_sha256"],
                        "cache_key": _cache_key(
                            config, premise_text, hypothesis_text
                        ),
                    }
                )

    # Does the rewritten template retain each original chunk?
    add_direction("template_to_source", template_chunks, source_chunks)
    # Does the original support every chunk introduced by the template?
    add_direction("source_to_template", source_chunks, template_chunks)
    return queries


def _load_tokenizer(config: Mapping[str, Any]) -> Any:
    from transformers import AutoTokenizer

    return AutoTokenizer.from_pretrained(
        config["model_snapshot"], local_files_only=True
    )


def _pair_token_count(tokenizer: Any, premise: str, hypothesis: str) -> int:
    encoded = tokenizer(
        premise,
        hypothesis,
        add_special_tokens=True,
        truncation=False,
    )
    ids = encoded["input_ids"] if isinstance(encoded, Mapping) else encoded.input_ids
    if ids and isinstance(ids[0], list):
        ids = ids[0]
    return len(ids)


def prepare_plan(
    config: Mapping[str, Any], tokenizer: Any | None = None
) -> dict[str, Any]:
    """Build the exact inference plan without loading the NLI weights."""
    tokenizer = tokenizer or _load_tokenizer(config)
    items = []
    total_queries = 0
    maximum_pair_tokens = 0
    chunk_budget = int(config["chunking"]["target_wordpiece_tokens"])
    max_length = int(config["model"]["max_length"])
    for source, record in zip(config["source_rows"], config["records"]):
        neutral, marker_count = strip_stance_markers(
            str(record["shared_template"]), str(record["stance_topology"])
        )
        source_chunks, source_code = chunk_text(
            str(source["original_response"]), tokenizer, chunk_budget
        )
        template_chunks, template_code = chunk_text(neutral, tokenizer, chunk_budget)
        queries = build_queries(source_chunks, template_chunks, config)
        for query in queries:
            count = _pair_token_count(
                tokenizer,
                str(query["premise_text"]),
                str(query["hypothesis_text"]),
            )
            if count > max_length:
                raise TriageError(
                    "Chunk pair exceeds model max_length; truncation is forbidden"
                )
            query["pair_token_count"] = count
            maximum_pair_tokens = max(maximum_pair_tokens, count)
        total_queries += len(queries)
        items.append(
            {
                "source_id": source["source_id"],
                "dataset": source.get("dataset", "other"),
                "task": source.get("task", "other"),
                "original_response_sha256": source["original_response_sha256"],
                "neutral_template_sha256": sha256_text(neutral),
                "marker_count": marker_count,
                "source_chunks": source_chunks,
                "template_chunks": template_chunks,
                "source_code": source_code,
                "template_code": template_code,
                "queries": queries,
            }
        )
    return {
        "items": items,
        "pair_count": len(items),
        "judgment_count": total_queries,
        "maximum_pair_tokens": maximum_pair_tokens,
        "chunk_budget": chunk_budget,
        "no_truncation": True,
    }


def _empty_cache(config: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema": CACHE_SCHEMA,
        "model": {
            "id": config["model"]["id"],
            "revision": config["model"]["revision"],
            "config_sha256": config["model"]["config_sha256"],
            "tokenizer_sha256": config["model"]["tokenizer_sha256"],
            "tokenizer_bundle_sha256": config["tokenizer_bundle_sha256"],
            "tokenizer_files_sha256": dict(
                sorted(config["model"]["tokenizer_files_sha256"].items())
            ),
            "weights_sha256": config["model"]["weights_sha256"],
            "max_length": int(config["model"]["max_length"]),
        },
        "judgments": {},
    }


def load_cache(config: Mapping[str, Any]) -> dict[str, Any]:
    path = config["cache_path_resolved"]
    expected = _empty_cache(config)
    if not path.exists():
        return expected
    value = json.loads(path.read_text(encoding="utf-8"))
    if (
        not isinstance(value, dict)
        or value.get("schema") != CACHE_SCHEMA
        or value.get("model") != expected["model"]
        or not isinstance(value.get("judgments"), dict)
    ):
        raise TriageError("Prediction cache is stale or malformed")
    validated: dict[str, Any] = {}
    for key, raw_judgment in value["judgments"].items():
        if not isinstance(key, str) or not HEX64_RE.fullmatch(key):
            raise TriageError("Prediction cache contains an invalid key")
        if not isinstance(raw_judgment, Mapping):
            raise TriageError("Prediction cache contains a malformed judgment")
        premise_sha = _require_hash(
            raw_judgment.get("premise_sha256"), "cache.premise_sha256"
        )
        hypothesis_sha = _require_hash(
            raw_judgment.get("hypothesis_sha256"), "cache.hypothesis_sha256"
        )
        if _cache_key_from_hashes(config, premise_sha, hypothesis_sha) != key:
            raise TriageError("Prediction cache key does not match its text hashes")
        validated[key] = {
            "premise_sha256": premise_sha,
            "hypothesis_sha256": hypothesis_sha,
            **_validate_prediction(raw_judgment),
        }
    value["judgments"] = validated
    return value


def _validate_prediction(prediction: Mapping[str, Any]) -> dict[str, Any]:
    label = str(prediction.get("label", "")).casefold()
    probabilities = prediction.get("probabilities")
    expected = {"contradiction", "entailment", "neutral"}
    if label not in expected or not isinstance(probabilities, Mapping):
        raise TriageError("NLI predictor returned an invalid result")
    normalized = {key: float(probabilities.get(key, -1.0)) for key in expected}
    if any(not 0.0 <= value <= 1.0 for value in normalized.values()):
        raise TriageError("NLI predictor returned invalid probabilities")
    if abs(sum(normalized.values()) - 1.0) > 1e-3:
        raise TriageError("NLI probabilities do not sum to one")
    if normalized[label] != max(normalized.values()):
        raise TriageError("NLI label does not match the probability argmax")
    return {"label": label, "probabilities": dict(sorted(normalized.items()))}


class LocalNLIPredictor:
    """Local-only DeBERTa predictor with MPS -> CUDA -> CPU preference."""

    def __init__(self, config: Mapping[str, Any], tokenizer: Any):
        import torch
        from transformers import AutoModelForSequenceClassification

        self.torch = torch
        self.tokenizer = tokenizer
        if torch.backends.mps.is_available():
            self.device = torch.device("mps")
        elif torch.cuda.is_available():
            self.device = torch.device("cuda")
        else:
            self.device = torch.device("cpu")
        self.model = AutoModelForSequenceClassification.from_pretrained(
            config["model_snapshot"],
            local_files_only=True,
            dtype=torch.float32,
        )
        initial_cpu_fallback = False
        try:
            self.model = self.model.to(self.device)
        except (RuntimeError, NotImplementedError):
            if self.device.type != "mps":
                raise
            self.device = torch.device("cpu")
            self.model = self.model.to(device=self.device, dtype=torch.float32)
            initial_cpu_fallback = True
            if hasattr(torch.mps, "empty_cache"):
                torch.mps.empty_cache()
        self.model.eval()
        raw_labels = getattr(self.model.config, "id2label", {})
        self.labels = {
            int(index): str(label).casefold() for index, label in raw_labels.items()
        }
        if set(self.labels.values()) != {"contradiction", "entailment", "neutral"}:
            raise TriageError("Pinned NLI model has an unexpected label mapping")
        self.max_length = int(config["model"]["max_length"])
        self.runtime = {
            "device": str(self.device),
            "dtype": "float32",
            "cpu_fallback": initial_cpu_fallback,
        }

    def _predict(self, pairs: Sequence[tuple[str, str]]) -> list[dict[str, Any]]:
        encoded = self.tokenizer(
            [value[0] for value in pairs],
            [value[1] for value in pairs],
            padding=True,
            truncation=False,
            return_tensors="pt",
        )
        if int(encoded["input_ids"].shape[1]) > self.max_length:
            raise TriageError("NLI batch would truncate; refusing inference")
        encoded = encoded.to(self.device)
        with self.torch.inference_mode():
            logits = self.model(**encoded).logits.float()
            probabilities = self.torch.softmax(logits, dim=-1).cpu().tolist()
        output = []
        for row in probabilities:
            values = {self.labels[index]: float(value) for index, value in enumerate(row)}
            label = max(values, key=values.get)
            output.append({"label": label, "probabilities": values})
        return output

    def predict(self, pairs: Sequence[tuple[str, str]]) -> list[dict[str, Any]]:
        try:
            return self._predict(pairs)
        except (RuntimeError, NotImplementedError):
            if self.device.type != "mps":
                raise
            self.device = self.torch.device("cpu")
            self.model = self.model.to(device=self.device, dtype=self.torch.float32)
            self.runtime.update({"device": "cpu", "cpu_fallback": True})
            if hasattr(self.torch.mps, "empty_cache"):
                self.torch.mps.empty_cache()
            return self._predict(pairs)

    def close(self) -> None:
        del self.model
        if self.device.type == "mps" and hasattr(self.torch.mps, "empty_cache"):
            self.torch.mps.empty_cache()
        elif self.device.type == "cuda":
            self.torch.cuda.empty_cache()


def _summary(values: Sequence[float | int]) -> dict[str, float | int | None]:
    if not values:
        return {"count": 0, "minimum": None, "median": None, "mean": None, "maximum": None}
    ordered = sorted(float(value) for value in values)
    middle = len(ordered) // 2
    median = (
        ordered[middle]
        if len(ordered) % 2
        else (ordered[middle - 1] + ordered[middle]) / 2.0
    )
    return {
        "count": len(ordered),
        "minimum": round(ordered[0], 6),
        "median": round(median, 6),
        "mean": round(sum(ordered) / len(ordered), 6),
        "maximum": round(ordered[-1], 6),
    }


def _safe_runtime(predictor: Any | None) -> dict[str, Any]:
    """Whitelist public runtime fields; never forward arbitrary predictor data."""
    raw = getattr(predictor, "runtime", {}) if predictor is not None else {}
    device = str(raw.get("device", "cached"))
    dtype = str(raw.get("dtype", "cached"))
    fallback = raw.get("cpu_fallback", False)
    if device not in {"mps", "cuda", "cpu", "cached"}:
        raise TriageError("Invalid public runtime device")
    if dtype not in {"float32", "cached"}:
        raise TriageError("Invalid public runtime dtype")
    if not isinstance(fallback, bool):
        raise TriageError("Invalid public runtime fallback flag")
    return {"device": device, "dtype": dtype, "cpu_fallback": fallback}


def _assert_public_text_free(
    public: Mapping[str, Any], config: Mapping[str, Any]
) -> None:
    """Fail if any per-example identity or source/candidate text reaches public JSON."""
    serialized = json.dumps(public, ensure_ascii=False, sort_keys=True)
    sensitive: set[str] = set()
    identity_fields = {
        "source_id",
        "review_id",
        "production_slot",
        "pool_id",
        "conversation_hash",
    }
    text_fields = {
        "prompt",
        "original_response",
        "shared_template",
        "confident_response",
        "hedged_response",
    }
    for row in config["source_rows"]:
        for field in identity_fields | text_fields:
            value = row.get(field)
            if isinstance(value, str) and value:
                sensitive.add(value)
    for row in config["records"]:
        for field in identity_fields | text_fields:
            value = row.get(field)
            if isinstance(value, str) and value:
                sensitive.add(value)
    leaked = [value for value in sensitive if value in serialized]
    if leaked:
        raise TriageError("Public report contains per-example identity or text")


def _private_chunk(chunk: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "index": int(chunk["index"]),
        "text_sha256": chunk["text_sha256"],
        "token_count": int(chunk["token_count"]),
        "protected_code_placeholder_count": int(
            chunk["protected_code_placeholder_count"]
        ),
    }


def aggregate_item(
    item: Mapping[str, Any],
    judgments: Mapping[str, Any],
    thresholds: Mapping[str, Any],
) -> dict[str, Any]:
    query_rows = []
    for query in item["queries"]:
        prediction = judgments[query["cache_key"]]
        query_rows.append(
            {
                key: query[key]
                for key in (
                    "direction",
                    "hypothesis_chunk_index",
                    "premise_chunk_index",
                    "candidate_rank",
                    "lexical_overlap",
                    "premise_sha256",
                    "hypothesis_sha256",
                    "cache_key",
                    "pair_token_count",
                )
            }
            | prediction
        )

    direction_summaries = {}
    flags = []
    for direction in ("template_to_source", "source_to_template"):
        rows = [row for row in query_rows if row["direction"] == direction]
        by_hypothesis: dict[int, list[dict[str, Any]]] = {}
        for row in rows:
            by_hypothesis.setdefault(int(row["hypothesis_chunk_index"]), []).append(row)
        best_rows = []
        for candidates in by_hypothesis.values():
            best_rows.append(
                max(
                    candidates,
                    key=lambda row: (
                        float(row["probabilities"]["entailment"]),
                        -float(row["probabilities"]["contradiction"]),
                        float(row["lexical_overlap"]),
                        -int(row["candidate_rank"]),
                    ),
                )
            )
        entailments = [float(row["probabilities"]["entailment"]) for row in best_rows]
        contradictions = [
            float(row["probabilities"]["contradiction"]) for row in best_rows
        ]
        low = [
            row
            for row in best_rows
            if float(row["probabilities"]["entailment"])
            < float(thresholds["minimum_best_entailment"])
        ]
        contradictory = [
            row
            for row in best_rows
            if float(row["probabilities"]["contradiction"])
            > float(thresholds["maximum_best_contradiction"])
        ]
        if low:
            flags.append(f"{direction}:low_best_entailment")
        if contradictory:
            flags.append(f"{direction}:high_best_contradiction")
        direction_summaries[direction] = {
            "hypothesis_chunk_count": len(best_rows),
            "low_best_entailment_chunk_count": len(low),
            "high_best_contradiction_chunk_count": len(contradictory),
            "best_entailment": _summary(entailments),
            "best_contradiction": _summary(contradictions),
        }

    if Counter(item["source_code"]["fenced_code_sha256"]) != Counter(
        item["template_code"]["fenced_code_sha256"]
    ):
        flags.append("fenced_code_exact_content_mismatch")
    if item["source_code"]["unmatched_fence_count"] or item["template_code"][
        "unmatched_fence_count"
    ]:
        flags.append("unmatched_fence_requires_review")

    return {
        "source_id": item["source_id"],
        "dataset": item["dataset"],
        "task": item["task"],
        "original_response_sha256": item["original_response_sha256"],
        "neutral_template_sha256": item["neutral_template_sha256"],
        "marker_count": item["marker_count"],
        "source_chunks": [_private_chunk(value) for value in item["source_chunks"]],
        "template_chunks": [
            _private_chunk(value) for value in item["template_chunks"]
        ],
        "source_code": item["source_code"],
        "template_code": item["template_code"],
        "judgments": query_rows,
        "direction_summaries": direction_summaries,
        "triage_flags": sorted(set(flags)),
        "triage_flagged": bool(flags),
        "semantic_certification": False,
    }


def _aggregate_public(
    config: Mapping[str, Any],
    plan: Mapping[str, Any],
    records: Sequence[Mapping[str, Any]],
    *,
    cache_hits: int,
    new_judgments: int,
    runtime: Mapping[str, Any],
) -> dict[str, Any]:
    flagged = [record for record in records if record["triage_flagged"]]
    flag_counts = Counter(
        flag for record in records for flag in record["triage_flags"]
    )
    source_chunk_counts = [len(record["source_chunks"]) for record in records]
    template_chunk_counts = [len(record["template_chunks"]) for record in records]
    by_dataset: dict[str, Counter[str]] = {}
    by_task: dict[str, Counter[str]] = {}
    for record in records:
        status = "flagged" if record["triage_flagged"] else "not_flagged"
        by_dataset.setdefault(str(record["dataset"]), Counter())[status] += 1
        by_task.setdefault(str(record["task"]), Counter())[status] += 1

    return {
        "schema": PUBLIC_SCHEMA,
        "protocol_version": PROTOCOL_VERSION,
        "contains_source_or_response_text": False,
        "contains_per_example_results": False,
        "status": "complete",
        "purpose": "independent_local_semantic_triage_for_blind_human_review",
        "semantic_certification": False,
        "training_data_validated": False,
        "authorizes_probe_scoring": False,
        "authorizes_sdt_training": False,
        "decision": "triage_complete_human_blind_review_still_required",
        "limitations": [
            "MNLI probabilities are screening signals, not semantic-equivalence certificates.",
            "This audit compares exact fenced-code hashes, then masks those blocks before NLI; construction validation covers additional protected code spans.",
            "Chunking can miss claims that require evidence across chunk boundaries.",
            "Naturalness, confidence ordering, and global cue scope require blind human review.",
        ],
        "bindings": {
            "config_sha256": config["config_sha256"],
            "source_file_sha256": config["source_file_sha256"],
            "source_ids_sha256": config["source_input"]["source_ids_sha256"],
            "source_response_hashes_sha256": config["source_input"][
                "response_hashes_sha256"
            ],
            "final_file_sha256": config["final_file_sha256"],
            "records_sha256": config["records_sha256"],
            "model_id": config["model"]["id"],
            "model_revision": config["model"]["revision"],
            "model_config_sha256": config["model"]["config_sha256"],
            "tokenizer_sha256": config["model"]["tokenizer_sha256"],
            "tokenizer_files_sha256": dict(
                sorted(config["model"]["tokenizer_files_sha256"].items())
            ),
            "tokenizer_bundle_sha256": config["tokenizer_bundle_sha256"],
            "model_weights_sha256": config["model"]["weights_sha256"],
        },
        "method": {
            "comparison": "original_response_vs_marker_stripped_shared_template",
            "directions": ["template_to_source", "source_to_template"],
            "target_wordpiece_tokens": plan["chunk_budget"],
            "counterpart_selection": config["chunking"][
                "counterpart_selection"
            ],
            "lexical_overlap_role": "diagnostic_and_deterministic_ranking_only",
            "maximum_observed_pair_tokens": plan["maximum_pair_tokens"],
            "model_max_length": int(config["model"]["max_length"]),
            "truncation": False,
            "thresholds": config["triage_thresholds"],
        },
        "counts": {
            "pair_count": len(records),
            "flagged_pair_count": len(flagged),
            "not_flagged_pair_count": len(records) - len(flagged),
            "judgment_count": int(plan["judgment_count"]),
            "cache_hits": cache_hits,
            "new_judgments": new_judgments,
            "flag_counts": dict(sorted(flag_counts.items())),
            "by_dataset": {
                key: dict(sorted(value.items())) for key, value in sorted(by_dataset.items())
            },
            "by_task": {
                key: dict(sorted(value.items())) for key, value in sorted(by_task.items())
            },
        },
        "chunk_counts": {
            "source": _summary(source_chunk_counts),
            "template": _summary(template_chunk_counts),
        },
        "runtime": dict(runtime),
    }


def run_triage(
    config_path: Path = DEFAULT_CONFIG,
    *,
    tokenizer: Any | None = None,
    predictor: Any | None = None,
    nonproduction_test_mode: bool = False,
) -> dict[str, Any]:
    """Execute cached local inference and write private/public artifacts."""
    injected = tokenizer is not None or predictor is not None
    if injected and not nonproduction_test_mode:
        raise TriageError(
            "Injected tokenizer/predictor requires nonproduction_test_mode"
        )
    if nonproduction_test_mode and (tokenizer is None or predictor is None):
        raise TriageError(
            "Nonproduction execution requires both tokenizer and predictor doubles"
        )
    config = load_config(config_path)
    tokenizer = tokenizer or _load_tokenizer(config)
    plan = prepare_plan(config, tokenizer)
    cache = _empty_cache(config) if nonproduction_test_mode else load_cache(config)
    required: dict[str, dict[str, Any]] = {}
    for item in plan["items"]:
        for query in item["queries"]:
            required.setdefault(str(query["cache_key"]), query)
    for key, query in required.items():
        if key not in cache["judgments"]:
            continue
        cached = cache["judgments"][key]
        if (
            cached["premise_sha256"] != query["premise_sha256"]
            or cached["hypothesis_sha256"] != query["hypothesis_sha256"]
            or _cache_key(config, query["premise_text"], query["hypothesis_text"])
            != key
        ):
            raise TriageError("Cached judgment does not match the required query")
    cached_before = sum(key in cache["judgments"] for key in required)
    missing = [key for key in required if key not in cache["judgments"]]

    owns_predictor = predictor is None
    if missing and predictor is None:
        predictor = LocalNLIPredictor(config, tokenizer)
    batch_size = int(config["model"]["batch_size"])
    for start in range(0, len(missing), batch_size):
        keys = missing[start : start + batch_size]
        pairs = [
            (
                str(required[key]["premise_text"]),
                str(required[key]["hypothesis_text"]),
            )
            for key in keys
        ]
        predictions = predictor.predict(pairs)
        if len(predictions) != len(keys):
            raise TriageError("NLI predictor returned the wrong batch size")
        for key, prediction in zip(keys, predictions):
            query = required[key]
            cache["judgments"][key] = {
                "premise_sha256": query["premise_sha256"],
                "hypothesis_sha256": query["hypothesis_sha256"],
                **_validate_prediction(prediction),
            }
        if not nonproduction_test_mode:
            _atomic_json(config["cache_path_resolved"], cache)

    runtime = _safe_runtime(predictor)
    if owns_predictor and predictor is not None:
        predictor.close()

    private_records = [
        aggregate_item(item, cache["judgments"], config["triage_thresholds"])
        for item in plan["items"]
    ]
    public = _aggregate_public(
        config,
        plan,
        private_records,
        cache_hits=cached_before,
        new_judgments=len(missing),
        runtime=runtime,
    )
    private = {
        "schema": PRIVATE_SCHEMA,
        "protocol_version": PROTOCOL_VERSION,
        "status": "complete",
        "semantic_certification": False,
        "public_report_sha256": canonical_sha256(public),
        "bindings": public["bindings"],
        "method": public["method"],
        "records": private_records,
        "aggregate": public["counts"],
    }
    _assert_public_text_free(public, config)
    if not nonproduction_test_mode:
        _atomic_json(config["private_output_path_resolved"], private)
        _atomic_json(config["public_report_path_resolved"], public)
    return public


def plan_summary(
    config_path: Path = DEFAULT_CONFIG,
    *,
    tokenizer: Any | None = None,
    nonproduction_test_mode: bool = False,
) -> dict[str, Any]:
    """Return a text-free no-inference plan for operator inspection."""
    if tokenizer is not None and not nonproduction_test_mode:
        raise TriageError("Injected tokenizer requires nonproduction_test_mode")
    config = load_config(config_path)
    plan = prepare_plan(config, tokenizer)
    cache = _empty_cache(config) if nonproduction_test_mode else load_cache(config)
    keys = {
        str(query["cache_key"])
        for item in plan["items"]
        for query in item["queries"]
    }
    hits = sum(key in cache["judgments"] for key in keys)
    return {
        "protocol_version": PROTOCOL_VERSION,
        "mode": "plan_only_no_model_inference",
        "contains_source_or_response_text": False,
        "pair_count": plan["pair_count"],
        "judgment_count": len(keys),
        "cache_hits": hits,
        "new_judgments_if_run": len(keys) - hits,
        "chunk_budget": plan["chunk_budget"],
        "maximum_pair_tokens": plan["maximum_pair_tokens"],
        "model_max_length": int(config["model"]["max_length"]),
        "no_truncation": plan["no_truncation"],
        "semantic_certification": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument(
        "--run",
        action="store_true",
        help="Explicitly load the local NLI weights and execute missing judgments.",
    )
    args = parser.parse_args()
    result = run_triage(args.config) if args.run else plan_summary(args.config)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
