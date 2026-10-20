"""Freeze the purposive, context-complete canary selection without changing text."""
import json
from prepare_sources import BASE, digest, write_json

def main():
    config = json.loads((BASE / "config.json").read_text())
    root = BASE / config["private_dir"]
    candidates = {r["row_idx"]: r for r in json.loads((root / "CANDIDATES.json").read_text())}
    chosen = config["selected_source_row_indices"]
    if len(chosen) != 50 or len(set(chosen)) != 50:
        raise RuntimeError("Expected exactly 50 distinct row indices")
    records = []
    for index, row_idx in enumerate(chosen, 1):
        r = dict(candidates[row_idx])
        cached = json.loads((root / r["source_cache_file"]).read_text())
        original_row = next(v["row"] for v in cached["response"]["rows"] if v["row_idx"] == row_idx)
        assert original_row == r["raw_source_row"]
        assert original_row["messages"][0]["content"] == r["question"]
        assert original_row["messages"][1]["content"] == r["original"]
        assert digest(r["original"]) == r["original_sha256"]
        r.update(review_id=f"HC{index:03d}", group_id=r["source_id"], manual_source_selection="purposefully_selected_by_assistant_not_fact_certified", human_review_completed=False)
        records.append(r)
    serialized = json.dumps(records, ensure_ascii=False, indent=2) + "\n"
    target = root / "SOURCES_50.json"
    if target.exists() and target.read_text() != serialized:
        raise RuntimeError("Refusing to overwrite a different frozen source selection")
    write_json(target, records)
    write_json(root / "SOURCE_SELECTION_MANIFEST.json", {"n_sources": 50, "n_unique_questions": len({r["question"] for r in records}), "source_file_sha256": digest(serialized), "words_total": sum(r["word_count"] for r in records), "question_and_original_verbatim_verified": True, "fact_accuracy_certified": False, "human_review_completed": False, "selection": "Purposive factual/explanatory first-turn chats; not a random sample or a population pass-rate estimate."})
    print(json.dumps({"sources": len(records), "words_total": sum(r["word_count"] for r in records), "file": str(target)}))

if __name__ == "__main__":
    main()
