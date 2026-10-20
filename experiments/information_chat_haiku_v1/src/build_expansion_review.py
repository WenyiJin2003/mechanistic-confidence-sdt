"""Build immutable, paginated local review snapshots from cached rewrites."""
from __future__ import annotations

import argparse
import html
import importlib.util
import json
import os
import random
from pathlib import Path

from run_expansion import BASE, dump, load, sha


def renderer():
    path = BASE.parents[1] / "experiments/factual_source_canary_v1/src/build_existing_dataset_review.py"
    spec = importlib.util.spec_from_file_location("local_review_renderer", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", type=Path, default=BASE / "configs/expansion_10000_v1.json")
    args = ap.parse_args()
    config = load(args.config)
    root = BASE / config["private_dir"]
    sources = load(root / "SOURCES.json")
    generated = {}
    provenance = {}
    for p in sorted((root / "provider").glob("*.parsed.json")):
        parsed = load(p)
        for row in parsed["records"]:
            if row["status"] == "ok":
                if row["id"] in generated:
                    raise RuntimeError("Duplicate generated ID")
                generated[row["id"]] = row
                request = load(p.with_name(p.name.replace(".parsed.json", ".request.json")))
                provenance[row["id"]] = {"request_sha256": request["request_sha256"], "prompt_sha256": request["prompt_sha256"], "repair_applied": False,
                    **({"generation_cache_source": row["generation_cache_source"], "cache_recovery_plan": parsed.get("recovery_plan_file")}
                       if row.get("generation_cache_source") else {}),
                    **({"output_normalization": parsed["output_normalization"]} if parsed.get("output_normalization") else {}),
                    **({"identical_duplicate_normalization": parsed["identical_duplicate_normalization"]}
                       if parsed.get("identical_duplicate_normalization") else {}),
                    **({"reviewed_empty_placeholder_normalization": parsed["reviewed_empty_placeholder_normalization"]}
                       if parsed.get("reviewed_empty_placeholder_normalization") else {}),
                    **({"local_budget_terminal_normalization": parsed["local_budget_terminal_normalization"]}
                       if parsed.get("local_budget_terminal_normalization") else {}),
                    **({"missing_status_metadata_normalization": parsed["missing_status_metadata_normalization"]}
                       if parsed.get("missing_status_metadata_normalization") else {})}
    for p in sorted(root.glob("provider_repairs*/*.parsed.json")):
        request = load(p.with_name(p.name.replace(".parsed.json", ".request.json")))
        for row in load(p)["records"]:
            if row["status"] == "ok":
                generated[row["id"]] = row
                provenance[row["id"]] = {"request_sha256": request["request_sha256"], "prompt_sha256": request["prompt_sha256"], "repair_applied": True}
            else:
                generated.pop(row["id"], None)
    triplets, reviews = [], []
    for source in sources:
        reused = source.get("reuse_canary", False)
        if not reused and source["review_id"] not in generated:
            continue
        answer = source if reused else generated[source["review_id"]]
        if source["raw_source_row"]["messages"][0]["content"] != source["question"] or source["raw_source_row"]["messages"][1]["content"] != source["original"]:
            raise RuntimeError("Source text changed")
        record = {**source, "confident": answer["confident"], "hesitant": answer["hesitant"], "writer": config["model"],
                  "audit_flags": answer.get("audit_flags", {}), "human_item_rating_received": False,
                  "user_general_canary_feedback": "positive" if reused else "not_yet_reviewed", "content_preservation_certified": False}
        if answer.get("content_review_notes"):
            record["model_assisted_content_review_notes"] = answer["content_review_notes"]
        if not reused:
            record["rewrite_provenance"] = provenance[source["review_id"]]
        triplets.append(record)
        if reused:
            continue
        high_first = random.Random(f"{config['seed']}:{source['review_id']}").getrandbits(1)
        a_role, b_role = ("confident", "hesitant") if high_first else ("hesitant", "confident")
        reviews.append({"review_id": source["review_id"], "dataset": "UltraChat · Haiku 扩量候选", "source_url": "https://huggingface.co/datasets/HuggingFaceH4/ultrachat_200k", "paper_url": "https://arxiv.org/abs/2305.14233",
                        "version_a": answer[a_role], "version_b": answer[b_role],
                        "a_metadata": {"candidate_role": a_role, "word_count": len(answer[a_role].split()), "text_sha256": sha(answer[a_role])},
                        "b_metadata": {"candidate_role": b_role, "word_count": len(answer[b_role].split()), "text_sha256": sha(answer[b_role])},
                        "reference": {"question": source["question"], "original_response": source["original"], "source_id": source["source_id"],
                                      "gold_answer": "Not provided; source answers are synthetic, not verified factual gold.", "source_model": "Source: UltraChat synthetic chat; rewrite: " + config["model"],
                                      "candidate_selection_note": "Same source-length and information-seeking filters as approved canary; exact Q/A and source group retained.",
                                      "selection_notes": answer.get("audit_flags", {}), "model_assisted_content_review": {"bounded_repair_applied": provenance[source["review_id"]]["repair_applied"], "human_certification": False,
                                          **({"content_review_notes": answer["content_review_notes"]} if answer.get("content_review_notes") else {})}}})
    ids = [r["source_id"] for r in triplets]
    if len(set(ids)) != len(ids):
        raise RuntimeError("Repeated source group")
    packet = {"protocol": config["protocol"], "target": config["target_sources"], "model": config["model"], "canary_approval_scope": config["canary_approval"],
              "human_review_completed": False, "new_triplets": len(reviews), "total_triplets": len(triplets), "triplets": triplets, "review_records": reviews}
    digest = sha(json.dumps(packet, sort_keys=True, ensure_ascii=False, separators=(",", ":")))
    out = root / "review_snapshots" / f"ready_{len(triplets):05d}_{digest[:10]}"
    out.mkdir(parents=True, exist_ok=True)
    dump(out / "TRIPLETS.json", packet)
    render = renderer().render
    links = []
    for offset in range(0, len(reviews), 100):
        group = reviews[offset:offset + 100]
        group_hash = sha(json.dumps(group, sort_keys=True, ensure_ascii=False))
        name = f"PAGE_{offset // 100 + 1:03d}.html"
        page = render(group, [{"dataset": config["dataset_id"], "selection_recipe": "Seeded, source-group-deduplicated first-turn information-seeking candidates. Original texts remain unchanged. This is not a representative random sample or a fact-certified dataset."}], group_hash,
                      title=f"新增改写审核 · {group[0]['review_id']}–{group[-1]['review_id']}",
                      introduction=f"本页 {len(group)} 条新增候选。对照 Original 检查内容保持、语气对比及自然度。A/B 方向随机，未预填人工判断。",
                      method_note="来源为 UltraChat 合成英文聊天。此前 50 条不重新生成，也不在这里要求重新审核。数字/长度检查不是语义保持认证。每个快照的检查记录独立，完成后请下载 JSON。没有自动上传或公开发布。",
                      metadata_title="查看生成方向与检查提示（建议判断后再看）",
                      metadata_note="方向来自写作指令，不是人工确认标签。原答不是经过核实的标准答案。")
        # Scope this export to rewritten triplets, not unmodified published pairs.
        page = page.replace("existing-original-pairs-human-review-v1", "haiku-expansion-human-review-v1").replace("original_dataset_", "haiku_expansion_")
        path = out / name
        if path.exists() and path.read_text() != page:
            raise RuntimeError("Refusing to overwrite a changed human review page")
        path.write_text(page, encoding="utf-8")
        links.append(f'<li><a href="{name}">{group[0]["review_id"]}–{group[-1]["review_id"]}</a> · {len(group)} 条新增</li>')
    old = BASE / config["canary_private_dir"] / "review_final_v2/REVIEW.html"
    old_link = html.escape(os.path.relpath(old, out), quote=True)
    status = load(root / "RUN_STATUS.json") if (root / "RUN_STATUS.json").exists() else {}
    index = f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>信息型聊天扩量审核</title><style>body{{max-width:850px;margin:40px auto;padding:0 20px;color:#252a30;font:17px/1.7 system-ui}}a{{color:#254b74}}li{{margin:12px 0}}small{{color:#59636e}}</style><h1>信息型聊天扩量审核</h1><p><strong>目标 {config['target_sources']:,} 条，目前生成 {len(triplets):,} 条三元组。</strong><br>包括原有 50 条和新增 {len(reviews)} 条。新增内容仍是待审核候选，不是已经通过的训练集。</p><p>已有 50 条逐字复用，<a href="{old_link}">原审核页保持不变</a>。新增样本分组如下：</p><ul>{''.join(links)}</ul><p><a href="TRIPLETS.json" download>下载当前全部三元组 JSON（含原有 50 条）</a></p><p><small>来源：UltraChat 合成英文聊天。改写：Claude Haiku。原答不是事实标准答案。此快照不会自动更新或上传。</small></p></html>'''
    (out / "INDEX.html").write_text(index, encoding="utf-8")
    result = {"total_generated_triplets": len(triplets), "new_generated_triplets": len(reviews), "reused_canary_triplets": len(triplets) - len(reviews),
              "packet_sha256": digest, "review_index": str(out / "INDEX.html"), "pages": len(links), "run_state": status.get("state"), "human_review_completed": False}
    dump(out / "MANIFEST.json", result)
    dump(root / "LATEST_REVIEW.json", result)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
