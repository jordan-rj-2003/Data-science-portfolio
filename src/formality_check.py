"""Register/formality confound check.

Tests whether the credibility axis's inter-article separation (found
across every weighting scheme tested so far) could just be tracking
generic stylistic register — sentence length, word length, lexical
diversity — rather than anything specifically about credibility language.
Uses standard structural stylometric measures rather than another GloVe
axis, deliberately: building a second embedding axis to check the first
would just raise the same word-selection-validity question one level
removed. These three measures need no word-list construction at all.

For each of the 11 articles (whole raw text, not zone-split — register
is a property of the writer's overall style, not particular to one zone):
  - average sentence length (words per sentence)
  - average word length (characters per alphabetic token)
  - type-token ratio (unique alphabetic tokens / total alphabetic tokens)

Correlated (Pearson, n=11) against each weighting variant's existing
Whole-zone credibility score. A strong correlation would be evidence that
register, not credibility-specific language, is driving separation; a
weak one would be evidence against that confound.
"""

import csv

import numpy as np

from src.preprocessing import get_nlp

ARTICLE_IDS = [f"A{i}" for i in range(1, 12)]


def register_metrics(text):
    nlp = get_nlp()
    doc = nlp(text)
    sentences = list(doc.sents)
    words = [t for t in doc if t.is_alpha]
    n_sentences = max(len(sentences), 1)
    avg_sentence_length = len(words) / n_sentences
    avg_word_length = sum(len(t.text) for t in words) / max(len(words), 1)
    lower_words = [t.text.lower() for t in words]
    type_token_ratio = len(set(lower_words)) / max(len(lower_words), 1)
    return {
        "avg_sentence_length": avg_sentence_length,
        "avg_word_length": avg_word_length,
        "type_token_ratio": type_token_ratio,
    }


def compute_all_register_metrics(raw_dir="data/raw"):
    metrics = {}
    for article_id in ARTICLE_IDS:
        with open(f"{raw_dir}/{article_id}.txt") as f:
            text = f.read()
        metrics[article_id] = register_metrics(text)
    return metrics


def _read_whole_zone_score_by_article(path, score_col):
    scores = {}
    with open(path) as f:
        for row in csv.DictReader(f):
            if row["zone"] == "Whole":
                scores[row["article"]] = float(row[score_col])
    return scores


def pearson(xs, ys):
    return float(np.corrcoef(xs, ys)[0, 1])


def main():
    register = compute_all_register_metrics()

    credibility_scores = {
        "production": _read_whole_zone_score_by_article(
            "outputs/tables/PRODUCTION_SCORES.csv", "score"
        ),
        "spacy_baseline": _read_whole_zone_score_by_article(
            "outputs/tables/PROD_vs_STAN_COMPARISON.csv", "spacy_baseline_score"
        ),
        "product_hybrid": _read_whole_zone_score_by_article(
            "outputs/tables/PRHYB_vs_PROD_COMPARISON.csv", "product_hybrid_score"
        ),
    }

    register_names = ["avg_sentence_length", "avg_word_length", "type_token_ratio"]
    correlations = {}
    for variant, scores in credibility_scores.items():
        ys = [scores[a] for a in ARTICLE_IDS]
        correlations[variant] = {}
        for reg_name in register_names:
            xs = [register[a][reg_name] for a in ARTICLE_IDS]
            correlations[variant][reg_name] = pearson(xs, ys)

    lines = [
        "# Register/formality confound check — observation only",
        "",
        "Drafted by the Data role (`skills/data/SKILL.md`). Tests whether "
        "credibility-axis separation could be explained by generic stylistic "
        "register (sentence length, word length, lexical diversity) rather "
        "than credibility-specific language. Pearson correlation (n=11 "
        "articles, Whole-zone scores) between each register measure and each "
        "weighting variant's credibility score. No interpretation of what "
        "these correlations mean is included here.",
        "",
        "## Register metrics per article",
        "",
        "| Article | Avg sentence length | Avg word length | Type-token ratio |",
        "|---|---|---|---|",
    ]
    for a in ARTICLE_IDS:
        r = register[a]
        lines.append(
            f"| {a} | {r['avg_sentence_length']:.2f} | {r['avg_word_length']:.2f} | {r['type_token_ratio']:.3f} |"
        )
    lines.append("")
    lines.append("## Pearson correlation: register measure vs. credibility score (Whole zone, n=11)")
    lines.append("")
    lines.append("| Variant | Avg sentence length | Avg word length | Type-token ratio |")
    lines.append("|---|---|---|---|")
    for variant, corrs in correlations.items():
        lines.append(
            f"| {variant} | {corrs['avg_sentence_length']:.3f} | "
            f"{corrs['avg_word_length']:.3f} | {corrs['type_token_ratio']:.3f} |"
        )
    lines.append("")
    lines.append("No conclusions are drawn from these figures in this document.")

    with open("outputs/REGISTER_CONFOUND_CHECK.md", "w") as f:
        f.write("\n".join(lines) + "\n")

    for variant, corrs in correlations.items():
        print(f"[{variant}] " + ", ".join(f"{k}={v:.3f}" for k, v in corrs.items()))
    print("Wrote outputs/REGISTER_CONFOUND_CHECK.md")


if __name__ == "__main__":
    main()
