"""Prepare and render a private six-source development preview.

This deliberately does not modify any frozen v4 artifact or certify a pair.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import random
from pathlib import Path

import build_factual_rewrite_review as review


BASE = Path(__file__).resolve().parents[1]
FROZEN = BASE / "private_data" / "rewrite_canary_v1"
OUTPUT = FROZEN / "epistemic_preview_v1"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render_preview(rows: list[dict], packet_hash: str) -> str:
    cards = []
    options = {
        "factual_core": [("yes", "Same factual core"), ("no", "Factual core changed"), ("uncertain", "Unsure")],
        "more_certain": [("a", "Version A"), ("b", "Version B"), ("tie", "No clear difference")],
        "contrast": [("clear", "Clearly different"), ("weak", "Too weak"), ("unnatural", "Exaggerated or unnatural")],
        "presentation": [("natural", "Both natural and comparable"), ("a_problem", "A has a problem"), ("b_problem", "B has a problem"), ("both_problem", "Both have problems")],
    }
    labels = {"factual_core": "1. Facts, legal status and scientific qualifications",
              "more_certain": "2. Which response sounds more certain?",
              "contrast": "3. Strength of the contrast", "presentation": "4. Naturalness and comparable detail"}
    for row in rows:
        controls = "".join(
            f'<label>{labels[field]}<select data-field="{field}"><option value="">Not reviewed</option>'
            + "".join(f'<option value="{value}">{label}</option>' for value, label in choices)
            + '</select></label>' for field, choices in options.items()
        )
        cards.append(
            f'<article data-id="{html.escape(row["review_id"])}"><h2>{html.escape(row["review_id"])}</h2>'
            f'<p>{html.escape(row["question"])}</p><details><summary>Original response</summary>'
            f'<p>{html.escape(row["original_response"])}</p></details><div class="versions">'
            f'<section><h3>Version A</h3><p>{html.escape(row["version_a"])}</p></section>'
            f'<section><h3>Version B</h3><p>{html.escape(row["version_b"])}</p></section></div>'
            f'<div class="controls">{controls}</div><label>Notes<textarea data-field="notes"></textarea></label></article>'
        )
    return '''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>Six-pair epistemic rewrite preview</title>
<style>body{font:16px/1.6 system-ui;color:#17202b;margin:24px auto;max-width:1400px;padding:0 20px}article{border-top:1px solid #ccc;margin-top:36px;padding-top:12px}h1{font-size:26px}h2{font-size:21px}h3{font-size:18px}.versions,.controls{display:grid;grid-template-columns:1fr 1fr;gap:24px}.versions section{background:#f5f7fa;padding:16px}p{white-space:pre-wrap}.controls{margin:18px 0}label{display:flex;flex-direction:column;gap:6px}select,textarea,button{font:inherit;padding:8px}textarea{min-height:65px}button{cursor:pointer}@media(max-width:850px){.versions,.controls{grid-template-columns:1fr}}</style></head><body>
<h1>Six-pair epistemic rewrite preview</h1>
<p>These are new development drafts on six previously inspected sources. The intended difference is how strongly the response commits to the same factual core.</p>
<p><strong>“Might”, “may”, “seems” and similar uncertainty expressions are allowed.</strong> Do not count that intended change as a factual error. Check that names, numbers, claims, scientific evidence strength and legal status remain the same. A bill describing provisions must not become an enacted historical event.</p>
<p>Both versions should sound natural, with a clear certainty difference. These drafts have not passed human review or activation analysis.</p>
<button id="export">Download feedback</button><span id="saved"></span>
''' + "".join(cards) + '''<script>
const packetHash=PACKET_HASH;const storeKey='epistemic-preview-'+packetHash;let feedback={};
try{feedback=JSON.parse(localStorage.getItem(storeKey)||'{}')}catch(e){}
for(const card of document.querySelectorAll('article')){const id=card.dataset.id;for(const control of card.querySelectorAll('[data-field]')){control.value=(feedback[id]||{})[control.dataset.field]||'';control.addEventListener('input',()=>{feedback[id]||={};feedback[id][control.dataset.field]=control.value;try{localStorage.setItem(storeKey,JSON.stringify(feedback));document.getElementById('saved').textContent=' Feedback saved in this browser'}catch(e){document.getElementById('saved').textContent=' Download feedback to keep your responses'}})}}
document.getElementById('export').onclick=()=>{const payload={schema:'epistemic-preview-human-feedback-v1',artifact_role:'development_preview',packet_sha256:packetHash,pair_count:6,human_review_certified:false,reviews:Object.entries(feedback).map(([review_id,r])=>({review_id,...r}))};const u=URL.createObjectURL(new Blob([JSON.stringify(payload,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=u;a.download='epistemic_preview_six_feedback.json';a.click();setTimeout(()=>URL.revokeObjectURL(u),1000)};
</script></body></html>'''.replace('PACKET_HASH', json.dumps(packet_hash))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--render", action="store_true")
    args = parser.parse_args()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    if not args.render:
        sources_path = FROZEN / "frozen_sources_v4.jsonl"
        key_path = FROZEN / "blind_review_clean6_v4" / "private_key" / "BLIND_REVIEW_KEY.json"
        sources = {row["source_id"]: row for row in review.read_records(sources_path)}
        key = json.loads(key_path.read_text(encoding="utf-8"))
        manifest_path = FROZEN / "blind_review_clean6_v4" / "BLIND_REVIEW_MANIFEST.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if digest(key_path) != manifest["answer_key_sha256"]:
            raise ValueError("old packet key hash mismatch")
        if digest(sources_path) != manifest["input_sha256"]["frozen_sources_v4"]:
            raise ValueError("frozen source hash mismatch")
        rows = []
        bindings = []
        for index, entry in enumerate(key["rows"], 1):
            source = sources[entry["source_id"]]
            preview_id = f"EP{index:03d}"
            rows.append({
                "preview_id": preview_id,
                "prompt": source["prompt"],
                "original_response": source["original_response"],
            })
            bindings.append({
                "preview_id": preview_id,
                "source_id": source["source_id"],
                "source_hash": source["source_hash"],
                "original_response_sha256": source["original_response_sha256"],
            })
        if len(rows) != 6:
            raise ValueError("expected six source records")
        review._write_json(OUTPUT / "SOURCE_ONLY.json", {"sources": rows})
        review._write_json(OUTPUT / "SOURCE_BINDINGS_PRIVATE.json", {
            "source_sha256": digest(sources_path), "rows": bindings,
        })
        print(json.dumps({"status": "source_preview_prepared", "source_count": len(rows)}))
        return

    sources_path = OUTPUT / "SOURCE_ONLY.json"
    pair_path = OUTPUT / "DRAFT_PAIRS.json"
    sources = json.loads(sources_path.read_text(encoding="utf-8"))["sources"]
    draft = json.loads(pair_path.read_text(encoding="utf-8"))
    pairs = draft["pairs"]
    by_id = {row["preview_id"]: row for row in pairs}
    if len(pairs) != 6 or len(by_id) != 6 or set(by_id) != {r["preview_id"] for r in sources}:
        raise ValueError("drafts must cover the same six sources exactly once")
    roles = ["confident"] * 3 + ["hesitant"] * 3
    random.Random(20261017).shuffle(roles)
    blinded, key, counts = [], [], []
    for source, a_role in zip(sources, roles):
        pair = by_id[source["preview_id"]]
        if any(not isinstance(pair.get(f"{role}_response"), str) or not pair[f"{role}_response"].strip()
               for role in ("confident", "hesitant")):
            raise ValueError("draft response missing")
        b_role = "hesitant" if a_role == "confident" else "confident"
        blinded.append({
            "review_id": source["preview_id"], "question": source["prompt"],
            "original_response": source["original_response"],
            "version_a": pair[f"{a_role}_response"], "version_b": pair[f"{b_role}_response"],
        })
        key.append({"preview_id": source["preview_id"], "version_a_role": a_role})
        counts.append({role: len(pair[f"{role}_response"].split())
                       for role in ("confident", "hesitant")})
    packet_hash = review.sha256_value(blinded)
    page = render_preview(blinded, packet_hash)
    (OUTPUT / "reviewer_only").mkdir(exist_ok=True)
    (OUTPUT / "private_key").mkdir(exist_ok=True)
    (OUTPUT / "reviewer_only" / "BLIND_REVIEW.html").write_text(page, encoding="utf-8")
    review._write_json(OUTPUT / "private_key" / "KEY.json", {"rows": key})
    provenance = {
        "schema": "epistemic-rewrite-development-preview-v1", "pair_count": 6,
        "status": "draft_pending_researcher_review", "artifact_role": "development_preview",
        "source_sha256": digest(sources_path), "draft_sha256": digest(pair_path),
        "packet_sha256": packet_hash, "writer": draft.get("writer"),
        "rewrite_rule_sha256": digest(BASE / "EPISTEMIC_REWRITE_UPDATE.md"),
        "editorial_changes": draft.get("editorial_changes", []),
        "length_measure": "whitespace_words_not_model_tokens", "word_counts": counts,
        "previously_inspected_sources": True, "old_v4_repair_budget_modified": False,
        "human_review_certified": False, "activation_extraction_started": False,
        "probe_fitting_started": False, "sdt_training_started": False,
    }
    review._write_json(OUTPUT / "PREVIEW_PROVENANCE.json", provenance)
    public = {field: provenance[field] for field in (
        "schema", "pair_count", "status", "artifact_role", "source_sha256",
        "draft_sha256", "packet_sha256", "rewrite_rule_sha256", "writer",
        "previously_inspected_sources", "old_v4_repair_budget_modified",
        "human_review_certified", "activation_extraction_started",
        "probe_fitting_started", "sdt_training_started",
    )}
    public["editorial_clarification_count"] = len(provenance["editorial_changes"])
    public["quality_review_status"] = "researcher_feedback_pending"
    public["development_limitations"] = [
        "Six previously inspected sources; not a held-out evaluation.",
        "The drafts remain close to source wording and repeat several hedges.",
        "No automatic strict-pass count or probe-performance claim.",
    ]
    review._write_json(BASE / "results" / "epistemic_preview_v1_status.json", public)
    print(json.dumps({"status": provenance["status"], "pair_count": 6,
                      "packet_sha256": packet_hash, "word_counts": counts}))


if __name__ == "__main__":
    main()
