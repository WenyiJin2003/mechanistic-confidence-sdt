"""Mocked engineering checks: no language-model inference or real writes."""
from copy import deepcopy
import importlib
from types import SimpleNamespace

import numpy as np
import pytest

from confidence_pilot.analyze_pairs import analyze_pairs
from confidence_pilot.common import load_config, read_jsonl
from confidence_pilot import transfer_run_v2 as transfer


def _legacy_catalog():
    rows = []
    for index in range(74):
        for family in ("A", "B", "C"):
            for correctness in ("correct", "incorrect"):
                prefix = f"old-{index:02d}-{family}-{correctness}"
                for certainty in ("confident", "hedged"):
                    other = "hedged" if certainty == "confident" else "confident"
                    style = "strong assertion" if certainty == "confident" else "soft reservation"
                    text = f"The answer is {index} with {style} for {correctness} in {family}."
                    rows.append({"variant_id": f"{prefix}-{certainty}",
                        "paired_variant_id": f"{prefix}-{other}", "source_id": f"old-{index:02d}",
                        "split": "train" if index < 72 else "test",
                        "domain": ("factual_qa", "arithmetic", "academic")[index % 3],
                        "correctness": correctness, "certainty": certainty,
                        "rewrite_family": family, "response_text": text,
                        "token_count": 14 if certainty == "confident" else 16,
                        "char_count": len(text),
                        "sequence_nll": 3 + index / 20 + (0 if certainty == "confident" else 2),
                        "mean_token_nll": .2 + index / 200 + (0 if certainty == "confident" else .3)})
    hidden = np.zeros((len(rows), 2, 4, 1536), dtype=np.float32)
    for position, row in enumerate(rows):
        index = int(row["source_id"].split("-")[1])
        sign = 1 if row["certainty"] == "confident" else -1
        family_shift = 100 if row["rewrite_family"] == "C" else 0
        hidden[position, :, :3, 0] = sign * (1 + index / 100 + family_shift)
        hidden[position, :, :3, 1] = sign * ((index % 5 - 2) / 10)
        hidden[position, :, :3, 2] = 2 if row["correctness"] == "correct" else -2
    # Independent source-first expectation, using the stored float32 states.
    differences = []
    for source in sorted({row["source_id"] for row in rows if row["split"] == "train"}):
        selected = [i for i, row in enumerate(rows) if row["source_id"] == source
                    and row["rewrite_family"] in {"A", "B"}]
        positive = hidden[[i for i in selected if rows[i]["certainty"] == "confident"], 0, 0].astype(float)
        negative = hidden[[i for i in selected if rows[i]["certainty"] == "hedged"], 0, 0].astype(float)
        differences.append((positive - negative).mean(axis=0))
    differences = np.stack(differences)
    direction = differences.mean(axis=0)
    direction /= np.linalg.norm(direction)
    return rows, hidden, differences, {"layer14_boundary": direction}


class _Archive:
    def __init__(self, arrays):
        self.arrays = arrays
        self.files = list(arrays)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def __getitem__(self, name):
        return self.arrays[name]


@pytest.fixture
def frozen_setup(monkeypatch):
    config = load_config("configs/paired_confidence_transfer_v2.yaml")
    config["analysis"]["null_repetitions"] = 6
    config["analysis"]["random_directions"] = 8
    old_rows, hidden, differences, directions = _legacy_catalog()
    state = {"rows": old_rows, "hidden": hidden, "differences": differences,
             "directions": directions, "npz": {}, "json": {}, "models": []}
    monkeypatch.setattr(transfer, "verify_frozen_inputs", lambda *args, **kwargs: None)
    monkeypatch.setattr(transfer, "read_jsonl", lambda path: state["rows"])

    def archive(path):
        if str(path).endswith("hidden_states.npz"):
            return _Archive({"hidden_states": state["hidden"],
                             "variant_ids": np.asarray(state.get("variant_ids",
                                 [row["variant_id"] for row in state["rows"]]))})
        return _Archive(state["directions"])

    monkeypatch.setattr(transfer.np, "load", archive)
    monkeypatch.setattr(transfer, "write_npz", lambda path, **arrays:
        state["npz"].__setitem__(path.name, {key: np.array(value, copy=True) for key, value in arrays.items()}))
    monkeypatch.setattr(transfer, "write_json", lambda path, value: state["json"].__setitem__(path.name, deepcopy(value)))
    make_pipeline = transfer.make_pipeline

    def capture_pipeline(*steps):
        model = make_pipeline(*steps)
        state["models"].append(model)
        return model

    monkeypatch.setattr(transfer, "make_pipeline", capture_pipeline)
    return config, state


