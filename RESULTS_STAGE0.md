# Stage 0 Results

Last updated: 2026-09-29

## Outcome

Stage 0 passed as a pipeline-validation experiment. Local generation, prompt-token hidden-state extraction, semantic grouping, entropy calculation, caching, linear probing, baseline evaluation, and leakage checks all ran end to end on Apple Silicon without CUDA, W&B, the OpenAI API, or another remote judge.

The matched Qwen 1.5B comparison also passed every engineering check. A subsequent 100-split cached audit found a weak hidden-state association that persisted across data re-partitioning: fixed layer 14 exceeded chance in 93/100 splits, and its five-fold cross-fitted AUROC was 0.588 with context-bootstrap 95% interval [0.507, 0.666]. However, the best layer was not stable and output-based uncertainty remained much stronger.

A 50-question sampling-reliability diagnostic then increased each question from 5 to 20 generated answers. It passed all four predeclared point-estimate gates, but 8/50 five-sample labels changed and bootstrap intervals remained wide. This supports using 10 rather than 5 answers per question in the next confirmation run. Together these results are encouraging pipeline evidence for continuing with 1.5B, not a paper-level replication or a mechanistic or causal result.

## Exact configuration

The canonical machine-readable configurations are `configs/stage0_qwen05b.yaml` for Run A/Run B, `configs/stage0_qwen05b_200.yaml` for the 0.5B follow-up, `configs/stage0_qwen15b_200.yaml` for the matched 1.5B comparison, and `configs/stage0_qwen15b_label_stability.yaml` for sampling reliability.

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

The 200-example follow-up kept the same model, dataset-selection seed, prompt, sampling settings, token position, and local NLI model, with these registered changes:

- 200 examples and five sampled generations per example (1,000 generations total)
- Layers 4, 8, 12, 16, 20, and 24
- Fixed context-grouped train/validation/test split with seed 42 and target fractions 60%/20%/20%
- Entropy threshold fitted only on training data and layer selected only on validation AUROC
- 50 shuffled-label fits per layer
- 2,000 context-group bootstrap resamples for test AUROC intervals
- SQuAD exact-match/F1 diagnostics and a hidden-state-plus-answer-NLL comparison

The matched 1.5B run keeps the same 200 examples, five generations, prompt, seeds, 12-token limit, grouped split, NLI model, and analysis. It changes the generator to `Qwen/Qwen2.5-1.5B-Instruct` and uses approximately depth-matched blocks 5, 9, 14, 19, 23, and 28. The unquantized generator runs in bfloat16 on MPS; saved hidden vectors remain float16.

## Deviations from the paper and upstream repository

1. The paper studies substantially larger language models. This pilot tests 0.5B and 1.5B instruction models.
2. The upstream local entailment path defaults to `microsoft/deberta-v2-xlarge-mnli`; the meaningful runs use `cross-encoder/nli-deberta-v3-small` to fit the local resource budget.
3. Run A uses normalized exact match as a transparent smoke-test grouping method. Run B uses local NLI.
4. The probe target is the notebook's cluster-assignment semantic entropy. Other likelihood-weighted semantic-entropy variants were not used as targets.
5. Only the final prompt token (TBG) is tested. The second-last generated token (SLT) is not tested.
6. Run B tests four representative layers rather than every layer. The 0.5B follow-up uses six layers; the 1.5B comparison uses six approximately depth-matched layers rather than identical absolute layer numbers.
7. The logistic probe standardizes each layer's activations. The upstream notebook uses scikit-learn logistic regression without an explicit scaler.
8. The entropy threshold is fitted on training data only rather than using a universal split across several datasets. This avoids test-label leakage but is not the paper's multi-dataset universal threshold.
9. Run B is the handoff's initial 50–100-example meaningful run (64 examples); the separate 200-example follow-up supplies the requested scale-up.
10. The 64-example run uses a fixed train/test split. The 200-example run corrects this limitation with context-grouped train/validation/test partitions and validation-only layer selection.
11. The follow-up adds SQuAD answer-correctness diagnostics and an answer-likelihood-augmented probe. These are Stage 0 diagnostics, not causal interventions or paper-level replications.
12. Qwen 1.5B uses bfloat16 because float16 produced non-finite sampling probabilities on MPS before the first answer. This is a documented hardware-compatibility deviation, not quantization.

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

