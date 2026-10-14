# Ordinary-Chat Provider Replication: 50 Paired Rewrites

## Conclusion

**The ordinary-Chat workflow produced all 50 direct confident/hesitant rewrite
pairs and passed both automated construction screens. On 13 October 2026, the
project researcher inspected the label-blind packet and judged it broadly
acceptable. The recipe is provisionally frozen while the next experiment is
discussed with the advisor. This remains a data-construction result only.**

The run reused the same 50 source groups from the already scored cue-holdout
challenge. It therefore cannot update the probe result or serve as an
independent evaluation. No activations were inspected or scored.

## Design and automated checks

- The frozen allocation is 5 tasks × 5 cue families × 2 pairs.
- The confident member is longer in 25 pairs and the hesitant member in 25.
- Every final pair differs by at most three tokens under the pinned
  Qwen2.5-1.5B tokenizer.
- Both members are complete responses, rather than one shared body with a
  detachable certainty sentence.
- Mechanical checks bind source hashes and test protected content, formatting,
  token direction, token gap, and grid membership.
- A separate shortcut screen checks generic certainty sentences, shared-body
  constructions, and very-high-similarity sparse edits.

Eighteen unique pairs received targeted full-pair regeneration across three
audit rounds: eight after the structural shortcut screen, eight after an
independent stratified pre-screen found that the confidence contrast was still
too local, and two additional watchlist pairs. One short pair required a second
rewrite pass. After the full audits were rerun, **50/50 passed the mechanical
validator and 50/50 passed the shortcut screen**, with no remaining automated
flags.

## Interpretation boundary

The automated checks and manual pre-screen do not certify semantic equivalence,
naturalness, or the intended confidence direction. The project researcher's
qualitative acceptance is a one-reviewer gate: no structured row-level export
was provided and inter-reviewer agreement was not measured. It should not be
described as independent human certification. The responses were generated
through an existing ordinary ChatGPT chat; the exact executed model slug was
not exposed.

Because the sources are score-exposed, this is a provider and rewrite-recipe
check, not a new probe experiment. If the advisor agrees to continue, the
provisionally frozen recipe should be applied to fresh, unscored sources before
any new activation or probe-performance claim.

## Reproducibility and data boundary

The public workflow is implemented in:

- [`src/prepare_chat_provider_replication.py`](src/prepare_chat_provider_replication.py)
- [`src/audit_provider_rewrites.py`](src/audit_provider_rewrites.py)
- [`src/merge_chat_repairs.py`](src/merge_chat_repairs.py)
- [`src/build_provider_review_html.py`](src/build_provider_review_html.py)
- [`reports/chat_provider_replication_50_summary.json`](reports/chat_provider_replication_50_summary.json)
- [`reports/chat_provider_replication_50_human_gate.json`](reports/chat_provider_replication_50_human_gate.json)
- [`manifests/chat_direct_pair_recipe_v1_freeze.json`](manifests/chat_direct_pair_recipe_v1_freeze.json)

Third-party source text, rewritten responses, row-level audits, and the blind
review packet remain in ignored `private_data/`. Only code and aggregate,
text-free results are committed.
