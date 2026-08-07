"""Standard weighting: inter-zone stdev, credibility axis vs. balance
axis, Corpus A (44 pieces, no control). Credibility numbers from the
four-way dilution analysis; balance numbers computed fresh this session.
"""

import matplotlib.pyplot as plt

headers = ["Zone", "Credibility axis stdev", "Balance axis stdev"]
rows = [
    ["Headline+Lead", "0.0545", "0.0402"],
    ["Body", "0.0271", "0.0242"],
    ["End", "0.0282", "0.0371"],
    ["Whole", "0.0253", "0.0241"],
]

fig, ax = plt.subplots(figsize=(8.5, 3.0))
ax.axis("off")
ax.set_title("Standard weighting — inter-zone stdev, credibility axis vs. balance axis",
              fontsize=12, fontweight="bold", loc="left", pad=10)
table = ax.table(cellText=rows, colLabels=headers, cellLoc="center", loc="center",
                  colWidths=[0.34, 0.33, 0.33])
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
plt.tight_layout()
plt.savefig("outputs/figures/STANDARD_CRED_VS_BAL_STDEV_TABLE.png", dpi=200, bbox_inches="tight")
print("Wrote outputs/figures/STANDARD_CRED_VS_BAL_STDEV_TABLE.png")
