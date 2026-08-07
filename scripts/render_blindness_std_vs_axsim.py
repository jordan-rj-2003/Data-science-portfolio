"""Axis-similarity vs. Standard baseline only -- mean |cosine to axis| of
each piece's own top-weighted token, across all 44 zones of Corpus A.
Numbers computed fresh from outputs/tables/STANDARD_TOP_TOKENS.csv and
AXSIM_TOP_TOKENS.csv against the credibility axis.
"""

import matplotlib.pyplot as plt

schemes = ["Standard", "Axis-similarity"]
means = [0.1285, 0.3225]
colors = ["#D85A30", "#3B6D11"]

fig, ax = plt.subplots(figsize=(6.5, 5.8))
bars = ax.bar(schemes, means, color=colors, width=0.5)
for bar, val in zip(bars, means):
    ax.text(bar.get_x() + bar.get_width() / 2, val + 0.008, f"{val:.4f}", ha="center", fontsize=11)

ax.set_ylabel("Top token μ cos to the axis")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.set_ylim(0, 0.36)
plt.tight_layout()
plt.savefig("outputs/figures/BLINDNESS_STD_VS_AXSIM.png", dpi=200, bbox_inches="tight")
print("Wrote outputs/figures/BLINDNESS_STD_VS_AXSIM.png")
