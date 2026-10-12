# Next Decision: Validate the Pair Construction Before Scaling

## Decision

**Do not start SDT loss training or a 1,000-pair generation run.** The activation
probe has a positive bounded transfer result, and the latest construction recipe
passes its mechanical canary after repair. The next uncertainty is whether the
new pairs are genuinely content-matched, natural, and robust to certainty-word
shortcuts.

## What is established

- The frozen layer-14 readout transferred to 47/50 new pairs; the fixed
  28-layer ensemble reached 48/50.
- Text, likelihood, and length controls reached 34/50, 30/50, and 25/50 on that
  challenge, so those controls do not fully explain the hidden-state result.
- The target remains **expressed certainty about preserved answer content**,
  not correctness, evidence support, subjective belief, or training benefit.
- Source review is selective: 74 of 200 candidates were eligible, 110 were
  rejected, and 16 need human review.
- The v3.7 two-stage canary reached 10/10 mechanical and final independent
  model-assisted semantic passes after five record-level local repairs.
- Together with v3.5, 20/20 retained canary pairs now pass both automated and
  model-assisted gates. This is not human certification.
- The v3.6 symmetric-copy data failed the genuine-paraphrase gate and is retained
  only as a cue-only lexical control.

## Immediate sequence

1. **Blind human-review the final 20 canary pairs.** Reviewers should judge
   content equivalence, speaker-level certainty, naturalness, and obvious
   shortcuts without seeing which side is labelled confident. Do not silently
   repair a scored evaluation set. The blinded, balanced local review packet is
   built; the judgments are pending.
2. **Freeze the cue-only baseline.** Use the same source identities and matched
   counts so that the effect of diverse rewriting can be separated from the
   effect of attaching certainty cues.
3. **Freeze a leave-one-cue-family-out evaluation.** Each run must test on a cue
   family absent from its training data. Keep layer 14 as the primary readout,
   the equal 28-layer score as the prespecified ensemble, and report every layer.
4. **Expand only after those gates pass.** Generate and review checkpoints at
   100, 300, and 700 sources. Preserve source-group boundaries and use one
   separately locked natural test set.
5. Extract hidden states once and fit the learning curves from cache. Compare
   the diverse pairs with the cue-only baseline using identical splits and
   paired source-level intervals.
6. Make a new explicit decision about whether a small functional loss pilot is
   justified.

## Pass conditions before expansion

- Blind human review finds no material content change or misplaced certainty
  scope in the final canary.
- The main condition uses genuine paraphrases rather than symmetric source
  copies.
- Cue placement, length direction, task, source, and output order are balanced.
- The baseline and cue-family holdout are fixed before activation scores are
  inspected.
- Record-level text remains private; public artifacts contain only code,
  settings, aggregate results, and hashes.

## Boundary

Correctness, evidence support, and semantic entropy remain separate diagnostics;
they are not labels for this experiment. No language-model training, activation
steering, or causal intervention is authorized in this phase. The downstream
four-arm loss proposal remains in
[NEXT_EXPERIMENT.md](../../docs/experiments/NEXT_EXPERIMENT.md), but it requires
a separate decision after the paired-data study is complete.

The full construction history and caveats are in
[DATA_CONSTRUCTION_GATE.md](reports/DATA_CONSTRUCTION_GATE.md).
