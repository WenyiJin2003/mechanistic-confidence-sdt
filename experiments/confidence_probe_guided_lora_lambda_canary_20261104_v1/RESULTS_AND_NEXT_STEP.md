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

## Smallest informative next experiment

Run a bounded **frozen-probe-ranked preference DPO** canary against a matched
continued-SFT control. This tests whether the probe contains a useful ranking
signal for selecting complete answers even though direct activation loss did
not reliably control visible language.

1. Start from the existing confident and hesitant SFT checkpoints.
2. On the same 156 CF200 training questions, generate a predeclared fixed
   number of candidate answers with frozen decoding settings and seeds.
3. Retain every question and candidate. Form a preference pair only when the
   two candidates have the same main answer/content under a frozen mechanical
   rule; record all unpaired cases rather than replacing them.
4. Re-feed the frozen candidate texts through the **unadapted base Qwen model**
   and score them with the frozen L14 probe. This is important: the training
   LoRA must not score its own activations.
5. For the confident adapter, prefer the higher-scoring candidate; for the
   hesitant adapter, reverse the preference. Train standard DPO with
   `beta = 0.1` for one short epoch, with no sweep.
6. Train matched continued-SFT controls from the same starting checkpoints and
   match data exposure and optimization budget as closely as possible.
7. Use two paired seeds: two roles by two methods by two seeds gives eight
   short training runs.

CF3 DEV113 and Cue50 Behavior46 may remain engineering diagnostics but cannot
become a new confirmatory test. Freeze 60 genuinely source-disjoint questions
for the primary behavioral check before training.

The primary endpoint is randomized blind directional credit for the
probe-ranked DPO confident/hesitant pair relative to matched continued-SFT.
Pre-freeze a diagnostic GO threshold of at least `+0.10`, positive improvement
in both paired seeds, and no more than a five-point degradation in content and
naturalness. Also require no material increase in repeated certainty cues,
refusals, severe length shifts, or incomplete answers.

Report the agreement between the probe's training-candidate ranking and an
independent behavioral judge. If that agreement is poor, a DPO score increase
would be evidence of lexical/proxy optimization rather than successful
confidence control.

This DPO canary is not claimed to be continuous on-policy RL, and success would
not by itself prove that teacher forcing was the sole problem. It is a direct
test of whether a frozen probe-derived preference can control complete-answer
generation better than direct hidden-state optimization.

Do not claim a general confidence intervention unless the free-generation
endpoint passes. Do not use a larger internal L14 gap alone as a GO decision.