## Run 200 — Qwen 0.5B fixed-split stability follow-up

The 200-example run completed end to end and passed all saved engineering checks.

- 1,000/1,000 generations were nonempty and produced 873 distinct normalized answers.
- Semantic cluster counts were non-degenerate: 10 questions had 1 cluster, 26 had 2, 52 had 3, 53 had 4, and 59 had 5.
- Semantic entropy had mean 1.1569 and standard deviation 0.4336, with seven observed values from 0 to log(5).
- Hidden states have shape `[200, 6, 896]`, dtype float16, and all values are finite.
- The final prompt-token position and prompt suffix were verified for every example. One 844-token prompt was left-truncated to the configured 768-token limit while preserving the question-bearing suffix.
- Generation plus six-layer hidden-state extraction took 153.5 seconds on MPS. The first 64 generation records were reused from the earlier five-sample run; their hidden states were recomputed because the layer set changed.
- A full replay then reused 200/200 generation records, 200/200 hidden-state records, and all NLI judgments; the cached generator stage completed in 0.4 seconds. The saved manifest records this latest replay.
- The saved clustering path contains 1,783 directed NLI judgments: 483 entailment, 1,041 neutral, and 259 contradiction. Mean winning-class probability was 0.935.

The context-grouped split contains 120 training, 39 validation, and 41 test questions, spanning 115, 39, and 39 unique contexts. The audit found zero ID, exact-question, or exact-context overlap and no cross-split question pairs above 0.9 token-Jaccard similarity. The train-only entropy threshold was 1.19355. Low/high label counts were 54/66 in training, 18/21 in validation, and 16/25 in test.

### Probe performance by layer

The primary layer was selected using validation AUROC only. Layer 4 won with validation AUROC 0.503; its untouched test AUROC was 0.628 with a context-group bootstrap 95% interval of [0.440, 0.800]. The interval crosses chance and the validation score is effectively chance, so this is not robust evidence of a usable hidden-state confidence signal.

| Layer | Validation AUROC | Test AUROC | Context-bootstrap 95% interval | Test accuracy |
|---:|---:|---:|---:|---:|
| **4 (selected)** | **0.503** | **0.628** | **[0.440, 0.800]** | **0.610** |
| 8 | 0.384 | 0.678 | [0.508, 0.828] | 0.659 |
| 12 | 0.386 | 0.610 | [0.423, 0.787] | 0.585 |
| 16 | 0.476 | 0.578 | [0.393, 0.755] | 0.561 |
| 20 | 0.410 | 0.543 | [0.365, 0.740] | 0.512 |
| 24 | 0.495 | 0.580 | [0.373, 0.785] | 0.634 |

Layer 8 has the highest nominal test AUROC, but its validation AUROC is 0.384. Treating it as the winner after observing test results would be test-set selection leakage, so it is reported only as a secondary diagnostic.

### Baselines and controls

| Method | Validation AUROC | Test AUROC | Test bootstrap 95% interval |
|---|---:|---:|---:|
| Constant train mean | 0.500 | 0.500 | — |
| Predictive entropy | 0.923 | 0.847 | [0.708, 0.955] |
| Answer negative log-likelihood | 0.899 | 0.855 | [0.726, 0.957] |
| Selected layer-4 hidden probe | 0.503 | 0.628 | [0.440, 0.800] |
| Layer-4 hidden state + answer NLL | 0.608 | 0.763 | — |

The 50 shuffled-label fits per layer produced mean test AUROCs between 0.506 and 0.535. At the selected layer, the empirical shuffled-label 95% interval was [0.368, 0.687], which contains the observed 0.628. Output-level predictive entropy and answer NLL were substantially stronger than the hidden probe. Adding layer-4 activations to answer NLL did not outperform answer NLL alone, so this run does not show incremental information in the selected hidden representation.

### Answer quality and correctness diagnostics

- Only 3.1% of individual samples exactly matched a SQuAD reference answer; mean sample F1 was 0.235.
- On the test split, just 4.9% of questions had any exact-match sample (2 of 41), so correctness AUROCs are highly unstable.
- The selected probe's correctness AUROC was 0.526, while raw answer log-likelihood reached 0.744.
- Semantic entropy and mean sample F1 had test Pearson correlation -0.328, in the expected direction but too noisy for a substantive claim.
- 805/1,000 generations used all 12 allowed new tokens. This indicates frequent truncation or verbosity and is the clearest answer-quality limitation of the current setup.

