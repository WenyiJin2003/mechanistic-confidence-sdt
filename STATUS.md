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

The pipeline is validated. On a genuinely fresh 500-question confirmation set, the frozen layer-14 probe reached test AUROC 0.718 with context-bootstrap 95% interval [0.603, 0.821] and exceeded the shuffled-label upper bound. This confirms a predictive internal association. Answer NLL was much stronger at 0.911, and adding layer 14 made it worse rather than better. The internal-signal gate passed, but the incremental-information and mechanistic-readiness gates failed. No mechanistic or causal claim is warranted.

## Recommended next step

Do not start synthetic-document mechanistic-loss training yet. First use the cached 500-question run to measure whether the learned layer-14 probe direction is stable across grouped folds and regularization choices. If the direction is stable, run a small activation-steering intervention with random-direction controls before deciding whether it is a defensible training loss.

## Fresh 500-question confirmation — completed

- Configuration: `configs/stage0_qwen15b_500_confirm.yaml`
- 500 SQuAD questions with 10 local answers each; exclude IDs, contexts, and exact or near-duplicate questions from the earlier 200-question 1.5B run.
- Layer 14 is the frozen primary analysis; layer 28 and validation selection are secondary.
- Signal gates: test AUROC at least 0.60, context-bootstrap lower 95% bound at least 0.50, and AUROC above the shuffled-label upper 95% bound.
- Mechanistic-readiness gate: adding layer-14 hidden state to answer NLL must beat answer NLL with a positive lower 95% bound.
- All engineering, leakage, and fresh-data exclusion checks passed.
- Frozen layer 14: test AUROC 0.718, context-bootstrap 95% interval [0.603, 0.821]; shuffled-label 95% upper bound 0.613. The signal gate passed.
- Answer NLL: test AUROC 0.911. Layer 14 plus NLL: 0.776; difference from NLL -0.135, interval [-0.226, -0.050]. The incremental and readiness gates failed.
- Validation selected layer 23 as a secondary result: validation AUROC 0.787 and test AUROC 0.848. It still trailed answer NLL.
- Results: `results/run_500_qwen15b_confirm/`
- Plot: `plots/run_500_qwen15b_confirm_probe_performance_by_layer.png`

## Semantic-entropy sampling reliability — completed

- Configuration: `configs/stage0_qwen15b_label_stability.yaml`
- Reuse the existing five answers for 50 questions sampled equally from five original entropy-rank strata.
- Add 15 answers per question, then compare 5-, 10-, and 20-sample semantic entropy under the frozen original training-only cutoff.
- Predeclared gates: 5-vs-20 agreement at least 0.80, kappa at least 0.60, Spearman at least 0.70, and 10-vs-20 agreement at least 0.90.
- No probe is retrained in this diagnostic; it tests the reliability of the target labels used to train a future probe.
- All four point-estimate gates passed: 5-vs-20 agreement 0.84, kappa 0.683, Spearman 0.808; 10-vs-20 agreement 0.90.
- Five-sample labels flipped for 8/50 questions (seven low-to-high and one high-to-low). Ten-sample labels flipped for 5/50.
- Stratified-bootstrap 95% intervals were [0.74, 0.92] for 5-vs-20 agreement and [0.688, 0.898] for Spearman; these wide intervals motivate a cautious conclusion.
- Results: `results/run_50_qwen15b_label_stability/label_stability_metrics.json`
- Plot: `plots/run_50_qwen15b_label_stability.png`

## Cached split-stability audit — completed

- 100/100 predeclared context-grouped splits were valid and passed leakage checks.
- Fixed layer 14: median test AUROC 0.628; 93/100 splits above chance.
- Five-fold cross-fitted layer-14 AUROC 0.588, context-bootstrap 95% interval [0.507, 0.666].
- Validation-selected layer median test AUROC 0.634.
- Overall preregistered gate did not pass: layers 14/19 were selected in 33% of splits, below the 60% criterion; layer 28 was selected in 49%.
- Output baselines remained much stronger: predictive entropy median 0.921 and answer NLL median 0.944.
- Results: `results/run_200_qwen15b_split_stability/stability_metrics.json`
- Plot: `plots/run_200_qwen15b_split_stability.png`

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
