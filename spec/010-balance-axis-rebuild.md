# Spec 010 — Balance/One-Sidedness Axis: Full Rebuild

Status: **Scope decided by Jordan, 2026-07-26 — supplementary axis, not
a full pivot.** After reviewing the token-level pole diagnostic (see
"Token pole diagnostic" addendum below), Jordan's own conclusion: "this
axis is good to include in the methodology but not worth the complete
pivot" — the balance axis stays in the dissertation as a genuine,
documented supplementary/comparative axis alongside the credibility
axis (methodology chapter, findings already gathered: axis construction,
Corpus B/ESPN rebuild, control-text check, Corpus A whole-document
check), **not as its replacement**. Jordan's own stated reasoning: the
threshold-cosine token-level diagnostic shows individual word placements
that "are not reflective of semantic framing" (e.g. "facts" and "video"
landing on the unbalanced pole, "anchored" landing on the balanced pole)
— read by Jordan as evidence of a deeper limitation: a single linear
axis can't cleanly separate the multiple non-linear, overlapping
abstractions that make up "balance" and "credibility" as constructs.
**Practical effect on this spec's task list**: task 3 (the full
7-variant × 4-zone rebuild on Corpus A) and task 6 (register-confound
check) are **not being pursued** under this scope decision — the work
already done (tasks 1, 2, 4, 5, plus the addenda below) is judged
sufficient to support "supplementary axis, documented trade-offs and
limitations" in the dissertation, without needing the full parity
rebuild that would be required to argue the balance axis as a complete
replacement. If Jordan wants task 3/6 revisited later for a different
reason, that would need fresh reasoning, not an assumption this
decision was incomplete.

Prior status history (2026-07-25): Task 1 (`build_balance_axis` in
`src/axis.py` + tests) was already complete as of the first update to
this spec this session — the spec previously said "not yet added,"
which was stale; caught and corrected while re-reading the spec before
starting new work, not left uncorrected.

## Naming convention, confirmed by Jordan (2026-07-26)
**Corpus A** = the original 11-article corpus (specs 001-006, 4 zones per
article). **Corpus B** = the ESPN World Cup corpus (spec 007, 53
articles, whole-document only). Resolves the assumption flagged in task
4's journal entry ("Corpus B" taken to mean ESPN, not yet confirmed) —
now confirmed correct, and the pairing (Corpus A for the original) is
new information. Use this naming in all future spec/journal entries
rather than "the original 11-article corpus" / "the ESPN corpus" for
brevity, now that it's an established, Jordan-confirmed convention.

## Addendum (2026-07-25) — vocabulary-wide top-20 words scatter + hub-word geometry check
Requested directly by Jordan in chat, not part of the original tasks 1-8
above. Reuses `build_balance_axis` (already built) and the
axis-geometry-investigation precedent from 2026-07-19 (nearest-word/
hub-word concentration check on the credibility axis, memory summary
in `msc-project-semantic-axis`), applied fresh to the balance axis:

