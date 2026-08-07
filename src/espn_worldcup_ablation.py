"""Spec 007 — ESPN World Cup corpus, credibility footprint at scale.

Whole-article only (no zone segmentation — see spec 007 CONSTRAINTS: this
corpus's Whole-equivalent robustness under threshold-cosine, per spec 006,
motivated skipping the short zones that were fragile there). Own
independent TF-IDF corpus (53 documents, NOT pooled with the original
11-article corpus, which is untouched). Uses the World Cup-specific
denylist (src/denylist.py WORLD_CUP_DENYLIST_TERMS) via the
denylist_terms parameter added to the preprocessing functions this
session — the original corpus's cached NLP pipeline is unaffected.

Runs both threshold-cosine pairs from spec 006 (tuned 0.25/0.02 and
statistically-principled 0.194/0.096) against the existing large
(21-vs-22-word) axis — unchanged.
"""

import csv
import statistics
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from collections import Counter

from src.axis import CREDIBLE_WORDS, NON_CREDIBLE_WORDS, build_axis, project
from src.axis_weighting import _cosine_similarity_to_axis
from src.compression import EmptyVectorError, compress_corpus
from src.denylist import WORLD_CUP_DENYLIST_TERMS
from src.glove import get_model
from src.naive_baseline import spacy_stopword_set
from src.preprocessing import clean_tokens, clean_tokens_stopword_baseline
from src.tfidf import HIGH_TF_IDF_CAP, HIGH_TF_THRESHOLD, compute_idf, compute_idf_plain

CORPUS_DIR = Path("data/espn_worldcup")

POS_THRESHOLD_TUNED = 0.25
NEG_THRESHOLD_TUNED = 0.02
POS_THRESHOLD_RANDOM_BASELINE = 0.194
NEG_THRESHOLD_RANDOM_BASELINE = 0.096


def load_corpus(corpus_dir=CORPUS_DIR):
    """Returns {"E{n}": raw_text} for every article, whole text (no zone
    split) — matches spec 007's whole-article-only design."""
    pieces = {}
    for path in sorted(corpus_dir.glob("E*.txt"), key=lambda p: int(p.stem[1:])):
        pieces[path.stem] = path.read_text()
    return pieces


def clean_corpus_world_cup(pieces, stopword_set, denylist_terms=WORLD_CUP_DENYLIST_TERMS):
    return {pid: clean_tokens_stopword_baseline(text, stopword_set, denylist_terms=denylist_terms)
            for pid, text in pieces.items()}


def clean_corpus_world_cup_production(pieces, denylist_terms=WORLD_CUP_DENYLIST_TERMS):
    """Production preprocessing (POS-tag filtering, not a stopword list)
    for the ESPN corpus, using the same World Cup-specific denylist as
    clean_corpus_world_cup — matches src.report.run_pipeline's default
    (pos_filter=True) preprocessing on the original 11-article corpus."""
    return {pid: clean_tokens(text, pos_filter=True, denylist_terms=denylist_terms)
            for pid, text in pieces.items()}


def compute_weights_production_flat(pieces):
    """Flat-corpus version of src.tfidf.compute_weights (production's
    continuity-corrected, high-TF-capped TF-IDF).

    compute_weights() groups pieces by zone-type via group_by_zone()
    (piece_id.split("Z")[1]) -- this corpus's "E1"-style piece IDs have no
    zone suffix (spec 007, whole-article only), so that grouping doesn't
    apply and would crash, the same problem already solved for
    threshold-cosine via compute_weights_threshold_cosine_flat above.
    Reimplements the same continuity-correction + high-TF-cap logic
    directly over the single flat 53-document corpus via compute_idf(),
    which itself has no zone-grouping assumption baked in.
    """
    idf = compute_idf(pieces)
    weights = {}
    for piece_id, tokens in pieces.items():
        tf = Counter(tokens)
        piece_weights = {}
        for term, count in tf.items():
            effective_idf = HIGH_TF_IDF_CAP if count > HIGH_TF_THRESHOLD else idf[term]
            piece_weights[term] = count * effective_idf
        weights[piece_id] = piece_weights
    return weights


def run_production_variant(clean_pieces, model, axis):
    """Single-corpus version of production weighting -- no threshold
    gate, no cosine consideration in the weight at all, matching how
    production works on the original 11-article corpus."""
    weights = compute_weights_production_flat(clean_pieces)
    vectors = {}
    empty_pieces = []
    for piece_id, term_weights in weights.items():
        try:
            vectors[piece_id] = compress_corpus({piece_id: term_weights}, model)[piece_id]
        except EmptyVectorError:
            empty_pieces.append(piece_id)
    scores = project(vectors, axis)
    return scores, weights, empty_pieces


