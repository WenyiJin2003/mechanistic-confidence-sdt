"""Synthetic, offline report integrity and privacy tests; no private run is read."""
import builtins
import copy
import importlib.util
import io
import json
from pathlib import Path
import re
import struct
import zlib

import numpy as np
import pytest


SCRIPT = Path(__file__).resolve().parents[1] / "src/build_reports.py"
SPEC = importlib.util.spec_from_file_location("haiku5000_build_reports", SCRIPT)
reports = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(reports)

PRIVATE_MARKER = "PRIVATE_SOURCE_TEXT_MUST_NEVER_APPEAR_73e5d1"
STAT = "development_candidate_label_diagnostic_not_human_validated"
BASELINES = (
    "character_tfidf", "negative_mean_token_nll", "negative_response_token_length",
    "negative_response_word_length", "constant_tie", "final_response_token_layer14",
    "mean_difference_layer14", "mean_difference_equal_28_ensemble",
)
CONTROLS = (
    "group_disjoint", "canary_forced_train", "feature_scaling_train_only",
    "score_scaling_train_only", "tfidf_vocabulary_train_only",
)


def metric(wins=700, ties=0, *, layer=None, ci=None):
    estimate = (wins + .5 * ties) / 1000
    value = {"estimate": estimate, "ci95": ci or [max(0, estimate-.03), min(1, estimate+.03)],
             "groups": 1000, "pairs": 1000, "wins": wins, "ties": ties,
             "losses": 1000-wins-ties}
    if layer is not None:
        value["layer"] = layer
    return value


@pytest.fixture
def result():
    layers = [metric(layer=layer) for layer in range(1, 29)]
    baselines = {name: metric(600) for name in BASELINES}
    baselines["constant_tie"] = metric(0, 1000, ci=[.5, .5])
    return {
        "status": "complete", "scientific_status": STAT,
        "human_review_completed": False, "content_preservation_certified": False,
        "candidate_pairs": 5000, "train_pairs": 4000, "test_pairs": 1000,
        "train_groups": 4000, "test_groups": 1000,
        "primary": {"layer14": copy.deepcopy(layers[13]),
                    "equal_28_layer_ensemble": metric(740)},
        "ensemble_minus_layer14": {"estimate": .04, "ci95": [.02, .06]},
        "layers": layers, "secondary": baselines,
        "shuffled_training_orientation": {
            "repeats": 5, "descriptive_not_formal_p_value": True,
            "training_pair_orientation_only": True, "unchanged_test_labels": True,
            "layer14": [.49, .50, .51, .50, .50],
            "equal_28_layer_ensemble": [.50, .49, .51, .50, .50],
        },
        "prompt_control_max_abs_difference": 0.,
        "leakage_controls": {**dict.fromkeys(CONTROLS, True),
                             "test_sign_or_layer_selection": False},
        "provenance": {name: str(index) * 64 for index, name in enumerate((
            "plan_sha256", "data_sha256", "extraction_settings_sha256",
            "padding_audit_sha256", "analysis_script_sha256"), start=1)},
        "limitations": ["human item review pending"],
        "elapsed_evaluation_seconds": 1.25,
    }


def png_chunk(kind, data):
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind+data))


def synthetic_png(*, private_metadata=False):
    chunks = [png_chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 6, 0, 0, 0))]
    if private_metadata:
        chunks.append(png_chunk(b"tEXt", b"Comment\x00" + PRIVATE_MARKER.encode()))
    chunks.extend([png_chunk(b"IDAT", zlib.compress(b"\x00\x10\x20\x30\xff")),
                   png_chunk(b"IEND", b"")])
    return b"\x89PNG\r\n\x1a\n" + b"".join(chunks)


def write_run(tmp_path, result, *, private_metadata=False):
    run = tmp_path / ("run-" + PRIVATE_MARKER)
    run.mkdir()
    (run / "RESULTS.json").write_text(json.dumps(result), encoding="utf-8")
    (run / "ALL_28_LAYERS.png").write_bytes(synthetic_png(private_metadata=private_metadata))
    return run


