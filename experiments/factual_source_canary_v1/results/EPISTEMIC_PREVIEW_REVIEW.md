# Six-pair epistemic rewrite preview: review and next step

**The new drafts make the intended certainty difference readable while
retaining the factual core, according to one blinded model-assisted review.**
They are useful recipe-development examples. They still need more natural,
varied wording and length counterbalancing before use in a larger probe study.

| Review judgment | Count |
|---|---:|
| Factual core preserved | **6/6** |
| Intended confident version selected | **6/6** |
| Clear certainty contrast | **6/6** |
| Both versions natural, with no issues noted | **2/6** |
| Neither version has major naturalness issues | **6/6** |

These are judgments about the text pairs. **They are not probe accuracy,
generated-answer correctness, or measured internal model confidence.** There
is one model reviewer and no structured human review of these new drafts yet.

## What was tested

The six sources are the same previously inspected three BillSum summaries and
three QASPER abstracts. There are no ASQA examples in this preview. A writer
received the original source responses and the revised epistemic rule. One
ambiguous “may learn” construction was clarified before this review; the
original draft hash and edit are recorded privately.

The reviewer saw only the original responses and randomized A/B texts. It did
not read the role key, writer JSON, or earlier reviews. Roles were balanced
3/3 in Version A. Its choices were compared with the key only after the review
was complete. The saved draft, HTML, packet and review hashes bind the result.

Both the text and the rubric changed relative to v4. Consequently, the old
**0/6 strict passes** and the new reviewer judgments are not a controlled
before/after comparison. The old result is preserved under its original rule.

## Remaining construction issues

**Length is associated with the label in all six pairs.** The confident
versions contain 841 whitespace-delimited words in total; the hesitant
versions contain 918. Choosing the shorter response would select the intended
confident arm in 6/6 pairs. This is a direct construction diagnostic, with no
fitted model or out-of-sample claim. These counts are words, not Qwen tokens.

**Hedge vocabulary is repetitive.** All six hesitant responses use the
seem/appear family, and several qualify nearly every sentence. The blind
review notes minor repetitive phrasing and inherited source-format issues.
Both arms remain close to the original wording and sentence order. This
preview supports a clear epistemic contrast, but does not yet demonstrate a
diverse full-rewrite recipe.

**The scope of uncertainty needs to stay visible.** In scientific summaries,
uncertainty about what a paper reports and uncertainty about its substantive
conclusion can overlap. Both may express hesitation, but the revised study
should record the distinction. A confident summary must still retain a source
finding qualified by “suggest,” “partly,” or “in simulation.” Such qualifiers
are not errors simply because they occur in the confident arm.

## Next construction batch

Use the saved six-pair page for researcher feedback. Prepare a small
development batch spanning ASQA, QASPER and BillSum before expanding the
120-source core. The next recipe should:

1. Keep the same factual core and allow clear epistemic uncertainty.
2. Rewrite both full responses naturally, using several constructions rather
   than inserting “seems” or “appears” before nearly every clause.
3. Preassign confident-longer and hesitant-longer cases independently of source
   and cue family, balanced within each dataset where the batch permits.
   Achieve this through natural paraphrasing, without deleting facts or padding.
4. Record observed word/token lengths and cue use; do not silently inherit the
   old v4 repair budgets or tight length cutoffs.
5. Preserve source groups for later splits. Keep these inspected development
   examples out of the eventual held-out probe evaluation.

This follows Cas's paired-data direction: better factual-rich text pairs,
then matched layer-14 and all-layer comparisons. Correctness, evidence support
and semantic entropy remain auxiliary diagnostics. No activations, probes or
SDT loss training were run in this review step.

The current next step is text review and recipe refinement. A larger run's
size and compute budget should be recorded before execution; this report does
not claim that such a run has started.

## Reproduce the aggregate result

With the private source, draft, role key, HTML and saved model review present:

```bash
python3 experiments/factual_source_canary_v1/src/summarize_epistemic_preview_review.py
```

The [text-free summary](epistemic_preview_v1_model_review_summary.json) records
the counts and all input hashes. The [revised rule](../EPISTEMIC_REWRITE_UPDATE.md)
defines the allowed epistemic change.
