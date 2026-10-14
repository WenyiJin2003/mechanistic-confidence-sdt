# v3.8 Genre-Aware Placement Canary

## Post-audit outcome

**Rejected as main paired-rewrite data; retain only as a cue-only diagnostic
and provenance record. Human review of the v3.8 packets should stop.** The frozen protocol below
correctly documents what was built, but a structural audit showed that the two
members of each main pair share the same neutral base and differ only through
one or two minimal, detachable cue substitutions. Fifteen of 20 pairs differ by
one Qwen token and five differ by two. Across the 20 main pairs, there are 25
differing Qwen-token positions, measured against 5,102 confident-side Qwen
tokens (0.49%).

This construction can test sensitivity to explicit lexical cues. It cannot
serve as the intended natural confident–hesitant rewrite dataset, and a perfect
naturalness review would not change that limitation. The next main-data canary
must directly rewrite both complete responses from the same source. The
remaining sections are preserved unchanged as the frozen pre-audit design.

## Archived pre-audit protocol

**The sections below are retained for provenance, not as current instructions.**

## Decision scope

This 20-pair canary is an **engineering and naturalness gate only**. It asks whether confidence/hedging cues can be added to diverse, frozen responses without changing their non-cue content or damaging the response genre and structure.

A perfect review authorizes only the next data-construction step: applying the frozen renderer to separately screened, eligible **prose/list/fenced-code** sources and reviewing those outputs. It does **not** authorize applying the renderer to all 100 sources unchanged. Markdown tables, dialogue, and indented code are deferred and require their own canaries before inclusion. The gate also does not authorize activation scoring, probe training, leave-one-cue-family-out claims, population estimates, steering, or SDT loss training.

## What changed after the v3.7 diagnostic

The v3.7 failure was primarily a rendering failure. Generic stance sentences were inserted inside numbered lists, tables, dialogue, code explanations, and scientific-method sequences. Some cues also used nouns that did not fit the response genre.

v3.8 keeps the neutral content frozen and changes only the local renderer within a deliberately narrow genre scope:

- source eligibility is checked before rendering and fails closed on strict-output, persona/role-play, unsupported-structure, protected-only, or no-safe-boundary cases;
- the present renderer is eligible only for prose plus responses containing lists or fenced code; cues are inserted only at audited boundaries outside protected list/fenced-code blocks;
- Markdown tables, dialogue, and indented code are marked ineligible/deferred rather than treated as solved by this renderer;
- five cue families use response-specific referents such as `summary`, `solution`, `comparison`, `review`, and `method description`;
- main pairs use the frozen neutral paraphrase; cue-only controls add the identical cue design to the frozen original response;
- deleting the recorded insertion spans must recover the relevant base text byte-for-byte;
- confident and hedged versions must have exactly equal complete-response token counts under the pinned Qwen tokenizer.
- each six-field blind-review packet binds both its visible rows and the semantic A/B answer-key core, so a label swap changes packet identity and invalidates an older export.

## Frozen sample

The selection contains 20 unique sources:

- 10 previously diagnosed examples form an enriched **development set**: 6 prior `reject`/`discuss` cases and 4 prior accepted controls needed to satisfy the frozen cross-category quotas safely;
- 10 previously unseen examples form a **fresh diagnostic subset**, not an unbiased test;
- 4 examples per task, 5 per placement topology, 15 WildChat / 5 HelpSteer;
- 4 examples per cue family, with every cue-family × topology combination represented once;
- 10 confident-first / 10 hedged-first planned orders, with independently blinded A/B review packets.

For both the neutral main arm and original-response control arm, the selected structural coverage is **14 prose-only sources, 3 sources containing lists, and 3 sources containing fenced code**. It contains **0 Markdown-table, 0 dialogue, and 0 indented-code sources**. This coverage is frozen in the config and public manifest, and the builder rejects a selected base outside that scope.

Four initially considered sources were excluded rather than forced into unsafe positions: one persona response, two protected-structure-only responses, and one strict final-section response with no defensible late slot. Exact reason codes are frozen in the config.

## Review gate

The main and cue-only control packets must each receive label-blind review for:

1. content equivalence;
2. correct certainty direction (`A more certain` or `B more certain`);
3. naturalness;
4. global cue scope;
5. structure and format preservation.

The pass rule is **20/20 on every dimension**. Any failure requires a renderer repair and a fresh canary. Even a pass applies only to eligible prose/list/fenced-code sources; table, dialogue, and indented-code support remains untested. No activation is inspected before this gate is frozen and reviewed.

## Files

- Frozen config: `configs/genre_aware_canary_v38.json`
- Local builder: `src/build_genre_aware_canary_v38.py`
- Tests: `tests/test_genre_aware_canary_v38.py`
- Public text-free manifest: `manifests/genre_aware_canary_v38.json`
- Private rendered pairs and review packets: `private_data/genre_aware_canary_v38/`

The public manifest contains hashes and design metadata only. Source prompts, responses, rendered pairs, and the A/B answer keys remain under ignored `private_data`.
