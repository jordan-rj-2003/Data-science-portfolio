"""Naive/standard-NLP baseline ablation, spec 002.

Runs two "textbook" preprocessing/weighting variants (spaCy stopwords and
NLTK stopwords, both paired with a plain/uncorrected TF-IDF formula)
alongside the production pipeline, and produces comparison tables,
key-statistics comparisons, and factual (no-conclusions) summary reports.
"""

import csv
import statistics
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from nltk.corpus import stopwords as nltk_stopwords_corpus

from src.axis import build_axis, project
from src.axis_plot import _article_num, _words_dataframe, add_document, graph
from src.compression import compress_corpus
from src.glove import get_model
from src.preprocessing import clean_corpus_stopword_baseline, get_nlp
from src.report import ZONE_NAMES, run_pipeline, write_comparison
from src.segmentation import segment_corpus
from src.tfidf import compute_weights_plain

ARTICLE_IDS = [f"A{i}" for i in range(1, 12)]


def spacy_stopword_set():
    return {w.lower() for w in get_nlp().Defaults.stop_words}


def nltk_stopword_set():
    return {w.lower() for w in nltk_stopwords_corpus.words("english")}


def run_baseline(stopword_set, raw_dir="data/raw", n_articles=11):
    """Returns (scores, weights) for one naive-baseline variant."""
    article_ids = [f"A{i}" for i in range(1, n_articles + 1)]
    raw_pieces = segment_corpus(raw_dir, article_ids)
    clean_pieces = clean_corpus_stopword_baseline(raw_pieces, stopword_set)
    weights = compute_weights_plain(clean_pieces)
    model = get_model()
    vectors = compress_corpus(weights, model)
    axis = build_axis(model)
    return project(vectors, axis), weights


def top_token_per_piece(weights):
    """weights: {"A{n}Z{z}": {term: weight}} -> [(piece_id, top_term, top_weight)]"""
    rows = []
    for piece_id, piece_weights in weights.items():
        if not piece_weights:
            rows.append((piece_id, None, None))
            continue
        top_term, top_weight = max(piece_weights.items(), key=lambda kv: kv[1])
        rows.append((piece_id, top_term, round(top_weight, 4)))
    return rows


def write_top_token_table(rows, out_path):
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["piece_id", "top_token", "weight"])
        w.writerows(rows)


def _rank_shift_stats(rows, label_a, label_b):
    shifts = [r["rank_shift"] for r in rows]
    abs_shifts = [abs(s) for s in shifts]
    deltas = [r[f"{label_a}_score"] - r[f"{label_b}_score"] for r in rows]
    by_zone = defaultdict(list)
    for r in rows:
        by_zone[r["zone"]].append(r["rank_shift"])
    return {
        "n": len(rows),
        "mean_abs": statistics.mean(abs_shifts),
        "median_abs": statistics.median(abs_shifts),
        "max_abs": max(abs_shifts),
        "unchanged": sum(1 for s in shifts if s == 0),
        "mean_signed": statistics.mean(shifts),
        "stdev_signed": statistics.pstdev(shifts),
        "min_signed": min(shifts),
        "max_signed": max(shifts),
        "mean_delta": statistics.mean(deltas),
        "stdev_delta": statistics.pstdev(deltas),
        "by_zone": {
            zone: {
                "mean_abs": statistics.mean(abs(s) for s in vals),
                "mean_signed": statistics.mean(vals),
            }
            for zone, vals in by_zone.items()
        },
    }


def _token_weight_stats(rows):
    """rows: [(piece_id, top_token, weight)] -> stats by zone and by article."""
    by_zone = defaultdict(list)
    by_article = defaultdict(list)
    for piece_id, _token, weight in rows:
        if weight is None:
            continue
        zone = ZONE_NAMES[int(piece_id.split("Z")[1])]
        article = piece_id.split("Z")[0]
        by_zone[zone].append(weight)
        by_article[article].append(weight)
    return (
        {z: (statistics.mean(v), statistics.pvariance(v)) for z, v in by_zone.items()},
        {a: (statistics.mean(v), statistics.pvariance(v)) for a, v in by_article.items()},
    )


def signed_delta_by_zone_and_article(comparison_rows, label_a, label_b):
    """comparison_rows: rows from write_comparison (piece_id, zone,
    article, {label_a}_score, {label_b}_score, ...). Returns
    (by_zone, by_article) dicts of mean signed (label_a - label_b) score
    delta — not absolute value."""
    by_zone = defaultdict(list)
    by_article = defaultdict(list)
    for r in comparison_rows:
        delta = r[f"{label_a}_score"] - r[f"{label_b}_score"]
        by_zone[r["zone"]].append(delta)
        by_article[r["article"]].append(delta)
    zone_means = {z: statistics.mean(v) for z, v in by_zone.items()}
    article_means = {a: statistics.mean(v) for a, v in by_article.items()}
    return zone_means, article_means


