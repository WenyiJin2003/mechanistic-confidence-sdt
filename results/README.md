# Result Index

Each directory contains checked-in aggregate artifacts. Large model weights and resumable inference caches are excluded from Git.

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

The canonical narrative report is [`../RESULTS_STAGE0.md`](../RESULTS_STAGE0.md). Figures are under [`../plots/`](../plots/).
