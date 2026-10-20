"""Offline integrity/leakage tests; never load the representation model."""
import importlib.util
import json
from pathlib import Path
import sys
from types import SimpleNamespace

import numpy as np
import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "src/run_cached_analysis.py"
SPEC = importlib.util.spec_from_file_location("haiku_cached_analysis", SCRIPT)
analysis = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(analysis)


def rows(count=20):
    return [{"review_id": f"HC{i:03d}", "source_id": f"source-{i}", "group_id": f"group-{i}",
             "question": f"Question {i}?", "original": f"Answer {i}.",
             "confident": f"Certainly answer {i}.", "hesitant": f"Possibly answer {i}.",
             "human_item_rating_received": False, "content_preservation_certified": False,
             "raw_source_row": {"messages": [{"role": "user", "content": f"Question {i}?"},
                                               {"role": "assistant", "content": f"Answer {i}."}]}}
            for i in range(count)]


def test_split_is_reproducible_and_exactly_80_20_independent_groups():
    data = rows()
    first = analysis.split_groups(data)
    assert first == analysis.split_groups(data)
    assert first["test_groups"] == 4
    train = {g for g, s in zip(first["groups"], first["splits"]) if s == "train"}
    test = {g for g, s in zip(first["groups"], first["splits"]) if s == "test"}
    assert not train & test
    assert len(train | test) == 20


def test_transitive_exact_normalized_prompt_and_original_duplicates_are_grouped():
    data = rows()
    data[1]["question"] = "  ＱＵＥＳＴＩＯＮ   0?  "
    data[2]["original"] = " ANSWER 1. "
    data[3]["group_id"] = data[2]["group_id"]
    split = analysis.split_groups(data)
    assert len(set(split["groups"][:4])) == 1
    assert len(set(split["splits"][:4])) == 1


def test_canary_and_all_duplicate_derivatives_are_forced_to_train():
    data = rows()
    data[0]["reuse_canary"] = True
    data[1]["question"] = data[0]["question"]
    data[2]["user_general_canary_feedback"] = "positive"
    split = analysis.split_groups(data)
    assert split["splits"][:3] == ["train"] * 3
    assert split["forced_train_groups"] == 2


def test_split_membership_is_invariant_to_row_order():
    data = rows()
    first, second = analysis.split_groups(data), analysis.split_groups(data[::-1])
    assignment = {r["source_id"]: s for r, s in zip(data, first["splits"])}
    assert assignment == {r["source_id"]: s for r, s in zip(data[::-1], second["splits"])}


def snapshot(tmp_path, data=None):
    data = rows(5) if data is None else data
    packet = {"triplets": data, "human_review_completed": False,
              "content_preservation_certified": False}
    packet_path, manifest_path = tmp_path / "TRIPLETS.json", tmp_path / "MANIFEST.json"
    packet_path.write_text(json.dumps(packet), encoding="utf-8")
    manifest_path.write_text(json.dumps({"schema_version": "test"}), encoding="utf-8")
    selector = {"triplets_file": str(packet_path), "triplets_file_sha256": analysis.file_sha(packet_path),
                "manifest_file": str(manifest_path), "manifest_file_sha256": analysis.file_sha(manifest_path),
                "packet_sha256": analysis.canonical_sha(packet)}
    entry = tmp_path / "SELECTOR.json"
    entry.write_text(json.dumps(selector), encoding="utf-8")
    return entry, packet


def test_snapshot_retains_exact_original_and_candidate_review_status(tmp_path):
    entry, expected = snapshot(tmp_path)
    packet, provenance = analysis.load_snapshot(entry, required_count=5, verify_provenance=False)
    assert packet == expected
    assert packet["triplets"][0]["original"] == "Answer 0."
    assert provenance["packet_canonical_sha256"] == analysis.canonical_sha(expected)


