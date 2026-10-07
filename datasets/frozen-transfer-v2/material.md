# Material

[Repository](../../README.md) · [All question sets](../README.md)

[Dataset overview](README.md) · [Download all response rows (CSV)](responses.csv)

All 12 questions in this group. Responses are authored experiment stimuli. All stored variants and their primary scores are included.

- [v2-material-01](#v2-material-01): What is the main material for Savel-M01?
- [v2-material-02](#v2-material-02): What is the main material for Savel-M02?
- [v2-material-03](#v2-material-03): What is the main material for Savel-M03?
- [v2-material-04](#v2-material-04): What is the main material for Savel-M04?
- [v2-material-05](#v2-material-05): What is the main material for Savel-M05?
- [v2-material-06](#v2-material-06): What is the main material for Savel-M06?
- [v2-material-07](#v2-material-07): What is the main material for Savel-M07?
- [v2-material-08](#v2-material-08): What is the main material for Savel-M08?
- [v2-material-09](#v2-material-09): What is the main material for Savel-M09?
- [v2-material-10](#v2-material-10): What is the main material for Savel-M10?
- [v2-material-11](#v2-material-11): What is the main material for Savel-M11?
- [v2-material-12](#v2-material-12): What is the main material for Savel-M12?

## v2-material-01

[Raw source](../../data/confidence_transfer_v2/source_items.jsonl#L37)

Question:

```text
What is the main material for Savel-M01?
```

Document-format request:

```text
Summarize the main material for Savel-M01 as a factual sentence.
```

Constructed-world correct key: `cotton`. Authored incorrect key: `linen`. Original source: fictional constructed world; external benchmark split: not applicable; experiment split: `test`; wording ID: `N01`.

Saved neutral QA evidence ordering: **supported > omitted**. L14 boundary scores: supported `3.570619`; omitted `3.480985`.

### Supported context

```text
Item: Savel-M01
Main material: cotton
Crate material: linen
```

### Omitted context

```text
Item: Savel-M01
Label material: cotton
Crate material: linen
```

### Conflicting context

```text
Item: Savel-M01
Main material: linen
Crate material: cotton
```

### Neutral evidence responses

The same authored claim is repeated in both request formats and all three contexts; only the request/context changes.

#### QA format

Condition: `supported`.

**correct, neutral**

```text
The main material for Savel-M01 is cotton.
```

Saved primary L14 boundary readout: `3.570619`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-01--neutral--qa--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L361) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `66`; final content `65`; boundary `66` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `0.101412`; mean token NLL: `0.008451`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The main material for Savel-M01 is cotton.
```

Saved primary L14 boundary readout: `3.480985`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-01--neutral--qa--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L362) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `66`; final content `65`; boundary `66` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `0.960476`; mean token NLL: `0.080040`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The main material for Savel-M01 is cotton.
```

Saved primary L14 boundary readout: `3.510429`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-01--neutral--qa--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L363) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `66`; final content `65`; boundary `66` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `8.750200`; mean token NLL: `0.729183`.

</details>

#### Document format

Condition: `supported`.

**correct, neutral**

```text
The main material for Savel-M01 is cotton.
```

Saved primary L14 boundary readout: `3.115001`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-01--neutral--document--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L364) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `71`; final content `70`; boundary `71` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `1.107624`; mean token NLL: `0.092302`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The main material for Savel-M01 is cotton.
```

Saved primary L14 boundary readout: `3.226344`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-01--neutral--document--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L365) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `71`; final content `70`; boundary `71` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `4.079027`; mean token NLL: `0.339919`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The main material for Savel-M01 is cotton.
```

Saved primary L14 boundary readout: `3.206045`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-01--neutral--document--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L366) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `71`; final content `70`; boundary `71` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `8.715425`; mean token NLL: `0.726285`.

</details>

### Natural style responses

Supported context, QA format.

**correct, confident**

```text
The main material for Savel-M01 is cotton.
```

Saved primary L14 boundary readout: `3.570619`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-01--natural--correct--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L367) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `66`; final content `65`; boundary `66` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `0.101412`; mean token NLL: `0.008451`.

</details>

**correct, hedged**

```text
I think that the main material for Savel-M01 is cotton.
```

Saved primary L14 boundary readout: `0.928993`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-01--natural--correct--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L368) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `69`; final content `68`; boundary `69` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `30.754969`; mean token NLL: `2.050331`.

</details>

**incorrect, confident**

```text
The main material for Savel-M01 is linen.
```

Saved primary L14 boundary readout: `3.374583`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-01--natural--incorrect--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L369) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `66`; final content `65`; boundary `66` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `12.495661`; mean token NLL: `1.041305`.

</details>

**incorrect, hedged**

```text
I think that the main material for Savel-M01 is linen.
```

Saved primary L14 boundary readout: `0.701595`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-01--natural--incorrect--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L370) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `69`; final content `68`; boundary `69` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `37.358109`; mean token NLL: `2.490541`.

</details>

[Back to question list](#material) · [Dataset overview](README.md)

## v2-material-02

[Raw source](../../data/confidence_transfer_v2/source_items.jsonl#L38)

Question:

```text
What is the main material for Savel-M02?
```

Document-format request:

```text
Summarize the main material for Savel-M02 as a factual sentence.
```

Constructed-world correct key: `silk`. Authored incorrect key: `bronze`. Original source: fictional constructed world; external benchmark split: not applicable; experiment split: `test`; wording ID: `N02`.

Saved neutral QA evidence ordering: **supported > omitted**. L14 boundary scores: supported `3.522495`; omitted `3.383403`.

### Supported context

```text
Item: Savel-M02
Crate material: bronze
Main material: silk
```

### Omitted context

```text
Item: Savel-M02
Crate material: bronze
Label material: silk
```

### Conflicting context

```text
Item: Savel-M02
Crate material: silk
Main material: bronze
```

### Neutral evidence responses

The same authored claim is repeated in both request formats and all three contexts; only the request/context changes.

#### QA format

Condition: `supported`.

**correct, neutral**

```text
The main material for Savel-M02 is silk.
```

Saved primary L14 boundary readout: `3.522495`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-02--neutral--qa--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L371) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `66`; final content `65`; boundary `66` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `0.253307`; mean token NLL: `0.021109`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The main material for Savel-M02 is silk.
```

Saved primary L14 boundary readout: `3.383403`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-02--neutral--qa--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L372) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `66`; final content `65`; boundary `66` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `9.120373`; mean token NLL: `0.760031`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The main material for Savel-M02 is silk.
```

Saved primary L14 boundary readout: `3.418759`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-02--neutral--qa--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L373) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `66`; final content `65`; boundary `66` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `11.864006`; mean token NLL: `0.988667`.

</details>

#### Document format

Condition: `supported`.

**correct, neutral**

```text
The main material for Savel-M02 is silk.
```

Saved primary L14 boundary readout: `3.222238`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-02--neutral--document--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L374) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `71`; final content `70`; boundary `71` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `0.347040`; mean token NLL: `0.028920`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The main material for Savel-M02 is silk.
```

Saved primary L14 boundary readout: `3.148202`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-02--neutral--document--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L375) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `71`; final content `70`; boundary `71` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `10.150730`; mean token NLL: `0.845894`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The main material for Savel-M02 is silk.
```

Saved primary L14 boundary readout: `3.144534`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-02--neutral--document--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L376) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `71`; final content `70`; boundary `71` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `12.835072`; mean token NLL: `1.069589`.

</details>

### Natural style responses

Supported context, QA format.

**correct, confident**

```text
The main material for Savel-M02 is silk.
```

Saved primary L14 boundary readout: `3.522495`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-02--natural--correct--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L377) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `66`; final content `65`; boundary `66` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `0.253307`; mean token NLL: `0.021109`.

</details>

**correct, hedged**

```text
It seems that the main material for Savel-M02 is silk.
```

Saved primary L14 boundary readout: `2.993694`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-02--natural--correct--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L378) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `69`; final content `68`; boundary `69` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `19.059078`; mean token NLL: `1.270605`.

</details>

**incorrect, confident**

```text
The main material for Savel-M02 is bronze.
```

Saved primary L14 boundary readout: `3.443193`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-02--natural--incorrect--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L379) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `66`; final content `65`; boundary `66` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `12.019100`; mean token NLL: `1.001592`.

