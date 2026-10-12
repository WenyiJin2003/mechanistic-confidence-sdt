import copy
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
import torch
from transformers import Qwen2Config, Qwen2ForCausalLM

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE / "src"))
import extraction as ex
from run_preflight import choose_pairs, flatten_pairs


def config():
    return ex.load_config(BASE / "configs/diverse_pairs_multilayer_v1.yaml")


def rows():
    return [{"source_id": "source", "group_id": "group", "prompt": "Explain this.",
             "variant": v, "response_text": t, "human_review": "pending"}
            for v, t in [("confident", "The answer is 5."), ("hedged", "I think the answer is 5.")]]


def test_real_cached_tokenizer_exact_spans_and_prompt():
    cfg = config()
    tokenizer = ex.load_tokenizer(cfg)
    first, second = [ex.tokenize_response(r, tokenizer, cfg) for r in rows()]
    assert first["prompt_ids"] == second["prompt_ids"]
    for tok, row in zip([first, second], rows()):
        assert tokenizer.decode(tok["response_ids"]) == row["response_text"]
        assert tok["input_ids"][tok["response_stop"]] == tokenizer.convert_tokens_to_ids("<|im_end|>")
        assert tok["final_response_position"] == tok["response_stop"] - 1
        assert not set(tok["response_ids"]) & set(tokenizer.all_special_ids)


def test_pooling_excludes_prompt_marker_padding_and_embedding():
    token = {"response_start": 2, "response_stop": 5}
    hidden = [torch.full((1, 10, 4), 99.0) for _ in range(4)]
    for layer in [1, 2, 3]:
        hidden[layer][0, 1] = -layer
        hidden[layer][0, 2:5] = layer
    selected = ex.pool_states(hidden, token, [1, 2, 3])
    assert selected.shape == (3, 3, 4)
    np.testing.assert_array_equal(selected[:, 0, 0], [1, 2, 3])
    np.testing.assert_array_equal(selected[:, 1, 0], [1, 2, 3])
    np.testing.assert_array_equal(selected[:, 2, 0], [-1, -2, -3])


def test_nll_shift_and_chunking_exclude_end_marker():
    ids = torch.tensor([0, 1, 2, 1, 3, 0])
    logits = torch.zeros((6, 4))
    logits[2] = torch.log(torch.tensor([0.05, 0.8, 0.10, 0.05]))
    logits[3, 0] = 50
    seq, mean = ex.response_nll(logits, ids, 2, 4, chunk_size=1)
    expected = -np.log(.25) - np.log(.8)
    assert seq == pytest.approx(expected, abs=1e-6)
    assert mean == pytest.approx(expected / 2, abs=1e-6)


def test_installed_qwen_layer_index_and_final_normalization():
    tiny = Qwen2Config(vocab_size=32, hidden_size=16, intermediate_size=24,
                      num_hidden_layers=2, num_attention_heads=2, num_key_value_heads=2)
    model = Qwen2ForCausalLM(tiny).eval()
    captured = {}
    def save(name):
        def hook(module, args, output):
            captured[name] = output.detach().clone()
        return hook
    hooks = [model.model.layers[0].register_forward_hook(save("block1")),
             model.model.layers[1].register_forward_hook(save("block2_pre_norm")),
             model.model.norm.register_forward_hook(save("final_norm"))]
    ids = torch.tensor([[1, 7, 3, 8]])
    with torch.inference_mode():
        result = model(input_ids=ids, output_hidden_states=True, use_cache=False)
        embedding = model.model.embed_tokens(ids)
    for hook in hooks:
        hook.remove()
    assert len(result.hidden_states) == 3
    torch.testing.assert_close(result.hidden_states[0], embedding)
    torch.testing.assert_close(result.hidden_states[1], captured["block1"])
    torch.testing.assert_close(result.hidden_states[2], captured["final_norm"])
    assert not torch.allclose(captured["block2_pre_norm"], captured["final_norm"])


def test_pair_identity_limits_and_review_gate():
    cfg = config()
    assert len(ex.validate_pair_rows(rows(), cfg)) == 1
    with pytest.raises(ValueError, match="exactly one"):
        ex.validate_pair_rows(rows()[:1], cfg)
    bad = rows()
    bad[1]["group_id"] = "other"
    with pytest.raises(ValueError, match="Group"):
        ex.validate_pair_rows(bad, cfg)
    cfg["runtime"]["max_pairs"] = 0
    with pytest.raises(ValueError, match="cap"):
        ex.validate_pair_rows(rows(), cfg)
    cfg = config()
    cfg["data"]["phase"] = "scientific_extraction"
    with pytest.raises(ValueError, match="Unreviewed"):
        ex.validate_pair_rows(rows(), cfg)


