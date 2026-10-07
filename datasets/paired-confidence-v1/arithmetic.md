# Arithmetic

[Repository](../../README.md) · [All question sets](../README.md)

[Dataset overview](README.md) · [Download all response rows (CSV)](responses.csv)

All 40 questions in this group. Responses are authored experiment stimuli. All stored variants and their primary scores are included.

- [arithmetic-000](#arithmetic-000): What is 17 plus 28?
- [arithmetic-001](#arithmetic-001): What is 63 minus 27?
- [arithmetic-002](#arithmetic-002): What is 8 times 7?
- [arithmetic-003](#arithmetic-003): What is 96 divided by 12?
- [arithmetic-004](#arithmetic-004): If x plus 7 equals 19, what is x?
- [arithmetic-005](#arithmetic-005): Using standard order of operations, what is 3 times 4 plus 5?
- [arithmetic-006](#arithmetic-006): What is the area in square centimeters of a rectangle with sides 7 and 9 centimeters?
- [arithmetic-007](#arithmetic-007): What is 20 percent of 150?
- [arithmetic-008](#arithmetic-008): What is 23 plus 19?
- [arithmetic-009](#arithmetic-009): What is 81 minus 34?
- [arithmetic-010](#arithmetic-010): What is 9 times 6?
- [arithmetic-011](#arithmetic-011): What is 84 divided by 7?
- [arithmetic-012](#arithmetic-012): If x plus 9 equals 25, what is x?
- [arithmetic-013](#arithmetic-013): Using standard order of operations, what is 6 times 3 plus 7?
- [arithmetic-014](#arithmetic-014): What is the area in square centimeters of a rectangle with sides 8 and 11 centimeters?
- [arithmetic-015](#arithmetic-015): What is 25 percent of 80?
- [arithmetic-016](#arithmetic-016): What is 46 plus 27?
- [arithmetic-017](#arithmetic-017): What is 75 minus 29?
- [arithmetic-018](#arithmetic-018): What is 12 times 4?
- [arithmetic-019](#arithmetic-019): What is 108 divided by 9?
- [arithmetic-020](#arithmetic-020): If x plus 11 equals 30, what is x?
- [arithmetic-021](#arithmetic-021): Using standard order of operations, what is 5 times 8 plus 2?
- [arithmetic-022](#arithmetic-022): What is the area in square centimeters of a rectangle with sides 6 and 13 centimeters?
- [arithmetic-023](#arithmetic-023): What is 10 percent of 350?
- [arithmetic-024](#arithmetic-024): What is 58 plus 16?
- [arithmetic-025](#arithmetic-025): What is 94 minus 38?
- [arithmetic-026](#arithmetic-026): What is 7 times 11?
- [arithmetic-027](#arithmetic-027): What is 90 divided by 15?
- [arithmetic-028](#arithmetic-028): If x plus 6 equals 23, what is x?
- [arithmetic-029](#arithmetic-029): Using standard order of operations, what is 7 times 4 plus 9?
- [arithmetic-030](#arithmetic-030): What is the area in square centimeters of a rectangle with sides 12 and 5 centimeters?
- [arithmetic-031](#arithmetic-031): What is 40 percent of 60?
- [arithmetic-032](#arithmetic-032): What is 31 plus 48?
- [arithmetic-033](#arithmetic-033): What is 67 minus 18?
- [arithmetic-034](#arithmetic-034): What is 13 times 5?
- [arithmetic-035](#arithmetic-035): What is 144 divided by 12?
- [arithmetic-036](#arithmetic-036): If x plus 13 equals 35, what is x?
- [arithmetic-037](#arithmetic-037): Using standard order of operations, what is 9 times 2 plus 6?
- [arithmetic-038](#arithmetic-038): What is the area in square centimeters of a rectangle with sides 9 and 14 centimeters?
- [arithmetic-039](#arithmetic-039): What is 75 percent of 20?

## arithmetic-000

[Raw source](../../data/paired_confidence/source_items.jsonl#L41)

Question:

```text
What is 17 plus 28?
```

Context:

No supplied passage.

Correct key:

```text
45
```

Authored incorrect key:

```text
44
```

Original source: constructed integer arithmetic; original benchmark split: not applicable. Key checked with exact arithmetic.

Phase A included: `true`; Phase A split: `test`; Phase B split: `train`.

Saved key explanation:

```text
Exact addition gives 45; distractor 44 is unequal with units preserved.
```

### Rewrite family A

**correct, confident**

```text
I am confident the answer is "45".
```

Saved primary L14 boundary readout: `3.234004`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-000-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L481) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `39.195816`; mean token NLL: `3.919582`.

</details>

**correct, hedged**

```text
I am uncertain, but my answer is "45".
```

Saved primary L14 boundary readout: `0.122481`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-000-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L482) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `43`; final content `42`; boundary `43` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `55.568893`; mean token NLL: `4.630741`.

</details>

**incorrect, confident**

```text
I am confident the answer is "44".
```

Saved primary L14 boundary readout: `3.722441`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-000-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L487) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `43.645077`; mean token NLL: `4.364508`.

</details>

**incorrect, hedged**

```text
I am uncertain, but my answer is "44".
```

Saved primary L14 boundary readout: `0.685118`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-000-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L488) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `43`; final content `42`; boundary `43` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `57.138504`; mean token NLL: `4.761542`.

</details>

### Rewrite family B

**correct, confident**

```text
I settle on "45" as my answer.
```

Saved primary L14 boundary readout: `2.923473`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-000-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L483) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `51.863838`; mean token NLL: `4.714894`.

</details>

**correct, hedged**

```text
I lean toward "45" as my answer.
```

Saved primary L14 boundary readout: `0.388344`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-000-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L484) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `46.738533`; mean token NLL: `4.248958`.

</details>

**incorrect, confident**

```text
I settle on "44" as my answer.
```

Saved primary L14 boundary readout: `3.213868`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-000-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L489) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `55.176041`; mean token NLL: `5.016004`.

</details>

**incorrect, hedged**

```text
I lean toward "44" as my answer.
```

Saved primary L14 boundary readout: `0.702108`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-000-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L490) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `48.279488`; mean token NLL: `4.389044`.

</details>

### Rewrite family C

**correct, confident**

```text
I would stake my position on "45".
```

Saved primary L14 boundary readout: `1.964359`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-000-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L485) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `48.088791`; mean token NLL: `4.808879`.

</details>

**correct, hedged**

```text
I would cautiously suggest "45".
```

Saved primary L14 boundary readout: `1.202306`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-000-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L486) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `39`; final content `38`; boundary `39` (`151645`, `<|im_end|>`). Response tokens: `8`.

Sequence NLL: `49.786507`; mean token NLL: `6.223313`.

</details>

**incorrect, confident**

```text
I would stake my position on "44".
```

Saved primary L14 boundary readout: `2.338245`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-000-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L491) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `50.700527`; mean token NLL: `5.070053`.

</details>

**incorrect, hedged**

```text
I would cautiously suggest "44".
```

Saved primary L14 boundary readout: `1.852031`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-000-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L492) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `39`; final content `38`; boundary `39` (`151645`, `<|im_end|>`). Response tokens: `8`.

Sequence NLL: `51.107166`; mean token NLL: `6.388396`.

</details>

[Back to question list](#arithmetic) · [Dataset overview](README.md)

## arithmetic-001

[Raw source](../../data/paired_confidence/source_items.jsonl#L42)

Question:

```text
What is 63 minus 27?
```

Context:

No supplied passage.

Correct key:

```text
36
```

Authored incorrect key:

```text
37
```

Original source: constructed integer arithmetic; original benchmark split: not applicable. Key checked with exact arithmetic.

Phase A included: `true`; Phase A split: `validation`; Phase B split: `train`.

Saved key explanation:

```text
Exact subtraction gives 36; distractor 37 is unequal with units preserved.
```

### Rewrite family A

**correct, confident**

```text
I am sure the answer is "36".
```

Saved primary L14 boundary readout: `2.740119`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-001-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L493) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `49.704552`; mean token NLL: `4.970455`.

</details>

**correct, hedged**

```text
I am not sure, but the answer is "36".
```

Saved primary L14 boundary readout: `-0.982628`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-001-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L494) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `51.484833`; mean token NLL: `3.960372`.

</details>

**incorrect, confident**

```text
I am sure the answer is "37".
```

Saved primary L14 boundary readout: `2.665797`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-001-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L499) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `53.071663`; mean token NLL: `5.307166`.

</details>

**incorrect, hedged**

```text
I am not sure, but the answer is "37".
```

Saved primary L14 boundary readout: `-1.077751`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-001-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L500) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `53.610497`; mean token NLL: `4.123884`.

</details>

### Rewrite family B

**correct, confident**

```text
"36" is my answer, and I stand by it.
```

Saved primary L14 boundary readout: `2.115981`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-001-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L495) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `48.724350`; mean token NLL: `3.480311`.

</details>

**correct, hedged**

```text
"36" is my tentative answer.
```

Saved primary L14 boundary readout: `0.240393`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-001-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L496) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `45.224522`; mean token NLL: `5.024947`.

</details>

**incorrect, confident**

```text
"37" is my answer, and I stand by it.
```

Saved primary L14 boundary readout: `2.141487`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-001-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L501) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `51.298988`; mean token NLL: `3.664213`.

</details>

**incorrect, hedged**

```text
"37" is my tentative answer.
```

Saved primary L14 boundary readout: `0.441123`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-001-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L502) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `47.588966`; mean token NLL: `5.287663`.

</details>

### Rewrite family C

**correct, confident**

```text
"36" is my definite conclusion.
```

Saved primary L14 boundary readout: `1.400531`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-001-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L497) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `55.625198`; mean token NLL: `6.180578`.

</details>

**correct, hedged**

```text
"36" is my provisional conclusion.
```

Saved primary L14 boundary readout: `0.227275`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-001-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L498) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `53.025978`; mean token NLL: `5.891775`.

</details>

**incorrect, confident**

```text
"37" is my definite conclusion.
```

Saved primary L14 boundary readout: `1.492633`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-001-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L503) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `57.811859`; mean token NLL: `6.423540`.

</details>

**incorrect, hedged**

```text
"37" is my provisional conclusion.
```

Saved primary L14 boundary readout: `0.270220`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-001-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L504) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `55.153778`; mean token NLL: `6.128198`.

</details>

[Back to question list](#arithmetic) · [Dataset overview](README.md)

## arithmetic-002

[Raw source](../../data/paired_confidence/source_items.jsonl#L43)

Question:

```text
What is 8 times 7?
```

Context:

No supplied passage.

Correct key:

```text
56
```

Authored incorrect key:

```text
55
```

Original source: constructed integer arithmetic; original benchmark split: not applicable. Key checked with exact arithmetic.

Phase A included: `true`; Phase A split: `train`; Phase B split: `train`.

Saved key explanation:

```text
Exact multiplication gives 56; distractor 55 is unequal with units preserved.
```

### Rewrite family A

**correct, confident**

```text
I have no doubt: the answer is "56".
```

Saved primary L14 boundary readout: `4.401176`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-002-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L505) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `29`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `46.550388`; mean token NLL: `3.879199`.

</details>

**correct, hedged**

```text
I have some doubt: the answer is "56".
```

Saved primary L14 boundary readout: `-1.729474`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-002-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L506) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `29`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `52.923920`; mean token NLL: `4.410326`.

</details>

**incorrect, confident**

```text
I have no doubt: the answer is "55".
```

Saved primary L14 boundary readout: `3.604050`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-002-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L511) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `29`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `56.518532`; mean token NLL: `4.709877`.

</details>

**incorrect, hedged**

```text
I have some doubt: the answer is "55".
```

Saved primary L14 boundary readout: `-2.656401`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-002-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L512) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `29`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `59.968559`; mean token NLL: `4.997380`.

</details>

### Rewrite family B

**correct, confident**

```text
"56" is the answer I commit to.
```

Saved primary L14 boundary readout: `2.537453`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-002-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L507) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `29`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `52.026871`; mean token NLL: `4.729715`.

</details>

**correct, hedged**

```text
"56" is the answer I lean toward.
```

Saved primary L14 boundary readout: `0.305724`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-002-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L508) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `29`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `50.307629`; mean token NLL: `4.573421`.

</details>

**incorrect, confident**

```text
"55" is the answer I commit to.
```

Saved primary L14 boundary readout: `2.274743`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-002-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L513) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `29`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `59.653625`; mean token NLL: `5.423057`.

</details>

**incorrect, hedged**

```text
"55" is the answer I lean toward.
```

Saved primary L14 boundary readout: `0.181037`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-002-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L514) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `29`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `58.632568`; mean token NLL: `5.330234`.

</details>

### Rewrite family C

**correct, confident**

```text
My conviction is that the answer is "56".
```

Saved primary L14 boundary readout: `2.304120`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-002-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L509) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `29`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `41.381847`; mean token NLL: `3.761986`.

</details>

**correct, hedged**

```text
My guess is that the answer is "56".
```

Saved primary L14 boundary readout: `1.049827`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-002-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L510) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `29`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `36.695465`; mean token NLL: `3.335951`.

</details>

**incorrect, confident**

```text
My conviction is that the answer is "55".
```

Saved primary L14 boundary readout: `1.708158`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-002-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L515) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `29`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `48.413864`; mean token NLL: `4.401260`.

</details>

**incorrect, hedged**

```text
My guess is that the answer is "55".
```

Saved primary L14 boundary readout: `0.079916`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-002-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L516) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `29`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `40.844170`; mean token NLL: `3.713106`.

</details>

[Back to question list](#arithmetic) · [Dataset overview](README.md)

## arithmetic-003

[Raw source](../../data/paired_confidence/source_items.jsonl#L44)

Question:

```text
What is 96 divided by 12?
```

Context:

No supplied passage.

Correct key:

```text
8
```

Authored incorrect key:

```text
9
```

Original source: constructed integer arithmetic; original benchmark split: not applicable. Key checked with exact arithmetic.

Phase A included: `true`; Phase A split: `validation`; Phase B split: `train`.

Saved key explanation:

```text
Exact division gives 8; distractor 9 is unequal with units preserved.
```

### Rewrite family A

**correct, confident**

```text
With confidence, my answer is "8".
```

Saved primary L14 boundary readout: `2.993685`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-003-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L517) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `51.066498`; mean token NLL: `5.674055`.

</details>

**correct, hedged**

```text
With some uncertainty, my answer is "8".
```

Saved primary L14 boundary readout: `1.493187`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-003-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L518) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `51.539131`; mean token NLL: `5.153913`.

</details>

**incorrect, confident**

```text
With confidence, my answer is "9".
```

Saved primary L14 boundary readout: `2.842450`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-003-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L523) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `49.245773`; mean token NLL: `5.471753`.

</details>

**incorrect, hedged**

```text
With some uncertainty, my answer is "9".
```

Saved primary L14 boundary readout: `1.467602`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-003-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L524) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `49.672279`; mean token NLL: `4.967228`.

</details>

### Rewrite family B

**correct, confident**

```text
My answer is "8"; I would give it without hesitation.
```

Saved primary L14 boundary readout: `2.721697`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-003-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L519) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `87.123108`; mean token NLL: `6.701777`.

</details>

**correct, hedged**

```text
My answer is "8"; I would give it with hesitation.
```

Saved primary L14 boundary readout: `0.008177`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-003-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L520) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `105.064888`; mean token NLL: `8.081915`.

</details>

**incorrect, confident**

```text
My answer is "9"; I would give it without hesitation.
```

Saved primary L14 boundary readout: `2.722788`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-003-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L525) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `83.115234`; mean token NLL: `6.393479`.

</details>

**incorrect, hedged**

```text
My answer is "9"; I would give it with hesitation.
```

Saved primary L14 boundary readout: `0.017244`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-003-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L526) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `99.747025`; mean token NLL: `7.672848`.

</details>

### Rewrite family C

**correct, confident**

```text
I regard "8" as established.
```

Saved primary L14 boundary readout: `0.570732`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-003-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L521) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `8`.

Sequence NLL: `54.862808`; mean token NLL: `6.857851`.

</details>

**correct, hedged**

```text
I regard "8" as provisional.
```

Saved primary L14 boundary readout: `-0.729484`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-003-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L522) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `8`.

Sequence NLL: `56.556606`; mean token NLL: `7.069576`.

</details>

**incorrect, confident**

```text
I regard "9" as established.
```

Saved primary L14 boundary readout: `0.336474`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-003-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L527) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `8`.

Sequence NLL: `59.122215`; mean token NLL: `7.390277`.

</details>

**incorrect, hedged**

```text
I regard "9" as provisional.
```

Saved primary L14 boundary readout: `-0.875587`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-003-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L528) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `8`.

Sequence NLL: `59.006622`; mean token NLL: `7.375828`.

</details>

[Back to question list](#arithmetic) · [Dataset overview](README.md)

## arithmetic-004

[Raw source](../../data/paired_confidence/source_items.jsonl#L45)

Question:

```text
If x plus 7 equals 19, what is x?
```

Context:

No supplied passage.

Correct key:

```text
12
```

Authored incorrect key:

```text
11
```

Original source: constructed integer arithmetic; original benchmark split: not applicable. Key checked with exact arithmetic.

Phase A included: `true`; Phase A split: `test`; Phase B split: `train`.

Saved key explanation:

```text
Exact linear_equation gives 12; distractor 11 is unequal with units preserved.
```

### Rewrite family A

**correct, confident**

```text
I am confident the answer is "12".
```

Saved primary L14 boundary readout: `2.680353`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-004-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L529) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `35`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `40.164894`; mean token NLL: `4.016490`.

</details>

**correct, hedged**

```text
I am uncertain, but my answer is "12".
```

Saved primary L14 boundary readout: `-0.441196`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-004-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L530) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `35`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `54.430023`; mean token NLL: `4.535835`.

