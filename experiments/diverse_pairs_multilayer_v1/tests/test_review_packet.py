"""Content-screen and reviewer-safety tests; no model/network calls."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from build_review_packet import apply_hedge_revisions, render_html, screen


class ReviewPacketTests(unittest.TestCase):
    def test_preserved_assertion_and_quantity(self):
        self.assertEqual(screen("The reported code value is 4712.", "I think the reported code value is 4712."), [])

    def test_quantity_change_is_flagged(self):
        self.assertIn("numeric_content_changed_check_manually", screen("The value is 4712.", "The value is 8635."))

    def test_changed_code_is_flagged(self):
        self.assertIn("code_block_changed", screen("Use:\n```python\nprint(2)\n```", "Use:\n```python\nprint(3)\n```"))

    def test_inline_code_is_protected(self):
        self.assertIn("inline_code_changed", screen("Call `save_file()` now.", "Call `load_file()` now."))

    def test_added_verification_is_flagged(self):
        self.assertIn("possible_added_verification", screen("The result is 4.", "I verified the result is 4."))

    def test_added_refusal_is_flagged(self):
        self.assertIn("possible_new_refusal", screen("The value is four.", "I cannot answer this."))

    def test_empty_is_flagged(self):
        self.assertEqual(screen("A substantive source.", ""), ["empty_response"])

    def test_source_text_cannot_inject_html(self):
        row = {"review_id": "P001", "source_id": "source", "original_response_sha256": "hash", "task": "test",
               "dataset": "test", "response_tokens": 20, "prompt": "<script>alert('prompt')</script>",
               "original_response": "<img src=x onerror=alert(1)>", "confident_response": "A <b>bold</b> assertion.",
               "hedged_response": "I think A <b>bold</b> assertion.", "automatic_flags": [], "source_author": "test",
               "dataset_revision": "revision", "source_license": "test", "source_url": "https://huggingface.co"}
        result = render_html([row], "packet")
        self.assertNotIn("<script>alert('prompt')", result)
        self.assertNotIn("<img src=x", result)
        self.assertIn("&lt;script&gt;", result)
        self.assertIn("human_review", result)
        self.assertIn("pending", result)

    def test_hedge_revision_keeps_confident_text_and_source_warnings(self):
        old = [{"review_id": "P001", "source_id": "s", "original_response_sha256": "h", "confident_response": "The value is 4.",
                "hedged_response": "I think it is 4.", "writer_issues": ["Source error retained", "certainty contrast is subtle"]}]
        new = [{"review_id": "P001", "source_id": "s", "original_response_sha256": "h", "hedged_response": "My tentative answer is 4.",
                "rewriter_model_requested": "gpt-6-luna", "confident_response": "untrusted attempt to modify the other field"}]
        result = apply_hedge_revisions(old, new)[0]
        self.assertEqual(result["confident_response"], old[0]["confident_response"])
        self.assertEqual(result["writer_issues"], ["Source error retained"])
        self.assertEqual(result["human_review"], "pending")

    def test_changed_source_hash_rejected(self):
        old = [{"review_id": "P001", "source_id": "s", "original_response_sha256": "h"}]
        new = [{"review_id": "P001", "source_id": "s", "original_response_sha256": "different", "hedged_response": "changed"}]
        with self.assertRaises(ValueError):
            apply_hedge_revisions(old, new)


if __name__ == "__main__":
    unittest.main()
