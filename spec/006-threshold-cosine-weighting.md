# Spec 006 — Thresholded Cosine-Relevance Weighting

Status: **Complete (2026-07-22)** — retroactively specified (built
reactively during discussion; see journal 2026-07-22).

Maps to: spec 003's deferred Phase 2 (thresholding at a single symmetric
`|cosine| < 0.2` cutoff — found at the time to leave 75% of pieces with
zero surviving negative-pole tokens, and left unbuilt). Revisited this
session with a key correction: an asymmetric threshold, motivated by a
diagnostic finding that the non-credible pole is structurally sparser in
GloVe's embedding space than the credible pole (fewer words sit strongly
negative-similar to the axis *at all*, independent of document content) —
first observed via the axis-geometry investigation (2026-07-19: only 2 of
43 axis words ever win as nearest-neighbour for any real document) and
confirmed directly this session via threshold-survivor counts.

## Goal (one sentence)
Test a hard include/exclude gate on axis-relevance — a token keeps its
full plain-TF-IDF weight if its cosine similarity to the axis clears an
asymmetric threshold (`pos_threshold=0.25`, `neg_threshold=0.02`), or is
dropped entirely otherwise — as a substitute for the continuous cosine
modifiers in specs 003/004.

## WHAT
1. **New weighting function**, `compute_weights_threshold_cosine(pieces,
   model, axis, pos_threshold, neg_threshold)` (`src/axis_weighting.py`):
   `weight(t) = tfidf_weight(t)` if `cosine_similarity(t, axis) >
   pos_threshold` or `< -neg_threshold`, else the term is dropped
   entirely (not down-weighted). `tfidf_weight` is plain TF-IDF
   (`compute_weights_plain`), same base as the other cosine-modulated
   variants. Independent (not symmetric `|cosine|`) thresholds by design.
2. **Threshold selection, diagnosed before committing**: checked
   zero-survivor counts at several threshold pairs before running the
   full ablation (see Key Results) — symmetric thresholds from 0.05 to
   0.2 left 8-33 of 44 pieces with zero negative-pole survivors while
   0/44 ever lost positive-pole survivors; raising the positive threshold
   alone to compensate (0.25/0.3/0.35, paired with a fixed
   `neg_threshold=0.02`) flipped the imbalance the other way, and 0.30
   /0.35 each produced one piece with zero survivors on *both* poles (a
   genuinely empty document — `EmptyVectorError` territory).
   `pos_threshold=0.25`/`neg_threshold=0.02` was the best balance found
   (12/44 zero-positive-survivor pieces, 2/44 zero-negative, 0/44 fully
   empty).
3. **New ablation script**, `src/threshold_cosine_ablation.py`: runs the
   threshold-cosine variant (spaCy-stopword preprocessing, matching the
   other cosine-based variants), explicitly catches `EmptyVectorError`
   per piece (none triggered at the chosen threshold pair, but handled
   rather than assumed), and compares against production and
   spaCy-baseline.
4. Comparison tables, top-token-per-piece table, 4-zone word+document
   chart (added `threshold_cosine` to `VARIANT_PALETTE`/`VARIANT_MARKERS`
   in `src/naive_baseline.py`), and a standalone per-piece scores table
   (`outputs/tables/axis_projection_scores_threshold_cosine.csv`,
   matching the format of the other per-scheme scores tables).

## WHY
Tests whether a binary relevance gate — rather than a continuous
multiplier — better isolates the intended "lexical footprint": does
cutting the axis-irrelevant middle out entirely (rather than merely
down-weighting it) surface more visibly credibility-relevant vocabulary
and produce more real inter-article separation than any prior variant?

## CONSTRAINTS
- Same 11-article corpus, same zone segmentation, same GloVe model, same
  large axis.
- Asymmetric thresholds are a direct response to a measured property of
  this specific axis/embedding space (pole sparsity), not an arbitrary
  tuning choice — the diagnostic numbers are recorded in Key Results
  below, not just asserted.

