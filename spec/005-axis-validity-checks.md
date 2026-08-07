# Spec 005 — Axis Validity Checks

Status: **Complete (2026-07-22)** — three independent checks, retroactively
specified (built reactively across one conversation, documented here per
governance's spec-first requirement — see journal 2026-07-22 for the
turn-by-turn reasoning).

Maps to: student's own critique of the axis-similarity/product-hybrid
family (specs 003/004) — real separation exists across the 11-article
corpus, but does it reflect genuine credibility-relevant language, or
could it be explained by (a) axis-size sensitivity, (b) the axis simply
detecting nothing more specific than "ordinary positive-valence English,"
or (c) generic stylistic register (sentence length, word choice) rather
than credibility-specific signal? Each check below targets one of these
three alternative explanations directly.

## Goal (one sentence)
Stress-test what the credibility axis actually measures, using three
independent checks that don't depend on each other: axis-size sensitivity,
a known-non-credible control text, and a register/formality confound
check — each targeting a distinct alternative explanation for the
separation found in specs 001-004.

## WHAT

### Check 1 — Small (4-vs-4) axis vs. large (21-vs-22) axis
- **New**: `build_small_axis(model)` (`src/axis.py`) — the Lit Review
  §2.2 proof-of-concept axis (`honest/true/accurate/impartial` vs.
  `dishonest/untrue/inaccurate/biased`), same normalize-then-average
  "grouped pairs" construction as `build_axis`, smaller word lists only.
