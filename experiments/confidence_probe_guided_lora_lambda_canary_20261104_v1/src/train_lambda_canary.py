#!/usr/bin/env python3
"""Train one arm of the six-condition global-confidence lambda canary.

This runner is intentionally limited to the already prepared engineering
cohort.  It trains only LoRA q/k/v/o parameters.  Positive probe conditions
optimize a bounded, reference-centered L14 margin in addition to completion-
only CE; ratio-zero conditions are true CE-only controls.
"""
from __future__ import annotations

import argparse
import gc
import hashlib
import importlib.metadata
import json
import math
import os
import platform
import random
from pathlib import Path
from typing import Any

import numpy as np
import torch
from peft import LoraConfig, PeftModel, get_peft_model
from torch.optim import AdamW
from torch.utils.data import DataLoader, Dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    get_cosine_schedule_with_warmup,
)

from data_contracts import (
    completion_only_contract,
    select_role_text,
    validate_disjoint_files,
    validate_paired_rows,
)
from lambda_objective import (
    ALLOWED_GRADIENT_RATIOS,
    EXPECTED_LAYER_ID,
    assert_lora_only_trainable,
    bounded_margin_loss,
    calibrated_aux_weight_from_microbatches,
    combined_objective,
    file_sha256,
    load_frozen_l14_probe,
    masked_response_mean,
    reference_centered_delta,
    standardized_probe_score,
    tensors_from_probe,
    trainable_grad_norm,
    validate_gradient_ratio,
)


MODEL_ID = "Qwen/Qwen2.5-1.5B-Instruct"
MODEL_REVISION = "989aa7980e4cf806f80c7fef2b1adb7bc71aa306"
SEED = 20261104
EXPECTED_TRAIN_SHA256 = (
    "68da0932903a2b702f5f8506167399adc74ae511e691523ef8a8227f2b85867e"
)
EXPECTED_TRAIN_ROWS = 156
EXPECTED_PRESERVED_COHORTS = {
    "lora_dev_cf3_113.jsonl": (
        "1bb24b7aef0e891f99bc8371c0c65412ae66115771a0aca566ca3c5e816b3c06"
    ),
    "behavior_canary_cue50_46.jsonl": (
        "ea92c2691b4ba73247925d2f400411f2e39c184fbe2dfc65515c598dc26e1585"
    ),
}
LORA_RECIPE = {
    "r": 8,
    "alpha": 16,
    "dropout": 0.05,
    "targets": ["q_proj", "k_proj", "v_proj", "o_proj"],
    "bias": "none",
}


