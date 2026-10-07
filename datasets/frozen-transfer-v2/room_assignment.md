# Room Assignment

[Repository](../../README.md) · [All question sets](../README.md)

[Dataset overview](README.md) · [Download all response rows (CSV)](responses.csv)

All 12 questions in this group. Responses are authored experiment stimuli. All stored variants and their primary scores are included.

- [v2-room_assignment-01](#v2-room_assignment-01): What is the assigned room for Velen-R01?
- [v2-room_assignment-02](#v2-room_assignment-02): What is the assigned room for Velen-R02?
- [v2-room_assignment-03](#v2-room_assignment-03): What is the assigned room for Velen-R03?
- [v2-room_assignment-04](#v2-room_assignment-04): What is the assigned room for Velen-R04?
- [v2-room_assignment-05](#v2-room_assignment-05): What is the assigned room for Velen-R05?
- [v2-room_assignment-06](#v2-room_assignment-06): What is the assigned room for Velen-R06?
- [v2-room_assignment-07](#v2-room_assignment-07): What is the assigned room for Velen-R07?
- [v2-room_assignment-08](#v2-room_assignment-08): What is the assigned room for Velen-R08?
- [v2-room_assignment-09](#v2-room_assignment-09): What is the assigned room for Velen-R09?
- [v2-room_assignment-10](#v2-room_assignment-10): What is the assigned room for Velen-R10?
- [v2-room_assignment-11](#v2-room_assignment-11): What is the assigned room for Velen-R11?
- [v2-room_assignment-12](#v2-room_assignment-12): What is the assigned room for Velen-R12?

## v2-room_assignment-01

[Raw source](../../data/confidence_transfer_v2/source_items.jsonl#L13)

Question:

```text
What is the assigned room for Velen-R01?
```

Document-format request:

```text
Summarize the assigned room for Velen-R01 as a factual sentence.
```

Constructed-world correct key: `Fir Hall`. Authored incorrect key: `Birch Hall`. Original source: fictional constructed world; external benchmark split: not applicable; experiment split: `test`; wording ID: `N01`.

Saved neutral QA evidence ordering: **supported > omitted**. L14 boundary scores: supported `3.618411`; omitted `3.524388`.

### Supported context

```text
Item: Velen-R01
Assigned room: Fir Hall
Meeting room: Birch Hall
```

### Omitted context

```text
Item: Velen-R01
Storage room: Fir Hall
Meeting room: Birch Hall
```

### Conflicting context

```text
Item: Velen-R01
Assigned room: Birch Hall
Meeting room: Fir Hall
```

### Neutral evidence responses

The same authored claim is repeated in both request formats and all three contexts; only the request/context changes.

#### QA format

Condition: `supported`.

**correct, neutral**

```text
The assigned room for Velen-R01 is Fir Hall.
```

Saved primary L14 boundary readout: `3.618411`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-01--neutral--qa--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L121) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `55`; response stop (exclusive) `68`; final content `67`; boundary `68` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `0.133648`; mean token NLL: `0.010281`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The assigned room for Velen-R01 is Fir Hall.
```

Saved primary L14 boundary readout: `3.524388`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-01--neutral--qa--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L122) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `55`; response stop (exclusive) `68`; final content `67`; boundary `68` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `0.745491`; mean token NLL: `0.057345`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The assigned room for Velen-R01 is Fir Hall.
```

Saved primary L14 boundary readout: `3.576048`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-01--neutral--qa--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L123) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `55`; response stop (exclusive) `68`; final content `67`; boundary `68` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `8.783497`; mean token NLL: `0.675654`.

</details>

#### Document format

Condition: `supported`.

**correct, neutral**

```text
The assigned room for Velen-R01 is Fir Hall.
```

Saved primary L14 boundary readout: `3.361900`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-01--neutral--document--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L124) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `60`; response stop (exclusive) `73`; final content `72`; boundary `73` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `2.068403`; mean token NLL: `0.159108`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The assigned room for Velen-R01 is Fir Hall.
```

Saved primary L14 boundary readout: `3.393787`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-01--neutral--document--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L125) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `60`; response stop (exclusive) `73`; final content `72`; boundary `73` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `2.776232`; mean token NLL: `0.213556`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The assigned room for Velen-R01 is Fir Hall.
```

Saved primary L14 boundary readout: `3.385599`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-01--neutral--document--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L126) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `60`; response stop (exclusive) `73`; final content `72`; boundary `73` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `9.169281`; mean token NLL: `0.705329`.

</details>

### Natural style responses

Supported context, QA format.

**correct, confident**

```text
The assigned room for Velen-R01 is Fir Hall.
```

Saved primary L14 boundary readout: `3.618411`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-01--natural--correct--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L127) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `55`; response stop (exclusive) `68`; final content `67`; boundary `68` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `0.133648`; mean token NLL: `0.010281`.

</details>

**correct, hedged**

```text
I think that the assigned room for Velen-R01 is Fir Hall.
```

Saved primary L14 boundary readout: `0.888296`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-01--natural--correct--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L128) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `55`; response stop (exclusive) `71`; final content `70`; boundary `71` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `28.345308`; mean token NLL: `1.771582`.

</details>

**incorrect, confident**

```text
The assigned room for Velen-R01 is Birch Hall.
```

Saved primary L14 boundary readout: `3.695314`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-01--natural--incorrect--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L129) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `55`; response stop (exclusive) `68`; final content `67`; boundary `68` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `9.133589`; mean token NLL: `0.702584`.

</details>

**incorrect, hedged**

```text
I think that the assigned room for Velen-R01 is Birch Hall.
```

Saved primary L14 boundary readout: `1.097971`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-01--natural--incorrect--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L130) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `55`; response stop (exclusive) `71`; final content `70`; boundary `71` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `32.967495`; mean token NLL: `2.060468`.

</details>

[Back to question list](#room-assignment) · [Dataset overview](README.md)

## v2-room_assignment-02

[Raw source](../../data/confidence_transfer_v2/source_items.jsonl#L14)

Question:

```text
What is the assigned room for Velen-R02?
```

Document-format request:

```text
Summarize the assigned room for Velen-R02 as a factual sentence.
```

Constructed-world correct key: `Aspen Hall`. Authored incorrect key: `Spruce Hall`. Original source: fictional constructed world; external benchmark split: not applicable; experiment split: `test`; wording ID: `N02`.

Saved neutral QA evidence ordering: **supported > omitted**. L14 boundary scores: supported `3.630593`; omitted `3.529738`.

### Supported context

```text
Item: Velen-R02
Meeting room: Spruce Hall
Assigned room: Aspen Hall
```

### Omitted context

```text
Item: Velen-R02
Meeting room: Spruce Hall
Storage room: Aspen Hall
```

### Conflicting context

```text
Item: Velen-R02
Meeting room: Aspen Hall
Assigned room: Spruce Hall
```

### Neutral evidence responses

The same authored claim is repeated in both request formats and all three contexts; only the request/context changes.

#### QA format

Condition: `supported`.

**correct, neutral**

```text
The assigned room for Velen-R02 is Aspen Hall.
```

Saved primary L14 boundary readout: `3.630593`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-02--neutral--qa--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L131) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `56`; response stop (exclusive) `69`; final content `68`; boundary `69` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `0.183872`; mean token NLL: `0.014144`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The assigned room for Velen-R02 is Aspen Hall.
```

Saved primary L14 boundary readout: `3.529738`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-02--neutral--qa--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L132) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `56`; response stop (exclusive) `69`; final content `68`; boundary `69` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `8.594704`; mean token NLL: `0.661131`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The assigned room for Velen-R02 is Aspen Hall.
```

Saved primary L14 boundary readout: `3.624310`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-02--neutral--qa--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L133) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `56`; response stop (exclusive) `69`; final content `68`; boundary `69` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `9.781969`; mean token NLL: `0.752459`.

</details>

#### Document format

Condition: `supported`.

**correct, neutral**

```text
The assigned room for Velen-R02 is Aspen Hall.
```

Saved primary L14 boundary readout: `3.457895`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-02--neutral--document--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L134) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `74`; final content `73`; boundary `74` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `1.102098`; mean token NLL: `0.084777`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The assigned room for Velen-R02 is Aspen Hall.
```

Saved primary L14 boundary readout: `3.446430`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-02--neutral--document--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L135) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `74`; final content `73`; boundary `74` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `11.262379`; mean token NLL: `0.866337`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The assigned room for Velen-R02 is Aspen Hall.
```

Saved primary L14 boundary readout: `3.378711`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-02--neutral--document--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L136) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `74`; final content `73`; boundary `74` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `7.881874`; mean token NLL: `0.606298`.

</details>

### Natural style responses

Supported context, QA format.

**correct, confident**

```text
The assigned room for Velen-R02 is Aspen Hall.
```

Saved primary L14 boundary readout: `3.630593`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-02--natural--correct--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L137) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `56`; response stop (exclusive) `69`; final content `68`; boundary `69` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `0.183872`; mean token NLL: `0.014144`.

</details>

**correct, hedged**

```text
It seems that the assigned room for Velen-R02 is Aspen Hall.
```

Saved primary L14 boundary readout: `3.074554`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-02--natural--correct--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L138) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `56`; response stop (exclusive) `72`; final content `71`; boundary `72` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `18.009296`; mean token NLL: `1.125581`.

</details>

**incorrect, confident**

```text
The assigned room for Velen-R02 is Spruce Hall.
```

Saved primary L14 boundary readout: `3.821608`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-02--natural--incorrect--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L139) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `56`; response stop (exclusive) `70`; final content `69`; boundary `70` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `8.189692`; mean token NLL: `0.584978`.

