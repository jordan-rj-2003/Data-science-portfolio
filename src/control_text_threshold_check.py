"""Control-text (USS Maine, 1898) check under threshold-cosine weighting,
random-baseline thresholds (spec 006/008's recommended primary method) --
extends the flat/axis-similarity control-text check in
src/control_text_check.py, which deliberately avoided threshold-cosine
because its TF-IDF component needs a document-frequency corpus to compute
rarity against, and neither flat nor axis-similarity weighting does.

Rather than joining the control text into the real 44-piece corpus (which
would change that corpus's own saved IDF statistics), this builds a small,
temporary 12-document corpus -- the 11 real articles' Whole (Z4) pieces plus
the control text, given the zone-shaped id "controlZ4" so it groups under
zone 4 alongside the real Whole pieces via compute_weights_plain's existing
group_by_zone logic. Only the control text's own score is reported; the
original corpus's saved outputs are never modified or re-run, and the 11
real pieces' fresh scores from this temporary corpus are not treated as a
replacement for their canonically saved threshold-cosine figures (df counts
shift slightly once a 12th document is added).
"""

from src.axis import build_axis, project
from src.axis_weighting import compute_weights_threshold_cosine
from src.compression import EmptyVectorError, compress_corpus
from src.glove import get_model
from src.naive_baseline import spacy_stopword_set
from src.preprocessing import clean_tokens_stopword_baseline
from src.segmentation import segment_corpus

CONTROL_PATH = "data/control/uss_maine_1898.txt"
CONTROL_ID = "controlZ4"

POS_THRESHOLD_RANDOM_BASELINE = 0.194
NEG_THRESHOLD_RANDOM_BASELINE = 0.096


def load_control_text(path=CONTROL_PATH):
    with open(path) as f:
        return f.read()


def run(pos_threshold=POS_THRESHOLD_RANDOM_BASELINE, neg_threshold=NEG_THRESHOLD_RANDOM_BASELINE):
    model = get_model()
    axis = build_axis(model)
    stopwords = spacy_stopword_set()

    article_ids = [f"A{i}" for i in range(1, 12)]
    raw_pieces = segment_corpus("data/raw", article_ids)
    whole_pieces = {pid: text for pid, text in raw_pieces.items() if pid.endswith("Z4")}

    clean_pieces = {pid: clean_tokens_stopword_baseline(text, stopwords) for pid, text in whole_pieces.items()}
    clean_pieces[CONTROL_ID] = clean_tokens_stopword_baseline(load_control_text(), stopwords)

    weights = compute_weights_threshold_cosine(clean_pieces, model, axis, pos_threshold, neg_threshold)
    control_weights = weights[CONTROL_ID]
    n_survivors = len(control_weights)

    if n_survivors == 0:
        return {
            "score": None,
            "empty": True,
            "n_survivors": 0,
            "top5": [],
        }

    try:
        vectors = compress_corpus({CONTROL_ID: control_weights}, model)
        score = project(vectors, axis)[CONTROL_ID]
        empty = False
    except EmptyVectorError:
        score = None
        empty = True

    all_survivors = sorted(control_weights.items(), key=lambda kv: kv[1], reverse=True)

    return {
        "score": score,
        "empty": empty,
        "n_survivors": n_survivors,
        "top5": all_survivors[:5],
        "all_survivors": all_survivors,
    }


def main():
    result = run()
    print(f"Surviving tokens after threshold gate: {result['n_survivors']}")
    if result["empty"]:
        print("No survivors on either pole -- empty vector, no score.")
    else:
        print(f"Score (large axis): {result['score']:.4f}")
        print("Top 5 surviving tokens by TF-IDF weight:")
        for term, weight in result["top5"]:
            print(f"  {term}: {weight:.4f}")


if __name__ == "__main__":
    main()
