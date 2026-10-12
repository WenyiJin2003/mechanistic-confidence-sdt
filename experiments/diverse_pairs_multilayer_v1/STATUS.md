# Diverse paired certainty / multi-layer status

Updated 11 October 2026. Revision 3 passed agent-assisted QA and the 50-pair
development diagnostic is complete. Individual human review is still pending;
no language-model training or causal intervention has been run.

| Step | Status | Evidence / next action |
|---|---|---|
| Complete handoff read and priority correction | completed | REDIRECTION_NOTE.md; historical reports retained |
| Workspace, environment and existing snapshot inspection | completed | LOCAL_RESOURCE_ASSESSMENT.md; independent branch/worktree |
| Public source access and schema precheck | completed | Both public preview endpoints parsed; pinned revisions recorded |
| Bounded source selection and development inventory | completed | 38 WildChat / 12 HelpSteer2 responses; pinned provenance, dedup screens; all train-development |
| Full 1,000-source group splits | deferred | The present recipe has strong shortcuts; do not scale it yet |
| Rewrite specification and first review packet | completed | GPT-6 Luna current-session workers; 50 pairs / 100 drafts; local HTML reviewer |
| Stronger hesitant wording (revision 2) | completed | User-requested hedge-only revision; confident versions and source texts frozen; first packet archived |
| Targeted content QA (revision 3) | completed | 40 kept, 10 revised, 50/50 accepted by a separate agent pass; not human review |
| Pilot rewriter authorization | completed | User requested resource-efficient model and 50 pairs; no independent paid API |
| Larger rewrite budget and quality decision | deferred | Build a counterbalanced challenge set before any scale-up |
| Human content review | pending | All 50 records remain human_review=pending |
| All-layer extraction and primary readout modules | completed | 100 responses, all 28 layers; final replay was 100 cache hits and zero forwards |
| Review-export validation and importer | completed | Exact packet/text hash and A/B checks; separate reviewed outputs; no actual export received |
| Limited model-forward benchmark | completed | 20 pairs / 40 responses, all 28 layers; final implementation 31.6 seconds; exact cache replay with zero forwards |
| Development layer-14 / ensemble comparison | completed | Both 50/50; no ensemble gain; surface controls also near-perfect |
| Independent cue/recipe-holdout challenge | next | New source groups, length counterbalancing, unseen cue families, blinded review |
| Final scientific evaluation protocol and split | planned | Freeze only after the challenge recipe is accepted |
| SDT training or activation steering | not authorized | Separate future decision |

Revision 3 retains three warnings about the original source answers (P002, P008
and P022). The answers were intentionally not corrected during style rewriting.
No final draft has an empty or identical pair, protected-code mismatch,
numerical-count warning or token-limit exceedance under the implemented rules.
These automated screens and the agent QA are not semantic certification by a
human reviewer. Private revision archives preserve every prior packet.

The main development result is deliberately narrow. Layer 14, the equal 28-layer
ensemble, every individual layer and character TF-IDF each ordered 50/50 pairs
correctly. Negative mean NLL ordered 49/50 and negative response length 47/50.
In 47/50 pairs the hesitant response is longer. Therefore this set establishes
easy separability, but cannot identify a preferred layer or rule out a shared
rewrite shortcut. The ensemble's 20-run shuffle control was also inconclusive:
two shuffled runs reached 100%. See the
[development report](reports/DEVELOPMENT_DIAGNOSTIC.md).

The regression suite checks hidden-state indexing, response spans, NLL shifting,
pair order, cache identity, source-disjoint folds, train-only transforms, metric
counts and stale review rejection. The focused final tests passed before the
diagnostic. The 50-card review workflow and final static packet checks also
passed; test annotations never changed the research data.

The earlier bounded engineering check covered 20 pairs / 40 responses and verified
finite `[40, 28, 3, 1536]` states, exact response spans, identical prompt controls,
padding invariance and zero-forward replay. The completed development cache now
covers 50 pairs / 100 responses. The final diagnostic replay used 100 cache hits
and zero model forwards. See the
[engineering record](results/EXTRACTION_SANITY.json) and
[diagnostic JSON](results/DEVELOPMENT_DIAGNOSTIC.json).

Human-review action: open private_data/REVIEW_50_PAIRS_V3.html, assess content,
certainty order and confounds, and return the downloaded JSON. The canonical
REVIEW_50_PAIRS.html points to the same Revision 3 content. A/B positions are
randomized and each revision has a distinct browser-storage key.

Research action: preregister and construct approximately 50 new challenge pairs,
not 1,000 replicas of the current recipe. Use unseen sources and cue families,
counterbalance length direction, blind the content/tone review, then compare the
already defined readouts with TF-IDF, length and NLL under the same frozen score.
