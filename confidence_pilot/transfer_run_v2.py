"""Frozen v1 controls and extraction adapters for the test-only v2 dataset."""
from __future__ import annotations

from collections import Counter
import subprocess
from typing import Any

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from confidence_pilot.analyze_pairs import _validate_and_pair, _selection, _source_means
from confidence_pilot.common import ROOT, file_hash, read_jsonl, resolve, write_json, write_npz
from confidence_pilot.extract_activations import extract_activations


def verify_frozen_inputs(config: dict[str, Any], *, require_commit: bool = True) -> None:
    if config["analysis"].get("no_v2_fitting") is not True:
        raise ValueError("v2 must remain test-only; readout fitting is prohibited")
    for key, item in config["source_artifacts"].items():
        if file_hash(item["path"]) != item["sha256"]:
            raise ValueError(f"Pinned v1 artifact changed: {key}")
    if require_commit:
        protected = ["CONFIDENCE_TRANSFER_PREREGISTRATION_V2.md",
                     "configs/paired_confidence_transfer_v2.yaml",
                     *config["data"].values(), "data/confidence_transfer_v2/data_audit.json",
                     "data/confidence_transfer_v2/manual_audit.md"]
        for name in protected:
            tracked = subprocess.run(["git", "ls-files", "--error-unmatch", name],
                                     cwd=ROOT, capture_output=True)
            diff = subprocess.run(["git", "diff", "HEAD", "--", name],
                                  cwd=ROOT, capture_output=True)
            if tracked.returncode or diff.stdout:
                raise ValueError(f"v2 requires an unchanged committed design/data file: {name}")