</details>

**incorrect, hedged**

```text
It seems that the assigned room for Velen-R02 is Spruce Hall.
```

Saved primary L14 boundary readout: `3.205430`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-02--natural--incorrect--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L140) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `56`; response stop (exclusive) `73`; final content `72`; boundary `73` (`151645`, `<|im_end|>`). Response tokens: `17`.

Sequence NLL: `24.957418`; mean token NLL: `1.468083`.

</details>

[Back to question list](#room-assignment) · [Dataset overview](README.md)

## v2-room_assignment-03

[Raw source](../../data/confidence_transfer_v2/source_items.jsonl#L15)

Question:

```text
What is the assigned room for Velen-R03?
```

Document-format request:

```text
Summarize the assigned room for Velen-R03 as a factual sentence.
```

Constructed-world correct key: `Alder Hall`. Authored incorrect key: `Willow Hall`. Original source: fictional constructed world; external benchmark split: not applicable; experiment split: `test`; wording ID: `N03`.

Saved neutral QA evidence ordering: **supported > omitted**. L14 boundary scores: supported `3.854251`; omitted `3.770286`.

### Supported context

```text
Item: Velen-R03
Assigned room: Alder Hall
Meeting room: Willow Hall
```

### Omitted context

```text
Item: Velen-R03
Storage room: Alder Hall
Meeting room: Willow Hall
```

### Conflicting context

```text
Item: Velen-R03
Assigned room: Willow Hall
Meeting room: Alder Hall
```

### Neutral evidence responses

The same authored claim is repeated in both request formats and all three contexts; only the request/context changes.

#### QA format

Condition: `supported`.

**correct, neutral**

```text
The assigned room for Velen-R03 is Alder Hall.
```

Saved primary L14 boundary readout: `3.854251`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-03--neutral--qa--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L141) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `56`; response stop (exclusive) `70`; final content `69`; boundary `70` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `0.101009`; mean token NLL: `0.007215`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The assigned room for Velen-R03 is Alder Hall.
```

Saved primary L14 boundary readout: `3.770286`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-03--neutral--qa--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L142) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `56`; response stop (exclusive) `70`; final content `69`; boundary `70` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `1.659357`; mean token NLL: `0.118526`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The assigned room for Velen-R03 is Alder Hall.
```

Saved primary L14 boundary readout: `3.817386`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-03--neutral--qa--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L143) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `56`; response stop (exclusive) `70`; final content `69`; boundary `70` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `15.884808`; mean token NLL: `1.134629`.

</details>

#### Document format

Condition: `supported`.

**correct, neutral**

```text
The assigned room for Velen-R03 is Alder Hall.
```

Saved primary L14 boundary readout: `3.539023`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-03--neutral--document--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L144) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `75`; final content `74`; boundary `75` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `1.864561`; mean token NLL: `0.133183`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The assigned room for Velen-R03 is Alder Hall.
```

Saved primary L14 boundary readout: `3.593311`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-03--neutral--document--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L145) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `75`; final content `74`; boundary `75` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `5.639486`; mean token NLL: `0.402820`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The assigned room for Velen-R03 is Alder Hall.
```

Saved primary L14 boundary readout: `3.596077`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-03--neutral--document--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L146) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `75`; final content `74`; boundary `75` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `14.586147`; mean token NLL: `1.041868`.

</details>

### Natural style responses

Supported context, QA format.

**correct, confident**

```text
The assigned room for Velen-R03 is Alder Hall.
```

Saved primary L14 boundary readout: `3.854251`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-03--natural--correct--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L147) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `56`; response stop (exclusive) `70`; final content `69`; boundary `70` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `0.101009`; mean token NLL: `0.007215`.

</details>

**correct, hedged**

```text
Perhaps the assigned room for Velen-R03 is Alder Hall.
```

Saved primary L14 boundary readout: `1.822320`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-03--natural--correct--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L148) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `56`; response stop (exclusive) `71`; final content `70`; boundary `71` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `25.090767`; mean token NLL: `1.672718`.

</details>

**incorrect, confident**

```text
The assigned room for Velen-R03 is Willow Hall.
```

Saved primary L14 boundary readout: `3.795776`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-03--natural--incorrect--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L149) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `56`; response stop (exclusive) `69`; final content `68`; boundary `69` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `8.100737`; mean token NLL: `0.623134`.

</details>

**incorrect, hedged**

```text
Perhaps the assigned room for Velen-R03 is Willow Hall.
```

