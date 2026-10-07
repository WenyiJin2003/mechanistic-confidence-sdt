# Code and reproduction

This is the code entry point. Questions and answers are under
[datasets/](../datasets/README.md); findings are under [reports/](../reports/README.md).

| Experiment | Implementation | Run entry point | Configuration / instructions |
|---|---|---|---|
| Stage 0: prompt-state semantic uncertainty | [stage0/pipeline.py](../stage0/pipeline.py), [stability](../stage0/stability.py), [label sampling](../stage0/label_stability.py), [direction audit](../stage0/direction_stability.py) | [run_stage0.py](../scripts/run_stage0.py) | [Stage 0 runbook](../docs/experiments/README_STAGE0.md), [configs](../configs/) |
| Stage 0B: answer-state semantic uncertainty | [stage0/answer_state.py](../stage0/answer_state.py) | [run_answer_state_probe.py](../scripts/run_answer_state_probe.py) | [Stage 0B configuration](../configs/stage0b_qwen15b_answer_state.yaml) |
| Paired Confidence v1 | [data construction](../confidence_pilot/data_validation.py), [state extraction](../confidence_pilot/extract_activations.py), [paired readout](../confidence_pilot/analyze_pairs.py) | [run_paired_confidence_pilot.py](../scripts/run_paired_confidence_pilot.py) | [V1 runbook](../docs/experiments/PAIRED_CONFIDENCE_README.md), [main-phase config](../configs/paired_confidence_phase_b.yaml) |
| Frozen Transfer v2 | [test data](../confidence_pilot/transfer_data_v2.py), [frozen controls](../confidence_pilot/transfer_run_v2.py), [transfer metrics](../confidence_pilot/transfer_analysis_v2.py) | [run_confidence_transfer_v2.py](../scripts/run_confidence_transfer_v2.py) | [V2 runbook](../docs/experiments/CONFIDENCE_TRANSFER_README_V2.md), [V2 config](../configs/paired_confidence_transfer_v2.yaml) |
| Readable data export | [export_question_sets.py](../scripts/export_question_sets.py) | The same script | [Question collections](../datasets/README.md) |

The research modules remain in their established package directories so imports,
commands and recorded artifact paths stay compatible. `scripts/` contains
entry points, `configs/` contains settings, and [tests/](../tests/) contains
verification code. No dataset is embedded in a source module.

The preserved upstream implementation is in
[semantic_entropy_probes/](../semantic_entropy_probes/) and
[semantic_uncertainty/](../semantic_uncertainty/). Its
[original README](../docs/UPSTREAM_README.md) and [license](../LICENSE) remain
available for provenance.

Model weights and per-input inference caches are local and excluded from Git.
Saved aggregate artifacts allow inspection of completed results without running
either model. Exporting readable data uses the existing files only.
