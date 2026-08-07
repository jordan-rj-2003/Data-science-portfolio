"""Preprocessing / NER / POS-filter spot checks, spec 001 task 10.

Uses the real spaCy pipeline (small, fast to load) rather than mocking it —
the whole point of these checks is to confirm what the actual tagger does
on real and realistic text, per src/preprocessing.py's own history of
POS-tag edge cases found only by checking real output.
"""

from src.denylist import WORLD_CUP_DENYLIST_TERMS
from src.preprocessing import clean_tokens, clean_tokens_stopword_baseline
from src.segmentation import load_article, segment
from tests.conftest import RAW_DIR


def test_pos_filter_removes_grammatical_scaffolding_keeps_modality():
    """DET/CCONJ/PRON/PUNCT are stripped; ADV/AUX/PART (intensifiers,
    modals, negation) are kept — the distinction spec 001 §3b is built on."""
    text = (
        "The player would very quickly deny the allegations, but WADA and "
        "Jannik Sinner said it wasn't true."
    )
    tokens = clean_tokens(text, pos_filter=True)
    assert tokens == [
        "player", "would", "very", "quickly", "deny", "allegations",
        "said", "was", "n't", "true",
    ]


def test_pos_filter_false_reverts_to_ner_only_removal():
    """pos_filter=False (the ablation baseline) keeps every stopword and
    punctuation mark, removing only named entities."""
    text = (
        "The player would very quickly deny the allegations, but WADA and "
        "Jannik Sinner said it wasn't true."
    )
    tokens = clean_tokens(text, pos_filter=False)
    assert tokens == [
        "the", "player", "would", "very", "quickly", "deny", "the",
        "allegations", ",", "but", "and", "said", "it", "was", "n't",
        "true", ".",
    ]


def test_single_character_punctuation_removed_regardless_of_pos_tag():
    """A mis-tagged lone hyphen (tagged ADJ inside 'semi-finalist', not
    PUNCT) must still be removed — the structural correction added
    2026-07-18 for exactly this tagger error."""
    text = "He is a semi-finalist and this is Sinner's ban."
    tokens = clean_tokens(text, pos_filter=True)
    assert "-" not in tokens
    assert tokens == ["is", "semi", "finalist", "is", "'s", "ban"]


def test_denylist_terms_removed_from_synthetic_text():
    text = (
        "Jannik Sinner accepted the ban after WADA and the ITIA reached an "
        "agreement over clostebol, as reported by the BBC."
    )
    tokens = clean_tokens(text, pos_filter=True)
    denylist_lower = {"sinner", "jannik", "wada", "itia", "clostebol", "bbc"}
    assert denylist_lower.isdisjoint(tokens)


def test_denylist_terms_removed_from_real_article_a1():
    """Spot-check against real data: A1 (BBC) is known to mention Sinner,
    WADA, ITIA, CAS, and clostebol by name (verified via grep on the raw
    file) — all must be gone after cleaning."""
    header, paragraphs = load_article(RAW_DIR / "A1.txt")
    whole_text = segment(header, paragraphs)[4]
    tokens = clean_tokens(whole_text, pos_filter=True)
    denylist_lower = {"sinner", "jannik", "wada", "itia", "cas", "clostebol"}
    assert denylist_lower.isdisjoint(tokens)


def test_stopword_baseline_removes_given_stopwords_and_keeps_content_words():
    """Spec 002: clean_tokens_stopword_baseline drops any token in the
    given stopword_set, regardless of POS tag — a deliberately different
    rule from clean_tokens' grammatical-category filter."""
    text = "The player would very quickly deny the allegations."
    stopword_set = {"the", "would"}
    tokens = clean_tokens_stopword_baseline(text, stopword_set)
    assert "the" not in tokens
    assert "would" not in tokens
    # words NOT in this stopword_set survive even though clean_tokens()
    # would keep/drop them on entirely different (grammatical) grounds
    assert "very" in tokens
    assert "quickly" in tokens
    assert "player" in tokens


def test_stopword_baseline_removes_punctuation_via_is_punct():
    text = "Wait, really? Yes!"
    tokens = clean_tokens_stopword_baseline(text, stopword_set=set())
    assert "," not in tokens
    assert "?" not in tokens
    assert "!" not in tokens
    assert "wait" in tokens


