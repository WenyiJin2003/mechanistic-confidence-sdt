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
- Completed the matched 200-example Qwen 1.5B comparison. All engineering and leakage checks passed.
- Verified with a full replay that all 200 generation records, all 200 hidden-state records, the dataset subset, and every entailment judgment are reusable without repeating the expensive stages.
- Trained linear probes and required baselines, audited the split for leakage, and created the layer plot.
- Wrote `RESULTS_STAGE0.md`.

## Current conclusion

The pipeline is validated. Qwen 1.5B substantially improved answer quality and validation selected layer 14 with AUROC 0.754; its test AUROC was 0.665 with context-bootstrap 95% interval [0.481, 0.844]. This is more promising than 0.5B but not conclusive, and output baselines remain stronger. No mechanistic or causal claim is warranted.

## Recommended next step

Use the cached 1.5B artifacts for a cheap multi-split stability analysis before collecting more generations or adding an internal mechanistic training loss.

## Matched Qwen 1.5B comparison — completed

- Configuration: `configs/stage0_qwen15b_200.yaml`
- Same 200 examples, five generations, fixed grouped split, prompt, seeds, and 12-token limit as the 0.5B follow-up
- Generator: `Qwen/Qwen2.5-1.5B-Instruct`, unquantized bfloat16 on MPS; float16 failed preflight with non-finite sampling probabilities
- Approximately depth-matched blocks: 5, 9, 14, 19, 23, and 28
- Results: `results/run_200_qwen15b/`
- Plot: `plots/run_200_qwen15b_probe_performance_by_layer.png`
- Selected layer 14: validation AUROC 0.754; test AUROC 0.665, 95% interval [0.481, 0.844]
- Output baselines: predictive entropy 0.833 and answer NLL 0.835 test AUROC

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
.venv/bin/python scripts/run_stage0.py --config configs/stage0_qwen15b_200.yaml --run run_200_qwen15b
```
