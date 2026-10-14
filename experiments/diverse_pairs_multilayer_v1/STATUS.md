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

**The v3.8 follow-up did not solve this problem.** Its genre-aware placement
changed where cues appeared, but the paired responses still shared the same
base text and differed only through minimal detachable cue substitutions. It is
therefore rejected as main paired-rewrite data and retained only as a cue-only
diagnostic/control. Human review of the v3.8 packets should stop.

**A replacement 50-pair direct-rewrite run now passes the automated construction
gates.** It uses the same score-exposed challenge sources, preserves the exact
5 × 5 × 2 grid and 25/25 length-direction balance, and reaches 50/50 mechanical
passes plus 50/50 shortcut-screen passes after eighteen unique pairs received targeted full-pair
regenerations. The project researcher judged the blind packet broadly
acceptable. The recipe is provisionally frozen and work is paused for advisor
review. No activations were inspected, so this does not change the probe result
or constitute an independent test. See the
[construction report](../cue_holdout_challenge_v1/CHAT_PROVIDER_REPLICATION_50.md).

| Item | Status | Result |
|---|---|---|
| Development probe | Complete | Layer 14 and the 28-layer ensemble both reached 50/50; text and length shortcuts remained |
| Cue/recipe-holdout challenge | Complete and score-exposed | Layer 14: 47/50; ensemble: 48/50 |
| Human review of the completed probe sets | Pending | Existing agent-assisted review is not human certification |
| 200-source rewrite review | Complete | 74 eligible, 110 rejected, 16 require human review |
| v3.3 full-pair canary | Rejected | 1 direct retain, 14 repairs, 5 discards out of 20 |
| v3.4 shared-base canary | Revised | 2 direct retains, 8 repairs out of 10 |
| v3.5 component canary | Historical gate result | 10/10 mechanical and independent semantic passes after repair; not current main data |
| v3.6 symmetric-copy canary | Control only | 0/10 paraphrase-gate passes; retain only as a lexical cue control |
| v3.7 two-stage canary | Historical gate result | 10/10 mechanical and independent model-assisted semantic passes after five record-level repairs; later rejected as a main recipe |
| Ordinary-Chat transport canary | Mechanical gate complete | 9/10 direct; 10/10 after one targeted numeric-preservation repair; GPT-5.6 was requested, but the exact executed model slug was not exposed |
| Historical v3.5/v3.7 canaries | Model-assisted gates complete | 20/20 mechanical and semantic passes; retained for provenance, not current main data, and not human-certified |
| Historical retained-canary human-review packet | Preserved; migration required before use | 20 earlier pairs retained only for provenance; its pre-binding manifest is rejected by the current importer and is not used by v3.8 |
| 100-source ordinary-Chat checkpoint | **Mechanically complete** | **100/100 final pass; 81 without recorded repair; 19 unique repaired records** |
| Local NLI triage | Complete | 506 bidirectional exhaustive-chunk judgments; 14/100 flagged; maximum 440/512 tokens with no truncation; triage only |
| Label-blind diagnostic review | **Complete; rendering gate did not pass** | **24 selected pairs: content preserved 24/24, clear contrast 24/24, intended A/B direction not recorded or verified, both natural 5/24; 5 accept, 4 discuss, 15 reject** |
| Full human certification | Not completed | Diagnostic review was model-assisted and the selected cases were nonrepresentative |
| v3.8 genre-aware canary | **Rejected as main data; preserve as control/provenance** | The 20 main pairs have 25 differing Qwen-token positions, measured against 5,102 confident-side Qwen tokens (0.49%); human review of the v3.8 packets should stop |
| 50-pair direct-rewrite provider run | **Broadly acceptable in one researcher screen; provisionally frozen** | 50/50 mechanical passes and 50/50 shortcut-screen passes after eighteen unique pairs received targeted regeneration; score-exposed recipe QA only |
| Advisor review | **Current pause point** | Decide whether to invest in one fresh, unscored evaluation; no new generation or activation scoring before discussion |
| Cue-only baseline and leave-one-cue-family-out test | Not frozen | Must be specified before probe scoring |
| 100-source layer comparison | Not started | Current rendering will not be scored; conditional on accepted direct full-pair rewrites and repeated review |
| 300/700-source expansion | Not started | Conditional on accepted paired rewrites and a successful fresh unscored result |
| SDT training or activation steering | Not authorized | Separate downstream decision |

The v3.3–v3.7 figures are sequential development results, not an unbiased method
benchmark. No full 1,000-pair run has been made.

## Rejected shared-base rendering

The v3.7/v3.8 rendering used two stages:

1. A language model produces one neutral, content-preserving paraphrase.
2. A local audited cue bank renders confident and hesitant versions from the
   same shared content.

This approach remains useful for a cue-only diagnostic, but it is no longer the
candidate main-data recipe. The v3.8 audit found that pair members were
effectively the same response plus one or two local cue substitutions. Human
naturalness review cannot resolve that shortcut. The replacement 50-pair run
rewrites both versions as complete responses with certainty integrated into the
substantive discourse. Its first qualitative screen is complete; advisor review
is now the active gate.

### Historical 100-source checkpoint

The ordinary-Chat workflow was previously exercised on 100 sources. The requested
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

1. Keep v3.8 frozen as a cue-only control and provenance record.
2. Record the 50-pair packet as broadly acceptable in one researcher screen,
   not as independent human certification.
3. Pause for advisor review. If continuation is agreed, apply the provisionally
   frozen recipe to fresh, unscored sources and repeat the full mechanical and
   human review gates.
4. Freeze the shortcut-control protocol before activation inspection.
5. Only then extract all layers once and report layer 14, every layer, and the
   fixed ensemble.
6. Expand to 300 and 700 sources only if the fresh unscored evidence
   warrants it.

The locked challenge must not be repaired or rescored. Private third-party text
and review files remain local and ignored. Historical canaries, failures, and
transport records stay in the repository as evidence but are not the current
execution plan.