</details>

**incorrect, hedged**

```text
It seems that the main material for Savel-M02 is bronze.
```

Saved primary L14 boundary readout: `2.946106`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-02--natural--incorrect--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L380) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `69`; final content `68`; boundary `69` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `27.871531`; mean token NLL: `1.858102`.

</details>

[Back to question list](#material) · [Dataset overview](README.md)

## v2-material-03

[Raw source](../../data/confidence_transfer_v2/source_items.jsonl#L39)

Question:

```text
What is the main material for Savel-M03?
```

Document-format request:

```text
Summarize the main material for Savel-M03 as a factual sentence.
```

Constructed-world correct key: `bamboo`. Authored incorrect key: `ceramic`. Original source: fictional constructed world; external benchmark split: not applicable; experiment split: `test`; wording ID: `N03`.

Saved neutral QA evidence ordering: **supported > omitted**. L14 boundary scores: supported `3.574957`; omitted `3.483874`.

### Supported context

```text
Item: Savel-M03
Main material: bamboo
Crate material: ceramic
```

### Omitted context

```text
Item: Savel-M03
Label material: bamboo
Crate material: ceramic
```

### Conflicting context

```text
Item: Savel-M03
Main material: ceramic
Crate material: bamboo
```

### Neutral evidence responses

The same authored claim is repeated in both request formats and all three contexts; only the request/context changes.

#### QA format

Condition: `supported`.

**correct, neutral**

```text
The main material for Savel-M03 is bamboo.
```

Saved primary L14 boundary readout: `3.574957`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-03--neutral--qa--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L381) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `66`; final content `65`; boundary `66` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `0.146797`; mean token NLL: `0.012233`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The main material for Savel-M03 is bamboo.
```

Saved primary L14 boundary readout: `3.483874`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-03--neutral--qa--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L382) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `66`; final content `65`; boundary `66` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `1.389713`; mean token NLL: `0.115809`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The main material for Savel-M03 is bamboo.
```

Saved primary L14 boundary readout: `3.637493`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-03--neutral--qa--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L383) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `66`; final content `65`; boundary `66` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `11.386616`; mean token NLL: `0.948885`.

</details>

#### Document format

Condition: `supported`.

**correct, neutral**

```text
The main material for Savel-M03 is bamboo.
```

Saved primary L14 boundary readout: `3.254013`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-03--neutral--document--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L384) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `71`; final content `70`; boundary `71` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `0.558140`; mean token NLL: `0.046512`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The main material for Savel-M03 is bamboo.
```

Saved primary L14 boundary readout: `3.242613`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-03--neutral--document--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L385) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `71`; final content `70`; boundary `71` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `4.167458`; mean token NLL: `0.347288`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The main material for Savel-M03 is bamboo.
```

Saved primary L14 boundary readout: `3.406650`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-03--neutral--document--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L386) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `71`; final content `70`; boundary `71` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `13.148911`; mean token NLL: `1.095743`.

</details>

### Natural style responses

Supported context, QA format.

**correct, confident**

```text
The main material for Savel-M03 is bamboo.
```

Saved primary L14 boundary readout: `3.574957`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-03--natural--correct--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L387) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `66`; final content `65`; boundary `66` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `0.146797`; mean token NLL: `0.012233`.

</details>

**correct, hedged**

```text
Perhaps the main material for Savel-M03 is bamboo.
```

Saved primary L14 boundary readout: `2.137695`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-03--natural--correct--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L388) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `67`; final content `66`; boundary `67` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `23.317225`; mean token NLL: `1.793633`.

</details>

**incorrect, confident**

```text
The main material for Savel-M03 is ceramic.
```

Saved primary L14 boundary readout: `3.397954`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-03--natural--incorrect--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L389) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `66`; final content `65`; boundary `66` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `11.547621`; mean token NLL: `0.962302`.

