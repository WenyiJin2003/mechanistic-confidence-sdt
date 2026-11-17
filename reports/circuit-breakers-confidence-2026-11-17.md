# Domain-specific confidence with a retain loss

**Retention reduced out-of-domain changes in wording and weakened the intended change in ecology and evolution.** On general science, the mean change moved from **−1.79** to **−0.10** on the 0–10 tone scale. On ecology and evolution, it moved from **−1.37** to **−0.16**.

## Earlier experiment on general questions

The first LoRA trained on general questions. In full-answer tests, its explanations sounded about 1 point more cautious on MMLU and 0.7 points more cautious on a separate set of Science Bowl biology questions. The MMLU shift persisted in answers without the common hedges we checked.

## Model and training

- **Original Qwen** is Qwen2.5-1.5B-Instruct without an adapter.
- **A (no retain)** learns to sound more cautious from fresh answers to ecology and evolution questions. An L21 Transformer probe supplies the training signal. The probe is initialized and refitted using 480 fixed confident/hesitant answer pairs. These pairs supervise the probe. The fresh ecology and evolution answers drive the LoRA updates.
- **B (retain)** adds the representation-preservation term from [Circuit Breakers, Algorithm 1](https://arxiv.org/html/2406.04313). It penalizes L21 differences between the adapted model and frozen Qwen on the same non-target question and answer. The retain set contains 120 non-target questions.
- A and B use matched initializations, question order and neutral KL, with two A100-matched seeds. All three models answer the same questions, and the judge sees the explanations with the model labels hidden.

## Results

Tone values are changes relative to original Qwen. Claude Opus 5.5 scored the degree of expressed confidence in the explanation on a 0–10 scale. Negative values mean more cautious wording. The parenthesized counts give the number of scorable tone pairs over the number of questions. Accuracy is the number of correct forced-choice answers over all questions.

| Evaluation domain | A: tone change | B: tone change | Qwen: correct | A: correct | B: correct |
|---|---:|---:|---:|---:|---:|
| Ecology & evolution | −1.37 (63/65) | −0.16 (64/65) | 51/65 | 53/65 | 49/65 |
| Physics | −1.19 (32/32) | +0.19 (32/32) | 29/32 | 31/32 | 30/32 |
| Earth science | −2.34 (32/32) | −0.16 (32/32) | 29/32 | 29/32 | 28/32 |
| Astronomy | −1.84 (31/32) | −0.33 (30/32) | 32/32 | 31/32 | 31/32 |
| General science overall | −1.79 (95/96) | −0.10 (94/96) | 90/96 | 91/96 | 89/96 |

The target questions cover ecosystems and population evolution, including habitat, genetic drift and founder effects. This target-domain analysis includes 65 ecology and evolution questions from [DOE Science Bowl](https://science.osti.gov/wdts/nsb/Regional-Competitions/Resources/HS-Sample-Questions) and [OpenStax Biology 2e](https://openstax.org/details/books/biology-2e). The general science evaluation has 96 questions from the [SciQ](https://huggingface.co/datasets/allenai/sciq) test and validation splits, 32 each in physics, earth science and astronomy. Known exact and near-textual duplicates with project training and earlier evaluation questions were excluded before generation. The overall general-science tone result weights all three disciplines equally.

The general-science B–Qwen effect is **−0.10 points** with a 95% paired bootstrap interval of **[−0.35, +0.13]**. The ecology B–Qwen effect is **−0.16** with an interval of **[−0.55, +0.25]**. All 483 model answers for these two domains were returned. All 161 review packets completed, with the unscorable pairs shown in the table. The Qwen, A and B general-science accuracy totals differed by at most two questions.

[Download the screen-share HTML](./circuit-breakers-confidence-2026-11-17.html) and open it locally in a browser.
