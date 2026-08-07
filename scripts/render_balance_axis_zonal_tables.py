"""Balance axis, Corpus A, zonal (all 4 zones) -- Production and Standard,
with and without the control text (which only ever appears in Whole,
since it was never zoned). Computed fresh this session -- spec 010's
task 3 (full zonal rebuild) was scoped out, only whole-document was done
before; this fills that gap for these 2 of the originally-planned 7
variants.
"""

import matplotlib.pyplot as plt


def render(headers, rows, title, out_path, col_widths, fig_w=10, highlight_rows=None):
    highlight_rows = highlight_rows or []
    fig, ax = plt.subplots(figsize=(fig_w, 0.5 * (len(rows) + 1) + 0.7))
    ax.axis("off")
    ax.set_title(title, fontsize=12, fontweight="bold", loc="left", pad=10)
    table = ax.table(cellText=rows, colLabels=headers, cellLoc="center", loc="center",
                      colWidths=col_widths)
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.9)
    for (r, c), cell in table.get_celld().items():
        cell.set_edgecolor("#CCCCCC")
        if r == 0:
            cell.set_facecolor("#2C2C2A")
            cell.set_text_props(color="white", fontweight="bold")
        elif r - 1 in highlight_rows:
            cell.set_facecolor("#F0997B")
            cell.set_text_props(fontweight="bold", color="#712B13")
        else:
            cell.set_facecolor("#F7F6F2" if r % 2 == 0 else "white")
    plt.tight_layout()
    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"Wrote {out_path}")


# 1. Zonal stats, Production vs Standard, no control
render(
    headers=["Zone", "Production mean", "stdev", "range", "Standard mean", "stdev", "range"],
    rows=[
        ["Headline+Lead", "-0.0186", "0.0326", "0.1100", "-0.0282", "0.0402", "0.1417"],
        ["Body", "-0.0235", "0.0190", "0.0604", "-0.0327", "0.0242", "0.0724"],
        ["End", "-0.0266", "0.0305", "0.1102", "-0.0377", "0.0371", "0.1584"],
        ["Whole", "-0.0241", "0.0176", "0.0552", "-0.0311", "0.0241", "0.0715"],
    ],
    title="Balance axis, Corpus A — zonal stats, Production vs. Standard (44 pieces, no control)",
    out_path="outputs/figures/BALANCE_AXIS_ZONAL_STATS_TABLE.png",
    col_widths=[0.19, 0.135, 0.11, 0.11, 0.135, 0.11, 0.11],
    fig_w=11,
)

# 2. Production, Whole zone, with control
render(
    headers=["Rank", "Piece", "Score"],
    rows=[
        ["1", "A4", "+0.0057"], ["2", "A8", "+0.0008"], ["3", "A2", "-0.0101"],
        ["4", "A5", "-0.0179"], ["5", "A11", "-0.0201"], ["6", "A10", "-0.0253"],
        ["7", "A9", "-0.0343"], ["8", "A6", "-0.0396"], ["9", "A3", "-0.0406"],
        ["10", "A1", "-0.0424"], ["11", "Control (1898)", "-0.0444"], ["12", "A7", "-0.0466"],
    ],
    title="Balance axis, Production, Whole zone — control text ranked 11th of 12",
    out_path="outputs/figures/BALANCE_AXIS_PROD_WHOLE_CONTROL_TABLE.png",
    col_widths=[0.2, 0.5, 0.3],
    fig_w=6,
    highlight_rows=[10],
)

# 3. Standard, Whole zone, with control
render(
    headers=["Rank", "Piece", "Score"],
    rows=[
        ["1", "A4", "+0.0060"], ["2", "A8", "+0.0027"], ["3", "A11", "-0.0122"],
        ["4", "A2", "-0.0151"], ["5", "A5", "-0.0250"], ["6", "Control (1898)", "-0.0383"],
        ["7", "A10", "-0.0448"], ["8", "A6", "-0.0492"], ["9", "A3", "-0.0496"],
        ["10", "A1", "-0.0505"], ["11", "A9", "-0.0520"], ["12", "A7", "-0.0601"],
    ],
    title="Balance axis, Standard, Whole zone — control text ranked 6th of 12",
    out_path="outputs/figures/BALANCE_AXIS_STAN_WHOLE_CONTROL_TABLE.png",
    col_widths=[0.2, 0.5, 0.3],
    fig_w=6,
    highlight_rows=[5],
)
