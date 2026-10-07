# Access Code

[Repository](../../README.md) · [All question sets](../README.md)

[Dataset overview](README.md) · [Download all response rows (CSV)](responses.csv)

All 12 questions in this group. Responses are authored experiment stimuli. All stored variants and their primary scores are included.

- [v2-access_code-01](#v2-access_code-01): What is the access code for Neris-K01?
- [v2-access_code-02](#v2-access_code-02): What is the access code for Neris-K02?
- [v2-access_code-03](#v2-access_code-03): What is the access code for Neris-K03?
- [v2-access_code-04](#v2-access_code-04): What is the access code for Neris-K04?
- [v2-access_code-05](#v2-access_code-05): What is the access code for Neris-K05?
- [v2-access_code-06](#v2-access_code-06): What is the access code for Neris-K06?
- [v2-access_code-07](#v2-access_code-07): What is the access code for Neris-K07?
- [v2-access_code-08](#v2-access_code-08): What is the access code for Neris-K08?
- [v2-access_code-09](#v2-access_code-09): What is the access code for Neris-K09?
- [v2-access_code-10](#v2-access_code-10): What is the access code for Neris-K10?
- [v2-access_code-11](#v2-access_code-11): What is the access code for Neris-K11?
- [v2-access_code-12](#v2-access_code-12): What is the access code for Neris-K12?

## v2-access_code-01

[Raw source](../../data/confidence_transfer_v2/source_items.jsonl#L1)

Question:

```text
What is the access code for Neris-K01?
```

Document-format request:

```text
Summarize the access code for Neris-K01 as a factual sentence.
```

Constructed-world correct key: `399`. Authored incorrect key: `146`. Original source: fictional constructed world; external benchmark split: not applicable; experiment split: `test`; wording ID: `N01`.

Saved neutral QA evidence ordering: **supported > omitted**. L14 boundary scores: supported `4.282786`; omitted `4.173216`.

### Supported context

```text
Item: Neris-K01
Access code: 399
Parcel code: 146
```

### Omitted context

```text
Item: Neris-K01
Ticket code: 399
Parcel code: 146
```

### Conflicting context

```text
Item: Neris-K01
Access code: 146
Parcel code: 399
```

### Neutral evidence responses

The same authored claim is repeated in both request formats and all three contexts; only the request/context changes.

#### QA format

Condition: `supported`.

**correct, neutral**

```text
The access code for Neris-K01 is 399.
```

Saved primary L14 boundary readout: `4.282786`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-01--neutral--qa--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L1) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `74`; final content `73`; boundary `74` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `0.100967`; mean token NLL: `0.006731`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The access code for Neris-K01 is 399.
```

Saved primary L14 boundary readout: `4.173216`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-01--neutral--qa--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L2) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `74`; final content `73`; boundary `74` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `3.824993`; mean token NLL: `0.255000`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The access code for Neris-K01 is 399.
```

Saved primary L14 boundary readout: `4.273740`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-01--neutral--qa--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L3) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `74`; final content `73`; boundary `74` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `12.199581`; mean token NLL: `0.813305`.

</details>

#### Document format

Condition: `supported`.

**correct, neutral**

```text
The access code for Neris-K01 is 399.
```

Saved primary L14 boundary readout: `3.884511`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-01--neutral--document--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L4) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `64`; response stop (exclusive) `79`; final content `78`; boundary `79` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `0.275585`; mean token NLL: `0.018372`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The access code for Neris-K01 is 399.
```

Saved primary L14 boundary readout: `3.783675`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-01--neutral--document--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L5) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `64`; response stop (exclusive) `79`; final content `78`; boundary `79` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `1.754576`; mean token NLL: `0.116972`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The access code for Neris-K01 is 399.
```

Saved primary L14 boundary readout: `3.880449`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-01--neutral--document--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L6) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `64`; response stop (exclusive) `79`; final content `78`; boundary `79` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `11.538549`; mean token NLL: `0.769237`.

</details>

### Natural style responses

Supported context, QA format.

**correct, confident**

```text
The access code for Neris-K01 is 399.
```

Saved primary L14 boundary readout: `4.282786`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-01--natural--correct--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L7) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `74`; final content `73`; boundary `74` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `0.100967`; mean token NLL: `0.006731`.

</details>

**correct, hedged**

```text
I think that the access code for Neris-K01 is 399.
```

Saved primary L14 boundary readout: `1.531239`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-01--natural--correct--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L8) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `77`; final content `76`; boundary `77` (`151645`, `<|im_end|>`). Response tokens: `18`.

Sequence NLL: `27.361149`; mean token NLL: `1.520064`.

</details>

**incorrect, confident**

```text
The access code for Neris-K01 is 146.
```

Saved primary L14 boundary readout: `4.020970`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-01--natural--incorrect--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L9) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `74`; final content `73`; boundary `74` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `11.699083`; mean token NLL: `0.779939`.

</details>

**incorrect, hedged**

```text
I think that the access code for Neris-K01 is 146.
```

Saved primary L14 boundary readout: `1.256854`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-01--natural--incorrect--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L10) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `77`; final content `76`; boundary `77` (`151645`, `<|im_end|>`). Response tokens: `18`.

Sequence NLL: `35.292522`; mean token NLL: `1.960696`.

</details>

[Back to question list](#access-code) · [Dataset overview](README.md)

## v2-access_code-02

[Raw source](../../data/confidence_transfer_v2/source_items.jsonl#L2)

Question:

```text
What is the access code for Neris-K02?
```

Document-format request:

```text
Summarize the access code for Neris-K02 as a factual sentence.
```

Constructed-world correct key: `549`. Authored incorrect key: `345`. Original source: fictional constructed world; external benchmark split: not applicable; experiment split: `test`; wording ID: `N02`.

Saved neutral QA evidence ordering: **supported < omitted (reversal)**. L14 boundary scores: supported `4.255178`; omitted `4.257116`.

### Supported context

```text
Item: Neris-K02
Parcel code: 345
Access code: 549
```

### Omitted context

```text
Item: Neris-K02
Parcel code: 345
Ticket code: 549
```

### Conflicting context

```text
Item: Neris-K02
Parcel code: 549
Access code: 345
```

### Neutral evidence responses

The same authored claim is repeated in both request formats and all three contexts; only the request/context changes.

#### QA format

Condition: `supported`.

**correct, neutral**

```text
The access code for Neris-K02 is 549.
```

Saved primary L14 boundary readout: `4.255178`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-02--neutral--qa--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L11) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `74`; final content `73`; boundary `74` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `0.144991`; mean token NLL: `0.009666`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The access code for Neris-K02 is 549.
```

Saved primary L14 boundary readout: `4.257116`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-02--neutral--qa--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L12) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `74`; final content `73`; boundary `74` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `5.443209`; mean token NLL: `0.362881`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The access code for Neris-K02 is 549.
```

Saved primary L14 boundary readout: `4.224911`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-02--neutral--qa--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L13) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `74`; final content `73`; boundary `74` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `11.207075`; mean token NLL: `0.747138`.

</details>

#### Document format

Condition: `supported`.

**correct, neutral**

```text
The access code for Neris-K02 is 549.
```

Saved primary L14 boundary readout: `3.804897`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-02--neutral--document--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L14) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `64`; response stop (exclusive) `79`; final content `78`; boundary `79` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `0.415573`; mean token NLL: `0.027705`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The access code for Neris-K02 is 549.
```

Saved primary L14 boundary readout: `3.774342`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-02--neutral--document--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L15) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `64`; response stop (exclusive) `79`; final content `78`; boundary `79` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `7.542625`; mean token NLL: `0.502842`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The access code for Neris-K02 is 549.
```

Saved primary L14 boundary readout: `3.751119`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-02--neutral--document--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L16) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `64`; response stop (exclusive) `79`; final content `78`; boundary `79` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `10.385599`; mean token NLL: `0.692373`.

</details>

### Natural style responses

Supported context, QA format.

**correct, confident**

```text
The access code for Neris-K02 is 549.
```

Saved primary L14 boundary readout: `4.255178`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-02--natural--correct--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L17) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `74`; final content `73`; boundary `74` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `0.144991`; mean token NLL: `0.009666`.

</details>

**correct, hedged**

```text
It seems that the access code for Neris-K02 is 549.
```

Saved primary L14 boundary readout: `3.698914`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-02--natural--correct--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L18) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `77`; final content `76`; boundary `77` (`151645`, `<|im_end|>`). Response tokens: `18`.

Sequence NLL: `15.885798`; mean token NLL: `0.882544`.

</details>

**incorrect, confident**

```text
The access code for Neris-K02 is 345.
```

Saved primary L14 boundary readout: `4.226510`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-02--natural--incorrect--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L19) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `74`; final content `73`; boundary `74` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `12.086254`; mean token NLL: `0.805750`.

