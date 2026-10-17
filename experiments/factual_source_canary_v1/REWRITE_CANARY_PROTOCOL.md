# Factual Rewrite Canary Protocol

## Decision rule

**Do not scale the factual rewrite set unless all 12 canary pairs pass.** A
passing pair expresses the same answer twice while changing only the speaker's
commitment: one response is clearly confident and the other clearly hesitant.

This is a data-quality gate. It does not test model activations, train a probe,
or establish that a confidence representation exists.

## Frozen design

- 12 frozen sources: 4 ASQA, 4 QASPER, and 4 BillSum. Active source-set revision
  v4 restores all 12 originally selected core sources. It contains no source
  replacement because the provenance audit invalidated both earlier
  replacement triggers; this does not mean either restored source has passed.
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

## Source-set revision and replacement rule

The earlier rank-only backup rule is superseded. An audit found that choosing
the lowest unused `review_rank` within a dataset can substantially change the
frozen length/complexity profile even when the replacement inherits the same
profile label. After the required backup-metadata corrections, a second
model-assisted review independently confirmed the profile-aware v5 rule and
exact mapping, which were then frozen. This review is not human certification.

For each eligible backup candidate, word count, sentence count, and corrected
qualifier count are recomputed as candidate-included midranks over a 41-row
reference pool: the same dataset's 40 frozen accepted core rows plus that
candidate. Backup qualifier counts come from the audited v5 ledger. The 12
selected core rows take their qualifier counts from the hash-bound v4 freeze,
preserving all three pre-existing reviewer-metadata corrections. The assignment is then solved
globally within each dataset as a one-to-one minimum-total-squared-distance
match between candidate features and failed slots' preregistered profile
targets. A hash of the complete mapping provides the deterministic tie-break.
This prevents one attractive backup from being reused and avoids letting the
other backup candidates define a candidate's rank.

The verified, text-free plan assigns six backups and is frozen in
[`results/rewrite_canary_v5_replacement_plan.json`](results/rewrite_canary_v5_replacement_plan.json).
Replacements remain within the same dataset and preserve the failed source's
cue family, length direction, draft order, batch, position, generation order,
and preregistered experimental slot. This artifact authorizes no model call:
**replacement generation remains unauthorized and has not started.**

`verified_plan` means that the inputs, method, and exact optimum mapping are
hash-bound and reproducible. Both the source mapping and the complete
assignment input table have frozen hashes. It does not certify profile-match
adequacy. Two assignments remain visibly off-target in the v5 feature space,
and the old 40-row source-selection distances are not direct thresholds for
the candidate-specific 41-row scores. A separate adequacy gate is required
before any replacement generation decision.

The first v5 planning checkpoint omitted three qualifier-count corrections
already present in the v4 freeze. The omission was found before replacement
generation, the mapping freeze was reset, and the corrected calculation was
independently recomputed and refrozen. The selected source IDs did not change;
the QASPER and BillSum costs did. The corrected artifact supersedes that
planning checkpoint, and no generated pair depends on the earlier distances.

The restored 12-source freeze remains the explicit v4 source-set revision.
Preparation writes
`frozen_sources_v4.jsonl`, writer-visible `SOURCE_BATCH_XX_V4.jsonl`,
reviewer-authoritative `SOURCE_BATCH_XX_VALIDATION_V4.jsonl`, and v4 prompt and
freeze-manifest files. The private v1, v2, and v3 freezes, batches, prompts,
and generated pairs are retained unchanged. Validation batches contain the full
frozen records, including the reviewer-only semantic qualifier descriptors;
writer batches continue to withhold those descriptors. There are no active
replacement-source prompts in v4.

Revision v3 is recorded as `superseded_pre_generation`: its source-freeze
artifacts remain checksum-guarded, but no rewrite generation began from them.
The v2 BillSum replacement and v3 QASPER replacement mappings are both
superseded because their repair-budget triggers depended on invalid-schema
runs that exposed reviewer-only semantic descriptors to the writer. Those runs
are quarantined and consume no repair budget. A public, source-text-free
adjudication record binds this decision to a detailed private ledger.

## Post-selection reviewer-metadata corrections

