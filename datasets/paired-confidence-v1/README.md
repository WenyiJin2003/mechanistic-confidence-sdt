# Paired confidence v1: all questions and authored answers

[Repository](../../README.md) · [All question sets](../README.md)

120 source questions and 1440 authored response variants. These responses were constructed for controlled experiments and then teacher-forced through the model for saved measurements. They are not sampled model answers. Correctness and confident/hedged/neutral labels are dataset labels. Wording labels do not measure a model's subjective confidence.

Every response is shown below its question. Token positions and the saved primary layer-14 boundary readout are included. Readout values are experiment scores, not probabilities that an answer is true. Markdown rounds numbers to six decimals; CSV retains the saved numeric values. No scores were refitted or recalculated.

Each source has 12 responses: correct/incorrect content × confident/hedged wording × rewrite families A/B/C. Phase A uses the marked 24-source subset and families A/B; Phase B uses all 120 sources. The two split labels refer to separate experiment partitions, not the original benchmark's split. Saved measurements here are Phase B.

- [Factual QA](factual_qa.md): 40 questions, 480 responses
- [Arithmetic](arithmetic.md): 40 questions, 480 responses
- [Academic](academic.md): 40 questions, 480 responses

Downloads and sources:

- [All authored response rows (CSV)](responses.csv)
- [All source questions (CSV)](sources.csv)
- [Raw source items](../../data/paired_confidence/source_items.jsonl)
- [Raw authored variants](../../data/paired_confidence/variants.jsonl)
- [Saved extraction rows](../../results/paired_confidence_phase_b/extraction_rows.jsonl)
- [Saved primary scores](../../results/paired_confidence_phase_b/readout_scores.npz)
- [Results report](../../reports/PAIRED_CONFIDENCE_RESULTS_V1.md)
- [Experiment guide](../../docs/experiments/PAIRED_CONFIDENCE_README.md)

Regenerate from saved artifacts with `python scripts/export_question_sets.py`. Source JSONL and result files remain authoritative.
