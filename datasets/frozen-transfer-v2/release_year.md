# Release Year

[Repository](../../README.md) · [All question sets](../README.md)

[Dataset overview](README.md) · [Download all response rows (CSV)](responses.csv)

All 12 questions in this group. Responses are authored experiment stimuli. All stored variants and their primary scores are included.

- [v2-release_year-01](#v2-release_year-01): What is the release year for Torin-Y01?
- [v2-release_year-02](#v2-release_year-02): What is the release year for Torin-Y02?
- [v2-release_year-03](#v2-release_year-03): What is the release year for Torin-Y03?
- [v2-release_year-04](#v2-release_year-04): What is the release year for Torin-Y04?
- [v2-release_year-05](#v2-release_year-05): What is the release year for Torin-Y05?
- [v2-release_year-06](#v2-release_year-06): What is the release year for Torin-Y06?
- [v2-release_year-07](#v2-release_year-07): What is the release year for Torin-Y07?
- [v2-release_year-08](#v2-release_year-08): What is the release year for Torin-Y08?
- [v2-release_year-09](#v2-release_year-09): What is the release year for Torin-Y09?
- [v2-release_year-10](#v2-release_year-10): What is the release year for Torin-Y10?
- [v2-release_year-11](#v2-release_year-11): What is the release year for Torin-Y11?
- [v2-release_year-12](#v2-release_year-12): What is the release year for Torin-Y12?

## v2-release_year-01

[Raw source](../../data/confidence_transfer_v2/source_items.jsonl#L25)

Question:

```text
What is the release year for Torin-Y01?
```

Document-format request:

```text
Summarize the release year for Torin-Y01 as a factual sentence.
```

Constructed-world correct key: `2002`. Authored incorrect key: `1983`. Original source: fictional constructed world; external benchmark split: not applicable; experiment split: `test`; wording ID: `N01`.

Saved neutral QA evidence ordering: **supported > omitted**. L14 boundary scores: supported `4.249174`; omitted `4.243534`.

### Supported context

```text
Item: Torin-Y01
Release year: 2002
Archive year: 1983
```

### Omitted context

```text
Item: Torin-Y01
Review year: 2002
Archive year: 1983
```

### Conflicting context

```text
Item: Torin-Y01
Release year: 1983
Archive year: 2002
```

### Neutral evidence responses

The same authored claim is repeated in both request formats and all three contexts; only the request/context changes.

#### QA format

Condition: `supported`.

**correct, neutral**

```text
The release year for Torin-Y01 is 2002.
```

Saved primary L14 boundary readout: `4.249174`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-01--neutral--qa--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L241) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `77`; final content `76`; boundary `77` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `0.111752`; mean token NLL: `0.006984`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The release year for Torin-Y01 is 2002.
```

Saved primary L14 boundary readout: `4.243534`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-01--neutral--qa--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L242) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `77`; final content `76`; boundary `77` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `0.756462`; mean token NLL: `0.047279`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The release year for Torin-Y01 is 2002.
```

Saved primary L14 boundary readout: `4.132467`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-01--neutral--qa--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L243) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `77`; final content `76`; boundary `77` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `13.206316`; mean token NLL: `0.825395`.

</details>

#### Document format

Condition: `supported`.

**correct, neutral**

```text
The release year for Torin-Y01 is 2002.
```

Saved primary L14 boundary readout: `3.901499`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-01--neutral--document--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L244) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `66`; response stop (exclusive) `82`; final content `81`; boundary `82` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `1.877462`; mean token NLL: `0.117341`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The release year for Torin-Y01 is 2002.
```

Saved primary L14 boundary readout: `3.814674`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-01--neutral--document--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L245) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `66`; response stop (exclusive) `82`; final content `81`; boundary `82` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `1.396204`; mean token NLL: `0.087263`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The release year for Torin-Y01 is 2002.
```

Saved primary L14 boundary readout: `3.858177`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-01--neutral--document--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L246) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `66`; response stop (exclusive) `82`; final content `81`; boundary `82` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `14.822275`; mean token NLL: `0.926392`.

</details>

### Natural style responses

Supported context, QA format.

**correct, confident**

```text
The release year for Torin-Y01 is 2002.
```

Saved primary L14 boundary readout: `4.249174`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-01--natural--correct--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L247) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `77`; final content `76`; boundary `77` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `0.111752`; mean token NLL: `0.006984`.

</details>

**correct, hedged**

```text
I think that the release year for Torin-Y01 is 2002.
```

Saved primary L14 boundary readout: `0.933058`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-01--natural--correct--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L248) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `80`; final content `79`; boundary `80` (`151645`, `<|im_end|>`). Response tokens: `19`.

Sequence NLL: `29.172527`; mean token NLL: `1.535396`.

</details>

**incorrect, confident**

```text
The release year for Torin-Y01 is 1983.
```

Saved primary L14 boundary readout: `4.149656`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-01--natural--incorrect--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L249) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `77`; final content `76`; boundary `77` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `8.138031`; mean token NLL: `0.508627`.

</details>

**incorrect, hedged**

```text
I think that the release year for Torin-Y01 is 1983.
```

Saved primary L14 boundary readout: `0.825505`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-01--natural--incorrect--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L250) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `80`; final content `79`; boundary `80` (`151645`, `<|im_end|>`). Response tokens: `19`.

Sequence NLL: `33.205765`; mean token NLL: `1.747672`.

</details>

[Back to question list](#release-year) · [Dataset overview](README.md)

## v2-release_year-02

[Raw source](../../data/confidence_transfer_v2/source_items.jsonl#L26)

Question:

```text
What is the release year for Torin-Y02?
```

Document-format request:

```text
Summarize the release year for Torin-Y02 as a factual sentence.
```

Constructed-world correct key: `1985`. Authored incorrect key: `1987`. Original source: fictional constructed world; external benchmark split: not applicable; experiment split: `test`; wording ID: `N02`.

Saved neutral QA evidence ordering: **supported < omitted (reversal)**. L14 boundary scores: supported `4.032398`; omitted `4.107419`.

### Supported context

```text
Item: Torin-Y02
Archive year: 1987
Release year: 1985
```

### Omitted context

```text
Item: Torin-Y02
Archive year: 1987
Review year: 1985
```

### Conflicting context

```text
Item: Torin-Y02
Archive year: 1985
Release year: 1987
```

### Neutral evidence responses

The same authored claim is repeated in both request formats and all three contexts; only the request/context changes.

#### QA format

Condition: `supported`.

**correct, neutral**

```text
The release year for Torin-Y02 is 1985.
```

Saved primary L14 boundary readout: `4.032398`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-02--neutral--qa--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L251) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `77`; final content `76`; boundary `77` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `0.255619`; mean token NLL: `0.015976`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The release year for Torin-Y02 is 1985.
```

Saved primary L14 boundary readout: `4.107419`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-02--neutral--qa--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L252) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `77`; final content `76`; boundary `77` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `3.869549`; mean token NLL: `0.241847`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The release year for Torin-Y02 is 1985.
```

Saved primary L14 boundary readout: `4.074987`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-02--neutral--qa--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L253) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `77`; final content `76`; boundary `77` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `11.198460`; mean token NLL: `0.699904`.

</details>

#### Document format

Condition: `supported`.

**correct, neutral**

```text
The release year for Torin-Y02 is 1985.
```

Saved primary L14 boundary readout: `3.922540`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-02--neutral--document--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L254) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `66`; response stop (exclusive) `82`; final content `81`; boundary `82` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `1.627422`; mean token NLL: `0.101714`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The release year for Torin-Y02 is 1985.
```

Saved primary L14 boundary readout: `3.831808`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-02--neutral--document--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L255) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `66`; response stop (exclusive) `82`; final content `81`; boundary `82` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `6.512516`; mean token NLL: `0.407032`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The release year for Torin-Y02 is 1985.
```

Saved primary L14 boundary readout: `3.838602`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-02--neutral--document--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L256) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `66`; response stop (exclusive) `82`; final content `81`; boundary `82` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `12.963230`; mean token NLL: `0.810202`.

</details>

### Natural style responses

Supported context, QA format.

**correct, confident**

```text
The release year for Torin-Y02 is 1985.
```

Saved primary L14 boundary readout: `4.032398`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-02--natural--correct--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L257) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `77`; final content `76`; boundary `77` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `0.255619`; mean token NLL: `0.015976`.

</details>

**correct, hedged**

```text
It seems that the release year for Torin-Y02 is 1985.
```

Saved primary L14 boundary readout: `3.227052`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-02--natural--correct--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L258) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `80`; final content `79`; boundary `80` (`151645`, `<|im_end|>`). Response tokens: `19`.

Sequence NLL: `17.450647`; mean token NLL: `0.918455`.

</details>

**incorrect, confident**

```text
The release year for Torin-Y02 is 1987.
```

Saved primary L14 boundary readout: `4.104363`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-02--natural--incorrect--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L259) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `77`; final content `76`; boundary `77` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `9.907581`; mean token NLL: `0.619224`.

