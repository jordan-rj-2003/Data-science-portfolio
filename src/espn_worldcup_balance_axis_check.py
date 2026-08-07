"""ESPN World Cup corpus ("Corpus B", spec 007) run through the new
balance axis (spec 010): standard baseline (spaCy-stopword preprocessing
+ plain TF-IDF, no cosine gate), production (POS-filtered,
continuity-corrected/high-TF-capped TF-IDF, no cosine gate), and
threshold-cosine (statistically-grounded 5th/95th-percentile pair,
re-derived for this axis via src.threshold_derivation). Compared in the
same fashion as the credibility-axis ESPN comparison
(espn_worldcup_production_check.py): flat (non-zone) rank-shift
comparison tables + separation stats.

Per spec 010 CONSTRAINTS: no new weighting formulas (only the axis vector
passed into project() changes; compute_weights_plain_flat here is a
flat-corpus port of the existing compute_weights_plain, same as
espn_worldcup_ablation.py already did for production/threshold-cosine),
and every output uses a `_balance_axis` suffix so nothing existing is
touched.
"""

import csv
import statistics
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.metrics.pairwise import cosine_similarity

from src.axis import BALANCE_WORDS, UNBALANCE_WORDS, build_balance_axis, project
from src.axis_weighting import _cosine_similarity_to_axis
from src.compression import EmptyVectorError, compress_corpus
from src.espn_worldcup_ablation import (
    _stats,
    clean_corpus_world_cup,
    clean_corpus_world_cup_production,
    load_corpus,
    run_production_variant,
    run_threshold_variant,
    write_scores_table,
    write_top_token_table,
)
from src.espn_worldcup_production_check import write_flat_comparison
from src.glove import get_model
from src.naive_baseline import spacy_stopword_set
from src.threshold_derivation import derive_thresholds
from src.tfidf import compute_idf_plain


def compute_weights_plain_flat(pieces):
    """Flat-corpus port of src.tfidf.compute_weights_plain (spec 002's
    naive-baseline weighting: TF x plain idf, no continuity correction, no
    high-TF cap). compute_weights_plain groups by zone-type via
    group_by_zone(), which doesn't apply to this corpus's zone-less
    "E{n}" piece IDs -- the same problem already solved for
    production/threshold-cosine via compute_weights_production_flat /
    compute_weights_threshold_cosine_flat in espn_worldcup_ablation.py."""
    idf = compute_idf_plain(pieces)
    weights = {}
    for piece_id, tokens in pieces.items():
        tf = Counter(tokens)
        weights[piece_id] = {term: count * idf[term] for term, count in tf.items()}
    return weights


def run_standard_baseline_variant(clean_pieces, model, axis):
    """Standard/naive baseline: spaCy-stopword preprocessing (already
    applied to clean_pieces via clean_corpus_world_cup) + plain flat
    TF-IDF, no cosine gate -- matches src.naive_baseline.run_baseline's
    spaCy variant on the original corpus, adapted for this corpus's flat
    piece IDs."""
    weights = compute_weights_plain_flat(clean_pieces)
    vectors = {}
    empty_pieces = []
    for piece_id, term_weights in weights.items():
        try:
            vectors[piece_id] = compress_corpus({piece_id: term_weights}, model)[piece_id]
        except EmptyVectorError:
            empty_pieces.append(piece_id)
    scores = project(vectors, axis)
    return scores, weights, empty_pieces


def diagnose_threshold_degeneracy(clean_pieces, model, axis, pos_threshold, neg_threshold):
    """Spec 010 RISK 1: before trusting a threshold pair on this
    axis/corpus, count how many pieces would have zero surviving tokens on
    the positive pole, negative pole, or both -- the same check spec 006
    ran before adopting a threshold pair for the credibility axis. Returns
    (zero_positive_pole, zero_negative_pole, zero_both) piece-id lists."""
    axis_2d = axis.reshape(1, -1)
    zero_pos, zero_neg, zero_both = [], [], []
    for piece_id, tokens in clean_pieces.items():
        pos_survivors = 0
        neg_survivors = 0
        for term in set(tokens):
            if term not in model:
                continue
            sim = _cosine_similarity_to_axis(term, model, axis_2d)
            if sim > pos_threshold:
                pos_survivors += 1
            elif sim < -neg_threshold:
                neg_survivors += 1
        piece_zero_pos = pos_survivors == 0
        piece_zero_neg = neg_survivors == 0
        if piece_zero_pos:
            zero_pos.append(piece_id)
        if piece_zero_neg:
            zero_neg.append(piece_id)
        if piece_zero_pos and piece_zero_neg:
            zero_both.append(piece_id)
    return zero_pos, zero_neg, zero_both


