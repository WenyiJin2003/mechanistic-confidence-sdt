# Project Guide

Start with the [root README](../README.md) for the findings,
[experiment map](experiments/EXPERIMENT_MAP.md) for the calculation, and
[cue-holdout result](../experiments/cue_holdout_challenge_v1/RESULTS.md)
for the latest measurement. The frozen layer-14 readout reached 47/50 on new
sources and cue constructions, compared with 34/50 for character TF-IDF,
30/50 for answer likelihood and 25/50 for counterbalanced length. This completes
a bounded pilot, not the full diverse-pair handoff. Human review and a matched
diverse-versus-template scale study come before any loss-training experiment.

## Study guide

| Step | Study | Finding or purpose | Read next |
|---:|---|---|---|
| **Current** | **Cue/recipe-holdout transfer** | **Frozen L14 47/50 and ensemble 48/50, above text, likelihood and length controls** | **[Result](../experiments/cue_holdout_challenge_v1/RESULTS.md) · [Protocol](../experiments/cue_holdout_challenge_v1/README.md)** |
| 1 | Stage 0 | Validated prompt-state semantic-uncertainty probing; likelihood was stronger | [Results](../reports/RESULTS_STAGE0.md#outcome) · [Runbook](experiments/README_STAGE0.md) |
| 2 | Stage 0B | Tested answer-state semantic uncertainty; no gain beyond likelihood | [Results](../reports/RESULTS_STAGE0.md#stage-0b--post-answer-hidden-state-diagnostic) |
| 3 | Paired Confidence v1 | Fitted an expressed-certainty direction | [Results](../reports/PAIRED_CONFIDENCE_RESULTS_V1.md) · [Runbook](experiments/PAIRED_CONFIDENCE_README.md) |
| 4 | Frozen Transfer v2 | New wording transferred; evidence robustness gate failed | [Results](../reports/CONFIDENCE_TRANSFER_RESULTS_V2.md) · [Registered design](../CONFIDENCE_TRANSFER_PREREGISTRATION_V2.md) |
| 5 | Separation v3 | Same-answer support sensitivity was not confirmed | [Results](../reports/CONFIDENCE_SEPARATION_RESULTS_V3.md) · [Registered design](experiments/CONFIDENCE_SEPARATION_V3_PREREGISTRATION.md) |
| Supplement | Cached audit | Tested comparator validity, geometry and projections | [Audit](../reports/CONFIDENCE_CORRECTNESS_AUDIT.md) |
| 6 | Evidence-Sensitive Readout v4 | Completed: 71.9% support ordering; missing-information and behavior checks failed | [Results](../reports/EVIDENCE_CONFIDENCE_RESULTS_V4.md) · [Runbook](experiments/EVIDENCE_CONFIDENCE_README_V4.md) · [Registered design](experiments/EVIDENCE_CONFIDENCE_V4_PREREGISTRATION.md) |
| 7a | Diverse Paired Certainty + Multi-Layer | Development readout was separable, but text and length shortcuts required an independent challenge | [Development result](../experiments/diverse_pairs_multilayer_v1/reports/DEVELOPMENT_DIAGNOSTIC.md) · [Protocol](../experiments/diverse_pairs_multilayer_v1/PROTOCOL.md) |
| **Next** | **Matched diversity/scale completion** | **Human review, diverse-vs-template comparison and 100/300/700-source learning curves remain** | **[Next decision](../experiments/diverse_pairs_multilayer_v1/NEXT_DECISION.md)** |
| Later | Synthetic-fact training pilot | Downstream proposal only; no training has run | [Proposal](experiments/NEXT_EXPERIMENT.md) |

Use the [research sequence and methods](experiments/EXPERIMENT_MAP.md) to compare
the labels, token positions and equations. The [dataset browser](../datasets/README.md)
shows every question and answer; the [report index](../reports/README.md) and
[artifact index](../results/README.md) provide the narrative and numerical records.

## Upstream source

- [UPSTREAM_README.md](UPSTREAM_README.md) — preserved upstream documentation

V3 and v4 are complete; full confidence validation remains open. Historical reports contain
the interpretation and recommended next steps at the time of each study; use
[active status](experiments/STATUS.md) for the latest decision. The bounded
transfer test is complete; the next step is human audit and completion of the
handoff's matched diversity/scale study. Loss training remains downstream.

Experiment runbooks, current status, and the experiment map are under `experiments/`.
Narrative reports are under `reports/` at the repository root. Both immutable
preregistrations retain their registered root paths for reproduction checks.
