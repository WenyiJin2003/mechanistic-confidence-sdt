# Academic

[Repository](../../README.md) · [All question sets](../README.md)

[Dataset overview](README.md) · [Download all response rows (CSV)](responses.csv)

All 40 questions in this group. Responses are authored experiment stimuli. All stored variants and their primary scores are included.

- [academic-000](#academic-000): What is the second most common element in the solar system?
- [academic-001](#academic-001): What is the energy released by electrons moving through the electron transport chain used to do?
- [academic-002](#academic-002): What is the chemical symbol for antimony?
- [academic-003](#academic-003): What is continued population growth after replacement fertility has been achieved called?
- [academic-004](#academic-004): Let x = 1. What is x << 3 in Python 3?
- [academic-005](#academic-005): In test construction and evaluation, what does validity refer to?
- [academic-006](#academic-006): What is the name of the ten-day New Year festival that celebrated Babylon's culture?
- [academic-007](#academic-007): Where is the sinoatrial node located?
- [academic-008](#academic-008): On which planet in our solar system can you find the Great Red Spot?
- [academic-009](#academic-009): Of Callisto, Europa, Ganymede, and Io, which moon is closest to Jupiter?
- [academic-010](#academic-010): What does the astronomical term ecliptic describe?
- [academic-011](#academic-011): What type of radiation causes a black hole to evaporate over time?
- [academic-012](#academic-012): What is the development of an egg without fertilization called?
- [academic-013](#academic-013): Where does fertilization normally occur in humans?
- [academic-014](#academic-014): Where does the Krebs cycle occur in humans?
- [academic-015](#academic-015): During which phase of the cell cycle does the quantity of DNA in a eukaryotic cell typically double?
- [academic-016](#academic-016): What does Hund's rule require?
- [academic-017](#academic-017): What net ionic equation results when aqueous NH4Br and AgNO3 are mixed?
- [academic-018](#academic-018): What is the molarity of a sodium hydroxide solution that requires 42.6 mL of 0.108 M HCl to neutralize 40.0 mL of the base?
- [academic-019](#academic-019): What fraction of an isotope remains after three half-lives?
- [academic-020](#academic-020): What is the tendency for migration to decrease with distance called?
- [academic-021](#academic-021): What is the outlying area serviced by an urban center called?
- [academic-022](#academic-022): What type of location is expressed by latitude and longitude coordinates?
- [academic-023](#academic-023): What is a government that combines religion and government called?
- [academic-024](#academic-024): What is the output of the statement "a" + "ab" in Python 3?
- [academic-025](#academic-025): What is the value of the Python expression 1 + 3 % 3?
- [academic-026](#academic-026): Let x = 8. What is x >> 1 in Python 3?
- [academic-027](#academic-027): What is the output of "abc"\[-1\] in Python 3?
- [academic-028](#academic-028): Our ability to perceive depth depends primarily on what other perceptual abilities?
- [academic-029](#academic-029): What phenomenon is illustrated when runners increase their pace after another runner comes into view?
- [academic-030](#academic-030): What is an unjustifiable, usually negative attitude toward a group and its members called?
- [academic-031](#academic-031): What taste do substances toxic to humans often have?
- [academic-032](#academic-032): What is the mi'raj?
- [academic-033](#academic-033): What does the term Qur'an literally mean?
- [academic-034](#academic-034): What is the communal meal offered at the place of worship called in Sikhism?
- [academic-035](#academic-035): What does the term anatman mean?
- [academic-036](#academic-036): Which bones does the coronal suture join?
- [academic-037](#academic-037): Between which layers does cerebrospinal fluid circulate around the brain?
- [academic-038](#academic-038): Where are the vital centres located in the brainstem?
- [academic-039](#academic-039): What kind of neuronal processes do all dorsal spinal nerve roots contain?

## academic-000

[Raw source](../../data/paired_confidence/source_items.jsonl#L81)

Question:

```text
What is the second most common element in the solar system?
```

Context:

No supplied passage.

Correct key:

```text
Helium
```

Authored incorrect key:

```text
Hydrogen
```

Original source: `cais/mmlu`, pinned test split, row `243`, subject `astronomy`, revision `c30699e8356da336a370243923dbaf21066bb9fe`.

Original multiple-choice options:

```text
0: Iron
1: Hydrogen
2: Methane
3: Helium
```

Phase A included: `true`; Phase A split: `train`; Phase B split: `train`.

Saved key explanation:

```text
The keyed answer is helium; hydrogen is the most common, not second most common.
```

### Rewrite family A

**correct, confident**

```text
I am confident the answer is "Helium".
```

Saved primary L14 boundary readout: `3.095204`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-000-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L961) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `43`; final content `42`; boundary `43` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `42.622810`; mean token NLL: `4.262281`.

</details>

**correct, hedged**

```text
I am uncertain, but my answer is "Helium".
```

Saved primary L14 boundary readout: `0.447305`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-000-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L962) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `56.716858`; mean token NLL: `4.726405`.

</details>

**incorrect, confident**

```text
I am confident the answer is "Hydrogen".
```

Saved primary L14 boundary readout: `3.041344`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-000-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L967) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `40.326904`; mean token NLL: `3.666082`.

</details>

**incorrect, hedged**

```text
I am uncertain, but my answer is "Hydrogen".
```

Saved primary L14 boundary readout: `0.745148`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-000-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L968) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `56.651756`; mean token NLL: `4.357827`.

</details>

### Rewrite family B

**correct, confident**

```text
I settle on "Helium" as my answer.
```

Saved primary L14 boundary readout: `2.357713`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-000-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L963) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `49.371334`; mean token NLL: `4.488303`.

</details>

**correct, hedged**

```text
I lean toward "Helium" as my answer.
```

Saved primary L14 boundary readout: `-0.911606`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-000-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L964) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `40.766502`; mean token NLL: `3.706046`.

</details>

**incorrect, confident**

```text
I settle on "Hydrogen" as my answer.
```

Saved primary L14 boundary readout: `2.400512`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-000-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L969) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `47.587631`; mean token NLL: `3.965636`.

</details>

**incorrect, hedged**

```text
I lean toward "Hydrogen" as my answer.
```

Saved primary L14 boundary readout: `-0.888375`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-000-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L970) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `39.146381`; mean token NLL: `3.262198`.

</details>

### Rewrite family C

**correct, confident**

```text
I would stake my position on "Helium".
```

Saved primary L14 boundary readout: `1.766653`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-000-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L965) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `43`; final content `42`; boundary `43` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `48.173088`; mean token NLL: `4.817309`.

</details>

**correct, hedged**

```text
I would cautiously suggest "Helium".
```

Saved primary L14 boundary readout: `1.631266`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-000-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L966) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `8`.

Sequence NLL: `43.204102`; mean token NLL: `5.400513`.

</details>

**incorrect, confident**

```text
I would stake my position on "Hydrogen".
```

Saved primary L14 boundary readout: `1.891766`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-000-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L971) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `46.151276`; mean token NLL: `4.195570`.

</details>

**incorrect, hedged**

```text
I would cautiously suggest "Hydrogen".
```

Saved primary L14 boundary readout: `1.519939`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-000-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L972) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `41.344620`; mean token NLL: `4.593847`.

</details>

[Back to question list](#academic) · [Dataset overview](README.md)

## academic-001

[Raw source](../../data/paired_confidence/source_items.jsonl#L82)

Question:

```text
What is the energy released by electrons moving through the electron transport chain used to do?
```

Context:

No supplied passage.

Correct key:

```text
produce ATP
```

Authored incorrect key:

```text
make NADH
```

Original source: `cais/mmlu`, pinned test split, row `2671`, subject `high_school_biology`, revision `c30699e8356da336a370243923dbaf21066bb9fe`.

Original multiple-choice options:

```text
0: break down glucose
1: make glucose
2: produce ATP
3: make NADH
```

Phase A included: `true`; Phase A split: `validation`; Phase B split: `train`.

Saved key explanation:

```text
This energy helps produce ATP; making NADH is the incorrect choice. The original completion stem is converted without adding reasoning.
```

### Rewrite family A

**correct, confident**

```text
I am sure the answer is "produce ATP".
```

Saved primary L14 boundary readout: `2.031291`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-001-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L973) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `48`; final content `47`; boundary `48` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `36.517212`; mean token NLL: `3.651721`.

</details>

**correct, hedged**

```text
I am not sure, but the answer is "produce ATP".
```

Saved primary L14 boundary readout: `-1.309865`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-001-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L974) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `51`; final content `50`; boundary `51` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `37.186951`; mean token NLL: `2.860535`.

</details>

**incorrect, confident**

```text
I am sure the answer is "make NADH".
```

Saved primary L14 boundary readout: `0.679542`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-001-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L979) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `50`; final content `49`; boundary `50` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `54.920242`; mean token NLL: `4.576687`.

</details>

**incorrect, hedged**

```text
I am not sure, but the answer is "make NADH".
```

Saved primary L14 boundary readout: `-1.292298`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-001-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L980) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `53`; final content `52`; boundary `53` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `56.577698`; mean token NLL: `3.771847`.

</details>

### Rewrite family B

**correct, confident**

```text
"produce ATP" is my answer, and I stand by it.
```

Saved primary L14 boundary readout: `0.663240`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-001-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L975) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `52`; final content `51`; boundary `52` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `57.124096`; mean token NLL: `4.080293`.

</details>

**correct, hedged**

```text
"produce ATP" is my tentative answer.
```

Saved primary L14 boundary readout: `-1.174876`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-001-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L976) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `49.578079`; mean token NLL: `5.508676`.

</details>

**incorrect, confident**

```text
"make NADH" is my answer, and I stand by it.
```

Saved primary L14 boundary readout: `0.675492`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-001-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L981) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `54`; final content `53`; boundary `54` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `69.429047`; mean token NLL: `4.339315`.

</details>

**incorrect, hedged**

```text
"make NADH" is my tentative answer.
```

Saved primary L14 boundary readout: `-1.471699`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-001-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L982) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `49`; final content `48`; boundary `49` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `61.497429`; mean token NLL: `5.590675`.

</details>

### Rewrite family C

**correct, confident**

```text
"produce ATP" is my definite conclusion.
```

Saved primary L14 boundary readout: `-0.777024`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-001-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L977) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `57.892761`; mean token NLL: `6.432529`.

</details>

**correct, hedged**

```text
"produce ATP" is my provisional conclusion.
```

Saved primary L14 boundary readout: `-1.228899`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-001-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L978) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `58.347244`; mean token NLL: `6.483027`.

</details>

**incorrect, confident**

```text
"make NADH" is my definite conclusion.
```

Saved primary L14 boundary readout: `-0.931584`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-001-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L983) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `49`; final content `48`; boundary `49` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `68.470467`; mean token NLL: `6.224588`.

</details>

**incorrect, hedged**

```text
"make NADH" is my provisional conclusion.
```

Saved primary L14 boundary readout: `-1.644857`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-001-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L984) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `49`; final content `48`; boundary `49` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `70.150421`; mean token NLL: `6.377311`.

</details>

[Back to question list](#academic) · [Dataset overview](README.md)

## academic-002

[Raw source](../../data/paired_confidence/source_items.jsonl#L83)

Question:

```text
What is the chemical symbol for antimony?
```

Context:

No supplied passage.

Correct key:

```text
Sb
```

Authored incorrect key:

```text
Fe
```

Original source: `cais/mmlu`, pinned test split, row `2983`, subject `high_school_chemistry`, revision `c30699e8356da336a370243923dbaf21066bb9fe`.

Original multiple-choice options:

```text
0: W
1: Sb
2: Fe
3: An
```

Phase A included: `true`; Phase A split: `train`; Phase B split: `train`.

Saved key explanation:

```text
Sb denotes antimony; Fe denotes iron.
```

### Rewrite family A

**correct, confident**

```text
I have no doubt: the answer is "Sb".
```

Saved primary L14 boundary readout: `3.332680`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-002-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L985) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `39.782227`; mean token NLL: `3.315186`.

</details>

**correct, hedged**

```text
I have some doubt: the answer is "Sb".
```

Saved primary L14 boundary readout: `-2.876967`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-002-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L986) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `49.836815`; mean token NLL: `4.153068`.

</details>

**incorrect, confident**

```text
I have no doubt: the answer is "Fe".
```

Saved primary L14 boundary readout: `2.630188`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-002-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L991) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `61.549133`; mean token NLL: `5.595376`.

</details>

**incorrect, hedged**

```text
I have some doubt: the answer is "Fe".
```

Saved primary L14 boundary readout: `-3.072159`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-002-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L992) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `69.496086`; mean token NLL: `6.317826`.

</details>

### Rewrite family B

**correct, confident**

```text
"Sb" is the answer I commit to.
```

Saved primary L14 boundary readout: `2.526594`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-002-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L987) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `68.440002`; mean token NLL: `6.844000`.

</details>

**correct, hedged**

```text
"Sb" is the answer I lean toward.
```

Saved primary L14 boundary readout: `0.229349`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-002-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L988) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `66.673569`; mean token NLL: `6.667357`.

</details>

**incorrect, confident**

```text
"Fe" is the answer I commit to.
```

Saved primary L14 boundary readout: `2.157084`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-002-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L993) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `71.521950`; mean token NLL: `7.152195`.

</details>

**incorrect, hedged**

```text
"Fe" is the answer I lean toward.
```

Saved primary L14 boundary readout: `-0.302637`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-002-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L994) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `69.530182`; mean token NLL: `6.953018`.

</details>

### Rewrite family C

**correct, confident**

```text
My conviction is that the answer is "Sb".
```

Saved primary L14 boundary readout: `1.372777`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-002-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L989) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `40.766045`; mean token NLL: `3.706004`.

</details>

**correct, hedged**

```text
My guess is that the answer is "Sb".
```

Saved primary L14 boundary readout: `-0.252678`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-002-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L990) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `32.025848`; mean token NLL: `2.911441`.

</details>

**incorrect, confident**

```text
My conviction is that the answer is "Fe".
```

Saved primary L14 boundary readout: `0.771486`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-002-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L995) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `61.985020`; mean token NLL: `6.198502`.

</details>

**incorrect, hedged**

```text
My guess is that the answer is "Fe".
```

Saved primary L14 boundary readout: `-0.589952`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-002-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L996) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `48.460854`; mean token NLL: `4.846086`.

</details>

[Back to question list](#academic) · [Dataset overview](README.md)

## academic-003

[Raw source](../../data/paired_confidence/source_items.jsonl#L84)

Question:

```text
What is continued population growth after replacement fertility has been achieved called?
```

Context:

No supplied passage.

Correct key:

```text
demographic momentum
```

Authored incorrect key:

```text
zero population growth
```

Original source: `cais/mmlu`, pinned test split, row `3448`, subject `high_school_geography`, revision `c30699e8356da336a370243923dbaf21066bb9fe`.

Original multiple-choice options:

```text
0: zero population growth.
1: rapid growth rate.
2: homeostatic plateau.
3: demographic momentum.
```

Phase A included: `true`; Phase A split: `test`; Phase B split: `train`.

Saved key explanation:

```text
Demographic momentum is the keyed term; zero population growth describes a different condition.
```

### Rewrite family A

**correct, confident**

```text
With confidence, my answer is "demographic momentum".
```

Saved primary L14 boundary readout: `2.628428`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-003-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L997) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `34`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `44.439571`; mean token NLL: `4.039961`.

</details>

**correct, hedged**

```text
With some uncertainty, my answer is "demographic momentum".
```

Saved primary L14 boundary readout: `1.696705`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-003-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L998) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `34`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `44.613697`; mean token NLL: `3.717808`.

</details>

**incorrect, confident**

```text
With confidence, my answer is "zero population growth".
```

Saved primary L14 boundary readout: `2.233190`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-003-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1003) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `34`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `44.704369`; mean token NLL: `4.064034`.

</details>

**incorrect, hedged**

```text
With some uncertainty, my answer is "zero population growth".
```

Saved primary L14 boundary readout: `1.544365`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-003-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1004) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `34`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `44.581036`; mean token NLL: `3.715086`.

</details>

### Rewrite family B

**correct, confident**

```text
My answer is "demographic momentum"; I would give it without hesitation.
```

Saved primary L14 boundary readout: `2.661282`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-003-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L999) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `34`; response stop (exclusive) `49`; final content `48`; boundary `49` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `73.296753`; mean token NLL: `4.886450`.

</details>

**correct, hedged**

```text
My answer is "demographic momentum"; I would give it with hesitation.
```

Saved primary L14 boundary readout: `-0.879742`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-003-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1000) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `34`; response stop (exclusive) `49`; final content `48`; boundary `49` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `84.806122`; mean token NLL: `5.653741`.

</details>

**incorrect, confident**

```text
My answer is "zero population growth"; I would give it without hesitation.
```

Saved primary L14 boundary readout: `2.470562`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-003-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1005) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `34`; response stop (exclusive) `49`; final content `48`; boundary `49` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `71.763641`; mean token NLL: `4.784243`.

</details>

**incorrect, hedged**

```text
My answer is "zero population growth"; I would give it with hesitation.
```

Saved primary L14 boundary readout: `-0.950227`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-003-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1006) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `34`; response stop (exclusive) `49`; final content `48`; boundary `49` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `80.818748`; mean token NLL: `5.387917`.

</details>

### Rewrite family C

**correct, confident**

```text
I regard "demographic momentum" as established.
```

Saved primary L14 boundary readout: `-0.657921`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-003-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1001) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `34`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `56.817940`; mean token NLL: `5.681794`.

</details>

**correct, hedged**

```text
I regard "demographic momentum" as provisional.
```

Saved primary L14 boundary readout: `-1.131337`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-003-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1002) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `34`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `59.334293`; mean token NLL: `5.933429`.

</details>

**incorrect, confident**

```text
I regard "zero population growth" as established.
```

Saved primary L14 boundary readout: `-0.590227`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-003-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1007) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `34`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `47.389198`; mean token NLL: `4.738920`.

</details>

**incorrect, hedged**

```text
I regard "zero population growth" as provisional.
```

Saved primary L14 boundary readout: `-1.364675`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-003-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1008) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `34`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `51.919945`; mean token NLL: `5.191995`.

</details>

[Back to question list](#academic) · [Dataset overview](README.md)

## academic-004

[Raw source](../../data/paired_confidence/source_items.jsonl#L85)

Question:

```text
Let x = 1. What is x << 3 in Python 3?
```

Context:

No supplied passage.

Correct key:

```text
8
```

Authored incorrect key:

```text
3
```

Original source: `cais/mmlu`, pinned test split, row `3182`, subject `high_school_computer_science`, revision `c30699e8356da336a370243923dbaf21066bb9fe`.

Original multiple-choice options:

```text
0: 1
1: 3
2: 8
3: 16
```

Phase A included: `true`; Phase A split: `train`; Phase B split: `train`.

Saved key explanation:

```text
A three-bit left shift gives 8, not 3.
```

### Rewrite family A

**correct, confident**

```text
I am confident the answer is "8".
```

Saved primary L14 boundary readout: `2.918187`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-004-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1009) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `39.933979`; mean token NLL: `4.437109`.

</details>

**correct, hedged**

```text
I am uncertain, but my answer is "8".
```

Saved primary L14 boundary readout: `0.331971`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-004-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1010) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `49`; final content `48`; boundary `49` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `56.306129`; mean token NLL: `5.118739`.

</details>

**incorrect, confident**

```text
I am confident the answer is "3".
```

Saved primary L14 boundary readout: `2.918975`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-004-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1015) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `42.397404`; mean token NLL: `4.710823`.

</details>

**incorrect, hedged**

```text
I am uncertain, but my answer is "3".
```

Saved primary L14 boundary readout: `0.229010`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-004-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1016) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `49`; final content `48`; boundary `49` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `54.934456`; mean token NLL: `4.994041`.

</details>

### Rewrite family B

**correct, confident**

```text
I settle on "8" as my answer.
```

Saved primary L14 boundary readout: `2.700921`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-004-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1011) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `48`; final content `47`; boundary `48` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `50.825241`; mean token NLL: `5.082524`.

</details>

**correct, hedged**

```text
I lean toward "8" as my answer.
```

Saved primary L14 boundary readout: `-0.178229`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-004-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1012) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `48`; final content `47`; boundary `48` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `48.757103`; mean token NLL: `4.875710`.

</details>

**incorrect, confident**

```text
I settle on "3" as my answer.
```

Saved primary L14 boundary readout: `2.743829`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-004-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1017) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `48`; final content `47`; boundary `48` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `48.574509`; mean token NLL: `4.857451`.

</details>

**incorrect, hedged**

```text
I lean toward "3" as my answer.
```

Saved primary L14 boundary readout: `-0.137772`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-004-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1018) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `48`; final content `47`; boundary `48` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `47.936466`; mean token NLL: `4.793647`.

</details>

### Rewrite family C

**correct, confident**

```text
I would stake my position on "8".
```

Saved primary L14 boundary readout: `1.894883`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-004-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1013) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `54.392883`; mean token NLL: `6.043653`.

</details>

**correct, hedged**

```text
I would cautiously suggest "8".
```