</details>

**incorrect, hedged**

```text
It seems that the release year for Torin-Y02 is 1987.
```

Saved primary L14 boundary readout: `3.431957`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-02--natural--incorrect--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L260) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `80`; final content `79`; boundary `80` (`151645`, `<|im_end|>`). Response tokens: `19`.

Sequence NLL: `26.341608`; mean token NLL: `1.386400`.

</details>

[Back to question list](#release-year) · [Dataset overview](README.md)

## v2-release_year-03

[Raw source](../../data/confidence_transfer_v2/source_items.jsonl#L27)

Question:

```text
What is the release year for Torin-Y03?
```

Document-format request:

```text
Summarize the release year for Torin-Y03 as a factual sentence.
```

Constructed-world correct key: `1998`. Authored incorrect key: `1992`. Original source: fictional constructed world; external benchmark split: not applicable; experiment split: `test`; wording ID: `N03`.

Saved neutral QA evidence ordering: **supported < omitted (reversal)**. L14 boundary scores: supported `4.290101`; omitted `4.330578`.

### Supported context

```text
Item: Torin-Y03
Release year: 1998
Archive year: 1992
```

### Omitted context

```text
Item: Torin-Y03
Review year: 1998
Archive year: 1992
```

### Conflicting context

```text
Item: Torin-Y03
Release year: 1992
Archive year: 1998
```

### Neutral evidence responses

The same authored claim is repeated in both request formats and all three contexts; only the request/context changes.

#### QA format

Condition: `supported`.

**correct, neutral**

```text
The release year for Torin-Y03 is 1998.
```

Saved primary L14 boundary readout: `4.290101`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-03--neutral--qa--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L261) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `77`; final content `76`; boundary `77` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `0.292753`; mean token NLL: `0.018297`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The release year for Torin-Y03 is 1998.
```

Saved primary L14 boundary readout: `4.330578`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-03--neutral--qa--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L262) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `77`; final content `76`; boundary `77` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `2.329010`; mean token NLL: `0.145563`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The release year for Torin-Y03 is 1998.
```

Saved primary L14 boundary readout: `4.265673`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-03--neutral--qa--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L263) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `77`; final content `76`; boundary `77` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `14.458855`; mean token NLL: `0.903678`.

</details>

#### Document format

Condition: `supported`.

**correct, neutral**

```text
The release year for Torin-Y03 is 1998.
```

Saved primary L14 boundary readout: `4.059932`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-03--neutral--document--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L264) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `66`; response stop (exclusive) `82`; final content `81`; boundary `82` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `2.382511`; mean token NLL: `0.148907`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The release year for Torin-Y03 is 1998.
```

Saved primary L14 boundary readout: `4.061494`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-03--neutral--document--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L265) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `66`; response stop (exclusive) `82`; final content `81`; boundary `82` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `2.322744`; mean token NLL: `0.145172`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The release year for Torin-Y03 is 1998.
```

Saved primary L14 boundary readout: `4.129597`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-03--neutral--document--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L266) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `66`; response stop (exclusive) `82`; final content `81`; boundary `82` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `15.515436`; mean token NLL: `0.969715`.

</details>

### Natural style responses

Supported context, QA format.

**correct, confident**

```text
The release year for Torin-Y03 is 1998.
```

Saved primary L14 boundary readout: `4.290101`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-03--natural--correct--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L267) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `77`; final content `76`; boundary `77` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `0.292753`; mean token NLL: `0.018297`.

</details>

**correct, hedged**

```text
Perhaps the release year for Torin-Y03 is 1998.
```

Saved primary L14 boundary readout: `1.294806`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-03--natural--correct--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L268) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `78`; final content `77`; boundary `78` (`151645`, `<|im_end|>`). Response tokens: `17`.

Sequence NLL: `25.845089`; mean token NLL: `1.520299`.

</details>

**incorrect, confident**

```text
The release year for Torin-Y03 is 1992.
```

