# Data Handling and De-identification Policy

Standalone reference for how source articles are handled, cited, and
anonymised in this project. Written so this can be followed mechanically
when the document-selection-and-compression work is actually built,
without having to re-derive the reasoning each time. This is guidance
based on UK copyright law (Copyright, Designs and Patents Act 1988) as
generally understood — not formal legal advice. If in doubt, check with
your supervisor or the university's research ethics office.

## 1. Copyright basis for using the articles at all

The relevant exception is **Section 29A CDPA — Text and Data Mining for
non-commercial research**, added in 2014 specifically for computational
analysis of copyrighted text (which is what TF-IDF/vector scoring is). It
permits copying a work for that purpose provided:

- You have **lawful access** to the work (publicly readable, or a
  subscription you hold — never a paywall you've circumvented).
- The purpose is **non-commercial research** (this dissertation qualifies).
- You give **sufficient acknowledgement** of the source, unless impossible.
- Copies aren't transferred to anyone else, and aren't used for anything
  beyond the research.

**Sections 29 and 30 CDPA** (fair dealing for research/private study, and
for quotation/criticism) separately cover quoting a short excerpt of an
article directly in the dissertation text, with a citation.

## 2. Raw article text — never published

Raw article text is saved locally under `data/raw/`, which is
`.gitignore`d. It is not committed to the repository, not included in any
export/zip of the project, and not reproduced in full anywhere in the
dissertation. Only:
- the derived numeric vectors/scores, and
- short quoted excerpts (a sentence or two) with citation, where useful
  for illustration in the write-up,

are ever published. This satisfies the "no redistribution beyond the
research" condition of s.29A regardless of anything else in this document.

**Action if the repo is ever pushed somewhere public** (GitHub, a
university repository): manually re-check `data/raw/` is genuinely absent
from that export before pushing — `.gitignore` only prevents accidental
commits going forward, it doesn't retroactively protect anything already
committed or copied outside git's tracking.

## 3. De-identification scheme (defamation and "objective truth" risk)

Separate from copyright: the research proposal's own ethics section flags
two risks that this scheme is designed to address:
- the risk of defamation from publishing a credibility judgement attached
  to a named, real news organisation, and
- the risk that a reader interprets the project as claiming to measure
  objective truth about a real publication's trustworthiness.

**The rule**: the dissertation body — results tables, plots, and all
discussion/interpretation of scores — never states a real outlet's name
next to an evaluative claim about it. Instead:

- Each article is referred to only as **"Article 1"** through
  **"Article 12"** (or "Outlet A"–"Outlet L") everywhere a score, ranking,
  or interpretive judgement appears.
- The real outlet name, publication date, and URL for each Article N
  appears **only** in a plain, neutral references/sources list (e.g. in
  the methodology or an appendix) — a normal citation, with no scores or
  commentary attached to it in that location.
- `data/manifest.csv` holds the real mapping (outlet, URL, date, word
  count) and **is committed** — it's metadata only, no copyrighted article
  text, so there's no copyright reason to keep it private. It lives
  outside `data/raw/` deliberately, so the git-ignore rule on raw article
  text doesn't accidentally catch it too.

**Honest limitation**: this is de-identification of the *evaluative
claims*, not technical anonymisation of the underlying information — a
reader could still cross-reference the results table against the sources
list and reconstruct which score belongs to which real outlet. What it
reliably prevents is the dissertation itself ever making a direct,
co-located statement like "[Real Outlet] scored low for credibility" —
which is the part that actually matters for defamation exposure and for
avoiding an "objective truth" framing. This is a risk-reduction measure,
not a guarantee; flag it to your supervisor as a deliberate methodological
choice rather than something to discover later.

## 4. NER-based bias-term removal

Named entities (people, organisations, places, etc.) are stripped from
each article's tokens before TF-IDF and vector averaging, so that names
like the outlets' own ("BBC," "Guardian") or the case's subject
("Sinner") don't pull the document vector toward an irrelevant, biased
part of embedding space — the goal is to isolate each article's
distinctive *lexical footprint* (hyperbole, word choice, framing), not
proper nouns.

spaCy's default statistical NER component has no simple confidence
threshold to "force" broader tagging. Two levers are used instead:

1. **Deterministic denylist via `EntityRuler`**, placed before the
   statistical `ner` component in the pipeline. Known high-risk terms are
   listed explicitly and guaranteed removed from every document,
   regardless of whether the statistical model would have tagged them in
   that particular sentence context:
   - The case's subject and variants ("Sinner," "Jannik Sinner")
   - Key organisations ("WADA," "ITIA," "CAS")
   - The substance name ("clostebol")
   - Each of the 12 outlets' own names (self-reference or cross-outlet
     quotation)
2. **Broad entity-label removal**: every entity type spaCy detects is
   treated as removable (not just PERSON/ORG/GPE, but NORP, FAC, EVENT,
   LAW, WORK_OF_ART, etc.) — erring toward removing more rather than less,
   consistent with the stated tolerance: losing an ordinary word
   mistakenly tagged as an entity is an acceptable cost; missing a real,
   bias-carrying entity is not.

The denylist guarantees the known risk terms are gone everywhere; the
broad statistical pass catches anything else (an official's name, a
quoted third party) that wasn't anticipated in advance.
