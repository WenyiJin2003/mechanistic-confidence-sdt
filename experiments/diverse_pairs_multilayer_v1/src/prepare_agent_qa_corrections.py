"""Archive revision 2 and prepare only the ten agent-QA correction inputs."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
PRIVATE = BASE / "private_data"
FLAGGED = {"P009", "P017", "P022", "P039", "P041", "P042", "P044", "P045", "P047", "P049"}


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main():
    rows = read_jsonl(PRIVATE / "PAIRED_RESPONSES_50.jsonl")
    audits = []
    for batch in range(1, 4):
        audits += read_jsonl(PRIVATE / f"agent_audit_batch_{batch}.jsonl")
    by_id = {r["review_id"]: r for r in rows}
    audit_by_id = {r["review_id"]: r for r in audits}
    if len(rows) != 50 or len(by_id) != 50 or len(audits) != 50 or len(audit_by_id) != 50:
        raise ValueError("A complete 50-pair packet and audit are required")
    actual = {rid for rid, audit in audit_by_id.items() if audit["recommended_action"] == "revise"}
    if actual != FLAGGED:
        raise ValueError(f"Unexpected correction set: {sorted(actual)}")

    archive = PRIVATE / "review_revision_2_before_agent_qa"
    archive.mkdir(exist_ok=True)
    for filename in ["PAIRED_RESPONSES_50.jsonl", "PAIR_QA_50.jsonl", "REVIEW_50_PAIRS.html", "REVIEW_50_PAIRS_V2.html", "REVIEW_UI_PREVIEW.png"]:
        source, target = PRIVATE / filename, archive / filename
        if source.exists() and not target.exists():
            shutil.copy2(source, target)
    for batch in range(1, 4):
        source, target = PRIVATE / f"agent_audit_batch_{batch}.jsonl", archive / f"agent_audit_batch_{batch}.jsonl"
        if not target.exists():
            shutil.copy2(source, target)

    assignments = {1: ["P009", "P017"], 2: ["P022"],
                   3: ["P039", "P041", "P042", "P044", "P045", "P047", "P049"]}
    for batch, ids in assignments.items():
        selected = []
        for rid in ids:
            row, audit = by_id[rid], audit_by_id[rid]
            selected.append({
                "review_id": rid, "source_id": row["source_id"],
                "original_response_sha256": row["original_response_sha256"],
                "prompt": row["prompt"], "original_response": row["original_response"],
                "confident_response": row["confident_response"],
                "current_hedged_response": row["hedged_response"],
                "audit_reason": audit["concise_reason"], "audit_confounds": audit["confounds"],
            })
        target = PRIVATE / f"agent_qa_correction_input_batch_{batch}.jsonl"
        target.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in selected), encoding="utf-8")
    print(json.dumps({"revision_2_archived": True, "correction_ids": sorted(FLAGGED),
                      "confident_responses_changed": 0, "agent_review_is_human_review": False}))


if __name__ == "__main__":
    main()