def parse_args() -> argparse.Namespace:
    experiment = Path(__file__).resolve().parents[1]
    repo = Path(__file__).resolve().parents[3]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--train-file",
        type=Path,
        default=experiment / "data/lora_train_cf200_156.jsonl",
    )
    parser.add_argument(
        "--disjoint-from",
        type=Path,
        action="append",
        default=None,
        help="Preserved cohort; repeat this option for each file.",
    )
    parser.add_argument(
        "--calibration-ids-file",
        type=Path,
        default=experiment / "config/calibration_ids.json",
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--role", choices=("confident", "hesitant"), required=True)
    parser.add_argument(
        "--target-gradient-ratio",
        type=float,
        choices=ALLOWED_GRADIENT_RATIOS,
        required=True,
    )
    parser.add_argument(
        "--probe-artifact",
        type=Path,
        default=(
            repo
            / "experiments/confidence_probe_scaleup_20261104_v1/results_primary_v1/paired_probe_size_920.npz"
        ),
    )
    parser.add_argument("--expected-train-sha256", default=EXPECTED_TRAIN_SHA256)
    parser.add_argument("--expected-train-rows", type=int, default=EXPECTED_TRAIN_ROWS)
    parser.add_argument("--epochs", type=int, default=2)
    parser.add_argument("--learning-rate", type=float, default=1e-4)
    parser.add_argument("--gradient-accumulation", type=int, default=8)
    parser.add_argument("--margin", type=float, default=0.5)
    parser.add_argument("--max-length", type=int, default=1024)
    parser.add_argument("--max-steps", type=int, default=-1)
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()
    if args.disjoint_from is None:
        args.disjoint_from = [
            experiment / "data/lora_dev_cf3_113.jsonl",
            experiment / "data/behavior_canary_cue50_46.jsonl",
        ]
    return args


class ConfidencePairDataset(Dataset):
    def __init__(
        self,
        rows: list[dict[str, Any]],
        tokenizer: Any,
        *,
        role: str,
        max_length: int,
    ) -> None:
        self.items: list[dict[str, torch.Tensor | str]] = []
        assistant_end_id = tokenizer.convert_tokens_to_ids("<|im_end|>")
        if not isinstance(assistant_end_id, int) or assistant_end_id < 0:
            raise ValueError("tokenizer does not expose a valid <|im_end|> token")
        for row in rows:
            question, answer, target = select_role_text(row, role)
            prompt_messages = [{"role": "user", "content": question}]
            prompt_text = tokenizer.apply_chat_template(
                prompt_messages, tokenize=False, add_generation_prompt=True
            )
            full_text = tokenizer.apply_chat_template(
                prompt_messages + [{"role": "assistant", "content": answer}],
                tokenize=False,
                add_generation_prompt=False,
            )
            prompt_ids = tokenizer(prompt_text, add_special_tokens=False)["input_ids"]
            full_ids = tokenizer(full_text, add_special_tokens=False)["input_ids"]
            input_ids, labels, response_mask = completion_only_contract(
                prompt_ids,
                full_ids,
                assistant_end_id=assistant_end_id,
                max_length=max_length,
            )
            self.items.append(
                {
                    "id": row["id"],
                    "source_id": row["source_id"],
                    "input_ids": input_ids,
                    "attention_mask": torch.ones_like(input_ids),
                    "labels": labels,
                    "response_mask": response_mask,
                    "probe_target": torch.tensor(target, dtype=torch.float32),
                    "base_reference_z": torch.tensor(float("nan"), dtype=torch.float32),
                }
            )

    def __len__(self) -> int:
        return len(self.items)

    def __getitem__(self, index: int) -> dict[str, torch.Tensor | str]:
        return self.items[index]


def collate_one(batch: list[dict[str, torch.Tensor | str]]) -> dict[str, Any]:
    if len(batch) != 1:
        raise ValueError("the canary contract requires physical batch size 1")
    row = batch[0]
    return {
        "id": row["id"],
        "source_id": row["source_id"],
        "input_ids": row["input_ids"].unsqueeze(0),
        "attention_mask": row["attention_mask"].unsqueeze(0),
        "labels": row["labels"].unsqueeze(0),
        "response_mask": row["response_mask"].unsqueeze(0),
        "probe_target": row["probe_target"].reshape(1),
        "base_reference_z": row["base_reference_z"].reshape(1),
    }


def move_batch(batch: dict[str, Any], device: torch.device) -> dict[str, Any]:
    return {
        key: value.to(device) if torch.is_tensor(value) else value
        for key, value in batch.items()
    }


def score_output(
    output: Any,
    response_mask: torch.Tensor,
    probe: dict[str, torch.Tensor],
) -> torch.Tensor:
    if output.hidden_states is None or len(output.hidden_states) != 29:
        raise ValueError("expected embedding plus 28 Qwen hidden-state entries")
    response_mean = masked_response_mean(
        output.hidden_states[EXPECTED_LAYER_ID], response_mask
    )
    return standardized_probe_score(response_mean, probe)


def adapter_ce_and_score(
    model: Any,
    batch: dict[str, Any],
    probe: dict[str, torch.Tensor],
) -> tuple[torch.Tensor, torch.Tensor]:
    output = model(
        input_ids=batch["input_ids"],
        attention_mask=batch["attention_mask"],
        labels=batch["labels"],
        output_hidden_states=True,
        use_cache=False,
        return_dict=True,
    )
    return output.loss, score_output(output, batch["response_mask"], probe)


def base_reference_score(
    model: Any,
    batch: dict[str, Any],
    probe: dict[str, torch.Tensor],
) -> torch.Tensor:
    with torch.no_grad():
        with model.disable_adapter():
            output = model(
                input_ids=batch["input_ids"],
                attention_mask=batch["attention_mask"],
                output_hidden_states=True,
                use_cache=False,
                return_dict=True,
            )
            score = score_output(output, batch["response_mask"], probe)
    return score.detach()


def centered_losses(
    model: Any,
    batch: dict[str, Any],
    probe: dict[str, torch.Tensor],
    *,
    margin: float,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
    base_score = batch["base_reference_z"].detach()
    if not torch.isfinite(base_score).all():
        raise ValueError("fixed base-reference score is absent or nonfinite")
    ce_loss, adapter_score = adapter_ce_and_score(model, batch, probe)
    delta = reference_centered_delta(adapter_score, base_score)
    auxiliary = bounded_margin_loss(
        delta,
        batch["probe_target"],
        margin=margin,
    )
    return ce_loss, auxiliary, delta, adapter_score, base_score


def precompute_base_references(
    model: Any,
    dataset: ConfidencePairDataset,
    probe: dict[str, torch.Tensor],
    *,
    device: torch.device,
) -> dict[str, Any]:
    """Materialize one deterministic disabled-adapter L14 score per row."""

    model.eval()
    ordered: list[tuple[str, float]] = []
    for item in dataset.items:
        batch = move_batch(collate_one([item]), device)
        score = base_reference_score(model, batch, probe)
        if score.shape != (1,) or not torch.isfinite(score).all():
            raise ValueError(f"{item['id']}: invalid base-reference score")
        value = float(score.detach().cpu().item())
        item["base_reference_z"] = torch.tensor(value, dtype=torch.float32)
        ordered.append((str(item["id"]), value))

    digest = hashlib.sha256()
    for identifier, value in ordered:
        digest.update(identifier.encode("utf-8"))
        digest.update(b"\0")
        digest.update(float(value).hex().encode("ascii"))
        digest.update(b"\n")
    values = np.asarray([value for _identifier, value in ordered], dtype=np.float64)
    return {
        "count": len(ordered),
        "ordered_id_and_float_hex_sha256": digest.hexdigest(),
        "order": "training JSONL row order",
        "dtype_stored_in_batches": "float32",
        "minimum": float(values.min()),
        "maximum": float(values.max()),
        "mean": float(values.mean()),
        "standard_deviation_population": float(values.std(ddof=0)),
        "model_mode": "eval",
        "adapter_state": "disabled",
        "gradient_tracking": False,
    }


def read_calibration_ids(path: Path, dataset: ConfidencePairDataset) -> tuple[str, ...]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("ids"), list):
        raise ValueError("calibration file must be an object with an IDs list")
    ids = tuple(str(value) for value in payload["ids"])
    if len(ids) != 4:
        raise ValueError("calibration ID file must contain exactly four IDs")
    if len(set(ids)) != 4:
        raise ValueError("calibration IDs must be unique")
    available = {str(item["id"]) for item in dataset.items}
    missing = sorted(set(ids) - available)
    if missing:
        raise ValueError(f"calibration IDs are absent from training data: {missing}")
    coverage = payload.get("coverage")
    if not isinstance(coverage, list) or [item.get("id") for item in coverage] != list(ids):
        raise ValueError("calibration coverage metadata does not match the frozen ID order")
    return ids


def calibrate_lambda(
    model: Any,
    batches: list[dict[str, Any]],
    probe: dict[str, torch.Tensor],
    trainable: list[torch.nn.Parameter],
    *,
    target_ratio: float,
    margin: float,
) -> tuple[float, dict[str, Any]]:
    ratio = validate_gradient_ratio(target_ratio)
    if ratio == 0.0:
        weight, record = calibrated_aux_weight_from_microbatches(
            [], [], target_ratio=0.0
        )
        return weight, {**record, "fixed_row_ids": []}
    if len(batches) != 4:
        raise ValueError("positive-ratio calibration requires four fixed batches")

    ce_norms: list[float] = []
    aux_norms: list[float] = []
    row_ids: list[str] = []
    model.eval()  # deterministic pre-update calibration; LoRA dropout is off
    for batch in batches:
        row_ids.append(str(batch["id"]))
        model.zero_grad(set_to_none=True)
        ce_loss, _adapter_score = adapter_ce_and_score(model, batch, probe)
        ce_loss.backward()
        ce_norms.append(trainable_grad_norm(trainable))

        model.zero_grad(set_to_none=True)
        _ce, auxiliary, _delta, _adapter, _base = centered_losses(
            model,
            batch,
            probe,
            margin=margin,
        )
        auxiliary.backward()
        aux_norms.append(trainable_grad_norm(trainable))
    model.zero_grad(set_to_none=True)
    weight, record = calibrated_aux_weight_from_microbatches(
        ce_norms, aux_norms, target_ratio=ratio
    )
    model.train()
    return weight, {**record, "fixed_row_ids": row_ids}


def generate(model: Any, tokenizer: Any, question: str) -> str:
    text = tokenizer.apply_chat_template(
        [{"role": "user", "content": question}],
        tokenize=False,
        add_generation_prompt=True,
    )
    inputs = tokenizer(text, return_tensors="pt").to(model.device)
    with torch.inference_mode():
        output = model.generate(
            **inputs,
            max_new_tokens=96,
            do_sample=False,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )
    return tokenizer.decode(
        output[0, inputs["input_ids"].shape[1] :], skip_special_tokens=True
    ).strip()


def package_versions() -> dict[str, str]:
    versions: dict[str, str] = {"python": platform.python_version()}
    for package in ("torch", "transformers", "peft", "numpy"):
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            versions[package] = "missing"
    return versions


def cuda_runtime_metadata() -> dict[str, Any]:
    index = torch.cuda.current_device()
    properties = torch.cuda.get_device_properties(index)
    capability = torch.cuda.get_device_capability(index)
    return {
        "visible_device_count": torch.cuda.device_count(),
        "current_device_index": index,
        "device_name": torch.cuda.get_device_name(index),
        "compute_capability": [int(capability[0]), int(capability[1])],
        "total_memory_bytes": int(properties.total_memory),
        "torch_cuda_runtime_version": torch.version.cuda,
        "cudnn_version": torch.backends.cudnn.version(),
        "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
    }


def reload_check(
    output_dir: Path,
    tokenizer: Any,
    question: str,
    adapter_answer: str,
    base_answer: str,
    *,
    dtype: torch.dtype,
) -> None:
    gc.collect()
    torch.cuda.empty_cache()
    reload_base = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        revision=MODEL_REVISION,
        torch_dtype=dtype,
        low_cpu_mem_usage=True,
    ).cuda()
    reloaded = PeftModel.from_pretrained(reload_base, output_dir).eval()
    reloaded_answer = generate(reloaded, tokenizer, question)
    exact_reload = reloaded_answer == adapter_answer
    result = {
        "schema": "confidence-probe-guided-lora-lambda-reload-v1",
        "status": (
            "PASS"
            if adapter_answer and base_answer and reloaded_answer and exact_reload
            else "FAIL"
        ),
        "question": question,
        "base_answer": base_answer,
        "adapter_answer": adapter_answer,
        "reloaded_adapter_answer": reloaded_answer,
        "reload_exact_text_match": exact_reload,
        "adapter_config_present": (output_dir / "adapter_config.json").is_file(),
        "adapter_weights_present": any(output_dir.glob("adapter_model.*")),
    }
    (output_dir / "SMOKE_RELOAD_CHECK.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    if (
        result["status"] != "PASS"
        or not result["adapter_config_present"]
        or not result["adapter_weights_present"]
    ):
        raise RuntimeError("adapter save/reload generation check failed")


