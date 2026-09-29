# Stage 0 Status

Last updated: 2026-09-28

## Completed

- Read `STAGE0_WORK_HANDOFF.md` in full.
- Inspected the machine, runtimes, free disk, and existing Hugging Face cache.
- Cloned upstream commit `02e2167dd1c00e27080d421f9b40e13e00f0452b` and created branch `codex/stage0-qwen05b`.
- Created and tested an isolated Python 3.11 environment.
- Verified float16 MPS execution.
- Generalized the upstream Hugging Face loader to accept a full model ID and removed unconditional CUDA placement from the touched paths.
- Completed and cached the five-example preflight.
- Completed Run A: 12 examples, three generations, exact-match grouping. All checks passed.
- Completed Run B pilot: 64 examples, five generations, local DeBERTa-small NLI. All checks passed.
- Verified that generation, hidden-state, dataset, and entailment caches are reusable.
- Trained linear probes and required baselines, audited the split for leakage, and created the layer plot.
- Wrote `RESULTS_STAGE0.md`.

## Current conclusion

The pipeline is validated, but the 64-example probe result is inconclusive and near chance. Output likelihood baselines outperform the hidden-state probes. No mechanistic or causal claim is warranted.

## Recommended next step

Run a 200-example Qwen 0.5B stability experiment with layers 4, 8, 12, 16, 20, and 24 and a fixed train/validation/test split. Move to 1.5B only if the larger 0.5B run remains at chance or answer-quality review identifies model capacity as the main limitation.

## In progress — 200-example stability run

- Added the separate `configs/stage0_qwen05b_200.yaml` configuration.
- Restored layers 4, 8, 12, 16, 20, and 24.
- Added fixed context-grouped train/validation/test splits, validation-only layer selection, bootstrap intervals, 50 shuffled-label repetitions, correctness diagnostics, and a hidden-plus-NLL comparison.
- Decoupled generation and hidden-state caches so the first 64 five-sample generations can be reused while six-layer hidden states are recomputed.
- Next checkpoint: commit and push the implementation, then execute and cache `run_200`.

## Resume commands

All completed phases replay from cache:

```bash
.venv/bin/python scripts/run_stage0.py --config configs/stage0_qwen05b.yaml --run run_a
.venv/bin/python scripts/run_stage0.py --config configs/stage0_qwen05b.yaml --run run_b
```
