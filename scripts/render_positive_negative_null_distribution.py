"""Null distribution of the same 1000-word reference sample (seed 42,
matching src/threshold_derivation.py exactly) projected onto a
constructed (positive - negative) axis, single antonym pair, same
grouped-pairs convention as build_axis/build_small_axis. Comparison
point for the credibility axis's own null distribution (pos/neg ratio
2.27) -- this one comes out at 0.95, i.e. near-symmetric.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import random

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from src.glove import get_model
from src.threshold_derivation import SAMPLE_SIZE, SEED, VOCAB_SIZE, build_reference_vocab

model = get_model()
vocab = build_reference_vocab(model, VOCAB_SIZE)
random.seed(SEED)
sample = random.sample(vocab, SAMPLE_SIZE)

pos_vec = model["positive"] / np.linalg.norm(model["positive"])
neg_vec = model["negative"] / np.linalg.norm(model["negative"])
pn_axis_unit = (pos_vec - neg_vec) / np.linalg.norm(pos_vec - neg_vec)

proj = np.array([np.dot(model[w] / np.linalg.norm(model[w]), pn_axis_unit) for w in sample])
p5, p95 = np.percentile(proj, 5), np.percentile(proj, 95)

fig, ax = plt.subplots(figsize=(8, 5.5))
sns.histplot(proj, stat="density", bins=40, color="#378ADD", alpha=0.55, ax=ax)
sns.kdeplot(proj, color="#185FA5", linewidth=1.8, ax=ax)
ax.axvline(0, linestyle=":", color="gray", linewidth=1)
ax.axvline(p5, linestyle="--", color="#A32D2D", linewidth=1.3, label=f"5th pct ({p5:.4f})")
ax.axvline(p95, linestyle="--", color="#3B6D11", linewidth=1.3, label=f"95th pct ({p95:.4f})")
ax.set_xlabel("Cosine similarity to (positive − negative) axis")
ax.set_ylabel("Density")
ax.set_title(
    "Null distribution: 1000-word reference sample on a\n"
    "constructed positive/negative axis (pos/neg ratio 0.95 — near-symmetric)",
    fontsize=12, fontweight="bold", loc="left", pad=14,
)
ax.legend(fontsize=9.5, frameon=False)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
plt.tight_layout()
plt.savefig("outputs/figures/POSITIVE_NEGATIVE_NULL_DISTRIBUTION.png", dpi=200, bbox_inches="tight")
print(f"mean={proj.mean():.4f} median={np.median(proj):.4f} p5={p5:.4f} p95={p95:.4f}")
print("Wrote outputs/figures/POSITIVE_NEGATIVE_NULL_DISTRIBUTION.png")
