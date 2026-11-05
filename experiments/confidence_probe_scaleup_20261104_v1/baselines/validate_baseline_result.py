#!/usr/bin/env python3
"""Provider-free integrity validation for the completed baseline result."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULT = HERE / "BASELINE_COMPARISON_RESULTS_AUTHENTICATED.json"
PROBE = HERE.parent / "results_primary_v1/PROBE_LEARNING_CURVE_RESULTS.json"
OUTPUT = HERE / "BASELINE_COMPARISON_VALIDATION_AUTHENTICATED.json"
SIZES = ("200", "500", "920")
TEXT = (
    "char_wb3_5__answer_only", "char_wb3_5__system_question_answer",
    "char3_5__answer_only", "char3_5__system_question_answer",
    "word1_2__answer_only", "word1_2__system_question_answer",
)
LENGTH = (
    "negative_response_token_length", "negative_response_word_length",
    "negative_response_character_length",
)
COUNTS = {"dev": 156, "internal_test": 193, "external_cf3": 113}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_metric(metric: dict, count: int, label: str) -> None:
    assert metric["pairs"] == count, label
    assert metric["wins"] + metric["ties"] + metric["losses"] == count, label
    expected = (metric["wins"] + 0.5 * metric["ties"]) / count
    assert abs(metric["paired_accuracy"] - expected) < 1e-15, label
    interval = metric["grouped_bootstrap_95_ci"]
    assert interval is not None and len(interval) == 2 and interval[0] <= interval[1], label


def main() -> int:
    if OUTPUT.exists():
        raise FileExistsError(OUTPUT)
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    probe = json.loads(PROBE.read_text(encoding="utf-8"))
    assert result["status"] == "complete"
    assert tuple(result["train_sizes"]) == (200, 500, 920)
    assert tuple(result["text_method_order"]) == TEXT
    assert tuple(result["length_method_order"]) == LENGTH
    assert result["denominators"]["missing"] == 0
    assert result["denominators"]["excluded"] == 0
    assert result["runtime"]["qwen_forwards"] == 0
    assert result["runtime"]["provider_calls"] == 0

    for method in LENGTH:
        for split, count in COUNTS.items():
            check_metric(result["length_controls"][method][split], count, f"{method}/{split}")

    for size in SIZES:
        curve = result["learning_curves"][size]
        assert set(curve["text_models"]) == set(TEXT)
        for method in TEXT:
            for split, count in COUNTS.items():
                check_metric(curve["text_models"][method][split], count,
                             f"{size}/{method}/{split}")
        assert curve["dev_designated_strongest_text_comparator"]["method"] in TEXT
        assert set(curve["probe_minus_all_baselines_on_internal_test"]) == {
            "layer14", "equal28"
        }
        for probe_name in ("layer14", "equal28"):
            assert set(curve["probe_minus_all_baselines_on_internal_test"][probe_name]) == (
                set(TEXT) | set(LENGTH)
            )
        for local_name, frozen_name in (("layer14", "primary_layer"), ("equal28", "ensemble")):
            observed = curve["probe_internal_test_metrics_recomputed_from_frozen_fit"][local_name]
            expected = probe["learning_curves"][size][frozen_name]["internal_test"]
            for key in (
                "pairs", "wins", "ties", "losses", "paired_accuracy",
                "answer_level_roc_auc", "mean_paired_margin", "median_paired_margin",
            ):
                assert observed[key] == expected[key], f"probe mismatch {size}/{local_name}/{key}"

    validation = {
        "schema": "confidence-probe-scaleup-baseline-validation-v1",
        "status": "PASS",
        "checks": {
            "exact_method_inventory": True,
            "all_metric_denominators_complete": True,
            "win_tie_loss_and_tie_half_arithmetic": True,
            "grouped_intervals_present": True,
            "all_nine_internal_test_contrasts_present": True,
            "reconstructed_probe_metrics_match_frozen_result_exactly": True,
            "missing": 0,
            "excluded": 0,
            "provider_calls": 0,
            "qwen_forwards": 0,
        },
        "artifacts": {
            "result": {"path": str(RESULT), "bytes": RESULT.stat().st_size,
                       "sha256": sha256(RESULT)},
            "baseline_runner": {"path": str(HERE / "run_baseline_comparison.py"),
                                "sha256": sha256(HERE / "run_baseline_comparison.py")},
            "tests": {"path": str(HERE / "test_run_baseline_comparison.py"),
                      "sha256": sha256(HERE / "test_run_baseline_comparison.py")},
            "preregistration": {"path": str(HERE / "BASELINE_PREREGISTRATION.json"),
                                "sha256": sha256(HERE / "BASELINE_PREREGISTRATION.json")},
            "frozen_probe_result": {"path": str(PROBE), "sha256": sha256(PROBE)},
        },
    }
    OUTPUT.write_text(json.dumps(validation, sort_keys=True, separators=(",", ":")) + "\n",
                      encoding="utf-8")
    print(json.dumps({"status": "PASS", "result_sha256": sha256(RESULT)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
