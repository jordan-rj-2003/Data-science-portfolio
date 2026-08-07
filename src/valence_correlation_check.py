"""Valence correlation check, threshold-cosine weighting (2026-08-03
addendum to spec 010, Jordan's own specification): for each piece, does its
count of positive-pole survivors correlate with its final score differently
than its count of negative-pole survivors does? Run for both axes
(credibility, balance) and both corpora, per Jordan's explicit scope
confirmation:
  - Corpus A: the 11 real whole-document (Z4) pieces only. Control text is
    computed as part of the same 12-document temporary corpus (needed for
    its own document-frequency stats, same technique as
    src/control_text_threshold_check.py) but excluded from the correlation
    itself -- it's a validity-check document, not part of the real corpus.
    Not the full 44-piece/4-zone battery (spec 010 task 3, still not built).
  - Corpus B: all 53 ESPN World Cup articles.

Credibility axis uses its statistically-grounded random-baseline threshold
pair (0.194/0.096, spec 006/008's recommended primary method) rather than
the degeneracy-tuned pair, to match the balance axis's own single
statistically-derived pair -- a like-for-like comparison between axes,
not a comparison confounded by also switching threshold-derivation method.

Extends src/survivor_count_correlation.py's total-survivor-count check
(which doesn't distinguish which pole a survivor came from) by reusing
src/token_pole_diagnostic.py's per-token pole classification -- already
corpus- and axis-agnostic (cosine>0 vs. cosine<0 relative to whichever
axis is passed in), so "n_balanced"/"n_unbalanced" from summarize() are
read here as "positive-pole"/"negative-pole" survivor counts generically,
not literally balance-axis-specific.

Uses np.corrcoef for Pearson r, matching src/survivor_count_correlation.py
and src/formality_check.py's existing convention (not scipy).
"""

import csv
from pathlib import Path

import numpy as np

from src.axis import build_axis, build_balance_axis, project
from src.axis_weighting import compute_weights_threshold_cosine
from src.compression import EmptyVectorError, compress_corpus
from src.control_text_balance_axis_check import CONTROL_ID, _whole_zone_pieces, load_control_text
from src.espn_worldcup_ablation import (
    NEG_THRESHOLD_RANDOM_BASELINE,
    POS_THRESHOLD_RANDOM_BASELINE,
    clean_corpus_world_cup,
    load_corpus,
    run_threshold_variant,
)
from src.glove import get_model
from src.naive_baseline import spacy_stopword_set
from src.preprocessing import clean_tokens_stopword_baseline
from src.threshold_derivation import derive_thresholds
from src.token_pole_diagnostic import compute_token_diagnostics, summarize


def pole_counts_and_scores(model, axis, weights, scores):
    """weights: {piece_id: {term: weight}}, scores: {piece_id: score}.
    Returns (n_positive, n_negative, score_values) as parallel lists, for
    pieces present in both, in a fixed order."""
    diagnostics = compute_token_diagnostics(model, axis, weights)
    summary = summarize(diagnostics)
    piece_ids = [pid for pid in summary if pid in scores]
    n_positive = [summary[pid]["n_balanced"] for pid in piece_ids]
    n_negative = [summary[pid]["n_unbalanced"] for pid in piece_ids]
    score_values = [scores[pid] for pid in piece_ids]
    return n_positive, n_negative, score_values


def pearson_r(x, y):
    return float(np.corrcoef(x, y)[0, 1])


def valence_correlation(n_positive, n_negative, score_values):
    """Returns (r_positive, r_negative, diff) where diff = r_positive - r_negative."""
    r_positive = pearson_r(n_positive, score_values)
    r_negative = pearson_r(n_negative, score_values)
    return r_positive, r_negative, r_positive - r_negative


def _corpus_a_whole_weights_and_scores(model, axis, pos_threshold, neg_threshold):
    whole_pieces = _whole_zone_pieces()
    stopwords = spacy_stopword_set()
    clean_pieces = {pid: clean_tokens_stopword_baseline(text, stopwords) for pid, text in whole_pieces.items()}
    clean_pieces[CONTROL_ID] = clean_tokens_stopword_baseline(load_control_text(), stopwords)

    weights = compute_weights_threshold_cosine(clean_pieces, model, axis, pos_threshold, neg_threshold)
    weights.pop(CONTROL_ID, None)

    vectors = {}
    for pid, w in weights.items():
        try:
            vectors[pid] = compress_corpus({pid: w}, model)[pid]
        except EmptyVectorError:
            continue
    scores = project(vectors, axis)
    return weights, scores


