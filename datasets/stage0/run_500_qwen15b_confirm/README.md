# run_500_qwen15b_confirm: questions and sampled answers

[Repository](../../../README.md) · [All question sets](../../README.md)

[All Stage0 runs](../README.md)

500 questions; 5000 saved model samples. Model: `Qwen/Qwen2.5-1.5B-Instruct`. Source: `squad_v2`, original benchmark split: `validation`. Grouping: `bidirectional_strict_entailment`.

Each question also has Stage0B leave-one-out entropy for observed answer indices 0 (primary) and 3 (robustness). The observed sample is excluded from the nine-answer entropy target. Primary held-out test probabilities are shown only for the 99 rows in the saved test-prediction artifact.

- [Questions 1–25](questions-001-025.md)
- [Questions 26–50](questions-026-050.md)
- [Questions 51–75](questions-051-075.md)
- [Questions 76–100](questions-076-100.md)
- [Questions 101–125](questions-101-125.md)
- [Questions 126–150](questions-126-150.md)
- [Questions 151–175](questions-151-175.md)
- [Questions 176–200](questions-176-200.md)
- [Questions 201–225](questions-201-225.md)
- [Questions 226–250](questions-226-250.md)
- [Questions 251–275](questions-251-275.md)
- [Questions 276–300](questions-276-300.md)
- [Questions 301–325](questions-301-325.md)
- [Questions 326–350](questions-326-350.md)
- [Questions 351–375](questions-351-375.md)
- [Questions 376–400](questions-376-400.md)
- [Questions 401–425](questions-401-425.md)
- [Questions 426–450](questions-426-450.md)
- [Questions 451–475](questions-451-475.md)
- [Questions 476–500](questions-476-500.md)

Downloads and sources:

- [All saved sampled-answer rows (CSV)](samples.csv)
- [Raw questions and samples](../../../results/run_500_qwen15b_confirm/generations.jsonl)
- [Raw entropy](../../../results/run_500_qwen15b_confirm/semantic_entropy.jsonl)
- [Results report](../../../reports/RESULTS_STAGE0.md)
- [Experiment guide](../../../docs/experiments/README_STAGE0.md)
