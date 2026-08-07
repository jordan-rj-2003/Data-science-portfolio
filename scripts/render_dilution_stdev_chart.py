"""Signal-dilution evidence chart: inter-article separation (stdev) across
every weighting scheme tested on Corpus A (11 articles, mean score per
article across its 4 zones). Numbers reproduced from outputs/CTHRT_COMPARISON.md
"Inter-article separation" table -- no numbers invented here.

The claim: standard TF-IDF-weighted averaging dilutes the signal by
including axis-irrelevant tokens in the average; gating those tokens out
before averaging (threshold-cosine) recovers dramatically more separation.
This chart is the single-glance version of that claim.
"""

import matplotlib.pyplot as plt

# Threshold-cosine here is the statistically-grounded random-baseline pair
# only -- the tuned pair (0.25/0.02) is never used anywhere in this chart
# or script, since it has no mathematical grounding (diagnostic only, per
# spec 006).
variants = [
    "Axis-similarity",
    "Production",
    "Standard",
    "Threshold-cosine\n(random baseline)",
]
stdevs = [0.0141, 0.0176, 0.0222, 0.0396]
colors = ["#B4B2A9"] * 3 + ["#D85A30"]

fig, ax = plt.subplots(figsize=(9, 5.5))
bars = ax.bar(variants, stdevs, color=colors, width=0.6, edgecolor="none")

for bar, val in zip(bars, stdevs):
    ax.text(bar.get_x() + bar.get_width() / 2, val + 0.001, f"{val:.4f}",
             ha="center", va="bottom", fontsize=10)

# annotate the dilution recovery vs the two "no gate" baselines
ax.annotate(
    "+78.4% vs\nStandard",
    xy=(3, 0.0396), xytext=(2.15, 0.032),
    fontsize=9.5, ha="center", color="#712B13",
    arrowprops=dict(arrowstyle="-", color="#712B13", lw=0.8),
)
ax.annotate(
    "+125.0% vs production",
    xy=(3, 0.0396), xytext=(1.35, 0.038),
    fontsize=9.5, ha="center", color="#712B13",
)

ax.set_ylabel("Inter-article score standard deviation\n(mean score per article)")
ax.set_title(
    "Signal dilution recovered by gating: inter-article separation by weighting scheme\n"
    "Credibility axis, Corpus A (11 articles)",
    fontsize=12, fontweight="bold", loc="left", pad=14,
)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.set_ylim(0, 0.05)
ax.tick_params(axis="x", labelsize=9.5)

plt.tight_layout()
plt.savefig("outputs/figures/SIGNAL_DILUTION_STDEV_COMPARISON.png", dpi=200, bbox_inches="tight")
print("Wrote outputs/figures/SIGNAL_DILUTION_STDEV_COMPARISON.png")
