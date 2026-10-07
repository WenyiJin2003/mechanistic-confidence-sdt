# Factual QA

[Repository](../../README.md) · [All question sets](../README.md)

[Dataset overview](README.md) · [Download all response rows (CSV)](responses.csv)

All 40 questions in this group. Responses are authored experiment stimuli. All stored variants and their primary scores are included.

- [factual_qa-000](#factual_qa-000): According to the passage, where had the Mongol capital been before Kublai moved it?
- [factual_qa-001](#factual_qa-001): According to the passage, following which MLS season was Chivas USA suspended?
- [factual_qa-002](#factual_qa-002): According to the passage, when did Prime Minister Wilson commit to some form of devolved legislature?
- [factual_qa-003](#factual_qa-003): According to the passage, what was the name of the first Huguenot outpost in South Carolina?
- [factual_qa-004](#factual_qa-004): According to the passage, which law imposed the national 55 mph speed limit in 1974?
- [factual_qa-005](#factual_qa-005): According to the passage, who wrote The Good War?
- [factual_qa-006](#factual_qa-006): According to the passage, when was Zhu Shijie born?
- [factual_qa-007](#factual_qa-007): According to the passage, which substance is electrolyzed to produce oxygen and hydrogen?
- [factual_qa-008](#factual_qa-008): According to the passage, mohammad Iqbal was what type of father to the State of Pakistan?
- [factual_qa-009](#factual_qa-009): According to the passage, who made up 19% of the student body in the 2012 Spring Quarter?
- [factual_qa-010](#factual_qa-010): According to the passage, what is one of the first responses the immune system has to infection?
- [factual_qa-011](#factual_qa-011): According to the passage, what do gravitational forces act between?
- [factual_qa-012](#factual_qa-012): According to the passage, what is the jelly-like middle material in cnidarians and ctenophores called?
- [factual_qa-013](#factual_qa-013): According to the passage, which month is the first in the year Parliament takes a two week vacation?
- [factual_qa-014](#factual_qa-014): According to the passage, how many museums are in Warsaw?
- [factual_qa-015](#factual_qa-015): According to the passage, how wide is the Rhine between Emmerich and Cleves?
- [factual_qa-016](#factual_qa-016): According to the passage, construction involves the translation of what?
- [factual_qa-017](#factual_qa-017): According to the passage, what sort of system releases the exhaust steam into the atmosphere?
- [factual_qa-018](#factual_qa-018): According to the passage, when is the Wianki festival held?
- [factual_qa-019](#factual_qa-019): According to the passage, along with electric motors, what type of engines superseded piston steam engines?
- [factual_qa-020](#factual_qa-020): According to the passage, on what railroad was Salamanca used?
- [factual_qa-021](#factual_qa-021): According to the passage, what will a pharmacist who passes the ambulatory pharmacist exam be called?
- [factual_qa-022](#factual_qa-022): According to the passage, what park is close to John Lennon street?
- [factual_qa-023](#factual_qa-023): According to the passage, what country was under the control of Norman barons?
- [factual_qa-024](#factual_qa-024): According to the passage, what is the name of Sky Q's broadband router?
- [factual_qa-025](#factual_qa-025): According to the passage, when was the French colony in modern day Brazil founded?
- [factual_qa-026](#factual_qa-026): According to the passage, what was the first British empire based on?
- [factual_qa-027](#factual_qa-027): According to the passage, when did Tamara marry a lawyer?
- [factual_qa-028](#factual_qa-028): According to the passage, between Brakel and what other city can the most landward tidal influence be detected?
- [factual_qa-029](#factual_qa-029): According to the passage, by what process can active immunity be generated in an artificial manner?
- [factual_qa-030](#factual_qa-030): According to the passage, which gender is more populous across all groups in Jacksonville?
- [factual_qa-031](#factual_qa-031): According to the passage, in the capabilities approach, economic growth and income are considered means rather than what?
- [factual_qa-032](#factual_qa-032): According to the passage, european imperialism was focused on what?
- [factual_qa-033](#factual_qa-033): According to the passage, in order to better understand the orientations of faults and folds, structural geologists do what with measurements of geological structures?
- [factual_qa-034](#factual_qa-034): According to the passage, which crime is defined almost identically across nations and jurisdictions?
- [factual_qa-035](#factual_qa-035): According to the passage, where was Ralph earl of?
- [factual_qa-036](#factual_qa-036): According to the passage, how many households had children under age 18 living in them?
- [factual_qa-037](#factual_qa-037): According to the passage, what type of treaty was the Lisbon Treaty?
- [factual_qa-038](#factual_qa-038): According to the passage, where do a majority of consultant pharmacists tend to work?
- [factual_qa-039](#factual_qa-039): According to the passage, who threw gold into the Rhine, according to legend?

## factual_qa-000

[Raw source](../../data/paired_confidence/source_items.jsonl#L1)

Question:

```text
According to the passage, where had the Mongol capital been before Kublai moved it?
```

Context:

```text
Kublai readied the move of the Mongol capital from Karakorum in Mongolia to Khanbaliq in 1264, constructing a new city near the former Jurchen capital Zhongdu, now modern Beijing, in 1266. In 1271, Kublai formally claimed the Mandate of Heaven and declared that 1272 was the first year of the Great Yuan (Chinese: 大元) in the style of a traditional Chinese dynasty. The name of the dynasty originated from the I Ching and describes the "origin of the universe" or a "primal force". Kublai proclaimed Khanbaliq the "Great Capital" or Daidu (Dadu, Chinese: 大都 in Chinese) of the dynasty. The era name was changed to Zhiyuan to herald a new era of Chinese history. The adoption of a dynastic name legitimized Mongol rule by integrating the government into the narrative of traditional Chinese political succession. Khublai evoked his public image as a sage emperor by following the rituals of Confucian propriety and ancestor veneration, while simultaneously retaining his roots as a leader from the steppes.
```

Correct key:

```text
Karakorum
```

Authored incorrect key:

```text
Samarkand
```

Original source: `squad_v2`, original ID `57286b003acd2414000df9c1`. Original benchmark split: SQuAD validation (cached Stage0 source). Correctness scope: supplied passage.

Phase A included: `true`; Phase A split: `validation`; Phase B split: `train`.

Saved key explanation:

```text
The passage names Karakorum, a different city.
```

### Rewrite family A

**correct, confident**

```text
I am confident the answer is "Karakorum".
```

Saved primary L14 boundary readout: `2.474796`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-000-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `293`; response stop (exclusive) `304`; final content `303`; boundary `304` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `34.476410`; mean token NLL: `3.134219`.

</details>

**correct, hedged**

```text
I am uncertain, but my answer is "Karakorum".
```

Saved primary L14 boundary readout: `0.225037`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-000-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L2) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `293`; response stop (exclusive) `306`; final content `305`; boundary `306` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `50.688957`; mean token NLL: `3.899151`.

</details>

**incorrect, confident**

```text
I am confident the answer is "Samarkand".
```

Saved primary L14 boundary readout: `1.923346`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-000-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L7) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `293`; response stop (exclusive) `304`; final content `303`; boundary `304` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `46.698330`; mean token NLL: `4.245303`.

</details>

**incorrect, hedged**

```text
I am uncertain, but my answer is "Samarkand".
```

Saved primary L14 boundary readout: `-0.218285`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-000-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L8) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `293`; response stop (exclusive) `306`; final content `305`; boundary `306` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `62.071579`; mean token NLL: `4.774737`.

</details>

### Rewrite family B

**correct, confident**

```text
I settle on "Karakorum" as my answer.
```

Saved primary L14 boundary readout: `2.077774`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-000-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L3) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `293`; response stop (exclusive) `305`; final content `304`; boundary `305` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `35.622055`; mean token NLL: `2.968505`.

</details>

**correct, hedged**

```text
I lean toward "Karakorum" as my answer.
```

Saved primary L14 boundary readout: `-0.776480`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-000-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L4) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `293`; response stop (exclusive) `305`; final content `304`; boundary `305` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `35.813103`; mean token NLL: `2.984425`.

</details>

**incorrect, confident**

```text
I settle on "Samarkand" as my answer.
```

Saved primary L14 boundary readout: `1.849353`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-000-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L9) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `293`; response stop (exclusive) `305`; final content `304`; boundary `305` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `46.577202`; mean token NLL: `3.881433`.

</details>

**incorrect, hedged**

```text
I lean toward "Samarkand" as my answer.
```

Saved primary L14 boundary readout: `-0.880773`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-000-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L10) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `293`; response stop (exclusive) `305`; final content `304`; boundary `305` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `46.013893`; mean token NLL: `3.834491`.

</details>

### Rewrite family C

**correct, confident**

```text
I would stake my position on "Karakorum".
```

Saved primary L14 boundary readout: `1.228004`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-000-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L5) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `293`; response stop (exclusive) `304`; final content `303`; boundary `304` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `40.338112`; mean token NLL: `3.667101`.

</details>

**correct, hedged**

```text
I would cautiously suggest "Karakorum".
```

Saved primary L14 boundary readout: `0.470530`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-000-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L6) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `293`; response stop (exclusive) `302`; final content `301`; boundary `302` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `36.926239`; mean token NLL: `4.102915`.

</details>

**incorrect, confident**

```text
I would stake my position on "Samarkand".
```

Saved primary L14 boundary readout: `1.012687`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-000-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L11) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `293`; response stop (exclusive) `304`; final content `303`; boundary `304` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `50.578156`; mean token NLL: `4.598014`.

</details>

**incorrect, hedged**

```text
I would cautiously suggest "Samarkand".
```

Saved primary L14 boundary readout: `0.179209`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-000-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L12) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `293`; response stop (exclusive) `302`; final content `301`; boundary `302` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `47.632710`; mean token NLL: `5.292523`.

</details>

[Back to question list](#factual-qa) · [Dataset overview](README.md)

## factual_qa-001

[Raw source](../../data/paired_confidence/source_items.jsonl#L2)

Question:

```text
According to the passage, following which MLS season was Chivas USA suspended?
```

Context:

```text
From 2005 to 2014, there were two Major League Soccer teams in Los Angeles — the LA Galaxy and Chivas USA — that both played at the StubHub Center and were local rivals. However, Chivas were suspended following the 2014 MLS season, with a second MLS team scheduled to return in 2018.
```

Correct key:

```text
2014
```

Authored incorrect key:

```text
2012
```

Original source: `squad_v2`, original ID `5706149552bb891400689882`. Original benchmark split: SQuAD validation (cached Stage0 source). Correctness scope: supplied passage.

Phase A included: `true`; Phase A split: `train`; Phase B split: `train`.

Saved key explanation:

```text
Chivas were suspended following2014, not2012.
```

### Rewrite family A

**correct, confident**

```text
I am sure the answer is "2014".
```

Saved primary L14 boundary readout: `2.381259`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-001-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L13) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `114`; response stop (exclusive) `126`; final content `125`; boundary `126` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `42.120075`; mean token NLL: `3.510006`.

</details>

**correct, hedged**

```text
I am not sure, but the answer is "2014".
```

Saved primary L14 boundary readout: `-0.337393`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-001-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L14) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `114`; response stop (exclusive) `129`; final content `128`; boundary `129` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `41.205650`; mean token NLL: `2.747043`.

</details>

**incorrect, confident**

```text
I am sure the answer is "2012".
```

Saved primary L14 boundary readout: `2.124283`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-001-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L19) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `114`; response stop (exclusive) `126`; final content `125`; boundary `126` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `47.322823`; mean token NLL: `3.943568`.

</details>

**incorrect, hedged**

```text
I am not sure, but the answer is "2012".
```

Saved primary L14 boundary readout: `-0.428367`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-001-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L20) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `114`; response stop (exclusive) `129`; final content `128`; boundary `129` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `44.427658`; mean token NLL: `2.961844`.

</details>

### Rewrite family B

**correct, confident**

```text
"2014" is my answer, and I stand by it.
```

Saved primary L14 boundary readout: `2.214613`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-001-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L15) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `114`; response stop (exclusive) `130`; final content `129`; boundary `130` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `60.119301`; mean token NLL: `3.757456`.

</details>

**correct, hedged**

```text
"2014" is my tentative answer.
```

Saved primary L14 boundary readout: `-0.332281`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-001-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L16) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `114`; response stop (exclusive) `125`; final content `124`; boundary `125` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `53.997238`; mean token NLL: `4.908840`.

</details>

**incorrect, confident**

```text
"2012" is my answer, and I stand by it.
```

Saved primary L14 boundary readout: `1.397950`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-001-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L21) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `114`; response stop (exclusive) `130`; final content `129`; boundary `130` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `56.828129`; mean token NLL: `3.551758`.

</details>

**incorrect, hedged**

```text
"2012" is my tentative answer.
```

Saved primary L14 boundary readout: `-0.492995`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-001-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L22) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `114`; response stop (exclusive) `125`; final content `124`; boundary `125` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `48.793625`; mean token NLL: `4.435784`.

</details>

### Rewrite family C

**correct, confident**

```text
"2014" is my definite conclusion.
```

Saved primary L14 boundary readout: `0.569637`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-001-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L17) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `114`; response stop (exclusive) `125`; final content `124`; boundary `125` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `65.541145`; mean token NLL: `5.958286`.

</details>

**correct, hedged**

```text
"2014" is my provisional conclusion.
```

Saved primary L14 boundary readout: `-0.528688`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-001-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L18) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `114`; response stop (exclusive) `125`; final content `124`; boundary `125` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `67.435440`; mean token NLL: `6.130495`.

</details>

**incorrect, confident**

```text
"2012" is my definite conclusion.
```

Saved primary L14 boundary readout: `0.192224`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-001-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L23) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `114`; response stop (exclusive) `125`; final content `124`; boundary `125` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `58.201912`; mean token NLL: `5.291083`.

</details>

**incorrect, hedged**

```text
"2012" is my provisional conclusion.
```

Saved primary L14 boundary readout: `-0.658963`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-001-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L24) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `114`; response stop (exclusive) `125`; final content `124`; boundary `125` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `58.500710`; mean token NLL: `5.318246`.

</details>

[Back to question list](#factual-qa) · [Dataset overview](README.md)

## factual_qa-002

[Raw source](../../data/paired_confidence/source_items.jsonl#L3)

Question:

```text
According to the passage, when did Prime Minister Wilson commit to some form of devolved legislature?
```

Context:

```text
During this time, the discovery of oil in the North Sea and the following "It's Scotland's oil" campaign of the Scottish National Party (SNP) resulted in rising support for Scottish independence, as well as the SNP. The party argued that the revenues from the oil were not benefitting Scotland as much as they should. The combined effect of these events led to Prime Minister Wilson committing his government to some form of devolved legislature in 1974. However, it was not until 1978 that final legislative proposals for a Scottish Assembly were passed by the United Kingdom Parliament.
```

Correct key:

```text
1974
```

Authored incorrect key:

```text
1972
```

Original source: `squad_v2`, original ID `572fad30a23a5019007fc870`. Original benchmark split: SQuAD validation (cached Stage0 source). Correctness scope: supplied passage.

Phase A included: `true`; Phase A split: `validation`; Phase B split: `train`.

Saved key explanation:

```text
Wilson's commitment is dated1974, not1972.
```

### Rewrite family A

**correct, confident**

```text
I have no doubt: the answer is "1974".
```

Saved primary L14 boundary readout: `3.433622`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-002-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L25) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `163`; response stop (exclusive) `177`; final content `176`; boundary `177` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `47.553970`; mean token NLL: `3.396712`.

</details>

**correct, hedged**

```text
I have some doubt: the answer is "1974".
```

Saved primary L14 boundary readout: `-2.173658`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-002-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L26) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `163`; response stop (exclusive) `177`; final content `176`; boundary `177` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `57.473106`; mean token NLL: `4.105222`.

</details>

**incorrect, confident**

```text
I have no doubt: the answer is "1972".
```

Saved primary L14 boundary readout: `3.203914`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-002-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L31) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `163`; response stop (exclusive) `177`; final content `176`; boundary `177` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `58.363289`; mean token NLL: `4.168807`.

</details>

**incorrect, hedged**

```text
I have some doubt: the answer is "1972".
```

Saved primary L14 boundary readout: `-2.454654`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-002-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L32) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `163`; response stop (exclusive) `177`; final content `176`; boundary `177` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `65.173973`; mean token NLL: `4.655284`.

</details>

### Rewrite family B

**correct, confident**

```text
"1974" is the answer I commit to.
```

Saved primary L14 boundary readout: `1.835439`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-002-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L27) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `163`; response stop (exclusive) `176`; final content `175`; boundary `176` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `56.996460`; mean token NLL: `4.384343`.

</details>

**correct, hedged**

```text
"1974" is the answer I lean toward.
```

Saved primary L14 boundary readout: `-0.141430`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-002-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L28) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `163`; response stop (exclusive) `176`; final content `175`; boundary `176` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `49.225887`; mean token NLL: `3.786607`.

</details>

**incorrect, confident**

```text
"1972" is the answer I commit to.
```

Saved primary L14 boundary readout: `1.532555`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-002-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L33) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `163`; response stop (exclusive) `176`; final content `175`; boundary `176` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `64.559708`; mean token NLL: `4.966131`.

</details>

**incorrect, hedged**

```text
"1972" is the answer I lean toward.
```

Saved primary L14 boundary readout: `-0.508909`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-002-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L34) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `163`; response stop (exclusive) `176`; final content `175`; boundary `176` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `56.834114`; mean token NLL: `4.371855`.

</details>

### Rewrite family C

**correct, confident**

```text
My conviction is that the answer is "1974".
```

Saved primary L14 boundary readout: `1.591340`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-002-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L29) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `163`; response stop (exclusive) `176`; final content `175`; boundary `176` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `35.147144`; mean token NLL: `2.703626`.

</details>

**correct, hedged**

```text
My guess is that the answer is "1974".
```

Saved primary L14 boundary readout: `0.958189`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-002-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L30) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `163`; response stop (exclusive) `176`; final content `175`; boundary `176` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `30.849079`; mean token NLL: `2.373006`.

</details>

**incorrect, confident**

```text
My conviction is that the answer is "1972".
```

Saved primary L14 boundary readout: `1.375352`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-002-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L35) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `163`; response stop (exclusive) `176`; final content `175`; boundary `176` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `44.568790`; mean token NLL: `3.428369`.

</details>

**incorrect, hedged**

```text
My guess is that the answer is "1972".
```

Saved primary L14 boundary readout: `0.567155`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-002-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L36) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `163`; response stop (exclusive) `176`; final content `175`; boundary `176` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `39.862099`; mean token NLL: `3.066315`.

</details>

[Back to question list](#factual-qa) · [Dataset overview](README.md)

## factual_qa-003

[Raw source](../../data/paired_confidence/source_items.jsonl#L4)

Question:

```text
According to the passage, what was the name of the first Huguenot outpost in South Carolina?
```

Context:

```text
French Huguenots made two attempts to establish a haven in North America. In 1562, naval officer Jean Ribault led an expedition that explored Florida and the present-day Southeastern U.S., and founded the outpost of Charlesfort on Parris Island, South Carolina. The Wars of Religion precluded a return voyage, and the outpost was abandoned. In 1564, Ribault's former lieutenant René Goulaine de Laudonnière launched a second voyage to build a colony; he established Fort Caroline in what is now Jacksonville, Florida. War at home again precluded a resupply mission, and the colony struggled. In 1565 the Spanish decided to enforce their claim to La Florida, and sent Pedro Menéndez de Avilés, who established the settlement of St. Augustine near Fort Caroline. Menéndez' forces routed the French and executed most of the Protestant captives.
```

Correct key:

```text
Charlesfort
```

Authored incorrect key:

```text
Jamestown
```

Original source: `squad_v2`, original ID `5710eb6fb654c5140001fa17`. Original benchmark split: SQuAD validation (cached Stage0 source). Correctness scope: supplied passage.

Phase A included: `true`; Phase A split: `test`; Phase B split: `train`.

Saved key explanation:

```text
Charlesfort is the named first South Carolina outpost.
```

### Rewrite family A

**correct, confident**

```text
With confidence, my answer is "Charlesfort".
```

Saved primary L14 boundary readout: `2.620328`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-003-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L37) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `236`; response stop (exclusive) `246`; final content `245`; boundary `246` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `42.160614`; mean token NLL: `4.216062`.

</details>

**correct, hedged**

```text
With some uncertainty, my answer is "Charlesfort".
```

Saved primary L14 boundary readout: `1.503780`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-003-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L38) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `236`; response stop (exclusive) `247`; final content `246`; boundary `247` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `46.707588`; mean token NLL: `4.246144`.

</details>

**incorrect, confident**

```text
With confidence, my answer is "Jamestown".
```

Saved primary L14 boundary readout: `2.157023`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-003-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L43) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `236`; response stop (exclusive) `247`; final content `246`; boundary `247` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `56.585167`; mean token NLL: `5.144106`.

</details>

**incorrect, hedged**

```text
With some uncertainty, my answer is "Jamestown".
```

Saved primary L14 boundary readout: `1.218083`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-003-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L44) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `236`; response stop (exclusive) `248`; final content `247`; boundary `248` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `59.454620`; mean token NLL: `4.954552`.

</details>

### Rewrite family B

**correct, confident**

```text
My answer is "Charlesfort"; I would give it without hesitation.
```

Saved primary L14 boundary readout: `2.379445`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-003-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L39) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `236`; response stop (exclusive) `250`; final content `249`; boundary `250` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `71.810104`; mean token NLL: `5.129293`.

</details>

**correct, hedged**

```text
My answer is "Charlesfort"; I would give it with hesitation.
```

Saved primary L14 boundary readout: `-0.972382`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-003-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L40) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `236`; response stop (exclusive) `250`; final content `249`; boundary `250` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `86.364677`; mean token NLL: `6.168906`.

</details>

**incorrect, confident**

```text
My answer is "Jamestown"; I would give it without hesitation.
```

Saved primary L14 boundary readout: `2.360889`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-003-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L45) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `236`; response stop (exclusive) `251`; final content `250`; boundary `251` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `78.896004`; mean token NLL: `5.259734`.

</details>

**incorrect, hedged**

```text
My answer is "Jamestown"; I would give it with hesitation.
```

Saved primary L14 boundary readout: `-0.899304`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-003-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L46) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `236`; response stop (exclusive) `251`; final content `250`; boundary `251` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `92.650772`; mean token NLL: `6.176718`.

</details>

### Rewrite family C

**correct, confident**

```text
I regard "Charlesfort" as established.
```

Saved primary L14 boundary readout: `-1.926685`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-003-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L41) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `236`; response stop (exclusive) `245`; final content `244`; boundary `245` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `42.552696`; mean token NLL: `4.728077`.

</details>

**correct, hedged**

```text
I regard "Charlesfort" as provisional.
```

Saved primary L14 boundary readout: `-2.213454`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-003-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L42) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `236`; response stop (exclusive) `245`; final content `244`; boundary `245` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `46.257011`; mean token NLL: `5.139668`.

</details>

**incorrect, confident**

```text
I regard "Jamestown" as established.
```

Saved primary L14 boundary readout: `-1.930067`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-003-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L47) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `236`; response stop (exclusive) `246`; final content `245`; boundary `246` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `53.568016`; mean token NLL: `5.356802`.

</details>

**incorrect, hedged**

```text
I regard "Jamestown" as provisional.
```

Saved primary L14 boundary readout: `-1.988529`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-003-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L48) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `236`; response stop (exclusive) `246`; final content `245`; boundary `246` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `55.508854`; mean token NLL: `5.550885`.

</details>

[Back to question list](#factual-qa) · [Dataset overview](README.md)

## factual_qa-004

[Raw source](../../data/paired_confidence/source_items.jsonl#L5)

Question:

```text
According to the passage, which law imposed the national 55 mph speed limit in 1974?
```

Context:

```text
To help reduce consumption, in 1974 a national maximum speed limit of 55 mph (about 88 km/h) was imposed through the Emergency Highway Energy Conservation Act. Development of the Strategic Petroleum Reserve began in 1975, and in 1977 the cabinet-level Department of Energy was created, followed by the National Energy Act of 1978.[citation needed] On November 28, 1995, Bill Clinton signed the National Highway Designation Act, ending the federal 55 mph (89 km/h) speed limit, allowing states to restore their prior maximum speed limit.
```

Correct key:

```text
Emergency Highway Energy Conservation Act
```

Authored incorrect key:

```text
National Highway Designation Act
```

Original source: `squad_v2`, original ID `57264efddd62a815002e8135`. Original benchmark split: SQuAD validation (cached Stage0 source). Correctness scope: supplied passage.

Phase A included: `true`; Phase A split: `train`; Phase B split: `train`.

Saved key explanation:

```text
The Energy Conservation Act imposed the limit; the distractor ended it.
```

### Rewrite family A

**correct, confident**

```text
I am confident the answer is "Emergency Highway Energy Conservation Act".
```

Saved primary L14 boundary readout: `2.454580`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-004-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L49) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `179`; response stop (exclusive) `192`; final content `191`; boundary `192` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `36.498611`; mean token NLL: `2.807585`.

</details>

**correct, hedged**

```text
I am uncertain, but my answer is "Emergency Highway Energy Conservation Act".
```

Saved primary L14 boundary readout: `-0.122619`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-004-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L50) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `179`; response stop (exclusive) `194`; final content `193`; boundary `194` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `53.058861`; mean token NLL: `3.537257`.

