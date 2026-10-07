# Frozen transfer v2: all questions and authored answers

[Repository](../../README.md) · [All question sets](../README.md)

48 source questions and 480 authored response variants. These responses were constructed for controlled experiments and then teacher-forced through the model for saved measurements. They are not sampled model answers. Correctness and confident/hedged/neutral labels are dataset labels. Wording labels do not measure a model's subjective confidence.

Every response is shown below its question. Token positions and the saved primary layer-14 boundary readout are included. Readout values are experiment scores, not probabilities that an answer is true. Markdown rounds numbers to six decimals; CSV retains the saved numeric values. No scores were refitted or recalculated.

The 48 entities are fictional constructed worlds. The true key stays fixed when evidence is supported, omitted, or conflicting. A response labeled correct can therefore lack support in the supplied context. All 48 sources are test-only.

Start with the [access-code example](access_code.md#v2-access_code-01), [room-assignment example](room_assignment.md#v2-room_assignment-01), or [release-year evidence-order reversal](release_year.md#v2-release_year-02).

- [Access Code](access_code.md): 12 questions, 120 responses
- [Room Assignment](room_assignment.md): 12 questions, 120 responses
- [Release Year](release_year.md): 12 questions, 120 responses
- [Material](material.md): 12 questions, 120 responses

Downloads and sources:

- [All authored response rows (CSV)](responses.csv)
- [All source questions (CSV)](sources.csv)
- [Raw source items](../../data/confidence_transfer_v2/source_items.jsonl)
- [Raw authored variants](../../data/confidence_transfer_v2/variants.jsonl)
- [Saved extraction rows](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl)
- [Saved primary scores](../../results/paired_confidence_transfer_v2/transfer_metrics.json)
- [Results report](../../reports/CONFIDENCE_TRANSFER_RESULTS_V2.md)
- [Experiment guide](../../docs/experiments/CONFIDENCE_TRANSFER_README_V2.md)

Regenerate from saved artifacts with `python scripts/export_question_sets.py`. Source JSONL and result files remain authoritative.
