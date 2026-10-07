"""Frozen content-paired source catalog; no model generation or downloads."""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import random
import statistics
from typing import Any

VERSION = "paired-confidence-pilot-v1"
DOMAINS = ("factual_qa", "arithmetic", "academic")
MMLU_REVISION = "c30699e8356da336a370243923dbaf21066bb9fe"
MMLU_SHA256 = "74a41822ce7d3def56e1682f958469c04642a5336a5ce912fa375fdb90fb25d7"
SPLIT_SEED = 20261007

# First8 per domain are the individually reviewed Phase A subset. SQuAD
# correctness is explicitly relative to the provided passage.
SQUAD_CATALOG = [
    ("57286b003acd2414000df9c1", "Samarkand", "The passage names Karakorum, a different city."),
    ("5706149552bb891400689882", "2012", "Chivas were suspended following2014, not2012."),
    ("572fad30a23a5019007fc870", "1972", "Wilson's commitment is dated1974, not1972."),
    ("5710eb6fb654c5140001fa17", "Jamestown", "Charlesfort is the named first South Carolina outpost."),
    ("57264efddd62a815002e8135", "National Highway Designation Act", "The Energy Conservation Act imposed the limit; the distractor ended it."),
    ("57286bf84b864d19001649d5", "Philip Roth", "Studs Terkel is the named author of The Good War."),
    ("5728804b4b864d1900164a46", "1259", "Zhu Shijie's lifespan begins in1249."),
    ("571ccfbadd7acb1400e4c164", "helium", "The passage specifies electrolysis of water, not helium."),
    ("5730088e947a6a140053cfad", "biological", "Iqbal is described as ideological father."),
    ("572863363acd2414000df989", "female students", "International students comprise19%; female students44%."),
    ("572900f73f37b31900477f69", "photosynthesis", "Inflammation is the immune response; photosynthesis is not an immune response."),
    ("5737804dc3c5551400e51f12", "electric charges", "Gravity acts between masses; electric charges are assigned to electromagnetism."),
    ("572647d0708984140094c14b", "keratin", "The jelly-like material is mesoglea."),
    ("572fbfa504bcaa1900d76c73", "October", "April is the first of the two listed recess months."),
    ("57339eb9d058e614000b5ef7", "61", "The passage counts60 museums."),
    ("572f7588947a6a140053c988", "500 m", "The stated river width is400m."),
    ("572745c6708984140094db99", "reality into designs", "The stated translation is designs into reality, not its reversal."),
    ("57114dfb50c2381900b54a54", "closed loop", "Open-loop releases steam; closed-loop recycles fluid."),
    ("57339dd94776f41900660ece", "New Year's Eve", "Wianki is tied to Midsummer's Night/Eve."),
    ("57115ac550c2381900b54a7a", "piston steam", "Internal combustion replaced piston steam engines."),
    ("571153422419e31400955580", "Liverpool and Manchester Railway", "Salamanca is explicitly assigned to Middleton Railway."),
    ("5726e985dd62a815002e94dd", "Board Certified Nuclear Pharmacist", "The named certification is Ambulatory Care, not Nuclear."),
    ("573368044776f41900660a2c", "Praga Park", "Park Ujazdowski is explicitly near John Lennon street."),
    ("56de3dbacffd8e1900b4b6d2", "Norway", "The country described is Wales."),
    ("57096505ed30961900e84082", "Sky Q Mini", "Sky Q Hub is the router; Mini is a set-top box."),
    ("571095a8a58dae1900cd6a77", "1560", "The colony began in1555;1560 is its destruction."),
    ("5730b541396df919000962c2", "free trade", "Mercantilism is the First Empire policy; free trade is later."),
    ("5733a6ac4776f41900660f59", "1918", "The marriage is explicitly dated1916."),
    ("572ff935b2c2fd140056869e", "Rotterdam", "Brakel and Zaltbommel are the named towns."),
    ("5729ffda1d046914007796af", "blood transfusion", "Vaccination induces the named artificial active immunity."),
    ("572827fc3acd2414000df5bd", "males", "The ratios report fewer males than females."),
    ("572a213e6aef0514001552ef", "the starting point", "Growth and income are means rather than the end itself."),
    ("573098f38ab72b1400f9c5d2", "resource depletion", "The named focus is economic growth."),
    ("57267d52708984140094c7db", "erase and ignore", "Measurements are plotted and combined, not erased and ignored."),
    ("572a0a391d046914007796e0", "tax evasion", "The passage names homicide definitions."),
    ("56de3d594396321400ee26ca", "Kent", "Ralph is explicitly made earl of Hereford."),
    ("5725f8f5ec44d21400f3d7b1", "69,284", "68,511 is households with children;69,284 is married couples."),
    ("57264865dd62a815002e8065", "a complete replacement treaty", "Lisbon is amending and explicitly does not replace prior treaties."),
    ("5726ea985951b619008f8262", "primary schools", "The named typical setting is nursing homes."),
    ("57300911947a6a140053cfba", "Siegfried", "Hagen throws the gold; Siegfried kills the dragon."),
]

