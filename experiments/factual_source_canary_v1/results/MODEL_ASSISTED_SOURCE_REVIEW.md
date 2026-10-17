# Model-Assisted Source Review

## Decision

**Use ASQA, QASPER author abstracts, and BillSum as the balanced long-form core. Keep FeTaQA outside the core as a short-form, table-grounded external test.**

The proposed canary contains **120 core sources and 240 rewritten texts**:

| Core source | Final quota | Role |
|---|---:|---|
| ASQA | 40 | Open-domain, long-form factual answers |
| QASPER | 40 | Scientific abstracts with paper evidence |
| BillSum | 40 | Document summaries and an SDT-format bridge |

A separate set of **20 FeTaQA sources / 40 rewritten texts** tests whether a fixed probe transfers to short table-grounded answers. It is excluded from probe training, layer selection, and the headline 120-source result.

## What was reviewed

The review used the first 10 records from each dataset in the locked deterministic candidate file. It checked factual support, self-contained content, and whether the response could be rewritten with a strong speaker-certainty contrast without changing its claims.

This is a **model-assisted diagnostic, not independent human validation**. It is sufficient to revise the construction plan, but not to certify the final dataset.

| Dataset | Accept | Repair, then review again | Short control | Reject |
|---|---:|---:|---:|---:|
| ASQA | 5 | 3 | 0 | 2 |
| QASPER | 5 | 3 | 0 | 2 |
| BillSum | 6 | 4 | 0 | 0 |
| FeTaQA | 0 | 0 | 8 | 2 |

Exact record-level decisions and reason codes are in `model_assisted_review.json`.

## What the audit changed

1. **Dataset membership is not a quality guarantee.** Two ASQA answers directly conflicted with or mismatched their evidence. Two QASPER abstracts were unsuitable because they contained only background or research aims rather than substantive findings.
2. **Scientific and legal qualifiers are content, not hesitation.** Words such as *may*, *suggests*, *potentially*, statutory exceptions, and comparison scope must be identical in both rewrites.
3. **Some claims depend on missing context.** QASPER results can live only in tables or formulas omitted from extracted prose. BillSum can invoke definitions from incorporated laws that are absent from the bill text field.
4. **FeTaQA is useful, but for a different role.** Its answers are typically one sentence and about 17 words. Mixing them into the core would introduce a strong length and format difference.

## Gate before rewriting

The current 50-candidate pools are too small to select 40 high-quality items per long-form source with a replacement reserve. Expand ASQA, QASPER, and BillSum deterministically to **100 candidates each**, then review fixed blocks until each has:

- **40 accepted sources for the canary**;
- **8 accepted backups**.

A `requires_source_repair` record becomes eligible only after the repair is logged and the record passes a second review. Before any rewrite, freeze the source ID, response and evidence hashes, and the proposition-level qualifiers that may not change. If 100 candidates produce fewer than 48 accepted sources, add the next deterministic block of 20 rather than weakening the gate.

Only after this source gate should the confident and hesitant versions be generated. No hidden-state extraction, probe fitting, SDT loss training, or steering is part of this audit.
