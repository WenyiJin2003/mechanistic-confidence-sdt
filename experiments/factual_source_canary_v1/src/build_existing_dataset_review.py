"""Present unmodified published response pairs for local human inspection.

Inputs are source-bound JSON extractions, not writer outputs. Nothing here
generates, repairs, trims, or paraphrases a source response.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import random
from collections import Counter
from pathlib import Path


FIELDS = ("content_equivalence", "more_certain", "contrast")
BASE = Path(__file__).resolve().parents[1]


def sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def dataset_label(value: str) -> str:
    if value.startswith("Steyvers"):
        return "Steyvers et al. (2025)"
    if value.startswith("LACIE"):
        return "LACIE (NeurIPS 2024)"
    if value.startswith("Stanford") or value.startswith("tatsu-lab"):
        return "Stanford LC (ICML 2024)"
    return "Linguistic Uncertainty (2025)" if value.startswith("Linguistic") else value


def select_field(field: str, label: str, options: list[tuple[str, str]]) -> str:
    choices = '<option value="">请选择</option>'
    choices += "".join(f'<option value="{esc(k)}">{esc(v)}</option>' for k, v in options)
    return f'<label>{label}<select data-field="{field}">{choices}</select></label>'


def render(records: list[dict], sources: list[dict], packet_hash: str, *,
           title: str = "两套现成数据的原始样本",
           introduction: str = "各 10 对，共 20 对。问题与回答逐字摘录，没有改写或修正。A/B 顺序已打乱。请先检查事实内容和语气，再展开来源标签。",
           method_note: str = "这是供人工检查的样本，不是已通过内容一致性审核的数据。Steyvers 保留来源 low/high 标签；另一套按人工均分筛选高低，不能把这两种标签当成同一测量。样本用于观察问题，不用于估计整个数据集的通过率。",
           metadata_title: str = "查看原始标签、评分与来源（建议判断后再看）",
           metadata_note: str = "评分反映原始评分者感受到的语言置信度，不是模型内部信心或事实正确性的认证。参考答案来自原数据，未在本次筛选中逐条核实。") -> str:
    cards = []
    for i, row in enumerate(records):
        ref = row["reference"]
        original_block = ""
        if ref.get("original_response") is not None:
            original_block = f'<details open><summary>Original · 原始回答（未改写）</summary><div class="question verbatim">{esc(ref["original_response"])}</div></details><br>'
        question_heading = "原始任务提示" if ref.get("question_kind") == "published_paragraph_generation_prompt" else "原始问题"
        visible_keys = {"original_role", "column", "cell", "annotation_mean", "source_csv_row", "intended_level", "valid_confidence_score_count", "confidence_scores",
                        "candidate_role", "original_id", "source_record_number", "listener_acceptance_probability", "word_count", "text_sha256", "body_offset", "body_end", "source_url", "source_config"}
        metadata = {
            "dataset": row["dataset"],
            "source_id": ref["source_id"],
            "reference_answer": ref["gold_answer"],
            "version_a_original_metadata": {k: v for k, v in row["a_metadata"].items() if k in visible_keys},
            "version_b_original_metadata": {k: v for k, v in row["b_metadata"].items() if k in visible_keys},
        }
        for k in ("domain", "excel_row", "sheet", "source_model", "source_human_answer_correct"):
            if k in ref:
                metadata[k] = ref[k]
        if "model_assisted_content_review" in ref:
            metadata["model_assisted_content_review"] = ref["model_assisted_content_review"]
        if "model_assisted_contrast_review" in ref:
            metadata["model_assisted_contrast_review"] = ref["model_assisted_contrast_review"]
        for key in ("candidate_selection_note", "content_concern", "contrast_concern", "selection_notes", "source_question_note"):
            if key in ref:
                metadata[key] = ref[key]
        controls = select_field("content_equivalence", "1. 两版的事实内容是否一致？", [
            ("same", "一致：事实、解释和范围相同"),
            ("same_answer_different_details", "答案相同，但解释或细节不同"),
            ("different_answer", "答案或核心事实不同"),
            ("uncertain", "无法判断"),
        ])
        controls += select_field("more_certain", "2. 哪一版说得更坚定？", [
            ("a", "Version A"), ("b", "Version B"),
            ("tie", "差不多"), ("uncertain", "无法判断"),
        ])
        controls += select_field("contrast", "3. 坚定和犹豫的区别是否明显？", [
            ("clear", "明显"), ("weak", "有一点，但不够明显"),
            ("none", "没有明显区别"), ("uncertain", "无法判断"),
        ])
        cards.append(f'''<article class="card" data-id="{esc(row['review_id'])}" {'hidden' if i else ''}>
<div class="meta">{esc(row['review_id'])} · {esc(dataset_label(row['dataset']))}</div>
<h2>{question_heading}</h2><div class="question verbatim">{esc(ref['question'])}</div>
{original_block}<div class="versions"><section><h2>Version A</h2><div class="response verbatim">{esc(row['version_a'])}</div></section>
<section><h2>Version B</h2><div class="response verbatim">{esc(row['version_b'])}</div></section></div>
<div class="review-grid">{controls}</div>
<label class="notes">备注<textarea data-field="notes" placeholder="例如：某个事实变了、语气区别太弱、固定词太多。"></textarea></label>
<details><summary>{esc(metadata_title)}</summary>
<p>{esc(metadata_note)}</p>
<pre>{esc(json.dumps(metadata, ensure_ascii=False, indent=2))}</pre>
<a href="{esc(row['source_url'])}" target="_blank" rel="noopener">原始数据</a> · <a href="{esc(row['paper_url'])}" target="_blank" rel="noopener">论文</a></details>
</article>''')
    choices = "".join(f'<option value="{i}">{esc(r["review_id"])} · {esc(dataset_label(r["dataset"]))}</option>' for i, r in enumerate(records))
    methods = "".join(f'<p><strong>{esc(s["dataset"])}</strong></p><pre>{esc(json.dumps(s["selection_recipe"], ensure_ascii=False, indent=2) if isinstance(s["selection_recipe"], dict) else s["selection_recipe"])}</pre>' for s in sources)
    ids_json = json.dumps([r["review_id"] for r in records])
    page = '''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title><style>
*{box-sizing:border-box}body{margin:0;background:#f6f7f8;color:#20252b;font:16px/1.6 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
main{max-width:1320px;margin:auto;padding:24px}h1{font-size:25px;margin:0 0 8px}h2{font-size:16px;margin:0 0 8px}
.intro{margin:0;color:#4b5563;max-width:1100px}.toolbar{display:flex;gap:10px;align-items:center;flex-wrap:wrap;padding:15px 0;position:sticky;top:0;background:#f6f7f8;z-index:2}
button,select{font:inherit;background:white;border:1px solid #c9ced4;border-radius:5px;padding:7px 10px}button{cursor:pointer}button:disabled{cursor:default;opacity:.4}
#jump{max-width:100%;width:390px;min-width:0}#progress{margin-left:auto;font-size:14px;color:#53606c}.card{background:white;border:1px solid #dce0e5;border-radius:8px;padding:22px}.card[hidden]{display:none}
.meta{color:#68707b;font-size:14px;margin-bottom:14px}.question{margin-bottom:18px}.verbatim{white-space:pre-wrap;overflow-wrap:anywhere}
.versions{display:grid;grid-template-columns:1fr 1fr;gap:20px}.versions section{border:1px solid #dbe0e6;background:#fafbfc;border-radius:6px;padding:18px}.response{font-size:18px;line-height:1.75}
.review-grid{display:grid;grid-template-columns:1.4fr 1fr 1.2fr;gap:15px;margin-top:24px}label{display:flex;flex-direction:column;gap:7px;font-size:14px}label select{width:100%;font-size:15px}.notes{margin-top:16px}
textarea{font:inherit;min-height:72px;padding:10px;border:1px solid #c9ced4;border-radius:5px;resize:vertical}details{margin-top:22px;color:#59636e;font-size:14px}summary{cursor:pointer}pre{font-size:12px;white-space:pre-wrap;overflow-wrap:anywhere}
.bottom{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-top:16px}.primary{background:#254b74;color:white;border-color:#254b74}a{color:#25527e}#save-status{font-size:13px;color:#59636e}
@media(max-width:850px){main{padding:14px}.versions,.review-grid{grid-template-columns:1fr}.response{font-size:17px}.toolbar{position:static}#progress{margin-left:0}.card{padding:16px}}
@media print{.toolbar,.bottom,.review-grid,.notes{display:none!important}.card[hidden]{display:block}.card{break-inside:avoid;margin-bottom:20px}details{display:none}}
</style></head><body><main>
<h1>__TITLE__</h1>
<p class="intro">__INTRODUCTION__</p>
<nav class="toolbar"><button id="prev">上一对</button><select id="jump">''' + choices + '''</select><button id="next">下一对</button><span id="progress"></span></nav>
''' + "\n".join(cards) + '''
<div class="bottom"><button class="primary" id="export">下载我的检查结果</button><span id="save-status"></span></div>
<details><summary>抽样方法与使用说明</summary>
<p>__METHOD_NOTE__</p>
''' + methods + '''<p>检查项会尝试保存在当前浏览器中。检查后请下载结果；使用另一浏览器或清理缓存不会保留进度。</p></details>
</main><script>
const ids=__IDS__,packetHash=__HASH__,key='existing-source-review:'+packetHash;
const cards=Array.from(document.querySelectorAll('.card')),jump=document.getElementById('jump');
let active=0,reviews={},storageOK=true;
try{reviews=JSON.parse(localStorage.getItem(key)||'{}')}catch(e){storageOK=false}
function updateProgress(){const done=ids.filter(id=>['content_equivalence','more_certain','contrast'].every(k=>(reviews[id]||{})[k])).length;document.getElementById('progress').textContent='已检查 '+done+' / '+ids.length;document.getElementById('save-status').textContent=storageOK?'已自动保存在当前浏览器；完成后请下载。':'浏览器无法自动保存，请下载检查结果。'}
function show(index){active=Math.max(0,Math.min(cards.length-1,index));cards.forEach((c,i)=>c.hidden=i!==active);jump.value=String(active);document.getElementById('prev').disabled=active===0;document.getElementById('next').disabled=active===cards.length-1}
cards.forEach(card=>card.querySelectorAll('[data-field]').forEach(el=>{const id=card.dataset.id;el.value=(reviews[id]||{})[el.dataset.field]||'';el.addEventListener('input',()=>{reviews[id]||={};reviews[id][el.dataset.field]=el.value;reviews[id].updated_at=new Date().toISOString();try{localStorage.setItem(key,JSON.stringify(reviews))}catch(e){storageOK=false}updateProgress()})}));
document.getElementById('prev').onclick=()=>show(active-1);document.getElementById('next').onclick=()=>show(active+1);jump.onchange=()=>show(Number(jump.value));
document.getElementById('export').onclick=()=>{const payload={schema:'existing-original-pairs-human-review-v1',packet_sha256:packetHash,source_texts_unmodified:true,exported_at:new Date().toISOString(),reviews:ids.map(id=>({review_id:id,...(reviews[id]||{})}))};const url=URL.createObjectURL(new Blob([JSON.stringify(payload,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='original_dataset_'+ids.length+'pairs_review.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)};
show(0);updateProgress();
</script></body></html>'''
    return page.replace("__IDS__", ids_json).replace("__HASH__", json.dumps(packet_hash)).replace("__TITLE__", esc(title)).replace("__INTRODUCTION__", esc(introduction)).replace("__METHOD_NOTE__", esc(method_note))


def build(inputs: list[Path], output: Path, seed: int) -> dict:
    if not output.resolve().is_relative_to((BASE / "private_data").resolve()):
        raise ValueError("original response extracts must stay under private_data")
    if (output / "REVIEW.html").exists():
        raise FileExistsError("Use a new review folder instead of overwriting an existing review")
    sources, records = [], []
    rng = random.Random(seed)
    for source_path in inputs:
        source = json.loads(source_path.read_text(encoding="utf-8"))
        if len(source["records"]) != 10:
            raise ValueError(f"Expected ten source records: {source_path}")
        if len({r["question"] for r in source["records"]}) != 10:
            raise ValueError("Each dataset must contribute ten distinct questions")
        source_info = {k: v for k, v in source.items() if k != "records"}
        source_info["extraction_sha256"] = hashlib.sha256(source_path.read_bytes()).hexdigest()
        sources.append(source_info)
        roles = ["high"] * 5 + ["low"] * 5
        rng.shuffle(roles)
        for source_record, role_a in zip(source["records"], roles):
            role_b = "low" if role_a == "high" else "high"
            a, b = source_record[role_a], source_record[role_b]
            if not all(isinstance(x["text"], str) and x["text"] for x in (a, b)) or a["text"] == b["text"]:
                raise ValueError("Pair requires two nonempty distinct original strings")
            records.append({
                "review_id": source_record["review_id"],
                "dataset": source["dataset"],
                "source_url": source["source_url"],
                "paper_url": source["paper_url"],
                "reference": {k: v for k, v in source_record.items() if k not in ("high", "low")},
                "version_a": a["text"], "version_b": b["text"],
                "a_metadata": {"original_role": role_a, **{k: v for k, v in a.items() if k != "text"}},
                "b_metadata": {"original_role": role_b, **{k: v for k, v in b.items() if k != "text"}},
                "version_a_sha256": sha256(a["text"]),
                "version_b_sha256": sha256(b["text"]),
                "review_status": "pending human review",
            })
    if len(records) != 20 or len({r["review_id"] for r in records}) != 20:
        raise ValueError("Expected twenty unique pairs")
    payload = {"schema": "existing-original-pairs-review-v1", "seed": seed,
               "source_texts_unmodified": True, "human_review_completed": False,
               "sources": sources, "pairs": records}
    packet_hash = sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    output.mkdir(parents=True, exist_ok=True)
    (output / "ORIGINAL_PAIRS.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    page = render(records, sources, packet_hash)
    (output / "REVIEW.html").write_text(page, encoding="utf-8")
    # Read the rendered DOM text back, so escaping never changes the responses.
    from html.parser import HTMLParser

    class ExtractResponses(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=True)
            self.active = False
            self.values = []
            self.parts = []

        def handle_starttag(self, tag, attrs):
            if tag == "div" and dict(attrs).get("class") == "response verbatim":
                self.active, self.parts = True, []

        def handle_data(self, data):
            if self.active:
                self.parts.append(data)

        def handle_endtag(self, tag):
            if self.active and tag == "div":
                self.values.append("".join(self.parts))
                self.active = False

    parser = ExtractResponses()
    parser.feed(page)
    expected = [r[k] for r in records for k in ("version_a", "version_b")]
    if parser.values != expected:
        raise ValueError("HTML text differs from extracted source responses")
    manifest = {"schema": "existing-original-pairs-manifest-v1", "pair_count": 20,
                "source_counts": dict(Counter(r["dataset"] for r in records)),
                "original_response_strings_verified": len(expected),
                "packet_sha256": packet_hash,
                "packet_hash_encoding": "UTF-8 JSON with ensure_ascii=False, sort_keys=True and default separators",
                "original_pairs_file_sha256": hashlib.sha256((output / "ORIGINAL_PAIRS.json").read_bytes()).hexdigest(),
                "page_sha256": sha256(page),
                "human_review_completed": False, "review_page": str(output / "REVIEW.html")}
    (output / "MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def refresh_view(output: Path) -> dict:
    """Refresh presentation only; retain every saved pair and its review identity."""
    payload = json.loads((output / "ORIGINAL_PAIRS.json").read_text(encoding="utf-8"))
    manifest = json.loads((output / "MANIFEST.json").read_text(encoding="utf-8"))
    packet_hash = sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    if packet_hash != manifest["packet_sha256"]:
        raise ValueError("Saved packet changed; refusing to refresh its review page")
    page = render(payload["pairs"], payload["sources"], packet_hash)
    (output / "REVIEW.html").write_text(page, encoding="utf-8")
    manifest.update(page_sha256=sha256(page),
                    packet_hash_encoding="UTF-8 JSON with ensure_ascii=False, sort_keys=True and default separators",
                    original_pairs_file_sha256=hashlib.sha256((output / "ORIGINAL_PAIRS.json").read_bytes()).hexdigest())
    (output / "MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--steyvers", type=Path, required=True)
    ap.add_argument("--linguistic", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--seed", type=int, default=20261018)
    ap.add_argument("--refresh-view", action="store_true")
    args = ap.parse_args()
    result = refresh_view(args.output) if args.refresh_view else build([args.steyvers, args.linguistic], args.output, args.seed)
    print(json.dumps(result, ensure_ascii=False))
