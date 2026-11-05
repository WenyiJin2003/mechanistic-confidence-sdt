# Probe-guided LoRA lambda canary: provider-free data preparation

## Completed experiment status

The six-arm engineering canary and its primary blinded behavioral evaluation
are complete. All six training arms and all six evaluation arms finished with
zero missing or excluded evaluation rows. The frozen L14 auxiliary objective
produced a strong monotonic increase in the internal confident-minus-hesitant
gap, but the independent behavioral endpoint did not reach the preregistered
selection threshold.

- L14 gap across all 159 questions: `0.530` at ratio 0, `1.236` at ratio
  0.05, and `1.654` at ratio 0.10.
- Claude Opus 5.5 medium blind-judge directional credit on DEV113: `0.540`,
  `0.549`, and `0.580`, respectively.
- Improvement over ratio 0 on DEV113: `+0.009` for ratio 0.05 and `+0.040`
  for ratio 0.10; both paired bootstrap intervals include zero.
- Behavior46 improvements: `0.000` and `+0.011`.
- Frozen decision: `NO_LAMBDA_SELECTION` because neither positive ratio met
  the required `+0.05` DEV behavioral improvement.

The supported conclusion is therefore narrower than behavioral success: the
objective reliably controls the targeted internal readout, but this canary did
not establish reliable transfer to visibly expressed confidence in free
generation. See `RESULTS_AND_NEXT_STEP.md` and
`outputs/lambda_canary_20261104_run01/judgments/PRIMARY_BLIND_JUDGE_ANALYSIS.json`.

This directory materializes only the data inputs for a small engineering
canary. It does not run a model, tokenizer, forward pass, provider request,
LoRA training job, or evaluator.

The frozen roles are:

- `data/lora_train_cf200_156.jsonl`: 156 paired CF200 rows for LoRA training.
- `data/lora_dev_cf3_113.jsonl`: 113 paired CF3 rows for lambda and stability checks.
- `data/behavior_canary_cue50_46.jsonl`: 46 post-exposure Cue50 questions for
  behavioral inspection, after excluding C002, C018, C021, and C026 because
  their normalized questions overlap a frozen probe collection.

All outputs preserve source identity, normalized question identity, both
confidence-role responses, task, length direction/bin when available, and
source provenance. Every row and the manifest explicitly state that this is a
post-exposure engineering canary, not a confirmatory test.

Run the provider-free builder and tests with:

```bash
python3 build_canary_data.py
python3 -m unittest -v test_canary_data.py
```

## Isolated six-condition trainer

The implementation under `src/` leaves all historical experiments and data
preparation artifacts unchanged. It runs the Cartesian product of target role
(`confident`, `hesitant`) and auxiliary/CE gradient-ratio target
(`0`, `0.05`, `0.10`).

All six conditions use the same Qwen2.5-1.5B-Instruct revision, LoRA q/k/v/o
recipe, optimizer, row order, completion-only masks, and training loop. Before
calibration or updating, every arm computes the disabled-adapter L14 score for
each teacher-forced training answer once in eval mode, detaches it, and reuses
that fixed reference. The positive-ratio objective is:

`CE + lambda * mean(relu(0.5 - role_sign * (z_adapter - stopgrad(z_base)))^2)`

Ratio-zero controls execute the same centered forward path but use exactly
`lambda = 0`. The frozen probe is the SHA-pinned 920-pair artifact, selecting
the unique entry where `layer_ids == 14`. The launcher reads only the prepared
156-row training set plus the 113-row dev and 46-row behavioral files for
source-disjointness checks; it never reads the reserved internal test file.

Provider-free checks:

```bash
/Library/Frameworks/Python.framework/Versions/3.13/bin/python3 \
  -m unittest discover -s tests -v
bash -n slurm/train_lambda_array.sbatch
```

The six GPU jobs are defined, but not launched, by
`slurm/train_lambda_array.sbatch`. A fresh `OUTPUT_ROOT` and the existing
pinned LoRA environment must be supplied explicitly at submission time.
`config/SIX_RUN_MATRIX.json` freezes the task-to-arm mapping. After all array
tasks succeed, `slurm/validate_six_runs.sbatch` can be submitted with an
`afterok` dependency to verify all six output lifecycles and matched run pins,
then emit the exact runtime manifest consumed by `evaluate_adapters.py`.
`slurm/evaluate_lambda_array.sbatch` evaluates the six arms in parallel on the
frozen dev and behavior-canary files, and `slurm/aggregate_canary.sbatch`
creates the randomized blind-judge packet after all six evaluations complete.
None of these steps reads the reserved internal test; the blind judge itself
remains a separate, explicitly authorized phase.
