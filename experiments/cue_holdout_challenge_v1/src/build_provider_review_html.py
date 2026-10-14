"""Build a private, label-blind HTML review for the Chat provider replication.

The reviewer sees the prompt, a neutrally labelled source answer, and randomized
Version A / Version B text. Source identifiers, cue-family metadata, and the
intended confident/hedged roles are never embedded in the reviewer-facing HTML.

Showing the source answer lets the reviewer detect shared drift in both rewrites
without revealing which rewrite is intended to be confident or hesitant.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

from prepare_blind_review import load_and_join_rows


CHALLENGE = Path(__file__).resolve().parents[1]
PRIVATE = CHALLENGE / "private_data"
DEFAULT_SEED = 20261013
REVIEW_FIELDS = (
    "source_fidelity",
    "content_equivalence",
    "stronger_speaker_confidence",
    "naturalness",
    "formatting_mismatch",
    "shortcut_concern",
)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _stable_digest(seed: int, purpose: str, value: str) -> bytes:
    return hashlib.sha256(f"{seed}\0{purpose}\0{value}".encode("utf-8")).digest()


def _stratum(row: dict[str, Any]) -> str:
    """Use the frozen task x cue-family cells to balance hidden A/B roles."""
    return f"{row.get('task', 'unknown')}\0{row.get('cue_family', 'unknown')}"


def balanced_role_assignments(
    rows: list[dict[str, Any]], seed: int
) -> dict[str, tuple[str, str]]:
    """Randomize roles reproducibly, balancing within each design stratum.

    The 50-source challenge has two rows in each task x cue-family cell, so
    this produces one confident-A and one hedged-A example per cell.  Odd-size
    strata remain reproducible and differ by at most one position.
    """
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[_stratum(row)].append(row)

    assignments: dict[str, tuple[str, str]] = {}
    # In the frozen 5 x 5 x 2 design, every task x cue-family stratum has one
    # row per length direction. Choose which direction is confident-A across
    # strata as evenly as possible. This preserves exact within-stratum A/B
    # balance without letting A/B position become a proxy for response length.
    paired_strata = {
        stratum: members
        for stratum, members in grouped.items()
        if len(members) == 2
        and {member.get("length_direction") for member in members}
        == {"confident_longer", "hedged_longer"}
    }
    ranked_strata = sorted(
        paired_strata,
        key=lambda stratum: _stable_digest(seed, "length-cross-balance", stratum),
    )
    confident_longer_count = len(ranked_strata) // 2
    if len(ranked_strata) % 2:
        confident_longer_count += (
            _stable_digest(seed, "odd-length-cross-balance", "all-strata")[0] & 1
        )
    confident_longer_a_strata = set(ranked_strata[:confident_longer_count])
    for stratum, members in paired_strata.items():
        confident_a_direction = (
            "confident_longer"
            if stratum in confident_longer_a_strata
            else "hedged_longer"
        )
        for member in members:
            source_id = member["source_id"]
            assignments[source_id] = (
                ("confident", "hedged")
                if member.get("length_direction") == confident_a_direction
                else ("hedged", "confident")
            )

    for stratum, members in grouped.items():
        if stratum in paired_strata:
            continue
        source_ids = [member["source_id"] for member in members]
        ranked = sorted(
            source_ids,
            key=lambda source_id: _stable_digest(
                seed, f"a-role:{stratum}", source_id
            ),
        )
        confident_a_count = len(ranked) // 2
        if len(ranked) % 2:
            confident_a_count += _stable_digest(seed, "odd-stratum", stratum)[0] & 1
        confident_a = set(ranked[:confident_a_count])
        for source_id in ranked:
            assignments[source_id] = (
                ("confident", "hedged")
                if source_id in confident_a
                else ("hedged", "confident")
            )
    return assignments


def build_blinded_rows(
    rows: list[dict[str, Any]], seed: int = DEFAULT_SEED
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    """Return reviewer rows and a separate private unblinding key."""
    if not rows:
        raise ValueError("No joined rewrite records found")
    source_ids = [row.get("source_id") for row in rows]
    if any(not isinstance(source_id, str) or not source_id for source_id in source_ids):
        raise ValueError("Every row must have a nonempty source_id")
    if len(set(source_ids)) != len(source_ids):
        raise ValueError("Duplicate source_id in joined rewrite records")

    assignments = balanced_role_assignments(rows, seed)
    ordered = sorted(
        rows,
        key=lambda row: _stable_digest(seed, "packet-order", row["source_id"]),
    )
    blinded: list[dict[str, str]] = []
    key: list[dict[str, str]] = []
    for index, row in enumerate(ordered, start=1):
        source_id = row["source_id"]
        prompt = row.get("prompt")
        source_answer = row.get("original_response")
        confident = row.get("confident_response")
        hedged = row.get("hedged_response")
        if not all(
            isinstance(value, str) and value.strip()
            for value in (prompt, source_answer, confident, hedged)
        ):
            raise ValueError(f"Missing prompt, source answer, or rewrite text for {source_id}")
        if confident == hedged:
            raise ValueError(f"Identical versions for {source_id}")

        a_role, b_role = assignments[source_id]
        values = {"confident": confident, "hedged": hedged}
        review_id = f"R{index:03d}"
        blinded.append(
            {
                "review_id": review_id,
                "prompt": prompt,
                "source_answer": source_answer,
                "version_a": values[a_role],
                "version_b": values[b_role],
            }
        )
        key.append(
            {
                "review_id": review_id,
                "source_id": source_id,
                "version_a_role": a_role,
                "version_b_role": b_role,
                "version_a_sha256": sha256_text(values[a_role]),
                "version_b_sha256": sha256_text(values[b_role]),
                "original_response_sha256": row.get("original_response_sha256", ""),
                "task": str(row.get("task", "")),
                "cue_family": str(row.get("cue_family", "")),
                "length_direction": str(row.get("length_direction", "")),
            }
        )
    return blinded, key


def _select(field: str, options: Iterable[tuple[str, str]]) -> str:
    option_html = '<option value="">Not reviewed</option>' + "".join(
        f'<option value="{html.escape(value, quote=True)}">{html.escape(label)}</option>'
        for value, label in options
    )
    return f'<select data-field="{field}">{option_html}</select>'


def render_html(rows: list[dict[str, str]], packet_hash: str, title: str) -> str:
    """Render a self-contained, local-only reviewer page."""
    def esc(value: Any) -> str:
        return html.escape(str(value), quote=True)

    cards: list[str] = []
    identities: list[dict[str, str]] = []
    for index, row in enumerate(rows):
        identities.append({"review_id": row["review_id"]})
        cards.append(
            f'''<article class="card" data-index="{index}" {'hidden' if index else ''}>
<div class="meta"><strong>{esc(row['review_id'])}</strong></div>
<section class="prompt"><h2>Prompt / 问题</h2><pre>{esc(row['prompt'])}</pre></section>
<section class="source"><h2>Source answer / 原始回答</h2><pre>{esc(row['source_answer'])}</pre></section>
<div class="versions"><section><h2>Version A</h2><pre>{esc(row['version_a'])}</pre></section>
<section><h2>Version B</h2><pre>{esc(row['version_b'])}</pre></section></div>
<div class="review">
<label>1. Source fidelity（A/B 是否都保留原始回答的所有实质内容）{_select('source_fidelity', [
    ('both_preserve_source', 'Both preserve the source answer'),
    ('a_drift', 'A changes, adds, or omits substantive source content'),
    ('b_drift', 'B changes, adds, or omits substantive source content'),
    ('both_drift', 'Both change, add, or omit substantive source content'),
    ('uncertain', 'Uncertain'),
])}</label>
<label>2. Pair equivalence（A/B 相互是否表达相同实质内容）{_select('content_equivalence', [
    ('equivalent', 'Equivalent in substantive content'),
    ('a_has_extra_or_missing_content', 'A contains a substantive addition or omission'),
    ('b_has_extra_or_missing_content', 'B contains a substantive addition or omission'),
    ('substantially_different', 'The two versions differ substantially'),
    ('uncertain', 'Uncertain'),
])}</label>
<label>3. Stronger speaker confidence（哪一版整体更坚定）{_select('stronger_speaker_confidence', [
    ('a', 'A is clearly more confident'),
    ('b', 'B is clearly more confident'),
    ('no_clear_difference', 'No clear confidence difference'),
    ('uncertain', 'Uncertain'),
])}</label>
<label>4. Naturalness（语言是否自然）{_select('naturalness', [
    ('both_natural', 'Both are natural'),
    ('a_unnatural', 'A is unnatural'),
    ('b_unnatural', 'B is unnatural'),
    ('both_unnatural', 'Both are unnatural'),
    ('uncertain', 'Uncertain'),
])}</label>
<label>5. Formatting mismatch（是否破坏要求的结构或格式）{_select('formatting_mismatch', [
    ('none', 'No meaningful formatting mismatch'),
    ('a_mismatch', 'A changes or breaks the requested format'),
    ('b_mismatch', 'B changes or breaks the requested format'),
    ('both_mismatch', 'Both change or break the requested format'),
    ('uncertain', 'Uncertain'),
])}</label>
<label>6. Shortcut / generic-label concern（是否只靠可删除的通用标签句表达语气）{_select('shortcut_concern', [
    ('none', 'No obvious shortcut; stance is integrated naturally'),
    ('a_only', 'A relies on a detachable or formulaic label'),
    ('b_only', 'B relies on a detachable or formulaic label'),
    ('both', 'Both rely on detachable or formulaic labels'),
    ('uncertain', 'Uncertain'),
])}</label>
</div>
<label class="notes">Notes / 备注<textarea data-field="notes" placeholder="Briefly note any changed claim, weak contrast, unnatural wording, formatting problem, or detachable confidence sentence."></textarea></label>
</article>'''
        )

    identities_json = json.dumps(identities, ensure_ascii=False).replace("<", "\\u003c")
    required_json = json.dumps(REVIEW_FIELDS)
    export_filename = f"chat_provider_blind_review_{len(rows)}.json"
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<style>
body{{margin:0;background:#f4f5f7;color:#18202b;font:16px/1.55 system-ui,-apple-system,sans-serif}}
main{{max-width:1500px;margin:auto;padding:24px}}h1{{font-size:27px;margin:0 0 8px}}.intro{{max-width:1100px}}
.notice{{background:#eef6ff;border-left:4px solid #3169b3;padding:10px 14px;margin:14px 0}}
.toolbar{{display:flex;gap:10px;align-items:center;flex-wrap:wrap;position:sticky;top:0;background:#f4f5f7;padding:10px 0;z-index:2}}
button,select{{font:inherit;padding:7px;border:1px solid #bac3ce;border-radius:7px;background:white}}button{{cursor:pointer}}.primary{{background:#2352a3;color:white}}
.card{{background:white;border:1px solid #dce1e7;border-radius:12px;padding:20px}}.card[hidden]{{display:none}}.meta{{color:#536071;margin-bottom:12px}}
pre{{font:15px/1.6 ui-monospace,SFMono-Regular,monospace;white-space:pre-wrap;overflow-wrap:anywhere}}
.prompt,.source{{background:#f7f8fa;border:1px solid #dbe2eb;border-radius:8px;padding:12px}}.source{{margin-top:12px;background:#fffaf0}}
.versions{{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:14px}}.versions section{{border:1px solid #dbe2eb;border-radius:8px;padding:12px;background:#fafbfd}}
h2{{font-size:17px;margin:0 0 8px}}.review{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin-top:18px}}
.review label{{display:flex;flex-direction:column;gap:6px}}.notes{{display:block;margin-top:14px}}textarea{{width:100%;min-height:78px;box-sizing:border-box;font:inherit;padding:8px}}
#progress{{font-weight:650}}@media(max-width:900px){{.versions,.review{{grid-template-columns:1fr}}.toolbar{{position:static}}}}
</style></head><body><main>
<header><h1>{esc(title)}</h1>
<p class="intro">Each card shows the source answer and two rewrites. Check both rewrites against the source, but do not try to infer which confidence condition was intended. The page deliberately omits source identity, cue family, length assignment, and answer key.</p>
<p class="notice"><strong>Main check:</strong> Both rewrites should preserve every substantive claim in the source answer while making one version clearly more speaker-confident. The contrast should be natural and integrated across the response, not added as a generic sentence such as “I am certain about this answer.”</p></header>
<nav class="toolbar"><button id="prev">Previous</button><span id="position"></span><button id="next">Next</button>
<label>Jump <select id="jump"></select></label><span id="progress"></span>
<button class="primary" id="export">Download review JSON</button><span id="save-status"></span></nav>
{''.join(cards)}
</main><script>
const packetHash={json.dumps(packet_hash)};const identities={identities_json};const required={required_json};
const storageKey='chat-provider-pair-review-'+packetHash;let reviews={{}};let current=0;let storageAvailable=true;
try{{reviews=JSON.parse(localStorage.getItem(storageKey)||'{{}}')}}catch(e){{storageAvailable=false}}
const cards=[...document.querySelectorAll('.card')];const jump=document.getElementById('jump');
identities.forEach((m,i)=>{{const o=document.createElement('option');o.value=i;o.textContent=m.review_id;jump.append(o)}});
function progress(){{const complete=identities.filter(m=>required.every(k=>(reviews[m.review_id]||{{}})[k])).length;document.getElementById('progress').textContent='Complete '+complete+' / '+identities.length;document.getElementById('save-status').textContent=storageAvailable?'Autosaved in this browser':'Browser storage unavailable; export often'}}
cards.forEach((card,i)=>card.querySelectorAll('[data-field]').forEach(el=>{{el.value=(reviews[identities[i].review_id]||{{}})[el.dataset.field]||'';el.addEventListener('input',()=>{{const id=identities[i].review_id;reviews[id]||={{}};reviews[id][el.dataset.field]=el.value;reviews[id].updated_at=new Date().toISOString();try{{localStorage.setItem(storageKey,JSON.stringify(reviews))}}catch(e){{storageAvailable=false}}progress()}})}}));
function show(i){{current=Math.max(0,Math.min(cards.length-1,i));cards.forEach((c,n)=>c.hidden=n!==current);jump.value=current;document.getElementById('position').textContent=(current+1)+' / '+cards.length;document.getElementById('prev').disabled=current===0;document.getElementById('next').disabled=current===cards.length-1;window.scrollTo(0,0)}}
document.getElementById('prev').onclick=()=>show(current-1);document.getElementById('next').onclick=()=>show(current+1);jump.onchange=()=>show(Number(jump.value));
document.getElementById('export').onclick=()=>{{const payload={{packet_sha256:packetHash,reviewed_at:new Date().toISOString(),blinded:true,reviews:identities.map(m=>({{...m,...(reviews[m.review_id]||{{}})}}))}};const url=URL.createObjectURL(new Blob([JSON.stringify(payload,null,2)],{{type:'application/json'}}));const a=document.createElement('a');a.href=url;a.download={json.dumps(export_filename)};a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)}};
show(0);progress();
</script></body></html>'''


def require_private_output(output_dir: Path, private_root: Path = PRIVATE) -> Path:
    output = output_dir.resolve()
    root = private_root.resolve()
    if output != root and root not in output.parents:
        raise ValueError(f"Review output must stay under ignored private_data: {root}")
    return output


def write_review_bundle(
    joined_rows: list[dict[str, Any]],
    output_dir: Path,
    *,
    seed: int = DEFAULT_SEED,
    title: str = "Blind review: Chat provider replication (50 pairs)",
    overwrite: bool = False,
    private_root: Path = PRIVATE,
) -> dict[str, Any]:
    """Write the self-contained HTML plus private mapping and manifest."""
    blinded, key = build_blinded_rows(joined_rows, seed=seed)
    rows_dump = "".join(
        json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in blinded
    )
    packet_hash = sha256_text(rows_dump)
    output = require_private_output(output_dir, private_root=private_root)
    manifest_path = output / "MANIFEST.json"
    if manifest_path.exists() and not overwrite:
        previous = json.loads(manifest_path.read_text(encoding="utf-8"))
        if previous.get("packet_sha256") != packet_hash:
            raise ValueError(
                "Refusing to overwrite a different review packet; pass --overwrite explicitly"
            )

    output.mkdir(parents=True, exist_ok=True)
    key_payload = {
        "packet_sha256": packet_hash,
        "seed": seed,
        "pairs": key,
    }
    key_text = json.dumps(key_payload, ensure_ascii=False, indent=2) + "\n"
    stratum_roles: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
    direction_roles: dict[str, Counter[str]] = defaultdict(Counter)
    for item in key:
        stratum_roles[(item["task"], item["cue_family"])][item["version_a_role"]] += 1
        direction_roles[item["length_direction"]][item["version_a_role"]] += 1
    stratum_balanced = all(
        abs(counts["confident"] - counts["hedged"]) <= 1
        for counts in stratum_roles.values()
    )
    direction_balanced = all(
        abs(counts["confident"] - counts["hedged"]) <= 1
        for counts in direction_roles.values()
    )
    manifest = {
        "packet_sha256": packet_hash,
        "unblind_key_sha256": sha256_text(key_text),
        "pairs": len(blinded),
        "blinded": True,
        "shows_prompt": True,
        "shows_original_response": True,
        "shows_source_identity": False,
        "reproducible_ab_order": True,
        "balanced_ab_within_task_x_cue_family": stratum_balanced,
        "length_direction_cross_balanced": direction_balanced,
        "review_fields": list(REVIEW_FIELDS),
        "human_review": "pending",
        "public_text_exported": False,
    }
    (output / "BLINDED_ROWS.jsonl").write_text(rows_dump, encoding="utf-8")
    (output / "BLIND_REVIEW.html").write_text(
        render_html(blinded, packet_hash, title), encoding="utf-8"
    )
    (output / "UNBLIND_KEY.json").write_text(key_text, encoding="utf-8")
    (output / "MANIFEST.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, required=True, help="Frozen 50-source JSONL")
    parser.add_argument("--input", nargs="+", type=Path, required=True, help="Completed writer JSONL batch(es)")
    parser.add_argument("--output-dir", type=Path, required=True, help="Directory under this experiment's private_data")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--title", default="Blind review: Chat provider replication (50 pairs)")
    parser.add_argument("--require-full", action="store_true", help="Require exactly all 50 frozen sources")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    joined = load_and_join_rows(args.sources, args.input, require_full=args.require_full)
    manifest = write_review_bundle(
        joined,
        args.output_dir,
        seed=args.seed,
        title=args.title,
        overwrite=args.overwrite,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
