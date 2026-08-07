"""Small (4-vs-4) proof-of-concept axis, Lit Review §2.2. Uses the real
GloVe model (session-scoped fixture, tests/conftest.py) since the axis
word lists are fixed real words, not synthetic fakes.
"""

import numpy as np

from src.axis import BALANCE_WORDS, UNBALANCE_WORDS, build_axis, build_balance_axis, build_small_axis


def test_small_axis_is_a_300d_vector(glove_model):
    axis = build_small_axis(glove_model)
    assert axis.shape == (300,)


def test_small_axis_differs_from_large_axis(glove_model):
    """Different word lists (4-vs-4 vs. 21-vs-22) must produce a
    different vector, not coincidentally the same direction."""
    small = build_small_axis(glove_model)
    large = build_axis(glove_model)
    assert not np.allclose(small, large)


def test_small_axis_is_deterministic(glove_model):
    assert np.array_equal(build_small_axis(glove_model), build_small_axis(glove_model))


# --- balance/one-sidedness axis, 2026-07-25 pivot ---


def test_balance_axis_is_a_300d_vector(glove_model):
    axis = build_balance_axis(glove_model)
    assert axis.shape == (300,)


def test_balance_axis_differs_from_credibility_axis(glove_model):
    balance = build_balance_axis(glove_model)
    credibility = build_axis(glove_model)
    assert not np.allclose(balance, credibility)


def test_balance_axis_is_deterministic(glove_model):
    assert np.array_equal(build_balance_axis(glove_model), build_balance_axis(glove_model))


def test_balance_word_pairs_are_matched_one_to_one(glove_model):
    """BALANCE_WORDS[i] must be intended to pair with UNBALANCE_WORDS[i]
    -- same length is a necessary (not sufficient) check that the lists
    stayed matched if either is ever edited."""
    assert len(BALANCE_WORDS) == len(UNBALANCE_WORDS) == 7


def test_balance_axis_equals_paired_antonym_difference_method(glove_model):
    """Confirms directly (not just asserts) that build_balance_axis's
    grouped-mean-difference construction is mathematically identical to
    Kozlowski et al.'s paired-antonym-difference method (mean of each
    pair's own (a-b) vector) for this matched, equal-sized word list."""
    grouped = build_balance_axis(glove_model)

    def unit(v):
        return v / np.linalg.norm(v)

    diffs = [unit(glove_model[a]) - unit(glove_model[b]) for a, b in zip(BALANCE_WORDS, UNBALANCE_WORDS)]
    paired = np.mean(diffs, axis=0)
    assert np.allclose(grouped, paired)
