# Evidence-Sensitive Readout v4

7 October 2026. **Study in progress; numerical results are pending.**

The earlier experiments established a transferable readout of expressed
certainty. V3 did not validate it as confidence in a specific answer: frozen
response-content readouts ranked the same answer higher under supporting than
contradicting evidence only 52.1% and 51.0% of the time.

V4 tests a different measurement. It learns contextual answer support on new
training records and checks unseen records, new wording and independently
elicited model behavior. This is the next measurement step; the synthetic-fact
training proposal is deferred.

## Registered study

- 168 fictional records across four schemas: 96 train, 24 validation, 48 test.
- Source identities, candidate values and context/question/neutral-response
  templates held out by split.
- 1,008 neutral responses under supporting, omitted and contradicting contexts;
  576 test-only style variants, for 1,584 supplied responses overall.
- Fixed primary readout: layer-14 response-content mean, paired logistic
  regression with C=0.01 and training-only scaling.
- 144 separate output prompts with greedy generations and both candidate
  sequence likelihoods; none enters readout fitting or selection.
- Registered evidence-ordering, style, null-control and behavioral-validity
  gates, including condition/schema-centered correlations.

## Results and interpretation

No v4 performance estimate is reported before the registered run. The final
report will include every registered endpoint, its source-level uncertainty,
all control comparisons and any failed schema or behavioral check.

Success would provide convergent evidence for an answer-support measurement on
these controlled tasks. It would not establish subjective belief, general
confidence, calibrated probability, causal control or improved synthetic-fact
learning. The data use simple fictional registries rather than natural
generated-answer confidence labels.

## Links

- [Registered design](../docs/experiments/EVIDENCE_CONFIDENCE_V4_PREREGISTRATION.md)
- [Study guide and reproduction](../docs/experiments/EVIDENCE_CONFIDENCE_README_V4.md)
- [Exact configuration](../configs/evidence_confidence_v4.yaml)
- [Runner](../scripts/run_evidence_confidence_v4.py)
- [Current project status](../docs/experiments/STATUS.md)
- [Completed v3 result](CONFIDENCE_SEPARATION_RESULTS_V3.md)