def test_stopword_baseline_still_removes_denylist_entities():
    """NER removal must stay identical to production — spec 002 keeps it
    unchanged, only the grammatical-filtering step is being swapped out."""
    text = "Jannik Sinner accepted the ban after WADA intervened."
    tokens = clean_tokens_stopword_baseline(text, stopword_set=set())
    denylist_lower = {"sinner", "jannik", "wada"}
    assert denylist_lower.isdisjoint(tokens)


def test_custom_denylist_removes_world_cup_terms_not_in_default_denylist():
    """Spec 007: a custom denylist_terms list removes terms the default
    Sinner-case denylist has never heard of (FIFA, competing nations)."""
    text = "FIFA confirmed that Argentina and France would meet in the final."
    tokens = clean_tokens(text, pos_filter=True, denylist_terms=WORLD_CUP_DENYLIST_TERMS)
    assert {"fifa", "argentina", "france"}.isdisjoint(tokens)


def test_custom_denylist_does_not_remove_original_denylist_terms():
    """The custom World Cup denylist is a separate list, not merged with
    the original — a term only on the original list (e.g. "Sinner")
    should NOT be removed when using the World Cup denylist, since
    football coverage has no reason to guard against it and this
    confirms the two lists are genuinely independent."""
    text = "Sinner is not a footballer, but FIFA governs football."
    tokens = clean_tokens(text, pos_filter=True, denylist_terms=WORLD_CUP_DENYLIST_TERMS)
    assert "sinner" in tokens
    assert "fifa" not in tokens


def test_default_denylist_unaffected_by_custom_denylist_calls():
    """Calling get_nlp() with a custom denylist elsewhere in the same
    process must not alter the default (None) pipeline's behaviour —
    the specific regression risk this spec-007 change introduces.

    Uses an invented placeholder term ("zonkwiddle") rather than a real
    FIFA/country name deliberately — real entity-like words (FIFA,
    Argentina) get removed by spaCy's own broad statistical NER pass
    regardless of any denylist, which would prove nothing about the
    denylist mechanism specifically. A made-up common-noun-shaped word
    isn't tagged as any entity type by the statistical pass, so its
    survival/removal here is attributable only to which denylist (if
    any) is active."""
    custom_terms = ["zonkwiddle"]
    clean_tokens("The zonkwiddle was announced.", pos_filter=True, denylist_terms=custom_terms)
    text = "Jannik Sinner announced the zonkwiddle."
    tokens = clean_tokens(text, pos_filter=True)  # default denylist, no custom terms
    assert "sinner" not in tokens  # original denylist still active
    assert "jannik" not in tokens
    # "zonkwiddle" is only on the custom list used in a prior call, not on
    # the default denylist — it must survive here, proving the custom
    # call didn't leak into (or replace) the default singleton.
    assert "zonkwiddle" in tokens


def test_world_cup_denylist_removes_confirmed_player_name_leaks():
    """Spec 007: a full-corpus audit found ~35 player/entity names that
    survived the broad statistical NER pass uncaught. Confirms the
    denylist patch actually removes a sample of them."""
    text = "Rochet made a fine save. Opta reported the statistic. Real Madrid's Bale scored."
    tokens = clean_tokens_stopword_baseline(text, set(), denylist_terms=WORLD_CUP_DENYLIST_TERMS)
    for leaked_term in ["rochet", "opta", "real", "madrid", "bale"]:
        assert leaked_term not in tokens, f"{leaked_term!r} should have been removed by the World Cup denylist"


def test_world_cup_denylist_does_not_strip_the_ordinary_word_real():
    """"Real" is deliberately not denylisted standalone -- only the
    two-word phrase "Real Madrid" -- so the ordinary adjective survives
    when it isn't part of that phrase."""
    text = "It was a real chance for Argentina to seal the win."
    tokens = clean_tokens_stopword_baseline(text, set(), denylist_terms=WORLD_CUP_DENYLIST_TERMS)
    assert "real" in tokens


def test_stopword_baseline_does_not_protect_negation_or_intensifiers():
    """Deliberate contrast with clean_tokens(pos_filter=True): a generic
    stopword list strips words the production design protects (spec 002
    WHY) — confirming the known, intended conflict actually occurs."""
    text = "He would never do that. It was only a very small mistake."
    spacy_like_stopwords = {"he", "would", "never", "that", "it", "was", "only", "a", "very"}
    tokens = clean_tokens_stopword_baseline(text, spacy_like_stopwords)
    assert "never" not in tokens
    assert "only" not in tokens
    assert "very" not in tokens
