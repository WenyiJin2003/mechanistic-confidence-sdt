# Stage0: all saved questions and sampled model answers

[Repository](../../README.md) · [All question sets](../README.md)

These are sampled model answers, including incorrect, incomplete, repetitive, and truncated answers. Every saved sample is shown unchanged. Reference answers are benchmark keys. Cluster-assignment entropy is the saved diversity target in nats; it is not a probability of correctness or a claim of subjective confidence.

Questions repeat across some runs. Run-specific sample IDs keep each saved answer traceable. The 500-question confirmation set records a fresh-source exclusion audit relative to the earlier 200-question 1.5B run. Stage0B annotations are attached to those same 500 questions, avoiding a duplicate question catalog.

- [preflight](preflight/README.md): 5 questions, 15 sampled answers, `Qwen/Qwen2.5-0.5B-Instruct`
- [run_a](run_a/README.md): 12 questions, 36 sampled answers, `Qwen/Qwen2.5-0.5B-Instruct`
- [run_b](run_b/README.md): 64 questions, 320 sampled answers, `Qwen/Qwen2.5-0.5B-Instruct`
- [run_200](run_200/README.md): 200 questions, 1000 sampled answers, `Qwen/Qwen2.5-0.5B-Instruct`
- [run_200_qwen15b](run_200_qwen15b/README.md): 200 questions, 1000 sampled answers, `Qwen/Qwen2.5-1.5B-Instruct`
- [run_500_qwen15b_confirm](run_500_qwen15b_confirm/README.md): 500 questions, 5000 sampled answers, `Qwen/Qwen2.5-1.5B-Instruct`
- [run_50_qwen15b_label_stability](run_50_qwen15b_label_stability/README.md): 50 questions, 1000 sampled answers, `Qwen/Qwen2.5-1.5B-Instruct`

[Stage0 results report](../../reports/RESULTS_STAGE0.md) · [Experiment guide](../../docs/experiments/README_STAGE0.md)

Regenerate from saved artifacts with `python scripts/export_question_sets.py`. Numeric CSV values retain stored precision; Markdown shows six decimals.