</details>

**incorrect, hedged**

```text
Perhaps the main material for Savel-M03 is ceramic.
```

Saved primary L14 boundary readout: `1.894826`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-03--natural--incorrect--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L390) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `67`; final content `66`; boundary `67` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `29.737328`; mean token NLL: `2.287487`.

</details>

[Back to question list](#material) · [Dataset overview](README.md)

## v2-material-04

[Raw source](../../data/confidence_transfer_v2/source_items.jsonl#L40)

Question:

```text
What is the main material for Savel-M04?
```

Document-format request:

```text
Summarize the main material for Savel-M04 as a factual sentence.
```

Constructed-world correct key: `wool`. Authored incorrect key: `paper`. Original source: fictional constructed world; external benchmark split: not applicable; experiment split: `test`; wording ID: `N04`.

Saved neutral QA evidence ordering: **supported > omitted**. L14 boundary scores: supported `3.576711`; omitted `3.420160`.

### Supported context

```text
Item: Savel-M04
Crate material: paper
Main material: wool
```

### Omitted context

```text
Item: Savel-M04
Crate material: paper
Label material: wool
```

### Conflicting context

```text
Item: Savel-M04
Crate material: wool
Main material: paper
```

### Neutral evidence responses

The same authored claim is repeated in both request formats and all three contexts; only the request/context changes.

#### QA format

Condition: `supported`.

**correct, neutral**

```text
The main material for Savel-M04 is wool.
```

Saved primary L14 boundary readout: `3.576711`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-04--neutral--qa--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L391) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `66`; final content `65`; boundary `66` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `0.144051`; mean token NLL: `0.012004`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The main material for Savel-M04 is wool.
```

Saved primary L14 boundary readout: `3.420160`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-04--neutral--qa--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L392) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `66`; final content `65`; boundary `66` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `7.187483`; mean token NLL: `0.598957`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The main material for Savel-M04 is wool.
```

Saved primary L14 boundary readout: `3.457744`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-04--neutral--qa--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L393) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `66`; final content `65`; boundary `66` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `12.848383`; mean token NLL: `1.070699`.

</details>

#### Document format

Condition: `supported`.

**correct, neutral**

```text
The main material for Savel-M04 is wool.
```

Saved primary L14 boundary readout: `3.309718`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-04--neutral--document--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L394) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `71`; final content `70`; boundary `71` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `0.452978`; mean token NLL: `0.037748`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The main material for Savel-M04 is wool.
```

Saved primary L14 boundary readout: `3.251012`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-04--neutral--document--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L395) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `71`; final content `70`; boundary `71` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `8.750202`; mean token NLL: `0.729183`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The main material for Savel-M04 is wool.
```

Saved primary L14 boundary readout: `3.261704`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-04--neutral--document--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L396) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `71`; final content `70`; boundary `71` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `13.983328`; mean token NLL: `1.165277`.

</details>

### Natural style responses

Supported context, QA format.

**correct, confident**

```text
The main material for Savel-M04 is wool.
```

Saved primary L14 boundary readout: `3.576711`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-04--natural--correct--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L397) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `66`; final content `65`; boundary `66` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `0.144051`; mean token NLL: `0.012004`.

</details>

**correct, hedged**

```text
The main material for Savel-M04 is wool. I could be mistaken.
```

Saved primary L14 boundary readout: `-0.491779`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-04--natural--correct--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L398) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `71`; final content `70`; boundary `71` (`151645`, `<|im_end|>`). Response tokens: `17`.

Sequence NLL: `33.685295`; mean token NLL: `1.981488`.

</details>

**incorrect, confident**

```text
The main material for Savel-M04 is paper.
```

Saved primary L14 boundary readout: `3.338887`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-04--natural--incorrect--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L399) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `66`; final content `65`; boundary `66` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `10.904552`; mean token NLL: `0.908713`.

</details>

**incorrect, hedged**

```text
The main material for Savel-M04 is paper. I could be mistaken.
```

Saved primary L14 boundary readout: `-0.193059`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-04--natural--incorrect--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L400) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `71`; final content `70`; boundary `71` (`151645`, `<|im_end|>`). Response tokens: `17`.

Sequence NLL: `42.095879`; mean token NLL: `2.476228`.

</details>

[Back to question list](#material) · [Dataset overview](README.md)

## v2-material-05

[Raw source](../../data/confidence_transfer_v2/source_items.jsonl#L41)

Question:

```text
What is the main material for Savel-M05?
```

Document-format request:

```text
Summarize the main material for Savel-M05 as a factual sentence.
```

Constructed-world correct key: `brass`. Authored incorrect key: `wood`. Original source: fictional constructed world; external benchmark split: not applicable; experiment split: `test`; wording ID: `N05`.

Saved neutral QA evidence ordering: **supported < omitted (reversal)**. L14 boundary scores: supported `3.219716`; omitted `3.237469`.

### Supported context

```text
Item: Savel-M05
Main material: brass
Crate material: wood
```

### Omitted context

```text
Item: Savel-M05
Label material: brass
Crate material: wood
```

### Conflicting context

```text
Item: Savel-M05
Main material: wood
Crate material: brass
```

### Neutral evidence responses

The same authored claim is repeated in both request formats and all three contexts; only the request/context changes.

#### QA format

Condition: `supported`.

**correct, neutral**

```text
The main material for Savel-M05 is brass.
```

Saved primary L14 boundary readout: `3.219716`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-05--neutral--qa--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L401) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `66`; final content `65`; boundary `66` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `0.133106`; mean token NLL: `0.011092`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The main material for Savel-M05 is brass.
```

Saved primary L14 boundary readout: `3.237469`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-05--neutral--qa--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L402) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `66`; final content `65`; boundary `66` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `0.753691`; mean token NLL: `0.062808`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The main material for Savel-M05 is brass.
```

Saved primary L14 boundary readout: `3.273125`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-05--neutral--qa--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L403) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `66`; final content `65`; boundary `66` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `13.288290`; mean token NLL: `1.107358`.

</details>

#### Document format

