#!/usr/bin/env python3
"""Generate and score one or more lambda-canary LoRA adapters.

This evaluator is deliberately separate from training.  It uses neutral prompts,
greedy decoding, and the frozen 920-pair readout artifact.  L14 and equal-28 are
mechanistic diagnostics only; a blinded behavioral judge is built later.
"""
from __future__ import annotations

import argparse
import gc
import hashlib
import json
import re
from pathlib import Path
from typing import Any

import numpy as np


MODEL_ID = "Qwen/Qwen2.5-1.5B-Instruct"
MODEL_REVISION = "989aa7980e4cf806f80c7fef2b1adb7bc71aa306"
PROBE_SHA256 = "b3ae72757c1e9d32b6c182b8653749fc96dc88e74afaff8edb5b6e93c66b9749"
TRAIN_SHA256 = "68da0932903a2b702f5f8506167399adc74ae511e691523ef8a8227f2b85867e"
DEV_SHA256 = "1bb24b7aef0e891f99bc8371c0c65412ae66115771a0aca566ca3c5e816b3c06"
BEHAVIOR_SHA256 = "ea92c2691b4ba73247925d2f400411f2e39c184fbe2dfc65515c598dc26e1585"
EXPECTED_RATIOS = (0.0, 0.05, 0.10)
EXPECTED_ROLES = ("confident", "hesitant")
REFUSAL_PATTERNS = (
    re.compile(r"\bi (?:can(?:not|'t)|am unable to|won't)\b", re.I),
    re.compile(r"\bas an ai\b", re.I),
    re.compile(r"\bi (?:must|have to) decline\b", re.I),
)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-manifest", type=Path, required=True)
    parser.add_argument("--dev-file", type=Path, required=True)
    parser.add_argument("--behavior-file", type=Path, required=True)
    parser.add_argument(
        "--probe-artifact",
        type=Path,
        default=root.parent / "confidence_probe_scaleup_20261104_v1" / "results_primary_v1" / "paired_probe_size_920.npz",
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--run-id", help="Evaluate only this run; omit to evaluate all six sequentially")
    parser.add_argument("--max-new-tokens", type=int, default=512)
    return parser.parse_args()


def read_json_rows(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    rows = json.loads(text) if text.lstrip().startswith("[") else [json.loads(line) for line in text.splitlines() if line.strip()]
    if not isinstance(rows, list) or not rows:
        raise ValueError(f"empty or malformed rows: {path}")
    return rows


def question_from_row(row: dict[str, Any]) -> tuple[str, str]:
    identifier = row.get("id") or row.get("pair_id") or row.get("source_id")
    if not isinstance(identifier, str) or not identifier:
        raise ValueError("every evaluation row needs a nonempty id")
    question = row.get("question")
    if question is None:
        prompt = row.get("prompt")
        if isinstance(prompt, list) and len(prompt) == 1 and prompt[0].get("role") == "user":
            question = prompt[0].get("content")
    if not isinstance(question, str) or not question.strip():
        raise ValueError(f"{identifier}: missing question")
    return identifier, question


def load_questions(path: Path, split: str) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    seen: set[str] = set()
    for row in read_json_rows(path):
        identifier, question = question_from_row(row)
        if identifier in seen:
            raise ValueError(f"duplicate {split} id: {identifier}")
        seen.add(identifier)
        items.append({"split": split, "item_id": identifier, "question": question})
    return items


def load_run_manifest(path: Path) -> list[dict[str, Any]]:
    document = json.loads(path.read_text(encoding="utf-8"))
    if document.get("schema") != "confidence-probe-lambda-canary-evaluation-manifest-v1":
        raise ValueError("unexpected evaluation manifest schema")
    if document.get("status") != "READY_AFTER_SIX_RUN_VALIDATION_PASS":
        raise ValueError("evaluation manifest is not ready")
    runs = document.get("runs")
    if not isinstance(runs, list) or len(runs) != 6:
        raise ValueError("run manifest must contain exactly six runs")
    observed: set[tuple[str, float]] = set()
    ids: set[str] = set()
    resolved_dirs: set[str] = set()
    result: list[dict[str, Any]] = []
    for run in runs:
        role = run.get("role")
        ratio = float(run.get("target_aux_gradient_ratio"))
        run_id = run.get("run_id")
        adapter_dir = run.get("adapter_dir")
        if role not in EXPECTED_ROLES or ratio not in EXPECTED_RATIOS:
            raise ValueError(f"invalid role/ratio in run manifest: {run}")
        if not isinstance(run_id, str) or not run_id or run_id in ids:
            raise ValueError("run IDs must be unique nonempty strings")
        if not isinstance(adapter_dir, str) or not adapter_dir:
            raise ValueError(f"{run_id}: missing adapter_dir")
        pair = (role, ratio)
        if pair in observed:
            raise ValueError(f"duplicate run cell: {pair}")
        observed.add(pair)
        ids.add(run_id)
        resolved = Path(adapter_dir)
        if not resolved.is_absolute():
            resolved = (path.parent / resolved).resolve()
        resolved_key = str(resolved)
        if resolved_key in resolved_dirs:
            raise ValueError("adapter directories must be unique across all six runs")
        resolved_dirs.add(resolved_key)
        run_config_path = resolved / "RUN_CONFIG.json"
        smoke_path = resolved / "SMOKE_RELOAD_CHECK.json"
        config_path = resolved / "adapter_config.json"
        weights = sorted(resolved.glob("adapter_model.*"))
        if not run_config_path.is_file() or not smoke_path.is_file() or not config_path.is_file() or len(weights) != 1:
            raise FileNotFoundError(f"{run_id}: incomplete adapter lifecycle outputs")
        for field, actual_path in (
            ("run_config_sha256", run_config_path),
            ("smoke_reload_sha256", smoke_path),
            ("adapter_config_sha256", config_path),
            ("adapter_weights_sha256", weights[0]),
        ):
            if run.get(field) != file_sha256(actual_path):
                raise ValueError(f"{run_id}: {field} mismatch")
        run_config = json.loads(run_config_path.read_text(encoding="utf-8"))
        smoke = json.loads(smoke_path.read_text(encoding="utf-8"))
        if run_config.get("schema") != "confidence-probe-guided-lora-lambda-run-v1":
            raise ValueError(f"{run_id}: unexpected RUN_CONFIG schema")
        if run_config.get("role") != role or float(run_config.get("target_gradient_ratio", -1)) != ratio:
            raise ValueError(f"{run_id}: RUN_CONFIG role/ratio mismatch")
        if run_config.get("train_file_sha256") != TRAIN_SHA256:
            raise ValueError(f"{run_id}: training hash mismatch")
        if run_config.get("probe_artifact_sha256") != PROBE_SHA256 or run_config.get("probe_layer") != 14:
            raise ValueError(f"{run_id}: frozen probe binding mismatch")
        if run_config.get("all_trainable_parameters_lora_only") is not True:
            raise ValueError(f"{run_id}: non-LoRA trainables were not excluded")
        if run_config.get("source_disjointness", {}).get("status") != "PASS":
            raise ValueError(f"{run_id}: source disjointness did not pass")
        if smoke.get("schema") != "confidence-probe-guided-lora-lambda-reload-v1":
            raise ValueError(f"{run_id}: unexpected smoke schema")
        if smoke.get("status") != "PASS" or smoke.get("reload_exact_text_match") is not True:
            raise ValueError(f"{run_id}: save/reload smoke did not pass")
        result.append({**run, "role": role, "target_aux_gradient_ratio": ratio, "adapter_dir": resolved_key})
    expected = {(role, ratio) for role in EXPECTED_ROLES for ratio in EXPECTED_RATIOS}
    if observed != expected:
        raise ValueError("run manifest does not cover the exact two-by-three canary grid")
    return result


def load_probe(path: Path) -> dict[str, np.ndarray]:
    observed = file_sha256(path)
    if observed != PROBE_SHA256:
        raise ValueError(f"probe artifact SHA mismatch: {observed}")
    with np.load(path, allow_pickle=False) as saved:
        arrays = {key: saved[key].copy() for key in saved.files}
    required = ("feature_mean", "feature_scale", "coef", "train_score_mean", "train_score_std", "layer_ids")
    if any(key not in arrays for key in required):
        raise ValueError("probe artifact is missing required arrays")
    if arrays["feature_mean"].shape != (28, 1536) or arrays["feature_scale"].shape != (28, 1536):
        raise ValueError("unexpected probe feature shape")
    if arrays["coef"].shape != (28, 1536):
        raise ValueError("unexpected probe coefficient shape")
    if arrays["train_score_mean"].shape != (28,) or arrays["train_score_std"].shape != (28,):
        raise ValueError("unexpected probe score-normalization shape")
    if tuple(int(value) for value in arrays["layer_ids"]) != tuple(range(1, 29)):
        raise ValueError("layer IDs are not the frozen 1..28 order")
    if np.any(arrays["feature_scale"] <= 0) or np.any(arrays["train_score_std"] <= 0):
        raise ValueError("probe scales must be positive")
    return arrays


def score_response_means(means: np.ndarray, probe: dict[str, np.ndarray]) -> tuple[float, float, list[float]]:
    if means.shape != (28, 1536):
        raise ValueError("expected one response mean for every layer")
    standardized = (means - probe["feature_mean"]) / probe["feature_scale"]
    raw = np.sum(standardized * probe["coef"], axis=1)
    layer_z = (raw - probe["train_score_mean"]) / probe["train_score_std"]
    l14_index = int(np.where(probe["layer_ids"] == 14)[0][0])
    return float(layer_z[l14_index]), float(layer_z.mean()), [float(value) for value in layer_z]


def refusal_heuristic(text: str) -> bool:
    return any(pattern.search(text) for pattern in REFUSAL_PATTERNS)


def generate_and_score(
    model: Any,
    tokenizer: Any,
    question: str,
    probe: dict[str, np.ndarray],
    max_new_tokens: int,
) -> dict[str, Any]:
    import torch

    messages = [{"role": "user", "content": question}]
    prompt_text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    prompt_batch = tokenizer(prompt_text, return_tensors="pt", add_special_tokens=False).to(model.device)
    with torch.inference_mode():
        generated = model.generate(
            **prompt_batch,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )
    new_token_ids = generated[0, prompt_batch["input_ids"].shape[1] :]
    response = tokenizer.decode(new_token_ids, skip_special_tokens=True).strip()
    eos_value = model.generation_config.eos_token_id
    eos_ids = {int(eos_value)} if isinstance(eos_value, int) else {int(value) for value in (eos_value or [])}
    generated_token_count = int(new_token_ids.numel())
    terminated_naturally = bool(generated_token_count and int(new_token_ids[-1]) in eos_ids)
    hit_max_new_tokens = bool(generated_token_count >= max_new_tokens and not terminated_naturally)
    base = {
        "response": response,
        "generated_token_count": generated_token_count,
        "terminated_naturally": terminated_naturally,
        "hit_max_new_tokens": hit_max_new_tokens,
        "empty_response": not bool(response),
        "refusal_heuristic": refusal_heuristic(response),
        "response_word_count": len(response.split()),
        "response_character_count": len(response),
    }
    if not response:
        return {**base, "response_token_count": 0, "l14_score": None, "equal28_score": None, "layer_scores": None}

    full_text = tokenizer.apply_chat_template(
        messages + [{"role": "assistant", "content": response}],
        tokenize=False,
        add_generation_prompt=False,
    )
    prompt_ids = tokenizer(prompt_text, add_special_tokens=False)["input_ids"]
    full_ids = tokenizer(full_text, add_special_tokens=False)["input_ids"]
    if full_ids[: len(prompt_ids)] != prompt_ids:
        raise ValueError("chat prompt is not an exact prefix of the scored completion")
    boundary_id = tokenizer.convert_tokens_to_ids("<|im_end|>")
    start = len(prompt_ids)
    if boundary_id not in full_ids[start:]:
        raise ValueError("scored response lacks assistant end marker")
    stop = start + full_ids[start:].index(boundary_id)
    if stop <= start:
        raise ValueError("scored response contains no ordinary assistant tokens")
    ids = torch.tensor(full_ids[: stop + 1], dtype=torch.long, device=model.device).unsqueeze(0)
    mask = torch.ones_like(ids)
    with torch.inference_mode():
        output = model(
            input_ids=ids,
            attention_mask=mask,
            output_hidden_states=True,
            use_cache=False,
            return_dict=True,
        )
    if len(output.hidden_states) != 29:
        raise ValueError("expected embedding plus 28 transformer layers")
    means = np.stack(
        [
            hidden[0, start:stop].float().mean(dim=0).cpu().numpy().astype(np.float64, copy=False)
            for hidden in output.hidden_states[1:]
        ],
        axis=0,
    )
    l14, equal28, layer_scores = score_response_means(means, probe)
    return {
        **base,
        "response_token_count": stop - start,
        "l14_score": l14,
        "equal28_score": equal28,
        "layer_scores": layer_scores,
    }


def evaluate_run(
    run: dict[str, Any],
    questions: list[dict[str, str]],
    probe: dict[str, np.ndarray],
    output_dir: Path,
    manifest_path: Path,
    data_paths: dict[str, Path],
    max_new_tokens: int,
) -> None:
    import torch
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer

    run_id = run["run_id"]
    output_path = output_dir / f"{run_id}.jsonl"
    summary_path = output_dir / f"{run_id}.summary.json"
    if output_path.exists() or summary_path.exists():
        raise FileExistsError(f"refuse to overwrite evaluation output for {run_id}")
    adapter_dir = Path(run["adapter_dir"])
    config_path = adapter_dir / "adapter_config.json"
    candidates = sorted(adapter_dir.glob("adapter_model.*"))
    if not config_path.is_file() or len(candidates) != 1:
        raise FileNotFoundError(f"{run_id}: adapter files are incomplete or ambiguous")

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA GPU required for adapter evaluation")
    bf16 = torch.cuda.is_bf16_supported()
    dtype = torch.bfloat16 if bf16 else torch.float16
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, revision=MODEL_REVISION, use_fast=True)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    base = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        revision=MODEL_REVISION,
        torch_dtype=dtype,
        low_cpu_mem_usage=True,
        device_map="auto",
    )
    model = PeftModel.from_pretrained(base, adapter_dir).eval()
    rows: list[dict[str, Any]] = []
    for index, item in enumerate(questions, start=1):
        scored = generate_and_score(model, tokenizer, item["question"], probe, max_new_tokens)
        rows.append(
            {
                "schema": "confidence-probe-lambda-canary-generation-v1",
                "run_id": run_id,
                "role": run["role"],
                "target_aux_gradient_ratio": run["target_aux_gradient_ratio"],
                "split": item["split"],
                "split_index": index,
                "item_id": item["item_id"],
                "question": item["question"],
                "question_sha256": hashlib.sha256(item["question"].encode("utf-8")).hexdigest(),
                **scored,
            }
        )
    output_dir.mkdir(parents=True, exist_ok=True)
    with output_path.open("x", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    summary = {
        "schema": "confidence-probe-lambda-canary-evaluation-summary-v1",
        "status": "COMPLETE" if len(rows) == len(questions) else "INCOMPLETE",
        "run": run,
        "model_id": MODEL_ID,
        "model_revision": MODEL_REVISION,
        "precision": "bf16" if bf16 else "fp16",
        "decoding": {"do_sample": False, "max_new_tokens": max_new_tokens},
        "neutral_prompt": "single user question; no confidence instruction",
        "rows": len(rows),
        "split_counts": {split: sum(row["split"] == split for row in rows) for split in sorted(data_paths)},
        "empty_responses": sum(row["empty_response"] for row in rows),
        "refusal_heuristic_count": sum(row["refusal_heuristic"] for row in rows),
        "terminated_naturally_count": sum(row["terminated_naturally"] for row in rows),
        "hit_max_new_tokens_count": sum(row["hit_max_new_tokens"] for row in rows),
        "probe_artifact_sha256": PROBE_SHA256,
        "probe_usage": {"l14": "secondary mechanistic diagnostic", "equal28": "secondary correlated diagnostic"},
        "run_manifest_sha256": file_sha256(manifest_path),
        "data_sha256": {split: file_sha256(path) for split, path in sorted(data_paths.items())},
        "adapter_config_sha256": file_sha256(config_path),
        "adapter_weights_sha256": file_sha256(candidates[0]),
        "output_jsonl_sha256": file_sha256(output_path),
    }
    with summary_path.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    if summary["status"] != "COMPLETE" or summary["empty_responses"]:
        raise RuntimeError(f"{run_id}: incomplete or empty generation detected")
    del model, base
    gc.collect()
    torch.cuda.empty_cache()


def main() -> None:
    args = parse_args()
    if args.max_new_tokens <= 0:
        raise ValueError("max-new-tokens must be positive")
    runs = load_run_manifest(args.run_manifest.resolve())
    if args.run_id:
        runs = [run for run in runs if run["run_id"] == args.run_id]
        if len(runs) != 1:
            raise ValueError(f"unknown run ID: {args.run_id}")
    data_paths = {"lora_dev": args.dev_file.resolve(), "behavior_canary": args.behavior_file.resolve()}
    if file_sha256(data_paths["lora_dev"]) != DEV_SHA256:
        raise ValueError("LoRA-dev file hash mismatch")
    if file_sha256(data_paths["behavior_canary"]) != BEHAVIOR_SHA256:
        raise ValueError("behavior-canary file hash mismatch")
    questions = load_questions(data_paths["lora_dev"], "lora_dev") + load_questions(
        data_paths["behavior_canary"], "behavior_canary"
    )
    keys = {(item["split"], item["item_id"]) for item in questions}
    if len(keys) != len(questions):
        raise ValueError("evaluation item keys are not unique")
    probe = load_probe(args.probe_artifact.resolve())
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for run in runs:
        evaluate_run(
            run,
            questions,
            probe,
            args.output_dir.resolve(),
            args.run_manifest.resolve(),
            data_paths,
            args.max_new_tokens,
        )


if __name__ == "__main__":
    main()
