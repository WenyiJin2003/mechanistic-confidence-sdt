import importlib.util
import hashlib
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

import numpy as np


PATH = Path(__file__).with_name("build_activation_bundles.py")
SPEC = importlib.util.spec_from_file_location("scaleup_extraction_tested", PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def row(identifier="P1"):
    return {
        "id": identifier, "source_id": "S-" + identifier, "group_id": "G-" + identifier,
        "question": "What is the answer?", "confident_response": "The answer is five.",
        "hesitant_response": "The answer may be five.",
    }


class ExtractionPreparationTests(unittest.TestCase):
    def test_tampered_frozen_module_is_rejected_before_top_level_side_effect(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            marker = base / "executed.txt"
            tampered = base / "tampered.py"
            tampered.write_text(
                "from pathlib import Path\n"
                f"Path({str(marker)!r}).write_text('executed')\n",
                encoding="utf-8",
            )
            with self.assertRaises(RuntimeError):
                MODULE._load_verified_frozen_module(tampered, "0" * 64)
            self.assertFalse(marker.exists())

    def test_forward_denominator_is_exact(self):
        self.assertEqual(MODULE.EXPECTED_NEW_MAIN_FORWARDS, 2538)

    def test_flat_rows_has_authenticated_role_order(self):
        flat = MODULE.flat_rows([row()])
        self.assertEqual([item["variant"] for item in flat], ["confident", "hedged"])
        self.assertEqual([item["response_text"] for item in flat],
                         [row()["confident_response"], row()["hesitant_response"]])

    def test_bundle_binds_both_response_axes(self):
        states = (np.arange(2 * 28 * 1536, dtype=np.float32) % 257).astype(np.float16)
        states = states.reshape(1, 2, 28, 1536)
        bundle = MODULE.build_bundle_arrays([row()], states)
        self.assertEqual(bundle["pair_order"].tolist(), ["confident", "hesitant"])
        self.assertEqual(bundle["response_content_sha256"].shape, (1, 2))
        self.assertEqual(bundle["state_binding_sha256"].shape, (1, 2))
        swapped = MODULE.build_bundle_arrays([row()], states[:, ::-1])
        self.assertNotEqual(bundle["state_binding_sha256"][0, 0],
                            swapped["state_binding_sha256"][0, 0])
        self.assertEqual(bundle["response_content_sha256"].tolist(),
                         swapped["response_content_sha256"].tolist())

    def test_nonfinite_or_wrong_shape_fails(self):
        with self.assertRaises(MODULE.ExtractionContractError):
            MODULE.build_bundle_arrays([row()], np.zeros((1, 2, 27, 1536), np.float16))
        states = np.zeros((1, 2, 28, 1536), np.float16)
        states[0, 0, 0, 0] = np.nan
        with self.assertRaises(MODULE.ExtractionContractError):
            MODULE.build_bundle_arrays([row()], states)

    def test_state_binding_uses_the_saved_float16_bytes(self):
        states = np.full((1, 2, 28, 1536), 1.0003, np.float32)
        bundle = MODULE.build_bundle_arrays([row()], states)
        self.assertEqual(bundle["states"].dtype, np.float16)
        expected = MODULE.state_binding_sha256(
            bundle["states"][0, 0], bundle["response_content_sha256"][0, 0])
        self.assertEqual(bundle["state_binding_sha256"][0, 0], expected)

    def test_response_cache_checks_tokens_axis_and_settings(self):
        token = {"input_ids": [1, 2, 3], "response_start": 1, "response_stop": 3}
        mask = np.array([False, True, True])
        pooled = np.zeros((28, 3, 1536), np.float16)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cache.npz"
            np.savez_compressed(
                path, pooled=pooled, input_ids=np.array([1, 2, 3]), response_mask=mask,
                layer_ids=np.arange(1, 29), positions=np.asarray(MODULE.POSITIONS),
                settings_sha256=np.asarray(MODULE.FEATURE_SETTINGS_SHA256),
            )
            loaded = MODULE._validate_response_cache(path, token, None)
            np.testing.assert_array_equal(loaded, pooled)
            bad = Path(directory) / "bad.npz"
            np.savez_compressed(
                bad, pooled=pooled, input_ids=np.array([1, 2, 4]), response_mask=mask,
                layer_ids=np.arange(1, 29), positions=np.asarray(MODULE.POSITIONS),
                settings_sha256=np.asarray(MODULE.FEATURE_SETTINGS_SHA256),
            )
            with self.assertRaises(MODULE.ExtractionContractError):
                MODULE._validate_response_cache(bad, token, None)

    def test_hash_contract_is_role_sensitive(self):
        self.assertNotEqual(MODULE.response_content_sha256(row(), "confident"),
                            MODULE.response_content_sha256(row(), "hesitant"))
        changed = row()
        changed["question"] += " "
        self.assertNotEqual(MODULE.pair_content_sha256(row()), MODULE.pair_content_sha256(changed))

    def test_runtime_mismatch_aborts_before_any_forward(self):
        calls = {"forward": 0}
        fake = SimpleNamespace(
            torch=SimpleNamespace(__version__="2.14.1"),
            transformers=SimpleNamespace(__version__=MODULE.EXPECTED_TRANSFORMERS_VERSION),
            extract_rows=lambda *args, **kwargs: calls.__setitem__("forward", calls["forward"] + 1),
        )
        with self.assertRaises(MODULE.ExtractionContractError):
            MODULE.verify_runtime_versions(fake)
        self.assertEqual(calls["forward"], 0)

    def test_runner_pin_tamper_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            runner = Path(directory) / "runner.py"
            prereg = Path(directory) / "pre.json"
            runner.write_bytes(b"runner-v1")
            prereg.write_bytes(b"{}\n")
            rh = hashlib.sha256(runner.read_bytes()).hexdigest()
            ph = hashlib.sha256(prereg.read_bytes()).hexdigest()
            pins = MODULE.authenticate_runner_pins(runner, prereg, rh, ph)
            self.assertEqual(pins["runner_sha256"], rh)
            runner.write_bytes(b"runner-v2")
            with self.assertRaises(MODULE.ExtractionContractError):
                MODULE.authenticate_runner_pins(runner, prereg, rh, ph)

    def test_cf3_mapping_uses_exact_padded_pair_cache_keys(self):
        class Tokenizer:
            pass

        class FakeExtraction:
            @staticmethod
            def load_tokenizer(config):
                return Tokenizer()

            @staticmethod
            def tokenize_response(item, tokenizer, config):
                ids = [1] + [ord(char) % 127 + 3 for char in item["response_text"]]
                return {"input_ids": ids, "response_start": 1, "response_stop": len(ids),
                        "response_ids": ids[1:]}

            @staticmethod
            def digest(value):
                raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
                return hashlib.sha256(raw.encode()).hexdigest()

        with tempfile.TemporaryDirectory() as directory:
            old_cache = MODULE.core.CF3_CACHE
            MODULE.core.CF3_CACHE = Path(directory)
            try:
                pair = row("CF3-X")
                tokens, padded = MODULE._tokenize_pairs([pair], FakeExtraction, {})
                for index, (token, width) in enumerate(zip(tokens, padded)):
                    key = FakeExtraction.digest({
                        "settings": MODULE.FEATURE_SETTINGS_SHA256,
                        "input_ids": token["input_ids"], "padded_length": width,
                    })
                    mask = np.zeros(len(token["input_ids"]), dtype=bool)
                    mask[token["response_start"]:token["response_stop"]] = True
                    pooled = np.full((28, 3, 1536), index + 1, np.float16)
                    np.savez_compressed(
                        MODULE.core.CF3_CACHE / f"{key}.npz", pooled=pooled,
                        input_ids=np.asarray(token["input_ids"]), response_mask=mask,
                        layer_ids=np.arange(1, 29), positions=np.asarray(MODULE.POSITIONS),
                        settings_sha256=np.asarray(MODULE.FEATURE_SETTINGS_SHA256),
                    )
                states, audit = MODULE.build_cf3_from_existing_cache([pair], FakeExtraction, {})
                self.assertEqual(states.shape, (1, 2, 28, 1536))
                self.assertTrue(np.all(states[0, 0] == 1))
                self.assertTrue(np.all(states[0, 1] == 2))
                self.assertEqual(audit["new_forwards"], 0)
                self.assertEqual(audit["reused_response_caches"], 2)
            finally:
                MODULE.core.CF3_CACHE = old_cache

    def test_partial_bundle_publication_resumes_and_rejects_tamper(self):
        arrays = MODULE.build_bundle_arrays(
            [row()], np.zeros((1, 2, 28, 1536), dtype=np.float16))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bundle.npz"
            self.assertEqual(MODULE._atomic_npz(path, **arrays), "created")
            with np.load(path, allow_pickle=False) as saved:
                for key in ("position", "settings_sha256", "model_id", "model_revision",
                            "split_freeze_sha256", "runner_sha256", "preregistration_sha256",
                            "bundle_schema_version", "bundle_builder_sha256"):
                    self.assertEqual(saved[key].shape, (), key)
            first_hash = MODULE.file_sha256(path)
            self.assertEqual(MODULE._atomic_npz(path, **arrays), "verified_existing")
            self.assertEqual(MODULE.file_sha256(path), first_hash)
            path.write_bytes(path.read_bytes() + b"tamper")
            with self.assertRaises(MODULE.ExtractionContractError):
                MODULE._atomic_npz(path, **arrays)

    def test_saved_bundle_loads_in_final_runner_with_scalar_metadata(self):
        runner_path = MODULE.RUNNER_SOURCE
        spec = importlib.util.spec_from_file_location("final_runner_bundle_integration", runner_path)
        runner = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(runner)
        pair = row()
        arrays = MODULE.build_bundle_arrays(
            [pair], np.zeros((1, 2, 28, 1536), dtype=np.float16))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bundle.npz"
            MODULE._atomic_npz(path, **arrays)
            loaded, metadata = runner.load_activation_bundle(path, [pair])
            self.assertEqual(loaded.shape, (1, 2, 28, 1536))
            self.assertEqual(metadata["pair_order"], ["confident", "hesitant"])

    def test_final_runner_rejects_v1_scalar_promotion_and_accepts_v2(self):
        spec = importlib.util.spec_from_file_location(
            "final_runner_scalar_regression", MODULE.RUNNER_SOURCE)
        runner = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(runner)
        pair = row("axis")
        arrays = MODULE.build_bundle_arrays(
            [pair], np.zeros((1, 2, 28, 1536), dtype=np.float16))
        v1_arrays = {
            key: (np.ascontiguousarray(value) if np.asarray(value).ndim == 0 else value)
            for key, value in arrays.items()
        }
        with tempfile.TemporaryDirectory() as directory:
            v1 = Path(directory) / "v1.npz"
            v2 = Path(directory) / "v2.npz"
            MODULE._write_deterministic_npz(v1, v1_arrays)
            MODULE._atomic_npz(v2, **arrays)
            with self.assertRaises(runner.ContractError):
                runner.load_activation_bundle(v1, [pair])
            loaded, _ = runner.load_activation_bundle(v2, [pair])
            self.assertEqual(loaded.shape, (1, 2, 28, 1536))

    def test_partial_audit_publication_resumes_and_rejects_tamper(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "audit.json"
            value = {"status": "complete", "count": 2}
            self.assertEqual(MODULE._atomic_json(path, value), "created")
            self.assertEqual(MODULE._atomic_json(path, value), "verified_existing")
            path.write_text("{}\n")
            with self.assertRaises(MODULE.ExtractionContractError):
                MODULE._atomic_json(path, value)

    def test_audit_resume_accepts_only_lifecycle_label_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "audit.json"
            created = {
                "status": "complete",
                "count": 2,
                "outputs": [
                    {"id": "train", "lifecycle": "created", "sha256": "a" * 64},
                    {"id": "dev", "lifecycle": "created", "sha256": "b" * 64},
                ],
                "audit_lifecycle": "created",
            }
            resumed = {
                "status": "complete",
                "count": 2,
                "outputs": [
                    {"id": "train", "lifecycle": "verified_existing", "sha256": "a" * 64},
                    {"id": "dev", "lifecycle": "verified_existing", "sha256": "b" * 64},
                ],
                "audit_lifecycle": "verified_existing_lifecycle_equivalent",
            }
            self.assertEqual(MODULE._atomic_json(path, created), "created")
            self.assertEqual(
                MODULE._atomic_json(path, resumed),
                "verified_existing_lifecycle_equivalent",
            )
            changed_science = dict(resumed, count=3)
            with self.assertRaises(MODULE.ExtractionContractError):
                MODULE._atomic_json(path, changed_science)

    def test_onedrive_owner_only_0700_is_resumable(self):
        arrays = MODULE.build_bundle_arrays(
            [row()], np.zeros((1, 2, 28, 1536), dtype=np.float16))
        with tempfile.TemporaryDirectory() as directory:
            bundle = Path(directory) / "bundle.npz"
            audit = Path(directory) / "audit.json"
            value = {"status": "complete"}
            MODULE._atomic_npz(bundle, **arrays)
            MODULE._atomic_json(audit, value)
            bundle.chmod(0o700)
            audit.chmod(0o700)
            self.assertEqual(MODULE._atomic_npz(bundle, **arrays), "verified_existing")
            self.assertEqual(MODULE._atomic_json(audit, value), "verified_existing")
            bundle.chmod(0o770)
            with self.assertRaises(MODULE.ExtractionContractError):
                MODULE._atomic_npz(bundle, **arrays)


if __name__ == "__main__":
    unittest.main()
