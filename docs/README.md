# Project Guide

Start with the [root README](../README.md) for the findings,
[experiment map](experiments/EXPERIMENT_MAP.md) for the calculation, and
[current evidence-validation study](experiments/EVIDENCE_CONFIDENCE_README_V4.md)
for the latest measurement study.

## Study guide

| Step | Study | Finding or purpose | Read next |
|---:|---|---|---|
| 1 | Stage 0 | Validated prompt-state semantic-uncertainty probing; likelihood was stronger | [Results](../reports/RESULTS_STAGE0.md#outcome) · [Runbook](experiments/README_STAGE0.md) |
| 2 | Stage 0B | Tested answer-state semantic uncertainty; no gain beyond likelihood | [Results](../reports/RESULTS_STAGE0.md#stage-0b--post-answer-hidden-state-diagnostic) |
| 3 | Paired Confidence v1 | Fitted an expressed-certainty direction | [Results](../reports/PAIRED_CONFIDENCE_RESULTS_V1.md) · [Runbook](experiments/PAIRED_CONFIDENCE_README.md) |
| 4 | Frozen Transfer v2 | New wording transferred; evidence robustness gate failed | [Results](../reports/CONFIDENCE_TRANSFER_RESULTS_V2.md) · [Registered design](../CONFIDENCE_TRANSFER_PREREGISTRATION_V2.md) |
| 5 | Separation v3 | Same-answer support sensitivity was not confirmed | [Results](../reports/CONFIDENCE_SEPARATION_RESULTS_V3.md) · [Registered design](experiments/CONFIDENCE_SEPARATION_V3_PREREGISTRATION.md) |
| Supplement | Cached audit | Tested comparator validity, geometry and projections | [Audit](../reports/CONFIDENCE_CORRECTNESS_AUDIT.md) |
| 6 | Evidence-Sensitive Readout v4 | Completed: 71.9% support ordering; missing-information and behavior checks failed | [Results](../reports/EVIDENCE_CONFIDENCE_RESULTS_V4.md) · [Runbook](experiments/EVIDENCE_CONFIDENCE_README_V4.md) · [Registered design](experiments/EVIDENCE_CONFIDENCE_V4_PREREGISTRATION.md) |
| 7 | Synthetic-fact training pilot | Deferred until measurement validation is assessed | [Earlier proposal](experiments/NEXT_EXPERIMENT.md) |

Use the [research sequence and methods](experiments/EXPERIMENT_MAP.md) to compare
the labels, token positions and equations. The [dataset browser](../datasets/README.md)
shows every question and answer; the [report index](../reports/README.md) and
[artifact index](../results/README.md) provide the narrative and numerical records.

## Upstream source

- [UPSTREAM_README.md](UPSTREAM_README.md) — preserved upstream documentation

V3 and v4 are complete; full confidence validation remains open. Historical reports contain
the interpretation and recommended next steps at the time of each study; use
[current status](experiments/STATUS.md) for the latest decision. The next step
tests whether a new evidence-support score has the behavioral validity needed
to motivate a confidence objective.

Experiment runbooks, current status, and the experiment map are under `experiments/`.
Narrative reports are under `reports/` at the repository root. Both immutable
preregistrations retain their registered root paths for reproduction checks.
