# Spec 007 — ESPN World Cup Corpus: Credibility Footprint at Scale

Status: **Complete (2026-07-22)** — all 9 tasks done under the 7
declared roles. See Key Results below.

## Roles used (per Appendix A.2 declaration format)

| Role | Justification for this task | Skills file |
|---|---|---|
| Planner | Decomposed the corpus-expansion goal into this spec before any collection or code; surfaced the single-outlet trade-off explicitly rather than leaving it implicit. | `skills/planner/SKILL.md` |
| Developer | Extends `src/denylist.py`/`src/preprocessing.py` to support a second, World Cup-specific entity denylist without altering the original 11-article pipeline's behaviour. | `skills/developer/SKILL.md` |
| Test | New pipeline path (custom-denylist NLP) needs its own tests — an untested change here risks silently corrupting the original corpus's cached pipeline. | `skills/test/SKILL.md` |
| Review | Independent check that the custom-denylist mechanism genuinely doesn't affect the original singleton's behaviour (the specific risk this task introduces). | `skills/review/SKILL.md` |
| Compliance | Project now touches a new set of licensed assets (ESPN articles) and a new copyright/ethics-scope question — see `compliance/espn-worldcup-corpus-addendum.md`. | `skills/compliance/SKILL.md` |
| Data | Once articles are collected, interprets the resulting scores/separation stats/survivor quality — same role this project has used throughout specs 001-006. | `skills/data/SKILL.md` |
| Reflection | Journal entry for this task, per standing practice. | `skills/reflection/SKILL.md` |

No required role omitted. Architect and Adversarial/Red-Team not used —
this task doesn't involve new system-level interfaces or security-relevant
surface area; Risk Assessor not used as a standing role, but its function
(flagging what needs escalation) is being served by the Compliance
addendum's explicit "needs a decision/check" items.

Maps to: this project's core hypothesis, unchanged since spec 001 — that
language use itself carries a lexical/credibility footprint, independent
of factual content. Everything built so far (specs 001-006) tested that
footprint on 11 articles, one event, multiple outlets. This spec tests
the same footprint — the same threshold-cosine method, the same axis —
on a bigger, different corpus, to see whether the footprint still shows
up: does the evaluative/hedging vocabulary threshold-cosine surfaced in
spec 006 (`shameful`, `allegedly`, `deliberately`, etc.) keep showing up
and keep producing real separation once the corpus is no longer 11
same-day articles about one story?

## Goal (one sentence)
Build a non-controversial, ESPN-sourced World Cup article corpus and
test whether the threshold-cosine method still isolates a real
credibility footprint — real evaluative/hedging vocabulary, real
inter-article separation — on this new corpus.

**One factual constraint on what this specific run can show**: because
this corpus is single-outlet (ESPN only, unlike the original 11-outlet
corpus), any separation found here is ESPN's own article-to-article
spread, not an outlet-vs-outlet credibility ranking. That's a limit on
what this particular result answers, not a change to what's being tested
— the footprint hypothesis itself is exactly as it's always been.

## WHAT

1. **Corpus**: N=24 ESPN articles (proposed — adjustable), 2022 FIFA
   World Cup (Qatar), whole-article text only (no zone segmentation —
   see CONSTRAINTS for why).
2. **Topic filter ("no controversial topics"), concrete criteria**:
   - **Include**: match previews, match reports/results, group-stage
     standings, statistical/tactical analysis, player on-pitch
     performance summaries, tournament schedule/format explainers.
   - **Exclude**: host-nation human-rights/political coverage, boycotts,
     disciplinary incidents (red cards treated as controversy rather
     than routine match events, referee/VAR controversies), player
     conduct scandals, injury tragedies, crowd violence, anything
     naming a real individual in an accusatory frame.
   - Each candidate article's inclusion/exclusion is logged (title + one-
     line reason) for the compliance record, matching the existing
     project's de-identification/data-handling practice.
3. **Collection method**: Browser tool `get_page_text`, matching how A3
   (Sky Sports), A4 (ATP Tour), A6 (ESPN), A9 (CBS Sports), A10 (SI),
   A11 (Yahoo Sports) were collected for the original corpus — ESPN was
   confirmed accessible this way in that session, WebFetch/`get_page_text`
   blocked domains (bbc.co.uk, theguardian.com, etc.) don't include
   espn.com. Saved to `data/espn_worldcup/A{n}.txt`, git-ignored (same
   copyright treatment as `data/raw/` — UK CDPA s.29A text-and-data-
   mining exception for non-commercial research), one file per article.
