# Probe-guided LoRA canary: result and next experiment

## What this experiment established

The frozen L14 auxiliary loss was technically effective. Increasing the
auxiliary-to-CE gradient ratio from 0 to 0.05 and 0.10 increased the internal
confident-minus-hesitant separation monotonically, and the ratio-0.10 change
was positive at all 28 evaluated layers on both evaluation splits.

The independent free-generation result was much weaker. Claude Opus 5.5
medium judged all 477 randomized A/B items with zero missing and zero
exclusions. On DEV113, ratio 0.10 improved directional credit by 0.040 over
ratio 0, with a paired 95% bootstrap interval of -0.009 to 0.088. On the
Behavior46 canary, the improvement was 0.011, with an interval of -0.033 to
0.054. The preregistered DEV threshold was +0.05, so no lambda was selected.

This is a partial mechanistic success and a method diagnostic, not a positive
behavioral result. The training objective can move the frozen probe readout,
but moving that readout under teacher-forced target answers was not sufficient
to produce a reliable visible confidence difference during neutral free
generation.

## Most likely explanation

The pattern is more consistent with a proxy-to-behavior mismatch than with a
merely weak lambda. Ratio 0.10 already caused a large internal shift, including
on the model's free-generated answers, while leaving most blind comparisons
tied. Teacher forcing and response-mean pooling may contribute, but teacher
forcing alone cannot explain why the free-generation readout moved without a
corresponding visible change. Increasing lambda alone would mainly test whether
the same internal statistic can be moved even farther.

## Primary next experiment: causal activation steering

The next question is not whether training can enlarge the L14 gap. Because L14
was part of the training objective, that enlargement is only a manipulation
check. The scientific question is whether the latent direction has a causal
effect on the model's generated language.

Run a provider-free inference intervention before any further LoRA or DPO
training:

1. Use the frozen 920-pair L14 direction and the unadapted
   Qwen2.5-1.5B-Instruct model under one neutral prompt and fixed decoding.
2. During autoregressive generation, add the normalized probe direction after
   layer 14 at every response-token position. Apply both signs so the same
   question produces `+probe` and `-probe` answers.
3. Scale the intervention in projection-standard-deviation units. For a target
   shift of `a` standard deviations, use
   `delta_h = a * sigma_score * w / ||w||^2`, so the intended score change is
   defined without using the resulting L14 gap as an endpoint.
4. Pre-freeze two modest magnitudes, for example `a = 0.5` and `a = 1.0`, and
   retain every generated answer. Do not select a magnitude by blind-judge
   performance.
5. Add a norm-matched direction orthogonal to the probe as the perturbation
   control, using the same positive and negative magnitudes.
6. Freeze a source-disjoint question set before generation. Previously exposed
   CF3 and Cue50 rows may be used only for engineering checks, not a new
   confirmatory claim.

The primary endpoint is a randomized blind comparison of `+probe` versus
`-probe`: which answer expresses greater confidence? The judge must not see
activations or intervention labels. Report content equivalence, naturalness,
refusal, completeness, length, and repeated certainty-cue rates separately.

Evidence that the latent representation affects output requires all of the
following:

- `+probe` is judged more confident than `-probe`, with a paired bootstrap
  interval excluding chance or a preregistered directional-credit improvement
  of at least 0.10.
- The effect is larger than the matched `+orthogonal` versus `-orthogonal`
  control.
- The effect shows the expected dose ordering without material content or
  language-quality degradation.
- The result is not driven only by a few repeated certainty phrases, refusals,
  length changes, or incomplete answers.

The measured post-intervention L14 score is only a verification that the hook
was applied correctly; it is not a success criterion.

If this intervention changes visible confidence, the L14 direction has causal
output relevance and can justify a later training intervention. If it does
not, the current evidence supports linear separability and manipulability of a
readout, but not causal usefulness for generation. A subsequent probe-ranked
DPO experiment would answer a different question—whether the probe is useful
as a preference-labeling signal—not whether the latent direction itself
controls output.

Do not claim a general confidence intervention unless the free-generation
endpoint passes. Do not use a larger internal L14 gap alone as a GO decision.
