"""ESPN World Cup corpus (spec 007) run through production weighting
(POS-tag filtering + continuity-corrected, high-TF-capped TF-IDF, no
cosine-relevance gate at all) and compared against the two
threshold-cosine variants already run on this corpus (spec 007's own
espn_worldcup_ablation.py, tuned and random-baseline threshold pairs).

Production has never been run on this corpus before -- espn_worldcup_ablation.py
only ever ran the two threshold-cosine variants against it. This adds
production as a third variant, using its own flat (non-zone-grouped)
weighting function (compute_weights_production_flat) and its own
preprocessing (clean_corpus_world_cup_production, POS-filter + the same
World Cup denylist), and compares it against the two existing threshold
variants. Does not touch or re-run anything already saved for those two
variants.
"""

import csv
import statistics
from pathlib import Path

from src.axis import build_axis, project
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
from src.glove import get_model
from src.naive_baseline import spacy_stopword_set

POS_THRESHOLD_TUNED = 0.25
NEG_THRESHOLD_TUNED = 0.02
POS_THRESHOLD_RANDOM_BASELINE = 0.194
NEG_THRESHOLD_RANDOM_BASELINE = 0.096


def write_flat_comparison(scores_a, scores_b, label_a, label_b, out_path):
    """Same idea as src.report.write_comparison, but for this corpus's
    flat "E{n}" piece IDs, which have no "Z" to split on."""
    rank_a = {pid: i + 1 for i, (pid, _) in
              enumerate(sorted(scores_a.items(), key=lambda kv: kv[1], reverse=True))}
    rank_b = {pid: i + 1 for i, (pid, _) in
              enumerate(sorted(scores_b.items(), key=lambda kv: kv[1], reverse=True))}
    rows = []
    for piece_id in scores_a:
        rows.append({
            "piece_id": piece_id,
            f"{label_a}_score": round(scores_a[piece_id], 4),
            f"{label_b}_score": round(scores_b[piece_id], 4),
            f"{label_a}_rank": rank_a[piece_id],
            f"{label_b}_rank": rank_b[piece_id],
            "rank_shift": rank_b[piece_id] - rank_a[piece_id],
        })
    rows.sort(key=lambda r: r[f"{label_a}_rank"])
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    shifts = [abs(r["rank_shift"]) for r in rows]
    return rows, {
        "mean_abs_shift": statistics.mean(shifts),
        "median_abs_shift": statistics.median(shifts),
        "max_abs_shift": max(shifts),
        "unchanged": sum(1 for s in shifts if s == 0),
    }


