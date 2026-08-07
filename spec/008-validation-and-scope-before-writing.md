# Spec 008 — Validation options and scope, before the write-up begins

Status: **Planning note (2026-07-22)** — not yet actioned. Written to be
picked up in a future session, ahead of starting the dissertation
write-up. Not a task with an approved implementation yet — read this,
decide priority/scope with the student, then convert into a proper
Planner-role spec (WHAT/WHY/CONSTRAINTS/TASK BREAKDOWN) before building
anything.

## Context: what prompted this

By the end of the 2026-07-22 session (specs 005-007), the project had:
- A defensible primary method (threshold-cosine, statistically-grounded
  "random-baseline" threshold pair — see spec 006) that produces real,
  replicated separation on two different corpora, with genuinely
  evaluative top vocabulary.
- Two known, named, unresolved problems with that method, distinct from
  each other, not to be conflated:
  1. **Topic-vs-credibility confound**: TF-IDF's rarity can currently
     only mean "rare among outlets covering one same-day event" (or, in
     the ESPN corpus, one tournament) — not genuine cross-topic
     stylistic distinctiveness. Needs a **larger, multi-event corpus**
     to fix at the root; no shortcut available within current data.
  2. **Survivor-count/article-length confound**: r=0.52 (survivors) /
     r=0.47 (word count) with score on the ESPN corpus, replicated at
     similar magnitude (0.39-0.47) across every weighting variant on the
     *original* 11-article corpus too — this is a within-document
     averaging mechanism (more tokens to average -> more dilution toward
     the corpus's ambient positive lean), not a cross-document
     rarity-resolution problem. **A bigger corpus does not directly fix
     this** — it's a different mechanism. There's one plausible
     (untested) indirect path: more documents could let TF-IDF properly
     suppress generic filler words via better IDF resolution, which
     might reduce reliance on raw survivor count — a testable prediction
     for a future, larger-corpus session, not a settled fix.
- No validation against an independent, non-circular ground truth has
  been attempted. Full external validation (human-subject credibility
  ratings) is ethics-blocked (see [[msc-governance-policy]] /
  `compliance/data-handling-and-deidentification.md`); an SVM trained on
  the axis's own cosine-similarity output was previously identified and
  correctly rejected as circular (2026-07-19 session).

## Three concrete options that need neither a bigger corpus nor new ethics approval

Priority order, cheapest/most-relevant first:

### 1. Compare against existing outlet-level bias ratings — TRIED AND REJECTED (2026-07-23)
Built and run in full as `spec/009-outlet-level-allsides-validation.md`.
Only 5/11 outlets had any AllSides rating (4/11 with a numeric value);
the resulting correlation was directionally consistent but statistically
meaningless at that sample size. Jordan reviewed the result and rejected
the whole avenue as not helpful ("i dont see this as a reasonable
inclusion... the validation step it doesnt help whatsoever"), not just
one detail of it. **Do not re-attempt this option** (including with a
different rating service like MBFC) without new reasoning from Jordan —
see spec 009's Outcome section and journal 2026-07-23 for the full
record. Original description of the option, kept for context:
Services like AllSides or Media Bias/Fact Check publicly rate real news
outlets on impartiality/bias. This is public, pre-existing, and
independent of anything derived from this project's own axis — not
article-level, but a genuine, non-circular reference point for the
original 11-outlet corpus's *aggregate* (per-outlet mean) score. Check
whether the axis's outlet-level ranking correlates at all with an
independent rating. Cheapest option, most directly relevant to the
actual research question (outlet-level credibility ranking), and doesn't
require building anything new. **Recommended starting point for a future
session.**

### 2. Formalise the student's own qualitative read
Not human-subjects research (that's specifically about collecting data
*from other people* — this is the student's own judgement, already used
informally throughout this project, e.g. the top-token "does this read
as credibility-relevant" checks in specs 006/007). Make it deliberate
and systematic: rank a sample of articles by the student's own judgement
of impartiality, independent of having seen the axis scores first, then
compare. Small-sample, qualitative, but legitimate convergent evidence
that costs nothing beyond time.

### 3. Domain-matched null baseline (sports vocabulary, not generic English)
Proposed twice this session (once for the `offside` discussion, once for
the general register-mismatch caveat on the statistically-grounded
threshold) and not yet built. Currently, the threshold-cosine
"random-baseline" pair's null population is 1000 random *generic
English* words — not sports-news-specific. Rebuild the same check using
a random sample of *sports/football vocabulary* (e.g. drawn from the
corpus itself, or a separate sports corpus) as the null population, and
see whether the threshold shifts. Would directly settle whether
topic-confound words like `offside`, `foul`, `penalty` are a systematic,
correctable-for pattern (in which case the threshold should be
recalibrated against this better-matched baseline) or an occasional,
tolerable edge case (in which case the generic-English baseline is fine
to keep using). Doesn't validate credibility directly, but bears
directly on how much to trust the separation already reported.

## What NOT to do based on this session's findings

- Don't denylist individual words that "feel" topic-confounded (e.g.
  `offside`) by hand — this was explicitly considered and rejected this
  session as reintroducing the unprincipled content-based word removal
  this project's whole design has rejected from the start. Option 3
  above is the principled version of the same instinct.
- Don't loosen the negative threshold to admit specific desired words
  (e.g. the `-0.04` idea, also considered and rejected this session) —
  checked and confirmed to readmit ~16% noise-level words, undoing the
  statistical grounding that was the whole point of the random-baseline
  pair.
- Don't treat the tuned threshold-cosine pair (0.25/0.02) as a second
  reportable weighting scheme — it's a useful *diagnostic* (it
  demonstrated the survivor-count confound attenuates when the poles are
  deliberately rebalanced, real evidence for the mechanism) but its own
  negative threshold is statistically indefensible (~23-30% chance any
  admitted word is noise) and shouldn't be presented as a method whose
  scores are trustworthy on their own.

## Recommended framing for the write-up in the meantime

Per this session's discussion: describe the axis as measuring *relative
impartiality-of-framing among sources presumed to be operating in good
faith*, not a general credibility/fake-news classifier (already
established via the control-text check, spec 005) — and name the
survivor-count/length confound plainly as an open limitation with named,
quantified evidence (r=0.52/0.47, replicated across variants and
corpora) rather than softened or explained away. This is a stronger,
more examiner-proof position than either overclaiming success or
concluding the whole approach is pointless (both extremes were
considered and corrected during this session — see journal 2026-07-22).
