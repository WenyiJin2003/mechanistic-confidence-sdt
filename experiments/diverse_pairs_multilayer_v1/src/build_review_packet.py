"""Assemble, screen and render drafts for real human content review.

No network, model inference or automatic human-review approval is performed.
"""
from __future__ import annotations

import hashlib
import html
import json
import random
import re
from collections import Counter
from pathlib import Path

from transformers import AutoTokenizer

BASE = Path(__file__).resolve().parents[1]
PRIVATE = BASE / "private_data"
SNAPSHOT = BASE.parents[2] / "semantic-entropy-probes-stage0/cache/huggingface/models--Qwen--Qwen2.5-1.5B-Instruct/snapshots/989aa7980e4cf806f80c7fef2b1adb7bc71aa306"


def read_rows(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def screen(original: str, changed: str) -> list[str]:
    flags = []
    if not changed.strip():
        return ["empty_response"]
    fenced = re.findall(r"```[\s\S]*?```", original)
    if any(block not in changed for block in fenced):
        flags.append("code_block_changed")
    inline = re.findall(r"(?<!`)`[^`\n]+`(?!`)", original)
    if any(block not in changed for block in inline):
        flags.append("inline_code_changed")
    urls = re.findall(r"https?://[^\s<>]+", original)
    if any(url not in changed for url in urls):
        flags.append("source_url_changed")
    numbers = lambda text: Counter(re.findall(r"(?<!\w)[+-]?\d+(?:\.\d+)?%?", text))
    if numbers(original) != numbers(changed):
        flags.append("numeric_content_changed_check_manually")
    if not 0.70 <= len(changed) / max(1, len(original)) <= 1.35:
        flags.append("length_change_check_manually")
    if re.search(r"\b(?:I verified|I checked|I confirmed|I tested|I ran the code)\b", changed, re.I) and not re.search(r"\b(?:I verified|I checked|I confirmed|I tested|I ran the code)\b", original, re.I):
        flags.append("possible_added_verification")
    if re.search(r"\b(?:cannot answer|can't answer|unable to answer)\b", changed, re.I) and not re.search(r"\b(?:cannot answer|can't answer|unable to answer)\b", original, re.I):
        flags.append("possible_new_refusal")
    return flags


def render_html(rows, packet_hash, revision=1):
    def esc(text):
        return html.escape(str(text), quote=True)
    rng = random.Random(20261011)
    cards, mappings = [], []
    for i, r in enumerate(rows):
        keys = ["confident_response", "hedged_response"]
        rng.shuffle(keys)
        mapping = {"A": keys[0], "B": keys[1]}
        mappings.append({"review_id": r["review_id"], "source_id": r["source_id"],
                         "original_response_sha256": r["original_response_sha256"],
                         "confident_sha256": sha(r["confident_response"]), "hedged_sha256": sha(r["hedged_response"]),
                         "display_mapping": mapping})
        flags = "; ".join(r["automatic_flags"]) or "未发现规则检查异常；内容保持仍待你审核"
        cards.append(f'''<article class="card" data-index="{i}" {'hidden' if i else ''}>
<div class="meta"><strong>{esc(r['review_id'])}</strong> · {esc(r['task'])} · {esc(r['dataset'])} · 原文 {r['response_tokens']} tokens</div>
<details><summary>查看原始问题</summary><pre>{esc(r['prompt'])}</pre></details>
<div class="columns"><section><h2>原始回答</h2><pre>{esc(r['original_response'])}</pre></section>
<section><h2>版本 A</h2><pre>{esc(r[keys[0]])}</pre></section><section><h2>版本 B</h2><pre>{esc(r[keys[1]])}</pre></section></div>
<p class="flags">自动检查：{esc(flags)}</p>
<div class="review"><label>两个版本都保持了原内容吗？<select data-field="content_preserved"><option value="">未审核</option><option value="yes">是</option><option value="no">否，有内容变更</option><option value="uncertain">不确定</option></select></label>
<label>哪一版表达更确定？<select data-field="more_certain"><option value="">未审核</option><option value="A">A 更确定</option><option value="B">B 更确定</option><option value="tie">差别不清楚</option><option value="uncertain">无法判断</option></select></label>
<label>是否还有长度、礼貌、权威或质量差异？<select data-field="other_confound"><option value="">未审核</option><option value="no">没有明显差异</option><option value="yes">有，请在备注说明</option><option value="uncertain">不确定</option></select></label></div>
<label class="note">备注<textarea data-field="notes" placeholder="例如：B 改掉了原文条件；数字有变化；两版语气区别不明显。"></textarea></label>
<details class="provenance"><summary>来源与标签（建议判断后再展开）</summary><p>来源作者：{esc(r['source_author'])}<br>来源 ID：{esc(r['source_id'])}<br>数据版本：{esc(r['dataset_revision'])}<br>许可：{esc(r['source_license'])}<br>改写模型：GPT-6 Luna，工作会话子任务<br>版本 A：{'坚定' if keys[0]=='confident_response' else '犹豫'}；版本 B：{'坚定' if keys[1]=='confident_response' else '犹豫'}</p><a href="{esc(r['source_url'])}" target="_blank" rel="noreferrer">数据来源</a></details>
</article>''')
    metadata = json.dumps(mappings, ensure_ascii=False).replace("<", "\\u003c")
    output = '''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>50 对 certainty 改写审核</title>
<style>body{margin:0;background:#f4f5f7;color:#18202b;font:16px/1.6 system-ui,-apple-system,sans-serif}main{max-width:1600px;margin:auto;padding:24px}h1{font-size:26px;margin:0 0 8px}header p{max-width:1100px}.toolbar{display:flex;gap:12px;align-items:center;flex-wrap:wrap;position:sticky;top:0;background:#f4f5f7;padding:12px 0;z-index:2}button,select{font:inherit;padding:7px 12px;border:1px solid #bec5ce;border-radius:7px;background:white}button{cursor:pointer}.primary{background:#2352a3;color:white;border-color:#2352a3}.card{background:white;border:1px solid #dce1e7;border-radius:12px;padding:20px}.card[hidden]{display:none}.meta{color:#4b5666;margin-bottom:12px}.columns{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin-top:14px}.columns section{border:1px solid #dbe2eb;border-radius:8px;padding:14px;background:#fafbfd}.columns section:first-child{background:#f6f7f8}h2{font-size:18px;margin:0 0 10px}pre{font:15px/1.65 ui-monospace,SFMono-Regular,monospace;white-space:pre-wrap;overflow-wrap:anywhere;margin:8px 0}.flags{font-size:14px;color:#685222;background:#fff7df;padding:10px;border-radius:6px}.review{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}.review label{display:flex;flex-direction:column;gap:6px}textarea{width:100%;min-height:80px;box-sizing:border-box;font:inherit;padding:10px;border:1px solid #bec5ce;border-radius:6px}.note{display:block;margin-top:16px}summary{cursor:pointer;color:#2352a3}.provenance{font-size:14px;margin-top:16px}#progress{font-weight:600}#save-status{font-size:13px;color:#536275}@media(max-width:1000px){.columns,.review{grid-template-columns:1fr}.toolbar{position:static}}@media print{.toolbar,.review,.note{display:none}.card[hidden]{display:block}.card{break-after:page}.columns{grid-template-columns:1fr}}</style></head><body><main>
<header><h1>50 对坚定／犹豫改写：人工审核</h1><p>每条都有真实来源的原始回答，以及两个改写版本。请核对<strong>内容是否保持、确定程度是否有区别、是否混入其他文风差异</strong>。不需要判断原答案是否正确，也不要把改写改成正确答案。A/B 顺序随机，预期标签默认收起。</p><p>这是待审开发集，不是已通过审核的数据，也没有 probe 成绩。审核在本页完成，不会上传。</p></header>
<nav class="toolbar"><button id="prev">上一条</button><span id="position"></span><button id="next">下一条</button><label>跳转 <select id="jump"></select></label><span id="progress"></span><button class="primary" id="export">下载审核结果 JSON</button><span id="save-status"></span></nav>
''' + "\n".join(cards) + '''
<p>请将下载的审核结果交给我，或直接反馈有问题的 P 编号。源回答、改写和审核材料保存在本地，不在公共 GitHub 中。</p></main><script>
const packetHash=''' + json.dumps(packet_hash) + ''';
const mapping=''' + metadata + ''';
const storageKey='certainty-review-'+packetHash;
let reviews={};let current=0;let storageAvailable=true;
try{reviews=JSON.parse(localStorage.getItem(storageKey)||'{}')}catch(e){storageAvailable=false}
const cards=[...document.querySelectorAll('.card')];const jump=document.getElementById('jump');
mapping.forEach((m,i)=>{const o=document.createElement('option');o.value=i;o.textContent=m.review_id;jump.append(o)});
function progress(){const complete=mapping.filter(m=>{const r=reviews[m.review_id]||{};return r.content_preserved&&r.more_certain&&r.other_confound}).length;document.getElementById('progress').textContent='已审核 '+complete+' / '+mapping.length;document.getElementById('save-status').textContent=storageAvailable?'浏览器内保存；完成后请下载结果':'浏览器保存不可用，请及时下载结果'}
cards.forEach((card,i)=>{card.querySelectorAll('[data-field]').forEach(el=>{el.value=(reviews[mapping[i].review_id]||{})[el.dataset.field]||'';el.addEventListener('input',()=>{const id=mapping[i].review_id;reviews[id] ||= {};reviews[id][el.dataset.field]=el.value;reviews[id].updated_at=new Date().toISOString();try{localStorage.setItem(storageKey,JSON.stringify(reviews))}catch(e){storageAvailable=false}progress()})})});
function show(i){current=Math.max(0,Math.min(cards.length-1,i));cards.forEach((c,n)=>c.hidden=n!==current);jump.value=current;document.getElementById('position').textContent=(current+1)+' / '+cards.length;document.getElementById('prev').disabled=current===0;document.getElementById('next').disabled=current===cards.length-1;window.scrollTo(0,0)}
document.getElementById('prev').onclick=()=>show(current-1);document.getElementById('next').onclick=()=>show(current+1);jump.onchange=()=>show(Number(jump.value));
document.getElementById('export').onclick=()=>{const payload={packet_sha256:packetHash,reviewer:'user',exported_at:new Date().toISOString(),reviews:mapping.map(m=>({...m,...(reviews[m.review_id]||{}),human_review:(reviews[m.review_id]?.content_preserved&&reviews[m.review_id]?.more_certain&&reviews[m.review_id]?.other_confound)?'annotated':'pending'}))};const url=URL.createObjectURL(new Blob([JSON.stringify(payload,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='human_review_50.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)};
show(0);progress();
</script></body></html>'''
    if revision == 2:
        output = output.replace("<h1>50 对坚定／犹豫改写：人工审核</h1>", f"<h1>50 对坚定／犹豫改写：人工审核 · V{revision}</h1><p>新版根据你的反馈加强了犹豫语气。坚定版和来源原文保持不变。A/B 仍随机排列，并非每条 B 都是犹豫版；请对新版重新审核。</p>")
    elif revision == 3:
        output = output.replace("<h1>50 对坚定／犹豫改写：人工审核</h1>", "<h1>50 对坚定／犹豫改写：人工审核 · V3</h1><p>本版根据 agent-assisted QA 定向修正了 10 条内容或文风问题；坚定版和来源原文保持不变。该 QA 不是人工审核。A/B 仍随机排列，并非每条 B 都是犹豫版；如需正式人工确认，请审核本版。</p>")
    return output


def apply_hedge_revisions(written, revisions):
    """Replace one field only, after exact source identity checks."""
    if len(revisions) != len(written) or len({r["review_id"] for r in revisions}) != len(written):
        raise ValueError("Incomplete or duplicate hedge revisions")
    by_review = {r["review_id"]: r for r in revisions}
    result = []
    for draft in written:
        revised = by_review[draft["review_id"]]
        if revised["source_id"] != draft["source_id"] or revised["original_response_sha256"] != draft["original_response_sha256"]:
            raise ValueError("Hedge revision changes source identity")
        if not revised["hedged_response"].strip():
            raise ValueError("Empty hedge revision")
        # The revision model never supplies confident text; copying it from the
        # original draft makes unchanged confidence an enforceable invariant.
        result.append({**draft, "previous_hedged_sha256": sha(draft["hedged_response"]),
                       "previous_writer_issues": draft.get("writer_issues", []),
                       "hedged_response": revised["hedged_response"], "hedge_revision": 2,
                       "hedge_rewriter_model_requested": revised["rewriter_model_requested"],
                       "hedge_revision_writer_notes": revised.get("revision_writer_notes", ""),
                       "writer_issues": [x for x in draft.get("writer_issues", []) if "source" in x.lower()]
                       + revised.get("revision_writer_issues", []), "human_review": "pending"})
    return result


def apply_targeted_corrections(written, corrections):
    """Apply the predeclared agent-QA correction set without touching other rows."""
    expected = {"P009", "P017", "P022", "P039", "P041", "P042", "P044", "P045", "P047", "P049"}
    by_id = {r["review_id"]: r for r in corrections}
    if len(corrections) != len(by_id) or set(by_id) != expected:
        raise ValueError("Incomplete, duplicate or unexpected agent-QA corrections")
    result = []
    for draft in written:
        if draft["review_id"] not in by_id:
            result.append(draft)
            continue
        corrected = by_id[draft["review_id"]]
        if (corrected["source_id"] != draft["source_id"] or
                corrected["original_response_sha256"] != draft["original_response_sha256"]):
            raise ValueError("Agent-QA correction changes source identity")
        if not corrected["hedged_response"].strip():
            raise ValueError("Empty agent-QA hedge correction")
        result.append({**draft, "revision_2_hedged_sha256": sha(draft["hedged_response"]),
                       "hedged_response": corrected["hedged_response"], "hedge_revision": 3,
                       "agent_qa_correction_reason": corrected["correction_reason"],
                       "agent_qa_model_requested": corrected["rewriter_model_requested"],
                       "agent_qa_reasoning_effort": corrected["reasoning_effort"],
                       "human_review": "pending"})
    return result


def main():
    originals = read_rows(PRIVATE / "review_sources_50.jsonl")
    written = []
    for i in range(1, 4):
        written += read_rows(PRIVATE / f"rewrite_output_batch_{i}.jsonl")
    replacement_file = PRIVATE / "rewrite_output_replacements.jsonl"
    if replacement_file.exists():
        replacements = read_rows(replacement_file)
        replaced_ids = {r["review_id"] for r in replacements}
        written = [r for r in written if r["review_id"] not in replaced_ids] + replacements
    revision = 1
    hedge_files = [PRIVATE / f"stronger_hedges_output_batch_{i}.jsonl" for i in range(1, 4)]
    if any(p.exists() for p in hedge_files):
        if not all(p.exists() for p in hedge_files):
            raise ValueError("Hedge revision batches are incomplete; retaining the previous packet")
        written = apply_hedge_revisions(written, [r for p in hedge_files for r in read_rows(p)])
        revision = 2
        original_packet = read_rows(PRIVATE / "review_revision_1" / "PAIRED_RESPONSES_50.jsonl")
        original_by_id = {r["review_id"]: r for r in original_packet}
        for row in written:
            old = original_by_id[row["review_id"]]
            if row["confident_response"] != old["confident_response"]:
                raise ValueError("Confident response changed in hedge-only revision")
    correction_files = [PRIVATE / f"agent_qa_correction_output_batch_{i}.jsonl" for i in range(1, 4)]
    if any(p.exists() for p in correction_files):
        if not all(p.exists() for p in correction_files):
            raise ValueError("Agent-QA correction batches are incomplete; retaining revision 2")
        archive = PRIVATE / "review_revision_2_before_agent_qa" / "PAIRED_RESPONSES_50.jsonl"
        if not archive.exists():
            raise ValueError("Revision 2 archive is required before targeted corrections")
        revision_2 = read_rows(archive)
        revision_2_by_id = {r["review_id"]: r for r in revision_2}
        written = apply_targeted_corrections(written, [r for p in correction_files for r in read_rows(p)])
        revision = 3
        for row in written:
            if row["confident_response"] != revision_2_by_id[row["review_id"]]["confident_response"]:
                raise ValueError("Confident response changed in agent-QA correction")
    by_id = {r["source_id"]: r for r in written}
    if len(written) != 50 or len(by_id) != 50 or set(by_id) != {r["source_id"] for r in originals}:
        raise ValueError("Missing or duplicate writer records; refusing incomplete packet")
    tokenizer = AutoTokenizer.from_pretrained(str(SNAPSHOT), local_files_only=True)
    assembled = []
    for source in originals:
        draft = by_id[source["source_id"]]
        if draft["original_response_sha256"] != source["original_response_sha256"] or draft["review_id"] != source["review_id"]:
            raise ValueError("Source hash or review identity mismatch")
        flags = []
        token_stats = {}
        for label in ["confident_response", "hedged_response"]:
            value = draft[label]
            flags += [label + ":" + f for f in screen(source["original_response"], value)]
            ids = tokenizer(value, add_special_tokens=False)["input_ids"]
            messages = [{"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": source["prompt"]}, {"role": "assistant", "content": value}]
            full_count = len(tokenizer.apply_chat_template(messages, tokenize=True))
            token_stats[label] = {"response_tokens": len(ids), "full_input_tokens": full_count}
            if len(ids) > 512 or full_count > 1024:
                flags.append(label + ":token_limit_exceeded")
        if draft["confident_response"] == draft["hedged_response"]:
            flags.append("identical_pair")
        flags += ["writer_issue:" + str(x) for x in draft.get("writer_issues", [])]
        assembled.append({**source, **draft, "automatic_flags": flags, "token_stats": token_stats, "human_review": "pending"})
    dump = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in assembled)
    packet_hash = sha(dump)
    (PRIVATE / "PAIRED_RESPONSES_50.jsonl").write_text(dump, encoding="utf-8")
    (PRIVATE / "PAIR_QA_50.jsonl").write_text("".join(json.dumps({"review_id": r["review_id"], "source_id": r["source_id"], "flags": r["automatic_flags"], "human_review": "pending"}) + "\n" for r in assembled), encoding="utf-8")
    html_file = PRIVATE / "REVIEW_50_PAIRS.html"
    page_html = render_html(assembled, packet_hash, revision)
    html_file.write_text(page_html, encoding="utf-8")
    if revision > 1:
        (PRIVATE / f"REVIEW_50_PAIRS_V{revision}.html").write_text(page_html, encoding="utf-8")
    aggregate = {"pairs": 50, "rewritten_responses": 100, "rewriter_model": "gpt-6-luna", "invocation": "current_codex_session_subagent",
                 "human_review": "pending", "independent_paid_api_calls": 0, "model_revision": None,
                 "automatic_flags_count": sum(bool(r["automatic_flags"]) for r in assembled),
                 "flagged_review_ids": [r["review_id"] for r in assembled if r["automatic_flags"]],
                 "flags_by_type": dict(Counter(f.split(":", 1)[-1] for r in assembled for f in r["automatic_flags"])),
                 "tasks": dict(Counter(r["task"] for r in assembled)), "sources": dict(Counter(r["dataset"] for r in assembled)),
                 "source_response_token_proxy": sum(r["response_tokens"] for r in assembled),
                 "rewrite_response_token_proxy": sum(v["response_tokens"] for r in assembled for v in r["token_stats"].values()),
                 "token_proxy_model": "Qwen2.5 tokenizer; not OpenAI billable tokens", "packet_sha256": packet_hash,
                 "confidence_readout_fitted": False, "representation_forward_calls": 0, "text_published": False}
    aggregate.update(review_revision=revision, confident_responses_unchanged=(revision >= 2),
                     initial_review_preserved=(revision >= 2),
                     agent_assisted_qa=(revision >= 3), agent_qa_is_human_review=False,
                     targeted_agent_qa_corrections=(10 if revision >= 3 else 0),
                     most_common_hedged_openings=Counter(" ".join(re.findall(r"\w+", r["hedged_response"].lower())[:5]) for r in assembled).most_common(5))
    (BASE / "manifests" / "rewrite_review_50_summary.json").write_text(json.dumps(aggregate, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(aggregate))


if __name__ == "__main__":
    main()