4. **Pipeline**: reuse `src/segmentation.py`'s article-loading (headline
   + paragraphs), `src/preprocessing.py` (`clean_corpus_stopword_baseline`,
   spaCy-stopword — matches the other cosine-based variants), plain
   TF-IDF computed **within this new corpus only** (its own N-document
   IDF stats — not pooled with the original 11-article corpus, which
   stays untouched), `compute_weights_threshold_cosine` (both threshold
   pairs from spec 006: tuned 0.25/0.02 and statistically-principled
   0.194/0.096), `compress_corpus`, and `project` onto the existing large
   axis (`build_axis` — the same 21-vs-22-word axis, unchanged).
5. **Output**: scores table, top-token table, a word+document axis
   chart (same style as existing `*_words_and_documents_Z*.png` charts,
   but one chart only since there's no zone segmentation), and an
   observation-only summary report — same Data-role convention as every
   prior ablation.
6. **Manifest**: `data/espn_worldcup/manifest.csv` — article ID, ESPN
   URL, one-line topic description, inclusion/exclusion notes for any
   candidates considered and rejected. De-identified in any
   score/analysis output (`A{n}` labels only), matching the existing
   scheme — even though single-outlet, this stays consistent with
   established practice rather than a one-off exception.

## WHY
Tests whether the credibility footprint spec 006 found — real
evaluative/hedging vocabulary, real separation — is a property of the
method itself, or an artefact of the specific 11-article, one-event
corpus it was found on. If the same kind of vocabulary and separation
shows up on a fresh, larger ESPN corpus, that's real evidence the
footprint generalizes. If it doesn't, that's important to know before
any larger, more expensive corpus is built.

## CONSTRAINTS
- **Whole-article only, no zone segmentation** — explicit decision,
  not a workaround. Rationale: (a) this run is about whether the
  footprint shows up at all across many stories, not about zone-specific
  patterns (the Headline+Lead-vs-body pattern from spec 006 was itself
  flagged as low-confidence due to short-zone fragility); (b) `Whole` was
  the
  single most robust zone-type under threshold-cosine in spec 006 (0/11
  pieces with ≤1 survivor, vs. 3/11 each for Headline+Lead/End) — using
  whole-article text for every piece avoids reintroducing that fragility
  at a larger scale before it's been resolved.
- Single outlet (ESPN) — results describe **ESPN's own article-to-article
  spread**, not a credibility ranking between outlets. Must be stated
  explicitly in the summary report and not conflated with specs 001-004's
  framing.
- New corpus's TF-IDF/IDF statistics are computed independently — the
  original 11-article corpus and its saved outputs are not modified or
  re-run.
- Same de-identification and copyright-handling conventions as the
  original corpus (raw text git-ignored, manifest committed, TDM
  exception).

## RISKS
1. **Topic-filter subjectivity**: "controversial" is a judgement call.
   Mitigated by logging inclusion/exclusion reasoning per candidate
   article (WHAT §2) rather than an undocumented selection — gives the
   Review/Compliance roles something concrete to check.
2. **ESPN accessibility not re-verified this session** — confirmed
   accessible in the original 2026-07-18 session; if blocked now, falls
   back to the same student-pastes-text approach used for BBC/Guardian/
   etc. in that session.
3. **Single-tournament corpus (2022 only)**: all N articles share one
   time period and one host — reduces but doesn't eliminate topic
   homogeneity relative to a fully independent set of stories (still one
   tournament, though many distinct matches/stories within it). Worth
   naming as a limitation, not a full test of the footprint across
   completely unrelated topics — a corpus spanning multiple tournaments
   or sports would be a stronger future step.
4. **N=24 is a proposal, not a fixed constraint** — genuinely limited by
   how many articles can be manually screened for the topic filter in a
   reasonable session; can be revised up or down before collection starts.

## SUCCESS / ACCEPTANCE CRITERIA
- N articles collected, manifest logged with inclusion/exclusion
  reasoning, raw text git-ignored.
- Both threshold pairs run, scores table + top-token table + one axis
  chart + observation-only summary produced.
- Summary explicitly states that this corpus is single-outlet (ESPN's
  own article-to-article spread, not a credibility ranking between
  outlets) and reports inter-article separation (stdev, range) and
  surviving-vocabulary quality (strong vs. near-boundary survivors, same
  check as spec 006) compared against the original 11-article corpus's
  own threshold-cosine figures as context.
- No modification to the original 11-article corpus or its saved outputs.

## TASK BREAKDOWN (ordered, dependencies marked)
1. Confirm N, tournament, and topic-filter criteria with student
   (this spec, awaiting approval). **Complete** — N=64 (one article per
   match), 2022 World Cup, topic filter as defined in WHAT §2.
2. **NER denylist extension** (Developer, before any collection).
   **Complete**: `src/denylist.py` gets `WORLD_CUP_DENYLIST_TERMS`
   (FIFA, ESPN self-reference, the 32 competing nations, tournament
   name) — additive, `DENYLIST_TERMS` itself untouched.
   `src/preprocessing.py` `get_nlp()`/`clean_tokens()`/`clean_corpus()`/
   `clean_tokens_stopword_baseline()`/`clean_corpus_stopword_baseline()`
   all gained an optional `denylist_terms` parameter (default `None` —
   original behaviour, original cached singleton, untouched). A custom
   terms list builds and caches a *separate* pipeline instance keyed by
   the terms themselves. Player/manager names are NOT pre-enumerated (not
   knowable before seeing the actual 64 articles) — relies on the
   existing broad statistical PERSON-entity removal for those, same as
   the original pipeline does for anyone beyond its own small explicit
   denylist.
   - **Test (complete)**: 3 new tests (`tests/test_preprocessing.py`) —
     custom denylist removes its own terms, custom and default denylists
     don't cross-contaminate, default singleton unaffected by a prior
     custom-denylist call. One test's first draft was wrong, not the
     code: it asserted "FIFA"/"Argentina" survive the *default* pipeline,
     but both get removed anyway by spaCy's own broad statistical NER
     (they're recognizable ORG/GPE entities independent of any
     denylist) — fixed by using an invented placeholder term
     ("zonkwiddle") that isolates the denylist mechanism specifically
     from the separate, already-existing statistical-NER mechanism. Full
     suite: 60/60 passing.
   - **Review (complete)**: grepped every existing call site of
     `clean_tokens`/`clean_corpus`/`clean_tokens_stopword_baseline`/
     `clean_corpus_stopword_baseline`/`get_nlp` across `src/` — all 7
     existing callers (`report.py`, `naive_baseline.py`,
     `axis_similarity_ablation.py`, `small_axis_ablation.py`,
     `threshold_cosine_ablation.py`, `control_text_check.py`,
     `formality_check.py`) call with no `denylist_terms` argument, all
     hit the unchanged default path. Confirmed additive-only change.
3. **Complete**: Collected via Browser tool `get_page_text` against
   ESPN's `/soccer/report/_/gameId/{id}` pages for all 64 matches of the
   2022 World Cup (group stage through final). **N=53 included, 16
   excluded** (15 for political/disciplinary controversy content, 1 for
   a gameId serving mismatched/duplicate content). Every candidate
   logged in `data/espn_worldcup/manifest.csv` with a one-line reason.
   Piece IDs are `E1`-`E53` (not `A{n}` — single flat corpus, no
   articles/zones distinction needed since there's no zone
   segmentation).

   Exclusion categories that actually came up, beyond what was
   anticipated in WHAT §2: anthem/political protests (Iran, both
   England-Iran and Wales-Iran; US-Iran flag dispute), OneLove
   armband/Qatar LGBTQ-rights coverage (Germany-Japan, England-USA,
   brief mentions counted too for consistency), colonial-era political
   tension (Tunisia-France anthem whistling), ethnic/political symbolism
   (Kosovo-Albanian gesture context, Serbia-Switzerland), and — not
   anticipated in the original spec — **player-conduct/disciplinary
   controversy** (Netherlands-Argentina's record 17 yellow cards and
   Messi's on-field conduct; the World Cup final itself, for its
   substantial 2010-bid-scandal/migrant-worker/host-nation-law
   discussion). The final two confirm the filter categories in WHAT §2
   ("disciplinary incidents", "host-nation human-rights/political
   coverage") needed to be applied even to the tournament's marquee
   matches, not just fringe stories.
4. **Complete**: Saved to `data/espn_worldcup/E{n}.txt`, added
   `data/espn_worldcup/` to `.gitignore` (matching `data/raw/`'s
   treatment), manifest committed (metadata only, matches existing
   practice).
5. **Complete**: `src/espn_worldcup_ablation.py` — whole-article text,
   `clean_tokens_stopword_baseline` with `WORLD_CUP_DENYLIST_TERMS`,
   both threshold-cosine pairs from spec 006. One real implementation
   bug caught before running: `compute_weights_threshold_cosine` calls
   `compute_weights_plain`, which groups pieces by zone-type via
   `group_by_zone()` (`piece_id.split("Z")[1]`) — this corpus's `E1`-style
   IDs have no zone suffix at all and would have crashed. Fixed with
   `compute_weights_threshold_cosine_flat()`, a local reimplementation
   using `compute_idf_plain()` directly (which has no zone-grouping
   assumption) rather than forcing non-zone-shaped IDs through
   zone-shaped code.
6. **Complete**: scores/top-token tables (both threshold pairs), one
   word+document axis chart, `outputs/espn-worldcup-comparison.md`.
7. **Complete**: 0/53 pieces empty on either pole for both threshold
   pairs; all scores confirmed in valid cosine-similarity range [-1, 1].
8. **Complete**: grepped every existing call site of the modified
   preprocessing functions (see task 2) — confirmed additive-only.
   Confirmed via file-modification timestamps that `data/raw/A1.txt`
   (2026-07-18) and `outputs/tables/axis_projection_scores_tfidf.csv`
   (2026-07-20) predate this session — the original corpus and its core
   outputs are untouched.
9. **Complete**: journal entry (see 2026-07-22 journal, this task).

## Key results (post NER-leak patch — see below)

- **Both threshold pairs ran cleanly**: 0/53 pieces empty on either pole.
- **Separation is larger than the original corpus's own threshold-cosine
  figures, for both threshold pairs**:

  | Corpus/variant | Overall stdev | Range |
  |---|---|---|
  | Original 11-article corpus, tuned pair | 0.0865 | 0.2871 |
  | Original 11-article corpus, random-baseline pair | 0.0396 | 0.1202 |
  | ESPN World Cup corpus (n=53), tuned | **0.1319** | **0.5108** |
  | ESPN World Cup corpus (n=53), random-baseline | **0.0637** | **0.3482** |

- **Tuned pair produces genuinely negative scores for a real fraction of
  the corpus**: 13/53 (25%) score negative, vs. a handful in the
  original 11-article corpus. Random-baseline pair produces zero
  negative scores (0/53) — a stark difference in behaviour between the
  two threshold pairs on this corpus, not seen this clearly on the
  original 11-article corpus.
- **Top-token quality, after the NER-leak patch below**: `profited`,
  `ploughed`, `routs`, `dumped`, `condemned`, `desperate` (most-negative
  articles) and `important`, `difference`, `good`, `upsets` (most-positive)
  — no entity names remain among the extreme-scoring articles' top
  tokens. Still reads as more generic than the original corpus's
  strongest survivors (`shameful`, `disgusting`, `allegedly`). Not yet
  checked whether this reflects genre difference (single-outlet
  wire-service-style match reports vs. the original corpus's more
  varied outlet styles) or something else.
- Unique top tokens: 603 (tuned), 526 (random-baseline) across 53
  pieces — both notably higher relative-to-corpus-size than the
  original corpus's 28-29 unique tokens across 44 pieces, though the
  much larger vocabulary pool (53 full articles vs. 44 zone-fragments)
  makes this comparison inexact.

No conclusions beyond these factual comparisons are drawn here — the
question of whether this constitutes "the same footprint at scale" or a
different phenomenon is left to the student, per this project's
established Data-role convention.

## Extension (2026-07-22, same day): NER-leak audit and patch

**Student's observation**: after seeing `opta` and `rochet` flagged as
NER misses in the top-token quality check, the student asked for a full
audit rather than a two-term patch.

**Audit method**: rather than testing lowercased candidate words in a
synthetic sentence (a first attempt that failed — spaCy's NER relies
heavily on capitalisation, so testing lowercased words out of context
mostly surfaced false positives like `day`/`half`/`today`, not real
entity leaks), cross-referenced the full surviving vocabulary (both
threshold pairs, 849 unique tokens) against words that actually appear
capitalised mid-sentence in the real source text. Found 42 candidates;
verified each by reading its actual sentence context. **35 confirmed
genuine leaks** (player first/last names, one club, one stadium, one
team nickname, one stats brand); 5 false positives from the
sentence-splitting heuristic (`finally`, `moments`, `buoyed` — genuine
sentence-initial words the regex mis-flagged; `referee` — part of a
capitalised acronym expansion, not a name; `ole` — the Spanish cheer
"Olé!", correctly not a leak).

**Patch**: `WORLD_CUP_PLAYER_AND_ENTITY_LEAKS` added to
`src/denylist.py` (35 terms), folded into `WORLD_CUP_DENYLIST_TERMS`.
One deliberate exclusion: `real` (from "Real Madrid") is **not**
denylisted standalone — it's an ordinary English adjective ("a real
chance") that would be wrongly stripped everywhere if denylisted alone;
"Real Madrid" (the two-word phrase) is denylisted instead, matching how
the original denylist already handles multi-word terms. Two new tests
confirm both halves of this (leaked terms removed; the word "real" on
its own survives). One implementation bug caught by the tests
themselves: `Opta` was accidentally left out of the first draft of the
patch list despite being one of the two originally-flagged leaks —
caught immediately by the new test failing, fixed before moving on.

**Verified after the patch**: re-ran the full audit script against the
patched pipeline — 818 unique survivors (down from 849), zero of the 35
patched terms remain (`real` alone correctly still present, confirmed
as the ordinary adjective use, not a residual "Real Madrid" fragment).
Pipeline re-run; results updated above. Full suite: 62/62 passing.

**Not claimed**: this is a reactive patch of confirmed leaks, not a
guarantee of zero remaining entity contamination — player names in a
53-article, 32-team corpus are open-ended, and only names that both
survived weighting and cleared a threshold were checked. A full
squad-list denylist (all ~700+ 2022 World Cup players) was considered
and explicitly deferred as a larger task not needed for this pass.
