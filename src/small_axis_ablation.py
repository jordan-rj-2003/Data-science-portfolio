"""Small (4-vs-4) axis vs. large (21-vs-22) axis ablation.

Tests whether projecting onto the Lit Review §2.2 proof-of-concept axis
(honest/true/accurate/impartial vs dishonest/untrue/inaccurate/biased)
changes results relative to the large axis used everywhere else in this
project, across three weighting variants: production (corrected TF-IDF +
POS-filtering), spaCy-baseline (plain TF-IDF + stopword-list), and the
product-form hybrid (TF*IDF*abs(cosine_similarity(word, axis))).

For production and spaCy-baseline, document vectors don't depend on the
axis at all (the axis only enters at the final cosine-similarity
projection step), so the same vectors are projected onto both axes.

For the product hybrid, the axis enters the weighting formula itself
(each token's weight is modulated by its own cosine similarity to the
axis) — so the small-axis run recomputes weights and re-compresses
document vectors using the small axis, rather than just re-projecting
the large-axis-weighted vectors. This is the "everywhere" scope: it tests
whether the whole hybrid method is sensitive to axis size, not just the
final score.
"""

import csv
import statistics
from collections import defaultdict
from pathlib import Path

from src.axis import (
    SMALL_CREDIBLE_WORDS,
    SMALL_NON_CREDIBLE_WORDS,
    build_axis,
    build_small_axis,
    project,
)
from src.axis_weighting import compute_weights_hybrid_product
from src.compression import compress_corpus
from src.glove import get_model
from src.naive_baseline import (
    build_variant_comparison_chart,
    spacy_stopword_set,
    top_token_per_piece,
    write_top_token_table,
)
from src.preprocessing import clean_corpus, clean_corpus_stopword_baseline
from src.report import ZONE_NAMES, write_comparison
from src.segmentation import segment_corpus
from src.tfidf import compute_weights, compute_weights_plain

ARTICLE_IDS = [f"A{i}" for i in range(1, 12)]


def _raw_and_model():
    raw_pieces = segment_corpus("data/raw", ARTICLE_IDS)
    model = get_model()
    return raw_pieces, model


def run_production_both_axes(raw_pieces, model, large_axis, small_axis):
    clean_pieces = clean_corpus(raw_pieces, pos_filter=True)
    weights = compute_weights(clean_pieces)
    vectors = compress_corpus(weights, model)
    return project(vectors, large_axis), project(vectors, small_axis)


def run_spacy_baseline_both_axes(raw_pieces, model, large_axis, small_axis):
    clean_pieces = clean_corpus_stopword_baseline(raw_pieces, spacy_stopword_set())
    weights = compute_weights_plain(clean_pieces)
    vectors = compress_corpus(weights, model)
    return project(vectors, large_axis), project(vectors, small_axis)


def run_product_hybrid_both_axes(raw_pieces, model, large_axis, small_axis):
    clean_pieces = clean_corpus_stopword_baseline(raw_pieces, spacy_stopword_set())

    large_weights = compute_weights_hybrid_product(clean_pieces, model, large_axis)
    large_vectors = compress_corpus(large_weights, model)
    large_scores = project(large_vectors, large_axis)

    small_weights = compute_weights_hybrid_product(clean_pieces, model, small_axis)
    small_vectors = compress_corpus(small_weights, model)
    small_scores = project(small_vectors, small_axis)

    return large_scores, small_scores, large_weights, small_weights


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


def _top_token_agreement(rows_a, rows_b):
    a = {pid: term for pid, term, _w in rows_a}
    b = {pid: term for pid, term, _w in rows_b}
    matches = sum(1 for pid in a if a[pid] == b[pid])
    return matches, len(a)