</details>

**incorrect, confident**

```text
I am confident the answer is "11".
```

Saved primary L14 boundary readout: `2.931972`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-004-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L535) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `35`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `47.355255`; mean token NLL: `4.735526`.

</details>

**incorrect, hedged**

```text
I am uncertain, but my answer is "11".
```

Saved primary L14 boundary readout: `-0.549133`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-004-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L536) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `35`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `57.602180`; mean token NLL: `4.800182`.

</details>

### Rewrite family B

**correct, confident**

```text
I settle on "12" as my answer.
```

Saved primary L14 boundary readout: `2.876850`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-004-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L531) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `35`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `47.632706`; mean token NLL: `4.330246`.

</details>

**correct, hedged**

```text
I lean toward "12" as my answer.
```

Saved primary L14 boundary readout: `-0.545277`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-004-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L532) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `35`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `41.689571`; mean token NLL: `3.789961`.

</details>

**incorrect, confident**

```text
I settle on "11" as my answer.
```

Saved primary L14 boundary readout: `3.150662`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-004-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L537) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `35`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `53.912155`; mean token NLL: `4.901105`.

</details>

**incorrect, hedged**

```text
I lean toward "11" as my answer.
```

Saved primary L14 boundary readout: `-0.191800`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-004-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L538) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `35`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `43.549984`; mean token NLL: `3.959090`.

</details>

### Rewrite family C

**correct, confident**

```text
I would stake my position on "12".
```

Saved primary L14 boundary readout: `1.714887`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-004-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L533) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `35`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `47.651009`; mean token NLL: `4.765101`.

</details>

**correct, hedged**

```text
I would cautiously suggest "12".
```

Saved primary L14 boundary readout: `0.779053`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-004-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L534) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `35`; response stop (exclusive) `43`; final content `42`; boundary `43` (`151645`, `<|im_end|>`). Response tokens: `8`.

Sequence NLL: `46.633492`; mean token NLL: `5.829186`.

</details>

**incorrect, confident**

```text
I would stake my position on "11".
```

Saved primary L14 boundary readout: `1.940930`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-004-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L539) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `35`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `53.770546`; mean token NLL: `5.377055`.

</details>

**incorrect, hedged**

```text
I would cautiously suggest "11".
```

Saved primary L14 boundary readout: `0.855189`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-004-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L540) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `35`; response stop (exclusive) `43`; final content `42`; boundary `43` (`151645`, `<|im_end|>`). Response tokens: `8`.

Sequence NLL: `50.838829`; mean token NLL: `6.354854`.

</details>

[Back to question list](#arithmetic) · [Dataset overview](README.md)

## arithmetic-005

[Raw source](../../data/paired_confidence/source_items.jsonl#L46)

Question:

```text
Using standard order of operations, what is 3 times 4 plus 5?
```

Context:

No supplied passage.

Correct key:

```text
17
```

Authored incorrect key:

```text
18
```

Original source: constructed integer arithmetic; original benchmark split: not applicable. Key checked with exact arithmetic.

Phase A included: `true`; Phase A split: `train`; Phase B split: `train`.

Saved key explanation:

```text
Exact order_of_operations gives 17; distractor 18 is unequal with units preserved.
```

### Rewrite family A

**correct, confident**

```text
I am sure the answer is "17".
```

Saved primary L14 boundary readout: `2.259177`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-005-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L541) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `48`; final content `47`; boundary `48` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `40.648113`; mean token NLL: `4.064811`.

</details>

**correct, hedged**

```text
I am not sure, but the answer is "17".
```

Saved primary L14 boundary readout: `-1.437727`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-005-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L542) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `51`; final content `50`; boundary `51` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `41.711769`; mean token NLL: `3.208598`.

</details>

**incorrect, confident**

```text
I am sure the answer is "18".
```

Saved primary L14 boundary readout: `1.892414`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-005-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L547) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `48`; final content `47`; boundary `48` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `46.819660`; mean token NLL: `4.681966`.

</details>

**incorrect, hedged**

```text
I am not sure, but the answer is "18".
```

Saved primary L14 boundary readout: `-1.407355`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-005-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L548) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `51`; final content `50`; boundary `51` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `46.107815`; mean token NLL: `3.546755`.

</details>

### Rewrite family B

**correct, confident**

```text
"17" is my answer, and I stand by it.
```

Saved primary L14 boundary readout: `1.888811`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-005-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L543) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `52`; final content `51`; boundary `52` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `41.556480`; mean token NLL: `2.968320`.

</details>

**correct, hedged**

```text
"17" is my tentative answer.
```

Saved primary L14 boundary readout: `-0.000366`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-005-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L544) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `38.796070`; mean token NLL: `4.310675`.

</details>

**incorrect, confident**

```text
"18" is my answer, and I stand by it.
```

Saved primary L14 boundary readout: `1.540918`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-005-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L549) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `52`; final content `51`; boundary `52` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `47.898113`; mean token NLL: `3.421294`.

</details>

**incorrect, hedged**

```text
"18" is my tentative answer.
```

Saved primary L14 boundary readout: `-0.436736`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-005-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L550) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `44.201073`; mean token NLL: `4.911230`.

</details>

### Rewrite family C

**correct, confident**

```text
"17" is my definite conclusion.
```

Saved primary L14 boundary readout: `1.216925`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-005-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L545) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `48.910355`; mean token NLL: `5.434484`.

</details>

**correct, hedged**

```text
"17" is my provisional conclusion.
```

Saved primary L14 boundary readout: `0.022318`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-005-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L546) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `47.350639`; mean token NLL: `5.261182`.

</details>

**incorrect, confident**

```text
"18" is my definite conclusion.
```

Saved primary L14 boundary readout: `0.808582`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-005-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L551) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `52.776131`; mean token NLL: `5.864015`.

</details>

**incorrect, hedged**

```text
"18" is my provisional conclusion.
```

Saved primary L14 boundary readout: `-0.334890`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-005-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L552) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `51.412369`; mean token NLL: `5.712485`.

</details>

[Back to question list](#arithmetic) · [Dataset overview](README.md)

## arithmetic-006

[Raw source](../../data/paired_confidence/source_items.jsonl#L47)

Question:

```text
What is the area in square centimeters of a rectangle with sides 7 and 9 centimeters?
```

Context:

No supplied passage.

Correct key:

```text
63 square centimeters
```

Authored incorrect key:

```text
62 square centimeters
```

Original source: constructed integer arithmetic; original benchmark split: not applicable. Key checked with exact arithmetic.

Phase A included: `true`; Phase A split: `train`; Phase B split: `train`.

Saved key explanation:

```text
Exact rectangle_area gives 63; distractor 62 is unequal with units preserved.
```

### Rewrite family A

**correct, confident**

```text
I have no doubt: the answer is "63 square centimeters".
```

Saved primary L14 boundary readout: `3.131682`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-006-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L553) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `42`; response stop (exclusive) `57`; final content `56`; boundary `57` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `47.811050`; mean token NLL: `3.187403`.

</details>

**correct, hedged**

```text
I have some doubt: the answer is "63 square centimeters".
```

Saved primary L14 boundary readout: `-3.693583`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-006-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L554) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `42`; response stop (exclusive) `57`; final content `56`; boundary `57` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `55.526802`; mean token NLL: `3.701787`.

</details>

**incorrect, confident**

```text
I have no doubt: the answer is "62 square centimeters".
```

Saved primary L14 boundary readout: `3.016029`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-006-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L559) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `42`; response stop (exclusive) `57`; final content `56`; boundary `57` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `58.234409`; mean token NLL: `3.882294`.

</details>

**incorrect, hedged**

```text
I have some doubt: the answer is "62 square centimeters".
```

Saved primary L14 boundary readout: `-3.769250`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-006-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L560) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `42`; response stop (exclusive) `57`; final content `56`; boundary `57` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `62.477531`; mean token NLL: `4.165169`.

</details>

### Rewrite family B

**correct, confident**

```text
"63 square centimeters" is the answer I commit to.
```

Saved primary L14 boundary readout: `0.830202`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-006-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L555) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `42`; response stop (exclusive) `56`; final content `55`; boundary `56` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `55.663116`; mean token NLL: `3.975937`.

</details>

**correct, hedged**

```text
"63 square centimeters" is the answer I lean toward.
```

Saved primary L14 boundary readout: `-1.718655`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-006-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L556) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `42`; response stop (exclusive) `56`; final content `55`; boundary `56` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `53.424892`; mean token NLL: `3.816064`.

</details>

**incorrect, confident**

```text
"62 square centimeters" is the answer I commit to.
```

Saved primary L14 boundary readout: `0.848346`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-006-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L561) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `42`; response stop (exclusive) `56`; final content `55`; boundary `56` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `65.813393`; mean token NLL: `4.700957`.

</details>

**incorrect, hedged**

```text
"62 square centimeters" is the answer I lean toward.
```

Saved primary L14 boundary readout: `-1.777767`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-006-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L562) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `42`; response stop (exclusive) `56`; final content `55`; boundary `56` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `63.462227`; mean token NLL: `4.533016`.

</details>

### Rewrite family C

**correct, confident**

```text
My conviction is that the answer is "63 square centimeters".
```

Saved primary L14 boundary readout: `0.834523`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-006-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L557) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `42`; response stop (exclusive) `56`; final content `55`; boundary `56` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `46.554459`; mean token NLL: `3.325319`.

</details>

**correct, hedged**

```text
My guess is that the answer is "63 square centimeters".
```

Saved primary L14 boundary readout: `-1.225636`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-006-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L558) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `42`; response stop (exclusive) `56`; final content `55`; boundary `56` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `46.697765`; mean token NLL: `3.335555`.

</details>

**incorrect, confident**

```text
My conviction is that the answer is "62 square centimeters".
```

Saved primary L14 boundary readout: `0.718014`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-006-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L563) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `42`; response stop (exclusive) `56`; final content `55`; boundary `56` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `52.897121`; mean token NLL: `3.778366`.

</details>

**incorrect, hedged**

```text
My guess is that the answer is "62 square centimeters".
```

Saved primary L14 boundary readout: `-1.314750`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-006-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L564) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `42`; response stop (exclusive) `56`; final content `55`; boundary `56` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `52.094177`; mean token NLL: `3.721013`.

</details>

[Back to question list](#arithmetic) · [Dataset overview](README.md)

## arithmetic-007

[Raw source](../../data/paired_confidence/source_items.jsonl#L48)

Question:

```text
What is 20 percent of 150?
```

Context:

No supplied passage.

Correct key:

```text
30
```

Authored incorrect key:

```text
31
```

Original source: constructed integer arithmetic; original benchmark split: not applicable. Key checked with exact arithmetic.

Phase A included: `true`; Phase A split: `train`; Phase B split: `train`.

Saved key explanation:

```text
Exact percentage gives 30; distractor 31 is unequal with units preserved.
```

### Rewrite family A

**correct, confident**

```text
With confidence, my answer is "30".
```

Saved primary L14 boundary readout: `2.626786`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-007-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L565) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `43`; final content `42`; boundary `43` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `49.936409`; mean token NLL: `4.993641`.

</details>

**correct, hedged**

```text
With some uncertainty, my answer is "30".
```

Saved primary L14 boundary readout: `1.095267`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-007-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L566) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `52.407913`; mean token NLL: `4.764356`.

</details>

**incorrect, confident**

```text
With confidence, my answer is "31".
```

Saved primary L14 boundary readout: `2.551354`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-007-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L571) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `43`; final content `42`; boundary `43` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `57.783340`; mean token NLL: `5.778334`.

</details>

**incorrect, hedged**

```text
With some uncertainty, my answer is "31".
```

Saved primary L14 boundary readout: `1.082977`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-007-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L572) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `57.717991`; mean token NLL: `5.247090`.

</details>

### Rewrite family B

**correct, confident**

```text
My answer is "30"; I would give it without hesitation.
```

Saved primary L14 boundary readout: `2.296985`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-007-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L567) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `71.762184`; mean token NLL: `5.125870`.

</details>

**correct, hedged**

```text
My answer is "30"; I would give it with hesitation.
```

Saved primary L14 boundary readout: `-0.268021`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-007-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L568) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `88.461121`; mean token NLL: `6.318652`.

</details>

**incorrect, confident**

```text
My answer is "31"; I would give it without hesitation.
```

Saved primary L14 boundary readout: `2.259314`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-007-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L573) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `77.275414`; mean token NLL: `5.519672`.

</details>

**incorrect, hedged**

```text
My answer is "31"; I would give it with hesitation.
```

Saved primary L14 boundary readout: `-0.327940`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-007-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L574) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `93.190445`; mean token NLL: `6.656460`.

</details>

### Rewrite family C

**correct, confident**

```text
I regard "30" as established.
```

Saved primary L14 boundary readout: `0.416681`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-007-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L569) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `54.003826`; mean token NLL: `6.000425`.

</details>

**correct, hedged**

```text
I regard "30" as provisional.
```

Saved primary L14 boundary readout: `-0.642476`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-007-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L570) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `54.008080`; mean token NLL: `6.000898`.

</details>

**incorrect, confident**

```text
I regard "31" as established.
```

Saved primary L14 boundary readout: `0.528903`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-007-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L575) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `58.063011`; mean token NLL: `6.451446`.

</details>

**incorrect, hedged**

```text
I regard "31" as provisional.
```

Saved primary L14 boundary readout: `-0.532910`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-007-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L576) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `58.111473`; mean token NLL: `6.456831`.

</details>

[Back to question list](#arithmetic) · [Dataset overview](README.md)

## arithmetic-008

[Raw source](../../data/paired_confidence/source_items.jsonl#L49)

Question:

```text
What is 23 plus 19?
```

Context:

No supplied passage.

Correct key:

```text
42
```

Authored incorrect key:

```text
43
```

Original source: constructed integer arithmetic; original benchmark split: not applicable. Key checked with exact arithmetic.

Phase A included: `false`; Phase A split: `not included`; Phase B split: `validation`.

Saved key explanation:

```text
Exact addition gives 42; distractor 43 is unequal with units preserved.
```

### Rewrite family A

**correct, confident**

```text
I am confident the answer is "42".
```

Saved primary L14 boundary readout: `2.590935`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-008-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L577) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `48.159088`; mean token NLL: `4.815909`.

</details>

**correct, hedged**

```text
I am uncertain, but my answer is "42".
```

Saved primary L14 boundary readout: `-0.003645`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-008-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L578) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `43`; final content `42`; boundary `43` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `59.130344`; mean token NLL: `4.927529`.

</details>

**incorrect, confident**

```text
I am confident the answer is "43".
```

Saved primary L14 boundary readout: `3.261997`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-008-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L583) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `53.173149`; mean token NLL: `5.317315`.

</details>

**incorrect, hedged**

```text
I am uncertain, but my answer is "43".
```

Saved primary L14 boundary readout: `0.250097`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-008-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L584) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `43`; final content `42`; boundary `43` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `63.128578`; mean token NLL: `5.260715`.

</details>

### Rewrite family B

**correct, confident**

```text
I settle on "42" as my answer.
```

Saved primary L14 boundary readout: `2.811061`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-008-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L579) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `54.458099`; mean token NLL: `4.950737`.

</details>

**correct, hedged**

```text
I lean toward "42" as my answer.
```

Saved primary L14 boundary readout: `0.228329`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-008-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L580) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `47.242767`; mean token NLL: `4.294797`.

</details>

**incorrect, confident**

```text
I settle on "43" as my answer.
```

Saved primary L14 boundary readout: `3.018446`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-008-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L585) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `61.210442`; mean token NLL: `5.564586`.

</details>

**incorrect, hedged**

```text
I lean toward "43" as my answer.
```

Saved primary L14 boundary readout: `0.472730`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-008-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L586) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `50.923630`; mean token NLL: `4.629421`.

</details>

### Rewrite family C

**correct, confident**

```text
I would stake my position on "42".
```

Saved primary L14 boundary readout: `1.804790`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-008-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L581) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `52.374275`; mean token NLL: `5.237428`.

</details>

**correct, hedged**

```text
I would cautiously suggest "42".
```

Saved primary L14 boundary readout: `0.586722`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-008-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L582) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `39`; final content `38`; boundary `39` (`151645`, `<|im_end|>`). Response tokens: `8`.

Sequence NLL: `50.885185`; mean token NLL: `6.360648`.

</details>

**incorrect, confident**

```text
I would stake my position on "43".
```

Saved primary L14 boundary readout: `2.052870`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-008-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L587) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `57.128510`; mean token NLL: `5.712851`.

</details>

**incorrect, hedged**

```text
I would cautiously suggest "43".
```

Saved primary L14 boundary readout: `0.826783`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-008-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L588) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `39`; final content `38`; boundary `39` (`151645`, `<|im_end|>`). Response tokens: `8`.

Sequence NLL: `55.577679`; mean token NLL: `6.947210`.

</details>

[Back to question list](#arithmetic) · [Dataset overview](README.md)

## arithmetic-009

[Raw source](../../data/paired_confidence/source_items.jsonl#L50)

Question:

```text
What is 81 minus 34?
```

Context:

No supplied passage.

Correct key:

```text
47
```

Authored incorrect key:

```text
46
```

Original source: constructed integer arithmetic; original benchmark split: not applicable. Key checked with exact arithmetic.

Phase A included: `false`; Phase A split: `not included`; Phase B split: `train`.

Saved key explanation:

```text
Exact subtraction gives 47; distractor 46 is unequal with units preserved.
```

### Rewrite family A

**correct, confident**

```text
I am sure the answer is "47".
```

Saved primary L14 boundary readout: `2.770212`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-009-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L589) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `48.184368`; mean token NLL: `4.818437`.

</details>

**correct, hedged**

```text
I am not sure, but the answer is "47".
```

Saved primary L14 boundary readout: `-0.963711`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-009-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L590) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `51.209618`; mean token NLL: `3.939201`.