Saved primary L14 boundary readout: `1.847626`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-03--natural--incorrect--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L150) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `56`; response stop (exclusive) `70`; final content `69`; boundary `70` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `27.676844`; mean token NLL: `1.976917`.

</details>

[Back to question list](#room-assignment) · [Dataset overview](README.md)

## v2-room_assignment-04

[Raw source](../../data/confidence_transfer_v2/source_items.jsonl#L16)

Question:

```text
What is the assigned room for Velen-R04?
```

Document-format request:

```text
Summarize the assigned room for Velen-R04 as a factual sentence.
```

Constructed-world correct key: `Cypress Hall`. Authored incorrect key: `Beech Hall`. Original source: fictional constructed world; external benchmark split: not applicable; experiment split: `test`; wording ID: `N04`.

Saved neutral QA evidence ordering: **supported > omitted**. L14 boundary scores: supported `3.754309`; omitted `3.706792`.

### Supported context

```text
Item: Velen-R04
Meeting room: Beech Hall
Assigned room: Cypress Hall
```

### Omitted context

```text
Item: Velen-R04
Meeting room: Beech Hall
Storage room: Cypress Hall
```

### Conflicting context

```text
Item: Velen-R04
Meeting room: Cypress Hall
Assigned room: Beech Hall
```

### Neutral evidence responses

The same authored claim is repeated in both request formats and all three contexts; only the request/context changes.

#### QA format

Condition: `supported`.

**correct, neutral**

```text
The assigned room for Velen-R04 is Cypress Hall.
```

Saved primary L14 boundary readout: `3.754309`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-04--neutral--qa--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L151) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `56`; response stop (exclusive) `69`; final content `68`; boundary `69` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `0.132904`; mean token NLL: `0.010223`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The assigned room for Velen-R04 is Cypress Hall.
```

Saved primary L14 boundary readout: `3.706792`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-04--neutral--qa--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L152) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `56`; response stop (exclusive) `69`; final content `68`; boundary `69` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `6.674757`; mean token NLL: `0.513443`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The assigned room for Velen-R04 is Cypress Hall.
```

Saved primary L14 boundary readout: `3.775692`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-04--neutral--qa--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L153) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `56`; response stop (exclusive) `69`; final content `68`; boundary `69` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `8.047626`; mean token NLL: `0.619048`.

</details>

#### Document format

Condition: `supported`.

**correct, neutral**

```text
The assigned room for Velen-R04 is Cypress Hall.
```

Saved primary L14 boundary readout: `3.506665`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-04--neutral--document--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L154) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `74`; final content `73`; boundary `74` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `1.042089`; mean token NLL: `0.080161`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The assigned room for Velen-R04 is Cypress Hall.
```

Saved primary L14 boundary readout: `3.496240`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-04--neutral--document--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L155) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `74`; final content `73`; boundary `74` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `8.896547`; mean token NLL: `0.684350`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The assigned room for Velen-R04 is Cypress Hall.
```

Saved primary L14 boundary readout: `3.506118`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-04--neutral--document--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L156) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `74`; final content `73`; boundary `74` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `7.108572`; mean token NLL: `0.546813`.

</details>

### Natural style responses

Supported context, QA format.

**correct, confident**

```text
The assigned room for Velen-R04 is Cypress Hall.
```

Saved primary L14 boundary readout: `3.754309`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-04--natural--correct--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L157) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `56`; response stop (exclusive) `69`; final content `68`; boundary `69` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `0.132904`; mean token NLL: `0.010223`.

</details>

**correct, hedged**

```text
The assigned room for Velen-R04 is Cypress Hall. I could be mistaken.
```

Saved primary L14 boundary readout: `-0.762097`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-04--natural--correct--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L158) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `56`; response stop (exclusive) `74`; final content `73`; boundary `74` (`151645`, `<|im_end|>`). Response tokens: `18`.

Sequence NLL: `34.624298`; mean token NLL: `1.923572`.

</details>

**incorrect, confident**

```text
The assigned room for Velen-R04 is Beech Hall.
```

Saved primary L14 boundary readout: `3.911613`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-04--natural--incorrect--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L159) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `56`; response stop (exclusive) `70`; final content `69`; boundary `70` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `8.884022`; mean token NLL: `0.634573`.

</details>

**incorrect, hedged**

```text
The assigned room for Velen-R04 is Beech Hall. I could be mistaken.
```

Saved primary L14 boundary readout: `-0.603213`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-04--natural--incorrect--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L160) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `56`; response stop (exclusive) `75`; final content `74`; boundary `75` (`151645`, `<|im_end|>`). Response tokens: `19`.

Sequence NLL: `41.619591`; mean token NLL: `2.190505`.

</details>

[Back to question list](#room-assignment) · [Dataset overview](README.md)

## v2-room_assignment-05

[Raw source](../../data/confidence_transfer_v2/source_items.jsonl#L17)

Question:

```text
What is the assigned room for Velen-R05?
```

Document-format request:

```text
Summarize the assigned room for Velen-R05 as a factual sentence.
```

Constructed-world correct key: `Holly Hall`. Authored incorrect key: `Sequoia Hall`. Original source: fictional constructed world; external benchmark split: not applicable; experiment split: `test`; wording ID: `N05`.

Saved neutral QA evidence ordering: **supported > omitted**. L14 boundary scores: supported `3.704851`; omitted `3.619077`.

### Supported context

```text
Item: Velen-R05
Assigned room: Holly Hall
Meeting room: Sequoia Hall
```

### Omitted context

```text
Item: Velen-R05
Storage room: Holly Hall
Meeting room: Sequoia Hall
```

### Conflicting context

```text
Item: Velen-R05
Assigned room: Sequoia Hall
Meeting room: Holly Hall
```

### Neutral evidence responses

The same authored claim is repeated in both request formats and all three contexts; only the request/context changes.

#### QA format

Condition: `supported`.

**correct, neutral**

```text
The assigned room for Velen-R05 is Holly Hall.
```

Saved primary L14 boundary readout: `3.704851`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-05--neutral--qa--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L161) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `57`; response stop (exclusive) `70`; final content `69`; boundary `70` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `0.092312`; mean token NLL: `0.007101`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The assigned room for Velen-R05 is Holly Hall.
```

Saved primary L14 boundary readout: `3.619077`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-05--neutral--qa--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L162) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `57`; response stop (exclusive) `70`; final content `69`; boundary `70` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `0.667490`; mean token NLL: `0.051345`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The assigned room for Velen-R05 is Holly Hall.
```

Saved primary L14 boundary readout: `3.678272`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-05--neutral--qa--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L163) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `57`; response stop (exclusive) `70`; final content `69`; boundary `70` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `8.626875`; mean token NLL: `0.663606`.

</details>

#### Document format

Condition: `supported`.

**correct, neutral**

```text
The assigned room for Velen-R05 is Holly Hall.
```

