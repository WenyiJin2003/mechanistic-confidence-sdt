# Stage 0 Results

Last updated: 2026-10-06

**Naming note.** Stage 0 and Stage 0B are semantic-uncertainty experiments, but
they fit separate probes at different positions. Stage 0 reads the final
rendered prompt token before any answer. Stage 0B reads the final ordinary
content token of one observed answer. Neither direction is the later Paired
Confidence v1 expressed-certainty direction at the post-response `<|im_end|>`
token. See the [canonical experiment map](EXPERIMENT_MAP.md).

## Stage 0B — post-answer hidden-state diagnostic

> **Conclusion: after one answer has been observed, its layer-14 hidden state contains a readable association with the semantic variability of nine alternative answers, but it does not improve on the likelihood of that same observed answer. This diagnostic therefore does not yet justify treating the probe direction as an independent confidence signal or turning it into a training loss.**

### Why this diagnostic was needed

The original Stage 0 probe reads the model at the end of the prompt, before an answer is generated. Stage 0B asks a narrower question that is closer to the proposed training setup: **after the model has produced one answer, does its internal state contain information about how much its other possible answers would vary?**

The comparison was designed to keep the information budget fair:

```text
one cached observed answer  ->  layer-14 hidden state and answer NLL
other nine cached answers   ->  leave-one-out semantic-entropy target
```

For each of the 500 questions, answer 0 was the predeclared observed answer. The model was run in teacher-forcing mode on the exact cached prompt and exact cached answer token IDs. The primary feature was the layer-14 state at the final answer-content token. The target was semantic entropy recomputed from answers 1–9 using the same greedy, bidirectional-NLI clustering procedure. A new high/low threshold was fitted on the 307 training questions only. The existing context-grouped split was preserved exactly: 307 train, 94 validation, and 99 test questions, with no context overlap.

The 20-question sanity gate and the full 500-question run passed. No answers were regenerated and no new NLI inference was performed.

### Primary held-out results

| Method | Information used | Test AUROC (95% context-bootstrap CI) | Log loss | Entropy Spearman |
|---|---|---:|---:|---:|
| Constant train mean | No answer-specific information | 0.500 | 0.679 | — |
| Answer length | One observed answer | 0.629 [0.503, 0.746] | 0.655 | 0.367 |
| Simple lexical controls | One observed answer | 0.644 [0.516, 0.766] | 0.663 | 0.408 |
| **Layer-14 final-token probe** | **One observed answer** | **0.693 [0.584, 0.794]** | **1.417** | **0.453** |
| **Same-answer sequence NLL** | **The same observed answer** | **0.773 [0.668, 0.864]** | **0.642** | **0.624** |
| NLL + cross-fitted scalar probe score | The same observed answer | 0.763 [0.659, 0.855] | 0.639 | 0.597 |

The primary probe was above chance, but it was weaker than same-answer NLL by 0.079 AUROC; the paired 95% interval was [-0.176, 0.015]. Adding a cross-fitted scalar probe score to NLL changed AUROC by -0.010 [-0.074, 0.049] and log loss by only 0.004 in favor of the combined model [-0.036, 0.039]. These intervals include zero, so there is **no reliable incremental gain over NLL**.

The secondary layer-14 mean-over-answer-tokens representation reached AUROC 0.708 [0.587, 0.812]. The exploratory layer-23 final-token representation reached 0.669 [0.560, 0.773]. Neither changes the primary conclusion. Fifty shuffled-label fits for the primary representation had mean test AUROC 0.478 and an empirical 95% range of [0.390, 0.581].

### Predeclared answer-index robustness check

Repeating the full analysis with answer 3 as the observed answer produced the same ordering:

| Method | Test AUROC (95% context-bootstrap CI) |
|---|---:|
| Layer-14 final-token probe | 0.720 [0.598, 0.827] |
| Same-answer sequence NLL | 0.789 [0.699, 0.873] |
| NLL + cross-fitted scalar probe score | 0.766 [0.659, 0.861] |

