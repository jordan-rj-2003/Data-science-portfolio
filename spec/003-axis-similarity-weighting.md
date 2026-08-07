# Spec 003 — Axis-Similarity Weighting (Phase 1: pure absolute cosine similarity)

Status: **Complete (2026-07-19)** — approved and implemented same day, all
8 tasks done. See Key Results below.

Maps to: two problems diagnosed from spec 002's results — (1) signal
dilution from averaging over many tokens in Body/Whole zones (mean token
count 280/345, vs. 25/40 for Headline+Lead/End — see
`outputs/naive-baseline-key-stats-comparison.md`); (2) the
highest-TF-IDF-weighted token per piece is frequently a word with no
real relationship to credibility ("number", "mr.", "resolution",
"lawyer" — see `outputs/tables/top_token_per_piece*.csv`), because
TF-IDF weight measures corpus-rarity, not axis-relevance.

## Goal (one sentence)
Replace TF-IDF weighting with a new weighting scheme — each surviving
token's weight is the absolute value of its own GloVe vector's cosine
similarity to the credibility axis — while keeping everything else
identical to the spaCy-stopword baseline (NER removal, spaCy stopword +
punctuation removal, no POS-tag filtering, no IDF/document-frequency
concept at all), to test whether weighting by axis-relevance rather than
corpus-rarity fixes both diagnosed problems.

## WHAT
1. **New weighting function**, `src/axis_weighting.py` (new module — this
   weighting scheme depends on the axis + GloVe model, not on
   corpus-level document frequency, so it doesn't fit `src/tfidf.py`'s
   scope; a new single-responsibility module is cleaner than bending
   `tfidf.py` to cover a non-frequency-based scheme):
   - `compute_weights_axis_similarity(pieces, model, axis)`: for each
     piece, for each **unique** surviving token (not per-occurrence —
     resolved decision below), weight = `abs(cosine_similarity(model[term], axis))`.
     Tokens not in the GloVe vocabulary are skipped when building the
     weight dict (mirrors `compress_piece`'s existing OOV handling,
     avoids a lookup error rather than deferring it).
   - No document-frequency/IDF concept, no zone-type grouping — this
     weight depends only on the word itself and the fixed axis vector.
