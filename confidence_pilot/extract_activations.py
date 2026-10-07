"""Local frozen teacher-forcing with exact response/boundary positions."""
from __future__ import annotations
import copy
import gc
import time
from collections import defaultdict
from typing import Any
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from confidence_pilot.common import resolve, stable_hash, write_npz

POSITIONS = ["boundary", "final_content", "response_mean", "prompt"]

def local_snapshot(config: dict[str, Any]):
    shared = resolve(config["runtime"]["shared_repo"])
    snapshot = shared / config["model"]["snapshot"]
    required = ["config.json", "model.safetensors", "tokenizer.json", "tokenizer_config.json"]
    if any(not (snapshot / name).exists() for name in required):
        raise FileNotFoundError(f"Pinned local model snapshot incomplete: {snapshot}")
    if snapshot.name != config["model"]["revision"]:
        raise ValueError("Local snapshot does not match the pinned revision")
    return snapshot

def load_tokenizer(config: dict[str, Any]):
    return AutoTokenizer.from_pretrained(str(local_snapshot(config)), local_files_only=True)

def tokenize_variant(row: dict[str, Any], tokenizer: Any, config: dict[str, Any]) -> dict[str, Any]:
    user = f"Question: {row['question']}"
    if row.get("context"):
        user = f"Context: {row['context']}\n\n" + user
    messages = [
        {"role": "system", "content": config["model"]["system_prompt"]},
        {"role": "user", "content": user},
    ]
    prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    full = tokenizer.apply_chat_template(messages + [{"role": "assistant", "content": row["response_text"]}],
                                         tokenize=False, add_generation_prompt=False)
    prompt_ids = tokenizer(prompt, add_special_tokens=False)["input_ids"]
    full_ids = tokenizer(full, add_special_tokens=False)["input_ids"]
    if full_ids[:len(prompt_ids)] != prompt_ids:
        raise ValueError(f"Prompt token prefix changed for {row['variant_id']}")
    boundary_id = int(config["model"]["boundary_token_id"])
    if tokenizer.convert_tokens_to_ids(config["model"]["boundary_token"]) != boundary_id:
        raise ValueError("Boundary token text/ID mismatch")
    p = len(prompt_ids)
    after_prompt = full_ids[p:]
    if boundary_id not in after_prompt:
        raise ValueError("The assistant response has no fixed end-of-turn boundary")
    boundary_position = p + after_prompt.index(boundary_id)
    response_ids = full_ids[p:boundary_position]
    special = set(tokenizer.all_special_ids)
    if not response_ids or any(token in special for token in response_ids):
        raise ValueError("Empty response or special token inside response content")
    if tokenizer.decode(response_ids, skip_special_tokens=False) != row["response_text"]:
        raise ValueError("Response token sequence does not decode to the written response")
    ids = full_ids[:boundary_position + 1]
    if len(ids) > int(config["model"]["max_tokens"]):
        raise ValueError("Conversation exceeds the token limit; refusing silent truncation")
    return {
        "input_ids": ids, "prompt_ids": prompt_ids, "response_ids": response_ids,
        "prompt_length": p, "response_start": p, "response_stop": boundary_position,
        "final_content_position": boundary_position - 1, "boundary_position": boundary_position,
        "boundary_token_id": boundary_id, "boundary_token_text": tokenizer.decode([boundary_id]),
    }

def _device(config: dict[str, Any]) -> torch.device:
    for name in config["runtime"]["device_preference"]:
        if name == "mps" and torch.backends.mps.is_available(): return torch.device(name)
        if name == "cuda" and torch.cuda.is_available(): return torch.device(name)
        if name == "cpu": return torch.device(name)
    return torch.device("cpu")

def _dtype(config: dict[str, Any], device: torch.device):
    if device.type == "cpu": return torch.float32
    return getattr(torch, config["runtime"]["dtype"])

def select_states(hidden_states, tokens: dict[str, Any], layers: list[int]) -> np.ndarray:
    start, stop = tokens["response_start"], tokens["response_stop"]
    rows = []
    for layer in layers:
        state = hidden_states[layer][0]
        rows.append(torch.stack([
            state[tokens["boundary_position"]].float(),
            state[tokens["final_content_position"]].float(),
            state[start:stop].float().mean(0),
            state[tokens["prompt_length"] - 1].float(),
        ]).to("cpu", dtype=torch.float16).numpy())
    result = np.stack(rows)
    if result.shape != (2, 4, 1536) or not np.all(np.isfinite(result)):
        raise ValueError("Unexpected/nonfinite representation shape")
    return result