For answer 3, the combined model changed AUROC relative to NLL by -0.023 [-0.091, 0.039]. This makes the result less likely to be an artifact of choosing answer 0. Answer index 7 was an optional extension, not a required gate, and was deferred to prioritize a complete, checked analysis before the meeting.

### Interpretation and limitations

- The post-answer state is **associated** with leave-one-out semantic entropy under a linear readout. It is not established as a causal control variable or a distinct confidence quantity.
- The same answer's likelihood is a stronger and much better calibrated predictor. The probe's high log loss also cautions against interpreting its raw probabilities literally.
- The target is estimated from nine samples and inherits errors from the local NLI clustering model.
- Only two answer-index choices, two layers, and simple linear probes were tested. Answer wording, length, and likelihood remain plausible sources of the decodable association.
- This experiment diagnoses representations only. It performs no activation intervention and trains no confidence loss.

### Implication for the Casper meeting

Stage 0B sharpens the decision point. We can say that **a post-answer layer-14 representation carries some information about future answer variability, but the current probe does not extract information beyond ordinary answer likelihood**. The useful meeting question is therefore not yet how to add this direction as a loss. It is what independent property the proposed mechanistic term should capture beyond likelihood, and what controlled evidence would be sufficient before using it during synthetic-document training.

The original Stage 0 conclusions are preserved below; Stage 0B is a separate diagnostic and does not revise them.

## Outcome

> **Decision: continue to a controlled activation-steering study. Do not use the probe direction as a training loss yet.**

### Confirmed

- **The full pipeline works:** generation, semantic clustering, entropy labels, hidden-state caching, linear probing, baselines, and leakage checks all ran end to end.
- **A layer-14 internal signal is detectable:** test AUROC **0.718 [0.603, 0.821]** on a fresh 500-question dataset.
- **The direction is reproducible enough to test:** nested-CV AUROC **0.738 [0.680, 0.793]** and median cross-split cosine similarity **0.600**, above the shuffled-label upper bound of **0.123**.
- **Qwen2.5-1.5B is the appropriate model for the next experiment.**

### Not confirmed

- **The probe does not add predictive value beyond answer likelihood.** Answer NLL reached AUROC **0.911**, and combining it with the probe did not improve performance.
- **No causal effect has been demonstrated.** The experiments show an association, not that the direction controls confidence.
- **Mechanistic-loss training is not yet justified.** That decision depends on the activation-steering experiment.

### Research implication

Stage 0 validates the **measurement and target-selection steps** of the proposed project. Stage 1 must test whether bidirectional manipulation of the frozen direction changes semantic entropy beyond the controls while preserving answer quality. Only a successful intervention should lead to a synthetic-document training pilot.

## Exact configuration

The canonical machine-readable configurations are `configs/stage0_qwen05b.yaml` for Run A/Run B, `configs/stage0_qwen05b_200.yaml` for the 0.5B follow-up, `configs/stage0_qwen15b_200.yaml` for the matched 1.5B comparison, `configs/stage0_qwen15b_label_stability.yaml` for sampling reliability, `configs/stage0_qwen15b_500_confirm.yaml` for fresh-data confirmation, and `configs/stage0_qwen15b_direction_stability.yaml` for the cached direction audit.

- Generator: `Qwen/Qwen2.5-0.5B-Instruct`, unquantized, float16
- Dataset: fixed answerable subset of SQuAD v2 validation, selection seed 1729
- Global seed: 20260928; per-example generation seed is global seed plus fixed subset index
- Prompt: Qwen chat template with context and a short-answer system instruction
- Temperature: 1.0; top-p 1.0; top-k 0; maximum 12 new tokens
- Token position: final token of the rendered prompt immediately before generation
- Transformer blocks: 4, 12, 20, and 24
- Run A: 12 examples, 3 generations, normalized exact-match grouping
- Run B: 64 examples, 5 generations, strict bidirectional NLI grouping
- Entailment model: `cross-encoder/nli-deberta-v3-small`, float32
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

