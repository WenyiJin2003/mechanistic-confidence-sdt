"""Check independent output parsing and likelihood token alignment."""
import unittest

import torch

from confidence_pilot.evidence_behavior_v4 import candidate_logps, parse_choice


class EvidenceBehaviorTests(unittest.TestCase):
    def test_parser_keeps_abstention_and_other(self):
        candidates = {"A": "4712", "B": "8635"}
        self.assertEqual(parse_choice("4712.", candidates), "A")
        self.assertEqual(parse_choice("The code is 8635.", candidates), "B")
        self.assertEqual(parse_choice("Unknown", candidates), "unknown")
        self.assertEqual(parse_choice("4712 or 8635", candidates), "other")
        self.assertEqual(parse_choice("The code is 94712", candidates), "other")
        self.assertEqual(parse_choice("The code is not 4712.", candidates), "other")
        self.assertEqual(parse_choice("4712 is incorrect.", candidates), "other")

    def test_candidate_score_uses_preceding_logits_and_all_suffix_tokens(self):
        ids = torch.tensor([[0, 1, 2, 3], [0, 1, 3, 2]])
        logits = torch.zeros((2, 4, 4))
        logits[0, 1, 2] = 3
        logits[0, 2, 3] = 3
        # At prompt_length=2, the last prompt token predicts the first value.
        a, b = candidate_logps(logits, ids, 2)
        self.assertGreater(a, b)
        logits[:, 3] = 100  # The last suffix token must never predict itself.
        self.assertEqual((a, b), tuple(candidate_logps(logits, ids, 2)))


if __name__ == "__main__":
    unittest.main()
