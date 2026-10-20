"""Cache public chat rows and screen first-turn responses without rewriting them."""
from __future__ import annotations
import concurrent.futures
import hashlib
import json
import re
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]

def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()

def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": "information-chat-research-canary/1.0"})
    with urllib.request.urlopen(request, timeout=45) as response:
        return json.load(response)

def source_screen(row, config):
    messages = row.get("messages", [])
    if len(messages) < 2 or [m.get("role") for m in messages[:2]] != ["user", "assistant"]:
        return None
    question, answer = [m["content"] for m in messages[:2]]
    words = len(answer.split())
    if not config["answer_words_min"] <= words <= config["answer_words_max"] or len(question) > config["question_chars_max"]:
        return None
    if not re.match(r"^(what|which|who|when|where|why|how|can you explain|could you explain|explain|describe|define|tell me about)\b", question, re.I):
        return None
    forbidden_question = r"\b(write|rewrite|story|poem|fiction|essay|recommend|suggest|best|should I|my |your |personal|opinion|prefer|recipe|cook|medicin|medical|patient|diagnos|treatment|therap|symptom|lawyer|legal advice|invest|stock|portfolio|tax|insurance|password|sexual|suicid|weapon|religio|God|favorite|travell?ing|visit|vacation|today|current|recent|latest|last year|next year)\b"
    if re.search(forbidden_question, question, re.I):
        return None
    if re.search(r"\b(as an AI|I (?:do not|don't|cannot|can't|am unable)|sorry|unfortunately|not have access|please provide|provide more|your specific|I recommend)\b|https?://|```|\[\d+\]", answer, re.I):
        return None
    if len(re.findall(r"(?m)^\s*(?:\d+[.)]|[-*])\s", answer)) > 5:
        return None
    return {"question": question, "original": answer, "word_count": words}

def main():
    config = json.loads((BASE / "config.json").read_text())
    root = BASE / config["private_dir"]
    raw = root / "source_cache"
    raw.mkdir(parents=True, exist_ok=True)
    meta_url = "https://huggingface.co/api/datasets/" + config["dataset_id"]
    before = fetch(meta_url)
    if before["sha"] != config["dataset_revision"]:
        raise RuntimeError("Dataset revision changed; review before changing the frozen configuration.")
    write_json(raw / "dataset_metadata.json", before)
    def page(offset):
        path = raw / f"rows_{offset:06d}.json"
        params = {"dataset": config["dataset_id"], "config": "default", "split": config["split"], "offset": offset, "length": config["page_size"]}
        url = "https://datasets-server.huggingface.co/rows?" + urllib.parse.urlencode(params)
        if not path.exists():
            write_json(path, {"source_url": url, "fetched_at": datetime.now(timezone.utc).isoformat(), "dataset_revision_checked": before["sha"], "response": fetch(url)})
        cached = json.loads(path.read_text())
        return path, cached
    candidates, manifests = [], []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for path, cached in pool.map(page, config["page_offsets"]):
            manifests.append({"file": str(path.relative_to(root)), "sha256": digest(path.read_text()), "url": cached["source_url"]})
            for item in cached["response"]["rows"]:
                source = item["row"]
                screened = source_screen(source, config)
                if screened is None:
                    continue
                candidates.append({"source_id": source["prompt_id"], "row_idx": item["row_idx"], "source_url": cached["source_url"], "source_cache_file": str(path.relative_to(root)), "raw_source_row": source, **screened,
                                   "question_sha256": digest(screened["question"]), "original_sha256": digest(screened["original"]), "manual_source_selection": "pending"})
    if fetch(meta_url)["sha"] != before["sha"]:
        raise RuntimeError("Dataset revision changed during capture.")
    by_id = {r["source_id"]: r for r in candidates}
    candidates = sorted(by_id.values(), key=lambda r: r["row_idx"])
    write_json(root / "CANDIDATES.json", candidates)
    write_json(root / "SOURCE_CAPTURE_MANIFEST.json", {"dataset": config["dataset_id"], "revision": before["sha"], "license": config["license"], "rows_screened": sum(config["page_size"] for _ in manifests), "candidates": len(candidates), "cache_files": manifests, "selection_is_purposive_not_representative": True})
    print(json.dumps({"candidates": len(candidates), "root": str(root)}))
    for r in candidates:
        print(json.dumps({"row_idx": r["row_idx"], "words": r["word_count"], "question": r["question"], "answer_start": r["original"][:160]}, ensure_ascii=False))

if __name__ == "__main__":
    main()
