# Same-split baseline comparison

This directory compares the frozen primary confidence probes with the six
historical shallow text-control recipes and three deterministic length rules on
the exact scale-up splits (train 920, dev 156, internal test 193, external CF3
113).  Text models are independently refit on the nested 200/500/920 training
prefixes.  Dev designates a strongest comparator, but all six models are kept
and reported.  Internal test is not used for fitting or recipe selection.

The run is provider-free.  It performs no Qwen or other model forward.  The
token-length control reuses the already-frozen Qwen response-token counts in
each evaluation row's `strict_evidence`; word and character rules are computed
directly from exact response strings.

The output includes paired win/tie/loss accuracy, answer-level ROC AUC,
grouped bootstrap intervals, the same frozen strata as the probe runner, exact
input/artifact hashes, and paired probe-minus-baseline contrasts.

The reviewed result is `BASELINE_COMPARISON_RESULTS_AUTHENTICATED.json`.
`BASELINE_COMPARISON_RESULTS_PREAUTHENTICATION.json` is retained only as an
audit trail from before the independent reviewer required explicit path/hash
binding of the probe fit NPZs and activation bundle; do not use it for claims.