- **New**: `src/small_axis_ablation.py` — projects production,
  spaCy-baseline, and product-hybrid document vectors onto both axes.
  For production/spaCy-baseline (axis-independent weighting), the same
  vectors are reprojected onto both axes. For product-hybrid, the axis
  enters the weighting formula itself, so weights are fully recomputed
  against the small axis too ("everywhere" scope, not just the final
  projection — student's explicit choice when asked).
- Comparison tables, top-token identity (product-hybrid only, since it's
  the only variant whose weights depend on axis size), and word+document
  zone charts using the small axis's own 8-word list.

### Check 2 — Control text (USS Maine, 1898)
- A single known non-credible/propagandistic historical text (Hearst's
  Feb 17, 1898 *New York Journal* front page — the textbook "yellow
  journalism" case study; see `data/control/SOURCE.md` for full
  provenance and why 20th-century totalitarian propaganda was considered
  and rejected as a source). Not part of the 11-article production
  corpus.
- Run through two weighting schemes that need no shared corpus — flat
  (TF-only) and axis-similarity (`compute_weights_axis_similarity`) —
  since joining a 12th document into the real per-zone corpora would
  change their IDF statistics. `src/control_text_check.py`.
- Compared against the production corpus's own flat-weighted and
  axis-similarity-weighted Whole-zone score ranges.

### Check 3 — Register/formality confound
- Three standard stylometric measures per article (average sentence
  length, average word length, type-token ratio) — deliberately *not*
  another GloVe axis, since building a second embedding axis to check the
  first would raise the same word-selection-validity question one level
  removed. `src/formality_check.py`.
- Pearson correlation (n=11, Whole-zone scores) against each weighting
  variant's credibility score.

## WHY
Directly answers three distinct "is this actually measuring credibility"
objections raised in discussion, each with its own control rather than
argued in the abstract:
1. Is the 21-vs-22 word axis's stability itself real, or an artifact of
   an arbitrarily large word list? (Check 1)
2. Does the axis distinguish genuinely non-credible writing from
   legitimate journalism, or does *any* ordinary English text score
   similarly? (Check 2)
3. Is the real inter-article separation found in specs 001-004 explained
   by generic house style rather than credibility-specific language?
   (Check 3)

## CONSTRAINTS
- No modification to the real 11-article corpus's own saved statistics
  (Check 2's corpus-contamination concern) — flat and axis-similarity
  weighting were chosen specifically because they need no shared corpus.
- Check 2's control text sourcing avoided real contemporary/named
  individuals (slander) and hate-propaganda targeting real ethnic/social
  groups (most well-documented 20th-century propaganda examples) — see
  `data/control/SOURCE.md` for the full reasoning.

## RISKS
1. Check 1: the small axis has only 8 words total vs. 43 for the large
   axis — any single word's idiosyncrasy has proportionally more
   influence; not fully independent evidence of "size doesn't matter in
   general," only evidence about *this specific* size reduction.
2. Check 2: single text, single era (1898) — GloVe was trained on modern
   text, so archaic phrasing could behave differently in embedding space
   than a contemporary example would. Suggestive, not a systematic study.
   Also uses flat/axis-similarity weighting only — doesn't directly test
   how production/spaCy-baseline/product-hybrid would score this text.
3. Check 3: three stylometric measures are a reasonable but not
   exhaustive set (don't capture tone, quoted-speech ratio, passive
   voice). n=11 gives wide confidence intervals — "no strong correlation
   detected" isn't the same as "definitively zero relationship."

## SUCCESS / ACCEPTANCE CRITERIA
- Check 1: comparison tables + 4 zone charts on the small axis; no crash.
- Check 2: scores + top-5-token report for both weighting schemes,
  compared against the production corpus's own range for the same scheme.
- Check 3: correlation table across all three weighting variants and all
  three register measures.
- All three: factual/no-conclusions summary reports, per this project's
  established Data-role convention.

## TASK BREAKDOWN
1. **Complete**: `build_small_axis` + `src/small_axis_ablation.py` +
   4 zone figures + `outputs/small-axis-comparison.md`.
2. **Complete**: `data/control/uss_maine_1898.txt` + `SOURCE.md` +
   `src/control_text_check.py` + `outputs/control-text-comparison.md`.
3. **Complete**: `src/formality_check.py` +
   `outputs/register-confound-check.md`.
4. **Complete**: this spec (retroactive) and journal entry.
5. **Not done**: unit tests for `build_small_axis` were added
   (`tests/test_axis.py`, 3 tests) but the control-text and
   register-confound scripts have no dedicated tests — both are one-off
   analysis scripts producing reports, not pipeline components reused
   elsewhere, so this follows the project's existing pattern of testing
   `src/` pipeline modules rather than one-off report-generation scripts
   (e.g. `src/naive_baseline.py`'s `main()` also has no direct test).

## Key results (2026-07-22)

**Check 1 (small vs. large axis)**: mean absolute rank shift 3.18-3.82
across all three variants — comparable to smaller-effect ablations
already in this project (POS-filtering: 2.41; production-vs-spaCy-
baseline: 3.45), well below the largest (axis-similarity comparisons:
7.6-9.2). Product-hybrid top-token identity: 33/44 pieces agree between
axes. Consistent with Kozlowski et al.'s own claim (more words -> more
stability) in the expected direction, though individual-piece rank
shifts (max 10-13) show axis size isn't inconsequential either.

**Check 2 (control text)**: scores 0.2379 (flat, large axis) and 0.3203
(axis-similarity, large axis) — both landing just below the entire
production corpus's own Whole-zone range for the same scheme (flat:
0.2390-0.2641; axis-similarity: 0.3340-0.3639), never negative. Confirms
the axis does not function as a fabrication/fake-news detector — a real,
useful scope limitation to state explicitly, not evidence the whole
method is void (see journal 2026-07-22 for the full "pointless vs. scope
correction" discussion).

**Check 3 (register confound)**: all correlations weak-to-moderate
(|r| = 0.061-0.339 across all three variants and all three register
measures) — well below the ~0.6-0.7 magnitude that would indicate house
style is the dominant driver of the separation found in specs 001-004.
Evidence against the crudest version of the house-style confound, not
proof against every possible stylistic explanation.

**Net effect on the project's framing**: the axis should be described as
measuring *relative* impartiality-of-framing among sources presumed to be
operating in good faith — not as a general credibility/fake-news
classifier, and not as something reducible to generic register. Both the
overclaim ("this detects credibility generally") and the overcorrection
("this is pointless, it only proves language is positive") were
considered and rejected in favour of this narrower, defensible framing.