def test_full_file_hash_detects_same_size_weight_change(tmp_path):
    file = tmp_path / "weights"
    file.write_bytes(b"AAAA")
    first = ex.file_sha256(file)
    file.write_bytes(b"BBBB")
    assert ex.file_sha256(file) != first


def test_reversed_pair_order_rejected_before_model_loading():
    with pytest.raises(ValueError, match="confident-then-hedged"):
        ex.validate_pair_rows(rows()[::-1], config())


class TinyTokenizer:
    pad_token_id = 0
    all_special_ids = [0, 2]
    chat_template = "synthetic-test-only"
    def apply_chat_template(self, messages, tokenize=False, add_generation_prompt=False):
        prefix = "P:" + messages[1]["content"] + ":A:"
        return prefix if add_generation_prompt else prefix + messages[-1]["content"] + "§"
    def __call__(self, text, add_special_tokens=False):
        return {"input_ids": [2 if char == "§" else ord(char) for char in text]}
    def convert_tokens_to_ids(self, text):
        return 2
    def decode(self, ids, skip_special_tokens=False):
        return "".join("§" if i == 2 else chr(i) for i in ids)


class TinyModel(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.dummy = torch.nn.Parameter(torch.zeros(1))
        self.config = SimpleNamespace(num_hidden_layers=3, hidden_size=4)
    def forward(self, input_ids, attention_mask, **kwargs):
        initial = input_ids.float()[:, :, None].repeat(1, 1, 4) / 256
        hidden = tuple(initial + i for i in range(4))
        return SimpleNamespace(hidden_states=hidden, logits=torch.zeros((*input_ids.shape, 256)))


def test_cache_resume_padding_and_tampered_mask(tmp_path, monkeypatch):
    cfg = config()
    cfg["model"].update(expected_num_layers=3, expected_hidden_size=4, layers=[1, 2, 3])
    cfg["runtime"].update(device_preference=["cpu"], cache_dir=str(tmp_path / "cache"))
    for name in ["model.safetensors", "config.json", "tokenizer.json", "tokenizer_config.json"]:
        (tmp_path / name).write_text("test-file")
    monkeypatch.setattr(ex, "local_snapshot", lambda c: tmp_path)
    monkeypatch.setattr(ex, "load_tokenizer", lambda c: TinyTokenizer())
    monkeypatch.setattr(ex.AutoModelForCausalLM, "from_pretrained", lambda *a, **k: TinyModel())
    _, states, first = ex.extract_rows(rows(), cfg, check_padding=True)
    assert first["forward_calls"] == 3
    assert first["padding_check"]["passed"]
    def must_not_load(*args, **kwargs):
        raise AssertionError("Model loaded during cache-only resume")
    monkeypatch.setattr(ex.AutoModelForCausalLM, "from_pretrained", must_not_load)
    _, cached, resumed = ex.extract_rows(rows(), cfg)
    assert resumed["forward_calls"] == 0 and resumed["cache_hits"] == 2
    np.testing.assert_array_equal(cached, states)
    cache_file = next((tmp_path / "cache").glob("*.npz"))
    with np.load(cache_file) as saved:
        arrays = {key: saved[key].copy() for key in saved.files}
    arrays["response_mask"][:] = False
    ex.write_npz(cache_file, **arrays)
    with pytest.raises(ValueError, match="span/layer"):
        ex.extract_rows(rows(), cfg)


def test_length_rank_selection_and_canonical_pair_order():
    pairs = [{"source_id": str(i), "group_id": str(i), "review_id": str(i),
              "reserved_split": "train_development", "prompt": "q", "confident_response": "c",
              "hedged_response": "h", "token_stats": {"c": {"full_input_tokens": i + 5}}}
             for i in range(50)]
    chosen = choose_pairs(pairs, 20)
    assert len(chosen) == 20 and chosen[0]["source_id"] == "0" and chosen[-1]["source_id"] == "49"
    flat = flatten_pairs(chosen)
    assert [r["variant"] for r in flat[:2]] == ["confident", "hedged"]
    assert flat[0]["human_review"] == "pending"