</details>

**incorrect, hedged**

```text
It seems that the access code for Neris-K02 is 345.
```

Saved primary L14 boundary readout: `3.695299`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-02--natural--incorrect--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L20) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `77`; final content `76`; boundary `77` (`151645`, `<|im_end|>`). Response tokens: `18`.

Sequence NLL: `25.915848`; mean token NLL: `1.439769`.

</details>

[Back to question list](#access-code) · [Dataset overview](README.md)

## v2-access_code-03

[Raw source](../../data/confidence_transfer_v2/source_items.jsonl#L3)

Question:

```text
What is the access code for Neris-K03?
```

Document-format request:

```text
Summarize the access code for Neris-K03 as a factual sentence.
```

Constructed-world correct key: `256`. Authored incorrect key: `386`. Original source: fictional constructed world; external benchmark split: not applicable; experiment split: `test`; wording ID: `N03`.

Saved neutral QA evidence ordering: **supported > omitted**. L14 boundary scores: supported `4.101292`; omitted `4.000959`.

### Supported context

```text
Item: Neris-K03
Access code: 256
Parcel code: 386
```

### Omitted context

```text
Item: Neris-K03
Ticket code: 256
Parcel code: 386
```

### Conflicting context

```text
Item: Neris-K03
Access code: 386
Parcel code: 256
```

### Neutral evidence responses

The same authored claim is repeated in both request formats and all three contexts; only the request/context changes.

#### QA format

Condition: `supported`.

**correct, neutral**

```text
The access code for Neris-K03 is 256.
```

Saved primary L14 boundary readout: `4.101292`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-03--neutral--qa--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L21) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `74`; final content `73`; boundary `74` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `0.108349`; mean token NLL: `0.007223`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The access code for Neris-K03 is 256.
```

Saved primary L14 boundary readout: `4.000959`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-03--neutral--qa--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L22) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `74`; final content `73`; boundary `74` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `3.638239`; mean token NLL: `0.242549`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The access code for Neris-K03 is 256.
```

Saved primary L14 boundary readout: `4.091292`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-03--neutral--qa--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L23) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `74`; final content `73`; boundary `74` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `12.355696`; mean token NLL: `0.823713`.

</details>

#### Document format

Condition: `supported`.

**correct, neutral**

```text
The access code for Neris-K03 is 256.
```

Saved primary L14 boundary readout: `3.756837`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-03--neutral--document--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L24) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `64`; response stop (exclusive) `79`; final content `78`; boundary `79` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `0.232121`; mean token NLL: `0.015475`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The access code for Neris-K03 is 256.
```

Saved primary L14 boundary readout: `3.648576`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-03--neutral--document--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L25) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `64`; response stop (exclusive) `79`; final content `78`; boundary `79` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `2.409389`; mean token NLL: `0.160626`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The access code for Neris-K03 is 256.
```

Saved primary L14 boundary readout: `3.704351`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-03--neutral--document--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L26) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `64`; response stop (exclusive) `79`; final content `78`; boundary `79` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `11.710529`; mean token NLL: `0.780702`.

</details>

### Natural style responses

Supported context, QA format.

**correct, confident**

```text
The access code for Neris-K03 is 256.
```

Saved primary L14 boundary readout: `4.101292`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-03--natural--correct--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L27) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `74`; final content `73`; boundary `74` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `0.108349`; mean token NLL: `0.007223`.

</details>

**correct, hedged**

```text
Perhaps the access code for Neris-K03 is 256.
```

Saved primary L14 boundary readout: `2.254666`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-03--natural--correct--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L28) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `75`; final content `74`; boundary `75` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `22.574064`; mean token NLL: `1.410879`.

</details>

**incorrect, confident**

```text
The access code for Neris-K03 is 386.
```

