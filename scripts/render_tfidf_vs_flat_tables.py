"""Render the TF-IDF-vs-flat evidence tables (spec 001/002) as PNGs for
dissertation embedding. Data reproduced directly from
outputs/tables/{FLAT,PRODUCTION}_SCORES.csv and
outputs/tables/{FLAT,PRODUCTION}_TOP_TOKENS.csv and
outputs/tables/PROD_vs_FLAT_COMPARISON.csv -- no numbers invented here.
"""

import matplotlib.pyplot as plt

OUT_DIR = "outputs/figures"


def render_table(headers, rows, out_path, title, col_widths=None, highlight_cols=None, fig_w=9, fontsize=10):
    highlight_cols = highlight_cols or []
    n_rows = len(rows) + 1
    n_cols = len(headers)
    fig_h = 0.55 * n_rows + 0.6
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    ax.axis("off")
    ax.set_title(title, fontsize=12, fontweight="bold", pad=14, loc="left")

    table = ax.table(
        cellText=rows,
        colLabels=headers,
        cellLoc="center",
        loc="center",
        colWidths=col_widths,
    )
    table.auto_set_font_size(False)
    table.set_fontsize(fontsize)
    table.scale(1, 1.8)

    for (r, c), cell in table.get_celld().items():
        cell.set_edgecolor("#CCCCCC")
        if r == 0:
            cell.set_facecolor("#2C2C2A")
            cell.set_text_props(color="white", fontweight="bold")
        else:
            cell.set_facecolor("#F7F6F2" if r % 2 == 0 else "white")
            if c in highlight_cols:
                cell.set_text_props(fontweight="bold")

    plt.tight_layout()
    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"Wrote {out_path}")


# 1. Rank-shift summary
render_table(
    headers=["Metric", "Value"],
    rows=[
        ["Mean absolute rank shift (44 pieces)", "4.73 (median 4.0, range 0-18)"],
        ["Pieces unchanged (shift = 0)", "6 / 44"],
        ["Pieces shifting >= 10 ranks", "5 / 44"],
        ["Largest single shift", "A9Z4: rank 25 (TF-IDF) -> rank 7 (flat), shift 18"],
        ["Mean score delta (TF-IDF - flat)", "+0.0055 (stdev 0.0147)"],
        ["Mean |shift| - Headline+Lead", "2.09"],
        ["Mean |shift| - End", "3.18"],
        ["Mean |shift| - Body", "6.82"],
        ["Mean |shift| - Whole", "6.82"],
    ],
    out_path=f"{OUT_DIR}/TFIDF_VS_FLAT_RANKSHIFT_TABLE.png",
    title="TF-IDF vs. flat weighting: rank-shift summary (n=44)",
    col_widths=[0.55, 0.45],
)

# 2. Zone range/ratio
render_table(
    headers=["Zone", "TF-IDF range", "Flat range", "Ratio"],
    rows=[
        ["Headline+Lead", "0.1693", "0.1694", "1.00x"],
        ["Body", "0.0725", "0.0188", "3.86x"],
        ["End", "0.1039", "0.1051", "0.99x"],
        ["Whole", "0.0774", "0.0251", "3.08x"],
    ],
    out_path=f"{OUT_DIR}/TFIDF_VS_FLAT_ZONE_RANGE_TABLE.png",
    title="TF-IDF vs. flat weighting: score range by zone",
    col_widths=[0.3, 0.23, 0.23, 0.24],
    highlight_cols=[3],
)

# 3. Zone stdev, with % change (TF-IDF vs flat) -- flat stdev never crosses
# zero here, so a percentage change is a legitimate magnitude comparison
# (unlike the axis SCORES themselves, which do cross zero -- see Theme 1
# discussion). pct = (tfidf - flat) / flat * 100.
render_table(
    headers=["Zone", "TF-IDF stdev", "Flat stdev", "% change"],
    rows=[
        ["Headline+Lead", "0.0522", "0.0470", "+11.1%"],
        ["Body", "0.0223", "0.0058", "+284.5%"],
        ["End", "0.0293", "0.0312", "-6.1%"],
        ["Whole", "0.0181", "0.0076", "+138.2%"],
        ["Inter-article (mean-per-article)", "0.0176", "0.0153", "+15.0%"],
    ],
    out_path=f"{OUT_DIR}/TFIDF_VS_FLAT_ZONE_STDEV_TABLE.png",
    title="TF-IDF vs. flat weighting: score standard deviation by zone",
    col_widths=[0.4, 0.2, 0.2, 0.2],
    highlight_cols=[3],
)

# 4. Top tokens
render_table(
    headers=["Metric", "Flat (no TF-IDF)", "Production (TF-IDF)"],
    rows=[
        ["Unique top tokens (44 pieces)", "15", "31"],
        ["Agreement (same top token)", "5 / 44", "5 / 44"],
        ["Most frequent top token", '"to" - 14/44 pieces', '"number" - 5/44 pieces'],
        ["Next most frequent",
         '"\'s" (8/44)\n"that" (4/44)',
         '"social", "resolution", "star",\n"points", "suspension" (2/44 each)'],
    ],
    out_path=f"{OUT_DIR}/TFIDF_VS_FLAT_TOP_TOKENS_TABLE.png",
    title="TF-IDF vs. flat weighting: top-weighted token comparison",
    col_widths=[0.24, 0.32, 0.44],
    fig_w=11,
    fontsize=9.5,
)