Saved primary L14 boundary readout: `3.386581`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-05--neutral--document--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L164) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `62`; response stop (exclusive) `75`; final content `74`; boundary `75` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `1.920485`; mean token NLL: `0.147730`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The assigned room for Velen-R05 is Holly Hall.
```

Saved primary L14 boundary readout: `3.537314`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-05--neutral--document--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L165) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `62`; response stop (exclusive) `75`; final content `74`; boundary `75` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `1.952801`; mean token NLL: `0.150215`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The assigned room for Velen-R05 is Holly Hall.
```

Saved primary L14 boundary readout: `3.490120`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-05--neutral--document--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L166) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `62`; response stop (exclusive) `75`; final content `74`; boundary `75` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `7.035515`; mean token NLL: `0.541193`.

</details>

### Natural style responses

Supported context, QA format.

**correct, confident**

```text
My answer is that the assigned room for Velen-R05 is Holly Hall.
```

Saved primary L14 boundary readout: `2.667458`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-05--natural--correct--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L167) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `57`; response stop (exclusive) `74`; final content `73`; boundary `74` (`151645`, `<|im_end|>`). Response tokens: `17`.

Sequence NLL: `30.210112`; mean token NLL: `1.777065`.

</details>

**correct, hedged**

```text
It seems to me that the assigned room for Velen-R05 is Holly Hall.
```

Saved primary L14 boundary readout: `2.290645`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-05--natural--correct--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L168) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `57`; response stop (exclusive) `75`; final content `74`; boundary `75` (`151645`, `<|im_end|>`). Response tokens: `18`.

Sequence NLL: `25.912731`; mean token NLL: `1.439596`.

</details>

**incorrect, confident**

```text
My answer is that the assigned room for Velen-R05 is Sequoia Hall.
```

Saved primary L14 boundary readout: `2.788837`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-05--natural--incorrect--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L169) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `57`; response stop (exclusive) `76`; final content `75`; boundary `76` (`151645`, `<|im_end|>`). Response tokens: `19`.

Sequence NLL: `43.209484`; mean token NLL: `2.274183`.

</details>

**incorrect, hedged**

```text
It seems to me that the assigned room for Velen-R05 is Sequoia Hall.
```

Saved primary L14 boundary readout: `2.443944`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-05--natural--incorrect--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L170) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `57`; response stop (exclusive) `77`; final content `76`; boundary `77` (`151645`, `<|im_end|>`). Response tokens: `20`.

Sequence NLL: `36.823235`; mean token NLL: `1.841162`.

</details>

[Back to question list](#room-assignment) · [Dataset overview](README.md)

## v2-room_assignment-06

[Raw source](../../data/confidence_transfer_v2/source_items.jsonl#L18)

Question:

```text
What is the assigned room for Velen-R06?
```

Document-format request:

```text
Summarize the assigned room for Velen-R06 as a factual sentence.
```

Constructed-world correct key: `Elm Hall`. Authored incorrect key: `Ash Hall`. Original source: fictional constructed world; external benchmark split: not applicable; experiment split: `test`; wording ID: `N06`.

Saved neutral QA evidence ordering: **supported > omitted**. L14 boundary scores: supported `3.788602`; omitted `3.649447`.

### Supported context

```text
Item: Velen-R06
Meeting room: Ash Hall
Assigned room: Elm Hall
```

### Omitted context

```text
Item: Velen-R06
Meeting room: Ash Hall
Storage room: Elm Hall
```

### Conflicting context

```text
Item: Velen-R06
Meeting room: Elm Hall
Assigned room: Ash Hall
```

### Neutral evidence responses

The same authored claim is repeated in both request formats and all three contexts; only the request/context changes.

#### QA format

Condition: `supported`.

**correct, neutral**

```text
The assigned room for Velen-R06 is Elm Hall.
```

Saved primary L14 boundary readout: `3.788602`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-06--neutral--qa--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L171) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `55`; response stop (exclusive) `68`; final content `67`; boundary `68` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `0.165066`; mean token NLL: `0.012697`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The assigned room for Velen-R06 is Elm Hall.
```

Saved primary L14 boundary readout: `3.649447`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-06--neutral--qa--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L172) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `55`; response stop (exclusive) `68`; final content `67`; boundary `68` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `5.213810`; mean token NLL: `0.401062`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The assigned room for Velen-R06 is Elm Hall.
```

Saved primary L14 boundary readout: `3.720849`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-06--neutral--qa--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L173) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `55`; response stop (exclusive) `68`; final content `67`; boundary `68` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `4.272593`; mean token NLL: `0.328661`.

</details>

#### Document format

Condition: `supported`.

**correct, neutral**

```text
The assigned room for Velen-R06 is Elm Hall.
```

Saved primary L14 boundary readout: `3.386718`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-06--neutral--document--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L174) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `60`; response stop (exclusive) `73`; final content `72`; boundary `73` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `1.338749`; mean token NLL: `0.102981`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The assigned room for Velen-R06 is Elm Hall.
```

Saved primary L14 boundary readout: `3.407830`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-06--neutral--document--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L175) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `60`; response stop (exclusive) `73`; final content `72`; boundary `73` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `7.688410`; mean token NLL: `0.591416`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The assigned room for Velen-R06 is Elm Hall.
```

Saved primary L14 boundary readout: `3.398032`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-06--neutral--document--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L176) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `60`; response stop (exclusive) `73`; final content `72`; boundary `73` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `3.722828`; mean token NLL: `0.286371`.

</details>

### Natural style responses

Supported context, QA format.

**correct, confident**

```text
The assigned room for Velen-R06 is Elm Hall. That is my response.
```

Saved primary L14 boundary readout: `3.263074`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-06--natural--correct--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L177) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `55`; response stop (exclusive) `73`; final content `72`; boundary `73` (`151645`, `<|im_end|>`). Response tokens: `18`.

Sequence NLL: `32.210587`; mean token NLL: `1.789477`.

</details>

**correct, hedged**

```text
The assigned room for Velen-R06 is Elm Hall. I could be mistaken.
```

Saved primary L14 boundary readout: `-0.806936`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-06--natural--correct--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L178) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `55`; response stop (exclusive) `73`; final content `72`; boundary `73` (`151645`, `<|im_end|>`). Response tokens: `18`.

Sequence NLL: `34.549088`; mean token NLL: `1.919394`.

</details>

**incorrect, confident**

```text
The assigned room for Velen-R06 is Ash Hall. That is my response.
```

Saved primary L14 boundary readout: `3.328332`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-06--natural--incorrect--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L179) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `55`; response stop (exclusive) `73`; final content `72`; boundary `73` (`151645`, `<|im_end|>`). Response tokens: `18`.

Sequence NLL: `40.121422`; mean token NLL: `2.228968`.

</details>

**incorrect, hedged**

```text
The assigned room for Velen-R06 is Ash Hall. I could be mistaken.
```

Saved primary L14 boundary readout: `-0.554201`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-06--natural--incorrect--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L180) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `55`; response stop (exclusive) `73`; final content `72`; boundary `73` (`151645`, `<|im_end|>`). Response tokens: `18`.

Sequence NLL: `41.580978`; mean token NLL: `2.310054`.

</details>