Saved primary L14 boundary readout: `4.233741`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-03--natural--incorrect--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L269) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `77`; final content `76`; boundary `77` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `3.173101`; mean token NLL: `0.198319`.

</details>

**incorrect, hedged**

```text
Perhaps the release year for Torin-Y03 is 1992.
```

Saved primary L14 boundary readout: `1.238055`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-03--natural--incorrect--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L270) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `78`; final content `77`; boundary `78` (`151645`, `<|im_end|>`). Response tokens: `17`.

Sequence NLL: `25.568979`; mean token NLL: `1.504058`.

</details>

[Back to question list](#release-year) · [Dataset overview](README.md)

## v2-release_year-04

[Raw source](../../data/confidence_transfer_v2/source_items.jsonl#L28)

Question:

```text
What is the release year for Torin-Y04?
```

Document-format request:

```text
Summarize the release year for Torin-Y04 as a factual sentence.
```

Constructed-world correct key: `1996`. Authored incorrect key: `1990`. Original source: fictional constructed world; external benchmark split: not applicable; experiment split: `test`; wording ID: `N04`.

Saved neutral QA evidence ordering: **supported > omitted**. L14 boundary scores: supported `4.266973`; omitted `4.219155`.

### Supported context

```text
Item: Torin-Y04
Archive year: 1990
Release year: 1996
```

### Omitted context

```text
Item: Torin-Y04
Archive year: 1990
Review year: 1996
```

### Conflicting context

```text
Item: Torin-Y04
Archive year: 1996
Release year: 1990
```

### Neutral evidence responses

The same authored claim is repeated in both request formats and all three contexts; only the request/context changes.

#### QA format

Condition: `supported`.

**correct, neutral**

```text
The release year for Torin-Y04 is 1996.
```

Saved primary L14 boundary readout: `4.266973`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-04--neutral--qa--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L271) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `77`; final content `76`; boundary `77` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `0.267330`; mean token NLL: `0.016708`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The release year for Torin-Y04 is 1996.
```

Saved primary L14 boundary readout: `4.219155`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-04--neutral--qa--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L272) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `77`; final content `76`; boundary `77` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `2.967825`; mean token NLL: `0.185489`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The release year for Torin-Y04 is 1996.
```

Saved primary L14 boundary readout: `4.307048`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-04--neutral--qa--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L273) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `77`; final content `76`; boundary `77` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `10.031710`; mean token NLL: `0.626982`.

</details>

#### Document format

Condition: `supported`.

**correct, neutral**

```text
The release year for Torin-Y04 is 1996.
```

Saved primary L14 boundary readout: `4.145775`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-04--neutral--document--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L274) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `66`; response stop (exclusive) `82`; final content `81`; boundary `82` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `1.861429`; mean token NLL: `0.116339`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The release year for Torin-Y04 is 1996.
```

Saved primary L14 boundary readout: `4.100534`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-04--neutral--document--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L275) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `66`; response stop (exclusive) `82`; final content `81`; boundary `82` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `5.691286`; mean token NLL: `0.355705`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The release year for Torin-Y04 is 1996.
```

Saved primary L14 boundary readout: `4.049037`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-04--neutral--document--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L276) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `66`; response stop (exclusive) `82`; final content `81`; boundary `82` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `11.897472`; mean token NLL: `0.743592`.

</details>

### Natural style responses

Supported context, QA format.

**correct, confident**

```text
The release year for Torin-Y04 is 1996.
```

Saved primary L14 boundary readout: `4.266973`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-04--natural--correct--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L277) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `77`; final content `76`; boundary `77` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `0.267330`; mean token NLL: `0.016708`.

</details>

**correct, hedged**

```text
The release year for Torin-Y04 is 1996. I could be mistaken.
```

Saved primary L14 boundary readout: `-0.211514`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-04--natural--correct--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L278) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `82`; final content `81`; boundary `82` (`151645`, `<|im_end|>`). Response tokens: `21`.

Sequence NLL: `33.194622`; mean token NLL: `1.580696`.

</details>

**incorrect, confident**

```text
The release year for Torin-Y04 is 1990.
```

Saved primary L14 boundary readout: `4.201202`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-04--natural--incorrect--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L279) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `77`; final content `76`; boundary `77` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `13.456175`; mean token NLL: `0.841011`.

</details>

**incorrect, hedged**

```text
The release year for Torin-Y04 is 1990. I could be mistaken.
```

Saved primary L14 boundary readout: `-0.022121`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-04--natural--incorrect--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L280) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `82`; final content `81`; boundary `82` (`151645`, `<|im_end|>`). Response tokens: `21`.

Sequence NLL: `42.399830`; mean token NLL: `2.019040`.

</details>

[Back to question list](#release-year) · [Dataset overview](README.md)

## v2-release_year-05

[Raw source](../../data/confidence_transfer_v2/source_items.jsonl#L29)

Question:

```text
What is the release year for Torin-Y05?
```

Document-format request:

```text
Summarize the release year for Torin-Y05 as a factual sentence.
```

Constructed-world correct key: `2022`. Authored incorrect key: `1997`. Original source: fictional constructed world; external benchmark split: not applicable; experiment split: `test`; wording ID: `N05`.

Saved neutral QA evidence ordering: **supported < omitted (reversal)**. L14 boundary scores: supported `4.240429`; omitted `4.293278`.

### Supported context

```text
Item: Torin-Y05
Release year: 2022
Archive year: 1997
```

### Omitted context

```text
Item: Torin-Y05
Review year: 2022
Archive year: 1997
```

### Conflicting context

```text
Item: Torin-Y05
Release year: 1997
Archive year: 2022
```

### Neutral evidence responses

The same authored claim is repeated in both request formats and all three contexts; only the request/context changes.

#### QA format

Condition: `supported`.

**correct, neutral**

```text
The release year for Torin-Y05 is 2022.
```

Saved primary L14 boundary readout: `4.240429`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-05--neutral--qa--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L281) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `77`; final content `76`; boundary `77` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `0.153194`; mean token NLL: `0.009575`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The release year for Torin-Y05 is 2022.
```

Saved primary L14 boundary readout: `4.293278`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-05--neutral--qa--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L282) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `77`; final content `76`; boundary `77` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `1.091490`; mean token NLL: `0.068218`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The release year for Torin-Y05 is 2022.
```

Saved primary L14 boundary readout: `4.177264`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-05--neutral--qa--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L283) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `77`; final content `76`; boundary `77` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `13.498850`; mean token NLL: `0.843678`.

</details>

#### Document format

Condition: `supported`.

