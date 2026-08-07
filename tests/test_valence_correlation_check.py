"""Tests for src/valence_correlation_check.py."""

import numpy as np

from src.axis import build_balance_axis
from src.valence_correlation_check import pearson_r, pole_counts_and_scores, valence_correlation


def test_pole_counts_and_scores_aligns_by_piece_id_and_splits_poles(glove_model):
    axis = build_balance_axis(glove_model)
    # "shameful" is strongly negative (unbalanced), "anchored" strongly
    # positive (balanced) on the balance axis -- same fixture as
    # tests/test_token_pole_diagnostic.py.
    weights = {
        "A1Z4": {"anchored": 1.0, "shameful": 1.0},
        "A2Z4": {"anchored": 1.0},
    }
    scores = {"A1Z4": 0.5, "A2Z4": -0.2}
    n_positive, n_negative, score_values = pole_counts_and_scores(glove_model, axis, weights, scores)
    assert n_positive == [1, 1]
    assert n_negative == [1, 0]
    assert score_values == [0.5, -0.2]


def test_pole_counts_and_scores_skips_pieces_missing_a_score(glove_model):
    axis = build_balance_axis(glove_model)
    weights = {"A1Z4": {"anchored": 1.0}, "A2Z4": {"shameful": 1.0}}
    scores = {"A1Z4": 0.5}
    n_positive, n_negative, score_values = pole_counts_and_scores(glove_model, axis, weights, scores)
    assert n_positive == [1]
    assert n_negative == [0]
    assert score_values == [0.5]


def test_pearson_r_perfect_positive_correlation():
    assert np.isclose(pearson_r([1, 2, 3, 4], [1, 2, 3, 4]), 1.0)


def test_pearson_r_perfect_negative_correlation():
    assert np.isclose(pearson_r([1, 2, 3, 4], [4, 3, 2, 1]), -1.0)


def test_valence_correlation_diff_is_r_positive_minus_r_negative():
    # n_positive rises with score (r=+1), n_negative falls with score (r=-1)
    # -- diff should be +1 - (-1) = +2, the maximum possible asymmetry.
    n_positive = [1, 2, 3, 4]
    n_negative = [4, 3, 2, 1]
    score_values = [1, 2, 3, 4]
    r_pos, r_neg, diff = valence_correlation(n_positive, n_negative, score_values)
    assert np.isclose(r_pos, 1.0)
    assert np.isclose(r_neg, -1.0)
    assert np.isclose(diff, 2.0)


def test_valence_correlation_zero_diff_when_poles_behave_identically():
    n_positive = [1, 2, 3, 4]
    n_negative = [1, 2, 3, 4]
    score_values = [1, 2, 3, 4]
    r_pos, r_neg, diff = valence_correlation(n_positive, n_negative, score_values)
    assert np.isclose(diff, 0.0)
