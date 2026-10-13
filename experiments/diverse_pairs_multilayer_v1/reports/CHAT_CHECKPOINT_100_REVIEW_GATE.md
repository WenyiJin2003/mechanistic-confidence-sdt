# Review Gate for the 100-Source Checkpoint

## Conclusion

**The 100-source construction is mechanically complete, but the current
rendered pairs are not ready for activation scoring.** A label-blind,
model-assisted diagnostic found that content preservation and a clear certainty
contrast were strong in the reviewed cases, while naturalness and cue placement
were not. The review did not record or verify which blind A/B arm matched the
intended confident or hesitant label.

This result changes the next step. We will retain the neutral paraphrases, test
a genre-aware rendering method on a fully reviewed 20-pair canary, and only
then decide whether to repair the full 100. We will not score layers or train a
loss on the current rendering.

## Two-stage diagnostic

### 1. Local NLI triage

A local `cross-encoder/nli-deberta-v3-small` pass compared each original
response with its marker-stripped neutral template in both directions. Long
responses were split into chunks and every cross-product chunk comparison was
scored.

| Item | Result |
|---|---:|
| Source–template pairs | 100 |
| NLI judgments | 506 |
| Maximum observed pair length | 440 / 512 tokens |
| Truncated comparisons | 0 |
| Pairs flagged for review | 14 / 100 |

These flags are triage signals, not semantic-equivalence judgments. The NLI
model can miss cross-chunk claims and cannot judge naturalness or global cue
scope.

### 2. Label-blind model-assisted review

The diagnostic review covered all 14 NLI-flagged pairs plus a task- and
dataset-balanced diagnostic sample of 10 unflagged pairs. Pair order and the
intended confident/hesitant labels were hidden from the reviewer.

| Review criterion | Result |
|---|---:|
| Answer content preserved | **24 / 24** |
| Clear certainty contrast judged | **24 / 24** |
| A/B direction matched to intended labels | Not recorded or verified |
| Both versions clearly natural | **5 / 24** |
| Cue applies to the full response | 22 / 24 |
| Final decision: accept | 5 |
| Final decision: discuss | 4 |
| Final decision: reject | 15 |

By selection group, the 14 NLI-flagged cases produced 2 accept, 3 discuss and
9 reject decisions. The 10 task- and dataset-balanced unflagged cases produced
3 accept, 1
discuss and 6 reject decisions.

The reviewed set was intentionally diagnostic and nonrepresentative because it
included every NLI flag. These counts are therefore **not an estimated failure
rate for all 100 pairs**. The review was model-assisted rather than human, so it
is also **not human certification**. Its purpose was to decide whether the
current rendering was safe to score. It was not.

## Main failure mode

The fixed global cue sentences often read unnaturally when attached to lists,
tables, dialogue, code or worked examples. They also conflict with strict
format or length instructions, and phrases such as “my conclusion” are
inappropriate for some genres. These are placement and genre confounds even
when the underlying answer content is preserved.

## Decision

1. Keep the 100 neutral templates and the complete mechanical audit trail.
2. Define source-eligibility rules and genre-specific cue placement.
3. Build a 20-pair canary spanning the affected genres and review all 20
   blindly.
4. Only if that canary passes, repair and re-render the 100 pairs, repeat the
   full review gate, and freeze the cue-only and cue-family-holdout controls.
5. Only after those gates pass, extract hidden states once and compare layer
   14, every individual layer, and the fixed 28-layer ensemble.

The earlier positive probe evidence remains separate: the frozen layer-14
readout reached 47/50 and the fixed ensemble reached 48/50 on the independent
50-pair challenge. The present result is a data-quality decision about a new
100-source construction, not a reversal or extension of those probe scores.

## Reproducibility links

- [NLI triage configuration](../configs/local_nli_semantic_triage_chat_100_v37.json)
- [Public NLI triage report](CHAT_CHECKPOINT_100_NLI_TRIAGE.json)
- [NLI triage implementation](../src/local_nli_semantic_triage.py)
- [Blind-review configuration](../configs/blind_human_review_chat_100_v37.json)
- [Blind-review packet builder](../src/build_blind_review_packet.py)
- [Blind-review import and validation](../src/import_blind_review.py)
- [Public agent-diagnostic aggregate](CHAT_CHECKPOINT_100_AGENT_DIAGNOSTIC.json)

Source text, response pairs, per-example flags, reviewer notes and the unblinding
key remain in ignored local storage. Public files contain only configuration,
aggregate results, hashes and code.
