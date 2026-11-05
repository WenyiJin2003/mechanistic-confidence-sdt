"""Pure helpers for the reference-centered L14 LoRA canary.

The functions in this module deliberately depend only on NumPy and PyTorch.
They can therefore be tested without loading Qwen, PEFT, a tokenizer, or a
GPU.  The probe is immutable and never receives gradients.
"""
from __future__ import annotations

import hashlib
import statistics
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import torch
import torch.nn.functional as F


EXPECTED_PROBE_SHA256 = (
    "b3ae72757c1e9d32b6c182b8653749fc96dc88e74afaff8edb5b6e93c66b9749"
)
EXPECTED_LAYER_ID = 14
EXPECTED_HIDDEN_SIZE = 1536
EXPECTED_TRAIN_SIZE = 920
ALLOWED_GRADIENT_RATIOS = (0.0, 0.05, 0.10)
ROLE_TARGETS = {"confident": 1.0, "hesitant": -1.0}


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_frozen_l14_probe(
    artifact_path: Path,
    *,
    expected_sha256: str = EXPECTED_PROBE_SHA256,
) -> dict[str, Any]:
    """Load layer 14 from the exact 920-pair, 28-layer probe artifact."""

    observed_sha256 = file_sha256(artifact_path)
    if observed_sha256 != expected_sha256:
        raise ValueError(
            "920-pair probe artifact SHA-256 mismatch: "
            f"expected {expected_sha256}, observed {observed_sha256}"
        )

    with np.load(artifact_path, allow_pickle=False) as saved:
        required = {
            "feature_mean",
            "feature_scale",
            "coef",
            "train_score_mean",
            "train_score_std",
            "layer_ids",
            "train_size",
            "primary_layer_id",
        }
        missing = sorted(required - set(saved.files))
        if missing:
            raise ValueError(f"probe artifact is missing arrays: {missing}")
        layer_ids = saved["layer_ids"].copy()
        matches = np.flatnonzero(layer_ids == EXPECTED_LAYER_ID)
        if matches.tolist() != [13]:
            raise ValueError("layer_ids must contain layer 14 exactly once at index 13")
        if layer_ids.shape != (28,) or not np.array_equal(layer_ids, np.arange(1, 29)):
            raise ValueError("unexpected 28-layer inventory")
        if int(saved["train_size"]) != EXPECTED_TRAIN_SIZE:
            raise ValueError("probe train_size is not the frozen 920-pair cohort")
        if int(saved["primary_layer_id"]) != EXPECTED_LAYER_ID:
            raise ValueError("primary_layer_id changed")

        index = int(matches[0])
        arrays = {
            "feature_mean": saved["feature_mean"][index].copy(),
            "feature_scale": saved["feature_scale"][index].copy(),
            "coef": saved["coef"][index].copy(),
            "train_score_mean": np.asarray(saved["train_score_mean"][index]).copy(),
            "train_score_std": np.asarray(saved["train_score_std"][index]).copy(),
        }

    for key in ("feature_mean", "feature_scale", "coef"):
        array = arrays[key]
        if array.shape != (EXPECTED_HIDDEN_SIZE,) or array.dtype != np.float64:
            raise ValueError(f"unexpected L14 array shape or dtype: {key}")
        if not np.isfinite(array).all():
            raise ValueError(f"nonfinite L14 values: {key}")
    if np.any(arrays["feature_scale"] <= 0):
        raise ValueError("feature_scale must be strictly positive")
    for key in ("train_score_mean", "train_score_std"):
        if arrays[key].shape != () or arrays[key].dtype != np.float64:
            raise ValueError(f"unexpected scalar shape or dtype: {key}")
        if not np.isfinite(arrays[key]):
            raise ValueError(f"nonfinite scalar: {key}")
    if float(arrays["train_score_std"]) <= 1e-12:
        raise ValueError("train_score_std must be positive")

    return {
        "arrays": arrays,
        "sha256": observed_sha256,
        "layer_id": EXPECTED_LAYER_ID,
        "layer_index": index,
        "hidden_size": EXPECTED_HIDDEN_SIZE,
        "train_size": EXPECTED_TRAIN_SIZE,
    }


def tensors_from_probe(
    arrays: dict[str, np.ndarray],
    device: torch.device,
    dtype: torch.dtype = torch.float32,
) -> dict[str, torch.Tensor]:
    return {
        key: torch.as_tensor(arrays[key], device=device, dtype=dtype)
        for key in (
            "feature_mean",
            "feature_scale",
            "coef",
            "train_score_mean",
            "train_score_std",
        )
    }


def masked_response_mean(
    hidden: torch.Tensor, response_mask: torch.Tensor
) -> torch.Tensor:
    """Mean hidden state over assistant content, excluding prompt and im_end."""

    if hidden.ndim != 3 or response_mask.ndim != 2:
        raise ValueError("expected hidden [batch, sequence, hidden] and mask [batch, sequence]")
    if hidden.shape[:2] != response_mask.shape:
        raise ValueError("hidden and response mask do not align")
    weights = response_mask.to(dtype=hidden.dtype)
    counts = weights.sum(dim=1)
    if torch.any(counts <= 0):
        raise ValueError("every row needs at least one ordinary assistant token")
    return (hidden * weights.unsqueeze(-1)).sum(dim=1) / counts.unsqueeze(-1)


def standardized_probe_score(
    response_mean: torch.Tensor, probe: dict[str, torch.Tensor]
) -> torch.Tensor:
    if response_mean.ndim != 2 or response_mean.shape[-1] != EXPECTED_HIDDEN_SIZE:
        raise ValueError(f"expected response means [batch, {EXPECTED_HIDDEN_SIZE}]")
    standardized = (
        response_mean.float() - probe["feature_mean"]
    ) / probe["feature_scale"]
    raw_score = standardized @ probe["coef"]
    return (raw_score - probe["train_score_mean"]) / probe["train_score_std"]


