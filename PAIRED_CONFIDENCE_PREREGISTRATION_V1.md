# Paired Confidence Pilot v1: preregistration

Registered 7 October 2026, before activation extraction or evaluation.

## Question and scope

Can a simple internal readout score a confidently phrased response above a hedged
response with the **same answer proposition**, on unseen source questions and
unseen rewrite families? Does the ordering hold within both correct and wrong
answers?

The intended construct is **expressed certainty**. A successful pilot identifies
a candidate readout of that construct. It does not identify subjective confidence,
factual belief, calibration, causal control, or a loss ready for synthetic document
training (SDT). The proposed research remains ordinary SDT plus a possible future
internal term; ordinary SDT specifies which content to learn. No intervention or
model training is authorized in this pilot.

Casper's meeting suggestion motivates matched confident/hedged responses and
separation from correctness. Every numerical, model, domain, layer, token,
template, and gate choice below is our implementation choice.

## Data and locked partitions

| Phase | Source questions | Domains | Train / validation / test | Families | Responses |
|---|---:|---|---|---|---:|
| A | 24 | 8 factual QA, 8 arithmetic/logic, 8 academic | 12 / 6 / 6 | A, B | 192 |
| B | 120 | 40 per domain | 72 / 24 / 24 | A, B, C | 1,440 |

Each source has correct and deliberately incorrect answer content. Each content
has confident and hedged versions, preserving the exact answer proposition and
all qualifications. Answers are uniformly double-quoted in both versions so
fragmentary MMLU choices remain grammatical as short-answer content. The four
cells are balanced. Templates use multiple distinct
phrasings; no rewrite instruction or certainty/correctness label enters Qwen's
input. No response generation or entailment inference is needed.

Factual QA reuses cached SQuAD v2 material, choosing at most one item per context.
Arithmetic keys are mechanically verified. Following the user's authorization,
academic items come from the MMLU test parquet, pinned to dataset `cais/mmlu`
revision `c30699e8356da336a370243923dbaf21066bb9fe` and file SHA-256
`74a41822ce7d3def56e1682f958469c04642a5336a5ce912fa375fdb90fb25d7`.
Use self-contained natural short-answer questions, the original correct choice,
and a keyed wrong choice; retain original questions/options and any adaptation.
This deliberately selected convenience sample is not an MMLU benchmark score.
Source provenance, distractor justification, templates, and source splits are
saved before extraction. The full Phase A audit table lists every source and all
four core variants, and a pair-level audit covers both families.

Splits are fixed and balanced by domain, using seed 20261007. All variants of one
source stay together. All 24 Phase A sources are assigned to Phase B training;
Phase B validation/test sources are fresh relative to the engineering pilot.
Family C never participates in fitting or hyperparameter selection. Validation
is reported without tuning any listed hyperparameter.

## Frozen model and representations

Qwen/Qwen2.5-1.5B-Instruct, local snapshot
`989aa7980e4cf806f80c7fef2b1adb7bc71aa306`, unquantized bfloat16 on MPS, CPU
float32 fallback. The tokenizer and model load from the pinned local snapshot;
weights and the existing Python environment are reused. Saved vectors are
float16. The natural conversation contains the user question/context and the
written assistant response, with system text `You are a helpful assistant.`

The primary feature is `hidden_states[14]` at the first fixed token immediately
after the complete response: Qwen's assistant end-of-turn token `<|im_end|>`,
ID **151645**. It is a special-token boundary convention and can itself encode
formatting effects. A response need not end in the same ordinary word/token.

Secondary features at layer 14 are (i) final ordinary response-content token and
(ii) mean over response-content tokens only. Layer 23 boundary is exploratory.
The final prompt token before the assistant response is a negative extraction
control. Inputs within each source have identical prompt IDs and are right-padded
to the same source-specific length to keep prefix numerical computations stable.
No padding/special boundary tokens enter response pooling or response NLL.

Four sources must pass the no-generation, exact-prefix, boundary-location,
finite-state, layer/width, prompt-invariance (absolute tolerance 1e-6), and resume
checks before all 24 sources are extracted. Every row is cached immediately with
model/config/input fingerprints.