def _new_rows():
    return [{"source_id": "new-world-1", "response_text": "The material for a new object is cork.",
             "certainty": "neutral", "split": "test", "sequence_nll": 13., "mean_token_nll": .9},
            {"source_id": "new-world-2", "response_text": "Perhaps the material for another object is steel.",
             "certainty": "hedged", "split": "test", "sequence_nll": 18., "mean_token_nll": 1.2}]


def test_frozen_word_and_numeric_scores_reproduce_v1_baselines(frozen_setup):
    config, state = frozen_setup
    augmented, controls = transfer.prepare_frozen_controls(_new_rows(), config)
    legacy = analyze_pairs(state["rows"], state["hidden"], {"phase": "b", "analysis": {
        "seed": config["analysis"]["null_seed"], "bootstrap_samples": 0,
        "null_repetitions": 6, "random_directions": 8,
        "logistic_c": config["analysis"]["frozen_baseline_c"],
        "max_iter": config["analysis"]["frozen_baseline_max_iter"]}})
    for model_index, name in ((0, "text_tfidf"), (2, "sequence_nll"), (3, "mean_token_nll")):
        features = ([row["response_text"] for row in state["rows"]] if name == "text_tfidf"
                    else np.asarray([[row[name]] for row in state["rows"]]))
        np.testing.assert_allclose(state["models"][model_index].decision_function(features),
                                   legacy["scores"][name], rtol=0, atol=1e-12)
    provenance = state["json"]["frozen_control_provenance.json"]
    assert provenance["sources"] == 72 and provenance["rows"] == 576
    assert provenance["v2_rows_used_for_fitting"] == 0
    assert all("old-" in source for source in provenance["source_ids"])
    vocabulary = provenance["text_models"]["tfidf_score"]["vocabulary"]
    assert "cork" not in vocabulary and "steel" not in vocabulary
    assert provenance["text_models"]["char_tfidf_score"]["settings"]["ngram_range"] == (3, 5)
    assert all(np.isfinite(row[name]) for row in augmented for name in (
        "tfidf_score", "char_tfidf_score", "frozen_sequence_nll_score", "frozen_mean_token_nll_score"))
    assert controls["random_controls"].shape == (8, 1536)


def test_v2_and_legacy_held_out_changes_cannot_change_fitted_controls(frozen_setup):
    config, state = frozen_setup
    transfer.prepare_frozen_controls(_new_rows(), config)
    parameters = deepcopy(state["npz"])
    provenance = deepcopy(state["json"])
    for index, row in enumerate(state["rows"]):
        if row["split"] != "train" or row["rewrite_family"] == "C":
            row["response_text"] = "unseenheldoutmarker " * 30
            row["sequence_nll"] += 2000
            row["mean_token_nll"] += 1000
            state["hidden"][index, :, :3] *= -200
    new_rows = _new_rows()
    for row in new_rows:
        row.update(response_text="neverfitnewmarker " * 100, certainty="confident",
                   sequence_nll=6000, mean_token_nll=800, split="train")
    transfer.prepare_frozen_controls(new_rows, config)
    assert provenance == state["json"]
    for artifact, arrays in parameters.items():
        for name, expected in arrays.items():
            np.testing.assert_array_equal(state["npz"][artifact][name], expected)


