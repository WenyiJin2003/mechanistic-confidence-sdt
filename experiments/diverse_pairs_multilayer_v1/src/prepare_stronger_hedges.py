"""Archive the reviewed draft and prepare hedge-only revision inputs."""
import json
import shutil
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
PRIVATE = BASE / "private_data"


def main():
    rows = [json.loads(line) for line in (PRIVATE / "PAIRED_RESPONSES_50.jsonl").read_text().splitlines()]
    if len(rows) != 50 or len({r["review_id"] for r in rows}) != 50:
        raise ValueError("A complete source-aligned 50-pair draft is required")
    archived = PRIVATE / "review_revision_1"
    archived.mkdir(exist_ok=True)
    for filename in ["PAIRED_RESPONSES_50.jsonl", "PAIR_QA_50.jsonl", "REVIEW_50_PAIRS.html", "REVIEW_UI_PREVIEW.png"]:
        if (PRIVATE / filename).exists() and not (archived / filename).exists():
            shutil.copy2(PRIVATE / filename, archived / filename)
    for batch, begin, end in [(1, 0, 17), (2, 17, 34), (3, 34, 50)]:
        inputs = []
        for row in rows[begin:end]:
            inputs.append({k: row[k] for k in ["review_id", "source_id", "original_response_sha256", "prompt", "original_response", "confident_response", "hedged_response", "rewrite_family"]})
        path = PRIVATE / f"stronger_hedges_input_batch_{batch}.jsonl"
        path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in inputs), encoding="utf-8")
    (BASE / "manifests" / "hedge_revision_2_plan.json").write_text(json.dumps({
        "revision": 2, "reason": "User requests a clearer hesitant tone; no probe scores were consulted",
        "sources": 50, "changed_field": "hedged_response", "confident_responses": "frozen",
        "source_content": "frozen", "rewriter_model_requested": "gpt-6-luna",
        "reasoning_effort": "low", "human_review": "pending", "stage": "train_development",
        "archived_revision": "private_data/review_revision_1", "paid_api_calls": 0
    }, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"sources": 50, "revision": 2, "confident_responses_rewritten": 0, "previous_revision_preserved": True}))


if __name__ == "__main__":
    main()
