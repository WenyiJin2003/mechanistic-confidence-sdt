# Documentation Index

Start with the [root README](../README.md) for the findings,
[experiment map](experiments/EXPERIMENT_MAP.md) for the calculation, and
[next-experiment proposal](experiments/NEXT_EXPERIMENT.md) for the research decision.

## Current research

- [Proposed synthetic-fact SFT pilot](experiments/NEXT_EXPERIMENT.md) — four matched training conditions; independent recall and retention outcomes; not yet run or preregistered
- [Experiment map and canonical names](experiments/EXPERIMENT_MAP.md) — separates semantic uncertainty, expressed certainty, and same-answer contextual correctness
- [Confidence–Correctness Separation v3](../reports/CONFIDENCE_SEPARATION_RESULTS_V3.md), [registered design](experiments/CONFIDENCE_SEPARATION_V3_PREREGISTRATION.md), and [configuration](../configs/confidence_separation_v3.yaml) — complete; wording transfers, both response-content candidates fail confirmation
- [Cached confidence/correctness audit](../reports/CONFIDENCE_CORRECTNESS_AUDIT.md) — comparator validity, geometric stability, projection and small subspaces; post-hoc, no new model calls
- [Frozen Transfer v2 — Expressed-Certainty Evidence-Transfer Test](../reports/CONFIDENCE_TRANSFER_RESULTS_V2.md), [preregistration](../CONFIDENCE_TRANSFER_PREREGISTRATION_V2.md), and [execution](experiments/CONFIDENCE_TRANSFER_README_V2.md) — complete; pooled wording/evidence transfer, failed primary fact-type robustness gate
- [Paired Confidence v1 — Answer-End Expressed-Certainty Readout](../reports/PAIRED_CONFIDENCE_RESULTS_V1.md), [design](../PAIRED_CONFIDENCE_PREREGISTRATION_V1.md), and [execution](experiments/PAIRED_CONFIDENCE_README.md) — completed expressed-certainty pilot
- [Stage 0 — Prompt-State Semantic-Uncertainty Probe and Stage 0B — Answer-State Semantic-Uncertainty Diagnostic](../reports/RESULTS_STAGE0.md), plus the [technical runbook](experiments/README_STAGE0.md) — historical semantic-uncertainty diagnostics
- [Report index](../reports/README.md) and [dataset browser](../datasets/README.md) — narrative conclusions and browsable questions, answers, and response variants
- [Artifact index](../results/README.md) — saved metrics, directions, and manifests

## Provenance and archive

- [UPSTREAM_README.md](UPSTREAM_README.md) — preserved upstream documentation
- [archive/INITIAL_PLAN_STAGE0.md](archive/INITIAL_PLAN_STAGE0.md) — original Stage 0 execution plan
- [archive/MACHINE_ASSESSMENT.md](archive/MACHINE_ASSESSMENT.md) — historical execution-environment note

Fresh response-content confirmation is complete. Historical reports contain
the interpretation and recommended next steps at the time of each study; use
[current status](experiments/STATUS.md) for the latest decision. The next proposed
study tests whether the candidate term helps fact learning, while preserving the
limits of its expressed-certainty interpretation.

Experiment runbooks, status notes, and the experiment map are under `experiments/`.
Narrative reports are under `reports/` at the repository root. Both immutable
preregistrations retain their registered root paths for reproduction checks.