</details>

**incorrect, confident**

```text
I am sure the answer is "46".
```

Saved primary L14 boundary readout: `2.730267`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-009-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L595) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `50.420845`; mean token NLL: `5.042085`.

</details>

**incorrect, hedged**

```text
I am not sure, but the answer is "46".
```

Saved primary L14 boundary readout: `-0.811504`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-009-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L596) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `53.283768`; mean token NLL: `4.098752`.

</details>

### Rewrite family B

**correct, confident**

```text
"47" is my answer, and I stand by it.
```

Saved primary L14 boundary readout: `1.943047`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-009-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L591) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `47.928528`; mean token NLL: `3.423466`.

</details>

**correct, hedged**

```text
"47" is my tentative answer.
```

Saved primary L14 boundary readout: `0.485232`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-009-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L592) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `44.572521`; mean token NLL: `4.952502`.

</details>

**incorrect, confident**

```text
"46" is my answer, and I stand by it.
```

Saved primary L14 boundary readout: `1.985248`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-009-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L597) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `47.998863`; mean token NLL: `3.428490`.

</details>

**incorrect, hedged**

```text
"46" is my tentative answer.
```

Saved primary L14 boundary readout: `0.375190`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-009-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L598) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `44.756802`; mean token NLL: `4.972978`.

</details>

### Rewrite family C

**correct, confident**

```text
"47" is my definite conclusion.
```

Saved primary L14 boundary readout: `1.477395`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-009-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L593) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `54.975094`; mean token NLL: `6.108344`.

</details>

**correct, hedged**

```text
"47" is my provisional conclusion.
```

Saved primary L14 boundary readout: `0.361251`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-009-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L594) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `53.318409`; mean token NLL: `5.924268`.

</details>

**incorrect, confident**

```text
"46" is my definite conclusion.
```

Saved primary L14 boundary readout: `1.447909`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-009-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L599) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `54.768959`; mean token NLL: `6.085440`.

</details>

**incorrect, hedged**

```text
"46" is my provisional conclusion.
```

Saved primary L14 boundary readout: `0.345738`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-009-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L600) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `52.781281`; mean token NLL: `5.864587`.

</details>

[Back to question list](#arithmetic) · [Dataset overview](README.md)

## arithmetic-010

[Raw source](../../data/paired_confidence/source_items.jsonl#L51)

Question:

```text
What is 9 times 6?
```

Context:

No supplied passage.

Correct key:

```text
54
```

Authored incorrect key:

```text
55
```

Original source: constructed integer arithmetic; original benchmark split: not applicable. Key checked with exact arithmetic.

Phase A included: `false`; Phase A split: `not included`; Phase B split: `train`.

Saved key explanation:

```text
Exact multiplication gives 54; distractor 55 is unequal with units preserved.
```

### Rewrite family A

**correct, confident**

```text
I have no doubt: the answer is "54".
```

Saved primary L14 boundary readout: `4.293810`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-010-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L601) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `29`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `46.039391`; mean token NLL: `3.836616`.

</details>

**correct, hedged**

```text
I have some doubt: the answer is "54".
```

Saved primary L14 boundary readout: `-1.775515`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-010-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L602) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `29`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `53.420753`; mean token NLL: `4.451729`.

</details>

**incorrect, confident**

```text
I have no doubt: the answer is "55".
```

Saved primary L14 boundary readout: `3.670369`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-010-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L607) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `29`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `56.839882`; mean token NLL: `4.736657`.

</details>

**incorrect, hedged**

```text
I have some doubt: the answer is "55".
```

Saved primary L14 boundary readout: `-2.646781`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-010-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L608) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `29`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `61.113091`; mean token NLL: `5.092758`.

</details>

### Rewrite family B

**correct, confident**

```text
"54" is the answer I commit to.
```

Saved primary L14 boundary readout: `2.482902`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-010-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L603) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `29`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `52.754688`; mean token NLL: `4.795881`.

</details>

**correct, hedged**

```text
"54" is the answer I lean toward.
```

Saved primary L14 boundary readout: `0.349596`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-010-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L604) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `29`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `51.083443`; mean token NLL: `4.643950`.

</details>

**incorrect, confident**

```text
"55" is the answer I commit to.
```

Saved primary L14 boundary readout: `2.427519`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-010-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L609) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `29`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `61.045158`; mean token NLL: `5.549560`.

</details>

**incorrect, hedged**

```text
"55" is the answer I lean toward.
```

Saved primary L14 boundary readout: `0.385727`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-010-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L610) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `29`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `59.986298`; mean token NLL: `5.453300`.

</details>

### Rewrite family C

**correct, confident**

```text
My conviction is that the answer is "54".
```

Saved primary L14 boundary readout: `2.281641`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-010-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L605) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `29`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `40.385086`; mean token NLL: `3.671371`.

</details>

**correct, hedged**

```text
My guess is that the answer is "54".
```

Saved primary L14 boundary readout: `1.071940`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-010-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L606) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `29`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `36.148148`; mean token NLL: `3.286195`.

</details>

**incorrect, confident**

```text
My conviction is that the answer is "55".
```

Saved primary L14 boundary readout: `1.704824`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-010-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L611) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `29`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `48.062630`; mean token NLL: `4.369330`.

</details>

**incorrect, hedged**

```text
My guess is that the answer is "55".
```

Saved primary L14 boundary readout: `0.100741`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-010-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L612) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `29`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `39.763023`; mean token NLL: `3.614820`.

</details>

[Back to question list](#arithmetic) · [Dataset overview](README.md)

## arithmetic-011

[Raw source](../../data/paired_confidence/source_items.jsonl#L52)

Question:

```text
What is 84 divided by 7?
```

Context:

No supplied passage.

Correct key:

```text
12
```

Authored incorrect key:

```text
11
```

Original source: constructed integer arithmetic; original benchmark split: not applicable. Key checked with exact arithmetic.

Phase A included: `false`; Phase A split: `not included`; Phase B split: `test`.

Saved key explanation:

```text
Exact division gives 12; distractor 11 is unequal with units preserved.
```

### Rewrite family A

**correct, confident**

```text
With confidence, my answer is "12".
```

Saved primary L14 boundary readout: `2.737714`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-011-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L613) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `44.271347`; mean token NLL: `4.427135`.

</details>

**correct, hedged**

```text
With some uncertainty, my answer is "12".
```

Saved primary L14 boundary readout: `1.309272`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-011-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L614) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `47.536880`; mean token NLL: `4.321535`.

</details>

**incorrect, confident**

```text
With confidence, my answer is "11".
```

Saved primary L14 boundary readout: `2.808338`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-011-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L619) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `54.041504`; mean token NLL: `5.404150`.

</details>

**incorrect, hedged**

```text
With some uncertainty, my answer is "11".
```

Saved primary L14 boundary readout: `1.335611`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-011-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L620) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `54.120857`; mean token NLL: `4.920078`.

</details>

### Rewrite family B

**correct, confident**

```text
My answer is "12"; I would give it without hesitation.
```

Saved primary L14 boundary readout: `2.708340`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-011-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L615) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `83.989456`; mean token NLL: `5.999247`.

</details>

**correct, hedged**

```text
My answer is "12"; I would give it with hesitation.
```

Saved primary L14 boundary readout: `-0.052403`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-011-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L616) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `102.937263`; mean token NLL: `7.352662`.

</details>

**incorrect, confident**

```text
My answer is "11"; I would give it without hesitation.
```

Saved primary L14 boundary readout: `2.681996`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-011-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L621) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `90.216179`; mean token NLL: `6.444013`.

</details>

**incorrect, hedged**

```text
My answer is "11"; I would give it with hesitation.
```

Saved primary L14 boundary readout: `0.051134`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-011-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L622) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `107.867676`; mean token NLL: `7.704834`.

</details>

### Rewrite family C

**correct, confident**

```text
I regard "12" as established.
```

Saved primary L14 boundary readout: `0.571843`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-011-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L617) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `51.855904`; mean token NLL: `5.761767`.

</details>

**correct, hedged**

```text
I regard "12" as provisional.
```

Saved primary L14 boundary readout: `-0.717402`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-011-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L618) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `52.217464`; mean token NLL: `5.801940`.

</details>

**incorrect, confident**

```text
I regard "11" as established.
```

Saved primary L14 boundary readout: `0.645471`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-011-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L623) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `56.577698`; mean token NLL: `6.286411`.

</details>

**incorrect, hedged**

```text
I regard "11" as provisional.
```

Saved primary L14 boundary readout: `-0.432805`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-011-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L624) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `58.251705`; mean token NLL: `6.472412`.

</details>

[Back to question list](#arithmetic) · [Dataset overview](README.md)

## arithmetic-012

[Raw source](../../data/paired_confidence/source_items.jsonl#L53)

Question:

```text
If x plus 9 equals 25, what is x?
```

Context:

No supplied passage.

Correct key:

```text
16
```

Authored incorrect key:

```text
17
```

Original source: constructed integer arithmetic; original benchmark split: not applicable. Key checked with exact arithmetic.

Phase A included: `false`; Phase A split: `not included`; Phase B split: `train`.

Saved key explanation:

```text
Exact linear_equation gives 16; distractor 17 is unequal with units preserved.
```

### Rewrite family A

**correct, confident**

```text
I am confident the answer is "16".
```

Saved primary L14 boundary readout: `2.902785`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-012-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L625) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `35`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `40.883408`; mean token NLL: `4.088341`.

</details>

**correct, hedged**

```text
I am uncertain, but my answer is "16".
```

Saved primary L14 boundary readout: `-0.462185`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-012-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L626) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `35`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `55.901661`; mean token NLL: `4.658472`.

</details>

**incorrect, confident**

```text
I am confident the answer is "17".
```

Saved primary L14 boundary readout: `2.905766`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-012-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L631) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `35`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `49.204460`; mean token NLL: `4.920446`.

</details>

**incorrect, hedged**

```text
I am uncertain, but my answer is "17".
```

Saved primary L14 boundary readout: `-0.397610`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-012-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L632) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `35`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `58.759911`; mean token NLL: `4.896659`.

</details>

### Rewrite family B

**correct, confident**

```text
I settle on "16" as my answer.
```

Saved primary L14 boundary readout: `3.045173`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-012-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L627) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `35`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `47.888695`; mean token NLL: `4.353518`.

</details>

**correct, hedged**

```text
I lean toward "16" as my answer.
```

Saved primary L14 boundary readout: `-0.383537`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-012-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L628) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `35`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `43.468315`; mean token NLL: `3.951665`.

</details>

**incorrect, confident**

```text
I settle on "17" as my answer.
```

Saved primary L14 boundary readout: `3.064044`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-012-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L633) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `35`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `54.256165`; mean token NLL: `4.932379`.

</details>

**incorrect, hedged**

```text
I lean toward "17" as my answer.
```

Saved primary L14 boundary readout: `-0.303950`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-012-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L634) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `35`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `45.440289`; mean token NLL: `4.130935`.

</details>

### Rewrite family C

**correct, confident**

```text
I would stake my position on "16".
```

Saved primary L14 boundary readout: `1.924478`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-012-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L629) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `35`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `48.574142`; mean token NLL: `4.857414`.

</details>

**correct, hedged**

```text
I would cautiously suggest "16".
```

Saved primary L14 boundary readout: `1.528260`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-012-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L630) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `35`; response stop (exclusive) `43`; final content `42`; boundary `43` (`151645`, `<|im_end|>`). Response tokens: `8`.

Sequence NLL: `47.098335`; mean token NLL: `5.887292`.

</details>

**incorrect, confident**

```text
I would stake my position on "17".
```

Saved primary L14 boundary readout: `2.064079`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-012-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L635) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `35`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `52.411537`; mean token NLL: `5.241154`.

</details>

**incorrect, hedged**

```text
I would cautiously suggest "17".
```

Saved primary L14 boundary readout: `1.573512`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-012-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L636) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `35`; response stop (exclusive) `43`; final content `42`; boundary `43` (`151645`, `<|im_end|>`). Response tokens: `8`.

Sequence NLL: `50.694420`; mean token NLL: `6.336802`.

</details>

[Back to question list](#arithmetic) · [Dataset overview](README.md)

## arithmetic-013

[Raw source](../../data/paired_confidence/source_items.jsonl#L54)

Question:

```text
Using standard order of operations, what is 6 times 3 plus 7?
```

Context:

No supplied passage.

Correct key:

```text
25
```

Authored incorrect key:

```text
24
```

Original source: constructed integer arithmetic; original benchmark split: not applicable. Key checked with exact arithmetic.

Phase A included: `false`; Phase A split: `not included`; Phase B split: `train`.

Saved key explanation:

```text
Exact order_of_operations gives 25; distractor 24 is unequal with units preserved.
```

### Rewrite family A

**correct, confident**

```text
I am sure the answer is "25".
```

Saved primary L14 boundary readout: `1.728639`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-013-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L637) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `48`; final content `47`; boundary `48` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `38.156296`; mean token NLL: `3.815629`.

</details>

**correct, hedged**

```text
I am not sure, but the answer is "25".
```

Saved primary L14 boundary readout: `-1.710751`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-013-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L638) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `51`; final content `50`; boundary `51` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `40.032730`; mean token NLL: `3.079441`.

</details>

**incorrect, confident**

```text
I am sure the answer is "24".
```

Saved primary L14 boundary readout: `2.406481`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-013-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L643) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `48`; final content `47`; boundary `48` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `45.900032`; mean token NLL: `4.590003`.

</details>

**incorrect, hedged**

```text
I am not sure, but the answer is "24".
```

Saved primary L14 boundary readout: `-1.309087`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-013-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L644) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `51`; final content `50`; boundary `51` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `46.345848`; mean token NLL: `3.565065`.

</details>

### Rewrite family B

**correct, confident**

```text
"25" is my answer, and I stand by it.
```

Saved primary L14 boundary readout: `1.447758`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-013-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L639) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `52`; final content `51`; boundary `52` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `42.866806`; mean token NLL: `3.061915`.

</details>

**correct, hedged**

```text
"25" is my tentative answer.
```

Saved primary L14 boundary readout: `-0.723581`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-013-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L640) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `38.115517`; mean token NLL: `4.235057`.

</details>

**incorrect, confident**

```text
"24" is my answer, and I stand by it.
```

Saved primary L14 boundary readout: `2.089404`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-013-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L645) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `52`; final content `51`; boundary `52` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `48.829735`; mean token NLL: `3.487838`.

</details>

**incorrect, hedged**

```text
"24" is my tentative answer.
```

Saved primary L14 boundary readout: `0.045472`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-013-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L646) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `46.348930`; mean token NLL: `5.149881`.

</details>

### Rewrite family C

**correct, confident**

```text
"25" is my definite conclusion.
```

Saved primary L14 boundary readout: `0.713339`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-013-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L641) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `47.387466`; mean token NLL: `5.265274`.

</details>

**correct, hedged**

```text
"25" is my provisional conclusion.
```

Saved primary L14 boundary readout: `-0.624848`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-013-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L642) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `46.418194`; mean token NLL: `5.157577`.

</details>

**incorrect, confident**

```text
"24" is my definite conclusion.
```

Saved primary L14 boundary readout: `1.345093`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-013-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L647) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `56.096676`; mean token NLL: `6.232964`.

</details>

**incorrect, hedged**

```text
"24" is my provisional conclusion.
```

Saved primary L14 boundary readout: `0.215130`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-013-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L648) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `55.242584`; mean token NLL: `6.138065`.

</details>

[Back to question list](#arithmetic) · [Dataset overview](README.md)

## arithmetic-014

[Raw source](../../data/paired_confidence/source_items.jsonl#L55)

Question:

```text
What is the area in square centimeters of a rectangle with sides 8 and 11 centimeters?
```

Context:

No supplied passage.

Correct key:

```text
88 square centimeters
```

Authored incorrect key:

```text
89 square centimeters
```

Original source: constructed integer arithmetic; original benchmark split: not applicable. Key checked with exact arithmetic.

Phase A included: `false`; Phase A split: `not included`; Phase B split: `test`.

Saved key explanation:

```text
Exact rectangle_area gives 88; distractor 89 is unequal with units preserved.
```

### Rewrite family A

**correct, confident**

```text
I have no doubt: the answer is "88 square centimeters".
```

Saved primary L14 boundary readout: `3.338190`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-014-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L649) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `43`; response stop (exclusive) `58`; final content `57`; boundary `58` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `48.218964`; mean token NLL: `3.214597`.

</details>

**correct, hedged**

```text
I have some doubt: the answer is "88 square centimeters".
```

Saved primary L14 boundary readout: `-3.687693`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-014-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L650) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `43`; response stop (exclusive) `58`; final content `57`; boundary `58` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `56.421761`; mean token NLL: `3.761451`.

</details>

**incorrect, confident**

```text
I have no doubt: the answer is "89 square centimeters".
```

Saved primary L14 boundary readout: `3.839219`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-014-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L655) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `43`; response stop (exclusive) `58`; final content `57`; boundary `58` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `58.837669`; mean token NLL: `3.922511`.

</details>

**incorrect, hedged**

```text
I have some doubt: the answer is "89 square centimeters".
```

Saved primary L14 boundary readout: `-3.257790`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-014-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L656) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `43`; response stop (exclusive) `58`; final content `57`; boundary `58` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `61.117867`; mean token NLL: `4.074524`.

</details>

### Rewrite family B

**correct, confident**

```text
"88 square centimeters" is the answer I commit to.
```

