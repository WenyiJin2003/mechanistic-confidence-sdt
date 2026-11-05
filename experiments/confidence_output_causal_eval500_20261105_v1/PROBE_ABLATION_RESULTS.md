# Probe-loss ablation on 500 fresh questions

## Question tested

This is the direct test of whether adding the frozen L14 probe objective changes
free-generation confidence beyond ordinary same-role SFT.

- Confident: `confident_r010` versus `confident_r000`.
- Hesitant: `hesitant_r010` versus `hesitant_r000`.

Within each comparison, the training data, role, model, seed, LoRA structure,
epochs, prompt, decoding, and 500 evaluation questions are matched. The intended
difference is whether the auxiliary probe gradient ratio is 0.10 or 0.

## Behavioral result

Claude Opus 5.5 medium judged all 1,000 randomized same-role pairs with zero
missing or excluded rows.

For confident SFT, adding probe loss did not make outputs more confidently
expressed:

- Probe-loss win: 6/500.
- CE-only win: 8/500.
- Tie: 483/500; cannot judge: 3/500.
- Directional credit: 49.8%, 95% bootstrap interval 49.1% to 50.5%.

For hesitant SFT, adding the opposite-direction probe loss produced a small but
inconclusive tendency toward more hesitant outputs:

- Probe-loss desired-direction win: 16/500. Here the desired direction means
  CE-only was judged more confident than probe-guided hesitant.
- Opposite-direction win: 9/500.
- Tie: 473/500; cannot judge: 2/500.
- Directional credit: 50.7%, interval 49.7% to 51.7%.

Across both roles, target-direction credit was 50.25%, interval 49.65% to
50.85%. The interval includes chance.

## Internal readout result

The probe objective did change the free-generated-answer representations in the
intended direction:

- Confident L14: +0.372 SD versus CE-only, interval +0.331 to +0.412.
- Hesitant L14: -0.526 SD versus CE-only, interval -0.588 to -0.470.
- Confident equal-28: +0.099 SD, interval +0.072 to +0.127.
- Hesitant equal-28: -0.153 SD, interval -0.194 to -0.116.

Response length did not reliably change in either role.

## Conclusion

The auxiliary loss successfully manipulates the latent probe readout, including
on free-generated responses. It does not, at this training strength and setup,
produce a reliable visible change in expressed confidence or hesitation on the
500-question cohort.

Therefore the current evidence supports **latent manipulability without
demonstrated behavioral utility**. A larger L14 gap alone is not evidence that
the latent representation improves output confidence control. The clean next
causal test is direct `+probe` versus `-probe` activation steering, with a
norm-matched orthogonal direction control, rather than increasing the auxiliary
loss solely to enlarge its own readout.

The Claude run's list-cost fields sum to $5.8283. This is usage metadata, not an
invoice or proof of an actual charge.
