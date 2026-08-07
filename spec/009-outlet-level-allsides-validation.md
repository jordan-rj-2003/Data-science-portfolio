# Spec 009 — Outlet-Level Validation Against AllSides Media Bias Ratings

Status: **Rejected (2026-07-23).** Built and run to completion (see
Outcome below), then judged by Jordan not worth keeping: "i dont see
this as a reasonable inclusion" / "the validation step it doesnt help
whatsoever." **Not used in the dissertation.** Kept in the repo as a
documented, tried-and-rejected avenue (same convention this project
already uses for the SVM-on-own-output approach and the tuned
threshold-cosine pair as a second reportable method) rather than
deleted — see journal 2026-07-23 for the full record.

## Outcome (2026-07-23)

Converted spec 008's option 1 into an actioned plan, scope decided
directly with Jordan (rating source, axis method, aggregation, and a
scoped de-identification exception — see Scope decisions below), then
downgraded from a formal validation claim to an exploratory check per
Jordan's own framing when approving it: "i just want to see how each
outlet's relative position relates to the allsides checker. i dont
imagine we'll get too much validation off it though." Built and run:
only 5 of 11 outlets had any AllSides rating at all, 4 with a numeric
value; Spearman on that 4-outlet subset was rho=-0.632, p=0.37 — direction
consistent with the hypothesis but not remotely significant. Full
result in `outputs/allsides-validation-comparison.md`.

