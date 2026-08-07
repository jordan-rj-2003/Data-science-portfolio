"""Ranked output — table + scatterplot, spec 001 WHAT §7.

Runs the full pipeline (segmentation -> preprocessing -> weighting ->
compression -> axis projection) and writes de-identified results to
outputs/. Labelled by A{n}Z{z} only, per the de-identification scheme —
never real outlet names (spec 001 De-identification section).

Two independent ablations, each isolating one design decision:
  - TF-IDF weighting vs. flat/no-TF-IDF (weight = TF only) — both using
    the current default (POS-filtered) preprocessing.
  - POS-tag grammatical filtering vs. no POS filtering (the original,
    pre-2026-07-18 behaviour: NER removal only) — both using TF-IDF
    weighting.
"""

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.axis import build_axis, project
from src.compression import compress_corpus
from src.glove import get_model
from src.preprocessing import clean_corpus
from src.segmentation import segment_corpus
from src.tfidf import compute_flat_weights, compute_weights

ZONE_NAMES = {1: "Headline+Lead", 2: "Body", 3: "End", 4: "Whole"}

WEIGHTING_FUNCS = {
    "tfidf": compute_weights,
    "flat": compute_flat_weights,
}


def run_pipeline(weighting="tfidf", pos_filter=True, raw_dir="data/raw", n_articles=11):
    article_ids = [f"A{i}" for i in range(1, n_articles + 1)]
    raw_pieces = segment_corpus(raw_dir, article_ids)
    clean_pieces = clean_corpus(raw_pieces, pos_filter=pos_filter)
    weights = WEIGHTING_FUNCS[weighting](clean_pieces)
    model = get_model()
    vectors = compress_corpus(weights, model)
    axis = build_axis(model)
    return project(vectors, axis)


def write_table(scores, out_path):
    rows = []
    for piece_id, score in sorted(scores.items(), key=lambda kv: kv[1], reverse=True):
        article, zone = piece_id.split("Z")
        rows.append(
            {
                "piece_id": piece_id,
                "article": article,
                "zone": ZONE_NAMES[int(zone)],
                "score": round(score, 4),
            }
        )
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["piece_id", "article", "zone", "score"])
        writer.writeheader()
        writer.writerows(rows)
    return rows


def write_figure(scores, out_path, title):
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes = axes.flatten()
    for zone_num, ax in zip([1, 2, 3, 4], axes):
        zone_scores = {pid: s for pid, s in scores.items() if pid.endswith(f"Z{zone_num}")}
        items = sorted(zone_scores.items(), key=lambda kv: kv[1])
        labels = [pid.split("Z")[0] for pid, _ in items]
        vals = [s for _, s in items]
        ax.scatter(vals, range(len(vals)), s=60)
        ax.set_yticks(range(len(vals)))
        ax.set_yticklabels(labels, fontsize=9)
        ax.set_title(f"{ZONE_NAMES[zone_num]} (Z{zone_num})")
        ax.set_xlabel("Credibility axis projection (cosine similarity)")
        ax.grid(axis="x", alpha=0.3)
    plt.suptitle(title, fontsize=13)
    plt.tight_layout()
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=130)
    plt.close(fig)


def write_comparison(scores_a, scores_b, label_a, label_b, out_path):
    """Side-by-side table: two schemes' scores, ranks, and the shift
    between them, per piece."""
    rank_a = {
        pid: i + 1
        for i, (pid, _) in enumerate(sorted(scores_a.items(), key=lambda kv: kv[1], reverse=True))
    }
    rank_b = {
        pid: i + 1
        for i, (pid, _) in enumerate(sorted(scores_b.items(), key=lambda kv: kv[1], reverse=True))
    }
    rows = []
    for piece_id in scores_a:
        article, zone = piece_id.split("Z")
        rows.append(
            {
                "piece_id": piece_id,
                "article": article,
                "zone": ZONE_NAMES[int(zone)],
                f"{label_a}_score": round(scores_a[piece_id], 4),
                f"{label_b}_score": round(scores_b[piece_id], 4),
                f"{label_a}_rank": rank_a[piece_id],
                f"{label_b}_rank": rank_b[piece_id],
                "rank_shift": rank_b[piece_id] - rank_a[piece_id],
            }
        )
    rows.sort(key=lambda r: r[f"{label_a}_rank"])
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "piece_id",
                "article",
                "zone",
                f"{label_a}_score",
                f"{label_b}_score",
                f"{label_a}_rank",
                f"{label_b}_rank",
                "rank_shift",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)
    return rows


def _summarize(rows, label_a, label_b, name):
    shifts = [abs(r["rank_shift"]) for r in rows]
    mean_shift = sum(shifts) / len(shifts)
    max_row = max(rows, key=lambda r: abs(r["rank_shift"]))
    print(f"[{name}] mean absolute rank shift: {mean_shift:.2f} / {len(rows)}")
    print(
        f"[{name}] largest shift: {max_row['piece_id']} "
        f"({label_a} rank {max_row[f'{label_a}_rank']} -> {label_b} rank {max_row[f'{label_b}_rank']})"
    )


def main():
    # Ablation 1: TF-IDF weighting vs. flat, both POS-filtered (production default)
    tfidf_scores = run_pipeline(weighting="tfidf", pos_filter=True)
    flat_scores = run_pipeline(weighting="flat", pos_filter=True)

    write_table(tfidf_scores, "outputs/tables/PRODUCTION_SCORES.csv")
    write_table(flat_scores, "outputs/tables/FLAT_SCORES.csv")
    weighting_comparison = write_comparison(
        tfidf_scores, flat_scores, "tfidf", "flat", "outputs/tables/PROD_vs_FLAT_COMPARISON.csv"
    )
    write_figure(
        tfidf_scores,
        "outputs/figures/PRODUCTION_BY_ZONE.png",
        "Credibility Axis Projection by Article and Zone — TF-IDF weighted (de-identified)",
    )
    write_figure(
        flat_scores,
        "outputs/figures/FLAT_BY_ZONE.png",
        "Credibility Axis Projection by Article and Zone — flat/unweighted mean, no TF-IDF (de-identified)",
    )
    _summarize(weighting_comparison, "tfidf", "flat", "TF-IDF vs flat")

    # Ablation 2: POS-tag filtering vs. no POS filtering, both TF-IDF-weighted
    pos_scores = tfidf_scores  # same as production run above
    no_pos_scores = run_pipeline(weighting="tfidf", pos_filter=False)

    write_table(no_pos_scores, "outputs/tables/PRODUCTION_NOPOSFILT_SCORES.csv")
    pos_comparison = write_comparison(
        pos_scores, no_pos_scores, "pos_filtered", "no_pos_filter", "outputs/tables/PRODUCTION_POSFILT_vs_NOPOSFILT_COMPARISON.csv"
    )
    write_figure(
        no_pos_scores,
        "outputs/figures/PRODUCTION_NOPOSFILT_BY_ZONE.png",
        "Credibility Axis Projection by Article and Zone — TF-IDF, no POS filtering (de-identified)",
    )
    _summarize(pos_comparison, "pos_filtered", "no_pos_filter", "POS-filtered vs unfiltered")

    print("Done. See outputs/tables/ and outputs/figures/.")


if __name__ == "__main__":
    main()
