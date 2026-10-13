"""Focused tests for the text-free agent diagnostic summary."""
from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path

import pytest


SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

import summarize_agent_diagnostic_review as diagnostic


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _text_sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _fixture(tmp_path: Path) -> tuple[Path, Path, Path, Path, dict]:
    packet = tmp_path / "private_data" / "packet"
    packet.mkdir(parents=True)
    rows = [
        {
            "review_id": f"R{index:03d}",
            "source_response": f"private source text {index}",
            "version_a": f"private version A {index}",
            "version_b": f"private version B {index}",
        }
        for index in range(1, 4)
    ]
    rows_path = packet / "BLINDED_ROWS.jsonl"
    rows_path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )
    packet_hash = _sha(rows_path)
    key_rows = []
    for index, row in enumerate(rows, start=1):
        key_rows.append(
            {
                "review_id": row["review_id"],
                "source_id": f"source-{index}",
                "source_response_sha256": _text_sha(row["source_response"]),
                "version_a_sha256": _text_sha(row["version_a"]),
                "version_b_sha256": _text_sha(row["version_b"]),
            }
        )
    key_path = packet / "UNBLIND_KEY.json"
    key_path.write_text(
        json.dumps({"packet_sha256": packet_hash, "pairs": key_rows}),
        encoding="utf-8",
    )
    (packet / "MANIFEST.json").write_text(
        json.dumps(
            {
                "packet_sha256": packet_hash,
                "unblind_key_sha256": _sha(key_path),
                "pairs": 3,
            }
        ),
        encoding="utf-8",
    )

    reports = tmp_path / "reports"
    reports.mkdir()
    nli_path = reports / "nli.json"
    nli_public = {
        "schema": "local-nli-semantic-triage-public-v1",
        "protocol_version": "local-nli-semantic-triage-v1",
        "status": "complete",
        "bindings": {"fixture": "binding"},
        "counts": {"flagged_pair_count": 2, "not_flagged_pair_count": 1},
    }
    nli_path.write_text(json.dumps(nli_public), encoding="utf-8")
    private_nli_path = tmp_path / "private_data" / "semantic_triage_v1.json"
    private_nli = {
        "schema": "local-nli-semantic-triage-private-v1",
        "protocol_version": "local-nli-semantic-triage-v1",
        "status": "complete",
        "semantic_certification": False,
        "public_report_sha256": diagnostic.canonical_sha256(nli_public),
        "bindings": nli_public["bindings"],
        "aggregate": nli_public["counts"],
        "records": [
            {"source_id": "source-1", "triage_flagged": True},
            {"source_id": "source-2", "triage_flagged": True},
            {"source_id": "source-3", "triage_flagged": False},
        ],
    }
    private_nli_path.write_text(json.dumps(private_nli), encoding="utf-8")
    private_review = {
        "schema": "agent-blind-diagnostic-private-v2",
        "reviewer_type": "agent",
        "human_certified": False,
        "blinded": True,
        "semantic_certification": False,
        "certainty_direction_relative_to_intended_labels": "not_captured_or_verified",
        "packet_sha256": packet_hash,
        "nli_report_sha256": _sha(nli_path),
        "private_nli_triage_sha256": _sha(private_nli_path),
        "unblind_key_sha256": _sha(key_path),
        "sampling_design": {
            "expected_reviewed_by_stratum": {
                "nli_flagged": 2,
                "nli_unflagged_sample": 1,
            },
            "nli_unflagged_selection": (
                "task- and dataset-balanced diagnostic sample"
            ),
        },
        "reviews": [
            {
                "review_id": "R001",
                "stratum": "nli_flagged",
                "content_preservation": "preserved",
                "certainty_contrast": "clear",
                "naturalness": "clearly_natural",
                "cue_scope": "global",
                "decision": "accept",
                "issue_categories": [],
            },
            {
                "review_id": "R002",
                "stratum": "nli_flagged",
                "content_preservation": "preserved",
                "certainty_contrast": "clear",
                "naturalness": "not_clearly_natural",
                "cue_scope": "global",
                "decision": "reject",
                "issue_categories": ["list_interruption"],
            },
            {
                "review_id": "R003",
                "stratum": "nli_unflagged_sample",
                "content_preservation": "preserved",
                "certainty_contrast": "clear",
                "naturalness": "not_clearly_natural",
                "cue_scope": "ambiguous",
                "decision": "discuss",
                "issue_categories": ["scope_ambiguity"],
            },
        ],
    }
    review_path = tmp_path / "private_data" / "agent_review.json"
    review_path.write_text(json.dumps(private_review), encoding="utf-8")
    return review_path, packet, nli_path, private_nli_path, private_review