def extraction_groups(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """v1's prompt-invariance assertion applies within, not across, contexts.

    Natural variants share a prompt and fixed padded tensor shape. Neutral
    conditions intentionally change prompts; their actual prompt/response
    token lengths have already been matched by the scoreless data gate.
    """
    result = []
    for row in rows:
        group = "|".join((row["source_id"], row["experiment"], row["format"], row["condition"]))
        result.append({**row, "original_source_id": row["source_id"], "source_id": group})
    return result


def extract_transfer(rows: list[dict[str, Any]], config: dict[str, Any]):
    grouped = extraction_groups(rows)
    extracted, hidden, runtime = extract_activations(grouped, config, grouped)
    restored = [{**row, "extraction_prompt_group": row["source_id"],
                 "source_id": row["original_source_id"]} for row in extracted]
    runtime["prompt_invariance_scope"] = "source + experiment + format + evidence condition"
    runtime["prompt_ids_identical_within_extraction_group"] = runtime.pop("prompt_ids_identical_within_source")
    runtime["right_padding_reference"] = "written variants sharing an identical prompt; neutral absolute token positions are matched"
    return restored, hidden, runtime


def prepare_frozen_controls(rows: list[dict[str, Any]], config: dict[str, Any]):
    """Fit only legacy v1 baselines, and reconstruct legacy v1 null vectors.

    No v2 labels, features, texts or source IDs enter fitting or orientation.
    Applying a fitted vectorizer to new texts is transform-only.
    """
    verify_frozen_inputs(config)
    old_rows = read_jsonl(config["source_artifacts"]["extraction_rows"]["path"])
    with np.load(resolve(config["source_artifacts"]["hidden_states"]["path"])) as archive:
        old_hidden = archive["hidden_states"]
        if archive["variant_ids"].tolist() != [row["variant_id"] for row in old_rows]:
            raise ValueError("v1 cached row/state alignment changed")
    with np.load(resolve(config["source_artifacts"]["directions"]["path"])) as archive:
        directions = {name: archive[name].copy() for name in archive.files}
    train_indices = np.asarray([i for i, row in enumerate(old_rows)
        if row["split"] == "train" and row["rewrite_family"] in {"A", "B"}])
    train_rows = [old_rows[i] for i in train_indices]
    old_sources = {row["source_id"] for row in train_rows}
    if old_sources & {row["source_id"] for row in rows}:
        raise ValueError("v2 source IDs overlap the legacy fitting pool")
    counts = Counter(row["source_id"] for row in train_rows)
    if len(counts) != 72 or len(train_rows) != 576:
        raise ValueError("Unexpected frozen v1 fitting pool")
    weights = np.asarray([1 / counts[row["source_id"]] for row in train_rows])
    weights *= len(weights) / weights.sum()
    labels = np.asarray([row["certainty"] == "confident" for row in train_rows], dtype=int)
    c = float(config["analysis"]["frozen_baseline_c"])
    iterations = int(config["analysis"]["frozen_baseline_max_iter"])
    # Original v1 seed, not the new data seed.
    baseline_seed = int(config["analysis"]["null_seed"])
    classifier = dict(C=c, max_iter=iterations, random_state=baseline_seed, solver="liblinear")
    vectors = {}
    provenance = {"training_pool": "v1 train sources, families A/B only",
                  "sources": 72, "rows": 576, "v2_rows_used_for_fitting": 0,
                  "source_ids": sorted(old_sources), "C": c, "max_iter": iterations,
                  "seed": baseline_seed, "text_models": {}, "numeric_models": {}}
    augmented = [dict(row) for row in rows]
    texts = [row["response_text"] for row in rows]
    lexical = {
        "tfidf_score": dict(ngram_range=(1, 2), min_df=2, max_features=5000, lowercase=True),
        "char_tfidf_score": dict(analyzer="char_wb", ngram_range=(3, 5), min_df=2,
                                 max_features=10000, lowercase=True),
    }
    for name, settings in lexical.items():
        model = make_pipeline(TfidfVectorizer(**settings), LogisticRegression(**classifier))
        model.fit([row["response_text"] for row in train_rows], labels,
                  logisticregression__sample_weight=weights)
        scores = model.decision_function(texts)
        for row, value in zip(augmented, scores):
            row[name] = float(value)
        vectorizer = model.named_steps["tfidfvectorizer"]
        lr = model.named_steps["logisticregression"]
        vectors[name + "_coef"] = lr.coef_
        vectors[name + "_intercept"] = lr.intercept_
        vectors[name + "_idf"] = vectorizer.idf_
        provenance["text_models"][name] = {"settings": settings,
            "vocabulary": vectorizer.vocabulary_, "classes": lr.classes_.tolist()}
    for field in ("sequence_nll", "mean_token_nll"):
        model = make_pipeline(StandardScaler(), LogisticRegression(**classifier))
        model.fit(np.asarray([[row[field]] for row in train_rows]), labels,
                  logisticregression__sample_weight=weights)
        scores = model.decision_function(np.asarray([[row[field]] for row in rows]))
        name = "frozen_" + field + "_score"
        for row, value in zip(augmented, scores):
            row[name] = float(value)
        scaler, lr = model.named_steps["standardscaler"], model.named_steps["logisticregression"]
        for suffix, value in (("coef", lr.coef_), ("intercept", lr.intercept_),
                              ("scaler_mean", scaler.mean_), ("scaler_scale", scaler.scale_)):
            vectors[name + "_" + suffix] = value
        provenance["numeric_models"][name] = {"field": field, "classes": lr.classes_.tolist()}
    pairs = _validate_and_pair(old_rows, old_hidden)
    train_pairs = _selection(pairs, split="train", family=("A", "B"))
    features = old_hidden[:, 0, 0].astype(np.float64)
    differences = features[[p["confident_index"] for p in pairs]] - features[[p["hedged_index"] for p in pairs]]
    source_ids, source_differences = _source_means(differences, pairs, train_pairs)
    reconstructed = source_differences.mean(axis=0)
    reconstructed /= np.linalg.norm(reconstructed)
    if not np.allclose(reconstructed, directions["layer14_boundary"], rtol=0, atol=1e-12):
        raise ValueError("Legacy source-difference calculation does not reproduce the pinned direction")
    rng = np.random.default_rng(baseline_seed)
    signs = rng.choice((-1.0, 1.0), size=(config["analysis"]["null_repetitions"], len(source_ids)))
    shuffled = signs @ source_differences / len(source_ids)
    norms = np.linalg.norm(shuffled, axis=1)
    directions["shuffled_controls"] = np.divide(shuffled, norms[:, None], out=np.zeros_like(shuffled),
                                                  where=norms[:, None] > 1e-12)
    random_count = int(config["analysis"]["random_directions"])
    if random_count < 2 or random_count % 2:
        raise ValueError("Random controls require an even number of antipodal directions")
    random = rng.standard_normal((random_count // 2, features.shape[1]))
    random /= np.linalg.norm(random, axis=1)[:, None]
    directions["random_controls"] = np.concatenate((random, -random))
    provenance["null_directions"] = {"seed": baseline_seed, "source_ids": source_ids.tolist(),
        "shuffled_repetitions": len(shuffled), "random_antipodal_count": random_count,
        "source_equal_training_differences": True, "v2_used": False}
    output = resolve(config["output"]["results_dir"])
    write_npz(output / "frozen_control_parameters.npz", **vectors)
    write_npz(output / "frozen_readout_and_null_directions.npz", **directions)
    write_json(output / "frozen_control_provenance.json", provenance)
    return augmented, directions
