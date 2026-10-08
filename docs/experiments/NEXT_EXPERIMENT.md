# Proposed Synthetic Fact Learning Pilot

7 October 2026. **Proposal for discussion; no training has been run.** Data,
loss settings and decision thresholds must be fixed before an empirical run.

## Research question

**Does an expressed-certainty objective help a model learn and retain target
facts beyond ordinary supervised training and simple additional supervision?**

The [fresh counterfactual study](../../reports/CONFIDENCE_SEPARATION_RESULTS_V3.md)
did not validate the current readout as evidence-sensitive factual confidence.
That result leaves its value as a training objective untested. The ordinary
loss specifies the content; the candidate internal term might influence its
learning. Any benefit must appear in independently measured behavior.

The first study would be **synthetic-fact supervised fine-tuning (SFT) on QA**,
using a completed-answer readout. It would not yet establish transfer to full
synthetic documents, causal identification of confidence, or knowledge replacement.

## Four comparison conditions

| Condition | Training objective | Question it answers |
|---|---|---|
| A: ordinary SFT | Next-token cross-entropy on the target responses | How well does the same data teach the facts? |
| B: candidate internal term | A plus a fixed expressed-certainty readout objective | Does this particular internal term add useful learning? |
| C: random-direction controls | A plus the same objective using several fixed random directions | Is the effect specific to the learned direction rather than generic extra gradients? |
| D: output-only control | A plus additional cross-entropy on the target fact span | Would simply emphasizing the answer tokens achieve the same result? |

Match starting checkpoint, examples, trainable parameters, optimizer, batch
order, updates and seeds. Every group must receive the same QA examples; the
internal-loss condition must not obtain extra content supervision. D reweights
the target fact tokens rather than scaling the entire original loss.

Use several random directions and training seeds in an empirical comparison.
A single seed is suitable only for an engineering check. Match random-vector
norms and measure the resulting auxiliary gradient norms on the same trainable
parameters. Equal loss coefficients alone do not imply equal intervention strength.

## Facts and evaluation inputs

Start with about **64–100 harmless fictional facts**, subject to the engineering
budget. This is a scale suggestion, not a statistical-power guarantee. Include
multiple training phrasings and reserve independent question phrasings for
evaluation. All variants of a fact stay bundled in analysis.

The primary test asks about facts learned during training using new questions,
without showing an answer-bearing document. Untrained fictional facts serve as
unknown controls; their answer accuracy is not a test of memory learning.

**New-fact learning and replacement are different studies.** A replacement test
requires first teaching facts K, checking that they were learned, and then
starting every comparison condition from that same checkpoint to teach K′.
The simpler new-fact study can validate training mechanics before that extension.

## Candidate objective and extraction

Use one frozen v1 direction and its original representation. A reasonable
starting candidate is the layer-14 mean over ordinary response-content states;
its expressed-certainty interpretation is known, and its factual-confidence
interpretation remains unvalidated. Fix this choice before training.

The supplied response should state the target fact neutrally. Do not add
certainty phrases solely to give the internal-loss condition an easier target.
All conditions use the same responses and token masks. The mean includes the
complete response content, not just the answer span and not the end marker.

A candidate objective with a bounded derivative with respect to its score is:

$$
\begin{aligned}
z_\theta(x,y)&=\frac{v^\top \bar h^{(14)}_\theta(x,y)-\mu_0}{\sigma_0},\\
\mathcal L_{\mathrm{candidate}}&=\operatorname{softplus}(-z_\theta(x,y)),\\
\mathcal L_B&=\mathcal L_{\mathrm{SFT}}+\lambda\mathcal L_{\mathrm{candidate}}.
\end{aligned}
$$

Here v is frozen. Reference mean μ₀ and scale σ₀ must be fixed from training
data or a predeclared training-only calibration set; neither may use evaluation
outcomes. Require σ₀ > 0 using a predeclared positive floor. This is a candidate
design, not a loss specified by Casper or already
implemented here. Softplus limits the derivative with respect to z, but the
resulting parameter gradients still depend on the model and normalization.

Freeze the reference statistics and report hidden-state norms and score
distributions. Set a small auxiliary-gradient budget relative to the ordinary
gradient on training-only batches, and apply the same calibration procedure to
random controls. Decide in advance whether coefficients are then fixed or adjusted
by a common rule. Higher raw scores can arise from norm or offset changes; those
changes alone cannot establish better fact learning.

A completed-answer loss can update model parameters through backpropagation.
Online steering before an answer is generated would require a separate study
of transfer to a generation-relevant state.

## Outcomes

**Primary outcomes:** recall of the trained target facts under held-out question
phrasings, and retention after all groups undergo the same subsequent
interference training. Average by fact, preserving its related variants.

Record answer likelihood or target-versus-alternative margins, sampling
consistency, unrelated capability retention, and certainty language in generated
answers as secondary outcomes. Check whether wrong answers become more assertive.
Measure calibration directly if it becomes an agreed objective.

Keep irrelevant interference, contradictory material and legitimate instructed
updates separate. Refusing a valid update is not automatically stronger or
better commitment. The intended behavior for each condition must be specified.

**Success requires improvement beyond A and meaningful controls on independent
fact-learning outcomes.** A lower auxiliary loss or higher readout score is an
optimization check, not the success criterion.

Before the run, specify a minimum useful gain and uncertainty analysis. Distinguish
an observed gain, evidence against that useful gain, and an underpowered result.
Report all conditions and failures rather than selecting the best seed or direction.

## Decisions before implementation

1. Agree whether the target is commitment to learned facts, linguistic
   assertiveness, or calibrated confidence.
2. Choose new-fact learning or a controlled replacement study from a shared K
   checkpoint.
3. Fix the data catalog, wording splits, representation, loss normalization,
   gradient budget, random controls, seeds and compute budget.
4. Fix recall and retention evaluations, interference behavior and decision
   thresholds.

An initial tiny gradient/memory check would establish whether the four conditions
can run fairly in the existing environment. It would carry no research conclusion.
The empirical comparison should follow a committed protocol. Transfer to full
document SDT would be a later test if this answer-state pilot shows useful effects.
