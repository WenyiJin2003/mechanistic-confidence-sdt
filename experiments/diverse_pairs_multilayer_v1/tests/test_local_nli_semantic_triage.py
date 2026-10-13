from __future__ import annotations

import json
import re
import sys
import types
from pathlib import Path
from typing import Any

import pytest

from experiments.diverse_pairs_multilayer_v1.src import (
    local_nli_semantic_triage as triage,
)


class FakeTokenizer:
    """Small offset-aware tokenizer stand-in; no model files are loaded."""

    @staticmethod
    def _spans(text: str) -> list[tuple[int, int]]:
        return [match.span() for match in re.finditer(r"\S+", text)]

    def __call__(
        self,
        text: str,
        text_pair: str | None = None,
        *,
        add_special_tokens: bool = True,
        return_offsets_mapping: bool = False,
        **_: Any,
    ) -> dict[str, Any]:
        spans = self._spans(text)
        ids = list(range(10, 10 + len(spans)))
        if text_pair is not None:
            pair_ids = list(range(1000, 1000 + len(self._spans(text_pair))))
            ids = ([1] if add_special_tokens else []) + ids + [2] + pair_ids
            if add_special_tokens:
                ids.append(3)
        elif add_special_tokens:
            ids = [1, *ids, 2]
        value: dict[str, Any] = {"input_ids": ids}
        if return_offsets_mapping:
            value["offset_mapping"] = spans
        return value


