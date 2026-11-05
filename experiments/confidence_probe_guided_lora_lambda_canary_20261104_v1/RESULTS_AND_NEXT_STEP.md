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

The pattern is more consistent with a teacher-forcing / generation-trajectory
mismatch, potentially combined with probe-specific shortcut optimization,
than with a merely weak lambda. Ratio 0.10 already caused a large internal
shift while leaving most blind comparisons tied. Increasing lambda alone may
therefore enlarge the same internal statistic without answering whether the
effect reaches the model's own generated trajectory.

## Smallest informative next experiment

Run one bounded root-cause diagnostic while reusing the completed ratio-0 and
teacher-forced ratio-0.10 arms as frozen references:

1. Train a new confident/hesitant pair at teacher-forced ratio 0.20.
2. Train a new confident/hesitant pair at ratio 0.10 using deterministic
   on-policy replay: at fixed intervals, generate the model's own completion
   without gradients, re-feed those generated tokens, and apply the same
   bounded L14 margin loss to that replayed completion. Keep the CE term on
   the original paired training answer.
3. Change no data, LoRA recipe, decoding settings, judge, or evaluation split.

This requires four new adapter trainings and directly separates two
explanations:

- If teacher-forced 0.20 improves behavior while on-policy 0.10 does not, the
  earlier auxiliary strength was probably insufficient.
- If on-policy 0.10 improves behavior while teacher-forced 0.20 does not, the
  main issue was objective placement on the wrong token trajectory.
- If both further enlarge L14 but neither improves blind behavior, the frozen
  readout is not currently a useful causal control signal for visible
  confidence under this training setup.

Pre-freeze the same primary success criterion: at least +0.05 DEV directional
credit over ratio 0, with the paired interval reported and no material loss of
content, fluency, refusal behavior, or output completeness. Behavior46 remains
a post-exposure secondary robustness check and must not be used to select the
method.

Do not claim a general confidence intervention unless the free-generation
endpoint passes. Do not use a larger internal L14 gap alone as a GO decision.
