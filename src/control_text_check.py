"""Control-text sanity check: does a known non-credible/propagandistic
piece of journalism score differently on the credibility axis than the
production 11-article corpus?

Uses flat (TF-only, no IDF) weighting deliberately: the control text is a
single document with no corpus of its own, so there's no valid
document-frequency statistic to compute IDF against (joining it into the
real 11-article corpus would change that corpus's own IDF values, which
we don't want to touch). Flat weighting needs no corpus at all — see
src/tfidf.py compute_flat_weights — making it the only one of this
project's three main weighting schemes that's meaningful for a lone
document, and it isolates exactly the question this check is about:
whether ordinary weighted-average vocabulary content alone lands positive
on this axis, independent of any TF-IDF corpus-relative rarity effects.

Not zone-segmented (headline+lead/body/end/whole): the control text is
~300 words with Hearst-era multi-deck sub-headlines rather than uniform
prose paragraphs, so it's treated as one whole-document score, compared
against the production corpus's own flat-weighted Whole (Z4) scores —
see outputs/tables/FLAT_SCORES.csv.
"""

import csv

from src.axis import build_axis, build_small_axis, project
from src.axis_weighting import compute_weights_axis_similarity
from src.compression import compress_corpus
from src.glove import get_model
from src.naive_baseline import spacy_stopword_set
from src.preprocessing import clean_tokens, clean_tokens_stopword_baseline
from src.tfidf import compute_flat_weights

CONTROL_PATH = "data/control/uss_maine_1898.txt"


def load_control_text(path=CONTROL_PATH):
    with open(path) as f:
        return f.read()


def run():
    text = load_control_text()
    model = get_model()
    tokens = clean_tokens(text, pos_filter=True)
    weights = compute_flat_weights({"control_uss_maine_1898": tokens})
    vectors = compress_corpus(weights, model)

    large_axis = build_axis(model)
    small_axis = build_small_axis(model)
    large_score = project(vectors, large_axis)["control_uss_maine_1898"]
    small_score = project(vectors, small_axis)["control_uss_maine_1898"]

    return large_score, small_score, len(tokens), weights["control_uss_maine_1898"]


def run_axis_similarity(model, large_axis, small_axis):
    """Axis-similarity weighting (weight = abs(cosine_similarity(word,
    axis)), spec 003 Phase 1) needs no corpus at all — each token's weight
    depends only on the word itself and the fixed axis vector — so, like
    flat weighting, it's directly applicable to a lone document without
    touching the real 11-article corpus's stats. Uses spaCy-stopword
    preprocessing, matching how this weighting scheme is run everywhere
    else in this project (src/axis_similarity_ablation.py)."""
    text = load_control_text()
    tokens = clean_tokens_stopword_baseline(text, spacy_stopword_set())

    large_weights = compute_weights_axis_similarity({"control_uss_maine_1898": tokens}, model, large_axis)
    large_vectors = compress_corpus(large_weights, model)
    large_score = project(large_vectors, large_axis)["control_uss_maine_1898"]

    small_weights = compute_weights_axis_similarity({"control_uss_maine_1898": tokens}, model, small_axis)
    small_vectors = compress_corpus(small_weights, model)
    small_score = project(small_vectors, small_axis)["control_uss_maine_1898"]

    return large_score, small_score, len(tokens), large_weights["control_uss_maine_1898"]


def _read_whole_zone_scores(path, score_col):
    scores = []
    with open(path) as f:
        for row in csv.DictReader(f):
            if row["zone"] == "Whole":
                scores.append(float(row[score_col]))
    return scores


def _range_str(scores):
    return (f"min {min(scores):.4f}, max {max(scores):.4f}, "
            f"mean {sum(scores)/len(scores):.4f}")


def write_summary(flat_result, axis_sim_result, flat_whole_scores, axis_sim_whole_scores, out_path):
    flat_large, flat_small, flat_n, flat_top = flat_result
    sim_large, sim_small, sim_n, sim_top = axis_sim_result
    flat_top5 = sorted(flat_top.items(), key=lambda kv: kv[1], reverse=True)[:5]
    sim_top5 = sorted(sim_top.items(), key=lambda kv: kv[1], reverse=True)[:5]
    lines = [
        "# Control text (USS Maine, 1898) vs. production corpus — observation only",
        "",
        "Drafted by the Data role (`skills/data/SKILL.md`). Runs a single known "
        "non-credible/propagandistic piece of journalism (see "
        "`data/control/SOURCE.md`) through two weighting schemes that need no "
        "shared corpus — flat/TF-only, and axis-similarity "
        "(weight = abs(cosine_similarity(word, axis)), spec 003 Phase 1) — so "
        "neither touches the real 11-article corpus's own statistics. Each is "
        "projected onto both the large (21-vs-22) and small (4-vs-4) axis. No "
        "interpretation of what these figures mean is included here.",
        "",
        "## Flat (TF-only) weighting",
        "",
        f"- Surviving tokens after preprocessing: {flat_n}.",
        f"- Large-axis score: {flat_large:.4f}. Small-axis score: {flat_small:.4f}.",
        f"- Production corpus's own flat-weighted Whole (Z4) scores, large axis, "
        f"for comparison (n={len(flat_whole_scores)}): {_range_str(flat_whole_scores)}.",
        "- Top 5 highest-weighted surviving tokens: "
        + ", ".join(f"{t} ({w:.2f})" for t, w in flat_top5) + ".",
        "",
        "## Axis-similarity weighting",
        "",
        f"- Surviving tokens after preprocessing: {sim_n}.",
        f"- Large-axis score: {sim_large:.4f}. Small-axis score: {sim_small:.4f}.",
        f"- Production corpus's own axis-similarity-weighted Whole (Z4) scores, "
        f"large axis, for comparison (n={len(axis_sim_whole_scores)}): "
        f"{_range_str(axis_sim_whole_scores)}.",
        "- Top 5 highest-weighted surviving tokens: "
        + ", ".join(f"{t} ({w:.4f})" for t, w in sim_top5) + ".",
        "",
        "No conclusions are drawn from these figures in this document.",
    ]
    with open(out_path, "w") as f:
        f.write("\n".join(lines) + "\n")


def main():
    model = get_model()
    large_axis = build_axis(model)
    small_axis = build_small_axis(model)

    flat_result = run()
    axis_sim_result = run_axis_similarity(model, large_axis, small_axis)

    flat_whole_scores = _read_whole_zone_scores(
        "outputs/tables/FLAT_SCORES.csv", "score"
    )
    axis_sim_whole_scores = _read_whole_zone_scores(
        "outputs/tables/AXSIM_vs_PROD_COMPARISON.csv", "axis_similarity_score"
    )

    write_summary(flat_result, axis_sim_result, flat_whole_scores, axis_sim_whole_scores,
                  "outputs/CONTROL_TEXT_COMPARISON.md")

    print(f"[flat] large-axis: {flat_result[0]:.4f}, small-axis: {flat_result[1]:.4f}, "
          f"production Whole range: {min(flat_whole_scores):.4f}-{max(flat_whole_scores):.4f}")
    print(f"[axis_similarity] large-axis: {axis_sim_result[0]:.4f}, small-axis: {axis_sim_result[1]:.4f}, "
          f"production Whole range: {min(axis_sim_whole_scores):.4f}-{max(axis_sim_whole_scores):.4f}")
    print("Wrote outputs/CONTROL_TEXT_COMPARISON.md")


if __name__ == "__main__":
    main()
