# All-layer extraction check

**The local extraction pipeline works on this bounded development subset.
This is not a result about probe accuracy or genuine model confidence.**

We read 20 paired drafts, covering five task categories and input lengths of
94–729 tokens, using frozen unquantized Qwen2.5-1.5B. No new answers were generated.
The subset was selected by evenly spaced input-length ranks before extraction,
not by readout performance and not as a population-random sample.

| Check | Final-code result |
|---|---|
| Pooled states | 40 responses × 28 layers × 3 positions × 1,536 dimensions; all finite |
| Positions | Response mean; last ordinary response token; last prompt token |
| Identical-prompt negative control | Maximum state difference 0 |
| Seven additional padding tokens | Maximum state difference 0; sequence-NLL difference 0 |
| Cache-only replay | 40 cache hits, zero forwards, exactly identical arrays; 2.44 seconds |
| Total preflight time | 31.6 seconds, including model loading and cache replay |
| Observed memory | Process RSS high water 2.72 GiB; MPS driver maximum observed 4.17 GiB; not additive |
| Regression suite | 181 tests passed, including historical tests |

The first implementation took 42.1 seconds. A strict confident-first pair-order
guard was then added and the implementation-hashed extraction was revalidated;
the initial summary and final full aggregate are recorded separately. Only the
current final-code record should be used to describe the implementation now.

States, tokens and same-response NLL stay in ignored local caches. The public
[aggregate](../results/EXTRACTION_SANITY.json) contains no response bodies.
Source texts and all 50 individual content reviews remain private/pending.

An illustrative token-linear estimate for 2,000 responses at current length
quartiles is about 14–24 minutes. It excludes rewriting, review, additional
baselines and views; it is neither a confidence interval nor approval for a
full run. The original, slower measurement gives about 16–27 minutes.

**Next:** import actual user annotations, exclude changed/unclear/confounded
pairs, and decide the expansion budget. Then freeze source groups and unseen
rewrite instructions before the same-data layer-14 / equal-ensemble comparison.
There is no scientific probe result, SDT loss training or activation steering.
