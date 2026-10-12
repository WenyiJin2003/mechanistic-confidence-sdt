import copy
import json
from collections import Counter
from pathlib import Path

import pytest
import yaml

from experiments.diverse_pairs_multilayer_v1.src import build_source_pool_1000 as pool


class TinyTokenizer:
    """Tokenizer-shaped fixture; it never loads a model or accesses a network."""

    def apply_chat_template(self, messages, tokenize=True):
        return list(range(sum(len(message["content"].split()) for message in messages) + 8))

    def __call__(self, text, add_special_tokens=False):
        return {"input_ids": list(range(len(text.split())))}


def real_config():
    return yaml.safe_load(pool.DEFAULT_CONFIG.read_text(encoding="utf-8"))


def small_config(tmp_path=None):
    config = real_config()
    config["seed"] = 17
    config["stratification"]["tasks"] = {task: 0.2 for task in pool.TASKS}
    config["stratification"]["lengths"] = {length: 1 / 3 for length in pool.LENGTHS}
    config["quotas"] = {
        partition: {
            split: {dataset: 10 for dataset in pool.DATASETS}
            for split in pool.SPLITS
        }
        for partition in pool.PARTITIONS
    }
    config["exclusions"]["minimum_old_source_ids"] = 0
    if tmp_path is not None:
        config["outputs"] = {
            "private_directory": "private/source_pool_1000_v1",
            "main_file": "SOURCE_MANIFEST_MAIN_1000.jsonl",
            "reserve_file": "SOURCE_MANIFEST_RESERVE_200.jsonl",
            "all_file": "SOURCE_MANIFEST.jsonl",
            "public_manifest": "manifests/source_pool_1000_freeze.json",
            "public_coverage": "manifests/source_pool_1000_coverage.json",
        }
    return config