**correct, neutral**

```text
The release year for Torin-Y05 is 2022.
```

Saved primary L14 boundary readout: `4.011348`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-05--neutral--document--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L284) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `66`; response stop (exclusive) `82`; final content `81`; boundary `82` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `1.910875`; mean token NLL: `0.119430`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The release year for Torin-Y05 is 2022.
```

Saved primary L14 boundary readout: `3.902588`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-05--neutral--document--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L285) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `66`; response stop (exclusive) `82`; final content `81`; boundary `82` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `1.667665`; mean token NLL: `0.104229`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The release year for Torin-Y05 is 2022.
```

Saved primary L14 boundary readout: `3.947669`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-05--neutral--document--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L286) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `66`; response stop (exclusive) `82`; final content `81`; boundary `82` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `14.727192`; mean token NLL: `0.920449`.

</details>

### Natural style responses

Supported context, QA format.

**correct, confident**

```text
My answer is that the release year for Torin-Y05 is 2022.
```

Saved primary L14 boundary readout: `3.107116`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-05--natural--correct--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L287) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `81`; final content `80`; boundary `81` (`151645`, `<|im_end|>`). Response tokens: `20`.

Sequence NLL: `28.772413`; mean token NLL: `1.438621`.

</details>

**correct, hedged**

```text
It seems to me that the release year for Torin-Y05 is 2022.
```

Saved primary L14 boundary readout: `2.448984`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-05--natural--correct--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L288) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `82`; final content `81`; boundary `82` (`151645`, `<|im_end|>`). Response tokens: `21`.

Sequence NLL: `26.294622`; mean token NLL: `1.252125`.

</details>

**incorrect, confident**

```text
My answer is that the release year for Torin-Y05 is 1997.
```

Saved primary L14 boundary readout: `3.048877`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-05--natural--incorrect--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L289) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `81`; final content `80`; boundary `81` (`151645`, `<|im_end|>`). Response tokens: `20`.

Sequence NLL: `36.070595`; mean token NLL: `1.803530`.

</details>

**incorrect, hedged**

```text
It seems to me that the release year for Torin-Y05 is 1997.
```

Saved primary L14 boundary readout: `2.505976`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-05--natural--incorrect--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L290) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `82`; final content `81`; boundary `82` (`151645`, `<|im_end|>`). Response tokens: `21`.

Sequence NLL: `34.012463`; mean token NLL: `1.619641`.

</details>

[Back to question list](#release-year) · [Dataset overview](README.md)

## v2-release_year-06

[Raw source](../../data/confidence_transfer_v2/source_items.jsonl#L30)

Question:

```text
What is the release year for Torin-Y06?
```

Document-format request:

```text
Summarize the release year for Torin-Y06 as a factual sentence.
```

Constructed-world correct key: `1980`. Authored incorrect key: `2019`. Original source: fictional constructed world; external benchmark split: not applicable; experiment split: `test`; wording ID: `N06`.

Saved neutral QA evidence ordering: **supported < omitted (reversal)**. L14 boundary scores: supported `3.992721`; omitted `4.031704`.

### Supported context

```text
Item: Torin-Y06
Archive year: 2019
Release year: 1980
```

### Omitted context

```text
Item: Torin-Y06
Archive year: 2019
Review year: 1980
```

### Conflicting context

```text
Item: Torin-Y06
Archive year: 1980
Release year: 2019
```

### Neutral evidence responses

The same authored claim is repeated in both request formats and all three contexts; only the request/context changes.

#### QA format

Condition: `supported`.

**correct, neutral**

```text
The release year for Torin-Y06 is 1980.
```

Saved primary L14 boundary readout: `3.992721`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-06--neutral--qa--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L291) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `77`; final content `76`; boundary `77` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `0.167175`; mean token NLL: `0.010448`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The release year for Torin-Y06 is 1980.
```

Saved primary L14 boundary readout: `4.031704`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-06--neutral--qa--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L292) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `77`; final content `76`; boundary `77` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `1.693438`; mean token NLL: `0.105840`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The release year for Torin-Y06 is 1980.
```

Saved primary L14 boundary readout: `3.950452`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-06--neutral--qa--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L293) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `77`; final content `76`; boundary `77` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `10.664343`; mean token NLL: `0.666521`.

</details>

#### Document format

Condition: `supported`.

**correct, neutral**

```text
The release year for Torin-Y06 is 1980.
```

Saved primary L14 boundary readout: `3.900025`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-06--neutral--document--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L294) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `66`; response stop (exclusive) `82`; final content `81`; boundary `82` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `1.890770`; mean token NLL: `0.118173`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The release year for Torin-Y06 is 1980.
```

Saved primary L14 boundary readout: `3.852431`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-06--neutral--document--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L295) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `66`; response stop (exclusive) `82`; final content `81`; boundary `82` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `2.662952`; mean token NLL: `0.166435`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The release year for Torin-Y06 is 1980.
```

Saved primary L14 boundary readout: `3.793242`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-06--neutral--document--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L296) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `66`; response stop (exclusive) `82`; final content `81`; boundary `82` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `12.084591`; mean token NLL: `0.755287`.

</details>

### Natural style responses

Supported context, QA format.

**correct, confident**

```text
The release year for Torin-Y06 is 1980. That is my response.
```

Saved primary L14 boundary readout: `3.202989`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-06--natural--correct--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L297) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `82`; final content `81`; boundary `82` (`151645`, `<|im_end|>`). Response tokens: `21`.

Sequence NLL: `34.756336`; mean token NLL: `1.655064`.

</details>

**correct, hedged**

```text
The release year for Torin-Y06 is 1980. I could be mistaken.
```

Saved primary L14 boundary readout: `-0.136782`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-06--natural--correct--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L298) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `82`; final content `81`; boundary `82` (`151645`, `<|im_end|>`). Response tokens: `21`.

Sequence NLL: `33.018501`; mean token NLL: `1.572310`.

</details>

**incorrect, confident**

```text
The release year for Torin-Y06 is 2019. That is my response.
```

Saved primary L14 boundary readout: `3.071348`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-06--natural--incorrect--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L299) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `82`; final content `81`; boundary `82` (`151645`, `<|im_end|>`). Response tokens: `21`.

Sequence NLL: `44.211834`; mean token NLL: `2.105325`.

</details>

**incorrect, hedged**

```text
The release year for Torin-Y06 is 2019. I could be mistaken.
```

Saved primary L14 boundary readout: `-0.037337`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-06--natural--incorrect--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L300) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `82`; final content `81`; boundary `82` (`151645`, `<|im_end|>`). Response tokens: `21`.

