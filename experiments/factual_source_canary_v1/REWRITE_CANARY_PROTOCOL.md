# Factual Rewrite Canary Protocol

## Decision rule

**Do not scale the factual rewrite set unless all 12 canary pairs pass.** A
passing pair expresses the same answer twice while changing only the speaker's
commitment: one response is clearly confident and the other clearly hesitant.

This is a data-quality gate. It does not test model activations, train a probe,
or establish that a confidence representation exists.

## Frozen design

- 12 previously accepted core sources: 4 ASQA, 4 QASPER, and 4 BillSum.
- Four deterministic coverage profiles per source family: short/simple,
  mid-length/plain, long/complex, and qualifier-sensitive.
- Five established rewrite strategies are allocated before generation.
- Confident-longer and hesitant-longer are balanced 6/6 overall and 2/2
  within each source family.
- The order in which the two versions are generated is balanced separately.
- The rewrite model sees the frozen question, response, and only those
  protected spans that occur literally in the response. It does not see the
  supporting evidence or reviewer-written semantic qualifier descriptors.
  The response is its sole content authority; it must not correct, supplement,
  or infer qualifications absent from that response.

Full third-party source text and generated pairs remain under ignored
`private_data/`. Public artifacts contain only identifiers, hashes,
allocations, aggregate checks, and review outcomes.

## Pair-level hard gates

Each pair must satisfy all of the following:

1. **Frozen identity.** The source ID, source hash, and response hash match the
   frozen input.
2. **Content preservation.** Both versions retain every claim, entity, number,
   condition, exception, comparison, causal scope, citation, and answer.
3. **Qualifier preservation.** Scientific, temporal, and legal qualifiers keep
   the same meaning and scope. Literal protected spans, when available, occur
   unchanged in both versions. Semantic qualifier descriptors remain private,
   are withheld from the writer, and are used only during manual review rather
   than treated as literal strings or generation instructions.
4. **Speaker-level contrast.** A blind reviewer selects the intended version
   as more confident and rates it at least two points higher on a five-point
   speaker-certainty scale.
5. **No object-level strengthening.** Certainty about the answer must not turn
   evidence into proof, permission into obligation, association into cause, or
   a qualified claim into an unqualified one.
6. **Natural full rewrites.** Both versions read naturally in the source genre.
   Neither may be a shared body with a detachable certainty sentence or a
   one-word cue swap.
7. **Matched presentation.** Response type, structure, detail, formatting, and
   helpfulness remain comparable.
8. **Controlled length.** Each version stays within 15% of source length; the
   pair-length ratio is at most 1.08; the absolute difference is no more than
   the larger of five tokens or 5% of the pair mean; and the assigned longer
   version is actually longer.

## Automatic shortcut screen

The mechanical screen rejects a pair when either version is the original
response verbatim, when removing a generic certainty sentence makes the
remaining bodies identical, or when a long pair changes too little text in too
few regions. It also flags reused certainty sentences and label-exclusive
words or phrases that could make the downstream task artificially easy.

These checks can reject obvious shortcuts, but they cannot certify semantic
equivalence or naturalness.

## Blind review

The reviewer sees only the frozen source, Version A, and Version B. The role
key is stored separately. For each pair the reviewer records:

- source fidelity;
- protected-qualifier preservation, using the private reviewer-only semantic
  descriptors after generation;
- whether the contrast is speaker-level;
- certainty of A and B on a 1–5 scale;
- which version is more confident;
- naturalness of both versions;
- formatting mismatch or shortcut concern;
- concise notes.

Any content, qualifier, scope, direction, or formatting failure triggers a
complete pair rewrite from the frozen source. One repair attempt is allowed;
otherwise the source is replaced by the next frozen backup from the same
dataset and the design is rebalanced.

## Scale boundary

Only a 12/12 pass permits expansion to the 120-source core. Averages cannot
hide a failed pair. Activation extraction begins only after the expanded data
has passed the same frozen checks and review process.
