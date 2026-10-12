# Research Reports

**Start with the [cue-holdout challenge result](../experiments/cue_holdout_challenge_v1/RESULTS.md):**
the frozen layer-14 readout ordered 47/50 new content-matched certainty pairs,
compared with 34/50 for character TF-IDF, 30/50 for answer likelihood and
25/50 for counterbalanced response length. The fixed all-layer ensemble reached
48/50, but its two-point gain does not justify the added complexity for a first
training pilot.

This supports a transferable hidden-state signal for **expressed certainty
about preserved answer content**. It does not establish subjective belief,
correctness, evidence-sensitive confidence, causality or training benefit. The
challenge is development-only until its locked text receives human blind review.

The earlier [v4 result](EVIDENCE_CONFIDENCE_RESULTS_V4.md) found contextual
support ordering at 71.9% on unseen facts and wording, but did not pass
missing-information and behavior validation. The
[v3 result](CONFIDENCE_SEPARATION_RESULTS_V3.md) explains why the old certainty
directions needed a different measurement. Training remains deferred.

These reports interpret the completed experiments. The [dataset browser](../datasets/README.md)
shows the questions, supplied answers, response variants, and row-level results;
the [artifact index](../results/README.md) links the original saved outputs.

| Step | Experiment | Report | Browse questions and answers | Execution guide |
|---:|---|---|---|---|
| **Current** | **Cue/recipe-holdout transfer** | **[Challenge result](../experiments/cue_holdout_challenge_v1/RESULTS.md)** | Locked private text; aggregate results and hashes public | **[Protocol](../experiments/cue_holdout_challenge_v1/README.md)** |
| 1–2 | Stage 0 and 0B semantic uncertainty | [Results](RESULTS_STAGE0.md) | [Generated answers](../datasets/stage0/README.md) | [Runbook](../docs/experiments/README_STAGE0.md) |
| 3 | Paired Confidence v1 | [Results](PAIRED_CONFIDENCE_RESULTS_V1.md) | [1,440 response variants](../datasets/paired-confidence-v1/README.md) | [Runbook](../docs/experiments/PAIRED_CONFIDENCE_README.md) |
| 4 | Frozen Transfer v2 | [Results](CONFIDENCE_TRANSFER_RESULTS_V2.md) | [480 responses](../datasets/frozen-transfer-v2/README.md) | [Runbook](../docs/experiments/CONFIDENCE_TRANSFER_README_V2.md) |
| 5 | Confidence–Correctness Separation v3 | [Results](CONFIDENCE_SEPARATION_RESULTS_V3.md) | [672 responses](../datasets/confidence-separation-v3/README.md) | [Registered design](../docs/experiments/CONFIDENCE_SEPARATION_V3_PREREGISTRATION.md) |
| Supplement | Cached geometry and comparator audit | [Results](CONFIDENCE_CORRECTNESS_AUDIT.md) | Reuses Steps 3 and 4 | [Configuration](../configs/confidence_correctness_audit.yaml) |
| 6 | Evidence-Sensitive Readout v4 | [Results](EVIDENCE_CONFIDENCE_RESULTS_V4.md) | [168 records, supplied responses and actual answers](../datasets/evidence-confidence-v4/README.md) | [Runbook](../docs/experiments/EVIDENCE_CONFIDENCE_README_V4.md) |
| 7a | Diverse Paired Certainty + Multi-Layer | [Development diagnostic](../experiments/diverse_pairs_multilayer_v1/reports/DEVELOPMENT_DIAGNOSTIC.md) | Private development text; aggregate results public | [Study guide](../experiments/diverse_pairs_multilayer_v1/README.md) |
| Next | Controlled synthetic-fact training pilot | [Design starting point](../docs/experiments/NEXT_EXPERIMENT.md) | To be preregistered after human audit | Not yet run |

The [experiment map](../docs/experiments/EXPERIMENT_MAP.md) distinguishes the targets,
token positions, and calculations. The [current status](../docs/experiments/STATUS.md)
records the completed challenge and next decision.

Earlier reports retain their contemporary conclusions. Their suggested next
measurement studies were completed in v3. V4 now fits a different target on
fresh training records; it does not replace or relabel the earlier failures.
The functional training proposal remains untested. The current recommendation
is to human-audit the locked challenge, then preregister a small four-arm pilot
whose outcomes are judged independently of the optimized certainty score.

The original [v1 preregistration](../PAIRED_CONFIDENCE_PREREGISTRATION_V1.md) and
[v2 preregistration](../CONFIDENCE_TRANSFER_PREREGISTRATION_V2.md) remain at their
registered paths so the frozen reproduction checks can use the unchanged files.
