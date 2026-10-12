# Next experiment: cue/recipe-holdout challenge

**Status: planned, not run.** This is the smallest useful follow-up to the
50-pair ceiling result. It stays on Cas's diverse paired-text research line; it
does not restart the v4 evidence-support route and does not train an SDT loss.

## Decision question

Does a readout trained on the current diverse pairs recognize expressed
certainty in new content when the obvious wording and length shortcuts are
deliberately counterbalanced?

## Data

- 50 new independent source groups, balanced across the same five task types.
- Both members of every pair are rewritten from the source response. Do not use
  the original response unchanged as the default confident member.
- Preserve propositions, numbers, conditions, code and reasoning.
- Use certainty constructions absent from the current training recipe and vary
  cue position, syntax and scope. Include compositional cases where the presence
  of words such as `certain` or `uncertain` alone gives the wrong prediction.
- Match structure and formatting within each pair. Make the confident response
  longer in 25 pairs and the hesitant response longer in 25; keep the absolute
  token difference within three tokens where practical.
- Freeze source IDs, pair text and recipe-family labels before activation scoring.
- Use blinded content/tone review. Agent QA can pre-screen, but cannot be recorded
  as human review.

All current 50 source groups and their derivatives are excluded. The challenge
text remains private until licensing and privacy review.

## Frozen models and scores

Fit the existing layer-14 paired logistic readout and equal 28-layer ensemble on
all current development pairs, using the already specified train-only feature
and score scaling. Apply them once to the locked challenge set.

Run the same fixed controls:

1. character TF-IDF trained only on the current 50 pairs;
2. negative mean response NLL;
3. negative response length;
4. mean-difference hidden-state direction;
5. 200 shuffled training-orientation fits, reported descriptively.

The primary outcome is confident-above-hesitant pair ordering for layer 14.
The ensemble comparison and every control use exactly the same 50 test pairs.
Intervals resample source groups; no test-set sign flip, layer selection,
threshold tuning or recipe repair is allowed after scoring.

## Decision rule

Use these rules before any test activations are inspected:

1. **Data gate:** before inspecting activations, repair or replace every pair
   that fails blinded content preservation or certainty ordering. Then freeze
   exactly 50 valid independent pairs, with the longer member confident in 25
   and hesitant in 25, preferably 5/5 within each task. Preserve task×family
   cell counts during replacement.
2. **Pilot transfer gate:** layer 14 orders at least 35/50 pairs correctly and
   its 95% source-bootstrap lower bound exceeds 50%. The shuffled-training
   distribution is descriptive and does not determine pass/fail.
3. **Incremental-value analysis:** compare layer 14 separately with each of
   TF-IDF, NLL and length. A gain of at least five pairs (10 percentage points)
   with a paired interval above zero supports added predictive value over that
   control. A tie or smaller gain means added value was not demonstrated; it
   does not prove that the readout captures only superficial wording.
4. **Ensemble gate:** prefer the ensemble only if it improves by at least three
   pairs and the paired interval is above zero. Otherwise prefer layer 14.

Any pilot transfer result must be repeated on a larger independently written and
human-reviewed set. Readiness for an internal training loss is a separate
decision: it also requires target-appropriate validation and a preregistered
training comparison judged by learning and retention, not probe scores alone.

Even a pass would validate transferable **expressed certainty**, not the truth of
an answer, evidence-sensitive confidence, or improved fact learning. Those are
separate later requirements for the proposed internal loss.
