"""Control-text (USS Maine, 1898) check under the new balance axis (spec
010 task 5). Combines the two existing credibility-axis control-text
checks' methods -- src/control_text_check.py (flat + axis-similarity
weighting) and src/control_text_threshold_check.py (threshold-cosine
weighting) -- against the balance axis instead, since neither
compute_weights_axis_similarity nor compute_weights_threshold_cosine is
axis-specific (spec 010 CONSTRAINTS: no new weighting formulas, only the
axis vector changes).

The original 11-article corpus hasn't been rebuilt against the balance
axis yet (spec 010 task 3, not started) -- rather than pre-empting or
duplicating that full rebuild, this computes just enough of a comparison
point itself: flat and axis-similarity weighted balance-axis scores for
the 11 articles' Whole (Z4) pieces (same technique as
control_text_check.py), and the same temporary 12-document
threshold-cosine corpus construction as control_text_threshold_check.py.
Neither the credibility-axis control-text outputs nor the original
corpus's saved statistics are modified or re-run differently than before.
"""

import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

from src.axis import BALANCE_WORDS, UNBALANCE_WORDS, build_balance_axis, project
from src.axis_plot import graph
from src.axis_weighting import compute_weights_axis_similarity, compute_weights_threshold_cosine
from src.compression import EmptyVectorError, compress_corpus
from src.glove import get_model
from src.naive_baseline import spacy_stopword_set
from src.preprocessing import clean_tokens, clean_tokens_stopword_baseline
from src.segmentation import segment_corpus
from src.tfidf import compute_flat_weights
from src.threshold_derivation import derive_thresholds

CONTROL_PATH = "data/control/uss_maine_1898.txt"
CONTROL_ID = "controlZ4"
ARTICLE_IDS = [f"A{i}" for i in range(1, 12)]


def load_control_text(path=CONTROL_PATH):
    with open(path) as f:
        return f.read()


def _whole_zone_pieces(raw_dir="data/raw", article_ids=ARTICLE_IDS):
    raw_pieces = segment_corpus(raw_dir, article_ids)
    return {pid: text for pid, text in raw_pieces.items() if pid.endswith("Z4")}


def run_flat(model, axis):
    """Flat (TF-only) weighting -- needs no corpus, matches
    control_text_check.py's method exactly, axis swapped to balance."""
    control_tokens = clean_tokens(load_control_text(), pos_filter=True)
    whole_pieces = _whole_zone_pieces()
    whole_tokens = {pid: clean_tokens(text, pos_filter=True) for pid, text in whole_pieces.items()}

    all_pieces = dict(whole_tokens)
    all_pieces[CONTROL_ID] = control_tokens
    weights = compute_flat_weights(all_pieces)
    vectors = compress_corpus(weights, model)
    scores = project(vectors, axis)

    control_score = scores.pop(CONTROL_ID)
    top5 = sorted(weights[CONTROL_ID].items(), key=lambda kv: kv[1], reverse=True)[:5]
    return {
        "score": control_score,
        "n_survivors": len(control_tokens),
        "top5": top5,
        "whole_zone_scores": scores,
    }


def run_axis_similarity(model, axis):
    """Axis-similarity weighting -- needs no corpus, matches
    control_text_check.py's method exactly, axis swapped to balance."""
    control_tokens = clean_tokens_stopword_baseline(load_control_text(), spacy_stopword_set())
    whole_pieces = _whole_zone_pieces()
    whole_tokens = {pid: clean_tokens_stopword_baseline(text, spacy_stopword_set())
                    for pid, text in whole_pieces.items()}

    all_pieces = dict(whole_tokens)
    all_pieces[CONTROL_ID] = control_tokens
    weights = compute_weights_axis_similarity(all_pieces, model, axis)
    vectors = compress_corpus(weights, model)
    scores = project(vectors, axis)

    control_score = scores.pop(CONTROL_ID)
    top5 = sorted(weights[CONTROL_ID].items(), key=lambda kv: kv[1], reverse=True)[:5]
    return {
        "score": control_score,
        "n_survivors": len(control_tokens),
        "top5": top5,
        "whole_zone_scores": scores,
    }


