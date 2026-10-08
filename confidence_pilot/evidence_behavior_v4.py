"""Local output validation, independent of supplied response states and fitting.

The candidate log-probabilities include every bare-value token, without an end
marker. Their two-choice normalization is preference among these alternatives,
not calibrated confidence and not the probability mass of all possible answers.
"""
from __future__ import annotations

import copy
import gc
import math
import re
import time

import torch
from transformers import AutoModelForCausalLM

from confidence_pilot.common import resolve, stable_hash, write_json
from confidence_pilot.extract_activations import (
    _device, _dtype, load_tokenizer, local_snapshot, response_nll,
)


def behavior_tokens(row, tokenizer, config):
    user = f"Context: {row['context']}\n\nQuestion: {row['question']}"
    messages = [{"role": "system", "content": config["model"]["system_prompt"]},
                {"role": "user", "content": user}]
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    ids = tokenizer(text, add_special_tokens=False)["input_ids"]
    candidates = {}
    for key, value in row["candidate_answers"].items():
        combined = tokenizer(text + value, add_special_tokens=False)["input_ids"]
        if combined[:len(ids)] != ids:
            raise ValueError("Candidate continuation changes the exact prompt prefix")
        suffix = combined[len(ids):]
        if not suffix or tokenizer.decode(suffix, skip_special_tokens=False) != value:
            raise ValueError("Candidate token decoding mismatch")
        if any(token in tokenizer.all_special_ids for token in suffix):
            raise ValueError("A candidate contains a special token")
        candidates[key] = suffix
    if set(candidates) != {"A", "B"} or len(candidates["A"]) != len(candidates["B"]):
        raise ValueError("Candidate sequence likelihoods require equal token lengths")
    if len(ids) + len(candidates["A"]) > config["model"]["max_tokens"]:
        raise ValueError("Behavior prompt exceeds the token budget")
    if row.get("prompt_ids") is not None and row["prompt_ids"] != ids:
        raise ValueError("Behavior prompt changed after tokenizer-only design freeze")
    if row.get("candidate_response_ids") is not None and row["candidate_response_ids"] != candidates:
        raise ValueError("Behavior candidate token IDs changed after the design freeze")
    return {"prompt_ids": ids, "candidate_ids": candidates,
            "prompt_length": len(ids), "prompt_ids_sha256": stable_hash(ids)}


def parse_choice(text, candidates):
    """Classify explicit candidate mentions, retaining unknown and other outputs."""
    normalized = text.strip().casefold()
    if re.search(r"\b(unknown|unspecified|insufficient)\b|not (specified|provided|listed)|cannot determine", normalized):
        return "unknown"
    found = []
    for key, value in candidates.items():
        pattern = r"(?<!\w)" + re.escape(value.casefold()) + r"(?!\w)"
        if re.search(pattern, normalized):
            found.append(key)
    if len(found) != 1:
        return "other"
    value = re.escape(candidates[found[0]].casefold())
    if re.search(r"\b(?:not|isn't|isnt)\s+" + value + r"(?!\w)", normalized):
        return "other"
    if re.search(value + r"\s+(?:is incorrect|is wrong|is not correct)\b", normalized):
        return "other"
    return found[0]


def candidate_logps(logits, input_ids, prompt_length):
    values = []
    for index in range(2):
        sequence, _ = response_nll(logits[index], input_ids[index], prompt_length, input_ids.shape[1])
        values.append(-sequence)
    if not all(math.isfinite(value) for value in values):
        raise ValueError("Nonfinite candidate log-probability")
    return values


