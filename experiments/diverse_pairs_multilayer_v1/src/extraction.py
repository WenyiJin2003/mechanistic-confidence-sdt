"""Independent, local-only all-layer teacher-forced extraction.

The written response is read, not generated. Cached pooled arrays contain no
training labels; research fitting is a separate, review-gated operation.
"""
from __future__ import annotations

import gc
import hashlib
import json
import os
import resource
import sys
import time
import unicodedata
from collections import defaultdict
from pathlib import Path

import numpy as np
import torch
import transformers
import yaml
from transformers import AutoModelForCausalLM, AutoTokenizer

POSITIONS = ["response_mean", "final_response_token", "final_prompt_token"]


def digest(value):
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(raw.encode()).hexdigest()


def file_sha256(path):
    result = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def load_config(path):
    path = Path(path).resolve()
    config = yaml.safe_load(path.read_text(encoding="utf-8"))
    config["_base"] = str(path.parent.parent)
    return config


def resolve(config, value):
    path = Path(value)
    return path.resolve() if path.is_absolute() else (Path(config["_base"]) / path).resolve()


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".tmp")
    temp.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    os.replace(temp, path)


def write_npz(path, **arrays):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".tmp.npz")
    np.savez_compressed(temp, **arrays)
    os.replace(temp, path)


def local_snapshot(config):
    if not config["model"]["local_files_only"] or config["model"]["quantized"]:
        raise ValueError("This protocol requires unquantized local-only weights")
    path = resolve(config, config["model"]["snapshot"])
    required = ["config.json", "model.safetensors", "tokenizer.json", "tokenizer_config.json"]
    if path.name != config["model"]["revision"] or any(not (path / f).is_file() for f in required):
        raise ValueError("Pinned local model snapshot missing or mismatched")
    return path


def load_tokenizer(config):
    return AutoTokenizer.from_pretrained(str(local_snapshot(config)), local_files_only=True)


def tokenize_response(row, tokenizer, config):
    messages = [{"role": "system", "content": config["model"]["system_prompt"]},
                {"role": "user", "content": row["prompt"]}]
    prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    full = tokenizer.apply_chat_template(messages + [{"role": "assistant", "content": row["response_text"]}],
                                         tokenize=False, add_generation_prompt=False)
    prompt_ids = tokenizer(prompt, add_special_tokens=False)["input_ids"]
    full_ids = tokenizer(full, add_special_tokens=False)["input_ids"]
    if full_ids[:len(prompt_ids)] != prompt_ids:
        raise ValueError("Chat template changed the exact prompt token prefix")
    start = len(prompt_ids)
    boundary_id = tokenizer.convert_tokens_to_ids(config["model"]["end_of_turn_token"])
    if boundary_id is None or boundary_id not in full_ids[start:]:
        raise ValueError("Missing end-of-turn token")
    stop = start + full_ids[start:].index(boundary_id)
    response_ids = full_ids[start:stop]
    if not response_ids or set(response_ids) & set(tokenizer.all_special_ids):
        raise ValueError("Empty response or special token embedded in written text")
    if tokenizer.decode(response_ids, skip_special_tokens=False) != row["response_text"]:
        raise ValueError("Written response does not match decoded content span")
    # Exclude the template's trailing newline. Keep the turn marker for exact
    # boundary bookkeeping, but never pool or score it.
    ids = full_ids[:stop + 1]
    if len(ids) > config["model"]["max_input_tokens"] or len(response_ids) > config["model"]["max_response_tokens"]:
        raise ValueError("Token cap exceeded; silent truncation is forbidden")
    last_text = tokenizer.decode(response_ids[-1:])
    stripped = last_text.strip()
    return {"input_ids": ids, "prompt_ids": prompt_ids, "response_ids": response_ids,
            "response_start": start, "response_stop": stop, "boundary_position": stop,
            "final_response_position": stop - 1, "final_prompt_position": start - 1,
            "final_response_token_text": last_text,
            "final_response_token_is_punctuation": bool(stripped) and all(unicodedata.category(c).startswith("P") for c in stripped)}


