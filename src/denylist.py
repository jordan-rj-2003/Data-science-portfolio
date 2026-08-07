"""NER denylist per spec 001 §3a: known high-risk terms guaranteed removed
before TF-IDF/vector averaging, regardless of what spaCy's statistical NER
tags. Grounded in the actual saved corpus (data/raw/*.txt), not guessed —
see journal 2026-07-18 for which outlet names actually appear as
self/cross-references.
"""

SUBJECT_TERMS = [
    "Sinner",
    "Jannik Sinner",
    "Jannik",
]

ORGANISATION_TERMS = [
    "WADA",
    "World Anti-Doping Agency",
    "ITIA",
    "International Tennis Integrity Agency",
    "CAS",
    "Court of Arbitration for Sport",
    "ATP",
    "International Tennis Federation",
]

SUBSTANCE_TERMS = [
    "clostebol",
    "Clostebol",
    "Trofodermin",
]

# Each of the 11 outlets' own names, per spec — kept complete even though
# most don't currently self/cross-reference in this corpus, since the
# denylist is meant to guard against future additions too.
OUTLET_TERMS = [
    "BBC",
    "Sky News",
    "Sky Sports",
    "Sky",
    "ATP Tour",
    "talkSPORT",
    "ESPN",
    "The Guardian",
    "Guardian",
    "The Independent",
    "Independent",
    "CBS Sports",
    "CBS",
    "Sports Illustrated",
    "Yahoo Sports",
    "Yahoo",
]

DENYLIST_TERMS = SUBJECT_TERMS + ORGANISATION_TERMS + SUBSTANCE_TERMS + OUTLET_TERMS

# Spec 007 — ESPN World Cup corpus. Additive, separate term set: does not
# touch DENYLIST_TERMS above, so the original 11-article pipeline's
# cached NLP singleton (src/preprocessing.py get_nlp()) and its output are
# completely unaffected by this corpus's existence. Player/manager names
# are deliberately NOT enumerated here — not knowable before seeing the
# actual 64 articles — and are left to the existing broad statistical
# PERSON-entity removal, same as the original pipeline relies on for
# anyone beyond its own small explicit denylist.
WORLD_CUP_ORGANISATION_TERMS = [
    "FIFA",
    "Fédération Internationale de Football Association",
    # This corpus's own source outlet — self-reference removal, same
    # rationale as OUTLET_TERMS above for the original 11-outlet corpus.
    "ESPN",
]

WORLD_CUP_EVENT_TERMS = [
    "World Cup",
    "FIFA World Cup",
    "the 2022 World Cup",
]

# The 32 nations that qualified for the 2022 FIFA World Cup (host nation
# included) — known in advance, so worth guaranteeing removal the same
# way the original denylist guarantees the 11 outlets' own names,
# regardless of how consistently spaCy's statistical NER tags each one
# in every sentence context.
WORLD_CUP_TEAM_TERMS = [
    "Qatar",
    "Ecuador",
    "Senegal",
    "Netherlands",
    "England",
    "Iran",
    "United States",
    "USA",
    "Wales",
    "Argentina",
    "Saudi Arabia",
    "Mexico",
    "Poland",
    "France",
    "Australia",
    "Denmark",
    "Tunisia",
    "Spain",
    "Costa Rica",
    "Germany",
    "Japan",
    "Belgium",
    "Canada",
    "Morocco",
    "Croatia",
    "Brazil",
    "Serbia",
    "Switzerland",
    "Cameroon",
    "Portugal",
    "Ghana",
    "Uruguay",
    "South Korea",
]

# Confirmed leaks found by a full-corpus audit (spec 007): cross-checked
# survivor vocabulary against capitalised mid-sentence words in the
# source text, then verified context on each match. Not exhaustive —
# player names in a 53-article, 32-team corpus are open-ended, and this
# is a reactive patch of what was actually found and confirmed, same
# convention as the original denylist. "Real" is deliberately NOT listed
# standalone — it's an ordinary English adjective ("a real chance") that
# would be stripped everywhere if denylisted alone; "Real Madrid" (the
# two-word phrase) is listed instead, which is what actually appeared.
WORLD_CUP_PLAYER_AND_ENTITY_LEAKS = [
    "Alves",
    "Andreas",
    "Bale",
    "Bayt",
    "Castelletto",
    "Dest",
    "Dumfries",
    "Eder",
    "Ferran",
    "Foden",
    "Fuller",
    "Lionel",
    "Maeda",
    "Mane",
    "Marquinhos",
    "Niclas",
    "Nikola",
    "Nunez",
    "Olmo",
    "Opta",
    "Ousmane",
    "Pavlovic",
    "Perisic",
    "Platini",
    "Rafinha",
    "Raheem",
    "Real Madrid",
    "Rochet",
    "Sadio",
    "Sargent",
    "Socceroos",
    "Szczesny",
    "Tite",
    "Vinicius",
    "Vlasic",
    "Weah",
]

WORLD_CUP_DENYLIST_TERMS = (
    WORLD_CUP_ORGANISATION_TERMS
    + WORLD_CUP_EVENT_TERMS
    + WORLD_CUP_TEAM_TERMS
    + WORLD_CUP_PLAYER_AND_ENTITY_LEAKS
)


def build_entity_ruler_patterns(terms=None):
    """EntityRuler patterns for the denylist terms, longest-phrase-first
    so multi-word terms (e.g. "Jannik Sinner") match before their
    single-word substrings (e.g. "Sinner") would otherwise claim the span.

    Matches case-insensitively via the LOWER token attribute — plain
    string patterns match case-sensitively, which missed real variants:
    BBC, the Guardian, and the Independent all write "Wada" and "Cas" in
    title case rather than all-caps "WADA"/"CAS" (a deliberate UK
    house-style convention, treating pronounceable acronyms like proper
    nouns), so exact-case matching silently let those through.

    terms: optional override list (e.g. WORLD_CUP_DENYLIST_TERMS). None
    (default) uses DENYLIST_TERMS — existing callers are unaffected.
    """
    source_terms = DENYLIST_TERMS if terms is None else terms
    unique_terms = sorted(set(source_terms), key=len, reverse=True)
    patterns = []
    for term in unique_terms:
        token_pattern = [{"LOWER": word.lower()} for word in term.split()]
        patterns.append({"label": "DENYLIST", "pattern": token_pattern})
    return patterns