After seeing that result, Jordan rejected the whole avenue outright
rather than a specific piece of it (asked to clarify scope of the
objection; answer was the validation step overall, not just the
correlation number or the ESPN construct-mismatch caveat). **Spec 008's
option 1 should not be re-attempted in a future session** without new
reasoning — options 2 (student's own qualitative judgement) and 3
(domain-matched null baseline) remain open in spec 008 if further
validation work is wanted later.

## Roles used (per Appendix A.2 declaration format)

| Role | Justification for this task | Skills file |
|---|---|---|
| Planner | Converts spec 008's option 1 from a planning note into an actioned spec; surfaces the de-identification conflict explicitly before any data collection. | `skills/planner/SKILL.md` |
| Compliance | This task requires real outlet names to be printed next to axis scores, for the first time in the project — a deliberate, scoped exception to the standing de-identification rule. Needs its own compliance addendum before writing begins. | `skills/compliance/SKILL.md` |
| Developer | New script to pull the 11 Whole-zone scores already computed, pair them with AllSides ratings, and compute a correlation. | `skills/developer/SKILL.md` |
| Data | Interprets whatever correlation (or lack of one) results, in light of the confounds already logged in spec 008 (N=11 is small; don't overclaim). | `skills/data/SKILL.md` |
| Review | Manual sanity check that each AllSides rating was read against the correct outlet, and that the join (outlet -> axis score -> rating) lines up row by row, before the comparison is shown. Scaled down from a unit-test fixture since this is now an exploratory look, not a reported validation figure. | `skills/review/SKILL.md` |
| Reflection | Journal entry, per standing practice. | `skills/reflection/SKILL.md` |

Architect and Adversarial/Red-Team not used — no new system-level
interface or security-relevant surface here. Risk Assessor not used as a
standing role; its function is served by the Compliance addendum below.

## Goal (one sentence)
Show, side by side, how each outlet's threshold-cosine random-baseline
axis position compares to its AllSides media-bias rating — an
exploratory relative-position check, not a claimed validation (N=11 is
too small and the constructs too mismatched to support that framing;
Jordan's own expectation going in is that this "won't get too much
validation" out of it).

## Scope decisions (made with Jordan, 2026-07-23)
1. **Rating source: AllSides only.** Its bias-lean rating (from blind,
   multi-partisan reviewer surveys) is the closest available proxy for
   "impartiality of framing" — distance from AllSides' center point
   stands in for degree of bias. This is a proxy, not a direct construct
   match (lean is about political orientation, not framing style); name
   this explicitly as a limitation in the write-up, not something the
   correlation number alone settles. MBFC is out of scope for this spec;
   could be a follow-up cross-check later if this result is promising
   enough to be worth strengthening.
2. **Axis-scoring method: threshold-cosine, random-baseline thresholds**
   (`POS_THRESHOLD_RANDOM_BASELINE=0.194`, `NEG_THRESHOLD_RANDOM_BASELINE
   =0.096`, `src/threshold_cosine_ablation.py`) — the method spec
   006/008 identify as the statistically-grounded, recommended primary
   method going forward, not the method most of the existing dissertation
   narrative currently reports scores with. **Consequence to flag**: this
   validation result technically supports threshold-cosine specifically,
   not the TF-IDF production scores the rest of the write-up leans on.
   The write-up needs to be explicit about which method this section
   validates, so it doesn't get read as validating "the axis" generically.
3. **Aggregation: Whole-document (Z4) zone score only**, one per outlet
   (11 articles, one per outlet, so this is just each outlet's existing
   Z4 score, no new averaging step). Chosen over a 4-zone mean because
   Whole most closely matches how AllSides rates an outlet holistically,
   and avoids compounding the already-flagged survivor-count/length
   confound (spec 008) across 3 extra zones per outlet. **Consequence to
   flag**: this uses only 11 of the 44 already-computed scores — deliberate,
   not an oversight.
4. **De-identification: scoped, flagged exception.** Every other result
   in this project keeps "Article 1"-"Article 11" labelling with real
   names confined to the neutral references list. This section is the
   one deliberate exception: the comparison is meaningless without real
   outlet names (AllSides rates named organisations, not anonymised
   labels), so this one section names outlets directly, with an explicit
   statement of why (external, non-circular validation requires it) and
   a pointer back to the standing de-identification rule for every other
   result in the dissertation. See `compliance/allsides-validation-
   addendum.md` (to be written under task 1 below) for the full
   reasoning, following the same structure as the existing
   `compliance/data-handling-and-deidentification.md` and the ESPN
   corpus's `compliance/espn-worldcup-corpus-addendum.md` precedent.

## WHAT
1. Look up each of the 11 outlets' current AllSides "Media Bias Rating"
   (Left / Lean Left / Center / Lean Right / Right, and AllSides' numeric
   scale where published) via their public ratings pages. Record: outlet,
   rating label, numeric value (if available), URL, access date — same
   fields as `data/manifest.csv`'s own convention.
2. Convert each rating to a single "distance from center" impartiality
   proxy (e.g. absolute value on AllSides' own left-right scale, or a
   simple ordinal mapping — Center=0, Lean=1, full Left/Right=2 — if
   AllSides doesn't publish a numeric scale for every outlet here).
3. Pull each outlet's existing Whole-zone (Z4) threshold-cosine
   random-baseline score from
   `outputs/tables/threshold_cosine_random_baseline_comparison_vs_production.csv`
   (already computed, spec 006 — no new pipeline run needed).
4. Compute Spearman rank correlation between the 11 axis scores and the
   11 AllSides distance-from-center values. **Spearman, not Pearson**:
   N=11 is small, and AllSides' rating is inherently ordinal/categorical
   for at least some outlets (not every outlet has a fine-grained numeric
   score published) — rank correlation is the honest fit for this data,
   not an arbitrary choice.
5. Write a new small table (`outputs/tables/allsides_validation.csv`:
   outlet, axis_score, allsides_rating, allsides_distance_from_center,
   ranks) and a short factual summary
   (`outputs/allsides-validation-comparison.md`, following the same
   pattern as `outputs/threshold-cosine-comparison.md`) reporting the
   correlation coefficient, its p-value, and a plain statement of what
   it does and doesn't show given N=11.
6. New compliance addendum (`compliance/allsides-validation-addendum.md`)
   documenting the scoped de-identification exception (see Scope
   decisions #4 above) before any outlet-named table is produced.

## WHY
Directly answers spec 008's stated gap: no validation against an
independent, non-circular ground truth has been attempted. AllSides is
public, pre-existing, and derived from something the project's own axis
never touched (partisan-lean survey data, not lexical footprint) — a
genuine external check, unlike the previously-rejected SVM-on-own-output
approach. Cheapest available option; doesn't require a bigger corpus,
new ethics approval, or new data collection.

## CONSTRAINTS
- N=11 — any correlation reported must be presented with that caveat
  loudly, not as a definitive validation either direction. A single
  outlier outlet can swing a Spearman correlation substantially at this
  sample size.
- AllSides rates the outlet as a general institution, not this specific
  article — the rating reflects the outlet's overall editorial stance,
  not necessarily this one Sinner-doping-case article. That's an
  unavoidable mismatch in what's being compared, not a bug to fix; name
  it as a limitation.
- Two of the 11 outlets carry known caveats from spec 001 already (A4
  ATP Tour is an official governing-body statement, not independent
  journalism; A9-A11 wire/aggregator-style coverage) — AllSides may not
  rate governing bodies at all (it rates news outlets). If AllSides has
  no rating for ATP Tour, that outlet is dropped from this specific
  comparison (N=10), not force-fit with a placeholder value.
- No new ethics approval needed (public, published third-party ratings,
  no human-subjects data collection) — confirmed against the same
  reasoning spec 008 already used to rule this option in.
- Must not alter or re-run the existing threshold-cosine pipeline —
  this task only reads an existing output table.

## RISKS
1. **Weak or null correlation is a real possible outcome, not a failure
   of execution.** If Spearman's rho comes out near zero, that is itself
   a reportable, honest finding (the axis may track something orthogonal
   to political lean, e.g. tone/hedging style rather than left-right
   framing) — must not be treated as a bug to debug away, and must not be
   quietly dropped from the write-up if it happens.
2. **Confirmation bias risk**: because this is the first external check
   this project has run, there's a temptation to read a weak positive
   correlation as more meaningful than N=11 supports. Mitigate by
   reporting the p-value alongside rho and stating the sample-size
   caveat in the same sentence as the headline number, not in a footnote.
3. **AllSides rating currency**: ratings can change over time (community
   feedback, editorial reviews) and may not reflect the outlet's stance
   specifically in Feb 2025. Record access date; treat as an accepted,
   named limitation rather than something to chase perfect precision on.
4. **De-identification exception scope creep**: this section must not
   become a precedent for loosening de-identification elsewhere in the
   dissertation. The compliance addendum should say explicitly that this
   is a one-section, justified exception, not a policy change.

## SUCCESS / ACCEPTANCE CRITERIA
- Compliance addendum written and read before any outlet-named table is
  produced.
- All 11 (or 10, if ATP Tour is unrated) outlets' AllSides ratings
  recorded with source URL and access date.
- One correlation table, one factual summary, both reproducible.
- The factual summary states the correlation, its p-value, N, and the
  sample-size/construct-mismatch caveats in the same paragraph as the
  headline result — not buried.
- A null or weak result is reported exactly as plainly as a strong one
  would be.

## TASK BREAKDOWN (ordered, dependencies noted)
1. Write `compliance/allsides-validation-addendum.md` (Compliance role).
   **Blocks everything else** — no outlet-named data collection starts
   before this exists.
2. Look up AllSides ratings for the 11 outlets (Developer/Data role,
   manual lookup — public web pages). Depends on 1.
3. Extract each outlet's Whole-zone threshold-cosine random-baseline
   score from the existing comparison CSV (Developer role, no pipeline
   re-run). Independent of 2, can run in parallel.
4. Join 2+3 into one side-by-side table, sorted by axis score, with
   AllSides rating alongside; compute Spearman rho + p-value as one
   extra descriptive data point (not the headline deliverable). Depends
   on 2 and 3.
5. Manual sanity check of the join, row by row (Review role) — right
   outlet, right rating. Depends on 4.
6. Write `outputs/tables/allsides_validation.csv` and a short factual
   note (`outputs/allsides-validation-comparison.md`) presenting the
   relative-position comparison plainly, with the N=11/construct-mismatch
   caveat stated up front rather than as a footnote (Developer/Data
   role). Depends on 5.
7. Journal entry (Reflection role). Depends on 6.

Approved by Jordan (2026-07-23) to proceed at this reduced scope —
starting at task 1 now.
