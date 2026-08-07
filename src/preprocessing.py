"""Preprocessing + NER filtering per spec 001 WHAT §3/§3a.

Tokenise, lower-case, remove named entities (denylist EntityRuler + broad
statistical ner pass), remove tokens in a small set of grammatical
categories via POS tagging (added 2026-07-18 — see below). No generic
stopword-list removal.

History: the original design (2026-07-18, earlier) kept every stopword
and punctuation mark, on the reasoning that the project measures lexical
footprint and shouldn't pre-judge which words are "unimportant" — words
like "very" or "just" could signal hyperbole, and TF-IDF was expected to
self-neutralise genuinely uninformative terms via document frequency.
That held for the *intent*, but in practice pure function words could
still get inflated weight when they were incidentally rare in this small
11-document sample (e.g. "you" scoring high because it mostly appeared
inside one quote only 2 of 11 outlets reproduced) rather than actually
distinctive — three rounds of patching the TF-IDF formula itself
(continuity correction, then a high-TF cap) narrowed but didn't fully
close this.

Resolution (student, 2026-07-18): the distinction that actually matters
isn't "is this word rare," it's "is this word grammatically capable of
carrying evaluative meaning at all." Determiners (the, a), prepositions
(of, in, during), coordinating conjunctions (and, or, but), pronouns
(you, it, he), and punctuation are structurally incapable of carrying
hyperbole or hedging regardless of context, so removing them isn't
imposing a content judgement — it's a grammatical one. Adverbs (where
intensifiers and hedges live: very, just, only, allegedly, certainly),
negation, and modal/auxiliary verbs (would, could, might — modality is
directly relevant to a credibility axis) are explicitly kept, which a
generic stopword list would not distinguish. The TF-IDF corrections
(src/tfidf.py) are kept in place as a defensive layer for genuine content
words (e.g. "responsible") that still repeat unevenly across outlets.
"""

import spacy

from src.denylist import build_entity_ruler_patterns

_NLP = None
_CUSTOM_NLP_CACHE = {}

# Pure grammatical categories with no evaluative content under any
# interpretation. Deliberately does NOT include ADV (adverbs — where
# intensifiers/hedges live), AUX (modals), PART (covers "not"/"n't"),
# VERB, NOUN, ADJ, PROPN (already NER-stripped), NUM, SCONJ.
EXCLUDED_POS = {"DET", "ADP", "CCONJ", "PRON", "PUNCT"}


def _build_nlp(denylist_terms):
    nlp = spacy.load("en_core_web_sm")
    ruler = nlp.add_pipe("entity_ruler", before="ner")
    ruler.add_patterns(build_entity_ruler_patterns(denylist_terms))
    return nlp


def get_nlp(denylist_terms=None):
    """Load spaCy once, with the denylist EntityRuler wired in before the
    statistical `ner` component so denylist terms are guaranteed removed
    regardless of sentence context (spec 001 §3a).

    denylist_terms: optional override (e.g. src.denylist.WORLD_CUP_DENYLIST_TERMS)
    for a different corpus's own high-risk entity list (spec 007). None
    (default) returns the original cached singleton, built from the
    project's default DENYLIST_TERMS — existing callers (every call site
    before spec 007) are completely unaffected, since they never pass
    this argument. A custom terms list is cached separately, keyed by the
    terms themselves (as a tuple, so it's hashable) — repeated calls with
    the same custom list reuse one pipeline instead of reloading spaCy
    each time, without ever touching or invalidating the default `_NLP`
    singleton the original 11-article corpus depends on.
    """
    global _NLP
    if denylist_terms is None:
        if _NLP is None:
            _NLP = _build_nlp(None)
        return _NLP

    cache_key = tuple(denylist_terms)
    if cache_key not in _CUSTOM_NLP_CACHE:
        _CUSTOM_NLP_CACHE[cache_key] = _build_nlp(denylist_terms)
    return _CUSTOM_NLP_CACHE[cache_key]


def clean_tokens(text, pos_filter=True, denylist_terms=None):
    """Return the cleaned token list for one piece of text: named
    entities removed (denylist + broad statistical pass), lower-cased.

    pos_filter=True (default, production behaviour): also removes
    grammatical scaffolding (POS-based — see EXCLUDED_POS) and lone
    mis-tagged punctuation. pos_filter=False reverts to the original
    (pre-2026-07-18) behaviour — NER removal only, every stopword and
    punctuation mark kept — for ablation comparison against the current
    default via src/report.py.

    denylist_terms: passthrough to get_nlp() for a different corpus's own
    denylist (spec 007). None (default) — unaffected, original behaviour.
    """
    nlp = get_nlp(denylist_terms)
    doc = nlp(text)
    tokens = []
    for token in doc:
        if token.ent_type_:  # any entity type at all — broad pass
            continue
        if token.is_space:  # structural artifact, not a content judgement
            continue
        if pos_filter:
            if token.pos_ in EXCLUDED_POS:
                continue
            if len(token.text) == 1 and not token.text.isalnum():
                # Catches lone punctuation the statistical POS tagger
                # occasionally mis-tags as something else (e.g. a
                # possessive apostrophe tagged PART, or a hyphen
                # mis-tagged NOUN inside "semi-finalist") — a single
                # non-alphanumeric character is punctuation regardless of
                # what the tagger assigns it; a structural correction,
                # not a content judgement.
                continue
        tokens.append(token.text.lower())
    return tokens


def clean_corpus(pieces, pos_filter=True, denylist_terms=None):
    """pieces: {"A{n}Z{z}": raw_text} -> {"A{n}Z{z}": [clean tokens]}"""
    return {
        piece_id: clean_tokens(text, pos_filter=pos_filter, denylist_terms=denylist_terms)
        for piece_id, text in pieces.items()
    }


def clean_tokens_stopword_baseline(text, stopword_set, denylist_terms=None):
    """Spec 002: naive/standard-NLP baseline. NER removal stays identical
    to clean_tokens() above; grammatical-category (POS-tag) filtering is
    replaced entirely by a generic stopword-list + punctuation check.

    stopword_set: any set of lowercased words to drop (e.g. spaCy's or
    NLTK's default English list) — deliberately parameterised rather than
    hardcoded so both lists can be run through the same function for a
    fair comparison (spec 002 WHAT §1).
    denylist_terms: passthrough to get_nlp() for a different corpus's own
    denylist (spec 007). None (default) — unaffected, original behaviour.
    """
    nlp = get_nlp(denylist_terms)
    doc = nlp(text)
    tokens = []
    for token in doc:
        if token.ent_type_:  # NER removal unchanged
            continue
        if token.is_space:
            continue
        if token.is_punct:  # spaCy's own punctuation flag, not the
            continue        # POS-tag-based workaround clean_tokens() uses
        lowered = token.text.lower()
        if lowered in stopword_set:
            continue
        tokens.append(lowered)
    return tokens


def clean_corpus_stopword_baseline(pieces, stopword_set, denylist_terms=None):
    """pieces: {"A{n}Z{z}": raw_text} -> {"A{n}Z{z}": [clean tokens]}"""
    return {
        piece_id: clean_tokens_stopword_baseline(text, stopword_set, denylist_terms=denylist_terms)
        for piece_id, text in pieces.items()
    }