The matched 1.5B run keeps the same 200 examples, five generations, prompt, seeds, 12-token limit, grouped split, NLI model, and analysis. It changes the generator to `Qwen/Qwen2.5-1.5B-Instruct` and uses approximately depth-matched blocks 5, 9, 14, 19, 23, and 28. The unquantized generator uses bfloat16; saved hidden vectors remain float16.

The direction audit loads no language model and generates no new answers. It freezes the confirmation threshold at 0.9899617766489042, uses source train+validation indices as a 401-example development pool, and leaves the source 99-example test split unfit and unscored. Layer 14 is primary and layer 23 is an exploratory challenger. It uses five outer context-grouped folds repeated five times, four inner folds, C values from 0.0001 to 10, a one-standard-error selection rule favoring the smallest eligible C, 20 disjoint split-half comparisons, 100 matched shuffled-label null repetitions, 5,000 context bootstrap resamples, and strictly nested scalar stacking of answer NLL with out-of-fold probe scores.

## Deviations from the paper and upstream repository

1. The paper studies substantially larger language models. This pilot tests 0.5B and 1.5B instruction models.
2. The upstream entailment path defaults to `microsoft/deberta-v2-xlarge-mnli`; the meaningful runs use the smaller `cross-encoder/nli-deberta-v3-small`.
3. Run A uses normalized exact match as a transparent smoke-test grouping method. Run B uses NLI.
4. The probe target is the notebook's cluster-assignment semantic entropy. Other likelihood-weighted semantic-entropy variants were not used as targets.
5. Only the final prompt token (TBG) is tested. The second-last generated token (SLT) is not tested.
6. Run B tests four representative layers rather than every layer. The 0.5B follow-up uses six layers; the 1.5B comparison uses six approximately depth-matched layers rather than identical absolute layer numbers.
7. The logistic probe standardizes each layer's activations. The upstream notebook uses scikit-learn logistic regression without an explicit scaler.
8. The entropy threshold is fitted on training data only rather than using a universal split across several datasets. This avoids test-label leakage but is not the paper's multi-dataset universal threshold.
9. Run B is the handoff's initial 50–100-example meaningful run (64 examples); the separate 200-example follow-up supplies the requested scale-up.
10. The 64-example run uses a fixed train/test split. The 200-example run corrects this limitation with context-grouped train/validation/test partitions and validation-only layer selection.
11. The follow-up adds SQuAD answer-correctness diagnostics and an answer-likelihood-augmented probe. These are Stage 0 diagnostics, not causal interventions or paper-level replications.
12. Qwen 1.5B uses bfloat16 because float16 produced non-finite sampling probabilities during preflight. This is a numerical-stability choice, not quantization.
13. Direction cosine, repeated nested CV, and scalar stacking are project-specific readiness checks rather than a direct reproduction of a reported paper table.
14. The direction audit reuses the confirmation run's train+validation pool. Its 99-example test split was already reported earlier and is reserved rather than treated as a new confirmatory set.

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
- The first 64 generation records were reused from the earlier five-sample run; their hidden states were recomputed because the layer set changed.
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

The matched 1.5B run passed all saved engineering checks.

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

This predeclared diagnostic sampled 50 questions equally from five rank strata of the original five-answer entropy distribution. It reused the original 250 answers and generated 750 new answers, producing 20 answers per question. The fixed cutoff `0.5867070452737222` came from the original Run B training split and was not refitted. No probe was trained in this analysis.

All answers and NLI decisions were cached. The analysis added 978 NLI judgments for the 10-answer prefix and 3,122 for the 20-answer prefix. Answers were non-degenerate: mean distinct normalized answers increased from 2.76 at five samples to 4.44 at ten and 7.46 at twenty; no question had only empty answers.