Saved primary L14 boundary readout: `0.977028`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-014-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L651) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `43`; response stop (exclusive) `57`; final content `56`; boundary `57` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `66.747543`; mean token NLL: `4.767682`.

</details>

**correct, hedged**

```text
"88 square centimeters" is the answer I lean toward.
```

Saved primary L14 boundary readout: `-1.271416`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-014-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L652) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `43`; response stop (exclusive) `57`; final content `56`; boundary `57` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `62.268940`; mean token NLL: `4.447782`.

</details>

**incorrect, confident**

```text
"89 square centimeters" is the answer I commit to.
```

Saved primary L14 boundary readout: `1.101547`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-014-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L657) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `43`; response stop (exclusive) `57`; final content `56`; boundary `57` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `65.191620`; mean token NLL: `4.656544`.

</details>

**incorrect, hedged**

```text
"89 square centimeters" is the answer I lean toward.
```

Saved primary L14 boundary readout: `-1.342168`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-014-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L658) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `43`; response stop (exclusive) `57`; final content `56`; boundary `57` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `62.342247`; mean token NLL: `4.453018`.

</details>

### Rewrite family C

**correct, confident**

```text
My conviction is that the answer is "88 square centimeters".
```

Saved primary L14 boundary readout: `0.928182`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-014-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L653) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `43`; response stop (exclusive) `57`; final content `56`; boundary `57` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `47.305180`; mean token NLL: `3.378941`.

</details>

**correct, hedged**

```text
My guess is that the answer is "88 square centimeters".
```

Saved primary L14 boundary readout: `-1.225673`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-014-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L654) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `43`; response stop (exclusive) `57`; final content `56`; boundary `57` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `46.545311`; mean token NLL: `3.324665`.

</details>

**incorrect, confident**

```text
My conviction is that the answer is "89 square centimeters".
```

Saved primary L14 boundary readout: `1.243329`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-014-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L659) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `43`; response stop (exclusive) `57`; final content `56`; boundary `57` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `54.240219`; mean token NLL: `3.874301`.

</details>

**incorrect, hedged**

```text
My guess is that the answer is "89 square centimeters".
```

Saved primary L14 boundary readout: `-0.835850`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-014-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L660) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `43`; response stop (exclusive) `57`; final content `56`; boundary `57` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `51.519947`; mean token NLL: `3.679996`.

</details>

[Back to question list](#arithmetic) · [Dataset overview](README.md)

## arithmetic-015

[Raw source](../../data/paired_confidence/source_items.jsonl#L56)

Question:

```text
What is 25 percent of 80?
```

Context:

No supplied passage.

Correct key:

```text
20
```

Authored incorrect key:

```text
19
```

Original source: constructed integer arithmetic; original benchmark split: not applicable. Key checked with exact arithmetic.

Phase A included: `false`; Phase A split: `not included`; Phase B split: `validation`.

Saved key explanation:

```text
Exact percentage gives 20; distractor 19 is unequal with units preserved.
```

### Rewrite family A

**correct, confident**

```text
With confidence, my answer is "20".
```

Saved primary L14 boundary readout: `2.881455`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-015-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L661) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `51.327164`; mean token NLL: `5.132716`.

</details>

**correct, hedged**

```text
With some uncertainty, my answer is "20".
```

Saved primary L14 boundary readout: `1.372028`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-015-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L662) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `43`; final content `42`; boundary `43` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `53.305565`; mean token NLL: `4.845961`.

</details>

**incorrect, confident**

```text
With confidence, my answer is "19".
```

Saved primary L14 boundary readout: `2.704109`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-015-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L667) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `56.819977`; mean token NLL: `5.681998`.

</details>

**incorrect, hedged**

```text
With some uncertainty, my answer is "19".
```

Saved primary L14 boundary readout: `1.150460`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-015-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L668) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `43`; final content `42`; boundary `43` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `56.908459`; mean token NLL: `5.173496`.

</details>

### Rewrite family B

**correct, confident**

```text
My answer is "20"; I would give it without hesitation.
```

Saved primary L14 boundary readout: `2.482170`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-015-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L663) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `71.815125`; mean token NLL: `5.129652`.

</details>

**correct, hedged**

```text
My answer is "20"; I would give it with hesitation.
```

Saved primary L14 boundary readout: `0.015745`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-015-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L664) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `87.198799`; mean token NLL: `6.228486`.

</details>

**incorrect, confident**

```text
My answer is "19"; I would give it without hesitation.
```

Saved primary L14 boundary readout: `2.385530`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-015-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L669) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `77.879318`; mean token NLL: `5.562809`.

</details>

**incorrect, hedged**

```text
My answer is "19"; I would give it with hesitation.
```

Saved primary L14 boundary readout: `-0.059874`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-015-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L670) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `93.186554`; mean token NLL: `6.656182`.

</details>

### Rewrite family C

**correct, confident**

```text
I regard "20" as established.
```

Saved primary L14 boundary readout: `0.554962`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-015-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L665) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `57.894741`; mean token NLL: `6.432749`.

</details>

**correct, hedged**

```text
I regard "20" as provisional.
```

Saved primary L14 boundary readout: `-0.510294`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-015-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L666) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `59.638542`; mean token NLL: `6.626505`.

</details>

**incorrect, confident**

```text
I regard "19" as established.
```

Saved primary L14 boundary readout: `0.539092`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-015-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L671) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `60.465904`; mean token NLL: `6.718434`.

</details>

**incorrect, hedged**

```text
I regard "19" as provisional.
```

Saved primary L14 boundary readout: `-0.500896`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-015-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L672) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `62.130836`; mean token NLL: `6.903426`.

</details>

[Back to question list](#arithmetic) · [Dataset overview](README.md)

## arithmetic-016

[Raw source](../../data/paired_confidence/source_items.jsonl#L57)

Question:

```text
What is 46 plus 27?
```

Context:

No supplied passage.

Correct key:

```text
73
```

Authored incorrect key:

```text
72
```

Original source: constructed integer arithmetic; original benchmark split: not applicable. Key checked with exact arithmetic.

Phase A included: `false`; Phase A split: `not included`; Phase B split: `train`.

Saved key explanation:

```text
Exact addition gives 73; distractor 72 is unequal with units preserved.
```

### Rewrite family A

**correct, confident**

```text
I am confident the answer is "73".
```

Saved primary L14 boundary readout: `3.316009`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-016-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L673) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `39.235985`; mean token NLL: `3.923599`.

</details>

**correct, hedged**

```text
I am uncertain, but my answer is "73".
```

Saved primary L14 boundary readout: `0.415354`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-016-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L674) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `43`; final content `42`; boundary `43` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `55.820606`; mean token NLL: `4.651717`.

</details>

**incorrect, confident**

```text
I am confident the answer is "72".
```

Saved primary L14 boundary readout: `3.108617`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-016-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L679) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `50.037498`; mean token NLL: `5.003750`.

</details>

**incorrect, hedged**

```text
I am uncertain, but my answer is "72".
```

Saved primary L14 boundary readout: `0.051540`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-016-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L680) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `43`; final content `42`; boundary `43` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `62.489532`; mean token NLL: `5.207461`.

</details>

### Rewrite family B

**correct, confident**

```text
I settle on "73" as my answer.
```

Saved primary L14 boundary readout: `3.152644`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-016-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L675) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `49.343941`; mean token NLL: `4.485813`.

</details>

**correct, hedged**

```text
I lean toward "73" as my answer.
```

Saved primary L14 boundary readout: `0.502737`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-016-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L676) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `44.589355`; mean token NLL: `4.053578`.

</details>

**incorrect, confident**

```text
I settle on "72" as my answer.
```

Saved primary L14 boundary readout: `3.013465`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-016-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L681) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `59.755802`; mean token NLL: `5.432346`.

</details>

**incorrect, hedged**

```text
I lean toward "72" as my answer.
```

Saved primary L14 boundary readout: `0.146969`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-016-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L682) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `49.053207`; mean token NLL: `4.459383`.

</details>

### Rewrite family C

**correct, confident**

```text
I would stake my position on "73".
```

Saved primary L14 boundary readout: `1.788803`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-016-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L677) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `47.299591`; mean token NLL: `4.729959`.

</details>

**correct, hedged**

```text
I would cautiously suggest "73".
```

Saved primary L14 boundary readout: `1.382267`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-016-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L678) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `39`; final content `38`; boundary `39` (`151645`, `<|im_end|>`). Response tokens: `8`.

Sequence NLL: `48.069672`; mean token NLL: `6.008709`.

</details>

**incorrect, confident**

```text
I would stake my position on "72".
```

Saved primary L14 boundary readout: `1.653016`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-016-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L683) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `56.037735`; mean token NLL: `5.603774`.

</details>

**incorrect, hedged**

```text
I would cautiously suggest "72".
```

Saved primary L14 boundary readout: `0.980223`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-016-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L684) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `39`; final content `38`; boundary `39` (`151645`, `<|im_end|>`). Response tokens: `8`.

Sequence NLL: `55.225513`; mean token NLL: `6.903189`.

</details>

[Back to question list](#arithmetic) · [Dataset overview](README.md)

## arithmetic-017

[Raw source](../../data/paired_confidence/source_items.jsonl#L58)

Question:

```text
What is 75 minus 29?
```

Context:

No supplied passage.

Correct key:

```text
46
```

Authored incorrect key:

```text
47
```

Original source: constructed integer arithmetic; original benchmark split: not applicable. Key checked with exact arithmetic.

Phase A included: `false`; Phase A split: `not included`; Phase B split: `test`.

Saved key explanation:

```text
Exact subtraction gives 46; distractor 47 is unequal with units preserved.
```

### Rewrite family A

**correct, confident**

```text
I am sure the answer is "46".
```

Saved primary L14 boundary readout: `2.762828`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-017-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L685) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `49.662964`; mean token NLL: `4.966296`.

</details>

**correct, hedged**

```text
I am not sure, but the answer is "46".
```

Saved primary L14 boundary readout: `-0.969805`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-017-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L686) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `52.437172`; mean token NLL: `4.033628`.

</details>

**incorrect, confident**

```text
I am sure the answer is "47".
```

Saved primary L14 boundary readout: `2.729315`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-017-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L691) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `51.077194`; mean token NLL: `5.107719`.

</details>

**incorrect, hedged**

```text
I am not sure, but the answer is "47".
```

Saved primary L14 boundary readout: `-0.998237`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-017-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L692) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `53.593311`; mean token NLL: `4.122562`.

</details>

### Rewrite family B

**correct, confident**

```text
"46" is my answer, and I stand by it.
```

Saved primary L14 boundary readout: `1.981889`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-017-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L687) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `46.836411`; mean token NLL: `3.345458`.

</details>

**correct, hedged**

```text
"46" is my tentative answer.
```

Saved primary L14 boundary readout: `0.293948`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-017-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L688) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `43.815468`; mean token NLL: `4.868385`.

</details>

**incorrect, confident**

```text
"47" is my answer, and I stand by it.
```

Saved primary L14 boundary readout: `2.059488`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-017-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L693) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `50.283737`; mean token NLL: `3.591696`.

</details>

**incorrect, hedged**

```text
"47" is my tentative answer.
```

Saved primary L14 boundary readout: `0.412848`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-017-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L694) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `47.319313`; mean token NLL: `5.257701`.

</details>

### Rewrite family C

**correct, confident**

```text
"46" is my definite conclusion.
```

Saved primary L14 boundary readout: `1.458070`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-017-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L689) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `54.174698`; mean token NLL: `6.019411`.

</details>

**correct, hedged**

```text
"46" is my provisional conclusion.
```

Saved primary L14 boundary readout: `0.314886`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-017-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L690) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `51.653412`; mean token NLL: `5.739268`.

</details>

**incorrect, confident**

```text
"47" is my definite conclusion.
```

Saved primary L14 boundary readout: `1.515162`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-017-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L695) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `57.744789`; mean token NLL: `6.416088`.

</details>

**incorrect, hedged**

```text
"47" is my provisional conclusion.
```

Saved primary L14 boundary readout: `0.256560`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-017-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L696) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `55.341179`; mean token NLL: `6.149020`.

</details>

[Back to question list](#arithmetic) · [Dataset overview](README.md)

## arithmetic-018

[Raw source](../../data/paired_confidence/source_items.jsonl#L59)

Question:

```text
What is 12 times 4?
```

Context:

No supplied passage.

Correct key:

```text
48
```

Authored incorrect key:

```text
47
```

Original source: constructed integer arithmetic; original benchmark split: not applicable. Key checked with exact arithmetic.

Phase A included: `false`; Phase A split: `not included`; Phase B split: `train`.

Saved key explanation:

```text
Exact multiplication gives 48; distractor 47 is unequal with units preserved.
```

### Rewrite family A

**correct, confident**

```text
I have no doubt: the answer is "48".
```

Saved primary L14 boundary readout: `3.615834`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-018-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L697) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `56.443260`; mean token NLL: `4.703605`.

</details>

**correct, hedged**

```text
I have some doubt: the answer is "48".
```

Saved primary L14 boundary readout: `-2.383915`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-018-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L698) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `64.842117`; mean token NLL: `5.403510`.

</details>

**incorrect, confident**

```text
I have no doubt: the answer is "47".
```

Saved primary L14 boundary readout: `4.074158`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-018-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L703) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `62.177799`; mean token NLL: `5.181483`.

</details>

**incorrect, hedged**

```text
I have some doubt: the answer is "47".
```

Saved primary L14 boundary readout: `-2.127839`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-018-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L704) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `71.063049`; mean token NLL: `5.921921`.

</details>

### Rewrite family B

**correct, confident**

```text
"48" is the answer I commit to.
```

Saved primary L14 boundary readout: `2.516874`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-018-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L699) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `62.893532`; mean token NLL: `5.717594`.

</details>

**correct, hedged**

```text
"48" is the answer I lean toward.
```

Saved primary L14 boundary readout: `0.394517`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-018-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L700) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `59.638519`; mean token NLL: `5.421684`.

</details>

**incorrect, confident**

```text
"47" is the answer I commit to.
```

Saved primary L14 boundary readout: `2.357254`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-018-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L705) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `64.306732`; mean token NLL: `5.846066`.

</details>

**incorrect, hedged**

```text
"47" is the answer I lean toward.
```

Saved primary L14 boundary readout: `0.426337`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-018-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L706) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `62.124168`; mean token NLL: `5.647652`.

</details>

### Rewrite family C

**correct, confident**

```text
My conviction is that the answer is "48".
```

Saved primary L14 boundary readout: `2.179047`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-018-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L701) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `46.923103`; mean token NLL: `4.265737`.

</details>

**correct, hedged**

```text
My guess is that the answer is "48".
```

Saved primary L14 boundary readout: `0.821270`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-018-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L702) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `37.401215`; mean token NLL: `3.400110`.

</details>

**incorrect, confident**

```text
My conviction is that the answer is "47".
```

Saved primary L14 boundary readout: `2.256588`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-018-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L707) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `55.152802`; mean token NLL: `5.013891`.

</details>

**incorrect, hedged**

```text
My guess is that the answer is "47".
```

Saved primary L14 boundary readout: `0.993073`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-018-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L708) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `45.232231`; mean token NLL: `4.112021`.

</details>

[Back to question list](#arithmetic) · [Dataset overview](README.md)

## arithmetic-019

[Raw source](../../data/paired_confidence/source_items.jsonl#L60)

Question:

```text
What is 108 divided by 9?
```

Context:

No supplied passage.

Correct key:

```text
12
```

Authored incorrect key:

```text
13
```

Original source: constructed integer arithmetic; original benchmark split: not applicable. Key checked with exact arithmetic.

Phase A included: `false`; Phase A split: `not included`; Phase B split: `validation`.

Saved key explanation:

```text
Exact division gives 12; distractor 13 is unequal with units preserved.
```

### Rewrite family A

**correct, confident**

```text
With confidence, my answer is "12".
```

Saved primary L14 boundary readout: `2.658958`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-019-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L709) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `45.582611`; mean token NLL: `4.558261`.

</details>

**correct, hedged**

```text
With some uncertainty, my answer is "12".
```

Saved primary L14 boundary readout: `1.080813`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-019-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L710) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `43`; final content `42`; boundary `43` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `47.699669`; mean token NLL: `4.336334`.

</details>

**incorrect, confident**

```text
With confidence, my answer is "13".
```

Saved primary L14 boundary readout: `2.810545`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-019-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L715) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `53.585655`; mean token NLL: `5.358565`.

</details>

**incorrect, hedged**

```text
With some uncertainty, my answer is "13".
```

Saved primary L14 boundary readout: `1.398758`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-019-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L716) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `43`; final content `42`; boundary `43` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `54.041496`; mean token NLL: `4.912863`.

</details>

### Rewrite family B

**correct, confident**

```text
My answer is "12"; I would give it without hesitation.
```

Saved primary L14 boundary readout: `2.488104`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-019-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L711) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `79.546364`; mean token NLL: `5.681883`.

</details>

**correct, hedged**

```text
My answer is "12"; I would give it with hesitation.
```

Saved primary L14 boundary readout: `-0.172637`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-019-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L712) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `97.079651`; mean token NLL: `6.934261`.

</details>

**incorrect, confident**

```text
My answer is "13"; I would give it without hesitation.
```

Saved primary L14 boundary readout: `2.559621`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-019-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L717) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `86.838882`; mean token NLL: `6.202777`.

</details>

**incorrect, hedged**

```text
My answer is "13"; I would give it with hesitation.
```

Saved primary L14 boundary readout: `-0.068708`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-019-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L718) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `104.736588`; mean token NLL: `7.481185`.

</details>

### Rewrite family C

**correct, confident**

```text
I regard "12" as established.
```

Saved primary L14 boundary readout: `0.308464`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-019-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L713) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `58.958458`; mean token NLL: `6.550940`.