## RISKS
1. **Structural artifact in "top token" comparisons**: thresholding
   doesn't only filter which words are eligible — it shrinks the
   competitor pool a "top token" is being judged against. A mediocre
   survivor (e.g. `banned`, weight 0.61, in a corpus where it appears in
   6-8 of 11 articles and therefore has low IDF) can win "top token" by
   default if the threshold gate removes most of its competition, not
   because TF-IDF judged it genuinely distinctive. Verified directly
   (see Key Results) — this is a real, word-specific effect, not
   uniform across every surfaced token.
2. **Topic-vs-credibility confound, same as every prior variant in this
   project**: several surfaced tokens (`banned`, `violations`, `scandal`,
   `contaminated`, `negligence`) describe the doping case's actual
   subject matter. Document-frequency checks (Key Results) show this
   cuts both ways word-by-word: some (`violations`, `scandal`: 1/11 docs)
   are genuinely rare and legitimately distinctive; others (`banned` in
   Headline+Lead/Body: 6-8/11 docs) are common enough that their
   surfacing is closer to risk 1 (shrunken-pool artifact) than genuine
   rarity-based distinctiveness.
3. Same corpus-composition caveat as every axis-relevance-weighted
   variant: this is a same-event corpus, so "rare" can only ever mean
   "rare for this one story," not "rare relative to how this kind of
   situation is normally described" (see discussion, journal 2026-07-22,
   on the context-vs-genre distinction and proposed multi-topic/genre-
   routed future-work architecture).

## SUCCESS / ACCEPTANCE CRITERIA
- Threshold pair selected via diagnostic, not guessed.
- Comparison tables vs. production and spaCy-baseline, top-token table,
  4 zone figures, standalone scores table.
- 0/44 pieces crash or silently produce a degenerate (empty) vector.

## TASK BREAKDOWN
1. **Complete**: `compute_weights_threshold_cosine`
   (`src/axis_weighting.py`) + 5 new tests (`tests/test_axis_weighting.py`
   — clears positive threshold, clears negative threshold, dropped
   between thresholds, asymmetric-threshold behaviour, OOV dropped).
   Full suite: 57/57 passing.
2. **Complete**: `src/threshold_cosine_ablation.py`, 2 comparison tables,
   1 top-token table, 4 zone figures, 1 standalone scores table.
3. **Complete**: `outputs/threshold-cosine-comparison.md` (factual
   summary) and this spec + journal entry.
4. **Complete (added 2026-07-22, later same day)**: a second,
   statistically-grounded threshold pair (`POS_THRESHOLD_RANDOM_BASELINE
   = 0.194`, `NEG_THRESHOLD_RANDOM_BASELINE = 0.096` in
   `src/threshold_cosine_ablation.py`) — see "Statistically-grounded
   threshold pair" below.

## Statistically-grounded threshold pair (added same day)

The tuned pair above (0.25/0.02) was optimised for pipeline robustness
(avoiding empty pieces), not statistical defensibility — its 0.02
negative threshold admits words with only a ~23-30% "clears this by pure
chance" rate against a random-word baseline (see Risks). A second pair
was derived instead as the 95th/5th percentile of 1000 random common
English words' cosine similarity to the axis — a word outside this range
has roughly a 90% chance of not being there by chance (10% two-tailed
noise rate), vs. the tuned pair's much weaker odds.

**This derivation was originally run as inline one-off scripts during
the session and was not reproducible from the repo alone until
`src/threshold_derivation.py` was added later (2026-07-22, prompted by
the student asking why they couldn't reproduce the exact numbers from a
different session)** — the constants were persisted in
`threshold_cosine_ablation.py`, but the *procedure* that produced them
wasn't saved anywhere runnable. `src/threshold_derivation.py` fixes
this: running `python -m src.threshold_derivation` regenerates
0.194/0.096 exactly, given the same GloVe model, vocabulary slice (top
20000 words, alphabetic, length > 2), sample size (1000), and seed (42)
— all four have to match for the same numbers to reproduce; matching
only the seed with a different vocabulary pool produces a different,
equally legitimate threshold calibrated against a different reference
population, not an error. 3 tests in
`tests/test_threshold_derivation.py` lock in reproducibility (same seed
-> documented constants; same seed twice -> identical result; different
seed -> different result, expected not a bug). Sampling stability
(30 independent draws, percentile stdev ~0.006-0.007) was checked the
same day this pair was derived — see journal 2026-07-22.

