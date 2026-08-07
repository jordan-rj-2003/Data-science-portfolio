"""Balance axis construction word pairs as a PNG table. From
BALANCE_WORDS/UNBALANCE_WORDS, src/axis.py.
"""

import matplotlib.pyplot as plt

headers = ["Balanced", "Unbalanced"]
rows = [
    ["balanced", "unbalanced"],
    ["measured", "exaggerated"],
    ["proportionate", "disproportionate"],
    ["restrained", "sensational"],
    ["even-handed", "one-sided"],
    ["moderate", "extreme"],
    ["calm", "dramatic"],
]

fig, ax = plt.subplots(figsize=(6.5, 0.55 * (len(rows) + 1) + 0.7))
ax.axis("off")
ax.set_title("Balance axis — 7 construction word pairs", fontsize=12, fontweight="bold", loc="left", pad=10)
table = ax.table(cellText=rows, colLabels=headers, cellLoc="center", loc="center", colWidths=[0.5, 0.5])
table.auto_set_font_size(False)
table.set_fontsize(11)
table.scale(1, 2.0)
for (r, c), cell in table.get_celld().items():
    cell.set_edgecolor("#CCCCCC")
    if r == 0:
        cell.set_facecolor("#2C2C2A")
        cell.set_text_props(color="white", fontweight="bold")
    else:
        cell.set_facecolor("#F7F6F2" if r % 2 == 0 else "white")
plt.tight_layout()
plt.savefig("outputs/figures/BALANCE_AXIS_WORDPAIRS_TABLE.png", dpi=200, bbox_inches="tight")
print("Wrote outputs/figures/BALANCE_AXIS_WORDPAIRS_TABLE.png")