def test_snapshot_rejects_file_tamper(tmp_path):
    entry, _ = snapshot(tmp_path)
    (tmp_path / "TRIPLETS.json").write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="file SHA256"):
        analysis.load_snapshot(entry, required_count=5, verify_provenance=False)


def test_snapshot_rejects_canonical_hash_mismatch(tmp_path):
    entry, _ = snapshot(tmp_path)
    selector = json.loads(entry.read_text())
    selector["packet_sha256"] = "0" * 64
    entry.write_text(json.dumps(selector), encoding="utf-8")
    with pytest.raises(ValueError, match="canonical SHA256"):
        analysis.load_snapshot(entry, required_count=5, verify_provenance=False)


@pytest.mark.parametrize("field", ["human_item_rating_received", "content_preservation_certified"])
def test_snapshot_rejects_silent_review_promotion(tmp_path, field):
    data = rows(5)
    data[0][field] = True
    entry, _ = snapshot(tmp_path, data)
    with pytest.raises(ValueError, match="review provenance"):
        analysis.load_snapshot(entry, required_count=5, verify_provenance=False)


def test_snapshot_rejects_changed_original_source_text(tmp_path):
    data = rows(5)
    data[0]["original"] = "A silently corrected source answer"
    entry, _ = snapshot(tmp_path, data)
    with pytest.raises(ValueError, match="cached source"):
        analysis.load_snapshot(entry, required_count=5, verify_provenance=False)


def test_memmap_run_directory_must_stay_inside_isolated_experiment(tmp_path):
    with pytest.raises(ValueError, match="named child"):
        analysis.safe_run_dir(tmp_path)
    with pytest.raises(ValueError, match="named child"):
        analysis.safe_run_dir(analysis.BASE / "private_data")
    assert analysis.safe_run_dir(analysis.BASE / "private_data/test") == analysis.BASE / "private_data/test"


def test_benchmark_covers_full_pending_length_range_and_ignores_completed():
    tokens = [[{"input_ids": [0] * (i + 3)}, {"input_ids": [0] * (i + 5)}] for i in range(100)]
    completed = np.zeros(100, dtype=bool)
    completed[3] = True
    chosen = analysis.select_pending(tokens, completed, 20)
    assert len(chosen) == len(set(chosen)) == 20
    assert chosen[0] == 0 and chosen[-1] == 99
    assert 3 not in chosen
    assert analysis.select_pending(tokens, np.ones(100, dtype=bool), 20) == []


def test_group_interval_uses_groups_and_half_ties():
    scores = np.asarray([[2, 0], [0, 2], [1, 1], [2, 0]], dtype=float)
    result = analysis.interval(scores, ["a", "a", "b", "b"], draws=500)
    assert result["estimate"] == .625
    assert result["groups"] == 2
    assert result["wins"] == 2 and result["losses"] == 1 and result["ties"] == 1
    assert result == analysis.interval(scores, ["a", "a", "b", "b"], draws=500)


def test_no_forward_without_explicit_flag(monkeypatch):
    class Args:
        permit_local_forward = False
    monkeypatch.setattr(analysis, "import_extraction", lambda: pytest.fail("model helpers imported"))
    with pytest.raises(ValueError, match="permit-local-forward"):
        analysis.extract(Args())


@pytest.mark.parametrize("missing", ["STATES.npy", "NLL.npy", "COMPLETED.npy"])
def test_resume_rejects_any_missing_array_without_recreating_it(tmp_path, missing):
    arrays = analysis.extraction_arrays(tmp_path, 1)
    arrays[2][:] = True
    arrays[2].flush()
    del arrays
    (tmp_path / missing).unlink()
    with pytest.raises(ValueError, match="Incomplete extraction array trio"):
        analysis.extraction_arrays(tmp_path, 1)
    assert not (tmp_path / missing).exists()