Saved primary L14 boundary readout: `0.432168`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-004-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1014) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `7`.

Sequence NLL: `47.939098`; mean token NLL: `6.848443`.

</details>

**incorrect, confident**

```text
I would stake my position on "3".
```

Saved primary L14 boundary readout: `1.719044`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-004-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1019) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `53.366859`; mean token NLL: `5.929651`.

</details>

**incorrect, hedged**

```text
I would cautiously suggest "3".
```

Saved primary L14 boundary readout: `0.591074`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-004-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1020) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `7`.

Sequence NLL: `46.527519`; mean token NLL: `6.646789`.

</details>

[Back to question list](#academic) · [Dataset overview](README.md)

## academic-005

[Raw source](../../data/paired_confidence/source_items.jsonl#L86)

Question:

```text
In test construction and evaluation, what does validity refer to?
```

Context:

No supplied passage.

Correct key:

```text
measures what it purports to measure
```

Authored incorrect key:

```text
yields consistent results on successive administrations
```

Original source: `cais/mmlu`, pinned test split, row `4890`, subject `high_school_psychology`, revision `c30699e8356da336a370243923dbaf21066bb9fe`.

Original multiple-choice options:

```text
0: measures what it purports to measure
1: yields consistent results on successive administrations
2: has been piloted and statistically analyzed
3: includes norms based on a representative sample of the general population
```

Phase A included: `true`; Phase A split: `train`; Phase B split: `train`.

Saved key explanation:

```text
Validity concerns whether the test measures its intended construct; consistent repeated results describe reliability.
```

### Rewrite family A

**correct, confident**

```text
I am sure the answer is "measures what it purports to measure".
```

Saved primary L14 boundary readout: `1.308723`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-005-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1021) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `49`; final content `48`; boundary `49` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `47.396549`; mean token NLL: `2.962284`.

</details>

**correct, hedged**

```text
I am not sure, but the answer is "measures what it purports to measure".
```

Saved primary L14 boundary readout: `-1.086524`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-005-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1022) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `52`; final content `51`; boundary `52` (`151645`, `<|im_end|>`). Response tokens: `19`.

Sequence NLL: `47.017334`; mean token NLL: `2.474597`.

</details>

**incorrect, confident**

```text
I am sure the answer is "yields consistent results on successive administrations".
```

Saved primary L14 boundary readout: `0.823683`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-005-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1027) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `48`; final content `47`; boundary `48` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `66.178772`; mean token NLL: `4.411918`.

</details>

**incorrect, hedged**

```text
I am not sure, but the answer is "yields consistent results on successive administrations".
```

Saved primary L14 boundary readout: `-1.124690`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-005-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1028) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `51`; final content `50`; boundary `51` (`151645`, `<|im_end|>`). Response tokens: `18`.

Sequence NLL: `63.984047`; mean token NLL: `3.554669`.

</details>

### Rewrite family B

**correct, confident**

```text
"measures what it purports to measure" is my answer, and I stand by it.
```

Saved primary L14 boundary readout: `1.171798`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-005-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1023) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `53`; final content `52`; boundary `53` (`151645`, `<|im_end|>`). Response tokens: `20`.

Sequence NLL: `65.294006`; mean token NLL: `3.264700`.

</details>

**correct, hedged**

```text
"measures what it purports to measure" is my tentative answer.
```

Saved primary L14 boundary readout: `-1.317747`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-005-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1024) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `48`; final content `47`; boundary `48` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `57.200806`; mean token NLL: `3.813387`.

</details>

**incorrect, confident**

```text
"yields consistent results on successive administrations" is my answer, and I stand by it.
```

Saved primary L14 boundary readout: `0.629474`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-005-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1029) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `52`; final content `51`; boundary `52` (`151645`, `<|im_end|>`). Response tokens: `19`.

Sequence NLL: `81.214882`; mean token NLL: `4.274467`.

</details>

**incorrect, hedged**

```text
"yields consistent results on successive administrations" is my tentative answer.
```

Saved primary L14 boundary readout: `-1.602901`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-005-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1030) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `74.640495`; mean token NLL: `5.331464`.

</details>

### Rewrite family C

**correct, confident**

```text
"measures what it purports to measure" is my definite conclusion.
```

Saved primary L14 boundary readout: `-0.895358`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-005-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1025) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `48`; final content `47`; boundary `48` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `63.618370`; mean token NLL: `4.241225`.

</details>

**correct, hedged**

```text
"measures what it purports to measure" is my provisional conclusion.
```

Saved primary L14 boundary readout: `-1.102479`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-005-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1026) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `48`; final content `47`; boundary `48` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `65.718750`; mean token NLL: `4.381250`.

</details>

**incorrect, confident**

```text
"yields consistent results on successive administrations" is my definite conclusion.
```

Saved primary L14 boundary readout: `-0.665996`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-005-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1031) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `82.775955`; mean token NLL: `5.912568`.

</details>

**incorrect, hedged**

```text
"yields consistent results on successive administrations" is my provisional conclusion.
```

Saved primary L14 boundary readout: `-1.552362`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-005-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1032) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `81.670746`; mean token NLL: `5.833625`.

</details>

[Back to question list](#academic) · [Dataset overview](README.md)

## academic-006

[Raw source](../../data/paired_confidence/source_items.jsonl#L87)

Question:

```text
What is the name of the ten-day New Year festival that celebrated Babylon's culture?
```

Context:

No supplied passage.

Correct key:

```text
Akitu
```

Authored incorrect key:

```text
Bast
```

Original source: `cais/mmlu`, pinned test split, row `13874`, subject `world_religions`, revision `c30699e8356da336a370243923dbaf21066bb9fe`.

Original multiple-choice options:

```text
0: Akitu
1: Wag and Thoth
2: Bast
3: Nehebkau
```

Phase A included: `true`; Phase A split: `test`; Phase B split: `train`.

Saved key explanation:

```text
Akitu is the Babylonian festival; Bast is the distractor. Only spelling and punctuation are standardized.
```

### Rewrite family A

**correct, confident**

```text
I have no doubt: the answer is "Akitu".
```

Saved primary L14 boundary readout: `3.367749`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-006-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1033) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `51`; final content `50`; boundary `51` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `34.604759`; mean token NLL: `2.661905`.

</details>

**correct, hedged**

```text
I have some doubt: the answer is "Akitu".
```

Saved primary L14 boundary readout: `-2.501381`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-006-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1034) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `51`; final content `50`; boundary `51` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `41.585754`; mean token NLL: `3.198904`.

</details>

**incorrect, confident**

```text
I have no doubt: the answer is "Bast".
```

Saved primary L14 boundary readout: `3.090665`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-006-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1039) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `50`; final content `49`; boundary `50` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `54.483543`; mean token NLL: `4.540295`.

</details>

**incorrect, hedged**

```text
I have some doubt: the answer is "Bast".
```

Saved primary L14 boundary readout: `-2.921266`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-006-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1040) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `50`; final content `49`; boundary `50` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `57.959061`; mean token NLL: `4.829922`.

</details>

### Rewrite family B

**correct, confident**

```text
"Akitu" is the answer I commit to.
```

Saved primary L14 boundary readout: `2.579021`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-006-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1035) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `49`; final content `48`; boundary `49` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `55.103176`; mean token NLL: `5.009380`.

</details>

**correct, hedged**

```text
"Akitu" is the answer I lean toward.
```

Saved primary L14 boundary readout: `0.575559`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-006-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1036) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `49`; final content `48`; boundary `49` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `53.507362`; mean token NLL: `4.864305`.

</details>

**incorrect, confident**

```text
"Bast" is the answer I commit to.
```

Saved primary L14 boundary readout: `2.623627`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-006-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1041) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `48`; final content `47`; boundary `48` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `60.806458`; mean token NLL: `6.080646`.

</details>

**incorrect, hedged**

```text
"Bast" is the answer I lean toward.
```

Saved primary L14 boundary readout: `0.431770`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-006-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1042) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `48`; final content `47`; boundary `48` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `59.550751`; mean token NLL: `5.955075`.

</details>

### Rewrite family C

**correct, confident**

```text
My conviction is that the answer is "Akitu".
```

Saved primary L14 boundary readout: `1.641626`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-006-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1037) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `50`; final content `49`; boundary `50` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `33.359413`; mean token NLL: `2.779951`.

</details>

**correct, hedged**

```text
My guess is that the answer is "Akitu".
```

Saved primary L14 boundary readout: `0.542779`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-006-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1038) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `50`; final content `49`; boundary `50` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `24.463230`; mean token NLL: `2.038603`.

</details>

**incorrect, confident**

```text
My conviction is that the answer is "Bast".
```

Saved primary L14 boundary readout: `1.274594`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-006-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1043) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `49`; final content `48`; boundary `49` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `52.195477`; mean token NLL: `4.745043`.

</details>

**incorrect, hedged**

```text
My guess is that the answer is "Bast".
```

Saved primary L14 boundary readout: `0.209166`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-006-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1044) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `49`; final content `48`; boundary `49` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `41.561256`; mean token NLL: `3.778296`.

</details>

[Back to question list](#academic) · [Dataset overview](README.md)

## academic-007

[Raw source](../../data/paired_confidence/source_items.jsonl#L88)

Question:

```text
Where is the sinoatrial node located?
```

Context:

No supplied passage.

Correct key:

```text
In the upper wall of the right atrium
```

Authored incorrect key:

```text
In the upper wall of the left ventricle
```

Original source: `cais/mmlu`, pinned test split, row `120`, subject `anatomy`, revision `c30699e8356da336a370243923dbaf21066bb9fe`.

Original multiple-choice options:

```text
0: Between the left atrium and the left ventricle
1: Between the right atrium and the right ventricle
2: In the upper wall of the right atrium
3: In the upper wall of the left ventricle
```

Phase A included: `true`; Phase A split: `validation`; Phase B split: `train`.

Saved key explanation:

```text
The keyed location is the upper right atrial wall; the selected wrong location is the upper left ventricular wall.
```

### Rewrite family A

**correct, confident**

```text
With confidence, my answer is "In the upper wall of the right atrium".
```

Saved primary L14 boundary readout: `2.375363`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-007-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1045) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `17`.

Sequence NLL: `47.290764`; mean token NLL: `2.781810`.

</details>

**correct, hedged**

```text
With some uncertainty, my answer is "In the upper wall of the right atrium".
```

Saved primary L14 boundary readout: `1.420612`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-007-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1046) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `48`; final content `47`; boundary `48` (`151645`, `<|im_end|>`). Response tokens: `18`.

Sequence NLL: `53.087692`; mean token NLL: `2.949316`.

</details>

**incorrect, confident**

```text
With confidence, my answer is "In the upper wall of the left ventricle".
```

Saved primary L14 boundary readout: `2.145140`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-007-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1051) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `48`; final content `47`; boundary `48` (`151645`, `<|im_end|>`). Response tokens: `18`.

Sequence NLL: `55.229137`; mean token NLL: `3.068285`.

</details>

**incorrect, hedged**

```text
With some uncertainty, my answer is "In the upper wall of the left ventricle".
```

Saved primary L14 boundary readout: `1.213637`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-007-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1052) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `49`; final content `48`; boundary `49` (`151645`, `<|im_end|>`). Response tokens: `19`.

Sequence NLL: `60.327480`; mean token NLL: `3.175131`.

</details>

### Rewrite family B

**correct, confident**

```text
My answer is "In the upper wall of the right atrium"; I would give it without hesitation.
```

Saved primary L14 boundary readout: `2.049705`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-007-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1047) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `51`; final content `50`; boundary `51` (`151645`, `<|im_end|>`). Response tokens: `21`.

Sequence NLL: `69.121704`; mean token NLL: `3.291510`.

</details>

**correct, hedged**

```text
My answer is "In the upper wall of the right atrium"; I would give it with hesitation.
```

Saved primary L14 boundary readout: `-1.706370`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-007-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1048) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `51`; final content `50`; boundary `51` (`151645`, `<|im_end|>`). Response tokens: `21`.

Sequence NLL: `79.120171`; mean token NLL: `3.767627`.

</details>

**incorrect, confident**

```text
My answer is "In the upper wall of the left ventricle"; I would give it without hesitation.
```

Saved primary L14 boundary readout: `2.221140`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-007-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1053) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `52`; final content `51`; boundary `52` (`151645`, `<|im_end|>`). Response tokens: `22`.

Sequence NLL: `77.141174`; mean token NLL: `3.506417`.

</details>

**incorrect, hedged**

```text
My answer is "In the upper wall of the left ventricle"; I would give it with hesitation.
```

Saved primary L14 boundary readout: `-1.669967`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-007-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1054) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `52`; final content `51`; boundary `52` (`151645`, `<|im_end|>`). Response tokens: `22`.

Sequence NLL: `86.578636`; mean token NLL: `3.935393`.

</details>

### Rewrite family C

**correct, confident**

```text
I regard "In the upper wall of the right atrium" as established.
```

Saved primary L14 boundary readout: `-0.281080`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-007-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1049) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `69.727592`; mean token NLL: `4.357975`.

</details>

**correct, hedged**

```text
I regard "In the upper wall of the right atrium" as provisional.
```

Saved primary L14 boundary readout: `-1.641389`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-007-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1050) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `66.962364`; mean token NLL: `4.185148`.

</details>

**incorrect, confident**

```text
I regard "In the upper wall of the left ventricle" as established.
```

Saved primary L14 boundary readout: `-0.422444`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-007-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1055) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `17`.

Sequence NLL: `76.189957`; mean token NLL: `4.481762`.

</details>

**incorrect, hedged**

```text
I regard "In the upper wall of the left ventricle" as provisional.
```

Saved primary L14 boundary readout: `-1.864872`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-007-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1056) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `17`.

Sequence NLL: `72.610382`; mean token NLL: `4.271199`.

</details>

[Back to question list](#academic) · [Dataset overview](README.md)

## academic-008

[Raw source](../../data/paired_confidence/source_items.jsonl#L89)

Question:

```text
On which planet in our solar system can you find the Great Red Spot?
```

Context:

No supplied passage.

Correct key:

```text
Jupiter
```

Authored incorrect key:

```text
Mars
```

Original source: `cais/mmlu`, pinned test split, row `250`, subject `astronomy`, revision `c30699e8356da336a370243923dbaf21066bb9fe`.

Original multiple-choice options:

```text
0: Venus
1: Mars
2: Jupiter
3: Saturn
```

Phase A included: `false`; Phase A split: `not included`; Phase B split: `train`.

Saved key explanation:

```text
The Great Red Spot is on Jupiter, not Mars.
```

### Rewrite family A

**correct, confident**

```text
I am confident the answer is "Jupiter".
```

Saved primary L14 boundary readout: `3.114848`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-008-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1057) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `36`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `31.715494`; mean token NLL: `3.171549`.

</details>

**correct, hedged**

```text
I am uncertain, but my answer is "Jupiter".
```

Saved primary L14 boundary readout: `0.756798`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-008-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1058) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `36`; response stop (exclusive) `48`; final content `47`; boundary `48` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `52.641407`; mean token NLL: `4.386784`.

</details>

**incorrect, confident**

```text
I am confident the answer is "Mars".
```

Saved primary L14 boundary readout: `2.812589`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-008-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1063) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `36`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `39.282120`; mean token NLL: `3.928212`.

</details>

**incorrect, hedged**

```text
I am uncertain, but my answer is "Mars".
```

Saved primary L14 boundary readout: `0.482194`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-008-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1064) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `36`; response stop (exclusive) `48`; final content `47`; boundary `48` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `56.490131`; mean token NLL: `4.707511`.

</details>

### Rewrite family B

**correct, confident**

```text
I settle on "Jupiter" as my answer.
```

Saved primary L14 boundary readout: `2.733522`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-008-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1059) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `36`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `40.481808`; mean token NLL: `3.680164`.

</details>

**correct, hedged**

```text
I lean toward "Jupiter" as my answer.
```

Saved primary L14 boundary readout: `-0.099765`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-008-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1060) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `36`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `36.806763`; mean token NLL: `3.346069`.

</details>

**incorrect, confident**

```text
I settle on "Mars" as my answer.
```

Saved primary L14 boundary readout: `2.389761`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-008-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1065) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `36`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `44.688339`; mean token NLL: `4.062576`.

</details>

**incorrect, hedged**

```text
I lean toward "Mars" as my answer.
```

Saved primary L14 boundary readout: `-0.534242`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-008-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1066) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `36`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `39.671261`; mean token NLL: `3.606478`.

</details>

### Rewrite family C

**correct, confident**

```text
I would stake my position on "Jupiter".
```

Saved primary L14 boundary readout: `2.657261`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-008-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1061) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `36`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `42.905201`; mean token NLL: `4.290520`.

</details>

**correct, hedged**

```text
I would cautiously suggest "Jupiter".
```

Saved primary L14 boundary readout: `2.003363`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-008-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1062) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `36`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `8`.

Sequence NLL: `35.949982`; mean token NLL: `4.493748`.

</details>

**incorrect, confident**

```text
I would stake my position on "Mars".
```

Saved primary L14 boundary readout: `2.420511`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-008-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1067) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `36`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `46.724998`; mean token NLL: `4.672500`.

</details>

**incorrect, hedged**

```text
I would cautiously suggest "Mars".
```

Saved primary L14 boundary readout: `1.741360`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-008-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1068) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `36`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `8`.

Sequence NLL: `40.261726`; mean token NLL: `5.032716`.

</details>

[Back to question list](#academic) · [Dataset overview](README.md)

## academic-009

[Raw source](../../data/paired_confidence/source_items.jsonl#L90)

Question:

```text
Of Callisto, Europa, Ganymede, and Io, which moon is closest to Jupiter?
```

Context:

No supplied passage.

Correct key:

```text
Io
```

Authored incorrect key:

```text
Callisto
```

Original source: `cais/mmlu`, pinned test split, row `260`, subject `astronomy`, revision `c30699e8356da336a370243923dbaf21066bb9fe`.

Original multiple-choice options:

```text
0: Callisto
1: Europa
2: Ganymede
3: Io
```

Phase A included: `false`; Phase A split: `not included`; Phase B split: `train`.

Saved key explanation:

```text
The original stem explicitly names the four Galilean moons; the adapted question preserves that restriction. Io is closest; Callisto is farthest.
```

### Rewrite family A

**correct, confident**

```text
I am sure the answer is "Io".
```

Saved primary L14 boundary readout: `2.586135`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-009-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1069) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `41`; response stop (exclusive) `50`; final content `49`; boundary `50` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `33.701313`; mean token NLL: `3.744590`.

</details>

**correct, hedged**

```text
I am not sure, but the answer is "Io".
```

Saved primary L14 boundary readout: `-0.551925`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-009-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1070) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `41`; response stop (exclusive) `53`; final content `52`; boundary `53` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `33.690380`; mean token NLL: `2.807532`.

</details>

**incorrect, confident**

```text
I am sure the answer is "Callisto".
```

Saved primary L14 boundary readout: `2.639369`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-009-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1075) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `41`; response stop (exclusive) `51`; final content `50`; boundary `51` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `39.340446`; mean token NLL: `3.934045`.

</details>

**incorrect, hedged**

```text
I am not sure, but the answer is "Callisto".
```

Saved primary L14 boundary readout: `-0.370069`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-009-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1076) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `41`; response stop (exclusive) `54`; final content `53`; boundary `54` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `37.527946`; mean token NLL: `2.886765`.

</details>

### Rewrite family B

**correct, confident**

```text
"Io" is my answer, and I stand by it.
```

Saved primary L14 boundary readout: `1.643264`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-009-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1071) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `41`; response stop (exclusive) `54`; final content `53`; boundary `54` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `50.650108`; mean token NLL: `3.896162`.

</details>

**correct, hedged**

```text
"Io" is my tentative answer.
```

Saved primary L14 boundary readout: `0.369042`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-009-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1072) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `41`; response stop (exclusive) `49`; final content `48`; boundary `49` (`151645`, `<|im_end|>`). Response tokens: `8`.

Sequence NLL: `42.720856`; mean token NLL: `5.340107`.

</details>

**incorrect, confident**

```text
"Callisto" is my answer, and I stand by it.
```

Saved primary L14 boundary readout: `1.554829`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-009-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1077) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `41`; response stop (exclusive) `55`; final content `54`; boundary `55` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `47.059929`; mean token NLL: `3.361423`.

</details>

**incorrect, hedged**

```text
"Callisto" is my tentative answer.
```

Saved primary L14 boundary readout: `0.582844`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-009-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1078) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `41`; response stop (exclusive) `50`; final content `49`; boundary `50` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `37.707214`; mean token NLL: `4.189691`.

</details>

### Rewrite family C

**correct, confident**

```text
"Io" is my definite conclusion.
```

Saved primary L14 boundary readout: `1.120282`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-009-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1073) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `41`; response stop (exclusive) `49`; final content `48`; boundary `49` (`151645`, `<|im_end|>`). Response tokens: `8`.

Sequence NLL: `53.018745`; mean token NLL: `6.627343`.

</details>

**correct, hedged**

```text
"Io" is my provisional conclusion.
```

