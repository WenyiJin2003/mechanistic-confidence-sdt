"""V4 fits source bundles, preserves candidate identity, and never fits behavior."""
from copy import deepcopy

import numpy as np
import pytest

from confidence_pilot.evidence_analysis_v4 import (
    NEUTRAL_ENDPOINTS, PRIMARY, SECONDARY, analyze, fit_readouts,
)


@pytest.fixture
def experiment(tmp_path):
    frozen = tmp_path / "frozen.npz"
    certainty = np.zeros(1536)
    certainty[1] = 1
    np.savez(frozen, layer14_response_mean=certainty, layer14_final_content=certainty)
    config = {"source_artifacts": {"directions": {"path": str(frozen)}},
              "analysis": {"expected_split_sources": {"train": 12, "validation": 4, "test": 8},
                           "pairwise_logistic_C": .01, "seed": 123, "max_iter": 3000,
                           "null_seed": 987, "null_repetitions": 8, "random_directions": 8,
                           "bootstrap_seed": 271828, "bootstrap_samples": 80}}
    rows, hidden, behavior = [], [], []
    for source_number in range(24):
        split = "train" if source_number < 12 else "validation" if source_number < 16 else "test"
        source = f"source-{source_number:02d}"
        strength = .7 + .05 * source_number
        fact_type = ("access_code", "material", "release_year", "room_assignment")[source_number % 4]
        template = "training-format" if split != "test" else "heldout-format"
        for world in ("A", "B", "omitted"):
            for answer in ("A", "B"):
                support = 0 if world == "omitted" else 1 if answer == world else -1
                for style in (("neutral", "confident", "hedged") if split == "test" else ("neutral",)):
                    index = len(rows)
                    tokens = 4 if style == "neutral" else 5
                    rows.append({"variant_id": f"{source}-{world}-{answer}-{style}", "source_id": source,
                                 "split": split, "fact_type": fact_type, "context_template": template,
                                 "world": world, "answer_key": answer, "certainty": style,
                                 "correctness": None if world == "omitted" else "correct" if support == 1 else "incorrect",
                                 "response_text": f"{style}: answer {answer}", "response_ids": [1 if answer == "A" else 2, tokens],
                                 "prompt_token_count": 20, "response_start_position": 20,
                                 "final_content_position": 20 + tokens - 1, "boundary_position": 20 + tokens,
                                 "mean_token_nll": 2 - support * .6, "sequence_nll": tokens * (2 - support * .6),
                                 "token_count": tokens})
                    feature = np.zeros((2, 4, 1536), dtype=np.float32)
                    feature[:, :3, 0] = support * strength
                    feature[:, :3, 1] = 0 if style == "neutral" else 10 if style == "confident" else -10
                    # Prompt context changes, but it cannot know the candidate answer.
                    feature[:, 3, 0] = 1 if world == "A" else -1 if world == "B" else 0
                    hidden.append(feature)
            if split == "test":
                candidate_margin = 2 * strength if world == "A" else -2 * strength if world == "B" else 0
                choice = world if world != "omitted" else "A" if source_number % 2 == 0 else "unknown"
                behavior.append({"source_id": source, "world": world, "candidate_sequence_logpA": candidate_margin / 2 - 6,
                                 "candidate_sequence_logpB": -candidate_margin / 2 - 6,
                                 "parsed_choice": choice, "greedy_text": choice})
    return rows, np.stack(hidden), behavior, config


def test_train_pairwise_mapping_and_frozen_reference(experiment):
    rows, hidden, _, config = experiment
    fitted = fit_readouts(rows, hidden, config)
    vector = fitted["vectors"][PRIMARY]
    np.testing.assert_allclose(vector[0], 1, atol=1e-8)
    np.testing.assert_allclose(vector[1:], 0, atol=1e-8)
    np.testing.assert_allclose(fitted["vectors"][SECONDARY], vector)
    np.testing.assert_array_equal(fitted["vectors"]["layer14_response_mean_frozen_certainty"][1], 1)
    provenance = fitted["provenance"]
    assert provenance["training_pairs"] == 24
    assert provenance["mirrored_training_rows"] == 48
    assert provenance["fit_intercept"] is False
    assert provenance["selection_used_validation_test_or_behavior"] is False
    assert provenance["C"] == .01
    assert all("source-" in source for source in provenance["training_source_ids"])
    assert np.linalg.norm(vector) == 1
    assert fitted["scaler_arrays"][PRIMARY + "__scaler_scale"].shape == (1536,)
    np.testing.assert_allclose(fitted["scaler_arrays"][PRIMARY + "__raw_coefficient"]
                               * fitted["scaler_arrays"][PRIMARY + "__scaler_scale"],
                               fitted["scaler_arrays"][PRIMARY + "__scaled_coefficient"])


