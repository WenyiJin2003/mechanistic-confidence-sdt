import copy
import hashlib
import random

import pytest

from experiments.diverse_pairs_multilayer_v1.src.import_reviews import apply_reviews


PACKET_HASH = "synthetic-packet-hash"


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


def sample_pairs(n=4):
    pairs = []
    for i in range(n):
        original = f"Original response {i}."
        pairs.append({
            "review_id": f"P{i + 1:03d}", "source_id": f"source-{i}",
            "original_response": original,
            "original_response_sha256": sha(original),
            "confident_response": f"Confident response {i}.",
            "hedged_response": f"Hedged response {i}.",
            "human_review": "pending",
        })
    return pairs


def export_for(pairs):
    rng = random.Random(20261011)
    reviews = []
    for pair in pairs:
        keys = ["confident_response", "hedged_response"]
        rng.shuffle(keys)
        reviews.append({
            "review_id": pair["review_id"], "source_id": pair["source_id"],
            "original_response_sha256": pair["original_response_sha256"],
            "confident_sha256": sha(pair["confident_response"]),
            "hedged_sha256": sha(pair["hedged_response"]),
            "display_mapping": {"A": keys[0], "B": keys[1]},
            "content_preserved": "yes", "more_certain": "A" if keys[0] == "confident_response" else "B",
            "other_confound": "no", "notes": "", "human_review": "annotated",
        })
    return {"packet_sha256": PACKET_HASH, "reviewer": "user",
            "exported_at": "2026-10-11T12:00:00Z", "reviews": reviews}


def test_valid_user_export_passes_and_does_not_mutate_draft():
    pairs = sample_pairs()
    payload = export_for(pairs)
    updated, aggregate = apply_reviews(pairs, payload, PACKET_HASH)
    assert all(row["human_review"] == "passed" for row in updated)
    assert all(row["human_review"] == "pending" for row in pairs)
    assert aggregate["passed_count"] == len(pairs)
    assert aggregate["proposed_expansion_gate"] is True
    assert aggregate["expansion_started"] is False
    assert updated[0]["human_review_annotation"]["reviewer"] == "user"


def test_stale_packet_hash_rejected():
    pairs = sample_pairs()
    payload = export_for(pairs)
    payload["packet_sha256"] = "stale"
    with pytest.raises(ValueError, match="stale"):
        apply_reviews(pairs, payload, PACKET_HASH)


def test_changed_response_text_hash_rejected():
    pairs = sample_pairs()
    payload = export_for(pairs)
    pairs[0]["hedged_response"] += " changed"
    with pytest.raises(ValueError, match="hedged_sha256"):
        apply_reviews(pairs, payload, PACKET_HASH)


def test_original_text_hash_corruption_rejected():
    pairs = sample_pairs()
    pairs[0]["original_response"] += " changed"
    with pytest.raises(ValueError, match="original response hash"):
        apply_reviews(pairs, export_for(pairs), PACKET_HASH)


@pytest.mark.parametrize("mutation,match", [
    (lambda p: p["reviews"].append(copy.deepcopy(p["reviews"][0])), "duplicate"),
    (lambda p: p["reviews"][0].update(review_id="P999"), "unknown"),
])
def test_duplicate_and_unknown_review_ids_rejected(mutation, match):
    pairs = sample_pairs()
    payload = export_for(pairs)
    mutation(payload)
    with pytest.raises(ValueError, match=match):
        apply_reviews(pairs, payload, PACKET_HASH)


def test_forged_ab_mapping_rejected():
    pairs = sample_pairs()
    payload = export_for(pairs)
    payload["reviews"][0]["display_mapping"] = {
        "A": "hedged_response", "B": "confident_response"}
    with pytest.raises(ValueError, match="A/B mapping"):
        apply_reviews(pairs, payload, PACKET_HASH)


def test_missing_or_uncertain_answers_remain_pending():
    pairs = sample_pairs()
    payload = export_for(pairs)
    payload["reviews"][0]["other_confound"] = ""
    payload["reviews"][1]["content_preserved"] = "uncertain"
    payload["reviews"][2]["more_certain"] = "uncertain"
    updated, aggregate = apply_reviews(pairs, payload, PACKET_HASH)
    assert [row["human_review"] for row in updated[:3]] == ["pending"] * 3
    assert aggregate["pending_count"] == 3
    assert aggregate["proposed_expansion_gate"] is False


def test_tied_certainty_is_a_definitive_rejection():
    pairs = sample_pairs()
    payload = export_for(pairs)
    payload["reviews"][0]["more_certain"] = "tie"
    updated, _ = apply_reviews(pairs, payload, PACKET_HASH)
    assert updated[0]["human_review"] == "rejected"


