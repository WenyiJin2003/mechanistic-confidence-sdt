# Next Decision: Complete the Diverse-Pair Study Before Training

## Decision

**Do not begin an SDT loss experiment yet.** The completed 50-development /
50-challenge study is a strong bounded pilot, but it does not complete the
full diverse-pair handoff. The next phase should finish the missing data and
scale comparisons while preserving the locked challenge as score-exposed.

## What the bounded pilot established

- A frozen layer-14 response-mean readout transferred to 47/50 new pairs.
- The equal 28-layer ensemble reached 48/50, a two-point difference with a
  paired interval of 0–6 points; there is no current reason to prefer it over
  the simpler layer-14 readout.
- Character TF-IDF, answer likelihood and length reached 34/50, 30/50 and
  25/50. These controls do not fully explain the hidden-state result.
- The supported interpretation remains **expressed certainty about preserved
  answer content**, not correctness, subjective belief or training benefit.

## What remains unanswered

1. Does high-quality diverse rewriting outperform a matched fixed-template
   baseline when source identities and pair counts are identical?
2. Does transfer improve reliably with 100, 300 and 700 training source groups?
3. Do the current content-preservation and certainty labels survive human blind
   review?
4. Are task, source, length and cue-family results stable at useful scale?

## Immediate sequence

1. Human-audit both existing 50-pair sets. Because their scores are already
   exposed, do not repair and rescore them; any material failure downgrades the
   recorded result and requires a genuinely new test set.
2. Build a quality-gated source pool from HelpSteer2 and WildChat, targeting
   1,000 grouped sources and an approximately 700/150/150 train/validation/test
   split. Preserve group boundaries even if exact counts move.
3. On the same source IDs, construct both diverse rewrites and an explicit
   fixed-template baseline. Keep these conditions separate from text-feature
   controls such as TF-IDF, and complete human QA before final-test scoring.
4. Freeze one natural test set, extraction settings, layer 14, the equal-layer
   ensemble and all decision rules before score inspection.
5. Extract all layers once and fit the 100/300/700 learning curves from cached
   states. Report paired source-bootstrap intervals and failure cases.
6. Make one new decision about expansion or a functional loss pilot.

## Boundary

No language-model training, activation steering or challenge tuning is
authorized in this phase. Third-party source text, rewrites and reviewer files
remain private. The downstream four-arm loss proposal is retained in
[NEXT_EXPERIMENT.md](../../docs/experiments/NEXT_EXPERIMENT.md), but it is not
the current next experiment.
