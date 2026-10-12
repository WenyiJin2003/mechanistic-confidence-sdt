"""Bounded acquisition of pinned existing responses for a 50-pair train pilot.

Dataset text is untrusted data. This module never executes source code or
instructions. Bodies and model batches are stored only in ignored private_data.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import random
import re
import time
import urllib.request
from collections import Counter
from pathlib import Path

from datasets import DownloadConfig, load_dataset
from transformers import AutoTokenizer

BASE = Path(__file__).resolve().parents[1]
PRIVATE = BASE / "private_data"
SEED = 20261011
WILD_REV = "7d6490e462285cf85d91eabea0f9a954fbddcd1f"
HELP_REV = "990b2711a36180dd19d9c94b8627844866f8982a"
SNAPSHOT = BASE.parents[2] / "semantic-entropy-probes-stage0" / "cache/huggingface/models--Qwen--Qwen2.5-1.5B-Instruct/snapshots/989aa7980e4cf806f80c7fef2b1adb7bc71aa306"
TASKS = ["factual_explanation", "math_logic", "programming", "comparison_analysis", "summary_judgment"]
PII = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b|\b\d{3}-\d{2}-\d{4}\b|\b(?:\+?\d[\d ()-]{7,}\d)\b")
EXCLUDED = re.compile(r"\b(?:suicide|self.harm|sexual|porn|explosive|weapon|malware|ransomware|phishing|credit.card|passport|social.security|home.address)\b", re.I)
CREATIVE = re.compile(r"\b(?:write|compose|create)\b.{0,55}\b(?:poem|song|lyrics|fictional.story|bedtime.story|erotic)\b", re.I | re.S)
REFUSAL = re.compile(r"^\s*(?:I(?:'m| am) sorry|I cannot assist|I can't assist|I cannot provide|As an AI)", re.I)


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def norm(text: str) -> str:
    return " ".join(text.casefold().split())


def shingles(text: str) -> set[str]:
    words = re.findall(r"\w+", text.casefold())
    return {" ".join(words[i:i + 5]) for i in range(max(0, len(words) - 4))}


def classify(prompt: str) -> str:
    """Heuristic task tags are explicitly subject to human review."""
    p = prompt.casefold()
    if re.search(r"\b(?:python|javascript|typescript|java|c\+\+|sql|html|css|programming|debug|function|algorithm|code|script|regex|program)\b", p):
        return "programming"
    if re.search(r"\b(?:calculate|solve|equation|arithmetic|algebra|probability|mathematical|math|logic|proof|integral|derivative)\b|\d\s*[+*/=]\s*\d", p):
        return "math_logic"
    if re.search(r"\b(?:summari[sz]e|summary|summaries|assess|evaluate|review|classify|identify.the.main|main.idea)\b", p):
        return "summary_judgment"
    if re.search(r"\b(?:compare|comparison|contrast|versus|pros.and.cons|advantages|disadvantages|analy[sz]e|argument|trade.off|better)\b", p):
        return "comparison_analysis"
    return "factual_explanation"


def eligible(prompt: str, response: str, tokenizer) -> tuple[bool, str, int, int]:
    if not prompt.strip() or not response.strip():
        return False, "empty", 0, 0
    text = prompt + "\n" + response
    if "<extra_id_1>" in text or "<|" in text:
        return False, "encoded_or_special_context_not_in_first_pilot", 0, 0
    if PII.search(text):
        return False, "possible_pii", 0, 0
    if EXCLUDED.search(text) or CREATIVE.search(prompt) or REFUSAL.search(response):
        return False, "not_applicable_for_this_pilot", 0, 0
    if len(response.split()) < 25:
        return False, "too_little_explanatory_content", 0, 0
    letters = re.findall(r"[^\W\d_]", text, re.UNICODE)
    if not letters or sum(c.isascii() for c in letters) / len(letters) < 0.94:
        return False, "text_language_screen", 0, 0
    messages = [{"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}, {"role": "assistant", "content": response}]
    total = len(tokenizer.apply_chat_template(messages, tokenize=True))
    length = len(tokenizer(response, add_special_tokens=False)["input_ids"])
    if total > 920 or length > 450:
        return False, "length_reserve_for_rewrites", total, length
    return True, "eligible", total, length


def fetch_json(url: str):
    with urllib.request.urlopen(url, timeout=30) as stream:
        return json.load(stream)


def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def main():
    PRIVATE.mkdir(parents=True, exist_ok=True)
    existing = PRIVATE / "review_sources_50.jsonl"
    if existing.exists():
        rows = [json.loads(x) for x in existing.read_text().splitlines()]
        if len(rows) != 50:
            raise ValueError("Existing pilot inventory is incomplete; refusing overwrite")
        print(json.dumps({"sources": 50, "cache_reused": True, "network_calls": 0}))
        return
    started = time.monotonic()
    tokenizer = AutoTokenizer.from_pretrained(str(SNAPSHOT), local_files_only=True)
    rejected, candidates, seen_prompts, seen_responses, near, near_prompts = [], [], set(), set(), [], []
    scan_counts = Counter()

    def add(row):
        ok, reason, total, length = eligible(row["prompt"], row["original_response"], tokenizer)
        prompt_hash = digest(norm(row["prompt"]))
        response_hash = digest(norm(row["original_response"]))
        words = shingles(row["original_response"])
        prompt_words = shingles(row["prompt"])
        if ok and (prompt_hash in seen_prompts or response_hash in seen_responses):
            ok, reason = False, "exact_prompt_or_response_duplicate"
        if ok and any(len(words & other) / max(1, len(words | other)) >= 0.82 for other in near):
            ok, reason = False, "near_response_duplicate"
        if ok and len(prompt_words) >= 5 and any(len(prompt_words & other) / max(1, len(prompt_words | other)) >= 0.85 for other in near_prompts):
            ok, reason = False, "near_prompt_duplicate"
        if not ok:
            rejected.append({"source_id": row["source_id"], "dataset": row["dataset"], "reason": reason})
            return
        seen_prompts.add(prompt_hash)
        seen_responses.add(response_hash)
        near.append(words)
        near_prompts.append(prompt_words)
        row.update(group_id="group-" + prompt_hash, normalized_prompt_sha256=prompt_hash,
                   original_response_sha256=digest(row["original_response"]),
                   task=classify(row["prompt"]), task_label_method="keyword_heuristic_pending_human_review",
                   target_input_tokens=total, response_tokens=length,
                   length_bin="short" if length <= 128 else "medium" if length <= 256 else "long",
                   reserved_split="train_development", human_review="pending")
        candidates.append(row)

    # Original HelpSteer2 response corpus, not preference/disagreement files.
    help_url = f"https://huggingface.co/datasets/nvidia/HelpSteer2/resolve/{HELP_REV}/train.jsonl.gz"
    help_file = PRIVATE / "downloads" / "helpsteer2_train.jsonl.gz"
    help_file.parent.mkdir(parents=True, exist_ok=True)
    if not help_file.exists():
        with urllib.request.urlopen(help_url, timeout=30) as stream:
            raw = stream.read(14_000_001)
        if len(raw) > 14_000_000:
            raise ValueError("HelpSteer download exceeded pilot limit")
        help_file.write_bytes(raw)
    with gzip.open(help_file, "rt", encoding="utf-8") as stream:
        help_rows = [(i, json.loads(line)) for i, line in enumerate(stream)]
    random.Random(SEED).shuffle(help_rows)
    for i, r in help_rows[:1200]:
        scan_counts["helpsteer2"] += 1
        add({"source_id": f"helpsteer2-train-row-{i}", "dataset": "nvidia/HelpSteer2",
             "dataset_revision": HELP_REV, "original_split": "train", "original_row_index": i,
             "source_url": help_url, "source_license": "CC-BY-4.0", "source_author": "existing corpus response; author model not specified per row",
             "prompt": r["prompt"], "original_response": r["response"],
             "source_quality_metadata": {k: r[k] for k in ["helpfulness", "correctness", "coherence", "complexity", "verbosity"]}})

    meta = fetch_json(f"https://huggingface.co/api/datasets/allenai/WildChat-1M/revision/{WILD_REV}")
    shard_paths = sorted(x["rfilename"] for x in meta["siblings"] if x["rfilename"].endswith(".parquet") and x["rfilename"].startswith("data/"))
    random.Random(SEED).shuffle(shard_paths)
    selected_shards = shard_paths[:3]
    urls = [f"https://huggingface.co/datasets/allenai/WildChat-1M/resolve/{WILD_REV}/{p}" for p in selected_shards]
    stream = load_dataset("parquet", data_files={"train": urls}, split="train", streaming=True,
                          download_config=DownloadConfig(max_retries=1))
    stream = stream.shuffle(seed=SEED, buffer_size=128)
    seen_conversations = set()
    for index, r in enumerate(stream):
        if index >= 1500 or time.monotonic() - started > 180:
            break
        scan_counts["wildchat"] += 1
        cid = r["conversation_hash"]
        if cid in seen_conversations:
            rejected.append({"source_id": "wildchat-" + cid, "dataset": "allenai/WildChat-1M", "reason": "same_conversation_or_exact_conversation_duplicate"})
            continue
        seen_conversations.add(cid)
        turns = r["conversation"]
        if len(turns) < 2 or turns[0]["role"] != "user" or turns[1]["role"] != "assistant":
            continue
        if r.get("toxic") or r.get("redacted") or any(t.get("toxic") or t.get("redacted") for t in turns[:2]):
            continue
        if any(t.get("language") != "English" for t in turns[:2]):
            continue
        sid = f"wildchat-{cid}-turn-{turns[1].get('turn_identifier')}"
        add({"source_id": sid, "dataset": "allenai/WildChat-1M", "dataset_revision": WILD_REV,
             "original_split": "train", "conversation_hash": cid, "target_turn_index": 1,
             "target_turn_identifier": turns[1].get("turn_identifier"), "source_author": r.get("model"),
             "source_url": f"https://huggingface.co/datasets/allenai/WildChat-1M/tree/{WILD_REV}",
             "source_license": "ODC-BY", "prompt": turns[0]["content"], "original_response": turns[1]["content"]})
        counts = Counter(x["task"] for x in candidates if x["dataset"] == "allenai/WildChat-1M")
        if scan_counts["wildchat"] >= 350 and all(counts[t] >= 15 for t in TASKS):
            break
    # Fixed pool hash ranking, source quota and task coverage. Quotas remain
    # diagnostic if eligibility makes exact source/task proportions impossible.
    ranked = sorted(candidates, key=lambda x: digest(str(SEED) + x["source_id"]))
    chosen, selected_ids, source_counts = [], set(), Counter()
    quotas = {"allenai/WildChat-1M": 38, "nvidia/HelpSteer2": 12}
    for round_index in range(10):
        for task in TASKS:
            options = [x for x in ranked if x["source_id"] not in selected_ids and x["task"] == task
                       and source_counts[x["dataset"]] < quotas[x["dataset"]]]
            if not options:
                options = [x for x in ranked if x["source_id"] not in selected_ids and source_counts[x["dataset"]] < quotas[x["dataset"]]]
            if not options:
                raise ValueError("Insufficient eligible independent sources under pilot budget")
            # Spread source types rather than filling the smaller source quota first.
            options.sort(key=lambda x: (source_counts[x["dataset"]] / quotas[x["dataset"]], digest(str(SEED) + x["source_id"])))
            item = options[0].copy()
            chosen.append(item)
            selected_ids.add(item["source_id"])
            source_counts[item["dataset"]] += 1
    rng = random.Random(SEED)
    orders = ["confident_first"] * 25 + ["hedged_first"] * 25
    rng.shuffle(orders)
    for i, row in enumerate(chosen, 1):
        row.update(review_id=f"P{i:03d}", rewrite_family="A" if i % 2 else "B",
                   rewrite_output_order=orders[i - 1])
    write_jsonl(existing, chosen)
    write_jsonl(PRIVATE / "source_candidates.jsonl", candidates)
    write_jsonl(PRIVATE / "source_rejections.jsonl", rejected)
    for batch, a, b in [(1, 0, 17), (2, 17, 34), (3, 34, 50)]:
        write_jsonl(PRIVATE / f"rewrite_input_batch_{batch}.jsonl", chosen[a:b])
    write_json(BASE / "manifests" / "review_source_inventory.json", {
        "seed": SEED, "sources": len(chosen), "by_dataset": dict(source_counts),
        "by_task": dict(Counter(x["task"] for x in chosen)), "by_length": dict(Counter(x["length_bin"] for x in chosen)),
        "scanned": dict(scan_counts), "eligible_pool": len(candidates), "rejected_logged": len(rejected),
        "wildchat_native_shards": selected_shards, "wildchat_buffer": 128,
        "sampling": "bounded mixed-shard buffer shuffle followed by deterministic quota selection; not uniform population sampling",
        "grouping": "one first-turn response per conversation; exact normalized prompt/response dedup; response 5-gram Jaccard >=0.82 screened across sources",
        "development_only": True, "final_test_excluded": True, "human_review": "pending",
        "text_published": False, "elapsed_seconds": time.monotonic() - started,
        "source_records": [{k: r[k] for k in ["source_id", "dataset", "dataset_revision", "group_id", "review_id", "task", "length_bin", "original_response_sha256"]} for r in chosen]
    })
    print(json.dumps({"sources": len(chosen), "by_dataset": dict(source_counts), "by_task": dict(Counter(x["task"] for x in chosen)),
                      "by_length": dict(Counter(x["length_bin"] for x in chosen)), "scan_counts": dict(scan_counts),
                      "eligible": len(candidates), "seconds": round(time.monotonic() - started, 1)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
    # Streaming HTTP workers can remain alive during interpreter shutdown.
    # All output files are closed above; prevent a completed bounded CLI from
    # lingering indefinitely with a live remote filesystem thread pool.
    import os
    import sys
    sys.stdout.flush()
    os._exit(0)
