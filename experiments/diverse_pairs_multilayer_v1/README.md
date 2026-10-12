# Diverse paired certainty and multi-layer readouts

**Current status: 50 paired drafts are ready for individual review; the
all-layer extraction pipeline passes a bounded 20-pair engineering check.
There is no new probe-performance result yet.**

This stage returns to the main research question: can diverse, content-preserving
confident/hedged responses reveal a transferable certainty-related readout, and
does a simple 28-layer ensemble improve on layer 14?

## What is ready

- 50 real-source responses, each with confident and hedged edits: 38 WildChat,
  12 HelpSteer2, covering five task categories. GPT-6 Luna performed the edits;
  the original answers were not regenerated. All are development data, never
  final-test sources.
- An interactive local review page. The stronger hesitant revision preserves
  confident text; the first packet is archived. Automatic checks passed except
  three retained source-content warnings. Individual human review is pending.
- A separate frozen-Qwen extractor: response mean, last ordinary response token,
  and last prompt token from all 28 layers; same-response NLL and resumable caches.
- CPU paired-logistic, equal-score ensemble and mean-difference modules, plus
  source-group bootstrap utilities tested on synthetic data.

The engineering check confirms finite states, exact response spans, identical
prompt controls, padding invariance and an exact cache-only replay without
model inference. These checks establish pipeline behavior, not generalization,
subjective confidence, correctness independence or usefulness as an SDT loss.

## Where to look

| Material | Location |
|---|---|
| Research definition and fixed method choices | [PROTOCOL.md](PROTOCOL.md) |
| Current progress and next action | [STATUS.md](STATUS.md) |
| Rewriter contract / resource record | [REWRITE_SPEC.md](REWRITE_SPEC.md) / [REWRITE_BUDGET.md](REWRITE_BUDGET.md) |
| Pinned source identities, coverage and draft checks | [manifests/](manifests/) |
| All-layer configuration | [configs/diverse_pairs_multilayer_v1.yaml](configs/diverse_pairs_multilayer_v1.yaml) |
| Engineering results, not probe scores | [results/EXTRACTION_SANITY.json](results/EXTRACTION_SANITY.json) |
| Extraction, readouts and review importer | [src/](src/) |
| Regression and synthetic-data checks | [tests/](tests/) |
| Original/rewritten text and actual annotations | `private_data/`, local and ignored |
| Token IDs and pooled hidden states | `cache/`, local and ignored |

Third-party text is not republished until licensing and privacy review. Source
IDs and hashes are available; the current local packet is not downloadable from
GitHub. Historical experiments and failed diagnostics remain unchanged elsewhere
in the repository.

## Next step

Complete the 50-pair content audit, then decide whether to expand the rewrite
protocol under a separate budget. Final source groups, unseen rewrite instructions
and evaluation controls must be frozen before scientific scoring. Out-of-fold
stacking, the main 2×2 evaluation runner and learning curves remain planned.
No automatic language-model training or activation steering is authorized.

## Run the engineering check

Use the existing project environment and already cached pinned Qwen snapshot.
Paths and limits are in the YAML; there are no model downloads or inference APIs.

```sh
python experiments/diverse_pairs_multilayer_v1/src/run_preflight.py --pairs 20
python -m pytest tests experiments/diverse_pairs_multilayer_v1/tests -q
```

The command needs the local development packet. A successful prior run supplies
cached response states; the explicit padding diagnostic still makes one forward.
Pure cache-only replay is exercised separately and requires zero model forwards.
The benchmark is not the main layer-14 versus ensemble experiment.
