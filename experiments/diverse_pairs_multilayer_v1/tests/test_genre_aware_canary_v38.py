import hashlib
import importlib.util
import json
from collections import Counter
from pathlib import Path

import pytest


BASE = Path(__file__).resolve().parents[1]
MODULE_PATH = BASE / "src" / "build_genre_aware_canary_v38.py"
SPEC = importlib.util.spec_from_file_location("genre_canary_v38", MODULE_PATH)
MOD = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MOD)


def test_marker_stripping_preserves_every_other_byte():
    source = "  alpha\r\n<STANCE_1>\r\n beta  \n<STANCE_2>\nend\n"
    assert MOD.strip_stance_markers(source) == "  alpha\r\n beta  \nend\n"
    assert MOD.strip_stance_markers("x <STANCE_1> y\n") == "x <STANCE_1> y\n"


def test_render_round_trip_uses_recorded_spans_not_find():
    base = "same cue text.\n\nBody with same cue text.\nConclusion."
    rendered, cue_spans, insertion_spans = MOD.render_with_spans(
        base, [0, len(base)], ["paragraph", "paragraph"], ["same cue text.", "same cue text."]
    )
    assert [rendered[x["start"] : x["end"]] for x in cue_spans] == ["same cue text."] * 2
    assert MOD.remove_spans(rendered, insertion_spans) == base


def test_structural_validation_fails_closed_inside_code_and_list():
    text = "Lead:\n```py\nx = 1\n```\n\n1. one\n2. two\nEnd."
    with pytest.raises(ValueError, match="inside code_fence"):
        MOD.validate_offset(text, text.index("x = 1"), "paragraph")
    with pytest.raises(ValueError, match="inside list_block"):
        MOD.validate_offset(text, text.index("2. two") + 2, "paragraph")
    MOD.validate_offset(text, len(text), "paragraph")


def test_table_and_dialogue_blocks_merge_and_selected_scope_fails_closed():
    text = (
        "| A | B |\n|---|---|\n| 1 | 2 |\n\n"
        'Alice: "First turn."\nBob: "Second turn."\n'
    )
    ranges = MOD.protected_ranges(text)
    tables = [item for item in ranges if item["kind"] == "markdown_table"]
    dialogues = [item for item in ranges if item["kind"] == "dialogue"]
    assert len(tables) == 1
    assert len(dialogues) == 1
    assert text[tables[0]["start"] : tables[0]["end"]].count("\n") == 3
    assert "Alice" in text[dialogues[0]["start"] : dialogues[0]["end"]]
    assert "Bob" in text[dialogues[0]["start"] : dialogues[0]["end"]]
    with pytest.raises(ValueError, match="inside markdown_table"):
        MOD.validate_offset(text, text.index("| 1"), "paragraph")

    fingerprint = MOD.structural_fingerprint(text)
    selected = [{
        "production_slot": "fixture",
        "main_structure": fingerprint,
        "control_structure": fingerprint,
    }]
    with pytest.raises(ValueError, match="exceed prose/list/fenced-code renderer scope"):
        MOD.renderer_scope_coverage(selected)

    indented = MOD.structural_fingerprint("Lead\n    x = 1\nEnd\n")
    with pytest.raises(ValueError, match="exceed prose/list/fenced-code renderer scope"):
        MOD.renderer_scope_coverage([{
            "production_slot": "indented-fixture",
            "main_structure": indented,
            "control_structure": indented,
        }])


def test_frozen_config_has_exact_quota_crossing_and_pinned_tokenizer():
    config = json.loads((BASE / "configs" / "genre_aware_canary_v38.json").read_text())
    entries = config["selection"]
    MOD.validate_quotas(entries)
    assert len({x["production_slot"] for x in entries}) == 20
    for topology in ["early", "middle", "late", "distributed"]:
        assert Counter(x["cue_family"] for x in entries if x["topology"] == topology) == Counter(
            ["confidence", "certainty", "stand", "view", "doubt"]
        )
    assert set(config["tokenizer"]["artifact_sha256"]) == {
        "tokenizer.json", "tokenizer_config.json", "vocab.json", "merges.txt"
    }
    assert config["gate_limitations"]["activation_not_inspected_before_freeze"] is True
    assert config["gate_limitations"]["authorizes_renderer_application_to_all_100_sources"] is False
    assert config["gate_limitations"]["table_dialogue_and_indented_code_require_separate_canaries"] is True
    expected_sources = {
        "contains_dialogue": 0,
        "contains_fenced_code": 3,
        "contains_indented_code": 0,
        "contains_list": 3,
        "contains_markdown_table": 0,
        "contains_other_unsupported": 0,
        "plain_prose_only": 14,
    }
    expected_ranges = {"code_fence": 6, "list_block": 3}
    scope = config["renderer_scope"]
    assert scope["eligible_response_structures"] == ["plain_prose", "list", "fenced_code"]
    assert scope["deferred_ineligible_structures"] == ["dialogue", "indented_code", "markdown_table"]
    assert scope["gate_pass_authorizes_all_100_without_rescreening"] is False
    assert scope["selected_coverage"]["main"] == {
        "sources": expected_sources,
        "protected_ranges": expected_ranges,
    }
    assert scope["selected_coverage"]["control"] == {
        "sources": expected_sources,
        "protected_ranges": expected_ranges,
    }
    assert MOD.renderer_scope_definition(MOD.renderer_scope_coverage(entries)) == scope
    for entry in entries:
        for arm in ["main_structure", "control_structure"]:
            assert not (
                {"markdown_table", "dialogue", "indented_code"}
                & set(entry[arm]["protected_kind_counts"])
            )
    stress = [x for x in entries if x["cohort"] == "development_stress"]
    fresh = [x for x in entries if x["cohort"] == "fresh_diagnostic"]
    assert Counter(x["prior_diagnostic_decision"] for x in stress) == Counter(
        {"reject": 3, "discuss": 3, "accept": 4}
    )
    assert all(x["prior_diagnostic_decision"] is None for x in fresh)