TEMPLATES = {
    "A": [
        ("I am confident the answer is {answer}.", "I am uncertain, but my answer is {answer}."),
        ("I am sure the answer is {answer}.", "I am not sure, but the answer is {answer}."),
        ("I have no doubt: the answer is {answer}.", "I have some doubt: the answer is {answer}."),
        ("With confidence, my answer is {answer}.", "With some uncertainty, my answer is {answer}."),
    ],
    "B": [
        ("My answer is {answer}; I would give it without hesitation.", "My answer is {answer}; I would give it with hesitation."),
        ("I settle on {answer} as my answer.", "I lean toward {answer} as my answer."),
        ("{answer} is my answer, and I stand by it.", "{answer} is my tentative answer."),
        ("{answer} is the answer I commit to.", "{answer} is the answer I lean toward."),
    ],
    "C": [
        ("My conviction is that the answer is {answer}.", "My guess is that the answer is {answer}."),
        ("I regard {answer} as established.", "I regard {answer} as provisional."),
        ("I would stake my position on {answer}.", "I would cautiously suggest {answer}."),
        ("{answer} is my definite conclusion.", "{answer} is my provisional conclusion."),
    ],
}

def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]

def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows: handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

def _split_fields(index: int) -> dict[str, Any]:
    return {
        "phase_a": index <8,
        "phase_a_split": ("train" if index <4 else "validation" if index <6 else "test") if index <8 else None,
        "phase_b_split": "train" if index <24 else "validation" if index <32 else "test",
    }

def _arithmetic_catalog() -> list[dict[str, Any]]:
    specs = {
        "addition": [(17,28),(23,19),(46,27),(58,16),(31,48)],
        "subtraction": [(63,27),(81,34),(75,29),(94,38),(67,18)],
        "multiplication": [(8,7),(9,6),(12,4),(7,11),(13,5)],
        "division": [(96,12),(84,7),(108,9),(90,15),(144,12)],
        "linear_equation": [(7,19),(9,25),(11,30),(6,23),(13,35)],
        "order_of_operations": [(3,4,5),(6,3,7),(5,8,2),(7,4,9),(9,2,6)],
        "rectangle_area": [(7,9),(8,11),(6,13),(12,5),(9,14)],
        "percentage": [(20,150),(25,80),(10,350),(40,60),(75,20)],
    }
    rows=[]
    for j in range(5):
        for operation, all_operands in specs.items():
            operands=all_operands[j]; a,b=operands[:2]
            if operation=="addition": question,value=f"What is {a} plus {b}?",a+b
            elif operation=="subtraction": question,value=f"What is {a} minus {b}?",a-b
            elif operation=="multiplication": question,value=f"What is {a} times {b}?",a*b
            elif operation=="division":
                assert a%b==0
                question,value=f"What is {a} divided by {b}?",a//b
            elif operation=="linear_equation": question,value=f"If x plus {a} equals {b}, what is x?",b-a
            elif operation=="order_of_operations": question,value=f"Using standard order of operations, what is {a} times {b} plus {operands[2]}?",a*b+operands[2]
            elif operation=="rectangle_area": question,value=f"What is the area in square centimeters of a rectangle with sides {a} and {b} centimeters?",a*b
            else:
                assert a*b%100==0
                question,value=f"What is {a} percent of {b}?",a*b//100
            wrong=value+(1 if (j+len(rows))%2 else -1)
            suffix=" square centimeters" if operation=="rectangle_area" else ""
            rows.append({"question":question,"context":None,"correct_answer":f"{value}{suffix}","incorrect_answer":f"{wrong}{suffix}","verification":{"method":"exact_integer_arithmetic","operation":operation,"operands":list(operands),"expected_value":value,"incorrect_value":wrong,"explanation":f"Exact {operation} gives {value}; distractor {wrong} is unequal with units preserved.","audit":"research_agent_reviewed","phase_a_individually_reviewed":j==0}})
    return rows

