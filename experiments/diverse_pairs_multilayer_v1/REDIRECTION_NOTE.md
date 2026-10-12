# Research direction update

11 October 2026. This note records the priority change that preceded the current
development diagnostic. The original handoff remains local because it contains
private research-communication metadata; this is its public-safe research
summary. For completed results and the updated decision, see the
[development diagnostic](reports/DEVELOPMENT_DIAGNOSTIC.md),
[cue-holdout result](../cue_holdout_challenge_v1/RESULTS.md), and
[next decision](NEXT_DECISION.md).

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

The 50-pair development comparison reached a ceiling shared by text, NLL and
length controls. Its separate 50-pair cue/recipe-holdout challenge is also
complete: layer 14 reached 47/50, compared with 34/50 for character TF-IDF,
30/50 for answer likelihood and 25/50 for length. This supports resuming the
quality-gated source expansion, but does not complete the planned
diverse-versus-template comparison or learning curves.

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
steering or paid rewriting is authorized here. Expansion toward the grouped
1,000-source target must retain the stated quality and resource gates; it is not
permission to substitute fixed templates for diverse rewriting.

See [local resources](LOCAL_RESOURCE_ASSESSMENT.md) and [status](STATUS.md).
