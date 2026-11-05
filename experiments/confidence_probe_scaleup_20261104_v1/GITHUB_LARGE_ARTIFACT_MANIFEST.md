# GitHub large-artifact manifest

The activation bundles listed below are local, regenerable caches. They are
not committed as ordinary Git blobs because three files exceed GitHub's
100 MB single-file limit and the complete redundant cache set is about 1.2 GB.
The extraction code, frozen input rows, audits, probe artifacts, metrics, and
all downstream canary adapters/evaluations are committed. These hashes bind
the local caches used by the recorded analyses.

| Bytes | SHA-256 | Local path |
|---:|---|---|
| 25,182,978 | `129e970b2d40b62cd615b2112f43ea986e761963c85b2346edcdab856f4bf115` | `extraction/bundles/dev_156_activations.npz` |
| 18,255,744 | `8ff9409396c0f3a2ffa6a958549f34ec28da4b2241cdee1376c2143018ae29ce` | `extraction/bundles/external_cf3_113_activations.npz` |
| 31,156,903 | `bd70975db26961f781fa0d309468dd7ddf562ff45e70b3802c9f466f1af50bb9` | `extraction/bundles/internal_test_193_activations.npz` |
| 148,498,138 | `41f85b8d7a88d61e02742a6f974bf8c6b4effb8af4028cd09fddcb428663f8d1` | `extraction/bundles/train_920_activations.npz` |
| 25,183,485 | `883d5ce0bfc4784b48f84486e428e29430f529f1bf35c7e912692ed16bf5fcae` | `extraction/bundles_v2/dev_156_activations.npz` |
| 31,157,410 | `11ee94ee6ee3ed27e1f2d06fedd3d448dad9dbd19e799f1c37297edbda80df4f` | `extraction/bundles_v2/internal_test_193_activations.npz` |
| 148,498,645 | `4b0fbca46316857df0a2e68300b44581f463022b02c91e41dd7f452e0989d20d` | `extraction/bundles_v2/train_920_activations.npz` |
| 25,183,502 | `167c173e27d7a587f5b1277cafd23e6eedf23a046e619dbfb8004a56559ff0c4` | `extraction/bundles_v3/dev_156_activations.npz` |
| 18,256,268 | `dc100ba63a6debe8fb7182b62e566a70bfea1dda7b39c60d59bc4e08e4f9ce09` | `extraction/bundles_v3/external_cf3_113_activations.npz` |
| 31,157,427 | `996b303f056457a6ab59c543d3c16e636c90a351a77a3d235ba8cd353537003f` | `extraction/bundles_v3/internal_test_193_activations.npz` |
| 148,498,662 | `cb1e4211ef02b2b1a833f116572d4c8fd6f94512e37179fd020dcea7d8a5beec` | `extraction/bundles_v3/train_920_activations.npz` |

The authoritative completed extraction is `bundles_v3`; earlier bundle
directories are preserved locally because the lifecycle records document the
V1 serialization failure and the V2 partial run. To recreate the authoritative
bundles, use `extraction/build_activation_bundles_v3_frozen.py` with the
environment and inputs pinned by `extraction/audits_v3/MAIN_EXTRACTION_AUDIT.json`.