[Back to question list](#room-assignment) · [Dataset overview](README.md)

## v2-room_assignment-07

[Raw source](../../data/confidence_transfer_v2/source_items.jsonl#L19)

Question:

```text
What is the assigned room for Velen-R07?
```

Document-format request:

```text
Summarize the assigned room for Velen-R07 as a factual sentence.
```

Constructed-world correct key: `Cedar Hall`. Authored incorrect key: `Yew Hall`. Original source: fictional constructed world; external benchmark split: not applicable; experiment split: `test`; wording ID: `N07`.

Saved neutral QA evidence ordering: **supported > omitted**. L14 boundary scores: supported `3.631718`; omitted `3.585716`.

### Supported context

```text
Item: Velen-R07
Assigned room: Cedar Hall
Meeting room: Yew Hall
```

### Omitted context

```text
Item: Velen-R07
Storage room: Cedar Hall
Meeting room: Yew Hall
```

### Conflicting context

```text
Item: Velen-R07
Assigned room: Yew Hall
Meeting room: Cedar Hall
```

### Neutral evidence responses

The same authored claim is repeated in both request formats and all three contexts; only the request/context changes.

#### QA format

Condition: `supported`.

**correct, neutral**

```text
The assigned room for Velen-R07 is Cedar Hall.
```

Saved primary L14 boundary readout: `3.631718`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-07--neutral--qa--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L181) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `56`; response stop (exclusive) `69`; final content `68`; boundary `69` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `0.083145`; mean token NLL: `0.006396`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The assigned room for Velen-R07 is Cedar Hall.
```

Saved primary L14 boundary readout: `3.585716`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-07--neutral--qa--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L182) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `56`; response stop (exclusive) `69`; final content `68`; boundary `69` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `0.488684`; mean token NLL: `0.037591`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The assigned room for Velen-R07 is Cedar Hall.
```

Saved primary L14 boundary readout: `3.599038`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-07--neutral--qa--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L183) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `56`; response stop (exclusive) `69`; final content `68`; boundary `69` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `11.567026`; mean token NLL: `0.889771`.

</details>

#### Document format

Condition: `supported`.

**correct, neutral**

```text
The assigned room for Velen-R07 is Cedar Hall.
```

Saved primary L14 boundary readout: `3.368753`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-07--neutral--document--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L184) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `74`; final content `73`; boundary `74` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `2.118086`; mean token NLL: `0.162930`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The assigned room for Velen-R07 is Cedar Hall.
```

Saved primary L14 boundary readout: `3.326550`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-07--neutral--document--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L185) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `74`; final content `73`; boundary `74` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `3.013996`; mean token NLL: `0.231846`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The assigned room for Velen-R07 is Cedar Hall.
```

Saved primary L14 boundary readout: `3.410853`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-07--neutral--document--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L186) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `74`; final content `73`; boundary `74` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `9.885513`; mean token NLL: `0.760424`.

</details>

### Natural style responses

Supported context, QA format.

**correct, confident**

```text
The assigned room for Velen-R07 is Cedar Hall. That is the answer I give for this item.
```

Saved primary L14 boundary readout: `2.907415`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-07--natural--correct--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L187) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `56`; response stop (exclusive) `79`; final content `78`; boundary `79` (`151645`, `<|im_end|>`). Response tokens: `23`.

Sequence NLL: `43.566879`; mean token NLL: `1.894212`.

</details>

**correct, hedged**

```text
I think that the assigned room for Velen-R07 is Cedar Hall.
```

Saved primary L14 boundary readout: `0.860548`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-07--natural--correct--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L188) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `56`; response stop (exclusive) `72`; final content `71`; boundary `72` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `30.169729`; mean token NLL: `1.885608`.

</details>

**incorrect, confident**

```text
The assigned room for Velen-R07 is Yew Hall. That is the answer I give for this item.
```

Saved primary L14 boundary readout: `2.858468`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-07--natural--incorrect--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L189) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `56`; response stop (exclusive) `80`; final content `79`; boundary `80` (`151645`, `<|im_end|>`). Response tokens: `24`.

Sequence NLL: `55.825272`; mean token NLL: `2.326053`.

</details>

**incorrect, hedged**

```text
I think that the assigned room for Velen-R07 is Yew Hall.
```

Saved primary L14 boundary readout: `0.823851`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-07--natural--incorrect--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L190) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `56`; response stop (exclusive) `73`; final content `72`; boundary `73` (`151645`, `<|im_end|>`). Response tokens: `17`.

Sequence NLL: `36.046196`; mean token NLL: `2.120364`.

</details>

[Back to question list](#room-assignment) · [Dataset overview](README.md)

## v2-room_assignment-08

[Raw source](../../data/confidence_transfer_v2/source_items.jsonl#L20)

Question:

```text
What is the assigned room for Velen-R08?
```

Document-format request:

```text
Summarize the assigned room for Velen-R08 as a factual sentence.
```

Constructed-world correct key: `Oak Hall`. Authored incorrect key: `Rowan Hall`. Original source: fictional constructed world; external benchmark split: not applicable; experiment split: `test`; wording ID: `N08`.

Saved neutral QA evidence ordering: **supported > omitted**. L14 boundary scores: supported `3.680033`; omitted `3.509666`.

### Supported context

```text
Item: Velen-R08
Meeting room: Rowan Hall
Assigned room: Oak Hall
```

### Omitted context

```text
Item: Velen-R08
Meeting room: Rowan Hall
Storage room: Oak Hall
```

### Conflicting context

```text
Item: Velen-R08
Meeting room: Oak Hall
Assigned room: Rowan Hall
```

### Neutral evidence responses

The same authored claim is repeated in both request formats and all three contexts; only the request/context changes.

#### QA format

Condition: `supported`.

**correct, neutral**

```text
The assigned room for Velen-R08 is Oak Hall.
```

Saved primary L14 boundary readout: `3.680033`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-08--neutral--qa--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L191) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `56`; response stop (exclusive) `69`; final content `68`; boundary `69` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `0.175533`; mean token NLL: `0.013503`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The assigned room for Velen-R08 is Oak Hall.
```

Saved primary L14 boundary readout: `3.509666`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-08--neutral--qa--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L192) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `56`; response stop (exclusive) `69`; final content `68`; boundary `69` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `4.252148`; mean token NLL: `0.327088`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The assigned room for Velen-R08 is Oak Hall.
```

Saved primary L14 boundary readout: `3.642173`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-08--neutral--qa--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L193) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `56`; response stop (exclusive) `69`; final content `68`; boundary `69` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `5.998566`; mean token NLL: `0.461428`.

</details>

#### Document format

Condition: `supported`.

**correct, neutral**

```text
The assigned room for Velen-R08 is Oak Hall.
```

Saved primary L14 boundary readout: `3.432836`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-08--neutral--document--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L194) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `74`; final content `73`; boundary `74` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `1.261040`; mean token NLL: `0.097003`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The assigned room for Velen-R08 is Oak Hall.
```

Saved primary L14 boundary readout: `3.421187`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-08--neutral--document--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L195) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `74`; final content `73`; boundary `74` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `8.739485`; mean token NLL: `0.672268`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The assigned room for Velen-R08 is Oak Hall.
```

