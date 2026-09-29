# Stage 0 Technical Runbook

## Pipeline

`stage0/pipeline.py` provides one local, resumable workflow:

1. select a deterministic answerable SQuAD v2 subset;
2. generate sampled answers and token log probabilities;
3. cache selected-layer hidden states at the final prompt token;
4. cluster answers by strict bidirectional local NLI;
5. compute semantic entropy and output-level uncertainty;
6. train standardized logistic probes and evaluate controls.

Device order is MPS, CUDA, then CPU. W&B is disabled and essential outputs are written locally.

## Setup

```bash
uv venv --python 3.11 .venv
uv pip install --python .venv/bin/python -r requirements-stage0.txt
```

## Commands

| Experiment | Command |
|---|---|
| Smoke test | `.venv/bin/python scripts/run_stage0.py --config configs/stage0_qwen05b.yaml --run run_a` |
| Initial NLI pilot | `.venv/bin/python scripts/run_stage0.py --config configs/stage0_qwen05b.yaml --run run_b` |
| 0.5B, 200 questions | `.venv/bin/python scripts/run_stage0.py --config configs/stage0_qwen05b_200.yaml --run run_200` |
| 1.5B, 200 questions | `.venv/bin/python scripts/run_stage0.py --config configs/stage0_qwen15b_200.yaml --run run_200_qwen15b` |
| Cached split audit | `.venv/bin/python scripts/run_split_stability.py --config configs/stage0_qwen15b_split_stability.yaml` |
| Sampling reliability | `.venv/bin/python scripts/run_label_stability.py --config configs/stage0_qwen15b_label_stability.yaml` |
| Fresh 1.5B confirmation | `.venv/bin/python scripts/run_stage0.py --config configs/stage0_qwen15b_500_confirm.yaml --run run_500_qwen15b_confirm` |
| Cached direction and stacking audit | `.venv/bin/python scripts/run_direction_stability.py --config configs/stage0_qwen15b_direction_stability.yaml` |

## Artifacts

Each main run writes:

- `generations.jsonl` — answers, token IDs, token log probabilities, correctness scores, and prompt metadata;
- `hidden_states.npz` — example IDs, layer IDs, and float16 hidden states;
- `entailment_judgments.jsonl` — NLI decisions used by semantic clustering;
- `semantic_entropy.jsonl` — cluster assignments and uncertainty measures;
- `probe_metrics.json` — splits, thresholds, probe results, baselines, and controls;
- `manifest.json` — exact configuration, software versions, runtimes, and integrity checks.

See [`results/README.md`](results/README.md) for the run index.

The cached direction audit writes `direction_stability_metrics.json`, a frozen raw-space direction artifact `frozen_probe_directions.npz`, and `plots/run_500_qwen15b_direction_stability.png`. It uses only the original train+validation pool (401 examples); the locked 99-example test split is not fitted or scored.

## Cache behavior

- Generation and hidden-state caches are written per example.
- NLI judgments are checkpointed in batches.
- Interrupted runs resume without repeating completed inference.
- `cache/` and Hugging Face weights are excluded from Git.
- Shareable aggregate artifacts remain under `results/`.

## Token and layer convention

The cached activation is the final token of the fully rendered chat prompt, immediately before answer generation. For Hugging Face causal models, requested layer `L` is stored from `hidden_states[L]`, the output after transformer block `L`; `hidden_states[0]` is the embedding output.

## Model notes

- Qwen2.5-0.5B runs unquantized float16 on MPS.
- Qwen2.5-1.5B runs unquantized bfloat16 on MPS; float16 failed its sampling preflight.
- Meaningful runs use `cross-encoder/nli-deberta-v3-small`, a resource-saving deviation from the upstream xlarge NLI model.
- The confirmation run excludes IDs, contexts, and exact or near-duplicate questions from the earlier 1.5B run.

Full interpretation belongs in [`RESULTS_STAGE0.md`](RESULTS_STAGE0.md); current project decisions belong in [`STATUS.md`](STATUS.md).