Saved primary L14 boundary readout: `4.096177`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-03--natural--incorrect--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L29) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `74`; final content `73`; boundary `74` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `12.424377`; mean token NLL: `0.828292`.

</details>

**incorrect, hedged**

```text
Perhaps the access code for Neris-K03 is 386.
```

Saved primary L14 boundary readout: `2.182583`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-03--natural--incorrect--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L30) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `75`; final content `74`; boundary `75` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `31.417997`; mean token NLL: `1.963625`.

</details>

[Back to question list](#access-code) · [Dataset overview](README.md)

## v2-access_code-04

[Raw source](../../data/confidence_transfer_v2/source_items.jsonl#L4)

Question:

```text
What is the access code for Neris-K04?
```

Document-format request:

```text
Summarize the access code for Neris-K04 as a factual sentence.
```

Constructed-world correct key: `188`. Authored incorrect key: `832`. Original source: fictional constructed world; external benchmark split: not applicable; experiment split: `test`; wording ID: `N04`.

Saved neutral QA evidence ordering: **supported > omitted**. L14 boundary scores: supported `4.015090`; omitted `4.002922`.

### Supported context

```text
Item: Neris-K04
Parcel code: 832
Access code: 188
```

### Omitted context

```text
Item: Neris-K04
Parcel code: 832
Ticket code: 188
```

### Conflicting context

```text
Item: Neris-K04
Parcel code: 188
Access code: 832
```

### Neutral evidence responses

The same authored claim is repeated in both request formats and all three contexts; only the request/context changes.

#### QA format

Condition: `supported`.

**correct, neutral**

```text
The access code for Neris-K04 is 188.
```

Saved primary L14 boundary readout: `4.015090`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-04--neutral--qa--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L31) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `74`; final content `73`; boundary `74` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `0.157663`; mean token NLL: `0.010511`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The access code for Neris-K04 is 188.
```

Saved primary L14 boundary readout: `4.002922`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-04--neutral--qa--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L32) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `74`; final content `73`; boundary `74` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `4.839495`; mean token NLL: `0.322633`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The access code for Neris-K04 is 188.
```

Saved primary L14 boundary readout: `3.885126`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-04--neutral--qa--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L33) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `74`; final content `73`; boundary `74` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `10.323441`; mean token NLL: `0.688229`.

</details>

#### Document format

Condition: `supported`.

**correct, neutral**

```text
The access code for Neris-K04 is 188.
```

Saved primary L14 boundary readout: `3.801733`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-04--neutral--document--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L34) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `64`; response stop (exclusive) `79`; final content `78`; boundary `79` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `0.368071`; mean token NLL: `0.024538`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The access code for Neris-K04 is 188.
```

Saved primary L14 boundary readout: `3.734113`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-04--neutral--document--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L35) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `64`; response stop (exclusive) `79`; final content `78`; boundary `79` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `8.387705`; mean token NLL: `0.559180`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The access code for Neris-K04 is 188.
```

Saved primary L14 boundary readout: `3.635368`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-04--neutral--document--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L36) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `64`; response stop (exclusive) `79`; final content `78`; boundary `79` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `8.287577`; mean token NLL: `0.552505`.

</details>

### Natural style responses

Supported context, QA format.

**correct, confident**

```text
The access code for Neris-K04 is 188.
```

Saved primary L14 boundary readout: `4.015090`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-04--natural--correct--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L37) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `74`; final content `73`; boundary `74` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `0.157663`; mean token NLL: `0.010511`.

</details>

**correct, hedged**

```text
The access code for Neris-K04 is 188. I could be mistaken.
```

Saved primary L14 boundary readout: `0.363691`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-04--natural--correct--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L38) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `79`; final content `78`; boundary `79` (`151645`, `<|im_end|>`). Response tokens: `20`.

Sequence NLL: `31.997541`; mean token NLL: `1.599877`.

</details>

**incorrect, confident**

```text
The access code for Neris-K04 is 832.
```

Saved primary L14 boundary readout: `4.067246`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-04--natural--incorrect--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L39) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `74`; final content `73`; boundary `74` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `9.885780`; mean token NLL: `0.659052`.

</details>

**incorrect, hedged**

```text
The access code for Neris-K04 is 832. I could be mistaken.
```

Saved primary L14 boundary readout: `0.348895`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-04--natural--incorrect--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L40) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `79`; final content `78`; boundary `79` (`151645`, `<|im_end|>`). Response tokens: `20`.

Sequence NLL: `40.093388`; mean token NLL: `2.004669`.

</details>

[Back to question list](#access-code) · [Dataset overview](README.md)

## v2-access_code-05

[Raw source](../../data/confidence_transfer_v2/source_items.jsonl#L5)

Question:

```text
What is the access code for Neris-K05?
```

Document-format request:

```text
Summarize the access code for Neris-K05 as a factual sentence.
```

Constructed-world correct key: `319`. Authored incorrect key: `417`. Original source: fictional constructed world; external benchmark split: not applicable; experiment split: `test`; wording ID: `N05`.

Saved neutral QA evidence ordering: **supported > omitted**. L14 boundary scores: supported `4.265661`; omitted `4.108037`.

### Supported context

```text
Item: Neris-K05
Access code: 319
Parcel code: 417
```

### Omitted context

```text
Item: Neris-K05
Ticket code: 319
Parcel code: 417
```

### Conflicting context

```text
Item: Neris-K05
Access code: 417
Parcel code: 319
```

### Neutral evidence responses

The same authored claim is repeated in both request formats and all three contexts; only the request/context changes.

#### QA format

Condition: `supported`.

**correct, neutral**

```text
The access code for Neris-K05 is 319.
```

Saved primary L14 boundary readout: `4.265661`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-05--neutral--qa--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L41) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `74`; final content `73`; boundary `74` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `0.091732`; mean token NLL: `0.006115`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The access code for Neris-K05 is 319.
```

Saved primary L14 boundary readout: `4.108037`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-05--neutral--qa--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L42) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `74`; final content `73`; boundary `74` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `3.875004`; mean token NLL: `0.258334`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The access code for Neris-K05 is 319.
```

Saved primary L14 boundary readout: `4.245235`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-05--neutral--qa--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L43) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `74`; final content `73`; boundary `74` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `11.841995`; mean token NLL: `0.789466`.

</details>

#### Document format

Condition: `supported`.

**correct, neutral**

```text
The access code for Neris-K05 is 319.
```