Saved primary L14 boundary readout: `0.004471`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-009-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1074) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `41`; response stop (exclusive) `49`; final content `48`; boundary `49` (`151645`, `<|im_end|>`). Response tokens: `8`.

Sequence NLL: `51.420799`; mean token NLL: `6.427600`.

</details>

**incorrect, confident**

```text
"Callisto" is my definite conclusion.
```

Saved primary L14 boundary readout: `1.426467`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-009-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1079) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `41`; response stop (exclusive) `50`; final content `49`; boundary `50` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `46.997993`; mean token NLL: `5.221999`.

</details>

**incorrect, hedged**

```text
"Callisto" is my provisional conclusion.
```

Saved primary L14 boundary readout: `0.117929`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-009-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1080) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `41`; response stop (exclusive) `50`; final content `49`; boundary `50` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `46.956543`; mean token NLL: `5.217394`.

</details>

[Back to question list](#academic) · [Dataset overview](README.md)

## academic-010

[Raw source](../../data/paired_confidence/source_items.jsonl#L91)

Question:

```text
What does the astronomical term ecliptic describe?
```

Context:

No supplied passage.

Correct key:

```text
The path of the Sun in the sky throughout a year
```

Authored incorrect key:

```text
The axial tilt of the Earth throughout a year
```

Original source: `cais/mmlu`, pinned test split, row `271`, subject `astronomy`, revision `c30699e8356da336a370243923dbaf21066bb9fe`.

Original multiple-choice options:

```text
0: The path of the Sun in the sky throughout a year.
1: The axial tilt of the Earth throughout a year.
2: The movement of the stars due to Earth’s rotation.
3: The central line through the axis of rotation.
```

Phase A included: `false`; Phase A split: `not included`; Phase B split: `train`.

Saved key explanation:

```text
It describes the Sun's apparent annual path across the sky, not Earth's axial tilt.
```

### Rewrite family A

**correct, confident**

```text
I have no doubt: the answer is "The path of the Sun in the sky throughout a year".
```

Saved primary L14 boundary readout: `3.303082`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-010-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1081) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `52`; final content `51`; boundary `52` (`151645`, `<|im_end|>`). Response tokens: `21`.

Sequence NLL: `55.143105`; mean token NLL: `2.625862`.

</details>

**correct, hedged**

```text
I have some doubt: the answer is "The path of the Sun in the sky throughout a year".
```

Saved primary L14 boundary readout: `-2.540363`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-010-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1082) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `52`; final content `51`; boundary `52` (`151645`, `<|im_end|>`). Response tokens: `21`.

Sequence NLL: `59.261883`; mean token NLL: `2.821994`.

</details>

**incorrect, confident**

```text
I have no doubt: the answer is "The axial tilt of the Earth throughout a year".
```

Saved primary L14 boundary readout: `2.869078`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-010-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1087) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `50`; final content `49`; boundary `50` (`151645`, `<|im_end|>`). Response tokens: `19`.

Sequence NLL: `73.829910`; mean token NLL: `3.885785`.

</details>

**incorrect, hedged**

```text
I have some doubt: the answer is "The axial tilt of the Earth throughout a year".
```

Saved primary L14 boundary readout: `-2.466366`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-010-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1088) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `50`; final content `49`; boundary `50` (`151645`, `<|im_end|>`). Response tokens: `19`.

Sequence NLL: `76.752937`; mean token NLL: `4.039629`.

</details>

### Rewrite family B

**correct, confident**

```text
"The path of the Sun in the sky throughout a year" is the answer I commit to.
```

Saved primary L14 boundary readout: `2.359476`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-010-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1083) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `50`; final content `49`; boundary `50` (`151645`, `<|im_end|>`). Response tokens: `19`.

Sequence NLL: `68.977264`; mean token NLL: `3.630382`.

</details>

**correct, hedged**

```text
"The path of the Sun in the sky throughout a year" is the answer I lean toward.
```

Saved primary L14 boundary readout: `-0.438477`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-010-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1084) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `50`; final content `49`; boundary `50` (`151645`, `<|im_end|>`). Response tokens: `19`.

Sequence NLL: `63.839336`; mean token NLL: `3.359965`.

</details>

**incorrect, confident**

```text
"The axial tilt of the Earth throughout a year" is the answer I commit to.
```

Saved primary L14 boundary readout: `1.931866`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-010-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1089) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `48`; final content `47`; boundary `48` (`151645`, `<|im_end|>`). Response tokens: `17`.

Sequence NLL: `80.822258`; mean token NLL: `4.754251`.

</details>

**incorrect, hedged**

```text
"The axial tilt of the Earth throughout a year" is the answer I lean toward.
```

Saved primary L14 boundary readout: `-0.491818`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-010-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1090) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `48`; final content `47`; boundary `48` (`151645`, `<|im_end|>`). Response tokens: `17`.

Sequence NLL: `76.320633`; mean token NLL: `4.489449`.

</details>

### Rewrite family C

**correct, confident**

```text
My conviction is that the answer is "The path of the Sun in the sky throughout a year".
```

Saved primary L14 boundary readout: `2.049453`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-010-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1085) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `51`; final content `50`; boundary `51` (`151645`, `<|im_end|>`). Response tokens: `20`.

Sequence NLL: `50.895729`; mean token NLL: `2.544786`.

</details>

**correct, hedged**

```text
My guess is that the answer is "The path of the Sun in the sky throughout a year".
```

Saved primary L14 boundary readout: `0.539093`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-010-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1086) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `51`; final content `50`; boundary `51` (`151645`, `<|im_end|>`). Response tokens: `20`.

Sequence NLL: `42.729855`; mean token NLL: `2.136493`.

</details>

**incorrect, confident**

```text
My conviction is that the answer is "The axial tilt of the Earth throughout a year".
```

Saved primary L14 boundary readout: `1.605298`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-010-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1091) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `49`; final content `48`; boundary `49` (`151645`, `<|im_end|>`). Response tokens: `18`.

Sequence NLL: `69.729996`; mean token NLL: `3.873889`.

</details>

**incorrect, hedged**

```text
My guess is that the answer is "The axial tilt of the Earth throughout a year".
```

Saved primary L14 boundary readout: `0.404381`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-010-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1092) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `49`; final content `48`; boundary `49` (`151645`, `<|im_end|>`). Response tokens: `18`.

Sequence NLL: `56.061737`; mean token NLL: `3.114541`.

</details>

[Back to question list](#academic) · [Dataset overview](README.md)

## academic-011

[Raw source](../../data/paired_confidence/source_items.jsonl#L92)

Question:

```text
What type of radiation causes a black hole to evaporate over time?
```

Context:

No supplied passage.

Correct key:

```text
Hawking radiation
```

Authored incorrect key:

```text
Planck radiation
```

Original source: `cais/mmlu`, pinned test split, row `308`, subject `astronomy`, revision `c30699e8356da336a370243923dbaf21066bb9fe`.

Original multiple-choice options:

```text
0: Schwarzschild radiation
1: Planck radiation
2: Kolmogorov radiation
3: Hawking radiation
```

Phase A included: `false`; Phase A split: `not included`; Phase B split: `test`.

Saved key explanation:

```text
Hawking radiation is the keyed phenomenon; Planck radiation is the distractor.
```

### Rewrite family A

**correct, confident**

```text
With confidence, my answer is "Hawking radiation".
```

Saved primary L14 boundary readout: `2.385095`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-011-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1093) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `35`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `48.448814`; mean token NLL: `4.037401`.

</details>

**correct, hedged**

```text
With some uncertainty, my answer is "Hawking radiation".
```

Saved primary L14 boundary readout: `1.558475`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-011-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1094) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `35`; response stop (exclusive) `48`; final content `47`; boundary `48` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `46.116501`; mean token NLL: `3.547423`.

</details>

**incorrect, confident**

```text
With confidence, my answer is "Planck radiation".
```

Saved primary L14 boundary readout: `1.944992`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-011-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1099) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `35`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `52.550751`; mean token NLL: `4.777341`.

</details>

**incorrect, hedged**

```text
With some uncertainty, my answer is "Planck radiation".
```

Saved primary L14 boundary readout: `1.047520`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-011-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1100) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `35`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `51.725441`; mean token NLL: `4.310453`.

</details>

### Rewrite family B

**correct, confident**

```text
My answer is "Hawking radiation"; I would give it without hesitation.
```

Saved primary L14 boundary readout: `2.293125`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-011-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1095) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `35`; response stop (exclusive) `51`; final content `50`; boundary `51` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `77.764427`; mean token NLL: `4.860277`.

</details>

**correct, hedged**

```text
My answer is "Hawking radiation"; I would give it with hesitation.
```

Saved primary L14 boundary readout: `-1.107123`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-011-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1096) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `35`; response stop (exclusive) `51`; final content `50`; boundary `51` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `88.327576`; mean token NLL: `5.520473`.

</details>

**incorrect, confident**

```text
My answer is "Planck radiation"; I would give it without hesitation.
```

Saved primary L14 boundary readout: `2.041669`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-011-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1101) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `35`; response stop (exclusive) `50`; final content `49`; boundary `50` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `88.679695`; mean token NLL: `5.911980`.

</details>

**incorrect, hedged**

```text
My answer is "Planck radiation"; I would give it with hesitation.
```

Saved primary L14 boundary readout: `-1.352626`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-011-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1102) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `35`; response stop (exclusive) `50`; final content `49`; boundary `50` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `98.112419`; mean token NLL: `6.540828`.

</details>

### Rewrite family C

**correct, confident**

```text
I regard "Hawking radiation" as established.
```

Saved primary L14 boundary readout: `-0.841436`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-011-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1097) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `35`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `68.546867`; mean token NLL: `6.231534`.

</details>

**correct, hedged**

```text
I regard "Hawking radiation" as provisional.
```

Saved primary L14 boundary readout: `-1.807672`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-011-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1098) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `35`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `67.774521`; mean token NLL: `6.161320`.

</details>

**incorrect, confident**

```text
I regard "Planck radiation" as established.
```

Saved primary L14 boundary readout: `-0.813344`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-011-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1103) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `35`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `67.940826`; mean token NLL: `6.794083`.

</details>

**incorrect, hedged**

```text
I regard "Planck radiation" as provisional.
```

Saved primary L14 boundary readout: `-1.965283`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-011-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1104) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `35`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `68.080574`; mean token NLL: `6.808057`.

</details>

[Back to question list](#academic) · [Dataset overview](README.md)

## academic-012

[Raw source](../../data/paired_confidence/source_items.jsonl#L93)

Question:

```text
What is the development of an egg without fertilization called?
```

Context:

No supplied passage.

Correct key:

```text
parthenogenesis
```

Authored incorrect key:

```text
meiosis
```

Original source: `cais/mmlu`, pinned test split, row `2700`, subject `high_school_biology`, revision `c30699e8356da336a370243923dbaf21066bb9fe`.

Original multiple-choice options:

```text
0: meiosis
1: parthenogenesis
2: embryogenesis
3: vegetative propagation
```

Phase A included: `false`; Phase A split: `not included`; Phase B split: `train`.

Saved key explanation:

```text
Parthenogenesis, not meiosis, denotes development without fertilization.
```

### Rewrite family A

**correct, confident**

```text
I am confident the answer is "parthenogenesis".
```

Saved primary L14 boundary readout: `2.822287`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-012-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1105) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `39.515308`; mean token NLL: `3.592301`.

</details>

**correct, hedged**

```text
I am uncertain, but my answer is "parthenogenesis".
```

Saved primary L14 boundary readout: `0.823586`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-012-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1106) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `55.649605`; mean token NLL: `4.280739`.

</details>

**incorrect, confident**

```text
I am confident the answer is "meiosis".
```

Saved primary L14 boundary readout: `2.821213`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-012-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1111) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `43`; final content `42`; boundary `43` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `41.281464`; mean token NLL: `4.128146`.

</details>

**incorrect, hedged**

```text
I am uncertain, but my answer is "meiosis".
```

Saved primary L14 boundary readout: `0.650765`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-012-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1112) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `62.069645`; mean token NLL: `5.172471`.

</details>

### Rewrite family B

**correct, confident**

```text
I settle on "parthenogenesis" as my answer.
```

Saved primary L14 boundary readout: `2.025100`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-012-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1107) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `51.522438`; mean token NLL: `4.293537`.

</details>

**correct, hedged**

```text
I lean toward "parthenogenesis" as my answer.
```

Saved primary L14 boundary readout: `-0.346066`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-012-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1108) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `41.643898`; mean token NLL: `3.470325`.

</details>

**incorrect, confident**

```text
I settle on "meiosis" as my answer.
```

Saved primary L14 boundary readout: `1.671054`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-012-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1113) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `51.560257`; mean token NLL: `4.687296`.

</details>

**incorrect, hedged**

```text
I lean toward "meiosis" as my answer.
```

Saved primary L14 boundary readout: `-0.521776`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-012-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1114) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `43.271046`; mean token NLL: `3.933731`.

</details>

### Rewrite family C

**correct, confident**

```text
I would stake my position on "parthenogenesis".
```

Saved primary L14 boundary readout: `1.164821`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-012-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1109) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `46.062592`; mean token NLL: `4.187508`.

</details>

**correct, hedged**

```text
I would cautiously suggest "parthenogenesis".
```

Saved primary L14 boundary readout: `1.338078`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-012-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1110) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `40.713356`; mean token NLL: `4.523706`.

</details>

**incorrect, confident**

```text
I would stake my position on "meiosis".
```

Saved primary L14 boundary readout: `1.071462`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-012-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1115) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `43`; final content `42`; boundary `43` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `48.390507`; mean token NLL: `4.839051`.

</details>

**incorrect, hedged**

```text
I would cautiously suggest "meiosis".
```

Saved primary L14 boundary readout: `1.458202`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-012-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1116) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `8`.

Sequence NLL: `42.326904`; mean token NLL: `5.290863`.

</details>

[Back to question list](#academic) · [Dataset overview](README.md)

## academic-013

[Raw source](../../data/paired_confidence/source_items.jsonl#L94)

Question:

```text
Where does fertilization normally occur in humans?
```

Context:

No supplied passage.

Correct key:

```text
fallopian tube
```

Authored incorrect key:

```text
uterus
```

Original source: `cais/mmlu`, pinned test split, row `2717`, subject `high_school_biology`, revision `c30699e8356da336a370243923dbaf21066bb9fe`.

Original multiple-choice options:

```text
0: ovary
1: fallopian tube
2: uterus
3: placenta
```

Phase A included: `false`; Phase A split: `not included`; Phase B split: `train`.

Saved key explanation:

```text
Normally it occurs in a fallopian tube, not in the uterus. The qualifier normally is preserved.
```

### Rewrite family A

**correct, confident**

```text
I am sure the answer is "fallopian tube".
```

Saved primary L14 boundary readout: `2.027105`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-013-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1117) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `47.681198`; mean token NLL: `3.973433`.

</details>

**correct, hedged**

```text
I am not sure, but the answer is "fallopian tube".
```

Saved primary L14 boundary readout: `-0.499879`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-013-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1118) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `47.329994`; mean token NLL: `3.155333`.

</details>

**incorrect, confident**

```text
I am sure the answer is "uterus".
```

Saved primary L14 boundary readout: `2.105617`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-013-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1123) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `39.506470`; mean token NLL: `3.950647`.

</details>

**incorrect, hedged**

```text
I am not sure, but the answer is "uterus".
```

Saved primary L14 boundary readout: `-1.108799`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-013-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1124) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `43`; final content `42`; boundary `43` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `40.943520`; mean token NLL: `3.149502`.

</details>

### Rewrite family B

**correct, confident**

```text
"fallopian tube" is my answer, and I stand by it.
```

Saved primary L14 boundary readout: `1.128848`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-013-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1119) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `58.603569`; mean token NLL: `3.662723`.

</details>

**correct, hedged**

```text
"fallopian tube" is my tentative answer.
```

Saved primary L14 boundary readout: `-0.785341`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-013-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1120) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `55.380493`; mean token NLL: `5.034590`.

</details>

**incorrect, confident**

```text
"uterus" is my answer, and I stand by it.
```

Saved primary L14 boundary readout: `1.223770`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-013-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1125) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `64.761314`; mean token NLL: `4.625808`.

</details>

**incorrect, hedged**

```text
"uterus" is my tentative answer.
```

Saved primary L14 boundary readout: `-0.611991`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-013-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1126) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `39`; final content `38`; boundary `39` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `56.597809`; mean token NLL: `6.288645`.

</details>

### Rewrite family C

**correct, confident**

```text
"fallopian tube" is my definite conclusion.
```

Saved primary L14 boundary readout: `-0.316720`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-013-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1121) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `64.120956`; mean token NLL: `5.829178`.

</details>

**correct, hedged**

```text
"fallopian tube" is my provisional conclusion.
```

Saved primary L14 boundary readout: `-1.459800`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-013-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1122) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `63.220192`; mean token NLL: `5.747290`.

</details>

**incorrect, confident**

```text
"uterus" is my definite conclusion.
```

Saved primary L14 boundary readout: `0.167128`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-013-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1127) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `39`; final content `38`; boundary `39` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `67.293304`; mean token NLL: `7.477034`.

</details>

**incorrect, hedged**

```text
"uterus" is my provisional conclusion.
```

Saved primary L14 boundary readout: `-1.271369`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-013-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1128) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `39`; final content `38`; boundary `39` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `64.546600`; mean token NLL: `7.171844`.

</details>

[Back to question list](#academic) · [Dataset overview](README.md)

## academic-014

[Raw source](../../data/paired_confidence/source_items.jsonl#L95)

Question:

```text
Where does the Krebs cycle occur in humans?
```

Context:

No supplied passage.

Correct key:

```text
mitochondrial matrix
```

Authored incorrect key:

```text
intermembrane space
```

Original source: `cais/mmlu`, pinned test split, row `2721`, subject `high_school_biology`, revision `c30699e8356da336a370243923dbaf21066bb9fe`.

Original multiple-choice options:

```text
0: mitochondrial matrix
1: inner mitochondrial membrane
2: outer mitochondrial membrane
3: intermembrane space
```

Phase A included: `false`; Phase A split: `not included`; Phase B split: `train`.

Saved key explanation:

```text
The mitochondrial matrix is the keyed site; the intermembrane space is not.
```

### Rewrite family A

**correct, confident**

```text
I have no doubt: the answer is "mitochondrial matrix".
```

Saved primary L14 boundary readout: `2.607711`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-014-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1129) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `49.154961`; mean token NLL: `3.511069`.

</details>

**correct, hedged**

```text
I have some doubt: the answer is "mitochondrial matrix".
```

Saved primary L14 boundary readout: `-3.303723`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-014-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1130) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `51.314873`; mean token NLL: `3.665348`.

</details>

**incorrect, confident**

```text
I have no doubt: the answer is "intermembrane space".
```

Saved primary L14 boundary readout: `2.257320`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-014-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1135) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `57.226219`; mean token NLL: `4.087587`.

</details>

**incorrect, hedged**

```text
I have some doubt: the answer is "intermembrane space".
```

Saved primary L14 boundary readout: `-3.426065`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-014-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1136) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `60.821259`; mean token NLL: `4.344376`.

</details>

### Rewrite family B

**correct, confident**

```text
"mitochondrial matrix" is the answer I commit to.
```

Saved primary L14 boundary readout: `0.408156`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-014-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1131) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `61.295967`; mean token NLL: `4.715075`.

</details>

**correct, hedged**

```text
"mitochondrial matrix" is the answer I lean toward.
```

Saved primary L14 boundary readout: `-1.809381`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-014-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1132) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `56.182945`; mean token NLL: `4.321765`.

</details>

**incorrect, confident**

```text
"intermembrane space" is the answer I commit to.
```

Saved primary L14 boundary readout: `0.084196`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-014-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1137) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `68.480759`; mean token NLL: `5.267751`.

</details>

**incorrect, hedged**

```text
"intermembrane space" is the answer I lean toward.
```

Saved primary L14 boundary readout: `-2.097173`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-014-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1138) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `62.875572`; mean token NLL: `4.836583`.

</details>

### Rewrite family C

**correct, confident**

```text
My conviction is that the answer is "mitochondrial matrix".
```

Saved primary L14 boundary readout: `1.041837`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-014-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1133) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `48.957993`; mean token NLL: `3.765999`.

</details>

**correct, hedged**

```text
My guess is that the answer is "mitochondrial matrix".
```

Saved primary L14 boundary readout: `-0.422224`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-014-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1134) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `35.905815`; mean token NLL: `2.761986`.

</details>

**incorrect, confident**

```text
My conviction is that the answer is "intermembrane space".
```

Saved primary L14 boundary readout: `0.872175`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-014-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1139) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `58.155785`; mean token NLL: `4.473522`.

</details>

**incorrect, hedged**

```text
My guess is that the answer is "intermembrane space".
```

Saved primary L14 boundary readout: `-0.594349`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-014-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1140) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `44.178810`; mean token NLL: `3.398370`.

</details>