</details>

**incorrect, confident**

```text
I am confident the answer is "National Highway Designation Act".
```

Saved primary L14 boundary readout: `2.620753`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-004-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L55) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `179`; response stop (exclusive) `192`; final content `191`; boundary `192` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `42.588783`; mean token NLL: `3.276060`.

</details>

**incorrect, hedged**

```text
I am uncertain, but my answer is "National Highway Designation Act".
```

Saved primary L14 boundary readout: `0.201096`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-004-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L56) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `179`; response stop (exclusive) `194`; final content `193`; boundary `194` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `57.392593`; mean token NLL: `3.826173`.

</details>

### Rewrite family B

**correct, confident**

```text
I settle on "Emergency Highway Energy Conservation Act" as my answer.
```

Saved primary L14 boundary readout: `2.140252`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-004-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L51) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `179`; response stop (exclusive) `193`; final content `192`; boundary `193` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `37.234772`; mean token NLL: `2.659626`.

</details>

**correct, hedged**

```text
I lean toward "Emergency Highway Energy Conservation Act" as my answer.
```

Saved primary L14 boundary readout: `-0.766335`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-004-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L52) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `179`; response stop (exclusive) `193`; final content `192`; boundary `193` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `35.694756`; mean token NLL: `2.549625`.

</details>

**incorrect, confident**

```text
I settle on "National Highway Designation Act" as my answer.
```

Saved primary L14 boundary readout: `2.378466`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-004-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L57) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `179`; response stop (exclusive) `193`; final content `192`; boundary `193` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `42.747971`; mean token NLL: `3.053427`.

</details>

**incorrect, hedged**

```text
I lean toward "National Highway Designation Act" as my answer.
```

Saved primary L14 boundary readout: `-0.696769`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-004-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L58) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `179`; response stop (exclusive) `193`; final content `192`; boundary `193` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `39.467556`; mean token NLL: `2.819111`.

</details>

### Rewrite family C

**correct, confident**

```text
I would stake my position on "Emergency Highway Energy Conservation Act".
```

Saved primary L14 boundary readout: `0.876358`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-004-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L53) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `179`; response stop (exclusive) `192`; final content `191`; boundary `192` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `41.872932`; mean token NLL: `3.220995`.

</details>

**correct, hedged**

```text
I would cautiously suggest "Emergency Highway Energy Conservation Act".
```

Saved primary L14 boundary readout: `0.465877`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-004-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L54) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `179`; response stop (exclusive) `190`; final content `189`; boundary `190` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `38.571571`; mean token NLL: `3.506506`.

</details>

**incorrect, confident**

```text
I would stake my position on "National Highway Designation Act".
```

Saved primary L14 boundary readout: `1.305355`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-004-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L59) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `179`; response stop (exclusive) `192`; final content `191`; boundary `192` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `46.040260`; mean token NLL: `3.541559`.

</details>

**incorrect, hedged**

```text
I would cautiously suggest "National Highway Designation Act".
```

Saved primary L14 boundary readout: `0.884393`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-004-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L60) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `179`; response stop (exclusive) `190`; final content `189`; boundary `190` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `43.288818`; mean token NLL: `3.935347`.

</details>

[Back to question list](#factual-qa) · [Dataset overview](README.md)

## factual_qa-005

[Raw source](../../data/paired_confidence/source_items.jsonl#L6)

Question:

```text
According to the passage, who wrote The Good War?
```

Context:

```text
In literature, author of the New York Times bestseller Before I Fall Lauren Oliver, Pulitzer Prize winning novelist Philip Roth, Canadian-born Pulitzer Prize and Nobel Prize for Literature winning writer Saul Bellow, political philosopher, literary critic and author of the New York Times bestseller "The Closing of the American Mind" Allan Bloom, ''The Good War" author Studs Terkel, American writer, essayist, filmmaker, teacher, and political activist Susan Sontag, analytic philosopher and Stanford University Professor of Comparative Literature Richard Rorty, and American writer and satirist Kurt Vonnegut are notable alumni.
```

Correct key:

```text
Studs Terkel
```

Authored incorrect key:

```text
Philip Roth
```

Original source: `squad_v2`, original ID `57286bf84b864d19001649d5`. Original benchmark split: SQuAD validation (cached Stage0 source). Correctness scope: supplied passage.

Phase A included: `true`; Phase A split: `train`; Phase B split: `train`.

Saved key explanation:

```text
Studs Terkel is the named author of The Good War.
```

### Rewrite family A

**correct, confident**

```text
I am sure the answer is "Studs Terkel".
```

Saved primary L14 boundary readout: `2.658376`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-005-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L61) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `157`; response stop (exclusive) `169`; final content `168`; boundary `169` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `38.434155`; mean token NLL: `3.202846`.

</details>

**correct, hedged**

```text
I am not sure, but the answer is "Studs Terkel".
```

Saved primary L14 boundary readout: `0.242826`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-005-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L62) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `157`; response stop (exclusive) `172`; final content `171`; boundary `172` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `39.875099`; mean token NLL: `2.658340`.

</details>

**incorrect, confident**

```text
I am sure the answer is "Philip Roth".
```

Saved primary L14 boundary readout: `2.483103`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-005-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L67) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `157`; response stop (exclusive) `167`; final content `166`; boundary `167` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `47.068779`; mean token NLL: `4.706878`.

</details>

**incorrect, hedged**

```text
I am not sure, but the answer is "Philip Roth".
```

Saved primary L14 boundary readout: `-0.309906`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-005-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L68) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `157`; response stop (exclusive) `170`; final content `169`; boundary `170` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `49.264946`; mean token NLL: `3.789611`.

</details>

### Rewrite family B

**correct, confident**

```text
"Studs Terkel" is my answer, and I stand by it.
```

Saved primary L14 boundary readout: `2.458335`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-005-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L63) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `157`; response stop (exclusive) `173`; final content `172`; boundary `173` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `48.235394`; mean token NLL: `3.014712`.

</details>

**correct, hedged**

```text
"Studs Terkel" is my tentative answer.
```

Saved primary L14 boundary readout: `0.023469`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-005-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L64) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `157`; response stop (exclusive) `168`; final content `167`; boundary `168` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `42.640278`; mean token NLL: `3.876389`.

</details>

**incorrect, confident**

```text
"Philip Roth" is my answer, and I stand by it.
```

Saved primary L14 boundary readout: `2.433568`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-005-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L69) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `157`; response stop (exclusive) `171`; final content `170`; boundary `171` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `57.167027`; mean token NLL: `4.083359`.

</details>

**incorrect, hedged**

```text
"Philip Roth" is my tentative answer.
```

Saved primary L14 boundary readout: `0.303124`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-005-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L70) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `157`; response stop (exclusive) `166`; final content `165`; boundary `166` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `49.237564`; mean token NLL: `5.470840`.

</details>

### Rewrite family C

**correct, confident**

```text
"Studs Terkel" is my definite conclusion.
```

Saved primary L14 boundary readout: `0.428887`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-005-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L65) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `157`; response stop (exclusive) `168`; final content `167`; boundary `168` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `52.802162`; mean token NLL: `4.800197`.

</details>

**correct, hedged**

```text
"Studs Terkel" is my provisional conclusion.
```

Saved primary L14 boundary readout: `-0.626794`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-005-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L66) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `157`; response stop (exclusive) `168`; final content `167`; boundary `168` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `49.739128`; mean token NLL: `4.521739`.

</details>

**incorrect, confident**

```text
"Philip Roth" is my definite conclusion.
```

Saved primary L14 boundary readout: `0.804503`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-005-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L71) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `157`; response stop (exclusive) `166`; final content `165`; boundary `166` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `60.857277`; mean token NLL: `6.761919`.

</details>

**incorrect, hedged**

```text
"Philip Roth" is my provisional conclusion.
```

Saved primary L14 boundary readout: `-0.269364`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-005-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L72) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `157`; response stop (exclusive) `166`; final content `165`; boundary `166` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `57.241821`; mean token NLL: `6.360202`.

</details>

[Back to question list](#factual-qa) · [Dataset overview](README.md)

## factual_qa-006

[Raw source](../../data/paired_confidence/source_items.jsonl#L7)

Question:

```text
According to the passage, when was Zhu Shijie born?
```

Context:

```text
Advances in polynomial algebra were made by mathematicians during the Yuan era. The mathematician Zhu Shijie (1249–1314) solved simultaneous equations with up to four unknowns using a rectangular array of coefficients, equivalent to modern matrices. Zhu used a method of elimination to reduce the simultaneous equations to a single equation with only one unknown. His method is described in the Jade Mirror of the Four Unknowns, written in 1303. The opening pages contain a diagram of Pascal's triangle. The summation of a finite arithmetic series is also covered in the book.
```

Correct key:

```text
1249
```

Authored incorrect key:

```text
1259
```

Original source: `squad_v2`, original ID `5728804b4b864d1900164a46`. Original benchmark split: SQuAD validation (cached Stage0 source). Correctness scope: supplied passage.

Phase A included: `true`; Phase A split: `test`; Phase B split: `train`.

Saved key explanation:

```text
Zhu Shijie's lifespan begins in1249.
```

### Rewrite family A

**correct, confident**

```text
I have no doubt: the answer is "1249".
```

Saved primary L14 boundary readout: `3.669281`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-006-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L73) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `157`; response stop (exclusive) `171`; final content `170`; boundary `171` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `43.945770`; mean token NLL: `3.138983`.

</details>

**correct, hedged**

```text
I have some doubt: the answer is "1249".
```

Saved primary L14 boundary readout: `-2.596042`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-006-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L74) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `157`; response stop (exclusive) `171`; final content `170`; boundary `171` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `53.419960`; mean token NLL: `3.815711`.

</details>

**incorrect, confident**

```text
I have no doubt: the answer is "1259".
```

Saved primary L14 boundary readout: `3.521488`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-006-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L79) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `157`; response stop (exclusive) `171`; final content `170`; boundary `171` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `56.504181`; mean token NLL: `4.036013`.

</details>

**incorrect, hedged**

```text
I have some doubt: the answer is "1259".
```

Saved primary L14 boundary readout: `-2.766577`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-006-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L80) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `157`; response stop (exclusive) `171`; final content `170`; boundary `171` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `62.636410`; mean token NLL: `4.474029`.

</details>

### Rewrite family B

**correct, confident**

```text
"1249" is the answer I commit to.
```

Saved primary L14 boundary readout: `2.155606`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-006-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L75) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `157`; response stop (exclusive) `170`; final content `169`; boundary `170` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `57.517406`; mean token NLL: `4.424416`.

</details>

**correct, hedged**

```text
"1249" is the answer I lean toward.
```

Saved primary L14 boundary readout: `-0.011824`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-006-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L76) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `157`; response stop (exclusive) `170`; final content `169`; boundary `170` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `55.684212`; mean token NLL: `4.283401`.

</details>

**incorrect, confident**

```text
"1259" is the answer I commit to.
```

Saved primary L14 boundary readout: `1.881745`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-006-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L81) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `157`; response stop (exclusive) `170`; final content `169`; boundary `170` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `66.290031`; mean token NLL: `5.099233`.

</details>

**incorrect, hedged**

```text
"1259" is the answer I lean toward.
```

Saved primary L14 boundary readout: `-0.306651`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-006-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L82) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `157`; response stop (exclusive) `170`; final content `169`; boundary `170` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `64.072403`; mean token NLL: `4.928647`.

</details>

### Rewrite family C

**correct, confident**

```text
My conviction is that the answer is "1249".
```

Saved primary L14 boundary readout: `1.529166`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-006-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L77) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `157`; response stop (exclusive) `170`; final content `169`; boundary `170` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `36.080338`; mean token NLL: `2.775411`.

</details>

**correct, hedged**

```text
My guess is that the answer is "1249".
```

Saved primary L14 boundary readout: `0.933712`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-006-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L78) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `157`; response stop (exclusive) `170`; final content `169`; boundary `170` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `32.995186`; mean token NLL: `2.538091`.

</details>

**incorrect, confident**

```text
My conviction is that the answer is "1259".
```

Saved primary L14 boundary readout: `1.305899`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-006-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L83) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `157`; response stop (exclusive) `170`; final content `169`; boundary `170` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `46.590202`; mean token NLL: `3.583862`.

</details>

**incorrect, hedged**

```text
My guess is that the answer is "1259".
```

Saved primary L14 boundary readout: `0.609798`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-006-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L84) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `157`; response stop (exclusive) `170`; final content `169`; boundary `170` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `42.654369`; mean token NLL: `3.281105`.

</details>

[Back to question list](#factual-qa) · [Dataset overview](README.md)

## factual_qa-007

[Raw source](../../data/paired_confidence/source_items.jsonl#L8)

Question:

```text
According to the passage, which substance is electrolyzed to produce oxygen and hydrogen?
```

Context:

```text
Oxygen gas can also be produced through electrolysis of water into molecular oxygen and hydrogen. DC electricity must be used: if AC is used, the gases in each limb consist of hydrogen and oxygen in the explosive ratio 2:1. Contrary to popular belief, the 2:1 ratio observed in the DC electrolysis of acidified water does not prove that the empirical formula of water is H2O unless certain assumptions are made about the molecular formulae of hydrogen and oxygen themselves. A similar method is the electrocatalytic O
2 evolution from oxides and oxoacids. Chemical catalysts can be used as well, such as in chemical oxygen generators or oxygen candles that are used as part of the life-support equipment on submarines, and are still part of standard equipment on commercial airliners in case of depressurization emergencies. Another air separation technology involves forcing air to dissolve through ceramic membranes based on zirconium dioxide by either high pressure or an electric current, to produce nearly pure O
2 gas.
```

Correct key:

```text
water
```

Authored incorrect key:

```text
helium
```

Original source: `squad_v2`, original ID `571ccfbadd7acb1400e4c164`. Original benchmark split: SQuAD validation (cached Stage0 source). Correctness scope: supplied passage.

Phase A included: `true`; Phase A split: `train`; Phase B split: `train`.

Saved key explanation:

```text
The passage specifies electrolysis of water, not helium.
```

### Rewrite family A

**correct, confident**

```text
With confidence, my answer is "water".
```

Saved primary L14 boundary readout: `2.274239`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-007-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L85) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `245`; response stop (exclusive) `254`; final content `253`; boundary `254` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `45.547123`; mean token NLL: `5.060791`.

</details>

**correct, hedged**

```text
With some uncertainty, my answer is "water".
```

Saved primary L14 boundary readout: `1.332006`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-007-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L86) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `245`; response stop (exclusive) `255`; final content `254`; boundary `255` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `40.420830`; mean token NLL: `4.042083`.

</details>

**incorrect, confident**

```text
With confidence, my answer is "helium".
```

Saved primary L14 boundary readout: `1.886414`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-007-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L91) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `245`; response stop (exclusive) `255`; final content `254`; boundary `255` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `58.271820`; mean token NLL: `5.827182`.

</details>

**incorrect, hedged**

```text
With some uncertainty, my answer is "helium".
```

Saved primary L14 boundary readout: `1.023090`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-007-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L92) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `245`; response stop (exclusive) `256`; final content `255`; boundary `256` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `52.212639`; mean token NLL: `4.746603`.

</details>

### Rewrite family B

**correct, confident**

```text
My answer is "water"; I would give it without hesitation.
```

Saved primary L14 boundary readout: `2.241994`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-007-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L87) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `245`; response stop (exclusive) `258`; final content `257`; boundary `258` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `67.698776`; mean token NLL: `5.207598`.

</details>

**correct, hedged**

```text
My answer is "water"; I would give it with hesitation.
```

Saved primary L14 boundary readout: `-0.701973`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-007-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L88) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `245`; response stop (exclusive) `258`; final content `257`; boundary `258` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `80.520058`; mean token NLL: `6.193851`.

</details>

**incorrect, confident**

```text
My answer is "helium"; I would give it without hesitation.
```

Saved primary L14 boundary readout: `2.012000`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-007-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L93) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `245`; response stop (exclusive) `259`; final content `258`; boundary `259` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `78.963104`; mean token NLL: `5.640222`.

</details>

**incorrect, hedged**

```text
My answer is "helium"; I would give it with hesitation.
```

Saved primary L14 boundary readout: `-0.691773`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-007-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L94) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `245`; response stop (exclusive) `259`; final content `258`; boundary `259` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `88.810410`; mean token NLL: `6.343601`.

</details>

### Rewrite family C

**correct, confident**

```text
I regard "water" as established.
```

Saved primary L14 boundary readout: `-0.962173`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-007-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L89) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `245`; response stop (exclusive) `253`; final content `252`; boundary `253` (`151645`, `<|im_end|>`). Response tokens: `8`.

Sequence NLL: `45.104279`; mean token NLL: `5.638035`.

</details>

**correct, hedged**

```text
I regard "water" as provisional.
```

Saved primary L14 boundary readout: `-1.564582`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-007-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L90) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `245`; response stop (exclusive) `253`; final content `252`; boundary `253` (`151645`, `<|im_end|>`). Response tokens: `8`.

Sequence NLL: `46.821007`; mean token NLL: `5.852626`.

</details>

**incorrect, confident**

```text
I regard "helium" as established.
```

Saved primary L14 boundary readout: `-0.741167`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-007-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L95) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `245`; response stop (exclusive) `254`; final content `253`; boundary `254` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `51.869812`; mean token NLL: `5.763312`.

</details>

**incorrect, hedged**

```text
I regard "helium" as provisional.
```

Saved primary L14 boundary readout: `-1.367170`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-007-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L96) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `245`; response stop (exclusive) `254`; final content `253`; boundary `254` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `55.757133`; mean token NLL: `6.195237`.

</details>

[Back to question list](#factual-qa) · [Dataset overview](README.md)

## factual_qa-008

[Raw source](../../data/paired_confidence/source_items.jsonl#L9)

Question:

```text
According to the passage, mohammad Iqbal was what type of father to the State of Pakistan?
```

Context:

```text
The views of Ali Shariati, ideologue of the Iranian Revolution, had resemblance with Mohammad Iqbal, ideological father of the State of Pakistan, but Khomeini's beliefs is perceived to be placed somewhere between beliefs of Sunni Islamic thinkers like Mawdudi and Qutb. He believed that complete imitation of the Prophet Mohammad and his successors such as Ali for restoration of Sharia law was essential to Islam, that many secular, Westernizing Muslims were actually agents of the West serving Western interests, and that the acts such as "plundering" of Muslim lands was part of a long-term conspiracy against Islam by the Western governments.
```

Correct key:

```text
ideological
```

Authored incorrect key:

```text
biological
```

Original source: `squad_v2`, original ID `5730088e947a6a140053cfad`. Original benchmark split: SQuAD validation (cached Stage0 source). Correctness scope: supplied passage.

Phase A included: `false`; Phase A split: `not included`; Phase B split: `validation`.

Saved key explanation:

```text
Iqbal is described as ideological father.
```

### Rewrite family A

**correct, confident**

```text
I am confident the answer is "ideological".
```

Saved primary L14 boundary readout: `2.530626`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-008-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L97) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `174`; response stop (exclusive) `184`; final content `183`; boundary `184` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `34.388817`; mean token NLL: `3.438882`.

</details>

**correct, hedged**

```text
I am uncertain, but my answer is "ideological".
```

Saved primary L14 boundary readout: `-0.360488`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-008-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L98) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `174`; response stop (exclusive) `186`; final content `185`; boundary `186` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `50.788773`; mean token NLL: `4.232398`.

</details>

**incorrect, confident**

```text
I am confident the answer is "biological".
```

Saved primary L14 boundary readout: `2.178439`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-008-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L103) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `174`; response stop (exclusive) `184`; final content `183`; boundary `184` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `47.878922`; mean token NLL: `4.787892`.

</details>

**incorrect, hedged**

```text
I am uncertain, but my answer is "biological".
```

Saved primary L14 boundary readout: `-0.680360`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-008-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L104) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `174`; response stop (exclusive) `186`; final content `185`; boundary `186` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `61.637142`; mean token NLL: `5.136428`.

</details>

### Rewrite family B

**correct, confident**

```text
I settle on "ideological" as my answer.
```

Saved primary L14 boundary readout: `1.463604`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-008-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L99) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `174`; response stop (exclusive) `185`; final content `184`; boundary `185` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `42.380348`; mean token NLL: `3.852759`.

</details>

**correct, hedged**

```text
I lean toward "ideological" as my answer.
```

Saved primary L14 boundary readout: `-0.863873`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-008-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L100) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `174`; response stop (exclusive) `185`; final content `184`; boundary `185` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `39.825756`; mean token NLL: `3.620523`.

</details>

**incorrect, confident**

```text
I settle on "biological" as my answer.
```

Saved primary L14 boundary readout: `1.255839`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-008-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L105) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `174`; response stop (exclusive) `185`; final content `184`; boundary `185` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `54.145512`; mean token NLL: `4.922319`.

</details>

**incorrect, hedged**

```text
I lean toward "biological" as my answer.
```

Saved primary L14 boundary readout: `-0.852025`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-008-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L106) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `174`; response stop (exclusive) `185`; final content `184`; boundary `185` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `49.275543`; mean token NLL: `4.479595`.

</details>

### Rewrite family C

**correct, confident**

```text
I would stake my position on "ideological".
```

Saved primary L14 boundary readout: `0.927339`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-008-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L101) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `174`; response stop (exclusive) `184`; final content `183`; boundary `184` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `36.895340`; mean token NLL: `3.689534`.

</details>

**correct, hedged**

```text
I would cautiously suggest "ideological".
```

Saved primary L14 boundary readout: `0.777036`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-008-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L102) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `174`; response stop (exclusive) `182`; final content `181`; boundary `182` (`151645`, `<|im_end|>`). Response tokens: `8`.

Sequence NLL: `32.694054`; mean token NLL: `4.086757`.

</details>

**incorrect, confident**

```text
I would stake my position on "biological".
```

Saved primary L14 boundary readout: `0.782198`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-008-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L107) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `174`; response stop (exclusive) `184`; final content `183`; boundary `184` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `47.398804`; mean token NLL: `4.739881`.

</details>

**incorrect, hedged**

```text
I would cautiously suggest "biological".
```

Saved primary L14 boundary readout: `0.557574`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-008-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L108) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `174`; response stop (exclusive) `182`; final content `181`; boundary `182` (`151645`, `<|im_end|>`). Response tokens: `8`.

Sequence NLL: `44.761574`; mean token NLL: `5.595197`.

</details>

[Back to question list](#factual-qa) · [Dataset overview](README.md)

## factual_qa-009

[Raw source](../../data/paired_confidence/source_items.jsonl#L10)

Question:

```text
According to the passage, who made up 19% of the student body in the 2012 Spring Quarter?
```

Context:

```text
In the fall quarter of 2014, the University of Chicago enrolled 5,792 students in the College, 3,468 students in its four graduate divisions, 5,984 students in its professional schools, and 15,244 students overall. In the 2012 Spring Quarter, international students comprised almost 19% of the overall study body, over 26% of students were domestic ethnic minorities, and about 44% of enrolled students were female. Admissions to the University of Chicago is highly selective. The middle 50% band of SAT scores for the undergraduate class of 2015, excluding the writing section, was 1420–1530, the average MCAT score for entering students in the Pritzker School of Medicine in 2011 was 36, and the median LSAT score for entering students in the Law School in 2011 was 171. In 2015, the College of the University of Chicago had an acceptance rate of 7.8% for the Class of 2019, the lowest in the college's history.
```

Correct key:

```text
international students
```

Authored incorrect key:

```text
female students
```

Original source: `squad_v2`, original ID `572863363acd2414000df989`. Original benchmark split: SQuAD validation (cached Stage0 source). Correctness scope: supplied passage.

Phase A included: `false`; Phase A split: `not included`; Phase B split: `train`.

Saved key explanation:

```text
International students comprise19%; female students44%.
```

### Rewrite family A

**correct, confident**

```text
I am sure the answer is "international students".
```

Saved primary L14 boundary readout: `1.462351`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-009-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L109) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `303`; response stop (exclusive) `313`; final content `312`; boundary `313` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `35.550621`; mean token NLL: `3.555062`.

</details>

**correct, hedged**

```text
I am not sure, but the answer is "international students".
```

Saved primary L14 boundary readout: `-1.657056`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-009-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L110) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `303`; response stop (exclusive) `316`; final content `315`; boundary `316` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `36.285057`; mean token NLL: `2.791158`.

