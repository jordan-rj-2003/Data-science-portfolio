"""Axis-similarity weighting spot checks, spec 003 task 7 / spec 004 task 3.

Uses a small fake GloVe-like model and a synthetic 2-d axis so the
expected weights can be checked exactly by hand, without paying for the
real 300-d model.
"""

import math

import numpy as np
import pytest

from src.axis_weighting import (
    compute_weights_axis_similarity,
    compute_weights_hybrid_product,
    compute_weights_hybrid_tfidf_cosine,
    compute_weights_threshold_cosine,
)


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
            "credible_word": np.array([1.0, 0.0]),      # cosine sim to axis = +1.0
            "noncredible_word": np.array([-1.0, 0.0]),  # cosine sim to axis = -1.0
            "orthogonal_word": np.array([0.0, 1.0]),    # cosine sim to axis = 0.0
        }
    )


@pytest.fixture
def axis():
    return np.array([1.0, 0.0])


def test_weight_is_absolute_value_not_signed(fake_model, axis):
    """A word aligned with the non-credible pole (cosine similarity -1.0)
    must get a positive weight (1.0), not a negative one — spec 003's
    resolved decision to use abs(cosine_similarity)."""
    pieces = {"A1Z1": ["noncredible_word"]}
    weights = compute_weights_axis_similarity(pieces, fake_model, axis)
    assert weights["A1Z1"]["noncredible_word"] == 1.0


def test_orthogonal_word_gets_near_zero_weight(fake_model, axis):
    pieces = {"A1Z1": ["orthogonal_word"]}
    weights = compute_weights_axis_similarity(pieces, fake_model, axis)
    assert weights["A1Z1"]["orthogonal_word"] == pytest.approx(0.0, abs=1e-9)


def test_out_of_vocabulary_tokens_are_skipped(fake_model, axis):
    pieces = {"A1Z1": ["credible_word", "nonexistent_oov_term"]}
    weights = compute_weights_axis_similarity(pieces, fake_model, axis)
    assert "nonexistent_oov_term" not in weights["A1Z1"]
    assert weights["A1Z1"]["credible_word"] == 1.0


def test_weight_is_independent_of_repetition_count(fake_model, axis):
    """Spec 003 Phase 1: no TF factor — a token appearing once vs. five
    times in a piece must get the identical weight."""
    pieces = {
        "A1Z1": ["credible_word"],
        "A2Z1": ["credible_word"] * 5,
    }
    weights = compute_weights_axis_similarity(pieces, fake_model, axis)
    assert weights["A1Z1"]["credible_word"] == weights["A2Z1"]["credible_word"] == 1.0


# --- spec 004: TF-IDF x axis-similarity hybrid ---


def test_hybrid_modifier_boosts_credible_and_noncredible_words_equally(fake_model, axis):
    """abs(cosine_similarity) means a word aligned with either pole gets
    the identical [1,2] modifier boost — resolved 2026-07-19: suppressing
    non-credible-pole words would remove the pipeline's most diagnostic
    signal for detecting bias-language, so both poles boost equally."""
    pieces = {
        "A1Z1": ["credible_word", "noncredible_word", "orthogonal_word"],
        "A2Z1": ["other_word"],
    }
    weights = compute_weights_hybrid_tfidf_cosine(pieces, fake_model, axis)

    plain_idf = math.log(2 / 1)  # each term in exactly 1 of 2 docs, TF=1
    assert weights["A1Z1"]["credible_word"] == pytest.approx(plain_idf * 2, rel=1e-9)
    assert weights["A1Z1"]["noncredible_word"] == pytest.approx(plain_idf * 2, rel=1e-9)
    assert weights["A1Z1"]["credible_word"] == weights["A1Z1"]["noncredible_word"]


def test_hybrid_modifier_is_one_for_axis_orthogonal_word(fake_model, axis):
    """cosine similarity 0.0 -> modifier (1 + 0) = 1 -> weight equals the
    plain TF-IDF weight unchanged."""
    pieces = {
        "A1Z1": ["credible_word", "noncredible_word", "orthogonal_word"],
        "A2Z1": ["other_word"],
    }
    weights = compute_weights_hybrid_tfidf_cosine(pieces, fake_model, axis)
    plain_idf = math.log(2 / 1)
    assert weights["A1Z1"]["orthogonal_word"] == pytest.approx(plain_idf, rel=1e-9)


def test_hybrid_out_of_vocabulary_term_keeps_unmodified_tfidf_weight(fake_model, axis):
    """A term with no GloVe vector gets modifier=1 (its plain TF-IDF
    weight passes through) rather than being dropped — compress_piece
    will skip it during compression regardless, since it can't look up a
    vector for it either way."""
    pieces = {
        "A1Z1": ["credible_word", "unknown_word"],
        "A2Z1": ["other_word"],
    }
    weights = compute_weights_hybrid_tfidf_cosine(pieces, fake_model, axis)
    plain_idf = math.log(2 / 1)
    assert weights["A1Z1"]["unknown_word"] == pytest.approx(plain_idf, rel=1e-9)


# --- product-form hybrid: weight = TF*IDF*abs(cosine), no floor ---


