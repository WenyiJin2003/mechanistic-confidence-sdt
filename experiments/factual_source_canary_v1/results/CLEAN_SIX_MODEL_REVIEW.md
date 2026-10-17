# Clean-Six Interim Blind Review

## Conclusion

**The current factual-rewrite recipe has not passed the data-quality gate.**
Two independent, label-blind model-assisted reviewers evaluated the six v4
pairs that had passed every mechanical check. Under the frozen strict rule,
**0/6 passed all content, certainty-direction, naturalness, formatting, and
shortcut checks**.

Both reviewers separated the six pairs the same way:

- **3/6 had content, qualifier, or scope drift.**
- **3/6 preserved the content but failed at least one other gate**, such as
  certainty direction, contrast size, naturalness, or shortcut resistance.

This is an interim diagnostic, not human certification. It is nevertheless a
clear reason to keep activation extraction, probe fitting, replacement
generation, and SDT loss training on hold.

## Method

The review builder first verified the complete frozen 12-pair set, all five
input hashes, the full validator coverage, and the source/pair artifact binding.
It then selected the six rows with no mechanical failure flags. The subset
contains three BillSum and three QASPER pairs; no ASQA pair passed the mechanical
screen.

Version A/B roles were hidden and balanced 3/3. Dataset, intended length
direction, writer order, and repeated cue families were counterbalanced as
tightly as the six-row design allows. Each reviewer saw only the question,
original response, and randomized Version A/B texts. The answer key was opened
only after both reviews were complete.

A strict pass required both reviewers to confirm all of the following:

1. both versions preserve the source content and qualifiers;
2. A and B remain mutually content-equivalent;
3. the difference is speaker-level rather than a change in evidence or claim;
4. the intended confident version is selected and scores at least two points
   higher on the five-point certainty scale;
5. both versions are natural;
6. formatting is matched and neither version relies on a shortcut cue.

## Aggregate result

| Unanimous gate | Pairs passing |
|---|---:|
| Content, qualifier, and speaker-scope gate | **3/6** |
| Intended confident version selected | **5/6** |
| Intended direction with at least a two-point certainty gap | **2/6** |
| Both versions rated natural | **3/6** |
| No formatting mismatch | **6/6** |
| No shortcut concern | **0/6** |
| **All strict gates** | **0/6** |

The reviewers agreed exactly on A/B content equivalence and on which version
sounded more certain for all six pairs. Each reviewer independently produced
zero strict passes.

One pair illustrates why direction and contrast are separate gates: both
reviewers explicitly selected the intended version as more certain, but each
gave its two versions equal numeric certainty ratings. The intended version
was therefore selected in **5/6** pairs under the frozen explicit-choice rule,
whereas score ordering alone would give **4/6**. This does not change the
two-point-gap result (**2/6**) or the strict result (**0/6**).

## Research implication

The mechanical screen was useful but insufficient: it did not catch
proposition-level drift, weak or reversed certainty contrasts, formulaic cue
sentences, or unnatural emphasis. These failures suggest a **rewrite-recipe
problem**, not merely a source-selection problem. Replacing sources alone may
therefore reproduce the same defects.

The frozen v5 mapping covers only the original six mechanical failures. If
human adjudication confirms the new review, the failed-slot set will expand and
that mapping must be recomputed before any replacement generation. The next
step is to human-adjudicate these six pairs, freeze the final failed-slot set,
and then decide whether to repair the two pairs that have not used a repair
budget or redesign the rewrite recipe more broadly.

## Boundary

This review evaluates constructed text pairs. It does not test Qwen hidden
states, establish a confidence representation, validate a mechanistic loss, or
support any causal claim.
