# Spec 001 — Document Selection and Compression

Status (updated 2026-07-19): Implementation substantially complete —
tasks 1-10, 9a, and 13-15 done (see Task Breakdown). Task 11 (code
review pass) is the current outstanding item; task 12 (journalling) is
ongoing throughout.
Maps to: Research Proposal Objective 2; Lit Review §2.3 "Document Gathering"
(currently empty) and the "efficient document compression" gap identified
from Hanselowski et al.

## Goal (one sentence)
Gather 11 news articles (final for this phase; a 12th may be added later
once the pipeline is built and tested — see Outlet list), all published
on 2025-02-15 (the day the Sinner doping case settlement/3-month-ban was
announced), split each into
structural zones (headline+lead / body / end) grounded in journalism's
inverted-pyramid structure and real reader consumption patterns, and
build a pipeline that compresses each zone — and the whole article — into
a document vector via TF-IDF-weighted averaging of GloVe word vectors,
with named entities stripped out first, so every piece can be projected
onto the existing credibility axis by cosine similarity.

## WHAT
1. A manifest of 11 confirmed articles (NYT/The Athletic dropped —
   inaccessible, and its color-piece style risked biasing the corpus even
   if it had been reachable; see Outlet list for the 12th-slot decision),
   all published the same day (the case's
   settlement/resolution announcement), spanning a deliberately mixed set
   of outlets (broadsheet / tabloid / wire / sport-specialist /
   international) so the corpus isn't accidentally biased toward one
   register.