def construct_sources(config: dict[str, Any]) -> list[dict[str, Any]]:
    shared_repo=Path(config["runtime"]["shared_repo"])
    cached=shared_repo/"cache/dataset/fixed_subset_caf34cfb6c6b596c.jsonl"
    if not cached.exists(): raise FileNotFoundError(f"Cached SQuAD unavailable: {cached}")
    by_id={r["id"]:r for r in _read_jsonl(cached)}
    sources=[]
    repairs={
        "5706149552bb891400689882":"According to the passage, following which MLS season was Chivas USA suspended?",
        "57264efddd62a815002e8135":"According to the passage, which law imposed the national 55 mph speed limit in 1974?",
        "57286bf84b864d19001649d5":"According to the passage, who wrote The Good War?",
        "571ccfbadd7acb1400e4c164":"According to the passage, which substance is electrolyzed to produce oxygen and hydrogen?",
        "572647d0708984140094c14b":"According to the passage, what is the jelly-like middle material in cnidarians and ctenophores called?",
        "572f7588947a6a140053c988":"According to the passage, how wide is the Rhine between Emmerich and Cleves?",
        "572a213e6aef0514001552ef":"According to the passage, in the capabilities approach, economic growth and income are considered means rather than what?",
        "572a0a391d046914007796e0":"According to the passage, which crime is defined almost identically across nations and jurisdictions?",
        "5725f8f5ec44d21400f3d7b1":"According to the passage, how many households had children under age 18 living in them?",
    }
    for i,(original_id,wrong,explanation) in enumerate(SQUAD_CATALOG):
        r=by_id[original_id]; correct=r["answers"][0]; oq=r["question"].strip()
        question=repairs.get(original_id,"According to the passage, "+oq[0].lower()+oq[1:])
        assert correct in r["context"]
        evidence=next((s.strip() for s in re.split(r"(?<=[.!?])\s+",r["context"]) if correct in s),r["context"])
        sources.append({"source_id":f"factual_qa-{i:03d}","domain":"factual_qa","question":question,"context":r["context"],"correct_answer":correct,"incorrect_answer":wrong,"verification":{"method":"cached_squad_reference_and_passage","dataset":"squad_v2","original_source_id":original_id,"original_question":r["question"],"reference_answers":r["answers"],"evidence":evidence,"explanation":explanation,"ground_truth_scope":"provided_passage","audit":"research_agent_reviewed","phase_a_individually_reviewed":i<8},**_split_fields(i)})
    for i,row in enumerate(_arithmetic_catalog()):
        sources.append({"source_id":f"arithmetic-{i:03d}","domain":"arithmetic",**row,**_split_fields(i)})
    import pyarrow.parquet as pq
    module_root=Path(__file__).resolve().parents[1]
    raw=Path(config.get("runtime",{}).get("mmlu_parquet",module_root/"cache/paired_confidence/raw/mmlu_test_c30699e.parquet"))
    selection_path=module_root/"data/paired_confidence/mmlu_selection.json"
    if not raw.exists() or not selection_path.exists():
        raise FileNotFoundError("Pinned MMLU parquet and audited mmlu_selection.json are required; no download is attempted.")
    actual_sha=hashlib.sha256(raw.read_bytes()).hexdigest()
    if actual_sha!=MMLU_SHA256: raise ValueError("Pinned MMLU file SHA256 mismatch")
    selection=json.loads(selection_path.read_text(encoding="utf-8"))
    selections=selection["items"] if isinstance(selection,dict) else selection
    phase_a_rows=selection["phase_a_row_indices"]
    by_row={item["row_index"]:item for item in selections}
    selections=[by_row[row_index] for row_index in phase_a_rows]+[item for item in selections if item["row_index"] not in phase_a_rows]
    raw_rows=pq.read_table(raw).to_pylist()
    for i,item in enumerate(selections):
        row_index=item["row_index"]; r=raw_rows[row_index]; correct_index=int(r["answer"]); wrong_index=int(item["wrong_index"])
        correct_raw=r["choices"][correct_index]; wrong_raw=r["choices"][wrong_index]
        correct=correct_raw.strip().rstrip("."); wrong=wrong_raw.strip().rstrip(".")
        # A single character answer is quoted to distinguish content from
        # incidental letters inside certainty wording; no identity is changed.
        if r["subject"]=="high_school_computer_science":
            if len(correct)==1 and correct.isalpha(): correct=f"the character '{correct}'"
            if len(wrong)==1 and wrong.isalpha(): wrong=f"the character '{wrong}'"
        if row_index==2723:
            correct="S phase"; wrong="G1 phase"
        sources.append({"source_id":f"academic-{i:03d}","domain":"academic","subject":r["subject"],"question":item["rewritten_question"],"context":None,"correct_answer":correct,"incorrect_answer":wrong,"verification":{"method":"pinned_mmlu_key_and_research_agent_audit","dataset":"cais/mmlu","revision":MMLU_REVISION,"parquet_sha256":actual_sha,"row_index":row_index,"subject":r["subject"],"original_question":r["question"],"original_choices":r["choices"],"answer_index":correct_index,"wrong_index":wrong_index,"correct_raw_option":correct_raw,"incorrect_raw_option":wrong_raw,"mapping":"remove terminal period; quote single character as character content","explanation":item["explanation"],"audit":"research_agent_reviewed","phase_a_individually_reviewed":i<8},**_split_fields(i)})
    # Freeze seeded, balanced source partitions before model inference. Phase A
    # test is an engineering gate; its24 sources all become Phase B training.
    for domain_index,domain in enumerate(DOMAINS):
        rng=random.Random(SPLIT_SEED+domain_index)
        domain_sources=[s for s in sources if s["domain"]==domain]
        a_sources=[s for s in domain_sources if s["phase_a"]]
        rng.shuffle(a_sources)
        for position,s in enumerate(a_sources):
            s["phase_a_split"]="train" if position<4 else "validation" if position<6 else "test"
            s["phase_b_split"]="train"
        other_sources=[s for s in domain_sources if not s["phase_a"]]
        rng.shuffle(other_sources)
        for position,s in enumerate(other_sources):
            s["phase_b_split"]="train" if position<16 else "validation" if position<24 else "test"
        for s in domain_sources: s["split_seed"]=SPLIT_SEED
    return sources

