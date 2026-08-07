# Spec 002 — Naive/Standard-NLP Baseline Ablation

Status: **Complete (2026-07-19)** — all 8 tasks done, see Task Breakdown.

Status (approval history): Approved, amended 2026-07-19 — scope widened from one stopword
list to two (spaCy and NLTK, run and compared side by side) plus explicit
key-statistics and axis-projection comparison reports, per student
instruction ("use spacy and nltk and compare key statistics as well as
axis projections. provide readable summary reports do not draw
conclusions"). NLTK is already installed in this environment with its
stopwords corpus already downloaded (verified — no install/download step
needed), and its use here is explicitly approved by the student (Developer
role: "do not introduce dependencies the student has not approved").

Maps to: spec 001's existing ablation pattern (tasks 14-15 — TF-IDF vs.
flat, POS-filtered vs. unfiltered). This is a third, independent ablation
in the same family.

## Goal (one sentence)
Build a third preprocessing/weighting variant — generic stopword +
punctuation removal instead of POS-tag grammatical filtering, and an
unmodified/plain TF-IDF formula instead of the continuity-corrected,
high-TF-capped one — run through the same segmentation → compression →
axis-projection chain as the production pipeline, to see how the ranking
differs under standard-practice choices instead of this project's
custom design.

## WHAT
1. **New preprocessing variant** in `src/preprocessing.py`: one function
   parameterised by *which* stopword set to use, rather than two
   near-duplicate functions (single-responsibility: one function, one
   new parameter, not a copy-paste per list).
   - NER removal (denylist `EntityRuler` + broad statistical pass)
     **unchanged** — stays exactly as in production, for both variants.
   - Remove POS-tag category filtering entirely, for both variants.
   - Instead: drop any token whose lowercased text is in the given
     stopword set, and drop any token where `token.is_punct` is true (the
     standard spaCy signal for punctuation, used directly rather than the
     production pipeline's "single non-alphanumeric character regardless
     of POS tag" workaround — that workaround exists specifically to
     patch POS-tagger errors, which doesn't apply once POS tags aren't
     being used for filtering at all).
   - Two concrete stopword sets: spaCy's `nlp.Defaults.stop_words` (326
     words) and NLTK's `stopwords.words('english')` (198 words) — see
     spec discussion above for their measured overlap (123 words) and
     divergence.
2. **New weighting variant** in `src/tfidf.py`: a new function (sibling
   to `compute_weights`/`compute_flat_weights`), plain
   `idf(t) = ln(N/df(t))` computed per zone-type corpus exactly as now,
   but with **no continuity correction** (a term in all 11 documents gets
   exactly `idf=0`, not the `N-0.5` floor) and **no high-TF cap** (no
   override regardless of how many times a term repeats in one piece).
   TF stays raw count, same tokens, same zone-grouping logic
   (`group_by_zone`) — only the two corrections are removed. Shared by
   both stopword-list variants, so preprocessing (which stopword list) is
   the only thing varying between them.
3. Run the resulting weights through **unchanged** `compress_corpus`,
   `build_axis`, `project` — nothing about compression or the axis itself
   is part of this ablation. Produces three parallel score sets:
   production (existing), spaCy-stopword baseline (new), NLTK-stopword
   baseline (new).
4. **Comparison tables** (axis projections), using the existing
   `write_comparison` pattern: production vs. spaCy-baseline, production
   vs. NLTK-baseline, and spaCy-baseline vs. NLTK-baseline directly — same
   format as the two existing ablation comparison tables.
5. **Key-statistics comparison**: for each of the three variants, the same
   kind of descriptive statistics already produced for the production
   pipeline's top tokens (mean/stdev/variance of top-token weight by zone
   and by article — see `outputs/tables/top_token_per_piece.csv` and the
   figures built from it) — computed for the two new variants and placed
   alongside the production figures for comparison.
6. **Readable summary reports** (markdown, `outputs/`), factual only, no
   conclusions — matching `outputs/ablation-summary.md`'s existing style
   and the Data role's rule ("distinguish observation from inference"):
   one covering the axis-projection comparisons, one covering the
   key-statistics comparison.

