"""Axis-similarity weighting ablation, spec 003 Phase 1, and the
TF-IDF/cosine hybrid, spec 004.

Runs the axis-similarity-weighted variant (weight =
abs(cosine_similarity(word, axis)), no TF, no IDF) and the hybrid variant
(weight = plain_tfidf * (1 + abs(cosine_similarity(word, axis)))) through
the same spaCy-stopword preprocessing as the naive baseline (spec 002),
and produces comparison tables, top-token tables, word+document axis
charts, and factual (no-conclusions) summary reports.
"""

from src.axis import build_axis, project
from src.axis_weighting import (
    compute_weights_axis_similarity,
    compute_weights_hybrid_product,
    compute_weights_hybrid_tfidf_cosine,
)
from src.compression import compress_corpus
from src.glove import get_model
from src.naive_baseline import (
    build_variant_comparison_chart,
    run_baseline,
    spacy_stopword_set,
    top_token_per_piece,
    write_top_token_table,
)
from src.preprocessing import clean_corpus_stopword_baseline
from src.report import run_pipeline, write_comparison
from src.segmentation import segment_corpus


def run_axis_similarity_variant(raw_dir="data/raw", n_articles=11):
    """Returns (scores, weights) for the axis-similarity-weighted variant."""
    article_ids = [f"A{i}" for i in range(1, n_articles + 1)]
    raw_pieces = segment_corpus(raw_dir, article_ids)
    clean_pieces = clean_corpus_stopword_baseline(raw_pieces, spacy_stopword_set())
    model = get_model()
    axis = build_axis(model)
    weights = compute_weights_axis_similarity(clean_pieces, model, axis)
    vectors = compress_corpus(weights, model)
    scores = project(vectors, axis)
    return scores, weights


def run_hybrid_variant(raw_dir="data/raw", n_articles=11):
    """Returns (scores, weights) for the TF-IDF x axis-similarity hybrid."""
    article_ids = [f"A{i}" for i in range(1, n_articles + 1)]
    raw_pieces = segment_corpus(raw_dir, article_ids)
    clean_pieces = clean_corpus_stopword_baseline(raw_pieces, spacy_stopword_set())
    model = get_model()
    axis = build_axis(model)
    weights = compute_weights_hybrid_tfidf_cosine(clean_pieces, model, axis)
    vectors = compress_corpus(weights, model)
    scores = project(vectors, axis)
    return scores, weights


def run_product_hybrid_variant(raw_dir="data/raw", n_articles=11):
    """Returns (scores, weights) for the TF*IDF*abs(cosine) product-form hybrid."""
    article_ids = [f"A{i}" for i in range(1, n_articles + 1)]
    raw_pieces = segment_corpus(raw_dir, article_ids)
    clean_pieces = clean_corpus_stopword_baseline(raw_pieces, spacy_stopword_set())
    model = get_model()
    axis = build_axis(model)
    weights = compute_weights_hybrid_product(clean_pieces, model, axis)
    vectors = compress_corpus(weights, model)
    scores = project(vectors, axis)
    return scores, weights


def main():
    production_scores = run_pipeline(weighting="tfidf", pos_filter=True)
    spacy_scores, _spacy_weights = run_baseline(spacy_stopword_set())
    axis_sim_scores, axis_sim_weights = run_axis_similarity_variant()
    hybrid_scores, hybrid_weights = run_hybrid_variant()
    product_scores, product_weights = run_product_hybrid_variant()

    write_top_token_table(
        top_token_per_piece(axis_sim_weights), "outputs/tables/AXSIM_TOP_TOKENS.csv"
    )
    write_top_token_table(
        top_token_per_piece(hybrid_weights), "outputs/tables/HYBR_TOP_TOKENS.csv"
    )
    write_top_token_table(
        top_token_per_piece(product_weights), "outputs/tables/PRHYB_TOP_TOKENS.csv"
    )

    comparisons = {
        "axis_similarity_vs_spacy": write_comparison(
            axis_sim_scores, spacy_scores, "axis_similarity", "spacy_baseline",
            "outputs/tables/AXSIM_vs_STAN_COMPARISON.csv",
        ),
        "axis_similarity_vs_production": write_comparison(
            axis_sim_scores, production_scores, "axis_similarity", "production",
            "outputs/tables/AXSIM_vs_PROD_COMPARISON.csv",
        ),
        "hybrid_vs_production": write_comparison(
            hybrid_scores, production_scores, "hybrid", "production",
            "outputs/tables/HYBR_vs_PROD_COMPARISON.csv",
        ),
        "hybrid_vs_spacy": write_comparison(
            hybrid_scores, spacy_scores, "hybrid", "spacy_baseline",
            "outputs/tables/HYBR_vs_STAN_COMPARISON.csv",
        ),
        "hybrid_vs_axis_similarity": write_comparison(
            hybrid_scores, axis_sim_scores, "hybrid", "axis_similarity",
            "outputs/tables/HYBR_vs_AXSIM_COMPARISON.csv",
        ),
        "product_vs_spacy": write_comparison(
            product_scores, spacy_scores, "product_hybrid", "spacy_baseline",
            "outputs/tables/PRHYB_vs_STAN_COMPARISON.csv",
        ),
        "product_vs_production": write_comparison(
            product_scores, production_scores, "product_hybrid", "production",
            "outputs/tables/PRHYB_vs_PROD_COMPARISON.csv",
        ),
        "product_vs_axis_similarity": write_comparison(
            product_scores, axis_sim_scores, "product_hybrid", "axis_similarity",
            "outputs/tables/PRHYB_vs_AXSIM_COMPARISON.csv",
        ),
    }

    model = get_model()
    axis = build_axis(model)
    scores_by_variant = {
        "production": production_scores,
        "spacy_baseline": spacy_scores,
        "axis_similarity": axis_sim_scores,
        "hybrid": hybrid_scores,
        "product_hybrid": product_scores,
    }
    for zone_num in [1, 2, 3, 4]:
        out_path = f"outputs/figures/PROD_STAN_AXSIM_HYBR_PRHYB_WORDS_AND_DOCUMENTS_Z{zone_num}.png"
        build_variant_comparison_chart(zone_num, model, axis, scores_by_variant, out_path)
        print(f"Wrote {out_path}")

    print("Wrote 8 comparison tables and 3 top-token tables to outputs/tables/.")
    return product_scores, product_weights, comparisons


if __name__ == "__main__":
    main()