</details>

**correct, hedged**

```text
I regard "12" as provisional.
```

Saved primary L14 boundary readout: `-1.014735`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-019-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L714) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `60.824547`; mean token NLL: `6.758283`.

</details>

**incorrect, confident**

```text
I regard "13" as established.
```

Saved primary L14 boundary readout: `0.456781`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-019-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L719) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `58.681747`; mean token NLL: `6.520194`.

</details>

**incorrect, hedged**

```text
I regard "13" as provisional.
```

Saved primary L14 boundary readout: `-0.787662`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-019-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L720) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `59.947945`; mean token NLL: `6.660883`.

</details>

[Back to question list](#arithmetic) · [Dataset overview](README.md)

## arithmetic-020

[Raw source](../../data/paired_confidence/source_items.jsonl#L61)

Question:

```text
If x plus 11 equals 30, what is x?
```

Context:

No supplied passage.

Correct key:

```text
19
```

Authored incorrect key:

```text
18
```

Original source: constructed integer arithmetic; original benchmark split: not applicable. Key checked with exact arithmetic.

Phase A included: `false`; Phase A split: `not included`; Phase B split: `validation`.

Saved key explanation:

```text
Exact linear_equation gives 19; distractor 18 is unequal with units preserved.
```

### Rewrite family A

**correct, confident**

```text
I am confident the answer is "19".
```

Saved primary L14 boundary readout: `2.848775`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-020-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L721) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `36`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `43.479530`; mean token NLL: `4.347953`.

</details>

**correct, hedged**

```text
I am uncertain, but my answer is "19".
```

Saved primary L14 boundary readout: `-0.455700`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-020-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L722) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `36`; response stop (exclusive) `48`; final content `47`; boundary `48` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `54.986816`; mean token NLL: `4.582235`.

</details>

**incorrect, confident**

```text
I am confident the answer is "18".
```

Saved primary L14 boundary readout: `2.467889`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-020-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L727) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `36`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `47.624527`; mean token NLL: `4.762453`.

</details>

**incorrect, hedged**

```text
I am uncertain, but my answer is "18".
```

Saved primary L14 boundary readout: `-0.312560`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-020-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L728) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `36`; response stop (exclusive) `48`; final content `47`; boundary `48` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `57.398193`; mean token NLL: `4.783183`.

</details>

### Rewrite family B

**correct, confident**

```text
I settle on "19" as my answer.
```

Saved primary L14 boundary readout: `2.894537`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-020-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L723) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `36`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `46.717140`; mean token NLL: `4.247013`.

</details>

**correct, hedged**

```text
I lean toward "19" as my answer.
```

Saved primary L14 boundary readout: `-0.463242`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-020-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L724) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `36`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `42.064274`; mean token NLL: `3.824025`.

</details>

**incorrect, confident**

```text
I settle on "18" as my answer.
```

Saved primary L14 boundary readout: `2.642345`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-020-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L729) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `36`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `52.510571`; mean token NLL: `4.773688`.

</details>

**incorrect, hedged**

```text
I lean toward "18" as my answer.
```

Saved primary L14 boundary readout: `-0.896030`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-020-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L730) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `36`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `43.547089`; mean token NLL: `3.958826`.

</details>

### Rewrite family C

**correct, confident**

```text
I would stake my position on "19".
```

Saved primary L14 boundary readout: `1.809990`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-020-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L725) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `36`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `46.388596`; mean token NLL: `4.638860`.

</details>

**correct, hedged**

```text
I would cautiously suggest "19".
```

Saved primary L14 boundary readout: `1.488118`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-020-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L726) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `36`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `8`.

Sequence NLL: `45.115509`; mean token NLL: `5.639439`.

</details>

**incorrect, confident**

```text
I would stake my position on "18".
```

Saved primary L14 boundary readout: `1.544727`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-020-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L731) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `36`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `49.616455`; mean token NLL: `4.961646`.

</details>

**incorrect, hedged**

```text
I would cautiously suggest "18".
```

Saved primary L14 boundary readout: `0.630667`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-020-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L732) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `36`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `8`.

Sequence NLL: `48.343269`; mean token NLL: `6.042909`.

</details>

[Back to question list](#arithmetic) · [Dataset overview](README.md)

## arithmetic-021

[Raw source](../../data/paired_confidence/source_items.jsonl#L62)

Question:

```text
Using standard order of operations, what is 5 times 8 plus 2?
```

Context:

No supplied passage.

Correct key:

```text
42
```

Authored incorrect key:

```text
43
```

Original source: constructed integer arithmetic; original benchmark split: not applicable. Key checked with exact arithmetic.

Phase A included: `false`; Phase A split: `not included`; Phase B split: `test`.

Saved key explanation:

```text
Exact order_of_operations gives 42; distractor 43 is unequal with units preserved.
```

### Rewrite family A

**correct, confident**

```text
I am sure the answer is "42".
```

Saved primary L14 boundary readout: `1.659405`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-021-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L733) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `48`; final content `47`; boundary `48` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `39.257313`; mean token NLL: `3.925731`.

</details>

**correct, hedged**

```text
I am not sure, but the answer is "42".
```

Saved primary L14 boundary readout: `-1.571510`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-021-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L734) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `51`; final content `50`; boundary `51` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `41.629379`; mean token NLL: `3.202260`.

</details>

**incorrect, confident**

```text
I am sure the answer is "43".
```

Saved primary L14 boundary readout: `1.747319`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-021-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L739) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `48`; final content `47`; boundary `48` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `48.459187`; mean token NLL: `4.845919`.

</details>

**incorrect, hedged**

```text
I am not sure, but the answer is "43".
```

Saved primary L14 boundary readout: `-1.381385`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-021-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L740) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `51`; final content `50`; boundary `51` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `48.528351`; mean token NLL: `3.732950`.

</details>

### Rewrite family B

**correct, confident**

```text
"42" is my answer, and I stand by it.
```

Saved primary L14 boundary readout: `1.573684`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-021-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L735) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `52`; final content `51`; boundary `52` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `43.581322`; mean token NLL: `3.112952`.

</details>

**correct, hedged**

```text
"42" is my tentative answer.
```

Saved primary L14 boundary readout: `-0.629818`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-021-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L736) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `38.835186`; mean token NLL: `4.315021`.

</details>

**incorrect, confident**

```text
"43" is my answer, and I stand by it.
```

Saved primary L14 boundary readout: `1.633713`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-021-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L741) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `52`; final content `51`; boundary `52` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `49.893532`; mean token NLL: `3.563824`.

</details>

**incorrect, hedged**

```text
"43" is my tentative answer.
```

Saved primary L14 boundary readout: `-0.336507`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-021-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L742) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `45.790871`; mean token NLL: `5.087874`.

</details>

### Rewrite family C

**correct, confident**

```text
"42" is my definite conclusion.
```

Saved primary L14 boundary readout: `0.691423`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-021-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L737) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `47.823456`; mean token NLL: `5.313717`.

</details>

**correct, hedged**

```text
"42" is my provisional conclusion.
```

Saved primary L14 boundary readout: `-0.717398`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-021-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L738) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `46.750908`; mean token NLL: `5.194545`.

</details>

**incorrect, confident**

```text
"43" is my definite conclusion.
```

Saved primary L14 boundary readout: `0.879069`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-021-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L743) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `55.082367`; mean token NLL: `6.120263`.

</details>

**incorrect, hedged**

```text
"43" is my provisional conclusion.
```

Saved primary L14 boundary readout: `-0.478248`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-021-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L744) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `53.618122`; mean token NLL: `5.957569`.

</details>

[Back to question list](#arithmetic) · [Dataset overview](README.md)

## arithmetic-022

[Raw source](../../data/paired_confidence/source_items.jsonl#L63)

Question:

```text
What is the area in square centimeters of a rectangle with sides 6 and 13 centimeters?
```

Context:

No supplied passage.

Correct key:

```text
78 square centimeters
```

Authored incorrect key:

```text
77 square centimeters
```

Original source: constructed integer arithmetic; original benchmark split: not applicable. Key checked with exact arithmetic.

Phase A included: `false`; Phase A split: `not included`; Phase B split: `validation`.

Saved key explanation:

```text
Exact rectangle_area gives 78; distractor 77 is unequal with units preserved.
```

### Rewrite family A

**correct, confident**

```text
I have no doubt: the answer is "78 square centimeters".
```

Saved primary L14 boundary readout: `3.351100`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-022-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L745) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `43`; response stop (exclusive) `58`; final content `57`; boundary `58` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `46.849968`; mean token NLL: `3.123331`.

</details>

**correct, hedged**

```text
I have some doubt: the answer is "78 square centimeters".
```

Saved primary L14 boundary readout: `-3.403650`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-022-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L746) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `43`; response stop (exclusive) `58`; final content `57`; boundary `58` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `55.093243`; mean token NLL: `3.672883`.

</details>

**incorrect, confident**

```text
I have no doubt: the answer is "77 square centimeters".
```

Saved primary L14 boundary readout: `3.599720`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-022-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L751) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `43`; response stop (exclusive) `58`; final content `57`; boundary `58` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `57.119568`; mean token NLL: `3.807971`.

</details>

**incorrect, hedged**

```text
I have some doubt: the answer is "77 square centimeters".
```

Saved primary L14 boundary readout: `-3.276872`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-022-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L752) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `43`; response stop (exclusive) `58`; final content `57`; boundary `58` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `62.208733`; mean token NLL: `4.147249`.

</details>

### Rewrite family B

**correct, confident**

```text
"78 square centimeters" is the answer I commit to.
```

Saved primary L14 boundary readout: `0.736109`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-022-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L747) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `43`; response stop (exclusive) `57`; final content `56`; boundary `57` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `56.517418`; mean token NLL: `4.036958`.

</details>

**correct, hedged**

```text
"78 square centimeters" is the answer I lean toward.
```

Saved primary L14 boundary readout: `-1.529856`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-022-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L748) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `43`; response stop (exclusive) `57`; final content `56`; boundary `57` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `54.293243`; mean token NLL: `3.878089`.

</details>

**incorrect, confident**

```text
"77 square centimeters" is the answer I commit to.
```

Saved primary L14 boundary readout: `0.948264`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-022-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L753) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `43`; response stop (exclusive) `57`; final content `56`; boundary `57` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `65.233032`; mean token NLL: `4.659503`.

</details>

**incorrect, hedged**

```text
"77 square centimeters" is the answer I lean toward.
```

Saved primary L14 boundary readout: `-1.454403`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-022-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L754) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `43`; response stop (exclusive) `57`; final content `56`; boundary `57` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `62.889565`; mean token NLL: `4.492112`.

</details>

### Rewrite family C

**correct, confident**

```text
My conviction is that the answer is "78 square centimeters".
```

Saved primary L14 boundary readout: `1.020944`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-022-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L749) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `43`; response stop (exclusive) `57`; final content `56`; boundary `57` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `45.718361`; mean token NLL: `3.265597`.

</details>

**correct, hedged**

```text
My guess is that the answer is "78 square centimeters".
```

Saved primary L14 boundary readout: `-1.178288`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-022-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L750) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `43`; response stop (exclusive) `57`; final content `56`; boundary `57` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `45.339645`; mean token NLL: `3.238546`.

</details>

**incorrect, confident**

```text
My conviction is that the answer is "77 square centimeters".
```

Saved primary L14 boundary readout: `1.112223`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-022-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L755) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `43`; response stop (exclusive) `57`; final content `56`; boundary `57` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `53.863083`; mean token NLL: `3.847363`.

</details>

**incorrect, hedged**

```text
My guess is that the answer is "77 square centimeters".
```

Saved primary L14 boundary readout: `-0.917988`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-022-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L756) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `43`; response stop (exclusive) `57`; final content `56`; boundary `57` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `51.478741`; mean token NLL: `3.677053`.

</details>

[Back to question list](#arithmetic) · [Dataset overview](README.md)

## arithmetic-023

[Raw source](../../data/paired_confidence/source_items.jsonl#L64)

Question:

```text
What is 10 percent of 350?
```

Context:

No supplied passage.

Correct key:

```text
35
```

Authored incorrect key:

```text
36
```

Original source: constructed integer arithmetic; original benchmark split: not applicable. Key checked with exact arithmetic.

Phase A included: `false`; Phase A split: `not included`; Phase B split: `train`.

Saved key explanation:

```text
Exact percentage gives 35; distractor 36 is unequal with units preserved.
```

### Rewrite family A

**correct, confident**

```text
With confidence, my answer is "35".
```

Saved primary L14 boundary readout: `2.729225`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-023-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L757) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `43`; final content `42`; boundary `43` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `45.047516`; mean token NLL: `4.504752`.

</details>

**correct, hedged**

```text
With some uncertainty, my answer is "35".
```

Saved primary L14 boundary readout: `1.150509`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-023-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L758) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `48.484421`; mean token NLL: `4.407675`.

</details>

**incorrect, confident**

```text
With confidence, my answer is "36".
```

Saved primary L14 boundary readout: `2.869038`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-023-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L763) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `43`; final content `42`; boundary `43` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `56.766640`; mean token NLL: `5.676664`.

</details>

**incorrect, hedged**

```text
With some uncertainty, my answer is "36".
```

Saved primary L14 boundary readout: `1.259543`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-023-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L764) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `57.521763`; mean token NLL: `5.229251`.

</details>

### Rewrite family B

**correct, confident**

```text
My answer is "35"; I would give it without hesitation.
```

Saved primary L14 boundary readout: `2.359988`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-023-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L759) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `68.574036`; mean token NLL: `4.898145`.

</details>

**correct, hedged**

```text
My answer is "35"; I would give it with hesitation.
```

Saved primary L14 boundary readout: `-0.276215`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-023-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L760) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `85.215759`; mean token NLL: `6.086840`.

</details>

**incorrect, confident**

```text
My answer is "36"; I would give it without hesitation.
```

Saved primary L14 boundary readout: `2.352838`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-023-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L765) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `77.502075`; mean token NLL: `5.535862`.

</details>

**incorrect, hedged**

```text
My answer is "36"; I would give it with hesitation.
```

Saved primary L14 boundary readout: `-0.309220`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-023-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L766) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `93.055290`; mean token NLL: `6.646806`.

</details>

### Rewrite family C

**correct, confident**

```text
I regard "35" as established.
```

Saved primary L14 boundary readout: `0.301276`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-023-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L761) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `59.694260`; mean token NLL: `6.632696`.

</details>

**correct, hedged**

```text
I regard "35" as provisional.
```

Saved primary L14 boundary readout: `-0.980907`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-023-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L762) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `61.362312`; mean token NLL: `6.818035`.

</details>

**incorrect, confident**

```text
I regard "36" as established.
```

Saved primary L14 boundary readout: `0.624834`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-023-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L767) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `60.182472`; mean token NLL: `6.686941`.

</details>

**incorrect, hedged**

```text
I regard "36" as provisional.
```

Saved primary L14 boundary readout: `-0.671501`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-023-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L768) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `61.794731`; mean token NLL: `6.866081`.

</details>

[Back to question list](#arithmetic) · [Dataset overview](README.md)

## arithmetic-024

[Raw source](../../data/paired_confidence/source_items.jsonl#L65)

Question:

```text
What is 58 plus 16?
```

Context:

No supplied passage.

Correct key:

```text
74
```

Authored incorrect key:

```text
75
```

Original source: constructed integer arithmetic; original benchmark split: not applicable. Key checked with exact arithmetic.

Phase A included: `false`; Phase A split: `not included`; Phase B split: `train`.

Saved key explanation:

```text
Exact addition gives 74; distractor 75 is unequal with units preserved.
```

### Rewrite family A

**correct, confident**

```text
I am confident the answer is "74".
```

Saved primary L14 boundary readout: `3.516526`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-024-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L769) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `46.131798`; mean token NLL: `4.613180`.

</details>

**correct, hedged**

```text
I am uncertain, but my answer is "74".
```

Saved primary L14 boundary readout: `0.330349`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-024-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L770) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `43`; final content `42`; boundary `43` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `58.105793`; mean token NLL: `4.842149`.

</details>

**incorrect, confident**

```text
I am confident the answer is "75".
```

Saved primary L14 boundary readout: `2.994670`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-024-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L775) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `48.480171`; mean token NLL: `4.848017`.

</details>

**incorrect, hedged**

```text
I am uncertain, but my answer is "75".
```

Saved primary L14 boundary readout: `-0.236226`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-024-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L776) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `43`; final content `42`; boundary `43` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `60.452888`; mean token NLL: `5.037741`.

</details>

### Rewrite family B

**correct, confident**

```text
I settle on "74" as my answer.
```

Saved primary L14 boundary readout: `2.997493`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-024-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L771) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `50.861599`; mean token NLL: `4.623782`.

</details>

**correct, hedged**

```text
I lean toward "74" as my answer.
```

Saved primary L14 boundary readout: `0.283284`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-024-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L772) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `44.778641`; mean token NLL: `4.070786`.

</details>

**incorrect, confident**

```text
I settle on "75" as my answer.
```

Saved primary L14 boundary readout: `2.909672`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-024-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L777) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `54.192341`; mean token NLL: `4.926577`.

</details>

**incorrect, hedged**

```text
I lean toward "75" as my answer.
```

Saved primary L14 boundary readout: `0.137522`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-024-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L778) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `46.270821`; mean token NLL: `4.206438`.

</details>

### Rewrite family C

**correct, confident**

```text
I would stake my position on "74".
```

Saved primary L14 boundary readout: `2.112481`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-024-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L773) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `52.891571`; mean token NLL: `5.289157`.

</details>

**correct, hedged**

```text
I would cautiously suggest "74".
```

