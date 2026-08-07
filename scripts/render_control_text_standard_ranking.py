"""Control text (USS Maine, 1898) ranked against the 11 real Corpus A
Whole-zone articles under Standard weighting (stopword removal + plain
TF-IDF) -- joint 12-document corpus, computed fresh this session (see
in-session reproduction). Control text ranks 11th of 12.
"""

import matplotlib.pyplot as plt

rows = [
    ["1", "A5", "0.2855"],
    ["2", "A11", "0.2745"],
    ["3", "A3", "0.2743"],
    ["4", "A6", "0.2719"],
    ["5", "A4", "0.2716"],
    ["6", "A1", "0.2637"],
    ["7", "A7", "0.2592"],
    ["8", "A8", "0.2559"],
    ["9", "A9", "0.2513"],
    ["10", "A10", "0.2462"],
    ["11", "Control (1898)", "0.2379"],
    ["12", "A2", "0.1938"],
]
headers = ["Rank", "Piece", "Score"]

fig, ax = plt.subplots(figsize=(6, 5.2))
ax.axis("off")
ax.set_title("Control text vs. Corpus A, Whole zone — Standard weighting\n(joint 12-document corpus)",
              fontsize=12, fontweight="bold", loc="left", pad=10)
table = ax.table(cellText=rows, colLabels=headers, cellLoc="center", loc="center",
                  colWidths=[0.2, 0.5, 0.3])
table.auto_set_font_size(False)
table.set_fontsize(10.5)
table.scale(1, 1.55)
for (r, c), cell in table.get_celld().items():
    cell.set_edgecolor("#CCCCCC")
    if r == 0:
        cell.set_facecolor("#2C2C2A")
        cell.set_text_props(color="white", fontweight="bold")
    elif rows[r - 1][1] == "Control (1898)":
        cell.set_facecolor("#F0997B")
        cell.set_text_props(fontweight="bold", color="#712B13")
    else:
        cell.set_facecolor("#F7F6F2" if r % 2 == 0 else "white")
plt.tight_layout()
plt.savefig("outputs/figures/CONTROL_TEXT_STANDARD_RANKING.png", dpi=200, bbox_inches="tight")
print("Wrote outputs/figures/CONTROL_TEXT_STANDARD_RANKING.png")
