"""Freeze and render the v3.8 genre-aware placement canary.

This is a data-engineering/naturalness gate only.  It never loads model weights,
reads activations, trains a probe, or changes the frozen neutral templates.  The
private freeze plan contains source-text anchors; the public frozen config and
manifest contain only IDs, hashes, offsets, and aggregate metadata.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import tokenizers
import transformers
from transformers import AutoTokenizer

SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
from build_blind_review_packet import build_packet


BASE = Path(__file__).resolve().parents[1]
MARKERS = {"<STANCE_1>", "<STANCE_2>"}
HARD_PROMPT_EXCLUSIONS = {
    "strict_output_contract": re.compile(
        r"\b(only strings|no explanations?|exactly \d+|less than \d+ characters?|"
        r"one sentence only|output only|must end with)\b", re.I
    ),
    "creative_roleplay_voice": re.compile(
        r"\b(act as|assume you are|role[- ]?play|in a dialog(?:ue)?)\b", re.I
    ),
}
SUPPORTED_PROTECTED_KINDS = {"list_block", "code_fence"}
DEFERRED_PROTECTED_KINDS = {"markdown_table", "dialogue", "indented_code"}


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(value: Any) -> str:
    return sha256_text(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")))


def resolve(raw: str | Path) -> Path:
    path = Path(raw)
    return path if path.is_absolute() else BASE / path


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def strip_stance_markers(text: str) -> str:
    """Remove only exact standalone placeholders; preserve every other byte."""
    return "".join(
        line
        for line in text.splitlines(keepends=True)
        if line.rstrip("\r\n") not in MARKERS
    )


def protected_ranges(text: str) -> list[dict[str, Any]]:
    """Return fail-closed ranges for code, tables, lists, dialogue, math, JSON/XML."""
    lines = text.splitlines(keepends=True)
    starts: list[int] = []
    cursor = 0
    for line in lines:
        starts.append(cursor)
        cursor += len(line)
    ranges: list[dict[str, Any]] = []
    in_fence = False
    fence_start = 0
    list_start: int | None = None
    for i, line in enumerate(lines):
        bare = line.rstrip("\r\n")
        start, end = starts[i], starts[i] + len(line)
        if re.match(r"^\s*```", bare):
            if not in_fence:
                in_fence, fence_start = True, start
            else:
                ranges.append({"kind": "code_fence", "start": fence_start, "end": end})
                in_fence = False
            continue
        if in_fence:
            continue
        is_list = bool(re.match(r"^\s*(?:[-*+] |\d+[.)]\s+)", bare))
        if is_list and list_start is None:
            list_start = start
        if list_start is not None and not is_list and bare.strip():
            ranges.append({"kind": "list_block", "start": list_start, "end": start})
            list_start = None
        if re.match(r"^\s*[A-Z][\w .'-]{0,30}:\s*[\"'\u201c]", bare):
            ranges.append({"kind": "dialogue", "start": start, "end": end})
        if bare.count("|") >= 2:
            ranges.append({"kind": "markdown_table", "start": start, "end": end})
        if re.match(r"^\s{4,}\S", bare):
            ranges.append({"kind": "indented_code", "start": start, "end": end})
        if re.match(r"^\s*(?:\$\$|\\\[|\\begin\{)", bare):
            ranges.append({"kind": "display_math", "start": start, "end": end})
        if re.match(r"^\s*[\[{<]", bare) and re.search(r"[:=>]", bare):
            ranges.append({"kind": "json_or_xml", "start": start, "end": end})
    if in_fence:
        ranges.append({"kind": "unclosed_code_fence", "start": fence_start, "end": len(text)})
    if list_start is not None:
        ranges.append({"kind": "list_block", "start": list_start, "end": len(text)})
    # Consecutive table rows and speaker turns are one protected object.  This
    # prevents a future caller from treating an internal row/turn boundary as a
    # safe insertion point even though these genres remain outside v3.8 scope.
    merged: list[dict[str, Any]] = []
    for kind in sorted(DEFERRED_PROTECTED_KINDS):
        kind_ranges = sorted(
            (dict(item) for item in ranges if item["kind"] == kind),
            key=lambda item: (item["start"], item["end"]),
        )
        for item in kind_ranges:
            if (
                merged
                and merged[-1]["kind"] == kind
                and not text[merged[-1]["end"] : item["start"]].strip()
            ):
                merged[-1]["end"] = max(merged[-1]["end"], item["end"])
            else:
                merged.append(item)
    merged.extend(
        dict(item) for item in ranges if item["kind"] not in DEFERRED_PROTECTED_KINDS
    )
    return sorted(merged, key=lambda item: (item["start"], item["end"], item["kind"]))


def structural_fingerprint(text: str) -> dict[str, Any]:
    ranges = protected_ranges(text)
    return {
        "text_sha256": sha256_text(text),
        "length_chars": len(text),
        "newline_count": text.count("\n"),
        "protected_ranges": ranges,
        "protected_ranges_sha256": canonical_hash(ranges),
        "protected_kind_counts": dict(sorted(Counter(x["kind"] for x in ranges).items())),
    }


def renderer_scope_coverage(entries: list[dict[str, Any]]) -> dict[str, Any]:
    """Validate the narrow v3.8 genre scope and return text-free coverage."""
    coverage: dict[str, Any] = {}
    unsupported: list[str] = []
    for arm in ("main", "control"):
        source_counts = Counter()
        range_counts = Counter()
        for entry in entries:
            kinds = entry[f"{arm}_structure"]["protected_kind_counts"]
            range_counts.update(kinds)
            present = set(kinds)
            source_counts["plain_prose_only"] += int(not present)
            source_counts["contains_list"] += int("list_block" in present)
            source_counts["contains_fenced_code"] += int("code_fence" in present)
            source_counts["contains_indented_code"] += int("indented_code" in present)
            source_counts["contains_markdown_table"] += int(
                "markdown_table" in present
            )
            source_counts["contains_dialogue"] += int("dialogue" in present)
            other = present - SUPPORTED_PROTECTED_KINDS - DEFERRED_PROTECTED_KINDS
            source_counts["contains_other_unsupported"] += int(bool(other))
            bad = present - SUPPORTED_PROTECTED_KINDS
            if bad:
                unsupported.append(
                    f"{entry['production_slot']}:{arm}:{','.join(sorted(bad))}"
                )
        coverage[arm] = {
            "sources": dict(sorted(source_counts.items())),
            "protected_ranges": dict(sorted(range_counts.items())),
        }
    if unsupported:
        raise ValueError(
            "Selected bases exceed prose/list/fenced-code renderer scope: "
            + "; ".join(unsupported)
        )
    return coverage


def renderer_scope_definition(coverage: dict[str, Any]) -> dict[str, Any]:
    return {
        "scope_version": "v38-prose-list-fenced-code-only-1",
        "eligible_response_structures": ["plain_prose", "list", "fenced_code"],
        "eligible_protected_kinds": sorted(SUPPORTED_PROTECTED_KINDS),
        "deferred_ineligible_structures": sorted(DEFERRED_PROTECTED_KINDS),
        "separate_canary_required_before_inclusion": sorted(
            DEFERRED_PROTECTED_KINDS
        ),
        "selected_coverage": coverage,
        "gate_pass_authorizes": "rerender_and_review_of_eligible_prose_list_fenced_code_sources_only",
        "gate_pass_authorizes_all_100_without_rescreening": False,
    }


def validate_offset(text: str, offset: int, style: str) -> None:
    if not 0 <= offset <= len(text):
        raise ValueError(f"Insertion offset {offset} outside [0,{len(text)}]")
    for item in protected_ranges(text):
        if item["start"] < offset < item["end"]:
            raise ValueError(f"Insertion at {offset} is inside {item['kind']} {item['start']}:{item['end']}")
    if style == "paragraph" and offset not in {0, len(text)}:
        if text[offset - 1] != "\n" and text[offset - 1] not in ".!?":
            raise ValueError(f"Paragraph insertion {offset} is not a structural/sentence boundary")
    if style == "inline_sentence" and offset not in {0, len(text)}:
        prefix = text[:offset].rstrip()
        if not prefix or prefix[-1] not in ".!?":
            raise ValueError(f"Inline insertion {offset} does not follow a completed sentence")
    # Never separate an introducing colon from a following protected object.
    prefix = text[:offset].rstrip()
    suffix = text[offset:].lstrip()
    if prefix.endswith(":") and (suffix.startswith("```") or re.match(r"(?:[-*+] |\d+[.)]\s+)", suffix)):
        raise ValueError("Insertion would separate an introduction from code/list content")


def locate(text: str, spec: dict[str, Any]) -> int:
    kind = spec["kind"]
    if kind == "start":
        return 0
    if kind == "end":
        return len(text)
    if kind == "before_anchor":
        anchor = spec["anchor"]
        if text.count(anchor) != 1:
            raise ValueError(f"Expected one private anchor, found {text.count(anchor)}")
        return text.index(anchor)
    raise ValueError(f"Unknown locator kind: {kind}")


def cue_bank() -> dict[str, Any]:
    return {
        "confidence": {
            "single": ["I have high confidence in this {referent} as a whole{qualification}.", "I have limited confidence in this {referent} as a whole{qualification}."],
            "distributed": [["I have high confidence in the {referent} that follows{qualification}.", "Overall, my confidence in it remains high."], ["I have limited confidence in the {referent} that follows{qualification}.", "Overall, my confidence in it remains limited."]],
        },
        "certainty": {
            "single": ["I am certain about this {referent} as presented{qualification}.", "I am uncertain about this {referent} as presented{qualification}."],
            "distributed": [["I am certain about the {referent} that follows{qualification}.", "Taken together, I remain certain about it."], ["I am uncertain about the {referent} that follows{qualification}.", "Taken together, I remain uncertain about it."]],
        },
        "stand": {
            "single": ["I confidently stand behind this {referent}{qualification}.", "I cautiously stand behind this {referent}{qualification}."],
            "distributed": [["I confidently stand behind the {referent} that follows{qualification}.", "Overall, it remains a position I fully endorse."], ["I cautiously stand behind the {referent} that follows{qualification}.", "Overall, it remains a position I cautiously endorse."]],
        },
        "view": {
            "single": ["This {referent}, as stated{qualification}, is my settled view.", "This {referent}, as stated{qualification}, is my provisional view."],
            "distributed": [["The {referent} that follows reflects my settled view{qualification}.", "Taken together, it remains my firm position."], ["The {referent} that follows reflects my provisional view{qualification}.", "Taken together, it remains my tentative position."]],
        },
        "doubt": {
            "single": ["Overall, I have little doubt about this {referent}{qualification}.", "Overall, I have some doubt about this {referent}{qualification}."],
            "distributed": [["I have little doubt about the {referent} that follows{qualification}.", "Overall, it leaves me with little doubt."], ["I have some doubt about the {referent} that follows{qualification}.", "Overall, it leaves me with some doubt."]],
        },
    }


def format_cues(entry: dict[str, Any], bank: dict[str, Any]) -> tuple[list[str], list[str]]:
    kind = "distributed" if entry["topology"] == "distributed" else "single"
    confident, hedged = bank[entry["cue_family"]][kind]
    if kind == "single":
        confident, hedged = [confident], [hedged]
    qualification = ", including its stated qualifications" if entry["include_qualifications"] else ""
    values = {"referent": entry["cue_referent"], "qualification": qualification}
    return [x.format(**values) for x in confident], [x.format(**values) for x in hedged]


def freeze(plan_path: Path, output_path: Path) -> dict[str, Any]:
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    source_path, neutral_path = resolve(plan["source_path"]), resolve(plan["neutral_path"])
    diagnostic_path = resolve(plan["prior_diagnostic_path"])
    diagnostic_key_path = resolve(plan["prior_unblind_key_path"])
    protocol_path = resolve(plan["protocol_path"])
    sources = load_jsonl(source_path)
    neutral_payload = json.loads(neutral_path.read_text(encoding="utf-8"))
    source_by_slot = {x["production_slot"]: x for x in sources}
    neutral_by_slot = {x["production_slot"]: x for x in neutral_payload["records"]}
    diagnostic = json.loads(diagnostic_path.read_text(encoding="utf-8"))
    diagnostic_key = json.loads(diagnostic_key_path.read_text(encoding="utf-8"))
    review_to_source = {x["review_id"]: x["source_id"] for x in diagnostic_key["pairs"]}
    diagnostic_by_source = {
        review_to_source[x["review_id"]]: x for x in diagnostic["reviews"]
    }
    bank = cue_bank()
    tokenizer_dir = resolve(plan["tokenizer"]["snapshot_path"])
    tokenizer_files = {
        name: sha256_file(tokenizer_dir / name)
        for name in ["tokenizer.json", "tokenizer_config.json", "vocab.json", "merges.txt"]
    }
    selected = []
    for spec in plan["selection"]:
        source = source_by_slot[spec["production_slot"]]
        neutral = neutral_by_slot[spec["production_slot"]]
        if source["source_id"] != neutral["source_id"]:
            raise ValueError(f"Source mismatch: {spec['production_slot']}")
        for code, pattern in HARD_PROMPT_EXCLUSIONS.items():
            if pattern.search(source["prompt"]):
                raise ValueError(f"Selected source triggers {code}: {spec['production_slot']}")
        prior_review = diagnostic_by_source.get(source["source_id"])
        if spec["cohort"] == "development_stress" and prior_review is None:
            raise ValueError(f"Stress source was not in the prior diagnostic: {spec['production_slot']}")
        if spec["cohort"] == "fresh_diagnostic" and prior_review is not None:
            raise ValueError(f"Fresh source was already in the prior diagnostic: {spec['production_slot']}")
        main_base = strip_stance_markers(neutral["shared_template"])
        control_base = source["original_response"]
        offsets: dict[str, list[int]] = {}
        styles: dict[str, list[str]] = {}
        for arm, base in [("main", main_base), ("control", control_base)]:
            placements = spec["placements"][arm]
            offsets[arm] = [locate(base, p) for p in placements]
            styles[arm] = [p["style"] for p in placements]
            for offset, style in zip(offsets[arm], styles[arm]):
                validate_offset(base, offset, style)
        entry = {
            key: value for key, value in spec.items() if key != "placements"
        }
        entry.update({
            "source_id_sha256": sha256_text(source["source_id"]),
            "original_response_sha256": source["original_response_sha256"],
            "neutral_base_sha256": sha256_text(main_base),
            "main_offsets": offsets["main"],
            "control_offsets": offsets["control"],
            "main_styles": styles["main"],
            "control_styles": styles["control"],
            "main_structure": structural_fingerprint(main_base),
            "control_structure": structural_fingerprint(control_base),
            "eligibility": "eligible",
            "eligibility_reason_codes": [],
            "prior_diagnostic_decision": prior_review.get("decision") if prior_review else None,
        })
        selected.append(entry)
    scope = renderer_scope_definition(renderer_scope_coverage(selected))
    config = {
        "protocol_version": "genre-aware-placement-canary-v3.8",
        "frozen": True,
        "frozen_date": plan["frozen_date"],
        "seed": plan["seed"],
        "purpose": "engineering_and_naturalness_gate_only",
        "gate_limitations": {
            "authorizes_probe_scoring": False,
            "authorizes_lofo_interpretation": False,
            "authorizes_population_claims": False,
            "authorizes_sdt_loss_training": False,
            "authorizes_renderer_application_to_all_100_sources": False,
            "table_dialogue_and_indented_code_require_separate_canaries": True,
            "lofo_reserved_for_fully_reviewed_100": True,
            "activation_not_inspected_before_freeze": True,
            "stress_set_role": "prior_diagnostic_development_set_6_failed_or_discuss_plus_4_accepted_controls",
            "fresh_set_role": "fresh_diagnostic_subset_not_unbiased_test",
        },
        "builder": {"path": "src/build_genre_aware_canary_v38.py", "file_sha256": sha256_file(Path(__file__))},
        "review_tooling": {
            "builder": {"path": "src/build_blind_review_packet.py", "file_sha256": sha256_file(SRC_DIR / "build_blind_review_packet.py")},
            "importer": {"path": "src/import_blind_review.py", "file_sha256": sha256_file(SRC_DIR / "import_blind_review.py")},
        },
        "protocol": {"path": plan["protocol_path"], "file_sha256": sha256_file(protocol_path)},
        "structure_algorithm_version": "protected-ranges-v38-2",
        "renderer_scope": scope,
        "inputs": {
            "source": {"path": plan["source_path"], "file_sha256": sha256_file(source_path), "records_sha256": canonical_hash(sources)},
            "neutral": {"path": plan["neutral_path"], "file_sha256": sha256_file(neutral_path), "records_sha256": neutral_payload["records_sha256"]},
            "prior_diagnostic": {"path": plan["prior_diagnostic_path"], "file_sha256": sha256_file(diagnostic_path)},
            "prior_unblind_key": {"path": plan["prior_unblind_key_path"], "file_sha256": sha256_file(diagnostic_key_path)},
        },
        "tokenizer": {
            **plan["tokenizer"], "artifact_sha256": tokenizer_files,
            "transformers_version": transformers.__version__,
            "tokenizers_version": tokenizers.__version__,
        },
        "eligibility_reason_taxonomy": plan["eligibility_reason_taxonomy"],
        "screened_exclusions": plan["screened_exclusions"],
        "cue_bank": bank,
        "cue_bank_sha256": canonical_hash(bank),
        "selection": selected,
        "outputs": plan["outputs"],
    }
    config["selection_sha256"] = canonical_hash(selected)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return config


def separator(base: str, offset: int, cue: str, style: str) -> tuple[str, int, int]:
    if style == "inline_sentence":
        insertion = cue + " "
        return insertion, 0, len(cue)
    left = "" if offset == 0 or base[:offset].endswith("\n\n") else ("\n" if base[:offset].endswith("\n") else "\n\n")
    right = "" if offset == len(base) or base[offset:].startswith("\n\n") else ("\n" if base[offset:].startswith("\n") else "\n\n")
    insertion = left + cue + right
    return insertion, len(left), len(left) + len(cue)


def render_with_spans(base: str, offsets: list[int], styles: list[str], cues: list[str]) -> tuple[str, list[dict[str, int]], list[dict[str, int]]]:
    if not (len(offsets) == len(styles) == len(cues)):
        raise ValueError("Cue/offset/style length mismatch")
    result, shift = base, 0
    cue_spans, insertion_spans = [], []
    for offset, style, cue in sorted(zip(offsets, styles, cues), key=lambda x: x[0]):
        insertion, cue_start, cue_end = separator(base, offset, cue, style)
        at = offset + shift
        result = result[:at] + insertion + result[at:]
        insertion_spans.append({"start": at, "end": at + len(insertion)})
        cue_spans.append({"start": at + cue_start, "end": at + cue_end})
        shift += len(insertion)
    return result, cue_spans, insertion_spans


def remove_spans(text: str, spans: list[dict[str, int]]) -> str:
    for span in sorted(spans, key=lambda x: x["start"], reverse=True):
        text = text[:span["start"]] + text[span["end"]:]
    return text


def validate_quotas(entries: list[dict[str, Any]]) -> dict[str, Any]:
    observed = {
        "task": Counter(x["task"] for x in entries),
        "topology": Counter(x["topology"] for x in entries),
        "dataset": Counter(x["dataset"] for x in entries),
        "cohort": Counter(x["cohort"] for x in entries),
        "cue_family": Counter(x["cue_family"] for x in entries),
        "pair_presentation_order": Counter(x["pair_presentation_order"] for x in entries),
    }
    expected = {
        "task": {x: 4 for x in ["comparison_analysis", "factual_explanation", "math_logic", "programming", "summary_judgment"]},
        "topology": {x: 5 for x in ["early", "middle", "late", "distributed"]},
        "dataset": {"allenai/WildChat-1M": 15, "nvidia/HelpSteer2": 5},
        "cohort": {"development_stress": 10, "fresh_diagnostic": 10},
        "cue_family": {x: 4 for x in ["confidence", "certainty", "stand", "view", "doubt"]},
        "pair_presentation_order": {"confident_first": 10, "hedged_first": 10},
    }
    normalized = {k: dict(v) for k, v in observed.items()}
    if normalized != expected:
        raise ValueError(f"Quota mismatch: {normalized}")
    for topology in expected["topology"]:
        if Counter(x["cue_family"] for x in entries if x["topology"] == topology) != Counter(expected["cue_family"].keys()):
            raise ValueError(f"Cue families not balanced within {topology}")
    return normalized


def write_pair_payload(path: Path, protocol: str, records: list[dict[str, Any]]) -> dict[str, Any]:
    payload = {"protocol_version": protocol, "records": records, "records_sha256": canonical_hash(records)}
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return payload


def render(config_path: Path) -> dict[str, Any]:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    if not config.get("frozen") or not config["gate_limitations"].get("activation_not_inspected_before_freeze"):
        raise ValueError("Refusing to render an unfrozen or activation-informed config")
    if sha256_file(resolve(config["builder"]["path"])) != config["builder"]["file_sha256"]:
        raise ValueError("Frozen builder changed")
    for name, binding in config["review_tooling"].items():
        if sha256_file(resolve(binding["path"])) != binding["file_sha256"]:
            raise ValueError(f"Frozen review {name} changed")
    if sha256_file(resolve(config["protocol"]["path"])) != config["protocol"]["file_sha256"]:
        raise ValueError("Frozen protocol changed")
    for name in ["source", "neutral", "prior_diagnostic", "prior_unblind_key"]:
        path = resolve(config["inputs"][name]["path"])
        if sha256_file(path) != config["inputs"][name]["file_sha256"]:
            raise ValueError(f"Frozen {name} input changed")
    source_path, neutral_path = resolve(config["inputs"]["source"]["path"]), resolve(config["inputs"]["neutral"]["path"])
    sources = load_jsonl(source_path)
    if canonical_hash(sources) != config["inputs"]["source"]["records_sha256"]:
        raise ValueError("Source record hash changed")
    neutral_payload = json.loads(neutral_path.read_text(encoding="utf-8"))
    if neutral_payload["records_sha256"] != config["inputs"]["neutral"]["records_sha256"]:
        raise ValueError("Neutral record hash changed")
    source_by_slot = {x["production_slot"]: x for x in sources}
    neutral_by_slot = {x["production_slot"]: x for x in neutral_payload["records"]}
    tokenizer_dir = resolve(config["tokenizer"]["snapshot_path"])
    for name, expected in config["tokenizer"]["artifact_sha256"].items():
        if sha256_file(tokenizer_dir / name) != expected:
            raise ValueError(f"Tokenizer artifact changed: {name}")
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_dir, local_files_only=True)
    quotas = validate_quotas(config["selection"])
    observed_scope = renderer_scope_definition(
        renderer_scope_coverage(config["selection"])
    )
    if observed_scope != config.get("renderer_scope"):
        raise ValueError("Frozen renderer scope or selected coverage changed")
    if canonical_hash(config["selection"]) != config["selection_sha256"]:
        raise ValueError("Frozen selection changed")
    output_dir = resolve(config["outputs"]["private_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    source_rows, main_records, control_records, audit_rows = [], [], [], []
    cue_pair_renderings: set[tuple[tuple[str, ...], tuple[str, ...]]] = set()
    confident_cue_sentences: set[str] = set()
    hedged_cue_sentences: set[str] = set()
    for entry in config["selection"]:
        source, neutral = source_by_slot[entry["production_slot"]], neutral_by_slot[entry["production_slot"]]
        if sha256_text(source["source_id"]) != entry["source_id_sha256"] or source["original_response_sha256"] != entry["original_response_sha256"]:
            raise ValueError(f"Frozen source mismatch: {entry['production_slot']}")
        main_base, control_base = strip_stance_markers(neutral["shared_template"]), source["original_response"]
        if structural_fingerprint(main_base) != entry["main_structure"] or structural_fingerprint(control_base) != entry["control_structure"]:
            raise ValueError(f"Structural fingerprint mismatch: {entry['production_slot']}")
        confident_cues, hedged_cues = format_cues(entry, config["cue_bank"])
        cue_pair_renderings.add((tuple(confident_cues), tuple(hedged_cues)))
        confident_cue_sentences.update(confident_cues)
        hedged_cue_sentences.update(hedged_cues)
        arm_records = {}
        for arm, base, offsets, styles in [
            ("main", main_base, entry["main_offsets"], entry["main_styles"]),
            ("control", control_base, entry["control_offsets"], entry["control_styles"]),
        ]:
            for offset, style in zip(offsets, styles):
                validate_offset(base, offset, style)
            confident, cspans, cinsert = render_with_spans(base, offsets, styles, confident_cues)
            hedged, hspans, hinsert = render_with_spans(base, offsets, styles, hedged_cues)
            if remove_spans(confident, cinsert) != base or remove_spans(hedged, hinsert) != base:
                raise ValueError(f"Non-cue bytes changed: {entry['production_slot']} {arm}")
            ct = len(tokenizer.encode(confident, add_special_tokens=False))
            ht = len(tokenizer.encode(hedged, add_special_tokens=False))
            if ct != ht:
                raise ValueError(f"Rendered token parity failed: {entry['production_slot']} {arm}: {ct} != {ht}")
            base_tokens = max(1, len(tokenizer.encode(base, add_special_tokens=False)))
            ratios = [len(tokenizer.encode(base[:x], add_special_tokens=False)) / base_tokens for x in offsets]
            topo = entry["topology"]
            if topo == "early" and not (len(ratios) == 1 and ratios[0] <= .25): raise ValueError("early placement invalid")
            if topo == "middle" and not (len(ratios) == 1 and .30 <= ratios[0] <= .70): raise ValueError("middle placement invalid")
            if topo == "late" and not (len(ratios) == 1 and ratios[0] >= .70): raise ValueError("late placement invalid")
            if topo == "distributed" and not (len(ratios) == 2 and ratios[0] <= .15 and ratios[1] >= .45 and ratios[1] - ratios[0] >= .40): raise ValueError("distributed placement invalid")
            arm_records[arm] = {
                "source_id": source["source_id"],
                "production_slot": entry["production_slot"],
                "original_response_sha256": source["original_response_sha256"],
                "status": "accepted",
                "cohort": entry["cohort"],
                "task": entry["task"], "dataset": entry["dataset"], "topology": topo,
                "cue_family": entry["cue_family"], "cue_referent": entry["cue_referent"],
                "pair_presentation_order": entry["pair_presentation_order"],
                "base_sha256": sha256_text(base), "insertion_offsets": offsets,
                "confident_response": confident, "hedged_response": hedged,
                "confident_response_sha256": sha256_text(confident), "hedged_response_sha256": sha256_text(hedged),
                "confident_cue_spans": cspans, "hedged_cue_spans": hspans,
                "confident_insertion_spans": cinsert, "hedged_insertion_spans": hinsert,
                "token_counts": {"confident": ct, "hedged": ht}, "placement_token_ratios": ratios,
                "factual_validity_note": entry.get("factual_validity_note"),
            }
        main_records.append(arm_records["main"]); control_records.append(arm_records["control"])
        source_rows.append({k: source[k] for k in ["source_id", "production_slot", "task", "dataset", "prompt", "original_response", "original_response_sha256"]})
        audit_rows.append({
            "production_slot": entry["production_slot"], "source_id_sha256": entry["source_id_sha256"],
            "eligibility": entry["eligibility"], "reason_codes": entry["eligibility_reason_codes"],
            "main_structure": entry["main_structure"], "control_structure": entry["control_structure"],
            "main_offsets": entry["main_offsets"], "control_offsets": entry["control_offsets"],
        })
    source_file = output_dir / "SOURCE_20.jsonl"
    source_file.write_text("".join(json.dumps(x, ensure_ascii=False, sort_keys=True) + "\n" for x in source_rows), encoding="utf-8")
    main_file, control_file = output_dir / "FINAL_MAIN_20.json", output_dir / "FINAL_CUE_ONLY_CONTROL_20.json"
    main_payload = write_pair_payload(main_file, config["protocol_version"] + "-main", main_records)
    control_payload = write_pair_payload(control_file, config["protocol_version"] + "-cue-only-control", control_records)
    audit_file = output_dir / "ELIGIBILITY_AND_STRUCTURE_AUDIT.json"
    audit_file.write_text(json.dumps({"records": audit_rows, "screened_exclusions": config["screened_exclusions"]}, indent=2) + "\n", encoding="utf-8")
    review_manifests = {}
    for arm, pair_file, payload, review_seed in [
        ("main", main_file, main_payload, int(config["seed"]) + 1),
        ("control", control_file, control_payload, int(config["seed"]) + 2),
    ]:
        review_config = {
            "title": f"v3.8 {arm} blind engineering review",
            "seed": review_seed,
            "expected_pairs": 20,
            "review_schema": {
                "schema_id": "v38-six-field-structure-v1",
                "include_structure_format": True,
            },
            "source_files": [{"path": str(source_file.relative_to(BASE)), "file_sha256": sha256_file(source_file)}],
            "pair_batches": [{"cohort": "development_stress" if False else f"v38_{arm}", "path": str(pair_file.relative_to(BASE)), "file_sha256": sha256_file(pair_file), "records_sha256": payload["records_sha256"]}],
            "output_dir": str((output_dir / f"review_{arm}").relative_to(BASE)),
        }
        review_config_path = output_dir / f"REVIEW_CONFIG_{arm.upper()}.json"
        review_config_path.write_text(json.dumps(review_config, indent=2) + "\n", encoding="utf-8")
        review_manifests[arm] = build_packet(review_config_path, base=BASE, overwrite=True)
    public_manifest = {
        "protocol_version": config["protocol_version"],
        "config_sha256": sha256_file(config_path),
        "builder_sha256": config["builder"]["file_sha256"],
        "review_tooling_sha256": {
            name: binding["file_sha256"] for name, binding in config["review_tooling"].items()
        },
        "protocol_sha256": config["protocol"]["file_sha256"],
        "selection_sha256": config["selection_sha256"],
        "contains_source_or_response_text": False,
        "purpose": config["purpose"], "gate_limitations": config["gate_limitations"],
        "renderer_scope": config["renderer_scope"],
        "selection_count": 20, "quota_counts": quotas,
        "cue_diversity": {
            "contains_cue_text": False,
            "unique_cue_pair_renderings": len(cue_pair_renderings),
            "unique_confident_cue_sentences": len(confident_cue_sentences),
            "unique_hedged_cue_sentences": len(hedged_cue_sentences),
        },
        "selected": [{
            "production_slot": x["production_slot"], "source_id_sha256": x["source_id_sha256"],
            "original_response_sha256": x["original_response_sha256"], "neutral_base_sha256": x["neutral_base_sha256"],
            "task": x["task"], "dataset": x["dataset"], "topology": x["topology"],
            "cue_family": x["cue_family"], "cohort": x["cohort"],
            "main_offsets": x["main_offsets"], "control_offsets": x["control_offsets"],
        } for x in config["selection"]],
        "private_artifact_hashes": {
            "source_20": sha256_file(source_file), "main_pairs": sha256_file(main_file),
            "control_pairs": sha256_file(control_file), "eligibility_audit": sha256_file(audit_file),
        },
        "review_packets": {arm: {k: m[k] for k in [
            "packet_sha256", "unblind_key_sha256", "pairs", "human_review",
            "review_schema_id", "review_schema_sha256", "key_core_sha256",
            "packet_hash_mode",
            "review_dimensions",
        ]} for arm, m in review_manifests.items()},
        "human_gate_status": "pending",
        "pass_rule": "20/20 content, intended direction, naturalness, global scope, and structure/format; any failure triggers repair and a fresh canary",
    }
    manifest_path = resolve(config["outputs"]["public_manifest"])
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(public_manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return public_manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    freeze_parser = sub.add_parser("freeze")
    freeze_parser.add_argument("--plan", type=Path, required=True)
    freeze_parser.add_argument("--output", type=Path, required=True)
    render_parser = sub.add_parser("render")
    render_parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()
    result = freeze(args.plan, args.output) if args.command == "freeze" else render(args.config)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