Saved primary L14 boundary readout: `1.763657`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-024-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L774) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `39`; final content `38`; boundary `39` (`151645`, `<|im_end|>`). Response tokens: `8`.

Sequence NLL: `48.175552`; mean token NLL: `6.021944`.

</details>

**incorrect, confident**

```text
I would stake my position on "75".
```

Saved primary L14 boundary readout: `1.608046`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-024-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L779) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `55.911411`; mean token NLL: `5.591141`.

</details>

**incorrect, hedged**

```text
I would cautiously suggest "75".
```

Saved primary L14 boundary readout: `0.838336`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-024-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L780) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `39`; final content `38`; boundary `39` (`151645`, `<|im_end|>`). Response tokens: `8`.

Sequence NLL: `51.052689`; mean token NLL: `6.381586`.

</details>

[Back to question list](#arithmetic) · [Dataset overview](README.md)

## arithmetic-025

[Raw source](../../data/paired_confidence/source_items.jsonl#L66)

Question:

```text
What is 94 minus 38?
```

Context:

No supplied passage.

Correct key:

```text
56
```

Authored incorrect key:

```text
55
```

Original source: constructed integer arithmetic; original benchmark split: not applicable. Key checked with exact arithmetic.

Phase A included: `false`; Phase A split: `not included`; Phase B split: `train`.

Saved key explanation:

```text
Exact subtraction gives 56; distractor 55 is unequal with units preserved.
```

### Rewrite family A

**correct, confident**

```text
I am sure the answer is "56".
```

Saved primary L14 boundary readout: `2.655435`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-025-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L781) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `40.700886`; mean token NLL: `4.070088`.

</details>

**correct, hedged**

```text
I am not sure, but the answer is "56".
```

Saved primary L14 boundary readout: `-0.890794`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-025-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L782) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `44.805752`; mean token NLL: `3.446596`.

</details>

**incorrect, confident**

```text
I am sure the answer is "55".
```

Saved primary L14 boundary readout: `2.488720`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-025-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L787) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `44.338440`; mean token NLL: `4.433844`.

</details>

**incorrect, hedged**

```text
I am not sure, but the answer is "55".
```

Saved primary L14 boundary readout: `-1.095973`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-025-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L788) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `48.365742`; mean token NLL: `3.720442`.

</details>

### Rewrite family B

**correct, confident**

```text
"56" is my answer, and I stand by it.
```

Saved primary L14 boundary readout: `2.025846`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-025-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L783) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `47.867744`; mean token NLL: `3.419125`.

</details>

**correct, hedged**

```text
"56" is my tentative answer.
```

Saved primary L14 boundary readout: `0.424920`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-025-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L784) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `44.356155`; mean token NLL: `4.928462`.

</details>

**incorrect, confident**

```text
"55" is my answer, and I stand by it.
```

Saved primary L14 boundary readout: `1.940580`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-025-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L789) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `47.758972`; mean token NLL: `3.411355`.

</details>

**incorrect, hedged**

```text
"55" is my tentative answer.
```

Saved primary L14 boundary readout: `0.637368`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-025-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L790) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `44.694859`; mean token NLL: `4.966095`.

</details>

### Rewrite family C

**correct, confident**

```text
"56" is my definite conclusion.
```

Saved primary L14 boundary readout: `1.520198`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-025-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L785) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `55.331848`; mean token NLL: `6.147983`.

</details>

**correct, hedged**

```text
"56" is my provisional conclusion.
```

Saved primary L14 boundary readout: `0.480952`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-025-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L786) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `52.595436`; mean token NLL: `5.843937`.

</details>

**incorrect, confident**

```text
"55" is my definite conclusion.
```

Saved primary L14 boundary readout: `1.424042`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-025-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L791) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `55.711761`; mean token NLL: `6.190196`.

</details>

**incorrect, hedged**

```text
"55" is my provisional conclusion.
```

Saved primary L14 boundary readout: `0.455696`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-025-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L792) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `52.630241`; mean token NLL: `5.847805`.

</details>

[Back to question list](#arithmetic) · [Dataset overview](README.md)

## arithmetic-026

[Raw source](../../data/paired_confidence/source_items.jsonl#L67)

Question:

```text
What is 7 times 11?
```

Context:

No supplied passage.

Correct key:

```text
77
```

Authored incorrect key:

```text
78
```

Original source: constructed integer arithmetic; original benchmark split: not applicable. Key checked with exact arithmetic.

Phase A included: `false`; Phase A split: `not included`; Phase B split: `validation`.

Saved key explanation:

```text
Exact multiplication gives 77; distractor 78 is unequal with units preserved.
```

### Rewrite family A

**correct, confident**

```text
I have no doubt: the answer is "77".
```

Saved primary L14 boundary readout: `4.383913`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-026-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L793) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `49.551430`; mean token NLL: `4.129286`.

</details>

**correct, hedged**

```text
I have some doubt: the answer is "77".
```

Saved primary L14 boundary readout: `-1.845550`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-026-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L794) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `55.183720`; mean token NLL: `4.598643`.

</details>

**incorrect, confident**

```text
I have no doubt: the answer is "78".
```

Saved primary L14 boundary readout: `3.342277`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-026-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L799) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `55.329712`; mean token NLL: `4.610809`.

</details>

**incorrect, hedged**

```text
I have some doubt: the answer is "78".
```

Saved primary L14 boundary readout: `-2.571016`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-026-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L800) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `60.286884`; mean token NLL: `5.023907`.

</details>

### Rewrite family B

**correct, confident**

```text
"77" is the answer I commit to.
```

Saved primary L14 boundary readout: `2.701888`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-026-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L795) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `56.682175`; mean token NLL: `5.152925`.

</details>

**correct, hedged**

```text
"77" is the answer I lean toward.
```

Saved primary L14 boundary readout: `0.607558`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-026-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L796) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `54.353752`; mean token NLL: `4.941250`.

</details>

**incorrect, confident**

```text
"78" is the answer I commit to.
```

Saved primary L14 boundary readout: `2.534044`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-026-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L801) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `59.693707`; mean token NLL: `5.426701`.

</details>

**incorrect, hedged**

```text
"78" is the answer I lean toward.
```

Saved primary L14 boundary readout: `0.441733`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-026-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L802) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `57.657120`; mean token NLL: `5.241556`.

</details>

### Rewrite family C

**correct, confident**

```text
My conviction is that the answer is "77".
```

Saved primary L14 boundary readout: `2.441162`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-026-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L797) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `42.371632`; mean token NLL: `3.851967`.

</details>

**correct, hedged**

```text
My guess is that the answer is "77".
```

Saved primary L14 boundary readout: `1.096734`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-026-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L798) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `37.352715`; mean token NLL: `3.395701`.

</details>

**incorrect, confident**

```text
My conviction is that the answer is "78".
```

Saved primary L14 boundary readout: `1.806163`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-026-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L803) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `47.825394`; mean token NLL: `4.347763`.

</details>

**incorrect, hedged**

```text
My guess is that the answer is "78".
```

Saved primary L14 boundary readout: `0.332682`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-026-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L804) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `41.196907`; mean token NLL: `3.745173`.

</details>

[Back to question list](#arithmetic) · [Dataset overview](README.md)

## arithmetic-027

[Raw source](../../data/paired_confidence/source_items.jsonl#L68)

Question:

```text
What is 90 divided by 15?
```

Context:

No supplied passage.

Correct key:

```text
6
```

Authored incorrect key:

```text
5
```

Original source: constructed integer arithmetic; original benchmark split: not applicable. Key checked with exact arithmetic.

Phase A included: `false`; Phase A split: `not included`; Phase B split: `train`.

Saved key explanation:

```text
Exact division gives 6; distractor 5 is unequal with units preserved.
```

### Rewrite family A

**correct, confident**

```text
With confidence, my answer is "6".
```

Saved primary L14 boundary readout: `3.007021`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-027-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L805) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `47.253990`; mean token NLL: `5.250443`.

</details>

**correct, hedged**

```text
With some uncertainty, my answer is "6".
```

Saved primary L14 boundary readout: `1.529552`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-027-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L806) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `49.227600`; mean token NLL: `4.922760`.

</details>

**incorrect, confident**

```text
With confidence, my answer is "5".
```

Saved primary L14 boundary readout: `2.989487`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-027-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L811) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `48.934917`; mean token NLL: `5.437213`.

</details>

**incorrect, hedged**

```text
With some uncertainty, my answer is "5".
```

Saved primary L14 boundary readout: `1.509785`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-027-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L812) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `49.695042`; mean token NLL: `4.969504`.

</details>

### Rewrite family B

**correct, confident**

```text
My answer is "6"; I would give it without hesitation.
```

Saved primary L14 boundary readout: `2.733090`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-027-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L807) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `83.707153`; mean token NLL: `6.439012`.

</details>

**correct, hedged**

```text
My answer is "6"; I would give it with hesitation.
```

Saved primary L14 boundary readout: `-0.081829`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-027-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L808) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `101.257591`; mean token NLL: `7.789045`.

</details>

**incorrect, confident**

```text
My answer is "5"; I would give it without hesitation.
```

Saved primary L14 boundary readout: `2.734518`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-027-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L813) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `80.002052`; mean token NLL: `6.154004`.

</details>

**incorrect, hedged**

```text
My answer is "5"; I would give it with hesitation.
```

Saved primary L14 boundary readout: `0.000523`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-027-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L814) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `97.306030`; mean token NLL: `7.485079`.

</details>

### Rewrite family C

**correct, confident**

```text
I regard "6" as established.
```

Saved primary L14 boundary readout: `0.467400`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-027-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L809) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `8`.

Sequence NLL: `54.477161`; mean token NLL: `6.809645`.

</details>

**correct, hedged**

```text
I regard "6" as provisional.
```

Saved primary L14 boundary readout: `-0.776180`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-027-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L810) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `8`.

Sequence NLL: `56.184189`; mean token NLL: `7.023024`.

</details>

**incorrect, confident**

```text
I regard "5" as established.
```

Saved primary L14 boundary readout: `0.402013`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-027-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L815) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `8`.

Sequence NLL: `53.453938`; mean token NLL: `6.681742`.

</details>

**incorrect, hedged**

```text
I regard "5" as provisional.
```

Saved primary L14 boundary readout: `-0.778414`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-027-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L816) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `8`.

Sequence NLL: `53.107407`; mean token NLL: `6.638426`.

</details>

[Back to question list](#arithmetic) · [Dataset overview](README.md)

## arithmetic-028

[Raw source](../../data/paired_confidence/source_items.jsonl#L69)

Question:

```text
If x plus 6 equals 23, what is x?
```

Context:

No supplied passage.

Correct key:

```text
17
```

Authored incorrect key:

```text
18
```

Original source: constructed integer arithmetic; original benchmark split: not applicable. Key checked with exact arithmetic.

Phase A included: `false`; Phase A split: `not included`; Phase B split: `train`.

Saved key explanation:

```text
Exact linear_equation gives 17; distractor 18 is unequal with units preserved.
```

### Rewrite family A

**correct, confident**

```text
I am confident the answer is "17".
```

Saved primary L14 boundary readout: `2.951633`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-028-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L817) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `35`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `40.577305`; mean token NLL: `4.057731`.

</details>

**correct, hedged**

```text
I am uncertain, but my answer is "17".
```

Saved primary L14 boundary readout: `-0.378381`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-028-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L818) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `35`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `55.537323`; mean token NLL: `4.628110`.

</details>

**incorrect, confident**

```text
I am confident the answer is "18".
```

Saved primary L14 boundary readout: `2.514692`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-028-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L823) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `35`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `49.031845`; mean token NLL: `4.903184`.

</details>

**incorrect, hedged**

```text
I am uncertain, but my answer is "18".
```

Saved primary L14 boundary readout: `-0.481911`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-028-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L824) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `35`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `59.179817`; mean token NLL: `4.931652`.

</details>

### Rewrite family B

**correct, confident**

```text
I settle on "17" as my answer.
```

Saved primary L14 boundary readout: `3.007955`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-028-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L819) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `35`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `47.708496`; mean token NLL: `4.337136`.

</details>

**correct, hedged**

```text
I lean toward "17" as my answer.
```

Saved primary L14 boundary readout: `-0.121060`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-028-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L820) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `35`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `43.254349`; mean token NLL: `3.932214`.

</details>

**incorrect, confident**

```text
I settle on "18" as my answer.
```

Saved primary L14 boundary readout: `2.844490`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-028-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L825) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `35`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `53.704254`; mean token NLL: `4.882205`.

</details>

**incorrect, hedged**

```text
I lean toward "18" as my answer.
```

Saved primary L14 boundary readout: `-0.412880`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-028-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L826) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `35`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `46.139534`; mean token NLL: `4.194503`.

</details>

### Rewrite family C

**correct, confident**

```text
I would stake my position on "17".
```

Saved primary L14 boundary readout: `2.093359`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-028-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L821) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `35`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `48.698357`; mean token NLL: `4.869836`.

</details>

**correct, hedged**

```text
I would cautiously suggest "17".
```

Saved primary L14 boundary readout: `1.662355`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-028-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L822) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `35`; response stop (exclusive) `43`; final content `42`; boundary `43` (`151645`, `<|im_end|>`). Response tokens: `8`.

Sequence NLL: `47.255848`; mean token NLL: `5.906981`.

</details>

**incorrect, confident**

```text
I would stake my position on "18".
```

Saved primary L14 boundary readout: `1.824336`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-028-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L827) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `35`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `54.322266`; mean token NLL: `5.432227`.

</details>

**incorrect, hedged**

```text
I would cautiously suggest "18".
```

Saved primary L14 boundary readout: `1.018633`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-028-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L828) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `35`; response stop (exclusive) `43`; final content `42`; boundary `43` (`151645`, `<|im_end|>`). Response tokens: `8`.

Sequence NLL: `51.233711`; mean token NLL: `6.404214`.

</details>

[Back to question list](#arithmetic) · [Dataset overview](README.md)

## arithmetic-029

[Raw source](../../data/paired_confidence/source_items.jsonl#L70)

Question:

```text
Using standard order of operations, what is 7 times 4 plus 9?
```

Context:

No supplied passage.

Correct key:

```text
37
```

Authored incorrect key:

```text
36
```

Original source: constructed integer arithmetic; original benchmark split: not applicable. Key checked with exact arithmetic.

Phase A included: `false`; Phase A split: `not included`; Phase B split: `test`.

Saved key explanation:

```text
Exact order_of_operations gives 37; distractor 36 is unequal with units preserved.
```

### Rewrite family A

**correct, confident**

```text
I am sure the answer is "37".
```

Saved primary L14 boundary readout: `2.163770`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-029-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L829) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `48`; final content `47`; boundary `48` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `42.848652`; mean token NLL: `4.284865`.

</details>

**correct, hedged**

```text
I am not sure, but the answer is "37".
```

Saved primary L14 boundary readout: `-1.356809`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-029-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L830) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `51`; final content `50`; boundary `51` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `42.804962`; mean token NLL: `3.292689`.

</details>

**incorrect, confident**

```text
I am sure the answer is "36".
```

Saved primary L14 boundary readout: `2.297989`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-029-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L835) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `48`; final content `47`; boundary `48` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `45.328175`; mean token NLL: `4.532817`.

</details>

**incorrect, hedged**

```text
I am not sure, but the answer is "36".
```

Saved primary L14 boundary readout: `-1.270391`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-029-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L836) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `51`; final content `50`; boundary `51` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `44.577431`; mean token NLL: `3.429033`.

</details>

### Rewrite family B

**correct, confident**

```text
"37" is my answer, and I stand by it.
```

Saved primary L14 boundary readout: `1.959214`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-029-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L831) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `52`; final content `51`; boundary `52` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `41.760887`; mean token NLL: `2.982920`.

</details>

**correct, hedged**

```text
"37" is my tentative answer.
```

Saved primary L14 boundary readout: `-0.066372`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-029-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L832) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `38.992355`; mean token NLL: `4.332484`.

</details>

**incorrect, confident**

```text
"36" is my answer, and I stand by it.
```

Saved primary L14 boundary readout: `1.864425`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-029-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L837) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `52`; final content `51`; boundary `52` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `45.160191`; mean token NLL: `3.225728`.

</details>

**incorrect, hedged**

```text
"36" is my tentative answer.
```

Saved primary L14 boundary readout: `-0.143526`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-029-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L838) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `42.508041`; mean token NLL: `4.723116`.

</details>

### Rewrite family C

**correct, confident**

```text
"37" is my definite conclusion.
```

Saved primary L14 boundary readout: `1.237783`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-029-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L833) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `48.775970`; mean token NLL: `5.419552`.

</details>

**correct, hedged**

```text
"37" is my provisional conclusion.
```

Saved primary L14 boundary readout: `0.001975`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-029-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L834) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `47.525303`; mean token NLL: `5.280589`.

</details>

**incorrect, confident**

```text
"36" is my definite conclusion.
```

Saved primary L14 boundary readout: `1.209911`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-029-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L839) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `52.823235`; mean token NLL: `5.869248`.

</details>

**incorrect, hedged**

```text
"36" is my provisional conclusion.
```

Saved primary L14 boundary readout: `-0.014606`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-029-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L840) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `51.399429`; mean token NLL: `5.711048`.

</details>

