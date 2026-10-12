"""Agent-QA development-only layer comparison; never final-test evidence."""
from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.sparse import vstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold

from extraction import extract_rows, load_config, resolve, write_json, write_npz
from readouts import (MeanDifferenceReadout, PairedLayerReadouts,
                      grouped_bootstrap_accuracy, grouped_bootstrap_difference,
                      paired_accuracy)
from run_preflight import flatten_pairs

BASE = Path(__file__).resolve().parents[1]
PRIVATE = BASE / "private_data"


def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def accepted_agent_qa(pairs):
    """Require complete same-session QA, while preserving human_review=pending."""
    initial = []
    for batch in range(1, 4):
        initial += read_jsonl(PRIVATE / f"agent_audit_batch_{batch}.jsonl")
    if len(initial) != len(pairs) or len({r["review_id"] for r in initial}) != len(pairs):
        raise ValueError("Incomplete initial agent-assisted audit")
    decisions = {r["review_id"]: r for r in initial}
    reaudit = []
    for batch in range(1, 4):
        reaudit += read_jsonl(PRIVATE / f"agent_qa_reaudit_batch_{batch}.jsonl")
    round_two = PRIVATE / "agent_qa_reaudit_round_2.jsonl"
    if round_two.exists():
        reaudit += read_jsonl(round_two)
    final_reaudit = {r["review_id"]: r for r in reaudit}
    accepted, rejected = [], []
    for pair in pairs:
        rid, audit = pair["review_id"], decisions[pair["review_id"]]
        if audit["recommended_action"] == "keep":
            okay = (audit["content_confident"] == "pass" and audit["content_hedged"] == "pass"
                    and audit["certainty_order"] == "pass")
            reason = audit["concise_reason"]
        else:
            check = final_reaudit.get(rid)
            okay = bool(check and check["decision"] == "accept" and
                        check["content_preserved"] == "pass" and check["certainty_clear"] == "pass")
            reason = check["concise_reason"] if check else "missing correction cross-audit"
        target = accepted if okay else rejected
        target.append({"review_id": rid, "source_id": pair["source_id"], "reason": reason})
    return accepted, rejected


def make_folds(tasks, groups, seed=20261011, n_splits=5):
    tasks, groups = np.asarray(tasks), np.asarray(groups)
    if len(set(groups)) != len(groups):
        raise ValueError("Development pilot expects one pair per independent source group")
    if min(Counter(tasks).values()) < n_splits:
        raise ValueError("Every task needs at least one pair per fold")
    splitter = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    folds = []
    for train, test in splitter.split(np.zeros(len(tasks)), tasks):
        if set(groups[train]) & set(groups[test]):
            raise ValueError("Source-group leakage across a development fold")
        folds.append((train, test))
    return folds


def cv_hidden_predictions(X, tasks, groups, *, C=.01, max_iter=2000, seed=20261011,
                          model_class=PairedLayerReadouts, orientations=None):
    folds = make_folds(tasks, groups, seed)
    layer_scores = np.full((len(X), 2, X.shape[2]), np.nan)
    equal_scores = np.full((len(X), 2), np.nan)
    fold_ids = np.full(len(X), -1)
    for fold, (train, test) in enumerate(folds):
        train_X = X[train].copy()
        if orientations is not None:
            swap = np.asarray(orientations)[train]
            train_X[swap] = train_X[swap, ::-1]
        model = model_class(C=C, max_iter=max_iter) if model_class is PairedLayerReadouts else model_class()
        model.fit(train_X, np.asarray(groups)[train])
        layer_scores[test] = model.decision_function(X[test])
        equal_scores[test] = model.equal_scores(X[test])
        fold_ids[test] = fold
    if not np.isfinite(layer_scores).all() or not np.isfinite(equal_scores).all() or (fold_ids < 0).any():
        raise ValueError("Incomplete cross-validated predictions")
    return layer_scores, equal_scores, fold_ids