2. **Zone segmentation (new)**: each article is split into three
   structural zones plus the whole document:
   - **Headline+Lead** — the article's title concatenated with its first
     paragraph. Combined deliberately: this is the unit most readers
     actually consume when skimming, and headline/lead are frequently the
     only part of an article most readers read at all — for a project
     about perceived credibility, that combined reading unit is more
     relevant than judging the headline in isolation. (Tradeoff: this
     gives up the ability to isolate whether bias concentrates in the
     headline specifically, distinct from the lead paragraph — accepted
     as the right trade given the project's actual research question.)
   - **Body** — every paragraph between the lead paragraph and the final
     two paragraphs (see End, next).
   - **End — revised: the last TWO paragraphs**, not one. Rationale
     (student): sports-news closings typically carry "what's next"
     content — next opponent, appeal date, upcoming fixture — which often
     runs longer than a single paragraph. One paragraph was too tight to
     reliably capture that.
   - **Whole** — the complete article text, unsegmented, kept as a
     baseline for comparison against the zone-level results.
   Splitting rule — **paragraph-based, confirmed**: paragraph breaks
   (not word-count or sentence-count) define the boundaries, because the
   lead paragraph is a real, well-defined concept in journalism practice,
   not an arbitrary cutoff. This produces 11 × 4 = 44 pieces to compress
   and project (48 if a 12th outlet is added), not 11 flat.
   **On zone length — important framing correction**: the goal is each
   zone's lexical footprint, not a statistically powered sample. A short
   zone dominated by hyperbolic language is a strong, correct signal, not
   a weak one because it's short — 3 hyperbolic words is real evidence.
   This applies throughout; see the corrected Risk 5 below.
3. **Preprocessing — revised twice, final 2026-07-18**: each piece is
   tokenised (spaCy), named entities removed (see 3a), grammatical
   scaffolding removed via POS tagging (see 3b), lower-cased. History
   (both revisions explicit corrections, not silent changes): the
   original design kept every stopword and punctuation mark, on the
   reasoning that the project measures lexical footprint and shouldn't
   pre-judge which words are "unimportant" — words like "very" or "just"
   could signal hyperbole, and stripping them via a generic stopword list
   would inject researcher bias into the one place the project is
   explicitly designed to avoid it ("we are not using our bias, we are
   letting language structure speak for itself" — student). That
   reasoning was sound but the mechanism relying on it (TF-IDF
   self-neutralising universal terms to near-zero) proved insufficient in
   practice — see Risk 5 and the agent journal's "TF-IDF weighting saga"
   for the full three-round debugging history. The resolution wasn't to
   abandon the "don't pre-judge words" principle, but to apply it more
   precisely: **grammatical category**, not frequency, determines whether
   a word can carry evaluative meaning. Pure structural categories
   (determiners, prepositions, coordinating conjunctions, pronouns,
   punctuation) are removed; adverbs, negation, and modal/auxiliary verbs
   — where intensifiers and hedging language actually live — are kept.
   This is not "standard stopword removal" (a fixed generic list would
   also remove the intensifiers this project needs); it's a targeted rule
   built from what was actually observed breaking. TF-IDF's IDF
   corrections (below) remain as a defensive layer for genuine content
   words that still repeat unevenly across outlets.
   3a. **NER filtering**: two combined passes, full detail in
       `compliance/data-handling-and-deidentification.md` §4.
       - A **denylist pass** using a spaCy `EntityRuler` placed before the
         statistical `ner` component: a fixed list of known high-risk
         terms (the case subject and name variants, key organisations,
         the substance name, and each of the 11 outlets' own names) is
         guaranteed removed regardless of sentence context. This exists
         because the statistical model alone can tag the same term
         inconsistently across documents, which is exactly the failure
         mode being avoided here. **Matched case-insensitively** (via
         spaCy's `LOWER` token attribute, not exact-string patterns) —
         an implementation bug initially matched only exact case, missing
         real spelling variants: BBC, the Guardian, and the Independent
         all write "Wada" and "Cas" in title case rather than all-caps
         "WADA"/"CAS" (a deliberate UK house-style convention treating
         pronounceable acronyms like proper nouns), so WADA/CAS leaked
         through uncaught in those three articles until this was fixed.
       - A **broad statistical pass**: every entity type spaCy's `ner`
         detects is treated as removable (not just PERSON/ORG/GPE — also
         NORP, FAC, EVENT, LAW, WORK_OF_ART, etc.), catching anything not
         on the denylist. Erring toward removing more, not less: losing
         an ordinary word to a false-positive tag is an acceptable cost,
         missing a real bias-carrying entity is not.
       Rationale: an outlet naming itself or another outlet, or repeating
       the subject's name, would otherwise pull the document vector
       toward that name's GloVe vector — which carries no credibility
       signal, just noise. The goal is to isolate each piece's distinctive
       lexical footprint, not its proper nouns.
   3b. **POS-tag filtering (added 2026-07-18)**: removes tokens whose
       spaCy POS tag is in `{DET, ADP, CCONJ, PRON, PUNCT}` — determiners,
       prepositions, coordinating conjunctions, pronouns, punctuation.
       Deliberately does **not** exclude `ADV` (adverbs — intensifiers/
       hedges: very, just, only, allegedly, certainly), `AUX` (modal
       verbs — would, could, might, directly relevant to a credibility
       axis), or `PART` (covers "not"/"n't" — negation must never be
       dropped, it flips meaning). One additional targeted rule: any
       single non-alphanumeric character is excluded regardless of its
       assigned POS tag, correcting for two observed statistical-tagger
       errors (a possessive apostrophe tagged `PART` rather than `PUNCT`;
       a hyphen mis-tagged `NOUN` inside "semi-finalist") — a lone
       punctuation mark is punctuation by definition, this isn't a
       content judgement, just a correction for tagger imperfection.
       Verified on real corpus data: "not," "very," "certainly," "might"
       all survive; "the," "and," "it," "during," and all punctuation
       correctly removed.
4. **TF-IDF, computed separately per zone-type — confirmed**: four
   separate 11-document corpora (all 11 headline+lead pieces together,
   all 11 bodies together, all 11 ends together, all 11 whole articles
   together — 12-document if a 12th outlet is added). Headline+lead
   vocabulary and body vocabulary are different linguistic registers —
   pooling them into one corpus would conflate "rare in a headline+lead"
   with "rare in a body paragraph." See Constraints for the corpus-size
   implication.
   - **Function-word weighting issue — fixed via POS tagging (2026-07-18)**:
     pure function words (`you`, `or`, `during`, punctuation) could score
     higher than genuinely rare content words when they were *locally*
     rare in this specific 11-document sample rather than actually
     distinctive. Full history: agent journal, 2026-07-18, "TF-IDF
     weighting saga" and "POS-tagging implemented." **Resolved in
     preprocessing** (spec 001 WHAT §3), not by further changes to the
     weighting formula below: grammatical-category filtering removes
     determiners, prepositions, coordinating conjunctions, pronouns, and
     punctuation before tokens ever reach TF-IDF, while explicitly
     keeping adverbs, negation, and modal/auxiliary verbs (where
     intensifiers and hedging language live). Deliberately not "standard
     stopword removal" — a fixed generic list would also remove the
     intensifiers this project needs to keep. The IDF corrections below
     (continuity correction, high-TF cap) remain in place as a defensive
     layer for genuine content words that still repeat unevenly across
     outlets (e.g. "responsible").
   - **IDF formula — confirmed, custom/unpadded**: `idf(t) = ln(N/df(t))`,
     no `+1` smoothing term. Deliberately **not** scikit-learn's built-in
     `TfidfVectorizer`, which always adds `+1` to the formula in both its
     smoothed and non-smoothed modes and so can never produce a literal
     zero (minimum ~1.0) — verified this numerically: with N=11,
     sklearn's ratio between rarest and most common word is ~2.8–3.4:1,
     versus infinite:1 (zero) for the custom formula. This distinction is
     load-bearing, not cosmetic: since preprocessing deliberately keeps
     stopwords (step 3), the self-neutralisation of universal terms has
     to actually reach (near-)zero for that decision to work as intended
     — a partial down-weighting under sklearn's padded formula would let
     stopword tokens meaningfully dilute the weighted average, undermining
     the reason stopwords were kept in the first place. TF is raw count
     within the piece.
     - **Continuity correction at df=N — added 2026-07-18**: a term
       present in literally every one of the N pieces gets
       `idf=ln(N/N)=0` under the plain formula, which makes
       `weight=TF×0=0` regardless of TF — erasing any distinction between
       a universal term used once vs. repeated several times in a given
       piece (student's example: "responsible," part of the widely-quoted
       WADA statement, appears once in 10 of 11 Bodies but twice in Sky
       Sports' — the old formula couldn't represent that difference).
       Fixed by treating the document count as `N−0.5` **only** at the
       exact `df=N` boundary (e.g. for N=11, `df=11` becomes `10.5`,
       giving `idf≈0.047`) — this sits below the real `df=N−1` value
       (`≈0.095` for N=11) so the ordering (more universal = lower
       weight) is preserved, while letting TF matter again for universal
       terms instead of zeroing them out. A standard continuity-correction
       technique (nudging a boundary count by 0.5 to avoid a `log`
       degeneracy), not an arbitrary patch, and self-scales if N changes
       (a 12th outlet would move the boundary to `11.5`). Verified against
       real data: `df=11 → 0.0465 < df=10 → 0.0953 < df=9 → 0.2007`,
       correct ordering; "responsible" now scores 0.0930 in Sky Sports
       (TF=2) vs. 0.0465 everywhere else (TF=1), exactly double as
       intended.
     **Implementation note**: since preprocessing keeps punctuation and
     stopwords, the TF (term-count) step must not silently reintroduce
     filtering through library defaults — if using scikit-learn's
     `CountVectorizer` for raw counts, `tokenizer`/`preprocessor` must be
     set to identity and `token_pattern=None` so it accepts the
     pre-tokenised lists from step 3 directly, or counts can be done with
     `collections.Counter` directly, bypassing sklearn's tokenizer
     entirely.
5. A document-compression function: for each of the 44 pieces, for every
   surviving token with a GloVe vector, **normalize that word's GloVe
   vector to unit length**, multiply by its TF-IDF weight, sum, divide by
   the sum of weights. Normalizing each word vector before weighting
   matches how the axis itself was constructed in the notebook (each
   axis word's vector was divided by its own norm before averaging) —
   confirmed for consistency even though the student's own check found
   minimal practical difference (~0.99–0.9995 alignment) for the
   axis-construction words specifically; not assumed to generalise to a
   full article's more heterogeneous vocabulary without checking.
   Tokens with no GloVe vector (most punctuation, some rare forms)
   contribute nothing — not a filtering choice, just nothing to
   normalize. **Edge case to handle explicitly, not let crash**: if every
   surviving token in a piece has zero TF-IDF weight (all universal
   across the zone-type corpus), the weighted average's denominator is
   zero — unlikely with real articles from different outlets, but must
   be handled rather than raise an unhandled exception.
6. A projection step: cosine similarity of each of the 44 vectors against
   the credibility axis. **Axis definition — resolved 2026-07-18**: the
   4-word-vs-4-word axis documented in the Lit Review §2.2
   (`Mean(honest, true, accurate, impartial) − Mean(dishonest, untrue,
   inaccurate, biased)`) was a proof-of-concept step — validating that
   the "grouped pairs" mean-difference method (Kozlowski et al.) works,
   on a small, hand-checked, BBC-guideline-grounded word set the student
   could sanity-check by eye (this is the stage where anomalous words
   like "grossly"/"blatantly" were manually reviewed and removed). Once
   validated, it was **expanded** into the notebook's actual final `axis`
   variable (cell 20) — 21 credible words, 22 non-credible words, a
   genuine superset of the original 8 built on the same selection
   principle, scaled up per Kozlowski et al.'s own finding that more
   words gives more axis stability. **The 21-vs-22 word axis is the real
   vector to use for projection** — confirmed by the student. The Lit
   Review §2.2 write-up hasn't yet been extended to document this
   expansion step; that's a documentation gap in the dissertation text,
   not a methodological inconsistency in the actual work.
7. A ranked output (table + scatterplot, consistent with the existing
   word-level axis plots) showing all 44 pieces ordered by score, grouped
   by zone-type, **labelled "Article 1"–"Article 11" with a zone column,
   never by real outlet name** (see De-identification section below).
   Also supports the more interesting comparison this design enables:
   whether a given zone-type (e.g. headline+lead) systematically scores
   further from centre than others across the 11 articles — i.e. whether
   bias/hyperbole concentrates in a particular structural part of the
   reporting.

## IDENTIFIER SCHEME (new)
Every piece gets a compact, consistent ID for indexing, output tables,
and plots: **A{article}Z{zone}**, e.g. `A1Z1`, `A1Z2`, `A3Z4`.
- Article number (`A1`–`A11` currently; `A12` reserved if a 12th outlet
  is added later) — assigned at outlet-selection time (task 1), fixed for
  the rest of the project.
- Zone number, fixed mapping:
  - `Z1` = Headline+Lead
  - `Z2` = Body
  - `Z3` = End
  - `Z4` = Whole
So `A1Z1` is Article 1's headline+lead, `A1Z4` is Article 1's whole
document, `A7Z2` is Article 7's body, etc. — 11 × 4 = 44 unique IDs
currently (48 if a 12th outlet is added). This is the identifier used
consistently in the manifest, intermediate data,
output tables, and plot labels, so a given piece can always be
cross-referenced across every stage of the pipeline without ambiguity.
This is separate from the de-identification labelling (`Article N`) below
— `A{n}Z{z}` is the technical/data identifier, "Article N" (with a
zone name spelled out) is what appears in dissertation prose. Both refer
to the same underlying piece.

## WHY
- Holding the topic constant isolates source-level linguistic/presentational
  variance from topic vocabulary variance — this is the whole point of
  picking one event across many outlets ("to keep results neutral").
- The lit review already identifies the risk in the naive approach:
  Hanselowski et al found flat word-vector averaging "fell behind" LSI/BoW
  for a similar task, which is the direct justification for weighting the
  average by TF-IDF instead of taking a flat mean (Aizawa's p-tfidf
  reasoning).
- **Zone segmentation** is a direct, deeper response to the same
  document-length problem Aizawa raises: comparing a 400-word tabloid
  piece against a 1,200-word broadsheet piece as if they were the same
  kind of object buries the signal. Splitting by structural zone
  (headline+lead, body, closing — journalism's inverted-pyramid
  structure) means comparisons happen within a matched structural role
  across outlets, not across wildly different whole-document lengths. It
  doesn't eliminate length heterogeneity — a lead is still short and a
  body is still long — but it stops conflating "different structural
  role" with "different amount of padding."
- **Headline+lead are combined, not split further**, because that's the
  unit real readers actually consume when skimming — for a project about
  perceived credibility, that's the analytically relevant reading unit,
  not an artificial minimum-viable-chunk-size decision.
- This is Objective 2 of the proposal and the direct prerequisite for
  Objective 3 (SVM scoring), which needs document vectors as input features.

## DE-IDENTIFICATION & OUTPUT HANDLING
Full policy and reasoning: `compliance/data-handling-and-deidentification.md`.
Summary for this phase:
- Real outlet names, URLs, and dates live in `data/manifest.csv`, which
  **is committed** (metadata only — no copyrighted article text, so no
  copyright reason to keep it private). The protection this scheme relies
  on isn't hiding that mapping; it's never stating an evaluative claim
  next to a real name. The manifest is a plain reference; the results
  table/plots (which carry the actual claims) use `A{n}Z{z}` only. A
  reader could still cross-reference the manifest against the results
  table — same honest limitation already noted below — but committing the
  manifest doesn't make that meaningfully easier, since the dissertation's
  own references list will disclose the same real names anyway.
- Every output this phase produces — the ranked table, the scatterplot,
  any in-notebook discussion of scores — refers to pieces only by their
  `A{n}Z{z}` ID (see Identifier Scheme above) or, in prose, "Article N"
  with the zone spelled out (e.g. "Article 3's headline+lead"). Never a
  real outlet name next to a score or interpretive claim.
- A separate, neutral references list (real name, URL, date — no
  commentary) is written up later in the dissertation, not part of this
  phase's code output.
- This addresses two risks flagged in the original research proposal:
  defamation exposure from a public, named credibility judgement, and the
  risk of the project being read as claiming objective truth about a real
  publication's trustworthiness.

## CONSTRAINTS
- **Copyright**: full article text should not be committed to the git repo.
  Raw article text goes in `data/raw/`, which is git-ignored; only the
  manifest (outlet, URL, date, word count, license/access notes) and the
  derived numeric vectors are committed. Short quotations for illustration
  in the write-up are fine under research/private-study fair dealing; bulk
  redistribution of full text is not. Full legal basis (UK CDPA s.29/29A):
  `compliance/data-handling-and-deidentification.md` §1.
- **Comparability**: articles should be full-length reporting, not
  paywalled stubs or live-blog fragments — otherwise document length
  variance swamps the signal TF-IDF is meant to control for.
- **Minimum article length — confirmed, 3 real paragraphs** (not counting
  the headline): 1 for headline+lead, 2 for end, with body allowed to be
  empty. Reconciles the student's "2 paragraph minimum, headline counted
  as one" with End now requiring two distinct paragraphs — with only 1-2
  real paragraphs, End would have to reuse text already claimed by
  headline+lead, which defeats the point of having separate zones. In
  practice this floor won't bind: hand-picked full-length reporting will
  routinely have well more than 3 paragraphs.
- **Publication date is fixed at 2025-02-15** for every article in the
  corpus (the settlement announcement), not just "about the case"
  generally — no exceptions now that NYT/The Athletic has been dropped.
  If an outlet's coverage of that day is a stub or wire reprint, swap in
  a different outlet rather than a different date.
- **Corpus size: 11 articles (44 pieces after segmentation), final for
  this phase** — build and test the pipeline against this count. A 12th
  outlet is possible future work, not a current requirement; if added
  later the pipeline should generalise to 12/48 without a rewrite, but
  should not be built to arbitrarily scale beyond that.
- **IDF scope — confirmed**: TF-IDF is computed separately per zone-type,
  four 11-document corpora currently (see WHAT §4), not one pooled
  corpus and not an external background corpus. The statistical thinness
  of IDF over only 11 (or 12) documents per zone-type (see Risks) is
  accepted as a documented limitation rather than solved.
- **Zone splitting — confirmed**: paragraph-based (headline + first
  paragraph = headline+lead, last TWO paragraphs = end, everything
  between = body), not word-count or sentence-count based. See WHAT §2.
- **NER filtering — confirmed**: spaCy is used to detect and remove named
  entities (organizations, people, places) from each piece's tokens
  before TF-IDF and vector averaging.
- Must reuse the existing GloVe model (`glove-wiki-gigaword-300`) and the
  existing axis definition already validated in the notebook — this phase
  does not re-derive the axis.

## RISKS
1. **Small-corpus IDF instability**: IDF computed over only 11 documents is
   statistically thin — terms unique to one outlet get large, noisy weights.
   Accepted as a documented limitation in the write-up (student confirmed
   in-corpus IDF over the background-corpus alternative).
2. **NER removal can over-strip**: spaCy's statistical NER is not perfect
   — it can mis-tag ordinary words as entities, or miss real ones
   inconsistently across documents. The denylist (§2a) removes this risk
   for the specific known terms that matter most (subject name, key
   organisations, outlet names); residual risk is limited to unanticipated
   entities the statistical pass might inconsistently catch or miss (e.g.
   a quoted third party named in only one article). Worth spot-checking a
   sample of filtered tokens by eye before trusting the output, not just
   assuming the filter behaved as intended.
3. **Outlet selection bias**: "neutral" only holds if the 11 outlets
   actually span the credibility/style spectrum rather than clustering in
   one register — worth sanity-checking the final list against that before
   locking it in.
4. **n=11 is a pilot, not a statistically powered sample** — fine for
   validating the pipeline and producing an illustrative ranking, not
   sufficient on its own for Objective 3's later evaluative use of the SVM.
   Segmentation raises n to 44 pieces, which helps Objective 3 somewhat,
   but the 11 pieces of any one zone-type are still just 11.
5. **Short-zone TF-IDF weighting (revised)** — corrected framing: this is
   NOT a "weak signal because it's short" concern. The goal is each
   zone's lexical footprint, and a short zone dominated by hyperbolic
   language is a strong, correct signal — a fully hyperbolic 3-word
   headline+lead is real evidence, not a statistically thin sample to be
   treated with less confidence. Since stopwords and punctuation are now
   kept (revised 2026-07-18, no longer stripped), this concern is less
   severe than originally framed — most zones retain far more tokens than
   they would have under stopword removal. The remaining genuine technical
   caveat is narrower still: for a headline that's almost entirely the
   subject's name (e.g. "Sinner banned"), NER stripping alone can leave
   very few content words, and TF-IDF has little room to differentiate
   weights among 2-3 terms — it converges toward a near-flat average in
   practice. That doesn't make the resulting footprint less meaningful; it
   means TF-IDF isn't doing much extra work
   over a flat mean for that specific piece. Worth noting in the write-up
   as a mechanism detail, not as a reliability downgrade.
6. **Zone-length imbalance within an article**: "headline+lead" (headline
   plus one paragraph) and "end" (two paragraphs) are typically short;
   "body" can be zero paragraphs or ten, depending on the article. This is
   expected and not a bug — the zones represent different structural
   roles, not equal-sized chunks — but body-zone vectors are usually
   averaged over more tokens than headline+lead/end zones, worth
   remembering when comparing scores across zone-types rather than
   within one.

## SUCCESS / ACCEPTANCE CRITERIA
- 11 articles (12th slot open), all published 2025-02-15, selected and
  logged in `data/manifest.csv` with outlet, URL, date, and word count.
- Each article is split into headline+lead / body / end zones (plus the
  whole document), producing 44 pieces total, each with a unique `A{n}Z{z}`
  ID traceable back to its article and zone (see Identifier Scheme).
- Preprocessing produces clean token lists for all 44 pieces with no
  unhandled HTML/markup artifacts and named entities removed.
- Each of the 44 pieces reduces to exactly one 300-dimensional vector.
- Pipeline validated against a synthetic sanity check (a clearly
  "credible-style" paragraph and a clearly "biased-style" paragraph) to
  confirm the projection sign matches expectation before trusting it on
  real articles.
- Output: a ranked table and a scatterplot of all 44 pieces' credibility
  scores, grouped by zone-type, labelled "Article 1"–"Article 11" (never
  real outlet names), in the same visual style as the existing word-level
  axis plot.
- Limitations (IDF instability, n=11 per zone-type, short-zone TF-IDF
  flattening, residual NER imprecision beyond the denylist) are written
  up, not omitted.

## TASK BREAKDOWN (ordered, dependencies marked)
1. Finalise the outlet list for 2025-02-15 coverage + manifest, with an
   "Article N" label assigned to each real outlet at selection time (no
   dependency). **Complete (2026-07-18): 11 articles, final for this
   phase** — see Outlet list section.
2. Save raw article text locally under `data/raw/` per manifest entry,
   git-ignored (depends on 1). **Complete for the 11 confirmed articles
   (2026-07-18)**: A1–A11 all saved (A1/A2/A5/A7/A8 pasted by student and
   cleaned by agent; the rest via Browser tool verbatim extraction),
   cleaned of nav/ad/caption boilerplate. A12 (NYT/The Athletic) dropped
   — inaccessible in this environment, and student judged its color-piece
   style would likely have biased the corpus regardless. 12th-slot
   decision pending — see Outlet list.
3. Build the NER denylist (subject name + variants, key organisations,
   substance name, all 11 (or 12) outlets' own names — now known from
   step 1) (depends on 1).
4. Zone segmentation function: split each article into headline+lead
   (headline + paragraph 1) / body (paragraphs 2 through n−2) / end (last
   two paragraphs) plus whole, producing 44 labelled pieces (48 if a 12th
   outlet is added); enforce the minimum-3-real-paragraph constraint and
   flag any article that fails it (depends on 2).
5. Preprocessing/cleaning function — HTML strip, normalise, tokenise —
   applied to all pieces (depends on 4).
6. NER filtering — load spaCy, wire in the denylist via `EntityRuler`
   before the statistical `ner` component, strip all entity-tagged tokens,
   applied to all pieces (depends on 3 and 5).
7. Fit TF-IDF separately per zone-type (4 corpora of 11, or 12 if the
   slot is filled), post-NER-filtering (depends on 6).
8. Document-compression function: TF-IDF-weighted GloVe mean per piece,
   using its own zone-type's TF-IDF (depends on 7; reuses the GloVe load
   already in `MSC PROJECT.ipynb`, now migrated to `notebooks/`).
9. Axis projection + ranking output for all pieces, labelled by
   `A{n}Z{z}` ID only (depends on 8; reuses the axis vector already
   derived in the notebook).
9a. **Complete (2026-07-19)**: word-level axis visualisation extended to
    overlay real document scores, per the student's own `graph()`/
    `add_document()` sketch in `notebooks/MSC PROJECT.ipynb` (cells 108-109
    — `add_document()` was written there but never actually called with a
    real vector). Ported into `src/axis_plot.py`: one chart per zone-type
    (`outputs/figures/axis_words_and_documents_Z{1-4}.png`), each showing
    the 43 axis words plus the 11 real articles' scores for that
    zone-type, articles in a distinct colour/marker and labelled `A{n}`
    only (never real outlet names, per de-identification). Depends on 9.
    **Governance note**: unlike every other item in this breakdown, this
    entry was written *after* `src/axis_plot.py` was already implemented
    and run, not before — the Planner-first order the governance policy
    requires (spec written and approved before code) was not followed for
    this task, and no automated tests exist for this module. See journal
    2026-07-19 ("Word+document axis visualisation") for the full account;
    not corrected retroactively so the deviation stays visible rather than
    being smoothed over.
10. **Complete (2026-07-19)**: sanity-check tests — Test role (depends on
    8 and 9). `tests/` (pytest, 32 passing): synthetic credible-vs-biased
    projection sign check (`test_axis_sanity.py`, using the real GloVe
    model — scored +0.333 / -0.351), OOV and empty-vector handling
    (`test_compression.py`), denylist spot-check both synthetic and
    against real article A1 (`test_preprocessing.py`), zone-boundary
    spot-checks on all 11 real articles plus the 3-paragraph boundary
    case (`test_segmentation.py`), and the two TF-IDF correction
    mechanisms (`test_tfidf.py`). Untested and flagged: `src/report.py`'s
    file-writing functions, and NER filtering is spot-checked on one
    article rather than all 11 — see journal 2026-07-19.
11. Code review pass — Review role (depends on 10).
12. Journal entries throughout — Reflection role (ongoing, not a gate).
13. **Complete (2026-07-18)**: POS-tag-based grammatical-category
    filtering in preprocessing — see WHAT §3b for the implemented rule
    and verification.
14. **Complete (2026-07-18)**: flat/no-TF-IDF baseline for comparison —
    `src/tfidf.py compute_flat_weights` (weight = TF only, no IDF factor
    — the "flat word-vector averaging" baseline from Hanselowski et al.,
    already cited in WHY), run through the same POS-filtered
    preprocessing and axis projection as the main pipeline via
    `src/report.py`. Produces
    `outputs/tables/axis_projection_comparison_weighting.csv` (per-piece
    score and rank under both schemes) alongside separate figures for
    each. Result: mean absolute rank shift of 4.73 positions out of 44
    between the two schemes, two pieces shifting by 18 ranks — concrete
    evidence TF-IDF weighting changes the outcome substantively, not
    just a theoretical justification.
15. **Complete (2026-07-18)**: second, independent ablation isolating
    the POS-tag filtering (task 13) itself — `clean_tokens`/
    `clean_corpus` in `src/preprocessing.py` take a `pos_filter` bool
    (default `True`; `False` reverts to the pre-2026-07-18 behaviour, NER
    removal only). Both runs use TF-IDF weighting, holding that constant.
    Produces `outputs/tables/axis_projection_comparison_pos.csv`. Result:
    mean absolute rank shift of 2.41/44 — smaller than the TF-IDF-vs-flat
    effect (4.73/44), consistent with the TF-IDF corrections (task 12)
    already containing most of the function-word inflation before
    POS-filtering was added; POS-filtering closes the remaining gap
    rather than being the primary corrective force. Both effects real and
    independent, not redundant.

## Resolved decisions (2026-07-18)
- IDF scope: per zone-type (4×12-doc corpora), confirmed — revised from
  the original single 12-doc corpus once zone segmentation was added.
- NER filtering with spaCy added to preprocessing, confirmed; revised to
  denylist (`EntityRuler`) + broad statistical pass, confirmed.
- Corpus date: 2025-02-15 (settlement announcement), confirmed.
- `MSC PROJECT.ipynb` copied into `notebooks/` in this repo (original left
  in place in Downloads too).
- Copyright/data-handling approach and de-identification scheme
  (Article N labelling everywhere an evaluative claim appears; real names
  live in the committed `data/manifest.csv` and a later neutral
  references list, never co-located with a score) confirmed; full detail
  in `compliance/data-handling-and-deidentification.md`. Compliance skill
  role added (`skills/compliance/SKILL.md`).
- Article count stays fixed (not expanded beyond outlet selection) —
  segmentation provides the additional analytical granularity instead.
  **Superseded (2026-07-18, later same day)**: this bullet originally said
  "stays at 12"; A12 (NYT/The Athletic) was dropped shortly afterward — see
  Outlet list below — bringing the final count to 11, not corrected here
  until 2026-07-19 (see journal 2026-07-19 code review).
- Zone segmentation added: headline+lead / body / end (paragraph-based) +
  whole document, per article — headline merged into the lead paragraph
  rather than kept as a fifth standalone zone, since headline+lead is the
  unit real readers actually consume together. 11 × 4 = 44 pieces (this
  bullet originally said "12 × 4 = 48"; corrected 2026-07-19 for the same
  reason as above).
- Framing correction: short zones are not "less reliable" — the project
  measures lexical footprint, not statistical power. A short,
  hyperbole-dominated zone is a strong signal regardless of length. The
  only genuine technical caveat is that TF-IDF weighting has little room
  to operate over 2-3 tokens (converges toward a flat average) — a
  mechanism detail, not a confidence downgrade.
- End zone redefined as the **last two paragraphs**, not one (student:
  sports-news closings — next opponent, appeal date — often need more
  than one paragraph). Minimum article length set at 3 real paragraphs
  (not counting the headline) to keep headline+lead and end from
  overlapping — reconciled with the student's "2 paragraph minimum,
  headline counted as one" (see Constraints for the reasoning).

## Outlet list (2026-07-18) — finalised at 11, 12th slot open for future work
Real outlet ↔ Article N mapping (this table itself is reference only —
the actual data goes in `data/manifest.csv`, which is committed; see the
De-identification section above for why that's fine — metadata only, no
copyrighted text, and the protection comes from never pairing a real name
with an evaluative claim, not from hiding the mapping):

| Article N | Outlet | Date | Note |
|---|---|---|---|
| A1 | BBC | 2025-02-15 | Confirmed: `cj48rn79kego` (straight announcement) |
| A2 | Sky News | 2025-02-15 | Confirmed |
| A3 | Sky Sports | 2025-02-15 | Confirmed (2nd Sky property, deliberate per student) |
| A4 | ATP Tour | 2025-02-15 | Confirmed — official body statement, not independent journalism (flagged earlier, student proceeded anyway) |
| A5 | talkSPORT | 2025-02-15 | Confirmed |
| A6 | ESPN | 2025-02-15 | Confirmed |
| A7 | The Guardian | 2025-02-15 | Confirmed — student verified freely accessible |
| A8 | The Independent | 2025-02-15 | Confirmed — student verified freely accessible |
| A9 | CBS Sports | 2025-02-15 | Confirmed |
| A10 | Sports Illustrated | 2025-02-15 | Confirmed |
| A11 | Yahoo Sports | 2025-02-15 | Confirmed |
| A12 | — | — | **DROPPED, FINAL (2026-07-18)**: NYT/The Athletic was inaccessible in this environment; CNN (the next candidate found) also returned "Content Unavailable For Legal Reasons" when tested. Student judged a color/feature piece risked biasing the corpus regardless of access. Student confirmed: proceed with 11, revisit a 12th only after the pipeline is built and tested — not a blocker for implementation. |

Task 1 (finalise outlet list + manifest) is **complete — 11 articles,
final for this phase**. `data/manifest.csv` reflects this (NYT/Athletic
row removed).

## Remaining open items
None blocking implementation. A 12th outlet remains a possible future
addition once the pipeline is built and tested (student's own framing:
"perfect the pipeline and test and then see what can be done
afterwards") — not tracked as an open spec item, just a possible later
iteration.

**Tooling constraint, for reference**: automated content reading is
blocked in this environment for bbc.co.uk, news.sky.com, talksport.com,
theguardian.com, independent.co.uk, nytimes.com, and cnn.com — raw text
for outlets on those domains needs the student to paste manually (used
for A1, A2, A5, A7, A8). The other domains tried (skysports.com,
atptour.com, espn.com, cbssports.com, si.com, sports.yahoo.com) were
fetchable via the Browser tool's verbatim text extraction — **not** via
WebFetch, which summarises through a small model rather than returning
exact text, and would corrupt the corpus for a project that depends on
exact word choice.