[Back to question list](#academic) · [Dataset overview](README.md)

## academic-015

[Raw source](../../data/paired_confidence/source_items.jsonl#L96)

Question:

```text
During which phase of the cell cycle does the quantity of DNA in a eukaryotic cell typically double?
```

Context:

No supplied passage.

Correct key:

```text
S phase
```

Authored incorrect key:

```text
G1 phase
```

Original source: `cais/mmlu`, pinned test split, row `2723`, subject `high_school_biology`, revision `c30699e8356da336a370243923dbaf21066bb9fe`.

Original multiple-choice options:

```text
0: G_1
1: G_2
2: M
3: S
```

Phase A included: `false`; Phase A split: `not included`; Phase B split: `test`.

Saved key explanation:

```text
DNA replication occurs in S phase rather than G1; typically is preserved.
```

### Rewrite family A

**correct, confident**

```text
With confidence, my answer is "S phase".
```

Saved primary L14 boundary readout: `2.234974`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-015-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1141) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `43`; response stop (exclusive) `53`; final content `52`; boundary `53` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `43.917442`; mean token NLL: `4.391744`.

</details>

**correct, hedged**

```text
With some uncertainty, my answer is "S phase".
```

Saved primary L14 boundary readout: `0.780619`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-015-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1142) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `43`; response stop (exclusive) `54`; final content `53`; boundary `54` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `42.644676`; mean token NLL: `3.876789`.

</details>

**incorrect, confident**

```text
With confidence, my answer is "G1 phase".
```

Saved primary L14 boundary readout: `1.943378`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-015-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1147) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `43`; response stop (exclusive) `54`; final content `53`; boundary `54` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `49.765629`; mean token NLL: `4.524148`.

</details>

**incorrect, hedged**

```text
With some uncertainty, my answer is "G1 phase".
```

Saved primary L14 boundary readout: `0.689931`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-015-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1148) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `43`; response stop (exclusive) `55`; final content `54`; boundary `55` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `45.970448`; mean token NLL: `3.830871`.

</details>

### Rewrite family B

**correct, confident**

```text
My answer is "S phase"; I would give it without hesitation.
```

Saved primary L14 boundary readout: `1.625266`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-015-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1143) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `43`; response stop (exclusive) `57`; final content `56`; boundary `57` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `64.877869`; mean token NLL: `4.634133`.

</details>

**correct, hedged**

```text
My answer is "S phase"; I would give it with hesitation.
```

Saved primary L14 boundary readout: `-1.872077`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-015-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1144) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `43`; response stop (exclusive) `57`; final content `56`; boundary `57` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `73.645233`; mean token NLL: `5.260374`.

</details>

**incorrect, confident**

```text
My answer is "G1 phase"; I would give it without hesitation.
```

Saved primary L14 boundary readout: `1.584774`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-015-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1149) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `43`; response stop (exclusive) `58`; final content `57`; boundary `58` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `69.590111`; mean token NLL: `4.639341`.

</details>

**incorrect, hedged**

```text
My answer is "G1 phase"; I would give it with hesitation.
```

Saved primary L14 boundary readout: `-1.931373`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-015-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1150) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `43`; response stop (exclusive) `58`; final content `57`; boundary `58` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `78.625931`; mean token NLL: `5.241729`.

</details>

### Rewrite family C

**correct, confident**

```text
I regard "S phase" as established.
```

Saved primary L14 boundary readout: `-0.968702`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-015-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1145) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `43`; response stop (exclusive) `52`; final content `51`; boundary `52` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `55.715889`; mean token NLL: `6.190654`.

</details>

**correct, hedged**

```text
I regard "S phase" as provisional.
```

Saved primary L14 boundary readout: `-2.181076`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-015-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1146) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `43`; response stop (exclusive) `52`; final content `51`; boundary `52` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `55.118305`; mean token NLL: `6.124256`.

</details>

**incorrect, confident**

```text
I regard "G1 phase" as established.
```

Saved primary L14 boundary readout: `-1.375759`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-015-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1151) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `43`; response stop (exclusive) `53`; final content `52`; boundary `53` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `56.337070`; mean token NLL: `5.633707`.

</details>

**incorrect, hedged**

```text
I regard "G1 phase" as provisional.
```

Saved primary L14 boundary readout: `-2.605390`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-015-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1152) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `43`; response stop (exclusive) `53`; final content `52`; boundary `53` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `55.441784`; mean token NLL: `5.544178`.

</details>

[Back to question list](#academic) · [Dataset overview](README.md)

## academic-016

[Raw source](../../data/paired_confidence/source_items.jsonl#L97)

Question:

```text
What does Hund's rule require?
```

Context:

No supplied passage.

Correct key:

```text
no two electrons can pair up if there is an empty orbital at the same energy level available
```

Authored incorrect key:

```text
no two electrons can occupy separate orbitals
```

Original source: `cais/mmlu`, pinned test split, row `2986`, subject `high_school_chemistry`, revision `c30699e8356da336a370243923dbaf21066bb9fe`.

Original multiple-choice options:

```text
0: no two electrons can have the same four quantum numbers
1: no two electrons with the same spin can occupy an orbital
2: no two electrons can occupy separate orbitals
3: no two electrons can pair up if there is an empty orbital at the same energy level available
```

Phase A included: `false`; Phase A split: `not included`; Phase B split: `validation`.

Saved key explanation:

```text
Equal-energy orbitals are occupied singly before pairing. The chosen wrong statement forbids separate orbitals. The distractor about four quantum numbers was avoided because it states the valid Pauli principle.
```

### Rewrite family A

**correct, confident**

```text
I am confident the answer is "no two electrons can pair up if there is an empty orbital at the same energy level available".
```

Saved primary L14 boundary readout: `2.333175`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-016-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1153) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `28`; response stop (exclusive) `54`; final content `53`; boundary `54` (`151645`, `<|im_end|>`). Response tokens: `26`.

Sequence NLL: `97.494026`; mean token NLL: `3.749770`.

</details>

**correct, hedged**

```text
I am uncertain, but my answer is "no two electrons can pair up if there is an empty orbital at the same energy level available".
```

Saved primary L14 boundary readout: `-0.028677`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-016-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1154) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `28`; response stop (exclusive) `56`; final content `55`; boundary `56` (`151645`, `<|im_end|>`). Response tokens: `28`.

Sequence NLL: `111.138794`; mean token NLL: `3.969243`.

</details>

**incorrect, confident**

```text
I am confident the answer is "no two electrons can occupy separate orbitals".
```

Saved primary L14 boundary readout: `2.573588`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-016-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1159) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `28`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `75.225037`; mean token NLL: `4.701565`.

</details>

**incorrect, hedged**

```text
I am uncertain, but my answer is "no two electrons can occupy separate orbitals".
```

Saved primary L14 boundary readout: `-0.017362`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-016-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1160) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `28`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `18`.

Sequence NLL: `87.848862`; mean token NLL: `4.880492`.

</details>

### Rewrite family B

**correct, confident**

```text
I settle on "no two electrons can pair up if there is an empty orbital at the same energy level available" as my answer.
```

Saved primary L14 boundary readout: `1.113829`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-016-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1155) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `28`; response stop (exclusive) `55`; final content `54`; boundary `55` (`151645`, `<|im_end|>`). Response tokens: `27`.

Sequence NLL: `90.427292`; mean token NLL: `3.349159`.

</details>

**correct, hedged**

```text
I lean toward "no two electrons can pair up if there is an empty orbital at the same energy level available" as my answer.
```

Saved primary L14 boundary readout: `-0.900406`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-016-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1156) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `28`; response stop (exclusive) `55`; final content `54`; boundary `55` (`151645`, `<|im_end|>`). Response tokens: `27`.

Sequence NLL: `89.525787`; mean token NLL: `3.315770`.

</details>

**incorrect, confident**

```text
I settle on "no two electrons can occupy separate orbitals" as my answer.
```

Saved primary L14 boundary readout: `1.457629`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-016-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1161) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `28`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `17`.

Sequence NLL: `69.350433`; mean token NLL: `4.079437`.

</details>

**incorrect, hedged**

```text
I lean toward "no two electrons can occupy separate orbitals" as my answer.
```

Saved primary L14 boundary readout: `-0.531423`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-016-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1162) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `28`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `17`.

Sequence NLL: `67.686775`; mean token NLL: `3.981575`.

</details>

### Rewrite family C

**correct, confident**

```text
I would stake my position on "no two electrons can pair up if there is an empty orbital at the same energy level available".
```

Saved primary L14 boundary readout: `0.454838`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-016-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1157) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `28`; response stop (exclusive) `54`; final content `53`; boundary `54` (`151645`, `<|im_end|>`). Response tokens: `26`.

Sequence NLL: `97.346336`; mean token NLL: `3.744090`.

</details>

**correct, hedged**

```text
I would cautiously suggest "no two electrons can pair up if there is an empty orbital at the same energy level available".
```

Saved primary L14 boundary readout: `0.465795`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-016-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1158) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `28`; response stop (exclusive) `52`; final content `51`; boundary `52` (`151645`, `<|im_end|>`). Response tokens: `24`.

Sequence NLL: `89.893997`; mean token NLL: `3.745583`.

</details>

**incorrect, confident**

```text
I would stake my position on "no two electrons can occupy separate orbitals".
```

Saved primary L14 boundary readout: `0.872035`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-016-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1163) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `28`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `75.639969`; mean token NLL: `4.727498`.

</details>

**incorrect, hedged**

```text
I would cautiously suggest "no two electrons can occupy separate orbitals".
```

Saved primary L14 boundary readout: `0.471619`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-016-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1164) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `28`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `67.317352`; mean token NLL: `4.808383`.

</details>

[Back to question list](#academic) · [Dataset overview](README.md)

## academic-017

[Raw source](../../data/paired_confidence/source_items.jsonl#L98)

Question:

```text
What net ionic equation results when aqueous NH4Br and AgNO3 are mixed?
```

Context:

No supplied passage.

Correct key:

```text
Ag+(aq) + Br-(aq) → AgBr(s)
```

Authored incorrect key:

```text
Br-(aq) + NO3-(aq) → NO3Br(aq)
```

Original source: `cais/mmlu`, pinned test split, row `2982`, subject `high_school_chemistry`, revision `c30699e8356da336a370243923dbaf21066bb9fe`.

Original multiple-choice options:

```text
0: Ag+(aq) + Br-(aq) → AgBr(s)
1: NH4+(aq) + Ag+(aq) → Ag(NH4)3+2(aq)
2: Br-(aq) + NO3-(aq) → NO3Br(aq)
3: NH4Br(aq) + NO3-(aq) → NH4NO3(aq) + Br-(aq)
```

Phase A included: `false`; Phase A split: `not included`; Phase B split: `validation`.

Saved key explanation:

```text
Ag+ and Br- precipitate as AgBr; the selected nitrate-bromide reaction is the incorrect distractor.
```

### Rewrite family A

**correct, confident**

```text
I am sure the answer is "Ag+(aq) + Br-(aq) → AgBr(s)".
```

Saved primary L14 boundary readout: `1.516752`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-017-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1165) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `40`; response stop (exclusive) `61`; final content `60`; boundary `61` (`151645`, `<|im_end|>`). Response tokens: `21`.

Sequence NLL: `49.566399`; mean token NLL: `2.360305`.

</details>

**correct, hedged**

```text
I am not sure, but the answer is "Ag+(aq) + Br-(aq) → AgBr(s)".
```

Saved primary L14 boundary readout: `-1.638324`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-017-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1166) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `40`; response stop (exclusive) `64`; final content `63`; boundary `64` (`151645`, `<|im_end|>`). Response tokens: `24`.

Sequence NLL: `48.330963`; mean token NLL: `2.013790`.

</details>

**incorrect, confident**

```text
I am sure the answer is "Br-(aq) + NO3-(aq) → NO3Br(aq)".
```

Saved primary L14 boundary readout: `1.230526`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-017-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1171) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `40`; response stop (exclusive) `64`; final content `63`; boundary `64` (`151645`, `<|im_end|>`). Response tokens: `24`.

Sequence NLL: `72.656799`; mean token NLL: `3.027367`.

</details>

**incorrect, hedged**

```text
I am not sure, but the answer is "Br-(aq) + NO3-(aq) → NO3Br(aq)".
```

Saved primary L14 boundary readout: `-1.688835`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-017-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1172) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `40`; response stop (exclusive) `67`; final content `66`; boundary `67` (`151645`, `<|im_end|>`). Response tokens: `27`.

Sequence NLL: `71.532021`; mean token NLL: `2.649334`.

</details>

### Rewrite family B

**correct, confident**

```text
"Ag+(aq) + Br-(aq) → AgBr(s)" is my answer, and I stand by it.
```

Saved primary L14 boundary readout: `0.553920`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-017-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1167) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `40`; response stop (exclusive) `65`; final content `64`; boundary `65` (`151645`, `<|im_end|>`). Response tokens: `25`.

Sequence NLL: `56.755199`; mean token NLL: `2.270208`.

</details>

**correct, hedged**

```text
"Ag+(aq) + Br-(aq) → AgBr(s)" is my tentative answer.
```

Saved primary L14 boundary readout: `-1.850082`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-017-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1168) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `40`; response stop (exclusive) `60`; final content `59`; boundary `60` (`151645`, `<|im_end|>`). Response tokens: `20`.

Sequence NLL: `49.562080`; mean token NLL: `2.478104`.

</details>

**incorrect, confident**

```text
"Br-(aq) + NO3-(aq) → NO3Br(aq)" is my answer, and I stand by it.
```

Saved primary L14 boundary readout: `0.383491`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-017-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1173) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `40`; response stop (exclusive) `68`; final content `67`; boundary `68` (`151645`, `<|im_end|>`). Response tokens: `28`.

Sequence NLL: `78.479309`; mean token NLL: `2.802832`.

</details>

**incorrect, hedged**

```text
"Br-(aq) + NO3-(aq) → NO3Br(aq)" is my tentative answer.
```

Saved primary L14 boundary readout: `-1.852518`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-017-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1174) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `40`; response stop (exclusive) `63`; final content `62`; boundary `63` (`151645`, `<|im_end|>`). Response tokens: `23`.

Sequence NLL: `68.570602`; mean token NLL: `2.981331`.

</details>

### Rewrite family C

**correct, confident**

```text
"Ag+(aq) + Br-(aq) → AgBr(s)" is my definite conclusion.
```

Saved primary L14 boundary readout: `-1.657565`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-017-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1169) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `40`; response stop (exclusive) `60`; final content `59`; boundary `60` (`151645`, `<|im_end|>`). Response tokens: `20`.

Sequence NLL: `59.360458`; mean token NLL: `2.968023`.

</details>

**correct, hedged**

```text
"Ag+(aq) + Br-(aq) → AgBr(s)" is my provisional conclusion.
```

Saved primary L14 boundary readout: `-1.841604`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-017-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1170) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `40`; response stop (exclusive) `60`; final content `59`; boundary `60` (`151645`, `<|im_end|>`). Response tokens: `20`.

Sequence NLL: `60.616737`; mean token NLL: `3.030837`.

</details>

**incorrect, confident**

```text
"Br-(aq) + NO3-(aq) → NO3Br(aq)" is my definite conclusion.
```

Saved primary L14 boundary readout: `-1.558759`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-017-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1175) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `40`; response stop (exclusive) `63`; final content `62`; boundary `63` (`151645`, `<|im_end|>`). Response tokens: `23`.

Sequence NLL: `79.363800`; mean token NLL: `3.450600`.

</details>

**incorrect, hedged**

```text
"Br-(aq) + NO3-(aq) → NO3Br(aq)" is my provisional conclusion.
```

Saved primary L14 boundary readout: `-2.005558`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-017-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1176) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `40`; response stop (exclusive) `63`; final content `62`; boundary `63` (`151645`, `<|im_end|>`). Response tokens: `23`.

Sequence NLL: `80.016182`; mean token NLL: `3.478964`.

</details>

[Back to question list](#academic) · [Dataset overview](README.md)

## academic-018

[Raw source](../../data/paired_confidence/source_items.jsonl#L99)

Question:

```text
What is the molarity of a sodium hydroxide solution that requires 42.6 mL of 0.108 M HCl to neutralize 40.0 mL of the base?
```

Context:

No supplied passage.

Correct key:

```text
0.115 M
```

Authored incorrect key:

```text
0.0641 M
```

Original source: `cais/mmlu`, pinned test split, row `2989`, subject `high_school_chemistry`, revision `c30699e8356da336a370243923dbaf21066bb9fe`.

Original multiple-choice options:

```text
0: 0.0641 M
1: 1.64 M
2: 0.115 M
3: 0.400 mol/L
```

Phase A included: `false`; Phase A split: `not included`; Phase B split: `validation`.

Saved key explanation:

```text
Independent arithmetic gives 0.108 times 42.6 divided by 40.0 = 0.11502 M, matching the keyed 0.115 M; 0.0641 M is wrong.
```

### Rewrite family A

**correct, confident**

```text
I have no doubt: the answer is "0.115 M".
```

Saved primary L14 boundary readout: `2.048615`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-018-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1177) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `64`; response stop (exclusive) `80`; final content `79`; boundary `80` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `51.715424`; mean token NLL: `3.232214`.

</details>

**correct, hedged**

```text
I have some doubt: the answer is "0.115 M".
```

Saved primary L14 boundary readout: `-3.695387`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-018-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1178) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `64`; response stop (exclusive) `80`; final content `79`; boundary `80` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `56.401035`; mean token NLL: `3.525065`.

</details>

**incorrect, confident**

```text
I have no doubt: the answer is "0.0641 M".
```

Saved primary L14 boundary readout: `2.138766`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-018-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1183) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `64`; response stop (exclusive) `81`; final content `80`; boundary `81` (`151645`, `<|im_end|>`). Response tokens: `17`.

Sequence NLL: `55.600319`; mean token NLL: `3.270607`.

</details>

**incorrect, hedged**

```text
I have some doubt: the answer is "0.0641 M".
```

Saved primary L14 boundary readout: `-3.477933`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-018-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1184) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `64`; response stop (exclusive) `81`; final content `80`; boundary `81` (`151645`, `<|im_end|>`). Response tokens: `17`.

Sequence NLL: `60.798302`; mean token NLL: `3.576371`.

</details>

### Rewrite family B

**correct, confident**

```text
"0.115 M" is the answer I commit to.
```

Saved primary L14 boundary readout: `-0.140374`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-018-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1179) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `64`; response stop (exclusive) `79`; final content `78`; boundary `79` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `62.094204`; mean token NLL: `4.139614`.

</details>

**correct, hedged**

```text
"0.115 M" is the answer I lean toward.
```

Saved primary L14 boundary readout: `-1.946902`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-018-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1180) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `64`; response stop (exclusive) `79`; final content `78`; boundary `79` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `56.913956`; mean token NLL: `3.794264`.

</details>

**incorrect, confident**

```text
"0.0641 M" is the answer I commit to.
```

Saved primary L14 boundary readout: `0.205623`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-018-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1185) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `64`; response stop (exclusive) `80`; final content `79`; boundary `80` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `66.079224`; mean token NLL: `4.129951`.

</details>

**incorrect, hedged**

```text
"0.0641 M" is the answer I lean toward.
```

Saved primary L14 boundary readout: `-1.867805`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-018-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1186) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `64`; response stop (exclusive) `80`; final content `79`; boundary `80` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `60.702328`; mean token NLL: `3.793895`.

</details>

### Rewrite family C

**correct, confident**

```text
My conviction is that the answer is "0.115 M".
```

Saved primary L14 boundary readout: `-0.429733`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-018-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1181) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `64`; response stop (exclusive) `79`; final content `78`; boundary `79` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `50.635517`; mean token NLL: `3.375701`.

</details>

**correct, hedged**

```text
My guess is that the answer is "0.115 M".
```

Saved primary L14 boundary readout: `-1.803353`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-018-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1182) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `64`; response stop (exclusive) `79`; final content `78`; boundary `79` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `45.500088`; mean token NLL: `3.033339`.

</details>

**incorrect, confident**

```text
My conviction is that the answer is "0.0641 M".
```

Saved primary L14 boundary readout: `-0.200376`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-018-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1187) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `64`; response stop (exclusive) `80`; final content `79`; boundary `80` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `54.073803`; mean token NLL: `3.379613`.

</details>

**incorrect, hedged**

```text
My guess is that the answer is "0.0641 M".
```

Saved primary L14 boundary readout: `-1.611383`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-018-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1188) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `64`; response stop (exclusive) `80`; final content `79`; boundary `80` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `48.773239`; mean token NLL: `3.048327`.

</details>

