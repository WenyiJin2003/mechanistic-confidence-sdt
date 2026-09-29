# Stage 0 Results

Date: 2026-09-28

## Outcome

Stage 0 passed as a pipeline-validation experiment. Local generation, prompt-token hidden-state extraction, semantic grouping, entropy calculation, caching, linear probing, baseline evaluation, and leakage checks all ran end to end on Apple Silicon without CUDA, W&B, the OpenAI API, or another remote judge.

This result does **not** establish a useful semantic-entropy probe in Qwen 0.5B. On the 64-example meaningful run, the best selected-layer probe was only slightly above chance and was weaker than output-based uncertainty baselines.

## Exact configuration

The canonical machine-readable configuration is `configs/stage0_qwen05b.yaml`.

- Generator: `Qwen/Qwen2.5-0.5B-Instruct`, unquantized, float16, MPS
- Dataset: fixed answerable subset of SQuAD v2 validation, selection seed 1729
- Global seed: 20260928; per-example generation seed is global seed plus fixed subset index
- Prompt: Qwen chat template with context and a short-answer system instruction
- Temperature: 1.0; top-p 1.0; top-k 0; maximum 12 new tokens
- Token position: final token of the rendered prompt immediately before generation
- Transformer blocks: 4, 12, 20, and 24
- Run A: 12 examples, 3 generations, normalized exact-match grouping
- Run B: 64 examples, 5 generations, strict bidirectional NLI grouping
- Entailment model: `cross-encoder/nli-deberta-v3-small`, float32, MPS
- Probe: standardized logistic regression, C=1.0, maximum 2,000 iterations
- Split: fixed 48/16 train/test split, seed 42
- Entropy threshold: reconstruction-error split fitted on training semantic-entropy values only
- Shuffled-label seed: 314159
- W&B: disabled; all essential artifacts saved locally

Software versions: Python 3.11.14, PyTorch 2.14.0, Transformers 4.57.6, Datasets 3.6.0, scikit-learn 1.9.1, NumPy 2.4.6, PyYAML 6.0.3, and Matplotlib 3.11.2.

## Deviations from the paper and upstream repository

1. The paper studies substantially larger language models. This pilot uses a 0.49B-parameter instruction model.
2. The upstream local entailment path defaults to `microsoft/deberta-v2-xlarge-mnli`; Run B uses `cross-encoder/nli-deberta-v3-small` to fit the local resource budget.
3. Run A uses normalized exact match as a transparent smoke-test grouping method. Run B uses local NLI.
4. The probe target is the notebook's cluster-assignment semantic entropy. Other likelihood-weighted semantic-entropy variants were not used as targets.
5. Only the final prompt token (TBG) is tested. The second-last generated token (SLT) is not tested.
6. Four representative layers are tested rather than every layer or the original six-layer request. This follows the resource-first handoff.
7. The logistic probe standardizes each layer's activations. The upstream notebook uses scikit-learn logistic regression without an explicit scaler.
8. The entropy threshold is fitted on training data only rather than using a universal split across several datasets. This avoids test-label leakage but is not the paper's multi-dataset universal threshold.
9. Run B is the handoff's initial 50–100-example meaningful run (64 examples), not the earlier proposed 200-example scale-up.
10. The 64-example run uses a fixed train/test split without a separate validation subset. No hyperparameters are selected from the test set, but a larger follow-up should use train/validation/test partitions.

## Run A — smoke test

- Passed all success checks.
- 36/36 generations were nonempty; 33 normalized answers were distinct.
- Cluster counts varied: three questions produced 2 clusters and nine produced 3 clusters.
- Cluster-assignment entropy had two values (0.6365 and 1.0986), mean 0.9831, standard deviation 0.2001.
- Hidden states have shape `[12, 4, 896]`, dtype float16, and finite values.
- The final prompt-token index was verified for every record.
- Five preflight generation records were reused; a subsequent Run A replay used 12/12 generation and hidden-state cache entries.
- The probe trained end to end. Its three-example test set is too small for interpretation.

## Run B — initial meaningful run