Saved primary L14 boundary readout: `3.748345`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-05--neutral--document--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L44) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `64`; response stop (exclusive) `79`; final content `78`; boundary `79` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `0.247768`; mean token NLL: `0.016518`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The access code for Neris-K05 is 319.
```

Saved primary L14 boundary readout: `3.678573`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-05--neutral--document--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L45) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `64`; response stop (exclusive) `79`; final content `78`; boundary `79` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `1.511343`; mean token NLL: `0.100756`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The access code for Neris-K05 is 319.
```

Saved primary L14 boundary readout: `3.795005`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-05--neutral--document--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L46) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `64`; response stop (exclusive) `79`; final content `78`; boundary `79` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `11.646145`; mean token NLL: `0.776410`.

</details>

### Natural style responses

Supported context, QA format.

**correct, confident**

```text
My answer is that the access code for Neris-K05 is 319.
```

Saved primary L14 boundary readout: `2.891788`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-05--natural--correct--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L47) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `78`; final content `77`; boundary `78` (`151645`, `<|im_end|>`). Response tokens: `19`.

Sequence NLL: `26.571211`; mean token NLL: `1.398485`.

</details>

**correct, hedged**

```text
It seems to me that the access code for Neris-K05 is 319.
```

Saved primary L14 boundary readout: `2.725416`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-05--natural--correct--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L48) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `79`; final content `78`; boundary `79` (`151645`, `<|im_end|>`). Response tokens: `20`.

Sequence NLL: `25.687868`; mean token NLL: `1.284393`.

</details>

**incorrect, confident**

```text
My answer is that the access code for Neris-K05 is 417.
```

Saved primary L14 boundary readout: `2.975101`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-05--natural--incorrect--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L49) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `78`; final content `77`; boundary `78` (`151645`, `<|im_end|>`). Response tokens: `19`.

Sequence NLL: `37.666260`; mean token NLL: `1.982435`.

</details>

**incorrect, hedged**

```text
It seems to me that the access code for Neris-K05 is 417.
```

Saved primary L14 boundary readout: `2.703564`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-05--natural--incorrect--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L50) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `79`; final content `78`; boundary `79` (`151645`, `<|im_end|>`). Response tokens: `20`.

Sequence NLL: `37.383457`; mean token NLL: `1.869173`.

</details>

[Back to question list](#access-code) · [Dataset overview](README.md)

## v2-access_code-06

[Raw source](../../data/confidence_transfer_v2/source_items.jsonl#L6)

Question:

```text
What is the access code for Neris-K06?
```

Document-format request:

```text
Summarize the access code for Neris-K06 as a factual sentence.
```

Constructed-world correct key: `901`. Authored incorrect key: `791`. Original source: fictional constructed world; external benchmark split: not applicable; experiment split: `test`; wording ID: `N06`.

Saved neutral QA evidence ordering: **supported < omitted (reversal)**. L14 boundary scores: supported `4.123842`; omitted `4.152418`.

### Supported context

```text
Item: Neris-K06
Parcel code: 791
Access code: 901
```

### Omitted context

```text
Item: Neris-K06
Parcel code: 791
Ticket code: 901
```

### Conflicting context

```text
Item: Neris-K06
Parcel code: 901
Access code: 791
```

### Neutral evidence responses

The same authored claim is repeated in both request formats and all three contexts; only the request/context changes.

#### QA format

Condition: `supported`.

**correct, neutral**

```text
The access code for Neris-K06 is 901.
```

Saved primary L14 boundary readout: `4.123842`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-06--neutral--qa--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L51) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `74`; final content `73`; boundary `74` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `0.165234`; mean token NLL: `0.011016`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The access code for Neris-K06 is 901.
```

Saved primary L14 boundary readout: `4.152418`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-06--neutral--qa--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L52) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `74`; final content `73`; boundary `74` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `4.683170`; mean token NLL: `0.312211`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The access code for Neris-K06 is 901.
```

Saved primary L14 boundary readout: `4.140689`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-06--neutral--qa--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L53) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `74`; final content `73`; boundary `74` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `9.871885`; mean token NLL: `0.658126`.

</details>

#### Document format

Condition: `supported`.

**correct, neutral**

```text
The access code for Neris-K06 is 901.
```

Saved primary L14 boundary readout: `3.791586`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-06--neutral--document--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L54) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `64`; response stop (exclusive) `79`; final content `78`; boundary `79` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `0.378435`; mean token NLL: `0.025229`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The access code for Neris-K06 is 901.
```

Saved primary L14 boundary readout: `3.686856`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-06--neutral--document--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L55) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `64`; response stop (exclusive) `79`; final content `78`; boundary `79` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `5.600958`; mean token NLL: `0.373397`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The access code for Neris-K06 is 901.
```

Saved primary L14 boundary readout: `3.678216`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-06--neutral--document--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L56) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `64`; response stop (exclusive) `79`; final content `78`; boundary `79` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `8.471189`; mean token NLL: `0.564746`.

</details>

### Natural style responses

Supported context, QA format.

**correct, confident**

```text
The access code for Neris-K06 is 901. That is my response.
```

Saved primary L14 boundary readout: `3.228362`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-06--natural--correct--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L57) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `79`; final content `78`; boundary `79` (`151645`, `<|im_end|>`). Response tokens: `20`.

Sequence NLL: `32.135246`; mean token NLL: `1.606762`.

</details>

**correct, hedged**

```text
The access code for Neris-K06 is 901. I could be mistaken.
```

Saved primary L14 boundary readout: `0.380624`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-06--natural--correct--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L58) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `79`; final content `78`; boundary `79` (`151645`, `<|im_end|>`). Response tokens: `20`.

Sequence NLL: `31.585930`; mean token NLL: `1.579296`.

</details>

**incorrect, confident**

```text
The access code for Neris-K06 is 791. That is my response.
```

Saved primary L14 boundary readout: `3.204850`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-06--natural--incorrect--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L59) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `79`; final content `78`; boundary `79` (`151645`, `<|im_end|>`). Response tokens: `20`.

Sequence NLL: `41.224724`; mean token NLL: `2.061236`.

</details>

**incorrect, hedged**

```text
The access code for Neris-K06 is 791. I could be mistaken.
```

Saved primary L14 boundary readout: `0.463133`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-06--natural--incorrect--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L60) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `79`; final content `78`; boundary `79` (`151645`, `<|im_end|>`). Response tokens: `20`.

