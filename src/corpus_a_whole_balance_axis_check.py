"""Corpus A (the original 11-article corpus), whole-document only, run
through 4 weighting schemes against the balance axis: standard baseline
(spaCy-stopword + plain TF-IDF), production (POS-filtered,
continuity-corrected TF-IDF), threshold-cosine (this axis's own
statistically-grounded pair, spec 010 task 2), and product hybrid
(TF-IDF x abs(cosine-to-axis), no floor -- added exploratorily, not part
of spec 010's original task list, to see whether it behaves differently
from the other three here).

"Whole-document only" needs no new corpus construction: Z4 ("Whole") in
src/segmentation.py is already defined as the full article text (header +
every real paragraph), so this restricts to the 11 existing Z4 pieces
rather than building a separate flat corpus the way Corpus B's ESPN
scripts had to. The USS Maine control text is folded in as a 12th "Z4"
document (same temporary-corpus technique as
src/control_text_balance_axis_check.py) so all 4 variants can be seen
against the control text at once, without touching the real corpus's own
saved statistics.

Distinct from spec 010 task 3 (the full 7-variant x 4-zone rebuild, still
not started) -- this is whole-document-only and scoped to exactly the 4
variants requested here.
"""

import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

from src.axis import BALANCE_WORDS, UNBALANCE_WORDS, build_balance_axis, project
from src.axis_plot import graph
from src.axis_weighting import compute_weights_hybrid_product, compute_weights_threshold_cosine
from src.compression import EmptyVectorError, compress_corpus
from src.control_text_balance_axis_check import CONTROL_ID, _whole_zone_pieces, load_control_text
from src.glove import get_model
from src.naive_baseline import spacy_stopword_set
from src.preprocessing import clean_tokens, clean_tokens_stopword_baseline
from src.tfidf import compute_weights, compute_weights_plain
from src.threshold_derivation import derive_thresholds


def _project_weights(weights, model, axis):
    """weights: {piece_id: {term: weight}}. Returns (scores, empty_pieces)."""
    vectors = {}
    empty = []
    for pid, w in weights.items():
        try:
            vectors[pid] = compress_corpus({pid: w}, model)[pid]
        except EmptyVectorError:
            empty.append(pid)
    return project(vectors, axis), empty


def run_standard_baseline(model, axis):
    whole_pieces = _whole_zone_pieces()
    stopwords = spacy_stopword_set()
    clean_pieces = {pid: clean_tokens_stopword_baseline(text, stopwords) for pid, text in whole_pieces.items()}
    clean_pieces[CONTROL_ID] = clean_tokens_stopword_baseline(load_control_text(), stopwords)

    weights = compute_weights_plain(clean_pieces)
    scores, empty = _project_weights(weights, model, axis)
    control_score = scores.pop(CONTROL_ID)
    top5 = sorted(weights[CONTROL_ID].items(), key=lambda kv: kv[1], reverse=True)[:5]
    return {"scores": scores, "control_score": control_score, "top5": top5, "empty": empty}


def run_production(model, axis):
    whole_pieces = _whole_zone_pieces()
    clean_pieces = {pid: clean_tokens(text, pos_filter=True) for pid, text in whole_pieces.items()}
    clean_pieces[CONTROL_ID] = clean_tokens(load_control_text(), pos_filter=True)

    weights = compute_weights(clean_pieces)
    scores, empty = _project_weights(weights, model, axis)
    control_score = scores.pop(CONTROL_ID)
    top5 = sorted(weights[CONTROL_ID].items(), key=lambda kv: kv[1], reverse=True)[:5]
    return {"scores": scores, "control_score": control_score, "top5": top5, "empty": empty}


