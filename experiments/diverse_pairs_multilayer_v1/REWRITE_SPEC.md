# First 50-pair rewrite pilot

11 October 2026. Training-development data only; final test excluded.

The user authorized selecting a resource-efficient rewriter and generating
50 pairs for their own content review. The selected model is **gpt-6-luna**,
invoked through short-context Codex subagents with low reasoning effort.
This uses current-session model allowance. No separately configured inference
API, API key, new local model or paid endpoint is used. Alias revision and
per-call billing token usage are not exposed by this invocation; record them
as unavailable rather than inventing snapshot IDs or token bills.

## Rewrite contract

From each existing source response, produce both confident_response and
hedged_response. Keep the source prompt identical and preserve:

- Answer identity, facts, named entities, dates, numbers, units and citations.
- All conditions, exceptions, object-level probabilities and causal reasoning.
- Code blocks and inline code verbatim; preserve formulas and derivation steps.
- Main response structure and approximately the same length.

Only the speaker's expressed epistemic commitment changes. Do not correct the
original answer, add verification or authority, supply new evidence, introduce a
different candidate answer, turn hedging into refusal, or replace object-level
possibility (e.g. 'can cause') with a deterministic claim ('causes').

Family A edits commitment naturally within an explanatory response; family B
edits commitment around the interpretation/conclusion while preserving reasoning.
These are development recipes, not a proven recipe diversity or generalization
claim. A test-only recipe C will be designed and frozen separately.

Joint JSON output order is balanced across 25 confident-first and 25 hedged-first
items. A repeated preamble across most responses is a templating warning, not a
successful diverse-rewrite implementation. A writer may report not_applicable;
retain failures rather than silently substituting a fabricated answer.

## Recording and review

Record source identity/revision/hash, prompt, original response, rewrite family,
requested output order, model alias, invocation route, attempt and agent-reported
issues. Keep response bodies, review annotations and any individual failures in
ignored private_data. Public files describe the protocol or aggregates only.

Automatic checks cover exact protected code/URLs, numeric-content changes,
empty/identical outputs, target tokenizer limits, length changes and repeated
phrases. Passing these screens is not semantic content certification.

The user reviews every pair against the original for:

1. Content preserved in both versions.
2. A clear and correctly ordered certainty difference.
3. Additional changes in politeness, authority, quality, length or reasoning.

The review interface displays randomized A/B versions without revealing the
expected certainty label initially. human_review stays pending until actual
annotations are received. No probe fitting or test scoring precedes this review.

## Revision 2: clearer hesitant commitment

The user's qualitative review found the two tones too similar. Preserve the
original 50 sources and confident responses; revise only hedged_response, using
the same configured GPT-6 Luna worker route. Archive the first packet and keep
its review-storage key intact. No held-out probe scores guide this revision.

Make the speaker's uncertainty conspicuous but moderate: a provisional reading,
best guess, or explicit lack of full certainty while still supplying the same
answer. Longer responses can qualify the interpretation and conclusion without
hedging every factual sentence. Vary natural formulations and where they occur;
do not prepend one standard disclaimer to all 50 items.

Do not change object-level probability, frequency, quantifiers, causal claims,
numeric derivations or code. Do not invent a reason for doubt, unavailable data,
new verification, a different answer, or a refusal. Target roughly the original
length and the existing token limits. New drafts require fresh human review;
the user's general feedback does not certify each pair's content preservation.
