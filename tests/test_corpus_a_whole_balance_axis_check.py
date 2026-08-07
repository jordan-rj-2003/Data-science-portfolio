"""Tests for src/corpus_a_whole_balance_axis_check.py, spec 010 addendum."""

import numpy as np

from src.axis import build_balance_axis
from src.corpus_a_whole_balance_axis_check import _project_weights
from src.glove import get_model


def test_project_weights_returns_scores_for_every_nonempty_piece(glove_model):
    axis = build_balance_axis(glove_model)
    weights = {
        "A1Z4": {"balanced": 1.0, "moderate": 1.0},
        "A2Z4": {"sensational": 1.0},
    }
    scores, empty = _project_weights(weights, glove_model, axis)
    assert set(scores.keys()) == {"A1Z4", "A2Z4"}
    assert empty == []


def test_project_weights_flags_empty_pieces():
    model = get_model()
    axis = build_balance_axis(model)
    weights = {"A1Z4": {}}
    scores, empty = _project_weights(weights, model, axis)
    assert empty == ["A1Z4"]
    assert scores == {}


def test_project_weights_scores_are_bounded_cosine_similarity(glove_model):
    axis = build_balance_axis(glove_model)
    weights = {"A1Z4": {"calm": 1.0, "measured": 1.0}}
    scores, _ = _project_weights(weights, glove_model, axis)
    assert -1.0 <= scores["A1Z4"] <= 1.0
