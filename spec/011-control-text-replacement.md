# Spec 011 — Control Text Replacement (USS Maine → GDR State Doping Propaganda)

Status: **Abandoned, 2026-08-06 — USS Maine control text kept, not
replaced.** Task 1 (sourcing a genuine, citable, archivally-legitimate
GDR-era press article) was attempted directly this session — full
account below — and did not clear the same evidentiary bar the existing
source was held to within a reasonable research effort. No ready-made,
already-translated primary-source transcription equivalent to the USS
Maine text (Historical Thinking Matters' educational-archive
reproduction) could be found. A legitimate archival source exists
(Staatsbibliothek zu Berlin's ZEFYS digitized newspaper archive,
including *Neues Deutschland* and *Neue Zeit* for 1976), but only in
German, meaning any English version would rest on an in-session
translation rather than a citable scholarly one — a real reduction in
evidentiary weight compared to the text being replaced. Presented to
Jordan as three options (pull and self-translate from ZEFYS; keep
searching for an English-original GDR statement to Western press/IOC; or
abandon the swap and keep USS Maine, noting the topical mismatch as a
stated limitation rather than a defect). **Jordan's decision: keep the
existing USS Maine control text** — recorded verbatim below per
governance's accountability requirement. This spec is kept, not deleted,
as the record of the reasoning and the ethical assessment already carried
out (still valid, should this be revisited later with a better sourcing
route).

Original scoping (2026-08-06, superseded by the above): Raised directly
by Jordan: the control text should be a known propaganda **sports**
story, for topical consistency with Corpus A/B (both sports journalism),
rather than the existing 1898 war-reporting example. Two candidates were
discussed; Jordan explicitly rejected one on ethical grounds and approved
the other, reasoning recorded verbatim below per governance's
accountability requirement.

## Goal (one sentence)
Replace `data/control/uss_maine_1898.txt` with a genuine, citable,
historically-documented example of state-driven sports propaganda (GDR
doping-program press coverage), re-deriving every existing control-text
check across both axes so the dissertation's control-text evidence is
topically consistent with the rest of the corpus, without lowering the
evidentiary bar the original source was held to.

## WHY
- Raised directly by Jordan: "can we make the control text a known
  propaganda sports story as thats more consistent with what we are
  doing" — the existing control text (1898 naval-disaster war reporting)
  works as a validity check but sits outside the project's own topic
  domain (sports journalism), which is a fair consistency concern for the
  dissertation's write-up.
- **Two candidates were put to Jordan, not decided unilaterally**:
  1. East German (GDR) state press coverage denying/covering up the
     state-run doping program (1970s-80s), confirmed via declassified
     Stasi records and Germany's own 2002 Doping-Opfer-Hilfegesetz
     (state law formally recognising and compensating the athletes as
     victims of the program).
  2. 1936 Berlin Olympics German press coverage of athletic achievement.
- **Jordan's own decision, stated directly**: "dont use 2 thats during a
  world war thats ethically dangeours run with 1 if its not too
  ethically clouded in my use of it" — option 2 rejected on ethical
  grounds (proximity to Nazi-era propaganda, the same category the
  original 1898 source's own `SOURCE.md` already ruled out once for the
  primary corpus, for the same reason: well-documented but also
  hate-propaganda-adjacent, not what this check actually needs). Option 1
  approved, conditional on an ethical check.
- **Ethical check carried out this session, presented to Jordan before
  approval**: option 1 is not ethically clouded, for three reasons —
  (a) settled, non-hateful history (the German state itself legally
  recognises the athletes as victims, not perpetrators); (b) the
  dishonesty being tested lives in the state apparatus and its press
  organs, not in any named individual, so scoring the article isn't a
  character judgement on a real person; (c) the existing pipeline's own
  NER-stripping (denylist pass + broad statistical pass, already applied
  to every control-text run) already removes any athlete names the
  source article contains, before compression — no new safeguard needed,
  the existing one already covers it. **Steer for the actual source
  text, once found**: prefer institutional/federation-voiced claims
  (state press denying doping, asserting "natural" or state-system
  athletic superiority) over a piece built heavily around one named
  athlete's personal story — cleaner, and more analogous to the original
  USS Maine source's own framing (an institutional claim asserted as
  fact, not a personal narrative).

