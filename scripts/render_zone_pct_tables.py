"""Zone-level percentage-change tables (replaces the grouped bar chart
version) -- % change vs. "Flat + POS-filter" baseline, per zone, for
stdev and range. Numbers reproduced from the same pipeline run as
render_zone_dilution.py.
"""

import matplotlib.pyplot as plt

zones = ["Headline+Lead", "Body", "End", "Whole"]
cols = ["Flat + stopword\nremoval", "Standard\n(stopword + plain TF-IDF)", "Production\n(POS-filter + corrected TF-IDF)"]
cols_weighted_only = ["Standard\n(stopword + plain TF-IDF)", "Production\n(POS-filter + corrected TF-IDF)"]

stdev_pct = {
    "Headline+Lead": [-4.7, 16.0, 11.3],
    "Body": [8.5, 359.3, 278.0],
    "End": [-5.4, -9.6, -6.1],
    "Whole": [22.4, 232.9, 138.2],
}
stdev_pct_weighted_only = {z: v[1:] for z, v in stdev_pct.items()}
range_pct = {
    "Headline+Lead": [-16.4, -10.0, 0.0],
    "Body": [24.3, 351.3, 283.1],
    "End": [-0.6, -8.7, -1.1],
    "Whole": [48.6, 293.6, 208.4],
}


def render(data, title, out_path, cols=cols, col_widths=None):
    rows = [[zone] + [f"{v:+.1f}%" for v in data[zone]] for zone in zones]
    n_cols = len(cols) + 1
    if col_widths is None:
        col_widths = [0.22] + [0.78 / (n_cols - 1)] * (n_cols - 1)
    fig, ax = plt.subplots(figsize=(10 if n_cols > 3 else 8, 3.0))
    ax.axis("off")
    ax.set_title(title, fontsize=12, fontweight="bold", loc="left", pad=10)
    table = ax.table(cellText=rows, colLabels=["Zone"] + cols, cellLoc="center",
                      loc="center", colWidths=col_widths)
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2.0)
    for (r, c), cell in table.get_celld().items():
        cell.set_edgecolor("#CCCCCC")
        if r == 0:
            cell.set_facecolor("#2C2C2A")
            cell.set_text_props(color="white", fontweight="bold")
        else:
            cell.set_facecolor("#F7F6F2" if r % 2 == 0 else "white")
            if c > 0:
                val = data[zones[r - 1]][c - 1]
                if val >= 50:
                    cell.set_text_props(fontweight="bold", color="#712B13")
    plt.tight_layout()
    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"Wrote {out_path}")


render(
    stdev_pct_weighted_only,
    "Inter-zone separation: % stdev increase from unweighted",
    "outputs/figures/ZONE_DILUTION_STDEV_PCT_TABLE.png",
    cols=cols_weighted_only,
    col_widths=[0.28, 0.36, 0.36],
)
render(
    range_pct,
    "Inter-zone range: % change in range vs. Flat + POS-filter baseline",
    "outputs/figures/ZONE_DILUTION_RANGE_PCT_TABLE.png",
)