def test_generated_pairs_are_byte_locked_token_paired_and_canonically_hashed():
    private = BASE / "private_data" / "genre_aware_canary_v38"
    for filename in ["FINAL_MAIN_20.json", "FINAL_CUE_ONLY_CONTROL_20.json"]:
        payload = json.loads((private / filename).read_text())
        assert payload["records_sha256"] == MOD.canonical_hash(payload["records"])
        assert len(payload["records"]) == 20
        for row in payload["records"]:
            assert row["token_counts"]["confident"] == row["token_counts"]["hedged"]
            assert MOD.remove_spans(row["confident_response"], row["confident_insertion_spans"]) == MOD.remove_spans(
                row["hedged_response"], row["hedged_insertion_spans"]
            )
            expected = 2 if row["topology"] == "distributed" else 1
            assert len(row["confident_cue_spans"]) == expected
            assert len(row["hedged_cue_spans"]) == expected


def test_public_manifest_is_text_free_and_claim_limited():
    manifest = json.loads((BASE / "manifests" / "genre_aware_canary_v38.json").read_text())
    serialized = json.dumps(manifest)
    forbidden_exact_keys = {
        "source_id", "prompt", "original_response", "shared_template",
        "confident_response", "hedged_response", "cue_referent",
    }
    def walk(value):
        if isinstance(value, dict):
            assert not (set(value) & forbidden_exact_keys)
            for child in value.values(): walk(child)
        elif isinstance(value, list):
            for child in value: walk(child)
    walk(manifest)
    assert "I have high confidence" not in serialized
    assert manifest["contains_source_or_response_text"] is False
    assert manifest["cue_diversity"] == {
        "contains_cue_text": False,
        "unique_cue_pair_renderings": 18,
        "unique_confident_cue_sentences": 23,
        "unique_hedged_cue_sentences": 23,
    }
    limits = manifest["gate_limitations"]
    assert limits["authorizes_probe_scoring"] is False
    assert limits["authorizes_lofo_interpretation"] is False
    assert limits["authorizes_sdt_loss_training"] is False
    assert limits["authorizes_renderer_application_to_all_100_sources"] is False
    assert manifest["renderer_scope"]["gate_pass_authorizes"] == (
        "rerender_and_review_of_eligible_prose_list_fenced_code_sources_only"
    )
    assert manifest["renderer_scope"]["selected_coverage"]["main"]["sources"]["contains_markdown_table"] == 0
    assert manifest["renderer_scope"]["selected_coverage"]["main"]["sources"]["contains_dialogue"] == 0
    assert manifest["renderer_scope"]["selected_coverage"]["main"]["sources"]["contains_indented_code"] == 0


def test_blind_packets_are_hash_bound_directional_and_balanced():
    private = BASE / "private_data" / "genre_aware_canary_v38"
    for arm in ["main", "control"]:
        review = private / f"review_{arm}"
        manifest = json.loads((review / "MANIFEST.json").read_text())
        key_text = (review / "UNBLIND_KEY.json").read_text()
        key = json.loads(key_text)
        assert hashlib.sha256(key_text.encode()).hexdigest() == manifest["unblind_key_sha256"]
        assert key["packet_sha256"] == manifest["packet_sha256"]
        assert Counter(x["version_a_label"] for x in key["pairs"]) == Counter({"confident": 10, "hedged": 10})
        html = (review / "BLIND_REVIEW.html").read_text()
        assert "a_more_certain" in html and "b_more_certain" in html
        assert 'data-field="structure_format"' in html
        assert "version_a_label" not in html
        assert manifest["review_dimensions"] == [
            "content_equivalence", "certainty_contrast", "naturalness",
            "cue_scope", "structure_format", "decision",
        ]
        assert manifest["packet_hash_mode"] == "schema-keycore-and-blinded-rows-sha256-v3"
        assert key["review_schema_sha256"] == manifest["review_schema_sha256"]
        assert key["key_core_sha256"] == manifest["key_core_sha256"]

        public = json.loads((BASE / "manifests" / "genre_aware_canary_v38.json").read_text())
        summary = public["review_packets"][arm]
        assert summary["packet_hash_mode"] == manifest["packet_hash_mode"]
        assert summary["review_schema_sha256"] == manifest["review_schema_sha256"]
        assert summary["key_core_sha256"] == manifest["key_core_sha256"]