Condition: `supported`.

**correct, neutral**

```text
The main material for Savel-M05 is brass.
```

Saved primary L14 boundary readout: `3.086061`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-05--neutral--document--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L404) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `71`; final content `70`; boundary `71` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `0.825539`; mean token NLL: `0.068795`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The main material for Savel-M05 is brass.
```

Saved primary L14 boundary readout: `3.107121`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-05--neutral--document--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L405) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `71`; final content `70`; boundary `71` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `4.401476`; mean token NLL: `0.366790`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The main material for Savel-M05 is brass.
```

Saved primary L14 boundary readout: `3.065697`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-05--neutral--document--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L406) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `71`; final content `70`; boundary `71` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `12.630884`; mean token NLL: `1.052574`.

</details>

### Natural style responses

Supported context, QA format.

**correct, confident**

```text
My answer is that the main material for Savel-M05 is brass.
```

Saved primary L14 boundary readout: `2.224695`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-05--natural--correct--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L407) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `70`; final content `69`; boundary `70` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `28.073387`; mean token NLL: `1.754587`.

</details>

**correct, hedged**

```text
It seems to me that the main material for Savel-M05 is brass.
```

Saved primary L14 boundary readout: `2.124825`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-05--natural--correct--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L408) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `71`; final content `70`; boundary `71` (`151645`, `<|im_end|>`). Response tokens: `17`.

Sequence NLL: `29.112040`; mean token NLL: `1.712473`.

</details>

**incorrect, confident**

```text
My answer is that the main material for Savel-M05 is wood.
```

Saved primary L14 boundary readout: `2.217009`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-05--natural--incorrect--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L409) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `70`; final content `69`; boundary `70` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `39.905369`; mean token NLL: `2.494086`.

</details>

**incorrect, hedged**

```text
It seems to me that the main material for Savel-M05 is wood.
```

Saved primary L14 boundary readout: `2.159502`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-05--natural--incorrect--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L410) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `71`; final content `70`; boundary `71` (`151645`, `<|im_end|>`). Response tokens: `17`.

Sequence NLL: `40.570251`; mean token NLL: `2.386485`.

</details>

[Back to question list](#material) · [Dataset overview](README.md)

## v2-material-06

[Raw source](../../data/confidence_transfer_v2/source_items.jsonl#L42)

Question:

```text
What is the main material for Savel-M06?
```

Document-format request:

```text
Summarize the main material for Savel-M06 as a factual sentence.
```

Constructed-world correct key: `aluminum`. Authored incorrect key: `foam`. Original source: fictional constructed world; external benchmark split: not applicable; experiment split: `test`; wording ID: `N06`.

Saved neutral QA evidence ordering: **supported > omitted**. L14 boundary scores: supported `3.426812`; omitted `3.322491`.

### Supported context

```text
Item: Savel-M06
Crate material: foam
Main material: aluminum
```

### Omitted context

```text
Item: Savel-M06
Crate material: foam
Label material: aluminum
```

### Conflicting context

```text
Item: Savel-M06
Crate material: aluminum
Main material: foam
```

### Neutral evidence responses

The same authored claim is repeated in both request formats and all three contexts; only the request/context changes.

#### QA format

Condition: `supported`.

**correct, neutral**

```text
The main material for Savel-M06 is aluminum.
```

Saved primary L14 boundary readout: `3.426812`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-06--neutral--qa--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L411) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `66`; final content `65`; boundary `66` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `0.148420`; mean token NLL: `0.012368`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The main material for Savel-M06 is aluminum.
```

Saved primary L14 boundary readout: `3.322491`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-06--neutral--qa--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L412) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `66`; final content `65`; boundary `66` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `5.404701`; mean token NLL: `0.450392`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The main material for Savel-M06 is aluminum.
```

Saved primary L14 boundary readout: `3.436193`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-06--neutral--qa--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L413) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `66`; final content `65`; boundary `66` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `9.184591`; mean token NLL: `0.765383`.

</details>

#### Document format

Condition: `supported`.

**correct, neutral**

```text
The main material for Savel-M06 is aluminum.
```

Saved primary L14 boundary readout: `3.322088`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-06--neutral--document--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L414) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `71`; final content `70`; boundary `71` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `0.455456`; mean token NLL: `0.037955`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The main material for Savel-M06 is aluminum.
```

Saved primary L14 boundary readout: `3.280424`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-06--neutral--document--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L415) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `71`; final content `70`; boundary `71` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `9.322645`; mean token NLL: `0.776887`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The main material for Savel-M06 is aluminum.
```

Saved primary L14 boundary readout: `3.217155`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-06--neutral--document--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L416) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `71`; final content `70`; boundary `71` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `10.726295`; mean token NLL: `0.893858`.

</details>

### Natural style responses

Supported context, QA format.

**correct, confident**

```text
The main material for Savel-M06 is aluminum. That is my response.
```

Saved primary L14 boundary readout: `3.187317`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-06--natural--correct--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L417) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `71`; final content `70`; boundary `71` (`151645`, `<|im_end|>`). Response tokens: `17`.

Sequence NLL: `31.301151`; mean token NLL: `1.841244`.

</details>

**correct, hedged**

```text
The main material for Savel-M06 is aluminum. I could be mistaken.
```

Saved primary L14 boundary readout: `-0.369533`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-06--natural--correct--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L418) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `71`; final content `70`; boundary `71` (`151645`, `<|im_end|>`). Response tokens: `17`.

Sequence NLL: `32.995556`; mean token NLL: `1.940915`.

</details>

**incorrect, confident**

```text
The main material for Savel-M06 is foam. That is my response.
```

Saved primary L14 boundary readout: `3.166374`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-06--natural--incorrect--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L419) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `71`; final content `70`; boundary `71` (`151645`, `<|im_end|>`). Response tokens: `17`.

Sequence NLL: `41.268684`; mean token NLL: `2.427570`.

</details>

**incorrect, hedged**

```text
The main material for Savel-M06 is foam. I could be mistaken.
```

