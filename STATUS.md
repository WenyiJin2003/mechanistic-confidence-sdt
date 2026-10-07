# Project Status

Last updated: 2026-10-06

## Latest diagnostic: Stage 0B

**Conclusion:** the post-answer hidden state contains a readable semantic-uncertainty signal, but it does **not** add reliable held-out information beyond the likelihood of the same answer.

| Observed answer | Same-answer NLL | Layer-14 post-answer probe | NLL + scalar probe |
|---|---:|---:|---:|
| Index 0 (primary) | **0.773** | 0.693 | 0.763 |
| Index 3 (predeclared robustness) | **0.789** | 0.720 | 0.766 |

For the primary run, combined-minus-NLL AUROC was **-0.010**, with a context-grouped 95% interval of **[-0.074, 0.049]**. The log-loss improvement interval also crossed zero. The 20-question gate and all 500 primary examples passed; the run made **zero new generation and zero NLI inference calls**. Optional index 7 was not run because the meeting-time result was already stable across the primary and index-3 analyses.

**Research implication:** do not convert this probe into a confidence loss on the basis of Stage 0B. The result does not erase the earlier Stage 0 association or direction-stability finding; it answers a narrower question and shows that the tested post-answer linear representation is not better than same-answer likelihood. The next meeting should clarify the intended confidence target and why an internal loss should add something that ordinary likelihood does not already provide.

Full details are in the separate **Stage 0B** section of [`RESULTS_STAGE0.md`](RESULTS_STAGE0.md).

## Project decision

**Proceed:** run a controlled activation-steering experiment with the frozen layer-14 direction.

**Do not proceed yet:** begin synthetic-document mechanistic-loss training. That step requires a bidirectional entropy change that outperforms the controls and preserves answer quality.

| Question | Answer |
|---|---|
| Is the pipeline validated? | **Yes** |
| Is the layer-14 direction stable enough for an intervention test? | **Yes** |
| Is a mechanistic-confidence training loss justified? | **No** |

## Immediate experiment

1. Verify the layer-14 hook against cached activations and require `alpha = 0` to reproduce baseline logits.
2. Compare negative-direction, positive-direction, zero-hook, matched random, shuffled-direction, and matched-temperature conditions.
3. Measure semantic entropy, exact match/F1, wrong consensus, output length, and degeneration.

The canonical quantitative record is [`RESULTS_STAGE0.md`](RESULTS_STAGE0.md). Reproduction commands are in [`README_STAGE0.md`](README_STAGE0.md), and artifacts are indexed in [`results/README.md`](results/README.md).
