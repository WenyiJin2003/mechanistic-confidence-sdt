"""Publish aggregate reports from a complete cached 5,000-pair evaluation.

This module never imports extraction, opens response text or hidden states, fits
a model, makes a network call, or changes the input run. Unknown JSON fields are
discarded; arbitrary strings from a private result are never rendered.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import re
import struct
import zlib

BASE = Path(__file__).resolve().parents[1]
REPO = BASE.parents[1]
README_START = "<!-- SCALEUP_RESULT_START -->"
README_END = "<!-- SCALEUP_RESULT_END -->"
STAT = "development_candidate_label_diagnostic_not_human_validated"
LAYERS = list(range(1, 29))
SECONDARY = {
    "character_tfidf": "Character TF-IDF paired logistic",
    "negative_mean_token_nll": "Negative mean response-token NLL",
    "negative_response_token_length": "Negative response-token length",
    "negative_response_word_length": "Negative response-word length",
    "constant_tie": "Constant tie",
    "final_response_token_layer14": "Final response token, layer 14",
    "mean_difference_layer14": "Mean-difference readout, layer 14",
    "mean_difference_equal_28_ensemble": "Mean-difference equal 28-layer ensemble",
}
LEAKAGE = {
    "group_disjoint": True, "canary_forced_train": True,
    "feature_scaling_train_only": True, "score_scaling_train_only": True,
    "tfidf_vocabulary_train_only": True, "test_sign_or_layer_selection": False,
}
LIMITATIONS = [
    "Human item review is pending; content preservation is uncertified.",
    "Writer-supplied confident/hesitant labels can be decoded through wording shortcuts shared across train and test.",
    "Synthetic UltraChat source answers are not verified factual gold.",
    "Exact normalized duplicates are grouped; approximate duplicates are not detected.",
    "Bootstrap intervals condition on this fitted training set; probes are not refitted in bootstrap draws.",
    "The 28-layer display is descriptive and has no multiple-comparison correction; it does not select a winning layer.",
    "Five shuffled-orientation fits are descriptive controls, not a formal permutation test or p-value.",
    "Results do not establish factual truth or correctness, calibrated uncertainty, intrinsic model confidence, semantic entropy, mechanistic validity, or causal control.",
    "No SDT training was performed; these results do not validate a signal or objective for SDT training.",
]
METHODOLOGY = {
    "data": "Exact frozen prefix of 5,000 cached UltraChat/Haiku triplets; every candidate retained.",
    "supervision": "Writer-supplied confident/hesitant rewrite labels; human review pending.",
    "model": "Qwen/Qwen2.5-1.5B-Instruct",
    "model_revision": "989aa7980e4cf806f80c7fef2b1adb7bc71aa306",
    "split_seed": 20261020,
    "split": "Deterministic SHA256-ordered 80/20 independent source/duplicate-group split; previously inspected canary groups forced into training.",
    "grouping": "Transitive union of source identity, group identity, exact NFKC/casefold/whitespace-normalized question and original-answer duplicates.",
    "representation": "Teacher-forced response-token mean states at all 28 hidden-state indices; layer 28 follows final RMSNorm.",
    "pooling": "Prompt, padding, and turn-marker tokens excluded; original answers retained without additional forwards.",
    "precision": "Pinned local, unquantized model; accelerator forward precision FP16 (CPU fallback FP32); stored states FP16.",
    "token_limits": "At most 1,024 input tokens and 512 response tokens; overlength candidates fail before forwarding, without truncation.",
    "batching": "One source pair (two responses) per right-padded forward batch, with explicit attention masks; pairs are ordered by length for throughput.",
    "readout": "A separately fitted L2 logistic readout per layer, C=0.01, no intercept, lbfgs, at most 2,000 iterations; mirrored confident-minus-hesitant feature differences with weight 0.5 each.",
    "feature_scaling": "Feature means and standard deviations fitted on both responses of training pairs only.",
    "fixed_comparison": "Predeclared layer 14 versus the equal mean of 28 layer scores standardized with their training-response means and population standard deviations; near-zero score variance maps to zero.",
    "test_selection": "No test-based layer, sign, hyperparameter, or threshold selection.",
    "metric": "Mean across held-out groups of confident score greater than hesitant score; exact ties count 0.5. Here each held-out group contains one pair.",
    "intervals": "95% percentile intervals from 2,000 held-out-group bootstrap draws; ensemble-minus-layer-14 uses the same resampled groups for both readouts.",
    "text_baseline": "Training-only char_wb TF-IDF vocabulary, ngrams 3–5, min_df=2, max_features=20,000, sublinear TF; mirrored weighted paired logistic, C=0.01, no intercept, liblinear, at most 2,000 iterations.",
    "length_and_nll": "Fixed negative token length, word length, and shifted mean response-token NLL; signs are not selected from test performance.",
    "mean_difference": "Training-standardized features projected onto the mean training confident-minus-hesitant feature vector; ensemble uses training-only score standardization.",
    "nulls": "Five fits with shuffled training-pair orientation and unchanged test labels; identical-prompt state and seven-token right-padding invariance checks.",
    "scope": "Cached evaluation and CPU readout fitting only; no new generation, model download, language-model training, SDT objective, or steering.",
}


def number(value, label, low=0.0, high=1.0):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not low <= value <= high:
        raise ValueError(f"Invalid aggregate numeric field: {label}")
    return float(value)


def integer(value, label, expected=None):
    if type(value) is not int or value < 0 or (expected is not None and value != expected):
        raise ValueError(f"Invalid aggregate count: {label}")
    return value


def metric(value, label):
    if not isinstance(value, dict):
        raise ValueError(f"Missing aggregate metric: {label}")
    result = {"estimate": number(value.get("estimate"), label)}
    bounds = value.get("ci95")
    if not isinstance(bounds, (list, tuple)) or len(bounds) != 2:
        raise ValueError(f"Invalid interval: {label}")
    result["ci95"] = [number(bound, label) for bound in bounds]
    if not result["ci95"][0] <= result["estimate"] <= result["ci95"][1]:
        raise ValueError(f"Interval does not contain estimate: {label}")
    for name in ("groups", "pairs"):
        result[name] = integer(value.get(name), label + "." + name, 1000)
    for name in ("wins", "ties", "losses"):
        result[name] = integer(value.get(name), label + "." + name)
    if result["wins"] + result["ties"] + result["losses"] != result["pairs"]:
        raise ValueError(f"Pair counts do not sum: {label}")
    expected = (result["wins"] + 0.5 * result["ties"]) / result["pairs"]
    if not math.isclose(result["estimate"], expected, abs_tol=1e-12, rel_tol=0):
        raise ValueError(f"Ordering estimate disagrees with counts: {label}")
    return result


def validate_results(payload):
    """Fail closed and construct a fresh, aggregate-only allowlisted result."""
    if not isinstance(payload, dict) or payload.get("status") != "complete":
        raise ValueError("A complete evaluation is required before publishing")
    if payload.get("scientific_status") != STAT:
        raise ValueError("Unexpected scientific status")
    safe = {"status": "complete", "scientific_status": STAT}
    for name in ("human_review_completed", "content_preservation_certified"):
        if payload.get(name) is not False:
            raise ValueError("Human review must remain explicitly pending and content preservation uncertified")
        safe[name] = False
    for name, count in (("candidate_pairs", 5000), ("train_pairs", 4000), ("test_pairs", 1000),
                        ("train_groups", 4000), ("test_groups", 1000)):
        safe[name] = integer(payload.get(name), name, count)
    primary = payload.get("primary", {})
    if not isinstance(primary, dict):
        raise ValueError("Missing predeclared comparison")
    safe["primary"] = {key: metric(primary.get(key), key)
                       for key in ("layer14", "equal_28_layer_ensemble")}
    layers = payload.get("layers")
    if not isinstance(layers, list) or len(layers) != 28:
        raise ValueError("All 28 layers are required")
    by_layer = {}
    for row in layers:
        if not isinstance(row, dict) or type(row.get("layer")) is not int or row["layer"] not in LAYERS or row["layer"] in by_layer:
            raise ValueError("Expected each of the 28 layer indices exactly once")
        by_layer[row["layer"]] = {"layer": row["layer"], **metric(row, "layer")}
    safe["layers"] = [by_layer[layer] for layer in LAYERS]
    if {k: v for k, v in safe["layers"][13].items() if k != "layer"} != safe["primary"]["layer14"]:
        raise ValueError("Layer-14 primary and layer table disagree")
    delta = payload.get("ensemble_minus_layer14", {})
    if not isinstance(delta, dict):
        raise ValueError("Missing paired ensemble-minus-layer-14 interval")
    estimate = number(delta.get("estimate"), "paired difference", -1, 1)
    bounds = delta.get("ci95")
    if not isinstance(bounds, (list, tuple)) or len(bounds) != 2:
        raise ValueError("Missing paired difference interval")
    bounds = [number(value, "paired difference interval", -1, 1) for value in bounds]
    if not bounds[0] <= estimate <= bounds[1] or not math.isclose(
            estimate, safe["primary"]["equal_28_layer_ensemble"]["estimate"] - safe["primary"]["layer14"]["estimate"],
            abs_tol=1e-12, rel_tol=0):
        raise ValueError("Paired difference disagrees with primary estimates or interval")
    safe["ensemble_minus_layer14"] = {"estimate": estimate, "ci95": bounds}
    secondary = payload.get("secondary", {})
    if not isinstance(secondary, dict):
        raise ValueError("Missing baseline metrics")
    safe["secondary"] = {key: metric(secondary.get(key), key) for key in SECONDARY}
    tie = safe["secondary"]["constant_tie"]
    if tie["ties"] != 1000 or tie["ci95"] != [0.5, 0.5]:
        raise ValueError("Constant-tie negative control is not exactly 0.5")
    nulls = payload.get("shuffled_training_orientation", {})
    if not isinstance(nulls, dict) or nulls.get("repeats") != 5 or type(nulls.get("repeats")) is not int:
        raise ValueError("Five shuffled-training-orientation controls are required")
    safe_nulls = {"repeats": 5}
    for name in ("descriptive_not_formal_p_value", "training_pair_orientation_only", "unchanged_test_labels"):
        if nulls.get(name) is not True:
            raise ValueError("Shuffled controls must remain descriptive and preserve test labels")
        safe_nulls[name] = True
    for name in ("layer14", "equal_28_layer_ensemble"):
        values = nulls.get(name)
        if not isinstance(values, list) or len(values) != 5:
            raise ValueError("Missing shuffled-control rates")
        safe_nulls[name] = [number(value, "shuffled rate") for value in values]
    safe["shuffled_training_orientation"] = safe_nulls
    controls = payload.get("leakage_controls", {})
    if not isinstance(controls, dict) or any(controls.get(k) is not v for k, v in LEAKAGE.items()):
        raise ValueError("Required leakage controls were not affirmed")
    safe["leakage_controls"] = dict(LEAKAGE)
    safe["prompt_control_max_abs_difference"] = number(payload.get("prompt_control_max_abs_difference"), "prompt control", 0, .005)
    return safe


def ordering_finding(result):
    a, b = result["primary"]["layer14"], result["primary"]["equal_28_layer_ensemble"]
    if a["ci95"][0] > .5 and b["ci95"][0] > .5:
        return "Both predeclared readouts distinguish the writer-supplied confident and hesitant rewrites above the constant-tie level in held-out groups."
    if a["ci95"][0] > .5 or b["ci95"][0] > .5:
        name = "Layer 14" if a["ci95"][0] > .5 else "The equal 28-layer ensemble"
        return f"{name} distinguishes writer-supplied rewrite labels above the constant-tie level; the other predeclared readout does not establish above-chance ordering."
    return "The predeclared readouts do not establish above-chance ordering of writer-supplied confident and hesitant rewrites in held-out groups."


def conclusion(result):
    a, b = result["primary"]["layer14"], result["primary"]["equal_28_layer_ensemble"]
    ordering = (f"Layer 14 achieved {show_metric(a)} and the equal 28-layer ensemble achieved {show_metric(b)} "
                "on 1,000 held-out groups. " + ordering_finding(result))
    delta = result["ensemble_minus_layer14"]["ci95"]
    if delta[0] > 0:
        comparison = "The equal 28-layer ensemble improves held-out ordering over layer 14 under the paired group-bootstrap interval."
    elif delta[1] < 0:
        comparison = "Layer 14 orders more pairs correctly than the equal 28-layer ensemble under the paired group-bootstrap interval."
    else:
        comparison = "The paired group-bootstrap interval does not resolve an advantage for the ensemble over layer 14; this is not an equivalence test."
    comparison = "Ensemble minus layer 14: " + show_delta(result["ensemble_minus_layer14"]) + ". " + comparison
    text = result["secondary"]["character_tfidf"]
    token = result["secondary"]["negative_response_token_length"]
    word = result["secondary"]["negative_response_word_length"]
    strongest = max((text, token, word), key=lambda value: value["estimate"])
    interpretation = (f"Character-only TF-IDF achieved {pct(text['estimate'])}; fixed negative token length achieved {pct(token['estimate'])} "
                      f"and fixed negative word length achieved {pct(word['estimate'])}. ")
    if strongest["estimate"] >= max(a["estimate"], b["estimate"]):
        interpretation += "A surface baseline matches or exceeds both predeclared point estimates. No added value of hidden-state readouts over these surface cues is demonstrated. Baseline comparisons are descriptive; no paired baseline interval is reported."
    elif max(a["estimate"], b["estimate"]) - strongest["estimate"] <= .02 + 1e-12:
        interpretation += "The strongest surface baseline is within two percentage points of the better predeclared readout, a descriptively comparable ordering rate. No added value over these surface cues is demonstrated. Baseline comparisons are descriptive; no paired baseline interval is reported."
    elif min(a["estimate"], b["estimate"]) > strongest["estimate"]:
        interpretation += "Both predeclared readouts have higher point estimates than these surface baselines. These comparisons are descriptive; no paired baseline interval establishes added value."
    else:
        interpretation += "The predeclared readouts do not both exceed the strongest surface baseline. These comparisons are descriptive; no paired baseline interval establishes added value."
    if strongest["ci95"][0] > .5:
        interpretation += " Writer labels are recoverable from surface cues in this sample."
    interpretation += " This is evidence about expressed certainty in a shared rewrite recipe. Wording shortcuts can explain high ordering rates; it is not proof of intrinsic model confidence, answer correctness, or a valid SDT training objective."
    if any(max(result["shuffled_training_orientation"][key]) >= result["primary"][key]["estimate"]
           for key in ("layer14", "equal_28_layer_ensemble")):
        interpretation += " At least one shuffled-orientation run reaches or exceeds its corresponding fitted readout, which weakens a training-label-specific interpretation; five runs cannot provide a formal p-value."
    return {"ordering": ordering, "ensemble_comparison": comparison, "interpretation": interpretation}


def meeting_interpretation(result):
    """A short spoken interpretation; the template already gives rates and CIs."""
    a, b = result["primary"]["layer14"], result["primary"]["equal_28_layer_ensemble"]
    established = sum(value["ci95"][0] > .5 for value in (a, b))
    if established == 2:
        text = "Both fixed readouts recover the writer's certainty labels in held-out pairs. "
    elif established == 1:
        text = "Only one fixed readout clearly exceeds chance; the other readout's ordering remains uncertain. "
    else:
        text = "Neither fixed readout establishes above-chance ordering of the writer's certainty labels. "
    surface = max(result["secondary"][key]["estimate"] for key in (
        "character_tfidf", "negative_response_token_length", "negative_response_word_length"))
    if surface >= max(a["estimate"], b["estimate"]):
        text += "Surface cues perform at least as well descriptively, so the hidden states show no added value over those cues. "
    elif max(a["estimate"], b["estimate"]) - surface <= .02 + 1e-12:
        text += "Surface cues give a descriptively comparable ordering rate, so no added value is established. "
    elif min(a["estimate"], b["estimate"]) > surface:
        text += "Readout point estimates exceed surface baselines, but this descriptive comparison has no paired uncertainty interval. "
    else:
        text += "The strongest surface cues exceed one readout; no paired interval establishes added value. "
    text += ("This measures expressed certainty under one rewrite recipe, not intrinsic confidence or answer correctness. "
             "Human item review and content-preservation checks remain pending; a wording shortcut could explain any apparent separation between the supplied labels. "
             "No SDT training or improved learning has been demonstrated. We need independent wording, content, and transfer checks before considering a training intervention.")
    if any(max(result["shuffled_training_orientation"][key]) >= result["primary"][key]["estimate"]
           for key in ("layer14", "equal_28_layer_ensemble")):
        text += " High shuffled controls further weaken training-label-specific claims."
    return text


def pct(value):
    return f"{100 * value:.2f}%"


def show_metric(value):
    return f"{pct(value['estimate'])} (95% CI {pct(value['ci95'][0])}–{pct(value['ci95'][1])})"


def show_delta(value):
    return f"{100 * value['estimate']:+.2f} percentage points (paired 95% CI {100 * value['ci95'][0]:+.2f} to {100 * value['ci95'][1]:+.2f})"


def render_report(result):
    claim = conclusion(result)
    lines = ["# 5,000-group expressed-certainty diagnostic", "", claim["ordering"], "",
             claim["ensemble_comparison"], "", claim["interpretation"], "",
             "Human item review remains pending and content preservation is uncertified. These are candidate writer labels; the source answers are synthetic and not factual gold.", "",
             "## Predeclared comparison", "", "5,000 independent groups / candidate pairs: 4,000 training groups and 1,000 held-out groups. No candidate pair was dropped.", "",
             "| Readout | Held-out ordering rate | Wins / ties / losses |", "| --- | --- | --- |"]
    for key, label in (("layer14", "Layer 14"), ("equal_28_layer_ensemble", "Equal 28-layer ensemble")):
        value = result["primary"][key]
        lines.append(f"| {label} | {show_metric(value)} | {value['wins']} / {value['ties']} / {value['losses']} |")
    lines.extend(["", "Ensemble minus layer 14: **" + show_delta(result["ensemble_minus_layer14"]) + "**. The interval uses paired resampling of held-out groups, not a comparison of the two marginal intervals.", "",
                  "## All 28 layers", "", "![All 28 layers, predeclared layer 14, ensemble, and character TF-IDF](ALL_28_LAYERS.png)", "",
                  "Layer 14 and the equal ensemble were fixed before test-score exposure. The highest plotted layer is descriptive; none of these 28 intervals is a family-wise simultaneous interval.", "",
                  "| Hidden-state index | Ordering rate | 95% group-bootstrap CI | Wins / ties / losses |",
                  "| --- | --- | --- | --- |"])
    for value in result["layers"]:
        label = f"{value['layer']} (predeclared)" if value["layer"] == 14 else str(value["layer"])
        lines.append(f"| {label} | {pct(value['estimate'])} | {pct(value['ci95'][0])}–{pct(value['ci95'][1])} | {value['wins']} / {value['ties']} / {value['losses']} |")
    lines.extend(["", "## Baselines and controls", "", "| Readout or fixed control | Held-out ordering rate |", "| --- | --- |"])
    for key, label in SECONDARY.items():
        lines.append(f"| {label} | {show_metric(result['secondary'][key])} |")
    lines.extend(["", "The text and length baselines test how much the shared rewrite recipe can be recovered from surface form. Differences from these baselines are descriptive; no paired interval for those comparisons is claimed.", "",
                  "| Shuffled training orientation | Layer 14 | Equal 28-layer ensemble |", "| --- | --- | --- |"])
    nulls = result["shuffled_training_orientation"]
    for index in range(5):
        lines.append(f"| Run {index + 1} | {pct(nulls['layer14'][index])} | {pct(nulls['equal_28_layer_ensemble'][index])} |")
    lines.extend(["", "These five fits shuffle training-pair orientation only; test labels remain fixed. They are descriptive controls, not formal permutation p-values.", "",
                  f"Identical-prompt states: maximum absolute paired difference {result['prompt_control_max_abs_difference']:.6g} (required ≤0.005). The upstream evaluator also verifies the frozen seven-token right-padding audit: maximum state difference ≤0.02 and sequence-NLL difference ≤0.05. The report builder does not rerun model forwards.", "",
                  "## Exact method", ""])
    for label, text in METHODOLOGY.items():
        lines.append(f"- {label.replace('_', ' ').capitalize()}: {text}")
    lines.extend(["", "The bootstrap seed is 20261020 plus the zero-based layer index for layer intervals, +40 for the ensemble, +41 for the paired difference, and +100 plus baseline insertion index for secondary intervals. Shuffled orientations use seed +901; their reported point estimates use 100 bootstrap draws internally, without reporting intervals.", "",
                  "## Limits on interpretation", ""])
    lines.extend("- " + item for item in LIMITATIONS)
    lines.extend(["", "## Reproduction and publication boundary", "",
                  "Run the cached evaluator only after extraction has completed, then run `src/build_reports.py` from this experiment. The builder accepts only a complete evaluation with exactly 5,000 candidates, 4,000 training groups/pairs, 1,000 held-out groups/pairs, all 28 layers, pending human review, and internally consistent aggregate counts. It performs no generation, downloads, readout fitting, or model forwards.", "",
                  "Published files contain aggregate metrics and static methodological text only. Private identifiers, per-item scores, response text, source paths, credentials, arbitrary input strings, and fitted arrays are excluded. Non-image PNG metadata is removed while preserving the plotted image.", ""])
    return "\n".join(lines)


def render_meeting_brief(result, template_path=None):
    """Fill the parent-owned static speaking-note template without private text."""
    template = Path(template_path) if template_path else BASE / "src/meeting_brief_template.md"
    if template.exists():
        text = template.read_text(encoding="utf-8")
    elif template_path is not None:
        raise FileNotFoundError("Meeting brief template is missing")
    else:
        text = "# Ten-minute meeting brief\n\n{{RESULT_INTERPRETATION}}\n\nLayer 14: {{L14}}\n\nEqual ensemble: {{ENSEMBLE}}\n\nPaired difference: {{DELTA}}\n\nCharacter TF-IDF: {{TEXT}}\n\nNegative token length: {{LENGTH}}\n"
    replacements = {
        "L14": show_metric(result["primary"]["layer14"]),
        "ENSEMBLE": show_metric(result["primary"]["equal_28_layer_ensemble"]),
        "TEXT": show_metric(result["secondary"]["character_tfidf"]),
        "LENGTH": show_metric(result["secondary"]["negative_response_token_length"]),
        "DELTA": show_delta(result["ensemble_minus_layer14"]),
        "RESULT_INTERPRETATION": meeting_interpretation(result),
    }
    for key, value in replacements.items():
        text = text.replace("{{" + key + "}}", value)
    if re.search(r"\{\{.*?\}\}", text, flags=re.DOTALL):
        raise ValueError("Unresolved meeting brief template placeholder")
    return text.rstrip() + "\n"


def render_readme(text, result):
    """Replace exactly the parent-owned result block; preserve its surroundings."""
    if text.count(README_START) != 1 or text.count(README_END) != 1:
        raise ValueError("README requires exactly one start marker and one end marker")
    start, end = text.index(README_START), text.index(README_END)
    if end < start:
        raise ValueError("README result markers are out of order")
    claim = conclusion(result)
    block = "\n\n### Findings from 5,000 groups\n\n"
    block += "**Layer 14: " + show_metric(result["primary"]["layer14"]) + "; "
    block += "equal 28-layer ensemble: " + show_metric(result["primary"]["equal_28_layer_ensemble"]) + ".** "
    block += "These ordering rates use 4,000 training groups and 1,000 held-out groups. " + ordering_finding(result) + "\n\n"
    block += claim["ensemble_comparison"] + "\n\n"
    block += claim["interpretation"] + "\n\n"
    block += "**Human item review is pending; content preservation is uncertified.**\n\n"
    block += "[Full report and all 28 layers](experiments/information_chat_scaleup_v1/results/RESULTS_5000.md) · "
    block += "[Aggregate JSON](experiments/information_chat_scaleup_v1/results/SUMMARY_5000.json) · "
    block += "[Ten-minute meeting brief](experiments/information_chat_scaleup_v1/reports/MEETING_BRIEF_10MIN.md)\n\n"
    return text[:start + len(README_START)] + block + text[end:]


def safe_png_bytes(data):
    """Preserve PNG image chunks, removing textual/EXIF/application metadata."""
    signature = b"\x89PNG\r\n\x1a\n"
    if not data.startswith(signature):
        raise ValueError("All-layer plot must be a PNG")
    kept, offset, names = [signature], 8, []
    allowed = {b"IHDR", b"PLTE", b"IDAT", b"IEND", b"tRNS", b"gAMA", b"cHRM", b"sRGB", b"pHYs"}
    while offset < len(data):
        if offset + 12 > len(data):
            raise ValueError("Incomplete all-layer PNG")
        length = struct.unpack(">I", data[offset:offset + 4])[0]
        end = offset + 12 + length
        if end > len(data):
            raise ValueError("Incomplete all-layer PNG chunk")
        kind, content = data[offset + 4:offset + 8], data[offset + 8:end - 4]
        if zlib.crc32(kind + content) & 0xffffffff != struct.unpack(">I", data[end - 4:end])[0]:
            raise ValueError("All-layer PNG checksum mismatch")
        if not names and kind != b"IHDR":
            raise ValueError("All-layer PNG header missing")
        if kind not in allowed and not kind[0] & 32:
            raise ValueError("Unknown critical PNG chunk")
        if kind in allowed:
            kept.append(data[offset:end])
        names.append(kind)
        offset = end
        if kind == b"IEND":
            break
    if offset != len(data) or b"IDAT" not in names or names[-1:] != [b"IEND"] or names.count(b"IHDR") != 1:
        raise ValueError("Invalid or incomplete all-layer PNG")
    return b"".join(kept)


def audit_predictions(path, result):
    """Optionally verify cached pair arithmetic; publish none of the arrays."""
    import numpy as np
    with np.load(path, allow_pickle=False) as cache:
        try:
            layers, ensemble, groups = cache["layer_scores"], cache["equal_scores"], cache["group_ids"]
        except (KeyError, ValueError) as error:
            raise ValueError("Prediction cache is missing required safe-check arrays") from error
        if layers.shape != (1000, 2, 28) or ensemble.shape != (1000, 2) or groups.shape != (1000,) or len(np.unique(groups)) != 1000:
            raise ValueError("Prediction cache shape/group count mismatch")
        if not np.isfinite(layers).all() or not np.isfinite(ensemble).all():
            raise ValueError("Prediction cache contains nonfinite scores")
        def check(scores, target):
            delta = scores[:, 0] - scores[:, 1]
            if (int((delta > 0).sum()), int((delta == 0).sum()), int((delta < 0).sum())) != (target["wins"], target["ties"], target["losses"]):
                raise ValueError("Prediction cache disagrees with aggregate pair counts")
        for index, value in enumerate(result["layers"]):
            check(layers[:, :, index], value)
        check(ensemble, result["primary"]["equal_28_layer_ensemble"])
        if "scaled_layer_scores" in cache:
            scaled = cache["scaled_layer_scores"]
            if scaled.shape != layers.shape or not np.isfinite(scaled).all() or not np.allclose(scaled.mean(2), ensemble, rtol=1e-12, atol=1e-12):
                raise ValueError("Prediction ensemble is not the equal mean of scaled layer scores")
        for key in SECONDARY:
            if key in cache:
                values = cache[key]
                if values.shape != (1000, 2) or not np.isfinite(values).all():
                    raise ValueError("Prediction baseline has invalid shape or scores")
                check(values, result["secondary"][key])


def build_report(run_dir, output_dir=None, *, predictions_path=None, brief_output_dir=None, readme_path=None):
    """Validate first, then write only deterministic public aggregate artifacts."""
    run = Path(run_dir)
    output = Path(output_dir) if output_dir is not None else BASE / "results"
    brief_output = Path(brief_output_dir) if brief_output_dir is not None else (BASE / "reports" if output_dir is None else output / "reports")
    readme = Path(readme_path) if readme_path is not None else (REPO / "README.md" if output_dir is None else None)
    input_result = (run / "RESULTS.json").read_bytes()
    result = validate_results(json.loads(input_result))
    input_plot = (run / "ALL_28_LAYERS.png").read_bytes()
    plot = safe_png_bytes(input_plot)
    if predictions_path is not None:
        audit_predictions(predictions_path, result)
    summary = {"schema_version": "haiku5000-public-summary-v1", **result,
               "conclusion": conclusion(result), "methodology": dict(METHODOLOGY),
               "limitations": list(LIMITATIONS), "predictions_audited": predictions_path is not None,
               "contains_per_item_data": False, "human_validated": False}
    artifacts = {
        output / "RESULTS_5000.md": render_report(summary).encode("utf-8"),
        output / "SUMMARY_5000.json": (json.dumps(summary, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8"),
        output / "ALL_28_LAYERS.png": plot,
        brief_output / "MEETING_BRIEF_10MIN.md": render_meeting_brief(summary).encode("utf-8"),
    }
    original_readme = readme.read_bytes() if readme is not None else None
    updated_readme = render_readme(original_readme.decode("utf-8"), summary).encode("utf-8") if readme is not None else None
    if input_result != (run / "RESULTS.json").read_bytes() or input_plot != (run / "ALL_28_LAYERS.png").read_bytes():
        raise ValueError("Cached inputs changed while constructing reports")
    for path, content in artifacts.items():
        if path.resolve().is_relative_to(run.resolve()):
            raise ValueError("Public outputs must not change the private run")
        if path.exists() and path.read_bytes() != content:
            raise FileExistsError("A different public report already exists; preserve it for explicit review")
    if readme is not None:
        if readme.resolve().is_relative_to(run.resolve()):
            raise ValueError("README output must not change the private run")
        if readme.read_bytes() != original_readme:
            raise ValueError("README changed while constructing reports")
    for path, content in artifacts.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            with path.open("xb") as handle:
                handle.write(content)
    if readme is not None and updated_readme != original_readme:
        readme.write_bytes(updated_readme)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, default=BASE / "private_data/run_5000_v1")
    parser.add_argument("--output-dir", type=Path, default=BASE / "results")
    parser.add_argument("--brief-output-dir", type=Path, default=BASE / "reports")
    parser.add_argument("--readme", type=Path, default=REPO / "README.md")
    parser.add_argument("--predictions", type=Path, help="Optional read-only arithmetic audit of the cached prediction archive")
    args = parser.parse_args()
    summary = build_report(args.run_dir, args.output_dir, predictions_path=args.predictions,
                           brief_output_dir=args.brief_output_dir, readme_path=args.readme)
    print(json.dumps({"status": "complete", "candidate_pairs": summary["candidate_pairs"],
                      "contains_per_item_data": False, "human_review_completed": False}))


if __name__ == "__main__":
    main()
