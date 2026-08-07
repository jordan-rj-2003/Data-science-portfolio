"""Four-way dilution/separability comparison: isolates preprocessing
(POS-filter vs stopword removal) from weighting (flat/no-IDF vs TF-IDF)
as two independent variables, rather than the confounded two-way
flat-vs-production comparison. All numbers computed fresh directly from
the pipeline (src/tfidf.py, src/axis.py, src/compression.py) against the
real 44-piece Corpus A, credibility axis -- see the inline computation
in-session for the exact reproduction.
"""

import matplotlib.pyplot as plt

conditions = [
    "Flat +\nPOS-filter",
    "Flat +\nstopword removal",
    "Standard\n(stopword + plain TF-IDF)",
    "Production\n(POS-filter + corrected TF-IDF)",
]
unique_top = [15, 21, 30, 31]
stdevs = [0.0153, 0.0154, 0.0222, 0.0176]
ranges = [0.1733, 0.1737, 0.1645, 0.1694]
colors = ["#B4B2A9", "#85B7EB", "#F0997B", "#D85A30"]

# --- Table ---
fig, ax = plt.subplots(figsize=(10.5, 3.0))
ax.axis("off")
ax.set_title("Preprocessing vs. weighting: isolating the two variables (Corpus A, n=44)",
              fontsize=12, fontweight="bold", loc="left", pad=10)
headers = ["Condition", "Unique top tokens", "Inter-article stdev", "Range", "Min", "Max"]
rows = [
    ["Flat + POS-filter", "15", "0.0153", "0.1733", "0.1263", "0.2996"],
    ["Flat + stopword removal", "21", "0.0154", "0.1737", "0.1188", "0.2925"],
    ["Standard (stopword + plain TF-IDF)", "30", "0.0222", "0.1645", "0.1235", "0.2880"],
    ["Production (POS-filter + corrected TF-IDF)", "31", "0.0176", "0.1694", "0.1270", "0.2963"],
]
table = ax.table(cellText=rows, colLabels=headers, cellLoc="center", loc="center",
                  colWidths=[0.34, 0.16, 0.16, 0.12, 0.11, 0.11])
table.auto_set_font_size(False)
table.set_fontsize(9.5)
table.scale(1, 1.9)
for (r, c), cell in table.get_celld().items():
    cell.set_edgecolor("#CCCCCC")
    if r == 0:
        cell.set_facecolor("#2C2C2A")
        cell.set_text_props(color="white", fontweight="bold")
    else:
        cell.set_facecolor("#F7F6F2" if r % 2 == 0 else "white")
plt.tight_layout()
plt.savefig("outputs/figures/FOURWAY_DILUTION_TABLE.png", dpi=200, bbox_inches="tight")
plt.close()

# --- Stdev chart ---
fig, ax = plt.subplots(figsize=(8.5, 5.5))
bars = ax.bar(conditions, stdevs, color=colors, width=0.6)
for bar, val in zip(bars, stdevs):
    ax.text(bar.get_x() + bar.get_width() / 2, val + 0.0004, f"{val:.4f}", ha="center", fontsize=10)
ax.set_ylabel("Inter-article score standard deviation\n(mean score per article)")
ax.set_title("Separation by condition: preprocessing alone barely moves it,\nweighting is what separates articles",
              fontsize=12, fontweight="bold", loc="left", pad=14)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.set_ylim(0, 0.026)
ax.tick_params(axis="x", labelsize=9)
plt.tight_layout()
plt.savefig("outputs/figures/FOURWAY_DILUTION_STDEV.png", dpi=200, bbox_inches="tight")
plt.close()

# --- Range chart ---
fig, ax = plt.subplots(figsize=(8.5, 5.5))
bars = ax.bar(conditions, ranges, color=colors, width=0.6)
for bar, val in zip(bars, ranges):
    ax.text(bar.get_x() + bar.get_width() / 2, val + 0.002, f"{val:.4f}", ha="center", fontsize=10)
ax.set_ylabel("Score range (max - min), all 44 pieces")
ax.set_title("Range by condition: all four stay in a similar narrow band\n(range is a weaker discriminator here than stdev)",
              fontsize=12, fontweight="bold", loc="left", pad=14)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.set_ylim(0, 0.21)
ax.tick_params(axis="x", labelsize=9)
plt.tight_layout()
plt.savefig("outputs/figures/FOURWAY_DILUTION_RANGE.png", dpi=200, bbox_inches="tight")
plt.close()

print("Wrote FOURWAY_DILUTION_TABLE.png, FOURWAY_DILUTION_STDEV.png, FOURWAY_DILUTION_RANGE.png")