def synthetic_row(dataset, task, length, index):
    source_id = f"{dataset.split('/')[-1]}-{task}-{length}-{index}"
    alphabetic_marker = "marker" + "".join(chr(97 + (value % 26)) for value in [index, index // 26, index // 676])
    prompt = (
        f"Explain the independent {task} example {index} for the {length} group. "
        f"Use source marker {source_id} {alphabetic_marker} and discuss its distinct assumptions clearly."
    )
    response = (
        f"This is the distinct response for {source_id}. It explains the requested topic with "
        "enough independent detail to support a later content-preserving rewrite while avoiding "
        "any shared factual template or repeated conclusion across records."
    )
    prompt_hash = pool.sha256_text(pool.normalize(prompt))
    canonical_hash = pool.sha256_text(pool.canonical_prompt(prompt))
    return {
        "source_id": source_id,
        "dataset": dataset,
        "dataset_revision": "synthetic-revision",
        "prompt": prompt,
        "original_response": response,
        "original_response_sha256": pool.sha256_text(response),
        "normalized_response_sha256": pool.sha256_text(pool.normalize(response)),
        "normalized_prompt_sha256": prompt_hash,
        "canonical_prompt_sha256": canonical_hash,
        "development_template_group": canonical_hash,
        "legacy_template_group": pool.legacy_template_group(prompt),
        "group_id": "group-" + canonical_hash,
        "task": task,
        "length_bin": length,
    }


def synthetic_candidates(per_cell=15):
    return [
        synthetic_row(dataset, task, length, index)
        for dataset in pool.DATASETS
        for task in pool.TASKS
        for length in pool.LENGTHS
        for index in range(per_cell)
    ]


def test_actual_config_has_exact_requested_source_and_split_quotas():
    config = real_config()
    assert sum(
        config["quotas"]["main"][split][dataset]
        for split in pool.SPLITS for dataset in pool.DATASETS
    ) == 1000
    assert sum(
        config["quotas"]["reserve"][split][dataset]
        for split in pool.SPLITS for dataset in pool.DATASETS
    ) == 200
    assert config["quotas"]["main"]["train"] == {
        "allenai/WildChat-1M": 525,
        "nvidia/HelpSteer2": 175,
    }
    assert config["quotas"]["main"]["validation"] == {
        "allenai/WildChat-1M": 112,
        "nvidia/HelpSteer2": 38,
    }
    assert config["quotas"]["main"]["test"] == {
        "allenai/WildChat-1M": 113,
        "nvidia/HelpSteer2": 37,
    }
    assert sum(pool.required_task_counts(config, pool.DATASETS[0]).values()) == 900
    assert sum(pool.required_task_counts(config, pool.DATASETS[1]).values()) == 300
    targets = pool.wildchat_stop_targets(config)
    assert all(
        targets[task] > pool.required_task_counts(config, pool.DATASETS[0])[task]
        for task in pool.TASKS
    )


def test_prepare_candidate_uses_local_tokenizer_shape_only():
    config = real_config()
    raw = synthetic_row(pool.DATASETS[0], "factual_explanation", "short", 999)
    for key in [
        "original_response_sha256", "normalized_response_sha256", "normalized_prompt_sha256",
        "canonical_prompt_sha256", "development_template_group", "legacy_template_group",
        "group_id", "task", "length_bin",
    ]:
        raw.pop(key, None)
    prepared, reason = pool.prepare_candidate(raw, TinyTokenizer(), config)
    assert reason == "eligible"
    assert prepared["source_id"] == raw["source_id"]
    assert prepared["original_response_sha256"] == pool.sha256_text(raw["original_response"])
    assert prepared["task"] == "factual_explanation"
    assert prepared["human_review"] == "pending"


def test_candidate_cache_reuses_only_matching_acquisition_config(tmp_path):
    config = real_config()
    path = tmp_path / "candidates.jsonl"
    rows = [synthetic_row(pool.DATASETS[0], "factual_explanation", "short", 50)]
    pool.write_candidate_cache(path, rows, config, {"shard": "synthetic"})
    assert pool.read_candidate_cache(path, config) == rows
    changed = copy.deepcopy(config)
    changed["screening"]["near_prompt_jaccard"] = 0.8
    with pytest.raises(ValueError, match="different acquisition config"):
        pool.read_candidate_cache(path, changed)


def test_duplicate_index_enforces_all_old_anchor_and_near_text_routes():
    config = real_config()
    old = synthetic_row(pool.DATASETS[0], "factual_explanation", "medium", 1)
    index = pool.DuplicateIndex(config)
    index.add(old)

    identity = synthetic_row(pool.DATASETS[1], "math_logic", "short", 2)
    identity["source_id"] = old["source_id"]
    assert index.duplicate_reason(identity) == "identity_overlap"

    group = synthetic_row(pool.DATASETS[1], "math_logic", "short", 3)
    group["group_id"] = old["group_id"]
    assert index.duplicate_reason(group) == "group_or_canonical_prompt_overlap"

    prompt_hash = synthetic_row(pool.DATASETS[1], "math_logic", "short", 4)
    prompt_hash["normalized_prompt_sha256"] = old["normalized_prompt_sha256"]
    assert index.duplicate_reason(prompt_hash) == "exact_prompt_overlap"

    response_hash = synthetic_row(pool.DATASETS[1], "math_logic", "short", 5)
    response_hash["original_response_sha256"] = old["original_response_sha256"]
    assert index.duplicate_reason(response_hash) == "exact_response_overlap"

    canonical_old = synthetic_row(pool.DATASETS[0], "factual_explanation", "short", 6)
    canonical_old["prompt"] = "Explain the result of calculation 123 with all assumptions and intermediate reasoning."
    index2 = pool.DuplicateIndex(config)
    index2.add(canonical_old)
    canonical_new = synthetic_row(pool.DATASETS[1], "math_logic", "short", 7)
    canonical_new["prompt"] = "Explain the result of calculation 456 with all assumptions and intermediate reasoning."
    for field in ["group_id", "development_template_group", "legacy_template_group", "canonical_prompt_sha256"]:
        canonical_new.pop(field, None)
    assert index2.duplicate_reason(canonical_new) == "group_or_canonical_prompt_overlap"

    near_old = synthetic_row(pool.DATASETS[0], "factual_explanation", "short", 8)
    near_old["prompt"] = " ".join(f"sharedword{i}" for i in range(45))
    index3 = pool.DuplicateIndex(config)
    index3.add(near_old)
    near_new = synthetic_row(pool.DATASETS[1], "math_logic", "short", 9)
    near_new["prompt"] = near_old["prompt"] + " oneadditionalword"
    for field in ["group_id", "development_template_group", "legacy_template_group", "canonical_prompt_sha256", "normalized_prompt_sha256"]:
        near_new.pop(field, None)
    assert index3.duplicate_reason(near_new) == "near_prompt_overlap"

    response_old = synthetic_row(pool.DATASETS[0], "factual_explanation", "short", 10)
    response_old["original_response"] = " ".join(f"responseword{i}" for i in range(45))
    index4 = pool.DuplicateIndex(config)
    index4.add(response_old)
    response_new = synthetic_row(pool.DATASETS[1], "math_logic", "short", 11)
    response_new["original_response"] = response_old["original_response"] + " oneadditionalresponseword"
    response_new.pop("original_response_sha256", None)
    response_new.pop("normalized_response_sha256", None)
    assert index4.duplicate_reason(response_new) == "near_response_overlap"


def test_selection_is_deterministic_exact_grouped_and_covers_held_out_cells():
    config = small_config()
    candidates = synthetic_candidates()
    first = pool.select_frozen_pool(copy.deepcopy(candidates), config)
    second = pool.select_frozen_pool(list(reversed(copy.deepcopy(candidates))), config)
    assert [row["source_id"] for row in first] == [row["source_id"] for row in second]
    assert len(first) == 120
    assert len({row["group_id"] for row in first}) == 120
    for partition in pool.PARTITIONS:
        for split in pool.SPLITS:
            for dataset in pool.DATASETS:
                assert sum(
                    row["pool_partition"] == partition
                    and row["split"] == split
                    and row["dataset"] == dataset
                    for row in first
                ) == 10
    for split in ["validation", "test"]:
        held_out = [row for row in first if row["pool_partition"] == "main" and row["split"] == split]
        assert {row["task"] for row in held_out} == set(pool.TASKS)
        assert {row["length_bin"] for row in held_out} == set(pool.LENGTHS)
    for partition in pool.PARTITIONS:
        for split in pool.SPLITS:
            bucket = [row for row in first if row["pool_partition"] == partition and row["split"] == split]
            if split == "test":
                assert {row["rewrite_family"] for row in bucket} == {"C"}
            else:
                assert {row["rewrite_family"] for row in bucket} <= {"A", "B"}
            for task in pool.TASKS:
                for length in pool.LENGTHS:
                    cell = [row for row in bucket if row["task"] == task and row["length_bin"] == length]
                    if not cell:
                        continue
                    if split != "test":
                        family_counts = Counter(row["rewrite_family"] for row in cell)
                        assert abs(family_counts["A"] - family_counts["B"]) <= 1
                    longer_counts = Counter(row["target_longer_member"] for row in cell)
                    assert abs(longer_counts["confident"] - longer_counts["hedged"]) <= 1


def test_freeze_is_text_private_resumable_and_never_touches_old_50(tmp_path):
    config = small_config(tmp_path)
    rows = pool.select_frozen_pool(synthetic_candidates(), config)
    old_50 = tmp_path / "experiments/diverse_pairs_multilayer_v1/private_data/review_sources_50.jsonl"
    old_50.parent.mkdir(parents=True)
    old_50.write_text("old-50-sentinel\n", encoding="utf-8")
    result = pool.freeze_outputs(
        rows,
        config,
        "synthetic-config-hash",
        Counter({"old_overlap": 3}),
        {"tokenizer.json": "tokenizer-hash", "tokenizer_config.json": "config-hash"},
        repo=tmp_path,
    )
    assert result["all_outputs_reused"] is False
    assert old_50.read_text(encoding="utf-8") == "old-50-sentinel\n"
    all_rows = pool.read_jsonl(Path(result["private_manifest"]))
    required = {
        "source_id", "prompt", "original_response", "original_response_sha256", "split",
        "rewrite_family", "rewrite_output_order", "target_longer_member",
    }
    assert required <= set(all_rows[0])
    manifest = json.loads(Path(result["public_manifest"]).read_text(encoding="utf-8"))
    assert manifest["contains_source_text"] is False
    assert "prompt" not in manifest["source_records"][0]
    assert "original_response" not in manifest["source_records"][0]
    assert manifest["source_count"] == 120
    assert manifest["main_source_count"] == 60
    main_path = tmp_path / config["outputs"]["private_directory"] / config["outputs"]["main_file"]
    assert manifest["main_file_sha256"] == pool.sha256_file(main_path)
    ordered_main = [row for row in all_rows if row["pool_partition"] == "main"]
    ordered_ids_hash = pool.sha256_bytes(
        "".join(row["source_id"] + "\n" for row in ordered_main).encode("utf-8")
    )
    assert manifest["main_source_ids_sha256"] == ordered_ids_hash
    assert manifest["source_ids_sha256"] == ordered_ids_hash

    replay = pool.freeze_outputs(
        rows,
        config,
        "synthetic-config-hash",
        Counter({"old_overlap": 3}),
        {"tokenizer.json": "tokenizer-hash", "tokenizer_config.json": "config-hash"},
        repo=tmp_path,
    )
    assert replay["all_outputs_reused"] is True

    main_path.write_text("corrupt\n", encoding="utf-8")
    with pytest.raises(FileExistsError, match="Refusing to overwrite"):
        pool.freeze_outputs(
            rows,
            config,
            "synthetic-config-hash",
            Counter({"old_overlap": 3}),
            {"tokenizer.json": "tokenizer-hash", "tokenizer_config.json": "config-hash"},
            repo=tmp_path,
        )