def test_valid_aggregate_result_is_accepted_without_mutating_input(result):
    original = copy.deepcopy(result)
    safe = reports.validate_results(result)
    assert result == original
    assert safe["candidate_pairs"] == 5000
    assert safe["train_pairs"] == safe["train_groups"] == 4000
    assert safe["test_pairs"] == safe["test_groups"] == 1000
    assert [row["layer"] for row in safe["layers"]] == list(range(1, 29))
    assert safe["human_review_completed"] is False
    assert safe["content_preservation_certified"] is False


@pytest.mark.parametrize("field,value", [
    ("status", "extracting"), ("status", "partial"),
    ("scientific_status", "human_validated"),
    ("candidate_pairs", 4999), ("candidate_pairs", 5000.0),
    ("train_pairs", 3999), ("test_pairs", 999),
    ("train_groups", 3999), ("test_groups", 999),
    ("human_review_completed", True), ("human_review_completed", 0),
    ("content_preservation_certified", True), ("content_preservation_certified", 0),
])
def test_partial_or_changed_scientific_contract_is_rejected(result, field, value):
    result[field] = value
    with pytest.raises(ValueError):
        reports.validate_results(result)


@pytest.mark.parametrize("change", ["missing", "duplicate", "out_of_range"])
def test_all_28_unique_layer_indices_are_required(result, change):
    if change == "missing":
        result["layers"].pop()
    elif change == "duplicate":
        result["layers"][-1]["layer"] = 27
    elif change == "out_of_range":
        result["layers"][-1]["layer"] = 29
    with pytest.raises(ValueError):
        reports.validate_results(result)


@pytest.mark.parametrize("field,value", [
    ("wins", 701), ("ties", -1), ("losses", 299), ("pairs", 999),
    ("groups", 999), ("estimate", .701), ("estimate", float("nan")),
    ("estimate", float("inf")), ("estimate", True),
    ("ci95", [.8, .6]), ("ci95", [-.1, .8]), ("ci95", [.6, 1.1]),
    ("ci95", [.71, .75]), ("ci95", [float("nan"), .8]),
])
def test_metric_arithmetic_finite_values_and_intervals_are_checked(result, field, value):
    result["layers"][0][field] = value
    with pytest.raises(ValueError):
        reports.validate_results(result)


def test_metric_ties_receive_exactly_half_credit(result):
    result["layers"][0] = metric(650, 100, layer=1)
    assert reports.validate_results(result)["layers"][0]["estimate"] == .7
    result["layers"][0]["estimate"] = .75
    with pytest.raises(ValueError):
        reports.validate_results(result)


def test_primary_layer14_must_agree_with_its_all_layer_entry(result):
    result["primary"]["layer14"] = metric(710, layer=14)
    with pytest.raises(ValueError):
        reports.validate_results(result)


@pytest.mark.parametrize("baseline", BASELINES)
def test_every_declared_baseline_is_required(result, baseline):
    del result["secondary"][baseline]
    with pytest.raises(ValueError):
        reports.validate_results(result)


@pytest.mark.parametrize("baseline", BASELINES)
def test_baseline_metrics_require_the_same_auditable_counts(result, baseline):
    del result["secondary"][baseline]["wins"]
    with pytest.raises(ValueError):
        reports.validate_results(result)


def test_constant_tie_control_must_be_all_ties_at_point_five(result):
    result["secondary"]["constant_tie"] = metric(500, ci=[.5, .5])
    with pytest.raises(ValueError):
        reports.validate_results(result)


