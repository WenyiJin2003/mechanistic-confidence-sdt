# Diverse Paired Certainty: Current Status

Updated 12 October 2026.

## Research result

**The bounded probe pilot passed its independent challenge.** A frozen layer-14
readout trained on 50 development pairs ordered 47/50 new confident–hesitant
pairs correctly; the fixed 28-layer ensemble reached 48/50. Character TF-IDF,
answer likelihood, and length reached 34/50, 30/50, and 25/50.

This supports a transferable signal for **expressed certainty about preserved
answer content** in this task. It does not establish correctness, evidence
support, subjective belief, causality, or usefulness as a training loss.

## Data-construction status

| Item | Status | Result |
|---|---|---|
| Development probe | Complete | Layer 14 and the 28-layer ensemble both reached 50/50; text and length shortcuts remained |
| Cue/recipe-holdout challenge | Complete and score-exposed | Layer 14: 47/50; ensemble: 48/50 |
| Human review of the completed probe sets | Pending | Existing agent-assisted review is not human certification |
| 200-source rewrite review | Complete | 74 eligible, 110 rejected, 16 require human review |
| v3.3 full-pair canary | Rejected | 1 direct retain, 14 repairs, 5 discards out of 20 |
| v3.4 shared-base canary | Revised | 2 direct retains, 8 repairs out of 10 |
| v3.5 component canary | Retained for final review | 10/10 mechanical and independent semantic passes after repair |
| v3.6 symmetric-copy canary | Control only | 0/10 paraphrase-gate passes; retain only as a lexical cue control |
| v3.7 two-stage canary | Retained for final review | 10/10 mechanical and independent model-assisted semantic passes after five record-level repairs |
| Combined retained canaries | Model-assisted gates complete | 20/20 mechanical and semantic passes; not human-certified |
| Blinded human-review packet | Ready | 20 pairs; reproducible A/B order, balanced 5/5 within each cohort; judgments pending |
| Blind human review of final 20 canary pairs | Pending | Required before expansion |
| Cue-only baseline and leave-one-cue-family-out test | Not frozen | Must be specified before probe scoring |
| 100/300/700-source learning curves | Not started | Conditional on the review and design gates |
| SDT training or activation steering | Not authorized | Separate downstream decision |

The v3.3–v3.7 figures are sequential development results, not an unbiased method
benchmark. No full 1,000-pair run has been made.

## Current method

The candidate main recipe uses two stages:

1. Claude produces one neutral, content-preserving paraphrase.
2. A local audited cue bank renders confident and hesitant versions from the
   same shared content.

Mechanical checks then test pair structure, length, cue placement, protected
content, and genuine paraphrasing. Independent semantic review checks content
equivalence and whether certainty belongs to the speaker rather than changing
the claim itself. Human review remains the final gate.

See the [data-construction report](reports/DATA_CONSTRUCTION_GATE.md) for the
full development table and the [challenge result](../cue_holdout_challenge_v1/RESULTS.md)
for the frozen probe evaluation.

## Immediate action

1. Complete blind human review of the final 20 canary pairs.
2. Freeze the matched cue-only baseline and leave-one-cue-family-out protocol.
3. If both gates pass, expand in checkpoints of 100, 300, and 700 sources.
4. Extract all layers once, reuse cached states, and report layer 14 plus every
   layer and the fixed equal-layer ensemble.

The locked challenge must not be repaired or rescored. Private third-party text
and review files remain local and ignored. Historical canaries, failures, and
transport records stay in the repository as evidence but are not the current
execution plan.