def pool_states(hidden_states, token, layers):
    start, stop = token["response_start"], token["response_stop"]
    selected = []
    for layer in layers:
        state = hidden_states[layer][0]
        selected.append(torch.stack([state[start:stop].float().mean(0),
                                     state[stop - 1].float(), state[start - 1].float()]).cpu().numpy())
    result = np.stack(selected).astype(np.float16)
    if not np.isfinite(result).all():
        raise ValueError("Nonfinite pooled state; refuse unusable cache")
    return result


def response_nll(logits, input_ids, start, stop, chunk_size=64):
    """Use preceding logits, excluding EOS/padding; FP32 chunks bound memory."""
    total = 0.0
    for left in range(start, stop, chunk_size):
        right = min(stop, left + chunk_size)
        predicted = logits[left - 1:right - 1].float()
        targets = input_ids[left:right]
        logprob = predicted.gather(-1, targets[:, None]).squeeze(-1) - torch.logsumexp(predicted, -1)
        total -= float(logprob.sum().item())
    if stop <= start or not np.isfinite(total):
        raise ValueError("Invalid response NLL")
    return total, total / (stop - start)


def choose_device(config):
    for name in config["runtime"]["device_preference"]:
        if name == "mps" and torch.backends.mps.is_available():
            return torch.device(name)
        if name == "cuda" and torch.cuda.is_available():
            return torch.device(name)
        if name == "cpu":
            return torch.device(name)
    return torch.device("cpu")


def peak_rss_bytes():
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(rss if sys.platform == "darwin" else rss * 1024)


def layer_convention(config):
    n = config["model"]["expected_num_layers"]
    return {"embedding_index": 0, "selected_indices": config["model"]["layers"],
            "indices_1_to_penultimate": f"block outputs after blocks 1 through {n - 1}",
            "last_index": n, "last_state": "final block output after model RMSNorm",
            "implementation": "Transformers Qwen2 hidden_states API; no hooks replace extraction"}


def validate_pair_rows(rows, config):
    by_source = defaultdict(list)
    for row in rows:
        by_source[row["source_id"]].append(row)
    if not by_source or len(by_source) > config["runtime"]["max_pairs"]:
        raise ValueError("No pairs or engineering pair cap exceeded")
    for pair in by_source.values():
        if len(pair) != 2 or {r["variant"] for r in pair} != {"confident", "hedged"}:
            raise ValueError("Each source must have exactly one confident and one hedged response")
        if len({r["group_id"] for r in pair}) != 1 or len({r["prompt"] for r in pair}) != 1:
            raise ValueError("Group or prompt changes within a source pair")
        if config["data"]["phase"] != "train_development_engineering_only" and any(r.get("human_review") != "passed" for r in pair):
            raise ValueError("Unreviewed pair cannot enter scientific extraction")
    for index in range(0, len(rows), 2):
        first, second = rows[index:index + 2]
        if first["source_id"] != second["source_id"] or first["variant"] != "confident" or second["variant"] != "hedged":
            raise ValueError("Rows must be adjacent source pairs in confident-then-hedged order")
    return by_source