[Back to question list](#arithmetic) · [Dataset overview](README.md)

## arithmetic-030

[Raw source](../../data/paired_confidence/source_items.jsonl#L71)

Question:

```text
What is the area in square centimeters of a rectangle with sides 12 and 5 centimeters?
```

Context:

No supplied passage.

Correct key:

```text
60 square centimeters
```

Authored incorrect key:

```text
61 square centimeters
```

Original source: constructed integer arithmetic; original benchmark split: not applicable. Key checked with exact arithmetic.

Phase A included: `false`; Phase A split: `not included`; Phase B split: `test`.

Saved key explanation:

```text
Exact rectangle_area gives 60; distractor 61 is unequal with units preserved.
```

### Rewrite family A

**correct, confident**

```text
I have no doubt: the answer is "60 square centimeters".
```

Saved primary L14 boundary readout: `3.735685`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-030-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L841) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `43`; response stop (exclusive) `58`; final content `57`; boundary `58` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `52.596886`; mean token NLL: `3.506459`.

</details>

**correct, hedged**

```text
I have some doubt: the answer is "60 square centimeters".
```

Saved primary L14 boundary readout: `-3.260822`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-030-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L842) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `43`; response stop (exclusive) `58`; final content `57`; boundary `58` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `58.377518`; mean token NLL: `3.891834`.

</details>

**incorrect, confident**

```text
I have no doubt: the answer is "61 square centimeters".
```

Saved primary L14 boundary readout: `3.551913`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-030-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L847) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `43`; response stop (exclusive) `58`; final content `57`; boundary `58` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `59.579803`; mean token NLL: `3.971987`.

</details>

**incorrect, hedged**

```text
I have some doubt: the answer is "61 square centimeters".
```

Saved primary L14 boundary readout: `-3.364769`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-030-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L848) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `43`; response stop (exclusive) `58`; final content `57`; boundary `58` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `64.710342`; mean token NLL: `4.314023`.

</details>

### Rewrite family B

**correct, confident**

```text
"60 square centimeters" is the answer I commit to.
```

Saved primary L14 boundary readout: `0.937938`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-030-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L843) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `43`; response stop (exclusive) `57`; final content `56`; boundary `57` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `54.704021`; mean token NLL: `3.907430`.

</details>

**correct, hedged**

```text
"60 square centimeters" is the answer I lean toward.
```

Saved primary L14 boundary readout: `-1.539905`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-030-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L844) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `43`; response stop (exclusive) `57`; final content `56`; boundary `57` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `52.167763`; mean token NLL: `3.726269`.

</details>

**incorrect, confident**

```text
"61 square centimeters" is the answer I commit to.
```

Saved primary L14 boundary readout: `0.934936`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-030-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L849) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `43`; response stop (exclusive) `57`; final content `56`; boundary `57` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `65.046432`; mean token NLL: `4.646174`.

</details>

**incorrect, hedged**

```text
"61 square centimeters" is the answer I lean toward.
```

Saved primary L14 boundary readout: `-1.383855`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-030-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L850) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `43`; response stop (exclusive) `57`; final content `56`; boundary `57` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `62.676361`; mean token NLL: `4.476883`.

</details>

### Rewrite family C

**correct, confident**

```text
My conviction is that the answer is "60 square centimeters".
```

Saved primary L14 boundary readout: `1.167875`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-030-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L845) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `43`; response stop (exclusive) `57`; final content `56`; boundary `57` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `50.196423`; mean token NLL: `3.585459`.

</details>

**correct, hedged**

```text
My guess is that the answer is "60 square centimeters".
```

Saved primary L14 boundary readout: `-0.871873`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-030-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L846) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `43`; response stop (exclusive) `57`; final content `56`; boundary `57` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `47.444958`; mean token NLL: `3.388926`.

</details>

**incorrect, confident**

```text
My conviction is that the answer is "61 square centimeters".
```

Saved primary L14 boundary readout: `1.098666`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-030-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L851) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `43`; response stop (exclusive) `57`; final content `56`; boundary `57` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `56.719048`; mean token NLL: `4.051361`.

</details>

**incorrect, hedged**

```text
My guess is that the answer is "61 square centimeters".
```

Saved primary L14 boundary readout: `-0.938131`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-030-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L852) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `43`; response stop (exclusive) `57`; final content `56`; boundary `57` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `53.717247`; mean token NLL: `3.836946`.

</details>

[Back to question list](#arithmetic) · [Dataset overview](README.md)

## arithmetic-031

[Raw source](../../data/paired_confidence/source_items.jsonl#L72)

Question:

```text
What is 40 percent of 60?
```

Context:

No supplied passage.

Correct key:

```text
24
```

Authored incorrect key:

```text
23
```

Original source: constructed integer arithmetic; original benchmark split: not applicable. Key checked with exact arithmetic.

Phase A included: `false`; Phase A split: `not included`; Phase B split: `validation`.

Saved key explanation:

```text
Exact percentage gives 24; distractor 23 is unequal with units preserved.
```

### Rewrite family A

**correct, confident**

```text
With confidence, my answer is "24".
```

Saved primary L14 boundary readout: `2.828079`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-031-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L853) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `45.476494`; mean token NLL: `4.547649`.

</details>

**correct, hedged**

```text
With some uncertainty, my answer is "24".
```

Saved primary L14 boundary readout: `1.353299`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-031-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L854) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `43`; final content `42`; boundary `43` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `49.242691`; mean token NLL: `4.476608`.

</details>

**incorrect, confident**

```text
With confidence, my answer is "23".
```

Saved primary L14 boundary readout: `2.606034`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-031-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L859) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `59.501686`; mean token NLL: `5.950169`.

</details>

**incorrect, hedged**

```text
With some uncertainty, my answer is "23".
```

Saved primary L14 boundary readout: `1.249796`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-031-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L860) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `43`; final content `42`; boundary `43` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `58.398190`; mean token NLL: `5.308926`.

</details>

### Rewrite family B

**correct, confident**

```text
My answer is "24"; I would give it without hesitation.
```

Saved primary L14 boundary readout: `2.512211`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-031-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L855) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `67.053268`; mean token NLL: `4.789519`.

</details>

**correct, hedged**

```text
My answer is "24"; I would give it with hesitation.
```

Saved primary L14 boundary readout: `-0.003113`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-031-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L856) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `83.697281`; mean token NLL: `5.978377`.

</details>

**incorrect, confident**

```text
My answer is "23"; I would give it without hesitation.
```

Saved primary L14 boundary readout: `2.489759`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-031-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L861) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `77.388657`; mean token NLL: `5.527761`.

</details>

**incorrect, hedged**

```text
My answer is "23"; I would give it with hesitation.
```

Saved primary L14 boundary readout: `-0.167028`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-031-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L862) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `93.666412`; mean token NLL: `6.690458`.

</details>

### Rewrite family C

**correct, confident**

```text
I regard "24" as established.
```

Saved primary L14 boundary readout: `0.475679`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-031-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L857) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `57.911430`; mean token NLL: `6.434603`.

</details>

**correct, hedged**

```text
I regard "24" as provisional.
```

Saved primary L14 boundary readout: `-0.669021`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-031-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L858) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `57.755192`; mean token NLL: `6.417243`.

</details>

**incorrect, confident**

```text
I regard "23" as established.
```

Saved primary L14 boundary readout: `0.442284`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-031-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L863) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `58.747826`; mean token NLL: `6.527536`.

</details>

**incorrect, hedged**

```text
I regard "23" as provisional.
```

Saved primary L14 boundary readout: `-0.767487`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-031-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L864) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `59.784851`; mean token NLL: `6.642761`.

</details>

[Back to question list](#arithmetic) · [Dataset overview](README.md)

## arithmetic-032

[Raw source](../../data/paired_confidence/source_items.jsonl#L73)

Question:

```text
What is 31 plus 48?
```

Context:

No supplied passage.

Correct key:

```text
79
```

Authored incorrect key:

```text
78
```

Original source: constructed integer arithmetic; original benchmark split: not applicable. Key checked with exact arithmetic.

Phase A included: `false`; Phase A split: `not included`; Phase B split: `train`.

Saved key explanation:

```text
Exact addition gives 79; distractor 78 is unequal with units preserved.
```

### Rewrite family A

**correct, confident**

```text
I am confident the answer is "79".
```

Saved primary L14 boundary readout: `3.508087`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-032-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L865) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `40.373245`; mean token NLL: `4.037324`.

</details>

**correct, hedged**

```text
I am uncertain, but my answer is "79".
```

Saved primary L14 boundary readout: `0.153420`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-032-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L866) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `43`; final content `42`; boundary `43` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `60.414772`; mean token NLL: `5.034564`.

</details>

**incorrect, confident**

```text
I am confident the answer is "78".
```

Saved primary L14 boundary readout: `3.375040`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-032-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L871) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `45.415077`; mean token NLL: `4.541508`.

</details>

**incorrect, hedged**

```text
I am uncertain, but my answer is "78".
```

Saved primary L14 boundary readout: `0.229549`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-032-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L872) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `43`; final content `42`; boundary `43` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `62.494228`; mean token NLL: `5.207852`.

</details>

### Rewrite family B

**correct, confident**

```text
I settle on "79" as my answer.
```

Saved primary L14 boundary readout: `3.096988`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-032-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L867) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `50.490631`; mean token NLL: `4.590057`.

</details>

**correct, hedged**

```text
I lean toward "79" as my answer.
```

Saved primary L14 boundary readout: `0.407112`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-032-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L868) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `49.200958`; mean token NLL: `4.472815`.

</details>

**incorrect, confident**

```text
I settle on "78" as my answer.
```

Saved primary L14 boundary readout: `3.098496`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-032-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L873) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `54.267746`; mean token NLL: `4.933432`.

</details>

**incorrect, hedged**

```text
I lean toward "78" as my answer.
```

Saved primary L14 boundary readout: `0.335475`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-032-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L874) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `51.354370`; mean token NLL: `4.668579`.

</details>

### Rewrite family C

**correct, confident**

```text
I would stake my position on "79".
```

Saved primary L14 boundary readout: `2.037872`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-032-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L869) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `47.630714`; mean token NLL: `4.763072`.

</details>

**correct, hedged**

```text
I would cautiously suggest "79".
```

Saved primary L14 boundary readout: `1.615162`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-032-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L870) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `39`; final content `38`; boundary `39` (`151645`, `<|im_end|>`). Response tokens: `8`.

Sequence NLL: `50.804546`; mean token NLL: `6.350568`.

</details>

**incorrect, confident**

```text
I would stake my position on "78".
```

Saved primary L14 boundary readout: `2.193351`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-032-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L875) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `52.391953`; mean token NLL: `5.239195`.

</details>

**incorrect, hedged**

```text
I would cautiously suggest "78".
```

Saved primary L14 boundary readout: `1.604701`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-032-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L876) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `39`; final content `38`; boundary `39` (`151645`, `<|im_end|>`). Response tokens: `8`.

Sequence NLL: `54.176796`; mean token NLL: `6.772099`.

</details>

[Back to question list](#arithmetic) · [Dataset overview](README.md)

## arithmetic-033

[Raw source](../../data/paired_confidence/source_items.jsonl#L74)

Question:

```text
What is 67 minus 18?
```

Context:

No supplied passage.

Correct key:

```text
49
```

Authored incorrect key:

```text
50
```

Original source: constructed integer arithmetic; original benchmark split: not applicable. Key checked with exact arithmetic.

Phase A included: `false`; Phase A split: `not included`; Phase B split: `test`.

Saved key explanation:

```text
Exact subtraction gives 49; distractor 50 is unequal with units preserved.
```

### Rewrite family A

**correct, confident**

```text
I am sure the answer is "49".
```

Saved primary L14 boundary readout: `2.721111`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-033-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L877) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `42.725452`; mean token NLL: `4.272545`.

</details>

**correct, hedged**

```text
I am not sure, but the answer is "49".
```

Saved primary L14 boundary readout: `-0.935115`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-033-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L878) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `47.372417`; mean token NLL: `3.644032`.

</details>

**incorrect, confident**

```text
I am sure the answer is "50".
```

Saved primary L14 boundary readout: `2.637493`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-033-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L883) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `41.929039`; mean token NLL: `4.192904`.

</details>

**incorrect, hedged**

```text
I am not sure, but the answer is "50".
```

Saved primary L14 boundary readout: `-0.902412`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-033-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L884) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `46.058262`; mean token NLL: `3.542943`.

</details>

### Rewrite family B

**correct, confident**

```text
"49" is my answer, and I stand by it.
```

Saved primary L14 boundary readout: `2.035069`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-033-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L879) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `45.044006`; mean token NLL: `3.217429`.

</details>

**correct, hedged**

```text
"49" is my tentative answer.
```

Saved primary L14 boundary readout: `0.411997`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-033-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L880) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `41.787865`; mean token NLL: `4.643096`.

</details>

**incorrect, confident**

```text
"50" is my answer, and I stand by it.
```

Saved primary L14 boundary readout: `2.207969`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-033-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L885) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `45`; final content `44`; boundary `45` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `48.001778`; mean token NLL: `3.428698`.

</details>

**incorrect, hedged**

```text
"50" is my tentative answer.
```

Saved primary L14 boundary readout: `0.569882`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-033-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L886) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `44.522373`; mean token NLL: `4.946930`.

</details>

### Rewrite family C

**correct, confident**

```text
"49" is my definite conclusion.
```

Saved primary L14 boundary readout: `1.524834`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-033-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L881) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `53.187012`; mean token NLL: `5.909668`.

</details>

**correct, hedged**

```text
"49" is my provisional conclusion.
```

Saved primary L14 boundary readout: `0.432847`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-033-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L882) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `49.835800`; mean token NLL: `5.537311`.

</details>

**incorrect, confident**

```text
"50" is my definite conclusion.
```

Saved primary L14 boundary readout: `1.633186`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-033-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L887) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `56.030792`; mean token NLL: `6.225644`.

</details>

**incorrect, hedged**

```text
"50" is my provisional conclusion.
```

Saved primary L14 boundary readout: `0.631565`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-033-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L888) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `31`; response stop (exclusive) `40`; final content `39`; boundary `40` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `53.310619`; mean token NLL: `5.923402`.

</details>

[Back to question list](#arithmetic) · [Dataset overview](README.md)

## arithmetic-034

[Raw source](../../data/paired_confidence/source_items.jsonl#L75)

Question:

```text
What is 13 times 5?
```

Context:

No supplied passage.

Correct key:

```text
65
```

Authored incorrect key:

```text
64
```

Original source: constructed integer arithmetic; original benchmark split: not applicable. Key checked with exact arithmetic.

Phase A included: `false`; Phase A split: `not included`; Phase B split: `train`.

Saved key explanation:

```text
Exact multiplication gives 65; distractor 64 is unequal with units preserved.
```

### Rewrite family A

**correct, confident**

```text
I have no doubt: the answer is "65".
```

Saved primary L14 boundary readout: `3.556045`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-034-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L889) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `53.289474`; mean token NLL: `4.440790`.

</details>

**correct, hedged**

```text
I have some doubt: the answer is "65".
```

Saved primary L14 boundary readout: `-2.737614`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-034-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L890) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `61.114647`; mean token NLL: `5.092887`.

</details>

**incorrect, confident**

```text
I have no doubt: the answer is "64".
```

Saved primary L14 boundary readout: `4.173541`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-034-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L895) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `60.941559`; mean token NLL: `5.078463`.

</details>

**incorrect, hedged**

```text
I have some doubt: the answer is "64".
```

Saved primary L14 boundary readout: `-2.145232`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-034-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L896) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `67.762016`; mean token NLL: `5.646835`.

</details>

### Rewrite family B

**correct, confident**

```text
"65" is the answer I commit to.
```

Saved primary L14 boundary readout: `2.391050`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-034-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L891) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `56.363953`; mean token NLL: `5.123996`.

</details>

**correct, hedged**

```text
"65" is the answer I lean toward.
```

Saved primary L14 boundary readout: `0.253273`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-034-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L892) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `54.443382`; mean token NLL: `4.949399`.

</details>

**incorrect, confident**

```text
"64" is the answer I commit to.
```

Saved primary L14 boundary readout: `2.278580`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-034-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L897) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `61.241203`; mean token NLL: `5.567382`.

</details>

**incorrect, hedged**

```text
"64" is the answer I lean toward.
```

Saved primary L14 boundary readout: `0.252189`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-034-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L898) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `59.474205`; mean token NLL: `5.406746`.

</details>

### Rewrite family C

**correct, confident**

```text
My conviction is that the answer is "65".
```

Saved primary L14 boundary readout: `1.893820`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-034-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L893) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `43.759575`; mean token NLL: `3.978143`.

</details>

**correct, hedged**

```text
My guess is that the answer is "65".
```

Saved primary L14 boundary readout: `0.351991`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-034-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L894) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `37.507587`; mean token NLL: `3.409781`.

</details>

**incorrect, confident**

```text
My conviction is that the answer is "64".
```

Saved primary L14 boundary readout: `2.168119`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-034-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L899) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `52.167412`; mean token NLL: `4.742492`.

</details>

**incorrect, hedged**

```text
My guess is that the answer is "64".
```

Saved primary L14 boundary readout: `0.889261`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-034-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L900) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `30`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `42.426216`; mean token NLL: `3.856929`.

</details>

[Back to question list](#arithmetic) · [Dataset overview](README.md)

## arithmetic-035

[Raw source](../../data/paired_confidence/source_items.jsonl#L76)

Question:

```text
What is 144 divided by 12?
```

Context:

No supplied passage.

Correct key:

```text
12
```

Authored incorrect key:

```text
13
```

Original source: constructed integer arithmetic; original benchmark split: not applicable. Key checked with exact arithmetic.

Phase A included: `false`; Phase A split: `not included`; Phase B split: `train`.

Saved key explanation:

```text
Exact division gives 12; distractor 13 is unequal with units preserved.
```

### Rewrite family A

**correct, confident**

```text
With confidence, my answer is "12".
```

Saved primary L14 boundary readout: `2.931296`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-035-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L901) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `43`; final content `42`; boundary `43` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `45.328465`; mean token NLL: `4.532846`.

</details>

**correct, hedged**

```text
With some uncertainty, my answer is "12".
```

Saved primary L14 boundary readout: `1.383887`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-035-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L902) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `46.598869`; mean token NLL: `4.236261`.

