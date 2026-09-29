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

The matched follow-up changes only the generator capacity and its six approximately depth-matched probe blocks. It keeps the same 200 examples, five generations, prompt, random seeds, 12-token limit, context-grouped split, local NLI model, and analysis:

```bash
.venv/bin/python scripts/run_stage0.py --config configs/stage0_qwen15b_200.yaml --run run_200_qwen15b
```

The 28-layer model is measured at blocks 5, 9, 14, 19, 23, and 28, corresponding approximately to blocks 4, 8, 12, 16, 20, and 24 in the 24-layer 0.5B model. Outputs are isolated under `results/run_200_qwen15b/` and `plots/run_200_qwen15b_probe_performance_by_layer.png`.

The script is resumable. Generation records and hidden states are written per example before aggregate analysis, and completed cache entries are reused.

## Token and layer convention

The cached token is the last token in the fully rendered chat prompt immediately before generation. For Hugging Face causal models, `hidden_states[0]` is the embedding output; requested layer `L` is stored from `hidden_states[L]`, the output after transformer block `L`.

## Important deviation

The upstream repository uses `microsoft/deberta-v2-xlarge-mnli` in its local NLI path. The meaningful Stage 0 run uses `cross-encoder/nli-deberta-v3-small`. The smoke test uses normalized exact-match grouping to validate the rest of the pipeline cheaply before downloading NLI weights.
