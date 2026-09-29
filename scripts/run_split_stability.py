#!/usr/bin/env python3
"""Run cached repeated-split stability diagnostics."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from stage0.stability import run_stability  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        default="configs/stage0_qwen15b_split_stability.yaml",
    )
    args = parser.parse_args()
    result = run_stability(args.config)
    print(
        json.dumps(
            {
                "passed": result["passed"],
                "gate_results": result["gate_results"],
                "summary": result["summary"],
                "cross_fitted_fixed_layer": result["cross_fitted_fixed_layer"],
                "elapsed_seconds": result["elapsed_seconds"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if result["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
