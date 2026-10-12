# Local resource assessment

Initial inspection, 11 October 2026: no representation-model forward or rewriting
had been performed at that point. Later pilot and preflight results are recorded
below and in STATUS.md; the initial inventory is retained for provenance.

## Workspace

- New branch: codex/diverse-pairs-multilayer-v1.
- New checkout: semantic-entropy-probes-diverse-pairs, alongside the two old trees.
- Base: public-project main commit 969255a8c05c3b7a0f2f34a79ed2f4fbc7edd053.
- Publication remote: stage0 -> WenyiJin2003/mechanistic-confidence-sdt.
  origin remains the OATML upstream and must not receive project changes.
- Both old worktrees were clean on inspection; neither was switched or reset.

## Reusable local resources

- Apple M3, 16 GiB RAM; approximately 192 GiB available disk at inspection.
- Existing semantic-entropy-probes-stage0/.venv: Python 3.11.14,
  torch 2.14.0, transformers 4.57.6, datasets 3.6.0, numpy 2.4.6,
  scikit-learn 1.9.1, pyarrow 25.0.1, huggingface-hub 0.36.2.
- MPS available; CUDA unavailable. Tiny MPS float32 and bfloat16 matrix operations
  returned finite values. This is not a full-model memory or throughput benchmark.
- Existing Qwen2.5-1.5B-Instruct snapshot:
  989aa7980e4cf806f80c7fef2b1adb7bc71aa306.
  Required model/config/tokenizer files exist; tokenizer loads locally.
  Weight file: 3,087,467,144 bytes. Configuration: 28 layers, width 1,536.
- Existing model/data cache approximately 5.4 GiB; environment approximately 1.1 GiB.
- Existing extraction code is tied to layers [14, 23], shape [2, 4, 1536], and a
  Question/Context wrapper. A separate new module must support all layers and
  natural source messages without changing historical extraction conventions.
- No WildChat/HelpSteer dataset or suitable natural rewrite assets found in the
  inspected project resources. Cached Qwen 0.5B/1.5B are not approved production
  rewriters. No new model download is necessary for representation extraction.
- FASRC login/job execution is unverified and is not a local preparation dependency.

## Source access precheck

Both original datasets' public first-row endpoints responded successfully;
actual schema parsing passed. Previews were inspected in memory only, with no
response bodies retained or printed. No bulk dataset download was performed.

| Dataset | Pinned proposed revision | Actual fields / provenance | Original size |
|---|---|---|---|
| allenai/WildChat-1M | 7d6490e462285cf85d91eabea0f9a954fbddcd1f | conversation_hash, model, conversation role/content/language/turn_identifier; contains metadata to omit | 837,989 train conversations; 14 parquet shards, about 3.36 GB compressed |
| nvidia/HelpSteer2 | 990b2711a36180dd19d9c94b8627844866f8982a | prompt, response, helpfulness, correctness, coherence, complexity, verbosity | 20,324 train / 1,038 validation rows; original train gzip about 11.3 MB |

The viewer preview is not revision-pinned; actual source acquisition must use
the pinned native files above. Official cards identify ODC-BY for WildChat and
CC-BY-4.0 for HelpSteer2. Text redistribution still requires a separate review.

Use bounded pinned shard streaming for WildChat; the full dataset is unnecessary.
HelpSteer2's original train file is small enough to inspect and sample locally.
Do not substitute its preference/disagreements subsets for confident/hedged pairs.
Conversation hashes may repeat; preserve turn provenance and group duplicates.
HelpSteer shared prompts and encoded multi-turn contexts require reconstruction.
Check exact and near duplicates across both sources before assigning splits.

## Outstanding resources

```yaml
rewrite_provider: null
rewrite_model: null
rewrite_model_revision: null
api_spend_cap: null
external_data_processing_approved: false
human_review: pending
```

No approved external API rewrite budget or independently human-reviewed rewrite
batch exists. On the user's subsequent authorization, a 50-pair pilot was
generated through current-session GPT-6 Luna workers. Source collection,
grouping, review tooling and extraction/readout code
can proceed. Formal rewriting and full dataset inference must wait for the
corresponding resource and quality conditions. No API credentials were inspected.
See REWRITE_BUDGET.md for the pilot route and observed account usage; larger-scale
rewriting remains subject to review and an expansion decision.

All-layer pooled FP16 states for 2,000 responses are approximately 164 MiB per
pooling position, or 328 MiB for response mean plus final content. This estimate
excludes model weights, token data, logits, peak memory and additional baselines.
Runtime cannot be extrapolated from the short v4 inputs; measure actual lengths.

## Immediate bounded precheck

Prepare source parsing, eligibility, duplicate grouping and provenance manifests;
then verify the separate all-layer extractor on a small engineering batch using
the local model. Measure natural-length inputs before deciding full-pass costs.
Target an initial run below 20–30 minutes and stop before an estimated full pass
above approximately two hours or sustained memory pressure without a decision.

## Executed engineering benchmark

The separate all-layer extractor has now read 20 development pairs (40 real
responses) on MPS in FP16. Input lengths span 94–729 tokens; response lengths
span 71–422. No new weights were downloaded and no responses were generated.
All 28 layers and three pooling/control positions were finite. Identical prompt
states and an extra-seven-token padding check had zero maximum difference.
A cache-only replay recovered all 40 arrays exactly with zero model forwards.

The initial benchmark, including loading, an additional padding forward and
cache replay, took 42.1 seconds. Process RSS high water was 2.28 GiB; maximum
observed MPS driver allocation was 4.17 GiB. These accounting measures overlap
and must not be added. The final implementation was revalidated after adding
a strict confident-first input-order guard; the initial summary and final full
aggregate are retained. The first run's per-forward timing table was not archived.
See results/EXTRACTION_SANITY.json and EXTRACTION_SANITY_INITIAL_SUMMARY.json.

At the measured throughput, an illustrative token-linear budget for 2,000
responses at current input-length quartiles is about 16–27 minutes. This is
not a confidence interval or an approved full run. It excludes source expansion,
rewriting, human review, template baselines and additional test views, and does
not establish throughput for arbitrary longer documents.
