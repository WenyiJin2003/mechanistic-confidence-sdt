# Factual Source Canary v1

## Current decision

**The 120-source core will use 40 ASQA responses, 40 QASPER author
abstracts, and 40 BillSum summaries.** FeTaQA is retained as a separate
20-source short-form external test, not as core training or layer-selection
data.

**Source selection is now complete:** 120 core records and 24 backups passed
the locked primary review plus a recomputed secondary sample audit. See
`results/SOURCE_SELECTION_RESULTS.md`.

**The next gate is frozen but not yet passed:** a deterministic 12-source
rewrite canary selects 4 ASQA, 4 QASPER, and 4 BillSum responses and assigns
balanced confident/hesitant construction conditions. The full design and hard
pass criteria are in [`REWRITE_CANARY_PROTOCOL.md`](REWRITE_CANARY_PROTOCOL.md).
Preparing this canary does not authorize activation scoring; all 12 pairs must
first pass mechanical checks and blind content review.

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

Full source text stays under ignored `private_data/`. No rewrite model is
called, no Qwen activations are extracted, and no probe is trained.

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
  --sources experiments/factual_source_canary_v1/private_data/rewrite_canary_v1/frozen_sources_v2.jsonl \
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
| `results/rewrite_canary_v1_freeze_summary.json` | public | Frozen balance checks and private-artifact hashes |
| `results/factual_rewrite_canary_status.json` | public | Aggregate gate and review status, with no record identities or text |
| `results/FACTUAL_REWRITE_CANARY_STATUS.md` | public | Plain-language canary status and decision boundary |

## Decision boundary

This audit can approve a data-construction recipe. It cannot establish a
confidence representation. The existing score-exposed 100 pairs remain
development material and are not reused as a final test set.
