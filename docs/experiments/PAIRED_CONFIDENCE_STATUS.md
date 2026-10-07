# Paired Confidence Pilot v1

7 October 2026. **Phase A and Phase B are complete.**

**Result:** a simple layer-14 mean-difference readout ordered all 48 family-C
test pairs correctly across 24 unseen sources. Correct and deliberately wrong
answers both retained 100% ordering. This supports a candidate readout of
**expressed certainty** in this controlled paired dataset.

| Phase B endpoint: family C on test sources | Pair ordering |
|---|---:|
| Layer 14 post-response boundary | 100% |
| Layer 14 final content / response mean | 100% / 100% |
| Layer 23 boundary, exploratory | 72.9% |
| Text TF-IDF | 56.3% |
| Token/character length | 62.5% |
| Response sequence NLL | 31.3% |

Data and extraction gates passed, source splits were preserved, and the final
prompt negative control was exactly identical across each source's variants.
The model was frozen; there were no generation, NLI, or API inference calls.

**Limits:** these are deliberately written certainty cues. Twelve of 200 shuffled
directions also achieved perfect ordering; the all-success bootstrap interval
[1,1] is saturated. The result does not establish a unique confidence mechanism,
subjective confidence, factual belief strength, or an SDT-ready loss.

**Recommendation:** improve wording diversity and prepare a transfer test with
neutral-phrased QA or synthetic-document representations. Stop here pending that
next decision; this pilot did not perform steering or training.

Read [the preregistration](../../PAIRED_CONFIDENCE_PREREGISTRATION_V1.md) for the design
and [the results](../../reports/PAIRED_CONFIDENCE_RESULTS_V1.md) for completed evidence.
