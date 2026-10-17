# Factual Source Canary v1

## Current decision

**17 October: the rewrite rule is being corrected.** Epistemic “might,” “may”
and similar hedges can vary commitment to the same factual core. Legal
permission, enactment status and a study's stated evidence strength remain
protected. The researcher found weak and unnatural contrasts in the six v4
examples; a separate six-source development preview is ready for feedback under
[the revised rule](EPISTEMIC_REWRITE_UPDATE.md). The v4 counts and artifacts
below remain historical results under the previous rubric.

The [preview status](results/epistemic_preview_v1_status.json) contains hashes
and provenance only. The six new drafts and a compact review page remain
private under `private_data/rewrite_canary_v1/epistemic_preview_v1/`.
Run `python3 src/prepare_epistemic_preview.py --render` from this experiment's
directory to rebuild the page from the saved drafts. No browser is opened.

**The blinded model review is complete:** 6/6 intended directions were
identified and 6/6 factual cores judged preserved. Both versions were fully
natural in 2/6 pairs; the other issues were minor. All six hesitant responses
are longer. The [review report](results/EPISTEMIC_PREVIEW_REVIEW.md) explains
these construction diagnostics and the next recipe changes. Researcher
feedback remains pending; these counts are not probe performance.

**The 120-source core will use 40 ASQA responses, 40 QASPER author
abstracts, and 40 BillSum summaries.** FeTaQA is retained as a separate
20-source short-form external test, not as core training or layer-selection
data.

**Source selection is now complete:** 120 core records and 24 backups passed
the locked primary review plus a recomputed secondary sample audit. See
`results/SOURCE_SELECTION_RESULTS.md`.

**The first v4 generation-and-repair cycle is complete, but the 12-source
rewrite canary has not passed.** It contains
4 ASQA, 4 QASPER, and 4 BillSum responses with balanced confident/hesitant
construction conditions. Fresh isolated generation produced 2/12 mechanically
clean pairs. Each of the ten initial failures then received exactly one
writer-safe full-pair repair; this raised the clean count to 6/12. The other
6/12 still fail frozen mechanical rules, and none qualifies for the narrowly
allowed final length-only repair. A separate, deterministic blind-review packet
was prepared for the six mechanically clean pairs. It is an interim
failure-discovery step, not the final 12-pair review or human certification.
Two independent blinded model-assisted reviewers have now completed that
interim review. They agreed on **0/6 strict passes**: three pairs fail the
content/qualifier/scope gate, and the other three fail at least one direction,
naturalness, or shortcut gate. See
[`results/CLEAN_SIX_MODEL_REVIEW.md`](results/CLEAN_SIX_MODEL_REVIEW.md).
The text-free packet-generation record is
[`results/rewrite_canary_v4_clean_six_packet_summary.json`](results/rewrite_canary_v4_clean_six_packet_summary.json).
Current review results are tracked separately in
[`results/rewrite_canary_v4_clean_six_model_review_summary.json`](results/rewrite_canary_v4_clean_six_model_review_summary.json).
The reproducible, text-free current ledger is
[`results/rewrite_canary_v4_current_checkpoint.json`](results/rewrite_canary_v4_current_checkpoint.json),
and its aggregate validator projection is in
[`results/rewrite_canary_v4_post_repair_validation_summary.json`](results/rewrite_canary_v4_post_repair_validation_summary.json).

The active source set is revision v4. It restores all 12 originally selected
core sources and contains no source replacements. A provenance audit found
that both earlier replacement triggers depended on repair prompts that exposed
reviewer-only semantic descriptors to the writer, so those runs are invalid
and do not consume repair budgets. This correction does not certify the
restored sources or their pairs. Private v1/v2/v3 artifacts remain intact, and
the preserved v2/v3 freeze artifacts are checksum-guarded.