## WHAT

### 1. Source and vet the replacement text (not yet done — current blocker)
Needs the same evidentiary bar as `data/control/uss_maine_1898.txt`'s own
`SOURCE.md`: genuinely public-domain or a legitimate educational/archival
reproduction (not scraped from an uncertain source), with a citable
provenance, matching the project's existing Section 29A CDPA / fair-dealing
basis already established for the main corpus
(`compliance/data-handling-and-deidentification.md` §1). Requires actual
research (not fabrication) — a real GDR-era state press article or
official federation statement denying/covering up doping, sourced via a
historical archive or academic/educational reproduction, English-language
or translated with the translation's own provenance noted.

### 2. Write `data/control/SOURCE.md` for the new text
Same structure as the existing one: what it is, why it's historically
credible as a propaganda example, why it was chosen over alternatives
(including recording the rejection of the 1936-Olympics candidate and
why), length/word-count note, legal basis for use.

### 3. Re-derive every existing control-text check against both axes
All of the following currently run against `uss_maine_1898.txt` and need
re-running against the new text, keeping the same weighting-scheme scope
each already has — no new weighting formulas, no scope creep beyond the
source-text swap itself:
- `src/control_text_check.py` (credibility axis: flat + axis-similarity,
  both large and small axis) → `outputs/CONTROL_TEXT_COMPARISON.md`
- `src/control_text_threshold_check.py` (credibility axis: threshold-
  cosine, random-baseline pair — **not** the tuned pair, matching this
  session's standing rule that tuned-pair results don't appear in any
  reported output) — currently has no saved table/figure at all (flagged
  earlier this session as a reproducibility gap); this replacement is a
  natural point to fix that alongside the text swap, not a scope
  addition.
- `src/control_text_balance_axis_check.py` (balance axis: flat + axis-
  similarity + threshold-cosine) → `outputs/CONTROL_TEXT_COMPARISON_BAL.md`
- `src/corpus_a_whole_balance_axis_check.py` — folds the control text in
  as a 12th document for the 4-variant whole-document balance-axis
  comparison; needs re-running with the new text's whole-document score.
- The new credibility-axis "control text among the cluster" figure built
  this session (`scripts/render_control_text_credibility_cluster.py` →
  `outputs/figures/CONTROL_TEXT_CREDIBILITY_CLUSTER.png`) and its
  companion table (`scripts/render_control_text_table.py` →
  `outputs/figures/CONTROL_TEXT_COMPARISON_TABLE.png`).

### 4. Update citing specs and the dissertation text
Specs 005, 007, 008, and 010 all reference the control-text check's
results by number (e.g. spec 010's task 5 write-up cites "-0.0298",
"-0.1042" etc. for the balance-axis version). These become stale once the
underlying text and scores change — flag each spec's relevant section
rather than silently leaving old numbers standing. Any dissertation prose
already drafted referencing the old USS Maine numbers (Theme 1's write-up
this session cites the flat/axis-similarity figures) needs the same
update once the new numbers exist.

## CONSTRAINTS
- **No change to any weighting formula or preprocessing pipeline** — this
  is a source-text swap only. Every function listed in WHAT §3 is reused
  unchanged; only the input text file changes.
- **The tuned threshold-cosine pair stays excluded from every output**,
  per the standing rule established earlier this session — the new
  threshold-cosine control-text check uses the random-baseline pair only.
- **Same de-identification discipline as the main corpus**: no real
  athlete or official's name appears in any output table, figure, or
  prose next to an evaluative score — NER-stripping handles this
  mechanically, but the final compressed output should still be spot-
  checked once, the same spot-check discipline already applied to the
  main corpus's NER filtering (spec 001 RISK 2).
