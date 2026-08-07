"""Token-level pole diagnostic for threshold-cosine weighting, Corpus A
whole documents + control text (2026-07-26 addendum to spec 010).

Built after manually inspecting why the control text (USS Maine, 1898)
scored *less* unbalanced than two real articles (A6Z4, A9Z4) under
threshold-cosine weighting: the final score is the cosine of the whole
weighted-average vector, so individual survivor words on opposite poles
partially cancel out. That hand check found several counterintuitive
individual-word placements -- "anchored" landing firmly on the balanced
pole, "facts" and "video" landing on the unbalanced pole -- that don't
obviously track their plain-English meaning. This saves the full picture
(every surviving token, every piece, its own cosine-to-axis value and
which pole it lands on) as reusable, reproducible code and a table,
rather than leaving it as a one-off inline check.
"""

import csv
from pathlib import Path

from src.axis import build_balance_axis
from src.axis_weighting import _cosine_similarity_to_axis, compute_weights_threshold_cosine
from src.control_text_balance_axis_check import CONTROL_ID, _whole_zone_pieces, load_control_text
from src.glove import get_model
from src.naive_baseline import spacy_stopword_set
from src.preprocessing import clean_tokens_stopword_baseline
from src.threshold_derivation import derive_thresholds


def compute_token_diagnostics(model, axis, weights):
    """weights: {piece_id: {term: tfidf_weight}} (post-threshold-gate
    survivors only). Returns {piece_id: [(term, tfidf_weight, cosine_to_axis), ...]}
    sorted by tfidf_weight descending within each piece."""
    axis_2d = axis.reshape(1, -1)
    result = {}
    for piece_id, term_weights in weights.items():
        rows = []
        for term, weight in term_weights.items():
            cosine = _cosine_similarity_to_axis(term, model, axis_2d)
            rows.append((term, weight, cosine))
        rows.sort(key=lambda r: r[1], reverse=True)
        result[piece_id] = rows
    return result


def write_table(diagnostics, out_path="outputs/tables/CTHRESH_POLE_DIAGNOSTIC_A_BAL.csv"):
    rows = []
    for piece_id, tokens in diagnostics.items():
        for rank, (term, weight, cosine) in enumerate(tokens, start=1):
            rows.append({
                "piece_id": piece_id,
                "rank": rank,
                "token": term,
                "tfidf_weight": round(weight, 4),
                "cosine_to_axis": round(cosine, 4),
                "pole": "balanced" if cosine > 0 else "unbalanced",
            })
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["piece_id", "rank", "token", "tfidf_weight", "cosine_to_axis", "pole"]
        )
        writer.writeheader()
        writer.writerows(rows)


def summarize(diagnostics):
    """Returns {piece_id: {"n_survivors", "n_balanced", "n_unbalanced"}}."""
    summary = {}
    for piece_id, tokens in diagnostics.items():
        n_balanced = sum(1 for _, _, c in tokens if c > 0)
        n_unbalanced = sum(1 for _, _, c in tokens if c < 0)
        summary[piece_id] = {
            "n_survivors": len(tokens),
            "n_balanced": n_balanced,
            "n_unbalanced": n_unbalanced,
        }
    return summary


def main():
    model = get_model()
    axis = build_balance_axis(model)
    pos_threshold, neg_threshold, _ = derive_thresholds(model, axis)

    whole_pieces = _whole_zone_pieces()
    stopwords = spacy_stopword_set()
    clean_pieces = {pid: clean_tokens_stopword_baseline(text, stopwords) for pid, text in whole_pieces.items()}
    clean_pieces[CONTROL_ID] = clean_tokens_stopword_baseline(load_control_text(), stopwords)

    weights = compute_weights_threshold_cosine(clean_pieces, model, axis, pos_threshold, neg_threshold)
    diagnostics = compute_token_diagnostics(model, axis, weights)
    write_table(diagnostics)

    print("Wrote outputs/tables/CTHRESH_POLE_DIAGNOSTIC_A_BAL.csv")
    for piece_id, stats in summarize(diagnostics).items():
        print(f"{piece_id}: {stats['n_survivors']} survivors, "
              f"{stats['n_balanced']} balanced-pole, {stats['n_unbalanced']} unbalanced-pole")


if __name__ == "__main__":
    main()
