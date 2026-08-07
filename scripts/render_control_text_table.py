"""Control text (USS Maine, 1898) vs. real corpus range -- table version,
credibility axis. Numbers from outputs/CONTROL_TEXT_COMPARISON.md (both
weighting schemes that need no shared corpus, so are meaningful for a
lone document).
"""

import matplotlib.pyplot as plt

headers = ["Weighting", "Control text score", "Whole (Z4)\nmin", "max", "mean"]
rows = [
    ["Flat (TF-only)", "0.2379", "0.2390", "0.2641", "0.2546"],
    ["Axis-similarity", "0.3203", "0.3340", "0.3639", "0.3489"],
]

fig, ax = plt.subplots(figsize=(10.5, 2.6))
ax.axis("off")
ax.set_title("Control text vs. real corpus range, credibility axis",
              fontsize=12, fontweight="bold", loc="left", pad=10)
table = ax.table(cellText=rows, colLabels=headers, cellLoc="center", loc="center",
                  colWidths=[0.24, 0.24, 0.18, 0.18, 0.18])
table.auto_set_font_size(False)
table.set_fontsize(10.5)
table.scale(1, 2.1)
for (r, c), cell in table.get_celld().items():
    cell.set_edgecolor("#CCCCCC")
    if r == 0:
        cell.set_facecolor("#2C2C2A")
        cell.set_text_props(color="white", fontweight="bold")
    else:
        cell.set_facecolor("#F7F6F2" if r % 2 == 0 else "white")
        if c == 1:
            cell.set_text_props(fontweight="bold", color="#712B13")
plt.tight_layout()
plt.savefig("outputs/figures/CONTROL_TEXT_COMPARISON_TABLE.png", dpi=200, bbox_inches="tight")
print("Wrote outputs/figures/CONTROL_TEXT_COMPARISON_TABLE.png")