def compute_weights_threshold_cosine_flat(pieces, model, axis, pos_threshold, neg_threshold):
    """Flat-corpus version of src.axis_weighting.compute_weights_threshold_cosine.

    The original function calls compute_weights_plain(), which groups
    pieces by zone-type via src.tfidf.group_by_zone() (piece_id.split("Z")[1])
    — this corpus's piece IDs ("E1", "E2", ...) have no zone suffix at
    all, since spec 007 uses whole-article text with no zone
    segmentation, so that grouping doesn't apply and would crash. This
    reimplements the same weighting logic (plain TF-IDF gated by a
    cosine-to-axis threshold) directly over the single flat 53-document
    corpus via compute_idf_plain(), which itself has no zone-grouping
    assumption baked in — rather than force these piece IDs through
    zone-shaped code that doesn't fit them.
    """
    idf = compute_idf_plain(pieces)
    axis_2d = axis.reshape(1, -1)
    weights = {}
    for piece_id, tokens in pieces.items():
        tf = Counter(tokens)
        piece_weights = {}
        for term, count in tf.items():
            tfidf_weight = count * idf[term]
            if term not in model:
                continue
            similarity = _cosine_similarity_to_axis(term, model, axis_2d)
            if similarity > pos_threshold or similarity < -neg_threshold:
                piece_weights[term] = tfidf_weight
        weights[piece_id] = piece_weights
    return weights


def run_threshold_variant(clean_pieces, model, axis, pos_threshold, neg_threshold):
    """Single-corpus version of the threshold-cosine weighting (no
    zone-type grouping needed — one corpus, one document-frequency
    count, unlike the original per-zone-type corpora)."""
    weights = compute_weights_threshold_cosine_flat(clean_pieces, model, axis, pos_threshold, neg_threshold)
    vectors = {}
    empty_pieces = []
    for piece_id, term_weights in weights.items():
        try:
            vectors[piece_id] = compress_corpus({piece_id: term_weights}, model)[piece_id]
        except EmptyVectorError:
            empty_pieces.append(piece_id)
    scores = project(vectors, axis)
    return scores, weights, empty_pieces


def write_scores_table(scores, out_path):
    rows = [{"piece_id": pid, "score": round(s, 4)} for pid, s in
             sorted(scores.items(), key=lambda kv: kv[1], reverse=True)]
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["piece_id", "score"])
        writer.writeheader()
        writer.writerows(rows)
    return rows


def write_top_token_table(weights, out_path):
    rows = []
    for pid, term_weights in weights.items():
        if not term_weights:
            rows.append((pid, None, None))
            continue
        top_term, top_weight = max(term_weights.items(), key=lambda kv: kv[1])
        rows.append((pid, top_term, round(top_weight, 4)))
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["piece_id", "top_token", "weight"])
        w.writerows(rows)
    return rows


def build_axis_chart(model, axis, scores_by_variant, out_path):
    all_words = CREDIBLE_WORDS + NON_CREDIBLE_WORDS
    from sklearn.metrics.pairwise import cosine_similarity
    word_scores = [cosine_similarity([axis], [model[w]])[0][0] for w in all_words]
    df = pd.DataFrame({"label": all_words, "score": word_scores, "kind": "word"})

    palette = {"word": "tab:blue", "tuned": "tab:cyan", "random_baseline": "tab:orange"}
    markers = {"word": "o", "tuned": "*", "random_baseline": "^"}
    for variant_name, scores in scores_by_variant.items():
        for pid, s in scores.items():
            df = pd.concat([df, pd.DataFrame({"label": [pid], "score": [s], "kind": [variant_name]})],
                            ignore_index=True)

    plt.figure(figsize=(12, 20))
    ax = sns.scatterplot(data=df, x="score", y="label", hue="kind", style="kind",
                          palette=palette, markers=markers, s=70)
    plt.title("ESPN World Cup corpus — words + articles, threshold-cosine (whole article, no zone split)")
    plt.yticks(fontsize=6)
    plt.axvline(0, linestyle="--")
    plt.xlim(-0.65, 0.65)
    plt.legend(loc="lower right")
    plt.tight_layout()
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=130)
    plt.close()


def _stats(scores):
    vals = list(scores.values())
    return {
        "n": len(vals),
        "mean": statistics.mean(vals),
        "stdev": statistics.pstdev(vals),
        "min": min(vals),
        "max": max(vals),
        "range": max(vals) - min(vals),
        "n_negative": sum(1 for v in vals if v < 0),
    }