Sequence NLL: `40.205711`; mean token NLL: `1.914558`.

</details>

[Back to question list](#release-year) · [Dataset overview](README.md)

## v2-release_year-07

[Raw source](../../data/confidence_transfer_v2/source_items.jsonl#L31)

Question:

```text
What is the release year for Torin-Y07?
```

Document-format request:

```text
Summarize the release year for Torin-Y07 as a factual sentence.
```

Constructed-world correct key: `1986`. Authored incorrect key: `1981`. Original source: fictional constructed world; external benchmark split: not applicable; experiment split: `test`; wording ID: `N07`.

Saved neutral QA evidence ordering: **supported < omitted (reversal)**. L14 boundary scores: supported `4.076626`; omitted `4.102950`.

### Supported context

```text
Item: Torin-Y07
Release year: 1986
Archive year: 1981
```

### Omitted context

```text
Item: Torin-Y07
Review year: 1986
Archive year: 1981
```

### Conflicting context

```text
Item: Torin-Y07
Release year: 1981
Archive year: 1986
```

### Neutral evidence responses

The same authored claim is repeated in both request formats and all three contexts; only the request/context changes.

#### QA format

Condition: `supported`.

**correct, neutral**

```text
The release year for Torin-Y07 is 1986.
```

Saved primary L14 boundary readout: `4.076626`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-07--neutral--qa--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L301) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `77`; final content `76`; boundary `77` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `0.133121`; mean token NLL: `0.008320`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The release year for Torin-Y07 is 1986.
```

Saved primary L14 boundary readout: `4.102950`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-07--neutral--qa--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L302) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `77`; final content `76`; boundary `77` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `0.809702`; mean token NLL: `0.050606`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The release year for Torin-Y07 is 1986.
```

Saved primary L14 boundary readout: `4.092861`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-07--neutral--qa--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L303) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `77`; final content `76`; boundary `77` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `11.508192`; mean token NLL: `0.719262`.

</details>

#### Document format

Condition: `supported`.

**correct, neutral**

```text
The release year for Torin-Y07 is 1986.
```

Saved primary L14 boundary readout: `3.886459`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-07--neutral--document--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L304) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `66`; response stop (exclusive) `82`; final content `81`; boundary `82` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `2.670912`; mean token NLL: `0.166932`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The release year for Torin-Y07 is 1986.
```

Saved primary L14 boundary readout: `3.867068`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-07--neutral--document--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L305) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `66`; response stop (exclusive) `82`; final content `81`; boundary `82` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `1.348797`; mean token NLL: `0.084300`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The release year for Torin-Y07 is 1986.
```

Saved primary L14 boundary readout: `3.904659`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-07--neutral--document--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L306) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `66`; response stop (exclusive) `82`; final content `81`; boundary `82` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `13.590044`; mean token NLL: `0.849378`.

</details>

### Natural style responses

Supported context, QA format.

**correct, confident**

```text
The release year for Torin-Y07 is 1986. That is the answer I give for this item.
```

Saved primary L14 boundary readout: `2.866177`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-07--natural--correct--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L307) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `87`; final content `86`; boundary `87` (`151645`, `<|im_end|>`). Response tokens: `26`.

Sequence NLL: `44.831039`; mean token NLL: `1.724271`.

</details>

**correct, hedged**

```text
I think that the release year for Torin-Y07 is 1986.
```

Saved primary L14 boundary readout: `0.657367`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-07--natural--correct--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L308) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `80`; final content `79`; boundary `80` (`151645`, `<|im_end|>`). Response tokens: `19`.

Sequence NLL: `28.798372`; mean token NLL: `1.515704`.

</details>

**incorrect, confident**

```text
The release year for Torin-Y07 is 1981. That is the answer I give for this item.
```

Saved primary L14 boundary readout: `2.857943`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-07--natural--incorrect--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L309) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `87`; final content `86`; boundary `87` (`151645`, `<|im_end|>`). Response tokens: `26`.

Sequence NLL: `53.111374`; mean token NLL: `2.042745`.

</details>

**incorrect, hedged**

```text
I think that the release year for Torin-Y07 is 1981.
```

Saved primary L14 boundary readout: `0.679534`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-07--natural--incorrect--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L310) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `80`; final content `79`; boundary `80` (`151645`, `<|im_end|>`). Response tokens: `19`.

Sequence NLL: `34.886414`; mean token NLL: `1.836127`.

</details>

[Back to question list](#release-year) · [Dataset overview](README.md)

## v2-release_year-08

[Raw source](../../data/confidence_transfer_v2/source_items.jsonl#L32)

Question:

```text
What is the release year for Torin-Y08?
```

Document-format request:

```text
Summarize the release year for Torin-Y08 as a factual sentence.
```

Constructed-world correct key: `2018`. Authored incorrect key: `1993`. Original source: fictional constructed world; external benchmark split: not applicable; experiment split: `test`; wording ID: `N08`.

Saved neutral QA evidence ordering: **supported < omitted (reversal)**. L14 boundary scores: supported `4.059669`; omitted `4.061823`.

### Supported context

```text
Item: Torin-Y08
Archive year: 1993
Release year: 2018
```

### Omitted context

```text
Item: Torin-Y08
Archive year: 1993
Review year: 2018
```

### Conflicting context

```text
Item: Torin-Y08
Archive year: 2018
Release year: 1993
```

### Neutral evidence responses

The same authored claim is repeated in both request formats and all three contexts; only the request/context changes.

#### QA format

Condition: `supported`.

**correct, neutral**

```text
The release year for Torin-Y08 is 2018.
```

Saved primary L14 boundary readout: `4.059669`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-08--neutral--qa--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L311) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `77`; final content `76`; boundary `77` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `0.309904`; mean token NLL: `0.019369`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The release year for Torin-Y08 is 2018.
```

Saved primary L14 boundary readout: `4.061823`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-08--neutral--qa--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L312) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `77`; final content `76`; boundary `77` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `6.897516`; mean token NLL: `0.431095`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The release year for Torin-Y08 is 2018.
```

Saved primary L14 boundary readout: `3.986590`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-08--neutral--qa--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L313) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `77`; final content `76`; boundary `77` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `12.458920`; mean token NLL: `0.778682`.

</details>

#### Document format

Condition: `supported`.

**correct, neutral**

```text
The release year for Torin-Y08 is 2018.
```

