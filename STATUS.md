# Project Status

Last updated: 7 October 2026. **Frozen-readout transfer v2 is complete.**

**Decision: do not use the primary boundary readout as an SDT loss. Preregister
fresh confirmation of the response-content candidates next.**

The unchanged v1 layer-14 boundary direction ordered 87/96 new wording pairs
(90.6%, source-bootstrap interval 81.3–97.9%) and 35/48 neutral QA evidence pairs
(72.9%, 60.4–85.4%). The latter holds answer tokens and prompt lengths fixed.
Raw negative mean-token NLL ordered all 48 evidence pairs correctly, passing
the independent manipulation check.

## Why the primary gate fails

Release-year evidence ordering was 4/12 (33.3%), violating the registered rule
that no fact type fall below chance. Access codes scored 8/12, materials 11/12,
and rooms 12/12. Pooled evidence ordering is above chance in this sample, but
the required robustness gate fails. The manipulation itself is valid.

Natural wording passed its registered checks, including correct/wrong content.
The study still labels supplied-context sufficiency and expressed certainty,
not subjective confidence or calibration. Strong individual null directions
and the drop to 50% evidence ordering after removing one estimated correctness
direction limit mechanistic interpretation.

## Next gate

The separately frozen layer-14 final-content and response-mean candidates
reached 93.8% evidence ordering, with wording scores of 86.5% and 100%.
They cannot rescue the failed primary endpoint. A new confirmation should
prospectively fix candidate positions and gates, then test fresh facts, varied
field names, and same-proposition wording controls against raw likelihood.

The eventual aim remains ordinary synthetic-document training (SDT) plus a
possible auxiliary internal-confidence loss that preserves answer accuracy.
Transfer confirmation comes before causal and answer-quality checks; no
confidence loss has been validated or trained.

Read the [v2 results](CONFIDENCE_TRANSFER_RESULTS_V2.md),
[unchanged preregistration](CONFIDENCE_TRANSFER_PREREGISTRATION_V2.md), and
[execution runbook](CONFIDENCE_TRANSFER_README_V2.md). The
[root README](README.md) distinguishes this work from the preserved
[Stage 0/0B semantic-uncertainty diagnostics](RESULTS_STAGE0.md) and
[paired expressed-certainty pilot v1](PAIRED_CONFIDENCE_RESULTS_V1.md).