## Matched Qwen 1.5B comparison

The matched 1.5B run completed in 811.6 seconds for generation and six-layer hidden-state extraction on MPS. All saved engineering checks passed.

- 1,000/1,000 generations were nonempty, with 565 distinct normalized answers.
- Individual-sample exact match rose from 3.1% at 0.5B to 46.7%; mean sample F1 rose from 0.235 to 0.661.
- Only 204/1,000 generations used all 12 tokens, compared with 805/1,000 at 0.5B.
- Cluster counts remained non-degenerate: 76 questions had 1 cluster, 47 had 2, 43 had 3, 19 had 4, and 15 had 5.
- Semantic entropy had mean 0.5882 and standard deviation 0.5446. Lower entropy is consistent with the larger model's more stable answers.
- Stored hidden states have shape `[200, 6, 1536]`, dtype float16, and all values are finite. The generator itself ran unquantized in bfloat16.
- The same leakage audit passed: 120/39/41 train/validation/test questions with no ID, exact-question, exact-context, or high-similarity question overlap.
- The train-only entropy threshold was 0.58671. Low/high labels were 63/57 in training, 25/14 in validation, and 19/22 in test.
- The saved clustering path contains 977 directed NLI judgments: 396 entailment, 443 neutral, and 138 contradiction. Mean winning-class probability was 0.934.

### 1.5B probe performance by layer

Validation selected layer 14 with AUROC 0.754. Its untouched test AUROC was 0.665 with context-group bootstrap 95% interval [0.481, 0.844]. This is more promising than the 0.5B selection result, but the interval still crosses chance.

| Layer | Validation AUROC | Test AUROC | Context-bootstrap 95% interval | Test accuracy |
|---:|---:|---:|---:|---:|
| 5 | 0.546 | 0.373 | [0.199, 0.563] | 0.390 |
| 9 | 0.580 | 0.409 | [0.230, 0.605] | 0.439 |
| **14 (selected)** | **0.754** | **0.665** | **[0.481, 0.844]** | **0.683** |
| 19 | 0.703 | 0.651 | [0.478, 0.820] | 0.634 |
| 23 | 0.629 | 0.656 | [0.462, 0.824] | 0.561 |
| 28 | 0.637 | 0.675 | [0.495, 0.848] | 0.610 |

Layer 28 has the highest nominal test AUROC, but layer 14 remains the primary result because it was selected on validation only.

### 1.5B baselines and controls

| Method | Validation AUROC | Test AUROC | Test bootstrap 95% interval |
|---|---:|---:|---:|
| Constant train mean | 0.500 | 0.500 | — |
| Predictive entropy | 0.969 | 0.833 | [0.689, 0.944] |
| Answer negative log-likelihood | 0.989 | 0.835 | [0.682, 0.941] |
| Selected layer-14 hidden probe | 0.754 | 0.665 | [0.481, 0.844] |
| Layer-14 hidden state + answer NLL | 0.809 | 0.713 | — |

At layer 14, 50 shuffled-label fits had mean test AUROC 0.521 and empirical 95% interval [0.368, 0.658]. The observed 0.665 lies just above that interval, which is encouraging but marginal. The bootstrap interval still includes chance, and adding the hidden state to answer NLL did not outperform answer NLL alone.

On the test split, 65.9% of questions had at least one exact-match sample and mean sample F1 was 0.628. Semantic entropy correlated with sample F1 at -0.714. The selected semantic-entropy probe's correctness AUROC was 0.603, while raw answer log-likelihood reached 0.854.

### Matched comparison summary

| Metric | Qwen 0.5B | Qwen 1.5B |
|---|---:|---:|
| Individual-sample exact match | 0.031 | 0.467 |
| Mean sample F1 | 0.235 | 0.661 |
| Generations using all 12 tokens | 80.5% | 20.4% |
| Mean semantic entropy | 1.157 | 0.588 |
| Selected-layer validation AUROC | 0.503 | 0.754 |
| Selected-layer test AUROC | 0.628 | 0.665 |
| Predictive-entropy test AUROC | 0.847 | 0.833 |
| Answer-NLL test AUROC | 0.855 | 0.835 |

The semantic-entropy targets are generated separately by each model, so the AUROC comparison is informative but not a paired evaluation of an identical target.