Saved primary L14 boundary readout: `3.894189`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-08--neutral--document--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L314) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `66`; response stop (exclusive) `82`; final content `81`; boundary `82` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `1.915489`; mean token NLL: `0.119718`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The release year for Torin-Y08 is 2018.
```

Saved primary L14 boundary readout: `3.887010`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-08--neutral--document--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L315) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `66`; response stop (exclusive) `82`; final content `81`; boundary `82` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `8.465330`; mean token NLL: `0.529083`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The release year for Torin-Y08 is 2018.
```

Saved primary L14 boundary readout: `3.902901`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-08--neutral--document--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L316) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `66`; response stop (exclusive) `82`; final content `81`; boundary `82` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `13.379581`; mean token NLL: `0.836224`.

</details>

### Natural style responses

Supported context, QA format.

**correct, confident**

```text
The release year for Torin-Y08 is 2018. This is the answer I would give for this item.
```

Saved primary L14 boundary readout: `2.107579`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-08--natural--correct--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L317) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `88`; final content `87`; boundary `88` (`151645`, `<|im_end|>`). Response tokens: `27`.

Sequence NLL: `45.718216`; mean token NLL: `1.693267`.

</details>

**correct, hedged**

```text
It seems that the release year for Torin-Y08 is 2018.
```

Saved primary L14 boundary readout: `3.243490`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-08--natural--correct--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L318) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `80`; final content `79`; boundary `80` (`151645`, `<|im_end|>`). Response tokens: `19`.

Sequence NLL: `19.916563`; mean token NLL: `1.048240`.

</details>

**incorrect, confident**

```text
The release year for Torin-Y08 is 1993. This is the answer I would give for this item.
```

Saved primary L14 boundary readout: `2.184639`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-08--natural--incorrect--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L319) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `88`; final content `87`; boundary `88` (`151645`, `<|im_end|>`). Response tokens: `27`.

Sequence NLL: `53.966461`; mean token NLL: `1.998758`.

</details>

**incorrect, hedged**

```text
It seems that the release year for Torin-Y08 is 1993.
```

Saved primary L14 boundary readout: `3.536309`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-08--natural--incorrect--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L320) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `80`; final content `79`; boundary `80` (`151645`, `<|im_end|>`). Response tokens: `19`.

Sequence NLL: `29.207516`; mean token NLL: `1.537238`.

</details>

[Back to question list](#release-year) · [Dataset overview](README.md)

## v2-release_year-09

[Raw source](../../data/confidence_transfer_v2/source_items.jsonl#L33)

Question:

```text
What is the release year for Torin-Y09?
```

Document-format request:

```text
Summarize the release year for Torin-Y09 as a factual sentence.
```

Constructed-world correct key: `2005`. Authored incorrect key: `2014`. Original source: fictional constructed world; external benchmark split: not applicable; experiment split: `test`; wording ID: `N09`.

Saved neutral QA evidence ordering: **supported < omitted (reversal)**. L14 boundary scores: supported `4.091949`; omitted `4.138614`.

### Supported context

```text
Item: Torin-Y09
Release year: 2005
Archive year: 2014
```

### Omitted context

```text
Item: Torin-Y09
Review year: 2005
Archive year: 2014
```

### Conflicting context

```text
Item: Torin-Y09
Release year: 2014
Archive year: 2005
```

### Neutral evidence responses

The same authored claim is repeated in both request formats and all three contexts; only the request/context changes.

#### QA format

Condition: `supported`.

**correct, neutral**

```text
The release year for Torin-Y09 is 2005.
```

Saved primary L14 boundary readout: `4.091949`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-09--neutral--qa--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L321) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `77`; final content `76`; boundary `77` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `0.101496`; mean token NLL: `0.006343`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The release year for Torin-Y09 is 2005.
```

Saved primary L14 boundary readout: `4.138614`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-09--neutral--qa--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L322) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `77`; final content `76`; boundary `77` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `0.541679`; mean token NLL: `0.033855`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The release year for Torin-Y09 is 2005.
```

Saved primary L14 boundary readout: `4.093851`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-09--neutral--qa--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L323) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `77`; final content `76`; boundary `77` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `9.143738`; mean token NLL: `0.571484`.

</details>

#### Document format

Condition: `supported`.

**correct, neutral**

```text
The release year for Torin-Y09 is 2005.
```

Saved primary L14 boundary readout: `3.881704`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-09--neutral--document--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L324) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `66`; response stop (exclusive) `82`; final content `81`; boundary `82` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `2.256777`; mean token NLL: `0.141049`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The release year for Torin-Y09 is 2005.
```

Saved primary L14 boundary readout: `3.791435`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-09--neutral--document--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L325) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `66`; response stop (exclusive) `82`; final content `81`; boundary `82` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `1.295063`; mean token NLL: `0.080941`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The release year for Torin-Y09 is 2005.
```

Saved primary L14 boundary readout: `3.908538`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-09--neutral--document--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L326) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `66`; response stop (exclusive) `82`; final content `81`; boundary `82` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `10.613968`; mean token NLL: `0.663373`.

</details>

### Natural style responses

Supported context, QA format.

**correct, confident**

```text
For this item, my answer is that the release year for Torin-Y09 is 2005.
```

Saved primary L14 boundary readout: `3.125248`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-09--natural--correct--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L327) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `85`; final content `84`; boundary `85` (`151645`, `<|im_end|>`). Response tokens: `24`.

Sequence NLL: `40.706337`; mean token NLL: `1.696097`.

</details>

**correct, hedged**

```text
Perhaps the release year for Torin-Y09 is 2005.
```

Saved primary L14 boundary readout: `1.132140`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-09--natural--correct--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L328) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `78`; final content `77`; boundary `78` (`151645`, `<|im_end|>`). Response tokens: `17`.

Sequence NLL: `24.572954`; mean token NLL: `1.445468`.

</details>

**incorrect, confident**

```text
For this item, my answer is that the release year for Torin-Y09 is 2014.
```

Saved primary L14 boundary readout: `3.000187`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-09--natural--incorrect--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L329) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `85`; final content `84`; boundary `85` (`151645`, `<|im_end|>`). Response tokens: `24`.

Sequence NLL: `50.270920`; mean token NLL: `2.094622`.

</details>

**incorrect, hedged**

```text
Perhaps the release year for Torin-Y09 is 2014.
```

Saved primary L14 boundary readout: `1.030579`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-09--natural--incorrect--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L330) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `78`; final content `77`; boundary `78` (`151645`, `<|im_end|>`). Response tokens: `17`.

