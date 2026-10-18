# WordNet and an economical rewrite model

**Use WordNet as an optional vocabulary aid, and use a language model for
natural changes in commitment and sentence construction.** Replacing “seems”
with a list of synonyms would still leave a vocabulary-based shortcut. This
step prepares a small construction pilot, not a new confidence-probe result.

## Writer choice and budget

The earlier six-pair epistemic preview was written by a GPT-6 session agent;
the earlier v4 factual canary used GPT-6 Luna at low reasoning effort. The new
three-source pilot explicitly uses **`gpt-6-luna`, reasoning `low`**. The
[official model guide](https://developers.openai.com/api/docs/models/gpt-6-luna)
describes Luna as an efficient model for focused, high-volume work. The
[reasoning guide](https://developers.openai.com/api/docs/guides/reasoning)
explains that lower reasoning effort favors lower token usage.

The implementation sends only a compact prompt and three original responses to
each isolated writer context. It does not inherit the research chat history.
Output is JSON only. There is one initial batch and one documented prompt
refinement on the same three sources, with no further retry loop. Both outputs
are retained. These are existing Codex writer tasks; no paid API credentials
are used. This does not make the work free of session usage, and API token
prices do not establish the percentage of a ChatGPT subscription quota used.
The exact backend snapshot and actual inference token usage are not exposed.

## What the small pilot found

The initial and refinement batches each contain the same three sources: one
ASQA answer, one BillSum summary, and one QASPER abstract. **Neither batch is
accepted as final paired data.** The initial writer self-corrected newly added
seem/appear wording before handoff, but still weakened “permanently” to
“lasting” and broadened a BERT-specific comparison. The refinement restored
those two details, but introduced first-person editorial commentary and
omitted source details in the longer answer. These are unblinded parent-model
diagnoses, not independent human judgments.

| Construction diagnostic | Initial prompt | Refined prompt |
|---|---:|---:|
| WordNet suggestions adopted | **0** | **0** |
| Cases meeting assigned length direction | 2/3 | 1/3 |
| Cases adding new seem/appear forms at final handoff | 0/3 | 0/3 |
| Researcher review complete | No | No |

The refinement has three hesitant-longer pairs, so the intended length
counterbalancing is not yet achieved. Removing two repeated words did not
automatically produce the desired natural variation. The two prompts and
candidate filtering changed together; this is **not an ablation showing that
WordNet helps or harms**.

This pilot supports a limited decision: Luna at low effort can generate
economical drafts, but the present prompt/model combination needs further
adjustment before scale-up. It does not establish that Luna cannot perform the
task. The next economical option to compare is a small Luna medium-effort
sample with a shorter factual checklist, measuring review/repair burden as
well as output size. That comparison has not been run. Do not silently repair
the drafts with a larger model and attribute the result to Luna.

The [initial status](results/wordnet_luna_preview_v1_status.json) and
[refinement status](results/wordnet_luna_preview_v2_status.json) contain only
aggregate diagnostics and provenance. Private candidate texts and notes are
preserved separately. No new probe result is claimed.

## What WordNet contributes

WordNet groups candidate words by sense, not by unrestricted interchangeability.
Its [official FAQ](https://wordnet.princeton.edu/frequently-asked-questions)
describes synonyms as context dependent, and
[NLTK's examples](https://www.nltk.org/howto/wordnet.html) explicitly distinguish
different senses of a word. The local helper therefore retains the synset and
definition, offers only a small number of candidates, and performs no automatic
replacement.

In the actual development sources, the unscreened lookup offered candidates
such as `recent → late`, `various → respective`, and `permanently → for good`.
These can be awkward or wrong for the intended sentence or genre. The
refinement retains only a manually reviewed temporal sense of “later”; it
allows “afterward/afterwards” and permits the writer to decline either.

If a neutral substitution is chosen, **the same choice must occur in both
arms**. This prevents our helper from assigning a separate vocabulary bank to
each confidence label. It does not guarantee that every other lexical cue is
balanced. Names, numbers, legal force, scientific qualifiers, and confidence
markers are not automatically substituted. WordNet neither supplies the
confidence labels nor certifies factual equivalence.

This small comparison cannot establish an augmentation benefit: the prompt and
the candidate filtering both changed. Actual adopted suggestions and all
construction flags are recorded, including zero adoption where applicable.

## The prompt

The [initial prompt](prompts/economical_rewrite_v1.txt) and
[prioritized refinement](prompts/economical_rewrite_v2.txt) are saved in full.
The refinement prioritizes:

1. Exact factual core and comparison scope, including “permanently” and
   BERT-specific comparisons.
2. A direct confident answer versus a clearly provisional endorsement of the
   same answer. Merely writing “the authors report” is insufficient.
3. Complete, fluent paraphrases with varied clause construction and a few
   well-scoped uncertainty expressions. This small challenge introduces no
   new “seem/appear” hedge, while retaining original protected uses.
4. Comparable detail and assigned length direction achieved without padding.

Avoiding “seem/appear” here is a bounded wording challenge, not a claim that
those words are invalid confidence expressions. The broader experiment should
vary and hold out entire wording families rather than simply banning words.

## Relationship to Cas's suggestion

The primary direction remains factual-rich, same-content confident/hesitant
pairs, followed by matched single-layer and multilayer comparisons. WordNet is
an auxiliary way to vary neutral wording; it does not replace that design.

Multilingual augmentation is another prospective test: translate both members
of a pair into the same target language, preserve the contrast and factual
core, and keep all translations from the same source in one split. Do not
associate English with one confidence label and another language with the
other. Sentence translation requires a separate generation and review step;
an English dictionary lookup does not perform it. No multilingual batch was run
in this pilot.

## Local reproduction

Install the optional dependency from `requirements-augmentation.txt` into the
research environment and download NLTK's `wordnet` corpus to
`private_data/resources/nltk_data/`. The preparation records the corpus SHA-256,
NLTK 3.9.2 and WordNet 3.0. Then, from the repository root:

```bash
python3 experiments/factual_source_canary_v1/src/prepare_economical_wordnet_preview.py
python3 experiments/factual_source_canary_v1/src/prepare_economical_wordnet_preview.py --refinement
```

Each writer reads only its saved private `WRITER_PROMPT.txt`. After saving the
draft JSON, run the corresponding finalizer, adding `--refinement` for the
second packet. The finalizer records numeric consistency, new seem/appear
cues, length direction and claimed shared WordNet substitutions. These
mechanical checks do not establish semantic equivalence or naturalness.
The reviewer pages are local only, and these scripts do not open the browser.