def test_builds_bound_text_free_noncertifying_summary(tmp_path):
    review_path, packet, nli_path, private_nli_path, _ = _fixture(tmp_path)
    summary = diagnostic.build_public_summary(
        review_path, packet, nli_path, private_nli_path, base=tmp_path
    )

    assert summary["reviewer_type"] == "agent"
    assert summary["human_certified"] is False
    assert summary["training_data_validated"] is False
    assert summary["authorizes_probe_scoring"] is False
    assert summary["certainty_direction_relative_to_intended_labels"] == (
        "not_captured_or_verified"
    )
    assert summary["bindings"]["nli_report_sha256"] == _sha(nli_path)
    assert summary["bindings"]["private_nli_triage_sha256"] == _sha(
        private_nli_path
    )
    assert summary["counts"]["decision"] == {
        "accept": 1,
        "discuss": 1,
        "reject": 1,
    }
    assert summary["counts"]["certainty_contrast"] == {"clear": 3}
    assert "certainty_ordering" not in summary["counts"]
    assert summary["sampling_design"]["nli_unflagged"]["selection"] == (
        "task- and dataset-balanced diagnostic sample"
    )
    assert summary["decision_counts_by_sampling_stratum"]["nli_flagged"] == {
        "accept": 1,
        "discuss": 0,
        "reject": 1,
    }

    public_text = json.dumps(summary)
    for private_value in (
        "R001",
        "R002",
        "R003",
        "private source text",
        "list_interruption",
        "scope_ambiguity",
    ):
        assert private_value not in public_text


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda review: review.update(human_certified=True), "human_certified"),
        (
            lambda review: review.pop(
                "certainty_direction_relative_to_intended_labels"
            ),
            "certainty_direction_relative_to_intended_labels",
        ),
        (lambda review: review.update(packet_sha256="0" * 64), "packet hash"),
        (lambda review: review.update(nli_report_sha256="0" * 64), "NLI report hash"),
        (
            lambda review: review.update(private_nli_triage_sha256="0" * 64),
            "detailed NLI hash",
        ),
        (
            lambda review: review["reviews"].append(copy.deepcopy(review["reviews"][0])),
            "Duplicate",
        ),
        (
            lambda review: review["reviews"][0].update(review_id="R999"),
            "not in packet",
        ),
        (
            lambda review: review["reviews"][0].update(comment="private prose"),
            "comments and source IDs",
        ),
    ],
)
def test_rejects_stale_unsafe_or_identity_invalid_review(tmp_path, mutation, message):
    review_path, packet, nli_path, private_nli_path, review = _fixture(tmp_path)
    mutation(review)
    review_path.write_text(json.dumps(review), encoding="utf-8")
    with pytest.raises(ValueError, match=message):
        diagnostic.build_public_summary(
            review_path, packet, nli_path, private_nli_path, base=tmp_path
        )


def test_requires_complete_flagged_stratum_and_matching_design(tmp_path):
    review_path, packet, nli_path, private_nli_path, review = _fixture(tmp_path)
    review["sampling_design"]["expected_reviewed_by_stratum"]["nli_flagged"] = 1
    review_path.write_text(json.dumps(review), encoding="utf-8")
    with pytest.raises(ValueError, match="Observed review strata"):
        diagnostic.build_public_summary(
            review_path, packet, nli_path, private_nli_path, base=tmp_path
        )


