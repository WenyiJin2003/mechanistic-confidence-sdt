# Research Reports

These reports interpret the completed experiments. The [dataset browser](../datasets/README.md)
shows the questions, supplied answers, response variants, and row-level results;
the [artifact index](../results/README.md) links the original saved outputs.

| Experiment | Report | Browse questions and answers | Execution guide |
|---|---|---|---|
| Stage 0 — Prompt-State Semantic-Uncertainty Probe and Stage 0B — Answer-State Semantic-Uncertainty Diagnostic | [Stage 0/0B results](RESULTS_STAGE0.md) | [Stage 0 datasets](../datasets/stage0/README.md) | [Stage 0 runbook](../docs/experiments/README_STAGE0.md) |
| Paired Confidence v1 — Answer-End Expressed-Certainty Readout | [V1 results](PAIRED_CONFIDENCE_RESULTS_V1.md) | [V1 questions and response variants](../datasets/paired-confidence-v1/README.md) | [V1 runbook](../docs/experiments/PAIRED_CONFIDENCE_README.md) |
| Frozen Transfer v2 — Expressed-Certainty Evidence-Transfer Test | [V2 results](CONFIDENCE_TRANSFER_RESULTS_V2.md) | [V2 facts, contexts, and responses](../datasets/frozen-transfer-v2/README.md) | [V2 runbook](../docs/experiments/CONFIDENCE_TRANSFER_README_V2.md) |
| Confidence–Correctness Separation v3 | [Fresh counterfactual results](CONFIDENCE_SEPARATION_RESULTS_V3.md) | [All 672 responses](../datasets/confidence-separation-v3/README.md) | [Registered design and endpoints](../docs/experiments/CONFIDENCE_SEPARATION_V3_PREREGISTRATION.md) |
| Cached geometry and comparator audit | [Confidence/correctness audit](CONFIDENCE_CORRECTNESS_AUDIT.md) | Reuses the complete v1/v2 collections | [Audit configuration](../configs/confidence_correctness_audit.yaml) |

The [experiment map](../docs/experiments/EXPERIMENT_MAP.md) distinguishes the targets,
token positions, and calculations. The [current status](../docs/experiments/STATUS.md)
records the completed confirmation result and next decision.

The original [v1 preregistration](../PAIRED_CONFIDENCE_PREREGISTRATION_V1.md) and
[v2 preregistration](../CONFIDENCE_TRANSFER_PREREGISTRATION_V2.md) remain at their
registered paths so the frozen reproduction checks can use the unchanged files.
