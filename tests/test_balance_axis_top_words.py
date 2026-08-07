"""Tests for src/balance_axis_top_words.py, spec 010 Addendum."""

import numpy as np
import pandas as pd

from src.axis import build_balance_axis
from src.balance_axis_top_words import nearest_top_word_win_counts, top_words_on_axis
from src.threshold_derivation import build_reference_vocab


def test_top_words_returns_requested_count(glove_model):
    axis = build_balance_axis(glove_model)
    vocab = build_reference_vocab(glove_model, vocab_size=2000)
    top_positive, top_negative = top_words_on_axis(glove_model, axis, vocab, n=20)
    assert len(top_positive) == 20
    assert len(top_negative) == 20


def test_top_positive_words_score_higher_than_top_negative(glove_model):
    axis = build_balance_axis(glove_model)
    vocab = build_reference_vocab(glove_model, vocab_size=2000)
    top_positive, top_negative = top_words_on_axis(glove_model, axis, vocab, n=20)
    min_positive_score = min(score for _, score in top_positive)
    max_negative_score = max(score for _, score in top_negative)
    assert min_positive_score > max_negative_score


def test_top_positive_words_sorted_descending(glove_model):
    axis = build_balance_axis(glove_model)
    vocab = build_reference_vocab(glove_model, vocab_size=2000)
    top_positive, _ = top_words_on_axis(glove_model, axis, vocab, n=20)
    scores = [score for _, score in top_positive]
    assert scores == sorted(scores, reverse=True)


def test_top_negative_words_sorted_ascending(glove_model):
    axis = build_balance_axis(glove_model)
    vocab = build_reference_vocab(glove_model, vocab_size=2000)
    _, top_negative = top_words_on_axis(glove_model, axis, vocab, n=20)
    scores = [score for _, score in top_negative]
    assert scores == sorted(scores)


def test_win_counts_returns_one_row_per_word(glove_model):
    vocab = build_reference_vocab(glove_model, vocab_size=2000)
    words = ["true", "balanced", "consistent"]
    df = nearest_top_word_win_counts(glove_model, words, vocab, sample_size=200)
    assert set(df["word"]) == set(words)
    assert len(df) == len(words)


def test_win_counts_sum_to_pool_size(glove_model):
    vocab = build_reference_vocab(glove_model, vocab_size=2000)
    words = ["true", "balanced", "consistent"]
    df = nearest_top_word_win_counts(glove_model, words, vocab, sample_size=200)
    assert df["win_count"].sum() == 200


def test_win_counts_is_deterministic(glove_model):
    vocab = build_reference_vocab(glove_model, vocab_size=2000)
    words = ["true", "balanced", "consistent"]
    df1 = nearest_top_word_win_counts(glove_model, words, vocab, sample_size=200, seed=42)
    df2 = nearest_top_word_win_counts(glove_model, words, vocab, sample_size=200, seed=42)
    pd.testing.assert_frame_equal(df1.reset_index(drop=True), df2.reset_index(drop=True))


def test_win_counts_sorted_descending(glove_model):
    vocab = build_reference_vocab(glove_model, vocab_size=2000)
    words = ["true", "balanced", "consistent", "elephant", "photosynthesis"]
    df = nearest_top_word_win_counts(glove_model, words, vocab, sample_size=200)
    assert list(df["win_count"]) == sorted(df["win_count"], reverse=True)


def test_top_words_never_appear_in_their_own_matching_pool(glove_model):
    """A word can't win a trivial self-match against itself."""
    vocab = build_reference_vocab(glove_model, vocab_size=2000)
    words = ["true", "balanced", "consistent"]
    df = nearest_top_word_win_counts(glove_model, words, vocab, sample_size=None)
    assert df["win_count"].sum() == len([w for w in vocab if w not in words])