def test_heldout_states_and_numeric_outcomes_cannot_change_fits(experiment):
    rows, hidden, _, config = experiment
    first = fit_readouts(rows, hidden, config)
    altered_rows, altered_hidden = deepcopy(rows), hidden.copy()
    for index, row in enumerate(altered_rows):
        if row["split"] != "train":
            altered_hidden[index] = -1000 * altered_hidden[index] + 700
            row["mean_token_nll"] += 5000
            row["sequence_nll"] += 5000
    second = fit_readouts(altered_rows, altered_hidden, config)
    assert first["provenance"] == second["provenance"]
    for name in first["vectors"]:
        np.testing.assert_array_equal(first["vectors"][name], second["vectors"][name])
    np.testing.assert_array_equal(first["shuffled_controls"], second["shuffled_controls"])


def test_control_refits_preserve_bundles_and_norms(experiment):
    rows, hidden, _, config = experiment
    fitted = fit_readouts(rows, hidden, config)
    assert fitted["shuffled_controls"].shape == (8, 1536)
    signs = fitted["provenance"]["shuffled_controls"]["source_bundled_sign_flips"]
    assert len(signs) == 8 and all(len(repetition) == 12 for repetition in signs)
    assert set(np.ravel(signs)) <= {-1., 1.}
    assert fitted["provenance"]["shuffled_controls"]["frozen_train_scaler"]
    np.testing.assert_allclose(np.linalg.norm(fitted["random_controls"], axis=1), 1)
    np.testing.assert_array_equal(fitted["random_controls"][:4], -fitted["random_controls"][4:])


def test_analysis_gates_and_candidate_blind_prompt_control(experiment):
    rows, hidden, behavior, config = experiment
    fitted = fit_readouts(rows, hidden, config)
    # A one-dimensional fixture has trivially correlated sign controls. Make the
    # analysis fixture's null orthogonal so that independent gate tests are clear.
    fitted["shuffled_controls"] = fitted["random_controls"].copy()
    fitted["shuffled_controls"][:, 0] = 0
    result = analyze(rows, hidden, fitted, behavior, config)
    primary = result["metrics"]["primary"]
    for endpoint in NEUTRAL_ENDPOINTS:
        metric = primary[endpoint]
        assert metric["accuracy"] == 1
        assert metric["n_sources"] == 8 and metric["n_pairs"] == 16
        assert metric["bootstrap_95"]["lower"] == 1
        assert set(metric["by_candidate"]) == {"A", "B"}
        assert set(metric["by_heldout_template"]) == {"heldout-format"}
        assert result["baselines"]["constant"][endpoint]["accuracy"] == .5
        assert result["baselines"]["response_token_length"][endpoint]["tie_fraction"] == 1
        assert result["readouts"]["layer14_prompt_candidateblind"][endpoint]["accuracy"] == .5
        assert result["readouts"]["layer14_response_mean_frozen_certainty"][endpoint]["accuracy"] == .5
    assert result["gates"]["evidence_support_generalization"]["passed"]
    assert result["gates"]["pilot_construct_validation"]["passed"]
    assert result["behavior"]["candidate_choice_coverage"]["accuracy"] == pytest.approx(5 / 6)
    assert result["behavior"]["known_world_generative_correctness"]["accuracy"] == 1
    assert result["behavior"]["greedy_agreement_unconditional"]["accuracy"] == pytest.approx(2 / 3)
    # Equal-source weighting: four source conditional agreements are 2/3,
    # four are 1; the pooled raw-prompt fraction would instead be 0.8.
    assert result["behavior"]["greedy_agreement_conditional_on_candidate_choice"]["accuracy"] == pytest.approx(5 / 6)
    assert result["behavior"]["known_world_candidate_choice_coverage"]["accuracy"] == 1
    assert result["behavior"]["condition_fact_type_centered_correlation"]["bootstrap_95"]["lower"] > 0
    assert result["behavior"]["omitted_choice_counts"]["unknown"] == 4
    assert all(row["world_correct"] is None for row in result["behavior"]["trace"] if row["world"] == "omitted")


