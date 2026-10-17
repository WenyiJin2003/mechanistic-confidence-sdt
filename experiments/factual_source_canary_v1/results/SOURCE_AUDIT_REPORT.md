# Factual Source Audit v1

## Status

**Source retrieval and mechanical screening are complete. A fixed 10-record-per-dataset model-assisted diagnostic is also complete; final source review is pending.**
No confident/hesitant rewrites, hidden-state extraction, or probe fitting has been run.

See `MODEL_ASSISTED_SOURCE_REVIEW.md` for the record-level diagnostic, revised
source roles, and the gate before rewriting.

## Mechanical audit

| Dataset | Candidates | Heuristic pass | Median words | Main flags |
|---|---:|---:|---:|---|
| asqa | 50 | 50 | 71.0 | preserve_source_qualification: 5 |
| fetaqa | 50 | 0 | 17.0 | short_response: 50, single_sentence: 48 |
| qasper | 50 | 50 | 136.0 | preserve_source_qualification: 12 |
| billsum | 50 | 50 | 144.5 | preserve_source_qualification: 10 |

The screen is intentionally provisional: 40–220 words, at least two sentences,
and non-empty evidence. It is a triage rule, not a scientific label.

## Revised next gate

Expand each long-form candidate pool to 100 and review fixed blocks until
ASQA, QASPER, and BillSum each contain 40 accepted sources plus 8 accepted
backups. Keep FeTaQA as a separate short-response test. Freeze the accepted
sources and protected factual qualifiers before confidence rewriting.