2. **Preprocessing**: reuse `clean_corpus_stopword_baseline` with spaCy's
   stopword set specifically (not NLTK's) — "everything else will remain
   the same as per the spaCy baseline" (student's own framing).
3. Run through **unchanged** `compress_corpus`, `build_axis`, `project` —
   same as every other variant so far.
4. **Comparison tables**: this variant vs. spaCy-baseline (isolates the
   weighting-scheme change specifically, holding preprocessing constant —
   the most direct test of the hypothesis) and vs. production (full
   contrast), same `write_comparison` format as the existing ablations.
5. **Key-statistics check**: top-token-per-piece extraction for this
   variant (same pattern as `top_token_per_piece.csv`) — this is the
   direct diagnostic for problem 2: do the winning tokens actually shift
   away from axis-irrelevant words like "number"/"mr." toward words
   plausibly related to credibility?
6. **Word+document axis chart**: reuse `src/naive_baseline.py`'s
   multi-variant overlay chart, adding this variant alongside
   production/spaCy/NLTK (or as its own comparison — student's call at
   review time).
7. **Readable summary report**: factual only, no conclusions, matching
   the established style.

## WHY
Directly tests the two diagnosed problems rather than asserting a fix
works. Extends the same "measure it, don't just assert it" standard
already applied three times in this project (flat-vs-TF-IDF,
POS-filtered-vs-unfiltered, naive-baseline-vs-production).

## CONSTRAINTS
- Same 11-article corpus, same zone segmentation, same GloVe model, same
  credibility axis, same spaCy-baseline preprocessing — only the
  weighting formula changes, consistent with how every prior ablation in
  this project is scoped.
- No new dependency — `cosine_similarity` (already imported via
  `sklearn.metrics.pairwise` in `src/axis.py`) and the existing GloVe
  model cover everything needed.

## RISKS
1. **Near-zero-similarity words aren't eliminated, just heavily
   down-weighted** — a word like "number" gets a small positive weight
   (e.g. 0.02), not exactly zero, since nothing in this phase thresholds
   the weight. Hard-zeroing low-relevance words is explicitly deferred to
   a later phase (see Remaining Open Items) — worth being clear this
   phase is a continuous re-weighting, not a cutoff.
2. **Dropping TF (repetition count) entirely is a real modelling choice,
   not a simplification for its own sake** — a word appearing once and a
   word appearing ten times in the same piece contribute identically
   under this scheme. Confirmed as the intended design for this phase
   (student: "we will start with axis-similarity only (abs) and
   analyse"), not an oversight.
3. **Every in-vocabulary token gets *some* weight**, including words with
   moderate-but-nonzero axis similarity that aren't really about
   credibility (e.g. a word that happens to sit near the axis by GloVe
   coincidence rather than genuine semantic relevance) — a known
   limitation of using cosine similarity to a hand-constructed axis as a
   relevance proxy, not specific to this pipeline.

## SUCCESS / ACCEPTANCE CRITERIA
- Comparison tables (this variant vs. spaCy-baseline; this variant vs.
  production), same format as existing ablations.
- Top-token-per-piece table for this variant, allowing direct comparison
  against `top_token_per_piece.csv`/`..._spacy_baseline.csv` to check
  whether the winning tokens actually shift.
- No crash, including the (unlikely but possible) all-zero-weight edge
  case already handled by `compress_piece`'s `EmptyVectorError`.
- Results reported factually (Data role — observation, not conclusions).

## TASK BREAKDOWN (ordered, dependencies marked)
1. **Complete**: `src/axis_weighting.py` — `compute_weights_axis_similarity`.
2. **Complete**: `src/axis_similarity_ablation.py` —
   `run_axis_similarity_variant`, chaining `segment_corpus` →
   `clean_corpus_stopword_baseline` (spaCy stopwords) →
   `compute_weights_axis_similarity` → `compress_corpus` →
   `build_axis`/`project`.
3. **Complete**: comparison tables —
   `outputs/tables/axis_similarity_comparison_vs_spacy.csv`,
   `..._vs_production.csv`.
4. **Complete**: `outputs/tables/top_token_per_piece_axis_similarity.csv`.
5. **Complete**: `outputs/figures/axis_similarity_words_and_documents_Z{1-4}.png`
   (reused `src/naive_baseline.py`'s `build_variant_comparison_chart`,
   which required making its chart title dynamic — it was hardcoded to
   say "production/spaCy/NLTK" regardless of which variants were
   actually passed in, which would have mislabelled this chart set).
6. **Complete**: two reports —
   `outputs/axis-similarity-axis-comparison.md`,
   `outputs/axis-similarity-key-stats.md` — factual only.
7. **Complete**: `tests/test_axis_weighting.py`, 4 new tests (abs value
   confirmed via a synthetic non-credible-aligned vector, OOV skipping,
   repetition-independence). Full suite: 43/43 passing.
8. **Complete**: this journal entry — see 2026-07-19, "Spec 003 built:
   axis-similarity weighting, Phase 1."

## Key results (2026-07-19)
- **Top-token identity shifted dramatically**: axis-similarity agrees
  with production on only 2/44 top tokens, and with spaCy-baseline on
  only 2/44 — far less agreement than spaCy-baseline and production had
  with each other (37/44, per spec 002). Winning tokens include
  "immediate", "negotiation", "ensure", "determined", "realize" —
  plausibly more credibility-relevant than "number"/"mr." — see
  `outputs/axis-similarity-key-stats.md` for the full list, no
  interpretation included there.
- **Body/Whole zone score variance dropped substantially**: stdev of the
  final projection score fell from 0.0223 (production) to 0.0097
  (axis-similarity) in Body, and from 0.0181 to 0.0102 in Whole —
  Headline+Lead and End did not show the same drop. See
  `outputs/axis-similarity-axis-comparison.md` §"Score variance by zone"
  for the full table.
- Both largest-rank-shift pieces in this phase (A5Z3, A10Z3, shifts of
  −28/−30) exceed the largest shift recorded in any prior ablation in
  this project (22, spec 002).

## Remaining open items — explicitly deferred, not forgotten
Per the student's own roadmap, two further phases are already agreed as
*future* work, not part of this spec:
- **Phase 2 — thresholding**: any token with `|cosine_similarity| < 0.2`
  gets weight 0 (a hard cutoff for "not axis-relevant enough to count at
  all"), rather than the continuous down-weighting this phase uses.
- **Phase 3 — hybrid weighting**: combining TF-IDF and axis-similarity
  (student's own suggestions to explore: `tfidf_score * cosine_similarity + 1`,
  or an exponentiated form of cosine similarity analogous to how the
  existing IDF formula uses `ln` — exact formula not yet decided).
These are recorded here so they aren't lost, but neither is in scope
until this phase (pure absolute cosine-similarity weighting) has been
built and analysed.