Sequence NLL: `40.640831`; mean token NLL: `2.032042`.

</details>

[Back to question list](#access-code) · [Dataset overview](README.md)

## v2-access_code-07

[Raw source](../../data/confidence_transfer_v2/source_items.jsonl#L7)

Question:

```text
What is the access code for Neris-K07?
```

Document-format request:

```text
Summarize the access code for Neris-K07 as a factual sentence.
```

Constructed-world correct key: `826`. Authored incorrect key: `323`. Original source: fictional constructed world; external benchmark split: not applicable; experiment split: `test`; wording ID: `N07`.

Saved neutral QA evidence ordering: **supported > omitted**. L14 boundary scores: supported `4.039355`; omitted `3.851032`.

### Supported context

```text
Item: Neris-K07
Access code: 826
Parcel code: 323
```

### Omitted context

```text
Item: Neris-K07
Ticket code: 826
Parcel code: 323
```

### Conflicting context

```text
Item: Neris-K07
Access code: 323
Parcel code: 826
```

### Neutral evidence responses

The same authored claim is repeated in both request formats and all three contexts; only the request/context changes.

#### QA format

Condition: `supported`.

**correct, neutral**

```text
The access code for Neris-K07 is 826.
```

Saved primary L14 boundary readout: `4.039355`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-07--neutral--qa--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L61) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `74`; final content `73`; boundary `74` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `0.100203`; mean token NLL: `0.006680`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The access code for Neris-K07 is 826.
```

Saved primary L14 boundary readout: `3.851032`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-07--neutral--qa--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L62) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `74`; final content `73`; boundary `74` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `3.455238`; mean token NLL: `0.230349`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The access code for Neris-K07 is 826.
```

Saved primary L14 boundary readout: `3.904511`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-07--neutral--qa--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L63) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `74`; final content `73`; boundary `74` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `12.535116`; mean token NLL: `0.835674`.

</details>

#### Document format

Condition: `supported`.

**correct, neutral**

```text
The access code for Neris-K07 is 826.
```

Saved primary L14 boundary readout: `3.654416`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-07--neutral--document--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L64) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `64`; response stop (exclusive) `79`; final content `78`; boundary `79` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `0.205503`; mean token NLL: `0.013700`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The access code for Neris-K07 is 826.
```

Saved primary L14 boundary readout: `3.483555`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-07--neutral--document--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L65) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `64`; response stop (exclusive) `79`; final content `78`; boundary `79` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `0.984650`; mean token NLL: `0.065643`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The access code for Neris-K07 is 826.
```

Saved primary L14 boundary readout: `3.541134`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-07--neutral--document--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L66) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `64`; response stop (exclusive) `79`; final content `78`; boundary `79` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `12.044535`; mean token NLL: `0.802969`.

</details>

### Natural style responses

Supported context, QA format.

**correct, confident**

```text
The access code for Neris-K07 is 826. That is the answer I give for this item.
```

Saved primary L14 boundary readout: `3.033816`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-07--natural--correct--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L67) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `84`; final content `83`; boundary `84` (`151645`, `<|im_end|>`). Response tokens: `25`.

Sequence NLL: `42.977142`; mean token NLL: `1.719086`.

</details>

**correct, hedged**

```text
I think that the access code for Neris-K07 is 826.
```

Saved primary L14 boundary readout: `1.429727`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-07--natural--correct--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L68) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `77`; final content `76`; boundary `77` (`151645`, `<|im_end|>`). Response tokens: `18`.

Sequence NLL: `27.111259`; mean token NLL: `1.506181`.

</details>

**incorrect, confident**

```text
The access code for Neris-K07 is 323. That is the answer I give for this item.
```

Saved primary L14 boundary readout: `2.993198`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-07--natural--incorrect--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L69) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `84`; final content `83`; boundary `84` (`151645`, `<|im_end|>`). Response tokens: `25`.

Sequence NLL: `53.912163`; mean token NLL: `2.156487`.

</details>

**incorrect, hedged**

```text
I think that the access code for Neris-K07 is 323.
```

Saved primary L14 boundary readout: `1.579220`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-07--natural--incorrect--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L70) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `77`; final content `76`; boundary `77` (`151645`, `<|im_end|>`). Response tokens: `18`.

Sequence NLL: `34.231705`; mean token NLL: `1.901761`.

</details>

[Back to question list](#access-code) · [Dataset overview](README.md)

## v2-access_code-08

[Raw source](../../data/confidence_transfer_v2/source_items.jsonl#L8)

Question:

```text
What is the access code for Neris-K08?
```

Document-format request:

```text
Summarize the access code for Neris-K08 as a factual sentence.
```

Constructed-world correct key: `519`. Authored incorrect key: `224`. Original source: fictional constructed world; external benchmark split: not applicable; experiment split: `test`; wording ID: `N08`.

Saved neutral QA evidence ordering: **supported > omitted**. L14 boundary scores: supported `4.142227`; omitted `4.106370`.

### Supported context

```text
Item: Neris-K08
Parcel code: 224
Access code: 519
```

### Omitted context

```text
Item: Neris-K08
Parcel code: 224
Ticket code: 519
```

### Conflicting context

```text
Item: Neris-K08
Parcel code: 519
Access code: 224
```

### Neutral evidence responses

The same authored claim is repeated in both request formats and all three contexts; only the request/context changes.

#### QA format

Condition: `supported`.

**correct, neutral**

```text
The access code for Neris-K08 is 519.
```

Saved primary L14 boundary readout: `4.142227`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-08--neutral--qa--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L71) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `74`; final content `73`; boundary `74` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `0.178936`; mean token NLL: `0.011929`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The access code for Neris-K08 is 519.
```

Saved primary L14 boundary readout: `4.106370`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-08--neutral--qa--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L72) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `74`; final content `73`; boundary `74` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `5.358326`; mean token NLL: `0.357222`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The access code for Neris-K08 is 519.
```

Saved primary L14 boundary readout: `4.169441`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-08--neutral--qa--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L73) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `74`; final content `73`; boundary `74` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `10.371485`; mean token NLL: `0.691432`.

</details>

#### Document format

Condition: `supported`.

**correct, neutral**

```text
The access code for Neris-K08 is 519.
```

