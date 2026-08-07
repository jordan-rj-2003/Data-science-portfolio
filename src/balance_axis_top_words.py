"""Vocabulary-wide top-20 words scatter + hub-word geometry check for the
balance/one-sidedness axis (spec 010 Addendum, 2026-07-25).

Applies the 2026-07-19 axis-geometry-investigation precedent (credibility
axis: "true"/"consistent" dominated nearest-word matching, then checked
against 500 random common words and found unusually generic/hub-like) to
the new balance axis, using a broad vocabulary scan instead of the
document-nearest-word matching used originally, since the question here
is "which real English words does this axis direction pick out," not
"which axis word matches which document."

Reference vocabulary reused from src/threshold_derivation.py
(build_reference_vocab: top 20000 GloVe words, alphabetic, length > 2)
for consistency with the rest of the project's methodology rather than
introducing a new filter.
"""

import random
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from src.axis import build_balance_axis
from src.glove import get_model
from src.threshold_derivation import SEED, VOCAB_SIZE, build_reference_vocab

HUB_SAMPLE_SIZE = 500


def top_words_on_axis(model, axis, vocab, n=20):
    """Returns (top_positive, top_negative): each a list of (word, score)
    tuples, sorted by score descending (positive) / ascending (negative,
    i.e. most negative first)."""
    axis_2d = axis.reshape(1, -1)
    vocab_matrix = np.array([model[w] for w in vocab])
    norms = np.linalg.norm(vocab_matrix, axis=1, keepdims=True)
    unit_vocab = vocab_matrix / norms
    axis_unit = axis_2d / np.linalg.norm(axis_2d)
    scores = (unit_vocab @ axis_unit.T).flatten()

    order = np.argsort(scores)
    top_negative = [(vocab[i], float(scores[i])) for i in order[:n]]
    top_positive = [(vocab[i], float(scores[i])) for i in order[::-1][:n]]
    return top_positive, top_negative


def nearest_top_word_win_counts(model, top_words, reference_vocab, sample_size=None, seed=SEED):
    """Reproduces the 2026-07-19 credibility-axis hub-word check's actual
    method (nearest-neighbour win tallying across many items), adapted to
    this context: since this analysis has no document corpus to match
    against the balance axis (unlike the original, which matched 44 real
    article pieces to 43 axis words), each word in `reference_vocab`
    (excluding `top_words` themselves, to avoid trivial self-matches)
    stands in as the thing being matched — for each, find which of
    `top_words` it is most cosine-similar to, and tally the wins. A hub
    word wins disproportionately across the whole vocabulary the way
    "true" won for 39/44 documents; an even spread means wins distribute
    roughly evenly across the 40 words instead."""
    pool = [w for w in reference_vocab if w not in top_words]
    if sample_size is not None:
        rng = random.Random(seed)
        pool = rng.sample(pool, sample_size)

    top_matrix = np.array([model[w] for w in top_words])
    top_unit = top_matrix / np.linalg.norm(top_matrix, axis=1, keepdims=True)

    pool_matrix = np.array([model[w] for w in pool])
    pool_unit = pool_matrix / np.linalg.norm(pool_matrix, axis=1, keepdims=True)

    sims = pool_unit @ top_unit.T  # (len(pool), len(top_words))
    winners = np.argmax(sims, axis=1)

    counts = {word: 0 for word in top_words}
    for idx in winners:
        counts[top_words[idx]] += 1

    df = pd.DataFrame({"word": list(counts.keys()), "win_count": list(counts.values())})
    df = df.sort_values("win_count", ascending=False).reset_index(drop=True)
    return df


def build_win_count_chart(win_df, out_path="outputs/figures/BALANCE_AXIS_HUB_WORD_CHECK.png"):
    total_items = win_df["win_count"].sum()
    top2_share = win_df["win_count"].iloc[:2].sum() / total_items
    plt.figure(figsize=(14, 5))
    ax = sns.barplot(data=win_df, x="word", y="win_count", color="tab:blue")
    ax.set_title(
        f"Top 2 words ('{win_df['word'].iloc[0]}', '{win_df['word'].iloc[1]}') take "
        f"{top2_share:.0%} of all {total_items} nearest-neighbour wins across {len(win_df)} words"
    )
    ax.set_xlabel("")
    ax.set_ylabel("Number of vocabulary words this word wins as nearest neighbour")
    plt.xticks(rotation=90, fontsize=8)
    plt.tight_layout()
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=130)
    plt.close()


def build_scatter(top_positive, top_negative, out_path="outputs/figures/BALANCE_AXIS_TOP_WORDS.png"):
    rows = [{"label": w, "score": s, "kind": "balanced pole"} for w, s in top_positive]
    rows += [{"label": w, "score": s, "kind": "unbalanced pole"} for w, s in top_negative]
    df = pd.DataFrame(rows)

    plt.figure(figsize=(12, 14))
    ax = sns.scatterplot(
        data=df,
        x="score",
        y="label",
        hue="kind",
        style="kind",
        palette={"balanced pole": "tab:blue", "unbalanced pole": "tab:orange"},
        markers={"balanced pole": "o", "unbalanced pole": "o"},
        s=90,
    )
    for _, row in df.iterrows():
        ax.annotate(row["label"], (row["score"], row["label"]), xytext=(7, -3), textcoords="offset points", fontsize=8)
    plt.title("Balance/One-Sidedness Axis — top 20 words per pole (vocabulary-wide scan)")
    plt.yticks([])
    plt.ylabel("")
    plt.axvline(0, linestyle="--")
    plt.legend(loc="lower right")
    plt.tight_layout()
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=130)
    plt.close()
    return df


def main():
    model = get_model()
    axis = build_balance_axis(model)
    vocab = build_reference_vocab(model, VOCAB_SIZE)

    top_positive, top_negative = top_words_on_axis(model, axis, vocab, n=20)
    scatter_df = build_scatter(top_positive, top_negative)
    scatter_df.to_csv("outputs/tables/BALANCE_AXIS_TOP_WORDS.csv", index=False)
    print("Wrote outputs/figures/BALANCE_AXIS_TOP_WORDS.png")
    print("Wrote outputs/tables/BALANCE_AXIS_TOP_WORDS.csv")

    all_words = [w for w, _ in top_positive] + [w for w, _ in top_negative]
    win_df = nearest_top_word_win_counts(model, all_words, vocab)
    win_df.to_csv("outputs/tables/BALANCE_AXIS_HUB_WORD_CHECK.csv", index=False)
    build_win_count_chart(win_df)
    print("Wrote outputs/tables/BALANCE_AXIS_HUB_WORD_CHECK.csv")
    print("Wrote outputs/figures/BALANCE_AXIS_HUB_WORD_CHECK.png")
    print()
    print(win_df.to_string(index=False))


if __name__ == "__main__":
    main()
