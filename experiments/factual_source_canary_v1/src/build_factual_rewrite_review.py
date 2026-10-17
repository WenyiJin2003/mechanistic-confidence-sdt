"""Build a private label-blind review page for the 12-pair factual canary.

The reviewer sees the question, frozen source response, and randomized Version
A/B rewrites.  Source identities, construction metadata, intended roles, and
the A/B answer key are stored only in a separate private key file.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


BASE = Path(__file__).resolve().parents[1]
PRIVATE = (BASE / "private_data").resolve()
DEFAULT_CONFIG = BASE / "configs" / "rewrite_canary_v1.json"
EXPECTED_PAIRS = 12
REQUIRED_REVIEW_FIELDS = (
    "source_fidelity",
    "qualifier_preservation",
    "speaker_level_scope",
    "certainty_a",
    "certainty_b",
    "stronger_certainty",
    "naturalness_a",
    "naturalness_b",
    "formatting_mismatch",
    "shortcut_concern",
)
SOURCE_IDENTITY_FIELDS = (
    "source_hash",
    "original_response_sha256",
    "dataset",
    "cue_family",
    "length_direction",
    "draft_order",
)
ALLOWED_LENGTH_DIRECTIONS = {"confident_longer", "hesitant_longer"}


def _canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def sha256_value(value: Any) -> str:
    return hashlib.sha256(_canonical_json_bytes(value)).hexdigest()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _stable_digest(seed: int, purpose: str, *values: str) -> bytes:
    material = "\0".join((str(seed), purpose, *values)).encode("utf-8")
    return hashlib.sha256(material).digest()


def read_records(path: Path) -> list[dict[str, Any]]:
    """Read JSONL, a JSON list, or an object containing ``pairs``."""
    raw = Path(path).read_text(encoding="utf-8").strip()
    if not raw:
        return []
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        rows: list[dict[str, Any]] = []
        for line_number, line in enumerate(raw.splitlines(), 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"{path}:{line_number}: invalid JSON: {exc.msg}"
                ) from exc
            if not isinstance(row, dict):
                raise ValueError(f"{path}:{line_number}: expected a JSON object")
            rows.append(row)
        return rows
    if isinstance(parsed, list):
        rows = parsed
    elif isinstance(parsed, dict) and isinstance(parsed.get("pairs"), list):
        rows = parsed["pairs"]
    elif isinstance(parsed, dict):
        rows = [parsed]
    else:
        raise ValueError(f"{path}: expected JSONL, a list, or an object")
    if not all(isinstance(row, dict) for row in rows):
        raise ValueError(f"{path}: every record must be a JSON object")
    return list(rows)


def _index_unique(rows: Sequence[dict[str, Any]], field: str, label: str) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for row in rows:
        value = row.get(field)
        if not isinstance(value, str) or not value:
            raise ValueError(f"{label}: missing {field}")
        if value in indexed:
            raise ValueError(f"{label}: duplicate {field}: {value}")
        indexed[value] = row
    return indexed


def join_sources_and_pairs(
    source_rows: Sequence[dict[str, Any]],
    pair_rows: Sequence[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Validate and join exactly 12 frozen sources to 12 final rewrite pairs."""
    if len(source_rows) != EXPECTED_PAIRS or len(pair_rows) != EXPECTED_PAIRS:
        raise ValueError(
            f"blind review requires exactly {EXPECTED_PAIRS} sources and pairs"
        )
    sources = _index_unique(source_rows, "source_id", "sources")
    pairs = _index_unique(pair_rows, "source_id", "pairs")
    if set(sources) != set(pairs):
        raise ValueError("source and pair source_id sets do not match")

    joined: list[dict[str, Any]] = []
    for source_id in sorted(sources):
        source = sources[source_id]
        pair = pairs[source_id]
        prompt = source.get("prompt")
        original = source.get("original_response")
        confident = pair.get("confident_response")
        hesitant = pair.get("hesitant_response")
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError(f"{source_id}: missing prompt")
        if not isinstance(original, str) or not original.strip():
            raise ValueError(f"{source_id}: missing original_response")
        if not isinstance(confident, str) or not confident.strip():
            raise ValueError(f"{source_id}: missing confident_response")
        if not isinstance(hesitant, str) or not hesitant.strip():
            raise ValueError(f"{source_id}: missing hesitant_response")
        if confident == hesitant:
            raise ValueError(f"{source_id}: pair members are identical")
        if sha256_text(original) != source.get("original_response_sha256"):
            raise ValueError(f"{source_id}: frozen original response hash is invalid")
        for field in SOURCE_IDENTITY_FIELDS:
            if pair.get(field) != source.get(field):
                raise ValueError(f"{source_id}: {field} identity mismatch")
        if source.get("length_direction") not in ALLOWED_LENGTH_DIRECTIONS:
            raise ValueError(f"{source_id}: invalid length_direction")
        joined.append({
            **source,
            "confident_response": confident,
            "hesitant_response": hesitant,
        })
    return joined