@pytest.mark.parametrize("changed", ["STATES.npy", "NLL.npy", "COMPLETED.npy"])
def test_resume_rejects_incorrect_array_dtype_or_shape(tmp_path, changed):
    arrays = analysis.extraction_arrays(tmp_path, 1)
    del arrays
    np.save(tmp_path / changed, np.zeros((1,), dtype=np.float32), allow_pickle=False)
    with pytest.raises(ValueError, match="shape/dtype mismatch"):
        analysis.extraction_arrays(tmp_path, 1)


def test_new_arrays_are_uncommitted_and_resume_preserves_completed_data(tmp_path):
    states, nll, completed = analysis.extraction_arrays(tmp_path, 1)
    assert not completed.any()
    states[0] = 3
    nll[0] = 7
    states.flush()
    nll.flush()
    completed[0] = True
    completed.flush()
    del states, nll, completed
    states, nll, completed = analysis.extraction_arrays(tmp_path, 1, read_only=True)
    assert completed.all() and (states == 3).all() and (nll == 7).all()


def test_padding_audit_is_bound_to_settings_and_passed_thresholds():
    audit = {"settings_sha256": "fingerprint", "extra_tokens": 7,
             "max_abs_state_difference": .001, "max_sequence_nll_difference": .005, "passed": True}
    audit["audit_sha256"] = analysis.canonical_sha(audit)
    analysis.validate_padding_audit(audit, "fingerprint")
    with pytest.raises(ValueError, match="Padding audit"):
        analysis.validate_padding_audit(audit, "other-fingerprint")
    audit["max_abs_state_difference"] = .1
    with pytest.raises(ValueError, match="Padding audit"):
        analysis.validate_padding_audit(audit, "fingerprint")


def test_batched_teacher_forcing_preserves_each_response_mask_and_pooling():
    import torch
    sys.path.insert(0, str(analysis.REFERENCE / "src"))
    import extraction as ex
    class TinyModel:
        def __call__(self, input_ids, attention_mask, **kwargs):
            self.ids = input_ids.clone()
            self.mask = attention_mask.clone()
            assert kwargs["use_cache"] is False
            base = input_ids.float()[:, :, None].repeat(1, 1, 4)
            return SimpleNamespace(hidden_states=tuple(base + i for i in range(29)),
                                   logits=torch.zeros((*input_ids.shape, 64)))
    tokenizer = SimpleNamespace(pad_token_id=0)
    tokens = [[{"input_ids": [4, 5, 6, 7, 2], "response_start": 2, "response_stop": 4},
               {"input_ids": [4, 5, 8, 9, 10, 2], "response_start": 2, "response_stop": 5}]]
    model = TinyModel()
    flat, pooled, loss, _, padded = analysis.teacher_forced_batch(
        model, tokenizer, tokens, [0], ex, torch.device("cpu"))
    assert [(i, v) for i, v, _ in flat] == [(0, 0), (0, 1)]
    assert pooled.shape == (2, 28, 3, 4)
    assert model.mask.tolist() == [[1, 1, 1, 1, 1, 0], [1, 1, 1, 1, 1, 1]]
    assert padded == 6
    np.testing.assert_array_equal(pooled[:, 0, 0, 0], [7.5, 10])
    np.testing.assert_array_equal(pooled[:, 0, 1, 0], [8, 11])
    np.testing.assert_array_equal(pooled[:, :, 2], np.asarray([pooled[0, :, 2]] * 2))
    np.testing.assert_allclose(loss[:, 1], np.log(64), atol=1e-6)
    np.testing.assert_allclose(loss[:, 0], np.asarray([2, 3]) * np.log(64), atol=1e-6)
    _, longer, longer_loss, _, padded = analysis.teacher_forced_batch(
        model, tokenizer, tokens, [0], ex, torch.device("cpu"), extra_padding=7)
    assert padded == 13
    np.testing.assert_array_equal(longer, pooled)
    np.testing.assert_allclose(longer_loss, loss, atol=1e-6)
