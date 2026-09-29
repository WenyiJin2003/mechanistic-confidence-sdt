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

The script is resumable. Generation records and hidden states are written per example before aggregate analysis, and completed cache entries are reused.

## Token and layer convention

The cached token is the last token in the fully rendered chat prompt immediately before generation. For Hugging Face causal models, `hidden_states[0]` is the embedding output; requested layer `L` is stored from `hidden_states[L]`, the output after transformer block `L`.

## Important deviation

The upstream repository uses `microsoft/deberta-v2-xlarge-mnli` in its local NLI path. The meaningful Stage 0 run uses `cross-encoder/nli-deberta-v3-small`. The smoke test uses normalized exact-match grouping to validate the rest of the pipeline cheaply before downloading NLI weights.
