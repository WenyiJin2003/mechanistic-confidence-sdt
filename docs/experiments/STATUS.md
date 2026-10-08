# Project Status

Last updated: 7 October 2026. **The cached separation audit and fresh v3 test are complete.**

**Current conclusion:** the frozen readouts transfer to expressed certainty in
controlled authored responses. They have not been validated as evidence-sensitive
confidence in a particular answer. Their usefulness as an auxiliary learning
objective remains untested.

## Latest evidence

The fresh v3 study fixes the two response-content candidates suggested by v2.
Both order all 192 assertive/hedged comparisons correctly. On 96 identical-
answer pairs where counterfactual contexts change whether the answer is correct,
final-response-token ordering is 52.1% and response-mean ordering is 51.0%.
Raw likelihood reaches 100%, so the context manipulation is detectable.

Response mean reaches 81.3% for supported versus omitted-role contexts, but
only 25% for rooms. Both candidates fail their registered confirmation checks.
This preserves the earlier v2 boundary failure rather than replacing it with
a selected better score. Read the [v3 report](../../reports/CONFIDENCE_SEPARATION_RESULTS_V3.md).

A separately labelled post-hoc check finds that response-mean scores also rise
for contradicted versus omitted answers on 80.2% of pairs, similar to the 81.3%
supported result. This is compatible with context availability rather than
claim-specific confidence; it does not change the confirmation gates.

The supplementary cached audit finds that the old boundary correctness contrast
reaches only 52.1% on v1 held-out correct/wrong comparisons; its final-response-
token counterpart reaches 79.2%. Thus the comparator's validity depends on the
representation. Direction cosines and low-rank projection do not prove distinct
semantic mechanisms. Read the [audit](../../reports/CONFIDENCE_CORRECTNESS_AUDIT.md).

## Proposed next experiment

The next proposal is a small synthetic-fact SFT study with a candidate answer-state
objective. Compare ordinary SFT, the same data with a frozen-readout loss,
random-direction controls, and extra target-fact cross-entropy. Measure held-out
question recall and retention after matched interference independently of score
optimization. Match auxiliary-gradient strength and log state norms.

Failure to classify contextual correctness narrows the readout's interpretation;
it does not by itself show that an auxiliary commitment objective is useless.
The ordinary training loss supplies the target content. Perfect vector
orthogonality is not a requirement for a useful additional term.

Agree the behavioral objective and protocol before an empirical training run.
QA-to-document transfer and K-to-K′ replacement each require their own controls.
Read the [next-experiment proposal](NEXT_EXPERIMENT.md). It is not yet a
preregistration. No training or causal intervention has been run.

## Access and reproduction

- [All new questions and responses](../../datasets/confidence-separation-v3/README.md)
- [Registered v3 design](CONFIDENCE_SEPARATION_V3_PREREGISTRATION.md)
- [V3 configuration](../../configs/confidence_separation_v3.yaml)
- [Experiment map](EXPERIMENT_MAP.md), [all reports](../../reports/README.md), [code map](../../code/README.md)

Historical Stage 0/0B uncertainty results and v1/v2 reports remain available
under their original experiment names. They address different targets and
token positions; they should not be merged into one “confidence probe.”
