# Cue holdout challenge: rewrite specification

## Purpose and unit of work

Create 50 paired rewrites from 50 new, independent source groups, balanced across the five challenge task types. Rewrite both the confident and hesitant member from the source response; do not use the source verbatim as the confident member. Each pair preserves the same answer and differs only in the speaker's expressed certainty.

Each source must have a clear focal answer or conclusion whose certainty can be
expressed naturally within the substantive discourse. Reject pure inventories
or outlines that would require a generic whole-answer endorsement wrapper.
Semantic source-quality and applicability review is agent-audited development
QA, not human validation.

Source dataset is not balanced within task. Source quality and focal-answer
suitability govern the mix; record actual per-task and overall dataset counts,
and do not describe the set as exactly balanced unless it is.

Use five cue families. Within each task type, write exactly two pairs per family (5 task types × 5 families × 2 pairs = 50). Assign distinct source groups to all pairs. Freeze source IDs, pair text, family, and length direction before activation scoring.

## Cue families

Use both members of every pair to express opposite certainty levels. Keep cue scope on the speaker's commitment to the same answer, not on the answer's factual content.

1. **Embedded stance predicates:** Put commitment or tentativeness in the grammar of a reporting, judgment, or conclusion clause; vary predicate, clause structure, and placement.
2. **Modal force and scope:** Express a stronger versus weaker speaker commitment through modal constructions, with no changes to the answer's conditions or object-level probabilities.
3. **Compositional polarity:** Combine negation, certainty vocabulary, and clause scope so that the whole construction determines the stance. Include cases where a word such as “certain” or “uncertain” alone would predict the wrong label (for example, negated uncertainty for the confident member or certainty about an inability to settle a claim for the hesitant member).
4. **Discourse-level calibration:** Place a concise commitment or reservation in a lead-in, parenthetical, or closing clause. Vary its position and syntax; do not add a new reason, premise, audience, or scenario.
5. **Contrastive commitment:** Use a balanced contrast or self-qualification to distinguish firm endorsement from provisional endorsement of the same answer. The contrast may qualify confidence, but must not qualify, retract, or add any answer proposition.

Across the challenge, include compositional cues in at least 10 pairs and across at least three task types. Vary cue position and syntax within every family. Do not reuse one fixed sentence template, opener, or simple word substitution across pairs.

The certainty contrast must be part of the response's substantive discourse. Do
not append a generic sentence such as “I endorse this answer/account/outline” to
an otherwise matched body, and do not express uncertainty about whether the
rewrite itself retained a list, slide, calculation, or detail. A reviewer must
be able to read the stance as commitment to the answer's claims. Across a batch,
vary whether the contrast appears in a governing clause, within a conclusion,
through modal scope, or through a genuinely compositional construction. A
closing clause is allowed only when it is natural for that particular answer;
it must not become the repeated recipe.

## Preservation and matching

- Preserve every source proposition, answer/list item, number, entity, condition, example, code/formula, and causal or logical step. Do not silently repair source errors or add facts, evidence, explanations, or context.
- Keep the answer type and framing stable: a list remains the same list, a solution remains a solution, and code remains code. Both versions must be rewritten from the source.
- Match formatting, paragraph and list structure, code fences, notation, and level of detail within each pair. Certainty cues should not change politeness, authority, helpfulness, or answer quality.
- Do not use the current recipe's common stand-alone prefaces or near-verbatim variants, including “I'm not fully certain,” “I'm not entirely certain,” “I'm not sure,” “my understanding is,” “my tentative answer,” “I may be wrong,” and “I could be mistaken.” Do not place a generic hedge before an otherwise unchanged response.
- Target an absolute within-pair token-count difference of no more than 3 tokens where practical. Use the same fixed tokenizer for both members and record counts. Do not pad with repeated content or remove answer material to meet the target.

## Length-direction counterbalance

Make the confident member longer in exactly 25 pairs and the hesitant member longer in exactly 25. For each task-type × cue-family cell, assign one of its two pairs to each direction. Keep the direction assignment fixed before review; a revision must preserve the assigned direction or be length-balanced again before review.

## QA, retries, and freeze

Run automated and agent-assisted QA for source-content preservation, pair identity, cue scope, length counts/direction, formatting, and forbidden-template reuse. Agent QA is a pre-screen only and must never be recorded or described as human review.

Before expanding beyond the first 10-pair microbatch, require an independent
blinded pre-screen to find no content failures, no reversed/tied certainty
order, and no material shortcut concern. A failed microbatch is rewritten from
the frozen sources and reviewed again; it is never repaired after activation
scores are inspected.

Have two reviewers independently assess each pair while blinded to cue-family labels and intended certainty direction. They should judge content preservation and which member communicates stronger speaker commitment; adjudicate disagreements without seeing model scores. If either reviewer flags a defect, allow one rewrite attempt, then repeat blinded review. Exclude any pair still failing content preservation or clearly expressed certainty. Draw replacements from a preregistered reserve set before the set is locked; keep the 25/25 length-direction balance and cell counts exact.

The canonical response JSONL fields are `blind_id`, `content_preservation`,
`stronger_commitment`, `formatting_mismatch`, `shortcut_concern`, and optional
`notes`. Values are respectively `pass|fail|uncertain`, `A|B|tie|uncertain`,
`no|yes|uncertain`, and `none|minor|repair|uncertain`. Alternate names or values
are not silently normalized. Two `agent` reviewers may create only an explicitly
development-only lock; two `human` reviewers are required for a human-reviewed
lock. Mixed reviewer types are refused. The public manifest contains two opaque
reviewer IDs with type, blinded/pass status, and the locked-pair and selection
manifest hashes. Agent QA is never human review.

After review, freeze the accepted 50 pairs, source IDs, family labels, token counts, and direction assignments before activation scoring. Do not revise or replace challenge items after scoring begins.