def test_behavior_is_not_required_to_fit_and_cannot_change_directions(experiment):
    rows, hidden, behavior, config = experiment
    fitted = fit_readouts(rows, hidden, config)
    result = analyze(rows, hidden, fitted, [], config)
    assert result["behavior"]["present"] is False
    assert not result["gates"]["pilot_construct_validation"]["passed"]
    changed = deepcopy(behavior)
    for row in changed:
        row["parsed_choice"] = "other"
    second = analyze(rows, hidden, fitted, changed, config)
    assert second["row_scores"] == result["row_scores"]
    assert second["behavior"]["candidate_choice_coverage"]["accuracy"] == 0
    assert second["behavior"]["known_world_generative_correctness"]["accuracy"] == 0
    assert not second["gates"]["independent_behavior_alignment"]["passed"]


def test_abstention_in_omitted_world_does_not_fail_known_world_coverage(experiment):
    rows, hidden, behavior, config = experiment
    fitted = fit_readouts(rows, hidden, config)
    behavior = deepcopy(behavior)
    for row in behavior:
        if row["world"] == "omitted":
            row["parsed_choice"] = "unknown"
    result = analyze(rows, hidden, fitted, behavior, config)
    assert result["behavior"]["candidate_choice_coverage"]["accuracy"] == pytest.approx(2 / 3)
    assert result["behavior"]["known_world_candidate_choice_coverage"]["accuracy"] == 1
    assert result["behavior"]["checks"]["known_world_candidate_coverage_ge_075"]
    assert result["behavior"]["passed"]


def test_same_response_likelihood_manipulation_is_required(experiment):
    rows, hidden, behavior, config = experiment
    fitted = fit_readouts(rows, hidden, config)
    for row in rows:
        row["mean_token_nll"] = 2
    result = analyze(rows, hidden, fitted, behavior, config)
    gate = result["gates"]["same_response_likelihood_manipulation"]
    assert gate["metric"]["accuracy"] == .5
    assert gate["passed"] is False
    assert not result["gates"]["evidence_support_generalization"]["passed"]


def test_strict_values_and_exact_abstention_are_separate_descriptive_checks(experiment):
    rows, hidden, behavior, config = experiment
    fitted = fit_readouts(rows, hidden, config)
    behavior = deepcopy(behavior)
    for row in behavior:
        row["candidate_answers"] = {key: row["source_id"] + "-" + key for key in ("A", "B")}
        if row["world"] == "A":
            row["greedy_text"] = " " + row["candidate_answers"]["A"] + ". "
            row["exact_candidate_value_match"] = True
        elif row["world"] == "B":
            row["greedy_text"] = "The value is " + row["candidate_answers"]["B"] + "."
            row["exact_candidate_value_match"] = False
        else:
            row["greedy_text"] = "unknown" if int(row["source_id"][-2:]) % 2 == 0 else "Unknown because the record is incomplete."
            row["parsed_choice"] = "unknown"
            row["exact_candidate_value_match"] = False
    result = analyze(rows, hidden, fitted, behavior, config)
    measured = result["behavior"]
    assert measured["known_world_generative_correctness"]["accuracy"] == 1
    assert measured["known_world_exact_value_correctness"]["accuracy"] == .5
    assert measured["omitted_exact_unknown_rate"]["accuracy"] == .5
    assert measured["known_world_exact_value_correctness"]["used_as_gate"] is False
    assert measured["omitted_exact_unknown_rate"]["used_as_gate"] is False
    assert measured["passed"]  # Existing parsed-choice gates are unchanged.
    assert measured["output_parsing_audit"]["known_world_non_exact_candidate_output_count"] == 8
    assert measured["output_parsing_audit"]["non_exact_candidate_output_count"] == 16
    assert all(row["candidate_answers"] for row in measured["trace"])
    assert all(row["exact_value_world_correct"] is None for row in measured["trace"] if row["world"] == "omitted")