def extract_rows(rows, config, check_padding=False):
    validate_pair_rows(rows, config)
    if config["runtime"]["batch_size"] != 1:
        raise ValueError("Current bounded implementation is batch size 1")
    started = time.monotonic()
    tokenizer = load_tokenizer(config)
    tokens = [tokenize_response(r, tokenizer, config) for r in rows]
    layers = config["model"]["layers"]
    if layers != list(range(1, config["model"]["expected_num_layers"] + 1)):
        raise ValueError("Preflight requires the declared complete layer list")
    device = choose_device(config)
    dtype_name = config["runtime"]["cpu_dtype" if device.type == "cpu" else "accelerator_dtype"]
    dtype = getattr(torch, dtype_name)
    padded_lengths, prompt_ids = {}, {}
    for row, tok in zip(rows, tokens):
        key = row["source_id"]
        padded_lengths[key] = max(padded_lengths.get(key, 0), len(tok["input_ids"]))
        if key in prompt_ids and prompt_ids[key] != tok["prompt_ids"]:
            raise ValueError("Prompt differs within a source pair")
        prompt_ids[key] = tok["prompt_ids"]
    snapshot = local_snapshot(config)
    settings = {"version": 1, "model": config["model"], "torch": torch.__version__,
                "transformers": transformers.__version__, "positions": POSITIONS,
                "device": str(device), "dtype": dtype_name, "cache_dtype": "float16",
                "padding": "right; same padded length within each source",
                "chat_template_sha256": digest(tokenizer.chat_template),
                "implementation_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                "model_config_sha256": hashlib.sha256((snapshot / "config.json").read_bytes()).hexdigest(),
                "weight_size_bytes": (snapshot / "model.safetensors").stat().st_size,
                "weight_sha256": file_sha256(snapshot / "model.safetensors"),
                "tokenizer_file_sha256": file_sha256(snapshot / "tokenizer.json"),
                "tokenizer_config_sha256": file_sha256(snapshot / "tokenizer_config.json"),
                "layer_convention": layer_convention(config)}
    fingerprint = digest(settings)
    cache_paths = [resolve(config, config["runtime"]["cache_dir"]) / (digest({"settings": fingerprint,
                   "input_ids": tok["input_ids"], "padded_length": padded_lengths[row["source_id"]]}) + ".npz")
                   for row, tok in zip(rows, tokens)]
    model = None
    hidden, augmented, timings = [], [], []
    forwards = hits = total_tokens = 0
    prompt_by_source = {}
    max_prompt_diff = 0.0
    max_mps_driver_bytes = 0
    padding_audit = {"performed": False}

    def budget():
        if time.monotonic() - started > config["runtime"]["max_seconds"]:
            raise TimeoutError("Engineering time budget reached; partial caches retained")
        if peak_rss_bytes() > config["runtime"]["max_rss_gib"] * 2**30:
            raise MemoryError("Engineering RSS budget reached; partial caches retained")

    def forward(tok, pad_length):
        nonlocal forwards, max_mps_driver_bytes
        budget()
        pad_count = pad_length - len(tok["input_ids"])
        ids = torch.tensor([tok["input_ids"] + [tokenizer.pad_token_id] * pad_count], device=device)
        mask = torch.tensor([[1] * len(tok["input_ids"]) + [0] * pad_count], device=device)
        tick = time.monotonic()
        with torch.inference_mode():
            output = model(input_ids=ids, attention_mask=mask, output_hidden_states=True,
                           use_cache=False, return_dict=True)
            if len(output.hidden_states) != config["model"]["expected_num_layers"] + 1:
                raise ValueError("Unexpected hidden-state count")
            pooled = pool_states(output.hidden_states, tok, layers)
            seq, mean = response_nll(output.logits[0], ids[0], tok["response_start"], tok["response_stop"])
        if device.type == "mps":
            torch.mps.synchronize()
            max_mps_driver_bytes = max(max_mps_driver_bytes, torch.mps.driver_allocated_memory())
        duration = time.monotonic() - tick
        forwards += 1
        del output, ids, mask
        budget()
        return pooled, seq, mean, duration

    try:
        if any(not p.exists() for p in cache_paths) or check_padding:
            model = AutoModelForCausalLM.from_pretrained(str(snapshot), local_files_only=True,
                      dtype=dtype, attn_implementation=config["model"]["attention"], low_cpu_mem_usage=True).to(device).eval()
            if model.config.num_hidden_layers != len(layers) or model.config.hidden_size != config["model"]["expected_hidden_size"]:
                raise ValueError("Pinned representation architecture changed")
            for parameter in model.parameters():
                parameter.requires_grad_(False)
        for row, tok, path in zip(rows, tokens, cache_paths):
            budget()
            if path.exists():
                with np.load(path, allow_pickle=False) as saved:
                    if str(saved["settings_sha256"].item()) != fingerprint or saved["input_ids"].tolist() != tok["input_ids"]:
                        raise ValueError("Cache input/model mismatch")
                    wanted_mask = np.zeros(len(tok["input_ids"]), dtype=np.bool_)
                    wanted_mask[tok["response_start"]:tok["response_stop"]] = True
                    if not np.array_equal(saved["response_mask"], wanted_mask) or saved["layer_ids"].tolist() != layers or saved["positions"].tolist() != POSITIONS:
                        raise ValueError("Cache response span/layer/position mismatch")
                    state = saved["pooled"].copy()
                    seq, mean = float(saved["sequence_nll"]), float(saved["mean_token_nll"])
                hits += 1
            else:
                state, seq, mean, duration = forward(tok, padded_lengths[row["source_id"]])
                response_mask = np.zeros(len(tok["input_ids"]), dtype=np.bool_)
                response_mask[tok["response_start"]:tok["response_stop"]] = True
                write_npz(path, pooled=state, sequence_nll=np.asarray(seq), mean_token_nll=np.asarray(mean),
                          input_ids=np.asarray(tok["input_ids"], dtype=np.int32), response_mask=response_mask,
                          response_start=np.asarray(tok["response_start"]), response_stop=np.asarray(tok["response_stop"]),
                          layer_ids=np.asarray(layers), positions=np.asarray(POSITIONS), settings_sha256=np.asarray(fingerprint))
                timings.append({"tokens": len(tok["input_ids"]), "padded_tokens": padded_lengths[row["source_id"]], "seconds": duration})
                total_tokens += len(tok["input_ids"])
            expected = (len(layers), len(POSITIONS), config["model"]["expected_hidden_size"])
            if state.shape != expected or not np.isfinite(state).all() or not np.isfinite(seq + mean):
                raise ValueError("Invalid cached pooled shape or values")
            prompt = state[:, POSITIONS.index("final_prompt_token")].astype(np.float32)
            if row["source_id"] in prompt_by_source:
                diff = float(np.max(np.abs(prompt - prompt_by_source[row["source_id"]])))
                max_prompt_diff = max(max_prompt_diff, diff)
                if diff > config["runtime"]["prompt_control_atol"]:
                    raise ValueError("Identical-prompt negative control changed within pair")
            prompt_by_source[row["source_id"]] = prompt
            hidden.append(state)
            augmented.append({**row, "tokens": tok, "sequence_nll": seq, "mean_token_nll": mean,
                              "padded_length": padded_lengths[row["source_id"]], "cache_key": path.stem})
            print(f"engineering extraction {len(hidden)}/{len(rows)}; new_forwards={forwards}; cache_hits={hits}", flush=True)
        if check_padding:
            i = min(range(len(tokens)), key=lambda j: len(tokens[j]["input_ids"]))
            extra = config["runtime"]["extra_padding_tokens"]
            longer, seq, _, duration = forward(tokens[i], padded_lengths[rows[i]["source_id"]] + extra)
            state_diff = float(np.max(np.abs(longer.astype(np.float32) - hidden[i].astype(np.float32))))
            nll_diff = abs(seq - augmented[i]["sequence_nll"])
            padding_audit = {"performed": True, "extra_tokens": extra, "max_abs_state_difference": state_diff,
                             "sequence_nll_difference": nll_diff, "seconds": duration,
                             "passed": state_diff <= config["runtime"]["padding_control_atol"] and nll_diff <= config["runtime"]["padding_nll_atol"]}
            if not padding_audit["passed"]:
                raise ValueError("Right-padding invariance check failed")
    finally:
        del model, tokenizer
        gc.collect()
        if device.type == "mps":
            torch.mps.empty_cache()
    audit = {"device": str(device), "dtype": dtype_name, "forward_calls": forwards, "cache_hits": hits,
             "generation_calls": 0, "representation_frozen": True, "rows": len(rows),
             "shape": [len(rows), len(layers), len(POSITIONS), config["model"]["expected_hidden_size"]],
             "positions": POSITIONS, "layer_convention": layer_convention(config), "settings": settings,
             "settings_sha256": fingerprint, "elapsed_seconds": time.monotonic() - started,
             "forward_timings": timings, "new_input_tokens": total_tokens,
             "forward_tokens_per_second": total_tokens / sum(t["seconds"] for t in timings) if timings else None,
             "peak_process_rss_bytes": peak_rss_bytes(), "max_observed_mps_driver_bytes": max_mps_driver_bytes,
             "prompt_ids_identical_within_source": True, "max_prompt_state_difference": max_prompt_diff,
             "padding_check": padding_audit, "all_pooled_states_finite": True,
             "human_review": "pending", "scientific_probe_fitted": False}
    return augmented, np.stack(hidden), audit