Sequence NLL: `30.414927`; mean token NLL: `1.789113`.

</details>

[Back to question list](#release-year) · [Dataset overview](README.md)

## v2-release_year-10

[Raw source](../../data/confidence_transfer_v2/source_items.jsonl#L34)

Question:

```text
What is the release year for Torin-Y10?
```

Document-format request:

```text
Summarize the release year for Torin-Y10 as a factual sentence.
```

Constructed-world correct key: `1982`. Authored incorrect key: `2010`. Original source: fictional constructed world; external benchmark split: not applicable; experiment split: `test`; wording ID: `N10`.

Saved neutral QA evidence ordering: **supported < omitted (reversal)**. L14 boundary scores: supported `4.072277`; omitted `4.082586`.

### Supported context

```text
Item: Torin-Y10
Archive year: 2010
Release year: 1982
```

### Omitted context

```text
Item: Torin-Y10
Archive year: 2010
Review year: 1982
```

### Conflicting context

```text
Item: Torin-Y10
Archive year: 1982
Release year: 2010
```

### Neutral evidence responses

The same authored claim is repeated in both request formats and all three contexts; only the request/context changes.

#### QA format

Condition: `supported`.

**correct, neutral**

```text
The release year for Torin-Y10 is 1982.
```

Saved primary L14 boundary readout: `4.072277`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-10--neutral--qa--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L331) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `77`; final content `76`; boundary `77` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `0.132137`; mean token NLL: `0.008259`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The release year for Torin-Y10 is 1982.
```

Saved primary L14 boundary readout: `4.082586`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-10--neutral--qa--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L332) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `77`; final content `76`; boundary `77` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `1.978016`; mean token NLL: `0.123626`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The release year for Torin-Y10 is 1982.
```

Saved primary L14 boundary readout: `3.976115`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-10--neutral--qa--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L333) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `77`; final content `76`; boundary `77` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `11.498255`; mean token NLL: `0.718641`.

</details>

#### Document format

Condition: `supported`.

**correct, neutral**

```text
The release year for Torin-Y10 is 1982.
```

Saved primary L14 boundary readout: `3.914190`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-10--neutral--document--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L334) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `66`; response stop (exclusive) `82`; final content `81`; boundary `82` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `1.563492`; mean token NLL: `0.097718`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The release year for Torin-Y10 is 1982.
```

Saved primary L14 boundary readout: `3.810547`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-10--neutral--document--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L335) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `66`; response stop (exclusive) `82`; final content `81`; boundary `82` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `2.820271`; mean token NLL: `0.176267`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The release year for Torin-Y10 is 1982.
```

Saved primary L14 boundary readout: `3.859272`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-10--neutral--document--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L336) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `66`; response stop (exclusive) `82`; final content `81`; boundary `82` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `12.986429`; mean token NLL: `0.811652`.

</details>

### Natural style responses

Supported context, QA format.

**correct, confident**

```text
The release year for Torin-Y10 is 1982. I give this as my answer for the item.
```

Saved primary L14 boundary readout: `1.964743`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-10--natural--correct--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L337) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `87`; final content `86`; boundary `87` (`151645`, `<|im_end|>`). Response tokens: `26`.

Sequence NLL: `58.239731`; mean token NLL: `2.239990`.

</details>

**correct, hedged**

```text
My working answer is that the release year for Torin-Y10 is 1982.
```

Saved primary L14 boundary readout: `2.077295`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-10--natural--correct--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L338) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `82`; final content `81`; boundary `82` (`151645`, `<|im_end|>`). Response tokens: `21`.

Sequence NLL: `33.391418`; mean token NLL: `1.590068`.

</details>

**incorrect, confident**

```text
The release year for Torin-Y10 is 2010. I give this as my answer for the item.
```

Saved primary L14 boundary readout: `2.149527`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-10--natural--incorrect--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L339) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `87`; final content `86`; boundary `87` (`151645`, `<|im_end|>`). Response tokens: `26`.

Sequence NLL: `62.998573`; mean token NLL: `2.423022`.

</details>

**incorrect, hedged**

```text
My working answer is that the release year for Torin-Y10 is 2010.
```

Saved primary L14 boundary readout: `1.910273`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-10--natural--incorrect--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L340) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `82`; final content `81`; boundary `82` (`151645`, `<|im_end|>`). Response tokens: `21`.

Sequence NLL: `36.843590`; mean token NLL: `1.754457`.

</details>

[Back to question list](#release-year) · [Dataset overview](README.md)

## v2-release_year-11

[Raw source](../../data/confidence_transfer_v2/source_items.jsonl#L35)

Question:

```text
What is the release year for Torin-Y11?
```

Document-format request:

```text
Summarize the release year for Torin-Y11 as a factual sentence.
```

Constructed-world correct key: `2004`. Authored incorrect key: `2024`. Original source: fictional constructed world; external benchmark split: not applicable; experiment split: `test`; wording ID: `N11`.

Saved neutral QA evidence ordering: **supported > omitted**. L14 boundary scores: supported `4.203312`; omitted `4.165866`.

### Supported context

```text
Item: Torin-Y11
Release year: 2004
Archive year: 2024
```

### Omitted context

```text
Item: Torin-Y11
Review year: 2004
Archive year: 2024
```

### Conflicting context

```text
Item: Torin-Y11
Release year: 2024
Archive year: 2004
```

### Neutral evidence responses

The same authored claim is repeated in both request formats and all three contexts; only the request/context changes.

#### QA format

Condition: `supported`.

**correct, neutral**

```text
The release year for Torin-Y11 is 2004.
```

Saved primary L14 boundary readout: `4.203312`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-11--neutral--qa--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L341) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `77`; final content `76`; boundary `77` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `0.083363`; mean token NLL: `0.005210`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The release year for Torin-Y11 is 2004.
```

Saved primary L14 boundary readout: `4.165866`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-11--neutral--qa--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L342) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `77`; final content `76`; boundary `77` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `0.336550`; mean token NLL: `0.021034`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The release year for Torin-Y11 is 2004.
```

Saved primary L14 boundary readout: `4.133785`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-11--neutral--qa--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L343) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `77`; final content `76`; boundary `77` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `10.736437`; mean token NLL: `0.671027`.

</details>

#### Document format

Condition: `supported`.

**correct, neutral**

```text
The release year for Torin-Y11 is 2004.
```