1. Project a broad reference vocabulary (reusing
   `threshold_derivation.build_reference_vocab` — top 20000 GloVe words,
   alphabetic, length > 2 — for consistency with the rest of the
   project's methodology rather than picking a new filter) onto the
   balance axis via cosine similarity; take the top 20 highest-scoring
   (balanced pole) and top 20 lowest-scoring (unbalanced pole) words.
   Scatter plot, same visual convention as `src/axis_plot.py`'s `graph()`.
2. Hub-word check: for these 40 words, compute each word's mean cosine
   similarity to a random sample of the same reference vocabulary
   (matching the 2026-07-19 "500 random common words" precedent) and
   compare across the 40 — is one word (or a few) disproportionately
   generic/hub-like the way "true" was on the credibility axis, or is
   similarity spread evenly? Reported factually (Data role), not assumed
   either way going in.
- **New module**: `src/balance_axis_top_words.py`, tested in
  `tests/test_balance_axis_top_words.py` — unlike the original
  2026-07-19 hub-word investigation (which was run inline and never
  saved, per the reproducibility-gap lesson already on record in the
  journal for `threshold_derivation.py`), this is saved as real,
  reusable, tested code from the start.

## Task 2 — done (2026-07-25): threshold-cosine degeneracy diagnosis for this axis
Statistically-grounded pair re-derived for the balance axis via
`threshold_derivation.derive_thresholds`: **pos=0.1087, neg=0.1347**
(single seed=42 draw — supersedes the 30-draw-average range quoted
above, which was an exploratory estimate, not the canonical value to
use going forward). Degeneracy check on the ESPN corpus (Corpus B, task
4 below): **3/53 pieces zero positive-pole survivors, 0/53 zero
negative-pole, 0/53 zero on both poles.** Answer to RISK 1: **no
degeneracy-avoidance "tuned" pair is needed for this axis** — the single
statistically-grounded pair is already non-degenerate (no piece loses
scoring entirely), unlike the credibility axis, which needed the
asymmetric tuned pair (spec 006) specifically because its negative pole
was structurally sparse.

## Task 4 — partially done (2026-07-25): ESPN corpus (Corpus B) rebuild
Requested directly by Jordan in chat: standard baseline (spaCy-stopword +
plain TF-IDF, no cosine gate — not originally listed in task 4 above,
added at Jordan's explicit direction this session), production, and
threshold-cosine (the pair from task 2) all run against the balance axis.
**New module**: `src/espn_worldcup_balance_axis_check.py`, tested in
`tests/test_espn_worldcup_balance_axis_check.py`. Full comparison in
`outputs/espn-worldcup-balance-axis-comparison.md`
(`outputs/tables/espn_worldcup_*_balance_axis.csv`). Reported factually
(Data role) — see journal 2026-07-25 for the numbers; not reproduced
here to avoid a second copy going stale.
**Not yet done from task 4's original scope**: nothing further — task 4
only ever specified production + threshold-cosine on this corpus, both
now covered.

## Task 5 — in progress (2026-07-26): control text (USS Maine, 1898) on the balance axis
Requested directly by Jordan in chat. Reuses the existing control-text
machinery unchanged in method (`src/control_text_check.py`'s flat +
axis-similarity weighting, `src/control_text_threshold_check.py`'s
threshold-cosine weighting) — both `compute_weights_axis_similarity` and
`compute_weights_threshold_cosine` are already axis-parametrized, so no
new weighting formula is needed, matching spec 010 CONSTRAINTS. Only the
axis vector (`build_balance_axis` instead of `build_axis`) and the
threshold pair (this axis's own 0.1087/0.1347 from task 2, instead of the
credibility axis's 0.194/0.096) change.
**New module**: `src/control_text_balance_axis_check.py`, tested in
`tests/test_control_text_balance_axis_check.py` (4 tests). Since the
original 11-article corpus hasn't been rebuilt against the balance axis
yet (task 3, still not started), this task computes just enough of a
comparison point itself — flat and axis-similarity weighted balance-axis
scores for the 11 articles' Whole (Z4) pieces, and the same temporary
12-document threshold-cosine corpus construction as
`control_text_threshold_check.py` — without pre-empting or duplicating
the full task-3 rebuild. **Done, 2026-07-26.** Results: flat -0.0298 vs.
Whole(Z4) range -0.0355 to -0.0167 (control sits at the low end, not
outside it); axis-similarity -0.0406 vs. -0.1049 to -0.0207 (well within
range); threshold-cosine -0.1042 vs. -0.1593 to +0.0902 (also within
range, on the low side). Full detail:
`outputs/control-text-balance-axis-comparison.md`. Reported factually, no
conclusions drawn on what "within range" means for the axis's validity —
that's Jordan's to interpret, especially since these Whole-zone
comparison scores are freshly computed for this check only, not the
canonical task-3 rebuild figures.

## Addendum (2026-07-26) — Corpus A, whole-document only, 4 variants + control text
Requested directly by Jordan in chat: Corpus A's 11 articles treated as
whole documents only (no zone segmentation — Z4/Whole already *is* the
full article text, per `src/segmentation.py`'s own Z4 definition, so this
needs no new corpus construction, just restricting to the 11 existing Z4
pieces), run through **standard baseline** (spaCy-stopword + plain
TF-IDF), **production** (POS-filtered, continuity-corrected TF-IDF),
**threshold-cosine** (this axis's own pair, task 2), and **product
hybrid** (`compute_weights_hybrid_product`, added "just to see if that
interacts any differently" — exploratory, not part of spec 010's
original task list) — all against the balance axis, with the USS Maine
control text folded in as a 12th document (same temporary-corpus
technique as task 5) so it can be seen against all 11 real whole
articles under all 4 schemes at once. **New module**:
`src/corpus_a_whole_balance_axis_check.py`, tested in
`tests/test_corpus_a_whole_balance_axis_check.py` (3 tests). Distinct
from task 3 (the full 7-variant × 4-zone rebuild, still not started) —
this is whole-document-only and scoped to the 4 variants Jordan asked
for here, not a substitute for task 3. **Done, 2026-07-26.** Per-variant
charts use a tight xlim (min/max of that variant's own scores ± 0.01,
via a new optional `xlim` param on `src.axis_plot.graph`, default
unchanged for every other caller) rather than the shared -0.65/0.65
range, and omit axis words entirely (they'd fall outside this tight
range and be invisible anyway). Results: standard baseline and
production nearly identical (control -0.0383 vs -0.0444, article ranges
both roughly -0.06 to +0.01); threshold-cosine widest spread by far
(-0.1593 to +0.0902) and the only variant where 2 real articles
(A6Z4, A9Z4) score more negative than the control text; product hybrid
(exploratory, not in spec 010's original scope) pulls everything
noticeably more negative than the two plain-TF-IDF variants (control
-0.0616, article range -0.1325 to +0.0125) — closer in spread to
threshold-cosine than to standard/production despite not gating tokens
out. Full numbers: `outputs/corpus-a-whole-balance-axis-comparison.md`.

## Addendum (2026-07-26) — survivor-count vs. score correlation, both axes
Requested directly by Jordan in chat: test whether the number of tokens
surviving the threshold-cosine gate correlates with a piece's score, the
same check he recalled being done on the credibility axis previously
(recalled value: r² ≈ 0.54). **No derivation script or saved output for
that exact prior number was found anywhere in the repo** (journal,
key-findings, outputs/*.md all searched) — same reproducibility-gap
pattern already on record for `threshold_derivation.py`. Rather than
trust the unreproducible recalled figure, built this fresh as reusable
code (`src/survivor_count_correlation.py`, tested in
`tests/test_survivor_count_correlation.py`, 6 tests) for both axes on the
ESPN corpus (Corpus B), using `np.corrcoef` (Pearson r) matching
`src/formality_check.py`'s existing convention. Results in journal
2026-07-26.

## Addendum (2026-07-26) — token pole diagnostic, and the scope decision it prompted
Jordan asked directly: how is the control text (USS Maine, 1898) *less*
unbalanced than two real Corpus A articles (A6Z4, A9Z4) under
threshold-cosine weighting? Investigated by hand first, then saved as
reusable code per Jordan's follow-up request: **New module**:
`src/token_pole_diagnostic.py`, tested in
`tests/test_token_pole_diagnostic.py` (4 tests). For every token
surviving the threshold-cosine gate in every Corpus A whole-document
piece + control (spec 010's earlier addendum), records its own
cosine-to-axis value and which pole it lands on — full table:
`outputs/tables/corpus_a_whole_balance_axis_token_pole_diagnostic.csv`.

**Mechanism found**: the final score is the cosine of the *whole*
weighted-average document vector, so positive-pole and negative-pole
survivors partially cancel out — it is not just "how dramatic does the
top-weighted word sound." Control's two biggest survivors ("destruction"
-0.157, "accident" -0.141) pull negative, but "anchored" (+0.213, the
single strongest pull found anywhere in this comparison) and "capital"
(+0.129) land on the *balanced* pole and substantially offset them. By
contrast A6Z4's "shameful" (-0.328, the most extreme value found) isn't
offset by its weaker positive survivors, and A9Z4 (only 11 total
survivors — small pieces let a couple of extreme words dominate) has 3
negative-pole survivors against 2 positive, including "facts" (-0.159)
landing on the *unbalanced* pole despite reading as neutral/evidentiary
in plain English.

**Jordan's own conclusion from this**, stated directly in chat: several
individual-word placements ("fact[s] is unbalanced and video is
unbalanced, anchored is largely balanced") "are not reflective of
semantic framing" — read as evidence that "the limitation of the whole
experiment is the inability to conflate multiple abstracts that make up
this non-linear idea of balance and credibility." This is Jordan's own
interpretive judgement, not the agent's — recorded here verbatim per
governance's accountability requirement, not paraphrased into a weaker
or stronger claim. **This is the reasoning that produced the scope
decision recorded in this spec's Status section above** (supplementary
axis, not full pivot; task 3/6 not being pursued).

## Addendum (2026-07-26) — same pole diagnostic on Corpus B (ESPN), grouped by net pole lean
Requested directly by Jordan: apply the same per-piece pole-survivor
counting to Corpus B (the ESPN corpus, 53 articles, threshold-cosine
weighting, this axis's own derived pair) instead of Corpus A, but grouped
differently — for each piece, `diff = n_balanced_survivors -
n_unbalanced_survivors` (negative when a piece has more unbalanced-pole
survivors, e.g. -1/-2/-3/-4), then bucket pieces into "positive pole"
(diff > 0), "negative pole" (diff < 0), and "tied" (diff == 0, reported
separately rather than folded into either bucket), and sum the diffs
within each bucket. **New module**:
`src/corpus_b_pole_diagnostic.py`, reusing
`token_pole_diagnostic.compute_token_diagnostics`/`summarize` unchanged
(both already corpus-agnostic) against Corpus B's threshold-cosine
weights. Tested in `tests/test_corpus_b_pole_diagnostic.py`.

## Roles used (per Appendix A.2 declaration format)

| Role | Justification for this task | Skills file |
|---|---|---|
| Planner | Decomposes the credibility-to-balance pivot into a scoped rebuild plan before any further implementation; surfaces the axis-word-list ownership question and validation-staging trade-off explicitly rather than deciding either unilaterally. | `skills/planner/SKILL.md` |
| Developer | Rebuilds the weighting battery, ESPN corpus run, and validity checks against the new axis, reusing existing weighting-function code unchanged — only the axis vector passed in changes. | `skills/developer/SKILL.md` |
| Test | New axis construction (`build_balance_axis`) and its threshold derivation need their own tests, matching how `build_axis`/`build_small_axis` and `threshold_derivation.py` are already tested. | `skills/test/SKILL.md` |
| Review | Independent check that re-running the full battery against the new axis doesn't silently alter or overwrite any of the existing credibility-axis outputs already used in the dissertation. | `skills/review/SKILL.md` |
| Data | Interprets the resulting scores/separation/top-token findings for the new axis, same role this project has used throughout. | `skills/data/SKILL.md` |
| Reflection | Journal entries throughout, per standing practice — already under way for this pivot (2026-07-25 entries). | `skills/reflection/SKILL.md` |

Compliance not invoked — no new data-handling or copyright question, this
task only adds a new axis construction and re-runs existing pipelines
against it. Architect and Adversarial/Red-Team not used, same reasoning
as prior specs.

## Goal (one sentence)
Rebuild the full weighting-scheme battery, the ESPN corpus run, and the
axis-validity checks against a new "balance/one-sidedness" axis instead
of the original credibility axis, keeping every existing credibility-axis
weighting variant unchanged and every existing output untouched, so the
two axes' results can sit side by side in the dissertation rather than
one replacing the other's evidence trail.

## Context: why this axis, why now
Established this session (2026-07-25), full detail in
`journal/agent-journal.md` and `key-findings/key-findings.md`:
- The original credibility axis conflates two different constructs —
  honesty/factual-accuracy language (honest/dishonest, true/untrue) and
  impartiality/balance language (impartial/biased) — on the assumption
  they point the same direction. The axis-geometry investigation
  (2026-07-19) already showed "true" is the single most generic, hub-like
  word in the whole vocabulary, dominating nearest-neighbour scoring for
  39/44 documents for reasons unrelated to genuine relevance.
- A quick six-word test (amazing, incredible, unbelievable, stunning,
  shocking, outrageous) showed the credibility axis scatters hyperbole
  words almost arbitrarily by surface emotional valence, while a new
  balance-only axis flags all six consistently as exaggerated regardless
  of valence.
- The pole-balance null-distribution diagnostic (using the recovered
  original methodology, `src/threshold_derivation.py`) confirms this is a
  real, structural difference, not a small-sample impression: credibility
  axis pos/neg ratio 2.03-2.27 (skewed positive) across multiple
  reproduction attempts; balance axis ratio 0.81-0.97 (near-symmetric)
  across the same range of attempts.

## WHAT

### 1. Final axis construction (complete, this session)
`build_balance_axis(model)` — mean of 7 individually hand-reviewed
antonym-pair difference vectors, matching `build_axis`/`build_small_axis`'s
existing normalize-then-difference convention:

```
Axis = mean of (unit(A_i) - unit(B_i)) for i = 1..7:
  balanced - unbalanced
  measured - exaggerated
  proportionate - disproportionate
  restrained - sensational
  even-handed - one-sided
  moderate - extreme
  calm - dramatic
```

Three candidate pairs were reviewed and cut: tempered/overblown,
neutral/partisan. One pair (nuanced/simplistic) has an **unresolved**
review status — a multi-select answer's custom text wasn't visible to
the agent, was never clarified, and defaulted to excluded. **Flagged for
Jordan to revisit directly if he wants it reconsidered** — not assumed
either way beyond "currently not in the 7-pair list."

Not yet added to `src/axis.py` as a named function — needs to be, as
task 1 below, so it's reusable the same way `build_axis`/`build_small_axis`
are, rather than living only in this session's scratch scripts.

### 2. Threshold-cosine's threshold pair for this axis (partially complete)
The statistically-grounded pair (95th/5th percentile of the same
reference vocabulary `threshold_derivation.py` already uses) has been
derived: pos_threshold ≈ 0.115-0.206, neg_threshold ≈ 0.091-0.135
depending on exact draw (30-draw average, exact original methodology:
pos=0.1149, neg=0.1300). **Not yet decided**: whether this axis needs a
separate degeneracy-avoidance "tuned" pair the way the credibility axis
did (spec 006) — the credibility axis's negative pole was so
structurally sparse that a single symmetric threshold left many pieces
with zero negative-pole survivors, motivating the asymmetric 0.25/0.02
pair. Since this new axis's poles are close to balanced, it's a real
open question whether that degeneracy problem exists here at all, or
whether the single statistically-grounded pair is already non-degenerate
on its own. **Task 2 below diagnoses this before assuming either way.**

### 3. Full rebuild scope (approved by Jordan, not yet built)
Re-run against the new balance axis, reusing every existing weighting
function unchanged (only the axis vector passed in changes):
- **11-article corpus**: flat, production, spaCy-baseline, NLTK-baseline,
  axis-similarity, both hybrids (floored and product), threshold-cosine
  (both the re-derived statistically-grounded pair and whatever tuned
  pair task 2 determines is needed, if any).
- **ESPN 53-article corpus**: production and threshold-cosine (matching
  spec 007's + this session's own scope on the credibility axis).
- **Axis-validity checks**: control-text (USS Maine, 1898) under flat and
  axis-similarity weighting (matching spec 005's original scope) plus
  threshold-cosine (matching this session's extension of that check);
  register-confound check (sentence length, word length, type-token
  ratio vs. score, matching spec 005).

## WHY
Directly tests whether the pivot's promise (construct-cleaner axis,
demonstrated on a handful of words) holds up at the same scale and rigour
the credibility axis was tested at. A pivot that only works on six
hand-picked words isn't yet evidence it works on real, full-length
articles — this rebuild is what would actually support using the balance
axis as more than a suggestive footnote.

## CONSTRAINTS
- **Every existing credibility-axis output stays untouched.** New outputs
  use a distinct naming convention (e.g. `_balance_axis` suffix on table/
  figure filenames) rather than overwriting `outputs/tables/
  axis_projection_scores_tfidf.csv` etc. This is a new, parallel set of
  results, not a replacement of the dissertation's existing evidence base.
- **No new weighting formulas.** This rebuild changes which axis vector
  is passed into `project()` and, where relevant, into the
  cosine-similarity-dependent weighting functions (axis-similarity, both
  hybrids, threshold-cosine) — it does not modify `compute_weights`,
  `compute_weights_plain`, `compute_weights_axis_similarity`,
  `compute_weights_hybrid_*`, or `compute_weights_threshold_cosine`
  themselves.
- **Given the September 10th deadline**: no staged small-then-large
  validation (already decided) — the 7-pair axis is the one being tested
  directly, not a pilot to be expanded later.
- **The nuanced/simplistic pair's unresolved status stays unresolved**
  until Jordan says otherwise — not silently added or permanently
  discarded without him actually deciding it.

## RISKS
1. **Degeneracy risk for threshold-cosine on this axis is genuinely
   unknown** — task 2 must check before the full battery runs, since a
   degenerate threshold pair (many zero-survivor pieces) would need
   resolving the same way spec 006 resolved it for the credibility axis,
   not assumed away because the poles are more balanced in the null
   distribution.
2. **Real chance the pivot doesn't hold up at full scale** — the six-word
   test and the pole-balance diagnostic are both real, checked evidence,
   but neither is the same as running the whole pipeline on 44 real
   pieces of article text. A weak or null separation result on the real
   corpus is a legitimate, reportable outcome here, same as it was for
   the AllSides validation and the control-text checks — must not be
   softened or hidden if it happens.
3. **Timeline**: this is a large rebuild (9+ weighting variants x 2
   corpora x validity checks) against a September 10th deadline. Worth
   Jordan explicitly confirming the full scope is still wanted once he
   sees the task count below, rather than assuming "yes to everything"
   from the earlier AskUserQuestion answer holds under time pressure.

## SUCCESS / ACCEPTANCE CRITERIA
- `build_balance_axis` added to `src/axis.py`, tested the same way
  `build_axis`/`build_small_axis` are.
- Threshold-cosine's threshold pair(s) for this axis derived via the
  same reproducible procedure as `threshold_derivation.py`, with the
  tuned-pair-necessity question (RISK 1) explicitly diagnosed, not
  assumed.
- All weighting variants in scope run against the new axis without
  crashing or silently degenerating, matching the same "0 empty pieces"
  bar every prior variant has been held to.
- Every new output lives alongside, not in place of, the existing
  credibility-axis outputs.
- Results reported factually (Data role), including if separation is
  weak or the pivot doesn't clearly outperform the credibility axis at
  full scale — not just the encouraging six-word result repeated as if
  it were the full finding.

## TASK BREAKDOWN (ordered, dependencies noted)
1. Add `build_balance_axis` to `src/axis.py` with the 7 confirmed pairs;
   add tests (`tests/test_axis.py`), matching `build_small_axis`'s
   existing test pattern.
2. Diagnose whether threshold-cosine needs a second, degeneracy-avoidance
   threshold pair for this axis (checking zero-survivor-piece counts at
   several candidate pairs, same method as spec 006), or whether the
   single statistically-grounded pair is already non-degenerate. Depends
   on 1.
3. Re-run the core weighting battery (flat, production, spaCy-baseline,
   NLTK-baseline, axis-similarity, both hybrids, threshold-cosine) on the
   11-article corpus against the new axis; new comparison tables, using
   the `_balance_axis`-suffixed output convention. Depends on 1, 2.
4. Re-run production and threshold-cosine on the ESPN 53-article corpus
   against the new axis. Depends on 1, 2.
5. Re-run the control-text (USS Maine) check under flat, axis-similarity,
   and threshold-cosine weighting against the new axis. Depends on 1, 2.
6. Re-run the register-confound check (sentence length, word length,
   type-token ratio vs. score) against the new axis's scores. Depends on 3.
7. Factual summary report(s), Data role, matching this project's
   established no-conclusions-drawn convention.
8. Journal entries throughout (already under way); update
   `key-findings/key-findings.md` with the rebuild's actual results once
   in hand.

**Not started** — stopping here per the Planner role's own rule. Confirm
this scope (especially given RISK 3, the timeline) before task 1 begins.
