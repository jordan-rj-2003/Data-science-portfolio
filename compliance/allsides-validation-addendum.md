# Compliance Addendum — AllSides Outlet-Level Comparison (Spec 009)

Extends `compliance/data-handling-and-deidentification.md` for the one
section of this project that deliberately breaks its own
de-identification rule. Same disclaimer as the parent document: general
understanding of UK law/ethics practice, not formal legal advice — check
with your supervisor or the university's research ethics office if in
doubt. Written as the Compliance role (`skills/compliance/SKILL.md`) —
advisory only; you and your supervisor hold final responsibility.

## 1. What's different here, and why it needs its own note

Every other result in this project follows the de-identification rule in
the parent document: real outlet names never appear next to a score or
evaluative claim in the dissertation body. This section is the single,
deliberate exception. AllSides publishes ratings *of named organisations*
— "the outlet whose axis score is 0.38 rates Center on AllSides" is not
a sentence that can be written without naming the outlet. There is no
de-identified version of this comparison that still means anything.

## 2. Scope of the exception (agreed with Jordan, 2026-07-23)

- Confined to **one clearly separated section** of the dissertation
  (e.g. its own subsection or appendix table), not folded into the main
  results narrative.
- That section states **up front, in the same place the table appears**,
  that this is a deliberate, scoped exception to the de-identification
  practice used everywhere else, and why (external validation against a
  named-organisation rating service requires it).
- Every other result in the dissertation — the 44-piece axis-projection
  scores, all ablation comparisons, the ESPN corpus — keeps the
  "Article N" / de-identified convention unchanged. This addendum does
  not loosen that anywhere else.
- Framed by Jordan explicitly as an exploratory relative-position check,
  not a validated causal or evaluative claim ("i just want to see how
  each outlet's relative position relates... i dont imagine we'll get
  too much validation off it though") — lowers, rather than raises, the
  defamation-risk profile relative to what spec 008 originally
  discussed, since a plainly-labelled exploratory comparison with a
  stated small-N caveat reads very differently from an asserted finding.

## 3. Why this doesn't reintroduce the original risk

The parent document's two risks were: (a) defamation from a credibility
judgement stated about a named real organisation, and (b) a reader
mistaking the project for a claim about objective truth/trustworthiness.
Neither is triggered the same way here:
- AllSides' rating is **their own published, independent judgement**,
  not this project's — quoting a public rating a third party already
  published about a named organisation is materially different from
  this project asserting its own credibility judgement about that
  organisation by name. The project is reporting "outlet X's *published,
  independent* rating is Y" plus "our own axis score for outlet X is Z"
  side by side — the evaluative claim ("X is biased") is AllSides',
  correctly attributed, not this project's original assertion.
- The stated N=11 caveat and "exploratory, not validation" framing
  (spec 009 Goal) directly heads off risk (b) — the section is framed as
  "does our number move roughly the same direction as theirs," not "we
  have proven X is credible/biased."
- Still worth naming as a residual, not eliminated, risk: once an
  outlet's *axis score* is placed next to its *real name* in this one
  section, a reader could lift that pairing out of context and treat it
  as this project's own claim about that outlet, stripped of the caveat.
  Same honest-limitation framing as the parent document: this is
  risk-reduction (scoping to one flagged section, attributing AllSides'
  judgement to AllSides), not a guarantee, and should be flagged to your
  supervisor as a deliberate methodological choice.

## 4. Data handling

- AllSides ratings, rating URLs, and access dates are public information
  about AllSides' own published output — no different in kind from
  `data/manifest.csv`'s existing outlet/URL/date fields, and can be
  committed the same way (metadata, not copyrighted article text).
- This does not touch raw article text at all — no new copyright
  question beyond what's already covered in the parent document for the
  original 11 articles.
- If AllSides has no rating for a given outlet (a real possibility for
  the sports-specific/UK-regional outlets in this corpus — see spec 009
  CONSTRAINTS), that outlet is simply dropped from this comparison and
  the omission stated plainly, not worked around.

## 5. Scope limit on this exception

This addendum authorises real-name use **only** within the one AllSides
comparison section specced in `spec/009-outlet-level-allsides-
validation.md`. It is not a precedent for relaxing de-identification
elsewhere in the project without its own explicit decision, following
the same process (surfaced as a scope question, decided with Jordan,
documented before data collection starts).
