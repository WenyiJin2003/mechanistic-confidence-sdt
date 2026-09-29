# Stage 0 Status

Last updated: 2026-09-29

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
- Completed the 200-example follow-up: 1,000 generations, six layers, context-grouped train/validation/test split, 50 shuffled-label controls, and 2,000 context-bootstrap resamples. All engineering checks passed.
- Verified with a full replay that all 200 generation records, all 200 hidden-state records, the dataset subset, and every entailment judgment are reusable without repeating the expensive stages.
- Trained linear probes and required baselines, audited the split for leakage, and created the layer plot.
- Wrote `RESULTS_STAGE0.md`.

## Current conclusion

The pipeline is validated. In the 200-example follow-up, validation selected layer 4 with validation AUROC 0.503; its test AUROC was 0.628 with context-bootstrap 95% interval [0.440, 0.800]. Predictive entropy (0.847) and answer negative log-likelihood (0.855) were much stronger on test. This run therefore does not provide robust evidence of a useful semantic-entropy-label signal in this 0.5B setup. No mechanistic or causal claim is warranted.

## Recommended next step

Move the next measurement run to Qwen 1.5B while keeping the same examples, split, prompt, sample count, and token limit for an interpretable model-size comparison. Consider a separate longer-generation ablation afterward because 805/1,000 current generations hit the 12-token cap.

## 200-example follow-up — completed

- Configuration: `configs/stage0_qwen05b_200.yaml`
- Results: `results/run_200/`
- Plot: `plots/run_200_probe_performance_by_layer.png`
- Full interpretation and limitations: `RESULTS_STAGE0.md`

## Resume commands

All completed phases replay from cache:

```bash
.venv/bin/python scripts/run_stage0.py --config configs/stage0_qwen05b.yaml --run run_a
.venv/bin/python scripts/run_stage0.py --config configs/stage0_qwen05b.yaml --run run_b
.venv/bin/python scripts/run_stage0.py --config configs/stage0_qwen05b_200.yaml --run run_200
```
