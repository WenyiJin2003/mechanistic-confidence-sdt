# Frozen Transfer v2 — Expressed-Certainty Evidence-Transfer Test

This test asks whether Paired Confidence v1's **unchanged** expressed-certainty
direction transfers to new wording and to changes in supplied evidence. It
does not train a confidence loss or fit a new readout on the transfer data.

Start with the [results](../../reports/CONFIDENCE_TRANSFER_RESULTS_V2.md). The
[preregistration](../../CONFIDENCE_TRANSFER_PREREGISTRATION_V2.md) fixes the decisions
made before extraction; the [config](../../configs/paired_confidence_transfer_v2.yaml)
contains all settings and pinned v1 artifact hashes.

## Run

Use the existing Stage 0 environment and pinned local Qwen snapshot. The default
configuration reuses the sibling `semantic-entropy-probes-stage0` checkout;
set `runtime.shared_repo` to its location on another machine. The same v1
directions and cached training artifacts must be present. No model download,
generation, NLI model, or paid API is needed.

```bash
# From this repository, with the existing environment active:
python -m pytest tests/test_transfer_data_v2.py tests/test_transfer_run_v2.py tests/test_transfer_analysis_v2.py -q
python scripts/run_confidence_transfer_v2.py --mode audit
python scripts/run_confidence_transfer_v2.py --mode run
```

`run` first performs a four-source extraction and exact cache-resume check,
then processes all 480 responses. Every forward is cached immediately. Design,
configuration and data files must be unchanged and committed before inference.
`--mode build` deterministically reconstructs the scoreless data; it must not
be used to alter the registered catalog after scores are observed.

The frozen model consumes each written assistant response (teacher forcing).
Primary extraction is `hidden_states[14]` at the response-end `<|im_end|>`
token, ID 151645: **after the response, not at the end of the question**. This
uses the state after block 14 under Hugging Face indexing (index 0 is the
embedding state). Final ordinary response-token and response-mean states have
their own separately fitted v1 directions and remain secondary.

Natural wording variants share identical prompts and fixed padded shapes.
Evidence conditions intentionally have different prompts but exactly equal
unpadded prompt lengths and identical neutral response tokens. Their assistant
token positions therefore match; padding is not used to fake this match.

## Artifacts

| Location | Contents |
|---|---|
| `data/confidence_transfer_v2/` | 48 fictional world keys, 480 written responses, scoreless template/context audit and token checks |
| `results/paired_confidence_transfer_v2/` | Aligned states, exact extraction positions, row scores, metrics, baseline/null parameters, hashes and runtime manifest |
| `plots/paired_confidence_transfer_v2.png` | The two required endpoints and controls with source-bootstrap intervals |
| `cache/confidence_transfer_v2/` | Resumable per-input forwards; local only, excluded from Git |

The word/character and numeric baseline classifiers are reconstructed using
**v1 training A/B rows only**. V2 texts are transformed, never fitted; v2
labels never determine orientation. Raw likelihood is reported separately from
these frozen certainty classifiers. Null vectors likewise use only the old
training-source differences and original RNG sequence.

Cached states allow analysis without another model pass. The manifest pins data,
implementation, inherited directions and aggregate artifacts. Rerunning on a
different device may produce small numerical differences; the original local
states remain the reference for exact result reproduction.
