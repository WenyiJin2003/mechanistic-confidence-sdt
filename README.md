# Mechanistic Confidence for Synthetic Fact Learning

## Current finding

**The independent cue-holdout challenge passed. A layer-14 linear readout trained
on the original 50 development pairs ranked the confident response above its
content-matched hesitant counterpart in 47/50 new pairs (94%; 95% interval
86–100%). The frozen 28-layer ensemble ranked 48/50 (96%).**

The challenge used new source groups, five tasks, five held-out certainty cue
families, exact 25/25 length counterbalancing and two complete blinded agent reviews.
Character TF-IDF reached 68%, answer likelihood 60% and response length 50%.
Unlike the original development diagnostic, the hidden-state result therefore
cannot be explained by those controls alone.

**Research decision:** this bounded 50-development / 50-challenge pilot supports
continuing the diverse-pair study, but it does not complete the full handoff.
The immediate next step is blind human review of the final construction canary,
followed by a matched cue-only baseline, leave-one-cue-family-out evaluation,
and 100/300/700-source learning curves. Use layer 14 as the simple primary
readout and keep the target name narrow:
**expressed certainty about preserved answer content**. Loss training remains a
downstream proposal, not the next experiment.

[Current result](experiments/cue_holdout_challenge_v1/RESULTS.md) ·
[Layer plot](experiments/cue_holdout_challenge_v1/results/CUE_HOLDOUT_LAYER_TRANSFER.png) ·
[Challenge protocol](experiments/cue_holdout_challenge_v1/README.md) ·
[Development diagnostic](experiments/diverse_pairs_multilayer_v1/reports/DEVELOPMENT_DIAGNOSTIC.md) ·
[Next decision](experiments/diverse_pairs_multilayer_v1/NEXT_DECISION.md) ·
[Data-construction gate](experiments/diverse_pairs_multilayer_v1/reports/DATA_CONSTRUCTION_GATE.md)

**Data expansion is not yet authorized.** Review of 200 source candidates kept
74, rejected 110 and sent 16 to human review. The latest two-stage rewrite
canary passed 10/10 mechanical checks after five recorded record-level repairs,
and its final independent model-assisted semantic audit retained 10/10. Together
with the earlier retained canary, **20/20 pairs now pass both checks**; blind
human review is still pending, with a balanced label-blind local review packet
already prepared. An
earlier symmetric-copy method is retained only as a lexical-control condition.
These are data-construction findings, not evidence for or against the activation
result above.

## Historical diagnostic findings

**A new linear probe detects contextual support for a fixed answer on unseen
facts and wording: 71.9% paired ordering. The full confidence validation remains
incomplete because missing information is not reliably distinguished.**

The historical v4 study kept Qwen 1.5B frozen and trained a new probe on neutral answers in 96 fictional records,
then tested 48 untouched records with different wording. It ranked the same
answer higher under supporting than contradicting evidence in **69/96 pairs
(71.9%; 95% interval 64.6–79.2%)**. This ordering remained 71.9% under both
confident and hedged wording. The earlier expressed-certainty readout reached
54.2% on the same neutral comparison.

**This establishes a partial evidence-support signal, not yet a validated
confidence measure.** Supported-versus-missing and missing-versus-contradicting
orderings were only 55.2% and 60.4%. Agreement with the model's own output
preferences weakened after accounting for context condition and fact type.
The measurement checks failed, so confidence-loss training remains deferred.
No auxiliary-loss training or causal intervention has been run here.

The long-term project asks whether ordinary SDT can be augmented with an
internal objective that helps a model learn target facts more reliably:

```math
\mathcal L_{\mathrm{total}}
=
\mathcal L_{\mathrm{SDT}}
+
\lambda\mathcal L_{\mathrm{internal}}.
```

[Historical v4 report](reports/EVIDENCE_CONFIDENCE_RESULTS_V4.md) ·
[Questions and answers](datasets/README.md) ·
[Method](docs/experiments/EXPERIMENT_MAP.md) ·
[Historical v4 method](docs/experiments/EVIDENCE_CONFIDENCE_README_V4.md)

## Research sequence

The historical experiment names remain in files and artifacts for
reproducibility. The research sequence is:

