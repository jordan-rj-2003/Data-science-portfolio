"""Survivor-count-vs-score correlation check, threshold-cosine weighting:
does the number of tokens surviving the cosine-relevance gate correlate
with how positive/negative a piece scores on the axis? Jordan recalled a
prior credibility-axis finding along these lines (r^2 ~= 0.54) -- no
derivation script for that exact number was found anywhere in the repo
(journal, key-findings, outputs/*.md all searched) -- matching this
project's recurring reproducibility-gap pattern (e.g.
threshold_derivation.py's own history). Rather than trust an
unreproducible recalled figure, this rebuilds the check fresh, as
reusable code, for both axes on the ESPN corpus (Corpus B), so the two
numbers are directly and reproducibly comparable.

Uses np.corrcoef for Pearson r, matching src/formality_check.py's
existing convention (not scipy, to stay consistent with the rest of the
project).
"""

from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from src.axis import build_axis, build_balance_axis
from src.espn_worldcup_ablation import (
    NEG_THRESHOLD_RANDOM_BASELINE,
    POS_THRESHOLD_RANDOM_BASELINE,
    clean_corpus_world_cup,
    load_corpus,
    run_threshold_variant,
)
from src.glove import get_model
from src.naive_baseline import spacy_stopword_set
from src.threshold_derivation import derive_thresholds


def survivor_counts_and_scores(weights, scores):
    """Aligns per-piece survivor count (len(weights[piece])) with score,
    for pieces present in both. Returns (counts, score_values) as parallel
    lists in a fixed piece order."""
    piece_ids = [pid for pid in weights if pid in scores]
    counts = [len(weights[pid]) for pid in piece_ids]
    score_values = [scores[pid] for pid in piece_ids]
    return counts, score_values


def pearson_r_and_r2(counts, score_values):
    r = float(np.corrcoef(counts, score_values)[0, 1])
    return r, r ** 2


def run_for_axis(model, axis, pos_threshold, neg_threshold):
    pieces = load_corpus()
    stopwords = spacy_stopword_set()
    clean_pieces = clean_corpus_world_cup(pieces, stopwords)
    scores, weights, empty = run_threshold_variant(clean_pieces, model, axis, pos_threshold, neg_threshold)
    counts, score_values = survivor_counts_and_scores(weights, scores)
    r, r2 = pearson_r_and_r2(counts, score_values)
    return {"r": r, "r2": r2, "n": len(counts), "counts": counts, "scores": score_values, "empty": empty}


def build_comparison_chart(credibility_result, balance_result,
                            out_path="outputs/figures/CTHRESH_SURVIVOR_COUNT_CORRELATION_ESPN.png"):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for ax, label, result in [
        (axes[0], "credibility axis", credibility_result),
        (axes[1], "balance axis", balance_result),
    ]:
        ax.scatter(result["counts"], result["scores"], color="tab:blue")
        ax.set_title(f"{label}\nr={result['r']:.3f}, r²={result['r2']:.3f}, n={result['n']}")
        ax.set_xlabel("Surviving tokens (threshold-cosine)")
        ax.set_ylabel("Axis score")
    fig.suptitle("ESPN World Cup corpus (Corpus B) — survivor count vs. score, threshold-cosine")
    fig.tight_layout()
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=130)
    plt.close(fig)


def write_summary(credibility_result, balance_result,
                   out_path="outputs/SURVIVOR_COUNT_CORRELATION_ESPN.md"):
    lines = [
        "# Survivor-count vs. score correlation, threshold-cosine — observation only",
        "",
        "Drafted by the Data role (`skills/data/SKILL.md`). Tests whether the "
        "number of tokens surviving the threshold-cosine gate correlates with "
        "a piece's axis score, on the ESPN World Cup corpus (Corpus B), for "
        "both the credibility axis (random-baseline threshold pair, spec 006) "
        "and the balance axis (this axis's own pair, spec 010 task 2). Jordan "
        "recalled a prior credibility-axis finding along these lines "
        "(r² ≈ 0.54); no derivation script or saved output for that exact "
        "number was found anywhere in the repo (journal, key-findings, "
        "outputs/*.md all searched) — this is a fresh, reproducible "
        "computation, not a reproduction of that specific prior run, so the "
        "two may legitimately differ. No interpretation of what these figures "
        "mean is included here.",
        "",
        "## Results",
        "",
        "| Axis | n | Pearson r | r² |",
        "|---|---|---|---|",
        f"| Credibility | {credibility_result['n']} | {credibility_result['r']:.4f} | {credibility_result['r2']:.4f} |",
        f"| Balance | {balance_result['n']} | {balance_result['r']:.4f} | {balance_result['r2']:.4f} |",
        "",
        "No conclusions are drawn from these figures in this document.",
    ]
    with open(out_path, "w") as f:
        f.write("\n".join(lines) + "\n")


def main():
    model = get_model()

    credibility_axis = build_axis(model)
    credibility_result = run_for_axis(
        model, credibility_axis, POS_THRESHOLD_RANDOM_BASELINE, NEG_THRESHOLD_RANDOM_BASELINE
    )

    balance_axis = build_balance_axis(model)
    pos_t, neg_t, _ = derive_thresholds(model, balance_axis)
    balance_result = run_for_axis(model, balance_axis, pos_t, neg_t)

    build_comparison_chart(credibility_result, balance_result)
    write_summary(credibility_result, balance_result)

    print(f"[credibility axis] n={credibility_result['n']} r={credibility_result['r']:.4f} "
          f"r2={credibility_result['r2']:.4f}")
    print(f"[balance axis] n={balance_result['n']} r={balance_result['r']:.4f} "
          f"r2={balance_result['r2']:.4f}")
    print("Wrote outputs/figures/CTHRESH_SURVIVOR_COUNT_CORRELATION_ESPN.png, "
          "outputs/SURVIVOR_COUNT_CORRELATION_ESPN.md")


if __name__ == "__main__":
    main()
