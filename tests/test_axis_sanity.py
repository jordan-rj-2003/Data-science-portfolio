"""Synthetic sanity check, spec 001 acceptance criteria:

"Pipeline validated against a synthetic sanity check (a clearly
credible-style paragraph and a clearly biased-style paragraph) to confirm
the projection sign matches expectation before trusting it on real
articles."

Uses the real GloVe model (via the session-scoped fixture) and the real
axis — this is the one test in the suite that exercises the full
preprocessing -> weighting -> compression -> projection chain end to end,
deliberately without touching the real 11-article corpus.
"""

from src.axis import build_axis, project
from src.compression import compress_corpus
from src.preprocessing import clean_tokens
from src.tfidf import compute_weights

CREDIBLE_TEXT = (
    "The report was honest, accurate, and fair. It presented the facts "
    "objectively and transparently, giving a truthful and reliable "
    "account with careful, consistent, well-substantiated evidence."
)

BIASED_TEXT = (
    "The dishonest report was misleading and unfair. It gave a biased, "
    "inaccurate account full of baseless claims, unsubstantiated "
    "allegations, and unreliable, unprofessional exaggeration."
)


def test_credible_paragraph_scores_higher_than_biased_paragraph(glove_model):
    pieces = {
        "SYN1Z1": clean_tokens(CREDIBLE_TEXT),
        "SYN2Z1": clean_tokens(BIASED_TEXT),
    }
    weights = compute_weights(pieces)
    vectors = compress_corpus(weights, glove_model)
    axis = build_axis(glove_model)
    scores = project(vectors, axis)

    assert scores["SYN1Z1"] > scores["SYN2Z1"]
    # Not just relative ordering — each should land on the expected side
    # of zero, i.e. the axis direction itself matches intuition.
    assert scores["SYN1Z1"] > 0
    assert scores["SYN2Z1"] < 0
