# Factual Source Pool Expansion v2

## Status

**Expanded source retrieval and mechanical screening are complete; final source review is pending.**
No confident/hesitant rewrites, hidden-state extraction, or probe fitting has been run.

## Mechanical audit

| Dataset | Candidates | Heuristic pass | Median words | Main flags |
|---|---:|---:|---:|---|
| asqa | 100 | 100 | 68.5 | preserve_source_qualification: 11 |
| fetaqa | 50 | 0 | 17.0 | short_response: 50, single_sentence: 48 |
| qasper | 100 | 100 | 141.5 | preserve_source_qualification: 24 |
| billsum | 100 | 89 | 153.5 | long_response: 8, preserve_source_qualification: 17, single_sentence: 3 |

The screen is intentionally provisional: 40–220 words, at least two sentences,
and non-empty evidence. It is a triage rule, not a scientific label.

## Revised next gate

Expand each long-form candidate pool to 100 and review fixed blocks until
ASQA, QASPER, and BillSum each contain 40 accepted sources plus 8 accepted
backups. Keep FeTaQA as a separate short-response test. Freeze the accepted
sources and protected factual qualifiers before confidence rewriting.