## Primary readout and estimand

For training source q, correctness k and family f in A/B, form

\[
d_{qkf}=h_{qkf}^{\mathrm{confident}}-h_{qkf}^{\mathrm{hedged}}.
\]

Average the differences within each source, then average sources equally and
normalize: \(v=\bar d/\|\bar d\|\). Score \(s(h)=v^\top h\). No scaler or
dimension selection is used for the primary raw-space mean-difference direction.

A pair scores 1 when confident > hedged, 0 when reversed, 0.5 for an exact tie.
Average within source and then across sources. Phase A primary endpoint is test
sources with familiar A/B families. Phase B primary endpoint is **family C on
fresh test sources**, comprising 48 pairs but only 24 independent source units.
Report correct/wrong, domain, family, subtype, and split strata.

All intervals use 2,000 source-bundle bootstrap resamples (seed 161803).
Comparisons use paired source draws. No individual-variant bootstrap or pooling
of responses as independent observations is permitted.

## Controls and ablations

- 200 shuffled directions: one random sign per training source, applied to all
  its confident-minus-hedged pairs before refitting.
- 200 norm-matched random directions, arranged as 100 antipodal pairs. Their
  average is chance; individual random directions can perform strongly when
  templates share a common shift. Report the full distribution, not a misleading
  narrow random-control interval.
- Token/character length, sequence NLL, and mean-token NLL baselines: train-only
  scaling and fixed L2 logistic regression, C=1, max_iter=2000.
- Train-only response TF-IDF word/bigram model plus fixed L2 logistic regression.
- Correctness-stratified results and template/source holdouts.
- Train-only style-balanced correct-minus-wrong direction; report its cosine
  with v and ordering after projecting that one direction out. Projection is an
  ablation, not proof of semantic independence.
- Ordering by response-length difference and template subtype; report matched
  and reversed-length groups where present.

A strong text baseline is expected for expressed certainty and is not itself a
failure. A signal confined to one phrase, one domain, correct content only, or
familiar templates requires redesign. No nonlinear or tuned secondary probe is
needed for v1.

## Progression rules

Phase A requires at least 95% content-preserving pairs, no split leakage, valid
extraction/cache checks, primary ordering at least 0.625, correct and wrong
subsets each >0.5, both A/B families >0.5, and at least two domains >0.5. The
ensemble mean of shuffled/random controls must fall within [0.4,0.6]. These weak
screens on six test sources authorize only Phase B; they are not confirmation.

Phase B is promising only if family-C/test-source ordering is at least 0.65 with
bootstrap lower bound >0.5, correct/wrong subsets each at least 0.60, no domain
below chance, projected ordering remains >0.5, and multiple held-out phrasings
and available length-controlled pairs retain ordering. Missing length controls
are a limitation rather than silently assumed evidence. Report any failure.

Stop after the construct pilot. A future decision may improve data diversity or
prepare an SDT transfer test; steering and confidence-loss training need a new
explicit decision.

## Methodological references

- [Rimsky et al., Contrastive Activation Addition](https://aclanthology.org/2024.acl-long.828/): inspiration for contrastive mean directions.
- [Marks & Tegmark, The Geometry of Truth](https://arxiv.org/abs/2310.06824): reference for truth-direction transfer and correctness cautions.
- [Miao & Ungar, Closing the Confidence–Faithfulness Gap](https://arxiv.org/abs/2603.25052): distinguishes verbalized confidence and calibration.
- [Kumaran et al., How do LLMs Compute Verbal Confidence](https://arxiv.org/abs/2603.17839): motivates answer-adjacent position checks; not a replication with this small model.
- [Kumaran, Reported Confidence Tracks Commitment More Than Correctness](https://arxiv.org/abs/2606.29490): motivates within-correctness comparisons.
- [Kossen et al., Semantic Entropy Probes](https://arxiv.org/abs/2406.15927): existing engineering lineage, with a different construct/target.
