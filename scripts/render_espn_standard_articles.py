"""Corpus B (ESPN, 53 articles), Standard weighting (stopword removal +
plain/uncorrected TF-IDF, no cosine gate) -- article-only projection onto
the credibility axis, no axis words plotted. Matches the existing
CTHRR_ARTICLES_ONLY_ESPN.png visual convention exactly, for a direct
side-by-side with the threshold-cosine (random baseline) version.

Standard has never been run on Corpus B before in this repo (only
production and the two threshold-cosine pairs exist) -- computed fresh
here via the same flat-corpus pattern already used in
src/espn_worldcup_ablation.py (compute_idf_plain over the whole 53-doc
corpus, no zone grouping, since ESPN piece IDs have no "Z").
"""

import csv
import random
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib.pyplot as plt

from src.axis import build_axis, project
from src.compression import compress_corpus
from src.espn_worldcup_ablation import CORPUS_DIR, clean_corpus_world_cup, load_corpus
from src.glove import get_model
from src.naive_baseline import spacy_stopword_set
from src.tfidf import compute_idf_plain


def compute_weights_standard_flat(pieces):
    """Standard = plain/uncorrected TF-IDF (no continuity correction, no
    high-TF cap, matching spec 002's naive baseline), no threshold gate,
    over the flat 53-document ESPN corpus."""
    idf = compute_idf_plain(pieces)
    weights = {}
    for piece_id, tokens in pieces.items():
        tf = Counter(tokens)
        weights[piece_id] = {term: count * idf[term] for term, count in tf.items()}
    return weights


def main():
    pieces = load_corpus(CORPUS_DIR)
    model = get_model()
    axis = build_axis(model)
    stopwords = spacy_stopword_set()
    clean_pieces = clean_corpus_world_cup(pieces, stopwords)

    weights = compute_weights_standard_flat(clean_pieces)
    vectors = compress_corpus(weights, model)
    scores = project(vectors, axis)

    Path("outputs/tables").mkdir(parents=True, exist_ok=True)
    with open("outputs/tables/STANDARD_SCORES_ESPN.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["piece_id", "score"])
        w.writeheader()
        for pid, s in sorted(scores.items(), key=lambda kv: kv[1], reverse=True):
            w.writerow({"piece_id": pid, "score": round(s, 4)})

    random.seed(42)
    fig, ax = plt.subplots(figsize=(11, 10))
    y = [random.random() for _ in scores]
    x = list(scores.values())
    labels = list(scores.keys())
    ax.scatter(x, y, s=60, color="#3B8BD4")
    for xi, yi, label in zip(x, y, labels):
        ax.annotate(label, (xi, yi), textcoords="offset points", xytext=(6, 3), fontsize=8)
    ax.axvline(0, linestyle="--", color="gray")
    ax.set_yticks([])
    ax.set_xlabel("score")
    ax.set_title("ESPN World Cup corpus — articles only, Standard (stopword + plain TF-IDF, whole article)")
    plt.tight_layout()
    plt.savefig("outputs/figures/STANDARD_ARTICLES_ONLY_ESPN.png", dpi=130)
    plt.close()

    import statistics
    vals = list(scores.values())
    print(f"n={len(vals)} mean={statistics.mean(vals):.4f} stdev={statistics.pstdev(vals):.4f} "
          f"range={max(vals)-min(vals):.4f} negative={sum(1 for v in vals if v < 0)}")
    print("Wrote outputs/tables/STANDARD_SCORES_ESPN.csv, outputs/figures/STANDARD_ARTICLES_ONLY_ESPN.png")


if __name__ == "__main__":
    main()