| Comparison against 20 answers | Label agreement | Cohen's kappa | Spearman correlation | Mean absolute entropy difference | Label flips |
|---|---:|---:|---:|---:|---:|
| 5 answers | 0.840 | 0.683 | 0.808 | 0.400 | 8/50 |
| 10 answers | 0.900 | 0.790 | 0.934 | 0.210 | 5/50 |

The 5-vs-20 stratified-bootstrap 95% intervals were [0.74, 0.92] for agreement, [0.485, 0.841] for kappa, and [0.688, 0.898] for Spearman. The 10-vs-20 intervals were [0.82, 0.96], [0.595, 0.920], and [0.870, 0.964]. Thus all point-estimate gates passed, but the lower bounds for the five-answer comparison fell below the registered gates.

The fixed high-entropy fraction increased from 0.48 at five answers to 0.62 at ten and 0.60 at twenty. Of the eight 5-vs-20 flips, seven were low-to-high and one high-to-low. This shows the practical weakness of five samples: rare alternative meanings can be missed, making some questions look more certain than they do with more sampling. It also means the raw entropy distribution depends on sampling budget, so comparisons must keep that budget fixed.

The result supports semantic entropy as a workable target for the next experiment, but does not validate a model's confidence by itself. It only measures the repeatability of labels constructed from sampled outputs and a smaller NLI model.

## Fresh 500-question Qwen 1.5B confirmation

This preregistered run used 500 SQuAD questions with 10 answers per question. It excluded every ID, exact context, exact question, and question with token-Jaccard similarity at least 0.9 to the earlier 200-question run. The exclusion audit found zero overlaps. The internal train/validation/test split contained 307/94/99 questions and 243/81/81 unique contexts, with zero cross-split ID, question, context, or near-duplicate overlap.

All 5,000 answers were nonempty, with 2,242 distinct normalized answers globally and a mean of 4.554 distinct answers per question. Individual-sample exact match was 0.502, mean F1 was 0.693, and 1,119/5,000 answers used all 12 tokens. Semantic entropy remained non-degenerate: mean 0.737, standard deviation 0.694, and cluster counts ranging from 1 to 10. Hidden states have shape `[500, 6, 1536]`, dtype float16, and finite values.

The train-only entropy threshold was 0.98996. Low/high label counts were 220/87 in training, 66/28 in validation, and 66/33 in test. Layer 14 was frozen as the primary analysis before generation; layer 28 and validation-selected layers were secondary.

### Confirmatory probe results

| Layer | Validation AUROC | Test AUROC | Context-bootstrap 95% interval | Status |
|---:|---:|---:|---:|---|
| 5 | 0.659 | 0.517 | [0.407, 0.633] | secondary |
| 9 | 0.631 | 0.660 | [0.541, 0.768] | secondary |
| **14** | **0.639** | **0.718** | **[0.603, 0.821]** | **predeclared primary** |
| 19 | 0.747 | 0.792 | [0.678, 0.882] | secondary |
| 23 | 0.787 | 0.848 | [0.751, 0.927] | validation-selected secondary |
| 28 | 0.711 | 0.790 | [0.689, 0.877] | predeclared secondary |

At layer 14, 50 shuffled-label fits had mean AUROC 0.498 and empirical 95% interval [0.385, 0.613]. The primary AUROC was at least 0.60, its bootstrap lower bound exceeded 0.50, and it exceeded the shuffled-label upper bound. All three predeclared internal-signal gates passed.

### Incremental-information test

| Method | Test AUROC | Context-bootstrap 95% interval |
|---|---:|---:|
| Constant train mean | 0.500 | — |
| Predictive entropy | 0.859 | [0.783, 0.922] |
| Answer negative log-likelihood | 0.911 | [0.851, 0.958] |
| Frozen layer-14 probe | 0.718 | [0.603, 0.821] |
| Layer 14 + answer NLL | 0.776 | — |

