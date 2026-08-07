"""Inter-zone separation (stdev) across the four preprocessing/weighting
conditions -- shows the dilution-recovery effect is concentrated in the
long zones (Body, Whole), and even there only responds to weighting, not
preprocessing. Numbers computed fresh from the pipeline, see in-session
reproduction.
"""

import matplotlib.pyplot as plt
import numpy as np

zones = ["Headline+Lead", "Body", "End", "Whole"]
conditions = ["Flat + POS-filter", "Flat + stopword removal",
              "Standard\n(stopword + plain TF-IDF)", "Production\n(POS-filter + corrected TF-IDF)"]
colors = ["#B4B2A9", "#85B7EB", "#F0997B", "#D85A30"]

stdev_by_cond = {
    "Flat + POS-filter": [0.0470, 0.0059, 0.0312, 0.0076],
    "Flat + stopword removal": [0.0448, 0.0064, 0.0295, 0.0093],
    "Standard\n(stopword + plain TF-IDF)": [0.0545, 0.0271, 0.0282, 0.0253],
    "Production\n(POS-filter + corrected TF-IDF)": [0.0523, 0.0223, 0.0293, 0.0181],
}
range_by_cond = {
    "Flat + POS-filter": [0.1694, 0.0189, 0.1051, 0.0251],
    "Flat + stopword removal": [0.1416, 0.0235, 0.1045, 0.0373],
    "Standard\n(stopword + plain TF-IDF)": [0.1524, 0.0853, 0.0960, 0.0988],
    "Production\n(POS-filter + corrected TF-IDF)": [0.1694, 0.0724, 0.1039, 0.0774],
}


def grouped_bar(data, ylabel, title, out_path, ymax):
    x = np.arange(len(zones))
    width = 0.2
    fig, ax = plt.subplots(figsize=(11, 6))
    for i, cond in enumerate(conditions):
        vals = data[cond]
        offset = (i - 1.5) * width
        bars = ax.bar(x + offset, vals, width, color=colors[i], label=cond.replace("\n", " "))
        for b, v in zip(bars, vals):
            ax.text(b.get_x() + b.get_width() / 2, v + ymax * 0.012, f"{v:.3f}",
                     ha="center", fontsize=7.5, rotation=90)
    ax.set_xticks(x)
    ax.set_xticklabels(zones, fontsize=10)
    ax.set_ylabel(ylabel)
    ax.set_title(title, fontsize=12, fontweight="bold", loc="left", pad=14)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_ylim(0, ymax)
    ax.legend(fontsize=8.5, frameon=False, loc="upper left", ncol=2)
    plt.tight_layout()
    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close()


grouped_bar(
    stdev_by_cond,
    "Score standard deviation, within zone",
    "Inter-zone separation by condition: the gain is concentrated in\nBody and Whole, and only when weighting (not preprocessing) is added",
    "outputs/figures/ZONE_DILUTION_STDEV.png",
    ymax=0.065,
)

grouped_bar(
    range_by_cond,
    "Score range (max - min), within zone",
    "Inter-zone range by condition: Body and Whole again show the\nlargest gap between flat and weighted conditions",
    "outputs/figures/ZONE_DILUTION_RANGE.png",
    ymax=0.20,
)

print("Wrote ZONE_DILUTION_STDEV.png, ZONE_DILUTION_RANGE.png")
