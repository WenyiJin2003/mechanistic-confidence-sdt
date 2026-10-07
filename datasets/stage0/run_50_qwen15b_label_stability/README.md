# run_50_qwen15b_label_stability: questions and sampled answers

[Repository](../../../README.md) · [All question sets](../../README.md)

[All Stage0 runs](../README.md)

50 questions; 1000 saved model samples. Model: `Qwen/Qwen2.5-1.5B-Instruct`. Source: `squad_v2`, original benchmark split: `validation`. Grouping: `bidirectional_strict_entailment`.

This is the stratified 50-question subset from `run_200_qwen15b`, with 20 saved answers per question. The first five samples are the original run's answers. Entropy values for 5, 10, and 20 samples are shown together.

- [Questions 1–25](questions-001-025.md)
- [Questions 26–50](questions-026-050.md)

Downloads and sources:

- [All saved sampled-answer rows (CSV)](samples.csv)
- [Raw questions and samples](../../../results/run_50_qwen15b_label_stability/combined_generations.jsonl)
- [Raw entropy](../../../results/run_50_qwen15b_label_stability/semantic_entropy_20.jsonl)
- [Results report](../../../reports/RESULTS_STAGE0.md)
- [Experiment guide](../../../docs/experiments/README_STAGE0.md)
