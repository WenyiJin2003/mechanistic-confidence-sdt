# Next Decision: Validate the 100 Pairs Before Probe Scoring

## Decision

**Do not start SDT loss training or scale to 1,000 pairs.** The activation probe
has a positive bounded transfer result, and the 100-source construction
checkpoint is mechanically complete. The next uncertainty is whether the new
pairs are genuinely content-matched, natural, and resistant to certainty-word
shortcuts.

## What is established

- The frozen layer-14 readout transferred to 47/50 new pairs; the fixed
  28-layer ensemble reached 48/50.
- Text, likelihood, and length controls reached 34/50, 30/50, and 25/50 on that
  challenge, so those controls do not fully explain the hidden-state result.
- The target remains **expressed certainty about preserved answer content**,
  not correctness, evidence support, semantic entropy, subjective belief, or
  training benefit.
- The new development checkpoint contains 100 sources and passes **100/100
  final mechanical checks**. Nineteen records have at least one recorded repair;
  semantic and blind human review remain pending.
- The checkpoint is balanced across ten cue sets, response order, and which
  pair member is longer. It spans five task groups and two source datasets.
- These construction results do not add a new probe score and do not make the
  pairs validated training data.

## Immediate sequence

1. **Run an independent semantic audit and label-blind human review of the 100
   pairs.** Review content equivalence, speaker-level certainty, naturalness,
   and obvious shortcuts. Record failures rather than silently repairing a
   scored evaluation set.
2. **Freeze the cue-only baseline.** Use the same source identities and matched
   counts so that the effect of diverse rewriting can be separated from the
   effect of attaching certainty cues.
3. **Freeze a leave-one-cue-family-out evaluation.** Each run must test on a cue
   family absent from its training data. Keep layer 14 as the primary readout,
   the equal 28-layer score as the prespecified ensemble, and report every layer.
4. **Extract hidden states once and cache them.** Compare layer 14, every layer,
   the fixed ensemble, text, likelihood, and length on identical source-level
   splits with paired intervals.
5. **Expand to 300 and 700 sources only if the 100-source review and shortcut
   controls support continuation.** Keep a separately locked natural test set.
6. Make a new explicit decision about whether a small functional loss pilot is
   justified.

## Pass conditions before probe scoring

- Independent review finds no material content change or misplaced confidence
  scope in the retained pairs.
- Human reviewers can distinguish the intended certainty contrast without
  systematic answer-content differences.
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

The completed construction checkpoint and its audit trail are in
[CHAT_CHECKPOINT_100.md](reports/CHAT_CHECKPOINT_100.md).