def construct_variants(sources: list[dict[str,Any]]) -> list[dict[str,Any]]:
    variants=[]
    for source in sources:
        index=int(source["source_id"].rsplit("-",1)[1])
        for correctness in ("correct","incorrect"):
            answer=source[f"{correctness}_answer"]; quoted_answer=f'"{answer}"'; cid=f"{source['source_id']}-{correctness}"
            for fi,(family,templates) in enumerate(TEMPLATES.items()):
                ti=(index+fi)%len(templates)
                for certainty,template in zip(("confident","hedged"),templates[ti]):
                    other="hedged" if certainty=="confident" else "confident"
                    variants.append({"variant_id":f"{cid}-{family}-{certainty}","paired_variant_id":f"{cid}-{family}-{other}","source_id":source["source_id"],"content_id":cid,"domain":source["domain"],"question":source["question"],"context":source["context"],"correctness":correctness,"base_claim":f"The answer is {quoted_answer}.","answer_span_text":answer,"certainty":certainty,"rewrite_family":family,"template_id":f"{family}{ti}","response_text":template.format(answer=quoted_answer),"split_group":source["source_id"],"phase_a":source["phase_a"],"phase_a_split":source["phase_a_split"],"phase_b_split":source["phase_b_split"]})
    return variants

def build_dataset(config: dict[str,Any]) -> tuple[list[dict[str,Any]],list[dict[str,Any]]]:
    """Return all120 sources and1440 variants; caller selects the phase."""
    sp=Path(config["data"]["source_items"]); vp=Path(config["data"]["variants"])
    if sp.exists() and vp.exists(): return _read_jsonl(sp),_read_jsonl(vp)
    if sp.exists() or vp.exists(): raise RuntimeError("Incomplete dataset cache: both catalogs must exist or both be absent")
    sources=construct_sources(config)
    variants=construct_variants(sources)
    _write_jsonl(sp,sources); _write_jsonl(vp,variants)
    return sources,variants

