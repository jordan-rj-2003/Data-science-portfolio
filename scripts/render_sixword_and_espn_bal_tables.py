"""Two balance-axis tables as PNGs: (1) the six-word hyperbole test,
(2) the ESPN (Corpus B) rebuild results, all three weighting variants.
Numbers from key-findings.md, 2026-07-25/07-26 entries.
"""

import matplotlib.pyplot as plt


def render(headers, rows, title, out_path, col_widths, fig_w=9, highlight_col=None):
    fig, ax = plt.subplots(figsize=(fig_w, 0.55 * (len(rows) + 1) + 0.7))
    ax.axis("off")
    ax.set_title(title, fontsize=12, fontweight="bold", loc="left", pad=10)
    table = ax.table(cellText=rows, colLabels=headers, cellLoc="center", loc="center",
                      colWidths=col_widths)
    table.auto_set_font_size(False)
    table.set_fontsize(10.5)
    table.scale(1, 2.0)
    for (r, c), cell in table.get_celld().items():
        cell.set_edgecolor("#CCCCCC")
        if r == 0:
            cell.set_facecolor("#2C2C2A")
            cell.set_text_props(color="white", fontweight="bold")
        else:
            cell.set_facecolor("#F7F6F2" if r % 2 == 0 else "white")
            if highlight_col is not None and c == highlight_col:
                cell.set_text_props(fontweight="bold", color="#712B13")
    plt.tight_layout()
    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"Wrote {out_path}")


# 1. Six-word hyperbole test
render(
    headers=["Word", "Credibility axis", "Balance axis"],
    rows=[
        ["amazing", "+0.1347 (reads credible)", "-0.1913"],
        ["stunning", "+0.0804 (reads credible)", "-0.1557"],
        ["incredible", "+0.0118", "-0.2440"],
        ["unbelievable", "-0.1240", "-0.3017"],
        ["shocking", "-0.1212", "-0.3439"],
        ["outrageous", "-0.3522", "-0.3990"],
    ],
    title="Six-word hyperbole test: credibility axis vs. balance axis",
    out_path="outputs/figures/SIXWORD_HYPERBOLE_TEST_TABLE.png",
    col_widths=[0.28, 0.4, 0.32],
)

# 2. ESPN (Corpus B) balance-axis rebuild
render(
    headers=["Variant", "Mean", "Stdev", "Range", "Negative-scoring"],
    rows=[
        ["Standard", "-0.0345", "0.0310", "0.1556", "47/53"],
        ["Production", "-0.0292", "0.0268", "0.1417", "47/53"],
        ["Threshold-cosine", "-0.0200", "0.1386", "0.5433", "29/53"],
    ],
    title="ESPN corpus (Corpus B), balance axis — all 3 weighting variants",
    out_path="outputs/figures/ESPN_BALANCE_AXIS_REBUILD_TABLE.png",
    col_widths=[0.26, 0.18, 0.18, 0.18, 0.2],
    highlight_col=2,
)
