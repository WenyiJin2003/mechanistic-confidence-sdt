import numpy as np
import pytest
import torch

from stage0.answer_state import (
    build_leave_one_out_targets,
    cross_fitted_probe_scores,
    greedy_leave_one_out_clusters,
    select_answer_representations,
    validate_preserved_split,
)
from stage0.pipeline import best_train_threshold, stable_hash


NLI_MODEL_ID = "cached-test-nli"


def _record(record_id: str, equivalent_targets: bool = False) -> dict:
    suffix = "same" if equivalent_targets else "different"
    return {
        "id": record_id,
        "question": f"Question {record_id}?",
        "context": f"Context {record_id}",
        "generations": [
            {
                "text": "observed",
                "token_ids": [10],
                "token_count": 1,
                "sequence_logprob": -0.4,
                "mean_token_logprob": -0.4,
            },
            {
                "text": f"first {suffix}",
                "token_ids": [11],
                "token_count": 1,
                "sequence_logprob": -0.5,
                "mean_token_logprob": -0.5,
            },
            {
                "text": f"second {suffix}",
                "token_ids": [12],
                "token_count": 1,
                "sequence_logprob": -0.6,
                "mean_token_logprob": -0.6,
            },
        ],
    }


def _add_judgment(cache: dict, record: dict, from_index: int, to_index: int, label: str) -> None:
    premise = f"{record['question']} {record['generations'][from_index]['text']}"
    hypothesis = f"{record['question']} {record['generations'][to_index]['text']}"
    key = stable_hash(
        {
            "model": NLI_MODEL_ID,
            "premise": premise,
            "hypothesis": hypothesis,
        }
    )
    cache[key] = {
        "premise": premise,
        "hypothesis": hypothesis,
        "label": label,
        "probabilities": {"entailment": float(label == "entailment")},
    }


def _target_pair_cache(records: list[dict], equivalent: list[bool]) -> dict:
    cache = {}
    for record, is_equivalent in zip(records, equivalent):
        _add_judgment(
            cache,
            record,
            1,
            2,
            "entailment" if is_equivalent else "neutral",
        )
        if is_equivalent:
            _add_judgment(cache, record, 2, 1, "entailment")
    return cache


def test_leave_one_out_clustering_uses_only_cached_pairwise_judgments():
    record = {
        "id": "greedy",
        "question": "Which answers agree?",
        "context": "A synthetic context",
        "generations": [
            {"text": "held out"},
            {"text": "alpha"},
            {"text": "beta"},
            {"text": "gamma"},
        ],
    }
    cache = {}
    _add_judgment(cache, record, 1, 2, "entailment")
    _add_judgment(cache, record, 2, 1, "entailment")
    _add_judgment(cache, record, 1, 3, "neutral")
    used = {}

    clusters, remaining = greedy_leave_one_out_clusters(
        record,
        observed_answer_index=0,
        nli_cache=cache,
        nli_model_id=NLI_MODEL_ID,
        used_judgments=used,
    )

    assert remaining == [1, 2, 3]
    assert clusters == [0, 0, 1]
    assert len(used) == 3
    assert all(row["record_id"] == "greedy" for row in used.values())

    with pytest.raises(KeyError, match="refusing to run NLI"):
        greedy_leave_one_out_clusters(
            record,
            observed_answer_index=0,
            nli_cache={},
            nli_model_id=NLI_MODEL_ID,
        )


def test_leave_one_out_threshold_is_fit_on_training_rows_only():
    equivalent = [True, False, True, False, False, True]
    records = [
        _record(f"row-{index}", equivalent_targets=value)
        for index, value in enumerate(equivalent)
    ]
    cache = _target_pair_cache(records, equivalent)
    train_indices = np.asarray([0, 1, 2], dtype=np.int64)

    rows, labels, threshold, _ = build_leave_one_out_targets(
        records,
        observed_answer_index=0,
        nli_cache=cache,
        nli_model_id=NLI_MODEL_ID,
        train_indices=train_indices,
    )

    entropy = np.asarray([row["leave_one_out_semantic_entropy"] for row in rows])
    assert np.isclose(threshold, best_train_threshold(entropy[train_indices]))
    assert np.isclose(threshold, np.log(2) / 2)
    np.testing.assert_array_equal(labels, entropy >= threshold)
    assert all(row["threshold_fit_on_training_only"] == threshold for row in rows)