def test_product_hybrid_crushes_axis_orthogonal_word_toward_zero(fake_model, axis):
    """No floor this time: cosine similarity 0.0 -> weight = tfidf * 0 = 0,
    regardless of how rare the word is — the fix for TF-IDF weighting
    axis-irrelevant tokens too highly (student, 2026-07-19)."""
    pieces = {
        "A1Z1": ["credible_word", "noncredible_word", "orthogonal_word"],
        "A2Z1": ["other_word"],
    }
    weights = compute_weights_hybrid_product(pieces, fake_model, axis)
    assert weights["A1Z1"]["orthogonal_word"] == pytest.approx(0.0, abs=1e-9)


def test_product_hybrid_boosts_credible_and_noncredible_words_equally(fake_model, axis):
    """abs(cosine) means both poles get the full tfidf weight scaled by
    the same relevance magnitude."""
    pieces = {
        "A1Z1": ["credible_word", "noncredible_word", "orthogonal_word"],
        "A2Z1": ["other_word"],
    }
    weights = compute_weights_hybrid_product(pieces, fake_model, axis)
    plain_idf = math.log(2 / 1)
    assert weights["A1Z1"]["credible_word"] == pytest.approx(plain_idf * 1.0, rel=1e-9)
    assert weights["A1Z1"]["noncredible_word"] == pytest.approx(plain_idf * 1.0, rel=1e-9)
    assert weights["A1Z1"]["credible_word"] == weights["A1Z1"]["noncredible_word"]


def test_product_hybrid_drops_out_of_vocabulary_terms_entirely(fake_model, axis):
    """Unlike the (1 + cosine) variant, there's no defensible default
    modifier with no floor, so OOV terms are dropped rather than passed
    through unmodified."""
    pieces = {
        "A1Z1": ["credible_word", "unknown_word"],
        "A2Z1": ["other_word"],
    }
    weights = compute_weights_hybrid_product(pieces, fake_model, axis)
    assert "unknown_word" not in weights["A1Z1"]
    assert "credible_word" in weights["A1Z1"]


# --- thresholded cosine-relevance: hard include/exclude gate, asymmetric thresholds ---


def test_threshold_cosine_keeps_word_clearing_positive_threshold(fake_model, axis):
    """credible_word has cosine similarity 1.0 to the axis, well above a
    pos_threshold of 0.5 -> keeps its full plain-TF-IDF weight."""
    pieces = {
        "A1Z1": ["credible_word", "orthogonal_word"],
        "A2Z1": ["other_word"],
    }
    weights = compute_weights_threshold_cosine(pieces, fake_model, axis, pos_threshold=0.5, neg_threshold=0.5)
    plain_idf = math.log(2 / 1)
    assert weights["A1Z1"]["credible_word"] == pytest.approx(plain_idf, rel=1e-9)


def test_threshold_cosine_keeps_word_clearing_negative_threshold(fake_model, axis):
    """noncredible_word has cosine similarity -1.0 -> kept when its
    magnitude clears neg_threshold, on the same terms as the positive
    pole (independent thresholds, but both can pass)."""
    pieces = {
        "A1Z1": ["noncredible_word", "orthogonal_word"],
        "A2Z1": ["other_word"],
    }
    weights = compute_weights_threshold_cosine(pieces, fake_model, axis, pos_threshold=0.5, neg_threshold=0.5)
    plain_idf = math.log(2 / 1)
    assert weights["A1Z1"]["noncredible_word"] == pytest.approx(plain_idf, rel=1e-9)


def test_threshold_cosine_drops_word_between_thresholds(fake_model, axis):
    """orthogonal_word has cosine similarity 0.0 -> clears neither
    pos_threshold nor neg_threshold -> dropped entirely, not down-weighted."""
    pieces = {
        "A1Z1": ["credible_word", "orthogonal_word"],
        "A2Z1": ["other_word"],
    }
    weights = compute_weights_threshold_cosine(pieces, fake_model, axis, pos_threshold=0.5, neg_threshold=0.5)
    assert "orthogonal_word" not in weights["A1Z1"]


def test_threshold_cosine_supports_asymmetric_thresholds(fake_model, axis):
    """A loose neg_threshold can admit the non-credible pole while a
    stricter pos_threshold simultaneously excludes a weaker positive
    word — the two thresholds are independent, not one symmetric |cosine|
    cutoff (this project's own diagnostic found the non-credible pole
    structurally sparser, motivating exactly this asymmetry)."""
    pieces = {
        "A1Z1": ["noncredible_word", "orthogonal_word"],
        "A2Z1": ["other_word"],
    }
    # neg_threshold=0.5 admits noncredible_word (sim=-1.0); pos_threshold=0.9
    # would exclude a word with sim=0.5 even though 0.5 > the old symmetric cutoff.
    weights = compute_weights_threshold_cosine(pieces, fake_model, axis, pos_threshold=0.9, neg_threshold=0.5)
    assert "noncredible_word" in weights["A1Z1"]
    assert "orthogonal_word" not in weights["A1Z1"]


def test_threshold_cosine_drops_out_of_vocabulary_terms(fake_model, axis):
    pieces = {
        "A1Z1": ["credible_word", "unknown_word"],
        "A2Z1": ["other_word"],
    }
    weights = compute_weights_threshold_cosine(pieces, fake_model, axis, pos_threshold=0.5, neg_threshold=0.5)
    assert "unknown_word" not in weights["A1Z1"]
    assert "credible_word" in weights["A1Z1"]
