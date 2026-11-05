# Authenticated same-split baseline comparison

The completed result uses the exact frozen train/dev/internal-test/external
splits, with nested training prefixes 200/500/920.  Every text recipe was fit
only on its current training prefix.  Dev alone designated a comparator; the
internal test did not select a recipe, sign, threshold, or hyperparameter.
There were 193/193 internal-test pairs scored by every method, with zero
missing and zero exclusions.

## Internal-test paired accuracy

| Method | train 200 | train 500 | train 920 |
|---|---:|---:|---:|
| L14 probe | 99.48% | 99.48% | 99.48% |
| equal28 probe | 99.48% | 100.00% | 100.00% |
| char_wb3_5 answer | 95.34% | 96.37% | 96.89% |
| char_wb3_5 system+question+answer | 95.34% | 96.37% | 96.89% |
| char3_5 answer | 95.34% | 96.89% | 97.93% |
| char3_5 system+question+answer | 95.34% | 96.37% | 97.93% |
| word1_2 answer | 95.85% | 96.89% | 98.45% |
| word1_2 system+question+answer | 96.37% | 97.41% | 98.96% |

The dev-designated comparator was `char3_5__answer_only` at train sizes 200
and 500, and `char3_5__system_question_answer` at 920.  Against that frozen
designation, equal28's paired advantage was +4.15 points at 200 (95% grouped
bootstrap CI +1.05 to +7.29), +3.11 at 500 (+1.03 to +5.67), and +2.07 at 920
(+0.51 to +4.15).  L14's corresponding 920 advantage was +1.55 points, with
an interval crossing zero (-0.52 to +3.66).

`word1_2__system_question_answer` was descriptively the strongest text result
on the already-scored 920 internal test (191/193, 98.96%), but it was not the
dev-designated comparator and must not be presented as if selected in advance.
Relative to this descriptive test-best model, L14 was +0.52 points (CI -1.04
to +2.11) and equal28 was +1.04 points (CI 0.00 to +2.60).

## Deterministic length controls on the same 193 pairs

| Length rule | wins | ties | losses | tie-half accuracy |
|---|---:|---:|---:|---:|
| negative frozen Qwen response-token count | 99 | 0 | 94 | 51.30% |
| negative whitespace word count | 98 | 20 | 75 | 55.96% |
| negative character count | 104 | 5 | 84 | 55.18% |

No Qwen or other language-model forward was performed.  Token-length scores
reuse the counts already frozen in each evaluation row.  The core conclusion
is therefore narrower than the small-data Cue50 result: both probes remain far
above deterministic length, while a text classifier trained on 920 pairs
closes most of the ordering gap.  Equal28 retains a modest advantage over the
dev-designated text comparator; the corresponding L14 advantage is unresolved
at this sample size.  Dev and internal test are factual-explanation-only, and
external CF3 remains post-exposure robustness rather than untouched
confirmation.