def _corpus_b_weights_and_scores(model, axis, pos_threshold, neg_threshold):
    pieces = load_corpus()
    stopwords = spacy_stopword_set()
    clean_pieces = clean_corpus_world_cup(pieces, stopwords)
    scores, weights, _empty = run_threshold_variant(clean_pieces, model, axis, pos_threshold, neg_threshold)
    return weights, scores


CORPORA = {
    "corpus_a_whole": _corpus_a_whole_weights_and_scores,
    "corpus_b": _corpus_b_weights_and_scores,
}


def run_all():
    model = get_model()
    credibility_axis = build_axis(model)
    balance_axis = build_balance_axis(model)
    balance_pos, balance_neg, _ = derive_thresholds(model, balance_axis)

    axis_configs = {
        "credibility": (credibility_axis, POS_THRESHOLD_RANDOM_BASELINE, NEG_THRESHOLD_RANDOM_BASELINE),
        "balance": (balance_axis, balance_pos, balance_neg),
    }

    results = {}
    for axis_name, (axis, pos_t, neg_t) in axis_configs.items():
        for corpus_name, fn in CORPORA.items():
            weights, scores = fn(model, axis, pos_t, neg_t)
            n_pos, n_neg, score_values = pole_counts_and_scores(model, axis, weights, scores)
            r_pos, r_neg, diff = valence_correlation(n_pos, n_neg, score_values)
            results[(axis_name, corpus_name)] = {
                "n": len(score_values), "r_positive": r_pos, "r_negative": r_neg, "diff": diff,
            }
    return results


def write_table(results, out_path="outputs/tables/CTHRESH_VALENCE_CORRELATION.csv"):
    rows = [
        {"axis": axis_name, "corpus": corpus_name, "n": r["n"],
         "r_positive": round(r["r_positive"], 4), "r_negative": round(r["r_negative"], 4),
         "diff": round(r["diff"], 4)}
        for (axis_name, corpus_name), r in results.items()
    ]
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["axis", "corpus", "n", "r_positive", "r_negative", "diff"])
        writer.writeheader()
        writer.writerows(rows)


def write_summary(results, out_path="outputs/CTHRESH_VALENCE_CORRELATION.md"):
    lines = [
        "# Valence correlation check: positive- vs. negative-pole survivor count vs. score",
        "",
        "Drafted by the Data role (`skills/data/SKILL.md`), per Jordan's own "
        "specification. For threshold-cosine weighting: does a piece's count "
        "of positive-pole survivors correlate with its final score "
        "differently than its count of negative-pole survivors does? Run for "
        "both axes (credibility, balance) and both corpora (Corpus A: the 11 "
        "real whole-document pieces, control text excluded from the "
        "correlation; Corpus B: all 53 ESPN articles). Credibility axis uses "
        "its statistically-grounded random-baseline threshold pair "
        "(0.194/0.096), matching the balance axis's own single "
        "statistically-derived pair, for a like-for-like comparison -- not "
        "the credibility axis's larger but partly-noisy tuned pair. No "
        "interpretation of what these figures mean is included here.",
        "",
        "## Results",
        "",
        "| Axis | Corpus | n | r (positive-pole survivors vs. score) | "
        "r (negative-pole survivors vs. score) | diff (r_positive − r_negative) |",
        "|---|---|---|---|---|---|",
    ]
    for (axis_name, corpus_name), r in results.items():
        lines.append(
            f"| {axis_name} | {corpus_name} | {r['n']} | {r['r_positive']:.4f} | "
            f"{r['r_negative']:.4f} | {r['diff']:+.4f} |"
        )
    lines += ["", "No conclusions are drawn from these figures in this document."]
    with open(out_path, "w") as f:
        f.write("\n".join(lines) + "\n")


def main():
    results = run_all()
    write_table(results)
    write_summary(results)
    for (axis_name, corpus_name), r in results.items():
        print(f"[{axis_name} / {corpus_name}] n={r['n']} r_positive={r['r_positive']:.4f} "
              f"r_negative={r['r_negative']:.4f} diff={r['diff']:+.4f}")
    print("Wrote outputs/tables/CTHRESH_VALENCE_CORRELATION.csv, outputs/CTHRESH_VALENCE_CORRELATION.md")


if __name__ == "__main__":
    main()
