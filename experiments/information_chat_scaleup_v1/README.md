# Cached 5,000-candidate expressed-certainty diagnostic

This independent experiment reads an exact frozen prefix of 5,000 cached
UltraChat/Haiku triplets. It retains every original question, answer, rewrite,
audit flag and generation provenance. These are candidate writer labels, with
human item review pending and content preservation uncertified. The source
answers are synthetic and are not factual gold. No SDT objective, steering,
language-model training, new generation, download or account call occurs.

The fixed comparison is a newly fitted layer-14 paired logistic readout against
an equal average of all 28 train-standardized layer scores. Every layer is also
displayed. The settings match the earlier diverse-pairs diagnostic: C=0.01,
L2, mirrored pair differences weighted 0.5 each, no intercept, at most 2,000
iterations, response-token mean pooling, and 2,000 group-bootstrap draws.
Layer 28 follows final RMSNorm under the installed Transformers convention.

Before scores are exposed, the preparation command verifies the frozen packet,
manifest and all pinned source/provider files, then fixes a deterministic 80/20
split of independent groups. Groups combine source/group identity and exact
normalized question or original-answer duplicates, including transitive links.
Previously inspected canary sources and their duplicate derivatives stay in
training. Approximate duplicates are not detected. Feature scaling, layer-score
scaling and the character TF-IDF vocabulary are fitted on training responses
only. Test scores never select a layer, sign, hyperparameter or threshold.

Both written rewrites are teacher-forced through the pinned, local, unquantized
Qwen2.5-1.5B snapshot. The original answer is preserved but does not add a forward.
Each batch contains both variants of one or two source groups, ordered by length
for throughput, with right padding and explicit attention masks. Response means,
last response tokens and final prompt tokens are pooled in the same forward.
Prompt, padding and turn-marker tokens are excluded from response pooling and
shifted response NLL. Overlength text fails before any forward; it is never
silently truncated or removed.

The complete FP16 states occupy approximately 2.4 GiB on disk. Extraction writes
to memory-mapped arrays and commits each completed pair after flushing states
and NLL; interrupted runs recompute only uncommitted pairs. Fingerprints bind
the plan, weights, tokenizer, software, device, precision, batching and code.
Changing these settings rejects cache mixing. Fits read one layer at a time and
cap CPU thread pools at one to bound memory and avoid generation contention.
The run directory must be a named child of this experiment's ignored
`private_data/` directory; old caches and generation files are never written.

Secondary controls are character TF-IDF, fixed negative token/word length,
negative mean response NLL, mean-difference readouts, last-token layer 14,
constant ties, identical-prompt states, right-padding invariance, and five
descriptive shuffled-training-orientation fits. All bootstrap intervals resample
held-out source groups and condition on the fitted training set. The shuffled
runs are descriptive controls, not formal permutation p-values.

From the repository root, use the existing stage0 Python environment:

```sh
../semantic-entropy-probes-stage0/.venv/bin/python \
  experiments/information_chat_scaleup_v1/src/run_cached_analysis.py prepare \
  --snapshot /absolute/path/to/FROZEN_05000.json \
  --run-dir experiments/information_chat_scaleup_v1/private_data/run_5000_v1

# An explicit, bounded first local-model benchmark; spans all pending lengths.
../semantic-entropy-probes-stage0/.venv/bin/python \
  experiments/information_chat_scaleup_v1/src/run_cached_analysis.py extract \
  --run-dir experiments/information_chat_scaleup_v1/private_data/run_5000_v1 \
  --permit-local-forward --limit-pairs 20 --max-seconds 180 --pairs-per-batch 1

# Resume only after inspecting the measured time and memory estimates.
../semantic-entropy-probes-stage0/.venv/bin/python \
  experiments/information_chat_scaleup_v1/src/run_cached_analysis.py extract \
  --run-dir experiments/information_chat_scaleup_v1/private_data/run_5000_v1 \
  --permit-local-forward --max-seconds 7200 --pairs-per-batch 1

../semantic-entropy-probes-stage0/.venv/bin/python \
  experiments/information_chat_scaleup_v1/src/run_cached_analysis.py evaluate \
  --run-dir experiments/information_chat_scaleup_v1/private_data/run_5000_v1

../semantic-entropy-probes-stage0/.venv/bin/python -m pytest \
  experiments/information_chat_scaleup_v1/tests -q
```

Results are private aggregate JSON, an all-28-layer plot, held-out predictions
and exact fitted linear readout arrays. Existing results are not overwritten.
High ordering accuracy can reflect wording shortcuts in a shared rewrite recipe;
it does not establish semantic equivalence, correctness, calibration, semantic
entropy, mechanistic validity, causal control or usefulness as an SDT objective.

Prior local measurements suggest roughly 80–135 minutes for 10,000 individual
response forwards at the earlier input-length distribution. Pair batching may
improve this; the first benchmark's measured estimate governs the actual run.
The estimate excludes readout fitting and plot creation and is not a guarantee.
