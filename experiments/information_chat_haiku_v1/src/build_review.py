"""Assemble provider-authenticated triplets, diagnostic flags, and a local review."""
from __future__ import annotations
import hashlib
import importlib.util
import json
import random
import re
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from prepare_sources import BASE, digest, write_json

NUMBER = re.compile(r"(?<![\w])\d+(?:[,.]\d+)*(?:%|°[CF])?")
STYLE_REVIEW_NOTES = {
    "HC002": "Check whether hedging the motion of an already-described moving object sounds natural.",
    "HC006": "Check the fluency of stacked modal/frequency wording such as may often.",
    "HC013": "Check whether the historical paragraph contains too many nested hedges.",
    "HC020": "Check contrast across the whole response, not only the opening and conclusion.",
    "HC032": "Check stacked qualifications such as can likely be roughly grouped.",
    "HC037": "Check whether uncertainty is placed on the intended answer rather than awkwardly on a person's category.",
    "HC039": "Check the phrasing and placement of the hedge in the logo description.",
}

def numbers(text):
    text = re.sub(r"(?m)^\s*\d+[.)]\s+", "", text)
    return Counter(NUMBER.findall(text))

def audit(source, rewrite):
    flags = []
    if numbers(source) != numbers(rewrite):
        flags.append("numeric_token_difference_check_manually")
    ratio = len(rewrite.split()) / len(source.split())
    if ratio < .70 or ratio > 1.40:
        flags.append("length_change_check_for_omission_or_padding")
    if re.search(r"\bI (?:can state|stand|am certain|am uncertain|am confident|am not confident)\b|(?:this answer|this explanation) as presented", rewrite, re.I):
        flags.append("detachable_certainty_boilerplate")
    if re.search(r"\b(?:I (?:checked|verified|confirmed)|verified sources|after checking|evidence proves|undeniably|without any doubt|absolutely certain)\b", rewrite, re.I):
        flags.append("potential_invented_evidence_or_exaggeration")
    return flags

