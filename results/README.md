# Result Index

Each completed directory contains checked-in aggregate artifacts. Large model
weights and resumable inference caches are excluded from Git. Narrative reports
interpret the evidence; this page indexes the saved artifacts.

## Expressed certainty and frozen transfer

| Directory | Scope | Primary evidence |
|---|---|---|
| [paired_confidence_phase_a/](paired_confidence_phase_a/) | V1 engineering pilot: 24 sources, 192 responses | [pair_metrics.json](paired_confidence_phase_a/pair_metrics.json), [manifest.json](paired_confidence_phase_a/manifest.json) |
| [paired_confidence_phase_b/](paired_confidence_phase_b/) | V1 construct pilot: 120 sources, 1,440 responses | [pair_metrics.json](paired_confidence_phase_b/pair_metrics.json), [readout_directions.npz](paired_confidence_phase_b/readout_directions.npz), [manifest.json](paired_confidence_phase_b/manifest.json) |

The completed [v1 report](../PAIRED_CONFIDENCE_RESULTS_V1.md) is the canonical
interpretation of these artifacts. Transfer v2 will write to
`paired_confidence_transfer_v2/`; it currently has no evaluated outcomes. See its
[preregistration](../CONFIDENCE_TRANSFER_PREREGISTRATION_V2.md) and
[results page](../CONFIDENCE_TRANSFER_RESULTS_V2.md).

## Historical semantic-uncertainty experiments

| Directory | Model / scale | Purpose | Primary file |
|---|---|---|---|
| `preflight/` | Qwen 0.5B, 5 questions | Device and generation check | `manifest.json` |
| `run_a/` | Qwen 0.5B, 12 questions | Smoke test | `manifest.json` |
| `run_b/` | Qwen 0.5B, 64 questions | Initial NLI pilot | `probe_metrics.json` |
| `run_200/` | Qwen 0.5B, 200 questions | Fixed-split follow-up | `probe_metrics.json` |
| `run_200_qwen15b/` | Qwen 1.5B, 200 questions | Matched model comparison | `probe_metrics.json` |
| `run_200_qwen15b_split_stability/` | Cached 1.5B data | Repeated-split and cross-fit audit | `stability_metrics.json` |
| `run_50_qwen15b_label_stability/` | Qwen 1.5B, 50 questions | 5/10/20-sample label reliability | `label_stability_metrics.json` |
| `run_500_qwen15b_confirm/` | Qwen 1.5B, 500 fresh questions | Preregistered confirmation | `probe_metrics.json` |
| `run_500_qwen15b_direction_stability/` | Cached 1.5B development data | Nested direction stability and corrected stacking | `direction_stability_metrics.json` |
| `run_500_qwen15b_answer_state/` | Cached Qwen 1.5B data, 500 questions | Stage 0B post-answer, same-information diagnostic | `answer_state_probe_metrics.json` |

The canonical historical report is [Stage 0/0B results](../RESULTS_STAGE0.md).
Figures are under [plots/](../plots/). [Project status](../STATUS.md) and the
[root README](../README.md) identify the current decision and research sequence.