def test_null_vectors_use_original_seed_source_means_and_rng_sequence(frozen_setup):
    config, state = frozen_setup
    _, controls = transfer.prepare_frozen_controls(_new_rows(), config)
    rng = np.random.default_rng(config["analysis"]["null_seed"])
    signs = rng.choice((-1., 1.), size=(6, 72))
    shuffled = signs @ state["differences"] / 72
    norms = np.linalg.norm(shuffled, axis=1)
    expected = np.divide(shuffled, norms[:, None], out=np.zeros_like(shuffled), where=norms[:, None] > 1e-12)
    np.testing.assert_array_equal(controls["shuffled_controls"], expected)
    random = rng.standard_normal((4, 1536))
    random /= np.linalg.norm(random, axis=1)[:, None]
    np.testing.assert_array_equal(controls["random_controls"], np.concatenate((random, -random)))
    np.testing.assert_array_equal(controls["random_controls"][:4], -controls["random_controls"][4:])


def test_overlapping_source_and_changed_pinned_direction_are_rejected(frozen_setup):
    config, state = frozen_setup
    rows = _new_rows()
    rows[0]["source_id"] = "old-00"
    with pytest.raises(ValueError, match="overlap"):
        transfer.prepare_frozen_controls(rows, config)
    state["directions"]["layer14_boundary"] = -state["directions"]["layer14_boundary"]
    with pytest.raises(ValueError, match="does not reproduce"):
        transfer.prepare_frozen_controls(_new_rows(), config)


def test_legacy_activation_row_alignment_is_checked_before_fitting(frozen_setup):
    config, state = frozen_setup
    state["variant_ids"] = [row["variant_id"] for row in reversed(state["rows"])]
    with pytest.raises(ValueError, match="row/state alignment changed"):
        transfer.prepare_frozen_controls(_new_rows(), config)
    assert not state["models"] and not state["npz"] and not state["json"]


def test_extraction_groups_share_only_identical_prompts_and_restore_sources(monkeypatch):
    rows = read_jsonl("data/confidence_transfer_v2/variants.jsonl")[:10]
    original = deepcopy(rows)
    called = {}

    def fake_extract(grouped, config, references):
        assert grouped == references
        called["groups"] = grouped
        return grouped, np.zeros((len(grouped), 2, 4, 1536), dtype=np.float32), {
            "prompt_ids_identical_within_source": True}

    monkeypatch.setattr(transfer, "extract_activations", fake_extract)
    restored, _, runtime = transfer.extract_transfer(rows, {})
    assert rows == original
    assert [row["source_id"] for row in restored] == [row["source_id"] for row in original]
    grouped = called["groups"]
    assert len({row["source_id"] for row in grouped}) == 7
    natural = [row for row in grouped if row["experiment"] == "natural_style"]
    assert len({row["source_id"] for row in natural}) == 1
    assert len({(row["question"], row["context"]) for row in natural}) == 1
    neutral = [row for row in grouped if row["experiment"] == "neutral_evidence"]
    assert len({row["source_id"] for row in neutral}) == 6
    assert runtime["prompt_ids_identical_within_extraction_group"] is True
    assert "prompt_ids_identical_within_source" not in runtime


def test_frozen_artifact_hash_and_committed_design_gate(monkeypatch):
    config = load_config("configs/paired_confidence_transfer_v2.yaml")
    expected = {item["path"]: item["sha256"] for item in config["source_artifacts"].values()}
    monkeypatch.setattr(transfer, "file_hash", lambda path: expected[path])
    monkeypatch.setattr(transfer.subprocess, "run", lambda *args, **kwargs:
        SimpleNamespace(returncode=0, stdout=b""))
    transfer.verify_frozen_inputs(config)
    config["analysis"]["no_v2_fitting"] = False
    with pytest.raises(ValueError, match="test-only"):
        transfer.verify_frozen_inputs(config)
    config["analysis"]["no_v2_fitting"] = True
    monkeypatch.setattr(transfer, "file_hash", lambda path: "changed")
    with pytest.raises(ValueError, match="Pinned v1 artifact changed"):
        transfer.verify_frozen_inputs(config, require_commit=False)
    monkeypatch.setattr(transfer, "file_hash", lambda path: expected[path])
    monkeypatch.setattr(transfer.subprocess, "run", lambda *args, **kwargs:
        SimpleNamespace(returncode=0, stdout=b"uncommitted edit" if args[0][1] == "diff" else b""))
    with pytest.raises(ValueError, match="unchanged committed"):
        transfer.verify_frozen_inputs(config)


