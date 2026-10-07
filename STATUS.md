# Project Status

Last updated: 7 October 2026.

**Current decision: evaluate frozen-readout transfer v2 before considering an
internal loss for synthetic-document training (SDT).** Its design and
[configuration](configs/paired_confidence_transfer_v2.yaml) are registered;
data/extraction validation and outcome evaluation are pending. No v2 scores are
available yet.

Paired pilot v1 is complete. Its layer-14 direction ordered 48/48 held-out
expressed-certainty pairs across 24 unseen sources. This is a controlled wording
result: 12/200 shuffled directions were also perfect, and five family-C reversals
occurred outside the test split. It does not establish a unique confidence
mechanism or an SDT-ready loss. The [v1 report](PAIRED_CONFIDENCE_RESULTS_V1.md)
contains the complete evidence and limitations.

## Next gate

V2 applies the unchanged v1 readout to 48 new fictional fact sources. Its two
required endpoints are natural wording transfer and supported-versus-omitted
evidence ordering for identical neutral QA responses. Both require ordering at
least 0.65 with a source-bootstrap lower bound above chance, plus the registered
correctness and fact-type checks. A separate response-likelihood manipulation
check must pass; otherwise the evidence test is inconclusive.

A wording-only pass supports wording transfer. Passing both endpoints supports
controlled supplied-context sensitivity. Neither outcome validates subjective
confidence, calibration, causal steering, or confidence-loss training. See the
[v2 preregistration](CONFIDENCE_TRANSFER_PREREGISTRATION_V2.md) and
[execution/results page](CONFIDENCE_TRANSFER_RESULTS_V2.md).

## Earlier evidence

Stage 0 found a reproducible pre-answer semantic-uncertainty association. Stage
0B found no reliable incremental value from a post-answer probe over the same
answer's likelihood. Those targets differ from the paired pilot's expressed
certainty. Their [historical report](RESULTS_STAGE0.md) is preserved; the current
research sequence is in [README.md](README.md).
