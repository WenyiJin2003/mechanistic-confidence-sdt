# Questions and answers

Start here to inspect the actual experiment inputs and answers. Each collection
contains every saved source and response, not a selected set of successful
examples. The pages render directly on GitHub; CSV files provide the same rows
for download.

| Step | Collection | Sources | Responses | What the answers are |
|---:|---|---:|---:|---|
| 1–2 | [Stage 0 / 0B](stage0/README.md) | Listed separately by run | Every cached sample | Responses generated locally by Qwen from SQuAD prompts |
| 3 | [Paired Confidence v1](paired-confidence-v1/README.md) | 120 | 1,440 | Authored confident/hedged rewrites, with both correct and deliberately wrong content |
| 4 | [Frozen Transfer v2](frozen-transfer-v2/README.md) | 48 | 480 | Authored response pairs and identical neutral answers under different evidence conditions |
| 5 | [Confidence–Correctness Separation v3](confidence-separation-v3/README.md) | 48 | 672 | Authored responses; the same answer becomes correct or incorrect when contextual role assignments swap |
| 6 | Evidence-Sensitive Readout v4, in progress | 168 | 1,584 supplied responses; 144 independent behavior prompts | New source/template splits; fixed answers under three evidence conditions; model-generated answers added during the run |

The v4 collection will include every training, validation and test record, all
three contexts, supplied response styles and the independent generated answers.
Its [runbook](../docs/experiments/EVIDENCE_CONFIDENCE_README_V4.md) and
[report status](../reports/EVIDENCE_CONFIDENCE_RESULTS_V4.md) describe the
in-progress study. No v4 scores are reported before the registered run.

## How to read a question

1. Read the **question and context** before looking at the answers.
2. Check the **reference answer or fictional world key**.
3. Compare the complete response variants or sampled answers.
4. Inspect the split, labels and saved score where available.

V1 and v2 catalog scores use the saved layer-14 response-end readout. V3 shows
the end-marker reference and the separately frozen final-response-token and
response-content-mean scores.
Higher means more aligned with the trained expressed-certainty direction.
It is not a probability, a confidence rating supplied by the model, or a
correctness guarantee. The catalog includes reversed orderings as well as
successful ones.

Stage 0 semantic entropy describes disagreement between sampled answer meanings.
Low entropy can also occur when the model repeatedly gives a wrong answer.
The Stage 0B diagnostic reuses the 500-question collection, observing one answer
and estimating entropy from the other nine.

## Data provenance

The readable collections are deterministic exports of the checked-in
[raw inputs](../data/README.md) and [saved experiment outputs](../results/README.md).
Source IDs and response IDs are retained for tracing an example back to its
original row. No answers are generated or labels recomputed by the exporter.

Regenerate the pages from the repository root:

```bash
python scripts/export_question_sets.py
```

The v3 runner exports its collection from its saved scored rows. It includes
every authored response, both counterfactual worlds, and the omitted-role
context. Its source-level labels describe the fictional context, not subjective
model confidence.

[Research reports](../reports/README.md) · [Experiment map](../docs/experiments/EXPERIMENT_MAP.md) · [Repository home](../README.md)
