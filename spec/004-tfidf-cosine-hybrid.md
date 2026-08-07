# Spec 004 — TF-IDF × Axis-Similarity Hybrid Weighting

Status: **Complete (2026-07-19)** — approved and implemented same day.
See Key Results below.

Maps to: spec 003's "Remaining open items — Phase 3 (hybrid weighting)",
now being built after Phase 1 (pure axis-similarity) revealed a real
tension worth addressing directly — axis-similarity weighting reduced
inter-article separation in 3 of 4 zones relative to production (see
journal 2026-07-19, "takeaways... separation of articles"), plausibly
because its corpus-independent weight lets the same handful of globally
high-similarity words dominate across many different articles. TF-IDF's
corpus-relative rarity is exactly the property that produces separation;
this hybrid tests whether combining both recovers separation while
keeping the Phase-1 improvement in *which* words get weighted highest.

## Goal (one sentence)
Weight each token by `tfidf_weight × (1 + abs(cosine_similarity(word, axis)))`
— TF-IDF's corpus-relative rarity, multiplicatively modulated by
axis-relevance — using the same spaCy-stopword preprocessing and plain
TF-IDF formula as the existing ablation family, and compare against
production, spaCy-baseline, and the Phase-1 axis-similarity variant.

## WHAT
1. **New weighting function**, `src/axis_weighting.py`
   (`compute_weights_hybrid_tfidf_cosine(pieces, model, axis)`): for each
   piece, `weight(t) = tfidf_weight(t, piece) × (1 + abs(cosine_similarity(model[t], axis)))`.
   - `tfidf_weight` computed exactly as `compute_weights_plain` (plain
     `idf(t) = ln(N/df(t))`, no continuity correction, no high-TF cap,
     grouped by zone-type) — same TF-IDF as spaCy-baseline.
   - The modifier `(1 + abs(cosine_similarity))` ranges [1, 2]: an
     axis-irrelevant word keeps ~its plain TF-IDF weight (×1); a
     strongly axis-relevant word (either pole) gets up to 2× its plain
     TF-IDF weight. **Resolved (student, 2026-07-19)**: absolute value,
     not signed — a word strongly aligned with the non-credible pole is
     genuinely diagnostic and must not have its contribution suppressed;
     the word's own GloVe vector (via `compress_piece`) already carries
     the correct direction into the average, so the weight's job is
     relevance-magnitude only, same principle as Phase 1.
2. **Preprocessing**: `clean_corpus_stopword_baseline` with spaCy's
   stopword set — same as spaCy-baseline and the Phase-1 axis-similarity
   variant, for direct comparability across the whole ablation family.
3. Run through **unchanged** `compress_corpus`, `build_axis`, `project`.
4. **Comparison tables**: this variant vs. production, vs. spaCy-baseline,
   vs. Phase-1 axis-similarity (three comparisons — the third is the
   direct test of whether the hybrid recovers separation relative to
   Phase 1).
5. **Inter-article separation check** (the specific statistic that
   motivated this spec): stdev across the 11 articles' mean scores, and
   stdev within each zone, compared against production and Phase-1
   axis-similarity's already-recorded figures.
6. **Top-token-per-piece extraction**, same pattern as every prior
   variant — checks whether the hybrid keeps Phase 1's shift away from
   axis-irrelevant words, or reverts toward TF-IDF's original top tokens.
7. **Word+document axis chart**, extending the existing multi-variant
   overlay.
8. **Readable summary report**, factual only, no conclusions.

## WHY
Directly tests whether the separation loss found in Phase 1 is a
consequence of dropping TF-IDF's corpus-relative rarity specifically —
if the hybrid's separation figures land closer to production's than
Phase 1's did, that's evidence for the mechanism; if not, the explanation
needs revisiting. Continues the "measure it" standard already applied to
every prior weighting change in this project.

## CONSTRAINTS
- Same 11-article corpus, same zone segmentation, same GloVe model, same
  axis — only the weighting formula changes.
- No new dependency.

## RISKS
1. **The [1, 2] modifier range is a real design choice, not a neutral
   default** — an axis-irrelevant word's weight is never reduced (floor
   of ×1, same as plain TF-IDF), only ever held flat or boosted. This
   means the hybrid can only move separation *toward* TF-IDF's pattern by
   amplifying already-rare, axis-relevant words further, not by
   suppressing axis-irrelevant ones — worth knowing this is asymmetric by
   construction, not incidental.
2. Same corpus-composition caveat already surfaced for Phase 1 (thin
   negative-pole vocabulary in this specific corpus) still applies here —
   the modifier can boost a word up to 2x if it's strongly axis-relevant,
   but there are still few strongly non-credible-pole words available to
   boost in this corpus.

## SUCCESS / ACCEPTANCE CRITERIA
- Three comparison tables (vs. production, vs. spaCy-baseline, vs.
  Phase-1 axis-similarity).
- Inter-article separation stdev (overall and by zone) reported
  side-by-side against production and Phase-1 figures.
- Top-token table, no crash, factual summary report only.

## TASK BREAKDOWN
1. **Complete**: `src/axis_weighting.py` —
   `compute_weights_hybrid_tfidf_cosine`.
