# Paired Confidence v1 — Answer-End Expressed-Certainty Readout

7 October 2026. Both phases are complete.

This experiment estimates a new post-response direction. It does not reuse the
Stage 0 prompt-state or Stage 0B answer-content semantic-uncertainty probes.
V1's Phase A/B labels are internal engineering/main scale-up phases, not the
separate project experiment named Stage 0B.

The pilot supports a candidate internal readout of **expressed certainty** on this
controlled sample: the preregistered layer-14 direction ordered all 48 held-out
family-C test pairs correctly, across 24 unseen source questions. All data,
extraction/cache, and statistical gates passed. This warrants a harder transfer
test, not a claim about subjective confidence, calibration, causal control, or a
validated synthetic-document-training (SDT) loss. Broad null-direction results
and five family-C failures outside the test split limit the interpretation.

## Sample and audit

| Phase | Sources by domain | Source train / validation / test | Families | Responses / pairs |
|---|---|---|---|---:|
| A | 8 cached SQuAD v2, 8 arithmetic/logic, 8 selected MMLU | 12 / 6 / 6 | A, B | 192 / 96 |
| B | 40 cached SQuAD v2, 40 arithmetic/logic, 40 selected MMLU | 72 / 24 / 24 | A, B, C | 1,440 / 720 |

Each source has correct and deliberately wrong answer content, each written
confidently and with hedging while retaining its answer proposition and
qualifications. MMLU covers eight subjects: one item per subject in A and five
in B; these are selected short-answer adaptations, not an MMLU benchmark score.
All 24 Phase-A sources enter Phase-B training; Phase-B validation/test sources
are fresh. Families A/B alone fit the direction; C is excluded from fitting and
selection. Splits stay grouped by source.

The recorded preservation rate is 100% in both phases, with no source leakage
or duplicate question/context groups. This is research-agent source/content
review plus deterministic pair validation, **not human review**. See the full
[A audit table](../data/paired_confidence/phase_a_audit_table.md),
[B audit table](../data/paired_confidence/phase_b_audit_table.md), and
[MMLU provenance](../data/paired_confidence/mmlu_selection.json).

## Frozen extraction and readout

The model is unquantized Qwen/Qwen2.5-1.5B-Instruct, snapshot
`989aa7980e4cf806f80c7fef2b1adb7bc71aa306`, run in bfloat16 on MPS; saved vectors
are float16. The primary feature is `hidden_states[14]` at `<|im_end|>`
(ID 151645), the first fixed token after the complete assistant response. Its
state **consumes the boundary token**, so formatting effects remain possible.
Secondary positions are the final ordinary content token and the mean of
response-content tokens; layer-23 boundary is exploratory.

For training source \(q\), correctness \(k\), and family \(f\in\{A,B\}\):

\[
d_{qkf}=h^{\mathrm{confident}}_{qkf}-h^{\mathrm{hedged}}_{qkf},\quad
\bar d_q=\operatorname{mean}_{k,f}d_{qkf},\quad
v=\frac{\operatorname{mean}_q\bar d_q}{\|\operatorname{mean}_q\bar d_q\|},
\quad s(h)=v^\top h.
\]

This is a raw-space, source-equal mean direction without scaling or dimension
selection. Pair outcomes are 1 for confident > hedged, 0 for reversal, and 0.5
for an exact tie; outcomes are averaged within source, then across sources.
Intervals use 2,000 source-bundle bootstrap draws; comparisons use paired source
draws, not independent responses.

```text
A/B training pairs → source-averaged direction → C pairs on fresh test sources
```

Exact prompt IDs and prompt states match within source (maximum difference 0).
Boundary, finite-state, layer/width, and exact-resume checks passed; the resumed
sanity pass required zero forward calls. Runs used teacher-forced forward
passes, with zero generation, NLI, or API calls. Manifest full-run elapsed times
were 35.6 seconds for A and 246.3 seconds for B, including cache reuse.

## Outcomes and controls

