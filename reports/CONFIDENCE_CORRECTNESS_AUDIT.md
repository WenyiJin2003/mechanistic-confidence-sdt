# Cached confidence–correctness audit

7 October 2026. This is a **post-hoc, cache-only audit of previously examined v1/v2 test data**, not fresh confirmation.

The old layer-14 boundary readout reliably tracks expressed certainty, but its estimated correctness comparator is weak on held-out answer orderings. Removing that comparator preserves wording sensitivity while losing much of the pooled v2 context-evidence signal. These results support further behavioral validation; they do not establish orthogonal mechanisms, independence from correctness, or a useful training loss.

## Estimators and held-out comparisons

The confidence vector is the exact saved v1 unit vector. At each of the four predefined representations, the correctness vector is a separate unit-normalized mean correct-minus-wrong contrast: average confident and hedged responses within each A/B family, average families within a source, then weight the 72 v1 training sources equally. No validation, test-C, or v2 activation enters fitting. A mean contrast is a candidate readout, **not a gold-standard correctness mechanism**. Correct and wrong v1 answers have different text, so content, lexical and answer-position cues remain possible.

The primary representation remains layer 14 at the assistant end marker. Its v1 test-C endpoint has 24 sources and 96 response rows: 48 certainty comparisons and, separately, 48 true-versus-wrong comparisons. These are not 96 independent correctness pairs. Correctness comparisons hold certainty style fixed; certainty comparisons hold correctness fixed. Positive margins score 1, reversals 0, and ties 0.5. The table reports source-equal accuracy and 95% source-bootstrap intervals for fixed fitted vectors.

| L14 boundary readout | Confident > hedged | Correct > wrong |
|---|---:|---:|
| Frozen confidence vector | 100.0% [100.0, 100.0] | 58.3% [37.5, 75.0] |
| Train-only correctness mean contrast | 64.6% [45.8, 83.3] | 52.1% [35.4, 70.8] |

For the correctness vector, true-versus-wrong ordering is 54.2% under confident wording and 50.0% under hedging. The confidence vector reaches 50.0% and 66.7%, respectively. Its certainty ordering is 100% for both correct and wrong content, as expected for the authored-style target; high scores do not imply a true answer. The correct-minus-wrong difference in certainty margins is −0.0066, with a source-paired interval spanning zero.

The predefined final-response-token correctness vector performs better: 79.2% [64.6, 91.7] on the same held-out correctness comparisons. Response-content mean reaches 62.5% [43.7, 81.3]. Each position uses its own training vector; the boundary vector is not transplanted to another position. The final response token may be punctuation, and response-content mean averages the complete response rather than only its answer span. Domain-specific boundary correctness vectors, fitted on 24 training sources apiece, reach only 50.0–53.1% on the other domains' test-C sources.

## Geometry and sampling uncertainty

The raw Euclidean cosine between the two primary unit vectors is 0.3017, corresponding to 72.4° and 9.1% squared directional overlap. In 1,000 training-source bootstrap refits of **both** vectors, the cosine interval is [0.1889, 0.3313]. Across 250 random split-half fits, mean direction agreement is 0.966 for confidence and 0.643 for correctness; the correctness estimate is appreciably less stable.

An additional 1,000-draw bootstrap independently resamples whole training and test source bundles, refits both directions, and evaluates the resampled test bundles. The primary correctness accuracy interval becomes [33.3, 72.9]%; confidence-to-certainty becomes [97.9, 100.0]%. Source bundles preserve the correlated answer/style comparisons; bootstrap intervals do not measure arbitrary new-domain or new-wording generalization. Saturated fixed-vector intervals describe this sample, not guaranteed population performance.

A cosine describes geometry in the chosen coordinates. It does not determine score covariance: even when $v^\top c=0$, $v^\top\Sigma c$ can be nonzero. Activation anisotropy, coordinate scaling, noisy contrasts, and unmodeled nonlinear readouts limit interpretation. This audit uses raw-space differences without whitening and makes no claim of semantic independence.

## Projection and exploratory subspaces

For the primary mean-contrast removal, the residual is $v_{\perp}=v-(v^\top c)c$. Its norm is 0.953389. The old saved residual was renormalized; this audit explicitly restores the original confidence-vector scale when comparing margins. Positive rescaling leaves ordering unchanged. The following changes are paired within v2 sources, with 1,000 source-bundle bootstrap draws.

| V2 endpoint | Original ordering | After mean-contrast removal | Paired change, percentage points [95% interval] |
|---|---:|---:|---:|
| Natural certainty wording | 90.6% | 90.6% | 0.0 [0.0, 0.0] |
| Neutral QA: supported > omitted | 72.9% | 50.0% | −22.9 [−35.5, −10.4] |
| Neutral document: supported > omitted | 75.0% | 54.2% | −20.8 [−33.3, −8.3] |

The QA mean margin falls from 0.0600 to 0.00316 on the common scale; the paired decrease is 0.05685 [0.04330, 0.07098]. With training and v2 source uncertainty jointly propagated, the QA ordering-change interval remains negative, [−37.5, −2.1] percentage points. The correctness comparator itself reaches 91.7% on this QA evidence endpoint, despite weak v1 boundary truth ordering. That association is compatible with contextual evidence sensitivity and does not validate the comparator as a general truth axis. Projection changes the scoring rule; it is not a model intervention or a causal identification result.

Exploratory uncentered SVD of the 72 training-source correctness contrasts gives rank-1/2/3 subspaces capturing 19.8/29.5/37.3% of training contrast energy. These are distinct from removal of the mean contrast. Their confidence projections retain strong wording ordering, while v2 QA evidence ordering becomes 43.8/50.0/60.4%; 200 matched-rank random subspace controls remain near 72%. A fixed train-only ridge readout refitted after each removal has wide, chance-containing held-out correctness intervals. Neither low-rank removal nor a weak residual decoder establishes that all correctness information has been erased.

Orthogonality is not a prerequisite for a useful regularizer: knowledge and justified confidence may share useful features. A proposed confidence loss should demonstrate the agreed held-out improvement, such as learning and using the SDT target facts; calibration is a separate requirement if it is part of the objective. The geometry here cannot substitute for that experiment, and removing an overlapping component may discard desirable context sensitivity. A candidate loss can be tried without first proving an independent confidence mechanism, provided its usefulness is tested through behavior rather than its own score.

## Reproducibility

The audit made zero model, generation, API or NLI calls. All canonical input hashes matched before and after; eight focused tests passed, including source grouping, train-only fitting, exact frozen-vector reproduction and common-scale margins.

Implementation: [analysis](../confidence_pilot/separation_audit.py), [runner](../scripts/run_separation_audit.py), [configuration](../configs/confidence_correctness_audit.yaml), [tests](../tests/test_separation_audit.py). Full outputs: [metrics](../results/confidence_correctness_audit/audit_metrics.json), [directions](../results/confidence_correctness_audit/audit_directions.npz), [manifest](../results/confidence_correctness_audit/manifest.json). Prior context: [v1 report](PAIRED_CONFIDENCE_RESULTS_V1.md), [v2 report](CONFIDENCE_TRANSFER_RESULTS_V2.md).
