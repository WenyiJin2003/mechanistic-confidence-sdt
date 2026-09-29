# Semantic Entropy Probes — Stage 0

This directory contains a small, local, resource-aware validation of the Semantic Entropy Probes pipeline using `Qwen/Qwen2.5-0.5B-Instruct` and SQuAD v2.

## What it does

- selects a deterministic answerable subset of SQuAD v2;
- samples short local generations;
- saves per-token log probabilities;
- caches the hidden state of the exact final prompt token at selected layers;
- groups sampled answers and computes semantic-entropy labels;
- trains a simple linear probe and evaluates required baselines;
- writes all artifacts locally without W&B or the OpenAI API.

## Setup

```bash
uv venv --python 3.11 .venv
uv pip install --python .venv/bin/python -r requirements-stage0.txt
```

## Run

```bash
.venv/bin/python scripts/run_stage0.py --config configs/stage0_qwen05b.yaml --run preflight
.venv/bin/python scripts/run_stage0.py --config configs/stage0_qwen05b.yaml --run run_a
```

Run B is intentionally gated on Run A:

```bash
.venv/bin/python scripts/run_stage0.py --config configs/stage0_qwen05b.yaml --run run_b
```

### 200-example stability follow-up

The pre-registered follow-up uses a separate configuration so the 64-example pilot remains reproducible:

```bash
.venv/bin/python scripts/run_stage0.py --config configs/stage0_qwen05b_200.yaml --run run_200
```

It adds layers 8 and 16, a fixed context-grouped train/validation/test split, validation-only layer selection, bootstrap intervals, 50 shuffled-label controls, SQuAD EM/F1 diagnostics, and a hidden-state-plus-answer-NLL comparison. Outputs are isolated under `results/run_200/` and `plots/run_200_probe_performance_by_layer.png`. The ignored local cache remains resumable per example and per NLI batch.

This follow-up is complete. All engineering checks passed, but the validation-selected hidden probe was not robust: layer 4 scored 0.503 validation AUROC and 0.628 test AUROC (context-bootstrap 95% interval [0.440, 0.800]), versus 0.847 for predictive entropy and 0.855 for answer negative log-likelihood on test. See `RESULTS_STAGE0.md` for the full table, leakage audit, failure analysis, and recommendation to move the next measurement run to Qwen 1.5B.

### Matched Qwen 1.5B comparison

The matched follow-up preserves the experimental protocol while changing the generator capacity and its six approximately depth-matched probe blocks. It keeps the same 200 examples, five generations, prompt, random seeds, 12-token limit, context-grouped split, local NLI model, and analysis:

```bash
.venv/bin/python scripts/run_stage0.py --config configs/stage0_qwen15b_200.yaml --run run_200_qwen15b
```

The 28-layer model is measured at blocks 5, 9, 14, 19, 23, and 28, corresponding approximately to blocks 4, 8, 12, 16, 20, and 24 in the 24-layer 0.5B model. Outputs are isolated under `results/run_200_qwen15b/` and `plots/run_200_qwen15b_probe_performance_by_layer.png`.

The 1.5B generator uses unquantized bfloat16 on MPS. An initial float16 preflight produced non-finite sampling probabilities before the first answer; bfloat16 preserves two-byte weights while providing the exponent range needed for stable local sampling.

This comparison is complete. All engineering checks passed. Validation selected layer 14 with AUROC 0.754; its test AUROC was 0.665 (context-bootstrap 95% interval [0.481, 0.844]), compared with 0.833 for predictive entropy and 0.835 for answer negative log-likelihood. Answer quality improved sharply over 0.5B, but the probe result remains preliminary; see `RESULTS_STAGE0.md`.

### Cached split-stability audit

The next diagnostic reuses the saved 1.5B generations, semantic labels, and hidden states. It performs 100 predeclared context-grouped splits, treats fixed layer 14 as the primary analysis, and treats validation-selected layers as secondary:

```bash
.venv/bin/python scripts/run_split_stability.py --config configs/stage0_qwen15b_split_stability.yaml
```

No generator or NLI model is loaded. Repeated-split percentiles are reported as sensitivity ranges rather than confidence intervals; a separate five-fold cross-fitted estimate uses context-group bootstrap intervals.

The audit is complete. Fixed layer 14 had median test AUROC 0.628 and exceeded chance in 93/100 splits; its cross-fitted AUROC was 0.588 with context-bootstrap 95% interval [0.507, 0.666]. The full preregistered gate did not pass because layers 14/19 were selected in only 33% of splits, while layer 28 was selected in 49%. This supports a weak internal association but not stable localization to one layer.

### Semantic-entropy sampling reliability

The next measurement checks whether five sampled answers provide a stable enough target for probe training. It selects 50 questions evenly across five original entropy-rank strata, reuses their existing five answers, adds 15 locally generated answers, and compares semantic entropy after 5, 10, and 20 samples:

```bash
.venv/bin/python scripts/run_label_stability.py --config configs/stage0_qwen15b_label_stability.yaml
```

The entropy cutoff remains frozen at `0.5867070452737222`, which was learned only from the original Run B training split. The predeclared pass criteria are at least 80% fixed-label agreement, Cohen's kappa of 0.60, and Spearman correlation of 0.70 for 5 versus 20 samples, plus at least 90% agreement for 10 versus 20. The ignored per-question cache makes additional generation resumable.

The script is resumable. Generation records and hidden states are written per example before aggregate analysis, and completed cache entries are reused.

## Token and layer convention

The cached token is the last token in the fully rendered chat prompt immediately before generation. For Hugging Face causal models, `hidden_states[0]` is the embedding output; requested layer `L` is stored from `hidden_states[L]`, the output after transformer block `L`.

## Important deviation

The upstream repository uses `microsoft/deberta-v2-xlarge-mnli` in its local NLI path. The meaningful Stage 0 run uses `cross-encoder/nli-deberta-v3-small`. The smoke test uses normalized exact-match grouping to validate the rest of the pipeline cheaply before downloading NLI weights.