def balanced_a_roles(rows: Sequence[dict[str, Any]], seed: int) -> dict[str, str]:
    """Assign exactly two A roles of each kind per four-record dataset.

    When each dataset contains two records per length direction, choose one
    confident-A record within each direction.  This prevents A/B role from
    becoming a proxy for which response is slightly longer.
    """
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        dataset = row.get("dataset")
        source_id = row.get("source_id")
        if not isinstance(dataset, str) or not dataset:
            raise ValueError("every row requires a dataset")
        if not isinstance(source_id, str) or not source_id:
            raise ValueError("every row requires a source_id")
        grouped[dataset].append(row)
    if sorted(len(values) for values in grouped.values()) != [4, 4, 4]:
        raise ValueError("review design requires three datasets with four rows each")

    roles: dict[str, str] = {}
    for dataset, members in sorted(grouped.items()):
        by_direction: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for member in members:
            by_direction[str(member.get("length_direction"))].append(member)
        balanced_directions = (
            set(by_direction) == ALLOWED_LENGTH_DIRECTIONS
            and all(len(group) == 2 for group in by_direction.values())
        )
        confident_a: set[str]
        if balanced_directions:
            confident_a = set()
            for direction, group in sorted(by_direction.items()):
                chosen = min(
                    group,
                    key=lambda row: _stable_digest(
                        seed,
                        "factual-review-a-role-within-direction",
                        dataset,
                        direction,
                        str(row["source_id"]),
                    ),
                )
                confident_a.add(str(chosen["source_id"]))
        else:
            ranked = sorted(
                members,
                key=lambda row: _stable_digest(
                    seed,
                    "factual-review-a-role",
                    dataset,
                    str(row["source_id"]),
                ),
            )
            confident_a = {str(row["source_id"]) for row in ranked[:2]}
        for member in members:
            source_id = str(member["source_id"])
            roles[source_id] = "confident" if source_id in confident_a else "hesitant"

    role_counts = Counter(roles.values())
    if role_counts != Counter({"confident": 6, "hesitant": 6}):
        raise AssertionError("A roles are not balanced 6/6")
    for dataset, members in grouped.items():
        counts = Counter(roles[str(row["source_id"])] for row in members)
        if counts != Counter({"confident": 2, "hesitant": 2}):
            raise AssertionError(f"{dataset}: A roles are not balanced 2/2")
    return roles


def build_blinded_rows(
    rows: Sequence[dict[str, Any]], seed: int
) -> tuple[list[dict[str, str]], list[dict[str, Any]]]:
    """Return reviewer-visible rows and a separate private answer key."""
    if len(rows) != EXPECTED_PAIRS:
        raise ValueError(f"expected exactly {EXPECTED_PAIRS} joined rows")
    a_roles = balanced_a_roles(rows, seed)
    ordered = sorted(
        rows,
        key=lambda row: _stable_digest(
            seed, "factual-review-packet-order", str(row["source_id"])
        ),
    )
    blinded: list[dict[str, str]] = []
    answer_key: list[dict[str, Any]] = []
    for index, row in enumerate(ordered, start=1):
        source_id = str(row["source_id"])
        a_role = a_roles[source_id]
        b_role = "hesitant" if a_role == "confident" else "confident"
        text = {
            "confident": str(row["confident_response"]),
            "hesitant": str(row["hesitant_response"]),
        }
        review_id = f"R{index:03d}"
        blinded.append({
            "review_id": review_id,
            "question": str(row["prompt"]),
            "original_response": str(row["original_response"]),
            "version_a": text[a_role],
            "version_b": text[b_role],
        })
        answer_key.append({
            "review_id": review_id,
            "source_id": source_id,
            "dataset": row["dataset"],
            "version_a_role": a_role,
            "version_b_role": b_role,
            "version_a_sha256": sha256_text(text[a_role]),
            "version_b_sha256": sha256_text(text[b_role]),
            "original_response_sha256": row["original_response_sha256"],
            "source_hash": row["source_hash"],
            "cue_family": row["cue_family"],
            "length_direction": row["length_direction"],
            "draft_order": row.get("draft_order"),
        })
    return blinded, answer_key