## WHY
Extends the same standard already applied twice in this project (spec
001 tasks 14-15): don't just assert a design choice matters, measure it.
This ablation specifically tests spec 001 §3's and §4's own stated
reasons for departing from typical NLP practice (POS-tag filtering
instead of stopword lists; a corrected IDF instead of the textbook
formula) by actually running the textbook alternative and comparing.

**Explicitly, per the student**: the known conflicts this baseline
creates — stripping negation (`n't`, `never`), intensifiers (`very`,
`just`, `only`), and several modals (`would`, `could`, `might`, `must`),
all words the production preprocessing was specifically built to protect
(see `src/preprocessing.py` module docstring and spec 001 WHAT §3b) — are
the deliberate point of the comparison, not a defect to avoid. "We are
testing alternative methods against my design... there will be
contradictions we are trying to see how results differ."

## CONSTRAINTS
- Same 11-article corpus, same zone segmentation, same GloVe model, same
  credibility axis — only preprocessing and weighting change, consistent
  with how the two existing ablations are scoped (spec 001 Constraints).
- NLTK is a new dependency, explicitly approved by the student (2026-07-19
  instruction: "use spacy and nltk") — already installed with its
  stopwords corpus already present in this environment, so no install or
  `nltk.download()` step is actually required. Note its contracted-form
  entries (e.g. `"doesn't"`) will never match spaCy's split tokenization
  (`does`/`n't`) — an inert mismatch worth knowing about when reading the
  results, not a bug to fix.
- scikit-learn's `TfidfVectorizer` remains rejected in favour of the
  hand-rolled plain formula for the weighting variant, since sklearn
  bundles in smoothed `+1` IDF, its own L2-normalization, and its own
  tokenizer simultaneously — three confounds at once instead of isolating
  just the two corrections being tested.
- NER/denylist removal stays exactly as in production (not part of what's
  being tested — see WHY).

## RISKS
1. **This baseline is expected to strip protected words** (negation,
   intensifiers, modals) — any resulting rank shift may be partly or
   wholly attributable to this known, deliberate change rather than a
   novel discovery. Worth stating plainly in the write-up as a designed
   contrast, not treated as a surprise finding.
2. **Plain IDF at df=11 (all pieces contain the term) gives exact
   `idf=0`** — the same erasure-of-repetition-signal problem the
   continuity correction was built to fix (spec 001 WHAT §4) will recur
   here by design.
