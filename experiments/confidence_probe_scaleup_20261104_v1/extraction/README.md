# Activation extraction preparation

Status: complete V3 cache-only rematerialization and validation. The original
extraction produced exactly 2,538 authenticated main-response caches once.
V3 reuses those caches and the 226 frozen CF3 caches; it cannot load or forward
the model. No probe fit is authorized by this directory.

Every invocation must use the exact pinned environment (Python 3.11.14,
PyTorch 2.14.0, Transformers 4.57.6, MPS float16), not the system Python:

```bash
/Users/jwy/Library/CloudStorage/OneDrive-Personal/文档/New\ project/semantic-entropy-probes-stage0/.venv/bin/python \
  /Users/jwy/Library/CloudStorage/OneDrive-Personal/文档/New\ project/semantic-entropy-probes-diverse-pairs/experiments/confidence_probe_scaleup_20261104_v1/extraction/build_activation_bundles.py \
  --mode preflight
```

The builder reconstructs and verifies the complete feature fingerprint before
the language model can load. It also authenticates the final runner
`12e94409...` and preregistration `48accc06...`.

The builder is bound to split freeze
`84391340c85ced2863d8b2c4181a12c724ba96a138afb488de8bf5f6444733ea`
and the existing local-only Qwen feature identity
`636f0513795e9ed72f0c0b65f50d91e614bfb2c624d9e20ec13dd169146d5138`.
The original extraction required exactly 2,538 teacher-forced response
forwards for the 920/156/193 main splits. Its per-response cache is resumable.
The 226 CF3 responses are authenticated and reused from their frozen cache
with no new forward.

Every consolidated bundle binds:

- exact pair ID and pair-content hash;
- response axis `[confident, hesitant]`;
- exact per-response content hashes;
- per-response state-to-text binding hashes;
- layers 1–28, response-mean pooling, hidden size 1536, model revision, and
  frozen feature settings.

`--mode preflight` tokenizes locally but performs no model forward.
`--mode cf3-only` reuses existing caches and performs no model forward.
In this final V3 builder, `--mode main` also authenticates and reuses all 2,538
existing response caches and has no model-loading path.

Bundle and audit publication is atomic and resumable. A rerun verifies and
reuses byte-identical deterministic bundles/audits; it never overwrites a
different partial artifact.

## V1 serialization failure and V2 replacement

The first completed extraction successfully produced all 2,538 authenticated
response caches, but its deterministic bundle writer promoted scalar metadata
from shape `()` to `(1,)`. The final runner correctly rejected those bundles.
The original `bundles/` and `audits/` files remain immutable and are recorded
in `V1_BUNDLE_SERIALIZATION_FAILURE.json`.

The repaired writer preserves scalar shapes and publishes only to new
`bundles_v2/` and `audits_v2/` paths. Re-running `--mode main` must reuse all
2,538 authenticated caches (`0` new forwards, `2,538` cache hits); no model
forward is repeated to repair serialization. The v2 main path has no model
loading or forward code: it directly authenticates all expected cache keys,
token IDs, response masks, layer IDs, pooling positions, and feature hashes.
Each v2 bundle is also compared to its preserved v1 counterpart: every
non-scalar array must be exactly equal, while scalar values must be equal with
only the shape corrected from `(1,)` to `()`.

OneDrive normalizes private files on this workspace to mode `0700`. Resume
verification therefore accepts either `0600` or owner-only `0700`, while
rejecting every group/other permission bit.

The v2 main bundles correctly repaired scalar shapes, but the then-exact-0600
resume check stopped CF3 publication after OneDrive normalized permissions.
Those partial v2 artifacts remain immutable and are recorded in
`V2_PARTIAL_LIFECYCLE_RECORD.json`. The complete final cache-only publication
uses `bundles_v3/` and `audits_v3/`; each file records the exact final builder
source hash. This avoids pointing final artifacts at an unavailable earlier
source revision.

## Frozen V3 implementation and resume evidence

`build_activation_bundles_v3_frozen.py` is the immutable bundle-producing
implementation, SHA-256
`6b6e0642529baf3306031c70b1a06077aee6c61decafe71a70eaa43fb87c4757`.
`build_activation_bundles.py` is a small lifecycle wrapper: it authenticates
that frozen source, preserves its exact bundle bytes, and permits an existing
audit to differ only in transient `lifecycle`/`audit_lifecycle` labels. Any
scientific-field difference remains a hard failure.

The provider-free regression suite passes 17/17, including rejection of a
tampered frozen module before any top-level side effect. A real target-directory
resume completed with 0 new forwards, 2,538 main cache hits, 0 model loads,
and 226/226 CF3 cache reuses. All four bundles and both audits retained their
pre-resume hashes. The frozen runner's second `--validate-only` record is
byte-identical to the first, SHA-256
`033a771af16c6264363b5f2430ab616b388bf6c5ca6e7c8b7f4018fb7a4908ee`.