class Readback(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.reading = False
        self.buffer = ""
        self.responses = []
    def handle_starttag(self, tag, attrs):
        if tag == "div" and "response" in dict(attrs).get("class", "").split():
            self.reading, self.buffer = True, ""
    def handle_data(self, data):
        if self.reading:
            self.buffer += data
    def handle_endtag(self, tag):
        if tag == "div" and self.reading:
            self.responses.append(self.buffer)
            self.reading = False

def main():
    config = json.loads((BASE / "config.json").read_text())
    root = BASE / config["private_dir"]
    sources = json.loads((root / "SOURCES_50.json").read_text())
    batches = sorted((root / config.get("provider_dir", "provider")).glob("batch_*.parsed.json"))
    if len(batches) != 10:
        raise RuntimeError(f"Expected 10 completed batches, found {len(batches)}")
    generated = {}
    total_cost, model_usage = 0., Counter()
    for path in batches:
        batch = json.loads(path.read_text())
        total_cost += batch.get("api_equivalent_usd") or 0
        for model, usage in batch["model_usage"].items():
            model_usage[model] += usage.get("outputTokens", 0)
        for row in batch["records"]:
            if row["id"] in generated:
                raise RuntimeError("Duplicate rewrite ID")
            generated[row["id"]] = row
    repairs = {}
    plan = json.loads((BASE / "repair_plan_v1.json").read_text())
    expected_repairs = {r["id"] for r in plan["repairs"]}
    for path in sorted((root / "provider_repairs_v1").glob("*.parsed.json")):
        batch = json.loads(path.read_text())
        for row in batch["records"]:
            if row["id"] in repairs:
                raise RuntimeError("Duplicate repair ID")
            repairs[row["id"]] = row
    if set(repairs) != expected_repairs:
        raise RuntimeError("Content-preservation repair pass is incomplete")
    second_pass = root / "provider_repairs_v2/batch_01.parsed.json"
    if not second_pass.exists():
        raise RuntimeError("Final HC040 content correction is incomplete")
    last = json.loads(second_pass.read_text())["records"]
    if len(last) != 1 or last[0]["id"] != "HC040" or last[0]["hesitant"] != repairs["HC040"]["hesitant"]:
        raise RuntimeError("Unexpected final correction ID or change to already-reviewed hesitant version")
    repairs["HC040"] = last[0]
    final_correction = json.loads((root / "provider_repairs_v3/batch_01.parsed.json").read_text())["records"]
    if len(final_correction) != 1 or final_correction[0]["id"] != "HC041":
        raise RuntimeError("Unexpected final predicate correction")
    prior = repairs["HC041"]
    corrected = final_correction[0]
    assert corrected["confident"] == prior["confident"].replace("enforced its purity", "ensured its purity")
    assert corrected["hesitant"] == prior["hesitant"].replace("sought to preserve its purity", "seems to have ensured its purity")
    repairs["HC041"] = corrected
    for identifier, revised in repairs.items():
        generated[identifier] = revised
    roles = [True] * 25 + [False] * 25
    random.Random(config["seed"]).shuffle(roles)
    triplets, reviews = [], []
    for source, high_first in zip(sources, roles):
        row = generated[source["review_id"]]
        if row["status"] != "ok":
            raise RuntimeError(f"Rejected source {row['id']}; do not silently replace it")
        assert source["raw_source_row"]["messages"][0]["content"] == source["question"]
        assert source["raw_source_row"]["messages"][1]["content"] == source["original"]
        assert digest(source["original"]) == source["original_sha256"]
        flagged = {role: audit(source["original"], row[role]) for role in ["confident", "hesitant"]}
        triplets.append({**source, "confident": row["confident"], "hesitant": row["hesitant"], "writer": config["model"], "repair_applied": row["id"] in repairs,
                         "audit_flags": flagged, "human_review_completed": False, "content_preservation_certified": False})
        a_role, b_role = ("confident", "hesitant") if high_first else ("hesitant", "confident")
        reviews.append({"review_id": row["id"], "dataset": "UltraChat 200k · Haiku 改写候选", "source_url": "https://huggingface.co/datasets/HuggingFaceH4/ultrachat_200k", "paper_url": "https://arxiv.org/abs/2305.14233",
                        "version_a": row[a_role], "version_b": row[b_role], "a_metadata": {"candidate_role": a_role, "text_sha256": digest(row[a_role]), "word_count": len(row[a_role].split())},
                        "b_metadata": {"candidate_role": b_role, "text_sha256": digest(row[b_role]), "word_count": len(row[b_role].split())},
                        "reference": {"question": source["question"], "original_response": source["original"], "source_id": source["source_id"], "gold_answer": "Not provided: original response is not verified factual gold.",
                                      "source_model": "UltraChat source: ChatGPT synthetic chat; rewrites: " + config["model"], "candidate_selection_note": "50 purposefully selected first-turn information-seeking responses. Entire original is retained.", "selection_notes": flagged,
                                      "model_assisted_contrast_review": {"status": "assistant_only_not_human_rating", "manual_check_hint": STYLE_REVIEW_NOTES.get(row["id"], "No specific style issue flagged; still requires human judgment.")}}})
    packet = {"protocol": config["protocol"], "model": config["model"], "dataset": config["dataset_id"], "revision": config["dataset_revision"], "triplets": triplets,
              "review_records": reviews, "human_review_completed": False, "content_preservation_certified": False, "source_text_unmodified": True}
    packet_json = json.dumps(packet, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    packet_hash = digest(packet_json)
    renderer = BASE.parents[1] / "experiments/factual_source_canary_v1/src/build_existing_dataset_review.py"
    spec = importlib.util.spec_from_file_location("source_review_renderer", renderer)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    page = module.render(reviews, [{"dataset": config["dataset_id"], "selection_recipe": "First user message and first assistant response retained verbatim. 4,000 public rows screened, 50 purposively selected; source revision and raw row caches recorded. Not a random sample. No new questions or source answers generated."}], packet_hash,
                         title="50 条信息型回答：Haiku 坚定／犹豫改写",
                         introduction="HC001–HC050，共 50 个三元组。每条展示原始问题、未改写的 Original，以及顺序随机的 A/B 改写。请检查内容是否保持、哪版更坚定，以及对比是否自然明显。尚未人工审核通过。",
                         method_note="来源是公开的 UltraChat 合成英文对话，不是真实用户日志，也不是经核实的事实答案库。改写仅由指定 Haiku 版本产生，原答没有截短或修正。数字及长度检查只能提示风险，不能证明事实保持。检查进度留在此浏览器，可下载 JSON，不会自动上传。",
                         metadata_title="查看生成方向、来源与自动检查提示（建议判断后再看）",
                         metadata_note="生成方向是给写作模型的目标，不是人工确认标签。这里没有人工 confidence 评分；原回答也不等于标准答案。请直接对照 Original 判断是否改了事实、范围或因果关系。")
    readback = Readback()
    readback.feed(page)
    expected = [r[k] for r in reviews for k in ["version_a", "version_b"]]
    assert readback.responses == expected, "HTML changed a generated response"
    assert not re.search(r"__(?:TITLE|IDS|HASH|INTRODUCTION|METHOD_NOTE)__", page)
    out = root / "review_final_v2"
    out.mkdir(exist_ok=True)
    target = out / "REVIEW.html"
    if target.exists() and target.read_text() != page:
        raise RuntimeError("Refusing to overwrite a different review: preserve existing human annotations")
    target.write_text(page, encoding="utf-8")
    write_json(out / "TRIPLETS_50.json", packet)
    all_calls = [json.loads(p.read_text()) for p in root.glob("provider*/*.raw.json")]
    cli_cost = sum(c.get("total_cost_usd", 0) for c in all_calls)
    public_cost = 0.
    token_totals = Counter()
    for call in all_calls:
        for model, usage in call.get("modelUsage", {}).items():
            # Separate the CLI's inferred cost table from current published API
            # rates. Include its small Haiku auxiliary calls and failed attempts.
            rates = (.10, .50, .20, .01) if model == "claude-haiku-5-5" else (1., 5., 2., .10)
            for field, rate in zip(["inputTokens", "outputTokens", "cacheCreationInputTokens", "cacheReadInputTokens"], rates):
                public_cost += usage.get(field, 0) * rate / 1_000_000
                token_totals[f"{model}:{field}"] += usage.get(field, 0)
    summary = {"triplets": 50, "rewrites": 100, "writer": config["model"], "model_output_tokens_initial_generation": dict(model_usage), "initial_generation_cli_cost_estimate_usd": total_cost,
               "all_attempts_cli_cost_estimate_usd": cli_cost, "repriced_public_api_estimate_usd_including_failures_and_helpers": public_cost,
               "public_pricing_source": "https://platform.claude.com/docs/en/about-claude/pricing", "pricing_checked_date": "2026-10-19",
               "public_price_assumption": "Current <=100k prompt token rates; cache writes conservatively priced at 1-hour rate. CLI internal model usage may differ from invoiced metering. Neither number is an invoice.",
               "all_attempts_token_counts": dict(token_totals), "provider_calls_including_failed_initial_attempt": len(all_calls), "bounded_repair_sources": sorted(repairs),
               "is_actual_invoice": False, "human_review_completed": False, "content_preservation_certified": False, "originals_verified_against_cached_rows": 50,
               "html_rewrites_verified_verbatim": 100, "diagnostic_flagged_source_ids": [t["review_id"] for t in triplets if any(t["audit_flags"].values())],
               "assistant_style_review_hints": STYLE_REVIEW_NOTES,
               "packet_semantic_sha256": packet_hash, "html_sha256": digest(page), "review_file": str(target)}
    write_json(out / "MANIFEST.json", summary)
    print(json.dumps(summary, ensure_ascii=False))

if __name__ == "__main__":
    main()