The v4 pairs were regenerated with GPT-6 Luna at low reasoning effort, using
one isolated writer context per batch. This writer only constructs the data;
it is not the Qwen model that will later be probed. The failed initial pairs
received one repair attempt each, generated in three fresh isolated repair
contexts from the frozen source and generic length rules only; prior candidate
text and reviewer-only semantic metadata were withheld. Six pairs remain
eligible for blind content review, and their private packet has received two
model-assisted reviews. Human adjudication remains pending. For the other six,
the rank-only backup rule
was rejected because it could substantially change the frozen
length/complexity profile. A model-assisted independent re-review accepted 18
unused backups and froze the exact mapping produced by the profile-aware v5
rule. This is not human certification. For each eligible backup, word count,
sentence count, and corrected qualifier count are recomputed as midranks in a
candidate-specific 41-row pool: the dataset's 40 accepted core rows plus that
candidate. Backup qualifier counts come from the audited v5 ledger; qualifier
counts for the 12 selected core rows come from the hash-bound v4 freeze, so its
three pre-existing reviewer-metadata corrections are retained. A global
same-dataset, one-to-one assignment then minimizes total squared distance to the
six failed slots' frozen profile targets, with a deterministic full-mapping hash
tie-break. The resulting text-free artifact reports `status: verified_plan`
and binds six replacements while preserving every slot allocation:
[`results/rewrite_canary_v5_replacement_plan.json`](results/rewrite_canary_v5_replacement_plan.json).
**Replacement generation remains unauthorized and has not started.** A
text-free supersession record
for the earlier invalid runs is in
`results/rewrite_canary_v1_revision_adjudication.json`; that record and the
freeze summary are explicitly labeled historical snapshots as of the v4
source freeze, rather than current progress ledgers. **This is a data-quality
and pipeline result, not evidence of a confidence representation.** Expansion
to 120 sources, activation extraction, probe fitting, and SDT loss training
remain blocked.

The v5 mapping covers only the six original mechanical failures. If human
adjudication confirms the clean-six review, the final failure set will expand
and v5 must be recomputed before any replacement generation. Because the new
failures include semantic drift, weak contrast, and shortcut language, source
replacement alone may not be sufficient; the rewrite recipe itself may need to
change.

The verified status is deliberately narrow: the mapping is reproducible and
globally optimal within the accepted backup pool, but no profile-adequacy rule
was frozen. Two selected backups remain visibly off-target in the v5 feature
space: their squared distances are 0.4006 and 0.1574, with largest coordinate
errors of 0.6171 and 0.3878. Original source-selection distances used a
different 40-row reference and are therefore not direct thresholds for these
candidate-specific 41-row scores. Replacement generation stays on hold while a
separate, metadata-only adequacy rule and the final failed-slot set are frozen.

An earlier v5 planning checkpoint omitted three reviewer-only qualifier-count
corrections that already existed in the v4 freeze. This was detected before any
replacement generation. The planner now binds the private v4 freeze manifest,
overlays all 12 selected-core counts, and freezes both the mapping hash and a
hash of every assignment input. The six source IDs did not change; the
corrected QASPER and BillSum costs did. This corrected artifact supersedes the
earlier planning checkpoint without invalidating any generated data, because
none was generated from it.

This decision follows a locked, model-assisted review of 10 candidates per
dataset. The review found that real-source answers still require explicit
contradiction, provenance, missing-evidence, and qualifier checks. It did not
validate a confidence representation and is not a substitute for final human
review. See `results/MODEL_ASSISTED_SOURCE_REVIEW.md`.

## Purpose

This stage audits candidate source material before any confidence rewriting or
probe fitting. The immediate question is whether public, traceable factual
datasets contain enough responses that are:

- substantive enough for a full-response rewrite;
- supported by explicit evidence;
- suitable for a strong confident/hesitant contrast without changing facts;
- groupable by original page, table, paper, or bill to prevent split leakage.

The planned core canary size is **120 source responses = 120 pairs = 240
rewritten texts**. A separate 20-source FeTaQA set evaluates short-form
transfer after the core pipeline is fixed.

## Candidate sources