def plot_signed_delta_bar(values_by_key, key_order, title, xlabel, out_path):
    """values_by_key: {key: mean_signed_delta}. key_order: display order."""
    df = pd.DataFrame({xlabel: key_order, "mean_signed_delta": [values_by_key[k] for k in key_order]})
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.barplot(df, x=xlabel, y="mean_signed_delta", ax=ax, color="steelblue")
    ax.set_title(title)
    ax.set_ylabel("Mean signed score delta")
    ax.axhline(0, color="black", linewidth=0.8)
    fig.tight_layout()
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=130)
    plt.close(fig)


VARIANT_PALETTE = {
    "word": "tab:blue",
    "production": "tab:red",
    "spacy_baseline": "tab:green",
    "nltk_baseline": "tab:orange",
    "axis_similarity": "tab:purple",
    "hybrid": "tab:brown",
    "product_hybrid": "tab:pink",
    "threshold_cosine": "tab:cyan",
}
VARIANT_MARKERS = {
    "word": "o",
    "production": "X",
    "spacy_baseline": "s",
    "nltk_baseline": "D",
    "axis_similarity": "P",
    "hybrid": "^",
    "product_hybrid": "v",
    "threshold_cosine": "*",
}


def build_variant_comparison_chart(zone_num, model, axis, scores_by_variant, out_path, words=None):
    """One chart per zone-type: the axis words plus every variant's 11
    articles for that zone, each variant in its own colour/marker (see
    VARIANT_PALETTE/VARIANT_MARKERS) — extends src/axis_plot.py's
    single-variant chart to overlay production, spaCy-baseline, and
    NLTK-baseline documents together for direct visual comparison. Pass
    `words` (e.g. the small 4-vs-4 axis's own word list) to plot against a
    different axis than the default large 21-vs-22 one."""
    df = _words_dataframe(axis, model, words=words)
    suffix = f"Z{zone_num}"
    for variant_name, scores in scores_by_variant.items():
        piece_ids = sorted((pid for pid in scores if pid.endswith(suffix)), key=_article_num)
        for piece_id in piece_ids:
            df = add_document(df, piece_id.split("Z")[0], scores[piece_id], kind=variant_name)
    variant_label = "/".join(scores_by_variant.keys())
    title = f"Credible Semantic Axis — words + Articles, {variant_label} ({ZONE_NAMES[zone_num]})"
    graph(df, title, out_path, palette=VARIANT_PALETTE, markers=VARIANT_MARKERS)


def main():
    production_scores = run_pipeline(weighting="tfidf", pos_filter=True)

    spacy_scores, spacy_weights = run_baseline(spacy_stopword_set())
    nltk_scores, nltk_weights = run_baseline(nltk_stopword_set())

    write_top_token_table(
        top_token_per_piece(spacy_weights), "outputs/tables/STANDARD_TOP_TOKENS.csv"
    )
    write_top_token_table(
        top_token_per_piece(nltk_weights), "outputs/tables/NLTK_TOP_TOKENS.csv"
    )

    comparisons = {
        "production_vs_spacy": write_comparison(
            production_scores, spacy_scores, "production", "spacy_baseline",
            "outputs/tables/PROD_vs_STAN_COMPARISON.csv",
        ),
        "production_vs_nltk": write_comparison(
            production_scores, nltk_scores, "production", "nltk_baseline",
            "outputs/tables/PROD_vs_NLTK_COMPARISON.csv",
        ),
        "spacy_vs_nltk": write_comparison(
            spacy_scores, nltk_scores, "spacy_baseline", "nltk_baseline",
            "outputs/tables/STAN_vs_NLTK_COMPARISON.csv",
        ),
    }

    model = get_model()
    axis = build_axis(model)
    scores_by_variant = {
        "production": production_scores,
        "spacy_baseline": spacy_scores,
        "nltk_baseline": nltk_scores,
    }
    for zone_num in [1, 2, 3, 4]:
        out_path = f"outputs/figures/PROD_STAN_NLTK_WORDS_AND_DOCUMENTS_Z{zone_num}.png"
        build_variant_comparison_chart(zone_num, model, axis, scores_by_variant, out_path)
        print(f"Wrote {out_path}")

    zone_deltas, article_deltas = signed_delta_by_zone_and_article(
        comparisons["production_vs_spacy"], "production", "spacy_baseline"
    )
    plot_signed_delta_bar(
        zone_deltas, ["Headline+Lead", "Body", "End", "Whole"],
        "Production − spaCy-baseline: mean signed score delta by zone", "Zone",
        "outputs/figures/PROD_vs_STAN_DELTA_BY_ZONE.png",
    )
    plot_signed_delta_bar(
        article_deltas, [f"A{i}" for i in range(1, 12)],
        "Production − spaCy-baseline: mean signed score delta by article", "Article",
        "outputs/figures/PROD_vs_STAN_DELTA_BY_ARTICLE.png",
    )

    print("Wrote 3 comparison tables and 2 top-token tables to outputs/tables/.")
    return production_scores, spacy_scores, nltk_scores, spacy_weights, nltk_weights, comparisons


if __name__ == "__main__":
    main()
