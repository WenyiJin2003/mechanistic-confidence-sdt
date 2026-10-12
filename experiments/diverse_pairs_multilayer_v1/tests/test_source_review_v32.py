"""Fixture-only tests for the offline v3.2 source-review pool."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from experiments.diverse_pairs_multilayer_v1.src import build_source_review_pool_v32 as builder
from experiments.diverse_pairs_multilayer_v1.src import promote_source_review_v32 as promoter


WILD = "allenai/WildChat-1M"
HELP = "nvidia/HelpSteer2"
WILD_REV = "wild-revision"
HELP_REV = "help-revision"
FINGERPRINT = "fixture-fingerprint"


def source_row(
    source_id: str,
    dataset: str,
    task: str,
    length: str,
    *,
    prompt: str | None = None,
    response: str | None = None,
) -> dict:
    prompt = prompt or f"Explain the stable fixture fact for {source_id}."
    response = response or (
        f"Fixture {source_id} gives a stable explanation with enough ordinary prose to support "
        "a content-preserving rewrite while keeping its central factual claim unchanged."
    )
    prompt_hash = builder.sha256_text(" ".join(prompt.casefold().split()))
    response_hash = builder.sha256_text(response)
    return {
        "source_id": source_id,
        "dataset": dataset,
        "dataset_revision": WILD_REV if dataset == WILD else HELP_REV,
        "prompt": prompt,
        "original_response": response,
        "original_response_sha256": response_hash,
        "normalized_response_sha256": builder.sha256_text(" ".join(response.casefold().split())),
        "normalized_prompt_sha256": prompt_hash,
        "canonical_prompt_sha256": prompt_hash,
        "group_id": f"group-{prompt_hash}",
        "development_template_group": builder.sha256_text(f"dev:{source_id}"),
        "legacy_template_group": builder.sha256_text(f"legacy:{source_id}"),
        "task": task,
        "length_bin": length,
    }


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(builder.jsonl_bytes(rows))


def fixture_config(tmp_path: Path) -> Path:
    cache = tmp_path / "cache" / "fixture.jsonl"
    eligible = [
        source_row("w-factual-short", WILD, "factual_explanation", "short"),
        source_row("w-factual-medium", WILD, "factual_explanation", "medium"),
        source_row("w-math-long", WILD, "math_logic", "long"),
        source_row("h-programming-long", HELP, "programming", "long"),
    ]
    excluded = source_row("excluded-main", WILD, "factual_explanation", "short")
    roleplay = source_row(
        "creative",
        WILD,
        "summary_judgment",
        "medium",
        prompt="Write a fictional character roleplay scene.",
    )
    cache_rows = eligible + [excluded, roleplay]
    write_jsonl(cache, cache_rows)
    metadata = {
        "acquisition_fingerprint": FINGERPRINT,
        "jsonl_sha256": builder.sha256_file(cache),
        "source_count": len(cache_rows),
    }
    cache.with_name(cache.name + ".meta.json").write_text(json.dumps(metadata) + "\n")
    anchor = tmp_path / "anchor.jsonl"
    write_jsonl(anchor, [excluded])

    config = {
        "protocol_version": builder.PROTOCOL_VERSION,
        "selection_seed": 17,
        "expected_acquisition_fingerprint": FINGERPRINT,
        "dataset_revisions": {WILD: WILD_REV, HELP: HELP_REV},
        "cache_patterns": [str(cache)],
        "required_exclusion_paths": [str(anchor)],
        "candidate_quotas": {
            "dataset_counts": {WILD: 3, HELP: 1},
            "task_counts": {
                "factual_explanation": 2,
                "math_logic": 1,
                "programming": 1,
            },
            "length_counts": {"short": 1, "medium": 1, "long": 2},
        },
        "promotion_targets": {
            "review_pool_64": {
                "dataset_counts": {WILD: 3, HELP: 1},
                "task_counts": {
                    "factual_explanation": 2,
                    "math_logic": 1,
                    "programming": 1,
                },
                "length_counts": {"short": 1, "medium": 1, "long": 2},
            },
            "primary_canary_32": {
                "dataset_counts": {WILD: 1, HELP: 1},
                "task_counts": {"factual_explanation": 1, "programming": 1},
                "length_counts": {"short": 1, "long": 1},
            },
        },
        "private_candidate_file": str(tmp_path / "private" / "candidates.jsonl"),
        "private_review_packet": str(tmp_path / "private" / "review-packet.jsonl"),
        "completed_review_file": str(tmp_path / "private" / "review-completed.jsonl"),
        "promoted_review_pool_file": str(tmp_path / "private" / "reviewed-4.jsonl"),
        "primary_canary_file": str(tmp_path / "private" / "canary-2.jsonl"),
        "public_freeze_manifest": str(tmp_path / "public-freeze.json"),
        "public_promotion_manifest": str(tmp_path / "public-promotion.json"),
    }
    path = tmp_path / "config.json"
    path.write_text(json.dumps(config, sort_keys=True) + "\n")
    return path


def test_prefilters_are_explicit_and_do_not_claim_approval():
    refusal = source_row(
        "refusal", WILD, "factual_explanation", "short", response="I cannot provide that information."
    )
    current = source_row(
        "current", WILD, "factual_explanation", "short", prompt="What is the latest exchange rate today?"
    )
    medical = source_row(
        "medical", WILD, "factual_explanation", "short", prompt="What dosage should I take for my symptoms?"
    )
    assert "refusal_or_clarification_only" in builder.prefilter_reasons(refusal)
    assert "current_or_time_sensitive" in builder.prefilter_reasons(current)
    assert "medical_guidance" in builder.prefilter_reasons(medical)
    assert builder.prefilter_reasons(source_row("plain", WILD, "factual_explanation", "short")) == []
    assert "approved" not in builder.PREFILTER_DESCRIPTIONS


def test_jsonl_reader_preserves_unicode_line_separator_inside_string(tmp_path: Path):
    path = tmp_path / "unicode.jsonl"
    row = {"source_id": "unicode", "original_response": "first\u2028second"}
    write_jsonl(path, [row])
    assert builder.read_jsonl(path) == [row]


def test_fixture_build_is_offline_text_free_public_and_blank_private_review(tmp_path: Path):
    config_path = fixture_config(tmp_path)
    first = builder.build(config_path)
    second = builder.build(config_path)
    assert first == second
    assert first["network_calls"] == 0 and first["model_calls"] == 0
    assert first["candidate_review_pool"]["count"] == 4
    assert first["candidate_review_pool"]["dataset_counts"] == {WILD: 3, HELP: 1}
    assert first["prefilter_exclusion_reason_counts_nonexclusive"]["roleplay_or_creative"] == 1
    assert first["excluded_by_anchor_field_nonexclusive"]["source_id"] == 1
    public_text = (tmp_path / "public-freeze.json").read_text()
    assert '"prompt"' not in public_text and '"original_response"' not in public_text
    packet = builder.read_jsonl(tmp_path / "private" / "review-packet.jsonl")
    assert len(packet) == 4
    assert all(row["review_decision"] == "" for row in packet)
    assert all(row["automated_prefilter_status"].endswith("not_human_approved") for row in packet)
    candidates = builder.read_jsonl(tmp_path / "private" / "candidates.jsonl")
    assert "excluded-main" not in {row["source_id"] for row in candidates}


def complete_review_packet(packet_path: Path, output_path: Path) -> None:
    rows = builder.read_jsonl(packet_path)
    for row in rows:
        row.update({
            "review_decision": "eligible",
            "content_stability": "pass",
            "rewrite_suitability": "pass",
            "uncertainty_central": "no",
            "high_stakes_or_current": "no",
        })
    write_jsonl(output_path, rows)


def test_promotion_fails_closed_on_incomplete_review_before_writing(tmp_path: Path):
    config_path = fixture_config(tmp_path)
    builder.build(config_path)
    packet = builder.read_jsonl(tmp_path / "private" / "review-packet.jsonl")
    write_jsonl(tmp_path / "private" / "review-completed.jsonl", packet)
    with pytest.raises(promoter.PromotionBlocked) as error:
        promoter.promote(config_path)
    assert error.value.details["missing_categorical_fields"]["review_decision"] == 4
    assert not (tmp_path / "private" / "reviewed-4.jsonl").exists()
    assert not (tmp_path / "private" / "canary-2.jsonl").exists()


def test_completed_fixture_promotes_exact_quotas_in_frozen_order(tmp_path: Path):
    config_path = fixture_config(tmp_path)
    builder.build(config_path)
    complete_review_packet(
        tmp_path / "private" / "review-packet.jsonl",
        tmp_path / "private" / "review-completed.jsonl",
    )
    result = promoter.promote(config_path)
    assert result["review_pool_64"]["count"] == 4
    assert result["primary_canary_32"]["count"] == 2
    assert result["primary_canary_32"]["dataset_counts"] == {WILD: 1, HELP: 1}
    assert result["primary_canary_32"]["task_counts"] == {
        "factual_explanation": 1,
        "programming": 1,
    }
    canary = builder.read_jsonl(tmp_path / "private" / "canary-2.jsonl")
    assert [row["candidate_sort_sha256"] for row in canary] == sorted(
        row["candidate_sort_sha256"] for row in canary
    )


def test_quota_failure_reports_marginal_gaps():
    rows = [
        {
            **source_row("only-wild", WILD, "factual_explanation", "short"),
            "candidate_sort_sha256": "0" * 64,
        }
    ]
    quotas = {
        "dataset_counts": {HELP: 1},
        "task_counts": {"factual_explanation": 1},
        "length_counts": {"short": 1},
    }
    with pytest.raises(promoter.PromotionBlocked) as error:
        promoter.select_lexicographically_exact(rows, quotas)
    assert error.value.details["dataset_counts"]["deficit"][HELP] == 1
    assert error.value.details["joint_quota_feasible"] is False
