# Project Status

Last updated: 8 October 2026. **V4 is complete. A new support readout transfers,
but confidence validation remains incomplete. Training stays deferred.**

**Current conclusion:** the earlier frozen readouts transfer to expressed
certainty. A new support-trained probe reaches 71.9% on identical-answer
support-versus-contradiction comparisons, including confident and hedged styles.
It fails missing-evidence and independent behavioral validation. We have
controlled evidence-support recognition, without a validated confidence loss
or demonstrated improvement in fact learning.

## Latest evidence

V4 evaluates 48 independent held-out records. Neutral support > contradiction
reaches **69/96 comparisons, 71.9% [64.6%, 79.2%]**, exceeding the shuffled
95th percentile of 61.5%. Confident and hedged comparisons also score 71.9%.

Supported > omitted is **55.2% [43.8, 66.7]**; omitted > contradicted is
**60.4% [47.9, 72.9]**. Material support-versus-omission falls to 12.5%, and
year omission-versus-contradiction is 37.5%. Missing evidence is not a false
answer label; the expected three-level ordering does not pass.

Independent output likelihood correlates with probe candidate margins at
**0.450 [0.318, 0.591]** overall, but condition/schema-centered correlation is
**0.205 [−0.016, 0.384]**. Known-context candidate coverage is 71.9%, below
75%. Generated correctness is 69.8% with explicit candidate parsing, or 65.6%
with strict exact-value matching. Omitted contexts elicit `unknown` on 40/48
prompts. Field-name outputs, unnecessary unknowns and three truncated answers
contribute to the behavioral interface failure. No outputs were rerun or
reclassified. The [v4 report](../../reports/EVIDENCE_CONFIDENCE_RESULTS_V4.md)
retains all failed gates, controls, strata and generated text.

## Earlier evidence

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

## Completed experiment: evidence-sensitive measurement v4

V4 fits a new answer-support readout using 96 new training records and tests
48 untouched records with unfamiliar context, question and answer templates.
Twenty-four validation records are diagnostic only. Both candidate answers
are supplied under supporting, omitted and contradicting evidence, with exact
answer/token-position controls. Test-only confident and hedged variants check
whether evidence ordering survives changes in tone.

The fixed primary method is paired L2 logistic regression (C=0.01) at the
layer-14 response-content mean. Independent paraphrases produce 144 short
greedy answers and full candidate sequence likelihoods. The registered gates
require evidence ordering, shuffled-label separation and behavioral agreement,
including correlations centered within evidence-condition/fact-schema groups.
The whole-study gate failed; no secondary readout replaces the primary.

Read the [v4 runbook](EVIDENCE_CONFIDENCE_README_V4.md),
[registered design](EVIDENCE_CONFIDENCE_V4_PREREGISTRATION.md),
[settings](../../configs/evidence_confidence_v4.yaml) and
[completed report](../../reports/EVIDENCE_CONFIDENCE_RESULTS_V4.md).

The next measurement should preflight clearer field mapping and sufficient
generation length on fresh training-only examples, counterbalance behavior
wording independently of candidate order, and test graded/conflicting evidence
on new records. Natural/generated-answer transfer remains necessary. Do not
tune v4's representation or thresholds on its observed test set. These results
do not establish subjective confidence, independence from correctness or a
causal mechanism.

## Deferred training proposal

The earlier proposal is a small synthetic-fact SFT study with a candidate answer-state
objective. Compare ordinary SFT, the same data with a frozen-readout loss,
random-direction controls, and extra target-fact cross-entropy. Measure held-out
question recall and retention after matched interference independently of score
optimization. Match auxiliary-gradient strength and log state norms.

Failure to classify contextual correctness narrows the readout's interpretation;
it does not by itself show that an auxiliary commitment objective is useless.
The ordinary training loss supplies the target content. Perfect vector
orthogonality is not a requirement for a useful additional term.

Measurement validation now takes priority. Agree the behavioral objective and
protocol before any later empirical training run.
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