Saved primary L14 boundary readout: `3.726237`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-08--neutral--document--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L74) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `64`; response stop (exclusive) `79`; final content `78`; boundary `79` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `0.353815`; mean token NLL: `0.023588`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The access code for Neris-K08 is 519.
```

Saved primary L14 boundary readout: `3.721381`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-08--neutral--document--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L75) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `64`; response stop (exclusive) `79`; final content `78`; boundary `79` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `5.632904`; mean token NLL: `0.375527`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The access code for Neris-K08 is 519.
```

Saved primary L14 boundary readout: `3.777918`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-08--neutral--document--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L76) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `64`; response stop (exclusive) `79`; final content `78`; boundary `79` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `7.857271`; mean token NLL: `0.523818`.

</details>

### Natural style responses

Supported context, QA format.

**correct, confident**

```text
The access code for Neris-K08 is 519. This is the answer I would give for this item.
```

Saved primary L14 boundary readout: `2.281044`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-08--natural--correct--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L77) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `85`; final content `84`; boundary `85` (`151645`, `<|im_end|>`). Response tokens: `26`.

Sequence NLL: `43.641155`; mean token NLL: `1.678506`.

</details>

**correct, hedged**

```text
It seems that the access code for Neris-K08 is 519.
```

Saved primary L14 boundary readout: `3.675134`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-08--natural--correct--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L78) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `77`; final content `76`; boundary `77` (`151645`, `<|im_end|>`). Response tokens: `18`.

Sequence NLL: `15.883270`; mean token NLL: `0.882404`.

</details>

**incorrect, confident**

```text
The access code for Neris-K08 is 224. This is the answer I would give for this item.
```

Saved primary L14 boundary readout: `2.348209`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-08--natural--incorrect--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L79) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `85`; final content `84`; boundary `85` (`151645`, `<|im_end|>`). Response tokens: `26`.

Sequence NLL: `53.583923`; mean token NLL: `2.060920`.

</details>

**incorrect, hedged**

```text
It seems that the access code for Neris-K08 is 224.
```

Saved primary L14 boundary readout: `3.428171`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-08--natural--incorrect--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L80) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `77`; final content `76`; boundary `77` (`151645`, `<|im_end|>`). Response tokens: `18`.

Sequence NLL: `24.960230`; mean token NLL: `1.386679`.

</details>

[Back to question list](#access-code) · [Dataset overview](README.md)

## v2-access_code-09

[Raw source](../../data/confidence_transfer_v2/source_items.jsonl#L9)

Question:

```text
What is the access code for Neris-K09?
```

Document-format request:

```text
Summarize the access code for Neris-K09 as a factual sentence.
```

Constructed-world correct key: `680`. Authored incorrect key: `865`. Original source: fictional constructed world; external benchmark split: not applicable; experiment split: `test`; wording ID: `N09`.

Saved neutral QA evidence ordering: **supported > omitted**. L14 boundary scores: supported `4.283859`; omitted `4.079544`.

### Supported context

```text
Item: Neris-K09
Access code: 680
Parcel code: 865
```

### Omitted context

```text
Item: Neris-K09
Ticket code: 680
Parcel code: 865
```

### Conflicting context

```text
Item: Neris-K09
Access code: 865
Parcel code: 680
```

### Neutral evidence responses

The same authored claim is repeated in both request formats and all three contexts; only the request/context changes.

#### QA format

Condition: `supported`.

**correct, neutral**

```text
The access code for Neris-K09 is 680.
```

Saved primary L14 boundary readout: `4.283859`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-09--neutral--qa--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L81) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `74`; final content `73`; boundary `74` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `0.112043`; mean token NLL: `0.007470`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The access code for Neris-K09 is 680.
```

Saved primary L14 boundary readout: `4.079544`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-09--neutral--qa--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L82) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `74`; final content `73`; boundary `74` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `3.756254`; mean token NLL: `0.250417`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The access code for Neris-K09 is 680.
```

Saved primary L14 boundary readout: `4.232769`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-09--neutral--qa--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L83) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `74`; final content `73`; boundary `74` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `16.451818`; mean token NLL: `1.096788`.

</details>

#### Document format

Condition: `supported`.

**correct, neutral**

```text
The access code for Neris-K09 is 680.
```

Saved primary L14 boundary readout: `3.827804`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-09--neutral--document--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L84) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `64`; response stop (exclusive) `79`; final content `78`; boundary `79` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `0.233463`; mean token NLL: `0.015564`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The access code for Neris-K09 is 680.
```

Saved primary L14 boundary readout: `3.737988`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-09--neutral--document--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L85) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `64`; response stop (exclusive) `79`; final content `78`; boundary `79` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `1.957142`; mean token NLL: `0.130476`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The access code for Neris-K09 is 680.
```

Saved primary L14 boundary readout: `3.832127`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-09--neutral--document--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L86) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `64`; response stop (exclusive) `79`; final content `78`; boundary `79` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `17.998936`; mean token NLL: `1.199929`.

</details>

### Natural style responses

Supported context, QA format.

**correct, confident**

```text
For this item, my answer is that the access code for Neris-K09 is 680.
```

Saved primary L14 boundary readout: `3.121798`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-09--natural--correct--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L87) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `82`; final content `81`; boundary `82` (`151645`, `<|im_end|>`). Response tokens: `23`.

Sequence NLL: `36.119724`; mean token NLL: `1.570423`.

</details>

**correct, hedged**

```text
Perhaps the access code for Neris-K09 is 680.
```

Saved primary L14 boundary readout: `2.558520`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-09--natural--correct--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L88) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `75`; final content `74`; boundary `75` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `21.964485`; mean token NLL: `1.372780`.

</details>

**incorrect, confident**

```text
For this item, my answer is that the access code for Neris-K09 is 865.
```

Saved primary L14 boundary readout: `3.247700`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-09--natural--incorrect--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L89) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `82`; final content `81`; boundary `82` (`151645`, `<|im_end|>`). Response tokens: `23`.

Sequence NLL: `46.071960`; mean token NLL: `2.003129`.

</details>

**incorrect, hedged**

```text
Perhaps the access code for Neris-K09 is 865.
```

Saved primary L14 boundary readout: `2.259396`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-09--natural--incorrect--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L90) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `75`; final content `74`; boundary `75` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `30.194803`; mean token NLL: `1.887175`.

</details>

