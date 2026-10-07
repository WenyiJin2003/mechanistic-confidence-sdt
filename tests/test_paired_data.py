"""The pilot data gates reject content changes and source leakage."""
from collections import Counter
from copy import deepcopy
import json
from pathlib import Path

from confidence_pilot.data_validation import (
    DOMAINS, SPLIT_SEED, construct_variants, validate_dataset,
)

ROOT = Path(__file__).resolve().parents[1]


def catalog(phase="a"):
    sources=[json.loads(line) for line in (ROOT/"data/paired_confidence/source_items.jsonl").read_text().splitlines()]
    variants=[json.loads(line) for line in (ROOT/"data/paired_confidence/variants.jsonl").read_text().splitlines()]
    families=["A","B"] if phase=="a" else ["A","B","C"]
    sources=[s for s in sources if phase=="b" or s["phase_a"]]
    ids={s["source_id"] for s in sources}
    variants=[v for v in variants if v["source_id"] in ids and v["rewrite_family"] in families]
    return sources,variants,{"phase":phase,"dataset":{"families":families}}


def test_complete_factorial_and_frozen_balanced_splits():
    for phase,total,expected in (("a",24,{"train":12,"validation":6,"test":6}),("b",120,{"train":72,"validation":24,"test":24})):
        sources,variants,config=catalog(phase)
        audit=validate_dataset(sources,variants,config)
        assert audit["passed"],audit["errors"]
        assert len(sources)==total
        assert audit["source_split_counts"]==expected
        assert audit["pair_preservation_fraction"]==1.0
        assert not audit["source_group_leakage"]
        for domain in DOMAINS:
            assert Counter(s[f"phase_{phase}_split"] for s in sources if s["domain"]==domain)=={k:v//3 for k,v in expected.items()}
        assert all(s["split_seed"]==SPLIT_SEED for s in sources)


def test_phase_a_mmlu_has_eight_subjects_and_stays_out_of_phase_b_test():
    sources,_,_=catalog()
    assert len({s["subject"] for s in sources if s["domain"]=="academic"})==8
    assert all(s["phase_b_split"]=="train" for s in sources)
    assert all(s["verification"]["phase_a_individually_reviewed"] for s in sources)


def test_variant_construction_reproducible_and_content_present_once():
    sources,variants,_=catalog("b")
    assert construct_variants(sources)==variants
    for v in variants:
        assert v["response_text"].count(v["answer_span_text"])==1
        assert v["split_group"]==v["source_id"]
    cell_counts=Counter((v["source_id"],v["correctness"],v["certainty"],v["rewrite_family"]) for v in variants)
    assert len(cell_counts)==1440 and set(cell_counts.values())=={1}


def test_gate_rejects_changed_answer_or_added_evidence():
    sources,variants,config=catalog()
    altered=deepcopy(variants)
    altered[0]["response_text"]+=" I verified this against an additional source."
    assert not validate_dataset(sources,altered,config)["passed"]
    altered=deepcopy(variants)
    altered[0]["answer_span_text"]="another answer"
    assert not validate_dataset(sources,altered,config)["passed"]


def test_gate_rejects_split_mismatch_and_duplicate_context():
    sources,variants,config=catalog()
    altered=deepcopy(variants); altered[0]["phase_a_split"]="test" if altered[0]["phase_a_split"]!="test" else "train"
    assert not validate_dataset(sources,altered,config)["passed"]
    altered_sources=deepcopy(sources)
    altered_sources[1]["context"]=altered_sources[0]["context"]
    audit=validate_dataset(altered_sources,variants,config)
    assert not audit["passed"] and audit["source_group_leakage"]


def test_phase_b_cell_cycle_answer_is_phase_not_character():
    sources,_,_=catalog("b")
    source=next(s for s in sources if s["domain"]=="academic" and s["verification"]["row_index"]==2723)
    assert source["correct_answer"]=="S phase"
    assert source["incorrect_answer"]=="G1 phase"
