"""Fixing relevance costs separation -- Standard vs. Axis-similarity,
as a table (real figures + % change), not a bar chart. Standard's stdev
from the four-way pipeline run (stopword removal + plain TF-IDF);
axis-similarity's from outputs/AXSIM_STAN_PROD_COMPARISON.md.
"""

import matplotlib.pyplot as plt

rows = [
    ["Body", "0.0271", "0.0097", "-64.2%"],
    ["Whole", "0.0253", "0.0102", "-59.7%"],
]
headers = ["Zone", "Standard stdev", "Axis-similarity stdev", "% change"]

fig, ax = plt.subplots(figsize=(8.5, 2.6))
ax.axis("off")
ax.set_title("Fixing relevance costs separation: Standard vs. Axis-similarity",
              fontsize=12, fontweight="bold", loc="left", pad=10)
table = ax.table(cellText=rows, colLabels=headers, cellLoc="center", loc="center",
                  colWidths=[0.22, 0.26, 0.30, 0.22])
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
        if c == 3:
            cell.set_text_props(fontweight="bold", color="#712B13")
plt.tight_layout()
plt.savefig("outputs/figures/BLINDNESS_TRADEOFF_TABLE_STD_VS_AXSIM.png", dpi=200, bbox_inches="tight")
print("Wrote outputs/figures/BLINDNESS_TRADEOFF_TABLE_STD_VS_AXSIM.png")