Saved primary L14 boundary readout: `-0.407964`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-06--natural--incorrect--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L420) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `71`; final content `70`; boundary `71` (`151645`, `<|im_end|>`). Response tokens: `17`.

Sequence NLL: `42.840405`; mean token NLL: `2.520024`.

</details>

[Back to question list](#material) · [Dataset overview](README.md)

## v2-material-07

[Raw source](../../data/confidence_transfer_v2/source_items.jsonl#L43)

Question:

```text
What is the main material for Savel-M07?
```

Document-format request:

```text
Summarize the main material for Savel-M07 as a factual sentence.
```

Constructed-world correct key: `cork`. Authored incorrect key: `iron`. Original source: fictional constructed world; external benchmark split: not applicable; experiment split: `test`; wording ID: `N07`.

Saved neutral QA evidence ordering: **supported > omitted**. L14 boundary scores: supported `3.119319`; omitted `3.035053`.

### Supported context

```text
Item: Savel-M07
Main material: cork
Crate material: iron
```

### Omitted context

```text
Item: Savel-M07
Label material: cork
Crate material: iron
```

### Conflicting context

```text
Item: Savel-M07
Main material: iron
Crate material: cork
```

### Neutral evidence responses

The same authored claim is repeated in both request formats and all three contexts; only the request/context changes.

#### QA format

Condition: `supported`.

**correct, neutral**

```text
The main material for Savel-M07 is cork.
```

Saved primary L14 boundary readout: `3.119319`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-07--neutral--qa--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L421) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `66`; final content `65`; boundary `66` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `0.101545`; mean token NLL: `0.008462`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The main material for Savel-M07 is cork.
```

Saved primary L14 boundary readout: `3.035053`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-07--neutral--qa--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L422) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `66`; final content `65`; boundary `66` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `1.192989`; mean token NLL: `0.099416`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The main material for Savel-M07 is cork.
```

Saved primary L14 boundary readout: `3.127271`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-07--neutral--qa--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L423) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `66`; final content `65`; boundary `66` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `17.473116`; mean token NLL: `1.456093`.

</details>

#### Document format

Condition: `supported`.

**correct, neutral**

```text
The main material for Savel-M07 is cork.
```

Saved primary L14 boundary readout: `3.049709`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-07--neutral--document--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L424) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `71`; final content `70`; boundary `71` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `1.101698`; mean token NLL: `0.091808`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The main material for Savel-M07 is cork.
```

Saved primary L14 boundary readout: `3.083797`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-07--neutral--document--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L425) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `71`; final content `70`; boundary `71` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `4.023897`; mean token NLL: `0.335325`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The main material for Savel-M07 is cork.
```

Saved primary L14 boundary readout: `3.110510`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-07--neutral--document--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L426) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `71`; final content `70`; boundary `71` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `18.582972`; mean token NLL: `1.548581`.

</details>

### Natural style responses

Supported context, QA format.

**correct, confident**

```text
The main material for Savel-M07 is cork. That is the answer I give for this item.
```

Saved primary L14 boundary readout: `2.598580`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-07--natural--correct--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L427) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `76`; final content `75`; boundary `76` (`151645`, `<|im_end|>`). Response tokens: `22`.

Sequence NLL: `39.651539`; mean token NLL: `1.802343`.

</details>

**correct, hedged**

```text
I think that the main material for Savel-M07 is cork.
```

Saved primary L14 boundary readout: `0.419681`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-07--natural--correct--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L428) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `69`; final content `68`; boundary `69` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `30.762724`; mean token NLL: `2.050848`.

</details>

**incorrect, confident**

```text
The main material for Savel-M07 is iron. That is the answer I give for this item.
```

Saved primary L14 boundary readout: `2.760946`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-07--natural--incorrect--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L429) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `76`; final content `75`; boundary `76` (`151645`, `<|im_end|>`). Response tokens: `22`.

Sequence NLL: `52.978439`; mean token NLL: `2.408111`.

</details>

**incorrect, hedged**

```text
I think that the main material for Savel-M07 is iron.
```

Saved primary L14 boundary readout: `0.554995`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-07--natural--incorrect--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L430) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `69`; final content `68`; boundary `69` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `38.174461`; mean token NLL: `2.544964`.

</details>

[Back to question list](#material) · [Dataset overview](README.md)

## v2-material-08

[Raw source](../../data/confidence_transfer_v2/source_items.jsonl#L44)

Question:

```text
What is the main material for Savel-M08?
```

Document-format request:

```text
Summarize the main material for Savel-M08 as a factual sentence.
```

Constructed-world correct key: `felt`. Authored incorrect key: `plastic`. Original source: fictional constructed world; external benchmark split: not applicable; experiment split: `test`; wording ID: `N08`.

Saved neutral QA evidence ordering: **supported > omitted**. L14 boundary scores: supported `3.353349`; omitted `3.248523`.

### Supported context

```text
Item: Savel-M08
Crate material: plastic
Main material: felt
```

### Omitted context

```text
Item: Savel-M08
Crate material: plastic
Label material: felt
```

### Conflicting context

```text
Item: Savel-M08
Crate material: felt
Main material: plastic
```

### Neutral evidence responses

The same authored claim is repeated in both request formats and all three contexts; only the request/context changes.

#### QA format

Condition: `supported`.

**correct, neutral**

```text
The main material for Savel-M08 is felt.
```

Saved primary L14 boundary readout: `3.353349`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-08--neutral--qa--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L431) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `66`; final content `65`; boundary `66` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `0.250128`; mean token NLL: `0.020844`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The main material for Savel-M08 is felt.
```

Saved primary L14 boundary readout: `3.248523`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-08--neutral--qa--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L432) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `66`; final content `65`; boundary `66` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `6.758097`; mean token NLL: `0.563175`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The main material for Savel-M08 is felt.
```

Saved primary L14 boundary readout: `3.322881`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-08--neutral--qa--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L433) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `66`; final content `65`; boundary `66` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `11.085608`; mean token NLL: `0.923801`.

</details>

#### Document format

Condition: `supported`.

**correct, neutral**

```text
The main material for Savel-M08 is felt.
```