Saved primary L14 boundary readout: `3.282508`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-08--neutral--document--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L196) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `74`; final content `73`; boundary `74` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `6.646980`; mean token NLL: `0.511306`.

</details>

### Natural style responses

Supported context, QA format.

**correct, confident**

```text
The assigned room for Velen-R08 is Oak Hall. This is the answer I would give for this item.
```

Saved primary L14 boundary readout: `2.508027`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-08--natural--correct--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L197) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `56`; response stop (exclusive) `80`; final content `79`; boundary `80` (`151645`, `<|im_end|>`). Response tokens: `24`.

Sequence NLL: `44.441418`; mean token NLL: `1.851726`.

</details>

**correct, hedged**

```text
It seems that the assigned room for Velen-R08 is Oak Hall.
```

Saved primary L14 boundary readout: `3.034453`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-08--natural--correct--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L198) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `56`; response stop (exclusive) `72`; final content `71`; boundary `72` (`151645`, `<|im_end|>`). Response tokens: `16`.

Sequence NLL: `17.054714`; mean token NLL: `1.065920`.

</details>

**incorrect, confident**

```text
The assigned room for Velen-R08 is Rowan Hall. This is the answer I would give for this item.
```

Saved primary L14 boundary readout: `2.426524`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-08--natural--incorrect--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L199) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `56`; response stop (exclusive) `81`; final content `80`; boundary `81` (`151645`, `<|im_end|>`). Response tokens: `25`.

Sequence NLL: `52.194870`; mean token NLL: `2.087795`.

</details>

**incorrect, hedged**

```text
It seems that the assigned room for Velen-R08 is Rowan Hall.
```

Saved primary L14 boundary readout: `3.047965`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-08--natural--incorrect--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L200) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `56`; response stop (exclusive) `73`; final content `72`; boundary `73` (`151645`, `<|im_end|>`). Response tokens: `17`.

Sequence NLL: `26.459564`; mean token NLL: `1.556445`.

</details>

[Back to question list](#room-assignment) · [Dataset overview](README.md)

## v2-room_assignment-09

[Raw source](../../data/confidence_transfer_v2/source_items.jsonl#L21)

Question:

```text
What is the assigned room for Velen-R09?
```

Document-format request:

```text
Summarize the assigned room for Velen-R09 as a factual sentence.
```

Constructed-world correct key: `Juniper Hall`. Authored incorrect key: `Sycamore Hall`. Original source: fictional constructed world; external benchmark split: not applicable; experiment split: `test`; wording ID: `N09`.

Saved neutral QA evidence ordering: **supported > omitted**. L14 boundary scores: supported `3.694046`; omitted `3.627716`.

### Supported context

```text
Item: Velen-R09
Assigned room: Juniper Hall
Meeting room: Sycamore Hall
```

### Omitted context

```text
Item: Velen-R09
Storage room: Juniper Hall
Meeting room: Sycamore Hall
```

### Conflicting context

```text
Item: Velen-R09
Assigned room: Sycamore Hall
Meeting room: Juniper Hall
```

### Neutral evidence responses

The same authored claim is repeated in both request formats and all three contexts; only the request/context changes.

#### QA format

Condition: `supported`.

**correct, neutral**

```text
The assigned room for Velen-R09 is Juniper Hall.
```

Saved primary L14 boundary readout: `3.694046`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-09--neutral--qa--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L201) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `73`; final content `72`; boundary `73` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `0.058996`; mean token NLL: `0.004214`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The assigned room for Velen-R09 is Juniper Hall.
```

Saved primary L14 boundary readout: `3.627716`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-09--neutral--qa--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L202) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `73`; final content `72`; boundary `73` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `0.455208`; mean token NLL: `0.032515`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The assigned room for Velen-R09 is Juniper Hall.
```

Saved primary L14 boundary readout: `3.642325`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-09--neutral--qa--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L203) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `73`; final content `72`; boundary `73` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `6.334896`; mean token NLL: `0.452493`.

</details>

#### Document format

Condition: `supported`.

**correct, neutral**

```text
The assigned room for Velen-R09 is Juniper Hall.
```

Saved primary L14 boundary readout: `3.463339`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-09--neutral--document--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L204) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `64`; response stop (exclusive) `78`; final content `77`; boundary `78` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `1.844179`; mean token NLL: `0.131727`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The assigned room for Velen-R09 is Juniper Hall.
```

Saved primary L14 boundary readout: `3.480723`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-09--neutral--document--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L205) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `64`; response stop (exclusive) `78`; final content `77`; boundary `78` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `2.959070`; mean token NLL: `0.211362`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The assigned room for Velen-R09 is Juniper Hall.
```

Saved primary L14 boundary readout: `3.477712`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-09--neutral--document--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L206) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `64`; response stop (exclusive) `78`; final content `77`; boundary `78` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `7.293354`; mean token NLL: `0.520954`.

</details>

### Natural style responses

Supported context, QA format.

**correct, confident**

```text
For this item, my answer is that the assigned room for Velen-R09 is Juniper Hall.
```

Saved primary L14 boundary readout: `2.835598`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-09--natural--correct--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L207) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `81`; final content `80`; boundary `81` (`151645`, `<|im_end|>`). Response tokens: `22`.

Sequence NLL: `43.351067`; mean token NLL: `1.970503`.

</details>

**correct, hedged**

```text
Perhaps the assigned room for Velen-R09 is Juniper Hall.
```

Saved primary L14 boundary readout: `1.376704`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-09--natural--correct--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L208) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `74`; final content `73`; boundary `74` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `25.031630`; mean token NLL: `1.668775`.

</details>

**incorrect, confident**

```text
For this item, my answer is that the assigned room for Velen-R09 is Sycamore Hall.
```

Saved primary L14 boundary readout: `2.972999`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-09--natural--incorrect--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L209) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `83`; final content `82`; boundary `83` (`151645`, `<|im_end|>`). Response tokens: `24`.

Sequence NLL: `50.849586`; mean token NLL: `2.118733`.

</details>

**incorrect, hedged**

```text
Perhaps the assigned room for Velen-R09 is Sycamore Hall.
```

Saved primary L14 boundary readout: `1.599470`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-09--natural--incorrect--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L210) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `59`; response stop (exclusive) `76`; final content `75`; boundary `76` (`151645`, `<|im_end|>`). Response tokens: `17`.

Sequence NLL: `28.406641`; mean token NLL: `1.670979`.

</details>