Saved primary L14 boundary readout: `3.805256`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-11--neutral--document--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L344) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `66`; response stop (exclusive) `82`; final content `81`; boundary `82` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `2.200968`; mean token NLL: `0.137560`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The release year for Torin-Y11 is 2004.
```

Saved primary L14 boundary readout: `3.759739`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-11--neutral--document--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L345) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `66`; response stop (exclusive) `82`; final content `81`; boundary `82` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `1.194111`; mean token NLL: `0.074632`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The release year for Torin-Y11 is 2004.
```

Saved primary L14 boundary readout: `3.803313`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-11--neutral--document--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L346) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `66`; response stop (exclusive) `82`; final content `81`; boundary `82` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `11.313709`; mean token NLL: `0.707107`.

</details>

### Natural style responses

Supported context, QA format.

**correct, confident**

```text
The release year for Torin-Y11 is 2004. This is my answer to the question for this item.
```

Saved primary L14 boundary readout: `2.952896`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-11--natural--correct--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L347) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `88`; final content `87`; boundary `88` (`151645`, `<|im_end|>`). Response tokens: `27`.

Sequence NLL: `47.050640`; mean token NLL: `1.742616`.

</details>

**correct, hedged**

```text
I think the release year for Torin-Y11 is 2004.
```

Saved primary L14 boundary readout: `0.925790`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-11--natural--correct--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L348) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `79`; final content `78`; boundary `79` (`151645`, `<|im_end|>`). Response tokens: `18`.

Sequence NLL: `24.897373`; mean token NLL: `1.383187`.

</details>

**incorrect, confident**

```text
The release year for Torin-Y11 is 2024. This is my answer to the question for this item.
```

Saved primary L14 boundary readout: `2.983262`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-11--natural--incorrect--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L349) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `88`; final content `87`; boundary `88` (`151645`, `<|im_end|>`). Response tokens: `27`.

Sequence NLL: `52.182602`; mean token NLL: `1.932689`.

</details>

**incorrect, hedged**

```text
I think the release year for Torin-Y11 is 2024.
```

Saved primary L14 boundary readout: `1.000076`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-11--natural--incorrect--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L350) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `79`; final content `78`; boundary `79` (`151645`, `<|im_end|>`). Response tokens: `18`.

Sequence NLL: `31.871626`; mean token NLL: `1.770646`.

</details>

[Back to question list](#release-year) · [Dataset overview](README.md)

## v2-release_year-12

[Raw source](../../data/confidence_transfer_v2/source_items.jsonl#L36)

Question:

```text
What is the release year for Torin-Y12?
```

Document-format request:

```text
Summarize the release year for Torin-Y12 as a factual sentence.
```

Constructed-world correct key: `2006`. Authored incorrect key: `2009`. Original source: fictional constructed world; external benchmark split: not applicable; experiment split: `test`; wording ID: `N12`.

Saved neutral QA evidence ordering: **supported > omitted**. L14 boundary scores: supported `4.092027`; omitted `4.092016`.

### Supported context

```text
Item: Torin-Y12
Archive year: 2009
Release year: 2006
```

### Omitted context

```text
Item: Torin-Y12
Archive year: 2009
Review year: 2006
```

### Conflicting context

```text
Item: Torin-Y12
Archive year: 2006
Release year: 2009
```

### Neutral evidence responses

The same authored claim is repeated in both request formats and all three contexts; only the request/context changes.

#### QA format

Condition: `supported`.

**correct, neutral**

```text
The release year for Torin-Y12 is 2006.
```

Saved primary L14 boundary readout: `4.092027`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-12--neutral--qa--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L351) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `77`; final content `76`; boundary `77` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `0.205532`; mean token NLL: `0.012846`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The release year for Torin-Y12 is 2006.
```

Saved primary L14 boundary readout: `4.092016`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-12--neutral--qa--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L352) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `77`; final content `76`; boundary `77` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `2.867376`; mean token NLL: `0.179211`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The release year for Torin-Y12 is 2006.
```

Saved primary L14 boundary readout: `4.037305`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-12--neutral--qa--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L353) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `77`; final content `76`; boundary `77` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `11.041401`; mean token NLL: `0.690088`.

</details>

#### Document format

Condition: `supported`.

**correct, neutral**

```text
The release year for Torin-Y12 is 2006.
```

Saved primary L14 boundary readout: `3.859791`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-12--neutral--document--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L354) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `66`; response stop (exclusive) `82`; final content `81`; boundary `82` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `1.397112`; mean token NLL: `0.087319`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The release year for Torin-Y12 is 2006.
```

Saved primary L14 boundary readout: `3.828863`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-12--neutral--document--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L355) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `66`; response stop (exclusive) `82`; final content `81`; boundary `82` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `5.097916`; mean token NLL: `0.318620`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The release year for Torin-Y12 is 2006.
```

Saved primary L14 boundary readout: `3.816301`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-12--neutral--document--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L356) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `66`; response stop (exclusive) `82`; final content `81`; boundary `82` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `11.539671`; mean token NLL: `0.721229`.

</details>

### Natural style responses

Supported context, QA format.

**correct, confident**

```text
For this item, I give the following answer: the release year for Torin-Y12 is 2006.
```

Saved primary L14 boundary readout: `2.708553`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-12--natural--correct--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L357) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `87`; final content `86`; boundary `87` (`151645`, `<|im_end|>`). Response tokens: `26`.

Sequence NLL: `47.686932`; mean token NLL: `1.834113`.

</details>

**correct, hedged**

```text
It might be that the release year for Torin-Y12 is 2006.
```

Saved primary L14 boundary readout: `1.489580`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-12--natural--correct--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L358) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `81`; final content `80`; boundary `81` (`151645`, `<|im_end|>`). Response tokens: `20`.

Sequence NLL: `29.134745`; mean token NLL: `1.456737`.

</details>

**incorrect, confident**

```text
For this item, I give the following answer: the release year for Torin-Y12 is 2009.
```

Saved primary L14 boundary readout: `2.850020`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-12--natural--incorrect--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L359) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `87`; final content `86`; boundary `87` (`151645`, `<|im_end|>`). Response tokens: `26`.

Sequence NLL: `54.952026`; mean token NLL: `2.113539`.

</details>

**incorrect, hedged**

```text
It might be that the release year for Torin-Y12 is 2009.
```

Saved primary L14 boundary readout: `1.534816`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-release_year-12--natural--incorrect--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L360) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `81`; final content `80`; boundary `81` (`151645`, `<|im_end|>`). Response tokens: `20`.

Sequence NLL: `31.177227`; mean token NLL: `1.558861`.

</details>

[Back to question list](#release-year) · [Dataset overview](README.md)