| Stratum | Role | Target |
|---|---|---:|
| ASQA | Long-form factual QA | 40 |
| QASPER | Author-written paper abstracts grounded in the full paper | 40 |
| BillSum | Human-written document summary and SDT-format bridge | 40 |
| FeTaQA | External short-form table-grounded test | 20 |

Natural Questions is not in this first audit because its long answer is a
selected evidence region rather than a human-written complete response. ToTTo
is not included because most targets are single sentences and it overlaps the
table-to-text source family already represented by FeTaQA.

## What this stage does

1. Fetch deterministic public slices through the Hugging Face dataset server.
2. Normalize source response, evidence, provenance, and leakage-group metadata.
3. Produce a local review table with full third-party text.
4. Commit only text-free hashes, length/evidence statistics, and aggregate
   results.

Source-level scientific or legal qualifications such as *may*, *estimated*,
or *suggests* are review flags, not automatic failures. They express part of
the underlying proposition and must remain unchanged in both eventual
certainty rewrites.

During the source-selection and canary-preparation substage, full source text
stays under ignored `private_data/`. Those preparation scripts do not call a
rewrite model, extract Qwen activations, or train a probe; the later v4 rewrite
generation is recorded separately above.

The canary preparation script writes three private four-source prompt batches,
a frozen private source file, and a text-free public manifest. It separates
semantic qualifier descriptions from literal protected spans, so descriptive
review notes are not incorrectly treated as exact quotations.

The [source acceptance protocol](SOURCE_ACCEPTANCE_PROTOCOL.md) fixes the
review order, decision meanings, dataset-specific checks, stopping rule, and
validation boundary before the expanded pool is reviewed.

The first mechanical pass confirmed that QASPER's annotated QA answers are
usually too short for the main full-response rewrite. The scientific stratum
therefore uses author-written abstracts as the source response and the paper
body as evidence. The original short QA formulation is not expanded with
model-generated facts.

## Run

```bash
python3 experiments/factual_source_canary_v1/src/build_source_audit.py \
  --config experiments/factual_source_canary_v1/configs/source_audit_v1.json
```

The script is resumable: downloaded row batches are cached locally and reused.

To build the larger candidate pool without changing the locked pilot audit:

```bash
python3 experiments/factual_source_canary_v1/src/build_source_audit.py \
  --config experiments/factual_source_canary_v1/configs/source_pool_expansion_v2.json \
  --output-tag expanded_pool_v2
```

The tagged run writes to separate private and public paths. It cannot overwrite
the 50-candidate files referenced by the completed diagnostic review.

The completed expansion contains 100 candidates each from ASQA, QASPER, and
BillSum, plus 50 FeTaQA short-form candidates. Mechanical screening retained
all 100 ASQA records, all 100 QASPER records, and 89/100 BillSum records. These
counts only define the review queue; they do not certify evidence support.

Prepare the deterministic 12-source rewrite canary with:

```bash
python3 experiments/factual_source_canary_v1/src/prepare_factual_rewrite_canary.py
```

The frozen design is in `configs/rewrite_canary_v1.json`. The public outputs
contain identifiers, hashes, allocations, and counts only; the question,
source response, qualifier text, and rewrite prompts remain private.

After the final 12 pairs have been validated, build the private blind-review
packet from the same frozen source and pair files:

```bash
python3 experiments/factual_source_canary_v1/src/build_factual_rewrite_review.py \
  --sources experiments/factual_source_canary_v1/private_data/rewrite_canary_v1/frozen_sources_v4.jsonl \
  --pairs experiments/factual_source_canary_v1/private_data/rewrite_canary_v1/WRITER_CANARY_12_FINAL.jsonl \
  --output-dir experiments/factual_source_canary_v1/private_data/rewrite_canary_v1/blind_review
```

The model-assisted pre-review ledger is also private. Its top-level schema is
`factual-rewrite-model-assisted-pre-review-v1`; it records
`review_type: model_assisted`, `blinded: true`, the exact `artifact_binding`
copied from the final validator summary, and 12 uniquely identified records
whose decisions are `pass`, `repair`, or `reject`. The public status builder
verifies that this binding matches the validator, shortcut-audit, and blind
packet bindings before combining any results.