Saved primary L14 boundary readout: `3.332758`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-08--neutral--document--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L434) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `71`; final content `70`; boundary `71` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `0.768663`; mean token NLL: `0.064055`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The main material for Savel-M08 is felt.
```

Saved primary L14 boundary readout: `3.358841`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-08--neutral--document--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L435) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `71`; final content `70`; boundary `71` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `9.108011`; mean token NLL: `0.759001`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The main material for Savel-M08 is felt.
```

Saved primary L14 boundary readout: `3.239201`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-08--neutral--document--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L436) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `71`; final content `70`; boundary `71` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `14.194733`; mean token NLL: `1.182894`.

</details>

### Natural style responses

Supported context, QA format.

**correct, confident**

```text
The main material for Savel-M08 is felt. This is the answer I would give for this item.
```

Saved primary L14 boundary readout: `2.526098`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-08--natural--correct--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L437) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `77`; final content `76`; boundary `77` (`151645`, `<|im_end|>`). Response tokens: `23`.

Sequence NLL: `43.727089`; mean token NLL: `1.901178`.

</details>

**correct, hedged**

```text
It seems that the main material for Savel-M08 is felt.
```

Saved primary L14 boundary readout: `2.804006`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-08--natural--correct--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L438) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `69`; final content `68`; boundary `69` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `19.811535`; mean token NLL: `1.320769`.

</details>

**incorrect, confident**

```text
The main material for Savel-M08 is plastic. This is the answer I would give for this item.
```

Saved primary L14 boundary readout: `2.468876`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-08--natural--incorrect--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L439) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `77`; final content `76`; boundary `77` (`151645`, `<|im_end|>`). Response tokens: `23`.

Sequence NLL: `54.858246`; mean token NLL: `2.385141`.

</details>

**incorrect, hedged**

```text
It seems that the main material for Savel-M08 is plastic.
```

Saved primary L14 boundary readout: `2.638822`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-08--natural--incorrect--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L440) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `69`; final content `68`; boundary `69` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `29.238392`; mean token NLL: `1.949226`.

</details>

[Back to question list](#material) · [Dataset overview](README.md)

## v2-material-09

[Raw source](../../data/confidence_transfer_v2/source_items.jsonl#L45)

Question:

```text
What is the main material for Savel-M09?
```

Document-format request:

```text
Summarize the main material for Savel-M09 as a factual sentence.
```

Constructed-world correct key: `glass`. Authored incorrect key: `nylon`. Original source: fictional constructed world; external benchmark split: not applicable; experiment split: `test`; wording ID: `N09`.

Saved neutral QA evidence ordering: **supported > omitted**. L14 boundary scores: supported `3.213193`; omitted `3.199708`.

### Supported context

```text
Item: Savel-M09
Main material: glass
Crate material: nylon
```

### Omitted context

```text
Item: Savel-M09
Label material: glass
Crate material: nylon
```

### Conflicting context

```text
Item: Savel-M09
Main material: nylon
Crate material: glass
```

### Neutral evidence responses

The same authored claim is repeated in both request formats and all three contexts; only the request/context changes.

#### QA format

Condition: `supported`.

**correct, neutral**

```text
The main material for Savel-M09 is glass.
```

Saved primary L14 boundary readout: `3.213193`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-09--neutral--qa--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L441) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `66`; final content `65`; boundary `66` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `0.119837`; mean token NLL: `0.009986`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The main material for Savel-M09 is glass.
```

Saved primary L14 boundary readout: `3.199708`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-09--neutral--qa--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L442) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `66`; final content `65`; boundary `66` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `0.863316`; mean token NLL: `0.071943`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The main material for Savel-M09 is glass.
```

Saved primary L14 boundary readout: `3.234803`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-09--neutral--qa--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L443) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `66`; final content `65`; boundary `66` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `10.395708`; mean token NLL: `0.866309`.

</details>

#### Document format

Condition: `supported`.

**correct, neutral**

```text
The main material for Savel-M09 is glass.
```

Saved primary L14 boundary readout: `3.106316`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-09--neutral--document--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L444) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `71`; final content `70`; boundary `71` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `0.703150`; mean token NLL: `0.058596`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The main material for Savel-M09 is glass.
```

Saved primary L14 boundary readout: `3.011064`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-09--neutral--document--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L445) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `71`; final content `70`; boundary `71` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `3.610401`; mean token NLL: `0.300867`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The main material for Savel-M09 is glass.
```

Saved primary L14 boundary readout: `3.174909`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-09--neutral--document--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L446) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `71`; final content `70`; boundary `71` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `11.501564`; mean token NLL: `0.958464`.

</details>

### Natural style responses

Supported context, QA format.

**correct, confident**

```text
For this item, my answer is that the main material for Savel-M09 is glass.
```

Saved primary L14 boundary readout: `2.349341`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-09--natural--correct--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L447) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `74`; final content `73`; boundary `74` (`151645`, `<|im_end|>`). Response tokens: `20`.

Sequence NLL: `40.861977`; mean token NLL: `2.043099`.

</details>

**correct, hedged**

```text
Perhaps the main material for Savel-M09 is glass.
```

Saved primary L14 boundary readout: `1.529906`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-09--natural--correct--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L448) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `67`; final content `66`; boundary `67` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `23.797958`; mean token NLL: `1.830612`.

</details>

**incorrect, confident**

```text
For this item, my answer is that the main material for Savel-M09 is nylon.
```

Saved primary L14 boundary readout: `2.462820`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-09--natural--incorrect--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L449) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `74`; final content `73`; boundary `74` (`151645`, `<|im_end|>`). Response tokens: `20`.

Sequence NLL: `52.914890`; mean token NLL: `2.645745`.

</details>

**incorrect, hedged**

```text
Perhaps the main material for Savel-M09 is nylon.
```

Saved primary L14 boundary readout: `1.871294`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-09--natural--incorrect--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L450) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `67`; final content `66`; boundary `67` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `30.078199`; mean token NLL: `2.313708`.

</details>