| Step | Study | Question | Result | Evidence | Status |
|---:|---|---|---|---|---|
| 1 | Stage 0 | Can a prompt state predict disagreement among future sampled answers? | Partly, but answer likelihood was stronger | [Report](reports/RESULTS_STAGE0.md#outcome) · [Data](datasets/stage0/README.md) | Complete |
| 2 | Stage 0B | Does an observed answer state predict disagreement among alternative answers? | Partly, with no gain beyond likelihood | [Report](reports/RESULTS_STAGE0.md#stage-0b--post-answer-hidden-state-diagnostic) · [Data](datasets/stage0/README.md) | Complete |
| 3 | Paired Confidence v1 | Can a linear direction distinguish confident from hedged wording? | Yes on the controlled held-out set | [Report](reports/PAIRED_CONFIDENCE_RESULTS_V1.md) · [Data](datasets/paired-confidence-v1/README.md) | Complete |
| 4 | Frozen Transfer v2 | Does the frozen direction transfer to new wording and evidence contexts? | Wording transferred; evidence robustness failed for one fact type | [Report](reports/CONFIDENCE_TRANSFER_RESULTS_V2.md) · [Data](datasets/frozen-transfer-v2/README.md) | Complete |
| 5 | Separation v3 | With the answer fixed, does the readout track whether context supports it? | The primary readouts scored 52.1% and 51.0% | [Report](reports/CONFIDENCE_SEPARATION_RESULTS_V3.md) · [Data](datasets/confidence-separation-v3/README.md) | Complete |
| 6 | Evidence-Sensitive Readout v4 | Can a new support readout transfer across facts and wording, and agree with model behavior? | 71.9% support ordering; missing-information and behavior checks failed | [Report](reports/EVIDENCE_CONFIDENCE_RESULTS_V4.md) · [Data](datasets/evidence-confidence-v4/README.md) | Complete |
| 7a | Diverse Paired Certainty + Multi-Layer | Is expressed certainty decodable across diverse content? | Hidden states reached 50/50, but text also reached 50/50; an independent challenge was required | [Report](experiments/diverse_pairs_multilayer_v1/reports/DEVELOPMENT_DIAGNOSTIC.md) | Development diagnostic complete |
| 7b | Cue/recipe-holdout transfer | Does the frozen certainty readout transfer to new sources and cue constructions beyond text, likelihood and length controls? | Layer 14: 47/50; ensemble: 48/50; TF-IDF: 34/50; likelihood: 30/50; length: 25/50 | [Result](experiments/cue_holdout_challenge_v1/RESULTS.md) | Development-only evaluation complete |
| **Current** | **Pair-construction gate** | **Can a diverse same-content pair recipe pass semantic and shortcut review before scale?** | **74/200 sources eligible; final canaries 20/20 mechanical and model-assisted semantic passes; human review pending** | **[Construction report](experiments/diverse_pairs_multilayer_v1/reports/DATA_CONSTRUCTION_GATE.md)** | **Blind human review next** |
| **Next** | **Matched diversity/scale completion** | **Does diverse rewriting beat a cue-only baseline under leave-one-cue-family-out transfer, and how does performance change at 100/300/700 sources?** | **Not yet tested** | **[Next decision](experiments/diverse_pairs_multilayer_v1/NEXT_DECISION.md)** | **Conditional on construction gate** |
| Later | Synthetic-fact training pilot | Does a candidate objective improve recall and retention beyond matched controls? | Not yet tested | [Downstream proposal](docs/experiments/NEXT_EXPERIMENT.md) | Requires a separate decision and preregistration |

```mermaid
flowchart LR
    U["Stage 0 / 0B<br/>Semantic uncertainty"] --> C["v1 / v2<br/>Expressed certainty"]
    C --> S["v3<br/>Fixed-answer validation"]
    S --> E["v4<br/>Partial evidence support"]
    C --> D["Diverse paired certainty<br/>development diagnostic"]
    D --> H["Cue/recipe-holdout<br/>94% at layer 14"]
    E -. "independent diagnostic" .-> T["Training loss<br/>deferred"]
    H --> X["Pair-construction gate<br/>+ blind human audit"]
    X --> M["Cue-only baseline +<br/>cue-family holdout"]
    M --> Y["100 / 300 / 700<br/>learning curves"]
    Y -. "only after a new decision" .-> T
```

Steps 1–3 estimate different readouts with different labels and token positions.
Only the v1 certainty directions from Step 3 are reused in Steps 4 and 5.

## How the certainty readout works

We first reproduced a small version of the
[Semantic Entropy Probes pipeline](https://arxiv.org/abs/2406.15927) to establish
generation, uncertainty labels, state extraction and evaluation. We then
studied a different target: expressed certainty in matched confident and hedged
answers. All certainty studies used supplied responses that Qwen read through
a forward pass; they did not label confidence in its own generated answers.

The early v1 readout averaged paired hidden-state differences at the response
end. The current challenge uses a stricter development-trained method: it
averages ordinary answer-token states at each layer, standardizes features on
the 50 development pairs, and fits a no-intercept paired logistic readout. The
layer-14 readout and equal 28-layer ensemble are then frozen before the 50 new
challenge pairs are scored. The [method](docs/experiments/EXPERIMENT_MAP.md)
gives the exact equations and split boundary.

## Step 5: why a new measurement was needed

We authored **48 new fictional records and 672 responses**. For example:

| | Supporting world | Contradicting world |
|---|---|---|
| Supplied fact | The depot's entry code is 4712. | The depot's entry code is 8635. |
| Identical response | The entry code is 4712. | The entry code is 4712. |

Both candidate values were tested. Answer tokens, response positions and prompt
lengths matched across worlds. The layer-14 directions were fitted on earlier
training data and frozen before this new test.

| Method | Confident > hedged | Same answer: supported > contradicted |
|---|---:|---:|
| Final ordinary response-token readout | **100.0%** | **52.1% [44.8, 59.4]** |
| Mean of response-content states | **100.0%** | **51.0% [47.9, 54.2]** |
| Answer likelihood | 43.2% | **100.0%** |

These are **paired score-ordering rates**, not generated-answer accuracy.
Intervals resample the 48 base records together with all their variants.
Likelihood confirms that the context change is detectable in this sample;
its perfect ordering is not evidence of perfectly calibrated confidence.

The response-mean score also rose when relevant context was present **and
contradicted the answer**: 80.2% versus 81.3% for supporting context, each
compared with omitted information. This post-hoc check suggests sensitivity to
relevant information being present, although context wording remains a possible
contributor. See the [full report and figure](reports/CONFIDENCE_SEPARATION_RESULTS_V3.md).

## Current conclusion

- **The main wording/length shortcut concern now has a positive transfer test.**
  On 50 new locked pairs, the frozen layer-14 readout reached 94%, compared
  with 68% for character TF-IDF, 60% for answer likelihood and 50% for length.
  This supports a transferable hidden-state signal for expressed certainty,
  while stopping short of a general-confidence or causal claim.
- **Evidence support is partly decodable across facts and wording.** V4's new
  probe reached 71.9% on fixed-answer supporting-versus-contradicting contexts,
  exceeding its shuffled-control criterion. Omission was never fitted as a
  false answer, and its held-out checks failed. The result supports contextual
  answer verification on this small task, rather than a general confidence scale.
- **Expressed certainty is decodable in these controlled tasks.** The earlier samples
  use a limited set of authored wording families; lexical and template cues
  remain possible, and the score does not establish the model's own belief.
  In v1, 12/200 shuffled directions also reached 100%; the
  [controls](reports/PAIRED_CONFIDENCE_RESULTS_V1.md#outcomes-and-controls)
  do not identify a unique certainty mechanism.
- **Confidence measurement remains unvalidated.** The old certainty directions
  lack reliable answer-support sensitivity; the new support probe fails the
  full uncertainty and behavior checks. Evidence ordering can survive a style
  change while absolute scores still shift substantially with that style.
- **Vector angles do not establish independent mechanisms.** Nearly
  perpendicular certainty and correctness contrasts can still detect the same
  wording. The [cached audit](reports/CONFIDENCE_CORRECTNESS_AUDIT.md) checks this
  without treating the estimated correctness direction as a complete truth axis.

## Historical Step 6: evidence-support test

V4 used **168 new fictional records**, split into 96 training, 24 validation
and 48 untouched test records. It supplied the same neutral answer under
supporting, omitted and contradicting evidence. It fitted only on training
support-versus-contradiction pairs, with one fixed layer and regularization.
Test records and context/question/answer templates are all held out.

| Primary same-answer comparison | Pair ordering | 95% source interval |
|---|---:|---:|
| Supported > contradicted | **71.9% (69/96)** | 64.6–79.2% |
| Supported > omitted | **55.2% (53/96)** | 43.8–66.7% |
| Omitted > contradicted | **60.4% (58/96)** | 47.9–72.9% |

These percentages count which context receives the higher score. They are
neither the model's confidence probabilities nor generated-answer accuracy.
All comparisons stay bundled within the 48 test records.

Independent question paraphrases elicited **144 actual model answers**.
On contexts supplying the requested fact, 67/96 answers explicitly mentioned
the correct candidate; 63/96 matched its value exactly. When information was
omitted, 40/48 answers were exactly `unknown`. Three known-context outputs were
cut short while restating the question, and others named a field instead of a
value. These output limitations contribute to the failed behavioral check.

The hidden-state probe and candidate likelihoods had an overall rank correlation
of 0.450. After centering by evidence condition and fact type it was 0.205,
with an interval spanning zero. Support classification alone therefore does
not establish the intended confidence interpretation.

The [registered design](docs/experiments/EVIDENCE_CONFIDENCE_V4_PREREGISTRATION.md)
fixed the controls and pass criteria before inference. The
[v4 report](reports/EVIDENCE_CONFIDENCE_RESULTS_V4.md) includes every endpoint
and limitation; the [independent audit](results/evidence_confidence_v4/independent_audit.json)
reproduced 46,762 numerical values with zero discrepancies.

For that separate evidence-support line, a future measurement should use a
clearer output task, graded or conflicting evidence, and fully crossed behavior
wording and candidate positions. It must test fresh records and model behavior
before treating that readout as a confidence loss.

## Downstream proposal: training study

Run a small **synthetic-fact SFT pilot** with four matched conditions: ordinary
SFT, SFT plus the frozen readout loss, random-direction controls, and an
output-only control that adds weight to target-answer tokens. Test new phrasings
of the trained facts and retention after the same interference step in all
groups. Judge improvement independently of the optimized readout score.

This first pilot would use completed-answer states, matching the current
readout. Transfer to ordinary document training would need separate testing.
The [downstream proposal](docs/experiments/NEXT_EXPERIMENT.md) preserves the
controls and decisions to fix before training. The cue-holdout result supports
retaining this option, but the [matched diversity/scale study](experiments/diverse_pairs_multilayer_v1/NEXT_DECISION.md)
and a new execution decision come first. It remains a proposal rather than a
completed experiment.

The [experiment map](docs/experiments/EXPERIMENT_MAP.md) gives the exact token
positions, data splits and equations. The [code map](code/README.md) provides
reproduction entry points; [project status](docs/experiments/STATUS.md) records
the current decision. The supplementary
[correctness and geometry audit](reports/CONFIDENCE_CORRECTNESS_AUDIT.md)
reuses data from Steps 3 and 4.

## Repository layout

| Folder | Purpose |
|---|---|
| [datasets/](datasets/README.md) | Readable questions, answers and CSV downloads |
| [data/](data/README.md) | Exact machine-readable source inputs and data audits |
| [reports/](reports/README.md) | Research findings and interpretation |
| [code/](code/README.md) | Code map and entry points for reproducing each experiment |
| [docs/](docs/README.md) | Methods, execution instructions and provenance |
| [results/](results/README.md) | Saved numerical outputs, states, readouts and manifests |
| [plots/](plots/) | Research figures |
| [configs/](configs/) | Experiment settings |

The code map points to `stage0/`, `confidence_pilot/` and `scripts/`. Their paths
are retained so existing commands and cached-artifact checks remain valid.
The two root preregistrations retain their original content and published paths.

## Sources

This work adapts Kossen et al.'s [*Semantic Entropy Probes*](https://arxiv.org/abs/2406.15927)
and [official OATML code](https://github.com/OATML/semantic-entropy-probes).
The upstream snapshot and MIT license are preserved; the small-model experiments
and paired-response studies are not a full paper replication.