def cv_text_predictions(pairs, tasks, groups, seed=20261011, C=.01, max_iter=2000):
    folds = make_folds(tasks, groups, seed)
    output = np.full((len(pairs), 2), np.nan)
    for train, test in folds:
        train_text = [pairs[i][key] for i in train for key in ("confident_response", "hedged_response")]
        vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=2,
                                     max_features=20000, sublinear_tf=True)
        matrix = vectorizer.fit_transform(train_text)
        # Responses were inserted as confident, hedged, confident, hedged, ... .
        # Keep the sparse matrix two-dimensional: scipy sparse arrays do not
        # support the three-dimensional pair view used by dense activations.
        delta = matrix[0::2] - matrix[1::2]
        symmetric = vstack([delta, -delta])
        labels = np.r_[np.ones(len(train)), np.zeros(len(train))]
        model = LogisticRegression(C=C, fit_intercept=False, max_iter=max_iter, solver="liblinear")
        model.fit(symmetric, labels, sample_weight=np.full(2 * len(train), .5))
        for i in test:
            transformed = vectorizer.transform([pairs[i]["confident_response"], pairs[i]["hedged_response"]])
            output[i] = model.decision_function(transformed)
    if not np.isfinite(output).all():
        raise ValueError("Incomplete text-baseline predictions")
    return output