def main():
    pieces = load_corpus()
    model = get_model()
    axis = build_axis(model)

    production_pieces = clean_corpus_world_cup_production(pieces)
    production_scores, production_weights, production_empty = run_production_variant(
        production_pieces, model, axis
    )
    if production_empty:
        print(f"WARNING [production]: {len(production_empty)} piece(s) empty: {production_empty}")

    write_scores_table(production_scores, "outputs/tables/PRODUCTION_SCORES_ESPN.csv")
    write_top_token_table(production_weights, "outputs/tables/PRODUCTION_TOP_TOKENS_ESPN.csv")

    stopwords = spacy_stopword_set()
    threshold_pieces = clean_corpus_world_cup(pieces, stopwords)

    threshold_scores = {}
    threshold_weights = {}
    for label, pos_t, neg_t in [
        ("tuned", POS_THRESHOLD_TUNED, NEG_THRESHOLD_TUNED),
        ("random_baseline", POS_THRESHOLD_RANDOM_BASELINE, NEG_THRESHOLD_RANDOM_BASELINE),
    ]:
        scores, weights, empty = run_threshold_variant(threshold_pieces, model, axis, pos_t, neg_t)
        threshold_scores[label] = scores
        threshold_weights[label] = weights

    label_acronyms = {"tuned": "CTHRT", "random_baseline": "CTHRR"}

    comparison_stats = {}
    for label in ("tuned", "random_baseline"):
        common_ids = {pid: production_scores[pid] for pid in production_scores if pid in threshold_scores[label]}
        other_ids = {pid: threshold_scores[label][pid] for pid in common_ids}
        _, stats = write_flat_comparison(
            common_ids, other_ids, "production", label,
            f"outputs/tables/PROD_vs_{label_acronyms[label]}_COMPARISON_ESPN.csv",
        )
        comparison_stats[label] = stats

    production_stats = _stats(production_scores)
    production_unique_tokens = len({t for w in production_weights.values() for t in w})

    top_token_agreement = {}
    for label in ("tuned", "random_baseline"):
        agree = sum(
            1 for pid in production_weights
            if production_weights[pid] and threshold_weights[label].get(pid)
            and max(production_weights[pid], key=production_weights[pid].get)
            == max(threshold_weights[label][pid], key=threshold_weights[label][pid].get)
        )
        top_token_agreement[label] = agree

    lines = [
        "# ESPN World Cup corpus: production vs. threshold-cosine — observation only",
        "",
        "Drafted by the Data role (`skills/data/SKILL.md`). Production "
        "(POS-tag filtering + continuity-corrected, high-TF-capped TF-IDF, "
        "no cosine-relevance gate) run for the first time on the 53-article "
        "ESPN World Cup corpus (spec 007), compared against the two "
        "threshold-cosine variants already run on it. Own flat (non-zone-"
        "grouped) weighting and preprocessing functions "
        "(`compute_weights_production_flat`, "
        "`clean_corpus_world_cup_production`, `src/espn_worldcup_ablation.py`) "
        "-- neither the original 11-article corpus nor the two existing "
        "threshold-cosine ESPN outputs are modified or re-run differently "
        "than before. No interpretation of what these figures mean is "
        "included here.",
        "",
        "## Production",
        "",
        f"- n={production_stats['n']}, {len(production_empty)} piece(s) empty.",
        f"- Mean score: {production_stats['mean']:.4f}, stdev: {production_stats['stdev']:.4f}.",
        f"- Range: {production_stats['min']:.4f} to {production_stats['max']:.4f} "
        f"(range {production_stats['range']:.4f}).",
        f"- {production_stats['n_negative']} of {production_stats['n']} pieces score negative.",
        f"- Unique top tokens: {production_unique_tokens}.",
        "",
        "## Rank-shift comparisons",
        "",
        "| | Production vs tuned | Production vs random-baseline |",
        "|---|---|---|",
        f"| Mean \\|rank shift\\| | {comparison_stats['tuned']['mean_abs_shift']:.2f} | "
        f"{comparison_stats['random_baseline']['mean_abs_shift']:.2f} |",
        f"| Median \\|rank shift\\| | {comparison_stats['tuned']['median_abs_shift']:.1f} | "
        f"{comparison_stats['random_baseline']['median_abs_shift']:.1f} |",
        f"| Max \\|rank shift\\| | {comparison_stats['tuned']['max_abs_shift']} | "
        f"{comparison_stats['random_baseline']['max_abs_shift']} |",
        f"| Pieces unchanged | {comparison_stats['tuned']['unchanged']}/{production_stats['n']} | "
        f"{comparison_stats['random_baseline']['unchanged']}/{production_stats['n']} |",
        f"| Top-token agreement | {top_token_agreement['tuned']}/{production_stats['n']} | "
        f"{top_token_agreement['random_baseline']}/{production_stats['n']} |",
        "",
        "## Separation, all three ESPN variants side by side",
        "",
        "| Variant | Mean | Stdev | Range | Negative |",
        "|---|---|---|---|---|",
        f"| Production | {production_stats['mean']:.4f} | {production_stats['stdev']:.4f} | "
        f"{production_stats['range']:.4f} | {production_stats['n_negative']}/{production_stats['n']} |",
    ]
    for label in ("tuned", "random_baseline"):
        s = _stats(threshold_scores[label])
        lines.append(
            f"| Threshold-cosine ({label}) | {s['mean']:.4f} | {s['stdev']:.4f} | "
            f"{s['range']:.4f} | {s['n_negative']}/{s['n']} |"
        )
    lines.append("")
    lines.append("No conclusions are drawn from these figures in this document.")

    with open("outputs/PRODUCTION_COMPARISON_ESPN.md", "w") as f:
        f.write("\n".join(lines) + "\n")

    print(f"[production] n={production_stats['n']} mean={production_stats['mean']:.4f} "
          f"stdev={production_stats['stdev']:.4f} range={production_stats['range']:.4f} "
          f"negative={production_stats['n_negative']}")
    for label in ("tuned", "random_baseline"):
        cs = comparison_stats[label]
        print(f"[production vs {label}] mean|shift|={cs['mean_abs_shift']:.2f} "
              f"max={cs['max_abs_shift']} unchanged={cs['unchanged']}/{production_stats['n']} "
              f"top_token_agreement={top_token_agreement[label]}/{production_stats['n']}")
    print("Wrote outputs/tables/PRODUCTION_{SCORES,TOP_TOKENS}_ESPN.csv, "
          "outputs/tables/PROD_vs_{CTHRT,CTHRR}_COMPARISON_ESPN.csv, "
          "outputs/PRODUCTION_COMPARISON_ESPN.md")


if __name__ == "__main__":
    main()