</details>

**incorrect, confident**

```text
I am sure the answer is "female students".
```

Saved primary L14 boundary readout: `1.043713`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-009-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L115) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `303`; response stop (exclusive) `313`; final content `312`; boundary `313` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `53.866173`; mean token NLL: `5.386617`.

</details>

**incorrect, hedged**

```text
I am not sure, but the answer is "female students".
```

Saved primary L14 boundary readout: `-1.928979`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-009-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L116) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `303`; response stop (exclusive) `316`; final content `315`; boundary `316` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `53.022148`; mean token NLL: `4.078627`.

</details>

### Rewrite family B

**correct, confident**

```text
"international students" is my answer, and I stand by it.
```

Saved primary L14 boundary readout: `1.141330`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-009-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L111) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `303`; response stop (exclusive) `317`; final content `316`; boundary `317` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `65.623383`; mean token NLL: `4.687385`.

</details>

**correct, hedged**

```text
"international students" is my tentative answer.
```

Saved primary L14 boundary readout: `-1.180318`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-009-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L112) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `303`; response stop (exclusive) `312`; final content `311`; boundary `312` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `57.495911`; mean token NLL: `6.388434`.

</details>

**incorrect, confident**

```text
"female students" is my answer, and I stand by it.
```

Saved primary L14 boundary readout: `0.999971`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-009-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L117) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `303`; response stop (exclusive) `317`; final content `316`; boundary `317` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `81.289238`; mean token NLL: `5.806374`.

</details>

**incorrect, hedged**

```text
"female students" is my tentative answer.
```

Saved primary L14 boundary readout: `-1.072497`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-009-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L118) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `303`; response stop (exclusive) `312`; final content `311`; boundary `312` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `72.685432`; mean token NLL: `8.076159`.

</details>

### Rewrite family C

**correct, confident**

```text
"international students" is my definite conclusion.
```

Saved primary L14 boundary readout: `-0.268802`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-009-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L113) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `303`; response stop (exclusive) `312`; final content `311`; boundary `312` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `68.711632`; mean token NLL: `7.634626`.

</details>

**correct, hedged**

```text
"international students" is my provisional conclusion.
```

Saved primary L14 boundary readout: `-1.467050`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-009-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L114) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `303`; response stop (exclusive) `312`; final content `311`; boundary `312` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `67.678474`; mean token NLL: `7.519831`.

</details>

**incorrect, confident**

```text
"female students" is my definite conclusion.
```

Saved primary L14 boundary readout: `-0.261698`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-009-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L119) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `303`; response stop (exclusive) `312`; final content `311`; boundary `312` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `82.373138`; mean token NLL: `9.152571`.

</details>

**incorrect, hedged**

```text
"female students" is my provisional conclusion.
```

Saved primary L14 boundary readout: `-1.339116`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-009-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L120) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `303`; response stop (exclusive) `312`; final content `311`; boundary `312` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `82.012985`; mean token NLL: `9.112554`.

</details>

[Back to question list](#factual-qa) · [Dataset overview](README.md)

## factual_qa-010

[Raw source](../../data/paired_confidence/source_items.jsonl#L11)

Question:

```text
According to the passage, what is one of the first responses the immune system has to infection?
```

Context:

```text
Inflammation is one of the first responses of the immune system to infection. The symptoms of inflammation are redness, swelling, heat, and pain, which are caused by increased blood flow into tissue. Inflammation is produced by eicosanoids and cytokines, which are released by injured or infected cells. Eicosanoids include prostaglandins that produce fever and the dilation of blood vessels associated with inflammation, and leukotrienes that attract certain white blood cells (leukocytes). Common cytokines include interleukins that are responsible for communication between white blood cells; chemokines that promote chemotaxis; and interferons that have anti-viral effects, such as shutting down protein synthesis in the host cell. Growth factors and cytotoxic factors may also be released. These cytokines and other chemicals recruit immune cells to the site of infection and promote healing of any damaged tissue following the removal of pathogens.
```

Correct key:

```text
Inflammation
```

Authored incorrect key:

```text
photosynthesis
```

Original source: `squad_v2`, original ID `572900f73f37b31900477f69`. Original benchmark split: SQuAD validation (cached Stage0 source). Correctness scope: supplied passage.

Phase A included: `false`; Phase A split: `not included`; Phase B split: `train`.

Saved key explanation:

```text
Inflammation is the immune response; photosynthesis is not an immune response.
```

### Rewrite family A

**correct, confident**

```text
I have no doubt: the answer is "Inflammation".
```

Saved primary L14 boundary readout: `3.241307`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-010-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L121) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `229`; response stop (exclusive) `242`; final content `241`; boundary `242` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `41.094521`; mean token NLL: `3.161117`.

</details>

**correct, hedged**

```text
I have some doubt: the answer is "Inflammation".
```

Saved primary L14 boundary readout: `-2.907689`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-010-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L122) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `229`; response stop (exclusive) `242`; final content `241`; boundary `242` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `48.183811`; mean token NLL: `3.706447`.

</details>

**incorrect, confident**

```text
I have no doubt: the answer is "photosynthesis".
```

Saved primary L14 boundary readout: `1.993428`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-010-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L127) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `229`; response stop (exclusive) `241`; final content `240`; boundary `241` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `56.389507`; mean token NLL: `4.699126`.

</details>

**incorrect, hedged**

```text
I have some doubt: the answer is "photosynthesis".
```

Saved primary L14 boundary readout: `-3.778160`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-010-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L128) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `229`; response stop (exclusive) `241`; final content `240`; boundary `241` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `59.372276`; mean token NLL: `4.947690`.

</details>

### Rewrite family B

**correct, confident**

```text
"Inflammation" is the answer I commit to.
```

Saved primary L14 boundary readout: `1.550516`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-010-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L123) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `229`; response stop (exclusive) `240`; final content `239`; boundary `240` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `43.699875`; mean token NLL: `3.972716`.

</details>

**correct, hedged**

```text
"Inflammation" is the answer I lean toward.
```

Saved primary L14 boundary readout: `0.239705`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-010-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L124) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `229`; response stop (exclusive) `240`; final content `239`; boundary `240` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `42.115623`; mean token NLL: `3.828693`.

</details>

**incorrect, confident**

```text
"photosynthesis" is the answer I commit to.
```

Saved primary L14 boundary readout: `0.794994`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-010-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L129) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `229`; response stop (exclusive) `240`; final content `239`; boundary `240` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `63.785091`; mean token NLL: `5.798645`.

</details>

**incorrect, hedged**

```text
"photosynthesis" is the answer I lean toward.
```

Saved primary L14 boundary readout: `-1.196989`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-010-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L130) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `229`; response stop (exclusive) `240`; final content `239`; boundary `240` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `60.946499`; mean token NLL: `5.540591`.

</details>

### Rewrite family C

**correct, confident**

```text
My conviction is that the answer is "Inflammation".
```

Saved primary L14 boundary readout: `1.242776`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-010-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L125) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `229`; response stop (exclusive) `241`; final content `240`; boundary `241` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `32.806435`; mean token NLL: `2.733870`.

</details>

**correct, hedged**

```text
My guess is that the answer is "Inflammation".
```

Saved primary L14 boundary readout: `0.662140`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-010-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L126) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `229`; response stop (exclusive) `241`; final content `240`; boundary `241` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `30.386381`; mean token NLL: `2.532198`.

</details>

**incorrect, confident**

```text
My conviction is that the answer is "photosynthesis".
```

Saved primary L14 boundary readout: `0.397826`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-010-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L131) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `229`; response stop (exclusive) `240`; final content `239`; boundary `240` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `48.653866`; mean token NLL: `4.423079`.

</details>

**incorrect, hedged**

```text
My guess is that the answer is "photosynthesis".
```

Saved primary L14 boundary readout: `-0.213200`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-010-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L132) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `229`; response stop (exclusive) `240`; final content `239`; boundary `240` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `44.326275`; mean token NLL: `4.029661`.

</details>

[Back to question list](#factual-qa) · [Dataset overview](README.md)

## factual_qa-011

[Raw source](../../data/paired_confidence/source_items.jsonl#L12)

Question:

```text
According to the passage, what do gravitational forces act between?
```

Context:

```text
All of the forces in the universe are based on four fundamental interactions. The strong and weak forces are nuclear forces that act only at very short distances, and are responsible for the interactions between subatomic particles, including nucleons and compound nuclei. The electromagnetic force acts between electric charges, and the gravitational force acts between masses. All other forces in nature derive from these four fundamental interactions. For example, friction is a manifestation of the electromagnetic force acting between the atoms of two surfaces, and the Pauli exclusion principle, which does not permit atoms to pass through each other. Similarly, the forces in springs, modeled by Hooke's law, are the result of electromagnetic forces and the Exclusion Principle acting together to return an object to its equilibrium position. Centrifugal forces are acceleration forces that arise simply from the acceleration of rotating frames of reference.:12-11:359
```

Correct key:

```text
masses
```

Authored incorrect key:

```text
electric charges
```

Original source: `squad_v2`, original ID `5737804dc3c5551400e51f12`. Original benchmark split: SQuAD validation (cached Stage0 source). Correctness scope: supplied passage.

Phase A included: `false`; Phase A split: `not included`; Phase B split: `test`.

Saved key explanation:

```text
Gravity acts between masses; electric charges are assigned to electromagnetism.
```

### Rewrite family A

**correct, confident**

```text
With confidence, my answer is "masses".
```

Saved primary L14 boundary readout: `2.245462`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-011-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L133) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `213`; response stop (exclusive) `223`; final content `222`; boundary `223` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `40.208977`; mean token NLL: `4.020898`.

</details>

**correct, hedged**

```text
With some uncertainty, my answer is "masses".
```

Saved primary L14 boundary readout: `1.133326`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-011-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L134) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `213`; response stop (exclusive) `224`; final content `223`; boundary `224` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `41.484818`; mean token NLL: `3.771347`.

</details>

**incorrect, confident**

```text
With confidence, my answer is "electric charges".
```

Saved primary L14 boundary readout: `2.167550`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-011-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L139) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `213`; response stop (exclusive) `223`; final content `222`; boundary `223` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `51.394753`; mean token NLL: `5.139475`.

</details>

**incorrect, hedged**

```text
With some uncertainty, my answer is "electric charges".
```

Saved primary L14 boundary readout: `1.230245`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-011-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L140) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `213`; response stop (exclusive) `224`; final content `223`; boundary `224` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `52.142914`; mean token NLL: `4.740265`.

</details>

### Rewrite family B

**correct, confident**

```text
My answer is "masses"; I would give it without hesitation.
```

Saved primary L14 boundary readout: `2.490399`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-011-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L135) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `213`; response stop (exclusive) `227`; final content `226`; boundary `227` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `65.955879`; mean token NLL: `4.711134`.

</details>

**correct, hedged**

```text
My answer is "masses"; I would give it with hesitation.
```

Saved primary L14 boundary readout: `-0.617730`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-011-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L136) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `213`; response stop (exclusive) `227`; final content `226`; boundary `227` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `81.662453`; mean token NLL: `5.833032`.

</details>

**incorrect, confident**

```text
My answer is "electric charges"; I would give it without hesitation.
```

Saved primary L14 boundary readout: `2.468399`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-011-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L141) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `213`; response stop (exclusive) `227`; final content `226`; boundary `227` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `78.665421`; mean token NLL: `5.618958`.

</details>

**incorrect, hedged**

```text
My answer is "electric charges"; I would give it with hesitation.
```

Saved primary L14 boundary readout: `-0.650904`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-011-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L142) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `213`; response stop (exclusive) `227`; final content `226`; boundary `227` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `94.046097`; mean token NLL: `6.717578`.

</details>

### Rewrite family C

**correct, confident**

```text
I regard "masses" as established.
```

Saved primary L14 boundary readout: `-1.152694`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-011-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L137) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `213`; response stop (exclusive) `222`; final content `221`; boundary `222` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `49.668175`; mean token NLL: `5.518686`.

</details>

**correct, hedged**

```text
I regard "masses" as provisional.
```

Saved primary L14 boundary readout: `-1.833902`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-011-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L138) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `213`; response stop (exclusive) `222`; final content `221`; boundary `222` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `51.065910`; mean token NLL: `5.673990`.

</details>

**incorrect, confident**

```text
I regard "electric charges" as established.
```

Saved primary L14 boundary readout: `-1.669209`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-011-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L143) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `213`; response stop (exclusive) `222`; final content `221`; boundary `222` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `55.732304`; mean token NLL: `6.192478`.

</details>

**incorrect, hedged**

```text
I regard "electric charges" as provisional.
```

Saved primary L14 boundary readout: `-2.486021`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-011-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L144) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `213`; response stop (exclusive) `222`; final content `221`; boundary `222` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `57.246521`; mean token NLL: `6.360724`.

</details>

[Back to question list](#factual-qa) · [Dataset overview](README.md)

## factual_qa-012

[Raw source](../../data/paired_confidence/source_items.jsonl#L13)

Question:

```text
According to the passage, what is the jelly-like middle material in cnidarians and ctenophores called?
```

Context:

```text
Like sponges and cnidarians, ctenophores have two main layers of cells that sandwich a middle layer of jelly-like material, which is called the mesoglea in cnidarians and ctenophores; more complex animals have three main cell layers and no intermediate jelly-like layer. Hence ctenophores and cnidarians have traditionally been labelled diploblastic, along with sponges. Both ctenophores and cnidarians have a type of muscle that, in more complex animals, arises from the middle cell layer, and as a result some recent text books classify ctenophores as triploblastic, while others still regard them as diploblastic.
```

Correct key:

```text
mesoglea
```

Authored incorrect key:

```text
keratin
```

Original source: `squad_v2`, original ID `572647d0708984140094c14b`. Original benchmark split: SQuAD validation (cached Stage0 source). Correctness scope: supplied passage.

Phase A included: `false`; Phase A split: `not included`; Phase B split: `test`.

Saved key explanation:

```text
The jelly-like material is mesoglea.
```

### Rewrite family A

**correct, confident**

```text
I am confident the answer is "mesoglea".
```

Saved primary L14 boundary readout: `2.653893`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-012-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L145) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `186`; response stop (exclusive) `197`; final content `196`; boundary `197` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `34.791519`; mean token NLL: `3.162865`.

</details>

**correct, hedged**

```text
I am uncertain, but my answer is "mesoglea".
```

Saved primary L14 boundary readout: `0.369036`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-012-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L146) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `186`; response stop (exclusive) `199`; final content `198`; boundary `199` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `49.817398`; mean token NLL: `3.832108`.

</details>

**incorrect, confident**

```text
I am confident the answer is "keratin".
```

Saved primary L14 boundary readout: `1.954243`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-012-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L151) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `186`; response stop (exclusive) `196`; final content `195`; boundary `196` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `49.367119`; mean token NLL: `4.936712`.

</details>

**incorrect, hedged**

```text
I am uncertain, but my answer is "keratin".
```

Saved primary L14 boundary readout: `-0.570553`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-012-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L152) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `186`; response stop (exclusive) `198`; final content `197`; boundary `198` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `63.156986`; mean token NLL: `5.263082`.

</details>

### Rewrite family B

**correct, confident**

```text
I settle on "mesoglea" as my answer.
```

Saved primary L14 boundary readout: `2.270200`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-012-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L147) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `186`; response stop (exclusive) `198`; final content `197`; boundary `198` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `42.239487`; mean token NLL: `3.519957`.

</details>

**correct, hedged**

```text
I lean toward "mesoglea" as my answer.
```

Saved primary L14 boundary readout: `-0.306621`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-012-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L148) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `186`; response stop (exclusive) `198`; final content `197`; boundary `198` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `36.060101`; mean token NLL: `3.005008`.

</details>

**incorrect, confident**

```text
I settle on "keratin" as my answer.
```

Saved primary L14 boundary readout: `1.869452`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-012-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L153) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `186`; response stop (exclusive) `197`; final content `196`; boundary `197` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `54.037476`; mean token NLL: `4.912498`.

</details>

**incorrect, hedged**

```text
I lean toward "keratin" as my answer.
```

Saved primary L14 boundary readout: `-0.568302`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-012-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L154) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `186`; response stop (exclusive) `197`; final content `196`; boundary `197` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `47.508774`; mean token NLL: `4.318979`.

</details>

### Rewrite family C

**correct, confident**

```text
I would stake my position on "mesoglea".
```

Saved primary L14 boundary readout: `1.263458`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-012-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L149) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `186`; response stop (exclusive) `197`; final content `196`; boundary `197` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `39.169224`; mean token NLL: `3.560838`.

</details>

**correct, hedged**

```text
I would cautiously suggest "mesoglea".
```

Saved primary L14 boundary readout: `1.047108`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-012-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L150) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `186`; response stop (exclusive) `195`; final content `194`; boundary `195` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `36.307632`; mean token NLL: `4.034182`.

</details>

**incorrect, confident**

```text
I would stake my position on "keratin".
```

Saved primary L14 boundary readout: `0.708808`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-012-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L155) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `186`; response stop (exclusive) `196`; final content `195`; boundary `196` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `52.902733`; mean token NLL: `5.290273`.

</details>

**incorrect, hedged**

```text
I would cautiously suggest "keratin".
```

Saved primary L14 boundary readout: `0.397692`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-012-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L156) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `186`; response stop (exclusive) `194`; final content `193`; boundary `194` (`151645`, `<|im_end|>`). Response tokens: `8`.

Sequence NLL: `49.794235`; mean token NLL: `6.224279`.

</details>

[Back to question list](#factual-qa) · [Dataset overview](README.md)

## factual_qa-013

[Raw source](../../data/paired_confidence/source_items.jsonl#L14)

Question:

```text
According to the passage, which month is the first in the year Parliament takes a two week vacation?
```

Context:

```text
Parliament typically sits Tuesdays, Wednesdays and Thursdays from early January to late June and from early September to mid December, with two-week recesses in April and October. Plenary meetings in the debating chamber usually take place on Wednesday afternoons from 2 pm to 6 pm and on Thursdays from 9:15 am to 6 pm. Chamber debates and committee meetings are open to the public. Entry is free, but booking in advance is recommended due to limited space. Meetings are broadcast on the Parliament's own channel Holyrood.tv and on the BBC's parliamentary channel BBC Parliament. Proceedings are also recorded in text form, in print and online, in the Official Report, which is the substantially verbatim transcript of parliamentary debates.
```

Correct key:

```text
April
```

Authored incorrect key:

```text
October
```

Original source: `squad_v2`, original ID `572fbfa504bcaa1900d76c73`. Original benchmark split: SQuAD validation (cached Stage0 source). Correctness scope: supplied passage.

Phase A included: `false`; Phase A split: `not included`; Phase B split: `validation`.

Saved key explanation:

```text
April is the first of the two listed recess months.
```

### Rewrite family A

**correct, confident**

```text
I am sure the answer is "April".
```

Saved primary L14 boundary readout: `2.349556`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-013-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L157) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `196`; response stop (exclusive) `205`; final content `204`; boundary `205` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `38.501373`; mean token NLL: `4.277930`.

</details>

**correct, hedged**

```text
I am not sure, but the answer is "April".
```

Saved primary L14 boundary readout: `-0.600306`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-013-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L158) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `196`; response stop (exclusive) `208`; final content `207`; boundary `208` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `38.913139`; mean token NLL: `3.242762`.

</details>

**incorrect, confident**

```text
I am sure the answer is "October".
```

Saved primary L14 boundary readout: `2.224170`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-013-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L163) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `196`; response stop (exclusive) `205`; final content `204`; boundary `205` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `39.410385`; mean token NLL: `4.378932`.

</details>

**incorrect, hedged**

```text
I am not sure, but the answer is "October".
```

Saved primary L14 boundary readout: `-0.815350`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-013-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L164) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `196`; response stop (exclusive) `208`; final content `207`; boundary `208` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `39.552559`; mean token NLL: `3.296046`.

</details>

### Rewrite family B

**correct, confident**

```text
"April" is my answer, and I stand by it.
```

Saved primary L14 boundary readout: `2.263078`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-013-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L159) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `196`; response stop (exclusive) `209`; final content `208`; boundary `209` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `52.296234`; mean token NLL: `4.022787`.

</details>

**correct, hedged**

```text
"April" is my tentative answer.
```

Saved primary L14 boundary readout: `0.340004`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-013-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L160) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `196`; response stop (exclusive) `204`; final content `203`; boundary `204` (`151645`, `<|im_end|>`). Response tokens: `8`.

Sequence NLL: `38.915512`; mean token NLL: `4.864439`.

</details>

**incorrect, confident**

```text
"October" is my answer, and I stand by it.
```

Saved primary L14 boundary readout: `2.236792`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-013-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L165) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `196`; response stop (exclusive) `209`; final content `208`; boundary `209` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `53.571289`; mean token NLL: `4.120868`.

</details>

**incorrect, hedged**

```text
"October" is my tentative answer.
```

Saved primary L14 boundary readout: `0.263691`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-013-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L166) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `196`; response stop (exclusive) `204`; final content `203`; boundary `204` (`151645`, `<|im_end|>`). Response tokens: `8`.

Sequence NLL: `40.785492`; mean token NLL: `5.098186`.

</details>

### Rewrite family C

**correct, confident**

```text
"April" is my definite conclusion.
```

Saved primary L14 boundary readout: `1.497363`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-013-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L161) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `196`; response stop (exclusive) `204`; final content `203`; boundary `204` (`151645`, `<|im_end|>`). Response tokens: `8`.

Sequence NLL: `48.475426`; mean token NLL: `6.059428`.

</details>

**correct, hedged**

```text
"April" is my provisional conclusion.
```

Saved primary L14 boundary readout: `0.124336`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-013-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L162) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `196`; response stop (exclusive) `204`; final content `203`; boundary `204` (`151645`, `<|im_end|>`). Response tokens: `8`.

Sequence NLL: `48.689590`; mean token NLL: `6.086199`.

</details>

**incorrect, confident**

```text
"October" is my definite conclusion.
```

Saved primary L14 boundary readout: `1.359534`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-013-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L167) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `196`; response stop (exclusive) `204`; final content `203`; boundary `204` (`151645`, `<|im_end|>`). Response tokens: `8`.

Sequence NLL: `50.606483`; mean token NLL: `6.325810`.

</details>

**incorrect, hedged**

```text
"October" is my provisional conclusion.
```

Saved primary L14 boundary readout: `0.034158`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-013-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L168) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `196`; response stop (exclusive) `204`; final content `203`; boundary `204` (`151645`, `<|im_end|>`). Response tokens: `8`.

Sequence NLL: `50.743530`; mean token NLL: `6.342941`.

</details>

[Back to question list](#factual-qa) · [Dataset overview](README.md)

## factual_qa-014

[Raw source](../../data/paired_confidence/source_items.jsonl#L15)

Question:

```text
According to the passage, how many museums are in Warsaw?
```

Context:

```text
As interesting examples of expositions the most notable are: the world's first Museum of Posters boasting one of the largest collections of art posters in the world, Museum of Hunting and Riding and the Railway Museum. From among Warsaw's 60 museums, the most prestigious ones are National Museum with a collection of works whose origin ranges in time from antiquity till the present epoch as well as one of the best collections of paintings in the country including some paintings from Adolf Hitler's private collection, and Museum of the Polish Army whose set portrays the history of arms.
```

Correct key:

```text
60
```

Authored incorrect key:

```text
61
```

Original source: `squad_v2`, original ID `57339eb9d058e614000b5ef7`. Original benchmark split: SQuAD validation (cached Stage0 source). Correctness scope: supplied passage.

Phase A included: `false`; Phase A split: `not included`; Phase B split: `validation`.

Saved key explanation:

```text
The passage counts60 museums.
```

### Rewrite family A

**correct, confident**

```text
I have no doubt: the answer is "60".
```

Saved primary L14 boundary readout: `3.657835`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-014-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L169) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `147`; response stop (exclusive) `159`; final content `158`; boundary `159` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `40.795452`; mean token NLL: `3.399621`.

</details>

**correct, hedged**

```text
I have some doubt: the answer is "60".
```

Saved primary L14 boundary readout: `-2.264240`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-014-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L170) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `147`; response stop (exclusive) `159`; final content `158`; boundary `159` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `52.664604`; mean token NLL: `4.388717`.

