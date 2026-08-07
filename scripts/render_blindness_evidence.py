"""TF-IDF context-blindness to axis relevance -- evidence set.
Numbers: mean/median |cosine to axis| of each scheme's own per-piece top
token (computed fresh, see in-session reproduction), plus the qualitative
top-token samples and separation trade-off already on record in
outputs/AXSIM_STAN_PROD_COMPARISON.md and outputs/CTHRT_COMPARISON.md.
"""

import matplotlib.pyplot as plt

# --- 1. Bar chart: mean |cos to axis| of top token, by scheme ---
# Threshold-cosine here is the statistically-grounded random-baseline pair
# (5th/95th percentile of a 1000-word null distribution) -- the tuned pair
# is deliberately excluded throughout this evidence set, since it has no
# mathematical grounding (diagnostic only, per spec 006).
schemes = ["Production\n(TF-IDF)", "Threshold-cosine\n(random baseline)", "Axis-similarity\n(pure relevance)"]
means = [0.1429, 0.2119, 0.3225]
near_orth = [11, 0, 0]  # count of 44 with |cos| < 0.1
colors = ["#D85A30", "#F0997B", "#3B6D11"]

fig, ax = plt.subplots(figsize=(9, 5.8))
bars = ax.bar(schemes, means, color=colors, width=0.55)
for bar, val, n in zip(bars, means, near_orth):
    ax.text(bar.get_x() + bar.get_width() / 2, val + 0.008, f"{val:.4f}",
             ha="center", fontsize=11)
    ax.text(bar.get_x() + bar.get_width() / 2, val - 0.02, f"{n}/44 near-orthogonal\n(|cos| < 0.1)",
             ha="center", fontsize=8.5, color="white", va="top")
ax.set_ylabel("Mean |cosine similarity to axis|\nof each piece's own top-weighted token")
ax.set_title(
    "Gating narrows the relevance gap but doesn't close it --\nsurvivors are still ranked by rarity, not by margin above threshold",
    fontsize=12, fontweight="bold", loc="left", pad=14,
)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.set_ylim(0, 0.38)
plt.tight_layout()
plt.savefig("outputs/figures/BLINDNESS_TOPTOKEN_COSINE.png", dpi=200, bbox_inches="tight")
plt.close()

# --- 2. Stats table ---
fig, ax = plt.subplots(figsize=(10, 3.0))
ax.axis("off")
ax.set_title("Per-piece top token: relevance-to-axis statistics (n=44)",
              fontsize=12, fontweight="bold", loc="left", pad=10)
rows = [
    ["Production (TF-IDF)", "0.1429", "0.1431", "0.0131 / 0.3993", "11/44 (25%)"],
    ["Threshold-cosine (random baseline)", "0.2119", "0.2157", "0.1051 / 0.3993", "0/44 (0%)"],
    ["Axis-similarity (pure relevance)", "0.3225", "0.3447", "0.2049 / 0.4352", "0/44 (0%)"],
]
headers = ["Scheme", "Mean |cos|", "Median |cos|", "Min / Max |cos|", "Near-orthogonal (|cos|<0.1)"]
table = ax.table(cellText=rows, colLabels=headers, cellLoc="center", loc="center",
                  colWidths=[0.30, 0.13, 0.14, 0.20, 0.23])
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
plt.savefig("outputs/figures/BLINDNESS_STATS_TABLE.png", dpi=200, bbox_inches="tight")
plt.close()

# --- 3. Qualitative examples table ---
fig, ax = plt.subplots(figsize=(11, 3.6))
ax.axis("off")
ax.set_title("Representative top-weighted tokens by scheme",
              fontsize=12, fontweight="bold", loc="left", pad=10)
rows = [
    ["Production\n(TF-IDF)", "number, resolution, mr., star,\npoints, social, suspension"],
    ["Threshold-cosine\n(random baseline)", "instance, reaching, think, furious,\nstatements, day, view, profile, allegedly"],
    ["Axis-similarity\n(pure relevance)", "able, provide, determined,\nimmediate"],
]
headers = ["Scheme", "Sample top tokens"]
table = ax.table(cellText=rows, colLabels=headers, cellLoc="center", loc="center",
                  colWidths=[0.25, 0.75])
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1, 2.6)
for (r, c), cell in table.get_celld().items():
    cell.set_edgecolor("#CCCCCC")
    if r == 0:
        cell.set_facecolor("#2C2C2A")
        cell.set_text_props(color="white", fontweight="bold")
    else:
        cell.set_facecolor("#F7F6F2" if r % 2 == 0 else "white")
plt.tight_layout()
plt.savefig("outputs/figures/BLINDNESS_EXAMPLES_TABLE.png", dpi=200, bbox_inches="tight")
plt.close()

# --- 4. Separation trade-off: relevance vs. separation ---
fig, ax = plt.subplots(figsize=(8.5, 5.5))
zones = ["Body", "Whole"]
prod_std = [0.0223, 0.0181]
axsim_std = [0.0097, 0.0102]
x = range(len(zones))
width = 0.32
bars1 = ax.bar([i - width/2 for i in x], prod_std, width, color="#D85A30", label="Production (TF-IDF)")
bars2 = ax.bar([i + width/2 for i in x], axsim_std, width, color="#3B6D11", label="Axis-similarity (pure relevance)")
for bars in (bars1, bars2):
    for b in bars:
        ax.text(b.get_x() + b.get_width()/2, b.get_height() + 0.0006, f"{b.get_height():.4f}",
                 ha="center", fontsize=9.5)
ax.set_xticks(list(x))
ax.set_xticklabels(zones, fontsize=11)
ax.set_ylabel("Inter-article score standard deviation")
ax.set_title("Fixing relevance costs separation: axis-similarity's more\nrelevant top tokens still separate articles worse than TF-IDF's",
              fontsize=12, fontweight="bold", loc="left", pad=14)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.legend(fontsize=9.5, frameon=False)
ax.set_ylim(0, 0.028)
plt.tight_layout()
plt.savefig("outputs/figures/BLINDNESS_SEPARATION_TRADEOFF.png", dpi=200, bbox_inches="tight")
plt.close()

print("Wrote BLINDNESS_TOPTOKEN_COSINE.png, BLINDNESS_STATS_TABLE.png, BLINDNESS_EXAMPLES_TABLE.png, BLINDNESS_SEPARATION_TRADEOFF.png")
