"""Small known-answer checks for the separate artifact-only auditor."""
import importlib.util
from pathlib import Path

import numpy as np
import pytest

SPEC = importlib.util.spec_from_file_location(
    "independent_v4_auditor", Path(__file__).resolve().parents[1] / "scripts/audit_evidence_confidence_v4.py")
AUDITOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDITOR)


def test_ordering_ties_and_equal_source_bootstrap():
    np.testing.assert_array_equal(AUDITOR.ordering([2., -2., 0.]), [1., 0., .5])
    result = AUDITOR.grouped_metric([1., 1., 0.], ["a", "a", "b"], 2000, 271828)
    assert result["accuracy"] == .5
    assert result["n_sources"] == 2 and result["n_pairs"] == 3
    assert result["bootstrap_95"] == {"lower": 0., "upper": 1.}


def test_mention_parser_and_strict_value_have_transparent_difference():
    choices = {"A": "4712", "B": "8635"}
    assert AUDITOR.parse("The value is 4712.", choices) == "A"
    assert AUDITOR.strict_choice("The value is 4712.", choices) == "other"
    assert AUDITOR.strict_choice(" 4712. ", choices) == "A"
    # The audit must expose this limitation rather than treating mentions as
    # validated affirmation of a supplied answer.
    assert AUDITOR.parse("It is not 4712.", choices) == "A"
    assert AUDITOR.strict_choice("It is not 4712.", choices) == "other"
    assert AUDITOR.parse("unknown", choices) == "unknown"
    assert AUDITOR.parse("4712 or 8635", choices) == "other"


def test_centered_correlation_resamples_sources_and_handles_degeneracy():
    x = np.array([1., 2., 11., 12., 3., 4., 13., 14.])
    keys = np.array(["A", "A", "B", "B", "A", "A", "B", "B"])
    groups = np.array(["a", "b", "a", "b", "c", "d", "c", "d"])
    centered = AUDITOR.center(x, keys)
    for key in set(keys):
        assert centered[keys == key].mean() == 0
    result = AUDITOR.correlation(x, x * 2, groups, 80, 271828, keys)
    assert result["spearman"] == 1
    assert result["bootstrap_95"]["lower"] > .999999
    assert result["n_sources"] == 4 and result["requested_bootstrap_draws"] == 80
    assert AUDITOR.rho(np.zeros(3), np.ones(3)) is None


def test_recursive_numeric_audit_rejects_modified_metric():
    audit = AUDITOR.Audit()
    audit.equal({"accuracy": .75, "values": [1., None]}, {"accuracy": .75, "values": [1., None]}, "fixture")
    assert audit.compared_scalars == 2
    with pytest.raises(AssertionError, match="Numeric result differs"):
        audit.equal({"accuracy": .75}, {"accuracy": .5}, "fixture")