def run_threshold_cosine(model, axis, pos_threshold, neg_threshold):
    """Threshold-cosine weighting -- builds the same temporary 12-document
    corpus as control_text_threshold_check.py (11 real Whole/Z4 pieces +
    control, grouped as zone 4 via the "controlZ4" id) so IDF has a real
    document-frequency statistic to compute against, without touching the
    real corpus's own saved TF-IDF statistics. Axis swapped to balance,
    threshold pair swapped to this axis's own derived pair (spec 010 task 2)."""
    stopwords = spacy_stopword_set()
    whole_pieces = _whole_zone_pieces()
    clean_pieces = {pid: clean_tokens_stopword_baseline(text, stopwords) for pid, text in whole_pieces.items()}
    clean_pieces[CONTROL_ID] = clean_tokens_stopword_baseline(load_control_text(), stopwords)

    weights = compute_weights_threshold_cosine(clean_pieces, model, axis, pos_threshold, neg_threshold)
    control_weights = weights[CONTROL_ID]
    n_survivors = len(control_weights)

    if n_survivors == 0:
        return {"score": None, "empty": True, "n_survivors": 0, "top5": [], "whole_zone_scores": {}}

    vectors = {}
    empty_whole_pieces = []
    for pid, w in weights.items():
        if pid == CONTROL_ID:
            continue
        try:
            vectors[pid] = compress_corpus({pid: w}, model)[pid]
        except EmptyVectorError:
            empty_whole_pieces.append(pid)

    try:
        control_vector = compress_corpus({CONTROL_ID: control_weights}, model)[CONTROL_ID]
        score = project({CONTROL_ID: control_vector}, axis)[CONTROL_ID]
        empty = False
    except EmptyVectorError:
        score = None
        empty = True

    whole_zone_scores = project(vectors, axis) if vectors else {}
    top5 = sorted(control_weights.items(), key=lambda kv: kv[1], reverse=True)[:5]

    return {
        "score": score,
        "empty": empty,
        "n_survivors": n_survivors,
        "top5": top5,
        "whole_zone_scores": whole_zone_scores,
        "empty_whole_pieces": empty_whole_pieces,
    }


def build_chart(model, axis, flat_result, axis_sim_result, threshold_result,
                 out_path="outputs/figures/FLAT_AXSIM_CONTROL_WORDS_AND_DOCUMENTS_BAL.png"):
    """Balance-axis words + the 11 real Whole(Z4) articles + the control
    text, overlaid. Reuses src.axis_plot.graph() directly (ax.annotate-based
    labelling, no y-axis tick text, matching every other words+documents
    chart in this project) rather than a bespoke chart -- each of the 11
    real articles and the control text share one categorical y-row across
    the three variants (same "one row per document, one point per variant"
    convention as src.naive_baseline.build_variant_comparison_chart), so the
    figure stays compact instead of needing one row of vertical space per
    point per variant."""
    all_words = BALANCE_WORDS + UNBALANCE_WORDS
    word_scores = [cosine_similarity([axis], [model[w]])[0][0] for w in all_words]
    df = pd.DataFrame({"label": all_words, "score": word_scores, "kind": "word"})

    palette = {"word": "tab:blue", "flat": "tab:orange", "axis_similarity": "tab:green",
               "threshold_cosine": "tab:red"}
    markers = {"word": "o", "flat": "s", "axis_similarity": "D", "threshold_cosine": "^"}

    for variant_name, result in [
        ("flat", flat_result), ("axis_similarity", axis_sim_result), ("threshold_cosine", threshold_result),
    ]:
        if result.get("score") is None:
            continue
        for pid, s in result["whole_zone_scores"].items():
            df = pd.concat([df, pd.DataFrame({"label": [pid], "score": [s], "kind": [variant_name]})],
                            ignore_index=True)
        df = pd.concat([df, pd.DataFrame({
            "label": ["control (USS Maine, 1898)"], "score": [result["score"]], "kind": [variant_name],
        })], ignore_index=True)

    graph(df, "Balance axis — words + 11 real Whole(Z4) articles + USS Maine (1898) control text",
          out_path, palette=palette, markers=markers)


def _range_str(scores):
    vals = list(scores.values())
    if not vals:
        return "no scores available"
    return f"min {min(vals):.4f}, max {max(vals):.4f}, mean {sum(vals) / len(vals):.4f}"


