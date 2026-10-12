"""One-shot leakage-safe transfer evaluation for the locked cue-holdout set.

This script intentionally fails closed unless the 50-pair challenge file has
matching lock metadata and two complete blinded reviews. It supports either a
human-reviewed transfer evaluation or an explicitly development-only agent-
reviewed pilot. No challenge threshold, layer, sign, or model selection occurs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve()
CHALLENGE = HERE.parents[1]
DEFAULT_CONFIG = CHALLENGE / "configs" / "cue_holdout_challenge_v1.yaml"
FROZEN_TASKS = (
    "factual_explanation", "math_logic", "programming",
    "comparison_analysis", "summary_judgment",
)
FROZEN_CUE_FAMILIES = (
    "embedded_stance_predicate", "modal_force_scope", "compositional_polarity",
    "discourse_level_calibration", "contrastive_commitment",
)
FROZEN_DATASETS = ("nvidia/HelpSteer2", "allenai/WildChat-1M")
FROZEN_REFERENCE_CONFIG = "../../diverse_pairs_multilayer_v1/configs/diverse_pairs_multilayer_v1.yaml"
FROZEN_REFERENCE_CONFIG_SHA256 = "1c8f857b2ba62d236e3eec55c7647285bc5aa673935ab824b97bc57f835fae9a"
FROZEN_TFIDF = {
    "analyzer": "char_wb", "ngram_range": [3, 5], "min_df": 2,
    "max_features": 20000, "sublinear_tf": True,
}


class ReviewStatusError(ValueError):
    """Raised when the locked challenge lacks the required human-review gate."""


def validate_frozen_protocol_config(config: dict[str, Any]) -> dict[str, Any]:
    """Fail closed if a score-affecting preregistered challenge setting changed."""
    if config.get("experiment") != "cue_holdout_challenge_v1" or config.get("protocol_version") != 1:
        raise ValueError("Unexpected challenge experiment or protocol version")
    if config.get("seed") != 20261012:
        raise ValueError("Challenge evaluation seed differs from the frozen protocol")
    if (config.get("reference_config") != FROZEN_REFERENCE_CONFIG
            or config.get("reference_config_sha256") != FROZEN_REFERENCE_CONFIG_SHA256):
        raise ValueError("Reference readout configuration differs from the frozen protocol")
    challenge = config.get("challenge")
    readout = config.get("readout")
    if not isinstance(challenge, dict) or not isinstance(readout, dict):
        raise ValueError("Challenge config must contain challenge and readout mappings")
    expected_challenge = {
        "required_pairs": 50,
        "required_independent_reviewers": 2,
        "source_datasets": list(FROZEN_DATASETS),
        "tasks": list(FROZEN_TASKS),
        "cue_families": list(FROZEN_CUE_FAMILIES),
        "required_longer_member_counts": {"confident_longer": 25, "hedged_longer": 25},
    }
    for key, value in expected_challenge.items():
        if challenge.get(key) != value:
            raise ValueError(f"Challenge {key} differs from the frozen protocol")
    if challenge.get("required_review_status") not in {
            "agent_reviewed_development_only", "human_review_passed"}:
        raise ValueError("Unsupported challenge review mode")
    expected_readout = {
        "primary_layer": 14,
        "ensemble": "equal_train_standardized_28_layer_scores",
        "bootstrap_draws": 2000,
        "shuffled_training_orientation_fits": 200,
        "nll_control": "negative_mean_response_token_nll",
        "length_control": "negative_response_token_length",
        "layer_selection_on_challenge": False,
        "sign_selection_on_challenge": False,
        "tfidf": FROZEN_TFIDF,
    }
    for key, value in expected_readout.items():
        if readout.get(key) != value:
            raise ValueError(f"Readout {key} differs from the frozen protocol")
    return {
        "primary_layer": 14,
        "ensemble": expected_readout["ensemble"],
        "layers": list(range(1, 29)),
        "challenge_layer_selection": False,
        "challenge_sign_selection": False,
    }


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_text(value: str) -> str:
    return _sha256_bytes(value.encode("utf-8"))


def _prompt_hash(row: dict) -> str:
    stored = row.get("normalized_prompt_sha256")
    if stored:
        return stored
    normalized = " ".join(row["prompt"].casefold().split())
    return _sha256_text(normalized)


def source_ids_sha256(rows: list[dict]) -> str:
    material = "\n".join(sorted(row["source_id"] for row in rows))
    return _sha256_text(material)


def _validated_source_datasets(values: Any) -> tuple[str, str]:
    if (not isinstance(values, (list, tuple)) or len(values) != 2
            or any(not isinstance(value, str) or not value.strip() for value in values)
            or len(set(values)) != 2):
        raise ValueError("Challenge config must declare exactly two distinct nonempty source datasets")
    return values[0], values[1]


def _dataset_counts(rows: list[dict], source_datasets: tuple[str, str]) -> dict[str, int]:
    counts = Counter(row.get("dataset") for row in rows)
    return {dataset: counts[dataset] for dataset in source_datasets}


def validate_lock_metadata(lock: dict, pairs_bytes: bytes, challenge_pairs: list[dict],
                           required_review_status: str = "human_review_passed",
                           selection_manifest_bytes: bytes | None = None,
                           required_independent_reviewers: int = 2) -> dict:
    if lock.get("locked") is not True:
        raise ValueError("Challenge metadata must explicitly set locked=true")
    status = lock.get("review_status")
    if not isinstance(status, str) or not status.strip():
        raise ValueError("Challenge lock metadata must include a nonempty review_status")
    if status == "agent_only_pre_screen":
        raise ReviewStatusError("review_status=agent_only_pre_screen is not an evaluation review status")
    if status != required_review_status:
        raise ReviewStatusError(f"Required review_status={required_review_status}; found {status}")
    reviewer_types = lock.get("reviewer_types")
    reviewers = lock.get("reviewers")
    if (not isinstance(reviewers, list) or len(reviewers) != required_independent_reviewers
            or lock.get("independent_reviewer_count") != required_independent_reviewers
            or lock.get("independent_reviews_complete") is not True
            or lock.get("reviews_blinded") is not True):
        raise ReviewStatusError("Lock must document the required complete, independent, blinded reviews")
    ids = [entry.get("reviewer_id") for entry in reviewers if isinstance(entry, dict)]
    types = [entry.get("reviewer_type") for entry in reviewers if isinstance(entry, dict)]
    if (len(ids) != required_independent_reviewers or len(set(ids)) != required_independent_reviewers
            or any(not isinstance(value, str) or not value for value in ids)
            or any(entry.get("review_status") != "passed" or entry.get("blinded") is not True
                   for entry in reviewers if isinstance(entry, dict))
            or len(types) != required_independent_reviewers
            or reviewer_types != types):
        raise ReviewStatusError("Reviewers must have distinct IDs, explicit types, and complete blinded passes")
    if status == "agent_reviewed_development_only":
        if (set(types) != {"agent"} or lock.get("human_review") != "pending"
                or lock.get("scientific_status") != "development_only_not_human_validated"
                or lock.get("agent_review_is_human_review") is not False):
            raise ReviewStatusError("Agent-reviewed development mode requires explicit non-human provenance")
        human_review = False
        scientific_status = "development_only_not_human_validated"
    elif status == "human_review_passed":
        if (set(types) != {"human"} or lock.get("human_review") != "passed"
                or lock.get("scientific_status") != "locked_human_reviewed_transfer_evaluation"
                or lock.get("agent_review_is_human_review") is not False):
            raise ReviewStatusError("Human-reviewed mode requires explicit human reviewer provenance")
        human_review = True
        scientific_status = "locked_human_reviewed_transfer_evaluation"
    else:
        raise ReviewStatusError(f"Unsupported review_status={status}")
    if lock.get("pair_count") != len(challenge_pairs) or len(challenge_pairs) != 50:
        raise ValueError("Lock pair_count and challenge file must both contain exactly 50 pairs")
    if lock.get("challenge_pairs_sha256") != _sha256_bytes(pairs_bytes):
        raise ValueError("Challenge pair file does not match its locked SHA-256")
    if lock.get("source_ids_sha256") != source_ids_sha256(challenge_pairs):
        raise ValueError("Challenge source IDs do not match the locked source-ID digest")
    hashes = lock.get("hashes")
    packet_digest = hashes.get("blind_packet_sha256") if isinstance(hashes, dict) else None
    if (not isinstance(packet_digest, str) or len(packet_digest) != 64
            or any(character not in "0123456789abcdef" for character in packet_digest)):
        raise ValueError("Challenge lock must include the exact blinded review-packet SHA-256")
    if any(not isinstance(row.get("dataset"), str) or not row["dataset"].strip()
           for row in challenge_pairs):
        raise ValueError("Every locked challenge pair must include a nonempty dataset")
    pair_dataset_counts = dict(sorted(Counter(row["dataset"] for row in challenge_pairs).items()))
    lock_counts = lock.get("counts")
    if not isinstance(lock_counts, dict) or lock_counts.get("datasets") != pair_dataset_counts:
        raise ValueError("Challenge dataset counts do not match the locked metadata")
    if selection_manifest_bytes is not None and lock.get("selection_manifest_sha256") != _sha256_bytes(selection_manifest_bytes):
        raise ValueError("Challenge lock does not match the frozen source-selection manifest")
    return {"review_status": status, "reviewer_types": types,
            "independent_reviewer_count": required_independent_reviewers,
            "human_review": human_review, "scientific_status": scientific_status,
            "agent_review_is_human_review": False, "by_dataset": pair_dataset_counts,
            "blind_packet_sha256": packet_digest}


def validate_development_acceptance(pairs: list[dict], manifest: dict,
                                    accepted_ids: set[str], rejected_ids: set[str]) -> dict:
    if len(pairs) != 50 or manifest.get("pairs") != 50:
        raise ValueError("Development training set must contain exactly 50 accepted pairs")
    ids = {row.get("review_id") for row in pairs}
    if None in ids or len(ids) != 50 or ids != accepted_ids or rejected_ids:
        raise ValueError("Development agent-QA acceptance does not cover the exact training set")
    if manifest.get("final_agent_accepted") != 50 or manifest.get("final_agent_rejected_or_pending") != 0:
        raise ValueError("Development agent-QA summary is incomplete")
    if manifest.get("agent_qa_is_human_review") is not False:
        raise ValueError("Development review provenance must explicitly say agent QA is not human review")
    if manifest.get("human_review") != "pending":
        raise ValueError("Development set's pending human-review status changed unexpectedly")
    return {"status": "agent_qa_accepted", "pairs": 50,
            "human_review": "pending", "agent_qa_is_human_review": False}


def _validate_pair_text(row: dict, *, challenge: bool,
                        required_review_status: str | None = None,
                        reviewer_types: list[str] | None = None,
                        independent_reviewer_count: int | None = None) -> None:
    required = ["source_id", "group_id", "prompt", "original_response",
                "confident_response", "hedged_response", "review_id"]
    if challenge:
        required += ["dataset", "task", "cue_family", "length_direction"]
    missing = [key for key in required if not isinstance(row.get(key), str) or not row[key].strip()]
    if missing:
        raise ValueError(f"Pair {row.get('review_id', '<unknown>')} missing fields: {', '.join(missing)}")
    if row["confident_response"] == row["hedged_response"]:
        raise ValueError(f"Identical confident/hedged responses for {row['review_id']}")
    if row.get("original_response_sha256") and row["original_response_sha256"] != _sha256_text(row["original_response"]):
        raise ValueError(f"Original response SHA-256 mismatch for {row['review_id']}")
    if row.get("normalized_prompt_sha256") and row["normalized_prompt_sha256"] != _sha256_text(" ".join(row["prompt"].casefold().split())):
        raise ValueError(f"Normalized prompt SHA-256 mismatch for {row['review_id']}")
    if challenge:
        if row["confident_response"] == row["original_response"] or row["hedged_response"] == row["original_response"]:
            raise ValueError(f"Both challenge variants must be rewritten from source: {row['review_id']}")
        if required_review_status == "agent_reviewed_development_only":
            expected = {"human_review": "pending", "scientific_status": "development_only_not_human_validated",
                        "agent_review_is_human_review": False}
        elif required_review_status == "human_review_passed":
            expected = {"human_review": "passed", "scientific_status": "locked_human_reviewed_transfer_evaluation",
                        "agent_review_is_human_review": False}
        else:
            raise ReviewStatusError("Challenge row validation requires an explicit supported review mode")
        for field, value in expected.items():
            if row.get(field) != value:
                raise ReviewStatusError(f"Challenge row {row['review_id']} must record {field}={value}")
        if (row.get("reviewer_types") != reviewer_types
                or row.get("independent_reviewer_count") != independent_reviewer_count
                or row.get("independent_reviews_complete") is not True
                or row.get("reviews_blinded") is not True):
            raise ReviewStatusError(f"Challenge row {row['review_id']} review provenance differs from lock")
        if row.get("reserved_split") not in (None, "challenge_holdout", "locked_challenge"):
            raise ValueError(f"Challenge row has unexpected split provenance: {row['review_id']}")


def validate_challenge_design(pairs: list[dict], tasks: list[str], cue_families: list[str],
                             direction_targets: dict[str, int],
                             required_review_status: str = "human_review_passed",
                             reviewer_types: list[str] | None = None,
                             independent_reviewer_count: int | None = None, *,
                             source_datasets: list[str] | tuple[str, str]) -> dict:
    declared_datasets = _validated_source_datasets(source_datasets)
    if reviewer_types is None:
        reviewer_types = ["human", "human"]
    if independent_reviewer_count is None:
        independent_reviewer_count = 2
    if len(pairs) != 50:
        raise ValueError("Challenge test set must contain exactly 50 pairs")
    for row in pairs:
        _validate_pair_text(row, challenge=True, required_review_status=required_review_status,
                            reviewer_types=reviewer_types,
                            independent_reviewer_count=independent_reviewer_count)
        if row["dataset"] not in declared_datasets:
            raise ValueError(f"Challenge pair {row['review_id']} has unsupported dataset {row['dataset']!r}")
    for field in ("source_id", "group_id"):
        if len({row[field] for row in pairs}) != 50:
            raise ValueError(f"Challenge pairs must have unique {field} values")
    if Counter(row["task"] for row in pairs) != Counter({task: 10 for task in tasks}):
        raise ValueError("Challenge must contain exactly 10 sources per task")
    if Counter(row["cue_family"] for row in pairs) != Counter({family: 10 for family in cue_families}):
        raise ValueError("Challenge cue-family margins must be exactly 10 each")
    cells = Counter((row["task"], row["cue_family"]) for row in pairs)
    if cells != Counter({(task, family): 2 for task in tasks for family in cue_families}):
        raise ValueError("Each task × cue-family cell must contain exactly two pairs")
    directions = Counter((row["task"], row["cue_family"], row["length_direction"]) for row in pairs)
    if directions != Counter({(task, family, direction): 1 for task in tasks for family in cue_families
                              for direction in direction_targets}):
        raise ValueError("Each task × cue-family cell must contain one source per length direction")
    if Counter(row["length_direction"] for row in pairs) != Counter(direction_targets):
        raise ValueError("Challenge must meet the frozen 25/25 length-direction assignment")
    if sum(row["cue_family"] == "compositional_polarity" for row in pairs) < 10:
        raise ValueError("Challenge must include at least 10 compositional-polarity pairs")
    return {"pairs": 50, "by_dataset": _dataset_counts(pairs, declared_datasets),
            "by_task": dict(Counter(row["task"] for row in pairs)),
            "by_cue_family": dict(Counter(row["cue_family"] for row in pairs)),
            "by_length_direction": dict(Counter(row["length_direction"] for row in pairs))}


def validate_selection_manifest(selection_manifest: dict, challenge: list[dict],
                                source_datasets: list[str] | tuple[str, str]) -> dict:
    declared_datasets = _validated_source_datasets(source_datasets)
    records = selection_manifest.get("source_records")
    if selection_manifest.get("source_count") != 50 or not isinstance(records, list) or len(records) != 50:
        raise ValueError("Frozen source-selection manifest must describe exactly 50 sources")
    selected = {row.get("source_id"): row for row in records}
    if len(selected) != 50 or set(selected) != {row["source_id"] for row in challenge}:
        raise ValueError("Challenge source IDs differ from the frozen selection manifest")
    for source_id, selected_row in selected.items():
        if selected_row.get("dataset") not in declared_datasets:
            raise ValueError(f"Selection source {source_id} has unsupported dataset {selected_row.get('dataset')!r}")
    for pair in challenge:
        selected_row = selected[pair["source_id"]]
        for field in ("dataset", "task", "cue_family", "length_direction", "group_id", "normalized_prompt_sha256"):
            if selected_row.get(field) != pair.get(field):
                raise ValueError(f"Challenge pair {pair['review_id']} changed frozen {field}")
    record_counts = _dataset_counts(records, declared_datasets)
    pair_counts = _dataset_counts(challenge, declared_datasets)
    manifest_counts = selection_manifest.get("by_dataset")
    if (not isinstance(manifest_counts, dict)
            or set(manifest_counts) - set(declared_datasets)
            or any(isinstance(value, bool) or not isinstance(value, int) or value < 0
                   for value in manifest_counts.values())):
        raise ValueError("Frozen selection manifest has invalid dataset counts")
    normalized_manifest_counts = {
        dataset: manifest_counts.get(dataset, 0) for dataset in declared_datasets
    }
    if record_counts != pair_counts or normalized_manifest_counts != record_counts:
        raise ValueError("Challenge dataset counts differ from the frozen selection manifest")
    return {"declared_source_datasets": list(declared_datasets), "by_dataset": pair_counts,
            "selection_records_match_locked_pairs": True,
            "selection_aggregate_matches_records": True}


def validate_independence(development: list[dict], challenge: list[dict]) -> dict:
    if len({row["source_id"] for row in development}) != len(development):
        raise ValueError("Development source IDs are not unique")
    if len({row["group_id"] for row in development}) != len(development):
        raise ValueError("Development source groups are not unique")
    for field, label in (("source_id", "source ID"), ("group_id", "source group")):
        overlap = {row[field] for row in development} & {row[field] for row in challenge}
        if overlap:
            raise ValueError(f"Development/challenge {label} leakage detected")
    dev_prompt_hashes = {_prompt_hash(row) for row in development}
    challenge_prompt_hashes = {_prompt_hash(row) for row in challenge}
    if dev_prompt_hashes & challenge_prompt_hashes:
        raise ValueError("Development/challenge normalized-prompt leakage detected")
    dev_originals = {row.get("original_response_sha256") or _sha256_text(row["original_response"])
                     for row in development}
    challenge_originals = {row.get("original_response_sha256") or _sha256_text(row["original_response"])
                          for row in challenge}
    if dev_originals & challenge_originals:
        raise ValueError("Development/challenge original-response leakage detected")
    return {"source_ids_disjoint": True, "groups_disjoint": True,
            "normalized_prompts_disjoint": True, "original_responses_disjoint": True}


def flatten_pairs(pairs: list[dict]) -> list[dict]:
    rows = []
    for pair in pairs:
        for variant in ("confident", "hedged"):
            rows.append({"source_id": pair["source_id"], "group_id": pair["group_id"],
                         "review_id": pair["review_id"], "variant": variant, "prompt": pair["prompt"],
                         "response_text": pair[variant + "_response"], "human_review": pair.get("human_review", "pending")})
    return rows


def _load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def require_fresh_result_path(path: Path) -> None:
    """Preserve the one-shot challenge result once it has been written."""
    if Path(path).exists():
        raise FileExistsError(f"Challenge result already exists; refusing overwrite: {path}")


def _grouped_interval(scores: Any, groups: Any, readouts: Any, seed: int, draws: int) -> dict:
    result = readouts.grouped_bootstrap_accuracy(scores, groups, n_boot=draws, seed=seed)
    delta = scores[:, 0] - scores[:, 1]
    return {"estimate": result["estimate"], "ci95": [float(x) for x in result["ci"]],
            "groups": int(result["groups"]), "wins": int((delta > 0).sum()),
            "ties": int((delta == 0).sum()), "losses": int((delta < 0).sum())}


def _difference(scores_a: Any, scores_b: Any, groups: Any, readouts: Any, seed: int, draws: int) -> dict:
    result = readouts.grouped_bootstrap_difference(scores_a, scores_b, groups, n_boot=draws, seed=seed)
    return {"estimate_b_minus_a": float(result["estimate"]),
            "ci95": [float(x) for x in result["ci"]], "groups": int(result["groups"])}


def _exploratory_groups(challenge: list[dict], field: str, categories: list[str],
                        scores_by_name: dict[str, Any], test_groups: Any,
                        readouts: Any, seed: int, draws: int) -> dict:
    out = {}
    for category in categories:
        indices = [i for i, pair in enumerate(challenge) if pair[field] == category]
        if len(indices) < 2:
            continue
        group = test_groups[indices]
        out[category] = {
            name: _grouped_interval(scores[indices], group, readouts,
                                    seed + len(out) * 10 + method_index, draws)
            for method_index, (name, scores) in enumerate(scores_by_name.items())
        }
    return out


def _fit_text_control(train_pairs: list[dict], test_pairs: list[dict], C: float,
                      vectorizer_config: dict, np: Any, LogisticRegression: Any,
                      TfidfVectorizer: Any, vstack: Any) -> Any:
    vectorizer = TfidfVectorizer(analyzer=vectorizer_config["analyzer"],
                                 ngram_range=tuple(vectorizer_config["ngram_range"]),
                                 min_df=vectorizer_config["min_df"],
                                 max_features=vectorizer_config["max_features"],
                                 sublinear_tf=vectorizer_config["sublinear_tf"])
    train_text = [pair[key] for pair in train_pairs for key in ("confident_response", "hedged_response")]
    matrix = vectorizer.fit_transform(train_text)
    delta = matrix[0::2] - matrix[1::2]
    symmetric = vstack([delta, -delta])
    labels = np.r_[np.ones(len(train_pairs)), np.zeros(len(train_pairs))]
    model = LogisticRegression(C=C, fit_intercept=False, max_iter=2000, solver="liblinear")
    model.fit(symmetric, labels, sample_weight=np.full(2 * len(train_pairs), .5))
    scores = np.empty((len(test_pairs), 2), dtype=float)
    for index, pair in enumerate(test_pairs):
        features = vectorizer.transform([pair["confident_response"], pair["hedged_response"]])
        scores[index] = model.decision_function(features)
    return scores


def fit_frozen_hidden_readouts(dev_X: Any, test_X: Any, dev_groups: Any,
                               readouts: Any, C: float, max_iter: int) -> dict:
    """Fit fixed hidden-state readouts on development arrays and score test arrays once."""
    paired = readouts.PairedLayerReadouts(C=C, max_iter=max_iter).fit(dev_X, dev_groups)
    layer_scores = paired.decision_function(test_X)
    ensemble_scores = paired.equal_scores(test_X)
    mean_difference = readouts.MeanDifferenceReadout().fit(dev_X, dev_groups)
    mean_difference_layers = mean_difference.decision_function(test_X)
    mean_difference_ensemble = mean_difference.equal_scores(test_X)
    return {"paired_model": paired, "layer_scores": layer_scores, "ensemble_scores": ensemble_scores,
            "mean_difference_model": mean_difference, "mean_difference_layer_scores": mean_difference_layers,
            "mean_difference_ensemble_scores": mean_difference_ensemble}


def evaluate_arrays(development: list[dict], challenge: list[dict], dev_states: Any, test_states: Any,
                    dev_enriched: list[dict], test_enriched: list[dict], extraction_audit: dict,
                    config: dict, np: Any, readouts: Any, TfidfVectorizer: Any,
                    LogisticRegression: Any, vstack: Any) -> dict:
    """Fit train-only readouts once, then evaluate the frozen models on challenge arrays."""
    n_dev, n_test = len(development), len(challenge)
    if dev_states.shape != (2 * n_dev, 28, 3, 1536) or test_states.shape != (2 * n_test, 28, 3, 1536):
        raise ValueError("Unexpected extracted state array shape")
    dev_X = dev_states.reshape(n_dev, 2, 28, 3, 1536)[:, :, :, 0, :].astype(np.float32)
    test_pair_states = test_states.reshape(n_test, 2, 28, 3, 1536)
    test_X = test_pair_states[:, :, :, 0, :].astype(np.float32)
    test_prompt_X = test_pair_states[:, :, :, 2, :]
    prompt_diff = float(np.max(np.abs(test_prompt_X[:, 0] - test_prompt_X[:, 1])))
    tolerance = float(config["runtime"]["prompt_control_atol"])
    if not extraction_audit.get("prompt_ids_identical_within_source") or prompt_diff > tolerance:
        raise ValueError("Identical-prompt negative control failed")
    dev_groups = np.asarray([pair["group_id"] for pair in development])
    test_groups = np.asarray([pair["group_id"] for pair in challenge])
    if len(set(dev_groups)) != n_dev or len(set(test_groups)) != n_test:
        raise ValueError("Readout fitting/evaluation requires independent unique source groups")

    reference = config["readout"]
    fitted = fit_frozen_hidden_readouts(dev_X, test_X, dev_groups, readouts,
                                        reference["C"], reference["max_iter"])
    layers = fitted["layer_scores"]
    ensemble = fitted["ensemble_scores"]
    md_layers = fitted["mean_difference_layer_scores"]
    md_ensemble = fitted["mean_difference_ensemble_scores"]
    l14_index = int(config["model"]["layers"].index(config["evaluation"]["primary_layer"]))

    tfidf = _fit_text_control(development, challenge, reference["C"], config["evaluation"]["tfidf"], np,
                              LogisticRegression, TfidfVectorizer, vstack)
    test_lookup = {(row["source_id"], row["variant"]): index for index, row in enumerate(test_enriched)}
    def score_pair_controls(pairs, lookup, enriched):
        nll_scores, length_scores = np.empty((len(pairs), 2)), np.empty((len(pairs), 2))
        actual_directions = Counter()
        token_deltas = []
        direction_mismatches = 0
        for index, pair in enumerate(pairs):
            positions = [lookup[(pair["source_id"], "confident")], lookup[(pair["source_id"], "hedged")]]
            # The extraction adapter keys augmented rows by source_id and variant in order.
            conf, hedge = (enriched[pos] for pos in positions)
            conf_len = len(conf["tokens"]["response_ids"])
            hedge_len = len(hedge["tokens"]["response_ids"])
            nll_scores[index] = [-conf["mean_token_nll"], -hedge["mean_token_nll"]]
            length_scores[index] = [-conf_len, -hedge_len]
            token_deltas.append(conf_len - hedge_len)
            actual_direction = ("confident_longer" if conf_len > hedge_len else
                                "hedged_longer" if hedge_len > conf_len else "tie")
            actual_directions[actual_direction] += 1
            direction_mismatches += actual_direction != pair["length_direction"]
        return nll_scores, length_scores, token_deltas, actual_directions, direction_mismatches

    nll, length, token_deltas, actual_direction_counts, direction_mismatches = score_pair_controls(
        challenge, test_lookup, test_enriched)
    expected_directions = config["challenge"]["required_longer_member_counts"]
    if (any(actual_direction_counts[key] != expected_directions[key] for key in expected_directions)
            or actual_direction_counts["tie"] or direction_mismatches):
        raise ValueError(f"Actual challenge token lengths violate frozen per-pair directions: {dict(actual_direction_counts)}")

    draws, seed = config["evaluation"]["bootstrap_draws"], config["seed"]
    layer_metrics = []
    for layer_index, layer_id in enumerate(config["model"]["layers"]):
        scores = layers[:, :, layer_index]
        metric = _grouped_interval(scores, test_groups, readouts, seed + layer_index, draws)
        metric.update(layer=int(layer_id), mean_pair_margin=float(np.mean(scores[:, 0] - scores[:, 1])))
        layer_metrics.append(metric)
    l14, md14 = layers[:, :, l14_index], md_layers[:, :, l14_index]
    primary = _grouped_interval(l14, test_groups, readouts, seed + 100, draws)
    ensemble_metric = _grouped_interval(ensemble, test_groups, readouts, seed + 101, draws)
    control_scores = {"char_tfidf": tfidf, "negative_mean_response_nll": nll,
                      "negative_response_token_length": length}
    controls = {name: _grouped_interval(scores, test_groups, readouts, seed + 110 + i, draws)
                for i, (name, scores) in enumerate(control_scores.items())}
    differences = {name: _difference(scores, l14, test_groups, readouts, seed + 130 + i, draws)
                   for i, (name, scores) in enumerate(control_scores.items())}
    ensemble_difference = _difference(l14, ensemble, test_groups, readouts, seed + 140, draws)
    mean_difference_control = {
        "layer14": _grouped_interval(md14, test_groups, readouts, seed + 150, draws),
        "equal_28_layer_mean_difference": _grouped_interval(md_ensemble, test_groups, readouts, seed + 151, draws),
    }

    rng = np.random.default_rng(seed + 200)
    shuffled_l14, shuffled_ensemble = [], []
    for _ in range(config["evaluation"]["shuffled_training_orientation_fits"]):
        flips = rng.random(n_dev) < .5
        shuffled_X = dev_X.copy()
        shuffled_X[flips] = shuffled_X[flips, ::-1]
        null_readout = readouts.PairedLayerReadouts(C=reference["C"], max_iter=reference["max_iter"])
        null_readout.fit(shuffled_X, dev_groups)
        null_layers = null_readout.decision_function(test_X)
        null_ens = null_readout.equal_scores(test_X)
        shuffled_l14.append(readouts.paired_accuracy(null_layers[:, :, l14_index]))
        shuffled_ensemble.append(readouts.paired_accuracy(null_ens))
    shuffled = {
        "repeats": len(shuffled_l14), "descriptive_not_formal_p_value": True,
        "layer14": {"mean": float(np.mean(shuffled_l14)), "q95": float(np.quantile(shuffled_l14, .95)),
                    "count_at_least_observed": int(np.sum(np.asarray(shuffled_l14) >= primary["estimate"]))},
        "equal_28_layer_ensemble": {"mean": float(np.mean(shuffled_ensemble)),
                                    "q95": float(np.quantile(shuffled_ensemble, .95)),
                                    "count_at_least_observed": int(np.sum(np.asarray(shuffled_ensemble) >= ensemble_metric["estimate"]))},
    }

    exploratory_scores = {"layer14": l14, "ensemble": ensemble, **control_scores}
    exploratory = {
        "interpretation": "descriptive subgroups only; no model, threshold, sign, family, or dataset selection",
        "by_task": _exploratory_groups(challenge, "task", config["challenge"]["tasks"],
                                        exploratory_scores, test_groups, readouts, seed + 300, draws),
        "by_cue_family": _exploratory_groups(
            challenge, "cue_family", config["challenge"]["cue_families"],
            exploratory_scores, test_groups, readouts, seed + 400, draws),
        "by_dataset": _exploratory_groups(
            challenge, "dataset", config["challenge"]["source_datasets"],
            exploratory_scores, test_groups, readouts, seed + 500, draws),
    }
    return {
        "layer14": primary,
        "equal_28_layer_ensemble": ensemble_metric,
        "ensemble_minus_layer14": ensemble_difference,
        "per_layer": layer_metrics,
        "controls": controls,
        "layer14_minus_controls": differences,
        "mean_difference_control": mean_difference_control,
        "shuffled_training_orientation": shuffled,
        "exploratory_diagnostics": exploratory,
        "length_audit": {"actual_confident_longer": actual_direction_counts["confident_longer"],
                         "actual_hedged_longer": actual_direction_counts["hedged_longer"],
                         "ties": actual_direction_counts["tie"],
                         "confident_minus_hedged_token_delta_min": int(min(token_deltas)),
                         "confident_minus_hedged_token_delta_max": int(max(token_deltas)),
                         "pairs_within_three_tokens": int(sum(abs(delta) <= 3 for delta in token_deltas))},
        "prompt_state_control": {"prompt_ids_identical_within_source": bool(extraction_audit["prompt_ids_identical_within_source"]),
                                 "max_abs_pair_difference": prompt_diff, "atol": tolerance},
        "extractor": {key: extraction_audit[key] for key in
                      ("rows", "forward_calls", "cache_hits", "elapsed_seconds", "device", "dtype",
                       "settings_sha256", "all_pooled_states_finite", "generation_calls")},
        "training_fits": {"paired_layer_readout_full_development_fit_count": 1,
                          "mean_difference_full_development_fit_count": 1,
                          "char_tfidf_fit_scope": "development responses only",
                          "score_and_feature_scaling_scope": "development responses only"},
        "selection_controls": {"challenge_layer_selection": False, "challenge_threshold_selection": False,
                               "challenge_sign_selection": False, "test_fit_for_primary_readout": False,
                               "dataset_stratum_used_for_selection_or_gating": False},
    }


def run(config_path: Path = DEFAULT_CONFIG) -> dict:
    import yaml

    config_path = Path(config_path).resolve()
    eval_config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    frozen_protocol = validate_frozen_protocol_config(eval_config)
    source_datasets = _validated_source_datasets(eval_config["challenge"].get("source_datasets"))
    base = config_path.parent.parent
    output = (base / eval_config["output"]["public_results"]).resolve()
    require_fresh_result_path(output)
    ref_path = (config_path.parent / eval_config["reference_config"]).resolve()
    ref_hash = _sha256_bytes(ref_path.read_bytes())
    if ref_hash != eval_config["reference_config_sha256"]:
        raise ValueError("Reference model/readout config hash differs from pinned challenge config")

    dev_path = (base / eval_config["development"]["pairs"]).resolve()
    dev_manifest_path = (base / eval_config["development"]["agent_qa_manifest"]).resolve()
    challenge_path = (base / eval_config["challenge"]["pairs"]).resolve()
    lock_path = (base / eval_config["challenge"]["lock_metadata"]).resolve()
    selection_manifest_path = (base / eval_config["challenge"]["selection_manifest"]).resolve()
    dev_pairs = _load_jsonl(dev_path)
    for pair in dev_pairs:
        _validate_pair_text(pair, challenge=False)
        if pair.get("reserved_split") != "train_development":
            raise ValueError(f"Development source is outside the pinned training split: {pair['review_id']}")
    challenge_pairs_bytes = challenge_path.read_bytes()
    challenge_pairs = [json.loads(line) for line in challenge_pairs_bytes.decode("utf-8").splitlines() if line.strip()]
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    selection_manifest_bytes = selection_manifest_path.read_bytes()
    selection_manifest = json.loads(selection_manifest_bytes.decode("utf-8"))
    lock_provenance = validate_lock_metadata(lock, challenge_pairs_bytes, challenge_pairs,
                                              eval_config["challenge"]["required_review_status"],
                                              selection_manifest_bytes,
                                              eval_config["challenge"]["required_independent_reviewers"])
    challenge_design = validate_challenge_design(
        challenge_pairs, eval_config["challenge"]["tasks"],
        eval_config["challenge"]["cue_families"],
        eval_config["challenge"]["required_longer_member_counts"],
        eval_config["challenge"]["required_review_status"],
        lock_provenance["reviewer_types"], lock_provenance["independent_reviewer_count"],
        source_datasets=source_datasets)
    dataset_provenance = validate_selection_manifest(
        selection_manifest, challenge_pairs, source_datasets)
    manifest = json.loads(dev_manifest_path.read_text(encoding="utf-8"))

    src = ref_path.parent.parent / "src"
    sys.path.insert(0, str(src))
    from run_development_diagnostic import accepted_agent_qa
    from extraction import extract_rows, load_config as load_reference_config, write_json
    import numpy as np
    from scipy.sparse import vstack
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    import readouts

    accepted, rejected = accepted_agent_qa(dev_pairs)
    dev_review = validate_development_acceptance(dev_pairs, manifest,
                    {row["review_id"] for row in accepted}, {row["review_id"] for row in rejected})
    independence = validate_independence(dev_pairs, challenge_pairs)
    if len(dev_pairs) != eval_config["development"]["required_pairs"] or len(challenge_pairs) != eval_config["challenge"]["required_pairs"]:
        raise ValueError("Pinned development/challenge pair counts changed")

    reference = load_reference_config(ref_path)
    if reference["model"]["revision"] != "989aa7980e4cf806f80c7fef2b1adb7bc71aa306":
        raise ValueError("Unexpected pinned Qwen snapshot revision")
    if reference["model"]["layers"] != list(range(1, 29)) or reference["readout"]["primary_reference_layer"] != 14:
        raise ValueError("Reference layer set or primary layer differs from preregistered config")
    reference["runtime"]["max_pairs"] = 100
    reference["runtime"]["max_seconds"] = eval_config["runtime"]["max_seconds"]
    reference["runtime"]["cache_dir"] = str((base / eval_config["runtime"]["cache_dir"]).resolve())
    reference["data"]["phase"] = "train_development_engineering_only"
    flat = flatten_pairs(dev_pairs) + flatten_pairs(challenge_pairs)
    started = time.monotonic()
    enriched, states, audit = extract_rows(flat, reference, check_padding=False)
    if states.shape != (200, 28, 3, 1536):
        raise ValueError(f"Unexpected combined extraction shape: {states.shape}")
    dev_enriched, test_enriched = enriched[:100], enriched[100:]
    dev_states, test_states = states[:100], states[100:]
    metrics = evaluate_arrays(dev_pairs, challenge_pairs, dev_states, test_states,
                              dev_enriched, test_enriched, audit, reference | {"evaluation": eval_config["readout"],
                              "challenge": eval_config["challenge"]}, np, readouts,
                              TfidfVectorizer, LogisticRegression, vstack)
    # Public outputs contain aggregate metrics and cryptographic provenance only.
    result = {
        "status": "complete",
        "scientific_status": lock_provenance["scientific_status"],
        "review_status": lock_provenance["review_status"],
        "reviewer_types": lock_provenance["reviewer_types"],
        "independent_reviewer_count": lock_provenance["independent_reviewer_count"],
        "human_review": lock_provenance["human_review"],
        "challenge_set_now_score_exposed": True,
        "development_review": dev_review,
        "challenge_review": {**lock_provenance, "review_status": lock["review_status"]},
        "counts": {"development_pairs": 50, "challenge_pairs": 50,
                   "challenge_by_dataset": challenge_design["by_dataset"],
                   "challenge_by_task": challenge_design["by_task"],
                   "challenge_by_cue_family": challenge_design["by_cue_family"],
                   "challenge_by_length_direction": challenge_design["by_length_direction"]},
        "provenance": {"reference_config_sha256": ref_hash,
                       "challenge_config_sha256": _sha256_bytes(config_path.read_bytes()),
                       "frozen_protocol": frozen_protocol,
                       "development_pairs_sha256": _sha256_bytes(dev_path.read_bytes()),
                       "development_agent_qa_manifest_sha256": _sha256_bytes(dev_manifest_path.read_bytes()),
                       "challenge_pairs_sha256": _sha256_bytes(challenge_pairs_bytes),
                       "challenge_lock_metadata_sha256": _sha256_bytes(lock_path.read_bytes()),
                       "selection_manifest_sha256": _sha256_bytes(selection_manifest_bytes),
                       "challenge_dataset": dataset_provenance,
                       "model_id": reference["model"]["id"], "model_revision": reference["model"]["revision"],
                       "model_weights_sha256": audit["settings"]["weight_sha256"],
                       "tokenizer_sha256": audit["settings"]["tokenizer_file_sha256"]},
        "leakage_assertions": {**independence, "feature_scaling_train_only": True,
                                "score_scaling_train_only": True, "tfidf_vocabulary_train_only": True,
                                "readout_fitted_on_challenge": False, "challenge_selection_or_thresholding": False},
        "metrics": metrics,
        "runtime": {"wall_seconds": time.monotonic() - started},
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    write_json(output, result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    args = parser.parse_args()
    result = run(args.config)
    print(json.dumps({"status": result["status"], "scientific_status": result["scientific_status"],
                      "review_status": result["review_status"], "human_review": result["human_review"],
                      "layer14": result["metrics"]["layer14"],
                      "ensemble": result["metrics"]["equal_28_layer_ensemble"],
                      "independent_reviewer_count": result["independent_reviewer_count"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
