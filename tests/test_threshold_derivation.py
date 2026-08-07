"""Confirms the saved threshold-derivation procedure reproduces the
documented constants (spec 006) — the whole point of saving this file
was to make the derivation itself reproducible from the repo alone,
not just its output, so this test is the guarantee that stays true."""

import pytest

from src.axis import build_axis
from src.threshold_derivation import derive_thresholds


def test_derivation_reproduces_documented_constants(glove_model):
    axis = build_axis(glove_model)
    pos_threshold, neg_threshold, _ = derive_thresholds(glove_model, axis)
    assert pos_threshold == pytest.approx(0.194, abs=0.001)
    assert neg_threshold == pytest.approx(0.096, abs=0.001)


def test_derivation_is_deterministic_given_same_seed(glove_model):
    axis = build_axis(glove_model)
    result_a = derive_thresholds(glove_model, axis, seed=42)
    result_b = derive_thresholds(glove_model, axis, seed=42)
    assert result_a[0] == result_b[0]
    assert result_a[1] == result_b[1]


def test_derivation_differs_with_a_different_seed(glove_model):
    """Not a bug -- a different seed samples different words, so a
    different (but similarly-sized, per the stability check) threshold
    is expected, not an error."""
    axis = build_axis(glove_model)
    result_42 = derive_thresholds(glove_model, axis, seed=42)
    result_7 = derive_thresholds(glove_model, axis, seed=7)
    assert result_42[:2] != result_7[:2]
