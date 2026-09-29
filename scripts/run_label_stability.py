#!/usr/bin/env python3
"""Run the cached 5-vs-10-vs-20 semantic-entropy reliability experiment."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from stage0.label_stability import run_label_stability  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        default="configs/stage0_qwen15b_label_stability.yaml",
    )
    args = parser.parse_args()
    result = run_label_stability(args.config)
    print(
        json.dumps(
            {
                "passed": result["passed"],
                "gate_results": result["gate_results"],
                "prefix_summaries": result["prefix_summaries"],
                "comparisons": result["comparisons"],
                "elapsed_seconds": result["runtime"]["elapsed_seconds"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if result["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