@pytest.mark.parametrize("field,value", [
    ("estimate", -.04), ("estimate", float("nan")),
    ("ci95", [.06, .02]), ("ci95", [-1.1, .1]),
    ("ci95", [.02, 1.1]), ("ci95", [.05, .06]),
])
def test_ensemble_delta_agrees_with_primary_estimates_and_valid_bounds(result, field, value):
    result["ensemble_minus_layer14"][field] = value
    with pytest.raises(ValueError):
        reports.validate_results(result)


@pytest.mark.parametrize("field,value", [
    ("repeats", 4), ("repeats", True),
    ("descriptive_not_formal_p_value", False),
    ("training_pair_orientation_only", False), ("unchanged_test_labels", False),
    ("unchanged_test_labels", 1), ("layer14", [.5]*4),
    ("equal_28_layer_ensemble", [.5]*6), ("layer14", [.5]*4 + [float("nan")]),
    ("equal_28_layer_ensemble", [.5]*4 + [1.1]),
])
def test_training_orientation_null_requires_five_repeats_and_explicit_flags(result, field, value):
    result["shuffled_training_orientation"][field] = value
    with pytest.raises(ValueError):
        reports.validate_results(result)


@pytest.mark.parametrize("control", CONTROLS)
@pytest.mark.parametrize("value", [False, 1, None])
def test_leakage_controls_must_be_literal_true(result, control, value):
    result["leakage_controls"][control] = value
    with pytest.raises(ValueError):
        reports.validate_results(result)


@pytest.mark.parametrize("value", [True, 0, None])
def test_test_based_sign_or_layer_selection_must_be_literal_false(result, value):
    result["leakage_controls"]["test_sign_or_layer_selection"] = value
    with pytest.raises(ValueError):
        reports.validate_results(result)


@pytest.mark.parametrize("value", [.0051, -.001, float("nan"), float("inf")])
def test_prompt_control_must_be_finite_and_within_audited_tolerance(result, value):
    result["prompt_control_max_abs_difference"] = value
    with pytest.raises(ValueError):
        reports.validate_results(result)


def test_public_validation_drops_untrusted_nested_metadata_and_free_text(result):
    result["raw_source_row"] = {"messages": [PRIVATE_MARKER]}
    result["question"] = PRIVATE_MARKER
    result["limitations"] = [PRIVATE_MARKER]
    result["provenance"]["snapshot_path"] = PRIVATE_MARKER
    result["layers"][0]["original"] = PRIVATE_MARKER
    result["primary"]["layer14"]["response"] = PRIVATE_MARKER
    result["secondary"]["character_tfidf"]["row_ids"] = [PRIVATE_MARKER]
    result["shuffled_training_orientation"]["raw_scores"] = PRIVATE_MARKER
    result["leakage_controls"]["prompt"] = PRIVATE_MARKER
    safe = reports.validate_results(result)
    assert PRIVATE_MARKER not in json.dumps(safe)
    assert PRIVATE_MARKER not in reports.render_report(safe)


def test_strong_conclusion_is_conditional_on_primary_and_paired_delta_intervals(result):
    decision = reports.conclusion(reports.validate_results(result))
    assert "Both predeclared readouts distinguish" in decision["ordering"]
    assert "improves held-out ordering" in decision["ensemble_comparison"]
    rendered = reports.render_report(reports.validate_results(result)).lower()
    assert "human" in rendered and "pending" in rendered
    assert "semantic entropy" in rendered
    assert "truth" in rendered


def test_intervals_crossing_chance_or_zero_do_not_support_strong_conclusions(result):
    result["layers"][13] = metric(510, layer=14, ci=[.48, .54])
    result["primary"]["layer14"] = copy.deepcopy(result["layers"][13])
    result["primary"]["equal_28_layer_ensemble"] = metric(520, ci=[.49, .55])
    result["ensemble_minus_layer14"] = {"estimate": .01, "ci95": [-.02, .04]}
    decision = reports.conclusion(reports.validate_results(result))
    assert "do not establish above-chance ordering" in decision["ordering"]
    assert "does not resolve an advantage" in decision["ensemble_comparison"]