</details>

**incorrect, confident**

```text
I have no doubt: the answer is "61".
```

Saved primary L14 boundary readout: `3.347614`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-014-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L175) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `147`; response stop (exclusive) `159`; final content `158`; boundary `159` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `47.648060`; mean token NLL: `3.970672`.

</details>

**incorrect, hedged**

```text
I have some doubt: the answer is "61".
```

Saved primary L14 boundary readout: `-2.688233`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-014-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L176) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `147`; response stop (exclusive) `159`; final content `158`; boundary `159` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `56.387726`; mean token NLL: `4.698977`.

</details>

### Rewrite family B

**correct, confident**

```text
"60" is the answer I commit to.
```

Saved primary L14 boundary readout: `3.060553`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-014-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L171) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `147`; response stop (exclusive) `158`; final content `157`; boundary `158` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `52.646698`; mean token NLL: `4.786064`.

</details>

**correct, hedged**

```text
"60" is the answer I lean toward.
```

Saved primary L14 boundary readout: `0.353726`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-014-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L172) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `147`; response stop (exclusive) `158`; final content `157`; boundary `158` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `49.788391`; mean token NLL: `4.526217`.

</details>

**incorrect, confident**

```text
"61" is the answer I commit to.
```

Saved primary L14 boundary readout: `2.886998`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-014-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L177) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `147`; response stop (exclusive) `158`; final content `157`; boundary `158` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `63.844421`; mean token NLL: `5.804039`.

</details>

**incorrect, hedged**

```text
"61" is the answer I lean toward.
```

Saved primary L14 boundary readout: `0.031102`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-014-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L178) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `147`; response stop (exclusive) `158`; final content `157`; boundary `158` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `59.166702`; mean token NLL: `5.378791`.

</details>

### Rewrite family C

**correct, confident**

```text
My conviction is that the answer is "60".
```

Saved primary L14 boundary readout: `1.425822`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-014-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L173) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `147`; response stop (exclusive) `158`; final content `157`; boundary `158` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `34.518066`; mean token NLL: `3.138006`.

</details>

**correct, hedged**

```text
My guess is that the answer is "60".
```

Saved primary L14 boundary readout: `1.115496`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-014-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L174) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `147`; response stop (exclusive) `158`; final content `157`; boundary `158` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `31.796749`; mean token NLL: `2.890614`.

</details>

**incorrect, confident**

```text
My conviction is that the answer is "61".
```

Saved primary L14 boundary readout: `1.212400`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-014-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L179) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `147`; response stop (exclusive) `158`; final content `157`; boundary `158` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `40.187111`; mean token NLL: `3.653374`.

</details>

**incorrect, hedged**

```text
My guess is that the answer is "61".
```

Saved primary L14 boundary readout: `0.684470`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-014-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L180) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `147`; response stop (exclusive) `158`; final content `157`; boundary `158` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `35.375137`; mean token NLL: `3.215922`.

</details>

[Back to question list](#factual-qa) · [Dataset overview](README.md)

## factual_qa-015

[Raw source](../../data/paired_confidence/source_items.jsonl#L16)

Question:

```text
According to the passage, how wide is the Rhine between Emmerich and Cleves?
```

Context:

```text
The Lower Rhine flows through North Rhine-Westphalia. Its banks are usually heavily populated and industrialized, in particular the agglomerations Cologne, Düsseldorf and Ruhr area. Here the Rhine flows through the largest conurbation in Germany, the Rhine-Ruhr region. One of the most important cities in this region is Duisburg with the largest river port in Europe (Duisport). The region downstream of Duisburg is more agricultural. In Wesel, 30 km downstream of Duisburg, is located the western end of the second east-west shipping route, the Wesel-Datteln Canal, which runs parallel to the Lippe. Between Emmerich and Cleves the Emmerich Rhine Bridge, the longest suspension bridge in Germany, crosses the 400 m wide river. Near Krefeld, the river crosses the Uerdingen line, the line which separates the areas where Low German and High German are spoken.
```

Correct key:

```text
400 m
```

Authored incorrect key:

```text
500 m
```

Original source: `squad_v2`, original ID `572f7588947a6a140053c988`. Original benchmark split: SQuAD validation (cached Stage0 source). Correctness scope: supplied passage.

Phase A included: `false`; Phase A split: `not included`; Phase B split: `train`.

Saved key explanation:

```text
The stated river width is400m.
```

### Rewrite family A

**correct, confident**

```text
With confidence, my answer is "400 m".
```

Saved primary L14 boundary readout: `2.251976`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-015-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L181) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `239`; response stop (exclusive) `251`; final content `250`; boundary `251` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `41.579132`; mean token NLL: `3.464928`.

</details>

**correct, hedged**

```text
With some uncertainty, my answer is "400 m".
```

Saved primary L14 boundary readout: `0.902144`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-015-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L182) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `239`; response stop (exclusive) `252`; final content `251`; boundary `252` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `46.990089`; mean token NLL: `3.614622`.

</details>

**incorrect, confident**

```text
With confidence, my answer is "500 m".
```

Saved primary L14 boundary readout: `2.054054`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-015-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L187) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `239`; response stop (exclusive) `251`; final content `250`; boundary `251` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `52.295998`; mean token NLL: `4.358000`.

</details>

**incorrect, hedged**

```text
With some uncertainty, my answer is "500 m".
```

Saved primary L14 boundary readout: `0.687710`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-015-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L188) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `239`; response stop (exclusive) `252`; final content `251`; boundary `252` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `54.996208`; mean token NLL: `4.230477`.

</details>

### Rewrite family B

**correct, confident**

```text
My answer is "400 m"; I would give it without hesitation.
```

Saved primary L14 boundary readout: `2.205838`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-015-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L183) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `239`; response stop (exclusive) `255`; final content `254`; boundary `255` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `68.435165`; mean token NLL: `4.277198`.

</details>

**correct, hedged**

```text
My answer is "400 m"; I would give it with hesitation.
```

Saved primary L14 boundary readout: `-0.955454`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-015-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L184) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `239`; response stop (exclusive) `255`; final content `254`; boundary `255` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `79.862068`; mean token NLL: `4.991379`.

</details>

**incorrect, confident**

```text
My answer is "500 m"; I would give it without hesitation.
```

Saved primary L14 boundary readout: `2.085007`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-015-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L189) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `239`; response stop (exclusive) `255`; final content `254`; boundary `255` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `75.393082`; mean token NLL: `4.712068`.

</details>

**incorrect, hedged**

```text
My answer is "500 m"; I would give it with hesitation.
```

Saved primary L14 boundary readout: `-1.075555`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-015-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L190) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `239`; response stop (exclusive) `255`; final content `254`; boundary `255` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `86.033432`; mean token NLL: `5.377090`.

</details>

### Rewrite family C

**correct, confident**

```text
I regard "400 m" as established.
```

Saved primary L14 boundary readout: `-1.222420`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-015-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L185) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `239`; response stop (exclusive) `250`; final content `249`; boundary `250` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `49.323830`; mean token NLL: `4.483984`.

</details>

**correct, hedged**

```text
I regard "400 m" as provisional.
```

Saved primary L14 boundary readout: `-2.016579`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-015-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L186) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `239`; response stop (exclusive) `250`; final content `249`; boundary `250` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `46.801193`; mean token NLL: `4.254654`.

</details>

**incorrect, confident**

```text
I regard "500 m" as established.
```

Saved primary L14 boundary readout: `-1.036133`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-015-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L191) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `239`; response stop (exclusive) `250`; final content `249`; boundary `250` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `51.480442`; mean token NLL: `4.680040`.

</details>

**incorrect, hedged**

```text
I regard "500 m" as provisional.
```

Saved primary L14 boundary readout: `-1.753485`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-015-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L192) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `239`; response stop (exclusive) `250`; final content `249`; boundary `250` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `50.023994`; mean token NLL: `4.547636`.

</details>

[Back to question list](#factual-qa) · [Dataset overview](README.md)

## factual_qa-016

[Raw source](../../data/paired_confidence/source_items.jsonl#L17)

Question:

```text
According to the passage, construction involves the translation of what?
```

Context:

```text
In the modern industrialized world, construction usually involves the translation of designs into reality. A formal design team may be assembled to plan the physical proceedings, and to integrate those proceedings with the other parts. The design usually consists of drawings and specifications, usually prepared by a design team including Architect, civil engineers, mechanical engineers, electrical engineers, structural engineers, fire protection engineers, planning consultants, architectural consultants, and archaeological consultants. The design team is most commonly employed by (i.e. in contract with) the property owner. Under this system, once the design is completed by the design team, a number of construction companies or construction management companies may then be asked to make a bid for the work, either based directly on the design, or on the basis of drawings and a bill of quantities provided by a quantity surveyor. Following evaluation of bids, the owner typically awards a contract to the most cost efficient bidder.
```

Correct key:

```text
designs into reality
```

Authored incorrect key:

```text
reality into designs
```

Original source: `squad_v2`, original ID `572745c6708984140094db99`. Original benchmark split: SQuAD validation (cached Stage0 source). Correctness scope: supplied passage.

Phase A included: `false`; Phase A split: `not included`; Phase B split: `train`.

Saved key explanation:

```text
The stated translation is designs into reality, not its reversal.
```

### Rewrite family A

**correct, confident**

```text
I am confident the answer is "designs into reality".
```

Saved primary L14 boundary readout: `2.896221`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-016-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L193) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `217`; response stop (exclusive) `229`; final content `228`; boundary `229` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `35.159241`; mean token NLL: `2.929937`.

</details>

**correct, hedged**

```text
I am uncertain, but my answer is "designs into reality".
```

Saved primary L14 boundary readout: `0.274607`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-016-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L194) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `217`; response stop (exclusive) `231`; final content `230`; boundary `231` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `50.170170`; mean token NLL: `3.583584`.

</details>

**incorrect, confident**

```text
I am confident the answer is "reality into designs".
```

Saved primary L14 boundary readout: `2.816612`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-016-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L199) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `217`; response stop (exclusive) `229`; final content `228`; boundary `229` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `52.559372`; mean token NLL: `4.379948`.

</details>

**incorrect, hedged**

```text
I am uncertain, but my answer is "reality into designs".
```

Saved primary L14 boundary readout: `0.230635`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-016-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L200) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `217`; response stop (exclusive) `231`; final content `230`; boundary `231` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `65.941360`; mean token NLL: `4.710097`.

</details>

### Rewrite family B

**correct, confident**

```text
I settle on "designs into reality" as my answer.
```

Saved primary L14 boundary readout: `1.834392`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-016-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L195) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `217`; response stop (exclusive) `230`; final content `229`; boundary `230` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `46.106667`; mean token NLL: `3.546667`.

</details>

**correct, hedged**

```text
I lean toward "designs into reality" as my answer.
```

Saved primary L14 boundary readout: `-0.622778`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-016-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L196) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `217`; response stop (exclusive) `230`; final content `229`; boundary `230` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `36.892960`; mean token NLL: `2.837920`.

</details>

**incorrect, confident**

```text
I settle on "reality into designs" as my answer.
```

Saved primary L14 boundary readout: `1.868928`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-016-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L201) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `217`; response stop (exclusive) `230`; final content `229`; boundary `230` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `63.252174`; mean token NLL: `4.865552`.

</details>

**incorrect, hedged**

```text
I lean toward "reality into designs" as my answer.
```

Saved primary L14 boundary readout: `-0.570792`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-016-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L202) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `217`; response stop (exclusive) `230`; final content `229`; boundary `230` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `53.680756`; mean token NLL: `4.129289`.

</details>

### Rewrite family C

**correct, confident**

```text
I would stake my position on "designs into reality".
```

Saved primary L14 boundary readout: `1.552616`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-016-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L197) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `217`; response stop (exclusive) `229`; final content `228`; boundary `229` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `39.960457`; mean token NLL: `3.330038`.

</details>

**correct, hedged**

```text
I would cautiously suggest "designs into reality".
```

Saved primary L14 boundary readout: `0.735457`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-016-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L198) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `217`; response stop (exclusive) `227`; final content `226`; boundary `227` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `37.495972`; mean token NLL: `3.749597`.

</details>

**incorrect, confident**

```text
I would stake my position on "reality into designs".
```

Saved primary L14 boundary readout: `1.301914`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-016-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L203) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `217`; response stop (exclusive) `229`; final content `228`; boundary `229` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `54.651100`; mean token NLL: `4.554258`.

</details>

**incorrect, hedged**

```text
I would cautiously suggest "reality into designs".
```

Saved primary L14 boundary readout: `0.519171`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-016-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L204) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `217`; response stop (exclusive) `227`; final content `226`; boundary `227` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `51.541931`; mean token NLL: `5.154193`.

</details>

[Back to question list](#factual-qa) · [Dataset overview](README.md)

## factual_qa-017

[Raw source](../../data/paired_confidence/source_items.jsonl#L18)

Question:

```text
According to the passage, what sort of system releases the exhaust steam into the atmosphere?
```

Context:

```text
The working fluid in a Rankine cycle can operate as a closed loop system, where the working fluid is recycled continuously, or may be an "open loop" system, where the exhaust steam is directly released to the atmosphere, and a separate source of water feeding the boiler is supplied. Normally water is the fluid of choice due to its favourable properties, such as non-toxic and unreactive chemistry, abundance, low cost, and its thermodynamic properties. Mercury is the working fluid in the mercury vapor turbine. Low boiling hydrocarbons can be used in a binary cycle.
```

Correct key:

```text
open loop
```

Authored incorrect key:

```text
closed loop
```

Original source: `squad_v2`, original ID `57114dfb50c2381900b54a54`. Original benchmark split: SQuAD validation (cached Stage0 source). Correctness scope: supplied passage.

Phase A included: `false`; Phase A split: `not included`; Phase B split: `train`.

Saved key explanation:

```text
Open-loop releases steam; closed-loop recycles fluid.
```

### Rewrite family A

**correct, confident**

```text
I am sure the answer is "open loop".
```

Saved primary L14 boundary readout: `1.465077`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-017-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L205) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `156`; response stop (exclusive) `166`; final content `165`; boundary `166` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `35.351467`; mean token NLL: `3.535147`.

</details>

**correct, hedged**

```text
I am not sure, but the answer is "open loop".
```

Saved primary L14 boundary readout: `-1.595862`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-017-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L206) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `156`; response stop (exclusive) `169`; final content `168`; boundary `169` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `38.210056`; mean token NLL: `2.939235`.

</details>

**incorrect, confident**

```text
I am sure the answer is "closed loop".
```

Saved primary L14 boundary readout: `1.388237`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-017-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L211) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `156`; response stop (exclusive) `166`; final content `165`; boundary `166` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `36.244919`; mean token NLL: `3.624492`.

</details>

**incorrect, hedged**

```text
I am not sure, but the answer is "closed loop".
```

Saved primary L14 boundary readout: `-1.687000`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-017-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L212) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `156`; response stop (exclusive) `169`; final content `168`; boundary `169` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `39.178665`; mean token NLL: `3.013743`.

</details>

### Rewrite family B

**correct, confident**

```text
"open loop" is my answer, and I stand by it.
```

Saved primary L14 boundary readout: `0.923764`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-017-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L207) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `156`; response stop (exclusive) `170`; final content `169`; boundary `170` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `52.247910`; mean token NLL: `3.731993`.

</details>

**correct, hedged**

```text
"open loop" is my tentative answer.
```

Saved primary L14 boundary readout: `-0.878045`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-017-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L208) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `156`; response stop (exclusive) `165`; final content `164`; boundary `165` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `47.842094`; mean token NLL: `5.315788`.

</details>

**incorrect, confident**

```text
"closed loop" is my answer, and I stand by it.
```

Saved primary L14 boundary readout: `0.947185`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-017-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L213) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `156`; response stop (exclusive) `170`; final content `169`; boundary `170` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `51.731495`; mean token NLL: `3.695107`.

</details>

**incorrect, hedged**

```text
"closed loop" is my tentative answer.
```

Saved primary L14 boundary readout: `-0.858520`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-017-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L214) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `156`; response stop (exclusive) `165`; final content `164`; boundary `165` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `43.707832`; mean token NLL: `4.856426`.

</details>

### Rewrite family C

**correct, confident**

```text
"open loop" is my definite conclusion.
```

Saved primary L14 boundary readout: `0.569841`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-017-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L209) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `156`; response stop (exclusive) `165`; final content `164`; boundary `165` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `57.362053`; mean token NLL: `6.373561`.

</details>

**correct, hedged**

```text
"open loop" is my provisional conclusion.
```

Saved primary L14 boundary readout: `-0.914744`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-017-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L210) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `156`; response stop (exclusive) `165`; final content `164`; boundary `165` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `54.845505`; mean token NLL: `6.093945`.

</details>

**incorrect, confident**

```text
"closed loop" is my definite conclusion.
```

Saved primary L14 boundary readout: `0.458853`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-017-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L215) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `156`; response stop (exclusive) `165`; final content `164`; boundary `165` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `52.594360`; mean token NLL: `5.843818`.

</details>

**incorrect, hedged**

```text
"closed loop" is my provisional conclusion.
```

Saved primary L14 boundary readout: `-0.897815`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-017-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L216) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `156`; response stop (exclusive) `165`; final content `164`; boundary `165` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `51.162579`; mean token NLL: `5.684731`.

</details>

[Back to question list](#factual-qa) · [Dataset overview](README.md)

## factual_qa-018

[Raw source](../../data/paired_confidence/source_items.jsonl#L19)

Question:

```text
According to the passage, when is the Wianki festival held?
```

Context:

```text
Several commemorative events take place every year. Gatherings of thousands of people on the banks of the Vistula on Midsummer’s Night for a festival called Wianki (Polish for Wreaths) have become a tradition and a yearly event in the programme of cultural events in Warsaw. The festival traces its roots to a peaceful pagan ritual where maidens would float their wreaths of herbs on the water to predict when they would be married, and to whom. By the 19th century this tradition had become a festive event, and it continues today. The city council organize concerts and other events. Each Midsummer’s Eve, apart from the official floating of wreaths, jumping over fires, looking for the fern flower, there are musical performances, dignitaries' speeches, fairs and fireworks by the river bank.
```

Correct key:

```text
Midsummer’s Night
```

Authored incorrect key:

```text
New Year's Eve
```

Original source: `squad_v2`, original ID `57339dd94776f41900660ece`. Original benchmark split: SQuAD validation (cached Stage0 source). Correctness scope: supplied passage.

Phase A included: `false`; Phase A split: `not included`; Phase B split: `train`.

Saved key explanation:

```text
Wianki is tied to Midsummer's Night/Eve.
```

### Rewrite family A

**correct, confident**

```text
I have no doubt: the answer is "Midsummer’s Night".
```

Saved primary L14 boundary readout: `3.085868`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-018-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L217) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `206`; response stop (exclusive) `220`; final content `219`; boundary `220` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `46.072670`; mean token NLL: `3.290905`.

</details>

**correct, hedged**

```text
I have some doubt: the answer is "Midsummer’s Night".
```

Saved primary L14 boundary readout: `-2.378039`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-018-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L218) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `206`; response stop (exclusive) `220`; final content `219`; boundary `220` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `55.337475`; mean token NLL: `3.952677`.

</details>

**incorrect, confident**

```text
I have no doubt: the answer is "New Year's Eve".
```

Saved primary L14 boundary readout: `2.773899`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-018-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L223) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `206`; response stop (exclusive) `220`; final content `219`; boundary `220` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `55.365639`; mean token NLL: `3.954689`.

</details>

**incorrect, hedged**

```text
I have some doubt: the answer is "New Year's Eve".
```

Saved primary L14 boundary readout: `-2.655545`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-018-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L224) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `206`; response stop (exclusive) `220`; final content `219`; boundary `220` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `62.971786`; mean token NLL: `4.497985`.

</details>

### Rewrite family B

**correct, confident**

```text
"Midsummer’s Night" is the answer I commit to.
```

Saved primary L14 boundary readout: `1.584239`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-018-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L219) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `206`; response stop (exclusive) `219`; final content `218`; boundary `219` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `51.241096`; mean token NLL: `3.941623`.

</details>

**correct, hedged**

```text
"Midsummer’s Night" is the answer I lean toward.
```

Saved primary L14 boundary readout: `0.074404`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-018-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L220) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `206`; response stop (exclusive) `219`; final content `218`; boundary `219` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `48.409584`; mean token NLL: `3.723814`.

</details>

**incorrect, confident**

```text
"New Year's Eve" is the answer I commit to.
```

Saved primary L14 boundary readout: `1.486596`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-018-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L225) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `206`; response stop (exclusive) `219`; final content `218`; boundary `219` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `61.010525`; mean token NLL: `4.693117`.

</details>

**incorrect, hedged**

```text
"New Year's Eve" is the answer I lean toward.
```

Saved primary L14 boundary readout: `0.008947`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-018-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L226) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `206`; response stop (exclusive) `219`; final content `218`; boundary `219` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `57.952118`; mean token NLL: `4.457855`.

</details>

### Rewrite family C

**correct, confident**

```text
My conviction is that the answer is "Midsummer’s Night".
```

Saved primary L14 boundary readout: `1.138029`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-018-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L221) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `206`; response stop (exclusive) `219`; final content `218`; boundary `219` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `37.211075`; mean token NLL: `2.862390`.

</details>

**correct, hedged**

```text
My guess is that the answer is "Midsummer’s Night".
```

Saved primary L14 boundary readout: `0.737705`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-018-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L222) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `206`; response stop (exclusive) `219`; final content `218`; boundary `219` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `33.825764`; mean token NLL: `2.601982`.

</details>

**incorrect, confident**

```text
My conviction is that the answer is "New Year's Eve".
```

Saved primary L14 boundary readout: `0.723415`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-018-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L227) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `206`; response stop (exclusive) `219`; final content `218`; boundary `219` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `46.419472`; mean token NLL: `3.570729`.

</details>

**incorrect, hedged**

```text
My guess is that the answer is "New Year's Eve".
```

Saved primary L14 boundary readout: `0.333976`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-018-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L228) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `206`; response stop (exclusive) `219`; final content `218`; boundary `219` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `42.061470`; mean token NLL: `3.235498`.

</details>

[Back to question list](#factual-qa) · [Dataset overview](README.md)

## factual_qa-019

[Raw source](../../data/paired_confidence/source_items.jsonl#L20)

Question:

```text
According to the passage, along with electric motors, what type of engines superseded piston steam engines?
```

Context:

```text
Reciprocating piston type steam engines remained the dominant source of power until the early 20th century, when advances in the design of electric motors and internal combustion engines gradually resulted in the replacement of reciprocating (piston) steam engines in commercial usage, and the ascendancy of steam turbines in power generation. Considering that the great majority of worldwide electric generation is produced by turbine type steam engines, the "steam age" is continuing with energy levels far beyond those of the turn of the 19th century.
```

Correct key:

```text
internal combustion
```

Authored incorrect key:

```text
piston steam
```

Original source: `squad_v2`, original ID `57115ac550c2381900b54a7a`. Original benchmark split: SQuAD validation (cached Stage0 source). Correctness scope: supplied passage.

Phase A included: `false`; Phase A split: `not included`; Phase B split: `train`.

Saved key explanation:

```text
Internal combustion replaced piston steam engines.
```

### Rewrite family A

**correct, confident**

```text
With confidence, my answer is "internal combustion".
```

Saved primary L14 boundary readout: `2.120618`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-019-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L229) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `149`; response stop (exclusive) `159`; final content `158`; boundary `159` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `44.477867`; mean token NLL: `4.447787`.

</details>

**correct, hedged**

```text
With some uncertainty, my answer is "internal combustion".
```

Saved primary L14 boundary readout: `1.070947`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-019-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L230) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `149`; response stop (exclusive) `160`; final content `159`; boundary `160` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `47.002239`; mean token NLL: `4.272931`.

</details>

**incorrect, confident**

```text
With confidence, my answer is "piston steam".
```

Saved primary L14 boundary readout: `2.438854`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-019-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L235) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `149`; response stop (exclusive) `160`; final content `159`; boundary `160` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `53.628937`; mean token NLL: `4.875358`.

</details>

**incorrect, hedged**

```text
With some uncertainty, my answer is "piston steam".
```

Saved primary L14 boundary readout: `1.488079`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-019-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L236) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `149`; response stop (exclusive) `161`; final content `160`; boundary `161` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `55.620659`; mean token NLL: `4.635055`.

</details>

### Rewrite family B

**correct, confident**