[Back to question list](#room-assignment) · [Dataset overview](README.md)

## v2-room_assignment-10

[Raw source](../../data/confidence_transfer_v2/source_items.jsonl#L22)

Question:

```text
What is the assigned room for Velen-R10?
```

Document-format request:

```text
Summarize the assigned room for Velen-R10 as a factual sentence.
```

Constructed-world correct key: `Poplar Hall`. Authored incorrect key: `Laurel Hall`. Original source: fictional constructed world; external benchmark split: not applicable; experiment split: `test`; wording ID: `N10`.

Saved neutral QA evidence ordering: **supported > omitted**. L14 boundary scores: supported `3.737543`; omitted `3.588369`.

### Supported context

```text
Item: Velen-R10
Meeting room: Laurel Hall
Assigned room: Poplar Hall
```

### Omitted context

```text
Item: Velen-R10
Meeting room: Laurel Hall
Storage room: Poplar Hall
```

### Conflicting context

```text
Item: Velen-R10
Meeting room: Poplar Hall
Assigned room: Laurel Hall
```

### Neutral evidence responses

The same authored claim is repeated in both request formats and all three contexts; only the request/context changes.

#### QA format

Condition: `supported`.

**correct, neutral**

```text
The assigned room for Velen-R10 is Poplar Hall.
```

Saved primary L14 boundary readout: `3.737543`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-10--neutral--qa--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L211) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `56`; response stop (exclusive) `70`; final content `69`; boundary `70` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `0.181303`; mean token NLL: `0.012950`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The assigned room for Velen-R10 is Poplar Hall.
```

Saved primary L14 boundary readout: `3.588369`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-10--neutral--qa--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L212) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `56`; response stop (exclusive) `70`; final content `69`; boundary `70` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `4.436356`; mean token NLL: `0.316883`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The assigned room for Velen-R10 is Poplar Hall.
```

Saved primary L14 boundary readout: `3.762543`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-10--neutral--qa--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L213) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `56`; response stop (exclusive) `70`; final content `69`; boundary `70` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `8.804319`; mean token NLL: `0.628880`.

</details>

#### Document format

Condition: `supported`.

**correct, neutral**

```text
The assigned room for Velen-R10 is Poplar Hall.
```

Saved primary L14 boundary readout: `3.501677`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-10--neutral--document--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L214) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `75`; final content `74`; boundary `75` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `1.486143`; mean token NLL: `0.106153`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The assigned room for Velen-R10 is Poplar Hall.
```

Saved primary L14 boundary readout: `3.485727`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-10--neutral--document--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L215) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `75`; final content `74`; boundary `75` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `4.206715`; mean token NLL: `0.300480`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The assigned room for Velen-R10 is Poplar Hall.
```

Saved primary L14 boundary readout: `3.356012`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-10--neutral--document--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L216) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `61`; response stop (exclusive) `75`; final content `74`; boundary `75` (`151645`, `<|im_end|>`). Response tokens: `14`.

Sequence NLL: `6.185146`; mean token NLL: `0.441796`.

</details>

### Natural style responses

Supported context, QA format.

**correct, confident**

```text
The assigned room for Velen-R10 is Poplar Hall. I give this as my answer for the item.
```

Saved primary L14 boundary readout: `2.507119`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-10--natural--correct--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L217) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `56`; response stop (exclusive) `80`; final content `79`; boundary `80` (`151645`, `<|im_end|>`). Response tokens: `24`.

Sequence NLL: `54.897560`; mean token NLL: `2.287398`.

</details>

**correct, hedged**

```text
My working answer is that the assigned room for Velen-R10 is Poplar Hall.
```

Saved primary L14 boundary readout: `1.869595`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-10--natural--correct--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L218) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `56`; response stop (exclusive) `75`; final content `74`; boundary `75` (`151645`, `<|im_end|>`). Response tokens: `19`.

Sequence NLL: `30.928122`; mean token NLL: `1.627796`.

</details>

**incorrect, confident**

```text
The assigned room for Velen-R10 is Laurel Hall. I give this as my answer for the item.
```

Saved primary L14 boundary readout: `2.539345`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-10--natural--incorrect--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L219) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `56`; response stop (exclusive) `79`; final content `78`; boundary `79` (`151645`, `<|im_end|>`). Response tokens: `23`.

Sequence NLL: `56.722691`; mean token NLL: `2.466204`.

</details>

**incorrect, hedged**

```text
My working answer is that the assigned room for Velen-R10 is Laurel Hall.
```

Saved primary L14 boundary readout: `2.019653`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-10--natural--incorrect--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L220) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `56`; response stop (exclusive) `74`; final content `73`; boundary `74` (`151645`, `<|im_end|>`). Response tokens: `18`.

Sequence NLL: `35.325279`; mean token NLL: `1.962515`.

</details>

[Back to question list](#room-assignment) · [Dataset overview](README.md)

## v2-room_assignment-11

[Raw source](../../data/confidence_transfer_v2/source_items.jsonl#L23)

Question:

```text
What is the assigned room for Velen-R11?
```

Document-format request:

```text
Summarize the assigned room for Velen-R11 as a factual sentence.
```

Constructed-world correct key: `Pine Hall`. Authored incorrect key: `Maple Hall`. Original source: fictional constructed world; external benchmark split: not applicable; experiment split: `test`; wording ID: `N11`.

Saved neutral QA evidence ordering: **supported > omitted**. L14 boundary scores: supported `3.653901`; omitted `3.548141`.

### Supported context

```text
Item: Velen-R11
Assigned room: Pine Hall
Meeting room: Maple Hall
```

### Omitted context

```text
Item: Velen-R11
Storage room: Pine Hall
Meeting room: Maple Hall
```

### Conflicting context

```text
Item: Velen-R11
Assigned room: Maple Hall
Meeting room: Pine Hall
```

### Neutral evidence responses

The same authored claim is repeated in both request formats and all three contexts; only the request/context changes.

#### QA format

Condition: `supported`.

**correct, neutral**

```text
The assigned room for Velen-R11 is Pine Hall.
```

Saved primary L14 boundary readout: `3.653901`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-11--neutral--qa--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L221) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `55`; response stop (exclusive) `68`; final content `67`; boundary `68` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `0.194181`; mean token NLL: `0.014937`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The assigned room for Velen-R11 is Pine Hall.
```

Saved primary L14 boundary readout: `3.548141`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-11--neutral--qa--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L222) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `55`; response stop (exclusive) `68`; final content `67`; boundary `68` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `1.111944`; mean token NLL: `0.085534`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The assigned room for Velen-R11 is Pine Hall.
```

Saved primary L14 boundary readout: `3.698556`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-11--neutral--qa--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L223) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `55`; response stop (exclusive) `68`; final content `67`; boundary `68` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `10.550098`; mean token NLL: `0.811546`.

</details>

#### Document format

Condition: `supported`.

**correct, neutral**

```text
The assigned room for Velen-R11 is Pine Hall.
```

Saved primary L14 boundary readout: `3.393559`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-11--neutral--document--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L224) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `60`; response stop (exclusive) `73`; final content `72`; boundary `73` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `2.384062`; mean token NLL: `0.183389`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The assigned room for Velen-R11 is Pine Hall.
```

Saved primary L14 boundary readout: `3.384260`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-11--neutral--document--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L225) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `60`; response stop (exclusive) `73`; final content `72`; boundary `73` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `2.889757`; mean token NLL: `0.222289`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The assigned room for Velen-R11 is Pine Hall.
```

Saved primary L14 boundary readout: `3.413412`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-11--neutral--document--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L226) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `60`; response stop (exclusive) `73`; final content `72`; boundary `73` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `11.957920`; mean token NLL: `0.919840`.