Phase A reached 100% on 24 A/B test pairs from **six sources**; its TF-IDF text
baseline also reached 100%. This was an engineering progression screen only.
Phase B's primary endpoint was **48 C pairs / 24 unseen sources**, with no ties.
Its bootstrap interval is [100%, 100%] because every observed source succeeded;
this saturated empirical interval does not guarantee 100% population accuracy.

| Phase-B C/test readout | Ordering | Source-bootstrap 95% interval |
|---|---:|---:|
| Layer 14 boundary, primary | 100% | 100–100% |
| Layer 14 final content | 100% | 100–100% |
| Layer 14 response mean | 100% | 100–100% |
| Layer 23 boundary, exploratory | 72.92% | 56.25–87.50% |
| Response TF-IDF | 56.25% | 50.00–62.50% |
| Token/character length | 62.50% | 45.83–79.17% |
| Sequence NLL | 31.25% | 14.58–50.00% |
| Mean-token NLL | 43.75% | 25.00–62.50% |
| NLL plus length | 52.08% | 33.33–70.83% |

The primary readout reached 100% separately for correct and wrong content
(24 pairs each), each domain (16 pairs / eight sources), and all C subtypes:
C0 10/5, C1 16/8, C2 6/3, C3 16/8 pairs/sources. Baselines use train-only
fitting and fixed hyperparameters. TF-IDF tied on **42/48 pairs (87.5%)**;
its low C score therefore mainly reflects ties and does not establish freedom
from lexical/style cues. The prompt negative control was entirely tied at 50%.

| Null directions, 200 per control | Mean | Empirical central 95% range | Full min–max |
|---|---:|---:|---:|
| A source-sign shuffled | 56.88% | 0–100% | 0–100% |
| A antipodal random | 50.00% | 8.33–91.67% | 0–100% |
| B source-sign shuffled | 53.35% | 2.08–100% | 0–100% |
| B antipodal random | 50.00% | 12.50–87.50% | 2.08–97.92% |

In B, **12/200 shuffled directions also reached 100%**. Random directions are
norm-matched, with 100 antipodal pairs, so their ensemble mean is mechanically
50%. These broad distributions are compatible with shared template shifts;
they are descriptive controls, not permutation p-values or evidence of a
unique confidence mechanism.

The confidence/correctness-direction cosine was 0.301743. Projecting out the
single train-only, style-balanced correctness direction retained 100% ordering;
this ablation does not establish semantic independence. Token length matched
within one token retained 100% on 42 pairs / 21 sources. The reversed-training-
length-sign subset also retained 100%, but contains only six pairs / three
sources, all C2, so that control is small and phrasing-specific.

Family C scored 98.61% on training sources and 93.75% on validation sources.
All **five reversed pairs** were academic C2: `academic-012` in training
(correct and wrong), `academic-016` in validation (correct), and `academic-020`
in validation (correct and wrong). None was excluded. Exact scores and indices
are in [saved scores](../results/paired_confidence_phase_b/readout_scores.npz) and
[pair metadata/metrics](../results/paired_confidence_phase_b/pair_metrics.json).

## Decision and reproducibility

Improve source, answer, and phrasing diversity and cue controls, then prepare a
neutral-style QA/document transfer test before considering causal intervention
or training. **No SDT loss has been validated.** The earlier Stage 0/0B work
probed semantic uncertainty from sampled-answer diversity; this experiment
labels expressed certainty in fixed written responses. The historical
[Stage 0 results](RESULTS_STAGE0.md) are unchanged.

The [preregistration](../PAIRED_CONFIDENCE_PREREGISTRATION_V1.md),
[A configuration](../configs/paired_confidence_phase_a.yaml),
[B configuration](../configs/paired_confidence_phase_b.yaml),
[A metrics](../results/paired_confidence_phase_a/pair_metrics.json),
[A manifest](../results/paired_confidence_phase_a/manifest.json), and
[B manifest](../results/paired_confidence_phase_b/manifest.json) record the locked
choices, gates, hashes, and runtime. The
[comparison plot](../plots/paired_confidence_pairwise_results.png) summarizes the
endpoints; numerical claims above follow the saved metrics.
