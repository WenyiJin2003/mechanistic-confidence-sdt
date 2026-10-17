import hashlib
import importlib.util
import json
import tempfile
import unittest
from collections import Counter, defaultdict
from pathlib import Path


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "build_factual_rewrite_review.py"
)
SPEC = importlib.util.spec_from_file_location(
    "build_factual_rewrite_review", MODULE_PATH
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


DATASETS = ("asqa", "qasper", "billsum")


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def fixture_rows() -> tuple[list[dict], list[dict]]:
    sources: list[dict] = []
    pairs: list[dict] = []
    for dataset_index, dataset in enumerate(DATASETS):
        for local_index in range(4):
            index = dataset_index * 4 + local_index
            source_id = f"private-source-{index:02d}"
            original = (
                f"Original factual response {index} contains a unique marker "
                f"originaltoken{index} and one carefully scoped conclusion."
            )
            direction = (
                "confident_longer" if local_index < 2 else "hesitant_longer"
            )
            draft_order = (
                "confident_first" if local_index % 2 == 0 else "hesitant_first"
            )
            identity = {
                "source_id": source_id,
                "source_hash": f"source-hash-secret-{index}",
                "original_response_sha256": _sha256_text(original),
                "dataset": dataset,
                "cue_family": f"private-cue-family-{index}",
                "length_direction": direction,
                "draft_order": draft_order,
            }
            sources.append({
                **identity,
                "prompt": f"What is the factual conclusion for item {index}?",
                "original_response": original,
                "protected_qualifiers": [],
                "protected_spans": [],
            })
            pairs.append({
                **identity,
                "confident_response": (
                    f"The evidence for item {index} supports the unique conclusion "
                    f"confidenttoken{index}."
                ),
                "hesitant_response": (
                    f"My reading of item {index} tentatively supports the same unique "
                    f"conclusion hesitanttoken{index}."
                ),
                "issues": [],
            })
    return sources, pairs


class FactualRewriteReviewBuilderTests(unittest.TestCase):
    def joined(self) -> list[dict]:
        sources, pairs = fixture_rows()
        return MODULE.join_sources_and_pairs(sources, pairs)

    def test_role_balance_is_six_six_and_two_two_per_dataset(self) -> None:
        joined = self.joined()
        _, key = MODULE.build_blinded_rows(joined, seed=20261017)
        self.assertEqual(
            Counter(row["version_a_role"] for row in key),
            Counter({"confident": 6, "hesitant": 6}),
        )
        by_dataset: dict[str, list[dict]] = defaultdict(list)
        for row in key:
            by_dataset[row["dataset"]].append(row)
        self.assertEqual(set(by_dataset), set(DATASETS))
        for rows in by_dataset.values():
            self.assertEqual(
                Counter(row["version_a_role"] for row in rows),
                Counter({"confident": 2, "hesitant": 2}),
            )
            # Avoid turning the planned longer arm into an A/B shortcut.
            by_direction: dict[str, list[str]] = defaultdict(list)
            for row in rows:
                by_direction[row["length_direction"]].append(
                    row["version_a_role"]
                )
            self.assertEqual(
                {direction: Counter(roles) for direction, roles in by_direction.items()},
                {
                    "confident_longer": Counter(
                        {"confident": 1, "hesitant": 1}
                    ),
                    "hesitant_longer": Counter(
                        {"confident": 1, "hesitant": 1}
                    ),
                },
            )

    def test_output_is_deterministic_and_input_order_independent(self) -> None:
        joined = self.joined()
        first_blind, first_key = MODULE.build_blinded_rows(
            joined, seed=20261017
        )
        second_blind, second_key = MODULE.build_blinded_rows(
            list(reversed(joined)), seed=20261017
        )
        self.assertEqual(first_blind, second_blind)
        self.assertEqual(first_key, second_key)
        packet_hash = MODULE.sha256_value(first_blind)
        self.assertEqual(
            MODULE.render_html(first_blind, packet_hash),
            MODULE.render_html(second_blind, packet_hash),
        )

    def test_blinded_rows_expose_only_review_content(self) -> None:
        blinded, _ = MODULE.build_blinded_rows(self.joined(), seed=20261017)
        self.assertEqual(
            set(blinded[0]),
            {
                "review_id",
                "question",
                "original_response",
                "version_a",
                "version_b",
            },
        )
        serialized = json.dumps(blinded, sort_keys=True)
        for forbidden in (
            "source_id",
            "source_hash",
            "dataset",
            "cue_family",
            "length_direction",
            "draft_order",
            "version_a_role",
        ):
            self.assertNotIn(f'"{forbidden}"', serialized)

    def test_html_has_all_fields_but_no_answer_key(self) -> None:
        joined = self.joined()
        blinded, key = MODULE.build_blinded_rows(joined, seed=20261017)
        page = MODULE.render_html(blinded, MODULE.sha256_value(blinded))
        for field in (*MODULE.REQUIRED_REVIEW_FIELDS, "notes"):
            self.assertIn(f'data-field="{field}"', page)
        self.assertIn("Download review JSON", page)
        for forbidden_key in (
            "source_id",
            "source_hash",
            "dataset",
            "cue_family",
            "length_direction",
            "draft_order",
            "version_a_role",
            "version_b_role",
        ):
            self.assertNotIn(f'"{forbidden_key}"', page)
        for row in key:
            self.assertNotIn(row["source_id"], page)
            self.assertNotIn(row["source_hash"], page)

    def test_bundle_is_private_and_keeps_key_separate(self) -> None:
        joined = self.joined()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            private = root / "private_data"
            output = private / "review"
            result = MODULE.write_review_bundle(
                joined,
                output,
                seed=20261017,
                private_root=private,
            )
            page = (output / "BLIND_REVIEW.html").read_text(encoding="utf-8")
            key = json.loads(
                (output / "BLIND_REVIEW_KEY.json").read_text(encoding="utf-8")
            )
            manifest = result["manifest"]
            self.assertEqual(len(key["rows"]), 12)
            self.assertEqual(
                manifest["version_a_role_counts"],
                {"confident": 6, "hesitant": 6},
            )
            self.assertEqual(
                manifest["version_a_role_counts_by_dataset"],
                {
                    dataset: {"confident": 2, "hesitant": 2}
                    for dataset in sorted(DATASETS)
                },
            )
            self.assertFalse(manifest["answer_key_embedded_in_html"])
            for row in key["rows"]:
                self.assertNotIn(row["source_id"], page)
                self.assertNotIn(row["source_hash"], page)
            with self.assertRaises(ValueError):
                MODULE.write_review_bundle(
                    joined,
                    root / "public_review",
                    seed=20261017,
                    private_root=private,
                )

    def test_identity_mismatch_is_rejected(self) -> None:
        sources, pairs = fixture_rows()
        pairs[0]["source_hash"] = "tampered"
        with self.assertRaisesRegex(ValueError, "source_hash identity mismatch"):
            MODULE.join_sources_and_pairs(sources, pairs)


if __name__ == "__main__":
    unittest.main()