**Open, acknowledged limitation, not yet resolved**: the reference
population is generic English vocabulary, not sports-news-domain-matched
— see spec 008, option 3, for the proposed (not yet built) fix.

## Key results (2026-07-22)

**Threshold diagnostic** (before running the full ablation):

| pos_threshold | neg_threshold | 0 positive-pole survivors | 0 negative-pole survivors | 0 on both poles |
|---|---|---|---|---|
| 0.05 | 0.05 | 0/44 | 8/44 | 0/44 |
| 0.10 | 0.10 | 0/44 | 14/44 | 0/44 |
| 0.15 | 0.15 | 0/44 | 20/44 | 0/44 |
| 0.20 | 0.20 | 0/44 | 33/44 | 0/44 |
| 0.25 | 0.02 | 12/44 | 2/44 | 0/44 |
| 0.30 | 0.02 | 18/44 | 2/44 | 1/44 |
| 0.35 | 0.02 | 23/44 | 2/44 | 1/44 |

`pos_threshold=0.25`/`neg_threshold=0.02` chosen: closest to balanced
degeneracy of the pairs tested, no fully-empty piece.

**Rank shift and separation, largest recorded in this project**:
mean absolute rank shift 9.59 (vs. production) / 9.32 (vs. spaCy-
baseline) — both exceed the previous largest (axis-similarity vs.
production, 9.23). Mean score delta -0.19 (threshold scores run
substantially lower on average). Inter-article separation stdev 0.0865,
range 0.2871 — roughly 4-6x every other variant's stdev (previous
largest: spaCy-baseline, 0.0222) and over 3x the widest range previously
recorded. First variant in the project where individual piece scores go
genuinely negative rather than clustering in a narrow positive band.

**Top-token identity**: 28 unique top tokens (vs. 31-32 for
production/spaCy-baseline/product-hybrid, 20 for axis-similarity). Reads
qualitatively more evaluative (`wrong`, `banned`, `sad`, `shameful`,
`deliberately`, `allegedly`, `negligence`, `contaminated`, `criticism`)
than any prior variant's top-token set.

**Document-frequency check on the "is this genuinely rare or just
topical" question** (word-by-word, per zone corpus, N=11):

| Word | Zone | df | idf | Assessment |
|---|---|---|---|---|
| negligence | Whole | 11/11 | 0.0 | Universal — correctly never wins here |
| negligence | End | 2/11 | 1.70 | Genuinely rare — legitimate win |
| banned | Headline+Lead | 6/11 | 0.61 | Common — wins by shrunken-pool default (weight only 0.61, low vs. other zones' 1.7-5.1) |
| banned | Body | 8/11 | 0.32 | Common, same caveat |
| banned | End | 2/11 | 1.70 | Genuinely rare in this zone — legitimate |
| violations | Whole | 1/11 | 2.40 | Genuinely rare — legitimate |
| scandal | Whole | 1/11 | 2.40 | Genuinely rare — legitimate |
| contaminated | Whole/Body | 2/11 | 1.70 | Comparatively rare — legitimate |

**Whole-article consistency** (a pattern this variant made visible that
was not visible in any prior weighting scheme, precisely because it
widened score dispersion enough to see it): 3 of 11 articles (A8, A10,
A11) have all 4 zones agree in sign under threshold-cosine — A8
notably tight (stdev 0.019 across its own 4 zones, consistently ~-0.05
to -0.08). Two more (A4, A5) agree in 3 of 4 zones, both times with
Headline+Lead as the sole negative outlier — across all 11 articles,
Headline+Lead is negative for 8/11, versus Body/End/Whole trending
positive far more often. Flagged as a genuinely interesting pattern
(possibly: headlines skew toward the non-credible pole more than body
text under this scheme) but not yet formally quantified beyond this
observation — a natural next check if this variant is pursued further.
