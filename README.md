# Measurement Studies Before an Internal SDT Loss

**We can read expressed certainty from Qwen's internal states. We have not yet
validated a readout of confidence in whether a particular answer is supported.**

On 48 fresh counterfactual records, the two frozen response-content candidates
ordered all 192 confident/hedged pairs correctly. With the answer text held
identical while its contextual correctness changed, their ordering rates were
52.1% and 51.0%, near chance. Both failed the registered confirmation checks.
The [new result](reports/CONFIDENCE_SEPARATION_RESULTS_V3.md) distinguishes
wording, contextual correctness, and availability of evidence.

For the response mean, relevant-context scores rise at almost the same rate
when the written answer is supported or contradicted (81.3% versus 80.2%). This
is compatible with context availability, rather than confidence in that answer;
the comparison is explicitly post-hoc.

**Geometric separation is also insufficient.** An almost perpendicular pair of
confidence/correctness contrasts can still recognize the same certainty wording.
The [cached audit](reports/CONFIDENCE_CORRECTNESS_AUDIT.md) checks the comparators,
direction stability and projection effects rather than treating a cosine as
proof of independent mechanisms.

The research goal is ordinary synthetic-document training (SDT) with an auxiliary
term that strengthens commitment to its target facts. A small controlled training
trial can test a candidate regularizer, but success must be judged by use of the
learned facts and generalization, not just an increased probe score. No SDT or
auxiliary-loss training has been performed here.

## Browse the questions and answers

**[Open the complete question-and-answer collections](datasets/README.md).**
These are ordinary GitHub pages: read the question, context, answer versions,
labels and saved scores directly, without opening JSON or running code.

| Collection | What you can inspect | Open |
|---|---|---|
| Paired Confidence v1 | 120 source questions and all 1,440 authored confident/hedged responses, grouped by domain and rewrite family | [Questions, answers and scores](datasets/paired-confidence-v1/README.md) |
| Frozen Transfer v2 | 48 fictional sources and all 480 authored responses, including supported/omitted/conflicting contexts and failures | [Questions, answers and scores](datasets/frozen-transfer-v2/README.md) |
| Confidence–Correctness Separation v3 | 48 fresh records and all 672 authored responses; identical answers across counterfactual worlds | [Questions, answers and scores](datasets/confidence-separation-v3/README.md) |
| Stage 0 / 0B | Saved SQuAD questions, reference answers, actual Qwen samples and semantic-entropy labels across runs | [Sampled-answer collections](datasets/stage0/README.md) |

V1–v3 responses were written as controlled inputs for Qwen to read. Stage 0
responses were sampled from Qwen. A probe score is a raw internal readout, not a
probability or a factual-accuracy score.

## Experiments

| Name | State used | Target | Report |
|---|---|---|---|
| Stage 0 — Prompt-State Semantic-Uncertainty Probe | Final rendered prompt token, before answering | Semantic entropy of sampled answers | [Stage 0 / 0B](reports/RESULTS_STAGE0.md#outcome) |
| Stage 0B — Answer-State Semantic-Uncertainty Diagnostic | Last ordinary token of one observed answer | Semantic entropy of nine alternative answers | [Stage 0B](reports/RESULTS_STAGE0.md#stage-0b--post-answer-hidden-state-diagnostic) |
| Paired Confidence v1 — Answer-End Expressed-Certainty Readout | Assistant `<\|im_end\|>` after the full response | Confident versus hedged wording | [V1](reports/PAIRED_CONFIDENCE_RESULTS_V1.md) |
| Frozen Transfer v2 — Expressed-Certainty Evidence-Transfer Test | Same response-end state and frozen v1 direction | New wording and supplied evidence | [V2](reports/CONFIDENCE_TRANSFER_RESULTS_V2.md) |
| Confidence–Correctness Separation v3 | Frozen v1 final-response-token and response-mean readouts; end marker as reference | Same-answer contextual truth, evidence availability, and certainty wording | [V3](reports/CONFIDENCE_SEPARATION_RESULTS_V3.md) |

V2 and v3 reuse the separately fitted v1 directions at their original positions.
The cached geometry audit fits correctness comparators only on old v1 training
sources. The
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
