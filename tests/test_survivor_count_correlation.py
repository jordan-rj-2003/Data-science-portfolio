"""Tests for src/survivor_count_correlation.py."""

import numpy as np

from src.survivor_count_correlation import pearson_r_and_r2, survivor_counts_and_scores


def test_survivor_counts_and_scores_aligns_by_piece_id():
    weights = {"E1": {"a": 1.0, "b": 2.0}, "E2": {"c": 1.0}}
    scores = {"E1": 0.5, "E2": -0.2}
    counts, score_values = survivor_counts_and_scores(weights, scores)
    assert counts == [2, 1]
    assert score_values == [0.5, -0.2]


def test_survivor_counts_and_scores_skips_pieces_missing_a_score():
    weights = {"E1": {"a": 1.0}, "E2": {"b": 1.0}}
    scores = {"E1": 0.5}
    counts, score_values = survivor_counts_and_scores(weights, scores)
    assert counts == [1]
    assert score_values == [0.5]


def test_pearson_r_and_r2_perfect_positive_correlation():
    r, r2 = pearson_r_and_r2([1, 2, 3, 4], [1, 2, 3, 4])
    assert np.isclose(r, 1.0)
    assert np.isclose(r2, 1.0)


def test_pearson_r_and_r2_perfect_negative_correlation():
    r, r2 = pearson_r_and_r2([1, 2, 3, 4], [4, 3, 2, 1])
    assert np.isclose(r, -1.0)
    assert np.isclose(r2, 1.0)


def test_pearson_r_and_r2_no_correlation():
    r, r2 = pearson_r_and_r2([1, 2, 3, 4], [1, 1, 1, 1])
    assert np.isnan(r)  # zero-variance y -- undefined correlation, not zero


def test_r2_is_r_squared():
    r, r2 = pearson_r_and_r2([1, 3, 2, 5, 4], [2, 1, 4, 3, 6])
    assert np.isclose(r2, r ** 2)
