# Next Decision: Fix Pair Rendering Before Probe Scoring

## Decision

**Do not score hidden-state layers on the current 100 pairs, start SDT loss
training, or scale to 1,000 pairs.** The construction is mechanically complete,
but a label-blind diagnostic found systematic naturalness and cue-placement
confounds. The next experiment is a fully reviewed 20-pair, genre-aware canary.

## What remains established

- The frozen layer-14 readout transferred to 47/50 independent challenge pairs;
  the fixed 28-layer ensemble reached 48/50.
- Character TF-IDF, answer likelihood and length reached 34/50, 30/50 and 25/50
  on that challenge. Those controls do not fully explain the earlier
  hidden-state result.
- The target remains **expressed certainty about preserved answer content**,
  not correctness, evidence support, semantic entropy, subjective belief or
  training benefit.
- The new checkpoint contains 100 sources and passes 100/100 mechanical checks.
  This construction result is separate from the earlier probe evidence.

## What the review gate found

Local bidirectional exhaustive-chunk NLI made 506 judgments, observed a maximum
of 440 tokens against a 512-token limit, used no truncation, and flagged 14/100
pairs for review. This was triage, not semantic certification.

A label-blind, model-assisted diagnostic reviewed all 14 flagged pairs plus a
task- and dataset-balanced diagnostic sample of 10 unflagged pairs:

| Result | Count |
|---|---:|
| Content preserved | **24/24** |
| Clear certainty contrast judged | **24/24** |
| A/B direction matched to intended labels | Not recorded or verified |
| Both versions clearly natural | **5/24** |
| Accept / discuss / reject | **5 / 4 / 15** |

The 14 flagged cases split 2/3/9 across accept/discuss/reject; the 10 unflagged
cases split 3/1/6. The selection deliberately oversampled NLI flags, so these
counts **must not be interpreted as a failure-rate estimate for all 100 pairs**.
The reviewer was model-assisted, not human, so this is also **not human
certification**.

The main failure was fixed global cue placement. Added sentences interrupt
lists, tables, dialogue, code and worked examples, conflict with strict format
or length constraints, and sometimes use genre-inappropriate “conclusion”
language. These artifacts could give a probe an easy shortcut.

## Immediate sequence

1. **Retain the neutral templates.** Do not regenerate content that passed the
   content-preservation diagnostic.
2. **Define source eligibility.** Exclude or specially handle responses whose
   requested format cannot naturally accommodate speaker-level calibration.
3. **Implement genre-aware cue placement.** Use renderers for prose, lists,
   tables, dialogue, code/examples and strict-format responses rather than one
   global insertion rule.
4. **Build a 20-pair canary and review all 20 blindly.** Cover the affected
   genres and report content preservation, clear contrast, intended A/B-label
   direction, naturalness, scope and accept/discuss/reject decisions.
5. **Only if the canary passes, repair and re-render the 100 pairs.** Repeat the
   complete review gate before inspecting activation scores.
6. **Then freeze shortcut controls and score once.** Predefine the matched
   cue-only baseline and leave-one-cue-family-out evaluation; cache all hidden
   layers and report layer 14, every layer, the fixed ensemble, text,
   likelihood and length on identical splits.
7. Expand to 300 and 700 sources only if the repaired 100-source study supports
   continuation. Make a separate decision before any functional loss pilot.

## Canary pass conditions

- All 20 pairs preserve answer content, show a clear speaker-level certainty
  contrast, and verify the intended confident/hesitant A/B direction.
- Naturalness and cue scope pass under a label-blind review, including the
  difficult genres identified above.
- Format, code, numerical values and user-requested constraints are preserved.
- Failures are recorded rather than silently repaired after seeing activation
  scores.
- The 100-source rerendering rules and later probe protocol are frozen before
  activation results are inspected.

## Boundary

Correctness, evidence support and semantic entropy remain separate diagnostics;
they are not labels for this experiment. No language-model training, activation
steering or causal intervention is authorized in this phase. The earlier 47/50
and 48/50 probe results remain positive bounded evidence, while the present
decision concerns the quality of a different, newly constructed dataset.

See the [review-gate report](reports/CHAT_CHECKPOINT_100_REVIEW_GATE.md),
[construction checkpoint](reports/CHAT_CHECKPOINT_100.md), and
[downstream loss proposal](../../docs/experiments/NEXT_EXPERIMENT.md).