@pytest.mark.parametrize("uncertain_readout", ["layer14", "equal_28_layer_ensemble"])
def test_one_readout_above_chance_does_not_support_a_claim_about_both(result, uncertain_readout):
    result["primary"][uncertain_readout]["ci95"] = [.4, .8]
    if uncertain_readout == "layer14":
        result["layers"][13]["ci95"] = [.4, .8]
    decision = reports.conclusion(reports.validate_results(result))
    assert "Both predeclared readouts distinguish" not in decision["ordering"]
    assert "the other predeclared readout does not establish above-chance ordering" in decision["ordering"]


def test_high_shuffled_orientation_control_qualifies_the_interpretation(result):
    result["shuffled_training_orientation"]["layer14"][0] = .75
    decision = reports.conclusion(reports.validate_results(result))
    assert "weakens" in decision["interpretation"]
    assert "formal p-value" in decision["interpretation"]


@pytest.mark.parametrize("baseline,wins,l14_wins,expected", [
    ("character_tfidf", 990, 700, "matches or exceeds both predeclared point estimates"),
    ("negative_response_token_length", 730, 700, "within two percentage points"),
    ("negative_response_word_length", 730, 700, "within two percentage points"),
    ("character_tfidf", 600, 700, "higher point estimates"),
    ("negative_response_token_length", 690, 700, "higher point estimates"),
    ("negative_response_token_length", 710, 690, "do not both exceed the strongest surface baseline"),
])
def test_surface_baseline_interpretation_depends_on_actual_measured_rates(result, baseline, wins,
                                                                        l14_wins, expected):
    result["secondary"][baseline] = metric(wins)
    result["layers"][13] = metric(l14_wins, layer=14)
    result["primary"]["layer14"] = copy.deepcopy(result["layers"][13])
    delta = .74 - l14_wins / 1000
    result["ensemble_minus_layer14"] = {"estimate": delta, "ci95": [delta-.02, delta+.02]}
    safe = reports.validate_results(result)
    decision = reports.conclusion(safe)
    interpretation = decision["interpretation"]
    assert expected in interpretation
    for name in ("character_tfidf", "negative_response_token_length", "negative_response_word_length"):
        assert f"{100 * result['secondary'][name]['estimate']:.2f}%" in interpretation
    assert f"{l14_wins / 10:.2f}%" in decision["ordering"]
    assert "74.00%" in decision["ordering"]
    if wins >= 730:
        assert "No added value" in interpretation
    else:
        assert "comparisons are descriptive; no paired baseline interval" in interpretation
    if wins == 730:
        assert "descriptively comparable" in interpretation
    assert "statistically superior" not in interpretation
    assert "statistically significant" not in interpretation
    rendered = reports.render_report(safe)
    assert interpretation in rendered
    assert "no paired interval for those comparisons" in rendered


def test_negative_delta_conclusion_favors_predeclared_layer14(result):
    result["primary"]["equal_28_layer_ensemble"] = metric(650)
    result["ensemble_minus_layer14"] = {"estimate": -.05, "ci95": [-.08, -.02]}
    decision = reports.conclusion(reports.validate_results(result))
    assert "Layer 14 orders more pairs" in decision["ensemble_comparison"]


def test_build_writes_public_aggregate_artifacts_and_strips_png_metadata(tmp_path, result):
    result["limitations"] = [PRIVATE_MARKER]
    result["raw_source_row"] = PRIVATE_MARKER
    run = write_run(tmp_path, result, private_metadata=True)
    output = tmp_path / "public"
    summary = reports.build_report(run, output)
    for name in ("RESULTS_5000.md", "SUMMARY_5000.json", "ALL_28_LAYERS.png"):
        path = output / name
        assert path.is_file()
        assert PRIVATE_MARKER.encode() not in path.read_bytes()
    saved = json.loads((output / "SUMMARY_5000.json").read_text(encoding="utf-8"))
    assert saved == summary
    assert saved["candidate_pairs"] == 5000
    assert saved["predictions_audited"] is False
    assert (output / "ALL_28_LAYERS.png").read_bytes().startswith(b"\x89PNG\r\n\x1a\n")


