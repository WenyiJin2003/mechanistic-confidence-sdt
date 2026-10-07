# Documentation Index

Current conclusions and the research sequence are in the [root README](../README.md);
the next decision gate is in [project status](experiments/STATUS.md).

## Current research

- [Experiment map and canonical names](experiments/EXPERIMENT_MAP.md) — separates Stage 0 prompt-state semantic uncertainty, Stage 0B answer-state semantic uncertainty, Paired Confidence v1 expressed certainty, and Frozen Transfer v2
- [Frozen Transfer v2 — Expressed-Certainty Evidence-Transfer Test](../reports/CONFIDENCE_TRANSFER_RESULTS_V2.md), [preregistration](../CONFIDENCE_TRANSFER_PREREGISTRATION_V2.md), and [execution](experiments/CONFIDENCE_TRANSFER_README_V2.md) — complete; pooled wording/evidence transfer, failed primary fact-type robustness gate
- [Paired Confidence v1 — Answer-End Expressed-Certainty Readout](../reports/PAIRED_CONFIDENCE_RESULTS_V1.md), [design](../PAIRED_CONFIDENCE_PREREGISTRATION_V1.md), and [execution](experiments/PAIRED_CONFIDENCE_README.md) — completed expressed-certainty pilot
- [Stage 0 — Prompt-State Semantic-Uncertainty Probe and Stage 0B — Answer-State Semantic-Uncertainty Diagnostic](../reports/RESULTS_STAGE0.md), plus the [technical runbook](experiments/README_STAGE0.md) — historical semantic-uncertainty diagnostics
- [Report index](../reports/README.md) and [dataset browser](../datasets/README.md) — narrative conclusions and browsable questions, answers, and response variants
- [Artifact index](../results/README.md) — saved metrics, directions, and manifests

## Provenance and archive

- [UPSTREAM_README.md](UPSTREAM_README.md) — preserved upstream documentation
- [archive/INITIAL_PLAN_STAGE0.md](archive/INITIAL_PLAN_STAGE0.md) — original Stage 0 execution plan
- [archive/MACHINE_ASSESSMENT.md](archive/MACHINE_ASSESSMENT.md) — historical execution-environment note

Historical reports, preregistrations, plans, and execution-environment notes are
preserved. The current next step is prospective confirmation of the separately
frozen response-content candidates; v2 does not validate an SDT loss.

Experiment runbooks, status notes, and the experiment map are under `experiments/`.
Narrative reports are under `reports/` at the repository root. Both immutable
preregistrations retain their registered root paths for reproduction checks.
