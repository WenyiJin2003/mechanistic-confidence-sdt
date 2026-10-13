"""Build a reproducible, label-blind human review packet for paired responses.

The reviewer-facing HTML contains only the source response and anonymized A/B
versions.  The A/B label mapping is written to a separate private key file.
All outputs are required to remain under this experiment's ignored
``private_data`` directory.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


BASE = Path(__file__).resolve().parents[1]
PRIVATE = BASE / "private_data"
BASE_REVIEW_DIMENSIONS = [
    "content_equivalence",
    "certainty_contrast",
    "naturalness",
    "cue_scope",
    "decision",
]
STRUCTURE_REVIEW_DIMENSION = "structure_format"
LEGACY_PACKET_HASH_MODE = "blinded-rows-sha256-v1"
KEY_BOUND_PACKET_HASH_MODE = "schema-keycore-and-blinded-rows-sha256-v3"
KEY_CORE_FIELDS = (
    "review_id",
    "source_id",
    "cohort",
    "version_a_label",
    "version_b_label",
    "source_response_sha256",
    "version_a_sha256",
    "version_b_sha256",
)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def review_schema_binding(schema_id: str, review_dimensions: list[str]) -> str:
    return json.dumps(
        {"review_schema_id": schema_id, "review_dimensions": review_dimensions},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def key_core_sha256(key_rows: list[dict[str, Any]]) -> str:
    """Hash the semantic A/B mapping without creating a packet-hash cycle."""
    core = []
    for index, entry in enumerate(key_rows):
        missing = [field for field in KEY_CORE_FIELDS if field not in entry]
        if missing:
            raise ValueError(f"Key entry {index} is missing core fields: {missing}")
        core.append({field: entry[field] for field in KEY_CORE_FIELDS})
    return sha256_text(
        json.dumps(
            core,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    )


def compute_packet_hash(
    rows_dump: str,
    schema_id: str,
    review_dimensions: list[str],
    key_core_hash: str | None = None,
) -> tuple[str, str, str]:
    binding = review_schema_binding(schema_id, review_dimensions)
    binding_hash = sha256_text(binding)
    if STRUCTURE_REVIEW_DIMENSION not in review_dimensions:
        return sha256_text(rows_dump), LEGACY_PACKET_HASH_MODE, binding_hash
    if not isinstance(key_core_hash, str) or len(key_core_hash) != 64:
        raise ValueError("Six-field packet requires key_core_sha256")
    preimage = (
        f"schema-keycore-bound-review-packet-v3\n{binding}\n"
        f"{key_core_hash}\n{rows_dump}"
    )
    return sha256_text(preimage), KEY_BOUND_PACKET_HASH_MODE, binding_hash


def load_records(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".jsonl":
        return [json.loads(line) for line in text.splitlines() if line.strip()]
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return [json.loads(line) for line in text.splitlines() if line.strip()]
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("records"), list):
        return payload["records"]
    raise ValueError(f"Unsupported record container: {path}")


def load_bound_records(
    base: Path, spec: dict[str, Any], *, require_records_hash: bool = False
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if not isinstance(spec, dict) or not spec.get("path") or not spec.get("file_sha256"):
        raise ValueError("Every review input must bind path and file_sha256")
    path = resolve_path(base, str(spec["path"]))
    actual_file_hash = sha256_file(path)
    if actual_file_hash != spec["file_sha256"]:
        raise ValueError(f"Review input file hash mismatch: {spec['path']}")
    records_hash = spec.get("records_sha256")
    if require_records_hash:
        if not records_hash:
            raise ValueError(f"Pair input must bind records_sha256: {spec['path']}")
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict) or payload.get("records_sha256") != records_hash:
            raise ValueError(f"Pair records hash mismatch: {spec['path']}")
    binding = {
        "path": str(spec["path"]),
        "file_sha256": actual_file_hash,
    }
    if records_hash:
        binding["records_sha256"] = records_hash
    return load_records(path), binding


def resolve_path(base: Path, raw_path: str) -> Path:
    path = Path(raw_path)
    return path if path.is_absolute() else base / path


def require_private_output(base: Path, raw_path: str) -> Path:
    output = resolve_path(base, raw_path).resolve()
    private = (base / "private_data").resolve()
    try:
        output.relative_to(private)
    except ValueError as exc:
        raise ValueError("Review artifacts must be written under private_data") from exc
    return output


def assignment(seed: int, source_id: str) -> tuple[str, str]:
    """Return a stable pseudo-random A/B label assignment for one source."""
    bit = hashlib.sha256(f"{seed}:{source_id}".encode("utf-8")).digest()[0] & 1
    return (("confident", "hedged") if bit == 0 else ("hedged", "confident"))


def stable_order(seed: int, source_id: str) -> bytes:
    return hashlib.sha256(f"order:{seed}:{source_id}".encode("utf-8")).digest()


def balanced_assignments(seed: int, cohort_sources: dict[str, list[str]]) -> dict[tuple[str, str], tuple[str, str]]:
    """Randomize A/B reproducibly while balancing positions within each cohort."""
    result = {}
    for cohort, source_ids in cohort_sources.items():
        ranked = sorted(
            source_ids,
            key=lambda source_id: hashlib.sha256(
                f"label:{seed}:{cohort}:{source_id}".encode("utf-8")
            ).digest(),
        )
        if len(ranked) == 1:
            result[(cohort, ranked[0])] = assignment(seed, ranked[0])
            continue
        confident_a_count = len(ranked) // 2
        if len(ranked) % 2:
            confident_a_count += hashlib.sha256(f"odd:{seed}:{cohort}".encode("utf-8")).digest()[0] & 1
        confident_a = set(ranked[:confident_a_count])
        for source_id in ranked:
            result[(cohort, source_id)] = (
                ("confident", "hedged") if source_id in confident_a else ("hedged", "confident")
            )
    return result


def assemble_blinded_rows(
    config: dict[str, Any], base: Path
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    sources: dict[str, dict[str, Any]] = {}
    source_bindings = []
    for source_spec in config["source_files"]:
        source_rows, binding = load_bound_records(base, source_spec)
        source_bindings.append(binding)
        for row in source_rows:
            source_id = row["source_id"]
            previous = sources.get(source_id)
            if previous is not None and previous.get("original_response_sha256") != row.get("original_response_sha256"):
                raise ValueError(f"Conflicting source records for {source_id}")
            sources[source_id] = row

    pairs: list[tuple[str, dict[str, Any]]] = []
    pair_bindings = []
    seen: set[str] = set()
    for batch in config["pair_batches"]:
        cohort = batch["cohort"]
        pair_rows, binding = load_bound_records(base, batch, require_records_hash=True)
        pair_bindings.append({"cohort": cohort, **binding})
        for row in pair_rows:
            source_id = row["source_id"]
            if source_id in seen:
                raise ValueError(f"Duplicate paired source: {source_id}")
            seen.add(source_id)
            if row.get("status") != "accepted":
                raise ValueError(f"Pair is not accepted: {source_id}")
            pairs.append((cohort, row))

    expected = config.get("expected_pairs")
    if expected is not None and len(pairs) != expected:
        raise ValueError(f"Expected {expected} pairs, found {len(pairs)}")

    seed = int(config["seed"])
    cohort_sources: dict[str, list[str]] = defaultdict(list)
    for cohort, pair in pairs:
        cohort_sources[cohort].append(pair["source_id"])
    label_assignments = balanced_assignments(seed, cohort_sources)
    pairs.sort(key=lambda item: stable_order(seed, item[1]["source_id"]))
    blinded: list[dict[str, Any]] = []
    key: list[dict[str, Any]] = []
    for index, (cohort, pair) in enumerate(pairs, start=1):
        source_id = pair["source_id"]
        if source_id not in sources:
            raise ValueError(f"Missing source record: {source_id}")
        source = sources[source_id]
        original = source["original_response"]
        source_hash = source.get("original_response_sha256") or sha256_text(original)
        if source_hash != sha256_text(original) or source_hash != pair["original_response_sha256"]:
            raise ValueError(f"Source hash mismatch: {source_id}")

        a_label, b_label = label_assignments[(cohort, source_id)]
        values = {
            "confident": pair["confident_response"],
            "hedged": pair["hedged_response"],
        }
        review_id = f"R{index:03d}"
        blinded.append(
            {
                "review_id": review_id,
                "task": source.get("task", "unknown"),
                "dataset": source.get("dataset", "unknown"),
                "prompt": source.get("prompt", ""),
                "source_response": original,
                "version_a": values[a_label],
                "version_b": values[b_label],
            }
        )
        key.append(
            {
                "review_id": review_id,
                "source_id": source_id,
                "cohort": cohort,
                "version_a_label": a_label,
                "version_b_label": b_label,
                "source_response_sha256": source_hash,
                "version_a_sha256": sha256_text(values[a_label]),
                "version_b_sha256": sha256_text(values[b_label]),
            }
        )
    return blinded, key, {
        "source_inputs": source_bindings,
        "pair_inputs": pair_bindings,
    }


def review_schema(config: dict[str, Any]) -> tuple[str, list[str]]:
    schema = config.get("review_schema")
    if schema is None:
        return "generic-five-field-v1", list(BASE_REVIEW_DIMENSIONS)
    if not isinstance(schema, dict):
        raise ValueError("review_schema must be an object")
    unknown = set(schema) - {"schema_id", "include_structure_format"}
    if unknown:
        raise ValueError(f"Unknown review_schema fields: {sorted(unknown)}")
    include_structure = schema.get("include_structure_format", False)
    if not isinstance(include_structure, bool):
        raise ValueError("review_schema.include_structure_format must be boolean")
    schema_id = schema.get(
        "schema_id",
        "generic-six-field-structure-v1" if include_structure else "generic-five-field-v1",
    )
    if not isinstance(schema_id, str) or not schema_id:
        raise ValueError("review_schema.schema_id must be nonempty text")
    dimensions = list(BASE_REVIEW_DIMENSIONS)
    if include_structure:
        dimensions.insert(-1, STRUCTURE_REVIEW_DIMENSION)
    return schema_id, dimensions


def render_html(
    rows: list[dict[str, Any]],
    packet_hash: str,
    title: str,
    review_dimensions: list[str],
) -> str:
    def esc(value: Any) -> str:
        return html.escape(str(value), quote=True)

    include_structure = STRUCTURE_REVIEW_DIMENSION in review_dimensions
    structure_field = (
        '<label>5. Structure and requested format（结构与格式是否保持）'
        '<select data-field="structure_format"><option value="">Not reviewed</option>'
        '<option value="both_preserved">Both preserve structure and requested format</option>'
        '<option value="a_changed">A changes structure or format</option>'
        '<option value="b_changed">B changes structure or format</option>'
        '<option value="both_changed">Both change structure or format</option>'
        '<option value="uncertain">Uncertain</option></select></label>'
        if include_structure else ""
    )
    structure_field_line = f"{structure_field}\n" if include_structure else ""
    decision_number = 6 if include_structure else 5
    required_js = (
        json.dumps(review_dimensions)
        if include_structure
        else "['content_equivalence','certainty_contrast','naturalness','cue_scope','decision']"
    )
    intro_dimensions = (
        "content equivalence, speaker-level certainty contrast, naturalness, "
        "whether the stance cue applies to the whole response, and "
        "structure/requested-format preservation"
        if include_structure
        else "content equivalence, speaker-level certainty contrast, naturalness, "
        "and whether the stance cue applies to the whole response"
    )
    cards = []
    identities = []
    for index, row in enumerate(rows):
        identities.append({"review_id": row["review_id"]})
        cards.append(
            f'''<article class="card" data-index="{index}" {'hidden' if index else ''}>
<div class="meta"><strong>{esc(row['review_id'])}</strong> · {esc(row['task'])} · {esc(row['dataset'])}</div>
<details><summary>Optional source prompt / 原问题</summary><pre>{esc(row['prompt'])}</pre></details>
<div class="source"><h2>Source response / 源回答</h2><pre>{esc(row['source_response'])}</pre></div>
<div class="versions"><section><h2>Version A</h2><pre>{esc(row['version_a'])}</pre></section>
<section><h2>Version B</h2><pre>{esc(row['version_b'])}</pre></section></div>
<div class="review">
<label>1. Content equivalence（内容是否保持）<select data-field="content_equivalence"><option value="">Not reviewed</option><option value="both_match">Both preserve the source content</option><option value="a_changes">A changes or drops content</option><option value="b_changes">B changes or drops content</option><option value="both_change">Both change or drop content</option><option value="uncertain">Uncertain</option></select></label>
<label>2. Speaker-level certainty contrast（整个回答的说话者确定程度）<select data-field="certainty_contrast"><option value="">Not reviewed</option><option value="a_more_certain">A is clearly more certain</option><option value="b_more_certain">B is clearly more certain</option><option value="no_clear_contrast">No clear contrast</option><option value="uncertain">Uncertain</option></select></label>
<label>3. Naturalness（语言是否自然）<select data-field="naturalness"><option value="">Not reviewed</option><option value="both_natural">Both are natural</option><option value="a_unnatural">A is unnatural</option><option value="b_unnatural">B is unnatural</option><option value="both_unnatural">Both are unnatural</option><option value="uncertain">Uncertain</option></select></label>
<label>4. Cue scope（语气线索是否覆盖整个回答）<select data-field="cue_scope"><option value="">Not reviewed</option><option value="both_global">Both versions have global scope</option><option value="a_local_only">A is only local or ambiguous</option><option value="b_local_only">B is only local or ambiguous</option><option value="both_local_only">Both are only local or ambiguous</option><option value="uncertain">Uncertain</option></select></label>
{structure_field_line}<label>{decision_number}. Overall decision<select data-field="decision"><option value="">Not reviewed</option><option value="accept">Accept pair</option><option value="reject">Reject pair</option><option value="discuss">Needs discussion</option></select></label>
</div>
<label class="comment">Comment / 备注<textarea data-field="comment" placeholder="Explain any content change, weak contrast, unnatural wording, or local-only cue. Reject if any issue makes the pair unsuitable."></textarea></label>
</article>'''
        )

    identities_json = json.dumps(identities, ensure_ascii=False).replace("<", "\\u003c")
    export_filename = f"blind_human_review_{len(rows)}.json"
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)}</title>
<style>body{{margin:0;background:#f4f5f7;color:#18202b;font:16px/1.55 system-ui,-apple-system,sans-serif}}main{{max-width:1500px;margin:auto;padding:24px}}h1{{font-size:27px;margin:0 0 8px}}.intro{{max-width:1050px}}.toolbar{{display:flex;gap:10px;align-items:center;flex-wrap:wrap;position:sticky;top:0;background:#f4f5f7;padding:10px 0;z-index:2}}button,select{{font:inherit;padding:7px;border:1px solid #bac3ce;border-radius:7px;background:white}}button{{cursor:pointer}}.primary{{background:#2352a3;color:white}}.card{{background:white;border:1px solid #dce1e7;border-radius:12px;padding:20px}}.card[hidden]{{display:none}}.meta{{color:#536071;margin-bottom:12px}}pre{{font:15px/1.6 ui-monospace,SFMono-Regular,monospace;white-space:pre-wrap;overflow-wrap:anywhere}}.source{{background:#f7f8fa;border:1px solid #dbe2eb;border-radius:8px;padding:12px;margin-top:12px}}.versions{{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:14px}}.versions section{{border:1px solid #dbe2eb;border-radius:8px;padding:12px;background:#fafbfd}}h2{{font-size:17px;margin:0 0 8px}}.review{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin-top:18px}}.review label{{display:flex;flex-direction:column;gap:6px}}.comment{{display:block;margin-top:14px}}textarea{{width:100%;min-height:78px;box-sizing:border-box;font:inherit;padding:8px}}#progress{{font-weight:650}}@media(max-width:900px){{.versions,.review{{grid-template-columns:1fr}}.toolbar{{position:static}}}}</style></head><body><main>
<header><h1>{esc(title)}</h1><p class="intro">Review each same-content pair without guessing its intended label. Compare both versions with the source, then judge <strong>{intro_dimensions}</strong>. This is not a correctness review. The page contains no answer key.</p></header>
<nav class="toolbar"><button id="prev">Previous</button><span id="position"></span><button id="next">Next</button><label>Jump <select id="jump"></select></label><span id="progress"></span><button class="primary" id="export">Download review JSON</button><span id="save-status"></span></nav>
{''.join(cards)}
</main><script>
const packetHash={json.dumps(packet_hash)};const identities={identities_json};const storageKey='blind-pair-review-'+packetHash;let reviews={{}};let current=0;let storageAvailable=true;
try{{reviews=JSON.parse(localStorage.getItem(storageKey)||'{{}}')}}catch(e){{storageAvailable=false}}
const cards=[...document.querySelectorAll('.card')];const jump=document.getElementById('jump');identities.forEach((m,i)=>{{const o=document.createElement('option');o.value=i;o.textContent=m.review_id;jump.append(o)}});
const required={required_js};
function progress(){{const complete=identities.filter(m=>required.every(k=>(reviews[m.review_id]||{{}})[k])).length;document.getElementById('progress').textContent='Complete '+complete+' / '+identities.length;document.getElementById('save-status').textContent=storageAvailable?'Saved in this browser until export':'Browser storage unavailable; export often'}}
cards.forEach((card,i)=>card.querySelectorAll('[data-field]').forEach(el=>{{el.value=(reviews[identities[i].review_id]||{{}})[el.dataset.field]||'';el.addEventListener('input',()=>{{const id=identities[i].review_id;reviews[id]||={{}};reviews[id][el.dataset.field]=el.value;reviews[id].updated_at=new Date().toISOString();try{{localStorage.setItem(storageKey,JSON.stringify(reviews))}}catch(e){{storageAvailable=false}}progress()}})}}));
function show(i){{current=Math.max(0,Math.min(cards.length-1,i));cards.forEach((c,n)=>c.hidden=n!==current);jump.value=current;document.getElementById('position').textContent=(current+1)+' / '+cards.length;document.getElementById('prev').disabled=current===0;document.getElementById('next').disabled=current===cards.length-1;window.scrollTo(0,0)}}
document.getElementById('prev').onclick=()=>show(current-1);document.getElementById('next').onclick=()=>show(current+1);jump.onchange=()=>show(Number(jump.value));
document.getElementById('export').onclick=()=>{{const payload={{packet_sha256:packetHash,reviewed_at:new Date().toISOString(),blinded:true,reviews:identities.map(m=>({{...m,...(reviews[m.review_id]||{{}})}}))}};const url=URL.createObjectURL(new Blob([JSON.stringify(payload,null,2)],{{type:'application/json'}}));const a=document.createElement('a');a.href=url;a.download={json.dumps(export_filename)};a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)}};show(0);progress();
</script></body></html>'''


def build_packet(
    config_path: Path, base: Path = BASE, *, overwrite: bool = False
) -> dict[str, Any]:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    schema_id, review_dimensions = review_schema(config)
    rows, key, input_bindings = assemble_blinded_rows(config, base)

    rows_dump = "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows)
    key_core_hash = key_core_sha256(key)
    packet_hash, packet_hash_mode, schema_hash = compute_packet_hash(
        rows_dump, schema_id, review_dimensions, key_core_hash
    )
    output_dir = require_private_output(base, config["output_dir"])
    existing_manifest = output_dir / "MANIFEST.json"
    if existing_manifest.exists() and not overwrite:
        previous = json.loads(existing_manifest.read_text(encoding="utf-8"))
        if previous.get("packet_sha256") != packet_hash:
            raise ValueError(
                "Refusing to overwrite a different review packet; use --overwrite explicitly"
            )
    output_dir.mkdir(parents=True, exist_ok=True)
    title = config.get("title", f"Blind review: {len(rows)} paired responses")
    html_text = render_html(rows, packet_hash, title, review_dimensions)
    key_payload = {
        "packet_sha256": packet_hash,
        "seed": int(config["seed"]),
        "pairs": key,
    }
    if STRUCTURE_REVIEW_DIMENSION in review_dimensions:
        key_payload.update(
            {
                "packet_hash_mode": packet_hash_mode,
                "review_schema_sha256": schema_hash,
                "key_core_sha256": key_core_hash,
            }
        )
    key_text = json.dumps(key_payload, indent=2) + "\n"
    manifest = {
        "packet_sha256": packet_hash,
        "unblind_key_sha256": sha256_text(key_text),
        "pairs": len(rows),
        "blinded": True,
        "reproducible_ab_order": True,
        "review_dimensions": review_dimensions,
        "human_review": "pending",
        "public_text_exported": False,
        "config_sha256": sha256_file(config_path),
        "input_bindings": input_bindings,
    }
    if STRUCTURE_REVIEW_DIMENSION in review_dimensions:
        # Schema metadata is opt-in so rerunning a historical five-field config
        # preserves its exact key and manifest serialization.
        manifest["packet_hash_mode"] = packet_hash_mode
        manifest["review_schema_sha256"] = schema_hash
        manifest["review_schema_id"] = schema_id
        manifest["key_core_sha256"] = key_core_hash
    (output_dir / "BLINDED_ROWS.jsonl").write_text(rows_dump, encoding="utf-8")
    (output_dir / "BLIND_REVIEW.html").write_text(html_text, encoding="utf-8")
    (output_dir / "UNBLIND_KEY.json").write_text(key_text, encoding="utf-8")
    (output_dir / "MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    print(json.dumps(build_packet(args.config, overwrite=args.overwrite), indent=2))


if __name__ == "__main__":
    main()
