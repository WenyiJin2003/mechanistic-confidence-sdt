# Frozen confidence-readout transfer v2

Registered 7 October 2026, before v2 activation extraction or outcome inspection.

## Why this test

Paired pilot v1 decoded deliberately written certainty cues. Its family-C result
was 48/48 correct orderings, but the phrases were fixed, TF-IDF often tied, and
12/200 shuffled directions were also perfect. A useful bridge must go beyond
rewritten tone: does the **same frozen direction** respond to the availability
of evidence when the answer's wording is identical?

This test has two required endpoints: natural wording transfer and neutral-answer
evidence transfer. It evaluates the existing direction; it does not learn a new
direction from context differences. The research remains construct validation.

## Frozen artifacts and positions

Use the v1 Phase-B `layer14_boundary` direction without refitting, renormalizing
its sign, choosing thresholds, or selecting a new layer. Source data, states,
direction file and metrics are SHA-256 pinned in
[`configs/paired_confidence_transfer_v2.yaml`](configs/paired_confidence_transfer_v2.yaml).

Qwen2.5-1.5B-Instruct remains frozen at local snapshot
`989aa7980e4cf806f80c7fef2b1adb7bc71aa306`. Extraction matches v1: layer 14 after
the assistant `<|im_end|>` boundary, ID 151645. Separately fitted v1 directions
for layer-14 final content, layer-14 response mean, layer-23 boundary, and the
correctness-projected boundary direction are frozen secondary readouts. Never
apply the boundary direction at a different position and call that direct transfer.

## Test-only data

Construct 48 novel fictional registry facts: 12 each for access codes, assigned
rooms, release years, and materials. Keys, entities, distractors, label choices,
and row order are fixed with seed 20261008. These invented facts have a recorded
world key; they do not depend on real-world knowledge or a benchmark score.
All sources are transfer-test units. There is no v2 training or validation split.

Each source produces ten written responses (480 in total):

| Component | Context / response | Rows per source |
|---|---|---:|
| Natural wording | Supported context; correct/wrong content × confident/hedged | 4 |
| Neutral QA | Supported / target-role omitted / conflicting context; identical true-answer sentence | 3 |
| Neutral document wording | The same conditions; factual-summary request and identical sentence | 3 |

Natural pairs use 12 new unquoted phrasing types, balanced across fact types,
with shorter and longer confident versions. Preserve the answer proposition,
entities, values, qualifications, and format; add no evidence or second answer.
Avoid v1's explicit confidence-marker vocabulary. Record token/character length
differences and scores by wording type. This is authored natural wording, not
an unconstrained sample of model-generated answers.

For neutral comparisons, supported records assign the keyed value to the queried
role. Omitted records retain both candidate values and entity order but put the
keyed value in an unrelated field; the target-role fact is absent. Conflicting
records assign the distractor to the queried role. Record order is balanced.
No context uses cue words such as `confirmed`, `unknown`, `missing`, or `uncertain`.

Select unrelated field labels from predeclared semantically valid pools using
**tokenization only**, before activation scores. Require identical full prompt
token counts and identical response-token sequences within each neutral format
across all three conditions. Padding alone cannot equalize absolute token
positions. Save selected labels/counts and audit their meaning.

The world truth key stays fixed in the supported/omitted comparison: both use the
same neutral answer. The labels measure supplied-context sufficiency, **not the
model's true confidence**. Conflict additionally changes answer-context
consistency and is therefore auxiliary.

## Outcomes and decision rules

Score each state as \(s(h)=v_{\mathrm{v1}}^\top h\). A paired ordering is 1 for
a positive difference, 0 for reversal, and 0.5 for a tie. Average pairs within
source, then average sources equally. Use 2,000 source-bundle bootstrap draws
(seed 161803); use shared source draws for paired method differences.

Required endpoints:

1. **Natural wording:** confident > hedged on 96 content pairs / 48 sources,
   averaged over correct and wrong content within source.
2. **Neutral QA evidence:** supported > target-role-omitted on 48 otherwise
   identical response pairs / 48 sources.

Both must reach ordering accuracy at least 0.65 with bootstrap lower bound >0.5.
Natural correct/wrong subsets must each reach at least 0.60, and no fact type may
be below chance on either required endpoint.

Independent manipulation check: raw response log likelihood (negative mean-token
NLL) must order supported > omitted neutral QA contexts with accuracy at least
0.75 and bootstrap lower bound >0.5. If it fails, call the evidence bridge
inconclusive; do not rewrite items to obtain a pass. The four-source engineering
check inspects extraction and matching only, without outcome-based edits.

If natural wording passes but neutral evidence fails, the result supports wording
transfer only. If both pass with a valid manipulation check, describe controlled
context sensitivity of this frozen expressed-certainty readout. Neither outcome
establishes subjective confidence, causal control, calibration, or an SDT loss.
Secondary positions/document format cannot rescue a failed required endpoint.

## Controls and reporting

- Correct/wrong, fact-type, wording, and length strata.
- Teacher-forced sequence/mean NLL; the evidence check uses raw -NLL without
  learning an orientation from v2 labels.
- Word/bigram TF-IDF and a stronger character 3–5-gram control, fitted only on
  the original v1 training A/B rows with fixed C=1. The word baseline reproduces
  v1. Numeric v1 NLL classifiers may also be reconstructed on that same pool.
- Identical-neutral-response text baselines must tie across context conditions;
  this is a negative control for response-only predictors.
- Reconstruct and freeze the 200 source-sign-shuffled and 200 antipodal random
  boundary directions from the v1 training pool and seed. Report full ordering
  distributions, not permutation p-values or narrow per-direction chance bands.
- The frozen v1 correctness direction/projection are descriptive ablations.
- Prompt-state invariance applies to wording variants sharing a context. Neutral
  context changes deliberately change prompt states; audit by source + format +
  context condition rather than asserting invariance across those conditions.

Cache each forward immediately. Save full data audits, exact tokens/positions,
states, row scores, metrics, baselines/null vectors, hashes, and a comparison plot.
Report every failure without exclusions. No generation, NLI inference, API
inference, steering, fine-tuning, or confidence-loss training is part of v2.
