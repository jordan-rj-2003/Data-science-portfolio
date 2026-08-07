"""Distribution of top-token weight, across article and across zone.

Reads outputs/tables/PRODUCTION_TOP_TOKENS.csv (the highest-weighted token
per piece, production TF-IDF/POS-filtered settings) and plots the weight
distribution grouped by article (n=4 per article) and, separately, by
zone (n=11 per zone). Boxplot + overlaid individual points, since n per
group is small enough that a boxplot alone would hide the real values.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def build_dataframe(table_path="outputs/tables/PRODUCTION_TOP_TOKENS.csv"):
    df = pd.read_csv(table_path)
    df["article_num"] = df["piece_id"].str.split("Z").str[0].str[1:].astype(int)
    df["zone_num"] = df["piece_id"].str.split("Z").str[1].astype(int)
    return df


def _boxplot_with_points(df, x, title, xlabel, out_path):
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.boxplot(df, x=x, y="weight", ax=ax, color="lightsteelblue", fliersize=0)
    sns.stripplot(df, x=x, y="weight", ax=ax, color="black", size=5, jitter=0.15)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Top-token weight")
    fig.tight_layout()
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=130, bbox_inches="tight")
    plt.close(fig)


def plot_by_article(df, out_path="outputs/figures/PRODUCTION_TOP_TOKEN_WEIGHT_BY_ARTICLE.png"):
    _boxplot_with_points(df, "article_num", "Top-token weight distribution by article", "Article", out_path)


def plot_by_zone(df, out_path="outputs/figures/PRODUCTION_TOP_TOKEN_WEIGHT_BY_ZONE.png"):
    _boxplot_with_points(df, "zone_num", "Top-token weight distribution by zone", "Zone", out_path)


def main():
    df = build_dataframe()
    plot_by_article(df)
    plot_by_zone(df)
    print("Wrote outputs/figures/PRODUCTION_TOP_TOKEN_WEIGHT_BY_ARTICLE.png")
    print("Wrote outputs/figures/PRODUCTION_TOP_TOKEN_WEIGHT_BY_ZONE.png")


if __name__ == "__main__":
    main()