Then build one concise public status page from the aggregate gate summaries
and private review metadata:

```bash
python3 experiments/factual_source_canary_v1/src/build_public_canary_status.py \
  --validation-summary experiments/factual_source_canary_v1/results/rewrite_canary_12_validation_summary.json \
  --shortcut-summary experiments/factual_source_canary_v1/results/factual_rewrite_shortcut_audit_summary.json \
  --pre-review experiments/factual_source_canary_v1/private_data/rewrite_canary_v1/MODEL_ASSISTED_PRE_REVIEW.json \
  --blind-review-manifest experiments/factual_source_canary_v1/private_data/rewrite_canary_v1/blind_review/BLIND_REVIEW_MANIFEST.json
```

The generated JSON and Markdown include only aggregate counts and input hashes.
They never copy source IDs, source text, rewrites, reviewer notes, or row-level
decisions. A completed blind-review form is reported as awaiting validated
import and adjudication; this status builder cannot claim human certification,
authorize activation scoring, or establish a confidence representation.

The final pair filename in the commands above is the planned merge target; use
the exact path recorded by the final merge provenance if it differs. All four
stage artifacts must contain the same canonical source/pair binding, so results
from different runs cannot be combined accidentally.

Rebuild the current text-free v4 execution checkpoint from the three initial
validator summaries, three repair manifests, the full post-repair validator,
and its bound pair artifact with:

```bash
python3 experiments/factual_source_canary_v1/src/build_factual_rewrite_current_checkpoint.py
```

The builder verifies that the repairs cover each of the ten initial failures
exactly once and that the public validator summary is the exact row-free
projection of the bound private validator output.

Rebuild the text-free v5 replacement plan from the frozen v4 slots, the
post-repair validator, and the two private v5 audit inputs with:

```bash
python3 experiments/factual_source_canary_v1/src/plan_factual_rewrite_replacements.py
```

The planner fails closed unless every input hash, source decision, qualifier
correction, same-dataset constraint, slot field, and frozen mapping agrees. A
`verified_plan` still leaves replacement generation and every downstream
authorization set to `false`.

Build the current interim review packet for only the six mechanically clean v4
pairs with:

```bash
python3 experiments/factual_source_canary_v1/src/build_factual_rewrite_clean_subset_review.py --overwrite
```

The script first verifies all 12 frozen sources, pairs, validation rows, input
hashes, and the full artifact binding. It then selects only rows with no
mechanical failure flags. The six-row A/B order is deterministic and balanced
3/3 overall, with the closest possible balance across dataset, length direction,
and writer order. Only
`private_data/rewrite_canary_v1/blind_review_clean6_v4/reviewer_only/BLIND_REVIEW.html`
should be given to a reviewer; the A/B key is stored separately under
`private_key/`. The packet cannot be imported as the final 12-pair review.

Build the deterministic review order with:

```bash
python3 experiments/factual_source_canary_v1/src/build_review_queue.py \
  --candidates experiments/factual_source_canary_v1/private_data/expanded_pool_v2/source_candidates.jsonl \
  --config experiments/factual_source_canary_v1/configs/source_pool_expansion_v2.json \
  --private-output experiments/factual_source_canary_v1/private_data/expanded_pool_v2/source_review_queue.jsonl \
  --public-output experiments/factual_source_canary_v1/results/expanded_pool_v2_review_queue_manifest.jsonl \
  --batch-size 20
```

## Outputs