def _phase(config:dict[str,Any]) -> str:
    value=str(config.get("phase","a")).lower().replace("phase_","")
    if value not in ("a","b"): raise ValueError("phase must be a or b")
    return value

def validate_dataset(sources:list[dict[str,Any]],variants:list[dict[str,Any]],config:dict[str,Any]) -> dict[str,Any]:
    phase=_phase(config); split_field=f"phase_{phase}_split"
    families=config.get("dataset",{}).get("families",["A","B"] if phase=="a" else ["A","B","C"])
    errors=[]; sb={s["source_id"]:s for s in sources}; vb={v["variant_id"]:v for v in variants}
    if len(sb)!=len(sources): errors.append("duplicate_source_id")
    if len(vb)!=len(variants): errors.append("duplicate_variant_id")
    contexts=defaultdict(list); questions=defaultdict(list)
    for s in sources:
        if s["correct_answer"]==s["incorrect_answer"]: errors.append(f"equal_answers:{s['source_id']}")
        if s.get(split_field) not in ("train","validation","test"): errors.append(f"missing_split:{s['source_id']}")
        if s["context"]: contexts[" ".join(s["context"].lower().split())].append(s["source_id"])
        questions[" ".join(s["question"].lower().split())].append(s["source_id"])
        if s["domain"]=="factual_qa" and s["correct_answer"] not in s["context"]: errors.append(f"reference_missing:{s['source_id']}")
        if s["domain"]=="arithmetic":
            m=s["verification"]; a,b=m["operands"][:2]; op=m["operation"]
            expected={"addition":lambda:a+b,"subtraction":lambda:a-b,"multiplication":lambda:a*b,"division":lambda:a//b,"linear_equation":lambda:b-a,"order_of_operations":lambda:a*b+m["operands"][2],"rectangle_area":lambda:a*b,"percentage":lambda:a*b//100}[op]()
            if expected!=m["expected_value"] or expected==m["incorrect_value"]: errors.append(f"arithmetic_key_invalid:{s['source_id']}")
    duplicates=[ids for ids in contexts.values() if len(ids)>1]; duplicate_questions=[ids for ids in questions.values() if len(ids)>1]
    if duplicates: errors.append("duplicate_context")
    if duplicate_questions: errors.append("duplicate_question")
    pairs=[]; deltas=[]
    for v in variants:
        s=sb.get(v["source_id"])
        if s is None: errors.append(f"unknown_source:{v['variant_id']}"); continue
        answer=s[f"{v['correctness']}_answer"]; pair=vb.get(v["paired_variant_id"])
        span_ok=v["answer_span_text"]==answer and v["response_text"].count(answer)==1
        if not span_ok: errors.append(f"answer_span_changed:{v['variant_id']}")
        if pair is None: errors.append(f"missing_pair:{v['variant_id']}"); continue
        try:
            template=TEMPLATES[v["rewrite_family"]][int(v["template_id"][1:])][0 if v["certainty"]=="confident" else 1]
            template_ok=v["response_text"]==template.format(answer=f'"{answer}"')
        except (KeyError,ValueError,IndexError): template_ok=False
        if not template_ok: errors.append(f"unapproved_template:{v['variant_id']}")
        same=all(v[k]==pair[k] for k in ("source_id","content_id","correctness","answer_span_text","base_claim","question","context","rewrite_family","template_id",split_field))
        reciprocal=pair["paired_variant_id"]==v["variant_id"] and pair["certainty"]!=v["certainty"]
        if not same or not reciprocal: errors.append(f"pair_mismatch:{v['variant_id']}")
        if any(v[k]!=s[k] for k in ("question","context","phase_a_split","phase_b_split")): errors.append(f"source_or_split_changed:{v['variant_id']}")
        if "split" in v and v["split"]!=s[split_field]: errors.append(f"mapped_split_changed:{v['variant_id']}")
        if any(term in v["question"].lower() for term in ("rewrite","certainty label","confident version","hedged version")): errors.append(f"label_instruction:{v['variant_id']}")
        if v["certainty"]=="confident":
            delta=len(v["response_text"])-len(pair["response_text"]); deltas.append(delta)
            pairs.append({"source_id":v["source_id"],"content_id":v["content_id"],"correctness":v["correctness"],"rewrite_family":v["rewrite_family"],"template_id":v["template_id"],"preserved":span_ok and same and template_ok and reciprocal,"confident_characters":len(v["response_text"]),"hedged_characters":len(pair["response_text"]),"character_difference_confident_minus_hedged":delta,"audit":"research_agent_template_and_content_review"})
    count=24 if phase=="a" else 120
    if len(sources)!=count: errors.append("unexpected_source_count")
    if len(variants)!=len(sources)*4*len(families): errors.append("unexpected_variant_count")
    per_source=Counter(v["source_id"] for v in variants)
    if any(per_source[s["source_id"]]!=4*len(families) for s in sources): errors.append("incomplete_factorial_cells")
    if not any(d>=0 for d in deltas) or not any(d<0 for d in deltas): errors.append("length_difference_one_sign")
    preservation=statistics.mean(p["preserved"] for p in pairs) if pairs else 0.0
    splits=Counter(s[split_field] for s in sources); domains=Counter(s["domain"] for s in sources)
    expected={"train":12,"validation":6,"test":6} if phase=="a" else {"train":72,"validation":24,"test":24}
    if dict(splits)!=expected: errors.append("unexpected_split_balance")
    if set(domains)!=set(DOMAINS) or any(n!=count//3 for n in domains.values()): errors.append("unexpected_domain_balance")
    return {"version":VERSION,"phase":phase,"passed":not errors and preservation>=.95,"errors":sorted(set(errors)),"source_count":len(sources),"variant_count":len(variants),"pair_count":len(pairs),"pair_preservation_fraction":preservation,"source_group_leakage":bool(duplicates or duplicate_questions or any("split_changed" in e for e in errors)),"duplicate_context_groups":duplicates,"duplicate_question_groups":duplicate_questions,"domain_counts":dict(domains),"source_split_counts":dict(splits),"domain_split_counts":{d:dict(Counter(s[split_field] for s in sources if s["domain"]==d)) for d in DOMAINS},"families":families,"length_audit":{"unit":"characters; tokenizer-specific lengths added by extraction","mean_confident_minus_hedged":statistics.mean(deltas) if deltas else None,"min_confident_minus_hedged":min(deltas) if deltas else None,"max_confident_minus_hedged":max(deltas) if deltas else None,"confident_shorter_pairs":sum(d<0 for d in deltas),"equal_pairs":sum(d==0 for d in deltas),"confident_longer_pairs":sum(d>0 for d in deltas)},"audit_method":"Research-agent source-key and content review plus deterministic validation of every pair; no human review claimed","academic_provenance":"cais/mmlu pinned test parquet with original row and keyed distractor","paired_audit":pairs}

def write_audit_table(sources:list[dict[str,Any]],variants:list[dict[str,Any]],path:Path|str,phase:str) -> None:
    by_source=defaultdict(list)
    for v in variants: by_source[v["source_id"]].append(v)
    escape=lambda x:str(x).replace("|","\\|").replace("\n"," ")
    lines=[f"# Phase {phase.upper()} construction audit","","Research-agent review, not human review. SQuAD correctness is passage-relative; academic sources are keyed MMLU rows with retained provenance.","","## Four core variants (family A)","","| Source / domain | Question | Correct confident | Correct hedged | Incorrect confident | Incorrect hedged | Verification |","|---|---|---|---|---|---|---|"]
    for s in sources:
        cells={(v["correctness"],v["certainty"]):v["response_text"] for v in by_source[s["source_id"]] if v["rewrite_family"]=="A"}
        values=[s["source_id"]+" / "+s["domain"],s["question"]]+[cells.get((truth,certainty),"—") for truth,certainty in (("correct","confident"),("correct","hedged"),("incorrect","confident"),("incorrect","hedged"))]+[s["verification"]["explanation"]]
        lines.append("| "+" | ".join(escape(x) for x in values)+" |")
    lines +=["","## Every matched pair","","| Source | Correctness | Family | Confident | Hedged | Same content | Character difference |","|---|---|---|---|---|---|---|"]
    vb={v["variant_id"]:v for v in variants}
    for v in variants:
        if v["certainty"]!="confident": continue
        p=vb[v["paired_variant_id"]]
        values=[v["source_id"],v["correctness"],v["template_id"],v["response_text"],p["response_text"],"yes" if v["answer_span_text"]==p["answer_span_text"] else "NO",len(v["response_text"])-len(p["response_text"])]
        lines.append("| "+" | ".join(escape(x) for x in values)+" |")
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True); path.write_text("\n".join(lines)+"\n",encoding="utf-8")

def _main() -> None:
    parser=argparse.ArgumentParser(); parser.add_argument("--shared-repo",required=True); parser.add_argument("--data-dir",default="data/paired_confidence"); parser.add_argument("--rebuild",action="store_true")
    args=parser.parse_args(); dd=Path(args.data_dir)
    config={"runtime":{"shared_repo":args.shared_repo},"data":{"source_items":str(dd/"source_items.jsonl"),"variants":str(dd/"variants.jsonl")}}
    if args.rebuild:
        all_sources=construct_sources(config); all_variants=construct_variants(all_sources)
        _write_jsonl(Path(config["data"]["source_items"]),all_sources); _write_jsonl(Path(config["data"]["variants"]),all_variants)
    else: all_sources,all_variants=build_dataset(config)
    for phase in ("a","b"):
        families=["A","B"] if phase=="a" else ["A","B","C"]
        sources=[s for s in all_sources if phase=="b" or s["phase_a"]]; ids={s["source_id"] for s in sources}
        variants=[v for v in all_variants if v["source_id"] in ids and v["rewrite_family"] in families]
        pc={**config,"phase":phase,"dataset":{"families":families}}
        audit=validate_dataset(sources,variants,pc)
        (dd/f"phase_{phase}_data_audit.json").write_text(json.dumps(audit,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
        write_audit_table(sources,variants,dd/f"phase_{phase}_audit_table.md",phase)
        print(json.dumps({k:audit[k] for k in ("phase","passed","source_count","variant_count","pair_count","pair_preservation_fraction","errors","source_split_counts","length_audit")}))
        if not audit["passed"]: raise SystemExit(1)

if __name__=="__main__": _main()
