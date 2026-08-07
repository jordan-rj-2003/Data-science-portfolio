"""Credibility axis and projection, spec 001 WHAT §6.

Axis word lists and construction method are reused exactly from
notebooks/MSC PROJECT.ipynb (cell 20) — the 21-vs-22 word version, not
the smaller 4-vs-4 version described in Lit Review §2.2. Confirmed
2026-07-18: the smaller version was a proof-of-concept step validating
the method; the larger version is the real vector used for all
projection work. See spec 001 WHAT §6 and the agent journal entry
"Axis discrepancy resolved before end of session" for the full reasoning.

Construction: mean of each word's unit-normalized GloVe vector, per
group, then credible-group mean minus non-credible-group mean.
"""

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

CREDIBLE_WORDS = [
    "honest",
    "accurate",
    "impartial",
    "unbiased",
    "truthful",
    "true",
    "reliable",
    "objective",
    "credible",
    "trustworthy",
    "transparent",
    "consistent",
    "fair",
    "truth",
    "straightforward",
    "thorough",
    "realistic",
    "facts",
    "reasonable",
    "correct",
    "careful",
]

NON_CREDIBLE_WORDS = [
    "inaccurate",
    "untrue",
    "biased",
    "misleading",
    "dishonest",
    "erroneous",
    "unfounded",
    "unfair",
    "irresponsible",
    "baseless",
    "incorrect",
    "unsubstantiated",
    "unreliable",
    "disingenuous",
    "groundless",
    "hypocritical",
    "inconsistent",
    "unprofessional",
    "unethical",
    "flawed",
    "unjust",
    "untruthful",
]


def _normalized_mean(words, model):
    vectors = [model[w] / np.linalg.norm(model[w]) for w in words]
    return np.mean(vectors, axis=0)


def build_axis(model):
    """Returns the 300-d axis vector: mean(credible) - mean(non_credible),
    each word normalized to unit length before averaging.
    """
    credible = _normalized_mean(CREDIBLE_WORDS, model)
    non_credible = _normalized_mean(NON_CREDIBLE_WORDS, model)
    return credible - non_credible


SMALL_CREDIBLE_WORDS = ["honest", "true", "accurate", "impartial"]
SMALL_NON_CREDIBLE_WORDS = ["dishonest", "untrue", "inaccurate", "biased"]


def build_small_axis(model):
    """Returns the 300-d proof-of-concept axis from Lit Review §2.2:
    mean(honest, true, accurate, impartial) - mean(dishonest, untrue,
    inaccurate, biased). Same normalize-then-average construction as
    build_axis, just the smaller 4-vs-4 word set."""
    credible = _normalized_mean(SMALL_CREDIBLE_WORDS, model)
    non_credible = _normalized_mean(SMALL_NON_CREDIBLE_WORDS, model)
    return credible - non_credible


BALANCE_WORDS = [
    "balanced",
    "measured",
    "proportionate",
    "restrained",
    "even-handed",
    "moderate",
    "calm",
]

UNBALANCE_WORDS = [
    "unbalanced",
    "exaggerated",
    "disproportionate",
    "sensational",
    "one-sided",
    "extreme",
    "dramatic",
]


def build_balance_axis(model):
    """Returns the 300-d balance/one-sidedness axis vector: mean(balance)
    - mean(unbalance), each word normalized to unit length before
    averaging. Same normalize-then-average construction as build_axis.

    Built 2026-07-25 to test whether the credibility axis's honest/true/
    impartial-vs-dishonest/untrue/biased wording conflates two different
    constructs (factual-accuracy/honesty language and impartiality/
    balance language) — this axis isolates the balance dimension alone,
    via 7 hand-reviewed antonym pairs (BALANCE_WORDS[i] paired with
    UNBALANCE_WORDS[i]). Three candidate pairs were reviewed and cut
    (tempered/overblown, neutral/partisan); one (nuanced/simplistic) has
    an unresolved review status and is not included — see journal
    2026-07-25 and spec 010.

    Mathematically identical to Kozlowski et al.'s paired-antonym-
    difference method (mean of each pair's own (a-b) vector) for this
    word list specifically, since the two groups are equal-sized and
    matched in order — confirmed directly, not assumed, before relying on
    either framing.
    """
    balance = _normalized_mean(BALANCE_WORDS, model)
    unbalance = _normalized_mean(UNBALANCE_WORDS, model)
    return balance - unbalance


def project(vectors, axis):
    """vectors: {"A{n}Z{z}": np.ndarray} document vectors.
    axis: the 300-d axis vector.
    Returns {"A{n}Z{z}": float} cosine similarity scores.
    """
    axis_2d = axis.reshape(1, -1)
    scores = {}
    for piece_id, vec in vectors.items():
        scores[piece_id] = float(cosine_similarity(axis_2d, vec.reshape(1, -1))[0][0])
    return scores