Layer 14 plus answer NLL underperformed answer NLL by 0.135 AUROC; the paired context-bootstrap difference interval was [-0.226, -0.050]. Therefore the incremental-information gate failed, and the preregistered conclusion is **not ready for mechanistic-loss training**. This does not prove that the hidden state contains no unique information; it shows that this standardized linear combination did not extract useful incremental information under the fixed protocol.

Validation selected layer 23, which reached test AUROC 0.848. This is a valid secondary result because selection used validation only, but it still trailed answer NLL, and it cannot replace layer 14 as the preregistered primary result.

On the test split, 87.9% of questions had at least one exact-match answer and mean sample F1 was 0.713. The layer-14 score predicted correctness with AUROC 0.766; the validation-selected layer reached 0.898, while raw answer likelihood reached 0.920. These are diagnostics, not independently preregistered correctness-probe results.

## Cached 500-question direction and stacking audit

This preregistered follow-up used only the 401 source train+validation examples and their 324 unique contexts. The locked 99-example test set was not used for fitting, model selection, gate selection, or scoring. Source artifact hashes, example order, threshold, layer map, split membership, and context separation were verified before analysis.

### Nested predictive performance

| Layer | Role | Development OOF AUROC | Context-bootstrap 95% interval | Continuous-entropy Spearman |
|---:|---|---:|---:|---:|
| **14** | **primary** | **0.738** | **[0.680, 0.793]** | 0.428 |
| 23 | exploratory challenger | 0.823 | [0.774, 0.868] | 0.598 |

Every one of the 25 primary-layer outer fits selected `C=0.0001` using inner grouped CV and the frozen one-standard-error rule. Layer 23 remains exploratory and cannot replace layer 14 as the primary analysis.

### Direction stability

Each of 20 repetitions trained two probes on disjoint 40% context-group subsets and compared their raw-coordinate directions on a shared 20% holdout.

| Layer-14 diagnostic | Result |
|---|---:|
| Median raw-direction cosine | **0.600** |
| 2.5th–97.5th percentile across splits | [0.347, 0.717] |
| Positive cosine fraction | 1.00 |
| Cosine at least 0.5 fraction | 0.85 |
| Median common-holdout score Spearman | 0.900 |
| Adjacent-C cosine | 0.837 |
| Shuffled-null median | -0.009 |
| Shuffled-null 97.5th percentile | 0.123 |
| Matched permutation p-value | 0.0099 |

All eight preregistered layer-14 direction gates passed. The final raw-space directions and exact scaler/probe parameters are frozen in `frozen_probe_directions.npz`; the saved unit vectors have norm 1.0 and the artifact hash is recorded in the metrics JSON.

### Corrected incremental-information test

The earlier hidden-plus-NLL comparison concatenated all 1,536 activations with NLL. This audit instead used only a cross-fitted scalar probe score plus NLL. Each meta-training score, its scaler, and its selected probe regularization excluded that row and its context.

| Model | Development OOF AUROC | OOF log-loss |
|---|---:|---:|
| Answer NLL only | **0.945** | **0.2807** |
| Layer-14 probe score only | 0.744 | 0.5082 |
| Answer NLL + layer-14 score | 0.943 | 0.2834 |

NLL-minus-combined log-loss was -0.00270 with paired context-bootstrap 95% interval [-0.00516, -0.00097]; combined-minus-NLL AUROC was -0.00134 [-0.00296, -0.00008]. The internal score therefore did not add predictive value under this corrected low-dimensional test. Direction stability and incremental value answer different questions: the former now supports a small intervention test, while the latter still blocks mechanistic-loss training.

## Failure analysis and limitations

