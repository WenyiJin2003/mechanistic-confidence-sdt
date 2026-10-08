# Research Reports

**Start with the [fresh v3 result](CONFIDENCE_SEPARATION_RESULTS_V3.md):** expressed
certainty transfers, but same-answer support ordering is near chance. The
[proposed next study](../docs/experiments/NEXT_EXPERIMENT.md) asks whether the
candidate readout nevertheless helps fact learning as an auxiliary objective.

These reports interpret the completed experiments. The [dataset browser](../datasets/README.md)
shows the questions, supplied answers, response variants, and row-level results;
the [artifact index](../results/README.md) links the original saved outputs.

| Step | Experiment | Report | Browse questions and answers | Execution guide |
|---:|---|---|---|---|
| 1–2 | Stage 0 and 0B semantic uncertainty | [Results](RESULTS_STAGE0.md) | [Generated answers](../datasets/stage0/README.md) | [Runbook](../docs/experiments/README_STAGE0.md) |
| 3 | Paired Confidence v1 | [Results](PAIRED_CONFIDENCE_RESULTS_V1.md) | [1,440 response variants](../datasets/paired-confidence-v1/README.md) | [Runbook](../docs/experiments/PAIRED_CONFIDENCE_README.md) |
| 4 | Frozen Transfer v2 | [Results](CONFIDENCE_TRANSFER_RESULTS_V2.md) | [480 responses](../datasets/frozen-transfer-v2/README.md) | [Runbook](../docs/experiments/CONFIDENCE_TRANSFER_README_V2.md) |
| 5 | Confidence–Correctness Separation v3 | [Results](CONFIDENCE_SEPARATION_RESULTS_V3.md) | [672 responses](../datasets/confidence-separation-v3/README.md) | [Registered design](../docs/experiments/CONFIDENCE_SEPARATION_V3_PREREGISTRATION.md) |
| Supplement | Cached geometry and comparator audit | [Results](CONFIDENCE_CORRECTNESS_AUDIT.md) | Reuses Steps 3 and 4 | [Configuration](../configs/confidence_correctness_audit.yaml) |
| 6 | Proposed synthetic-fact training study | [Design](../docs/experiments/NEXT_EXPERIMENT.md) | To be fixed | Not yet preregistered |

The [experiment map](../docs/experiments/EXPERIMENT_MAP.md) distinguishes the targets,
token positions, and calculations. The [current status](../docs/experiments/STATUS.md)
records the completed confirmation result and next decision.

Earlier reports retain their contemporary conclusions. Their suggested next
measurement studies have now been completed in v3; the current proposal is a
functional training comparison, not another relabelling of the old results.

The original [v1 preregistration](../PAIRED_CONFIDENCE_PREREGISTRATION_V1.md) and
[v2 preregistration](../CONFIDENCE_TRANSFER_PREREGISTRATION_V2.md) remain at their
registered paths so the frozen reproduction checks can use the unchanged files.