def run_threshold_cosine(model, axis, pos_threshold, neg_threshold):
    whole_pieces = _whole_zone_pieces()
    stopwords = spacy_stopword_set()
    clean_pieces = {pid: clean_tokens_stopword_baseline(text, stopwords) for pid, text in whole_pieces.items()}
    clean_pieces[CONTROL_ID] = clean_tokens_stopword_baseline(load_control_text(), stopwords)

    weights = compute_weights_threshold_cosine(clean_pieces, model, axis, pos_threshold, neg_threshold)
    scores, empty = _project_weights(weights, model, axis)
    control_score = scores.pop(CONTROL_ID, None)
    control_weights = weights.get(CONTROL_ID, {})
    top5 = sorted(control_weights.items(), key=lambda kv: kv[1], reverse=True)[:5]
    return {"scores": scores, "control_score": control_score, "top5": top5, "empty": empty,
            "n_control_survivors": len(control_weights)}


def run_product_hybrid(model, axis):
    whole_pieces = _whole_zone_pieces()
    stopwords = spacy_stopword_set()
    clean_pieces = {pid: clean_tokens_stopword_baseline(text, stopwords) for pid, text in whole_pieces.items()}
    clean_pieces[CONTROL_ID] = clean_tokens_stopword_baseline(load_control_text(), stopwords)

    weights = compute_weights_hybrid_product(clean_pieces, model, axis)
    scores, empty = _project_weights(weights, model, axis)
    control_score = scores.pop(CONTROL_ID)
    top5 = sorted(weights[CONTROL_ID].items(), key=lambda kv: kv[1], reverse=True)[:5]
    return {"scores": scores, "control_score": control_score, "top5": top5, "empty": empty}


def _words_df(model, axis):
    all_words = BALANCE_WORDS + UNBALANCE_WORDS
    word_scores = [cosine_similarity([axis], [model[w]])[0][0] for w in all_words]
    return pd.DataFrame({"label": all_words, "score": word_scores, "kind": "word"})


def build_combined_chart(model, axis, results_by_variant,
                          out_path="outputs/figures/STAN_PROD_CTHRESH_PRHYB_WORDS_AND_DOCUMENTS_A_BAL.png"):
    """All 4 variants overlaid on one chart, matching the multi-variant
    convention already used elsewhere (e.g. src.naive_baseline.build_variant_comparison_chart)."""
    df = _words_df(model, axis)
    palette = {"word": "tab:blue", "standard_baseline": "tab:orange", "production": "tab:red",
               "threshold_cosine": "tab:purple", "product_hybrid": "tab:brown"}
    markers = {"word": "o", "standard_baseline": "s", "production": "X",
               "threshold_cosine": "^", "product_hybrid": "P"}
    for variant_name, result in results_by_variant.items():
        for pid, s in result["scores"].items():
            df = pd.concat([df, pd.DataFrame({"label": [pid], "score": [s], "kind": [variant_name]})],
                            ignore_index=True)
        if result["control_score"] is not None:
            df = pd.concat([df, pd.DataFrame({
                "label": ["control (USS Maine, 1898)"], "score": [result["control_score"]], "kind": [variant_name],
            })], ignore_index=True)
    graph(df, "Balance axis — Corpus A (whole documents) + control text, all 4 variants",
          out_path, palette=palette, markers=markers)


def build_variant_chart(model, axis, variant_name, result, out_path):
    """One chart per variant: this variant's 11 real whole-article scores
    + control, annotated (no y-tick labels, matching graph()'s convention)
    with a tight xlim computed from this variant's own score range instead
    of the shared -0.65/0.65 default -- so the document cluster is visible
    in detail instead of compressed into a shared wide axis. Balance-axis
    words are deliberately left out here (they'd sit far outside this tight
    range and be invisible anyway, with an empty legend entry to show for
    it) -- see the combined chart for words + documents together."""
    rows = [{"label": pid, "score": s, "kind": "document"} for pid, s in result["scores"].items()]
    if result["control_score"] is not None:
        rows.append({"label": "control (USS Maine, 1898)", "score": result["control_score"], "kind": "control"})
    df = pd.DataFrame(rows)

    all_scores = list(result["scores"].values()) + (
        [result["control_score"]] if result["control_score"] is not None else []
    )
    margin = 0.01
    xlim = (min(all_scores) - margin, max(all_scores) + margin)

    palette = {"word": "tab:blue", "document": "tab:red", "control": "black"}
    markers = {"word": "o", "document": "X", "control": "*"}
    graph(df, f"Balance axis — Corpus A (whole documents) + control text, {variant_name}",
          out_path, palette=palette, markers=markers, xlim=xlim)