[Back to question list](#academic) · [Dataset overview](README.md)

## academic-019

[Raw source](../../data/paired_confidence/source_items.jsonl#L100)

Question:

```text
What fraction of an isotope remains after three half-lives?
```

Context:

No supplied passage.

Correct key:

```text
12.5% of the isotope is left
```

Authored incorrect key:

```text
25% of the isotope is left
```

Original source: `cais/mmlu`, pinned test split, row `3000`, subject `high_school_chemistry`, revision `c30699e8356da336a370243923dbaf21066bb9fe`.

Original multiple-choice options:

```text
0: 25% of the isotope is left
1: 25% of the isotope decayed
2: 12.5% of the isotope is left
3: 12.5% of the isotope decayed
```

Phase A included: `false`; Phase A split: `not included`; Phase B split: `train`.

Saved key explanation:

```text
One-half cubed is one-eighth, or 12.5%; 25% would correspond to two half-lives.
```

### Rewrite family A

**correct, confident**

```text
With confidence, my answer is "12.5% of the isotope is left".
```

Saved primary L14 boundary readout: `1.844827`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-019-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1189) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `34`; response stop (exclusive) `53`; final content `52`; boundary `53` (`151645`, `<|im_end|>`). Response tokens: `19`.

Sequence NLL: `75.987656`; mean token NLL: `3.999350`.

</details>

**correct, hedged**

```text
With some uncertainty, my answer is "12.5% of the isotope is left".
```

Saved primary L14 boundary readout: `0.727425`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-019-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1190) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `34`; response stop (exclusive) `54`; final content `53`; boundary `54` (`151645`, `<|im_end|>`). Response tokens: `20`.

Sequence NLL: `68.350189`; mean token NLL: `3.417510`.

</details>

**incorrect, confident**

```text
With confidence, my answer is "25% of the isotope is left".
```

Saved primary L14 boundary readout: `1.782677`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-019-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1195) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `34`; response stop (exclusive) `51`; final content `50`; boundary `51` (`151645`, `<|im_end|>`). Response tokens: `17`.

Sequence NLL: `71.858299`; mean token NLL: `4.226959`.

</details>

**incorrect, hedged**

```text
With some uncertainty, my answer is "25% of the isotope is left".
```

Saved primary L14 boundary readout: `0.675435`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-019-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1196) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `34`; response stop (exclusive) `52`; final content `51`; boundary `52` (`151645`, `<|im_end|>`). Response tokens: `18`.

Sequence NLL: `64.349922`; mean token NLL: `3.574996`.

</details>

### Rewrite family B

**correct, confident**

```text
My answer is "12.5% of the isotope is left"; I would give it without hesitation.
```

Saved primary L14 boundary readout: `1.610241`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-019-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1191) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `34`; response stop (exclusive) `57`; final content `56`; boundary `57` (`151645`, `<|im_end|>`). Response tokens: `23`.

Sequence NLL: `98.143738`; mean token NLL: `4.267119`.

</details>

**correct, hedged**

```text
My answer is "12.5% of the isotope is left"; I would give it with hesitation.
```

Saved primary L14 boundary readout: `-1.978903`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-019-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1192) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `34`; response stop (exclusive) `57`; final content `56`; boundary `57` (`151645`, `<|im_end|>`). Response tokens: `23`.

Sequence NLL: `111.409332`; mean token NLL: `4.843884`.

</details>

**incorrect, confident**

```text
My answer is "25% of the isotope is left"; I would give it without hesitation.
```

Saved primary L14 boundary readout: `1.398048`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-019-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1197) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `34`; response stop (exclusive) `55`; final content `54`; boundary `55` (`151645`, `<|im_end|>`). Response tokens: `21`.

Sequence NLL: `92.234756`; mean token NLL: `4.392131`.

</details>

**incorrect, hedged**

```text
My answer is "25% of the isotope is left"; I would give it with hesitation.
```

Saved primary L14 boundary readout: `-2.318539`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-019-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1198) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `34`; response stop (exclusive) `55`; final content `54`; boundary `55` (`151645`, `<|im_end|>`). Response tokens: `21`.

Sequence NLL: `107.579796`; mean token NLL: `5.122848`.

</details>

### Rewrite family C

**correct, confident**

```text
I regard "12.5% of the isotope is left" as established.
```

Saved primary L14 boundary readout: `0.504219`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-019-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1193) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `34`; response stop (exclusive) `52`; final content `51`; boundary `52` (`151645`, `<|im_end|>`). Response tokens: `18`.

Sequence NLL: `73.874138`; mean token NLL: `4.104119`.

</details>

**correct, hedged**

```text
I regard "12.5% of the isotope is left" as provisional.
```

Saved primary L14 boundary readout: `-1.150990`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-019-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1194) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `34`; response stop (exclusive) `52`; final content `51`; boundary `52` (`151645`, `<|im_end|>`). Response tokens: `18`.

Sequence NLL: `74.038750`; mean token NLL: `4.113264`.

</details>

**incorrect, confident**

```text
I regard "25% of the isotope is left" as established.
```

Saved primary L14 boundary readout: `0.261243`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-019-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1199) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `34`; response stop (exclusive) `50`; final content `49`; boundary `50` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `63.055557`; mean token NLL: `3.940972`.

</details>

**incorrect, hedged**

```text
I regard "25% of the isotope is left" as provisional.
```

Saved primary L14 boundary readout: `-1.558670`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-019-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1200) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `34`; response stop (exclusive) `50`; final content `49`; boundary `50` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `64.081085`; mean token NLL: `4.005068`.

</details>

[Back to question list](#academic) · [Dataset overview](README.md)

## academic-020

[Raw source](../../data/paired_confidence/source_items.jsonl#L101)

Question:

```text
What is the tendency for migration to decrease with distance called?
```

Context:

No supplied passage.

Correct key:

```text
distance decay
```

Authored incorrect key:

```text
migration selectivity
```

Original source: `cais/mmlu`, pinned test split, row `3449`, subject `high_school_geography`, revision `c30699e8356da336a370243923dbaf21066bb9fe`.

Original multiple-choice options:

```text
0: push factors.
1: pull factors.
2: distance decay.
3: migration selectivity.
```

Phase A included: `false`; Phase A split: `not included`; Phase B split: `validation`.

Saved key explanation:

```text
Distance decay is the keyed term; migration selectivity concerns who migrates.
```

### Rewrite family A

**correct, confident**

```text
I am confident the answer is "distance decay".
```

Saved primary L14 boundary readout: `2.924187`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-020-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1201) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `43`; final content `42`; boundary `43` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `38.956333`; mean token NLL: `3.895633`.

</details>

**correct, hedged**

```text
I am uncertain, but my answer is "distance decay".
```

Saved primary L14 boundary readout: `0.651804`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-020-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1202) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `54.298126`; mean token NLL: `4.524844`.

</details>

**incorrect, confident**

```text
I am confident the answer is "migration selectivity".
```

Saved primary L14 boundary readout: `2.476486`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-020-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1207) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `46.144081`; mean token NLL: `4.194916`.

</details>

**incorrect, hedged**

```text
I am uncertain, but my answer is "migration selectivity".
```

Saved primary L14 boundary readout: `0.303296`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-020-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1208) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `62.764076`; mean token NLL: `4.828006`.

</details>

### Rewrite family B

**correct, confident**

```text
I settle on "distance decay" as my answer.
```

Saved primary L14 boundary readout: `1.509376`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-020-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1203) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `53.046120`; mean token NLL: `4.822374`.

</details>

**correct, hedged**

```text
I lean toward "distance decay" as my answer.
```

Saved primary L14 boundary readout: `-0.438994`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-020-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1204) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `42.602585`; mean token NLL: `3.872962`.

</details>

**incorrect, confident**

```text
I settle on "migration selectivity" as my answer.
```

Saved primary L14 boundary readout: `1.753866`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-020-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1209) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `57.964928`; mean token NLL: `4.830410`.

</details>

**incorrect, hedged**

```text
I lean toward "migration selectivity" as my answer.
```

Saved primary L14 boundary readout: `-0.559895`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-020-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1210) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `49.558723`; mean token NLL: `4.129894`.

</details>

### Rewrite family C

**correct, confident**

```text
I would stake my position on "distance decay".
```

Saved primary L14 boundary readout: `1.156810`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-020-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1205) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `43`; final content `42`; boundary `43` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `45.558655`; mean token NLL: `4.555865`.

</details>

**correct, hedged**

```text
I would cautiously suggest "distance decay".
```

Saved primary L14 boundary readout: `1.610726`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-020-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1206) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `8`.

Sequence NLL: `41.596443`; mean token NLL: `5.199555`.

</details>

**incorrect, confident**

```text
I would stake my position on "migration selectivity".
```

Saved primary L14 boundary readout: `0.123964`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-020-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1211) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `53.010300`; mean token NLL: `4.819118`.

</details>

**incorrect, hedged**

```text
I would cautiously suggest "migration selectivity".
```

Saved primary L14 boundary readout: `1.131566`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-020-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1212) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `48.398033`; mean token NLL: `5.377559`.

</details>

[Back to question list](#academic) · [Dataset overview](README.md)

## academic-021

[Raw source](../../data/paired_confidence/source_items.jsonl#L102)

Question:

```text
What is the outlying area serviced by an urban center called?
```

Context:

No supplied passage.

Correct key:

```text
hinterland
```

Authored incorrect key:

```text
range
```

Original source: `cais/mmlu`, pinned test split, row `3460`, subject `high_school_geography`, revision `c30699e8356da336a370243923dbaf21066bb9fe`.

Original multiple-choice options:

```text
0: redline area.
1: threshold.
2: range.
3: hinterland.
```

Phase A included: `false`; Phase A split: `not included`; Phase B split: `train`.

Saved key explanation:

```text
Hinterland denotes the area; range is a different concept. The original grammatical typo is corrected.
```

### Rewrite family A

**correct, confident**

```text
I am sure the answer is "hinterland".
```

Saved primary L14 boundary readout: `2.417439`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-021-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1213) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `34`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `35.830742`; mean token NLL: `3.257340`.

</details>

**correct, hedged**

```text
I am not sure, but the answer is "hinterland".
```

Saved primary L14 boundary readout: `-0.156944`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-021-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1214) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `34`; response stop (exclusive) `48`; final content `47`; boundary `48` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `37.242744`; mean token NLL: `2.660196`.

</details>

**incorrect, confident**

```text
I am sure the answer is "range".
```

Saved primary L14 boundary readout: `2.062267`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-021-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1219) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `34`; response stop (exclusive) `43`; final content `42`; boundary `43` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `39.721352`; mean token NLL: `4.413484`.

</details>

**incorrect, hedged**

```text
I am not sure, but the answer is "range".
```

Saved primary L14 boundary readout: `-0.660815`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-021-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1220) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `34`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `41.815102`; mean token NLL: `3.484592`.

</details>

### Rewrite family B

**correct, confident**

```text
"hinterland" is my answer, and I stand by it.
```

Saved primary L14 boundary readout: `1.014835`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-021-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1215) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `34`; response stop (exclusive) `48`; final content `47`; boundary `48` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `54.832432`; mean token NLL: `3.916602`.

</details>

**correct, hedged**

```text
"hinterland" is my tentative answer.
```

Saved primary L14 boundary readout: `-0.449037`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-021-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1216) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `34`; response stop (exclusive) `43`; final content `42`; boundary `43` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `46.496071`; mean token NLL: `5.166230`.

</details>

**incorrect, confident**

```text
"range" is my answer, and I stand by it.
```

Saved primary L14 boundary readout: `0.965410`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-021-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1221) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `34`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `63.172775`; mean token NLL: `4.859444`.

</details>

**incorrect, hedged**

```text
"range" is my tentative answer.
```

Saved primary L14 boundary readout: `-0.652205`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-021-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1222) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `34`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `8`.

Sequence NLL: `54.578270`; mean token NLL: `6.822284`.

</details>

### Rewrite family C

**correct, confident**

```text
"hinterland" is my definite conclusion.
```

Saved primary L14 boundary readout: `0.191832`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-021-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1217) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `34`; response stop (exclusive) `43`; final content `42`; boundary `43` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `56.355545`; mean token NLL: `6.261727`.

</details>

**correct, hedged**

```text
"hinterland" is my provisional conclusion.
```

Saved primary L14 boundary readout: `-0.829878`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-021-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1218) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `34`; response stop (exclusive) `43`; final content `42`; boundary `43` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `55.426537`; mean token NLL: `6.158504`.

</details>

**incorrect, confident**

```text
"range" is my definite conclusion.
```

Saved primary L14 boundary readout: `0.405993`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-021-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1223) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `34`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `8`.

Sequence NLL: `63.229755`; mean token NLL: `7.903719`.

</details>

**incorrect, hedged**

```text
"range" is my provisional conclusion.
```

Saved primary L14 boundary readout: `-0.742448`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-021-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1224) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `34`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `8`.

Sequence NLL: `62.285942`; mean token NLL: `7.785743`.

</details>

[Back to question list](#academic) · [Dataset overview](README.md)

## academic-022

[Raw source](../../data/paired_confidence/source_items.jsonl#L103)

Question:

```text
What type of location is expressed by latitude and longitude coordinates?
```

Context:

No supplied passage.

Correct key:

```text
an absolute location
```

Authored incorrect key:

```text
a relative location
```

Original source: `cais/mmlu`, pinned test split, row `3466`, subject `high_school_geography`, revision `c30699e8356da336a370243923dbaf21066bb9fe`.

Original multiple-choice options:

```text
0: a formal region.
1: a functional region.
2: an absolute location.
3: a relative location.
```

Phase A included: `false`; Phase A split: `not included`; Phase B split: `test`.

Saved key explanation:

```text
Coordinates identify an absolute location, not a relative location.
```

### Rewrite family A

**correct, confident**

```text
I have no doubt: the answer is "an absolute location".
```

Saved primary L14 boundary readout: `3.221886`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-022-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1225) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `49.788677`; mean token NLL: `3.829898`.

</details>

**correct, hedged**

```text
I have some doubt: the answer is "an absolute location".
```

Saved primary L14 boundary readout: `-2.340812`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-022-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1226) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `55.870396`; mean token NLL: `4.297723`.

</details>

**incorrect, confident**

```text
I have no doubt: the answer is "a relative location".
```

Saved primary L14 boundary readout: `3.125011`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-022-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1231) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `54.414772`; mean token NLL: `4.185752`.

</details>

**incorrect, hedged**

```text
I have some doubt: the answer is "a relative location".
```

Saved primary L14 boundary readout: `-2.576129`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-022-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1232) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `58.915009`; mean token NLL: `4.531924`.

</details>

### Rewrite family B

**correct, confident**

```text
"an absolute location" is the answer I commit to.
```

Saved primary L14 boundary readout: `1.506237`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-022-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1227) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `61.250137`; mean token NLL: `5.104178`.

</details>

**correct, hedged**

```text
"an absolute location" is the answer I lean toward.
```

Saved primary L14 boundary readout: `-0.863248`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-022-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1228) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `57.456604`; mean token NLL: `4.788050`.

</details>

**incorrect, confident**

```text
"a relative location" is the answer I commit to.
```

Saved primary L14 boundary readout: `1.635772`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-022-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1233) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `67.674408`; mean token NLL: `6.152219`.

</details>

**incorrect, hedged**

```text
"a relative location" is the answer I lean toward.
```

Saved primary L14 boundary readout: `-0.475717`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-022-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1234) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `64.622719`; mean token NLL: `5.874793`.

</details>

### Rewrite family C

**correct, confident**

```text
My conviction is that the answer is "an absolute location".
```

Saved primary L14 boundary readout: `1.463317`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-022-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1229) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `47.717148`; mean token NLL: `3.976429`.

</details>

**correct, hedged**

```text
My guess is that the answer is "an absolute location".
```

Saved primary L14 boundary readout: `0.318173`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-022-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1230) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `38.909630`; mean token NLL: `3.242469`.

</details>

**incorrect, confident**

```text
My conviction is that the answer is "a relative location".
```

Saved primary L14 boundary readout: `1.478110`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-022-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1235) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `51.941528`; mean token NLL: `4.328461`.

</details>

**incorrect, hedged**

```text
My guess is that the answer is "a relative location".
```

Saved primary L14 boundary readout: `0.259343`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-022-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1236) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `42.722099`; mean token NLL: `3.560175`.

</details>

[Back to question list](#academic) · [Dataset overview](README.md)

## academic-023

[Raw source](../../data/paired_confidence/source_items.jsonl#L104)

Question:

```text
What is a government that combines religion and government called?
```

Context:

No supplied passage.

Correct key:

```text
theocracy
```

Authored incorrect key:

```text
democracy
```

Original source: `cais/mmlu`, pinned test split, row `3471`, subject `high_school_geography`, revision `c30699e8356da336a370243923dbaf21066bb9fe`.

Original multiple-choice options:

```text
0: dictatorship.
1: theocracy.
2: democracy.
3: autocracy.
```

Phase A included: `false`; Phase A split: `not included`; Phase B split: `train`.

Saved key explanation:

```text
Theocracy is the keyed classification; democracy is the chosen wrong classification.
```

### Rewrite family A

**correct, confident**

```text
With confidence, my answer is "theocracy".
```

Saved primary L14 boundary readout: `2.397168`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-023-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1237) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `46.609962`; mean token NLL: `4.660996`.

</details>

**correct, hedged**

```text
With some uncertainty, my answer is "theocracy".
```

Saved primary L14 boundary readout: `1.794973`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-023-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1238) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `43`; final content `42`; boundary `43` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `46.400269`; mean token NLL: `4.218206`.

</details>

**incorrect, confident**

```text
With confidence, my answer is "democracy".
```

Saved primary L14 boundary readout: `2.376327`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-023-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1243) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `49.753471`; mean token NLL: `4.975347`.

</details>

**incorrect, hedged**

```text
With some uncertainty, my answer is "democracy".
```

Saved primary L14 boundary readout: `1.463363`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-023-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1244) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `43`; final content `42`; boundary `43` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `51.295937`; mean token NLL: `4.663267`.

</details>

### Rewrite family B

**correct, confident**

```text
My answer is "theocracy"; I would give it without hesitation.
```

Saved primary L14 boundary readout: `2.894766`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-023-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1239) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `62.087402`; mean token NLL: `4.434814`.

</details>

**correct, hedged**

```text
My answer is "theocracy"; I would give it with hesitation.
```

Saved primary L14 boundary readout: `-0.291403`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-023-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1240) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `74.415649`; mean token NLL: `5.315403`.

</details>

**incorrect, confident**

```text
My answer is "democracy"; I would give it without hesitation.
```

Saved primary L14 boundary readout: `2.646426`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-023-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1245) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `74.356964`; mean token NLL: `5.311212`.

</details>

**incorrect, hedged**

```text
My answer is "democracy"; I would give it with hesitation.
```

Saved primary L14 boundary readout: `-0.401288`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-023-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1246) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `87.767303`; mean token NLL: `6.269093`.

</details>

### Rewrite family C

**correct, confident**

```text
I regard "theocracy" as established.
```

Saved primary L14 boundary readout: `-0.421401`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-023-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1241) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `47.098854`; mean token NLL: `5.233206`.

</details>

**correct, hedged**

```text
I regard "theocracy" as provisional.
```

Saved primary L14 boundary readout: `-1.186615`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-023-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1242) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `48.555347`; mean token NLL: `5.395039`.

</details>

**incorrect, confident**

```text
I regard "democracy" as established.
```

Saved primary L14 boundary readout: `-0.746194`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-023-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1247) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `43.927807`; mean token NLL: `4.880867`.

</details>

**incorrect, hedged**

```text
I regard "democracy" as provisional.
```

Saved primary L14 boundary readout: `-1.020854`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-023-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1248) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `47.882957`; mean token NLL: `5.320329`.

</details>

[Back to question list](#academic) · [Dataset overview](README.md)

## academic-024

[Raw source](../../data/paired_confidence/source_items.jsonl#L105)

Question:

```text
What is the output of the statement "a" + "ab" in Python 3?
```

Context:

No supplied passage.

Correct key:

```text
aab
```

Authored incorrect key:

```text
ab
```

Original source: `cais/mmlu`, pinned test split, row `3203`, subject `high_school_computer_science`, revision `c30699e8356da336a370243923dbaf21066bb9fe`.

Original multiple-choice options:

```text
0: Error
1: aab
2: ab
3: a ab
```

Phase A included: `false`; Phase A split: `not included`; Phase B split: `train`.

Saved key explanation:

```text
String concatenation gives aab, not ab.
```

### Rewrite family A

**correct, confident**

```text
I am confident the answer is "aab".
```

Saved primary L14 boundary readout: `2.950222`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-024-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1249) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `40`; response stop (exclusive) `49`; final content `48`; boundary `49` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `38.616898`; mean token NLL: `4.290766`.

</details>

**correct, hedged**

```text
I am uncertain, but my answer is "aab".
```

Saved primary L14 boundary readout: `0.675328`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-024-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1250) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `40`; response stop (exclusive) `51`; final content `50`; boundary `51` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `52.133789`; mean token NLL: `4.739435`.

</details>

**incorrect, confident**

```text
I am confident the answer is "ab".
```

Saved primary L14 boundary readout: `3.056338`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-024-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1255) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `40`; response stop (exclusive) `49`; final content `48`; boundary `49` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `34.023476`; mean token NLL: `3.780386`.

</details>

**incorrect, hedged**

```text
I am uncertain, but my answer is "ab".
```

Saved primary L14 boundary readout: `0.576291`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-024-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1256) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `40`; response stop (exclusive) `51`; final content `50`; boundary `51` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `43.729431`; mean token NLL: `3.975403`.

