# Project Status

Last updated: 2026-09-29

## Current decision

Stage 0 is complete. The local pipeline, frozen hidden-state signal, and layer-14 probe direction all passed their respective checks. The direction is now eligible for a small activation-steering diagnostic. The project is **not yet ready for a mechanistic-confidence loss** because corrected stacking still found no predictive value beyond answer likelihood, and no causal intervention has been run.

| Gate | Result | Evidence |
|---|---|---|
| Engineering and leakage checks | Passed | All saved checks passed; fresh/old overlap was zero |
| Semantic-label reliability | Passed with caution | 10-vs-20 sample agreement was 90% |
| Frozen internal-signal probe | Passed | Layer 14 AUROC 0.718 [0.603, 0.821] |
| Above shuffled-label control | Passed | Probe 0.718; shuffled upper bound 0.613 |
| Stable intervention direction | Passed | Nested OOF AUROC 0.738 [0.680, 0.793]; median cosine 0.600 versus null upper 0.123 |
| Corrected incremental information over answer NLL | Failed | Combined worsened log-loss by 0.0027; 95% interval [0.0010, 0.0052] |
| Eligible for activation steering | **Yes** | All eight layer-14 direction gates passed |
| Ready for mechanistic loss | **No** | Incremental gate failed; causal evidence absent |

## Next step

Run one small, bidirectional activation-steering diagnostic with the frozen layer-14 direction:

1. first verify that the hook reproduces cached layer-14 activations and that `alpha = 0` exactly preserves logits;
2. on a limited held-out set, compare confidence steering, uncertainty steering, zero-hook, matched-norm random direction, shuffled direction, and a matched output-temperature control;
3. measure semantic entropy, exact match/F1, wrong-consensus rate, output length, and degeneration.

Proceed toward synthetic-document training only if steering changes semantic entropy in both intended directions, exceeds the controls, and preserves answer quality. A failed steering test should stop the mechanistic-loss path rather than trigger a larger training run.

## Completed experiments

| Experiment | Outcome | Location |
|---|---|---|
| Smoke test and NLI pilot | Pipeline passed | `results/run_a/`, `results/run_b/` |
| Qwen 0.5B, 200 questions | Probe not robust | `results/run_200/` |
| Qwen 1.5B, 200 questions | Promising but wide interval | `results/run_200_qwen15b/` |
| Cached split audit | Weak repeatable signal; unstable best layer | `results/run_200_qwen15b_split_stability/` |
| Sampling reliability | Ten samples recommended | `results/run_50_qwen15b_label_stability/` |
| Fresh Qwen 1.5B confirmation | Internal signal passed; readiness failed | `results/run_500_qwen15b_confirm/` |
| Cached direction and stacking audit | Direction passed; incremental value failed | `results/run_500_qwen15b_direction_stability/` |

See [`RESULTS_STAGE0.md`](RESULTS_STAGE0.md) for the full evidence and [`README_STAGE0.md`](README_STAGE0.md) for commands.