## Cached 1.5B split-stability audit

This preregistered diagnostic reused the 200 saved questions, semantic-entropy values, and hidden states without loading either model. It ran 100 context-grouped 60/20/20 splits with seeds 42–141. For every split, the entropy threshold and feature scaler were fitted on training data only. Fixed layer 14 was the primary analysis; validation-selected layers were secondary. All 100 splits met the minimum class-count rule and passed the leakage audit.

### Primary fixed-layer result

- Layer-14 median test AUROC: 0.628; IQR [0.558, 0.673]
- Above chance in 93/100 splits; at least 0.60 in 62/100 splits
- One shuffled-label fit per split: median 0.497
- Continuous-entropy prediction was weaker: median test Spearman correlation 0.219
- Five-fold cross-fitted layer-14 AUROC: 0.588, context-bootstrap 95% interval [0.507, 0.666]
- Cross-fitted correctness AUROC from the low-entropy score: 0.592, 95% interval [0.506, 0.676]

The fixed-layer stability gates passed. Because the cross-fitted interval's lower bound is just above 0.5, the result supports a weak internal cross-validated association, not a strong predictor.

### Layer localization and controls

| Diagnostic | Result |
|---|---:|
| Validation-selected probe median test AUROC | 0.634 |
| Predictive-entropy median test AUROC | 0.921 |
| Answer-NLL median test AUROC | 0.944 |
| Layer 14 selected | 18/100 splits |
| Layer 19 selected | 15/100 splits |
| Layer 23 selected | 16/100 splits |
| Layer 28 selected | 49/100 splits |

The preregistered overall gate was **not passed** because layers 14 and 19 together were selected in only 33% of splits, below the 60% requirement. Layer 28 was selected most often and had median test AUROC 0.667, but it is a post hoc observation and does not replace the fixed layer-14 primary result.

The cross-fitted hidden probe trailed answer NLL by 0.342 AUROC, with context-bootstrap difference interval [-0.424, -0.259]. Therefore the internal signal is repeatable but does not add evidence of superiority over the sampled-output likelihood baseline.

Repeated test sets overlap heavily, so across-split percentiles are sensitivity ranges rather than confidence intervals. The five-fold analysis provides a cross-fitted context-bootstrap interval, but it does not cover all uncertainty from model refitting, threshold estimation, or new data and cannot replace fresh-data confirmation.

## Semantic-entropy sampling reliability

This predeclared diagnostic sampled 50 questions equally from five rank strata of the original five-answer entropy distribution. It reused the original 250 answers and generated 750 new answers locally, producing 20 answers per question. The fixed cutoff `0.5867070452737222` came from the original Run B training split and was not refitted. No probe was trained in this analysis.

All answers and NLI decisions were cached. The run took 610.5 seconds on MPS and added 978 NLI judgments for the 10-answer prefix and 3,122 for the 20-answer prefix. Answers were non-degenerate: mean distinct normalized answers increased from 2.76 at five samples to 4.44 at ten and 7.46 at twenty; no question had only empty answers.

| Comparison against 20 answers | Label agreement | Cohen's kappa | Spearman correlation | Mean absolute entropy difference | Label flips |
|---|---:|---:|---:|---:|---:|
| 5 answers | 0.840 | 0.683 | 0.808 | 0.400 | 8/50 |
| 10 answers | 0.900 | 0.790 | 0.934 | 0.210 | 5/50 |

The 5-vs-20 stratified-bootstrap 95% intervals were [0.74, 0.92] for agreement, [0.485, 0.841] for kappa, and [0.688, 0.898] for Spearman. The 10-vs-20 intervals were [0.82, 0.96], [0.595, 0.920], and [0.870, 0.964]. Thus all point-estimate gates passed, but the lower bounds for the five-answer comparison fell below the registered gates.

The fixed high-entropy fraction increased from 0.48 at five answers to 0.62 at ten and 0.60 at twenty. Of the eight 5-vs-20 flips, seven were low-to-high and one high-to-low. This shows the practical weakness of five samples: rare alternative meanings can be missed, making some questions look more certain than they do with more sampling. It also means the raw entropy distribution depends on sampling budget, so comparisons must keep that budget fixed.

The result supports semantic entropy as a workable target for the next experiment, but does not validate a model's confidence by itself. It only measures the repeatability of labels constructed from sampled outputs and a small local NLI model.

