# WordNet and an economical rewrite model

**Use WordNet as an optional vocabulary aid, and use a language model for
natural changes in commitment and sentence construction.** Replacing “seems”
with a list of synonyms would still leave a vocabulary-based shortcut. This
step prepares a small construction pilot, not a new confidence-probe result.

## Latest: ten-source augmentation preview

The researcher found that the three examples still relied too heavily on
“may”. The [ten-source augmentation prompt](prompts/augmentation_ten_v1.txt)
therefore explicitly requests **lexical and syntactic augmentation in both
arms**, not a shared source body with a modal inserted. It asks for at least
five primary uncertainty constructions, with no primary construction leading
more than two pairs. Newly added “may” and “might” should each occur in no more
than three hesitant texts. Direct assertions, varied clause order and ordinary
paraphrasing supply the confident style; stock intensifiers are not required.
These are construction targets, not an automatic quality certification.

This preview uses ten previously inspected development sources from the
frozen v4 set: four ASQA responses, three BillSum summaries and three QASPER
abstracts. Selection takes the first records of each dataset in frozen order;
it is not based on rewrite quality or probe scores. Existing reviewer-only cue
assignments, protected-span annotations, previous drafts and length targets
are withheld from the writer. A fresh source-only Luna medium context wrote
one ten-pair batch. Parent review identified six drafts for a bounded
follow-up: inconsistent whole-response commitment, conditional “would” without
epistemic doubt, a changed record condition, or uncertainty attached to
reporting rather than the main finding. A second source-only Luna medium
context received those six originals plus a
[generic addendum](prompts/augmentation_ten_repair_addendum.txt), not the
previous candidates or reviewer-only annotations. The other four drafts are
unchanged. This is one documented follow-up, not an automatic retry loop or a
parent rewrite. The initial configuration records the initial one-context
plan; the execution status records both contexts. Old artifacts are preserved.
No activation extraction, probe fitting or training is authorized by this step.

**The follow-up is not a quality pass.** Newly added marker presence in the
final ten drafts is: may 4/10, could 4/10, perhaps 2/10, “one possibility” 2/10,
“possible that” 1/10 and seem/appear 1/10. Categories overlap, and counts do
not identify epistemic scope. The may cap of three was missed. Unblinded parent
inspection flags four pairs on the review page: weak whole-response contrast,
an omitted full entity name and ambiguous conditional legal wording, a changed
record condition, and an unsupported extra research aim/scientific-scope
change. Some problems survived or were introduced by the follow-up. All ten
remain drafts; **zero pairs are accepted as training data**. No further writer
calls are made in this step.

All ten drafts are for researcher review, not accepted training data. Vocabulary
counts are reported separately from writer-reported construction descriptions;
neither is a validated syntactic-diversity or factual-equivalence measure.
Later experiments must still keep variants of one source in the same split,
control length, and test held-out wording families. This preview by itself
cannot establish that lexical shortcuts have been removed. The
[execution record](results/augmentation_ten_v1_status.json) reports actual
marker counts, raw-output hashes and review status, not a probe score.

## Earlier: three revised illustrations

The [v3 prompt](prompts/economical_rewrite_v3.txt) prioritizes factual
completeness, a clear change in commitment to the main claims, and fluent
paraphrasing in both versions. It removes WordNet requirements and length
quotas for this illustration round. The same three development sources were
used with **GPT-6 Luna at medium reasoning effort**. One initial batch and one
bounded [fluency refinement](prompts/economical_rewrite_v3_fluency_addendum.txt)
were generated in separate source-only contexts. There was no retry loop.

The final review packet contains three pairs, pending researcher review. Two
technical-scope phrases in the hesitant scientific abstract were clarified by
the parent session: making the BERT comparison explicit and replacing “Its
results” with “RobBERT” as the subject of the performance claim. These edits
are recorded separately; both unedited Luna batches remain intact. The final
packet must therefore **not be described as unedited Luna output**.

| Development source | Confident words | Hesitant words |
|---|---:|---:|
| ASQA | 46 | 51 |
| BillSum | 56 | 55 |
| QASPER | 157 | 168 |

These are whitespace word counts, not model tokens. No independent blind
review, human certification, activation extraction or probe fitting was run
for this packet. The prompt, effort and constraints changed together, so any
apparent improvement cannot be attributed to one change. Length and wording
controls are still needed before scaling. Source-specific factual reminders
also make this a development exercise, not a held-out writer evaluation.
See the [text-free provenance record](results/rewrite_illustrations_v3_status.json).

## Writer choice and budget

The earlier six-pair epistemic preview was written by a GPT-6 session agent;
the earlier v4 factual canary used GPT-6 Luna at low reasoning effort. The
earlier three-source WordNet pilot used **`gpt-6-luna`, reasoning `low`**. The
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

## What the earlier low-effort pilot found

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

That earlier pilot supports a limited decision: Luna at low effort can generate
economical drafts, but the present prompt/model combination needs further
adjustment before scale-up. It does not establish that Luna cannot perform the
task. The medium-effort follow-up is now documented above, including the two
parent edits. It is still too small and too development-specific to establish
a reliable cost-quality comparison. Do not silently repair the drafts with a
larger model and attribute the result to Luna.

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

The latest three-example page can be rebuilt from its saved private drafts
without any generation:

```bash
python3 experiments/factual_source_canary_v1/src/prepare_rewrite_illustrations_v3.py --render
```

The ten-example page can likewise be rebuilt without a model call:

```bash
python3 experiments/factual_source_canary_v1/src/prepare_augmentation_ten.py --render
```

Omit `--render` only to prepare a new source packet before generation; the
preparer refuses to overwrite an existing packet. `--prepare-repair` prepares
the single documented six-source follow-up and refuses a second preparation.
The separate role key and
full source/candidate text remain under ignored `private_data/`. No script
opens a browser.

Each writer reads only its saved private `WRITER_PROMPT.txt`. After saving the
draft JSON, run the corresponding finalizer, adding `--refinement` for the
second packet. The finalizer records numeric consistency, new seem/appear
cues, length direction and claimed shared WordNet substitutions. These
mechanical checks do not establish semantic equivalence or naturalness.
The reviewer pages are local only, and these scripts do not open the browser.