def interval(scores, groups, seed, draws):
    scores = np.asarray(scores, dtype=float)
    delta = scores[:, 0] - scores[:, 1]
    result = grouped_bootstrap_accuracy(scores, groups, n_boot=draws, seed=seed)
    return {"estimate": result["estimate"], "ci95": list(result["ci"]), "groups": result["groups"],
            "wins": int(np.count_nonzero(delta > 0)), "ties": int(np.count_nonzero(delta == 0)),
            "losses": int(np.count_nonzero(delta < 0))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=str(BASE / "configs/diverse_pairs_multilayer_v1.yaml"))
    parser.add_argument("--shuffle-repeats", type=int, default=20)
    args = parser.parse_args()
    config = load_config(args.config)
    pairs = read_jsonl(resolve(config, config["data"]["pairs"]))
    accepted, rejected = accepted_agent_qa(pairs)
    if rejected or len(accepted) != len(pairs):
        raise ValueError(f"Agent-QA gate incomplete; rejected/pending IDs: {[r['review_id'] for r in rejected]}")
    config["runtime"]["max_pairs"] = len(pairs)
    config["runtime"]["max_seconds"] = 1200
    rows = flatten_pairs(pairs)
    started = time.monotonic()
    enriched, states, extraction = extract_rows(rows, config, check_padding=False)
    expected = (2 * len(pairs), 28, 3, 1536)
    if states.shape != expected:
        raise ValueError(f"Unexpected state shape {states.shape}; expected {expected}")
    pair_states = states.reshape(len(pairs), 2, 28, 3, 1536).astype(np.float32)
    X = pair_states[:, :, :, 0, :]
    final_X = pair_states[:, :, :, 1, :]
    prompt_X = pair_states[:, :, :, 2, :]
    tasks = np.asarray([p["task"] for p in pairs])
    groups = np.asarray([p["group_id"] for p in pairs])
    layers = np.asarray(config["model"]["layers"])
    l14 = int(np.flatnonzero(layers == config["readout"]["primary_reference_layer"])[0])
    C, max_iter = config["readout"]["C"], config["readout"]["max_iter"]
    layer_scores, equal_scores, fold_ids = cv_hidden_predictions(X, tasks, groups, C=C, max_iter=max_iter)
    mean_layers, mean_equal, _ = cv_hidden_predictions(X, tasks, groups, C=C, max_iter=max_iter,
                                                        model_class=MeanDifferenceReadout)
    final_layers, final_equal, _ = cv_hidden_predictions(final_X, tasks, groups, C=C, max_iter=max_iter)
    text_scores = cv_text_predictions(pairs, tasks, groups, C=C, max_iter=max_iter)
    nll = -np.asarray([[enriched[2*i]["mean_token_nll"], enriched[2*i+1]["mean_token_nll"]]
                      for i in range(len(pairs))])
    lengths = -np.asarray([[len(enriched[2*i]["tokens"]["response_ids"]),
                           len(enriched[2*i+1]["tokens"]["response_ids"])] for i in range(len(pairs))], float)
    draws, seed = config["readout"]["bootstrap_draws"], config["seed"]
    layer_metrics = [{"layer": int(layer), **interval(layer_scores[:, :, i], groups, seed + i, draws),
                      "mean_pair_margin": float(np.mean(layer_scores[:, 0, i] - layer_scores[:, 1, i]))}
                     for i, layer in enumerate(layers)]
    difference = grouped_bootstrap_difference(layer_scores[:, :, l14], equal_scores, groups,
                                               n_boot=draws, seed=seed + 100)
    metrics = {
        "status": "development_diagnostic_complete", "scientific_status": "not_final_test_evidence",
        "supervision": "agent-assisted QA; same configured model family as rewriter; not human review",
        "pairs": len(pairs), "folds": 5, "all_final_test_sources_scored": False,
        "response_pooling": "mean ordinary assistant-response tokens",
        "layer14": interval(layer_scores[:, :, l14], groups, seed, draws),
        "equal_28_layer_ensemble": interval(equal_scores, groups, seed + 1, draws),
        "ensemble_minus_layer14": {"estimate": difference["estimate"], "ci95": list(difference["ci"])},
        "layers": layer_metrics,
        "secondary": {
            "last_response_token_layer14": interval(final_layers[:, :, l14], groups, seed + 2, draws),
            "last_response_token_equal_ensemble": interval(final_equal, groups, seed + 3, draws),
            "mean_difference_layer14": interval(mean_layers[:, :, l14], groups, seed + 4, draws),
            "mean_difference_equal_ensemble": interval(mean_equal, groups, seed + 5, draws),
            "char_tfidf": interval(text_scores, groups, seed + 6, draws),
            "fixed_negative_mean_nll": interval(nll, groups, seed + 7, draws),
            "fixed_negative_response_length": interval(lengths, groups, seed + 8, draws),
            "constant_tie": {"estimate": .5, "ci95": [.5, .5]},
            "prompt_max_abs_pair_difference": float(np.max(np.abs(prompt_X[:, 0] - prompt_X[:, 1]))),
        },
        "extraction": {"forward_calls": extraction["forward_calls"], "cache_hits": extraction["cache_hits"],
                       "elapsed_seconds": extraction["elapsed_seconds"], "device": extraction["device"],
                       "dtype": extraction["dtype"]},
        "agent_qa": {"accepted": len(accepted), "rejected_or_pending": len(rejected),
                     "human_review": "pending", "initial_agent_revisions": 10,
                     "same_model_family_audit_limitation": True},
        "pair_construction_diagnostics": {
            "hedged_response_longer": int(sum(len(p["hedged_response"]) > len(p["confident_response"])
                                                  for p in pairs)),
            "median_hedged_minus_confident_characters": float(np.median([
                len(p["hedged_response"]) - len(p["confident_response"]) for p in pairs])),
            "confident_response_equals_source_verbatim": int(sum(
                p["confident_response"] == p["original_response"] for p in pairs)),
            "hedged_contains_confident_verbatim": int(sum(
                p["confident_response"] in p["hedged_response"] for p in pairs)),
        },
        "leakage_controls": {"group_disjoint_folds": True, "feature_scaling_train_only": True,
                             "score_scaling_train_only": True, "test_sign_selection": False,
                             "test_model_selection": False},
    }
    rng = np.random.default_rng(seed + 200)
    shuffled_l14, shuffled_equal = [], []
    for repeat in range(args.shuffle_repeats):
        orientations = rng.random(len(pairs)) < .5
        shuffled_layers, shuffled_ensemble, _ = cv_hidden_predictions(
            X, tasks, groups, C=C, max_iter=max_iter, orientations=orientations, seed=seed)
        shuffled_l14.append(paired_accuracy(shuffled_layers[:, :, l14]))
        shuffled_equal.append(paired_accuracy(shuffled_ensemble))
    metrics["shuffled_pair_labels"] = {
        "repeats": args.shuffle_repeats, "descriptive_not_formal_p_value": True,
        "layer14": {"values": shuffled_l14, "mean": float(np.mean(shuffled_l14)),
                    "q95": float(np.quantile(shuffled_l14, .95)),
                    "count_at_least_learned": int(np.sum(np.asarray(shuffled_l14) >= metrics["layer14"]["estimate"]))},
        "equal_ensemble": {"values": shuffled_equal, "mean": float(np.mean(shuffled_equal)),
                           "q95": float(np.quantile(shuffled_equal, .95)),
                           "count_at_least_learned": int(np.sum(np.asarray(shuffled_equal) >= metrics["equal_28_layer_ensemble"]["estimate"]))},
    }
    metrics["wall_seconds"] = time.monotonic() - started
    results = BASE / "results"
    write_json(results / "DEVELOPMENT_DIAGNOSTIC.json", metrics)
    write_npz(PRIVATE / "development_cv_predictions.npz", layer_scores=layer_scores,
              equal_scores=equal_scores, final_layer_scores=final_layers, final_equal_scores=final_equal,
              text_scores=text_scores, nll_scores=nll, length_scores=lengths, fold_ids=fold_ids,
              group_ids=groups, review_ids=np.asarray([p["review_id"] for p in pairs]))
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.plot(layers, [m["estimate"] for m in layer_metrics], marker="o", linewidth=1.6,
            label="Per-layer paired logistic")
    ax.axhline(.5, color="gray", linestyle="--", linewidth=1, label="Constant/tie baseline")
    ax.axhline(metrics["equal_28_layer_ensemble"]["estimate"], color="#16856a", linewidth=1.8,
               label="Equal 28-layer ensemble")
    ax.scatter([14], [metrics["layer14"]["estimate"]], s=70, color="#b73535", zorder=4, label="Layer 14")
    ax.set(xlabel="Qwen hidden-state layer", ylabel="Held-out pair ordering rate",
           title="Development diagnostic only: expressed-certainty ordering", ylim=(0, 1.02), xticks=range(2, 29, 2))
    ax.text(.99, .70,
            f"Surface controls\ncharacter TF-IDF: {metrics['secondary']['char_tfidf']['estimate']:.2f}\n"
            f"negative mean NLL: {metrics['secondary']['fixed_negative_mean_nll']['estimate']:.2f}\n"
            f"negative length: {metrics['secondary']['fixed_negative_response_length']['estimate']:.2f}\n\n"
            "Perfect layer scores are not\nmechanistic validation.",
            transform=ax.transAxes, ha="right", va="center", fontsize=9,
            bbox={"boxstyle": "round,pad=.5", "facecolor": "white", "edgecolor": "#c8c8c8", "alpha": .96})
    ax.legend(frameon=False, ncol=2)
    ax.grid(axis="y", alpha=.2)
    fig.tight_layout()
    fig.savefig(results / "DEVELOPMENT_LAYER_COMPARISON.png", dpi=180)
    plt.close(fig)
    print(json.dumps({"pairs": len(pairs), "layer14": metrics["layer14"],
                      "equal_ensemble": metrics["equal_28_layer_ensemble"],
                      "ensemble_minus_layer14": metrics["ensemble_minus_layer14"],
                      "tfidf": metrics["secondary"]["char_tfidf"], "nll": metrics["secondary"]["fixed_negative_mean_nll"],
                      "forward_calls": extraction["forward_calls"], "cache_hits": extraction["cache_hits"],
                      "wall_seconds": metrics["wall_seconds"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
