# Fresh factual evaluation cohort (500 questions)

This experiment freezes a fresh, source-disjoint factual-question cohort for
testing whether the existing confidence LoRAs and frozen-probe activation
interventions causally change model outputs.

## Why these are questions, not Claude rewrites

The existing confidence-pair collections have already been used for probe
training, development, internal testing, LoRA training, or post-exposure
robustness checks. Asking Claude to write another 500 confident/hesitant answer
pairs would measure Claude's rewrite style again. Instead, the evaluated Qwen
conditions must answer the same fresh questions themselves. Claude may later
judge the resulting answers in blinded batches.

## Source and isolation

- Source: TriviaQA questions and accepted-answer aliases from the locally cached
  LACIE release.
- Raw source SHA-256:
  `b6db83dcd94c8781ae7740422928d3f70e8d7b9a836e7f6b0a240232ab718c0c`.
- No generated Mistral response text is imported.
- Questions are normalized with Unicode NFKC, HTML unescaping, whitespace
  collapse, and case-folding.
- Every question overlapping the current probe/LoRA/evaluation splits or the
  earlier selected LACIE review sets is excluded before deterministic sampling.
- The cohort is balanced across short, medium, and long question-length tertiles
  (167/166/167).

This is an engineering-held-out, source-disjoint behavioral evaluation cohort.
It is not a claim that these public TriviaQA questions were absent from the base
model's pretraining corpus.

## Files

- `build_eval_cohort.py`: deterministic, write-once cohort builder.
- `tests/test_eval_cohort.py`: structural, provenance, and overlap tests.
- `private_data/EVAL_COHORT_500.jsonl`: local question cohort; kept private to
  respect the source-review handling note.
- `COHORT_FREEZE.json`: exact counts, hashes, exclusions, and selection recipe.

## Intended next experiment

Run the same 500 questions under pre-frozen model conditions, including baseline
and representative `+/-` activation-steering strengths. Blind condition labels,
then compare output confidence, correctness, fluency, and answer length. The
frozen probe score is a manipulation check; behavioral confidence is the primary
causal endpoint.
