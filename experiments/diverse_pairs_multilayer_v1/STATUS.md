# Diverse Paired Certainty: Current Status

Updated 13 October 2026.

## Research result

**The bounded probe pilot passed its independent challenge.** A frozen layer-14
readout trained on 50 development pairs ordered 47/50 new confident–hesitant
pairs correctly; the fixed 28-layer ensemble reached 48/50. Character TF-IDF,
answer likelihood, and length reached 34/50, 30/50, and 25/50.

This supports a transferable signal for **expressed certainty about preserved
answer content** in this task. It does not establish correctness, evidence
support, subjective belief, causality, or usefulness as a training loss.

## Data-construction status

**The 100-source set is mechanically complete but not activation-ready in its
current form.** A label-blind, model-assisted diagnostic found preserved
content and a clear certainty contrast in all 24 reviewed cases, but it did not
record or verify A/B direction against the intended labels. Both pair members
were clearly natural in only 5/24. Fixed global cue placement creates genre and
formatting confounds, so probe scoring is paused.

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
| GPT-5.6 ordinary-Chat transport canary | Mechanical gate complete | 9/10 direct; 10/10 after one targeted numeric-preservation repair |
| Combined retained canaries | Model-assisted gates complete | 20/20 mechanical and semantic passes; not human-certified |
| Historical retained-canary human-review packet | Ready | 20 earlier pairs; reproducible A/B order, balanced 5/5 within each cohort; judgments pending |
| 100-source ordinary-Chat checkpoint | **Mechanically complete** | **100/100 final pass; 81 without recorded repair; 19 unique repaired records** |
| Local NLI triage | Complete | 506 bidirectional exhaustive-chunk judgments; 14/100 flagged; maximum 440/512 tokens with no truncation; triage only |
| Label-blind diagnostic review | **Complete; rendering gate did not pass** | **24 selected pairs: content preserved 24/24, clear contrast 24/24, intended A/B direction not recorded or verified, both natural 5/24; 5 accept, 4 discuss, 15 reject** |
| Full human certification | Not completed | Diagnostic review was model-assisted and the selected cases were nonrepresentative |
| Genre-aware 20-pair canary | Next | Add source eligibility and genre-specific cue placement; review all 20 blindly |
| Cue-only baseline and leave-one-cue-family-out test | Not frozen | Must be specified before probe scoring |
| 100-source layer comparison | Not started | Current rendering will not be scored; conditional on successful canary, repair and repeated review |
| 300/700-source expansion | Not started | Conditional on a successful canary and repaired 100-source result |
| SDT training or activation steering | Not authorized | Separate downstream decision |

The v3.3–v3.7 figures are sequential development results, not an unbiased method
benchmark. No full 1,000-pair run has been made.

## Current method

The candidate pair recipe uses two stages:

1. A language model produces one neutral, content-preserving paraphrase.
2. A local audited cue bank renders confident and hesitant versions from the
   same shared content.

The ordinary-Chat workflow has now been exercised on 100 sources. The requested
model family was GPT-5.6, but the exact Chat model slug was not exposed. The
final set contains 75 WildChat and 25 HelpSteer sources across five task groups,
ten balanced cue sets, balanced output order, and balanced longer-member
assignment. All 100 records pass final mechanical checks. Eighty-one have no
recorded repair; 19 have at least one, comprising 12 model-regenerated templates
and eight local template repairs with one overlap. Five sources were replaced
within the same strata before finalization.

One twenty-record response exceeded the thread read limit and was re-emitted in
groups of ten. One stale-ID response was rejected and retried. These are recorded
transport events, not missing data. The [checkpoint report](reports/CHAT_CHECKPOINT_100.md),
[freeze manifest](manifests/gpt56_chat_neutral_100_v37_freeze.json), and
[text-free summary](manifests/gpt56_chat_neutral_100_v37_summary.json) contain
the public audit trail.

Mechanical checks then test pair structure, length, cue placement, protected
content, and genuine paraphrasing. A local NLI triage made 506 bidirectional
chunk judgments and flagged 14/100 records. The subsequent label-blind
model-assisted review covered all 14 flags plus a task- and dataset-balanced
diagnostic sample of 10 unflagged records. The NLI-flagged group yielded
2 accept, 3 discuss and 9 reject decisions; the unflagged sample yielded 3, 1
and 6. Because this selection oversampled flags, it is a diagnostic rather than
a population-rate estimate. It is also not human certification.

The dominant issue was not changed answer content. Fixed global cue sentences
were unnatural or misplaced in lists, tables, dialogue, code and examples,
strict-format responses, and genres where “conclusion” language does not fit.

See the [data-construction report](reports/DATA_CONSTRUCTION_GATE.md) for the
full development table and the [challenge result](../cue_holdout_challenge_v1/RESULTS.md)
for the frozen probe evaluation. The
[review-gate report](reports/CHAT_CHECKPOINT_100_REVIEW_GATE.md) gives the new
aggregate results and decision.

## Immediate action

1. Retain the neutral templates and define source eligibility plus genre-aware
   cue placement.
2. Build a 20-pair canary across the affected genres and review every pair
   blindly.
3. Only if the canary passes, repair and re-render the 100 pairs, repeat the
   full review gate, and freeze the shortcut-control protocol.
4. Only then extract all layers once and report layer 14, every layer, and the
   fixed ensemble.
5. Expand to 300 and 700 sources only if the repaired 100-source evidence
   warrants it.

The locked challenge must not be repaired or rescored. Private third-party text
and review files remain local and ignored. Historical canaries, failures, and
transport records stay in the repository as evidence but are not the current
execution plan.
