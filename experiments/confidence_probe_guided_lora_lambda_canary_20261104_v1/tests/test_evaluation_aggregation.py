from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


agg = load_module("aggregate_canary", ROOT / "src" / "aggregate_canary.py")


def synthetic_grid(n: int = 4):
    grid = {}
    for role in agg.ROLES:
        for ratio in agg.RATIOS:
            rows = {}
            for index in range(n):
                split = "lora_dev" if index < n // 2 else "behavior_canary"
                key = (split, f"item-{index}")
                direction = 1 if role == "confident" else -1
                rows[key] = {
                    "run_id": f"{role}-{ratio:.2f}",
                    "role": role,
                    "target_aux_gradient_ratio": ratio,
                    "split": split,
                    "item_id": key[1],
                    "question": f"question {index}",
                    "response": f"{role} response {index} ratio {ratio}",
                    "l14_score": float(index + direction * ratio),
                    "equal28_score": float(index + direction * ratio / 2),
                    "response_token_count": 10 + index,
                    "response_word_count": 8 + index,
                    "response_character_count": 30 + index,
                    "empty_response": False,
                    "refusal_heuristic": False,
                }
            grid[(role, ratio)] = rows
    return grid


def test_role_specific_comparison_direction_and_score_aggregation():
    grid = synthetic_grid()
    confident = agg.comparison_summary(grid[("confident", 0.0)], grid[("confident", 0.10)], "confident", 0.10)
    hesitant = agg.comparison_summary(grid[("hesitant", 0.0)], grid[("hesitant", 0.10)], "hesitant", 0.10)
    assert confident["expected_direction"] == "guided_more_confident"
    assert hesitant["expected_direction"] == "guided_more_hesitant"
    assert confident["mean_l14_delta_guided_minus_baseline"] == pytest.approx(0.10)
    assert hesitant["mean_l14_delta_guided_minus_baseline"] == pytest.approx(-0.10)
    assert confident["mean_equal28_delta_guided_minus_baseline"] == pytest.approx(0.05)
    assert confident["rows"] == hesitant["rows"] == 4


def test_blinding_is_deterministic_balanced_and_hides_sources():
    grid = synthetic_grid(20)
    packet_a, key_a = agg.build_decomposition_blind_packet(grid, "seed")
    packet_b, key_b = agg.build_decomposition_blind_packet(grid, "seed")
    assert packet_a == packet_b
    assert key_a == key_b
    assert len(packet_a) == 2 * 2 * 20
    assert all("guided" not in json.dumps(row).lower() for row in packet_a)
    assert {row["A_source"] for row in key_a} == {"baseline", "guided"}
    assert len({row["blind_id"] for row in packet_a}) == len(packet_a)


def test_primary_direct_separation_and_blind_packet_cover_all_ratios():
    grid = synthetic_grid(20)
    summaries = agg.direct_separation_summary(grid)
    assert [row["ratio"] for row in summaries] == list(agg.RATIOS)
    assert all(row["rows"] == 20 for row in summaries)
    assert summaries[0]["mean_l14_gap_change_vs_ratio0"] == pytest.approx(0.0)
    assert summaries[1]["mean_l14_gap_change_vs_ratio0"] == pytest.approx(0.10)
    assert summaries[2]["mean_l14_gap_change_vs_ratio0"] == pytest.approx(0.20)
    assert all(row["confident_capped"] == row["hesitant_capped"] == 0 for row in summaries)

    packet_a, key_a = agg.build_primary_direct_blind_packet(grid, "seed")
    packet_b, key_b = agg.build_primary_direct_blind_packet(grid, "seed")
    assert packet_a == packet_b
    assert key_a == key_b
    assert len(packet_a) == len(agg.RATIOS) * 20
    assert {row["ratio"] for row in key_a} == set(agg.RATIOS)
    assert {row["A_source"] for row in key_a} == {"confident", "hesitant"}
    assert all("A_source" not in row and "B_source" not in row for row in packet_a)
    assert all("role" not in row and "ratio" not in row for row in packet_a)


def test_grid_loader_rejects_missing_rows(tmp_path: Path):
    runs = []
    for role in agg.ROLES:
        for ratio in agg.RATIOS:
            run_id = f"{role}-{ratio:.2f}"
            runs.append({"run_id": run_id, "role": role, "target_aux_gradient_ratio": ratio})
            rows = list(synthetic_grid(4)[(role, ratio)].values())
            if role == "hesitant" and ratio == 0.10:
                rows.pop()
            (tmp_path / f"{run_id}.jsonl").write_text(
                "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8"
            )
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"runs": runs}), encoding="utf-8")
    with pytest.raises(ValueError, match="item mismatch"):
        agg.load_grid(manifest, tmp_path)


def test_score_formula_matches_manual_numpy_without_importing_gpu_stack():
    source = (ROOT / "src" / "evaluate_adapters.py").read_text(encoding="utf-8")
    assert "score_response_means" in source
    means = np.arange(28 * 3, dtype=np.float64).reshape(28, 3)
    feature_mean = np.zeros_like(means)
    feature_scale = np.ones_like(means) * 2
    coef = np.ones_like(means)
    raw = np.sum((means - feature_mean) / feature_scale * coef, axis=1)
    train_mean = np.arange(28, dtype=np.float64)
    train_std = np.ones(28, dtype=np.float64) * 2
    layer_z = (raw - train_mean) / train_std
    assert layer_z[13] == pytest.approx((raw[13] - 13) / 2)
    assert layer_z.mean() == pytest.approx(float(np.mean(layer_z)))


def test_scripts_declare_zero_missing_and_secondary_equal28():
    aggregate_source = (ROOT / "src" / "aggregate_canary.py").read_text(encoding="utf-8")
    evaluate_source = (ROOT / "src" / "evaluate_adapters.py").read_text(encoding="utf-8")
    assert '"missing_rows": 0' in aggregate_source
    assert '"excluded_rows": 0' in aggregate_source
    assert "secondary correlated diagnostic" in evaluate_source
    assert "do_sample=False" in evaluate_source