def test_complete_content_failure_is_rejected():
    pairs = sample_pairs()
    payload = export_for(pairs)
    payload["reviews"][0]["content_preserved"] = "no"
    updated, aggregate = apply_reviews(pairs, payload, PACKET_HASH)
    assert updated[0]["human_review"] == "rejected"
    assert aggregate["rejected_count"] == 1
    assert aggregate["proposed_expansion_gate"] is False


def test_hard_content_failure_rejects_even_if_another_field_is_uncertain():
    pairs = sample_pairs()
    payload = export_for(pairs)
    payload["reviews"][0]["content_preserved"] = "no"
    payload["reviews"][0]["other_confound"] = "uncertain"
    updated, aggregate = apply_reviews(pairs, payload, PACKET_HASH)
    assert updated[0]["human_review"] == "rejected"
    assert aggregate["rejected_count"] == 1


def test_wrong_certainty_and_confound_reject_even_when_content_preserved():
    pairs = sample_pairs()
    payload = export_for(pairs)
    payload["reviews"][0]["more_certain"] = "B" if payload["reviews"][0]["more_certain"] == "A" else "A"
    payload["reviews"][1]["other_confound"] = "yes"
    updated, _ = apply_reviews(pairs, payload, PACKET_HASH)
    assert [updated[i]["human_review"] for i in (0, 1)] == ["rejected", "rejected"]


def test_tone_comment_without_individual_answers_is_not_approval():
    pairs = sample_pairs()
    payload = export_for(pairs)
    payload["reviews"] = []
    # A general note cannot substitute for the three explicit per-pair fields.
    payload["comment"] = "OK, the tone seems different."
    updated, aggregate = apply_reviews(pairs, payload, PACKET_HASH)
    assert all(row["human_review"] == "pending" for row in updated)
    assert aggregate["passed_count"] == 0
    assert aggregate["proposed_expansion_gate"] is False


def test_agent_marker_is_not_accepted_as_user_review():
    pairs = sample_pairs()
    payload = export_for(pairs)
    payload["reviewer"] = "assistant"
    with pytest.raises(ValueError, match="reviewer"):
        apply_reviews(pairs, payload, PACKET_HASH)


def test_cli_checks_exact_source_jsonl_hash_before_writing(tmp_path):
    import json
    from experiments.diverse_pairs_multilayer_v1.src.import_reviews import main

    pairs = sample_pairs()
    payload = export_for(pairs)
    pairs_path = tmp_path / "pairs.jsonl"
    pairs_path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in pairs))
    reviews_path = tmp_path / "reviews.json"
    reviews_path.write_text(json.dumps(payload))
    summary_path = tmp_path / "summary.json"
    summary_path.write_text(json.dumps({"packet_sha256": "wrong-source-hash"}))
    output_path = tmp_path / "reviewed.jsonl"
    with pytest.raises(ValueError, match="source pair JSONL hash"):
        main(["--reviews", str(reviews_path), "--output", str(output_path),
              "--pairs", str(pairs_path), "--summary", str(summary_path)])
    assert not output_path.exists()
    assert not output_path.with_suffix(".jsonl.annotations.json").exists()


def test_cli_writes_new_reviewed_data_and_separate_export_atomically(tmp_path, capsys):
    import json
    import hashlib
    from experiments.diverse_pairs_multilayer_v1.src.import_reviews import main

    pairs = sample_pairs()
    pair_bytes = "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in pairs)
    pairs_path = tmp_path / "pairs.jsonl"
    pairs_path.write_text(pair_bytes)
    reviews_path = tmp_path / "reviews.json"
    payload = export_for(pairs)
    packet_hash = hashlib.sha256(pair_bytes.encode()).hexdigest()
    payload["packet_sha256"] = packet_hash
    reviews_path.write_text(json.dumps(payload))
    summary_path = tmp_path / "summary.json"
    summary_path.write_text(json.dumps({"packet_sha256": packet_hash}))
    output_path = tmp_path / "reviewed.jsonl"
    assert main(["--reviews", str(reviews_path), "--output", str(output_path),
                 "--pairs", str(pairs_path), "--summary", str(summary_path)]) == 0
    reviewed = [json.loads(line) for line in output_path.read_text().splitlines()]
    sidecar = output_path.with_suffix(".jsonl.annotations.json")
    assert all(row["human_review"] == "passed" for row in reviewed)
    assert json.loads(sidecar.read_text())["reviewer"] == "user"
    assert json.loads(capsys.readouterr().out)["expansion_started"] is False


def test_invalid_enums_and_unknown_fields_rejected():
    pairs = sample_pairs()
    payload = export_for(pairs)
    payload["reviews"][0]["content_preserved"] = "looks fine"
    with pytest.raises(ValueError, match="invalid content_preserved"):
        apply_reviews(pairs, payload, PACKET_HASH)
    payload = export_for(pairs)
    payload["reviews"][0]["approval"] = True
    with pytest.raises(ValueError, match="unknown review fields"):
        apply_reviews(pairs, payload, PACKET_HASH)