@pytest.mark.parametrize("failure", (None, "neutral_position", "cache_resume"))
def test_four_source_engineering_gate_without_model_inference(monkeypatch, failure):
    runner = importlib.import_module("scripts.run_confidence_transfer_v2")
    config = load_config("configs/paired_confidence_transfer_v2.yaml")
    sources = read_jsonl(config["data"]["source_items"])
    rows = read_jsonl(config["data"]["variants"])
    calls = []
    reports = []

    def fake_extract(selected, settings):
        calls.append(selected)
        assert len(selected) == 40
        assert len({row["fact_type"] for row in selected}) == 4
        extracted = []
        for row in selected:
            boundary = row["prompt_token_count"] + len(row["response_ids"])
            extracted.append({**row, "response_start_position": row["prompt_token_count"],
                "response_stop_position_exclusive": boundary, "boundary_position": boundary,
                "final_content_position": boundary - 1, "boundary_token_id": 151645})
        if failure == "neutral_position":
            extracted[0]["boundary_position"] += 1
            extracted[0]["response_stop_position_exclusive"] += 1
            extracted[0]["final_content_position"] += 1
        hidden = np.zeros((40, 2, 4, 1536), dtype=np.float32)
        if failure == "cache_resume" and len(calls) == 2:
            hidden[0, 0, 0, 0] = 1
        runtime = {"generation_calls": 0, "nli_calls": 0, "openai_api_calls": 0,
            "forward_calls": 40 if len(calls) == 1 else 0,
            "cache_hits": 0 if len(calls) == 1 else 40,
            "prompt_ids_identical_within_extraction_group": True,
            "max_prompt_state_difference": 0}
        return extracted, hidden, runtime

    monkeypatch.setattr(runner, "extract_transfer", fake_extract)
    monkeypatch.setattr(runner, "write_json", lambda path, report: reports.append(report))
    if failure is None:
        report = runner.sanity(rows, sources, config)
        assert report["passed"] and all(report["checks"].values())
        assert report["outcome_scores_inspected"] is False
    else:
        with pytest.raises(RuntimeError, match="Engineering gate failed"):
            runner.sanity(rows, sources, config)
        assert not reports[-1]["passed"]
        key = ("neutral_response_and_absolute_position_match" if failure == "neutral_position"
               else "exact_cache_resume")
        assert reports[-1]["checks"][key] is False
    assert len(calls) == 2 and calls[0] == calls[1]


def test_script_verifies_committed_inputs_before_any_extraction(monkeypatch):
    runner = importlib.import_module("scripts.run_confidence_transfer_v2")
    config = load_config("configs/paired_confidence_transfer_v2.yaml")
    monkeypatch.setattr(runner, "load_config", lambda path: config)
    monkeypatch.setattr(runner, "validate_transfer_dataset", lambda *args: {
        "passed": True, "catalog_sha256": "fixed-scoreless-catalog"})
    require_commit_flags = []

    def frozen_gate(settings, *, require_commit: bool):
        assert settings is config
        if require_commit:
            raise ValueError("uncommitted design")
        require_commit_flags.append(require_commit)

    monkeypatch.setattr(runner, "verify_frozen_inputs", frozen_gate)
    monkeypatch.setattr(runner, "extract_transfer", lambda *args:
        pytest.fail("Extraction started before the committed design gate passed"))
    monkeypatch.setattr(runner, "write_json", lambda *args:
        pytest.fail("An output was written before the committed design gate passed"))
    result = runner.run("mock-config.yaml", "audit")
    assert result["passed"] and require_commit_flags == [False]
    with pytest.raises(ValueError, match="uncommitted design"):
        runner.run("mock-config.yaml", "run")
