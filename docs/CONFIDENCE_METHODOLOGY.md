# From a confidence probe to conditional tone control

**Updated November 17, 2026.** The model is **Qwen2.5-1.5B-Instruct**. The probe uses internal activations to estimate **expressed confidence**: how firmly the wording commits to an answer. The supervision comes from answer pairs with different tones. Factual accuracy, token likelihood and calibrated confidence are separate quantities.

## 1. Build pairs that vary tone

Start with a question and two ways of giving the same answer. One is more confident and one is more hesitant. Preserve the central claim, quantities and qualifications. Check content, tone and naturalness. For example, both versions might say that a $45 ticket costs $6 more than the $39 available. The wording can express that conclusion firmly or tentatively.

Fit the probe on labeled pairs and keep evaluation questions separate from fitting. Earlier transfer tests also held out wording families and balanced which version was longer. Text features, answer likelihood and response length provide controls for shortcuts. The [cue-holdout report](../experiments/cue_holdout_challenge_v1/RESULTS.md) documents that earlier test.

## 2. Read internal states with three probe architectures

For the later experiments, Qwen reads the question and the supplied answer. The probe reads hidden states at ordinary answer tokens, using hidden-state index 21 in the model. Each state already contains context from the question and the answer so far. Average the token scores to compare two complete answers.

| Probe | How it works | What the experiment asks |
|---|---|---|
| **Linear** | A weighted sum turns one hidden-state vector into one score. The earlier L14 study applied a linear readout to answer-averaged states. The later matched L21 study scored one answer-token state at a time. | Is the distinction visible in a simple direction? |
| **MLP** | An eight-unit hidden layer with ReLU combines features nonlinearly. The matched L21 MLP still receives one answer-token state at a time. | Does a nonlinear readout help with the same input? |
| **Transformer** | A small causal attention block scores the current answer token using its state and up to 15 earlier answer-token states. | Does giving the probe a short stretch of answer context help? |

The matched pilots compared a probe kept fixed during LoRA training with one refitted after every LoRA update. The Transformer varies both capacity and access to earlier token states, so that comparison tests the variant as a whole. The later 480-pair recipe also changed the target loss, so its results do not isolate the effect of dataset size.

## 3. Test whether a probe can change generated answers

**The 480 fixed answer pairs train the probe. Fresh model answers train the LoRA.** The main Qwen weights are frozen during adapter training.

1. Let the current adapter answer a new batch of training questions.
2. Hold the probe fixed and score those fresh answers. In the 480-pair Transformer recipe, compare each answer with the original Qwen's answer to the same question, using the same probe for both. Update the LoRA toward the requested tone. A separate KL term keeps the output distribution near Qwen on neutral anchor examples.
3. Re-encode the same 480 labeled pairs under the updated model and refit the probe on those states. This lets the readout track changes in the adapted model's internal states. Repeat.

Evaluate the finished adapter on new questions using a shared neutral prompt. A blinded judge scores the wording of the generated explanation from 0 to 10. The answer key separately checks the model's selected option. The general-question Transformer LoRA shifted tone by about **−1.0 on MMLU** and **−0.7 on Science Bowl biology**, relative to original Qwen. The MMLU shift also appeared in answers without the common hedges checked in a follow-up analysis. [Public evaluation report](../reports/circuit-breakers-confidence-2026-11-17.md)

## 4. Limit where the tone changes

The conditional experiment gives the probe-guided LoRA updates **ecology and evolution questions**. At evaluation, the same adapter is used for every domain under the same prompt.

- **A · Without retain.** Use the cautious-tone objective and the existing neutral KL term.
- **B · With retain.** Use the same training and add an activation-matching term inspired by [Circuit Breakers](https://arxiv.org/html/2406.04313). On non-target questions, both models read the same question and the same original-Qwen answer. Penalize the distance between their L21 states at the corresponding answer tokens.

| Evaluation domain | A · Tone change vs. Qwen | B · Tone change vs. Qwen |
|---|---:|---:|
| Ecology and evolution | −1.37 | −0.16 |
| General science (physics, earth science and astronomy) | −1.79 | −0.10 |

Lower means more cautious. The retain loss reduced the shift outside the target domain and weakened the intended shift inside it. The [public report](../reports/circuit-breakers-confidence-2026-11-17.md) gives the separate accuracy results, scorable counts and uncertainty intervals. Whether the adapter can preserve both a meaningful target shift and baseline behavior elsewhere remains open.

**Next experiment.** Compare **120 vs. 480 distinct target questions** with the same number of generated training answers and LoRA steps. Run both retain conditions at each scale. This tests whether greater question coverage helps at a fixed training budget.
