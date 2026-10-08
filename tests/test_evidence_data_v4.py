"""V4 keeps answers fixed and holds out both source identities and templates."""
from collections import Counter
from copy import deepcopy

import pytest

from confidence_pilot.common import load_config
from confidence_pilot.extract_activations import load_tokenizer
from confidence_pilot.evidence_data_v4 import FACT_TYPES, build_dataset, validate_dataset


@pytest.fixture(scope="module")
def catalog():
    config = load_config("configs/paired_confidence_transfer_v2.yaml")
    tokenizer = load_tokenizer(config)
    sources, rows, behavior, audit = build_dataset(config, tokenizer)
    return config, tokenizer, sources, rows, behavior, audit


def test_fixed_counts_and_disjoint_sources_values_templates(catalog):
    _, _, sources, rows, behavior, audit = catalog
    assert audit["passed"], audit["errors"]
    assert (len(sources), len(rows), len(behavior)) == (168, 1584, 144)
    assert Counter(source["split"] for source in sources) == {"train": 96, "validation": 24, "test": 48}
    assert Counter(row["certainty"] for row in rows) == {"neutral": 1008, "confident": 288, "hedged": 288}
    assert Counter(source["context_template"] for source in sources) == {"T1": 96, "T2": 24, "T3": 24, "T4": 24}
    assert audit["source_freshness"]["all_keys_new"]
    assert audit["candidate_order_counts"] == {"A-B": 84, "B-A": 84}
    for fact in FACT_TYPES:
        assert Counter(source["split"] for source in sources if source["fact_type"] == fact) == {"train": 24, "validation": 6, "test": 12}
    assert len({value for source in sources for value in source["candidate_values"].values()}) == 336


def test_fixed_candidates_and_symmetric_two_role_omission(catalog):
    _, _, sources, rows, _, audit = catalog
    for source in sources:
        a, b = source["candidate_values"]["A"], source["candidate_values"]["B"]
        locations = source["tokenization_audit"]["candidate_context_token_positions"]
        assert locations["A"] == locations["B"] == locations["omitted"]
        for context in source["contexts"].values():
            assert context.count(a) == context.count(b) == 1
            assert (context.index(a) < context.index(b)) == (source["candidate_order"][0] == "A")
        assert source["target_role"] not in source["contexts"]["omitted"]
        assert source["distractor_role"] not in source["contexts"]["omitted"]
    for row in rows:
        if row["world"] == "omitted":
            assert row["correctness"] is row["reference_world"] is row["world_correct_value"] is None
            assert row["condition"] == "absent"
        else:
            assert row["correctness"] == ("correct" if row["world"] == row["answer_key"] else "incorrect")
    assert audit["omission_role_edit_counts_by_answer_key"] == {"A": 2, "B": 2}


def test_world_answer_style_crossings_and_absolute_token_identity(catalog):
    _, _, sources, rows, _, audit = catalog
    lookup = {(row["source_id"], row["world"], row["answer_key"], row["certainty"]): row for row in rows}
    for source in sources:
        styles = ("neutral", "confident", "hedged") if source["split"] == "test" else ("neutral",)
        for key in ("A", "B"):
            for style in styles:
                chosen = [lookup[(source["source_id"], world, key, style)] for world in ("A", "B", "omitted")]
                for field in ("response_text", "response_ids", "prompt_token_count", "answer_token_positions", "response_start_position", "boundary_position"):
                    assert all(row[field] == chosen[0][field] for row in chosen)
                assert all(row["response_text"].count(row["answer_span_text"]) == 1 for row in chosen)
    assert len(audit["world_identity_checks"]) == 528


def test_independent_behavior_has_full_three_worlds_and_equal_candidate_lengths(catalog):
    _, _, _, _, behavior, audit = catalog
    for row in behavior:
        assert row["split"] == "test"
        assert row["question"] != row["extraction_question"]
        assert "reply unknown" in row["question"]
        assert row["candidate_token_counts"]["A"] == row["candidate_token_counts"]["B"]
        assert row["correct_answer_key"] == (None if row["world"] == "omitted" else row["world"])
        assert row["expected_abstention"] == (row["world"] == "omitted")
    assert len(audit["behavior_checks"]) == 48
    assert all(check["passed"] for check in audit["behavior_checks"])


@pytest.mark.parametrize("change", ("label", "position", "behavior", "drop"))
def test_audit_rejects_dataset_mutations(catalog, change):
    config, tokenizer, sources, rows, behavior, _ = catalog
    chosen_rows, chosen_behavior = deepcopy(rows), deepcopy(behavior)
    if change == "label":
        chosen_rows[0]["condition"] = "contradicted"
    elif change == "position":
        chosen_rows[0]["answer_token_positions"][0] += 1
    elif change == "behavior":
        chosen_behavior[0]["correct_answer_key"] = "B"
    else:
        chosen_rows.pop()
    audit = validate_dataset(sources, chosen_rows, chosen_behavior, config, tokenizer)
    assert not audit["passed"] and audit["errors"]