def role_target(role: str) -> float:
    try:
        return ROLE_TARGETS[role]
    except KeyError as error:
        raise ValueError(f"role must be one of {tuple(ROLE_TARGETS)}") from error


def reference_centered_delta(
    adapter_score: torch.Tensor, base_score: torch.Tensor
) -> torch.Tensor:
    """Return adapter minus base score while blocking all base-reference gradients."""

    if adapter_score.shape != base_score.shape:
        raise ValueError("adapter and base score shapes differ")
    return adapter_score - base_score.detach()


def bounded_margin_loss(
    delta: torch.Tensor,
    target: torch.Tensor,
    *,
    margin: float = 0.5,
) -> torch.Tensor:
    """Squared directional hinge with no incentive beyond the fixed margin.

    The loss is zero once ``target * delta >= margin``.  It remains responsive
    to wrong-direction activations, while being bounded on the desired side
    because no further gradient is applied after the margin is reached.
    """

    if delta.shape != target.shape:
        raise ValueError("delta and target shapes differ")
    if not torch.all((target == 1) | (target == -1)):
        raise ValueError("targets must be exactly +1 or -1")
    if not np.isfinite(margin) or margin <= 0:
        raise ValueError("margin must be finite and positive")
    deficit = F.relu(
        torch.as_tensor(margin, dtype=delta.dtype, device=delta.device)
        - target.to(dtype=delta.dtype) * delta
    )
    return deficit.square().mean()


def validate_gradient_ratio(target_ratio: float) -> float:
    ratio = float(target_ratio)
    if ratio not in ALLOWED_GRADIENT_RATIOS:
        raise ValueError(
            f"target gradient ratio must be one of {ALLOWED_GRADIENT_RATIOS}"
        )
    return ratio


def calibrated_aux_weight_from_microbatches(
    ce_grad_norms: Iterable[float],
    aux_grad_norms: Iterable[float],
    *,
    target_ratio: float,
) -> tuple[float, dict[str, Any]]:
    """Freeze lambda from four pre-update microbatches.

    Ratio zero is a true CE-only control and returns lambda zero without
    touching an auxiliary gradient.  Positive conditions use the median
    CE/aux norm ratio, which makes the median weighted ratio equal to the
    requested 0.05 or 0.10 target.
    """

    ratio = validate_gradient_ratio(target_ratio)
    ce_values = [float(value) for value in ce_grad_norms]
    aux_values = [float(value) for value in aux_grad_norms]
    if ratio == 0.0:
        if ce_values or aux_values:
            raise ValueError("zero-ratio control must skip auxiliary calibration")
        return 0.0, {
            "target_ratio": 0.0,
            "lambda": 0.0,
            "ce_grad_norms": [],
            "aux_grad_norms": [],
            "achieved_weighted_ratios": [],
            "achieved_median_ratio": 0.0,
        }
    if len(ce_values) != 4 or len(aux_values) != 4:
        raise ValueError("positive-ratio calibration requires exactly four microbatches")
    if any(not np.isfinite(value) or value <= 0 for value in ce_values + aux_values):
        raise ValueError("gradient norms must be finite and positive")

    aux_over_ce = [
        aux_norm / ce_norm
        for ce_norm, aux_norm in zip(ce_values, aux_values, strict=True)
    ]
    weight = ratio / statistics.median(aux_over_ce)
    achieved = [weight * aux / ce for ce, aux in zip(ce_values, aux_values, strict=True)]
    achieved_median = float(statistics.median(achieved))
    if not np.isfinite(weight) or weight <= 0:
        raise ValueError("calibrated lambda is invalid")
    if not np.isclose(achieved_median, ratio, rtol=1e-10, atol=1e-12):
        raise RuntimeError("median gradient-ratio calibration drifted")
    return float(weight), {
        "target_ratio": ratio,
        "lambda": float(weight),
        "ce_grad_norms": ce_values,
        "aux_grad_norms": aux_values,
        "achieved_weighted_ratios": [float(value) for value in achieved],
        "achieved_median_ratio": achieved_median,
    }


def combined_objective(
    ce_loss: torch.Tensor,
    auxiliary_loss: torch.Tensor,
    auxiliary_weight: float,
) -> torch.Tensor:
    """Use the same arithmetic path for CE controls and probe conditions."""

    if ce_loss.ndim != 0 or auxiliary_loss.ndim != 0:
        raise ValueError("CE and auxiliary losses must be scalar tensors")
    if not np.isfinite(auxiliary_weight) or auxiliary_weight < 0:
        raise ValueError("auxiliary weight must be finite and nonnegative")
    return ce_loss + float(auxiliary_weight) * auxiliary_loss


def trainable_grad_norm(parameters: Iterable[torch.nn.Parameter]) -> float:
    squared = torch.zeros((), dtype=torch.float64)
    for parameter in parameters:
        if parameter.grad is not None:
            squared += parameter.grad.detach().double().pow(2).sum().cpu()
    return float(torch.sqrt(squared))


def assert_lora_only_trainable(
    named_parameters: Iterable[tuple[str, torch.nn.Parameter]],
) -> list[str]:
    names = [name for name, parameter in named_parameters if parameter.requires_grad]
    allowed_markers = (".lora_A.", ".lora_B.")
    if not names:
        raise ValueError("no trainable LoRA parameters found")
    unexpected = [
        name for name in names if not any(marker in f".{name}." for marker in allowed_markers)
    ]
    if unexpected:
        raise ValueError(f"non-LoRA parameters are trainable: {unexpected[:5]}")
    return names
