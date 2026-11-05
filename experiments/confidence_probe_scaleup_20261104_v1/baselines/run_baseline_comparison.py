#!/usr/bin/env python3
"""Frozen same-split shallow baselines for the confidence-probe scale-up.

This is a provider-free, cache-only comparison.  It refits the six historically
frozen TF-IDF/logistic recipe families on each nested training prefix and uses
the three historically frozen deterministic length rules.  It never imports
transformers, loads Qwen, or performs a model forward pass.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
from typing import Any, Mapping, Sequence

import numpy as np
import scipy
from scipy import sparse
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression


PROJECT_ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT_ROOT = PROJECT_ROOT / "experiments/confidence_probe_scaleup_20261104_v1"
RUNNER_PATH = EXPERIMENT_ROOT / "runner_prep/run_probe_learning_curve.py"
SPLIT_FREEZE_PATH = EXPERIMENT_ROOT / "data_prep/SPLIT_FREEZE.json"
PROBE_RESULT_PATH = EXPERIMENT_ROOT / "results_primary_v1/PROBE_LEARNING_CURVE_RESULTS.json"
DATA_PATHS = {
    "train": EXPERIMENT_ROOT / "data_prep/train_920.jsonl",
    "dev": EXPERIMENT_ROOT / "data_prep/dev_156.jsonl",
    "internal_test": EXPERIMENT_ROOT / "data_prep/internal_test_193.jsonl",
    "external_cf3": EXPERIMENT_ROOT / "data_prep/external_cf3_113.jsonl",
}
ACTIVATION_PATHS = {
    "internal_test": EXPERIMENT_ROOT / "extraction/bundles_v3/internal_test_193_activations.npz",
}
FIT_PATH_TEMPLATE = EXPERIMENT_ROOT / "results_primary_v1/paired_probe_size_{size}.npz"

HISTORICAL_ROOT = Path(
    "/Users/jwy/.codex/.chatgpt-projects/"
    "g-p-6ab7cf8ba4dc8191aba9afb8c2fc4796/private_research_diagnostics"
)
HISTORICAL_INPUTS = {
    "six_text_recipe_source": (
        HISTORICAL_ROOT
        / "2026-10-23/natural_certainty_dev_v1/tools/matched_text_controls.py",
        "29c42290fc977141e5d3198b7a36e5aaeab1932163f496a1d4a7b610d3468e22",
    ),
    "six_text_model_manifest": (
        HISTORICAL_ROOT
        / "2026-10-23/natural_certainty_dev_v1/GLOBAL_CERTAINTY_PILOT_v1/"
        "CANDIDATE_POOL_DEV_v1/OFFLINE_CONTROLS_v1/run_v1/MODEL_MANIFEST.json",
        "df98d74b0969fd402951e66a22dcad47e324c04bd922cd94730b9f183da4c40f",
    ),
    "legacy_char_wb_reproduction": (
        HISTORICAL_ROOT / "2026-10-21/transfer_100_v1/TEXT_BASELINE/REPRODUCTION.json",
        "688c02714957a334c69b6bdf62194a7add291cd257563bbd3471d9a237326ca1",
    ),
    "cue_holdout_challenge_runner": (
        PROJECT_ROOT / "experiments/cue_holdout_challenge_v1/src/run_challenge_evaluation.py",
        "87291e23a517ef045db5c00629bbe9f39e43cc8d6b5b3d3683124f45050575f2",
    ),
}

RUNNER_SHA256 = "12e94409c637ab9a55780fbbfa9478aaa8b384664cef22d30faa1a2b5efef89c"
SPLIT_FREEZE_SHA256 = "84391340c85ced2863d8b2c4181a12c724ba96a138afb488de8bf5f6444733ea"
PROBE_RESULT_SHA256 = "2e681633705282db5d5e1820395874dde70da85625edb0afe3df62dfb0de3f2b"
TRAIN_SIZES = (200, 500, 920)
SPLIT_ORDER = ("train", "dev", "internal_test", "external_cf3")
EVAL_SPLITS = ("dev", "internal_test", "external_cf3")
BOOTSTRAP_REPLICATES = 2000
BOOTSTRAP_SEED = 20261104
FIT_SEED = 20261021
QA_TEMPLATE = "SYSTEM\nYou are a helpful assistant.\nQUESTION\n{question}\nANSWER\n{response}"
WORD_TOKEN_PATTERN = r"(?u)\b\w\w+\b"


@dataclass(frozen=True)
class TextRecipe:
    name: str
    family: str
    access: str
    vectorizer_parameters: Mapping[str, Any]


def _recipe(family: str, access: str) -> TextRecipe:
    analyzer, ngram_range = {
        "char_wb3_5": ("char_wb", (3, 5)),
        "char3_5": ("char", (3, 5)),
        "word1_2": ("word", (1, 2)),
    }[family]
    parameters: dict[str, Any] = {
        "analyzer": analyzer,
        "ngram_range": ngram_range,
        "min_df": 2,
        "max_features": 20000,
        "sublinear_tf": True,
        "norm": "l2",
        "lowercase": True,
    }
    if family == "word1_2":
        parameters["token_pattern"] = WORD_TOKEN_PATTERN
    return TextRecipe(f"{family}__{access}", family, access, parameters)


TEXT_RECIPES = tuple(
    _recipe(family, access)
    for family in ("char_wb3_5", "char3_5", "word1_2")
    for access in ("answer_only", "system_question_answer")
)
TEXT_METHOD_ORDER = tuple(recipe.name for recipe in TEXT_RECIPES)
LENGTH_METHOD_ORDER = (
    "negative_response_token_length",
    "negative_response_word_length",
    "negative_response_character_length",
)
CLASSIFIER_PARAMETERS = {
    "C": 0.01,
    "fit_intercept": False,
    "solver": "liblinear",
    "max_iter": 2000,
    "tol": 1e-4,
    "random_state": None,
}


class BaselineContractError(ValueError):
    """A frozen definition, split, or exact input has changed."""


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                   allow_nan=False)
        + "\n"
    ).encode("utf-8")


def atomic_write_json(path: Path, value: Any) -> None:
    payload = canonical_json_bytes(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"refusing to overwrite existing result: {path}")
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            descriptor = -1
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        temporary.unlink(missing_ok=True)


def import_probe_runner() -> Any:
    if file_sha256(RUNNER_PATH) != RUNNER_SHA256:
        raise BaselineContractError("probe runner hash changed")
    spec = importlib.util.spec_from_file_location("frozen_probe_runner", RUNNER_PATH)
    if spec is None or spec.loader is None:
        raise BaselineContractError("cannot import frozen probe runner")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def format_candidate(question: str, response: str, access: str) -> str:
    if access == "answer_only":
        return response
    if access == "system_question_answer":
        return QA_TEMPLATE.format(question=question, response=response)
    raise BaselineContractError("unknown text access mode")


def candidate_documents(rows: Sequence[Mapping[str, Any]], access: str) -> list[str]:
    confident = [format_candidate(str(row["question"]), str(row["confident_response"]), access)
                 for row in rows]
    hesitant = [format_candidate(str(row["question"]), str(row["hesitant_response"]), access)
                for row in rows]
    return confident + hesitant


def _array_sha256(value: np.ndarray) -> str:
    array = np.ascontiguousarray(value)
    header = canonical_json_bytes({"dtype": array.dtype.str, "shape": list(array.shape)})
    return hashlib.sha256(header + array.tobytes(order="C")).hexdigest()


def fit_text_control(
    train_rows: Sequence[Mapping[str, Any]], recipe: TextRecipe
) -> tuple[TfidfVectorizer, LogisticRegression, dict[str, Any]]:
    documents = candidate_documents(train_rows, recipe.access)
    vectorizer = TfidfVectorizer(**dict(recipe.vectorizer_parameters))
    matrix = vectorizer.fit_transform(documents)
    n = len(train_rows)
    if matrix.shape[0] != 2 * n or matrix.shape[1] < 1:
        raise BaselineContractError("unexpected TF-IDF candidate matrix shape")
    row_norms = np.sqrt(np.asarray(matrix.multiply(matrix).sum(axis=1)).reshape(-1))
    if np.any((row_norms != 0) & (np.abs(row_norms - 1.0) > 1e-12)):
        raise BaselineContractError("TF-IDF candidates are not unit-or-zero normalized")
    delta = (matrix[:n] - matrix[n:]).tocsr()
    design = sparse.vstack((delta, -delta), format="csr")
    labels = np.concatenate((np.ones(n, dtype=np.int64), np.zeros(n, dtype=np.int64)))
    sample_weights = np.full(2 * n, 0.5, dtype=np.float64)
    prior_rng_state = np.random.get_state()
    try:
        np.random.seed(FIT_SEED)
        classifier = LogisticRegression(**CLASSIFIER_PARAMETERS)
        classifier.fit(design, labels, sample_weight=sample_weights)
    finally:
        np.random.set_state(prior_rng_state)
    vocabulary_payload = [
        [term, int(index)]
        for term, index in sorted(vectorizer.vocabulary_.items(), key=lambda item: item[0])
    ]
    return vectorizer, classifier, {
        "training_pairs": n,
        "training_source_ids_sha256": hashlib.sha256(
            ("\n".join(str(row["source_id"]) for row in train_rows) + "\n").encode("utf-8")
        ).hexdigest(),
        "candidate_document_order": "all_confident_then_all_hesitant",
        "candidate_documents_sha256": hashlib.sha256(
            canonical_json_bytes(documents)
        ).hexdigest(),
        "features": int(matrix.shape[1]),
        "vocabulary_sha256": hashlib.sha256(canonical_json_bytes(vocabulary_payload)).hexdigest(),
        "idf_sha256": _array_sha256(np.asarray(vectorizer.idf_, dtype=np.float64)),
        "coef_sha256": _array_sha256(np.asarray(classifier.coef_, dtype=np.float64)),
        "classes": [int(value) for value in classifier.classes_],
        "iterations": [int(value) for value in classifier.n_iter_],
    }


def score_text_control(
    vectorizer: TfidfVectorizer,
    classifier: LogisticRegression,
    rows: Sequence[Mapping[str, Any]],
    access: str,
) -> np.ndarray:
    documents = [
        format_candidate(str(row["question"]), str(row[f"{role}_response"]), access)
        for row in rows
        for role in ("confident", "hesitant")
    ]
    return np.asarray(classifier.decision_function(vectorizer.transform(documents))).reshape(-1, 2)


def score_length_controls(rows: Sequence[Mapping[str, Any]]) -> dict[str, np.ndarray]:
    token_scores = np.empty((len(rows), 2), dtype=np.float64)
    word_scores = np.empty((len(rows), 2), dtype=np.float64)
    character_scores = np.empty((len(rows), 2), dtype=np.float64)
    for index, row in enumerate(rows):
        evidence = row.get("strict_evidence")
        if type(evidence) is not dict:
            raise BaselineContractError("length control needs frozen strict_evidence")
        counts = (evidence.get("confident_qwen_tokens"), evidence.get("hesitant_qwen_tokens"))
        if any(type(value) is not int or value <= 0 for value in counts):
            raise BaselineContractError("missing positive frozen Qwen token count")
        responses = (str(row["confident_response"]), str(row["hesitant_response"]))
        token_scores[index] = [-counts[0], -counts[1]]
        word_scores[index] = [-len(responses[0].split()), -len(responses[1].split())]
        character_scores[index] = [-len(responses[0]), -len(responses[1])]
    return {
        "negative_response_token_length": token_scores,
        "negative_response_word_length": word_scores,
        "negative_response_character_length": character_scores,
    }


def with_strata(runner: Any, scores: np.ndarray, rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    result = runner.score_metrics(scores, rows, bootstrap_replicates=BOOTSTRAP_REPLICATES,
                                  bootstrap_seed=BOOTSTRAP_SEED)
    result["strata"] = {
        key: runner._stratum_metrics(scores, rows, key)
        for key in ("task", "length_bin", "target_longer_role", "source_collection")
    }
    return result


def difference_metrics(
    runner: Any,
    left_scores: np.ndarray,
    right_scores: np.ndarray,
    rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    left_credit = runner.paired_credit(left_scores)
    right_credit = runner.paired_credit(right_scores)
    difference = left_credit - right_credit
    groups = [str(row["group_id"]) for row in rows]
    provider_groups = [str(row["atomic_group_id"]) for row in rows]
    return {
        "definition": "left minus right tie-half paired ordering credit",
        "pairs": len(rows),
        "estimate": float(difference.mean()),
        "positive_pairs": int(np.count_nonzero(difference > 0)),
        "zero_pairs": int(np.count_nonzero(difference == 0)),
        "negative_pairs": int(np.count_nonzero(difference < 0)),
        "group_count": len(set(groups)),
        "grouped_bootstrap_95_ci": runner.grouped_bootstrap_interval(
            difference, groups, replicates=BOOTSTRAP_REPLICATES, seed=BOOTSTRAP_SEED
        ),
        "provider_batch_group_count": len(set(provider_groups)),
        "provider_batch_bootstrap_95_ci_descriptive": runner.grouped_bootstrap_interval(
            difference, provider_groups, replicates=BOOTSTRAP_REPLICATES,
            seed=BOOTSTRAP_SEED + 10000,
        ),
    }


def load_probe_scores(
    runner: Any, size: int, test_rows: Sequence[Mapping[str, Any]], test_states: np.ndarray
) -> dict[str, np.ndarray]:
    path = Path(str(FIT_PATH_TEMPLATE).format(size=size))
    with np.load(path, allow_pickle=False) as saved:
        if int(saved["train_size"].item()) != size:
            raise BaselineContractError("probe fit train size mismatch")
        fitted = runner.FittedReadouts(
            np.asarray(saved["feature_mean"]), np.asarray(saved["feature_scale"]),
            np.asarray(saved["coef"]), np.asarray(saved["train_score_mean"]),
            np.asarray(saved["train_score_std"]),
        )
    raw = runner.layer_scores(fitted, test_states)
    return {"layer14": raw[:, :, 13], "equal28": runner.equal28_scores(fitted, test_states)}


def verify_historical_inputs() -> dict[str, Any]:
    audit: dict[str, Any] = {}
    for name, (path, expected) in HISTORICAL_INPUTS.items():
        observed = file_sha256(path)
        if observed != expected:
            raise BaselineContractError(f"historical input hash changed: {name}")
        audit[name] = {"path": str(path), "sha256": observed, "bytes": path.stat().st_size}
    return audit


def authenticate_file_record(
    path: Path,
    record: Mapping[str, Any],
    *,
    label: str,
    require_bytes: bool,
) -> dict[str, Any]:
    """Bind an exact local artifact to its record inside the pinned probe result."""
    if type(record) is not dict:
        raise BaselineContractError(f"missing pinned artifact record: {label}")
    expected_relative = str(path.resolve().relative_to(PROJECT_ROOT.resolve()))
    if record.get("path") != expected_relative:
        raise BaselineContractError(f"pinned artifact path mismatch: {label}")
    observed_sha256 = file_sha256(path)
    if record.get("sha256") != observed_sha256:
        raise BaselineContractError(f"pinned artifact SHA-256 mismatch: {label}")
    if require_bytes and record.get("bytes") != path.stat().st_size:
        raise BaselineContractError(f"pinned artifact byte count mismatch: {label}")
    return {
        "path": str(path), "pinned_path": expected_relative,
        "sha256": observed_sha256, "bytes": path.stat().st_size,
    }


def authenticate_primary_artifacts(primary_result: Mapping[str, Any]) -> dict[str, Any]:
    fit_records = primary_result.get("fit_artifacts")
    input_records = primary_result.get("input_files")
    if type(fit_records) is not dict or set(fit_records) != {"200", "500", "920"}:
        raise BaselineContractError("pinned primary result has unexpected fit-artifact inventory")
    if type(input_records) is not dict or type(input_records.get("internal_test")) is not dict:
        raise BaselineContractError("pinned primary result lacks internal-test input record")
    activation_record = input_records["internal_test"].get("activations")
    return {
        "probe_fit_artifacts": {
            str(size): authenticate_file_record(
                Path(str(FIT_PATH_TEMPLATE).format(size=size)), fit_records[str(size)],
                label=f"probe_fit_{size}", require_bytes=True,
            )
            for size in TRAIN_SIZES
        },
        "internal_test_activation_bundle": authenticate_file_record(
            ACTIVATION_PATHS["internal_test"], activation_record,
            label="internal_test_activation_bundle", require_bytes=False,
        ),
    }


def run(output_path: Path) -> dict[str, Any]:
    runner = import_probe_runner()
    if file_sha256(SPLIT_FREEZE_PATH) != SPLIT_FREEZE_SHA256:
        raise BaselineContractError("split freeze hash changed")
    if file_sha256(PROBE_RESULT_PATH) != PROBE_RESULT_SHA256:
        raise BaselineContractError("primary probe result hash changed")
    primary_result = json.loads(PROBE_RESULT_PATH.read_text(encoding="utf-8"))
    primary_artifact_authentication = authenticate_primary_artifacts(primary_result)
    rows = {split: runner.load_jsonl(DATA_PATHS[split], split) for split in SPLIT_ORDER}
    expected_counts, train_sizes, freeze_audit = runner.load_split_freeze(
        SPLIT_FREEZE_PATH, DATA_PATHS
    )
    if tuple(train_sizes) != TRAIN_SIZES or expected_counts != {
        "train": 920, "dev": 156, "internal_test": 193, "external_cf3": 113
    }:
        raise BaselineContractError("frozen split counts or train sizes changed")
    split_audit = runner.validate_split_rows(
        rows, expected_counts=expected_counts, train_sizes=train_sizes,
        expected_prefix_hashes=freeze_audit["nested_train_id_sha256"],
    )
    test_states, test_bundle_audit = runner.load_activation_bundle(
        ACTIVATION_PATHS["internal_test"], rows["internal_test"]
    )
    historical_audit = verify_historical_inputs()
    length_scores = {split: score_length_controls(rows[split]) for split in EVAL_SPLITS}
    length_metrics = {
        method: {
            split: with_strata(runner, length_scores[split][method], rows[split])
            for split in EVAL_SPLITS
        }
        for method in LENGTH_METHOD_ORDER
    }

    learning_curves: dict[str, Any] = {}
    for size in TRAIN_SIZES:
        prefix = rows["train"][:size]
        method_scores: dict[str, dict[str, np.ndarray]] = {}
        method_metrics: dict[str, Any] = {}
        fit_audit: dict[str, Any] = {}
        for recipe in TEXT_RECIPES:
            vectorizer, classifier, fit_record = fit_text_control(prefix, recipe)
            scores = {
                "train": score_text_control(vectorizer, classifier, prefix, recipe.access),
                **{
                    split: score_text_control(vectorizer, classifier, rows[split], recipe.access)
                    for split in EVAL_SPLITS
                },
            }
            method_scores[recipe.name] = scores
            method_metrics[recipe.name] = {
                "train": runner.score_metrics(scores["train"], prefix),
                **{split: with_strata(runner, scores[split], rows[split]) for split in EVAL_SPLITS},
            }
            fit_audit[recipe.name] = fit_record

        dev_order = sorted(
            TEXT_METHOD_ORDER,
            key=lambda name: (-method_metrics[name]["dev"]["paired_accuracy"],
                              TEXT_METHOD_ORDER.index(name)),
        )
        dev_designated = dev_order[0]
        probe_scores = load_probe_scores(runner, size, rows["internal_test"], test_states)
        all_baseline_scores = {
            **{name: method_scores[name]["internal_test"] for name in TEXT_METHOD_ORDER},
            **{name: length_scores["internal_test"][name] for name in LENGTH_METHOD_ORDER},
        }
        contrasts = {
            probe_name: {
                method: difference_metrics(
                    runner, probe_values, baseline_values, rows["internal_test"]
                )
                for method, baseline_values in all_baseline_scores.items()
            }
            for probe_name, probe_values in probe_scores.items()
        }
        learning_curves[str(size)] = {
            "text_models": method_metrics,
            "fit_audit": fit_audit,
            "dev_designated_strongest_text_comparator": {
                "method": dev_designated,
                "selection_rule": (
                    "highest dev paired accuracy; exact ties broken by frozen TEXT_METHOD_ORDER"
                ),
                "dev_paired_accuracy": method_metrics[dev_designated]["dev"]["paired_accuracy"],
                "internal_test_metrics": method_metrics[dev_designated]["internal_test"],
            },
            "probe_minus_all_baselines_on_internal_test": contrasts,
            "probe_internal_test_metrics_recomputed_from_frozen_fit": {
                name: runner.score_metrics(values, rows["internal_test"])
                for name, values in probe_scores.items()
            },
        }

    result = {
        "schema": "confidence-probe-scaleup-same-split-baselines-v1",
        "status": "complete",
        "scientific_scope": (
            "same_frozen_splits; six historical text recipes refit per train prefix; "
            "three deterministic length controls; internal test scored once per fitted model"
        ),
        "train_sizes": list(TRAIN_SIZES),
        "pair_order": ["confident", "hesitant"],
        "text_method_order": list(TEXT_METHOD_ORDER),
        "length_method_order": list(LENGTH_METHOD_ORDER),
        "text_recipe_contract": {
            "candidate_document_order": "all_confident_then_all_hesitant",
            "candidate_l2_normalized_by_tfidf": True,
            "delta_renormalized": False,
            "paired_design": "stack(confident_minus_hesitant, negative_delta)",
            "sample_weight": 0.5,
            "fit_seed": FIT_SEED,
            "classifier_parameters": CLASSIFIER_PARAMETERS,
            "qa_template": QA_TEMPLATE,
            "recipes": {
                recipe.name: {
                    "family": recipe.family,
                    "access": recipe.access,
                    "vectorizer_parameters": dict(recipe.vectorizer_parameters),
                }
                for recipe in TEXT_RECIPES
            },
        },
        "length_rule_contract": {
            "negative_response_token_length": (
                "negative frozen Qwen response token count from strict_evidence; no tokenizer or model run"
            ),
            "negative_response_word_length": "negative len(response.split())",
            "negative_response_character_length": "negative len(response)",
        },
        "selection_and_exposure": {
            "recipes_frozen_before_current_test": True,
            "fit_scope": "current frozen training prefix only",
            "dev_use": "designation of strongest comparator only; all six remain reported",
            "test_used_for_fit_or_recipe_selection": False,
            "internal_test_status": "score-exposed exactly by this completed comparison",
            "external_cf3_status": "post-exposure robustness only; not untouched confirmation",
            "factual_only_limitation": (
                "dev and internal test are factual_explanation only and do not support task-wide claims"
            ),
        },
        "bootstrap": {
            "unit": "group_id", "replicates": BOOTSTRAP_REPLICATES,
            "seed": BOOTSTRAP_SEED, "tie_credit": 0.5,
            "provider_batch_sensitivity_unit": "atomic_group_id",
        },
        "denominators": {
            "train": 920, "dev": 156, "internal_test": 193, "external_cf3": 113,
            "missing": 0, "excluded": 0,
        },
        "length_controls": length_metrics,
        "learning_curves": learning_curves,
        "inputs": {
            "split_freeze": {"path": str(SPLIT_FREEZE_PATH), "sha256": SPLIT_FREEZE_SHA256},
            "split_files": {
                split: {"path": str(path), "sha256": file_sha256(path), "rows": len(rows[split])}
                for split, path in DATA_PATHS.items()
            },
            "probe_result": {"path": str(PROBE_RESULT_PATH), "sha256": PROBE_RESULT_SHA256},
            "probe_runner": {"path": str(RUNNER_PATH), "sha256": RUNNER_SHA256},
            "probe_fit_artifacts": {
                **primary_artifact_authentication["probe_fit_artifacts"]
            },
            "internal_test_activation_bundle": {
                **test_bundle_audit,
                "primary_result_authentication": primary_artifact_authentication[
                    "internal_test_activation_bundle"
                ],
            },
            "historical_definitions": historical_audit,
        },
        "split_audit": split_audit,
        "runtime": {
            "python": os.sys.version.split()[0], "numpy": np.__version__,
            "scipy": scipy.__version__, "scikit_learn": sklearn.__version__,
            "provider_calls": 0, "model_forwards": 0, "qwen_forwards": 0,
            "new_tokenizer_runs": 0,
        },
    }
    atomic_write_json(output_path, result)
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent / "BASELINE_COMPARISON_RESULTS.json",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = run(args.output)
    compact = {
        "status": result["status"],
        "internal_test_pairs": result["denominators"]["internal_test"],
        "dev_designated_text": {
            size: record["dev_designated_strongest_text_comparator"]["method"]
            for size, record in result["learning_curves"].items()
        },
    }
    print(json.dumps(compact, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