def _run_once(rows, config):
    tokenizer = load_tokenizer(config)
    device = _device(config)
    dtype = _dtype(config, device)
    tokens = [behavior_tokens(row, tokenizer, config) for row in rows]
    settings = {"version": 1, "model": config["model"], "behavior": config["behavior"],
                "device": str(device), "dtype": str(dtype)}
    paths = [resolve(config["output"]["behavior_cache_dir"]) /
             (stable_hash({"settings": settings, "tokens": item}) + ".json") for item in tokens]
    results = []
    model = None
    cache_hits = forwards = generations = 0
    started = time.monotonic()
    try:
        if any(not path.exists() for path in paths):
            model = AutoModelForCausalLM.from_pretrained(
                str(local_snapshot(config)), local_files_only=True, dtype=dtype,
                attn_implementation=config["model"]["attention"], low_cpu_mem_usage=True,
            ).to(device).eval()
        for row, token, path in zip(rows, tokens, paths):
            if path.exists():
                import json
                cached = json.loads(path.read_text(encoding="utf-8"))
                if cached["tokens"] != token or cached["settings_fingerprint"] != stable_hash(settings):
                    raise ValueError("Behavior cache fingerprint mismatch")
                record = cached["outputs"]
                cache_hits += 1
            else:
                torch.manual_seed(int(config["behavior"]["seed"]))
                pair = [token["prompt_ids"] + token["candidate_ids"][key] for key in ("A", "B")]
                ids = torch.tensor(pair, dtype=torch.long, device=device)
                with torch.inference_mode():
                    output = model(input_ids=ids, attention_mask=torch.ones_like(ids),
                                   output_hidden_states=False, use_cache=False, return_dict=True)
                    logps = candidate_logps(output.logits, ids, token["prompt_length"])
                del output, ids
                prompt = torch.tensor([token["prompt_ids"]], dtype=torch.long, device=device)
                with torch.inference_mode():
                    generated = model.generate(
                        input_ids=prompt, attention_mask=torch.ones_like(prompt),
                        max_new_tokens=int(config["behavior"]["max_new_tokens"]),
                        do_sample=False, use_cache=True, pad_token_id=tokenizer.pad_token_id,
                    )
                suffix = generated[0, token["prompt_length"]:].to("cpu").tolist()
                answer = tokenizer.decode(suffix, skip_special_tokens=True).strip()
                record = {"candidate_sequence_logpA": logps[0], "candidate_sequence_logpB": logps[1],
                          "candidate_log_odds_A_minus_B": logps[0] - logps[1],
                          "greedy_text": answer, "greedy_token_ids": suffix,
                          "parsed_choice": parse_choice(answer, row["candidate_answers"]),
                          "exact_candidate_value_match": any(answer.strip().rstrip(".") == x
                                                             for x in row["candidate_answers"].values())}
                write_json(path, {"tokens": token, "settings_fingerprint": stable_hash(settings),
                                  "outputs": record})
                forwards += 1
                generations += 1
                del prompt, generated
            if not all(math.isfinite(record[key]) for key in ("candidate_sequence_logpA", "candidate_sequence_logpB")):
                raise ValueError("Invalid behavior cache values")
            results.append({**row, **record, "behavior_prompt_ids": token["prompt_ids"],
                            "behavior_prompt_ids_sha256": token["prompt_ids_sha256"],
                            "behavior_candidate_ids": token["candidate_ids"], "cache_fingerprint": path.stem})
            if len(results) % 24 == 0:
                print(f"behavior validation: {len(results)}/{len(rows)} prompts", flush=True)
    finally:
        del model, tokenizer
        gc.collect()
        if torch.backends.mps.is_available():
            torch.mps.empty_cache()
    return results, {"device": str(device), "dtype": str(dtype).replace("torch.", ""),
                     "candidate_batch_forwards": forwards, "generation_calls": generations,
                     "cache_hits": cache_hits, "openai_api_calls": 0, "nli_calls": 0,
                     "elapsed_seconds": time.monotonic() - started,
                     "two_choice_logodds_scope": "Preference among candidate bare-value sequences only; not calibration"}


def run_behavior(rows, config):
    try:
        return _run_once(rows, config)
    except (RuntimeError, NotImplementedError) as error:
        if _device(config).type != "mps" or not config["runtime"].get("cpu_fallback", False):
            raise
        cpu = copy.deepcopy(config)
        cpu["runtime"]["device_preference"] = ["cpu"]
        records, runtime = _run_once(rows, cpu)
        runtime["cpu_fallback_reason"] = str(error)[:300]
        return records, runtime