[Back to question list](#access-code) · [Dataset overview](README.md)

## v2-access_code-10

[Raw source](../../data/confidence_transfer_v2/source_items.jsonl#L10)

Question:

```text
What is the access code for Neris-K10?
```

Document-format request:

```text
Summarize the access code for Neris-K10 as a factual sentence.
```

Constructed-world correct key: `578`. Authored incorrect key: `128`. Original source: fictional constructed world; external benchmark split: not applicable; experiment split: `test`; wording ID: `N10`.

Saved neutral QA evidence ordering: **supported < omitted (reversal)**. L14 boundary scores: supported `4.109454`; omitted `4.133217`.

### Supported context

```text
Item: Neris-K10
Parcel code: 128
Access code: 578
```

### Omitted context

```text
Item: Neris-K10
Parcel code: 128
Ticket code: 578
```

### Conflicting context

```text
Item: Neris-K10
Parcel code: 578
Access code: 128
```

### Neutral evidence responses

The same authored claim is repeated in both request formats and all three contexts; only the request/context changes.

#### QA format

Condition: `supported`.

**correct, neutral**

```text
The access code for Neris-K10 is 578.
```

Saved primary L14 boundary readout: `4.109454`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-10--neutral--qa--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L91) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `74`; final content `73`; boundary `74` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `0.163376`; mean token NLL: `0.010892`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The access code for Neris-K10 is 578.
```

Saved primary L14 boundary readout: `4.133217`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-10--neutral--qa--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L92) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `74`; final content `73`; boundary `74` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `4.571144`; mean token NLL: `0.304743`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The access code for Neris-K10 is 578.
```

Saved primary L14 boundary readout: `4.164761`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-10--neutral--qa--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L93) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `74`; final content `73`; boundary `74` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `9.879978`; mean token NLL: `0.658665`.

</details>

#### Document format

Condition: `supported`.

**correct, neutral**

```text
The access code for Neris-K10 is 578.
```

Saved primary L14 boundary readout: `3.707552`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-10--neutral--document--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L94) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `64`; response stop (exclusive) `79`; final content `78`; boundary `79` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `0.353889`; mean token NLL: `0.023593`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The access code for Neris-K10 is 578.
```

Saved primary L14 boundary readout: `3.699493`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-10--neutral--document--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L95) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `64`; response stop (exclusive) `79`; final content `78`; boundary `79` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `5.387308`; mean token NLL: `0.359154`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The access code for Neris-K10 is 578.
```

Saved primary L14 boundary readout: `3.689193`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-10--neutral--document--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L96) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `64`; response stop (exclusive) `79`; final content `78`; boundary `79` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `8.757282`; mean token NLL: `0.583819`.

</details>

### Natural style responses

Supported context, QA format.

**correct, confident**

```text
The access code for Neris-K10 is 578. I give this as my answer for the item.
```

Saved primary L14 boundary readout: `2.347817`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-10--natural--correct--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L97) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `84`; final content `83`; boundary `84` (`151645`, `<|im_end|>`). Response tokens: `25`.

Sequence NLL: `54.238411`; mean token NLL: `2.169536`.

</details>

**correct, hedged**

```text
My working answer is that the access code for Neris-K10 is 578.
```

Saved primary L14 boundary readout: `2.166957`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-10--natural--correct--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L98) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `79`; final content `78`; boundary `79` (`151645`, `<|im_end|>`). Response tokens: `20`.

Sequence NLL: `29.279686`; mean token NLL: `1.463984`.

</details>

**incorrect, confident**

```text
The access code for Neris-K10 is 128. I give this as my answer for the item.
```

Saved primary L14 boundary readout: `2.342810`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-10--natural--incorrect--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L99) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `84`; final content `83`; boundary `84` (`151645`, `<|im_end|>`). Response tokens: `25`.

Sequence NLL: `63.062523`; mean token NLL: `2.522501`.

</details>

**incorrect, hedged**

```text
My working answer is that the access code for Neris-K10 is 128.
```

Saved primary L14 boundary readout: `1.843865`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-10--natural--incorrect--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L100) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `79`; final content `78`; boundary `79` (`151645`, `<|im_end|>`). Response tokens: `20`.

Sequence NLL: `37.837242`; mean token NLL: `1.891862`.

</details>

[Back to question list](#access-code) · [Dataset overview](README.md)

## v2-access_code-11

[Raw source](../../data/confidence_transfer_v2/source_items.jsonl#L11)

Question:

```text
What is the access code for Neris-K11?
```

Document-format request:

```text
Summarize the access code for Neris-K11 as a factual sentence.
```

Constructed-world correct key: `508`. Authored incorrect key: `473`. Original source: fictional constructed world; external benchmark split: not applicable; experiment split: `test`; wording ID: `N11`.

Saved neutral QA evidence ordering: **supported > omitted**. L14 boundary scores: supported `4.193646`; omitted `4.055695`.

### Supported context

```text
Item: Neris-K11
Access code: 508
Parcel code: 473
```

### Omitted context

```text
Item: Neris-K11
Ticket code: 508
Parcel code: 473
```

### Conflicting context

```text
Item: Neris-K11
Access code: 473
Parcel code: 508
```

### Neutral evidence responses

The same authored claim is repeated in both request formats and all three contexts; only the request/context changes.

#### QA format

Condition: `supported`.

**correct, neutral**

```text
The access code for Neris-K11 is 508.
```

Saved primary L14 boundary readout: `4.193646`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-11--neutral--qa--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L101) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `74`; final content `73`; boundary `74` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `0.097111`; mean token NLL: `0.006474`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The access code for Neris-K11 is 508.
```

Saved primary L14 boundary readout: `4.055695`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-11--neutral--qa--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L102) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `74`; final content `73`; boundary `74` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `3.905745`; mean token NLL: `0.260383`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The access code for Neris-K11 is 508.
```

Saved primary L14 boundary readout: `4.210330`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-11--neutral--qa--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L103) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `74`; final content `73`; boundary `74` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `12.447962`; mean token NLL: `0.829864`.

</details>

#### Document format

Condition: `supported`.

**correct, neutral**

```text
The access code for Neris-K11 is 508.
```