def test_rejects_declared_stratum_that_disagrees_with_detailed_membership(tmp_path):
    review_path, packet, nli_path, private_nli_path, review = _fixture(tmp_path)
    review["reviews"][0]["stratum"] = "nli_unflagged_sample"
    review_path.write_text(json.dumps(review), encoding="utf-8")
    with pytest.raises(ValueError, match="Declared NLI stratum disagrees"):
        diagnostic.build_public_summary(
            review_path, packet, nli_path, private_nli_path, base=tmp_path
        )


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (
            lambda private_nli: private_nli.update(public_report_sha256="0" * 64),
            "public_report_sha256",
        ),
        (
            lambda private_nli: private_nli.update(bindings={"fixture": "tampered"}),
            "bindings disagree",
        ),
    ],
)
def test_rejects_private_nli_provenance_tamper(tmp_path, mutation, message):
    review_path, packet, nli_path, private_nli_path, review = _fixture(tmp_path)
    private_nli = json.loads(private_nli_path.read_text(encoding="utf-8"))
    mutation(private_nli)
    private_nli_path.write_text(json.dumps(private_nli), encoding="utf-8")
    review["private_nli_triage_sha256"] = _sha(private_nli_path)
    review_path.write_text(json.dumps(review), encoding="utf-8")
    with pytest.raises(ValueError, match=message):
        diagnostic.build_public_summary(
            review_path, packet, nli_path, private_nli_path, base=tmp_path
        )


def test_rejects_missing_member_of_complete_flagged_stratum(tmp_path):
    review_path, packet, nli_path, private_nli_path, review = _fixture(tmp_path)
    review["reviews"] = [
        record for record in review["reviews"] if record["review_id"] != "R002"
    ]
    review["sampling_design"]["expected_reviewed_by_stratum"]["nli_flagged"] = 1
    review_path.write_text(json.dumps(review), encoding="utf-8")
    with pytest.raises(ValueError, match="every NLI-flagged pair"):
        diagnostic.build_public_summary(
            review_path, packet, nli_path, private_nli_path, base=tmp_path
        )


def test_rejects_unblind_mapping_tamper(tmp_path):
    review_path, packet, nli_path, private_nli_path, review = _fixture(tmp_path)
    key_path = packet / "UNBLIND_KEY.json"
    key = json.loads(key_path.read_text(encoding="utf-8"))
    key["pairs"][1]["source_id"], key["pairs"][2]["source_id"] = (
        key["pairs"][2]["source_id"],
        key["pairs"][1]["source_id"],
    )
    key_path.write_text(json.dumps(key), encoding="utf-8")
    review["unblind_key_sha256"] = _sha(key_path)
    review_path.write_text(json.dumps(review), encoding="utf-8")
    with pytest.raises(ValueError, match="UNBLIND_KEY does not match"):
        diagnostic.build_public_summary(
            review_path, packet, nli_path, private_nli_path, base=tmp_path
        )


def test_requires_private_input_and_refuses_output_overwrite(tmp_path):
    review_path, packet, nli_path, private_nli_path, review = _fixture(tmp_path)
    public_input = tmp_path / "review.json"
    public_input.write_text(json.dumps(review), encoding="utf-8")
    with pytest.raises(ValueError, match="private_data"):
        diagnostic.build_public_summary(
            public_input, packet, nli_path, private_nli_path, base=tmp_path
        )

    summary = diagnostic.build_public_summary(
        review_path, packet, nli_path, private_nli_path, base=tmp_path
    )
    output = tmp_path / "reports" / "summary.json"
    output.write_text("existing", encoding="utf-8")
    with pytest.raises(FileExistsError, match="Refusing to overwrite"):
        diagnostic.write_public_summary(output, summary)