def build_axis_chart(model, axis, scores_by_variant, out_path):
    """Balance-axis equivalent of espn_worldcup_ablation.build_axis_chart:
    the 14 balance/unbalance axis words plus every variant's 53 articles
    overlaid, each variant in its own colour/marker."""
    all_words = BALANCE_WORDS + UNBALANCE_WORDS
    word_scores = [cosine_similarity([axis], [model[w]])[0][0] for w in all_words]
    df = pd.DataFrame({"label": all_words, "score": word_scores, "kind": "word"})

    palette = {"word": "tab:blue", "standard": "tab:orange", "production": "tab:red",
               "threshold_cosine": "tab:cyan"}
    markers = {"word": "o", "standard": "s", "production": "X", "threshold_cosine": "*"}
    for variant_name, scores in scores_by_variant.items():
        for pid, s in scores.items():
            df = pd.concat([df, pd.DataFrame({"label": [pid], "score": [s], "kind": [variant_name]})],
                            ignore_index=True)

    plt.figure(figsize=(12, 20))
    ax = sns.scatterplot(data=df, x="score", y="label", hue="kind", style="kind",
                          palette=palette, markers=markers, s=70)
    plt.title("ESPN World Cup corpus (Corpus B) — balance-axis words + articles, "
               "standard/production/threshold-cosine")
    plt.yticks(fontsize=6)
    plt.axvline(0, linestyle="--")
    plt.legend(loc="lower right")
    plt.tight_layout()
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=130)
    plt.close()


def top_token_frequency(weights_by_variant, n=10):
    """For each variant, tallies how often each token wins the top-weight
    slot across all 53 pieces (matching the "Unique top tokens" stat
    already used in espn_worldcup_production_check.py, extended here to
    show *which* tokens repeat, not just the count). Returns
    {variant: [(token, count), ...]} sorted by count descending, top n."""
    result = {}
    for variant, weights in weights_by_variant.items():
        top_tokens = []
        for term_weights in weights.values():
            if term_weights:
                top_tokens.append(max(term_weights.items(), key=lambda kv: kv[1])[0])
        result[variant] = Counter(top_tokens).most_common(n)
    return result


def write_top_token_frequency_table(freq_by_variant, out_path):
    rows = []
    for variant, tokens in freq_by_variant.items():
        for rank, (token, count) in enumerate(tokens, start=1):
            rows.append({"variant": variant, "rank": rank, "token": token, "count": count})
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["variant", "rank", "token", "count"])
        writer.writeheader()
        writer.writerows(rows)


def build_top_token_frequency_chart(freq_by_variant, out_path):
    fig, axes = plt.subplots(1, len(freq_by_variant), figsize=(6 * len(freq_by_variant), 5))
    for ax, (variant, tokens) in zip(axes, freq_by_variant.items()):
        labels = [t for t, _ in tokens]
        counts = [c for _, c in tokens]
        ax.barh(labels[::-1], counts[::-1], color="tab:blue")
        ax.set_title(variant)
        ax.set_xlabel("Times this token is a piece's top-weighted token")
    fig.suptitle("ESPN World Cup corpus (Corpus B) — most frequent top tokens, balance axis")
    fig.tight_layout()
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=130)
    plt.close(fig)


