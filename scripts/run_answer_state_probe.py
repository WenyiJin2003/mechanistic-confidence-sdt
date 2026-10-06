#!/usr/bin/env python3
"""Run the cache-only Stage 0B post-answer diagnostic."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from stage0.answer_state import run_stage0b, run_stage0b_robustness  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        default="configs/stage0b_qwen15b_answer_state.yaml",
    )
    parser.add_argument(
        "--mode",
        choices=("sanity", "full", "robustness"),
        default="full",
        help="Run only the 20-question gate or the complete primary analysis.",
    )
    args = parser.parse_args()
    result = (
        run_stage0b_robustness(args.config)
        if args.mode == "robustness"
        else run_stage0b(args.config, mode=args.mode)
    )
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