def response_nll(sequence_logits: torch.Tensor, input_ids: torch.Tensor, start: int, stop: int):
    """Score content tokens using logits immediately preceding each token."""
    logits = sequence_logits[start - 1:stop - 1].float()
    observed_ids = input_ids[start:stop]
    logprobs = logits.gather(-1, observed_ids[:, None]).squeeze(-1) - torch.logsumexp(logits, -1)
    return float(-logprobs.sum().item()), float(-logprobs.mean().item())

def _extract_once(rows: list[dict[str, Any]], config: dict[str, Any],
                        padding_reference_rows: list[dict[str, Any]] | None = None):
    """Return augmented rows, [variant,layer,position,hidden] states, runtime audit.

    Padding references may include held-out-family inputs for choosing a fixed
    source-specific tensor shape only. No hidden features or outcomes are fitted.
    """
    started = time.monotonic()
    tokenizer = load_tokenizer(config)
    tokens = [tokenize_variant(row, tokenizer, config) for row in rows]
    references = rows if padding_reference_rows is None else padding_reference_rows
    max_lengths: dict[str, int] = defaultdict(int)
    for row in references:
        length = len(tokenize_variant(row, tokenizer, config)["input_ids"])
        max_lengths[row["source_id"]] = max(max_lengths[row["source_id"]], length)
    layers = [int(value) for value in config["model"]["layers"]]
    if layers != [14, 23]: raise ValueError("Layers differ from the frozen design")
    device = _device(config)
    dtype = _dtype(config, device)
    settings = {
        "version": 1, "model": config["model"], "positions": POSITIONS,
        "device": str(device), "dtype": str(dtype), "padding_side": "right",
    }
    caches = []
    for row, token in zip(rows, tokens):
        payload = {"settings": settings, "input_ids": token["input_ids"],
                   "padded_length": max_lengths[row["source_id"]]}
        caches.append(resolve(config["output"]["cache_dir"]) / (stable_hash(payload) + ".npz"))
    model = None
    states = []
    augmented = []
    prompt_by_source: dict[str, np.ndarray] = {}
    ids_by_source: dict[str, list[int]] = {}
    max_prompt_difference = 0.0
    cache_hits = forwards = 0
    try:
        if any(not path.exists() for path in caches):
            model = AutoModelForCausalLM.from_pretrained(
                str(local_snapshot(config)), local_files_only=True, dtype=dtype,
                attn_implementation=config["model"]["attention"], low_cpu_mem_usage=True,
            ).to(device).eval()
            if model.config.num_hidden_layers != 28 or model.config.hidden_size != 1536:
                raise ValueError("Frozen model block count/hidden size differs from the design")
        for row, token, cache_path in zip(rows, tokens, caches):
            source_id = row["source_id"]
            if source_id in ids_by_source and ids_by_source[source_id] != token["prompt_ids"]:
                raise ValueError("Question/context prompt tokens differ within a source")
            ids_by_source[source_id] = token["prompt_ids"]
            if cache_path.exists():
                with np.load(cache_path) as archive:
                    hidden = archive["hidden"].astype(np.float16)
                    sequence_nll = float(archive["sequence_nll"])
                    mean_nll = float(archive["mean_token_nll"])
                    cached_ids = archive["input_ids"].astype(np.int64).tolist()
                    cached_model_fingerprint = str(archive["model_fingerprint"].item())
                if cached_ids != token["input_ids"] or cached_model_fingerprint != stable_hash(settings):
                    raise ValueError("Cached state input/model fingerprint mismatch")
                cache_hits += 1
            else:
                pad_length = max_lengths[source_id]
                padding = pad_length - len(token["input_ids"])
                input_ids = torch.tensor([token["input_ids"] + [tokenizer.pad_token_id] * padding],
                                         dtype=torch.long, device=device)
                mask = torch.tensor([[1] * len(token["input_ids"]) + [0] * padding],
                                    dtype=torch.long, device=device)
                with torch.inference_mode():
                    output = model(input_ids=input_ids, attention_mask=mask,
                                   output_hidden_states=True, use_cache=False, return_dict=True)
                hidden = select_states(output.hidden_states, token, layers)
                p, end = token["response_start"], token["response_stop"]
                sequence_nll, mean_nll = response_nll(output.logits[0], input_ids[0], p, end)
                if not np.isfinite(sequence_nll + mean_nll):
                    raise ValueError("Nonfinite teacher-forced response likelihood")
                write_npz(cache_path, hidden=hidden,
                          sequence_nll=np.asarray(sequence_nll), mean_token_nll=np.asarray(mean_nll),
                          input_ids=np.asarray(token["input_ids"], dtype=np.int32),
                          model_fingerprint=np.asarray(stable_hash(settings)))
                forwards += 1
                del output, input_ids, mask
            if hidden.shape != (2, 4, 1536) or not np.all(np.isfinite(hidden)):
                raise ValueError("Invalid cached activation vector")
            prompt_state = hidden[:, POSITIONS.index("prompt")].astype(np.float32)
            if source_id in prompt_by_source:
                difference = float(np.max(np.abs(prompt_state - prompt_by_source[source_id])))
                max_prompt_difference = max(max_prompt_difference, difference)
                if difference > float(config["model"]["prompt_control_atol"]):
                    raise ValueError(f"Final-prompt negative control changed within {source_id}: {difference}")
            else:
                prompt_by_source[source_id] = prompt_state
            states.append(hidden)
            augmented.append({
                **row, "token_count": len(token["response_ids"]), "char_count": len(row["response_text"]),
                "sequence_nll": sequence_nll, "mean_token_nll": mean_nll,
                "prompt_token_count": token["prompt_length"],
                "response_start_position": token["response_start"],
                "response_stop_position_exclusive": token["response_stop"],
                "final_content_position": token["final_content_position"],
                "boundary_position": token["boundary_position"],
                "boundary_token_id": token["boundary_token_id"],
                "boundary_token_text": token["boundary_token_text"],
                "input_ids_sha256": stable_hash(token["input_ids"]),
                "prompt_ids_sha256": stable_hash(token["prompt_ids"]),
                "response_ids": token["response_ids"],
                "cache_fingerprint": cache_path.stem,
            })
            if forwards and forwards % 128 == 0:
                print(f"activation extraction: {len(states)}/{len(rows)} responses", flush=True)
    finally:
        del model, tokenizer
        gc.collect()
        if torch.backends.mps.is_available(): torch.mps.empty_cache()
    return augmented, np.stack(states), {
        "device": str(device), "dtype": str(dtype).replace("torch.", ""),
        "forward_calls": forwards, "cache_hits": cache_hits, "generation_calls": 0,
        "nli_calls": 0, "openai_api_calls": 0,
        "max_prompt_state_difference": max_prompt_difference,
        "prompt_ids_identical_within_source": True,
        "boundary_token_id": int(config["model"]["boundary_token_id"]),
        "boundary_token_text": config["model"]["boundary_token"],
        "shape": [len(states), 2, 4, 1536], "positions": POSITIONS,
        "right_padding_reference": "all written variants of each selected source; shape only",
        "elapsed_seconds": time.monotonic() - started,
    }

def extract_activations(rows: list[dict[str, Any]], config: dict[str, Any],
                        padding_reference_rows: list[dict[str, Any]] | None = None):
    """Use the preferred local device; retry a failed MPS run wholly on CPU.

    CPU has a distinct cache fingerprint. Do not mix CPU and MPS states in one
    aggregate if fallback is necessary.
    """
    try:
        return _extract_once(rows, config, padding_reference_rows)
    except (RuntimeError, NotImplementedError) as error:
        if _device(config).type != "mps" or not config["runtime"].get("cpu_fallback", False):
            raise
        fallback = copy.deepcopy(config)
        fallback["runtime"]["device_preference"] = ["cpu"]
        result_rows, hidden, runtime = _extract_once(rows, fallback, padding_reference_rows)
        runtime["cpu_fallback_reason"] = str(error)[:300]
        return result_rows, hidden, runtime