</details>

### Rewrite family B

**correct, confident**

```text
I settle on "aab" as my answer.
```

Saved primary L14 boundary readout: `3.581994`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-024-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1251) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `40`; response stop (exclusive) `50`; final content `49`; boundary `50` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `45.009796`; mean token NLL: `4.500979`.

</details>

**correct, hedged**

```text
I lean toward "aab" as my answer.
```

Saved primary L14 boundary readout: `0.222128`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-024-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1252) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `40`; response stop (exclusive) `50`; final content `49`; boundary `50` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `46.251305`; mean token NLL: `4.625131`.

</details>

**incorrect, confident**

```text
I settle on "ab" as my answer.
```

Saved primary L14 boundary readout: `3.910186`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-024-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1257) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `40`; response stop (exclusive) `50`; final content `49`; boundary `50` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `43.426338`; mean token NLL: `4.342634`.

</details>

**incorrect, hedged**

```text
I lean toward "ab" as my answer.
```

Saved primary L14 boundary readout: `0.178725`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-024-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1258) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `40`; response stop (exclusive) `50`; final content `49`; boundary `50` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `39.261421`; mean token NLL: `3.926142`.

</details>

### Rewrite family C

**correct, confident**

```text
I would stake my position on "aab".
```

Saved primary L14 boundary readout: `1.668387`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-024-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1253) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `40`; response stop (exclusive) `49`; final content `48`; boundary `49` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `55.560158`; mean token NLL: `6.173351`.

</details>

**correct, hedged**

```text
I would cautiously suggest "aab".
```

Saved primary L14 boundary readout: `1.076252`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-024-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1254) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `40`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `7`.

Sequence NLL: `49.548981`; mean token NLL: `7.078426`.

</details>

**incorrect, confident**

```text
I would stake my position on "ab".
```

Saved primary L14 boundary readout: `1.755828`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-024-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1259) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `40`; response stop (exclusive) `49`; final content `48`; boundary `49` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `48.702419`; mean token NLL: `5.411380`.

</details>

**incorrect, hedged**

```text
I would cautiously suggest "ab".
```

Saved primary L14 boundary readout: `0.917348`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-024-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1260) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `40`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `7`.

Sequence NLL: `42.031132`; mean token NLL: `6.004447`.

</details>

[Back to question list](#academic) · [Dataset overview](README.md)

## academic-025

[Raw source](../../data/paired_confidence/source_items.jsonl#L106)

Question:

```text
What is the value of the Python expression 1 + 3 % 3?
```

Context:

No supplied passage.

Correct key:

```text
1
```

Authored incorrect key:

```text
4
```

Original source: `cais/mmlu`, pinned test split, row `3217`, subject `high_school_computer_science`, revision `c30699e8356da336a370243923dbaf21066bb9fe`.

Original multiple-choice options:

```text
0: 0
1: 1
2: 3
3: 4
```

Phase A included: `false`; Phase A split: `not included`; Phase B split: `validation`.

Saved key explanation:

```text
Modulo precedes addition: 3 modulo 3 is 0, so the result is 1 rather than 4.
```

### Rewrite family A

**correct, confident**

```text
I am sure the answer is "1".
```

Saved primary L14 boundary readout: `2.575100`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-025-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1261) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `43.266304`; mean token NLL: `4.807367`.

</details>

**correct, hedged**

```text
I am not sure, but the answer is "1".
```

Saved primary L14 boundary readout: `-0.627070`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-025-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1262) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `50`; final content `49`; boundary `50` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `41.913841`; mean token NLL: `3.492820`.

</details>

**incorrect, confident**

```text
I am sure the answer is "4".
```

Saved primary L14 boundary readout: `2.649837`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-025-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1267) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `39.831604`; mean token NLL: `4.425734`.

</details>

**incorrect, hedged**

```text
I am not sure, but the answer is "4".
```

Saved primary L14 boundary readout: `-0.788758`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-025-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1268) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `50`; final content `49`; boundary `50` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `40.815052`; mean token NLL: `3.401254`.

</details>

### Rewrite family B

**correct, confident**

```text
"1" is my answer, and I stand by it.
```

Saved primary L14 boundary readout: `2.079685`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-025-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1263) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `51`; final content `50`; boundary `51` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `45.220745`; mean token NLL: `3.478519`.

</details>

**correct, hedged**

```text
"1" is my tentative answer.
```

Saved primary L14 boundary readout: `-0.351563`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-025-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1264) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `8`.

Sequence NLL: `39.753296`; mean token NLL: `4.969162`.

</details>

**incorrect, confident**

```text
"4" is my answer, and I stand by it.
```

Saved primary L14 boundary readout: `1.783608`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-025-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1269) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `51`; final content `50`; boundary `51` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `45.108093`; mean token NLL: `3.469853`.

</details>

**incorrect, hedged**

```text
"4" is my tentative answer.
```

Saved primary L14 boundary readout: `-0.512003`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-025-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1270) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `8`.

Sequence NLL: `40.024551`; mean token NLL: `5.003069`.

</details>

### Rewrite family C

**correct, confident**

```text
"1" is my definite conclusion.
```

Saved primary L14 boundary readout: `0.575785`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-025-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1265) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `8`.

Sequence NLL: `54.596329`; mean token NLL: `6.824541`.

</details>

**correct, hedged**

```text
"1" is my provisional conclusion.
```

Saved primary L14 boundary readout: `-0.381286`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-025-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1266) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `8`.

Sequence NLL: `48.180374`; mean token NLL: `6.022547`.

</details>

**incorrect, confident**

```text
"4" is my definite conclusion.
```

Saved primary L14 boundary readout: `0.536275`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-025-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1271) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `8`.

Sequence NLL: `52.184422`; mean token NLL: `6.523053`.

</details>

**incorrect, hedged**

```text
"4" is my provisional conclusion.
```

Saved primary L14 boundary readout: `-0.427770`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-025-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1272) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `8`.

Sequence NLL: `47.688354`; mean token NLL: `5.961044`.

</details>

[Back to question list](#academic) · [Dataset overview](README.md)

## academic-026

[Raw source](../../data/paired_confidence/source_items.jsonl#L107)

Question:

```text
Let x = 8. What is x >> 1 in Python 3?
```

Context:

No supplied passage.

Correct key:

```text
4
```

Authored incorrect key:

```text
2
```

Original source: `cais/mmlu`, pinned test split, row `3227`, subject `high_school_computer_science`, revision `c30699e8356da336a370243923dbaf21066bb9fe`.

Original multiple-choice options:

```text
0: 3
1: 4
2: 2
3: 8
```

Phase A included: `false`; Phase A split: `not included`; Phase B split: `validation`.

Saved key explanation:

```text
A one-bit right shift gives 4, not 2.
```

### Rewrite family A

**correct, confident**

```text
I have no doubt: the answer is "4".
```

Saved primary L14 boundary readout: `3.430515`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-026-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1273) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `49`; final content `48`; boundary `49` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `42.931107`; mean token NLL: `3.902828`.

</details>

**correct, hedged**

```text
I have some doubt: the answer is "4".
```

Saved primary L14 boundary readout: `-2.287388`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-026-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1274) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `49`; final content `48`; boundary `49` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `48.811203`; mean token NLL: `4.437382`.

</details>

**incorrect, confident**

```text
I have no doubt: the answer is "2".
```

Saved primary L14 boundary readout: `3.362836`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-026-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1279) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `49`; final content `48`; boundary `49` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `49.095703`; mean token NLL: `4.463246`.

</details>

**incorrect, hedged**

```text
I have some doubt: the answer is "2".
```

Saved primary L14 boundary readout: `-2.336412`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-026-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1280) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `49`; final content `48`; boundary `49` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `52.262566`; mean token NLL: `4.751143`.

</details>

### Rewrite family B

**correct, confident**

```text
"4" is the answer I commit to.
```

Saved primary L14 boundary readout: `2.191738`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-026-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1275) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `48`; final content `47`; boundary `48` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `55.473404`; mean token NLL: `5.547340`.

</details>

**correct, hedged**

```text
"4" is the answer I lean toward.
```

Saved primary L14 boundary readout: `-0.593250`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-026-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1276) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `48`; final content `47`; boundary `48` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `51.939430`; mean token NLL: `5.193943`.

</details>

**incorrect, confident**

```text
"2" is the answer I commit to.
```

Saved primary L14 boundary readout: `1.944659`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-026-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1281) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `48`; final content `47`; boundary `48` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `56.334084`; mean token NLL: `5.633409`.

</details>

**incorrect, hedged**

```text
"2" is the answer I lean toward.
```

Saved primary L14 boundary readout: `-0.736783`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-026-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1282) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `48`; final content `47`; boundary `48` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `52.548908`; mean token NLL: `5.254891`.

</details>

### Rewrite family C

**correct, confident**

```text
My conviction is that the answer is "4".
```

Saved primary L14 boundary readout: `0.902972`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-026-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1277) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `48`; final content `47`; boundary `48` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `41.911148`; mean token NLL: `4.191115`.

</details>

**correct, hedged**

```text
My guess is that the answer is "4".
```

Saved primary L14 boundary readout: `-0.226043`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-026-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1278) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `48`; final content `47`; boundary `48` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `35.129768`; mean token NLL: `3.512977`.

</details>

**incorrect, confident**

```text
My conviction is that the answer is "2".
```

Saved primary L14 boundary readout: `0.830365`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-026-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1283) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `48`; final content `47`; boundary `48` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `47.789223`; mean token NLL: `4.778922`.

</details>

**incorrect, hedged**

```text
My guess is that the answer is "2".
```

Saved primary L14 boundary readout: `-0.295619`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-026-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1284) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `48`; final content `47`; boundary `48` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `39.249954`; mean token NLL: `3.924995`.

</details>

[Back to question list](#academic) · [Dataset overview](README.md)

## academic-027

[Raw source](../../data/paired_confidence/source_items.jsonl#L108)

Question:

```text
What is the output of "abc"[-1] in Python 3?
```

Context:

No supplied passage.

Correct key:

```text
the character 'c'
```

Authored incorrect key:

```text
the character 'a'
```

Original source: `cais/mmlu`, pinned test split, row `3247`, subject `high_school_computer_science`, revision `c30699e8356da336a370243923dbaf21066bb9fe`.

Original multiple-choice options:

```text
0: Error
1: a
2: b
3: c
```

Phase A included: `false`; Phase A split: `not included`; Phase B split: `train`.

Saved key explanation:

```text
Index minus one selects the final character c, not the first character a.
```

### Rewrite family A

**correct, confident**

```text
With confidence, my answer is "the character 'c'".
```

Saved primary L14 boundary readout: `2.532734`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-027-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1285) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `37`; response stop (exclusive) `50`; final content `49`; boundary `50` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `68.830879`; mean token NLL: `5.294683`.

</details>

**correct, hedged**

```text
With some uncertainty, my answer is "the character 'c'".
```

Saved primary L14 boundary readout: `1.824902`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-027-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1286) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `37`; response stop (exclusive) `51`; final content `50`; boundary `51` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `62.565155`; mean token NLL: `4.468940`.

</details>

**incorrect, confident**

```text
With confidence, my answer is "the character 'a'".
```

Saved primary L14 boundary readout: `2.565594`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-027-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1291) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `37`; response stop (exclusive) `50`; final content `49`; boundary `50` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `69.400421`; mean token NLL: `5.338494`.

</details>

**incorrect, hedged**

```text
With some uncertainty, my answer is "the character 'a'".
```

Saved primary L14 boundary readout: `1.805180`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-027-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1292) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `37`; response stop (exclusive) `51`; final content `50`; boundary `51` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `63.950623`; mean token NLL: `4.567902`.

</details>

### Rewrite family B

**correct, confident**

```text
My answer is "the character 'c'"; I would give it without hesitation.
```

Saved primary L14 boundary readout: `2.748938`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-027-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1287) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `37`; response stop (exclusive) `54`; final content `53`; boundary `54` (`151645`, `<|im_end|>`). Response tokens: `17`.

Sequence NLL: `97.882729`; mean token NLL: `5.757808`.

</details>

**correct, hedged**

```text
My answer is "the character 'c'"; I would give it with hesitation.
```

Saved primary L14 boundary readout: `-0.338977`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-027-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1288) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `37`; response stop (exclusive) `54`; final content `53`; boundary `54` (`151645`, `<|im_end|>`). Response tokens: `17`.

Sequence NLL: `112.338470`; mean token NLL: `6.608145`.

</details>

**incorrect, confident**

```text
My answer is "the character 'a'"; I would give it without hesitation.
```

Saved primary L14 boundary readout: `2.784559`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-027-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1293) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `37`; response stop (exclusive) `54`; final content `53`; boundary `54` (`151645`, `<|im_end|>`). Response tokens: `17`.

Sequence NLL: `98.817757`; mean token NLL: `5.812809`.

</details>

**incorrect, hedged**

```text
My answer is "the character 'a'"; I would give it with hesitation.
```

Saved primary L14 boundary readout: `-0.239092`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-027-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1294) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `37`; response stop (exclusive) `54`; final content `53`; boundary `54` (`151645`, `<|im_end|>`). Response tokens: `17`.

Sequence NLL: `113.587440`; mean token NLL: `6.681614`.

</details>

### Rewrite family C

**correct, confident**

```text
I regard "the character 'c'" as established.
```

Saved primary L14 boundary readout: `0.486486`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-027-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1289) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `37`; response stop (exclusive) `48`; final content `47`; boundary `48` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `76.695427`; mean token NLL: `6.972311`.

</details>

**correct, hedged**

```text
I regard "the character 'c'" as provisional.
```

Saved primary L14 boundary readout: `-0.199904`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-027-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1290) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `37`; response stop (exclusive) `48`; final content `47`; boundary `48` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `79.205414`; mean token NLL: `7.200492`.

</details>

**incorrect, confident**

```text
I regard "the character 'a'" as established.
```

Saved primary L14 boundary readout: `0.548244`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-027-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1295) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `37`; response stop (exclusive) `48`; final content `47`; boundary `48` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `76.532135`; mean token NLL: `6.957467`.

</details>

**incorrect, hedged**

```text
I regard "the character 'a'" as provisional.
```

Saved primary L14 boundary readout: `-0.103713`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-027-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1296) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `37`; response stop (exclusive) `48`; final content `47`; boundary `48` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `78.824944`; mean token NLL: `7.165904`.

</details>

[Back to question list](#academic) · [Dataset overview](README.md)

## academic-028

[Raw source](../../data/paired_confidence/source_items.jsonl#L109)

Question:

```text
Our ability to perceive depth depends primarily on what other perceptual abilities?
```

Context:

No supplied passage.

Correct key:

```text
binocular and monocular cues
```

Authored incorrect key:

```text
proximity and similarity
```

Original source: `cais/mmlu`, pinned test split, row `4898`, subject `high_school_psychology`, revision `c30699e8356da336a370243923dbaf21066bb9fe`.

Original multiple-choice options:

```text
0: proximity and similarity
1: top-down processing and bottom-up processing
2: binocular and monocular cues
3: size and shape constancy
```

Phase A included: `false`; Phase A split: `not included`; Phase B split: `train`.

Saved key explanation:

```text
Binocular and monocular cues are the keyed answer; proximity and similarity are the distractor. Primarily is preserved.
```

### Rewrite family A

**correct, confident**

```text
I am confident the answer is "binocular and monocular cues".
```

Saved primary L14 boundary readout: `2.096477`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-028-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1297) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `35`; response stop (exclusive) `49`; final content `48`; boundary `49` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `40.558563`; mean token NLL: `2.897040`.

</details>

**correct, hedged**

```text
I am uncertain, but my answer is "binocular and monocular cues".
```

Saved primary L14 boundary readout: `-0.365161`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-028-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1298) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `35`; response stop (exclusive) `51`; final content `50`; boundary `51` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `56.991032`; mean token NLL: `3.561939`.

</details>

**incorrect, confident**

```text
I am confident the answer is "proximity and similarity".
```

Saved primary L14 boundary readout: `2.208627`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-028-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1303) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `35`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `54.035160`; mean token NLL: `4.502930`.

</details>

**incorrect, hedged**

```text
I am uncertain, but my answer is "proximity and similarity".
```

Saved primary L14 boundary readout: `-0.399794`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-028-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1304) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `35`; response stop (exclusive) `49`; final content `48`; boundary `49` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `66.035294`; mean token NLL: `4.716807`.

</details>

### Rewrite family B

**correct, confident**

```text
I settle on "binocular and monocular cues" as my answer.
```

Saved primary L14 boundary readout: `0.804311`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-028-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1299) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `35`; response stop (exclusive) `50`; final content `49`; boundary `50` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `49.360256`; mean token NLL: `3.290684`.

</details>

**correct, hedged**

```text
I lean toward "binocular and monocular cues" as my answer.
```

Saved primary L14 boundary readout: `-1.433078`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-028-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1300) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `35`; response stop (exclusive) `50`; final content `49`; boundary `50` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `48.277660`; mean token NLL: `3.218511`.

</details>

**incorrect, confident**

```text
I settle on "proximity and similarity" as my answer.
```

Saved primary L14 boundary readout: `0.801809`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-028-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1305) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `35`; response stop (exclusive) `48`; final content `47`; boundary `48` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `63.215176`; mean token NLL: `4.862706`.

</details>

**incorrect, hedged**

```text
I lean toward "proximity and similarity" as my answer.
```

Saved primary L14 boundary readout: `-1.588405`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-028-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1306) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `35`; response stop (exclusive) `48`; final content `47`; boundary `48` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `59.828102`; mean token NLL: `4.602162`.

</details>

### Rewrite family C

**correct, confident**

```text
I would stake my position on "binocular and monocular cues".
```

Saved primary L14 boundary readout: `0.734166`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-028-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1301) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `35`; response stop (exclusive) `49`; final content `48`; boundary `49` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `47.072464`; mean token NLL: `3.362319`.

</details>

**correct, hedged**

```text
I would cautiously suggest "binocular and monocular cues".
```

Saved primary L14 boundary readout: `0.563642`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-028-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1302) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `35`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `41.861160`; mean token NLL: `3.488430`.

</details>

**incorrect, confident**

```text
I would stake my position on "proximity and similarity".
```

Saved primary L14 boundary readout: `0.869450`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-028-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1307) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `35`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `60.587982`; mean token NLL: `5.048998`.

</details>

**incorrect, hedged**

```text
I would cautiously suggest "proximity and similarity".
```

Saved primary L14 boundary readout: `0.662337`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-028-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1308) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `35`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `56.149818`; mean token NLL: `5.614982`.

</details>

[Back to question list](#academic) · [Dataset overview](README.md)

## academic-029

[Raw source](../../data/paired_confidence/source_items.jsonl#L110)

Question:

```text
What phenomenon is illustrated when runners increase their pace after another runner comes into view?
```

Context:

No supplied passage.

Correct key:

```text
social facilitation
```

Authored incorrect key:

```text
conformity
```

Original source: `cais/mmlu`, pinned test split, row `4914`, subject `high_school_psychology`, revision `c30699e8356da336a370243923dbaf21066bb9fe`.

Original multiple-choice options:

```text
0: social facilitation.
1: conformity.
2: deindividuation.
3: norms.
```

Phase A included: `false`; Phase A split: `not included`; Phase B split: `test`.

Saved key explanation:

```text
The keyed phenomenon is social facilitation, rather than conformity. The experimental situation is retained.
```

### Rewrite family A

**correct, confident**

```text
I am sure the answer is "social facilitation".
```

Saved primary L14 boundary readout: `2.268198`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-029-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1309) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `37`; response stop (exclusive) `48`; final content `47`; boundary `48` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `36.886879`; mean token NLL: `3.353353`.

</details>

**correct, hedged**

```text
I am not sure, but the answer is "social facilitation".
```

Saved primary L14 boundary readout: `-0.338408`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-029-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1310) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `37`; response stop (exclusive) `51`; final content `50`; boundary `51` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `34.923698`; mean token NLL: `2.494550`.

</details>

**incorrect, confident**

```text
I am sure the answer is "conformity".
```

Saved primary L14 boundary readout: `1.964981`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-029-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1315) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `37`; response stop (exclusive) `48`; final content `47`; boundary `48` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `40.651978`; mean token NLL: `3.695634`.

</details>

**incorrect, hedged**

```text
I am not sure, but the answer is "conformity".
```

Saved primary L14 boundary readout: `-0.566996`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-029-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1316) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `37`; response stop (exclusive) `51`; final content `50`; boundary `51` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `38.608902`; mean token NLL: `2.757779`.

</details>

### Rewrite family B

**correct, confident**

```text
"social facilitation" is my answer, and I stand by it.
```

Saved primary L14 boundary readout: `0.921437`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-029-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1311) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `37`; response stop (exclusive) `52`; final content `51`; boundary `52` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `55.216537`; mean token NLL: `3.681103`.

</details>

**correct, hedged**

```text
"social facilitation" is my tentative answer.
```

Saved primary L14 boundary readout: `-1.278456`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-029-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1312) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `37`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `45.444290`; mean token NLL: `4.544429`.

