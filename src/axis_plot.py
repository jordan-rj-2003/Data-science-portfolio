"""Word + document axis visualisation, spec 001 WHAT §7.

Ports the student's own `graph()` / `add_document()` sketch from
notebooks/MSC PROJECT.ipynb (cells 108-109) into the pipeline. In the
notebook, `add_document()` was written but never actually called with a
real document vector — this wires it up to the real 44-piece pipeline
instead of leaving it dead code.

One chart per zone-type (Z1-Z4): the same 43 axis words as the notebook's
own word-level plot, plus the 11 real articles' scores for that zone-type
overlaid in a distinct colour/marker so they're easy to pick out against
the word cloud. Documents are labelled "A{n}" only, per the
de-identification scheme (spec 001) — never real outlet names.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.metrics.pairwise import cosine_similarity

from src.axis import CREDIBLE_WORDS, NON_CREDIBLE_WORDS, build_axis
from src.glove import get_model
from src.report import ZONE_NAMES, run_pipeline


def _words_dataframe(axis, model, words=None):
    """Same words, same scoring, same construction order as the notebook's
    own cell 107 — order matters, since graph() below places labels on the
    y-axis in row order, not sorted by score (matching the original).
    Defaults to the large 21-vs-22 axis word list; pass `words` (e.g. the
    small 4-vs-4 axis's own word list) to plot against a different axis."""
    all_words = words if words is not None else CREDIBLE_WORDS + NON_CREDIBLE_WORDS
    scores = [cosine_similarity([axis], [model[word]])[0][0] for word in all_words]
    return pd.DataFrame({"label": all_words, "score": scores, "kind": "word"})


def add_document(df, label, score, kind="document"):
    """Ports the notebook's add_document() (cell 109) — appends one
    document's axis score as a new labelled row via the same concat
    approach, generalised with a `kind` column so it can be told apart
    from axis words (and, optionally, from other document variants) on
    the combined chart. `kind` defaults to "document" for the original
    single-variant use (src/axis_plot.py); pass a variant name (e.g.
    "spacy_baseline") to overlay multiple document sets distinctly."""
    new_row = pd.DataFrame({"label": [label], "score": [score], "kind": [kind]})
    return pd.concat([df, new_row], ignore_index=True)


def graph(df, title, out_path, palette=None, markers=None, xlim=(-0.65, 0.65)):
    """Ports the notebook's graph() (cell 108): scatter + inline
    annotations + dashed zero line + hidden y-axis labels. Extended with a
    `kind` hue/style so document points stand out from axis words. Default
    palette/markers cover the original two kinds ("word"/"document");
    pass custom dicts to support additional document-variant kinds.
    `xlim` defaults to the original fixed (-0.65, 0.65) range every
    existing caller relies on; pass a tighter tuple (or None to let
    matplotlib auto-scale) when a chart's own data sits in a narrower
    band and the fixed range would just add empty margin."""
    if palette is None:
        palette = {"word": "tab:blue", "document": "tab:red"}
    if markers is None:
        markers = {"word": "o", "document": "X"}
    plt.figure(figsize=(12, 14))
    ax = sns.scatterplot(
        data=df,
        x="score",
        y="label",
        hue="kind",
        style="kind",
        palette=palette,
        markers=markers,
        s=90,
    )
    # One annotation per unique label, not per row: in the single-variant
    # case each label is already unique (no behaviour change), but the
    # multi-variant overlay repeats the same label once per kind (e.g.
    # "A1" for production/spaCy/NLTK all landing at nearly the same
    # score) — annotating every row there stamps the same text on top of
    # itself 2-3 times. Placed at the mean score across that label's
    # points so it sits centred on the cluster rather than favouring
    # whichever kind happened to be added first.
    for label, group in df.groupby("label", sort=False):
        mean_score = group["score"].mean()
        ax.annotate(
            label,
            (mean_score, label),
            xytext=(7, -3),
            textcoords="offset points",
            fontsize=8,
        )
    plt.title(title)
    plt.yticks([])
    plt.ylabel("")
    plt.axvline(0, linestyle="--")
    if xlim is not None:
        plt.xlim(*xlim)
    plt.legend(loc="lower right")
    plt.tight_layout()
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=130)
    plt.close()


def _article_num(piece_id):
    return int(piece_id.split("Z")[0][1:])


def build_zone_chart(zone_num, model, axis, doc_scores, out_path):
    df = _words_dataframe(axis, model)
    suffix = f"Z{zone_num}"
    piece_ids = sorted((pid for pid in doc_scores if pid.endswith(suffix)), key=_article_num)
    for piece_id in piece_ids:
        df = add_document(df, piece_id.split("Z")[0], doc_scores[piece_id])
    title = f"Credible Semantic Axis — words + Articles ({ZONE_NAMES[zone_num]})"
    graph(df, title, out_path)


def main():
    model = get_model()
    axis = build_axis(model)
    doc_scores = run_pipeline(weighting="tfidf", pos_filter=True)  # production default
    for zone_num in [1, 2, 3, 4]:
        out_path = f"outputs/figures/PRODUCTION_WORDS_AND_DOCUMENTS_Z{zone_num}.png"
        build_zone_chart(zone_num, model, axis, doc_scores, out_path)
        print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