- **Every existing number stays traceable to its own text** until fully
  replaced — outputs from the old (USS Maine) and new (GDR) control texts
  should not be silently conflated; if any dissertation section still
  needs the old USS Maine result for a specific reason, that should be an
  explicit decision, not an accidental leftover.

## RISKS
1. **Source availability**: a genuinely citable, English-language (or
   provenance-clear translated), archivally-sourced GDR press article may
   be harder to find than the USS Maine example, which had a ready-made
   educational-archive transcription. If nothing meets the bar, that's a
   legitimate reason to revisit the text choice, not a reason to lower
   the bar.
2. **Numbers will change, possibly the story with them**: the new text's
   scores may not land in the same place relative to the corpus range
   that the USS Maine text did (0.2379/0.3203/0.3126, all inside or just
   below the real corpus range) — that's a real, reportable outcome
   either way, not something to be steered toward a particular result.
3. **Scope**: touches 4 specs and 6 code/output artifacts — worth
   confirming this is still wanted as a full re-derivation (not a partial
   swap) before task 1 begins, given the number of downstream files.

## SUCCESS / ACCEPTANCE CRITERIA
- New control text sourced, vetted, and documented in
  `data/control/SOURCE.md` to the same evidentiary standard as the text
  it replaces.
- All four control-text check modules (WHAT §3) re-run against the new
  text, both axes, random-baseline threshold-cosine only.
- The credibility-axis "cluster" figure and table rebuilt with the new
  text.
- Specs 005/007/008/010 and any dissertation prose citing old USS Maine
  numbers updated or flagged.
- No real individual's name appears co-located with an evaluative claim
  in any new output.

## TASK BREAKDOWN (ordered, dependencies noted)
1. Source and vet the replacement text (WHAT §1) — **not started, current
   blocker for everything else**.
2. Write `data/control/SOURCE.md` for the new text (WHAT §2). Depends on 1.
3. Re-run `control_text_check.py` (credibility axis, flat + axis-
   similarity). Depends on 2.
4. Re-run `control_text_threshold_check.py` (credibility axis, threshold-
   cosine random-baseline) and save a proper table/figure this time
   (fixing the pre-existing reproducibility gap). Depends on 2.
5. Re-run `control_text_balance_axis_check.py` (balance axis, all three
   schemes). Depends on 2.
6. Re-run `corpus_a_whole_balance_axis_check.py`'s 12th-document control
   inclusion. Depends on 2.
7. Rebuild `CONTROL_TEXT_CREDIBILITY_CLUSTER.png` and
   `CONTROL_TEXT_COMPARISON_TABLE.png`. Depends on 3.
8. Update specs 005/007/008/010 and flag any dissertation prose citing
   old numbers. Depends on 3-6.
9. Journal entry recording final numbers and any surprises. Ongoing.

**Not started beyond task 1's research** — stopping here per the
Planner role's own rule, pending Jordan confirming the scope (RISK 3)
and task 1 actually producing a usable source text.

## Roles used (per Appendix A.2 declaration format)

| Role | Justification for this task | Skills file |
|---|---|---|
| Planner | Decomposes the text-swap into a scoped task list, surfaces the multi-spec footprint and the tuned-pair exclusion rule explicitly rather than assuming either. | `skills/planner/SKILL.md` |
| Compliance | New source text needs its own copyright/provenance check before use, matching the standard already applied to the main corpus and the original control text. | `skills/compliance/SKILL.md` |
| Developer | Re-runs existing, unchanged weighting functions against the new input text across four modules. | `skills/developer/SKILL.md` |
| Data | Reports the new numbers factually once available, same no-conclusions-drawn convention as every other check in this project. | `skills/data/SKILL.md` |
| Reflection | Journal entry recording the ethical reasoning and decision (this session, 2026-08-06). | `skills/reflection/SKILL.md` |

Adversarial/Red-Team not used — no new attack surface. Architect not
used — no structural/architecture change, only an input swap.
