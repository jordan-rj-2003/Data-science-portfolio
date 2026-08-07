# Compliance Addendum — ESPN World Cup Corpus (Spec 007)

Extends `compliance/data-handling-and-deidentification.md` for the new,
larger, single-outlet corpus. Same disclaimer as the parent document:
general understanding of UK copyright law, not formal legal advice — if
in doubt, check with your supervisor or the university's research ethics
office. Written as the Compliance role (`skills/compliance/SKILL.md`) —
advisory only; you and your supervisor hold final responsibility.

## 1. Copyright basis — same as before, and scale doesn't change it

**Section 29A CDPA (text-and-data-mining for non-commercial research)**
is not capped at a specific number of works — it's conditioned on
*purpose* (non-commercial research) and *manner of use* (computational
analysis, no redistribution), not volume. Going from 11 articles to ~64
doesn't change the legal basis, provided the same four conditions still
hold: lawful access (freely published on espn.com, no paywall bypass),
non-commercial research purpose (unchanged — same dissertation), sufficient
acknowledgement (manifest with source URLs, committed — same practice as
before), and no redistribution of the raw text beyond the research
(raw text git-ignored — same practice as before).

**One point worth being aware of, not certain of**: s.29A includes a
provision that contract terms purporting to prevent an act permitted
under the exception are unenforceable — meaning a website's Terms of
Service generally can't override this specific statutory permission for
non-commercial research TDM. This is my understanding of the general
shape of the law, not a confirmed reading of ESPN's specific ToS or a
substitute for actually checking it. Worth a supervisor conversation if
this project is ever making any claim beyond "internal, non-commercial,
non-redistributed academic analysis" — which, per the existing practice
below, it isn't.

## 2. Raw text handling — unchanged practice, applies to the new corpus too

Same as the original corpus: raw ESPN article text saved to
`data/espn_worldcup/` (git-ignored, per spec 007 WHAT §3), never
published in full, never redistributed. Only derived scores/vectors and
short cited excerpts (a sentence or two, with citation) appear in the
dissertation. This is the condition that matters most for the s.29A
basis, and it's identical to the original corpus's treatment.

## 3. De-identification — same principle, adjusted for single-outlet scope

The original scheme protects against two risks: defamation from a
credibility judgement attached to a *named, real organisation*, and
misreading the project as measuring *objective truth*. This corpus is
single-outlet (ESPN only), so there's no outlet-vs-outlet comparison to
de-identify — but the same structural discipline should still apply, one
level down:

- Refer to each piece only by ID (e.g. `E1`-`E64`) in any results table,
  score, or evaluative discussion — never "the [specific match/story]
  article scored low," which would still functionally be "ESPN's
  coverage of X was less credible," just naming the story instead of a
  competing outlet.
- `data/espn_worldcup/manifest.csv` (article ID, URL, one-line topic,
  inclusion/exclusion note) is committed, same as `data/manifest.csv` —
  metadata only, no copyrighted text, no evaluative claims attached to it
  at that location.
- Same honest limitation as before: a reader could cross-reference the
  manifest against the results and reconstruct which score belongs to
  which real match/story. The de-identification prevents the
  dissertation *itself* from making that direct co-located statement; it
  isn't airtight anonymisation.

## 4. NER-based bias-term removal — same mechanism, new denylist entries needed

Reuse the existing `EntityRuler` + broad statistical NER removal, but the
denylist (`src/denylist.py`) is currently built for the Sinner/doping
case specifically (subject name, WADA/ITIA/CAS, the substance name, the
11 outlets' own names). For this corpus, the denylist should be reviewed
and likely extended for World Cup-specific high-frequency entities that
could pull document vectors toward irrelevant embedding-space regions the
same way "Sinner" or "WADA" would have — e.g. FIFA, host/team country
names, and any recurring player/manager names likely to appear across
many of the 64 articles. **Not yet done — flagged as a task for spec 007
implementation, not assumed to carry over unchanged.**

## 5. Personal data (GDPR) — consistent with existing practice, not a new category

Match reports will name real players, managers, and officials — public
figures acting in their public professional capacity, reporting on
publicly-held, publicly-broadcast sporting events. This is the same
category of content as the original corpus (which already named WADA
officials, the case's subject, etc., handled by NER removal for the
*embedding-space* reason above, not because it was treated as sensitive
personal data). No special-category or sensitive personal data is
involved. Doesn't require a different ethical treatment than the
original corpus.

## 6. Ethics approval scope — check, don't assume

The project's existing ethics approval was understood (per prior
discussion, 2026-07-19) to permit "expanding the corpus with more
published secondary text" as distinct from the primary human-subject
data collection the approval form blocks. That reasoning should extend
to this corpus (still published secondary text, still no human
participants). **However**: this is a materially different corpus from
what the original approval likely had in mind when written (different
subject matter — sport results/previews rather than a specific
credibility case study; single-outlet rather than multi-outlet;
significantly larger N). Recommend a brief check with your supervisor
that the existing ethics approval's wording covers this specific
expansion before large-scale collection, rather than assuming the
2026-07-19 reasoning was written with this exact use in mind — it wasn't.

## Summary — what's ready vs. what needs a decision/check before collection

| Item | Status |
|---|---|
| Copyright/TDM legal basis | Extends cleanly, no change needed |
| Raw text git-ignore practice | Extends cleanly, no change needed |
| De-identification scheme | Extends with adjustment (single-outlet framing) |
| GDPR/personal data | No new concern |
| NER denylist | **Needs extending for World Cup entities before running** |
| Ethics approval scope | **Recommend a quick supervisor check before large-scale collection** |