def write_summary(flat_result, axis_sim_result, threshold_result, pos_threshold, neg_threshold,
                   out_path="outputs/CONTROL_TEXT_COMPARISON_BAL.md"):
    lines = [
        "# Control text (USS Maine, 1898) vs. Whole (Z4) pieces — balance axis, observation only",
        "",
        "Drafted by the Data role (`skills/data/SKILL.md`). Runs the same known "
        "non-credible/propagandistic control text (see `data/control/SOURCE.md`) "
        "used for the credibility-axis check, now against the new balance/"
        "one-sidedness axis (spec 010), under three weighting schemes: flat "
        "(TF-only), axis-similarity, and threshold-cosine (this axis's own "
        "statistically-grounded pair, spec 010 task 2). Comparison points are "
        "the 11 real articles' Whole (Z4) pieces, freshly weighted here (the "
        "original corpus's own saved credibility-axis statistics are untouched, "
        "and this is not a substitute for the full task-3 rebuild). No "
        "interpretation of what these figures mean is included here.",
        "",
        "## Flat (TF-only) weighting",
        "",
        f"- Surviving tokens after preprocessing: {flat_result['n_survivors']}.",
        f"- Balance-axis score: {flat_result['score']:.4f}.",
        f"- 11 real Whole (Z4) pieces, same flat weighting, balance axis "
        f"(n={len(flat_result['whole_zone_scores'])}): {_range_str(flat_result['whole_zone_scores'])}.",
        "- Top 5 highest-weighted surviving tokens: "
        + ", ".join(f"{t} ({w:.2f})" for t, w in flat_result["top5"]) + ".",
        "",
        "## Axis-similarity weighting",
        "",
        f"- Surviving tokens after preprocessing: {axis_sim_result['n_survivors']}.",
        f"- Balance-axis score: {axis_sim_result['score']:.4f}.",
        f"- 11 real Whole (Z4) pieces, same axis-similarity weighting, balance "
        f"axis (n={len(axis_sim_result['whole_zone_scores'])}): "
        f"{_range_str(axis_sim_result['whole_zone_scores'])}.",
        "- Top 5 highest-weighted surviving tokens: "
        + ", ".join(f"{t} ({w:.4f})" for t, w in axis_sim_result["top5"]) + ".",
        "",
        f"## Threshold-cosine weighting (pos={pos_threshold:.4f}, neg={neg_threshold:.4f})",
        "",
        f"- Surviving tokens after threshold gate: {threshold_result['n_survivors']}.",
    ]
    if threshold_result.get("empty"):
        lines.append("- No survivors on either pole — empty vector, no score.")
    else:
        lines += [
            f"- Balance-axis score: {threshold_result['score']:.4f}.",
            f"- 11 real Whole (Z4) pieces, same threshold-cosine weighting "
            f"(from this temporary 12-document corpus), balance axis "
            f"(n={len(threshold_result['whole_zone_scores'])}): "
            f"{_range_str(threshold_result['whole_zone_scores'])}.",
            "- Top 5 surviving tokens by weight: "
            + ", ".join(f"{t} ({w:.4f})" for t, w in threshold_result["top5"]) + ".",
        ]
        if threshold_result.get("empty_whole_pieces"):
            lines.append(
                f"- {len(threshold_result['empty_whole_pieces'])} real Whole piece(s) had zero "
                f"survivors in this temporary corpus: {threshold_result['empty_whole_pieces']}."
            )
    lines += ["", "No conclusions are drawn from these figures in this document."]

    with open(out_path, "w") as f:
        f.write("\n".join(lines) + "\n")


def main():
    model = get_model()
    axis = build_balance_axis(model)
    pos_threshold, neg_threshold, _ = derive_thresholds(model, axis)

    flat_result = run_flat(model, axis)
    axis_sim_result = run_axis_similarity(model, axis)
    threshold_result = run_threshold_cosine(model, axis, pos_threshold, neg_threshold)

    write_summary(flat_result, axis_sim_result, threshold_result, pos_threshold, neg_threshold)
    build_chart(model, axis, flat_result, axis_sim_result, threshold_result)
    print("Wrote outputs/figures/FLAT_AXSIM_CONTROL_WORDS_AND_DOCUMENTS_BAL.png")

    print(f"[flat] balance-axis score: {flat_result['score']:.4f}, "
          f"Whole(Z4) range: {_range_str(flat_result['whole_zone_scores'])}")
    print(f"[axis_similarity] balance-axis score: {axis_sim_result['score']:.4f}, "
          f"Whole(Z4) range: {_range_str(axis_sim_result['whole_zone_scores'])}")
    if threshold_result.get("empty"):
        print("[threshold_cosine] no survivors -- empty vector, no score.")
    else:
        print(f"[threshold_cosine] balance-axis score: {threshold_result['score']:.4f}, "
              f"Whole(Z4) range: {_range_str(threshold_result['whole_zone_scores'])}")
    print("Wrote outputs/CONTROL_TEXT_COMPARISON_BAL.md")


if __name__ == "__main__":
    main()
