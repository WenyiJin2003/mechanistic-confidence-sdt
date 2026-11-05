# Confidence-probe scale-up runner preparation

Status: **implementation prepared; no real Qwen forward, probe fit, or score
has been executed by this phase**.

This directory contains a cache-only learning-curve runner for the separately
frozen collection-isolated split: 920 C1000 train, 156 CF200 dev, 193 CF2
internal test, and 113 CF3 external-robustness pairs. It implements
one source-paired logistic readout for every Qwen layer, nested training
prefixes 200/500/920, layerwise results, raw-hidden-space direction stability,
and the preregistered equal-28 ensemble.

## Scientific contract

- Train order and the 920-pair maximum are frozen by `SPLIT_FREEZE.json`; the
  first 200 and first 500 are strict prefixes of 920.
- No `id`, `source_id`, construction `group_id`, normalized exact question, or
  available lineage hash may cross train, dev, internal test, or external CF3.
- Each layer uses the existing method exactly: training-only `StandardScaler`,
  confident-minus-hesitant delta, symmetric `+d/-d` logistic rows, `C=0.01`,
  no intercept, fixed confident-positive orientation.
- Layer 14 remains the primary single layer. All 28 layers are reported; no
  best layer is selected from dev, test, or CF3.
- The primary multilayer result is the already-established equal-28 rule:
  standardize each layer's response score using training responses only, then
  average all 28 with fixed weight 1/28. There are no learned ensemble weights.
- The main interval conditions on the frozen item/source-lineage `group_id`.
  A separate bootstrap using the split freeze's `atomic_group_id` is reported
  only as a descriptive provider-batch sensitivity because dev/test contain
  few batches. This preserves the actual C1000 lane cooldown chains, CF200
  documents, CF2 canary/scale shards, and CF3 shards rather than reconstructing
  groups from ambiguous lane/document numbers.
- CF3 is robustness evidence, not fresh confirmation, because frozen probe and
  baseline scores have already been exposed on it.

The exact frozen choices are in `PREREGISTRATION.json`.

## Activation input contract

The statistical runner never loads Qwen. Each split needs one consolidated NPZ
with these keys:

- `pair_ids`: Unicode array `[N]`, exactly the JSONL `id` inventory (arbitrary
  physical order is allowed; the runner reorders and checks exact equality).
- `pair_content_sha256`: Unicode array `[N]`, binding each ID to the exact
  `source_id`, question, confident response, and hesitant response using the
  runner's canonical `pair_content_sha256` function.
- `pair_order`: exactly `['confident', 'hesitant']`.
- `response_content_sha256`: Unicode array `[N, 2]`, binding each response-axis
  entry to its role and exact text.
- `state_binding_sha256`: Unicode array `[N, 2]`, binding each pooled state
  tensor's bytes to the corresponding response-content hash. This makes an
  accidental confident/hesitant state swap fail closed.
- `states`: finite float array `[N, 2, 28, 1536]`, where response axis 0 is
  confident and axis 1 hesitant.
- `layer_ids`: integers 1 through 28.
- scalar `position`: `response_mean`.
- scalar `settings_sha256`:
  `636f0513795e9ed72f0c0b65f50d91e614bfb2c624d9e20ec13dd169146d5138`.
- scalar `model_id`: `Qwen/Qwen2.5-1.5B-Instruct`.
- scalar `model_revision`:
  `989aa7980e4cf806f80c7fef2b1adb7bc71aa306`.

The future extraction stage should use the frozen Qwen formatter and cache
implementation already used for Cue50 and CF3. It needs 2,538 new
teacher-forced forwards for the 1,269 main-split pairs. CF3 already has all 240
response caches, so the strict 113-row subset should require zero new CF3
forwards after exact ID/hash authentication. See
`CACHE_AND_ENVIRONMENT_AUDIT.json`.

The runner accepts only the exact split freeze with SHA-256
`84391340c85ced2863d8b2c4181a12c724ba96a138afb488de8bf5f6444733ea`.

## Execution environment

Use the existing environment:

```bash
../semantic-entropy-probes-stage0/.venv/bin/python
```

It currently provides Python 3.11.14, NumPy 2.4.6, scikit-learn 1.9.1,
PyTorch 2.14.0, and Transformers 4.57.6. GPU/CUDA is preferred only for the
future teacher-forced extraction. The cache-only readouts are CPU work.

After a separate extraction and authority freeze, a validation-only invocation
is:

```bash
../semantic-entropy-probes-stage0/.venv/bin/python \
  experiments/confidence_probe_scaleup_20261104_v1/runner_prep/run_probe_learning_curve.py \
  --split-freeze experiments/confidence_probe_scaleup_20261104_v1/data_prep/SPLIT_FREEZE.json \
  --train-data experiments/confidence_probe_scaleup_20261104_v1/data_prep/train_920.jsonl \
  --dev-data experiments/confidence_probe_scaleup_20261104_v1/data_prep/dev_156.jsonl \
  --internal-test-data experiments/confidence_probe_scaleup_20261104_v1/data_prep/internal_test_193.jsonl \
  --external-cf3-data experiments/confidence_probe_scaleup_20261104_v1/data_prep/external_cf3_113.jsonl \
  --train-activations /frozen/path/train_920_activations.npz \
  --dev-activations /frozen/path/dev_156_activations.npz \
  --internal-test-activations /frozen/path/internal_test_193_activations.npz \
  --external-cf3-activations /frozen/path/external_cf3_113_activations.npz \
  --output-dir /new/empty/output/directory \
  --validate-only
```

Remove `--validate-only` only after the complete input and execution bridge is
frozen. The runner refuses overwrites.

## Provider-free tests

The tests use only synthetic hidden states and temporary files. They cover the
exact logistic/equal-28 formulas, zero-score-variance behavior, split-manifest
tampering, NFKC question leakage, activation text binding, and response-axis
swaps:

```bash
cd experiments/confidence_probe_scaleup_20261104_v1/runner_prep
/Users/jwy/Library/CloudStorage/OneDrive-Personal/文档/New\ project/semantic-entropy-probes-stage0/.venv/bin/python -m unittest -v \
  test_run_probe_learning_curve.py
```