- Passed all success checks.
- 320/320 generations were nonempty; 290 normalized answers were distinct.
- Semantic cluster counts: 1 cluster (2 examples), 2 (6), 3 (17), 4 (22), and 5 (17).
- Cluster-assignment entropy mean 1.1961, standard deviation 0.3831, with seven distinct values from 0 to log(5).
- Hidden states have shape `[64, 4, 896]`, dtype float16, and finite values.
- The 12 hidden-state records shared with Run A were reused.
- The train-only entropy threshold was 1.19355. Labels were 20 low / 28 high in training and 5 low / 11 high in test.
- The split audit found zero ID overlap, zero exact question overlap, zero exact context overlap, and zero train/test question pairs above 0.9 token-Jaccard similarity.
- The saved clustering path used 601 directed NLI judgments: 164 entailment, 353 neutral, and 84 contradiction. Mean winning-class probability was 0.938.

### Held-out performance

The test set contains 16 examples, so these values have high sampling uncertainty.

| Method | Layer | Accuracy | AUROC | Log loss |
|---|---:|---:|---:|---:|
| Linear probe | 4 | 0.438 | 0.436 | 1.271 |
| Linear probe | 12 | 0.688 | 0.564 | 1.459 |
| Linear probe | 20 | 0.438 | 0.218 | 1.624 |
| Linear probe | 24 | 0.625 | 0.527 | 0.963 |
| Constant train mean | — | 0.688 | 0.500 | 0.644 |
| Predictive entropy | — | 0.750 | 0.782 | 0.498 |
| Answer negative log-likelihood | — | 0.813 | 0.836 | 0.485 |
| Mean answer length | — | 0.688 | 0.500 | 0.654 |
| Prompt length | — | 0.438 | 0.382 | 0.667 |

Shuffled-label probe AUROCs at layers 4, 12, 20, and 24 were 0.655, 0.509, 0.436, and 0.691. Their instability and occasional strength relative to the true-label probes reinforce that this sample is too small for a substantive probe-performance conclusion.

## Failure analysis and limitations

- Probe performance is weak: the best layer AUROC is 0.564, while output likelihood baselines are much stronger.
- Qwen 0.5B often emits incomplete or incorrect answers within the 12-token limit. This validates the machinery but makes the semantic target noisier than it would be for a stronger QA model.
- Surface diversity is extremely high (290 distinct normalized answers out of 320), which may reflect poor answer stability as much as useful uncertainty.
- The small NLI model is a major deviation. Its high-confidence classifications do not by themselves validate equivalence judgments on short answer fragments.
- The 16-example test set makes per-layer and shuffled-label AUROCs highly variable.
- There are 896 features but only 48 training examples, so regularized linear probes can still overfit.
- Run B lacks a separate validation set and tests only four layers at one token position.
- No correctness probe, causal intervention, SDT claim, biological claim, or mechanistic-causality claim is supported here.

## Recommendation

Stay with Qwen 0.5B for one final 200-example stability run before downloading Qwen 1.5B. The pipeline is fast, labels are non-degenerate, and the output-based baselines behave sensibly; scaling the existing cached setup is the cheapest way to determine whether the near-chance probe is merely small-sample noise. That follow-up should restore layers 4, 8, 12, 16, 20, and 24 and use fixed train/validation/test splits.

Move to 1.5B only if the 200-example 0.5B probe remains at chance, or if manual review confirms that 0.5B answer quality is the dominant source of label noise. At that point, changing model size would be justified; doing so now would confound sample-size instability with model-capacity effects.

## Artifacts

- `results/run_a/generations.jsonl`
- `results/run_a/semantic_entropy.jsonl`
- `results/run_a/hidden_states.npz`
- `results/run_a/probe_metrics.json`
- `results/run_b/generations.jsonl`
- `results/run_b/entailment_judgments.jsonl`
- `results/run_b/semantic_entropy.jsonl`
- `results/run_b/hidden_states.npz`
- `results/run_b/probe_metrics.json`
- `results/run_b/manifest.json`
- `plots/probe_performance_by_layer.png`

Actual storage after both runs: isolated environment 1.1 GB, model/dataset/generation caches 1.6 GB, and result artifacts 1.3 MB. Cached model directories are 953 MB for Qwen and 552 MB for DeBERTa-small.
