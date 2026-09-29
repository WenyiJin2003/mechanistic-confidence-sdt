# Semantic Entropy Probes — Local Stage 0

A resource-efficient validation of the [Semantic Entropy Probes](https://arxiv.org/abs/2406.15927) pipeline on Apple Silicon. All generation, entailment, hidden-state extraction, and analysis run locally; no OpenAI API, remote judge, CUDA, or Weights & Biases is used.

## Bottom line

- The pipeline runs end to end and passes its engineering, caching, and leakage checks.
- On 500 fresh SQuAD questions, the preregistered Qwen2.5-1.5B layer-14 probe predicts semantic entropy with test AUROC **0.718** and a context-bootstrap 95% interval of **[0.603, 0.821]**.
- A cached nested-CV audit found a stable layer-14 direction: OOF AUROC **0.738 [0.680, 0.793]** and median disjoint-half cosine **0.600**, versus a shuffled-null upper bound of **0.123**.
- Answer likelihood remains stronger. Corrected scalar stacking did not improve it: NLL-minus-combined log-loss was **-0.0027 [-0.0052, -0.0010]**.

**Decision:** the direction is stable enough for a small controlled activation-steering test. It has not shown incremental predictive value beyond output likelihood, so the project is still not ready for a mechanistic-confidence training loss.

## What was tested

For each question, the pipeline:

1. samples short answers from a local Qwen model;
2. clusters semantically equivalent answers with a local NLI model;
3. converts cluster frequencies into semantic entropy;
4. saves the hidden state of the final prompt token;
5. trains a linear probe to predict high versus low semantic entropy;
6. compares the probe with constant, output-likelihood, and shuffled-label controls.

This tests whether uncertainty is statistically decodable from one activation. It does **not** establish mechanistic causality, tamper resistance, SDT, or biological knowledge.

## Confirmatory result

The primary result uses 500 questions that do not overlap the earlier 200-question experiment by ID, context, exact question, or near-duplicate question. Each question has 10 sampled answers. The context-grouped split contains 307 training, 94 validation, and 99 test questions.

| Method | Test AUROC | 95% interval |
|---|---:|---:|
| Constant baseline | 0.500 | — |
| Preregistered layer 14 | **0.718** | **[0.603, 0.821]** |
| Validation-selected layer 23 | 0.848 | [0.751, 0.927] |
| Predictive entropy | 0.859 | [0.783, 0.922] |
| Answer negative log-likelihood | **0.911** | **[0.851, 0.958]** |
| Layer 14 + answer NLL | 0.776 | — |

AUROC is 0.5 at chance and 1.0 for perfect ranking. Layer 14 exceeds both chance and the shuffled-label 95% upper bound of 0.613. Its combination with answer NLL underperforms NLL alone by 0.135 AUROC; the paired interval is [-0.226, -0.050].

![Probe performance by layer](plots/run_500_qwen15b_confirm_probe_performance_by_layer.png)

## Direction-stability gate

This follow-up used only the locked 401-example development pool. The previously reported 99-example test split was not fitted or scored.

| Diagnostic | Layer 14 result | Gate |
|---|---:|---:|
| Repeated nested-CV OOF AUROC | 0.738 [0.680, 0.793] | Passed |
| Disjoint-half raw-direction cosine | 0.600 median [0.347, 0.717] | Passed |
| Shuffled-null median-cosine upper 95% | 0.123 | Passed |
| Common-holdout score correlation | 0.900 median | Passed |
| NLL-minus-combined log-loss | -0.0027 [-0.0052, -0.0010] | Failed incremental-value gate |

![Direction stability](plots/run_500_qwen15b_direction_stability.png)

## Evidence chain

| Phase | Purpose | Main outcome |
|---|---|---|
| 0.5B smoke and pilot | Validate the pipeline | Engineering checks passed; probe evidence was weak |
| Matched 1.5B run, 200 questions | Improve answer quality | Layer 14 test AUROC 0.665; interval crossed chance |
| Cached split audit | Test partition sensitivity | Fixed layer 14 cross-fitted AUROC 0.588 [0.507, 0.666] |
| Sampling audit, 50 questions | Test label reliability | 5-vs-20 agreement 84%; 10-vs-20 agreement 90% |
| Fresh 1.5B confirmation, 500 questions | Confirm the internal signal | Layer 14 passed; incremental-information gate failed |
| Cached direction audit, 401 development questions | Test whether one intervention direction is reproducible | Direction gate passed; corrected incremental gate failed |

## Reproduce

Requirements: Apple Silicon or CPU, Python 3.11, and [`uv`](https://docs.astral.sh/uv/).

```bash
uv venv --python 3.11 .venv
uv pip install --python .venv/bin/python -r requirements-stage0.txt

.venv/bin/python scripts/run_stage0.py \
  --config configs/stage0_qwen15b_500_confirm.yaml \
  --run run_500_qwen15b_confirm

.venv/bin/python scripts/run_direction_stability.py \
  --config configs/stage0_qwen15b_direction_stability.yaml
```

The 500-question generation takes about 41 minutes on an M3 MacBook Air. The cached direction audit takes about two minutes on CPU and loads no language model. Per-example caches under `cache/` are resumable and intentionally excluded from Git; checked-in aggregate artifacts are under `results/`.

## Repository guide

- [`RESULTS_STAGE0.md`](RESULTS_STAGE0.md) — full methods, metrics, deviations, and limitations
- [`README_STAGE0.md`](README_STAGE0.md) — commands, cache behavior, and artifact format
- [`STATUS.md`](STATUS.md) — current decision and next experiment
- [`results/README.md`](results/README.md) — result-directory index
- [`configs/`](configs/) — frozen experiment configurations
- [`stage0/`](stage0/) — local generation, clustering, probe, and stability code
- [`scripts/`](scripts/) — command-line entry points
- [`docs/UPSTREAM_README.md`](docs/UPSTREAM_README.md) — preserved upstream documentation

## Important deviations

- Generator size is 0.5B or 1.5B rather than the larger models studied in the paper.
- The upstream `microsoft/deberta-v2-xlarge-mnli` judge is replaced with `cross-encoder/nli-deberta-v3-small` for local execution.
- Only selected layers and the final prompt token are tested.
- Qwen2.5-1.5B uses unquantized bfloat16 on MPS because float16 sampling produced non-finite probabilities.

See [`RESULTS_STAGE0.md`](RESULTS_STAGE0.md) for the complete deviation and failure analysis.

## Provenance

Based on Kossen et al., [*Semantic Entropy Probes: Robust and Cheap Hallucination Detection in LLMs*](https://arxiv.org/abs/2406.15927), and the [OATML reference implementation](https://github.com/OATML/semantic-entropy-probes) at commit `02e2167dd1c00e27080d421f9b40e13e00f0452b`. The upstream MIT license is retained.
