"""The v2 transfer controls preserve truth while varying displayed evidence."""
from collections import Counter
from copy import deepcopy

import pytest

from confidence_pilot.common import load_config, read_jsonl
from confidence_pilot.extract_activations import load_tokenizer, tokenize_variant
from confidence_pilot.transfer_data_v2 import (
    CONDITIONS, DATASET_SEED, FACT_SPECS, FACT_TYPES, FORMATS,
    _match_omission_label, build_transfer_dataset, validate_transfer_dataset,
    write_transfer_dataset,
)


@pytest.fixture(scope="module")
def catalog():
    config = load_config("configs/paired_confidence_phase_b.yaml")
    config["dataset"]["seed"] = DATASET_SEED
    sources, rows, audit = build_transfer_dataset(config)
    return config, sources, rows, audit


def test_complete_held_out_catalog_and_fresh_fictional_world_keys(catalog):
    config, sources, rows, audit = catalog
    assert audit["passed"], audit["errors"]
    assert len(sources) == 48 and len(rows) == 480
    assert Counter(s["fact_type"] for s in sources) == dict.fromkeys(FACT_TYPES, 12)
    assert Counter(row["experiment"] for row in rows) == {"natural_style": 192, "neutral_evidence": 288}
    assert len({s["entity"] for s in sources}) == 48
    assert all(s["split"] == "test" and s["provenance"]["seed"] == DATASET_SEED for s in sources)
    assert all(row["split"] == "test" for row in rows)
    assert audit["source_freshness"]["all_keys_new"]
    assert audit["model_scoring_calls"] == audit["model_generation_calls"] == audit["downloads"] == 0
    second_sources, second_rows, second_audit = build_transfer_dataset(config)
    assert second_sources == sources and second_rows == rows
    assert second_audit["catalog_sha256"] == audit["catalog_sha256"]
    assert read_jsonl("data/confidence_transfer_v2/source_items.jsonl") == sources
    assert read_jsonl("data/confidence_transfer_v2/variants.jsonl") == rows


def test_writer_rejects_v1_output_paths_before_writing(catalog):
    config, _, _, _ = catalog
    with pytest.raises(ValueError, match="v1 files are protected"):
        write_transfer_dataset(config)


def test_evidence_conditions_keep_world_truth_candidates_and_balanced_order(catalog):
    _, sources, _, audit = catalog
    for source in sources:
        assert source["true_value"] != source["false_value"]
        for condition in CONDITIONS:
            context = source["contexts"][condition]
            assert context.count(source["entity"]) == 1
            assert context.count(source["true_value"]) == context.count(source["false_value"]) == 1
        assert f"{source['target_label']}: {source['true_value']}" in source["contexts"]["supported"]
        assert source["target_label"] not in source["contexts"]["omitted"]
        assert f"{source['omission_label']}: {source['true_value']}" in source["contexts"]["omitted"]
        assert f"{source['target_label']}: {source['false_value']}" in source["contexts"]["conflicting"]
    assert audit["target_line_order_counts"] == {"first": 24, "second": 24}
    assert all(counts == {"true_first": 24, "false_first": 24}
               for counts in audit["value_order_balanced_per_condition"].values())


def test_exact_neutral_response_ids_and_prompt_lengths_in_both_views(catalog):
    config, sources, rows, audit = catalog
    tokenizer = load_tokenizer(config)
    neutral = [row for row in rows if row["experiment"] == "neutral_evidence"]
    for source in sources:
        for view in FORMATS:
            chosen = [row for row in neutral if row["source_id"] == source["source_id"] and row["format"] == view]
            tokens = [tokenize_variant(row, tokenizer, config) for row in chosen]
            assert {row["condition"] for row in chosen} == set(CONDITIONS)
            assert {row["response_text"] for row in chosen} == {source["world_claim"]}
            assert len({tuple(token["response_ids"]) for token in tokens}) == 1
            assert len({token["prompt_length"] for token in tokens}) == 1
            assert all(row["correctness"] == "correct" and row["certainty"] == "neutral" for row in chosen)
    assert audit["neutral_comparison_count_per_format"] == {"qa": 48, "document": 48}


def test_natural_styles_keep_one_answer_and_have_matched_and_reversed_lengths(catalog):
    _, sources, rows, audit = catalog
    by_source = {source["source_id"]: source for source in sources}
    by_id = {row["variant_id"]: row for row in rows}
    natural = [row for row in rows if row["experiment"] == "natural_style"]
    for row in natural:
        source = by_source[row["source_id"]]
        partner = by_id[row["paired_variant_id"]]
        expected = source["true_value"] if row["correctness"] == "correct" else source["false_value"]
        assert row["answer_span_text"] == expected
        assert row["response_text"].count(expected) == 1
        assert row["context"] == source["contexts"]["supported"]
        assert row["question"] == source["qa_question"]
        assert partner["paired_variant_id"] == row["variant_id"]
        assert row["answer_span_text"] == partner["answer_span_text"]
        assert row["context"] == partner["context"] and row["question"] == partner["question"]
    assert audit["natural_pair_count"] == 96
    assert len(audit["template_pairs"]) == 12
    assert all(item["assigned_source_count"] == 4 and set(item["assigned_fact_types"]) == set(FACT_TYPES)
               for item in audit["template_pairs"])
    assert all(audit["length_subsets"][name] for name in (
        "token_length_matched", "word_length_matched", "char_length_matched",
        "assertion_longer_all_lengths", "assertion_shorter_all_lengths"))


@pytest.mark.parametrize("change", ("added_evidence", "changed_answer", "changed_prompt", "changed_condition"))
def test_gate_rejects_content_and_evidence_mutations(catalog, change):
    config, sources, rows, _ = catalog
    mutated = deepcopy(rows)
    if change == "added_evidence":
        mutated[0]["response_text"] += " I checked another register."
    elif change == "changed_answer":
        mutated[0]["answer_span_text"] = sources[0]["false_value"]
    elif change == "changed_prompt":
        mutated[0]["context"] = sources[0]["contexts"]["conflicting"]
    else:
        mutated[0]["condition"] = "omitted"
    audit = validate_transfer_dataset(sources, mutated, config)
    assert not audit["passed"] and audit["errors"]


def test_no_model_can_be_loaded_and_unmatchable_omission_is_reported(catalog, monkeypatch):
    from transformers import AutoModelForCausalLM
    config, sources, _, _ = catalog

    def forbidden_model(*args, **kwargs):
        raise AssertionError("The scoreless data builder tried to load a model")

    monkeypatch.setattr(AutoModelForCausalLM, "from_pretrained", forbidden_model)
    build_transfer_dataset(config)
    spec = deepcopy(FACT_SPECS["access_code"])
    spec["omission_labels"] = ("Recipient identification sequence used for shipping labels",)
    monkeypatch.setitem(FACT_SPECS, "access_code", spec)
    with pytest.raises(ValueError, match="No tokenizer-only omission label matches"):
        _match_omission_label(sources[0], load_tokenizer(config), config)
