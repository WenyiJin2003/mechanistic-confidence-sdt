# Confidence–Correctness Separation v3

7 October 2026. Design and analysis are committed before any v3 model forward
pass or score inspection. This is a new independent measurement study. The
separate analysis of existing v1/v2 caches is exploratory and is not retroactively
preregistered by this document.

## Question

Does the old expressed-certainty readout distinguish the truth of an identical
answer under counterfactual contexts, and does its wording response survive in
both correct and incorrect conditions? This separates answer-text identity
from context-defined correctness. Contextual correctness and evidence support
still covary; neither is a ground-truth measurement of the model's belief.

## Frozen choices

Use the pinned local, unquantized Qwen2.5-1.5B-Instruct snapshot and the exact
extraction implementation used in v1/v2. The two primary candidates are the
separately fitted v1 layer-14 **final ordinary response token** direction and
the v1 layer-14 **response-content mean** direction. These candidates were
chosen after v2; their v2 outcomes remain exploratory, and v3 provides fresh
data. The old boundary-token direction is a reference, never a replacement
endpoint selected after seeing v3. Layer 23 is descriptive only.

All confidence vectors are loaded unchanged from the original v1 archive.
Correctness comparators are source-equal, style-balanced correct-minus-wrong
contrasts estimated exclusively from v1 training sources and A/B wording.
Their construction is fixed before v3 and reproduced from the old caches.
There is no v3 fitting, sign flip, threshold tuning, rank selection, or item
exclusion based on scores.

## Fresh data

48 new fictional entities, 12 each for access codes, assigned rooms, release
years and materials. None enters any readout fitting pool. Each base entity
has two candidate values kept in a fixed line order. In world A, candidate A
has the queried role and B has an unrelated role. In world B the role labels
swap, making B correct. An omitted context retains both candidate values
under unrelated role labels. No context contains confidence or uncertainty
markers.

For each of the two worlds, candidate A and B answers are each written in
confident, hedged and neutral styles: 12 rows per entity. The omitted context
has the two neutral answers: another two rows. Total: 672 written responses.
Three fresh wording families are fixed before extraction. Their labels refer
to authored expression, not subjective certainty. Omitted-answer correctness
is unlabelled; absence of evidence is not coded as a false answer.

Only the pinned tokenizer may select semantically valid role labels from
predeclared pools. Full rendered prompt lengths must match within each entity
across all three contexts. Identical-response comparisons must have identical
response token IDs and identical absolute response positions. Padding alone
does not satisfy these requirements. Save every label selection and token gate.
Extraction uses prompt groups, so its prompt-invariance check applies only to
responses with exactly the same question/context.

## Endpoints

Score `s(h) = v.T @ h`. Positive paired margins get 1, reversals 0 and ties 0.5.
Average within base entity, then average entities equally. Intervals use 2,000
base-entity bootstrap draws, preserving all worlds, values and styles together.

1. **Certainty wording:** confident > hedged with world and answer fixed.
   Four comparisons per entity, 192 overall. Report correct and incorrect
   content separately, plus wording-family and fact-type strata.
2. **Neutral true versus false:** for each candidate's identical neutral answer,
   score in its supporting world > score in the other world. Two comparisons
   per entity, 96 overall. Truth here is the supplied world's reference fact.
3. **Neutral supported versus omitted:** identical neutral answer in its
   supporting world > the omitted-role context. Two per entity, 96 overall.

Report all three endpoints for both primary candidates. A candidate earns
confirmation on this controlled sample only if all three orderings are at least
0.65, their source-bootstrap lower bounds exceed 0.5, and no fact type is below
chance. Wording within correct and incorrect cells must each exceed chance.
No single best candidate is selected as a validated confidence mechanism.

Raw negative mean-token NLL is an independent manipulation comparator. It must
reach 0.75 with lower bound above 0.5 on both neutral context endpoints. Failure
makes that context manipulation inconclusive; it does not permit rewriting
examples after score inspection. Report saturation of empirical bootstrap
intervals without claiming perfect population performance.

## Comparators and safeguards

- Frozen v1 confidence/correctness cross-readout results, plus removal of each
  one-dimensional estimated correctness contrast. Renormalized ordering and
  common-scale margins are distinguished. This does not erase all correctness.
- Frozen correctness vectors at the same token positions; these are competing
  explanations, not correctness gold standards.
- Response-only token length, which must tie for identical-answer context
  comparisons. Raw likelihood uses its predetermined higher-likelihood sign.
- 200 norm-matched antipodal random directions, fixed seed and no orientation
  selection. Report their distribution descriptively, not as permutation p-values.
- Certainty-by-correctness interaction margins, candidate-value balance,
  per-fact and per-wording failures. Keep all failures in the public catalog.
- Four-source engineering check, one source per fact type, before full extraction.
  Verify token positions and exact cache resume without inspecting scores.

Save raw inputs, cached states, exact extracted-token metadata, all scores,
source-level intervals, manifests, a plot, and a readable question/answer catalog.
Results speak to wording and context sensitivity. They do not establish internal
belief, calibration, causality, SDT learning gains, or resistance to relearning.
