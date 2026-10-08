# Evidence-Sensitive Readout v4

**In progress.** This study asks whether a new internal readout responds to
support for a particular answer and agrees with the model's own output choices.
It follows v3's finding that the earlier certainty directions mainly tracked
assertive versus tentative language.

The measurement takes priority over the
[deferred training proposal](NEXT_EXPERIMENT.md). A score that recognizes
support can be useful, but that alone would not establish subjective confidence
or justify treating its optimization as improved fact learning.

## Data and extraction

| Component | Fixed design |
|---|---|
| Model | Frozen Qwen2.5-1.5B-Instruct, pinned local snapshot |
| Records | 168 new fictional records: 96 train, 24 validation, 48 test |
| Fact schemas | Access codes, assigned rooms, release years, materials |
| Neutral responses | Both candidate answers in three contexts: 1,008 rows |
| Style stress test | Confident and hedged versions on test records only: 576 rows |
| Independent behavior | Different question paraphrases: 144 greedy answers and two candidate likelihoods per prompt |
| Primary state | Layer 14 mean over complete ordinary response content, excluding the end marker |

Source identities, candidate values and context/question/neutral-answer
templates are disjoint across splits. Each context lists both values at fixed
positions. The queried role supports A, supports B, or is omitted. Omission
does not have an invented correctness label. Identical-answer comparisons have
matching response IDs, prompt lengths and absolute response positions.

Materials and room values are fictional numbered mixtures and suites. These
simple authored schemas make the controls tractable but limit generalization
to natural QA and facts learned from documents.

## Fit and validation

Fit only training neutral support-versus-contradiction differences and their
sign-reversed copies. Use L2 logistic regression, C=0.01, no intercept, and
training-only feature scaling. Convert coefficients to raw-state coordinates
and unit-normalize:

```math
\Delta h_{q,a}=h^{\mathrm{supported}}_{q,a}-h^{\mathrm{contradicted}}_{q,a},
\qquad s(h)=v^\top h.
```

Validation is diagnostic; it cannot select a representation, sign or penalty.
The score is an ordering measurement, not a calibrated probability.

Held-out tests require supported > contradicted, supported > omitted and
omitted > contradicted. Each must reach 65%, with source-bootstrap lower
bound above 50% and no fact schema below chance. Evidence ordering must also
survive both certainty styles and exceed the registered shuffled-label control
criterion. Old certainty vectors, random directions, constant/length and
prompt-only controls remain visible.

Independent questions ask for a bare value or `unknown`. All generated
outputs are retained. Behavioral validation checks candidate likelihood
correlations overall and after centering by condition and schema, generated
correctness and candidate coverage. Two-candidate normalized likelihood omits
other possible answers and cannot establish calibration.

The [registered design](EVIDENCE_CONFIDENCE_V4_PREREGISTRATION.md) specifies
every gate. The [report](../../reports/EVIDENCE_CONFIDENCE_RESULTS_V4.md) records
results and failures once the run finishes.

## Reproduction

From the repository root, using the existing dependencies and local snapshot:

```bash
python scripts/run_evidence_confidence_v4.py --mode build
python scripts/run_evidence_confidence_v4.py --mode audit
python scripts/run_evidence_confidence_v4.py --mode sanity
python scripts/run_evidence_confidence_v4.py --mode run
```

The protocol, inputs and implementation must be committed before model
extraction. The runner verifies that freeze and reuses matching caches.

- [Exact settings](../../configs/evidence_confidence_v4.yaml)
- [Run entry point](../../scripts/run_evidence_confidence_v4.py)
- [Data gates](../../confidence_pilot/evidence_data_v4.py)
- [Readout analysis](../../confidence_pilot/evidence_analysis_v4.py)
- [Behavior extraction](../../confidence_pilot/evidence_behavior_v4.py)

Model weights are unchanged. No fine-tuning, activation intervention or
external model API is used. A passing result would motivate broader measurement
tests before an internal confidence objective is described as validated.
