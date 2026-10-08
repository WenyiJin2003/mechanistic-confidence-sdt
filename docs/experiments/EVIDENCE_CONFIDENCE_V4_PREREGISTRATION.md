# Evidence-Sensitive Readout v4: Registered Pilot Design

7 October 2026. Design to be committed before any v4 model extraction.

## Question and scope

Can a new linear readout track support for a particular supplied answer across
fresh facts and unfamiliar wording, and agree with the frozen model's own
output choices? Earlier v1 vectors captured expressed certainty, while v3
failed identical-answer support-versus-contradiction comparisons. V4 fits a
different target from new training data. It does not refit a v1 vector on v3
test outcomes.

The label is agreement with the displayed fictional record. A positive result
establishes a candidate evidence-support measurement on these tasks. It does
not establish subjective belief, an independent confidence mechanism, calibrated
probabilities, or a validated SDT loss. In particular, responding to supplied
context is not the same as retrieving facts learned in model parameters.

## Fixed model and data

- Local, unquantized Qwen/Qwen2.5-1.5B-Instruct; revision
  `989aa7980e4cf806f80c7fef2b1adb7bc71aa306`; bfloat16 on MPS where available,
  then CUDA or CPU with separate device fingerprints.
- 168 fictional records, four schemas: access codes, assigned rooms, release
  years and materials. Per schema: 24 training, 6 validation, 12 test records.
  Totals: 96 train, 24 validation, 48 untouched test.
- Entity identities, candidate values and source groups are disjoint across
  splits and compared against earlier catalogs. New context, question and
  neutral-response templates are held out by split: T1 train, T2 validation,
  T3/T4 test. Candidate order and answer key are balanced.
- Each record has two candidate values and three contexts: A supported,
  B supported, queried role omitted. Both values remain at fixed written
  locations; role assignments change. Omission carries no correctness label.
- Both neutral answers are supplied in all contexts: 1,008 rows. Test records
  additionally have confident and hedged versions in every context: 576 rows.
  Total: 1,584 teacher-forced responses.
- Within a same-answer context comparison, response IDs, prompt lengths and
  absolute response positions match exactly. Omission-role selection can use
  only the pinned tokenizer, from predeclared unrelated-role alternatives;
  it cannot inspect model scores. Candidate values have equal token lengths
  within each record. Do not truncate or remove failed records after scoring.

## Fitting and token positions

The primary representation is layer 14, the mean of ordinary response-content
token states, including the full supplied answer and excluding the end marker.
Layer 14 means `hidden_states[14]`, after transformer block 14.

For each training source and each answer, form the same-answer contrast between
supporting and contradicting contexts. Fit an L2 logistic linear classifier to
these differences and their sign-reversed copies. The reversed copy reverses
the label, giving balanced classes and no fitted intercept. Every source has
the same number of comparisons. Scale features on this training-only mirrored
pool. Fix `C=0.01`, without validation or test tuning. Convert the coefficients
back to raw-state coordinates and unit-normalize for scoring.

```math
\Delta h_{q,a}=h_{q,a}^{\mathrm{supported}}-h_{q,a}^{\mathrm{contradicted}},
\qquad s(h)=v^\top h.
```

The score orders evidence support; the classifier sigmoid is not reported as
the model's probability of being correct. Omitted contexts and styled responses
never fit the readout. Validation records provide diagnostics only, without
model, position, regularization or sign selection.

Prespecified secondary comparisons: the same logistic procedure at layer-14
final ordinary response token; a source-balanced mean contrast at response
mean; the frozen v1 certainty directions at their original response-mean and
final-content positions. A prompt-only candidate-blind contrast is a negative
control. Secondary success cannot rescue a failed primary endpoint.

## Held-out endpoints and controls

Primary neutral endpoints, testing the same written answer:

1. Supported > contradicted.
2. Supported > omitted.
3. Omitted > contradicted.

Each endpoint has 96 comparisons bundled in 48 independent test records.
Calculate 1 for positive margins, 0 for reversed margins and 0.5 for exact ties.
Average within record, then across records. Report 2,000 whole-record bootstrap
draws and separate fact-schema, answer-key and context-template strata.

Each neutral endpoint must reach 65%, have its 95% lower bound above 50%,
and have no fact-schema score below chance. Supported-versus-contradicted
ordering must also reach 65% with a lower bound above chance separately under
confident and hedged wording. Report wording effects separately; high scores
on confidently phrased wrong answers remain an interpretation risk.

Fit 200 controls with one sign flip per training record, preserving both answer
comparisons as a bundle. Keep C and training-only scaling fixed. The primary
neutral support-versus-contradiction score must exceed the controls' 95th
percentile. Also report 200 norm-matched random directions, a constant/length
baseline, same-response likelihood, and the frozen old certainty directions.
Control distributions are conditional diagnostics, not permutation p-values.

The likelihood manipulation check requires supported-versus-contradicted
ordering >=75%, with a 95% lower bound above chance. A failed check makes
the interpretation inconclusive rather than proving an absent internal signal.

## Separate output-behavior validation

For each test record/context, use an independently phrased question requesting
a bare value and allowing `unknown` when the record lacks the queried fact.
There are 144 prompts. These prompts and all output measurements are excluded
from fitting and feature selection.

1. Score both complete bare candidate sequences using preceding-token logits.
   Candidate sequence lengths match. Save full sequence log-probabilities and
   their log odds. The two-candidate normalization ignores other/unknown
   outputs, so it cannot establish calibration.
2. Generate one unconstrained greedy answer per prompt, at most 12 new tokens.
   Record the exact text and IDs. Count candidate A, candidate B, unknown and
   other responses; keep all responses, including noncandidate outputs.
3. Compare the frozen probe's A-minus-B neutral-answer margin in each context
   with the independent output log odds and generated choices. Report Spearman
   correlation with source bootstrap, condition/fact-schema-centered correlation,
   coverage and both unconditional and covered-only choice agreement.

Behavior checks require positive overall and condition/fact-schema-centered
correlations, each with its source-bootstrap lower bound above zero,
>=65% known-context generated-answer correctness with
lower bound above chance, and >=75% candidate coverage on known contexts.
Unknown output on omitted contexts is reported separately; omission is not
silently given an invented correct candidate. All exact-match and explicit
candidate-mention parsing choices are reported transparently.

Passing evidence and behavior checks is convergent evidence for a controlled
measurement. It is not sufficient to claim that all lexical/context shortcuts
are removed. If those checks pass, the next measurement study should add graded
or conflicting evidence and natural/generated-answer transfer before an SDT
loss is described as a validated mechanistic confidence objective.

## Freeze, outputs and decision

Commit this protocol, config, data, data audit, extraction/behavior code and
analysis implementation before the first model forward. Verify exact resume
and finite states on four training records, one per schema, without inspecting
their predictive scores. Maintain distinct caches for changed inputs/settings.

Save original inputs, response states, fitted vectors, scaling provenance,
row-level scores, behavior outputs, metrics, plot, source browser and manifests
locally. Publish readable examples, aggregate arrays, code and reports to
GitHub; model weights and per-input inference caches remain local.

If evidence or behavior validation fails, retain the result and diagnose which
condition failed. Do not increase the dataset, switch representation or tune C
on the observed test set to obtain a passing result. No model fine-tuning,
activation intervention, OpenAI API or NLI model is used in this experiment.
