# Next Decision: Human-Review Direct Pairs Before New Probe Scoring

> **Current status (2026-10-13):** The frozen v3.8 shared-base canary remains
> rejected as main data. A replacement 50-pair direct-rewrite run now passes
> the automated construction gates; blind human review is pending. These are
> the already score-exposed challenge sources, so the packet is provider and
> recipe QA rather than a new probe evaluation. See
> [the construction report](../cue_holdout_challenge_v1/CHAT_PROVIDER_REPLICATION_50.md).

## Decision

**Do not score hidden-state layers on the current 100 pairs, start SDT loss
training, or scale to 1,000 pairs.** The earlier construction is mechanically complete,
but a label-blind diagnostic found systematic naturalness and cue-placement
confounds. V3.8 changed cue placement but retained a shared neutral base, so it
did not test natural full-response rewriting. The next experiment is a small,
fully reviewed direct-rewrite recipe in which both pair members are directly
and completely rewritten from the same source. The 50-pair provider run now
passes automated checks; human review is the remaining gate.

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

## Why v3.8 stopped before human review

V3.8 preserved one neutral base and changed only one or two minimal,
detachable certainty cues per pair. Fifteen of its 20 main pairs differ by one
Qwen token and five differ by two; in total, there are 25 differing Qwen-token
positions, measured against 5,102 confident-side Qwen tokens (0.49%). This is a valid cue-only shortcut
condition, not a natural confident–hesitant rewrite dataset. Human ratings of
fluency or content preservation cannot repair that scientific mismatch.

## Immediate sequence

1. **Retain v3.8 only as a diagnostic/control.** Do not continue its human
   review or treat it as main data.
2. **Human-review the completed 50-pair direct-rewrite packet.** Report content
   preservation, intended A/B-label direction, naturalness, cue scope,
   formatting, distributed rewriting, and accept/discuss/reject decisions.
3. **If it passes, freeze the source-eligibility and rewrite recipe.** The
   current sources are score-exposed and cannot become a new test set.
4. **Apply the frozen recipe to fresh, unscored sources.** Repeat the complete
   mechanical and blind human review gates before inspecting activations.
5. **Then freeze shortcut controls and score once.** Predefine the matched
   cue-only baseline and leave-one-cue-family-out evaluation; cache all hidden
   layers and report layer 14, every layer, the fixed ensemble, text,
   likelihood and length on identical splits.
6. Expand to 300 and 700 sources only if the fresh unscored study supports
   continuation. Make a separate decision before any functional loss pilot.

## Canary pass conditions

- All reviewed pairs preserve answer content, show a clear speaker-level certainty
  contrast, and verify the intended confident/hesitant A/B direction.
- Both members are complete rewrites; where genre and length permit, the
  contrast is distributed through the response. It cannot reduce to deleting
  one generic sentence or swapping one local polarity word.
- Naturalness and cue scope pass under a label-blind review, including the
  difficult genres identified above.
- Format, code, numerical values and user-requested constraints are preserved.
- Failures are recorded rather than silently repaired after seeing activation
  scores.
- The unscored-set rendering rules and later probe protocol are frozen before
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