- The earlier 200-question 1.5B probe was underpowered: its selected-layer interval crossed chance and its test set contained only 41 questions.
- The 100-split audit supports a weak signal but rejects a stable layer-14/19 localization claim; the best validation layer shifts and favors layer 28 in 49% of splits.
- Continuous semantic-entropy prediction is weak, suggesting part of the binary AUROC result depends on how entropy is thresholded.
- Five-answer labels are imperfect: 16% changed when expanded to 20 answers, and their bootstrap lower bounds did not clear the point-estimate gates.
- The entropy cutoff was originally learned from a five-answer distribution. Holding it fixed prevents post hoc tuning but exposes a sampling-budget shift; the next run must use one fixed answer count throughout training and evaluation.
- The fresh 500-question result confirms predictiveness but not incremental value: the frozen internal probe is substantially weaker than answer NLL, and the specified combined model performs worse than NLL alone.
- Layer strength rises sharply in later blocks, and exploratory layer 23 remains more predictive than primary layer 14. The direction audit resolves the immediate stability question for layer 14 but not why the signal is distributed this way.
- Output likelihood baselines remain substantially stronger, and hidden-state-plus-NLL models do not improve on NLL alone.
- Qwen 0.5B often emits incomplete or incorrect answers within the 12-token limit. This validates the machinery but makes the semantic target noisier than it would be for a stronger QA model.
- Qwen 1.5B greatly improves answer quality, but 38% of questions produce only one semantic cluster, changing the target distribution relative to 0.5B.
- The small NLI model is a major deviation. Its high-confidence classifications do not by themselves validate equivalence judgments on short answer fragments.
- The follow-up's 41-example test set still gives wide per-layer confidence intervals. The 50 shuffled-label fits and context bootstrap quantify some instability, but this is not a multi-training-seed study.
- There are 1,536 hidden-state features. The direction audit uses 401 development examples, nested regularization, disjoint fits, and shuffled controls, but it is still not an independent new-data replication of the direction.
- Only one token position and one prompt format are tested.
- A stable decodable direction does not imply that moving activations along it will control uncertainty. Hook placement, zero-intervention equivalence, bidirectionality, random-direction controls, correctness preservation, and wrong-consensus behavior remain untested.
- The reserved 99-example split was already observed in the confirmation report. It remains clean for intervention selection but is not a pristine new-data confirmation set; a later confirmatory steering run should use fresh questions if resources permit.
- No correctness-targeted probe, causal intervention, SDT claim, biological claim, or mechanistic-causality claim is supported here.

## Recommendation

Continue with Qwen 1.5B, but move only to the intervention stage. The fresh-data run confirms a predictive internal association, and the cached audit confirms that its layer-14 direction is reproducible enough to test. The corrected incremental-information gate still fails, and no causal intervention has been tested; Stage 0 therefore validates the measurement and target-selection steps, not the proposed training loss itself.

The next experiment should be a small bidirectional activation-steering diagnostic using the frozen layer-14 unit direction. Before sampling, confirm that the hook captures the same cached activation and that `alpha = 0` exactly reproduces baseline logits. Then compare negative-direction confidence steering, positive-direction uncertainty steering, zero-hook, matched-norm random direction, shuffled direction, and a matched output-temperature control. Evaluate semantic entropy together with exact match/F1, wrong-consensus rate, output length, and degeneration.

Only a bidirectional, control-beating entropy change that preserves answer quality should justify designing a synthetic-document mechanistic-loss pilot. Otherwise, stop or revise the representation rather than scaling training.

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
- `results/run_500_qwen15b_confirm/generations.jsonl`
- `results/run_500_qwen15b_confirm/entailment_judgments.jsonl`
- `results/run_500_qwen15b_confirm/semantic_entropy.jsonl`
- `results/run_500_qwen15b_confirm/hidden_states.npz`
- `results/run_500_qwen15b_confirm/probe_metrics.json`
- `results/run_500_qwen15b_confirm/manifest.json`
- `plots/run_500_qwen15b_confirm_probe_performance_by_layer.png`
- `results/run_500_qwen15b_direction_stability/direction_stability_metrics.json`
- `results/run_500_qwen15b_direction_stability/frozen_probe_directions.npz`
- `plots/run_500_qwen15b_direction_stability.png`