def write_summary(results_by_variant, pos_threshold, neg_threshold,
                   out_path="outputs/STAN_PROD_CTHRESH_PRHYB_COMPARISON_A_BAL.md"):
    lines = [
        "# Corpus A, whole documents only — balance axis, 4 variants + control text",
        "",
        "Drafted by the Data role (`skills/data/SKILL.md`). Corpus A's 11 "
        "articles, whole-document only (Z4, the existing \"Whole\" zone -- "
        "no new corpus construction needed), run through standard baseline, "
        "production, threshold-cosine, and product hybrid against the "
        "balance axis, with the USS Maine control text folded in as a 12th "
        "document. Distinct from spec 010 task 3 (the full 7-variant x "
        "4-zone rebuild, still not started). No interpretation of what "
        "these figures mean is included here.",
        "",
        f"Threshold-cosine pair used: pos={pos_threshold:.4f}, neg={neg_threshold:.4f}.",
        "",
        "## Scores",
        "",
        "| Variant | Control score | Real articles: min | max | mean |",
        "|---|---|---|---|---|",
    ]
    for variant_name, result in results_by_variant.items():
        vals = list(result["scores"].values())
        control_str = f"{result['control_score']:.4f}" if result["control_score"] is not None else "empty"
        lines.append(
            f"| {variant_name} | {control_str} | {min(vals):.4f} | {max(vals):.4f} | "
            f"{sum(vals)/len(vals):.4f} |"
        )
    lines += ["", "## Control text top 5 tokens per variant", ""]
    for variant_name, result in results_by_variant.items():
        top5_str = ", ".join(f"{t} ({w:.4f})" for t, w in result["top5"]) if result["top5"] else "none (empty)"
        lines.append(f"- **{variant_name}**: {top5_str}")
    lines += ["", "No conclusions are drawn from these figures in this document."]

    with open(out_path, "w") as f:
        f.write("\n".join(lines) + "\n")


def main():
    model = get_model()
    axis = build_balance_axis(model)
    pos_threshold, neg_threshold, _ = derive_thresholds(model, axis)

    results_by_variant = {
        "standard_baseline": run_standard_baseline(model, axis),
        "production": run_production(model, axis),
        "threshold_cosine": run_threshold_cosine(model, axis, pos_threshold, neg_threshold),
        "product_hybrid": run_product_hybrid(model, axis),
    }

    for variant_name, result in results_by_variant.items():
        if result["empty"]:
            print(f"WARNING [{variant_name}]: {len(result['empty'])} piece(s) empty: {result['empty']}")

    build_combined_chart(model, axis, results_by_variant)
    print("Wrote outputs/figures/STAN_PROD_CTHRESH_PRHYB_WORDS_AND_DOCUMENTS_A_BAL.png")

    variant_acronyms = {
        "standard_baseline": "STANDARD", "production": "PRODUCTION",
        "threshold_cosine": "CTHRESH", "product_hybrid": "PRHYB",
    }
    for variant_name, result in results_by_variant.items():
        out_path = f"outputs/figures/{variant_acronyms[variant_name]}_WORDS_AND_DOCUMENTS_A_BAL.png"
        build_variant_chart(model, axis, variant_name, result, out_path)
        print(f"Wrote {out_path}")

    write_summary(results_by_variant, pos_threshold, neg_threshold)
    print("Wrote outputs/STAN_PROD_CTHRESH_PRHYB_COMPARISON_A_BAL.md")

    for variant_name, result in results_by_variant.items():
        vals = list(result["scores"].values())
        control_str = f"{result['control_score']:.4f}" if result["control_score"] is not None else "empty"
        print(f"[{variant_name}] control={control_str}, real articles min={min(vals):.4f} "
              f"max={max(vals):.4f} mean={sum(vals)/len(vals):.4f}")


if __name__ == "__main__":
    main()
