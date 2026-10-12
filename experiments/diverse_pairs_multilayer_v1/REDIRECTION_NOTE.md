# Research direction update

11 October 2026. Preparation only; no new scientific results.

The next primary study is **Diverse Paired Certainty + Multi-Layer Readout**.
It asks whether content-preserving confident/hedged rewrites of diverse existing
assistant responses yield an expressed-certainty readout that generalizes to
unseen source content and rewrite instructions, and whether a multi-layer
ensemble improves on layer 14 using the same data and supervision.

The current supervised label is **expressed certainty about preserved answer
content**. Epistemic qualification changes deliberately; answer propositions,
entities, numbers, conditions, code and reasoning must remain intact. This label
does not supply ground truth for subjective model confidence.

Historical Stage 0/0B and v1–v4 data, reports, negative results, code and caches
remain intact. Correctness, contextual evidence support, semantic entropy and
model-generated answers are separate diagnostics. They neither train the new
primary readout nor constitute prerequisites for constructing the paired data.
V4 is a support-trained diagnostic; its 71.9% result is not an improvement of
the original certainty-trained readout.

## Planned comparison

- Approximately 1,000 independent source responses: 750 WildChat-1M and
  250 original HelpSteer2, subject to eligibility and coverage checks.
- Group conversations, shared prompts and near duplicates before rewriting;
  target approximately 700/150/150 train/validation/test groups.
- Preserve a separate test rewrite-instruction family and unseen source groups.
- Compare fixed-template and natural diverse rewrite training on identical source
  IDs and pair counts, evaluating the same locked natural test pairs.
- Refit a layer-14 paired linear readout and a 28-layer equal-score ensemble.
  Train-only scaling applies to both; source-grouped OOF stacking is secondary.
- Pool ordinary assistant response tokens; cache a final-content-token diagnostic.
  Check the actual last-layer normalization and API indexing before extraction.

These choices are proposed implementation decisions, not completed experiments.
The protocol and final eligible sources must be frozen before test scoring.

## Resource and quality boundaries

Reuse the existing pinned, unquantized Qwen2.5-1.5B snapshot only as a frozen
representation model. Its local availability does not establish a suitable
production rewriter. The user subsequently authorized a 50-pair pilot using
current-session GPT-6 Luna; larger-scale rewriting still needs its own quality
and resource decision. External API spending remains unapproved.
Third-party response bodies and rewrites stay in ignored private_data;
inference caches stay in ignored cache. No source text has been published.

An actual human reviewer must inspect the first approximately 50 training pairs.
Until that happens, human_review is pending. Agent review is not human review.
Templates are an explicit baseline, never a substitute for the main rewrites.

No old generation is rerun, and no language-model training, SDT loss, activation
steering, paid rewriting or full 1,000-source inference is authorized by this
preparation stage. The immediate computational stage is a bounded precheck.

See [local resources](LOCAL_RESOURCE_ASSESSMENT.md) and [status](STATUS.md).