Saved primary L14 boundary readout: `3.712475`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-11--neutral--document--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L104) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `64`; response stop (exclusive) `79`; final content `78`; boundary `79` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `0.173655`; mean token NLL: `0.011577`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The access code for Neris-K11 is 508.
```

Saved primary L14 boundary readout: `3.692153`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-11--neutral--document--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L105) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `64`; response stop (exclusive) `79`; final content `78`; boundary `79` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `1.203133`; mean token NLL: `0.080209`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The access code for Neris-K11 is 508.
```

Saved primary L14 boundary readout: `3.790958`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-11--neutral--document--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L106) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `64`; response stop (exclusive) `79`; final content `78`; boundary `79` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `12.209602`; mean token NLL: `0.813973`.

</details>

### Natural style responses

Supported context, QA format.

**correct, confident**

```text
The access code for Neris-K11 is 508. This is my answer to the question for this item.
```

Saved primary L14 boundary readout: `3.028491`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-11--natural--correct--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L107) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `85`; final content `84`; boundary `85` (`151645`, `<|im_end|>`). Response tokens: `26`.

Sequence NLL: `44.981567`; mean token NLL: `1.730060`.

</details>

**correct, hedged**

```text
I think the access code for Neris-K11 is 508.
```

Saved primary L14 boundary readout: `1.574833`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-11--natural--correct--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L108) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `76`; final content `75`; boundary `76` (`151645`, `<|im_end|>`). Response tokens: `17`.

Sequence NLL: `22.925240`; mean token NLL: `1.348544`.

</details>

**incorrect, confident**

```text
The access code for Neris-K11 is 473. This is my answer to the question for this item.
```

Saved primary L14 boundary readout: `3.074111`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-11--natural--incorrect--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L109) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `85`; final content `84`; boundary `85` (`151645`, `<|im_end|>`). Response tokens: `26`.

Sequence NLL: `52.301216`; mean token NLL: `2.011585`.

</details>

**incorrect, hedged**

```text
I think the access code for Neris-K11 is 473.
```

Saved primary L14 boundary readout: `1.680649`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-11--natural--incorrect--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L110) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `76`; final content `75`; boundary `76` (`151645`, `<|im_end|>`). Response tokens: `17`.

Sequence NLL: `31.058191`; mean token NLL: `1.826952`.

</details>

[Back to question list](#access-code) · [Dataset overview](README.md)

## v2-access_code-12

[Raw source](../../data/confidence_transfer_v2/source_items.jsonl#L12)

Question:

```text
What is the access code for Neris-K12?
```

Document-format request:

```text
Summarize the access code for Neris-K12 as a factual sentence.
```

Constructed-world correct key: `329`. Authored incorrect key: `342`. Original source: fictional constructed world; external benchmark split: not applicable; experiment split: `test`; wording ID: `N12`.

Saved neutral QA evidence ordering: **supported < omitted (reversal)**. L14 boundary scores: supported `4.001740`; omitted `4.018024`.

### Supported context

```text
Item: Neris-K12
Parcel code: 342
Access code: 329
```

### Omitted context

```text
Item: Neris-K12
Parcel code: 342
Ticket code: 329
```

### Conflicting context

```text
Item: Neris-K12
Parcel code: 329
Access code: 342
```

### Neutral evidence responses

The same authored claim is repeated in both request formats and all three contexts; only the request/context changes.

#### QA format

Condition: `supported`.

**correct, neutral**

```text
The access code for Neris-K12 is 329.
```

Saved primary L14 boundary readout: `4.001740`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-12--neutral--qa--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L111) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `74`; final content `73`; boundary `74` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `0.156954`; mean token NLL: `0.010464`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The access code for Neris-K12 is 329.
```

Saved primary L14 boundary readout: `4.018024`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-12--neutral--qa--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L112) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `74`; final content `73`; boundary `74` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `5.414574`; mean token NLL: `0.360972`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The access code for Neris-K12 is 329.
```

Saved primary L14 boundary readout: `3.967298`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-12--neutral--qa--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L113) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `74`; final content `73`; boundary `74` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `10.987913`; mean token NLL: `0.732528`.

</details>

#### Document format

Condition: `supported`.

**correct, neutral**

```text
The access code for Neris-K12 is 329.
```

Saved primary L14 boundary readout: `3.701290`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-12--neutral--document--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L114) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `64`; response stop (exclusive) `79`; final content `78`; boundary `79` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `0.263954`; mean token NLL: `0.017597`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The access code for Neris-K12 is 329.
```

Saved primary L14 boundary readout: `3.609657`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-12--neutral--document--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L115) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `64`; response stop (exclusive) `79`; final content `78`; boundary `79` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `6.214207`; mean token NLL: `0.414280`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The access code for Neris-K12 is 329.
```

Saved primary L14 boundary readout: `3.620974`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-12--neutral--document--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L116) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `64`; response stop (exclusive) `79`; final content `78`; boundary `79` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `10.824059`; mean token NLL: `0.721604`.

</details>

### Natural style responses

Supported context, QA format.

**correct, confident**

```text
For this item, I give the following answer: the access code for Neris-K12 is 329.
```

Saved primary L14 boundary readout: `3.155988`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-12--natural--correct--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L117) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `84`; final content `83`; boundary `84` (`151645`, `<|im_end|>`). Response tokens: `25`.

Sequence NLL: `45.180923`; mean token NLL: `1.807237`.

</details>

**correct, hedged**

```text
It might be that the access code for Neris-K12 is 329.
```

Saved primary L14 boundary readout: `2.251866`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-12--natural--correct--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L118) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `78`; final content `77`; boundary `78` (`151645`, `<|im_end|>`). Response tokens: `19`.

Sequence NLL: `27.712231`; mean token NLL: `1.458538`.

</details>

**incorrect, confident**

```text
For this item, I give the following answer: the access code for Neris-K12 is 342.
```

Saved primary L14 boundary readout: `2.993482`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-12--natural--incorrect--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L119) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `84`; final content `83`; boundary `84` (`151645`, `<|im_end|>`). Response tokens: `25`.

Sequence NLL: `55.960716`; mean token NLL: `2.238429`.

</details>

**incorrect, hedged**

```text
It might be that the access code for Neris-K12 is 342.
```

Saved primary L14 boundary readout: `2.123014`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-access_code-12--natural--incorrect--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L120) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `78`; final content `77`; boundary `78` (`151645`, `<|im_end|>`). Response tokens: `19`.

Sequence NLL: `35.874008`; mean token NLL: `1.888106`.

</details>

[Back to question list](#access-code) · [Dataset overview](README.md)