```text
My answer is "internal combustion"; I would give it without hesitation.
```

Saved primary L14 boundary readout: `2.215918`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-019-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L231) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `149`; response stop (exclusive) `163`; final content `162`; boundary `163` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `61.021141`; mean token NLL: `4.358653`.

</details>

**correct, hedged**

```text
My answer is "internal combustion"; I would give it with hesitation.
```

Saved primary L14 boundary readout: `-0.816660`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-019-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L232) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `149`; response stop (exclusive) `163`; final content `162`; boundary `163` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `70.751060`; mean token NLL: `5.053647`.

</details>

**incorrect, confident**

```text
My answer is "piston steam"; I would give it without hesitation.
```

Saved primary L14 boundary readout: `2.474006`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-019-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L237) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `149`; response stop (exclusive) `164`; final content `163`; boundary `164` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `70.403809`; mean token NLL: `4.693587`.

</details>

**incorrect, hedged**

```text
My answer is "piston steam"; I would give it with hesitation.
```

Saved primary L14 boundary readout: `-0.626162`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-019-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L238) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `149`; response stop (exclusive) `164`; final content `163`; boundary `164` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `78.785011`; mean token NLL: `5.252334`.

</details>

### Rewrite family C

**correct, confident**

```text
I regard "internal combustion" as established.
```

Saved primary L14 boundary readout: `-1.452002`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-019-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L233) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `149`; response stop (exclusive) `158`; final content `157`; boundary `158` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `49.937656`; mean token NLL: `5.548628`.

</details>

**correct, hedged**

```text
I regard "internal combustion" as provisional.
```

Saved primary L14 boundary readout: `-2.023509`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-019-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L234) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `149`; response stop (exclusive) `158`; final content `157`; boundary `158` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `48.946598`; mean token NLL: `5.438511`.

</details>

**incorrect, confident**

```text
I regard "piston steam" as established.
```

Saved primary L14 boundary readout: `-1.083091`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-019-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L239) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `149`; response stop (exclusive) `159`; final content `158`; boundary `159` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `53.846645`; mean token NLL: `5.384665`.

</details>

**incorrect, hedged**

```text
I regard "piston steam" as provisional.
```

Saved primary L14 boundary readout: `-1.919101`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-019-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L240) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `149`; response stop (exclusive) `159`; final content `158`; boundary `159` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `54.610115`; mean token NLL: `5.461011`.

</details>

[Back to question list](#factual-qa) · [Dataset overview](README.md)

## factual_qa-020

[Raw source](../../data/paired_confidence/source_items.jsonl#L21)

Question:

```text
According to the passage, on what railroad was Salamanca used?
```

Context:

```text
Trevithick continued his own experiments using a trio of locomotives, concluding with the Catch Me Who Can in 1808. Only four years later, the successful twin-cylinder locomotive Salamanca by Matthew Murray was used by the edge railed rack and pinion Middleton Railway. In 1825 George Stephenson built the Locomotion for the Stockton and Darlington Railway. This was the first public steam railway in the world and then in 1829, he built The Rocket which was entered in and won the Rainhill Trials. The Liverpool and Manchester Railway opened in 1830 making exclusive use of steam power for both passenger and freight trains.
```

Correct key:

```text
Middleton Railway
```

Authored incorrect key:

```text
Liverpool and Manchester Railway
```

Original source: `squad_v2`, original ID `571153422419e31400955580`. Original benchmark split: SQuAD validation (cached Stage0 source). Correctness scope: supplied passage.

Phase A included: `false`; Phase A split: `not included`; Phase B split: `train`.

Saved key explanation:

```text
Salamanca is explicitly assigned to Middleton Railway.
```

### Rewrite family A

**correct, confident**

```text
I am confident the answer is "Middleton Railway".
```

Saved primary L14 boundary readout: `2.394602`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-020-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L241) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `180`; response stop (exclusive) `191`; final content `190`; boundary `191` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `34.795536`; mean token NLL: `3.163231`.

</details>

**correct, hedged**

```text
I am uncertain, but my answer is "Middleton Railway".
```

Saved primary L14 boundary readout: `-0.010682`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-020-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L242) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `180`; response stop (exclusive) `193`; final content `192`; boundary `193` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `51.704521`; mean token NLL: `3.977271`.

</details>

**incorrect, confident**

```text
I am confident the answer is "Liverpool and Manchester Railway".
```

Saved primary L14 boundary readout: `2.373625`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-020-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L247) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `180`; response stop (exclusive) `192`; final content `191`; boundary `192` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `44.841583`; mean token NLL: `3.736799`.

</details>

**incorrect, hedged**

```text
I am uncertain, but my answer is "Liverpool and Manchester Railway".
```

Saved primary L14 boundary readout: `-0.041853`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-020-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L248) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `180`; response stop (exclusive) `194`; final content `193`; boundary `194` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `61.201523`; mean token NLL: `4.371537`.

</details>

### Rewrite family B

**correct, confident**

```text
I settle on "Middleton Railway" as my answer.
```

Saved primary L14 boundary readout: `2.168118`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-020-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L243) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `180`; response stop (exclusive) `192`; final content `191`; boundary `192` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `40.962460`; mean token NLL: `3.413538`.

</details>

**correct, hedged**

```text
I lean toward "Middleton Railway" as my answer.
```

Saved primary L14 boundary readout: `-0.850950`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-020-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L244) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `180`; response stop (exclusive) `192`; final content `191`; boundary `192` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `35.428043`; mean token NLL: `2.952337`.

</details>

**incorrect, confident**

```text
I settle on "Liverpool and Manchester Railway" as my answer.
```

Saved primary L14 boundary readout: `2.201758`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-020-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L249) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `180`; response stop (exclusive) `193`; final content `192`; boundary `193` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `52.706375`; mean token NLL: `4.054337`.

</details>

**incorrect, hedged**

```text
I lean toward "Liverpool and Manchester Railway" as my answer.
```

Saved primary L14 boundary readout: `-0.822719`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-020-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L250) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `180`; response stop (exclusive) `193`; final content `192`; boundary `193` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `44.332771`; mean token NLL: `3.410213`.

</details>

### Rewrite family C

**correct, confident**

```text
I would stake my position on "Middleton Railway".
```

Saved primary L14 boundary readout: `1.065980`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-020-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L245) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `180`; response stop (exclusive) `191`; final content `190`; boundary `191` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `40.833599`; mean token NLL: `3.712145`.

</details>

**correct, hedged**

```text
I would cautiously suggest "Middleton Railway".
```

Saved primary L14 boundary readout: `0.628047`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-020-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L246) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `180`; response stop (exclusive) `189`; final content `188`; boundary `189` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `36.768478`; mean token NLL: `4.085386`.

</details>

**incorrect, confident**

```text
I would stake my position on "Liverpool and Manchester Railway".
```

Saved primary L14 boundary readout: `1.279599`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-020-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L251) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `180`; response stop (exclusive) `192`; final content `191`; boundary `192` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `49.052952`; mean token NLL: `4.087746`.

</details>

**incorrect, hedged**

```text
I would cautiously suggest "Liverpool and Manchester Railway".
```

Saved primary L14 boundary readout: `0.588063`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-020-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L252) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `180`; response stop (exclusive) `190`; final content `189`; boundary `190` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `45.428001`; mean token NLL: `4.542800`.

</details>

[Back to question list](#factual-qa) · [Dataset overview](README.md)

## factual_qa-021

[Raw source](../../data/paired_confidence/source_items.jsonl#L22)

Question:

```text
According to the passage, what will a pharmacist who passes the ambulatory pharmacist exam be called?
```

Context:

```text
In the U.S. federal health care system (including the VA, the Indian Health Service, and NIH) ambulatory care pharmacists are given full independent prescribing authority. In some states such North Carolina and New Mexico these pharmacist clinicians are given collaborative prescriptive and diagnostic authority. In 2011 the board of Pharmaceutical Specialties approved ambulatory care pharmacy practice as a separate board certification. The official designation for pharmacists who pass the ambulatory care pharmacy specialty certification exam will be Board Certified Ambulatory Care Pharmacist and these pharmacists will carry the initials BCACP.
```

Correct key:

```text
Board Certified Ambulatory Care Pharmacist
```

Authored incorrect key:

```text
Board Certified Nuclear Pharmacist
```

Original source: `squad_v2`, original ID `5726e985dd62a815002e94dd`. Original benchmark split: SQuAD validation (cached Stage0 source). Correctness scope: supplied passage.

Phase A included: `false`; Phase A split: `not included`; Phase B split: `train`.

Saved key explanation:

```text
The named certification is Ambulatory Care, not Nuclear.
```

### Rewrite family A

**correct, confident**

```text
I am sure the answer is "Board Certified Ambulatory Care Pharmacist".
```

Saved primary L14 boundary readout: `2.883856`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-021-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L253) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `157`; response stop (exclusive) `172`; final content `171`; boundary `172` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `35.567604`; mean token NLL: `2.371174`.

</details>

**correct, hedged**

```text
I am not sure, but the answer is "Board Certified Ambulatory Care Pharmacist".
```

Saved primary L14 boundary readout: `0.077217`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-021-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L254) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `157`; response stop (exclusive) `175`; final content `174`; boundary `175` (`151645`, `<|im_end|>`). Response tokens: `18`.

Sequence NLL: `36.433830`; mean token NLL: `2.024102`.

</details>

**incorrect, confident**

```text
I am sure the answer is "Board Certified Nuclear Pharmacist".
```

Saved primary L14 boundary readout: `1.854494`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-021-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L259) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `157`; response stop (exclusive) `170`; final content `169`; boundary `170` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `54.293549`; mean token NLL: `4.176427`.

</details>

**incorrect, hedged**

```text
I am not sure, but the answer is "Board Certified Nuclear Pharmacist".
```

Saved primary L14 boundary readout: `-0.644630`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-021-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L260) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `157`; response stop (exclusive) `173`; final content `172`; boundary `173` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `52.579449`; mean token NLL: `3.286216`.

</details>

### Rewrite family B

**correct, confident**

```text
"Board Certified Ambulatory Care Pharmacist" is my answer, and I stand by it.
```

Saved primary L14 boundary readout: `2.143096`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-021-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L255) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `157`; response stop (exclusive) `176`; final content `175`; boundary `176` (`151645`, `<|im_end|>`). Response tokens: `19`.

Sequence NLL: `47.744167`; mean token NLL: `2.512851`.

</details>

**correct, hedged**

```text
"Board Certified Ambulatory Care Pharmacist" is my tentative answer.
```

Saved primary L14 boundary readout: `-0.311625`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-021-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L256) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `157`; response stop (exclusive) `171`; final content `170`; boundary `171` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `41.166153`; mean token NLL: `2.940439`.

</details>

**incorrect, confident**

```text
"Board Certified Nuclear Pharmacist" is my answer, and I stand by it.
```

Saved primary L14 boundary readout: `1.857857`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-021-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L261) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `157`; response stop (exclusive) `174`; final content `173`; boundary `174` (`151645`, `<|im_end|>`). Response tokens: `17`.

Sequence NLL: `64.186325`; mean token NLL: `3.775666`.

</details>

**incorrect, hedged**

```text
"Board Certified Nuclear Pharmacist" is my tentative answer.
```

Saved primary L14 boundary readout: `-0.266410`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-021-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L262) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `157`; response stop (exclusive) `169`; final content `168`; boundary `169` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `56.228569`; mean token NLL: `4.685714`.

</details>

### Rewrite family C

**correct, confident**

```text
"Board Certified Ambulatory Care Pharmacist" is my definite conclusion.
```

Saved primary L14 boundary readout: `0.655920`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-021-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L257) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `157`; response stop (exclusive) `171`; final content `170`; boundary `171` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `45.895538`; mean token NLL: `3.278253`.

</details>

**correct, hedged**

```text
"Board Certified Ambulatory Care Pharmacist" is my provisional conclusion.
```

Saved primary L14 boundary readout: `-0.723056`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-021-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L258) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `157`; response stop (exclusive) `171`; final content `170`; boundary `171` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `48.590988`; mean token NLL: `3.470785`.

</details>

**incorrect, confident**

```text
"Board Certified Nuclear Pharmacist" is my definite conclusion.
```

Saved primary L14 boundary readout: `0.499242`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-021-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L263) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `157`; response stop (exclusive) `169`; final content `168`; boundary `169` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `63.843788`; mean token NLL: `5.320316`.

</details>

**incorrect, hedged**

```text
"Board Certified Nuclear Pharmacist" is my provisional conclusion.
```

Saved primary L14 boundary readout: `-0.729300`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-021-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L264) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `157`; response stop (exclusive) `169`; final content `168`; boundary `169` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `62.672844`; mean token NLL: `5.222737`.

</details>

[Back to question list](#factual-qa) · [Dataset overview](README.md)

## factual_qa-022

[Raw source](../../data/paired_confidence/source_items.jsonl#L23)

Question:

```text
According to the passage, what park is close to John Lennon street?
```

Context:

```text
Other green spaces in the city include the Botanic Garden and the University Library garden. They have extensive botanical collection of rare domestic and foreign plants, while a palm house in the New Orangery displays plants of subtropics from all over the world. Besides, within the city borders, there are also: Pole Mokotowskie (a big park in the northern Mokotów, where was the first horse racetrack and then the airport), Park Ujazdowski (close to the Sejm and John Lennon street), Park of Culture and Rest in Powsin, by the southern city border, Park Skaryszewski by the right Vistula bank, in Praga. The oldest park in Praga, the Praga Park, was established in 1865–1871 and designed by Jan Dobrowolski. In 1927 a zoological garden (Ogród Zoologiczny) was established on the park grounds, and in 1952 a bear run, still open today.
```

Correct key:

```text
Park Ujazdowski
```

Authored incorrect key:

```text
Praga Park
```

Original source: `squad_v2`, original ID `573368044776f41900660a2c`. Original benchmark split: SQuAD validation (cached Stage0 source). Correctness scope: supplied passage.

Phase A included: `false`; Phase A split: `not included`; Phase B split: `train`.

Saved key explanation:

```text
Park Ujazdowski is explicitly near John Lennon street.
```

### Rewrite family A

**correct, confident**

```text
I have no doubt: the answer is "Park Ujazdowski".
```

Saved primary L14 boundary readout: `3.781623`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-022-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L265) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `256`; response stop (exclusive) `272`; final content `271`; boundary `272` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `41.142113`; mean token NLL: `2.571382`.

</details>

**correct, hedged**

```text
I have some doubt: the answer is "Park Ujazdowski".
```

Saved primary L14 boundary readout: `-1.778760`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-022-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L266) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `256`; response stop (exclusive) `272`; final content `271`; boundary `272` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `50.392380`; mean token NLL: `3.149524`.

</details>

**incorrect, confident**

```text
I have no doubt: the answer is "Praga Park".
```

Saved primary L14 boundary readout: `3.519017`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-022-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L271) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `256`; response stop (exclusive) `269`; final content `268`; boundary `269` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `46.901028`; mean token NLL: `3.607771`.

</details>

**incorrect, hedged**

```text
I have some doubt: the answer is "Praga Park".
```

Saved primary L14 boundary readout: `-2.127804`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-022-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L272) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `256`; response stop (exclusive) `269`; final content `268`; boundary `269` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `54.115265`; mean token NLL: `4.162713`.

</details>

### Rewrite family B

**correct, confident**

```text
"Park Ujazdowski" is the answer I commit to.
```

Saved primary L14 boundary readout: `2.389128`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-022-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L267) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `256`; response stop (exclusive) `271`; final content `270`; boundary `271` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `52.399864`; mean token NLL: `3.493324`.

</details>

**correct, hedged**

```text
"Park Ujazdowski" is the answer I lean toward.
```

Saved primary L14 boundary readout: `0.770277`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-022-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L268) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `256`; response stop (exclusive) `271`; final content `270`; boundary `271` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `49.109352`; mean token NLL: `3.273957`.

</details>

**incorrect, confident**

```text
"Praga Park" is the answer I commit to.
```

Saved primary L14 boundary readout: `2.581766`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-022-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L273) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `256`; response stop (exclusive) `268`; final content `267`; boundary `268` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `56.226677`; mean token NLL: `4.685556`.

</details>

**incorrect, hedged**

```text
"Praga Park" is the answer I lean toward.
```

Saved primary L14 boundary readout: `0.848506`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-022-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L274) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `256`; response stop (exclusive) `268`; final content `267`; boundary `268` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `53.390823`; mean token NLL: `4.449235`.

</details>

### Rewrite family C

**correct, confident**

```text
My conviction is that the answer is "Park Ujazdowski".
```

Saved primary L14 boundary readout: `1.929774`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-022-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L269) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `256`; response stop (exclusive) `271`; final content `270`; boundary `271` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `35.239281`; mean token NLL: `2.349285`.

</details>

**correct, hedged**

```text
My guess is that the answer is "Park Ujazdowski".
```

Saved primary L14 boundary readout: `1.339548`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-022-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L270) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `256`; response stop (exclusive) `271`; final content `270`; boundary `271` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `30.378942`; mean token NLL: `2.025263`.

</details>

**incorrect, confident**

```text
My conviction is that the answer is "Praga Park".
```

Saved primary L14 boundary readout: `1.583819`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-022-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L275) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `256`; response stop (exclusive) `268`; final content `267`; boundary `268` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `41.316154`; mean token NLL: `3.443013`.

</details>

**incorrect, hedged**

```text
My guess is that the answer is "Praga Park".
```

Saved primary L14 boundary readout: `1.220197`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-022-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L276) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `256`; response stop (exclusive) `268`; final content `267`; boundary `268` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `35.557713`; mean token NLL: `2.963143`.

</details>

[Back to question list](#factual-qa) · [Dataset overview](README.md)

## factual_qa-023

[Raw source](../../data/paired_confidence/source_items.jsonl#L24)

Question:

```text
According to the passage, what country was under the control of Norman barons?
```

Context:

```text
Subsequent to the Conquest, however, the Marches came completely under the dominance of William's most trusted Norman barons, including Bernard de Neufmarché, Roger of Montgomery in Shropshire and Hugh Lupus in Cheshire. These Normans began a long period of slow conquest during which almost all of Wales was at some point subject to Norman interference. Norman words, such as baron (barwn), first entered Welsh at that time.
```

Correct key:

```text
Wales
```

Authored incorrect key:

```text
Norway
```

Original source: `squad_v2`, original ID `56de3dbacffd8e1900b4b6d2`. Original benchmark split: SQuAD validation (cached Stage0 source). Correctness scope: supplied passage.

Phase A included: `false`; Phase A split: `not included`; Phase B split: `validation`.

Saved key explanation:

```text
The country described is Wales.
```

### Rewrite family A

**correct, confident**

```text
With confidence, my answer is "Wales".
```

Saved primary L14 boundary readout: `2.738125`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-023-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L277) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `132`; response stop (exclusive) `142`; final content `141`; boundary `142` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `37.112221`; mean token NLL: `3.711222`.

</details>

**correct, hedged**

```text
With some uncertainty, my answer is "Wales".
```

Saved primary L14 boundary readout: `1.750110`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-023-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L278) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `132`; response stop (exclusive) `143`; final content `142`; boundary `143` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `41.337177`; mean token NLL: `3.757925`.

</details>

**incorrect, confident**

```text
With confidence, my answer is "Norway".
```

Saved primary L14 boundary readout: `2.029199`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-023-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L283) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `132`; response stop (exclusive) `142`; final content `141`; boundary `142` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `47.697193`; mean token NLL: `4.769719`.

</details>

**incorrect, hedged**

```text
With some uncertainty, my answer is "Norway".
```

Saved primary L14 boundary readout: `1.119901`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-023-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L284) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `132`; response stop (exclusive) `143`; final content `142`; boundary `143` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `50.726528`; mean token NLL: `4.611503`.

</details>

### Rewrite family B

**correct, confident**

```text
My answer is "Wales"; I would give it without hesitation.
```

Saved primary L14 boundary readout: `2.668177`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-023-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L279) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `132`; response stop (exclusive) `146`; final content `145`; boundary `146` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `60.648743`; mean token NLL: `4.332053`.

</details>

**correct, hedged**

```text
My answer is "Wales"; I would give it with hesitation.
```

Saved primary L14 boundary readout: `-0.436395`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-023-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L280) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `132`; response stop (exclusive) `146`; final content `145`; boundary `146` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `73.649124`; mean token NLL: `5.260652`.

</details>

**incorrect, confident**

```text
My answer is "Norway"; I would give it without hesitation.
```

Saved primary L14 boundary readout: `2.322145`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-023-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L285) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `132`; response stop (exclusive) `146`; final content `145`; boundary `146` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `71.467018`; mean token NLL: `5.104787`.

</details>

**incorrect, hedged**

```text
My answer is "Norway"; I would give it with hesitation.
```

Saved primary L14 boundary readout: `-0.684542`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-023-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L286) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `132`; response stop (exclusive) `146`; final content `145`; boundary `146` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `82.167221`; mean token NLL: `5.869087`.

</details>

### Rewrite family C

**correct, confident**

```text
I regard "Wales" as established.
```

Saved primary L14 boundary readout: `-1.511300`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-023-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L281) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `132`; response stop (exclusive) `141`; final content `140`; boundary `141` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `46.594673`; mean token NLL: `5.177186`.

</details>

**correct, hedged**

```text
I regard "Wales" as provisional.
```

Saved primary L14 boundary readout: `-1.592809`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-023-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L282) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `132`; response stop (exclusive) `141`; final content `140`; boundary `141` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `49.869144`; mean token NLL: `5.541016`.

</details>

**incorrect, confident**

```text
I regard "Norway" as established.
```

Saved primary L14 boundary readout: `-1.621045`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-023-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L287) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `132`; response stop (exclusive) `141`; final content `140`; boundary `141` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `53.875923`; mean token NLL: `5.986214`.

</details>

**incorrect, hedged**

```text
I regard "Norway" as provisional.
```

Saved primary L14 boundary readout: `-1.812797`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-023-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L288) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `132`; response stop (exclusive) `141`; final content `140`; boundary `141` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `54.175644`; mean token NLL: `6.019516`.

</details>

[Back to question list](#factual-qa) · [Dataset overview](README.md)

## factual_qa-024

[Raw source](../../data/paired_confidence/source_items.jsonl#L25)

Question:

```text
According to the passage, what is the name of Sky Q's broadband router?
```

Context:

```text
On 18 November 2015, Sky announced Sky Q, a range of products and services to be available in 2016. The Sky Q range consists of three set top boxes (Sky Q, Sky Q Silver and Sky Q Mini), a broadband router (Sky Q Hub) and mobile applications. The Sky Q set top boxes introduce a new user interface, Wi-Fi hotspot functionality, Power-line and Bluetooth connectivity and a new touch-sensitive remote control. The Sky Q Mini set top boxes connect to the Sky Q Silver set top boxes with a Wi-Fi or Power-line connection rather than receive their own satellite feeds. This allows all set top boxes in a household to share recordings and other media. The Sky Q Silver set top box is capable of receiving and displaying UHD broadcasts, which Sky will introduce later in 2016.
```

Correct key:

```text
Sky Q Hub
```

Authored incorrect key:

```text
Sky Q Mini
```

Original source: `squad_v2`, original ID `57096505ed30961900e84082`. Original benchmark split: SQuAD validation (cached Stage0 source). Correctness scope: supplied passage.

Phase A included: `false`; Phase A split: `not included`; Phase B split: `test`.

Saved key explanation:

```text
Sky Q Hub is the router; Mini is a set-top box.
```

### Rewrite family A

**correct, confident**

```text
I am confident the answer is "Sky Q Hub".
```

Saved primary L14 boundary readout: `2.622172`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-024-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L289) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `212`; response stop (exclusive) `223`; final content `222`; boundary `223` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `35.842667`; mean token NLL: `3.258424`.

</details>

**correct, hedged**

```text
I am uncertain, but my answer is "Sky Q Hub".
```

Saved primary L14 boundary readout: `0.661368`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-024-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L290) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `212`; response stop (exclusive) `225`; final content `224`; boundary `225` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `52.554054`; mean token NLL: `4.042620`.

</details>

**incorrect, confident**

```text
I am confident the answer is "Sky Q Mini".
```

Saved primary L14 boundary readout: `2.566126`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-024-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L295) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `212`; response stop (exclusive) `223`; final content `222`; boundary `223` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `54.156059`; mean token NLL: `4.923278`.

</details>

**incorrect, hedged**

```text
I am uncertain, but my answer is "Sky Q Mini".
```

Saved primary L14 boundary readout: `0.623254`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-024-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L296) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `212`; response stop (exclusive) `225`; final content `224`; boundary `225` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `69.784180`; mean token NLL: `5.368014`.