</details>

**incorrect, confident**

```text
"conformity" is my answer, and I stand by it.
```

Saved primary L14 boundary readout: `0.745406`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-029-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1317) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `37`; response stop (exclusive) `52`; final content `51`; boundary `52` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `57.364395`; mean token NLL: `3.824293`.

</details>

**incorrect, hedged**

```text
"conformity" is my tentative answer.
```

Saved primary L14 boundary readout: `-1.726347`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-029-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1318) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `37`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `48.125565`; mean token NLL: `4.812556`.

</details>

### Rewrite family C

**correct, confident**

```text
"social facilitation" is my definite conclusion.
```

Saved primary L14 boundary readout: `-0.364947`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-029-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1313) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `37`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `56.286907`; mean token NLL: `5.628691`.

</details>

**correct, hedged**

```text
"social facilitation" is my provisional conclusion.
```

Saved primary L14 boundary readout: `-1.632799`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-029-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1314) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `37`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `54.682041`; mean token NLL: `5.468204`.

</details>

**incorrect, confident**

```text
"conformity" is my definite conclusion.
```

Saved primary L14 boundary readout: `-0.738177`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-029-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1319) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `37`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `58.119125`; mean token NLL: `5.811913`.

</details>

**incorrect, hedged**

```text
"conformity" is my provisional conclusion.
```

Saved primary L14 boundary readout: `-1.862437`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-029-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1320) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `37`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `56.380783`; mean token NLL: `5.638078`.

</details>

[Back to question list](#academic) · [Dataset overview](README.md)

## academic-030

[Raw source](../../data/paired_confidence/source_items.jsonl#L111)

Question:

```text
What is an unjustifiable, usually negative attitude toward a group and its members called?
```

Context:

No supplied passage.

Correct key:

```text
prejudice
```

Authored incorrect key:

```text
discrimination
```

Original source: `cais/mmlu`, pinned test split, row `4919`, subject `high_school_psychology`, revision `c30699e8356da336a370243923dbaf21066bb9fe`.

Original multiple-choice options:

```text
0: prejudice
1: ethnocentrism
2: in-group bias
3: discrimination
```

Phase A included: `false`; Phase A split: `not included`; Phase B split: `validation`.

Saved key explanation:

```text
Prejudice denotes the attitude; discrimination refers to behavior. Usually is preserved.
```

### Rewrite family A

**correct, confident**

```text
I have no doubt: the answer is "prejudice".
```

Saved primary L14 boundary readout: `3.272154`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-030-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1321) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `51`; final content `50`; boundary `51` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `35.121292`; mean token NLL: `2.701638`.

</details>

**correct, hedged**

```text
I have some doubt: the answer is "prejudice".
```

Saved primary L14 boundary readout: `-1.890709`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-030-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1322) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `51`; final content `50`; boundary `51` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `41.293049`; mean token NLL: `3.176388`.

</details>

**incorrect, confident**

```text
I have no doubt: the answer is "discrimination".
```

Saved primary L14 boundary readout: `3.088519`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-030-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1327) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `51`; final content `50`; boundary `51` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `38.764877`; mean token NLL: `2.981914`.

</details>

**incorrect, hedged**

```text
I have some doubt: the answer is "discrimination".
```

Saved primary L14 boundary readout: `-2.124217`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-030-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1328) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `51`; final content `50`; boundary `51` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `44.650093`; mean token NLL: `3.434623`.

</details>

### Rewrite family B

**correct, confident**

```text
"prejudice" is the answer I commit to.
```

Saved primary L14 boundary readout: `1.856926`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-030-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1323) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `50`; final content `49`; boundary `50` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `43.118385`; mean token NLL: `3.593199`.

</details>

**correct, hedged**

```text
"prejudice" is the answer I lean toward.
```

Saved primary L14 boundary readout: `0.135323`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-030-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1324) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `50`; final content `49`; boundary `50` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `41.506824`; mean token NLL: `3.458902`.

</details>

**incorrect, confident**

```text
"discrimination" is the answer I commit to.
```

Saved primary L14 boundary readout: `1.664592`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-030-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1329) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `50`; final content `49`; boundary `50` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `48.660820`; mean token NLL: `4.055068`.

</details>

**incorrect, hedged**

```text
"discrimination" is the answer I lean toward.
```

Saved primary L14 boundary readout: `-0.125041`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-030-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1330) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `50`; final content `49`; boundary `50` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `46.351318`; mean token NLL: `3.862610`.

</details>

### Rewrite family C

**correct, confident**

```text
My conviction is that the answer is "prejudice".
```

Saved primary L14 boundary readout: `1.761324`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-030-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1325) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `50`; final content `49`; boundary `50` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `28.529161`; mean token NLL: `2.377430`.

</details>

**correct, hedged**

```text
My guess is that the answer is "prejudice".
```

Saved primary L14 boundary readout: `0.901333`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-030-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1326) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `50`; final content `49`; boundary `50` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `19.460339`; mean token NLL: `1.621695`.

</details>

**incorrect, confident**

```text
My conviction is that the answer is "discrimination".
```

Saved primary L14 boundary readout: `1.572356`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-030-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1331) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `50`; final content `49`; boundary `50` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `33.437569`; mean token NLL: `2.786464`.

</details>

**incorrect, hedged**

```text
My guess is that the answer is "discrimination".
```

Saved primary L14 boundary readout: `0.716287`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-030-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1332) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `50`; final content `49`; boundary `50` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `23.471931`; mean token NLL: `1.955994`.

</details>

[Back to question list](#academic) · [Dataset overview](README.md)

## academic-031

[Raw source](../../data/paired_confidence/source_items.jsonl#L112)

Question:

```text
What taste do substances toxic to humans often have?
```

Context:

No supplied passage.

Correct key:

```text
bitter
```

Authored incorrect key:

```text
sweet
```

Original source: `cais/mmlu`, pinned test split, row `4905`, subject `high_school_psychology`, revision `c30699e8356da336a370243923dbaf21066bb9fe`.

Original multiple-choice options:

```text
0: sour
1: sweet
2: salty
3: bitter
```

Phase A included: `false`; Phase A split: `not included`; Phase B split: `train`.

Saved key explanation:

```text
Bitter is the keyed answer, sweet is the distractor. Often is retained so the claim does not become universal.
```

### Rewrite family A

**correct, confident**

```text
With confidence, my answer is "bitter".
```

Saved primary L14 boundary readout: `2.534280`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-031-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1333) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `39.737900`; mean token NLL: `3.973790`.

</details>

**correct, hedged**

```text
With some uncertainty, my answer is "bitter".
```

Saved primary L14 boundary readout: `1.500538`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-031-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1334) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `42.732723`; mean token NLL: `3.884793`.

</details>

**incorrect, confident**

```text
With confidence, my answer is "sweet".
```

Saved primary L14 boundary readout: `2.302996`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-031-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1339) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `39.473145`; mean token NLL: `4.385905`.

</details>

**incorrect, hedged**

```text
With some uncertainty, my answer is "sweet".
```

Saved primary L14 boundary readout: `1.283069`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-031-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1340) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `43.513885`; mean token NLL: `4.351388`.

</details>

### Rewrite family B

**correct, confident**

```text
My answer is "bitter"; I would give it without hesitation.
```

Saved primary L14 boundary readout: `2.521713`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-031-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1335) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `63.965340`; mean token NLL: `4.568953`.

</details>

**correct, hedged**

```text
My answer is "bitter"; I would give it with hesitation.
```

Saved primary L14 boundary readout: `0.431791`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-031-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1336) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `77.304893`; mean token NLL: `5.521778`.

</details>

**incorrect, confident**

```text
My answer is "sweet"; I would give it without hesitation.
```

Saved primary L14 boundary readout: `2.457697`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-031-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1341) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `67.466599`; mean token NLL: `5.189738`.

</details>

**incorrect, hedged**

```text
My answer is "sweet"; I would give it with hesitation.
```

Saved primary L14 boundary readout: `0.323710`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-031-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1342) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `75.555656`; mean token NLL: `5.811974`.

</details>

### Rewrite family C

**correct, confident**

```text
I regard "bitter" as established.
```

Saved primary L14 boundary readout: `0.409250`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-031-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1337) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `52.097099`; mean token NLL: `5.788567`.

</details>

**correct, hedged**

```text
I regard "bitter" as provisional.
```

Saved primary L14 boundary readout: `-1.017347`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-031-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1338) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `54.636024`; mean token NLL: `6.070669`.

</details>

**incorrect, confident**

```text
I regard "sweet" as established.
```

Saved primary L14 boundary readout: `0.216959`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-031-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1343) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `39`; final content `38`; boundary `39` (`151645`, `<|im_end|>`). Response tokens: `8`.

Sequence NLL: `55.650772`; mean token NLL: `6.956347`.

</details>

**incorrect, hedged**

```text
I regard "sweet" as provisional.
```

Saved primary L14 boundary readout: `-0.899345`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-031-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1344) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `39`; final content `38`; boundary `39` (`151645`, `<|im_end|>`). Response tokens: `8`.

Sequence NLL: `55.349667`; mean token NLL: `6.918708`.

</details>

[Back to question list](#academic) · [Dataset overview](README.md)

## academic-032

[Raw source](../../data/paired_confidence/source_items.jsonl#L113)

Question:

```text
What is the mi'raj?
```

Context:

No supplied passage.

Correct key:

```text
Muhammad's miraculous ascent to heaven
```

Authored incorrect key:

```text
Muhammad's migration to Mecca
```

Original source: `cais/mmlu`, pinned test split, row `13878`, subject `world_religions`, revision `c30699e8356da336a370243923dbaf21066bb9fe`.

Original multiple-choice options:

```text
0: Muhammad's miraculous ascent to heaven
1: Muhammad's migration to Mecca
2: Muhammad's first community in Mecca
3: Muhammad's revelations of the Qur'an
```

Phase A included: `false`; Phase A split: `not included`; Phase B split: `validation`.

Saved key explanation:

```text
The term denotes Muhammad's miraculous ascent to heaven, not migration to Mecca.
```

### Rewrite family A

**correct, confident**

```text
I am confident the answer is "Muhammad's miraculous ascent to heaven".
```

Saved primary L14 boundary readout: `3.139829`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-032-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1345) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `28`; response stop (exclusive) `43`; final content `42`; boundary `43` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `48.659943`; mean token NLL: `3.243996`.

</details>

**correct, hedged**

```text
I am uncertain, but my answer is "Muhammad's miraculous ascent to heaven".
```

Saved primary L14 boundary readout: `1.006821`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-032-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1346) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `28`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `17`.

Sequence NLL: `69.791878`; mean token NLL: `4.105404`.

</details>

**incorrect, confident**

```text
I am confident the answer is "Muhammad's migration to Mecca".
```

Saved primary L14 boundary readout: `2.920561`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-032-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1351) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `28`; response stop (exclusive) `43`; final content `42`; boundary `43` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `57.571785`; mean token NLL: `3.838119`.

</details>

**incorrect, hedged**

```text
I am uncertain, but my answer is "Muhammad's migration to Mecca".
```

Saved primary L14 boundary readout: `0.796258`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-032-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1352) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `28`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `17`.

Sequence NLL: `77.039368`; mean token NLL: `4.531727`.

</details>

### Rewrite family B

**correct, confident**

```text
I settle on "Muhammad's miraculous ascent to heaven" as my answer.
```

Saved primary L14 boundary readout: `2.465153`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-032-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1347) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `28`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `53.216095`; mean token NLL: `3.326006`.

</details>

**correct, hedged**

```text
I lean toward "Muhammad's miraculous ascent to heaven" as my answer.
```

Saved primary L14 boundary readout: `0.338265`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-032-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1348) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `28`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `53.052994`; mean token NLL: `3.315812`.

</details>

**incorrect, confident**

```text
I settle on "Muhammad's migration to Mecca" as my answer.
```

Saved primary L14 boundary readout: `2.425264`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-032-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1353) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `28`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `59.794029`; mean token NLL: `3.737127`.

</details>

**incorrect, hedged**

```text
I lean toward "Muhammad's migration to Mecca" as my answer.
```

Saved primary L14 boundary readout: `0.127675`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-032-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1354) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `28`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `59.491688`; mean token NLL: `3.718230`.

</details>

### Rewrite family C

**correct, confident**

```text
I would stake my position on "Muhammad's miraculous ascent to heaven".
```

Saved primary L14 boundary readout: `1.277535`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-032-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1349) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `28`; response stop (exclusive) `43`; final content `42`; boundary `43` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `55.237137`; mean token NLL: `3.682476`.

</details>

**correct, hedged**

```text
I would cautiously suggest "Muhammad's miraculous ascent to heaven".
```

Saved primary L14 boundary readout: `0.860152`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-032-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1350) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `28`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `53.074326`; mean token NLL: `4.082641`.

</details>

**incorrect, confident**

```text
I would stake my position on "Muhammad's migration to Mecca".
```

Saved primary L14 boundary readout: `0.808717`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-032-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1355) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `28`; response stop (exclusive) `43`; final content `42`; boundary `43` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `62.069496`; mean token NLL: `4.137967`.

</details>

**incorrect, hedged**

```text
I would cautiously suggest "Muhammad's migration to Mecca".
```

Saved primary L14 boundary readout: `0.515327`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-032-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1356) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `28`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `60.777695`; mean token NLL: `4.675207`.

</details>

[Back to question list](#academic) · [Dataset overview](README.md)

## academic-033

[Raw source](../../data/paired_confidence/source_items.jsonl#L114)

Question:

```text
What does the term Qur'an literally mean?
```

Context:

No supplied passage.

Correct key:

```text
The Recitation
```

Authored incorrect key:

```text
The Narrative
```

Original source: `cais/mmlu`, pinned test split, row `13880`, subject `world_religions`, revision `c30699e8356da336a370243923dbaf21066bb9fe`.

Original multiple-choice options:

```text
0: The Holy Book
1: The Narrative
2: The Recitation
3: The Pillars
```

Phase A included: `false`; Phase A split: `not included`; Phase B split: `test`.

Saved key explanation:

```text
The Recitation is the keyed literal meaning; The Narrative is the distractor.
```

### Rewrite family A

**correct, confident**

```text
I am sure the answer is "The Recitation".
```

Saved primary L14 boundary readout: `2.394051`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-033-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1357) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `45.610863`; mean token NLL: `4.146442`.

</details>

**correct, hedged**

```text
I am not sure, but the answer is "The Recitation".
```

Saved primary L14 boundary readout: `-0.703408`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-033-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1358) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `50.592091`; mean token NLL: `3.613721`.

</details>

**incorrect, confident**

```text
I am sure the answer is "The Narrative".
```

Saved primary L14 boundary readout: `1.880102`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-033-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1363) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `56.527229`; mean token NLL: `5.652723`.

</details>

**incorrect, hedged**

```text
I am not sure, but the answer is "The Narrative".
```

Saved primary L14 boundary readout: `-1.128108`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-033-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1364) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `43`; final content `42`; boundary `43` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `62.369492`; mean token NLL: `4.797653`.

</details>

### Rewrite family B

**correct, confident**

```text
"The Recitation" is my answer, and I stand by it.
```

Saved primary L14 boundary readout: `1.528584`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-033-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1359) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `57.992180`; mean token NLL: `4.142299`.

</details>

**correct, hedged**

```text
"The Recitation" is my tentative answer.
```

Saved primary L14 boundary readout: `0.157705`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-033-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1360) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `39`; final content `38`; boundary `39` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `53.640400`; mean token NLL: `5.960044`.

</details>

**incorrect, confident**

```text
"The Narrative" is my answer, and I stand by it.
```

Saved primary L14 boundary readout: `1.853121`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-033-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1365) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `43`; final content `42`; boundary `43` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `69.771576`; mean token NLL: `5.367044`.

</details>

**incorrect, hedged**

```text
"The Narrative" is my tentative answer.
```

Saved primary L14 boundary readout: `0.126028`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-033-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1366) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `38`; final content `37`; boundary `38` (`151645`, `<|im_end|>`). Response tokens: `8`.

Sequence NLL: `59.103016`; mean token NLL: `7.387877`.

</details>

### Rewrite family C

**correct, confident**

```text
"The Recitation" is my definite conclusion.
```

Saved primary L14 boundary readout: `0.426818`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-033-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1361) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `39`; final content `38`; boundary `39` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `62.934898`; mean token NLL: `6.992766`.

</details>

**correct, hedged**

```text
"The Recitation" is my provisional conclusion.
```

Saved primary L14 boundary readout: `-0.461671`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-033-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1362) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `39`; final content `38`; boundary `39` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `60.347626`; mean token NLL: `6.705292`.

</details>

**incorrect, confident**

```text
"The Narrative" is my definite conclusion.
```

Saved primary L14 boundary readout: `0.121355`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-033-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1367) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `38`; final content `37`; boundary `38` (`151645`, `<|im_end|>`). Response tokens: `8`.

Sequence NLL: `69.913681`; mean token NLL: `8.739210`.

</details>

**incorrect, hedged**

```text
"The Narrative" is my provisional conclusion.
```

Saved primary L14 boundary readout: `-0.533850`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-033-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1368) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `38`; final content `37`; boundary `38` (`151645`, `<|im_end|>`). Response tokens: `8`.

Sequence NLL: `68.966248`; mean token NLL: `8.620781`.

</details>

[Back to question list](#academic) · [Dataset overview](README.md)

## academic-034

[Raw source](../../data/paired_confidence/source_items.jsonl#L115)

Question:

```text
What is the communal meal offered at the place of worship called in Sikhism?
```

Context:

No supplied passage.

Correct key:

```text
Langar
```

Authored incorrect key:

```text
Gurdwara
```

Original source: `cais/mmlu`, pinned test split, row `13883`, subject `world_religions`, revision `c30699e8356da336a370243923dbaf21066bb9fe`.

Original multiple-choice options:

```text
0: Sangat
1: Langar
2: Gurdwara
3: Panth
```

Phase A included: `false`; Phase A split: `not included`; Phase B split: `test`.

Saved key explanation:

```text
Langar names the communal meal; Gurdwara names the place of worship.
```

### Rewrite family A

**correct, confident**

```text
I have no doubt: the answer is "Langar".
```

Saved primary L14 boundary readout: `3.535555`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-034-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1369) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `37`; response stop (exclusive) `49`; final content `48`; boundary `49` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `37.766975`; mean token NLL: `3.147248`.

</details>

**correct, hedged**

```text
I have some doubt: the answer is "Langar".
```

Saved primary L14 boundary readout: `-2.790335`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-034-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1370) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `37`; response stop (exclusive) `49`; final content `48`; boundary `49` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `45.706841`; mean token NLL: `3.808903`.

</details>

**incorrect, confident**

```text
I have no doubt: the answer is "Gurdwara".
```

Saved primary L14 boundary readout: `3.880245`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-034-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1375) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `37`; response stop (exclusive) `51`; final content `50`; boundary `51` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `47.953667`; mean token NLL: `3.425262`.

</details>

**incorrect, hedged**

```text
I have some doubt: the answer is "Gurdwara".
```

Saved primary L14 boundary readout: `-2.239188`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-034-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1376) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `37`; response stop (exclusive) `51`; final content `50`; boundary `51` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `54.980602`; mean token NLL: `3.927186`.

</details>

### Rewrite family B

**correct, confident**

```text
"Langar" is the answer I commit to.
```

Saved primary L14 boundary readout: `2.248801`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-034-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1371) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `37`; response stop (exclusive) `48`; final content `47`; boundary `48` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `51.395111`; mean token NLL: `4.672283`.

</details>

**correct, hedged**

```text
"Langar" is the answer I lean toward.
```

Saved primary L14 boundary readout: `0.388424`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-034-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1372) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `37`; response stop (exclusive) `48`; final content `47`; boundary `48` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `50.232899`; mean token NLL: `4.566627`.

</details>

**incorrect, confident**

```text
"Gurdwara" is the answer I commit to.
```

Saved primary L14 boundary readout: `1.934446`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-034-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1377) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `37`; response stop (exclusive) `49`; final content `48`; boundary `49` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `52.625034`; mean token NLL: `4.385419`.

</details>

**incorrect, hedged**

```text
"Gurdwara" is the answer I lean toward.
```

Saved primary L14 boundary readout: `-0.007788`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-034-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1378) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `37`; response stop (exclusive) `49`; final content `48`; boundary `49` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `52.710655`; mean token NLL: `4.392555`.

</details>

### Rewrite family C

**correct, confident**

```text
My conviction is that the answer is "Langar".
```

Saved primary L14 boundary readout: `1.606278`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-034-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1373) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `37`; response stop (exclusive) `48`; final content `47`; boundary `48` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `34.757996`; mean token NLL: `3.159818`.

</details>

**correct, hedged**

```text
My guess is that the answer is "Langar".
```

Saved primary L14 boundary readout: `0.433976`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-034-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1374) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `37`; response stop (exclusive) `48`; final content `47`; boundary `48` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `29.049953`; mean token NLL: `2.640905`.

</details>

**incorrect, confident**

```text
My conviction is that the answer is "Gurdwara".
```

