# V3.2 smoke quality gate

V3.2 is a controlled eight-pair rewrite smoke test. It adds a frozen 4/4
length-direction assignment and permits one narrowly defined retry for a
single mechanical failure. The audit is offline: it validates saved artifacts
and prepares a private blind review, but never calls Claude, Qwen, or another
model.

## Frozen attempt policy

Attempt 0 always contains all eight source pairs. A retry is authorized only
when attempt 0 has exactly seven accepted pairs, zero `not_applicable` pairs,
and one failed pair whose recorded issues are all in the frozen mechanical
issue taxonomy. The retry regenerates both members of that one pair, receives
only the closed issue-category labels, and may run once. Semantic-review
failures, `needs_review`, and `not_applicable` outputs are never retried.

The canonical set uses the earliest passing output for each source. Therefore,
an accepted attempt-0 pair can never be replaced by a retry. The stop/go rule
requires at least 7/8 accepted on attempt 0 and exactly 8/8 accepted with zero
`not_applicable` rows after the optional retry.

## Integrity and mechanical gate

The audit binds the current v3.2 generation contract, attempt-0 fingerprint,
optional retry contract and fingerprint, frozen source-record hashes, prompt
hashes, target word counts, target length directions, parsed-record hashes,
canonical selection, and status artifact. Missing, partial, duplicated,
unauthorized, stale, or differently bound artifacts fail closed.

Before accepting cached output, the gate invokes the runner's local replay
verifier: raw transport hashes are checked and parsed records are reconstructed
from the successful raw response under the frozen validator. This is cache
verification only and makes no generation call.

The frozen length assignment must be exactly four confident-longer and four
hedged-longer pairs. Every final pair must realize its assigned non-tie
direction and exact target word counts. A tie is reported but blocks
progression. The inherited preservation, structure, protected-span, length,
duplicate, wrapper, template, edit-parity, and source-suitability checks also
remain active.

A legitimate `not_applicable` row remains visible in status totals and blocks
progression. Because it has no candidates, it is excluded from candidate-text,
length, preservation, edit, shortcut, and cue metrics; the public report gives
both the evaluated and excluded counts.

## Private blind semantic review

Only after eight final records are accepted does the audit write an X/Y review
packet and a separate decoding key below `private_data/`. The reviewer sees the
source and randomly ordered candidates, but not confidence labels, generation
order, length assignment, rewrite recipe, topology assignment, source ID, or
the key.

All eight pairs must pass content preservation, certainty ordering, speaker
scope, formatting, naturalness, absence of confounds and shortcuts, and the
assigned stance topology. A complete passing agent review may authorize only
**canary development**. It never authorizes production generation or scaling.

## Public output

The report is aggregate only. It contains attempt-0 and final status counts,
retry-category counts, length-direction results, source-suitability coverage,
mechanical diagnostics, semantic-review totals, and the decision. It contains
no source or candidate text, source IDs, hashes, phrases, ngrams, reviewer
notes, or per-example values. A blocked report is written before private input
is read, so any preparation failure still leaves an auditable public result.

Run the offline gate from the repository root:

```sh
python -m experiments.diverse_pairs_multilayer_v1.src.audit_claude_canary_v32 \
  --set smoke

python -m experiments.diverse_pairs_multilayer_v1.src.audit_claude_canary_v32 \
  --set smoke \
  --review experiments/diverse_pairs_multilayer_v1/private_data/claude_rewrite_dev_v32/smoke/review/completed_review.json
```

The default public report is
`reports/claude_smoke_v32_quality_gate.json`. The packet and key remain under
`private_data/claude_rewrite_dev_v32/smoke/review/`.
