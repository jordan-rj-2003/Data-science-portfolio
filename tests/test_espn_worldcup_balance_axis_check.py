"""Tests for src/espn_worldcup_balance_axis_check.py, spec 010 task 2/4."""

import numpy as np

from src.axis import build_balance_axis
from src.espn_worldcup_balance_axis_check import (
    compute_weights_plain_flat,
    diagnose_threshold_degeneracy,
)


def test_compute_weights_plain_flat_matches_tf_times_plain_idf():
    pieces = {
        "E1": ["ball", "ball", "goal"],
        "E2": ["ball", "referee"],
    }
    weights = compute_weights_plain_flat(pieces)
    # "ball" appears in both docs (df=2, n=2) -> idf = ln(2/2) = 0
    assert weights["E1"]["ball"] == 0.0
    assert weights["E2"]["ball"] == 0.0
    # "goal" appears in one doc only (df=1, n=2) -> idf = ln(2/1) = ln(2)
    assert weights["E1"]["goal"] == 1 * np.log(2)
    assert weights["E2"]["referee"] == 1 * np.log(2)


def test_compute_weights_plain_flat_does_not_group_by_zone():
    """Flat "E{n}" piece IDs have no "Z" suffix -- must not crash the way
    compute_weights_plain's group_by_zone() would."""
    pieces = {"E1": ["word"], "E2": ["other"]}
    weights = compute_weights_plain_flat(pieces)
    assert set(weights.keys()) == {"E1", "E2"}


def test_diagnose_threshold_degeneracy_flags_zero_survivor_pieces(glove_model):
    axis = build_balance_axis(glove_model)
    # A very strict pair (thresholds near the axis's own max cosine range)
    # should push every piece toward zero survivors on both poles.
    pieces = {"E1": ["ball", "goal", "referee"]}
    zero_pos, zero_neg, zero_both = diagnose_threshold_degeneracy(
        pieces, glove_model, axis, pos_threshold=0.999, neg_threshold=0.999
    )
    assert zero_pos == ["E1"]
    assert zero_neg == ["E1"]
    assert zero_both == ["E1"]


def test_diagnose_threshold_degeneracy_permissive_thresholds_have_survivors(glove_model):
    axis = build_balance_axis(glove_model)
    pieces = {"E1": ["balanced", "moderate", "calm"]}
    zero_pos, zero_neg, zero_both = diagnose_threshold_degeneracy(
        pieces, glove_model, axis, pos_threshold=0.0, neg_threshold=0.0
    )
    assert zero_both == []