@pytest.mark.parametrize("problem", ["missing_results", "partial_results", "missing_plot", "bad_plot"])
def test_build_fails_closed_without_creating_outputs(tmp_path, result, problem):
    run = write_run(tmp_path, result)
    if problem == "missing_results":
        (run / "RESULTS.json").unlink()
    elif problem == "partial_results":
        result["status"] = "extracting"
        (run / "RESULTS.json").write_text(json.dumps(result), encoding="utf-8")
    elif problem == "missing_plot":
        (run / "ALL_28_LAYERS.png").unlink()
    else:
        (run / "ALL_28_LAYERS.png").write_bytes(b"not a png")
    output = tmp_path / "public"
    with pytest.raises((ValueError, FileNotFoundError)):
        reports.build_report(run, output)
    assert not output.exists() or not list(output.iterdir())


def test_builder_never_reads_private_caches_or_imports_model_stack(tmp_path, result, monkeypatch):
    run = write_run(tmp_path, result)
    for name in ("DATA.json", "PLAN.json", "TRIPLETS.json", "PREDICTIONS.npz",
                 "FROZEN_READOUTS.npz", "STATES.npy", "NLL.npy"):
        (run / name).write_text(PRIVATE_MARKER, encoding="utf-8")
    original_open, original_io_open = builtins.open, io.open
    original_import = builtins.__import__

    def guarded_open(file, *args, **kwargs):
        if isinstance(file, (str, Path)) and Path(file).parent == run:
            assert Path(file).name in {"RESULTS.json", "ALL_28_LAYERS.png"}
        return original_open(file, *args, **kwargs)

    def guarded_import(name, *args, **kwargs):
        assert name.split(".")[0] not in {"torch", "transformers", "sklearn", "anthropic"}
        return original_import(name, *args, **kwargs)

    def guarded_io_open(file, *args, **kwargs):
        if isinstance(file, (str, Path)) and Path(file).parent == run:
            assert Path(file).name in {"RESULTS.json", "ALL_28_LAYERS.png"}
        return original_io_open(file, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", guarded_open)
    monkeypatch.setattr(io, "open", guarded_io_open)
    monkeypatch.setattr(builtins, "__import__", guarded_import)
    reports.build_report(run, tmp_path / "public")


def write_predictions(path, *, changed=False, tied_layer=False):
    layer_scores = np.zeros((1000, 2, 28))
    layer_scores[:700, 0, :] = 1
    layer_scores[700:, 1, :] = 1
    if tied_layer:
        layer_scores[:, :, 0] = 0
        layer_scores[:650, 0, 0] = 1
        layer_scores[750:, 1, 0] = 1
    equal_scores = np.zeros((1000, 2))
    equal_scores[:740, 0] = 1
    equal_scores[740:, 1] = 1
    if changed:
        equal_scores[0] = [0, 1]
    np.savez(path, layer_scores=layer_scores, equal_scores=equal_scores,
             group_ids=np.asarray([f"synthetic-private-group-{i}" for i in range(1000)]),
             source_text=np.asarray([PRIVATE_MARKER], dtype=object))


def test_optional_prediction_audit_uses_only_allowed_arrays_and_redacts_ids(tmp_path, result):
    run = write_run(tmp_path, result)
    predictions = run / "PREDICTIONS.npz"
    write_predictions(predictions)
    output = tmp_path / "public"
    summary = reports.build_report(run, output, predictions_path=predictions)
    assert summary["predictions_audited"] is True
    for path in output.rglob("*"):
        if path.is_file():
            assert PRIVATE_MARKER.encode() not in path.read_bytes()
            assert b"synthetic-private-group-" not in path.read_bytes()


def test_prediction_audit_preserves_half_credit_for_ties(tmp_path, result):
    result["layers"][0] = metric(650, 100, layer=1)
    run = write_run(tmp_path, result)
    predictions = run / "PREDICTIONS.npz"
    write_predictions(predictions, tied_layer=True)
    summary = reports.build_report(run, tmp_path / "public", predictions_path=predictions)
    assert summary["layers"][0]["estimate"] == .7
    assert summary["layers"][0]["ties"] == 100
    assert summary["predictions_audited"] is True


def test_prediction_disagreement_fails_before_public_output(tmp_path, result):
    run = write_run(tmp_path, result)
    predictions = run / "PREDICTIONS.npz"
    write_predictions(predictions, changed=True)
    output = tmp_path / "public"
    with pytest.raises(ValueError):
        reports.build_report(run, output, predictions_path=predictions)
    assert not output.exists() or not list(output.iterdir())


def test_readme_renderer_replaces_only_the_unique_marked_block(result):
    prefix, suffix = "# Existing project\n\nKeep the original context.\n\n", "\n\n## Other work\nKeep this too.\n"
    existing = (prefix + "<!-- SCALEUP_RESULT_START -->\nOLD AUTO RESULT\n"
                "<!-- SCALEUP_RESULT_END -->" + suffix)
    updated = reports.render_readme(existing, reports.validate_results(result))
    assert updated.startswith(prefix + "<!-- SCALEUP_RESULT_START -->")
    assert updated.endswith("<!-- SCALEUP_RESULT_END -->" + suffix)
    assert "OLD AUTO RESULT" not in updated
    assert updated.count("<!-- SCALEUP_RESULT_START -->") == 1
    assert updated.count("<!-- SCALEUP_RESULT_END -->") == 1


def test_readme_findings_separate_primary_comparison_and_baseline_paragraphs(result):
    existing = "Prefix\n<!-- SCALEUP_RESULT_START -->\nold\n<!-- SCALEUP_RESULT_END -->\nSuffix"
    rendered = reports.render_readme(existing, reports.validate_results(result))
    block = rendered.split("<!-- SCALEUP_RESULT_START -->", 1)[1].split("<!-- SCALEUP_RESULT_END -->", 1)[0]
    paragraphs = [paragraph.strip() for paragraph in block.split("\n\n") if paragraph.strip()]
    heading = next(i for i, paragraph in enumerate(paragraphs) if "Findings from 5,000 groups" in paragraph)
    primary = next(i for i, paragraph in enumerate(paragraphs) if "**Layer 14:" in paragraph)
    comparison = next(i for i, paragraph in enumerate(paragraphs) if "Ensemble minus layer 14:" in paragraph)
    baselines = next(i for i, paragraph in enumerate(paragraphs) if "Character-only TF-IDF achieved" in paragraph)
    pending = next(i for i, paragraph in enumerate(paragraphs) if "Human item review" in paragraph)
    assert heading < primary < comparison < baselines < pending
    assert paragraphs[heading].startswith("#")
    bold_spans = re.findall(r"\*\*(.*?)\*\*", paragraphs[primary])
    assert any("70.00%" in span and "74.00%" in span for span in bold_spans)
    assert block.count("Layer 14 achieved") <= 1
    assert block.count("70.00%") == 1
    assert block.count("74.00%") == 1
    assert "Character-only" not in paragraphs[primary]
    assert "Layer 14 achieved" not in paragraphs[comparison]
    assert "Layer 14 achieved" not in paragraphs[baselines]
    assert len(paragraphs[pending].split()) < 35
    assert "Full report and all 28 layers" in block
    assert "Ten-minute meeting brief" in block


def english_words(text):
    return re.findall(r"\b[A-Za-z]+(?:['’-][A-Za-z]+)*\b", text)


@pytest.mark.parametrize("case", ["lower_surface", "dominant_surface", "comparable_surface", "weak_ordering"])
def test_meeting_interpretation_is_concise_conditional_and_does_not_repeat_metrics(result, case):
    if case == "dominant_surface":
        result["secondary"]["character_tfidf"] = metric(990)
    elif case == "comparable_surface":
        result["secondary"]["negative_response_token_length"] = metric(730)
    elif case == "weak_ordering":
        result["layers"][13] = metric(510, layer=14, ci=[.48, .54])
        result["primary"]["layer14"] = copy.deepcopy(result["layers"][13])
        result["primary"]["equal_28_layer_ensemble"] = metric(520, ci=[.49, .55])
        result["ensemble_minus_layer14"] = {"estimate": .01, "ci95": [-.02, .04]}
    safe = reports.validate_results(result)
    meaning = reports.meeting_interpretation(safe)
    assert 80 <= len(english_words(meaning)) <= 110
    assert "95% CI" not in meaning
    assert "Layer 14 achieved" not in meaning
    for primary in safe["primary"].values():
        assert f"{primary['estimate'] * 100:.2f}%" not in meaning
    lowered = meaning.lower()
    assert "human" in lowered and "pending" in lowered
    assert "sdt" in lowered
    if case == "lower_surface":
        assert "readout point estimates exceed surface baselines" in lowered
        assert "descriptive" in lowered
    elif case in {"dominant_surface", "comparable_surface"}:
        assert "added value" in lowered
        assert "no " in lowered or "not " in lowered
    else:
        assert "neither fixed readout establishes above-chance ordering" in lowered
    rendered = reports.render_meeting_brief(safe)
    assert meaning in rendered
    assert " ".join(reports.conclusion(safe).values()) not in rendered
    assert "{{" not in rendered
    speech = rendered.split("## 0 to 1 minute", 1)[1].split("## 备用公式", 1)[0]
    assert len(english_words(speech)) < 1350


@pytest.mark.parametrize("existing", [
    "# README without markers\n",
    "<!-- SCALEUP_RESULT_START -->\nmissing end\n",
    "missing start\n<!-- SCALEUP_RESULT_END -->\n",
    "<!-- SCALEUP_RESULT_END -->\nwrong order\n<!-- SCALEUP_RESULT_START -->\n",
    "<!-- SCALEUP_RESULT_START -->\n<!-- SCALEUP_RESULT_START -->\n<!-- SCALEUP_RESULT_END -->\n",
    "<!-- SCALEUP_RESULT_START -->\n<!-- SCALEUP_RESULT_END -->\n<!-- SCALEUP_RESULT_END -->\n",
])
def test_readme_rejects_missing_duplicate_or_reversed_markers_without_any_write(tmp_path, result, existing):
    safe = reports.validate_results(result)
    with pytest.raises(ValueError):
        reports.render_readme(existing, safe)
    run = write_run(tmp_path, result)
    readme = tmp_path / "README.md"
    readme.write_text(existing, encoding="utf-8")
    output = tmp_path / "public"
    output.mkdir()
    sentinel = output / "SUMMARY_5000.json"
    sentinel.write_text("existing public result must survive", encoding="utf-8")
    with pytest.raises(ValueError):
        reports.build_report(run, output, readme_path=readme)
    assert readme.read_text(encoding="utf-8") == existing
    assert sentinel.read_text(encoding="utf-8") == "existing public result must survive"
    assert list(output.iterdir()) == [sentinel]


def test_build_updates_readme_using_the_same_pure_renderer(tmp_path, result):
    run = write_run(tmp_path, result)
    existing = "Keep prefix\n<!-- SCALEUP_RESULT_START -->\nold\n<!-- SCALEUP_RESULT_END -->\nKeep suffix\n"
    readme = tmp_path / "README.md"
    readme.write_text(existing, encoding="utf-8")
    summary = reports.build_report(run, tmp_path / "public", readme_path=readme)
    assert readme.read_text(encoding="utf-8") == reports.render_readme(existing, summary)
