#!/usr/bin/env python3
"""Run the preregistered cached direction-stability audit."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from stage0.direction_stability import run_direction_stability  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        default="configs/stage0_qwen15b_direction_stability.yaml",
    )
    parser.add_argument(
        "--strict-gates",
        action="store_true",
        help="Exit with status 2 when the scientific gates fail (a completed failed audit is otherwise status 0).",
    )
    args = parser.parse_args()
    result = run_direction_stability(args.config)
    primary = result["layers"][str(result["primary_layer"])]
    stacking = result["primary_layer_nested_stacking"]
    print(
        json.dumps(
            {
                "completed": True,
                "reserved_test_examples_used": False,
                "primary_layer": result["primary_layer"],
                "primary_oof_auroc": primary["nested_cv"]["oof_auroc"],
                "primary_oof_auroc_95": primary["nested_cv"][
                    "oof_auroc_context_bootstrap_95"
                ],
                "primary_median_raw_direction_cosine": primary["split_half"][
                    "raw_direction_cosine"
                ]["median"],
                "shuffled_cosine_upper_95": primary["split_half"]["shuffled_control"][
                    "raw_direction_cosine"
                ]["empirical_97.5"],
                "nll_minus_combined_log_loss": stacking[
                    "nll_minus_combined_log_loss"
                ],
                "primary_direction_gate_results": result[
                    "primary_direction_gate_results"
                ],
                "eligible_for_activation_steering": result[
                    "eligible_for_activation_steering"
                ],
                "incremental_information_passed": result[
                    "incremental_information_passed"
                ],
                "ready_for_mechanistic_loss": False,
                "elapsed_seconds": result["elapsed_seconds"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    if args.strict_gates and not result["eligible_for_activation_steering"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