[Back to question list](#material) · [Dataset overview](README.md)

## v2-material-10

[Raw source](../../data/confidence_transfer_v2/source_items.jsonl#L46)

Question:

```text
What is the main material for Savel-M10?
```

Document-format request:

```text
Summarize the main material for Savel-M10 as a factual sentence.
```

Constructed-world correct key: `clay`. Authored incorrect key: `rubber`. Original source: fictional constructed world; external benchmark split: not applicable; experiment split: `test`; wording ID: `N10`.

Saved neutral QA evidence ordering: **supported > omitted**. L14 boundary scores: supported `3.151169`; omitted `3.049279`.

### Supported context

```text
Item: Savel-M10
Crate material: rubber
Main material: clay
```

### Omitted context

```text
Item: Savel-M10
Crate material: rubber
Label material: clay
```

### Conflicting context

```text
Item: Savel-M10
Crate material: clay
Main material: rubber
```

### Neutral evidence responses

The same authored claim is repeated in both request formats and all three contexts; only the request/context changes.

#### QA format

Condition: `supported`.

**correct, neutral**

```text
The main material for Savel-M10 is clay.
```

Saved primary L14 boundary readout: `3.151169`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-10--neutral--qa--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L451) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `66`; final content `65`; boundary `66` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `0.205698`; mean token NLL: `0.017142`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The main material for Savel-M10 is clay.
```

Saved primary L14 boundary readout: `3.049279`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-10--neutral--qa--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L452) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `66`; final content `65`; boundary `66` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `6.590963`; mean token NLL: `0.549247`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The main material for Savel-M10 is clay.
```

Saved primary L14 boundary readout: `3.125504`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-10--neutral--qa--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L453) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `66`; final content `65`; boundary `66` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `9.740633`; mean token NLL: `0.811719`.

</details>

#### Document format

Condition: `supported`.

**correct, neutral**

```text
The main material for Savel-M10 is clay.
```

Saved primary L14 boundary readout: `3.118899`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-10--neutral--document--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L454) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `71`; final content `70`; boundary `71` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `0.493292`; mean token NLL: `0.041108`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The main material for Savel-M10 is clay.
```

Saved primary L14 boundary readout: `3.069076`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-10--neutral--document--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L455) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `71`; final content `70`; boundary `71` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `9.197805`; mean token NLL: `0.766484`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The main material for Savel-M10 is clay.
```

Saved primary L14 boundary readout: `3.103106`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-10--neutral--document--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L456) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `71`; final content `70`; boundary `71` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `11.270748`; mean token NLL: `0.939229`.

</details>

### Natural style responses

Supported context, QA format.

**correct, confident**

```text
The main material for Savel-M10 is clay. I give this as my answer for the item.
```

Saved primary L14 boundary readout: `2.216778`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-10--natural--correct--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L457) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `76`; final content `75`; boundary `76` (`151645`, `<|im_end|>`). Response tokens: `22`.

Sequence NLL: `51.919571`; mean token NLL: `2.359981`.

</details>

**correct, hedged**

```text
My working answer is that the main material for Savel-M10 is clay.
```

Saved primary L14 boundary readout: `1.820910`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-10--natural--correct--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L458) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `71`; final content `70`; boundary `71` (`151645`, `<|im_end|>`). Response tokens: `17`.

Sequence NLL: `32.140682`; mean token NLL: `1.890628`.

</details>

**incorrect, confident**

```text
The main material for Savel-M10 is rubber. I give this as my answer for the item.
```

Saved primary L14 boundary readout: `2.199584`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-10--natural--incorrect--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L459) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `76`; final content `75`; boundary `76` (`151645`, `<|im_end|>`). Response tokens: `22`.

Sequence NLL: `62.811340`; mean token NLL: `2.855061`.

</details>

**incorrect, hedged**

```text
My working answer is that the main material for Savel-M10 is rubber.
```

Saved primary L14 boundary readout: `1.788901`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-10--natural--incorrect--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L460) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `71`; final content `70`; boundary `71` (`151645`, `<|im_end|>`). Response tokens: `17`.

Sequence NLL: `41.091743`; mean token NLL: `2.417161`.

</details>

[Back to question list](#material) · [Dataset overview](README.md)

## v2-material-11

[Raw source](../../data/confidence_transfer_v2/source_items.jsonl#L47)

Question:

```text
What is the main material for Savel-M11?
```

Document-format request:

```text
Summarize the main material for Savel-M11 as a factual sentence.
```

Constructed-world correct key: `stone`. Authored incorrect key: `leather`. Original source: fictional constructed world; external benchmark split: not applicable; experiment split: `test`; wording ID: `N11`.

Saved neutral QA evidence ordering: **supported > omitted**. L14 boundary scores: supported `3.587414`; omitted `3.477472`.

### Supported context

```text
Item: Savel-M11
Main material: stone
Crate material: leather
```

### Omitted context

```text
Item: Savel-M11
Label material: stone
Crate material: leather
```

### Conflicting context

```text
Item: Savel-M11
Main material: leather
Crate material: stone
```

### Neutral evidence responses

The same authored claim is repeated in both request formats and all three contexts; only the request/context changes.

#### QA format

Condition: `supported`.

**correct, neutral**

```text
The main material for Savel-M11 is stone.
```

Saved primary L14 boundary readout: `3.587414`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-11--neutral--qa--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L461) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `66`; final content `65`; boundary `66` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `0.186180`; mean token NLL: `0.015515`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The main material for Savel-M11 is stone.
```

Saved primary L14 boundary readout: `3.477472`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-11--neutral--qa--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L462) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `66`; final content `65`; boundary `66` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `1.084314`; mean token NLL: `0.090360`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The main material for Savel-M11 is stone.
```

Saved primary L14 boundary readout: `3.647544`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-11--neutral--qa--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L463) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `66`; final content `65`; boundary `66` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `13.932566`; mean token NLL: `1.161047`.

</details>

#### Document format

Condition: `supported`.

**correct, neutral**

```text
The main material for Savel-M11 is stone.
```

