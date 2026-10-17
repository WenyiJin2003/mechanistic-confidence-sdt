# Factual Source Selection Results

## Conclusion

**The source-quality gate is complete for the 120-source core.** The frozen set
contains 40 ASQA responses, 40 QASPER author abstracts, and 40 BillSum
summaries. Each source also has eight accepted backups, for 48 effective
records per dataset.

This is a data-construction result. No confident or hesitant rewrite has been
generated, and no activation, probe, or loss has been evaluated on these
sources.

## Selection outcome

| Dataset | Primary records reviewed | Primary accepts | Secondary downgrades | Effective accepts | Core | Backups |
|---|---:|---:|---:|---:|---:|---:|
| ASQA | 74 | 51 | 3 | 48 | 40 | 8 |
| QASPER | 71 | 50 | 2 | 48 | 40 | 8 |
| BillSum | 88 | 52 | 4 | 48 | 40 | 8 |
| **Total** | **233** | **153** | **9** | **144** | **120** | **24** |

Primary review followed a locked, seed-based order and stopped only after a
dataset retained 48 accepted records. A separate deterministic 12-record sample
was then reassessed within each effective pool. When that audit found a problem,
the record was excluded, review continued to the next candidate, and the
secondary sample was recomputed. The final samples are **12/12 confirmed for
each dataset**.

## What the gate removed

The rejected or repair-required records included:

- answers that contradicted or exceeded their supplied evidence;
- ambiguous calendar-year, season-year, or “current” questions;
- exact scientific results available only in omitted tables or inconsistent
  between an abstract and paper body;
- legal summaries that omitted exceptions, conditions, or modal language;
- long, nested responses unlikely to survive two natural full rewrites without
  scope loss.

These are source problems, not confidence labels. They were handled before any
certainty manipulation.

## Frozen outputs

- `selected_core_sources_v1_manifest.jsonl` is the public, text-free manifest
  of 120 core records and 24 backups.
- `source_selection_v1_summary.json` records decision counts, audit counts,
  file hashes, and gate status.
- Full responses, evidence, reviewer notes, and protected qualifiers remain in
  ignored local files under `private_data/expanded_pool_v2/`.

## Validation boundary

The review was model-assisted, including the secondary audit. It is not
independent human certification. The result establishes a reproducible source
gate suitable for beginning a small rewrite canary; it does not establish that
the eventual pairs are natural, content-equivalent, or activation-valid.

The next operation should generate a small batch of direct, full-response
confident/hesitant rewrites from the frozen core, blind the A/B order, and check
content preservation, contrast strength, naturalness, and shortcut cues before
scaling to all 120 sources.