def test_source_split_membership_is_reused_exactly_and_context_disjoint():
    records = [
        {"id": f"row-{index}", "context": f"Context {index}"}
        for index in range(6)
    ]
    source_probe = {
        "train_indices": [4, 0, 2],
        "validation_indices": [5],
        "test_indices": [1, 3],
        "split_method": "fixed_group_split_by_normalized_context",
    }

    split = validate_preserved_split(
        records,
        source_probe,
        expected_sizes={"train": 3, "validation": 1, "test": 2},
    )

    np.testing.assert_array_equal(split["train"], [4, 0, 2])
    np.testing.assert_array_equal(split["validation"], [5])
    np.testing.assert_array_equal(split["test"], [1, 3])
    assert split["audit"]["source_membership_reused_exactly"] is True
    assert set(split["audit"]["context_overlap_counts"].values()) == {0}

    records[1]["context"] = records[0]["context"]
    with pytest.raises(ValueError, match="leaks .* contexts"):
        validate_preserved_split(records, source_probe)


def test_answer_state_selection_uses_final_content_token_and_answer_only_mean():
    hidden_states = [torch.zeros((1, 8, 3), dtype=torch.float32) for _ in range(24)]
    hidden_states[14][0] = torch.arange(24, dtype=torch.float32).reshape(8, 3)
    hidden_states[23][0] = 100 + torch.arange(24, dtype=torch.float32).reshape(8, 3)

    selected = select_answer_representations(
        hidden_states,
        prompt_length=3,
        answer_length=2,
        primary_layer=14,
        exploratory_layer=23,
    )

    assert int(selected["answer_start_index"]) == 3
    assert int(selected["answer_stop_index_exclusive"]) == 5
    assert int(selected["final_answer_token_index"]) == 4
    np.testing.assert_array_equal(
        selected["layer_14_final_answer_token"],
        hidden_states[14][0, 4].numpy().astype(np.float16),
    )
    np.testing.assert_array_equal(
        selected["layer_14_mean_answer_tokens"],
        hidden_states[14][0, 3:5].mean(dim=0).numpy().astype(np.float16),
    )
    np.testing.assert_array_equal(
        selected["layer_23_final_answer_token"],
        hidden_states[23][0, 4].numpy().astype(np.float16),
    )


def test_cross_fitted_probe_scores_cover_training_once_and_ignore_reserved_rows():
    rng = np.random.default_rng(29)
    groups = np.repeat(np.asarray([f"context-{index}" for index in range(18)]), 2)
    labels = np.tile([0, 1], 18)
    features = rng.normal(size=(len(labels), 5))
    features[:, 0] += 1.5 * labels
    train_indices = np.arange(24, dtype=np.int64)
    reserved_indices = np.arange(24, len(labels), dtype=np.int64)

    scores, model, ledger = cross_fitted_probe_scores(
        features,
        labels,
        groups,
        train_indices,
        n_splits=3,
        c_value=0.5,
        seed=7,
    )

    assert len(scores) == len(train_indices)
    assert np.all(np.isfinite(scores))
    heldout = [index for fold in ledger for index in fold["heldout_source_indices"]]
    assert sorted(heldout) == train_indices.tolist()
    assert len(heldout) == len(set(heldout))
    assert all(fold["context_overlap"] == 0 for fold in ledger)
    assert all(
        set(fold["fit_source_indices"]).isdisjoint(reserved_indices)
        and set(fold["heldout_source_indices"]).isdisjoint(reserved_indices)
        for fold in ledger
    )

    # Changing every held-out row must not change any cross-fitted score or the
    # final train-only model. This directly checks that reserved rows never fit
    # either the fold probes or the final probe used by the scalar meta-model.
    changed_features = features.copy()
    changed_features[reserved_indices] = 10_000 + rng.normal(
        size=changed_features[reserved_indices].shape
    )
    changed_labels = labels.copy()
    changed_labels[reserved_indices] = 1 - changed_labels[reserved_indices]
    changed_scores, changed_model, changed_ledger = cross_fitted_probe_scores(
        changed_features,
        changed_labels,
        groups,
        train_indices,
        n_splits=3,
        c_value=0.5,
        seed=7,
    )

    np.testing.assert_allclose(scores, changed_scores)
    np.testing.assert_allclose(
        model.decision_function(features[train_indices]),
        changed_model.decision_function(features[train_indices]),
    )
    assert ledger == changed_ledger