Reviewer-only semantic descriptors may be corrected after source selection
when independent pre-review shows that they are not licensed by the frozen
response. Such a correction is not a source replacement and may not change the
selected source, response identity, experimental slot, or any writer-visible
field. The configuration records only the source ID, old descriptor hashes and
count, removed and retained hashes, new count, and a text-free correction
rationale; descriptor text remains private. A correction may clear an entirely
invalid list or remove only specifically hashed descriptors while retaining the
rest in their original order. Preparation fails closed unless the private
pre-correction and post-correction descriptor hashes match exactly. It then
serializes every writer-visible batch, prompt, replacement source, and
replacement prompt both before and after correction and requires the two byte
strings to match exactly. This revision-independent check prevents
reviewer-only changes from reaching the writer without reusing revision-specific
artifact hashes. A committed, text-free checksum inventory also causes
preparation to fail if any locally preserved v2 or v3 freeze artifact is
missing or changed. The correction is applied before the v4
reviewer-authoritative freeze and validation batches are written.

The current v4 correction ledger contains three source-specific entries: the
applicable corrections for two BillSum sources and the restored QASPER source.
The correction for the withdrawn BillSum backup is not active. No replacement
text is added. Optional coverage-gap suggestions are not part of the frozen
correction ledger.

## Pair provenance boundary at the v4 freeze

At the time of the v4 source freeze, all 12 pairs required fresh initial
generation. Every earlier factual-canary call had used the same continuing
writer thread after that context had seen reviewer-only semantic descriptors.
A later prompt being writer-safe by itself therefore does not make its output
cleanly isolated. All pre-v4 outputs are retained only as audit history, are
ineligible for reuse, and consume no repair budget.

The preregistered execution rule required only the three official v4 batch
prompts, each in a new isolated writer context that had not seen reviewer
metadata or earlier factual-canary prompts. Pair-specific repair prompts were
not authorized until these fresh outputs had been validated. Scale-up,
activation extraction, and probe fitting remain unauthorized. The historical
freeze summary and revision adjudication preserve this as-of-freeze state;
current progress is recorded in
`results/rewrite_canary_v4_current_checkpoint.json`.

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
complete pair rewrite from the frozen source. One repair attempt is allowed.
If that repaired pair is content-clean and misses only the preregistered length
gap by no more than two tokens, one final full-pair length repair is allowed;
it may not change the content decision. Any remaining failure enters the
model-assisted, same-dataset replacement process described above while
preserving the failed source's preregistered experimental slot. The frozen v5
plan is a necessary data-design gate, not generation authorization or human
certification; a separate decision is required before any replacement model
call. Outputs
produced under a discovered prompt-schema defect are rejected as invalid
pipeline runs rather than counted as source-specific repairs.

## Current v4 checkpoint

Fresh isolated generation yielded 2 mechanically clean pairs out of 12. There
was one repair attempt for each of the ten initial failures. Each writer-safe
full-pair repair exposed only the frozen writer-visible source and a typed,
nonsemantic length-policy failure code. After repair, 6 of 12 pairs are
mechanically clean and 6 still fail. None of the remaining failures satisfies
the final-repair exception: the failures include direction, protected-span,
ratio, or gap deviations greater
than the allowed two-token margin. A second model-assisted review independently
confirmed the profile-aware v5 rule, corrected backup metadata, and exact
six-source mapping. They were then frozen in a verified, text-free plan for six
same-dataset replacements. This is not human certification. Replacement
generation is still unauthorized and has not started. The six mechanically
clean pairs still require blind content review and are not yet certified. This
checkpoint is generated and hash-bound by
`src/build_factual_rewrite_current_checkpoint.py`; it records three isolated
initial contexts and three isolated repair contexts, GPT-6 Luna at low
reasoning effort, and no authorization for activation extraction or probe
fitting.

The checkpoint's `next_action` records the audit hold at the end of v4
generation and repair. The verified v5 replacement-plan artifact supersedes
that historical next-action field; it does not alter the v4 execution record.

## Scale boundary

Only a 12/12 pass permits expansion to the 120-source core. Averages cannot
hide a failed pair. Activation extraction begins only after the expanded data
has passed the same frozen checks and review process.