def write_summary(stats_by_variant, empty_by_variant, unique_tokens_by_variant, out_path):
    lines = [
        "# ESPN World Cup corpus (spec 007) — observation only",
        "",
        "Drafted by the Data role (`skills/data/SKILL.md`). 53-article, "
        "single-outlet (ESPN), whole-article (no zone segmentation) corpus "
        "spanning the entire 2022 World Cup (group stage through final), "
        "screened for non-controversial content (see "
        "`data/espn_worldcup/manifest.csv` for inclusion/exclusion "
        "reasoning per candidate article). Own independent TF-IDF "
        "statistics — not pooled with the original 11-article corpus, "
        "which is untouched. Tests whether the credibility footprint found "
        "in spec 006 (real evaluative/hedging vocabulary, real separation) "
        "shows up on a larger, different corpus. This is ESPN's own "
        "article-to-article spread, not a credibility ranking between "
        "outlets. No interpretation of what these figures mean is "
        "included here.",
        "",
    ]
    for variant, stats in stats_by_variant.items():
        lines.append(f"## {variant}")
        lines.append("")
        lines.append(f"- n={stats['n']}, {empty_by_variant[variant]} piece(s) with zero survivors on both poles.")
        lines.append(f"- Mean score: {stats['mean']:.4f}, stdev: {stats['stdev']:.4f}.")
        lines.append(f"- Range: {stats['min']:.4f} to {stats['max']:.4f} (range {stats['range']:.4f}).")
        lines.append(f"- {stats['n_negative']} of {stats['n']} pieces score negative.")
        lines.append(f"- Unique top tokens: {unique_tokens_by_variant[variant]}.")
        lines.append("")
    lines.append("## Comparison against the original 11-article corpus's threshold-cosine figures (spec 006)")
    lines.append("")
    lines.append("| Corpus/variant | Overall stdev | Range |")
    lines.append("|---|---|---|")
    lines.append("| Original corpus, tuned pair | 0.0865 | 0.2871 |")
    lines.append("| Original corpus, random-baseline pair | 0.0396 | 0.1202 |")
    for variant, stats in stats_by_variant.items():
        lines.append(f"| ESPN World Cup corpus, {variant} | {stats['stdev']:.4f} | {stats['range']:.4f} |")
    lines.append("")
    lines.append("No conclusions are drawn from these figures in this document.")

    with open(out_path, "w") as f:
        f.write("\n".join(lines) + "\n")


def main():
    pieces = load_corpus()
    model = get_model()
    axis = build_axis(model)
    stopwords = spacy_stopword_set()
    clean_pieces = clean_corpus_world_cup(pieces, stopwords)

    scores_by_variant = {}
    weights_by_variant = {}
    empty_by_variant = {}
    for label, pos_t, neg_t in [
        ("tuned", POS_THRESHOLD_TUNED, NEG_THRESHOLD_TUNED),
        ("random_baseline", POS_THRESHOLD_RANDOM_BASELINE, NEG_THRESHOLD_RANDOM_BASELINE),
    ]:
        scores, weights, empty = run_threshold_variant(clean_pieces, model, axis, pos_t, neg_t)
        scores_by_variant[label] = scores
        weights_by_variant[label] = weights
        empty_by_variant[label] = len(empty)
        if empty:
            print(f"WARNING [{label}]: {len(empty)} piece(s) empty on both poles: {empty}")
        label_acronym = {"tuned": "CTHRT", "random_baseline": "CTHRR"}[label]
        write_scores_table(scores, f"outputs/tables/{label_acronym}_SCORES_ESPN.csv")
        write_top_token_table(weights, f"outputs/tables/{label_acronym}_TOP_TOKENS_ESPN.csv")

    stats_by_variant = {label: _stats(scores) for label, scores in scores_by_variant.items()}
    unique_tokens_by_variant = {
        label: len({t for w in weights.values() for t in w})
        for label, weights in weights_by_variant.items()
    }

    build_axis_chart(model, axis, scores_by_variant, "outputs/figures/CTHRT_CTHRR_WORDS_AND_DOCUMENTS_ESPN.png")
    write_summary(stats_by_variant, empty_by_variant, unique_tokens_by_variant,
                  "outputs/CTHRT_vs_CTHRR_COMPARISON_ESPN.md")

    for label, stats in stats_by_variant.items():
        print(f"[{label}] n={stats['n']} mean={stats['mean']:.4f} stdev={stats['stdev']:.4f} "
              f"range={stats['range']:.4f} negative={stats['n_negative']}")
    print("Wrote outputs/tables/{CTHRT,CTHRR}_{SCORES,TOP_TOKENS}_ESPN.csv, "
          "outputs/figures/CTHRT_CTHRR_WORDS_AND_DOCUMENTS_ESPN.png, "
          "outputs/CTHRT_vs_CTHRR_COMPARISON_ESPN.md")


if __name__ == "__main__":
    main()
