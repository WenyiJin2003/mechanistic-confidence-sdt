from __future__ import annotations

import pytest

from experiments.diverse_pairs_multilayer_v1.src import (
    apply_local_template_repairs_v37 as local,
)


def test_v37_local_patch_is_hash_tied_and_exact():
    record = {"production_slot": "P0001", "shared_template": "A marker here."}
    patch = {
        "production_slot": "P0001",
        "prior_template_sha256": local.transport.sha256_text(
            record["shared_template"]
        ),
        "template_replacements": [{"old": "marker", "new": "signal"}],
        "reason": "test",
    }
    updated = local.apply_template_patch(record, patch)
    assert updated["shared_template"] == "A signal here."
    assert updated["local_repair_lineage"]["model_calls"] == 0


def test_v37_local_patch_rejects_hash_mismatch():
    with pytest.raises(ValueError, match="Prior template hash mismatch"):
        local.apply_template_patch(
            {"production_slot": "P0001", "shared_template": "text"},
            {
                "production_slot": "P0001",
                "prior_template_sha256": "0" * 64,
                "reason": "test",
            },
        )