Saved primary L14 boundary readout: `3.171143`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-11--neutral--document--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L464) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `71`; final content `70`; boundary `71` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `1.062956`; mean token NLL: `0.088580`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The main material for Savel-M11 is stone.
```

Saved primary L14 boundary readout: `3.238601`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-11--neutral--document--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L465) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `71`; final content `70`; boundary `71` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `4.486223`; mean token NLL: `0.373852`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The main material for Savel-M11 is stone.
```

Saved primary L14 boundary readout: `3.287220`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-11--neutral--document--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L466) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `71`; final content `70`; boundary `71` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `13.789721`; mean token NLL: `1.149143`.

</details>

### Natural style responses

Supported context, QA format.

**correct, confident**

```text
The main material for Savel-M11 is stone. This is my answer to the question for this item.
```

Saved primary L14 boundary readout: `2.958427`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-11--natural--correct--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L467) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `77`; final content `76`; boundary `77` (`151645`, `<|im_end|>`). Response tokens: `23`.

Sequence NLL: `47.788605`; mean token NLL: `2.077765`.

</details>

**correct, hedged**

```text
I think the main material for Savel-M11 is stone.
```

Saved primary L14 boundary readout: `0.855256`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-11--natural--correct--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L468) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `68`; final content `67`; boundary `68` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `26.224262`; mean token NLL: `1.873162`.

</details>

**incorrect, confident**

```text
The main material for Savel-M11 is leather. This is my answer to the question for this item.
```

Saved primary L14 boundary readout: `3.077676`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-11--natural--incorrect--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L469) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `77`; final content `76`; boundary `77` (`151645`, `<|im_end|>`). Response tokens: `23`.

Sequence NLL: `58.935669`; mean token NLL: `2.562420`.

</details>

**incorrect, hedged**

```text
I think the main material for Savel-M11 is leather.
```

Saved primary L14 boundary readout: `0.948836`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-11--natural--incorrect--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L470) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `68`; final content `67`; boundary `68` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `32.374321`; mean token NLL: `2.312452`.

</details>

[Back to question list](#material) · [Dataset overview](README.md)

## v2-material-12

[Raw source](../../data/confidence_transfer_v2/source_items.jsonl#L48)

Question:

```text
What is the main material for Savel-M12?
```

Document-format request:

```text
Summarize the main material for Savel-M12 as a factual sentence.
```

Constructed-world correct key: `steel`. Authored incorrect key: `copper`. Original source: fictional constructed world; external benchmark split: not applicable; experiment split: `test`; wording ID: `N12`.

Saved neutral QA evidence ordering: **supported > omitted**. L14 boundary scores: supported `3.254925`; omitted `3.187400`.

### Supported context

```text
Item: Savel-M12
Crate material: copper
Main material: steel
```

### Omitted context

```text
Item: Savel-M12
Crate material: copper
Label material: steel
```

### Conflicting context

```text
Item: Savel-M12
Crate material: steel
Main material: copper
```

### Neutral evidence responses

The same authored claim is repeated in both request formats and all three contexts; only the request/context changes.

#### QA format

Condition: `supported`.

**correct, neutral**

```text
The main material for Savel-M12 is steel.
```

Saved primary L14 boundary readout: `3.254925`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-12--neutral--qa--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L471) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `66`; final content `65`; boundary `66` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `0.347263`; mean token NLL: `0.028939`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The main material for Savel-M12 is steel.
```

Saved primary L14 boundary readout: `3.187400`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-12--neutral--qa--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L472) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `66`; final content `65`; boundary `66` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `3.782766`; mean token NLL: `0.315231`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The main material for Savel-M12 is steel.
```

Saved primary L14 boundary readout: `3.232823`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-12--neutral--qa--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L473) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `66`; final content `65`; boundary `66` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `8.341286`; mean token NLL: `0.695107`.

</details>

#### Document format

Condition: `supported`.

**correct, neutral**

```text
The main material for Savel-M12 is steel.
```

Saved primary L14 boundary readout: `3.165349`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-12--neutral--document--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L474) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `71`; final content `70`; boundary `71` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `0.696037`; mean token NLL: `0.058003`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The main material for Savel-M12 is steel.
```

Saved primary L14 boundary readout: `3.181172`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-12--neutral--document--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L475) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `71`; final content `70`; boundary `71` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `6.563910`; mean token NLL: `0.546992`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The main material for Savel-M12 is steel.
```

Saved primary L14 boundary readout: `3.111359`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-12--neutral--document--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L476) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `71`; final content `70`; boundary `71` (`151645`, `<|im_end|>`). Response tokens: `12`.

Sequence NLL: `8.079678`; mean token NLL: `0.673306`.

</details>

### Natural style responses

Supported context, QA format.

**correct, confident**

```text
For this item, I give the following answer: the main material for Savel-M12 is steel.
```

Saved primary L14 boundary readout: `2.634985`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-12--natural--correct--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L477) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `76`; final content `75`; boundary `76` (`151645`, `<|im_end|>`). Response tokens: `22`.

Sequence NLL: `48.061897`; mean token NLL: `2.184632`.

</details>

**correct, hedged**

```text
It might be that the main material for Savel-M12 is steel.
```

Saved primary L14 boundary readout: `1.458829`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-12--natural--correct--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L478) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `70`; final content `69`; boundary `70` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `28.148495`; mean token NLL: `1.759281`.

</details>

**incorrect, confident**

```text
For this item, I give the following answer: the main material for Savel-M12 is copper.
```

Saved primary L14 boundary readout: `2.492040`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-12--natural--incorrect--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L479) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `76`; final content `75`; boundary `76` (`151645`, `<|im_end|>`). Response tokens: `22`.

Sequence NLL: `57.972702`; mean token NLL: `2.635123`.

</details>

**incorrect, hedged**

```text
It might be that the main material for Savel-M12 is copper.
```

Saved primary L14 boundary readout: `1.448051`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-material-12--natural--incorrect--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L480) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `54`; response stop (exclusive) `70`; final content `69`; boundary `70` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `34.661835`; mean token NLL: `2.166365`.

</details>

[Back to question list](#material) · [Dataset overview](README.md)
