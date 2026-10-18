"""Prepare a three-source, low-effort writer packet with optional WordNet hints.

This script performs local dictionary lookups only; it never calls a model.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

import nltk
from nltk.corpus import wordnet as wn


BASE = Path(__file__).resolve().parents[1]
PRIVATE = BASE / "private_data"
OUTPUT = PRIVATE / "rewrite_canary_v1" / "wordnet_luna_preview_v1"
RESOURCES = PRIVATE / "resources" / "nltk_data"
SEEDS = {"later": "r", "otherwise": "r", "permanently": "r", "recent": "a",
         "various": "a", "earlier": "a", "publicly": "r"}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def hints_for(text: str) -> list[dict]:
    """Return senses separately. Never flatten senses or alter input text."""
    words = set(re.findall(r"\b[a-z]+\b", text.lower()))
    hints = []
    for word, pos in SEEDS.items():
        if word not in words:
            continue
        senses = []
        for synset in wn.synsets(word, pos=pos)[:2]:
            choices = sorted({lemma.name().replace("_", " ") for lemma in synset.lemmas()
                              if lemma.name().replace("_", " ").lower() != word})
            if choices:
                senses.append({"synset": synset.name(), "definition": synset.definition(),
                               "candidates": choices[:3]})
        if senses:
            hints.append({"source_word": word, "senses": senses})
        if len(hints) == 2:
            break
    return hints


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refinement", action="store_true", help="Prepare the single bounded prompt-refinement batch")
    args = parser.parse_args()
    output = OUTPUT.with_name("wordnet_luna_preview_v2") if args.refinement else OUTPUT
    nltk.data.path.insert(0, str(RESOURCES))
    if wn.get_version() != "3.0":
        raise ValueError("expected WordNet 3.0")
    config_path = BASE / "configs" / ("economical_wordnet_preview_v2.json" if args.refinement else "economical_wordnet_preview_v1.json")
    config = json.loads(config_path.read_text(encoding="utf-8"))
    frozen_path = PRIVATE / "rewrite_canary_v1" / "frozen_sources_v4.jsonl"
    sources = [json.loads(line) for line in frozen_path.read_text(encoding="utf-8").splitlines()]
    # Short factual ASQA example, HEART bill, and factual-rich RobBERT abstract.
    selectors = [lambda r: r["dataset"] == "asqa" and r["profile"] == "short_simple",
                 lambda r: r["dataset"] == "billsum" and "HEART Act" in r["original_response"],
                 lambda r: r["dataset"] == "qasper" and "RobBERT" in r["original_response"]]
    selected = []
    for selector in selectors:
        matches = [row for row in sources if selector(row)]
        if len(matches) != 1:
            raise ValueError("development source selection must be unambiguous")
        selected.append(matches[0])
    source_rows, bindings = [], []
    for index, (source, length_direction) in enumerate(zip(selected, config["length_directions"]), 1):
        identifier = f"WP{index:03d}"
        hints = hints_for(source["original_response"])
        if args.refinement:
            # Manual context screen on this fixed three-source development set.
            # Retain only the temporal sense of "later"; reject other senses
            # and awkward/general hints rather than forcing a substitution.
            hints = [{"source_word": "later", "senses": [
                {**sense, "candidates": [c for c in sense["candidates"] if c in {"afterward", "afterwards"}]}
                for sense in hint["senses"] if sense["synset"] == "subsequently.r.01"
            ]} for hint in hints if hint["source_word"] == "later"]
        source_rows.append({"preview_id": identifier, "prompt": source["prompt"],
                            "original_response": source["original_response"],
                            "length_direction": length_direction,
                            "optional_wordnet_hints": hints})
        bindings.append({"preview_id": identifier, "source_id": source["source_id"],
                         "source_hash": source["source_hash"], "dataset": source["dataset"]})
    prompt_path = BASE / "prompts" / ("economical_rewrite_v2.txt" if args.refinement else "economical_rewrite_v1.txt")
    rule = prompt_path.read_text(encoding="utf-8")
    payload = {"sources": source_rows}
    output.mkdir(parents=True, exist_ok=True)
    if (output / "DRAFT_PAIRS.json").exists():
        raise FileExistsError("drafts already exist; do not overwrite a completed generation packet")
    write(output / "SOURCE_ONLY.json", payload)
    writer_prompt = rule + "\nINPUT_JSON\n" + json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    (output / "WRITER_PROMPT.txt").write_text(writer_prompt, encoding="utf-8")
    write(output / "INPUT_MANIFEST_PRIVATE.json", {
        "schema": "wordnet-luna-source-packet-v1", "source_count": 3,
        "nltk_version": nltk.__version__, "wordnet_version": wn.get_version(),
        "wordnet_resource_sha256": digest(RESOURCES / "corpora" / "wordnet.zip"),
        "source_pool_sha256": digest(frozen_path), "config_sha256": digest(config_path),
        "prompt_template_sha256": digest(prompt_path),
        "writer_prompt_sha256": digest(output / "WRITER_PROMPT.txt"),
        "source_only_sha256": digest(output / "SOURCE_ONLY.json"),
        "writer_model": config["writer_model"], "reasoning_effort": config["reasoning_effort"],
        "wordnet_role": config["wordnet_role"], "wordnet_auto_replacement": False,
        "prompt_revision": "v2_bounded_refinement" if args.refinement else "v1_initial",
        "wordnet_context_screen": "manual, source-specific; only temporal later retained" if args.refinement else "unscreened candidate senses; optional only",
        "bindings": bindings,
    })
    print(json.dumps({"source_count": 3, "writer_model": config["writer_model"],
                      "reasoning_effort": config["reasoning_effort"],
                      "writer_prompt_characters": len(writer_prompt),
                      "wordnet_hint_counts": [len(r["optional_wordnet_hints"]) for r in source_rows],
                      "model_calls_made": 0}))


if __name__ == "__main__":
    main()