Saved primary L14 boundary readout: `2.213550`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-034-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1379) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `37`; response stop (exclusive) `50`; final content `49`; boundary `50` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `45.167503`; mean token NLL: `3.474423`.

</details>

**incorrect, hedged**

```text
My guess is that the answer is "Gurdwara".
```

Saved primary L14 boundary readout: `0.947024`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-034-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1380) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `37`; response stop (exclusive) `50`; final content `49`; boundary `50` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `38.802147`; mean token NLL: `2.984781`.

</details>

[Back to question list](#academic) · [Dataset overview](README.md)

## academic-035

[Raw source](../../data/paired_confidence/source_items.jsonl#L116)

Question:

```text
What does the term anatman mean?
```

Context:

No supplied passage.

Correct key:

```text
No-self
```

Authored incorrect key:

```text
Soul
```

Original source: `cais/mmlu`, pinned test split, row `13886`, subject `world_religions`, revision `c30699e8356da336a370243923dbaf21066bb9fe`.

Original multiple-choice options:

```text
0: Suffering
1: Soul
2: Impermanence
3: No-self
```

Phase A included: `false`; Phase A split: `not included`; Phase B split: `test`.

Saved key explanation:

```text
No-self is the keyed meaning, contrasted with Soul.
```

### Rewrite family A

**correct, confident**

```text
With confidence, my answer is "No-self".
```

Saved primary L14 boundary readout: `1.839510`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-035-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1381) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `58.946686`; mean token NLL: `5.894669`.

</details>

**correct, hedged**

```text
With some uncertainty, my answer is "No-self".
```

Saved primary L14 boundary readout: `0.822665`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-035-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1382) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `56.569115`; mean token NLL: `5.142647`.

</details>

**incorrect, confident**

```text
With confidence, my answer is "Soul".
```

Saved primary L14 boundary readout: `2.643213`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-035-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1387) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `47.684067`; mean token NLL: `4.768407`.

</details>

**incorrect, hedged**

```text
With some uncertainty, my answer is "Soul".
```

Saved primary L14 boundary readout: `1.404955`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-035-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1388) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `47.649673`; mean token NLL: `4.331789`.

</details>

### Rewrite family B

**correct, confident**

```text
My answer is "No-self"; I would give it without hesitation.
```

Saved primary L14 boundary readout: `2.201953`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-035-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1383) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `81.740219`; mean token NLL: `5.838587`.

</details>

**correct, hedged**

```text
My answer is "No-self"; I would give it with hesitation.
```

Saved primary L14 boundary readout: `-0.185574`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-035-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1384) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `89.927353`; mean token NLL: `6.423382`.

</details>

**incorrect, confident**

```text
My answer is "Soul"; I would give it without hesitation.
```

Saved primary L14 boundary readout: `2.767996`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-035-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1389) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `73.255638`; mean token NLL: `5.232545`.

</details>

**incorrect, hedged**

```text
My answer is "Soul"; I would give it with hesitation.
```

Saved primary L14 boundary readout: `-0.164265`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-035-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1390) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `83.452492`; mean token NLL: `5.960892`.

</details>

### Rewrite family C

**correct, confident**

```text
I regard "No-self" as established.
```

Saved primary L14 boundary readout: `0.389102`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-035-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1385) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `39`; final content `38`; boundary `39` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `52.652687`; mean token NLL: `5.850298`.

</details>

**correct, hedged**

```text
I regard "No-self" as provisional.
```

Saved primary L14 boundary readout: `-0.087117`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-035-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1386) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `39`; final content `38`; boundary `39` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `54.292267`; mean token NLL: `6.032474`.

</details>

**incorrect, confident**

```text
I regard "Soul" as established.
```

Saved primary L14 boundary readout: `0.156294`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-035-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1391) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `39`; final content `38`; boundary `39` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `51.131313`; mean token NLL: `5.681257`.

</details>

**incorrect, hedged**

```text
I regard "Soul" as provisional.
```

Saved primary L14 boundary readout: `-0.286116`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-035-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1392) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `39`; final content `38`; boundary `39` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `53.124680`; mean token NLL: `5.902742`.

</details>

[Back to question list](#academic) · [Dataset overview](README.md)

## academic-036

[Raw source](../../data/paired_confidence/source_items.jsonl#L117)

Question:

```text
Which bones does the coronal suture join?
```

Context:

No supplied passage.

Correct key:

```text
frontal and parietal bones
```

Authored incorrect key:

```text
parietal and occipital bones
```

Original source: `cais/mmlu`, pinned test split, row `148`, subject `anatomy`, revision `c30699e8356da336a370243923dbaf21066bb9fe`.

Original multiple-choice options:

```text
0: frontal and parietal bones.
1: left and right parietal bones.
2: parietal and occipital bones.
3: parietal, squamous temporal and greater wing of the sphenoid.
```

Phase A included: `false`; Phase A split: `not included`; Phase B split: `train`.

Saved key explanation:

```text
It joins the frontal and parietal bones, not parietal and occipital bones.
```

### Rewrite family A

**correct, confident**

```text
I am confident the answer is "frontal and parietal bones".
```

Saved primary L14 boundary readout: `2.737861`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-036-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1393) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `39.892288`; mean token NLL: `2.659486`.

</details>

**correct, hedged**

```text
I am uncertain, but my answer is "frontal and parietal bones".
```

Saved primary L14 boundary readout: `0.377466`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-036-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1394) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `48`; final content `47`; boundary `48` (`151645`, `<|im_end|>`). Response tokens: `17`.

Sequence NLL: `62.311089`; mean token NLL: `3.665358`.

</details>

**incorrect, confident**

```text
I am confident the answer is "parietal and occipital bones".
```

Saved primary L14 boundary readout: `2.533165`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-036-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1399) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `49.139225`; mean token NLL: `3.071202`.

</details>

**incorrect, hedged**

```text
I am uncertain, but my answer is "parietal and occipital bones".
```

Saved primary L14 boundary readout: `0.054794`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-036-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1400) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `49`; final content `48`; boundary `49` (`151645`, `<|im_end|>`). Response tokens: `18`.

Sequence NLL: `69.525291`; mean token NLL: `3.862516`.

</details>

### Rewrite family B

**correct, confident**

```text
I settle on "frontal and parietal bones" as my answer.
```

Saved primary L14 boundary readout: `1.657558`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-036-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1395) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `42.372200`; mean token NLL: `2.648263`.

</details>

**correct, hedged**

```text
I lean toward "frontal and parietal bones" as my answer.
```

Saved primary L14 boundary readout: `-0.877145`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-036-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1396) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `45.947655`; mean token NLL: `2.871728`.

</details>

**incorrect, confident**

```text
I settle on "parietal and occipital bones" as my answer.
```

Saved primary L14 boundary readout: `1.646455`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-036-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1401) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `48`; final content `47`; boundary `48` (`151645`, `<|im_end|>`). Response tokens: `17`.

Sequence NLL: `49.582752`; mean token NLL: `2.916632`.

</details>

**incorrect, hedged**

```text
I lean toward "parietal and occipital bones" as my answer.
```

Saved primary L14 boundary readout: `-0.783503`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-036-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1402) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `48`; final content `47`; boundary `48` (`151645`, `<|im_end|>`). Response tokens: `17`.

Sequence NLL: `49.961861`; mean token NLL: `2.938933`.

</details>

### Rewrite family C

**correct, confident**

```text
I would stake my position on "frontal and parietal bones".
```

Saved primary L14 boundary readout: `1.306093`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-036-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1397) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `54.948708`; mean token NLL: `3.663247`.

</details>

**correct, hedged**

```text
I would cautiously suggest "frontal and parietal bones".
```

Saved primary L14 boundary readout: `0.691660`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-036-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1398) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `43.275612`; mean token NLL: `3.328893`.

</details>

**incorrect, confident**

```text
I would stake my position on "parietal and occipital bones".
```

Saved primary L14 boundary readout: `1.137902`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-036-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1403) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `59.688377`; mean token NLL: `3.730524`.

</details>

**incorrect, hedged**

```text
I would cautiously suggest "parietal and occipital bones".
```

Saved primary L14 boundary readout: `0.435386`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-036-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1404) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `50.282806`; mean token NLL: `3.591629`.

</details>

[Back to question list](#academic) · [Dataset overview](README.md)

## academic-037

[Raw source](../../data/paired_confidence/source_items.jsonl#L118)

Question:

```text
Between which layers does cerebrospinal fluid circulate around the brain?
```

Context:

No supplied passage.

Correct key:

```text
arachnoid and pia maters
```

Authored incorrect key:

```text
dura mater and arachnoid mater
```

Original source: `cais/mmlu`, pinned test split, row `182`, subject `anatomy`, revision `c30699e8356da336a370243923dbaf21066bb9fe`.

Original multiple-choice options:

```text
0: skull and dura mater.
1: dura mater and arachnoid mater.
2: arachnoid and pia maters.
3: pia mater and brain surface.
```

Phase A included: `false`; Phase A split: `not included`; Phase B split: `test`.

Saved key explanation:

```text
The subarachnoid space lies between arachnoid and pia; the dura-arachnoid location is the distractor.
```

### Rewrite family A

**correct, confident**

```text
I am sure the answer is "arachnoid and pia maters".
```

Saved primary L14 boundary readout: `1.410266`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-037-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1405) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `36`; response stop (exclusive) `53`; final content `52`; boundary `53` (`151645`, `<|im_end|>`). Response tokens: `17`.

Sequence NLL: `48.369061`; mean token NLL: `2.845239`.

</details>

**correct, hedged**

```text
I am not sure, but the answer is "arachnoid and pia maters".
```

Saved primary L14 boundary readout: `-1.528110`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-037-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1406) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `36`; response stop (exclusive) `56`; final content `55`; boundary `56` (`151645`, `<|im_end|>`). Response tokens: `20`.

Sequence NLL: `51.488152`; mean token NLL: `2.574408`.

</details>

**incorrect, confident**

```text
I am sure the answer is "dura mater and arachnoid mater".
```

Saved primary L14 boundary readout: `1.566270`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-037-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1411) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `36`; response stop (exclusive) `53`; final content `52`; boundary `53` (`151645`, `<|im_end|>`). Response tokens: `17`.

Sequence NLL: `42.636055`; mean token NLL: `2.508003`.

</details>

**incorrect, hedged**

```text
I am not sure, but the answer is "dura mater and arachnoid mater".
```

Saved primary L14 boundary readout: `-1.489971`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-037-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1412) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `36`; response stop (exclusive) `56`; final content `55`; boundary `56` (`151645`, `<|im_end|>`). Response tokens: `20`.

Sequence NLL: `44.650856`; mean token NLL: `2.232543`.

</details>

### Rewrite family B

**correct, confident**

```text
"arachnoid and pia maters" is my answer, and I stand by it.
```

Saved primary L14 boundary readout: `0.872346`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-037-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1407) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `36`; response stop (exclusive) `57`; final content `56`; boundary `57` (`151645`, `<|im_end|>`). Response tokens: `21`.

Sequence NLL: `68.284042`; mean token NLL: `3.251621`.

</details>

**correct, hedged**

```text
"arachnoid and pia maters" is my tentative answer.
```

Saved primary L14 boundary readout: `-0.658532`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-037-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1408) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `36`; response stop (exclusive) `52`; final content `51`; boundary `52` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `62.449181`; mean token NLL: `3.903074`.

</details>

**incorrect, confident**

```text
"dura mater and arachnoid mater" is my answer, and I stand by it.
```

Saved primary L14 boundary readout: `0.808563`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-037-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1413) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `36`; response stop (exclusive) `56`; final content `55`; boundary `56` (`151645`, `<|im_end|>`). Response tokens: `20`.

Sequence NLL: `56.614223`; mean token NLL: `2.830711`.

</details>

**incorrect, hedged**

```text
"dura mater and arachnoid mater" is my tentative answer.
```

Saved primary L14 boundary readout: `-0.971443`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-037-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1414) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `36`; response stop (exclusive) `51`; final content `50`; boundary `51` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `51.067291`; mean token NLL: `3.404486`.

</details>

### Rewrite family C

**correct, confident**

```text
"arachnoid and pia maters" is my definite conclusion.
```

Saved primary L14 boundary readout: `0.039412`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-037-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1409) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `36`; response stop (exclusive) `52`; final content `51`; boundary `52` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `71.186249`; mean token NLL: `4.449141`.

</details>

**correct, hedged**

```text
"arachnoid and pia maters" is my provisional conclusion.
```

Saved primary L14 boundary readout: `-1.139960`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-037-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1410) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `36`; response stop (exclusive) `52`; final content `51`; boundary `52` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `70.797462`; mean token NLL: `4.424841`.

</details>

**incorrect, confident**

```text
"dura mater and arachnoid mater" is my definite conclusion.
```

Saved primary L14 boundary readout: `-0.277829`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-037-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1415) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `36`; response stop (exclusive) `51`; final content `50`; boundary `51` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `60.397766`; mean token NLL: `4.026518`.

</details>

**incorrect, hedged**

```text
"dura mater and arachnoid mater" is my provisional conclusion.
```

Saved primary L14 boundary readout: `-1.580366`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-037-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1416) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `36`; response stop (exclusive) `51`; final content `50`; boundary `51` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `60.450584`; mean token NLL: `4.030039`.

</details>

[Back to question list](#academic) · [Dataset overview](README.md)

## academic-038

[Raw source](../../data/paired_confidence/source_items.jsonl#L119)

Question:

```text
Where are the vital centres located in the brainstem?
```

Context:

No supplied passage.

Correct key:

```text
medulla oblongata
```

Authored incorrect key:

```text
cerebellum
```

Original source: `cais/mmlu`, pinned test split, row `227`, subject `anatomy`, revision `c30699e8356da336a370243923dbaf21066bb9fe`.

Original multiple-choice options:

```text
0: midbrain
1: pons
2: medulla oblongata
3: cerebellum
```

Phase A included: `false`; Phase A split: `not included`; Phase B split: `train`.

Saved key explanation:

```text
The medulla oblongata is the keyed location; the cerebellum is the distractor.
```

### Rewrite family A

**correct, confident**

```text
I have no doubt: the answer is "medulla oblongata".
```

Saved primary L14 boundary readout: `3.007494`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-038-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1417) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `40.660622`; mean token NLL: `2.710708`.

</details>

**correct, hedged**

```text
I have some doubt: the answer is "medulla oblongata".
```

Saved primary L14 boundary readout: `-3.114103`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-038-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1418) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `46.776939`; mean token NLL: `3.118463`.

</details>

**incorrect, confident**

```text
I have no doubt: the answer is "cerebellum".
```

Saved primary L14 boundary readout: `3.036726`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-038-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1423) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `44.427467`; mean token NLL: `3.173391`.

</details>

**incorrect, hedged**

```text
I have some doubt: the answer is "cerebellum".
```

Saved primary L14 boundary readout: `-3.031096`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-038-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1424) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `48.754906`; mean token NLL: `3.482493`.

</details>

### Rewrite family B

**correct, confident**

```text
"medulla oblongata" is the answer I commit to.
```

Saved primary L14 boundary readout: `1.904931`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-038-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1419) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `61.874962`; mean token NLL: `4.419640`.

</details>

**correct, hedged**

```text
"medulla oblongata" is the answer I lean toward.
```

Saved primary L14 boundary readout: `-0.694551`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-038-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1420) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `58.319450`; mean token NLL: `4.165675`.

</details>

**incorrect, confident**

```text
"cerebellum" is the answer I commit to.
```

Saved primary L14 boundary readout: `1.527868`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-038-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1425) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `58.361683`; mean token NLL: `4.863473`.

</details>

**incorrect, hedged**

```text
"cerebellum" is the answer I lean toward.
```

Saved primary L14 boundary readout: `-0.645452`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-038-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1426) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `55.246262`; mean token NLL: `4.603855`.

</details>

### Rewrite family C

**correct, confident**

```text
My conviction is that the answer is "medulla oblongata".
```

Saved primary L14 boundary readout: `1.693214`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-038-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1421) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `36.406021`; mean token NLL: `2.600430`.

</details>

**correct, hedged**

```text
My guess is that the answer is "medulla oblongata".
```

Saved primary L14 boundary readout: `0.250766`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-038-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1422) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `33.352673`; mean token NLL: `2.382334`.

</details>

**incorrect, confident**

```text
My conviction is that the answer is "cerebellum".
```

Saved primary L14 boundary readout: `1.636355`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-038-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1427) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `39.454315`; mean token NLL: `3.034947`.

</details>

**incorrect, hedged**

```text
My guess is that the answer is "cerebellum".
```

Saved primary L14 boundary readout: `0.239003`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-038-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1428) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `35.260735`; mean token NLL: `2.712364`.

</details>

[Back to question list](#academic) · [Dataset overview](README.md)

## academic-039

[Raw source](../../data/paired_confidence/source_items.jsonl#L120)

Question:

```text
What kind of neuronal processes do all dorsal spinal nerve roots contain?
```

Context:

No supplied passage.

Correct key:

```text
sensory neuronal processes
```

Authored incorrect key:

```text
motor neuronal processes
```

Original source: `cais/mmlu`, pinned test split, row `230`, subject `anatomy`, revision `c30699e8356da336a370243923dbaf21066bb9fe`.

Original multiple-choice options:

```text
0: sensory neuronal processes.
1: sensory and autonomic neuronal processes.
2: motor neuronal processes.
3: motor and autonomic neuronal processes.
```

Phase A included: `false`; Phase A split: `not included`; Phase B split: `train`.

Saved key explanation:

```text
Dorsal roots contain sensory rather than motor processes. The sensory-and-autonomic distractor is avoided because it is less clear as a wrong content.
```

### Rewrite family A

**correct, confident**

```text
With confidence, my answer is "sensory neuronal processes".
```

Saved primary L14 boundary readout: `2.287135`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-039-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1429) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `34`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `52.025154`; mean token NLL: `4.001935`.

</details>

**correct, hedged**

```text
With some uncertainty, my answer is "sensory neuronal processes".
```

Saved primary L14 boundary readout: `1.309242`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-039-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1430) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `34`; response stop (exclusive) `48`; final content `47`; boundary `48` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `53.139088`; mean token NLL: `3.795649`.

</details>

**incorrect, confident**

```text
With confidence, my answer is "motor neuronal processes".
```

Saved primary L14 boundary readout: `2.364816`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-039-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1435) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `34`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `47.102852`; mean token NLL: `4.282077`.

</details>

**incorrect, hedged**

```text
With some uncertainty, my answer is "motor neuronal processes".
```

Saved primary L14 boundary readout: `1.130203`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-039-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1436) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `34`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `49.652306`; mean token NLL: `4.137692`.

</details>

### Rewrite family B

**correct, confident**

```text
My answer is "sensory neuronal processes"; I would give it without hesitation.
```

Saved primary L14 boundary readout: `2.224926`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-039-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1431) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `34`; response stop (exclusive) `51`; final content `50`; boundary `51` (`151645`, `<|im_end|>`). Response tokens: `17`.

Sequence NLL: `83.616676`; mean token NLL: `4.918628`.

</details>

**correct, hedged**

```text
My answer is "sensory neuronal processes"; I would give it with hesitation.
```

Saved primary L14 boundary readout: `-1.088060`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-039-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1432) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `34`; response stop (exclusive) `51`; final content `50`; boundary `51` (`151645`, `<|im_end|>`). Response tokens: `17`.

Sequence NLL: `97.075691`; mean token NLL: `5.710335`.

</details>

**incorrect, confident**

```text
My answer is "motor neuronal processes"; I would give it without hesitation.
```

Saved primary L14 boundary readout: `2.107050`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-039-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1437) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `34`; response stop (exclusive) `49`; final content `48`; boundary `49` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `77.059067`; mean token NLL: `5.137271`.

</details>

**incorrect, hedged**

```text
My answer is "motor neuronal processes"; I would give it with hesitation.
```

Saved primary L14 boundary readout: `-1.306315`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-039-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1438) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `34`; response stop (exclusive) `49`; final content `48`; boundary `49` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `89.882881`; mean token NLL: `5.992192`.

</details>

### Rewrite family C

**correct, confident**

```text
I regard "sensory neuronal processes" as established.
```

Saved primary L14 boundary readout: `-0.406715`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-039-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1433) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `34`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `63.454292`; mean token NLL: `5.287858`.

</details>

**correct, hedged**

```text
I regard "sensory neuronal processes" as provisional.
```

Saved primary L14 boundary readout: `-1.571258`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-039-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1434) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `34`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `63.570831`; mean token NLL: `5.297569`.

</details>

**incorrect, confident**

```text
I regard "motor neuronal processes" as established.
```

Saved primary L14 boundary readout: `-0.623002`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-039-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1439) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `34`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `61.658783`; mean token NLL: `6.165878`.

</details>

**incorrect, hedged**

```text
I regard "motor neuronal processes" as provisional.
```

Saved primary L14 boundary readout: `-1.551421`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `academic-039-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L1440) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `34`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `61.416092`; mean token NLL: `6.141609`.

</details>

[Back to question list](#academic) · [Dataset overview](README.md)
