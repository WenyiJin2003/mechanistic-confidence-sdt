"""V3's truth swap preserves the same written answer and factorial crossing."""
from collections import Counter
from copy import deepcopy

import pytest

from confidence_pilot.common import load_config
from confidence_pilot.extract_activations import load_tokenizer
from confidence_pilot.separation_data_v3 import (
    ANSWER_KEYS, CERTAINTIES, FACT_SPECS, FACT_TYPES, WORDING_FAMILIES,
    build_dataset, validate_separation_dataset, write_separation_dataset,
)


@pytest.fixture(scope="module")
def catalog():
    config = load_config("configs/paired_confidence_transfer_v2.yaml")
    tokenizer = load_tokenizer(config)
    sources, rows, audit = build_dataset(config, tokenizer)
    return config, tokenizer, sources, rows, audit


def test_complete_fresh_and_balanced_catalog(catalog):
    config, tokenizer, sources, rows, audit = catalog
    assert audit["passed"], audit["errors"]
    assert len(sources) == 48 and len(rows) == 672
    assert Counter(source["fact_type"] for source in sources) == dict.fromkeys(FACT_TYPES, 12)
    assert Counter(source["wording_id"] for source in sources) == dict.fromkeys(WORDING_FAMILIES, 16)
    assert len({source["entity"] for source in sources}) == 48
    assert len({row["variant_id"] for row in rows}) == 672
    assert audit["source_freshness"]["all_keys_new"]
    assert audit["candidate_order_counts"] == {"A-B": 24, "B-A": 24}
    assert all(row["split"] == "test" for row in rows)
    rebuilt_sources, rebuilt_rows, rebuilt_audit = build_dataset(config, tokenizer)
    assert rebuilt_sources == sources and rebuilt_rows == rows
    assert rebuilt_audit["catalog_sha256"] == audit["catalog_sha256"]


def test_worlds_swap_roles_with_fixed_values_and_no_truth_in_omission(catalog):
    _, _, sources, rows, audit = catalog
    for source in sources:
        a, b = source["value_A"], source["value_B"]
        assert a != b
        for context in source["contexts"].values():
            assert context.count(a) == context.count(b) == context.count(source["entity"]) == 1
            assert context.index(a) < context.index(b) if source["candidate_order"][0] == "A" else context.index(b) < context.index(a)
        assert f"{a}: {source['target_role']}" in source["contexts"]["A"]
        assert f"{b}: {source['distractor_role']}" in source["contexts"]["A"]
        assert f"{b}: {source['target_role']}" in source["contexts"]["B"]
        assert f"{a}: {source['distractor_role']}" in source["contexts"]["B"]
        assert source["target_role"] not in source["contexts"]["omitted"]
    for row in rows:
        if row["world"] == "omitted":
            assert row["correctness"] is row["reference_world"] is row["world_correct_value"] is None
            assert row["supplied_support"] == "absent" and row["certainty"] == "neutral"
        else:
            correct = row["world"] == row["answer_key"]
            assert row["correctness"] == ("correct" if correct else "incorrect")
            assert row["supplied_support"] == ("supported" if correct else "contradicted")
    assert audit["world_row_counts"] == {"A": 288, "B": 288, "omitted": 96}
    assert audit["correctness_row_counts"] == {"correct": 288, "incorrect": 288, "None": 96}


def test_full_factorial_and_one_prompt_per_group(catalog):
    _, _, sources, rows, _ = catalog
    for source in sources:
        chosen = [row for row in rows if row["source_id"] == source["source_id"]]
        expected = {(world, answer, certainty) for world in ("A", "B")
                    for answer in ANSWER_KEYS for certainty in CERTAINTIES}
        expected |= {("omitted", answer, "neutral") for answer in ANSWER_KEYS}
        assert {(row["world"], row["answer_key"], row["certainty"]) for row in chosen} == expected
        for world in ("A", "B", "omitted"):
            group = [row for row in chosen if row["world"] == world]
            assert len({(row["context"], row["question"], row["prompt_group_id"]) for row in group}) == 1
        assert len({row["prompt_group_id"] for row in chosen}) == 3


