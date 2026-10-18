# Short-Fact Paired-Confidence Pilot

## Decision

The next dataset pilot will use **short FEVER claims annotated `SUPPORTS` as
candidate factual cores**, not as confidence labels. The main dataset will not
be built from fixed phrases such as “I am confident” or from a single
`is`/`might be` template. Those constructions are useful controls, but they
would make a lexical shortcut too easy.

This phase validates the data construction before any activation extraction:

1. verify a small set of factual cores against their cited evidence;
2. create natural confident/hesitant versions that preserve each core fact;
3. review confidence contrast, factual equivalence and naturalness separately;
4. scale only if the review gate passes.

## What the source data contains

Each raw FEVER row contains a claim, a source-selection label and one or more
Wikipedia evidence locators:

```json
{
  "id": 177348,
  "label": "SUPPORTS",
  "claim": "<short factual statement>",
  "evidence": [[["<annotation id>", "<evidence id>", "<page>", "<sentence>"]]]
}
```

The local audit found 80,035 `SUPPORTS` rows and 68,936 exact-deduplicated
claims passing the mechanical 5–40-word, one-or-two-sentence screen. This is
only source capacity. The preview also contained generic claims, grammatical
errors, dated rankings and ambiguous entities, so source and evidence review
remain mandatory.

[Audit counts](results/short_factual_source_feasibility_v1.json)

## What prior work already covers

| Work | Relevant method | Consequence for this project |
|---|---|---|
| [Zhang et al., NAACL 2024](https://aclanthology.org/2024.naacl-long.91/) | Assigned half of 1,260 Baize dialogues to a more confident rewrite and half to a more tentative rewrite with GPT-3.5-turbo while asking it to preserve information. These were not matched confident/hesitant pairs for every source. | Confidence rewriting itself is not new. Our contribution cannot be merely asking a model for two tones. |
| [EMBER, NAACL 2025](https://aclanthology.org/2025.naacl-long.452/) | Added sampled strengthener, neutral or weakener phrases to 2,000 QA answers, used GPT-4o at temperature 0, and manually refined a small fraction. | Useful external lexical-control dataset, but too dependent on explicit cue phrases to be the main training set. |
| [Mapping Clinical Doubt, 2025 preprint](https://arxiv.org/abs/2511.22402) | Built certain/uncertain modal-word pairs and measured paired final-token activation differences across every layer, including Qwen2.5-0.5B-Instruct. It did not train the same linear confidence probe. | This is the closest mechanistic precedent. Our experiment must test natural full-response variation and generalization beyond the substituted cue family, not just reproduce modal-word sensitivity. |
| [PolyJudge-Uncertain, ACL SRW 2026](https://aclanthology.org/2026.acl-srw.33/) | Used deterministic assertive/hedged templates for short factual answers and found that a construction artifact changed an early result. | Fixed templates and apparent cue effects require explicit artifact checks and human review. |
| [Yona et al., EMNLP 2024](https://aclanthology.org/2024.emnlp-main.443/) | Distinguished internal confidence from decisive or hedged language. | The current label should remain **expressed epistemic confidence**, not calibrated truth or correctness. |

## Pilot configuration

### D0: data-quality canary

- **24 verified factual cores / 48 texts**.
- Four broad subject groups, two length bins and three facts per cell.
- One source page and one evidence sentence per fact; no repeated evidence
  sentence across facts.
- Exclude unstable rankings, underspecified entities, malformed originals,
  subjective claims and facts whose scope cannot be expressed in one or two
  sentences.
- Generate both versions together in one structured record:

```text
source_id
canonical_proposition
confident_text
hesitant_text
cue_family
preserved_atoms
```

- Freeze entities, relation, polarity, numbers, dates, units, quantifiers,
  attribution and causal direction.
- Vary epistemic commitment to that proposition. Do not append detachable
  comments such as “I stand firmly behind this answer” or “I am uncertain
  about this explanation.”
- Use four construction families, six pairs each: modal auxiliary, epistemic
  adverb, impersonal matrix clause, and bare assertion versus a natural
  `seems`/`appears` construction. Cap any exact confidence phrase at two uses.
- Prefer one sentence and 8–30 words. Target an absolute length difference of
  at most three words or a relative difference of at most 20%; counterbalance
  which version is longer.
- Use a low-variance writer setting. If the interface does not expose sampling
  controls, record the exact model, prompt and session instead of claiming a
  temperature value.

### Review gate

Reviewers see randomized A/B order and judge three questions independently:

1. Is the same factual proposition preserved?
2. Is the confidence contrast clear and in the intended direction?
3. Are both sentences natural standalone text?

Proceed only if at least **20 of 24 pairs** pass all three questions, no cue
family falls below **4 of 6**, and there is no entity, polarity, number, date or
scope drift. A failed gate means revising the recipe or writer, not selecting
only favorable examples after the fact.

### D1: representation test after D0 passes

- Expand to **100 factual cores / 200 texts**.
- Use Qwen2.5-1.5B-Instruct and cache the final factual-content token at all 28
  layers. Layer 14 remains a preregistered single-layer readout; the fixed
  all-layer ensemble is reported separately.
- Keep both versions of a fact, all paraphrases and facts from the same source
  group in the same split.
- Train a linear probe on expressed-confidence labels.
- Report paired ranking by layer alongside response length, answer
  likelihood, character/word TF-IDF and shuffled-label controls.
- Add a **cue-family holdout**: train without one construction family and test
  on that family. This is the central check that the probe learned more than a
  small vocabulary list.
- Evaluate EMBER as an external lexical diagnostic; do not mix it into the
  main FEVER training split.

## Claim boundary

A positive result would support a transferable linear readout of **expressed
confidence about preserved factual content**. It would not yet show calibrated
confidence, factual correctness, causal control, or a valid training loss.
