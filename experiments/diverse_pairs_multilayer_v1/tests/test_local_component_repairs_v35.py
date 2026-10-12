from __future__ import annotations

import pytest

from experiments.diverse_pairs_multilayer_v1.src import (
    apply_local_component_repairs_v35 as local,
)


def _record():
    return {
        "production_slot": "P0001",
        "shared_template": "Before <STANCE_1> after",
        "confident_cues": ["clearly"],
        "hedged_cues": ["perhaps"],
    }


def test_local_patch_is_hash_tied_and_text_replacement_is_unique():
    record = _record()
    patch = {
        "production_slot": "P0001",
        "prior_component_sha256": local.component_sha256(record),
        "template_replacements": [{"old": "Before", "new": "Earlier"}],
        "confident_cues": ["quite clearly"],
        "reason": "test",
    }
    updated = local.apply_patch_to_record(record, patch)
    assert updated["shared_template"] == "Earlier <STANCE_1> after"
    assert updated["confident_cues"] == ["quite clearly"]
    assert updated["local_repair_lineage"]["model_calls"] == 0


def test_local_patch_rejects_prior_hash_mismatch():
    with pytest.raises(ValueError, match="Prior component hash mismatch"):
        local.apply_patch_to_record(_record(), {
            "production_slot": "P0001",
            "prior_component_sha256": "0" * 64,
            "reason": "test",
        })