def _select(field: str, options: Iterable[tuple[str, str]]) -> str:
    option_html = '<option value="">Not reviewed</option>' + "".join(
        f'<option value="{html.escape(value, quote=True)}">{html.escape(label)}</option>'
        for value, label in options
    )
    return f'<select data-field="{html.escape(field, quote=True)}">{option_html}</select>'


def render_html(rows: Sequence[dict[str, str]], packet_sha256: str) -> str:
    """Render a self-contained page that contains no role or source key."""
    def esc(value: Any) -> str:
        return html.escape(str(value), quote=True)

    cards: list[str] = []
    identities: list[dict[str, str]] = []
    for index, row in enumerate(rows):
        review_id = row["review_id"]
        identities.append({"review_id": review_id})
        cards.append(f'''<article class="card" data-index="{index}" {'hidden' if index else ''}>
<div class="meta"><strong>{esc(review_id)}</strong></div>
<section class="source-block"><h2>Question</h2><pre>{esc(row['question'])}</pre></section>
<section class="source-block"><h2>Original response</h2><pre>{esc(row['original_response'])}</pre></section>
<div class="versions"><section><h2>Version A</h2><pre>{esc(row['version_a'])}</pre></section>
<section><h2>Version B</h2><pre>{esc(row['version_b'])}</pre></section></div>
<div class="review-grid">
<label>1. Source fidelity{_select('source_fidelity', [
    ('both_preserve', 'Both preserve every substantive source claim'),
    ('a_drift', 'A adds, removes, or changes substantive content'),
    ('b_drift', 'B adds, removes, or changes substantive content'),
    ('both_drift', 'Both drift from the source'),
    ('uncertain', 'Uncertain'),
])}</label>
<label>2. Qualifier preservation{_select('qualifier_preservation', [
    ('both_preserve', 'Both preserve qualifiers, scope, conditions, and exceptions'),
    ('a_changes', 'A changes qualifier meaning or scope'),
    ('b_changes', 'B changes qualifier meaning or scope'),
    ('both_change', 'Both change qualifier meaning or scope'),
    ('not_applicable', 'No meaningful qualifier in the source'),
    ('uncertain', 'Uncertain'),
])}</label>
<label>3. Speaker-level scope{_select('speaker_level_scope', [
    ('both_speaker_level', 'Both vary only the speaker’s commitment'),
    ('a_object_level_shift', 'A changes evidence, probability, causality, or obligation'),
    ('b_object_level_shift', 'B changes evidence, probability, causality, or obligation'),
    ('both_object_level_shift', 'Both change object-level force'),
    ('uncertain', 'Uncertain'),
])}</label>
<label>4. Certainty of A (1–5){_select('certainty_a', [
    ('1', '1 — strongly hesitant'), ('2', '2 — hesitant'),
    ('3', '3 — neutral/mixed'), ('4', '4 — certain'),
    ('5', '5 — strongly certain'),
])}</label>
<label>5. Certainty of B (1–5){_select('certainty_b', [
    ('1', '1 — strongly hesitant'), ('2', '2 — hesitant'),
    ('3', '3 — neutral/mixed'), ('4', '4 — certain'),
    ('5', '5 — strongly certain'),
])}</label>
<label>6. Which version is more certain?{_select('stronger_certainty', [
    ('a', 'A'), ('b', 'B'), ('tie', 'Tie / no clear difference'),
    ('uncertain', 'Uncertain'),
])}</label>
<label>7. Naturalness of A{_select('naturalness_a', [
    ('natural', 'Natural'), ('minor', 'Minor awkwardness'),
    ('unnatural', 'Unnatural'), ('uncertain', 'Uncertain'),
])}</label>
<label>8. Naturalness of B{_select('naturalness_b', [
    ('natural', 'Natural'), ('minor', 'Minor awkwardness'),
    ('unnatural', 'Unnatural'), ('uncertain', 'Uncertain'),
])}</label>
<label>9. Formatting mismatch{_select('formatting_mismatch', [
    ('none', 'None'), ('a', 'A only'), ('b', 'B only'),
    ('both', 'Both'), ('uncertain', 'Uncertain'),
])}</label>
<label>10. Shortcut concern{_select('shortcut_concern', [
    ('none', 'None; both read as complete rewrites'),
    ('a', 'A relies on a detachable or formulaic cue'),
    ('b', 'B relies on a detachable or formulaic cue'),
    ('both', 'Both rely on detachable or formulaic cues'),
    ('uncertain', 'Uncertain'),
])}</label>
</div>
<label class="notes">Notes<textarea data-field="notes" placeholder="Record any changed claim, qualifier, weak contrast, unnatural wording, format problem, or shortcut."></textarea></label>
</article>''')

    identities_json = json.dumps(identities, ensure_ascii=False).replace("<", "\\u003c")
    required_json = json.dumps(REQUIRED_REVIEW_FIELDS)
    export_name = f"factual_rewrite_blind_review_{len(rows)}.json"
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Factual rewrite blind review</title>
<style>
body{{margin:0;background:#f5f6f8;color:#17202b;font:16px/1.55 system-ui,-apple-system,sans-serif}}
main{{max-width:1500px;margin:auto;padding:24px}}h1{{font-size:27px;margin:0 0 8px}}.intro{{max-width:1080px}}
.notice{{background:#eef5ff;border-left:4px solid #2c62ae;padding:10px 14px;margin:14px 0}}
.toolbar{{display:flex;gap:10px;align-items:center;flex-wrap:wrap;position:sticky;top:0;background:#f5f6f8;padding:10px 0;z-index:2}}
button,select{{font:inherit;padding:7px;border:1px solid #bac3ce;border-radius:7px;background:white}}button{{cursor:pointer}}.primary{{background:#2454a4;color:white}}
.card{{background:white;border:1px solid #dce1e7;border-radius:12px;padding:20px}}.card[hidden]{{display:none}}.meta{{color:#536071;margin-bottom:12px}}
pre{{font:15px/1.6 ui-monospace,SFMono-Regular,monospace;white-space:pre-wrap;overflow-wrap:anywhere}}
.source-block{{background:#fffaf0;border:1px solid #e3dccd;border-radius:8px;padding:12px;margin-top:12px}}
.versions{{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:14px}}.versions section{{border:1px solid #dbe2eb;border-radius:8px;padding:12px;background:#fafbfd}}
h2{{font-size:17px;margin:0 0 8px}}.review-grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin-top:18px}}
.review-grid label{{display:flex;flex-direction:column;gap:6px}}.notes{{display:block;margin-top:14px}}textarea{{width:100%;min-height:82px;box-sizing:border-box;font:inherit;padding:8px}}
#progress{{font-weight:650}}@media(max-width:900px){{.versions,.review-grid{{grid-template-columns:1fr}}.toolbar{{position:static}}}}
</style></head><body><main>
<header><h1>Factual rewrite blind review</h1>
<p class="intro">Each card shows one frozen source response and two complete rewrites in randomized order. Compare both versions with the source before judging their certainty.</p>
<p class="notice"><strong>Main check:</strong> both versions must preserve the same factual content and proposition-level qualifiers. Their difference should concern only the speaker’s commitment, remain natural, and not rely on a detachable label sentence.</p></header>
<nav class="toolbar"><button id="prev">Previous</button><span id="position"></span><button id="next">Next</button>
<label>Jump <select id="jump"></select></label><span id="progress"></span>
<button class="primary" id="export">Download review JSON</button><span id="save-status"></span></nav>
{''.join(cards)}
</main><script>
const packetHash={json.dumps(packet_sha256)};const identities={identities_json};const required={required_json};
const storageKey='factual-rewrite-blind-review-'+packetHash;let reviews={{}};let current=0;let storageAvailable=true;
try{{reviews=JSON.parse(localStorage.getItem(storageKey)||'{{}}')}}catch(e){{storageAvailable=false}}
const cards=[...document.querySelectorAll('.card')];const jump=document.getElementById('jump');
identities.forEach((m,i)=>{{const o=document.createElement('option');o.value=i;o.textContent=m.review_id;jump.append(o)}});
function progress(){{const complete=identities.filter(m=>required.every(k=>(reviews[m.review_id]||{{}})[k])).length;document.getElementById('progress').textContent='Complete '+complete+' / '+identities.length;document.getElementById('save-status').textContent=storageAvailable?'Autosaved in this browser':'Browser storage unavailable; download often'}}
cards.forEach((card,i)=>card.querySelectorAll('[data-field]').forEach(el=>{{el.value=(reviews[identities[i].review_id]||{{}})[el.dataset.field]||'';el.addEventListener('input',()=>{{const id=identities[i].review_id;reviews[id]||={{}};reviews[id][el.dataset.field]=el.value;reviews[id].updated_at=new Date().toISOString();try{{localStorage.setItem(storageKey,JSON.stringify(reviews))}}catch(e){{storageAvailable=false}}progress()}})}}));
function show(i){{current=Math.max(0,Math.min(cards.length-1,i));cards.forEach((card,n)=>card.hidden=n!==current);jump.value=current;document.getElementById('position').textContent=(current+1)+' / '+cards.length;document.getElementById('prev').disabled=current===0;document.getElementById('next').disabled=current===cards.length-1;window.scrollTo(0,0)}}
document.getElementById('prev').onclick=()=>show(current-1);document.getElementById('next').onclick=()=>show(current+1);jump.onchange=()=>show(Number(jump.value));
document.getElementById('export').onclick=()=>{{const payload={{packet_sha256:packetHash,blinded:true,reviews:identities.map(m=>({{...m,...(reviews[m.review_id]||{{}})}}))}};const url=URL.createObjectURL(new Blob([JSON.stringify(payload,null,2)],{{type:'application/json'}}));const a=document.createElement('a');a.href=url;a.download={json.dumps(export_name)};a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)}};
show(0);progress();
</script></body></html>'''


def require_private_output(output_dir: Path, private_root: Path = PRIVATE) -> Path:
    output = Path(output_dir).resolve()
    root = Path(private_root).resolve()
    if output != root and root not in output.parents:
        raise ValueError(f"review output must stay under private_data: {root}")
    return output


def _write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_review_bundle(
    joined_rows: Sequence[dict[str, Any]],
    output_dir: Path,
    *,
    seed: int,
    overwrite: bool = False,
    private_root: Path = PRIVATE,
) -> dict[str, Any]:
    """Write HTML, separate answer key, and a private binding manifest."""
    output = require_private_output(output_dir, private_root)
    output.mkdir(parents=True, exist_ok=True)
    blinded, answer_key = build_blinded_rows(joined_rows, seed)
    packet_sha256 = sha256_value(blinded)
    html_text = render_html(blinded, packet_sha256)
    paths = {
        "html": output / "BLIND_REVIEW.html",
        "answer_key": output / "BLIND_REVIEW_KEY.json",
        "manifest": output / "BLIND_REVIEW_MANIFEST.json",
    }
    existing = [path for path in paths.values() if path.exists()]
    if existing and not overwrite:
        raise FileExistsError(
            "review bundle already exists: " + ", ".join(str(path) for path in existing)
        )
    paths["html"].write_text(html_text, encoding="utf-8")
    key_payload = {
        "schema": "factual-rewrite-blind-key-v1",
        "seed": seed,
        "packet_sha256": packet_sha256,
        "rows": answer_key,
    }
    _write_json(paths["answer_key"], key_payload)
    manifest = {
        "schema": "factual-rewrite-blind-review-v1",
        "seed": seed,
        "pair_count": len(blinded),
        "packet_sha256": packet_sha256,
        "html_sha256": sha256_file(paths["html"]),
        "answer_key_sha256": sha256_file(paths["answer_key"]),
        "version_a_role_counts": dict(sorted(Counter(
            row["version_a_role"] for row in answer_key
        ).items())),
        "version_a_role_counts_by_dataset": {
            dataset: dict(sorted(Counter(
                row["version_a_role"] for row in answer_key if row["dataset"] == dataset
            ).items()))
            for dataset in sorted({str(row["dataset"]) for row in answer_key})
        },
        "review_fields": list(REQUIRED_REVIEW_FIELDS) + ["notes"],
        "blinded": True,
        "answer_key_embedded_in_html": False,
        "human_review_certified": False,
    }
    _write_json(paths["manifest"], manifest)
    return {
        "paths": {name: str(path) for name, path in paths.items()},
        "manifest": manifest,
    }


def load_seed(config_path: Path) -> int:
    config = json.loads(Path(config_path).read_text(encoding="utf-8"))
    seed = config.get("seed") if isinstance(config, dict) else None
    if not isinstance(seed, int):
        raise ValueError("config requires an integer seed")
    return seed


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, required=True)
    parser.add_argument("--pairs", type=Path, required=True)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PRIVATE / "rewrite_canary_v1" / "blind_review",
    )
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args(argv)

    sources = read_records(args.sources)
    pairs = read_records(args.pairs)
    joined = join_sources_and_pairs(sources, pairs)
    result = write_review_bundle(
        joined,
        args.output_dir,
        seed=load_seed(args.config),
        overwrite=args.overwrite,
    )
    print(json.dumps(result["manifest"], ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
