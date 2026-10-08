# Code and reproduction

This is the code entry point. Questions and answers are under
[datasets/](../datasets/README.md); findings are under [reports/](../reports/README.md).

| Step | Experiment | Implementation | Run entry point | Configuration / instructions |
|---:|---|---|---|---|
| 1 | Stage 0: prompt-state semantic uncertainty | [pipeline](../stage0/pipeline.py), [stability](../stage0/stability.py), [label sampling](../stage0/label_stability.py), [direction audit](../stage0/direction_stability.py) | [run_stage0.py](../scripts/run_stage0.py) | [Runbook](../docs/experiments/README_STAGE0.md), [configs](../configs/) |
| 2 | Stage 0B: answer-state semantic uncertainty | [answer_state.py](../stage0/answer_state.py) | [run_answer_state_probe.py](../scripts/run_answer_state_probe.py) | [Configuration](../configs/stage0b_qwen15b_answer_state.yaml) |
| 3 | Paired Confidence v1 | [data](../confidence_pilot/data_validation.py), [extraction](../confidence_pilot/extract_activations.py), [analysis](../confidence_pilot/analyze_pairs.py) | [run_paired_confidence_pilot.py](../scripts/run_paired_confidence_pilot.py) | [Runbook](../docs/experiments/PAIRED_CONFIDENCE_README.md), [config](../configs/paired_confidence_phase_b.yaml) |
| 4 | Frozen Transfer v2 | [data](../confidence_pilot/transfer_data_v2.py), [run](../confidence_pilot/transfer_run_v2.py), [analysis](../confidence_pilot/transfer_analysis_v2.py) | [run_confidence_transfer_v2.py](../scripts/run_confidence_transfer_v2.py) | [Runbook](../docs/experiments/CONFIDENCE_TRANSFER_README_V2.md), [config](../configs/paired_confidence_transfer_v2.yaml) |
| 5 | Confidence–Correctness Separation v3 | [data](../confidence_pilot/separation_data_v3.py), [run and analysis](../confidence_pilot/separation_run_v3.py) | [run_confidence_separation_v3.py](../scripts/run_confidence_separation_v3.py) | [Config](../configs/confidence_separation_v3.yaml), [registered design](../docs/experiments/CONFIDENCE_SEPARATION_V3_PREREGISTRATION.md) |
| 6 | Evidence-Sensitive Readout v4 | [data](../confidence_pilot/evidence_data_v4.py), [analysis](../confidence_pilot/evidence_analysis_v4.py), [behavior](../confidence_pilot/evidence_behavior_v4.py) | [run_evidence_confidence_v4.py](../scripts/run_evidence_confidence_v4.py) | [Config](../configs/evidence_confidence_v4.yaml), [runbook](../docs/experiments/EVIDENCE_CONFIDENCE_README_V4.md), [design](../docs/experiments/EVIDENCE_CONFIDENCE_V4_PREREGISTRATION.md) |
| Verification | Independent v4 artifact audit | [audit_evidence_confidence_v4.py](../scripts/audit_evidence_confidence_v4.py) | The same script; no model calls | [58-check result](../results/evidence_confidence_v4/independent_audit.json) |
| Reproduction | Public cached v4 arithmetic | [reproduce_evidence_metrics_v4.py](../scripts/reproduce_evidence_metrics_v4.py) | The same script; no model weights required | [Runbook](../docs/experiments/EVIDENCE_CONFIDENCE_README_V4.md) |
| Supplement | Confidence/correctness cached audit | [analysis](../confidence_pilot/separation_audit.py) | [run_separation_audit.py](../scripts/run_separation_audit.py) | [Config](../configs/confidence_correctness_audit.yaml), [results](../reports/CONFIDENCE_CORRECTNESS_AUDIT.md) |
| Utility | Readable data export | [export_question_sets.py](../scripts/export_question_sets.py) | The same script | [Question collections](../datasets/README.md) |

The research modules remain in their established package directories so imports,
commands and recorded artifact paths stay compatible. `scripts/` contains
entry points, `configs/` contains settings, and [tests/](../tests/) contains
verification code. Exact authored inputs and their scoreless audits are saved
under [data/](../data/README.md).

The preserved upstream implementation is in
[semantic_entropy_probes/](../semantic_entropy_probes/) and
[semantic_uncertainty/](../semantic_uncertainty/). Its
[original README](../docs/UPSTREAM_README.md) and [license](../LICENSE) remain
available for provenance.

Model weights and per-input inference caches are local and excluded from Git.
Saved aggregate artifacts allow inspection of completed results without running
either model. Exporting readable data uses the existing files only.
