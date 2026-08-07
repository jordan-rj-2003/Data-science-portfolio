"""Pole-survivor diagnostic for Corpus B (ESPN, 53 articles), threshold-
cosine weighting, balance axis -- same underlying per-token diagnostic as
src/token_pole_diagnostic.py (built for Corpus A), applied here instead
to Corpus B and grouped differently per Jordan's request: for each piece,
diff = n_balanced_survivors - n_unbalanced_survivors (negative when a
piece has more unbalanced-pole survivors, e.g. -1/-2/-3/-4), bucketed into
"positive pole" (diff > 0), "negative pole" (diff < 0), and "tied"
(diff == 0, reported separately rather than folded into either bucket),
with the diffs summed within each bucket.

Reuses token_pole_diagnostic.compute_token_diagnostics/summarize
unchanged -- both are already corpus-agnostic (just {piece_id: {term:
weight}} in, per-piece stats out) -- so no new token-level logic is
needed here, only the ESPN corpus loading/weighting (already built,
espn_worldcup_ablation.py) and the new grouping/summing step.
"""

import csv
from pathlib import Path

from src.axis import build_balance_axis
from src.espn_worldcup_ablation import clean_corpus_world_cup, load_corpus, run_threshold_variant
from src.glove import get_model
from src.naive_baseline import spacy_stopword_set
from src.threshold_derivation import derive_thresholds
from src.token_pole_diagnostic import compute_token_diagnostics, summarize


def group_by_pole_lean(summary):
    """summary: {piece_id: {"n_survivors", "n_balanced", "n_unbalanced"}}
    (from token_pole_diagnostic.summarize). Returns
    {"positive_pole": {piece_id: diff, ...}, "negative_pole": {...}, "tied": {...}}
    where diff = n_balanced - n_unbalanced."""
    positive_pole, negative_pole, tied = {}, {}, {}
    for piece_id, stats in summary.items():
        diff = stats["n_balanced"] - stats["n_unbalanced"]
        if diff > 0:
            positive_pole[piece_id] = diff
        elif diff < 0:
            negative_pole[piece_id] = diff
        else:
            tied[piece_id] = diff
    return {"positive_pole": positive_pole, "negative_pole": negative_pole, "tied": tied}


def sum_by_group(groups):
    """groups: output of group_by_pole_lean. Returns {group_name: sum_of_diffs}."""
    return {name: sum(diffs.values()) for name, diffs in groups.items()}


def average_by_group(groups):
    """groups: output of group_by_pole_lean. Returns {group_name: mean_diff},
    0.0 for an empty group rather than a division-by-zero error."""
    return {
        name: (sum(diffs.values()) / len(diffs) if diffs else 0.0)
        for name, diffs in groups.items()
    }


def write_table(summary, groups, out_path="outputs/tables/CTHRESH_POLE_DIAGNOSTIC_ESPN_BAL.csv"):
    piece_to_group = {}
    for group_name, diffs in groups.items():
        for piece_id in diffs:
            piece_to_group[piece_id] = group_name

    rows = []
    for piece_id, stats in summary.items():
        diff = stats["n_balanced"] - stats["n_unbalanced"]
        rows.append({
            "piece_id": piece_id,
            "n_survivors": stats["n_survivors"],
            "n_balanced": stats["n_balanced"],
            "n_unbalanced": stats["n_unbalanced"],
            "diff": diff,
            "group": piece_to_group[piece_id],
        })
    rows.sort(key=lambda r: r["diff"])
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["piece_id", "n_survivors", "n_balanced", "n_unbalanced", "diff", "group"]
        )
        writer.writeheader()
        writer.writerows(rows)


def main():
    model = get_model()
    axis = build_balance_axis(model)
    pos_threshold, neg_threshold, _ = derive_thresholds(model, axis)

    pieces = load_corpus()
    stopwords = spacy_stopword_set()
    clean_pieces = clean_corpus_world_cup(pieces, stopwords)

    _, weights, empty = run_threshold_variant(clean_pieces, model, axis, pos_threshold, neg_threshold)
    if empty:
        print(f"WARNING: {len(empty)} piece(s) empty on both poles, excluded from diagnostics: {empty}")

    diagnostics = compute_token_diagnostics(model, axis, weights)
    summary = summarize(diagnostics)
    groups = group_by_pole_lean(summary)
    group_sums = sum_by_group(groups)
    group_averages = average_by_group(groups)

    write_table(summary, groups)
    print("Wrote outputs/tables/CTHRESH_POLE_DIAGNOSTIC_ESPN_BAL.csv")
    for name in ("positive_pole", "negative_pole", "tied"):
        print(f"{name}: {len(groups[name])} pieces, sum of diffs = {group_sums[name]:+d}, "
              f"average diff = {group_averages[name]:+.2f}")


if __name__ == "__main__":
    main()
