# Raw experiment inputs

For ordinary reading, open the [question-and-answer collections](../datasets/README.md).
This folder holds the exact inputs used by the scripts.

| Folder | Contents | Readable version |
|---|---|---|
| [paired_confidence/](paired_confidence/) | 120 source records, 1,440 response variants, source/template audits and MMLU provenance | [V1 questions and answers](../datasets/paired-confidence-v1/README.md) |
| [confidence_transfer_v2/](confidence_transfer_v2/) | 48 fictional world keys, 480 response variants, token-matching checks and scoreless audit | [V2 questions and answers](../datasets/frozen-transfer-v2/README.md) |

Each `source_items.jsonl` contains one source per line. Each `variants.jsonl`
contains one authored response variant per line. Source and variant IDs identify
the same examples in the extraction files and readable exports.

The original Stage 0 question inputs and generated answers are recorded together
in each run's `generations.jsonl` under [results/](../results/README.md).
Their [readable collections](../datasets/stage0/README.md) expose the question,
reference answer, all sampled answers and cached entropy.

Raw input files and saved output artifacts retain their original paths and bytes.
Presentation changes do not alter the data used in the registered experiments.