def write_summary(stats_by_variant, top_token_agreement_product_hybrid, out_path):
    lines = [
        "# Small (4-vs-4) axis vs. large (21-vs-22) axis — observation only",
        "",
        "Drafted by the Data role (`skills/data/SKILL.md`). Compares the "
        "Lit Review §2.2 proof-of-concept axis (honest/true/accurate/impartial "
        "vs dishonest/untrue/inaccurate/biased) against the large axis used "
        "everywhere else, across three weighting variants. No interpretation "
        "of what these differences mean is included here. Source: "
        "`outputs/tables/SMALL_AXIS_*_COMPARISON.csv`.",
        "",
    ]
    for variant, stats in stats_by_variant.items():
        lines.append(f"## {variant}")
        lines.append("")
        lines.append(f"- Mean absolute rank shift: {stats['mean_abs']:.2f}, "
                      f"median {stats['median_abs']:.1f}, "
                      f"range {stats['min_signed']} to {stats['max_signed']}.")
        lines.append(f"- {stats['unchanged']} of {stats['n']} pieces unchanged (shift = 0).")
        lines.append(f"- Signed shift: mean {stats['mean_signed']:.3f} (structural, as in "
                      f"every other rank-shift comparison in this project), "
                      f"stdev {stats['stdev_signed']:.3f}, "
                      f"range {stats['min_signed']} to {stats['max_signed']}.")
        lines.append(f"- Mean score delta (large_axis − small_axis): "
                      f"{stats['mean_delta']:.4f}, stdev {stats['stdev_delta']:.4f}.")
        zone_line = ", ".join(
            f"{zone} {v['mean_abs']:.2f}/{v['mean_signed']:+.2f}"
            for zone, v in stats["by_zone"].items()
        )
        lines.append(f"- Mean absolute/signed rank shift by zone: {zone_line}.")
        lines.append("")

    matches, n = top_token_agreement_product_hybrid
    lines.append("## Product hybrid: top-token identity, large axis vs. small axis")
    lines.append("")
    lines.append(f"- Same top token under both axes: {matches}/{n} pieces "
                  f"(only the product hybrid's weighting depends on the axis "
                  f"itself; production and spaCy-baseline token weights are "
                  f"identical regardless of which axis they're later projected onto).")
    lines.append("")
    lines.append("No conclusions are drawn from these figures in this document.")

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        f.write("\n".join(lines) + "\n")


def main():
    raw_pieces, model = _raw_and_model()
    large_axis = build_axis(model)
    small_axis = build_small_axis(model)

    production_large, production_small = run_production_both_axes(raw_pieces, model, large_axis, small_axis)
    spacy_large, spacy_small = run_spacy_baseline_both_axes(raw_pieces, model, large_axis, small_axis)
    product_large, product_small, product_large_weights, product_small_weights = run_product_hybrid_both_axes(
        raw_pieces, model, large_axis, small_axis
    )

    comparisons = {
        "production": write_comparison(
            production_large, production_small, "large_axis", "small_axis",
            "outputs/tables/SMALL_AXIS_PRODUCTION_COMPARISON.csv",
        ),
        "spacy_baseline": write_comparison(
            spacy_large, spacy_small, "large_axis", "small_axis",
            "outputs/tables/SMALL_AXIS_STANDARD_COMPARISON.csv",
        ),
        "product_hybrid": write_comparison(
            product_large, product_small, "large_axis", "small_axis",
            "outputs/tables/SMALL_AXIS_PRHYB_COMPARISON.csv",
        ),
    }

    write_top_token_table(
        top_token_per_piece(product_large_weights), "outputs/tables/PRHYB_TOP_TOKENS_LARGE_AXIS.csv"
    )
    write_top_token_table(
        top_token_per_piece(product_small_weights), "outputs/tables/PRHYB_TOP_TOKENS_SMALL_AXIS.csv"
    )

    stats_by_variant = {
        variant: _rank_shift_stats(rows, "large_axis", "small_axis")
        for variant, rows in comparisons.items()
    }

    agreement = _top_token_agreement(
        top_token_per_piece(product_large_weights), top_token_per_piece(product_small_weights)
    )

    write_summary(stats_by_variant, agreement, "outputs/SMALL_AXIS_COMPARISON.md")

    for variant, stats in stats_by_variant.items():
        print(f"[{variant}] mean absolute rank shift: {stats['mean_abs']:.2f} / {stats['n']}")

    scores_by_variant = {
        "production": production_small,
        "spacy_baseline": spacy_small,
        "product_hybrid": product_small,
    }
    small_words = SMALL_CREDIBLE_WORDS + SMALL_NON_CREDIBLE_WORDS
    for zone_num in [1, 2, 3, 4]:
        out_path = f"outputs/figures/SMALL_AXIS_PROD_STAN_PRHYB_WORDS_AND_DOCUMENTS_Z{zone_num}.png"
        build_variant_comparison_chart(zone_num, model, small_axis, scores_by_variant, out_path, words=small_words)
        print(f"Wrote {out_path}")

    print("Done. See outputs/tables/SMALL_AXIS_*_COMPARISON.csv, outputs/SMALL_AXIS_COMPARISON.md, "
          "and outputs/figures/SMALL_AXIS_PROD_STAN_PRHYB_WORDS_AND_DOCUMENTS_Z*.png.")


if __name__ == "__main__":
    main()
