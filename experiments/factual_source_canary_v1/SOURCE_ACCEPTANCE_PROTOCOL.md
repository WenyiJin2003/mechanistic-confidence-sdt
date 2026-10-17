# Source Acceptance Protocol

## Objective

Select a factual, evidence-traceable core **before** generating confident and
hesitant versions. This gate evaluates source quality only. It does not measure
confidence, activations, correctness of Qwen generations, or probe performance.

## Locked review order

Candidates are ordered separately within each dataset by:

1. mechanical eligibility;
2. `SHA256(seed, dataset, source_id)` using seed `20261017`.

The order is divided into fixed batches of 20. Review continues until each core
dataset contains 48 accepted sources or its candidate pool is exhausted. This
prevents reviewers from choosing examples because they appear easy or support a
preferred result.

## Decisions

| Decision | Meaning | Eligible for selection? |
|---|---|---:|
| `accept` | Claims are supported, the source is self-contained, and a full-pair rewrite is feasible | Yes |
| `requires_source_repair` | Potentially usable after a documented source-level correction or evidence retrieval | No |
| `reject` | Contradictory, unsupported, provenance-mismatched, or unsuitable | No |

A repaired source must pass a second review before its status changes to
`accept`. Repairs happen before confidence rewriting and must be recorded.

## Shared checks

- Every substantive claim in the response is traceable to supplied evidence.
- The question, response, and evidence refer to the same entity and event.
- The response contains enough independent content for a full-response rewrite.
- Speaker certainty can change without changing factual scope.
- Proposition-level qualifiers are listed and frozen. Examples include
  *may*, *suggests*, *approximately*, legal exceptions, comparison scope, and
  time or population restrictions.

## Dataset-specific checks

### ASQA

- Resolve ambiguous questions and competing short answers.
- Reject response/evidence contradictions and Wikipedia provenance mismatch.
- Avoid time-sensitive wording unless the response fixes the relevant date.

### QASPER

- Require paper-specific methods or findings, not survey background or aim-only
  abstracts.
- Verify that exact metrics and comparisons appear in extracted evidence;
  missing tables and formulas do not count as support.
- Freeze scientific uncertainty, causal scope, and baseline conditions.

### BillSum

- Verify all operative provisions against the supplied bill text.
- Reject or repair claims that depend on definitions from an incorporated law
  absent from the evidence.
- Avoid summaries whose nested conditions cannot be reliably preserved in two
  natural rewrites.

## Freeze rule

For each dataset, the first 40 accepted records in locked review order become
the core; the next eight become backups. Before rewriting, freeze the source ID,
group ID, response and evidence hashes, protected qualifiers, and pair-level
split. Full third-party text remains local and ignored by Git.

## Validation boundary

The primary pass is model-assisted and must be labelled as such. It is not
independent human certification. Before activation scoring, the final sources
and their rewritten pairs require a separate blinded quality audit. No probe
layer may be selected using these source-quality decisions.
