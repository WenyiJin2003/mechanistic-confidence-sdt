# Project Status

Last updated: 2026-09-29

## Current decision

Stage 0 is complete. The local pipeline is validated, and a preregistered hidden-state signal reproduced on 500 fresh questions. The project is **not yet ready for a mechanistic-confidence loss** because the hidden probe did not add predictive value beyond answer likelihood.

| Gate | Result | Evidence |
|---|---|---|
| Engineering and leakage checks | Passed | All saved checks passed; fresh/old overlap was zero |
| Semantic-label reliability | Passed with caution | 10-vs-20 sample agreement was 90% |
| Frozen internal-signal probe | Passed | Layer 14 AUROC 0.718 [0.603, 0.821] |
| Above shuffled-label control | Passed | Probe 0.718; shuffled upper bound 0.613 |
| Incremental information over answer NLL | Failed | Layer 14 + NLL 0.776 versus NLL 0.911 |
| Ready for mechanistic loss | **No** | Incremental-information gate failed |

## Next step

Use the cached 500-question artifacts; do not generate new answers yet.

1. Fit layer-14 probes across grouped folds and regularization strengths.
2. Measure cosine similarity of the learned probe directions.
3. If the direction is stable, run a small activation-steering experiment with positive, negative, and random-direction controls.

Only a reproducible intervention that changes semantic entropy in the intended direction without unacceptable correctness loss should be promoted into a synthetic-training loss.

## Completed experiments

| Experiment | Outcome | Location |
|---|---|---|
| Smoke test and NLI pilot | Pipeline passed | `results/run_a/`, `results/run_b/` |
| Qwen 0.5B, 200 questions | Probe not robust | `results/run_200/` |
| Qwen 1.5B, 200 questions | Promising but wide interval | `results/run_200_qwen15b/` |
| Cached split audit | Weak repeatable signal; unstable best layer | `results/run_200_qwen15b_split_stability/` |
| Sampling reliability | Ten samples recommended | `results/run_50_qwen15b_label_stability/` |
| Fresh Qwen 1.5B confirmation | Internal signal passed; readiness failed | `results/run_500_qwen15b_confirm/` |

See [`RESULTS_STAGE0.md`](RESULTS_STAGE0.md) for the full evidence and [`README_STAGE0.md`](README_STAGE0.md) for commands.
