# Confidence Readouts Before Synthetic-Document Training

**Transfer v2 is complete: the frozen readout transfers to new certainty wording
and shows a pooled association with supplied evidence, but fails its registered
fact-type robustness gate. The boundary readout is not ready for an SDT loss.**

The primary direction was unchanged from paired pilot v1. V2 tested 48 fresh
fictional facts, with identical neutral answer tokens across evidence conditions.

| Required endpoint | Ordering | Source-bootstrap 95% interval |
|---|---:|---:|
| New confident/hedged wording | 87/96 (90.6%) | 81.3–97.9% |
| Neutral QA: supported > omitted evidence | 35/48 (72.9%) | 60.4–85.4% |
| Independent raw-likelihood manipulation check | 48/48 (100%) | Saturated empirical interval |

Both pooled readout scores exceed their thresholds, but release-year evidence
ordering is **4/12 (33.3%)**, below chance. The preregistration required no fact
type below chance. The evidence manipulation passed, so this is a completed
robustness failure, not absence of a pooled signal or an inconclusive manipulation.
See the [v2 results](CONFIDENCE_TRANSFER_RESULTS_V2.md).

The research aim is ordinary synthetic-document training (SDT) plus a possible
auxiliary internal-confidence loss that preserves answer accuracy. Before that
term can guide training, we need to know whether it measures support for an
answer rather than rewarding assertive wording. Transfer is one prerequisite;
causal effects and held-out accuracy/calibration still need separate validation.

## Next decision

The separately frozen layer-14 final-content and response-mean readouts reached
93.8% evidence ordering; their wording scores were 86.5% and 100%, respectively.
They are candidates for **prospective confirmation on fresh data**, not substitutes
for the failed primary endpoint. Fix the candidate positions and decision rules
before testing new facts, field names, and same-proposition wording controls.

Removing the single v1 correctness direction reduced primary evidence ordering
to 50%; that ablation does not prove independence or a confidence mechanism.
Strong individual null directions also remain possible. No subjective-confidence,
calibration, causal-control, or training-loss claim is established.

## Research sequence

Stage 0 and Stage 0B are this project's measurement-stage names, not stages
defined by the original paper. These studies use distinct targets and endpoints.

| Study | Question | Conclusion |
|---|---|---|
| [Stage 0](RESULTS_STAGE0.md) | Do pre-answer states predict sampled semantic uncertainty? | Reproducible association and direction; no improvement over answer likelihood. |
| [Stage 0B](RESULTS_STAGE0.md#stage-0b--post-answer-hidden-state-diagnostic) | Does a post-answer probe add information beyond the same answer's likelihood? | No reliable incremental gain. |
| [Paired pilot v1](PAIRED_CONFIDENCE_RESULTS_V1.md) | Can a readout order expressed certainty with answer content fixed? | Candidate on controlled rewrites; shared phrasing shifts and broad nulls limit interpretation. |
| [Frozen transfer v2](CONFIDENCE_TRANSFER_RESULTS_V2.md) | Does that unchanged readout transfer to wording and supplied evidence? | Pooled transfer association; required fact-type gate fails. |

```mermaid
flowchart LR
    V["v2: primary robustness gate fails"] --> F["Freeze content-readout candidates; test fresh data"]
    F -->|"only if confirmed"| C["Causal and answer-quality checks"]
    C -->|"only if validated"| L["Consider an auxiliary SDT loss"]
```

## Evidence and reproduction

- [Current status](STATUS.md) — completed result and next decision
- [V2 results](CONFIDENCE_TRANSFER_RESULTS_V2.md), [preregistration](CONFIDENCE_TRANSFER_PREREGISTRATION_V2.md), and [execution runbook](CONFIDENCE_TRANSFER_README_V2.md)
- [V1 results](PAIRED_CONFIDENCE_RESULTS_V1.md), [preregistration](PAIRED_CONFIDENCE_PREREGISTRATION_V1.md), and [execution](PAIRED_CONFIDENCE_README.md)
- [Stage 0/0B report](RESULTS_STAGE0.md) and [technical runbook](README_STAGE0.md) — historical findings preserved
- [Artifact index](results/README.md) and [documentation/provenance](docs/README.md)

This small-scale Qwen study adapts Kossen et al.'s
[*Semantic Entropy Probes*](https://arxiv.org/abs/2406.15927) and
[official OATML implementation](https://github.com/OATML/semantic-entropy-probes);
it is not a full paper replication. The preserved upstream snapshot is commit
`02e2167dd1c00e27080d421f9b40e13e00f0452b`, with its MIT license retained.
