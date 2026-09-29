# Stage 0 Plan

## Scope

This is a pipeline-validation reproduction of Semantic Entropy Probes. It is not an SDT experiment and does not test mechanistic causality.

## Execution plan

1. Validate Qwen on five fixed SQuAD v2 contextual questions with three sampled answers each.
2. If the answers are nonempty and not globally identical, run the 12-example smoke test. Reuse the five cached preflight examples.
3. Cache the final-prompt-token hidden state at transformer blocks 4, 12, 20, and 24, along with generated tokens and token log probabilities.
4. For the smoke test, group normalized exact matches. This transparent shortcut is allowed by the handoff but is a deliberate deviation from the paper.
5. Compute cluster-assignment semantic entropy, predictive entropy, and answer negative log-likelihood.
6. Train a standardized logistic-regression probe using a deterministic split and a threshold fitted only on training semantic-entropy values. Compare it with a train-mean constant baseline, output uncertainty, and shuffled training labels.
7. Stop and reassess if the initial local job approaches 20 minutes.
8. Only after a healthy smoke test, run an initial meaningful experiment on 64 examples and five generations using `cross-encoder/nli-deberta-v3-small`. Scale toward 200 examples only if labels and cost are healthy.

## Estimated resources

- Qwen download: approximately 1.0 GB
- Python environment: approximately 0.4–1.0 GB on Apple Silicon
- DeBERTa-small download for the meaningful run: approximately 0.4 GB
- Generated Stage 0 caches: well below 0.1 GB
- Five-example preflight plus smoke test: approximately 5–15 minutes after download
- Initial 64-example meaningful run: approximately 10–30 minutes; it will be split into resumable stages

## Repository strategy

The upstream repository remains available as Git history and reference code on branch `codex/stage0-qwen05b`. New work is isolated in `stage0/`, `scripts/`, `configs/`, `cache/`, `results/`, and top-level Stage 0 documentation. Essential outputs are local; W&B and remote LLM APIs are not used.
