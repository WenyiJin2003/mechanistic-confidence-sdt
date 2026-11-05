# Confidence probe scale-up data freeze

This directory contains a provider-free, collection-isolated split of existing confidence pairs. No model, tokenizer, forward pass, probe, or classifier was run to create it.

## Frozen files

| File | Rows | Role |
|---|---:|---|
| `train_200.jsonl` | 200 | Small nested training prefix |
| `train_500.jsonl` | 500 | Medium nested training prefix |
| `train_920.jsonl` | 920 | Full training set: accepted C1000 only |
| `dev_156.jsonl` | 156 | Development set: strict CF200 only |
| `internal_test_193.jsonl` | 193 | Untouched internal test: strict CF2 only |
| `external_cf3_113.jsonl` | 113 | Separate post-exposure robustness set |
| `EXCLUDED_CROSS_SPLIT_DUPLICATES_20.jsonl` | 20 | Complete audit of lower-priority duplicate exclusions |

`train_200` is the exact first 200 rows of `train_500`, which is the exact first 500 rows of `train_920`. Identity groups never cross either prefix boundary.

## Selection and leakage control

The priority is internal test > dev > train. Questions are normalized using Unicode NFKC, collapse of all whitespace to one ASCII space, trim, then Unicode casefold. A lower-priority row is audit-excluded if its normalized question or source ID occurs in a higher-priority split. This removes 20 rows: two from CF200 and 18 from C1000. All exclusions remain unchanged in the audit JSONL.

The top-level split is fully collection-isolated. Source IDs, normalized questions, exact questions, and identity groups have zero overlap across train/dev/internal-test. The original frozen input files and every generated file are byte- and SHA-256-pinned in `SPLIT_FREEZE.json`.

## Important limitation

Both dev and internal test contain only `factual_explanation` pairs. They can evaluate factual confidence-pair transfer, but they cannot support task-wide GO claims for programming, math, comparison, or summary tasks. CF3 was previously scored and has no completed human review, so it is labeled post-exposure robustness, not untouched confirmation.
