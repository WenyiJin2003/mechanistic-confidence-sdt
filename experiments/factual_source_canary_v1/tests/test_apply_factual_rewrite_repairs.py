import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock


MODULE_PATH = (
    Path(__file__).resolve().parents[1] / "src" / "apply_factual_rewrite_repairs.py"
)
SPEC = importlib.util.spec_from_file_location("apply_factual_rewrite_repairs", MODULE_PATH)
overlay = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(overlay)


def sha256_text(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def make_source(index):
    return {
        "source_id": f"source-{index}",
        "source_hash": sha256_text(f"source-{index}"),
        "original_response_sha256": sha256_text(f"original-{index}"),
        "dataset": ("asqa", "billsum", "qasper")[index % 3],
        "cue_family": f"cue-{index % 2}",
        "length_direction": "confident_longer" if index % 2 else "hesitant_longer",
        "draft_order": "confident_first" if index % 2 else "hesitant_first",
        "generation_order": index,
    }


def make_pair(source, suffix="base"):
    return {
        "source_id": source["source_id"],
        "source_hash": source["source_hash"],
        "original_response_sha256": source["original_response_sha256"],
        "dataset": source["dataset"],
        "cue_family": source["cue_family"],
        "length_direction": source["length_direction"],
        "draft_order": source["draft_order"],
        "generation_order": source["generation_order"],
        "confident_response": f"Confident {suffix} {source['source_id']}",
        "hesitant_response": f"Hesitant {suffix} {source['source_id']}",
        "issues": [],
    }


def write_jsonl(path, rows):
    path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


class ApplyFactualRewriteRepairsTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.private_root = self.root / "private_data"
        self.private_root.mkdir()
        self.sources = [make_source(index) for index in range(1, 5)]
        self.source_path = self.root / "sources.jsonl"
        self.base_path = self.root / "base.jsonl"
        self.output_path = self.private_root / "final.jsonl"
        self.provenance_path = self.private_root / "overlay.json"
        write_jsonl(
            self.source_path,
            [self.sources[2], self.sources[0], self.sources[3], self.sources[1]],
        )
        write_jsonl(self.base_path, [make_pair(source) for source in reversed(self.sources)])

    def tearDown(self):
        self.temporary_directory.cleanup()

    def repair_path(self, rows, name="repairs.jsonl"):
        path = self.root / name
        write_jsonl(path, rows)
        return path

    def apply(self, repair_paths, *, provenance=True, overwrite=False):
        return overlay.apply_factual_rewrite_repairs(
            self.source_path,
            self.base_path,
            repair_paths,
            self.output_path,
            provenance_path=self.provenance_path if provenance else None,
            overwrite=overwrite,
            private_root=self.private_root,
        )

    def test_repairs_subset_and_orders_complete_output_by_authoritative_order(self):
        repair = make_pair(self.sources[2], "repaired")
        repair["generation_order"] = self.sources[2]["generation_order"]
        provenance = self.apply([self.repair_path([repair])])

        rows = [json.loads(line) for line in self.output_path.read_text().splitlines()]
        self.assertEqual(
            [row["source_id"] for row in rows],
            ["source-1", "source-2", "source-3", "source-4"],
        )
        self.assertEqual(rows[2]["confident_response"], "Confident repaired source-3")
        self.assertEqual(rows[2]["generation_order"], 3)
        self.assertEqual(rows[1]["confident_response"], "Confident base source-2")
        self.assertEqual(provenance["repair_count"], 1)
        self.assertEqual(
            provenance["output"]["sha256"],
            hashlib.sha256(self.output_path.read_bytes()).hexdigest(),
        )
        self.assertEqual(json.loads(self.provenance_path.read_text()), provenance)

    def test_json_pairs_wrapper_and_optional_provenance_are_supported(self):
        repair_path = self.root / "repair.json"
        repair_path.write_text(json.dumps({"pairs": [make_pair(self.sources[0], "fixed")]}))

        provenance = self.apply([repair_path], provenance=False)

        self.assertTrue(self.output_path.is_file())
        self.assertFalse(self.provenance_path.exists())
        self.assertEqual(provenance["repair_count"], 1)

    def test_unknown_or_case_changed_source_id_is_rejected_without_output(self):
        repair = make_pair(self.sources[0], "fixed")
        repair["source_id"] = "Source-1"

        with self.assertRaises(overlay.RepairOverlayError) as caught:
            self.apply([self.repair_path([repair])])

        self.assertTrue(
            any(
                "unknown_repair_source_id:Source-1" in item
                for item in caught.exception.errors
            )
        )
        self.assertFalse(self.output_path.exists())
        self.assertFalse(self.provenance_path.exists())

    def test_duplicate_repair_ids_across_inputs_are_rejected_without_output(self):
        first = self.repair_path([make_pair(self.sources[1], "first")], "first.jsonl")
        second = self.repair_path([make_pair(self.sources[1], "second")], "second.jsonl")

        with self.assertRaises(overlay.RepairOverlayError) as caught:
            self.apply([first, second])

        self.assertTrue(
            any(
                "duplicate_repair_source_id:source-2" in item
                for item in caught.exception.errors
            )
        )
        self.assertFalse(self.output_path.exists())
        self.assertFalse(self.provenance_path.exists())

    def test_changed_or_missing_identity_field_is_rejected_without_output(self):
        changed = make_pair(self.sources[0], "changed")
        changed["cue_family"] = "different-cue"
        missing = make_pair(self.sources[1], "missing")
        del missing["draft_order"]

        with self.assertRaises(overlay.RepairOverlayError) as caught:
            self.apply([self.repair_path([changed, missing])])

        self.assertTrue(
            any(
                "changed_repair_identity:source-1:cue_family" in item
                for item in caught.exception.errors
            )
        )
        self.assertTrue(
            any(
                "repair_identity_field_missing:source-2:draft_order" in item
                for item in caught.exception.errors
            )
        )
        self.assertFalse(self.output_path.exists())

    def test_every_frozen_identity_field_is_protected(self):
        for field in overlay.IDENTITY_FIELDS:
            with self.subTest(field=field):
                repair = make_pair(self.sources[0], "changed")
                repair[field] = f"changed-{field}"
                path = self.repair_path([repair])

                with self.assertRaises(overlay.RepairOverlayError) as caught:
                    self.apply([path])

                self.assertTrue(
                    any(
                        f"changed_repair_identity:source-1:{field}" in item
                        for item in caught.exception.errors
                    )
                )
                self.assertFalse(self.output_path.exists())

    def test_stale_base_identity_is_rejected_before_output(self):
        pairs = [make_pair(source) for source in self.sources]
        pairs[2]["source_hash"] = sha256_text("stale")
        write_jsonl(self.base_path, pairs)

        with self.assertRaises(overlay.RepairOverlayError) as caught:
            self.apply([self.repair_path([make_pair(self.sources[0], "fixed")])])

        self.assertIn(
            "stale_base_identity:source-3:source_hash", caught.exception.errors
        )
        self.assertFalse(self.output_path.exists())

    def test_generation_order_change_is_rejected(self):
        repair = make_pair(self.sources[3], "changed")
        repair["generation_order"] = 99

        with self.assertRaises(overlay.RepairOverlayError) as caught:
            self.apply([self.repair_path([repair])])

        self.assertTrue(
            any(
                "changed_repair_identity:source-4:generation_order" in item
                for item in caught.exception.errors
            )
        )
        self.assertFalse(self.output_path.exists())

    def test_incomplete_base_is_rejected_before_output(self):
        write_jsonl(self.base_path, [make_pair(source) for source in self.sources[:-1]])

        with self.assertRaises(overlay.RepairOverlayError) as caught:
            self.apply([self.repair_path([make_pair(self.sources[0], "fixed")])])

        self.assertIn("missing_base_source_id:source-4", caught.exception.errors)
        self.assertFalse(self.output_path.exists())

    def test_second_atomic_commit_failure_restores_prior_files(self):
        repair_path = self.repair_path([make_pair(self.sources[0], "fixed")])
        old_output = b"old output\n"
        old_provenance = b'{"old":true}\n'
        self.output_path.write_bytes(old_output)
        self.provenance_path.write_bytes(old_provenance)
        real_replace = overlay.os.replace
        replace_count = 0

        def fail_on_second_commit(source, destination):
            nonlocal replace_count
            replace_count += 1
            if replace_count == 4:
                raise OSError("simulated provenance commit failure")
            return real_replace(source, destination)

        with mock.patch.object(overlay.os, "replace", side_effect=fail_on_second_commit):
            with self.assertRaises(OSError):
                self.apply([repair_path], overwrite=True)

        self.assertEqual(self.output_path.read_bytes(), old_output)
        self.assertEqual(self.provenance_path.read_bytes(), old_provenance)
        self.assertEqual(list(self.private_root.glob("*.tmp")), [])
        self.assertEqual(list(self.private_root.glob("*.rollback")), [])


if __name__ == "__main__":
    unittest.main()