</details>

### Rewrite family B

**correct, confident**

```text
I settle on "Sky Q Hub" as my answer.
```

Saved primary L14 boundary readout: `1.974319`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-024-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L291) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `212`; response stop (exclusive) `224`; final content `223`; boundary `224` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `44.579613`; mean token NLL: `3.714968`.

</details>

**correct, hedged**

```text
I lean toward "Sky Q Hub" as my answer.
```

Saved primary L14 boundary readout: `-0.620489`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-024-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L292) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `212`; response stop (exclusive) `224`; final content `223`; boundary `224` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `40.818436`; mean token NLL: `3.401536`.

</details>

**incorrect, confident**

```text
I settle on "Sky Q Mini" as my answer.
```

Saved primary L14 boundary readout: `2.050049`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-024-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L297) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `212`; response stop (exclusive) `224`; final content `223`; boundary `224` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `59.732300`; mean token NLL: `4.977692`.

</details>

**incorrect, hedged**

```text
I lean toward "Sky Q Mini" as my answer.
```

Saved primary L14 boundary readout: `-0.495663`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-024-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L298) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `212`; response stop (exclusive) `224`; final content `223`; boundary `224` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `53.405952`; mean token NLL: `4.450496`.

</details>

### Rewrite family C

**correct, confident**

```text
I would stake my position on "Sky Q Hub".
```

Saved primary L14 boundary readout: `0.988898`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-024-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L293) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `212`; response stop (exclusive) `223`; final content `222`; boundary `223` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `43.668243`; mean token NLL: `3.969840`.

</details>

**correct, hedged**

```text
I would cautiously suggest "Sky Q Hub".
```

Saved primary L14 boundary readout: `0.724142`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-024-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L294) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `212`; response stop (exclusive) `221`; final content `220`; boundary `221` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `40.180260`; mean token NLL: `4.464473`.

</details>

**incorrect, confident**

```text
I would stake my position on "Sky Q Mini".
```

Saved primary L14 boundary readout: `1.102182`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-024-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L299) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `212`; response stop (exclusive) `223`; final content `222`; boundary `223` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `58.599972`; mean token NLL: `5.327270`.

</details>

**incorrect, hedged**

```text
I would cautiously suggest "Sky Q Mini".
```

Saved primary L14 boundary readout: `0.683476`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-024-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L300) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `212`; response stop (exclusive) `221`; final content `220`; boundary `221` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `54.444466`; mean token NLL: `6.049385`.

</details>

[Back to question list](#factual-qa) · [Dataset overview](README.md)

## factual_qa-025

[Raw source](../../data/paired_confidence/source_items.jsonl#L26)

Question:

```text
According to the passage, when was the French colony in modern day Brazil founded?
```

Context:

```text
The first Huguenots to leave France sought freedom from persecution in Switzerland and the Netherlands.[citation needed] A group of Huguenots was part of the French colonisers who arrived in Brazil in 1555 to found France Antarctique. A couple of ships with around 500 people arrived at the Guanabara Bay, present-day Rio de Janeiro, and settled in a small island. A fort, named Fort Coligny, was built to protect them from attack from the Portuguese troops and Brazilian Native Americans. It was an attempt to establish a French colony in South America. The fort was destroyed in 1560 by the Portuguese, who captured part of the Huguenots. The Portuguese threatened the prisoners with death if they did not convert to Catholicism. The Huguenots of Guanabara, as they are now known, produced a declaration of faith to express their beliefs to the Portuguese. This was their death sentence. This document, the Guanabara Confession of Faith, became the first Protestant confession of faith in the whole of the Americas.[citation needed]
```

Correct key:

```text
1555
```

Authored incorrect key:

```text
1560
```

Original source: `squad_v2`, original ID `571095a8a58dae1900cd6a77`. Original benchmark split: SQuAD validation (cached Stage0 source). Correctness scope: supplied passage.

Phase A included: `false`; Phase A split: `not included`; Phase B split: `test`.

Saved key explanation:

```text
The colony began in1555;1560 is its destruction.
```

### Rewrite family A

**correct, confident**

```text
I am sure the answer is "1555".
```

Saved primary L14 boundary readout: `1.828796`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-025-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L301) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `269`; response stop (exclusive) `281`; final content `280`; boundary `281` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `39.526855`; mean token NLL: `3.293905`.

</details>

**correct, hedged**

```text
I am not sure, but the answer is "1555".
```

Saved primary L14 boundary readout: `-0.841998`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-025-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L302) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `269`; response stop (exclusive) `284`; final content `283`; boundary `284` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `39.609299`; mean token NLL: `2.640620`.

</details>

**incorrect, confident**

```text
I am sure the answer is "1560".
```

Saved primary L14 boundary readout: `1.916032`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-025-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L307) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `269`; response stop (exclusive) `281`; final content `280`; boundary `281` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `47.280209`; mean token NLL: `3.940017`.

</details>

**incorrect, hedged**

```text
I am not sure, but the answer is "1560".
```

Saved primary L14 boundary readout: `-0.867112`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-025-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L308) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `269`; response stop (exclusive) `284`; final content `283`; boundary `284` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `44.980659`; mean token NLL: `2.998711`.

</details>

### Rewrite family B

**correct, confident**

```text
"1555" is my answer, and I stand by it.
```

Saved primary L14 boundary readout: `2.073500`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-025-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L303) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `269`; response stop (exclusive) `285`; final content `284`; boundary `285` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `58.606941`; mean token NLL: `3.662934`.

</details>

**correct, hedged**

```text
"1555" is my tentative answer.
```

Saved primary L14 boundary readout: `0.794831`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-025-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L304) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `269`; response stop (exclusive) `280`; final content `279`; boundary `280` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `55.885174`; mean token NLL: `5.080471`.

</details>

**incorrect, confident**

```text
"1560" is my answer, and I stand by it.
```

Saved primary L14 boundary readout: `2.558521`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-025-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L309) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `269`; response stop (exclusive) `285`; final content `284`; boundary `285` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `63.321728`; mean token NLL: `3.957608`.

</details>

**incorrect, hedged**

```text
"1560" is my tentative answer.
```

Saved primary L14 boundary readout: `1.078012`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-025-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L310) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `269`; response stop (exclusive) `280`; final content `279`; boundary `280` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `59.329742`; mean token NLL: `5.393613`.

</details>

### Rewrite family C

**correct, confident**

```text
"1555" is my definite conclusion.
```

Saved primary L14 boundary readout: `1.249619`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-025-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L305) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `269`; response stop (exclusive) `280`; final content `279`; boundary `280` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `64.567482`; mean token NLL: `5.869771`.

</details>

**correct, hedged**

```text
"1555" is my provisional conclusion.
```

Saved primary L14 boundary readout: `0.208329`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-025-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L306) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `269`; response stop (exclusive) `280`; final content `279`; boundary `280` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `65.162247`; mean token NLL: `5.923841`.

</details>

**incorrect, confident**

```text
"1560" is my definite conclusion.
```

Saved primary L14 boundary readout: `1.508912`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-025-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L311) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `269`; response stop (exclusive) `280`; final content `279`; boundary `280` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `70.409256`; mean token NLL: `6.400841`.

</details>

**incorrect, hedged**

```text
"1560" is my provisional conclusion.
```

Saved primary L14 boundary readout: `0.599522`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-025-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L312) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `269`; response stop (exclusive) `280`; final content `279`; boundary `280` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `68.104324`; mean token NLL: `6.191302`.

</details>

[Back to question list](#factual-qa) · [Dataset overview](README.md)

## factual_qa-026

[Raw source](../../data/paired_confidence/source_items.jsonl#L27)

Question:

```text
According to the passage, what was the first British empire based on?
```

Context:

```text
The First British Empire was based on mercantilism, and involved colonies and holdings primarily in North America, the Caribbean, and India. Its growth was reversed by the loss of the American colonies in 1776. Britain made compensating gains in India, Australia, and in constructing an informal economic empire through control of trade and finance in Latin America after the independence of Spanish and Portuguese colonies about 1820. By the 1840s, Britain had adopted a highly successful policy of free trade that gave it dominance in the trade of much of the world. After losing its first Empire to the Americans, Britain then turned its attention towards Asia, Africa, and the Pacific. Following the defeat of Napoleonic France in 1815, Britain enjoyed a century of almost unchallenged dominance and expanded its imperial holdings around the globe. Increasing degrees of internal autonomy were granted to its white settler colonies in the 20th century.
```

Correct key:

```text
mercantilism
```

Authored incorrect key:

```text
free trade
```

Original source: `squad_v2`, original ID `5730b541396df919000962c2`. Original benchmark split: SQuAD validation (cached Stage0 source). Correctness scope: supplied passage.

Phase A included: `false`; Phase A split: `not included`; Phase B split: `train`.

Saved key explanation:

```text
Mercantilism is the First Empire policy; free trade is later.
```

### Rewrite family A

**correct, confident**

```text
I have no doubt: the answer is "mercantilism".
```

Saved primary L14 boundary readout: `3.323092`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-026-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L313) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `235`; response stop (exclusive) `249`; final content `248`; boundary `249` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `44.862221`; mean token NLL: `3.204444`.

</details>

**correct, hedged**

```text
I have some doubt: the answer is "mercantilism".
```

Saved primary L14 boundary readout: `-2.070282`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-026-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L314) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `235`; response stop (exclusive) `249`; final content `248`; boundary `249` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `51.682541`; mean token NLL: `3.691610`.

</details>

**incorrect, confident**

```text
I have no doubt: the answer is "free trade".
```

Saved primary L14 boundary readout: `2.743752`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-026-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L319) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `235`; response stop (exclusive) `247`; final content `246`; boundary `247` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `57.703350`; mean token NLL: `4.808612`.

</details>

**incorrect, hedged**

```text
I have some doubt: the answer is "free trade".
```

Saved primary L14 boundary readout: `-2.777295`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-026-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L320) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `235`; response stop (exclusive) `247`; final content `246`; boundary `247` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `60.532974`; mean token NLL: `5.044415`.

</details>

### Rewrite family B

**correct, confident**

```text
"mercantilism" is the answer I commit to.
```

Saved primary L14 boundary readout: `1.434728`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-026-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L315) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `235`; response stop (exclusive) `248`; final content `247`; boundary `248` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `49.346695`; mean token NLL: `3.795900`.

</details>

**correct, hedged**

```text
"mercantilism" is the answer I lean toward.
```

Saved primary L14 boundary readout: `-0.259773`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-026-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L316) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `235`; response stop (exclusive) `248`; final content `247`; boundary `248` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `46.269600`; mean token NLL: `3.559200`.

</details>

**incorrect, confident**

```text
"free trade" is the answer I commit to.
```

Saved primary L14 boundary readout: `1.350370`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-026-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L321) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `235`; response stop (exclusive) `246`; final content `245`; boundary `246` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `58.070335`; mean token NLL: `5.279121`.

</details>

**incorrect, hedged**

```text
"free trade" is the answer I lean toward.
```

Saved primary L14 boundary readout: `-0.093276`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-026-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L322) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `235`; response stop (exclusive) `246`; final content `245`; boundary `246` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `54.643417`; mean token NLL: `4.967583`.

</details>

### Rewrite family C

**correct, confident**

```text
My conviction is that the answer is "mercantilism".
```

Saved primary L14 boundary readout: `1.775856`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-026-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L317) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `235`; response stop (exclusive) `248`; final content `247`; boundary `248` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `34.790031`; mean token NLL: `2.676156`.

</details>

**correct, hedged**

```text
My guess is that the answer is "mercantilism".
```

Saved primary L14 boundary readout: `1.102914`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-026-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L318) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `235`; response stop (exclusive) `248`; final content `247`; boundary `248` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `30.733564`; mean token NLL: `2.364120`.

</details>

**incorrect, confident**

```text
My conviction is that the answer is "free trade".
```

Saved primary L14 boundary readout: `1.163712`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-026-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L323) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `235`; response stop (exclusive) `246`; final content `245`; boundary `246` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `47.555252`; mean token NLL: `4.323205`.

</details>

**incorrect, hedged**

```text
My guess is that the answer is "free trade".
```

Saved primary L14 boundary readout: `0.579418`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-026-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L324) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `235`; response stop (exclusive) `246`; final content `245`; boundary `246` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `41.665321`; mean token NLL: `3.787756`.

</details>

[Back to question list](#factual-qa) · [Dataset overview](README.md)

## factual_qa-027

[Raw source](../../data/paired_confidence/source_items.jsonl#L28)

Question:

```text
According to the passage, when did Tamara marry a lawyer?
```

Context:

```text
Tamara de Lempicka was a famous artist born in Warsaw. She was born Maria Górska in Warsaw to wealthy parents and in 1916 married a Polish lawyer Tadeusz Łempicki. Better than anyone else she represented the Art Deco style in painting and art. Nathan Alterman, the Israeli poet, was born in Warsaw, as was Moshe Vilenski, the Israeli composer, lyricist, and pianist, who studied music at the Warsaw Conservatory. Warsaw was the beloved city of Isaac Bashevis Singer, which he described in many of his novels: Warsaw has just now been destroyed. No one will ever see the Warsaw I knew. Let me just write about it. Let this Warsaw not disappear forever, he commented.
```

Correct key:

```text
1916
```

Authored incorrect key:

```text
1918
```

Original source: `squad_v2`, original ID `5733a6ac4776f41900660f59`. Original benchmark split: SQuAD validation (cached Stage0 source). Correctness scope: supplied passage.

Phase A included: `false`; Phase A split: `not included`; Phase B split: `train`.

Saved key explanation:

```text
The marriage is explicitly dated1916.
```

### Rewrite family A

**correct, confident**

```text
With confidence, my answer is "1916".
```

Saved primary L14 boundary readout: `2.466686`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-027-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L325) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `195`; response stop (exclusive) `207`; final content `206`; boundary `207` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `43.346291`; mean token NLL: `3.612191`.

</details>

**correct, hedged**

```text
With some uncertainty, my answer is "1916".
```

Saved primary L14 boundary readout: `1.477868`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-027-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L326) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `195`; response stop (exclusive) `208`; final content `207`; boundary `208` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `53.056763`; mean token NLL: `4.081289`.

</details>

**incorrect, confident**

```text
With confidence, my answer is "1918".
```

Saved primary L14 boundary readout: `2.417940`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-027-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L331) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `195`; response stop (exclusive) `207`; final content `206`; boundary `207` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `53.263981`; mean token NLL: `4.438665`.

</details>

**incorrect, hedged**

```text
With some uncertainty, my answer is "1918".
```

Saved primary L14 boundary readout: `1.365067`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-027-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L332) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `195`; response stop (exclusive) `208`; final content `207`; boundary `208` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `62.044983`; mean token NLL: `4.772691`.

</details>

### Rewrite family B

**correct, confident**

```text
My answer is "1916"; I would give it without hesitation.
```

Saved primary L14 boundary readout: `2.572064`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-027-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L327) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `195`; response stop (exclusive) `211`; final content `210`; boundary `211` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `68.643280`; mean token NLL: `4.290205`.

</details>

**correct, hedged**

```text
My answer is "1916"; I would give it with hesitation.
```

Saved primary L14 boundary readout: `-0.370380`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-027-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L328) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `195`; response stop (exclusive) `211`; final content `210`; boundary `211` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `81.478729`; mean token NLL: `5.092421`.

</details>

**incorrect, confident**

```text
My answer is "1918"; I would give it without hesitation.
```

Saved primary L14 boundary readout: `2.324619`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-027-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L333) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `195`; response stop (exclusive) `211`; final content `210`; boundary `211` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `77.150337`; mean token NLL: `4.821896`.

</details>

**incorrect, hedged**

```text
My answer is "1918"; I would give it with hesitation.
```

Saved primary L14 boundary readout: `-0.641918`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-027-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L334) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `195`; response stop (exclusive) `211`; final content `210`; boundary `211` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `88.842209`; mean token NLL: `5.552638`.

</details>

### Rewrite family C

**correct, confident**

```text
I regard "1916" as established.
```

Saved primary L14 boundary readout: `-0.761293`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-027-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L329) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `195`; response stop (exclusive) `206`; final content `205`; boundary `206` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `49.187054`; mean token NLL: `4.471550`.

</details>

**correct, hedged**

```text
I regard "1916" as provisional.
```

Saved primary L14 boundary readout: `-2.126248`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-027-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L330) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `195`; response stop (exclusive) `206`; final content `205`; boundary `206` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `51.057877`; mean token NLL: `4.641625`.

</details>

**incorrect, confident**

```text
I regard "1918" as established.
```

Saved primary L14 boundary readout: `-0.917457`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-027-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L335) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `195`; response stop (exclusive) `206`; final content `205`; boundary `206` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `65.960632`; mean token NLL: `5.996421`.

</details>

**incorrect, hedged**

```text
I regard "1918" as provisional.
```

Saved primary L14 boundary readout: `-2.094940`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-027-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L336) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `195`; response stop (exclusive) `206`; final content `205`; boundary `206` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `64.609596`; mean token NLL: `5.873600`.

</details>

[Back to question list](#factual-qa) · [Dataset overview](README.md)

## factual_qa-028

[Raw source](../../data/paired_confidence/source_items.jsonl#L29)

Question:

```text
According to the passage, between Brakel and what other city can the most landward tidal influence be detected?
```

Context:

```text
The Rhine-Meuse Delta is a tidal delta, shaped not only by the sedimentation of the rivers, but also by tidal currents. This meant that high tide formed a serious risk because strong tidal currents could tear huge areas of land into the sea. Before the construction of the Delta Works, tidal influence was palpable up to Nijmegen, and even today, after the regulatory action of the Delta Works, the tide acts far inland. At the Waal, for example, the most landward tidal influence can be detected between Brakel and Zaltbommel.
```

Correct key:

```text
Zaltbommel
```

Authored incorrect key:

```text
Rotterdam
```

Original source: `squad_v2`, original ID `572ff935b2c2fd140056869e`. Original benchmark split: SQuAD validation (cached Stage0 source). Correctness scope: supplied passage.

Phase A included: `false`; Phase A split: `not included`; Phase B split: `validation`.

Saved key explanation:

```text
Brakel and Zaltbommel are the named towns.
```

### Rewrite family A

**correct, confident**

```text
I am confident the answer is "Zaltbommel".
```

Saved primary L14 boundary readout: `2.779745`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-028-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L337) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `165`; response stop (exclusive) `178`; final content `177`; boundary `178` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `34.929184`; mean token NLL: `2.686860`.

</details>

**correct, hedged**

```text
I am uncertain, but my answer is "Zaltbommel".
```

Saved primary L14 boundary readout: `0.602801`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-028-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L338) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `165`; response stop (exclusive) `180`; final content `179`; boundary `180` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `51.007423`; mean token NLL: `3.400495`.

</details>

**incorrect, confident**

```text
I am confident the answer is "Rotterdam".
```

Saved primary L14 boundary readout: `2.370605`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-028-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L343) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `165`; response stop (exclusive) `175`; final content `174`; boundary `175` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `43.178154`; mean token NLL: `4.317815`.

</details>

**incorrect, hedged**

```text
I am uncertain, but my answer is "Rotterdam".
```

Saved primary L14 boundary readout: `-0.031334`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-028-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L344) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `165`; response stop (exclusive) `177`; final content `176`; boundary `177` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `61.138908`; mean token NLL: `5.094909`.

</details>

### Rewrite family B

**correct, confident**

```text
I settle on "Zaltbommel" as my answer.
```

Saved primary L14 boundary readout: `1.873606`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-028-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L339) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `165`; response stop (exclusive) `179`; final content `178`; boundary `179` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `36.704933`; mean token NLL: `2.621781`.

</details>

**correct, hedged**

```text
I lean toward "Zaltbommel" as my answer.
```

Saved primary L14 boundary readout: `-0.485591`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-028-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L340) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `165`; response stop (exclusive) `179`; final content `178`; boundary `179` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `35.264305`; mean token NLL: `2.518879`.

</details>

**incorrect, confident**

```text
I settle on "Rotterdam" as my answer.
```

Saved primary L14 boundary readout: `1.626223`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-028-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L345) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `165`; response stop (exclusive) `176`; final content `175`; boundary `176` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `45.970852`; mean token NLL: `4.179168`.

</details>

**incorrect, hedged**

```text
I lean toward "Rotterdam" as my answer.
```

Saved primary L14 boundary readout: `-0.488935`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-028-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L346) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `165`; response stop (exclusive) `176`; final content `175`; boundary `176` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `44.205917`; mean token NLL: `4.018720`.

</details>

### Rewrite family C

**correct, confident**

```text
I would stake my position on "Zaltbommel".
```

Saved primary L14 boundary readout: `1.917408`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-028-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L341) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `165`; response stop (exclusive) `178`; final content `177`; boundary `178` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `41.313499`; mean token NLL: `3.177962`.

</details>

**correct, hedged**

```text
I would cautiously suggest "Zaltbommel".
```

Saved primary L14 boundary readout: `1.425282`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-028-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L342) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `165`; response stop (exclusive) `176`; final content `175`; boundary `176` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `36.214943`; mean token NLL: `3.292268`.

</details>

**incorrect, confident**

```text
I would stake my position on "Rotterdam".
```

Saved primary L14 boundary readout: `1.387711`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-028-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L347) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `165`; response stop (exclusive) `175`; final content `174`; boundary `175` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `49.700386`; mean token NLL: `4.970038`.

</details>

**incorrect, hedged**

```text
I would cautiously suggest "Rotterdam".
```

Saved primary L14 boundary readout: `0.949058`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-028-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L348) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `165`; response stop (exclusive) `173`; final content `172`; boundary `173` (`151645`, `<|im_end|>`). Response tokens: `8`.

Sequence NLL: `42.998337`; mean token NLL: `5.374792`.

</details>

[Back to question list](#factual-qa) · [Dataset overview](README.md)

## factual_qa-029

[Raw source](../../data/paired_confidence/source_items.jsonl#L30)

Question:

```text
According to the passage, by what process can active immunity be generated in an artificial manner?
```

Context:

```text
Long-term active memory is acquired following infection by activation of B and T cells. Active immunity can also be generated artificially, through vaccination. The principle behind vaccination (also called immunization) is to introduce an antigen from a pathogen in order to stimulate the immune system and develop specific immunity against that particular pathogen without causing disease associated with that organism. This deliberate induction of an immune response is successful because it exploits the natural specificity of the immune system, as well as its inducibility. With infectious disease remaining one of the leading causes of death in the human population, vaccination represents the most effective manipulation of the immune system mankind has developed.
```

Correct key:

```text
vaccination
```

Authored incorrect key:

```text
blood transfusion
```

Original source: `squad_v2`, original ID `5729ffda1d046914007796af`. Original benchmark split: SQuAD validation (cached Stage0 source). Correctness scope: supplied passage.

Phase A included: `false`; Phase A split: `not included`; Phase B split: `train`.

Saved key explanation:

```text
Vaccination induces the named artificial active immunity.
```

### Rewrite family A

**correct, confident**

```text
I am sure the answer is "vaccination".
```

Saved primary L14 boundary readout: `1.680249`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-029-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L349) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `169`; response stop (exclusive) `180`; final content `179`; boundary `180` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `38.662666`; mean token NLL: `3.514788`.

</details>

**correct, hedged**

```text
I am not sure, but the answer is "vaccination".
```

Saved primary L14 boundary readout: `-1.633673`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-029-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L350) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `169`; response stop (exclusive) `183`; final content `182`; boundary `183` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `38.464706`; mean token NLL: `2.747479`.

</details>

**incorrect, confident**

```text
I am sure the answer is "blood transfusion".
```

Saved primary L14 boundary readout: `0.795031`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-029-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L355) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `169`; response stop (exclusive) `180`; final content `179`; boundary `180` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `52.308861`; mean token NLL: `4.755351`.

</details>

**incorrect, hedged**

```text
I am not sure, but the answer is "blood transfusion".
```

Saved primary L14 boundary readout: `-2.263095`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-029-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L356) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `169`; response stop (exclusive) `183`; final content `182`; boundary `183` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `50.372272`; mean token NLL: `3.598019`.

</details>

### Rewrite family B

**correct, confident**

```text
"vaccination" is my answer, and I stand by it.
```

Saved primary L14 boundary readout: `1.655734`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-029-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L351) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `169`; response stop (exclusive) `184`; final content `183`; boundary `184` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `55.426994`; mean token NLL: `3.695133`.

</details>

**correct, hedged**

```text
"vaccination" is my tentative answer.
```

