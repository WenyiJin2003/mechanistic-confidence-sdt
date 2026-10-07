import numpy as np
import torch
from confidence_pilot.common import load_config
from confidence_pilot.extract_activations import load_tokenizer, tokenize_variant, select_states, response_nll

def test_exact_response_prefix_boundary_and_content_span():
    config = load_config("configs/paired_confidence_phase_a.yaml")
    tokenizer = load_tokenizer(config)
    confident = {"variant_id": "c", "question": "What is 2 + 3?", "context": None,
                 "response_text": "I am confident: the answer is 5."}
    hedged = {**confident, "variant_id": "h", "response_text": "I am uncertain: the answer is 5."}
    first = tokenize_variant(confident, tokenizer, config)
    second = tokenize_variant(hedged, tokenizer, config)
    assert first["prompt_ids"] == second["prompt_ids"]
    assert first["input_ids"][first["boundary_position"]] == 151645
    assert first["final_content_position"] == first["boundary_position"] - 1
    assert tokenizer.decode(first["response_ids"]) == confident["response_text"]
    assert not set(first["response_ids"]) & set(tokenizer.all_special_ids)

def test_representation_pooling_excludes_prompt_boundary_and_padding():
    config = load_config("configs/paired_confidence_phase_a.yaml")
    tokenizer = load_tokenizer(config)
    row = {"variant_id": "c", "question": "What is 2 + 3?", "context": None,
           "response_text": "The answer is 5."}
    tokens = tokenize_variant(row, tokenizer, config)
    length = len(tokens["input_ids"]) + 5
    hidden_states = [torch.zeros((1, length, 1536)) for _ in range(24)]
    for layer in (14, 23):
        hidden_states[layer][0, tokens["response_start"]:tokens["response_stop"]] = 2
        hidden_states[layer][0, tokens["boundary_position"]] = 7
        hidden_states[layer][0, tokens["boundary_position"]+1:] = 100
    selected = select_states(hidden_states, tokens, [14, 23])
    assert selected.shape == (2, 4, 1536)
    np.testing.assert_array_equal(selected[:, 0], 7)
    np.testing.assert_array_equal(selected[:, 1], 2)
    np.testing.assert_array_equal(selected[:, 2], 2)
    np.testing.assert_array_equal(selected[:, 3], 0)

def test_response_nll_uses_preceding_logits_and_excludes_boundary_padding():
    input_ids = torch.tensor([0, 1, 2, 1, 3, 0])
    logits = torch.zeros((6, 4))
    logits[2] = torch.log(torch.tensor([0.05, 0.8, 0.10, 0.05]))
    logits[3, 0] = 50  # Bad boundary prediction must not enter response NLL.
    sequence, mean = response_nll(logits, input_ids, start=2, stop=4)
    expected = -np.log(.25) - np.log(.8)
    assert np.isclose(sequence, expected, atol=1e-6)
    assert np.isclose(mean, expected / 2, atol=1e-6)
