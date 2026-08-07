"""Document compression spot checks, spec 001 task 10.

Uses a small fake GloVe-like model (dict-backed, supports `in` and `[]`)
so the weighted-average arithmetic and edge cases can be checked exactly
by hand, without paying for the real 300-d model load.
"""

import numpy as np
import pytest

from src.compression import EmptyVectorError, compress_corpus, compress_piece


class FakeModel:
    def __init__(self, vectors):
        self._vectors = vectors

    def __contains__(self, term):
        return term in self._vectors

    def __getitem__(self, term):
        return self._vectors[term]


@pytest.fixture
def fake_model():
    return FakeModel(
        {
            "good": np.array([3.0, 4.0]),   # norm 5 -> unit [0.6, 0.8]
            "bad": np.array([0.0, 5.0]),    # norm 5 -> unit [0.0, 1.0]
        }
    )


def test_normal_path_matches_hand_computed_weighted_average(fake_model):
    term_weights = {"good": 2.0, "bad": 1.0}
    result = compress_piece(term_weights, fake_model)
    expected = (2.0 * np.array([0.6, 0.8]) + 1.0 * np.array([0.0, 1.0])) / 3.0
    assert np.allclose(result, expected)


def test_out_of_vocabulary_terms_are_skipped_not_errored(fake_model):
    """A term with no GloVe vector contributes nothing to the average —
    this must not raise, and must not affect the result versus the same
    piece without the OOV term at all."""
    with_oov = compress_piece({"good": 1.0, "nonexistent_oov_term": 5.0}, fake_model)
    without_oov = compress_piece({"good": 1.0}, fake_model)
    assert np.allclose(with_oov, without_oov)


def test_all_terms_out_of_vocabulary_raises_empty_vector_error(fake_model):
    with pytest.raises(EmptyVectorError):
        compress_piece({"nonexistent_a": 1.0, "nonexistent_b": 2.0}, fake_model)


def test_all_zero_weights_raises_empty_vector_error(fake_model):
    """Every surviving token is in-vocabulary but has zero TF-IDF weight
    (e.g. every token appeared in every document of its zone-type corpus
    and was capped) — the documented zero-total-weight edge case."""
    with pytest.raises(EmptyVectorError):
        compress_piece({"good": 0.0, "bad": 0.0}, fake_model)


def test_empty_term_weights_raises_empty_vector_error(fake_model):
    with pytest.raises(EmptyVectorError):
        compress_piece({}, fake_model)


def test_compress_corpus_returns_one_vector_per_piece(fake_model):
    weights = {"A1Z1": {"good": 1.0}, "A1Z2": {"bad": 1.0}}
    vectors = compress_corpus(weights, fake_model)
    assert set(vectors) == {"A1Z1", "A1Z2"}
    assert vectors["A1Z1"].shape == (2,)