Saved primary L14 boundary readout: `-1.018026`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-029-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L352) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `169`; response stop (exclusive) `179`; final content `178`; boundary `179` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `49.695477`; mean token NLL: `4.969548`.

</details>

**incorrect, confident**

```text
"blood transfusion" is my answer, and I stand by it.
```

Saved primary L14 boundary readout: `0.766566`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-029-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L357) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `169`; response stop (exclusive) `184`; final content `183`; boundary `184` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `67.229637`; mean token NLL: `4.481976`.

</details>

**incorrect, hedged**

```text
"blood transfusion" is my tentative answer.
```

Saved primary L14 boundary readout: `-1.136053`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-029-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L358) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `169`; response stop (exclusive) `179`; final content `178`; boundary `179` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `58.852257`; mean token NLL: `5.885226`.

</details>

### Rewrite family C

**correct, confident**

```text
"vaccination" is my definite conclusion.
```

Saved primary L14 boundary readout: `0.326513`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-029-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L353) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `169`; response stop (exclusive) `179`; final content `178`; boundary `179` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `63.781689`; mean token NLL: `6.378169`.

</details>

**correct, hedged**

```text
"vaccination" is my provisional conclusion.
```

Saved primary L14 boundary readout: `-1.297134`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-029-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L354) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `169`; response stop (exclusive) `179`; final content `178`; boundary `179` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `58.332008`; mean token NLL: `5.833201`.

</details>

**incorrect, confident**

```text
"blood transfusion" is my definite conclusion.
```

Saved primary L14 boundary readout: `0.127979`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-029-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L359) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `169`; response stop (exclusive) `179`; final content `178`; boundary `179` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `67.809898`; mean token NLL: `6.780990`.

</details>

**incorrect, hedged**

```text
"blood transfusion" is my provisional conclusion.
```

Saved primary L14 boundary readout: `-1.210244`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-029-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L360) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `169`; response stop (exclusive) `179`; final content `178`; boundary `179` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `65.659081`; mean token NLL: `6.565908`.

</details>

[Back to question list](#factual-qa) · [Dataset overview](README.md)

## factual_qa-030

[Raw source](../../data/paired_confidence/source_items.jsonl#L31)

Question:

```text
According to the passage, which gender is more populous across all groups in Jacksonville?
```

Context:

```text
As of 2010[update], there were 366,273 households out of which 11.8% were vacant. 23.9% of households had children under the age of 18 living with them, 43.8% were married couples, 15.2% had a female householder with no husband present, and 36.4% were non-families. 29.7% of all households were made up of individuals and 7.9% had someone living alone who was 65 years of age or older. The average household size was 2.55 and the average family size was 3.21. In the city, the population was spread out with 23.9% under the age of 18, 10.5% from 18 to 24, 28.5% from 25 to 44, 26.2% from 45 to 64, and 10.9% who were 65 years of age or older. The median age was 35.5 years. For every 100 females there were 94.1 males. For every 100 females age 18 and over, there were 91.3 males.
```

Correct key:

```text
females
```

Authored incorrect key:

```text
males
```

Original source: `squad_v2`, original ID `572827fc3acd2414000df5bd`. Original benchmark split: SQuAD validation (cached Stage0 source). Correctness scope: supplied passage.

Phase A included: `false`; Phase A split: `not included`; Phase B split: `train`.

Saved key explanation:

```text
The ratios report fewer males than females.
```

### Rewrite family A

**correct, confident**

```text
I have no doubt: the answer is "females".
```

Saved primary L14 boundary readout: `2.839270`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-030-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L361) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `325`; response stop (exclusive) `337`; final content `336`; boundary `337` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `38.620548`; mean token NLL: `3.218379`.

</details>

**correct, hedged**

```text
I have some doubt: the answer is "females".
```

Saved primary L14 boundary readout: `-2.465900`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-030-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L362) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `325`; response stop (exclusive) `337`; final content `336`; boundary `337` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `53.865768`; mean token NLL: `4.488814`.

</details>

**incorrect, confident**

```text
I have no doubt: the answer is "males".
```

Saved primary L14 boundary readout: `2.925116`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-030-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L367) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `325`; response stop (exclusive) `337`; final content `336`; boundary `337` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `38.472580`; mean token NLL: `3.206048`.

</details>

**incorrect, hedged**

```text
I have some doubt: the answer is "males".
```

Saved primary L14 boundary readout: `-2.355917`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-030-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L368) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `325`; response stop (exclusive) `337`; final content `336`; boundary `337` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `53.228226`; mean token NLL: `4.435686`.

</details>

### Rewrite family B

**correct, confident**

```text
"females" is the answer I commit to.
```

Saved primary L14 boundary readout: `1.328655`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-030-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L363) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `325`; response stop (exclusive) `335`; final content `334`; boundary `335` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `58.806171`; mean token NLL: `5.880617`.

</details>

**correct, hedged**

```text
"females" is the answer I lean toward.
```

Saved primary L14 boundary readout: `-0.360925`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-030-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L364) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `325`; response stop (exclusive) `335`; final content `334`; boundary `335` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `55.630356`; mean token NLL: `5.563035`.

</details>

**incorrect, confident**

```text
"males" is the answer I commit to.
```

Saved primary L14 boundary readout: `1.207764`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-030-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L369) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `325`; response stop (exclusive) `336`; final content `335`; boundary `336` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `58.300442`; mean token NLL: `5.300040`.

</details>

**incorrect, hedged**

```text
"males" is the answer I lean toward.
```

Saved primary L14 boundary readout: `-0.177565`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-030-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L370) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `325`; response stop (exclusive) `336`; final content `335`; boundary `336` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `54.513939`; mean token NLL: `4.955812`.

</details>

### Rewrite family C

**correct, confident**

```text
My conviction is that the answer is "females".
```

Saved primary L14 boundary readout: `0.995328`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-030-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L365) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `325`; response stop (exclusive) `336`; final content `335`; boundary `336` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `35.270992`; mean token NLL: `3.206454`.

</details>

**correct, hedged**

```text
My guess is that the answer is "females".
```

Saved primary L14 boundary readout: `0.263528`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-030-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L366) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `325`; response stop (exclusive) `336`; final content `335`; boundary `336` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `30.686523`; mean token NLL: `2.789684`.

</details>

**incorrect, confident**

```text
My conviction is that the answer is "males".
```

Saved primary L14 boundary readout: `0.963943`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-030-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L371) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `325`; response stop (exclusive) `336`; final content `335`; boundary `336` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `34.824097`; mean token NLL: `3.165827`.

</details>

**incorrect, hedged**

```text
My guess is that the answer is "males".
```

Saved primary L14 boundary readout: `0.267436`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-030-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L372) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `325`; response stop (exclusive) `336`; final content `335`; boundary `336` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `30.444002`; mean token NLL: `2.767637`.

</details>

[Back to question list](#factual-qa) · [Dataset overview](README.md)

## factual_qa-031

[Raw source](../../data/paired_confidence/source_items.jsonl#L32)

Question:

```text
According to the passage, in the capabilities approach, economic growth and income are considered means rather than what?
```

Context:

```text
The capabilities approach – sometimes called the human development approach – looks at income inequality and poverty as form of “capability deprivation”. Unlike neoliberalism, which “defines well-being as utility maximization”, economic growth and income are considered a means to an end rather than the end itself. Its goal is to “wid[en] people’s choices and the level of their achieved well-being” through increasing functionings (the things a person values doing), capabilities (the freedom to enjoy functionings) and agency (the ability to pursue valued goals).
```

Correct key:

```text
the end itself
```

Authored incorrect key:

```text
the starting point
```

Original source: `squad_v2`, original ID `572a213e6aef0514001552ef`. Original benchmark split: SQuAD validation (cached Stage0 source). Correctness scope: supplied passage.

Phase A included: `false`; Phase A split: `not included`; Phase B split: `validation`.

Saved key explanation:

```text
Growth and income are means rather than the end itself.
```

### Rewrite family A

**correct, confident**

```text
With confidence, my answer is "the end itself".
```

Saved primary L14 boundary readout: `2.427841`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-031-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L373) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `151`; response stop (exclusive) `162`; final content `161`; boundary `162` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `39.544937`; mean token NLL: `3.594994`.

</details>

**correct, hedged**

```text
With some uncertainty, my answer is "the end itself".
```

Saved primary L14 boundary readout: `1.817846`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-031-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L374) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `151`; response stop (exclusive) `163`; final content `162`; boundary `163` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `43.349258`; mean token NLL: `3.612438`.

</details>

**incorrect, confident**

```text
With confidence, my answer is "the starting point".
```

Saved primary L14 boundary readout: `1.982995`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-031-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L379) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `151`; response stop (exclusive) `162`; final content `161`; boundary `162` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `55.108742`; mean token NLL: `5.009886`.

</details>

**incorrect, hedged**

```text
With some uncertainty, my answer is "the starting point".
```

Saved primary L14 boundary readout: `1.309278`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-031-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L380) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `151`; response stop (exclusive) `163`; final content `162`; boundary `163` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `56.321297`; mean token NLL: `4.693441`.

</details>

### Rewrite family B

**correct, confident**

```text
My answer is "the end itself"; I would give it without hesitation.
```

Saved primary L14 boundary readout: `2.786985`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-031-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L375) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `151`; response stop (exclusive) `166`; final content `165`; boundary `166` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `61.011940`; mean token NLL: `4.067462`.

</details>

**correct, hedged**

```text
My answer is "the end itself"; I would give it with hesitation.
```

Saved primary L14 boundary readout: `0.014924`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-031-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L376) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `151`; response stop (exclusive) `166`; final content `165`; boundary `166` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `76.170128`; mean token NLL: `5.078009`.

</details>

**incorrect, confident**

```text
My answer is "the starting point"; I would give it without hesitation.
```

Saved primary L14 boundary readout: `2.495005`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-031-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L381) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `151`; response stop (exclusive) `166`; final content `165`; boundary `166` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `76.719978`; mean token NLL: `5.114665`.

</details>

**incorrect, hedged**

```text
My answer is "the starting point"; I would give it with hesitation.
```

Saved primary L14 boundary readout: `-0.572503`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-031-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L382) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `151`; response stop (exclusive) `166`; final content `165`; boundary `166` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `92.776077`; mean token NLL: `6.185072`.

</details>

### Rewrite family C

**correct, confident**

```text
I regard "the end itself" as established.
```

Saved primary L14 boundary readout: `-0.182254`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-031-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L377) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `151`; response stop (exclusive) `161`; final content `160`; boundary `161` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `48.017487`; mean token NLL: `4.801749`.

</details>

**correct, hedged**

```text
I regard "the end itself" as provisional.
```

Saved primary L14 boundary readout: `-0.897136`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-031-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L378) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `151`; response stop (exclusive) `161`; final content `160`; boundary `161` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `49.631702`; mean token NLL: `4.963170`.

</details>

**incorrect, confident**

```text
I regard "the starting point" as established.
```

Saved primary L14 boundary readout: `-0.294595`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-031-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L383) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `151`; response stop (exclusive) `161`; final content `160`; boundary `161` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `61.653027`; mean token NLL: `6.165303`.

</details>

**incorrect, hedged**

```text
I regard "the starting point" as provisional.
```

Saved primary L14 boundary readout: `-1.130740`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-031-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L384) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `151`; response stop (exclusive) `161`; final content `160`; boundary `161` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `62.622993`; mean token NLL: `6.262300`.

</details>

[Back to question list](#factual-qa) · [Dataset overview](README.md)

## factual_qa-032

[Raw source](../../data/paired_confidence/source_items.jsonl#L33)

Question:

```text
According to the passage, european imperialism was focused on what?
```

Context:

```text
Europe's expansion into territorial imperialism was largely focused on economic growth by collecting resources from colonies, in combination with assuming political control by military and political means. The colonization of India in the mid-18th century offers an example of this focus: there, the "British exploited the political weakness of the Mughal state, and, while military activity was important at various times, the economic and administrative incorporation of local elites was also of crucial significance" for the establishment of control over the subcontinent's resources, markets, and manpower. Although a substantial number of colonies had been designed to provide economic profit and to ship resources to home ports in the seventeenth and eighteenth centuries, Fieldhouse suggests that in the nineteenth and twentieth centuries in places such as Africa and Asia, this idea is not necessarily valid:
```

Correct key:

```text
economic growth
```

Authored incorrect key:

```text
resource depletion
```

Original source: `squad_v2`, original ID `573098f38ab72b1400f9c5d2`. Original benchmark split: SQuAD validation (cached Stage0 source). Correctness scope: supplied passage.

Phase A included: `false`; Phase A split: `not included`; Phase B split: `test`.

Saved key explanation:

```text
The named focus is economic growth.
```

### Rewrite family A

**correct, confident**

```text
I am confident the answer is "economic growth".
```

Saved primary L14 boundary readout: `2.750198`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-032-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L385) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `196`; response stop (exclusive) `206`; final content `205`; boundary `206` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `37.554855`; mean token NLL: `3.755486`.

</details>

**correct, hedged**

```text
I am uncertain, but my answer is "economic growth".
```

Saved primary L14 boundary readout: `-0.456781`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-032-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L386) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `196`; response stop (exclusive) `208`; final content `207`; boundary `208` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `51.500656`; mean token NLL: `4.291721`.

</details>

**incorrect, confident**

```text
I am confident the answer is "resource depletion".
```

Saved primary L14 boundary readout: `2.285649`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-032-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L391) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `196`; response stop (exclusive) `206`; final content `205`; boundary `206` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `53.940804`; mean token NLL: `5.394080`.

</details>

**incorrect, hedged**

```text
I am uncertain, but my answer is "resource depletion".
```

Saved primary L14 boundary readout: `-1.034320`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-032-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L392) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `196`; response stop (exclusive) `208`; final content `207`; boundary `208` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `66.563210`; mean token NLL: `5.546934`.

</details>

### Rewrite family B

**correct, confident**

```text
I settle on "economic growth" as my answer.
```

Saved primary L14 boundary readout: `2.483439`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-032-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L387) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `196`; response stop (exclusive) `207`; final content `206`; boundary `207` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `46.876438`; mean token NLL: `4.261494`.

</details>

**correct, hedged**

```text
I lean toward "economic growth" as my answer.
```

Saved primary L14 boundary readout: `-0.135797`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-032-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L388) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `196`; response stop (exclusive) `207`; final content `206`; boundary `207` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `35.774239`; mean token NLL: `3.252203`.

</details>

**incorrect, confident**

```text
I settle on "resource depletion" as my answer.
```

Saved primary L14 boundary readout: `2.189607`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-032-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L393) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `196`; response stop (exclusive) `207`; final content `206`; boundary `207` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `59.530090`; mean token NLL: `5.411827`.

</details>

**incorrect, hedged**

```text
I lean toward "resource depletion" as my answer.
```

Saved primary L14 boundary readout: `-0.585559`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-032-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L394) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `196`; response stop (exclusive) `207`; final content `206`; boundary `207` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `49.794868`; mean token NLL: `4.526806`.

</details>

### Rewrite family C

**correct, confident**

```text
I would stake my position on "economic growth".
```

Saved primary L14 boundary readout: `1.389493`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-032-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L389) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `196`; response stop (exclusive) `206`; final content `205`; boundary `206` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `40.009697`; mean token NLL: `4.000970`.

</details>

**correct, hedged**

```text
I would cautiously suggest "economic growth".
```

Saved primary L14 boundary readout: `1.122641`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-032-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L390) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `196`; response stop (exclusive) `204`; final content `203`; boundary `204` (`151645`, `<|im_end|>`). Response tokens: `8`.

Sequence NLL: `36.784698`; mean token NLL: `4.598087`.

</details>

**incorrect, confident**

```text
I would stake my position on "resource depletion".
```

Saved primary L14 boundary readout: `0.853989`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-032-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L395) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `196`; response stop (exclusive) `206`; final content `205`; boundary `206` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `54.319683`; mean token NLL: `5.431968`.

</details>

**incorrect, hedged**

```text
I would cautiously suggest "resource depletion".
```

Saved primary L14 boundary readout: `0.608381`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-032-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L396) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `196`; response stop (exclusive) `204`; final content `203`; boundary `204` (`151645`, `<|im_end|>`). Response tokens: `8`.

Sequence NLL: `51.628555`; mean token NLL: `6.453569`.

</details>

[Back to question list](#factual-qa) · [Dataset overview](README.md)

## factual_qa-033

[Raw source](../../data/paired_confidence/source_items.jsonl#L34)

Question:

```text
According to the passage, in order to better understand the orientations of faults and folds, structural geologists do what with measurements of geological structures?
```

Context:

```text
Structural geologists use microscopic analysis of oriented thin sections of geologic samples to observe the fabric within the rocks which gives information about strain within the crystalline structure of the rocks. They also plot and combine measurements of geological structures in order to better understand the orientations of faults and folds in order to reconstruct the history of rock deformation in the area. In addition, they perform analog and numerical experiments of rock deformation in large and small settings.
```

Correct key:

```text
plot and combine
```

Authored incorrect key:

```text
erase and ignore
```

Original source: `squad_v2`, original ID `57267d52708984140094c7db`. Original benchmark split: SQuAD validation (cached Stage0 source). Correctness scope: supplied passage.

Phase A included: `false`; Phase A split: `not included`; Phase B split: `validation`.

Saved key explanation:

```text
Measurements are plotted and combined, not erased and ignored.
```

### Rewrite family A

**correct, confident**

```text
I am sure the answer is "plot and combine".
```

Saved primary L14 boundary readout: `2.026573`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-033-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L397) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `137`; response stop (exclusive) `148`; final content `147`; boundary `148` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `33.726128`; mean token NLL: `3.066012`.

</details>

**correct, hedged**

```text
I am not sure, but the answer is "plot and combine".
```

Saved primary L14 boundary readout: `-1.458987`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-033-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L398) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `137`; response stop (exclusive) `151`; final content `150`; boundary `151` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `37.589462`; mean token NLL: `2.684962`.

</details>

**incorrect, confident**

```text
I am sure the answer is "erase and ignore".
```

Saved primary L14 boundary readout: `1.406192`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-033-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L403) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `137`; response stop (exclusive) `148`; final content `147`; boundary `148` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `60.617500`; mean token NLL: `5.510682`.

</details>

**incorrect, hedged**

```text
I am not sure, but the answer is "erase and ignore".
```

Saved primary L14 boundary readout: `-1.546673`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-033-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L404) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `137`; response stop (exclusive) `151`; final content `150`; boundary `151` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `60.907928`; mean token NLL: `4.350566`.

</details>

### Rewrite family B

**correct, confident**

```text
"plot and combine" is my answer, and I stand by it.
```

Saved primary L14 boundary readout: `1.983809`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-033-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L399) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `137`; response stop (exclusive) `152`; final content `151`; boundary `152` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `50.351379`; mean token NLL: `3.356759`.

</details>

**correct, hedged**

```text
"plot and combine" is my tentative answer.
```

Saved primary L14 boundary readout: `-0.633795`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-033-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L400) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `137`; response stop (exclusive) `147`; final content `146`; boundary `147` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `42.882202`; mean token NLL: `4.288220`.

</details>

**incorrect, confident**

```text
"erase and ignore" is my answer, and I stand by it.
```

Saved primary L14 boundary readout: `1.466679`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-033-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L405) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `137`; response stop (exclusive) `152`; final content `151`; boundary `152` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `74.463287`; mean token NLL: `4.964219`.

</details>

**incorrect, hedged**

```text
"erase and ignore" is my tentative answer.
```

Saved primary L14 boundary readout: `-0.223436`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-033-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L406) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `137`; response stop (exclusive) `147`; final content `146`; boundary `147` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `67.000565`; mean token NLL: `6.700057`.

</details>

### Rewrite family C

**correct, confident**

```text
"plot and combine" is my definite conclusion.
```

Saved primary L14 boundary readout: `0.572333`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-033-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L401) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `137`; response stop (exclusive) `147`; final content `146`; boundary `147` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `51.170761`; mean token NLL: `5.117076`.

</details>

**correct, hedged**

```text
"plot and combine" is my provisional conclusion.
```

Saved primary L14 boundary readout: `-1.064136`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-033-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L402) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `137`; response stop (exclusive) `147`; final content `146`; boundary `147` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `51.958893`; mean token NLL: `5.195889`.

</details>

**incorrect, confident**

```text
"erase and ignore" is my definite conclusion.
```

Saved primary L14 boundary readout: `0.451828`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-033-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L407) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `137`; response stop (exclusive) `147`; final content `146`; boundary `147` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `77.235748`; mean token NLL: `7.723575`.

</details>

**incorrect, hedged**

```text
"erase and ignore" is my provisional conclusion.
```

Saved primary L14 boundary readout: `-0.696924`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-033-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L408) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `137`; response stop (exclusive) `147`; final content `146`; boundary `147` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `75.058662`; mean token NLL: `7.505866`.

</details>

[Back to question list](#factual-qa) · [Dataset overview](README.md)

## factual_qa-034

[Raw source](../../data/paired_confidence/source_items.jsonl#L35)

Question:

```text
According to the passage, which crime is defined almost identically across nations and jurisdictions?
```

Context:

```text
Crime rate has also been shown to be correlated with inequality in society. Most studies looking into the relationship have concentrated on homicides – since homicides are almost identically defined across all nations and jurisdictions. There have been over fifty studies showing tendencies for violence to be more common in societies where income differences are larger. Research has been conducted comparing developed countries with undeveloped countries, as well as studying areas within countries. Daly et al. 2001 found that among U.S States and Canadian Provinces there is a tenfold difference in homicide rates related to inequality. They estimated that about half of all variation in homicide rates can be accounted for by differences in the amount of inequality in each province or state. Fajnzylber et al. (2002) found a similar relationship worldwide. Among comments in academic literature on the relationship between homicides and inequality are:
```

Correct key:

```text
homicides
```

Authored incorrect key:

```text
tax evasion
```

Original source: `squad_v2`, original ID `572a0a391d046914007796e0`. Original benchmark split: SQuAD validation (cached Stage0 source). Correctness scope: supplied passage.

Phase A included: `false`; Phase A split: `not included`; Phase B split: `test`.

Saved key explanation:

```text
The passage names homicide definitions.
```

### Rewrite family A

**correct, confident**

```text
I have no doubt: the answer is "homicides".
```

Saved primary L14 boundary readout: `3.190611`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-034-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L409) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `215`; response stop (exclusive) `228`; final content `227`; boundary `228` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `46.953384`; mean token NLL: `3.611799`.

</details>

**correct, hedged**

```text
I have some doubt: the answer is "homicides".
```

Saved primary L14 boundary readout: `-2.188248`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-034-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L410) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `215`; response stop (exclusive) `228`; final content `227`; boundary `228` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `51.575741`; mean token NLL: `3.967365`.

</details>

**incorrect, confident**

```text
I have no doubt: the answer is "tax evasion".
```

Saved primary L14 boundary readout: `2.115416`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-034-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L415) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `215`; response stop (exclusive) `227`; final content `226`; boundary `227` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `62.776527`; mean token NLL: `5.231377`.

</details>

**incorrect, hedged**

```text
I have some doubt: the answer is "tax evasion".
```

Saved primary L14 boundary readout: `-3.208986`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-034-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L416) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `215`; response stop (exclusive) `227`; final content `226`; boundary `227` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `65.030991`; mean token NLL: `5.419249`.

</details>

### Rewrite family B

**correct, confident**

```text
"homicides" is the answer I commit to.
```

Saved primary L14 boundary readout: `1.510772`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-034-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L411) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `215`; response stop (exclusive) `226`; final content `225`; boundary `226` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `59.484970`; mean token NLL: `5.407724`.

</details>

**correct, hedged**

```text
"homicides" is the answer I lean toward.
```

Saved primary L14 boundary readout: `0.069468`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-034-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L412) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `215`; response stop (exclusive) `226`; final content `225`; boundary `226` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `56.029579`; mean token NLL: `5.093598`.

</details>

**incorrect, confident**

```text
"tax evasion" is the answer I commit to.
```

Saved primary L14 boundary readout: `0.580683`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-034-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L417) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `215`; response stop (exclusive) `226`; final content `225`; boundary `226` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `66.441223`; mean token NLL: `6.040111`.

</details>

**incorrect, hedged**

```text
"tax evasion" is the answer I lean toward.
```

Saved primary L14 boundary readout: `-0.795146`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-034-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L418) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `215`; response stop (exclusive) `226`; final content `225`; boundary `226` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `62.427792`; mean token NLL: `5.675254`.

</details>

### Rewrite family C

**correct, confident**

```text
My conviction is that the answer is "homicides".
```