def write_summary(pos_threshold, neg_threshold, degeneracy, stats_by_variant, empty_by_variant,
                   comparison_stats, unique_tokens_by_variant,
                   out_path="outputs/STAN_PROD_CTHRESH_COMPARISON_ESPN_BAL.md"):
    zero_pos, zero_neg, zero_both = degeneracy
    n = stats_by_variant["standard"]["n"]
    lines = [
        "# ESPN World Cup corpus (Corpus B) — balance axis, standard fashion comparison",
        "",
        "Drafted by the Data role (`skills/data/SKILL.md`). Three variants run "
        "against the new balance/one-sidedness axis (spec 010): standard "
        "baseline (spaCy-stopword preprocessing + plain TF-IDF, no cosine "
        "gate), production (POS-filtered, continuity-corrected TF-IDF, no "
        "cosine gate), and threshold-cosine (statistically-grounded "
        "5th/95th-percentile pair, re-derived for this axis). Neither the "
        "credibility-axis ESPN outputs nor the original 11-article corpus "
        "are modified or re-run differently than before. No interpretation "
        "of what these figures mean is included here.",
        "",
        f"## Threshold pair used (statistically-grounded, this axis)",
        "",
        f"- pos_threshold = {pos_threshold:.4f}, neg_threshold = {neg_threshold:.4f} "
        f"(5th/95th percentile of the same reference-vocabulary sample "
        "`threshold_derivation.py` already uses, re-derived against the "
        "balance axis).",
        "",
        "## Degeneracy diagnosis (spec 010 RISK 1)",
        "",
        f"- {len(zero_pos)}/{n} pieces have zero surviving positive-pole tokens.",
        f"- {len(zero_neg)}/{n} pieces have zero surviving negative-pole tokens.",
        f"- {len(zero_both)}/{n} pieces have zero survivors on both poles "
        "(would be excluded from scoring entirely).",
        "",
        "## Separation, all three variants",
        "",
        "| Variant | n | Mean | Stdev | Range | Negative |",
        "|---|---|---|---|---|---|",
    ]
    for label in ("standard", "production", "threshold_cosine"):
        s = stats_by_variant[label]
        lines.append(
            f"| {label} | {s['n']} | {s['mean']:.4f} | {s['stdev']:.4f} | "
            f"{s['range']:.4f} | {s['n_negative']}/{s['n']} |"
        )
    lines += [
        "",
        "## Top tokens",
        "",
        "| Variant | Unique top tokens |",
        "|---|---|",
    ]
    for label in ("standard", "production", "threshold_cosine"):
        lines.append(f"| {label} | {unique_tokens_by_variant[label]}/{n} |")
    lines += [
        "",
        "See `outputs/tables/TOP_TOKEN_FREQUENCY_ESPN_BAL.csv` "
        "for which specific tokens repeat as a piece's top token, and "
        "`outputs/figures/TOP_TOKEN_FREQUENCY_ESPN_BAL.png`.",
        "",
        "## Rank-shift comparisons",
        "",
        "| Comparison | Mean \\|shift\\| | Median \\|shift\\| | Max \\|shift\\| | Unchanged |",
        "|---|---|---|---|---|",
    ]
    for pair_label, stats in comparison_stats.items():
        lines.append(
            f"| {pair_label} | {stats['mean_abs_shift']:.2f} | {stats['median_abs_shift']:.1f} | "
            f"{stats['max_abs_shift']} | {stats['unchanged']}/{n} |"
        )
    lines += ["", "No conclusions are drawn from these figures in this document."]

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        f.write("\n".join(lines) + "\n")