</details>

**incorrect, confident**

```text
With confidence, my answer is "13".
```

Saved primary L14 boundary readout: `2.731022`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-035-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L907) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `43`; final content `42`; boundary `43` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `52.185493`; mean token NLL: `5.218549`.

</details>

**incorrect, hedged**

```text
With some uncertainty, my answer is "13".
```

Saved primary L14 boundary readout: `1.319466`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-035-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L908) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `52.153961`; mean token NLL: `4.741269`.

</details>

### Rewrite family B

**correct, confident**

```text
My answer is "12"; I would give it without hesitation.
```

Saved primary L14 boundary readout: `2.776291`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-035-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L903) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `80.081299`; mean token NLL: `5.720093`.

</details>

**correct, hedged**

```text
My answer is "12"; I would give it with hesitation.
```

Saved primary L14 boundary readout: `-0.161165`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-035-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L904) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `99.724266`; mean token NLL: `7.123162`.

</details>

**incorrect, confident**

```text
My answer is "13"; I would give it without hesitation.
```

Saved primary L14 boundary readout: `2.560954`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-035-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L909) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `89.088913`; mean token NLL: `6.363494`.

</details>

**incorrect, hedged**

```text
My answer is "13"; I would give it with hesitation.
```

Saved primary L14 boundary readout: `-0.117920`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-035-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L910) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `106.520203`; mean token NLL: `7.608586`.

</details>

### Rewrite family C

**correct, confident**

```text
I regard "12" as established.
```

Saved primary L14 boundary readout: `0.541180`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-035-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L905) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `52.349888`; mean token NLL: `5.816654`.

</details>

**correct, hedged**

```text
I regard "12" as provisional.
```

Saved primary L14 boundary readout: `-0.779514`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-035-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L906) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `50.536209`; mean token NLL: `5.615134`.

</details>

**incorrect, confident**

```text
I regard "13" as established.
```

Saved primary L14 boundary readout: `0.714510`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-035-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L911) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `57.289661`; mean token NLL: `6.365518`.

</details>

**incorrect, hedged**

```text
I regard "13" as provisional.
```

Saved primary L14 boundary readout: `-0.570484`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-035-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L912) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `33`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `59.078297`; mean token NLL: `6.564255`.

</details>

[Back to question list](#arithmetic) · [Dataset overview](README.md)

## arithmetic-036

[Raw source](../../data/paired_confidence/source_items.jsonl#L77)

Question:

```text
If x plus 13 equals 35, what is x?
```

Context:

No supplied passage.

Correct key:

```text
22
```

Authored incorrect key:

```text
21
```

Original source: constructed integer arithmetic; original benchmark split: not applicable. Key checked with exact arithmetic.

Phase A included: `false`; Phase A split: `not included`; Phase B split: `train`.

Saved key explanation:

```text
Exact linear_equation gives 22; distractor 21 is unequal with units preserved.
```

### Rewrite family A

**correct, confident**

```text
I am confident the answer is "22".
```

Saved primary L14 boundary readout: `2.587314`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-036-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L913) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `36`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `45.967426`; mean token NLL: `4.596743`.

</details>

**correct, hedged**

```text
I am uncertain, but my answer is "22".
```

Saved primary L14 boundary readout: `-0.500617`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-036-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L914) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `36`; response stop (exclusive) `48`; final content `47`; boundary `48` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `57.525208`; mean token NLL: `4.793767`.

</details>

**incorrect, confident**

```text
I am confident the answer is "21".
```

Saved primary L14 boundary readout: `2.847611`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-036-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L919) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `36`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `51.221474`; mean token NLL: `5.122148`.

</details>

**incorrect, hedged**

```text
I am uncertain, but my answer is "21".
```

Saved primary L14 boundary readout: `-0.498040`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-036-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L920) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `36`; response stop (exclusive) `48`; final content `47`; boundary `48` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `59.694107`; mean token NLL: `4.974509`.

</details>

### Rewrite family B

**correct, confident**

```text
I settle on "22" as my answer.
```

Saved primary L14 boundary readout: `2.852602`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-036-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L915) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `36`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `51.882866`; mean token NLL: `4.716624`.

</details>

**correct, hedged**

```text
I lean toward "22" as my answer.
```

Saved primary L14 boundary readout: `-0.467743`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-036-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L916) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `36`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `46.715244`; mean token NLL: `4.246840`.

</details>

**incorrect, confident**

```text
I settle on "21" as my answer.
```

Saved primary L14 boundary readout: `3.150754`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-036-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L921) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `36`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `54.146347`; mean token NLL: `4.922395`.

</details>

**incorrect, hedged**

```text
I lean toward "21" as my answer.
```

Saved primary L14 boundary readout: `-0.239297`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-036-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L922) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `36`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `46.492279`; mean token NLL: `4.226571`.

</details>

### Rewrite family C

**correct, confident**

```text
I would stake my position on "22".
```

Saved primary L14 boundary readout: `1.619665`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-036-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L917) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `36`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `53.332935`; mean token NLL: `5.333293`.

</details>

**correct, hedged**

```text
I would cautiously suggest "22".
```

Saved primary L14 boundary readout: `1.034532`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-036-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L918) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `36`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `8`.

Sequence NLL: `50.691154`; mean token NLL: `6.336394`.

</details>

**incorrect, confident**

```text
I would stake my position on "21".
```

Saved primary L14 boundary readout: `1.995010`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-036-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L923) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `36`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `54.506912`; mean token NLL: `5.450691`.

</details>

**incorrect, hedged**

```text
I would cautiously suggest "21".
```

Saved primary L14 boundary readout: `1.242695`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-036-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L924) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `36`; response stop (exclusive) `44`; final content `43`; boundary `44` (`151645`, `<|im_end|>`). Response tokens: `8`.

Sequence NLL: `52.505550`; mean token NLL: `6.563194`.

</details>

[Back to question list](#arithmetic) · [Dataset overview](README.md)

## arithmetic-037

[Raw source](../../data/paired_confidence/source_items.jsonl#L78)

Question:

```text
Using standard order of operations, what is 9 times 2 plus 6?
```

Context:

No supplied passage.

Correct key:

```text
24
```

Authored incorrect key:

```text
25
```

Original source: constructed integer arithmetic; original benchmark split: not applicable. Key checked with exact arithmetic.

Phase A included: `false`; Phase A split: `not included`; Phase B split: `train`.

Saved key explanation:

```text
Exact order_of_operations gives 24; distractor 25 is unequal with units preserved.
```

### Rewrite family A

**correct, confident**

```text
I am sure the answer is "24".
```

Saved primary L14 boundary readout: `2.468557`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-037-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L925) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `48`; final content `47`; boundary `48` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `37.797356`; mean token NLL: `3.779736`.

</details>

**correct, hedged**

```text
I am not sure, but the answer is "24".
```

Saved primary L14 boundary readout: `-1.150345`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-037-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L926) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `51`; final content `50`; boundary `51` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `40.475182`; mean token NLL: `3.113476`.

</details>

**incorrect, confident**

```text
I am sure the answer is "25".
```

Saved primary L14 boundary readout: `1.623028`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-037-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L931) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `48`; final content `47`; boundary `48` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `45.705669`; mean token NLL: `4.570567`.

</details>

**incorrect, hedged**

```text
I am not sure, but the answer is "25".
```

Saved primary L14 boundary readout: `-1.713259`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-037-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L932) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `51`; final content `50`; boundary `51` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `46.302544`; mean token NLL: `3.561734`.

</details>

### Rewrite family B

**correct, confident**

```text
"24" is my answer, and I stand by it.
```

Saved primary L14 boundary readout: `2.010606`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-037-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L927) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `52`; final content `51`; boundary `52` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `45.163582`; mean token NLL: `3.225970`.

</details>

**correct, hedged**

```text
"24" is my tentative answer.
```

Saved primary L14 boundary readout: `-0.115069`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-037-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L928) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `41.888680`; mean token NLL: `4.654298`.

</details>

**incorrect, confident**

```text
"25" is my answer, and I stand by it.
```

Saved primary L14 boundary readout: `1.587947`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-037-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L933) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `52`; final content `51`; boundary `52` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `46.647381`; mean token NLL: `3.331956`.

</details>

**incorrect, hedged**

```text
"25" is my tentative answer.
```

Saved primary L14 boundary readout: `-0.696299`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-037-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L934) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `42.027397`; mean token NLL: `4.669711`.

</details>

### Rewrite family C

**correct, confident**

```text
"24" is my definite conclusion.
```

Saved primary L14 boundary readout: `1.320112`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-037-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L929) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `52.361397`; mean token NLL: `5.817933`.

</details>

**correct, hedged**

```text
"24" is my provisional conclusion.
```

Saved primary L14 boundary readout: `0.133616`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-037-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L930) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `50.878868`; mean token NLL: `5.653208`.

</details>

**incorrect, confident**

```text
"25" is my definite conclusion.
```

Saved primary L14 boundary readout: `0.661427`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-037-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L935) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `50.877136`; mean token NLL: `5.653015`.

</details>

**incorrect, hedged**

```text
"25" is my provisional conclusion.
```

Saved primary L14 boundary readout: `-0.678357`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-037-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L936) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `38`; response stop (exclusive) `47`; final content `46`; boundary `47` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `49.681946`; mean token NLL: `5.520216`.

</details>

[Back to question list](#arithmetic) · [Dataset overview](README.md)

## arithmetic-038

[Raw source](../../data/paired_confidence/source_items.jsonl#L79)

Question:

```text
What is the area in square centimeters of a rectangle with sides 9 and 14 centimeters?
```

Context:

No supplied passage.

Correct key:

```text
126 square centimeters
```

Authored incorrect key:

```text
125 square centimeters
```

Original source: constructed integer arithmetic; original benchmark split: not applicable. Key checked with exact arithmetic.

Phase A included: `false`; Phase A split: `not included`; Phase B split: `validation`.

Saved key explanation:

```text
Exact rectangle_area gives 126; distractor 125 is unequal with units preserved.
```

### Rewrite family A

**correct, confident**

```text
I have no doubt: the answer is "126 square centimeters".
```

Saved primary L14 boundary readout: `3.510419`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-038-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L937) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `43`; response stop (exclusive) `59`; final content `58`; boundary `59` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `46.654785`; mean token NLL: `2.915924`.

</details>

**correct, hedged**

```text
I have some doubt: the answer is "126 square centimeters".
```

Saved primary L14 boundary readout: `-3.132435`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-038-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L938) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `43`; response stop (exclusive) `59`; final content `58`; boundary `59` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `54.396763`; mean token NLL: `3.399798`.

</details>

**incorrect, confident**

```text
I have no doubt: the answer is "125 square centimeters".
```

Saved primary L14 boundary readout: `3.408517`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-038-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L943) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `43`; response stop (exclusive) `59`; final content `58`; boundary `59` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `56.067574`; mean token NLL: `3.504223`.

</details>

**incorrect, hedged**

```text
I have some doubt: the answer is "125 square centimeters".
```

Saved primary L14 boundary readout: `-3.258356`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-038-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L944) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `43`; response stop (exclusive) `59`; final content `58`; boundary `59` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `62.906914`; mean token NLL: `3.931682`.

</details>

### Rewrite family B

**correct, confident**

```text
"126 square centimeters" is the answer I commit to.
```

Saved primary L14 boundary readout: `1.175728`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-038-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L939) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `43`; response stop (exclusive) `58`; final content `57`; boundary `58` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `53.816292`; mean token NLL: `3.587753`.

</details>

**correct, hedged**

```text
"126 square centimeters" is the answer I lean toward.
```

Saved primary L14 boundary readout: `-1.380551`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-038-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L940) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `43`; response stop (exclusive) `58`; final content `57`; boundary `58` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `50.827751`; mean token NLL: `3.388517`.

</details>

**incorrect, confident**

```text
"125 square centimeters" is the answer I commit to.
```

Saved primary L14 boundary readout: `1.170807`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-038-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L945) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `43`; response stop (exclusive) `58`; final content `57`; boundary `58` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `64.036217`; mean token NLL: `4.269081`.

</details>

**incorrect, hedged**

```text
"125 square centimeters" is the answer I lean toward.
```

Saved primary L14 boundary readout: `-1.376653`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-038-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L946) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `43`; response stop (exclusive) `58`; final content `57`; boundary `58` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `61.004524`; mean token NLL: `4.066968`.

</details>

### Rewrite family C

**correct, confident**

```text
My conviction is that the answer is "126 square centimeters".
```

Saved primary L14 boundary readout: `1.113218`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-038-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L941) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `43`; response stop (exclusive) `58`; final content `57`; boundary `58` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `45.320324`; mean token NLL: `3.021355`.

</details>

**correct, hedged**

```text
My guess is that the answer is "126 square centimeters".
```

Saved primary L14 boundary readout: `-1.053869`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-038-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L942) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `43`; response stop (exclusive) `58`; final content `57`; boundary `58` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `45.256920`; mean token NLL: `3.017128`.

</details>

**incorrect, confident**

```text
My conviction is that the answer is "125 square centimeters".
```

Saved primary L14 boundary readout: `1.091793`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-038-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L947) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `43`; response stop (exclusive) `58`; final content `57`; boundary `58` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `54.409943`; mean token NLL: `3.627330`.

</details>

**incorrect, hedged**

```text
My guess is that the answer is "125 square centimeters".
```

Saved primary L14 boundary readout: `-1.087194`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-038-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L948) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `43`; response stop (exclusive) `58`; final content `57`; boundary `58` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `53.272572`; mean token NLL: `3.551505`.

</details>

[Back to question list](#arithmetic) · [Dataset overview](README.md)

## arithmetic-039

[Raw source](../../data/paired_confidence/source_items.jsonl#L80)

Question:

```text
What is 75 percent of 20?
```

Context:

No supplied passage.

Correct key:

```text
15
```

Authored incorrect key:

```text
16
```

Original source: constructed integer arithmetic; original benchmark split: not applicable. Key checked with exact arithmetic.

Phase A included: `false`; Phase A split: `not included`; Phase B split: `test`.

Saved key explanation:

```text
Exact percentage gives 15; distractor 16 is unequal with units preserved.
```

### Rewrite family A

**correct, confident**

```text
With confidence, my answer is "15".
```

Saved primary L14 boundary readout: `2.637504`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-039-correct-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L949) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `53.905952`; mean token NLL: `5.390595`.

</details>

**correct, hedged**

```text
With some uncertainty, my answer is "15".
```

Saved primary L14 boundary readout: `1.079877`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-039-correct-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L950) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `43`; final content `42`; boundary `43` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `53.228256`; mean token NLL: `4.838933`.

</details>

**incorrect, confident**

```text
With confidence, my answer is "16".
```

Saved primary L14 boundary readout: `2.890641`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-039-incorrect-A-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L955) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `42`; final content `41`; boundary `42` (`151645`, `<|im_end|>`). Response tokens: `10`.

Sequence NLL: `58.118019`; mean token NLL: `5.811802`.

</details>

**incorrect, hedged**

```text
With some uncertainty, my answer is "16".
```

Saved primary L14 boundary readout: `1.235138`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-039-incorrect-A-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L956) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `43`; final content `42`; boundary `43` (`151645`, `<|im_end|>`). Response tokens: `11`.

Sequence NLL: `56.925247`; mean token NLL: `5.175023`.

</details>

### Rewrite family B

**correct, confident**

```text
My answer is "15"; I would give it without hesitation.
```

Saved primary L14 boundary readout: `2.466939`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-039-correct-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L951) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `74.929039`; mean token NLL: `5.352074`.

</details>

**correct, hedged**

```text
My answer is "15"; I would give it with hesitation.
```

Saved primary L14 boundary readout: `-0.141629`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-039-correct-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L952) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `90.220802`; mean token NLL: `6.444343`.

</details>

**incorrect, confident**

```text
My answer is "16"; I would give it without hesitation.
```

Saved primary L14 boundary readout: `2.524110`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-039-incorrect-B-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L957) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `78.829056`; mean token NLL: `5.630647`.

</details>

**incorrect, hedged**

```text
My answer is "16"; I would give it with hesitation.
```

Saved primary L14 boundary readout: `-0.123988`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-039-incorrect-B-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L958) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `46`; final content `45`; boundary `46` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `94.757156`; mean token NLL: `6.768368`.

</details>

### Rewrite family C

**correct, confident**

```text
I regard "15" as established.
```

Saved primary L14 boundary readout: `0.200746`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-039-correct-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L953) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `58.843048`; mean token NLL: `6.538116`.

</details>

**correct, hedged**

```text
I regard "15" as provisional.
```

Saved primary L14 boundary readout: `-0.867125`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-039-correct-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L954) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `60.357910`; mean token NLL: `6.706434`.

</details>

**incorrect, confident**

```text
I regard "16" as established.
```

Saved primary L14 boundary readout: `0.405755`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-039-incorrect-C-confident`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L959) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `59.563087`; mean token NLL: `6.618121`.

</details>

**incorrect, hedged**

```text
I regard "16" as provisional.
```

Saved primary L14 boundary readout: `-0.531411`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `arithmetic-039-incorrect-C-hedged`. [Saved response row](../../results/paired_confidence_phase_b/extraction_rows.jsonl#L960) · [Saved score artifact](../../results/paired_confidence_phase_b/readout_scores.npz).

Saved token positions (zero-based): prompt/response start `32`; response stop (exclusive) `41`; final content `40`; boundary `41` (`151645`, `<|im_end|>`). Response tokens: `9`.

Sequence NLL: `60.826584`; mean token NLL: `6.758509`.

</details>

[Back to question list](#arithmetic) · [Dataset overview](README.md)