Saved primary L14 boundary readout: `1.327072`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-034-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L413) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `215`; response stop (exclusive) `227`; final content `226`; boundary `227` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `32.194107`; mean token NLL: `2.682842`.

</details>

**correct, hedged**

```text
My guess is that the answer is "homicides".
```

Saved primary L14 boundary readout: `0.865206`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-034-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L414) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `215`; response stop (exclusive) `227`; final content `226`; boundary `227` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `26.654123`; mean token NLL: `2.221177`.

</details>

**incorrect, confident**

```text
My conviction is that the answer is "tax evasion".
```

Saved primary L14 boundary readout: `0.295244`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-034-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L419) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `215`; response stop (exclusive) `226`; final content `225`; boundary `226` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `47.752739`; mean token NLL: `4.341158`.

</details>

**incorrect, hedged**

```text
My guess is that the answer is "tax evasion".
```

Saved primary L14 boundary readout: `-0.156844`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-034-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L420) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `215`; response stop (exclusive) `226`; final content `225`; boundary `226` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `40.248512`; mean token NLL: `3.658956`.

</details>

[Back to question list](#factual-qa) · [Dataset overview](README.md)

## factual_qa-035

[Raw source](../../data/paired_confidence/source_items.jsonl#L36)

Question:

```text
According to the passage, where was Ralph earl of?
```

Context:

```text
Even before the Norman Conquest of England, the Normans had come into contact with Wales. Edward the Confessor had set up the aforementioned Ralph as earl of Hereford and charged him with defending the Marches and warring with the Welsh. In these original ventures, the Normans failed to make any headway into Wales.
```

Correct key:

```text
Hereford
```

Authored incorrect key:

```text
Kent
```

Original source: `squad_v2`, original ID `56de3d594396321400ee26ca`. Original benchmark split: SQuAD validation (cached Stage0 source). Correctness scope: supplied passage.

Phase A included: `false`; Phase A split: `not included`; Phase B split: `test`.

Saved key explanation:

```text
Ralph is explicitly made earl of Hereford.
```

### Rewrite family A

**correct, confident**

```text
With confidence, my answer is "Hereford".
```

Saved primary L14 boundary readout: `2.349691`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-035-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L421) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `102`; response stop (exclusive) `112`; final content `111`; boundary `112` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `41.774994`; mean token NLL: `4.177499`.

</details>

**correct, hedged**

```text
With some uncertainty, my answer is "Hereford".
```

Saved primary L14 boundary readout: `1.790333`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-035-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L422) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `102`; response stop (exclusive) `113`; final content `112`; boundary `113` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `44.618683`; mean token NLL: `4.056244`.

</details>

**incorrect, confident**

```text
With confidence, my answer is "Kent".
```

Saved primary L14 boundary readout: `1.809056`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-035-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L427) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `102`; response stop (exclusive) `111`; final content `110`; boundary `111` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `50.018421`; mean token NLL: `5.557602`.

</details>

**incorrect, hedged**

```text
With some uncertainty, my answer is "Kent".
```

Saved primary L14 boundary readout: `1.232857`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-035-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L428) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `102`; response stop (exclusive) `112`; final content `111`; boundary `112` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `52.654564`; mean token NLL: `5.265456`.

</details>

### Rewrite family B

**correct, confident**

```text
My answer is "Hereford"; I would give it without hesitation.
```

Saved primary L14 boundary readout: `2.634294`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-035-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L423) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `102`; response stop (exclusive) `116`; final content `115`; boundary `116` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `61.941833`; mean token NLL: `4.424417`.

</details>

**correct, hedged**

```text
My answer is "Hereford"; I would give it with hesitation.
```

Saved primary L14 boundary readout: `-0.336299`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-035-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L424) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `102`; response stop (exclusive) `116`; final content `115`; boundary `116` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `72.233963`; mean token NLL: `5.159569`.

</details>

**incorrect, confident**

```text
My answer is "Kent"; I would give it without hesitation.
```

Saved primary L14 boundary readout: `2.588893`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-035-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L429) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `102`; response stop (exclusive) `115`; final content `114`; boundary `115` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `69.677544`; mean token NLL: `5.359811`.

</details>

**incorrect, hedged**

```text
My answer is "Kent"; I would give it with hesitation.
```

Saved primary L14 boundary readout: `-0.314281`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-035-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L430) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `102`; response stop (exclusive) `115`; final content `114`; boundary `115` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `81.366257`; mean token NLL: `6.258943`.

</details>

### Rewrite family C

**correct, confident**

```text
I regard "Hereford" as established.
```

Saved primary L14 boundary readout: `-1.468373`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-035-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L425) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `102`; response stop (exclusive) `111`; final content `110`; boundary `111` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `43.460426`; mean token NLL: `4.828936`.

</details>

**correct, hedged**

```text
I regard "Hereford" as provisional.
```

Saved primary L14 boundary readout: `-1.658356`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-035-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L426) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `102`; response stop (exclusive) `111`; final content `110`; boundary `111` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `45.727070`; mean token NLL: `5.080786`.

</details>

**incorrect, confident**

```text
I regard "Kent" as established.
```

Saved primary L14 boundary readout: `-1.023817`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-035-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L431) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `102`; response stop (exclusive) `110`; final content `109`; boundary `110` (`151645`, `<|im_end|>`). Response tokens: `8`.

Sequence NLL: `53.967167`; mean token NLL: `6.745896`.

</details>

**incorrect, hedged**

```text
I regard "Kent" as provisional.
```

Saved primary L14 boundary readout: `-1.382204`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-035-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L432) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `102`; response stop (exclusive) `110`; final content `109`; boundary `110` (`151645`, `<|im_end|>`). Response tokens: `8`.

Sequence NLL: `54.741135`; mean token NLL: `6.842642`.

</details>

[Back to question list](#factual-qa) · [Dataset overview](README.md)

## factual_qa-036

[Raw source](../../data/paired_confidence/source_items.jsonl#L37)

Question:

```text
According to the passage, how many households had children under age 18 living in them?
```

Context:

```text
There were 158,349 households, of which 68,511 (43.3%) had children under the age of 18 living in them, 69,284 (43.8%) were opposite-sex married couples living together, 30,547 (19.3%) had a female householder with no husband present, 11,698 (7.4%) had a male householder with no wife present. There were 12,843 (8.1%) unmarried opposite-sex partnerships, and 1,388 (0.9%) same-sex married couples or partnerships. 35,064 households (22.1%) were made up of individuals and 12,344 (7.8%) had someone living alone who was 65 years of age or older. The average household size was 3.07. There were 111,529 families (70.4% of all households); the average family size was 3.62.
```

Correct key:

```text
68,511
```

Authored incorrect key:

```text
69,284
```

Original source: `squad_v2`, original ID `5725f8f5ec44d21400f3d7b1`. Original benchmark split: SQuAD validation (cached Stage0 source). Correctness scope: supplied passage.

Phase A included: `false`; Phase A split: `not included`; Phase B split: `train`.

Saved key explanation:

```text
68,511 is households with children;69,284 is married couples.
```

### Rewrite family A

**correct, confident**

```text
I am confident the answer is "68,511".
```

Saved primary L14 boundary readout: `2.351189`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-036-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L433) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `276`; response stop (exclusive) `290`; final content `289`; boundary `290` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `41.112770`; mean token NLL: `2.936626`.

</details>

**correct, hedged**

```text
I am uncertain, but my answer is "68,511".
```

Saved primary L14 boundary readout: `0.338847`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-036-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L434) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `276`; response stop (exclusive) `292`; final content `291`; boundary `292` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `52.763817`; mean token NLL: `3.297739`.

</details>

**incorrect, confident**

```text
I am confident the answer is "69,284".
```

Saved primary L14 boundary readout: `2.464074`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-036-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L439) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `276`; response stop (exclusive) `290`; final content `289`; boundary `290` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `48.175373`; mean token NLL: `3.441098`.

</details>

**incorrect, hedged**

```text
I am uncertain, but my answer is "69,284".
```

Saved primary L14 boundary readout: `0.499623`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-036-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L440) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `276`; response stop (exclusive) `292`; final content `291`; boundary `292` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `58.354767`; mean token NLL: `3.647173`.

</details>

### Rewrite family B

**correct, confident**

```text
I settle on "68,511" as my answer.
```

Saved primary L14 boundary readout: `2.688081`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-036-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L435) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `276`; response stop (exclusive) `291`; final content `290`; boundary `291` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `39.832382`; mean token NLL: `2.655492`.

</details>

**correct, hedged**

```text
I lean toward "68,511" as my answer.
```

Saved primary L14 boundary readout: `-0.482535`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-036-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L436) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `276`; response stop (exclusive) `291`; final content `290`; boundary `291` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `36.519775`; mean token NLL: `2.434652`.

</details>

**incorrect, confident**

```text
I settle on "69,284" as my answer.
```

Saved primary L14 boundary readout: `2.803501`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-036-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L441) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `276`; response stop (exclusive) `291`; final content `290`; boundary `291` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `46.442039`; mean token NLL: `3.096136`.

</details>

**incorrect, hedged**

```text
I lean toward "69,284" as my answer.
```

Saved primary L14 boundary readout: `-0.510579`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-036-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L442) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `276`; response stop (exclusive) `291`; final content `290`; boundary `291` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `42.144012`; mean token NLL: `2.809601`.

</details>

### Rewrite family C

**correct, confident**

```text
I would stake my position on "68,511".
```

Saved primary L14 boundary readout: `1.363867`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-036-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L437) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `276`; response stop (exclusive) `290`; final content `289`; boundary `290` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `44.580658`; mean token NLL: `3.184333`.

</details>

**correct, hedged**

```text
I would cautiously suggest "68,511".
```

Saved primary L14 boundary readout: `0.567760`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-036-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L438) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `276`; response stop (exclusive) `288`; final content `287`; boundary `288` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `42.642647`; mean token NLL: `3.553554`.

</details>

**incorrect, confident**

```text
I would stake my position on "69,284".
```

Saved primary L14 boundary readout: `1.486232`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-036-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L443) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `276`; response stop (exclusive) `290`; final content `289`; boundary `290` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `50.582001`; mean token NLL: `3.613000`.

</details>

**incorrect, hedged**

```text
I would cautiously suggest "69,284".
```

Saved primary L14 boundary readout: `0.790974`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-036-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L444) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `276`; response stop (exclusive) `288`; final content `287`; boundary `288` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `49.378563`; mean token NLL: `4.114880`.

</details>

[Back to question list](#factual-qa) · [Dataset overview](README.md)

## factual_qa-037

[Raw source](../../data/paired_confidence/source_items.jsonl#L38)

Question:

```text
According to the passage, what type of treaty was the Lisbon Treaty?
```

Context:

```text
Following the Nice Treaty, there was an attempt to reform the constitutional law of the European Union and make it more transparent; this would have also produced a single constitutional document. However, as a result of the referendum in France and the referendum in the Netherlands, the 2004 Treaty establishing a Constitution for Europe never came into force. Instead, the Lisbon Treaty was enacted. Its substance was very similar to the proposed constitutional treaty, but it was formally an amending treaty, and – though it significantly altered the existing treaties – it did not completely replace them.
```

Correct key:

```text
an amending treaty
```

Authored incorrect key:

```text
a complete replacement treaty
```

Original source: `squad_v2`, original ID `57264865dd62a815002e8065`. Original benchmark split: SQuAD validation (cached Stage0 source). Correctness scope: supplied passage.

Phase A included: `false`; Phase A split: `not included`; Phase B split: `validation`.

Saved key explanation:

```text
Lisbon is amending and explicitly does not replace prior treaties.
```

### Rewrite family A

**correct, confident**

```text
I am sure the answer is "an amending treaty".
```

Saved primary L14 boundary readout: `2.814468`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-037-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L445) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `150`; response stop (exclusive) `162`; final content `161`; boundary `162` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `43.097851`; mean token NLL: `3.591488`.

</details>

**correct, hedged**

```text
I am not sure, but the answer is "an amending treaty".
```

Saved primary L14 boundary readout: `-0.380114`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-037-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L446) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `150`; response stop (exclusive) `165`; final content `164`; boundary `165` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `41.270638`; mean token NLL: `2.751376`.

</details>

**incorrect, confident**

```text
I am sure the answer is "a complete replacement treaty".
```

Saved primary L14 boundary readout: `2.609479`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-037-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L451) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `150`; response stop (exclusive) `162`; final content `161`; boundary `162` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `55.334011`; mean token NLL: `4.611167`.

</details>

**incorrect, hedged**

```text
I am not sure, but the answer is "a complete replacement treaty".
```

Saved primary L14 boundary readout: `-0.511944`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-037-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L452) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `150`; response stop (exclusive) `165`; final content `164`; boundary `165` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `51.844696`; mean token NLL: `3.456313`.

</details>

### Rewrite family B

**correct, confident**

```text
"an amending treaty" is my answer, and I stand by it.
```

Saved primary L14 boundary readout: `2.164701`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-037-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L447) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `150`; response stop (exclusive) `166`; final content `165`; boundary `166` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `61.772270`; mean token NLL: `3.860767`.

</details>

**correct, hedged**

```text
"an amending treaty" is my tentative answer.
```

Saved primary L14 boundary readout: `0.271240`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-037-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L448) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `150`; response stop (exclusive) `161`; final content `160`; boundary `161` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `56.009911`; mean token NLL: `5.091810`.

</details>

**incorrect, confident**

```text
"a complete replacement treaty" is my answer, and I stand by it.
```

Saved primary L14 boundary readout: `1.327347`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-037-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L453) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `150`; response stop (exclusive) `165`; final content `164`; boundary `165` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `66.836212`; mean token NLL: `4.455748`.

</details>

**incorrect, hedged**

```text
"a complete replacement treaty" is my tentative answer.
```

Saved primary L14 boundary readout: `-0.110307`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-037-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L454) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `150`; response stop (exclusive) `160`; final content `159`; boundary `160` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `56.976925`; mean token NLL: `5.697692`.

</details>

### Rewrite family C

**correct, confident**

```text
"an amending treaty" is my definite conclusion.
```

Saved primary L14 boundary readout: `1.455840`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-037-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L449) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `150`; response stop (exclusive) `161`; final content `160`; boundary `161` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `65.716476`; mean token NLL: `5.974225`.

</details>

**correct, hedged**

```text
"an amending treaty" is my provisional conclusion.
```

Saved primary L14 boundary readout: `0.413903`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-037-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L450) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `150`; response stop (exclusive) `161`; final content `160`; boundary `161` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `62.480526`; mean token NLL: `5.680048`.

</details>

**incorrect, confident**

```text
"a complete replacement treaty" is my definite conclusion.
```

Saved primary L14 boundary readout: `0.917085`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-037-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L455) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `150`; response stop (exclusive) `160`; final content `159`; boundary `160` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `64.449692`; mean token NLL: `6.444969`.

</details>

**incorrect, hedged**

```text
"a complete replacement treaty" is my provisional conclusion.
```

Saved primary L14 boundary readout: `0.160715`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-037-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L456) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `150`; response stop (exclusive) `160`; final content `159`; boundary `160` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `63.002007`; mean token NLL: `6.300200`.

</details>

[Back to question list](#factual-qa) · [Dataset overview](README.md)

## factual_qa-038

[Raw source](../../data/paired_confidence/source_items.jsonl#L39)

Question:

```text
According to the passage, where do a majority of consultant pharmacists tend to work?
```

Context:

```text
Consultant pharmacy practice focuses more on medication regimen review (i.e. "cognitive services") than on actual dispensing of drugs. Consultant pharmacists most typically work in nursing homes, but are increasingly branching into other institutions and non-institutional settings. Traditionally consultant pharmacists were usually independent business owners, though in the United States many now work for several large pharmacy management companies (primarily Omnicare, Kindred Healthcare and PharMerica). This trend may be gradually reversing as consultant pharmacists begin to work directly with patients, primarily because many elderly people are now taking numerous medications but continue to live outside of institutional settings. Some community pharmacies employ consultant pharmacists and/or provide consulting services.
```

Correct key:

```text
nursing homes
```

Authored incorrect key:

```text
primary schools
```

Original source: `squad_v2`, original ID `5726ea985951b619008f8262`. Original benchmark split: SQuAD validation (cached Stage0 source). Correctness scope: supplied passage.

Phase A included: `false`; Phase A split: `not included`; Phase B split: `train`.

Saved key explanation:

```text
The named typical setting is nursing homes.
```

### Rewrite family A

**correct, confident**

```text
I have no doubt: the answer is "nursing homes".
```

Saved primary L14 boundary readout: `3.283465`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-038-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L457) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `179`; response stop (exclusive) `193`; final content `192`; boundary `193` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `41.322472`; mean token NLL: `2.951605`.

</details>

**correct, hedged**

```text
I have some doubt: the answer is "nursing homes".
```

Saved primary L14 boundary readout: `-2.441427`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-038-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L458) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `179`; response stop (exclusive) `193`; final content `192`; boundary `193` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `51.181259`; mean token NLL: `3.655804`.

</details>

**incorrect, confident**

```text
I have no doubt: the answer is "primary schools".
```

Saved primary L14 boundary readout: `2.544504`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-038-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L463) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `179`; response stop (exclusive) `191`; final content `190`; boundary `191` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `60.638664`; mean token NLL: `5.053222`.

</details>

**incorrect, hedged**

```text
I have some doubt: the answer is "primary schools".
```

Saved primary L14 boundary readout: `-3.043708`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-038-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L464) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `179`; response stop (exclusive) `191`; final content `190`; boundary `191` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `65.564224`; mean token NLL: `5.463686`.

</details>

### Rewrite family B

**correct, confident**

```text
"nursing homes" is the answer I commit to.
```

Saved primary L14 boundary readout: `1.388401`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-038-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L459) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `179`; response stop (exclusive) `192`; final content `191`; boundary `192` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `57.913269`; mean token NLL: `4.454867`.

</details>

**correct, hedged**

```text
"nursing homes" is the answer I lean toward.
```

Saved primary L14 boundary readout: `-0.104337`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-038-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L460) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `179`; response stop (exclusive) `192`; final content `191`; boundary `192` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `53.900574`; mean token NLL: `4.146198`.

</details>

**incorrect, confident**

```text
"primary schools" is the answer I commit to.
```

Saved primary L14 boundary readout: `0.925665`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-038-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L465) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `179`; response stop (exclusive) `190`; final content `189`; boundary `190` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `69.627022`; mean token NLL: `6.329729`.

</details>

**incorrect, hedged**

```text
"primary schools" is the answer I lean toward.
```

Saved primary L14 boundary readout: `-0.540256`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-038-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L466) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `179`; response stop (exclusive) `190`; final content `189`; boundary `190` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `65.447952`; mean token NLL: `5.949814`.

</details>

### Rewrite family C

**correct, confident**

```text
My conviction is that the answer is "nursing homes".
```

Saved primary L14 boundary readout: `1.303294`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-038-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L461) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `179`; response stop (exclusive) `192`; final content `191`; boundary `192` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `30.745516`; mean token NLL: `2.365040`.

</details>

**correct, hedged**

```text
My guess is that the answer is "nursing homes".
```

Saved primary L14 boundary readout: `0.993207`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-038-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L462) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `179`; response stop (exclusive) `192`; final content `191`; boundary `192` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `28.139008`; mean token NLL: `2.164539`.

</details>

**incorrect, confident**

```text
My conviction is that the answer is "primary schools".
```

Saved primary L14 boundary readout: `0.678678`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-038-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L467) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `179`; response stop (exclusive) `190`; final content `189`; boundary `190` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `48.639973`; mean token NLL: `4.421816`.

</details>

**incorrect, hedged**

```text
My guess is that the answer is "primary schools".
```

Saved primary L14 boundary readout: `0.237208`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-038-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L468) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `179`; response stop (exclusive) `190`; final content `189`; boundary `190` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `45.612820`; mean token NLL: `4.146620`.

</details>

[Back to question list](#factual-qa) · [Dataset overview](README.md)

## factual_qa-039

[Raw source](../../data/paired_confidence/source_items.jsonl#L40)

Question:

```text
According to the passage, who threw gold into the Rhine, according to legend?
```

Context:

```text
Germanic tribes crossed the Rhine in the Migration period, by the 5th century establishing the kingdoms of Francia on the Lower Rhine, Burgundy on the Upper Rhine and Alemannia on the High Rhine. This "Germanic Heroic Age" is reflected in medieval legend, such as the Nibelungenlied which tells of the hero Siegfried killing a dragon on the Drachenfels (Siebengebirge) ("dragons rock"), near Bonn at the Rhine and of the Burgundians and their court at Worms, at the Rhine and Kriemhild's golden treasure, which was thrown into the Rhine by Hagen.
```

Correct key:

```text
Hagen
```

Authored incorrect key:

```text
Siegfried
```

Original source: `squad_v2`, original ID `57300911947a6a140053cfba`. Original benchmark split: SQuAD validation (cached Stage0 source). Correctness scope: supplied passage.

Phase A included: `false`; Phase A split: `not included`; Phase B split: `test`.

Saved key explanation:

```text
Hagen throws the gold; Siegfried kills the dragon.
```

### Rewrite family A

**correct, confident**

```text
With confidence, my answer is "Hagen".
```

Saved primary L14 boundary readout: `2.829791`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-039-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L469) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `184`; response stop (exclusive) `194`; final content `193`; boundary `194` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `37.939545`; mean token NLL: `3.793954`.

</details>

**correct, hedged**

```text
With some uncertainty, my answer is "Hagen".
```

Saved primary L14 boundary readout: `1.940718`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-039-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L470) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `184`; response stop (exclusive) `195`; final content `194`; boundary `195` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `44.390247`; mean token NLL: `4.035477`.

</details>

**incorrect, confident**

```text
With confidence, my answer is "Siegfried".
```

Saved primary L14 boundary readout: `2.976208`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-039-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L475) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `184`; response stop (exclusive) `195`; final content `194`; boundary `195` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `48.601433`; mean token NLL: `4.418312`.

</details>

**incorrect, hedged**

```text
With some uncertainty, my answer is "Siegfried".
```

Saved primary L14 boundary readout: `1.973873`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-039-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L476) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `184`; response stop (exclusive) `196`; final content `195`; boundary `196` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `53.583221`; mean token NLL: `4.465269`.

</details>

### Rewrite family B

**correct, confident**

```text
My answer is "Hagen"; I would give it without hesitation.
```

Saved primary L14 boundary readout: `2.710331`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-039-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L471) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `184`; response stop (exclusive) `198`; final content `197`; boundary `198` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `58.063446`; mean token NLL: `4.147389`.

</details>

**correct, hedged**

```text
My answer is "Hagen"; I would give it with hesitation.
```

Saved primary L14 boundary readout: `-0.082055`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-039-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L472) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `184`; response stop (exclusive) `198`; final content `197`; boundary `198` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `70.475098`; mean token NLL: `5.033936`.

</details>

**incorrect, confident**

```text
My answer is "Siegfried"; I would give it without hesitation.
```

Saved primary L14 boundary readout: `2.637957`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-039-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L477) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `184`; response stop (exclusive) `199`; final content `198`; boundary `199` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `64.780304`; mean token NLL: `4.318687`.

</details>

**incorrect, hedged**

```text
My answer is "Siegfried"; I would give it with hesitation.
```

Saved primary L14 boundary readout: `-0.234560`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-039-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L478) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `184`; response stop (exclusive) `199`; final content `198`; boundary `199` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `76.339294`; mean token NLL: `5.089286`.

</details>

### Rewrite family C

**correct, confident**

```text
I regard "Hagen" as established.
```

Saved primary L14 boundary readout: `-1.113465`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-039-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L473) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `184`; response stop (exclusive) `193`; final content `192`; boundary `193` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `45.229439`; mean token NLL: `5.025493`.

</details>

**correct, hedged**

```text
I regard "Hagen" as provisional.
```

Saved primary L14 boundary readout: `-1.490500`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-039-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L474) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `184`; response stop (exclusive) `193`; final content `192`; boundary `193` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `46.964302`; mean token NLL: `5.218256`.

</details>

**incorrect, confident**

```text
I regard "Siegfried" as established.
```

Saved primary L14 boundary readout: `-1.197915`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-039-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L479) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `184`; response stop (exclusive) `194`; final content `193`; boundary `194` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `48.389931`; mean token NLL: `4.838993`.

</details>

**incorrect, hedged**

```text
I regard "Siegfried" as provisional.
```

Saved primary L14 boundary readout: `-1.717677`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `factual_qa-039-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L480) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `184`; response stop (exclusive) `194`; final content `193`; boundary `194` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `49.906189`; mean token NLL: `4.990619`.

</details>

[Back to question list](#factual-qa) · [Dataset overview](README.md)
