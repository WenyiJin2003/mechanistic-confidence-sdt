# Diverse paired certainty / multi-layer status

Updated 11 October 2026. Revision 2 of the 50 rewrite pairs is ready for human review;
no certainty readout or language-model training results exist yet.

| Step | Status | Evidence / next action |
|---|---|---|
| Complete handoff read and priority correction | completed | REDIRECTION_NOTE.md; historical reports retained |
| Workspace, environment and existing snapshot inspection | completed | LOCAL_RESOURCE_ASSESSMENT.md; independent branch/worktree |
| Public source access and schema precheck | completed | Both public preview endpoints parsed; pinned revisions recorded |
| Bounded source selection and development inventory | completed | 38 WildChat / 12 HelpSteer2 responses; pinned provenance, dedup screens; all train-development |
| Full 1,000-source group splits | planned | Reserve pilot identities/groups outside final test; do not claim a locked full split |
| Rewrite specification and first review packet | completed | GPT-6 Luna current-session workers; 50 pairs / 100 drafts; local HTML reviewer |
| Stronger hesitant wording (revision 2) | completed | User-requested hedge-only revision; confident versions and source texts frozen; first packet archived |
| Pilot rewriter authorization | completed | User requested resource-efficient model and 50 pairs; no independent paid API |
| Larger rewrite budget and quality decision | blocked | Await actual human pilot audit and separate expansion estimate |
| Human content review | in_progress | User is the reviewer; all 50 records remain human_review=pending |
| All-layer extraction and primary readout modules | completed | Separate extractor; paired logistic, train-scaled equal ensemble, mean-difference and source-group bootstrap; synthetic tests only for readouts |
| Review-export validation and importer | completed | Exact packet/text hash and A/B checks; separate reviewed outputs; no actual export received |
| Limited model-forward benchmark | completed | 20 pairs / 40 responses, all 28 layers; final implementation 31.6 seconds; exact cache replay with zero forwards |
| Final scientific evaluation protocol and split | planned | Method choices specified in PROTOCOL.md; final sources and held-out recipe not frozen |
| OOF stacking and full evaluation driver | planned | Never substitute training-in-sample stacking |
| Main 2x2 comparison and learning curves | planned | Requires reviewed rewrites and frozen protocol; no test scores yet |
| SDT training or activation steering | not authorized | Separate future decision |

Revision 2 retains three original-source warnings (P002, P008 and P022).
The first packet's weaker certainty contrasts prompted this revision; its texts
and flags remain archived. No final draft has an empty
or identical pair, code/URL mismatch, numerical-count warning or token-limit
exceedance under the implemented rules. This is not semantic certification.
The most common normalized five-word hesitant opening occurs in 10/50 drafts.
Repeated uncertainty language remains a possible lexical shortcut; human audit
and later wording controls are still needed, even when the tone gap is clearer.
Two unusable original sources and their drafts were archived and replaced from
same-source/task reserves; all failures remain in ignored private_data.

The final historical-plus-new regression suite passed **181 tests**. Extraction
tests include the installed Qwen API's last-layer normalization, exact token
spans, NLL shift, strict pair ordering, content-bound caches and zero-forward
resume. Synthetic readout tests check positive confident-score orientation,
train-only transforms and equal source-group weighting. Review-import tests
reject stale text, packet hashes and incorrect A/B mappings.
Temporary headless Chrome tests
passed 50-card navigation, browser-local progress saving, and review JSON export;
test annotations were ephemeral and did not update the research data.
The first-packet quota observation is historical, not a quota estimate for the
additional revision. Shared-account usage cannot be isolated to these rewrites.
See REWRITE_BUDGET.md.

The engineering subset spans 94–729 input tokens and all five current task
categories. States have shape `[40, 28, 3, 1536]`, with response mean, last ordinary
response token and prompt negative control. All states are finite; maximum
prompt and padding state differences were zero. Final-code peak process RSS was
2.72 GiB and observed MPS driver allocation 4.17 GiB (overlapping accounting,
not additive). The exact 40-hit cache replay took 2.44 seconds. The initial
42.1-second run is retained as a summary; final-code revalidation followed a
strict input-order guard. No research probe was fitted and no final test scored.
See [engineering record](results/EXTRACTION_SANITY.json).

Next user action: open private_data/REVIEW_50_PAIRS_V2.html, assess content, certainty
ordering and confounds, and return the downloaded human_review_50.json.
The canonical REVIEW_50_PAIRS.html also contains revision 2. A/B positions are
randomized; the revised field is the actual hedged response, not always B.
Each revision has a distinct browser-storage key, so reviews of the first packet
do not silently certify changed text.
Next research action: receive the actual content-review export, apply validated
annotations without editing the draft packet, and decide a bounded source/rewrite
expansion. General tone approval is recorded as such, not individual approval.
