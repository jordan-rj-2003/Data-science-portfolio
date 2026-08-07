"""Derivation of the statistically-grounded threshold-cosine pair
(POS_THRESHOLD_RANDOM_BASELINE / NEG_THRESHOLD_RANDOM_BASELINE in
src/threshold_cosine_ablation.py), spec 006.

This was originally run as one-off inline scripts during a 2026-07-22
session and never saved as an actual file — meaning the specific
constants (0.194/0.096) were persisted, but the procedure that produced
them wasn't reproducible by anyone without that session's exact
in-conversation code. This file is that procedure, saved properly, so
the derivation itself — not just its output — is reproducible from the
repo alone.

Method: the 5th/95th percentile of 1000 random common-English words'
cosine similarity to the large (21-vs-22-word) credibility axis. A
candidate token's cosine similarity outside this range has roughly a
90% chance of not being there by pure chance relative to this reference
population (10% two-tailed noise rate) — see journal 2026-07-22 for the
full reasoning, including the sampling-stability check (30 independent
1000-word draws, percentile stdev ~0.006-0.007) and the acknowledged
open caveat that this reference population is generic English, not
sports-news-domain-matched (see spec 008, option 3).

Reproducibility requires matching ALL of: the GloVe model
(glove-wiki-gigaword-300), the vocabulary slice (top 20000 by frequency
rank, alphabetic, length > 2), the sample size (1000), and the random
seed (42) — matching only the seed with a different vocabulary pool (a
different model, a different frequency cutoff, a different filter) will
produce a different but equally legitimate statistically-grounded
threshold, calibrated against a different reference population. Neither
is "more correct" than the other; they're just not interchangeable
unless the whole procedure matches, not only the seed.
"""

import random

import numpy as np

from src.axis import build_axis
from src.axis_weighting import _cosine_similarity_to_axis
from src.glove import get_model

VOCAB_SIZE = 20000
SAMPLE_SIZE = 1000
SEED = 42


def build_reference_vocab(model, vocab_size=VOCAB_SIZE):
    """The top `vocab_size` most frequent words in the GloVe model,
    filtered to alphabetic words longer than 2 characters — the same
    filter used throughout this session's derivation."""
    return [w for w in model.index_to_key[:vocab_size] if w.isalpha() and len(w) > 2]


def derive_thresholds(model=None, axis=None, seed=SEED, sample_size=SAMPLE_SIZE, vocab_size=VOCAB_SIZE):
    """Returns (pos_threshold, neg_threshold) as the 95th/5th percentile
    of a random sample's cosine similarity to the axis. neg_threshold is
    returned as a positive magnitude (matching how
    compute_weights_threshold_cosine uses it: `similarity < -neg_threshold`)."""
    if model is None:
        model = get_model()
    if axis is None:
        axis = build_axis(model)
    axis_2d = axis.reshape(1, -1)

    vocab = build_reference_vocab(model, vocab_size)
    random.seed(seed)
    sample = random.sample(vocab, sample_size)
    sims = np.array([_cosine_similarity_to_axis(w, model, axis_2d) for w in sample])

    pos_threshold = float(np.percentile(sims, 95))
    neg_threshold = float(-np.percentile(sims, 5))
    return pos_threshold, neg_threshold, sims


def check_sampling_stability(model=None, axis=None, n_draws=30, sample_size=SAMPLE_SIZE, vocab_size=VOCAB_SIZE):
    """Reproduces the stability check from journal 2026-07-22: draws the
    threshold n_draws times with different seeds (0..n_draws-1) and
    reports how much the percentile estimate itself varies."""
    if model is None:
        model = get_model()
    if axis is None:
        axis = build_axis(model)

    pos_vals, neg_vals = [], []
    for seed in range(n_draws):
        pos_t, neg_t, _ = derive_thresholds(model, axis, seed=seed, sample_size=sample_size, vocab_size=vocab_size)
        pos_vals.append(pos_t)
        neg_vals.append(neg_t)
    return np.array(pos_vals), np.array(neg_vals)


def main():
    model = get_model()
    axis = build_axis(model)
    pos_threshold, neg_threshold, sims = derive_thresholds(model, axis)
    print(f"Reference vocabulary: top {VOCAB_SIZE} words, alphabetic, length > 2, sample size {SAMPLE_SIZE}, seed {SEED}")
    print(f"pos_threshold (95th percentile) = {pos_threshold:.4f}")
    print(f"neg_threshold (5th percentile magnitude) = {neg_threshold:.4f}")
    print(f"Reference sample: mean={sims.mean():+.4f}, stdev={sims.std():.4f}")
    print()
    print("These should match POS_THRESHOLD_RANDOM_BASELINE / NEG_THRESHOLD_RANDOM_BASELINE "
          "in src/threshold_cosine_ablation.py (0.194 / 0.096).")


if __name__ == "__main__":
    main()
