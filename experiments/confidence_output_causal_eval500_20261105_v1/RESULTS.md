# Direct 500-question evaluation results

## Outcome

Both frozen ratio-0.10 adapters answered all 500 fresh factual questions under
the same neutral prompt, producing 1,000 answers. Ten of ten GPU cells completed
with zero empty answers. Claude Opus 5.5 medium judged all 500 randomized A/B
pairs in ten batches, with zero missing, excluded, or failed rows.

Claude selected the confident adapter as more confident 24 times and the
hesitant adapter 9 times; 466 comparisons were ties and one was unjudgeable.
Counting ties and the unjudgeable row as 0.5, directional credit was 51.5%, with
a paired bootstrap 95% interval of 50.4% to 52.6%. Among the 33 directional
comparisons, the confident model won 72.7% (one-sided exact binomial p=0.0068).

This is a small and sparse visible effect, not a large behavioral split.

## Internal versus visible effect

The internal separation was much larger:

- L14 confident-minus-hesitant mean difference: +0.979 SD, 95% bootstrap
  interval +0.897 to +1.069.
- Equal-28 mean difference: +0.328 SD, interval +0.276 to +0.382.

Thus the auxiliary objective strongly changes the frozen readout, but that
change usually does not alter visible confidence. Exact responses were identical
for 142/500 pairs, and Claude called 466/500 confidence ties even though only 142
were text-identical.

## Quality and confounds

- Material content difference: 78/500.
- Fluency issue: 24 confident answers and 25 hesitant answers.
- Length dominated judgment: 0/500.
- Hit the 256-token cap: 22 confident and 21 hesitant answers; all retained.
- Refusal heuristic: 8 confident and 10 hesitant answers.
- Mean generated-token difference, confident minus hesitant: -2.8 tokens,
  bootstrap interval -7.3 to +1.6.

The post-hoc clean subset—no material difference, fluency flag, or length
confound—contained 391 pairs: 2 confident wins, 2 hesitant wins, and 387 ties.
This subset is descriptive, not a replacement endpoint, but it shows that most
detectable directional differences were entangled with another review flag.

## Interpretation

The larger cohort confirms a weak, statistically detectable directional effect
of the two trained adapters, but not robust, clean separation of expressed
confidence. It also strengthens the earlier proxy-to-behavior diagnosis: the
L14 statistic moves substantially more than language behavior.

This experiment compares two trained LoRAs. It does not establish that the L14
direction itself causally controls generation. The direct next test remains a
frozen `+probe` versus `-probe` activation intervention with a norm-matched
orthogonal control on this same 500-question cohort.

The Claude usage record reports a sum of $2.8485 across list-cost fields. This
is recorded usage metadata, not an invoice or proof of an actual charge.
