"""Control text (USS Maine, 1898) plotted among the credibility axis's
own word cluster and the real 11-article Whole-zone scores -- same house
style as src/axis_plot.py's existing word+document charts. Flat (TF-only)
weighting throughout, matching src/control_text_check.py's own validated
methodology (the only weighting scheme that needs no shared corpus, so
it's meaningful for a lone document without touching the real corpus's
IDF statistics).
"""

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.axis import build_axis
from src.axis_plot import _words_dataframe, add_document, graph
from src.control_text_check import run as run_control_flat
from src.glove import get_model

model = get_model()
axis = build_axis(model)

df = _words_dataframe(axis, model)

# 11 real articles, Whole (Z4), flat weighting -- same source as
# outputs/CONTROL_TEXT_COMPARISON.md's own comparison range.
with open("outputs/tables/FLAT_SCORES.csv") as f:
    for row in csv.DictReader(f):
        if row["zone"] == "Whole":
            df = add_document(df, row["article"], float(row["score"]), kind="article")

control_large_score, control_small_score, n_tokens, _ = run_control_flat()
df = add_document(df, "Control (1898)", control_large_score, kind="control")

palette = {"word": "tab:blue", "article": "tab:green", "control": "tab:red"}
markers = {"word": "o", "article": "s", "control": "X"}

graph(
    df,
    "Credibility axis — words + Corpus A (Whole, flat weighting) + control text",
    "outputs/figures/CONTROL_TEXT_CREDIBILITY_CLUSTER.png",
    palette=palette,
    markers=markers,
)
print(f"Control text large-axis score: {control_large_score:.4f}")
print("Wrote outputs/figures/CONTROL_TEXT_CREDIBILITY_CLUSTER.png")
