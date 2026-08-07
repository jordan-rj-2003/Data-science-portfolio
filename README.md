# Semantic Axis Projection

**An explainable approach to ranking news articles using word embeddings.**

MSc AI dissertation project (IS4T702, University of South Wales, supervisor Dr. Mabrouka Abuhmida).

## What this is

News articles can be one-sided in *which* facts they select, how they frame them, and what they
omit — even when every individual fact is true. This project tests whether that kind of
selection/framing bias leaves a measurable footprint in an article's word choice, without ever
touching whether the underlying facts are true.

The method:

1. Build a **semantic axis** in GloVe embedding space from two theory-grounded word sets —
   e.g. `mean(honest, true, accurate, impartial, …) − mean(dishonest, untrue, inaccurate, biased, …)`
   — derived from BBC editorial guidelines, not invented ad hoc.
2. Compress each article (or a structural zone of it — headline+lead / body / end) into a single
   document vector via **TF-IDF-weighted averaging of GloVe word vectors**, after stripping named
   entities so the score can't just be tracking *who* is mentioned.
3. **Project** each document vector onto the axis via cosine similarity to get an interpretable
   score — no black-box classifier sits between the text and the number.

## Why GloVe over BERT

Contextual embeddings were considered and explicitly declined: there's no clean equivalent of "one
fixed vector per axis word" for a contextual model, and static GloVe vectors keep the whole pipeline
inspectable end to end — a deliberate explainability trade-off, not an oversight. See
`Project-Findings-Chronological.txt` for the full reasoning.

## Repo layout

```
src/            Pipeline modules: segmentation, NER filtering, TF-IDF, GloVe compression,
                axis construction/projection, weighting-scheme variants, validity checks
tests/          pytest suite covering every pipeline stage
spec/           Spec-first design documents (one per feature/experiment), written before
                implementation per the course's AI-use governance policy
journal/        Dated agent journal — the working record behind every spec decision
skills/         Role definitions (planner / developer / test / review / reflection) the
                AI assistant was constrained to per the governance policy
key-findings/   Consolidated, chronological findings log
outputs/        Result tables and figures (safe to publish — articles are referenced only
                by de-identified IDs like A1Z2, never by outlet name)
compliance/     Copyright and de-identification handling notes
data/           `manifest.csv` (article ID → outlet mapping, metadata only) and
                `control/` (a public-domain 1898 text used as a validity check).
                Raw article text itself is git-ignored — see Data below.
notebooks/      Original exploratory notebook this pipeline was migrated from
```

## Data

Raw article text is **not included in this repository** (`data/raw/`, `data/espn_worldcup/` are
git-ignored). It's used locally under the UK CDPA s.29A text-and-data-mining exception for
non-commercial research, but isn't cleared for redistribution. Results throughout this repo
reference articles only by de-identified ID (`A{n}Z{zone}`) — real outlet names live solely in
`data/manifest.csv` and are never shown alongside a score or interpretive claim. See
`compliance/data-handling-and-deidentification.md` for the full policy.

`data/control/uss_maine_1898.txt` is a public-domain 1898 historical text used as an independent
validity check and is included in full.

## Running it

```bash
pip install -r requirements.txt
python -m src.report        # runs the full pipeline end to end
pytest                      # run the test suite
```

The first run downloads the `glove-wiki-gigaword-300` embeddings via `gensim.downloader`
(~1GB, cached locally after that).

## Methodology notes

- **No stopword removal, no punctuation filtering** — only named-entity removal is applied as a
  deliberate content judgement (entities are confounds for a credibility axis specifically, not
  "unimportant" words generally). TF-IDF is trusted to self-neutralise genuinely uninformative
  terms.
- Every weighting scheme tested (TF-IDF, flat/no-IDF, axis-similarity, several hybrids,
  threshold-cosine gating) is kept in `src/` as a documented ablation, not deleted once superseded
  — the trade-offs between them are part of the project's own findings.
- Two corpora: **Corpus A** (11 hand-picked articles, same day/event, 4 zones each) and
  **Corpus B** (53-article ESPN World Cup corpus, whole-document only) test the same hypothesis at
  different scale.

## AI-assisted development

Built with Claude Code under a course-mandated governance policy: specification before
implementation, defined agent roles for planning/development/testing/review/reflection, and a
full dated journal of every design decision — all feeding a required dissertation appendix
declaring AI tool use. Every methodological choice was made and is defensible by the author; see
`spec/` and `journal/agent-journal.md` for the full record.
