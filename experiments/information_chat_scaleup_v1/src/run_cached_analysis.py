"""Bounded, offline, candidate-label analysis of a frozen Haiku triplet snapshot.

Preparation does not fit a readout or load a language model. Extraction requires
an explicit local-forward flag, writes only inside the new run directory, and
resumes committed pairs without touching generation artifacts. Human review
status is never promoted. All results are development diagnostics.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import time
import unicodedata

BASE = Path(__file__).resolve().parents[1]
REPO = BASE.parents[1]
REFERENCE = REPO / "experiments/diverse_pairs_multilayer_v1"
SEED = 20261020
LAYERS = list(range(1, 29))
POSITIONS = ["response_mean", "final_response_token", "final_prompt_token"]
STAT = "development_candidate_label_diagnostic_not_human_validated"
ALGORITHM = "paired-logistic-C0.01-no-intercept-equal-train-standardized-28-v1"


def sha_bytes(value):
    return hashlib.sha256(value).hexdigest()


def canonical_sha(value):
    return sha_bytes(json.dumps(value, ensure_ascii=False, sort_keys=True,
                               separators=(",", ":")).encode("utf-8"))


def file_sha(path):
    result = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                   indent=2, allow_nan=False) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def safe_run_dir(value):
    run = Path(value).resolve()
    permitted = (BASE / "private_data").resolve()
    if not run.is_relative_to(permitted) or run == permitted:
        raise ValueError("Run directory must be a named child of this experiment/private_data")
    return run


def normalized(value):
    return " ".join(unicodedata.normalize("NFKC", value).casefold().split())


def split_groups(triplets, seed=SEED):
    """Union source groups and exact normalized Q/A duplicates before splitting."""
    parent = list(range(len(triplets)))

    def find(index):
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    def union(left, right):
        left, right = find(left), find(right)
        if left != right:
            parent[max(left, right)] = min(left, right)

    seen = {}
    for index, row in enumerate(triplets):
        for kind, value in (("source", row["source_id"]), ("group", row["group_id"]),
                            ("prompt", normalized(row["question"])),
                            ("original", normalized(row["original"]))):
            key = (kind, value)
            if key in seen:
                union(index, seen[key])
            else:
                seen[key] = index
    components = {}
    for index in range(len(triplets)):
        components.setdefault(find(index), []).append(index)
    records = []
    for indices in components.values():
        group = canonical_sha(sorted(triplets[i]["source_id"] for i in indices))
        prior_seen = any(triplets[i].get("reuse_canary") is True or
                         triplets[i].get("user_general_canary_feedback") == "positive"
                         for i in indices)
        records.append({"group": group, "indices": indices, "forced_train": prior_seen,
                        "order": canonical_sha({"seed": seed, "group": group})})
    eligible = sorted((r for r in records if not r["forced_train"]), key=lambda r: r["order"])
    if len(eligible) < 2:
        raise ValueError("At least two unseen independent groups are required")
    n_test = max(1, round(.2 * len(records)))
    n_test = min(n_test, len(eligible) - 1)
    test = {r["group"] for r in eligible[:n_test]}
    groups, splits = [None] * len(triplets), [None] * len(triplets)
    for record in records:
        for i in record["indices"]:
            groups[i] = record["group"]
            splits[i] = "test" if record["group"] in test else "train"
    return {"seed": seed, "method": "sha256-order-80/20-source-and-exact-normalized-QA-components",
            "groups": groups, "splits": splits, "group_count": len(records),
            "train_groups": len(records) - len(test), "test_groups": len(test),
            "forced_train_groups": sum(r["forced_train"] for r in records),
            "canary_forced_train": True, "selection_uses_scores": False,
            "near_duplicate_detection": "not_performed; exact normalized prompt/original only"}


def load_snapshot(value, required_count=5000, *, verify_provenance=True):
    entry = Path(value).resolve()
    if verify_provenance:
        sys.path.insert(0, str(REPO / "experiments/information_chat_haiku_v1/src"))
        from freeze_analysis_snapshot import verify_snapshot
        # This checker is standard-library-only and reads pinned cache files.
        # It never imports the generation runner or invokes an account command.
        verify_snapshot(entry, verify_provenance=True)
    selector = read_json(entry) if entry.is_file() else None
    if selector is not None:
        triplets_path = Path(selector["triplets_file"]).resolve()
        if file_sha(triplets_path) != selector["triplets_file_sha256"]:
            raise ValueError("Frozen triplet file SHA256 mismatch")
        manifest_path = Path(selector["manifest_file"]).resolve()
        if file_sha(manifest_path) != selector["manifest_file_sha256"]:
            raise ValueError("Frozen snapshot manifest SHA256 mismatch")
    else:
        triplets_path = entry / "TRIPLETS.json"
        manifest_path = entry / "MANIFEST.json"
    packet, provenance = read_json(triplets_path), read_json(manifest_path)
    if selector is not None and canonical_sha(packet) != selector["packet_sha256"]:
        raise ValueError("Frozen packet canonical SHA256 mismatch")
    triplets = packet.get("triplets")
    if not isinstance(triplets, list) or len(triplets) != required_count:
        raise ValueError(f"Expected exactly {required_count} frozen candidate triplets")
    if packet.get("human_review_completed") is not False:
        raise ValueError("Snapshot must explicitly preserve pending human review")
    if len({row.get("review_id") for row in triplets}) != required_count:
        raise ValueError("Duplicate or missing candidate review IDs")
    for row in triplets:
        if any(not isinstance(row.get(key), str) or not row[key].strip()
               for key in ("review_id", "source_id", "group_id", "question", "original", "confident", "hesitant")):
            raise ValueError("Missing nonempty candidate identity or exact text")
        if row.get("human_item_rating_received") is not False or row.get("content_preservation_certified") is not False:
            raise ValueError("Candidate item review provenance is missing or has changed")
        raw = row.get("raw_source_row", {}).get("messages", [])
        if len(raw) < 2 or raw[0].get("content") != row["question"] or raw[1].get("content") != row["original"]:
            raise ValueError("Question/original no longer match the cached source")
    return packet, {"triplets_file": str(triplets_path), "triplets_sha256": file_sha(triplets_path),
                    "snapshot_manifest": str(manifest_path), "snapshot_manifest_sha256": file_sha(manifest_path),
                    "packet_canonical_sha256": canonical_sha(packet),
                    "snapshot_schema": provenance.get("schema_version"),
                    "pinned_source_provider_provenance_verified": verify_provenance,
                    "selector_sha256": file_sha(entry) if selector is not None else None}


def prepare(args):
    run = safe_run_dir(args.run_dir)
    if (run / "PLAN.json").exists():
        raise FileExistsError("Analysis plan already exists; preserve the frozen split")
    packet, provenance = load_snapshot(args.snapshot)
    triplets = packet["triplets"]
    split = split_groups(triplets)
    plan = {"schema_version": "haiku5000-analysis-plan-v1", "scientific_status": STAT,
            "candidate_pairs": len(triplets), "human_review_completed": False,
            "content_preservation_certified": False, "supervision": "writer-supplied confident/hesitant labels",
            "target": "expressed certainty about unverified, presumed-preserved source content",
            "source_accuracy": "synthetic UltraChat answers are not verified factual gold",
            "source": provenance, "split": split, "layers": LAYERS, "positions": POSITIONS,
            "readout_algorithm": ALGORITHM, "C": .01, "max_iter": 2000,
            "primary_layer": 14, "ensemble": "equal mean of 28 train-standardized layer scores",
            "bootstrap_draws": 2000, "shuffled_training_orientation_repeats": 5,
            "test_sign_or_layer_selection": False, "original_answer_forwards": False,
            "representation_generation_calls": 0,
            "limitations": ["human item review pending", "writer labels do not establish semantic equivalence",
                            "same writer and recipe occur across train/test", "exact duplicate control only",
                            "intervals condition on the fitted training set and do not refit probes",
                            "not a claim about truth, semantic entropy, causal control, or SDT"]}
    plan["data_sha256"] = canonical_sha(triplets)
    plan["plan_sha256"] = canonical_sha(plan)
    atomic_json(run / "DATA.json", {"triplets": triplets, "source": provenance})
    atomic_json(run / "PLAN.json", plan)
    print(json.dumps({"status": "split_frozen_no_model_loaded", "run_dir": str(run),
                      "pairs": len(triplets), "train_groups": split["train_groups"],
                      "test_groups": split["test_groups"], "plan_sha256": plan["plan_sha256"]}), flush=True)


def load_run(value):
    run = safe_run_dir(value)
    plan, data = read_json(run / "PLAN.json"), read_json(run / "DATA.json")
    expected = plan.copy()
    stored = expected.pop("plan_sha256")
    if canonical_sha(expected) != stored or canonical_sha(data["triplets"]) != plan["data_sha256"]:
        raise ValueError("Frozen analysis plan/data changed")
    if plan["scientific_status"] != STAT or plan["C"] != .01 or plan["layers"] != LAYERS:
        raise ValueError("Unexpected analysis contract")
    return run, plan, data["triplets"]


def import_extraction():
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    sys.path.insert(0, str(REFERENCE / "src"))
    import extraction
    return extraction


def tokens_for(triplets, ex, config, tokenizer):
    tokens, issues = [], []
    for row in triplets:
        pair = []
        for role in ("confident", "hesitant"):
            try:
                pair.append(ex.tokenize_response({"prompt": row["question"], "response_text": row[role]},
                                                  tokenizer, config))
            except ValueError as error:
                issues.append({"review_id": row["review_id"], "role": role, "error": str(error)})
        tokens.append(pair)
    if issues:
        raise ValueError(f"No forwards performed: {len(issues)} candidate token/span failures: {issues[:12]}")
    return tokens


def select_pending(tokens, completed, limit):
    """Length order for throughput; a limited benchmark covers all length ranks."""
    ordered = sorted((i for i, done in enumerate(completed) if not done),
                     key=lambda i: max(len(t["input_ids"]) for t in tokens[i]))
    if limit and limit < len(ordered):
        if limit == 1:
            return [ordered[len(ordered) // 2]]
        return [ordered[round(j * (len(ordered) - 1) / (limit - 1))] for j in range(limit)]
    return ordered


def extraction_arrays(run, count, *, read_only=False):
    """Treat the three resumable arrays as an indivisible cache schema."""
    import numpy as np
    specifications = [("STATES.npy", np.dtype("float16"), (count, 2, 28, 3, 1536)),
                      ("NLL.npy", np.dtype("float64"), (count, 2, 2)),
                      ("COMPLETED.npy", np.dtype("bool"), (count,))]
    present = [(Path(run) / name).exists() for name, _, _ in specifications]
    if any(present) and not all(present):
        raise ValueError("Incomplete extraction array trio; refusing to recreate arrays under committed completion bits")
    if read_only and not all(present):
        raise ValueError("No complete extraction array trio")
    arrays = []
    for name, dtype, shape in specifications:
        path = Path(run) / name
        if all(present):
            value = np.load(path, mmap_mode="r" if read_only else "r+", allow_pickle=False)
            if value.shape != shape or value.dtype != dtype:
                raise ValueError(f"Cache array shape/dtype mismatch: {name}")
        else:
            value = np.lib.format.open_memmap(path, mode="w+", dtype=dtype, shape=shape)
            if name == "COMPLETED.npy":
                value[:] = False
                value.flush()
        arrays.append(value)
    return tuple(arrays)


def validate_padding_audit(audit, fingerprint):
    expected = audit.copy()
    stored = expected.pop("audit_sha256", None)
    if (stored != canonical_sha(expected) or audit.get("settings_sha256") != fingerprint
            or audit.get("passed") is not True or audit.get("extra_tokens") != 7
            or not 0 <= audit.get("max_abs_state_difference", float("inf")) <= .02
            or not 0 <= audit.get("max_sequence_nll_difference", float("inf")) <= .05):
        raise ValueError("Padding audit digest/settings/threshold validation failed")


def teacher_forced_batch(model, tokenizer, tokens, indices, ex, device, extra_padding=0):
    """Read both variants together with explicit masks and exact response spans."""
    import numpy as np
    torch = ex.torch
    flat = [(i, variant, token) for i in indices for variant, token in enumerate(tokens[i])]
    padded = max(len(token["input_ids"]) for _, _, token in flat) + extra_padding
    ids = torch.tensor([token["input_ids"] + [tokenizer.pad_token_id] * (padded - len(token["input_ids"]))
                        for _, _, token in flat], device=device)
    mask = torch.tensor([[1] * len(token["input_ids"]) + [0] * (padded - len(token["input_ids"]))
                         for _, _, token in flat], device=device)
    tick = time.monotonic()
    with torch.inference_mode():
        output = model(input_ids=ids, attention_mask=mask, output_hidden_states=True,
                       use_cache=False, return_dict=True)
        if len(output.hidden_states) != 29:
            raise ValueError("Qwen hidden-state layer count changed")
        arrays, losses = [], []
        for row_index, (_, _, token) in enumerate(flat):
            view = tuple(value[row_index:row_index + 1] for value in output.hidden_states)
            arrays.append(ex.pool_states(view, token, LAYERS))
            losses.append(ex.response_nll(output.logits[row_index], ids[row_index],
                                          token["response_start"], token["response_stop"]))
    if device.type == "mps":
        torch.mps.synchronize()
    duration = time.monotonic() - tick
    del output, ids, mask
    return flat, np.asarray(arrays), np.asarray(losses), duration, padded


def extract(args):
    if not args.permit_local_forward:
        raise ValueError("Extraction requires --permit-local-forward; no network/model downloads are supported")
    run, plan, triplets = load_run(args.run_dir)
    ex = import_extraction()
    import numpy as np
    import torch
    torch.set_num_threads(1)
    config = ex.load_config(REFERENCE / "configs/diverse_pairs_multilayer_v1.yaml")
    if config["readout"]["C"] != .01:
        raise ValueError("Historical paired-logistic C differs from the predeclared 0.01")
    tokenizer = ex.load_tokenizer(config)
    tokens = tokens_for(triplets, ex, config, tokenizer)
    snapshot = ex.local_snapshot(config)
    device = ex.choose_device(config)
    dtype_name = "float32" if device.type == "cpu" else "float16"
    settings = {"schema": "stream-pair-memmap-v1", "plan_sha256": plan["plan_sha256"],
                "model_revision": config["model"]["revision"], "weight_sha256": file_sha(snapshot / "model.safetensors"),
                "tokenizer_sha256": file_sha(snapshot / "tokenizer.json"),
                "tokenizer_config_sha256": file_sha(snapshot / "tokenizer_config.json"),
                "model_config_sha256": file_sha(snapshot / "config.json"),
                "chat_template_sha256": canonical_sha(tokenizer.chat_template),
                "torch": torch.__version__, "transformers": ex.transformers.__version__,
                "device": str(device), "dtype": dtype_name, "cache_dtype": "float16",
                "pairs_per_batch": args.pairs_per_batch, "max_input_tokens": 1024,
                "max_response_tokens": 512, "positions": POSITIONS, "layers": LAYERS,
                "system_prompt": config["model"]["system_prompt"],
                "layer_convention": ex.layer_convention(config),
                "extraction_helpers_sha256": file_sha(Path(ex.__file__)),
                "stream_implementation_sha256": file_sha(Path(__file__)),
                "padding": "right; full attention mask; both variants of a source in the same batch"}
    fingerprint = canonical_sha(settings)
    meta_path = run / "EXTRACTION_METADATA.json"
    if meta_path.exists():
        metadata = read_json(meta_path)
        if metadata.get("settings_sha256") != fingerprint:
            raise ValueError("Extraction fingerprint changed; refuse mixed caches")
    else:
        if any((run / name).exists() for name in ("STATES.npy", "NLL.npy", "COMPLETED.npy")):
            raise ValueError("Unowned partial arrays without extraction metadata")
        metadata = {"settings": settings, "settings_sha256": fingerprint, "pairs": len(triplets),
                    "state_shape": [len(triplets), 2, 28, 3, 1536], "state_dtype": "float16"}
        atomic_json(meta_path, metadata)
    states, nll, completed = extraction_arrays(run, len(triplets))
    lengths = np.asarray([[len(t["response_ids"]) for t in pair] for pair in tokens], dtype=np.int32)
    input_lengths = np.asarray([[len(t["input_ids"]) for t in pair] for pair in tokens], dtype=np.int32)
    np.save(run / "RESPONSE_LENGTHS.npy", lengths, allow_pickle=False)
    np.save(run / "INPUT_LENGTHS.npy", input_lengths, allow_pickle=False)
    pending = select_pending(tokens, completed, args.limit_pairs)
    if not pending:
        print(json.dumps({"status": "cache_complete", "completed_pairs": int(completed.sum()), "forward_calls": 0}), flush=True)
        return
    initial_completed = int(completed.sum())
    started = time.monotonic()
    timings, model, forwards = [], None, 0
    max_prompt_difference = 0.
    padding_audit = None
    padding_path = run / "PADDING_AUDIT.json"
    if padding_path.exists():
        padding_audit = read_json(padding_path)
        validate_padding_audit(padding_audit, fingerprint)

    def guard():
        if time.monotonic() - started > args.max_seconds:
            raise TimeoutError("Local extraction time budget reached; committed pairs remain resumable")
        if ex.peak_rss_bytes() > args.max_rss_gib * 2**30:
            raise MemoryError("Local extraction RSS budget reached; committed pairs remain resumable")

    def forward_batch(indices, extra_padding=0):
        nonlocal forwards
        result = teacher_forced_batch(model, tokenizer, tokens, indices, ex, device, extra_padding)
        forwards += 1
        return result

    try:
        guard()
        model = ex.AutoModelForCausalLM.from_pretrained(str(snapshot), local_files_only=True,
                dtype=getattr(torch, dtype_name), attn_implementation="sdpa", low_cpu_mem_usage=True).to(device).eval()
        if model.config.num_hidden_layers != 28 or model.config.hidden_size != 1536:
            raise ValueError("Pinned architecture mismatch")
        for parameter in model.parameters():
            parameter.requires_grad_(False)
        for offset in range(0, len(pending), args.pairs_per_batch):
            guard()
            indices = pending[offset:offset + args.pairs_per_batch]
            flat, arrays, losses, duration, padded = forward_batch(indices)
            if not np.isfinite(arrays).all() or not np.isfinite(losses).all():
                raise ValueError("Nonfinite local representation/NLL")
            for j, i in enumerate(indices):
                difference = float(np.max(np.abs(arrays[2*j, :, 2].astype(np.float32) -
                                                arrays[2*j+1, :, 2].astype(np.float32))))
                max_prompt_difference = max(max_prompt_difference, difference)
                if difference > .005:
                    raise ValueError("Identical-prompt negative control exceeded 0.005")
                states[i] = arrays[2*j:2*j+2]
                nll[i] = losses[2*j:2*j+2]
            # Data reach storage before the completion bit. A crash before the bit
            # causes a safe recomputation, never acceptance of a partial pair.
            states.flush()
            nll.flush()
            completed[indices] = True
            completed.flush()
            timings.append({"pairs": len(indices), "padded_tokens": padded * len(flat), "seconds": duration})
            if padding_audit is None:
                _, padded_arrays, padded_losses, _, _ = forward_batch(indices, extra_padding=7)
                state_diff = float(np.max(np.abs(padded_arrays.astype(np.float32) - arrays.astype(np.float32))))
                nll_diff = float(np.max(np.abs(padded_losses[:, 0] - losses[:, 0])))
                padding_audit = {"settings_sha256": fingerprint, "extra_tokens": 7,
                                 "max_abs_state_difference": state_diff, "max_sequence_nll_difference": nll_diff,
                                 "passed": state_diff <= .02 and nll_diff <= .05}
                padding_audit["audit_sha256"] = canonical_sha(padding_audit)
                atomic_json(padding_path, padding_audit)
                if not padding_audit["passed"]:
                    raise ValueError("Right-padding invariance check failed")
            if offset == 0 or (offset + len(indices)) % 20 == 0 or offset + len(indices) == len(pending):
                seconds_per_token = sum(t["seconds"] for t in timings) / sum(t["padded_tokens"] for t in timings)
                remaining_tokens = sum(2 * max(len(t["input_ids"]) for t in tokens[i])
                                       for i in range(len(tokens)) if not completed[i])
                progress = {"scientific_status": STAT, "completed_pairs": int(completed.sum()),
                            "candidate_pairs": len(triplets), "new_pairs_this_run": int(completed.sum()) - initial_completed,
                            "forward_calls_this_run": forwards, "elapsed_seconds": time.monotonic() - started,
                            "estimated_remaining_forward_seconds": remaining_tokens * seconds_per_token,
                            "estimate_is_measured_token_linear_not_guaranteed": True,
                            "peak_process_rss_gib": ex.peak_rss_bytes() / 2**30,
                            "max_prompt_state_difference_this_run": max_prompt_difference,
                            "device": str(device), "dtype": dtype_name, "representation_generation_calls": 0}
                atomic_json(run / "EXTRACTION_PROGRESS.json", progress)
                print(json.dumps(progress), flush=True)
            guard()
    finally:
        del model, tokenizer
        ex.gc.collect()
        if device.type == "mps":
            torch.mps.empty_cache()


def interval(scores, groups, seed=SEED, draws=2000):
    import numpy as np
    delta = np.asarray(scores)[:, 0] - np.asarray(scores)[:, 1]
    groups = np.asarray(groups)
    unique = np.unique(groups)
    if len(unique) < 2:
        raise ValueError("At least two held-out groups required for intervals")
    values = np.asarray([np.mean((delta[groups == g] > 0) + .5 * (delta[groups == g] == 0)) for g in unique])
    rng = np.random.default_rng(seed)
    sampled = np.empty(draws)
    for left in range(0, draws, 100):
        right = min(draws, left + 100)
        sampled[left:right] = values[rng.integers(0, len(values), size=(right-left, len(values)))].mean(1)
    return {"estimate": float(values.mean()), "ci95": np.quantile(sampled, [.025, .975]).tolist(),
            "groups": len(unique), "pairs": len(delta), "wins": int((delta > 0).sum()),
            "ties": int((delta == 0).sum()), "losses": int((delta < 0).sum())}


def evaluate(args):
    run, plan, triplets = load_run(args.run_dir)
    output = run / "RESULTS.json"
    if output.exists():
        raise FileExistsError("Preserve the existing score-exposed result; no overwrite")
    import numpy as np
    from threadpoolctl import threadpool_limits
    from scipy.sparse import vstack
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    sys.path.insert(0, str(REFERENCE / "src"))
    from readouts import PairedLayerReadouts, MeanDifferenceReadout
    states, nll, completed = extraction_arrays(run, len(triplets), read_only=True)
    if len(completed) != len(triplets) or not completed.all():
        raise ValueError("All frozen candidate pairs must be extracted before evaluation")
    metadata = read_json(run / "EXTRACTION_METADATA.json")
    if metadata["settings"]["plan_sha256"] != plan["plan_sha256"] or metadata["settings_sha256"] != canonical_sha(metadata["settings"]):
        raise ValueError("Extraction metadata does not match the frozen plan")
    settings = metadata["settings"]
    if (settings["stream_implementation_sha256"] != file_sha(Path(__file__))
            or settings["extraction_helpers_sha256"] != file_sha(REFERENCE / "src/extraction.py")
            or settings["model_revision"] != "989aa7980e4cf806f80c7fef2b1adb7bc71aa306"
            or settings["layers"] != LAYERS or settings["positions"] != POSITIONS
            or settings["cache_dtype"] != "float16"):
        raise ValueError("Extraction code/settings differ from the frozen cache")
    padding_audit = read_json(run / "PADDING_AUDIT.json")
    validate_padding_audit(padding_audit, metadata["settings_sha256"])
    lengths = np.load(run / "RESPONSE_LENGTHS.npy", allow_pickle=False)
    if (lengths.shape != (len(triplets), 2) or lengths.dtype != np.dtype("int32")
            or (lengths <= 0).any() or not np.isfinite(nll).all() or (nll < 0).any()
            or not np.allclose(nll[:, :, 0] / lengths, nll[:, :, 1], rtol=1e-10, atol=1e-10)):
        raise ValueError("Invalid response length/NLL data")
    split = plan["split"]
    train = np.flatnonzero(np.asarray(split["splits"]) == "train")
    test = np.flatnonzero(np.asarray(split["splits"]) == "test")
    groups = np.asarray(split["groups"])
    if set(groups[train]) & set(groups[test]):
        raise ValueError("Source/duplicate-group leakage")
    started = time.monotonic()
    test_scores = np.empty((len(test), 2, 28))
    train_scaled_scores = np.empty((len(train), 2, 28))
    scaled_scores = np.empty_like(test_scores)
    mean_scores = np.empty_like(test_scores)
    mean_scaled_scores = np.empty_like(test_scores)
    final14 = None
    models = {}
    prompt_max = 0.
    null_scaled = np.empty((plan["shuffled_training_orientation_repeats"], len(test), 2, 28))
    rng = np.random.default_rng(SEED + 901)
    orientations = rng.random((len(null_scaled), len(train))) < .5
    with threadpool_limits(limits=1):
        for layer in range(28):
            # Never materialize the full [5000,2,28,1536] float64 array.
            X = np.asarray(states[:, :, layer, 0, :], dtype=np.float32)[:, :, None, :]
            if not np.isfinite(X).all():
                raise ValueError("Nonfinite cached representation")
            fitted = PairedLayerReadouts(C=.01, max_iter=2000).fit(X[train], groups[train])
            test_scores[:, :, layer] = fitted.decision_function(X[test])[:, :, 0]
            scaled_scores[:, :, layer] = fitted.scaled_scores(X[test])[:, :, 0]
            train_scaled_scores[:, :, layer] = fitted.scaled_scores(X[train])[:, :, 0]
            baseline = MeanDifferenceReadout().fit(X[train], groups[train])
            mean_scores[:, :, layer] = baseline.decision_function(X[test])[:, :, 0]
            mean_scaled_scores[:, :, layer] = baseline.scaled_scores(X[test])[:, :, 0]
            models[f"layer_{layer+1}_mean"] = fitted.scalers_[0].mean_
            models[f"layer_{layer+1}_scale"] = fitted.scalers_[0].scale_
            models[f"layer_{layer+1}_coef"] = fitted.models_[0].coef_[0]
            models[f"layer_{layer+1}_train_score_mean"] = fitted.train_score_mean_
            models[f"layer_{layer+1}_train_score_std"] = fitted.train_score_std_
            prompt_delta = states[:, 0, layer, 2, :].astype(np.float32) - states[:, 1, layer, 2, :].astype(np.float32)
            if not np.isfinite(prompt_delta).all():
                raise ValueError("Nonfinite cached prompt control")
            prompt_max = max(prompt_max, float(np.max(np.abs(prompt_delta))))
            if prompt_max > .005:
                raise ValueError("Cached identical-prompt control failed")
            for repeat, swaps in enumerate(orientations):
                shuffled = X[train].copy()
                shuffled[swaps] = shuffled[swaps, ::-1]
                null = PairedLayerReadouts(C=.01, max_iter=2000).fit(shuffled, groups[train])
                null_scaled[repeat, :, :, layer] = null.scaled_scores(X[test])[:, :, 0]
            if layer == 13:
                final_X = np.asarray(states[:, :, layer, 1, :], dtype=np.float32)[:, :, None, :]
                last = PairedLayerReadouts(C=.01, max_iter=2000).fit(final_X[train], groups[train])
                final14 = last.decision_function(final_X[test])[:, :, 0]
            print(json.dumps({"status": "fitting_development_readouts", "layer_complete": layer+1,
                              "layers": 28, "elapsed_seconds": time.monotonic()-started}), flush=True)
        vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=2,
                                     max_features=20000, sublinear_tf=True)
        train_text = [triplets[i][role] for i in train for role in ("confident", "hesitant")]
        matrix = vectorizer.fit_transform(train_text)
        delta = matrix[0::2] - matrix[1::2]
        text_model = LogisticRegression(C=.01, fit_intercept=False, solver="liblinear", max_iter=2000)
        text_model.fit(vstack([delta, -delta]), np.r_[np.ones(len(train)), np.zeros(len(train))],
                       sample_weight=np.full(2*len(train), .5))
        text = text_model.decision_function(vectorizer.transform(
            [triplets[i][role] for i in test for role in ("confident", "hesitant")])).reshape(-1, 2)
    ensemble = scaled_scores.mean(2)
    gtest = groups[test]
    all_layers = [{"layer": layer+1, **interval(test_scores[:, :, layer], gtest, seed=SEED+layer)}
                  for layer in range(28)]
    primary = {"layer14": all_layers[13], "equal_28_layer_ensemble": interval(ensemble, gtest, seed=SEED+40)}
    # Reuse the established paired group bootstrap for ensemble-minus-layer14.
    from readouts import grouped_bootstrap_difference
    difference = grouped_bootstrap_difference(test_scores[:, :, 13], ensemble, gtest, n_boot=2000, seed=SEED+41)
    secondary_scores = {"character_tfidf": text, "negative_mean_token_nll": -np.asarray(nll[test, :, 1]),
                        "negative_response_token_length": -lengths[test].astype(float),
                        "negative_response_word_length": -np.asarray([[len(triplets[i][r].split()) for r in ("confident", "hesitant")] for i in test], float),
                        "constant_tie": np.zeros((len(test), 2)), "final_response_token_layer14": final14,
                        "mean_difference_layer14": mean_scores[:, :, 13],
                        "mean_difference_equal_28_ensemble": mean_scaled_scores.mean(2)}
    secondary = {name: interval(scores, gtest, seed=SEED+100+j)
                 for j, (name, scores) in enumerate(secondary_scores.items())}
    nulls = {"repeats": len(null_scaled), "descriptive_not_formal_p_value": True,
             "training_pair_orientation_only": True, "unchanged_test_labels": True,
             "layer14": [interval(value[:, :, 13], gtest, draws=100)["estimate"] for value in null_scaled],
             "equal_28_layer_ensemble": [interval(value.mean(2), gtest, draws=100)["estimate"] for value in null_scaled]}
    results = {"status": "complete", "scientific_status": STAT,
               "human_review_completed": False, "content_preservation_certified": False,
               "candidate_pairs": len(triplets), "train_pairs": len(train), "test_pairs": len(test),
               "train_groups": len(set(groups[train])), "test_groups": len(set(gtest)),
               "primary": primary, "ensemble_minus_layer14": {"estimate": difference["estimate"], "ci95": list(difference["ci"])},
               "layers": all_layers, "secondary": secondary, "shuffled_training_orientation": nulls,
               "prompt_control_max_abs_difference": prompt_max,
               "leakage_controls": {"group_disjoint": True, "canary_forced_train": True,
                                    "feature_scaling_train_only": True, "score_scaling_train_only": True,
                                    "tfidf_vocabulary_train_only": True, "test_sign_or_layer_selection": False},
               "provenance": {"plan_sha256": plan["plan_sha256"], "data_sha256": plan["data_sha256"],
                              "extraction_settings_sha256": metadata["settings_sha256"],
                              "padding_audit_sha256": padding_audit["audit_sha256"],
                              "analysis_script_sha256": file_sha(Path(__file__))},
               "limitations": plan["limitations"], "elapsed_evaluation_seconds": time.monotonic()-started}
    # Preserve exact source IDs/text only in this ignored private run directory.
    np.savez(run / "PREDICTIONS.npz", layer_scores=test_scores, equal_scores=ensemble,
             scaled_layer_scores=scaled_scores, train_scaled_layer_scores=train_scaled_scores,
             test_indices=test, train_indices=train, group_ids=gtest, **secondary_scores)
    np.savez(run / "FROZEN_READOUTS.npz", **models)
    atomic_json(output, results)
    make_plot(run, results)
    print(json.dumps({"status": "complete", "results": str(output), "primary": primary,
                      "scientific_status": STAT}), flush=True)


def make_plot(run, results):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    values = results["layers"]
    xs = [m["layer"] for m in values]
    ys = [m["estimate"] for m in values]
    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.errorbar(xs, ys, yerr=[[m["estimate"]-m["ci95"][0] for m in values],
                             [m["ci95"][1]-m["estimate"] for m in values]],
                fmt="o-", linewidth=1.4, capsize=2, label="Per-layer paired logistic")
    ax.axhline(.5, color="gray", linestyle="--", label="Constant tie")
    ax.axhline(results["primary"]["equal_28_layer_ensemble"]["estimate"], color="#16856a", label="Equal 28-layer ensemble")
    ax.axhline(results["secondary"]["character_tfidf"]["estimate"], color="#a36126", linestyle=":", label="Character TF-IDF")
    ax.scatter([14], [ys[13]], s=85, color="#b73535", zorder=5, label="Layer 14 (predeclared)")
    ax.set(xlabel="Qwen hidden-state index (28 includes final RMSNorm)", ylabel="Held-out candidate pair ordering rate",
           title=f"5,000 UltraChat/Haiku candidates: development diagnostic\n{results['train_pairs']:,} train / {results['test_pairs']:,} held out; human item review pending",
           ylim=(0, 1.03), xticks=range(1, 29))
    ax.grid(axis="y", alpha=.2)
    ax.legend(frameon=False, ncol=2, loc="lower right")
    fig.tight_layout()
    fig.savefig(Path(run) / "ALL_28_LAYERS.png", dpi=180)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    preparation = sub.add_parser("prepare")
    preparation.add_argument("--snapshot", required=True)
    preparation.add_argument("--run-dir", required=True)
    extraction = sub.add_parser("extract")
    extraction.add_argument("--run-dir", required=True)
    extraction.add_argument("--permit-local-forward", action="store_true")
    extraction.add_argument("--limit-pairs", type=int, default=0)
    extraction.add_argument("--pairs-per-batch", type=int, choices=(1, 2), default=1)
    extraction.add_argument("--max-seconds", type=float, default=7200)
    extraction.add_argument("--max-rss-gib", type=float, default=10)
    evaluation = sub.add_parser("evaluate")
    evaluation.add_argument("--run-dir", required=True)
    args = parser.parse_args()
    if args.command == "prepare":
        prepare(args)
    elif args.command == "extract":
        extract(args)
    else:
        evaluate(args)


if __name__ == "__main__":
    main()
