# Semantic Uncertainty and Expressed-Certainty Readouts

This repository studies two related but distinct constructs: semantic uncertainty
in sampled answers and expressed certainty in fixed written responses. It adapts
Kossen et al.'s [*Semantic Entropy Probes*](https://arxiv.org/abs/2406.15927) and
[official OATML implementation](https://github.com/OATML/semantic-entropy-probes)
for small-scale Qwen experiments, then adds a controlled paired-response pilot.
It is not a full replication of the original paper.

## Current conclusion

Paired confidence pilot v1 supports a candidate layer-14 readout of **expressed
certainty** on a controlled dataset: it ordered all 48 held-out rewrite pairs
across 24 unseen sources. Shared phrasing effects remain plausible: 12 of 200
shuffled directions also achieved perfect ordering, and five family-C pairs
failed outside the test split. See the [v1 results](PAIRED_CONFIDENCE_RESULTS_V1.md).

**Next decision: test the unchanged v1 readout on fresh wording and on identical
neutral answers with different supplied evidence, before considering a
mechanistic loss for synthetic-document training (SDT).** Transfer v2 is
[preregistered](CONFIDENCE_TRANSFER_PREREGISTRATION_V2.md); no v2 outcome has
been evaluated yet. Its [results page](CONFIDENCE_TRANSFER_RESULTS_V2.md) records
the current execution state.

The present evidence does not establish subjective confidence, factual belief,
calibration, or causal control. A tone-sensitive readout could reward assertive
writing without tracking support for an answer. The evidence-transfer test
therefore comes before any decision to use this readout as an SDT loss; even a
successful transfer would leave causal and training validation outstanding.

## Research sequence

Stage 0 and Stage 0B are this project's names for measurement diagnostics, not
stages defined by the original paper. Stage 0B adds a post-answer comparison
using the same observed answer for the probe and likelihood baseline.

| Study | Question | Evidence and decision |
|---|---|---|
| Stage 0 | Can pre-answer activations predict sampled semantic uncertainty? | A reproducible association and direction, without improvement over answer likelihood. [Report](RESULTS_STAGE0.md) |
| Stage 0B | Does a post-answer probe add information beyond the same answer's likelihood? | No reliable incremental gain. [Report](RESULTS_STAGE0.md#stage-0b--post-answer-hidden-state-diagnostic) |
| Paired pilot v1 | Can a readout distinguish expressed certainty with answer content fixed? | A candidate on controlled rewrites; broader transfer remains untested. [Report](PAIRED_CONFIDENCE_RESULTS_V1.md) |
| Frozen-readout transfer v2 | Does the v1 direction transfer to fresh wording and neutral answers under different evidence? | Design registered; outcomes pending. [Design](CONFIDENCE_TRANSFER_PREREGISTRATION_V2.md) |

These studies have different targets and endpoints. Their scores are not a
single improving confidence benchmark. Historical reports retain their original
findings and decisions; [STATUS.md](STATUS.md) gives the current project decision.

## Transfer v2 at a glance

The primary v1 layer-14 boundary direction is frozen without refitting, sign
selection, or new thresholds. Forty-eight fictional registry facts supply fresh
test sources. Two required endpoints ask whether it orders new confident/hedged
wording and whether it scores a neutral answer higher when the context supplies
its target fact than when that fact is omitted. The evidence comparison requires
identical response tokens and exactly matched full prompt token counts.

An independent response-likelihood check must verify that the evidence
manipulation works. Both primary endpoints must pass their registered gates;
secondary positions and document-format results cannot rescue a failure.
Supported-versus-omitted labels measure supplied-context sufficiency, not the
model's true confidence. The [preregistration](CONFIDENCE_TRANSFER_PREREGISTRATION_V2.md)
and [configuration](configs/paired_confidence_transfer_v2.yaml) specify the
controls, hashes, and decision rules. V2 performs no steering or model training.

## Reproduction and evidence

- [Current project status](STATUS.md) — current result, next gate, and limits
- [Transfer v2 preregistration](CONFIDENCE_TRANSFER_PREREGISTRATION_V2.md) and [results](CONFIDENCE_TRANSFER_RESULTS_V2.md) — frozen design and execution state
- [Paired pilot v1 execution](PAIRED_CONFIDENCE_README.md), [preregistration](PAIRED_CONFIDENCE_PREREGISTRATION_V1.md), and [results](PAIRED_CONFIDENCE_RESULTS_V1.md) — completed construct pilot
- [Stage 0/0B results](RESULTS_STAGE0.md) and [technical runbook](README_STAGE0.md) — historical semantic-uncertainty evidence and reproduction
- [Aggregate artifact index](results/README.md) — checked-in evidence; resumable inference caches and model weights are excluded from Git
- [Documentation index](docs/README.md) — upstream provenance and historical plans

The preserved upstream snapshot is pinned to commit
`02e2167dd1c00e27080d421f9b40e13e00f0452b`, and its MIT license is retained.
