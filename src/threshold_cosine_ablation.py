"""Thresholded cosine-relevance ablation: a hard include/exclude gate on
axis-relevance, as a substitute for the continuous cosine-modifier hybrids
in src/axis_weighting.py (compute_weights_hybrid_tfidf_cosine,
compute_weights_hybrid_product). Only tokens whose cosine similarity to
the axis clears a threshold (on either pole) keep their plain TF-IDF
weight; every other token is dropped entirely, rather than down-weighted.

Asymmetric thresholds (pos_threshold=0.25, neg_threshold=0.02): a
diagnostic this session found the non-credible pole is structurally
sparser in GloVe's embedding space than the credible pole (far fewer
words sit strongly negative-similar to the axis at all, regardless of
document content) — a single symmetric |cosine| cutoff starves the
negative pole long before the positive pole is affected (at |cosine|<0.2,
75% of pieces had zero surviving negative-pole tokens). Checked before
picking this pair: pos_threshold=0.25 paired with neg_threshold=0.02 gives
12/44 pieces with zero positive-pole survivors and 2/44 with zero
negative-pole survivors (closest to balanced degeneracy of the thresholds
tested, and no piece loses survivors on both poles at once — 0.30/0.35
each produced one fully-empty piece).
"""

from src.axis import build_axis, project
from src.axis_weighting import compute_weights_threshold_cosine
from src.compression import EmptyVectorError, compress_corpus
from src.glove import get_model
from src.naive_baseline import (
    VARIANT_MARKERS,
    VARIANT_PALETTE,
    build_variant_comparison_chart,
    run_baseline,
    spacy_stopword_set,
    top_token_per_piece,
    write_top_token_table,
)
from src.preprocessing import clean_corpus_stopword_baseline
from src.report import run_pipeline, write_comparison
from src.segmentation import segment_corpus

POS_THRESHOLD = 0.25
NEG_THRESHOLD = 0.02

# Alternative pair, derived from the 5th/95th percentile of a 1000-word
# random common-English-vocabulary sample's cosine similarity to this
# axis (see spec 006 / journal 2026-07-22) — a statistically principled
# "distinguishable from a random word" cutoff, rather than one tuned to
# avoid degenerate (empty) pieces. Diagnosed before running: 0/44 pieces
# empty on both poles, 0/44 empty on the positive pole, but 14/44 empty on
# the negative pole (vs. 2/44 for the tuned pair above) — stricter, at the
# cost of more pieces losing all negative-pole signal.
POS_THRESHOLD_RANDOM_BASELINE = 0.194
NEG_THRESHOLD_RANDOM_BASELINE = 0.096

ARTICLE_IDS = [f"A{i}" for i in range(1, 12)]


def run_threshold_cosine_variant(raw_dir="data/raw", n_articles=11,
                                  pos_threshold=POS_THRESHOLD, neg_threshold=NEG_THRESHOLD):
    """Returns (scores, weights, empty_pieces) for the thresholded-cosine
    variant. empty_pieces lists any piece where every token was dropped
    (no survivors on either pole) — handled explicitly rather than left to
    crash, per this project's established EmptyVectorError convention."""
    article_ids = [f"A{i}" for i in range(1, n_articles + 1)]
    raw_pieces = segment_corpus(raw_dir, article_ids)
    clean_pieces = clean_corpus_stopword_baseline(raw_pieces, spacy_stopword_set())
    model = get_model()
    axis = build_axis(model)
    weights = compute_weights_threshold_cosine(clean_pieces, model, axis, pos_threshold, neg_threshold)

    vectors = {}
    empty_pieces = []
    for piece_id, term_weights in weights.items():
        try:
            vectors[piece_id] = compress_corpus({piece_id: term_weights}, model)[piece_id]
        except EmptyVectorError:
            empty_pieces.append(piece_id)

    scores = project(vectors, axis)
    return scores, weights, empty_pieces


def run_and_report(pos_threshold, neg_threshold, label, production_scores=None, spacy_scores=None):
    """label distinguishes output filenames (e.g. "threshold_cosine" for
    the degeneracy-tuned pair, "threshold_cosine_random_baseline" for the
    5th/95th-percentile-derived pair) so multiple threshold choices can be
    run and compared without overwriting each other's outputs."""
    if production_scores is None:
        production_scores = run_pipeline(weighting="tfidf", pos_filter=True)
    if spacy_scores is None:
        spacy_scores, _ = run_baseline(spacy_stopword_set())

    threshold_scores, threshold_weights, empty_pieces = run_threshold_cosine_variant(
        pos_threshold=pos_threshold, neg_threshold=neg_threshold
    )
    if empty_pieces:
        print(f"WARNING: {len(empty_pieces)} piece(s) had zero survivors on both poles, "
              f"excluded from scoring/comparison: {empty_pieces}")

    label_acronym = {"threshold_cosine": "CTHRT", "threshold_cosine_random_baseline": "CTHRR"}[label]

    write_top_token_table(
        top_token_per_piece(threshold_weights), f"outputs/tables/{label_acronym}_TOP_TOKENS.csv"
    )

    comparisons = {
        f"{label}_vs_production": write_comparison(
            threshold_scores, {k: v for k, v in production_scores.items() if k in threshold_scores},
            label, "production",
            f"outputs/tables/{label_acronym}_vs_PROD_COMPARISON.csv",
        ),
        f"{label}_vs_spacy": write_comparison(
            threshold_scores, {k: v for k, v in spacy_scores.items() if k in threshold_scores},
            label, "spacy_baseline",
            f"outputs/tables/{label_acronym}_vs_STAN_COMPARISON.csv",
        ),
    }

    model = get_model()
    axis = build_axis(model)
    scores_by_variant = {
        "production": production_scores,
        "spacy_baseline": spacy_scores,
        label: threshold_scores,
    }
    VARIANT_PALETTE.setdefault(label, "tab:cyan")
    VARIANT_MARKERS.setdefault(label, "*")
    for zone_num in [1, 2, 3, 4]:
        out_path = f"outputs/figures/PROD_STAN_{label_acronym}_WORDS_AND_DOCUMENTS_Z{zone_num}.png"
        build_variant_comparison_chart(zone_num, model, axis, scores_by_variant, out_path)
        print(f"Wrote {out_path}")

    for name, rows in comparisons.items():
        shifts = [abs(r["rank_shift"]) for r in rows]
        print(f"[{name}] n={len(rows)}, mean absolute rank shift: {sum(shifts)/len(shifts):.2f}")

    print(f"Wrote 2 comparison tables, 1 top-token table, 4 figures for label={label}.")
    return threshold_scores, threshold_weights, empty_pieces, comparisons


def main():
    production_scores = run_pipeline(weighting="tfidf", pos_filter=True)
    spacy_scores, _spacy_weights = run_baseline(spacy_stopword_set())

    run_and_report(POS_THRESHOLD, NEG_THRESHOLD, "threshold_cosine", production_scores, spacy_scores)
    run_and_report(
        POS_THRESHOLD_RANDOM_BASELINE, NEG_THRESHOLD_RANDOM_BASELINE,
        "threshold_cosine_random_baseline", production_scores, spacy_scores,
    )


if __name__ == "__main__":
    main()
