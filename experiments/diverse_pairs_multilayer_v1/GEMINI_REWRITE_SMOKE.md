# Gemini rewrite smoke: stopped before scale

## Conclusion

**Do not use the current Antigravity/Gemini route for the 1,000-pair
expansion.** It can generate confident/hesitant rewrites, but the eight-source
smoke failed the frozen output, length, and semantic-preservation gates. No
Gemini-generated pair has been promoted into the study dataset.

## What was tested

- The same eight frozen, real-source records used by the v3.2 rewrite smoke.
- `gemini-3.8-flash-low` through the user's authenticated Antigravity CLI.
- A custom text-only agent with an empty tool list. It could not run commands,
  read or write files, browse, or invoke subagents.
- The unchanged v3.2 local Qwen tokenizer and mechanical validator.
- Private source and output text remained under ignored `private_data/` paths;
  public reports contain aggregates only.

Two preliminary transport attempts returned no text after a requested command
was denied. The final text-only attempt returned all eight pairs without using
tools, but violated the structured-output contract: it used a top-level array,
renamed fields, and appended prose. A diagnostic-only adapter mapped the known
aliases so the unchanged content validator could inspect the cached response.
This mapping does not count as a protocol pass and cannot authorize scaling.

## Results

| Check | Result |
|---|---:|
| Strict frozen smoke gate | **0/8 passed** |
| Pairs failing only exact source-relative word targets | 7/8 |
| Pairs with additional length/direction failures | 1/8 |
| Clear content-preservation failures in agent-assisted review | **2/8** |
| Successful call usage reported by Antigravity | 84,728 input / 5,749 output tokens |

The two clear semantic failures were consequential rather than stylistic. One
rewrite weakened a safety requirement from an obligation to a recommendation;
another changed a hypothesis from a proposed explanation to a definitive one.
Three additional pairs expressed only a weak or highly localized contrast.

Across the three research-data calls, Antigravity reported 125,860 input and
5,969 output tokens. At this rate, scaling the same agent workflow to 1,000
sources would be inefficient even before review and filtering.

## Decision and next step

This is a **generation-method failure, not evidence against the research
hypothesis**. The activation experiment has not been rerun and its earlier
results are unchanged.

Before expanding the paired dataset:

1. enlarge and review the primary-eligible natural-source pool;
2. choose a direct structured-generation route rather than an agent harness;
3. require a fresh canary to pass content preservation, confidence contrast,
   length counterbalancing, and blinded human review;
4. only then generate the 100/300/700 learning-curve sets.

Machine-readable aggregate reports:

- [Mechanical diagnostic](reports/gemini_smoke_v32g_textonly_diagnostic.json)
- [Semantic review](reports/gemini_smoke_v32g_semantic_review.json)