def main():
    pieces = load_corpus()
    model = get_model()
    axis = build_balance_axis(model)

    pos_threshold, neg_threshold, _ = derive_thresholds(model, axis)
    print(f"Balance axis, statistically-grounded threshold pair: "
          f"pos={pos_threshold:.4f} neg={neg_threshold:.4f}")

    stopwords = spacy_stopword_set()
    stopword_pieces = clean_corpus_world_cup(pieces, stopwords)
    production_pieces = clean_corpus_world_cup_production(pieces)

    degeneracy = diagnose_threshold_degeneracy(stopword_pieces, model, axis, pos_threshold, neg_threshold)
    zero_pos, zero_neg, zero_both = degeneracy
    print(f"Degeneracy check: {len(zero_pos)}/{len(pieces)} zero positive-pole survivors, "
          f"{len(zero_neg)}/{len(pieces)} zero negative-pole, {len(zero_both)}/{len(pieces)} zero on both.")

    standard_scores, standard_weights, standard_empty = run_standard_baseline_variant(
        stopword_pieces, model, axis
    )
    production_scores, production_weights, production_empty = run_production_variant(
        production_pieces, model, axis
    )
    threshold_scores, threshold_weights, threshold_empty = run_threshold_variant(
        stopword_pieces, model, axis, pos_threshold, neg_threshold
    )

    empty_by_variant = {"standard": standard_empty, "production": production_empty,
                         "threshold_cosine": threshold_empty}
    for label, empty in empty_by_variant.items():
        if empty:
            print(f"WARNING [{label}]: {len(empty)} piece(s) empty: {empty}")

    write_scores_table(standard_scores, "outputs/tables/STANDARD_SCORES_ESPN_BAL.csv")
    write_scores_table(production_scores, "outputs/tables/PRODUCTION_SCORES_ESPN_BAL.csv")
    write_scores_table(threshold_scores, "outputs/tables/CTHRESH_SCORES_ESPN_BAL.csv")

    write_top_token_table(standard_weights, "outputs/tables/STANDARD_TOP_TOKENS_ESPN_BAL.csv")
    write_top_token_table(production_weights, "outputs/tables/PRODUCTION_TOP_TOKENS_ESPN_BAL.csv")
    write_top_token_table(threshold_weights, "outputs/tables/CTHRESH_TOP_TOKENS_ESPN_BAL.csv")

    scores_by_variant = {
        "standard": standard_scores,
        "production": production_scores,
        "threshold_cosine": threshold_scores,
    }

    pairs = [
        ("threshold_cosine", "production"),
        ("threshold_cosine", "standard"),
        ("production", "standard"),
    ]
    label_acronyms = {"threshold_cosine": "CTHRESH", "production": "PROD", "standard": "STAN"}
    comparison_stats = {}
    for label_a, label_b in pairs:
        scores_a = scores_by_variant[label_a]
        scores_b = scores_by_variant[label_b]
        common_ids = {pid: scores_a[pid] for pid in scores_a if pid in scores_b}
        other_ids = {pid: scores_b[pid] for pid in common_ids}
        _, stats = write_flat_comparison(
            common_ids, other_ids, label_a, label_b,
            f"outputs/tables/{label_acronyms[label_a]}_vs_{label_acronyms[label_b]}_COMPARISON_ESPN_BAL.csv",
        )
        comparison_stats[f"{label_a} vs {label_b}"] = stats

    stats_by_variant = {label: _stats(scores) for label, scores in scores_by_variant.items()}

    weights_by_variant = {
        "standard": standard_weights,
        "production": production_weights,
        "threshold_cosine": threshold_weights,
    }
    unique_tokens_by_variant = {
        label: len({max(w.items(), key=lambda kv: kv[1])[0] for w in weights.values() if w})
        for label, weights in weights_by_variant.items()
    }
    freq_by_variant = top_token_frequency(weights_by_variant)
    write_top_token_frequency_table(freq_by_variant, "outputs/tables/TOP_TOKEN_FREQUENCY_ESPN_BAL.csv")
    build_top_token_frequency_chart(freq_by_variant, "outputs/figures/TOP_TOKEN_FREQUENCY_ESPN_BAL.png")

    write_summary(pos_threshold, neg_threshold, degeneracy, stats_by_variant, empty_by_variant,
                  comparison_stats, unique_tokens_by_variant)

    chart_path = "outputs/figures/STAN_PROD_CTHRESH_WORDS_AND_DOCUMENTS_ESPN_BAL.png"
    build_axis_chart(model, axis, scores_by_variant, chart_path)
    print(f"Wrote {chart_path}")
    print("Wrote outputs/figures/TOP_TOKEN_FREQUENCY_ESPN_BAL.png")

    for label, stats in stats_by_variant.items():
        print(f"[{label}] n={stats['n']} mean={stats['mean']:.4f} stdev={stats['stdev']:.4f} "
              f"range={stats['range']:.4f} negative={stats['n_negative']} "
              f"unique_top_tokens={unique_tokens_by_variant[label]}")
    for pair_label, stats in comparison_stats.items():
        print(f"[{pair_label}] mean|shift|={stats['mean_abs_shift']:.2f} max={stats['max_abs_shift']} "
              f"unchanged={stats['unchanged']}")
    print("Wrote outputs/tables/{STANDARD,PRODUCTION,CTHRESH}_*_ESPN_BAL.csv, "
          "outputs/STAN_PROD_CTHRESH_COMPARISON_ESPN_BAL.md")


if __name__ == "__main__":
    main()