def test_identical_response_and_absolute_answer_positions_across_truth_swap(catalog):
    _, _, sources, rows, audit = catalog
    by_key = {(row["source_id"], row["world"], row["answer_key"], row["certainty"]): row for row in rows}
    for source in sources:
        for answer in ANSWER_KEYS:
            for certainty in CERTAINTIES:
                a = by_key[(source["source_id"], "A", answer, certainty)]
                b = by_key[(source["source_id"], "B", answer, certainty)]
                for field in ("response_text", "response_ids", "prompt_token_count", "answer_token_positions",
                              "response_start_position", "boundary_position", "final_content_position"):
                    assert a[field] == b[field]
            supported = by_key[(source["source_id"], answer, answer, "neutral")]
            omitted = by_key[(source["source_id"], "omitted", answer, "neutral")]
            for field in ("response_text", "response_ids", "prompt_token_count", "answer_token_positions"):
                assert supported[field] == omitted[field]
    assert audit["primary_neutral_world_pair_count"] == 96
    assert audit["all_certainty_world_pair_count"] == 288
    assert audit["support_omission_pair_count"] == 96


def test_confidence_language_preserves_claim_and_crosses_correctness(catalog):
    _, _, _, rows, audit = catalog
    factorial = [row for row in rows if row["world"] != "omitted"]
    for row in factorial:
        assert row["response_text"].count(row["answer_span_text"]) == 1
        assert row["response_text"].count(row["entity"]) == 1
        assert '"' not in row["response_text"] and "'" not in row["response_text"]
        assert row["certainty_label_scope"] == "authored_language_style"
    for family in WORDING_FAMILIES:
        selected = [row for row in factorial if row["wording_id"] == family]
        assert Counter((row["correctness"], row["certainty"]) for row in selected) == {
            (correctness, certainty): 32 for correctness in ("correct", "incorrect") for certainty in CERTAINTIES}
    assert audit["confidence_pair_count"] == 192
    deltas = {family: {check["word_length_delta_confident_minus_hedged"] for check in audit["style_checks"]
                      if check["wording_id"] == family} for family in WORDING_FAMILIES}
    assert all(delta < 0 for delta in deltas["F1"])
    assert deltas["F2"] == {0}
    assert all(delta > 0 for delta in deltas["F3"])


@pytest.mark.parametrize("change", ("truth_label", "world", "answer", "confidence", "prompt", "drop_row", "position"))
def test_gate_rejects_important_mutations(catalog, change):
    config, tokenizer, sources, rows, _ = catalog
    changed = deepcopy(rows)
    if change == "truth_label":
        changed[0]["correctness"] = "incorrect"
    elif change == "world":
        changed[0]["world"] = "B"
    elif change == "answer":
        changed[0]["answer_span_text"] = sources[0]["value_B"]
    elif change == "confidence":
        changed[0]["response_text"] += " I checked an extra record."
    elif change == "prompt":
        changed[0]["context"] = sources[0]["contexts"]["B"]
    elif change == "position":
        changed[0]["answer_token_positions"][0] += 1
    else:
        changed.pop()
    audit = validate_separation_dataset(sources, changed, config, tokenizer)
    assert not audit["passed"] and audit["errors"]


def test_no_model_loading_and_output_scope_guard(catalog, monkeypatch):
    from transformers import AutoModelForCausalLM
    config, tokenizer, _, _, audit = catalog

    def forbidden(*args, **kwargs):
        raise AssertionError("Data construction loaded a model")

    monkeypatch.setattr(AutoModelForCausalLM, "from_pretrained", forbidden)
    build_dataset(config, tokenizer)
    assert audit["tokenizer_called"]
    assert audit["model_scoring_calls"] == audit["model_generation_calls"] == audit["nli_calls"] == 0
    assert audit["openai_api_calls"] == audit["downloads"] == 0
    with pytest.raises(ValueError, match="prior files are protected"):
        write_separation_dataset(config)


def test_tokenizer_only_gate_fails_when_omitted_roles_cannot_match(catalog, monkeypatch):
    config, tokenizer, _, _, _ = catalog
    spec = deepcopy(FACT_SPECS["access_code"])
    spec["omission_roles"] = ("lengthy decorative lettering printed on the packaging for local delivery",)
    monkeypatch.setitem(FACT_SPECS, "access_code", spec)
    with pytest.raises(ValueError, match="No tokenizer-only omission role matches"):
        build_dataset(config, tokenizer)
