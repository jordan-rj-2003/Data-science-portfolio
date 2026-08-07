"""Document compression per spec 001 WHAT §5.

For each piece: normalize each surviving token's GloVe vector to unit
length, multiply by its TF-IDF weight (src/tfidf.py), sum, divide by the
sum of weights actually used. Tokens with no GloVe vector contribute
nothing — nothing to normalize, not a filtering choice. The zero-total-
weight edge case (every in-vocabulary token in a piece happens to have
zero TF-IDF weight) is handled explicitly rather than left to raise an
unhandled exception.
"""

import numpy as np


class EmptyVectorError(ValueError):
    """Raised when a piece has no in-vocabulary token with nonzero
    weight — nothing to compress."""


def compress_piece(term_weights, model):
    """term_weights: {term: tf_idf_weight} for one piece.
    model: gensim KeyedVectors (GloVe).
    Returns the TF-IDF-weighted average of unit-normalized GloVe vectors.
    """
    numerator = None
    denominator = 0.0
    for term, weight in term_weights.items():
        if term not in model:
            continue
        vec = model[term]
        norm = np.linalg.norm(vec)
        if norm == 0:
            continue  # defensive; GloVe shouldn't produce zero vectors
        unit_vec = vec / norm
        contribution = weight * unit_vec
        numerator = contribution if numerator is None else numerator + contribution
        denominator += weight

    if numerator is None or denominator == 0:
        raise EmptyVectorError(
            "No in-vocabulary token with nonzero weight — cannot compress this piece."
        )
    return numerator / denominator


def compress_corpus(weights, model):
    """weights: {"A{n}Z{z}": {term: tf_idf_weight}} for all pieces.
    Returns {"A{n}Z{z}": np.ndarray} — one 300-d document vector per piece.
    """
    return {
        piece_id: compress_piece(term_weights, model)
        for piece_id, term_weights in weights.items()
    }
