#!/usr/bin/env python3
"""Run one resumable Stage 0 phase."""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from stage0.pipeline import load_config, run  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/stage0_qwen05b.yaml")
    parser.add_argument(
        "--run",
        required=True,
        help="Run name declared under the selected configuration's `runs` mapping.",
    )
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    config, path = load_config(args.config)
    os.environ.setdefault("HF_HOME", config["project"]["hf_cache_dir"])
    os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    logging.info("Configuration: %s", path)
    manifest = run(config, args.run)
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0 if manifest["checks"]["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