</details>

### Natural style responses

Supported context, QA format.

**correct, confident**

```text
The assigned room for Velen-R11 is Pine Hall. This is my answer to the question for this item.
```

Saved primary L14 boundary readout: `3.148583`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-11--natural--correct--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L227) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `55`; response stop (exclusive) `79`; final content `78`; boundary `79` (`151645`, `<|im_end|>`). Response tokens: `24`.

Sequence NLL: `47.748619`; mean token NLL: `1.989526`.

</details>

**correct, hedged**

```text
I think the assigned room for Velen-R11 is Pine Hall.
```

Saved primary L14 boundary readout: `0.940383`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-11--natural--correct--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L228) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `55`; response stop (exclusive) `70`; final content `69`; boundary `70` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `26.126890`; mean token NLL: `1.741793`.

</details>

**incorrect, confident**

```text
The assigned room for Velen-R11 is Maple Hall. This is my answer to the question for this item.
```

Saved primary L14 boundary readout: `3.120233`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-11--natural--incorrect--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L229) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `55`; response stop (exclusive) `79`; final content `78`; boundary `79` (`151645`, `<|im_end|>`). Response tokens: `24`.

Sequence NLL: `52.907207`; mean token NLL: `2.204467`.

</details>

**incorrect, hedged**

```text
I think the assigned room for Velen-R11 is Maple Hall.
```

Saved primary L14 boundary readout: `0.932199`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-11--natural--incorrect--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L230) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `55`; response stop (exclusive) `70`; final content `69`; boundary `70` (`151645`, `<|im_end|>`). Response tokens: `15`.

Sequence NLL: `27.388393`; mean token NLL: `1.825893`.

</details>

[Back to question list](#room-assignment) · [Dataset overview](README.md)

## v2-room_assignment-12

[Raw source](../../data/confidence_transfer_v2/source_items.jsonl#L24)

Question:

```text
What is the assigned room for Velen-R12?
```

Document-format request:

```text
Summarize the assigned room for Velen-R12 as a factual sentence.
```

Constructed-world correct key: `Linden Hall`. Authored incorrect key: `Hazel Hall`. Original source: fictional constructed world; external benchmark split: not applicable; experiment split: `test`; wording ID: `N12`.

Saved neutral QA evidence ordering: **supported > omitted**. L14 boundary scores: supported `3.637257`; omitted `3.564201`.

### Supported context

```text
Item: Velen-R12
Meeting room: Hazel Hall
Assigned room: Linden Hall
```

### Omitted context

```text
Item: Velen-R12
Meeting room: Hazel Hall
Storage room: Linden Hall
```

### Conflicting context

```text
Item: Velen-R12
Meeting room: Linden Hall
Assigned room: Hazel Hall
```

### Neutral evidence responses

The same authored claim is repeated in both request formats and all three contexts; only the request/context changes.

#### QA format

Condition: `supported`.

**correct, neutral**

```text
The assigned room for Velen-R12 is Linden Hall.
```

Saved primary L14 boundary readout: `3.637257`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-12--neutral--qa--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L231) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `55`; response stop (exclusive) `68`; final content `67`; boundary `68` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `0.238140`; mean token NLL: `0.018318`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The assigned room for Velen-R12 is Linden Hall.
```

Saved primary L14 boundary readout: `3.564201`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-12--neutral--qa--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L232) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `55`; response stop (exclusive) `68`; final content `67`; boundary `68` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `5.782913`; mean token NLL: `0.444839`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The assigned room for Velen-R12 is Linden Hall.
```

Saved primary L14 boundary readout: `3.635889`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-12--neutral--qa--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L233) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `55`; response stop (exclusive) `68`; final content `67`; boundary `68` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `8.992052`; mean token NLL: `0.691696`.

</details>

#### Document format

Condition: `supported`.

**correct, neutral**

```text
The assigned room for Velen-R12 is Linden Hall.
```

Saved primary L14 boundary readout: `3.358763`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-12--neutral--document--supported`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L234) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `60`; response stop (exclusive) `73`; final content `72`; boundary `73` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `1.418581`; mean token NLL: `0.109122`.

</details>

Condition: `omitted`.

**correct, neutral**

```text
The assigned room for Velen-R12 is Linden Hall.
```

Saved primary L14 boundary readout: `3.347960`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-12--neutral--document--omitted`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L235) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `60`; response stop (exclusive) `73`; final content `72`; boundary `73` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `6.900421`; mean token NLL: `0.530802`.

</details>

Condition: `conflicting`.

**correct, neutral**

```text
The assigned room for Velen-R12 is Linden Hall.
```

Saved primary L14 boundary readout: `3.299523`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-12--neutral--document--conflicting`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L236) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `60`; response stop (exclusive) `73`; final content `72`; boundary `73` (`151645`, `<|im_end|>`). Response tokens: `13`.

Sequence NLL: `8.995243`; mean token NLL: `0.691942`.

</details>

### Natural style responses

Supported context, QA format.

**correct, confident**

```text
For this item, I give the following answer: the assigned room for Velen-R12 is Linden Hall.
```

Saved primary L14 boundary readout: `3.024253`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-12--natural--correct--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L237) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `55`; response stop (exclusive) `78`; final content `77`; boundary `78` (`151645`, `<|im_end|>`). Response tokens: `23`.

Sequence NLL: `50.530525`; mean token NLL: `2.196979`.

</details>

**correct, hedged**

```text
It might be that the assigned room for Velen-R12 is Linden Hall.
```

Saved primary L14 boundary readout: `1.646591`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-12--natural--correct--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L238) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `55`; response stop (exclusive) `72`; final content `71`; boundary `72` (`151645`, `<|im_end|>`). Response tokens: `17`.

Sequence NLL: `26.801651`; mean token NLL: `1.576568`.

</details>

**incorrect, confident**

```text
For this item, I give the following answer: the assigned room for Velen-R12 is Hazel Hall.
```

Saved primary L14 boundary readout: `2.973279`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-12--natural--incorrect--confident`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L239) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `55`; response stop (exclusive) `78`; final content `77`; boundary `78` (`151645`, `<|im_end|>`). Response tokens: `23`.

Sequence NLL: `54.664398`; mean token NLL: `2.376713`.

</details>

**incorrect, hedged**

```text
It might be that the assigned room for Velen-R12 is Hazel Hall.
```

Saved primary L14 boundary readout: `1.659261`.

<details>
<summary>Technical details and saved source row</summary>

Variant ID: `v2-room_assignment-12--natural--incorrect--hedged`. [Saved response row](../../results/paired_confidence_transfer_v2/extraction_rows.jsonl#L240) · [Saved score artifact](../../results/paired_confidence_transfer_v2/transfer_metrics.json).

Saved token positions (zero-based): prompt/response start `55`; response stop (exclusive) `72`; final content `71`; boundary `72` (`151645`, `<|im_end|>`). Response tokens: `17`.

Sequence NLL: `32.293514`; mean token NLL: `1.899619`.

</details>

[Back to question list](#room-assignment) · [Dataset overview](README.md)
