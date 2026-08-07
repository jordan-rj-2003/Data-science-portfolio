"""Axis-similarity weighting, spec 003 Phase 1, and the TF-IDF/cosine
hybrid, spec 004.

Phase 1 weights each surviving token by the absolute value of its own
GloVe vector's cosine similarity to the credibility axis, instead of by
TF-IDF. No document-frequency/IDF concept and no zone-type grouping —
this weight depends only on the word itself and the fixed axis vector,
which is why it lives in its own module rather than src/tfidf.py.

Deliberately no TF (repetition-count) factor in Phase 1: weight is
computed once per unique surviving token, independent of how many times
it occurs in the piece (spec 003 Resolved Decisions — Phase 1 tests
axis-relevance alone, not frequency-and-relevance).

Spec 004 combines both: plain TF-IDF (corpus-relative rarity), modulated
multiplicatively by axis-relevance.
"""

from sklearn.metrics.pairwise import cosine_similarity

from src.tfidf import compute_weights_plain


def _cosine_similarity_to_axis(term, model, axis_2d):
    return cosine_similarity(axis_2d, model[term].reshape(1, -1))[0][0]


def compute_weights_axis_similarity(pieces, model, axis):
    """pieces: {"A{n}Z{z}": [tokens]} -> {"A{n}Z{z}": {term: weight}}.

    weight(t) = abs(cosine_similarity(model[t], axis)). Tokens not in the
    GloVe vocabulary are skipped when building the weight dict (mirrors
    compress_piece's own OOV handling, rather than deferring the lookup
    error to compression time).
    """
    axis_2d = axis.reshape(1, -1)
    weights = {}
    for piece_id, tokens in pieces.items():
        piece_weights = {}
        for term in set(tokens):
            if term not in model:
                continue
            piece_weights[term] = abs(_cosine_similarity_to_axis(term, model, axis_2d))
        weights[piece_id] = piece_weights
    return weights


def compute_weights_hybrid_tfidf_cosine(pieces, model, axis):
    """pieces: {"A{n}Z{z}": [tokens]} -> {"A{n}Z{z}": {term: weight}}.

    weight(t, piece) = tfidf_weight(t, piece) * (1 + abs(cosine_similarity(t, axis))).
    tfidf_weight is plain TF-IDF (compute_weights_plain — same formula as
    the spaCy-baseline variant: no continuity correction, no high-TF
    cap, grouped by zone-type). The modifier ranges [1, 2]: an
    axis-irrelevant word keeps ~its plain TF-IDF weight, a strongly
    axis-relevant word (either pole) gets up to 2x. Absolute value, not
    signed — resolved 2026-07-19: a word strongly aligned with the
    non-credible pole is genuinely diagnostic and must not have its
    contribution suppressed; the word's own GloVe vector (via
    compress_piece) already carries the correct direction into the
    average, so the weight's job is relevance-magnitude only, same
    principle as Phase 1.

    Terms with no GloVe vector get no modifier applied (their plain
    TF-IDF weight passes through unmodified) rather than being dropped —
    compress_piece already skips OOV terms during compression regardless,
    so there's no reason to lose the plain-TF-IDF weight information here.
    """
    tfidf_weights = compute_weights_plain(pieces)
    axis_2d = axis.reshape(1, -1)
    weights = {}
    for piece_id, term_weights in tfidf_weights.items():
        piece_weights = {}
        for term, tfidf_weight in term_weights.items():
            if term in model:
                modifier = 1 + abs(_cosine_similarity_to_axis(term, model, axis_2d))
            else:
                modifier = 1
            piece_weights[term] = tfidf_weight * modifier
        weights[piece_id] = piece_weights
    return weights


def compute_weights_hybrid_product(pieces, model, axis):
    """pieces: {"A{n}Z{z}": [tokens]} -> {"A{n}Z{z}": {term: weight}}.

    weight(t, piece) = tfidf_weight(t, piece) * abs(cosine_similarity(t, axis)).
    Unlike compute_weights_hybrid_tfidf_cosine's (1 + abs(cosine)) modifier
    (floor of x1, only ever boosts), this has no floor: an axis-irrelevant
    word (cosine near 0) gets its weight crushed toward zero regardless of
    how rare it is, rather than merely failing to get a bonus. Resolved
    2026-07-19 (student): TF-IDF was weighting axis-irrelevant tokens too
    highly; this gives topic-relevance real (suppressing) influence rather
    than a modest nudge.

    Terms with no GloVe vector are dropped entirely (unlike the
    (1 + cosine) variant, which passed the plain TF-IDF weight through
    unmodified) — with no floor, there's no defensible default modifier
    for a term whose axis-relevance can't be measured at all, and
    compress_piece would skip it during compression regardless.
    """
    tfidf_weights = compute_weights_plain(pieces)
    axis_2d = axis.reshape(1, -1)
    weights = {}
    for piece_id, term_weights in tfidf_weights.items():
        piece_weights = {}
        for term, tfidf_weight in term_weights.items():
            if term not in model:
                continue
            similarity = abs(_cosine_similarity_to_axis(term, model, axis_2d))
            piece_weights[term] = tfidf_weight * similarity
        weights[piece_id] = piece_weights
    return weights


def compute_weights_threshold_cosine(pieces, model, axis, pos_threshold, neg_threshold):
    """pieces: {"A{n}Z{z}": [tokens]} -> {"A{n}Z{z}": {term: weight}}.

    Hard-threshold alternative to the continuous cosine modifiers above:
    weight(t, piece) = tfidf_weight(t, piece) if
    cosine_similarity(t, axis) > pos_threshold or
    cosine_similarity(t, axis) < -neg_threshold, else the term is dropped
    entirely (not merely down-weighted). A term's TF-IDF weight passes
    through completely unmodified if it clears its pole's threshold —
    unlike compute_weights_hybrid_product, relevance is a binary
    include/exclude gate here, not a continuous multiplier.

    pos_threshold and neg_threshold are independent (not a single
    symmetric |cosine| cutoff): diagnostic checks this session found the
    non-credible pole is structurally sparser in GloVe's embedding space
    than the credible pole (far fewer words sit strongly negative-similar
    to this axis at all, regardless of document content), so a single
    symmetric threshold systematically starves the negative pole long
    before the positive pole is affected. A looser neg_threshold and
    stricter pos_threshold compensate for that asymmetry rather than
    applying one cutoff to both sides.

    Terms with no GloVe vector are dropped (their axis-relevance can't be
    measured), matching compute_weights_hybrid_product.
    """
    tfidf_weights = compute_weights_plain(pieces)
    axis_2d = axis.reshape(1, -1)
    weights = {}
    for piece_id, term_weights in tfidf_weights.items():
        piece_weights = {}
        for term, tfidf_weight in term_weights.items():
            if term not in model:
                continue
            similarity = _cosine_similarity_to_axis(term, model, axis_2d)
            if similarity > pos_threshold or similarity < -neg_threshold:
                piece_weights[term] = tfidf_weight
        weights[piece_id] = piece_weights
    return weights