3. **No high-TF cap** — a single high-frequency surviving token could
   dominate a piece's vector the same way the original uncorrected
   formula did before the 2026-07-18 fixes (see journal, "TF-IDF
   weighting saga") — again, expected and part of what's being measured,
   not a bug to patch within this ablation.
4. Standard English stopword lists are built for general text, not this
   project's specific domain (sports/legal reporting) — spaCy's list may
   remove or keep words in ways that don't map cleanly onto "genuinely
   uninformative here."

## SUCCESS / ACCEPTANCE CRITERIA
- Three comparison tables (piece_id, both schemes' scores/ranks,
  rank_shift), covering all 44 pieces each: production-vs-spaCy-baseline,
  production-vs-NLTK-baseline, spaCy-baseline-vs-NLTK-baseline. Same
  format as the two existing ablation comparison tables.
- Mean/median/max absolute rank shift reported for each, following the
  same `_summarize` pattern already used for the other two ablations.
- Key-statistics comparison (top-token weight mean/stdev/variance by zone
  and by article) computed for all three variants.
- No crash, including at the df=N boundary (idf=0 case) and for any
  high-TF surviving token.
- Two readable summary reports (axis-projection comparison;
  key-statistics comparison), reported factually (Data role —
  observation, not conclusions), matching `outputs/ablation-summary.md`'s
  existing style.

## TASK BREAKDOWN (ordered, dependencies marked)
1. **Complete**: `src/preprocessing.py` — `clean_tokens_stopword_baseline`
   / `clean_corpus_stopword_baseline`, parameterised by stopword set (NER
   removal unchanged; `token.is_punct` for punctuation; no POS-tag
   filtering).
2. **Complete**: `src/tfidf.py` — `compute_idf_plain` /
   `compute_weights_plain` (no continuity correction, no high-TF cap).
3. **Complete**: `src/naive_baseline.py` runs all three pipelines —
   production (existing `run_pipeline`), spaCy-stopword baseline, NLTK-
   stopword baseline — through unchanged `compress_corpus`/`build_axis`/
   `project`.
4. **Complete**: three comparison tables in `outputs/tables/`:
   `naive_baseline_comparison_production_vs_spacy.csv`,
   `..._production_vs_nltk.csv`, `..._spacy_vs_nltk.csv`.
5. **Complete**: key-statistics extraction —
   `outputs/tables/top_token_per_piece_spacy_baseline.csv` and
   `..._nltk_baseline.csv`, alongside the existing production table.
6. **Complete**: two readable summary reports —
   `outputs/naive-baseline-axis-comparison.md`,
   `outputs/naive-baseline-key-stats-comparison.md` — factual only, no
   conclusions.
7. **Complete**: Test role — 7 new tests added across
   `tests/test_preprocessing.py` (stopword removal, punctuation removal,
   NER unchanged, negation/intensifier non-protection confirmed as the
   intended contrast) and `tests/test_tfidf.py` (`idf=0` exactly at
   df=11, agreement with the corrected formula away from that boundary,
   no high-TF cap applied). Full suite: 39/39 passing.
8. **Complete**: this journal entry — see 2026-07-19, "Spec 002 built:
   naive-baseline ablation (spaCy + NLTK)".

## Key results (2026-07-19)
- Largest single rank shift recorded across *all* ablations in this
  project so far: A6Z3, production rank 8 → spaCy-baseline rank 30 (shift
  of 22) — see `outputs/naive-baseline-axis-comparison.md` §1.
- 36/44 pieces pick an identical top-weighted token regardless of which
  of the three variants is used — see
  `outputs/naive-baseline-key-stats-comparison.md`.
- Full figures in the two summary reports; no interpretation included
  there per the student's explicit instruction.

## Task 9 (added 2026-07-19): word+document axis figures for all three variants
**Complete**: extended `src/axis_plot.py`'s word+document chart (spec 001
task 9a) to overlay production, spaCy-baseline, and NLTK-baseline
documents together on the same chart, one per zone-type
(`outputs/figures/naive_baseline_axis_words_and_documents_Z{1-4}.png`).
Required two small backward-compatible extensions to `axis_plot.py`:
`add_document()` gained an optional `kind` parameter (default
`"document"`, unchanged for existing callers) and `graph()` gained
optional `palette`/`markers` parameters (default to the original two-kind
scheme). Also fixed a real readability bug found while building this:
`graph()` was annotating every row, which is harmless when every label is
unique (the original single-variant case) but stamps the same "A1"/"A9"
text on top of itself 2-3 times once multiple variants share near-
identical scores for the same article — changed to one annotation per
unique label, positioned at that label's mean score. Verified no
regression by regenerating an original single-variant chart
(`axis_words_and_documents_Z4.png`) and comparing — pixel-identical
result, since labels were already unique there. Full test suite re-run:
39/39 still passing.

## Resolved decisions (2026-07-19, amended same day)
- NER/denylist removal: kept unchanged. Only grammatical-filtering style
  and the TF-IDF formula are being tested.
- Weighting: hand-rolled plain IDF, not scikit-learn's `TfidfVectorizer`
  — isolates exactly the two corrections' effect. Shared by both
  stopword-list variants.
- Tokenizer: spaCy tokens kept (not NLTK's `word_tokenize`) — no second
  confound from different tokenization boundaries.
- Stopword lists: **both** spaCy's `nlp.Defaults.stop_words` and NLTK's
  `stopwords.words('english')` are run and compared directly (amended
  from the original single-spaCy-list plan), chosen specifically *despite*
  (not unaware of) their overlap with words the production design
  protects — confirmed by the student as the intended contradiction being
  tested, not an oversight.