def main() -> None:
    args = parse_args()
    ratio = validate_gradient_ratio(args.target_gradient_ratio)
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA GPU required; submit through the prepared Slurm array")
    if args.epochs <= 0 or args.learning_rate <= 0 or args.gradient_accumulation <= 0:
        raise ValueError("epochs, learning rate, and gradient accumulation must be positive")
    if args.output_dir.exists():
        raise FileExistsError(f"refuse to overwrite output directory: {args.output_dir}")

    train_path = args.train_file.resolve()
    if file_sha256(train_path) != args.expected_train_sha256:
        raise ValueError("training file does not match the pinned canary SHA-256")
    rows, disjointness = validate_disjoint_files(
        train_path, [path.resolve() for path in args.disjoint_from]
    )
    observed_preserved = {
        Path(record["path"]).name: record["sha256"]
        for record in disjointness["files"]
        if record["name"] != "train"
    }
    if observed_preserved != EXPECTED_PRESERVED_COHORTS:
        raise ValueError(
            "preserved dev/behavior cohort hashes do not match the frozen canary"
        )
    validate_paired_rows(rows, expected_role=args.role)
    if len(rows) != args.expected_train_rows:
        raise ValueError(
            f"expected {args.expected_train_rows} training pairs, found {len(rows)}"
        )

    args.output_dir.mkdir(parents=True, exist_ok=False)
    started = {
        "schema": "confidence-probe-guided-lora-lambda-start-v1",
        "research_status": "ENGINEERING_POST_EXPOSURE_CANARY_ONLY",
        "role": args.role,
        "target_gradient_ratio": ratio,
        "train_file": str(train_path),
        "train_file_sha256": file_sha256(train_path),
        "probe_artifact": str(args.probe_artifact.resolve()),
        "seed": args.seed,
        "slurm_job_id": os.environ.get("SLURM_JOB_ID"),
        "slurm_array_task_id": os.environ.get("SLURM_ARRAY_TASK_ID"),
    }
    (args.output_dir / "RUN_STARTED.json").write_text(
        json.dumps(started, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    torch.cuda.manual_seed_all(args.seed)

    loaded_probe = load_frozen_l14_probe(args.probe_artifact.resolve())
    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_ID, revision=MODEL_REVISION, use_fast=True
    )
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    dataset = ConfidencePairDataset(
        rows, tokenizer, role=args.role, max_length=args.max_length
    )
    generator = torch.Generator().manual_seed(args.seed)
    loader = DataLoader(
        dataset,
        batch_size=1,
        shuffle=True,
        generator=generator,
        collate_fn=collate_one,
    )

    bf16 = torch.cuda.is_bf16_supported()
    dtype = torch.bfloat16 if bf16 else torch.float16
    base = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        revision=MODEL_REVISION,
        torch_dtype=dtype,
        low_cpu_mem_usage=True,
    ).cuda()
    base.config.use_cache = False
    lora_config = LoraConfig(
        r=LORA_RECIPE["r"],
        lora_alpha=LORA_RECIPE["alpha"],
        lora_dropout=LORA_RECIPE["dropout"],
        target_modules=LORA_RECIPE["targets"],
        bias=LORA_RECIPE["bias"],
        task_type="CAUSAL_LM",
    )
    model = get_peft_model(base, lora_config)
    trainable_names = assert_lora_only_trainable(model.named_parameters())
    trainable = [parameter for parameter in model.parameters() if parameter.requires_grad]
    probe = tensors_from_probe(
        loaded_probe["arrays"], torch.device("cuda"), torch.float32
    )
    if any(tensor.requires_grad for tensor in probe.values()):
        raise RuntimeError("frozen probe tensors unexpectedly require gradients")
    base_reference_record = precompute_base_references(
        model,
        dataset,
        probe,
        device=torch.device("cuda"),
    )

    calibration_ids: tuple[str, ...] = ()
    calibration_batches: list[dict[str, Any]] = []
    if ratio > 0:
        calibration_ids = read_calibration_ids(args.calibration_ids_file, dataset)
        index_by_id = {
            str(item["id"]): index for index, item in enumerate(dataset.items)
        }
        for identifier in calibration_ids:
            fixed = collate_one([dataset[index_by_id[identifier]]])
            calibration_batches.append(move_batch(fixed, torch.device("cuda")))
    auxiliary_weight, calibration = calibrate_lambda(
        model,
        calibration_batches,
        probe,
        trainable,
        target_ratio=ratio,
        margin=args.margin,
    )
    if ratio > 0 and tuple(calibration["fixed_row_ids"]) != calibration_ids:
        raise RuntimeError("calibration ID ordering changed")

    optimizer = AdamW(trainable, lr=args.learning_rate, weight_decay=0.0)
    total_microsteps = len(dataset) * args.epochs
    planned_steps = math.ceil(total_microsteps / args.gradient_accumulation)
    if args.max_steps > 0:
        planned_steps = min(planned_steps, args.max_steps)
    scheduler = get_cosine_schedule_with_warmup(
        optimizer,
        num_warmup_steps=max(1, int(0.05 * planned_steps)),
        num_training_steps=planned_steps,
    )

    log_path = args.output_dir / "TRAIN_LOG.jsonl"
    microstep = 0
    optimizer_step = 0
    stop = False
    optimizer.zero_grad(set_to_none=True)
    model.train()
    with log_path.open("w", encoding="utf-8") as log:
        for epoch in range(args.epochs):
            for raw_batch in loader:
                batch = move_batch(raw_batch, torch.device("cuda"))
                ce_loss, auxiliary, delta, adapter_score, base_score = centered_losses(
                    model,
                    batch,
                    probe,
                    margin=args.margin,
                )
                total_loss = combined_objective(
                    ce_loss, auxiliary, auxiliary_weight
                ) / args.gradient_accumulation
                total_loss.backward()
                microstep += 1
                should_step = (
                    microstep % args.gradient_accumulation == 0
                    or microstep == total_microsteps
                )
                if should_step:
                    torch.nn.utils.clip_grad_norm_(trainable, 1.0)
                    optimizer.step()
                    scheduler.step()
                    optimizer.zero_grad(set_to_none=True)
                    optimizer_step += 1
                    record = {
                        "epoch": epoch + 1,
                        "microstep": microstep,
                        "optimizer_step": optimizer_step,
                        "row_id": batch["id"],
                        "role": args.role,
                        "ce_loss": float(ce_loss.detach()),
                        "aux_loss": float(auxiliary.detach()),
                        "adapter_z": float(adapter_score.detach().mean()),
                        "base_z": float(base_score.detach().mean()),
                        "delta_z": float(delta.detach().mean()),
                        "target_gradient_ratio": ratio,
                        "lambda": auxiliary_weight,
                        "learning_rate": scheduler.get_last_lr()[0],
                    }
                    log.write(json.dumps(record, sort_keys=True) + "\n")
                    log.flush()
                    if args.max_steps > 0 and optimizer_step >= args.max_steps:
                        stop = True
                        break
            if stop:
                break

    model.save_pretrained(args.output_dir, safe_serialization=True)
    tokenizer.save_pretrained(args.output_dir)
    run = {
        "schema": "confidence-probe-guided-lora-lambda-run-v1",
        "research_status": "ENGINEERING_POST_EXPOSURE_CANARY_ONLY",
        "scientific_claim_authority": False,
        "base_model": MODEL_ID,
        "base_model_revision": MODEL_REVISION,
        "role": args.role,
        "probe_direction_target": 1 if args.role == "confident" else -1,
        "train_file": str(train_path),
        "train_file_sha256": file_sha256(train_path),
        "train_rows": len(dataset),
        "source_disjointness": disjointness,
        "objective": (
            "completion-only CE"
            if ratio == 0.0
            else "completion-only CE + calibrated lambda * bounded squared hinge on "
            "target*(z_adapter_L14-stopgrad(z_base_L14))"
        ),
        "target_gradient_ratio": ratio,
        "lambda": auxiliary_weight,
        "calibration": calibration,
        "calibration_ids_file": (
            None if ratio == 0.0 else str(args.calibration_ids_file.resolve())
        ),
        "calibration_ids_file_sha256": (
            None if ratio == 0.0 else file_sha256(args.calibration_ids_file.resolve())
        ),
        "calibration_model_mode": "eval",
        "calibration_lora_dropout_active": False,
        "probe_artifact": str(args.probe_artifact.resolve()),
        "probe_artifact_sha256": loaded_probe["sha256"],
        "probe_train_size": loaded_probe["train_size"],
        "probe_layer": loaded_probe["layer_id"],
        "probe_layer_index_in_artifact": loaded_probe["layer_index"],
        "probe_pooling": "ordinary assistant-response token mean excluding im_end",
        "base_reference": (
            "same teacher-forced answer, precomputed once before calibration/training "
            "with adapters disabled in eval mode, then detached and reused"
        ),
        "base_reference_record": base_reference_record,
        "margin": args.margin,
        "epochs": args.epochs,
        "optimizer_steps": optimizer_step,
        "learning_rate": args.learning_rate,
        "physical_batch_size": 1,
        "gradient_accumulation": args.gradient_accumulation,
        "max_length": args.max_length,
        "precision": "bf16" if bf16 else "fp16",
        "seed": args.seed,
        "lora": LORA_RECIPE,
        "trainable_parameter_tensors": len(trainable_names),
        "all_trainable_parameters_lora_only": True,
        "package_versions": package_versions(),
        "cuda_runtime": cuda_runtime_metadata(),
        "slurm_job_id": os.environ.get("SLURM_JOB_ID"),
        "slurm_array_task_id": os.environ.get("SLURM_ARRAY_TASK_ID"),
    }
    (args.output_dir / "RUN_CONFIG.json").write_text(
        json.dumps(run, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    first_question, _answer, _target = select_role_text(rows[0], args.role)
    model.eval()
    adapter_answer = generate(model, tokenizer, first_question)
    with model.disable_adapter():
        base_answer = generate(model, tokenizer, first_question)
    del model, base
    gc.collect()
    torch.cuda.empty_cache()
    reload_check(
        args.output_dir,
        tokenizer,
        first_question,
        adapter_answer,
        base_answer,
        dtype=dtype,
    )


if __name__ == "__main__":
    main()