def test_exact_value_fallback_requires_available_candidate_values(experiment):
    rows, hidden, behavior, config = experiment
    fitted = fit_readouts(rows, hidden, config)
    # These lightweight fixtures have no value map or exact-match flag.
    result = analyze(rows, hidden, fitted, behavior, config)
    assert result["behavior"]["known_world_exact_value_correctness"]["accuracy"] == 0
    behavior = deepcopy(behavior)
    for row in behavior:
        row["candidate_answers"] = {"A": "A", "B": "B"}
    measured = analyze(rows, hidden, fitted, behavior, config)["behavior"]
    assert measured["known_world_exact_value_correctness"]["accuracy"] == 1
    assert measured["output_parsing_audit"]["known_world_non_exact_candidate_output_count"] == 0


def test_shuffled_control_is_a_strict_descriptive_gate(experiment):
    rows, hidden, behavior, config = experiment
    fitted = fit_readouts(rows, hidden, config)
    fitted["shuffled_controls"] = np.tile(fitted["vectors"][PRIMARY], (8, 1))
    result = analyze(rows, hidden, fitted, behavior, config)
    gate = result["gates"]["shuffled_control"]
    assert gate["observed"] == gate["upper_95th_percentile"] == 1
    assert gate["passed"] is False
    assert "not a permutation p-value" in gate["interpretation"]


def test_style_sensitivity_is_reported_without_becoming_a_gate(experiment):
    rows, hidden, behavior, config = experiment
    fitted = fit_readouts(rows, hidden, config)
    result = analyze(rows, hidden, fitted, behavior, config)
    diagnostic = result["readouts"]["layer14_response_mean_frozen_certainty"]["style_diagnostics"]
    assert diagnostic["used_as_gate"] is False
    assert diagnostic["by_evidence_condition"]["supported"]["confident_minus_hedged"]["estimate"] == 20
    # Frozen wording readout gives exactly constant neutral scores, so a
    # standardized shift has no defined denominator and must not be invented.
    assert diagnostic["neutral_score_standard_deviation"] == 0
    assert diagnostic["maximum_absolute_standardized_style_shift"] is None


@pytest.mark.parametrize("mutation", ("split", "drop", "duplicate", "answer_text", "position", "omitted_truth", "count", "c_value", "train_style"))
def test_invalid_design_is_rejected(experiment, mutation):
    rows, hidden, _, config = experiment
    rows, hidden, config = deepcopy(rows), hidden.copy(), deepcopy(config)
    if mutation == "split":
        rows[0]["split"] = "test"
    elif mutation == "drop":
        rows, hidden = rows[1:], hidden[1:]
    elif mutation == "duplicate":
        rows[0]["variant_id"] = rows[1]["variant_id"]
    elif mutation == "answer_text":
        rows[0]["response_text"] = "changed answer"
    elif mutation == "position":
        rows[0]["final_content_position"] += 1
    elif mutation == "omitted_truth":
        next(row for row in rows if row["world"] == "omitted")["correctness"] = "incorrect"
    elif mutation == "count":
        config["analysis"]["expected_split_sources"]["train"] += 1
    elif mutation == "c_value":
        config["analysis"]["pairwise_logistic_C"] = 1
    else:
        rows[0]["certainty"] = "confident"
    with pytest.raises(ValueError):
        fit_readouts(rows, hidden, config)


def test_incomplete_behavior_and_non_test_behavior_are_rejected(experiment):
    rows, hidden, behavior, config = experiment
    fitted = fit_readouts(rows, hidden, config)
    with pytest.raises(ValueError, match="Incomplete independent"):
        analyze(rows, hidden, fitted, behavior[1:], config)
    behavior = deepcopy(behavior)
    behavior[0]["source_id"] = "source-00"
    with pytest.raises(ValueError, match="non-test"):
        analyze(rows, hidden, fitted, behavior, config)