| Output | Visibility | Contents |
|---|---|---|
| `private_data/source_candidates.jsonl` | local only | Full response and evidence text |
| `private_data/source_audit_template.csv` | local only | Human-review worksheet |
| `results/source_candidate_manifest.jsonl` | public | Text-free hashes and audit metadata |
| `results/source_audit_summary.json` | public | Aggregate counts and distributions |
| `results/SOURCE_AUDIT_REPORT.md` | public | Plain-language audit report |
| `results/model_assisted_review.json` | public | Text-free record decisions and reason codes |
| `results/MODEL_ASSISTED_SOURCE_REVIEW.md` | public | Review findings and revised selection gate |
| `results/expanded_pool_v2_candidate_manifest.jsonl` | public | Text-free 350-record expanded-pool manifest |
| `results/expanded_pool_v2_review_queue_manifest.jsonl` | public | Locked, text-free review order and batches |
| `results/expanded_pool_v2_summary.json` | public | Expanded-pool aggregate statistics |
| `results/EXPANDED_POOL_V2_REPORT.md` | public | Expanded-pool mechanical audit |
| `results/selected_core_sources_v1_manifest.jsonl` | public | Text-free 120-core and 24-backup selection |
| `results/source_selection_v1_summary.json` | public | Review counts, hashes, and completed-gate status |
| `results/SOURCE_SELECTION_RESULTS.md` | public | Final source-selection conclusion and limitations |
| `results/rewrite_canary_v1_source_manifest.jsonl` | public | Text-free 12-source rewrite-canary allocation |
| `results/rewrite_canary_v1_freeze_summary.json` | public | Historical v4-freeze balance/provenance snapshot and private-artifact hashes |
| `results/rewrite_canary_v1_revision_adjudication.json` | public | Historical as-of-v4-freeze v2/v3 supersession and pair-provenance snapshot |
| `results/rewrite_canary_v4_current_checkpoint.json` | public | Reproducible v4 generation-and-repair counts, writer-context metadata, decisions, and artifact hashes |
| `results/rewrite_canary_v4_post_repair_validation_summary.json` | public | Aggregate mechanical result after one repair attempt for each of ten initial failures |
| `results/rewrite_canary_v4_clean_six_packet_summary.json` | public | Text-free record of how the separate six-pair interim blind-review packet was generated; current results are tracked separately and no downstream work is authorized |
| `results/rewrite_canary_v4_clean_six_model_review_summary.json` | public | Aggregate, text-free adjudication of two independent blinded model reviews; 0/6 strict passes and human adjudication pending |
| `results/CLEAN_SIX_MODEL_REVIEW.md` | public | Concise conclusion, method, aggregate gate results, and implications of the clean-six review |
| `results/rewrite_canary_v5_replacement_plan.json` | public | Verified text-free six-source replacement plan, model-assisted review provenance, profile-aware assignment method, artifact bindings, and explicit no-generation authorization; not human-certified |
| `private_data/rewrite_canary_v1/blind_review_clean6_v4/reviewer_only/BLIND_REVIEW.html` | local only | Label-blind reviewer page for the mechanically clean six; interim failure discovery only |
| `private_data/rewrite_canary_v1/blind_review_clean6_v4/private_key/BLIND_REVIEW_KEY.json` | local only | Separate A/B answer key; never distribute with the reviewer page |
| `private_data/rewrite_canary_v1/SOURCE_SET_ADJUDICATION_V4.json` | local only | Detailed invalid-run quarantine and source-set correction ledger |
| `private_data/rewrite_canary_v1/REPLACEMENT_SOURCE_SEMANTIC_AUDIT_V5.json` | local only | Model-assisted accept/hold decisions for all 24 backup sources; not human certification |
| `private_data/rewrite_canary_v1/REPLACEMENT_METADATA_CORRECTIONS_V5.json` | local only | Hash-bound qualifier corrections and audit provenance used by the v5 planner |
| `results/factual_rewrite_canary_status.json` | public | Aggregate gate and review status, with no record identities or text |
| `results/FACTUAL_REWRITE_CANARY_STATUS.md` | public | Plain-language canary status and decision boundary |

## Decision boundary

This audit can approve a data-construction recipe. It cannot establish a
confidence representation. The existing score-exposed 100 pairs remain
development material and are not reused as a final test set.