## Failure analysis and limitations

- The 1.5B probe is more promising, but its selected-layer test interval still crosses chance and the test set contains only 41 questions.
- The 100-split audit supports a weak signal but rejects a stable layer-14/19 localization claim; the best validation layer shifts and favors layer 28 in 49% of splits.
- Continuous semantic-entropy prediction is weak, suggesting part of the binary AUROC result depends on how entropy is thresholded.
- Five-answer labels are imperfect: 16% changed when expanded to 20 answers, and their bootstrap lower bounds did not clear the point-estimate gates.
- The entropy cutoff was originally learned from a five-answer distribution. Holding it fixed prevents post hoc tuning but exposes a sampling-budget shift; the next run must use one fixed answer count throughout training and evaluation.
- Output likelihood baselines remain substantially stronger, and hidden-state-plus-NLL models do not improve on NLL alone.
- Qwen 0.5B often emits incomplete or incorrect answers within the 12-token limit. This validates the machinery but makes the semantic target noisier than it would be for a stronger QA model.
- Qwen 1.5B greatly improves answer quality, but 38% of questions produce only one semantic cluster, changing the target distribution relative to 0.5B.
- The small NLI model is a major deviation. Its high-confidence classifications do not by themselves validate equivalence judgments on short answer fragments.
- The follow-up's 41-example test set still gives wide per-layer confidence intervals. The 50 shuffled-label fits and context bootstrap quantify some instability, but this is not a multi-training-seed study.
- There are 1,536 hidden-state features but only 120 training examples in the 1.5B run, so even regularized linear probes can overfit.
- Only one token position and one prompt format are tested.
- No correctness-targeted probe, causal intervention, SDT claim, biological claim, or mechanistic-causality claim is supported here.

## Recommendation

Continue measurement work with Qwen 1.5B rather than 0.5B. The split audit shows that a weak internal signal survives data re-partitioning, but its exact layer is not stable and it remains far below output-based uncertainty. The label diagnostic passed, while also showing that five answers are noisier than desirable.

The next experiment should use 10 answers per question on a fresh 500-question SQuAD subset, with a context-grouped split and a primary layer frozen before generation. Layer 14 is the conservative fixed primary layer from the earlier analysis; layer 28 can be reported as a predeclared secondary sensitivity check. The analysis should retain output-likelihood baselines and test whether the hidden probe adds information beyond them. Do not begin synthetic-document training or add an internal mechanistic loss until that fresh-data result confirms the internal signal.

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
- `results/run_200/generations.jsonl`
- `results/run_200/entailment_judgments.jsonl`
- `results/run_200/semantic_entropy.jsonl`
- `results/run_200/hidden_states.npz`
- `results/run_200/probe_metrics.json`
- `results/run_200/manifest.json`
- `plots/run_200_probe_performance_by_layer.png`
- `results/run_200_qwen15b/generations.jsonl`
- `results/run_200_qwen15b/entailment_judgments.jsonl`
- `results/run_200_qwen15b/semantic_entropy.jsonl`
- `results/run_200_qwen15b/hidden_states.npz`
- `results/run_200_qwen15b/probe_metrics.json`
- `results/run_200_qwen15b/manifest.json`
- `plots/run_200_qwen15b_probe_performance_by_layer.png`
- `results/run_200_qwen15b_split_stability/stability_metrics.json`
- `plots/run_200_qwen15b_split_stability.png`
- `results/run_50_qwen15b_label_stability/combined_generations.jsonl`
- `results/run_50_qwen15b_label_stability/entailment_judgments_20.jsonl`
- `results/run_50_qwen15b_label_stability/semantic_entropy_5.jsonl`
- `results/run_50_qwen15b_label_stability/semantic_entropy_10.jsonl`
- `results/run_50_qwen15b_label_stability/semantic_entropy_20.jsonl`
- `results/run_50_qwen15b_label_stability/label_stability_metrics.json`
- `plots/run_50_qwen15b_label_stability.png`

Actual storage after both 200-example runs and the stability audit: isolated environment 1.1 GB, result artifacts about 11 MB, plots about 408 KB, and the local Hugging Face cache reports 5.4 GB. Cached model directories are 953 MB for Qwen 0.5B, 2.9 GB for Qwen 1.5B, and 552 MB for DeBERTa-small.
