# Factual Source Canary v1

## Current decision

**The 120-source core will use 40 ASQA responses, 40 QASPER author
abstracts, and 40 BillSum summaries.** FeTaQA is retained as a separate
20-source short-form external test, not as core training or layer-selection
data.

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
| `results/expanded_pool_v2_summary.json` | public | Expanded-pool aggregate statistics |
| `results/EXPANDED_POOL_V2_REPORT.md` | public | Expanded-pool mechanical audit |

## Decision boundary

This audit can approve a data-construction recipe. It cannot establish a
confidence representation. The existing score-exposed 100 pairs remain
development material and are not reused as a final test set.
