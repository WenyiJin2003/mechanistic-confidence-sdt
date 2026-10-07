# Measurement Studies Before an Internal SDT Loss

**A frozen readout distinguishes new certainty wording and responds to supplied
evidence, but its evidence sensitivity varies by fact type. It has not been
validated as a training objective.**

Frozen Transfer v2 ordered 87/96 wording pairs (90.6%) and 35/48 identical-answer
evidence pairs (72.9%). Release-year evidence scored 4/12, failing the registered
robustness check. Content-token candidates are promising secondary findings.
Read the [full result](reports/CONFIDENCE_TRANSFER_RESULTS_V2.md) for controls,
failures and the limits of these conclusions.

The research goal is ordinary synthetic-document training (SDT) with a possible
auxiliary loss based on a model's internal confidence signal. No SDT or auxiliary
loss training has been performed in these experiments.

## Browse the questions and answers

**[Open the complete question-and-answer collections](datasets/README.md).**
These are ordinary GitHub pages: read the question, context, answer versions,
labels and saved scores directly, without opening JSON or running code.

| Collection | What you can inspect | Open |
|---|---|---|
| Paired Confidence v1 | 120 source questions and all 1,440 authored confident/hedged responses, grouped by domain and rewrite family | [Questions, answers and scores](datasets/paired-confidence-v1/README.md) |
| Frozen Transfer v2 | 48 fictional sources and all 480 authored responses, including supported/omitted/conflicting contexts and failures | [Questions, answers and scores](datasets/frozen-transfer-v2/README.md) |
| Stage 0 / 0B | Saved SQuAD questions, reference answers, actual Qwen samples and semantic-entropy labels across runs | [Sampled-answer collections](datasets/stage0/README.md) |

V1 and v2 responses were written as controlled inputs for Qwen to read. Stage 0
responses were sampled from Qwen. A probe score is a raw internal readout, not a
probability or a factual-accuracy score.

## Experiments

| Name | State used | Target | Report |
|---|---|---|---|
| Stage 0 — Prompt-State Semantic-Uncertainty Probe | Final rendered prompt token, before answering | Semantic entropy of sampled answers | [Stage 0 / 0B](reports/RESULTS_STAGE0.md#outcome) |
| Stage 0B — Answer-State Semantic-Uncertainty Diagnostic | Last ordinary token of one observed answer | Semantic entropy of nine alternative answers | [Stage 0B](reports/RESULTS_STAGE0.md#stage-0b--post-answer-hidden-state-diagnostic) |
| Paired Confidence v1 — Answer-End Expressed-Certainty Readout | Assistant `<\|im_end\|>` after the full response | Confident versus hedged wording | [V1](reports/PAIRED_CONFIDENCE_RESULTS_V1.md) |
| Frozen Transfer v2 — Expressed-Certainty Evidence-Transfer Test | Same response-end state and frozen v1 direction | New wording and supplied evidence | [V2](reports/CONFIDENCE_TRANSFER_RESULTS_V2.md) |

Only v1 → v2 reuses the same fitted direction. The
[experiment map](docs/experiments/EXPERIMENT_MAP.md) explains the data and
equations; [project status](docs/experiments/STATUS.md) gives the current decision.

## Repository layout

| Folder | Purpose |
|---|---|
| [datasets/](datasets/README.md) | Readable questions, answers and CSV downloads |
| [data/](data/README.md) | Exact machine-readable source inputs and data audits |
| [reports/](reports/README.md) | Research findings and interpretation |
| [code/](code/README.md) | Code map and entry points for reproducing each experiment |
| [docs/](docs/README.md) | Methods, execution instructions and provenance |
| [results/](results/README.md) | Saved numerical outputs, states, readouts and manifests |
| [plots/](plots/) | Research figures |
| [configs/](configs/) | Experiment settings |

The code map points to `stage0/`, `confidence_pilot/` and `scripts/`. Their paths
are retained so existing commands and cached-artifact checks remain valid.
The two root preregistrations retain their original content and published paths.

This work adapts Kossen et al.'s [*Semantic Entropy Probes*](https://arxiv.org/abs/2406.15927)
and [official OATML code](https://github.com/OATML/semantic-entropy-probes).
The upstream snapshot and MIT license are preserved; the small-model experiments
and paired-response studies are not a full paper replication.