2. **Complete**: `src/axis_similarity_ablation.py` extended with
   `run_hybrid_variant`; produces 3 comparison tables
   (`outputs/tables/hybrid_comparison_vs_{production,spacy,axis_similarity}.csv`),
   a top-token table (`..._top_token_per_piece_hybrid.csv`), and adds the
   hybrid to the existing 4-zone word+document chart (now 4 variants
   overlaid: production/spaCy-baseline/axis-similarity/hybrid).
3. **Complete**: `tests/test_axis_weighting.py`, 3 new tests (modifier
   boosts both poles equally via abs value, modifier=1 for
   axis-orthogonal words, OOV terms keep unmodified plain-TF-IDF
   weight). Full suite: 46/46 passing.
4. **Complete**: this journal entry, and
   `outputs/hybrid-weighting-comparison.md` (factual report).

## Key results (2026-07-19, corrected same day)
- **Top-token identity reverted toward TF-IDF**: hybrid agrees with
  spaCy-baseline on 28/44 top tokens and production on 25/44, but only
  3/44 with Phase-1 axis-similarity. 31 unique top tokens (same as
  production/spaCy-baseline; axis-similarity had 20). Words like
  "number" and "mr." reappear at the top of several pieces — the
  [1, 2]-bounded modifier is not enough to overturn TF-IDF's much larger
  dynamic range in most pieces.
- **Inter-article separation: the modifier's isolated effect is
  negligible, corrected from an earlier overstated claim.** The first
  pass compared the hybrid's separation against *production's* and
  reported "recovered, exceeded production in 3/4 zones" — but that
  comparison is confounded, since production differs from the hybrid in
  two ways at once (corrected-vs-plain TF-IDF, and POS-filter-vs-
  stopword-list preprocessing). The true single-variable control is
  spaCy-baseline (identical preprocessing and TF-IDF formula to the
  hybrid, differing only by the modifier). Against that control, the
  modifier changes separation by only 0.0004-0.0012 in every zone —
  negligible next to the ~0.01-0.02 shifts seen elsewhere in this
  project. spaCy-baseline's plain TF-IDF already had separation
  comparable to or exceeding production's *before* any modifier was
  added (e.g. Headline+Lead: spaCy-baseline 0.0545 vs. production
  0.0522) — the earlier framing attributed that pre-existing property to
  the modifier by comparing against the wrong baseline.
- **What the modifier does measurably do**: change the top-ranked token
  in 16 of 44 pieces (28/44 unchanged vs. spaCy-baseline) without a
  corresponding effect on inter-article separation — consistent with a
  [1,2]-bounded multiplier being enough to flip which single word wins
  the max within a piece, without shifting the overall weighted average
  enough to change how separated that piece's score is from others.
- See `outputs/hybrid-weighting-comparison.md` for full figures and the
  correction; no interpretation of what to do next is included there.

## Extension (2026-07-19, same day): product-form hybrid, no floor

**Student's diagnosis**: the floored `(1 + abs(cosine))` modifier only
ever boosts, never suppresses, so TF-IDF's much wider dynamic range keeps
winning — axis-irrelevant tokens like "number" stay weighted too highly.
Proposed dropping the floor entirely: `weight = TF * IDF * abs(cosine_similarity)`,
so an axis-irrelevant word gets crushed toward zero regardless of rarity.

**One objection raised and resolved before implementing**: does this
revive the same risk that sank AHC/KMeans-based axis-vocabulary selection
(spec 003 lit-review discussion) — mathematical proximity picking up
co-occurrence noise rather than genuine relevance? Student's counter,
accepted as valid: AHC/KMeans risk was specifically about *unsupervised
discovery* (letting co-occurrence structure in the data decide which
words cluster together); this weights tokens by distance to a single,
already-validated, theory-grounded coordinate (the axis itself), not by
discovering structure. Different operation, and whatever residual risk
remains is a property of using cosine-similarity-to-axis at all — which
every variant in this project already depends on for the final
projection score, not something unique to this weighting choice.

**Implemented**: `compute_weights_hybrid_product` (`src/axis_weighting.py`).
OOV terms dropped entirely (no defensible default modifier without a
floor). 4 new tests (49/49 suite passing). Full comparison:
`outputs/product-hybrid-comparison.md`.

**Key results**:
- Top-token identity sits genuinely in between the extremes: 32 unique
  top tokens (more than any other variant — production/spaCy-baseline
  31, floored hybrid 31, axis-similarity 20), only 27/44 agreement with
  the floored hybrid, 11-15/44 with the TF-IDF-based variants.
- Inter-article separation, against the true control (spaCy-baseline):
  overall stdev 0.0222 -> 0.0173, a real drop (though smaller than
  Phase-1 axis-similarity's drop to 0.0141) — Whole and Body zones drop
  notably (0.0253->0.0208, 0.0271->0.0248), Headline+Lead is unchanged
  (0.0545->0.0547), End rises (0.0283->0.0320).
- **Net picture**: removing the floor moved top-token identity much
  further from TF-IDF (as intended) at a real, non-negligible cost to
  separation — smaller than Phase 1's cost, but not the "best of both"
  outcome the floored hybrid's (misattributed) figures had originally
  seemed to promise. This variant sits as a genuine middle point between
  axis-similarity and TF-IDF on both statistics, not a variant that beats
  each on its own strength.