class FakePredictor:
    def __init__(self, entailment: float = 0.9, contradiction: float = 0.03):
        self.entailment = entailment
        self.contradiction = contradiction
        self.calls: list[list[tuple[str, str]]] = []
        self.runtime = {
            "device": "cpu",
            "dtype": "float32",
            "cpu_fallback": False,
            "untrusted_debug_text": "Original answer 0 must never reach public output",
        }

    def predict(self, pairs: list[tuple[str, str]]) -> list[dict[str, Any]]:
        self.calls.append(list(pairs))
        neutral = 1.0 - self.entailment - self.contradiction
        return [
            {
                "label": "entailment",
                "probabilities": {
                    "contradiction": self.contradiction,
                    "entailment": self.entailment,
                    "neutral": neutral,
                },
            }
            for _ in pairs
        ]


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def _fixture(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> tuple[Path, Path]:
    base = tmp_path / "experiment"
    private = base / "private_data"
    reports = base / "reports"
    monkeypatch.setattr(triage, "BASE", base)
    monkeypatch.setattr(triage, "PRIVATE_ROOT", private.resolve())
    monkeypatch.setattr(triage, "REPORT_ROOT", reports.resolve())

    source_path = private / "source.jsonl"
    final_path = private / "final.json"
    source_rows = []
    records = []
    for index in range(2):
        original = (
            f"Original answer {index} gives the same central claim and supporting detail. "
            "It preserves the stated condition."
        )
        source_id = f"source-{index}"
        original_hash = triage.sha256_text(original)
        source_rows.append(
            {
                "source_id": source_id,
                "review_id": f"review-secret-{index}",
                "dataset": "synthetic",
                "task": "factual_explanation",
                "original_response": original,
                "original_response_sha256": original_hash,
            }
        )
        records.append(
            {
                "source_id": source_id,
                "original_response_sha256": original_hash,
                "status": "accepted",
                "stance_topology": "early",
                "shared_template": (
                    "<STANCE_1>\n"
                    f"The original answer {index} states the same central claim with supporting detail. "
                    "The stated condition remains present."
                ),
            }
        )
    _write_jsonl(source_path, source_rows)
    records_sha = triage.sha256_bytes(
        json.dumps(records, sort_keys=True).encode("utf-8")
    )
    _write_json(final_path, {"records": records, "records_sha256": records_sha})

    revision = "a" * 40
    snapshot = tmp_path / "model" / revision
    snapshot.mkdir(parents=True)
    _write_json(
        snapshot / "config.json",
        {
            "id2label": {
                "0": "contradiction",
                "1": "entailment",
                "2": "neutral",
            }
        },
    )
    _write_json(snapshot / "tokenizer.json", {"fake": True})
    _write_json(snapshot / "tokenizer_config.json", {"fake": True})
    _write_json(snapshot / "special_tokens_map.json", {"fake": True})
    _write_json(snapshot / "added_tokens.json", {"fake": True})
    (snapshot / "spm.model").write_bytes(b"fake-sentencepiece")
    (snapshot / "model.safetensors").write_bytes(b"fake-weights")
    tokenizer_files = {
        name: triage.sha256_file(snapshot / name)
        for name in (
            "added_tokens.json",
            "special_tokens_map.json",
            "spm.model",
            "tokenizer.json",
            "tokenizer_config.json",
        )
    }

    config = {
        "protocol_version": triage.PROTOCOL_VERSION,
        "expected_pairs": 2,
        "source_input": {
            "path": str(source_path),
            "file_sha256": triage.sha256_file(source_path),
            "source_ids_sha256": triage.sha256_text(
                "".join(f"{row['source_id']}\n" for row in source_rows)
            ),
            "response_hashes_sha256": triage.sha256_text(
                "\n".join(row["original_response_sha256"] for row in source_rows)
            ),
        },
        "final_input": {
            "path": str(final_path),
            "file_sha256": triage.sha256_file(final_path),
            "records_sha256": records_sha,
        },
        "model": {
            "id": "test/nli",
            "revision": revision,
            "snapshot": str(snapshot),
            "config_sha256": triage.sha256_file(snapshot / "config.json"),
            "tokenizer_sha256": triage.sha256_file(snapshot / "tokenizer.json"),
            "tokenizer_files_sha256": tokenizer_files,
            "weights_sha256": triage.sha256_file(snapshot / "model.safetensors"),
            "max_length": 80,
            "batch_size": 3,
            "local_files_only": True,
            "device_preference": ["mps", "cuda", "cpu"],
            "dtype": "float32",
        },
        "chunking": {
            "target_wordpiece_tokens": 32,
            "counterpart_selection": "all_chunk_cross_product",
            "lexical_overlap": "word_count_cosine",
        },
        "triage_thresholds": {
            "minimum_best_entailment": 0.5,
            "maximum_best_contradiction": 0.5,
        },
        "cache_path": str(private / "audit" / "cache.json"),
        "private_output_path": str(private / "audit" / "details.json"),
        "public_report_path": str(reports / "aggregate.json"),
    }
    config_path = base / "configs" / "triage.json"
    _write_json(config_path, config)
    return config_path, base


def test_load_config_binds_source_final_records_and_model(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config_path, _ = _fixture(tmp_path, monkeypatch)
    config = triage.load_config(config_path)
    assert len(config["source_rows"]) == 2
    assert len(config["records"]) == 2
    assert config["records_sha256"] == config["final_input"]["records_sha256"]

    final_path = Path(config["final_input"]["path"])
    final_path.write_text(final_path.read_text() + " ", encoding="utf-8")
    with pytest.raises(triage.TriageError, match="Bound file hash changed"):
        triage.load_config(config_path)


def test_marker_stripping_is_standalone_and_fail_closed() -> None:
    text, count = triage.strip_stance_markers(
        "First claim.\n<STANCE_1>\nSecond claim.\n<STANCE_2>\n",
        "distributed",
    )
    assert count == 2
    assert "STANCE" not in text
    assert "First claim" in text and "Second claim" in text

    with pytest.raises(triage.TriageError, match="marker identity or count"):
        triage.strip_stance_markers("<STANCE_1>\nOnly one.", "distributed")
    with pytest.raises(triage.TriageError, match="marker"):
        triage.strip_stance_markers("Inline <STANCE_1> marker.", "early")
    with pytest.raises(triage.TriageError, match="marker identity or count"):
        triage.strip_stance_markers(
            "<STANCE_1>\nFirst.\n<STANCE_1>\nSecond.", "distributed"
        )
    with pytest.raises(triage.TriageError, match="marker identity or count"):
        triage.strip_stance_markers(
            "<STANCE_1>\nFirst.\n<STANCE_2>\nSecond.\n<STANCE_2>\n",
            "distributed",
        )


def test_chunking_masks_fenced_code_and_never_exceeds_budget() -> None:
    code = " ".join(f"token_{index}" for index in range(200))
    text = f"Opening explanation.\n\n```python\n{code}\n```\n\nClosing explanation."
    chunks, stats = triage.chunk_text(text, FakeTokenizer(), maximum=12)
    assert stats["fenced_code_block_count"] == 1
    assert stats["unmatched_fence_count"] == 0
    assert all(chunk["token_count"] <= 12 for chunk in chunks)
    joined = "\n".join(str(chunk["text"]) for chunk in chunks)
    assert "token_199" not in joined
    assert "PROTECTED_CODE_" in joined


def test_exact_fenced_code_hash_mismatch_is_flagged() -> None:
    item = {
        "source_id": "private-source",
        "dataset": "synthetic",
        "task": "programming",
        "original_response_sha256": "1" * 64,
        "neutral_template_sha256": "2" * 64,
        "marker_count": 1,
        "source_chunks": [],
        "template_chunks": [],
        "source_code": {
            "fenced_code_block_count": 1,
            "unmatched_fence_count": 0,
            "fenced_code_sha256": ["a" * 64],
            "forced_prose_split_count": 0,
        },
        "template_code": {
            "fenced_code_block_count": 1,
            "unmatched_fence_count": 0,
            "fenced_code_sha256": ["b" * 64],
            "forced_prose_split_count": 0,
        },
        "queries": [],
    }
    result = triage.aggregate_item(
        item,
        {},
        {
            "minimum_best_entailment": 0.5,
            "maximum_best_contradiction": 0.5,
        },
    )
    assert "fenced_code_exact_content_mismatch" in result["triage_flags"]


def test_full_cross_product_queries_are_bidirectional_and_revision_bound() -> None:
    config = {
        "model": {
            "id": "test/nli",
            "revision": "revision-a",
            "config_sha256": "1" * 64,
            "tokenizer_sha256": "2" * 64,
            "tokenizer_files_sha256": {"tokenizer.json": "2" * 64},
            "weights_sha256": "3" * 64,
            "max_length": 512,
        },
        "chunking": {"counterpart_selection": "all_chunk_cross_product"},
    }
    source = [
        {"index": 0, "text": "alpha common", "text_sha256": triage.sha256_text("alpha common")},
        {"index": 1, "text": "beta common", "text_sha256": triage.sha256_text("beta common")},
        {"index": 2, "text": "gamma common", "text_sha256": triage.sha256_text("gamma common")},
    ]
    template = [
        {"index": 0, "text": "alpha shared", "text_sha256": triage.sha256_text("alpha shared")},
        {"index": 1, "text": "beta shared", "text_sha256": triage.sha256_text("beta shared")},
        {"index": 2, "text": "gamma shared", "text_sha256": triage.sha256_text("gamma shared")},
    ]
    queries = triage.build_queries(source, template, config)
    assert len(queries) == 18
    assert {query["direction"] for query in queries} == {
        "template_to_source",
        "source_to_template",
    }
    assert {query["candidate_rank"] for query in queries} == {1, 2, 3}
    old_key = queries[0]["cache_key"]
    config["model"]["revision"] = "revision-b"
    assert triage.build_queries(source, template, config)[0]["cache_key"] != old_key


def test_nonproduction_doubles_return_text_free_report_but_never_write(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config_path, base = _fixture(tmp_path, monkeypatch)
    tokenizer = FakeTokenizer()
    first_predictor = FakePredictor()
    first = triage.run_triage(
        config_path,
        tokenizer=tokenizer,
        predictor=first_predictor,
        nonproduction_test_mode=True,
    )
    assert first["semantic_certification"] is False
    assert first["training_data_validated"] is False
    assert first["counts"]["pair_count"] == 2
    assert first["counts"]["new_judgments"] > 0
    assert sum(len(batch) for batch in first_predictor.calls) == first["counts"][
        "new_judgments"
    ]
    assert first["method"]["truncation"] is False
    assert first["authorizes_probe_scoring"] is False
    assert first["authorizes_sdt_training"] is False
    assert set(first["runtime"]) == {"device", "dtype", "cpu_fallback"}

    public_path = base / "reports" / "aggregate.json"
    private_path = base / "private_data" / "audit" / "details.json"
    cache_path = base / "private_data" / "audit" / "cache.json"
    assert not public_path.exists()
    assert not private_path.exists()
    assert not cache_path.exists()
    public_text = json.dumps(first, ensure_ascii=False)
    for forbidden in (
        "Original answer 0",
        "Original answer 1",
        "source-0",
        "source-1",
        "review-secret-0",
        "review-secret-1",
        "untrusted_debug_text",
    ):
        assert forbidden not in public_text

    with pytest.raises(triage.TriageError, match="nonproduction_test_mode"):
        triage.run_triage(
            config_path, tokenizer=tokenizer, predictor=FakePredictor()
        )


def test_tampered_cached_hash_key_or_prediction_fails_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config_path, base = _fixture(tmp_path, monkeypatch)
    config = triage.load_config(config_path)
    cache_path = base / "private_data" / "audit" / "cache.json"
    cache = triage._empty_cache(config)
    premise = "frozen premise"
    hypothesis = "frozen hypothesis"
    key = triage._cache_key(config, premise, hypothesis)
    cache["judgments"][key] = {
        "premise_sha256": triage.sha256_text(premise),
        "hypothesis_sha256": triage.sha256_text(hypothesis),
        "label": "entailment",
        "probabilities": {
            "contradiction": 0.03,
            "entailment": 0.9,
            "neutral": 0.07,
        },
    }
    _write_json(cache_path, cache)
    assert triage.load_cache(config)["judgments"][key]["label"] == "entailment"

    bad_hash = json.loads(json.dumps(cache))
    bad_hash["judgments"][key]["premise_sha256"] = "f" * 64
    _write_json(cache_path, bad_hash)
    with pytest.raises(triage.TriageError, match="cache key"):
        triage.load_cache(config)

    bad_probability = json.loads(json.dumps(cache))
    bad_probability["judgments"][key]["probabilities"]["entailment"] = 2.0
    _write_json(cache_path, bad_probability)
    with pytest.raises(triage.TriageError, match="invalid probabilities"):
        triage.load_cache(config)

    bad_argmax = json.loads(json.dumps(cache))
    bad_argmax["judgments"][key]["label"] = "neutral"
    _write_json(cache_path, bad_argmax)
    with pytest.raises(triage.TriageError, match="probability argmax"):
        triage.load_cache(config)


def test_plan_summary_never_writes_outputs_or_loads_predictor(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config_path, base = _fixture(tmp_path, monkeypatch)
    summary = triage.plan_summary(
        config_path,
        tokenizer=FakeTokenizer(),
        nonproduction_test_mode=True,
    )
    assert summary["mode"] == "plan_only_no_model_inference"
    assert summary["no_truncation"] is True
    assert summary["pair_count"] == 2
    assert summary["new_judgments_if_run"] == summary["judgment_count"]
    assert not (base / "reports" / "aggregate.json").exists()
    assert not (base / "private_data" / "audit" / "cache.json").exists()


def test_initial_mps_model_transfer_falls_back_to_cpu(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class Device:
        def __init__(self, name: str):
            self.type = name

        def __str__(self) -> str:
            return self.type

    class FakeModel:
        def __init__(self):
            self.config = types.SimpleNamespace(
                id2label={0: "contradiction", 1: "entailment", 2: "neutral"}
            )
            self.transfers: list[str] = []

        def to(self, device: Device | None = None, **_: Any) -> "FakeModel":
            assert device is not None
            self.transfers.append(device.type)
            if device.type == "mps":
                raise RuntimeError("simulated MPS transfer failure")
            return self

        def eval(self) -> None:
            return None

    model = FakeModel()
    fake_torch = types.SimpleNamespace(
        float32="float32",
        device=lambda name: Device(name),
        backends=types.SimpleNamespace(
            mps=types.SimpleNamespace(is_available=lambda: True)
        ),
        cuda=types.SimpleNamespace(is_available=lambda: False, empty_cache=lambda: None),
        mps=types.SimpleNamespace(empty_cache=lambda: None),
    )
    fake_transformers = types.SimpleNamespace(
        AutoModelForSequenceClassification=types.SimpleNamespace(
            from_pretrained=lambda *args, **kwargs: model
        )
    )
    monkeypatch.setitem(sys.modules, "torch", fake_torch)
    monkeypatch.setitem(sys.modules, "transformers", fake_transformers)
    predictor = triage.LocalNLIPredictor(
        {
            "model_snapshot": Path("/unused/local/snapshot"),
            "model": {"max_length": 512},
        },
        FakeTokenizer(),
    )
    assert model.transfers == ["mps", "cpu"]
    assert predictor.runtime == {
        "device": "cpu",
        "dtype": "float32",
        "cpu_fallback": True,
    }
